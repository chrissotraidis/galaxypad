#!/usr/bin/env python3
"""Summarize a complete fixed VI window; elapsed counters are not exclusive CPU states."""
import argparse
import csv
import json
import math


def distribution(values):
    """Nearest-rank quantiles over known values; missing counters are not zero."""
    known = sorted(value for value in values if value is not None)
    if not known:
        return dict(valid=0, missing=len(values), total_ms=None, mean_ms=None,
                    p50_ms=None, p95_ms=None, p99_ms=None, over_60hz_budget=None)
    quantile = lambda fraction: known[math.ceil(len(known) * fraction) - 1]
    return dict(valid=len(known), missing=len(values)-len(known),
                total_ms=sum(known), mean_ms=sum(known)/len(known),
                p50_ms=quantile(.50), p95_ms=quantile(.95), p99_ms=quantile(.99),
                over_60hz_budget=sum(value > 1000/60 for value in known))


def summarize(rows, start, end):
    if end <= start or len(rows) < 2:
        raise ValueError('Need a positive window and at least two samples')
    fields = ('wall_ns', 'thread_cpu_ns', 'cpu_clock_valid',
              'efb_elapsed_ns', 'throttle_elapsed_ns')
    samples = [{key: int(row[key]) for key in fields} for row in rows]
    for sample, row in zip(samples, rows):
        sample['wakeup_elapsed_ns'] = (int(row['wakeup_elapsed_ns'])
                                      if row.get('wakeup_elapsed_ns') is not None else None)
        sample['gather_wait_elapsed_ns'] = (int(row['gather_wait_elapsed_ns'])
                                          if row.get('gather_wait_elapsed_ns') is not None else None)
        sample['dvd_wait_elapsed_ns'] = (int(row['dvd_wait_elapsed_ns'])
                                        if row.get('dvd_wait_elapsed_ns') is not None else None)
        sample['idle_wait_elapsed_ns'] = (int(row['idle_wait_elapsed_ns'])
                                         if row.get('idle_wait_elapsed_ns') is not None else None)
    if any(b['wall_ns'] <= a['wall_ns'] for a, b in zip(samples, samples[1:])):
        raise ValueError('Wall timestamps must strictly increase')
    if samples[0]['wall_ns'] > start or samples[-1]['wall_ns'] < end:
        raise ValueError('Retained samples do not cover requested window')
    intervals = []
    for a, b in zip(samples, samples[1:]):
        # Only intervals wholly inside the window; do not import loading time.
        if a['wall_ns'] < start or b['wall_ns'] > end:
            continue
        delta = lambda key: ((b[key]-a[key])/1e6 if a[key] is not None and
                             b[key] is not None and b[key] >= a[key] else None)
        cpu = delta('thread_cpu_ns') if a['cpu_clock_valid'] and b['cpu_clock_valid'] else None
        intervals.append(dict(end_seconds=(b['wall_ns']-start)/1e9,
                              wall_ms=delta('wall_ns'), cpu_ms=cpu,
                              efb_elapsed_ms=delta('efb_elapsed_ns'),
                              throttle_elapsed_ms=delta('throttle_elapsed_ns'),
                              idle_wait_elapsed_ms=delta('idle_wait_elapsed_ns'),
                              dvd_wait_elapsed_ms=delta('dvd_wait_elapsed_ns'),
                              gather_wait_elapsed_ms=delta('gather_wait_elapsed_ns'),
                              wakeup_elapsed_ms=delta('wakeup_elapsed_ns')))
    count = sum(start <= s['wall_ns'] < end for s in samples)
    return dict(vi_events=count, vi_hz=count/((end-start)/1e9),
                complete_intervals=len(intervals),
                invalid_cpu_intervals=sum(i['cpu_ms'] is None for i in intervals),
                counter_reset_intervals=sum(i['efb_elapsed_ms'] is None or
                                            i['throttle_elapsed_ms'] is None for i in intervals),
                interval_distributions={key: distribution([i[key] for i in intervals])
                                        for key in ('wall_ms', 'cpu_ms', 'efb_elapsed_ms',
                                                    'throttle_elapsed_ms', 'idle_wait_elapsed_ms',
                                                    'dvd_wait_elapsed_ms', 'gather_wait_elapsed_ms',
                                                    'wakeup_elapsed_ms')},
                longest_intervals=sorted(intervals, key=lambda i: i['wall_ms'], reverse=True)[:20],
                caveat='Counters are elapsed durations, not disjoint off-CPU states; missing/reset counters are null. VI is not display scanout.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace')
    parser.add_argument('--start-ns', type=int, required=True)
    parser.add_argument('--end-ns', type=int, required=True)
    args = parser.parse_args()
    with open(args.trace) as stream:
        rows = list(csv.DictReader(line for line in stream if not line.startswith('#')))
    print(json.dumps(summarize(rows, args.start_ns, args.end_ns), indent=2))
