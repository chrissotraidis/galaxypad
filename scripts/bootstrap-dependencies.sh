#!/usr/bin/env bash
# Check out the committed dependency graph. Never apply patches or reset local work.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runtime="$root/ref/ModernGekko"
sources_only=false
references=false
for argument in "$@"; do
  case "$argument" in
    --sources-only) sources_only=true ;;
    --references) references=true ;;
    *) echo "usage: $0 [--sources-only] [--references]" >&2; exit 2 ;;
  esac
done

# Older workspaces contain patched standalone clones here. Leave those intact;
# migrate in a new checkout or explicitly relocate them before running bootstrap.
if [[ -L "$runtime" ]]; then
  echo "ref/ModernGekko is a local symlink; use a new checkout for pinned submodules." >&2
  exit 1
fi
if [[ -e "$runtime/.git" && -n "$(git -C "$runtime" status --porcelain --untracked-files=all --ignore-submodules=none)" ]]; then
  echo "Dependency checkout has local changes; preserve them before updating: $runtime" >&2
  exit 1
fi

git -C "$root" submodule sync --recursive
git -C "$root" submodule update --init --no-recommend-shallow -- ref/ModernGekko
git -C "$runtime" submodule update --init --no-recommend-shallow -- vendor/dolphin
git -C "$runtime/vendor/dolphin" submodule update --init --no-recommend-shallow -- DolRecomp
if [[ "$sources_only" == false ]]; then
  # Apple builds do not use the Qt/FFmpeg binary bundles or Windows dependencies.
  git -C "$runtime/vendor/dolphin" submodule update --init -- \
    Externals/SDL/SDL Externals/SFML/SFML Externals/bzip2/bzip2 \
    Externals/cpp-optparse/cpp-optparse Externals/cubeb/cubeb \
    Externals/curl/curl Externals/enet/enet Externals/fmt/fmt \
    Externals/glslang/glslang Externals/hidapi/hidapi-src \
    Externals/imgui/imgui Externals/implot/implot Externals/libspng/libspng \
    Externals/libusb/libusb Externals/lz4/lz4 \
    Externals/minizip-ng/minizip-ng Externals/pugixml/pugixml \
    Externals/spirv_cross/SPIRV-Cross Externals/tinygltf/tinygltf \
    Externals/watcher/watcher Externals/xxhash/xxHash \
    Externals/zlib-ng/zlib-ng Externals/zstd/zstd
  git -C "$runtime/vendor/dolphin/Externals/cubeb/cubeb" submodule update --init --recursive
fi
python3 "$root/scripts/dependency-lock.py" --root "$root"

# Research references are not part of the runtime or required by source checks.
if [[ "$references" == true ]]; then
  python3 - "$root" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
root = Path(sys.argv[1])
repositories = json.loads((root / 'config/dependencies.lock.json').read_text())['repositories']
for key, directory in [('sunpad', 'sunpad-reviewed'), ('petari', 'petari'),
                       ('modernGekkoTemplate', 'ModernGekko-Template')]:
    pin = repositories[key]
    path = root / 'ref' / directory
    if not path.exists():
        subprocess.run(['git', 'clone', '--filter=blob:none', pin['url'], str(path)], check=True)
        subprocess.run(['git', '-C', str(path), 'checkout', '--detach', pin['revision']], check=True)
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain'], text=True).strip()
    if actual != pin['revision'] or dirty:
        sys.exit(f'Research reference differs from its pin or contains edits; preserved: {path}')
PY
fi
echo "Pinned GalaxyPad dependency sources are ready; no patches were applied."
