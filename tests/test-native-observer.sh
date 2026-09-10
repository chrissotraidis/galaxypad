#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang -std=c11 -fsanitize=address,undefined -Wall -Wextra -Werror \
  -I "$root/ref/ModernGekko/include" "$root/tests/test-native-observer.c" \
  "$root/apple/shared/GalaxyPadNativeObserver.c" -o "$root/generated/tests/native-observer"
"$root/generated/tests/native-observer"
