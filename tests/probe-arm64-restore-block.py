#!/usr/bin/env python3
"""Private real-DOL lwz/blr export and complete-state differential gate.

Optional direct RAM loads and an isolated unsanitized block cost gate.
"""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import tempfile
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--direct-cpu',action='store_true')
parser.add_argument('--mixed',action='store_true')
parser.add_argument('--fast-load',action='store_true')
parser.add_argument('--benchmark',action='store_true')
args=parser.parse_args()
if args.fast_load and not args.direct_cpu:
    parser.error('--fast-load requires --direct-cpu')
root=Path(__file__).resolve().parents[1]
vendor=root/'ref/ModernGekko/vendor/dolphin'
chunk_address='803190A0' if args.mixed else '805170A0'
start=0x80319ab8 if args.mixed else 0x80517584
count=10 if args.mixed else 4
end=start+4*count
chunks=list((root/'generated/modules-scale-r387/RMGE01').glob(
    '*/dolrecomp-output/RMGE01_generated/chunks/*'+chunk_address+'.c'))
assert len(chunks)==1
source=chunks[0].read_text()
expected_hash=('34534c0a4f7fa9105f1a41c7f01a053dbf9fc9dc38d40ac79d0007ab8e7b766b' if args.mixed else
               '9b221ad3e1b417287e425640cc318e30fc5a6378e2956bf65a929be455acfd94')
assert hashlib.sha256(source.encode()).hexdigest()==expected_hash
dol=(root/'generated/extracted/run1/sys/main.dol').read_bytes()
assert hashlib.sha256(dol).hexdigest()=='2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09'
offsets=struct.unpack_from('>18I',dol,0)
addresses=struct.unpack_from('>18I',dol,0x48)
sizes=struct.unpack_from('>18I',dol,0x90)
sections=[(off,addr,size) for off,addr,size in zip(offsets,addresses,sizes)
          if addr<=start and end<=addr+size]
assert len(sections)==1
offset,address,size=sections[0]
words=struct.unpack_from('>'+str(count)+'I',dol,offset+start-address)
if args.mixed:
    assert [word>>26 for word in words]==[32,31,14,36,32,36,31,36,14,19]
else:
    for i,word in enumerate(words[:3]):
        assert word>>26==32 and (word>>21)&31==29+i and (word>>16)&31==11
        assert struct.unpack('>h',struct.pack('>H',word&0xffff))[0]==-12+i*4
assert words[-1]==0x4e800020
body=source.split(f'label_{start:08X}:',1)[1].split(f'label_{end:08X}:',1)[0]
body=f'label_{start:08X}:'+body
body=body.replace('goto return_dispatch_'+chunk_address+';','return;')
switch=[]
for entry in range(count):
    pc=start+entry*4
    exact=f'case 0x{pc:08X}u: ctx->downcount -= {count-entry}; goto label_{pc:08X};'
    assert exact in source
    switch.append(exact)
reference='static __attribute__((noinline)) void reference(CPUState* ctx) { switch(ctx->pc) {'+''.join(switch)+'default:std::abort();}\n'+body+'\n}\n'
flags=['-std=c++23','-O2','-arch','arm64','-mmacosx-version-min=14.0','-D_M_ARM_64=1',
       '-I'+str(root/'tests/aot-support'),'-I'+str(root/'tests'),
       '-I'+str(vendor/'GXRuntime/include'),'-I'+str(vendor/'Source/Core'),
       '-I'+str(vendor/'Externals/fmt/fmt/include')]
if args.direct_cpu:
    flags+=['-DAOT_DIRECT_CPU=1','-include',str(root/'tests/aot-cpu-gpr-layout.h')]
if args.mixed:
    flags+=['-DAOT_MIXED_BLOCK=1']
if args.fast_load:
    flags+=['-DAOT_FAST_LOAD=1']
def run(args,**kwargs):return subprocess.run(args,check=True,text=True,**kwargs)
with tempfile.TemporaryDirectory(prefix='galaxypad-aot-block-') as temporary:
    work=Path(temporary)
    (work/'restore-reference.inc').write_text(reference)
    run(['xcrun','clang++',*flags,str(root/'tests/export-arm64-restore-block.cpp'),
         str(vendor/'Source/Core/Common/Arm64Emitter.cpp'),
         str(vendor/'Source/Core/Core/PowerPC/JitArm64/JitArm64_RegCache.cpp'),'-o',str(work/'export')])
    arguments=[f'{start:08x}',*[f'{word:08x}' for word in words]]
    assembly=run([str(work/'export'),*arguments],capture_output=True).stdout
    rejected=subprocess.run([str(work/'export'),*arguments[:1],'0',*arguments[2:]],
                            capture_output=True,text=True)
    assert rejected.returncode==2 and not rejected.stdout
    (work/'block.S').write_text(assembly)
    run(['xcrun','clang','-arch','arm64','-mmacosx-version-min=14.0','-c',
         str(work/'block.S'),'-o',str(work/'block.o')])
    run(['xcrun','clang++',*flags,'-I'+str(work),'-fsanitize=address,undefined',
         str(root/'tests/arm64-restore-block-driver.cpp'),str(work/'block.o'),'-o',str(work/'driver')])
    result=run([str(work/'driver')],capture_output=True).stdout
    benchmark=None
    if args.benchmark:
        run(['xcrun','clang++',*flags,'-I'+str(work),
             str(root/'tests/arm64-restore-block-driver.cpp'),str(work/'block.o'),'-o',str(work/'bench')])
        benchmark=run([str(work/'bench'),'--benchmark'],capture_output=True).stdout
    print(json.dumps(dict(dol_sha256=hashlib.sha256(dol).hexdigest(),
                          source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                          words=[f'{word:08x}' for word in words],assembly=assembly,result=result,
                          direct_cpu=args.direct_cpu,
                          mixed=args.mixed,
                          fast_load=args.fast_load,
                          benchmark=benchmark,
                          scope='Actual integer block and all suffixes; GPR adapter only, no FP/CR/full backend/performance proof'),indent=2))
