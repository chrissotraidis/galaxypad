#!/usr/bin/env python3
"""Compile exact copied Mixer methods and validate real 48 kHz PCM offline."""
import argparse, importlib.util, json, re, shutil, subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gap',ROOT/'tests/test-audio-gap-fill-experiment.py');gap=importlib.util.module_from_spec(spec);spec.loader.exec_module(gap)
def method(s,begin,end):
 a=s.index(begin);return s[a:s.index(end,a)]
PREFIX=gap.PREFIX.replace('struct WaveFileWriter {};','struct WaveFileWriter {void AddStereoSamplesBE(const s16*,u32,s32,s32,s32){}};').replace('#define WARN_LOG_FMT(...)','#define WARN_LOG_FMT(...)\n#define ERROR_LOG_FMT(...)').replace('inline void RecordDmaEnqueue(size_t, int64_t) {} inline void RecordDmaUnderrun() {}','inline uint64_t enqueues=0, underruns=0; inline void RecordDmaEnqueue(size_t, int64_t) {++enqueues;} inline void RecordDmaUnderrun() {++underruns;}')+r'''
#include <fstream>
#include <iostream>
namespace Common {inline u16_t_dummy_not_used() = delete;}
'''.replace('namespace Common {inline u16_t_dummy_not_used() = delete;}','namespace Common {inline uint16_t swap16(uint16_t x){return __builtin_bswap16(x);}}\nclass PointerWrap {public: bool IsReadMode() const {return true;} void Do(u32& value){value=3375;} template<class T> void Do(T&) {}};')
HARNESS=r'''
Mixer::Mixer(u32 rate):m_output_sample_rate(rate) {
 m_config_emulation_speed=1; m_config_audio_preserve_pitch=false;
 m_config_fill_audio_gaps=true;m_config_audio_buffer_ms=120;
}
Mixer::~Mixer()=default;
int main(int argc,char** argv) {
 assert(argc==6);double ratio=std::stod(argv[1]);int callback=std::stoi(argv[2]);
 std::string scenario=argv[3], output=argv[4];double freq=std::stod(argv[5]);
 auto mixer=std::make_unique<Mixer>(48000);auto& m=*mixer;
 std::vector<s16> pcm;double owed=0;uint64_t index=0;double maxAge=0;
 for(int frame=0;frame<8*48000;frame+=callback) {
  double t=frame/48000.;bool pause=scenario=="pause"&&t>=3&&t<4;
  bool stall=scenario=="stall"&&t>=3&&t<4;
  Core::state=pause?Core::State::Paused:Core::State::Running;
  double speed=scenario=="changing"?(t<2?1:(t<5?.67:.85)):ratio;
  owed+=(pause||stall)?0:callback*32000.*speed/48000.;
  int burst=scenario=="bursty6"?6:(scenario=="bursty"?3:1);
  size_t count=(frame/callback)%burst==burst-1?size_t(owed):0;
  if(count)owed-=count;
  std::vector<s16> input(count*2);
  for(size_t i=0;i<count;i++,index++) {
   s16 l=std::lround(10000*std::sin(2*3.141592653589793*freq*index/32000.));
   s16 r=std::lround(8000*std::sin(2*3.141592653589793*431*index/32000.));
   input[2*i]=Common::swap16(r);input[2*i+1]=Common::swap16(l);
   fixtureArrivals.push_back(t);
  }
  m.PushSamples(input.data(),count);
  if(scenario=="restore"&&frame/callback==int(3*48000/callback)) {
   FIXTURE_RESTORE
  }
  if(scenario=="unsupported"&&frame/callback==int(3*48000/callback)) {
   m.m_dma_mixer.SetInputSampleRateDivisor(Mixer::FIXED_SAMPLE_RATE_DIVIDEND/48000);
   FIXTURE_UNSUPPORTED
  }
  std::vector<s16> block(callback*2);fixtureNow=t;fixtureOutput=0;
  m.m_dma_mixer.Mix(block.data(),callback);
  if(pause)for(auto sample:block)assert(sample==0);
  pcm.insert(pcm.end(),block.begin(),block.end());
 }
 std::ofstream f(output,std::ios::binary);f.write(reinterpret_cast<const char*>(pcm.data()),pcm.size()*2);
 FIXTURE_STATS
}
'''

