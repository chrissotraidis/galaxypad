# GalaxyPad PRD: Super Mario Galaxy, native on Apple platforms

Status: approved for **gated autonomous execution**. Written 4 Sep 2026.

Audience: an autonomous agentic system with full control of an Apple Silicon macOS machine.

Companion document: `docs/GOAL-LOOP.md` (the operating loop). Read both documents before changing source, installing dependencies, extracting the disc, or launching a target.

Decision: **GO for a private technical porting program. NO-GO for a public source or binary release until the technical, physical-device, package-safety, provenance, and rights gates in this document are all satisfied.**

---

## 1. Objective

Build **GalaxyPad** (`galaxypad`, working project and repository name): a native ARM64 application for **macOS, iPadOS, and iOS** that runs a supported retail revision of **Super Mario Galaxy for Wii** from game data supplied locally by the user.

The intended execution stack is:

```text
User-owned supported Super Mario Galaxy Wii disc image
        │
        ├── exact identity, partition, and main.dol verification
        │
        ▼
DolRecomp ahead-of-time PowerPC translation
        │
        ▼
Locally generated ARM64 game module
        │
        ▼
ModernGekko + Dolphin-derived Wii compatibility services
        │
        ├── Wii boot / IOS / ES / NAND / SYSCONF
        ├── MEM1 / MEM2 / DSP / GX / EFB
        ├── WPAD / KPAD / Nunchuk / saves
        └── Metal renderer and Apple platform integration
        │
        ├── GalaxyPad.app for Apple Silicon Mac
        └── universal GalaxyPad app for iPad and iPhone
```

**DolRecomp** is the CPU translation path. **ModernGekko and its Dolphin-derived runtime** provide the Wii hardware and operating environment. **SunPad** is the reference Apple implementation and lives at `ref/sunpad`; use its game-neutral Apple shell, Metal surface integration, touch-layout editor, input mixer, controller ownership, three-dot menu, disc import, settings, diagnostics, lifecycle handling, build scripts, dependency discipline, package audits, and evidence practices. Treat `ref/sunpad` as read-only.

The **Petari** Super Mario Galaxy decompilation is a pinned source map and behavioral reference, not the executable product path. It may supply names, control-flow understanding, subsystem inventories, and function-level patch targets. Its exact symbols and addresses apply only when its supported `RMGK01` Rev 0 `main.dol` matches the user-supplied DOL. For any other region or revision, the extracted retail DOL is authoritative and Petari is semantic guidance only.

GalaxyPad is **not** a general Wii emulator frontend. It is a game-specific Apple integration around a locally generated static-recompilation module and a bounded compatibility runtime. Do not describe it as “emulator-free”: the runtime is Dolphin-derived, and bounded fallback execution may exist during development.

The user has authorized the agent to install required developer tools and download public source code and public tool data. That authorization does **not** extend to downloading Nintendo disc images, extracted assets, saves, keys from untrusted sources, leaked SDK material, or another commercial game as a test fixture. The supplied Galaxy image in `ref/` is the only assumed copyrighted game input.

### Delivery order

1. **Reproducible state and rights boundary.** Record the root state, inspect the supplied image without modifying it, pin every source/tool input, make game-data safety checks executable, and set the initial release state to `private-only`.
2. **Exact Wii input identity.** Identify the disc format, six-character title ID, region, disc/revision fields, partition layout, image hashes, extracted `main.dol` hashes, and all executable files. Do not assume a U.S. revision or copy Petari’s Korean hash onto another image.
3. **Wii toolchain gate.** Prove that DolRecomp is operating in Broadway/Wii mode with 64 MiB MEM2, that the title database/setup state cannot silently force GameCube mode, and that extraction and module generation are deterministic.
4. **macOS native core.** Generate the ARM64 module, boot the Wii runtime on Apple Silicon, create a Metal surface, and instrument AOT coverage, fallback execution, Wii services, EFB reads, input, audio, saves, and memory before attempting broad gameplay.
5. **macOS first-play loop.** Title/file select → new file → Star Festival/opening → Gateway Galaxy → movement, jump, pointer, and spin → first Grand Star → Comet Observatory → save → clean exit → relaunch and load.
6. **Complete macOS game path.** Story progression through the final Bowser encounter and credits, followed by late-game and completion-content coverage sufficient to prove that every required control and subsystem works.
7. **Correctness and performance.** Preserve the title’s measured 60 Hz behavior, native rendering semantics, EFB/Z-readback-dependent pointer behavior, Wii/Nunchuk controls, DSP audio, routed Wii Remote speaker cues, NAND saves, and MEM1/MEM2 behavior. Measure; do not infer.
8. **iPadOS Simulator.** Port the same AOT core and Apple shell to one iPad Simulator, with no runtime PowerPC JIT, and complete the first-play loop.
9. **iOS Simulator.** Shut down the iPad Simulator, boot one iPhone Simulator, and complete the first-play loop with the same AOT core and product control model.
10. **SunPad-derived product shell.** Finish the direct-touch pointer, editable controls, three-dot menu, game-data management, controller mapping, lifecycle, diagnostics, privacy, and original GalaxyPad icon set.
11. **Physical-device and release gates.** Build exact candidates for physical iPad and iPhone, obtain Chris’s hands-on evidence, audit source and packages, resolve license/rights decisions, and publish nothing until the exact artifact is explicitly approved.

Three requirements are hard, not aspirational:

- **The first-play loop must work end to end.** A generated module, successful compile, process ID, title screen, pointer visible in one menu, or Gateway Galaxy that cannot save and reload is not a playable port.
- **Required Wii interactions must have a non-motion Apple control path.** A user must be able to complete the game on touch and on a conventional Apple-compatible controller without shaking an iPad or depending on controller gyro hardware.
- **A public release requires exact-artifact testing and explicit rights clearance.** “User supplies the ISO,” “the package is ROM-free,” or “the decomp is public” does not independently authorize distribution.

---

## 2. What “done” means

All of the following, each backed by evidence from Section 11:

- **D1. Exact disc identity and extraction.** The original input in `ref/rom/` remains byte-identical. GalaxyPad records its container format, size, SHA-1, SHA-256, six-character title ID, region, disc number, revision, partition map, `main.dol` SHA-1/SHA-256, extracted filesystem manifest, and any additional executable modules. The supported baseline is the exact verified image, not a guessed regional hash.
- **D2. Reproducible Wii AOT pipeline.** The pinned toolchain extracts the image and generates an ARM64 module from `main.dol` reproducibly. The build proves Broadway/Wii mode, a 64 MiB MEM2 model, correct MEM1/MEM2 address translation, and the intended backend. DolRecomp’s SMC report and every warning are interpreted; no silent GameCube-mode downgrade, unreviewed executable file, or unexplained code range remains.
- **D3. macOS first-play loop.** The packaged Apple Silicon macOS app reaches the title and pointer-driven file-select UI, creates a new file, completes the opening and Gateway Galaxy, obtains the first Grand Star, reaches the Comet Observatory, writes progress, exits cleanly, relaunches, and restores the file with video, input, pointer, music, sound effects, and stable timing.
- **D4. Complete macOS story path.** A fresh GalaxyPad-created save progresses through every required observatory dome and story gate, completes the final Bowser encounter and credits, returns to the post-game state, and has no progression, save, input, rendering, audio, or memory blocker.
- **D5. Completion-content and mechanic coverage.** Every galaxy/mission class needed for a completion claim is reachable; comet and Hungry Luma paths, Green/Trial content, transformations, bosses, water/flying sections, cannon/sling/bubble pointer interactions, ball-rolling and ray-surfing tilt sections, Luigi/post-game content, and the final completion sequence are exercised with documented saves and routes. A story-complete preview may exist while D5 is open, but it must not be called fully complete.
- **D6. Timing, rendering, and EFB correctness.** The supported revision’s reference cadence is measured. GalaxyPad sustains correct 60 Hz gameplay behavior where the original does, preserves cutscene and audio timing, renders the title’s native 640×456 NTSC/EURGB60 EFB path correctly at 1×, and maintains correct GX/EFB semantics. Star Pointer depth reads, target selection, Pull Stars, Star Bit collection/shooting, reticles, reflections, shadows, post-processing, mip behavior, and scene transitions remain correct. Performance claims include frame-time and EFB-stall measurements.
- **D7. Complete Apple control model.** Touch and conventional controllers provide Nunchuk movement, A/B, C/Z, Plus/pause, required D-pad/other buttons, a dedicated Spin action, absolute pointer positioning, pointer click/shoot behavior, and non-motion alternatives for all mandatory tilt and shake mechanics. No required route depends on device gyro. Optional controller motion is capability-detected, default-off until accepted, and never replaces the non-motion path.
- **D8. Audio, speaker, saves, and Wii services.** Main DSP audio has correct pitch and continuity; Wii Remote speaker cues are deliberately routed into the host mix or explicitly rejected by Chris after comparison; rumble/haptics fail safely; Wii NAND save creation, multiple files, star writes, copy/erase behavior, termination, relaunch, backup/recovery, and corruption tests pass. IOS/ES/SYSCONF and disc-partition behavior are stable and reproducible.
- **D9. Simulator core.** One iPadOS Simulator, then one iOS Simulator, each boots through the first-play loop with the same AOT game identity. No runtime PowerPC JIT, writable-executable guest code, downloaded executable module, or dynamic code generation is used on iPadOS/iOS. Simulator results are diagnostic evidence, not physical-device acceptance.
- **D10. GalaxyPad Apple shell.** SunPad’s game-neutral Metal host, touch-layout editor, input mixer, controller handoff, three-dot menu, staged game-data import, settings persistence, lifecycle behavior, diagnostics, privacy filtering, and audit machinery work as GalaxyPad. The app includes original, provenance-documented macOS/iOS/iPadOS icons that use no Nintendo art, logos, screenshots, or extracted assets.
- **D11. Stability and reproducibility.** Background/foreground, interruptions, renderer recreation, controller connect/disconnect, pointer activation/deactivation, native-menu presentation, repeated galaxy/observatory transitions, saves, 60-minute soak, and memory-pressure tests complete without stuck input, missing pointer, save corruption, sustained audio underrun, runaway EFB stalls, unbounded memory growth, or orphan processes. The applicable technical matrix reproduces from a clean checkout using scripts and pinned public dependencies.
- **D12. Public candidate.** The exact source revision and exact macOS/app/IPA artifacts pass physical iPad and iPhone hands-on testing, source/package audits, license/notices review, and the rights gate in Section 12. A candidate is not public until Chris explicitly approves that exact artifact.

