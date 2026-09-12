# GalaxyPad iPad resume note — 2026-09-11

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

Latest merge: PR #2, `2941a9b5d40eb056e2d0e6df2f5c95dfd8578d4b`.
The follow-up Metal probe found median 5.697 ms host wait versus 0.05777 ms
command-buffer GPU execution; copy and handler bodies are small. Next investigate
submission/completion latency, preserving real depth. Whole-EFB caching is rejected
for this scene. Correct-depth audio diagnostic had zero new underruns over its
36.901-second interior interval. See the handoff for scope and exact evidence.


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

## Resumed on the existing Mac Simulator — 2026-09-12

### Decision: removing PGO rejected

The same handoff host with the preserved unprofiled module
`f988f9a78f875f78c2c9ae89f458c2d85785c0e62de4595ef12d1af7734c8b03`
reached the same scene but yielded 38.2/37.3/37.0/38.0 sparse HUD FPS,
versus 45.5/45.5/44.0/45.5 with PGO. CPU snapshots were 102.0–104.4%
and RSS 774,960–775,456 KiB. Reject removing PGO as an improvement.
Evidence: `generated/runtime/ipad-iteration-1/resume-20260912-existing-unprofiled/`.
Canonical PGO module and host artifacts remain unchanged. GalaxyPad was stopped
after the trial; the existing Simulator and MeleePad remain running.

Next performance hypothesis: train the existing instrumented module on this
verified 121-star Observatory route and compare one new profile-use build to
the unchanged PGO control. Prior training came from the wrong opening scene;
current PGO clearly helps but does not establish that its profile is optimal.
Use the same host/module inputs, exact advanced seed, camera, orientation,
resolution and logging-off capture. Never call training/profiling FPS acceptance.
The physical build/install gate remains unmet. The goal is active, not blocked.

### Correct-scene comparison and attribution

On the existing single Simulator, the unchanged control yielded sparse stationary
HUD readings 45.0/45.0/44.0/45.0 emulator FPS. The handoff-fix host with the same
PGO module yielded 45.5/45.5/44.0/45.5. This is no meaningful performance win;
the source guard remains a tested correctness candidate, not a promoted
performance candidate. Both visibly retained Luigi at the same 121-star
Observatory platform, scale 1 and aspect mode 0, with frame logging off.

A separate post-window 8-second CPU sample in
`resume-20260912-existing-candidate/cpu-sample-diagnostic.txt` was processed with
`python3 scripts/summarize-fallback-sample.py <sample> --output <cpu-self-summary.json>`.
Of 6,402 CPU-thread wall-stack samples, 3,397 belong to generated chunks (53.1%),
622 to the host Run symbol (9.7%), 269 to dispatcher (4.2%), and 304 to out-of-line
PPC helpers (4.7%). Largest individual generated function: func_804B60A0, 155
samples. These are conserved self counts, not CPU-time percentages or frame
acceptance. This favors investigating broad native execution/profile coverage
over another tiny vertex-conversion change.

The existing post-run local diagnostic report for control (exported without
sending it) records 778 cumulative DMA underruns, 7 backlog drops and 241.467 ms
maximum producer gap. It includes startup/navigation and is not an audio delta
for the stationary window. Thermal 0 means nominal or unsupported. Continuous
frame-window FPS, frame-tail statistics, emulation-speed percentage and timed
audio deltas remain unavailable in this logging-off capture; no acceptance is
claimed from their absence. Physical installation and saves remain untouched.

The user's continuation is being executed on the sole already-booted iPad
Simulator (`94BACEE0-DE7F-4D31-8097-4F3F0B02C7D1`, same M5 13-inch model).
GalaxyPad uses its own app container; MeleePad was not terminated or modified.
This resolves the prior access assumption without booting a second iPad.

The advanced file is now visually verified: `slot1-details.png` shows 121 stars,
2324 star bits, and Complete; `loaded-scene.png` shows Luigi at the Observatory
central map platform with those counts. Initial HUD reading is 39.0 emu FPS.
Evidence is `generated/runtime/ipad-iteration-1/resume-20260912-existing-control/`.
The logging-off stationary control retains screenshots/process snapshots and
is not instrumented or sampled; startup confirms scale 1, aspect mode 0,
frame_logging 0. Full performance/audio acceptance remains open.

The canonical unattended harness now defaults to the private
`generated/runtime/ipad-iteration-1/advanced-seed/Wii` copy and validates the
exact advanced save hash before any Simulator operation. A deliberate old-seed
attempt exited 1 with `save seed does not match the verified 121-star file`.
It also captures file selection/details and removes the obsolete opening-story
A pulses. The original backups and physical saves were not changed. The harness
still performs diagnostics after its route; it must not be mistaken for a
logging-off unsampled FPS acceptance tool.

