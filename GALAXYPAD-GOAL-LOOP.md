# GalaxyPad goal-based loop

Operating loop for the autonomous build of GalaxyPad. The requirements live in `docs/PRD.md`; this document is how you run. Written 4 Sep 2026.

## The goal stack

Work the lowest unmet goal. A goal is met only when its required evidence exists in `docs/` under PRD Section 11. Never work a higher goal while a lower goal is broken; a regression reopens the lowest affected goal.

- **G0. Environment, state, and private boundary ready.** Toolchain and free space verified; current git state recorded; `ref/sunpad` and selected upstreams pinned/read with push disabled; `RIGHTS-STATUS.md` says `private-only` or a stronger explicitly approved state; repository safety checks reject game/generated/save/private data; no stray Simulator or game process exists.
- **G1. Exact Galaxy input identified.** Original image preserved; title ID, region, revision, partitions, full-image hashes, `main.dol` hashes, deterministic extracted manifest, and every executable-looking DOL/REL/RSO/blob are recorded. `config/galaxypad-disc.json` represents the exact supported input.
- **G2. Wii/Broadway substrate proven.** DolRecomp setup/title data and `wit` are pinned; the build guard proves Wii/Broadway mode and 64 MiB MEM2; the selected coherent ModernGekko/RecompCore graph initializes the Wii address model; a missing database can no longer silently create a GameCube build.
- **G3. Executable model and AOT module proven.** Exact-DOL C-backend generation completes; SMC and warnings are interpreted; executable inventory and coverage telemetry exist; the ARM64 module compiles/links; every fallback/unknown PC is named; the HOME-menu RSO has a bounded native replacement plan.
- **G4. macOS Wii runtime boots.** GalaxyPad creates a Metal surface; exact disc/module identity matches; IOS/ES/NAND/SYSCONF, MEM1/MEM2, disc, DSP, GX, and WPAD/KPAD initialize; the AOT entry point executes; no unresolved native link or fatal runtime-init failure remains.
- **G5. macOS title and file select work.** Stable video/audio reach the title; mouse/controller pointer works in file select; a new file can be created; pointer/EFB and input breadcrumbs are credible. A title screenshot alone does not satisfy this goal.
- **G6. macOS first Grand Star loop works.** New file → Star Festival/opening → Gateway Galaxy → movement/jump/camera → pointer/Star Bits/Pull or Launch interaction → dedicated Spin when unlocked → first Grand Star → Comet Observatory → save → clean exit/relaunch/load. This is the first hard technical feasibility gate. (PRD D3)
- **G7. Complete macOS story works.** A fresh GalaxyPad save progresses through all required story gates, final Bowser, credits, post-game return, save, and relaunch with no progression, timing, render, input, audio, memory, or save blocker. (PRD D4)
- **G8. Completion mechanics and controls are covered.** Pointer menus and world depth, cannon/sling/bubble, transformations, bosses, comet/Hungry Luma/Green/Trial paths, stick-backed ball/ray/tilt controls, all mandatory shake consumers, Luigi/post-game content, and completion sequence have evidence. Direct Touch and Classic Pointer are both usable. (PRD D5, D7)
- **G9. Correctness, performance, audio, and persistence are stable.** Reference 60 Hz behavior, 1× 640×456-class baseline, EFB/Z readback correctness/cost, MEM2 high-water behavior, DSP/main audio, Wii Remote speaker decision, NAND saves, repeated transitions, and 60-minute soak pass. (PRD D6, D8, D11)
- **G10. iPadOS Simulator first-play loop works.** With every other Simulator shut down, one iPad Simulator runs the same exact AOT identity through G6 with no runtime PowerPC JIT or executable-code generation. Touch, pointer, Spin, save/reload, lifecycle, menu, and diagnostics pass.
- **G11. iPhone Simulator first-play loop works.** The iPad Simulator is shut down first; one iPhone Simulator runs the same exact AOT identity through G6; compact controls, pointer precision, safe areas, menu, lifecycle, and diagnostics pass.
- **G12. SunPad-derived GalaxyPad shell is complete.** Game-neutral Apple host, editable Galaxy controls, controller handoff, three-dot menu, game-data import/reimport/remove, module matching, settings, Direct Touch, diagnostics/privacy, original macOS/iOS/iPadOS icons, and provenance are complete. (PRD D10)
- **G13. Technical matrix and clean clone are green.** PRD matrix rows 1–35 pass against exact artifacts; the regression suite and full macOS/iPad Simulator/iPhone Simulator pipeline reproduce from scripts and pins; no undocumented manual build step remains.
- **G14. Physical candidate accepted.** Chris tests the exact candidate on Apple Silicon Mac, physical iPad, and physical iPhone; artifact hashes, hardware/OS, hands-on pointer/touch/control/audio/performance/save evidence, and open defects are recorded. Simulator results cannot satisfy this goal.
- **G15. Public release explicitly authorized.** Source/package rights, GPL/corresponding-source obligations, generated-module boundary, notices, game-data/privacy audits, icon provenance, candidate hashes, and Chris’s explicit release authorization are recorded. Only then may the authorized source, macOS binary, or IPA action occur.

