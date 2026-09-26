#!/usr/bin/env python3
"""Rebuild the iPhone host from this checkout with the Preview 4 recipe.

Recompiles every native host source using the retained 7163 compile commands,
relinks against the retained, hash-verified Preview 3 core archive, and emits an
unsigned app shell (sign it with experiments/register-residency/package-candidate.py).
"""
from pathlib import Path
import argparse, hashlib, json, plistlib, subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--retained', type=Path, required=True, help='Checkout holding the retained 7163/7165/7166 build inputs')
p.add_argument('--output', type=Path, required=True)
p.add_argument('--build', required=True)
p.add_argument('--overlay-inputs', type=Path, required=True,
               help='Directory with the retained Mixer.cpp, Mixer.h and AudioTempo.h (release build records)')
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
old = a.retained.resolve(); out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
base = old/'generated/iphone-ui-7163-20260916'
archive = old/'generated/audio-slowdown-7165-20260916/libGalaxyPadCore.a'
shell = old/'generated/game-mode-7166-20260916/GalaxyPad.app'
sha = lambda f: hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(archive) == json.loads((archive.parent/'receipt.json').read_text())['archive_sha256']
app = out/'GalaxyPad.app'
subprocess.run(['ditto', str(shell), str(app)], check=True)
receipt = json.loads((base/'receipt.json').read_text())
overlay = json.loads((base/'audio-overlay.json').read_text())
for entry in overlay['roots']:
    entry['name'] = entry['name'].replace(str(old), str(root))
    entry['external-contents'] = str((a.overlay_inputs/Path(entry['external-contents']).name).resolve())
    assert Path(entry['external-contents']).is_file(), entry['external-contents']
(out/'audio-overlay.json').write_text(json.dumps(overlay, indent=2))
disc = json.loads((root/'config/galaxypad-disc.json').read_text())
values = {'IMAGE_SHA256': disc['container']['sha256'], 'IMAGE_BYTES': disc['container']['sizeBytes'],
          'DOL_SHA256': disc['executables'][0]['sha256'], 'DOL_BYTES': disc['executables'][0]['sizeBytes'],
          'RSO_SHA256': disc['executables'][1]['sha256'], 'SYMBOL_SHA256': disc['executableMetadata'][0]['sha256']}
header = (root/'apple/shared/GalaxyPadDiscIdentity.h.in').read_text()
for k, v in values.items():
    header = header.replace('@GALAXYPAD_' + k + '@', str(v))
assert '@GALAXYPAD_' not in header
(out/'GalaxyPadDiscIdentity.h').write_text(header)
sdk = subprocess.check_output(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path'], text=True).strip()
old_sdk = '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS26.5.sdk'
rewrite = lambda x: (x.replace(old_sdk, sdk).replace(str(base), str(out))
                     .replace(str(old/'apple'), str(root/'apple')).replace(str(old/'ref'), str(root/'ref')))
commands = [[rewrite(x) for x in cmd] for cmd in receipt['compile']]
commands.append([x.replace('main.mm', 'GalaxyPadGyroPointer.mm') for x in commands[0]])
with (out/'compile.log').open('w') as log:
    for cmd in commands:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
link = [rewrite(x) for x in receipt['link']]
link = [str(archive) if x.endswith('/device/libGalaxyPadCore.a') else x for x in link]
link.insert(link.index('-o'), str(out/'GalaxyPadGyroPointer.mm.o'))
with (out/'link.log').open('w') as log:
    subprocess.run(link, stdout=log, stderr=subprocess.STDOUT, check=True)
info = plistlib.loads((app/'Info.plist').read_bytes())
info['CFBundleVersion'] = a.build
info['NSMotionUsageDescription'] = plistlib.loads((root/'apple/ios/Info.plist.in').read_bytes())['NSMotionUsageDescription']
(app/'Info.plist').write_bytes(plistlib.dumps(info))
record = {'build': a.build, 'git': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
          'dirty': bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', 'apple'], text=True).strip()),
          'core_sha256': sha(archive), 'unsigned_host_sha256': sha(app/'GalaxyPad'),
          'overlay_sources': {e['external-contents']: sha(e['external-contents']) for e in overlay['roots']},
          'sources': {c[c.index('-c') + 1]: sha(c[c.index('-c') + 1]) for c in commands}}
(out/'receipt.json').write_text(json.dumps(record, indent=1) + '\n')
print(json.dumps({k: record[k] for k in ('build', 'git', 'dirty', 'unsigned_host_sha256')}))
