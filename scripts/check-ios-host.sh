#!/usr/bin/env bash
# Compile-only check; not link, launch or lifecycle acceptance.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
[[ -f "$root/generated/build/ios-simulator-app/GalaxyPadDiscIdentity.h" ]] || {
  echo "Configure the Simulator app first to generate GalaxyPadDiscIdentity.h" >&2
  exit 1
}
xcrun --sdk iphonesimulator clang++ -std=c++23 -fobjc-arc -fblocks \
  -target arm64-apple-ios16.0-simulator \
  -D_ARCH_64=1 -D_M_ARM_64=1 \
  -isysroot "$(xcrun --sdk iphonesimulator --show-sdk-path)" \
  -I"$root/ref/ModernGekko/include" \
  -isystem "$root/ref/ModernGekko/vendor/dolphin/GXRuntime/include" \
  -isystem "$root/ref/ModernGekko/vendor/dolphin/Source/Core" \
  -isystem "$root/ref/ModernGekko/vendor/dolphin/Externals/fmt/fmt/include" \
  -isystem "$root/generated/build/ios-simulator-core/vendor/dolphin/Source/Core" \
  -I"$root/generated/build/ios-simulator-app" \
  -Wall -Wextra -Werror -fsyntax-only "$root/apple/ios/GalaxyPadCoreHost.mm"
