"""Actual four-load sequence: shared range guard, original observer fallback.

Private correctness experiment, not installed code or a performance claim.
"""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
include = root / 'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
matches = list((root / 'generated/modules-scale-r387/RMGE01').glob(
    '*/dolrecomp-output/RMGE01_generated/chunks/*804B60A0.c'))
assert len(matches) == 1
source = matches[0].read_text()
body = 'label_804B66A0:' + source.split('label_804B66A0:', 1)[1].split('label_804B66B0:', 1)[0]
assert body.count('mem_read32(ctx, ea)') == 4
assert set(re.findall(r'ctx->(\w+)', body)) == {'pc', 'gpr'}
cases = ''.join(f'case 0x{pc:X}: goto label_{pc:X};' for pc in range(0x804B66A0, 0x804B66B0, 4))
program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
static unsigned fast_calls, calls;
static u32 addresses[4], pcs[4];
static u64 external(CPUState* c,u32 addr,u8 size) {
 assert(size==4 && calls<4);addresses[calls]=addr;pcs[calls]=c->pc;calls++;
 c->gpr[1]+=4; c->gpr[30]^=addr; // Later loads must see callback mutations.
 return addr^c->pc;
}
static void reference(CPUState* ctx) {
 switch(ctx->pc) { CASES default:return; }
 BODY
}
// No persistent mapping cache. A single bounded range is proved for this call.
static void candidate(CPUState* c) {
 if(c->pc!=0x804B66A0u) {reference(c);return;}
 const u32 base=c->gpr[1], start=base+52u;
 if(base>UINT32_MAX-72u) {reference(c);return;}
 u8* p=NULL;
 // Avoid size underflow and null pointer arithmetic in the range probe.
 if(c->ram && c->ram_size>=20 && (!c->exram || c->exram_size>=20))
   p=get_ram_ptr(c,start,20,NULL);
 const uintptr_t lo=(uintptr_t)p, state=(uintptr_t)c;
 if(!p || lo>UINTPTR_MAX-20 || state>UINTPTR_MAX-sizeof(*c) ||
    (lo<state+sizeof(*c) && state<lo+20)) {reference(c);return;}
 c->gpr[31]=read_be32(p+8);
 c->gpr[30]=read_be32(p+4);
 c->gpr[29]=read_be32(p);
 c->gpr[0]=read_be32(p+16);
 c->pc=0x804B66ACu;
 fast_calls++;
}
static u8 ram[256],exram[256];
static u32 rng=783;
static u32 random32(void){rng=rng*1664525u+1013904223u;return rng;}
int main(void) {
 const u32 bases[]={0x80000000u,0xc0000000u,0x90000000u,0xd0000000u,0xcc000000u,0xfffffff0u};
 for(unsigned i=0;i<120000;i++) {
  CPUState a={0};a.ram=ram;a.ram_size=sizeof ram;
  a.exram=(i%3)?exram:NULL;a.exram_size=sizeof exram;a.external_read=external;
  for(unsigned r=0;r<32;r++) a.gpr[r]=random32();
  for(unsigned j=0;j<256;j++){ram[j]=(u8)random32();exram[j]=(u8)random32();}
  a.gpr[1]=bases[i%6]+(i%280)-64u;a.pc=0x804B66A0u+4u*(i%4);
  CPUState b=a;u32 expected_addr[4],expected_pc[4];
  calls=0;memset(addresses,0,sizeof addresses);memset(pcs,0,sizeof pcs);
  reference(&a);unsigned n=calls;
  memcpy(expected_addr,addresses,sizeof addresses);memcpy(expected_pc,pcs,sizeof pcs);
  calls=0;memset(addresses,0,sizeof addresses);memset(pcs,0,sizeof pcs);
  candidate(&b);
  assert(!memcmp(&a,&b,sizeof a) && n==calls);
  assert(!memcmp(expected_addr,addresses,sizeof addresses));
  assert(!memcmp(expected_pc,pcs,sizeof pcs));
 }
 // A destination write aliases later source bytes: must retain sequential path.
 CPUState a={0};a.ram=(u8*)&a;a.ram_size=sizeof a;a.pc=0x804B66A0u;
 a.gpr[1]=0x80000000u+(u32)((u8*)&a.gpr[29]-(u8*)&a)-52u;
 CPUState b=a;b.ram=(u8*)&b;unsigned before=fast_calls;
 reference(&a);candidate(&b);assert(fast_calls==before);
 a.ram=b.ram=NULL;assert(!memcmp(&a,&b,sizeof a));
 assert(fast_calls>1000);
 printf("120000 actual load-span CPU/callback comparisons plus CPU alias pass; %u shared-range calls\n",fast_calls);
}
'''.replace('CASES', cases).replace('BODY', body)
with tempfile.TemporaryDirectory(prefix='galaxypad-load-span-') as directory:
    c = Path(directory) / 'test.c'
    binary = Path(directory) / 'test'
    c.write_text(program)
    subprocess.run(['clang', '-O2', '-fsanitize=address,undefined', '-I', str(include),
                    str(c), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
