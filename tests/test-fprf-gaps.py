"""Fail-closed source recognition for the read-only nonadjacent FPRF census."""
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gaps', root/'scripts/audit-fprf-gaps.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def writer(pc):
    return f'''label_{pc:08X}:
    ctx->pc = 0x{pc:08X}u;
    // {pc:08X}: ps_add  f1, f2, f3
    if (!ppc_fp_available_inline(ctx, 0x{pc:08X}u)) return;
    ppc_ps_add_op(ctx, 1, 2, 3);

'''

def gap(op='addi', code='ctx->gpr[3] = ctx->gpr[4] + (u32)(s32)(-4);'):
    return f'''label_80001004:
    ctx->pc = 0x80001004u;
    // 80001004: {op}    r3, r4, -4
    {code}

'''

prefix = '\nvoid func_80001000(CPUState* ctx) {\n'
suffix = 'label_8000100C:\n    return;\n}\n'
source = prefix + writer(0x80001000) + gap() + writer(0x80001008) + suffix
assert audit.regions(source) == [dict(producer='80001000', overwrite='80001008', gaps=['addi'])]
for body in [gap('lwz', 'ctx->gpr[3] = mem_read32(ctx, 0);'),
             gap('addi', 'ctx->gpr[3] = observer(ctx);'),
             gap('addi', 'ctx->gpr[3] = ctx->fpscr;'),
             gap('addi', 'ctx->gpr[3] = 1; return;'),
             gap('addi.', 'ctx->gpr[3] = 1;'),
             gap('mffs', 'ctx->fpr[3] = ctx->fpscr;'),
             gap('nop', 'ctx->exception = 1;'),
             gap().replace('label_80001004:', 'label_80002004:')]:
    assert not audit.regions(prefix + writer(0x80001000) + body + writer(0x80001008) + suffix)
assert not audit.regions(source.replace('ctx->gpr[4]', 'ctx->gpr[32]'))
assert not audit.regions(source.replace('// 80001008: ps_add ', '// 80001008: ps_add. '))
print('FPRF gap audit: recognized integer gap and ten barrier/unknown/entry cases pass')
