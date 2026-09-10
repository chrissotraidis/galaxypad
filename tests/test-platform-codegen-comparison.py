#!/usr/bin/env python3
import importlib.util
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'scripts/compare-platform-codegen.py'
spec=importlib.util.spec_from_file_location('platform_codegen',path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def decoded(word='910143fd', op='add'):
    return m.parse(['00000010 <_func_80000000>:',
                    f' 10: {word}  {op}\tx29, sp, #0x50'], {'func_80000000'})

a=decoded()
r=m.compare(a,a)['func_80000000']
assert r['same_encoding_sequence'] and r['same_opcode_sequence']
r=m.compare(a,decoded('910147fd'))['func_80000000']
assert not r['same_encoding_sequence'] and r['same_opcode_sequence']
assert r['raw_encoding_matches_at_same_index']==0
r=m.compare(a,decoded('d10183ff','sub'))['func_80000000']
assert not r['same_opcode_sequence']
r=m.compare(a,{'func_80000000':a['func_80000000']*2})['func_80000000']
assert r['native_instructions']==1 and r['simulator_instructions']==2
assert not r['same_opcode_sequence'] and not r['same_encoding_sequence']
for lines in ([],['00000010 <_func_80000000>:'],
              ['00000010 <_func_80000000>:','00000020 <_func_80000000>:']):
    try:
        m.parse(lines,{'func_80000000'})
    except ValueError:
        pass
    else:
        raise AssertionError('Missing/empty/duplicate symbol accepted')
try:
    m.compare(a,{})
except ValueError:
    pass
else:
    raise AssertionError('Different symbol sets accepted')
print('Platform comparison preserves raw encoding/opcode distinction and rejects incomplete inputs')
