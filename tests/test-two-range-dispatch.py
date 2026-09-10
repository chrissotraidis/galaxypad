"""Exact generated dispatch wrapper with adversarial callbacks and aliasing."""
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from two_range_lookup import transform,START
from psq_scale import reference_source
generated=root/'generated/modules-thp-r205/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-daa33a86eff05b70/dolrecomp-output/RMGE01_generated'
source=(generated/'RMGE01.h').read_text();changed=transform(source)
tables=source[source.index('#define DOLRECOMP_LOOKUP_RUNS'):source.index(START)]
names=re.findall(r'^    (func_[0-9A-F]+),$',tables,re.M)
assert len(names)==1322
def wrapper(text,prefix):
    body=text[text.index(START):text.index('static inline DOLRECOMP_UNUSED int dolrecomp_run_blocks')]
    for name in ('dolrecomp_find_original','dolrecomp_call_original','dolrecomp_physical_pc_alias','dolrecomp_call'):
        body=re.sub(r'\b'+name+r'\b',prefix+name,body)
    return body
stubs='\n'.join(f'static void {name}(CPUState* c) {{ observe(c,3,{i}u);c->gpr[3]={i}u;c->pc=c->lr;c->downcount-=7; }}' for i,name in enumerate(names))
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
cpu_reference=reference_source((core/'cpu.c').read_text())
assert hashlib.sha256((core.parent.parent/'include/core/cpu.h').read_bytes()).hexdigest()=='7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'
program=r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdio.h>
typedef void (*DolRecompFunction)(CPUState*);
#define DOLRECOMP_UNUSED
static CPUState cpu;
typedef struct { u32 kind,address;CPUState state; } Event;
static Event events[16];
static unsigned count,mode,replacement_mode,host_hits,alias_hits,chunk_hits;
static void observe(CPUState* c,u32 kind,u32 address) {
 assert(c==&cpu&&count<16);events[count].kind=kind;events[count].address=address;
 events[count++].state=*c;
 if(kind==2)host_hits++;
 if(kind==3)chunk_hits++;
 if(kind==2&&address>=0x80000000u)alias_hits++;
}
STUBS
TABLES
static bool second_host(CPUState* c,u32 address) {
 observe(c,4,address);c->gpr[9]^=address;return (mode&1)!=0;
}
static bool host(CPUState* c,u32 address) {
 observe(c,2,address);c->pc^=0x76543210u;c->gpr[8]++;
 if(mode&2)c->ram_size=0x01800000u;
 if(mode&4)c->ram_size=0;
 if(mode&8)c->host_call=NULL;
 if(mode&16)c->host_call=second_host;
 c->exception^=PPC_EXC_PROGRAM;
 return (mode&1)!=0;
}
static int dolrecomp_dispatch_replacement(CPUState* c,u32 address) {
 observe(c,1,address);
 if(replacement_mode&2)c->host_call=host;
 c->cr^=address;
 return replacement_mode==1||(replacement_mode==3&&address>=0x80000000u);
}
REFERENCE
CANDIDATE
int main(void) {
 const u32 addresses[]={0,1,0x4000,0x4001,0x64dc,0x64e0,0x70a0,0x52d27c,
  0x80004000u,0x80004001u,0x800064dcu,0x800064e0u,0x800070a0u,0x8052d27cu,
  0x8052d280u,0x90000000u,0xc0004000u,0xffffffffu};
 const u32 sizes[]={0,0x4000,0x4001,0x01800000u,0x80004001u,0xffffffffu};
 unsigned cases=0;
 for(mode=0;mode<32;mode++)for(replacement_mode=0;replacement_mode<4;replacement_mode++)
 for(unsigned enabled=0;enabled<2;enabled++)for(unsigned size=0;size<6;size++)
 for(unsigned a=0;a<sizeof(addresses)/sizeof(*addresses);a++) {
  CPUState initial={0};initial.ram_size=sizes[size];initial.host_call=enabled?host:NULL;
  initial.pc=0x87654321u;initial.lr=0x12345678u;initial.downcount=-123;
  cpu=initial;count=0;memset(events,0,sizeof events);
  int expected=reference_dolrecomp_call(&cpu,addresses[a]);
  CPUState final=cpu;Event trace[16];memcpy(trace,events,sizeof trace);unsigned n=count;
  cpu=initial;count=0;memset(events,0,sizeof events);
  int actual=candidate_dolrecomp_call(&cpu,addresses[a]);
  assert(actual==expected&&!memcmp(&cpu,&final,sizeof cpu));
  assert(n==count&&!memcmp(events,trace,sizeof events));cases++;
 }
 assert(host_hits&&alias_hits&&chunk_hits);
 printf("%u complete dispatch CPU/event-order comparisons pass; host=%u virtual/alias=%u chunk=%u\n",
        cases,host_hits,alias_hits,chunk_hits);
}
'''.replace('STUBS',stubs).replace('TABLES',tables).replace('REFERENCE',wrapper(source,'reference_')).replace('CANDIDATE',wrapper(changed,'candidate_'))
with tempfile.TemporaryDirectory(prefix='galaxypad-dispatch-oracle-') as temporary:
    directory=Path(temporary);harness=directory/'probe.c';harness.write_text(program)
    (directory/'cpu.c').write_text(cpu_reference)
    for name,flags in [('sanitized',['-O1','-fsanitize=address,undefined']),('optimized',['-O2'])]:
        binary=directory/name
        subprocess.run(['clang','-std=c11',*flags,'-ffunction-sections','-fdata-sections',
                        '-I',str(core.parent.parent/'include'),str(harness),str(directory/'cpu.c'),
                        '-Wl,-dead_strip','-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
