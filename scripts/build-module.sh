#!/usr/bin/env bash
# Build the exact RMGE01 Broadway module through the pinned ModernGekko port tool.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
extraction="${GALAXYPAD_EXTRACTION:-$root/generated/extracted/run1}"
build_dir="${GALAXYPAD_DESKTOP_BUILD:-$root/generated/build/moderngekko-desktop}"
output="${GALAXYPAD_MODULE_OUTPUT:-$root/generated/modules}"
# inspect runs from the caller's directory, build runs from build_dir. Keep
# both operations on the same cache when a relative override is supplied.
[[ "$output" == /* ]] || output="$root/$output"
chunk_instructions="${GALAXYPAD_C_CHUNK_INSTRUCTIONS:-1024}"
dispatch_lookup="${GALAXYPAD_DISPATCH_LOOKUP:-indexed}"
profile_use="${GALAXYPAD_PGO_PROFILE:-}"
port="$build_dir/moderngekko-port"
titles="$root/config/gametdb-titles.txt"

"$root/scripts/generate-aot.sh" --preflight
[[ -x "$port" ]] || {
  echo "missing ModernGekko port tool; run scripts/build-desktop-tools.sh" >&2
  exit 1
}

mkdir -p "$build_dir/database" "$output"
cp "$titles" "$build_dir/database/titles.txt"
export MACOSX_DEPLOYMENT_TARGET="${GALAXYPAD_MACOS_DEPLOYMENT_TARGET:-14.0}"

build_options=(
  --backend c
  --toolchain clang
  --c-chunk-instructions "$chunk_instructions"
  --dispatch-lookup "$dispatch_lookup"
  --output "$output"
)
if [[ -n "$profile_use" ]]; then
  [[ "$profile_use" == /* ]] || profile_use="$root/$profile_use"
  [[ -f "$profile_use" ]] || {
    echo "missing PGO profile: $profile_use" >&2
    exit 1
  }
  build_options+=(--profile-use "$profile_use")
fi

"$port" inspect "$extraction" --output "$output"
(
  cd "$build_dir"
  ./moderngekko-port build "$extraction" "${build_options[@]}"
)
"$port" inspect "$extraction" --output "$output"

echo "Built and selected the exact RMGE01 Broadway module."
