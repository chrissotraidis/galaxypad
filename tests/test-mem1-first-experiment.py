#!/usr/bin/env python3
"""Differentially test actual memory helpers with one resolver-order change.

Separate TUs use original/candidate cpu.h. This validates initialized mapping
windows, not arbitrary invalid pointers or uninitialized CPUState fields.
No game/module/app build or selection occurs.
"""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('experiment', root/'scripts/create-mem1-first-experiment.py')
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)
include = experiment.SOURCE/'include'
wrapper = r'''
#include "core/cpu.h"
#define JOIN_(a,b) a##b
#define JOIN(a,b) JOIN_(a,b)
u8* JOIN(PREFIX,_map)(CPUState* c,u32 a,u32 s,u32* out) {return get_ram_ptr(c,a,s,out);}
u64 JOIN(PREFIX,_read)(CPUState* c,u32 a,u32 s) {
 switch(s) {case 1:return mem_read8(c,a);case 2:return mem_read16(c,a);
 case 4:return mem_read32(c,a);case 8:return mem_read64(c,a);default:__builtin_trap();}
}
void JOIN(PREFIX,_write)(CPUState* c,u32 a,u32 s,u64 v) {
 switch(s) {case 1:mem_write8(c,a,v);break;case 2:mem_write16(c,a,v);break;
 case 4:mem_write32(c,a,v);break;case 8:mem_write64(c,a,v);break;default:__builtin_trap();}
}
'''
host = r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdio.h>
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
u8* ref_map(CPUState*,u32,u32,u32*);u8* candidate_map(CPUState*,u32,u32,u32*);
u64 ref_read(CPUState*,u32,u32);u64 candidate_read(CPUState*,u32,u32);
void ref_write(CPUState*,u32,u32,u64);void candidate_write(CPUState*,u32,u32,u64);
typedef struct {u8 ram[4096],new_ram[4096],exram[4096];u64 events;CPUState* cpu;} Trace;
static u32 rng=0x129a;
static u32 random32(void) {rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static void mutate(CPUState* c,u32 a,u64 v,u32 width) {
 Trace* t=c->external_user_data;
 t->events=t->events*131+a+v+width;
 c->ram=t->new_ram;c->ram_size=256;c->exram_size=256;
 c->gpr[11]^=a;c->reserve_valid=true;c->reserve_addr=0x80000000;
}
static u64 external_read(CPUState* c,u32 a,u8 w) {mutate(c,a,0,w);return 0x1234567887654321ull;}
static void external_write(CPUState* c,u32 a,u64 v,u8 w) {mutate(c,a,v,w);}
static void journal(u32 a,u32 w,void* user) {CPUState* c=user;mutate(c,a,0,w);}
static void initialize(CPUState* c,Trace* t) {
 memset(c,0,sizeof(*c));memset(t,0,sizeof(*t));t->cpu=c;
 for(unsigned i=0;i<4096;i++){t->ram[i]=i*3;t->new_ram[i]=i*7;t->exram[i]=i*13;}
 c->ram=t->ram;c->ram_size=4096;c->exram=t->exram;c->exram_size=4096;
 c->external_user_data=t;c->external_read=external_read;c->external_write=external_write;
}
static void equal(CPUState a,CPUState b,Trace* x,Trace* y) {
 assert((a.ram==x->ram)==(b.ram==y->ram));
 assert((a.ram==x->new_ram)==(b.ram==y->new_ram));
 assert((a.exram==x->exram)==(b.exram==y->exram));
 a.ram=b.ram=NULL;a.exram=b.exram=NULL;a.external_user_data=b.external_user_data=NULL;
 assert(memcmp(&a,&b,sizeof(a))==0);assert(x->events==y->events);
 assert(memcmp(x->ram,y->ram,sizeof(x->ram))==0);
 assert(memcmp(x->new_ram,y->new_ram,sizeof(x->new_ram))==0);
 assert(memcmp(x->exram,y->exram,sizeof(x->exram))==0);
}
int main(void) {
 CPUState a,b;Trace x,y;initialize(&a,&x);
 const u32 edges[]={0,0x7fffffff,0x80000000,0x80000ff8,0x80000ffc,0x80000fff,
 0x80001000,0x8fffffff,0x90000000,0x90000ff8,0x90000fff,0x90001000,
 0xbfffffff,0xc0000000,0xc0000fff,0xd0000000,0xd0000fff,0xe0000000,0xffffffff};
 unsigned maps=0;
 for(unsigned mode=0;mode<3;mode++) {
  a.exram=mode==0?NULL:mode==1?x.exram:x.ram;
  a.exram_size=mode==0?0:4096;
  for(u32 width=1;width<=8;width*=2) for(unsigned i=0;i<100000;i++) {
   u32 addr=i<sizeof(edges)/sizeof(edges[0])?edges[i]:random32();
   if(i%3==0)addr=(i&1?0x80000000u:0x90000000u)+(addr&8191);
   u32 l=0xabcdef,r=l;
   assert(ref_map(&a,addr,width,&l)==candidate_map(&a,addr,width,&r));assert(l==r);
   assert(ref_map(&a,addr,width,NULL)==candidate_map(&a,addr,width,NULL));maps++;
  }
 }
 // Overlapping declared guest windows: MEM2 must still win. Allocate the
 // large MEM1 virtually and touch no pages in it; both returned pointers are
 // within allocated objects, so this does not rely on invalid pointer math.
 u8* large=malloc(0x10001000u);assert(large);a.ram=large;a.ram_size=0x10001000u;
 a.exram=x.exram;a.exram_size=4096;
 for(u32 w=1;w<=8;w*=2)for(u32 off=0;off<4096;off++) {
  u32 l=17,r=17;u32 addr=0x90000000u+off;
  assert(ref_map(&a,addr,w,&l)==candidate_map(&a,addr,w,&r));assert(l==r);
 }
 free(large);
 unsigned scenarios=0;
 for(u32 width=1;width<=8;width*=2)for(unsigned mode=0;mode<6;mode++) {
  initialize(&a,&x);initialize(&b,&y);
  a.reserve_valid=b.reserve_valid=true;a.reserve_addr=b.reserve_addr=0xc0000000;
  u32 addr=mode<2?0x80000000u:mode<4?0x90000000u:0xe0000000u;
  if(mode==1){a.exram=x.ram;b.exram=y.ram;}
  g_mem_write_journal=mode==0?journal:NULL;
  g_mem_write_journal_user=&a;ref_write(&a,addr,width,0x1234567887654321ull);
  g_mem_write_journal_user=&b;candidate_write(&b,addr,width,0x1234567887654321ull);
  equal(a,b,&x,&y);
  g_mem_write_journal=NULL;
  // External callbacks change both pointers and dimensions. Subsequent reads
  // must observe the remap, including the now-unmapped 0x80000300 address.
  assert(ref_read(&a,0xe0000000,width)==candidate_read(&b,0xe0000000,width));
  assert(ref_read(&a,0x80000000,width)==candidate_read(&b,0x80000000,width));
  assert(ref_read(&a,0x80000300,width)==candidate_read(&b,0x80000300,width));
  ref_write(&a,0xc0000000,width,19);candidate_write(&b,0xc0000000,width,19);
  equal(a,b,&x,&y);scenarios++;
 }
 // Guest RAM may alias CPUState. A mapped write clears EXRAM's pointer, and
 // the very next operation must use the live metadata and external callback.
 initialize(&a,&x);initialize(&b,&y);a.ram=(u8*)&a;b.ram=(u8*)&b;
 a.ram_size=b.ram_size=sizeof(CPUState);
 ref_write(&a,0x80000000u+offsetof(CPUState,exram),8,0);
 candidate_write(&b,0x80000000u+offsetof(CPUState,exram),8,0);
 assert(!a.exram&&!b.exram);
 assert(ref_read(&a,0x90000000,4)==candidate_read(&b,0x90000000,4));
 equal(a,b,&x,&y);
 printf("%u initialized mapping comparisons, overlapping precedence, %u mutation scenarios and CPUState alias pass\n",maps,scenarios);
}
'''

with tempfile.TemporaryDirectory(prefix='galaxypad-mem1-first-') as temporary:
    out = Path(temporary)
    candidate_include = out/'candidate-include'
    shutil.copytree(include, candidate_include)
    original = (include/'core/cpu.h').read_text()
    (candidate_include/'core/cpu.h').write_text(original.replace(experiment.body(original), experiment.CANDIDATE))
    (out/'wrapper.c').write_text(wrapper)
    (out/'host.c').write_text(host)
    for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-fsanitize=address,undefined'])]:
        objects=[]
        for prefix,headers in [('ref',include),('candidate',candidate_include)]:
            obj=out/(name+'-'+prefix+'.o');objects.append(str(obj))
            subprocess.run(['clang',*flags,'-I'+str(headers),'-DPREFIX='+prefix,
                            '-c',str(out/'wrapper.c'),'-o',str(obj)],check=True)
        binary=out/name
        subprocess.run(['clang',*flags,'-I'+str(include),str(out/'host.c'),*objects,
                        '-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True,timeout=30)
print('Original-helper and MEM1-first precedence differential checks pass')
