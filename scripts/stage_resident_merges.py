"""Private real-DOL paired-merge region in an otherwise unchanged C chunk.

Build-time static assembly only. No normal builder selects this experiment.
"""
import hashlib
import importlib.util
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
START=0x804B651C
END=START+16

def build(source,directory,multiply=False,fma=False,lanes=False,long_region=False):
    start=0x804B64E0 if lanes else (0x804B6504 if fma else (START-4 if multiply else START))
    end=0x804B64F4 if lanes else (0x804B6514 if fma else END)
    if long_region: start,end=0x804B64E0,0x804B6514
    count=(end-start)//4
    assert hashlib.sha256(source.encode()).hexdigest()=='38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'
    dol=(ROOT/'generated/extracted/run1/sys/main.dol').read_bytes()
    assert hashlib.sha256(dol).hexdigest()=='2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09'
    sections=list(zip(struct.unpack_from('>18I',dol,0),struct.unpack_from('>18I',dol,0x48),
                      struct.unpack_from('>18I',dol,0x90)))
    matches=[s for s in sections if s[1]<=start and end<=s[1]+s[2]]
    assert len(matches)==1
    offset,address,_=matches[0]
    words=struct.unpack_from(f'>{count}I',dol,offset+start-address)
    if long_region:
        assert [(w>>1)&31 for w in words]==[30,13,28,25,14,11,25,30,10,25,25,30,25]
        assert [w>>26 for w in words]==[4]*6+[59]+[4]*6
    elif lanes:
        assert [(w>>1)&31 for w in words]==[30,13,28,25,14]
    elif fma:
        assert [(w>>1)&31 for w in words]==[25,25,30,25]
    else:
        assert [(w>>1)&1023 for w in words[-4:]]==[592,528,592,560]
        if multiply: assert ((words[0]>>1)&31)==25
    assert all(w>>26 in (4,59) and not w&1 for w in words)
    directory.mkdir()
    vendor=ROOT/'ref/ModernGekko/vendor/dolphin'
    if multiply or fma or lanes or long_region:
        helpers=vendor/'GXRuntime/src/core/cpu_interpreter_float.c'
        assert hashlib.sha256(helpers.read_bytes()).hexdigest()=='554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
    spec=importlib.util.spec_from_file_location('fpr_adapter',ROOT/'tests/adapt-arm64-fpr-cache.py')
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    reference=(vendor/'Source/Core/Core/PowerPC/JitArm64/JitArm64_RegCache.cpp').read_text()
    (directory/'cache.cpp').write_text(adapter.adapt(reference))
    flags=['-std=c++23','-O2','-arch','arm64','-mmacosx-version-min=14.0','-D_M_ARM_64=1',
           '-I'+str(ROOT/'tests/aot-support'),'-I'+str(ROOT/'tests'),
           '-I'+str(vendor/'GXRuntime/include'),'-I'+str(vendor/'Source/Core'),
           '-I'+str(vendor/'Externals/fmt/fmt/include'),
           '-include',str(ROOT/'tests/aot-cpu-fpr-layout.h')]
    commands=[['xcrun','clang++',*flags,str(ROOT/'tests/export-resident-merge-region.cpp'),
               str(vendor/'Source/Core/Common/Arm64Emitter.cpp'),str(directory/'cache.cpp'),
               '-o',str(directory/'export')]]
    subprocess.run(commands[-1],check=True)
    arguments=[f'{start:x}',*[f'{w:08x}' for w in words]]
    commands.append([str(directory/'export'),*arguments])
    assembly=subprocess.check_output(commands[-1],text=True)
    for invalid in [[arguments[0],'0',*arguments[2:]],['',*arguments[1:]],
                    [f'{START+1:x}',*arguments[1:]],['100000000',*arguments[1:]],
                    [arguments[0],'',*arguments[2:]]]:
        rejected=subprocess.run([str(directory/'export'),*invalid],capture_output=True)
        assert rejected.returncode==2 and not rejected.stdout
    (directory/'region.S').write_text(assembly)
    obj=directory/'region.o'
    commands.append(['xcrun','clang','-arch','arm64','-mmacosx-version-min=14.0','-c',
                     str(directory/'region.S'),'-o',str(obj)])
    subprocess.run(commands[-1],check=True)
    declarations=''.join(f'void galaxypad_resident_merge_{i}(CPUState*);\n' for i in range(count))
    replacement=''
    for i in range(count):
        pc=start+i*4
        replacement+=(f'label_{pc:08X}:\n    ctx->pc = 0x{pc:08X}u;\n'
                      f'    if (!ppc_fp_available_inline(ctx, 0x{pc:08X}u)) return;\n'
                      f'    galaxypad_resident_merge_{i}(ctx);\n    goto label_{end:08X};\n\n')
    begin=source.index(f'label_{start:08X}:')
    region_end=source.index(f'label_{end:08X}:')
    assert source.count('void func_804B60A0(CPUState* ctx)')==1
    assert source[begin:region_end].count('label_')==count
    text=source[:begin]+replacement+source[region_end:]
    text=text.replace('void func_804B60A0(CPUState* ctx)',declarations+'\nvoid func_804B60A0(CPUState* ctx)',1)
    return text,obj,dict(words=[f'{w:08x}' for w in words],start=start,end=end,
                         commands=commands,assembly_sha256=hashlib.sha256(assembly.encode()).hexdigest())
