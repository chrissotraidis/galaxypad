import copy
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('work', Path(__file__).resolve().parents[1]/'scripts/summarize-process-work.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
a = dict(pid=1, start_abstime=5, before_ns=10, after_ns=12, instructions=100, cycles=50)
b = dict(pid=1, start_abstime=5, before_ns=30, after_ns=32, instructions=400, cycles=150)
capture = dict(first=a, last=b)
stamps = [0, 11, 20, 31, 40]
r = m.summarize(capture, stamps)
assert (r['vi_count_min'], r['vi_count_max']) == (1, 3)
assert r['per_vi_ranges']['instructions'] == [100, 300]
for field, value in [('pid', 2), ('start_abstime', 6), ('instructions', 99), ('before_ns', 9)]:
    bad = copy.deepcopy(capture); bad['last'][field] = value
    try:
        m.summarize(bad, stamps)
        raise AssertionError('invalid capture accepted')
    except ValueError:
        pass
for bad in ([11, 20, 31], [0, 20, 20, 40], []):
    try:
        m.summarize(capture, bad)
        raise AssertionError('invalid VI sequence accepted')
    except ValueError:
        pass
print('Process-work identity, reset, VI coverage and uncertain boundary tests pass')

tail = m.summarize_recording(capture, stamps, 2, verified_prefix_capacity=5)
assert tail['recording']['dropped'] == 2
assert tail['recording']['retained_tail_margin_ns'] == 8
assert tail['per_vi_ranges'] == r['per_vi_ranges']
for seq, dropped, capacity in [(stamps,2,None),(stamps,2,4),
                                (stamps,-1,5),([0,11,20,25,29],2,5)]:
    try:
        m.summarize_recording(capture,seq,dropped,capacity)
    except ValueError:
        pass
    else:
        raise AssertionError('Unverified prefix or uncovered window accepted')
print('Verified append-only tail retains drop metadata; default, capacity and coverage failures reject')
