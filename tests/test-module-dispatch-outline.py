#!/usr/bin/env python3
"""Exercise actual emitted call semantics and module wrapper with adversarial hooks."""
import ast
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'ref/ModernGekko/vendor/dolphin'
emit=(CORE/'DolRecomp/src/backend/dispatch.c').read_text()
a=emit.index('    fprintf(out, "\\nstatic inline int dolrecomp_call_original')
b=emit.index('    fprintf(out, "\\nstatic inline DOLRECOMP_UNUSED int dolrecomp_run_blocks',a)
body=''.join(ast.literal_eval(m) for m in re.findall(r'fprintf\(out, ("(?:[^"\\]|\\.)*")\);',emit[a:b]))
module=(CORE/'module-template/module_export.c').read_text()
wrapper=module[module.index('#if defined(GALAXYPAD_OUTLINE_DISPATCH_SLOWPATH)'):module.index('static void chassis_on_state_loaded')]
program=r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
static unsigned mode,replacement,events;
static unsigned event_kind[16];static CPUState event_state[16];
static void note(CPUState* c,unsigned k){assert(events<16);event_kind[events]=k;event_state[events++]=*c;}
static bool second(CPUState* c,u32 a){note(c,4);c->gpr[10]^=a;return mode&1;}
static bool host(CPUState* c,u32 a){note(c,2);c->pc^=0x4321;c->gpr[8]++;
 if(mode&2)c->ram_size=0xffffffff; if(mode&4)c->ram_size=0;
 if(mode&8)c->host_call=NULL;if(mode&16)c->host_call=second;
 c->exception^=1;return mode&1;}
bool ppc_host_call(CPUState* c,u32 a){return c->host_call(c,a);}
static int dolrecomp_dispatch_replacement(CPUState* c,u32 a){
#ifdef DOLRECOMP_ENABLE_REPLACEMENTS
 note(c,1);c->cr^=a;if(replacement&2)c->host_call=host;
 return replacement==1||(replacement==3&&a>=GC_RAM_BASE);
#else
 return 0;
#endif
}
static void chunk(CPUState*c){note(c,3);c->gpr[3]++;c->pc=c->lr;c->downcount-=7;}
typedef void (*DolRecompFunction)(CPUState*);
static DolRecompFunction dolrecomp_find_original(u32 a){
 return (a>=0x80004000u&&a<0x80005000u&&!(a&3))?chunk:NULL;}
BODY
WRAPPER
int main(void){
 u32 addresses[]={0,1,0x4000,0x4001,0x4ffc,0x5000,0x7ffffffc,0x80004000,
 0x80004001,0x80004ffc,0x80005000,0x90004000,0xc0004000,0xffffffff};
 u32 sizes[]={0,0x4000,0x4001,0x1800000,0x80004001,0xffffffff};unsigned cases=0;
 for(mode=0;mode<32;mode++)for(replacement=0;replacement<4;replacement++)
 for(unsigned enabled=0;enabled<2;enabled++)for(unsigned s=0;s<6;s++)
 for(unsigned a=0;a<sizeof(addresses)/sizeof(*addresses);a++){
 CPUState c={0};c.ram_size=sizes[s];c.host_call=enabled?host:NULL;
 c.pc=0x12345678;c.lr=0x87654321;c.downcount=-77;CPUState initial=c;
 events=0;memset(event_state,0,sizeof event_state);memset(event_kind,0,sizeof event_kind);
 int expected=dolrecomp_call(&c,addresses[a]);CPUState final=c;unsigned n=events;
 CPUState saved[16];unsigned kinds[16];memcpy(saved,event_state,sizeof saved);memcpy(kinds,event_kind,sizeof kinds);
 c=initial;events=0;memset(event_state,0,sizeof event_state);memset(event_kind,0,sizeof event_kind);
 int actual=chassis_dispatch(&c,addresses[a]);assert(expected==actual);assert(!memcmp(&final,&c,sizeof c));
 assert(n==events&&!memcmp(saved,event_state,sizeof saved)&&!memcmp(kinds,event_kind,sizeof kinds));cases++;
 }
 printf("%u full-state/event-order comparisons passed\n",cases);
}
'''.replace('BODY',body).replace('WRAPPER',wrapper)
with tempfile.TemporaryDirectory(prefix='galaxypad-dispatch-outline-') as t:
 p=Path(t);(p/'test.c').write_text(program)
 for mode,flags in [('release',['-O2']),('sanitized',['-O1','-fsanitize=address,undefined'])]:
  for replacements in [False,True]:
   cmd=['clang','-std=c11',*flags,'-DGALAXYPAD_OUTLINE_DISPATCH_SLOWPATH=1','-I',str(CORE/'GXRuntime/include'),str(p/'test.c'),'-o',str(p/'test')]
   if replacements:cmd+=['-DDOLRECOMP_ENABLE_REPLACEMENTS=1']
   subprocess.run(cmd,check=True);subprocess.run([str(p/'test')],check=True)