def run(candidate,out):
 out.mkdir(parents=True,exist_ok=False)
 original=(gap.experiment.SOURCE/'Mixer.cpp').read_text();oh=(gap.experiment.SOURCE/'Mixer.h').read_text()
 commands=[];results=[]
 for variant in ['candidate','reference','control']:
  c=(candidate/'Mixer.cpp').read_text() if variant=='candidate' else original
  h=(candidate/'Mixer.h').read_text() if variant=='candidate' else oh
  h=re.sub(r'^#(?:include|pragma).*\n','',h,flags=re.M).replace('private:','public:')
  extra='inline std::vector<double> fixtureArrivals; inline double fixtureNow=0,fixtureAge=0,fixtureAgeAt=0; inline size_t fixtureOutput=0;\n'
  if variant=='candidate':
   h=h.replace('    Granule m_front{}, m_back{};','''    Granule m_front{}, m_back{};
    std::array<uint64_t,256> fixtureFront{},fixtureBack{};
    std::array<uint64_t,128> fixturePrevious{};
''')
   # Source ordinal +1 allows zero-initialized no-source markers.
   h=h.replace('    std::array<uint64_t,128> fixturePrevious{};', '    std::array<uint64_t,128> fixturePrevious{};\n    std::array<uint64_t,1536> fixtureCallback{};')
   c=c.replace('m_mixer->m_dma_tempo.Pull(m_mixer->m_dma_tempo_callback.data(), tempo_frames);',
               'm_mixer->m_dma_tempo.Pull(m_mixer->m_dma_tempo_callback.data(), tempo_frames, fixtureCallback.data());')
   c=c.replace('    Granule raw;',"""    auto& markers = granule == &m_front ? fixtureFront : fixtureBack;
    for(size_t i=0;i<128;i++) {
      const auto source=fixtureCallback[m_mixer->m_dma_tempo_callback_index-128+i];
      markers[i]=fixturePrevious[i];
      markers[i+128]=source==galaxypad::experiment::AudioTempo::NoSource?0:source+1;
      fixturePrevious[i]=markers[i+128];
    }
    Granule raw;""")
   c=c.replace('  m_front = {}; m_back = {}; m_current_index = 0;','  m_front = {}; m_back = {}; m_current_index = 0;\n  fixtureFront={};fixtureBack={};fixturePrevious={};')
   needle='    // Polynomial Interpolators'
   c=c.replace(needle,'''    for(int delta=-2;delta<=3;delta++) {
      for(auto source : {fixtureFront[(ft+delta)&GRANULE_MASK],fixtureBack[(bt+delta)&GRANULE_MASK]})
        if(source) {
          const double age=fixtureNow+fixtureOutput/48000.-fixtureArrivals.at(source-1);
          if(age>fixtureAge){fixtureAge=age;fixtureAgeAt=fixtureNow+fixtureOutput/48000.;}
        }
    }
    ++fixtureOutput;
'''+needle)
   body=method(c,'void Mixer::MixerFifo::DoState(','\nvoid Mixer::MixerFifo::SetInputSampleRateDividend(')
   body+=method(c,'void Mixer::MixerFifo::Mix(','\nstd::size_t Mixer::Mix(')
   body+=method(c,'void Mixer::PushSamples(','\nvoid Mixer::PushStreamingSamples(')
   body+=method(c,'void Mixer::MixerFifo::SetInputSampleRateDivisor(','\nu32 Mixer::MixerFifo::GetInputSampleRateDivisor(')
   body+=method(c,'u32 Mixer::MixerFifo::GetInputSampleRateDivisor(','\nvoid Mixer::MixerFifo::SetVolume(')
   body+=method(c,'std::pair<s32, s32> Mixer::MixerFifo::GetVolume(','\nvoid Mixer::MixerFifo::ApplyGranuleWindow(')
   body+=c[c.index('void Mixer::MixerFifo::ApplyGranuleWindow('):]
   harness=HARNESS.replace('FIXTURE_RESTORE','PointerWrap p; m.m_dma_mixer.DoState(p);').replace('FIXTURE_UNSUPPORTED','assert(m.m_dma_tempo_failed.load());assert(m.m_dma_mixer.GetInputSampleRateDivisor()==3375);')
   harness=harness.replace('FIXTURE_STATS',r'''auto s=m.m_dma_tempo.ReadStatistics();
 assert(GalaxyPadDiagnostics::enqueues==s.inputAccepted/128);
 assert(GalaxyPadDiagnostics::underruns==s.unavailableWindows);
 std::cout<<"{\"underruns\":"<<s.unavailableWindows<<",\"input_accepted\":"<<s.inputAccepted<<",\"input_rejected\":"<<s.inputRejected<<",\"enqueues\":"<<GalaxyPadDiagnostics::enqueues<<",\"max_wall_age_ms\":"<<fixtureAge*1000<<",\"max_age_at\":"<<fixtureAgeAt<<"}\n";''')
  else:
   if variant=='reference':
    a=c.index('#if defined(__APPLE__)');b=c.index('#endif',a)+len('#endif');c=c[:a]+c[b:]
   body=gap.fifo_source(c)
   body+=method(c,'void Mixer::PushSamples(','\nvoid Mixer::PushStreamingSamples(')
   body+=method(c,'void Mixer::MixerFifo::SetInputSampleRateDivisor(','\nu32 Mixer::MixerFifo::GetInputSampleRateDivisor(')
   body+=method(c,'u32 Mixer::MixerFifo::GetInputSampleRateDivisor(','\nvoid Mixer::MixerFifo::SetVolume(')
   body+=method(c,'std::pair<s32, s32> Mixer::MixerFifo::GetVolume(','\nvoid Mixer::MixerFifo::Enqueue(')
   harness=HARNESS.replace('FIXTURE_RESTORE','').replace('FIXTURE_UNSUPPORTED','').replace('FIXTURE_STATS','std::cout<<"{}\\n";')
  tempo_header = candidate/'AudioTempo.h'
  if not tempo_header.exists(): tempo_header = candidate.parent/'AudioTempo.h'
  unit=PREFIX+'\n#include "'+str(tempo_header)+'"\n'+extra+h+'\n'+body+'\n'+harness
  (out/(variant+'.cpp')).write_text(unit)
  for label,flags in [('release',['-O3']),('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
   if variant!='candidate' and label=='sanitized':continue
   exe=out/(variant+'-'+label)
   cmd=[shutil.which('clang++'),'-std=c++20',*flags,str(out/(variant+'.cpp')),'-o',str(exe)];commands.append(cmd);subprocess.run(cmd,check=True)
   cases=[(1,512,'steady',997)]
   if variant=='candidate':cases +=[(r,512,'steady',f) for r in (.67,.74,.85) for f in (55,997)]+[(.67,512,'bursty6',55),(.67,1024,'bursty',997),(.67,512,'changing',997),(.67,512,'stall',997),(.67,512,'pause',997),(.67,512,'restore',997),(.67,512,'unsupported',997)]
   for ratio,callback,scenario,freq in cases:
    stem=f'{variant}-{label}-{ratio}-{callback}-{scenario}-{freq}';path=out/(stem+'.s16')
    cmd=[str(exe),str(ratio),str(callback),scenario,str(path),str(freq)];p=subprocess.run(cmd,text=True,capture_output=True);assert p.returncode==0,(cmd,p.stdout,p.stderr)
    row=json.loads(p.stdout);row.update(name=stem,ratio=ratio,scenario=scenario)
    pcm=np.fromfile(path,np.int16).reshape(-1,2);x=pcm[48000*2:48000*7,0].astype(float)
    if scenario in ('steady','bursty','bursty6'):
     power=np.abs(np.fft.rfft(x*np.hanning(len(x))))**2;f=np.fft.rfftfreq(len(x),1/48000);peak=f[np.argmax(power)];row['pitch_hz']=float(peak);row['tone_band_power']=float(power[abs(f-freq)<=5].sum()/power.sum())
     if variant=='candidate':assert abs(peak-freq)<=2 and row['tone_band_power']>.85,row
    if variant=='candidate':
     assert row['max_wall_age_ms']<=120,row
     if scenario not in ('stall','unsupported'):assert row['underruns']==0,row
     if scenario=='stall':assert row['underruns']>0 and np.max(np.abs(pcm[int(3.8*48000):int(3.95*48000)]))<=1,row
     if scenario in ('pause','restore'):assert np.max(abs(pcm[int(4.4*48000):int(4.9*48000)]))>1000,row
     if scenario=='unsupported':assert np.max(abs(pcm[int(3.2*48000):]))==0,row
    results.append(row);print(row,flush=True)
 (out/'results.json').write_text(json.dumps({'results':results,'commands':commands},indent=2)+'\n')
 # Compare against the exact legacy fixed-rate kernel after integer time alignment.
 a=np.fromfile(out/'candidate-release-1-512-steady-997.s16',np.int16).reshape(-1,2)
 b=np.fromfile(out/'reference-release-1-512-steady-997.s16',np.int16).reshape(-1,2)
 start=48000*2;length=48000
 scores=[np.mean((a[start:start+length].astype(float)-b[start+shift:start+length+shift])**2) for shift in range(-6000,6001)]
 shift=int(np.argmin(scores))-6000;error=a[start:start+length].astype(float)-b[start+shift:start+length+shift]
 comparison={'reference_time_shift_48k_samples':shift,'aligned_rms_s16_error':float(np.sqrt(np.mean(error**2))),'aligned_max_s16_error':float(abs(error).max())}
 assert comparison['aligned_rms_s16_error'] <= 1 and comparison['aligned_max_s16_error'] <= 3, comparison
 (out/'reference-comparison.json').write_text(json.dumps(comparison,indent=2)+'\n');print(comparison)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.candidate.resolve(),a.output.resolve())
