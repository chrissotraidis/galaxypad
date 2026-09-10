#!/bin/bash
# Private pinned video-only FFmpeg dependency. Does not change app defaults.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
THP_SDK="${GALAXYPAD_IOS_SDK:-iphonesimulator}"
case "$THP_SDK" in
  iphonesimulator) THP_TARGET=arm64-apple-ios16.0-simulator ;;
  iphoneos) THP_TARGET=arm64-apple-ios16.0 ;;
  *) echo "Unsupported SDK: $THP_SDK" >&2; exit 1 ;;
esac
ARCHIVE="$ROOT/generated/tools/ffmpeg-thp-r654/ffmpeg-8.0.1.tar.xz"
EXPECTED=05ee0b03119b45c0bdb4df654b96802e909e0a752f72e4fe3794f487229e5a41
test "$(shasum -a 256 "$ARCHIVE" | awk '{print $1}')" = "$EXPECTED"
THP_ROOT="$ROOT/generated/tools/ffmpeg-thp-$THP_SDK"
SOURCE="$THP_ROOT/ffmpeg-8.0.1"
mkdir -p "$THP_ROOT"
if [[ ! -f "$SOURCE/configure" ]]; then tar -xf "$ARCHIVE" -C "$THP_ROOT"; fi
SDKROOT_PATH="$(xcrun --sdk "$THP_SDK" --show-sdk-path)"
CLANG_PATH="$(xcrun --sdk "$THP_SDK" --find clang)"
cd "$SOURCE"
./configure --disable-everything --disable-autodetect --disable-network \
  --disable-doc --disable-debug --disable-programs --disable-avformat \
  --disable-avdevice --disable-avfilter --disable-swresample --disable-swscale \
  --enable-decoder=thp --enable-cross-compile --target-os=darwin --arch=aarch64 \
  --cc="$CLANG_PATH" --sysroot="$SDKROOT_PATH" \
  --extra-cflags="-target $THP_TARGET" --extra-ldflags="-target $THP_TARGET" \
  > "$THP_ROOT/configure.log" 2>&1
make -j4 > "$THP_ROOT/build.log" 2>&1
test -f libavcodec/libavcodec.a && test -f libavutil/libavutil.a
file libavcodec/libavcodec.a libavutil/libavutil.a
shasum -a 256 libavcodec/libavcodec.a libavutil/libavutil.a
