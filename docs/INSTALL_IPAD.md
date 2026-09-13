# Install GalaxyPad on iPhone or iPad — experimental preview

Download the IPA from the [public preview release](https://github.com/chrissotraidis/galaxypad/releases/tag/v0.1.0-preview.1). It supports both device families and requires your own Apple signing. Skip the local export step below when using that release IPA. The installation assistant described here is a development helper; its export action remains pinned to an older local candidate.

See [current preview notes](PREVIEW-2026-09-13.md) for build 13 and validation limits. Historical evidence below does not supersede that release record.

## Local development assistant

Double-click **Install on iPad.command** in the project folder. This opens native
Mac dialogs, not a website. Xcode command-line tools and Python 3 are required.
If Finder refuses to open it, run `bash "Install on iPad.command"` in Terminal
from this project. Do not disable Gatekeeper globally.

**A Git pull transfers source, not the private app.** The export action currently
uses the prepared R913 candidate in ignored `generated/` on the development Mac.
On a different checkout it will report that the candidate is missing. Transfer
your private IPA separately from that Mac, or complete the documented local
device build with your own verified game input. The preview release now provides a separate audited IPA; the historical assistant does not produce that artifact.

### Building a new device candidate without the old private cache

After bootstrapping dependencies and verifying/extracting the exact supported
image to `generated/extracted/run1`, a fresh checkout can compile an unprofiled
module with `bash scripts/build-ios-device-fresh-module.sh`. This uses the pinned
Broadway C recompiler, indexed 1,024-instruction chunks, the reviewed cycle fix,
and the device module template. It does not require or replace the historical
accepted module or PGO profile. It produces a new candidate whose performance
and hardware behavior must be checked separately.

Build the core and host from the same pinned graph. The host build provisions
that core automatically; iPhoneOS selects the maintained audio variant and its
matching Mixer layout. Do not combine an older core archive with fresh headers.

```sh
GALAXYPAD_IOS_SDK=iphoneos bash scripts/build-ios-simulator-core.sh
GALAXYPAD_IOS_SDK=iphoneos bash scripts/build-ios-simulator-app.sh
```

Stage that host with the fresh module explicitly:

```sh
bash scripts/stage-private-ios-device.sh \
  generated/build/ios-device-app/GalaxyPad.app \
  generated/build/ios-device-fresh-module/gRMGE01_recomp.dylib
```

Signing, installation, and game-data transfer remain separate private steps.

On 2026-09-10 this path produced a signed app that installed and visibly reached
save-file setup on an attached iPad14,5 running iPadOS 26.6.1. The unsigned host
matched R913 (`27b37908…a3753`); the fresh module was
`2a7d1ec1…d5295` before signing. This establishes device startup, not sustained
gameplay, audio quality, or full-game acceptance.

That private installation stored `RMGE01.wbfs` and an `RMGE01/` folder containing
extracted `sys/` and `files/ModuleData/` under
`Library/Application Support/GalaxyPad/GameData/`.
The existing runtime boots directly from the WBFS; it does not need a duplicate
extracted asset tree for this path. A full USB readback matched the pinned WBFS
SHA-256 and all seven metadata files. The ordinary in-app import still requires
9 GiB and performs its existing full extraction.

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
for `org.galaxypad.GalaxyPad` covering your iPad. Profile expiry, device registration and
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

## Historical assistant evidence and limitations

R913 private candidate `generated/device-stage.ZaTANc/GalaxyPad.app` is a Release
IOS/ARM64 build with module48f455eb. Signing/device installation remains untested
until hardware and credentials are available. Simulator binaries are rejected.
The assistant's IPA path is private/local and is not a supported LiveContainer,
computer-free, public-distribution or automatic-signing promise.

### September 11 controls and logging update

Private build 0.1.0 (2) was installed in place and relaunched on the same iPad, preserving the existing save slot; first boot normalized checksum/Mii metadata in that slot, so a byte-for-byte post-boot hash is not expected. It adds a Galaxy-style app pause panel, a labeled Start + control, SunPad-oriented iPad spacing, and opt-in frame/audio/performance diagnostics. See [physical feedback and remaining issues](IPAD-FEEDBACK-2026-09-11.md); pointer accuracy, plaza performance and physical-controller acceptance remain open.
