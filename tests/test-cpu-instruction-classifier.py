import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1]/'scripts/classify-cpu-instructions.py'
spec = importlib.util.spec_from_file_location('classifier', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
asm = ' 100: f946ce68 ldr x8, [x19, #0xd98]\n 104: 54000061 b.ne 0x110\n'
summary = {'addresses': [{'name': 'kernel', 'raw_offset': '0x101', 'samples': 3},
                         {'name': 'kernel', 'raw_offset': '0x105', 'samples': 2}]}
row = module.classify(summary, asm, ['kernel'])['kernel']
assert row == {'samples': 5, 'families': {'load': 3, 'branch': 2},
               'x19_memory_offsets': {'0xd98': 3}}
marked = {'addresses': summary['addresses'] + [
    {'name': 'kernel', 'raw_offset': '0x102', 'samples': 4},
    {'name': 'unrelated', 'raw_offset': '0xfff', 'samples': 99}]}
detail = module.classify(marked, asm, ['kernel'], details=True)['kernel']
assert detail['instructions'] == [
    {'offset': '0x100', 'samples': 7, 'opcode': 'ldr', 'operands': 'x8, [x19, #0xd98]'},
    {'offset': '0x104', 'samples': 2, 'opcode': 'b.ne', 'operands': '0x110'}]
assert sum(site['samples'] for site in detail['instructions']) == detail['samples'] == 9
assert module.family('blr') == 'call'
assert module.family('fadd') == 'scalar_fp'
assert module.family('fmov') == 'fp_move_or_conversion'
assert module.family('fcvt') == 'fp_move_or_conversion'
assert module.family('stp') == 'store'
try:
    module.classify(summary, '', ['kernel'])
except ValueError:
    pass
else:
    raise AssertionError('Missing instruction must fail closed')
print('Instruction join, marker alignment, weighted grouping and missing-PC tests pass')
journal = {0x100: ('adrp', 'x9, 0x6000 <_g_ppc_lazy_fp_enabled>'),
           0x104: ('ldr', 'x9, [x9, #0x8]')}
symbols = {0x6008: '_g_mem_write_journal'}
assert module.load_origin(journal, 0x104, symbols) == 'memory_write_journal_global_adjacent'
assert module.load_origin(journal, 0x104) == 'unresolved'
assert module.load_origin(journal, 0x104, {0x6000: '_g_mem_write_journal'}) == 'unresolved'
assert module.load_origin(journal, 0x104, {0x6008: '_other'}) == 'unresolved'
journal[0x100] = ('adrp', 'x8, 0x6000 <_g_mem_write_journal>')
assert module.load_origin(journal, 0x104, symbols) == 'unresolved'
print('Numeric global address attribution rejects misleading labels and wrong bases')

weighted = {'addresses': [dict(row, cycles=weight) for row, weight in
                         zip(summary['addresses'], [100, 0])]}
result = module.classify(weighted, asm, ['kernel'], details=True, weight_field='cycles')['kernel']
assert result['cycles'] == 100 and result['families'] == {'load':100, 'branch':0}
assert result['instructions'][0]['cycles'] == 100
assert module.classify(weighted, asm, ['kernel'])['kernel']['samples'] == 5
try:
    module.classify(summary, asm, ['kernel'], weight_field='cycles')
except KeyError:
    pass
else:
    raise AssertionError('Missing cycle weights must not silently become sample counts')
print('Cycle weights remain distinct from sample counts, including zero and missing weights')
