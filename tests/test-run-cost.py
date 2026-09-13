from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp'
assert (core/'RunCost.h').read_bytes() == (root/'apple/experiments/run-cost/sampler.h').read_bytes()
run = (core/'StaticRecompCore_Run.cpp').read_text()
assert run.count('RunCost::Scope cost_span(') == 2
native = run.index('RunLane::Native);')
assert run.index('SyncIn();', native) < run.index('RunLane::NonNativeRouting);')
assert run.index('SyncOut();', native) < run.index('RunLane::NonNativeRouting);')
assert run.index('run_cost->Report(stderr)') > run.rindex('interpreter.SingleStepInner();')
assert 'std::strcmp(cost_enabled, "1") == 0' in run
assert 'cost_marker && *cost_marker' in run
assert 'cost_start_file.clear();' in run
with tempfile.TemporaryDirectory(prefix='galaxypad-run-cost-') as directory:
    binary = str(Path(directory)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(root/'tests/test-run-cost.cpp'),
                    '-o', binary], check=True)
    subprocess.run([binary], check=True)

print('Sparse run-cost accounting, null opt-out, early exits and failed clocks pass')
