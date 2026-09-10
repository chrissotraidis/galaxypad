#!/usr/bin/env python3
"""Bounded, profiler-free host/frame capture; keep the visible scene unchanged."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import time


def vm_counters(raw):
    return {name.strip(): int(value) for name, value in
            re.findall(r'^([^:\n]+):\s+(\d+)\.', raw, re.M)}


def frame_summary(lines, start, end):
    windows = []
    for line in lines.splitlines():
        if '[GalaxyPad frame window]' not in line:
            continue
        stamp = datetime.strptime(line[:23], '%Y-%m-%d %H:%M:%S.%f').timestamp()
        values = dict(re.findall(r'(\w+)=([\d.]+)', line))
        seconds = float(values['seconds'])
        # Discard boundary windows: they include time outside the capture.
        if stamp - seconds < start or stamp > end:
            continue
        windows.append(dict(epoch=stamp, seconds=seconds,
                            presented=int(values['presented']),
                            min_observed_fps=float(values['min_observed_fps']),
                            vi_rate_estimate=(float(values['vi_rate_estimate'])
                                              if 'vi_rate_estimate' in values else None),
                            emulation_speed_estimate=(float(values['emulation_speed_estimate'])
                                                      if 'emulation_speed_estimate' in values else None)))
    duration = sum(w['seconds'] for w in windows)
    return dict(windows=windows, covered_seconds=duration,
                weighted_presented_fps=(sum(w['presented'] for w in windows) / duration
                                        if duration else None))


def run(argv):
    return subprocess.check_output(argv, text=True, timeout=5).strip()


def snapshot(pid):
    before = time.time()
    identity = run(['ps', '-p', str(pid), '-o', 'lstart=,comm='])
    vm = run(['vm_stat'])
    process = run(['ps', '-p', str(pid), '-o', 'pid=,time=,%cpu=,rss='])
    # ps %CPU is a recent average, not CPU utilization for this exact interval.
    peers = run(['ps', '-axo', 'pid=,%cpu=,rss=,comm='])
    busiest = sorted(peers.splitlines(), key=lambda row: float(row.split()[1]),
                     reverse=True)[:8]
    return dict(before_epoch=before, after_epoch=time.time(), identity=identity,
                vm=vm_counters(vm), process=process, busiest_processes=busiest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--scene', required=True)
    parser.add_argument('--seconds', type=int, default=30)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if not 10 <= args.seconds <= 45 or args.pid <= 0:
        parser.error('Use a positive PID and 10..45 seconds')
    if not args.output.resolve().is_relative_to(root / 'generated'):
        parser.error('Output must remain in private generated/')
    if args.output.exists():
        parser.error('Refusing to overwrite evidence')
    executable = Path(run(['ps', '-p', str(args.pid), '-o', 'comm=']))
    if executable.name not in ('GalaxyPad', 'GalaxyPadRunner'):
        parser.error('Target is not a GalaxyPad runtime')
    with args.log.open() as stream:
        stream.seek(0, 2)
        first = snapshot(args.pid)
        print('Capture started; keep the scene unchanged, no build or profiler.', flush=True)
        time.sleep(args.seconds)
        last = snapshot(args.pid)
        lines = stream.read()
    if first['identity'] != last['identity']:
        raise SystemExit('Process identity changed; measurement rejected')
    keys = ('Swapins', 'Swapouts', 'Compressions', 'Decompressions')
    deltas = {key: last['vm'][key] - first['vm'][key] for key in keys}
    if any(value < 0 for value in deltas.values()):
        raise SystemExit('VM counter regression; measurement rejected')
    record = dict(scene=args.scene, captured_utc=datetime.now(timezone.utc).isoformat(),
                  pid=args.pid, log=str(args.log.resolve()), first=first, last=last,
                  vm_page_deltas=deltas,
                  frames=frame_summary(lines, first['after_epoch'], last['before_epoch']),
                  raw_frame_log=lines,
                  caveat='System VM deltas are not per-process causation. ps CPU is a recent '
                         'average. Legacy presented/FPS fields count after_frame_event, not '
                         'display completion, VI or source frames. Cadence estimates use upstream '
                         'rolling windows, not this capture interval. Log timestamps '
                         'are interpreted in the host local timezone. No audio or hardware proof.')
    with args.output.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(vm_page_deltas=deltas, frames=record['frames']), indent=2))


if __name__ == '__main__':
    main()