### Explicit non-goals for the baseline

- Super Mario Galaxy 2. Its engine overlap may make it a later project, but it requires a separate disc/executable/module/REL/rights/control audit.
- A general Wii game browser, general Dolphin frontend, multi-title launcher, or arbitrary DOL loader.
- App Store submission, TestFlight, notarization, commercial signing, automatic updates, or store-review work.
- Network play, netplay, downloadable mods, runtime code mods, texture packs, cheats, randomizers, save editors, or online services.
- Runtime PowerPC JIT on iPadOS or iOS.
- Downloading or bundling a Wii image, extracted Nintendo files, external NAND dump, copyrighted system files, another commercial title, or a generated game module from an unverified third party.
- Enhanced frame-rate patches, arbitrary ultrawide projection, texture replacement, free camera, or gameplay changes before D1–D11. Galaxy already targets 60 Hz; do not create a “120 fps” track before baseline correctness.
- Making two-player Co-Star mode a blocker for the initial single-player product. P2 may be added after the P1 technical matrix, but its absence must be documented.
- Treating optional device gyro, controller gyro, HD rumble, or a separate physical speaker as required hardware. The baseline must remain playable without them.

---

## 3. Why this is feasible — and what remains unproven

### 3.1 Evidence supporting a GO decision

The following was validated by source and repository review on 4 Sep 2026. It is research evidence, not execution evidence for GalaxyPad:

- **The CPU toolchain explicitly supports Wii DOLs.** DolRecomp accepts a Wii `main.dol` plus six-character title ID, selects the Broadway profile, models 64 MiB of MEM2, and can emit portable C or LLVM-native objects.
- **A Wii title has crossed this upstream stack.** ModernGekko’s `kirby` release contains Windows and Linux x86_64 builds of a Kirby Wii recompilation. This proves that Wii DOL → DolRecomp → ModernGekko is not merely a planned architecture. It does not prove macOS, ARM64, Galaxy, or mobile.
- **Galaxy has an unusually favorable executable shape.** Petari’s supported build centers on one `sys/main.dol`, and the current source audit found no normal game REL overlay set. The agent must verify the supplied image independently, but the known target avoids the REL-heavy shape that complicates other Wii games.
- **Galaxy’s baseline rendering cadence is explicit.** Petari’s frame controller selects one update per retrace, and its render-mode definitions use a 640×456 EFB for NTSC/progressive/EURGB60 paths. The game also has native 4:3 and 16:9 modes; no generic widescreen hack is needed for baseline 16:9.
- **The main special rendering requirement is known.** Dolphin’s title settings for the `RMG` family enable CPU EFB access and deferred invalidation. Petari’s Star Pointer code performs `GXPeekZ` from a draw-sync callback at the pointer position. This makes the primary correctness/performance risk observable and measurable rather than mysterious.
- **The dynamic HOME-menu code is bounded.** The retail game loads a separate Home Button Menu RSO and exposes seven named entry points. GalaxyPad can replace the console HOME UI with its native three-dot menu through a narrow adapter rather than executing downloaded/generated PowerPC jump code on mobile.
- **The required controls have tractable non-motion routes.** ModernGekko’s touch override already exposes Wii buttons, IR X/Y, Nunchuk C/Z, and Nunchuk stick. Galaxy’s player code distinguishes swing from button triggers, and its source includes stick-based movement logic beneath accelerometer-driven sphere control. The runtime still needs a Galaxy-specific Spin/shake channel and a complete motion-consumer audit.
- **SunPad already solves the Apple half.** SunPad provides a proven Apple Silicon/macOS and iPhone/iPad architecture around DolRecomp/ModernGekko, including a CAMetalLayer host, no-JIT mobile configuration, on-device disc import, editable touch UI, controller handling, settings, diagnostics, lifecycle work, dependency pins, safety scripts, and package audits.

### 3.2 What this review did not prove

All of the following remain execution gates:

- The identity, region, revision, condition, and extractability of the actual ISO that will be present in `ref/`.
- That the exact supplied image has no REL or other executable modules beyond `main.dol` and the known HOME-menu RSO.
- That the SunPad-pinned ModernGekko/DolRecomp graph boots a Wii title on Apple Silicon without a deliberate upstream update.
- That Wii IOS/ES/NAND/SYSCONF, encrypted partition mounting, DSP, MEM2, WPAD/KPAD, and saves all work through this Apple harness.
- That the generated Galaxy module compiles, links, loads, and reaches the entry point on macOS.
- That all required executed code is AOT-covered or has a bounded, mobile-compatible fallback.
- That DolRecomp’s SMC scan is clean for the exact DOL. Its own documentation says self-modifying code is not automatically handled.
- That stubbing/replacing the Home Button Menu preserves pause, resume, fade, and shutdown semantics.
- The measured cost of Star Pointer EFB/Z reads on any Apple GPU. Apple GPUs use a tile-based architecture, so CPU/GPU synchronization must be profiled instead of hand-waved.
- That direct touch can collapse pointer positioning and context-sensitive A/B actions without false input in file select, menus, Star Bit shooting, Pull Stars, cannons, sling pods, and bubbles.
- That every motion/tilt consumer has a correct stick-backed or button-backed alternative.
- That the Wii Remote speaker stream can be mixed into Apple audio with correct ordering, pitch, latency, and volume.
- That iPhone-class hardware can sustain the title’s 60 Hz workload and EFB behavior at a usable thermal state.
- That a public source or binary release is legally and license-compliant.

### 3.3 Conclusion

Proceed. GalaxyPad is a credible and strategically strong private port target because the Wii recompilation substrate exists, Galaxy’s known executable layout is favorable, the principal graphics risk is identifiable, and SunPad supplies the Apple product shell.

Do **not** call it easy. The work is materially harder than copying SunPad: Galaxy introduces Wii boot services, MEM2, Nunchuk/IR input, pointer-dependent EFB readback, a dynamic HOME-menu subsystem, Wii Remote speaker audio, and mandatory tilt/shake mechanics that need product-quality non-motion alternatives.

This feasibility review was source-level. No Galaxy image was available in the research environment, so no extraction, module generation, Apple build, launch, gameplay, frame-time measurement, save test, or package audit was executed. The agent must not convert this GO decision into a completion claim.

---

## 4. Environment and workspace

The agent has control of an Apple Silicon Mac and may install missing public tools. Verify and record, at minimum:

- Xcode 26.x and command-line tools;
- working macOS, iPadOS Simulator, and iOS Simulator SDKs;
- AppleClang with C11 and C++23 support;
- CMake, Ninja, `pkg-config`, Git, Python 3, `jq`, `ripgrep`, and `sha1sum`/`shasum` equivalents;
- LLVM 19 or 20 only if the LLVM backend is deliberately selected;
- Wiimms ISO Tools (`wit`) or a source-audited equivalent for Wii extraction;
- Instruments, `xcrun simctl`, `xcrun devicectl`, `codesign`, `vtool`, and `otool`;
- sufficient free disk space for the original image, staged extraction, generated code/objects, app products, and evidence.

Every downloaded tool must have its source URL, version/revision, checksum where available, license, and purpose recorded. Prefer source builds and official upstream releases. Never let a setup script fetch game data.

Recommended repository layout:

```text
docs/
  PRD.md
  GOAL-LOOP.md
  JOURNAL.md
  STATUS.md
  RIGHTS-STATUS.md
  DISC-IDENTITY.md
  DEPENDENCIES.md
  UPSTREAM-DELTA.md
  EXECUTABLE-COVERAGE.md
  WII-SUBSYSTEMS.md
  INPUT-AND-POINTER.md
  MOTION-AUDIT.md
  EFB-READBACK.md
  AUDIO.md
  SAVE-AND-NAND.md
  PERF.md
  RELEASE-READINESS.md
  artifacts/                    local and gitignored by default
ref/                            entirely gitignored
  sunpad/                       pinned read-only reference clone
  petari/                       pinned source/semantic reference
  ModernGekko/                  pinned prepared runtime checkout
  ModernGekko-Template/         pinned pipeline reference
  rom/
    original/                   user-supplied image; never modified
  controls/                     optional lawful homebrew/control DOLs only
config/
  galaxypad-disc.json           generated identity allowlist for one revision
  galaxypad-runtime.ini         stable runtime configuration
  galaxypad-controls.ini        Wii Remote + Nunchuk baseline mapping
  galaxypad-symbols.map         exact-region symbols when verified
  galaxypad-patches.json        ordered patch/replacement manifest
generated/                      entirely gitignored
  staged-disc/
  extracted/
  aot/
  module/
  build/
port/
  apple/
    shared/
    ios/
    macos/
  runtime/
  patches/
scripts/
tests/
GalaxyPad.xcodeproj
```

