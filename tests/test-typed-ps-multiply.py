"""Precision-qualified paired multiply oracle; not a product helper or speed claim."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
program=r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <arm_neon.h>
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
static unsigned fast_calls;
// Precondition: both source lanes are exact widened binary32 values. This
// precondition must come from guarded dataflow, not merely the opcode name.
static void typed_mul(CPUState* cpu,u8 d,u8 a,u8 c) {
 const f64 a0=cpu->fpr[a],a1=cpu->ps1[a],c0=cpu->fpr[c],c1=cpu->ps1[c];
 if((cpu->fpscr&FPSCR_NI_BIT)||!isfinite(a0)||!isfinite(a1)||!isfinite(c0)||!isfinite(c1)) {
   ppc_ps_mul_op(cpu,d,a,c);return;
 }
 const float32x2_t left={(f32)a0,(f32)a1},right={(f32)c0,(f32)c1};
 const float32x2_t result=vmul_f32(left,right);
 const f32 ps0=vget_lane_f32(result,0),ps1=vget_lane_f32(result,1);
 ps_write_both(cpu,d,ps0,ps1);set_fprf(cpu,classify_f32(ps0));fast_calls++;
}
static u32 random_word(u32* s){*s^=*s<<13;*s^=*s>>17;*s^=*s<<5;return *s;}
int main(void){
 const u32 special[]={0,0x80000000,1,0x007fffff,0x00800000,0x3f800000,
   0x3f000000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc00001,0x7f800001};
 const u8 alias[][3]={{0,1,2},{1,1,2},{2,1,2},{1,1,1}};
 u32 seed=779;unsigned cases=0;u64 saved;
 __asm__ volatile("mrs %0, fpcr":"=r"(saved));
 for(unsigned rn=0;rn<4;rn++)for(unsigned ni=0;ni<2;ni++)
 for(unsigned index=0;index<4;index++)for(unsigned i=0;i<20000;i++){
   CPUState a={0};a.fpscr=(random_word(&seed)&~(FPSCR_NI_BIT|3u))|rn|(ni?FPSCR_NI_BIT:0);
   // Prepare input values with host flush disabled; source payloads must not
   // depend on the previous test's host mode or flags.
   CPUState prepare={0};ppc_fpscr_control_updated(&prepare);
   for(unsigned r=0;r<3;r++){
     u32 x=i<2197?special[(i+r)%13]:random_word(&seed);
     u32 y=i<2197?special[(i/13+r*3)%13]:random_word(&seed);
     a.fpr[r]=(f64)f32_value(x);a.ps1[r]=(f64)f32_value(y);
   }
   CPUState b=a;ppc_fpscr_control_updated(&a);feclearexcept(FE_ALL_EXCEPT);
   ppc_ps_mul_op(&a,alias[index][0],alias[index][1],alias[index][2]);int flags=fetestexcept(FE_ALL_EXCEPT);
   ppc_fpscr_control_updated(&b);feclearexcept(FE_ALL_EXCEPT);
   typed_mul(&b,alias[index][0],alias[index][1],alias[index][2]);
   if(memcmp(&a,&b,sizeof a)||flags!=fetestexcept(FE_ALL_EXCEPT)){
     fprintf(stderr,"typed multiply mismatch rn=%u ni=%u alias=%u case=%u flags=%x/%x\n",rn,ni,index,i,flags,fetestexcept(FE_ALL_EXCEPT));return 1;
   }
   cases++;
 }
 __asm__ volatile("msr fpcr, %0"::"r"(saved));
 assert(fast_calls>100000);
 printf("%u precision-qualified CPU/host-flag cases pass; %u vector-path calls\n",cases,fast_calls);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-typed-multiply-') as directory:
    cpp=Path(directory)/'test.c';binary=Path(directory)/'test';cpp.write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
                    '-fsanitize=address,undefined','-Wl,-dead_strip','-I',str(core),
                    '-I',str(core.parents[1]/'include'),str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
