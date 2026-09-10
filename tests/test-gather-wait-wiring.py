"""Verify the installed CPU gather wait patch and bootstrap recovery order."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
core = root / 'ref/ModernGekko/vendor/dolphin/Source/Core'
source = (core / 'VideoCommon/CommandProcessor.cpp').read_text()
assert source.count('GetCPUGatherWaitTiming().Measure(') == 1
assert ('GetCPUGatherWaitTiming().Measure(\n'
        '            [this] { m_system.GetFifo().FlushGpu(); });') in source
metrics = (core / 'VideoCommon/PerformanceMetrics.h').read_text()
assert 'galaxypad::IdleWaitTiming m_gather_wait_timing;' in metrics
bootstrap = (root / 'scripts/bootstrap-dependencies.sh').read_text()
patch = root / 'patches/ModernGekko-dolphin/0020-gather-wait-timing.patch'
assert hashlib.sha256(patch.read_bytes()).hexdigest() in bootstrap
assert bootstrap.index('apply --reverse "$gather_core_patch"') < bootstrap.index('apply --reverse "$dvd_core_patch"')
restore = bootstrap.split('trap restore_overlay_patches EXIT')[0]
assert restore.index('apply "$gather_core_patch"') > restore.index('apply "$dvd_core_patch"')
print('Gather wait installed scope, member isolation, patch pin and peel order pass')
runtime = (root / 'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'GetCPUGatherWaitTiming().Configure(\n      m_impl->vi_timing.Enabled());' in runtime
assert 'GetCPUGatherWaitTiming().ElapsedNs()' in runtime
patch = root / 'patches/ModernGekko/0023-gather-wait-recorder.patch'
assert hashlib.sha256(patch.read_bytes()).hexdigest() in bootstrap
assert bootstrap.index('apply --reverse "$gather_runtime_patch"') < bootstrap.index('apply --reverse "$dvd_runtime_patch"')
for name in ('vi-timing-buffer.h', 'vi-timing-recorder.h'):
    assert (root / 'patches/experiments' / name).read_bytes() == (root / 'ref/ModernGekko/src/runtime' / name).read_bytes()
print('Gather VI opt-in, runtime patch pin and recorder header parity pass')
