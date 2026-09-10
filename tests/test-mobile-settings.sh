#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++20 -fobjc-arc -fblocks -fsanitize=address,undefined \
  -framework Foundation "$root/tests/test-mobile-settings.mm" \
  "$root/apple/shared/GalaxyPadSettings.mm" -o "$root/generated/tests/mobile-settings"
"$root/generated/tests/mobile-settings"
