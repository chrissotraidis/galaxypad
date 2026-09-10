import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1]/'scripts/summarize-scene-trace.py'
spec = importlib.util.spec_from_file_location('scene_trace', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
def row(t, event='vi_end_field'):
    return dict(steady_ns=str(t), event=event, value='0')
rows = [row(0),row(1_000_000_000),row(59_000_000_000),row(60_000_000_000)]
result = module.summarize(rows,0,2)
assert result['complete_minutes']==1
assert result['bins'][0]['count']==3
assert result['event']=='vi_end_field'
assert result['bins'][0]['max_gap_ms']==58000
assert module.summarize(rows[:-1],0,2)['bins']==[]
assert module.summarize(rows+[row(120_000_000_000,'audio_callback')],0,2)['complete_minutes']==2
assert module.summarize([dict(steady_ns='',event=None,value=None)],0)['bins']==[]
mixed = rows + [row(2_000_000_000, 'present_done'),
                row(60_000_000_000, 'present_done')]
present = module.summarize(mixed,0,2,'present_done')
assert present['bins'][0]['count']==1
assert present['bins'][0]['hz']==1/60
assert module.summarize(mixed,0,2,'frame_begin')['bins'][0]['count']==0
assert module.summarize(mixed,0,2)['bins'][0]['count']==3
try:
    module.summarize(rows,0,2,'unrecognized')
except ValueError:
    pass
else:
    raise AssertionError('Unknown cadence event accepted')
print('Complete-window, half-open boundary, event separation and trailing-line tests pass')
