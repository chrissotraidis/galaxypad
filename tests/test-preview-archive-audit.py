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
    # Outputs may appear while packaging/signing runs after the preflight check.
    # Publishing must preserve either competing artifact and clean only its own.
    candidate = root / 'candidate.zip'
    candidate.write_bytes(b'synthetic archive')
    output = root / 'release.zip'
    sidecar = root / 'release.zip.manifest.json'
    for competing in (output, sidecar):
        competing.write_bytes(b'other run evidence')
        try:
            module.publish_archive(candidate, output, {})
        except FileExistsError:
            pass
        else:
            raise AssertionError('Overwrote competing output')
        assert competing.read_bytes() == b'other run evidence'
        assert not (sidecar if competing == output else output).exists()
        competing.unlink()
    module.publish_archive(candidate, output, {})
    assert output.read_bytes() == candidate.read_bytes()
    import hashlib
    import json
    assert json.loads(sidecar.read_text())['archive_sha256'] == hashlib.sha256(candidate.read_bytes()).hexdigest()
print('Preview archive privacy and concurrent output preservation checks passed.')
