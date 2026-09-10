"""Read-only generated-chunk audit; not a binary, runtime or performance audit."""
import argparse
import hashlib
from pathlib import Path
import json

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('artifact',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
accepted=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
assert hashlib.sha256(accepted.read_bytes()).hexdigest()=='1180447313459c4c153ca74e5215811e88a9b69a00d15feff940f062148fc631'
old=accepted.parent/'dolrecomp-output/RMGE01_generated/chunks'
new=args.artifact/'dolrecomp-output/RMGE01_generated/chunks'
names={p.name for p in old.glob('chunk_*.c')}
assert len(names)==1322 and names=={p.name for p in new.glob('chunk_*.c')}
changed=[]
for name in sorted(names):
    if hashlib.sha256((old/name).read_bytes()).digest()!=hashlib.sha256((new/name).read_bytes()).digest():
        changed.append(name)
target='chunk_1103_text1_804530A0.c'
assert changed==[target],changed
original=(old/target).read_text()
assert hashlib.sha256(original.encode()).hexdigest()=='e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
helper=(root/'patches/experiments/dcbz-ram-loop.inc').read_text()
assert hashlib.sha256(helper.encode()).hexdigest()=='ed743fdeb1b32af89dfd1fbfefa671a63b2a36ed7c2c59b684f105275783a421'
anchor='for (u32 i = 0; i < 32; i += 4) mem_write32(ctx, ea + i, 0);'
assert original.count(anchor)==8
expected=original.replace(anchor,'u8* line = galaxypad_dcbz_prepare(ctx, ea);\n        for (u32 i = 0; i < 32; i += 4) galaxypad_dcbz_store(ctx, ea, line, i);')
expected=expected.replace('void func_804530A0(CPUState* ctx) {','#include <string.h>\n'+helper+'\nvoid func_804530A0(CPUState* ctx) {')
assert (new/target).read_text()==expected
print(json.dumps(dict(chunks=len(names),unchanged=len(names)-1,changed=changed,
    transformed_sha256=hashlib.sha256(expected.encode()).hexdigest(),
    exact_tested_transform=True,binary_verified=False),indent=2))
