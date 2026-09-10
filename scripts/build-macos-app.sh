#!/usr/bin/env bash
# Build a local, private Apple Silicon GalaxyPad.app without game data.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
build="${GALAXYPAD_DESKTOP_BUILD:-$root/generated/build/moderngekko-desktop}"
output="${GALAXYPAD_MACOS_OUTPUT:-$root/generated/macos/GalaxyPad.app}"
module_marker="$root/generated/modules/RMGE01/active-module.txt"

# Promote an audited module without silently rebuilding the tested runtime.
if [[ "${1:-}" == --module-only && $# == 1 ]]; then
  "$root/scripts/audit-module.sh"
  module="$(<"$module_marker")"
  [[ -d "$output" ]] || { echo "module-only promotion requires an existing app" >&2; exit 1; }
  staging="$(mktemp -d "$(dirname -- "$output")/module-promotion.XXXXXX")"
  candidate="$staging/GalaxyPad.app"
  cp -R "$output" "$candidate"
  cp "$module" "$candidate/Contents/MacOS/gRMGE01_recomp.dylib"
  codesign --force --deep --sign - "$candidate"
  for unchanged in GalaxyPad GalaxyPadRunner GalaxyPadFrontend; do
    cmp "$output/Contents/MacOS/$unchanged" "$candidate/Contents/MacOS/$unchanged"
  done
  GALAXYPAD_MACOS_APP="$candidate" "$root/scripts/audit-macos-app.sh"
  backup="$output.previous.$(date -u +%Y%m%dT%H%M%SZ)"
  [[ ! -e "$backup" ]] || { echo "backup already exists: $backup" >&2; exit 1; }
  mv "$output" "$backup"
  mv "$candidate" "$output"
  rmdir "$staging"
  echo "Module promoted; previous package retained at $backup"
  exit 0
fi
[[ $# == 0 ]] || { echo "usage: $0 [--module-only]" >&2; exit 2; }

"$root/scripts/bootstrap-dependencies.sh"
"$root/scripts/audit-module.sh"
[[ -f "$module_marker" ]] || { echo "missing active module marker" >&2; exit 1; }
module="$(<"$module_marker")"
cmake -S "$root/ref/ModernGekko" -B "$build" \
  -DMODERNGEKKO_FRONTEND_NAME=GalaxyPad \
  -DMODERNGEKKO_USER_DIRECTORY_NAME=GalaxyPad \
  -DMODERNGEKKO_REQUIRED_DISC_ID=RMGE01 \
  -DMODERNGEKKO_REQUIRED_DOL_SHA256=2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09
cmake --build "$build" --target moderngekko-run moderngekko-launcher --parallel "${GALAXYPAD_JOBS:-8}"

for required in "$build/moderngekko-run" "$build/ModernGekko" "$module"; do
  [[ -f "$required" ]] || { echo "missing package input: $required" >&2; exit 1; }
  if otool -L "$required" | grep -Eq '/opt/homebrew|/usr/local'; then
    echo "non-portable dependency in $required" >&2
    exit 1
  fi
done
[[ "$(vtool -show-build "$module" | awk '/minos/ {print $2; exit}')" == 14.* ]] || {
  echo "module does not target macOS 14" >&2
  exit 1
}

mkdir -p "$(dirname -- "$output")"
bash "$root/scripts/build-macos-icon.sh"
if [[ -e "$output" ]]; then
  mv "$output" "$output.previous.$(date -u +%Y%m%dT%H%M%SZ)"
fi
mkdir -p "$output/Contents/MacOS" "$output/Contents/Resources"
cp "$root/apple/macos/Info.plist" "$output/Contents/Info.plist"
cp "$root/generated/branding/GalaxyPad.icns" "$output/Contents/Resources/GalaxyPad.icns"
cp "$root/apple/macos/GalaxyPad" "$output/Contents/MacOS/GalaxyPad"
cp "$build/moderngekko-run" "$output/Contents/MacOS/GalaxyPadRunner"
# The upstream launcher resolves this sibling name before searching PATH.
ln -s GalaxyPadRunner "$output/Contents/MacOS/moderngekko-run"
cp "$build/ModernGekko" "$output/Contents/MacOS/GalaxyPadFrontend"
cp "$module" "$output/Contents/MacOS/gRMGE01_recomp.dylib"
# Dolphin's macOS File::GetSysDirectory resolves the bundle Resources directory.
cp -R "$build/Sys" "$output/Contents/Resources/Sys"
cp "$root/apple/macos/default-config.ini" "$output/Contents/Resources/default-config.ini"
cp "$root/apple/macos/default-Dolphin.ini" "$output/Contents/Resources/default-Dolphin.ini"
cp "$root/apple/macos/default-WiimoteNew.ini" "$output/Contents/Resources/default-WiimoteNew.ini"
chmod +x "$output/Contents/MacOS/GalaxyPad"

codesign --force --deep --sign - "$output"
codesign --verify --deep --strict "$output"
echo "$output"