G6 is the first hard feasibility gate. G7 and G13 are the technical release bar. G14 and G15 are mandatory for any public binary. There is no fallback to a title-screen demo, file-select-only release, Gateway-only release, pointer-with-fake-depth release, macOS-JIT-only release, motion-required mobile release, or “ROM-free therefore cleared” release.

`RIGHTS-STATUS.md = private-only` does not block G1–G13. It blocks publication and G15.

## The loop

Repeat until the current authorized terminal goal is met:

1. **Pick** the lowest unmet goal. Choose the smallest concrete step that can advance it.
2. **Check state before acting.** Read `docs/STATUS.md`, the last `JOURNAL.md` entry, the relevant technical inventory, `git status`, running processes, booted Simulators, disc/DOL/module hashes, dependency pins, selected save/NAND, runtime settings, and verified build caches. Do not rebuild or regenerate what a matching verified cache already holds.
3. **State the hypothesis.** Name what this step is testing and what evidence would support or refute it. “Try things” is not a hypothesis.
4. **Execute** one bounded step. Install public tooling, clone public source, or download official setup data only when required; record source/version/hash/license. Never download game data.
5. **Test immediately.** Run the smallest relevant check when the step completes. Compilation is not launch; launch is not title; title is not file select; file select is not Gateway; Gateway is not a saved/reloaded Grand Star; story credits are not completion-content coverage.
6. **Capture evidence.** Put the screenshot, log excerpt, manifest, profile, hash, or capture under the local dated artifacts path. Append one dated journal entry: goal, hypothesis, step, command, result, evidence path, interpretation, and next step.
7. **Update** `docs/STATUS.md` and the relevant inventory (`DISC-IDENTITY.md`, `EXECUTABLE-COVERAGE.md`, `WII-SUBSYSTEMS.md`, `INPUT-AND-POINTER.md`, `MOTION-AUDIT.md`, `EFB-READBACK.md`, `AUDIO.md`, `SAVE-AND-NAND.md`, `PERF.md`, or `RIGHTS-STATUS.md`) if state changed.
8. **Continue.** If the step failed, enter the unblocking ladder before retrying. A changed hypothesis or variable is required for another attempt.

## Process hygiene — hard rules

