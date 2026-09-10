"""Exact transform scope and fail-closed source guards, not runtime correctness."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from thp_dead_pc import transform, PATTERN

source = (root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed = transform(source)
guard = '    if (g_ppc_lazy_fp_enabled && !(ctx->msr & PPC_MSR_FP))\n        ctx->pc = '
assert changed.count(guard) == 95
assert changed.replace(guard, '    ctx->pc = ') == source
for invalid in (source+'\n', changed):
    try:
        transform(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('Changed/reapplied source accepted')
match = next(PATTERN.finditer(source))
sample = source[match.start():match.end()+100]
assert PATTERN.search(sample)
for invalid in (sample.replace('ppc_ps_', 'unknown_ps_'),
                sample.replace('return false;', 'return;'),
                sample.replace('    // ', '    mem_read32(ctx, 0);\n    // ', 1)):
    assert not PATTERN.search(invalid)
print('95 exact PC sites; byte-exact reversal; unknown/reapplied source and observers refused')
