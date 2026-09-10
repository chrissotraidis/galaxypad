#!/usr/bin/env python3
"""Extract Instruments per-thread metric rows without averaging unlike cores."""
import argparse
import json
import math
import xml.etree.ElementTree as ET


def aggregate(rows):
    intervals = {}
    for row in rows:
        key = (row['thread'], row['core'], row['timestamp_ns'], row['duration_ns'])
        metrics = intervals.setdefault(key, {})
        if row['metric'] in metrics:
            raise ValueError('duplicate interval metric')
        metrics[row['metric']] = row
    ends = {}
    for thread, core, timestamp, duration in sorted(intervals, key=lambda k: (k[0], int(k[2]))):
        start, length = int(timestamp), int(duration)
        if start < 0 or length <= 0:
            raise ValueError('invalid interval bounds')
        if start < ends.get(thread, 0):
            raise ValueError(f'overlapping thread intervals at {start}')
        ends[thread] = start + length
    totals = {}
    for key, metrics in intervals.items():
        if set(metrics) != {'cycle', 'delivery', 'processing', 'discarded', 'useful'}:
            raise ValueError('incomplete bottleneck interval')
        cycles = int(metrics['cycle']['sum'] or 0)
        if cycles < 0:
            raise ValueError('negative cycle count')
        group = totals.setdefault(key[:2], {'cycles': 0, 'intervals': 0, 'excluded_intervals': 0, 'excluded_cycles': 0,
            'duration_ns': 0, 'excluded_duration_ns': 0,
            'time_weighted': dict.fromkeys(('delivery', 'processing', 'discarded', 'useful'), 0.0),
            'nonunit_intervals': 0, 'nonunit_cycles': 0, 'max_fraction_sum_error': 0.0,
            'weighted': dict.fromkeys(('delivery', 'processing', 'discarded', 'useful'), 0.0)})
        if not cycles or any(metrics[metric]['average'] is None for metric in group['weighted']):
            group['excluded_intervals'] += 1
            group['excluded_cycles'] += cycles
            group['excluded_duration_ns'] += int(key[3])
            continue
        fractions = {metric: float(metrics[metric]['average']) for metric in group['weighted']}
        if any(not math.isfinite(v) or not 0 <= v <= 1 for v in fractions.values()):
            raise ValueError('invalid bottleneck fraction')
        # Instruments exports independently derived fractions. Preserve and
        # disclose non-unit totals instead of normalizing or silently discarding.
        sum_error = abs(sum(fractions.values()) - 1)
        group['max_fraction_sum_error'] = max(group['max_fraction_sum_error'], sum_error)
        if sum_error > 1e-6:
            group['nonunit_intervals'] += 1
            group['nonunit_cycles'] += cycles
        group['cycles'] += cycles
        group['intervals'] += 1
        group['duration_ns'] += int(key[3])
        for metric in group['weighted']:
            group['weighted'][metric] += fractions[metric] * cycles
            group['time_weighted'][metric] += fractions[metric] * int(key[3])
    return [dict(thread=key[0], core=key[1], cycles=g['cycles'], intervals=g['intervals'],
                 excluded_intervals=g['excluded_intervals'], excluded_cycles=g['excluded_cycles'],
                 nonunit_intervals=g['nonunit_intervals'], nonunit_cycles=g['nonunit_cycles'],
                 max_fraction_sum_error=g['max_fraction_sum_error'],
                 duration_ns=g['duration_ns'], excluded_duration_ns=g['excluded_duration_ns'],
                 time_weighted_fractions={m: v/g['duration_ns'] for m, v in g['time_weighted'].items()},
                 cycle_weighted_fractions={m: v/g['cycles'] for m, v in g['weighted'].items()})
            for key, g in totals.items() if g['cycles']]


def summarize(root, thread_filter):
    references = {e.attrib['id']: e for e in root.iter() if 'id' in e.attrib}
    def resolve(e):
        return references[e.attrib['ref']] if 'ref' in e.attrib else e
    result = []
    for node in root.findall('node'):
        schema = node.find('schema')
        if schema is None or schema.get('name') != 'MetricTableForThread':
            continue
        columns = [c.findtext('mnemonic') for c in schema.findall('col')]
        for row in node.findall('row'):
            if len(row) != len(columns):
                raise ValueError('metric row/schema mismatch')
            fields = dict(zip(columns, map(resolve, row)))
            thread = fields['thread'].get('fmt', '')
            if thread_filter not in thread:
                continue
            def value(name):
                e = fields[name]
                return None if e.tag == 'sentinel' else e.text
            result.append(dict(thread=thread, core=value('core'),
                metric=value('metric-name'), label=value('metric-display-name'),
                average=value('average'), sum=value('sum'),
                timestamp_ns=value('timestamp'), duration_ns=value('duration')))
    if not result:
        raise ValueError('no matching per-thread metric rows')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xml')
    parser.add_argument('--thread', default='CPU thread')
    parser.add_argument('--aggregate', action='store_true')
    args = parser.parse_args()
    rows = summarize(ET.parse(args.xml).getroot(), args.thread)
    print(json.dumps(aggregate(rows) if args.aggregate else rows, indent=2))
