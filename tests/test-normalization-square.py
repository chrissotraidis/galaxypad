"""Stress the exact R785 input guard and arithmetic against the real helper."""
import ast
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
tree = ast.parse((root/'tests/probe-transform-inline.py').read_text())
matches = [node.value.value for node in ast.walk(tree)
           if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
           and isinstance(node.value.value, str)
           and 'static inline void normalize_square(' in node.value.value]
assert len(matches) == 1
helper = matches[0]
assert helper.count('const float32x2_t v=') == 1
helper = helper.replace('const float32x2_t v=', '++fast_calls; const float32x2_t v=')
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
program = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <arm_neon.h>
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
static unsigned fast_calls;
''' + helper + r'''
static u64 rng=786;
static u64 random64(void){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return rng;}
int main(void) {
 const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
   0x0010000000000000ull,0x3690000000000000ull,0x380fffffc0000000ull,
   0x3810000000000000ull,0x3ff0000000000000ull,0x3ff0000000000001ull,
   0x47efffffe0000000ull,0x7fefffffffffffffull,0x7ff0000000000000ull,
   0xfff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000001234ull};
 u64 saved;__asm__ volatile("mrs %0, fpcr":"=r"(saved));
 unsigned cases=0;
 for(unsigned rn=0;rn<4;rn++)for(unsigned ni=0;ni<2;ni++)
 for(unsigned i=0;i<32768;i++) {
   CPUState a={0};a.fpscr=((u32)random64()&~(FPSCR_NI_BIT|3u))|rn|(ni?FPSCR_NI_BIT:0);
   u64 x,y;
   if(i<256) {x=special[i%16];y=special[i/16];}
   else if(i%3==0) {x=random64();y=random64();}
   else if(i%3==1) {x=convert_to_double((u32)random64());y=convert_to_double((u32)random64());}
   else {x=((u64)(i%2048)<<52)|(random64()&0x800fffffffffffffull);y=x^1;}
   a.fpr[2]=f64_value(x);a.ps1[2]=f64_value(y);
   a.fpr[5]=f64_value(random64());a.ps1[5]=f64_value(random64());
   CPUState b=a;
   ppc_fpscr_control_updated(&a);feclearexcept(FE_ALL_EXCEPT);
   if(i%7==0)feraiseexcept(FE_DIVBYZERO);
   ppc_ps_mul_op(&a,5,2,2);int flags=fetestexcept(FE_ALL_EXCEPT);
   ppc_fpscr_control_updated(&b);feclearexcept(FE_ALL_EXCEPT);
   if(i%7==0)feraiseexcept(FE_DIVBYZERO);
   normalize_square(&b);
   if(memcmp(&a,&b,sizeof a)||flags!=fetestexcept(FE_ALL_EXCEPT)) {
     fprintf(stderr,"Mismatch rn=%u ni=%u case=%u bits=%llx/%llx\n",rn,ni,i,
             (unsigned long long)x,(unsigned long long)y);return 1;
   }
   cases++;
 }
 __asm__ volatile("msr fpcr, %0"::"r"(saved));
 assert(fast_calls>10000);
 printf("%u checked-square CPU/host-flag comparisons pass; %u vector-path calls\n",cases,fast_calls);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-square-guard-') as directory:
    c = Path(directory)/'test.c'
    binary = Path(directory)/'test'
    c.write_text(program)
    subprocess.run(['clang', '-O2', '-std=c11', '-ffp-contract=off', '-fno-fast-math',
                    '-fsanitize=address,undefined', '-Wl,-dead_strip', '-I', str(core),
                    '-I', str(core.parents[1]/'include'), str(c), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
