import importlib.util
import plistlib
from pathlib import Path

path = Path(__file__).resolve().parents[1]/'scripts/audit-trace-window.py'
spec = importlib.util.spec_from_file_location('trace_window', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
obj = dict(_rawStartTime=100., _rawEndTime=161.,
           _rawWindowStartTime=151., _rawDuration=plistlib.UID(1))
archive = {'$objects': [obj, 10.]}
result = module.audit(archive)[0]
assert result['recording_seconds'] == 61
assert result['discarded_prefix_seconds'] == 51
assert result['retained_seconds'] == 10
for key, bad in [('_rawWindowStartTime', 99.), ('_rawDuration', 60.),
                 ('_rawEndTime', float('nan'))]:
    modified = dict(obj, **{key: bad})
    try:
        module.audit({'$objects': [modified, 10.]})
    except ValueError:
        pass
    else:
        raise AssertionError(f'Invalid {key} accepted')
try:
    module.audit({'$objects': []})
except ValueError:
    pass
else:
    raise AssertionError('Missing window accepted')
print('Retained trace window, references and invalid timing guards pass')
