"""Offline C/ARM64 IR comparison using the staged standalone CPU interface.

No game data, runtime module, or reference source is modified. Requires R433's
explicit staged probe build. This initial corpus is not all-opcode coverage.
"""
from pathlib import Path
import argparse
import os
import shlex
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--probe',type=Path,default=root/'generated/llvm-arm64-probe-r433')
parser.add_argument('--runtime',action='store_true',help='Use real GXRuntime CPU structure and helpers instead of standalone CPU')
parser.add_argument('--fp-boundaries',action='store_true',help='Exercise all rounding/NI modes, FP unavailable exits and special operand bits')
parser.add_argument('--exception-policy-oracle',action='store_true',help='Separate oracle: verify C block-precharge and IR faulting-instruction charge; NOT C/IR equivalence')
parser.add_argument('--memory-boundaries',action='store_true',help='MEM1/MEM2 mirrors, edges, callback remapping and journal/reservation checks')
args=parser.parse_args();probe=args.probe.resolve();build=probe/'build';src=probe/'staged/src'
if args.memory_boundaries and (not args.runtime or args.fp_boundaries or args.exception_policy_oracle):
    parser.error('--memory-boundaries requires --runtime and cannot combine with FP modes')
if args.exception_policy_oracle:
    if not args.runtime:
        parser.error('--exception-policy-oracle requires --runtime')
    args.fp_boundaries=True
blocks=[
 [0x3863ffff,0x7c841a14,0x2c03000a,0x4e800020],
 [0x2c03000a,0x41800008,0x38840001,0x4e800020],
 [0x80850000,0x90850004,0x38a50008,0x4e800020],
 [0x1022182a,0x10853028,0x4e800020],
]
driver=r'''
extern "C" {
#include "backend/emitter.h"
}
#include "backend/llvm/llvm_backend.h"
#include "ir/dolir_builder.h"
#include <cassert>
int main(int argc,char** argv) {
  assert(argc==4); FILE* c=fopen(argv[1],"w"); assert(c);
  emit_header_for_cpu(c,DOLRECOMP_CPU_BROADWAY);
  emit_set_chunk_table(nullptr,0);
  DolIRModule module; dolir_module_init(&module);
  BLOCKS
  emit_footer(c); assert(!fclose(c));
  DolLLVMOptions options{};options.optimization_level=2;options.verify=1;
  options.emit_ir=1;options.ir_path=argv[3];
  assert(dolllvm_emit_object(&module,argv[2],&options,stderr));
  dolir_module_free(&module);
}
'''
emits=[]
for index,words in enumerate(blocks):
    address=0x80001000+index*0x100
    emits.append('{ const u32 words[]={'+','.join(hex(w)+'u' for w in words)+'};'
      f'PPCInst insts[{len(words)}]; for(unsigned i=0;i<{len(words)};i++) insts[i]=ppc_decode(words[i],{hex(address)}u+i*4);'
      f'assert(emit_function(c,insts,{len(words)},{hex(address)}u));'
      f'assert(dolir_build_chunk(&module,insts,{len(words)},{hex(address)}u)); }}')
