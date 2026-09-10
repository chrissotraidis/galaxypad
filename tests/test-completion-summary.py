import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion', root/'scripts/summarize-completion-timing.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def row(stream, kind, wall, cpu=0, valid=1):
    return dict(stream=stream, kind=kind, wall_ns=wall, thread_cpu_ns=cpu, cpu_clock_valid=valid)


rows = [row('cpu', 'wait_begin', 0), row('cpu', 'wait_end', 100, 20),
        row('cpu', 'wait_begin', 110), row('cpu', 'wait_end', 120, 0, 0),
        row('graphics', 'before_notify', 0), row('graphics', 'after_notify', 1),
        row('graphics', 'before_notify', 90), row('graphics', 'after_notify', 91),
        row('graphics', 'before_notify', 130), row('graphics', 'after_notify', 131)]
result = module.summarize(rows, 0, 120)
assert result['complete_waits'] == 2
assert result['longest_waits'][0]['cpu_ms'] == 20/1e6
assert len(result['longest_waits'][0]['notifications_within']) == 4
assert result['longest_waits'][0]['next_notification']['wall_ns'] == 130
assert result['longest_waits'][1]['cpu_ms'] is None
assert module.summarize(rows, 1, 120)['complete_waits'] == 1
for events, start, end in ((rows, -1, 120), (rows, 0, 132), (rows, 10, 10),
                           (rows[1:], 0, 120), (rows[:4]+rows[5:], 1, 120)):
    try:
        module.summarize(events, start, end)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid or incomplete stream accepted')
print('Completion window coverage, boundary pairing, adjacent observations and CPU validity pass')

meta = dict(flight_version=1, triggered=1, graphics_frozen=1, not_before_ns=0,
            threshold_ns=20, trigger_start_ns=0, trigger_end_ns=100,
            invalid_waits=0, cpu_overwritten=10, graphics_overwritten=20)
def header(values):
    return '# ' + ' '.join(f'{k}={v}' for k, v in values.items())
flight_rows = rows[:2]+rows[4:]
assert module.summarize_flight(header(meta), flight_rows)['status'] == 'trigger_context_retained'
assert module.summarize_flight(header(dict(meta, triggered=0, graphics_frozen=0,
                                          trigger_end_ns=0)), [])['status'] == 'not_triggered'
assert module.summarize_flight(header(dict(meta, graphics_frozen=0)), flight_rows)['status'] == 'graphics_response_missing'
for changed, events in ((dict(meta, flight_version=2), flight_rows),
                        (dict(meta, not_before_ns=1), flight_rows),
                        (dict(meta, threshold_ns=101), flight_rows),
                        (dict(meta, invalid_waits=1), flight_rows),
                        (dict(meta, trigger_end_ns=99), flight_rows),
                        (meta, flight_rows[:-2]), (meta, flight_rows[:-1])):
    try:
        module.summarize_flight(header(changed), events)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid flight capture accepted')
print('Flight trigger/no-response metadata, arming, endpoints and retained context guards pass')