- **One Simulator at a time.** Before booting a Simulator, run `xcrun simctl list devices booted`; shut down every booted device, then boot only the intended iPad or iPhone. This is not optional.
- **One game instance at a time.** Before launching on any target, kill every previous GalaxyPad, ModernGekko, Simulator app, runtime, launcher, profiler-attached copy, and stray test harness. Multiple instances corrupt save/NAND/config evidence and create false input/audio/renderer defects.
- **Kill before relaunch, always.** Never layer a new run on a hung, crashed, or half-terminated process.
- **One variable at a time.** During runtime, AOT, fallback, EFB, input, timing, audio, MEM2, and optimization work, change one variable, rerun the same evidence-producing test, and journal the result.
- **Clean up after crashes.** Check for booted Simulators, orphan processes, locked save/NAND/config files, stale Metal/Instruments captures, incomplete imports, staging directories, and partial logs before the next run.
- **Never touch the original input.** The image in `ref/rom/original/` and `ref/sunpad` are read-only. Work from ignored staged paths. Re-hash whenever state is uncertain.
- **Never leak game data.** Images, partitions, `main.dol`, REL/RSO files, extracted assets, generated AOT/objects/modules, saves/NAND, screenshots/audio, crash memory, and private logs never enter a commit, issue, upload, public artifact, or paste.
- **No destructive cleanup.** Never run `git clean -fdx`, blanket `rm -rf` against the project root, destructive reset, or a command that can erase ignored inputs/evidence. Inspect exact paths first.
- **Respect unknown work.** Do not overwrite or reset modifications you did not create. Isolate changes or leave a handoff.
- **Pin before patching.** Verify exact root and recursive revisions before applying a SunPad or GalaxyPad patch. A patch applying with fuzz is not proof of correctness.
- **No silent Sunshine carryover.** GMSE01 hashes, GameCube pad mappings, FLUDD analog trigger behavior, Sunshine audio/timing/widescreen patches, save paths, or UI labels are hypotheses until Galaxy reproduces the need.
- **No silent upstream mixing.** ModernGekko, its RecompCore/Dolphin vendor tree, DolRecomp, template, and patch set form one graph. Record and test a coherent update; never cherry-pick random binaries or commits into an unrecorded combination.
- **No title-database footgun.** Every Galaxy build must prove Broadway and 64 MiB MEM2. A build that silently fell back to GameCube mode is invalid regardless of what it renders.
- **No silent stubs.** A stub is allowed only for an optional external device or a named bounded system path whose original contract is understood. Never stub progression, disc reads, pointer depth, save, audio timing, input state, MEM2, or scene behavior merely to reach another screen.
- **No fallback fiction.** macOS JitArm64 or interpreter fallback may expose a missing AOT range; it does not prove that iPad/iPhone can execute the path. Log every mode and keep mobile acceptance separate.
- **No fake EFB optimization.** Never disable CPU EFB access, return a constant/stale depth, force every target to the foreground, or skip draw-sync semantics to make a benchmark green.
- **No motion-only baseline.** Device tilt, device shake, and controller gyro are optional. The lowest accepted path always includes dedicated Spin and stick-backed tilt controls.
- **No runtime-downloaded code.** The Apple apps may import user game data; they may not download a generated module, mod, executable patch, or guest code.
- **Timebox repetition.** The same command failing the same way twice is a blocker. Stop repeating it and enter the unblocking ladder. Never run an unchanged third attempt.
- **No publication by momentum.** A technically green build remains private until G15. Do not push releases, tags, packages, screenshots, or generated files without explicit authorization.

## Wii substrate discipline — hard rules

- Treat disc identity, title ID, DOL identity, Broadway selection, MEM2 state, IOS, NAND, SYSCONF, and module identity as one boot contract. Log them before game code.
- Verify the exact extracted image. “Galaxy usually has no RELs” is not an executable inventory.
- Any required file loaded as executable is an AOT/dynamic-code incident until classified. Record source path, hash, guest range, loader, and route.
- Use a clean local virtual NAND by default. Never borrow or download a personal NAND/system-file bundle to make a failure disappear.
- MEM2 faults are layout incidents before capacity assumptions. Record arenas, paired heaps, allocation, address, and high-water marks before changing sizes.
- The optional homebrew/control DOL may isolate the Wii substrate. A commercial control title is never a hidden prerequisite and may not be downloaded.

## Recompilation and dynamic-code discipline — hard rules

