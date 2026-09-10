"""Exercise the real macOS counter API and fail-closed CLI parsing."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='galaxypad-work-counter-') as temporary:
    executable = str(Path(temporary)/'snapshot')
    subprocess.run(['clang', '-O2', '-Wall', '-Wextra', '-Werror',
                    str(root/'scripts/process-work-snapshot.c'), '-o', executable], check=True)
    subprocess.run([executable, '--self-test'], check=True)
    for invalid in ('', '0', '-1', '12junk', '999999999999999999999999'):
        assert subprocess.run([executable, invalid], capture_output=True).returncode == 2
    samples = [json.loads(subprocess.check_output([executable, str(os.getpid())])) for _ in range(2)]
    first, last = samples
    assert first['pid'] == last['pid'] == os.getpid()
    assert first['start_abstime'] == last['start_abstime'] > 0
    assert first['before_ns'] <= first['after_ns'] <= last['before_ns'] <= last['after_ns']
    assert 0 < first['instructions'] <= last['instructions']
    assert 0 < first['cycles'] <= last['cycles']
    clock_source = Path(temporary)/'clock.cpp'
    clock_source.write_text('#define main snapshot_main\n#include "' + str(root/'scripts/process-work-snapshot.c') + '"\n#undef main\n' + r'''
#include <chrono>
#include <cassert>
int main() {
  const auto steady = [] { return std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count(); };
  for (int i = 0; i < 1000; ++i) {
    auto a = steady(); auto snapshot_clock = now_ns(); auto b = steady();
    assert(static_cast<uint64_t>(a) <= snapshot_clock && snapshot_clock <= static_cast<uint64_t>(b));
  }
}
''')
    subprocess.run(['clang++', '-std=c++17', str(clock_source), '-o', executable], check=True)
    subprocess.run([executable], check=True)
print('Process counter identity, monotonic snapshots, invalid PID parsing and actual API checks pass')
