"""Test a patch against pinned upstream headers, not an already modified checkout."""
from pathlib import Path
import json
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
dolphin = root/'ref/ModernGekko/vendor/dolphin'
pin = json.loads((root/'config/dependencies.lock.json').read_text())['repositories']['recompCore']['upstreamRevision']
with tempfile.TemporaryDirectory(prefix='galaxypad-completion-observer-') as temporary:
    stage = Path(temporary)
    common = stage/'Source/Core/Common'
    common.mkdir(parents=True)
    for name in ('BlockingLoop.h', 'Event.h', 'Flag.h'):
        data = subprocess.check_output(['git', '-C', str(dolphin), 'show',
                                        f'{pin}:Source/Core/Common/{name}'])
        (common/name).write_bytes(data)
    subprocess.run(['git', 'apply', str(root/'patches/experiments/completion-observer.patch')],
                   cwd=stage, check=True)
    executable = stage/'test'
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    '-I'+str(stage/'Source/Core'), str(root/'tests/completion-observer.cpp'),
                    '-o', str(executable)], check=True)
    subprocess.run([str(executable)], check=True, timeout=20)
print('Pinned completion observer: enabled/disabled wait, wakeup, notification pairs and stop pass')
