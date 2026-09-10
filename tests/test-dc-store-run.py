"""Compare the emitted DC segment with the guarded offline replacement."""
from pathlib import Path
import subprocess
import tempfile
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from fuse_dc_stores import HELPER, transform
source=(root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed=transform(source)
outer='void func_804520A0(CPUState* ctx) {'
assert source.split(outer,1)[1]==changed.split(outer,1)[1]
segment=source.split('\nlabel_80452788:\n',1)[1].split('\nlabel_8045279C:\n',1)[0]
program=r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdlib.h>
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
bool g_ppc_lazy_fp_enabled=true;
bool ppc_fp_raise_unavailable(CPUState* c,u32 cia) { abort(); }
bool ppc_psq_store(CPUState* c,u8 r,u32 ea,bool w,u8 g,bool indexed,u32 cia) { abort(); }
HELPER
static bool reference(CPUState* ctx) { SEGMENT
 return true;
label_804527AC: abort();
}
static u8 ram[512],exram[512];
static u64 seed=17;
static u64 random64(void) {seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return seed;}
static void journal(u32 a,u32 b,void* c) {abort();}
int main(void) {
 unsigned hits=0;
 for(unsigned i=0;i<100000;i++) {
  CPUState a={0};a.ram=ram;a.ram_size=sizeof ram;a.exram=exram;a.exram_size=sizeof exram;
  a.msr=PPC_MSR_FP;a.hid2=PPC_HID2_LSQE;a.cr=(u32)random64();a.xer=(u32)random64();
  a.fpr[0]=f64_value(random64());a.ps1[0]=f64_value(random64());a.fpscr=(u32)random64();
  const u32 bases[]={0x80000000,0xc0000000,0x90000000,0xd0000000};
  a.gpr[10]=bases[i%4]+(i%100);a.downcount=(s64)(i%1000)-500;
  a.reserve_addr=a.gpr[10]+(i%80);a.reserve_valid=i&1;
  CPUState b=a;u8 expected_ram[512],expected_exram[512];
  memset(ram,0xa5,sizeof ram);memset(exram,0x5a,sizeof exram);assert(reference(&a));
  memcpy(expected_ram,ram,sizeof ram);memcpy(expected_exram,exram,sizeof exram);
  memset(ram,0xa5,sizeof ram);memset(exram,0x5a,sizeof exram);
  assert(galaxy_dc_store_run(&b));hits++;
  assert(!memcmp(&a,&b,sizeof a));
  assert(!memcmp(ram,expected_ram,sizeof ram) && !memcmp(exram,expected_exram,sizeof exram));
 }
 for(unsigned i=0;i<14;i++) {
  CPUState c={0};c.ram=ram;c.ram_size=512;c.gpr[10]=0x80000000;
  c.msr=PPC_MSR_FP;c.hid2=PPC_HID2_LSQE;
  switch(i) {
   case 0:c.gpr[7]=1;break;case 1:c.exception=1;break;case 2:c.msr=0;break;
   case 3:c.hid2=0;break;case 4:c.gqr[0]=4;break;case 5:g_mem_write_journal=journal;break;
   case 6:c.ram_size=16;break;case 7:c.ram_size=0xffffffffu;break;
   case 8:c.exram=exram;c.exram_size=1;break;case 9:c.gpr[10]=0xe0000000;break;
   case 10:c.gpr[10]=0x800001e0;break;case 11:c.downcount=INT64_MIN;break;
   case 12:c.ram=(u8*)&c;c.ram_size=sizeof c;break;
   case 13:c.ram=(u8*)&g_mem_write_journal;c.gpr[10]=0x7ffffff0;break;
  }
  CPUState before=c;assert(!galaxy_dc_store_run(&c));assert(!memcmp(&c,&before,sizeof c));
  g_mem_write_journal=NULL;
 }
 printf("%u emitted DC-segment state/memory/reservation cases;14 guards pass\n",hits);
}
'''.replace('HELPER',HELPER).replace('SEGMENT',segment)
with tempfile.TemporaryDirectory(prefix='galaxypad-dc-stores-') as directory:
    path=Path(directory);(path/'test.c').write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-fsanitize=address,undefined',
                    '-I',str(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'),
                    str(path/'test.c'),'-o',str(path/'test')],check=True)
    subprocess.run([str(path/'test')],check=True)
