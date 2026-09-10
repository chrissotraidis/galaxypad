"""Exact-DOL fixed-plan test; no execution equivalence or speed claim."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
dol = root / 'generated/extracted/run1/sys/main.dol'
assert hashlib.sha256(dol.read_bytes()).hexdigest() == (
    '2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09')
with tempfile.TemporaryDirectory(prefix='galaxypad-vector-plan-') as directory:
    binary = str(Path(directory) / 'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(root/'tests/test-vector-plan.cpp'),
                    '-o', binary], check=True)
    subprocess.run([binary, str(dol)], check=True)
print('121 fixed vector entries and 3872 single-bit mutations pass; execution unproven')
