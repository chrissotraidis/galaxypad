"""Canonical DVD wait instrumentation scope, opt-in and provenance."""
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
runtime=(root/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'GetCPUDVDWaitTiming().Configure(\n      m_impl->vi_timing.Enabled());' in runtime
assert 'GetCPUDVDWaitTiming().ElapsedNs()' in runtime
core=root/'ref/ModernGekko/vendor/dolphin/Source/Core'
dvd=(core/'Core/HW/DVD/DVDThread.cpp').read_text()
assert dvd.count('GetCPUDVDWaitTiming().Measure(')==1
assert 'GetCPUDVDWaitTiming().Measure(\n          [this] { m_result_queue.WaitForData(); });' in dvd
metrics=(core/'VideoCommon/PerformanceMetrics.h').read_text()
assert 'galaxypad::IdleWaitTiming m_dvd_wait_timing;' in metrics
bootstrap=(root/'scripts/bootstrap-dependencies.sh').read_text()
for path in ('ModernGekko/0022-dvd-wait-recorder.patch', 'ModernGekko-dolphin/0019-dvd-wait-timing.patch'):
    assert hashlib.sha256((root/'patches'/path).read_bytes()).hexdigest() in bootstrap
assert bootstrap.index('apply --reverse "$dvd_runtime_patch"') < bootstrap.index('apply --reverse "$flight_runtime_patch"')
assert bootstrap.index('apply --reverse "$dvd_core_patch"') < bootstrap.index('apply --reverse "$flight_core_patch"')
print('DVD wait exact boundary, VI opt-in, member isolation and pinned peel order pass')
