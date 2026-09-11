#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
case "${GALAXYPAD_IOS_SDK:-iphonesimulator}" in
  iphonesimulator) lane=ios-simulator ;;
  iphoneos) lane=ios-device ;;
  *) echo "GALAXYPAD_IOS_SDK must be iphonesimulator or iphoneos" >&2; exit 2 ;;
esac
# The app links the packaged core archive rather than the core build tree.
# Refresh it here so a source-only core rebuild cannot leave the app with a
# stale RuntimeConfig/ABI or runtime implementation.
bash "$root/scripts/provision-ios-simulator-core.sh"
build="$root/generated/build/$lane-app"
cmake -S "$root/apple/ios" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/$lane-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$build" --parallel 4
# The resource-copy target runs after linking. Seal the complete Simulator
# bundle, not the linker's resource-free ad-hoc executable signature.
# Device signing remains a separate explicit staging workflow.
if [[ "$lane" == ios-simulator ]]; then
  codesign --force --sign - "$build/GalaxyPad.app"
  codesign --verify --deep --strict "$build/GalaxyPad.app"
fi
xcrun vtool -show-build "$build/GalaxyPad.app/GalaxyPad"
