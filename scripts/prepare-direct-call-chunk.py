#!/usr/bin/env python3
"""Create one isolated guarded-call chunk; never rewrite the selected module."""
import argparse
from bisect import bisect_right
from pathlib import Path
import re

ENTRY = re.compile(r'case 0x([0-9A-F]{8})u: (.*?)goto label_\1;')
SITE = re.compile(
    r'(// ([0-9A-F]{8}): bl\s+0x([0-9A-F]{8})\s*\n[ \t]*\{\n)'
    r'(?P<indent>[ \t]*)ctx->lr = 0x([0-9A-F]{8})u;\n'
    r'(?P=indent)ctx->pc = 0x([0-9A-F]{8})u;\n'
    r'(?P=indent)return;')


def transform(source, resolve):
    entries = dict(ENTRY.findall(source))
    count = 0

    def replace(match):
        nonlocal count
        comment, pc, target, indent, lr, written_target = match.groups()
        continuation = f'{int(pc, 16) + 4:08X}'
        if lr != continuation or written_target != target:
            raise ValueError(f'Inconsistent BL at {pc}')
        if continuation not in entries:
            return match.group(0)
        charge = entries[continuation]
        if charge and not re.fullmatch(r'ctx->downcount -= [0-9]+; ', charge):
            raise ValueError(f'Unknown continuation entry accounting at {continuation}')
        function = resolve(target)
        if function is None:
            return match.group(0)
        count += 1
        return (f'{comment}{indent}ctx->lr = 0x{lr}u;\n'
                f'{indent}ctx->pc = 0x{target}u;\n'
                f'{indent}if (galaxypad_direct_transfer(ctx, 0x{target}u, '
                f'0x{continuation}u, {function})) {{\n'
                f'{indent}    {charge}goto label_{continuation};\n'
                f'{indent}}}\n{indent}return;')

    return SITE.sub(replace, source), count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chunk', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    chunk = args.chunk.resolve(strict=True)
    generated = chunk.parent.parent
    output = args.output.resolve()
    if output.is_relative_to(generated) or output.exists():
        parser.error('Output must be a new file outside the selected generated tree')
    paths = sorted(chunk.parent.glob('chunk_*.c'),
                   key=lambda p: int(p.stem.rsplit('_', 1)[1], 16))
    starts = [int(p.stem.rsplit('_', 1)[1], 16) for p in paths]
    cache = {}

    def resolve(target):
        address = int(target, 16)
        if not 0x80000000 <= address < 0x81800000:
            return None
        index = bisect_right(starts, address) - 1
        if index < 0:
            return None
        path = paths[index]
        if path == chunk:
            return None
        if path not in cache:
            cache[path] = dict(ENTRY.findall(path.read_text()))
        if target not in cache[path]:
            return None
        return f'func_{starts[index]:08X}'

    source, count = transform(chunk.read_text(), resolve)
    include = re.search(r'^#include "\.\./([^"/]+\.h)"$', source, re.M)
    if not include or not count:
        parser.error('Expected generated header and at least one eligible call')
    header = (generated / include.group(1)).resolve(strict=True)
    transfer = Path(__file__).resolve().parents[1] / 'apple/experiments/guarded-direct-calls/transfer.h'
    source = source.replace(include.group(0),
                            f'#include "{header}"\n#include "{transfer}"', 1)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also rejects another writer racing the preflight check.
    with output.open('x') as stream:
        stream.write(source)
    print(f'{count} guarded sites written to {output}; original tree untouched')


if __name__ == '__main__':
    main()
