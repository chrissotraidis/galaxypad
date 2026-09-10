"""Round-trip current XF overlays in a disposable tree, never the live vendor."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
vendor = root/'ref/ModernGekko/vendor/dolphin'
patches = root/'patches/ModernGekko-dolphin'
names = ['Source/Core/VideoCommon/OpcodeDecoding.h', 'Source/Core/VideoCommon/OpcodeDecoding.cpp']
originals = {name: (vendor/name).read_bytes() for name in names}
with tempfile.TemporaryDirectory(prefix='galaxypad-xf-patches-') as directory:
    folder = Path(directory)
    for name, data in originals.items():
        path = folder/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for patch in ['0028-malformed-xf-origin.patch','0024-malformed-xf-context.patch']:
        subprocess.run(['git','apply','--reverse',str(patches/patch)],cwd=folder,check=True)
    for patch in ['0024-malformed-xf-context.patch','0028-malformed-xf-origin.patch']:
        subprocess.run(['git','apply',str(patches/patch)],cwd=folder,check=True)
    assert all((folder/name).read_bytes() == data for name,data in originals.items())
assert all((vendor/name).read_bytes() == data for name,data in originals.items())
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
assert bootstrap.index('apply --reverse "$xf_origin_patch"') < bootstrap.index(
    'apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$xf_context_patch"')
assert bootstrap.count('xf_origin_peeled=false') == 2
print('XF overlays peel/reapply byte-exact; live source unchanged; bootstrap order checked')
