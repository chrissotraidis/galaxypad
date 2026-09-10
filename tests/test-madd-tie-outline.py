"""Compare exact scalar result/state/host flags, including constructed FMA ties."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from outline_madd_tie import transform

core = root / 'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source = (core / 'cpu_interpreter_float.c').read_text()
changed = transform(source)
try:
    transform(source + '\n')
except ValueError:
    pass
else:
    raise AssertionError('Source mismatch accepted')
start = changed.index('__attribute__((noinline,cold)) static f64 galaxypad_madd_tie(')
end = changed.index('\nbool fp_invalid_gated(', start)
candidate = changed[start:end].replace('FPRes ni_madd_msub(', 'FPRes candidate_madd(')
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
  0xfff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000000123ull};
 u64 seed=0x315aa832ull; unsigned ties=0, corrections=0, cases=0;
 for(unsigned mode=0;mode<4;mode++) {
  assert(fesetround(modes[mode])==0);
  for(unsigned i=0;i<60000;i++) {
   f64 a,b,c;
   if(i<1000) { a=f64_value(special[i/100]); b=f64_value(special[i/10%10]); c=f64_value(special[i%10]); }
   else if(i<11000) {
    // Exactly representable halfway values plus perturbations smaller than a double ULP.
    a=f64_value(0x3ff0000010000000ull+((u64)(i%16)<<29));
    c=1.0; b=(i&1)?0x1p-55:-0x1p-55;
    if(i&2) a=-a;
   } else { a=f64_value(rng(&seed)); b=f64_value(rng(&seed)); c=f64_value(rng(&seed)); }
   for(unsigned variant=0;variant<4;variant++) {
    bool sub=variant&1, single=variant&2;
    f64 initial=single?fma(a,force_25bit_c(c),sub?-b:b):0.0;
    bool tie=single && ((f64_bits(initial)&0x1fffffffull)==0x10000000ull);
    ties+=tie;
    CPUState reference={0}; reference.fpscr=(u32)rng(&seed); CPUState actual=reference;
    assert(feclearexcept(FE_ALL_EXCEPT)==0);
    FPRes expected=ni_madd_msub(&reference,a,c,b,sub,single);
    int flags=fetestexcept(FE_ALL_EXCEPT);
    corrections+=tie && isfinite(initial) && f64_bits(initial)!=f64_bits(expected.value);
    assert(feclearexcept(FE_ALL_EXCEPT)==0);
    FPRes result=candidate_madd(&actual,a,c,b,sub,single);
    assert(flags==fetestexcept(FE_ALL_EXCEPT));
    assert(f64_bits(expected.value)==f64_bits(result.value));
    assert(expected.exception==result.exception);
    assert(!memcmp(&reference,&actual,sizeof actual)); cases++;
   }
  }
 }
 assert(ties>1000 && corrections>1000);
 printf("%u scalar result/state/host-flags cases; %u ties, %u corrected results pass\n",cases,ties,corrections);
}
'''.replace('CANDIDATE', candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-madd-tie-') as directory:
    path = Path(directory)
    (path / 'test.c').write_text(program)
    for flags in (['-O1', '-fsanitize=address,undefined'], ['-O2']):
        subprocess.run(['clang', '-std=c11', '-ffp-contract=off', '-fno-fast-math',
                        '-ffunction-sections', '-fdata-sections', '-I', str(core),
                        '-I', str(core.parent.parent / 'include'), *flags,
                        str(path / 'test.c'), '-Wl,-dead_strip', '-o', str(path / 'test')], check=True)
        subprocess.run([str(path / 'test')], check=True)
