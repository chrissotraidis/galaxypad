#!/usr/bin/env python3
"""Read-only candidate census across strictly recognized integer-only gaps.

Counts are not a transformation authorization or a dynamic savings estimate.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re

spec = importlib.util.spec_from_file_location('adjacent', Path(__file__).with_name('audit-fprf-regions.py'))
adjacent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adjacent)
HEADER = re.compile(r'    ctx->pc = 0x([0-9A-F]{8})u;\n    // \1: (\S+)[^\n]*\n')
INTEGER = {'li', 'lis', 'addi', 'addis', 'ori', 'oris', 'xori', 'xoris',
           'mr', 'or', 'xor', 'and', 'andc', 'nor', 'nand', 'eqv', 'not',
           'add', 'subf', 'nop'}
ASSIGN = re.compile(r'ctx->gpr\[(?:[0-9]|[12][0-9]|3[01])\] = ([^;]+);')
ATOMS = re.compile(r'ctx->gpr\[(?:[0-9]|[12][0-9]|3[01])\]|\((?:u32|s32)\)|0x[0-9A-Fa-f]+u?|[0-9]+u?')


def integer_gap(body, address):
    header = HEADER.match(body)
    if not header or int(header[1], 16) != address or header[2] not in INTEGER:
        return None
    code = body[header.end():].strip()
    if header[2] == 'nop':
        return 'nop' if not code else None
    assignment = ASSIGN.fullmatch(code)
    if not assignment:
        return None
    # Only register/immediate expressions and casts; no calls or other state.
    residue = ATOMS.sub('', assignment[1])
    if not re.fullmatch(r'[\s()+\-&|^~<>]*', residue):
        return None
    return header[2]


def regions(text):
    start = text.find('\nvoid func_')
    if start < 0:
        return []
    text = text[start:]
    labels = list(adjacent.LABEL.finditer(text))
    pending = None
    gaps = []
    previous = None
    result = []
    for index, label in enumerate(labels):
        address = int(label[1], 16)
        if previous is not None and address != previous + 4:
            pending, gaps = None, []
        previous = address
        end = labels[index+1].start() if index+1 < len(labels) else len(text)
        body = text[label.end():end]
        writer = adjacent.BODY.fullmatch(body)
        if writer and int(writer['pc'], 16) == address:
            if pending is not None:
                result.append(dict(producer=f'{pending:08X}', overwrite=f'{address:08X}', gaps=list(gaps)))
            pending, gaps = address, []
        elif pending is not None and (operation := integer_gap(body, address)):
            gaps.append(operation)
        else:
            pending, gaps = None, []
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generated', type=Path)
    args = parser.parse_args()
    files = sorted((args.generated/'chunks').glob('chunk_*.c'))
    if not files:
        parser.error('No chunk sources')
    records = []
    gap_counts = Counter()
    for path in files:
        raw = path.read_bytes()
        found = regions(raw.decode())
        if found:
            records.append(dict(file=str(path), sha256=hashlib.sha256(raw).hexdigest(), regions=found))
            gap_counts.update(op for item in found for op in item['gaps'])
    all_regions = [item for row in records for item in row['regions']]
    print(json.dumps(dict(chunks_scanned=len(files), regions=len(all_regions),
                          nonadjacent=sum(bool(item['gaps']) for item in all_regions),
                          gap_operations=dict(gap_counts), files=records,
                          caveat='Source candidates only; no dynamic coverage, transformation or speedup proof.'), indent=2))


if __name__ == '__main__':
    main()
