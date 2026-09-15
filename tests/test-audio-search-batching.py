#!/usr/bin/env python3
"""Differential PCM/accounting and cost check for opt-in candidate batching."""
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon/AudioTempo.h'
OUT = ROOT / 'generated/audio-search-20260915/validation'
OUT.mkdir(parents=True, exist_ok=True)
source = (ROOT/'tests/audio-tempo.cpp').read_text().replace(
    '../experiments/audio-tempo/AudioTempo.h', str(HEADER))
(OUT/'bench.cpp').write_text(source)
cases = [(r, cb, f, k, scenario) for r, cb, f, k, scenario in [
    (1,128,997,0,'steady'),(.60,341,997,0,'steady'),
    (.67,341,55,0,'steady'),(.74,128,440,1,'bursty'),
    (.85,512,110,2,'steady'),(.67,341,997,3,'steady'),
    (.67,341,997,4,'steady'),(.67,341,997,0,'stall'),
    (.67,341,997,0,'reset'),(.67,341,997,0,'changing'),
    (.67,341,997,0,'recover'),(.67,341,55,0,'gap'),
    (.67,341,55,0,'bursty6'),(.67,341,997,0,'flush'),
    (1,341,997,0,'bursty6'),(.67,683,55,0,'bursty')]]
rows=[]
for mode, flags in [('release',['-O3']),('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    for candidate in (0,1):
        subprocess.run(['clang++','-std=c++20',*flags,
            f'-DGALAXYPAD_AUDIO_BATCHED_SEARCH={candidate}',str(OUT/'bench.cpp'),
            '-o',str(OUT/f'{mode}-{candidate}')],check=True)
    for case in cases:
        results=[]; hashes=[]
        for candidate in (0,1):
            pcm=OUT/f'{mode}-{candidate}.f32'
            proc=subprocess.run([str(OUT/f'{mode}-{candidate}'),*map(str,case),str(pcm),'8'],
                                check=True,capture_output=True,text=True)
            data=json.loads(proc.stdout)
            hashes.append(hashlib.sha256(pcm.read_bytes()).hexdigest())
            results.append({k:v for k,v in data.items() if k not in
                ('push_ns','pull_ns','max_pull_ns','processing_realtime_fraction')})
        assert hashes[0]==hashes[1], (mode,case,'PCM differs')
        assert results[0]==results[1], (mode,case,'accounting/provenance differs')
        rows.append({'mode':mode,'case':case,'pcm_sha256':hashes[0],'identical':True})
times={0:[],1:[]}
for repetition in range(9):
    for candidate in ((0,1) if repetition%2==0 else (1,0)):
        proc=subprocess.run([str(OUT/f'release-{candidate}'),'.60','341','997','0','steady',str(OUT/'timing.f32'),'12'],check=True,capture_output=True,text=True)
        times[candidate].append(json.loads(proc.stdout)['pull_ns'])
medians={k:statistics.median(v) for k,v in times.items()}
report={'header_sha256':hashlib.sha256(HEADER.read_bytes()).hexdigest(),
        'comparisons':rows,'pull_ns':times,'median_pull_ns':medians,
        'reduction':1-medians[1]/medians[0],
        'scope':'offline Mac CPU cost; not gameplay FPS or physical audio acceptance'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'{len(rows)} differential cases passed; median Pull CPU reduction {report["reduction"]:.1%}')
