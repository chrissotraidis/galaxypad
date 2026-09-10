from pathlib import Path
import csv
import io
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='galaxypad-host-pressure-') as temporary:
    binary=Path(temporary)/'probe'
    subprocess.run(['clang++','-std=c++17','-O2','-pthread','-Wall','-Wextra',
                    '-fsanitize=address,undefined',str(root/'scripts/host-pressure-probe.cpp'),
                    '-o',str(binary)],check=True)
    capture=subprocess.run([str(binary),'1'],capture_output=True,text=True,check=True,timeout=5)
    rows=list(csv.DictReader(io.StringIO(capture.stdout)))
    assert 1<=len(rows)<=12
    for row in rows:
        assert None not in row and all(value is not None for value in row.values())
        assert int(row['valid'])==1 and int(row['end_ns'])>=int(row['start_ns'])
    for a,b in zip(rows,rows[1:]):
        assert int(b['start_ns'])>=int(a['end_ns'])
    for args in ([],['0'],['121'],['-1'],['junk'],['1','2']):
        result=subprocess.run([str(binary),*args],capture_output=True,timeout=5)
        assert result.returncode!=0 and not result.stdout
print('Host counters read without privilege escalation; bounded CSV, ordering and argument tests pass')
