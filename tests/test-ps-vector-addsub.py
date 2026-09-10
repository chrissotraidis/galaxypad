"""Isolated vector arithmetic oracle; never changes the product module."""
from pathlib import Path
import argparse
import platform
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--benchmark',action='store_true',help='Isolated ABBA helper timings, not game performance')
args=parser.parse_args()
if platform.machine() != 'arm64':
    raise SystemExit('This isolated NEON experiment requires ARM64')
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
candidate = (root/'patches/experiments/ps-vector-addsub.inc').read_text()
program = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <arm_neon.h>
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
#include <time.h>
CANDIDATE
static u64 next(u64* s) { *s ^= *s<<13; *s ^= *s>>7; *s ^= *s<<17; return *s; }
#ifdef BENCH
__attribute__((noinline)) static void control(CPUState* c,unsigned op) {
  if(op) ppc_ps_sub_op(c,2,0,1); else ppc_ps_add_op(c,2,0,1);
}
__attribute__((noinline)) static void experiment(CPUState* c,unsigned op) {
  vector_addsub(c,2,0,1,op);
}
static double now(void) { struct timespec t; assert(!clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t)); return t.tv_sec+t.tv_nsec*1e-9; }
int main(void) {
  for(unsigned payload=0;payload<3;payload++) {
    CPUState initial={0}; initial.msr=PPC_MSR_FP;
    initial.fpr[0]=payload==0?1.25:payload==1?1.234567890123:0x1p-140;
    initial.fpr[1]=payload==0?-0.5:payload==1?0.987654321012:0x1p-142;
    initial.ps1[0]=-initial.fpr[1]; initial.ps1[1]=initial.fpr[0];
    for(unsigned run=0;run<4;run++) {
      unsigned candidate=run==1||run==2; CPUState c=initial;
      double begin=now();
      for(unsigned i=0;i<1000000;i++) {
        if(candidate) experiment(&c,i&1); else control(&c,i&1);
        __asm__ volatile(""::"r"(&c):"memory");
      }
      printf("payload=%u candidate=%u ns_per_call=%.3f\n",payload,candidate,(now()-begin)*1000);
    }
  }
}
#else
int main(void) {
  const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
    0x0010000000000000ull,0x380fffffffffffffull,0x3810000000000000ull,
    0x7fefffffffffffffull,0x7ff0000000000000ull,0xfff0000000000000ull,
    0x7ff0000000000001ull,0x7ff8000000000123ull,0xfff8000000000123ull};
  u64 seed=0x428012937ull, saved;
  __asm__ volatile("mrs %0, fpcr":"=r"(saved));
  unsigned count=0;
  for(unsigned rn=0;rn<4;rn++) for(unsigned ni=0;ni<2;ni++)
  for(unsigned op=0;op<2;op++) for(unsigned i=0;i<40000;i++) {
    CPUState a={0};
    a.fpscr=((u32)next(&seed)&~(FPSCR_RN_MASK|FPSCR_NI_BIT))|rn|(ni?FPSCR_NI_BIT:0);
    ppc_fpscr_control_updated(&a);
    unsigned digits=i;
    for(unsigned r=0;r<3;r++) {
      a.fpr[r]=f64_value(i<28561?special[digits%13]:next(&seed)); digits/=13;
      a.ps1[r]=f64_value(i<28561?special[digits%13]:next(&seed)); digits/=13;
    }
    CPUState b=a;
    assert(!feclearexcept(FE_ALL_EXCEPT));
    if(op) ppc_ps_sub_op(&a,i%3,0,1); else ppc_ps_add_op(&a,i%3,0,1);
    int flags=fetestexcept(FE_ALL_EXCEPT);
    assert(!feclearexcept(FE_ALL_EXCEPT));
    vector_addsub(&b,i%3,0,1,op);
    if(memcmp(&a,&b,sizeof a)||flags!=fetestexcept(FE_ALL_EXCEPT)) {
      fprintf(stderr,"mismatch rn=%u ni=%u op=%u case=%u flags=%x/%x\n",
        rn,ni,op,i,flags,fetestexcept(FE_ALL_EXCEPT)); return 1;
    }
    count++;
  }
  __asm__ volatile("msr fpcr, %0"::"r"(saved));
  printf("%u cases: full CPUState and host flags agree; no runtime speed claim\n",count);
}
#endif
'''.replace('CANDIDATE',candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-vector-oracle-') as directory:
    temp=Path(directory)
    (temp/'probe.c').write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
                    *(['-DBENCH'] if args.benchmark else ['-fsanitize=undefined']),
                    '-ffunction-sections','-fdata-sections',
                    '-Wl,-dead_strip','-I',str(core),'-I',str(core.parent.parent/'include'),
                    str(temp/'probe.c'),'-o',str(temp/'probe')],check=True)
    subprocess.run([str(temp/'probe')],check=True)
