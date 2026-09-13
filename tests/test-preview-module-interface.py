#!/usr/bin/env python3
"""Exercise the real Mac packager with synthetic dylibs; no game code or loading."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run(list(map(str, args)), check=True, capture_output=True, text=True)


with tempfile.TemporaryDirectory(prefix='galaxypad-module-package-test-') as temporary:
    root = Path(temporary)
    app = root / 'GalaxyPad.app'
    binaries = app / 'Contents/MacOS'
    binaries.mkdir(parents=True)
    (app / 'Contents/Resources').mkdir()
    shutil.copyfile(ROOT / 'apple/macos/Info.plist', app / 'Contents/Info.plist')
    shutil.copyfile(ROOT / 'apple/macos/GalaxyPad', binaries / 'GalaxyPad')
    (binaries / 'GalaxyPad').chmod(0o755)
    host = root / 'host.c'
    host.write_text('int main(void) { return 0; }\n')
    run('xcrun', 'clang', '-arch', 'arm64', '-mmacosx-version-min=14.0',
        host, '-o', binaries / 'GalaxyPadRunner')
    shutil.copyfile(binaries / 'GalaxyPadRunner', binaries / 'GalaxyPadFrontend')
    notices = root / 'notices'
    notices.mkdir()
    (notices / 'NOTICE.txt').write_text('Synthetic test inputs; no game code.\n')
    module = binaries / 'gRMGE01_recomp.dylib'
    source = root / 'module.c'
    # The success fixture has the loader interface, not a working game module.
    # Package checks must never call it. Runtime descriptor validation is separate.
    for label, code, succeeds in [
        ('unrelated', 'int unrelated_function(void) { return 7; }\n', False),
        ('interface', 'const void *staticrecomp_get_module(void) { return 0; }\n', True),
    ]:
        source.write_text(code)
        run('xcrun', 'clang', '-dynamiclib', '-arch', 'arm64', '-mmacosx-version-min=14.0',
            '-Wl,-install_name,@rpath/gRMGE01_recomp.dylib', source, '-o', module)
        before = {p.relative_to(app): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in app.rglob('*') if p.is_file()}
        output = root / (label + '.zip')
        result = subprocess.run([
            'python3', str(ROOT / 'scripts/package-preview.py'),
            '--app', str(app), '--platform', 'macos', '--output', str(output),
            '--notices', str(notices), '--source-revision', '0' * 40,
        ], capture_output=True, text=True)
        assert (result.returncode == 0) == succeeds, (label, result.stdout, result.stderr)
        assert output.exists() == succeeds
        assert output.with_suffix('.zip.manifest.json').exists() == succeeds
        if not succeeds:
            assert 'missing staticrecomp_get_module' in result.stderr, result.stderr
        after = {p.relative_to(app): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in app.rglob('*') if p.is_file()}
        assert before == after, 'Packaging mutated the input app'

    # Reject an output inside either input tree before mkdir/copy/signing can
    # mutate it, and preserve an existing sidecar even when the archive is absent.
    for output, error in [
        (app / 'Contents/Resources/new/preview.zip', 'outside the input'),
        (notices / 'new/preview.zip', 'outside the input'),
        (root / 'existing-sidecar.zip', 'outputs must be new'),
    ]:
        sidecar = output.with_suffix(output.suffix + '.manifest.json')
        if output.name == 'existing-sidecar.zip':
            sidecar.write_text('existing evidence')
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        result = subprocess.run([
            'python3', str(ROOT / 'scripts/package-preview.py'),
            '--app', str(app), '--platform', 'macos', '--output', str(output),
            '--notices', str(notices), '--source-revision', '0' * 40,
        ], capture_output=True, text=True)
        assert result.returncode != 0 and error in result.stderr, result.stderr
        assert not output.exists()
        assert before == {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        if output.name != 'existing-sidecar.zip':
            assert not output.parent.exists(), 'Invalid output created directories in the input'
print('Preview module interface rejection and successful signing/package path passed.')
