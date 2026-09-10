#!/usr/bin/env python3
"""Compare real app and module CPUState layouts used by the observer callback."""
import pathlib
import subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
output=ROOT/'generated/tests'
output.mkdir(parents=True,exist_ok=True)
layouts=[]
for name,header,include in [
    ('module','core/cpu.h',ROOT/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'),
    ('host','moderngekko/cpu_state.h',ROOT/'ref/ModernGekko/include')]:
    executable=output/('observer-layout-'+name)
    subprocess.run(['xcrun','clang','-std=c11','-Wall','-Wextra','-Werror',
        '-DPROBE_CPU_HEADER="'+header+'"','-I',str(include),
        str(ROOT/'tests/probe-cpu-field-offsets.c'),'-o',str(executable)],check=True)
    layouts.append(subprocess.check_output([str(executable)],text=True))
assert layouts[0]==layouts[1], 'Observer host/module layout mismatch:\n'+'\n'.join(layouts)
print(layouts[0],end='')
print('Observer host/module CPU layout matches for all probed fields')
