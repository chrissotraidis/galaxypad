"""Source-derived classification prototype; no runtime source modification."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu_interpreter_float.c').read_text()
original = 'u32 reference(' + source.split('u32 classify_f32(',1)[1].split('\nvoid set_fprf',1)[0]
candidate = original.replace('u32 reference(', 'u32 candidate(')
anchor='    u32 fraction = bits & 0x007FFFFFu;'
assert candidate.count(anchor)==1
candidate=candidate.replace(anchor,anchor+'\n'+(root/'patches/experiments/classify-f32-normal.inc').read_text())
code=r'''
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>
#include <time.h>
typedef uint32_t u32; typedef float f32;
'''+original+candidate+r'''
static void check(u32 bits) {
  f32 value;memcpy(&value,&bits,4);
  assert(reference(value)==candidate(value));
}
int main(void) {
  // Exhaust both special exponent classes, both signs, every fraction.
  for(u32 frac=0;frac<0x800000;frac++) {
    check(frac);check(frac|0x80000000);
    check(frac|0x7f800000);check(frac|0xff800000);
  }
  // Normal exponent/sign classes, representative fractions and random bits.
  u32 random=123;
  for(u32 e=1;e<255;e++) for(u32 s=0;s<2;s++) {
    check((e<<23)|(s<<31));check((e<<23)|(s<<31)|0x7fffff);
  }
  for(unsigned i=0;i<1000000;i++) {
    random=random*1664525u+1013904223u;check(random);
  }
  puts("all special-value bit patterns and normal-class/random classification parity passed");
#ifdef BENCHMARK
  volatile u32 sink=0;
  for(unsigned trial=0;trial<6;trial++) {
    double times[2];
    for(unsigned order=0;order<2;order++) {
      unsigned choice=order^(trial&1);
      u32 (*volatile fn)(f32)=choice?candidate:reference;
      clock_t begin=clock();
      for(unsigned i=0;i<10000000;i++) sink=fn((i&1)?-12.25f:34.5f);
      times[choice]=(double)(clock()-begin)/CLOCKS_PER_SEC;
    }
    printf("classify candidate/reference %.4f (%.6f/%.6f)\n",times[1]/times[0],times[1],times[0]);
  }
  (void)sink;
#endif
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-classify-') as temp:
    base=Path(temp);(base/'test.c').write_text(code)
    for mode in ['sanitize','benchmark']:
        flags=['-fsanitize=undefined'] if mode=='sanitize' else ['-DBENCHMARK']
        subprocess.run(['clang','-O2',*flags,str(base/'test.c'),'-o',str(base/mode)],check=True)
        subprocess.run([str(base/mode)],check=True)
