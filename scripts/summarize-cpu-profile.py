#!/usr/bin/env python3
"""Read an xctrace cpu-profile XML export; never launch or modify the game.

Report CPU-thread leaf counts and cycle weights. Optional binary-relative
half-open ranges must come from the exact traced binary's disassembly.
Addresses retain raw profiler bits; range matching aligns ARM64 PCs to 4 bytes.
"""
import argparse
from collections import Counter
import json
import xml.etree.ElementTree as ET


def summarize(root, ranges=(), binary_name='gRMGE01_recomp.dylib', thread_prefix='CPU thread '):
    if not thread_prefix.strip():
        raise ValueError('Thread prefix must not be empty')
    ids = {e.get('id'): e for e in root.iter() if e.get('id')}

    def resolve(e):
        if e is None:
            raise ValueError('Missing required CPU-profile field')
        seen = set()
        while e.get('ref'):
            ref = e.get('ref')
            if ref in seen:
                raise ValueError('Cyclic XML reference')
            seen.add(ref)
            e = ids[ref]
        return e

    counts, cycles, cores, addresses = (Counter() for _ in range(4))
    address_cycles = Counter()
    region_counts, region_cycles = Counter(), Counter()
    total = 0
    for row in root.iter('row'):
        thread = resolve(row.find('thread'))
        if not thread.get('fmt', '').startswith(thread_prefix):
            continue
        total += 1
        weight = int(resolve(row.find('cycle-weight')).text)
        if weight < 0:
            raise ValueError('Negative cycle weight')
        cores[resolve(row.find('core')).get('fmt')] += 1
        tagged = resolve(row.find('tagged-backtrace'))
        stack = resolve(tagged.find('backtrace'))
        if len(stack) == 0:
            counts['<empty stack>'] += 1
            cycles['<empty stack>'] += weight
            continue
        frame = resolve(stack[0])
        name = frame.get('name', '<unnamed>')
        counts[name] += 1
        cycles[name] += weight
        binary = frame.find('binary')
        if binary is None:
            continue
        binary = resolve(binary)
        if binary.get('name') != binary_name:
            continue
        offset = int(frame.get('addr'), 16) - int(binary.get('load-addr'), 16)
        addresses[(name, hex(offset))] += 1
        address_cycles[(name, hex(offset))] += weight
        for label, start, end in ranges:
            if start <= (offset & ~3) < end:
                region_counts[label] += 1
                region_cycles[label] += weight
    if total == 0:
        raise ValueError('No CPU-thread samples; wrong export or target')
    assert sum(counts.values()) == total == sum(cores.values())
    return dict(samples=total, cycles=sum(cycles.values()), cores=dict(cores), thread_prefix=thread_prefix,
                address_binary=binary_name,
                leaves=[dict(name=n, samples=c, cycles=cycles[n])
                        for n, c in counts.most_common()],
                addresses=[dict(name=n, raw_offset=p, samples=c, cycles=address_cycles[(n,p)])
                           for (n, p), c in addresses.most_common()],
                ranges=[dict(name=n, start=hex(s), end=hex(e),
                             samples=region_counts[n], cycles=region_cycles[n])
                        for n, s, e in ranges])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xml')
    parser.add_argument('--binary', default='gRMGE01_recomp.dylib',
                        help='Exact binary name for offsets/ranges; leaf totals still cover the CPU thread')
    parser.add_argument('--thread-prefix', default='CPU thread ',
                        help='Exact thread-name prefix; Simulator uses CPU-GPU thread')
    parser.add_argument('--range', action='append', default=[], metavar='NAME:START:END')
    args = parser.parse_args()
    ranges = []
    for value in args.range:
        name, start, end = value.split(':')
        start, end = int(start, 0), int(end, 0)
        if start < 0 or end <= start or start % 4 or end % 4:
            parser.error('Ranges must be nonempty, nonnegative, ARM64-aligned')
        if any(name == n for n, _, _ in ranges):
            parser.error('Range names must be unique')
        ranges.append((name, start, end))
    if not args.thread_prefix.strip():
        parser.error('Thread prefix must not be empty')
    print(json.dumps(summarize(ET.parse(args.xml).getroot(), ranges, args.binary,
                               args.thread_prefix), indent=2))
