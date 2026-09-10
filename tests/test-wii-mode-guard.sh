#!/usr/bin/env bash
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
temp_dir="$(mktemp -d)"
trap 'rm -rf "$temp_dir"' EXIT

if GALAXYPAD_TITLES_DB="$temp_dir/missing" "$root/scripts/generate-aot.sh" --preflight >/dev/null 2>&1; then
  echo "guard accepted a missing title database" >&2
  exit 1
fi
printf 'GMSE01 = Wrong game\n' > "$temp_dir/wrong-titles.txt"
if GALAXYPAD_TITLES_DB="$temp_dir/wrong-titles.txt" "$root/scripts/generate-aot.sh" --preflight >/dev/null 2>&1; then
  echo "guard accepted a title database without RMGE01" >&2
  exit 1
fi

"$root/scripts/generate-aot.sh" --preflight
echo "Wii/Broadway fail-closed guard tests passed"
