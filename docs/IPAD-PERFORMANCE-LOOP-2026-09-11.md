# Physical iPad performance loop — 2026-09-11

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

The current signed GalaxyPad build is running on the iPad with frame logging
off by default. The previous device run already showed the heavy scene falling
to about 32–49 FPS while process CPU reached about 108–111%; turning the optional
frame windows off therefore does not address the main slowdown. The retained
evidence points to guest execution/upstream production pressure, not a starving
RemoteIO callback: requested and delivered audio frames matched, short callbacks
were zero, and backlog drops stayed low while underruns rose.

## Self-audit follow-up — 2026-09-12

No performance fix was promoted during the preceding work window. The latest
logging-off Simulator control reached the same seeded late-game scene with
`render_scale=1`, `aspect_ratio_mode=0`, a 2064x2752 4:3 screenshot, and a
visible 56.4 emulator-FPS counter. Its 8-second host sample contained 4,392
`StaticRecompCore::Run` samples, 4,088 `chassis_dispatch` samples, and 581
`VertexLoader::RunVertices` samples. This is qualified control evidence only:
QEMU and system services continued to consume substantial host CPU.

The host audit identified twelve stale read-only MeleePad `afcclient` transfers
at roughly 92–99% CPU each and terminated only those explicit jobs. The
physical iPad and unrelated Simulators were untouched. The current canonical
Simulator module remains the unprofiled `-O2`/ThinLTO
`generated/build/ios-simulator-fresh-module/gRMGE01_recomp.dylib`; no current
`.profdata` or active-module marker exists. The fresh-module builder now
accepts an optional `GALAXYPAD_PGO_PROFILE` and retains the same unprofiled
default.

The next performance iteration is therefore: obtain a quiet/roomier host,
instrument current AOT inputs, train on the autonomous late-game route, merge
and validate the profile, then run one matched PGO candidate/control pair. A
further micro-optimization or logging toggle is not justified before that
comparison.

## Valid active-scene profile — 2026-09-11

After the physical tap on “Back to Game”, the lifecycle log recorded
`runtime_paused=0`, `menu_presented=0`, and `active=1` at 09:59:35. The live
mirror showed the fixed 121-star Observatory central galaxy-map platform.
With frame logging still off, the retained 10-second CPU Profiler capture
(`generated/runtime/…/resumed-active-20260911/pass-1/cpu.trace`) contained
34,090 CPU/GPU-thread samples. The largest attributed stacks were
`StaticRecompCore::Run()` (3,372 samples), `chassis_dispatch` (1,377),
`Pos_ReadIndex` (1,158), `Normal_ReadIndex<unsigned short, short, 1u>` (907),
`VertexLoader::RunVertices` (724), and `TexCoord_ReadIndex` (685). The
RemoteIO mixer thread accounted for 515 samples, while the main thread had
28, so this capture points first at the CPU/GPU emulation and vertex-loader
path rather than an audio callback stall. The full CPU profile export
completed successfully; the separate thermal-state export exited 139 and is
treated as an Instruments exporter limitation. This is attribution evidence,
not an FPS measurement.

## Loop

1. Reach one fixed heavy scene and leave the visible view unchanged.
2. Visually confirm the scene is active, not the three-dot or app pause panel,
   and pass `--active-scene-confirmed`.
3. Run an unsampled 30-second device-presence window with logging still off.
4. Attach the CPU Profiler for a bounded 10-second attribution sample. Treat
   this as diagnostic only because profiling can perturb timing.
5. Keep the raw `.trace`, process snapshots, and exit statuses even if the
   command-line XML exporter crashes. A successful capture is still useful;
   exporter failure is a tooling limitation, not a game conclusion.
6. Make one source/build change only, install the new private candidate, and
   repeat the same scene. Reject the candidate unless CPU/emulation evidence
   improves without a correctness, audio, or lifecycle regression.

The first offline candidate screen used the available iPhoneOS device compile
database after the Simulator compile database was found missing. The quiet
native-burst differential still passes 5,376 cases, but its full `Run` object
grew from 6,672 to 7,216 bytes of text (+8.3%) under the device policy. That
candidate is rejected before module integration; this is not a gameplay FPS
claim.

The runnable loop is:

