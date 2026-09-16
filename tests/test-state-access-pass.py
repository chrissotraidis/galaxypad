#!/usr/bin/env python3
"""Execute the maintained compiler pass's IR differential tests, ROM-free."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
compiler = root / 'ref/ModernGekko/vendor/dolphin/DolRecomp'
sources = [compiler / path for path in (
    'src/ir/dolir.c', 'src/ir/state_access.c', 'tests/test_state_access.c')]
with tempfile.TemporaryDirectory(prefix='galaxypad-state-access-') as directory:
    for mode, flags in [('optimized', ['-O2']), ('sanitized', ['-O1', '-g', '-fsanitize=address,undefined'])]:
        output = Path(directory) / mode
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        *flags, '-I', str(compiler / 'src'),
                        *map(str, sources), '-o', str(output)], check=True)
        subprocess.run([str(output)], check=True)
