#!/usr/bin/env bash
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

for path in \
  ref/example.wbfs \
  generated/aot/game.c \
  docs/artifacts/private.log \
  nand/title/save.bin \
  saves/progress.sav; do
  git -C "$root" check-ignore -q "$path" || {
    echo "expected ignored path: $path" >&2
    exit 1
  }
done

echo "Repository ignore policy tests passed"
