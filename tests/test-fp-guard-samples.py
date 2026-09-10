#!/usr/bin/env python3
"""Synthetic parser checks; contains no retail instructions or addresses."""
from pathlib import Path
import runpy

parse = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                          'scripts/audit-fp-guard-samples.py'))['guards']
ops = ['adrp x8, 0x1000 <_g_ppc_lazy_fp_enabled>', 'ldrb w8, [x8]',
       'cmp w8, #0x1', 'b.ne 0x1020', 'ldr w8, [x0, #0x298]',
       'tbz w8, #0xd, 0x2000']


def listing(items):
    return '\n'.join(f'{0x1000 + i * 4:x}: 00000000 {op}'
                     for i, op in enumerate(items))


assert parse(listing(ops)) == [[0x1000 + i * 4 for i in range(6)]]
assert parse(listing(ops).replace('[x0,', '[x19,'))
for old, new in [('_g_ppc_lazy_fp_enabled', '_other'), ('#0x298', '#0x290'),
                 ('#0xd,', '#0xc,'), ('b.ne', 'b.eq'), ('[x0,', '[x7,')]:
    assert not parse(listing(ops).replace(old, new)), (old, new)
assert not parse(listing(ops).replace('1014:', '1018:'))
assert not parse(listing(ops[:-1]))
print('FP guard sample parser positive and rejection cases passed')
