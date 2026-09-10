"""Exercise the allocation-free timing buffer with its single-writer contract."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='galaxypad-vi-timing-') as temporary:
    executable = str(Path(temporary)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/vi-timing-buffer.cpp'), '-o', executable], check=True)
    subprocess.run([executable], check=True)
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/vi-timing-recorder.cpp'), '-o', executable], check=True)
    subprocess.run([executable, temporary], check=True)
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/idle-wait-timing.cpp'), '-o', executable], check=True)
    subprocess.run([executable], check=True)
print('VI timing order, capacity, dropped samples, invalid clocks and joined writer pass')
print('Recorder disabled clock bypass, deferred export, restart and no-overwrite guards pass')
print('Idle wait exactly-once, disabled clock bypass, accumulation, reset and saturation pass')

with tempfile.TemporaryDirectory(prefix='galaxypad-completion-events-') as temporary:
    executable = str(Path(temporary)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/completion-events.cpp'), '-o', executable], check=True)
    subprocess.run([executable], check=True)
print('Separate completion writers, joined reads, capacity and disabled clock bypass pass')

with tempfile.TemporaryDirectory(prefix='galaxypad-completion-recorder-') as temporary:
    executable = str(Path(temporary)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/completion-recorder.cpp'), '-o', executable], check=True)
    subprocess.run([executable, temporary], check=True)
print('Completion recorder two-writer export, disabled/no-overwrite/restart/file-error guards pass')

with tempfile.TemporaryDirectory(prefix='galaxypad-recent-events-') as temporary:
    executable = str(Path(temporary)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/recent-completion-events.cpp'), '-o', executable], check=True)
    subprocess.run([executable], check=True, timeout=10)
print('Recent event chronological wrap, owner freeze, request handoff and clock bypass pass')

with tempfile.TemporaryDirectory(prefix='galaxypad-completion-trigger-') as temporary:
    executable = str(Path(temporary)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/completion-trigger.cpp'), '-o', executable], check=True)
    subprocess.run([executable], check=True, timeout=15)
print('Completion trigger arming, threshold, first-trigger retention and paired owner freeze pass')

with tempfile.TemporaryDirectory(prefix='galaxypad-flight-recorder-') as temporary:
    executable = str(Path(temporary)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/completion-flight-recorder.cpp'), '-o', executable], check=True)
    subprocess.run([executable, temporary], check=True, timeout=15)
print('Flight recorder arming/trigger/graphics-response metadata, joined export and no-overwrite pass')

with tempfile.TemporaryDirectory(prefix='galaxypad-flight-options-') as temporary:
    executable = str(Path(temporary)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(root/'tests/completion-flight-options.cpp'), '-o', executable], check=True)
    subprocess.run([executable], check=True)
print('Explicit arming parse/overflow and idle timestamp reuse with disabled bypass pass')
