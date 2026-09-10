# Mobile implementation — active 2026-09-08

## R500 user correction — use the actual SunPad UI systems

Chris explicitly reiterated that GalaxyPad must use SunPad's three-dot menu and
touch controls. The custom UITableViewController menu and incremental substitute
overlay are NOT the requested product UI, even where their tests pass. Stop
extending those substitutes. Adapt the actual pinned SunPadGameOverlay (native
UIMenu, raw touch buttons/sticks, grouped D-pad, settings/editor bar, per-control
selection/size/reset, controller visibility), its shared settings and diagnostic
interfaces into Galaxy-owned files, preserving appearance, interaction and
provenance. Change only game-specific mappings/features to the Galaxy PRD.

Preserve the tested Wii runtime host, input mixer/virtual device, viewport mapping,
clear/pause/shutdown safeguards and private data boundary. Wire the reference UI
to those interfaces; do not carry GameCube/FLUDD/Sunshine timing or aspect hacks.
Full required actions must work; prototype accessibility/editor tests do not
establish SunPad UI parity. Next: read the complete reference overlay/settings
implementation and perform the direct port, then compare visible behavior.

Chris authorized beginning mobile development while macOS timing/audio acceptance
remains open. This changes scheduling, not the original PRD or gate evidence.
Installed macOS runner671729c6/module1fb635f7 remains the behavioral reference.

## Reference and build boundary

- Read-only SunPad checkout fcdc1411e483a86ca80ec82e7cd53839c51ff865 (GPL-3.0).
  Reviewed iOS core build/toolchain, host interface, app lifecycle, input state
  and mixer; README, handoff and known-issue/testing/performance context consulted.
- GalaxyPad owns its adaptations. Keep license/provenance; no copied Sunshine
  game identity, GameCube/FLUDD mappings, 30Hz patches or GameCube-only extraction.
- scripts/build-ios-simulator-core.sh configures the existing patched/pinned
  runtime in generated/build/ios-simulator-core. It does not bootstrap, mutate
  dependency overlays, provision game data or touch the macOS build directory.
- Simulator toolchain targets arm64/iOS16; configured minimum OS is not tested
  compatibility. Check actual binary platform and runtime code-generation policy.

## Delivery sequence

R493: first native three-dot menu has touch visibility/opacity settings and
confirmed Stop. Touch off/on, Done, system dismissal and Stop cancellation were
interacted with; opacity change remains unproven. Paused-menu Stop exposed STM
power-button starvation: resume-before-shutdown now passes visible Game stopped.
Dealloc has same guard, compile-only so far. Full required menu hierarchy,
editable/advanced controls and mobile acceptance are still unfinished.

R491 current boundary: Simulator core/module/app link and render title; native
Stop completes. Touch A/B samples and Classic Pointer visibility reach emulated
Wii input. Viewport geometry is captured on the renderer thread and read by the
overlay; touches retain Classic aim without synthesizing A/B. No file-select,
simultaneous-button, pointer-target/depth or mobile gameplay/performance pass yet.
Basic stick/seven-button overlay is not the full editor/menu/controller product.
Native host uses C++23 to match pinned renderer headers. macOS remains separate.

R475: Simulator core build completed; matching AOT module is compiling in
generated/build/ios-simulator-module through build-ios-simulator-module.sh.
Reuses accepted generated code and PGO without replacing the macOS module.
Native executable, touch UI and mobile runtime acceptance are not yet delivered.

R474: GalaxyPadInput.h adapts SunPad's locked two-source mixer and rising-edge
latching into logical Wii/Nunchuk actions. Adds dedicated Spin, viewport pointer
ownership, normalized movement/tilt and clear-all. No raw GC report bits/FLUDD
triggers. ASan/UBSan behavioral tests pass and arm64 iOS16 Simulator syntax
check passes. Not wired to an overlay/runtime yet; no touch gameplay claim.
Runtime source already disables fallback JIT on iOS and selects software vertex
loading; final app/runtime execution still requires verification.

R651: byte-cache default candidate6f41c070 installed on sole iPad Simulator;
full regression suite passes. Launch without byte override is in progress; actual
default-path activation pending. Updated private physical stage d5VpYL includes
app936265bd and module48f455eb; unsigned/uninstalled, no hardware claim.

R645: physical module38249 exit0; private staging helper succeeds at
generated/device-stage.qAV3Pi/GalaxyPad.app. App and module IOS/arm64/min16;
module SHA48f455ebc33f8eb2fc58151cd722ea756db77a5738a9573a0a49f0c656110041.
Unsigned, uninstalled and not device-runtime accepted. Source no-JIT policy
checked; execution evidence remains mandatory. Suite3418 running; see STATUS.

R644: physical startup now loads the bundled Frameworks AOT module and imported
private GameData. Simulator development paths remain compile-time isolated.
Device app links successfully; both platform main objects compile. Import still
requires relaunch. Private staging helper is syntax-checked but not yet executed
while device module38249 links. No signed package, device launch or speed claim.

R643 completion update: physicalruntime and app shell compile/link successfully.
Runtimeobject and executable identify IOS/minimum16.0/sdk26.5; provisionedcore
archiveARM64. DeviceAOTmodule stillbuilding38249; signing/modulepackaging/device
execution unverified. Source/appbuild output is not a device-playability claim.

R643: SDK selection now covers core/module/app/provisioning entry points.
GALAXYPAD_IOS_SDK=iphoneos selects independent ios-device build directories;
default remains iphonesimulator. App CMake selects matching archive/header paths
from its SDK. Device and Simulator configurations checked independently; unsupported
SDK values rejected before work. Physical CoreHost object compiled successfully
and vtool identifies IOS, minimum16.0, SDK26.5. Core build85533 still in progress;
archive provisioning/module/app linking and signed device launch remain unproven.

R642: preparing a distinct physical-device performance lane. Existing runtime
builder accepts GALAXYPAD_IOS_SDK=iphoneos and selects ios-device-toolchain.cmake
with generated/build/ios-device-core; default remains Simulator. Core build85533
in progress, not yet provisioned or linked into a device app. App CMake, module
and archive provisioning still require explicit device paths/platform audits.
No connected device or device-performance claim. See STATUS for current handle.

1. Build Simulator runtime and matching RMGE01 AOT module; audit identities,
   Wii/MEM2, fallback policy, Metal/software vertex loading and module provisioning.
2. Adapt SunPad native host, lifecycle and error reporting. Wire Galaxy normalized
   Wii/Nunchuk input, dedicated Spin, pointer and non-motion tilt, not GC mappings.
3. Bring up one iPad Simulator with usable touch controls and three-dot menu.
   Retain layout editing, safe areas, controller handoff, clear-on-interruption,
   persistence and diagnostics. Complete PRD9.5 menu actions, not inert placeholders.
4. Verify actual first-play/save/reload, input, pointer-depth and lifecycle.
   Record FPS/frame-time/audio separately from UI success and macOS evidence.
5. Shut down iPad Simulator, then adapt/test compact iPhone layout and interactions.
6. Physical iPad/iPhone testing establishes actual performance/thermal/audio/touch
   behavior. Simulator performance neither promises nor disproves device speed.

Full story/mechanics, macOS and mobile stability, soak, reproducibility, rights
and explicit release acceptance remain mandatory. No public artifacts authorized.
