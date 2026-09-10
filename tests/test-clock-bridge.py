"""Check the actual clock bridge, not a different Python monotonic epoch."""
import csv
import io
from pathlib import Path
import subprocess
import tempfile
import time

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='galaxypad-clock-bridge-') as temporary:
    binary = Path(temporary) / 'probe'
    subprocess.run(['clang++', '-std=c++17', '-O1', '-fsanitize=address,undefined',
                    str(root/'scripts/clock-bridge.cpp'), '-o', str(binary)], check=True)
    for args in ([], ['0'], ['121'], ['1x'], [''], ['-1']):
        result = subprocess.run([str(binary), *args], capture_output=True)
        assert result.returncode == 2 and not result.stdout
    before = time.time_ns()
    output = subprocess.check_output([str(binary), '1'], text=True)
    after = time.time_ns()
    rows = [{k:int(v) for k,v in row.items()} for row in csv.DictReader(io.StringIO(output))]
    assert 2 <= len(rows) <= 12
    for row in rows:
        assert row['steady_before_ns'] <= row['steady_after_ns']
        assert before <= row['wall_unix_ns'] <= after
    assert all(a['steady_after_ns'] < b['steady_before_ns'] for a,b in zip(rows,rows[1:]))
    assert rows[-1]['steady_after_ns']-rows[0]['steady_before_ns'] >= 1_000_000_000
print('Clock bridge argument bounds, wall epoch, ordering and bounded capture pass')
