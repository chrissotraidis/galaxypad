"""Capture identity checks and unchanged foreground state, without a live game."""
import json
from pathlib import Path
import runpy
import sys
import tempfile
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / 'scripts/capture-process-work.py'
with tempfile.TemporaryDirectory() as directory:
    profile = Path(directory).resolve()
    executable = profile / 'GalaxyPad'
    executable.touch()
    first = dict(pid=42, start_abstime=10, before_ns=100, after_ns=101,
                 instructions=100, cycles=200)
    last = dict(first, before_ns=200, after_ns=201, instructions=200, cycles=400)
    for mobile in (False, True):
        responses = [f'GalaxyPadRunner --user-dir {profile}']
        argv = [str(script), '42', str(profile), '--probe', str(executable)]
        if mobile:
            argv += ['--executable', str(executable)]
            responses += [str(executable)]
        responses += [json.dumps(first).encode(), json.dumps(last).encode()]
        with patch.object(sys, 'argv', argv), \
             patch('subprocess.check_output', side_effect=responses) as query, \
             patch('subprocess.run', side_effect=AssertionError('must not change focus')), \
             patch('time.sleep'):
            runpy.run_path(str(script), run_name='__main__')
        output = profile / 'process-work.json'
        assert json.loads(output.read_text())['last'] == last
        output.unlink()
        assert query.call_count == (4 if mobile else 3)
    with patch.object(sys, 'argv', argv), \
         patch('subprocess.check_output', side_effect=['other', '/wrong/executable']), \
         patch('time.sleep', side_effect=AssertionError('must reject before waiting')):
        try:
            runpy.run_path(str(script), run_name='__main__')
        except SystemExit as error:
            assert 'requested executable' in str(error)
        else:
            raise AssertionError('wrong PID accepted')
print('Native/mobile capture identity, snapshots and no-focus-change checks pass')
