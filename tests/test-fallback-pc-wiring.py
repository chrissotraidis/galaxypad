"""Source-boundary checks plus actual histogram sanitizer test; not runtime proof."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root / 'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp'
assert (core/'FallbackHistogram.h').read_bytes() == (
    root/'apple/experiments/fallback-pcs/histogram.h').read_bytes()
run = (core/'StaticRecompCore_Run.cpp').read_text()
hooks = (core/'StaticRecompCore_Hooks.cpp').read_text()
life = (core/'StaticRecompCore.cpp').read_text()
assert run.count('m_fallback_histogram->Record(') == 2
for path in ('Forced', 'Uncovered'):
    pos = run.index('FallbackPath::' + path)
    assert run[pos:].split('interpreter.SingleStepInner();', 1)[0].strip().endswith(
        'ppc.downcount -=')
hook = hooks.split('void StaticRecompCore::HookInstructionFallback(', 1)[1]
assert hook.count('m_fallback_histogram->Record(') == 1
assert hook.index('return;') < hook.index('FallbackPath::InstructionHook')
assert hook.index('ppc.pc = cia;') < hook.index('FallbackPath::InstructionHook')
assert 'std::strcmp(fallback_pcs, "1") == 0' in life
shutdown = life.split('void StaticRecompCore::Shutdown()', 1)[1]
assert 'm_fallback_histogram->dropped' in shutdown
assert 'm_fallback_histogram.reset();' in shutdown
with tempfile.TemporaryDirectory(prefix='galaxypad-fallback-test-') as directory:
    binary = str(Path(directory)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-fsanitize=address,undefined',
                    str(root/'tests/test-fallback-histogram.cpp'), '-o', binary], check=True)
    subprocess.run([binary], check=True)
print('fallback PC source wiring passes; no live attribution or timing proof')
