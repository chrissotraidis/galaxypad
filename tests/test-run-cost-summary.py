from pathlib import Path
import importlib.util

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('summary', root/'scripts/summarize-run-cost.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
fixture = '''[galaxypad-run-cost] capture-start pc=80004000
[galaxypad-run-cost] cpu_ns=256000 clock_errors=0 inclusion=256
[galaxypad-run-cost-lane] lane=0 spans=256 selected=1 completed=1 ns=500 squared_ns=250000 maximum_ns=500
[galaxypad-run-cost-lane] lane=1 spans=256 selected=1 completed=1 ns=100 squared_ns=10000 maximum_ns=100
'''
result = module.summarize(fixture)
assert result['lanes'][0]['estimated_cpu_fraction'] == 0.5
assert result['lanes'][1]['estimated_cpu_fraction'] == 0.1
assert not result['lanes'][0]['enough_samples_for_screening']
assert module.summarize(fixture + fixture, 1)['cpu_ns'] == 256000
assert module.summarize(fixture + fixture, 2)['selected_run'] == 2
try:
    module.summarize(fixture, 2)
except ValueError:
    pass
else:
    raise AssertionError('Missing Run selected')
for bad in (fixture + fixture, fixture.replace('clock_errors=0', 'clock_errors=1'),
            fixture.replace('completed=1', 'completed=0'), fixture.replace('lane=1', 'lane=0'),
            fixture.replace('squared_ns=250000', 'squared_ns=1'),
            fixture.replace('cpu_ns=256000', 'cpu_ns=0')):
    try:
        module.summarize(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid report accepted')
print('Run-cost estimates and incomplete/duplicate/clock/moment rejection pass')
