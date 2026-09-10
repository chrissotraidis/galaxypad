"""Isolated paired-load correctness and timing; never changes runtime sources."""
import hashlib
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
include = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
header = (include/'core/cpu.h').read_text()
assert hashlib.sha256(header.encode()).hexdigest() == '7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'
body = header.split('static inline bool ppc_psq_load_inline(', 1)[1].split('\nstatic inline bool ppc_psq_store_inline', 1)[0]
anchor = '        cpu->fpr[frD] = f64_value(convert_to_double(mem_read32(cpu, ea)));'
assert body.count(anchor) == 1
candidate = 'static bool candidate(' + body.replace(anchor,
    (root/'patches/experiments/psq-ram-pair-load.inc').read_text()+'\n'+anchor)
program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
static u8 ram[256],exram[256],replacement[256];
static unsigned callbacks,slow;
static u64 external(CPUState* c,u32 ea,u8 size) {
 assert(size==4);++callbacks;c->ram=replacement;c->msr^=0x2000;
 c->fpr[3]=42;return ea^0x12345678;
}
bool ppc_psq_load(CPUState* c,u8 r,u32 ea,bool w,u8 g,bool indexed,u32 cia) {
 ++slow;c->pc=cia;return false;
}
'''+candidate+r'''
static bool reference(CPUState* c,u8 r,u32 ea,bool w,u8 g,bool indexed,u32 cia) {
 return ppc_psq_load_inline(c,r,ea,w,g,indexed,cia);
}
static unsigned seed=17;
static unsigned random32(void) {seed=seed*1664525u+1013904223u;return seed;}
int main(void) {
#ifdef BENCHMARK
 CPUState c={0};c.ram=ram;c.ram_size=256;c.exram=exram;c.exram_size=256;
 c.hid2=PPC_HID2_LSQE;
 for(unsigned i=0;i<64;i++) {
  u32 bits=0x3f000000u+(i<<16);if(i&1) bits|=0x80000000u;
  write_be32(ram+i*4,bits);write_be32(exram+i*4,bits);
 }
 for(unsigned memory=0;memory<2;memory++) for(unsigned trial=0;trial<6;trial++) {
  double times[2];
  for(unsigned step=0;step<2;step++) {
   unsigned which=step^(trial&1);
   bool(*volatile fn)(CPUState*,u8,u32,bool,u8,bool,u32)=which?candidate:reference;
   clock_t begin=clock();
   for(unsigned i=0;i<5000000;i++) fn(&c,3,(memory?0x90000000u:0x80000000u)+(i%60)*4,false,0,false,0);
   times[which]=(double)(clock()-begin)/CLOCKS_PER_SEC;
  }
  printf("memory=%u trial=%u reference=%.6f candidate=%.6f ratio=%.4f\n",memory,trial,times[0],times[1],times[1]/times[0]);
 }
#else
 const u32 bases[]={0x80000000u,0xc0000000u,0x90000000u,0xd0000000u,0xffffff00u};
 for(unsigned i=0;i<100000;i++) {
  for(unsigned j=0;j<256;j++) {ram[j]=random32()>>24;exram[j]=random32()>>24;replacement[j]=random32()>>24;}
  CPUState a={0};a.ram=ram;a.ram_size=256;a.exram=i%3?exram:NULL;a.exram_size=256;
  a.hid2=i%7?PPC_HID2_LSQE:0;a.gqr[0]=i%13?0:4u<<16;a.external_read=external;
  CPUState b=a;u32 ea=bases[i%5]+random32()%264;
  callbacks=slow=0;bool ar=reference(&a,3,ea,i%11==0,0,i%17==0,0x1234);
  unsigned ac=callbacks,as=slow;callbacks=slow=0;
  bool br=candidate(&b,3,ea,i%11==0,0,i%17==0,0x1234);
  assert(ar==br && ac==callbacks && as==slow && !memcmp(&a,&b,sizeof a));
 }
 // First lane assignment must be observable to a second RAM read that aliases it.
 CPUState a={0};a.ram=(u8*)&a;a.ram_size=sizeof a;a.hid2=PPC_HID2_LSQE;
 a.fpr[3]=17.25;CPUState b=a;b.ram=(u8*)&b;
 u32 ea=0x80000000u+(u32)((u8*)&a.fpr[3]-(u8*)&a);
 reference(&a,3,ea,false,0,false,0);candidate(&b,3,ea,false,0,false,0);
 a.ram=b.ram=NULL;assert(!memcmp(&a,&b,sizeof a));
 puts("100000 paired loads plus CPU alias pass: mapping boundaries, mirrors, callback remaps, type/LSQE routing");
#endif
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-pair-load-') as directory:
    temp = Path(directory)
    (temp/'test.c').write_text(program)
    for name, flags in (('test', ['-O2', '-fsanitize=address,undefined']),
                        ('bench', ['-O2', '-DBENCHMARK'])):
        subprocess.run(['clang', *flags, '-I', str(include), str(temp/'test.c'), '-o', str(temp/name)], check=True)
        subprocess.run([str(temp/name)], check=True, timeout=60)
