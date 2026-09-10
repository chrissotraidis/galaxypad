#!/usr/bin/env python3
"""Prepare an isolated, hash-gated candidate; never edit the accepted module tree."""
import hashlib
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITES = {
    'chunk_1015_text1_803FB0A0.c': (0x803FB0EC, '50133c193f685cdd0a57ab9b7e2aa181c09ee77b14975d939e17e0f64422b7b6'),
    'chunk_0372_text1_801780A0.c': (0x80178EC8, 'c01249edc071a20f6b4692e42a1a2df252be227b585f21c9357b55823f8ea937'),
}
DECL = 'extern void galaxypad_native_observe(const CPUState*, unsigned int);\n'
def instrument(source, site):
    label = f'label_{site:08X}:\n    ctx->pc = 0x{site:08X}u;\n'
    if source.count(label) != 1 or 'galaxypad_native_observe' in source:
        raise ValueError('Expected one uninstrumented materialized site')
    # Counted-loop helpers precede the main function in this pinned emitter.
    if source.index(label) < source.index('void func_'):
        raise ValueError('Selected site is inside an outlined helper')
    include = '#include "../RMGE01.h"\n'
    if source.count(include) != 1:
        raise ValueError('Unexpected generated header')
    call = f'    galaxypad_native_observe(ctx, 0x{site:08X}u);\n'
    candidate = source.replace(include, include+DECL).replace(label, label+call)
    assert candidate.replace(DECL, '').replace(call, '') == source
    return candidate

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify():
    base=ROOT/'generated/native-observer-r562'
    tree=base/'RMGE01_generated'
    report=json.loads((base/'manifest.json').read_text())
    expected={item['path'] for item in report['files']}
    actual={str(path.relative_to(tree)) for path in tree.rglob('*') if path.is_file()}
    assert actual==expected, 'Candidate inventory changed'
    for item in report['files']:
        path=tree/item['path']
        assert path.resolve().is_relative_to(tree.resolve())
        assert digest(path.read_bytes())==item['candidate'], item['path']
    assert report['sites']==[hex(site) for site,_ in SITES.values()]
    print('Candidate inventory and all recorded hashes verified')

def main():
    module = pathlib.Path((ROOT/'generated/modules/RMGE01/active-module.txt').read_text().strip())
    assert module.resolve().is_relative_to(ROOT/'generated')
    assert digest(module.read_bytes()) == 'c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939'
    source = module.parent/'dolrecomp-output/RMGE01_generated'
    assert digest((source/'main.dol').read_bytes()) == '2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09'
    changes = {}
    for name,(site,expected) in SITES.items():
        raw=(source/'chunks'/name).read_bytes()
        assert digest(raw)==expected, name
        changes[name]=instrument(raw.decode(),site)
    destination=ROOT/'generated/native-observer-r562/RMGE01_generated'
    if destination.exists():
        raise SystemExit('Candidate already exists; inspect it instead of overwriting')
    shutil.copytree(source,destination)
    for name,text in changes.items():
        (destination/'chunks'/name).write_text(text)
    files=[]
    for original in sorted(source.rglob('*')):
        if not original.is_file(): continue
        relative=original.relative_to(source)
        before=original.read_bytes(); after=(destination/relative).read_bytes()
        changed=before!=after
        assert not changed or str(relative) in {'chunks/'+name for name in SITES}
        files.append({'path':str(relative),'source':digest(before),'candidate':digest(after)})
    assert sum(f['source']!=f['candidate'] for f in files)==2
    report={'sites':[hex(site) for site,_ in SITES.values()], 'files':files,
            'warning':'Source coverage only; candidate is not yet compiled or runtime validated'}
    (destination.parent/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Prepared {destination}; exactly two changed files among {len(files)} audited files')

if __name__=='__main__':
    if sys.argv[1:]==['--verify']: verify()
    elif not sys.argv[1:]: main()
    else: raise SystemExit('Usage: prepare-native-observer.py [--verify]')
