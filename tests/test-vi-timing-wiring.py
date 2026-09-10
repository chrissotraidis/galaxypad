"""Canonical recorder provenance and shutdown placement; not a runtime smoke."""
from pathlib import Path
import hashlib

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
patch = root/'patches/ModernGekko/0017-vi-timing-recorder.patch'
digest = hashlib.sha256(patch.read_bytes()).hexdigest()
assert digest == 'c5a2da36a4de45e3a6c440ccd03593971649f9109f0cafa64cdae81536a02b6e'
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
assert digest in bootstrap
counter_patch = root/'patches/ModernGekko-dolphin/0015-cpu-throttle-counter.patch'
counter_digest = hashlib.sha256(counter_patch.read_bytes()).hexdigest()
assert counter_digest == '15ae34e6ad58c5d3995aa1b8591b041f5bc405ddc7ab901366bcac3d8a47f68f'
assert counter_digest in bootstrap
metrics = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/PerformanceMetrics.h').read_text()
assert 'DT GetCPUThrottleElapsed() const { return m_time_sleeping; }' in metrics
assert bootstrap.index('apply --reverse "$vi_timing_patch"') < bootstrap.index(
    'apply --reverse "$thp_policy_patch"')
print('VI recorder header parity, opt-in, post-join placement and patch pin pass')
assert (root/'patches/experiments/rolling/idle-wait-timing.h').read_bytes() == (
    root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common/GalaxyPadIdleWaitTiming.h').read_bytes()
assert 'GetCPUIdleWaitTiming().Configure(\n      m_impl->vi_timing.Enabled() || galaxypad::completion_recorder.Enabled());' in source
assert 'GetCPUIdleWaitTiming().ElapsedNs()' in source
timing = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/CoreTiming.cpp').read_text()
assert 'GetCPUIdleWaitTiming().Measure(\n        [this] {' in timing
assert 'm_system.GetFifo().FlushGpu();' in timing
for name, expected in (
    ('ModernGekko/0018-idle-wait-recorder.patch', 'fd268ed85ae8ad14624ac402cc399b9a38f440b116a2bfa44322e30490c75967'),
    ('ModernGekko-dolphin/0016-idle-wait-timing.patch', '63970dcc657af8239d2ccf64da74cf88395721e5aaec945fedf88f9388e776c1')):
    assert hashlib.sha256((root/'patches'/name).read_bytes()).hexdigest() == expected
    assert expected in bootstrap
assert bootstrap.index('apply --reverse "$idle_recorder_patch"') < bootstrap.index(
    'apply --reverse "$vi_timing_patch"')
print('Idle wait header parity, opt-in configuration, CPU idle boundary and patch pins pass')
