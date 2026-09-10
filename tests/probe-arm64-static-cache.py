#!/usr/bin/env python3
"""Execute statically linked reference GPR-cache emission across a mutable callback."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
vendor=root/'ref/ModernGekko/vendor/dolphin'
common=vendor/'Source/Core/Common/Arm64Emitter.cpp'
cache=vendor/'Source/Core/Core/PowerPC/JitArm64/JitArm64_RegCache.cpp'
flags=['-std=c++23','-O2','-arch','arm64','-mmacosx-version-min=14.0',
       '-D_M_ARM_64=1','-I'+str(root/'tests/aot-support'),
       '-I'+str(vendor/'GXRuntime/include'),
       '-I'+str(vendor/'Source/Core'),'-I'+str(vendor/'Externals/fmt/fmt/include')]
def run(args,**kwargs):
    return subprocess.run(args,check=True,text=True,**kwargs)
with tempfile.TemporaryDirectory(prefix='galaxypad-aot-cache-') as temporary:
    work=Path(temporary)
    run(['xcrun','clang++',*flags,str(root/'tests/export-arm64-cache-probe.cpp'),
         str(common),str(cache),'-o',str(work/'export')])
    assembly=run([str(work/'export')],capture_output=True).stdout
    (work/'probe.S').write_text(assembly)
    run(['xcrun','clang','-arch','arm64','-mmacosx-version-min=14.0','-c',
         str(work/'probe.S'),'-o',str(work/'probe.o')])
    run(['xcrun','clang++',*flags,str(root/'tests/arm64-cache-probe-driver.cpp'),
         str(work/'probe.o'),'-o',str(work/'driver')])
    result=run([str(work/'driver')],capture_output=True).stdout
    print(json.dumps(dict(reference_cache_sha256=hashlib.sha256(cache.read_bytes()).hexdigest(),
                          assembly=assembly,result=result,
                          scope='GPR cache transport only; no PPC decoding, FP, memory access, cycles or CPUState adapter'),indent=2))
