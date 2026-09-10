"""Negative observation-boundary tests for read-only emitted-region audit."""
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', root/'scripts/audit-fprf-regions.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def instruction(pc, name='add', extra=''):
    return (f'label_{pc:08X}:\n    ctx->pc = 0x{pc:08X}u;\n'
            f'    // {pc:08X}: ps_{name}  f0, f1, f2\n'
            f'    if (!ppc_fp_available_inline(ctx, 0x{pc:08X}u)) return;\n'
            f'    ppc_ps_{name}_op(ctx, 0, 1, 2);\n{extra}\n')

prefix = '\nvoid func_00001000(CPUState* ctx) {\n'
tail = 'label_00001008:\n    return;\n}\n'
left, right = instruction(0x1000), instruction(0x1004, 'sub')
assert audit.regions(prefix + left + right + tail) == [0x1000]
barriers = ['    ctx->cr = ctx->fpscr;\n', '    ppc_fpscr_updated(ctx);\n',
            '    mem_read32(ctx, 0);\n', '    if (ctx->exception) return;\n',
            '    return;\n', '    goto label_00001008;\n',
            '    ctx->downcount -= 1;\n', '    loop_00001004(ctx);\n',
            '    ctx->msr = 0;\n', '    ppc_fallback_instruction(ctx,0,0);\n']
for barrier in barriers:
    for a, b in [(instruction(0x1000, extra=barrier), right),
                 (left, instruction(0x1004, 'sub', barrier))]:
        assert not audit.regions(prefix + a + b + tail), barrier
assert not audit.regions(prefix + left + instruction(0x1008) + tail)
assert not audit.regions(prefix + left + right.replace('ps_sub  ', 'ps_sub. ') + tail)
assert not audit.regions(prefix + left + right.replace('00001004u', '00002004u') + tail)
assert not audit.regions(prefix + left + right.replace('ppc_ps_sub_op', 'unrecognized') + tail)
assert not audit.regions(prefix + left + '\n}\nvoid func_00001004() {\n' + right + tail)
assert not audit.regions('static void loop_00001000() {\n' + left + right + tail)
print('Adjacent writer accepted; Rc/reader/memory/exception/exit/CFG/chunk/unknown barriers rejected')
