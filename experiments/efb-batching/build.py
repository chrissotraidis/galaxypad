#!/usr/bin/env python3
"""Explicit isolated build. Run only after concurrent measurements release host."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import os
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build',action='store_true',help='Actually compile, copy and relink the isolated app')
parser.add_argument('--output',type=Path,help='Prepared output directory, for retaining older candidates')
args=parser.parse_args()
if not args.build:
    parser.error('Pass --build only after the owning measurement has finished')
root=Path(__file__).resolve().parents[2]
out=args.output.resolve() if args.output else root/'generated/experiments/efb-batching-20260913'
j=json.loads((out/'recipe.json').read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(j['original_core'])==j['core_sha256'],'Frozen core identity changed'
assert digest(j['probe_header'])==j['probe_header_sha256'],'Re-run prepare.py after header changes'
for path,expected in j.get('extra_input_hashes',{}).items():
    assert digest(path)==expected,'Re-run prepare.py after batch implementation changes'
def test_source(name):
    return j.get('test_sources',{}).get(name,str(Path(__file__).with_name(name)))
test=out/'test-probe'
subprocess.run(['xcrun','clang++','-std=c++23','-fsanitize=address,undefined',
  test_source('test-probe.cpp'),'-o',str(test)],check=True)
subprocess.run([str(test)],check=True)
if j.get('batch_prototype'):
    policy_test=out/'test-batch-policy'
    subprocess.run(['xcrun','clang++','-std=c++23','-fsanitize=address,undefined',
      test_source('test-batch-policy.cpp'),'-o',str(policy_test)],check=True)
    subprocess.run([str(policy_test)],check=True)
    metal_test=out/'test-metal-parity'
    subprocess.run(['xcrun','clang++','-std=c++23','-O2','-fno-objc-arc',
      test_source('test-metal-parity.mm'),'-framework','Foundation',
      '-framework','Metal','-o',str(metal_test)],check=True)
    with (out/'metal-parity.log').open('w') as log:
        subprocess.run([str(metal_test)],env={**os.environ,'MTL_DEBUG_LAYER':'1'},
                       stdout=log,stderr=subprocess.STDOUT,check=True)
for index,item in enumerate(j['compile_commands']):
    with (out/f'compile-{index}.log').open('w') as log:
        subprocess.run(item['argv'],cwd=item['directory'],stdout=log,stderr=subprocess.STDOUT,check=True)
originalMembers=subprocess.check_output(['ar','-t',j['original_core']],text=True).splitlines()
for member in j['replace_members']:assert originalMembers.count(member)==1,(member,originalMembers.count(member))
newCore=out/'libGalaxyPadCore.a'
shutil.copyfile(j['original_core'],newCore)
subprocess.run(['ar','-r',str(newCore),*[str(out/x) for x in j['replace_members']]],check=True)
subprocess.run(['ranlib',str(newCore)],check=True)
newMembers=subprocess.check_output(['ar','-t',str(newCore)],text=True).splitlines()
assert newMembers==originalMembers,'Unexpected archive member scope changed'
app=out/'GalaxyPad.app'
shutil.copytree(j['original_app'],app,dirs_exist_ok=True)
with (out/'link.log').open('w') as log:
    subprocess.run(j['link'],stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run(['codesign','--force','--sign','-',str(app)],check=True)
j.update(status='sanitizer recorder test and isolated compile/link/sign passed; not installed or runtime validated',
  candidate_core_sha256=digest(newCore),candidate_host_sha256=digest(app/'GalaxyPad'),
  instrumented_source_hashes={str(out/(Path(p).name)):digest(out/(Path(p).name)) for p in j['source_hashes']})
(out/'recipe.json').write_text(json.dumps(j,indent=2)+'\n')
print(app)
