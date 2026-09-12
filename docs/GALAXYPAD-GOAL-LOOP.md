# GalaxyPad goal-based loop

## September 13: Pull Star fixed in Simulator; performance baseline corrected

Disabled EFB depth access caused the dome target failure. The source now enables
real EFB reads. Simulator hand-cursor acquisition, held-A pull, galaxy selection
and entry into Loopdeeloop Galaxy pass on host
`0baf09083c5accb108f32a77b95bc4ae64b4ab7cb2c57a25459b79b60825dd41`.
Physical update is installed and launch-verified; all 33 protected files remained
byte-identical. Signed host is
`13b32e380581253ca0da7d076ce18c7eb0a54d2e136dec83a449df33089cadc8`.
Xbox/gameplay acceptance still needs user confirmation. Menu event and mixed
pointer ownership fixes are included in this fresh host.

Correct-depth heavy-scene logging-off samples are 45.0–49.0 frame events/s over
60 seconds. Earlier 56–60 results below used disabled depth and are historical
relative comparisons, not playable-config acceptance. Audio/tails need a new
separate run. Next: measure cache misses and EFB service cost, preserve true depth,
then test a small justified change against this corrected control. Build commands,
exact hashes and private evidence paths are in the
[current handoff](PERFORMANCE-2026-09-12.md#september-13-pull-star-cause-reproduced-and-corrected).
Release remains NO-GO. Previous main checkpoint is `892ff71e208b07d3d790c697b83e63678361d5f4`.

## 2026-09-12 — installed performance/audio candidate; physical feedback and Start fix

Current summary: [performance and hardware handoff](PERFORMANCE-2026-09-12.md).
Logging-off matched-route gain is roughly 44→58 frame events/s. Separate diagnostic
control recorded 157 underruns; combined candidate recorded zero. Actual mixer PCM
has no sustained silence in its 60–120 second gameplay interval; listening and
physical audio acceptance remain open. These measurements must not be conflated.

Installed signed physical host:
`85d84c887cae4b3736b5304cbf757a0543d74e99b4e418e3618184c73b00d0ad`.
Signed nested module:
`aa7d6b6f38d0fae938dcc83509672e6d5ef822567eb0d5d005e5547b3c1e55d2`.
Evidence: `generated/runtime/ipad-iteration-1/physical-dual-core-audio-tempo-20260912/`.
In-place install and process inventory establish launch; the game save readback is
identical. Six configuration/history/preference files changed while the user
started playing; do not claim complete snapshot equality or restore older data.
Selected render scale became 2×; active physical resolution remains unverified.

User reports stable, promising gameplay with remaining slowdowns and intermittent
Xbox Start/Menu. New source fix uses event-time button state; exact old source
fails the queued quick-tap regression and current source passes. Evidence:
`generated/experiments/controller-menu-event-20260912/result.json`.
The installed hash above predates this follow-up. Next: validate the new controller
candidate, merge the documented work, then rebuild/retest before another hardware
promotion. Confirm physical Xbox behavior directly with the user. Compare known
active 1× and 2× physical settings before attributing slowdowns or extrapolating
to iPhone. Four-minute Simulator capture still needs review and a matched control.

The app runs native AOT ARM64 game code with a Dolphin-derived Wii runtime and
interpreter fallbacks; it is not emulator-free. No release acceptance is claimed.

## 2026-09-12 — repeated dual-core gain and real-game tempo continuity

Dual-core repeat logging-off HUD over120s:54.5,55.5,58,60,58,57,59,59,59,57.2,
60,59.1,58.2. Fresh unchangedcontrol60s:43,41.8,44,45,41.8,46.4,44.5. Two
candidate windows support the threading bottleneck fix; continuous frame tails
are not established by sparse HUD. Summary: generated/runtime/ipad-iteration-1/
dual-core-comparison-20260912/summary.json. Private candidate retained for gates.
Separate dual-core original-audio diagnostic:21new underruns/57.999946s,
97.1365%nonzero output,13946real enqueues. This improves supply but still fails
no-recurring-underrun target. Three-dot runtime/inputblock and nativepause/resume
checked through Simulator UI with counters; initial idle-disconnect dialog phase
explicitly excluded. Evidence: dual-core-lifecycle-20260912/review.json.

Full isolated tempo-v8 core rebuild passes1550compiler-policy entries,18core
Mixer layout consumers plushostconsumer,platform/signatureand45controlhashes.
Host bb8b49859d1573122ce5bcb8c001b7bc91f7827c47a838cb66c2c802a8aabba9.
Single-core logging-off audio candidate HUD41,42,44,44.6,43.6,45.5,45.5; no
performance win claimed. Actual separatediagnostic58.099106s:0newunderruns,
0newfull/backlogdrops,0shortcallbacks,2788864/2788864nonzero outputframes,
10580real128-frame enqueues (~23309inputframes/s). Evidence:
generated/runtime/ipad-iteration-1/audio-tempo-v8-diagnostic-20260912/candidate/audio-summary.json.
Cumulative26underruns precededthiswindow;321full-drop events also predatedit,
including200duringnavigation. Newdropunit is rejected8-frameinputcalls whereas
oldFIFOeventsrepresented128-framegranules; do notcomparethosecounts directly.
No resets/suppression. Soundquality/startup/pause andphysicalacceptance remain.

Combined private dual-core+tempo-v8 host built/signed with matchedMixerheaders:
ef9898603ebf4eddf7fb01f6406f862aa20e03ad808025cf48078b50bcc69953,
generated/build/ios-simulator-dual-core-audio-tempo-20260912/GalaxyPad.app.
Nowunderlogging-off120sroute, followedbyactualaudioandlifecyclegates. OldPGOmodule
90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f remainsunchanged.
No physicalinstall. Physicalrecipeaudit foundseparateIOSsignedcontrolmodule919b…;
Simulator90e… isnotdevice-compatible. DevicefullaudioABI rebuildpreparedonly.


## 2026-09-12 — dual-core gain under repeat; audio tempo v8 source gate passed

The isolated session-only MAIN_CPU_THREAD=true host produced logging-off HUD
56.4,55.5,58.0,58.0,58.0,59.1,59.1 FPS over60s. All8scene/window images were
directly verified as active121-star Observatory gameplay. Live executable SHA
ad0add304f633bacae5bb97565038417208c268a31cec8e28efa19d025a17d86 and separate CPU
and Video threads confirmed after acceptance window. Original module remains
90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f. This is a
promising provisional gain, not sustained60FPS or physical acceptance. Fresh
control and120srepeat are being run without build contention. Sparse HUD does
not establish frame tails, speed or audio. Evidence and exact launch manifests:
generated/runtime/ipad-iteration-1/dual-core-comparison-20260912/.

Audio tempo copied integration v8 passes30 exact48k Mixer cases plus sanitizers,
including slow67-100%production, bursts, steps and actual pause/restore paths.
Measured oldest sample age max118.625ms; unavailable windows zero in supported
producing cases,234 during real1sstarvation. Real enqueue counters remain real.
These are offline tests, not realgame acceptance. Full core+host dependents must
rebuild because Mixer layout changed. Frozen source under
generated/experiments/audio-tempo-integration-v8-20260912/; Mixer.cpp SHA
102a876d8efe784e2c37c4cadae46eadc4479f0776797a8388d16d31215565e1.
First configure stopped at a false source-set gate: duplicate sources collapsed
1550target entries to1539. The strict gate is repaired and1550commands match
control, with7regression checks. Fresh recipe ready under
generated/build/ios-simulator-audio-tempo-isolated-retry-20260912/; compilation
waits for logging-off windows. Normal startup DMA32k is supported; any other
DMA rate latches candidate failure and must be checked in actual diagnostics.
No120msbuffer increase, physical install or release selected.


## 2026-09-12 — actual audio replay rejection; tempo prototype underway

The user reiterated fixing audio underruns. Actual matched-scene diagnostic
intervals (not FPS acceptance) reject simple replay: candidate236 underruns over
~53.2s (4.436/s), control184 over~58.1s (3.167/s), approximately2359guestframes each.
Candidate nonzero output100%; control69.1624%. Producer23672.8/21665.2samples/s
tracks emulated44.342/40.602FPS, so sustained CPU slowdown explains the supply
shortfall. Both diagnostic image sets were verified in the same gameplay scene.
No counter suppression, physical promotion or audio-quality acceptance.
Exact logs, counters, hashes, scene reviews and decisions:
generated/runtime/ipad-iteration-1/audio-gap-fill-diagnostic-20260912/comparison-summary.json.
Logging-off audio candidate HUD42,43,45.5,46,45.5,45,44.6; no improvement selected.

A new isolated pitch-preserving tempo prototype is being tested in
experiments/audio-tempo/AudioTempo.h with tests/audio-tempo.cpp and
tests/test-audio-tempo.py. It has not been integrated into the app. Current work
covers actual32k→48k callback sizes,67%production/bursts, pitch/stereo/transients,
startup/stall recovery and measured source wall-age within120ms, not merely
input-frame capacity. Tests exposed spurious unity re-entry and stale recovery;
those are being corrected before integration. Reset must be quiescent; live
pause handling needs consumer-only flush. No new audio-buffer increase accepted.
If prototype passes, changing Mixer layout requires a complete isolated core
and dependent allocation rebuild, plus legacy-unity-output and realgame gates.

CPU scheduling audit excludes E-core starvation in the observed interval:
CPUthread99.27% walltime; at least97.44% execution on Pcores. Whole-chunk restrict
is unsafe through callback aliases. Evidence: generated/cpu-scheduling-audit-20260912/
and generated/cpu-state-alias-audit-20260912/. No priority/alias hack selected.

## 2026-09-12 — O3 rejected; audio gap-fill candidate running

O3+oldPGO module aa8760b88656aa05f9f3e0c6c6becaace47f3b2802ad5193682413d85a622d11
shows no gain versus unchanged O2+oldPGO. All14candidate/immediate-control images
were directly reviewed: same scene, no dialogs/crash. OCR means44.429/45.286;
manual review differs in three small candidate HUD readings, retained separately.
Either reading rejects a gain. Exact records/limits:
generated/runtime/ipad-iteration-1/o3-old-pgo-comparison-20260912/summary.json.
Earlier delayed control windows invalidated by guest idle disconnect are excluded.
Capture now supports --provisional immediately after launch, with mandatory later
visual review; stale scene checks remain. Do not insert model/build delays between
route and capture. No capture is accepted based solely on route success.

M3 tuning rejected before fullbuild: actual Apple backend emitted identical
native and linked instructions for both hotTUs. Evidence:
generated/target-tuning-source-audit-20260912/two-tu-screen/summary.json.

Next actual audio source candidate restores the configured generic gap filler
while Running; Apple DMA earlyreturn had bypassed AudioFillGaps. Offline exact
FIFO tests at44/60 production removed recurring~122ms zero-output spans; fullspeed,
disabledgapfill, stalls and pause/resume checks pass O2/ASan/UBSan. Musical replay
quality and runtime underruns remain unverified; do not claim sound accepted.
Host4e8d29281a536d35e9960e0a4adccbce937fef2f1c29e9903ec177842468bce8:
generated/build/ios-simulator-audio-gap-fill-app-20260912/GalaxyPad.app.
Normal controlmodule90e24 remains unchanged. OneMixerobject selected in linkmap;
baseline relink reproduced b3ed exactly, signatures pass. Patch/tests/buildrecipe:
generated/experiments/audio-gap-fill-20260912/. Immediate route/capture:
generated/runtime/ipad-iteration-1/audio-gap-fill-comparison-20260912/candidate.
No physical promotion. Next: evaluate logging-offFPS, then separate actualaudio
output/underrun diagnostics against unchangedcontrol; reject regressions honestly.

## 2026-09-12 — fresh LUT rejection; O3 with validated PGO building

Fresh LUT run stayed in gameplay:43.6,44.6,43.6,44.5,43,43.7,44 HUD FPS,
mean43.857 versus controls44.614/44.786. Reject as performancecandidate;
memoryreduction alone does not meet the selection rule. Exact retained evidence:
generated/runtime/ipad-iteration-1/coarse-lut-comparison-20260912/summary.json.

Next build command: python3 scripts/prepare-o3-old-pgo-experiment.py --output
generated/build/ios-simulator-o3-old-pgo-20260912 --execute --jobs 4.
This changes only final frontendO2→O3 while retaining validatedoldPGO, strictFP,
normalABI and unchangedThinLTOlinkpolicy. PreviousO3trialwasunprofiledand cannot
answerthiscomparison. Recipe checks source/input stamps, compile/linkparity,
profilediagnostics and module-table parity. Build log:
generated/runtime/ipad-iteration-1/o3-old-pgo-build-20260912.log.
Matched freshcontrol route: generated/runtime/ipad-iteration-1/o3-old-pgo-comparison-20260912/control.
Wait for compilers/linkers to end before timing. No candidate selected/deployed.

## 2026-09-12 — two CPU source screens rejected

MEM1-first precedence-preserving helper passed1.2M mapping cases plus callback,
overlap, journal and reservation checks at O2 and ASan/UBSan. Exact old-PGO
func805170A0 codegen grew23467→24116 instructions, addingregisterpreservation for
onlyoneinstruction saved on its firstMEM1 path. Reject beforefullbuild.
Evidence: generated/experiments/mem1-first-precedence-20260912/.

Shared ps_madds0/1 multiplier rounding passed960,016 completeCPU/host-FPflag cases.
Fair separate-TU ThinLTO+oldPGO microcomparison regressed madds0 +12.56%, madds1
+10.13%, losing everypair. Reject beforefullmodulelink; profile-free microgain
is superseded. Evidence: generated/shared-ps-rounding-20260912-final/policy-cost-summary.json.
These source/codegen/cost screens are not game FPS acceptance.

The invalid LUT-window Wii Remote disconnect OSD maps to guest HCI_CMD_DISCONNECT;
neutral reports continue and A activates the emulated remote. No hostkeepalive or
automaticinput hack is justified. Sourceaudit: generated/runtime/ipad-iteration-1/coarse-lut-comparison-20260912/idle-disconnect-source-audit.md.
Fresh LUT repeat is underway after external compiler jobs ended; no gainselected.

## 2026-09-12 — coarse LUT remains unselected; guest Back verified

Coarse LUT host3c63d8085e42fb45af142b3d7d6194f01ecc433ae3c5d1d9ad2cacceb9724ec8
with unchanged old PGO launched the correct scene. First window became invalid
when the emulated Wii Remote disconnected and a dialog reported60FPS. This is
not a gain. After A reconnect, pointer(0.5,0.45),2s aim then2s A selected Back and
returned to gameplay, confirming the original guest menu exit route.
Updated controller help source explains Back+A; native Xbox toggle remains separate.

Repeat HUD45,45.5,44,41.8,45,32.7,33.6; last dips coincided with CPU allocation
88.6/88.5% and numerous external compiler jobs appearing in host-after inventory.
Candidate remains unselected pending comparable host conditions. RSS about700864KiB
is lower than the roughly763000KiB control, but no FPS gain is established.
Exact commands, hashes, images, manifests and decision:
generated/runtime/ipad-iteration-1/coarse-lut-comparison-20260912/summary.json.
Next prepared source screens: safe MEM1-first address selection preserving live
metadata and MEM2 overlap precedence; shared exact multiplier rounding in
ps_madds0/1. No unsafe fixed-map contract or altered FP behavior accepted.

## 2026-09-12 — dispatch boundary measured and rejected

Both preserve_none variants completed the fixed logging-off Observatory window.
V1 mean43.043 HUD FPS; corrected inline v2 mean43.586; repeated unchanged control
44.786. Reject both for no improvement. V2 final linked assembly eliminated the
normal ABI spill bridge, but that source change did not improve this scene.
Exact seven-point readings, manifests and hashes:
generated/runtime/ipad-iteration-1/preserve-none-comparison-20260912/summary.json.
V2 module SHA42380a4cdc0f03458e6789fdbced98bce1c1395d9cdbe79a6194ccfa62e0e2fb;
host90fdd93b7f0f66d67ae2cb6f75c9839b4336d1675403b2b1870352b276a55546.
A separate post-window sample is diagnostic only. Sparse HUD windows do not prove
frame tails, audio or physical controls; no physical deployment.

Next small source candidate: validated32-byte eligibility lookup buckets reduce
88MiB to11MiB; generic unaligned modules retain4-byte fallback. Actual-source
ASan/UBSan fixture passed81scenarios/423,360address and invalidation comparisons.
Copied source/patch/buildrecipe: generated/coarse-chunk-lut-20260912-final/.
Build command: python3 generated/coarse-chunk-lut-20260912-final/build-host.py.
Uses normal ABI and unchanged old PGO independently of the rejected ABI variants.

## 2026-09-12 — measured PGO rejection; dispatch boundary next

Logging-off, visually verified 121-star Observatory route, scale 1, aspect 0,
same pause-toggle host b3edb1647b350bc35256f8fba8c2e63878b842b7b5111b8df0864c7eb2018d43:
old PGO control averaged 44.614 HUD FPS (44–45.5); fresh heavy-profile candidate
averaged 43.671 (42.7–44.6). Reject the fresh profile; retain control module
90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f.
Exact observations/hashes: generated/runtime/ipad-iteration-1/heavy-profile-comparison-20260912/summary.json.
These are seven sparse HUD observations over 60 seconds, not continuous frame-tail
or timed audio acceptance.

Extended TSP module 01c45a1be01c7b603f933c48bb563c52497a448f081c403fc2dd8572638cbb64
had HUD 29.1,20,30.9,45,45,45.5,44 with matching CPU allocation dips and concurrent
external builds/emulators. First window inconclusive; unselected pending repeat.
Evidence: generated/runtime/ipad-iteration-1/ext-tsp-comparison-20260912/candidate.

Next source candidate carries preserve_none through the optional versioned module
boundary into Run, retaining the normal descriptor fallback. Build succeeded;
Simulator comparison starts at generated/runtime/ipad-iteration-1/preserve-none-comparison-20260912/candidate.
Build command: bash generated/experiments/preserve-none-boundary-20260912/build-candidate.sh.
Host SHA-256: 90fdd93b7f0f66d67ae2cb6f75c9839b4336d1675403b2b1870352b276a55546.
No physical install or acceptance yet.

Continuous profile output must include %c in LLVM_PROFILE_FILE; overriding the
embedded filename without it disabled live updates. The harness now rejects this
invalid training configuration. Explicit flushed interval above remains valid.
Touch guest Start+ repeat did not close the original guest menu in a separate
logical input run; B also did not close it. This remains open, distinct from the
software-tested native Xbox Menu/Options toggle fix. Evidence: heavy-profile-comparison-20260912/candidate/plus-*.png and plus-input-diagnostic.log.

## 2026-09-12 — renewed Simulator performance loop

Latest user instructions supersede the old single-Simulator and single-subagent
limits: multiple Simulators are allowed, with multiple secondary-account Astra
high agents for independent source work. Primary owns candidate selection/builds
and the current Simulator route. Other apps/data are preserved. Work continues;
no performance success or physical promotion is claimed.

New executable loop: `scripts/galaxypad-simulator-comparison-loop.py`.
For each one-change candidate, run `launch APP MODULE FRESH_OUTPUT`, visually
verify `scene.png` (Luigi,121 stars,2324 bits,Observatory map platform), repair
navigation if needed, then `capture OUTPUT --scene-verified --seconds 60`.
Repeat unchanged control/candidate under comparable host conditions, record the
decision, and move to the next measured hypothesis. The loop checks live host and
module hashes, refuses instrumented modules, verifies scale1/aspect0/loggingNO,
records concurrent Simulator/host inventory and sparse HUD/process observations.
The route stops before sampling and backs up Simulator Wii state before reseeding.
It does not provide continuous frame-tail, speed or timed audio proof; those
remaining acceptance limits must not be inferred from sparse screenshots.

Current PGO comparison uses identical host
`b3edb1647b350bc35256f8fba8c2e63878b842b7b5111b8df0864c7eb2018d43`,
control module `90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f`,
and fresh candidate `54b117d28c18e27241c3241797e42505d00aab3492863db1b147f7773e70d1ec`
at `generated/build/ios-simulator-heavy-pgo-20260912/gRMGE01_recomp.dylib`.
Evidence: `generated/runtime/ipad-iteration-1/heavy-profile-comparison-20260912/`.
Matched windows completed: fresh profile rejected; see newer result above.

Heavy profile capture was repaired: continuous flags did not produce live file
updates. The first raw file had total count1. An explicit diagnostic LLDB call,
`expression -- ((int (*)())(void*)__llvm_profile_write_file)()`, appends a complete
32,388,648-byte record. Extracting the last record before/after a60-second
stationary Observatory interval, validating identical schemas/nonnegative deltas,
and merging only those deltas produced profile
`f46ec57792e9714c694d33998153addc88d6d90d6a015e5796df501bf5f0cd9c`.
All32,551 functions match;5,562 have positive interval counts. Files, debugger
commands and timing: `heavy-pgo-training-20260912/retry/flushed-window/` under the
same evidence root. Debugger/training observations are not FPS acceptance.
The build uses `GALAXYPAD_PGO_PROFILE=$PWD/generated/runtime/ipad-iteration-1/heavy-pgo-training-20260912/retry/flushed-window/observatory.profdata`
and `GALAXYPAD_SIMULATOR_MODULE_BUILD=$PWD/generated/build/ios-simulator-heavy-pgo-20260912`
with `GALAXYPAD_BUILD_JOBS=4 bash scripts/build-ios-simulator-fresh-module.sh`.
Build passed; no hash mismatch, only existing comment/unprofiled integer-file warnings.

Parallel source decisions: four-stage vertex dispatch unroll rejected after819
ASan/UBSan parity cases and16 slower paired timing rounds (+2.9–13.7%). Evidence
`generated/vertex-stage-unroll-20260912-screen/`. Simple per-chunk `preserve_none`
ABI also rejected: wrapper preservation offsets the savings;46,080 O2/UBSan
state/memory/callback cases pass but complete boundary code grows. Evidence
`generated/runtime/ipad-iteration-1/audio-generated-source-audit-20260912/REPORT.md`.
A versioned optional dispatch ABI reaching the actual host Run loop is now being
screened separately, with canonical ABI unchanged. No speculative audio-buffer
increase: existing audio sample mostly waits and does not establish mixer cost
as the CPU bottleneck. Zero short callbacks is not callback deadline proof.

## 2026-09-12 — Menu resume regression reproduced and fixed in Simulator

The production controller adapter previously stopped reading input whenever native
pause blocked gameplay. The second Menu press therefore could not resume. It now
observes Menu/Options release and press while the native pause panel is visible,
and toggles that panel; unrelated dialogs still block the shortcut. Pause re-arm
requires Menu/Options release, not perfectly centered sticks. Touch Start + remains
the guest Wii Plus input pending a separate live-game repeat-press check.

The isolated UIKit controller test reproduced the old gate failure, then passed
with the corrected adapter. Evidence:
`generated/runtime/ipad-iteration-1/pause-toggle-20260912/before-console.log`
(`FAIL: second Menu press resumes while gameplay is blocked`) and
`after-console.log` (`GALAXYPAD_UI_TEST_PASS`). These use software controller
snapshots on the sole existing Simulator, not physical Xbox acceptance. The added
held-stick regression also passes in `after-held-stick-console.log`; the final
host gameplay comparison remains in progress. Fresh Simulator host:
`generated/build/ios-simulator-pause-toggle-app/GalaxyPad.app/GalaxyPad`, SHA-256
`b3edb1647b350bc35256f8fba8c2e63878b842b7b5111b8df0864c7eb2018d43`.
Built with `cmake --build generated/build/ios-simulator-pause-toggle-app -j 4`,
then `codesign --force --sign -` on that app and strict deep verification passed.
Test app built with `bash tests/build-mobile-ui.sh`; executable SHA-256
`0cae6f819cb9c6dc9d8b58eb1e03b86d22f73ba032adcfa426c7fe66edc7f1c1`.

The module build script also now clears cached C and shared-linker profile flags
when switching back to unprofiled mode. A real CMake cache probe reproduced stale
flags and verified the fix; see `pgo-mode-reset-20260912/result.txt` under the same
runtime evidence root. This is build correctness, not an FPS claim.

The first Observatory training capture is rejected for profile generation: its
counter-before copy occurred after termination, so it cannot isolate the verified
60-second scene from lengthy title/navigation training. Preserve
`heavy-pgo-training-20260912/observatory-35979.profraw` as diagnostic evidence only.
Next: capture before/train/stop/after in one sequence after visual scene verification,
validate counter deltas, then build an isolated profile-use module. The unchanged
PGO control remains selected; physical app and saves are untouched. Goal stays active.

## Existing Simulator test resumed — 2026-09-12

Reused the sole booted Simulator without changing MeleePad. Verified the actual
121-star Observatory, reproduced low-40 FPS, tested the handoff guard and rejected
the unprofiled module (37–38 FPS versus 44–45.5 with PGO). The canonical harness
now rejects the old zero-star seed and uses the verified advanced save. See the
latest performance-loop/resume entries for exact evidence and next heavy-scene
PGO training hypothesis. Goal active; no physical promotion.

## 2026-09-12 scene-identity correction

The default unattended seed `717f7fb3…e36c` is the old zero-star save,
not the 121-star save. The resumed logging-off screenshot shows Star Festival.
Prior unattended results using that seed are not late-game acceptance.
See the newest entry in `IPAD-PERFORMANCE-LOOP-2026-09-11.md` for artifacts,
the reproduced hidden-touch pointer-handoff fix, and the pending advanced-scene
control gate. The canonical PGO module and physical installation are preserved.

Operating loop for the autonomous build of GalaxyPad. The requirements live in
`docs/GALAXYPAD-PRD.md`; this document is how you run. Written 4 Sep 2026.

## Self-audit follow-up — 2026-09-12

The performance issue remains unresolved. The current control still reaches the
seeded late-game scene at about 56.4 emulator FPS with logging off, and its
sample remains dominated by `StaticRecompCore::Run` and `chassis_dispatch`.
The previous work window did not produce a promoted performance change; it
spent too much time on rejected micro-candidates and diagnostics while the
host was carrying unrelated CPU-heavy work.

The host audit found and terminated only twelve stale read-only MeleePad
`afcclient` transfers that had been consuming about 92–99% CPU each. QEMU and
system services remain active, so the new control is still qualified. The
physical iPad and unrelated Simulators were not touched.

The current Simulator module is an unprofiled `-O2`/ThinLTO build. The
historical PGO profile and active-module marker are absent, and the old iOS
PGO builder points at those missing artifacts. The fresh Simulator module
builder now accepts an optional `GALAXYPAD_PGO_PROFILE` without changing its
default. The next valid iteration is therefore current-input instrumentation
and representative PGO training on a quiet, roomier host, followed by one
matched candidate/control run. Until that exists, another source micro-edit is
not an evidence-led step.

## Active goal loop — 2026-09-11

The active Codex goal is to resolve the physical-iPad slowdown and related
pause/controller issues without disturbing the advanced save or app data. The
loop is intentionally gated:

1. Visually resume the 121-star Observatory save and hold one fixed heavy scene.
2. Confirm `runtime_paused=0 menu=0` in the lifecycle log and pass
   `--active-scene-confirmed` to `scripts/galaxypad-performance-loop.sh`.
3. Capture one unsampled logging-off interval and one bounded CPU Profiler trace.
4. Select one source-level candidate only after the profile and an actual-policy
   correctness/cost gate agree; rebuild and reinstall privately.
5. Repeat the same scene, retaining process identity, VI/audio evidence, and
   save hash. Keep a candidate only if performance improves without lifecycle,
   input, audio, or correctness regression.

The first profile was rejected because the app was paused behind the three-dot
menu. The quiet native-burst differential gate passes 5,376 cases. Its
actual-policy cost screen now compiles against the available iPhoneOS device
flags: the private candidate object is 7,216 bytes of text versus 6,672 for
control (+8.3%), so this lane is rejected on the source-level cost gate. No
module rebuild or FPS claim follows from that result. Astra Medium was assigned
through the secondary account for the heavy computer-use audit and confirmed
the paused state.

The paused-state gate was later cleared by a physical “Back to Game” tap. The
accepted active-scene profile captured 34,090 CPU/GPU-thread samples on the
121-star Observatory platform and identified `Normal_ReadIndex<unsigned short,
short, 1u>` among the measured hot stacks. The isolated reader reduction was
later audited out because the staged archive member was byte-identical to
control. The next whole-normalization candidate passed 261,120 complete-routine
comparisons and 69,120 callback cases, but its unattended Simulator samples
matched control and one reverse-order replay failed before renderer readiness.
It is parked; it was never installed on the physical iPad.

The current private device build adds the iPad display correction and menu
guard: absent or invalid aspect preferences resolve to 4:3 (`aspect_ratio_mode=0`),
while 16:9 remains an explicit Display choice. The three-dot UIMenu is input
blocking but runtime-neutral; its host gate cannot request `Runtime::Pause`,
and dismissal clears the gate synchronously. The top Pause and three-dot
controls are both lowered by 8 points. The exact bundle was installed in
place without changing the app database UUID or save data; physical menu,
controller, and touch confirmation remains the next required check.

The same device build additionally defaults touch controls to hide when an
extended controller connects and to reappear when it disconnects, with a
persistent visibility breadcrumb. It raises the right-stick pointer response
to 1.2×. The exact physical console sequence now proves the visibility
contract (`hidden=0` → `hidden=1` → `hidden=0`) for the tested Xbox controller;
the raw excerpt is retained at
`generated/runtime/ipad-iteration-1/controller-hotplug-console-20260911.log`.
These are bounded input changes; the performance loop remains separate and
must continue to use logging-off matched scenes plus opt-in profiles.

## Menu-inclusive diagnostic recheck — 2026-09-11

The canonical Simulator host was rebuilt so opt-in frame windows no longer
discard the runtime interval while the three-dot menu is visible. The logger
records `native_menu`, `ui_blocked`, and `pause_requested`; normal gameplay
still starts with frame logging off. Focused settings and UIKit overlay tests
pass, and the rebuilt app completed the seeded route with the unchanged save
seed hash. Eighteen qualified windows averaged 59.109 frame events/s, with a
49.058 lowest window and a late 98.728 ms guest DMA producer gap. Output audio
had zero short callbacks, but DMA underruns rose 1 → 14; unrelated QEMU and
`afcclient` load invalidates this as a clean performance comparison. No source
performance candidate passed, the canonical module remains selected, and the
physical iPad remains untouched.

## Self-audit and reorientation — 2026-09-11

The performance problem is not resolved. The work completed in this loop was
diagnostic and preventative rather than a speed fix: audio starvation was
shown to follow guest-producer gaps, the CPU sample consistently led into
`StaticRecompCore::Run` and `chassis_dispatch`, and EFB readback was absent.
The host was also carrying an Android emulator, file-transfer workers, and
other CPU-heavy processes, so the Simulator numbers were qualified rather
than clean device-equivalent acceptance.

Five bounded candidates were rejected for no repeatable runtime benefit,
regression, or unsafe boundary behavior. A fresh generated-module `-O3`
candidate reduced module text by 371,864 bytes versus the current `-O2`
module, but its matched route was 56.730 versus 56.987 frame events/sec,
with equal phase-trace DMA underruns (70) and backlog drops (6). Its average
process CPU was lower (73.247% versus 75.615%), but the frame/audio result was
not a material or clean win; it was not promoted.

The loop is reoriented around causal measurement before another source edit:
obtain a clean matched baseline when unrelated host load is absent, identify
exclusive cost in the exact retained heavy scene, and require a repeatable
frame-pacing and audio improvement. If that cannot be done in the Simulator,
the remaining blocker is the missing unattended physical-iPad input/profile
path, not a reason to keep generating micro-optimizations.

## Reoriented unattended loop — 2026-09-11

The physical-only loop is not suitable when the operator is away. QuickTime is
an observation/recording surface, and CoreDevice exposes no supported touch or
gamepad injection. XCUITest is the supported physical-tap alternative, but
this checkout has no signed UI-test runner; it also cannot prove a simultaneous
title-screen A+B hold or emulate an Xbox controller. The active iteration lane
therefore moves to the iPad Simulator, with the physical iPad reserved for
final performance and input acceptance.

The unattended lane is `scripts/galaxypad-unattended-simulator-loop.sh`. It
requires a built Simulator app, fresh Simulator module, extracted local game
root and disc path, and the private save seed. It boots one dedicated
Simulator, refuses by default to disturb a different already-booted Simulator,
and can preserve one explicitly allowed unrelated Simulator, installs
the app, seeds only `Library/Application Support/GalaxyPad/Wii`, launches with
the read-only host game/module paths, and leaves persistent frame logging off.
It then drives the observed route autonomously: a 30-second simultaneous A+B
hold (the title transition is unusually slow on this host), pointer settle
plus A on file 1, pointer settle plus A on Play, 30 bounded A pulses through
the opening story, a late-game screenshot, and a bounded host `sample` CPU
capture. Every candidate gets a new ignored output directory; no physical app
container or save is touched. A failed run also writes `failure-state.log`
with the exit status, booted devices, launchd state, PID state, and console
tail for the next iteration.

The first five-second route attempt was rejected as a navigation result, not
an input result: the log showed host acceptance, device consumption, and Wii
Remote A+B (`3072`) but the title remained visible. A clean 30-second hold
then reached file select; the same unattended pointer actions reached Play and
the late-game plaza at
`generated/runtime/ipad-iteration-1/simulator-reorientation-unattended-plaza-manual.png`
with frame logging off. The repeatable script output
`generated/runtime/ipad-iteration-1/simulator-reorientation-unattended-30s-plaza/`
contains the corresponding late-scene screenshot, input-route log, and CPU
profile; its on-screen counter read 51.0 FPS with frame logging off. The
earlier `...unattended-plaza/` output remains as the intentionally retained
failed five-second route-timing pass.

For the next diagnostic rung, the same script accepts
`GALAXYPAD_SIMULATOR_EFB_TRACE=/absolute/output/efb-trace.csv`. That opt-in
trace records EFB read coordinates, guest PC/LR, and elapsed time; it is kept
off for normal candidate comparisons because per-read file output can perturb
timing. An EFB-focused candidate must use this trace only to confirm
whether the observed `PeekEFBDepth` waits are pointer work or broader guest
render work before any semantics-changing EFB edit is attempted.

Simulator evidence is for deterministic correctness, scene reachability, and
candidate-to-candidate CPU attribution—not an iPad FPS claim. A candidate can
advance to physical installation only after the same saved scene, lifecycle,
audio, and save invariants pass in the Simulator; the physical iPad then gets
one in-place install and a separate acceptance check.

The unattended iteration rule is now explicit: select one measured shared
execution/dispatch hypothesis, run its offline correctness and cost gates,
build one private Simulator module, and run the exact save/input route against
control. A failed build, crash, missing readiness signal, no-op profile, or
regression parks the candidate and leaves the physical baseline unchanged. If
an unrelated Simulator must remain booted, set
`GALAXYPAD_ALLOW_OTHER_SIMULATORS=1`; the output records that host-pressure
qualification. Do not install a candidate on the iPad until this lane passes.

R915 is the first candidate to clear that unattended comparison: it specializes
the common three-component indexed position reader and two-component texture
reader while preserving the original branches for all other formats. The
forward pair measured 54.4 versus 52.7 FPS and the reverse pair 50.0 versus
47.3 FPS for candidate versus control. Both reached the same seeded late-game
scene with the same save hash and one pre-existing privacy-filter error. The
candidate was then rebuilt for `iphoneos`, signed with the existing development
profile, installed in place, and relaunched. The physical active-scene smoke
holds roughly 59.8–60.0 FPS at 1× with frame logging enabled and audio
underruns flat at three, but it has not reproduced the user's heavy moving
scene because the current desktop route cannot inject physical touch or an
Xbox controller. R915 is therefore a measured candidate with device startup
evidence, not final physical acceptance.

## Active user priority — R838 complete app experience

R911: prioritize a useful physical-iPad baseline; Simulator-only results cannot
establish device performance. See PHYSICAL-IPAD-FIRST-TEST.md. The connected
iPad and valid development signing identity are now verified for this private
run. Full PRD remains unchanged; UI is exploratory-test quality only.
R910 private module built and ran; R911 confirms actual guarded-path use but
its timing capture is invalid because SIGTERM did not export VI/work CSVs.
Never repeat that termination method for measurement: native menu Stop, verify
exported files and coverage, then terminate/restore/shutdown. No gain claimed.

R909–R910 whole normalization vector candidate passes261120 full-routine cases
and expanded known-result/rejection fixtures. Complete-routine ordinary inputs
improve~40–44% in NI0/NI1; rejected large/zero inputs regress. Private Simulator
module build34260 exited0; R911 staged and restored the private test host.
See NORMALIZATION-VECTOR-R910.md. No current FPS gain or lasting app change;
avoid returning to another round of isolated scalar opcode work.

R908 audits prior vector work before another implementation. Add/sub helper
R432 and cross-product R813 already failed scene benefit; do not repeat them.
Next bounded candidate is whole9-op normalization with guarded resident paired
vectors and exact reciprocal/scalar semantics, not scratch-state inlining or
more scalar-emitter coverage. VECTOR-REORIENTATION-R908.md records8 live input
lanes, rounding/observer hazards and complete-routine cost requirements. No FPS
gain, app change, or new performance measurement in this audit.

R907 reaches the13-op resident arithmetic cost gate and rejects the scalar
variant. Fixed/random/halfway whole-routine correctness passes, but both8-pair
cost runs are slower. Removing per-op scratch saves lowers instructions below
control without fixing latency. See RESIDENT-LONG-COST-R907.md. No app build.
Next materially different arithmetic execution (reference paired-vector path),
after auditing existing vector/precision experiments; no further scalar opcode
coverage or frame tuning on this variant. Full PRD and iPad performance remain.

R906 adds resident paired fused arithmetic with reference halfway correction,
NaN/exception handling, and non-NaN result negation. Actual four-op arithmetic
region passes fixed/random/explicit-halfway whole-routine tests, each629760
comparisons. See RESIDENT-FMA-R906.md. Next lane-selected/scalar/sum forms for
the longer64E0–6510 span, then complete-routine cost. No app or FPS gain yet.

R905 adds direct resident paired multiplication with exact rounding/status
behavior. Fixed and randomized-operand/FPSCR whole-routine tests each pass629760
cases. A raw underflow-flag mismatch was traced to the actual helper's
unconditional conversion and fixed, not masked. See RESIDENT-MULTIPLY-R905.md.
Next fused arithmetic/scalar/sum lowering for the long arithmetic span, then
whole-routine cost. Five-op integration is not a performance win or app candidate.

R904 integrates four real DOL paired merges into an otherwise original whole
chunk via build-time ARM64 suffix functions. Original dispatch charges and
FP-unavailable entry behavior remain; complete selected-routine comparisons
pass629760 cases. See RESIDENT-REGION-ENTRY-R904.md. Next substantial resident
arithmetic region, then complete-routine cost and only then same-scene iPad
measurement. No tiny-fragment benchmark, app promotion, or new FPS claim.

R903 completes paired-merge record-bit value/CR1 lowering in the private cache
prototype; intermediate non-record full-state checkpoint prevents hidden CR
regressions. Combined/plain/conversion tests each100k pass. See
PAIRED-MERGE-CR1-R903.md. Next explicit guest entry/availability/PC/cycle handling,
then broader resident arithmetic and whole-routine cost. No app/backend promotion
or FPS improvement; all original PRD requirements remain required.

R902 extends the private offline FPR-cache path with exact non-record paired
merge decoding/value lowering; resident source capture handles aliases/spills.
100k full-state/status comparisons pass in combined/plain/regression modes.
See RESIDENT-PAIRED-MERGES-R902.md. Next guest entry/availability/cycle boundaries
and broader arithmetic with resident values, then complete-routine actual-policy
cost. No transport microbenchmark or product/backend promotion; no FPS gain.

R901 whole-chunk guard-relocation cost gate failed: selected wide routine still
passes629760 correctness cases, but candidate executes~3% more instructions and
is slower in all8pairs; smaller code and changed PGO applicability do not prove
game benefit. See FP-GUARD-COST-R901.md. Close this rollout, no module build or
per-helper follow-on tuning. Next materially different shared execution/data-
lifetime mechanism from existing R899 evidence, not another baseline capture.

R900 implements private FP guard-chain relocation with original external-entry
guards/cycle charges and unchanged arithmetic/status. Wide629760 full-state
comparisons pass including lazy mode both ways. See FP-GUARD-CHAINS-R900.md.
Next actual-policy WHOLE-CHUNK control/candidate correctness and cost, retaining
normal dispatch; no extracted-routine speedup claim or module build yet.
Platform comparison also finds identical opcode sequences/counts across577
sampled native/Simulator chunks. No new FPS gain; full product goal remains.

R899 heavy native instruction capture completed and mapped:577 chunks,27,445
CPU observations, loads52.44% of generated sampled weights. See
HEAVY-NATIVE-PROFILE-R899.md for identities, trace, timing contamination and
non-identical iPad scene limits. Runtime cleanly stopped/save unchanged.
Heavy-scene attribution is available: next shared-code implementation hypothesis
from this disassembly, not another baseline/profile or closed small-routine lane.
No new FPS gain or physical-device/gameplay acceptance.

R898 reconciles retained invaded-plaza wall sample with starting-plaza weighted
profile; see PERFORMANCE-SCOPE-R898.md. Cost is broad, and recent tiny-routine
screens cannot establish a material whole-game gain. Next one source-matched
native invaded-plaza instruction profile using the known working attach path:
identify which shared-code mechanism grows after the movie, then implement and
test it on iPad. No unchanged Simulator profiler retries, new sampler framework,
movie throughput replay, or another narrow guarded-memory variant.

R897 same-process iPad transition captured completely: movie59.88VI/s, invaded
plaza37.15VI/s with23.42ms CPU/VI and178.58M instructions/VI;74audio underruns in
interior21.5s gameplay interval. See POSTMOVIE-IPAD-R897.md. This is heavier than
R890 quiet plaza, not a cutscene-decoder failure or new FPS gain. Next material
whole-workload CPU reduction informed by retained profile coverage; no repeated
movie counters, tiny-routine tuning, or speculative depth-wait removal.

R896 readback audit reconciled with prior R595–604: no justified wait removal;
actual-method staging control-flow regression passes ASan/UBSan. Preserve depth.
Next actual heavier post-movie iPad gameplay: R890 neutral pre-invasion56VI/s is
not R791 invaded-plaza31.95VI/s. Reuse existing larger recorder/output telemetry
across that transition, separating workload growth from slower same-work execution.
No new recorder architecture, neutral-title loop or speculative wait rewrite.
Original full PRD and shippable iPad experience remain required.

R895 transfer tests complete: normalization regresses and cross has negligible
CPU gain. Wide correctness still passes. Close broad direct-memory rollout;
no more guard tuning/module builds for it. See WIDE-FP-TRANSFER-R895.md.
Next source-audit CPU/GPU synchronization at EFB cache population/Metal staging
Flush for a concrete removable submission/wait cost, preserving current depth
semantics. No stale-depth workaround or repeated duplicate-peek experiment.
Full PRD and iPad gameplay/cutscene acceptance remain required; no new FPS gain.

R894 private guarded direct-memory routine passes314880 comparisons. Initial
whole-routine cost shows~15% fewer instructions but only5–7% CPU improvement;
not whole-game gain. See WIDE-FP-CANDIDATE-R894.md for final-guard timing caveat.
Next test transferability to different representative whole routines, preserving
callbacks/aliases/arithmetic and actual-policy cost. Do not tune this small
single-routine win or build a full module without material aggregate evidence.

R893 complete41-instruction original-chunk oracle passes314880 comparisons,
including aliases, quantization, callbacks and independent cycle/exception checks.
See WIDE-FP-ORACLE-R893.md. Next implement private guarded normal-RAM candidate
against this oracle, then inspect/measure whole-routine code under actual policy.
No candidate/FPS gain yet; no additional baseline/census/module build justified.

R892 memory-inclusive source query/tests complete; selected larger41-instruction
804B64A4–6544 routine for explicit observer-preserving oracle/fast-path contract.
See FP-MEMORY-SPANS-R892.md. Next implement that complete routine boundary, not
another census, compact-normalization variant or unchanged gameplay capture.
No module build before material actual-policy cost evidence; no FPS gain yet.

R891 correction after reading actual R791 evidence: native movie callback delivery
already passed; post-movie starvation coincided with sustained slow gameplay.
Do not invent a separate decoder audio bug, enlarge buffers or replay that movie
for the same throughput proof. Perceptual sync/device/promotion gates stay open.
R890 platform comparison is now complete enough to resume CPU implementation:
evaluate broader whole-routine register retention, not the rejected compact
normalization/state-copy, restrict, lookup snapshot or guarded direct-call designs.
Require a concrete observer/entry/cycle contract and material containing-routine
cost reduction before module integration. No speed gain claimed by this audit.

R890 actual iPad matching plaza baseline completes:56.114VI/s,15.660ms CPU/VI,
139.705M thread instructions/VI,98.38% P-core time, zero swap in full host bracket.
No historical6–22FPS reproduction or new code speedup. See
IPAD-PERFORMANCE-RESULT-R890.md. Stop unchanged baseline/recorder-build loops.
Next implementation lanes: material correctness-qualified CPU instruction
reduction (honor closed shared-state/FP designs), and existing native-THP movie
candidate's unresolved audio/transition gate. Accept changes on repeated iPad
gameplay/cutscene windows and sustained routes, not macOS-only or counters alone.
Full original PRD and product finish requirements remain unchanged.

R889 completes native CPU-thread comparison (THREAD-WORK-NATIVE-RESULT-R889.md).
Similar instruction work, slower Simulator CPU execution; native itself drops
60→32VI/s with stable work late in the capture. No optimization gain established.
User explicitly prioritizes iPad Simulator. Next capture synchronized iPad
thread/VI and host-pressure data during actual slowdown, select one material
intervention, then matched baseline/candidate gameplay AND cutscene verification.
No more control-only or unchanged title-check loops as performance progress.
Original full PRD, SunPad fidelity, audio/device/package gates remain intact.

R888 private paired recorder capacity65536 built/tested; product default intact.
Next run R889 native neutral-plaza measurement with working background-input
route and unchanged module. Require complete coverage; do not rebuild again or
claim instrumentation as an FPS improvement. Full original PRD remains active.

R887 corrected native runner reaches neutral plaza and completes snapshots, but
paired16384-row recorders filled before the requested window. Completeness check
rejects it; no result accepted. Next increase bounded private recorder capacity
or arm post-startup, with paired-buffer tests; never relax coverage validation.
Reuse working background-input route, not another unchanged-capacity attempt.

R886 isolated native counter candidate r886c now includes tested default-off
--background-input; control/source/object scope checks and signature pass.
Next launch this candidate with the option and fresh recorder outputs for the
pending R836 native thread-work comparison. No repeat build needed; no speed
gain established. Original PRD/product/physical/audio requirements unchanged.

R885 returns to unresolved native-versus-Simulator CPU-thread work comparison.
File-only BackgroundInput change is invalid: RuntimeConfig overwrites it; existing
counter runner lacks the isolated tested --background-input patch. Native attempt
stopped cleanly, no valid comparison. Next integrate that option into isolated
counter runner with control/scope proof, then capture once. No repeated unchanged
navigation or new module build. UI/full PRD/device/audio objectives remain intact.

R884 physical-iOS Release host rebuilt and privately staged with unchanged
device module. Current UI changes compile for IOS16+, not just Simulator.
No device connected, no signed hardware/runtime acceptance. Next Back/story
layout and bounded performance work; retain full PRD, not another unchanged build.

R883 packaged B activation returns existing file panel to planets with scripted
input released. Causal button response proven, not full accessibility/Plus proof.
Next current physical-iOS host compilation/integration (older device candidate
lacks recent changes), then remaining Back/story layout and performance work.
Do not repeat file/title checks without a new decision. Full PRD remains intact.

R881 adds explicit accessibility button pulses, isolated from physical-held
input, with reset/menu cancellation. Focused UIKit tests and host build pass;
not installed or causal proof of R880 Plus behavior. Next check actual activation
before claiming input acceptance; do not remap the valid Plus binding speculatively.

R880 actual phone confirmation/plaza visual check passes for new Plus placement;
save unchanged/clean stop. AX Plus activation produced no visible game pause,
so input behavior remains open: inspect activation vs mapping vs phase before
claiming a fix. Movement stick still overlaps Back/story; those remain next
layout targets. No repeat file-opening loop solely to re-prove Plus geometry.

R879 phone pause candidate moves inward beside actions (.72,.62), preserving
custom layouts/iPad. Lower-right proposal was rejected because it reintroduced
R848 save-Yes overlap. Focused exclusion/min-target tests and host build pass.
Next actual phone gameplay/confirmation visual verification, not position-only
acceptance; other Back/story/button/HUD overlaps remain open.

R878 verifies one actual same-process stop/restart pair: clean idle screen,
explicit Restart, fresh renderer/module initialization in same PID and two clean
stops, save unchanged. Not gameplay-input or audio acceptance. Return next to
known phone HUD/control overlaps and an actual gameplay action rather than
repeating this startup pair. Preserve performance and full original PRD gates.

R877 implements idle gameplay visibility and guarded Restart Game; Release build
and isolated overlay regressions pass. Next actual packaged same-process
stop/restart test is required: idle menu access, no idle game controls, clear
restart affordance, fresh rendering/input after restart, clean stop/save retention.
Do not treat isolated UI tests as runtime reuse proof. Full PRD remains open.

R876 actual packaged Audio menu/stop/relaunch pass completed: mute and50% persist,
unmute preserves50%, runtime config reflects both, clean exits/save unchanged.
Not audible gain or physical/audio acceptance. Next concrete UX defect is the
stopped screen: hide inapplicable gameplay controls and offer explicit Restart,
with startup guarding and continued menu/data access. Do not repeat the same
Audio startup solely to prove stored values again. Output gain remains open.

R875 queue refresh: main-volume/mute settings and native Audio menu now compile
and pass isolated UIKit regressions. Next stage this host with the unchanged
accepted module and verify actual menu operation, mute/unmute, pause/resume and
stop/relaunch retention on one Simulator. Do not infer audible gain from the
R874 parameter probe or these UI tests. Separate Wii Remote speaker gain remains
open. Then return to phone layout overlap and gameplay/performance acceptance;
avoid repeating title navigation, tilt-consumer audits or counters without a
specific new decision. Icon/README assets exist, not full release acceptance.

R862 queue refresh: R861 verified packaged iPhone import/save recovery through
plaza movement; do not repeat the opening by default. Next close discoverability
and actual gameplay control gaps: concise in-menu touch guidance, followed by
unverified pointer/action or motion-alternative gameplay and lifecycle checks.
Keep the known phone HUD/control overlaps open. Icon assets and README exist,
but neither implies full branding, packaging, physical-device or release acceptance.
No measured performance improvement is claimed by the recent product passes.

R847 corrects the R846 detour: fallback counts are also present in R841/R844
iPad runs, and PERF R489/R553 plus JOURNAL R755/R758 already describe the counter
semantics and phase-specific vector census. They are not evidence of a new iPhone
regression or an interpreter time budget. Do not repeat that census by default.
Next extend the clean iPhone product run beyond startup into title/file creation
and gameplay, checking actual control/HUD placement and lifecycle. Keep its saves
separate. Native-only and performance acceptance remain unproven; preserve the
complete product queue below.

Chris explicitly requests continued app-experience optimization, refined controls
and a sensible shippable touch menu, an original GalaxyPad iPadOS/iOS app icon,
and README parity with SunPad. This supersedes earlier performance-only queue
ordering, not the original PRD/G0–G15 acceptance requirements or release gates.

1. Native thread-work navigation attempts are stopped; no valid comparison was
   captured. Park this lane while advancing the user-facing work below. Do not
   expand profiling tooling as the default queue.
2. Refine controls and the three-dot menu against the actual original SunPad
   implementation and Galaxy's actions. Keep primary controls ergonomic, avoid
   action-word text crammed into buttons and persistent rarely used controls.
   Verify mappings, simultaneous touches, pointer/Spin, safe areas, editing/reset,
   menu pause/resume and input clearing on one Simulator at a time. Inspect before
   changing; preserve working wiring and test each changed interaction.
3. Create original GalaxyPad icon artwork and complete iPhone/iPad AppIcon assets,
   with provenance and small-size/masked visual checks. No Nintendo artwork,
   characters, extracted textures or copied SunPad branding. Retain editable
   project-owned source and satisfy the PRD's macOS branding requirement too.
4. Bring README structure and usability to SunPad parity: accurate overview,
   screenshots when available, supported game/platform boundaries, prerequisites,
   reproducible setup/build/run, controls/menu documentation, troubleshooting,
   credits/notices and honest known limitations. Do not copy unsupported claims,
   declare releases available, or publish private/game-derived artifacts.
5. Continue performance changes with falsifiable, bounded comparisons and visible
   gameplay/audio evidence. Product/UI/icon/documentation work no longer waits
   for every performance uncertainty to be resolved. No benchmark-only completion.

Each continuation should advance a concrete user-facing deliverable or close a
specific runtime defect/evidence gap. Record what changed and what was actually
verified. All story/save/lifecycle/audio/stability/device/packaging requirements
remain; shippable is an acceptance standard, not authorization to publish.

## Active priority adjustment — R824 generated state lifetime

R836 completes the actual Simulator CPU-thread window:49.379VI/s,17.941ms CPU/VI,
140.437M thread instructions/VI,98.33% Performance-core CPU time. No dropped
samples or clock-unit mismatch. Do not blame E-core dominance for this run or
call its difference from R831 a speed fix. Next isolated native host-only recorder
counterpart, with verified control identity and unchanged guest module, to compare
same-thread work versus execution time. See THREAD-WORK-RESULT-R836.md. No repeat
Simulator capture, QoS tuning or original PRD scope reduction is warranted.

R832 standalone self-thread counter probe passes on native and Simulator with
verified Mach clock conversion. Next private opt-in VI-recorder integration and
injected-counter tests before a host-only diagnostic build, reusing unchanged
guest modules. Keep private SPI out of ordinary release targets. Measure actual
CPU-thread work/core-class time; standalone probe placement is not game evidence.
See THREAD-COUNTER-PROBE-R832.md. All original product requirements remain.

R831 completes the R830/R831 neutral-plaza platform comparison: Simulator CPU
time is2.07x native with only2.83% more whole-process instructions/VI. This is
not guest-thread or frequency attribution. Next qualify a bounded self-thread
counter probe and its clock units before another app build; preserve denied
profiling boundaries and do not repeat unchanged attaches or QoS tuning. See
PLAZA-PLATFORM-RESULT-R831.md. No speed fix or product gate is claimed; full
original PRD/SunPad/gameplay/audio/stability/device objective remains unchanged.

R828 supersedes the compact-normalization continuation: full audit retains96
host-flag failures; a separately qualified finite workload is~27% slower with
~7% more instructions. Park this design without further tuning or game build.
Next reconcile retained macOS/Simulator per-frame work, settings and host-version
differences before selecting another generated arithmetic target. See
NORMALIZATION-DISPOSITION-R828.md. Full original product requirements remain.

R827 compact FP closure passes isolated oracle and reduces scratch, but the
actual-policy whole-chunk routine fails host flags before timing. Investigate
the retained exact failing case; do not mask flags or promote from isolated
success. No game rebuild until correctness and cost gates pass. See
COMPACT-NORMALIZATION-R827.md. Full original requirements remain unchanged.

R826 establishes a real normalization-region oracle: all9suffixes and state/FP
flags pass in sanitized and ThinLTO modes. A local full-CPUState copy still has
a large stack frame; it is a correctness scaffold, not a speed candidate.
Evaluate compact FP-state/helper dataflow against this oracle before a cost
gate or game build. See NORMALIZATION-STATE-R826.md. Do not keep copying full
CPUState or tuning attributes; all original requirements remain unchanged.

R825 closes a simple CPUState restrict annotation: three whole-chunk private
ThinLTO pairs have identical instruction encodings. No timing run or app rebuild
is warranted for that design. Explicit state-lifetime changes remain distinct;
do not replace them with another alias/inline attribute. See
STATE-ALIAS-CODEGEN-R825.md for the verified compile-only boundary.

R822 supplied an actual macOS plaza per-PC profile; R823/R824 resolve opcode
weights and conservative local load origins. Next inspect whole-chunk optimized
state lifetimes and prototype only a substantive reduction that is not already
performed by LLVM or equivalent to rejected mapping-cache designs. Preserve
callback observations, aliases, exceptions, interior entries and cycle accounting.
Require full-state differential and actual-policy whole-chunk cost gates before
another app build, then matched gameplay A/B before promotion. Do not build a
general provenance analyzer or repeat unchanged profiles. See
PLAZA-LOAD-ORIGINS-R824.md. Original full PRD/SunPad/device requirements remain.

## Active priority adjustment — R815 shared native-loop cost gate

R817 supersedes the pending cost gate: separate-TU extracted-burst measurements
show no material repeatable savings with nontrivial callbacks. Park quiet-loop
specialization; no app rebuild or more tiny flag variants. Return to broad
source-correlated generated-code costs across chunks using retained R813 data,
not entry-frequency-only target selection. RUN-QUIET-COST-R817.md records results
and limitations. All original requirements remain unchanged.

R813 closed the cross-product candidate without repeatable game-speed benefit.
R814 separates thread costs and identifies shared Run self work. R815 audits
optional configuration and passes an extracted native-burst differential with
stub services. Next measure actual-policy whole-burst specialization cost, with
opaque representative callbacks and entry/code-size overhead, before a private
host rebuild. Preserve live SMC, hooks, timing, exceptions and CPU state; no
stale eligibility caches. Park this lane if savings are negligible. See
RUN-QUIET-AUDIT-R815.md. Full original PRD/SunPad/gameplay/audio/stability/device
objective remains unchanged; tests alone do not establish performance.

## Active priority adjustment — R806 actual mode prerequisite

R813 disposition supersedes the R808 next step: sequential plaza measurements
25.93 baseline,26.63/26.01 candidate,27.06 reverse baseline show no repeatable
material gain. Park the cross-product region; no further guard tuning or
expansion from its local benchmark. Fresh post-measurement plaza CPU sample is
retained; classify CPU/GPU stacks separately and map host dispatch/vertex-decode
cost to source before another build. See CROSS-DISPOSITION-R813.md. All original
product requirements remain unchanged.

R808 update: NI-capable diagnostic now passes actual Star Festival plaza
eligibility:99.21695% of999424 calls fast, zero mode rejection. Simulator stopped,
save unchanged. Next distinct uninstrumented candidate and matched sequential
plaza speed comparison, not more eligibility-only runs. Diagnostic FPS remains
poor and is not a performance A/B. See CROSS-SCENE-R808.md. All original goals
below remain in force.

Live title/file-select counters all rejected the old NI guard; observed FPSCR
86004004 has NI1/RN0. Bounded NI-capable source passes local/full-context gates
with retained ordinary-input benefit. Build a distinct diagnostic using verified
unchanged control/objects, then remeasure applicability before uninstrumented
scene A/B. Do not reuse the NI-rejecting R804 binary or infer gameplay gains from
the menu observation. CROSS-LIVE-MODE-R806.md records evidence and save safety.
Full original PRD/SunPad/performance/audio/stability/device goals remain intact.

## Active priority adjustment — R803 measure applicability before promotion

Expanded callback/journal/alias/suffix gates pass. Varied eligible inputs retain
~20% local gain, but large-value rejection and midpoint ties cost~19%/~29% more.
The fallthrough rewrite preserves rejection state but does not remove the cost.
Next use a private bounded diagnostic candidate to measure actual scene
eligibility/rejection mix; retained entry counts have no operand distribution.
Keep instrumentation measurements separate from uninstrumented scene CPU/FPS
A/B. Do not promote or keep tuning guards based only on ideal inputs.
CROSS-CONTEXT-R803.md records evidence. Original PRD and all product gates remain.

## Active priority adjustment — R802 whole FP island benefit

Whole cross-product vector region in the existing C backend passes focused and
actual-routine state gates and reduces local CPU time~19.52%, instructions~10%
under original strict-FP/ThinLTO flags. Candidate profile is unmatched and the
workload is fixed-input: this is not game-wide benefit. CROSS-ISLAND-R802.md
records evidence. Prioritize this simpler existing-backend path over additional
offline compiler expansion. Extend callback/alias/tie/varied-input and rejection
cost coverage before a private module, then bounded scene A/B. Preserve full
original PRD/SunPad/audio/stability/gameplay/device requirements and exact source
identity. No default promotion or completion claim from an isolated routine.

## Active priority adjustment — R798 offline exporter cost screen

The bounded offline integer exporter now links and passes full-state, callback,
RAM and CPU-alias differentials for two real blocks. Direct RAM load emission
does not beat generated C in the isolated mixed-block cost screen. Do not
promote it or tune the same tiny fixture repeatedly. Qualify a larger observed
hot region and its state-observation boundaries; account for helper crossings,
register lifetime and save/restore work before further backend expansion.
Require actual-policy material cost improvement before a broader module build.
ARM64-DIRECT-LOAD-R798.md records results and limitations. Full original PRD,
SunPad, gameplay, movie/audio, stability and physical-device gates remain.

## Active priority adjustment — R793 broader native lowering

Mapping lifetime audit does not justify blanket cache removal across mutable
module/callback boundaries. Current C memory variants retain their prior cost
dispositions. Evaluate a private offline ARM64 complete-block exporter using
reference register allocation/precision dataflow, with static helper relocations
and an explicit state adapter. NATIVE-EXECUTION-R793.md records live-pointer,
GQR-specialization and code-cache dependencies. Prove relocatable linking,
full block state/memory/exception/cycle equivalence, then material actual-policy
cost reduction before broader build. No runtime code generation on mobile.
At R793 this exporter was not implemented; R794–R798 provide a bounded integer
prototype, not a complete backend. Preserve all original PRD/SunPad/device,
movie/audio and stability requirements; no completion claim from an isolated block.

## Active priority adjustment — R791 movie delivery evidence

Private native movie now has matched59.946frame-events/sec and approximately48kHz
nonzero callback delivery with zero new underruns in36.9seconds; complete5591
native frames/0fallback, clean return/stop. Post-movie gameplay31.953events/sec,
104underruns in21.5seconds despite full output callbacks. See MOVIE-AUDIO-R791.md.
This is callback evidence, not perceptual pitch/AV-sync/device acceptance. Keep
native decoder default OFF pending remaining gates; no more unchanged movie
throughput/output-counter replays. Return to material native guest execution
cost with retained instruction-level coverage/exact-policy disassembly before
another candidate build. No tiny helper variants or larger audio buffers to mask
the sustained producer deficit. Full original PRD, SunPad UI, stability and device
requirements are unchanged.

## Active priority adjustment — R788 local arithmetic lane disposition

Instruction-level retained coverage corrected cold target selection. Hot square
has a bounded~7%routine gain; general multiply and shared-load/type variants only
~1.1%/~3.4% with higher instruction work. None proves material game-level gain.
Do not extend those variants with more predicate/attribute tuning or a full build.
Next close a missing timing/audio delivery gate on the substantially faster
private native movie path, first auditing retained logs for the exact evidence
gap. No unchanged opening replay, throughput or pixel checks just to restate
known completion. Gameplay CPU deficit and all original PRD gates remain open;
no default decoder promotion without the required evidence.

## Active priority adjustment — 9 September, R780 precision cost gate

Guarded precision propagation passes full-transform correctness but yields only
about2.8% local CPU benefit with more instructions. This is insufficient for a
full module build or game-speed claim. Close this batch implementation for
promotion; no further attribute/representation variants. Before implementing
broader typed lowering, establish reachable coverage and attributable native
cost using retained profiles/source, then choose a materially larger target.
Run regressions including precision-fact/typed-arithmetic tests. Preserve the
original performance, cutscene/audio, stability, SunPad and device requirements.

## Active priority adjustment — 9 September, R769 actual-policy FP result

Mandatory float-helper inlining fails the whole-chunk ThinLTO/PGO cost screen:
~1.4% fewer instructions, slightly slower CPU time, versus the misleading~16%
standalone result.22,528 fixture comparisons pass but do not justify deployment.
Close blanket inlining and attribute tuning. No full module build is warranted.
This is not proof all FP/state-lifetime changes fail; new work must change the
underlying generated dataflow and demonstrate a material benefit in real build
context, not isolated helper code. Keep the malformed XF stability fault open
and inspect retained origin evidence before any renewed long gameplay run.
Original PRD, SunPad UI, audio, progression and physical-device gates remain.

## Active priority adjustment — 9 September, R764 CPU-time split

Fresh phase-selected Simulator plaza capture gives non-native routing an
estimated2.08% of CPU-thread time (includes fallback AND host-call routing).
Native bursts dominate.14,145 native and3,426 non-native samples, no clock
errors. Raw native estimate101.35% illustrates sampling/clock overhead, not
impossible physical utilization; do not normalize it or claim precise shares.
See RUN-COST-EXPERIMENT.md. This is enough to park the vector acceleration lane,
not a speed improvement or instruction-level native attribution.

Return to material native execution overhead: inspect repeated state/timing
materialization and shared FP work under the original observer/cycle/exception
contracts. Use source/disassembly and retained profile evidence to qualify a
substantial change before a full module build. Do not restart the rejected
dispatch-only vector, direct-call ABBA failure, or tiny lookup variants.
Full original PRD, performance/stability, SunPad UI and physical-device gates
remain unchanged. Default diagnostic clocks remain OFF.

## Active priority adjustment — 9 September, R761 vector cost screen

R762 fresh current-build plaza sample:9 interpreter-ancestry samples out of1695,
but236 Run self samples. This is wall sampling, NOT an exhaustive CPU-cost bound.
Two displayed Run offsets map to AOT dispatch/bookkeeping; collapsed offsets
cannot be apportioned. Deprioritize vector execution; next distinguish AOT
state/timing work from fallback chassis cost, retaining material-benefit gates.

R755/R758 established low-vector fallback-step dominance and exact installed
RAM templates, not CPU-time dominance. R760 recognition and R761 reuse of the
actual interpreter dispatch tables now pass focused tests. The dispatch-only
guarded candidate loses its isolated ABBA cost screen (6.73–7.08ns versus
4.35–4.37ns baseline); do not integrate, rebuild or polish this variant.

Next qualify the WHOLE fallback path's CPU cost in the verified plaza before
designing broader batching/chassis changes. Use a bounded diagnostic with
explicit overhead/phase limits; step counts alone do not establish this cost.
If cost is minor, close this lane and return to measured AOT/shared-state work.
If material, preserve the R759 exception/fetch/budget/observer contracts before
reducing repeated chassis work. No general cached-backend swap or mobile JIT.
The prior Simulator ownership note is superseded by the user's authorization
to switch: shut down the existing Simulator before booting another, no repeated
permission request. Full original PRD and G0–G15 remain unchanged.

## Active priority adjustment — 9 September, R736 measured direct-call disposition

R745 stability interruption: R742 runtime ended after malformed XF command
00611600, with no clean shutdown/census. Analyze the captured FIFO command
boundary before another performance run; do not suppress the assertion. UI
access recovered, but another project's Simulator is booted: preserve it and
the one-Simulator limit. Full performance and original PRD scope remain intact.

R740 next executable diagnostic: identify actual mobile interpreter PCs with a
bounded opt-in census (FALLBACK-PC-EXPERIMENT.md). R737–R739 narrow shared-FP
variants failed scope/code-shape screening; do not keep extending them. Broader
shared-state work remains eligible with a material-benefit case. The census is
attribution, not performance acceptance or authorization to bypass verification.

The first guarded cross-chunk design is closed for promotion after R734–R736
matched-binary AB/BA trials. CPU/VI improvement did not reproduce; process
instructions/VI increased in both pairs. Preserve experimental code/artifacts
but keep binding off in product paths. This is not proof every possible direct
call architecture fails, nor permission to enable the unsafe prototype.

Next major lever: shared floating-point helper/state-materialization overhead.
Use current source and retained profiles to identify repeated work across
instructions, then implement one semantics-preserving shared-path change with
an explicit observer/exception contract and material-benefit gate. Do not reopen
tiny routine/lookup experiments or loosen FPRF/NaN behavior without proof.
Full PRD/G0–G15, SunPad UI, mobile/device, story/audio/stability gates remain.
See DIRECT-CALL-EXPERIMENT.md R736 for measurements and limitations.

## Earlier priority adjustment — 9 September, R711 independent review

Chris supplied an independent performance review and requested reassessment.
Follow `docs/REVIEW-RESPONSE-2026-09-09.md` for its source-checked disposition
and experiment gates. This supersedes the narrow profiling/memory work queue,
not the original PRD or G0–G15 acceptance criteria. The actual PRD filename is
`docs/GALAXYPAD-PRD.md`.

1. Make architectural AOT execution overhead the main performance workstream.
   First evaluate guarded cross-chunk call/return on an isolated macOS diagnostic
   path; do not simply enable the existing unsafe direct-call flag.
2. Use matched CPU time/VI, process instructions/VI and dispatches/VI, retaining
   visual correctness, frame-time and host-pressure checks. Do not infer dynamic
   call rates from static branch counts or whole-run charged-cycle ratios.
3. One major lever at a time, a material predicted benefit before a full module
   build, and explicit success/failure thresholds. Preserve SMC, hook, exception,
   timebase, stop, depth and callback contracts before promotion.
4. Second priority is shared FP/state-materialization work with explicit observed
   semantics; third is identified mobile fallback overhead. JIT comparisons do
   not by themselves authorize silent accuracy reductions.
5. Stop unchanged plaza wall-stack recaptures, small mod lookup tuning, repeated
   movie navigation and further checkpoint-memory iteration as the default loop.
   Current memory candidate is recorded but its live release check is unfinished.

Full SunPad UI/menu/touch fidelity, story completion, stability, audio, packaging
and physical iOS/iPadOS proof remain required. No performance gate is closed by
accepting this review or by passing a synthetic experiment.

## Active priority adjustment — 8 September, R653

Chris explicitly reprioritized frame rate and prerecorded-cutscene performance.
The full G0–G15/PRD scope and acceptance criteria below are unchanged. Performance
now gates resuming the long mobile first-play route; UI polish, touch verification,
and repeated title-to-movie navigation are not the main work queue.

Follow `docs/CUTSCENE-PERFORMANCE-PLAN.md` in this order:

1. Establish exact video cadence and isolate decoder throughput from host stalls.
   Use direct movie frames and a bounded harness rather than navigating the game
   for every experiment. Distinguish source frames, VI, presents and wall time.
2. Investigate a native ARM64 THP decoder at the existing THPVideoDecode boundary,
   preserving the exact supported game's outputs, side effects and player contract.
   Existing generated-code kernel extraction is not a whole native decoder.
3. Fix measured buffering, synchronization and audio-clock bottlenecks, preserving
   guest timing, completion, cancellation and return-to-gameplay semantics.
4. Quantify memory compression/swap and process contention with timed deltas.
   No killing unrelated apps, clearing caches or changing their settings without
   permission. Device/signing access remains a separate physical-proof boundary.
5. Optimize upload/presentation or gameplay EFB only when stage timings identify
   them. No speculative resolution/QoS changes or returning fake/stale depth.

An experiment must change the decision: standalone throughput plus output parity,
then a complete in-game movie with normal duration/audio and correct return.
No more unchanged byte-cache A/B runs; its mobile default is already implemented.
Do not equate that incremental improvement with cutscene/performance acceptance.
Resume broader progression and SunPad UI completion after this blocker is reduced.

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

## Current unattended performance loop status — 2026-09-11

The Simulator loop now has a measured candidate/control gate with frame windows,
host CPU, audio underrun counters, save-seed identity, screenshots, and CPU samples.
The normal-reader pointer candidate passed its offline parity gate but failed the
end-to-end gate: 58.416 FPS average and +25 underruns versus 58.817 FPS and +15
underruns for control. The candidate is parked/rejected, the canonical core archive
is restored, and no physical-device install was performed. The remaining performance
defect is still the shared native execution/dispatch path under the seeded late-game
scene; the next loop step is one separately measured candidate there or an opt-in EFB
dispatch trace, not another resolution/logging toggle or vertex-reader rewrite.

## Self-audit reorientation — 2026-09-12

The goal loop did not deliver a speed improvement in the preceding work window.
It produced useful negative results and a partial diagnosis, but I continued
through several low-leverage candidates after the evidence had shifted to the
shared native execution path. No candidate was promoted and no physical device
or save was changed.

The next loop step is therefore measurement, not another patch: capture
timestamped stacks and scheduler state during the stationary seeded scene and
correlate them with DMA underrun gaps. `RunCost` percentages and phase-file
writes are not exclusive attribution. The host must be quiet enough for a
matched comparison; unrelated QEMU, transfer, and build jobs remain out of
scope and must not be killed by this loop.

The harness has an opt-in System Trace path. macOS rejected the first live
`spindump` attempt without root, and the unprivileged Simulator `xctrace`
attach could not resolve the Simulator PID. These are recorded tooling
failures, not game results. Advance to a source optimization only after two
captures show one lane accounts for at least 60% of combined underrun-gap time.

## Packed texture-coordinate candidate — rejected — 23:04 JST

Secondary Astra Medium reviewed the retained profile and selected one bounded
candidate in the u16-indexed signed-16 two-component texture-coordinate path.
The ARM64 object gate passed with a 12-byte text reduction and no calls or
spills, but the matched five-second phase trace did not: 19 DMA underruns for
the candidate versus 18 for control, and 231 versus 253 terminal frames.
The source was reverted and the canonical Simulator core/app rebuilt. The
physical iPad and unrelated Simulators were left untouched.

## Dispatcher duplicate-PC-store candidate — rejected — 23:18 JST

A generated-module candidate removed the duplicate `ctx->pc = address` store
from the private original-call helper. It passed the static module-size gate
with an 8-byte `__text` reduction, but matched five-second phase traces were
worse: 252 terminal frames and 19 DMA underruns versus 256 frames and 17 for
the canonical control. It was rejected; the canonical Simulator app/module
remain selected and the physical iPad was untouched.

## Latest unattended iteration — 22:26 JST

The rebuilt canonical Simulator app completed a bounded logging-off contract run
on the dedicated iPad Simulator. Startup logged `aspect_ratio_mode=0` (4:3) and
`frame_logging=0`; the 2064x2752 capture shows the expected 4:3 gameplay viewport.
The loop now records `host-top-before.log` and `host-top-after.log` beside each
profile so concurrent Android/QEMU, indexing, or other host work is visible in
the evidence. This run was host-pressure-qualified because unrelated QEMU was
over 100% CPU.

A branch-hint experiment against the measured vertex cache branches increased
the ARM64 object text sizes (Normal 12,236 to 12,856 bytes; Position 6,456 to
7,116 bytes), so it was reverted and not promoted. The canonical module remains
selected, the physical iPad remains untouched, focused checks pass, and the
full repository suite remains limited by the known missing private THP fixture
`generated/thp-kernels-r198-exits/candidate.c`.
The page-table and 16-bit lookup variants were also measured and rejected; the
baseline remains the only installed Simulator candidate.

The following EFB trace attempt was diagnostic only. With
`GALAXYPAD_SIMULATOR_EFB_TRACE` enabled, the baseline route produced no
`efb-trace.csv` and reported zero EFB peeks in every runtime snapshot. This
route did not enter EFB readback, so the next performance hypothesis remains
the shared native execution/dispatch path (or, separately, making trace
activation reportable), not an EFB semantic change. The run still captured a
295.192 ms maximum frame gap and DMA underruns increasing from 2 to 23; its
full evidence is under
`generated/runtime/ipad-iteration-1/simulator-baseline-efb-trace-20260911/`.

The opt-in phase capture at
`generated/runtime/ipad-iteration-1/simulator-baseline-phase-trace-20260911/`
adds 73,451 timestamped events. It records 43 DMA underruns, producer enqueue
gaps up to 223.194 ms, frame-end gaps up to 441.205 ms, queue depth only 1–35,
zero queue-full drops, and zero short output callbacks. The first underruns
fall inside 59.040, 114.069, and 188.675 ms producer gaps; subsequent bursts
occur after the queue has drained to two-to-six entries. This is diagnostic
confirmation of guest-side producer starvation under CPU pressure. The phase
trace is not an FPS acceptance run because its per-event file writes perturb
timing.

Prebuilt 1024 and 512 C-loop variants were both tested but are not valid
budget-only differentials because their compile commands omitted the baseline
module's ThinLTO flag. The 1024 run measured 57.295 FPS average, 38.455 FPS
minimum, 72.53% CPU, and 48 underruns; 512 measured 58.055 FPS average,
44.815 FPS minimum, 69.05% CPU, and 27 underruns; the matched telemetry
baseline measured 58.540 FPS average, 47.170 FPS minimum, 68.46% CPU, and 23
underruns. Both are rejected as package candidates, with no selection or
physical install. A proper ThinLTO-preserving budget build is required before
making a budget conclusion.

The fair ThinLTO-preserving 1024-cycle candidate then completed on the same
seeded replay. It measured 58.080 FPS average, 44.999 FPS minimum, 43.644 FPS
minimum observed, 69.925% average CPU, and 33 cumulative DMA underruns,
versus the canonical telemetry baseline at 58.540 FPS, 47.170 FPS minimum,
39.095 FPS minimum observed, 68.461% average CPU, and 23 underruns. It is
rejected as slower and less audio-stable; the canonical module remains
selected and no physical install changed. Evidence is under
`generated/runtime/ipad-iteration-1/simulator-loop1024-ipo-candidate-20260911/`.

The fair ThinLTO-preserving 512-cycle candidate also completed on the same
seeded replay. It measured 58.632 FPS average, 47.883 FPS minimum, 46.365 FPS
minimum observed, 69.542% average CPU, 25 cumulative DMA underruns, and three
backlog drops, versus the canonical telemetry baseline at 58.540 FPS, 47.170
FPS minimum, 39.095 FPS minimum observed, 68.461% average CPU, 23 underruns,
and two backlog drops. The slight frame-rate increase does not offset worse
CPU/audio counters, so the candidate is rejected; the canonical module remains
selected and no physical install changed. Evidence is under
`generated/runtime/ipad-iteration-1/simulator-loop512-ipo-candidate-20260911b/`.

The existing opt-in run-cost census was exercised in a temporary diagnostic
build. Adding periodic reporting made the disabled path regress to 57.880 FPS
average, 75.14% average CPU, and 43 cumulative DMA underruns, so that change
was reverted and the canonical app/core were rebuilt. The temporary run
recorded 12.002 seconds of CPU-thread time; its one-in-256 samples extrapolate
to about 81.19% native execution and 1.03% non-native routing, with the
remainder outside those selected lanes. This is coarse attribution only, not
an FPS/audio acceptance run, but it lowers the priority of fallback/interpreter
routing and keeps the hotspot on generated native execution
(`StaticRecompCore::Run` -> `chassis_dispatch`, led by `func_805170A0`).
Evidence is under
`generated/runtime/ipad-iteration-1/simulator-baseline-run-cost-20260911b/`;
no module selection or physical install changed. The post-revert replay is
qualified because the host simultaneously carried an unrelated QEMU process
above 100% CPU and other workloads; it is not a clean performance comparison.

## Current unattended performance loop status — 2026-09-11

The Simulator loop now has a measured candidate/control gate with frame windows,
host CPU, audio underrun counters, save-seed identity, screenshots, and CPU samples.
The normal-reader pointer candidate passed its offline parity gate but failed the
end-to-end gate: 58.416 FPS average and +25 underruns versus 58.817 FPS and +15
underruns for control. The candidate is parked/rejected, the canonical core archive
is restored, and no physical-device install was performed. The remaining performance
defect is still the shared native execution/dispatch path under the seeded late-game
scene; the next loop step is one separately measured candidate there or an opt-in EFB
dispatch trace, not another resolution/logging toggle or vertex-reader rewrite.
