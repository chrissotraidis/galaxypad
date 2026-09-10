"""General checked multiply: raw bits, rounding, flags and register aliases."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
helper = (root/'patches/experiments/checked-ps-multiply.inc').read_text()
assert helper.count('const float32x2_t left =') == 1
helper = helper.replace('const float32x2_t left =', '++fast_calls; const float32x2_t left =')
program = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <arm_neon.h>
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
static unsigned fast_calls;
''' + helper + r'''
static u64 rng=787;
static u64 random64(void){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return rng;}
int main(void) {
 const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
   0x0010000000000000ull,0x3690000000000000ull,0x380fffffc0000000ull,
   0x3810000000000000ull,0x3ff0000000000000ull,0x3ff0000000000001ull,
   0x47efffffe0000000ull,0x7fefffffffffffffull,0x7ff0000000000000ull,
   0xfff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000001234ull};
 const u8 alias[][3]={{0,1,2},{1,1,2},{2,1,2},{0,1,1},{1,1,1}};
 u64 saved;__asm__ volatile("mrs %0, fpcr":"=r"(saved));
 unsigned cases=0;
 for(unsigned rn=0;rn<4;rn++)for(unsigned ni=0;ni<2;ni++)
 for(unsigned k=0;k<5;k++)for(unsigned i=0;i<16384;i++) {
   CPUState a={0};a.fpscr=((u32)random64()&~(FPSCR_NI_BIT|3u))|rn|(ni?FPSCR_NI_BIT:0);
   for(unsigned r=0;r<3;r++) {
     u64 x,y;
     if(i<256) {x=special[(i+r)%16];y=special[(i/16+r)%16];}
     else if(i%3==0) {x=random64();y=random64();}
     else if(i%3==1) {x=convert_to_double((u32)random64());y=convert_to_double((u32)random64());}
     else {x=((u64)((i+r)%2048)<<52)|(random64()&0x800fffffffffffffull);y=x^1;}
     a.fpr[r]=f64_value(x);a.ps1[r]=f64_value(y);
   }
   CPUState b=a;const u8 d=alias[k][0],ra=alias[k][1],rc=alias[k][2];
   ppc_fpscr_control_updated(&a);feclearexcept(FE_ALL_EXCEPT);
   if(i%7==0)feraiseexcept(FE_DIVBYZERO);
   ppc_ps_mul_op(&a,d,ra,rc);int flags=fetestexcept(FE_ALL_EXCEPT);
   ppc_fpscr_control_updated(&b);feclearexcept(FE_ALL_EXCEPT);
   if(i%7==0)feraiseexcept(FE_DIVBYZERO);
   checked_ps_multiply(&b,d,ra,rc);
   if(memcmp(&a,&b,sizeof a)||flags!=fetestexcept(FE_ALL_EXCEPT)) {
     fprintf(stderr,"Mismatch rn=%u ni=%u alias=%u case=%u\n",rn,ni,k,i);return 1;
   }
   cases++;
 }
 __asm__ volatile("msr fpcr, %0"::"r"(saved));
 assert(fast_calls>10000);
 printf("%u checked-multiply CPU/host-flag comparisons pass; %u vector-path calls; five alias patterns\n",cases,fast_calls);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-checked-multiply-') as directory:
    c = Path(directory)/'test.c'
    binary = Path(directory)/'test'
    c.write_text(program)
    subprocess.run(['clang', '-O2', '-std=c11', '-ffp-contract=off', '-fno-fast-math',
                    '-fsanitize=address,undefined', '-Wl,-dead_strip', '-I', str(core),
                    '-I', str(core.parents[1]/'include'), str(c), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
