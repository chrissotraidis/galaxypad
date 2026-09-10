"""Compile a full cached restore chunk candidate privately with real PGO flags."""
from pathlib import Path
import hashlib
import json
import re
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
build = module.parent/'module-build'
source = module.parent/'dolrecomp-output/RMGE01_generated/chunks/chunk_1299_text1_805170A0.c'
profile = root/'generated/pgo/rmge01.profdata'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source) == '9b221ad3e1b417287e425640cc318e30fc5a6378e2956bf65a929be455acfd94'
assert sha(profile) == 'f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'
before = {str(p): sha(p) for p in (source, profile, module)}
original = source.read_text()
guard = '''
    {
        u32 base = ctx->gpr[11] - 12u;
        u32 masked = base & ~0x40000000u;
        u8 *ptr = NULL;
        if (ctx->exram && ctx->exram_size >= 12 &&
            masked - 0x90000000u <= ctx->exram_size - 12)
            ptr = ctx->exram + (masked - 0x90000000u);
        else if (ctx->ram && ctx->ram_size >= 12 &&
                 masked - 0x80000000u <= ctx->ram_size - 12)
            ptr = ctx->ram + (masked - 0x80000000u);
        if (ptr && ((uintptr_t)ptr + 12 <= (uintptr_t)ctx ||
                    (uintptr_t)ptr >= (uintptr_t)ctx + sizeof(*ctx))) {
            ctx->pc = 0x80517584u; ctx->gpr[29] = read_be32(ptr);
            ctx->pc = 0x80517588u; ctx->gpr[30] = read_be32(ptr + 4);
            ctx->pc = 0x8051758Cu; ctx->gpr[31] = read_be32(ptr + 8);
            goto label_80517590;
        }
    }
'''
assert original.count('label_80517584:\n') == 1
candidate = original.replace('label_80517584:\n', 'label_80517584:\n'+guard)
assert candidate.replace(guard, '', 1) == original
# External entry suffix charges and original return dispatcher remain verbatim.
db = json.loads(subprocess.check_output(['ninja', '-t', 'compdb', '-x'], cwd=build))
command = shlex.split(next(e['command'] for e in db if e.get('file') == str(source)))
command = [s.replace('\\', '') if s.startswith('-DMODULE_GAME_ID=') else s for s in command]
out = root/'generated/restore-profile-r451'
out.mkdir(exist_ok=False)
report = {'inputs': before, 'variants': {}, 'compile_command': command}
for name, text in [('control', original), ('candidate', candidate)]:
    folder = out/name; folder.mkdir()
    src = folder/source.name
    text = text.replace('#include "../RMGE01.h"', '#include "'+str(source.parent.parent/'RMGE01.h')+'"')
    src.write_text(text)
    args = command.copy(); args[args.index('-c')+1] = str(src)
    for opt, filename in [('-o', 'chunk.ll'), ('-MF', 'chunk.d'), ('-MT', 'chunk.ll')]:
        args[args.index(opt)+1] = str(folder/filename)
    args += ['-S', '-emit-llvm', '-Wprofile-instr-out-of-date', '-Wprofile-instr-unprofiled']
    proc = subprocess.run(args, cwd=build, capture_output=True, text=True)
    (folder/'compiler.log').write_text(proc.stdout+proc.stderr)
    proc.check_returncode()
    ir = (folder/'chunk.ll').read_text()
    counts = {m[1]: int(m[2]) for m in re.finditer(r'^!(\d+) = !\{!"function_entry_count", i64 (\d+)', ir, re.M)}
    definition = next(l for l in ir.splitlines() if l.startswith('define ') and '@func_805170A0(' in l)
    tag = re.search(r'!prof !(\d+)', definition)
    report['variants'][name] = {'function_entry_count': counts.get(tag[1]) if tag else None,
        'ir_bytes': len(ir), 'diagnostics': proc.stdout+proc.stderr}
assert all(sha(Path(path)) == digest for path, digest in before.items())
control_count = report['variants']['control']['function_entry_count']
candidate_count = report['variants']['candidate']['function_entry_count']
report['profile_compatible'] = control_count is not None and candidate_count == control_count
report['promotion_allowed'] = False
report['boundary'] = 'Private full-chunk code-generation/PGO check only. Not executed, installed or a speedup.'
(out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report['variants'], indent=2))
