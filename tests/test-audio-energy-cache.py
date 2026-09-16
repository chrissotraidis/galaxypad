#!/usr/bin/env python3
"""Exact PCM/accounting checks for cached audio-search energies."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon/AudioTempo.h'
OUT = ROOT / 'generated/audio-energy-20260916/maintained-validation'
OUT.mkdir(parents=True, exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument('--benchmark',action='store_true')
args=parser.parse_args()
source = (ROOT/'tests/audio-tempo.cpp').read_text().replace(
    '../experiments/audio-tempo/AudioTempo.h', str(HEADER))
source = source.replace('  const double t = double(index)', """  if (kind == 5) return {0, 0};
  if (kind == 6) {
    unsigned v = unsigned(index) * 747796405u + 2891336453u;
    v = ((v >> ((v >> 28u) + 4u)) ^ v) * 277803737u;
    float n = (int((v >> 22u) ^ v) % 32768) / 32768.f;
    return {n, n * -.75f};
  }
  if (kind == 7) return {index & 1 ? .99f : -.99f, index & 2 ? .99f : -.99f};
  if (kind == 8) return {index & 1 ? 1e-25f : -1e-25f, index & 2 ? 1e-10f : -1e-10f};
  const double t = double(index)""")
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
cases += [(.67,341,997,k,'steady') for k in (5,6,7,8)]
rows=[]
for mode, flags in [('scalar-release',['-O3']),('release',['-O3']),
                    ('scalar-sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer']),
                    ('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    for candidate in (0,1):
        subprocess.run(['clang++','-std=c++20',*flags,
            f'-DGALAXYPAD_AUDIO_BATCHED_SEARCH={0 if mode.startswith("scalar") else 1}',
            f'-DGALAXYPAD_AUDIO_CACHED_ENERGY={candidate}',str(OUT/'bench.cpp'),
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
for repetition in range(9 if args.benchmark else 0):
    for candidate in ((0,1) if repetition%2==0 else (1,0)):
        proc=subprocess.run([str(OUT/f'release-{candidate}'),'.60','341','997','0','steady',str(OUT/'timing.f32'),'12'],check=True,capture_output=True,text=True)
        times[candidate].append(json.loads(proc.stdout)['pull_ns'])
medians={k:statistics.median(v) for k,v in times.items()} if args.benchmark else None
report={'header_sha256':hashlib.sha256(HEADER.read_bytes()).hexdigest(),
        'comparisons':rows,'pull_ns':times,'median_pull_ns':medians,
        'reduction':1-medians[1]/medians[0] if medians else None,
        'scope':'offline Mac elapsed Pull time; not gameplay FPS or physical audio acceptance'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(f"{len(rows)} differential PCM/accounting/provenance cases passed")
if medians: print(f'Median Pull reduction {report["reduction"]:.1%}; host component only')
