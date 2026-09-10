"""Check CPU-only notification timing and pinned bootstrap ordering."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
core = root / 'ref/ModernGekko/vendor/dolphin/Source/Core'
fifo = (core / 'VideoCommon/Fifo.cpp').read_text()
body = fifo.split('void FifoManager::RunGpu()\n{', 1)[1].split('\nint FifoManager::RunGpuOnCpu', 1)[0]
assert body.count('WakeupWithNotification(') == 1
assert ('if (Core::IsCPUThread())\n'
        '        m_system.GetPerfMetrics().GetCPUWakeupTiming().Measure([&event] { event.Set(); });\n'
        '      else\n        event.Set();') in body
loop = (core / 'Common/BlockingLoop.h').read_text()
assert 'WakeupWithNotification([](Event& event) { event.Set(); });' in loop
assert loop.count('notify(m_new_work_event);') == 1
patch = root / 'patches/ModernGekko-dolphin/0021-wakeup-notification-timing.patch'
bootstrap = (root / 'scripts/bootstrap-dependencies.sh').read_text()
assert hashlib.sha256(patch.read_bytes()).hexdigest() in bootstrap
assert bootstrap.index('apply --reverse "$wakeup_core_patch"') < bootstrap.index('apply --reverse "$gather_core_patch"')
assert 'a/Source/Core/Common/Event.h' not in patch.read_text()
print('Wakeup CPU ownership, default notification, unchanged Event and patch ordering pass')
runtime = (root / 'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'GetCPUWakeupTiming().Configure(\n      m_impl->vi_timing.Enabled());' in runtime
assert 'GetCPUWakeupTiming().ElapsedNs()' in runtime
patch = root / 'patches/ModernGekko/0024-wakeup-recorder.patch'
assert hashlib.sha256(patch.read_bytes()).hexdigest() in bootstrap
assert bootstrap.index('apply --reverse "$wakeup_runtime_patch"') < bootstrap.index('apply --reverse "$gather_runtime_patch"')
print('Wakeup runtime VI opt-in, export and pinned ordering pass')
