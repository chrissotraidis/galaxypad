#!/usr/bin/env bash
# Private local staging only. Does not sign, install, upload or create a release.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
case "${GALAXYPAD_IOS_SDK:-iphoneos}" in
  iphoneos) lane=ios-device; platform=IOS; label=device ;;
  iphonesimulator) lane=ios-simulator; platform=IOSSIMULATOR; label=simulator ;;
  *) echo 'GALAXYPAD_IOS_SDK must be iphonesimulator or iphoneos' >&2; exit 2 ;;
esac
if (( $# > 2 )); then
  echo "Usage: $0 [device-app [device-module]]" >&2
  exit 2
fi
app="${1:-$root/generated/build/$lane-app/GalaxyPad.app}"
module="${2:-$root/generated/build/$lane-module/gRMGE01_recomp.dylib}"
for binary in "$app/GalaxyPad" "$module"; do
  [[ -f "$binary" ]] || { echo "Missing device build: $binary" >&2; exit 1; }
  [[ "$(xcrun lipo -archs "$binary")" == arm64 ]]
  metadata="$(xcrun vtool -show-build "$binary")"
  rg -q "^[[:space:]]*platform $platform$" <<<"$metadata"
  rg -q '^[[:space:]]*minos 16\.0$' <<<"$metadata"
done
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Info.plist")" == org.galaxypad.GalaxyPad ]]
[[ -s "$app/Assets.car" ]] || { echo 'Missing compiled app icons' >&2; exit 1; }
for key in CFBundleIcons 'CFBundleIcons~ipad'; do
  [[ "$(/usr/libexec/PlistBuddy -c "Print :$key:CFBundlePrimaryIcon:CFBundleIconName" "$app/Info.plist")" == AppIcon ]]
done
python3 "$root/scripts/check-ios-game-mode.py" "$app/Info.plist"
symbols="$(xcrun nm -gjU "$module")"
rg -Fxq '_staticrecomp_get_module' <<<"$symbols"
install_name="$(xcrun otool -D "$module")"
rg -Fxq '@rpath/gRMGE01_recomp.dylib' <<<"$install_name"
# Never overwrite an earlier staged build or mutate compiler outputs.
stage="$(mktemp -d "$root/generated/$label-stage.XXXXXX")"
staged_app="$stage/GalaxyPad.app"
ditto "$app" "$staged_app"
mkdir -p "$staged_app/Frameworks"
ditto "$module" "$staged_app/Frameworks/gRMGE01_recomp.dylib"
cmp "$module" "$staged_app/Frameworks/gRMGE01_recomp.dylib"
shasum -a 256 "$staged_app/GalaxyPad" "$staged_app/Frameworks/gRMGE01_recomp.dylib"
printf 'Private staged app: %s\nNot signed for a device; not a release or runtime acceptance.\n' "$staged_app"
