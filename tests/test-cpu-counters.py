import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('counters', Path(__file__).resolve().parents[1]/'scripts/summarize-cpu-counters.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
rows = []
for timestamp, cycles, delivery in ((0, 100, .2), (10, 300, .6)):
    for name, value in [('cycle', cycles), ('delivery', delivery),
                        ('useful', 1-delivery), ('processing', 0), ('discarded', 0)]:
        rows.append(dict(thread='CPU', core='Performance', timestamp_ns=str(timestamp),
                         duration_ns='10', metric=name, sum=str(value) if name == 'cycle' else None,
                         average=None if name == 'cycle' else str(value)))
result = m.aggregate(rows)
assert result[0]['cycles'] == 400
assert result[0]['cycle_weighted_fractions']['delivery'] == .5
assert abs(result[0]['time_weighted_fractions']['delivery'] - .4) < 1e-12
assert result[0]['duration_ns'] == 20
missing = [dict(row) for row in rows]
missing[1]['average'] = None
assert m.aggregate(missing)[0]['excluded_cycles'] == 100
assert m.aggregate(missing)[0]['cycles'] == 300
assert m.aggregate(missing)[0]['excluded_duration_ns'] == 10
overlap = [dict(row) for row in rows]
for row in overlap[5:]:
    row['timestamp_ns'] = '9'
    row['core'] = 'Efficiency'
negative = [dict(row) for row in rows]
negative[0]['sum'] = '-1'
nan = [dict(row) for row in rows]
nan[1]['average'] = 'nan'
bad_sum = [dict(row) for row in rows]
bad_sum[1]['average'] = '.9'
assert m.aggregate(bad_sum)[0]['nonunit_intervals'] == 1
assert m.aggregate(bad_sum)[0]['nonunit_cycles'] == 100
for invalid in (rows[:-1], rows + [rows[0]], overlap, negative, nan):
    try:
        m.aggregate(invalid)
        raise AssertionError('invalid intervals accepted')
    except ValueError:
        pass
columns = ('timestamp', 'duration', 'thread', 'process', 'sum', 'average',
           'metric-name', 'metric-display-name', 'core', 'documentation')
xml = ET.Element('trace-query-result')
node = ET.SubElement(xml, 'node')
schema = ET.SubElement(node, 'schema', name='MetricTableForThread')
for column in columns:
    ET.SubElement(ET.SubElement(schema, 'col'), 'mnemonic').text = column
row = ET.SubElement(node, 'row')
for index, value in enumerate(('0', '10', 'CPU test', 'process', None, '.2',
                               'delivery', 'Delivery', 'Performance', 'doc')):
    element = ET.SubElement(row, 'sentinel' if value is None else 'string', id=str(index+1))
    if value is not None:
        element.text = value
        element.set('fmt', value)
second = ET.SubElement(node, 'row')
for index in range(10):
    ET.SubElement(second, 'string', ref=str(index+1))
parsed = m.summarize(xml, 'CPU test')
assert len(parsed) == 2 and parsed[0] == parsed[1]
assert parsed[0]['sum'] is None and parsed[0]['average'] == '.2'
try:
    m.summarize(xml, 'absent thread')
    raise AssertionError('missing thread accepted')
except ValueError:
    pass
print('Counter XML references/sentinels, weighting, overlap, missing and invalid-value checks pass')
