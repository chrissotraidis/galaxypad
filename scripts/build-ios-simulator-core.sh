#!/usr/bin/env bash
# Build only the pinned runtime; never bootstrap/overwrite the active macOS graph.
# Adapted from SunPad fcdc1411 scripts/ios-build-core.sh (GPL-3.0).
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runtime="$root/ref/ModernGekko"
# Keep the established Simulator default; device work has a separate build tree.
case "${GALAXYPAD_IOS_SDK:-iphonesimulator}" in
  iphonesimulator) lane=ios-simulator ;;
  iphoneos) lane=ios-device ;;
  *) echo "GALAXYPAD_IOS_SDK must be iphonesimulator or iphoneos" >&2; exit 2 ;;
esac
build="$root/generated/build/$lane-core"
[[ "$(git -C "$runtime" rev-parse HEAD)" == 0514d9f03f8602809f66fc92fdca87d30e752997 ]]
[[ "$(git -C "$runtime/vendor/dolphin" rev-parse HEAD)" == 13e492094902644b0d113c586300d358640f9e19 ]]
patch="$root/patches/ios-simulator-framebuffer-fetch.patch"
if ! git -C "$runtime/vendor/dolphin" apply --reverse --check "$patch" 2>/dev/null; then
  git -C "$runtime/vendor/dolphin" apply --check "$patch"
  git -C "$runtime/vendor/dolphin" apply "$patch"
fi
cmake -S "$runtime" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/$lane-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DUSE_SYSTEM_FMT=OFF -DUSE_SYSTEM_LZ4=OFF -DUSE_SYSTEM_ZSTD=OFF \
  -DENABLE_QT=OFF -DENABLE_TESTS=OFF -DBUILD_TESTING=OFF \
  -DMODERNGEKKO_ENABLE_DOLPHIN_TESTS=OFF \
  -DENABLE_CUBEB=OFF -DENABLE_VULKAN=OFF -DHAVE_PIPE2=0
cmake --build "$build" --target moderngekko --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
