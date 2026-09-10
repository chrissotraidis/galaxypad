"""Pure clock-alignment and storage stop-policy regressions; no recording."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from scheduler_clock import calibrate, steady_bounds
from capture_scheduler import stop_reason, recorder_command, GIB

base = ['xcrun', 'xctrace', 'record']
tail = ['--attach', '123', '--time-limit', '10s', '--window', '10s', '--output', '/tmp/probe.trace']
assert recorder_command(123, Path('/tmp/probe.trace'), 10) == base + ['--template', 'System Trace'] + tail
assert recorder_command(123, Path('/tmp/probe.trace'), 10, True) == base + ['--instrument', 'Thread State Trace'] + tail

rows = [dict(steady_before_ns=100, steady_after_ns=110, wall_unix_ns=1005),
        dict(steady_before_ns=200, steady_after_ns=214, wall_unix_ns=1107)]
c = calibrate(rows)
assert c['offset_low_ns'] == 893 and c['offset_high_ns'] == 907
assert steady_bounds(c, 1050) == (143,157)
for action in (lambda:calibrate([]), lambda:calibrate(rows[::-1]),
               lambda:calibrate(rows, 10), lambda:steady_bounds(c,1004),
               lambda:steady_bounds(c,1108),
               lambda:calibrate([dict(rows[0],steady_after_ns=99),rows[1]])):
    try: action()
    except ValueError: pass
    else: raise AssertionError('Invalid calibration/coverage accepted')
assert stop_reason(30*GIB,29*GIB,10,30) is None
assert stop_reason(30*GIB,15*GIB,10,30)=='free_space_reserve'
assert stop_reason(30*GIB,25*GIB,10,30)=='observed_volume_growth'
assert stop_reason(30*GIB,29*GIB,121,30)=='recorder_timeout'
assert stop_reason(30*GIB,26*GIB,120,30) is None
print('Scheduler clock bounds, no extrapolation, disk reserve/growth/time guards pass')
