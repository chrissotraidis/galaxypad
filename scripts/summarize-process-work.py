#!/usr/bin/env python3
"""Normalize process-wide work by VI counts, preserving snapshot uncertainty."""
import argparse
import csv
import json
import re


def summarize(capture, stamps):
    a, b = capture['first'], capture['last']
    if (a['pid'], a['start_abstime']) != (b['pid'], b['start_abstime']):
        raise ValueError('process identity changed')
    if not (0 <= a['before_ns'] <= a['after_ns'] < b['before_ns'] <= b['after_ns']):
        raise ValueError('invalid query brackets')
    if not stamps or any(y <= x for x, y in zip(stamps, stamps[1:])):
        raise ValueError('invalid VI sequence')
    if stamps[0] > a['before_ns'] or stamps[-1] < b['after_ns']:
        raise ValueError('incomplete VI coverage')
    minimum = sum(a['after_ns'] <= t < b['before_ns'] for t in stamps)
    maximum = sum(a['before_ns'] <= t < b['after_ns'] for t in stamps)
    if minimum <= 0:
        raise ValueError('empty guaranteed VI window')
    deltas = {k: b[k]-a[k] for k in ('instructions', 'cycles')}
    if any(v <= 0 for v in deltas.values()):
        raise ValueError('counter reset or unavailable work counts')
    seconds = ((b['before_ns']+b['after_ns'])-(a['before_ns']+a['after_ns']))/2e9
    return dict(scope='whole process, not guest CPU thread; VI is not presentation',
                duration_seconds=seconds, vi_count_min=minimum, vi_count_max=maximum,
                vi_hz_range=[minimum/seconds, maximum/seconds], deltas=deltas,
                snapshot_uncertainty_ns=[a['after_ns']-a['before_ns'], b['after_ns']-b['before_ns']],
                per_vi_ranges={k: [v/maximum, v/minimum] for k, v in deltas.items()})


def summarize_recording(capture, stamps, dropped, verified_prefix_capacity=None):
    """Opt-in only for a verified append-only, fixed-capacity recorder.

    Capacity/coverage cannot prove an arbitrary producer never drops internally.
    The caller must verify that producer contract; default still rejects drops.
    """
    if dropped < 0:
        raise ValueError('negative dropped count')
    if dropped and (verified_prefix_capacity is None or
                    verified_prefix_capacity <= 0 or len(stamps) != verified_prefix_capacity):
        raise ValueError('drops require verified complete prefix capacity')
    result = summarize(capture, stamps)  # All original coverage guards remain.
    result['recording'] = dict(dropped=dropped,
        verified_prefix_capacity=verified_prefix_capacity,
        retained_tail_margin_ns=stamps[-1]-capture['last']['after_ns'],
        dropped_outside_window=bool(dropped))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture')
    parser.add_argument('vi')
    parser.add_argument('--verified-prefix-capacity', type=int,
                        help='Only for a source-verified append-only recorder; retain drop count and require complete measured coverage')
    args = parser.parse_args()
    with open(args.capture) as source:
        capture = json.load(source)
    with open(args.vi) as source:
        header = re.fullmatch(r'# dropped=(\d+)', source.readline().strip())
        if not header:
            raise SystemExit('VI recorder has unknown status')
        stamps = [int(r['wall_ns']) for r in csv.DictReader(source)]
    print(json.dumps(summarize_recording(capture, stamps, int(header[1]),
                                        args.verified_prefix_capacity), indent=2))
