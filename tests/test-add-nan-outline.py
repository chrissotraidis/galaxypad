"""Compare ni_add result, exception, whole CPU state and host FP flags."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from outline_add_nan import transform

core = root / 'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source = (core / 'cpu_interpreter_float.c').read_text()
changed = transform(source)
try:
    transform(source + '\n')
except ValueError:
    pass
else:
    raise AssertionError('Source mismatch accepted')
start = changed.index('__attribute__((noinline,cold)) static FPRes galaxypad_add_nan(')
end = changed.index('FPRes ni_sub(', start)
candidate = changed[start:end].replace('FPRes ni_add(', 'FPRes candidate_add(')
assert changed[:start] == source[:source.index('FPRes ni_add(')]
assert changed[end:] == source[source.index('FPRes ni_sub('):]
program = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
CANDIDATE
static u64 rng(u64* s) { *s^=*s<<13; *s^=*s>>7; *s^=*s<<17; return *s; }
int main(void) {
 const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
 const u64 special[]={0,0x8000000000000000ull,1,0xfffffffffffffull,
  0x10000000000000ull,0x7fefffffffffffffull,0x7ff0000000000000ull,
  0xfff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000000123ull,
  0xfff0000000000123ull,0xfff8000000000456ull};
 u64 seed=0x332aa832ull; unsigned cases=0,nans=0;
 for(unsigned mode=0;mode<4;mode++) {
  assert(fesetround(modes[mode])==0);
  for(unsigned i=0;i<60000;i++) {
   f64 a=f64_value(i<144?special[i/12]:rng(&seed));
   f64 b=f64_value(i<144?special[i%12]:rng(&seed));
   CPUState reference={0}; reference.fpscr=(u32)rng(&seed); CPUState actual=reference;
   assert(feclearexcept(FE_ALL_EXCEPT)==0);
   FPRes expected=ni_add(&reference,a,b);
   int flags=fetestexcept(FE_ALL_EXCEPT);
   assert(feclearexcept(FE_ALL_EXCEPT)==0);
   FPRes result=candidate_add(&actual,a,b);
   assert(flags==fetestexcept(FE_ALL_EXCEPT));
   assert(f64_bits(expected.value)==f64_bits(result.value));
   assert(expected.exception==result.exception);
   assert(!memcmp(&reference,&actual,sizeof actual)); cases++;
   nans+=isnan(expected.value);
  }
 }
 assert(nans>100);
 printf("%u ni_add state/result/host-flags cases, %u NaN results pass\n",cases,nans);
}
'''.replace('CANDIDATE', candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-add-nan-') as temporary:
    directory=Path(temporary)
    harness=directory/'probe.c'; harness.write_text(program)
    for name, flags in [('sanitized',['-O1','-fsanitize=address,undefined']),('optimized',['-O2'])]:
        binary=directory/name
        subprocess.run(['clang','-std=c11',*flags,'-ffp-contract=off','-fno-fast-math',
                        '-ffunction-sections','-fdata-sections',
                        '-I',str(core),'-I',str(core.parent.parent/'include'),str(harness),
                        '-Wl,-dead_strip','-lm','-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
