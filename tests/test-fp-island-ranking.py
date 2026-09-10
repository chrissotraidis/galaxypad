#!/usr/bin/env python3
import hashlib
import importlib.util
from pathlib import Path
import tempfile

spec = importlib.util.spec_from_file_location('islands', Path(__file__).resolve().parents[1] / 'scripts/rank-fp-islands.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'chunk.c'
    # Include an outlined duplicate before the selected function.
    text = 'label_00001000:\n// 00001000: wrong\nvoid func_test(CPUState* ctx) {\n'
    entries = []
    for pc, mnemonic, count in [(0x1000,'fmuls',5),(0x1004,'ps_madd',6),
                                (0x1008,'lfs',6),(0x100c,'fmuls',0),
                                (0x1010,'fmuls',0),(0x1014,'fmuls',None),
                                (0x1018,'fmuls',7),(0x1020,'fmuls',7)]:
        label = f'label_{pc:08X}:'
        text += f'{label}\n// {pc:08X}: {mnemonic} f0,f1,f2\nppc_test(ctx);\n'
        entries.append(dict(label=label,count=count))
    path.write_text(text)
    data = dict(filenames=[str(path)],chunk_sha256=hashlib.sha256(text.encode()).hexdigest(),
                profile_sha256='fixture',function_name='func_test',instruction_entries=entries)
    result = module.rank(data)['islands']
    assert len(result) == 2
    assert result[0]['entry_attempts'] == 11 and result[0]['length'] == 2
    assert result[0]['minimum_site_count'] == 5 and result[0]['maximum_site_count'] == 6
    assert result[1]['entry_attempts'] == 0
    assert result[0]['instructions'][0]['helpers'] == ['ppc_test']
    larger = module.rank(data, include_memory=True)
    assert larger['include_memory']
    assert len(larger['islands']) == 1
    span = larger['islands'][0]
    assert span['length'] == 5 and span['entry_attempts'] == 17
    assert span['memory_observers'] == ['00001008']
    assert span['instructions'][2]['memory_observer']
    assert not span['instructions'][0]['memory_observer']
    assert 'not proven routines' in larger['caveat']
    path.write_text(text + '\n')
    try:
        module.rank(data)
    except ValueError as error:
        assert 'Source changed' in str(error)
    else:
        raise AssertionError('Changed source accepted')
print('FP island ranking: boundaries, gaps, unknown versus zero, scope and hashes pass')
