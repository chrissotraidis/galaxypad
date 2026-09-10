"""Actual emitted tail versus fused leader, including every interior entry."""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from fuse_huffman_tail import parts, transform, START, END
module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
source = (module.parent/'dolrecomp-output/RMGE01_generated/chunks/chunk_1103_text1_804530A0.c').read_text()
helper = parts(source)
changed = transform(source)
anchor = 'label_'+START+':'
insertion = '\n    if (galaxy_huffman_tail(ctx)) goto label_'+END+';\n    goto label_80453AF0;'
assert changed.replace(helper+'\n', '', 1).replace(anchor+insertion, anchor, 1) == source
addresses = [f'{pc:08X}' for pc in range(int(START,16), int(END,16),4)]
cases = '\n'.join(re.search(r'case 0x'+pc+r'u: [^\n]+', source)[0] for pc in addresses)
body = anchor+source.split(anchor,1)[1].split('label_'+END+':',1)[0]
ending = '\nlabel_80453AEC: return 0;\nlabel_80453AF0: return 1;\n'
ref = 'static int reference(CPUState* ctx) { switch(ctx->pc) {\n'+cases+'\ndefault: return 2;}\n'+body+ending+'}\n'
cand = ref.replace('reference(', 'candidate(',1).replace(anchor, anchor+insertion,1)
program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
static u8 ram[2048], exram[2048], alternate[2048];
static CPUState* active;
static unsigned mode, reads, writes, journals;
static u64 events;
static void record(CPUState* cpu, u32 addr, u64 value, unsigned size) {
    const u8* p=(const u8*)cpu;
    for(unsigned i=0;i<sizeof(*cpu);i++) events=(events^p[i])*1099511628211ULL;
    events=(events^addr^value^size)*1099511628211ULL;
}
static u64 read_cb(CPUState* cpu,u32 addr,u8 size) {
    reads++;record(cpu,addr,17,size);
    if(mode&1) {cpu->gpr[4]^=0x100;cpu->gpr[31]^=0x4321;cpu->ram=alternate;cpu->exception^=1;}
    return 17;
}
static void write_cb(CPUState* cpu,u32 addr,u64 value,u8 size) {
    writes++;record(cpu,addr,value,size);
    if(mode&1) {cpu->gpr[5]=63;cpu->xer^=0x80000000;cpu->cr^=0x1234;}
}
static void journal(u32 offset,u32 size,void* user) {
    (void)user;journals++;record(active,offset,read_be16(active->ram+offset),size);
    if(mode&1) {active->ram=alternate;active->gpr[5]=64;active->reserve_valid=true;}
}
HELPER
REFERENCE
CANDIDATE
static u32 seed=0x9876abcd;
static u32 rng(void){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return seed;}
int main(void) {
  unsigned count=0;
  const u32 bases[]={0x80000000,0xc0000000,0x90000000,0xd0000000,0xe0000000};
  for(mode=0;mode<8;mode++) for(unsigned i=0;i<1000;i++) for(unsigned e=0;e<16;e++) {
    CPUState a={0};
    for(unsigned j=0;j<32;j++)a.gpr[j]=rng();
    a.pc=0x80453AAC+4*e;a.downcount=(s64)(i%100)-50;
    a.cr=rng();a.xer=rng();a.exception=rng();a.reserve_addr=bases[i%5]+(i%32)*32;a.reserve_valid=i&1;
    a.ram=ram;a.ram_size=sizeof ram;a.exram=exram;a.exram_size=sizeof exram;
    a.external_read=read_cb;a.external_write=write_cb;
    a.gpr[5]=i%70;a.gpr[10]=bases[i%5]+16;a.gpr[4]=bases[(i/5)%5]+512;
    a.gpr[28]=i%40;a.gpr[31]=i<33?(i==32?0:1u<<i):rng();
    if(mode&4)a.gpr[4]=a.gpr[10]-a.gpr[5]; // Output may overlap input table.
    for(unsigned j=0;j<sizeof ram;j++){ram[j]=j+i;exram[j]=j^i;alternate[j]=0x55;}
    u8 initial[3][2048],result[3][2048];
    memcpy(initial[0],ram,2048);memcpy(initial[1],exram,2048);memcpy(initial[2],alternate,2048);
    CPUState b=a;g_mem_write_journal=(mode&2)?journal:NULL;
    active=&a;reads=writes=journals=0;events=0;
    int ar=reference(&a);u64 ae=events;unsigned nr=reads,nw=writes,nj=journals;
    memcpy(result[0],ram,2048);memcpy(result[1],exram,2048);memcpy(result[2],alternate,2048);
    memcpy(ram,initial[0],2048);memcpy(exram,initial[1],2048);memcpy(alternate,initial[2],2048);
    active=&b;reads=writes=journals=0;events=0;int br=candidate(&b);
    assert(ar==br && !memcmp(&a,&b,sizeof a));
    assert(ae==events && nr==reads && nw==writes && nj==journals);
    assert(!memcmp(result[0],ram,2048)&&!memcmp(result[1],exram,2048)&&!memcmp(result[2],alternate,2048));
    count++;
  }
  printf("%u full-state/memory/event comparisons over16entries and8modes passed\n",count);
}
'''.replace('HELPER',helper).replace('REFERENCE',ref).replace('CANDIDATE',cand)
header=module.parent/'dolrecomp-output/RMGE01_generated/RMGE01.h'
# Both audited headers preserve the memory helpers exercised here; the newer
# header changes only original-dispatch lookup. Keep unknown headers fail-closed.
assert hashlib.sha256(header.read_bytes()).hexdigest() in {
    '2cf2a7c3752cd6ab93f7c41140aaa2f3c1ae477cca6587925d6a5b51c3d683b9',
    'da2def2ce566f57929afe0a8a2f7de5539b17624eb37452d6928790ac6999336',
}
program=program.replace('"core/cpu.h"', '"'+str(header)+'"')
include=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
with tempfile.TemporaryDirectory(prefix='galaxypad-huffman-tail-') as directory:
    temp=Path(directory);(temp/'test.c').write_text(program)
    for flags in (['-O1','-fsanitize=address,undefined'],['-O2']):
        subprocess.run(['clang','-I',str(include),*flags,str(temp/'test.c'),'-o',str(temp/'test')],check=True)
        subprocess.run([str(temp/'test')],check=True)