- Capture DolRecomp’s SMC report and every warning for the exact DOL. Suppressing output is not resolving it.
- Log AOT hit, interpreter fallback, macOS JIT fallback, unknown PC, and executable-write events from the first native boot.
- Every fallback incident records guest address, current function/scene, frequency, expected section, and mobile consequence.
- macOS JIT may be a diagnostic safety net only. A required path that works solely under JIT keeps the lowest affected goal unmet.
- The HOME Button Menu RSO and its seven entry points are an explicit subsystem. Replace it narrowly with the native menu; never globally disable dynamic-code checks.
- A Petari symbol is exact only when the DOL hash and range match. Wrong-region names are clues, not patch addresses.
- A function replacement preserves original semantics, carries provenance, and has a focused regression. Never patch a symptom without naming the underlying behavior.

## Pointer and EFB discipline — hard rules

- Keep Dolphin’s required `RMG` baseline: CPU EFB access enabled, deferred invalidation enabled, and arbitrary mipmap detection enabled until measured evidence justifies a compatible change.
- Instrument the first pointer frame. Record `GXPeekZ` count, coordinates, active channel, stall, returned depth, selected target, and frame interval.
- Prove correctness at 1× before increasing internal resolution.
- Classic Pointer is the bring-up baseline. Direct Touch is a separate product layer and receives its own context matrix.
- Pointer visibility is deliberate host/guest state. Clear or restore it explicitly across cutscenes, transitions, native menus, controller handoff, background/foreground, and runtime restart.
- A readback optimization stays default-off until it reproduces target/depth outcomes and improves recorded frame time.
- P2/Co-Star pointer work is disabled in the P1 baseline unless explicitly being tested; do not pay or claim its cost accidentally.

## Input and motion discipline — hard rules

- Generate a Wii Remote **with Nunchuk** profile. `Extension = None` or sideways-only output is invalid for Galaxy.
- Keep one normalized host state for touch, keyboard/mouse, and GameController input; merge by explicit rules and clear on ownership/lifecycle transitions.
- Spin is a dedicated host action. Prefer a virtual Wii Remote/Nunchuk shake pulse; otherwise patch one named query. Never globally steal A or B.
- Audit every swing, acceleration, gyro, IR, distance, roll, rumble, and speaker consumer. Do not assume Mario’s spin is the entire motion surface.
- Each mandatory tilt mechanic gets a tested stick-backed path before optional motion work begins.
- Optional `GCMotion` is capability-detected, manually activated only while needed, stopped on pause/background/disconnect, and never required.
- No touch, pointer, Spin, tilt, or controller value may remain logically held after native UI, interruption, or lifecycle transition.

## Audio, save, and lifecycle discipline — hard rules

- Main DSP audio and the Wii Remote speaker stream are separate evidence paths. Hearing music is not proof of speaker-cue routing.
- Verify guest timebase, producer cadence, Apple callback, queue depth, underruns, and pitch before changing buffers.
- Use disposable ignored saves/NAND. Hash and back up before/after a test that can write.
- A save write passes only after game-visible relaunch/load. A file timestamp or nonzero size is insufficient.
- Keep saves separate from imported game data; removing/reimporting the image must not silently remove or rewrite saves.
- Lifecycle tests include native menu, picker/share sheet, resign-active, background grace, audio interruption, renderer recreation, memory warning, controller disconnect, and clean shutdown.

## Unblocking ladder

When blocked, escalate through these in order. Journal each rung used.

