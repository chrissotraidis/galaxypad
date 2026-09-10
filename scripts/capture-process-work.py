#!/usr/bin/env python3
"""Two bounded process-wide snapshots; caller verifies scene and closes runtime."""
import argparse
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('pid', type=int)
parser.add_argument('profile', type=Path)
parser.add_argument('--probe', type=Path, required=True)
parser.add_argument('--executable', type=Path,
                    help='exact executable for a non-runner target; profile is the output directory')
args = parser.parse_args()
profile = args.profile.resolve()
command = subprocess.check_output(['ps', '-p', str(args.pid), '-o', 'command='], text=True)
if args.executable:
    executable = subprocess.check_output(['ps', '-p', str(args.pid), '-o', 'comm='], text=True).strip()
    if Path(executable).resolve() != args.executable.resolve() or not args.executable.is_file():
        raise SystemExit('PID is not the requested executable')
elif str(profile) not in command or 'GalaxyPadRunner' not in command:
    raise SystemExit('PID is not the requested GalaxyPad profile')
output = profile/'process-work.json'
if output.exists():
    raise SystemExit('refusing to overwrite existing measurement')
# The caller establishes scene and foreground state. Measurement must not change it.
time.sleep(10)
def snapshot():
    return json.loads(subprocess.check_output([str(args.probe.resolve()), str(args.pid)], timeout=5))
first = snapshot()
time.sleep(30)
last = snapshot()
if (first['pid'], first['start_abstime']) != (last['pid'], last['start_abstime']):
    raise SystemExit('process identity changed')
if first['after_ns'] >= last['before_ns'] or any(last[k] < first[k] for k in ('instructions', 'cycles')):
    raise SystemExit('clock/counter regression')
with output.open('x') as destination:
    json.dump({'command': command.strip(), 'first': first, 'last': last,
               'scope': 'whole process; normalize to bracketed VI counts after clean exit'}, destination, indent=2)
print('Two process snapshots complete after warm-up; inspect scene and close exact runtime PID')
