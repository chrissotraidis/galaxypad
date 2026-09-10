"""Actual build entry points reject unsafe generation before tools or writes."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    for script, args in [('generate-aot.sh', []),
                         ('generate-aot.sh', ['--preflight']),
                         ('build-module.sh', [])]:
        for value in ('1', '0', '', None):
            env = dict(os.environ,
                       GALAXYPAD_DOLRECOMP_BIN=str(base/'absent-tool'),
                       GALAXYPAD_AOT_OUTPUT=str(base/'aot-output'),
                       GALAXYPAD_MODULE_OUTPUT=str(base/'module-output'),
                       GALAXYPAD_DESKTOP_BUILD=str(base/'desktop'))
            env.pop('DOLRECOMP_UNSAFE_DIRECT_CALLS', None)
            if value is not None:
                env['DOLRECOMP_UNSAFE_DIRECT_CALLS'] = value
            result = subprocess.run(['bash', str(root/'scripts'/script), *args],
                                    env=env, text=True, capture_output=True, timeout=10)
            assert result.returncode != 0
            expected = ('unsafe cross-chunk direct calls' if value == '1'
                        else 'missing built DolRecomp')
            assert expected in result.stderr, (script, value, result.stderr)
            assert list(base.iterdir()) == [], 'Guard must run before output creation'
print('Unsafe direct-call opt-in refused by generation/preflight/module entry points')
