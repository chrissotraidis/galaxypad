#!/usr/bin/env python3
"""Rebuild only CoreHost against final7 objects/core; never installs or launches."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
root=Path(__file__).resolve().parents[2]
base=root/'generated/build/ios-simulator-settings-perf7-final-20260913'
variant2='--retain-neutral-base' in sys.argv[1:]
out=root/('generated/experiments/pointer-gameplay-pass2-v2-20260913' if variant2 else
          'generated/experiments/pointer-gameplay-pass2-20260913')
recipe=json.loads((base/'recipe.json').read_text())
subprocess.run(['python3',str(Path(__file__).with_name('make-corehost-overlay.py')),
                *(['--retain-neutral-base'] if variant2 else [])],check=True)
command=next(c.copy() for c in recipe['compile_commands'] if any(x.endswith('/GalaxyPadCoreHost.mm') for x in c))
originalObject=command[command.index('-o')+1]
newObject=str(out/'GalaxyPadCoreHost.mm.o')
command=[x.replace(originalObject,newObject) for x in command]
command += ['-I',str(root),'-ivfsoverlay',str(out/'overlay.json')]
link=recipe['link'].copy()
originalApp=Path(link[link.index('-o')+1]).parent
newApp=out/'GalaxyPad.app'
shutil.copytree(originalApp,newApp,dirs_exist_ok=True)
link=[newObject if x==originalObject else x for x in link]
link[link.index('-o')+1]=str(newApp/'GalaxyPad')
link=[('-Wl,-map,'+str(out/'host-link.map')) if x.startswith('-Wl,-map,') else x for x in link]
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
core=next(x for x in link if x.endswith('/libGalaxyPadCore.a'))
assert digest(core)==recipe['core_sha256'], 'Core changed since final7'
for stage,args in [('compile',command),('link',link)]:
    with (out/(stage+'.log')).open('w') as log:
        subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run(['codesign','--force','--sign','-',str(newApp)],check=True)
receipt={'compile':command,'link':link,'core_sha256':digest(core),
    'base_host_sha256':digest(originalApp/'GalaxyPad'),'host_sha256':digest(newApp/'GalaxyPad'),
    'source_sha256':{str(p):digest(p) for p in [root/'apple/ios/GalaxyPadCoreHost.mm',out/'GalaxyPadCoreHost.mm',root/'experiments/pointer/NeutralGameplayReadiness.h']},
    'module_sha256':{str(p.relative_to(newApp)):digest(p) for p in newApp.rglob('*.dylib')},
    'status':'compiled, linked, ad-hoc signed; not installed or runtime validated'}
(out/'recipe.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(newApp)