```sh
scripts/galaxypad-performance-loop.sh \
  --pid 7869 \
  --scene "current fixed heavy scene" \
  --passes 1 \
  --active-scene-confirmed \
  --wait-for-active \
  --log generated/runtime/ipad-iteration-1/launch-console-pause-panel-logging-off-default.log
```

The `--wait-for-active` mode watches the supplied lifecycle log and begins only
after a new active transition is present. Passing `--log PATH` does not enable
frame logging; the current log still records `frame_logging=0`. The loop retains
before/after device process snapshots and never substitutes a host `ps` reading
for remote iPad CPU data. Use a new output directory for every candidate. The
script never installs, launches, terminates, suspends, or changes GalaxyPad or
its saves.

The earlier paused mirror state (`runtime_paused=1 menu=1`) was deliberately
rejected as a performance sample. It was the explicit Pause panel state, not
the intended three-dot behavior. The three-dot menu is now required to report
`pause_runtime=0` while it blocks gameplay input; the active-scene pass above
is the accepted performance baseline.
The secondary-account Astra Medium audit also confirmed that the current
desktop environment has no supported non-destructive touch-injection route:
QuickTime mirroring is display-only and `devicectl` exposes no physical touch
command. The active-scene gate therefore requires one direct tap on the iPad.
The earlier bounded watcher reached its 600-second limit while waiting for
that physical tap; it is historical diagnostic output only.

## Latest unattended recheck and physical input evidence — 16:42 JST

The logging-off unattended Simulator replay reached the seeded late-game
Observatory plaza without operator input. Its screenshot is
`generated/runtime/ipad-iteration-1/simulator-r915-recheck-20260911-163729/scene.png`;
the on-screen `emu FPS` counter read 47.3. The bounded 8-second sample
attributed 4,263 samples to `StaticRecompCore::Run()` and 3,990 to
`chassis_dispatch`, with the remaining work spread across generated code and
vertex readers. The Simulator result is a candidate-attribution and route
check only, not a physical-iPad FPS measurement.

The physical console excerpt at
`generated/runtime/ipad-iteration-1/controller-hotplug-console-20260911.log`
now proves the hot-plug contract: controller connect logged
`connected=1 ... hidden=1`, and disconnect logged `connected=0 ... hidden=0`.
The app was relaunched without the console attachment as PID 8160 after the
device service was released; the save backup hash remained
`cd8d1fa98c266aa321dbb018247e5df7a084e5330ffa55f2012df4971b1bc473`.

## Candidate under test — normal indexed reader

The active profile identified `Normal_ReadIndex<unsigned short, short, 1u>` as
a measured hot path. A device-policy differential retained the existing
500,000-case parity test and reduced that isolated symbol from 63 to 55
instructions (object text 12,236 to 12,036 bytes). The private candidate
archive and signed app are staged under
`generated/runtime/ipad-iteration-1/performance-loop-20260911/normal-reader-candidate-20260911b/`.
The candidate is not considered effective until it is installed in place and
the same active scene is profiled with no lifecycle, audio, visual, or save
regression.

That first device package was subsequently audited before accepting its result:
the `VertexLoader_Normal.cpp.o` member in the staged archive was byte-identical
to the baseline member, so the 63-to-55 isolated probe did not reach the app.
It is rejected as a performance candidate and supplies no device comparison.
The loop has been reoriented to the unattended Simulator route documented in
`docs/GALAXYPAD-GOAL-LOOP.md`; the physical iPad remains reserved for the final
candidate install/acceptance pass. The first complete manual verification of
that route used a 30-second title A+B hold, pointer-based file selection and
Play, then 30 A pulses through the opening story. It reached the late-game
plaza at
`generated/runtime/ipad-iteration-1/simulator-reorientation-unattended-plaza-manual.png`
with logging off and showed 48.2 FPS in the on-screen counter. This is a
Simulator reachability and diagnostic baseline, not a physical-iPad FPS claim.
The repeatable script now uses that 30-second title hold and emits
`input-route.log` alongside the screenshot and bounded host `sample` profile.
For targeted attribution, set
`GALAXYPAD_SIMULATOR_EFB_TRACE=/absolute/output/efb-trace.csv`; the script
passes that opt-in path to the Simulator and clears it on exit. The trace
contains EFB read coordinates, guest PC/LR, and elapsed time, so the next
candidate can separate pointer-related depth waits from broader rendering
work without changing behavior.

