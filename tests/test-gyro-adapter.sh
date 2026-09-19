#!/usr/bin/env bash
# Headless process in an already booted Simulator; no app installation or UI switch.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fobjc-arc -fblocks -Wall -Wextra -Werror \
  -target arm64-apple-ios16.0-simulator -isysroot "$(xcrun --sdk iphonesimulator --show-sdk-path)" \
  "$root/tests/test-gyro-adapter.mm" "$root/apple/ios/GalaxyPadGyroPointer.mm" \
  "$root/apple/shared/GalaxyPadSettings.mm" \
  -framework UIKit -framework Foundation -framework CoreMotion -framework GameController -framework QuartzCore \
  -o "$root/generated/tests/gyro-adapter"
if [[ $# == 1 ]]; then
  xcrun simctl spawn "$1" "$root/generated/tests/gyro-adapter"
fi
