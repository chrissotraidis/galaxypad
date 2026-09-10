"""Exact emitted first-pass oracle: read-ahead, journals and resumed state."""
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from local_thp_columns import candidate_source,transform
from psq_scale import reference_source
source=(root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
try:
    candidate_source(source+'\n')
except ValueError:
    pass
else:
    raise AssertionError('Unpinned candidate source accepted')
assert hashlib.sha256(source.encode()).hexdigest()=='98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
changed=transform(source)
outer='void func_804520A0(CPUState* ctx) {'
assert changed.split(outer,1)[1]==source.split(outer,1)[1]
second='static __attribute__((noinline, flatten)) bool thp_kernel_1('
assert changed.split(second,1)[1]==source.split(second,1)[1]
assert changed.count('if(galaxy_try_local_columns(ctx,&completed))')==1
body='\nlabel_80452750:\n'+source.split('\nlabel_80452750:\n',1)[1].split('\nlabel_80452970:\n',1)[0]
labels=re.findall(r'^label_([0-9A-F]+):',body,re.M)
assert set(re.findall(r'goto label_([0-9A-F]+);',body))-set(labels)=={'80452970'}
assert body.count('DOLRECOMP_C_LOOP_CYCLE_BUDGET')==4
switch='switch(ctx->pc) {\n'+''.join(f'case 0x{pc}u: goto label_{pc};\n' for pc in labels)+'default: abort();\n}\n'
header=re.search(r'^#include "([^"]+RMGE01.h)"',source,re.M)[1]
program=r'''
#pragma STDC FENV_ACCESS ON
#include "HEADER"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <fenv.h>
void galaxypad_deferred_add(CPUState*,u8,u8,u8);
void galaxypad_deferred_sub(CPUState*,u8,u8,u8);
void galaxypad_deferred_mul(CPUState*,u8,u8,u8);
void galaxypad_deferred_madd(CPUState*,u8,u8,u8,u8,bool,bool);
static bool phase(CPUState* ctx) { SWITCH BODY
label_80452970: ctx->pc=0x80452970u; return true;
}
CANDIDATE
static u8 ram[4096],exram[4096];
static CPUState* owner;
static s64 credit;
static unsigned reads,journals,max_coeff,max_quant,yields;
static u64 digest;
static void hash(const void* pointer,size_t n) {
 const u8* p=pointer;while(n--){digest^=*p++;digest*=1099511628211ull;}
}
static void observe(CPUState* c,u32 address,u8 size) {
 assert(c==owner);CPUState normalized=*c;normalized.downcount-=credit;
 hash(&normalized,sizeof normalized);hash(&address,sizeof address);hash(&size,sizeof size);
}
static u64 read_external(CPUState* c,u32 ea,u8 size) {
 observe(c,ea,size);reads++;
 u32 offset;
 if(ea>=0x80001000u&&ea+size<=0x80001010u) {
  offset=ea-0x80001000u;if(offset+size>max_coeff)max_coeff=offset+size;
 } else {assert(ea>=0x90001000u&&ea+size<=0x90001008u);
  offset=ea-0x90001000u;if(offset+size>max_quant)max_quant=offset+size;
 }
 // Deterministic nonzero read-ahead values; resulting registers are observable.
 u64 value=0;for(unsigned i=0;i<size;i++)value=(value<<8)|(1+offset+i);
 return value;
}
static void journal(u32 offset,u32 size,void* user) {
 assert(user==owner);observe(owner,offset,(u8)size);hash(ram+offset,size);journals++;
}
typedef struct {CPUState cpu;u8 ram[4096],exram[4096];u64 digest;unsigned reads,journals,mc,mq;} Result;
static unsigned candidate_hits;
static void run(unsigned pattern,bool boundary,bool yielding,bool use_journal,bool candidate,Result* result) {
 memset(ram,0,sizeof ram);memset(exram,0,sizeof exram);
 unsigned coeff=boundary?3968:512,quant=boundary?3840:512;
 for(unsigned col=0;col<8;col++) {
  write_be16(ram+coeff+16*col,4);
  if(pattern)write_be16(ram+coeff+16*col+2*(1u<<(pattern-1)),3);
  for(unsigned i=0;i<8;i++)write_be32(exram+quant+32*col+4*i,0x3f800000u);
 }
 CPUState c={0};c.ram=ram;c.ram_size=sizeof ram;c.exram=exram;c.exram_size=sizeof exram;
 c.external_read=read_external;c.msr=PPC_MSR_FP;c.hid2=PPC_HID2_LSQE;c.gqr[5]=0x00070007;
 c.gpr[3]=0x80000000u+coeff;c.gpr[5]=0x90000000u+quant;c.gpr[10]=0x800000f8u;
 c.ctr=8;c.pc=0x80452750u;c.reserve_valid=true;c.reserve_addr=0x80000100u;
 const float constants[]={1024.f,-2.613125930f,1.082392200f,1.847759065f,1.414213562f};
 for(unsigned i=0;i<5;i++)c.fpr[25+i]=c.ps1[25+i]=constants[i];
 c.downcount=yielding?-256:100000;credit=c.downcount;owner=&c;
 digest=14695981039346656037ull;reads=journals=max_coeff=max_quant=yields=0;
 g_mem_write_journal=use_journal?journal:NULL;g_mem_write_journal_user=&c;
 unsigned hits=0;
 while(true) {
  bool done=false;
  if(candidate&&galaxy_try_local_columns(&c,&done)){hits++;candidate_hits++;}
  else done=phase(&c);
  if(done)break;
  assert(!c.exception&&++yields<=8);
  assert(c.pc==0x80452750u||c.pc==0x80452770u);
  // Keep the remaining budget negative to exercise each taken backedge.
 }
 const unsigned expected_writes[]={64,112,80,64};
 assert(c.ctr==0&&c.pc==0x80452970u&&!c.reserve_valid&&journals==(use_journal?expected_writes[pattern]:0));
 assert(hits==(unsigned)(candidate&&!use_journal&&!boundary));
 if(yielding)assert(yields==7);else assert(yields==0);
 if(boundary&&pattern)assert(max_coeff==16&&max_quant==8&&reads>0);
 else assert(reads==0);
 c.downcount-=credit;result->cpu=c;memcpy(result->ram,ram,sizeof ram);memcpy(result->exram,exram,sizeof exram);
 result->digest=digest;result->reads=reads;result->journals=journals;result->mc=max_coeff;result->mq=max_quant;
 g_mem_write_journal=NULL;g_mem_write_journal_user=NULL;
}
int main(void) {
 unsigned cases=0;const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
 for(unsigned mode=0;mode<4;mode++) {assert(!fesetround(modes[mode]));
  for(unsigned p=0;p<4;p++)for(unsigned b=0;b<2;b++) {
   Result a={0},c={0};feclearexcept(FE_ALL_EXCEPT);run(p,b,false,true,false,&a);int flags=fetestexcept(FE_ALL_EXCEPT);
   feclearexcept(FE_ALL_EXCEPT);run(p,b,true,true,false,&c);assert(flags==fetestexcept(FE_ALL_EXCEPT));
   assert(!memcmp(&a,&c,sizeof a));cases++;
   for(unsigned j=0;j<2;j++)for(unsigned y=0;y<2;y++) {
    feclearexcept(FE_ALL_EXCEPT);run(p,b,y,j,false,&a);flags=fetestexcept(FE_ALL_EXCEPT);
    feclearexcept(FE_ALL_EXCEPT);run(p,b,y,j,true,&c);assert(flags==fetestexcept(FE_ALL_EXCEPT));
    assert(!memcmp(&a,&c,sizeof a));
   }
  }
 }
 assert(candidate_hits==32);
 for(unsigned test=0;test<18;test++) {
  CPUState c={0};c.ram=ram;c.ram_size=sizeof ram;c.exram=exram;c.exram_size=sizeof exram;
  c.pc=0x80452750u;c.ctr=8;c.msr=PPC_MSR_FP;c.hid2=PPC_HID2_LSQE;c.gqr[5]=0x00070007;
  c.gpr[3]=0x80000200u;c.gpr[5]=0x90000200u;c.gpr[10]=0x800000f8u;
  switch(test) {
   case 0:c.pc+=4;break;case 1:c.ctr=7;break;case 2:c.exception=1;break;
   case 3:c.msr=0;break;case 4:c.hid2=0;break;case 5:c.gqr[5]^=0x01000000;break;
   case 6:c.gqr[0]=4;break;case 7:c.gqr[0]=0x40000;break;
   case 8:g_mem_write_journal=journal;break;case 9:c.downcount=INT64_MIN;break;
   case 10:c.ram=NULL;break;case 11:c.ram_size=100;break;case 12:c.exram_size=100;break;
   case 13:c.gpr[3]=0x80000f80u;break;case 14:c.gpr[5]=0x90000f00u;break;
   case 15:c.gpr[10]=c.gpr[3]-8;break;
   case 16:c.exram=ram;break;
   case 17:c.ram=(u8*)&c;c.ram_size=sizeof c;c.gpr[3]=0x80000000u;break;
  }
  CPUState before=c;u8 old_ram[4096],old_exram[4096];
  memcpy(old_ram,ram,sizeof ram);memcpy(old_exram,exram,sizeof exram);
  bool completed=true;assert(!galaxy_try_local_columns(&c,&completed));
  assert(completed&&!memcmp(&before,&c,sizeof c));
  assert(!memcmp(old_ram,ram,sizeof ram)&&!memcmp(old_exram,exram,sizeof exram));
  g_mem_write_journal=NULL;
 }
 printf("%u first-pass resume and %u candidate comparisons; %u actual local-state hits pass\n",cases,cases*4,candidate_hits);
 puts("18 rejected states preserve CPU, memory and completion output");
}
'''.replace('HEADER',header).replace('SWITCH',switch).replace('BODY',body).replace('CANDIDATE',candidate_source(source))
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
cpu_reference=reference_source((core/'cpu.c').read_text())
for path,expected in (
    (core/'cpu_interpreter_float.c','554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'),
    (core.parent.parent/'include/core/cpu.h','7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'),
):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,path
with tempfile.TemporaryDirectory(prefix='galaxypad-first-pass-') as temporary:
    path=Path(temporary);(path/'test.c').write_text(program)
    (path/'cpu.c').write_text(cpu_reference)
    for flags in (['-O1','-fsanitize=address,undefined'],['-O2']):
        subprocess.run(['clang','-std=c11',*flags,'-ffp-contract=off','-fno-fast-math',
                        '-ffunction-sections','-fdata-sections','-I',str(core.parent.parent/'include'),
                        str(path/'test.c'),str(path/'cpu.c'),str(core/'cpu_interpreter_float.c'),
                        str(core/'cpu_exception.c'),'-Wl,-dead_strip','-o',str(path/'test')],check=True)
        subprocess.run([str(path/'test')],check=True)
