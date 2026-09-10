#!/usr/bin/env python3
"""Private split-lane reference FP cache transport, not FP arithmetic proof."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--exact-conversion',action='store_true')
parser.add_argument('--paired-merges',action='store_true',
                    help='Exercise resident paired-lane merge values; no guest entry/cycle proof')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
vendor=root/'ref/ModernGekko/vendor/dolphin'
cache=vendor/'Source/Core/Core/PowerPC/JitArm64/JitArm64_RegCache.cpp'
spec=importlib.util.spec_from_file_location('adapter',root/'tests/adapt-arm64-fpr-cache.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
flags=['-std=c++23','-O2','-arch','arm64','-mmacosx-version-min=14.0','-D_M_ARM_64=1',
       '-I'+str(root/'tests/aot-support'),'-I'+str(root/'tests'),
       '-I'+str(vendor/'GXRuntime/include'),'-I'+str(vendor/'Source/Core'),
       '-I'+str(vendor/'Externals/fmt/fmt/include'),
       '-include',str(root/'tests/aot-cpu-fpr-layout.h')]
if args.exact_conversion:flags+=['-DAOT_EXACT_FP=1']
if args.paired_merges:flags+=['-DAOT_PAIRED_MERGES=1']
def run(args,**kw):return subprocess.run(args,check=True,text=True,**kw)
with tempfile.TemporaryDirectory(prefix='galaxypad-fpr-cache-') as directory:
    work=Path(directory)
    source=cache.read_text()
    try:
        adapter.adapt(source+'\n')
    except AssertionError:
        pass
    else:
        raise AssertionError('Changed cache source accepted')
    adapted=adapter.adapt(source);(work/'cache.cpp').write_text(adapted)
    run(['xcrun','clang++',*flags,str(root/'tests/export-arm64-fpr-probe.cpp'),
         str(vendor/'Source/Core/Common/Arm64Emitter.cpp'),str(work/'cache.cpp'),'-o',str(work/'export')])
    assembly=run([str(work/'export')],capture_output=True).stdout
    (work/'probe.S').write_text(assembly)
    run(['xcrun','clang','-arch','arm64','-mmacosx-version-min=14.0','-c',str(work/'probe.S'),'-o',str(work/'probe.o')])
    run(['xcrun','clang++',*flags,'-fsanitize=address,undefined',
         str(root/'tests/arm64-fpr-probe-driver.cpp'),str(work/'probe.o'),'-o',str(work/'driver')])
    result=run([str(work/'driver')],capture_output=True).stdout
    print(json.dumps(dict(reference_sha256=hashlib.sha256(cache.read_bytes()).hexdigest(),
                         adapted_sha256=hashlib.sha256(adapted.encode()).hexdigest(),
                         result=result,assembly=assembly,exact_conversion=args.exact_conversion,
                         paired_merges=args.paired_merges,
                         scope=__doc__),indent=2))
