#!/usr/bin/env python3
"""Packaging must reject private data and escaping paths before publication."""
import importlib.util
from pathlib import Path
import tempfile
import zipfile

spec = importlib.util.spec_from_file_location('package_preview', Path(__file__).resolve().parents[1] / 'scripts/package-preview.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    for name in ['Payload/GalaxyPad.app/GameData.bin', 'Payload/GalaxyPad.app/saves/file.bin',
                 'Payload/GalaxyPad.app/disc.RVZ', '../escape', '/absolute',
                 'Payload/GalaxyPad.app/embedded.mobileprovision']:
        archive = root / 'bad.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            z.writestr(name, b'private')
        try:
            module.audit_archive(archive)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Accepted {name}')
    archive = root / 'good.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('Payload/GalaxyPad.app/Frameworks/gRMGE01_recomp.dylib', b'generated module permitted')
        z.writestr('Payload/GalaxyPad.app/Sys/GameSettings/RMG.ini', b'[Core]')
    module.audit_archive(archive)
    app = root / 'GalaxyPad.app'
    app.mkdir()
    (app / 'escape').symlink_to('/etc/passwd')
    try:
        module.audit_tree(app)
    except ValueError:
        pass
    else:
        raise AssertionError('Accepted escaping symlink')
print('Preview archive privacy audit passed.')
