"""Offline exact-kernel dead-PC experiment; retain PC before unavailable-FP faults."""
import hashlib
import re

SOURCE_SHA = '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
PATTERN = re.compile(
    r'(?P<start>\nlabel_(?P<pc>[0-9A-F]{8}):\n)'
    r'    ctx->pc = 0x(?P=pc)u;\n'
    r'(?P<body>    // (?P=pc): ps_(?:add|sub|mul|madd|msub|nmadd|nmsub)  [^\n]+\n'
    r'    if \(!ppc_fp_available_inline\(ctx, 0x(?P=pc)u\)\) return false;\n'
    r'    ppc_ps_(?:add|sub|mul|madd)_op\(ctx, [0-9, truefals]+\);\n)'
    r'(?=\nlabel_(?P<next>[0-9A-F]{8}):\n    ctx->pc = 0x(?P=next)u;)')


def transform(source):
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Unexpected extracted kernel identity')
    prefix, tail = source.split('\nvoid func_804520A0(', 1)
    count = 0
    def replace(match):
        nonlocal count
        if int(match['next'], 16) != int(match['pc'], 16) + 4:
            return match[0]
        count += 1
        return (match['start'] + '    if (g_ppc_lazy_fp_enabled && !(ctx->msr & PPC_MSR_FP))\n'
                + f"        ctx->pc = 0x{match['pc']}u;\n" + match['body'])
    changed = PATTERN.sub(replace, prefix)
    assert count == 95, 'Unexpected exact dead-PC site count'
    return changed + '\nvoid func_804520A0(' + tail