driver=driver.replace('BLOCKS','\n'.join(emits))
harness=r'''
#pragma STDC FENV_ACCESS ON
#include "cpu/cpu.h"
#include <fenv.h>
#include <stdio.h>
#include <stddef.h>
#include <string.h>
DECLARATIONS
static unsigned memory_mode,event_count;
static u64 events[32];
static u8* remapped_ram;
static void event(u64 a,u64 b,u64 c) {
  if(event_count+3>32) { fprintf(stderr,"event overflow\n"); __builtin_trap(); }
  events[event_count++]=a;events[event_count++]=b;events[event_count++]=c;
}
static u64 external_read(CPUState* cpu,u32 address,u8 width) {
  event(address,width,1);
  if(memory_mode==6) {
    cpu->ram=remapped_ram;cpu->gpr[5]=0x80000000u;cpu->gpr[6]^=0x9876;
  }
  return 0x12345678;
}
static void external_write(CPUState* cpu,u32 address,u64 value,u8 width) {
  event(address,width,value);cpu->gpr[7]^=0x1234;
}
static void journal(u32 offset,u32 width,void* user) {
  CPUState* cpu=(CPUState*)user;
  event(offset,width,2|((u64)cpu->reserve_valid<<8));
  if(memory_mode==7) cpu->ram=remapped_ram;
  if(memory_mode==10) { cpu->reserve_valid=true;cpu->reserve_addr=0x80000060; }
}
static u64 next(u64* s) { *s^=*s<<13;*s^=*s>>7;*s^=*s<<17;return *s; }
int main(void) {
  void (*c[])(CPUState*)={C_FUNCTIONS};
  void (*ir[])(CPUState*)={IR_FUNCTIONS};
  unsigned lengths[]={LENGTHS};
  unsigned char ram[384],initial[384],expected[384];
  u64 seed=0x434123765ull;unsigned cases=0,failures=0,cycle_only=0;
  const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
    0x0010000000000000ull,0x380fffffffffffffull,0x3810000000000000ull,
    0x7fefffffffffffffull,0x7ff0000000000000ull,0xfff0000000000000ull,
    0x7ff0000000000001ull,0x7ff8000000000123ull,0xfff8000000000123ull};
  for(unsigned mode=0;mode<MODE_COUNT;mode++)
  for(unsigned block=0;block<4;block++) for(unsigned entry=0;entry<lengths[block];entry++)
  for(unsigned sample=0;sample<2000;sample++) {
    if(POLICY_ORACLE && (!(mode&8)||block!=3||entry>=2)) continue;
    if(MEM_BOUNDARIES && block!=2) continue;
    CPUState a={0};
    for(unsigned r=0;r<32;r++) {
      a.gpr[r]=(u32)next(&seed);
      a.fpr[r]=(double)(int)(next(&seed)%20001)-10000;
      a.ps1[r]=(double)(int)(next(&seed)%20001)/32.0-100;
    }
    a.cr=(u32)next(&seed);a.xer=(u32)next(&seed);a.msr=0x2000;
    if(FP_BOUNDARIES) {
      a.msr=(mode&8)?0:0x2000;
      a.fpscr=(mode&3)|((mode&4)?4:0);
      for(unsigned r=0;r<32;r++) {
        u64 lo=sample<169?special[(sample+r)%13]:next(&seed);
        u64 hi=sample<169?special[(sample/13+r)%13]:next(&seed);
        memcpy(&a.fpr[r],&lo,sizeof lo);memcpy(&a.ps1[r],&hi,sizeof hi);
      }
    }
    a.pc=0x80001000u+block*0x100+entry*4;a.lr=0x81234564;
    a.ram=ram;a.ram_size=128;a.gpr[5]=0x80000000;
    if(MEM_BOUNDARIES) {
      static const u32 addresses[]={0x80000000,0xc0000000,0x90000000,0xd0000000,
                                   0x8000007c,0x9000007c,0xe0000000,0x80000000,
                                   0xc0000000,0xd0000000,0x80000000};
      memory_mode=mode;remapped_ram=ram+256;
      a.exram=ram+128;a.exram_size=128;a.gpr[5]=addresses[mode];
      a.external_read=external_read;a.external_write=external_write;
      a.reserve_valid=true;a.reserve_addr=a.gpr[5]+4;
      if(mode==8||mode==9) a.reserve_addr^=0x40000000u;
    }
    a.downcount=10000;
    for(unsigned i=0;i<sizeof ram;i++) initial[i]=(unsigned char)next(&seed);
    CPUState b=a;
    CPUState before=a;
    u64 saved_events[32]={0};unsigned saved_count=0;
    event_count=0;memset(events,0,sizeof events);
    if(MEM_BOUNDARIES) { g_mem_write_journal=journal;g_mem_write_journal_user=&a; }
    if(FP_BOUNDARIES) ppc_fpscr_control_updated(&a);
    memcpy(ram,initial,sizeof ram);feclearexcept(FE_ALL_EXCEPT);c[block](&a);
    int flags=fetestexcept(FE_ALL_EXCEPT);memcpy(expected,ram,sizeof ram);
    saved_count=event_count;memcpy(saved_events,events,sizeof events);
    event_count=0;memset(events,0,sizeof events);
    if(MEM_BOUNDARIES) g_mem_write_journal_user=&b;
    if(FP_BOUNDARIES) ppc_fpscr_control_updated(&b);
    memcpy(ram,initial,sizeof ram);feclearexcept(FE_ALL_EXCEPT);ir[block](&b);
    if(POLICY_ORACLE) {
      int ir_flags=fetestexcept(FE_ALL_EXCEPT);
      CPUState want_ir=before;
      ppc_fpscr_control_updated(&want_ir);
      feclearexcept(FE_ALL_EXCEPT);
      int available=ppc_fp_available(&want_ir,before.pc);
      int expected_flags=fetestexcept(FE_ALL_EXCEPT);
      /* Paired add/sub and blr each cost one in both pinned instruction tables.
         No following instruction executes once the FP-unavailable guard exits. */
      want_ir.downcount-=1;
      CPUState want_c=want_ir;
      want_c.downcount-=lengths[block]-entry-1;
      if(available||want_ir.pc!=0x800||memcmp(&a,&want_c,sizeof a)||
         memcmp(&b,&want_ir,sizeof b)||memcmp(expected,initial,sizeof ram)||
         memcmp(ram,initial,sizeof ram)||flags!=expected_flags||ir_flags!=expected_flags) {
        fprintf(stderr,"exception policy oracle failed mode=%u entry=%u sample=%u\n",mode,entry,sample);
        return 1;
      }
      cases++;
      continue;
    }
    int event_difference=saved_count!=event_count||memcmp(saved_events,events,sizeof events);
    if(memcmp(&a,&b,sizeof a)||memcmp(expected,ram,sizeof ram)||flags!=fetestexcept(FE_ALL_EXCEPT)||event_difference) {
      failures++;
      int other=memcmp(expected,ram,sizeof ram)||flags!=fetestexcept(FE_ALL_EXCEPT)||event_difference;
      for(size_t k=0;k<sizeof a;k++)
        if((k<offsetof(CPUState,downcount)||k>=offsetof(CPUState,downcount)+sizeof a.downcount)
           &&((unsigned char*)&a)[k]!=((unsigned char*)&b)[k]) other=1;
      if(!other) cycle_only++;
      size_t offset=0;while(offset<sizeof a&&((unsigned char*)&a)[offset]==((unsigned char*)&b)[offset])offset++;
      if(sample==0) fprintf(stderr,"mismatch mode=%u block=%u entry=%u sample=%u byte=%zu Cpc=%x IRpc=%x Ccycles=%lld IRcycles=%lld flags=%x/%x memory=%d\n",
        mode,block,entry,sample,offset,a.pc,b.pc,(long long)a.downcount,(long long)b.downcount,flags,fetestexcept(FE_ALL_EXCEPT),memcmp(expected,ram,sizeof ram));
      if(sample==0 && MEM_BOUNDARIES) fprintf(stderr,"reservation=%u/%u gpr5=%x/%x gpr6=%x/%x events=%u/%u event_difference=%d\n",
        a.reserve_valid,b.reserve_valid,a.gpr[5],b.gpr[5],a.gpr[6],b.gpr[6],saved_count,event_count,event_difference);
    }
    cases++;
  }
  if(POLICY_ORACLE) printf("%u exception policy cases pass separate full-state/RAM/host-flag expectations: C suffix charge, IR single instruction; NOT equivalence or game acceptance\n",cases);
  else printf("%u C/IR cases: %u failures (%u downcount-only); full CPUState, RAM, callback events and host flags; standalone interface only\n",cases,failures,cycle_only);
  return failures?1:0;
}
'''
names=[f'func_{0x80001000+i*0x100:08X}' for i in range(len(blocks))]
harness=harness.replace('DECLARATIONS','\n'.join(f'void {prefix}{n}(CPUState*);' for n in names for prefix in ('','c_')))
harness=harness.replace('C_FUNCTIONS',','.join('c_'+n for n in names)).replace('IR_FUNCTIONS',','.join(names))
harness=harness.replace('LENGTHS',','.join(str(len(b)) for b in blocks))
harness=harness.replace('MODE_COUNT','11' if args.memory_boundaries else '16' if args.fp_boundaries else '1').replace('FP_BOUNDARIES','1' if args.fp_boundaries else '0')
harness=harness.replace('MEM_BOUNDARIES','1' if args.memory_boundaries else '0')
harness=harness.replace('POLICY_ORACLE','1' if args.exception_policy_oracle else '0')
runtime=root/'ref/ModernGekko/vendor/dolphin/GXRuntime'
if args.runtime:
    harness=harness.replace('#include "cpu/cpu.h"','#include "core/cpu.h"')
    harness=harness.replace('standalone interface only','GXRuntime CPU interface; not a chassis/game acceptance test')
