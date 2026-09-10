# Install GalaxyPad on your iPad — private test

Double-click **Install on iPad.command** in the project folder. This opens native
Mac dialogs, not a website. Xcode command-line tools and Python 3 are required.
If Finder refuses to open it, run `bash "Install on iPad.command"` in Terminal
from this project. Do not disable Gatekeeper globally.

**A Git pull transfers source, not the private app.** The export action currently
uses the prepared R913 candidate in ignored `generated/` on the development Mac.
On a different checkout it will report that the candidate is missing. Transfer
your private IPA separately from that Mac, or complete the documented local
device build with your own verified game input. No release asset is uploaded.

## 1. Export the app

Choose **Export private unsigned IPA**. The assistant packages the current
physical-iOS candidate and reveals it in Finder with a SHA-256 file alongside.
It includes the locally generated game executable module, but not the disc
image, extracted game assets, saves or signing credentials. Keep it private;
this is not a public release, App Store or TestFlight build.

## 2. Sign it with your Apple identity

Use your trusted iOS re-signing/install workflow. The app AND its nested
`Frameworks/gRMGE01_recomp.dylib` must be signed. The unsigned IPA cannot be
installed directly. This assistant does not request your Apple password, obtain
certificates, create provisioning profiles or accept Apple agreements.

For development signing, set up your Apple account/team in Xcode and a profile
for `org.galaxypad.GalaxyPad` covering your iPad. The current Mac has no valid
signing identity on the last check. Profile expiry, device registration and
entitlements must match; ad-hoc Mac signing with `codesign -s -` is insufficient.
If your signing tool also installs the IPA, use that tool's install action.

## 3. Install a signed app with the assistant

Connect/unlock your iPad and trust this Mac. Enable Developer Mode on the iPad
if requested by the development-install workflow. Choose **Install signed app
on iPad**, select the signed `.app` (not the IPA), then enter the exact iPad name
or identifier shown in the dialog. The assistant checks the device platform,
bundled module, provisioning-profile presence and code signatures before asking
Apple's device service to install. Apple performs final provisioning validation.

Installation updates this bundle identifier in place; it does not deliberately
erase saves. Back up any important existing GalaxyPad save before testing an
update. Do not uninstall the old app as a troubleshooting shortcut.

## 4. First launch

Open GalaxyPad yourself. Import your locally supplied, supported RMGE01 revision0
Galaxy image using the native game-data import UI. Keep at least9 GiB free on
the iPad for import/extraction/headroom. Do not download another image or include
game data in the IPA. Original disc and saves remain separate from app packaging.

Test movement/jump/spin, pointer, sound and the three-dot menu. Use the local
diagnostic report preview before sharing anything. Follow
[the first hardware test](PHYSICAL-IPAD-FIRST-TEST.md) for comparable scenes.
The UI and performance are experimental; neither device boot nor60FPS is proven.

## Current evidence and limitations

R913 private candidate `generated/device-stage.ZaTANc/GalaxyPad.app` is a Release
IOS/ARM64 build with module48f455eb. Signing/device installation remains untested
until hardware and credentials are available. Simulator binaries are rejected.
The assistant's IPA path is private/local and is not a supported LiveContainer,
computer-free, public-distribution or automatic-signing promise.
