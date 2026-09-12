#!/usr/bin/env python3
"""Stage exact shared multiplier rounding for ps_madds0/1; never compile or select.

The original arithmetic helper stays byte-identical. A prepared-c copy retains
original c for NaN/exception semantics and accepts one exact rounded multiplier
shared by both lanes. It does not assume float provenance or skip rounding.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
SOURCE=CORE/'cpu_interpreter_float.c'
SHA='554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
HELPER='galaxypad_ni_madd_msub_prepared'


def function(text,signature):
    start=text.index(signature);i=text.index('{',start)+1;depth=1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]+'\n'


def make(source):
    original=function(source,'FPRes ni_madd_msub(')
    signature='FPRes ni_madd_msub(CPUState* cpu, f64 a, f64 c, f64 b, bool sub, bool single)'
    assert original.startswith(signature)
    prepared=original.replace(signature,'static FPRes '+HELPER+'(CPUState* cpu, f64 a, f64 c, f64 b,\n                                                  bool sub, bool single, f64 c_round)',1)
    assert prepared.count('        f64 c_round = force_25bit_c(c);\n')==1
    prepared=prepared.replace('        f64 c_round = force_25bit_c(c);\n','',1)
    changed={}
    for lane,array in [(0,'fpr'),(1,'ps1')]:
        old=function(source,f'void ppc_ps_madds{lane}(')
        shared=f'cpu->{array}[c]'
        assert old.count(shared)==2
        new=old.replace('{\n',f'{{\n    const f64 multiplier = {shared};\n    const f64 rounded_multiplier = force_25bit_c(multiplier);\n',1)
        # Substitute only the two operation arguments, preserving initialization.
        start=new.index('    f32 ps0')
        tail=new[start:].replace(shared,'multiplier').replace('ni_madd_msub(',HELPER+'(')
        assert tail.count('false, true).value')==2
        new=new[:start]+tail.replace('false, true).value','false, true, rounded_multiplier).value')
        changed[old]=new
    candidate=source
    for old,new in changed.items():candidate=candidate.replace(old,new,1)
    anchor='void ppc_ps_madds0('
    pos=candidate.index(anchor);candidate=candidate[:pos]+prepared+'\n'+candidate[pos:]
    restored=candidate.replace(prepared+'\n','',1)
    for old,new in changed.items():restored=restored.replace(new,old,1)
    assert restored==source
    assert function(candidate,'FPRes ni_madd_msub(')==original
    test_helpers=prepared+'\n'+'\n'.join(new.replace('void ppc_ps_madds','void candidate_ps_madds',1) for new in changed.values())
    return candidate,test_helpers


DRIVER=r'''
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
#include <time.h>
PREPARED_HELPERS
static u64 random_bits(u64* s){*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;return *s;}
typedef void (*Operation)(CPUState*,u8,u8,u8,u8);
static Operation volatile operations[]={ppc_ps_madds0,candidate_ps_madds0,ppc_ps_madds1,candidate_ps_madds1};
int main(int argc,char** argv){
 (void)argv;
 const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
 const u64 edges[]={0,0x8000000000000000ull,1,0x8000000000000001ull,
  0x000fffffffffffffull,0x0010000000000000ull,0x380fffffffffffffull,
  0x3810000000000000ull,0x3fefffffffffffffull,0x3ff0000000000000ull,
  0x3ff0000008000000ull,0x3ff0000010000000ull,0x3ff0000018000000ull,
  0x7fefffffffffffffull,0x7ff0000000000000ull,0xfff0000000000000ull,
  0x7ff0000000000001ull,0x7ff8000000000123ull,0xfff0000000000001ull,0xfff8000000000123ull};
 const u8 aliases[][4]={{3,0,1,2},{0,0,1,2},{1,0,1,2},{2,0,1,2},{0,0,0,0},{1,0,0,1}};
 u64 seed=0x5920260912ull;unsigned comparisons=0;
 for(unsigned lane=0;lane<2;lane++)for(unsigned mode=0;mode<4;mode++)for(unsigned ni=0;ni<2;ni++){
  assert(fesetround(modes[mode])==0);
  for(unsigned i=0;i<10000;i++)for(unsigned alias=0;alias<6;alias++){
   CPUState a={0};a.fpscr=(u32)random_bits(&seed);
   a.fpscr=(a.fpscr&~FPSCR_NI_BIT)|(ni?FPSCR_NI_BIT:0);
   // Include all 20^3 edge triples in each operand role, then random raw bits.
   for(unsigned r=0;r<4;r++){
    u64 lo=i<8000?edges[(i/(r==0?1:r==1?20:400)+r)%20]:random_bits(&seed);
    u64 hi=i<8000?edges[(i/(r==0?400:r==1?20:1)+r+3)%20]:random_bits(&seed);
    a.fpr[r]=f64_value(lo);a.ps1[r]=f64_value(hi);
   }
   CPUState b=a;const u8* regs=aliases[alias];
   assert(feclearexcept(FE_ALL_EXCEPT)==0);
   operations[2*lane](&a,regs[0],regs[1],regs[2],regs[3]);
   int flags=fetestexcept(FE_ALL_EXCEPT);
   assert(feclearexcept(FE_ALL_EXCEPT)==0);
   operations[2*lane+1](&b,regs[0],regs[1],regs[2],regs[3]);
   assert(flags==fetestexcept(FE_ALL_EXCEPT));
   assert(!memcmp(&a,&b,sizeof a));++comparisons;
  }
 }
 // Explicit double-rounding ties: (1 + 2^-24) +/- 2^-53. The FMA
 // double result lies exactly on the single midpoint; residual correction matters.
 for(unsigned lane=0;lane<2;lane++)for(unsigned mode=0;mode<4;mode++)for(unsigned sign=0;sign<2;sign++){
  assert(fesetround(modes[mode])==0);CPUState a={0};
  a.fpr[0]=1.0;a.ps1[0]=-1.0;
  a.fpr[1]=a.ps1[1]=f64_value(0x3ff0000010000000ull);
  a.fpr[2]=a.ps1[2]=f64_value(0x3ca0000000000000ull|((u64)sign<<63));
  CPUState b=a;assert(feclearexcept(FE_ALL_EXCEPT)==0);
  operations[2*lane](&a,3,0,1,2);int flags=fetestexcept(FE_ALL_EXCEPT);
  assert(feclearexcept(FE_ALL_EXCEPT)==0);operations[2*lane+1](&b,3,0,1,2);
  assert(flags==fetestexcept(FE_ALL_EXCEPT));assert(!memcmp(&a,&b,sizeof a));++comparisons;
 }
 printf("PASS %u complete CPUState/host FP status comparisons: four rounding modes, NI, aliases, NaN payloads, subnormals, tie edges\n",comparisons);
 if(argc<2)return 0;
 assert(fesetround(FE_TONEAREST)==0);
 puts("lane,round,variant,cpu_ns_per_operation,checksum");
 for(unsigned lane=0;lane<2;lane++)for(unsigned round=0;round<6;round++)for(unsigned order=0;order<2;order++){
  unsigned variant=order^(round&1);Operation op=operations[2*lane+variant];CPUState c={0};
  c.fpr[0]=0.875;c.ps1[0]=-0.4375;c.fpr[1]=0.8125;c.ps1[1]=-0.625;
  c.fpr[2]=0.1875;c.ps1[2]=-0.3125;u64 checksum=0;
  const unsigned iterations=5000000;clock_t start=clock();
  for(unsigned i=0;i<iterations;i++){
   // Change live operands without destination feedback or dead-code elision.
   c.fpr[1]=f64_value(0x3fe0000000000000ull+((u64)(i&1023)<<31));
   c.ps1[1]=f64_value(0xbfe0000000000000ull+((u64)(i&1023)<<31));
   op(&c,3,0,1,2);checksum+=f64_bits(c.fpr[3])^f64_bits(c.ps1[3])^c.fpscr;
  }
  double ns=(double)(clock()-start)*1e9/CLOCKS_PER_SEC/iterations;
  printf("%u,%u,%u,%.6f,%llu\n",lane,round,variant,ns,(unsigned long long)checksum);
 }
}
'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args();out=args.output.resolve()
    if out.exists():p.error('Output exists; preserve prior evidence')
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:p.error('Pinned floating-point source changed')
    source=raw.decode();candidate,helpers=make(source);out.mkdir(parents=True)
    (out/'cpu_interpreter_float.c').write_text(candidate)
    (out/'shared-rounding.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),candidate.splitlines(True),fromfile='a/cpu_interpreter_float.c',tofile='b/cpu_interpreter_float.c')))
    # The test includes the original source by absolute path, then adds candidates.
    driver=DRIVER.replace('#include "cpu_interpreter_float.c"','#include "'+str(SOURCE)+'"').replace('PREPARED_HELPERS',helpers)
    (out/'test-shared-rounding.c').write_text(driver)
    flags=['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math','-frounding-math',
           '-ffunction-sections','-fdata-sections','-Wl,-dead_strip','-I',str(CORE),'-I',str(CORE.parent.parent/'include')]
    manifest={'status':'prepared; not built or tested','canonical_sha256':SHA,'candidate_sha256':hashlib.sha256(candidate.encode()).hexdigest(),
              'parity_command':flags+['-fsanitize=address,undefined',str(out/'test-shared-rounding.c'),'-o',str(out/'parity')],
              'cost_command':flags+[str(out/'test-shared-rounding.c'),'-o',str(out/'cost')],
              'profile_caveat':'Verify unchanged wrapper function hashes/entry counts and final module-policy object before interpreting cost. Synthetic cost is not FPS.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(out/'manifest.json')

if __name__=='__main__':main()
