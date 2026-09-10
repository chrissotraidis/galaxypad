"""Run existing threaded completion cases through the installed notification hook."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'tests/completion-observer.cpp').read_text()
assert source.count('loop.Wakeup();') == 1
source = source.replace('loop.Wakeup();',
                        'loop.WakeupWithNotification([](Common::Event& event) { event.Set(); });')
with tempfile.TemporaryDirectory(prefix='galaxypad-wakeup-threaded-') as temporary:
    path = Path(temporary) / 'probe.cpp'
    path.write_text(source)
    binary = Path(temporary) / 'probe'
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    '-I' + str(root / 'ref/ModernGekko/vendor/dolphin/Source/Core'),
                    str(path), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=20)
print('Installed notification hook: threaded payload, completion, wait and stop cases pass')
