"""Source/provenance guards; runtime scheduling attribution needs a fresh capture."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
common = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common'
for name in ('completion-events.h', 'completion-recorder.h', 'completion-session.h',
             'recent-completion-events.h', 'completion-trigger.h',
             'completion-flight-recorder.h', 'completion-flight-options.h'):
    assert (root/'patches/experiments'/name).read_bytes() == (common/name).read_bytes()
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
for name, digest in (
    ('ModernGekko/0019-completion-recorder.patch', '01c931eb6103d5e0c0437231ee386a6ed5802dfca5c5c574dcd5006178e71186'),
    ('ModernGekko-dolphin/0017-completion-timing.patch', 'cba14f51f95284ab097a1b0d5aef6f99bb8dd6571bd7b7e8b39efd56bc5933c4'),
    ('ModernGekko/0020-completion-flight.patch', 'c72c94b29bb419f423218deb4a8d3fcb2762b911273dc0d64df20c187d6d3172'),
    ('ModernGekko-dolphin/0018-completion-flight.patch', 'c40a8223d07fa85f0dccb33f13ed886f9c53b15ca60af5f1813598b31968466b')):
    assert hashlib.sha256((root/'patches'/name).read_bytes()).hexdigest() == digest
    assert digest in bootstrap
assert bootstrap.index('apply --reverse "$completion_recorder_patch"') < bootstrap.index(
    'apply --reverse "$idle_recorder_patch"')
assert bootstrap.index('apply --reverse "$completion_timing_patch"') < bootstrap.index(
    'apply --reverse "$idle_wait_patch"')
runtime = (root/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'completion_recorder.Configure(completion_path, completion_deadline,' in runtime
assert 'std::getenv("GALAXYPAD_COMPLETION_ARM_DELAY_MS")' in runtime
assert 'completion_config_valid ? completion_threshold : 0' in runtime
assert bootstrap.index('apply --reverse "$flight_core_patch"') < bootstrap.index('apply --reverse "$completion_timing_patch"')
assert bootstrap.index('apply --reverse "$flight_runtime_patch"') < bootstrap.index('apply --reverse "$completion_recorder_patch"')
assert 'completion_recorder.FlushAfterJoin();' in runtime
assert runtime.count('m_impl->FlushViTiming();') == 2
for indent in ('  ', '    '):
    assert (indent+'Core::Shutdown(Core::System::GetInstance());\n'+
            indent+'m_impl->FlushViTiming();') in runtime
base = root/'ref/ModernGekko/vendor/dolphin/Source/Core'
fifo = (base/'VideoCommon/Fifo.cpp').read_text()
assert 'completion_recorder.Enabled() ? &galaxypad::ObserveCompletion : nullptr' in fifo
timing = (base/'Core/CoreTiming.cpp').read_text()
assert '[this] { m_system.GetFifo().FlushGpu(); },\n        [](std::uint64_t start, std::uint64_t end)' in timing
assert 'galaxypad::completion_recorder.CPUWait(start, end);' in timing
assert 'completion_recorder.RecordCPU' not in timing
loop = (common/'BlockingLoop.h').read_text()
assert 'notification_observer(observer_context, true);\n        m_done_event.Set();\n        if (notification_observer)\n          notification_observer(observer_context, false);' in loop
print('Completion header parity, patch pins, opt-in, endpoints and post-Shutdown export pass')