### Hard workspace rules

- Never modify, rename, truncate, move, or delete the user’s original image. Work from ignored copies or read-only mounts.
- Treat `ref/sunpad`, `ref/petari`, and every upstream checkout as read-only inputs. Apply GalaxyPad changes through pinned patches or owned integration code.
- Pin every checkout and recursive submodule. Disable push URLs for reference checkouts.
- Never commit or upload a disc image, partition dump, extracted Nintendo file, `main.dol`, generated AOT C/object/module, save/NAND content, screenshot or audio capture containing protected game content, crash memory, private log, key material, provisioning profile, signing identity, or absolute private path.
- Keep `docs/artifacts/` local/ignored until an explicit release review selects safe evidence.
- Never run `git clean -fdx`, destructive resets, blanket `rm -rf` against the root, or a command that can erase ignored inputs/evidence. Inspect exact paths first.
- Do not overwrite unknown local work. Preserve or isolate modifications you did not create.
- Do not push any branch, tag, release, package, screenshot, generated module, or public issue without Chris’s explicit authorization.
- Do not run more than one Simulator or more than one GalaxyPad/game process at a time.

---

## 5. Inputs, references, and starting pins

### 5.1 The user-supplied Galaxy image

The initial baseline is the **single exact Super Mario Galaxy image supplied in `ref/`**. Do not assume it is U.S. Rev 0. Search only within the designated ignored input folder and stop on ambiguity if multiple candidate images exist.

Before extraction:

1. Record source filename, format, byte length, filesystem permissions, SHA-1, and SHA-256.
2. Read the Wii disc header without altering the image.
3. Require a recognized Super Mario Galaxy title ID from the `RMG?01` family and record the exact value. Known retail IDs include `RMGE01`, `RMGJ01`, `RMGP01`, and `RMGK01`; the actual image decides.
4. Record region, disc number, revision, Wii magic, partition table, data-partition identity, and any update partition separately.
5. Extract to a unique ignored staging directory using a pinned tool.
6. Record `sys/main.dol` SHA-1 and SHA-256, all executable-looking files (`.dol`, `.rel`, `.rso`, executable blobs found by the disc manifest), and a deterministic filesystem manifest.
7. Verify extraction by repeating the manifest/hash operation from a clean staging directory or by an equivalent deterministic check.
8. Create `config/galaxypad-disc.json` containing only identity metadata and expected hashes, never game bytes.

If the title ID is not a supported Super Mario Galaxy retail image, extraction fails, the image is corrupt, or multiple images conflict, leave G1 unmet and write a precise handoff. Do not patch the header or accept “close enough.”

Petari’s pinned `RMGK01` config records `main.dol` SHA-1 `25c5959534b3c21246c6c7e42021b916b41fb578`. Use its address map as exact only if the supplied DOL matches that value. Otherwise build a revision-specific map and validate every imported symbol against section boundaries and known bytes.

### 5.2 The Apple reference: `ref/sunpad`

Pin SunPad to the reviewed revision first:

```text
chrissotraidis/sunpad
efd42ca45457af5950e0558c66703cb766959e11
```

Before writing GalaxyPad product code, read in order:

1. `README.md` — supported targets, current execution model, touch/menu behavior, game-data boundary, and release wording.
2. `docs/ARCHITECTURE.md` — AOT module/runtime boundary, Apple host layering, no-JIT mobile path, and separation rules.
3. `docs/BUILDING.md` and `docs/DEPENDENCIES.md` — exact source graph, patches, build tools, clean-clone behavior, module generation, and device provisioning.
4. `docs/IOS_IPADOS.md` and `docs/MACOS.md` — CAMetalLayer host, import/extraction, input mixer, lifecycle, diagnostics, and platform-specific paths.
5. `docs/TESTING.md`, `docs/STATUS.md`, `docs/KNOWN_ISSUES.md`, `docs/TECH-DEBT.md`, and `docs/HANDOFF.md` — actual evidence, solved failures, unsafe assumptions, and remaining boundaries.
6. `docs/LEGAL_AND_PROVENANCE.md`, `THIRD_PARTY_NOTICES.md`, and package/install documentation — source/package boundary and exact-artifact discipline.
7. `scripts/` — especially dependency bootstrap, game preparation, iOS core builds, device deployment, macOS packaging, repository checks, package audits, diagnostics, and input test helpers.
8. `patches/` — understand every ModernGekko/RecompCore/Metal/no-JIT/audio/lifecycle change before porting it.
9. `apple/shared/`, `apple/ios/`, `apple/macos/`, and `tests/` — settings, normalized input, UIKit/AppKit host, overlay, controller slots, import, diagnostics, and regression style.

Copy mechanisms and tests only through GalaxyPad-owned source with provenance. Do not rename SunPad wholesale and silently retain Sunshine assumptions.

### 5.3 Galaxy source reference: `ref/petari`

Pin the reviewed Petari revision:

```text
SMGCommunity/Petari
845164b4faec4703002eb99b4b75ee1788204230
```

Read at minimum:

| Path | What it establishes |
|---|---|
| `README.md` | Supported `RMGK01` Rev 0 boundary; decomp is not itself a PC/native port |
| `config/RMGK01/config.yml` | Exact Korean `main.dol` hash and object identity |
| `config/RMGK01/symbols.txt`, `splits.txt` | Named functions, section ranges, and source mapping for the matching DOL |
| `src/Game/System/GameSystemFrameControl.cpp` | 60 Hz movement/update intent |
| `src/Game/System/RenderMode.cpp` | 640×456 NTSC/EURGB60 EFB and native 4:3/16:9 modes |
| `src/Game/System/HeapMemoryWatcher.cpp` | Paired MEM1/MEM2 heaps, large early MEM2 allocations, and OOM behavior |
| `src/Game/System/HomeButtonMenuWrapper.cpp` | Dynamic RSO loading and seven HOME-menu entry points |
| `src/Game/Screen/StarPointerDirector.cpp` | Draw-sync pointer update and `GXPeekZ` depth reads |
| `src/Game/Player/MarioActorPad.cpp`, `MarioActor.cpp` | Swing/button action selection and player input behavior |
| `src/Game/Ride/SpherePadController.cpp` | Stick-driven sphere movement path |
| `src/Game/Ride/SphereAccelSensorController.cpp` | Accelerometer-driven sphere path and button braking/jump behavior |
| `src/Game/Speaker/SpkSpeakerCtrl.cpp` | Wii Remote speaker state, periodic stream, encoding, and timing |
| Wii SDK wrappers under `src/RVL_SDK/` | WPAD/KPAD, GX, IOS/OS behavior as represented by the matching code |

Do not submit AI-generated decompilation work to Petari. GalaxyPad consumes Petari as a read-only research input.

### 5.4 Core toolchain and coherent pin tracks

Start from SunPad’s **known Apple track**, because it has executed on Apple targets:

| Component | Starting revision from SunPad | Role |
|---|---|---|
| SunPad | `efd42ca45457af5950e0558c66703cb766959e11` | Apple product/reference implementation |
| ModernGekko | `0514d9f03f8602809f66fc92fdca87d30e752997` | Runtime and launcher |
| ModernGekko vendor RecompCore/Dolphin | `13e492094902644b0d113c586300d358640f9e19` | Dolphin-derived execution/render/audio/input substrate |
| ModernGekko-Template | `1ee85bb5e09c38f493a09f5fa6e9dc8228b23e42` | Extract/recompile/module/run pipeline reference |
| DolRecomp | `fa0cf619e8d7eb8cba7eaf55267a12caaebb46aa` | DOL-to-C/LLVM translator within the reviewed Apple graph |

Also record the source-reviewed newer upstream track as of 4 Sep 2026:

| Component | Reviewed newer revision | Reason to evaluate, not auto-adopt |
|---|---|---|
| ModernGekko | `5417826c31187d4dadf8588c7aa25bf107782936` | Newer Wii/runtime work |
| ModernGekko vendor RecompCore/Dolphin | `55c7b023fa0f4eba1cf3fdbbb25b1c5ec468d5ac` | Coherent vendor pointer for the newer runtime |
| ModernGekko-Template | `eedda2b02dde3aefc02796d859f0033b916aad03` | Current generic Wii/GameCube pipeline |
| DolRecomp | `1bec3554ecc4817cf78319ca3d8a0669477f29fa` | Newer LLVM/native ABI and Wii pipeline state |

Create `docs/DEPENDENCIES.md`, a machine-readable dependency lock, and `docs/UPSTREAM-DELTA.md`.

Rules:

