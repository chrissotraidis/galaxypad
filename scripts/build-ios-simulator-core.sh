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
python3 "$root/scripts/dependency-lock.py"
# Simulator framebuffer support is committed in the pinned RecompCore fork.

cmake -S "$runtime" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/$lane-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DUSE_SYSTEM_FMT=OFF -DUSE_SYSTEM_LZ4=OFF -DUSE_SYSTEM_ZSTD=OFF \
  -DENABLE_QT=OFF -DENABLE_TESTS=OFF -DBUILD_TESTING=OFF \
  -DMODERNGEKKO_ENABLE_DOLPHIN_TESTS=OFF \
  -DENABLE_CUBEB=OFF -DENABLE_VULKAN=OFF -DHAVE_PIPE2=0
cmake --build "$build" --target moderngekko --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