## Resume audit and touch handoff fix — 2026-09-12

### Blocked audit — exclusive Simulator access required

On the third consecutive goal turn with this conflict, `xcrun simctl list
devices booted` still reports only MeleePad Netplay iPad booted. GalaxyPad remains
shut down. The handoff candidate and isolation guard have completed their
available offline/UIKit checks; no valid late-game control/candidate comparison
or physical promotion has occurred. `git diff --check` remains clean.
The goal is blocked pending the other task releasing Simulator access. Do not
terminate that unrelated task or bypass the one-iPad limit. Resume from the
prepared advanced-save file selection, verify 121 stars and Observatory, then
measure control before testing/promoting a performance candidate.

### Current stop point: Simulator isolation conflict

The next continuation revalidated that only MeleePad remains booted. The
canonical harness now rejects every unrelated booted Simulator, including when
GalaxyPad is also booted; `GALAXYPAD_ALLOW_OTHER_SIMULATORS` no longer bypasses
the check. The prepared file-select harness has the same guard. A live attempt
with the old override set exited 1 before boot/install/save mutation, as required.
Evidence: `generated/runtime/ipad-iteration-1/resume-20260912-isolation-guard/`.
`bash -n` and `git diff --check` pass. This fixes the harness isolation defect;
it does not establish gameplay performance or prevent another task from booting
a device later. Recheck isolation during any future capture.

The advanced-save control reached file selection, but another task booted
`MeleePad Netplay iPad` during the run. GalaxyPad's dedicated Simulator was
terminated and shut down immediately; only the unrelated MeleePad Simulator
remains booted. Do not restart GalaxyPad while another iPad is booted.
No heavy-scene or candidate/control result was produced, and the candidate
was not installed on the physical iPad.

Prepared seed: `generated/runtime/ipad-iteration-1/resume-20260912-heavy-control/seed-Wii`
contains a copy of the verified `cd8d1fa9…` save; original backups are untouched.
Evidence: `file-select-ready.png`, `save-seed.sha256`, `isolation-conflict.txt`,
and `shutdown.log` in that run directory. File selection shows occupied Mario
slot 1; the star count/Observatory still need direct visual verification.
Next: after the other Simulator is shut down by its owner, use the preserved
`file-select-harness.sh`, select slot 1, inspect its star count, then Play and
verify the Observatory. The initial 30-second A+B hold still showed the title;
a fresh 1-second A+B edge advanced to file selection. Do not reuse the old
opening-story pulse sequence blindly. Only then establish a logging-off
control and compare the isolated handoff candidate using the same PGO module.

The resumed logging-off control exposed an invalid scene assumption: the
unattended harness defaults to `preinstall/Wii`, whose GameData SHA-256 is
`717f7fb3e0749b404adf551332ea0ce457a182c64e17b750bab60b197476e36c`.
This is the original zero-star backup (see `IPAD-FEEDBACK-2026-09-11.md`),
not the later 121-star save. Current screenshots show Star Festival, not the
Observatory. Earlier unattended results using this seed must not be called
late-game heavy-scene acceptance. PGO format validation does not establish
representative late-game training.

Evidence: `generated/runtime/ipad-iteration-1/resume-20260912-baseline/`.
The generated-only acceptance harness disables frame/phase logging and sampling
and stops its startup console stream before the stationary window. Sparse HUD
readings at 0/10/20/30 seconds were 60.0/60.0/59.1/58.2 emulator frame events/s;
these are not a continuous frame-window or display-completion measurement.
Frame-time tails, emulation-speed percentage, guest thermal state, and audio
underrun deltas were unavailable with this logging-off path. Concurrent host
work qualifies all timings. No performance candidate is accepted from this run.

A separate concrete controller/touch defect was reproduced in the UIKit test:
after controller auto-hide clears touch aim, a new screen contact could reclaim
pointer ownership even while controls were hidden. `touchesBegan` now rejects
contacts while `_touchControlsHidden` is true. The regression checks clear,
rejection while hidden, and reacquisition when shown. Before-fix evidence is
`generated/tests/mobile-ui.1e2Lhv` (FAIL: hidden touch controls cannot reclaim
controller aim). The after-fix UIKit run passed all checks, including the new
regression (`generated/tests/mobile-ui.hlNXD7`; wrapper
`resume-20260912-baseline/mobile-ui-after.log`).
Input/controller/settings shell tests pass. This is a
correctness candidate, not a claimed FPS optimization or physical input pass.