- Reproduce the SunPad Apple track first or establish exactly why it cannot perform the Wii gate.
- Run an explicit capability probe for Wii title-ID handling, Broadway selection, MEM2, Wii input override, extraction, and module ABI.
- If a newer upstream is required, update **ModernGekko, its vendor tree, DolRecomp, and applicable patches as one reviewed graph**. Do not mix commits opportunistically.
- Rebase SunPad patches one at a time, record conflicts and behavior, and rerun the full applicable matrix after any pin change.
- Do not choose the LLVM backend merely because it is newer. Establish a working C-backend baseline first unless the pinned pipeline demonstrably requires LLVM.

### 5.5 Primary external references

The agent may research a named blocker in these primary sources:

- `https://github.com/ExpansionPak/DolRecomp`
- `https://github.com/ExpansionPak/ModernGekko`
- `https://github.com/ExpansionPak/ModernGekko-Template`
- `https://github.com/ExpansionPak/RecompCore`
- `https://github.com/SMGCommunity/Petari`
- `https://github.com/dolphin-emu/dolphin`
- official Apple Metal, GameController, CoreMotion, Instruments, and Xcode documentation

Use issues, source history, and release artifacts only to answer a specific blocker. Return from research to a controlled experiment.

---

## 6. Phase 0 gate: reproducibility, safety, and rights state

Technical work may proceed privately after this phase. No public work may proceed merely because the build launches.

1. Create `docs/RIGHTS-STATUS.md` with the state: **private technical work authorized by Chris; public source and binary redistribution not approved**.
2. Record the licenses and exact revisions of SunPad, ModernGekko, the Dolphin/RecompCore vendor tree, DolRecomp, ModernGekko-Template, Petari, `wit`, and every added dependency.
3. Record that copying/adapting GPL-covered SunPad/ModernGekko/Dolphin code creates source and notice obligations for any distribution. Do not treat “separate repository” as an escape from those obligations.
4. Choose a tentative, non-public release topology:
   - a separate GalaxyPad integration repository containing original Apple integration, permitted patches, build scripts, and documentation;
   - private-only source until upstream/rightsholder/license questions are resolved; or
   - another topology explicitly reviewed before publication.
5. Port and strengthen SunPad’s repository safety checks before generated data exists. Reject disc images, Wii partitions, `main.dol`, extracted files, generated AOT/module outputs, saves/NAND, screenshots, audio captures, crash dumps, logs with game memory, credentials, signing material, and `ref/` content.
6. Record `git status`, root revision, host/tool versions, free disk space, active processes, and booted Simulators.
7. Pin `ref/sunpad`, the selected coherent toolchain graph, and `ref/petari`; disable push URLs and refuse dirty/unknown source trees.
8. Inventory the supplied disc according to Section 5.1 and write `docs/DISC-IDENTITY.md`.
9. Create a clean-clone/bootstrap script that downloads only public source/tools and never looks outside the designated game-data path.

G0/G1 may be complete while `RIGHTS-STATUS.md` remains `private-only`. That state blocks publication, not private technical execution.

---

## 7. Phase 1 gates: Wii substrate, AOT coverage, pointer, controls, audio, and saves

### 7.1 Wii setup and the Broadway/MEM2 guard

DolRecomp’s current Wii CLI depends on setup/title data. Its source-reviewed behavior can fall back to GameCube/titleless mode when the titles database is absent, which selects the Gekko profile and zero MEM2. Galaxy would then fail in ways that resemble a game bug.

Required process:

1. Build the pinned DolRecomp from source.
2. Run its setup path in a controlled location and record the title database and `wit` identity.
3. Add `scripts/verify-wii-mode.sh` that fails unless all of the following are observed for the supplied title:
   - exact six-character Wii title ID passed through;
   - effective CPU is Broadway/Wii, not Gekko/GameCube;
   - MEM2 is enabled at the expected Wii address range with 64 MiB capacity;
   - extracted title identity matches `config/galaxypad-disc.json`;
   - generated module metadata carries the same DOL hash/title identity.
4. Make every build entry point call this guard. A warning in a log is insufficient.
5. Instrument MEM1/MEM2 creation and the early Galaxy heap layout before gameplay. Record arena bases, sizes, largest allocations, failures, and high-water marks.

A lawful, source-built homebrew Wii DOL may be used as an optional substrate control. Kirby may be used only if Chris independently supplies legally obtained required game data; the agent must not download it. Failure to obtain a commercial control title does not block Galaxy work.

### 7.2 Extraction and executable inventory

Create `docs/EXECUTABLE-COVERAGE.md` from the **exact supplied image**.

For every executable or potentially executable file, record:

- path and containing partition;
- format (`DOL`, `REL`, `RSO`, raw executable data, unknown);
- SHA-1/SHA-256 and byte size;
- load address/range where derivable;
- loader/call site where known;
- whether DolRecomp covers it;
- whether it is required for normal gameplay;
- runtime path or bounded replacement;
- test scene that proves the decision.

Do not inherit “zero RELs” from a research note without scanning the actual extraction. If ordinary gameplay RELs exist, stop and design their coherent recompilation/runtime registration before claiming broad AOT coverage.

The known Home Button Menu files are a separate dynamic-code case. Inventory them even if the app plans not to execute them.

### 7.3 AOT generation, maps, and fallback telemetry

Generate the first module with the portable C backend unless a documented blocker requires LLVM. Keep all generated output ignored.

Required process:

1. Generate from a clean AOT directory using the exact extracted `main.dol` and title ID.
2. Capture DolRecomp’s section analysis, SMC report, suspicious-instruction report, warnings, unresolved ranges, and output manifest.
3. Supply an exact-region function map only after validating its executable ranges and bytes. Reject a mismatched Petari map.
4. Compile and link the module with AppleClang for macOS ARM64.
5. Record module size, symbol count, object count, compile/link time, Mach-O platform/minimum OS, code-signing state, and DOL identity embedded in the module descriptor.
6. Add runtime telemetry for every dispatch mode: AOT hit, interpreter fallback, macOS JitArm64 fallback, invalid/unknown guest PC, and attempted executable write.
7. For each fallback range, record address, call stack/source symbol when known, frequency, target scene, and whether mobile can execute it.

Development policy:

- macOS JitArm64 fallback may be enabled temporarily to discover uncovered paths.
- iPadOS/iOS may never rely on a runtime PowerPC JIT.
- A bounded interpreter fallback is permissible during bring-up, but every required path must be measured. It may not silently dominate a hot loop or make the mobile build nonviable.
- No public candidate may contain an unexplained executable range, silent SMC bypass, or a gameplay path that works only because macOS JIT handled it.

### 7.4 Self-modifying code and the HOME-menu RSO

DolRecomp documents SMC as unhandled. Treat every store to executable memory, instruction-cache invalidation, branch trampoline, and dynamic module load as a first-class incident.

The known HOME-menu path loads `/ModuleData/product.sel` and `HomeButtonMenuWrapperRSO.rso`, creates jump code, links the module, and exposes seven named operations:

- `HBMCreateRSO`
- `HBMInitRSO`
- `HBMCalcRSO`
- `HBMDrawRSO`
- `HBMGetSelectBtnNumRSO`
- `HBMSetAdjustFlagRSO`
- `HBMStartBlackOutRSO`

GalaxyPad’s baseline must **not** execute or generate that PowerPC jump code on iPadOS/iOS. Implement a narrow native adapter that replaces the Wii HOME-menu behavior with GalaxyPad’s three-dot menu while preserving game-visible pause/resume/fade/selection semantics. Name every replaced function/address, preserve return/state expectations, and add regressions for:

- opening and closing the native menu from gameplay;
- no guest HOME overlay or RSO link attempt;
- input cleared while native UI is open;
- audio pause/resume behavior;
- scene/cutscene return;
- background/foreground while the menu is open;
- clean quit without a stuck blackout or paused game.

Never “solve” an SMC report by globally ignoring executable writes or disabling cache semantics.

### 7.5 Wii services gate

Create `docs/WII-SUBSYSTEMS.md` and verify separately:

- Wii disc header and encrypted data partition access;
- IOS/ES boot path used by the title;
- clean virtual NAND and title save directories;
- SYSCONF region, language, aspect, progressive, and controller settings;
- MEM1/MEM2 address spaces, arenas, caches, and paired Galaxy heaps;
- DVD/file reads, async callbacks, cancellation, and scene transitions;
- OS alarms, threads, timing, and exception behavior;
- GX command processing, EFB/XFB, texture cache, mipmaps, and Metal presentation;
- DSP/JAudio production and Apple output;
- WPAD/KPAD connection state, Wii Remote, Nunchuk, rumble, speaker, and disconnect behavior.

Do not use an external personal NAND dump as the default. Generate the smallest clean, local, ignored Wii state supported by the runtime. If the title truly requires data not generated or present on the disc, document the exact requirement and stop rather than downloading it from an untrusted source.

### 7.6 Pointer and EFB/Z-readback gate

Dolphin’s stable `RMG` settings require:

```ini
[Video_Hacks]
EFBAccessEnable = True
EFBAccessDeferInvalidation = True

[Video_Enhancements]
ArbitraryMipmapDetection = True
```

These settings are the baseline. Do not disable CPU EFB access to obtain a higher FPS number; the Star Pointer’s world interaction depends on depth reads.

Create `docs/EFB-READBACK.md` and instrument:

- every `GXPeekZ`/CPU EFB read count, coordinates, channel, scene, and reason;
- render-thread wait, GPU completion wait, readback latency, and total frame contribution;
- active pointer count and deliberate pointer-visible state;
- 1× EFB baseline before higher internal resolutions;
- file select, Observatory, dense galaxy gameplay, Star Bit sweeps, Pull Stars, cannon aim, sling pod, bubble, talk interaction, cutscenes, and transitions;
- correctness under deferred invalidation and after renderer recreation.

