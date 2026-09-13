"""Check CPU-only notification timing and pinned fork integration."""
from pathlib import Path

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
event = (core / 'Common/Event.h').read_text()
assert 'GetCPUWakeupTiming' not in event  # Timing remains CPU-side, not in every Event.
print('Wakeup CPU ownership, default notification, unchanged Event and fork source wiring pass')
runtime = (root / 'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'GetCPUWakeupTiming().Configure(\n      m_impl->vi_timing.Enabled());' in runtime
assert 'GetCPUWakeupTiming().ElapsedNs()' in runtime
print('Wakeup runtime VI opt-in, export and fork source wiring pass')
