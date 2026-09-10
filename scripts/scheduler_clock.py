"""Observed wall/VI-clock offset envelope; refuse missing coverage or broad drift."""

def calibrate(rows, max_span_ns=1_000_000):
    if len(rows) < 2:
        raise ValueError('Need contemporary clock pairs before and after capture')
    for row in rows:
        if row['steady_before_ns'] > row['steady_after_ns']:
            raise ValueError('Reversed clock bracket')
    for a, b in zip(rows, rows[1:]):
        if a['steady_after_ns'] >= b['steady_before_ns'] or a['wall_unix_ns'] >= b['wall_unix_ns']:
            raise ValueError('Clocks must strictly advance')
    low = min(r['wall_unix_ns']-r['steady_after_ns'] for r in rows)
    high = max(r['wall_unix_ns']-r['steady_before_ns'] for r in rows)
    if high-low > max_span_ns:
        raise ValueError('Clock drift/query uncertainty exceeds allowed envelope')
    return dict(offset_low_ns=low, offset_high_ns=high,
                wall_start_ns=rows[0]['wall_unix_ns'], wall_end_ns=rows[-1]['wall_unix_ns'],
                observed_span_ns=high-low,
                caveat='Observed envelope only; unsampled clock steps are not ruled out.')

def steady_bounds(calibration, wall_ns):
    if not calibration['wall_start_ns'] <= wall_ns <= calibration['wall_end_ns']:
        raise ValueError('No contemporaneous clock coverage; refusing extrapolation')
    return (wall_ns-calibration['offset_high_ns'], wall_ns-calibration['offset_low_ns'])
