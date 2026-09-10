"""Actual module export + saved PGO/ThinLTO; opaque synthetic guest callees."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from two_range_lookup import transform
spec=importlib.util.spec_from_file_location('graph_builder',root/'scripts/build-dc-column-experiment.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
module=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(module)=='1180447313459c4c153ca74e5215811e88a9b69a00d15feff940f062148fc631'
generated=module.parent/'dolrecomp-output/RMGE01_generated';build=module.parent/'module-build'
original=(generated/'RMGE01.h').read_text();candidate=transform(original)
export=root/'ref/ModernGekko/vendor/dolphin/module-template/module_export.c'
assert sha(export)=='1e3efee3cf6384a245da1f03a4163098fcb68e7acf615fa86f566d34fc7efd41'
rows=builder.parse_graph((build/'build.ninja').read_text())
fields=[r[3] for r in rows if r[0]=='CMakeFiles/gRMGE01_recomp.dir/module_export.c.o'][0]
flags=shlex.split(' '.join(fields[k] for k in ('DEFINES','INCLUDES','FLAGS')))
assert '-flto=thin' in flags and flags[-3:]==['-O2','-ffp-contract=off','-fno-fast-math']
profile=root/'generated/pgo/rmge01.profdata'
assert sha(profile)=='f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'
assert '-fprofile-instr-use='+str(profile) in flags
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
names=re.findall(r'^    (func_[0-9A-F]+),$',original,re.M);assert len(names)==1322
stubs='\n'.join(f'void {name}(CPUState* c) {{c->gpr[1]={i}u;c->gpr[2]++;c->pc=c->lr;c->downcount-=3;}}' for i,name in enumerate(names))
program=r'''
#include "StaticRecompABI.h"
#include <assert.h>
#include <stdio.h>
#include <time.h>
STUBS
extern const StaticRecompModuleDesc* staticrecomp_get_module(void);
static unsigned host_mode;
static bool host(CPUState* c,u32 address) { c->gpr[7]^=address;return host_mode==3; }
static uint64_t now(void) {struct timespec t;assert(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t)==0);return (uint64_t)t.tv_sec*1000000000ull+t.tv_nsec;}
int main(void) {
 const StaticRecompModuleDesc* desc=staticrecomp_get_module();
 assert(desc->cpu_state_size==sizeof(CPUState));
 for(unsigned mode=0;mode<6;mode++) {
  CPUState c={0};c.ram_size=0x01800000;c.lr=0x12345678;
  c.host_call=mode>=3?host:NULL;host_mode=mode;
  unsigned hits=0;uint64_t start=now();
  for(unsigned i=0;i<5000000;i++) {
   unsigned chunk=i%1322;
   u32 address=chunk<3?0x80004000u+chunk*4096:0x800070a0u+(chunk-3)*4096;
   address+=(i&31)*4;
   if(mode==1)address&=0x7fffffffu;
   if(mode==2&&i%2)address|=1;
   if(mode==5)address=0x80517538u;
   hits+=desc->dispatch(&c,address);
  }
  uint64_t elapsed=now()-start;
  assert(hits==(mode==2?2500000u:5000000u));
  printf("{\"mode\":%u,\"ns_per_dispatch\":%.6f,\"hits\":%u,\"chunk_calls\":%u}\n",mode,(double)elapsed/5000000,hits,c.gpr[2]);
 }
}
'''.replace('STUBS',stubs)
with tempfile.TemporaryDirectory(prefix='galaxypad-dispatch-bench-') as temporary:
    temp=Path(temporary);harness=temp/'harness.c';harness.write_text(program)
    native=temp/'harness.o'
    includes=shlex.split(fields['INCLUDES'])
    subprocess.run(['/usr/bin/clang','-O2','-std=gnu11','-arch','arm64','-mmacosx-version-min=14.0',*includes,'-c',str(harness),'-o',str(native)],check=True)
    binaries={}
    for name,header in [('control',original),('candidate',candidate)]:
        directory=temp/name;directory.mkdir()
        (directory/'RMGE01.h').write_text(header)
        (directory/'generated.h').write_text('#include "RMGE01.h"\n')
        obj=directory/'export.o';binary=directory/'probe'
        command=['/usr/bin/clang','-I'+str(directory),*flags,'-c',str(export),'-o',str(obj)]
        print(json.dumps({'variant':name,'compile':command}),flush=True)
        subprocess.run(command,check=True)
        subprocess.run(['/usr/bin/clang',*flags,str(native),str(obj),str(core/'cpu.c'),str(core/'cpu_interpreter_float.c'),
                        '-Wl,-dead_strip','-o',str(binary)],check=True)
        subprocess.run(['xcrun','size',str(binary)],check=True)
        binaries[name]=binary
    for name in ('control','candidate','candidate','control'):
        output=subprocess.check_output([str(binaries[name])],text=True)
        print(json.dumps({'variant':name,'rows':[json.loads(line) for line in output.splitlines()]}),flush=True)