The trace-enabled replay produced 10,365 depth-read rows after the Simulator
app was terminated to freeze the file. The whole launch-to-profile window had
a 1.242 ms mean and 11.391 ms maximum read duration; 648 reads exceeded 5 ms
and 6 exceeded 10 ms. Reads clustered at `(0,0)` and `(520,377)`, with a
smaller `(212,270)` group, and the two verified guest callers were LR
`0x80385be0` and `0x8029e6e4`. Because this includes route startup and the
bounded profile rather than a stationary-only interval, it is diagnostic
evidence for the next experiment, not a new FPS or device claim.

## R915 indexed position/texture candidate — measured improvement, device smoke

R915 specializes only the common `N == 3` indexed position and `N == 2`
indexed texture readers in `VertexLoader_Position.cpp` and
`VertexLoader_TextCoord.cpp`; all other template cases retain their original
loops and the position-cache behavior is unchanged. It was built in an
isolated iPad Simulator core and linked into a private app. With the 64-tile
EFB configuration, logging off, the same save seed and the same automated
route, the forward pair measured candidate `54.4 FPS` versus control `52.7
FPS`; the reverse-order pair measured candidate `50.0 FPS` versus control
`47.3 FPS`. Both pairs reached the same late-game plaza. The raw CPU samples
still show `StaticRecompCore`, `chassis_dispatch`, and synchronous EFB depth
waits, so this is a bounded end-to-end gain, not evidence that the EFB stall
has been solved. Artifacts are retained under
`generated/runtime/ipad-iteration-1/vertex-r915-*`.

The candidate was then rebuilt for `iphoneos`, signed with the same development
identity/profile as the protected baseline, and installed in place. The
device launched the fresh module and reported `frame_logging=0` on the first
smoke, followed by an opt-in logging run. In the active scene the iPad logged
roughly `59.8–60.0 FPS` at render scale 1, `efb_depth_peeks=7007` and
`efb_total_peek_ms=2261.174` over the retained window, while cumulative audio
underruns stayed at `3`, requested and delivered frames matched, and short
callbacks stayed at `0`. This is useful physical startup/active-scene evidence
but not heavy-scene acceptance: no unattended physical input path exists to
recreate movement or the three-dot gesture. The candidate remains installed
for observation; no claim of final device performance or pause acceptance is
made.

R915 is kept as the current measured candidate. The next loop step is a
physical comparison only when the fixed heavy scene can be reached through a
real touch/controller action, or an additional unattended Simulator candidate
targeting the measured `StaticRecompCore`/dispatch path. Do not change EFB
semantics based on the readback stack alone.

## Unattended R911 normalization differential — parked

The whole-normalization candidate passed the offline gate: 261,120 complete
routine CPU-state/memory/callback/FPSR comparisons and 69,120 callback cases.
The private Simulator module is
`generated/build/ios-simulator-normalization-r911/gRMGE01_recomp.dylib`
(SHA-256 `c2ebd795db9d0a414d368f37f23558968ccc3a571ffab39d9ba10de2193240d9`),
against control module
`generated/build/ios-simulator-fresh-module/gRMGE01_recomp.dylib`
(SHA-256 `f988f9a78f875f78c2c9ae89f458c2d85785c0e62de4595ef12d1af7734c8b03`).

The first same-host pair both reached the seeded late-game plaza with logging
off: candidate `50.0 FPS` and control `49.1 FPS`. Their bounded samples were
effectively the same (`StaticRecompCore::Run` 5,435 vs. 5,458;
`chassis_dispatch` 5,097 vs. 5,152; EFB depth waits 589 vs. 587). A
reverse-order control also completed (`StaticRecompCore::Run` 5,530), while a
reverse-order candidate replay exited before the renderer-ready signal. Its
console log contains normal startup and no GalaxyPad crash/dyld report; it has
no screenshot or profile. A subsequent control replay completed again, so the
candidate is rejected/parked rather than installed on the physical iPad.

The accepted unattended control artifact is
`generated/runtime/ipad-iteration-1/normalization-control-r911c/`; the failed
candidate artifact is retained at
`generated/runtime/ipad-iteration-1/normalization-candidate-r911b/`. The
dedicated GalaxyPad Simulator is the only surface the loop may automate; an
unrelated already-booted Simulator was preserved and is recorded in each
output, so comparisons made while it is booted are host-pressure-qualified.
Future failed runs also retain `failure-state.log` with the Simulator state,
launchd/PID state, and console tail.
The next iteration must target the measured shared execution/dispatch path and
must pass the same unattended route before any physical install is considered.