Acceptance rules:

- Pointer target depth and selection must match the reference behavior.
- No stale, fabricated, constant, delayed-by-several-frames, or always-frontmost depth value may substitute for a real read merely to improve performance.
- Optimize only after baseline evidence. Candidate optimizations include one read per active pointer per frame, suppressing P2 reads when Co-Star mode is disabled, deliberate off-screen state when no pointer interaction is active, batching/caching proven equivalent reads, or a game-specific replacement whose math is validated against the original.
- Every optimization is default-off until it reproduces the same target/depth outcomes and improves recorded frame time.
- A stable 60 Hz average with severe spikes is not a pass. Record percentiles and worst-case transition/readback frames.

### 7.7 Control and motion gate

Create `docs/INPUT-AND-POINTER.md` and `docs/MOTION-AUDIT.md`.

Inventory every use of:

- Wii Remote buttons and D-pad;
- Nunchuk stick, C, and Z;
- IR position, visibility, distance, roll, and pointer channels;
- Wii Remote and Nunchuk shake/swing;
- accelerometer and gyroscope data;
- rumble;
- Wii Remote speaker state;
- P2/Co-Star input.

#### Technical baseline control modes

**macOS:**

- keyboard and mouse profile;
- conventional controller profile;
- mouse absolute pointer;
- explicit Spin button;
- right-stick or another deliberate axis for tilt stages;
- generated `WiimoteNew.ini` must select an emulated Wii Remote with Nunchuk, not `Extension = None` or sideways-only defaults.

**iPad/iPhone touch:**

- left Nunchuk movement stick;
- A, B, C, Z, Plus/pause, Spin, and any required D-pad/secondary button;
- full-screen absolute pointer surface that does not conflict with the editable controls;
- touch-edit mode, independent size/opacity, safe areas, and reset;
- no mandatory device shake or device tilt.

**physical controller:**

- left stick → Nunchuk;
- face/shoulder buttons → A/B/C/Z/Spin/Plus according to a documented default;
- right stick → pointer with recenter/sensitivity options or another accepted pointer mode;
- right stick or a mode-specific axis → ball/ray tilt where required;
- haptics when available, safe no-haptics behavior otherwise.

#### Spin and shake

ModernGekko’s current touch override exposes buttons, IR, and Nunchuk controls but not explicit accelerometer/shake channels. Add a narrow GalaxyPad-owned virtual Spin/shake path.

Preference order:

1. Extend the runtime input overrider with explicit Wii Remote/Nunchuk shake pulse controls, preserving the guest’s existing action queries.
2. If that is not viable, replace one named game input query or action function so a host Spin pulse is ORed with the original swing result.
3. Do not globally repurpose A or B, because both have context-sensitive gameplay uses.

Test spin initiation, cooldown/refractory behavior, held-button behavior, repeated spins, swimming, Launch Stars, enemies, transformations, cutscenes, and any non-Mario shake consumer. A dedicated button is the baseline; optional shake gestures may be added later.

#### Pointer product modes

Implement in two stages:

1. **Classic Pointer mode (bring-up):** touch/mouse/right-stick controls IR position; A and B remain explicit controls. This is the lowest-risk correctness path.
2. **Direct Touch mode (product target):** a tap or touch-and-drag performs the correct context-sensitive pointer action without requiring the player to aim, release, then reach for another button. It must be accepted separately for file select, ordinary menus, Star Bit collection/shooting, Pull Stars, cannons, sling pods, and bubble blowing. It may use named game-state hooks; it may not indiscriminately emit A or B in every context.

Classic Pointer remains available as a fallback even after Direct Touch is accepted.

Pointer visibility is an explicit state machine. Do not inherit “IR signal disappeared” semantics that leave the cursor hidden after cutscenes, pipes, teleports, native menus, or lifecycle transitions. Test every such transition.

Distance-to-display zoom and pointer roll are non-essential for the baseline unless exact gameplay evidence proves otherwise. Preserve neutral values and document the omission rather than feeding noisy synthetic data.

#### Tilt stages

The baseline must provide a conventional stick-backed route for every mandatory accelerometer-controlled mechanic. Source-inspect and patch each consumer rather than assuming one class covers all tilt gameplay.

For sphere/ball stages, evaluate reusing the game’s `SpherePadController` behavior or redirecting the relevant accelerometer path to normalized host axes. Apply the same discipline to ray surfing and any other tilt mechanic. Preserve dead zones, sensitivity, braking, jump, camera-relative direction, reset/recenter, and tutorial prompts.

Optional motion may be added after the stick path is accepted:

- use controller `GCMotion` only when the connected controller reports supported motion;
- activate sensors only while needed and deactivate on pause/background/disconnect;
- never assume Xbox controllers have gyro;
- keep device/iPad tilt default-off because physically tilting the display is an inferior baseline and an accessibility burden.

### 7.8 Audio and Wii Remote speaker gate

Create `docs/AUDIO.md` and separate three paths:

1. DSP/JAudio game mix;
2. Apple audio output and lifecycle;
3. Wii Remote speaker stream.

Verify music, voices, ambient audio, UI, Star Bit sounds, spin, launch, enemies, transformations, bosses, cutscenes, Observatory, final sequence, and credits. Record sample rate, producer cadence, queue depth, underruns, pitch, guest timebase, and interruption recovery.

Galaxy’s Wii Remote speaker subsystem encodes and sends small buffers on a periodic alarm. GalaxyPad has no separate controller speaker requirement. Route those decoded cues into the main host output with a separately adjustable **Wii Remote Speaker** volume and preserve relative timing. If the selected runtime already decodes the stream, expose that output; otherwise add a bounded host sink. Do not silently report speaker success because main audio plays.

A private feasibility build may advance while speaker routing is open if it does not block progression. A public/complete candidate requires either:

- accepted mixed speaker cues with evidence; or
- Chris’s explicit documented decision that the cues are intentionally omitted, with honest release wording.

### 7.9 Save, NAND, and identity gate

Create `docs/SAVE-AND-NAND.md`. Test with disposable local state:

- clean virtual NAND initialization;
- first file creation and profile name;
- saves after the first Grand Star and later story gates;
- multiple file slots;
- file copy/erase behavior;
- relaunch/load after normal quit;
- relaunch/load after forced app termination;
- background/foreground during a pending write;
- repeated writes and long sessions;
- backup and byte-for-byte restore;
- corrupt/truncated save handling;
- no cross-talk between macOS, Simulator, device, and test fixtures unless an explicit migration is performed;
- no deletion of saves when stored game data is removed;
- module/disc identity mismatch rejection before save access.

Never commit a save or NAND fixture. Record only hashes, sizes, operations, and game-visible outcomes.

### 7.10 Phase 1 pass condition

Phase 1 is complete only when:

- exact disc and DOL identity are recorded;
- extraction is deterministic and every executable file is classified;
- Broadway mode and 64 MiB MEM2 are proven by an executable guard;
- the selected coherent toolchain is pinned;
- DolRecomp generation completes with every warning/SMC finding interpreted;
- the ARM64 module compiles and links;
- dispatch/fallback telemetry exists;
- Wii services have a written test inventory;
- the HOME-menu RSO has a bounded native strategy;
- input, pointer/EFB, motion, audio/speaker, and save plans are explicit;
- all remaining risks are recorded without being mislabeled as passes.

---

## 8. Phase 2: macOS bring-up and complete-game path

Build a reproducible pipeline, not a terminal-history artifact. Port the shape of SunPad’s scripts and add Wii-specific guards. Provide single-purpose commands equivalent to:

```text
scripts/check-prerequisites.sh
scripts/bootstrap-dependencies.sh
scripts/verify-sources.sh
scripts/verify-wii-mode.sh
scripts/identify-disc.sh
scripts/prepare-disc.sh
scripts/inventory-executables.sh
scripts/build-host-tools.sh
scripts/generate-galaxy-module.sh
scripts/audit-smc-and-coverage.sh
scripts/build-macos-app.sh
scripts/run-macos-smoke.sh
scripts/build-ios-simulator-core.sh
scripts/build-ios-device-core.sh
scripts/capture-crashes.sh
scripts/check-repository.sh
scripts/audit-apple-package.sh
scripts/package-unsigned-ipa.sh       # created but not authorized for release
```

Every script must be idempotent for verified unchanged inputs and stop rather than mutate an unknown or mismatched checkout.

### 8.1 macOS bring-up ladder

Each rung is tested immediately and receives a dated screenshot/log/profile where applicable:

1. GalaxyPad initializes its owned directories, settings, logs, and a Metal surface without touching the original image.
2. The app selects/validates the supported image and proves module/DOL identity match.
3. ModernGekko boots in Wii/Broadway mode; MEM1/MEM2, clean NAND, IOS/ES, SYSCONF, DVD/file services, DSP, GX, and WPAD/KPAD initialize without an unexplained fallback.
4. The AOT module entry point executes; dispatch telemetry confirms AOT activity and records any fallback.
5. The title renders at the expected cadence with continuous audio and stable memory.
6. Mouse/controller pointer selects a file slot and the new-file flow accepts input.
7. The Star Festival/opening completes without timing, cutscene, audio, disc-read, or pointer failure.
8. Gateway Galaxy loads; Nunchuk movement, A jump, C/Z, camera, pointer, Star Bits, and the dedicated Spin action work when the game makes spin available.
9. Pointer depth interactions and launch/Pull Star behavior work with correct EFB reads.
10. The first Grand Star is obtained, the Comet Observatory loads, and the save is written.
11. GalaxyPad exits cleanly, relaunches with the same exact disc/module identity, and restores the file in a playable Observatory state.

