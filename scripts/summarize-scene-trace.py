#!/usr/bin/env python3
"""Report only complete minute bins in a fixed scene trace; read-only."""
import argparse
import csv
import json
import math


EVENTS = ('vi_end_field', 'frame_begin', 'present_done')


def summarize(rows, start, minutes=10, event='vi_end_field'):
    if event not in EVENTS:
        raise ValueError(f'Unsupported cadence event: {event}')
    bins = [[] for _ in range(minutes)]
    watermark = start
    previous = None
    for row in rows:
        # A live trace may have one unfinished trailing line.
        if not row.get('steady_ns') or not row.get('event') or row.get('value') is None:
            continue
        timestamp = int(row['steady_ns'])
        watermark = max(watermark, timestamp)
        if row['event'] != event:
            continue
        index = (timestamp-start)//60_000_000_000
        if 0 <= index < minutes:
            gap = None if previous is None else (timestamp-previous)/1e6
            bins[index].append(gap)
        previous = timestamp
    complete = min(minutes, max(0, (watermark-start)//60_000_000_000))
    result = []
    for index in range(complete):
        gaps = sorted(gap for gap in bins[index] if gap is not None)
        result.append(dict(minute=index+1, count=len(bins[index]),
                           hz=len(bins[index])/60,
                           p99_ms=gaps[max(0,math.ceil(len(gaps)*.99)-1)] if gaps else None,
                           max_gap_ms=max(gaps) if gaps else None,
                           gaps_ge_20ms=sum(gap>=20 for gap in gaps)))
    return dict(event=event, complete_minutes=complete, requested_minutes=minutes, bins=result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace')
    parser.add_argument('--start-ns', type=int, required=True)
    parser.add_argument('--minutes', type=int, default=10)
    args = parser.parse_args()
    if args.minutes < 1:
        parser.error('minutes must be positive')
    with open(args.trace) as stream:
        rows = list(csv.DictReader(stream))
    print(json.dumps({event: summarize(rows, args.start_ns, args.minutes, event)
                      for event in EVENTS}, indent=2))