## Current interpretation

- Render resolution is not the leading lever: the earlier heavy scene was
  already measured at render scale 1.
- The three-dot menu is input-only host UI. It blocks gameplay input while
  open but must not pause the emulated CPU or audio clock. Only the app Pause
  panel, modal UI, or lifecycle interruption may request a runtime pause.
- The controller pause path now presents an app-style pause panel. “Back to
  Game” resumes; holding Start + is reserved for the original Wii-style pause
  screen and its Return to Observatory action.
- The next performance candidate should come from the measured shared native
  execution path, not another logging toggle, resolution guess, audio-buffer
  tweak, or unchanged profiler retry. The Simulator sample likewise points at
  `StaticRecompCore::Run`, `chassis_dispatch`, and
  `FramebufferManager::PeekEFBDepth`/Metal staging; it is useful for
  candidate attribution but does not replace the physical profile.
- Before changing EFB behavior, collect one opt-in EFB dispatch trace on the
  unattended late-game route and compare its wait distribution and guest PCs
  with the physical profile. No EFB semantics change is accepted from the
  stack name alone.

All loop artifacts stay under private `generated/` output. Saves, disc data,
signing material, and raw private device logs are not publication artifacts.

## Current UI/aspect correction — 2026-09-11

The latest exact private iPad install reports `aspect_ratio_mode=0` and a
normalized viewport of `{{0, 0.013671875}, {1, 0.97265625}}`, so the default
device presentation is 4:3 with small top/bottom letterboxing. Invalid saved
aspect values now safely resolve to 4:3; 16:9 remains an explicit Display
menu choice. The three-dot menu host gate is explicitly input-only and cannot
request a runtime pause; both top controls were lowered by 8 points.

The build was installed in place with the same app database UUID and a
byte-identical pre-install save backup. Focused UIKit, controller, and
strict-signature checks pass. Physical menu/controller/touch confirmation is
still pending because this desktop has no supported unattended hardware-input
route; the next device interaction should check that gameplay continues while
the three-dot menu is open and that touch/controller input returns after it is
dismissed.

The follow-up build also defaults automatic touch-control hiding on for a
connected controller, logs `connected/auto_hide/hidden` on each reconciliation,
and increases right-stick pointer response from 0.8× to 1.2×. Its fresh device
launch logged `connected=1 auto_hide=1 hidden=1`. Performance logging remains
off for normal play; the established physical evidence still points to
CPU/emulation production pressure and audio underruns, so this UI/input pass
does not claim a performance improvement.

## Unattended normal-reader differential — rejected — 2026-09-11

The next bounded experiment targeted the measured `Normal_ReadIndex`/vertex-loader
path. `ReadIndirect` kept its input cursor, cache writes, and conversion semantics,
but used a local output cursor and one final shared-cursor commit. The offline probe
passed 500,000 normal conversions with matching output bytes, caches, cursor, and
guards. The isolated object changed from 12,236 to 12,036 bytes of `__text`; the
candidate core archive is
`generated/ios/iphonesimulator/normal-pointer/libGalaxyPadCore.a`
(SHA-256 `311e3ff59ec7eb410877c5e8756f245a13da62dbfccd35320c53f75cdca54c3b`).

The candidate and control were run through the same unattended seeded route on the
dedicated iPad Pro 13-inch M5 Simulator with frame logging enabled, render scale 1,
and the same save seed (`717f7fb3e0749b404adf551332ea0ce457a182c64e17b750bab60b197476e36c`).
The candidate captured 19 frame windows at 58.416 FPS average, 47.545 FPS minimum,
and 71.29% average host CPU; audio underruns rose from 2 to 27. The control captured
18 windows at 58.817 FPS average, 45.470 FPS minimum, and 69.17% average host CPU;
underruns rose from 3 to 18. The candidate's one slightly better worst FPS window
does not outweigh its higher average CPU and larger underrun increase, so it is
rejected and not promoted.

Full evidence is retained privately at
`generated/runtime/ipad-iteration-1/simulator-normal-pointer-candidate-logging-20260911/`
and
`generated/runtime/ipad-iteration-1/simulator-normal-pointer-control-logging-20260911/`.
The canonical core archive was restored to the baseline after the run, and the
physical iPad was not touched.