Only after rung 11 works may the macOS build be described as **playable**. Before that, use precise wording such as “boots,” “reaches title,” or “reaches Gateway Galaxy.”

### 8.2 Story-complete route

Run at least one fresh GalaxyPad-created save through the full story path. Record every observatory unlock, dome transition, Grand Star, major ability/tutorial, boss, required transformation, and final sequence. The route must end with:

- the final Bowser encounter completed;
- credits completed without audio/video/timing failure;
- post-credits return/save visible;
- clean exit and relaunch into the post-game file.

Do not substitute an imported late-game save for the fresh story proof. Keep ignored later-game fixtures for regression speed, but identify their origin and never publish them.

### 8.3 Completion and mechanic route

After story completion, build a coverage ledger by galaxy/mission/mechanic rather than relying on random play. Include:

- every observatory dome and major galaxy family;
- comet variants and Hungry Luma routes;
- Green/Trial content;
- Bee, Boo, Spring, Fire/Ice, Flying, and other transformations present in the supported revision;
- all major bosses and multi-phase battles;
- swimming, flying, gravity transitions, moving platforms, rails, launch stars, and scripted camera paths;
- ball-rolling and ray-surfing non-motion controls;
- cannon, sling pod, bubble, Pull Star, menu, and Star Bit pointer modes;
- Luigi/post-game unlocks and completion sequence;
- file-select and save behavior after high completion.

A completion claim requires evidence that no content class is inaccessible and that a GalaxyPad-created completion state has been reached. Until then, report the exact highest verified boundary.

---

## 9. Phase 3: timing, performance, Apple targets, and product shell

### 9.1 Reference cadence and rendering baseline

Do not derive performance targets from the host display refresh rate. Establish the supported revision’s behavior from a known-good reference run and game source:

1. Measure VI/retrace, game-update, rendered-frame, present, audio-task, and input-poll cadence in title, file select, Observatory, Gateway, dense galaxies, bosses, transformations, pointer-heavy scenes, transitions, final sequence, and credits.
2. Confirm the expected 60 Hz path and document any intentional half-rate animation, cutscene, loading, or PAL behavior.
3. Use 1× internal resolution first. For the known NTSC/EURGB60 path, treat 640×456 as the expected EFB reference until the exact revision proves otherwise.
4. Measure median, 95th, 99th, and worst frame intervals; CPU and GPU time; EFB wait/readback time; memory high-water marks; DSP/audio queue behavior; module dispatch mix; and thermal state on devices.
5. Profile with Instruments and runtime counters. Change one variable at a time.
6. Verify 4:3 and native 16:9 separately. Native 16:9 may become the product default after acceptance; Fill/ultrawide remains experimental.
7. Higher render scales (2×–4×) are quality options, not baseline acceptance. Each carries its own pointer/EFB and device performance result.

Never label an option “60 FPS mode”; 60 Hz is the original baseline. Any mode that alters CPU clock, synchronization, or game cadence is an unstable experiment and default-off.

### 9.2 Pointer and direct-touch acceptance

For every pointer scene, capture:

- touch/mouse/controller coordinate;
- guest IR coordinate and visibility state;
- framebuffer coordinate;
- returned depth;
- selected target or no-target result;
- guest A/B/shoot state;
- frame/readback latency;
- transition before and after the interaction.

Direct Touch must not block camera/movement controls, trigger accidental Star Bit shots in menus, select a hidden/off-screen UI item, remain held after a native sheet, or disappear after a transition. Validate multiple aspect ratios and safe-area/device classes.

### 9.3 iPadOS Simulator — first mobile target

Only after the macOS first-play loop is stable:

1. Shut down all Simulators and verify none are booted.
2. Build the ModernGekko/RecompCore core, Galaxy module, and GalaxyPad app for one arm64 iPad Simulator destination.
3. Preserve the mobile boundary: no JitArm64, no executable memory generation, no downloaded module, and no writable-executable vertex loader.
4. Provision the exact matching module and game data through ignored development paths.
5. Complete the first-play loop with touch controls and capture Simulator evidence.
6. Test Direct Touch and Classic Pointer, Spin, Nunchuk movement, save/relaunch, three-dot menu, background/foreground, controller connect/disconnect, and diagnostics.
7. Record performance as diagnostic only.
8. Kill the app and shut down the iPad Simulator before moving to iPhone.

### 9.4 iPhone Simulator — second mobile target

Repeat the same process with one iPhone Simulator only after the iPad Simulator is shut down. Use the same exact DOL/module identity and stable configuration. Complete the first-play loop and separately accept compact-phone control reachability, pointer precision, menu readability, safe areas, thermal-risk assumptions, and no stuck input.

Simulator success does not prove physical-device speed, heat, audio routing, touch feel, storage behavior, or sustained memory pressure.

### 9.5 Porting the SunPad shell

Extract game-neutral code into GalaxyPad-owned paths before renaming symbols. Preserve provenance and license notices.

#### Core Apple host

Port and adapt:

- UIKit/AppKit + CAMetalLayer presentation;
- background game thread and deterministic shutdown;
- ModernGekko runtime construction and error reporting;
- module identity and signed-module loading for development;
- shared settings and normalized thread-safe input;
- controller enumeration, stable P1 ownership, stale-controller reconciliation, disconnect release, and touch auto-hide;
- lifecycle pause/resume, audio deactivation/reactivation, renderer recreation, memory warning, and save grace window;
- persistent low-frequency diagnostics and privacy-bounded report generation.

Do not port Sunshine-specific GameCube pad mappings, analog FLUDD trigger behavior, GMSE01 hashes, 30-fps patches, widescreen code, game-specific save paths, or Sunshine labels.

#### Game-data import and module matching

The development build may use a host-prepared extracted tree. The product shell must support a user-selected exact image without bundling it.

Evaluate two storage-safe routes:

1. retained validated image mounted/read through the runtime; or
2. staged local extraction to an app-private game tree.

For either route:

- preflight available storage and report the actual required space;
- avoid an unnecessary full-image + full-extraction + second staging copy peak;
- use a unique staging directory and atomic activation;
- leave the prior working installation intact after a failed reimport;
- validate title ID, revision, image/DOL hash, partition, required files, and module identity before launch;
- keep saves separately and preserve them when game data is removed;
- never compile on-device or download an executable module;
- reject a valid Galaxy image whose `main.dol` does not match the provisioned module, with actionable wording.

#### Touch controls

Start from SunPad’s raw multitouch, editing, normalized positions, grouped controls, size/opacity, safe-area, controller handoff, input-latch, and reset mechanisms. Replace the control surface with Galaxy-specific defaults:

- large Nunchuk movement stick on the left;
- large **A / Jump** action;
- dedicated **Spin** action;
- **B**, **C**, and **Z**;
- **Plus / Pause**;
- D-pad and Minus/1/2/Home available in edit/advanced layout even if rarely used;
- pointer surface over the gameplay viewport;
- context-safe pointer tap/hold/drag behavior;
- tilt-stick mode available when a tilt section is active or manually selected.

All controls must have VoiceOver labels in native UI, sufficient contrast, minimum touch size, and no overlap with the three-dot menu or unsafe screen edges. A pointer touch must not drag the editable controls outside edit mode.

No input may remain held after menu presentation, alert, file picker, share sheet, controller handoff, app resign-active, backgrounding, crash recovery, or runtime restart.

#### Three-dot menu

Match the accepted SunPad hierarchy and behavior, adapted to Galaxy:

- **Display**
  - Auto / 1× / 2× / 3× / 4× internal resolution;
  - Native 16:9 and Original 4:3;
  - Fill Screen only as clearly labeled experimental behavior;
  - filtering/mipmap options only when supported and tested;
  - FPS/performance overlay as a developer option.
- **Controls**
  - Touch Controls on/off;
  - Direct Touch / Classic Pointer;
  - pointer sensitivity/recenter for controller mode;
  - Spin mapping;
  - tilt-stick sensitivity/inversion/recenter;
  - physical-controller mapping;
  - layout edit, reset, size, and opacity;
  - automatic hide with a physical controller.
- **Audio**
  - main volume;
  - Wii Remote Speaker volume;
  - explicit output/mute status where useful.
- **Unstable Experiments**
  - default-off only;
  - restart requirements and mode identity logged;
  - no experiment may silently replace the stable path.
- **Game Data & Saves**
  - import or reimport;
  - validate/identify supported image;
  - show exact title/revision/DOL identity;
  - remove stored game data without removing saves;
  - show save/NAND status and safe actions only.
- **Share Diagnostic Log**
- **Report a Problem**
- **About / Third-Party Notices / Rights wording**

The menu replaces the Wii HOME overlay. Test dismissal, pause/resume, pointer state, held-input clearing, audio, backgrounding, and return to gameplay.

#### Diagnostics

Log, at minimum:

