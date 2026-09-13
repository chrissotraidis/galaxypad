#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
# Small synthetic identity only for this standalone test, not the mobile target.
xcrun clang++ -std=c++23 -g -fobjc-arc -fsanitize=address,undefined \
  -Wall -Wextra -Werror -framework Foundation \
  -I "$root/tests/fixtures/import" \
  "$root/tests/test-import-transaction.mm" \
  -o "$root/generated/tests/import-transaction"
"$root/generated/tests/import-transaction"
