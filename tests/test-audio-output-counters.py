"""RemoteIO telemetry buffer bounds, opt-out, peaks, reset and concurrent reads."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
vendor=root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common'
assert (root/'apple/shared/GalaxyPadAudioOutputCounters.h').read_bytes() == (vendor/'GalaxyPadAudioOutputCounters.h').read_bytes()
source=r'''
#include "GalaxyPadAudioOutputCounters.h"
#include <cassert>
#include <thread>
extern "C" std::uint64_t ReadSharedFrames();
int main() {
 galaxypad::audio::OutputCounters counters;
 const std::int16_t samples[]={0,0,-32768,32767,0,-1};
 galaxypad::audio::outputCounters.Start(true);
 galaxypad::audio::outputCounters.Record(samples,3,3);
 assert(ReadSharedFrames()==3); // App and runtime translation units share storage.
 counters.Record(nullptr,UINT32_MAX,UINT32_MAX);
 assert(!counters.Read().available && counters.Read().callbacks==0);
 counters.Start(true);
 counters.Record(samples,3,3);
 auto s=counters.Read();
 assert(s.available && s.callbacks==1 && s.frames==3 && s.nonzeroFrames==2 && s.peak==32768);
 counters.Record(samples,10,1); // Only first silent stereo pair is accessible.
 counters.Record(nullptr,8,8);
 counters.Record(samples,0,3);
 s=counters.Read();
 assert(s.callbacks==4 && s.requestedFrames==21 && s.frames==4 && s.shortCallbacks==2);
 assert(s.nonzeroFrames==2 && s.peak==32768);
 counters.Start(false);counters.Record(samples,3,3);
 s=counters.Read();assert(!s.available && !s.callbacks && !s.peak);
 counters.Start(true);
 std::atomic<bool> done=false;
 std::thread writer([&]{for(int i=0;i<100000;i++)counters.Record(samples,3,3);done=true;});
 std::uint64_t previous=0;
 while(!done.load()) {s=counters.Read();assert(s.callbacks>=previous);previous=s.callbacks;}
 writer.join();s=counters.Read();
 assert(s.callbacks==100000 && s.frames==300000 && s.nonzeroFrames==200000);
 assert(s.shortCallbacks==0 && s.peak==32768);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-audio-output-') as directory:
    c=Path(directory)/'test.cpp';binary=Path(directory)/'test';c.write_text(source)
    other=Path(directory)/'runtime.cpp'
    other.write_text('#include "'+str(vendor/'GalaxyPadAudioOutputCounters.h')+'"\nextern "C" std::uint64_t ReadSharedFrames(){return galaxypad::audio::outputCounters.Read().frames;}\n')
    subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined',
                    '-I',str(root/'apple/shared'),str(c),str(other),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Audio output counters: bounds, silence, signed peak, opt-out/reset and concurrent reads pass')
