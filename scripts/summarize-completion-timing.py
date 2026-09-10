#!/usr/bin/env python3
"""Compare observed CPU waits with graphics notification boundaries, without causal pairing."""
import argparse
import bisect
import csv
import json


def summarize(rows, start, end):
    if end <= start:
        raise ValueError('Invalid window')
    streams = {'cpu': [], 'graphics': []}
    for row in rows:
        event = dict(row)
        for key in ('wall_ns', 'thread_cpu_ns', 'cpu_clock_valid'):
            event[key] = int(row[key])
        streams[event['stream']].append(event)
    for name, events in streams.items():
        if not events or events[0]['wall_ns'] > start or events[-1]['wall_ns'] < end:
            raise ValueError(f'{name} retained stream does not cover window')
        kinds = ('wait_begin', 'wait_end') if name == 'cpu' else ('before_notify', 'after_notify')
        for i, event in enumerate(events):
            if event['kind'] != kinds[i % 2]:
                raise ValueError(f'{name} unpaired boundary sequence')
            if i and event['wall_ns'] < events[i-1]['wall_ns']:
                raise ValueError(f'{name} wall clock moved backwards')
    graphics = streams['graphics']
    times = [event['wall_ns'] for event in graphics]
    waits = []
    cpu = streams['cpu']
    for a, b in zip(cpu[::2], cpu[1::2]):
        if a['wall_ns'] < start or b['wall_ns'] > end:
            continue
        lower = bisect.bisect_left(times, a['wall_ns'])
        upper = bisect.bisect_right(times, b['wall_ns'])
        cpu_delta = b['thread_cpu_ns']-a['thread_cpu_ns']
        waits.append(dict(start_ns=a['wall_ns'], end_ns=b['wall_ns'],
                          wall_ms=(b['wall_ns']-a['wall_ns'])/1e6,
                          cpu_ms=cpu_delta/1e6 if a['cpu_clock_valid'] and
                          b['cpu_clock_valid'] and cpu_delta >= 0 else None,
                          notifications_within=graphics[lower:upper],
                          previous_notification=graphics[lower-1] if lower else None,
                          next_notification=graphics[upper] if upper < len(graphics) else None))
    return dict(complete_waits=len(waits), longest_waits=sorted(waits, key=lambda w: w['wall_ms'], reverse=True)[:10],
                caveat='Notification observations are not DONE publication or one-to-one wait matches; elapsed gaps can include scheduling.')


def summarize_flight(header, rows):
    if not header.startswith('# '):
        raise ValueError('Missing flight metadata')
    metadata = {}
    for token in header[2:].split():
        key, value = token.split('=', 1)
        if key in metadata:
            raise ValueError('Duplicate metadata')
        metadata[key] = int(value)
    required = {'flight_version', 'triggered', 'graphics_frozen', 'not_before_ns',
                'threshold_ns', 'trigger_start_ns', 'trigger_end_ns', 'invalid_waits',
                'cpu_overwritten', 'graphics_overwritten'}
    if set(metadata) != required or any(value < 0 for value in metadata.values()):
        raise ValueError('Invalid flight metadata fields')
    if metadata['flight_version'] != 1 or metadata['triggered'] not in (0, 1) or metadata['graphics_frozen'] not in (0, 1):
        raise ValueError('Unsupported version or flags')
    if not metadata['threshold_ns']:
        raise ValueError('Invalid threshold')
    if not metadata['triggered']:
        if metadata['trigger_start_ns'] or metadata['trigger_end_ns'] or metadata['graphics_frozen']:
            raise ValueError('Inconsistent untriggered metadata')
        return dict(status='not_triggered', metadata=metadata)
    start, end = metadata['trigger_start_ns'], metadata['trigger_end_ns']
    if start < metadata['not_before_ns'] or end-start < metadata['threshold_ns']:
        raise ValueError('Trigger violates arming/threshold')
    if not metadata['graphics_frozen']:
        return dict(status='graphics_response_missing', metadata=metadata)
    if metadata['invalid_waits']:
        raise ValueError('Capture contains invalid wait clocks')
    cpu = [row for row in rows if row['stream'] == 'cpu']
    graphics = [row for row in rows if row['stream'] == 'graphics']
    if len(cpu) < 2 or len(cpu) % 2 or not graphics or len(graphics) % 2:
        raise ValueError('Incomplete retained event pairs')
    if int(cpu[-2]['wall_ns']) != start or int(cpu[-1]['wall_ns']) != end:
        raise ValueError('Frozen CPU endpoints do not match trigger metadata')
    result = summarize(rows, start, end)
    if result['complete_waits'] != 1:
        raise ValueError('Expected one exact triggering wait')
    return dict(status='trigger_context_retained', metadata=metadata, **result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace')
    parser.add_argument('--start-ns', type=int)
    parser.add_argument('--end-ns', type=int)
    parser.add_argument('--flight', action='store_true')
    args = parser.parse_args()
    with open(args.trace) as stream:
        header = stream.readline()
        stream.seek(0)
        rows = list(csv.DictReader(line for line in stream if not line.startswith('#')))
    if args.flight:
        result = summarize_flight(header, rows)
    else:
        if args.start_ns is None or args.end_ns is None:
            parser.error('--start-ns and --end-ns are required unless --flight is used')
        result = summarize(rows, args.start_ns, args.end_ns)
    print(json.dumps(result, indent=2))
