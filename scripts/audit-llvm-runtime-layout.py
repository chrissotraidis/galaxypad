#!/usr/bin/env python3
"""Compare compiler-derived layouts for fields actually used by LLVM emission.

Matching offsets are necessary, not sufficient, for runtime compatibility.
The complete structs intentionally differ; never cast/copy them by full size.
"""
from pathlib import Path
import json
import re
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
backend=root/'ref/ModernGekko/vendor/dolphin/DolRecomp/src/backend/llvm'
fields=sorted(set(re.findall(r'offsetof\(CPUState,\s*(\w+)\)',
                            '\n'.join(p.read_text() for p in backend.glob('*.cpp')))))
assert fields
extra=['cache_control']
with tempfile.TemporaryDirectory(prefix='galaxypad-llvm-layout-') as directory:
    temp=Path(directory);results={}
    for name,header,include in [
        ('standalone','cpu/cpu.h',root/'ref/ModernGekko/vendor/dolphin/DolRecomp/src'),
        ('runtime','core/cpu.h',root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include')]:
        source='#include <stdio.h>\n#include <stddef.h>\n#include "'+header+'"\nint main(void) {\n'
        source+='printf("struct %zu %zu\\n",sizeof(CPUState),_Alignof(CPUState));\n'
        for field in fields+extra:
            source+=f'printf("{field} %zu %zu\\n",offsetof(CPUState,{field}),sizeof(((CPUState*)0)->{field}));\n'
        source+='}\n';path=temp/(name+'.c');path.write_text(source)
        subprocess.run(['clang','-std=c11','-O0','-I',str(include),str(path),'-o',str(temp/name)],check=True)
        lines=subprocess.check_output([str(temp/name)],text=True).splitlines()
        results[name]={x.split()[0]:list(map(int,x.split()[1:])) for x in lines}
    differences={f:{n:r[f] for n,r in results.items()} for f in fields
                 if results['standalone'][f]!=results['runtime'][f]}
    print(json.dumps({'llvm_fields':fields,'layouts':results,'used_field_differences':differences,
      'boundary':'Offsets/sizes only. Complete CPU structs differ; helper semantics and module/chassis ABI are not proven.'},indent=2))
    if differences:raise SystemExit('LLVM-emitted field layout mismatch')
