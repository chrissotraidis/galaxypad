"""Guard the private compact helper extraction and its deliberately narrow ABI."""
from pathlib import Path
import importlib.util

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('compact',root/'scripts/compact_fp_state.py')
compact=importlib.util.module_from_spec(spec);spec.loader.exec_module(compact)
source=(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu_interpreter_float.c').read_text()
code,names,manifest=compact.build(source)
assert len(names)==25
assert set(compact.ROOTS)<=names.keys()
assert manifest['fields']==['fpr','fpscr','ps1']
assert 'CPUState' not in code
assert not any(name in code for name in ['mem_read','mem_write','ppc_take_exception'])
assert code.startswith('typedef struct { f64 fpr[7], ps1[7]; u32 fpscr; } CompactFPState;')
try:
    compact.build(source+'\n')
except AssertionError:
    pass
else:
    raise AssertionError('Changed source accepted')
print('25 exact reversible helper bodies; compact fields and changed-source refusal pass')
