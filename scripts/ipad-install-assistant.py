#!/usr/bin/env python3
"""Local native-dialog installer. No accounts, uploads, signing keys or game-data copies."""
import argparse
import hashlib
import pathlib
import plistlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_APP = ROOT / 'generated/device-stage.ZaTANc/GalaxyPad.app'


def run(*args):
    return subprocess.check_output(list(map(str, args)), text=True, stderr=subprocess.STDOUT)


def dialog(message, button='OK'):
    run('osascript', '-e', '''on run argv
display dialog (item 1 of argv) with title "GalaxyPad iPad Installer" buttons {item 2 of argv} default button 1
end run''', message, button)


def validate(app, signed=False):
    app = pathlib.Path(app).absolute()
    if app.is_symlink() or not app.is_dir() or app.suffix != '.app':
        raise ValueError('Choose a GalaxyPad .app bundle, not a Simulator app or IPA.')
    info = plistlib.loads((app / 'Info.plist').read_bytes())
    if info.get('CFBundleIdentifier') != 'org.galaxypad.GalaxyPad':
        raise ValueError('Bundle identifier is not org.galaxypad.GalaxyPad.')
    for relative in ('GalaxyPad', 'Frameworks/gRMGE01_recomp.dylib'):
        binary = app / relative
        if not binary.is_file():
            raise ValueError(f'Missing {relative}')
        if run('xcrun', 'lipo', '-archs', binary).strip() != 'arm64':
            raise ValueError(f'{relative} is not an ARM64 device binary.')
        metadata = run('xcrun', 'vtool', '-show-build', binary)
        if not any(line.split() == ['platform', 'IOS'] for line in metadata.splitlines()):
            raise ValueError(f'{relative} is not an iOS device binary.')
    if signed:
        if not (app / 'embedded.mobileprovision').is_file():
            raise ValueError('No provisioning profile. Re-sign the app and nested module first; see docs/INSTALL_IPAD.md.')
        run('codesign', '--verify', '--deep', '--strict', app)
    return app


def export_ipa(app):
    app = validate(app)
    # Export only the known staged build. Arbitrary input bundles could include
    # user data or credentials; signed-app installation is a separate path.
    if app != DEFAULT_APP.resolve():
        raise ValueError('IPA export accepts only the documented private candidate.')
    expected = {'GalaxyPad': '27b37908b9884d2ece7f064772127d11bc073de52cdc43cff25f1223ab8a3753',
                'Frameworks/gRMGE01_recomp.dylib': '48f455ebc33f8eb2fc58151cd722ea756db77a5738a9573a0a49f0c656110041'}
    for relative, digest in expected.items():
        if hashlib.sha256((app / relative).read_bytes()).hexdigest() != digest:
            raise ValueError('Candidate binary changed. Revalidate it before exporting.')
    forbidden = {'.wbfs', '.iso', '.rvz', '.gcm', '.sav', '.gci', '.p12', '.mobileprovision'}
    for path in app.rglob('*'):
        if path.is_symlink() or path.suffix.lower() in forbidden or path.name == 'GameData.bin':
            raise ValueError(f'Unexpected private data or symlink in bundle: {path.name}')
    output = pathlib.Path(tempfile.mkdtemp(prefix='ipad-install.', dir=ROOT / 'generated'))
    payload = output / 'Payload'
    payload.mkdir()
    run('ditto', '--norsrc', '--noextattr', app, payload / 'GalaxyPad.app')
    ipa = output / 'GalaxyPad-private-unsigned.ipa'
    run('ditto', '-c', '-k', '--norsrc', '--noextattr', '--keepParent', payload, ipa)
    digest = run('shasum', '-a', '256', ipa).split()[0]
    (output / 'SHA256.txt').write_text(f'{digest}  {ipa.name}\n')
    return ipa


def gui():
    choice = run('osascript', '-e', '''choose from list {"Export private unsigned IPA", "Install signed app on iPad", "Signing and first-launch help"} with title "GalaxyPad iPad Installer" with prompt "Private hardware test. Signing is required; no disc image or saves are included." default items {"Export private unsigned IPA"}''').strip()
    if choice == 'false':
        return
    if choice == 'Signing and first-launch help':
        run('open', ROOT / 'docs/INSTALL_IPAD.md')
    elif choice == 'Export private unsigned IPA':
        ipa = export_ipa(DEFAULT_APP)
        run('open', '-R', ipa)
        dialog('Private IPA exported and revealed in Finder. It is NOT install-signed. Re-sign BOTH the app and Frameworks/gRMGE01_recomp.dylib with your Apple identity using your trusted signing workflow. See docs/INSTALL_IPAD.md. Nothing was uploaded or installed.')
    elif choice == 'Install signed app on iPad':
        app = run('osascript', '-e', 'POSIX path of (choose file with prompt "Choose your signed GalaxyPad.app" of type {"com.apple.application-bundle"})').strip()
        app = validate(app, signed=True)
        devices = run('xcrun', 'devicectl', 'list', 'devices')
        target = run('osascript', '-e', '''on run argv
set response to display dialog ("Connected-device inventory:" & return & item 1 of argv & return & "Enter your exact iPad name or identifier. Unlock it and trust this Mac first.") with title "Install GalaxyPad" default answer "" buttons {"Cancel", "Install"} default button "Install"
return text returned of response
end run''', devices).strip()
        if not target or target.startswith('-'):
            raise ValueError('A device name or identifier is required.')
        run('xcrun', 'devicectl', 'device', 'install', 'app', '--device', target, app, '--timeout', '120')
        dialog('GalaxyPad installation succeeded. Open it on your iPad. Import your own supported Galaxy image through the app. This assistant did not launch the game, erase data or transfer your saves.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='export the private unsigned IPA without dialogs')
    args = parser.parse_args()
    try:
        if args.export:
            print(export_ipa(DEFAULT_APP))
        else:
            gui()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        message = error.output if isinstance(error, subprocess.CalledProcessError) else str(error)
        if '(-128)' not in message:  # Native Cancel is not an installation failure.
            if args.export:
                raise SystemExit(message)
            dialog('No successful installation was confirmed.\n\n' + message[-2500:])
