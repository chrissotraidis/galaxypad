#!/usr/bin/env python3
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('chains',Path(__file__).resolve().parents[1]/'scripts/fp_guard_chains.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def block(pc):
    return (f'label_{pc:08X}:\n    ctx->pc = 0x{pc:08X}u;\n'
            f'    // {pc:08X}: ps_add  f0, f1, f2\n'
            f'    if (!ppc_fp_available_inline(ctx, 0x{pc:08X}u)) return;\n'
            '    ppc_ps_add_op(ctx, 0, 1, 2);\n\n')

source=('void example(CPUState* ctx) {\nswitch(ctx->pc) {\n'
        'case 0x80000000u: goto label_80000000;\n'
        'case 0x80000004u: ctx->downcount -= 2; goto label_80000004;\n}\n'+
        block(0x80000000)+block(0x80000004)+'label_80000008:\nreturn;\n}\n')
changed,pcs=m.transform(source)
assert pcs==[0x80000004]
assert 'ctx->downcount -= 2; ctx->pc = 0x80000004u; if (!ppc_fp_available_inline(ctx, 0x80000004u)) return; goto label_80000004;' in changed
assert changed.count('ppc_fp_available_inline')==source.count('ppc_fp_available_inline')
assert m.transform(changed)==(changed,[])
for old,new in [
    ('ppc_ps_add_op(ctx, 0, 1, 2);','ppc_ps_add_op(ctx, 32, 1, 2);'),
    ('ppc_ps_add_op(ctx, 0, 1, 2);','unknown(ctx, 0, 1, 2);'),
    ('ppc_ps_add_op(ctx, 0, 1, 2);','mem_write32(ctx, 0, 1);'),
    ('ppc_ps_add_op(ctx, 0, 1, 2);','ppc_ps_add_op(ctx, 0, 1, 2);\n    ctx->msr = 0;'),
    ('ps_add  f0','ps_add. f0'),
    ('label_80000008:\nreturn;', 'label_80000008:\ngoto label_80000004;')]:
    text=source.replace(old,new)
    assert m.transform(text)==(text,[]),new
assert m.transform(source+source)==(source+source,[])
print('FP guard chain transform preserves suffix guards and rejects observer/entry/operand hazards')
