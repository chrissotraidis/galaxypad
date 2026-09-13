"""Source/provenance guards; runtime scheduling attribution needs a fresh capture."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
common = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common'
for name in ('completion-events.h', 'completion-recorder.h', 'completion-session.h',
             'recent-completion-events.h', 'completion-trigger.h',
             'completion-flight-recorder.h', 'completion-flight-options.h'):
    assert (root/'patches/experiments'/name).read_bytes() == (common/name).read_bytes()
runtime = (root/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
assert 'completion_recorder.Configure(completion_path, completion_deadline,' in runtime
assert 'std::getenv("GALAXYPAD_COMPLETION_ARM_DELAY_MS")' in runtime
assert 'completion_config_valid ? completion_threshold : 0' in runtime
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
print('Completion header parity, fork source checks, opt-in, endpoints and post-Shutdown export pass')
