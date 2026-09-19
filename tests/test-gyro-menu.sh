#!/usr/bin/env bash
# Headless UIKit action dispatch on an already booted Simulator; no app replacement.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fobjc-arc -fblocks -Wall -Wextra -Werror \
  -target arm64-apple-ios16.0-simulator -isysroot "$(xcrun --sdk iphonesimulator --show-sdk-path)" \
  "$root/tests/test-gyro-menu.mm" "$root/apple/ios/GalaxyPadGameOverlay.mm" \
  "$root/apple/shared/GalaxyPadSettings.mm" "$root/apple/shared/GalaxyPadDiagnostics.mm" \
  -framework UIKit -framework Foundation -framework QuartzCore -framework GameController -framework CoreGraphics \
  -o "$root/generated/tests/gyro-menu"
if [[ $# == 1 ]]; then
  xcrun simctl spawn "$1" "$root/generated/tests/gyro-menu"
fi
