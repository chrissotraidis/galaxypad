"""Bounded private System Trace with an observed-free-space watchdog, not a disk quota."""
import argparse
import json
from pathlib import Path
import shutil
import signal
import subprocess
import time

GIB = 1024**3

def recorder_command(pid, output, seconds, thread_only=False):
    selection = (['--instrument', 'Thread State Trace'] if thread_only else
                 ['--template', 'System Trace'])
    return ['xcrun', 'xctrace', 'record', *selection, '--attach', str(pid),
            '--time-limit', f'{seconds}s', '--window', f'{seconds}s',
            '--output', str(output)]

def stop_reason(initial, available, elapsed, seconds):
    if available < 16*GIB:
        return 'free_space_reserve'
    if initial-available > 4*GIB:
        return 'observed_volume_growth'
    if elapsed > seconds+90:
        return 'recorder_timeout'
    return None

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=30)
    parser.add_argument('--thread-only', action='store_true',
                        help='Standalone Thread State Trace; dependencies still collect other events')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if not 1 <= args.seconds <= 60 or args.pid <= 0:
        parser.error('Positive PID and duration1..60 required')
    if not output.is_relative_to(root/'generated/runtime') or output.suffix != '.trace':
        parser.error('Output must be a private generated/runtime .trace path')
    log = output.with_suffix('.capture.log')
    record = output.with_suffix('.watchdog.json')
    if not output.parent.is_dir() or any(p.exists() for p in (output, log, record)):
        parser.error('Use an existing private directory and entirely new output paths')
    command = subprocess.check_output(['ps', '-p', str(args.pid), '-o', 'comm='], text=True).strip()
    if Path(command).name != 'GalaxyPadRunner':
        parser.error('Target is not GalaxyPadRunner')
    initial = shutil.disk_usage(output.parent).free
    if initial < 20*GIB:
        parser.error('At least20GiB available required before recording')
    argv = recorder_command(args.pid, output, args.seconds, args.thread_only)
    start = time.monotonic()
    reason = None
    signalled = None
    minimum = initial
    with log.open('x') as stream:
        process = subprocess.Popen(argv, stdout=stream, stderr=subprocess.STDOUT)
        while process.poll() is None:
            now = time.monotonic()
            available = shutil.disk_usage(output.parent).free
            minimum = min(minimum, available)
            if reason is None:
                reason = stop_reason(initial, available, now-start, args.seconds)
                if reason:
                    process.send_signal(signal.SIGINT)
                    signalled = now
            elif now-signalled > 30:
                process.kill()  # Only the recorder child, never the game or other tools.
                break
            time.sleep(1)
        code = process.wait()
    record.write_text(json.dumps(dict(command=argv, exit_code=code, stop_reason=reason,
        initial_available_bytes=initial, minimum_available_bytes=minimum,
        elapsed_seconds=time.monotonic()-start,
        caveat='Filesystem free-space watchdog, not a hard byte quota; other activity may trigger it. '
               'No trace or temporary data is deleted automatically.'), indent=2)+'\n')
    return 1 if reason or code else 0

if __name__ == '__main__':
    raise SystemExit(main())
