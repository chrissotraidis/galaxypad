"""Verify the installed CPU gather wait patch in the pinned fork."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
core = root / 'ref/ModernGekko/vendor/dolphin/Source/Core'
source = (core / 'VideoCommon/CommandProcessor.cpp').read_text()
assert source.count('GetCPUGatherWaitTiming().Measure(') == 1
assert ('GetCPUGatherWaitTiming().Measure(\n'
        '            [this] { m_system.GetFifo().FlushGpu(); });') in source
metrics = (core / 'VideoCommon/PerformanceMetrics.h').read_text()
assert 'galaxypad::IdleWaitTiming m_gather_wait_timing;' in metrics
print('Gather wait installed scope, member isolation, fork source check and fork integration pass')
runtime = (root / 'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'GetCPUGatherWaitTiming().Configure(\n      m_impl->vi_timing.Enabled());' in runtime
assert 'GetCPUGatherWaitTiming().ElapsedNs()' in runtime
for name in ('vi-timing-buffer.h', 'vi-timing-recorder.h'):
    assert (root / 'patches/experiments' / name).read_bytes() == (root / 'ref/ModernGekko/src/runtime' / name).read_bytes()
print('Gather VI opt-in, runtime fork source check and recorder header parity pass')
