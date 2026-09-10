"""Exercise the generated BL census without compiling or mutating a module."""
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('census', root / 'scripts/audit-direct-call-sites.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
prefix = '// 80001000: bl      0x80002000\nctx->lr = 0x80001004u;\n'
suffix = '\nlabel_80001004:\n    // 80001004: nop\n'
cases = {
    'return_to_chassis': 'ctx->pc = 0x80002000u; return;',
    'local_goto': 'if (budget) { ctx->pc = 0x80002000u; return; } goto label_80002000;',
    'direct_cross_chunk': 'ctx->pc = 0x80002000u; func_80002000(ctx); return;'
}
for expected, body in cases.items():
    assert module.classify(prefix + body + suffix) == {expected: 1}
assert module.classify('// 80001000: blr\nreturn;') == {}
for bad in ('return;', 'ctx->pc = 0x80003000u; return;'):
    try:
        module.classify(prefix + bad + suffix)
    except ValueError:
        pass
    else:
        raise AssertionError('Unknown branch shape accepted')
print('Direct BL census classifications and fail-closed unknown shapes pass')
