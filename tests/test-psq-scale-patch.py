"""Prove the prepared source overlay reproduces the tested candidate exactly."""
from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from psq_scale import transform, reference_source

source = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu.c'
checkout = source.read_text()
original = reference_source(checkout)
expected = transform(original)
assert hashlib.sha256(expected.encode()).hexdigest() == '05e221c01bead6801c51217f84398bd10f22e1b810f6d06977e04d8a801436ea'
patch = root/'patches/ModernGekko-dolphin/0022-psq-store-scale.patch'
patch_hash = '74ca7e8c82bf32d25af12bde4cf1b4318ceb7a34ad7e0925540e415227fd7486'
assert hashlib.sha256(patch.read_bytes()).hexdigest() == patch_hash
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
assert patch_hash in bootstrap
peel = bootstrap.index('if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$psq_scale_patch"')
assert peel < bootstrap.index('if git -C "$ref/ModernGekko" apply --reverse --check "$runtime_directories_patch"')
apply = bootstrap.index('apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$psq_scale_patch"')
assert apply > bootstrap.index('1350d1196b38b147477890ef0dc59d5d9e389a55a169d51913fc033be34edb69 ]]')
assert apply < bootstrap.index('verify_patch_scope "$ref/ModernGekko/vendor/dolphin" "DolRecomp"')
assert '"$wakeup_core_patch" "$psq_scale_patch"' in bootstrap
assert 'if [[ "$psq_scale_peeled" == true ]]; then' in bootstrap
with tempfile.TemporaryDirectory(prefix='galaxypad-scale-patch-') as directory:
    folder = Path(directory)
    target = folder/'GXRuntime/src/core/cpu.c'
    target.parent.mkdir(parents=True)
    target.write_text(original)
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=folder, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=folder, check=True)
    assert target.read_text() == expected
    reapplied = subprocess.run(['git', 'apply', '--check', str(patch)], cwd=folder,
                              capture_output=True)
    assert reapplied.returncode != 0
    subprocess.run(['git', 'apply', '--reverse', '--check', str(patch)], cwd=folder, check=True)
    subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=folder, check=True)
    assert target.read_text() == original
assert source.read_text() == checkout
print('Scale overlay matches tested candidate, rejects reapplication, reverses exactly; checkout unchanged')
