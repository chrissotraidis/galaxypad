#!/usr/bin/env python3
"""Package an explicit app as an experimental preview; never mutate build/install inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import zipfile

FORBIDDEN = {'.iso', '.gcm', '.rvz', '.wia', '.wbfs', '.gcz', '.dol', '.rel', '.rso',
             '.sav', '.gci', '.raw', '.p12', '.pem', '.key', '.cer', '.mobileprovision',
             '.provisionprofile', '.log', '.trace', '.crash', '.ips', '.profraw', '.profdata'}
PRIVATE_DIRS = {'saves', 'save', 'nand', 'gamedata', 'game-data', 'screenshots', 'extracted'}
MACH_MAGICS = {b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xca\xfe\xba\xbe'}


def run(*args):
    return subprocess.check_output(list(map(str, args)), text=True, stderr=subprocess.STDOUT)


def audit_tree(app):
    for path in app.rglob('*'):
        rel = path.relative_to(app)
        if path.suffix.lower() in FORBIDDEN or path.name.lower() == 'gamedata.bin' or any(p.lower() in PRIVATE_DIRS for p in rel.parts):
            raise ValueError(f'Private content: {rel}')
        if path.is_symlink() and (os.path.isabs(os.readlink(path)) or not path.resolve().is_relative_to(app.resolve()) or not path.exists()):
            raise ValueError(f'Unsafe symlink: {rel}')


def audit_archive(path):
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            p = Path(item.filename)
            if p.is_absolute() or '..' in p.parts or p.suffix.lower() in FORBIDDEN or p.name.lower() == 'gamedata.bin' or any(x.lower() in PRIVATE_DIRS for x in p.parts):
                raise ValueError(f'Unsafe archive entry: {item.filename}')
        bad = archive.testzip()
        if bad:
            raise ValueError(f'Corrupt archive entry: {bad}')


def publish_archive(candidate, output, manifest):
    """Create both outputs exclusively, preserving artifacts from another run."""
    manifest_path = output.with_suffix(output.suffix + '.manifest.json')
    manifest['archive_sha256'] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    created = []
    try:
        with output.open('xb') as archive_file:
            created.append(output)
            with manifest_path.open('x') as manifest_file:
                created.append(manifest_path)
                with candidate.open('rb') as source:
                    shutil.copyfileobj(source, archive_file)
                manifest_file.write(json.dumps(manifest, indent=2) + '\n')
    except Exception:
        # Remove only outputs this invocation created, never a competing file.
        for path in reversed(created):
            path.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', required=True, type=Path)
    parser.add_argument('--platform', required=True, choices=['ios', 'macos'])
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--notices', required=True, type=Path, help='Reviewed directory of notices and corresponding-source instructions')
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    if len(args.source_revision) != 40 or any(c not in '0123456789abcdef' for c in args.source_revision):
        parser.error('source revision must be the full commit SHA')
    manifest_path = args.output.with_suffix(args.output.suffix + '.manifest.json')
    if (not args.app.is_dir() or args.app.is_symlink() or not args.notices.is_dir()
            or any(p.exists() or p.is_symlink() for p in (args.output, manifest_path))):
        parser.error('app/notices must exist; archive and manifest outputs must be new')
    if any(args.output.resolve().is_relative_to(p.resolve()) for p in (args.app, args.notices)):
        parser.error('output must be outside the input app and notices directory')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='galaxypad-preview-') as temp:
        stage = Path(temp)
        parent = stage / 'Payload' if args.platform == 'ios' else stage
        parent.mkdir(exist_ok=True)
        app = parent / 'GalaxyPad.app'
        run('ditto', '--norsrc', '--noextattr', args.app, app)
        # Remove personal provisioning and signature metadata only in the copy.
        for path in list(app.rglob('*')):
            if path.name == '_CodeSignature' and path.is_dir():
                shutil.rmtree(path)
            elif path.suffix.lower() in {'.mobileprovision', '.provisionprofile'}:
                path.unlink()
        audit_tree(app)
        resources = app if args.platform == 'ios' else app / 'Contents/Resources'
        shutil.copytree(args.notices, resources / 'PreviewNotices')
        audit_tree(app)
        info = plistlib.loads((app / ('Info.plist' if args.platform == 'ios' else 'Contents/Info.plist')).read_bytes())
        expected_id = 'org.galaxypad.GalaxyPad' if args.platform == 'ios' else 'com.galaxypad.GalaxyPad.macos'
        if info.get('CFBundleIdentifier') != expected_id:
            raise ValueError('Unexpected bundle identifier')
        if args.platform == 'ios':
            run('python3', Path(__file__).with_name('check-ios-game-mode.py'), app / 'Info.plist')
        module = app / ('Frameworks/gRMGE01_recomp.dylib' if args.platform == 'ios' else 'Contents/MacOS/gRMGE01_recomp.dylib')
        if not module.is_file():
            raise ValueError('Missing AOT module')
        # Architecture alone does not make a library a StaticRecomp module.
        # Check the loader entry point before signing or publishing the copy;
        # never dlopen an input merely to inspect its interface.
        module_exports = set(run('xcrun', 'nm', '-gjU', module).splitlines())
        if '_staticrecomp_get_module' not in module_exports:
            raise ValueError('AOT module is missing staticrecomp_get_module')
        binaries = []
        for path in app.rglob('*'):
            if not path.is_file() or path.is_symlink():
                continue
            with path.open('rb') as stream:
                macho = stream.read(4) in MACH_MAGICS
            if not macho:
                continue
            binaries.append(path)
            if run('xcrun', 'lipo', '-archs', path).strip() != 'arm64':
                raise ValueError(f'Unexpected architecture: {path.relative_to(app)}')
            platform = 'IOS' if args.platform == 'ios' else 'MACOS'
            if not any(line.split() == ['platform', platform] for line in run('xcrun', 'vtool', '-show-build', path).splitlines()):
                raise ValueError('Wrong binary platform')
            for line in run('xcrun', 'otool', '-L', path).splitlines()[1:]:
                dependency = line.strip().split(' (')[0]
                if not dependency.startswith(('/System/Library/', '/usr/lib/', '@rpath/', '@loader_path/', '@executable_path/')):
                    raise ValueError(f'Nonportable dependency in {path.relative_to(app)}')
            # Strip debug symbols only, preserving all exported runtime/module symbols.
            exports = set(run('xcrun', 'nm', '-gjU', path).splitlines())
            run('xcrun', 'strip', '-S', path)
            if set(run('xcrun', 'nm', '-gjU', path).splitlines()) != exports:
                raise ValueError('Debug stripping changed exported symbols')
            # A new ad-hoc signature does not retain the developer certificate or entitlements.
            subprocess.run(['codesign', '--remove-signature', str(path)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            run('codesign', '--force', '--sign', '-', '--timestamp=none', path)
        if not binaries:
            raise ValueError('No native binaries')
        run('codesign', '--force', '--deep', '--sign', '-', '--timestamp=none', app)
        run('codesign', '--verify', '--deep', '--strict', app)
        signature = run('codesign', '-dvv', app)
        if 'Signature=adhoc' not in signature or 'Authority=' in signature:
            raise ValueError('Personal signature remains')
        manifest = {'source_revision': args.source_revision, 'platform': args.platform,
                    'version': info.get('CFBundleShortVersionString'), 'build': info.get('CFBundleVersion'),
                    'signing': 'ad-hoc; iOS requires recipient signing', 'includes_generated_aot_module': True,
                    'files': {str(p.relative_to(app)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(app.rglob('*')) if p.is_file() and not p.is_symlink()}}
        target = parent if args.platform == 'ios' else app
        candidate = stage / ('preview.ipa' if args.platform == 'ios' else 'preview.zip')
        run('ditto', '-c', '-k', '--norsrc', '--noextattr', '--keepParent', target, candidate)
        audit_archive(candidate)
        publish_archive(candidate, args.output, manifest)
        print(f"{manifest['archive_sha256']}  {args.output.name}")


if __name__ == '__main__':
    main()
