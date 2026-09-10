#!/usr/bin/env python3
"""Read-only host samples for a matched game run. Keep output private/ignored.

No process termination, priority changes, cache purging or privileged tools.
Cumulative VM counters are retained alongside interval deltas; swap allocation
and a thermal-warning query alone cannot establish current paging/throttling.
"""
import argparse
import json
import re
import subprocess
import time


def vm_counters(output):
    result = {}
    for line in output.splitlines():
        match = re.fullmatch(r'([^:]+):\s+(\d+)\.', line.strip())
        if match:
            result[match[1].strip('"')] = int(match[2])
    if not {'Swapins', 'Swapouts', 'Pageouts'} <= result.keys():
        raise ValueError('Incomplete vm_stat counters')
    return result


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=5)
    return dict(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=int, default=90)
    parser.add_argument('--interval', type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.interval <= args.seconds <= 3600:
        parser.error('Require 1 <= interval <= seconds <= 3600')
    start = time.monotonic()
    previous = None
    previous_time = None
    sample = 0
    while sample*args.interval <= args.seconds:
        deadline = start+sample*args.interval
        time.sleep(max(0, deadline-time.monotonic()))
        now = time.monotonic()
        vm = run(['vm_stat'])
        current = vm_counters(vm['stdout']) if vm['exit_code'] == 0 else None
        delta = None
        if current is not None and previous is not None:
            delta = {key:current[key]-previous[key] for key in
                     ('Swapins','Swapouts','Pageins','Pageouts','Compressions','Decompressions')}
        row = dict(elapsed_seconds=now-start, monotonic_ns=time.monotonic_ns(),
                   monotonic_raw_ns=time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW),
                   wall_time_ns=time.time_ns(),
                   interval_seconds=None if previous_time is None else now-previous_time,
                   vm=vm, vm_counter_delta=delta,
                   memory_pressure=run(['memory_pressure','-Q']),
                   swap=run(['sysctl','vm.swapusage']),
                   thermal_warnings=run(['pmset','-g','therm']),
                   processes=run(['ps','-axo','pid,pcpu,rss,comm','-r']))
        print(json.dumps(row), flush=True)
        previous, previous_time = current, now
        sample += 1


if __name__ == '__main__':
    main()
