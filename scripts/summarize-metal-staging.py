#!/usr/bin/env python3
"""Summarize bounded CPU-wall staging spans; never report GPU-only time/FPS."""
import argparse
import csv
import json
import statistics
import math
from pathlib import Path

def correlate_waits(rows):
    """Match only a unique same-buffer handler contained in a host wait.

    Pointer identities may be reused: never match across disjoint intervals.
    Missing/ambiguous matches remain explicit, including capture boundaries.
    """
    handlers = {}
    for row in rows:
        token = int(row.get('buffer', '0'))
        if token < 0 or token >= 2**64:
            raise ValueError('Invalid buffer identity')
        if token and row['stage'] == 'completion_handler':
            handlers.setdefault(token, []).append((int(row['begin_ns']), int(row['end_ns']), row.get('clock')))
    before, after = [], []
    gpu_to_handler = []
    gpu_clock_unavailable = gpu_order_invalid = 0
    unmatched = ambiguous = unrecorded = 0
    for row in rows:
        if row['stage'] != 'wait':
            continue
        token = int(row.get('buffer', '0'))
        if not token:
            unrecorded += 1
            continue
        begin, end = int(row['begin_ns']), int(row['end_ns'])
        matches = [(a, b, clock) for a, b, clock in handlers.get(token, []) if begin <= a <= b <= end]
        if len(matches) == 1:
            a, b, clock = matches[0]
            before.append((a - begin) / 1e6)
            after.append((end - b) / 1e6)
            if (clock != 'mach_absolute' or row.get('clock') != clock or
                    row.get('gpu_valid') != '1' or 'gpu_end_s' not in row):
                gpu_clock_unavailable += 1
            else:
                gap = a / 1e9 - float(row['gpu_end_s'])
                if gap < 0:
                    gpu_order_invalid += 1
                else:
                    gpu_to_handler.append(gap * 1000)
        elif matches:
            ambiguous += 1
        else:
            unmatched += 1
    return {'matched': len(before), 'unmatched': unmatched, 'ambiguous': ambiguous,
            'unrecorded': unrecorded,
            'gpu_end_to_handler': {
                'available': len(gpu_to_handler), 'unavailable': gpu_clock_unavailable,
                'invalid_order': gpu_order_invalid,
                'median_ms': statistics.median(gpu_to_handler) if gpu_to_handler else None,
                'max_ms': max(gpu_to_handler) if gpu_to_handler else None},
            'wait_begin_to_handler_begin_median_ms': statistics.median(before) if before else None,
            'handler_end_to_wait_end_median_ms': statistics.median(after) if after else None,
            'handler_end_to_wait_end_max_ms': max(after) if after else None}

def summarize(rows):
    groups = {stage: [] for stage in ('copy_setup', 'submit', 'wait', 'completion_handler')}
    ids = set()
    gpu_values = []
    gpu_unavailable = gpu_unrecorded = 0
    for row in rows:
        sample = int(row['sample'])
        begin, end = int(row['begin_ns']), int(row['end_ns'])
        if sample in ids or not 0 <= sample < 4096 or begin < 0 or end < begin:
            raise ValueError('Invalid sample identity or time ordering')
        if row['stage'] not in groups:
            raise ValueError('Unknown staging phase')
        ids.add(sample)
        groups[row['stage']].append((end - begin) / 1_000_000)
        if 'gpu_start_s' in row or 'gpu_end_s' in row or 'clock' in row:
            start_s, end_s = float(row['gpu_start_s']), float(row['gpu_end_s'])
            if row['clock'] not in ('mach_absolute', 'steady'):
                raise ValueError('Unknown host clock domain')
            if not math.isfinite(start_s) or not math.isfinite(end_s) or start_s < 0 or end_s < start_s:
                raise ValueError('Invalid absolute GPU timestamps')
            if (row.get('gpu_valid') == '1' and start_s <= 0) or (row.get('gpu_valid') != '1' and (start_s or end_s)):
                raise ValueError('Unexpected absolute GPU timestamps')
        if 'gpu_valid' in row or 'gpu_ms' in row:
            valid = int(row['gpu_valid'])
            duration = float(row['gpu_ms'])
            if valid not in (0, 1) or not math.isfinite(duration) or duration < 0:
                raise ValueError('Invalid GPU timing fields')
            if (valid and row['stage'] != 'wait') or (not valid and duration != 0):
                raise ValueError('Unexpected GPU interval')
            if row['stage'] == 'wait':
                if valid:
                    gpu_values.append(duration)
                else:
                    gpu_unavailable += 1
        elif row['stage'] == 'wait':
            gpu_unrecorded += 1
    if not ids or ids != set(range(len(ids))):
        raise ValueError('Empty or incomplete trace sequence')
    return {'records': len(ids), 'cap_reached': len(ids) == 4096,
            'wait_handler_correlation': correlate_waits(rows),
            'units': 'stages: CPU wall milliseconds; GPU intervals reported separately',
            'gpu_wait_records': {'available': len(gpu_values), 'unavailable': gpu_unavailable,
                                 'unrecorded': gpu_unrecorded,
                                 'median_ms': statistics.median(gpu_values) if gpu_values else None,
                                 'max_ms': max(gpu_values) if gpu_values else None},
            'stages': {stage: {'count': len(values), 'total_ms': sum(values),
                      'median_ms': statistics.median(values), 'max_ms': max(values)}
                       for stage, values in groups.items() if values}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    args = parser.parse_args()
    with args.trace.open() as stream:
        print(json.dumps(summarize(list(csv.DictReader(stream))), indent=2))
