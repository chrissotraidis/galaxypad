#!/usr/bin/env bash
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
plist="$root/apple/macos/Info.plist"
video="$root/apple/macos/default-config.ini"
input="$root/apple/macos/default-WiimoteNew.ini"
core="$root/apple/macos/default-Dolphin.ini"

plutil -lint "$plist" >/dev/null
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist")" == \
  com.galaxypad.GalaxyPad.macos ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$plist")" == 14.0 ]]
grep -Fxq 'resolution=640x528' "$video"
grep -Fxq 'backend=Metal' "$video"
grep -Fxq 'CPUThread = True' "$core"
grep -Fxq 'AudioBufferSize = 120' "$core"
grep -Fxq 'Extension = Nunchuk' "$input"
grep -Fxq 'Options/Sideways Wiimote = False' "$input"
grep -Fxq 'IR/Up = `Cursor Y-`' "$input"
grep -Fxq 'IR/Right = `Cursor X+`' "$input"
grep -Fxq 'Shake/X = L' "$input"
grep -Fxq 'Nunchuk/Stick/Up = W' "$input"

# Execute the actual launcher guard against an isolated new/existing profile.
python3 - "$root" <<'PY'
import os
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

root = pathlib.Path(sys.argv[1])
identity = json.loads((root / 'config/galaxypad-disc.json').read_text())
dol_hash = next(item['sha256'] for item in identity['executables'] if item['path'] == 'sys/main.dol')
for name in ('build-desktop-tools.sh', 'build-macos-app.sh'):
    build = (root / 'scripts' / name).read_text()
    for definition in ('MODERNGEKKO_FRONTEND_NAME=GalaxyPad',
                       'MODERNGEKKO_USER_DIRECTORY_NAME=GalaxyPad',
                       'MODERNGEKKO_REQUIRED_DISC_ID=RMGE01',
                       'MODERNGEKKO_REQUIRED_DOL_SHA256=' + dol_hash):
        assert '-D' + definition in build, (name, definition)
launcher = (root / 'apple/macos/GalaxyPad').read_text()
start = 'if [[ ! -f "$user_dir/Config/Dolphin.ini" ]]; then'
guard = start + launcher.split(start, 1)[1].split('\nfi', 1)[0] + '\nfi'
with tempfile.TemporaryDirectory(prefix='galaxypad-defaults-') as temporary:
    base = pathlib.Path(temporary)
    (base / 'profile/Config').mkdir(parents=True)
    (base / 'Contents/Resources').mkdir(parents=True)
    default = root / 'apple/macos/default-Dolphin.ini'
    shutil.copyfile(default, base / 'Contents/Resources/default-Dolphin.ini')
    target = base / 'profile/Config/Dolphin.ini'
    env = dict(os.environ, user_dir=str(base / 'profile'), contents=str(base / 'Contents'))
    subprocess.run(['bash', '-eu', '-c', guard], env=env, check=True)
    assert target.read_bytes() == default.read_bytes()
    # A distinct existing file must survive byte-for-byte, regardless of content.
    existing = root / 'apple/macos/default-config.ini'
    shutil.copyfile(existing, target)
    subprocess.run(['bash', '-eu', '-c', guard], env=env, check=True)
    assert target.read_bytes() == existing.read_bytes()
PY

echo "macOS app configuration tests passed"
