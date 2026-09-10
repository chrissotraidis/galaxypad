"""Guard runtime-owned profile setup order; runtime save/load remains required."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
source = (root/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
block = source.split('if (!s_external_ui_common) {', 1)[1].split('\n  }', 1)[0]
calls = ['UICommon::SetUserDirectory(', 'UICommon::CreateDirectories();',
         'UICommon::Init();', 'impl->ui_initialized = true;']
assert all(block.count(call) == 1 for call in calls)
assert [block.index(call) for call in calls] == sorted(block.index(call) for call in calls)
assert source.count('UICommon::CreateDirectories();') == 1
upstream = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/UICommon/UICommon.cpp').read_text()
directories = upstream.split('void CreateDirectories()', 1)[1].split('\n}\n', 1)[0]
assert 'File::CreateFullPath(File::GetUserPath(D_STATESAVES_IDX));' in directories
patch = root/'patches/ModernGekko/0026-runtime-user-directories.patch'
digest = hashlib.sha256(patch.read_bytes()).hexdigest()
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
assert bootstrap.count(digest) == 2
assert bootstrap.index('apply --reverse "$runtime_directories_patch"') < bootstrap.index('apply --reverse "$wakeup_runtime_patch"')
assert bootstrap.index('apply "$wakeup_runtime_patch" || true') < bootstrap.index('apply "$runtime_directories_patch" || true')
scope = bootstrap.split('verify_patch_scope "$ref/ModernGekko" vendor/dolphin', 1)[1].split('lc_pair_runtime_patch=', 1)[0]
assert '"$runtime_directories_patch"' in scope
print('Runtime-owned directory creation precedes Init; external ownership and canonical patch ordering guarded')
