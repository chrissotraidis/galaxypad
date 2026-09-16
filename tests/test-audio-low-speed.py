#!/usr/bin/env python3
"""Reproduce sub-60% starvation and exercise the opt-in lower tempo floor."""
import array
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon/AudioTempo.h'
# Preserve allocation, capacity, input accounting, pause and unity assertions.
# Inspect unavailableWindows below: the control must reproduce the actual fault.
source = (ROOT / 'tests/audio-tempo.cpp').read_text().replace(
    '../experiments/audio-tempo/AudioTempo.h', str(HEADER)).replace(
    '  if (scenario != "stall") assert(stats.unavailableWindows == 0);\n'
    '  else assert(stats.unavailableWindows > 0);', '')
cases = [(r, cb, f, scenario) for r in (.55, .57, .60, .67)
         for cb, f, scenario in ((683, 997, 'steady'), (341, 55, 'bursty6'),
                                (341, 997, 'changing'), (341, 997, 'recover'))]
cases += [(.57,341,997,s) for s in ('stall','reset','flush')]
cases += [(1,341,997,s) for s in ('steady','bursty6')]
with tempfile.TemporaryDirectory(prefix='galaxypad-audio-low-speed-') as tmp:
    out = Path(tmp)
    (out/'probe.cpp').write_text(source)
    def run(exe, ratio, callback, frequency, scenario):
        result = subprocess.run([str(exe),str(ratio),str(callback),str(frequency),
            '0',scenario,str(out/'pcm.f32'),'12'],check=True,capture_output=True,text=True)
        return json.loads(result.stdout), (out/'pcm.f32').read_bytes()
    def compile_probe(name, flags, enabled):
        exe = out/name
        subprocess.run(['clang++','-std=c++20',*flags,
            '-DGALAXYPAD_AUDIO_BATCHED_SEARCH=1','-DGALAXYPAD_AUDIO_CACHED_ENERGY=1',
            f'-DGALAXYPAD_AUDIO_LOW_SPEED={enabled}',str(out/'probe.cpp'),'-o',str(exe)],check=True)
        return exe
    control = compile_probe('control',['-O3'],0)
    old, _ = run(control,.57,683,997,'steady')
    assert old['unavailable_windows'] > 100, old
    normal, normal_pcm = run(control,1,341,997,'steady')
    for name, flags in [('release',['-O3']), ('sanitized',[
            '-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
        exe = compile_probe(name,flags,1)
        for ratio, callback, frequency, scenario in cases:
            stats, raw = run(exe,ratio,callback,frequency,scenario)
            # New 55%-speed coverage has a separate 160 ms wall-age budget;
            # the historical default-path 120 ms gates remain unchanged.
            assert stats['max_wall_age_ms'] + 4 <= 160, stats
            assert stats['unavailable_windows'] == 0 if scenario != 'stall' else stats['unavailable_windows'] > 0, stats
            pcm = array.array('f'); pcm.frombytes(raw)
            if scenario not in ('stall','reset','flush'):
                longest = current = 0
                for v in pcm[64000::2]:
                    current = current+1 if abs(v)<1e-7 else 0
                    longest = max(longest,current)
                assert longest < 32, (ratio,scenario,longest)
            else:
                assert max(abs(v) for v in pcm[320000:326400:2]) > .5, stats
            if ratio == 1 and scenario == 'steady':
                assert hashlib.sha256(raw).digest() == hashlib.sha256(normal_pcm).digest()
print(f'Control starvation reproduced; {len(cases)*2} low-speed, recovery and unity checks passed')
