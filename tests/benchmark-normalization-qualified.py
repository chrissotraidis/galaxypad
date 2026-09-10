#!/usr/bin/env python3
"""Cost only for an all-comparisons-passing finite workload; no promotion gate.

R828 full corpus still fails host flags. This screen decides whether further
correctness engineering has plausible value; it cannot approve this candidate.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
retained=root/'generated/normalization-compact-whole-r827-czpxyahy'
source=(retained/'probe.c').read_text()
assert source.count('pattern<64')==1
source=source.replace('pattern<64','pattern<1')
# Every remaining full-state, memory, cycle and host-flag assertion is retained.
assert 'flags!=fetestexcept(FE_ALL_EXCEPT)' in source
assert 'assert(!memcmp(&a,&b,sizeof a))' in source
assert 'assert(!memcmp(expected,ram,256))' in source
assert 'return 3;' in source
(out/'probe.c').write_text(source)
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
command=['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
 '-I',str(core),'-I',str(core.parents[1]/'include'),'-Wl,-dead_strip',
 str(out/'probe.c'),str(core/'cpu_interpreter_table.c'),'-o',str(out/'probe')]
subprocess.run(command,check=True)
result=subprocess.run([str(out/'probe')],text=True,capture_output=True)
(out/'result.log').write_text(result.stdout+result.stderr)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(out/'report.json').write_text(json.dumps({'command':command,'exit_code':result.returncode,
 'reference_sha256':sha(retained/'reference.dylib'),
 'candidate_sha256':sha(retained/'candidate.dylib'),
 'boundary':'One qualified finite workload only; full host-flag corpus still fails; NOT promotion or FPS evidence'},indent=2)+'\n')
print(result.stdout+result.stderr,flush=True)
result.check_returncode()