## Unattended dispatcher lookup differentials — rejected — 2026-09-11

Two smaller experiments then targeted the shared verified-chunk lookup. A
page-sized table with two candidates per page exposed an initial fallback bug:
the `0xA0`-offset chunk boundaries put adjacent chunks on the same pages, and
the first single-slot version fell back to a 1,322-range scan. Its 20-window
capture fell to 20.058 FPS average with +263 underruns. The corrected two-slot
version avoided that scan but still measured 50.186 FPS average, 38.910 FPS
minimum, and +171 underruns, so the entire page-table route is rejected.

A 16-bit per-instruction table kept the original direct-index hot path and
reduced the lookup footprint without the page checks. It measured 56.008 FPS
average, 25.663 FPS minimum, and +68 underruns in 20 windows, also worse than
the baseline control. Its private archive is
`generated/ios/iphonesimulator/lookup16/libGalaxyPadCore.a`
(SHA-256 `dd295c1bf0517d50d68aad9921043732498c9884af04c6132906a109b1f010fb`).
Both lookup candidates are rejected and the canonical archive/app were restored
to the baseline. Private captures remain under
`generated/runtime/ipad-iteration-1/simulator-page-cache-candidate-logging-20260911/`,
`generated/runtime/ipad-iteration-1/simulator-page-cache-candidate-fixed-logging-20260911/`,
and
`generated/runtime/ipad-iteration-1/simulator-lookup16-candidate-logging-20260911/`.

## R915 attribution correction — 2026-09-11

The earlier R915 position/texture source claim is historical evidence only. A
later archive-member audit found the candidate and baseline
`VertexLoader_Position.cpp.o` and `VertexLoader_TextCoord.cpp.o` members were
byte-identical. Therefore the earlier FPS spread cannot be attributed to those
source changes; no R915 performance promotion is justified. The physical smoke
and UI/controller fixes remain documented separately, while the performance
loop continues from the baseline shared execution path.

## Final private label build — 2026-09-11 16:30 JST

The latest host rebuild is installed and running as PID 8142. The gameplay HUD
now calls the counter `emu FPS`; it is the existing frame-event rate and not a
display-completion measurement. Startup still reports `frame_logging=0`, 4:3,
and controller auto-hide enabled. This pass changes no performance path; the
slowdown and audio-underrun investigation remains the next performance loop
target.

## Baseline EFB trace attempt — diagnostic only — 2026-09-11

The baseline was replayed through the same unattended seeded Simulator route
with `GALAXYPAD_SIMULATOR_EFB_TRACE` enabled. The private output is
`generated/runtime/ipad-iteration-1/simulator-baseline-efb-trace-20260911/`.
No `efb-trace.csv` was created, and the runtime counters stayed at zero for
color peeks, depth peeks, total/max peek time, frames containing peeks, and
peaks per frame. The captured route therefore did not exercise the EFB peek
path; this is evidence that EFB readback is not implicated in this route, not
proof that every game scene is EFB-free.

The same run still showed the shared performance failure: the late window
declined to 46.414 FPS with a 295.192 ms maximum frame gap and seven gaps at
or above 33 ms (three at or above 100 ms). DMA underruns rose from 2 to 23,
while requested and delivered audio callback frames remained equal and
`output_short_callbacks=0`. No source or canonical artifact was changed by
this diagnostic attempt; the baseline archive and Simulator app remain
restored, and the physical iPad was not touched.

## DMA phase correlation — diagnostic only — 2026-09-11

The harness now accepts `GALAXYPAD_SIMULATOR_PHASE_TRACE` for a separate
phase-event capture and retains the filtered runtime log. The baseline trace
at `generated/runtime/ipad-iteration-1/simulator-baseline-phase-trace-20260911/phase.csv`
contains 73,451 events, including 43 DMA underruns, 24,956 DMA enqueues, and
5,967 frame-end events. It is trace-on evidence only; its file writes are not
used for an FPS comparison.

The ordering is nevertheless actionable. Enqueue gaps of 59.040, 114.069,
and 188.675 ms contain the first four underruns, with the queue falling to
two entries. Later underruns recur while enqueue gaps are 10–28 ms and the
queue is already between two and six entries. The maximum enqueue gap is
223.194 ms, the maximum frame-end gap is 441.205 ms, and no queue-full drop or
short output callback occurs. This ties starvation to the guest DMA producer
falling behind under CPU pressure, not to CoreAudio delivering short buffers.
The next performance candidate must therefore target the shared guest/AOT
execution cost or its scheduling boundary; changing audio output policy would
hide the symptom rather than address the measured cause.

