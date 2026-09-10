"""Focused transformation checks; compiling a chunk is not execution proof."""
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare', root / 'scripts/prepare-direct-call-chunk.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = '''case 0x80001004u: ctx->downcount -= 7; goto label_80001004;
    // 80001000: bl      0x80002000
    {
            ctx->lr = 0x80001004u;
            ctx->pc = 0x80002000u;
            return;
    }
label_80001004:
    ctx->pc = 0x80001004u;
'''
result, count = module.transform(source, lambda target: 'func_80002000')
assert count == 1
assert 'ctx->downcount -= 7; goto label_80001004;' in result.split('galaxypad_direct_transfer')[1]
assert result.count('ctx->lr = 0x80001004u;') == 1
assert result.count('ctx->pc = 0x80002000u;') == 1
assert module.transform(source, lambda target: None) == (source, 0)
missing = source.replace('case 0x80001004u:', 'case 0x80003000u:')
assert module.transform(missing, lambda target: 'func_80002000') == (missing, 0)
for invalid in (source.replace('downcount -= 7', 'downcount += 7'),
                source.replace('ctx->lr = 0x80001004', 'ctx->lr = 0x80001008')):
    try:
        module.transform(invalid, lambda target: 'func_80002000')
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid accounting/link shape accepted')
print('Direct-call chunk transformation: suffix charge, preserved state, exclusions and fail-closed shapes pass')
