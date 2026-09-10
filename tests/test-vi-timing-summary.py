import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('vi_summary', root/'scripts/summarize-vi-timing.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def row(wall, cpu, valid=1, efb=0, throttle=0):
    return dict(wall_ns=wall, thread_cpu_ns=cpu, cpu_clock_valid=valid,
                efb_elapsed_ns=efb, throttle_elapsed_ns=throttle)


rows = [row(0, 0), row(10, 5, efb=3, throttle=4), row(30, 12, efb=4, throttle=8),
        row(50, 0, 0), row(60, 2)]
result = module.summarize(rows, 10, 50)
assert result['vi_events'] == 2 and result['complete_intervals'] == 2
assert result['invalid_cpu_intervals'] == 1 and result['counter_reset_intervals'] == 1
assert result['interval_distributions']['cpu_ms']['valid'] == 1
assert result['interval_distributions']['cpu_ms']['missing'] == 1
assert result['interval_distributions']['cpu_ms']['mean_ms'] == 7/1e6
assert result['interval_distributions']['wall_ms']['valid'] == 2
assert result['longest_intervals'][0]['cpu_ms'] == 7/1e6
assert result['longest_intervals'][0]['efb_elapsed_ms'] == 1/1e6
assert result['longest_intervals'][0]['throttle_elapsed_ms'] == 4/1e6
assert result['longest_intervals'][0]['idle_wait_elapsed_ms'] is None
assert result['interval_distributions']['dvd_wait_elapsed_ms']['valid'] == 0
assert result['interval_distributions']['gather_wait_elapsed_ms']['valid'] == 0
assert result['interval_distributions']['wakeup_elapsed_ms']['valid'] == 0
for index, item in enumerate(rows):
    item['wakeup_elapsed_ns'] = index * 13
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['wakeup_elapsed_ms'] == 13/1e6
rows[2]['wakeup_elapsed_ns'] = 0
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['wakeup_elapsed_ms'] is None
for index, item in enumerate(rows):
    item['gather_wait_elapsed_ns'] = index * 11
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['gather_wait_elapsed_ms'] == 11/1e6
rows[2]['gather_wait_elapsed_ns'] = 0
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['gather_wait_elapsed_ms'] is None
for index, item in enumerate(rows):
    item['dvd_wait_elapsed_ns'] = index * 7
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['dvd_wait_elapsed_ms'] == 7/1e6
rows[2]['dvd_wait_elapsed_ns'] = 0
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['dvd_wait_elapsed_ms'] is None
for index, item in enumerate(rows):
    item['idle_wait_elapsed_ns'] = index * 2
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['idle_wait_elapsed_ms'] == 2/1e6
rows[2]['idle_wait_elapsed_ns'] = 0
assert module.summarize(rows, 10, 50)['longest_intervals'][0]['idle_wait_elapsed_ms'] is None
for bad_rows, start, end in ((rows, -1, 50), (rows, 10, 61), (rows, 10, 10),
                             (rows[::-1], 10, 50), (rows[:1], 10, 50)):
    try:
        module.summarize(bad_rows, start, end)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid window/order accepted')
print('VI complete-window boundaries, CPU validity and counter-reset guards pass')

stats = module.distribution([None, 1000/60, 20, 10, 30])
assert stats == dict(valid=4, missing=1, total_ms=60+1000/60,
                     mean_ms=(60+1000/60)/4, p50_ms=1000/60,
                     p95_ms=30, p99_ms=30, over_60hz_budget=2)
assert module.distribution([None])['total_ms'] is None
assert module.distribution([])['over_60hz_budget'] is None
assert module.distribution([3])['p99_ms'] == 3
print('VI distribution nearest-rank, missing-value and strict-budget guards pass')
