"""Exercise bounded read-only thread observation on a controlled local worker."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='galaxypad-thread-state-') as temporary:
    binary = Path(temporary) / 'probe'
    subprocess.run(['clang++', '-std=c++17', '-O2', '-pthread', '-Wall', '-Wextra',
                    '-fsanitize=address,undefined', str(root / 'scripts/thread-state-probe.cpp'),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary), '--self-test'], check=True, timeout=10)
    for args in ([], ['-1','1','2'], ['1','121','2'], ['1','1','1'],
                 ['1','1','101'], ['junk','1','2'], [str(os.getpid()),'1','2']):
        result = subprocess.run([str(binary), *args], capture_output=True, timeout=5)
        assert result.returncode != 0 and not result.stdout, (args,result)
print('Thread probe sanitizer, bounds, malformed args and non-runner rejection pass')
