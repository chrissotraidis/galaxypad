"""Actual scalar helpers: instruction name alone cannot establish single precision."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
program=r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <stdio.h>
int main(void) {
 unsigned cases=0;
 for(unsigned op=0;op<2;op++)for(unsigned enabled=0;enabled<2;enabled++)
 for(unsigned alias=0;alias<3;alias++) {
   CPUState c={0};c.fpscr=enabled?FPSCR_VE_BIT:0;
   c.fpr[0]=1.234567890123;c.ps1[0]=-1.876543210987;
   c.fpr[1]=op?f64_value(0x7ff0000000000001ull):f64_value(0x7ff0000000000000ull);
   c.ps1[1]=1.234567890123;c.fpr[2]=0;c.ps1[2]=-1.234567890123;
   u64 before0=f64_bits(c.fpr[alias]),before1=f64_bits(c.ps1[alias]);
   if(op)ppc_frsp(&c,alias,1);else ppc_fmuls(&c,alias,1,2);
   assert(c.fpscr & FPSCR_VX_ANY_MASK);
   if(enabled) {
     assert(f64_bits(c.fpr[alias])==before0 && f64_bits(c.ps1[alias])==before1);
     if(alias==0)assert(f64_bits(force_25bit_c(c.fpr[0]))!=f64_bits(c.fpr[0]));
   } else {
     assert(isnan(c.fpr[alias]) && isnan(c.ps1[alias]));
     assert(f64_bits(force_25bit_c(c.fpr[alias]))==f64_bits(c.fpr[alias]));
   }
   cases++;
 }
 // A successful finite write establishes a single even if invalid trapping
 // is enabled; rejecting every VE-enabled path would also be too coarse.
 CPUState c={0};c.fpscr=FPSCR_VE_BIT;c.fpr[1]=1.25;c.fpr[2]=2;
 ppc_fmuls(&c,0,1,2);assert(c.fpr[0]==2.5 && c.ps1[0]==2.5);
 puts("12 invalid scalar/VE/alias cases and finite VE-enabled success pass");
 puts("Unconditional scalar single-result type propagation is unsound for current helper semantics.");
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-single-facts-') as directory:
    cpp=Path(directory)/'test.c';binary=Path(directory)/'test';cpp.write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
                    '-fsanitize=address,undefined','-Wl,-dead_strip','-I',str(core),
                    '-I',str(core.parents[1]/'include'),str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
