#!/usr/bin/env bash
# Audit the private local GalaxyPad.app without exposing protected inputs.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
app="${GALAXYPAD_MACOS_APP:-$root/generated/macos/GalaxyPad.app}"
module_marker="$root/generated/modules/RMGE01/active-module.txt"

"$root/scripts/audit-module.sh"
[[ -f "$module_marker" ]] || { echo "missing active module marker" >&2; exit 1; }
source_module="$(<"$module_marker")"

[[ -d "$app" ]] || { echo "missing private app: $app" >&2; exit 1; }
cmp "$root/apple/macos/GalaxyPad" "$app/Contents/MacOS/GalaxyPad"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Contents/Info.plist")" == \
  com.galaxypad.GalaxyPad.macos ]] || { echo "unexpected bundle identity" >&2; exit 1; }
[[ "$(/usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$app/Contents/Info.plist")" == \
  14.0 ]] || { echo "unexpected deployment target" >&2; exit 1; }

for executable in GalaxyPadRunner GalaxyPadFrontend gRMGE01_recomp.dylib; do
  path="$app/Contents/MacOS/$executable"
  [[ -f "$path" ]] || { echo "missing packaged executable: $executable" >&2; exit 1; }
  file "$path" | grep -q 'arm64' || { echo "non-arm64 package input: $executable" >&2; exit 1; }
  if otool -L "$path" | grep -Eq '/opt/homebrew|/usr/local'; then
    echo "non-portable dependency in $executable" >&2
    exit 1
  fi
done

[[ "$(readlink "$app/Contents/MacOS/moderngekko-run")" == GalaxyPadRunner ]] || {
  echo "launcher runner alias is missing or points outside the bundle" >&2; exit 1;
}

# File::GetSysDirectory on macOS does not search next to the executable.
game_settings="$app/Contents/Resources/Sys/GameSettings/RMG.ini"
cmp "$root/apple/macos/default-Dolphin.ini" "$app/Contents/Resources/default-Dolphin.ini"
[[ -f "$game_settings" ]] || { echo "missing runtime-resolved Galaxy settings" >&2; exit 1; }
for setting in 'EFBAccessEnable = True' 'EFBAccessDeferInvalidation = True' \
  'ArbitraryMipmapDetection = True'; do
  grep -Fxq "$setting" "$game_settings" || {
    echo "missing required Galaxy setting: $setting" >&2; exit 1;
  }
done

[[ -f "$source_module" ]] || { echo "missing audited source module" >&2; exit 1; }
actual_source_hash="$(shasum -a 256 "$source_module" | awk '{print $1}')"
# Deep signing replaces the linker's ad-hoc signature, so the sealed package has
# a distinct deterministic hash. Sign a same-named temporary copy to derive the
# expected package identity from the currently audited source module.
temporary="$(mktemp -d "${TMPDIR:-/tmp}/galaxypad-app-audit.XXXXXX")"
trap 'rm -rf "$temporary"' EXIT
expected_signed_module="$temporary/gRMGE01_recomp.dylib"
cp "$source_module" "$expected_signed_module"
codesign --force --sign - "$expected_signed_module" >/dev/null
expected_signed_module_hash="$(shasum -a 256 "$expected_signed_module" | awk '{print $1}')"
actual_signed_hash="$(shasum -a 256 "$app/Contents/MacOS/gRMGE01_recomp.dylib" | awk '{print $1}')"
[[ "$actual_signed_hash" == "$expected_signed_module_hash" ]] || {
  echo "packaged module does not match active source after signing" >&2
  echo "  source SHA-256:          $actual_source_hash" >&2
  echo "  expected signed SHA-256: $expected_signed_module_hash" >&2
  echo "  packaged signed SHA-256: $actual_signed_hash" >&2
  exit 1
}
nm -gj "$app/Contents/MacOS/gRMGE01_recomp.dylib" | grep -Fxq '_staticrecomp_get_module'
strings "$app/Contents/MacOS/gRMGE01_recomp.dylib" | grep -Fxq 'RMGE01'

protected="$(find "$app" -type f \( \
  -iname '*.iso' -o -iname '*.gcm' -o -iname '*.rvz' -o -iname '*.wia' -o \
  -iname '*.wbfs' -o -iname '*.gcz' -o -iname '*.dol' -o -iname '*.rel' -o \
  -iname '*.rso' -o -iname '*.sav' -o -iname '*.gci' -o -iname '*.raw' -o \
  -iname '*.png' -path '*/ScreenShots/*' -o -iname '*.wav' -o -iname '*.flac' \
  \) -print)"
if [[ -n "$protected" ]]; then
  echo "protected runtime input found in package:" >&2
  echo "$protected" >&2
  exit 1
fi

codesign --verify --deep --strict "$app"
echo "Private macOS app audit passed"
