#!/usr/bin/env python3
"""Read-only coverage audit for strictly adjacent, unobserved FPRF writers.

This intentionally rejects any unrecognized emitted statement. It does not
modify generated code or establish eligibility for other emitter versions.
"""
import json
import re
from pathlib import Path

LABEL = re.compile(r'^label_([0-9A-F]{8}):\n', re.M)
BODY = re.compile(
    r'    ctx->pc = 0x(?P<pc>[0-9A-F]{8})u;\n'
    r'    // (?P=pc): ps_(?:add|sub|mul|madd|msub|nmadd|nmsub)  .*\n'
    r'    if \(!ppc_fp_available_inline\(ctx, 0x(?P=pc)u\)\) return;\n'
    r'    ppc_ps_(?:add|sub|mul|madd)_op\(ctx, [0-9, truefals]+\);\n\s*\Z')


def regions(text):
    # Count primary function bodies only, not separately outlined loop bodies.
    start = text.find('\nvoid func_')
    if start < 0:
        return []
    text = text[start:]
    labels = list(LABEL.finditer(text))
    result = []
    for index in range(len(labels) - 1):
        first, second = labels[index:index + 2]
        end = labels[index + 2].start() if index + 2 < len(labels) else len(text)
        a, b = int(first[1], 16), int(second[1], 16)
        if b != a + 4:
            continue
        left = BODY.fullmatch(text[first.end():second.start()])
        right = BODY.fullmatch(text[second.end():end])
        if left and right and int(left['pc'], 16) == a and int(right['pc'], 16) == b:
            result.append(a)
    return result


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    module = Path((root / 'generated/modules/RMGE01/active-module.txt').read_text().strip())
    chunks = module.parent / 'dolrecomp-output/RMGE01_generated/chunks'
    counts, examples = {}, {}
    for path in sorted(chunks.glob('*.c')):
        eligible = regions(path.read_text())
        if eligible:
            counts[path.name] = len(eligible)
            if '804520A0' in path.name:
                examples[path.name] = [f'{pc:08X}' for pc in eligible]
    print(json.dumps({'eligible_writes': sum(counts.values()),
                      'chunks_with_regions': len(counts),
                      'largest': sorted(counts.items(), key=lambda item: -item[1])[:10],
                      'decoder_regions': examples}, indent=2))
