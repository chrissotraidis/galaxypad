# GalaxyPad

<img src="apple/ios/Assets.xcassets/AppIcon.appiconset/AppIcon.png" width="128" alt="GalaxyPad orbital spiral app icon">

A native Apple app experience for Super Mario Galaxy, built around an exact-game
ahead-of-time recompilation pipeline, Metal rendering, and SunPad-derived touch
controls and native menus. Game code is compiled to native ARM64 ahead of time;
a Dolphin-derived runtime still supplies Wii hardware emulation and interpreter
fallbacks. iOS does not use a runtime PowerPC JIT.

**Private development build · not release-ready · no game data included**

## Current status

GalaxyPad boots and has visible gameplay evidence on macOS, iPad Simulator, and
iPhone Simulator.
That is not full-game or shipping acceptance. Performance, audio, pointer accuracy,
touch ergonomics, lifecycle reliability, and physical-device testing remain open.

| Platform | Current boundary |
| --- | --- |
| Apple silicon Mac | Packaged app and gameplay; one measured stationary plaza window reached 59.95 VI/s. Sustained performance across the game is not accepted. |
| iPad Simulator | Corrected depth access restores Pull Star activation and level entry. Heavy-scene logging-off samples are 45–49 frame events/s. Earlier 56–60 and audio results used disabled depth and do not establish playable-config acceptance. |
| iPhone Simulator | A persisted new file loads into the opening plaza and diagnostic movement works. Recent gameplay windows were about 31–46 frame events/s under concurrent host load; touch and sustained performance are not accepted. |
| Physical iPad | Updated in place with the depth-access, Menu-event and pointer-handoff fixes; saves preserved and launch verified. User gameplay/input confirmation and performance acceptance remain open. |
| Physical iPhone | Current candidate has no physical performance acceptance. |

HUD readings measure frame events, **not guaranteed displayed FPS**. Logging-off
performance and separate audio/tail diagnostics are reported in the
[September 12 performance handoff](docs/PERFORMANCE-2026-09-12.md). Simulator results
cannot establish how the app performs on physical hardware.

See [current status](docs/STATUS.md), [development journal](docs/JOURNAL.md),
[original PRD](docs/GALAXYPAD-PRD.md), and [active goal loop](docs/GALAXYPAD-GOAL-LOOP.md).
The [release-readiness checklist](docs/RELEASE-READINESS.md) records the current
no-go decision and outstanding exact-candidate gates.

## Downloads

There is no approved public app, IPA, TestFlight, or release download. Do not treat
local experimental packages as supported releases. Publication and distribution
remain subject to the [rights and packaging gates](docs/RIGHTS-STATUS.md).

## Supported game data

The current pipeline accepts only the pinned **RMGE01, revision 0** input described
in [disc identity](config/galaxypad-disc.json). Another region, revision, modified
image, or even a different container hash is not automatically supported.

Supply your own authorized local image. GalaxyPad does not download games.
Keep images in ignored `ref/` and extractions, generated modules, saves and runtime
evidence in ignored local storage. Never commit those files.

## Build from source

Development currently targets Apple silicon with full Xcode and its iOS SDKs,
CMake, Ninja, and the pinned dependencies listed in
[DEPENDENCIES](docs/DEPENDENCIES.md) and the [dependency lock](config/dependencies.lock.json).
Configured minimums are macOS 14 and iOS/iPadOS 16; these are not tested-device
compatibility promises. The pinned Intel WIT tool also requires Rosetta.

**The mobile build is currently tied to accepted local module and PGO artifacts.**
It is not yet a one-command clean-clone build. Scripts reject mismatched inputs;
do not bypass their identity checks to make a build succeed.

Run commands from the repository root. Source setup and exact-image verification:

```sh
bash scripts/bootstrap-dependencies.sh
bash scripts/verify-disc.sh ref/supermariogalaxy.wbfs
```