- app/build/source identity;
- disc title ID, revision, and hashes without game bytes;
- module DOL identity and signature status;
- boot phase and Wii/Broadway/MEM2 state;
- IOS/ES/NAND/SYSCONF milestones;
- renderer, EFB scale/aspect, frame cadence, and EFB-readback counters;
- AOT/interpreter/JIT dispatch counts and unknown PCs;
- HOME-menu replacement state;
- controller ownership, pointer mode/visibility, input clear, Spin/tilt mode identity;
- audio/DSP/speaker mode and underrun summary;
- save-write milestones without save contents;
- lifecycle, memory warning, thermal state on device, runtime warning/error, screenshot marker, and clean exit.

Exported diagnostics must exclude disc bytes, extracted filenames where unnecessarily revealing, generated code, saves/NAND contents, screenshots, speaker/game audio samples, absolute container paths, signing information, credentials, and raw controller/touch histories.

### 9.6 Original app icons and branding

Create a complete original icon set for:

- macOS `.icns` / asset catalog sizes;
- iPhone and iPad AppIcon asset slots;
- high-resolution source artwork retained in an editable project-owned format;
- `PROVENANCE.md` recording authoring method, date, prompt/source inputs if generated, and confirmation that no game assets were used.

The icon should communicate a cosmic/galactic “GalaxyPad” identity without using Mario, Lumas, stars copied from Nintendo art, Nintendo logos, screenshots, box art, or extracted textures. Verify legibility at favicon/small-icon size, light/dark wallpapers, rounded iOS masks, and macOS presentation.

---

## 10. Phase 4: test matrix

Adopt the attached reference documents’ evidence rules: compilation is not gameplay, source inspection is not runtime acceptance, one Simulator means exactly one, and every claim belongs to the exact artifact that was run.

For every row record target, hardware/Simulator, OS, build configuration, root revision, dependency-lock revision, disc title/revision/hash, DOL/module hash, commands, settings/mode identity, logs, screenshots/profiles, result, and remaining defects. Rows marked hands-on require real interaction; automation supplements but does not replace them.

| # | Row | Target | Pass condition |
|---|---|---|---|
| 1 | Repository safety and rights state | repo | `RIGHTS-STATUS.md` is explicit; game/generated/save/log/signing patterns are ignored and actively rejected |
| 2 | Exact disc identity | clean checkout + supplied image | Title ID, region, revision, partitions, full-image hashes, DOL hashes, and deterministic manifest recorded; original unchanged |
| 3 | Wii/Broadway/MEM2 guard | host tools | Build refuses missing title setup or GameCube fallback; Broadway and 64 MiB MEM2 proven in logs/tests |
| 4 | Extraction and executable inventory | extracted image | Every DOL/REL/RSO/executable candidate classified; no silent “zero REL” assumption |
| 5 | AOT generation and module identity | macOS build | DolRecomp completes; SMC/warnings interpreted; ARM64 module links; descriptor matches exact DOL |
| 6 | Dispatch and fallback coverage | macOS | AOT/interpreter/JIT/unknown telemetry works; no required path depends on unexplained or mobile-incompatible fallback |
| 7 | HOME-menu RSO replacement | macOS + iPad Sim | Native menu opens/closes; no RSO execution/jump generation; pause/audio/input/return semantics pass |
| 8 | Wii service initialization | macOS | IOS/ES/NAND/SYSCONF, MEM1/MEM2, disc, DSP, GX, WPAD/KPAD initialize with clean evidence |
| 9 | Boot to title and file select | macOS, iPad Sim, iPhone Sim | Title renders with audio; pointer can create/select a file; clean runtime log |
| 10 | Opening and Gateway Galaxy | macOS hands-on; iPad Sim hands-on | Opening completes; movement, jump, camera, Star Bits, pointer, Spin tutorial/action, and launch interactions work |
| 11 | First Grand Star and persistence | all three | First Grand Star obtained; Observatory reached; save writes; clean exit/relaunch restores playable state |
| 12 | Observatory and dome transitions | macOS | Repeated observatory/dome/galaxy entry and return preserve render, pointer, audio, memory, and save state |
| 13 | Story progression and final credits | macOS hands-on | Fresh-save route reaches final Bowser, completes credits, returns post-game, saves and reloads |
| 14 | Completion-content coverage | macOS | Required comet/Hungry Luma/Green/Trial/Luigi/post-game paths and completion sequence are reachable and recorded |
| 15 | Mario movement, gravity, camera, and transformations | macOS + iPad Sim | Representative ground, water, flying, gravity transitions, camera, and every transformation class pass |
| 16 | Pointer menus and ordinary interactions | macOS + iPad Sim + iPhone Sim | File/menu selection, Star Bit collection/shooting, Pull/Launch Stars, talk/target depth and visibility pass |
| 17 | Continuous pointer mechanics | macOS + iPad Sim hands-on | Cannon, sling pod, bubble/air and any other hold-drag pointer mechanics are controllable and correct |
| 18 | Spin and shake replacement | all three | Dedicated Spin and every mandatory shake consumer preserve trigger/cooldown/context behavior without device shaking |
| 19 | Ball, ray, and other tilt mechanics | macOS + iPad Sim hands-on | Stick-backed non-motion routes complete required stages; deadzone/sensitivity/recenter/brake/jump behavior accepted |
| 20 | Reference timing and frame pacing | macOS | 60 Hz baseline documented; scene profiles and frame-time percentiles show no material timing drift |
| 21 | EFB/Z-readback correctness and cost | macOS + iPad Sim | Required `GXPeekZ` semantics pass; readback counts/stalls recorded; no invalid shortcut; pointer-heavy scenes remain usable |
| 22 | Rendering correctness | macOS + iPad Sim | 1× 640×456 reference, 4:3/native 16:9, mipmaps, reflections, shadows, effects, cutscenes, transitions and higher scales tested |
| 23 | MEM1/MEM2 and heap stability | macOS + iPad Sim | Arena/layout/high-water evidence; no OOM, alias, corruption, or unbounded growth through heavy transitions |
| 24 | Main audio and Wii Remote speaker | macOS + iPad Sim | Correct pitch/continuity and cues; speaker stream mixed or explicit accepted omission; no sustained underrun/desync |
| 25 | NAND saves and recovery | macOS + iPad Sim | Fresh/multiple saves, repeated writes, termination, copy/erase, backup/recovery, corruption and data-removal separation pass |
| 26 | iPadOS Simulator core | one iPad Sim only | First-play loop with same AOT identity, no JIT/dynamic code, touch/menu/lifecycle/diagnostics pass |
| 27 | iPhone Simulator core | one iPhone Sim only | iPad Simulator shut down first; compact layout and first-play loop pass with same AOT identity |
| 28 | Touch UI and Direct Touch | iPad Sim + iPhone Sim hands-on | Controls/edit/reset/opacity/safe areas/Classic Pointer/Direct Touch/tilt mode and no stuck inputs pass |
| 29 | Physical-controller and haptics | macOS + Simulators | Mapping, P1 ownership, connect/disconnect, touch hide/show, pointer/recenter, no-motion completeness, and safe no-haptics pass |
| 30 | Lifecycle and interruption | iPad Sim + iPhone Sim | Native menu, alerts, picker/share sheet, background/foreground, audio interruption, memory warning, renderer return and clean exit pass |
| 31 | Game-data import and module match | iPad Sim + iPhone Sim | Correct image imports/activates; wrong/mismatched image rejected; failure rolls back; remove preserves saves; storage preflight honest |
| 32 | Diagnostics and privacy | macOS + iPad Sim | Required breadcrumbs/mode identity present; export excludes protected game/private/signing data |
| 33 | Clean clone and regression suite | fresh directory | Full pipeline reproduces from scripts/pins; automated unit/smoke tests pass; no undocumented manual build step |
| 34 | Soak and repeated transitions | macOS + iPad Sim | At least 60 minutes with repeated observatory/galaxy/pointer/save cycles; stable frame/audio/memory/EFB/input/save state |
| 35 | Original icon/branding package | macOS + iOS assets | Complete icon sets render correctly; provenance exists; no Nintendo/game asset or copied logo is present |
| 36 | Exact public candidate | physical iPad + iPhone + Mac + audits | Chris plays exact artifacts; source/package/notices/rights gates pass; hashes recorded; explicit final authorization exists |

Rows 1–35 are the technical program. Row 36 is not inferred from them. A source release, macOS binary release, and unsigned IPA release are separate decisions and may have different rights outcomes.

---

## 11. Evidence, journal, and reporting

Maintain in `docs/`:

