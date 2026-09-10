import importlib.util
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prepare',ROOT/'scripts/prepare-native-observer.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
source='#include "../RMGE01.h"\nvoid func_80002000(CPUState* ctx) {\nlabel_80002004:\n    ctx->pc = 0x80002004u;\n    ctx->gpr[3]++;\n}\n'
candidate=module.instrument(source,0x80002004)
assert candidate.index('ctx->pc =')<candidate.index('galaxypad_native_observe(ctx,')<candidate.index('ctx->gpr[3]++')
for bad in [candidate,source.replace('label_80002004:','label_80002008:'),source+source,
            source.replace('void func_80002000','static void loop_80002000')+'void func_80003000() {}']:
    try: module.instrument(bad,0x80002004)
    except ValueError: pass
    else: raise AssertionError('Malformed or duplicate instrumentation accepted')
print('Observer preparation: exact location, duplicate/missing/helper rejection pass')