With the verified extraction already prepared at `generated/extracted/run1`,
the desktop stages are:

```sh
bash scripts/build-desktop-tools.sh
bash scripts/generate-aot.sh
bash scripts/build-module.sh
bash scripts/build-macos-app.sh
```

The default desktop package is `generated/macos/GalaxyPad.app`. Read
[executable coverage](docs/EXECUTABLE-COVERAGE.md) and the build scripts before
replacing an accepted module with a newly generated one.

For a prepared, identity-matched mobile workspace, the Simulator stages are:

```sh
bash scripts/build-ios-simulator-core.sh
bash scripts/provision-ios-simulator-core.sh
bash scripts/build-ios-simulator-module.sh
bash scripts/build-ios-simulator-app.sh
```

The app is produced under `generated/build/ios-simulator-app/`. A Simulator app is
not a device app. The scripts select a separate device lane with
`GALAXYPAD_IOS_SDK=iphoneos`; signing and private staging are separate steps in
`scripts/stage-private-ios-device.sh`. See [mobile implementation](docs/MOBILE-IMPLEMENTATION.md).

## Install on your physical iPad

Double-click **Install on iPad.command** for native Mac setup dialogs:

- Export the current private unsigned IPA and reveal it in Finder.
- Install a signed GalaxyPad app onto your connected iPad.
- Open signing and first-launch instructions.

Follow [Install on iPad](docs/INSTALL_IPAD.md). An Apple signing identity and
matching provisioning profile are still required; the assistant does not create
them or ask for your Apple password. The candidate is experimental; installation and early iPad gameplay do not
establish release readiness. No game image or save is included or uploaded.

## First launch and game data

Use the mobile three-dot menu's game-data import actions for the supported input.
The host validates identity rather than accepting arbitrary games. Import requires
at least 9 GiB available for the private image copy, extraction and headroom;
existing data and saves are not counted as reclaimable space.

For a private self-contained Simulator bundle, stage the built host and module
with `GALAXYPAD_IOS_SDK=iphonesimulator bash scripts/stage-private-ios-device.sh APP_PATH`.
Despite its historical name, this script validates either SDK explicitly; its
default remains device staging. Sign the copied Simulator module and then the
copied app ad hoc before installation. Staging alone does not sign or install.
Import, data
removal, and saves are separate responsibilities—read
[save and NAND handling](docs/SAVE-AND-NAND.md) before changing local data.
The desktop development package uses its prepared local module/data workflow;
it does not imply mobile import or packaging acceptance.

Run **only one game or Simulator at a time** during validation. Do not erase a
Simulator or replace a save merely to resolve a launch problem.

## Controls and the three-dot menu

The active mobile overlay adapts SunPad's actual controls/editor and native
`UIMenu`, with Galaxy-specific Wii Remote + Nunchuk actions. It is not a claim
that Galaxy originally supports a GameCube controller.

- Movement, pointer aim, A/B actions and Spin have distinct input paths.
- Controls includes a Touch Control Guide, touch visibility, layout settings, controller mapping, and
  optional tilt and extra Wii buttons. Rarely used buttons need not stay visible.
- Touch Tilt Stick offers 0.5× / 1× / 1.5× sensitivity, vertical inversion and
  recenter. These affect only touch tilt, not movement or controller input;
  completing ball/ray stages with this route remains unverified.
- Display contains rendering options; unsupported aspect-ratio choices are
  currently disabled. Higher rendering resolution is not a CPU slowdown fix.
- Audio contains main-volume presets and mute, preserving the chosen level when
  unmuted. Packaged Simulator menu/stop/relaunch retention is checked; audible
  output validation and separate Wii Remote speaker volume are still pending.
- Game-data actions, diagnostic sharing, About and confirmed Stop are available
  through the native menu, subject to host support.
- After stopping, gameplay controls disappear and **Restart Game** starts a new
  runtime without closing the app. One packaged iPhone Simulator stop/restart
  cycle is verified; broader lifecycle and physical-device coverage remain open.
