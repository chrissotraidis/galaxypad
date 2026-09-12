#!/usr/bin/env python3
"""Exercise exact diagnostic header with bounded PCM, overflow and WAV roundtrip."""
import json, subprocess, tempfile, wave, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='galaxypad-pcm-test-') as tmp:
 p=Path(tmp)
 (p/'test.cpp').write_text(r'''
#include "DiagnosticPcmCapture.h"
#include <cassert>
int main(int argc,char** argv) {
 using galaxypad::diagnostic::PcmCapture;
 PcmCapture c;
 assert(!c.Start(argv[1],32000,8));
 assert(!c.Start(argv[1],48000,0));
 assert(c.Start(argv[1],48000,8));
 assert(!c.Start(argv[1],48000,8));
 int16_t a[]={1,-1,2,-2,3,-3,4,-4,5,-5,6,-6};
 c.Record(a,6,6,100);
 c.Record(a,6,3,200);
 c.Record(nullptr,2,2,300);
 assert(c.Finish());
 // Exclusive output creation must fail without replacing the prior capture.
 assert(c.Start(argv[1],48000,8)); c.Record(a,1,1,400);
 assert(!c.Finish());
 assert(c.Finish());
}
''')
 for flags in (['-O3'],['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']):
  exe=p/('test'+str(len(flags)))
  subprocess.run(['c++','-std=c++20',*flags,'-I',str(ROOT/'experiments/audio-pcm-capture'),str(p/'test.cpp'),'-o',str(exe)],check=True)
  wav=p/(exe.name+'.wav')
  subprocess.run([str(exe),str(wav)],check=True)
  with wave.open(str(wav)) as f:
   assert (f.getnchannels(),f.getframerate(),f.getsampwidth(),f.getnframes())==(2,48000,2,8)
   assert struct.unpack('<16h',f.readframes(8))==(1,-1,2,-2,3,-3,4,-4,5,-5,6,-6,1,-1,2,-2)
  m=json.loads(Path(str(wav)+'.json').read_text())
  assert m['captured_frames']==8 and m['observed_mixed_frames']==9
  assert m['omitted_after_limit_frames']==1 and m['short_callbacks']==1 and m['invalid_callbacks']==1
  assert m['callbacks']==3 and m['callback_requested_min']==2 and m['callback_requested_max']==6
  assert m['first_host_time']==100 and m['last_host_time']==300 and m['wav_write_ok']
 print('PASS: O3 and ASan/UBSan PCM exact stereo roundtrip, limit, short/null callbacks, rate gate, exclusive creation')
