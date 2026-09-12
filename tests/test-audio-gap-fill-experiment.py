#!/usr/bin/env python3
"""Offline production-FIFO regression, not hardware sound or runtime acceptance.

Compile exact MixerFifo Mix/Enqueue/Dequeue bodies and actual Mixer.h layout.
Stub unrelated configuration/decoder/logging/diagnostics dependencies only.
Both variants use Apple startup/rate policy. Tests never launch the game.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('experiment', ROOT/'scripts/create-audio-gap-fill-experiment.py')
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)

PREFIX = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <limits>
#include <memory>
#include <string>
#include <vector>
using s16 = int16_t; using s32 = int32_t; using u8 = uint8_t;
using u32 = uint32_t; using u64 = uint64_t;
using DT_s = std::chrono::duration<double>;
#define DOLPHIN_FORCE_INLINE inline
#define WARN_LOG_FMT(...)
namespace AudioCommon {struct SurroundDecoder {};}
struct WaveFileWriter {};
namespace Config {using ConfigChangedCallbackID = int;}
namespace MathUtil {
template<class T, class V> T SaturatingCast(V v) {
 return static_cast<T>(std::clamp(v, static_cast<V>(std::numeric_limits<T>::min()),
                                   static_cast<V>(std::numeric_limits<T>::max())));
}}
namespace Core {
enum class State {Running, Paused}; inline State state = State::Running;
struct System {static System& GetInstance(){static System s;return s;}};
inline State GetState(System&) {return state;}
}
namespace GalaxyPadDiagnostics {
inline void RecordDmaQueueFullDrop() {} inline void RecordDmaBacklogDrop() {}
inline void RecordDmaEnqueue(size_t, int64_t) {} inline void RecordDmaUnderrun() {}
}
'''

HARNESS = r'''
Mixer::Mixer(u32 rate): m_output_sample_rate(rate) {
 m_config_emulation_speed=1; m_config_audio_preserve_pitch=false;
 m_config_fill_audio_gaps=true; m_config_audio_buffer_ms=120;
}
Mixer::~Mixer() = default;

extern "C" void* NAME(create)(bool fill) {
 auto* m = new Mixer(48000); m->m_config_fill_audio_gaps=fill; return m;
}
extern "C" void NAME(destroy)(void* p) {delete static_cast<Mixer*>(p);}
extern "C" void NAME(running)(bool running) {
 Core::state=running ? Core::State::Running : Core::State::Paused;
}
extern "C" void NAME(push)(void* p, const s16* samples, size_t n) {
 auto* m=static_cast<Mixer*>(p);
 for(size_t i=0;i<n;i++) m->m_dma_mixer.PushSample(samples[2*i],samples[2*i+1]);
}
extern "C" void NAME(mix)(void* p, s16* samples, size_t n) {
 std::fill(samples,samples+2*n,0); static_cast<Mixer*>(p)->m_dma_mixer.Mix(samples,n);
}
'''

MAIN = r'''
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>
using s16=int16_t;
extern "C" {
void* control_create(bool);void* candidate_create(bool);
void control_destroy(void*);void candidate_destroy(void*);
void control_running(bool);void candidate_running(bool);
void control_push(void*,const s16*,size_t);void candidate_push(void*,const s16*,size_t);
void control_mix(void*,s16*,size_t);void candidate_mix(void*,s16*,size_t);
}
struct API {
 void* (*create)(bool);void(*destroy)(void*);void(*running)(bool);
 void(*push)(void*,const s16*,size_t);void(*mix)(void*,s16*,size_t);
};
API control{control_create,control_destroy,control_running,control_push,control_mix};
API candidate{candidate_create,candidate_destroy,candidate_running,candidate_push,candidate_mix};
struct Result {std::vector<s16> pcm;size_t silent_frames=0,max_silent=0;double rms=0;};
Result render(API a, double ratio, bool fill, int callback, bool lifecycle=false) {
 auto* m=a.create(fill);a.running(true);Result result;size_t input_index=0;double owed=0;
 // 8 seconds: settled playback, optional complete stall, pause, resume.
 for(int frame=0;frame<8*48000;frame+=callback) {
   double t=frame/48000.;bool pause=lifecycle && t>=4 && t<5;
   bool stall=lifecycle && t>=2 && t<3;
   a.running(!pause);
   owed += (pause || stall)?0:callback*32000.*ratio/48000.;
   size_t count=static_cast<size_t>(owed);owed-=count;
   std::vector<s16> input(count*2);
   for(size_t i=0;i<count;i++,input_index++) {
     // Non-window-periodic stereo tones expose replay cancellation/modulation.
     input[2*i]=std::lround(10000*std::sin(2*3.141592653589793*997*input_index/32000.));
     input[2*i+1]=std::lround(8000*std::sin(2*3.141592653589793*431*input_index/32000.));
   }
   a.push(m,input.data(),count);std::vector<s16> output(callback*2);
   a.mix(m,output.data(),callback);
   result.pcm.insert(result.pcm.end(),output.begin(),output.end());
 }
 a.destroy(m);size_t run=0;double power=0;
 for(size_t i=48000;i<result.pcm.size()/2;i++) {
   int l=result.pcm[2*i],r=result.pcm[2*i+1];power+=double(l)*l+double(r)*r;
   if(abs(l)<=1 && abs(r)<=1){result.silent_frames++;run++;result.max_silent=std::max(run,result.max_silent);}
   else run=0;
 }
 result.rms=std::sqrt(power/((result.pcm.size()/2-48000)*2));return result;
}
double peak(const Result& r,double start,double end) {
 double p=0;for(size_t i=start*48000*2;i<end*48000*2;i++)p=std::max(p,double(abs(r.pcm[i])));return p;
}
int main() {
 for(int callback:{128,512}) {
   auto nominal_a=render(control,1,true,callback),nominal_b=render(candidate,1,true,callback);
   assert(nominal_a.pcm==nominal_b.pcm);
   auto off_a=render(control,44./60,false,callback),off_b=render(candidate,44./60,false,callback);
   assert(off_a.pcm==off_b.pcm);
   for(double ratio:{44./60,0.85,0.98}) {
     auto old=render(control,ratio,true,callback),fresh=render(candidate,ratio,true,callback);
     printf("callback=%d ratio=%.6f control_silence=%zu/%zu candidate_silence=%zu/%zu rms=%.2f/%.2f\n",
       callback,ratio,old.silent_frames,old.max_silent,fresh.silent_frames,fresh.max_silent,old.rms,fresh.rms);
     assert(fresh.max_silent<48); // No 1 ms simultaneous stereo silence after startup.
     if(ratio<0.9)assert(old.max_silent>480 && fresh.rms>old.rms);
   }
   auto cycle=render(candidate,44./60,true,callback,true);
   assert(peak(cycle,2.9,3.0)<=2); // Complete producer stall fades repeated history away.
   assert(peak(cycle,4.3,4.9)<=1); // Paused core never continuously replays history.
   assert(peak(cycle,5.3,5.9)>1000); // Resume refills reserve and recovers signal.
   printf("callback=%d nominal and disabled output exact; stall fade/pause/resume PASS\n",callback);
 }
}
'''


def fifo_source(source):
    sections = []
    for begin, end in [('void Mixer::MixerFifo::Mix(', '\nstd::size_t Mixer::Mix('),
                       ('void Mixer::MixerFifo::Enqueue()', '\nbool Mixer::MixerFifo::Dequeue(')]:
        start = source.index(begin)
        sections.append(source[start:source.index(end, start)])
    sections.append(source[source.index('bool Mixer::MixerFifo::Dequeue('):])
    return '\n'.join(sections)


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    original = (experiment.SOURCE/'Mixer.cpp').read_text()
    header = (experiment.SOURCE/'Mixer.h').read_text()
    # Keep actual data layout/operators/PushSample; expose members only for fixture access.
    header = re.sub(r'^#(?:include|pragma).*\n', '', header, flags=re.M).replace('private:', 'public:')
    for name, source in [('control', original), ('candidate', experiment.candidate(original))]:
        body = PREFIX + '\nnamespace '+name+' {\n' + header + '\n' + fifo_source(source)
        body += '\n#define NAME(x) '+name+'_ ## x\n' + HARNESS + '\n#undef NAME\n}\n'
        (output/(name+'.cpp')).write_text(body)
    (output/'main.cpp').write_text(MAIN)
    compiler = shutil.which('clang++')
    if not compiler:
        raise RuntimeError('clang++ required')
    commands=[]
    for label, flags in [('O2', ['-O2']), ('sanitized', ['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
        command=[compiler,'-std=c++20','-D__APPLE__=1',*flags,
                 *[str(output/(n+'.cpp')) for n in ['control','candidate','main']],'-o',str(output/label)]
        commands.append(command)
        subprocess.run(command,check=True)
        print(label,flush=True)
        subprocess.run([str(output/label)],check=True)
    (output/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output:run(args.output)
    else:
        with tempfile.TemporaryDirectory(prefix='galaxypad-audio-gap-') as temp:run(Path(temp))