- Game Data & Save Status shows the supported revision and expected DOL hash,
  plus imported-image/save-file presence. It does not revalidate data or inspect
  completed stars; a detected file is not proof of a healthy save.

Exact mappings, pointer limitations and tested interactions live in
[Input and pointer](docs/INPUT-AND-POINTER.md). The desktop diagnostic defaults
are WASD movement, mouse pointer, J=A, K=B, U=C, I=Z, L=Spin and Return=Plus.
These are not a final editable desktop-control specification.

Touch layout, simultaneous input, menu dismissal/input clearing, and small-screen
usability still require acceptance. Do not infer physical multitouch usability
from a scripted Simulator test.

To adjust controls, open **Controls → Touch Control Settings → Move controls**.
Select a control to change its size, then choose **Done**. **Reset This Device
Layout** restores positions and sizes for that device, preserving opacity and
controller-visibility preferences. Custom positions survive default-layout
updates. Known phone issues include overlap with Back and some story text. The
default phone pause position now clears the observed confirmation and plaza views;
its gameplay pause behavior still needs a conclusive input check.
These are open layout defects, not a finished touch experience.

## Diagnostics and troubleshooting

Use **Share Diagnostic Log** in the three-dot menu. Review the exported contents
before sharing; keep game data, saves, private paths and captured game media out
of public reports. Include the app/module identity, device or Simulator model,
scene, steps to reproduce, and whether audio slows with the picture.

**Slow gameplay or cutscenes:** this is an open project defect, not something we
assume is your machine. Compare the same scene and separate CPU time, presentation,
audio and host pressure. Experimental native movie decoding is off by default
and is not a general gameplay fix. See [performance notes](docs/PERF.md).

**Input appears frozen:** confirm the game has focus, the menu/editor is closed,
and controls are enabled. Diagnostic desktop profiles can disable background
input. Do not repeatedly send inputs without checking the visible game state.

**Build rejects a hash:** check the exact pinned input and artifact provenance;
do not disable the guard or substitute a different revision.

**Storage pressure:** `generated/` contains large local build and evidence files.
Inventory exact paths first; preserve active packages, source images and saves.
No blanket cleanup command is recommended.

## Validation

`bash scripts/check-repository.sh` runs repository checks. UIKit checks are
separate: `bash tests/run-mobile-ui.sh BOOTED_SIMULATOR_UUID` requires exactly one
already-booted Simulator and installs an isolated test app. Passing these checks
does not prove game completion, smooth presentation, audio, or device readiness.

## Project map

| Path | Purpose |
| --- | --- |
| `apple/ios/` | Native mobile host, Metal view, active `GalaxyPadGameOverlay.mm` and menu adapters |
| `apple/shared/` | Input, settings, diagnostics and shared integration |
| `config/` | Exact disc identity and pinned dependencies |
| `patches/` | Reviewed integration patches and isolated experiments |
| `scripts/`, `tests/` | Build, audit and regression tools |
| `docs/` | PRD, goal loop, evidence and handoffs |
| `ref/`, `generated/` | Ignored local dependencies/data and build/runtime artifacts |

## Credits, legal and contributing

GalaxyPad builds on SunPad, ModernGekko, RecompCore/Dolphin, DolRecomp and WIT;
Petari is a source reference. Exact upstream URLs and revisions are recorded in
the [dependency lock](config/dependencies.lock.json). Preserve upstream notices
and license obligations when adapting code. Nintendo's game and trademarks belong
to their respective owners; this project is not affiliated with Nintendo.

Contributions should be small, testable and consistent with the original PRD.
Record visible results and known failures, not just counters or successful builds.
Do not include retail content, generated game code, modules, saves or protected
screenshots. This README is not a distribution license; consult
[RIGHTS-STATUS](docs/RIGHTS-STATUS.md) before any publication.
