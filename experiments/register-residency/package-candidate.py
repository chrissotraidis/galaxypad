#!/usr/bin/env python3
"""Package a private iPhone test app: installed baseline app + a replacement game module.

Signs with the baseline's own certificate (by SHA-1), entitlements and embedded
profile, so the result installs in place over the baseline and keeps app data.
"""
from pathlib import Path
import argparse, hashlib, json, plistlib, shutil, subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-app', type=Path, required=True)
p.add_argument('--signer-app', type=Path, help='Installed app whose certificate/entitlements to reuse (default: baseline)')
p.add_argument('--module', type=Path, required=True)
p.add_argument('--build', required=True, help='New CFBundleVersion')
p.add_argument('--output', type=Path, required=True, help='New directory for the signed app and receipt')
a = p.parse_args()
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
sha = lambda f: hashlib.sha256(Path(f).read_bytes()).hexdigest()
run = lambda *c, **k: subprocess.run(list(map(str, c)), check=True, **k)
out_of = lambda *c: subprocess.check_output(list(map(str, c)), stderr=subprocess.DEVNULL)

signer = a.signer_app or a.baseline_app
run('codesign', '--verify', '--deep', '--strict', signer)
run('codesign', '-d', '--extract-certificates=' + str(out/'certificate'), signer,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
identity = hashlib.sha1((out/'certificate0').read_bytes()).hexdigest().upper()
assert identity in subprocess.check_output(['security', 'find-identity', '-v', '-p', 'codesigning'], text=True)
entitlements = out_of('codesign', '-d', '--entitlements', ':-', signer)
(out/'entitlements.plist').write_bytes(entitlements)

app = out/'GalaxyPad.app'
shutil.copytree(a.baseline_app, app, symlinks=True)
module = app/'Frameworks/gRMGE01_recomp.dylib'
baseline_module = sha(module)
shutil.copyfile(a.module, module)
info = plistlib.loads((app/'Info.plist').read_bytes())
old_build = info['CFBundleVersion']
info['CFBundleVersion'] = a.build
(app/'Info.plist').write_bytes(plistlib.dumps(info, fmt=plistlib.FMT_BINARY))
run('codesign', '--force', '--sign', identity, '--timestamp=none', module)
run('codesign', '--force', '--sign', identity, '--entitlements', out/'entitlements.plist', '--timestamp=none', app)
run('codesign', '--verify', '--deep', '--strict', app)
receipt = {'baseline_app': str(a.baseline_app), 'baseline_build': old_build, 'build': a.build,
           'baseline_module_sha256': baseline_module, 'unsigned_module_sha256': sha(a.module),
           'signed_module_sha256': sha(module), 'signed_host_sha256': sha(app/'GalaxyPad'),
           'signer_sha1': identity}
(out/'receipt.json').write_text(json.dumps(receipt, indent=1) + '\n')
print(json.dumps(receipt, indent=1))
