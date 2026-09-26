#!/usr/bin/env python3
"""Map one unchanged, SHA-pinned tail to existing Clang PGO counters.

Produces LLVM text only; never links, installs or runs guest code.
The final lfs has one FPU-unavailable exit. Its successful arm flows directly
to the chunk return, so label count minus unavailable count is the tail count.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = 'e58a578fa2a522909f2f9f24ddbddb2fc536f766c93a044d0dc57dc3481d7cae'
NAME = 'func_804B50A0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
commands = ROOT / 'generated/build/ios-simulator-pgo-use-20260912/compile_commands.json'
entry = next(c for c in json.loads(commands.read_text())
             if c['file'].endswith('chunk_1201_text1_804B50A0.c'))
source = Path(entry['file'])
if sha(source) != SOURCE_SHA:
    raise ValueError('Pinned source changed; re-audit the tail before mapping counters')
original = shlex.split(entry['command'])
profile = Path(next(x.split('=', 1)[1] for x in original
                    if x.startswith('-fprofile-instr-use=')))
command = []
skip = False
for arg in original:
    if skip:
        skip = False
        continue
    if arg == '-o':
        skip = True
        continue
    if arg == '-c' or arg.startswith(('-O', '-flto', '-fprofile-instr-use=')):
        continue
    command.append(arg)
ir_path = (args.output / 'instrumentation.ll').resolve()
command += ['-O0', '-S', '-emit-llvm', '-fprofile-instr-generate',
            '-Xclang', '-disable-llvm-passes', '-o', str(ir_path)]
subprocess.run(command, cwd=entry['directory'], check=True)
ir = ir_path.read_text()
metadata = re.search(r'@llvm.instrprof.increment\(ptr @__profn_' + NAME +
                    r', i64 (-?\d+), i32 (\d+), i32 0\)', ir)
if not metadata:
    raise ValueError('Missing front-end function instrumentation')
instrumentation_hash = int(metadata[1]) & ((1 << 64) - 1)
count = int(metadata[2])
raw = subprocess.check_output(['xcrun', 'llvm-profdata', 'show', '--counts',
                              '--function=' + NAME, str(profile)], text=True)
if int(re.search(r'Hash: (0x[0-9a-f]+)', raw)[1], 16) != instrumentation_hash:
    raise ValueError('Instrumentation CFG hash does not match archived profile')
values = [int(re.search(r'Function count: (\d+)', raw)[1])]
values += json.loads('[' + re.search(r'Block counts: \[(.*?)\]', raw)[1] + ']')
if len(values) != count:
    raise ValueError('Counter count mismatch')
# The source SHA pins control flow; also verify the reviewed IR segment and
# counter indices rather than assuming compiler versions retain their numbering.
last_pc = str(0x804B609C - (1 << 32))
tail_pc = str(0x804B60A0 - (1 << 32))
store = list(re.finditer(r'  store i32 ' + last_pc + r',', ir))
if len(store) != 1:
    raise ValueError('Final instruction PC store is not unique')
label_start = ir.rfind('\n\n', 0, store[0].start())
tail = re.search(r'  store i32 ' + tail_pc + r',.*\n  br label %\d+', ir[store[0].start():])
if not tail:
    raise ValueError('Tail does not flow directly to return block')
segment = ir[label_start:store[0].start() + tail.end()]
indices = [int(i) for i in re.findall(r'@llvm.instrprof.increment\(ptr @__profn_' +
           NAME + r', i64 -?\d+, i32 \d+, i32 (\d+)\)', segment)]
if indices != [2339, 2340] or segment.count('br i1 ') != 1:
    raise ValueError('Reviewed final-label/FPU-exit structure changed')
if '@ppc_fp_available_inline' not in segment or '@mem_read32' not in segment:
    raise ValueError('Expected final lfs helpers missing')
if values[2340] > values[2339]:
    raise ValueError('Invalid counter difference')
(args.output / 'tail-ir.txt').write_text(segment + '\n')
report = dict(source=str(source), source_sha256=SOURCE_SHA,
    compile_commands_sha256=sha(commands), profile=str(profile),
    profile_sha256=sha(profile), instrumentation_hash=f'0x{instrumentation_hash:016x}',
    counter_count=count, function_entries=values[0], last_label_counter_index=2339,
    last_label_count=values[2339], unavailable_counter_index=2340,
    unavailable_count=values[2340], tail_crossings=values[2339]-values[2340],
    cut_pc='0x804B60A0', command=command, ir_sha256=sha(ir_path),
    limitations=['Historical training count, not present-scene edge rate or CPU cost.',
        'Successful normal returns only; unexpected nonlocal host exits would invalidate subtraction.',
        'No source/module optimization, execution, installation or speedup.'])
(args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'command'}, indent=2))
