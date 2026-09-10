#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Adapted from SunPad fcdc1411 scripts/ios-provision.sh. Core only: no game
# paths, game data, save files or generated module are copied by this script.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
sdk="${GALAXYPAD_IOS_SDK:-iphonesimulator}"
case "$sdk" in
  iphonesimulator) lane=ios-simulator; platform=IOSSIMULATOR ;;
  iphoneos) lane=ios-device; platform=IOS ;;
  *) echo "GALAXYPAD_IOS_SDK must be iphonesimulator or iphoneos" >&2; exit 2 ;;
esac
build="$root/generated/build/$lane-core"
out="$root/generated/ios/$sdk/libs"
core="$build/vendor/dolphin/Source/Core"
external="$build/vendor/dolphin/Externals"
libs=("$build/libmoderngekko.a")
for relative in \
  UICommon/libuicommon.a Core/libcore.a DiscIO/libdiscio.a \
  VideoBackends/Null/libvideonull.a VideoBackends/Metal/libvideometal.a \
  VideoCommon/libvideocommon.a AudioCommon/libaudiocommon.a \
  InputCommon/libinputcommon.a Common/libcommon.a; do
  libs+=("$core/$relative")
done
for relative in \
  FreeSurround/libFreeSurround.a SDL/SDL/libSDL3.a LZO/liblzo2.a \
  spirv_cross/libspirv_cross.a xxhash/libxxhash.a implot/libimplot.a \
  imgui/libimgui.a glslang/glslang/SPIRV/libSPIRV.a \
  glslang/glslang/glslang/libglslang.a tinygltf/libtinygltf.a enet/enet/libenet.a \
  SFML/libsfml-network.a SFML/libsfml-system.a FatFs/libFatFs.a \
  curl/curl/lib/libcurl.a mbedtls/library/libmbedtls.a \
  mbedtls/library/libmbedx509.a mbedtls/library/libmbedcrypto.a \
  libspng/libspng/libspng_static.a zlib-ng/zlib-ng/libz.a \
  pugixml/pugixml/libpugixml.a cpp-optparse/libcpp-optparse.a \
  minizip-ng/minizip-ng/libminizip-ng.a liblzma/liblzma.a fmt/fmt/libfmt.a \
  lz4/lz4/build/cmake/liblz4.a zstd/zstd/build/cmake/lib/libzstd.a; do
  libs+=("$external/$relative")
done
for lib in "${libs[@]}"; do
  [[ -f "$lib" ]] || { printf 'Missing %s archive: %s\n' "$sdk" "$lib" >&2; exit 1; }
done
# Check a real runtime object rather than trusting the build directory's name.
object="$build/CMakeFiles/moderngekko.dir/src/runtime/dolphin_runtime.cpp.o"
xcrun vtool -show-build "$object" | rg -q "^[[:space:]]*platform $platform$"
mkdir -p "$out"
xcrun libtool -static -o "$out/libGalaxyPadCore.a" "${libs[@]}"
xcrun lipo "$out/libGalaxyPadCore.a" -verify_arch arm64
shasum -a 256 "$out/libGalaxyPadCore.a"