1. **Read the first causal error and full context.** Use persistent runtime log, unified log, crash report, full build output, AOT/fallback trace, Wii boot trace, MEM2 allocation log, EFB profile, input trace, audio counters, and save log. Do not diagnose from the final cascade line.
2. **Check current project state.** Confirm disc/DOL/module hashes, title ID, Broadway/MEM2 guard, root revision, dependency graph, patch manifest, generated cache identity, active save/NAND, settings, running processes, and Simulator state.
3. **Reproduce the last known-good boundary.** Run the exact recorded command/artifact/settings. If it no longer passes, reopen the lowest regressed goal before experimenting farther ahead.
4. **Check SunPad.** Read the exact reference script, Apple host, input mixer, import flow, diagnostics, test, relevant patch, `KNOWN_ISSUES.md`, `TECH-DEBT.md`, `TESTING.md`, and `HANDOFF.md`. Reuse only the game-neutral mechanism.
5. **Check the exact Galaxy input and Petari.** Use the extracted manifest, DOL sections/disassembly, exact-region map, and named source paths to turn addresses into behavior. Do not apply a Korean address to another revision.
6. **Check the toolchain source.** Read DolRecomp analysis/backend/module code, ModernGekko runtime/module loader, RecompCore/Dolphin Wii boot, memory, DiscIO, DSP, GX/EFB, WPAD/KPAD, save, and Metal paths at the pinned revisions.
7. **Research one named question.** Search primary source, issue history, commits, and official Apple documentation. Research must answer a precise blocker and return to a bounded experiment.
8. **Reduce the problem.** Examples: toolchain check before disc; Wii mode before game code; homebrew DOL before Galaxy only when lawful; C backend before LLVM; AOT entry before title; title before pointer; Classic Pointer before Direct Touch; one EFB read before full UI; main audio before speaker mix; one save write before repeated termination; macOS before Simulator; iPad before iPhone; 1× before 2×–4×.
9. **Route around narrowly.** Replace one named SMC function, HOME-menu entry, input query, tilt consumer, speaker sink, or runtime defect. Preserve original semantics, add a regression, and keep the stable route explicit. Do not replace a subsystem with no-ops.
10. **Park and pivot.** If a blocker survives a working session, write a complete reproducible defect and take the largest step on the same or later workstream that does not falsify the lowest goal—for example, shell extraction while an EFB profile is blocked. Do not mark the blocked goal met.
11. **Stop and hand off only for a real decision/blocker.** Valid conditions: unusable/wrong/corrupt image; exact identity cannot be established; required source/tool is unavailable; an unavoidable executable path cannot run without prohibited dynamic code; continuing would destroy/leak protected input; physical-device action is required; a public rights/release decision is required; or a measured hardware limit leaves no semantics-preserving route. Ordinary compile errors, crashes, black screens, missing audio, bad pointer state, save defects, MEM2 faults, and performance regressions have an unblocking path.

## Testing rhythm

- **Per change:** run the smallest build/boot/gameplay/regression check relevant to the changed layer.
- **Per dependency change:** verify recursive pins and patch provenance; rerun Wii-mode guard, module generation, macOS boot, and the highest known-good gameplay smoke.
- **Per AOT/replacement change:** inspect SMC/coverage output; run the exact scene; compare dispatch counts and unknown PCs; verify mobile compatibility.
- **Per Wii-subsystem change:** run a narrow boot/service test plus the highest known-good gameplay boundary.
- **Per EFB change:** rerun the same pointer coordinate/scene at 1×; compare depth, target, read count, stall, and frame-time distribution.
- **Per input change:** run deterministic press/hold/release, simultaneous inputs, pointer, Spin, tilt, menu/lifecycle clear, controller connect/disconnect, and stuck-state tests.
- **Per audio change:** run music, voice, effects, Star Bit/speaker cue, transition, interruption, and pitch/underrun checks.
- **Per save change:** back up disposable state; write in game; exit/terminate as specified; relaunch and verify visible progress; compare hashes; never commit the fixture.
- **Per goal claim:** complete the exact evidence required by PRD Section 11 before changing `STATUS.md` to met.
- **Per session:** run the host regression suite and a boot/end-to-end smoke on the highest known-good target. End with the exact known-good command, revision, artifact/module/disc/save identity, settings, and next lowest step.
- **Per Simulator target:** verify all others are shut down; capture `xcrun simctl io <device> screenshot`; kill the app and shut the device down at session end.
- **Per candidate:** run the entire applicable matrix against the exact artifact. Do not combine evidence from earlier packages.
- **Input automation:** extend SunPad’s pipe/test-input machinery for Wii controls, IR coordinates, Spin pulses, and tilt axes. Use repeatable file-select/Gateway/Observatory routes. Rows marked hands-on remain hands-on.
- **Honesty rule:** configured, source-inspected, or unit-tested behavior is not a gameplay acceptance claim. Performance numbers come only from recorded measurements.