## Prebuilt C-loop budget probes — not a valid differential — 2026-09-11

The prebuilt `generated/build/ios-simulator-loop1024-module/gRMGE01_recomp.dylib`
(SHA-256 `b297074484e49d1bed972e33530b239495c50b9d140aef5da09769d748cd7e42`)
captured 20 windows at 57.295 FPS average, 38.455 FPS minimum, 72.53% average
CPU, and 48 cumulative DMA underruns. The prebuilt 512 variant captured 19
windows at 58.055 FPS average, 44.815 FPS minimum, 69.05% average CPU, and
27 underruns. The matched telemetry baseline captured 19 windows at 58.540
FPS average, 47.170 FPS minimum, 68.46% average CPU, and 23 underruns.

Both prebuilt variants were configured without the baseline module's ThinLTO
flag, so these runs are package regressions, not valid C-loop-budget-only
comparisons. They are rejected as candidates and do not establish the budget
effect. Evidence is retained under
`generated/runtime/ipad-iteration-1/simulator-loop1024-candidate-20260911/`
and
`generated/runtime/ipad-iteration-1/simulator-loop512-candidate-20260911/`.
No module selection or physical install changed.

## ThinLTO C-loop budget 1024 — rejected — 2026-09-11

A fair budget-only candidate was built from the baseline module graph with
ThinLTO preserved and `DOLRECOMP_C_LOOP_CYCLE_BUDGET=1024`.
`generated/build/ios-simulator-loop1024-ipo-module/gRMGE01_recomp.dylib`
has SHA-256
`554e278875d719121e72ff5ac32115d723a4e5225ff996043b99d7de8df35b38`.
On the same seeded route it captured 19 windows at 58.080 FPS average,
44.999 FPS minimum, 43.644 FPS minimum observed, 69.925% average CPU, and
33 cumulative DMA underruns. The matched telemetry baseline captured 19
windows at 58.540 FPS average, 47.170 FPS minimum, 39.095 FPS minimum
observed, 68.461% average CPU, and 23 cumulative DMA underruns.

The ThinLTO-preserving 1024 candidate is therefore rejected: it is slower on
average, has a worse measured window minimum, uses more CPU, and produces ten
more cumulative underruns. The canonical module remains the only selected
Simulator candidate; no physical-device install changed. Evidence is retained
under
`generated/runtime/ipad-iteration-1/simulator-loop1024-ipo-candidate-20260911/`.

## ThinLTO C-loop budget 512 — rejected — 2026-09-11

A second fair budget-only candidate was built from the same baseline module
graph with ThinLTO preserved and `DOLRECOMP_C_LOOP_CYCLE_BUDGET=512`.
`generated/build/ios-simulator-loop512-ipo-module/gRMGE01_recomp.dylib`
has SHA-256
`ab1bb51066fd23e1be5e086a402ccd10fc1120a2d9883fd6316202f035cf0b6f`.
On the same seeded route it captured 19 windows at 58.632 FPS average,
47.883 FPS minimum, 46.365 FPS minimum observed, 69.542% average CPU, and
25 cumulative DMA underruns with three backlog drops. The matched telemetry
baseline captured 19 windows at 58.540 FPS average, 47.170 FPS minimum,
39.095 FPS minimum observed, 68.461% average CPU, and 23 cumulative DMA
underruns with two backlog drops.

Although the 512 candidate's frame-rate summary is slightly higher, it uses
more CPU and worsens the measured audio starvation counters. It is rejected as
the overall performance candidate; the canonical module remains selected and
no physical-device install changed. Evidence is retained under
`generated/runtime/ipad-iteration-1/simulator-loop512-ipo-candidate-20260911b/`.

## Run-cost CPU census — diagnostic only — 2026-09-11

