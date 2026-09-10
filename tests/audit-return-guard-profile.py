"""Audit actual cached compile/PGO compatibility for a private return guard.

Only emits diagnostic LLVM IR into generated/, never replaces a module/object.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shlex
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--selector',action='store_true',help='Preserve caller CFG via an inline selector instead of a new caller branch')
p.add_argument('--output',type=Path,default=root/'generated/return-profile-r445')
options=p.parse_args()
module=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
cache=module.parent;build=cache/'module-build'
source=cache/'dolrecomp-output/RMGE01_generated/chunks/chunk_1202_text1_804B60A0.c'
profile=root/'generated/pgo/rmge01.profdata'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(profile)=='f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'
before={str(path):sha(path) for path in (source,profile,module)}
db=json.loads(subprocess.check_output(['ninja','-t','compdb','-x'],cwd=build))
entry=next(e for e in db if e.get('file')==str(source))
command=shlex.split(entry['command'])
command=[s.replace('\\','') if s.startswith('-DMODULE_GAME_ID=') else s for s in command]
original=source.read_text();head,tail=original.split('return_dispatch_804B60A0:\n')
targets=[int(a,16) for a,b in re.findall(r'case 0x([0-9A-F]+)u: goto label_([0-9A-F]+);',tail) if a==b]
assert len(targets)==18 and tail.count('    switch (ctx->pc) {')==1
guard=f'    if ((u32)(ctx->pc - 0x{min(targets):08X}u) > 0x{max(targets)-min(targets):X}u) return;\n'
candidate=head+'return_dispatch_804B60A0:\n'+tail.replace('    switch (ctx->pc) {',guard+'    switch (ctx->pc) {')
assert candidate.replace(guard,'',1)==original
if options.selector:
 helper=f'''static inline __attribute__((always_inline, no_profile_instrument_function))
u32 bounded_return_selector(u32 pc) {{
    return (u32)(pc - 0x{min(targets):08X}u) <= 0x{max(targets)-min(targets):X}u ? pc : 0u;
}}
'''
 assert 0 not in targets and original.count('void func_804B60A0(')==1
 candidate=head+'return_dispatch_804B60A0:\n'+tail.replace('switch (ctx->pc)', 'switch (bounded_return_selector(ctx->pc))')
 candidate=candidate.replace('void func_804B60A0(',helper+'void func_804B60A0(')
 assert candidate.replace(helper,'',1).replace('switch (bounded_return_selector(ctx->pc))','switch (ctx->pc)')==original
out=options.output.resolve();assert out.is_relative_to(root/'generated');out.mkdir(exist_ok=False)
report={'inputs':before,'compile_command':command,'variants':{}}
for name,text in (('control',original),('candidate',candidate)):
 folder=out/name;folder.mkdir();src=folder/source.name
 # The real source includes ../RMGE01.h. Resolve it explicitly without copying
 # or changing the header or its local dependency tree.
 text=text.replace('#include "../RMGE01.h"','#include "'+str(source.parent.parent/'RMGE01.h')+'"')
 src.write_text(text)
 args=command.copy();args[args.index('-c')+1]=str(src)
 for opt,filename in (('-o','chunk.ll'),('-MF','chunk.d'),('-MT','chunk.ll')):
  args[args.index(opt)+1]=str(folder/filename)
 args+=['-S','-emit-llvm','-Wprofile-instr-out-of-date','-Wprofile-instr-unprofiled']
 result=subprocess.run(args,cwd=build,text=True,capture_output=True)
 (folder/'compiler.log').write_text(result.stdout+result.stderr)
 result.check_returncode()
 ir=(folder/'chunk.ll').read_text()
 counts={m[1]:int(m[2]) for m in re.finditer(r'^!(\d+) = !\{!"function_entry_count", i64 (\d+)',ir,re.M)}
 definition=next(line for line in ir.splitlines() if line.startswith('define ') and '@func_804B60A0(' in line)
 tag=re.search(r'!prof !(\d+)',definition)
 report['variants'][name]={'source_sha256':sha(src),'ir_bytes':len(ir),
  'function_entry_count':counts.get(tag[1]) if tag else None,
  'diagnostics':result.stdout+result.stderr}
assert all(sha(Path(path))==digest for path,digest in before.items())
report['boundary']='Exact cached compiler flags/PGO audit only; no module replacement or gameplay claim.'
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