- `JOURNAL.md`: append-only, dated. Every session records the lowest unmet goal, hypothesis, bounded step, exact commands, result, evidence path, interpretation, blocker analysis, and next step.
- `STATUS.md`: current goal, macOS bring-up rung, Simulator order/state, matrix status, exact known-good commands/artifact hashes, active disc/save identity, and open defects.
- `RIGHTS-STATUS.md`: private/public authorization, source and dependency licenses, provenance, release topology, and decisions required.
- `DISC-IDENTITY.md`: immutable source-image metadata, partition/extraction manifest, DOL identity, supported revision, and module-match rules.
- `DEPENDENCIES.md`: tool versions, exact commits/submodules, licenses, source URLs, checksums, and host requirements.
- `UPSTREAM-DELTA.md`: SunPad-known graph versus selected GalaxyPad graph, every rebase/patch, reason, test impact, and rollback point.
- `EXECUTABLE-COVERAGE.md`: all executable files/ranges, SMC findings, AOT and fallback coverage, replacements, and proof scenes.
- `WII-SUBSYSTEMS.md`: IOS/ES/NAND/SYSCONF, MEM1/MEM2, disc, OS, DSP, GX, WPAD/KPAD state and defects.
- `INPUT-AND-POINTER.md`: control mapping, guest/host channels, pointer modes, visibility state machine, target/readback evidence, controller ownership, and accessibility decisions.
- `MOTION-AUDIT.md`: every swing/accel/gyro consumer, chosen non-motion route, optional motion route, and regression.
- `EFB-READBACK.md`: title settings, readback call sites, counts, stalls, correctness captures, experiments, and before/after profiles.
- `AUDIO.md`: DSP/main output, speaker stream, timing, underruns, cue checklist, lifecycle, and accepted omissions.
- `SAVE-AND-NAND.md`: virtual NAND identity, save operations, hashes, recovery/corruption tests, and data-removal separation.
- `PERF.md`: reference cadence, frame/present/audio/input measurements, EFB cost, CPU/GPU profiles, memory/thermal/soak history, and exact settings.
- `RELEASE-READINESS.md`: exact source/artifact hashes, matrix summary, physical-device evidence, package/source audits, notices, rights decisions, icon provenance, and explicit go/no-go.
- `artifacts/`: local ignored logs, screenshots, videos, Instruments traces, crash captures, manifests, and hashes, organized by date and artifact identity.

Every acceptance record states what was actually run and observed. A source read proves source intent. A successful extraction proves only extraction. A module proves only generation/linkage. A PID proves only process creation. A screenshot proves only one frame. A pointer icon proves neither depth nor target selection. A Simulator proves only Simulator behavior. A save file hash proves neither game-visible restoration nor corruption safety. A different build proves nothing about the candidate.

**Honesty rule: if it was not run and observed, it is not done.**

---

## 12. Public release, legal, provenance, and wording

This section is an engineering release gate, not legal advice.

### 12.1 Initial state

Private local feasibility work is authorized by Chris. No public GalaxyPad source merge, fork publication, macOS binary, app bundle, dylib, IPA, generated module, tag, release, screenshot set, or game-derived artifact is authorized by this PRD alone.

The public-source and public-binary questions differ:

- GalaxyPad integration source may include/adapt GPL-covered SunPad/ModernGekko/Dolphin code and must satisfy exact corresponding-source and notice obligations.
- The locally generated AOT module is derived from a retail executable and may contain translated game logic even when no ISO/assets are bundled.
- A package can be “ROM-free” and still require a separate rights decision.

### 12.2 Release topology

Before publication, `RIGHTS-STATUS.md` must select and justify one:

1. **Separate GPL-compatible integration repository.** GalaxyPad contains permitted Apple/runtime integration, scripts, patches, tests, and docs; users build against their own supported image. Generated game code and extracted data remain local. Binary distribution remains a separate decision.
2. **Private-only project.** No source or binary publication.
3. **Another explicitly reviewed topology.** Record permissions, licenses, corresponding-source plan, generated-module treatment, notices, and package boundary before use.

Do not publish inside Petari or imply Petari maintainers endorse a native port. Respect its contribution policy and use it as a read-only reference.

### 12.3 Source and package audits

Audits must find no:

- Wii ISO/WBFS/RVZ or partition dump;
- `main.dol`, REL, RSO, extracted Nintendo asset, audio, model, texture, text, or system file;
- generated DolRecomp C, object, archive, or module unless an explicit binary-rights decision authorizes the exact artifact;
- save/NAND data, crash memory, raw private logs, screenshots/audio samples not approved for publication;
- title keys, personal NAND, credentials, tokens, signing identities, provisioning profiles, or machine-specific secrets;
- accidental `ref/`, `generated/`, build-cache, developer-path, or user-home content;
- unfulfilled GPL/source/notice obligation;
- Nintendo trademark/logo/art copied into GalaxyPad’s icon or branding.

### 12.4 Approved descriptive wording

Use this substance only after publication is authorized:

> GalaxyPad is an unofficial native Apple integration for a user-supplied supported Super Mario Galaxy Wii disc image. It uses ahead-of-time static recompilation through DolRecomp and a ModernGekko/Dolphin-derived compatibility runtime for Wii services and Metal rendering. Users must supply their own legally obtained supported game data. GalaxyPad is not affiliated with, endorsed by, or sponsored by Nintendo.

Do not call it official, emulator-free, a decompilation port, or proof that owning a disc automatically grants redistribution rights. Do not imply Petari, DolRecomp, ModernGekko, Dolphin, or SunPad maintainers endorse GalaxyPad.

### 12.5 Public-candidate gate

A public candidate requires all of the following in `RELEASE-READINESS.md`:

- D1–D11 and technical matrix rows 1–35 green or an explicitly scoped preview boundary that names every open row;
- exact root/source/dependency revisions and exact artifact hashes;
- exact supported disc identity and module-match rule, without distributing the disc;
- physical Mac, iPad, and iPhone hands-on evidence for the exact candidate;
- source and package audits green;
- complete third-party notices and corresponding-source plan;
- original icon provenance complete;
- explicit decisions for source distribution, macOS binary, and IPA/module distribution;
- no unresolved severity-1 progression, save, crash, privacy, package, or rights issue;
- Chris’s explicit final authorization for that exact release action.

---

## 13. Risk register

| Risk | Standing | Required response |
|---|---|---|
| Apple ARM64 Wii path unproven in this lineage | Primary substrate risk | Start from SunPad’s known Apple graph; prove Broadway/MEM2/Wii services on macOS; update upstream only as a coherent reviewed graph |
| CPU EFB/Z readback on Apple GPU | Primary performance/correctness risk | Instrument at first pointer frame; 1× baseline; preserve real depth; profile stalls; optimize only with semantic equivalence |
| iPhone 60 Hz performance/thermal limits | Unproven | macOS then iPad Simulator then iPhone Simulator; physical profiles; quality-scale fallback without changing game cadence |
| Supplied disc revision unknown | Expected | Derive exact identity/hashes; never hard-code a guessed U.S. hash; reject module mismatch |
| “Zero RELs” may not hold for exact image | Research-supported, not yet proven | Scan exact extraction; inventory every executable; stop on unhandled required module |
| DolRecomp missing-title database downgrades to GameCube mode | Confirmed tool footgun in reviewed source | Mandatory setup plus executable Broadway/MEM2 guard in every build entry point |
| SMC unsupported | Toolchain limitation | Run exact-DOL report; inspect executable writes/icache; named bounded replacements only; no global bypass |
| HOME-menu RSO generates/executes code | Confirmed bounded dynamic path | Replace seven-entry subsystem with native menu adapter; test pause/fade/input/lifecycle; never run RSO on mobile |
| MEM2 heap layout and OOM | Confirmed game architecture | Instrument arenas/paired heaps/high-water marks; preserve address layout; investigate first panic, never enlarge blindly |
| AOT module size/build time | Unknown for Galaxy | Record output/object/module size and load/link time; cache by DOL/toolchain identity; keep generated outputs local |
| Mac JIT hides missing AOT coverage | Likely bring-up hazard | Dispatch telemetry; no required path accepted solely under JitArm64; mobile no-JIT test early |
| Pointer visibility lost after transitions | Known risk class | Explicit host/guest visibility state machine; regression across cutscenes, teleports, menus, lifecycle, controller handoff |
| Direct Touch emits wrong context action | Product risk | Classic Pointer first; mode-aware Direct Touch; per-context matrix; fallback remains available |
| Required shake path absent from current touch overrider | Confirmed source gap | Add explicit virtual shake/Spin channel or one named input replacement; test every consumer |
| Tilt mechanics depend on accelerometer | Confirmed | Full motion-consumer audit; stick-backed route for every mandatory mechanic; optional motion later |
| Nunchuk not emitted by generic controller profile | Confirmed configuration gap | Generate emulated Wii Remote + Nunchuk profile; regression on C/Z/stick and reconnect |
| Wii Remote speaker cues lost | Confirmed separate subsystem | Decode/route into main mix with volume and timing tests, or explicit Chris-approved omission |
| Wii NAND/save behavior on Apple lifecycle | Unproven | Clean NAND, repeated/termination/recovery/corruption tests; saves separate from game data |
| Wii image import requires large storage/copies | Product risk | Storage preflight; choose mount vs extraction deliberately; atomic staging; avoid unnecessary triple-copy peak |
| Toolchain drift and mixed pins | High | Dependency lock, upstream-delta ledger, exact patch provenance, one coherent update at a time, full matrix rerun |
| SunPad patch overreach | High | Port mechanisms first; reproduce Galaxy symptom before applying Sunshine-specific fixes |
| Full-game regression cost | High | Fresh story completion plus structured completion ledger; ignored milestone fixtures and scripted smoke routes never replace proof |
| Simulator/device gap | Certain | Physical iPad/iPhone acceptance for exact artifact; no device claim from Simulator |
| GPL/provenance obligations | Confirmed | Preserve notices/source, audit copied code and patches, document corresponding-source plan |
| Generated AOT module rights | Unresolved public-release question | Keep local/private; separate source and binary decisions; never infer clearance from ROM-free packaging |
| Commercial/takedown sensitivity | Non-technical risk | Conservative wording, no assets, no automatic publication, explicit final authorization |