## Using the SunPad machinery — not just its appearance

- **Dependency control:** port exact locks, dirty-check refusal, recursive setup, revision verification, disabled push URLs, and coherent patch application. Produce a GalaxyPad lock and upstream-delta ledger.
- **Scripts:** port the shape of SunPad’s bootstrap, preparation, core/module builds, device deployment, macOS packaging, crash capture, repository checks, IPA/package audits, and deterministic input helpers; add Wii-mode, disc-identity, executable-inventory, and EFB-profile scripts.
- **AOT boundary:** preserve local image → exact DOL → ignored DolRecomp output → locally generated module → game-data-free source tree. No on-device compiler and no runtime-downloaded executable code.
- **Apple shell:** extract CAMetalLayer host, loading/error presentation, settings, normalized input, controller ownership, paths, lifecycle, import staging, diagnostics, and privacy before renaming.
- **Input mixer:** extend the state model to Wii Remote/Nunchuk/IR/Spin/tilt; do not force Wii input through the old GameCube layout.
- **Three-dot menu:** retain the accepted Display, Controls, Unstable Experiments, Game Data & Saves, Report a Problem, and diagnostics hierarchy; adapt labels/actions to Galaxy and replace the guest HOME overlay.
- **Game-data safety:** preserve security-scoped picker handling, validation, unique staging, atomic activation, rollback, real removal, and save separation. Add large-Wii-image storage preflight and exact DOL/module matching.
- **Logging:** wire boot, Wii mode, MEM2, dispatch, EFB, pointer, Spin/tilt, audio/speaker, save, and lifecycle breadcrumbs before the port becomes unstable.
- **Experimental framework:** every risky EFB optimization, renderer change, timing change, Direct Touch heuristic, motion mode, aspect fill, or performance mode is default-off, has a logged identity, and never silently replaces the stable baseline.
- **Release safety:** keep source/package audits executable throughout development. Passing them once at the end is insufficient if the build graph or module packaging changes.
- **Branding:** create original GalaxyPad icons with provenance; never derive them from game art or extracted assets.

## Session start checklist

1. Read `docs/STATUS.md`, the last `JOURNAL.md` entry, and the relevant inventory for the lowest unmet goal.
2. Run `git status`; preserve unknown work. Record the root revision.
3. Run `xcrun simctl list devices booted`; shut down strays. Kill GalaxyPad, ModernGekko, launcher, runtime, and test processes.
4. Confirm the original image and active staged copy hashes when relevant. Confirm exact DOL/module identity.
5. Verify `ref/sunpad`, selected ModernGekko/RecompCore/DolRecomp/template, and Petari revisions against the GalaxyPad lock; check patches target the intended commits.
6. Run or verify the Broadway/MEM2 guard before a Wii build.
7. Confirm the active save/NAND/test fixture and back it up if the session can write it.
8. Confirm stable settings: target, backend, EFB scale, aspect, pointer mode, Spin route, tilt route, audio/speaker mode, and fallback policy.
9. State the session goal, hypothesis, and smallest next step in `JOURNAL.md`.
10. Enter the loop.

## Session end checklist

1. Kill the game/runtime and shut down every Simulator.
2. Run the regression suite and highest known-good smoke test, or state exactly why one cannot run.
3. Record root/dependency revisions, disc/DOL/module/build identity, evidence paths, settings/mode identity, active save/NAND hashes, open processes (none expected), and remaining defect.
4. Update `STATUS.md` and every changed technical inventory.
5. Remove incomplete import staging directories only after verifying they are not the original input or required evidence.
6. Run repository safety checks before any commit.
7. Leave one unambiguous next step for the lowest unmet goal.
