"""Private exact-DOL sampled-chunk emission audit, not execution or FPS proof.

All generated code/objects remain in ignored generated/. No game bytes are
embedded in this script. Reuses the R439 staged public emitter build.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shlex
import struct
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('dol',type=Path)
p.add_argument('output',type=Path)
p.add_argument('--probe',type=Path,default=root/'generated/llvm-arm64-probe-r439-fixed')
args=p.parse_args()
data=args.dol.read_bytes()
identity=hashlib.sha256(data).hexdigest()
assert identity=='2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09'
out=args.output.resolve()
assert out.is_relative_to(root/'generated')
out.mkdir(parents=True,exist_ok=False)
address=0x804b60a0;count=1024
offsets=struct.unpack_from('>18I',data,0)
addresses=struct.unpack_from('>18I',data,0x48)
sizes=struct.unpack_from('>18I',data,0x90)
matches=[off+address-base for off,base,size in zip(offsets,addresses,sizes)
         if base<=address and address+count*4<=base+size]
assert len(matches)==1
(out/'words.bin').write_bytes(data[matches[0]:matches[0]+count*4])
probe=args.probe.resolve()
src=probe/'staged/src';build=probe/'build'
driver=r'''
extern "C" {
#include "backend/emitter.h"
}
#include "backend/llvm/llvm_backend.h"
#include "ir/dolir_builder.h"
#include <cassert>
int main(int argc,char**argv) {
 assert(argc==5);FILE* input=fopen(argv[1],"rb");assert(input);
 PPCInst insts[1024];unsigned unknown=0;
 for(unsigned i=0;i<1024;i++) {
   unsigned char bytes[4];assert(fread(bytes,1,4,input)==4);
   u32 word=((u32)bytes[0]<<24)|((u32)bytes[1]<<16)|((u32)bytes[2]<<8)|bytes[3];
   insts[i]=ppc_decode(word,0x804b60a0u+i*4);
   if(insts[i].op==PPC_OP_UNKNOWN) unknown++;
 }
 fclose(input);fprintf(stderr,"instructions=1024 unknown=%u\n",unknown);
 assert(unknown==0);
 FILE* c=fopen(argv[2],"w");assert(c);
 emit_header_for_cpu(c,DOLRECOMP_CPU_BROADWAY);emit_set_chunk_table(nullptr,0);
 assert(emit_function(c,insts,1024,0x804b60a0u));emit_footer(c);fclose(c);
 DolIRModule module;dolir_module_init(&module);
 assert(dolir_build_chunk(&module,insts,1024,0x804b60a0u));
 DolLLVMOptions options{};options.optimization_level=2;options.verify=1;
 options.emit_ir=1;options.ir_path=argv[4];
 assert(dolllvm_emit_object(&module,argv[3],&options,stderr));
 dolir_module_free(&module);
}
'''
(out/'driver.cpp').write_text(driver)
llvm=Path('/opt/homebrew/opt/llvm@20')
libs=shlex.split(subprocess.check_output([str(llvm/'bin/llvm-config'),'--link-shared','--ldflags','--libs','--system-libs'],text=True))
subprocess.run(['clang++','-std=c++17','-I'+str(src),str(out/'driver.cpp'),
 *[str(build/('lib'+lib+'.a')) for lib in ('dr_backend','dr_llvm','dr_ir','dr_frontend')],
 *libs,'-lz','-Wl,-rpath,'+str(llvm/'lib'),'-o',str(out/'emit')],check=True)
env=os.environ.copy();env['GALAXYPAD_LLVM_ARM64_PROBE']='1'
subprocess.run([str(out/'emit'),str(out/'words.bin'),str(out/'chunk.c'),str(out/'ir.o'),str(out/'ir.ll')],env=env,check=True)
runtime=root/'ref/ModernGekko/vendor/dolphin/GXRuntime'
subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
 '-DDOLRECOMP_CPU_HEADER="core/cpu.h"','-I'+str(src),'-I'+str(runtime/'include'),
 '-Dfunc_804B60A0=c_func_804B60A0','-c',str(out/'chunk.c'),'-o',str(out/'c.o')],check=True)
for name in ('c','ir'):
    asm=subprocess.check_output([str(llvm/'bin/llvm-objdump'),'--disassemble',str(out/(name+'.o'))],text=True)
    (out/(name+'.asm')).write_text(asm)
profile=json.loads((root/'generated/runtime/late-good-egg-r422/summary.json').read_text())
row=next(r for r in profile['leaves'] if r['name']=='func_804B60A0')
report={'dol_sha256':identity,'guest_start':hex(address),'instructions':count,
 'profile_leaf_samples':row['samples'],'profile_total_samples':profile['samples'],
 'probe_provenance_sha256':hashlib.sha256((probe/'staged/probe-provenance.json').read_bytes()).hexdigest(),
 'objects':{n:{'bytes':(out/(n+'.o')).stat().st_size,'sha256':hashlib.sha256((out/(n+'.o')).read_bytes()).hexdigest()} for n in ('c','ir')},
 'boundary':'Exact sampled chunk emission only. No PGO/LTO or installed compiler-policy parity; no runtime fixture, speed or gameplay acceptance.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
