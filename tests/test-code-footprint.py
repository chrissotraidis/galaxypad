import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('footprint', Path(__file__).resolve().parents[1]/'scripts/summarize-code-footprint.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = {'address_binary': 'fixture', 'addresses': [
    {'raw_offset': '0x1', 'samples': 4},
    {'raw_offset': '0x3', 'samples': 1},
    {'raw_offset': '0x40', 'samples': 3},
    {'raw_offset': '0x1000', 'samples': 2},
    {'raw_offset': '0x2000', 'samples': 0}]}
r = module.summarize(data, 64)
assert r['samples'] == 10 and r['distinct_aligned_pcs'] == 3
assert r['sampled_blocks'] == 3
assert r['blocks_covering_percent'] == {'50': 1, '90': 3, '99': 3}
assert module.summarize(data, 4096)['sampled_blocks'] == 2
assert module.summarize({'addresses': []}, 64)['blocks_covering_percent']['99'] == 0
for size in (0, 3, 63):
    try:
        module.summarize(data, size)
        raise AssertionError('accepted invalid block size')
    except ValueError:
        pass
print('Sampled footprint alignment, aggregation, coverage and empty-input checks pass')
