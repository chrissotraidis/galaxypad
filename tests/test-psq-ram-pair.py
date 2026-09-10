"""Isolated direct-RAM paired-store prototype against actual inline helper."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
include = root / 'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
header = (include / 'core/cpu.h').read_text()
original = header.split('static inline bool ppc_psq_store_inline(', 1)[1].split('\nu32 ppc_eciwx', 1)[0]
candidate = 'static bool candidate(' + original
anchor = '        mem_write32(cpu, ea, convert_to_single_ftz(f64_bits(cpu->fpr[frS])));'
assert candidate.count(anchor) == 1
candidate = candidate.replace(anchor, (root / 'patches/experiments/psq-ram-pair-store.inc').read_text() + '\n' + anchor)
source = r'''
#include "core/cpu.h"
#include <assert.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
typedef struct {u32 address,value,size;} Event;
static Event events[8]; static unsigned count,slow;
static CPUState* active;
static void external(CPUState* c,u32 ea,u64 value,u8 size) {
  assert(count<8); events[count++]=(Event){ea,(u32)value,size};
  c->ps1[3]=123; // Original must read lane1 after the callback.
}
static void journal(u32 offset,u32 size,void* user) {
  assert(count<8); events[count++]=(Event){offset,0,size};
  active->ps1[3]=456;
}
bool ppc_psq_store(CPUState* c,u8 r,u32 ea,bool w,u8 g,bool indexed,u32 cia) {
  ++slow; c->pc=cia; return false;
}
'''+candidate+r'''
static u8 ram[256],exram[256];
static u32 rng=123;
static u32 random32(void){rng=rng*1664525u+1013904223u;return rng;}
static void check(CPUState initial,u32 ea,bool w,u8 g,bool indexed) {
  u8 expected_ram[256],expected_exram[256]; Event expected_events[8];
  memset(ram,0xaa,sizeof ram);memset(exram,0x55,sizeof exram);
  CPUState a=initial;active=&a;count=slow=0;memset(events,0,sizeof events);
  bool result=ppc_psq_store_inline(&a,3,ea,w,g,indexed,0x1234);
  memcpy(expected_ram,ram,sizeof ram);memcpy(expected_exram,exram,sizeof exram);
  memcpy(expected_events,events,sizeof events);unsigned n=count,s=slow;
  memset(ram,0xaa,sizeof ram);memset(exram,0x55,sizeof exram);
  CPUState b=initial;active=&b;count=slow=0;memset(events,0,sizeof events);
  assert(candidate(&b,3,ea,w,g,indexed,0x1234)==result);
  assert(!memcmp(&a,&b,sizeof a));
  assert(!memcmp(expected_ram,ram,sizeof ram));
  assert(!memcmp(expected_exram,exram,sizeof exram));
  assert(n==count && s==slow && !memcmp(expected_events,events,sizeof events));
}
static bool reference(CPUState* c,u8 r,u32 ea,bool w,u8 g,bool indexed,u32 cia) {
  return ppc_psq_store_inline(c,r,ea,w,g,indexed,cia);
}
int main(void) {
#ifdef BENCHMARK
  CPUState c={0};c.ram=ram;c.ram_size=sizeof ram;
  c.exram=exram;c.exram_size=sizeof exram;c.hid2=PPC_HID2_LSQE;
  c.fpr[3]=12.25;c.ps1[3]=-34.5;
  for(unsigned trial=0;trial<6;trial++) {
    double times[2];
    for(unsigned order=0;order<2;order++) {
      unsigned choice=order^(trial&1);
      bool (*volatile fn)(CPUState*,u8,u32,bool,u8,bool,u32)=choice?candidate:reference;
      clock_t begin=clock();
      for(unsigned i=0;i<5000000;i++) fn(&c,3,0x90000000+(i%60)*4,false,0,false,0);
      times[choice]=(double)(clock()-begin)/CLOCKS_PER_SEC;
    }
    printf("RAM pair candidate/reference %.4f (%.6f/%.6f CPU seconds)\n",times[1]/times[0],times[1],times[0]);
  }
  return 0;
#endif
  const u32 bases[]={0x80000000,0xc0000000,0x90000000,0xd0000000};
  for(unsigned i=0;i<100000;i++) {
    CPUState c={0};c.ram=ram;c.ram_size=sizeof ram;
    c.exram=(i%3)?exram:NULL;c.exram_size=sizeof exram;
    c.hid2=(i%7)?PPC_HID2_LSQE:0;c.external_write=external;
    c.fpr[3]=f64_value(((u64)random32()<<32)|random32());
    c.ps1[3]=f64_value(((u64)random32()<<32)|random32());
    c.gqr[0]=(i%13)?0:4;c.reserve_valid=true;
    u32 ea=bases[i%4]+(random32()%260);
    c.reserve_addr=(i%2)?ea:ea+4;
    g_mem_write_journal=(i%5)?NULL:journal;
    check(c,ea,i%11==0,0,i%17==0);
  }
  // CPU-alias exclusion: the first write can change the second lane's value.
  g_mem_write_journal=NULL;
  CPUState a={0};a.ram=(u8*)&a;a.ram_size=sizeof a;a.hid2=PPC_HID2_LSQE;
  a.fpr[3]=12;a.ps1[3]=34;CPUState b=a;b.ram=(u8*)&b;
  u32 ea=0x80000000u+(u32)((u8*)&a.ps1[3]-(u8*)&a);
  ppc_psq_store_inline(&a,3,ea,false,0,false,0);
  candidate(&b,3,ea,false,0,false,0);
  a.ram=b.ram=NULL;assert(!memcmp(&a,&b,sizeof a));
  puts("100k paired RAM stores: values, boundaries, mirrors, reservations, callbacks and CPU alias passed");
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-ram-pair-') as temp:
    base = Path(temp)
    (base / 'test.c').write_text(source)
    subprocess.run(['clang', '-O2', '-fsanitize=address,undefined', '-I', str(include),
                    str(base / 'test.c'), '-o', str(base / 'test')], check=True)
    subprocess.run([str(base / 'test')], check=True)
    subprocess.run(['clang', '-O2', '-DBENCHMARK', '-I', str(include),
                    str(base / 'test.c'), '-o', str(base / 'bench')], check=True)
    subprocess.run([str(base / 'bench')], check=True)
