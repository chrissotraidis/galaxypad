"""Execute cached exact-chunk objects on a bounded synthetic interior path.

Not a recorded gameplay-state fixture or installed PGO/LTO performance claim.
Requires probe-llvm-game-chunk.py artifacts; contains no game instruction bytes.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('artifacts',type=Path)
p.add_argument('--arithmetic',action='store_true',help='Exercise the 44-instruction arithmetic path with mapped vector/constants')
p.add_argument('--full-entry',action='store_true',help='Only the routine start; does not establish interior-entry equivalence')
p.add_argument('--reverse-order',action='store_true',help='BAAB instead of ABBA timing order')
p.add_argument('--iterations',type=int,default=1000000)
args=p.parse_args();folder=args.artifacts.resolve()
if not 1<=args.iterations<=10000000:p.error('iterations must be 1..10000000')
report=json.loads((folder/'report.json').read_text())
assert report['guest_start']=='0x804b60a0' and report['instructions']==1024
for name in ('c','ir'):
    assert hashlib.sha256((folder/(name+'.o')).read_bytes()).hexdigest()==report['objects'][name]['sha256']
source=r'''
#pragma STDC FENV_ACCESS ON
#include "core/cpu.h"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
void c_func_804B60A0(CPUState*);
void func_804B60A0(CPUState*);
static double now(void) {
 struct timespec t;assert(!clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t));
 return t.tv_sec+t.tv_nsec*1e-9;
}
int main(void) {
 unsigned char ram[256],expected[256];unsigned count=0;
 unsigned char payload[256];memset(payload,0xa5,sizeof payload);
 if(ARITHMETIC) {
  memset(payload,0,sizeof payload);
  write_be32(payload+64,0x3f800000);write_be32(payload+68,0x40000000);write_be32(payload+72,0x40400000);
  write_be32(payload+128,0x3f000000);write_be32(payload+132,0x40400000);
 }
 CPUState initial={0};initial.ram=ram;initial.ram_size=sizeof ram;
 initial.msr=0x2000;initial.gpr[3]=0x80000000;initial.lr=0x81234564;
 initial.hid2=PPC_HID2_LSQE|PPC_HID2_PSE;
 if(ARITHMETIC) {initial.gpr[4]=0x80000040;initial.gpr[2]=0x80000080u-9400;}
 const unsigned start_pc=ARITHMETIC?0x804b6278:0x804b6224,entries=ARITHMETIC?44:11;
 for(unsigned entry=0;entry<(FULL_ENTRY?1:entries);entry++) for(unsigned sample=0;sample<1000;sample++) {
  CPUState a=initial;
  for(unsigned r=0;r<32;r++) { a.fpr[r]=(double)(int)(sample+r*13)/17-50;a.ps1[r]=-a.fpr[r]; }
  if(ARITHMETIC) for(unsigned r=0;r<32;r++) {a.fpr[r]=(sample%97+r+1)/31.0;a.ps1[r]=(sample%83+r+1)/29.0;}
  a.pc=start_pc+entry*4;a.downcount=10000;
  CPUState b=a;memcpy(ram,payload,sizeof ram);feclearexcept(FE_ALL_EXCEPT);
  c_func_804B60A0(&a);int flags=fetestexcept(FE_ALL_EXCEPT);memcpy(expected,ram,sizeof ram);
  memcpy(ram,payload,sizeof ram);feclearexcept(FE_ALL_EXCEPT);func_804B60A0(&b);
  if(memcmp(&a,&b,sizeof a)||memcmp(expected,ram,sizeof ram)||flags!=fetestexcept(FE_ALL_EXCEPT)) {
   size_t k=0;while(k<sizeof a&&((u8*)&a)[k]==((u8*)&b)[k])k++;
   fprintf(stderr,"entry=%u sample=%u mismatch byte=%zu PC=%x/%x cycles=%lld/%lld flags=%x/%x\n",
     entry,sample,k,a.pc,b.pc,(long long)a.downcount,(long long)b.downcount,flags,fetestexcept(FE_ALL_EXCEPT));
   return 1;
  }
  assert(a.pc==initial.lr&&a.downcount==10000-(entries-entry)&&!a.exception);count++;
 }
 printf("%u exact-chunk %s full-state/RAM/flag cases pass; synthetic finite inputs\n",count,FULL_ENTRY?"normal-entry":"all-selected-entries");
 for(unsigned run=0;run<4;run++) {
  CPUState s=initial;for(unsigned r=0;r<32;r++) {s.fpr[r]=r/17.0;s.ps1[r]=-r/19.0;}
  memcpy(ram,payload,sizeof ram);
  int candidate=(run==1||run==2)^REVERSE;
  void (*fn)(CPUState*)=candidate?func_804B60A0:c_func_804B60A0;
  double start=now();
  for(unsigned i=0;i<ITERATIONS;i++) {s.pc=start_pc;s.downcount=10000;if(ARITHMETIC){s.fpr[1]=0.2;s.fpr[2]=0.8;}fn(&s);}
  printf("run=%u backend=%s ns_per_call=%.3f\n",run,candidate?CANDIDATE_LABEL:"C",(now()-start)*1e9/ITERATIONS);
 }
 puts("No gameplay-state distribution, installed-policy parity or FPS claim.");
}
'''
source=source.replace('ARITHMETIC','1' if args.arithmetic else '0').replace('FULL_ENTRY','1' if args.full_entry else '0')
source=source.replace('CANDIDATE_LABEL',json.dumps(report.get('candidate_label','IR')))
source=source.replace('REVERSE','1' if args.reverse_order else '0').replace('ITERATIONS',str(args.iterations))
runtime=root/'ref/ModernGekko/vendor/dolphin/GXRuntime'
with tempfile.TemporaryDirectory(prefix='galaxypad-exact-chunk-') as directory:
    temp=Path(directory);(temp/'test.c').write_text(source)
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
      '-ffunction-sections','-fdata-sections','-Wl,-dead_strip','-I'+str(runtime/'include'),
      '-I'+str(runtime/'src/core'),str(temp/'test.c'),str(folder/'c.o'),str(folder/'ir.o'),
      *[str(runtime/'src/core'/n) for n in ('cpu.c','cpu_interpreter_float.c','cpu_exception.c','cpu_interpreter_table.c')],
      '-o',str(temp/'test')],check=True)
    subprocess.run([str(temp/'test')],check=True)
