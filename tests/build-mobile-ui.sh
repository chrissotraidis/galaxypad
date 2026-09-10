#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
app="$root/generated/tests/OverlayTests.app"
sdk="$(xcrun --sdk iphonesimulator --show-sdk-path)"
mkdir -p "$app"
xcrun clang++ -std=c++23 -fobjc-arc -fblocks -Wall -Wextra \
  -target arm64-apple-ios16.0-simulator -isysroot "$sdk" \
  "$root/tests/mobile-ui/main.mm" "$root/apple/ios/GalaxyPadGameOverlay.mm" \
  "$root/apple/ios/GalaxyPadAboutViewController.mm" \
  "$root/apple/shared/GalaxyPadSettings.mm" \
  -framework UIKit -framework Foundation -framework QuartzCore -framework GameController -framework CoreGraphics \
  -o "$app/OverlayTests"
cp "$root/tests/mobile-ui/Info.plist" "$app/Info.plist"
