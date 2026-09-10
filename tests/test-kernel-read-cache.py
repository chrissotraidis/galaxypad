"""Offline cached-read parity and exact transform scope/invalidation checks."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from cache_kernel_reads import HELPERS, transform
source = (root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed = transform(source)
signature = 'void func_804520A0(CPUState* ctx) {'
assert changed.split(signature, 1)[1] == source.split(signature, 1)[1]
body = changed.split(signature, 1)[0]
assert len(re.findall(r'\b(?:mem_write\d+|ppc_psq_store_inline)\(ctx,', body)) == 94
assert body.count('map.valid = false;') == 94
assert len(re.findall(r'map.valid = false;\s+(?:mem_write\d+|ppc_psq_store_inline)\(ctx,', body)) == 94
try:
    transform(source+'\n')
except ValueError:
    pass
else:
    raise AssertionError('Changed source accepted')

program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <stddef.h>
HELPERS
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
static u8 ram0[64],ram1[64],ex0[64],ex1[64];
static u64 remap(CPUState* c,u32 address,u8 size) {
    c->ram=c->ram==ram0?ram1:ram0;
    c->exram=c->exram==ex0?ex1:ex0;
    c->ram_size=c->ram_size==64?32:64;
    c->exram_size=c->exram_size==64?32:64;
    return 0xabcdef1234567890ull ^ address ^ size;
}
int main(void) {
 for(unsigned i=0;i<64;i++) {ram0[i]=i;ram1[i]=255-i;ex0[i]=i+65;ex1[i]=i+130;}
 CPUState a={0}; a.ram=ram0;a.ram_size=64;a.exram=ex0;a.exram_size=64;a.external_read=remap;
 CPUState b=a; GalaxyKernelMap map={0}; unsigned cases=0;
 const u32 bases[]={0x80000000,0xc0000000,0x90000000,0xd0000000,0xe0000000,0};
 for(unsigned pass=0;pass<50;pass++) for(unsigned bits=0;bits<4;bits++)
 for(unsigned base=0;base<6;base++) for(unsigned off=0;off<70;off++) {
    u32 address=bases[base]+off;u32 size=1u<<bits;u64 expected,actual;
    if(size==1) expected=mem_read8(&a,address);
    else if(size==2) expected=mem_read16(&a,address);
    else if(size==4) expected=mem_read32(&a,address);
    else expected=mem_read64(&a,address);
    actual=galaxy_kernel_read(&b,&map,address,size);
    if(size==1) actual=(u8)actual;
    if(size==2) actual=(u16)actual;
    if(size==4) actual=(u32)actual;
    assert(expected==actual && !memcmp(&a,&b,sizeof a));cases++;
 }
 // A generated store invalidates before it executes; the next read must resnapshot.
 a.ram=ram0; b.ram=ram0; a.ram_size=b.ram_size=64;
 map.valid=false; (void)galaxy_kernel_read(&b,&map,0x80000000,4);
 a.ram=b.ram=ram1; map.valid=false;
 assert(mem_read32(&a,0x80000000)==galaxy_kernel_read(&b,&map,0x80000000,4));
 // RAM may alias CPUState: a store can change the mapping descriptor itself.
 a.ram=(u8*)&a;b.ram=(u8*)&b;a.ram_size=b.ram_size=sizeof(CPUState);
 map.valid=false;(void)galaxy_kernel_read(&b,&map,0x80000000,4);
 u8* destination=ram0;u64 value=read_be64((u8*)&destination);
 mem_write64(&a,0x80000000u+offsetof(CPUState,ram),value);
 map.valid=false;mem_write64(&b,0x80000000u+offsetof(CPUState,ram),value);
 assert(a.ram==ram0 && b.ram==ram0);
 assert(mem_read32(&a,0x80000000)==galaxy_kernel_read(&b,&map,0x80000000,4));
 printf("%u cached-read cases: widths, boundaries, mirrors, callback pointer/size remaps pass\n",cases);
}
'''.replace('HELPERS', HELPERS)
with tempfile.TemporaryDirectory(prefix='galaxypad-kernel-cache-') as directory:
    path=Path(directory);(path/'test.c').write_text(program)
    subprocess.run(['clang','-O2','-std=c11','-fsanitize=address,undefined',
                    '-I',str(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'),
                    str(path/'test.c'),'-o',str(path/'test')],check=True)
    subprocess.run([str(path/'test')],check=True)
