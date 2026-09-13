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
    capability = subprocess.run([executable, '--self-test'], capture_output=True, text=True)
    if capability.returncode == 77:
        assert 'unavailable on this host' in capability.stderr
        print(capability.stderr.strip())
        print('Live PMU progress unavailable; identity, clock, API failure and simulated counter cases still run.')
    else:
        capability.check_returncode()
        print(capability.stdout.strip())
    for invalid in ('', '0', '-1', '12junk', '999999999999999999999999'):
        assert subprocess.run([executable, invalid], capture_output=True).returncode == 2
    missing = subprocess.run([executable, '2147483647'], capture_output=True, text=True)
    assert missing.returncode == 1 and 'proc_pid_rusage' in missing.stderr
    samples = [json.loads(subprocess.check_output([executable, str(os.getpid())])) for _ in range(2)]
    first, last = samples
    assert first['pid'] == last['pid'] == os.getpid()
    assert first['start_abstime'] == last['start_abstime'] > 0
    assert first['before_ns'] <= first['after_ns'] <= last['before_ns'] <= last['after_ns']
    assert first['instructions'] <= last['instructions'] and first['cycles'] <= last['cycles']
    for sample in samples:
        assert sample['work_counters_available'] == bool(sample['instructions'] and sample['cycles'])
    if capability.returncode == 0:
        assert first['work_counters_available'] and last['work_counters_available']
    else:
        assert not first['work_counters_available'] and not last['work_counters_available']
    # Exercise the complete CLI with a successful API that exposes no PMU,
    # and with an API error, regardless of the current machine's capabilities.
    fake_source = Path(temporary)/'fake.c'
    fake_source.write_text('#define proc_pid_rusage fake_rusage\n#define main snapshot_main\n#include "' + str(root/'scripts/process-work-snapshot.c') + '"\n#undef main\n' + r'''
int fake_rusage(int pid, int flavor, rusage_info_t *buffer) {
  (void)pid;(void)flavor;
  if (getenv("SNAPSHOT_TEST_API_ERROR")) { errno=EACCES; return -1; }
  struct rusage_info_v4 *value=(struct rusage_info_v4 *)buffer;
  value->ri_proc_start_abstime=10;
  value->ri_user_time=100;
  return 0;
}
int main(int argc,char **argv) { return snapshot_main(argc,argv); }
''')
    fake = str(Path(temporary)/'fake')
    subprocess.run(['clang', '-O1', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                    str(fake_source), '-o', fake], check=True)
    unavailable = subprocess.run([fake, '--self-test'], capture_output=True, text=True)
    assert unavailable.returncode == 77 and not unavailable.stdout
    assert 'instructions=0->0 cycles=0->0' in unavailable.stderr
    zero_sample = json.loads(subprocess.check_output([fake, str(os.getpid())]))
    assert zero_sample['work_counters_available'] is False and zero_sample['instructions'] == zero_sample['cycles'] == 0
    api_error = subprocess.run([fake, '--self-test'], capture_output=True, text=True,
                               env=dict(os.environ, SNAPSHOT_TEST_API_ERROR='1'))
    assert api_error.returncode == 1 and 'proc_pid_rusage' in api_error.stderr
    clock_source = Path(temporary)/'clock.cpp'
    clock_source.write_text('#define main snapshot_main\n#include "' + str(root/'scripts/process-work-snapshot.c') + '"\n#undef main\n' + r'''
#include <chrono>
#include <cassert>
int main() {
  rusage_info_v4 first{}, last{};
  first.ri_proc_start_abstime=last.ri_proc_start_abstime=10;
  assert(counter_progress(&first,&last)==77); // API success, no PMU counters.
  first.ri_instructions=100;first.ri_cycles=200;
  last=first;assert(counter_progress(&first,&last)==1); // Nonzero but stalled.
  last.ri_instructions++;last.ri_cycles++;
  assert(counter_progress(&first,&last)==0);
  last.ri_instructions=99;assert(counter_progress(&first,&last)==1);
  last=first;last.ri_proc_start_abstime++;assert(counter_progress(&first,&last)==1);
  first={};last={};assert(counter_progress(&first,&last)==1); // Missing identity.
  first.ri_proc_start_abstime=last.ri_proc_start_abstime=10;
  last.ri_instructions=100;assert(counter_progress(&first,&last)==77); // Partial support.
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
