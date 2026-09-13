"""Canonical recorder provenance and shutdown placement; not a runtime smoke."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for name in ('vi-timing-buffer.h', 'vi-timing-recorder.h'):
    assert (root/'patches/experiments'/name).read_bytes() == (
        root/'ref/ModernGekko/src/runtime'/name).read_bytes()
source = (root/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'm_impl->vi_timing.Configure(std::getenv("GALAXYPAD_VI_TIMING"));' in source
assert 'if (m_impl->vi_timing.Enabled())\n          m_impl->vi_timing.Record(' in source
assert 'GalaxyPadDiagnostics::s_efb_peek_ns.load(std::memory_order_relaxed)' in source
assert 'GetPerfMetrics().GetCPUThrottleElapsed()).count()' in source
assert source.count('m_impl->FlushViTiming();') == 2
for indent in ('  ', '    '):
    assert (indent+'Core::Shutdown(Core::System::GetInstance());\n'+
            indent+'m_impl->FlushViTiming();') in source
metrics = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/PerformanceMetrics.h').read_text()
assert 'DT GetCPUThrottleElapsed() const { return m_time_sleeping; }' in metrics
print('VI recorder header parity, opt-in, post-join placement and fork source check pass')
assert (root/'patches/experiments/rolling/idle-wait-timing.h').read_bytes() == (
    root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common/GalaxyPadIdleWaitTiming.h').read_bytes()
assert 'GetCPUIdleWaitTiming().Configure(\n      m_impl->vi_timing.Enabled() || galaxypad::completion_recorder.Enabled());' in source
assert 'GetCPUIdleWaitTiming().ElapsedNs()' in source
timing = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/CoreTiming.cpp').read_text()
assert 'GetCPUIdleWaitTiming().Measure(\n        [this] {' in timing
assert 'm_system.GetFifo().FlushGpu();' in timing
print('Idle wait header parity, opt-in configuration, CPU idle boundary and fork source checks pass')
