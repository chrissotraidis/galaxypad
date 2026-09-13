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
    if args.output.exists() or not args.app.is_dir() or args.app.is_symlink() or not args.notices.is_dir():
        parser.error('app/notices must exist; output must be new')
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
        module = app / ('Frameworks/gRMGE01_recomp.dylib' if args.platform == 'ios' else 'Contents/MacOS/gRMGE01_recomp.dylib')
        if not module.is_file():
            raise ValueError('Missing AOT module')
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
        shutil.copyfile(candidate, args.output)
        manifest['archive_sha256'] = hashlib.sha256(args.output.read_bytes()).hexdigest()
        args.output.with_suffix(args.output.suffix + '.manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(f"{manifest['archive_sha256']}  {args.output.name}")


if __name__ == '__main__':
    main()
