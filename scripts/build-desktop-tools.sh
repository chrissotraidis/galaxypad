#!/usr/bin/env bash
# Build the pinned ModernGekko desktop inspection, module, and runtime tools.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
source_dir="$root/ref/ModernGekko"
build_dir="${GALAXYPAD_DESKTOP_BUILD:-$root/generated/build/moderngekko-desktop}"

[[ -f "$source_dir/CMakeLists.txt" ]] || {
  echo "missing pinned ModernGekko checkout; run scripts/bootstrap-dependencies.sh" >&2
  exit 1
}

cmake -S "$source_dir" -B "$build_dir" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0 \
  -DMODERNGEKKO_FRONTEND_NAME=GalaxyPad \
  -DMODERNGEKKO_USER_DIRECTORY_NAME=GalaxyPad \
  -DMODERNGEKKO_REQUIRED_DISC_ID=RMGE01 \
  -DMODERNGEKKO_REQUIRED_DOL_SHA256=2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09 \
  -DUSE_SYSTEM_LIBS=OFF \
  -DENABLE_VULKAN=OFF \
  -DENABLE_QT=OFF \
  -DENABLE_TESTS=ON \
  -DUSE_DISCORD_PRESENCE=OFF \
  -DUSE_MGBA=OFF \
  -DUSE_RETRO_ACHIEVEMENTS=OFF \
  -DENABLE_AUTOUPDATE=OFF \
  -DENABLE_ANALYTICS=OFF \
  -DUSE_UPNP=OFF

cmake --build "$build_dir" --target moderngekko-port moderngekko-run \
  moderngekko-module-info \
  --parallel "${GALAXYPAD_JOBS:-8}"

echo "Built pinned ModernGekko desktop tools."
