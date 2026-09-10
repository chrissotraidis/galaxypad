"""Private complete arithmetic island differential; no product integration."""
from pathlib import Path
import subprocess
import tempfile
import argparse
import hashlib
parser=argparse.ArgumentParser(description=__doc__)
sources=parser.add_mutually_exclusive_group()
sources.add_argument('--diagnostic-source',type=Path)
sources.add_argument('--uninstrumented-source',type=Path)
parser.add_argument('--require-ni-fast',action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
helper=(root/'patches/experiments/cross-island-vector.inc').read_text()
if args.diagnostic_source or args.uninstrumented_source:
    diagnostic=(args.diagnostic_source or args.uninstrumented_source).read_text()
    header=diagnostic.splitlines()[0]
    assert header.startswith('#include "') and header.endswith('/RMGE01.h"')
    assert diagnostic.count(header)==2
    helper=diagnostic.split(header)[1]
    if args.diagnostic_source:
        assert 'static void cross_report(void)' in helper
    else:
        assert all(name not in diagnostic for name in ['cross_report','cross_calls','cross_fast','cross_mode','cross_range','cross_ties'])
        assert helper=='\n#include "cpu_interpreter_private.h"\n#include <arm_neon.h>\n'+(root/'patches/experiments/cross-island-vector.inc').read_text()+'\n// DolRecomp output\n'
    print('diagnostic_source_sha256='+hashlib.sha256(diagnostic.encode()).hexdigest(),flush=True)
helper=helper.replace('const float64x2_t out5=', '++fast_calls; const float64x2_t out5=')
helper=helper.replace('__asm__ volatile("msr fpsr, %0"::"r"(saved_status):"memory");',
                      '++tie_calls; __asm__ volatile("msr fpsr, %0"::"r"(saved_status):"memory");')
helper=helper.replace('if(!cross_island_try(cpu)) cross_island_original(cpu);',r'''
  const CPUState before=*cpu;
  u64 before_flags,after_flags;
  __asm__ volatile("mrs %0, fpsr":"=r"(before_flags));
  if(!cross_island_try(cpu)) {
    __asm__ volatile("mrs %0, fpsr":"=r"(after_flags));
    assert(!memcmp(cpu,&before,sizeof(before)) && before_flags==after_flags);
    cross_island_original(cpu);
  }
''')
program=r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <arm_neon.h>
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
static unsigned fast_calls,tie_calls;
'''+helper+r'''
static u64 rng=802;
static u64 random64(void){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return rng;}
int main(void) {
 u64 saved_mode,saved_status;
 __asm__ volatile("mrs %0, fpcr":"=r"(saved_mode));
 __asm__ volatile("mrs %0, fpsr":"=r"(saved_status));
 unsigned cases=0,fast_by_ni[2]={0,0};
 const u32 edge[]={0,0x80000000,1,0x7fffff,0x7f800000,0xff800000,0x7f800001,0x7fc12345};
 for(unsigned rn=0;rn<4;++rn)for(unsigned ni=0;ni<2;++ni)
 for(unsigned iteration=0;iteration<32768;++iteration) {
  CPUState a={0};
  for(unsigned r=0;r<32;++r) {
   u64 lanes[2];
   for(unsigned lane=0;lane<2;++lane) {
    const u64 random=random64();
    if(iteration<512) lanes[lane]=convert_to_double(edge[(iteration+r+lane)%8]);
    else if(iteration%4==0) lanes[lane]=random;
    else {
     const u32 bits=((u32)random&0x807fffffu)|((97u+(u32)(random>>32)%61u)<<23);
     lanes[lane]=convert_to_double(bits);
    }
   }
   memcpy(&a.fpr[r],&lanes[0],8);memcpy(&a.ps1[r],&lanes[1],8);
   a.gpr[r]=random64();
  }
  if(iteration%257==0) {
   // Exact halfway result: (1 * (1+2^-23)) - 2^-24.
   a.fpr[0]=a.ps1[0]=1.0;a.fpr[1]=a.ps1[1]=1.0;
   a.fpr[2]=a.ps1[2]=0x1p-24;a.fpr[3]=a.ps1[3]=0x1.000002p0;
   a.fpr[6]=a.ps1[6]=2.0;
  } else if(iteration%263==0) {
   for(unsigned k=0;k<5;++k) {
    const unsigned r=(unsigned[]){0,1,2,3,6}[k];
    a.fpr[r]=f64_value((iteration&1)?0x8000000000000000ull:0);
    a.ps1[r]=f64_value((iteration&2)?0x8000000000000000ull:0);
   }
  }
  a.fpscr=((u32)random64()&~(FPSCR_NI_BIT|FPSCR_RN_MASK))|rn|(ni?FPSCR_NI_BIT:0);
  a.pc=0x804b6ccc;a.downcount=12345;CPUState b=a;
  const u64 initial=iteration&0x9f;
  ppc_fpscr_control_updated(&a);
  __asm__ volatile("msr fpsr, %0"::"r"(initial));
  cross_island_original(&a);
  u64 expected,actual;__asm__ volatile("mrs %0, fpsr":"=r"(expected));
  ppc_fpscr_control_updated(&b);
  __asm__ volatile("msr fpsr, %0"::"r"(initial));
  const unsigned fast_before=fast_calls;
  cross_island_vector(&b);
  fast_by_ni[ni]+=fast_calls-fast_before;
  __asm__ volatile("mrs %0, fpsr":"=r"(actual));
  if(memcmp(&a,&b,sizeof(a))||actual!=expected) {
   fprintf(stderr,"Mismatch rn=%u ni=%u iteration=%u flags=%llx/%llx fast=%u ties=%u\n",
           rn,ni,iteration,(unsigned long long)actual,(unsigned long long)expected,fast_calls,tie_calls);
   return 1;
  }
  ++cases;
 }
 __asm__ volatile("msr fpcr, %0"::"r"(saved_mode));
 __asm__ volatile("msr fpsr, %0"::"r"(saved_status));
 assert(fast_calls>10000);
 assert(fast_by_ni[0]>10000);
#ifdef REQUIRE_NI_FAST
 assert(fast_by_ni[1]>10000);
#endif
 assert(tie_calls>0);
 printf("%u whole-island CPU/FPSR cases passed; %u fast paths; %u tie fallbacks\n",cases,fast_calls,tie_calls);
 printf("Fast-path coverage NI0=%u NI1=%u\n",fast_by_ni[0],fast_by_ni[1]);
}
'''
if args.diagnostic_source:
    assert program.count('cross_island_vector(&b);')==1
    program=program.replace('cross_island_vector(&b);','cross_island_vector(&b);cross_report();')
if args.require_ni_fast or not args.diagnostic_source:
    program='#define REQUIRE_NI_FAST 1\n'+program
with tempfile.TemporaryDirectory(prefix='galaxypad-cross-island-') as directory:
    c=Path(directory)/'test.c';binary=Path(directory)/'test'
    c.write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
                    '-fsanitize=address,undefined','-Wl,-dead_strip','-I',str(core),
                    '-I',str(core.parents[1]/'include'),str(c),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