The existing opt-in `GALAXYPAD_RUN_COST` census was exercised in a temporary
diagnostic build. Periodic reporting was added so the result could be captured
before a bounded Simulator run was terminated, but that reporting itself
regressed the normal disabled path: the replay fell to 57.880 FPS average,
75.14% average CPU, and 43 cumulative DMA underruns. The periodic-reporting
change was reverted and the canonical app/core were rebuilt; the unattended
harness no longer exposes this diagnostic-only path.
The retained run is
`generated/runtime/ipad-iteration-1/simulator-baseline-run-cost-20260911b/`.
That temporary build recorded 12.002 seconds of CPU-thread time; the final
cumulative sampled totals extrapolate to about 9.744 seconds of native
execution (81.19%) and 0.123 seconds of non-native routing (1.03%). The
remaining CPU time is outside the two selected lanes and the estimate is
intentionally coarse because of random sampling. This attribution remains
useful, but it is not evidence that the current canonical build includes
periodic reporting or that performance improved.

This materially lowers the priority of interpreter/fallback routing as the
cause of the observed slowdown. The measured hotspot remains native generated
execution (`StaticRecompCore::Run` -> `chassis_dispatch`, led by
`func_805170A0` in the matching CPU sample), while the phase trace already
linked audio starvation to guest-producer gaps. The census is attribution only,
not an FPS or audio-acceptance run; no module selection or physical install
changed. A post-revert replay was also retained, but host pressure included an
unrelated QEMU process above 100% CPU and other workloads, so it is qualified
evidence rather than a clean baseline comparison.

## Post-rebuild Simulator contract and hotspot guard — 22:26 JST

The canonical rebuilt app completed a three-second unattended Simulator route
with logging off and was terminated only on the dedicated iPad Pro 13-inch M5
Simulator. Startup logged `aspect_ratio_mode=0` and `frame_logging=0`; the
captured 2064x2752 screenshot shows the 4:3 gameplay viewport with the expected
letterbox. The run also saved `host-top-before.log` and `host-top-after.log` so
future FPS/audio comparisons can qualify concurrent host load. At capture time,
the unrelated Android QEMU process exceeded 100% CPU, so this run is a contract
check and not a clean performance comparison.

A measured ARM64 branch-hint candidate for the already-hot vertex cache paths
was rejected before integration: `VertexLoader_Normal.cpp.o` grew from 12,236
to 12,856 bytes of text and `VertexLoader_Position.cpp.o` grew from 6,456 to
7,116 bytes. The hints were reverted; the canonical source/archive remains
unchanged by this experiment. Focused mobile, controller, audio, EFB, CPU
profile, run-cost, syntax, and diff checks pass. The full repository check is
still blocked only by the previously documented missing private fixture
`generated/thp-kernels-r198-exits/candidate.c`.

## Packed texture-coordinate candidate — rejected — 23:04 JST

Secondary Astra Medium identified the u16-indexed, signed-16 two-component
texture-coordinate converter as a bounded candidate from the retained CPU
sample (159 leaf observations). The temporary ARM64 implementation read the
two adjacent components with one exact-width four-byte load and preserved the
ordered writes. Its targeted object shrank by 12 bytes of text with no calls
or spills, and its Simulator route reached the normal seeded late-game scene.

The candidate did not clear the runtime gate. In matched five-second phase
traces it recorded 19 DMA underruns versus 18 for control; in the final five
seconds it completed 231 frames versus 253 for control. It was reverted, the
canonical source/core/app were rebuilt, and the canonical module remained
selected. The phase traces are retained under
`generated/runtime/ipad-iteration-1/simulator-texcoord-packed-candidate-phase-20260911/`
and
`generated/runtime/ipad-iteration-1/simulator-texcoord-packed-control-phase-20260911/`.

## Dispatcher duplicate-PC-store candidate — rejected — 23:18 JST

The generated dispatcher candidate removed the duplicate `ctx->pc = address`
store from its private original-call helper; the enclosing dispatcher already
writes the address and is the only caller path. The candidate module passed
the static gate with an 8-byte `__text` reduction.

The runtime gate failed in matched five-second phase traces: 252 terminal
frames and 19 DMA underruns for the candidate versus 256 frames and 17
underruns for the canonical module. The candidate was not promoted. Evidence
is retained under
`generated/runtime/ipad-iteration-1/simulator-dispatch-pcstore-candidate-phase-20260911/`
and
`generated/runtime/ipad-iteration-1/simulator-dispatch-pcstore-control-phase-20260911/`.

## Menu-inclusive diagnostic recheck — 2026-09-11 23:28 JST

