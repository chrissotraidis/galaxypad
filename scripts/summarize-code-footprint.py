#!/usr/bin/env python3
"""Observed sampled-PC footprint, not executed-code size or cache-miss proof."""
import argparse
from collections import Counter
import json


def summarize(data, block_size):
    if block_size < 4 or block_size & (block_size - 1):
        raise ValueError('block size must be a power of two >= 4')
    blocks = Counter()
    pcs = Counter()
    for row in data['addresses']:
        weight = row['samples']
        if not isinstance(weight, int) or weight < 0:
            raise ValueError('invalid sample count')
        if not weight:
            continue
        pc = int(row['raw_offset'], 16) & ~3
        if pc < 0:
            raise ValueError('negative module offset')
        pcs[pc] += weight
        blocks[pc // block_size] += weight
    total = sum(blocks.values())
    coverage = {}
    ranked = sorted(blocks.values(), reverse=True)
    for percent in (50, 90, 99):
        count = accumulated = 0
        for weight in ranked:
            accumulated += weight
            count += 1
            if accumulated * 100 >= total * percent:
                break
        coverage[str(percent)] = count
    return dict(binary=data.get('address_binary'), samples=total,
                distinct_aligned_pcs=len(pcs), block_size=block_size,
                sampled_blocks=len(blocks), blocks_covering_percent=coverage,
                boundary='Sampled addresses only; not cache misses, dynamic instructions, or removable time.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('summary')
    args = parser.parse_args()
    with open(args.summary) as source:
        data = json.load(source)
    print(json.dumps([summarize(data, size) for size in (64, 4096, 16384)], indent=2))
