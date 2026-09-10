"""Offline, source-pinned MEM1 lookup guard experiment; no product edits."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
include = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
assert hashlib.sha256((include/'core/cpu.h').read_bytes()).hexdigest() == '7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'
source = r'''
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include "core/cpu.h"
__attribute__((noinline)) u8* reference(CPUState* c,u32 a,u32 s,u32* out) {
    return get_ram_ptr(c,a,s,out);
}
__attribute__((noinline)) u8* candidate(CPUState* c,u32 a,u32 s,u32* out) {
    u32 masked=a & ~0x40000000u;
    // Only skip MEM2 when its unsigned range predicate cannot match.
    // Preserve the original behavior for unusual sizes and overlap.
    if (masked < 0x90000000u && c->exram_size >= s && c->exram_size <= 0x10000000u) {
        u32 offset=masked-0x80000000u;
        if (offset <= c->ram_size-s) {
            if(out) *out=offset;
            return c->ram+offset;
        }
        return NULL;
    }
    return get_ram_ptr(c,a,s,out);
}
int main(void) {
    CPUState c={0};
    c.ram_size=0x1800000; c.exram_size=0x4000000;
    c.ram=malloc(c.ram_size); u8* exram=malloc(c.exram_size);
    assert(c.ram && exram);
    const u32 edges[]={0,0x7fffffffu,0x80000000u,0x817fffffu,0x81800000u,
      0x8fffffffu,0x90000000u,0x93ffffffu,0x94000000u,0xc0000000u,
      0xd0000000u,0xe0000000u,0xffffffffu};
    unsigned count=0; u32 random=123;
    for(unsigned mode=0;mode<2;mode++) {
      c.exram=mode?exram:NULL;
      for(u32 size=1;size<=8;size*=2) {
        for(unsigned i=0;i<200000;i++) {
          random=random*1664525u+1013904223u;
          u32 a=i<sizeof(edges)/sizeof(edges[0])?edges[i]:random;
          u32 left=0x1234,right=left;
          assert(reference(&c,a,size,&left)==candidate(&c,a,size,&right));
          assert(left==right);
          assert(reference(&c,a,size,NULL)==candidate(&c,a,size,NULL));
          count++;
        }
      }
    }
    free(c.ram);free(exram);
    printf("%u pointer/offset/null-output comparisons passed on initialized Wii layouts\n",count);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-mem1-lookup-') as directory:
    temp = Path(directory)
    (temp/'test.c').write_text(source)
    subprocess.run(['clang','-O2','-fsanitize=address,undefined','-I',str(include),
                    str(temp/'test.c'),'-o',str(temp/'test')],check=True)
    subprocess.run([str(temp/'test')],check=True)
    subprocess.run(['clang','-O2','-S','-I',str(include),str(temp/'test.c'),
                    '-o',str(temp/'test.s')],check=True)
    assembly=(temp/'test.s').read_text()
    for name,end in [('reference','candidate'),('candidate','main')]:
        block=assembly.split('_'+name+':',1)[1].split('_'+end+':',1)[0]
        print(name+' assembly:')
        print(block.split('.cfi_endproc',1)[0])