The host logger was rebuilt so opt-in five-second frame windows remain eligible
while the three-dot UIMenu is open. The menu still blocks gameplay input, but
its source path does not request a runtime pause; explicit pause/modal UI
continues to be excluded by `pause_requested` and the paused-state check. The
window record now includes `native_menu`, `ui_blocked`, and `pause_requested`
state fields. Normal gameplay still defaults to `frame_logging=0`.

The rebuilt canonical app completed the unattended seeded route on the
dedicated iPad Pro 13-inch M5 Simulator with the save seed hash
`717f7fb3e0749b404adf551332ea0ce457a182c64e17b750bab60b197476e36c`.
Eighteen diagnostic windows averaged 59.109 frame events/s, with a 49.058
lowest window and a 23.998 lowest one-second observation. The late windows
degraded while unrelated host work was active, including Android QEMU above
100% CPU and concurrent `afcclient` processes; this is qualified evidence, not
a clean performance comparison.

Audio delivery recorded zero short output callbacks. DMA underruns rose from 1
to 14 in the final window, with two backlog drops and a 98.728 ms maximum guest
producer gap. The phase trace contained 24,585 DMA enqueues, 20 underruns, and
2 backlog drops; the runtime counters recorded a 291.298 ms maximum frame gap,
5 gaps at or above 33 ms, and 2 at or above 100 ms. EFB counters remained zero.
This repeats the guest-producer starvation signature and does not identify a
new source-level performance candidate. The canonical module/app remain
selected and the physical iPad was not touched.

## Self-audit and `-O3` candidate — 2026-09-11

The current performance issue remains open. The completed work in this pass
established that logging is not the primary cause: a logging-off route still
placed the CPU-GPU thread in `StaticRecompCore::Run` and `chassis_dispatch`.
The same route also ran while unrelated Android QEMU, `afcclient`, and
MacDroid processes consumed substantial host CPU, which prevents treating the
Simulator FPS as a clean hardware comparison.

The next bounded build-level candidate was generated-module `-O3` against the
canonical `-O2` module. The AOT inputs were unchanged; module `__text` fell
from 104,055,996 to 103,684,132 bytes (371,864 bytes). In matched seeded
Simulator routes with identical diagnostic settings, `-O3` measured 56.730
versus 56.987 frame events/sec for `-O2`; average process CPU was 73.247%
versus 75.615%, while phase-trace DMA underruns were 70 versus 70 and backlog
drops 6 versus 6. Because it did not improve frame pacing or audio under the
qualified host load, it was rejected and the canonical `-O2` module remains
selected.

This is a stopping rule for the current micro-optimization lane: the next
iteration needs a clean matched baseline and exclusive-cost attribution, or a
separately authorized physical heavy-scene capture. More logging or another
small dispatcher/code-size edit is not evidence of progress by itself.

## Self-audit follow-up — 2026-09-12

The audit of the preceding work window found no promoted performance change.
No commit was made; the tracked edits are diagnostics, UI/default behavior,
the unattended harness, and documentation. The generated-module `-O3`
candidate and the earlier loop-budget, lookup, vertex-reader,
texture-coordinate, and dispatcher candidates remain rejected or parked, so
the canonical module is still `-O2`.

The decisive evidence is still one level short of a root cause. Logging-off
sampling places the CPU-GPU thread in native generated execution, and DMA
underruns occur with guest-producer enqueue gaps; CoreAudio has zero short
callbacks. However, `RunCost` is inclusive and the phase logger writes a
mutex-protected file, so neither can assign the starvation interval to guest
compute, Metal/presentation, or host scheduling. The host was also carrying an
Android QEMU process, many `afcclient` transfers, and compiler work.

The unattended harness now has an opt-in System Trace attach for the required
timestamped scheduler capture. The first attempt using `spindump` was rejected
by macOS because live capture requires root (exit 77). The unprivileged
`xctrace --template 'System Trace' --attach <Simulator-PID>` attempt reached
the stationary scene but returned `Cannot find process for provided pid`
(exit 21). Both are tooling failures; no performance conclusion is drawn from
them. The GalaxyPad Simulator process was terminated after the failed capture,
and the physical iPad, saves, and unrelated Simulators were untouched.

Next gate: two stationary captures on a quiet host with timestamped stacks and
scheduler state, or a separately authorized physical Instruments capture. Only
then should a code lane proceed, and only if it explains at least 60% of the
combined underrun-gap duration consistently.
