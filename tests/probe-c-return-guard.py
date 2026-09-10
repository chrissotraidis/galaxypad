"""Stage one bounded C local-return guard; no product source mutation.

Uses private cached exact-chunk artifacts; retains original sparse switch and
cycle guard. The candidate only rejects PCs outside its legal return envelope.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source',type=Path)
p.add_argument('output',type=Path)
p.add_argument('--selector',action='store_true',help='Use an inline selector preserving the caller profile CFG')
args=p.parse_args();source=args.source.resolve();out=args.output.resolve()
assert out.is_relative_to(root/'generated')
report=json.loads((source/'report.json').read_text())
assert report['guest_start']=='0x804b60a0'
assert hashlib.sha256((source/'c.o').read_bytes()).hexdigest()==report['objects']['c']['sha256']
text=(source/'chunk.c').read_text()
head,tail=text.split('return_dispatch_804B60A0:\n')
matches=re.findall(r'case 0x([0-9A-F]+)u: goto label_([0-9A-F]+);',tail)
assert matches and all(a==b for a,b in matches)
targets=[int(a,16) for a,b in matches]
low=min(targets);span=max(targets)-low
guard=f'    if ((u32)(ctx->pc - 0x{low:08X}u) > 0x{span:X}u) return;\n'
assert tail.count('    switch (ctx->pc) {')==1
candidate=head+'return_dispatch_804B60A0:\n'+tail.replace('    switch (ctx->pc) {',guard+'    switch (ctx->pc) {')
assert candidate.replace(guard,'',1)==text
if args.selector:
 helper=f'''static inline __attribute__((always_inline, no_profile_instrument_function))
u32 bounded_return_selector(u32 pc) {{
    return (u32)(pc - 0x{low:08X}u) <= 0x{span:X}u ? pc : 0u;
}}
'''
 assert 0 not in targets and text.count('void func_804B60A0(')==1
 candidate=head+'return_dispatch_804B60A0:\n'+tail.replace('switch (ctx->pc)','switch (bounded_return_selector(ctx->pc))')
 candidate=candidate.replace('void func_804B60A0(',helper+'void func_804B60A0(')
 assert candidate.replace(helper,'',1).replace('switch (bounded_return_selector(ctx->pc))','switch (ctx->pc)')==text
out.mkdir(parents=True,exist_ok=False)
(out/'candidate.c').write_text(candidate)
shutil.copy2(source/'c.o',out/'c.o')
runtime=root/'ref/ModernGekko/vendor/dolphin/GXRuntime'
subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
 '-DDOLRECOMP_CPU_HEADER="core/cpu.h"','-I'+str(root/'generated/llvm-arm64-probe-r442/staged/src'),
 '-I'+str(runtime/'include'),'-c',str(out/'candidate.c'),'-o',str(out/'ir.o')],check=True)
# Keep the existing harness object slot naming, but label the actual backend.
report['candidate_label']='C-return-selector' if args.selector else 'C-return-guard'
report['source_sha256']=hashlib.sha256(text.encode()).hexdigest()
report['guard']={'low':hex(low),'span':hex(span),'targets':len(targets)}
report['objects']['ir']={'bytes':(out/'ir.o').stat().st_size,
 'sha256':hashlib.sha256((out/'ir.o').read_bytes()).hexdigest()}
report['boundary']='C-only return-envelope guard; original switch/cycle guard/instructions unchanged; no installed PGO/LTO or gameplay claim.'
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
# Exhaust the entire 16-bit low-word space for the relevant high word plus
# surrounding high-word boundaries; an outside envelope can never be a target.
tested=0
for high in (0,0x7fff0000,0x804b0000,0x804c0000,0xffff0000):
 for low_word in range(65536):
  pc=high|low_word
  assert (pc in targets)==(((pc-low)&0xffffffff)<=span and pc in targets)
  tested+=1
print(f'{tested} envelope/target comparisons pass; {len(targets)} targets; unchanged cycle guard and original switch')
print(json.dumps(report,indent=2))
