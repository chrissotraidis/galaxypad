from pathlib import Path
import importlib.util

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('summary', root/'scripts/summarize-fallback-sample.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
fixture = '''Call graph:
    10 Thread_1: CPU thread
    + 10 thread_start  (in libc)
    +   4 Interpreter::SingleStepInner()  (in app)
    +   ! 3 Interpreter::mtspr()  (in app)
    +   3 func_game  (in module)
    +   2 __psynch_cvwait  (in libc)
    +   1 PowerPC::MMU::Read()  (in app)
    10 Thread_2: other
'''
result = module.summarize(fixture)
assert result['groups'] == dict(interpreter_stack=4, other=3, recognized_wait=2,
                               shared_mmu_icache_hle_unattributed=1)
for bad in (fixture.replace('! 3 Interpreter', '! 5 Interpreter'),
            fixture.replace('+ 10 thread_start', '+ 9 thread_start')):
    try:
        module.summarize(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Malformed tree accepted')
print('Sample accounting preserves self/inclusive distinction and rejects inconsistent trees')

symbols = '''Call graph:
    20 Thread_1: CPU thread
    + 20 StaticRecompCore::Run()  (in app)
    +   16 chassis_dispatch  (in module)
    +   ! 10 func_80001234  (in module)
    +   ! : 3 ppc_helper  (in module)
    +   ! 4 moderngekko::ModManager::Dispatch(CPUState*, unsigned int)  (in app)
    20 Thread_2: Video thread
    + 20 func_80001234  (in module)
'''
result = module.summarize(symbols)
assert result['symbol_self_buckets'] == dict(host_run_symbol=4, module_dispatch_symbol=2,
    generated_chunks_including_inlined_work=7, out_of_line_ppc_helpers=3,
    hook_routing_symbols=4)
assert result['generated_chunks'] == [dict(name='func_80001234', samples=7)]
assert sum(result['symbol_self_buckets'].values()) == 20
print('Symbol buckets conserve CPU-only self counts and exclude helper children/video samples')
