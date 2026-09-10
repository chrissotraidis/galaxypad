"""Read-only public thermal probe bounds, schema and timestamp checks."""
import csv
import io
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='galaxypad-thermal-') as temporary:
    binary = Path(temporary)/'probe'
    subprocess.run(['clang++','-std=c++17','-O2','-Wall','-Wextra',
                    '-fsanitize=address,undefined','-framework','Foundation',
                    str(root/'scripts/thermal-state-probe.mm'),'-o',str(binary)],check=True)
    for args in ([],['0'],['121'],['-1'],['junk'],['1x'],[''],['1','2']):
        result=subprocess.run([str(binary),*args],capture_output=True,timeout=5)
        assert result.returncode==2 and not result.stdout
    result=subprocess.run([str(binary),'1'],capture_output=True,text=True,check=True,timeout=10)
    assert 'unsupported' in result.stdout and 'no frequency inference' in result.stdout
    rows=list(csv.DictReader(io.StringIO('\n'.join(line for line in result.stdout.splitlines() if not line.startswith('#')))))
    assert len(rows)==2
    previous=0
    for row in rows:
        begin,end=int(row['start_ns']),int(row['end_ns'])
        assert previous<=begin<=end
        previous=end
        assert int(row['thermal_state']) in range(4)
        assert int(row['low_power_mode']) in (0,1)
print('Thermal probe bounds, sanitizer, schema and monotonic query intervals pass')