Exact artifacts:
- Unchanged control executable: `650bc3b5e34d60ab58d4974d81f934327b4fdbf4d848b33478b3929e717359f8`.
- Selected PGO module: `90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f`.
- Validated profile: `784f47e4904a36319b7805cd7807091d1d486ccc4cacc09f4785636d3949ca54`.
- Isolated handoff candidate executable: `2446fbd5534a6893f406909b385c6dd605abed525eda7c3e9ddc1b5c8e861954`.
- Preserved normalized advanced save: `cd8d1fa98c266aa321dbb018247e5df7a084e5330ffa55f2012df4971b1bc473`.

Build command: `cmake -S apple/ios -B generated/build/ios-simulator-handoff-app
-G Ninja -DCMAKE_TOOLCHAIN_FILE="$PWD/scripts/ios-simulator-toolchain.cmake"
-DCMAKE_BUILD_TYPE=Release`, then `cmake --build
generated/build/ios-simulator-handoff-app --parallel 4`. Ad-hoc signing and
`codesign --verify --deep --strict` passed. Build output is
`resume-20260912-baseline/handoff-build.log`. Control artifacts were not rebuilt.

The physical app was observed alive at PID 9161. The preserved staged bundle
`generated/device-stage.JOtjGn/GalaxyPad.app` passes strict signature verification;
its host/module hashes are `b62abff0c0401ddfd390dbb3efad9124c67a14f4e6873a3b7784caf9ee4da05d`
and `919b2382ebf37007bf86865f1d2f46ca048bec61b45574797483684a039a047b`.
Those are local staged-file hashes, not a readback hash of the installed bundle.
No physical install, save replacement, or physical input test occurred.

Next gate: verify the advanced file and Observatory visually in the sole
Simulator before a matched control/candidate capture. Keep the 120 ms audio
buffer, 4:3 default, module, resolution, and scene fixed. Do not promote this
candidate until the required heavy-scene/audio gate is available and passes.

## Stop point

The latest known-good private iPhoneOS candidate was installed in place on the
physical iPad and relaunched successfully today. The staged bundle is
`generated/device-stage.JOtjGn/GalaxyPad.app`; the current run was alive as
device process PID 8171 when this note was written. Its development signature
passes strict verification. No uninstall, app-data reset, save replacement, or
WBFS change was performed.

The preserved save backups before and after the install have the same SHA-256:
`cd8d1fa98c266aa321dbb018247e5df7a084e5330ffa55f2012df4971b1bc473`.

## Proven this session

- iPad startup defaults to 4:3; explicit 16:9 remains available.
- Frame logging is off by default (`frame_logging=0`).
- The Xbox handoff was captured on the physical device: disconnected
  `hidden=0` → connected `hidden=1` → disconnected `hidden=0`; ownership and
  held input were cleared on each transition.
- The latest Simulator recheck reached the late-game Observatory plaza with
  logging off at 47.3 `emu FPS`. Its bounded sample still points at
  `StaticRecompCore::Run()` and `chassis_dispatch`; this is not an iPad FPS
  result.
- The three-dot menu source fix is present: it blocks gameplay input but is
  runtime-neutral (`pause_runtime=0`). Direct physical open/dismiss gameplay
  continuity and audio behavior still need confirmation.

## Parked candidate

The two-range dispatcher candidate was built and strict-signed, but its
unattended Simulator launch crashed before renderer readiness with
`EXC_BAD_ACCESS` at a null instruction pointer in the candidate module during
runtime startup. It was not installed on the physical iPad. The crash report
is the private macOS diagnostic report `GalaxyPad-2026-09-11-170551.ips`.
Do not promote that candidate without isolating the null indirect call.

## Resume sequence

1. Keep the physical iPad baseline on the staged bundle above. Do not erase
   its app data or replace the advanced save.
2. Directly test the three-dot menu in the fixed heavy scene: opening it must
   not pause or freeze gameplay/audio; the top Pause control is the intentional
   pause path.
3. Reconfirm Xbox connect/disconnect, touch-control visibility, and right-stick
   pointer response (1.2×). Treat the physical device as the acceptance gate.
4. Continue performance work with one measured candidate at a time. Use the
   logging-off matched-scene loop and retain CPU/audio/lifecycle evidence.
5. For unattended Simulator work, resume with:

   ```sh
   GALAXYPAD_SIMULATOR_PROFILE_SECONDS=8 \
   GALAXYPAD_SIMULATOR_FRAME_LOGGING=NO \
   bash scripts/galaxypad-unattended-simulator-loop.sh \
     generated/build/ios-simulator-app/GalaxyPad.app \
     generated/runtime/ipad-iteration-1/<new-run-directory>
   ```

The broader repository gate is not a clean green gate because the private
fixture `generated/thp-kernels-r198-exits/candidate.c` is unavailable. That
limitation, the physical performance cause, and direct three-dot continuity
remain open for the next session.
