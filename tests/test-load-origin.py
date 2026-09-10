#!/usr/bin/env python3
"""Require full local instruction evidence before classifying a branch-table load."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
origin = runpy.run_path(str(root / 'scripts/classify-cpu-instructions.py'))['load_origin']
table = {0: ('adrp', 'x9, 0x6c0e000 <table>'),
         4: ('add', 'x9, x9, #0x888'),
         8: ('adr', 'x10, 0x100 <code>'),
         12: ('ldrh', 'w11, [x9, x8, lsl #1]'),
         16: ('add', 'x10, x10, x11, lsl #2'),
         20: ('br', 'x10')}
assert origin(table, 12) == 'pc_relative_branch_table'
for missing in (0, 4, 8, 16, 20):
    changed = dict(table)
    del changed[missing]
    assert origin(changed, 12) == 'unresolved'
for pc, wrong in ((0, ('adrp', 'x8, 0x6c0e000')), (4, ('add', 'x9, x8, #0x888')),
                  (8, ('adr', 'x11, 0x100')), (16, ('add', 'x10, x10, x11, lsl #1')),
                  (20, ('br', 'x11'))):
    assert origin(table | {pc: wrong}, 12) == 'unresolved'
assert origin({0: ('ldr', 'x8, [x19, #0xd98]')}, 0) == 'unresolved'
assert origin({0: ('ldp', 'x26, x25, [sp, #0x10]')}, 0) == 'stack'
lazy = {0: ('adrp', 'x8, 0x1000 <_g_ppc_lazy_fp_enabled>'),
        4: ('ldrb', 'w8, [x8]')}
assert origin(lazy, 4) == 'unresolved'
assert origin(lazy, 4, {0x1000:'_other',0x1010:'_g_ppc_lazy_fp_enabled'}) == 'unresolved'
assert origin(lazy, 4, {0x1000:'_g_ppc_lazy_fp_enabled'}) == 'lazy_fp_global_adjacent'
lazy[4] = ('ldrb', 'w8, [x8, #0x10]')
assert origin(lazy, 4, {0x1010:'_g_ppc_lazy_fp_enabled'}) == 'lazy_fp_global_adjacent'
assert origin(lazy, 4, {0x1000:'_g_ppc_lazy_fp_enabled'}) == 'unresolved'
print('Load origins: exact table pattern, missing/wrong dependencies and conservative unknowns pass')
