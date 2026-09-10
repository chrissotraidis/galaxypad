#!/usr/bin/env python3
"""Stage opt-in Metal timing source without modifying the pinned checkout."""
from pathlib import Path
import hashlib
import argparse
import json
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 'fcca51b4c765721fd242cb2f25620418bd3d98be69cbd82df1814985c7fb4ace'
EXPECTED_TRACKER = '79f8f187dd10b4776090b0b7bf9c1d727f0a9657bcd46c126c93aaeb87d44040'

def instrument_tracker(source):
    if hashlib.sha256(source).hexdigest() != EXPECTED_TRACKER:
        raise ValueError('Unreviewed MTLStateTracker source identity')
    text = source.decode()
    start_marker = 'q = std::move(m_current_perf_query)](id<MTLCommandBuffer> buf) {'
    end_marker = '\n      }];\n  m_current_perf_query = nullptr;'
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError('Ambiguous render completion handler')
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker, start)
    # The original lock_guard dies before the wrapper records/logs its interval.
    return ('#include "metal-staging-timing.h"\n' + text[:start] +
            '\n        GalaxyPadDiagnostics::TraceStaging("completion_handler", [&] {' +
            text[start:end] + '\n        }, reinterpret_cast<std::uintptr_t>((__bridge void*)buf));' + text[end:])

def instrument(source):
    if hashlib.sha256(source).hexdigest() != EXPECTED:
        raise ValueError('Unreviewed MTLTexture source identity')
    text = source.decode()
    text = '#include "metal-staging-timing.h"\n' + text
    start = text.index('void Metal::StagingTexture::CopyFromTexture(')
    body = text.index('\n{\n', start) + 2
    end = text.index('\n}\n\nvoid Metal::StagingTexture::CopyToTexture', body)
    text = text[:body] + '\n  GalaxyPadDiagnostics::TraceStaging("copy_setup", [&] {' + text[body:end] + '\n  });' + text[end:]
    for old, stage in [
        ('    g_state_tracker->FlushEncoders();\n    g_state_tracker->NotifyOfCPUGPUSync();', 'submit')]:
        if text.count(old) != 1:
            raise ValueError('Ambiguous staging operation')
        text = text.replace(old, '    GalaxyPadDiagnostics::TraceStaging("' + stage + '", [&] {\n' + old + '\n    });')
    old = '    [m_wait_buffer waitUntilCompleted];'
    if text.count(old) != 1:
        raise ValueError('Ambiguous completion wait')
    text = text.replace(old, '''    GalaxyPadDiagnostics::TraceStagingGPU("wait", [&] {
    [m_wait_buffer waitUntilCompleted];
    }, [&] {
      return GalaxyPadDiagnostics::ValidateStagingGPUInterval(
          [m_wait_buffer status] == MTLCommandBufferStatusCompleted,
          [m_wait_buffer GPUStartTime], [m_wait_buffer GPUEndTime]);
    }, reinterpret_cast<std::uintptr_t>((__bridge void*)(id<MTLCommandBuffer>)m_wait_buffer));''')
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compile', action='store_true', help='Compile a separate diagnostic object; do not relink app')
    parser.add_argument('--completion-handler', action='store_true', help='Also stage the render completion handler probe')
    args = parser.parse_args()
    source = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core/VideoBackends/Metal/MTLTexture.mm'
    staged = instrument(source.read_bytes())
    output = ROOT / 'generated/metal-staging-probe'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'MTLTexture.mm').write_text(staged)
    (output / 'metal-staging-timing.h').write_bytes((ROOT / 'patches/experiments/metal-staging-timing.h').read_bytes())
    sources = [source]
    if args.completion_handler:
        tracker = source.with_name('MTLStateTracker.mm')
        (output / tracker.name).write_text(instrument_tracker(tracker.read_bytes()))
        sources.append(tracker)
    print(output / 'MTLTexture.mm')
    if args.compile:
        commands = json.loads((ROOT / 'generated/build/ios-simulator-core/compile_commands.json').read_text())
        for item in sources:
            matches = [entry for entry in commands if Path(entry['file']) == item]
            if len(matches) != 1:
                raise ValueError('Expected one exact Simulator Metal compilation command')
            entry = matches[0]
            command = shlex.split(entry['command'])
            if command.count(str(item)) != 1 or command.count('-o') != 1:
                raise ValueError('Unrecognized compiler command')
            command[command.index(str(item))] = str(output / item.name)
            command[command.index('-o') + 1] = str(output / (item.name + '.o'))
            subprocess.run(command, cwd=entry['directory'], check=True)

if __name__ == '__main__':
    main()
