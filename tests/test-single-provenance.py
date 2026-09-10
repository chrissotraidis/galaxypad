"""Audit canonical-single identity and its NI boundary; no product transform."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
program = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
int main(void) {
  const u64 special[] = {0,0x8000000000000000ull,1,0x000fffffffffffffull,
    0x0010000000000000ull,0x380fffffffffffffull,0x3810000000000000ull,
    0x7fefffffffffffffull,0x7ff0000000000000ull,0xfff0000000000000ull,
    0x7ff0000000000001ull,0x7ff8000000000123ull,0xfff8000000000123ull};
  u64 seed=0x465001ull, saved;
  __asm__ volatile("mrs %0, fpcr":"=r"(saved));
  unsigned count=0;
  for (unsigned rn=0;rn<4;++rn) for (unsigned ni=0;ni<2;++ni) {
    CPUState cpu={0}; cpu.fpscr=rn|(ni?FPSCR_NI_BIT:0);
    ppc_fpscr_control_updated(&cpu);
    for (unsigned i=0;i<100000;++i) {
      seed^=seed<<13; seed^=seed>>7; seed^=seed<<17;
      f64 input=f64_value(i<sizeof(special)/sizeof(*special)?special[i]:seed);
      volatile f64 canonical=(f64)force_single(&cpu,input);
      assert(!feclearexcept(FE_ALL_EXCEPT));
      f64 result=(f64)force_single(&cpu,canonical);
      assert(f64_bits(result)==f64_bits(canonical));
      assert(!fetestexcept(FE_ALL_EXCEPT));
      count++;
    }
  }
  CPUState cpu={0}; ppc_fpscr_control_updated(&cpu);
  volatile f64 subnormal=(f64)force_single(&cpu,0x1p-140);
  assert(subnormal!=0);
  cpu.fpscr=FPSCR_NI_BIT;
  assert((f64)force_single(&cpu,subnormal)==0);
  assert(f64_bits(subnormal)!=f64_bits((f64)force_single(&cpu,subnormal)));
  __asm__ volatile("msr fpcr, %0"::"r"(saved));
  printf("%u canonical-single identities preserve bits/host flags; NI-change counterexample confirmed\n",count);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-single-provenance-') as directory:
    temp=Path(directory); (temp/'probe.c').write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
        '-fsanitize=undefined','-ffunction-sections','-fdata-sections','-Wl,-dead_strip',
        '-I'+str(core),'-I'+str(core.parent.parent/'include'),str(temp/'probe.c'),
        '-o',str(temp/'probe')],check=True)
    subprocess.run([str(temp/'probe')],check=True)
