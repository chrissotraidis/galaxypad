"""Exercise the actual output-normalization block before changing cwd."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'scripts/build-module.sh').read_text()
block = 'output=' + source.split('\noutput=', 1)[1].split('\nchunk_instructions=', 1)[0]
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp) / 'project with spaces'
    for value, expected in [(None, str(base/'generated/modules')),
                            ('generated/custom cache', str(base/'generated/custom cache')),
                            (str(Path(tmp)/'absolute cache'), str(Path(tmp)/'absolute cache'))]:
        env = dict(os.environ, TEST_PROJECT_ROOT=str(base))
        env.pop('GALAXYPAD_MODULE_OUTPUT', None)
        if value is not None:
            env['GALAXYPAD_MODULE_OUTPUT'] = value
        result = subprocess.check_output(['bash', '-eu', '-c',
            'root="$TEST_PROJECT_ROOT"\n' + block + '\ncd /\nprintf "%s" "$output"'], env=env).decode()
        assert result == expected, (result, expected)
print('Module output default/relative/absolute paths survive cwd changes')
