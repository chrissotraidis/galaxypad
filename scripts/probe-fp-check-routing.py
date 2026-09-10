#!/usr/bin/env python3
"""Prepare private checked-entry/unchecked-fallthrough kernel experiment."""
from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[1]
source_path = root/'generated/modules-thp-r205/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-daa33a86eff05b70/dolrecomp-output/RMGE01_generated/chunks/chunk_1102_text1_804520A0.c'
source = source_path.read_text()
assert hashlib.sha256(source.encode()).hexdigest() == 'fa455a7ae795c5428ce66c56d745416d2c5d9815ac32db14da571428b3661bae'
end = source.index('void func_804520A0(CPUState* ctx) {')
kernel = source[:end]
labels = list(re.finditer(r'^label_([0-9A-F]{8}):\n', kernel, re.M))
body = re.compile(
    r'    ctx->pc = 0x([0-9A-F]{8})u;\n'
    r'    // \1: ps_(?:add|sub|mul|madd|msub|nmadd|nmsub)  [^\n]*\n'
    r'    if \(!ppc_fp_available_inline\(ctx, 0x\1u\)\) return false;\n'
    r'    (?:ppc_ps_(?:add|sub|mul|madd)_op|galaxypad_deferred_(?:add|sub|mul|madd))'
    r'\(ctx, [0-9, truefals]+\);\n\s*')
insertions = []
edges = []
for left, right, following in zip(labels, labels[1:], labels[2:]):
    a = body.fullmatch(kernel[left.end():right.start()])
    b = body.fullmatch(kernel[right.end():following.start()])
    if not a or not b or int(b[1],16) != int(a[1],16)+4:
        continue
    pc = b[1]
    check = f'    if (!ppc_fp_available_inline(ctx, 0x{pc}u)) return false;\n'
    check_end = kernel.index(check, right.end()) + len(check)
    insertions.append((right.start(), f'    ctx->pc = 0x{pc}u;\n    goto fp_ready_{pc};\n\n'))
    insertions.append((check_end, f'fp_ready_{pc}:\n'))
    edges.append((a[1],pc))
assert edges, 'No eligible arithmetic edges'
candidate = source
for at, text in sorted(insertions, reverse=True):
    candidate = candidate[:at]+text+candidate[at:]
# Reversing all additions must recover every original checked entry and body.
restored = candidate
for _, text in insertions:
    assert restored.count(text) == 1
    restored = restored.replace(text, '', 1)
assert restored == source
out = root/'generated/fp-check-routing-r219'
out.mkdir(exist_ok=False)
(out/'reference.c').write_text(source)
(out/'candidate.c').write_text(candidate)
(out/'edges.txt').write_text(''.join(f'{a} -> {b}\n' for a,b in edges))
print(f'{len(edges)} normal arithmetic edges bypass a repeated check; all original entries retained')
print('Candidate SHA256:', hashlib.sha256(candidate.encode()).hexdigest())
print('Structural preparation only; execution and fault-entry tests required')
