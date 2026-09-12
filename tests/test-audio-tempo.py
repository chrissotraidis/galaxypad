#!/usr/bin/env python3
"""Offline quality/accounting/cost screen of an unintegrated audio tempo prototype."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RATE = 32000


def tone_quality(pcm, frequency):
    samples = pcm[RATE * 2:RATE * 7, 0].astype(np.float64)
    fft = np.fft.rfft(samples * np.hanning(len(samples)))
    power = np.abs(fft) ** 2
    frequencies = np.fft.rfftfreq(len(samples), 1 / RATE)
    peak = frequencies[np.argmax(power)]
    near = np.abs(frequencies-frequency) <= 5
    return {'peak_hz': float(peak), 'pitch_error_hz': float(abs(peak-frequency)),
            'target_band_power_fraction': float(power[near].sum()/power.sum()),
            'rms': float(np.sqrt(np.mean(samples**2)))}


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which('clang++')
    commands = []
    results = []
    # Actual compiler builds, without app/core/module builds or Simulator use.
    for name, flags in [('release', ['-O3','-DNDEBUG']),
                        ('sanitized', ['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
        # Keep assertions even in optimized gate: runtime accounting is part of it.
        flags = [flag for flag in flags if flag != '-DNDEBUG']
        command = [compiler,'-std=c++20',*flags,str(ROOT/'tests/audio-tempo.cpp'),'-o',str(output/name)]
        subprocess.run(command,check=True); commands.append(command)
        cases = [(1,128,997,0,'steady'),(.67,341,997,0,'steady'),
                 (.74,128,440,1,'bursty'),(.85,512,110,2,'steady'),
                 (.67,341,997,0,'stall'),(.67,341,997,0,'reset'),
                 (.67,341,997,0,'changing'),(1,128,997,0,'bursty'),
                 (.67,341,997,0,'recover'),(.67,512,997,0,'bursty')]
        cases += [(.67,341,55,0,'gap')]
        cases += [(.67,341,55,0,'bursty6'),(.67,341,997,0,'flush')]
        cases += [(1,341,997,0,'bursty6'),(1,341,997,0,'bursty')]
        if name == 'release':
            cases += [(r,341,f,0,'steady') for r in (.67,.74,.85,.98) for f in (55,110,440,997)]
            cases += [(.67,341,997,3,'steady')]
            cases += [(.67,341,997,4,'steady')]
            cases += [(.67,512,55,0,'bursty'),(.67,512,431,2,'bursty')]
            cases += [(.67,683,55,0,'bursty'),(.67,683,997,0,'bursty')]
        for index, (ratio, callback, freq, kind, scenario) in enumerate(cases):
            stem = f'{name}-{index}-{ratio}-{freq}-{scenario}'
            path = output/(stem+'.f32')
            argv = [str(output/name),str(ratio),str(callback),str(freq),str(kind),scenario,str(path),'8']
            result = subprocess.run(argv,text=True,capture_output=True)
            assert result.returncode == 0, (argv,result.stdout,result.stderr)
            stats = json.loads(result.stdout); stats.update(name=stem, scenario=scenario,kind=kind)
            assert stats['max_wall_age_ms'] + 4 <= 120, stats
            if scenario == 'bursty6': assert stats['unity_entries'] == 0, stats
            pcm = np.fromfile(path,np.float32).reshape(-1,2)
            assert np.isfinite(pcm).all()
            assert np.max(np.abs(pcm)) <= .9
            settled = pcm[RATE:]
            if scenario not in ('stall','reset','flush'):
                quiet = np.max(np.abs(settled),axis=1) < 1.e-7
                edges = np.flatnonzero(np.diff(np.r_[False,quiet,False]))
                longest = max(edges[1::2]-edges[::2],default=0)
                stats['longest_silent_frames'] = int(longest)
                assert longest < RATE*.001
            if kind in (0,1,2,4) and scenario in ('steady','bursty','bursty6'):
                stats['quality'] = tone_quality(pcm,freq)
                assert stats['quality']['pitch_error_hz'] <= 2.0, stats
                assert stats['quality']['target_band_power_fraction'] >= .85, stats
                if kind == 4:
                    stats['right_quality'] = tone_quality(pcm[:,::-1],431)
                    assert stats['right_quality']['pitch_error_hz'] <= 2.0, stats
                    assert stats['right_quality']['target_band_power_fraction'] >= .85, stats
            if kind == 0: assert np.array_equal(pcm[:,0]*.5,pcm[:,1])
            if kind == 1: assert np.array_equal(-pcm[:,0],pcm[:,1])
            if kind == 2:
                # Cross-spectrum phase checks a stereo relationship that must not
                # be independently time shifted by channel-local grain searches.
                x = pcm[RATE*2:RATE*7].astype(np.float64)
                phase = np.exp(-2j*np.pi*freq*np.arange(len(x))/RATE)
                channel = (x*phase[:,None]).sum(axis=0)
                relative = np.angle(channel[1]/channel[0])
                stats['stereo_phase_error_radians'] = float(abs(relative-.73))
                assert abs(relative-.73) < .05
            if scenario == 'stall':
                assert np.max(np.abs(pcm[int(3.7*RATE):int(3.95*RATE)])) < 1.e-6
                assert np.max(np.abs(pcm[int(4.4*RATE):int(4.9*RATE)])) > .5
            if scenario == 'reset':
                assert np.max(np.abs(pcm[int(3.1*RATE):int(3.9*RATE)])) == 0
                assert np.max(np.abs(pcm[int(4.4*RATE):int(4.9*RATE)])) > .5
            if kind == 3:
                # Count distinct transient clusters, allowing less than a grain of
                # local jitter but not missing clicks or repeated delayed echoes.
                envelope = np.abs(pcm[:,0])
                indices = np.flatnonzero(envelope>.30)
                groups = np.split(indices,np.flatnonzero(np.diff(indices)>RATE*.050)+1)
                peaks = [int(g[np.argmax(envelope[g])]) for g in groups if len(g)]
                expected = int(8*ratio/.5)+1
                stats['transient_count'] = len(peaks); stats['expected_input_transients'] = expected
                assert abs(len(peaks)-expected) <= 1, stats
                stats['median_transient_peak'] = float(np.median(envelope[peaks]))
                assert stats['median_transient_peak'] >= .6, stats
            results.append(stats)
            (output/'results-in-progress.json').write_text(json.dumps(results,indent=2)+'\n')
            print(stem, 'PASS', f"cost={stats['processing_realtime_fraction']*100:.3f}%",flush=True)
    manifest = {'results':results,'commands':commands,
        'source_sha256':hashlib.sha256((ROOT/'experiments/audio-tempo/AudioTempo.h').read_bytes()).hexdigest(),
        'scope':'Offline prototype; no app integration, game/audio/device acceptance, or physical CPU timing'}
    (output/'results.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
