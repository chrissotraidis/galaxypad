#!/usr/bin/env python3
"""Freeze prepared experiment inputs without rebuilding or changing app bytes."""
import argparse, hashlib, json, shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--probe',type=Path)
a=p.parse_args();out=a.output.resolve();recipe=out/'recipe.json';j=json.loads(recipe.read_text())
receipt=out/'recipe-before-input-freeze.json'
if not receipt.exists():shutil.copyfile(recipe,receipt)
overlay_path=out/'overlay.json';overlay=json.loads(overlay_path.read_text())
def freeze(original,source=None):
 original=Path(original).resolve();source=Path(source or original).resolve()
 target=out/'frozen-inputs'/original.name;target.parent.mkdir(exist_ok=True)
 shutil.copyfile(source,target)
 overlay['roots']=[r for r in overlay['roots'] if r['name']!=str(original)]
 overlay['roots'].append({'type':'file','name':str(original),'external-contents':str(target)})
 return str(target),hashlib.sha256(target.read_bytes()).hexdigest()
path,digest=freeze(j['probe_header'],a.probe)
assert digest==j['probe_header_sha256'],'Wrong historical probe header'
j['probe_header']=path
extras={}
for original,expected in j.get('extra_input_hashes',{}).items():
 path,digest=freeze(original);assert digest==expected;extras[path]=digest
j['extra_input_hashes']=extras
j['test_sources']={}
for name in ['test-probe.cpp']+(['test-batch-policy.cpp','test-metal-parity.mm'] if j.get('batch_prototype') else []):
 path,digest=freeze(Path(__file__).with_name(name));j['test_sources'][name]=path
 j['extra_input_hashes'][path]=digest
# Relative quoted includes in frozen tests resolve through this VFS mapping.
for original in ['EfbBatchProbe.h','MetalEfbBatch.h','MetalEfbBatchImpl.inc']:
 target=out/'frozen-inputs'/original
 if target.exists():overlay['roots'].append({'type':'file','name':str(target),'external-contents':str(target)})
overlay_path.write_text(json.dumps(overlay,indent=2)+'\n');recipe.write_text(json.dumps(j,indent=2)+'\n')
print(out)