with tempfile.TemporaryDirectory(prefix='galaxypad-c-ir-') as directory:
    temp=Path(directory);(temp/'driver.cpp').write_text(driver);(temp/'harness.c').write_text(harness)
    llvm=Path('/opt/homebrew/opt/llvm@20')
    libs=shlex.split(subprocess.check_output([str(llvm/'bin/llvm-config'),'--link-shared','--ldflags','--libs','--system-libs'],text=True))
    subprocess.run(['clang++','-std=c++17','-I'+str(src),str(temp/'driver.cpp'),
      *[str(build/('lib'+lib+'.a')) for lib in ('dr_backend','dr_llvm','dr_ir','dr_frontend')],
      *libs,'-lz','-Wl,-rpath,'+str(llvm/'lib'),'-o',str(temp/'emit')],check=True)
    env=os.environ.copy();env['GALAXYPAD_LLVM_ARM64_PROBE']='1'
    subprocess.run([str(temp/'emit'),str(temp/'generated.c'),str(temp/'ir.o'),str(temp/'ir.ll')],env=env,check=True)
    flags=['-O2','-std=c11','-ffp-contract=off','-fno-fast-math','-I'+str(src)]
    if args.runtime:
        flags+=['-DDOLRECOMP_CPU_HEADER="core/cpu.h"','-I'+str(runtime/'include'),
                '-I'+str(runtime/'src/core'),'-ffunction-sections','-fdata-sections']
    subprocess.run(['clang',*flags,*['-D'+n+'=c_'+n for n in names],'-c',str(temp/'generated.c'),'-o',str(temp/'c.o')],check=True)
    helpers=([str(runtime/'src/core'/name) for name in ('cpu.c','cpu_interpreter_float.c','cpu_exception.c')]+['-Wl,-dead_strip']
             if args.runtime else [str(build/'libdr_cpu.a')])
    subprocess.run(['clang',*flags,str(temp/'harness.c'),str(temp/'c.o'),str(temp/'ir.o'),*helpers,'-o',str(temp/'compare')],check=True)
    subprocess.run([str(temp/'compare')],check=True)
