#!/usr/bin/env python3
"""Summarize cumulative counters inside one visually verified, uninterrupted phase.

This measures callback delivery, not audibility, pitch or audiovisual sync.
Times are the host log's monotonic seconds, not wall-clock timestamps.
"""
import argparse
import json
from pathlib import Path
import re

COUNTERS = ('dma_enqueues', 'dma_underruns', 'dma_backlog_drops',
            'dma_full_drops', 'output_callbacks', 'output_requested_frames',
            'output_frames', 'output_nonzero_frames', 'output_short_callbacks')


def summarize(text, start, end):
    if not start < end:
        raise ValueError('Start must precede end')
    rows = []
    for line in text.splitlines():
        if '[GalaxyPad audio counters]' not in line:
            continue
        fields = dict(re.findall(r'(\w+)=([\d.]+)', line))
        before, after = float(fields['mono_before']), float(fields['mono_after'])
        if before < start or after > end:
            continue
        if before > after:
            raise ValueError('Invalid snapshot bracket')
        if fields['output_counters_available'] != '1':
            raise ValueError('Output instrumentation unavailable in selected phase')
        rows.append(dict(before=before, after=after,
                         **{key: int(fields[key]) for key in COUNTERS}))
    if len(rows) < 2:
        raise ValueError('Need at least two complete snapshots inside the phase')
    for previous, current in zip(rows, rows[1:]):
        if not 0 < current['before'] - previous['after'] <= 7:
            raise ValueError('Non-monotonic time or logging gap; split the phase')
        if any(current[key] < previous[key] for key in COUNTERS):
            raise ValueError('Counter reset; split the phase')
    first, last = rows[0], rows[-1]
    low = last['before'] - first['after']
    high = last['after'] - first['before']
    delta = {key: last[key] - first[key] for key in COUNTERS}
    return dict(snapshots=len(rows), start_mono=first['before'],
                end_mono=last['after'], seconds_bounds=[low, high], delta=delta,
                output_frames_per_second_bounds=[delta['output_frames'] / high,
                                                 delta['output_frames'] / low],
                nonzero_frame_fraction=(delta['output_nonzero_frames'] /
                                        delta['output_frames']
                                        if delta['output_frames'] else None),
                limitation=('Rate bounds cover snapshot timestamps only, not callback '
                            'quantization or separately atomic counter reads; '
                            'not audibility or AV-sync proof'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--start', type=float, required=True)
    parser.add_argument('--end', type=float, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.log.read_text(), args.start, args.end), indent=2))
