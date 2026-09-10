"""Exact emitted zero-column comparison, including host FP flags and aliases."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from zero_dc_column import get_helper,transform
nonzero_dc='--nonzero-dc' in sys.argv
second_kernel='--second-kernel' in sys.argv
assert not second_kernel or nonzero_dc
source=(root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed=transform(source,nonzero_dc=nonzero_dc,both_kernels=second_kernel)
outer='void func_804520A0(CPUState* ctx) {'
assert source.split(outer,1)[1]==changed.split(outer,1)[1]
start,end=('80452BDC','80452C30') if second_kernel else ('80452750','804527A4')
segment=source.split(f'\nlabel_{start}:\n',1)[1].split(f'\nlabel_{end}:\n',1)[0]
labels=set(re.findall(r'(?m)^label_([A-F0-9]+):',segment))
targets=set(re.findall(r'goto label_([A-F0-9]+);',segment))-labels
traps='\n'.join('label_'+label+': abort();' for label in sorted(targets))
program=r'''
#pragma STDC FENV_ACCESS ON
#include "core/cpu.h"
#include <assert.h>
#include <stdlib.h>
#include <fenv.h>
HELPER
static bool reference(CPUState* ctx) {SEGMENT
 return true;
TRAPS
}
static u8 ram[1024],exram[1024];
static u64 seed=13;
static u64 random64(void){seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return seed;}
static void journal(u32 a,u32 b,void* c){abort();}
int main(void) {
 const int modes[]={FE_TONEAREST,FE_UPWARD,FE_DOWNWARD,FE_TOWARDZERO};
 const u32 special[]={0,0x80000000,1,0x7f800000,0xff800000,0x7f800001,0x7fc12345,0xffc12345};
 unsigned hits=0;
 for(unsigned mode=0;mode<4;mode++) {
  assert(fesetround(modes[mode])==0);
  for(unsigned i=0;i<10000;i++) {
   memset(ram,0xa5,sizeof ram);memset(exram,0x5a,sizeof exram);
   const u32 bases[]={0x80000000,0xc0000000,0x90000000,0xd0000000};
   u32 base=bases[i%4];u8* memory=i%4<2?ram:exram;
   memset(memory,0,16);
   write_be32(memory+64,i<64?special[i/8]:(u32)random64());
   write_be32(memory+68,i<64?special[i%8]:(u32)random64());
   CPUState a={0};a.ram=ram;a.ram_size=sizeof ram;a.exram=exram;a.exram_size=sizeof exram;
   a.msr=PPC_MSR_FP;a.hid2=PPC_HID2_LSQE;a.gqr[5]=0x00070007;
   // Include output overlapping coefficients or quant values. All source reads
   // must finish before stores, just as in the original emitted segment.
   const u32 outputs[]={120u,0xfffffff8u,56u};
   a.gpr[3]=base;a.gpr[5]=base+64;a.gpr[10]=base+outputs[i%3];
   a.gpr[0]=a.gpr[6]=a.gpr[7]=a.gpr[8]=0x87654321;
   a.cr=(u32)random64();a.xer=(u32)random64();a.fpscr=(u32)random64();
   a.ctr=i%10;a.downcount=(s64)(i%1000)-500;
   a.reserve_addr=base+100+i%100;a.reserve_valid=i&1;
   CPUState b=a;u8 initial_ram[1024],initial_exram[1024],result_ram[1024],result_exram[1024];
   memcpy(initial_ram,ram,sizeof ram);memcpy(initial_exram,exram,sizeof exram);
   feclearexcept(FE_ALL_EXCEPT);assert(reference(&a));int flags=fetestexcept(FE_ALL_EXCEPT);
   memcpy(result_ram,ram,sizeof ram);memcpy(result_exram,exram,sizeof exram);
   memcpy(ram,initial_ram,sizeof ram);memcpy(exram,initial_exram,sizeof exram);
   feclearexcept(FE_ALL_EXCEPT);assert(galaxy_zero_column(&b));hits++;
   assert(flags==fetestexcept(FE_ALL_EXCEPT));
   assert(!memcmp(&a,&b,sizeof a));
   assert(!memcmp(result_ram,ram,sizeof ram)&&!memcmp(result_exram,exram,sizeof exram));
  }
 }
 for(unsigned i=0;i<13;i++) {
  memset(ram,0,sizeof ram);
  CPUState c={0};c.ram=ram;c.ram_size=sizeof ram;c.msr=PPC_MSR_FP;c.hid2=PPC_HID2_LSQE;
  c.gqr[5]=0x00070007;c.gpr[3]=0x80000000;c.gpr[5]=0x80000040;c.gpr[10]=0x80000078;
  switch(i) {
   case 0:ram[0]=1;break;case 1:ram[15]=1;break;case 2:c.exception=1;break;
   case 3:c.msr=0;break;case 4:c.hid2=0;break;case 5:c.gqr[5]^=0x1000000;break;
   case 6:c.gqr[0]=0x40000;break;case 7:c.gqr[0]=4;break;
   case 8:g_mem_write_journal=journal;break;case 9:c.gpr[3]=0xe0000000;break;
   case 10:c.gpr[10]=0x800003f0;break;case 11:c.downcount=INT64_MIN;break;
   case 12:c.ram=(u8*)&c;c.ram_size=sizeof c;break;
  }
  CPUState before=c;assert(!galaxy_zero_column(&c));assert(!memcmp(&before,&c,sizeof c));
  g_mem_write_journal=NULL;
 }
 printf("%u zero-column state/memory/host-FP cases across4rounding modes;13 guards pass\n",hits);
}
'''.replace('HELPER',get_helper(nonzero_dc,kernel=int(second_kernel))).replace('SEGMENT',segment).replace('TRAPS',traps)
if second_kernel:
    program=program.replace('galaxy_zero_column(', 'galaxy_second_column(')
if nonzero_dc:
    program=program.replace('i<10000','i<65536')
    program=program.replace('memset(memory,0,16);',
                            'memset(memory,0,16);write_be16(memory,(u16)(i-32768));')
    program=program.replace('case 0:ram[0]=1;', 'case 0:ram[2]=1;')
    program=program.replace('zero-column state/memory/host-FP', 'signed-DC-column state/memory/host-FP')
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
with tempfile.TemporaryDirectory(prefix='galaxypad-zero-column-') as directory:
    path=Path(directory);(path/'test.c').write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-fsanitize=address,undefined',
                    '-ffp-contract=off','-fno-fast-math','-ffunction-sections','-fdata-sections',
                    '-I',str(core.parent.parent/'include'),str(path/'test.c'),
                    str(core/'cpu.c'),str(core/'cpu_interpreter_float.c'),str(core/'cpu_exception.c'),
                    '-Wl,-dead_strip','-o',str(path/'test')],check=True)
    subprocess.run([str(path/'test')],check=True)
