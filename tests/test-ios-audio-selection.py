#!/usr/bin/env python3
"""Verify SDK header layout agrees with CMake's maintained audio source choice."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core'
AUDIO = CORE / 'AudioCommon'
EXPECTED = {
    'IOS/Mixer.cpp': '102a876d8efe784e2c37c4cadae46eadc4479f0776797a8388d16d31215565e1',
    'IOS/Mixer.h': '4e14a7db9b84f372b65ac660c8653c1f7207f243d36e2bfe9b84b5ed81ee0c27',
    'AudioTempo.h': '4830d3f0568cb8faf50c7c2fb7720f50b9958bbed37dc310fddbbd4898035871',
}
for relative, digest in EXPECTED.items():
    assert hashlib.sha256((AUDIO / relative).read_bytes()).hexdigest() == digest, relative

with tempfile.TemporaryDirectory(prefix='galaxypad-audio-selection-') as tmp:
    fixture = Path(tmp)
    prefix = (AUDIO / 'CMakeLists.txt').read_text().split('add_library(audiocommon', 1)[0]
    for system, expected in [('iOS', 'IOS/Mixer.cpp'), ('Darwin', 'Mixer.cpp'), ('Linux', 'Mixer.cpp')]:
        script = fixture / 'selection.cmake'
        script.write_text(f'set(CMAKE_SYSTEM_NAME {system})\n' + prefix +
                          f'if(NOT MIXER_SOURCE STREQUAL "{expected}")\n'
                          'message(FATAL_ERROR "Wrong mixer source")\nendif()\n')
        subprocess.run(['cmake', '-P', str(script)], check=True)
    # This checks preprocessing selection, not semantic compilation. Strip only
    # unrelated includes so --sources-only CI needs no external fmt checkout.
    # Keep actual selector directives and both actual class bodies unchanged.
    headers = fixture / 'headers'
    for relative in ['Mixer.h', 'IOS/Mixer.h']:
        original = (AUDIO / relative).read_text()
        selected = ''.join(line for line in original.splitlines(keepends=True)
            if not line.lstrip().startswith('#include') or
            line.strip() in ('#include <TargetConditionals.h>',
                             '#include "AudioCommon/IOS/Mixer.h"'))
        copied = headers / 'AudioCommon' / relative
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_text(selected)
    for sdk, target, tempo in [('iphoneos', 'arm64-apple-ios16.0', True),
                               ('iphonesimulator', 'arm64-apple-ios16.0-simulator', True),
                               ('macosx', 'arm64-apple-macos13.0', False)]:
        sdk_path = subprocess.check_output(['xcrun', '--sdk', sdk, '--show-sdk-path'], text=True).strip()
        source = fixture / 'layout.cpp'
        source.write_text('#include "AudioCommon/Mixer.h"\n')
        result = subprocess.check_output(['xcrun', '--sdk', sdk, 'clang++', '-E', '-x', 'c++',
            '-std=c++20', '-isysroot', sdk_path, '-target', target, '-I', str(headers), str(source)], text=True)
        assert ('m_dma_tempo_callback_index' in result) == tempo, sdk
        assert 'class Mixer' in result, sdk
    # Exercise accepted code directly, including accounting, stalls and state flush.
    source = fixture / 'tempo.cpp'
    source.write_text((ROOT / 'tests/audio-tempo.cpp').read_text().replace(
        '../experiments/audio-tempo/AudioTempo.h', str(AUDIO / 'AudioTempo.h')))
    executable = fixture / 'tempo'
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-O1',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(source), '-o', str(executable)], check=True)
    for ratio, scenario in [(1, 'steady'), (.67, 'stall'), (.67, 'reset'), (.67, 'flush')]:
        result = subprocess.run([str(executable), str(ratio), '341', '997', '0', scenario,
                                 str(fixture / 'pcm.bin'), '8'], text=True, capture_output=True)
        assert result.returncode == 0, (scenario, result.stdout, result.stderr)
        stats = json.loads(result.stdout)
        assert stats['input_accepted'] > 0
        assert stats['input_retired'] <= stats['input_accepted']
print('iOS audio source identities and iPhoneOS/Simulator/macOS header selection passed.')
