"""Differential check of an isolated cache-line clear; never builds the app."""
import hashlib
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--loop', action='store_true')
args = parser.parse_args()

root = Path(__file__).resolve().parents[1]
include = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
assert hashlib.sha256((include/'core/cpu.h').read_bytes()).hexdigest() == '7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'
program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
static CPUState cpu;
static u8 ram[512], exram[512], replacement[512];
static unsigned events, digest, mutate;
static void journal(u32 offset,u32 size,void* user) {
    assert(user == &cpu); ++events;
    digest = digest * 33u + offset + size + ram[offset];
    if (mutate) {cpu.ram=replacement;cpu.reserve_valid=true;cpu.reserve_addr=0x80000000u;}
}
static void external(CPUState* c,u32 ea,u64 value,u8 size) {
    assert(c==&cpu && value==0 && size==4); ++events;
    digest=digest*33u+ea+size;
    if(mutate) {c->ram=replacement;c->ram_size=512;c->reserve_valid=true;}
}
static void reference(CPUState* c,u32 address) {
    u32 ea=address&~31u;
    for(u32 i=0;i<32;i+=4) mem_write32(c,ea+i,0);
}
''' + (root/('patches/experiments/dcbz-ram-loop.inc' if args.loop else 'patches/experiments/dcbz-ram-line.inc')).read_text() + r'''
typedef struct { CPUState state;u8 a[512],b[512],c[512];unsigned events,digest;} Result;
static Result run(unsigned variant,unsigned mode,u32 address,unsigned size,unsigned seed) {
    memset(&cpu,0,sizeof(cpu));
    for(unsigned i=0;i<512;i++) ram[i]=exram[i]=replacement[i]=(u8)(i*17+seed);
    cpu.ram=ram;cpu.ram_size=size;cpu.exram=exram;cpu.exram_size=size;
    cpu.reserve_addr=(seed&1)?address:(address^0x40000000u);cpu.reserve_valid=seed&2;
    cpu.external_write=external;mutate=mode&1;events=digest=0;
    g_mem_write_journal=(mode&2)?journal:NULL;g_mem_write_journal_user=&cpu;
    if(mode&4) cpu.exram=NULL;
    if(variant) galaxypad_dcbz_ram_line(&cpu,address);else reference(&cpu,address);
    Result result={0};result.state=cpu;
    memcpy(result.a,ram,512);memcpy(result.b,exram,512);memcpy(result.c,replacement,512);
    result.events=events;result.digest=digest;return result;
}
int main(void) {
    const u32 bases[]={0x80000000u,0xc0000000u,0x90000000u,0xd0000000u,0xe0000000u,0xffffffe0u};
    const unsigned sizes[]={32,64,128,256,512};
    unsigned cases=0;
    for(unsigned mode=0;mode<8;mode++)for(unsigned b=0;b<6;b++)
      for(unsigned s=0;s<5;s++)for(unsigned offset=0;offset<544;offset+=7) {
        u32 address=bases[b]+offset;
        Result a=run(0,mode,address,sizes[s],offset),bresult=run(1,mode,address,sizes[s],offset);
        assert(memcmp(&a,&bresult,sizeof(a))==0);++cases;
      }
    /* RAM may alias CPUState. Do not fold stores that change guest registers,
     * pc, or reservation fields; the original store order remains visible. */
    for(unsigned offset=0;offset<640;offset+=32) {
        CPUState result[2];
        for(unsigned variant=0;variant<2;variant++) {
            memset(&cpu,0,sizeof(cpu));cpu.ram=(u8*)&cpu;cpu.ram_size=sizeof(cpu);
            cpu.reserve_valid=true;cpu.reserve_addr=0x80000000u+offset;
            cpu.pc=0x804534c8;cpu.gpr[3]=42;g_mem_write_journal=NULL;
            if(variant)galaxypad_dcbz_ram_line(&cpu,0x80000000u+offset);
            else reference(&cpu,0x80000000u+offset);
            result[variant]=cpu;
        }
        assert(memcmp(result,result+1,sizeof(cpu))==0);++cases;
    }
    printf("dcbz full-state/memory/callback comparisons: %u passed\n",cases);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-dcbz-') as temp:
    source = Path(temp)/'probe.c'
    source.write_text(program)
    for name, flags in [('sanitized', ['-O1', '-fsanitize=address,undefined']), ('optimized', ['-O2'])]:
        binary = Path(temp)/name
        subprocess.run(['clang', '-I'+str(include), *flags, str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
