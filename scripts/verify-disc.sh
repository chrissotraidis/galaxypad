#!/usr/bin/env bash
# Verify the one exact supported source image and, optionally, an extraction.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
image=${1:-}
extraction=${2:-}
expected_sha=bd0d3d4bc1376a8614fd8f4fee5df86be6bc676e9d617944918fda79ed9e3589

if [[ -z "$image" || ! -f "$image" ]]; then
  echo "usage: $0 ref/path/to/image.wbfs [generated/extraction]" >&2
  exit 2
fi

image="$(cd "$(dirname "$image")" && pwd)/$(basename "$image")"
case "$image" in
  "$root"/ref/*) ;;
  *) echo "image must be inside the ignored ref directory" >&2; exit 2 ;;
esac

actual_sha="$(shasum -a 256 "$image" | awk '{print $1}')"
[[ "$actual_sha" == "$expected_sha" ]] || {
  echo "unsupported image SHA-256: $actual_sha" >&2
  exit 1
}

wit="$root/ref/tools/wit-v3.05a-r8638-mac/bin/wit"
[[ -x "$wit" ]] || {
  echo "missing pinned WIT under ref/tools; see docs/DEPENDENCIES.md" >&2
  exit 1
}
id6="$(arch -x86_64 "$wit" ID6 "$image")"
[[ "$id6" == RMGE01 ]] || {
  echo "unsupported title ID: $id6" >&2
  exit 1
}

if [[ -n "$extraction" ]]; then
  [[ -f "$extraction/sys/boot.bin" && -f "$extraction/sys/main.dol" ]] || {
    echo "incomplete extraction: $extraction" >&2
    exit 1
  }
  main_sha="$(shasum -a 256 "$extraction/sys/main.dol" | awk '{print $1}')"
  [[ "$main_sha" == 2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09 ]] || {
    echo "extracted main.dol does not match the supported input" >&2
    exit 1
  }
fi

echo "Verified exact GalaxyPad input: RMGE01 revision 0 ($actual_sha)"
