from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
sync = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Sync.cpp').read_text()
body = sync.split('void StaticRecompCore::AdvanceGuestTimebase(u64 cpu_cycles)', 1)[1].split('}', 1)[0]
assert 'm_timebase_cycle_remainder + cpu_cycles' in body
assert 'm_guest.timebase += total_cycles / SystemTimers::TIMER_RATIO;' in body
assert 'm_timebase_cycle_remainder = total_cycles % SystemTimers::TIMER_RATIO;' in body
timers = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/HW/SystemTimers.h').read_text()
assert 'TIMER_RATIO = 12' in timers
with tempfile.TemporaryDirectory(prefix='galaxypad-deferred-tb-') as directory:
    binary = str(Path(directory)/'test')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(root/'tests/test-deferred-timebase.cpp'),
                    '-o', binary], check=True)
    subprocess.run([binary], check=True)
print('Deferred TB arithmetic: 62208 boundary triples and one million mixed events pass; runtime observers unproven')
