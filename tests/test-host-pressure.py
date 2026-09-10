"""VM counter parsing must not confuse page gauges with paging rates."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1]/'scripts/record-host-pressure.py'
spec = importlib.util.spec_from_file_location('host_pressure', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
parsed = module.vm_counters('''Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free: 17.
"Translation faults": 1234.
Swapins: 50.
Swapouts: 70.
Pageouts: 3.
''')
assert parsed == {'Pages free':17, 'Translation faults':1234, 'Swapins':50, 'Swapouts':70, 'Pageouts':3}
try:
    module.vm_counters('Swapins: 50.\n')
except ValueError:
    pass
else:
    raise AssertionError('Incomplete snapshots must not imply zero paging')
print('Host VM parser: page gauges/cumulative counters and missing-data rejection pass')
