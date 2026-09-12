# GalaxyPad status

Last updated: 2026-09-12

## 2026-09-12 performance gain, hardware feedback and Start fix

The current private iPad candidate is installed and running. Matched Simulator
gameplay improved from roughly 44 to 58 frame events/s; separate audio diagnostics
recorded zero new underruns versus 157 in the control. The user reports stability
but continuing slowdowns and unreliable Xbox Start/Menu. A subsequent source fix
preserves queued button-event edges and passes an old-fails/new-passes regression;
physical retest remains due. A new physical report says the dome Pull Star cannot
be activated, blocking galaxy selection; reproduction is in progress. This supersedes the historical candidate identities
below. See [the current handoff](PERFORMANCE-2026-09-12.md) for exact hashes,
preservation differences, architecture limits and evidence. **Not release-ready.**

## 2026-09-11 end-of-session candidate installed

Reinstalled the latest known-good strict-signed private iPhoneOS bundle
`generated/device-stage.JOtjGn/GalaxyPad.app` in place on the physical iPad
and relaunched it successfully; the current process was PID 8171. The save
backups before and after installation remain byte-identical, and no app-data,
save, or WBFS reset was performed. The two-range R916b module experiment is
parked after a Simulator null-instruction-pointer crash before renderer
readiness; it was not installed on the iPad. See
`docs/RESUME-2026-09-11-GALAXYPAD-IPAD.md` for the next-session sequence.

## 2026-09-11 physical controller hot-plug proven

The exact physical iPad console log now proves the requested Xbox handoff:
`connected=0 ... hidden=0`, then `connected=1 ... hidden=1`, then
`connected=0 ... hidden=0`, with ownership changing 0 → 1 → 0 and input
cleared on each transition. The raw private excerpt is retained at
`generated/runtime/ipad-iteration-1/controller-hotplug-console-20260911.log`.
The console attachment was released, the same app was relaunched without
uninstalling or changing its save, and it is currently PID 8160. The post-
release backup matches the pre-release SHA-256. Three-dot continuity and
heavy-scene performance remain open.

The latest unattended logging-off Simulator recheck reached the seeded plaza
at 47.3 emu FPS; its 8-second sample still shows `StaticRecompCore::Run()` and
`chassis_dispatch` as the principal attribution. This is not an iPad FPS
claim and no new performance fix is claimed from it.

## 2026-09-11 final private host rebuild installed

The latest iPhoneOS host rebuild is strict-signed and installed in place on
the iPad as PID 8142. The HUD now identifies the existing frame-event counter
as `emu FPS`; startup still reports 4:3, `frame_logging=0`, and
`connected=1 auto_hide=1 hidden=1`. The app database UUID and save state were
preserved. This pass does not claim a performance gain; the CPU/emulation and
audio-underrun investigation remains open, with physical disconnect/reconnect
and three-dot continuity awaiting direct confirmation.

## 2026-09-11 controller visibility and native-menu correction

The newest exact iPad install fixes the half-second native-menu pause window
caused by the generic `presentViewController:` override. The three-dot UIMenu
now blocks gameplay input but cannot request a runtime pause. Touch controls
default to hiding when an extended controller connects and reappear on the
disconnect reconciliation path; the current launch logged
`connected=1 auto_hide=1 hidden=1`. Right-stick pointer response is now 1.2×.
Focused controller/UIKit checks, strict signing, in-place installation, and
4:3 logging-off launch evidence pass. Physical disconnect/reconnect and
pointer comfort remain open; performance is still separately limited by the
measured CPU/emulation and audio-production pressure.

## 2026-09-11 iPad aspect and menu correction

The latest exact private device build is installed in place. Startup reports
`aspect_ratio_mode=0` and `frame_logging=0`; the iPad normalized viewport is
`{{0, 0.013671875}, {1, 0.97265625}}`, confirming 4:3 with top/bottom
letterboxing. Invalid saved aspect values now also fall back to 4:3, while
16:9 remains an explicit Display choice.

The three-dot host gate is input-only and explicitly forces `pause_runtime=0`;
the top Pause panel remains the intentional runtime pause. Menu dismissal now
releases the gate synchronously, and both top controls are 8 points lower.
The exact install preserved the app database UUID and a byte-identical save
backup. Focused UIKit/controller/signature checks pass; physical menu,
controller, touch, and cursor confirmation remains open.

## 2026-09-11 unattended Simulator performance lane

The active loop is now autonomous when the operator is away:
`scripts/galaxypad-unattended-simulator-loop.sh` installs the private
Simulator app, seeds only the private Wii save, waits for renderer readiness,
holds title A+B for 30 seconds, selects file 1 and Play by pointer, advances
the opening story with bounded A pulses, captures the late-game plaza and
profiles with frame logging off. A clean replay reached the plaza and showed
51.0 FPS on-screen. The earlier five-second attempt correctly proved input
consumption but failed the unusually slow title transition; it is retained as
a harness-timing defect, not an input-bridge defect.

An opt-in `GALAXYPAD_SIMULATOR_EFB_TRACE` path now exposes the existing EFB
read trace. The trace-enabled run recorded 10,365 depth reads, 1.242 ms mean,
11.391 ms maximum, and 648 reads over 5 ms across the launch-to-profile
window. This is diagnostic only. The physical iPad remains installed at the
known-good logging-off baseline and is reserved for final device acceptance;
no physical touch injection is available from the current desktop route.
The next lowest step is one stationary late-scene EFB/caller comparison, then
one semantics-preserving candidate only if the wait cost is confirmed.

The R911 whole-normalization candidate then passed 261,120 complete-routine
comparisons and 69,120 callback cases, but did not improve the unattended
late-game profile. The first matched pair read 50.0 FPS for the candidate and
49.1 FPS for control, with effectively identical `StaticRecompCore::Run`,
`chassis_dispatch`, and EFB-wait sample counts. A reverse-order candidate
replay stopped before renderer readiness while a subsequent control replay
completed. The candidate is parked and was never installed on the physical
iPad. See `docs/IPAD-PERFORMANCE-LOOP-2026-09-11.md`; the next candidate must
come from the measured shared execution/dispatch path and pass the unattended
Simulator route before hardware consideration.

## R915 local installation assistant

Double-click Install on iPad.command: native dialogs export the hash-pinned
private IPA, install a signed app, or open help. README/INSTALL_IPAD.md updated.
Final local IPA: generated/ipad-install.7z6b20r8/GalaxyPad-private-unsigned.ipa.
Archive CRC/layout/binary parity pass; four installer fixture checks pass and
native menu/Cancel verified. Actual signing/install is untested (no device or
identity). Full suite R914 passed before installer addition. No release claim.

## R913 physical test candidate staged

Release build11885 and private stage60036 exited0. New unsigned candidate:
generated/device-stage.ZaTANc/GalaxyPad.app, host
27b37908b9884d2ece7f064772127d11bc073de52cdc43cff25f1223ab8a3753,
unchanged device module48f455ebc33f8eb2fc58151cd722ea756db77a5738a9573a0a49f0c656110041.
Includes R912 report improvements; physical IOS/min16/sdk26.5 and icon/module
staging checks pass. Settings/import activation/SDK-selection regressions pass.
Not signed, installed or hardware-tested. Earlier stages preserved. Full PRD open.

## R912 device-test diagnostic preparation

Local mobile reports now identify Simulator/device, OS, thermal/low-power state
and available cumulative DMA audio counters. Misleading presentedFrames label
is replaced by frameEvents/after_frame_event with explicit non-presentation and
non-timed-window caveats. Device and Simulator main.mm compile with warnings as
errors; existing redaction/report tests pass. Source change only: existing R884
unsigned device stage does not include it yet. No hardware or FPS acceptance.

## Current performance priority — R911

Private R910 Simulator module linked successfully and ran on the single
iPad Simulator in R911. Existing save hash remains99d432d5. A read-only debugger
sample confirms43,442,348 fast calls and18,218,166 rejections across startup/file
selection/story; this is mixed-scene eligibility, not gameplay timing. Actual
same-scene baseline/candidate measurement is still pending. No FPS gain claimed.
Runtime stopped, original host restored; timing attempt invalid because SIGTERM
did not export VI/work CSVs. Physical baseline preparation is now prioritized
when a device/signing is available. See PHYSICAL-IPAD-FIRST-TEST.md and
NORMALIZATION-IPAD-R911.md. No gain or ship-readiness claimed.

Whole normalization vector candidate clears ordinary-input complete-routine
cost (~40–44% faster), with rejection penalties explicitly measured. Expanded
state/observer/status and known-result fixtures pass. Private Simulator link
34260 exited0; candidate d966417b is verified. See NORMALIZATION-VECTOR-R910.md.
Next measure real iPad scene eligibility and matched performance.

Prior vector helper/cross-product scene failures have been checked. The next
distinct implementation is the full normalization arithmetic region, using
guarded paired values and exact reciprocal/scalar behavior in the existing
backend. See VECTOR-REORIENTATION-R908.md. No new app improvement; the rejected
R907 scalar candidate remains private and unselected.

The13-op scalar resident arithmetic candidate passed correctness but failed
the whole-routine cost gate: slower in all8 pairs even after redundant scratch
preservation was removed. Do not promote it. See RESIDENT-LONG-COST-R907.md.
Next direction must reduce arithmetic execution cost, not merely keep values
resident or add scalar opcode coverage. Installed app performance is unchanged.

Private resident fused arithmetic now preserves halfway rounding and exception
semantics in an actual four-op region. Fixed/random/explicit-halfway tests each
pass629760 full-routine comparisons. See RESIDENT-FMA-R906.md. Remaining
lane-selected/scalar/sum lowering is needed for the longer region before a
useful cost gate. No measured app improvement or Simulator launch this turn.

Private ARM64 resident multiplication now joins actual merge code; final fixed
and randomized-operand/FPSCR whole-routine tests each pass629760 comparisons.
One raw underflow mismatch was explained by exact helper disassembly and fixed.
See RESIDENT-MULTIPLY-R905.md. Broader arithmetic and a cost gate remain; this
does not improve the installed app yet. No game or Simulator is running.

Four actual DOL merges now run through a private static ARM64 resident region
inside the original chunk. Selected-routine state/callback/status comparisons
pass629760 cases. See RESIDENT-REGION-ENTRY-R904.md. No new game performance
gain: last measured heavy iPad plaza remains37.15 VI/s; movie59.88 VI/s.
Next broader resident arithmetic and whole-routine cost, not another tiny
transport benchmark. No app or Simulator is running.

Private paired-merge prototype now handles recorded CR1 updates and verifies an
intermediate non-record observer state. Three final modes each pass100k cases;
guest entry/cycle/arithmetic integration is still open. See
PAIRED-MERGE-CR1-R903.md. This is not an app performance improvement; no game or
Simulator is running. Earlier checkpoints below describe their own revisions.

R902 implements private resident paired-merge value lowering in the existing
offline FPR-cache prototype. Combined/plain/conversion regressions pass100k
full-state cases each. Guest entry/cycle/arithmetic integration is still missing;
this is not a faster product build. See RESIDENT-PAIRED-MERGES-R902.md.

R901 rejects the private guard-relocation candidate on cost: full-chunk libraries
preserve selected-routine correctness, but~3% extra instructions and all8timing
pairs slower. It remains outside the app. See FP-GUARD-COST-R901.md; do not
resume R900's pending cost step below or build a game module from it.

R900 private shared-code candidate now implemented: repeated FP availability
checks bypassed only on verified arithmetic fall-through; external entries keep
their checks. Wide629760 full-state comparisons pass. Not in any product build,
no cost/FPS result yet. Next whole-chunk actual-policy control/candidate gate.
See FP-GUARD-CHAINS-R900.md. No game, Simulator or experiment remains running.

R899 now completes the native heavy-scene instruction capture and exact-module
mapping. See HEAVY-NATIVE-PROFILE-R899.md: broad generated work remains, loads
52.44% of sampled generated weights; no single new dominant routine. All runtime
and profiler handles finished/save unchanged. Next implementation hypothesis
from retained instruction evidence, not another profile. The separate timing
window overlapped offline analysis and does not prove a clean performance gain.

Actual iPad movie: 59.88 VI/s; following invaded plaza: 37.15 VI/s,
23.42 ms CPU/VI, 178.58 million CPU-thread instructions/VI. Gameplay audio
accumulated 74 underruns in an interior 21.5-second interval. These are not
display-completion FPS or an optimization gain. See POSTMOVIE-IPAD-R897.md.

R898 reconciles old heavy-scene samples with the quieter native instruction
profile. Next source-matched native heavy-scene instruction attribution, then a
shared-code candidate and matched iPad test; see PERFORMANCE-SCOPE-R898.md.
Small guarded-routine rollout is rejected. Correct depth and timing stay intact.
No Simulator is booted. R897 restored the iPad host85ffc100 and preserved save
99d432d5; that diagnostic host is not the latest product UI. The product checkpoint
below remains separate. No recent product-level performance breakthrough.

## Current checkpoint — R884 physical-iOS integration

Recent product changes, not a performance breakthrough:

- Audio menu: persisted main volume/mute; R876 actual Simulator menu and
  stop/relaunch retention passed. Audible gain, speaker-specific output and
  physical-device audio remain unverified.
- Stopped screen: explicit Restart and hidden gameplay controls. R878 one
  same-process restart pair rendered successfully and stopped cleanly.
- Phone Plus default(.72,.62): R880 actual confirmation/plaza views clear the
  earlier central/Yes overlap. Movement stick still overlaps Back/story text.
- R881 accessibility button pulse: isolated UIKit tests pass release, held-touch
  preservation, reset, idle and settings cancellation. R883 packaged Simulator B
  activation returns file panel to planets with scripted input released. No
  matched baseline/full accessibility or Plus-behavior acceptance.

Installed iPhone candidate is R883 generated/simulator-stage.Zmi382/GalaxyPad.app,
host174c72e371bad471c2b32ec3f5213c9e72d320dc438f7c846d1bd0fbc8b7a7e8.
Its pre-staging host generated/candidates/product-r841/GalaxyPad.app is
5554b5848c0fb5c411e4bae129b9577e55839063dab9f4521d6ef1d292fb4b2d.
The installed app contains the accessibility implementation.

Broad repository regression completed successfully (50968 exit0,
generated/check-r882.log). This excludes packaged UIKit/runtime acceptance;
tracked-file checks also do not audit the largely untracked checkout for release.
Physical-iOS Release build now current; private stage
generated/device-stage.E7pIDj/GalaxyPad.app contains host
70b573b177d56e30d1d8054e17b34bc0f2f626ead44b91fe947926c1eaed0958
and unchanged device module48f455eb...10041. Not signed for a device or tested
on hardware; fresh devicectl reports no connected devices.

Next: Back/story layout and bounded performance work.
Do not repeat visual
confirmation/navigation just to re-establish R880. Retain full PRD performance,
gameplay, audio, device, packaging and licensing gates; no shippable claim.

## Historical checkpoints

Entries below describe their individual revisions, not the current queue.

**R874 Audio-menu dependency investigated; suspected RemoteIO issue refuted.**
Native menu lacks Audio controls. Standalone sole-phone capability probe accepts
existing HAL volume parameter and reads back0 (both statuses0), so no backend
replacement justified. Actual mute/volume output not tested. Next lifecycle-safe
runtime/host volume adapter then menu/persistence/output verification. Game/app
data untouched; no stream started; Simulator shut down. Performance still open.

**R873 slot3 recovery confirmed; ascent remains unresolved.**
Walkthrough identifies tower-top Luma/Sling Star, not glowing objects along the
bridge. Slot3 visibly reloads; diagonal/right movement returns to tower wall,
short forward jump does not find ascent. No new progression/bug/FPS claim.
Existing checkpoints retained; native Quit68047exit0, NAND unchanged. Next use
better visual route evidence or reassess approach before repeating these inputs.

**R872 actual Good Egg traversal/Spin advances isolated route.**
Slot2 reload works; Mario traverses underside, climbs stairs/ledge, Spin defeats
stair enemy into Star Bits, then reaches curved path end. Slot3af5bfcfb preserves
position; not reload-tested, no Launch Star/new star reached. Four short input
fixtures added; route needs further navigation. Native Quit49211exit0/fallback0/
smc_failed0; NAND unchanged.74underruns/43backlogs over~782s excludes audio/timing
acceptance despite frequent near60 title labels. No product performance change.

**R871 isolated Good Egg continuation checkpoint established.**
No verified ball/ray checkpoint found in inspected records. Copied historical
R418 Config/Wii/states into progression-r871, preserving originals. Normal Mac
runner671729c6/modulec0021b9f loads slot1 into Good Egg; Pipe movement reaches
house. New isolated slot2ec44edde saved, reload not yet checked. Native Quit
31316exit0; copied NAND unchanged. Next continue progression from slot2, not
instrument title screens. Whole-run45underruns/12backlogs; no FPS/audio acceptance.

**R870 ball dispatch/output boundary confirmed in exact DOL.**
Constructor installs acceleration vtable; shared sphere movement dynamically
calls its axis slot, separate from jump/brake. SHA-guarded audit now checks
construction, table entries, indirect call and scalar output stores. This gives
a narrow original-output observation boundary; no adapter installed or gameplay
claim. Next observe actual ride outputs/object state before changing behavior.

**R869 exact RMGE01 tilt call sites confirmed.**
Read-only SHA-guarded audit passes for ball acceleration getter, distinct plain
stick X/Y calls, ball held/triggered A and ray gate/shared acceleration calls.
USA names remain candidate labels; raw branch operands verified independently.
See TILT-CONSUMER-AUDIT.md and scripts/audit-tilt-consumers.py. Next dispatch and
return-boundary confirmation before live mechanic probe. No runtime/patch/FPS claim.

**R868 ball/ray consumer map identifies separate acceptance paths.**
Tamakoro uses acceleration-controller subclass, not plain SpherePadController;
ray independently consumes acceleration with speed/A/tutorial gates. Vendor
acceleration also includes point rotation. TILT-CONSUMER-AUDIT.md records source
and incomplete-reference caveats. No global orientation patch justified. Next
resolve exact RMGE01 consumers before mechanic-specific capture/adapter work.
No runtime/build/product change or new performance evidence this pass.

**R867 touch tilt response controls implemented.**
Touch-only0.5×/1×/1.5× sensitivity, vertical inversion and recenter submenu;
default unchanged. Response changes clear touch input, axis scaling clamps,
malformed preferences safe. UIKit LTJKzM passes with direct-handler assertions;
Release host803c93a6 builds/signs/verifies. Not installed/staged/gameplay accepted.
Existing fjpWgy product/data untouched. Next source/actual mechanic coverage,
not treating input-option tests as ball/ray completion. Simulator shut down.

**R866 shortened guide/status visually fit on iPhone landscape.**
Installed private fjpWgy hostd3c3ffa4/module32a92fdb. Both screens show complete
copy and Done without scrolling at874×402/default text size; both dismiss.
Screenshots/runtime under generated/runtime/product-r866. Startup/menu evidence,
not gameplay or larger Dynamic Type acceptance. Native Stop failed0; save50b7290a
unchanged. No source change needed. Next gameplay/control gaps, not another
default-size menu-copy pass; performance/full PRD remain open.

**R865 native UI recovered; actual guide/status checked and copy shortened.**
Explicitly opening Simulator's device window restored CUA access. Installed
ZSXvs9 hostdecd823c/module32a92fdb; plain launch uses existing import. Guide and
status open/dismiss; status detects image/save. Both long alerts required scroll
on compact landscape, so shortened copy in source. Host42f9215b builds/signs,
phone UIKit NxFYwp passes; shorter copy not yet installed/visually checked.
Native stop failed0; save unchanged after resolving relocated data container.
No gameplay/FPS acceptance. Next compact-copy recheck then gameplay control gaps.

**R864 read-only game-data/save status added to native menu.**
PRD menu now has supported title/revision/expected DOL identity and imported
image/save-file presence. Explicitly not a fresh integrity/progress check; no
save contents read or changed. Phone isolated UIKit cGLZFl passes; Release host
6baab23b builds/signs/verifies. Not staged/installed or product visually accepted.
CUA getApp still times out; headless focused tests work. Existing product/data
unchanged; sole Simulator shut down. Full input/lifecycle/performance gates open.

**R863 updated self-contained Simulator candidate ready; UI check deferred.**
Private stage iGn9x1 includes R859–R862 host fixes and bundled module; signatures
verify, host0445a3e1/module32a92fdb. Not installed: existing7BjbCR/data untouched.
Sole phone boot succeeded, but native UI getApp repeatedly timed out (-10005);
inventory still reported Simulator running. No game launched or guide visual
acceptance. Shutdown requested and verified before handoff. Next install/test
this exact stage when native UI access works, without reimporting data.

**R862 touch guide added inside the existing Controls menu.**
Letter-only game buttons unchanged. Guide explains X/spin, Y/camera, separate
aim/action, title A+B, optional non-motion tilt stick and customization. Phone
isolated UIKit regressions pass (mobile-ui.OcRdCe); Release host builds and signs,
SHA69f23f7f. Not staged/installed or visually accepted in product; installed
7BjbCR and imported data remain unchanged. Simulator shut down. Queue refreshed
to avoid repeating opening recovery; next actual guide usability and unresolved
gameplay/control coverage. No FPS gain or shippable-control claim.

**R861 packaged iPhone save recovery reaches plaza and movement.**
Installed7BjbCR uses bundled module/private imported data; only diagnostic input
file argument. Original Mario file/time visible, Play→story→plaza, movement works.
Post-stop save byte-identical to pre-import50b7290a. SAVE-AND-NAND.md records exact
scope. No reimport/build/timing claim. Console72939 terminal0, Simulator off.
Next required gameplay/control coverage beyond repeated opening verification;
full first-play/physical/timing/audio gates remain open.

**R860 import storage preflight implemented and tested.**
Before staging/copying, exact-image import now requires9GiB available: supported
WBFS plus disc-sized extraction bound and headroom, no assumed deletion of old
data. Unknown capacity fails closed; later write failures remain handled. Tests
cover just-below/exact threshold, no staging/extractor call on rejection and
existing cancellation/activation/save isolation. Hostd7965e0c rebuild/sign passes,
not installed/staged. Existing imported phone data retained; no Simulator run.
Next packaged file recovery without another import, then full product input work.

**R859 real folder import and argument-free packaged boot pass.**
App imports supported image from Documents through native menu, activates data;
save50b7290a unchanged after import and boot/stop. Plain relaunch loads bundled
module and visibly reaches wrist-strap rendering. No development paths/input,
not full gameplay/save-recovery acceptance. Fixed stale success text in source
(not rebuilt). Installed self-contained7BjbCR retained; phone shut down. Import
consumed storage: about19Gi free afterward; retain current data for follow-up,
avoid another full copy/import. Next saved-file recovery via packaged route.

**R858 packaged Simulator launch reaches import setup without arguments.**
Private stage7BjbCR embeds accepted3acdc module; after ad-hoc signing host3de9facf
and module32a92fdb. Actual phone launch without arguments now displays supported
image import instructions, not missing-module error; Game Data menu reachable.
No actual import/game run yet. Staging SDK allowlist added, cross-platform input
rejected,15 invalid-SDK cases pass. Next real folder import then argument-free
gameplay using preserved phone save. Console62448 terminal0, Simulator off.

**R857 real editor Home/return passes; bundled Simulator startup gap fixed in source.**
Installed dae0296e without development arguments, no game launched. Editor→2
selection→Home→samePID86342 return→Done restores normal overlay. Not an active
drag/audio/game interruption test. Missing-module screen exposes Simulator-only
argument dependence: now both platforms select packaged Frameworks module,
with explicit override remaining Simulator-only. Host857d6501 builds/signs;
not installed or bundled-path runtime-tested. Next private Simulator staging and
argument-free launch/import path, preserving existing phone saves. Simulator off.

**R856 broad regression suite passes; device stage includes editor fixes.**
check-repository94553 exits0 with final safety marker; logcheck-repository-r856.log.
This covers its automated checks, not UIKit (separately passed R855), gameplay,
physical devices or untracked-source publication audit. Device host71522 rebuilt
and staged RvOFtT/23284c78 with unchanged R853 core and48f455eb module. Latest
source fixes now in both candidate lanes; neither updated host game-tested.
Next actual product editor/lifecycle verification and unresolved gameplay/control
coverage. No Simulator/game launched and no performance gain this pass.

**R855 cancelled editor drags no longer overwrite layouts.**
Red k7HOeF reproduces unwanted persistence. Cancellation/failure now restores
saved/default geometry without writing preferences; normal completion still saves.
Phone r4jVe9 and sequential iPad SaYVdL pass direct gesture-state regressions.
Simulator candidate rebuilt/signed dae0296e includes R854/R855, not installed or
game-tested; device stages unchanged. Both Simulators shut down. Next actual
editor interruption validation and remaining phone occlusion, not another startup
or microbenchmark-only loop.

**R854 layout reset now preserves appearance preferences; both UIKit targets pass.**
Reset confirmation promises positions/sizes, but source also removed opacity.
New regression reproduces failurehhdC5z; removed opacity deletion. Phone nQzRhf
and sequential iPad5qnbg8 pass: geometry/cached sizes reset, opacity/controller
visibility retained. Preview now clears singleton size cache with preferences.
README updated. Source/test change only; existing staged products predate this
fix and need rebuilding before acceptance. Both Simulators shut down, no game run.

**R853 device core refreshed; new private stage, signing/device gates open.**
Old R643 archivef4730e66 replaced by current-source226-step rebuild/provision
b1c9def7. Host relink succeeds; new stageEI86W0 host8824315d/module48f455eb passes
staging checks. No install-signed bundle or physical acceptance: zero valid local
signing identities, no connected devices. Older stages retained. Simulator/save
data untouched. Continue independently testable product work while these gates
remain open; never label successful link as module/runtime correctness proof.

**R852 current device host built and privately staged, not install-signed.**
Release/THP-off device-r852 builds with current overlay/icons against existing
device core. Staged yXz4N2 contains hostb2665b80/module48f455eb. Architecture,
iOS16 platform, module export/install-name, bundle identity and icon metadata
checks pass. Staging accepts explicit candidate paths and rejects old icon-less
app. No devices connected; no install/physical acceptance. Next audit existing
device core/module provenance and signing prerequisites before hands-on candidate.

**R851 release-readiness index added; repeated converter lead closed.**
Current normal/indexed loader source reviewed; R683/R684 already tested reduced
normal-output cursor work with inconsistent microbenchmark gain, no promotion.
Do not restart this tiny-converter lane from R849 sample alone. Added missing
RELEASE-READINESS.md with exact host/module hashes, dirty-source caveat, D1–D12
and matrix1–36 unaccepted release boundary, physical/notices/rights/icon gates.
README links it. No runtime change or FPS gain. Next concrete product work is
remaining phone control occlusion and physical-device candidate readiness, not
another startup replay or converter benchmark.

**R850 slowdown sample reviewed; README reflects actual iPhone boundary.**
Main thread1288/1315 sampled stacks in run-loop wait. CPU-GPU thread includes
826 samples under one native Run branch and142 under vertex conversion; nested
waits are not exclusive CPU costs. No touch-UI dominance or new speedup shown.
R536 already tested mobile dual-core without a clear win. Next bounded source
review of portable indexed vertex conversion, before any new runtime experiment;
do not repeat dual-core or fallback totals. README now separates Simulator from
physical-device evidence and documents editor access plus known phone overlaps.

**R849 iPhone persisted file loads into plaza; performance still fails.**
Installed67fc872a, same3acdc module. File1 Mario icon survives previous run/install;
loads story then plaza, diagnostic movement visibly works. Centered Plus clears
Yes/No labels (tested empty file2 then cancelled). Back/story and introductory
Mario overlap remain; not shippable layout. Recent gameplay windows31.32–46.42
after-frame events/s; concurrent JumpConnect214%CPU complicates attribution.
Two-second sample retained. Clean Stop failed=0; console54226 exits0, phone off.
Next review actual phone layout tradeoffs and targeted slowdown sample, not
another file-creation replay. No physical-touch/jump/full first-play acceptance.

**R848 real iPhone file flow exposes pause-button obstruction; candidate fixed.**
Run79ebf127 reaches new-file confirmation and icon selection using explicit
diagnostic input. Plus visibly overlays Yes; changed phone default to horizontal
safe-area center, preserving saved origins. UIKit AlruL3 passes including new
center assertion; product67fc872a rebuilt/signed, not installed or visually retested.
Brief Home/foreground restores same PID79737/icon screen; no full lifecycle/save
acceptance. Native Stop failed=0, console57313 exits0; sole Simulator shut down.
Next actual new candidate confirmation-screen recheck, then finish file creation.

**R847 counter interpretation corrected; resume iPhone product progression.**
R846 is not a demonstrated iPhone-only regression: R841/R844 iPad logs also have
nonzero fallback counts. Current Run source counts interpreter steps but not
fallback-JIT execution; hook_fb increments before native cache shortcuts. Existing
PERF R489/R553 and JOURNAL R755/R758 cover this distinction and prior vector census.
No new census/build warranted from totals alone. Next actual clean iPhone
title/file creation/gameplay and lifecycle, with separate saves; no FPS gain claimed.

**R846 actual clean iPhone startup/settings pass; fallback investigation next.**
Installed private79ebf127 on the sole iPhone Simulator with unchanged3acdc module;
no previous GalaxyPad data container existed. Wrist-strap rendering and real
compact settings/Reset visibility verified, native Stop confirmed and failed=0.
Shutdown nevertheless reports fallback=7843419, hook_fb=11230256, smc_failed=0;
this is not native-only acceptance or a performance gain. No gameplay/save-load
claim. Evidence in generated/runtime/product-r846/runtime.log and settings-phone.png.
Console91133 exited0; phone shut down; private app retained on phone, no iPad changes.

**R845 phone settings/editor obstruction fixed; both UIKit targets pass.**
Reset fully visible on tested phone; editor moved above controls so1/2/−/+ can be
selected, Done44pt and menu remains clear. Actual2 selection/Done observed.
Phone qlRMQy and iPad H2Rh0i pass sequentially. Private79ebf127 product rebuilt,
not installed/promoted. PHONE-EDITOR-R845.md records limits and next actual iPhone
product pass. No game/save changes; both Simulators shut down.

**R844 actual plaza HUD clears; compact settings and iPad icon observed.**
Private fdf7539e run verifies R841 corner overlap resolved in opening plaza,
touch-only compact settings open/close, A response afterward, clean Stop and
unchanged save. Inset physical reach remains unaccepted; file-menu overlap remains.
Original icon visible on iPad home/Dock. Added macOS ICNS generation/package wiring,
focused checks pass; no full macOS package promotion. PRODUCT-UI-R844.md records
evidence and remaining gates. Prior app restored, sole Simulator shut down.

**R843 iPad HUD-clearance candidate built, not product-accepted.**
Inset default clusters clear conservative R841 corner zones in UIKit; D-pad now
included in pairwise tests. Story-clearance and optional-control collisions fixed;
full iPad suite cnoWtk passes. Preview shows increased inward thumb reach, an open
ergonomic tradeoff, not shippable acceptance. Private fdf7539e candidate under
generated/candidates/product-r841 includes R842 settings; next actual plaza and
settings comparison before any promotion. No game run; Simulator shut down.

**R842 touch settings simplified; revised product host rebuilt.**
Removed duplicate/low-contrast render selector and its obsolete handler/state;
Display retains all four render choices. Panel capped at320pt, Close/Reset44pt,
rows minimum44pt. UIKit regression eOJsHY and product rebuild pass. Removal seen
in preview; final compact geometry still needs visual/product recheck. No saved
control origins found in actual product preferences: R841 HUD intrusion is default
geometry, not a custom-position artifact. Simulator shut down; full goal open.

**R841 real product candidate reaches opening plaza; remaining UI defects visible.**
Built/signed0a1fe67e with R838–R840 icon/menu/controls, unchanged3acdc module.
Real file/story/plaza run shows Star Bit/life-icon intrusion still present and
low-contrast duplicate resolution row in touch settings. Native settings close
and confirmed Stop work; failed=0, save unchanged. PRODUCT-UI-R841.md records
exact evidence and next targeted fixes. Prior app restored; Simulator shut down.

**R840 compact-phone control targets corrected; phone and iPad UIKit passes.**
Default D-pad/small phone targets and menu meet44pt; separated phone move/Down,
A/B and Spin/C hit boxes without changing mappings or saved positions. Visible
iPhone preview inspected; new safe-area/minimum-size/non-overlap checks pass.
PHONE-CONTROLS-R840.md records evidence and next private product build containing
R838–R840 for actual gameplay HUD/settings validation. Both Simulators shut down
sequentially; no product promotion or performance acceptance.

**R839 native menu refined and verified in isolated UIKit preview.**
FPS now under Display; Stop and data removal retain confirmation plus destructive
styling. Stop disables without a runtime callback and refreshes on attachment.
UIKit regression passes; actual FPS toggle/reopen visually verified. No product
promotion or gameplay/performance acceptance. MENU-REFINEMENT-R839.md records
evidence and next control/settings/gameplay-layout pass. Sole Simulator shut down.

**R838 reoriented toward complete app experience; README added.**
Active loop now advances SunPad controls/menu, original app branding and README
alongside bounded performance work. Native comparison attempts stopped cleanly:
first remained at file details; retry stayed at title with background input
disabled in its copied profile. No valid new CPU-thread comparison or FPS gain.
The top-level README now separates current evidence, build prerequisites and
artifact-pinned mobile limitations from unaccepted shipping/device claims.
Original orbital icon source/catalog added, with CMake compilation before signing.
Real actool passes both SDKs; 1024px opaque input and both family metadata verified.
Focused merge/preservation/repeat-build regression passes. Not yet installed for
home-screen acceptance; macOS icon and editable artwork remain open. Controls/menu
are the next product pass; no game/Simulator running and no new performance claim.

**R837 native thread-work host built, isolated matching profile ready.**
Unchanged runtime object matches archive exactly. Native control has only parsed
UUID/LINKEDIT-reservation differences; all other bytes match, tests preserve this
explicit boundary. Candidate9ee5404f is signed/verified, not launched. See
THREAD-WORK-NATIVE-HOST-R837.md for exact prepared runtime/profile and next30s
native plaza comparison. Normal app/module/save untouched; no runtime/Simulator.

**R836 complete self-thread plaza capture:49.379VI/s,98.33% Performance-core time.**
Zero drops; CPU17.941ms/VI,140.437M thread instructions/VI. Mach CPU time agrees
with existing clock. This rules out E-core dominance for this run, not historical
slowdowns; no optimization or accepted FPS gain. THREAD-WORK-RESULT-R836.md gives
native same-thread counterpart as next gate, no repeated Simulator capture.
Original app restored, save unchanged, sole Simulator shut down.

**R835 private game recorder runs/exports; first measured window rejected.**
Both buffers filled1.419s before capture end; strict analysis rejects incomplete
coverage. Added sidecar pairing/topology/reset/error/Mach-unit tests, all pass.
THREAD-WORK-CAPTURE-R835.md records UI-delay cause and prompt-navigation retry
using same built host. Original app restored; Simulator shut down. Container
UUIDs changed during reinstall; resolve current paths, do not reuse old UUIDs.

**R834 private Simulator host built and signed; not installed/run.**
Runtime control object matches archive exactly. Unchanged host relink differs
only in parsed signing-related LINKEDIT virtual reservation; all other bytes
match. Candidate changes only runtime object via private VFS overlay; normal
app/archive/module untouched. THREAD-WORK-HOST-R834.md records ready24002e50 app
and next sidecar-analysis/actual CPU-thread plaza measurement. No live Simulator.

**R833 private thread-work VI overlay implemented and tested; not game-built.**
Opt-in fixed-buffer self-thread/per-core-class counters, explicit errors/raw Mach
units and post-join sidecar export. Fake-provider sanitizer tests, ordinary/private
VI lifecycle and native worker-thread integration pass. Ordinary fixture excludes
SPI and ignores opt-in. THREAD-WORK-RECORDER-R833.md gives private host-build and
sidecar-analysis next gates. No normal app/module/save changes or runtime.

**R832 self-thread counter feasibility passes native and Simulator.**
Standalone private probe reads instruction/cycle/core-class counters; Mach CPU
time agrees with thread clock within0.006%. Not game residency or a speed fix.
THREAD-COUNTER-PROBE-R832.md records source/build identities and next private
opt-in recorder integration with tests, then host-only diagnostic build.
No game or Simulator remains; no product/module/save changes.

**R831 matched Simulator plaza:30.689VI/s versus native59.949; no speed fix yet.**
CPU-thread time29.490 versus14.226ms/VI, but whole-process instructions only2.83%
higher and cycles1.24% lower. Complete window retained despite later tail drops.
PLAZA-PLATFORM-RESULT-R831.md separates evidence from clock/core speculation and
sets a bounded self-thread-counter feasibility gate before another game build.
Runtime stopped cleanly, save unchanged, sole Simulator shut down. Full goal open.

**R830 macOS neutral-plaza baseline measured:59.949VI/s,14.226ms CPU/VI.**
Fixed30s window has1799VI; whole-process213.0M instructions/VI. First capture
rejected for missing coverage; retry's865tail drops occur after the fully retained
window and are reported explicitly with6.105s margin. Prefix-aware tests pass.
MAC-PLAZA-WORK-R830.md records exact evidence and next matching Simulator run.
Both macOS attempts stopped cleanly, copied saves unchanged; no live runtime.

**R829 platform audit complete; private plaza measurement ready, not launched.**
Prior platform/priority results rechecked; no fixed Simulator ceiling or new QoS
fix. Recent plaza counters are not matched across targets. Copied profile/save,
independent Pipe and current process-work probe prepared; focused timing tests
pass. PLAZA-PLATFORM-PREFLIGHT-R829.md specifies next native launch and bounded
capture, then Simulator sequentially. No game/Simulator or normal product change.

**R828 compact normalization parked: qualified workload is slower.**
Full8,704-case guest-state/memory audit passes but96host-flag mismatches remain.
On a separately qualified finite workload, unchanged whole-chunk candidate is
~27% slower with~7% more instructions. No promotion or further tuning of this
design. NORMALIZATION-DISPOSITION-R828.md records exact evidence and next
macOS/Simulator cost reconciliation. No game/Simulator or normal app/save change.

**R827 compact normalization passes isolation but fails whole-chunk host flags.**
Compact helper closure reduces work-path frame to192bytes; both isolated294,912-
case suites pass. Actual-policy containing-routine gate reproduces flags0x15
versus0x1 with equal full CPUState at pattern3/RN0/NI0/entry3. Timing never ran.
Retained libraries/source/reproducer and next action in COMPACT-NORMALIZATION-R827.md.
Keep candidate private; no app/save changes or game/Simulator running.

**R826 normalization local-state oracle passes, but codegen still has large scratch.**
294,912 full-state/FPSR comparisons pass in both sanitized O2 and ThinLTO modes.
All9suffixes/internal-external charges and FP-unavailable cases covered. Local
CPUState retains a large stack frame, so this is a correctness scaffold, not a
candidate for game build or FPS claim. NORMALIZATION-STATE-R826.md records next
compact FP-state/helper-dataflow gate. No runtime, Simulator or product changes.

**R825 whole-chunk alias-annotation experiment closed without a rebuild.**
Three private O2/strict-FP/ThinLTO pairs have identical instruction encodings
after adding CPUState restrict. Artifact/source/link checks pass; no candidate
executed. STATE-ALIAS-CODEGEN-R825.md records limits and the explicit-state-
retention next gate. No app/save changes, running game or Simulator, or FPS gain.

**R824 load-origin attribution corrected; callback semantics reverified.**
Exact numeric global addresses replace nearest-symbol inference. Load-origin,
instruction-classifier and callback-remapping tests pass. Most sampled loads
remain unresolved; no claim that their weights are removable cost. See
PLAZA-LOAD-ORIGINS-R824.md for artifacts and the whole-chunk state-lifetime gate.
No runtime/build/app/module/save change or proven FPS gain; full goal remains active.

**R823 weighted instruction map resolves all sampled PCs across574 chunks.**
Generated chunks17,459samples; loads8,975/about51.6% of chunk cycle weights.
This is opcode attribution, not memory latency/state provenance or removable cost.
Exact module SHA and count/weight conservation checked; focused classifier tests
pass. PLAZA-INSTRUCTION-MAP-R823.md records retained context/report and next gate:
prove repeated load origins and mutation boundaries before broad lowering changes.
No runtime/build/app/module/save changes; original full objective remains active.

**R822 macOS plaza CPU profile captured successfully and runtime cleanly stopped.**
Same R821 process reached visually verified neutral plaza. CPU Profiler attach
and export exit0;25,462 CPU-thread samples retain per-PC cycle weights. Trace
module UUID/path match selected source-audited binary. Artifacts in
generated/runtime/plaza-profile-r821; MAC-PLAZA-PROFILE-R822.md records limits.
Next weighted PC-to-disassembly mapping across chunks, no rebuild/repeated boot.
Native Quit/session10913exit0, smc_failed0, copied save unchanged; no game/profiler/
booted Simulator left. Whole-run FPS/audio counters are not acceptance evidence.

**R821 source-matched macOS profile prepared; sole runtime is live.**
Current helper-source fingerprint and PGO hash match selected macOS module;
strict-FP/ThinLTO policy matches Simulator, but R730 host/platform differ.
Isolated copied Simulator save hash verified. Runtime10913/PID55020 has loaded
the exact baseline module and native window now resolves. Continue SAME process
to visually verified plaza, then bounded CPU Profiler ATTACH; no restart or second
game. MAC-PROFILE-PROVENANCE-R821.md records paths, flags, limits and next action.
No CPU capture yet, no normal app/module/save edits, no booted Simulator device.

**R820 macOS CPU-profile preflight succeeds; raw-task sampler is unavailable.**
Ordinary task access to owned child denied (KERN_FAILURE); no register reads or
permission changes. CPU Profiler macOS test workload capture/export succeeds:
9,083 samples with per-PC cycle weights, 6.5MiB trace. Time limit kills only the
test target (exit54/SIGKILL), so real-game profiling must attach, not short-launch.
PROFILE-PREFLIGHT-R820.md defines next source-matched macOS plaza profile after
runner/module provenance audit. No game/Simulator/profiler running or app/save change.

**R819 plaza capture attempted; Simulator Instruments path is unusable here.**
Unchanged baseline reached visually verified neutral plaza. Host-default attach
could not find PID; explicit-device CPU and Time Profiler both stalled and were
stopped by bounded watchdogs (child exit1). No usable instruction profile. Narrow
spindump fallback requires root and was not used. PLAZA-PROFILER-LIMIT-R819.md
records evidence and next preflight: ordinary-access raw-PC sampler on an owned
test process before another game boot, or source-matched macOS profiling fallback.
Game/profilers stopped, sole Simulator shut down, save hash unchanged.

**R818 CPU-symbol accounting identifies the missing per-instruction evidence.**
3,496/6,004 observations reside in 420 generated chunks; top ten contribute 844.
Collapsed offsets cannot distinguish arithmetic/state/branch work within them.
Parser conserves exclusive CPU-only counts; xctrace parser now keeps per-PC cycle
weights. Focused tests pass. PLAZA-SYMBOL-COST-R818.md defines next action: one
unchanged-baseline, visually verified plaza CPU Profiler capture, no rebuild.
Template is available; actual capture feasibility remains to be tested. No runtime
or Simulator started and no normal app/module/save change.

**R817 quiet-loop specialization parked after the runtime cost screen.**
Separate-TU extracted bursts retain opaque callbacks and timed entry selection.
Nontrivial workloads show no material repeatable benefit across two invocations;
nearly empty bursts are the only consistent winners. No app rebuild warranted.
RUN-QUIET-COST-R817.md records raw artifacts and synthetic-layout limitations.
Next aggregate native generated-code costs across chunks using retained R813
sample/source evidence, respecting prior failed-lane dispositions. Focused tests pass;
normal app/module/save unchanged, no Simulator or game running.

**R816 complete Run variants compile under actual Simulator host flags.**
Private control/candidate objects and exact commands/hashes/disassembly retained
in generated/quiet-run-r816. Run code grows 544 bytes; no speed inference.
Exact complete candidate-source check plus 5,376 differential cases pass in both
sanitized and optimized tests. Runtime cost screen is still pending; do that
before an app rebuild. RUN-QUIET-OBJECT-R816.md records the boundary and next gate.
No Simulator, install, runtime-source, normal module or save change.

**R815 native-loop optional-configuration audit and first differential pass.**
Init/lifecycle-only optional flags can support a private quiet specialization;
live SMC/hook/interrupt/CPU checks remain unchanged. New extracted complete-burst
test passes 5,376 cases each under ASan/UBSan and -O2, with explicit stub services.
No product source, installed app, save, or module changed; Simulator remains off.
RUN-QUIET-AUDIT-R815.md records limits. Next actual-host-policy whole-burst cost
screen before a host build; no performance improvement claimed yet.

**R814 sample/source map favors shared CPU runtime over vertex-only work.**
Video thread56.22% sampled waiting; vertex pipeline13.83% of video observations.
CPU Run self698/6004; inclusive module-call counts are not host self cost.
Exact host disassembly maps optional flags, cycle/timebase and hook checks.
PLAZA-COST-MAP-R814.md records limits and next gate: configuration mutability
audit, then whole-loop fast/general-path equivalence/cost before any host build.
No runtime or product change, no predicted FPS gain. Cross-product stays parked.

**R813 cross-product candidate parked: no repeatable game-speed gain.**
Reverse baseline27.06437 versus candidate26.63122/26.00536 and first baseline
25.92818. Matching neutral plaza/screenshots; no promotion. Separate post-capture
CPU sample retained at plaza-cpu-r813.sample.txt. Next classify CPU/GPU stacks
and map larger host/vertex costs to source, not more tuning this region.
Simulator stopped, save99d432... unchanged. CROSS-DISPOSITION-R813.md records
results, sample limitations and continuation. Original full objective active.

**R812 clean candidate captures show no material gain so far.**
Candidate26.63122 and26.00536 frame-events/sec versus baseline25.92818;
background CPU/VM variation retained. Same neutral plaza visually confirmed.
Candidate stopped, save99d432... unchanged. Reverse baseline console61573 now
starting in SAME sole Simulator; log cross-baseline-r812-reverse.log. Continue
that runtime for final order check. CROSS-CANDIDATE-R812.md records evidence.
No promotion or FPS improvement claim; likely park region after order check.

**R811 baseline plaza measured; candidate runtime live.**
Baseline capture83752 exit0:8complete windows/42.000638seconds,25.92818
after_frame_events/sec. Same plaza before/after, neutral input; host background
load retained. Baseline49602 stopped, save99d432... unchanged. Candidate50305/
console10535 now live in SAME sole Simulator; startup wrist-strap screenshot
confirmed. Continue this runtime to neutral plaza, then45second matched capture.
CROSS-BASELINE-R811.md records evidence. No comparative speed gain yet.

**R810 clean module ready; baseline runtime starting.**
Build53784 finished exit0; candidate59e9fd... passes Simulator/signature gates.
Baseline PID49602/console58553 now running in the sole iPad Simulator; startup
screenshot still says Starting Galaxy. Continue SAME runtime, no second boot.
Log cross-baseline-r810.log, input input-r810.json. Save backed up99d432... .
CROSS-AB-PROTOCOL-R810.md records matched plaza route/capture and comparison
gates. Existing capture tests pass. No comparative speed result yet.

**R809 counter-free source passes; private module link running.**
Exact helper/source identity and262144 CPU/FPSR cases pass,24129 fast cases per
NI mode. Builder rechecks prior control/all1329objects/flags and removes all
eligibility counters. Exec53784 now links; poll SAME handle. Last48934 active
655%CPU. See CROSS-UNINSTRUMENTED-R809.md. No Simulator, finished candidate,
end-to-end gain or normal-module promotion claimed.

**R808 real plaza eligibility passes; end-to-end speed remains unproven.**
R807 private build finished and validated. Exact-source NI0/NI1 coverage now
asserted separately,24129 fast cases each. One Simulator reached Star Festival;
movement/jump visually observed. Plaza window999424 calls,99.21695% fast,0 mode
rejects. Diagnostic frame windows16.60..26.04 FPS, ongoing DMA underruns: still
slow, not a speed A/B. Simulator stopped, save and normal module unchanged.
See CROSS-SCENE-R808.md. Next distinct uninstrumented candidate and matched
sequential plaza comparison; no default promotion or PRD acceptance claim.

**R807 NI-capable diagnostic source passes; private link running.**
New --ni build verifies all1329 object hashes and prior control/flags before
reuse. Exact instrumented source passes262144 state/status cases,48258fast/256ties.
Session29185 now links candidate; last ld46900 active~677%CPU at2m59s. Poll SAME
handle. CROSS-NI-DIAGNOSTIC-R807.md records paths/hashes and tested scene-window
summary options. No Simulator booted, finished candidate or gameplay results yet.

**R806 live diagnostic found NI-mode rejection; source candidate corrected.**
Private build5301 passed. Title/file-select observation:10.4M calls, all mode
rejected. One-shot CPU read confirms FPSCR0x86004004 (NI1/RN0). Simulator stopped;
save unchanged. Bounded NI-capable source now passes262144 standalone cases,
12000 callback/alias+7680 suffix+512 NI/workload cases; ordinary NI workload~19%
faster locally. CROSS-LIVE-MODE-R806.md records artifacts. Old diagnostic binary
still rejects NI; next build distinct NI-capable diagnostic and remeasure. No FPS gain.

**R805 unchanged control matched; private diagnostic candidate linking.**
Same session5301 now links candidate after exact baseline/control SHA match and
successful one-chunk compile. Last linker45352 active~637%CPU at4m48s. Poll same
handle. Exact diagnostic source passes262144 state/status tests including logging;
64 synthetic counter records validate. CROSS-DIAGNOSTIC-R805.md records hashes.
No gameplay percentages, finished candidate verification or Simulator run yet.

**R804 private diagnostic control link running.**
Session5301 is live; unchanged Simulator module relink must match baseline SHA
before one diagnostic chunk is compiled. Last linker44968 actively used~704%CPU.
Do not restart; poll same handle. CROSS-DIAGNOSTIC-R804.md records paths/gates.
Counter summary validation test passes; no scene eligibility results or candidate
artifact yet. Normal module/app/save unchanged, no Simulator booted.

**R803 broader cross-island tests pass; rejection overhead remains.**
12000 callback/journal/alias/suffix cases plus7680 prior context cases and256
workload cases pass. Standalone262144 cases now prove false-return CPU/FPSR
preservation. Ordinary/small workloads~20% faster; rejected large inputs~19%
slower and forced ties~29% slower. See CROSS-CONTEXT-R803.md. Fallthrough rewrite
did not remove this penalty. Next actual-scene eligibility/rejection measurement,
not default promotion or more speculative guard tuning. No app/Simulator change.

**R802 whole FP island shows a material local improvement.**
Guarded six-instruction cross-product region in existing C backend passes262144
CPU/FPSR cases (including128 forced tie fallbacks) and7680 actual-routine suffix/
RAM/status comparisons. Full-chunk strict-FP/ThinLTO screen:43.608→35.095ns,
~19.52% less local CPU time, ~865→778instructions. Candidate PGO is unprofiled;
fixed-input routine result is not game FPS. See CROSS-ISLAND-R802.md.
Next broader context/guard coverage before private module/scene A/B. Prioritize
this simpler path over more offline-backend expansion. No app/module promotion.

**R801 exact FP widening integrated into private cache mode.**
Integer-only single-to-double lane conversion preserves raw special values and
does not depend on FPCR.100000 full-state/FPSR/FPCR cases pass, including65536
systematic exponent/sign/mantissa/mode cases. GPR and non-converting FP cache
regressions also pass100000each, empty stderr. ARM64-FP-CONVERSION-R801.md records
limits. No precision-safe facts assumed, guest arithmetic or FPS improvement
claimed. Next actual FP region lowering and actual-policy cost gate.

**R800 split-lane FP cache transport passes.**
Reference adjacent PS0/PS1 layout is incompatible with CPUState's separate
arrays. Private source-pinned IO adapter fixes loads/stores, retaining allocator.
100000 full-state callback-entry/final-state and FPSR comparisons pass, including
dirty upper lanes, duplicated values and spills. See ARM64-FPR-LAYOUT-R800.md.
Single conversion hooks still abort; next exact conversion/precision gate then
whole-region lowering. No FPS improvement, app/module or Simulator change.

**R799 sustained FP work qualified from exact retained coverage.**
New tested ranker identifies9-op normalization and6-op cross-product arithmetic
spans at22.6M/19.3M attempts per site. These are frequency, not CPU-time claims.
FP-ISLANDS-R799.md records state/exception/observer requirements and prior lane
rejections. Next actual FP-cache state/ABI adaptation before whole-region
lowering and actual-policy cost gate. No app/module change or FPS improvement.

**R798 direct RAM loads correct in focused tests, not faster.**
Mixed block:152320 matrix+2880 CPU-alias comparisons; restore60928+1152 pass.
Helper-only regression also passes. Unsanitized local cost screen is slower
than generated C, not grounds for promotion. See ARM64-DIRECT-LOAD-R798.md.
Next qualify a larger observed hot region and state-observation boundaries;
do not keep tuning this tiny fixture or build an app from it. No FPS gain,
app/module change, Simulator boot or save change; original goal remains active.

**R797 mixed arithmetic/load/store block passes differential tests.**
Real ten-instruction block and all suffixes:152320 complete CPUState/RAM/callback
comparisons pass. Store journals may mutate registers/mapping/LR/flags/cycles.
Earlier restore regressions60928direct+60928frame also pass; stderr empty.
ARM64-MIXED-BLOCK-R797.md records scope. Next direct normal-RAM lowering to
remove ordinary helper crossings, retaining slow-path contracts. No game FPS
improvement, module/app promotion or mobile execution claimed.

**R796 real PPC restore block exported and differentially tested.**
Exact DOL lwz/blr block plus all four suffix entries now executes as statically
linked reference-emitter output. Direct CPUState GPR layout removes frame copies.
30,464 full CPUState/callback-trace comparisons pass; five invalid entries reject
unchanged. Includes callback remapping/register/LR/flag/cycle changes.69376exit0,
empty stderr. ARM64-RESTORE-BLOCK-R796.md records limits. No FPS gain or app
promotion; mixed arithmetic/FP/CR/memory and module integration remain open.

**R795 reference GPR cache now emits and executes offline.**
Unmodified reference allocator with a private emitter/constant-propagation host
passes100000 flush/callback/reload byte-layout comparisons. Callback sees pending
writes and changes all GPRs; generated continuation reloads them. Final44457exit0,
empty stderr. Noncopyable reference CPU object requires explicit field adaptation.
ARM64-GPR-CACHE-R795.md records limits: PPC decoding, full state adapter, FP,
memory/exception/cycle behavior and performance remain open. No app/game changes.

**R794 static ARM64 export/link prerequisite implemented.**
Actual reference emitter produces immutable object code with a symbolic helper
relocation. Two separately linked/load-addressed macOS libraries pass200,000
calls; signature checks and IOS/IOSSIMULATOR object compilation pass. Corrected
assembler deployment target. This is transport only: PPC block lowering,
register-cache integration, state adapter and performance remain unimplemented.
See ARM64-STATIC-LINK-R794.md. No app/module selection, no Simulator/game run.

**R793 mapping boundary audit complete; offline ARM64 candidate scoped.**
Selected host initializes mapping at Run entry, but SyncIn/module/mod callbacks
expose mutable CPUState and journal stores retain acquired pointers. No broad
cache removal justified. Reference ARM64 register caching/precision tracking is
a larger architectural difference; exporter must replace live addresses, state
layout assumptions and runtime code-cache mutation. Concrete source inventory
recorded in NATIVE-EXECUTION-R793.md. Next private offline complete-block exporter
with relocatable helpers/state adapter, then correctness and material cost gate.
No working exporter or FPS gain yet; no runtime/artifact changes, full goal active.

**R792 coverage corrected and shared memory work ranked.**
Selected-function filtering removes duplicate outlined-helper labels; querying
actual statements fixes comment gaps. Retained804B60A0 and805170A0 coverage now
ranked against exact source hashes. Word loads/stores account for about70% of
known second-chunk entries, including frequent register saves/restores. Historical
frequency is not CPU cost or FPS gain. Prior cache/profile rejections retained.
Next mapping-writer/callback-boundary audit before any broader implementation.
See COVERED-WORK-R792.md. No runtime/build selection; full goal remains active.

**R791 movie audio delivery measured; gameplay starvation remains.**
Private nativeTHP movie:59.946 frame events/sec over36.900s, approximately48kHz
nonzero output, zero new DMA underruns/drops/short callbacks. Post-movie plaza:
31.953 events/sec over21.500s,104 underruns,54.58%nonzero output despite48kHz
callbacks. No build/profiler during capture. Sequential scene comparison, not
controlled host A/B or perceptual/AV-sync proof. See MOVIE-AUDIO-R791.md.
Movie completed5591 accepted/0fallback, native stop failed0/smc_failed0; save
99d432d5 unchanged. Console29585/shutdown99733 exit0; no game or booted Simulator. Default remains
OFF; return to material native execution cost, not more movie throughput replays
or buffer enlargement. Full original PRD/SunPad/device gates remain open.

**R791 diagnostic candidate deployed; live audio/movie gate in progress.**
R790 full regression94352 exited0. Core65936 and private nativeTHP app33555
builds/signing pass; normal app unchanged. Candidate binary85ffc100...bcc,
module3acdcddc...bac0. First launch omitted Simulator development paths and
showed missing-module UI; corrected arguments, not packaging/source. Current
console29585/PID38079, generated/ios-runtime-r791b.log, sole M5 Simulator.
RemoteIO output counters are live/available and nonzero;48kHz callback delivery
does not prevent observed DMA underruns in slower scenes. No audio acceptance.
New phase-window summarizer rejects resets/gaps/unavailable output; focused tests
pass. Next one visually bracketed native movie/audio measurement, then clean stop.

**R790 RemoteIO output telemetry implemented; regression subsequently passed R791.**
Opt-in bounded lock-free output counters now feed host logs; no playback policy
change. Sanitizer tests and app/runtime shared-storage test pass. Host, main and
RemoteIO compile checks pass; canonical0030patch integrated. Bootstrap ordering/
unified-patch issues fixed, final46754/repeat38174exit0. Fullsuite logcheck-r790.log,
completed94352exit0 in R791; see latest deployment above. Next private nativeTHP diagnostic build
and targeted audio/movie measurement after regression. AUDIO.md records limits.

**R789 mobile audio evidence gap identified; host logging implemented.**
Retained native-movie logs have no ongoing RemoteIO output counts. Existing DMA
events now exposed by lifecycle-locked host snapshot and optional bracketed
five-second audio-counter logs; missing output counts explicitly unavailable.
Host95898exit0 and main actual-policy syntax check pass; no link/install/run yet.
Next optional RemoteIO callback measurement then targeted movie/audio capture.
No buffering/decoder/default/save changes. See AUDIO.md for evidence boundaries.

**R788 shared-load/type prefix also lacks material cost benefit.**
86334exit0,7680 full-routine comparisons;~3.4%local CPU improvement with~8%more
instructions. No promotion; guard-boundary integration coverage is incomplete.
Close this implementation without more micro-tuning. Next missing timing/audio
evidence for the substantially faster private movie path, starting with retained
logs rather than another unchanged replay. CROSS-RANGE-R788.md. Full PRD open.

**R787 general checked multiply fails material cost gate.**
655360 sanitizer-backed CPU/hostflag cases pass including fivealias patterns.
Full-chunk other hot routine75110exit0,7680 comparisons. Only~1.1%local time
benefit with~8%more instructions; no deployment or fullmodule build justified.
Square's~7%cannot be generalized. CHECKED-MULTIPLY-R787.md records exact scope.
App/save unchanged; original goal remains incomplete.

**R786 checked-square guard passes sanitizer stress.**
53008exit0:262144 actual-helper CPU/hostflag comparisons,43133 vector calls,
raw64/raw32/exponent/boundary values and pre-existing flags. Exact probe helper
extracted via AST; test registered, full suite not rerun. Retained instruction
profile locates additional19.3M/7.1M paired-multiply sites for independent cost
qualification. No general-multiply or game-speed claim; app/save unchanged.

**R785 hot normalization candidate shows bounded local improvement.**
Checked binary32 paired square at804B6BD4, full-chunk actual-policy compilation.
15227exit0:8704 CPU/RAM/hostflag comparisons including randomized inputmemory.
Second alternating run~7%lower routine CPU time, slightly more instructions.
Not gameFPS, sanitizer or wholemodule acceptance; no deployment. Next precision
guard stress and broader executed-site applicability. NORMALIZATION-SQUARE-R785.md.

**R784 instruction-level profile corrects hot-target selection.**
Temporary coverage object + retained profile,91102exit0. R783 load sites0
training executions; old44-op transform9787; normalization804B6BCC22.6million.
Chunk call count alone was insufficient.1023 labels mapped, one unknown remains
null. Expected newer-object timestamp warning retained, no counter mismatch.
See INSTRUCTION-COVERAGE-R784.md. No app/build promotion or fresh FPS claim.

**R783 shared RAM-load range correctness prerequisite passes.**
Actual four-load span,120000 CPU/ordered-callback comparisons under ASan/UBSan;
17145 shared-range calls, interior entries and alias/callback-mutation fallbacks
preserved. Separate experimental test, not module or whole-function timing proof.
Initial exact-body scan finds1853 instructions in4+ same-base load spans; static
coverage alone insufficient to promote. See RAM-LOAD-SPAN-EXPERIMENT.md. No app,
runtime or save change and no game-speed claim.

**R782 broader pure-GPR batching lacks static scope.**
Read-only1322chunk census40039exit0:169835 recognized integer instructions,
only671 in callback-free spans of8+. Focused boundary tests pass/registered;
full suite not rerun after addition. No emitter or app change justified. Retained
profile and per-burst savings budget documented in NATIVE-SCOPE-R782.md; neither
is a game-speed claim. Next dataflow work must address memory/helper boundaries,
not another local batch or repeated unchanged runtime profile.

**R781 full regression passes, including new precision tests.**
check-repository.sh session30339exit0; generated/check-r781.log ends Repository
safety checks passed. Includes R778 scalar fact counterexample and R779640000
typed multiply cases, plus existing runtime/input/render regression gates.
R780 transform benchmark remains separate. Final material/credential/path scans
cover tracked files only, not release approval for this broadly untracked tree.
No runtime or app build this turn; no claim of game-speed or stability completion.

**R780 guarded typed span passes correctness; benefit too small to promote.**
23621exit0;22,528 full-transform CPU/RAM/hostflag checks. Four precision-qualified
paired multiplies in the actual full chunk improve mean local CPU time about2.8%
but increase instructions about4.6%. Not a game FPS result, no deployment or full
module build justified. Original fallbacks/interior entries and FP settings remain.
See FP-TYPE-FACTS.md. Next full regression including R778/R779, then broader native
cost/coverage qualification before any further emitter implementation.

**R779 typed paired-multiply arithmetic passes; integration/cost unproven.**
Precision-qualified finite binary32 multiply with NIclear agrees with actual
helper across640000 CPU/hostflag cases under ASan/UBSan,292605 vector-path
calls. Other cases use original helper. Type precondition is explicit, not yet
proved at generated callsites; R778 scalar-success guards still required.
Registered test, no benchmark or runtime/module changes. Next guarded full-chunk
type propagation and cost gate, not standalone-helper performance extrapolation.

**R778 precision-dataflow correctness boundary established.**
Actual scalar helpers under VE can preserve an old non-single destination after
an invalid operation. New source-derived sanitizer test passes12 invalid/alias/
VE cases and finite success, proving opcode-only single-result propagation is
unsafe for current semantics. Registered test; no runtime change. Rechecked
R425 config: accurate FPRF/NaNs enabled in historical fast JIT reference, so
accuracy defaults alone do not explain gap. See FP-TYPE-FACTS.md for required
success/entry/callback fact boundaries. Full goal and speed deficit remain open.

**R777 scalar-lane variant rejects array-copy cost explanation.**
Same19-op batch lowered to23 named lane variables plus four-byte FPSCR,
without arrays/memcpy.22,528 full-transform CPU/RAM/hostflag cases pass;
51437exit0. Baseline~2745 vs candidate~2949instructions, candidate slower,
nearly identical to prior array variant. Retract array-copy overhead as working
diagnosis; no more representation/attribute variants or full module build.
No app/runtime changes. Full original performance and PRD gates remain open.

**R776 local-FP copy-in/out span fails cost screen; no deployment.**
Whole-chunk actual-policy prototype batches19 pure FP instructions with unchanged
arithmetic and ten destination-register/FPSCR writeback.22,528 full-transform
CPU/RAM/host-flag cases pass, including unavailable-FPU/interior-entry cases.
Final25795exit0: instruction work grows~7%, timing is slower/noisy; new candidate
PGO missing-data warning retained. Reject this copy-in/out implementation without
full module build or attribute tuning. Not a general verdict on register-lifetime
lowering. See LOCAL-FP-SPAN-EXPERIMENT.md. App/core/save unchanged; full goal open.

**R775 repository regression run completed successfully.**
check-repository.sh session63723exit0; generated/check-r775.log ends
Repository safety checks passed. Includes new FIFO/gather tests, nativeTHP
configuration warning gate, run-cost/deferred-TB and existing runtime/input/
render diagnostics. Experimental transform benchmark is separate, not covered
by this suite. Final credential/path/material scans are tracked-file checks,
not approval of the broadly untracked checkout or a releasable package.
Corrected stale PRD companion link to actual goal-loop filename. No runtime
or app build this turn. Full PRD/performance/stability/device gates remain open.

**R774 R772 live run finished cleanly; intermittent XF fault remains open.**
Original-decoder movie visibly returned to invaded plaza; subsequent movement
reached Toad dialogue, life3. Native Stop at06:32:55 local logged failed0 and
smc_failed0; idle host terminated, console28463exit0. No game remains running;
sole M5 remains booted. Save99d432d5 unchanged after stop. About16minutes from
host launch, not a defined soak/performance gate. No targeted XF assertion in
this run; do not infer crash fixed. devicectl5950exit0: no physical devices found.
No further unchanged opening replay justified. Keep origin diagnostics for next
substantive build and return to material performance work; full PRD still open.

**R773 same live session reaches airship movie; failure not reproduced yet.**
Revalidated28463/PID11247 and sole M5; no restart/install. Visually navigated
from waterside overlook through town square and triggered first airship movie.
Second screenshot30s later shows Peach overlooking the attacked town, proving
visible advancement, not completed playback or accurate cadence/audio. At9m35s
process alive; no malformed-XF/source assertion or runtime-exit line in log.
Original decoder remains selected for this stability run, not a performance
candidate test. All input leases released. Continue session28463 and check for
movie-to-invaded-plaza return; do not count this as crash resolution or acceptance.

**R772 live stability reproduction in progress — do not restart blindly.**
Existing installed appe2f9c933 verified, sole M5 DE8E956F booted; launch console
session28463/PID11247 currently live. Log generated/ios-runtime-r772.log,
leased input generated/input-r772.json. NativeTHP NO, run-cost/fallback census
OFF; existing failure-origin diagnostics retained. Visually reached plaza and
moved Mario up path to waterside overlook; life3/starbits0. At4m40s process was
alive with no XF assertion. No stability pass/FPS gain. Save99d432d5 verified
before launch; no checkpoint operation. Continue same live session after checking
handle/PID and current screen. Do not run builds/profilers alongside it.

**R771 gather-write width/burst mismatch not reproduced.**
Source-derived actual AOT gather switch, FastWrite8/16/32/64 and UpdateGatherPipe
pass32,768 sequences/1,310,720 writes under ASan/UBSan: residual0..31, widths
1/2/4/8, varying payloads, byte-order oracle, spill, burst count and FIFO wrap.
The AOT8byte route's eight byte writes match the direct64bit route at completed
write boundaries. Stubs exclude MMU/CP side effects and concurrent observation;
not a live crash fix. Test registered. Further isolated width/compaction tests
are not the next step: obtain failure origin with existing instrumented build
before adding producer tracing. CPU-ahead history alone cannot identify GPU input.

**R770 graphics-failure boundary narrowed; no crash fix claimed.**
Retained R742 log predates origin instrumentation and cannot name the producer.
Actual non-deterministic ReadDataFromFifo passes33,153 occupancy/compaction
cases plus two exact residual-prefix shapes under ASan/UBSan. Both wrap and
non-wrap preserve the two-byte10 00 prefix followed by32bytes; no corruption
found in this isolated append/compaction path. Test registered in repository
checks. CopyFromEmu is stubbed; producer, DMA, concurrency and deterministic
path remain unproven. Next upstream gather-pipe/burst history, not another
XF-case-only test or assertion suppression. No runtime launched/app changed.

**R769 actual-policy whole-chunk test rejects blanket FP inlining.**
Complete1024-instruction chunk compiled as separate baseline/candidate libraries
with real macOS ThinLTO/PGO/final-O2/NDEBUG/strict flags.22,528 full-state/RAM/
host-flag fixture comparisons pass through actual entry switch. Warmed ABBA x2:
baseline191.20–193.91ns versus candidate194.01–197.01ns; instruction saving only
~1.4%, not R768's standalone16%.70051exit0. No full module rebuild or deployment.
Same-policy single-chunk comparison, not installed whole-module/game proof;
profile warnings retained. Close this implementation, no more inline attributes.
Full performance/stability/PRD remains open; next revisit unresolved malformed
XF provenance and broader state-lifetime opportunities, not repeat tiny probes.

**R768 complete-transform FP inlining screened; not deployed.**
Actual44-instruction emitted body with unchanged strict arithmetic passes22,528
CPU/RAM/host-flag comparisons in ASan/UBSan and release across every entry,
RN/NI and special/raw FP patterns. Warmed ABBA shows~16% fewer process
instructions in this standalone fixture; CPU170.75–178.01ns versus145.36–153.59.
Static function grows1570 to5519 instructions. This is not installed ThinLTO/PGO
or gameplay evidence, and falls short of the review's2x work-reduction screen.
No blanket inlining promotion/full module build. Next exact-build bounded
code comparison to resolve whether benefit survives real compiler policy;
callbacks/faults and representative coverage remain. See TRANSFORM-INLINE-EXPERIMENT.

**R767 cutscene fidelity coverage extended; no product promotion.**
Freshly compiled original-module and native compatibility probes completed
PrologueA frames1/500/2000/4000/5000/5590. Across2,119,680 output bytes,
four differ, each by1; frames1/500/4000 are exact. Original paths pass exact-once
DMA coverage and boundary guards. This is sampled offline fidelity, not full
movie parity, audio sync, device acceptance or a new speed improvement.
Native candidate remains private opt-in; normal app unchanged. Cutscene
feasibility already established; do not extend this into another throughput or
opening replay loop. Return to material gameplay-native execution work under
the external review's effect-size and correctness gates. Full PRD remains open.

**R766 value-FP interface screened; silent decoder-request gap fixed in source.**
Value-in/paired-value-out add/sub/mul prototype passes192000 full-state/host-flag
cases in UBSan and release. After matching internal inlining on BOTH sides,
three-op candidate19.44–19.53ns loses to original18.75–18.90ns; no promotion or
module build. Earlier sanitizer/unmatched-policy timings are not speed evidence.
Normal Simulator app nativeTHP OFF versus separate private thp-app ON confirmed.
Host now warns if NativeTHP YES is requested in an unsupported build; actual
preprocessor gate test passes. Installed app unchanged. Next review native
cutscene candidate's remaining acceptance gates and correct build selection,
not more small FP interface/attribute tuning. Full original PRD remains open.
Host compile-check81301exit0 after repairing stale generated/GXRuntime include
paths and matching ARM64 definitions. Vendor headers treated as system headers;
host warnings remain errors. Warning source has not yet been packaged/launched.

**R765 deferred timebase arithmetic screened; no product integration.**
Audited actual GXRuntime/C module, direct TB reads/writes, SyncIn/Out, lockstep
snapshot and trace boundaries. Six generated mftb calls in two chunks are static
sites, not complete observer coverage or dynamic counts. Isolated deferred
accounting passes62,208 boundary triples and1million mixed events under ASan/
UBSan. Sparse-read arithmetic saves about1.8ns/charge locally; every-charge
advantage does not repeat. No material whole-game benefit case yet, so no full
module build or standalone timing tweak promoted. Retain tested building block;
next broader native state-materialization/shared execution work. App unchanged.

**R764 live CPU-time split parks vector acceleration.**
Signed appe2f9c933/coreceda1909 installed; visually verified plaza before fresh
marker. Selected first Run capture:80.602s CPU,14,145 native/3,426 non-native
samples, clock_errors0. Non-native routing estimate2.0809% ±0.0872percentage
points nominal; native101.35% ±4.14pp raw, reflecting sampling/clock overhead.
Not normalized, not exact shares/FPS. Stop menu paused/resumed Run: explicit
--run1 excludes separate0.669s stop-tail report. Native bursts clearly dominate;
return to substantial native state/timing/shared-FP overhead, not vectors.
Native Stop failed0/smc_failed0; runtime53350exit0; save99d432d5 unchanged.
One M5 remains booted/no game. Host empty-clock mean389.457ns is a warning,
not Simulator calibration/subtraction. Full PRD remains unfinished.

**R763 sparse CPU-thread native/non-native cost probe built.**
Opt-in fixed sampler brackets whole native bursts and non-native routing with
approximately1/256 clocked spans; reports actual CPU-thread capture denominator,
sample sums/squares/max and clock failures at Run return. Mandatory fresh marker
allows scene selection; no histogram required. Default no clock/allocation.
ASan/UBSan accounting, source scopes, patch0029/0027 roundtrip and prior fallback
tests pass. Incremental Simulator core6078exit0; not packaged/installed yet.
Next RUN-COST-EXPERIMENT.md bounded plaza capture and overhead qualification;
no measured cost split or FPS gain yet. Full original PRD remains open.

**R762 fresh installed-build plaza sample weakens vector priority.**
App0078ae5d verified installed, histogramOFF/nativeTHPOFF. Visually reached
Star Festival plaza and verified same scene after20s sample (30053exit0).
1695 CPU-thread wall samples:9 interpreter ancestry,4 shared MMU/I-cache/HLE,
96 recognized waits;236 Run self and69 chassis self. Not CPU-time percentages
or exhaustive fallback attribution. Exact binary Run offsets1504/1300 shown
in the collapsed sample map to AOT-side bookkeeping/dispatch, not the fallback
loop; cannot assign all236 to those two offsets. No vector rewrite justified.
Native Stop failed0, runtime1197exit0 after idle termination; save99d432d5
unchanged, sole M5 left booted/no game. Sample/parser tests/artifacts retained.
Next distinguish Run AOT-state/timing overhead from fallback chassis cost with
a bounded measurement; do not restart vector microtuning or claim FPS gain.

**R761 dispatch-only vector candidate fails cost screen; not integrated.**
Implemented isolated fixed function-pointer dispatch from actual interpreter
tables. ASan/UBSan tests prove operation selection/operand identity at121 entries
and rejection of3872 mutations; operation-body spies do NOT prove semantics.
Release ABBA dispatch-only timing: baseline4.35133, guarded7.07893,
guarded6.72917, baseline4.37446ns/instruction, identical checksums. Guard cost
outweighs removed table dispatch. No app build justified; stop this variant.
Next whole-fallback CPU-cost qualification before broader chassis/batching work.
No runtime change or FPS claim; full original PRD scope remains open.

**R760 fixed vector recognizer implemented; sanitizer tests pass.**
Isolated apple/experiments/vector-execution/plan.h covers all121 interior
instruction positions, including the generic default-handler branch. Exact
pinned DOL comparison passes; all3872 single-bit mutations, unsupported entries,
unaligned PCs and high-address aliases reject. No guest memory or state access;
recognition consumes only a caller-supplied fetched word. Test registered in
repository checks. Not wired into runtime: actual interpreter differential
execution and net-cost gate remain next. No new build, Simulator run or FPS gain.

**R759 vector execution contract and existing-backend boundary audited.**
Read actual SingleStepInner, MMU I-cache fetch, cached interpreter data emitter,
timing loop and static core cache ownership. Cached interpreter uses nonexec
pages but isn't a drop-in AOT fallback. Selected bounded static-vector plan
experiment with original operation semantics/fetch/hook/budget/rfi contracts;
no global backend switch. VECTOR-EXECUTION-EXPERIMENT.md records gates and
<8%net-benefit stop rule. Implementation/differential execution still pending;
no source behavior, build, live run or speed gain this turn.

**R758 live plaza vector RAM matches exact DOL templates.**
All500/800/900 generic152bytes match with expected exception numbers; c00
syscall28bytes match. vector-comparison-r758.json records hashes/no differences.
Visually confirmed same plaza, one-shot trigger, native Stop failed0, save99d432d5
unchanged; idle app terminated/session72830exit0. Source identity established
in RAM, not instruction-cache equivalence/later immutability. Next bounded
guarded execution/cost experiment preserving HID0/MMU/rfi/cycles and fallback.
App0078ae5d/core17f82b9a, nativeTHP explicitly OFF; no timing improvement claim.

**R757 trigger-time physical vector snapshot compiled.**
At existing one-shot capture boundary, dump256bytes each at500/800/900/c00
from CPU-thread physical RAM. Null/small buffers reject; no per-step reads or
instruction-cache claim. Tests verify exact four-line output and bounds plus
expected DOL exception patches/mismatch rejection. Core68814 exits0; app not
rebuilt/installed yet. Canonical0027 updated/reverse-checks. Next package and
trigger in same visually verified plaza; no native-vector candidate enabled.

**R756 exception-vector roles and DOL templates identified.**
Exact DOL unique system-call template804aab88/28bytes and generic exception
template804a1ca0/152bytes. R755 PC paths match7instruction syscall438498entries;
34instruction generic paths external31034,FPU20433,decrementer42720entries.
Source routing confirms vector roles; runtime installed bytes still unverified.
Current generated syscall template falls back for three HID0 accesses, so
simple relocation would not remove all interpreter cost. Next runtime vector
byte comparison and cost-qualified candidate, preserving exception/MMU/cache/
cycle behavior. Artifactexception-templates-r756.json; no app or code-path change.

**R755 zero-loss plaza fallback census identifies low-memory priority.**
App7adf2a6e/core61500bf1 built/installed; runtime71606/PID451. Visually reached
Star Festival plaza via title/file1/story, marker then capture-start804ab358.
Plaza visible before/after; native Stop failed0, session cleanly ended after
idle app termination. Save99d432d5 unchanged, sole M5 remains booted.
Census6326386events/187keys/dropped0:6271844 low-memory (99.1379%),54431DOL
hook,111other. Low blocks c00=3069486,900=1452480,500=1055156,800=694722.
This is interpreter step distribution, NOT share of CPU time. High-address
startup traffic nearly absent. Next map exact vector bytes/semantics and cost.
IMPORTANT actual CMake nativeTHP=OFF despite launch request; do not claim native
movie enabled or compare this run to prior THP-on timing. No FPS gain claimed.

**R754 scene-triggered fallback capture built for Simulator.**
With FALLBACK_PCS=1 and GALAXYPAD_FALLBACK_START_FILE set, no histogram records
until a fresh marker is created after visual scene verification. CPU polls once
per1024timing slices; one-shot activation logs actual guestPC/nativecounter.
No marker deletion, no per-step file I/O; legacy whole-session mode retained.
Actual init/poll fragments pass sanitizer trigger tests; wiring/summary pass.
Core53457 terminal exit0, ios-core-r754.log. Not provisioned/installed yet.
Next package then use NEW absent marker path, observe scene, create marker,
verify capture-start, and clean-stop. Marker alone never proves gameplay.

**R753 diagnostic loss reduction passes recorded-key replay.**
Census now32768slots/16bounded probes and mixes high address bits before
masking;512KiB allocated only when opted in. R751 retained3916keys/5801917events
replay with0drops. Missing keys/order from lossy original remain unknown;
this is not live zero-loss proof or performance gain. Focused wiring/sanitizer/
summary tests pass. Canonical0027 updated/reverse-checks, bootstrap hash updated.
No rebuild/install yet: add phase separation before next diagnostic build.

**R752 fallback PCs mapped to exact initial image ranges.**
DOL text80004000..800064e0 and800070a0..8052d280; initial apploader loaded
81200000..8123b73c, entry81200294. Recorded3449008steps lie outside those
initial ranges;2315199low-memory,37710DOL text. No observed initial-loader PCs.
This does not identify runtime relocations or steady-gameplay cost. Added
header-based mapping tool with image hashes and boundary/truncation tests;
focused pass, suite registered. Artifactfallback-image-ranges-r752.json.
Next phase-separated lower-loss runtime census and executable-byte provenance,
not speculative registration of high-address code. No app/module changes.

**R751 authorized Simulator switch; first actual fallback census captured.**
User explicitly authorizes switching without repeated permission questions.
M4 shut down before M5 boot; sole DE8E956F. Installed signed2bdf90ee candidate,
save99d432d5 unchanged. Runtime77298/PID98808 clean native Stop at04:22:09,
failed0/smc_failed0, then idle app terminated; session exit0. No game remains.
Startup census total7465985, recorded5801917, dropped1664068 (22.29%);3916keys.
Recorded prefixes91=3144947,00=2315287,92=303973,80=37710. Not exclusively low
vectors, but startup/partial counts aren't steady-gameplay costs. Next address
mapping plus phase-separated capture and loss control. Logios-runtime-r751.log,
summaryfallback-pcs-r751.json. Data now5D8104BD-10AF-4224-99F6-76AB1256EA22.
Prior shared-Simulator blocker resolved. No graphics repro or FPS gain claimed.

**R750 live validation blocked on shared Simulator availability.**
M4/iOS18.5 device08636791 remains sole booted Simulator, unchanged across
R748–R750. No GalaxyPad process. Signed candidate verifies and full R748b
suite passed; useful preparation is complete. Await permission to switch or
release of that device. Do not shut down another project's session or boot a
second Simulator. Goal blocked, not complete; retain candidate and saved data.

**R749 full R748b suite passes; XF bootstrap ordering repaired.**
Same suite2589 terminal exit0, ends Repository safety checks passed. Separate
new XF overlay round-trip test passes byte-exact temporary peel/reapply and
live-source immutability. Found0028 blocks0024 reverse detection; bootstrap now
peels0028 first and restores it on error/reapplies after0024. Shell syntax and
bundle signature pass. Full bootstrap not run; no claim all overlay chains
were validated. Latest app remains ready/uninstalled; other M4 still booted.

**R748 app packaged; Simulator signing repaired; full checks rerunning.**
Provision/app87275 exit0. Bundle verification exposed resource seal mismatch:
Simulator build now ad-hoc signs AFTER resource copy and verifies; device lane
unchanged. Rebuild96322 exit0, signed app2bdf90eecf95ca5268d5121dfc48d207aa640b7d78d8c0ea9e640cf3f140f07e;
core38eab9cffd4ded4b22e7e4e1d7c7781c8de7174e0b3ba997dc3eb68fb7292fe8.
Full suite26075 failed older EFB hook source pin due to exact new histogram
block. Test now removes only that known block before original hash checks;
focused EFB passes. Full rerun2589 LIVE, generated/check-r748b.log; poll SAME.
Not installed. Other M4 remains sole booted device; asked user to release lane
or authorize switch when appropriate. No game/save or other-project mutation.

**R747 failure-only GX origin diagnostic built; not installed yet.**
Malformed XF now reports main-fifo/display-list, preprocess flag, and active
display-list guest address/size. Other decoder clients report unspecified.
Formatting remains inside failing ASSERT_MSG branch; no parser/repair changes.
Actual helper tests pass FIFO/list/preprocess/unknown/stale-address cases;
existing624partial cases and window-bounds tests pass. Canonical0028 reverse
check passes; Simulator core39624 exits0, ios-core-r747.log. Next provision
candidate when the single-Simulator lane is available; preceding-refill history
still absent, so origin alone is not producer attribution. Other M4 stays open.

**R746 actual XF partial-input behavior passes focused regression.**
624 valid truncation/refill cases across1..16words pass ASan/UBSan with actual
extracted decoder case; malformed captured header rejects before callback.
No partial-command consumption bug reproduced. This is not whole-FIFO or
concurrency proof. Local Fifo.cpp changes affect wakeup/timing, not byte-copy/
compaction logic. Main FIFO and recursive display lists both call Run, so R742
offset0 alone cannot distinguish them. Next failure context must identify input
origin and preceding boundary before assigning producer fault. No new runtime.

**R745 UI recovered; R742 ended with malformed GX stream, no census.**
Runtime56672 terminal exit0 and PID89863 absent; this is launcher completion,
not clean core shutdown. Log at03:12:09 has XF assertion cmd2=00611600,
offset0/available34, no histogram/shutdown. Save99d432d5 unchanged. Actual bytes
start10 00 followed by six complete BP writes16..1b=0. Offline capture probe
passes; residual2+burst32 is a hypothesis, not proof of producer corruption.
Prior native Stop blocker no longer applies. CUA now works; another project's
iPad M4/iOS18.5 device08636791 is booted, GalaxyPad device shut down. Leave that
device untouched; do not boot a second one. Next investigate FIFO producer/
consumer command boundary with this concrete failure; retain assertion.

**R744 runtime evidence blocked on native Stop/UI recovery.**
Same PID89863 verified live03:29; no shutdown/census in R742 log. CUA Simulator
getApp times out again, third consecutive turn with this same external failure.
Diagnostic source/tests/build and analyzer are ready; patch reverse-check still
passes. Stop speculative optimization until the missing address evidence exists.
Need Chris to use three-dot Stop Game, or working CUA access. Preserve SAME
runtime56672/log/save; do not force-quit or start another simulator. Full goal
unfinished; recording blocked status rather than repeating unchanged polls.

**R743 census analyzer ready; native Stop still awaits UI access.**
PID89863 verified live at02:03 elapsed; CUA getApp still times out. Added
summarize-fallback-pcs.py with exact accounting, separate paths, alias retention,
drop disclosure and incomplete/mixed-session rejection. Focused tests pass;
current R742 log correctly rejects missing shutdown census. Asked Chris via
nonblocking question to use three-dot Stop Game if visible, not force-quit.
No runtime restart or performance claim. Next inspect SAME log/session after
native stop; do not mistake the analyzer's expected exit2 for runtime failure.

**R742 diagnostic app installed/running; UI access temporarily failing.**
Build/provision87179 exits0; app c45c54fb9cf435ebe6556e2da678d5dde2758ad97187bfd605f359297bf75387,
core725421349d14d2f32b72f622f0961b1f2dcf50a854ed698e2d212a2b2dbe4058.
Sole DE8E956F booted; runtime56672/PID89863 launched with FALLBACK_PCS=1.
Log generated/ios-runtime-r742.log, screenshot simulator-r742.png shows wrist
strap screen (not gameplay). CUA getApp times out even after session reset;
no native Stop or histogram dump yet. Revalidate same runtime, recover UI access
and clean-stop to obtain census; do not restart blindly. Save99d432d5 unchanged
after install. New data container08E9491E-C8E3-46DC-A455-1A170D70E08C.
Old installed executable backed up in generated/candidates/r742-installed-baseline.

**R741 fallback-PC wiring compiles for Simulator.**
Opt-in GALAXYPAD_FALLBACK_PCS=1 allocates a bounded census; default allocates
none. Forced/uncovered chassis and slow instruction-hook paths record pre-step
PCs; cache fast path excluded. Shutdown prints totals/drops and exact PC/path
counts. Canonical patch0027 reverse-checks; focused sanitizer/wiring tests pass
and suite registered. Incremental Simulator core79368 exits0 (15 steps).
No app provision/install or live capture yet; no game/booted Simulator. Next
package diagnostic core, preserve installed/save identities, then capture PCs.

**R740 mobile fallback-PC diagnostic started; runtime attribution still open.**
Identified three actual interpreter-step sites, excluding native cache fast-path
hook calls and desktop JIT. Added bounded diagnostic histogram and sanitized
tests (pass); not wired into product or captured live yet. Next opt-in lifecycle
and exact pre-step integration, then a single-Simulator address census. See
FALLBACK-PC-EXPERIMENT.md. No performance improvement claimed.

**R739 isolated NI-mode hint parked; no performance improvement established.**
800000 conversion cases match result bits, host exception flags and unchanged
FPSCR across four rounding modes and both NI modes. Original and hinted ps_add
each compile to84 static instructions. This does not measure dynamic cost, but
does not justify a module build. Actual linked ps_add already inlines arithmetic
and status helpers; blanket helper inlining is not a sufficient diagnosis.
No product source/module or installed app changed. See shared-state experiment.

**R738 integer-gap FPRF extension has insufficient demonstrated scope; parked.**
New conservative read-only census scans1322chunks:165regions, only1nonadjacent
addition (addi/li gap). Source hashes/addresses in generated/fprf-gaps-r738.json.
Focused positive/negative barrier tests pass; suite registered. No transformed
code/module build or speed claim. Do not expand one opcode at a time to rescue
this narrow idea; next shared helper lowering/state traffic with broader impact.

**R737 shared-state audit avoids repeating existing FPRF optimization.**
Current R387 strict adjacent-writer audit finds164 remaining sites/68chunks;
119decoder deferrals already promoted historically. Narrow provenance and
one-chunk entry splitting also have prior parked results. New boundary in
SHARED-STATE-EXPERIMENT.md: audit broader straight-line status liveness across
proven non-observing integer gaps, preserving callbacks/exits/FP observers and
all external entries. No new module build justified yet; no product edits/run.

**R736 direct-call trial not promoted; priority moves to shared FP/state.**
Reverse pair enabledCPU28.988783ms/VI vsdisabled24.533556; processinstructions
298.073222M vs286.856603M/VI. Initial5.66%CPU gain did not reproduce; instructions
increased in both pairs. Host/focus uncontrolled: do not claim universal regression.
No established material gain, so close this design for promotion per experiment
gate. Goal loop/active queue now prioritize shared FP/state with accuracy intact.
Both repeat captures/sessions cleanly exit0, fallback0/smc_failed0, saves106e
unchanged; no game remains. Detailed four-window table/limitations in experiment.
No installed app/module changed and no full PRD gate closed.

**R735 first enabled comparison: small gain, below architectural target.**
Same signedrunner871f4f/module6871db, fresh enabledR724 profile, runtime65580/
PID87354. bound1; nativeLoadState2 visually same GoodEgg before/aftercapture.
Capture42244exit0:1146VI/30.005s=38.1935Hz, CPU24.761164ms/VI vs26.247646unbound
(5.6633% lower); process294.600105M instructions/VI vs289.964938M (+1.5985%).
Single fixed-order pair, not repeatable/net-product win. Whole-run checks1,204,746,800
transfers1,203,316,401 confirms active path but is not matched-window dispatch/VI.
CleanQuit65580exit0, fallback0/smc_failed0, save106e unchanged; PID absent.
Next reverse-order repeat. If reproducibly<8%, close this design per gate rather
than promote or chase micro-tweaks. No installed app change; full PRD remains.

**R734 diagnostic module links; first unbound gameplay baseline captured.**
Module37737 completed exit0. SHA6871db5d16c9c6244e2b803fb5ecc3c2fc32941e56bdcae9a9395df4eef7fb24;
exports binding setter, loader ABI3/CPU3/3528bytes/1322chunks, codesign verifies.
Unbound R730 runner86966/session84704 booted explicit R724 profile; startup delay
sample showed game-directory hashing. Native LoadState2 restored correct hanging
Mario Good Egg scene, visually checked before/after. Capture95366exit0:
30.009s/1084VI/36.122Hz, CPUmean26.247646ms/VI,289.964938M process instructions/VI.
Zero invalid/reset intervals. Clean native Quit84704exit0, fallback0/smc_failed0;
save106e8248 unchanged. No game/simulator should remain; verify before next launch.
Next SAME module/runner/settings with GALAXYPAD_GUARDED_DIRECT_CALLS=1 in untouched
direct-enabled-r724 profile. No paired improvement or acceptance claimed yet.

**R733 all diagnostic objects compiled; ThinLTO link confirmed active.**
Same build37737 live after bounded waits; log1331/1333, all chunk/binding object
steps complete. LinkerPID86383 confirmed at07:53 elapsed,650%CPU,~1.2GiB RSS;
CPU time advanced to52:26,36GiB disk available. Same37737 re-polled live.
Quiet log is active linking, not terminal failure. Poll SAME37737 next; do not
restart. No simulator/game running. Runner/profile preparations remain ready;
module export/signature/runtime verification still waits on successful link.

**R731 simulator clean-stopped; diagnostic module still building.**
Stopped paused75679 via native menu, runtime log01:41:15.881 failed0/smc_failed0.
Simulator save stillSHA99d432d5. Terminated idle app and shut down soleDE8E956F;
8698exit0, PID absent and no booted devices. No app/save/checkpoint deleted.
Module37737 remains live, latest1105/1333; poll SAME handle next. Desktop runner
and R724 profiles ready, no desktop game launched during compilation.

**R730 isolated diagnostic app bundle prepared and signature-verified.**
New generated/macos/direct-calls-r730/GalaxyPad.app contains guarded runner,
dedicated Info.plist and desktop Sys resources; no game/module or normal launcher.
Bundle ID org.galaxypad.directcalls.diagnostic. plutil/codesign verify pass37936
exit0; signed runnerSHA871f4f8726cf1e12c56022a61dfbd013cbfa6614ce68ee6873982e869a9f4faf.
Not launched. Use explicit --game/--module/--user-dir R724 profile. Module37737
still live, latest910/1333; simulator remains paused. Normal installed app untouched.

**R729 guard-enabled desktop runner linked and symbol-verified.**
Runner87774 completed exit0, final link succeeded (duplicate-library warnings).
SHA b5151c2f38f6b76638e93f9c57e0a5fb156f165068828fa0e83cad953ef5c2c5.
nm confirms HookDirectCallBoundary; binary strings contain versioned setter,
enable flag and bound/checks/transfers diagnostics. Not a runtime binding proof.
Module37737 remains live, latest819/1333; poll SAME handle next. Simulator still
paused until compiler load ends. No installed app change or benchmark yet.

**R728 verified build wait; no source/runtime changes.**
Same module37737 and runner87774 each polled with bounded50s waits; both remain
live and advancing, latest709/1333 and196/232. Last disk check36GiB available. No build failure
observed. Simulator stays paused. Continue these exact handles, then inspect
links before launch; no new build, restart, measurement or performance claim.

**R725 verified build wait; existing CPU/VI measurement path checked.**
Module37737 live350/1333 after bounded50s wait; runner87774 live74/232 and
re-polled. No build failure observed. Simulator remains paused. Existing VI
recorder uses CLOCK_THREAD_CPUTIME_ID in CPU-timing VICallback->VI end-field
event, buffered until post-join flush. Wiring and summary tests pass again.
No added instrumentation or new performance result. Next poll same build handles.

**R724 matched disposable profiles ready; both builds still running.**
Created generated/runtime/direct-unbound-r724 and direct-enabled-r724 from the
retained R462 Config/Wii/config.ini/slot2 only; no caches/logs copied. Config diff
empty, both checkpointSHA74e453b5 and saveSHA106e8248 verified; own input FIFOs.
No runtime launched or restore compatibility claimed. Module37737 live221/1333,
runner87774 live40/232 at last poll. Continue SAME handles, simulator stays paused.
Next link/symbol checks then clean simulator stop before any desktop game launch.

**R723 diagnostic module and guard-enabled runner builds in flight.**
Module session37737 remains live and advancing (R722log). Backed up current
desktop runner to generated/candidates/r723-runner-baseline/moderngekko-run;
bothSHA13354ea966aeca76f893c769ee81c0b85ce260dcefa14c80debf8f3459c8f53a.
Started moderngekko-run build session87774, parallel1, log
generated/direct-call-runner-build-r723.log (232-step dependency rebuild).
Module parallel2 plus runner parallel1; no runtime measurements. Both handles
re-polled live. Poll SAME handles next; simulator stays paused until builds end.
No new executable/module link or performance result yet. Packaged app untouched.

**R722 full isolated diagnostic module build running.**
Verified compile graph:1321 overlay chunks,1 original chunk,1 binding, no duplicate
sources, ThinLTO/O2/strict FP.36GiB available at start. ExistingPID75679 verified;
native menu opened to pause simulator during compile. Full module build started
session37737, log generated/direct-call-build-r722.log, parallel2; compiling
chunks with no observed error so far. Poll SAME live handle next; no restart on
timeout. Simulator remains deliberately paused until build ends. No linked
candidate yet. Then link guard-enabled diagnostic runner and prepare matched
baseline/active comparisons; old PGO/JIT measurements are context, not controls.

**R721 broad isolated caller overlay prepared and configured.**
prepare-direct-call-overlay.py86148exit0:150,753 guarded sites,1321 changed chunks
of1322,361MiB in generated/direct-call-r721. Source/override hashes and coverage
recorded in manifest.json written last. Selected generated tree untouched.
Experimental CMake now accepts and hash-validates overlay sources against target.
Configure generated/build/direct-call-r721 session63234 completed exit0 after
123.1s, reporting validated overlay. No full module build launched. Source-shape/
differential tests pass again. Next validate broad graph before diagnostic
link/materiality run; configuration may regenerate for the parsing-only edit.

**R720 retained profile rules out the one-chunk candidate as a useful benchmark.**
1322 historical PGO chunk entries total2,895,966,494; test chunk0166 has247,493
(0.00855%). Top20 destinations account45.9042%, not removable-call share or CPU
cost. Next broad eligible caller overlay, not only hot callee chunks. Keep the
single-chunk build as integration proof only. No runtime change/performance gain.

**R719 diagnostic build wrapper configures and compiles real candidate objects.**
New experimental CMakeLists wraps vendor module target, replacing one explicitly
selected chunk and adding binding.c without editing vendor/selected sources.
generated/build/direct-call-r719 configure89506exit0; transformed chunk0166 and
binding object build65636exit0 with arm64 ThinLTO, O2, strict FP. Generated module
tables still report1322 ranges. No complete module/runtime link or benchmark.
Sole Simulator/PID75679 revalidated, paused through menu during object build and
resumed afterward. Next diagnostic coverage/materiality decision and full link
only when justified; installed module remains unchanged.

**R718 transformed nested fixtures execute with matching boundary state.**
New test-direct-call-differential.py applies actual chunk transformer to two
generated-shaped caller fixtures and compiles original/transformed executables
with actual binding/transfer helper. Each passes36 binding/depth/rejection modes
under ASan/UBSan: five boundary PC/LR/value/cumulative-charge records match the
unbound dispatcher baseline, final saved LR matches, total53 cycles, depth0.
Registered in suite. Guest bodies/runtime accounting are explicit fixtures, not
actual gameplay or full runtime proof. Next macOS diagnostic module integration;
no installed module change or FPS improvement claimed.

**R717 actual guard and transfer helper pass nested execution tests.**
Extended test-direct-call-boundary.py to link actual binding.c/transfer.h with
extracted runtime guard and outer charge code. Five nested cases verify normal
return, forced fallback with matching outer continuation, pause, synchronous
exception and depth exhaustion. Exact cycles/timebase/remainder, balanced depth,
unwind and resumed-caller counts pass ASan/UBSan (exit0). Runtime services and
callee bodies remain stubs; not full generated-module execution or a speedup.
Next generated differential fixture and macOS diagnostic integration.

**R716 isolated generated-call wiring reaches actual chunk compilation.**
prepare-direct-call-chunk.py produced generated/direct-call-r716/chunk_0166.c
with76 guarded sites; clang C11 syntax check passes against real GXRuntime CPU
header. Original generated tree remains untouched. Transformation preserves
continuation switch-entry suffix cycle charges, canonical target membership,
LR/PC and fail-closed source shapes. Focused transformation tests pass.
Not linked/executed or benchmarked. Next differential execution, especially
nested unwind with the real runtime guard; full goal remains unfinished.

**R715 replacement-aware experimental transfer glue tested.**
Added transfer.h: balanced depth, guarded target and continuation, module
replacement-before-original ordering, early-return propagation without PC
rewrites. Actual helper/binding pass eight ASan/UBSan cases; registered in suite.
No generated sites or installed binary changed, no performance gain measured.
Next isolated call-site wiring and nested accounting/SMC integration checks.
See DIRECT-CALL-EXPERIMENT.md for test scope and remaining requirements.

**R714 host direct-transfer guard wired, compiled and accounting-tested.**
Default-off GALAXYPAD_GUARDED_DIRECT_CALLS=1 optional dynamic-module setter,
detach-before-unload, target/continuation guard with current validation/hook/
timing/exception/run-state checks. Denied boundary latches unwind; already
committed glue does not receive an extra outer minimum cycle. Existing normal
empty dispatch retains minimum1. Canonical0026 f9c905b4 registered/reverse-check.
Actual guard/outer-body stub tests pass ASan/UBSan; macOS Core.cpp/Run.cpp objects
compile44167exit0. No linked runtime/module or enabled direct-call run yet.
Next wire isolated generated call/continuation sites and module replacement
routing, then integrated differential tests. Current75679/d34fe135 resumed intact.


**R713 experimental direct-call binding implemented and dynamically tested.**
New apple/experiments/guarded-direct-calls/binding.{h,c}: optional versioned
module setter, absent/rejected binding returns to dispatcher, explicit detach,
no CPUState ABI change. Actual shared-library dlopen/dlsym lifecycle test passes
ASan/UBSan15290exit0 and is registered in repository suite. Not yet wired into
core/emitter; no full module build or performance result. See DIRECT-CALL-EXPERIMENT.
Current75679/d34fe135 untouched. Next actual boundary guards and cycle-accounting
integration, not more census/profile work.


**R712 current direct-call census complete; guarded integration boundary specified.**
Actual1322chunk source fingerprint1a0cc009. DirectBL165220:150916 return to
chassis,14304local goto,0direct calls. Static site counts, not dynamic cost.
New census script/tests pass; artifact generated/direct-call-census-r712.json.
DIRECT-CALL-EXPERIMENT.md identifies target AND continuation validation,
host-interception obligations, and exact-once cycle/timebase accounting; early
guard flush must not incur another outer minimum1cycle on glue-only unwind.
Next implement isolated versioned direct-transfer binding through existing
dynamic module loader; preserve CPUState ABI and default dispatcher behavior.
No unsafe flag, module rebuild or performance gain claimed. Current75679 remains.


**R711 independent review adopted with corrections; architectural work now first.**
Saved full submitted review in INDEPENDENT-PERFORMANCE-REVIEW-2026-09-09.md;
source-checked disposition and decisive experiment in REVIEW-RESPONSE-2026-09-09.md.
Goal loop and performance queue now prioritize guarded cross-chunk call/return,
then shared FP/state work, then named mobile fallback. Stop small lookup/movie/
checkpoint-memory iterations as default. Preserve all original PRD gates.
Corrections: current1322chunks, R705 named exclusive weights89 not140; neither
wall-stack counts nor whole-run14.02charged cycles/dispatch prove the review's
precise cost/rate claims. Unsafe prototype lacks required guards; not enabled.
Currentlive75679/session11407/d34fe135, ios-runtime-r710b.log. R710 deployed
memory candidate, corrected filtered INFO log to stderr, rebuilt successfully.
No candidate-owned restore or live released-byte proof yet; this lane is parked.
See response document for exact app/core/patch identities and current containers.


**R709 undo-memory candidate links; full regression suite PASS.**
Core17086exit0, provision/app12869exit0. Candidate appSHA
dd96031a16c768efe9b2ab399dd3fdf18f994118368ad9907f8e1eb23af4fe75;
provisioned coreb5f6a1c95129470aa7debd9df2f6fbdb16d7dbfeac412de66824b6d9095330a8.
nm confirms new LoadAsWithoutRetainingUndo and load-flow symbols in linked app.
Full check-repository.sh86990exit0, generated/check-r709.log ends safety checks
passed. Current installed84f0fe05 backed up to generated/candidates/r709-baseline/
GalaxyPad.app; SHA verified. Candidate NOT installed yet. Same71970/session84246
resumed after native-menu pause for tests/build. Next clean stop/install candidate,
create its own same-build checkpoint, and verify live release-byte log plus
restore/movement. Old BFA5 checkpoint must remain identity-guarded, not bypassed.


**R708 development-checkpoint undo-memory candidate implemented, not deployed.**
New State::LoadAsWithoutRetainingUndo retains rollback throughout loading and
releases its buffer only after success outside input recording/playback, before
callbacks can start another load. Normal LoadAs remains unchanged. Simulator
development restore calls the opt-in API; exact app/module/NAND guards preserved.
Canonical0025-development-checkpoint-undo-release.patch registered, SHA6f34f55f.
128 actual-flow stub cases plus default retention pass ASan/UBSan; checkpoint
identity/path tests pass. Actual Simulator State.cpp object builds52604exit0.
Full suite, final core/app link, deployment and live released-byte check pending.
Current71970/session84246/84f0fe05 unchanged, resumed after compile; R707log.
This addresses avoidable retained memory after checkpoint loads, not pre-load
CPU slowdown. No measured memory saving or FPS benefit claimed yet.


**R707 candidate plaza checkpoint survives clean restart; currentPID71970.**
Same-build84f0fe05 checkpointBFA5E5B8 restored in66439; moved2s, visually verified
different position, restored again to plaza entry. Native Stop clean at00:14:38
failed0; final nativeTHP5591accepted/0fallback. NANDGameData99d432d5 unchanged.
Terminated idle app after clean shutdown; launched same installed app and flags
in soleDE8E956F. NewPID71970/session84246, log generated/ios-runtime-r707.log.
Restored BFA5 from fresh wrist-strap screen; plaza visible,1s movement responded,
then restored again to retain entry scene. Same-process and cross-process restore
now verified for THIS candidate checkpoint, not cross-build compatibility or
later movie decoder reinitialization. BFA5 size44821637,SHA50505369e0c328829927
650cb39fb5814b6049e28a2422e4417615c8f004c24b. Undo-load buffer now used in this
run; previous no-undo baseline no longer applies. No controlled speedup claim.


**R706 presentation API audit; hardware target still unavailable.**
Same66439/84f0fe05 kept live. Installed Simulator MTLDrawable header omits
addPresentedHandler/presentedTime; Mac and physical-iOS headers expose them.
No unsupported selector or false screen-FPS counter added. devicectl: no devices;
codesigning:0 valid identities. Hardware proof remains open, not a blocker for
CPU optimization. R705 fresh5s gameplay sample retained in plaza-sample-r705.txt:
CPU428 wall-stack samples,37float-future waits,12BlockingLoop waits,15Dispatch
leaves; broad generated work, no new single dominant SDK routine established.
Read-only review prompt delivered at user's request; no reviewer result received.
No build/source/runtime settings change or performance gain this checkpoint.

**R704 actual thread CPU time separates gameplay from a controller warning.**
Same66439/84f0fe05/soleSimulator. Extended external thread-state probe to accept
Simulator GalaxyPad and CPU/Video names, verify process birth identity, and retain
nanosecond CPU counters. Controlled worker self-test passes. First30s capture
51.38 frame-event Hz was visually found with a controller-disconnection dialog;
do NOT classify it as normal gameplay or improvement. A pulse dismissed it.
Visually bracketed unobstructed plaza repeat:37.622660 frame-event Hz, speed
0.614–0.687; CPU25.943207s/29.993576s=86.50% of one core, Video11.264737s/
29.913406s=37.66%. No compressions/swapouts,4swapins. Overlapping but not exactly
aligned capture intervals; no per-frame CPU-cost claim. CPU work is substantial;
non-CPU remainder mixes waiting/descheduling. No core-type/frequency proof.
Artifacts cpu-gameplay-r704.csv,video-gameplay-r704.csv,gameplay-cadence-r704.json.
First capture thread-cadence-r704.json has a stale scene label; retain raw evidence
with this correction. Next prioritize representative CPU execution hotspots,
then synchronous graphics costs; visual scene checks required before AND after.
No app rebuild, performance gain, actual display-rate or full-gate claim.

**R703 dispatch candidate movie hook and return verified; gameplay still slow.**
Same66439/session56873/84f0fe05/soleDE8E956F, now stationary invaded-plaza entry.
Traversed festival to PrologueA. Movie visibly advanced/returned;45s capture
59.952020 frame-event Hz, VI~59.94/speed~1. Eighteen emitted native windows5415
calls/0fallback,mean1.654606ms; final partial unflushed, no5591-total claim yet.
Post-movie30s:37.557276Hz, speed0.577–0.696. Prior35.51Hz is not a controlled
comparison or proven gain. No profiler/build/settings changes during captures.
Fresh candidate plaza checkpoint BFA5E5B8-9F1C-470E-AFC3-0C0F5AE029E2.sav final
exists (~43MiB), alongside44ECfestival and oldDAF88. New restore not yet tested.
Latest checkpoint preference now plazaBFA5; no undo-load buffer used in this run.
Artifacts candidate-movie-r703.json,candidate-postmovie-r703.json/.png; sameR700log.
Next retain this scene for gameplay work; do not repeat opening/THP microbench
or small dispatch tuning as the main performance strategy. No full gate closed.

**R702 candidate reaches Star Festival and writes its own checkpoint.**
Same66439/session56873/84f0fe05/DE8E956F. Selected Play This File, advanced story
pages, visibly reached festival and moved forward4s. Now at foot of flower-lined
hill beyond starting circular flowerbed. Story~60 events, gameplay~40–50; no
performance acceptance or dispatch gain claimed. No graphics assertion seen.
New unique checkpoint44EC9B1E-3DFB-447D-8AED-48A748DA0834.sav at festival START,
data63F66D50/.../GalaxyPad/DevelopmentCheckpoints. Final file exists (~40MiB);
this particular file's restore not yet tested. OldDAF88 checkpoint retained,
old app/preferences backed up in generated/candidates/r695-baseline. Current
last-checkpoint preference now refers to new build. No restore/undo buffer used
in this process. candidate-festival-r702.png; log remains ios-runtime-r700.log.
Next continue same run up hill toward plaza/movie, then test native THP patch
with0030 and return to gameplay. No rebuild/restart or extra Simulator needed.

**R701 full suite passes; dispatch/quiet-interval evidence does not show major fix.**
Same66439/session56873/84f0fe05/soleDE8E956F preserved at selected Mario file.
3s10ms selected-file sample11367: CPU254samples,10 ModDispatch,20float-future waits;
Video253samples,20EFB completion,71condition waits. OldR695same scene hadCPU254,
12ModDispatch/21future,Video254/18EFB/68condition. Counts are sampled wall stacks,
not exclusive CPU time, controlled benefit or significance. No major gain shown.
Paused via native menu for full check-repository.sh29506, exit0; check-r701.log
ends Repository safety checks passed. Includes checkpoint/XF/dispatch regressions.
Resumed, quiet45s capture29047 (no intermediate tools/screenshots/profiler/build):
46.053140 frame-event Hz, speed0.573–1.0025, zero compression/swapouts,4swapins.
Quiet observation alone does not remove slowdown; no claim host effects excluded.
Artifacts dispatch-selected-sample-r701.txt,quiet-selected-r701.json. No product
source or settings changes. Next continue candidate into gameplay/native movie
hook test and retain its own checkpoint; stop repeating file-select microchecks.

**R700 dispatch candidate deployed; no FPS benefit established.**
CurrentPID66439/session56873, soleDE8E956F, installed84f0fe05 verified, module
unchanged3acdcddc. Selected Mario file/Play This File visible. Logios-runtime-r700.log.
Prior65953 clean exit failed0 at23:28:05 before terminate/install. Preserved old
4942411a app, checkpoint and preferences under generated/candidates/r695-baseline/.
New bundle8711DD6A-1FD2-4D3A-B8EE-336B1A2BA7AC,data63F66D50-27D8-4C6B-9026-
195F10A64B88. Save still99d432d5. Old checkpoint635bcb49 matches private backup.
Restore on new app refused at23:29:46 (identity mismatch), no state loaded.
Corrected PointerPitch22 launch spelling. File-selected30s capture36551 yielded
46.505595 frame-event Hz, no swap/compression growth,1297decompressions. This is
NOT evidence of improvement over old run54.4Hz or a controlled regression result;
host/scene timing varied. No malformed-XF recurrence yet. Candidate gameplay and
native movie hook after0030 not exercised yet; no new checkpoint for this build.
Next continue candidate into representative gameplay, create its own guarded
checkpoint, compare CPU dispatch samples and scene timings before promotion.
Full goal remains open; no extra Simulator, publication or unrelated app changes.

**R699 same-build checkpoint survives clean process restart.**
Old63074 native Stop exited failed0 at23:22:51; final nativeTHP5591/0.
Terminated idle host via simctl, verified absent, relaunched same installed
4942411a (NOT84f0fe05). NewPID65953/session12239, soleDE8E956F. Logios-runtime-r699.log.
Native menu restore23:24:13 at startup safety screen returned saved invaded plaza.
Forward3s41564 moved Mario near central ice block; screenshot confirms movement.
GameData.bin still99d432d5. Native THP after fresh-process restore/audio not tested.
30s capture64560:39.549088 frame-event Hz over26.599855s; zero new compression,
4swapins/0swapouts/7161decompressions. Not exact-position controlled A/B: fixed
wall-time movement covers different distances at different simulation speeds.
Artifacts relaunch-plaza-r699.json/.png. Same checkpoint/app/module identities;
cross-build remains blocked, candidate84f0fe05 built but NOTinstalled. Runtime65953
live in invaded plaza. Next candidate deployment/measurement with save preserved;
do not reinterpret this old-build result as benefit from0030 dispatch change.
Launch had redundant typo flag GalaxyPadDevNativePointerPitch22 NO; actual prior
GalaxyPadDevPointerPitch22 remainsNO in persisted settings. No pointer change claimed.

**R698 host pressure measured; dispatch fast-reject candidate built, not installed.**
Same live63074/installed4942411a/soleDE8E956F preserved, paused for compilation,
then resumed near central frozen Toad. New candidate84f0fe0567897035fb86a52de9454
b4e300b62933872822c22567a30e5937b4c; provisioned corea5a46e262095651c567addb264
256f1e97e9e8b0f5d7a2b80caa6ba02ccd26ee. No in-game gain claimed.
Baseline30s plaza:26.88671 frame-event Hz, zero swapin/out but298743 compressions
and124514 decompressions (16KiB pages). ChatGPT111%/renderer63% CPU at first snapshot.
Separate sample259/thread: CPU11 float-future waits and32 ModManager::Dispatch
samples under chassis+348; Video134 condition waits,9 EFB completion,45 RunVertices.
Counts are sampled wall stacks, not exclusive CPU percentages/sole-cause proof.
Added static-address rejection in Dispatch AFTER runtime_start and pending-return
processing. Earlier0029 changed HandlesAddress only. Canonical0030 hashbba8bb0e
registered; sanitizer tests for startup/null/state preservation/patch/return-SP
matching and reload pass. Core47715/app4124 exit0; no full suite this step.
vmmap snapshot:footprint521.3M,peak841.1M,writable403.9M swapped category (not proof
of disk I/O). Its 'corpse' label is snapshot type:63074 still live, logs advancing.
Checkpoint header uncompressed114630753bytes (~109.3MiB); upstream retains an undo
buffer after restore. Exact live undo allocation not measured; no change made.
Next test same-build clean relaunch/restore before replacing installed candidate;
exact-app guard prevents using old state with84f0fe05. Preserve checkpoint/save.
Then measure new dispatch candidate; do not claim lookup tests prove FPS gain.

**R697 same-process checkpoint save/restore and post-restore movement verified.**
Same63074/session23593/4942411a/soleDE8E956F; currently in invaded plaza near
central frozen Toad after post-restore forward3s input. Native menu save23:09:04
created DevelopmentCheckpoints/DAF88E8D-F375-4E39-8ED7-353C2CC9FA8A.sav,
43,875,609bytes in data583E547C. Moved Mario forward3s, visibly changed position;
native menu restore23:10:23 returned original position/camera. Another forward3s
again moved Mario, confirming input continues. Evidence checkpoint-before-r697.png,
checkpoint-restored-r697.png,checkpoint-input-after-r697.png and liveR695 log.
GameData.bin hash remains99d432d5. Restore opened SDIOSlot0 via DoState and created
app-private Load/WiiSD.raw; this is upstream restore behavior, not a game-save
write. No existing save/checkpoint overwritten. Cross-process restore, native THP
state continuity across reload, audio and full NAND persistence still unproven.
Same-build checkpoint now usable for repeat scene positioning within this process;
cannot load it across app builds because exact app identity is guarded. Next
measure CPU/graphics waits in retained slow plaza; no routine opening replay.
No product source change or performance gain this turn. Full goal remains open.

**R696 same session reaches post-movie plaza; movie/gameplay slowdown separated.**
Still63074/session23593, sole DE8E956F, same4942411a candidate/module/settings.
Play This File and story pages advanced with leased diagnostic input, visible
Star Festival traversal, PrologueA invasion movie and return to invaded plaza.
No checkpoint action used. Current Mario stationary in invaded plaza; retain run.
Movie capture59.918719 frame-event Hz, VI59.94, speed~1; post-movie35.509369Hz,
speed0.570–0.636. This is not screen-present cadence/audio acceptance.
18 emitted native decoder windows5415calls/0fallback, means1.553mswall/1.541msCPU;
final partial window unflushed, no5591-total assertion. Worst18.624ms/paired2.679ms.
No malformed XF recurrence so far, not a fix. Logs remain ios-runtime-r695.log;
new captures movie-r696.json,post-movie-r696.json/.png. No builds/profilers during
captures. Next validate guarded same-build development checkpoint at this useful
location, then investigate gameplay CPU/graphics synchronization without another
opening restart. Full PRD and original acceptance gates remain unchanged/open.

**R695 diagnostic candidate live; file-select crash not reproduced.**
One game63074/session23593, sole DE8E956F iPad Simulator, selected Mario file
screen (Play This File visible). No checkpoint action used. App4942411a874a6a78
c695a0538f7035763e8ade093437f91fa7073e9aa091af9e, coreabc8556711f3ee292f8fee4
c513b694a6c9628c3b251391950c39e5845ad4e60; module unchanged3acdcddc.
Bundle2375B099-16D6-4900-BAF9-A2DD4CABDBE4; data container relocated on install
to583E547C-ED32-4AC8-B7CC-067D9E9D4A58. Current GameData.bin hash99d432d5
matches preinstall and R693 backup. Same launch settings; fresh ios-runtime-r695.log.
Idle file list30s capture:59.13 frame-event Hz; selected file30s:54.40Hz,
speed estimates0.787–0.913 in selected capture. NOT screen-present counters.
Both captures:4 swapins,0 swapouts,0 compressions; no claim of no host contention.
File selection(.38,.66)+A succeeded visibly; no malformed-XF assertion through
22:53 local. Non-reproduction does NOT close the intermittent graphics defect.
Separate3s/10ms stack sample:254 samples/thread; CPU21 float-future waits,
Video18 PeekEFBDepth/Metal completion waits,68 condition waits. These are sampled
wall stacks, not exclusive CPU percentages or a complete frame budget.
Artifacts file-select-r695.json, file-selected-r695.json/.png,
file-selected-sample-r695.txt. No build/profiler during30s captures. Keep this
same runtime; next continue visible route or validate same-build checkpoint
at a useful location. Do not rebuild/restart solely to chase a nonreproduced
failure. Failure context is armed if it recurs; original full goal remains open.

**R694 bounded malformed-XF context built; not deployed.**
No game or Simulator running. Installed R693 candidate43b624f6 and its save are
unchanged. Added failure-only command-span offset plus <=32 bytes before/after
the invalid XF header; original assertion and decoding behavior are preserved.
No continuous FIFO dump, ring buffer, or successful-command formatting. Context
does not identify the corrupting producer by itself. Canonical Dolphin patch0024
SHA8ae3658143fc2f7cfaf3e2f35f48a1921d81b09088ebbf8e4607429902d94ab4
is bootstrap-registered; reverse-apply check and shell syntax pass.
ASan/UBSan helper bounds test passes for every offset in spans1–128; formatting
library stubbed, so this is not live decoder proof. Initial build caught incorrect
StringUtil namespace; corrected rebuild96210 exited0 (xf-context-build-r694b.log).
Core not yet provisioned/app rebuilt/installed. Next provision this core, rebuild
app, verify artifact identities, reproduce R693 file-select route on sole Simulator
with fresh log. Capture the failure window if it recurs; do not suppress it.
Performance queue updated in CUTSCENE-PERFORMANCE-PLAN.md; no performance gain
claimed and full original goal remains active.

**R693 candidate deployed; live simulation slowdown confirmed, then graphics assertion.**
NOgame/Simulator running now. Old52374cleanstop22:34:43failed0, nativeTHP12667/0
(5591+7076), not audio/displaycadenceproof. Backup generated/save-backups-r693/
GameData.bin SHA99d432d5 unchanged afterinstall/failure. Installed43b624f6 verified,
bundleD02C68A8-B335-471A-A952-826B9132D946,data7F79188A-A4E8-4844-8FCD-707B50FD74E5.
New61558/session12825 reachedfileselect; sameflagsplusDevCheckpointsYES.
Log generated/ios-runtime-r693.log confirms frameevents~23–32Hz,VI~20–33Hz,
speed~0.33–0.56: simulationitself slows, not merelydisplayreporting. Rollingstats
arenotidenticalwindowtotals. Checkpointaction NEVERused; nocheckpointcreated.
At22:37:46 graphicsGX_LOAD_XF_REG assertionstream_size_temp<16,cmd2=61E30E70.
AppreturnedtoSpringBoard,61558absent,consoleexit0butNOcleanruntimeexitmarker.
NoDiagnosticReport found. SoleSimulator shutdownafterevidence/savehashcheck.
Next investigate/reproducegraphicscommandstreamfailure on exactcandidate before
checkpointacceptance/performancepromotion; nevermaskinvalidXFsize. PriorR600
hadunknownopcodeFF,notproofsamecause. No newsourcechange thisturn. Fullgoalactive.

**R692 checkpoint restore/identity guards built; next actual deployment/test.**
Candidate43b624f64f67643ca5092683d3337092970f6a9a5ce3a92edc689e470ce63806
build74979exit0,checkpoint-restore-build-r692.log; NOTinstalled. Same52374/c00098d3
preserved,menu pausedduringbuild thenresumed. Restoreaction gatedbySimulator and
GalaxyPadDevCheckpoints. Save recordsUUIDfilename andSHA256ofapp,module,GameData.bin
inprivateNSUserDefaults. Restore requiresexactidentity,UUIDbasename,finalregularfile
32bytes..512MiB. No pending.tmpload; upstreamLoadAs handlesformatvalidation. Input
cleared; logsrequestonly. Hash uses64KiBstreambuffer,files<=1GiB. Sameapp/module
requirement meansNOTcross-build compatibility; usefulforsame-buildrepeatability.
ActualFoundationASan/UBSan tests verifyhashabc,missingfile,identitymismatches and
traversal/invalidfilenames; sourcegateschecked. No livecheckpointwrite/reloadproof.
Next justifiedinstall can validatecheckpoint save/move/restore plusVI/speedlogs;
backupNAND andcleannativestopfirst. Originalfirstplay/NAND/device/audio/perf gates
remainopen; emulatorcheckpoint cannotreplace them. LatestfullsuiteR690precheckpoint.

**R691 development checkpoint save action built, not deployed or save-proven.**
Same52374/c00098d3/DE8E956F preserved, pausedforbuild thenresumed. Added
Simulator-only/default-off GalaxyPadDevCheckpoints menu action and host request.
Writes uniqueUUID.sav under appprivateApplicationSupport/GalaxyPad/DevelopmentCheckpoints;
never reuseslot/overwriteexisting. Gatesrunning/pausedruntime,notstopping,2GiB
available,under8directoryentries,30scooldown. Clearsinput; State::SaveAs schedules
CPUthread save and upstream temporaryfile rename. Log says requested,notcompleted.
No restore action yet; no actual checkpoint created. Sourceaudit: StateRead clears
StaticRecomp cacheverification viaJitInterface, nextburstSyncIn restoresregisters.
This is not cross-process/mobile restoreproof. Candidate3844exit0,
2a50d777892fa9a7579895c7cbec911a659199eb2a4e3060b99893e134cc09f6,
notinstalled. Sourcecontracttestpasses,wiredintosuite; lastfullsuiteR690prechange.
Next finish guardedrestore/identityvalidation before justifieddeployment; don't
substitute emulatorcheckpoint for originalNANDsave/reload or firstplaygate.

**R690 full repository regression suite passes after cadence changes.**
Revalidated52374,pausedvia native menu; check-repository.sh1684exit0, log
generated/check-r690.log ends Native diagnostic and hook-lookup regressions passed
and Repository safety checks passed. Includes new3case livecapture parser tests;
not liveVI/speed evidence or fullgame/device acceptance. Candidate02711110 remains
built,notinstalled; installedc00098d3 and sameGatewayruntime preserved,resumed
after suite. No gameinput/settings or extraSimulator. Current historicalFPS
correction inR689 still applies. Next continue firstplay or add a narrowlyscoped
development checkpoint path to avoid repeatedopening on necessaryrebuilds: macOS
tooling has emulatorstates, iOShostcurrentlydoesnot. Checkpointwouldnot replace
actualNANDsave/reload acceptance. No performance/gameplaygate closed.

**R689 cadence diagnostics built; important correction to historical FPS label.**
Existing diagnostic_frame_count increments at after_frame_event, NOT display
completion. Historical 'presented FPS' wording is too strong; treat those numbers
as engine frame-event cadence, not verified screen presents. Sourcechecked
after_frame_event registrations and trigger sites; live counter unchanged.
Added host cadenceEstimate using upstream any-thread GetVPS/GetSpeed (atomic
rolling stats) to opt-in5s log. New counter_source=after_frame_event and corrected
accessibility label; legacy presentedfield retained for parsercompatibility.
Capture helper retains optionalVI/speed estimates,3tests pass including oldlogs.
Simulatorcandidate builds99183exit0,02711110688812d4dab1ca95718d18352794f3a85f31480e79d84b51f770d879,
NOTinstalled. Log generated/cadence-build-r689b.log. Same52374/c00098d3 preserved,
menu paused duringbuild then dismissed. No newcoreinstrumentation/ABIchange,
no runtime speed claim. Next use new logging at next justified deployment, not
restart Gateway solelyforlogging. Continue firstplay; inputmapping sourcechecks
show no swappedA/Z/axisbinding, but downstreammotion still needs visibleproof.

**R688 landscape traversal/tunnel observed; no gate closed.**
Same52374/c00098d3/soleDE8E956F retained. Rotated Simulator into landscape;
viewport/controls resize visibly without restart. Short left/up/A attempts near
roofedge barely moved; Z+down1s cleared toward grassyrocks, then up1.2s led into
darkhole with brief bluebubble and visible return to rocky surface. All leased
inputscompletedneutral. Final near darkhole/coin, not rabbitcatch. Capture
generated/ios-gateway-tunnel-r688.png.16–38FPS momentary readings, no improvement
claim or normalmovement/camera acceptance. Navigation behavior needs further
inspection before declaring merely collision; no source/settings/inputmapping
change. Read simulatorinput implementation: lease/lifecycle neutralization exists,
not proof of every downstream release. No profiler/build thisturn. Continue same
Gateway firstplay, aiming to reach rabbitinteraction rather than repeat opening.

**R687 Simulator trace attachment unavailable; retained native evidence is small.**
Same52374 remains live at Gateway.5s CPUProfiler defaulttarget failsPIDlookup
58651exit21. Revalidated runtime, readR534 stalledexplicitCPUProfiler history.
DifferentTimeProfiler5s explicitDE8E956F attaches but exceedslimit; recorder57482
INT at41s thenTERM,39942exit1. No usable capture, no xctrace remains. Do not retry
these Simulator attachment paths unchanged or treat observation failure as game
termination. Incomplete gateway-time-r687.trace retained privately.
Confirmed retained native1fb635f7 module matchesR423profile. Inspected exactnative
matrix linear body5f66ee0..5f676cc:23/28822CPUleafsamples fall there (~0.08%).
Shared/outlined code excluded, so not totalroutinecost, not Simulator timing or
an upperbound. This provides no basis to prioritize standalone PSMTXMultVec HLE
as the large performance fix. No replacement installed. Continue broader original
goal with currentruntime; avoid further matrix-only audit/profiler retries unless
new evidence changes expected payoff. No performance/input/save/audio gate closed.

**R686 exact matrix instruction and native-entry mapping established.**
Same52374live, no input/build/restart. ExactDOL matrix audit now checks all21
reference instruction words, not just prefix. Active Simulator GENERATED_DIR
points to modules-scale-r387 source. Entry804b683c charges21cycles; generated
loads/stores and paired operations retain guards/exceptions. A naive matrix
multiply would not preserve this contract. Hash-gated map-matrix-native-entries.py
verifies actual ARM64 table-dispatch instructions and maps all21guest entries.
Primarynativeentry5f66ef0; interior entries suchas5f844d4 are charge stubs branching
back into body. Entries are not contiguous extents: never count samples by their
min/max. Artifacts matrix-{boundary,native-entries}-r686.json and matrix-chunk-r686.asm.
Existing R676 sample aggregates10parentchunk observations with truncated PC list,
so it cannot establish routine cost. No native replacement justified yet. Next
derive body/control-flow ownership then use precise-PC evidence, not chunkname
or85callsitecount as proof. Gateway retained at last rocky-side position. Fullgoal
active; no performance/audio/save gate promoted.

**R685 Gateway traversal continues; exact matrix-vector candidate located.**
Same52374/c00098d3/DE8E956F remains live, no restart/build/settings change.
Up input blocked beside rock; down-left cleared it and traversed planet with
camera following. Rabbit jump tutorial reappeared on another side. Short left/A,
C and diagonal inputs ended neutral; now beside small roof/platform near dark
coin hole on rocky side. No rabbit catch or Grand Star yet,18–30FPS observed.
Avoid prolonged blind navigation; performance remains priority. New read-only
audit-matrix-boundary.py hash-gates exact DOL and uniquely locates PSMTXMultVec
prefix/84byte/blr correspondence at804b683c,85direct callsites. Evidence
generated/matrix-boundary-r685.json. Full21instruction/ABI/FP audit and actual
function cost remain unverified; hot parentchunk804B60A0 does not prove this
routine hot. Next inspect emitted implementation and map existing samples before
any native replacement. No hook installed. Converter candidate remains isolated.

**R684 normal microbenchmark mixed; no integration or runtime rebuild.**
Previous turn progress: parity/codegen candidate. Same52374/soleDE8E956F verified;
native menu paused for benchmark then dismissed. Extended probe-normal-output.py
with alternating-order unsanitized native benchmark. Final8pairs of50M calls each
have identical nonzero whole-output checksum; CPU/wall recorded. Candidate wins
6/8pairs, loses2, substantial timing spread: not robust runtime benefit proof.
Keep isolated; do not spend an app restart on this result. Earlier5M probe checksum
sampled an always-zero byte and is superseded by full3float-word checksum run.
Evidence generated/normal-output-benchmark-r684b.csv; all500000parity cases pass.
No vendor/core/app source change. Full suite remainsR678, not rerun during gameplay.
Resumed Gateway; leased A+moveY0.8 for2s completed39629exit0, neutral. Tutorial
prompt disappears, camera now overhead with Mario beside central rock. Fresh CUA
shows scene progressing, FPS~16 at capture, not performance or full-input proof.
Same runtime retained; next continue Gateway route and prioritize broader measured
CPU work over further tiny converter microbench iterations. Original goal active.

**R683 software normal conversion candidate: parity passes, real codegen improves.**
Same52374/c00098d3/DE8E956F Gateway session retained; native menu paused for
isolated compilation, dismissed afterward. No runtime/vendor source or install
change. PriorR676 sample has13 normal-reader and10 texcoord-reader leaf samples,
so investigated those rather than repeating already-refuted duplicate EFB waits.
Real ARM64 normal-s16/index16 code redundantly reloads/advances global output for
each component. Isolated candidate keeps local output, advances global once.
500000 extracted-reader comparisons under ASan/UBSan pass output bytes, all three
caches, cursor, sentinels and remaining; five input types,3/9components and offsets.
Actual Simulator translation unit compiles with original flags, object isolated
under generated/normal-output-r683. Named normal function shrinks63→55 static
instructions; observed redundant pointer updates removed. This is codegen proof,
NOT a measured FPS/throughput improvement or whole-loader parity. Candidate needs
bounded throughput comparison and broader loader validation before integration.
Harness tests/probe-normal-output.py --compile-simulator; private assembly beside
object. No JIT, fast-math, fake depth, or unrelated app change. Full goal active.

**R682 scene-correlated slowdown capture; Gateway remains ~31FPS without swap growth.**
Same PID52374/appc00098d3/soleDE8E956F, no restart or runtime change. Gateway
jump tutorial visibly stationary before/after. New capture-live-slowdown.py takes
bounded host snapshots and contemporaneous frame logs, rejects boundary windows,
records scene and exact process identity, and writes private evidence only.
30s capture: four complete windows663presents/21.400632s=30.980393FPS;
system swapins/swapouts/compressions all delta0, decompressions+288pages.
This does not support growing swap traffic as this interval's cause. CPU/graphics
work and waits remain candidates; no claim host contention is absent. No profiler
or build during capture. Evidence generated/ios-gateway-slowdown-r682.json.
Two parser regressions pass and are wired into repository checks; full suite not
rerun this turn to avoid competing with live runtime. Latest full pass remainsR678.
Next: preserve current Gateway scene/progression and investigate measured CPU/GPU
synchronization costs; no more routine movie restart or generic lookup microbench.
Full PRD remains active; no new performance, input, audio or Grand Star acceptance.

**R681 same no-JIT session reaches Gateway after the castle movie.**
Still PID52374/session42232 on soleDE8E956F, appc00098d3, log ios-runtime-r679.log.
Moved away from plaza wall, crossed castle bridge/grounds, triggered second
cutscene at entrance. Native timing windows report zero fallback and mostly
~60FPS presentation; no full per-movie count or audio-sync claim. Fade then
Gateway rabbit dialogue visibly appears. Captures ios-castle-movie-r681.png and
ios-gateway-arrival-r681.png. A pulse advanced initial dialogue; input neutral.
No code/build/settings change or runtime restart. This verifies the observed
castle→Gateway transition, not completed G6/G10, Grand Star, save/reload, stable
gameplay or audio. Next continue same live Gateway rabbit introduction and first
play route. Brief camera/C and move/A attempts are not full control acceptance.

**R680 live CPU/wall attribution: 25.990ms wall, 2.091ms CPU on the same call.**
Same PID52374/session42232, c00098d3 candidate, soleDE8E956F. Native movie
visibly completed and returned to gameplay; 18 emitted timing windows cover5409
calls, all zero fallback, weighted wall2.791ms vsCPU2.767ms. Remaining partial
window has not flushed because run stays active; do not claim total5591 yet.
Worst emitted call at epoch1788920046.422117 window:25.990mswall/2.091msCPU,
about23.899ms outside active CPU execution. This supports wait/descheduling, not
a heavy decode computation; it does not identify the wait or attribute R677's
separate63ms spike. No more routine decoder rewrite/timing-only restart planned.
Movie screenshot and post-return movement verified; gameplay still14–29FPS in
observed windows. Runtime stays live for first-play progression beyond invasion.
Log ios-runtime-r679.log, screenshot ios-cpu-timing-return-r680.png. No source,
build or settings change, no sampling profiler during this movie. Audio gate open.
Final route point: opposite edge of post-invasion plaza beside small orange-roof
house; right10s38045exit0 did not visibly advance far. Input neutral. Inspect
collision/camera-relative movement before repeating that direction; same52374 live.

**R679 verified diagnostic candidate installed and in gameplay.**
Candidate c00098d3…831a4 installed and hash-verified; sole Simulator DE8E956F.
Data container CC387840-B2E8-4E08-BCFC-0535FF946ACE; save 99d432d5…ab64f
unchanged. Runtime PID52374/session42232, log generated/ios-runtime-r679.log.
Same no-fallback-JIT, byte-default, pair0, nativeTHP YES and THP_TIMING1 settings.
Existing save reached Star Festival; story needed additional spaced A pulses in
this slower run. Inputs42178/60176 completed neutral. CPU-time logger has not yet
seen a movie call: do not claim live attribution from its synthetic tests.
Continue this same run toward movie, collect CPU-versus-wall spike evidence, then
continue first-play progression if stable; avoid another routine timing-only
restart. Gameplay remains around29–33FPS in current observations, not accepted.
No source change or extra build this turn; R678 repository suite remains latest.
Final continuation: forward22s helper14989exit0, now at dock approach beside
Toad speech bubble, not still at spawn. Input neutral; same52374 alive.

**R678 timing logger regression-tested; repository suite passes.**
No game/Simulator running. Corrected window seconds to last-call end minus first
call start; idle_since_last_call is separate, so shutdown idle no longer inflates
decode span. Added deterministic test of actual THPMod source with fake clocks and
decoder:63mswall/3msCPU pairing, unavailableCPU sample, fallback counts, periodic
flush, load reset and zero per-frame timing calls when disabled. ASan/UBSan pass.
test-native-diagnostics.sh adds timing and mod-address tests to repository suite.
Candidate rebuild56122exit0, SHA
c00098d3059736fdd2494bc2ff6e12c921381b40b79c02bbf986a74503d831a4, NOT installed.
Full suite40073exit0, generated/check-r678.log ends Repository safety checks passed. Installed
remainsf55578e4. Next runtime spike classification with CPU-vs-wall fields; no FPS,
audio, physical-device or completion claim from synthetic clock tests.

**R677 movie timing identifies rare63ms call; CPU-time diagnostics built.**
Continued48962/R676 through village/invasion. Native5591accepted/0fallback,
visible movie→gameplay return, clean exit20:51:32.974failed0. Nineteen bounded
windows: mean dispatch2.333–3.884ms; maximum63.209ms in window ending
epoch1788918573.546146. Overlapping presentation window20:49:31.902 averages
54.423FPS/min43.636, then recovers60.004. Most movie windows~60FPS; not zero-stutter.
Wall time alone cannot distinguish work from descheduling. Added opt-in thread
CPU mean/count and CPU time paired with max-wall call; errors reported-1, no game
logic changed. Build10937exit0, thp-cpu-timing-build-r677.log, new app
b8bf6d053f10d70c5efcecf66d13c16f916dac729e6b31263faa11519afa1077 NOT installed.
Installed remainsf55578e4, all runtimes/Simulator stopped; save99d432d5 unchanged.
Use epoch/date for cross-logger correlation: CLOCK_MONOTONIC and CACurrentMediaTime
have different origins here. Final unload window includes post-movie idle time;
do not infer movie duration from summed window seconds. Audio sync still open.
Read R458–R470 before generic dispatch/layout work: earlier negative candidates
must not be repeated. Software vertex loader is intentional no-JIT; no change.

**R676 candidate deployed; live gameplay still32–37FPS.**
Preserved R672 baseline at generated/candidates/r672-baseline/GalaxyPad.app,
hash7d14ec65…926e6. Installedf55578e4…6b9bf verified on soleDE8E956F; data now
F0BF4B9E-A33B-4015-8102-9A1FC368FAEC, save99d432d5…ab64f unchanged. Running
PID48962/session27479, generated/ios-runtime-r676.log, nativeTHP YES and
SIMCTL_CHILD_GALAXYPAD_THP_TIMING=1. Five-second frame diagnostics verified live.
Existing save→story→stationary Star Festival spawn; leased inputs neutral.
Gameplay windows31.66–37.27FPS with min observations24.55–25.00, UI intervals1.1s.
No large visible gain and no controlled same-scene before/after attribution.
Sample73706exit0:CPU18/250future wait and video18/250EFBdepth wait, distributed
generated/dispatch stacks; video42/250vertex loader. Hook lookup6/250 remains a
small component. No further lookup microbenchmark loop. Timed140s host counters
show zero swap-in/out and zero new compression; decompression15205pages, so do
not call memory pressure absent, but swap growth does not explain this interval.
Next continue same session for movie timing logs and broader CPU/vertex/readback
attribution. New movie diagnostics not exercised yet; full PRD gates unchanged.

**R675 dispatch hook fast-rejection built; game gain not measured.**
R674 gameplay sample8/250stacks in ModManager::HandlesAddress motivated removing
two hash lookups for addresses outside static patch/hook min/max. Dynamic return
addresses are checked regardless of bounds. Canonical ModernGekko patch0029 added
and bootstrap hash/scope registered. Focused boundary/return/unload/reload tests
pass ASan/UBSan after fixing test descriptor lifetime.20M negative checks0.143550s
before vs0.035385s after: microbenchmark only, not gameplay improvement.
Simulator core37330exit0, provision/app74558exit0. Corefc37721c…8eb59;
candidatef55578e49d64945c19e03bafec05fa76a5cf972d42cb4bd10251a36103e6b9bf.
Not installed. Prior R672 candidate still installed, Simulator shut down; preserve
it for any baseline. New candidate includes R673 logging and unchanged opt-in
native THP. Next live same-scene comparison with bounded timing, not more lookup
microbenchmarks. Full runtime suite/bootstrap execution not rerun.

**R674 live native movie completes:5591 accepted,0 fallback; ~60FPS windows.**
Same R672 installed candidate/PID46228, no replacement build installed. Existing
save→story→Star Festival→invasion movie. First native acceptance logged; two full
movie windows59.706850/59.967060FPS. CUA shows movie advancing and return to
post-invasion gameplay, then24.935638FPS gameplay window. Clean stop20:22:47.440
failed0; native accepted5591/fallback0 matches source frame count. Exact wall-time
start/end and audio sync not captured; no full correctness/performance acceptance.
Artifacts ios-native-movie-r674.png, ios-native-movie-return-r674.png and CPU samples
ios-{gameplay,native-movie}-r674.sample.txt; runtime ios-runtime-r672.log.
Gameplay sample points to distributed generated/dispatch CPU work and synchronous
EFB depth wait (CPU29/250, video28/250samples), not pure GPU saturation. See PERF.
Terminated shell and shut down soleSimulator after successful runtime exit. Next
investigate dispatch cost with bounded checks; preserve native movie candidate,
use R673 diagnostic binary at next launch. No default promotion or device change.

**R673 bounded slowdown diagnostics built; existing live run preserved.**
User requested better logging paired with visible slowdowns. Added opt-in five-second
frame summaries, minimum observed FPS and max UI observation interval (not actual
frame gaps); native GALAXYPAD_THP_TIMING=1 records timestamped call/fallback counts
and mean/max validation+decode dispatch time, not original fallback execution time.
Build61521exit0, log thp-logging-build-r673.log, candidate SHA
aca244d2356f711fad9f58234429c4a6cc9a9462faf30ce4554e4eacbb32d099.
NOT installed yet: PID46228 still runs R672 candidate/log. Paused via menu during
incremental build (CPU1.9%), then resumed; only DE8E956F booted. Advanced existing
save to story pages; no native frame accepted yet. Earlier live title windows57–59
fell to49–52 around file selection: decoder cannot explain all slowdowns.
Next continue same story→movie and establish native acceptance. At next justified
restart install new candidate and enable SIMCTL_CHILD_GALAXYPAD_THP_TIMING=1;
correlate five-second logs with visible movie/audio and timed host-memory deltas.
No movie-speed, audio, physical-device or full-suite acceptance claimed.

**R672 opt-in Simulator candidate linked, installed and visibly at title.**
Fallback now uses real CPU external_write/MMU callback plus reservation handling;
no dummy module journal globals. Configured STATICRECOMP_LOCKSTEP disables native
decoder creation. Forced fallback retest byte-exact R657 and5130879generatedcycles.
Candidate app SHA7d14ec657fdd2cc7dd02024ce998b053f4420f511b17a2a42b942e42bcb926e6,
IOSSIMULATOR/min16/sdk26.5. Separate ios-simulator-thp-app build succeeded.
Installed on sole DE8E956F; bundle F136F3E2-E0D8-4515-A464-A5F8CB0A48EF;
data2F933ECE-E7BB-4A4C-8310-CEB7B3841CF8, save99d432d5…ab64f unchanged.
Running PID46228/session13248, generated/ios-runtime-r672.log; exact DOL gate,
native initialized1/modloaded confirmed. Title visible60FPS snapshot is not movie
performance proof. Mod registration logs chunk fallback[804520a0,804530a0); assess
its impact during actual native acceptance. Next SAME run→existing save→movie,
confirm first native frame and whole playback/cadence/audio; no restart needed.

**R671 Simulator FFmpeg dependency built; opt-in app wiring added, link NOT complete.**
build-thp-dependency.sh verifies pinned archive, separate SDK directory, video-only
LGPL2.1+ ARM64/IOSSIMULATOR/min16/sdk26.5 objects. avcodec a4e7fb68…c0352,
avutil2e32a0dc…8513e.30007exit0. Added CMake option defaultOFF, Simulator-only,
runtime GalaxyPadDevNativeTHP flag plus exact DOL check; descriptor appended to
builtin mods. Transform moved to shared source, test include wrapper retained.
Separate candidate generated/build/ios-simulator-thp-app: initial header collision
fixed by C-only FFmpeg include path.34799exit1 then86222exit1 at link: core archive
does not expose g_mem_write_journal/_user used by fallback helper. Do NOT add dummy
journal globals. Next adapt fallback through real chassis callback or validated
ABI, retest equivalence, then relink. No app installed/launched; normal build and
device app unchanged. Logs thp-simulator-dependency-r671.log,thp-app-r671*.log.

**R670 actual replacement callback success/fallback verified offline.**
GalaxyPadTHPPatch.c tries bounded native decode at80452398; success returns via
LR, rejection executes original stwu with core mem_write32 and advances8045239c,
charges1 then generated interior charges remaining26. Active write journal forces
original path. THP_REAL_PATCH fixture tests actual callback, not a simulated skip.
Forced rejection: original wrapper success, byte-exact R657 output and unchanged
5130879generated inner cycles; native success: exact R669 prototype output.
Logs generated/thp-patch-{fallback,native}-r670.log. No mod registration/app build
yet; next isolated Simulator FFmpeg dependency and opt-in target wiring. Original
installed defaults/packages unchanged; no game or Simulator running.

**R669 actual compiled player-wrapper fixture passes native handoff.**
THP_PLAYER_WRAPPER builds a bounded local player fixture, executes exact wrapper
8038d2e4→THPVideoDecode→inner resolver/native→original return. Returns1 in101
dispatches and writes frameNumber42 through original instructions; guards intact.
Added parsed work pointer/alignment/dimensions/entropy-cursor consistency and
output nonoverlap with stack/player/readbuffer/work state. Synthetic sanitized
checks and compiled-wrapper guarded run pass. Logs generated/thp-player-r669.log
and thp-player-guarded-r669.log. Offline fixture is not live playback/cadence proof.
Next explicit mod-patch fallback and opt-in dependency/app target integration;
installed apps and package defaults unchanged, no Simulator running.

**R668 read-only exact-caller guest frame resolver added; still unwired.**
GalaxyPadTHPGuest.{h,c} validates inner PC/LR, outer saved return8038d310,
wrapper savedr31, THP1.1 two-component video/audio header, valid buffer/index,
declared capacity/payload bounds, original packet identity, dimensions and
texture arguments; maps only bounded cached MEM1/MEM2, rejects MMIO.
Exact generated caller8038d30c and texture/work/read-index offsets inspected.
Synthetic ASan/UBSan positive/rejection cases pass without CPU-state mutation.
Live wrapper capture/eligibility not yet proven; no native mod registered or app
target changed. Next original-work/header consistency checks and actual wrapper
fixture/patch fallback execution before live candidate build.

**R667 inner guest-state/cycle attribution measured; no guessed timing charge.**
Original frame0 generated inner downcount charge5130879; frame1000=6281568.
GQR and FPSCR preserved in sampled returns. Tail contains advancing entropy and
Y/U/V destination cursors in THP work area. Reference player only allocates/
passes work buffer; decoder globals have no external source references found.
This supports scratch ownership, not proof against every exact-DOL access.
Harness records generated charge only (no scheduler, interpreter fallback cycle
accounting or wall-time conversion); it is not console-cycle truth. No constant
charge or sleep added. Next live packet bounds/patch eligibility and real-player
cadence test under disabled-by-default native path. No app target changed.

**R666 offline inner-call handoff and rejection fallback proven.**
THP_NATIVE_INNER harness keeps original THPInit/header parsing and outer return;
at80452398 native adapter runs once, returns via LR, outer function returns0 in
99dispatches versus21463original. Output exactly equals R664 native prototype;
guards intact. THP_NATIVE_REJECT supplies invalid host length only: native rejects,
original decoder completes and output cmp equals R657 original byte-for-byte.
Logs generated/thp-inner-r666.log/thp-inner-reject-r666.log. This is offline
control-flow/output proof, not cycle/work-state/player/audio or app integration.
ModManager entry hooks restore CPUState, so actual replacement requires a patch
path with explicit fallback, not an observational hook. Next bounded live packet
eligibility plus guest state/timing treatment. App/package remains unchanged.

**R665 bounded native decoder interface implemented, NOT wired into app targets.**
apple/shared/GalaxyPadTHPDecoder.{h,c} accepts padded-copy compressed video packets,
validates8bit/full-range420/dimensions≤640x480/16alignment, limits input4MiB,
rejects overlapping/undersized destinations, and commits GX I8 planes only after
validation. CPU-thread-owned context, no filesystem/audio/gameclock behavior.
Pinned FFmpeg8.0.1 private ABI remains explicit; prototype transform link is still
diagnostic. ASan/UBSan adapter test16decode/reject/recovery iterations passes,
bit-exact against R664 prototype output, guards/failure atomicity intact.
Initial test caught FFmpeg bit-depth discovery resetting custom IDCT;8bit init,
reinitialization and postdecode callback identity checks now prevent silent fallback.
Log generated/thp-adapter-r665.log. Next exact guest boundary state/timing adapter,
dependency target integration and broader outputs; original package unchanged.

**R664 native sparse compatibility prototype: large errors removed, ~956FPS decode.**
Diagnostic FAAN now preserves SDK quarter-row middle-output ordering before the
column pass only when coefficients2..7arezero and AC1nonzero, plus final floor.
Compared frames0/1000/3000:1/11/3differing bytes of353280each, all magnitude1;
all U planes exact. Not full bit parity or whole-movie output validation.
Tracing-disabled single-thread full-movie benchmark decodes5591frames/30862320
blocks in5.847835s,956.08FPS,1.04594ms/frame average.10445exit0, log
generated/thp-native-sparse-bench-r664.log. No game/Simulator or competing build.
Next bounded rounding-edge coverage and integration contract/memory/cadence;
stock private FFmpeg context wrapper is diagnostic, not shipped product code.

**R663 isolated sparse-path reversal matches reference SDK algebra.**
Diagnostic THP_SPARSE_INPUT changes only first block to AC(1,0)=16, others0;
existing module output row136,135,132,126,129,123,120,119. Independent cosine row
has middle129,126 instead. check-thp-sparse-case.py reproduces actual row from
SDK quarter-path algebra; generated instruction804527cc is ps_nmsub as reference.
This supports an SDK-compatible sparse-path quirk, not a demonstrated port bug;
no physical-Wii oracle claimed. Next native compatibility treatment at sparse
first-pass transform branch, then whole-frame comparison and throughput. No
blanket output swap, brightness tweak or product promotion. Evidence thp-sparse-r663.log/gx.

**R662 worst-pixel independent IDCT check implicates existing sparse-transform behavior.**
Added probe-thp-idct-outliers.py: double cosine mathematical reference for12worst
floor-native/original differences across Y/U/V. Native matches floor(cosine) at
all12; original differs5–7levels. Log generated/thp-idct-outliers-r662.log.
This is not Wii floating-point semantics proof or proof of a recompiler defect.
Inspected affected coefficient sparsity and reference quarter/half IDCT assembly;
next isolate those sparse paths against exact generated instructions, distinguish
original SDK behavior from port error. Do not force native to match unexplained
baseline errors or promote mathematical output without contract review. No game
or product change; performance-first full PRD goal remains active.

**R661 quantization scaling matches; final rounding explains most pixel bias.**
Captured original scaled float tables and native DQT values for first six Y/U/V
blocks:384/384 entries match exact float bits after reference AAN scaling.
compare-thp-quant.py passes. Diagnostic FAAN wrapper changes only lrintf→floorf
conversion, without editing FFmpeg source or product. First-frame meanabsolute
Y/U/V errors drop to0.08398/0.05994/0.04276, signed bias nearzero; mismatches remain
16286/2853/2292samples, max7/7/5. Not parity and not promoted. Native coefficient
decoder/table selection are supported by evidence; next remaining transform
arithmetic differences, not a blanket brightness correction. Product unchanged.

**R660 full first-frame raw coefficients MATCH:353280/353280 across5520blocks.**
Original module dispatcher exposes every inverse-transform entry. Native helper
wraps FFmpeg8.0.1 private idct_put diagnostically, reverses scan permutation,
quantization and1024DC bias with divisibility assertions, then calls original
transform unchanged. Whole-frame coefficient logs compare exactly; native plane
output cmp still matches untraced R657. Thus first-frame mismatch is downstream
of raw entropy/coefficient decoding: dequantization/transform/output conversion.
Private logs generated/thp-all-blocks-r660.log and thp-native-all-blocks-r660.log.
Next compare quantization scaling/transform arithmetic; do not rework Huffman
decoding or change brightness/tolerances. No game/product integration yet.

**R659 offline transfer/plane checks pass; reference frame is reproducible.**
tests/test-thp-frame-dma.c exercises the actual harness callback for256cases:
all1–128block lengths, both directions, no-trigger behavior, DMA_T clearing,
PC advancement and boundary bytes; ASan/UBSan pass. Original-frame harness now
checks each destination byte transferred exactly once and32-byte guards around
all three planes. Sanitized harness run succeeds and output matches R657 exactly
despite0xa5-prefilled destinations. Existing module itself is not sanitizer-built.
Evidence generated/thp-frame-guarded-r659.log and thp-original-guarded-r659.gx.
This rules out tested DMA/unwritten-plane errors, not every oracle assumption.
Next coefficient/dequantization versus transform/store comparison; no product
integration, game/Simulator launch, save change or performance acceptance.

**R658 mismatch persists across frames; stock IDCT selection is not the fix.**
Native probe now accepts explicit auto/integer/simple/float-AAN IDCT; both probes
accept a bounded frame index. Frame0 integer and float-AAN still max8/8/6 errors,
not improved parity. Verified FFmpeg config includes FAAN and ARM64 override only
selects NEON for auto/simpleauto/simpleneon, so this exercised distinct paths.
Frames1000 and3000 original decode successfully with353280DMA bytes each;
native auto comparisons maxerrors11/10/9 and8/9/10, meanabsolute~0.48–0.59.
Log generated/thp-compare-r658.log. No stock-IDCT option is promoted. Next isolate
coefficient/dequantization versus transform/store differences, with harness DMA
and guard tests before trusting a custom correction. No game or product change.

**R657 first complete original/native frame comparison obtained; NOT byte-identical.**
Offline harness executes existing module's THPInit and full THPVideoDecode,
returns0 after21463dispatches and353280DMA bytes. Added bounded DMAU/DMAL
fallback semantics from existing Dolphin interpreter (synchronous RAM/LC only).
Native first-frame helper and GX I8 untile comparator added. PrologueA frame0:
Y/U/V max absolute byte errors8/8/6; mean absolute0.494/0.484/0.300. Differences
have mostly negative bias, consistent with a rounding question, not proof of its
cause. Native decoder is therefore not yet a drop-in pixel-equivalent candidate.
Evidence generated/thp-frame-r657-output.log, thp-compare-r657.jsonl; protected
plane files stay ignored/local. Next validate harness transfers/guards and compare
additional frames/IDCT rounding; no in-game hook, package, save or Simulator change.

**R656 original-module offline frame harness now executing; DMA support next.**
Added tests/probe-thp-frame.c: loads existing c0021b9f module, ABI/CPU-size/game
checks, DOL sections, real first PrologueA video packet; bounded dispatch and
explicit unsupported-operation failures. Original THPInit returns1. Offline
OSRegisterVersion side effects explicitly omitted (not OS-state parity). Correct
MSR FP/HID2 LSQE/PSE/LCE prerequisites resolve initial harness exceptions.
Current stop: mtspr instruction7cdae3a6 at804a3194 (DMAU); no complete frame yet.
Log generated/thp-frame-r656.log; next implement bounded locked-cache DMA from
existing emulator semantics, then compare outputs. No game/build/Simulator live.

**R655 exact THP boundary audit completed; no hook installed.**
Exact-DOL assertions identify outer804514ec and inner decompression80452398,
called at8045174c; Petari symbols are Korean-region and cannot be used verbatim.
Extended audit-thp-boundaries.py passes; generated/thp-contract-r655.json.
Prefer retaining guest validation/player/audio while replacing inner full-frame
decode, subject to original frame bounds, tiled-plane/rounding and state oracle.
Next complete-frame reference execution/capture, not another throughput run.
No runtime/Simulator, product or package change; all full-goal gates remain open.

**R654 native THP throughput feasibility PASSED; integration not attempted.**
Private minimal ARM64 FFmpeg 8.0.1 built from official source, LGPL2.1+ config.
Three complete PrologueA video-only null-output runs:5591frames in4.2196/3.9718/
3.9850s,1325–1408FPS,0.710–0.755ms/frame average. One decoder thread; no game or
Simulator, build completed before timing. Log generated/native-thp-r654.log;
reproducible scripts/benchmark-native-thp.py and CUTSCENE-PERFORMANCE-PLAN.md.
Next complete-frame output/layout/rounding and guest-contract oracle before any
native decoder integration. No product changes, in-game gain, audio or device
acceptance claimed. Full goal remains open; performance-first queue unchanged.

**R653 USER REORIENTED LOOP: cutscene/decoder performance first.**
Read docs/CUTSCENE-PERFORMANCE-PLAN.md and updated goal loop. Full PRD unchanged.
Next direct-frame native THP decoder feasibility/benchmark, then playback/audio
pipeline and timed host-pressure isolation; not more navigation or micro A/Bs.
Actual PrologueA header59.94FPS/5591frames/~93.277s. Default run still dipped to
9.12/12.21/6.41FPS amid heavy host compression/swap; correlation not sole cause.
Stopped31065 cleanly19:00:31.868failed0/session27754exit0, soleSimulatoroff;
save99d432d5…ab64f unchanged. No product changes or new performance acceptance.

**R652 installed byte DEFAULT activation PROVEN; movie running31065/27754.**
Same6f41c070/module3acdcddc, no byte env override, pair0 and no VI recorder.
Normal existing-file/story/village route reaches invasion movie; log confirms
byte activationpc80452a2c/eae0000000. Screenshot ios-default-byte-r652-movie.png.
No restart/default edits. Inputs neutral after helper56952exit0. Keep this run
and continue beyond movie toward first Grand Star/save loop; do not restart for
another identical benchmark. Sole DE8E956F; no build/test competition. Startup,
activation and movie rendering do not close performance/audio/gameplay gates.
Log remains generated/ios-runtime-r651.log. Original full PRD goal remains open.

**R651 suite PASSED; byte-default candidate INSTALLED and starting27754.**
Full suite30113exit0, Repository safety checks passed. Installed6f41c070 on sole
DE8E956F via26271exit0; installed hash matches candidate, save99d432d5…ab64f
unchanged. New bundle71C4F911-984E-4AF5-9EEB-F813D0BD6B6F; data container
DC42BFFE-C73A-43D7-9D4A-D0E971DCE3A4. Module3acdcddc unchanged.
Runtime31065/launch27754 visibly ready at title. Log generated/ios-runtime-r651.log removes byte env override and VI
trace; pair0/QoSNO, same pointer flags. Next observe ready game, prove movie byte
activation via app default, then continue gameplay beyond movie. No new benchmark
comparison planned. Only one Simulator; no competing build/test work.
Updated unsigned private device stage generated/device-stage.d5VpYL/GalaxyPad.app
contains app936265bd and module48f455eb; no signing/install/hardware acceptance.
Original PRD performance/gameplay/audio/device gates remain open.

**R650 byte-cache default implemented after enabled confirmation; NOT installed.**
Same enabled run movie windows41.173276 and40.884548FPS, versus disabled35.387/
36.053; activationpc80452a2c/eae0000000 repeats. Incremental gain, not60Hz or
exact phase/host-controlled estimate. Clean exit18:38:37.069failed0/session65315
exit0, Simulatoroff, save unchanged. Byte-only mobile default now set before
UIApplicationMain with overwrite0; explicit0/other values retained, pair untouched.
Focused compiled default/opt-out tests pass. Simulator app10794exit0 SHA
6f41c070723857ae685046b9c94b377c83a12986ccf79f99f7f4ac6a5335588b;
device app83123exit0 SHA936265bd5744518f51530b82a80c5507d50403cc46f899bb4ac3b3e473ca7cfd.
Neither deployed. Full suite30113 running generated/check-r650.log; poll samehandle.
Next finish suite, install candidate and verify activation without byte env override;
do not repeat unchanged benchmark. Device staged qAV3Pi still older unsigned app.
Original PRD, gameplay stability, audio and hardware gates remain open.

**R649 enabled confirmation RUNNING65315/PID28264; no default change.**
Same verified app54786759/module3acdcddc/save99d432d5…ab64f; sole DE8E956F.
Byte1/pair0/QoSNO, same geometry/diagnostics, no competing build or suite.
Log generated/ios-runtime-r649.log; VI runtime/lc-byte-confirm-r649-vi.csv
(early16384samples only; movie timing must use complete presented windows).
Title/file/Play succeeded; story helper53181exit0, gameplay visually inspected.
Forward route helper5612exit0; visually at village overlook dock, input neutral.
Continue route off dock into plaza. Next movie activation and enabled
confirmation before default/opt-out change. Original PRD goal remains active.

**R648 same-artifact byte-disabled control running76274/PID26686.**
FINAL: control full movie windows1097/31.000029=35.387064FPS and
1096/30.400043=36.052580FPS. EnabledR64740.195464 suggests11–14% gain, not
phase/host-controlled proof. No byte activation with explicit0. Next one enabled
confirmation before default decision; no repeat generic QoS/fallback sampling.
Clean stop18:23:34.642failed0; session76274exit0, soleSimulatoroff, save unchanged.
VI dropped26209: no movie CPU timing. No source/default changes or PRD acceptance.
Previous R647 progress: movie activation and40.195FPS window; clean shutdown.
Verified app54786759/module3acdcddc/save99d432d5…ab64f, no prior runtime/Simulator.
Sole DE8E956F booted, byte0/pair0/QoSNO with prior geometry and diagnostics.
Log generated/ios-runtime-r648.log, VI runtime/lc-byte-control-r648-vi.csv.
Story helper25305exit0; replay plus bounded corrections reach invasion movie,
verified screenshot generated/lc-byte-control-r648-movie.png. Same runtime live.
Next capture full movie-only presented window after18:20:26 (first may be mixed),
complete presented windows. Navigation-only checks are not touch acceptance.
Host/phase differences remain caveats; no default promotion or speed claim.

**R647 mobile byte-cache activation PROVEN; same movie runtime6596 live.**
FINAL UPDATE: clean runtime exit18:05:15.662 failed0; session6596exit0, sole
Simulator shut down. Save99d432d5…ab64f unchanged. First complete movie window
18:03:22–18:03:53:1234/30.699982=40.195464FPS. No paired speed claim.
VI dropped23207 confirms movie CPU timing unavailable. Next byte0 comparison,
using complete presented windows; no repeat generic fallback-total inference.
Same25126/app54786759/module3acdcddc, byte1/pair0. Diagnostic route reaches Bowser
invasion movie; log confirms [galaxypad-lc-byte-fast] active pc80452a2c/ea e0000000.
Screenshot generated/lc-byte-r647-movie.png. Full movie presented windows pending;
no matched disabled comparison or speed claim. VI recorder holds only16384samples
and filled during navigation, so this run cannot supply movie CPU timing. Use
complete presented windows only; do not summarize absent late VI samples.
Next finish movie window, clean stop, plan matched byte0 control. Sole iPad only;
no build/test competing. Full original PRD goal remains active.

**R646 suite PASSED; hardware unavailable; byte-cache mobile trial running6596.**
R645 suite3418 exit0, Repository safety checks passed. No signing identities and
no connected devices. Private staged device app remains unsigned/uninstalled.
Next local performance test uses unchanged Simulator app54786759/module3acdcddc,
LC_BYTE_FAST=1 only, LC_PAIR_FAST=0, QoS flagNO. Native historical movie benefit
does not establish mobile benefit; require activation and paired scene timing.
Sole iPad DE8E956F booted; runtime25126/session6596 startup, log
generated/ios-runtime-r646.log; VI generated/runtime/lc-byte-simulator-r646-vi.csv.
Save99d432d5…ab64f verified before launch. No rebuild or concurrent test load.
Title A+B, existing Mario file and Play succeeded; now opening story page1.
Next advance story, reach movie and verify byte-path activation; no touch
verification lane or default promotion. Original PRD goal remains open.

**R645 device module completed and private app staged; suite running3418.**
Original module38249 exit0. Module SHA256
48f455ebc33f8eb2fc58151cd722ea756db77a5738a9573a0a49f0c656110041.
Stage generated/device-stage.qAV3Pi/GalaxyPad.app contains unchanged R644 app
and matching IOS/arm64/min16 module; export/install-name checks pass. Dependencies
are system libraries/frameworks only. App is unsigned; no installation or device
runtime/performance evidence. Source checks confirm iOS excludes ARM64 fallback
JIT construction and selects software vertex loading, not full execution proof.
Full regression suite3418 is live, log generated/check-r645.log. Poll same handle.
Next suite result, device signing/access preparation, then real-hardware timing.
No game/Simulator launched. Original PRD and gameplay/performance gates stay open.

**R644 physical-device startup wired; module linker still running (38249).**
Device app51942 exit0, SHA256
2e73e706f21684bb69bb0f1740348261237d1fe801d0a866a5ad0aa2e64eb40d.
Physical startup now selects the bundled Frameworks module and verified imported
GameData; Simulator development paths remain Simulator-only. Both platform main
objects compile. New private staging script passes syntax checks but has NOT run.
Original module linker23142 remains active after 5:48, about685%CPU; poll38249,
do not restart. Log generated/build-ios-device-module-r643.log. Next finish and
audit device module, run scripts/stage-private-ios-device.sh, then package/no-JIT
checks and signing/device access. No connected device or booted Simulator found.
No device launch, gameplay or performance claim. Full PRD goal stays active.

**R643 device core AND app shell BUILT; device module RUNNING session38249.**
Core85533exit0; runtimeobjectIOS/min16/sdk26.5. Provisionexit0/arm64 archive
f4730e664825bd931afd76b3d2614cbdfcde2813a192af73349e53a58a751435.
Deviceapp33663exit0, executable96f44f1a16533f28cdb01d50756f1895ca7151b9d7a34d439362bd5ef4c5f85d,
vtoolIOS/min16/sdk26.5. NOT a signed/playable/device-performance result: AOTmodule
still building via GALAXYPAD_IOS_SDK=iphoneos, log build-ios-device-module-r643.log.
Poll same38249; do not restart on timeout. SDKselection isolated across all four
entrypoints; Simulatordefault/header/archivepaths verifiedunchanged. InvalidSDK
tests pass. Next moduleplatform/ABI/noJIT/packageaudit, then signing/deviceaccess.
No games or Simulators running. Full originalgoal remainsactive.

**R642 QoS parked; physical-iOS core build RUNNING session85533.** Same-build
off51.108VI/s/CPU15.779ms versuson52.611/15.719: not a convincing improvement
against measured variability. DefaultOFF retained, no promotion. Runtime8598/
27787 cleanexit0/failed0, soleSimulatoroff. No device connected; asked user.
Build GALAXYPAD_IOS_SDK=iphoneos uses separate generated/build/ios-device-core;
log generated/build-ios-device-core-r642.log. Last observed cmake9135/builder9128
live; progressed through778/1480 compilation steps. Cache confirms Release,
arm64,iphoneos. Poll samehandle, no restart on timeout. Simulator/macOS graphs unchanged.
Next audit device core platform then provisioning/module/app device paths; actual
device speed/signing/full PRD acceptance unproven. Full goal remains active.

**R641 queue experiment REJECTED; direct CPU candidate measured, no speedfix.**
QueueNO/YES both worker requestedQoS25/CPU21. SDK API is REQUESTED class, not
effective priority/core placement; old actualQoS label corrected. Removed queue
flag. Installed54786759 with new default-off GalaxyPadDevCPUUserInitiatedQoS;
enabled CPU logs21→25/result0. File selection52.611VI/s,15.719msCPU/VI,
164.764M processinstructions/VI,51.751Mcycles/VI. No clear large gain; next same
binary explicitNO control then park absent repeatable improvement. No promotion.
7767/session98543 cleanexit0/failed0, soleSimulator shut down. Full goal active.

**R640 next: test default-off Simulator scheduling candidate.** R639 fullsuite
64026 PASSED. Simulator matched visible-pointer file select53.014VI/s,
15.208msCPU/VI,178.935M processinstructions/VI,55.409Mcycles/VI: lower gross work
than native yet slower CPU time. See PERF.md caveats including externalMetalHost.
Candidate builds12379exit0, NOT installed; launch flag GalaxyPadDevUserInitiatedQoS
defaultsNO, YES requests runtime queue USER_INITIATED. Logs worker and actual CPU
QoS separately, no guest-clock changes. Next same-candidate NO/YES comparison.
Prior installedbf6da365 unchanged.5921/session32327 clean exit0/failed=0;
soleSimulator shut down. No runtime remains. Full original goal active.

**R639 native file-selection measured; full suite RUNNING session64026.**
Native4315/session5785 clean exit0.30.0051s/1795VI=59.823VI/s,11.101ms CPU/VI;
whole-process192.777M instructions/VI,58.244M cycles/VI. Visible pre/post scene,
no dropped trace samples. Pointer visible native versus invisible R638Simulator:
match this for next Simulator work capture. Same module/app, no speedfix.
Capture helper now exact-executable aware, no focus mutation; focused tests pass.
Poll existing64026/check-r639.log before next runtime (no overlapping CPU load).
No games or booted Simulators. Full original goal remains active.

**R638 PERFORMANCE PLATFORM COMPARISON — no runtime left running.** Native title
59.933VI/s,10.126ms CPU/VI; Simulator title53.350VI/s,15.598ms CPU/VI;
Simulator file selection50.717VI/s,16.194ms CPU/VI. Full minute windows, exact
identities/caveats in PERF.md. No rebuild or speedfix; historical~35FPS is not a
stable ceiling. Both compiler targets default apple-m1, PGO/ThinLTO/O2 retained.
Next native file-selection match, then paired instructions/cycles/core residency
to separate execution cost from scheduling. NO return to touch-verification loop.
Native3003/session40402 exit0, Simulator3504/session96470 clean exit0/failed=0,
sole device shut down. No connected physical device. Full goal remains open.

**R637 USER REPRIORITIZED PERFORMANCE — stop touch-verification loop.** Same
99791/session2532 remains RUNNING near village lakeside, appbf6da365. User called
out lack of meaningful speed work. New pathological window220/30.500797=7.21FPS;
host snapshot JumpConnect284.4%CPU/game47.1%. Later unchanged scene, Jump8.6%/
game137.3%, FPS recovered27.73. Strong contention correlation, not controlled
causal proof and NOT explanation/fix for baseline~35FPS. Do not terminate remote
access without user approval. Sample399CPU observations:327underchassis includes
27floatfuture waits;44Run body. No dominant readback wait. Evidence
ios-r637-village-slow.sample.txt, host-village-r637.txt, continuedR635log.
Next prioritize matched native-macOS/Simulator workload comparison and meaningful
AOT CPU execution-cost investigation, not UI tweaks or repeated generic samples.

**R636 updated candidate in gameplay:** same99791/session2532, appbf6da365.
Actual touchA advanced remaining story/invitation into Star Festival, visibly
jumped, then Mario returned to standing. Diagnostic forward5s helper16919 exit0
reached hill base; not sustained touch-stick proof. Paused there, life3/coins0/
bits0. Story text clear and A below inventory; stick overlaps part of livesicon,
so full layout acceptance remains open. Gameplay window35.63FPS, no speedfix.
Evidence ui-r636-opening-native.png and continued R635log. Next continue route
and pointer/control testing on this candidate; no rebuild required.

**R635 latest UI INSTALLED and story clearance observed:** appbf6da365 runs
PID99791/session2532, normalmodule3acdcddc, log ios-runtime-r635.log. Actual touch
pointer/A selects existing file, starts story and advances to page2. Screenshot
ui-r635-story-clear-native.png shows last line clear of left stick/D-pad.
Paused on page2. Previous95966 clean exit16:01:42.344 failed=0, session5906exit0.
GameData hash still99d432d5…ab64f, backupR629 intact; new containerB15813C8-2128-
40B3-B01C-A1D13300D5E6. Sole iPad unchanged. Story windows57.27/59.05FPS are
different scene workload, NOT proof of performance fix. Gameplay remains open.

**R634 left story overlap candidate fixed; R633 suite PASSED:** session98404
exit0 and Repository safety checks passed, before this layout change. New story
rectangle UIKit test fails old layout; lowering alone still overlaps1.01pt.
Default iPad stick now8pt from safe left edge, left cluster uses full safe-bottom
room. Final real UIKit runner passes all checks; preview inspected and captured
ui-r634-layout-native.png. Product candidatebf6da365927800e0365a030219caf7c39e76bca8670e7ceaaf1d5763f46855b2
built exit0, NOT installed. Same paused95966 still0037f222 on storypage2.
Next deploy/test candidate; no need to preserve unsaved test position indefinitely.

**R633 full regression RUNNING — preserve session98404:** bash
scripts/check-repository.sh > generated/check-r633.log launched; handle repeatedly
confirmed live, latest completed640000-case CPUState/host-flags check, compiler
children active. Do not restart suite or call it passed yet. Installed0037f222
same95966/session5906: actual touch pointer/A entered story and A advancedpage1.
Paused on page2. Screenshot ui-r633-story-layout-native.png exposes remaining
left-stick/D-pad overlap with last story-text line; next layout target.
Concurrent regression load means FPS here is NOT a benchmark.

**R632 sampled-load provenance refined, no optimization:** exact retained macOS
audit identifies214/28822 sampled leaves as optional write-journal pointer loads,
not RAM mapping or lazy-FP globals. Numeric-symbol classifier and negative tests
pass; unknown selected loads3804→3590. Artifact shared-aot-work-r632.json.
No runtime changes, restart or speed claim. Installed0037f222 remains paused95966.

**R631 host load checked:** same95966 candidate, file detail resumed and paused.
Host16GiB M1Air/8logical CPUs: GalaxyPad134–159%CPU, Logitech67–75%, aggregate
idle30–42%, no swap deltas in bounded samples. Background load exists but no
sole-cause attribution; file-detail window35FPS. No process/priority changes or
speedup. Evidence generated/host-perf-r631.txt and PERF.md. Generic scheduling
captures already parked; next performance step needs CPU-cost hypothesis.

**R630 UIKit false-green launcher fixed:** tests/run-mobile-ui.sh now validates
one requested booted device, builds isolated harness, and requires explicit
completion with no FAIL lines. Actual old R627 failure log exits1; fresh UIKit
run exits0 with verified marker (generated/ui-runner-r630.log). Three parser
tests pass and join repository suite. Product unchanged0037f222; returned to
same paused95966/session5906. No performance or gameplay progression claim.

**R629 NEW UI INSTALLED — supersedes old live checkpoint:** app0037f222 now
running PID95966/session5906, log generated/ios-runtime-r629.log, normalmodule
3acdcddc and pointer experimentsNO. Sole iPad unchanged. R619 runtime clean exit
15:40:06.682 failed=0; shell terminated. Unsaved tutorial position intentionally
discarded to unblock deployment, NOT saved/reloaded. Existing GameData preserved
SHA99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f;
backup generated/save-backup-r629. Actual pointer/A selected retained Mariofile1
dated07:02, zeroStars. Revised layout visible over title/file detail; paused
at file details. Artifact ui-r629-installed-file-native.png. Windows34.59/36.80FPS,
no performance fix. Data container now1667B463-8717-4DD3-8E95-141BDFEF9E80.
Next use installed candidate; old87155 preservation notes are obsolete.

**R628 live resume verified, no catch/save progress:** same87155/24676, old
installed appb853f060, sole iPad. After isolated UIKit apps, native menu dismissal
15:35:14.043 resumed rendering and input; diagnostic movement and actual touchY
responded. Short route lost rabbit beyond crater; no accepted catch or save.
Screenshot ui-r628-resumed-gameplay-native.png; R619log windows32.73–43.14FPS.
Paused again at grass/dirt edge beside large flower patch, not former rock.
Do not repeat unchanged blind chase; next needs reliable rabbit interception or
target acquisition. R627 candidate remains uninstalled; full goal remains open.

**R627 A/HUD regression fixed in UIKit candidate:** lowered default iPad A42pt
within existing cluster. New recorded-Gateway inventory rectangle assertion
fails before change and passes after; all-control non-overlap and existing input
tests pass. Real preview inspected: ui-r627-layout-preview-native.png. This is
one observed HUD-region check, not full-scene/controller/phone acceptance.
Release candidate0037f222c4a9846b59b4ff45d72de1ee54ed2df7b218fe7b97394ed2fd9708cd
built, NOT installed. Harness terminated; foreground product remained87155,
paused2.3%CPU at R624 checkpoint. Next return to first-play/save progression;
candidate runtime check pending safe replacement. Pointer offset/FPS remainopen.

**R626 real UIKit layout test passes; partial HUD overlap remains:** existing
isolated OverlayTests ran on sole iPad, no second game. Letterboxed all-control
non-overlap and A+B/release/editor tests pass. Optional tilt default moved inward
to avoid lowered actions. Preview screenshot ui-r626-layout-preview-native.png
shows lower placement but A still partly intersects prior gameplay Star Bit HUD.
Do not call layout finished. Candidate rebuilt bc8e47e19dce2826cfd86e7b2adbedcd83279d7732f192b5420b654ec1e86296,
not installed. Harness terminated, original87155 foregrounded with same paused
rocky-grass checkpoint visibly intact. Continue geometry refinement or gameplay
toward save; pointer alignment/performance and full goal remain open.

**R625 UI candidate built, NOT installed:** default iPad face-button cluster now
anchors toward safe bottom when a lower gutter exists; Plus sits inward beside
the cluster. Saved origins, phone defaults and mappings unchanged. Sizing and
stick-routing sanitizer tests pass; Release Simulator build exit0, appSHA
157e229cb2361207bd162fe897a441ef55b26ef50a4dc67f826a4bdd11161e33.
Live R624 checkpoint still PID87155 (2.1%CPU), old installed appb853f060 paused.
Do NOT conflate rebuilt disk artifact with running app. Visual/input acceptance
of new placement pending; preserve unsaved gameplay before replacement.

**R624 LIVE PAUSED — actual touch collection and shot:** same PID87155/session24676,
sole iPad, normal binaries unchanged. Actual Y recentered camera; corrected touch
aim collected a roof Star Bit while Mario stationary (0→1, bit disappeared).
Actual B fired toward the cursor, 1→0 with visible impact; no verified rabbit stun
or catch. Diagnostic short approaches ended on rocky grass near fleeing rabbit.
Native pause15:24:59.085 blocked=1/input cleared, process1.4%CPU/session live.
Preserve checkpoint; do not restart. Pointer offset and right-control/HUD overlap
remain actionable defects. Recent windows33.92–40.85FPS, no speed improvement
claim. Screenshot ui-r624-pointer-shot-approach-native.png; continued R619log.

**R623 LIVE PAUSED — house-side crater exit:** same PID87155/session24676 and
single iPad, normal app/module unchanged. Pipe traversed both directions; crater
traversal ended beside blue-roof house with coins7/life3/bits0. Last touchB bush
shot spent1→0 without verified reveal. Rabbit visible moving near rim, but NO
catch dialogue/count accepted. Pause15:13:48.874 blocked=1/input cleared, session
live/process2.5%CPU. Preserve checkpoint. Evidence ui-r623-crater-exit-native.png
and continued R619log. Next improve targeting/catch route, not repeat blind chase.

**R622 LIVE PAUSED — three-rabbit hide-and-seek active:** PID87155/session24676
unchanged, sole iPad. Followed initial rabbit/group; actual touch pointer/B used
one Star Bit (2→1), no verified stun/catch. Approach triggered hide-and-seek and
catch-all-three dialogue; actualA advanced both into gameplay. No individual
hide-and-seek catches accepted. Native pause14:52:58.378 blocked=1/input cleared,
session live/process1.9%CPU. Preserve; resume from flower patch to search three
hiding places. Screenshot generated/ui-r622-hide-seek-native.png, R619log.

**R621 LIVE PAUSED — Gateway tutorial:** same PID87155/session24676,
appb853f060/module3acdcddc, sole iPad. Castle cinematic completed and Mario landed
in Gateway. Actual touchA advanced first rabbit dialogue; diagnostic movement
traversed curved surface with camera rotation. Initial rabbit tutorial still
unfinished, no catches accepted. Native pause14:39:52.658 blocked=1/input cleared,
session live, process3.3%CPU. Do not restart; dismiss native menu to continue.
Evidence generated/ui-r621-gateway-native.png and continued ios-runtime-r619.log.
Recent scene windows35–37FPS, not performance acceptance or cross-scene speedup.

**R620 LIVE PAUSED — castle-lift cinematic:** same PID87155/session24676,
appb853f060/module3acdcddc, sole iPad. Revalidated then resumed R619; invasion
completed, diagnostic axes navigated attacked plaza/bridge/castle and triggered
castle-lift cinematic. Native pause14:25:44.194 blocked=1/input cleared, process
2%CPU and session live. Do not relaunch; dismiss native menu to continue toward
Gateway. Screenshot generated/ui-r620-castle-lift-native.png; continuing R619log.
No touch-stick, save/reload, audio or GrandStar acceptance. No performance fix.

**R619 LIVE PAUSED CONTINUATION — do not relaunch:** PID87155/session24676,
sole iPad DE8E956F, appb853f060/module3acdcddc. Native menu opened14:07:34.137,
blocked=1/input cleared, process2.1%CPU, session confirmed live. Dismiss native
menu to resume the Bowser airship invasion reached through real gameplay.
Touch pointer/A selects file and advances story; actual touchA visibly jumps.
Leased diagnostic controller axes move Mario through flowerbed, hill and village
to the invasion trigger; NOT sustained touch-stick or physical-controller proof.
Gameplay windows near30FPS, invasion drops22–27FPS. Full acceptance still open.
Evidence generated/ios-runtime-r619.log, ui-r619-before-move-native.png,
ui-r619-invasion-native.png. Right buttons visibly overlap coin/Star Bit HUD;
layout remains unfinished. Preserve live progress for next continuation.

**R618 current-module provenance checked:** R617 image UUID matches normal
module3acdcddc; current build graph uses PGO/ThinLTO/effectiveO2/strictFP. Two
explicit sampled PCs resolve to lazy-FP availability loads, not new unexplained
arithmetic hotspots. Prior rejected narrow guard experiment remains parked;
no optimization or gameplay claim. No game launched. Next return to substantive
playability progression rather than repeating this compiler/guard audit.

**R617 normal-module baseline remains slow:** app b853f060/module3acdcddc,
movement trace0 and pointer experimentsNO. Visible file select, latest pre-sample
30.500377s window1148frames=37.638879FPS. Three-second10ms sample has246CPU-thread
observations:200 nested under chassis dispatch includes23 float-future waits;
native chunk work spread across many functions. No single-fix inference from
nested counts. Runtime86550 clean exit13:50:15.174 failed=0, shell terminated.
No gameplay progression or speed gain. Evidence generated/ios-runtime-r617.log,
ios-r617-file-select.sample.txt and ui-r617-file-select-native.png.

**R616 full regression pass:** bash scripts/check-repository.sh session80809
exited0; generated/check-r616.log ends Repository safety checks passed. Includes
new settings default, placement geometry, movement trace and input tests plus
existing generated-code/runtime checks. No game launched. This is not Simulator
gameplay, clean-clone, performance or publication acceptance; tracked-file
safety checks do not audit the largely untracked tree for publication. Reviewed
retained CPU profile without a justified new optimization; do not weaken cycle
budget checks or restart rejected mapping-cache experiments.

**R615 live movement reaches device:** opt-in bounded change trace shows two
center-start CUA drags emit only near-neutral(-.007642,.021738), then zero within
0.756/9.337ms, not a useful held movement test. Off-center contact emits
(.697838,.021738), device samples identical axes5.851ms later and returns neutral
after release (4poll interval). No movement remapping/hold stretching justified.
Sustained UIKit movement still unaccepted. Trace tests and Release build pass;
installed b853f060933607ed356754485c572e79f8ea0ddcc4b892f1032dfea63548f227.
Runtime84935 clean exit13:43:09.611 failed=0, idle shell terminated. Trace disabled
unless GALAXYPAD_MOVEMENT_TRACE=1; next resume gameplay/performance work, do not
repeat short center-start drags as movement acceptance. Full goal remains active.

**R614 movement boundary audit:** source routes UIKit moveX/Y through the mixer
to Dolphin MoveX/Y and Nunchuk directions with matching signs. Focused regression
now proves a neutral connected controller does not mask held touch axes over120
polls, release clears immediately, and a contact released before polling is not
latched. Input and stick-routing sanitizer suites pass. This makes short-drag
sampling a plausible explanation, not a diagnosed live cause. No production
input change, new build, runtime or performance claim. Next capture bounded
UIKit publication versus device-consumption evidence for the actual drag.

**R613 layout refresh works; stick test inconclusive:** installed8eb80408,
viewport publication logged and left cluster visibly shifts. Actual touch route
reaches story and Star Festival starting area; A advances all story prompts.
Text obstruction reduced, some longer lines still overlap. Short automated stick
drags gave no clear Mario displacement; no sustained-touch API available, so
movement not accepted or diagnosed yet. Runtime83333 clean exit13:33:13.203
failed=0, shell terminated. Next isolate UIKit axis publication/consumption before
calling this layout gameplay-ready. Full goal active, no FPS acceptance.

**R612 live layout test exposed missing invalidation:** R611 installed but title
controls stayed at previous positions. Host viewport starts zero and changes
after rendering; overlay had no corresponding relayout. Added cached viewport
comparison on existing UI timer, requests layout/logs only on change. New build
passes, not installed/live verified. Failed-preview runtime82906 clean exit
13:16:45.888 failed=0, shell terminated. Next verify new viewport log and layout;
R611 appearance remains unaccepted. Saved opacity1.0 not overwritten.

**R611 default left-cluster placement built:** iPad defaults use available bottom
letterboxing for stick/D-pad, capped by12pt safe-area margin. Same cluster shift
computed from default geometry; individually saved positions untouched. No phone,
button size, mapping or right-cluster change. Bounds/sanitizer and routing tests
pass; app d51f48bb…a0f8f1d built, not installed/visually accepted. Next story-screen
comparison at55% preview, including saved-layout behavior. No FPS claim.

**R610 opacity preview verified:** installed R609206091cb. Initial run revealed
saved opacity1.0; default change correctly preserves it. Separate temporary
launch override0.55 visibly improves text visibility, but stick/D-pad still
overlap words. Actual touch file→Play→story and A page advance work. Saved1.0
verified unchanged after clean exits13:01:42.651 and13:08:07.140 failed=0;
preview shell terminated, app installed/stopped. No layout/FPS acceptance.
Next adjust default positioning around available letterboxing without replacing
saved user layouts; opacity alone is not sufficient.

**R609 less-obstructive opacity default built:** SunPad styling/hit targets and
editor behavior retained; absent-key control opacity now0.55 instead of0.82 for
Galaxy text visibility. Explicit user settings untouched. Settings default,
explicit0.82 and clamp tests pass ASan/UBSan; settings test added to full suite.
Release app206091cb…406260 built, not installed/visually accepted yet. Installed
R608 shell remains idle. Next compare actual story screen and input at new opacity.

**R608 normal touch route verified:** stable normal app ff855d69/module3acdcddc,
all pointer experiments disabled. Diagnostic A+B at title only, then actual
UIKit drag+A selected existing file1, drag+A activated Play This File and visibly
reached opening story. Default path is usable for these targets; calibrated
experiment is not a prerequisite for this bounded route. No full-screen accuracy,
Direct Touch, gameplay/save or speed acceptance. P2-labelled icon observed in
detail remains unexplained, not proven second-controller configuration. Clean
native exit12:53:48.805 failed=0; normal app shell stopped, sole iPad Simulator.

**R607 full repository regressions pass:** first run caught stale source hash in
macOS reference-JIT test. Proved drift consists exactly of canonical R557
built-in-descriptor patch; test now reverses/reapplies it in temp copy and checks
both old/new hashes before selector tests. No runtime source changed. Full rerun
53750 exited0, check-r607-fixed.log ends Repository safety checks passed.
This is regression evidence, not gameplay/performance/device acceptance. Normal
app remains stopped; full goal active.

**R606 load classification refined:** exact retained macOS disassembly proves
sampled chunk-entry PC field and indexed code jump-table roles. Added conservative
local branch-table pattern classifier and negative regressions. Retained top20
loads:147 table,640 adjacent lazy-FP global,185 stack,3804 unresolved. Table
samples~0.51% of CPU leaves, not a cost estimate or whole-slowdown explanation.
No runtime/rebuild/performance gain. Next remaining high-weight CPU-state/guest
load provenance; do not promote a speculative dispatch rewrite.

**R605 CPU build/load audit:** current R562 build graph already has effectiveO2,
ThinLTO,PGO,strictFP; not a debug-build explanation. Reused exact retained macOS
profile/module through existing audit:4776 sampled loads in top20 chunks include
640 adjacent lazy-FP-global loads,185 stack,3951 unresolved. Unresolved is not
guest-data attribution and does not justify a broad rewrite. New report
shared-aot-work-r605.json. No rebuild/runtime; normal app remains stopped.
Next resolve high-weight load base provenance, not another compiler flag sweep.

**R604 common-clock trace + broader sample:** explicit mach_absolute host clock
and absolute GPU times, validated matching/parser tests.198/198 matched intervals
ordered; GPU-end→handler-entry median0.731249ms. Total staging waits0.619035s in
5.699802s trace (~10.9% aggregate/wall, not whole-app speedup). Cannot explain
the full cadence deficit alone. Broader3s sample has247 samples/CPU thread,
199 nested dispatch including35 float-future waits; native execution remains
substantial. Return to whole CPU/render balance before more callback probes.
Runtime77475 clean exit12:32:54.247 failed=0; normal app restored98312 exit0,
stopped. No performance fix or acceptance claim.

**R603 command-correlated waits:** added optional buffer identity to diagnostic
CSV and conservative same-buffer/contained-interval matcher. Tests/build pass.
Scene-armed capture matched all190 waits: median wait-begin→handler-begin1.642437ms,
handler-end→wait-end0.0341665ms. Most observed wait precedes handler execution;
queued work/completion delivery not separated. No synchronization rewrite or
performance gain. Runtime76911 clean exit12:25:23.817 failed=0; normal app restored
(12740 exited0), stopped. Full goal remains active.

**R602 handler cost measured:** scene-armed file-select capture,4096 rows over
6.347338s.3232 handler spans median0.000375ms/max0.024041ms;216 host waits
median1.4488955ms. Expensive original render-handler body is not supported as
the wait explanation in this capture. Delivery/queueing/wakeup remain unmeasured;
do not rewrite mutex or remove waits. Native clean exit12:18:57.898 failed=0;
normal app restored (3607 exited0), stopped. No speed/stability acceptance.

**R601 completion-handler probe built:** exact-source-gated tracker wrapper
measures original render completion handler, including mutex acquisition/work.
Logging occurs after original lock destruction. Sanitizer, delayed-arm and
concurrent trace tests pass; staged objects and isolated candidate compile/link.
Candidate6140e4be…149faed not installed/run. Normal ff855d69…cb34e4 unchanged,
no GalaxyPad process, sole iPad Simulator. Next scene-armed file-select capture
tests handler cost; no performance improvement or handler attribution yet.

**R600 scene-armed staging trace:** added diagnostic-only marker gate; no samples
or clocks before arming. Unit/integration sanitizer tests, object compile and
candidate build pass. Visually settled file select armed at12:05:32 local:
4096 records,1023 valid GPU intervals, GPU median0.066875ms versus host wait
median1.710834ms. Not subtractable scheduler cost or performance improvement.
Apple wait contract includes completion handlers; next measure handler/lock
duration without removing required synchronization. File select remained visible
at stop; runtime also logged FIFO Unknown Opcode0xff at12:08:27.966, so stability
is not accepted. Clean native exit12:11:05.229 failed=0; normal app restored
(67724 exited0), stopped. Full original goal remains active.

**R599 GPU timestamps available:** R598 candidate ran at title; cap exhausted
before any file-select action.1024/1024 GPU intervals valid. GPU median.055ms
versus host wait.779ms, not subtractable scheduler cost or file-select evidence.
Need explicit scene arming before further readback conclusions. Runtime74816/
59524 clean exit12:00:16.841 failed=0; normal app restored (90000 exited0), stopped.
No FPS improvement, source change or completed gameplay gate.

**R598 GPU-timestamp probe built:** Apple contract checked; reads after existing
completion wait, rejects zero/error/nonfinite/reversed intervals. CSV/summarizer
distinguish unavailable from unrecorded and keep GPU duration separate from host
wait. Tests/compile/relink pass; diagnostic app d5e0855f…b8f20 not installed/run.
Next live capture verifies Simulator timestamp availability. Normal app remains
installed/stopped; no performance or GPU attribution claim yet.

**R597 diagnostic candidate ran:** isolated link verified instrumented Metal
object ownership. Candidate982e9447…128d2f reached title/file select;4096 valid
staging spans captured. Copy setup32.1ms total,submit14.6ms,wait2225.4ms. Host
completion wait dominates measured spans, not necessarily total game or GPU-only
time. Trace lacks scene markers; no gameplay/depth/speed acceptance. Runtime74135
clean stop11:52:30.616 failed=0. Normal ff855d69…cb34e4 bundle unchanged on disk.
Normal app restored successfully (install30734 exited0), not relaunched. Next
verify available GPU timing semantics before separating execution from waits.

**R596 staged Metal timing probe compiles:** default-off copy_setup/submit/wait
wall-time spans,4096-record shared cap; operation-order/disabled-clock/CSV tests
pass ASan/UBSan. Hash-gated generator leaves pinned source and stable app intact.
Separate Simulator object f6935f3f…23adc0 compiled, not linked/installed/run.
Next link isolated candidate and collect bounded trace. Stage spans cover Metal
staging generally, not uniquely EFB and not pure GPU execution. No speed gain.

**R595 EFB flush regression:** inspected actual Simulator source graph. Sync
population clears pending flush; cached reads do not wait twice; async population
waits at first read. Actual PeekEFBDepth compiled against test doubles passes
ASan/UBSan for these branches/value/origin forwarding; regression added to suite.
No Metal/GPU performance proof or product optimization. Existing submission
experiments remain rejected; next distinguish Simulator staging setup/completion
cost before changing readback. R594 remains stopped; no runtime this turn.

**R594 context-off measured:** same app/module; context reader and dependent
experimental mapper disabled, native observer already off. Clean windows
28.49/37.44/34.94/34.87FPS, still failed. Diagnostics removal is not a sufficient
cure; no precise overhead estimate from these variable short runs. Runtime72759/
session21376 clean exit11:39:11.386 failed=0 through native confirmation; sole iPad Sim. No new build.
Return to native compute/readback investigation rather than more UI-flag trials.

**R593 observer-off measured:** same app/module, only native attachment flag NO.
Stable file select37.25/33.97/35.31FPS, overlapping earlier attached range; no
causal gain or zero-overhead claim. Slowdown persists without callback. Context
reader remains enabled; next isolate it/dependent mapper with context flag NO.
Runtime72333/session21546 clean stop11:33:15.626 failed=0, sole iPad Sim shell.
No rebuild/source change or performance acceptance; see PERF.md.

**R592 native-site attribution:** exact R591 module UUID/hash matched. Eight
explicit sampled offsets disassembled: mixed lazy-FP checks, single conversion,
nonfinite checks, jump-table access and checked RAM/EXRAM mapping. Aggregate
sample counts cannot be assigned to individual omitted PCs. No dominant rewrite
target proven; see PERF.md, generated/r592-*.asm. Next same-binary experiment:
disable only native observer attachment to measure diagnostic overhead. No new
runtime/build; R591 remains cleanly stopped. Full performance goal still open.

**R591 live touch visibility + performance comparison:** hiding/restoring works
over real file select; restored Touch aim and explicit A select existing file1.
Same-scene windows visible31.0/36.1,hidden33.5/31.9,restored34.8FPS: no consistent
gain and no60FPS acceptance. Short separate sample again shows native execution
and EFB waits (PERF.md), not evidence UI visibility is the main slowdown. Runtime
71366/session32084 clean exit11:23:54.574 failed=0; app ff855d69…cb34e4 unchanged.
Next performance step: attribute generated native hotspots in this fresh sample
to exact guest functions/operations before selecting a semantics-preserving change.

**R590 installed manual visibility/persistence verified:** app ff855d69…cb34e4
launched without developer game paths (shell only). Real Controls→Touch Controls
hid all sticks/buttons while preserving Menu. Terminate/relaunch retained off;
menu remained reachable and restored primary controls. CUA screenshots/AX checked,
native captures ui-r590-hidden/restored-native.png saved. Preference left on;
shell terminated, sole iPad Sim. No game input/performance claim from this test;
R589 isolated input tests remain the input evidence. Next: live-game touch-off/
restore check, then return to the outstanding measured performance bottleneck.

**R589 manual Touch Controls switch built/tested:** Controls menu now has an
on/off action (default on). Off hides sticks/buttons and rejects pointer touches,
clears held input, and preserves menu access. Manual preference composes with
controller auto-hide; editing exposes controls temporarily without losing it.
Isolated UIKit tests pass (70873/session26635 exited0), Release build passes
(48733), SHA ff855d69067bc1cac94d53ce2770f807d760ee3510f18ce0aea0a243b9cb34e4.
Installed (session40239 exited0), not launched; product menu/gameplay visual verification remains next. This provides
manual unobstructed viewing, not automatic cutscene handling or performance.

**R588 installed auxiliary controls verified:** R587 app d49995b6…d9aea0 ran
as70273/session7663, same R562 module/experimental pointer flags, sole iPad Sim.
Native Controls toggle showed1/2/Minus, retained its checkmark on reopening,
then hid them again; primary controls unchanged. Verified primary/extra native
screenshots. Menu resume worked; diagnostic A+B reached file list, actual Touch
drag then UI A selected existing file1. Clean stop11:10:27.891 failed=0.
Title screenshots27/40FPS and file-list32.7FPS still fail performance. No new
gameplay/save acceptance. Extra keys left off. Next shell gap: PRD Touch Controls
on/off is still missing (controller auto-hide is not a manual toggle), useful
for unobstructed viewing without guessing guest cutscene states.

**R587 advanced Wii keys:** PRD9.3 explicitly permits rarely used keys in the
advanced layout. 1/2/Minus now default hidden, accessible through Controls →
Show Extra Wii Buttons and always present in the layout editor. Plus, D-pad,
movement, A/B/C/Z/Spin stay available; no saved geometry or key mapping changed.
Toggle clears held input before hiding hit targets. Isolated UIKit regressions
pass on the sole iPad Simulator (runtime70038 exited0); Release app build passes.
Installed app SHA d49995b631e7b5f315c25233161dfba51b4bed9e0256e45ea63d5d39ffd9aea0;
not launched. Fresh product/gameplay visual acceptance remains next; this does not resolve
story text obstruction from primary controls or the performance defect.

**R586 file-detail touch route verified:** opt-in calibrated mapping now also
accepts stable FileConfirm nerve806a0128, never pending transitions. Readiness/
camera sanitizer tests and Release build pass. Real UIKit drag highlighted Play
This File; explicit A reached the opening story. Verified ui-r586-play.png and
ui-r586-started.png. App SHA813fef1b…ce95b; same R562 observer module. Runtime68993
clean stop11:01:28.092 failed=0. File detail roughly24–28FPS; opening screenshot
48.2FPS, later windows45–47FPS: performance remains failed. Overlay still covers
story text. No automatic action, default/device promotion, gameplay acceptance,
or save-integrity claim. Next: reduce story/control obstruction and validate
gameplay pointer contexts before broadening this experimental mapping.

**R585 actual touch consumer verified:** installed R584 app, enabled22/calibrated
touch flags. CUA drag through UIKit Touch channel hovered file1; native hit at
(321.355,298.066). Real A selected file detail; B returned. Native menu open/
dismiss cleared retained aim/hover; fresh drag then hovered file2. Screenshots
ui-r585-touch/cleared/retouch.png verified. Ordinary release intentionally retains
Classic Pointer aim; cancellation/reset clears it. No automatic action or new save.
Runtime68048/session47340 clean stop10:49:57.000 failed=0; sole Simulator shell.
Performance still roughly25–38FPS. Full context mapping/actions and PRD remain
open; experimental file-list mapping is not a product-wide promotion.

**R584 opt-in touch consumer builds:** Simulator GalaxyPadDevCalibratedTouch
requires22-profile/context observer and evaluates mapping at mixer consumption.
Only pointer coordinates/visibility change; buttons, axes and controller pointer
remain untouched. Snapshots older than250ms reject, as do unknown readiness and
any observed Spin/tilt (neutral experiment invalidated until next session).
Input/camera/readiness regressions and build79599 pass, app SHA
2a2314c091ba07845a63abf1de908eace83f9bf9b33ecfe736e2b03aa7e68b94, not installed.
R581 remains installed/stopped. Next live TOUCH-channel test: existing dev input
file is Controller and bypasses mapping. No consumer runtime acceptance yet.

**R583 runtime calibration bridge builds:** exact-DOL VI observer now publishes
optional menu model configuration and monotonic observation time under a separate
mutex; input reset clears both. Readiness requires22-profile flag, FileSelect
waiting Nerve/no pending transition, expected calibration/filter and neutral
reference/acceleration horizons. Sanitizer rejection cases and camera grid pass.
Build76830 SHA059d23c6f67f3c7d9574654705f487f63dc1fecc9a2be06c44ac237d7fc4701b
passed, not installed. R581 app remains installed/stopped. Next freshness-gated
touch consumer; no input/action change or live bridge acceptance yet.

**R582 shared forward model extracted:** GalaxyPadPointerModel.h now owns the
neutral menu projection/WPAD/KPAD path formerly duplicated in the test harness.
Explicit configuration and neutral-orientation prerequisite; malformed values,
missing/degenerate LEDs reject. Sanitizer tests retain441/441 coverage at22/24
and reproduce four R580/R581 measured positions within.002 logical pixels.
No runtime wiring/build/launch yet; R581 installed app remains stopped. Next
bridge verified runtime context/configuration to the touch path. No gameplay,
performance or full Direct Touch acceptance; original goal remains active.

**R581 live edge checks pass:**22-degree inverse places valid pointer at bottom,
left and right test points, <=.524 logical-pixel coordinate error. Verified
ui-r581-bottom/left/right.png during leases; no-target returns expected, no A.
Bounded movement observer allows misses to carry position evidence; regression
tests and build24370 pass. Installed app SHA
418d3477202e96ef1f229f86cb150ea1d11e1135c2c2ef675b8e217c6c11710c.
Runtime66373/session31652 clean stop10:28:09.851 failed=0. Sole Simulator shell,
no game. Normal/device profile unchanged; next configuration-aware touch mapping
integration. Performance still23.6–32.7FPS in captures; full goal remains active.

**R580 inverse verified at one live target:** Simulator-only22-degree profile,
inverse input(.411593,.685748) for desired(.38,.64) produces file1 hit at
(315.896,291.972), error(-.264,+.132) logical pixels versus832x456 expectation.
ui-r580-hover.png visibly confirms hover,27.3FPS. Initial ui-r580.png expired
lease; not hover evidence. App SHA
c90ab8764d798e99834d33113c400932e8e1fb6cb4925fc1e3cc350e76181e5c installed.
Runtime65791/session57265 clean stop10:21:15.821 failed=0; sole Simulator shell.
Normal/device profiles unchanged; no automatic taps or touch mapping promotion.
Next live bottom/edge checks and configuration-aware mapping; full goal open.

**R579 bounded inverse implemented, test-only:** finite/fail-closed shared solver
passes actual camera + reconciled neutral WPAD/KPAD model under sanitizers.
At current pitch20,420/441 viewport targets solve; bottom row is unreachable.
Pitch22/24 solve441/441 within0.0015 normalized (~1.25 logical pixels horizontal).
Fixed neighborhood handles integer-camera discontinuities;75 evaluations max.
No runtime/config/input changes or app rebuild; R578 remains installed/stopped.
Next live-verify pitch22 and inverse coordinates before touch wiring. Tracking,
readiness, performance, all original PRD/device/story acceptance remain open.

**R578 forward pointer chain reconciled:** live orientation/regular-point snapshot
matches audited conversion formula. Camera-to-KPAD discrepancy resolved by retail
WPAD Y inversion (767-row), now raw-instruction checked and included in camera
fixture. Both live regular points match within1e-6; no control-axis change.
Reader/hook/camera sanitizer tests pass; installed app SHA
2e209383c58d1aa94b2ed1c6d2e65703a62ae3d85249c007c82770e8f1e9133d.
Verified ui-r578.png file1 hover shows26FPS; no performance acceptance. Runtime
64595/session98723 clean stop10:08:42.213 failed=0; sole Simulator shell, no game.
Next bounded inverse against verified forward chain; full PRD remains active.

**R577 filter mode proven live:** 84 finite emitted-filter cases pass sanitizers;
conversion's 1000-case regression also passes. Read-only calibration now includes
mode, with raw retail load proof and missing/invalid/snapshot-retention tests.
Installed app SHA8aef69364b8f809e635d42b3bf21db6983c67424360e432213b05cf2df9f2745.
Title and file1 hover report mode0: strong near-target damping, not mode1's hard
dead zone. Verified screenshot ui-r577.png shows file1 hover and34.5FPS; no speed
improvement or Direct Touch acceptance. PID63970/session30170 cleanly stopped
10:02:16.246 failed=0. Sole Simulator shell remains; next active orientation and
bounded inverse validation. Full PRD/performance remain open.

**R576 conversion block executes:** extracted accepted generated8044FA6C–8044FB2C
agrees with midpoint/rotation/scale formula for1000 finite cases under sanitizers.
Probe explicitly doubles finite arithmetic and excludes tracking/filter/FPSCR;
not complete KPAD equivalence. generated/kpad-conversion-r576.log. No runtime/UI
or input changes; R575 remains stopped, sole Simulator shell. Next filter and
active orientation evidence before inverse mapping; full goal/performance open.

**R575 live calibration verified:** R574 host installed; title and two file-target
hits report center(0,-0.2), scale2.272727, radius0.03, sensitivity0.5. Verified
ui-r575-right.png; no automatic taps/save changes. Raw logical width608/832 audited,
not assumed EFB640. R575 PID62707/session91906 stopped09:48:20.013 failed=0; one
Simulator shell only. Next retail horizon/scale/filter execution proof before
inverse mapping; performance/full PRD remain open.

**R574 calibration reader builds:** retail setters identify P1 KPAD center/scale
and position filter fields. Raw instruction checks and bounded-reader sanitizer
tests pass; native query frames snapshot calibration. App76531 build passes,
SHA f6a3caacdc1719b6d735d11958c9b4dc2dba754f862a0bdc211b88ee965a8d33,
not installed. R571 shell remains stopped, no game/module rebuild. Next live
active calibration capture with existing observer module; no inverse/tap/FPS claim.

**R573 camera projection isolated:** actual CameraLogic projection/Matrix compiled
and tested under sanitizers; center/offset/hidden/two-target probes pass. Initial
ideal center expectation corrected for observed one-pixel float/truncation effect.
tests/test-pointer-camera.py added to suite, focused log pointer-camera-r573.log.
No runtime/settings/input changes, no game active, same single Simulator shell.
Next retail KPAD conversion/calibration audit; no guessed inverse or FPS claim.

**R572 live pointer sample proof:** installed R571 host; native reader sees two
distinct file actors/processed coordinates matching pointer-only movement. A hit
persists with pastValid1/currentValid0, confirming stale-validity boundary.
Coordinates also expose that host Cursor->virtual remote->KPAD is not direct
screen scaling. See DIRECT-TOUCH-CONTRACT.md and ios-runtime-r572.log.
Clean stop09:35:29.363 failed=0; sole Simulator/app shell, no game active. Next
camera/KPAD coordinate mapping audit, not heuristic two-point tap calibration.

**R571 processed pointer reader builds:** exact P1 chain/raw contracts verified.
Bounded reader captures past/current XY/validity; native query frames snapshot at
entry. Sanitizer tests cover malformed/nonfinite data, endian decoding and snapshot
retention; Release app65401 builds. Not installed yet; installed R568 shell stopped.
Next install new host with existing R562 observer module, live separated-target
sample correlation. No automatic taps, no module regeneration, full goal open.

**R570 pointer buffering identified:** exact USA instruction audit proves hit tests
use past XY+4/validity+0xc, not current XY+0x18. Movement copies current to past
before refreshing current. Retail validity predicate differs from Petari inline
helper, so source-map behavior alone was insufficient. Expanded raw-DOL audit
passes; generated/pointer-contract-r570.json. No runtime/module/UI mutation;
R569 remains cleanly stopped, one Simulator/app shell. Next correlate past sample
with host revisions before queued touch actions. Full goal/performance unresolved.

**R569 native observer delivery verified:** candidate attaches, misses and file1
hit match visible pointer highlight; ordinary A select/B back work. No mod fallback
or pairing-invalid messages observed. Accepted module remains untouched. Current
run59957/session29427 cleanly stopped at09:22:46.427 failed=0; app shell only,
ios-runtime-r569.log, same sole Simulator. Detach reset precedes exit delivery in
source; no dedicated live detach counter. No latest-touch revision proof or
performance gain claimed. See updated DIRECT-TOUCH-CONTRACT.md. Next guest pointer
sampling freshness investigation and matched performance work.

**R568 compact SunPad auxiliary keys:** iPad UIKit regression and Release app build
pass; compact 1/2 and horizontal +/- replace wide pills, phone auxiliaries move
down, letter-only faces/masks/editor preferences preserved. Installed app SHA
522b0dd47cd0f1cefb83ce74b76cb0f0fd6c872fa15d037df4a140ed5818b0be.
R559 clean stop failed=0 at09:11:41.692. New R568 PID59521/session66921 uses accepted
module, native observer OFF, same sole Simulator. Startup still in progress at
last initial check; now title and A+B transition to file select visibly verified,
generated/ui-r568-file.png. File screen instantaneous27.3FPS; prior30.5s window
35.705FPS, so performance remains unresolved. See TOUCH-UI-R568.md.
Observer module finished linking: candidate SHA
c1c06e0a03ab0822120f855291abf195139299b924e9363eb71408a15d521421,
IOSSIMULATOR and both exports verified. Original build log had trailing shell EOF;
current script bash -n passes and rerun73281 exit0 reports no work to do and vtool
success. Candidate is NOT installed/selected; next observer test remains separate.

**R567 verified link wait:** original build48689 still running. Same linker58198
advanced3:04→4:49 elapsed and32:33 accumulated CPU,688%CPU last check; no error or
restart. Sole Simulator remains paused. Poll same handle to completion before
module/export audit; do not treat the unfinished output as a valid candidate.

**R566 linking, same build:** module48689 has reached ThinLTO link; linker58198
verified live (42s,680%CPU), ninja54354. Do not restart. Added exact-DOL scan proving
one direct BL caller80178EC4 to query803FB0EC; indirect callers remain possible.
Native callback now ignores unsupported LR values; sanitizer regression and app
rebuild36983 pass. R559 remains paused. Next poll same48689 then module/export
audit and live validation; full goal open.

**R565 source and callback ABI checks:** candidate1328-file inventory/hashes
reverified. Actual host and GXRuntime CPU headers compiled independently: size3528,
gpr/pc/lr plus all other probed offsets/sizes match. New regression passes and is
in suite. Same module build48689 still live, beyond959/1333; retain handle through
link. Existing PGO mismatch/unprofiled and nested-comment warnings recorded, not
suppressed. App candidate ready; no install yet. R559 remains paused in one Sim.

**R564 host integration builds:** Simulator DevNativePointerObserver uses separate
module export, exact DOL/API/site validation and CPU-thread-only read-only callback.
Suppresses generic DevPointerHooks when selected. Scoped library outlives runtime
destruction and binding detachment. Pointer/binding sanitizer tests and app build
6167 pass (build-app-r563.log). Not installed yet. Same module build48689 remains
live,702/1333; continue that handle through link. R559 still paused in native menu.

**R563 host binding checks pass; same build running:** added observer-only API
compatibility and RAII registration helper. Rejects version/CPU ABI/size/DOL/site
list/function mismatch; invalid replacement detaches old registration; destruction
detaches once. ASan/UBSan test passes. Not wired into CoreHost yet. Candidate build
48689 revalidated live, advanced182→350/1333; no restart. R559 still paused in
native menu, single Simulator. Next host attachment while stopped and final module
export/identity audit when this build completes.

**R562 candidate module compiling:** exact accepted source hashes verified; isolated
generated/native-observer-r562 copy changes only query803FB0EC and return80178EC8
chunks. Calls inserted after existing PC materialization, before original work;
stripping additions recovers original bytes.1328-file manifest verified. Named
sites are outside outlined helper. Preparation regression passes. Candidate-only
CMake extension links observer bridge with actual GXRuntime CPU header.
Build session48689 is LIVE, build-native-observer-r562.log (last95/1333); poll
same handle, do not restart. R559 PID53265 paused via native menu while compiling,
single Simulator. Accepted module/app unchanged. Next link/export/coverage audit,
host attach/detach and live callback/input validation. Full goal remains open.

**R561 separate native observer bridge:** added optional module extension with
version/CPU ABI/size, exact DOL identity, two named sites and stopped-CPU
attach/detach contract. Read-only callback does not use ModManager or alter
CPUState layout. Sanitizer tests pass for identity, rejection, site filtering,
state preservation and detach. Not linked into a generated module or app yet;
site metadata is not emission proof. Next exact generated-site instrumentation
and module coverage audit before host attachment. R559 unchanged/live.

**R560 isolated native observer prototype passes:** tests/probe-native-observer.py
copies actual emitter/CFG into a temporary directory, inserts two selected label
callbacks and disables outlined counted loops only for their containing functions.
Generated C executes under ASan/UBSan: external entries, fallthrough, back-edges,
local returns, null callbacks, results and cycle charges pass. No production
emitter/ABI/module/guard change. Next metadata/observer-only dispatch contract and
exact query-site integration; generic mod patches cannot be treated as observers.
R559 PID53265 remains live with DevPointerHooks NO, sole Simulator at title.

**R559 diagnostic removed from live path:** clean R558 Stop08:33:00.255 failed0;
same installed binary relaunched with DevPointerHooks NO. PID53265/session4980,
ios-runtime-r559.log. Title visually verified, no mod-loaded/mod-fallback/hook
messages, one GalaxyPad process. VI context probe remains opt-in enabled.
Native emitter review confirms local gotos/return dispatch and counted-loop
helpers can bypass generic dispatcher hooks. Preserve current fallback guard;
next isolated emitted-code tests for named-site coverage before a native observer
candidate. No FPS gain or Direct Touch completion claim; Simulator left at title.

**R558 live hit-test callback proven (diagnostic only):** exact-DOL-gated
DevPointerHooks registers app-linked observers. Pairing/bounds/reset sanitizer
test passes; app build passes. Installed after clean R555 exit08:28:32.733.
PID52918/session72476, ios-runtime-r558.log; executable58d41d658e9d7de59358360cd9d6dcfcb07b4f9269c1ea07483d58338aaf52d2.
File1 hover visibly matches actor81144cc8/result1; entry return80178ec8 matches
audited BL80178ec4→803fb0ec. No input injection. IMPORTANT: built-in hooks force
chunk803fb0a0–803fc0a0 into fallback. Do not promote this route as normal Direct
Touch or compare its FPS. Next native hook delivery alternative/remove diagnostic
flag before performance runs. One Simulator at file select, writer neutral.

**R557 built-in runtime plumbing:** RuntimeConfig now accepts app-linked descriptor
pointers (must outlive Runtime), exclusive with mod directories. Existing manager
validates them; rejection returns ModuleRejected before core start. Empty list
preserves directory path. Canonical0028 patch/bootstrap hash/peel/restore added;
reverse check/shell syntax and static-hook sanitizer test pass. Core57945,
provision/app59191 exit0. No hook enabled or candidate installed yet; R555 still
live. Next exact-DOL-gated bounded entry/return observer and live delivery test.

**R556 static pointer-hook route verified in isolation:** actual ModManager compiled
with dynamic modules disabled; ASan/UBSan proves attached observer ABI/title checks,
entry/return CPU-state preservation, stack matching and unload cleanup. Test added
to suite. Runtime config still only exposes directory mods; next add explicit
built-in descriptors and validate emitted-module hook delivery before touch action.
No runtime/build/settings change; R555 PID51592 revalidated live. Full goal open.

**R555 About installed and checked:** R552 clean exit08:13:13.051 failed0.
UIKit host67480 exits0 with PASS including About assertions. R554 candidate
installed, executable0e1c5bc68e4961a91cad3872f0511dabceceebbe8d7cd5b2dcfbd0dd729c3c3a;
PID51592/session67312, ios-runtime-r555.log. About visibly readable, Done works
at startup and active title. A+B while sheet open discarded; resumed title stays
put, fresh A+B subsequently reaches file select. Logs record native UI block and
clear on both transitions. Sole Simulator left there, input neutral. No full
notices/audio/device/performance acceptance. Next Direct Touch integration.

**R554 About screen built, not installed:** three-dot About action presents native
scrollable Dynamic Type text with app version, dependency credits and private-only
rights wording. Explicitly labels full bundled notices/corresponding-source audit
unfinished. Uses existing host presentation/input-clear gate. Release build passes;
UIKit test host includes read-only/Dynamic Type/wording/Done assertions (execution
pending). Next install and verify screen/dismiss/pause behavior; R552 PID50620
remains live unchanged. Full notices, Direct Touch and performance still open.

**R553 fallback follow-up:** current source confirms hook_fb includes native cache
fast paths, not only interpreter execution; R489 macOS/JIT counter caveat still
applies. One-second live sample completes (ios-r553-file-select.sample.txt): two
explicit interpreter subtrees among144 CPU samples,21 CPU float-future waits and
21 video depth-readback waits. Overlapping counts, not a recoverable time budget.
No evidence for fallback dominance here; do not claim an optimization. R552
PID50620 remains unchanged/live. Continue Direct Touch freshness integration;
performance work must retain native execution/readback attribution, not infer
cost from cumulative fallback totals.

**R552 live selector transition verified:** R551 candidate installed after clean
R549 exit08:03:50.460 failed0. PID50620/session87943, ios-runtime-r552.log;
executable c24ffa5a2d9bd0d688591e6c6fbc3a73c03658dcc8ce958b76b8a5c4bc879f2a.
Visible selection→confirmation→B Back matches states806a0114→0118→0128→0110→0114,
all mode5. Pending0118 was observed while current0114/old item still pointing;
confirmation retains old item but invalid flag set. Do not authorize by mode or
cached item alone. Sole Simulator left at file select, input neutral.
R549 shutdown also reports fallback102102386/hook_fb260286803 (not zero); no
performance/AOT acceptance. Next resolve guest input/hit-test freshness and
classify these fallback paths before claiming their cost or changing policy.

**R551 scene-state probe built, not installed:** source inspection confirms mode5
is shared by file selection and copy selection; Spine can have a pending Nerve.
Exact-DOL audit verifies LiveActor spine+0x50 and pending+8/current+4 getter.
Bounded reader exposes both; opt-in probe now logs state changes. Sanitizer test,
exact-DOL audit and Release build pass (build-r551.log, session39858 exit0).
R549 PID49469 remains installed/live, sole booted Simulator. Next clean Stop,
install R551 and compare ordinary file-select→confirmation states visibly before
integrating queued taps. Guest input-revision freshness remains unresolved.

**R550 queued-tap policy:** added tested one-shot queue binding gesture, epoch,
pointer revision, intended target and monotonic deadline. Rejects stale/mismatched
observations, waits for readiness/A release, cancels safely. ASan/UBSan queue and
existing mobile input tests pass. Not connected to guest input yet: R549 cached
hover cannot certify processing of a new pointer revision. Next establish that
guest hit-test/input boundary before wiring this policy; no timer shortcut.
R549 PID49469 confirmed live, unchanged; no install or additional Simulator.

**R549 file-target observation:** Release candidate installed after clean R548
Stop; sole Simulator PID49469/session18901, ios-runtime-r549.log. Bounded mode5
request-owner reader identifies selector81111800, file1 item81144cc8 and file2
item81192d08. Both visibly highlight, report pointing/noninvalid, and clear on
pointer disappearance. Native screenshot ui-r549.png verifies file2 hover.
Sanitizer tests and exact-DOL call-site audit pass. This remains an opt-in
diagnostic, not automatic selection: cached hover may lag new coordinates.
Next implement fresh-input-bound queued selection with cancellation, without
letting stale taps enter another menu. Input neutral; Simulator left visible.
SunPad-style letter faces/lower auxiliary controls retained. Performance open;
file-select windows around42–47 FPS are not gameplay or speedup acceptance.

**R548 LIVE context probe:** opt-in Simulator DevPointerContext checks exact DOL
and observes every sixth VI field on CPU thread, logs changes only. Release build
passes; installed after clean Stop. PID48778/session44678, ios-runtime-r548.log.
Visible title corresponds mode4/object8091f3d8, A+B→file select mode5/same object.
Brief unknown sample between title samples observed; context cannot be assumed
continuous. No target readiness or Direct Touch action yet. Sole Simulator left
at file select with saved Mario1, diagnostic input neutral. Performance open.

**R547 context-reader foundation:** exact-DOL getter chain and mode offset
verified; bounds-checked CPU-thread reader and sanitizer tests added. Not wired
into runtime yet; no new overhead or touch behavior. Same R545/PID47040 remains
live. Next bounded CPU-thread mode observation, then target-readiness integration.

**R546 menu contract verified:** investigated Direct Touch readiness instead of
hardcoding a delay. Downloaded pinned Bussun USA symbol text; raw hash-gated DOL
audit verifies file-item pointing/invalid loads, menu button Nerve/A call sites,
and P1 menu predicate calls. See DIRECT-TOUCH-CONTRACT.md and executable audit.
No runtime hook/UI behavior change; target identity/lifetime probe is next.
Same R545/PID47040/session79921 remains live. Full product/performance goal open.

**R545 live validation:** R544 pointer candidate installed after clean
R542 Stop. Sole Simulator now PID47040/session79921, ios-runtime-r545.log.
Executable SHA256 a70d10c4fea5d94391ccdafeb96eed8e0456f8b9d476eb1c081054236b34ff43;
AOT module unchanged3acdcddc…1bac0. Save/config backup ios-r545-nand-before.tgz.
Mixer/controller/lease/exact-pointer regressions pass. Mario file1 survives
restart/update and loads opening story; GameData hash unchanged99d432d5…ab64f.
Immediate pointer+A still misses file selection.0.2s pre-aim succeeds at file1
and Play. Thus branch fix is not sufficient for zero-delay Direct Touch; no
latency/FPS gain claim. Screenshot ui-r545-reload.png verified. Current scene
first opening page, inputs neutral; Simulator remains visible.

**R544 built, NOT installed:** pointer hidden→visible bug isolated and corrected
by preserving visibility before EmulatePoint overwrites position. Exact-body
regression fails before/pass after; visible smoothing preserved. Canonical patch
0023, bootstrap hash/peel/restore/scope and repository test added. Incremental
Simulator core/provision/Release app builds pass. No FPS/calibration fix claimed.
Live remains R542 PID45436/session75150 at Festival hill foot. Next clean stop,
install candidate, test immediate pointer reacquisition against file selection;
save remains fresh Mario file1 and gameplay/reload/Direct Touch gates open.

**R543 live gameplay evidence (same R542 binary/session):** touch A advanced all
opening pages into Star Festival. Diagnostic forward2s moved Mario into flowerbed;
touch A jump and forward3s+touch A visibly moved/jumped toward hill. Final neutral
left Mario stationary at hill foot. Native screenshot ui-r543-festival.png verified.
No first-Grand-Star/save-reload/physical-multitouch acceptance. Gameplay windows
41.465890/41.493492FPS. One-second5ms sample ios-r543-festival.sample.txt: UI mostly
sleeping136/141; CPU118/141 under native dispatch (22future waits), video21/141
depth-readback waits. Not a quantified optimization budget. Pointer source lead:
EmulatePoint writes positive position before checking whether it was hidden;
its intended immediate-reacquisition branch is unreachable. No core change yet.

**R542 LIVE — mobile file creation/opening reached:** Simulator-only, explicit
DevInputFile full-snapshot bridge implemented through existing Controller mixer
source (real controllers reserved while opt-in active, touch remains separate).
Lease/malformed/reset sanitizer tests and Release build pass. Includes R541.
Sole iPad PID45436/session75150, generated/ios-runtime-r542.log. R540 stopped
cleanly; Wii/Config backed up first. Actual A+B→file select→file1 hover/select→
create/Mario icon/confirm→Play This File→opening story visibly verified.
generated/ui-r542-opening.png captured natively and visually verified.
Input automation is NOT touch/hardware/gameplay acceptance; no save reload yet.
Observed pointer acquisition needs pre-aim before A; cursor alignment needs
calibration (Play target required y.92). Menu snapshots31–51FPS, performance open.
Current file1 is fresh Mario/0stars; next advance opening and test movement/jump,
then calibrate pointer before context-aware Direct Touch. See SIMULATOR-INPUT.md.

**R541 built, NOT installed:** mobile physical-controller Right Shoulder alias
corrected C→A, allowing right-stick aiming with A/B shoulder actions. Default Y
still C; user mappings preserved. Failing-before/passing-after chord regression,
controller and mixer sanitizer tests, Release build pass. No touch-layout change.
Live Simulator remains R540 PID44540/session35150. Hardware/gameplay acceptance
still open; a controller-only build is not worth interrupting the visible run.

**R540 installed:** SunPad-style R539 layout retained. Fixed letterbox contacts
stealing pointer ownership from playfield touches. Regression fails before fix,
passes after; pointer movement/cancellation also preserve independently held A.
Handler tests are not physical multitouch acceptance. Release build passes.
R539 stopped cleanly (`runtime exit failed=0`); sole iPad Simulator now launching
R540 PID44540/session35150, generated/ios-runtime-r540.log. Title and retained
layout visually verified in Simulator: 35.5FPS snapshot, not performance or
gameplay acceptance. No performance gain claimed. Runtime left visible.

**R539 LIVE (supersedes rejected R538):** user rejects button subtitles/top
utility row. Removed all visible action copy, SunPad A/B/X/Y/Z lettering and
lower-corner cluster pattern restored using actual reference screenshot/source.
X=Spin, Y=Nunchuk C; identifiers and bits preserved.1/2 above movement, +/- pills
above right cluster. New regression checks enforce letter-only/no-top-aux defaults;
UIKit input/editor/tilt/nonoverlap tests and Release build pass. Sole iPad runtime
PID43791/session37622, ios-runtime-r539.log, ui-r539-verified.png. Title visibly
verified; still~37FPS observer snapshot, not performance acceptance. Optional
yellow stick remains tilt, not pointer. Current research identifies simultaneous
aim+A/B as priority; don't substitute more styling for interaction implementation.

**R538 LIVE:** user rejected generic touch layout; researched Nintendo Galaxy
manual and handheld pointer precedent, implemented Galaxy-specific iPad hierarchy
(A/Spin prominent, action-labelled A/B/C/Z, left camera controls, upper utilities,
optional tilt in SunPad Controls menu). See GALAXY-TOUCH-DESIGN.md for sources and
remaining interaction gates. Release build/UIKit tests pass; actual menu tilt
on/off verified, restored OFF. Sole Simulator PID42791/session33924, log
ios-runtime-r538.log, same module/native resolution/dual-core local experiment.
Verified screenshot ui-r538-verified.png. R536 communication warning recurred
without profiler; separate defect, not fixed. No gameplay/ergonomics acceptance.
30s FPS logging now live: post-menu window1073/30.000012=35.766652FPS; earlier
53.099824 window spans startup/title transition and is not comparable. Performance
still open. Next user-priority control work: context-aware Direct Touch and live
action chords; do not claim Classic Pointer or title is the finished experience.

**R537:** mapped R536 Run offsets against exact app disassembly: +1072 is
the return site of native dispatch, +988 dispatch-sample flag load, +1488 lookup
metadata load. Aggregated sample leaves do not expose per-offset weights; no
interpreter-dominance claim. Prior lookup-snapshot optimization already failed
R469 repeatability, remains parked. Added opt-in GalaxyPadLogFrameRateWindows
30-second presented-frame windows, reset across native UI/lifecycle/Stop.
Release build passes; new telemetry NOT installed/live-tested yet. Current visible
runtime remains R536/PID41431. Next enable telemetry on a clean launch, verify
window resets, then collect comparable title intervals without profiler/builds.

**R536 LIVE (supersedes R533):** sole iPad Simulator DE8E956F… running PID41431,
console session5578, generated/ios-runtime-r536.log. R535 UI revision installed:
separated smaller SunPad defaults, compact auxiliary controls/FPS, hidden status
bar; UIKit overlap/44pt/input/editor checks and Release build pass. User settings
preserved. Title visually verified; no gameplay/60Hz acceptance.

R534 CPU Profiler hung; exact xctrace stopped after user observed ~6FPS. Subsequent
counter recovered to41–44 but Wii Remote interruption appeared; not stability.
Fresh R535 title29–41FPS. R536 LOCAL EXPERIMENT adds Core/CPUThread=True only in
Simulator data profile (81B4D48A…/Library/Application Support/GalaxyPad/Config/
Dolphin.ini). Thread separation verified by short sample; title31.8/39.1FPS,
no clear gain and NOT promoted to product defaults. Next isolate native module/
dispatcher cost and map fallback PCs; do not assume dual-core solved performance.
Leave this one Simulator visible; don't start another. Sample ios-r536-title.sample.txt:
106/140 CPU-thread samples under native chassis_dispatch (includes8 EFB waits),
21 exclusive StaticRecompCore::Run; UIKit main mostly asleep. No sustained profiler.

**R533 LIVE:** user asked why game wasn't visible; returned focus to runtime and
left sole iPad Simulator/game OPEN. PID39834, console session7078, log ios-runtime-
r533.log. External development root/disc/module (installed data removed R531),
no fallback JIT, FPS on. Upright title snapshots41–52 presentedFPS, not stable60
or gameplay acceptance. Sample ios-r533-title.sample.txt targets CPU-GPU work.
Do not boot/relaunch another runtime before checking this live session.

**R532:** standalone Share Diagnostic Log added to SunPad menu, opening existing
redacted local review before explicit system sharing. Shared report context now
labels configured image/DOL hashes separately from missing loaded-module data.
App build and redaction tests pass; new UI/share cancellation remains unverified.

**R531:** live SunPad removal Cancel preserves installed image/DOL; confirmed
idle removal deletes 6.4 GiB installed tree, leaves no staging, and all19 NAND
file hashes unchanged. Free space39→46GiB. Original image preserved; reimport
required for next private-data boot. Simulator off. Running-game removal untested.

**R530:** SunPad stored-data removal connected to confirmed runtime exit, atomic
detach and off-main deletion of installed GameData only. Sanitizer tests preserve
save/recovery sentinels and reject unsafe targets/running state; build passes.
Live confirmation/removal UI untested; no real data deleted. Recovery cleanup open.

**R529:** isolated UIKit host passes actual overlay slider hit testing, selection,
ValueChanged→1.25x geometry/settings, and A+B callback/release sequencing. Tests
invoke UIControl events, not physical touches; real gestures/gameplay remain open.
Product code/settings unchanged. Test app uninstalled; sole Simulator shut down.

**R528:** sole-iPad Wii2 placement visually clear above1; SunPad editor selects
it and exposes “2 size,” then exits normally. Slider automation did not change
size, so resize/persistence remain unverified. No game runtime; Simulator off.

**R527:** audited simultaneous touch state (independent held bits, multitouch
overlay); no single-button-only bug found. Added missing Wii 2 via SunPad button/
editor path, existing runtime binding already present. App build/input tests pass;
new control layout and real multitouch/file select still require UI verification.

**R526:** orientation correction verified through live imported-data safety/title
screens without modal. Separate physical UI A/B clicks reach runtime counters
(2 button samples,4 transitions,last0); simultaneous chord/file select unverified.
Clean Stop, exit failed=0, Simulator off. No gameplay/performance acceptance.

**R525:** removed Galaxy-only iOS26 scene-orientation lock, retaining landscape
masks. Sole-iPad rotation now upright without native modal; fresh landscape
relaunch also upright. App build passes. Gameplay-time/both-side/device rotation
unverified. Idle test only, no game runtime; Simulator shut down.

**R524:** imported private GameData boots to visible Galaxy title with only the
development module argument (no external root/disc), fallback JIT disabled.
SunPad Stop yields shutdown counters, runtime exit failed=0 and visible Game
stopped. Simulator off. Sideways presentation persists until native modal;
orientation is next blocker to usable mobile testing. No gameplay/FPS acceptance.

**R523:** real supported-image import through SunPad folder menu succeeds on sole
iPad. Installed WBFS/DOL hashes match configured identities; both files/ and sys/
compare byte-for-byte with known-good run1 (diff exits0). No leftover import stage.
Temporary Documents selection copy deleted; installed 6.4 GiB retained for next
launch, 40 GiB available. Simulator off. Imported-data boot/gameplay not yet tested.

**R522:** explicit unactivated-stage discard added and connected to activation
failure. Worker/activated-data guards, verified-cancel cleanup, installed marker
and save preservation pass sanitizer tests; app build passes. Cleanup is off-main.
Crash-leftover and retained previous-install recovery/cleanup remain unfinished.

**R521:** expanded transaction sanitizer tests pass copy-progress cancellation,
simulated extraction failure/partial-stage cleanup, stopped-runtime and single-use
activation gates, byte-identical synthetic source and save sentinel preservation.
Full repository suite passes (`generated/check-r521.log`). Synthetic 32 MiB test
identity/stub extractor are test-only; real Wii extraction remains unverified.

**R520:** SunPad folder import adapted and enabled; Documents Files sharing/open
in place configured, private GameData/NAND stay in Application Support. Sole-iPad
synthetic WBFS selection correctly rejects, leaves source unchanged and no stage,
and menu reopens. App build passes. Test fixture removed, Simulator shut down.
Real import, picker file-provider access, empty/multiple-folder UI remain open.

**R519:** sole-iPad cold-start menu → import disclosure → Files picker → cancel
→ reopened menu verified. Fixed idle Stop disabling the overlay; rebuilt and
verified Stop → Game stopped → menu opens again. No game/image import performed.
Orientation initially sideways after rotation, upright after picker presentation;
cold-start orientation still needs investigation. Simulator shut down.

**R518:** SunPad Import/Reimport action now opens the document picker and drives
private copy/verification/cancellation, then waits for CoreHost teardown before
activation. Menu available before setup/after Stop. App build and host syntax
pass; no UIKit or real import acceptance yet. Folder import/removal stay disabled.
Simulator relaunch prefers installed data with development module; device module
packaging/startup remains unfinished and is explicitly disclosed in import result.

**R517:** private import transaction compiled: bounded cancellable copy, verified
extractor handoff, stopped-runtime activation gate, single-use ownership and
off-main failed-stage cleanup. Synthetic rejection/pre-cancel tests and existing
atomic activation tests pass under sanitizers. Not wired to menu yet; real copy,
mid-operation cancellation, cleanup failures and extraction remain unverified.

**R516:** checked extractor now accepts thread-safe cancellation, polled during
hashing and between file exports, including a final completion gate. Simulator
app builds; cancellation runtime tests and the import transaction/UI remain open.
Actual SunPad menu and touch implementation remain the mobile UI baseline.

**R515:** atomic staged GameData activation/rollback helper passes real-filesystem
sanitizer tests and iOS syntax. Save isolation verified with synthetic sentinel.
App import transaction integration and real extraction remain unfinished.

**R514:** SunPad-derived checked Wii extractor builds, with configured exact image/
DOL hashes and fail-closed per-file exports. Not wired to import UI or exercised
on game data yet. Transaction activation/rollback and extraction tests are next.

**R513:** mapping UI swap and on-disk values, reset and dismissal/resume verified
on sole iPad. Full repository checks pass. Native Stop clean; no physical
controller/gameplay or across-relaunch mapping acceptance. Simulator shut down.

**R512:** SunPad-style controller assignment UI enabled, with Galaxy action swaps,
versioned persistence and neutral reset. All120 mapping permutations tested;
app build passes. UI/relaunch/controller hardware acceptance remains pending.

**R511:** Apple controller adapter integrated with runtime/mixer lifecycle and
SunPad P1 ownership; app build and policy sanitizer tests pass. Actual controller
connect/disconnect/input unverified; configurable mapping UI still unfinished.

**R510:** SunPad-derived single-player controller ownership and Galaxy Wii
mapping/pointer/tilt/reset policy added. Sanitizer tests pass; Apple controller
callbacks/menu integration and hardware/gameplay tests remain to be done.

**R509:** actual local report generation, synthetic redaction, preview and
dismissal/resume verified on sole iPad; clean Stop. Share-sheet path unverified;
stable preview toolbar IDs added for follow-up. No upload; Simulator shut down.

**R508:** Report a Problem now connects to guided local generation, readonly
preview and explicit Share. App build and isolated report/redaction/log-rotation
tests pass; UIKit flow still untested. Detailed PRD diagnostic fields incomplete.
No upload or Simulator launch; pending resize/held-input checks remain open.

**R507:** SunPad diagnostics backend adapted with strengthened redaction and
size bounds; focused formatting/privacy tests pass. Not connected to the menu
yet; next local report/preview integration and end-to-end privacy verification.
Held-touch/resize runtime checks remain pending; Simulator off.

**R506:** SunPad-derived sticks now invalidate old touch ownership on reset;
hidden controls clear input. Build and existing input/routing tests pass, UIKit
held-contact test pending. Resize handler diagnostic added for next single-iPad
test; this newly built app has not been installed. Simulator remains off.

**R505:** upright landscape title/reference controls verified. Editor A selection
and FPS toggle/pause/resume visible; resize remains unverified (AX slider value
changes without geometry/persistence). Native Stop clean. Next isolate reference
slider gesture delivery and complete input/first-play and required menu actions.

**R504:** explicit Simulator Device → Orientation → Landscape Left yields a
correctly upright full-landscape shell; no app orientation policy change needed.
Geometry diagnostic confirms landscape window/scene. Next repeat actual game/
reference-control tests in this explicit orientation; device/resizing unverified.

**R503:** SunPad-derived menu/controls/editor integrated into app; build passes.
Single-iPad visible menu/settings/editor open/Done and confirmed native Stop pass.
Full action adapters, editor gesture/input tests and scene presentation remain
unfinished. No gameplay/performance acceptance; see journal for exact artifact.

**R502:** actual SunPad overlay/menu/editor source port now exists as
GalaxyPadGameOverlay, with normalized Wii input adaptations; strict Simulator
syntax passes. Not yet wired into CMake/main. Next integrate native-menu lifetime,
Stop/settings/actions and replace the prototype before visible UI validation.

**R501:** direct SunPad shared settings port added with provenance; Simulator
syntax and Foundation getter/range tests pass. Not yet wired into the app.
Next finish reading/adapting actual reference overlay/menu/editor, then replace
prototype UI. No Simulator running; full mobile gameplay/performance gates open.

## Active user override — iPad/iPhone implementation authorized

**R500 USER CORRECTION:** use SunPad's actual three-dot menu and touch-control
systems, not the custom table-sheet/overlay substitutes. Direct pinned-reference
port is now the next action; preserve tested runtime/input safeguards. See
MOBILE-IMPLEMENTATION.md. No SunPad UI parity accepted; Simulator shut down.

**R499:** full R498 regression passes. Added stable tilt-setting AX identifiers.
Early-startup Stop exposed a separate ignored graceful-shutdown event; single
10s second-request fallback implemented/builds, runtime test pending. Simulator
off. Ready-title Stop previously passed; no broader shutdown acceptance claimed.

**R498:** manual tilt-stick mode, sensitivity/inversion/recenter and visible mode
label implemented. Routing/mixer sanitizers and app build pass; runtime mode UI
and game tilt mechanics unverified. Full suite running, no Simulator launched.
Full advanced controls/menu/gameplay and performance remain open.

**R497:** accessible sizing visibly changes A, survives relaunch, and confirmed
Reset Layout restores default positions/sizes. Native shutdown passes both runs.
Full R496 regression passed. Simulator off. Raw drag/pinch and gameplay unproven;
next advanced Galaxy controls/tilt and remaining menu sections.

**R496:** per-control sizing/persistence, pinch and accessible size actions
implemented. Size bounds/input sanitizers and app build pass; runtime sizing,
reset and relaunch unverified. Full regression running in check-r496.log.
No Simulator running. Advanced controls/full menu/gameplay remain open.

**R495:** edit-only accessible move actions visibly reposition A and persist
normalized coordinates. Instrumented mouse drag never reaches recognizer; drag
validation remains open. Actions disappear on Done; shutdown passes. Full
size/advanced controls/reset accessibility/menu remain incomplete. Simulator off.

**R494:** first normalized-position editor builds; Edit/Done UI transitions and
post-editor native shutdown work. Drag attempts did not move or persist controls;
gesture delivery versus coordinate targeting needs diagnosis. No editor pass.
App/Simulator shut down. Full menu/advanced controls/gameplay remain open.

**R493:** corrected Stop from paused menu completes normal guest teardown and
visibly reaches Game stopped. Same safeguard added to dealloc; build/sanitizers
pass, deallocation-specific runtime test pending. App/Simulator shut down.
Next editable/advanced controls and full native menu; gameplay/performance open.

**R492:** native menu opens, touch visibility toggles, Done/system dismissal
return to game; Stop confirmation/cancel works. Confirmed Stop from paused menu
hangs because guest cannot process STM power-button event. Host resume-before-
shutdown correction built next; runtime retest required. App/Simulator shut down.
Full R491 regression passes. Full menu/editor and mobile acceptance still open.

**R491:** viewport-backed Classic Pointer compiles and reaches emulated Wii
sampling (6,434 visible-pointer samples). Native stop passes; app/Simulator off.
Target accuracy/depth and simultaneous A+B/file select still unverified. Full
suite57927 subsequently passed; native menu/editor and mobile performance remain open.

**R490:** separate touch A/B taps reach emulated Wii input:21 held samples,
4 transitions, final0. Native stop verified again. Simultaneous A+B, pointer,
movement gameplay/editor/full menu remain open. App/Simulator shut down.

**R488:** first movement/button touch overlay connected to host and builds.
Runtime delivery/visual layout test next. Pointer, editor and full menu unfinished;
macOS LC fast-path launch defaults differ from mobile, causal audit still open.

**R487:** input device registration=1, title visible, first-frame feedback and
native Stop Game completion verified. Significant fallback counters observed:
16.7m fallback,37m hook_fb; classify before performance comparison/acceptance.
Joystick component builds, not yet placed/wired. App/Simulator shut down.

**R486:** host now registers the Galaxy device after core startup, supplies its
mapping and clears input on lifecycle/menu/stop. Builds pass; runtime device
registration, touch delivery and hotplug recovery still need tests.

**R485:** Galaxy-owned virtual input device compiles for Simulator: buttons,
Nunchuk movement, pointer/hide, Spin and non-motion tilt through standard runtime
control groups. Mixer tests pass. Host registration/touch UI not yet connected.

**R484:** repeated iPad startup renders Wii screen without prior fetch-pipeline
or missing-shader errors in the bounded log. Added first-frame feedback/Stop Game
for next build; visible UI action testing pending. No gameplay/FPS acceptance.

**R483:** Simulator-only framebuffer-fetch capability correction implemented;
core/provision/app rebuild passes. Actual failing shader used render-target
color input. Runtime retest pending; physical-device/macOS code path unchanged.

**R482:** Galaxy AOT loads and visibly renders Wii wrist-strap screen in iPad
Simulator. Not gameplay: no touch input yet. Added missing public Sys resources;
build passes, rerun pending. Simulator render-target-read pipeline error remains
open. Runtime terminated and sole Simulator shut down; macOS unaffected.

**R481 correction:** scene/view actually1210x834 landscape despite portrait
Simulator capture. Presentation behavior remains open; do not keep changing
orientation masks. Next runtime boot and Galaxy controls, with responsive visual
acceptance still required. No mobile gameplay/performance evidence yet.

**R479:** native shell visibly launches on one iPad Simulator; no game started.
Portrait orientation remains a reproducible defect despite plist/delegate masks.
Shell terminated and Simulator shut down; next scene/orientation correction and
input/UI integration. This is not mobile gameplay or performance acceptance.

**R478:** first native UIKit/Metal Simulator app compiles and links, actual
IOSSIMULATOR binary confirmed. Isolated build script passes. Not launched yet;
touch controls, frame-ready feedback, import and full menu remain incomplete.
Matching Simulator module61005 also completed0; no live build remains.

**R477:** native Metal/runtime host implemented with worker-owned teardown and
menu/lifecycle pause reconciliation; Simulator compiler check passes. Not linked
or launched yet; input release/UI wiring and runtime tests remain next.

**R476:** Simulator native core provisioned into libGalaxyPadCore.a; script and
arm64 check pass. Matching module build61005 remains live at1317/1332; preserve
the same handle. Native app link/launch, controls and menu remain next, unproven.

**R474:** mobile input foundation implemented/tested: logical Galaxy actions,
Spin tap latching, two-source axes/pointer ownership and full release on lifecycle
clears. Sanitized test and iOS Simulator syntax pass; test added to repo suite.
Visible shell/controls not wired yet. Core build82535 exits0 in separate
ios-simulator-core directory. Runtime object platform IOSSIMULATOR verified;
matching AOT module/app still pending. No Simulator booted.

Chris now requests mobile implementation before closing macOS performance.
Preserve installed macOS app, keep G6–G9 open and pause optimization experiments.
Begin iPad core/AOT/native SunPad-derived shell, touch controls and complete menu;
then iPhone with one Simulator only. Device performance is unproven; Simulator
is not device acceptance. See updated EXECUTION-PLAN for scheduling override.

## Current direction — user refinement, 2026-09-08

**R470:** exact-disassembly join covers20 hottest chunks/7782CPU samples. Loads
dominate selected sites;513 of588 formerly labelled FP samples are fmov, now
separated from arithmetic. Actual ABI probe identifies d98 as downcount, not RAM.
No broad float or map-cache rewrite justified. Next prove high-weight load bases
before choosing shared work reduction. No FPS/product change; full goal/G6 intact.

**R469:** reverse-order pair rejects lookup snapshot promotion: candidate55.7842
vs control55.8897Hz, essentially equal instructions/VI and slightly worse tails.
R468 gain did not repeat; candidate parked, installed app unchanged. Saves intact,
both game/capture handles exit0/native-only/no Simulator. Full suite28233 exits0;
generated/check-r469.log ends Repository safety checks passed. Next shared AOT helper expansion across sampled
chunks, no unchanged third pair or snapshot tuning. G6/full mobile scope unchanged.

**R468:** same-graph isolated runner pair measured control55.2931 versus candidate
56.4910Hz; candidate~2.22% fewer process instructions/VI and improved p99
20.49→19.73ms. Preliminary one-order result, not stable60Hz or audio acceptance.
Both visibly retain fixture scene, save unchanged, clean exit/native-only.
Normal app untouched; next fresh-profile reverse-order pair before promotion.

**R467:** run-scoped metadata candidate is staged, not installed. Writer audit
supports fixed lookup storage during Run; mutable verification/module state
still read each check.4.79m differential cases pass in each sanitized/optimized
build. Real-flag isolated Run objects compile; added stack storage means no
speedup inferred. Next one-object isolated runner link and matched gameplay
comparison, preserving normal app/module/save. See PERF; G6/mobile hold unchanged.

**R466:** precision scope audit completed and local candidate parked: four
path-only sites, no established dynamic impact, shared external entries remain
unknown. No module build. Retained exact-runner profile now attributes3702/3711
Run samples to inspected loop regions; dispatchability/lookup account for1218
of28822CPU leaves. Next audit mutable writers before considering invariant-mode
specialization of shared execution-loop work. No FPS/product or gate change.

Full original PRD/G0–G15 remains the active goal; G6 is still lowest unmet.
EXECUTION-PLAN now incorporates R462/R463's ~3.81× AOT process-work/VI finding
and explicitly separates diagnostic progress from delivered FPS improvements.
Startup feedback is complete. Finish the current precision scope audit with a
go/no-go impact decision before any product optimization/build; no open-ended
microbenchmark lane. Next delivery is demonstrably smooth, audio-stable macOS
gameplay and remaining macOS acceptance, then iPad and iPhone with the complete
SunPad-derived appearance, touch/editor/pointer controls and three-dot menu.
Planning-only refinement; no new speedup, gate promotion or runtime test claimed.

## Active plan — user-directed reorientation, 2026-09-07

**R465:** canonical-single identity oracle800000cases passes bits/host flags under
unchanged control; NI-change counterexample proves invalidation needed. Existing
R195 guarded25bit experiment remains parked. External suffix entries, gated
scalar writes and callbacks prevent blanket single-provenance annotations. Next
map actual successful-producer/entry facts before a scoped code experiment; no
product/FPS change or module build. See PERF; G6/mobile hold unchanged.

**R464:** installed-module bounded arithmetic fixture passes44entry PC/cycle/
exception checks and measures~2753–2763host instructions per44guest-instruction
call including driver/dispatch. No rebuild or LLVM retest. Source distinction:
reference tracks single-precision register provenance; AOT helpers use repeated
general conversions. Next prove precision facts/observation boundaries before
any specialization. Synthetic-only evidence, no FPS/gate change or game running.

**R463:** reference work/VI measurement completes at59.9492Hz and69.047million
process instructions/VI versus AOT54.4876Hz/263.149million: about3.81x execution
work per VI, not just a cache-stall explanation. Same visible scene/save retained,
clean exit; no product/FPS change. Next actual sampled-block instruction-expansion
attribution with existing harness, preserving state/flag/callback semantics and
parked-experiment decisions. No new full-module or repeated aggregate capture.

**R462:** actual AOT low-overhead process-work/VI baseline completed, same visible
late scene and unchanged runner/module.30.0068s/1635VI=54.4876Hz;263.149million
whole-process instructions per VI. Clock compatibility and uncertain boundary
tests pass; both brackets yield same VI count. Clean exit/save106e unchanged.
Next matched reference process-work/VI window, not another AOT baseline. No FPS
fix/product change or G6/mobile promotion. See PERF for scope/confounds.

**R461:** added Apple-definition time-weighted counter summaries (AOT delivery
38.24%, reference44.70%; same interpretation), and tested a read-only macOS
process instruction/cycle snapshot probe. Raw Instruments counter arrays remain
unmapped; no fabricated retired-count claim. Next bracket matched VI windows with
process snapshots, avoiding another heavyweight Instruments capture. No game/
Simulator/build/product change or FPS gain this turn. See PERF for scope limits.

**R460:** actual reference counter comparison complete, clean exit/save unchanged.
Counter overlap/XML/missing-value validation passes. Reference P-core delivery
46.06% exceeds AOT38.10% despite faster execution: reject a larger relative
instruction-delivery fraction as explanation; no layout/rebuild justified.
Next inspect existing raw counter definitions for retired-work quantities and
guest-progress normalization. No new FPS/product change, no runtime/Simulator.

**R459:** CPU Counters capability and actual late-scene AOT capture completed.
Performance-core cycle-weighted instruction-bandwidth fractions: delivery38.10%,
processing6.28%, discarded7.74%, useful47.88%. Instrumented run visibly slowed;
these are not ordinary FPS or removable-time percentages. Same scene visible
before/after, runner exits0/native-only/save106e unchanged. Next matched diagnostic
reference counter capture and validate interval aggregation before code changes.
No game/Simulator left; full PRD/G6/mobile hold unchanged. Details in PERF/JOURNAL.

**R458:** retained-profile audit quantifies scattered sampled module code but
finds no cache/retired-instruction counters in the existing capture. New tested
footprint summarizer; current module UUID matches R422. No product/FPS change.
Next inspect CPU Counters event support, then one bounded accepted-AOT late-scene
capture capable of distinguishing instruction delivery from retired execution.
Do not repeat cycle-only profiling or infer cache misses from footprint. See PERF.

**R457 integration complete:** canonical 0027 frontend startup-progress patch
installed through bootstrap; initial/repeated bootstrap pass and launcher source
matches the R456 tested candidate exactly. Expanded six-case nonblocking monitor
test and full repository suite pass. Candidate and normal-app audits pass after
frontend-only promotion: frontendc283de0c, runner671729c6/module1fb635f7 unchanged.
Previous frontend retained in generated/frontend-before-r457. No runtime rerun:
R456 supplies same-binary visible startup/cancel/failure/gameplay evidence; this
turn proves integration/package identity, not new FPS/audio acceptance. Next
EXECUTION-PLAN step2 CPU/audio blocker; startup side task closed. No Simulator.

**R457 planning checkpoint:** refreshed EXECUTION-PLAN.md against R456 evidence.
Original PRD/G0–G15 remain intact. Finish the tested startup-feedback patch's
canonical integration once, then return to the measured AOT CPU/audio blocker;
no new frontend audit loop or rejected optimization replay. Startup feedback is
not an FPS gain. macOS acceptance still precedes iPad then iPhone, with the full
SunPad-derived shell, three-dot menu and touch/pointer/Spin/tilt scope retained.
Planning-only change; no product code, build, runtime or gate status changed.

**R456:** controlled failure dialog and actual-game handoff pass on isolated
startup-progress app. Elapsed startup visible; parent window disappears after
module-ready; real-save Observatory and movement work, Command-Q exits both0,
save106e unchanged. Frontendc283de0c; accepted runner/module unchanged. Normal
package still untouched. Next canonical patch integration and focused wait/UI
policy regressions, then frontend-only promotion audit. Audio1underrun/4backlogs
and known heavy-scene performance deficits remain; no G6/mobile promotion.

**R455:** isolated frontend linked without changing normal build products.
Visible18s startup status captured using controlled non-game child; separate
120s-delay close test gracefully terminates child and parent exits0/no orphans.
Failure-dialog and actual-game readiness/handoff still pending; not packaged.
Use new frontend-progress-r455 XDG for dummy tests, never R447 gameplay profile.
R448 raw log was inadvertently overwritten by test reuse; correction recorded
in MACOS-ACCEPTANCE.md. Saves unchanged. No gameplay performance claim.

**R454:** isolated startup-progress frontend compiles with actual cached flags.
It draws elapsed startup status at4Hz, hides on the existing module-loaded log
marker, and handles close as graceful child termination request while retaining
nonblocking monitoring. Staged only, NOT packaged or visually accepted. Next
compile/link this frontend alone and exercise launch/cancel/failure/ready behavior
with one child before canonical patch integration. Game CPU/audio deficit unchanged.

**R453:** page-table prototype parked after boundary-only timing fails to show
a repeatable gain. Nested callback and acquired-pointer ordering tests pass in
isolation, not runtime integration. Next address R448's verified hidden-launcher/
~40s pre-window startup feedback defect using existing parent wait path; no module
rebuild. This is not a fix for gameplay CPU/audio deficits. G6/mobile hold intact.

**R452:** broader data-page resolver prototype matches635520 pointer/offset cases
with sanitizers, but validating mapping metadata every access is slower than
current ranges. No module build. Next enumerate actual callback/mapping mutation
boundaries before any boundary-only refresh design; no stale-pointer shortcut.
This is not the code-dispatch two-range optimization. See PERF.md for evidence.

**R451: park narrow restore prototype.** Full actual-flag compilation loses
238,389,378-entry PGO metadata in candidate. No valid speed comparison or game
build follows; this does not prove it is slower. Limited measured scope does not
justify retraining/rebuilding now. Next broader AOT/reference memory-contract
source comparison, not another tiny helper. Full PRD/G6/mobile hold unchanged.

**R450:** next sampled chunk identified as register save/restore plus dispatch.
Isolated three-load whole-range prototype passes7616 ASan/UBSan full-state and
callback-count cases. Not installed and no timing gain measured. Next full-block
profile/code-shape check before considering a module. Entry-cycle/return validation
and all original PRD/G6/performance/mobile gates remain open. See PERF.md.

**R449:** retained-profile/assembly audit rejects FP-availability guard elision
as the next performance candidate:238 recognized guard samples/28822CPU samples
across two hottest guest chunks, with callback/exception requirements intact.
No game rebuild or speedup claim. Next exact sampled-site/behavior audit of
805170A0, not another already-rejected hottest-chunk microbenchmark. See PERF.md.

**R448: packaged-entry check executed.** Actual frontend Play → bundled child →
real-save Observatory → visible movement → native pause/resume → movement →
Command-Q passes this narrow path; parent session24515 exits0, save unchanged,
no game/Simulator left. Details/boundaries in MACOS-ACCEPTANCE.md. Three audio
underruns/five backlog drops and slow-scene deficits remain open. Next step2 of
EXECUTION-PLAN.md; do not repeat step1. No speedup or mobile promotion claimed.

**Current execution queue: [EXECUTION-PLAN.md](EXECUTION-PLAN.md).** This supersedes
older next-action proposals below, not the original PRD or G0–G15. G6 remains
lowest unmet. Finish one current packaged-entry stability check, then resolve
measured macOS cadence/audio deficits, complete the macOS story/mechanics/stability
gates, and only then promote to iPad followed by iPhone. The full expected touch,
pointer, Spin/tilt, SunPad-derived three-dot menu and product appearance remain
mandatory. Recent parked experiments delivered no verified installed-game FPS gain.

**R447 acceptance reorientation:** see MACOS-ACCEPTANCE.md for the consolidated
evidence boundary. Fresh package audit passes; normal runner/module still match
R390. R77 Nunchuk/explicit selection, R78 actual import/handoff and R80 responsive
parent monitoring are already evidenced, despite older stale pending notes.
Next current packaged frontend→visible child real-save gameplay/pause/resume/
shutdown check, using prepared frontend-acceptance-r447 disposable profile and
no states/reimport/rebuild. Preparation only, no game launched yet. This addresses
product-path evidence, NOT the unresolved macOS cadence/audio performance blocker.
Full PRD/G6/mobile hold unchanged; parked optimization experiments stay parked.

**R446 decision: PARK the return-envelope/selector experiment.** Profiled-IR
objects preserve the real65,272,501entry count;55k full-state checks pass.
Initial arithmetic timing looked favorable but longer5M-call BAAB did not
reproduce it (selector231.75–232.30ns, C225.68–232.38ns). Merge/store is slightly
slower in both orders. No consistent gain; no game-module build, promotion or
unchanged repeat. LLVM also remains parked. Next review remaining macOS G6
gameplay/stability acceptance and last accepted runtime evidence before selecting
further performance work; do not default back to rejected dispatcher/compiler
microbenchmarks. Full PRD/story/mobile/product-shell scope stays intact.

**R445 profile compatibility:** the direct branch guard loses the real function's
65,272,501-entry PGO profile; reject that form. An equivalent inline selector
preserves the caller switch CFG, keeps the exact entry count, and produces no
missing-profile warning. It leaves ctx->pc unchanged and maps only impossible
return targets to the existing default.55k execution/327680 target checks pass.
No gain established: incidental unprofiled timings overlapped the repository
suite and are not performance evidence. Next a quiet comparison using the
audited profiled compiler settings before any module build. Product unchanged;
LLVM and earlier generic dispatcher experiments remain parked.

**R444 audit/candidate:** historical R139/R140/R420 already investigated generic
host-loop/entry-frequency changes; do not repeat them. New C-only local-return
envelope guard leaves original sparse switch and cycle guard intact.327,680
target checks and55k actual-chunk state/RAM/flag cases pass. Isolated merge/store
C35.60–35.66ns vs control36.30–37.27; arithmetic224.46–226.86 vs234.86–240.66.
These are synthetic, unprofiled-build timings, NOT installed/FPS evidence.
Next inspect current generated source and cached PGO/compile graph to determine
whether a matched candidate can preserve or honestly account for profile changes;
no full rebuild/promotion before that check. LLVM remains parked. Product unchanged.

**R443 decision: PARK this LLVM backend experiment.** On the cached full chunk,
normal arithmetic entry passes1000full-state/RAM/flag cases but IR takes307–324ns
versus C228–242ns (ABBA). Merge/store was already~3× slower. Broader synthetic
interior-entry arithmetic comparison also fails; it is preserved, not masked.
No full LLVM module, further unchanged rebuild or speedup claim. This does not
prove LLVM can never help; this candidate lacks evidence for further investment.
Next return to existing C-path dispatch: establish guest-entry distribution
using an existing bounded trace if suitable, and test one supported change to
entry/return dispatch shape while retaining SMC validation and cycle accounting.
Prior fixed-size chunk/primary-entry split/unsafe-direct-call/mapping-cache
experiments stay parked. Existing STATICRECOMP_TRACE_FILE samples every2^20
dispatches; it may locate entries but is deterministic sparse sampling, not an
exact distribution or unbiased cycle-cost profile. Inspect prior traces first.
Full original PRD/G6/macOS-first/mobile hold unchanged; installed game untouched.

**R442 execution checkpoint:** direct-context state shrinks the SAME chunk to
187,112bytes __TEXT (1.39× C), stack2,960bytes. Synthetic88k memory/32k policy/
30k baseline and new11k exact-chunk interior-entry state tests pass. But the
tested merge/store path costs~110ns IR versus36–37ns C (ABBA): NOT a speed win.
No full-module go. Next reuse these cached objects for one arithmetic-heavy
path with explicit finite-input fixture and correctness checks; do not rebuild
or infer whole-game performance from this narrow path. Product unchanged.
Full PRD/G6/mobile hold remains. See PERF R442 for fixture setup corrections.

**R441 structural experiment:** keeping private cached CPU slots in memory
reduces the SAME chunk's stack from94,528 to2,944bytes and __TEXT from2,405,424
to1,243,140bytes. C stays byte-identical at134,452bytes of __TEXT. All88k memory,
32k exception-policy and30k baseline cases pass. This supports cached-state SSA
merging as the large-stack cause, but code remains9.25× C: still NO full module
or speedup claim. Next test removal of duplicated cached/context state traffic
against this same chunk and correctness corpus; materialize currently writes
every function-wide dirty slot at each boundary. Keep this a bounded experiment,
not a general compiler rewrite. Installed app and full PRD/G6/mobile hold unchanged.

**R440 go/no-go: NO full LLVM module in the current chunk shape.** Exact
R422-profiled chunk0x804B60A0 (1024 instructions,1143/28822 leaf samples) emits
successfully, but experimental ARM64 __TEXT is2,405,424bytes versus C134,452
(17.89×), with a~92.3KiB stack frame. This is a code-generation scaling defect,
not a measured speedup. Keep generated/game-chunk-r440 as the reproducible
case; next inspect all-instruction-entry/state-merge lowering and test one
bounded structural correction against this SAME chunk before any expansion.
Do not blindly rebuild a full game module or present a tiny-helper timing as
representative. No runtime fixture/FPS comparison completed; installed app
unchanged. Full original PRD/G6/mobile hold remains in force. See PERF R440.

**R439 prototype fix verified:** a fresh isolated stage corrects mapped-store
reservation clearing, mirror normalization and reservation synchronization/reload
around journals. Expanded88,000-case memory corpus passes with no masks, including
journal mutation. Baseline30k, exception-policy32k and ARM64 probe guards pass.
Unfixed R433 control still fails the same expanded corpus. Product/reference
sources and installed app unchanged. Next select one measured gameplay block
from the existing R422 profile and compare C/IR generated work and CPU cost under
a defensible fixture. This is the go/no-go checkpoint before a full module, not
permission to assume all opcode/chassis/callback contracts or FPS acceptance.
Use generated/llvm-arm64-probe-r439-fixed; keep R433 as the unfixed control.

**R438 memory decision:** new 80,000-case real-runtime memory corpus exposes
30,000 failures: external stores clear reservations too early in IR; mirrored
reservation addresses are not normalized; the journal observes stale reservation
state despite matching final state. MEM1/MEM2, edges, remapping and journal
events are now compared without masks. Baseline30,000 still passes. Next make
one staged-only reservation-boundary fix against the actual runtime contract,
then rerun this corpus and FP policy checks. Do not build a game module yet.
The normal installed app is unchanged; these are prototype defects, not a claim
that the user's lag comes from reservations. See PERF/JOURNAL R438.

**R437 timing decision:** the focused 32,000-case policy oracle passes separate
full-state/RAM/flag expectations for C suffix-precharge and IR faulting-instruction
charge. Pinned Dolphin interpreter and ARM64 JIT source support charging through
the faulting instruction, not its unexecuted suffix. Do not patch IR to copy C's
precharge. The strict differential discrepancy remains visible; this is not
whole-backend equivalence or permission to alter the installed C module.
Next extend memory/callback boundary coverage in the same staged probe, retaining
the explicit exception-policy oracle; then evaluate one measured gameplay block.
The existing C exception overcharge is a separate correctness issue, with no
evidence yet that it causes the sustained gameplay slowdown. See PERF R437.

**R436 evidence update:** the expanded real-runtime differential corpus ran
480,000 cases; 32,000 fail, all solely in downcount on FP-unavailable exits.
C precharges the remaining basic block; IR charges instructions individually
before the exception. The original 30,000-case baseline still passes. Do not
mask cycle differences or blindly change either backend to match the other.
Next determine the chassis timing contract at exception/dispatcher boundaries
and add a focused expected-cycle oracle before any backend integration or
full-module build. See PERF/JOURNAL R436. Installed app remains unchanged.

This section supersedes all historical next actions below. The active goal is
the **entire original PRD D1–D12 and goal loop G0–G15**, including the expected
SunPad-derived macOS/iPadOS/iOS product experience. Performance work is a means
to that product, not a replacement goal. Original acceptance criteria remain
unchanged; no gate is promoted by this planning update.

### 1. Resolve the macOS performance/stability blocker

G6 remains the lowest unmet gate. Preserve the first Grand Star and real
save/relaunch evidence from R60/R61 and persistence recheck R363; the remaining
current-artifact timing/stability proof is not complete.

- Evidence: matched late Good Egg AOT CPU time was 16.6832 ms versus 6.2571 ms
  for the accuracy-enabled diagnostic JIT reference (6.8277 ms without arena
  Fastmem). This identifies an execution-subsystem opportunity, not proof that
  a compiler alone explains every reported 20–40 FPS episode.
- Park the vector helper: matched gameplay showed no meaningful improvement.
  Do not repeat unchanged fractional helper, compiler-flag or profiling loops.
- Next bounded experiment: extend the existing C/ARM64-IR differential harness
  for FP exception exits, rounding/special values, and memory/callback boundaries.
  Preserve complete state, cycle, RAM and host-flag comparisons. R434 already
  passes 30,000 cases with actual runtime helpers; full repository suite18146
  is terminal exit0 (`generated/check-r434.log`). This is not a speedup.
- Decision checkpoint: after those contract tests, compare one measured gameplay
  block's generated work and execution cost. Proceed to an isolated game candidate
  only with a defensible correctness contract and meaningful measured opportunity.
  If absent, document the result and pivot; do not expand into an open-ended
  compiler port or build a full module just because the prototype compiles.
- Candidate acceptance requires matched visible gameplay, a moving/heavy route,
  cadence and frame-time tails, responsive input, audio, transitions, saves and
  clean shutdown. A quiet 60 Hz counter, synthetic test or microbenchmark is not
  acceptance. Retain safe dispatch/SMC validation, strict arithmetic and AOT;
  diagnostic JIT is never the mobile or shipping solution.

### 2. Close the original macOS gates, then promote the same core

Finish remaining G6 evidence, then G7 story progression, G8 mechanics and G9
performance/audio/lifecycle/persistence/60-minute soak. After these gates, run
G10 on one iPad Simulator, shut it down, then G11 on one iPhone Simulator.
Never run more than one game or Simulator. No mobile build/promotion now.

### 3. Deliver the expected complete Apple interface

G10–G12 must carry the original PRD Sections 9.2–9.6, not a placeholder shell:
editable Galaxy touch layouts; movement/A/B/C/Z/pause; dedicated Spin;
stick-backed tilt; Direct Touch and Classic Pointer; controller handoff;
safe areas and accessible controls; SunPad-derived styling and original branding.
The full three-dot menu includes Display, Controls, Audio, Unstable Experiments,
Game Data & Saves, Share Diagnostic Log, Report a Problem, and About/notices.
Verify each action plus pause/resume, input clearing and return to gameplay,
along with import/save separation and lifecycle. Compare actual iPad/iPhone
screens and interactions to the pinned reference and PRD, not compilation alone.

G13 clean-clone/matrix, G14 physical-device hands-on evidence and G15 explicit
rights/release authorization remain required. No public release is authorized.
No game or booted Simulator was found at this checkpoint; installed app unchanged.

## Historical reorientation and experiment checkpoints (R425–R434)

The following records are retained as evidence, not current pending commands.

**R434 latest:**30emitter-used CPU field offsets/sizes match the actual
runtime, though full structs differ and must not be interchanged. New
C-versus-IR harness passes30000full CPUState/RAM/host-flag cases, first
standalone and then with real GXRuntime CPU/float/exception helpers. Four
small blocks only; no game/chassis/all-opcode or FPS acceptance. Next extend
the same harness to exception exits, FP modes/specials and memory/callback
boundaries before a measured gameplay-block prototype. Reuse existing tools;
no full module yet. Original PRD/G6/mobile hold and installed app unchanged.

**R433 latest:** offline ARM64 LLVM prototype now emits16synthetic blocks
and passes standalone expected-value execution tests. Explicit opt-in and
cross-chunk range-table rejection pass; unsigned narrow Apple ABI attributes
and dispatcher returns checked. Separate LLVM20.1.8 installed, default
AppleClang21/product pins unchanged. All source changes are staged outside
the reference tree. This is NOT the real Galaxy CPU ABI, differential proof,
mobile readiness or a speedup. Next C-backend/IR block differential tests and
actual runtime CPU/helper ABI audit before any game-module attempt. Full
PRD/G6 remains active; normal app unchanged. See PERF/JOURNAL R433.

R433 full repository suite92677 is now terminal exit0 (check-r433.log).
No active install/build/test/runtime from this step. Reuse staged probe and
LLVM20; do not reinstall or restage. Existing upstream C emitter/execution
fixtures provide the next differential-harness entry point.

**Latest decision R432:** vector candidate measured55.10VI Hz/CPU16.6606ms
versus matched control55.0667Hz/16.6513ms. No meaningful gameplay gain;
PARK, do not promote or repeat this helper experiment. Candidate exited
cleanly/native-only/save106e unchanged; no game/Simulator. Normal app remains
unchanged. Previous pending build/cooldown/candidate-launch notes below are
historical and complete. Next investigate a small dispatcher-preserving
ARM64 LLVM-IR prototype, with R426 target/AppleABI/code-validation barriers
explicitly handled and guest-block differential tests before any full-module
build. No blind backend switch, unsafe calls or precision relaxation. Full
original PRD/G6 remains the objective; this is not a compiler-only goal.

The running goal remains the entire original `GALAXYPAD-PRD.md` and goal
loop, including the expected iOS/iPadOS appearance and complete product shell.
Do not replace it with an optimization-only goal or a JIT-only macOS demo.

**Refined immediate objective:** address the demonstrated AOT CPU-execution
deficit with a substantial, correctness-preserving change, then prove smooth
macOS gameplay on the actual candidate. R424's same-runner/same-scene AOT
control used 16.6832ms CPU at 55.0667 VI Hz. R425's JIT reference with FPRF
and AccurateNaNs enabled used 6.25712ms at 59.9333 VI Hz. This supports an
execution-subsystem investigation; it is not full semantic equivalence,
proof of every reported 20–40FPS episode, or a delivered speedup.

**Next bounded step:** inspect the AOT execution/code-generation boundary
against the measured reference and choose one architectural hypothesis with
a falsifiable correctness test and meaningful potential gain. Audit any
alternative backend's ARM64/ABI/FP/memory/SMC support before prototyping;
the pinned LLVM backend does not currently support this target. Do not
blindly switch backends, weaken arithmetic, bypass validation, or repeat
parked fractional helper, compiler-flag or unchanged profiling experiments.
Reject a hypothesis lacking evidence rather than funding another full build.

R426 audit completed: LLVM is not a safe drop-in. Beyond its target gate,
Apple narrow-argument ABI attributes differ (actual-header compiler probe
passes for macOS/iOS Simulator), and its unconditional direct cross-chunk
calls do not preserve the C backend's dispatch-validation boundary. Do not
build a full module by removing the guard. Next inspect structural C-backend
state materialization/helper boundaries in measured gameplay hotspots;
retain validation and quantify scope before selecting a candidate. Details
and reproducible ABI probe are recorded in PERF. No product speedup yet.

R427 refines that next action: selected gameplay hotspots are load-heavy,
not dominated by stack spills; prior safe mapping cache already regressed.
Accuracy-enabled reference with arena Fastmem disabled (BAT-table lookup
instead) still reaches59.9333VI Hz/CPU6.82772ms, versus AOT16.6832ms.
Thus an arena-memory port alone is not supported as the large-gap solution.
Inspect generated block work/state liveness and helper boundaries next;
do not repeat register/mapping caches or run another unchanged profile.
Matched scene verified, clean exit, dropped0/save106e unchanged; normal app
unchanged, no game/Simulator. This remains diagnostic progress, not a fix.

R428 now has a concrete isolated candidate: paired NEON add/sub on finite
inputs, original fallback for nonfinite inputs, unchanged rounding/FPRF.
640000 full-state/host-flag cases and full1440case kernel oracle pass;
fullsuite34575 exit0. Offline kernel ABBA shows~4.00% less CPU time, not
Good Egg FPS or a solution to the whole reference gap. Normal app untouched.
Next audit cached module compile/link and PGO provenance for a valid isolated
control/candidate pair, then measure actual Good Egg gameplay if the pair is
defensible. No repeat microbench or full regeneration by default. PERF/JOURNAL
contain exact artifacts; full original PRD and mobile hold remain unchanged.

R429 current live work: isolated control/candidate module build session9634
is linking from cached chunks, no regeneration. Exact profiled function-entry
metadata matches between the pair; wrapper optimization changes six helper
counts versus original baseline, so installed-app parity is not presumed.
Candidate IR confirms vector arithmetic. Poll the SAME session to completion,
then inspect generated/vector-build-r429/build-provenance.json and run prepared
generated/package-vector-pair-r429.py only after both modules finish. No game
running; no normal app/module/marker changes. Next is matched gameplay on the
isolated pair, with original-app comparison before any promotion. Latest
source regression remains R428 fullsuite green; no shipped FPS claim.

R430 update: control module linked c308b0b1...ad2bc5 and module-info validates
ABI3/CPUABI3/1322chunks/19SMC/entry8000403c. SAME session9634 now links
candidate; final protected-input assertions still pending. Separate normal-AOT
profiles vector-control-r430/vector-candidate-r430 prepared with matching
slot2/save106e, neither launched. After terminal success/package audit, use
prepared measure-vector-r430.py with absolute runner path and exactPID,
visibly load slot2 before measuring and close promptly after final screenshot.
No game/Simulator, no normal app mutation, no FPS or goal-promotion claim.

R431 supersedes pending build state:9634 and package63457 both exit0.
Both isolated apps now validated; runners match normal671729c6. Signed
control moduleaa23fc0e...4328c0, candidate220f6aed...cc414a; complete hashes
in generated/vector-build-r429/packages.json. Original input hash assertions
passed, normal installed app unchanged. Build thermal pressure was Fair;
cooldown probe4062 runs60s to cooldown.csv. Inspect recovery before launching
prepared vector-control-r430, visibly restore slot2, measure and close; then
candidate sequentially. No rebuild, no runtime or FPS acceptance yet.

R431 runtime update: control completed,55.066667VI Hz/CPU16.651327ms/
p99wall20.181458ms,31thermal0/0/no dropped samples, native-only/save106e
unchanged, clean exit30466. Same scene verified before/after. Actual34.58ms
worst interval remains; no smoothness gate passed. Candidate not launched
yet: post-run thermalFair, cooldown82247 currently runs60s to between-r431.csv.
Poll that same handle, check recovery, then launch prepared candidate app and
profile using the identical10s warm-up/30s method. No rebuild needed; normal
app remains untouched. PERF contains exact window and identities.

Tail checkpoint: cooldown82247 has now exited0; last readings remainFair.
No process is waiting on that handle anymore. Recheck current thermal state
before candidate launch; do not restart the completed build or control run.

**Promotion sequence:** finish macOS G6–G9 evidence, then G10 iPad Simulator,
G11 iPhone Simulator, and the complete G12 SunPad-derived GalaxyPad shell.
The product must include editable Galaxy touch controls, Direct Touch and
Classic Pointer, dedicated Spin and stick-backed tilt, controller handoff,
safe-area layouts, the full PRD three-dot menu, import/save separation,
lifecycle, diagnostics and original branding. Verify both appearance and
actions against the original PRD/reference, not merely compilation. One
game and one Simulator maximum. G13–G15 retain their original requirements.

G6 remains lowest unmet because the full current-artifact stability evidence
is incomplete; first Grand Star and real save/relaunch were already proven
in R60/R61 and persistence rechecked in R363. Preserve that progress instead
of repeatedly restarting basic feasibility. No gate is promoted here.

R425 runtime closed cleanly (27460 exit0); save106e unchanged; no Simulator
booted. Its intended 30s window is retained, but the run was left open after
measurement and the VI buffer reports 5741 later dropped events. Treat this
as diagnostic evidence, not a clean whole-run or acceptance capture.
The chronological notes below are historical; this section supersedes their
pending next actions. Normal installed app and active module remain unchanged.

The full original PRD and G0–G15 remain the objective. This changes execution
priorities, not completion criteria. G6 is still the lowest unmet gate; no
mobile promotion or public release is authorized by this checkpoint.

1. **Reproduce the sustained slowdown the user sees.** Use the normal installed
   app, foreground window, verified working input and a visible gameplay route.
   Record exact settings, scene, thermal/host context, VI versus presentation
   cadence, frame-time tails and audio behavior. A quiet near60Hz checkpoint
   is not a substitute for the reported20–40FPS case.
2. **Identify its dominant cost before changing code.** Separate sustained CPU
   execution, graphics/readback/presentation blocking, and host scheduling or
   background-state effects. The rare80–90ms hitch is a separate symptom until
   evidence connects it. Use existing diagnostics first; do not default to
   another large capture or speculative scheduling policy.
3. **Make one high-impact, semantics-preserving fix.** Compare the same visibly
   verified route without profiler/compiler interference. Judge user-visible
   smoothness, tail times, audio and input—not isolated microbenchmark wins.
   Park fractional helper experiments unless new evidence makes one dominant.
4. **Close macOS gates.** Complete remaining G6 stability evidence, then original story/mechanic,
   performance/audio/lifecycle/soak requirements. Do not mark any passed from
   build logs, a screenshot, a short quiet window or an imported late save.
5. **Promote the same core and expected product experience.** One iPad Simulator,
   then one iPhone Simulator; full Galaxy touch/Spin/tilt/pointer controls,
   Direct Touch and Classic Pointer, editable layouts, SunPad-derived complete
   three-dot menu, import/save separation, lifecycle, diagnostics and original
   branding. Preserve physical-device, clean-clone and rights gates unchanged.

### Current decision and next bounded step

**R424 measured CPU-reference gap:** Same diagnostic runner34e96be1, exact
late slot2, Metal1x/dual core/Cubeb,10s warm-up then30s quiet hanging scene.
AOT55.0667Hz/CPU16.6832ms/p99wall20.0684ms versus referenceJIT59.9333Hz/
CPU6.04808ms/p99wall16.7356ms. EFBmean1.22219ms AOT versus1.54384ms JIT;
readback alone cannot explain the AOT deficit here. Both complete/no drops/
invalid/reset,31thermal readings each nominal-or-unsupported/lowpower0,
visible slot reload and final scene, unchanged save106e, clean exits.

Important boundary: JIT defaults FPRF=False, AccurateNaNs=False and FP
exceptions=False; AOT's arithmetic contract differs. Do not attribute the
whole10.64ms gap solely to compiler quality or ship JIT/relax AOT precision.
Next run prepared reference-fp-r425 with FPRF=True/AccurateNaNs=True using the
same app/checkpoint/window. FloatExceptions and DivByZeroExceptions remain
explicitFalse: source shows enabling them forces interpreter fallback, not
a like-for-like JIT precision setting. AccurateFmadds defaultsTrue unchanged.
This tests precision versus execution overhead without changing the product.
No game/Simulator; original full PRD and mobile hold remain.

**R423 next action — matched CPU-backend diagnostic, not mobile promotion:**
Remaining FPRF eligibility covers17.57% whole-chunk samples, not removable
cost. Exact80018C04 classification has5/28822 samples; the14-site804B6128–
804B615C chain has0 inclusive stack samples. Park this extension absent new
evidence; no candidate module built. A macOS-only, explicit opt-in reference
runner now selects Dolphin JITARM64 or default StaticRecomp in the same binary.
It is isolated at generated/macos/reference-jit-r423/GalaxyPad.app:
runner34e96be1bba0441eff255f03b031f0285ea183239cea2f91c4249ab4cd2e09df,
module1fb635f7 unchanged. Package audit and fullsuite7572 exit0. Patch remains
UNAPPLIED to reference sources; normal installed app unchanged.

Next launch this diagnostic with GALAXYPAD_MACOS_REFERENCE_JIT unset for AOT
control, visually reload prepared reference-aot-r423 slot2, then collect a
bounded stable-scene window. Close it before a separate explicit flag=1 run
using reference-jit-r423's independent matching profile. Compare only this
same runner with flag off/on; JIT warm-up, state compatibility, CPU selection,
render/input/save behavior must be verified. This tests shared-runtime/host
headroom versus AOT execution cost. JIT is not a product remedy, does not meet
AOT coverage, and is excluded by preprocessor from iOS. No game/Simulator
running. Full PRD and macOS-performance-first mobile hold remain unchanged.

**R422:** Normal-app late-route10s CPU profile saved/exported; same distributed
hotspot mix as R419 (Run3711/28822 leaves, dispatch1256, guest804B60A01143,
800180A01130), not a newly dominant wait or decoder. Saved darker-side rim
slot2 SHA74e453b5fd20b6a603a9811dfb363c9b66903662bda83971c558f57493adfe01
in late-good-egg-r422; reload untested. Native-only clean exit/save106e intact.
Do not repeat this profile unchanged. Build history rejects O3/Oz/blanket
inlining/Gateway-PGO repeats; pinned LLVM production backend rejects ARM64.
Unsafe direct calls bypass code validation and remain prohibited; inherited
opt-in now fails generation/module preflight with an actual-entrypoint test.
Fullsuite41653 exit0. Next bounded offline check: compare remaining164
adjacent-unobserved-FPRF sites (68chunks) against this gameplay profile before
considering any broader transformation. Largest gameplay chunk804B60A0 has23
sites. Eligibility alone is not speed evidence; park if contribution is small.
Normal app unchanged; no game/Simulator; full PRD/performance-first hold intact.

**R421 normal-app result:** Normal runner671729c6/module1fb635f7 restored the
same Good Egg slot1; exact-PID frontmost activation made default foreground
input work. Initial short movement verified, then checkpoint restored and
60s same movement fixture measured3464VI=57.7333Hz, CPUmean16.02255ms,
wallp9518.842ms/p9920.41575ms, EFBmean.571624ms. No drops/invalid/reset.
Worst frame interval57.276ms (CPU38.383ms) confirms a hitch remains.
Final view showed Mario hanging from the planet's darker-side rim, life3,
Star Bits2. Five-second bins55.8–60.4Hz; final15s56.0–56.4Hz with
CPU17.04–17.20ms. No sustained20–40FPS reproduced; no dramatic normal-app
versus diagnostic slowdown supported. Different trajectories/thermal context
prevent a causal build comparison. BackgroundInput persistedFalse, normal
app unchanged, save106e unchanged, runtime98500 and helper5353 exit0.
Next target the late darker-side workload on normal runner, not startup or
the earlier transient profile window, to identify the scene-dependent CPU
increase. No mobile promotion; full PRD and original acceptance unchanged.

**R420 attribution evidence:** Exact-instruction attribution completed; no single removable
runtime hotspot emerged. Run leaf samples span idle check529, backedge
policy774, chunk validation702, dispatch/REL/counter528, cycle/timebase289,
exception269, trace/lockstep234 and sampling guard202. Earlier R139 already
identified the same class of overhead. Do not repeat that optimization lane
without a new high-impact hypothesis. Next compare the normal installed app
on the same visibly verified Good Egg route, with actual foreground input,
before treating the diagnostic56.25Hz as representative of the user's app.
Runtime checks are not removed; no FPS gain or mobile promotion claimed.

The running goal retains the entire original PRD, including the expected
iPad/iPhone product appearance. Performance investigation is a prerequisite,
not a replacement goal. No milestone is promoted in this refinement.

R419's Good Egg CPU profile exported successfully: 29,266 CPU-thread leaf
samples; StaticRecompCore::Run accounts for 3,549 (12.1%) and chassis_dispatch
for 1,285 (4.4%). These are sample shares, not exclusive frame-time savings.
This is a gameplay-specific lead toward runtime execution/dispatch overhead,
not proof of the user's 20–40FPS cause. Inspect exact sampled offsets and
call paths before selecting one semantics-preserving change. Do not restart
parked movie microbenchmarks or large scheduler captures without new evidence.

R419 planned step (completed by R420 above): attribute runtime/dispatch samples in the exact diagnostic binary,
then test a concrete hypothesis on a repeatable visible gameplay route. Any
candidate must earn promotion through matched, unprofiled measurements and
correct input/render/audio/save behavior. Reconcile the diagnostic runner's
different library graph with the normal app before claiming a user-app gain.

Mobile promotion requires the original macOS G6–G9 evidence, not one near60Hz
window. Then execute G10 iPad and G11 iPhone sequentially and finish G12's
SunPad-derived visual/product contract: editable Galaxy touch controls,
Direct Touch plus Classic Pointer, dedicated Spin and non-motion tilt,
safe-area layouts, complete three-dot hierarchy (including Audio, game data
and saves, diagnostics and About), lifecycle and controller handoff. Verify
appearance and interactions on both sizes; a compiling mobile shell is not
acceptance. Clean-clone, physical-device and explicit publication gates remain.

R419 ended cleanly/native-only; no game or booted Simulator remains. Save106e
unchanged. No normal app or product source changed in this refinement.

**R418 measurement evidence:** Fresh Good Egg slot1 reload visually verified.
Bounded60s input run3375VI/56.25Hz, CPUmean16.127ms, p99wall20.885ms,
meanEFB.883ms; worst26.887wall/23.516CPU. Complete/no drops/invalid/reset.
New whole-run81939color reads but elapsed readback alone does not explain
deficit. Next short CPU profile in this scene to identify dominant gameplay
work, not another movie helper optimization or heavy scheduler trace. Final
movement position was not captured (automatic close preceded UI inspection);
input log/counters are not a whole-route visual proof. Runtime89103/helper23885/
thermal16593 exit0/save106e unchanged/native-only; no game/Simulator. Full PRD
and macOS-performance-first mobile hold remain; diagnostic app unchanged.

**R417 evidence:** Explicit background-input diagnostic live test
reached Good Egg Galaxy/Dino Piranha and movement worked; input750samples/
64transitions, IR visible136246/136246 samples, persisted BackgroundInputTrue.
Runtime45157 cleanexit0/native-only/save106e unchanged. Saved arrival slot1
a30fd3ed3f39e1978e2b726f9f09a9d0d723f67bc8edb3845844ff857198669b
in background-r416 (reload untested). Next fresh bounded gameplay measurement
from this new scene, not another Observatory run. VI overflow27294 and309
whole-run underruns forbid full-session performance/audio acceptance. Normal
app/source unchanged; no game/Simulator; full PRD/mobile hold intact.

**R416 build evidence:** Parser regression passes; isolated signed
diagnostic app built/audited at generated/macos/background-input-r416/GalaxyPad.app
(runnerb4df2afa/module1fb635f7). Actual CLI logs opt-in/default-off help. Normal
app/reference source unchanged. Fullsuite23060 exited0(check-r416.log).
Next background-r416 live flag/pointer/button/cleanexit test; no further build.
No game/Simulator. Diagnostic uses existing desktop library graph, not an FPS
A/B candidate; full original PRD/mobile hold remains.

**R415 correction:** The host RuntimeConfig defaults
input.background_input=false and DolphinRuntime writes it over the INI value.
R414's INI-only experiment was not a persistent explicit input policy; success
does not isolate it from focus/timing effects. Prepared unapplied, default-off
runner-background-input.patch adds an explicit logged CLI flag; apply check
passes against runner source967accdf. Next focused parser/runtime-config test,
isolated runner build and actual pointer/button test before more timing runs.
Terrace slot5 restored and tutorial advanced, but pointer later disappeared;
no galaxy entry or performance acceptance claimed. Runtime60494 exited0,
save106e unchanged, no game/Simulator. Full PRD and mobile hold unchanged.

**R414 evidence (interpretation corrected above):** BackgroundInput=False plus AX window
raise still produced zero button samples and no save-load. Changing only that
setting to True in the disposable profile allowed identical Pipe input to load
the real save and move Mario. Keep normal user settings unchanged; automation
must explicitly declare its input-gate policy and verify actual game response.
Moving Observatory60s:59.95VIHz, p99wall18.363ms, CPUmean15.196ms, no dropped
samples; not a reproduction of sustained20–40FPS or overall audio acceptance.
Next follow gameplay beyond this short Observatory route and match the user's
reported scene/window context (optional clarification sent). Inspect actual
normal-profile settings before attributing a diagnostic-only result: user
profile also Metal/1x/dual core, not an obvious resolution mismatch. No game,
recorder or Simulator remains. Historical capture plans below are superseded.

R412: full scheduler capture failed finalization/storage watchdog, no usable timing metadata; incomplete3.3GiB trace deleted after recorder terminal, logs/VI/clocks retained. Runtime57208/input99969/clock97050/fullsuite9724 exit0; recorder83740 exit1. Standalone1s preflight85054 saved29MiB/retained1.354s, thread-state export67171 exit0; still includes syscall/VM dependencies/other processes. Explicit --thread-only watchdog option/tests added. Next10s clock-bracketed loading-transition capture, not another full30s System Trace. Normal app unchanged/save106e unchanged/native-only/dropped0; no game/Simulator. Large stalls unresolved; full PRD/mobile hold intact.

R411: clock bridge/observed offset bounds and storage/time watchdog implemented/tests pass; actual1s bridge37.167us envelope. Fullsuite62416 exit0/generated/check-r411.log. Prepared scheduler-r411 exact slot1/save106e profile, no launch. Next one30s explicit-retention scheduler capture with contemporaneous clock coverage and watchdog; audit retention before aligning VI/thread states. No hard-byte-quota or unprofiled performance claim; normal app/defaults unchanged/no live handles/game/Simulator/full PRD and mobile hold intact.

R410: paired-read candidate566 parked. Atomic movie control56.85Hz/CPU17.4128ms versus candidate57.1667Hz/17.3134ms, p99 slightly worse; sub-percent difference not promotion evidence. Both Fair thermal snapshots/dropped0/EFB0/clean native-only exits/savea574 unchanged, no long historical hitch reproduced. No reverse/gameplay runs for this marginal result; prepared gameplay fixtures remain unrun. Next inspect clock/window tooling for correctly aligned, storage-bounded scheduler evidence of historical low-CPU hitches, addressing R232 disk-full/R307 polling ambiguity rather than unchanged probes. Normal app/defaults unchanged/no game/Simulator/full PRD and mobile hold intact.

R409: build29035 exit0/module audit passed. Unselected candidate5661634558290b6b2889805ab1c49966a12ce22f9b4228f92d949f2a511479e7; fresh controlc0021b9f exactly matches accepted. Independent hashes/provenance/unchanged flags verified; one expected profile mismatch recorded. Next R408 prepared movie profiles with explicit control/candidate module overrides/normal runner/VI-only/atomic helper; then fixedR409 railing gameplay regression if warranted. Suite5283 passed. Normal671729c6runner/1fb635f7module rehashed unchanged, no live handles/game/Simulator. Full PRD/performance/audio/mobile hold intact.

R408: isolated builder29035 live/control ld40732 (4m46/497.6%CPU), generated/build-s16-pair-r408.log and generated/s16-pair-r408. Currentc0021b9f graph pinned, only chunk1102 substituted,1329hashes/identical flags/one response difference verified. Candidate gated on unchanged control hash before compile/link; poll same handle, no restart. Suite5283 exit0/generated/check-r408.log. Prepared identical s16-pair-control/candidate-r408 movie profiles plus atomic helper; no launch before build/audit terminal. No normal app/marker/default change, no game/Simulator; full PRD/performance/audio/mobile hold intact.

R407: isolated checked4-byte signed16 pair passes278906helper cases perASan/O2 plus full1440-case kernel oracle/digest882be09b1f38e9ad; fixture matches currentfa455chunk/currentCPU05e221 both sides. Fullsuite84886 and benchmark32926 exit0. Saved-PGO strictFP/ThinLTO ABBA meanCPU~2.9528%less/text229376→212992; not FPS/gameplay evidence. Next isolated one-chunk builder/currentc0021b9f graph audit, then atomic movie and fixed-state gameplay regression; no normal app/default/source promotion. No game/Simulator/live handles; full PRD/performance/audio/mobile hold intact.

R406: current1fb635f7 module CPU profile completed/exported,31807samples/31772P-core; decoder kernels+coefficient chunk43.77%, kernel load-PC attribution77.15%. Exact-binary join confirms existing hot paths, not a performance fix. Runtime53384/capture47041/export26557 exit0/movie advancement/savea574 unchanged/fallback0/smc0; no game/Simulator. Next guarded four-byte mapping for two signed16 coefficient lanes, exact callback/alias/boundary oracle first; differs from parked per-lane S16 and eight-byte type0 load paths. No app/default/source change/full PRD and mobile hold intact.

R405: corrected atomic movie fixture completed100/50,56.933/56.817VIHz,CPU17.3906/17.3978ms, zero EFB in both60s windows. Interval50 parked: no overall gain; normal100 unchanged. R404 manual-anchor pair invalid (candidate crossed into gameplay), retained/excluded. All runtime/helper handles exit0/fallback0/smc0/savea574 unchanged; no game/Simulator. Next exact-current-module CPU profile after accepted two-range/store-scale changes, using corrected atomic trigger timing; no repeated submission/scheduling-only probes. Full original PRD/performance/audio/mobile hold open.

R403: fixed-state50/100 pair completed, identical three depth outcomes; mean read service~19.3% lower with50, CPU~.341% higher,59.933/59.9VIHz (no material cadence gain). Both retain non-EFB hitches; early control audio events do not prove a candidate fix. First untimed/overflowed control excluded; replacement timed automatically, all handles exit0/saves106e unchanged/fallback0/smc0. Evidence submit-comparison-r403.json. Normal671729c6runner/1fb635f7module/default100 unchanged; no game/Simulator,62GiB free. Next VI-only existing movie fixture100/50 comparison to bound CPU-heavy regression risk, no rebuild. Full PRD/performance/audio/mobile hold open.

R402: first isolated100/50 submission pair completed cleanly/save106e unchanged/fallback0/smc0. Both60s windows~59.95Hz/zero audio events;50 has~21%less service but~.94%more CPU. Different camera/depth state invalidates attribution; not promotion evidence. Next exact profile-r374 slot1 fixture/no movement/verified restored state comparison, not unchanged wall-clock movement pair. Evidence submit-comparison-r402.json. Normal default100/app unchanged/no game/Simulator; full PRD/mobile hold open.

R401: stage runtime50873 exit0/real-save load+movement+cleanclose/save106e unchanged/fallback0/smc0.21519matched reads; ~92.71% measured time inside framebuffer service. Slowest11.078ms=.001dispatch+11.071service+.006resume, not queue delay. Previous40ms outlier absent. Existing early command-buffer submission default is100draws; next isolated100/50 profile comparison to test overlap without skipping depth or changing guest time. Normal app/default unchanged, no runtime/Simulator; full PRD/mobile hold remains.

R400: depth-stage overlay integrated; initial/repeat bootstrap and exact layered-source/context/stage tests pass. Separate build36535 exit0/private audit passed, runner52104227...0528b in generated/macos/efb-dispatch-r400 with provenance. Normal app671729c6 unchanged. Full suite15593 exited0/generated/check-r400.log. Next stage-resolved real-save diagnostic. No game/Simulator/mobile work; full PRD/performance hold remains.

R399: existing R39839.98ms depth read lies near91.73ms wall/18.55ms CPU frame; queue/service/resume split missing. Prepared unapplied opt-in depth-dispatch timing patch5226881b...b638. Actual patched-header ASan/UBSan/O2 sync/future/float-bit/order/opt-out/reversal tests pass; full suite66819 exited0/generated/check-r399.log. Next reproducible integration/separate diagnostic build/one stage-resolved run. No runtime/app changes/no game; full PRD/performance/mobile hold remains.

R398: corrected EFB context verified live:16896reads allPC804ba23c (actual lwz), two LR values follow exact calls to804ba228, zero unattributed. Real-save title→Observatory/movement/cleanexit39668 passed, save106e unchanged/fallback0/smc0. Evidence generated/runtime/efb-context-r398/caller-verification.json. No performance-fix claim: whole-run4underruns/7backlogs and intermittent waits remain. Normal app unchanged/no game/Simulator; full PRD/mobile hold open. Next discriminate wait stages using existing trace/caller evidence, not another unchanged reproduction.

R397: live-AOT context patch integrated; initial/repeat bootstrap and exact original/patched context tests pass. Separate build34215 exit0/private audit passed; runner09353ce1...93f74b in generated/macos/efb-context-r397 with provenance. Normal app671729c6 unchanged. Full suite81870 exited0/generated/check-r397.log. Next real-save route to verify actual memory-read caller PCs. No runtime/Simulator/mobile work; full PRD/performance hold open.

R396: prepared unapplied live-AOT EFB context patch4d5782fa...b775. Scoped opt-in PC/LR in both external-read hooks; EFB color/depth use scope, zero when unattributed. Focused ASan/UBSan/O2/two-TU/nesting/exception/thread/opt-out and exact patch apply/reverse tests pass. Full suite53488 exited0/generated/check-r396.log. Next reproducible bootstrap integration then isolated diagnostic build/caller verification; runtime source/normal app unchanged (runner671729c6 rehashed), no game/Simulator. Full PRD/performance/mobile hold open.

R395: existing per-read EFB trace on same loading route runs60.0VIHz/oneunderrun, not prior45.4Hz/39; slowdown intermittent. Pointer482,378 dominates measured reads. Found stale AOT caller attribution: EFB trace takes mirrored PPC PC/LR, while HookExternalRead only propagates MSR; common PC804a3c9c is mfmsr, not memory read. Next scoped live-AOT diagnostic context with nesting/opt-out tests, no emulated-state mutation. Runtime30022/load95565 exit0/visible Observatory/save106e unchanged/fallback0/smc0; no game/Simulator, normal app unchanged. Full PRD/mobile hold remains.

R394: existing R393 trace localizes39underruns to15s after file-load confirmation:45.4VIHz/24.218kHz guest audio, meanCPU14.715ms/EFB6.268ms vs quiet Observatory EFB.478ms. Separate isolated stall has different CPU/wakeup pattern. EFB timer spans CPU future/video/Metal completion—not GPU execution alone. Evidence cluster-analysis-r394.json/transition-window-r394.json. Next existing per-read EFB trace on loading route to identify exact slow callers/coordinates; no shortcut or unchanged quiet-window replay. No new run/build/app change/no Simulator; full PRD/mobile hold intact.

R393: event-capable diagnostic runtime24713 exit0, real-save title→Observatory/movement/clean close, save106e unchanged/fallback0/smc0. Fixed60s59.933333VIHz/CPU15.611282ms/p99wall18.554708ms; exact zero window underruns/backlogs/full drops. Whole47underruns are44before/3after; counts match event trace, ordinals complete/VI dropped0. Evidence generated/runtime/audio-events-r393. One quiet diagnostic window is not stutter/audio acceptance; next classify recorded event clusters without repeating unchanged probes. Normal app unchanged, no game/Simulator; sustained movie CPU deficit/full PRD/mobile hold still open.

R392: exact opt-in audio-event patch wired into reproducible bootstrap; initial/repeat bootstrap and focused original/patched-header tests pass. Separate diagnostic build92997 and full suite80674 completed exit0; private package audit passed. Header9c11e94e...f772b/runnerfa9adfa5...14102 provenance recorded in generated/macos/audio-events-r392/provenance.json. Normal app/buffering unchanged. Next bounded event-resolved real-save recording with phase plus VI diagnostics, then correlate exact underruns with CPU/wall intervals; old event-less traces cannot establish zero underruns. No runtime smoke yet for diagnostic app. Cleanup already complete: Devices492MiB/no booted Simulator/64GiB free. Full PRD/performance/audio/mobile hold remains.

R390: postpromotion suite45970 exit0. Installed app no-override/no diagnostics smoke2377 passes bundledmodule load/title→real106esave→Observatory/movement/cleanexit; fallback0/smc0/saveunchanged. No game/Simulator. Store-scale optimization fully incorporated, but whole-run9underruns/10backlogs and movie<60Hz keep performance/audio/full PRD open. Next examine separate quantized-load factor path with new exact oracle; mobile hold remains.

R389: canonical build53203 exit0/modulec0021b9f byte-identical to runtime-tested candidate, absolute-path audit passes, cache-hit34932 exit0. Explicit marker selection and module-only promotion22590 exit0/private package audit pass. Normalrunner671729c6 unchanged; signedmodule now1fb635f7...1dc7a, rollback GalaxyPad.app.previous.20260907T210556Z retained. Postpromotion suite running generated/check-promoted-scale-r389.log; next no-override installed-package smoke. No game/Simulator. Approx1%movie gain integrated, full PRD/performance/audio/mobile hold remains open.

R388: same canonical build53203 compilation reached1330/1332, final ld16924 active (713.6%CPU). Continue same handle; no restart. Normalrunner671729c6 unchanged/no game/Simulator/marker selection. Next terminal audit/manifest and comparison to c0021b9f testedcandidate, then cache-hit proof before module-only packaging. Full PRD/performance/mobile hold remains.

R387: integrated fullkernel oracle25874 exit0/all1440case digests match882be09b1f38e9ad; R386suitepassed. Canonical separate-output build53203 live at426/1332, generated/modules-scale-r387 cachec4cbfba1bd04990b. Entire generated source tree identical to acceptedR366; headerda2def/chunkfa455verified, only CPU helper source changed. Poll same53203 through link/audit then compare isolatedc0021b9f candidate before promotion. No game/Simulator/app/normalmarker change; full PRD/performance/mobile hold remains.

R386 checkpoint: integrated fullsuite53768 exit0/repository safety passes. Whole-kernel oracle25874 still live; continue same handle before canonical build. Installed app unchanged.

R386: canonical0022scale overlay bootstrapped twice (11518/79734exit0), actual CPU source05e221c0 exactly testedcandidate. Historical oracle tests recover/compile byte-exact1350d119 from two known hashes, reject unknown sources. Suite53768 and fullkernel oracle25874 running; poll same handles before canonical separate-output build. No runtime/Simulator/app/marker change; original full PRD/G6/performance/audio/mobile hold remains.

R385: gameplay control59.95Hz/CPU15.659910ms/p99wall17.69525ms versus candidate59.95Hz/15.669610ms/18.299375ms. No material mean/cadence regression (~0.062%CPU delta), not better-tail claim. Cleanexit84607/fallback0/smc0/save106eunchanged, no runtime/Simulator. Prepared unapplied0022-psq-store-scale.patch SHA74ca7e8...7486 and exact apply/reverse/reapplication regression passes; suite running generated/check-r385.log. Next canonical bootstrap wiring and exact historical-oracle preservation, then isolated reproducible build/audit/byte comparison before promotion. Installed app/marker unchanged/full PRD/mobile hold intact.

R384: candidate real-save Observatory/movement/nativepause/resume/postresume movement/cleanexit66186 pass bounded checks, save106eunchanged/fallback0/smc0. Fixed60s59.95Hz/CPU15.669610ms/p99wall18.299375ms, invalid0/reset0. Late328dropped samples occur after full retained window (last retained92s beyond end); not whole-run trace/audio/soak acceptance. No game/Simulator/app change. Prepared psq-scale-gameplay-control-r384 with same106esave/no states; next matched control gameplay timing before canonical integration. Full PRD/performance-first mobile hold intact.

R383: reverse movie pair confirms modest scale gain: candidate56.85Hz/CPU17.390126ms versus control56.416667Hz/17.542846ms (~0.768%cadence/0.871%CPU). Both orders favor candidate; combined ~1.036%cadence gain, not60Hz/audio acceptance. Both dropped0/invalid0/reset0, clean exits16203/84818, savea574unchanged/fallback0/smc0. No runtime/build/Simulator. Prepared psq-scale-gameplay-r383 with real106e...2c90save/no states/independent pipe. Next gameplay/lifecycle and timing regression, no third movie pair or promotion yet. Normalapp/module unchanged/full PRD/mobile hold intact.

R382: build35607 exit0/audit passed, unselected scale candidatec0021b9f...c7939. First matched movie pair control56.233333Hz/CPU17.578963ms versus candidate56.966667Hz/CPU17.378906ms (~1.304%cadence gain/1.138%less CPU); both dropped0/invalid0/reset0, visible movie advance, clean exits18728/47851, unchanged savea574/fallback0/smc0. No runtime/Simulator/build remains. Next reverse candidate→control pair, then gameplay regression if confirmed; no installed app/marker change. Full PRD/G6/performance/audio/mobile hold intact.

R381 checkpoint: fullsuite80439 exit0/repository safety passed. Same build35607 still live, ld7796 verified688.6%CPU at2m51; continue same handle, do not restart quiet link. No game/Simulator/candidate selection.

R381: whole-kernel timing19629 exit0, savedPGO CPU ABBA mean25068.8555ns control versus24531.9505candidate (~2.1417%lower), same text size. Isolated --psq-scale module build35607 live at candidate link; unchanged control549988 reused after full graph/1329object/compiler/link equality gates. Candidate CPU source only, compile flags identical, expected1of51PGO mismatch. Fullsuite80439 running. Poll same handles before runtime. Prepared matching psq-scale-{control,candidate}-r381 profiles (slot3aea2...b7ab8/savea574...afa6/Metal1x/separate pipes). No game/Simulator/app selection; full PRD/G6/performance-first mobile hold intact.

R380: exact quantized-store power-of-two factor candidate is offline/unselected. Actual-quantizer672816cases pass in sanitized/O2 builds (rounding/flags/errno), full-kernel oracle86386 exit0/all1440cases match882be09b1f38e9ad, fullsuite29380 exit0. No normal app/module change. SavedPGO whole-kernel CPU timing running generated/psq-scale-kernel-bench-r380.log; poll same handle, no runtime/build/test overlap. Microbenchmark gain alone is insufficient. Full PRD/G6/performance-first mobile hold intact.

R379: authorized other-project Simulator cleanup remains complete (Devices492MiB, all shutdown,66GiB available); no further deletion needed. Dead-PC candidate movie comparison completed: control56.366667VIHz/17.560408ms CPU versus candidate56.45VIHz/17.513327ms CPU, only0.148% cadence and0.268% CPU improvement in one sequential pair. Too small for promotion; park candidate pending materially new evidence, no unchanged reverse-pair loop. Candidate fresh capture retry-r379 has dropped0/invalid0/reset0, advancing movie, clean exit28080/fallback0/smc_failed0/save unchanged. Prior candidate17940 closed cleanly but exceeded recorder capacity (3606dropped) before trigger; excluded, preserved. No game/Simulator/build remains; installed app unchanged. Next investigate a larger measured guest-CPU cost with a falsifiable source hypothesis, not more sub-percent PC-store timing. Full PRD/performance-first mobile hold intact.

R377: SAME build63125 passed unchanged-control relink, exact5499889a558e44197bb740b3b3c5cc96187bcd80e3a8df097b814cb2703692e1. One changed chunk compiled (expected1of33PGO mismatch); candidate link now live. No restart/app selection. Prepared identical dead-pc-movie-{control,candidate}-r377 profiles with slot3aea2...b7ab8/savea574...afa6/Metal1x and separate pipes; no game/Simulator. Poll63125 to terminal audit before any runtime. FullsuiteR376passed/current app unchanged/performance-mobile hold intact.

R376 checkpoint: fullsuite18256 exit0/repository safety passed. Build63125 still live at unchanged-control relink (verified ld4515 active); no restart/candidate/app promotion. Poll same handle until terminal, then control hash gate/candidate compile/link/audit. No game/Simulator.

R376: all95dead-PC sites pass direct-entry oracle26201 in sanitized/optimized builds:194560cases/48640FPfaults/145920next-PC observers each, fullstate/return/hostflags identical. New --dead-pc isolated builder uses current549988module/da2defheader, requires exact unchanged control relink before one-chunk candidate. Build63125 running generated/build-dead-pc-r376.log; suite18256 running generated/check-r376.log. Poll same handles, no app/marker change or runtime/Simulator. Next module audit then runtime regression only if build valid; full performance/mobile hold remains.

R375 suite completion:56374 exit0/repository safety passed. All handles terminal/no game/Simulator. Next direct-entry oracle for95dead-PC sites, then assess actual module experiment; no app change.

R375 timing completion:56789 exit0, CPU-time ABBA control25072.758/candidate24912.310ns (~0.640%lower). Tiny offline result only; no module build/selection. Need exhaustive changed-site direct-entry/fault/observer coverage before deciding full-module test. Fullsuite56374 running generated/check-r375.log after benchmark; all other handles terminal/no game/Simulator. Normal app671729c6/module75db unchanged; full performance/mobile hold intact.

R375: isolated95site guarded dead-PC store experiment passes full-kernel sanitized/optimized oracle68724 (1440cases,digest882be09b1f38e9ad) and exact-scope regression. Only arithmetic PC writes whose adjacent successor rematerializes PC; unavailable-FP path keeps original PC before helper. No generated module/app change. SavedPGO strictFP CPU-time ABBA56789 running generated/dead-pc-bench-r375.log; keep other tests/builds idle, poll same handle, then suite. No runtime/Simulator/full-goal claim; performance/mobile hold unchanged.

R374: fresh-profile directory/save-state fix accepted and normal app promoted. Started without StateSaves; candidate created it automatically. Title→real-save Observatory→save slot1→visible movement→load slot1 restores original position/camera→movement works→cleanexit24399. Slot4a4217264a1968fc6b93fce8fb213eb9e50af1aaebf378cd2f14be9c28f15edb (39042803bytes), NAND106e...2c90 unchanged; fallback0/smc_failed0. Audited promotion88449 exit0, normal runner now671729c6...d762/module75db...323c; rollback generated/macos/GalaxyPad.app.previous.r374 retained. No game/Simulator. R373 fullsuite remains applicable. Next return to movie CPU hotspot work; stop unchanged intermittent-tail diagnostics. Performance/audio/full PRD/mobile hold remain open.

R373 completion: candidate build77238, app audit90150 and post-bootstrap suite9513 all exit0. Candidate runner671729c6bb32e29ec44e95dedae0044c9c3d7e64f99736653f3146d806d3d762, same signed module75db...323c. Candidate generated/macos/profile-r373/GalaxyPad.app remains unselected; no game/Simulator. Next fresh profile without StateSaves, launch candidate, verify directory automatically created, save/load slot visibly and clean close. Normal app untouched/performance-mobile hold unchanged.

R373: fixed missing standard UICommon::CreateDirectories between SetUserDirectory and Init under runtime-owned profile guard, canonical0026 SHAeae4e6...eb6a2. Structural regression fails old/passes patched, bootstrap68699/repeat78871 exit0. Separate candidate build77238 running generated/build-profile-r373.log (199steps), normal app unchanged. Initial suite raced temporary bootstrap peel; corrected source verified and suite9513 running generated/check-after-bootstrap-r373.log after bootstrap. Poll same handles then fresh-profile actual state save/load. No runtime/Simulator, no performance or persistence acceptance yet; mobile hold intact.

R372: no-UI120s diagnostic completed/clean SIGTERM handler exit0. Window392973275282125..393093275282125:59.941667VIHz, CPUmean15.6335ms, wallp9917.739959ms, DMA32000/callback48000frames/s. Still90.357ms VI at+35.49s with19.776msCPU/3.520msEFB/0.379msidle/0DVD/gather/0.028mswakeup. UI capture not necessary; remaining elapsed time unclassified, not proven scheduler fault. Audio endpoints straddle window (last+143.72s around shutdown), so no zero-underrun claim. All handles78769/81888/82589 exit0, dropped/invalid/reset0, save106e...2c90 unchanged/fallback0/smc0, no game/Simulator. Stop unchanged tail-observation loops. Next fix known fresh-profile StateSaves creation defect (UICommon creates it; runtime profile setup needs audit) then return to measured movie CPU work; performance/mobile hold remains.

R371: combined diagnostic complete, runtime64924/load47655/controls59770 exit0, no game/Simulator. Fixed60s392486715612083..392546715612083:3597VI59.95Hz,CPUmean15.6748ms,p99wall18.2077ms; dropped/invalid/reset0. Last underrun at+78.10s outside fixed window overlaps84.773ms VI/20.071ms CPU/48.486ms idle FlushGpu elapsed, EFB0.613ms/DVD0/gather0/wakeup0.031ms. Confirms wait-heavy audio incident, not CPU execution alone or proven GPU/scheduler fault. End-of-run UI observation is a confound. No third unchanged wait/phase capture: next test observer contribution with no UI queries/capture in or after measurement before signal-based clean shutdown. Correlation evidence generated/runtime/audio-cpu-r371/correlation.json. Save106e...2c90 unchanged/fallback0/smc0; normal app unchanged/full PRD/mobile hold intact.

R370: diagnostic no-pause trace localizes last underrun to active Observatory window+19.4s. 60s392072117502541..392132117502541:3596VI,14998DMA granules (~31995.7frames/s), callbacks48000frames/s. At+19.30s DMA gap69.36ms and VI gap89.06ms drain queue24→6→2; callbacks remain regular (window max11.38ms). Not purely startup/pause; mean production near target does not prevent transient starvation. Trace overhead means not acceptance or definitive host-vs-guest attribution. Runtime4592/load39486/controls62098 exit0/native2778999045/fallback0/smc0/save106e...2c90 unchanged. Evidence audio-active-r370 phase.csv/window-summary.json/stall-summary.txt. No game/Simulator. Next correlate VI CPU-time and wall-time tails with audio events using existing diagnostic recorder; no buffer-policy change from this trace alone. Full PRD/mobile hold intact.

R369: normal packaged app audit and real-save smoke pass. Runtime14607 exits0 after title→one-star Observatory→visible movement→native pause/resume→visible movement→clean close. Log proves bundled module75db...323c, no override; native2498717729/fallback0/smc_failed0. Save106e...2c90 unchanged. Private evidence generated/runtime/package-r369 including screenshot. No game/Simulator. Aggregate182s includes18s pause and startup/transitions: four underruns/seven backlog corrections are not uninterrupted performance/audio acceptance. Next uninterrupted gameplay/audio measurement using selected normal app, isolate steady active interval from startup/pause; heavy movie56Hz remains open. Full PRD and mobile hold unchanged.

R368 completion: suite53489 exits0/repository safety passes (generated/check-r368.log). All handles terminal; no game/Simulator. Next fresh normal-package real-save gameplay smoke with STATICRECOMP_MODULE unset to verify bundled selection. No performance or full-goal acceptance claim.

R368: cleanup reverified: CoreSimulator Devices492MiB, all devices shutdown,66GiB available; R283 already erased other-project simulator app/save data, so no repeated deletion. Post-selection R367 suite24309 actually exited1: test-huffman-tail.py pinned only the old generated header. Added the exact audited two-range header identity alongside the old identity; unknown headers still refuse. Focused65038 exits0,128000 state/memory/event comparisons in each sanitized/optimized build. Full suite53489 running generated/check-r368.log. No product changes/game/Simulator. Next finish suite, then fresh normal-package real-save smoke; G6 performance/audio and mobile hold remain.

R367: canonical build52431 exit0, module audit passes and binary byte-identical to tested5499889a558e44197bb740b3b3c5cc96187bcd80e3a8df097b814cb2703692e1. Cache-hit83592 exit0. Strengthened new-policy header/normalized-header audit +9case test passes; suite71019 exit0. Selected canonical module and module-only package71372 exit0/auditpasses. New signed module75db109bdfb1a1b096eed361c20e0e36443b0e31d5296600a305ce25a2e2323c; runner/frontend/wrapper unchanged. Rollback GalaxyPad.app.previous.20260907T182801Z and marker backup in two-range-integration-r365. Post-selection suite24309 running generated/check-r367-selected.log. NEXT fresh normal-package real-save smoke before claiming installed-runtime acceptance. No game/Simulator; full PRD/G6/performance/audio/mobile hold unchanged.

R366 checkpoint: SAME52431 still live, compile reached1330/1332 and verified linker93238 active18s/~664%CPU. Poll52431 through link; no restart or app promotion. All tests terminal; no game/Simulator.

R366: canonical module build52431 running generated/build-module-r366.log, separate modules-two-range-r366 cache suffixede0bf4e2d66a29f. Preflightpasses, new RMGE01.h and normalized generated.h byte-identical to tested R358 header SHAda2def2ce566f57929afe0a8a2f7de5539b17624eb37452d6928790ac6999336; all chunk sources unchanged. Original savedPGO/ThinLTO/O2/strictFP flags verified. Suite89152 exit0/repository safety passes. Poll SAME52431 through compile/link, then manifest/audit/binary comparison. Normal active marker/app unchanged, no game/Simulator; full PRD/G6/mobile hold.

R365 completion: port build45774 exit0, SHA69d41668bf3a234f0380c1f530c325f49e01435b965f7209bbbcc211d5e85d7f; suite64927 exit0/repository safety passes generated/check-r365.log. All handles terminal/no runtime. Next separate-output canonical module build with savedPGO using new port; normal app/active marker still unchanged.

R365: two-range port/cache/manifest/header-copy wiring integrated via pinned ModernGekko0025 SHA1a8378...69bc. Initial bootstrap90207 refused missing scope inventory; corrected42385 and repeat15649 exit0. Wiring regression now covers scope registration. Build-tool45774 running generated/build-port-r365.log (199 dependency steps after bootstrap); suite64927 running generated/check-r365.log. Poll same handles. No app/module marker change, no game/Simulator. Next canonical module build in separate output with savedPGO, verify generated header and module before package/selection. Full PRD/G6/mobile hold intact.

R364 completion: suite15683 exit0/repository safety passes generated/check-r364.log. All handles terminal/no game/Simulator. Proposed canonical policy verified; port/bootstrap/cache wiring remains next, not yet installed.

R364: proposed compiled C++ two-range policy exactly matches runtime-tested R358 header. ASan/UBSan test48682 exit0 covers exact disc/DOL/backend/chunk/indexed eligibility, missing/changed hash refusal before writes, malformed boundaries and reapplication rejection. Added policy/test/full-suite entry; NOT wired into port/bootstrap/cache yet. Next pinned overlay includes policy, key+manifest before cache lookup, applies before generated.h copy, with reverse/apply/recovery bootstrap tests. No vendor/module/app/marker change; full PRD/G6/mobile hold intact. Suite running generated/check-r364.log.

R363 completion: suite54374 exit0/repository safety passes generated/check-r363.log. All handles terminal/no game/Simulator. Canonical reproducible two-range integration next; normal app unchanged.

R363: candidate new in-game save→title→cleanexit→fresh-process load→playable Observatory passes. Save changed5040...64a6→106e8248bd8081404e8258a7ca33c54e0d476d651f139fde5ee2e4aad7302c90, game confirmed saved, reload hash unchanged. Runtime86776/72217 exit0/fallback0/smc_failed0; no game/Simulator. Corrected Plus fixture0.15→0.4s after source12-frame hold requirement; in-game menu works. Next canonical reproducible two-range build integration then package audit/runtime verification, not further unchanged benchmarks. Candidate still unselected; full PRD/G6/performance/audio/mobile hold unchanged. Suite running generated/check-r363.log.

R362 completion: suite21713 exited0/repository safety passes generated/check-r362.log. All handles terminal/no game or booted Simulator. Next new in-game save/relaunch with candidate (use private R361 progression or fresh real-save copy); emulator checkpoint alone is not persistence proof.

R362: candidate movie56.4Hz/CPU17.550668613ms/p9919.409917 versus control56.333333Hz/17.572339819ms/p9919.604875. Negligible difference/no meaningful regression in this pair, NOT60Hz/audio acceptance. Both movie visibly runs/cleanexit/savea574...afa6 unchanged/fallback0/smc_failed0/dropped0/invalid-reset0. All runtime/recorder handles terminal, no game/Simulator. Candidate549988...692e1 remains unselected; next in-game save/relaunch regression, no more unchanged movie pairs. Suite running generated/check-r362.log; full PRD/G6/mobile hold intact.

R361 completion: suite27830 exited0/repository safety passes generated/check-r361.log. All runtime/input/test handles terminal, no game/Simulator. Candidate remains unselected; movie and in-game save/relaunch regression next.

R361: candidate549988...692e1 real-save title→file select→Observatory→Terrace interior→Pull Star→galaxy-selection tutorial visibly works. Movement after native pause/resume verified; subtitle updates correctly. Runtime62035 exit0/native9079459951/fallback0/smc_failed0/save5040...64a6 unchanged. ~651s functional session includes pause/VI dropped21667: NOT timing/audio/soak acceptance. Private slot5f3368150bfc401ed2758ebf39a86995b93d055aac6bbcfb8fc2c6fcbef1e244d preserves galaxy-selection tutorial (reload untested). No game/Simulator/app promotion. Next candidate movie regression and in-game save/relaunch before integration; full PRD/G6/mobile hold intact. Suite running generated/check-r361.log.

R360 completion: suite7723 exit0/repository safety passes generated/check-r360.log. All handles terminal. Prepared dispatch-gameplay-r361 with Config/Wii/config.ini from R352 and neutral pipe, no savestates; save5040...64a6 verified. Next candidate real-save title/file-select→Observatory gameplay/transition/save-relaunch, not more fixed timing pairs. No runtime/Simulator/app promotion.

R360: reverse pair candidate59.933333Hz/CPU15.617004961ms/p9918.887875 versus control59.95Hz/15.718986385ms/p9919.043083. Both orders favor small meanCPU saving (~0.68%combined), not large FPS/stability proof. Fresh identical checkpoint, all runtime/recorder handles exit0/save unchanged/fallback0/smc_failed0/dropped0/invalid-reset0. No game/Simulator. Stop unchanged timing pairs; next candidate549988...692e1 real-save gameplay/transition/save-relaunch and movie regression before integration/selection. Suite running generated/check-r360.log. Full PRD/G6/mobile hold unchanged.

R359 completion: suite38398 exited0/repository safety passes generated/check-r359.log. Both VI recorders dropped0. All build/test/runtime/recorder handles terminal; no game or booted Simulator. Next reverse-order fixed gameplay comparison; candidate remains unselected.

R359: R358 build3365 exit0/auditpasses candidate549988...692e1,114404424bytes, unselected. Fixed identical railing first pair control59.916667Hz/CPU15.738210119ms/p9918.612458 versus candidate59.933333Hz/15.624909539ms/p9917.786167. Both cleanexit/save5040...64a6 unchanged/fallback0/smc_failed0/invalid-reset0. Small first-pair benefit (~0.72%CPU) not promotion proof. Next fresh reverse-order candidate/control fixed60s pair; no unchanged third pair. No game/Simulator; full PRD/G6/mobile hold unchanged. Suite running generated/check-r359.log; poll returned handle.

R358 checkpoint: regression suite31239 exited0/repository safety passes generated/check-r358.log. Build3365 still live; verified linker78672 at2m28s/~670%CPU. Poll SAME3365; no restart. No game/Simulator/app promotion. Cleanup remains complete.

R358: isolated --two-range module-export-object build3365 running generated/build-two-range-r358.log. Original export source path and savedPGO/ThinLTO flags retained; private header override only. Accepted control reuse requires exact compiler/graph/all1329objects/link response match. No app/marker selection. R357 suite54084 exited0/repository safety passes. Next poll SAME3365 through link/audit, then fixed gameplay validation. Full PRD/G6/mobile hold unchanged.

R357: cleanup verified already complete: Simulator Devices492MiB, no booted devices,69GiB available. No further erasure necessary. Recovered complete dispatcher benchmark log; all four ABBA runs finish with expected hit counts. Synthetic virtual dispatch12.146→6.674ns and hot host-declined5.080→3.994ns; NOT FPS evidence. One changed function loses incompatible saved PGO data (compiler warning). Actual module/app unchanged. Regression suite54084 running generated/check-r357.log; poll same handle. Next isolated actual-module build then fixed-gameplay validation, keeping macOS performance first and full PRD/mobile hold.

R356: complete actual dispatcher wrapper oracle passes27648cases/buildASanUBSan/O2, fullCPU/result/ordered callback snapshots. Covers host/replacement handling,physical aliases,holes/alignment,bounds,mutatedPC/RAMsize/exception/callback pointer. Uses actualCPUState/ppc_host_call with observable chunk stubs; not game/timing acceptance. Suite90885 exit0/repository safety passes generated/check-r356.log. All handles terminal. Next savedPGO/ThinLTO full-dispatch benchmark with opaque addresses before module work. No runtime/app promotion; fullPRD/G6/mobile hold unchanged.

R355: source-pinned two-range lookup prototype passes6435854comparisons/1352457hits and1322chunk identities inASanUBSan/O2. Uses exact accepted tables, every byte of supported span+hole/alignment/boundary/random probes. All wrapper/callback/alias code byte-identical; no timing claim. Suite89877 exit0/repository safety passes generated/check-r355.log. All handles terminal. Next full-wrapper semantics and savedPGO/ThinLTO dispatch timing before module work. No game/Simulator/app promotion; fullPRD/G6/mobile hold unchanged.

R354: accepted fixed-gameplay CPU profile78034/export83466 exit0,29459CPU samples. Run3391+chassis_dispatch2184 (~18.92%); THP kernels absent. Exact dispatcher sample→assembly join identifies metadata/function-table loads; generated lookup has only two ranges. Next source-pinned two-range lookup prototype with exhaustive pointer/alignment/hole tests and unchanged callbacks/alias/timing, before benchmarking. Runtime72375 cleanexit/save unchanged/fallback0/smc0; no game/Simulator. Suite65661 exit0/repository safety passes generated/check-r354.log. All handles terminal/fullPRD/G6/mobile hold unchanged.

R353: fixed identical railing checkpoint/no input control58.35Hz/CPU16.21918581ms vs candidate55.066667Hz/17.34333067ms. All handles cleanexit/save5040...64a6 unchanged/fallback0/smc0/dropped0; same position/camera. Host/order effects not excluded, but gameplay benefit unproven. PARK signed16d379ff...16a6; no promotion/canonical integration or more unchanged timing pairs. Next accepted fixed-gameplay CPU profile (reuse existing evidence first), target gameplay bottleneck rather than movie-only helper gains. Suite79144 exit0/repository safety passes generated/check-r353.log. All handles terminal/no game/Simulator; fullPRD/G6/mobile hold unchanged.

R352: fixed Observatory railing fixture created from accepted module/real save, slot4 SHA406a1cd20209e00852ad3d9a3450e6869c33cdd9a9b8e9dda2abb3d8a1f30e09,38949741bytes, generated/runtime/observatory-fixed-r352/StateSaves/RMGE01.s04. Reload verified same hanging position/camera; clean exit/save unchanged/fallback0/smc0. Initial missingStateSaves directory fixed for disposable profile. Next exact-slot4 neutral/no-movement control/candidate60s timing to remove route drift. Suite87711 exit0/repository safety passes generated/check-r352.log. All handles terminal/no game/Simulator; candidate unselected/fullPRD/mobile hold.

R351: fresh real-save control58.583333Hz/CPU15.48811081ms vs candidate56.1Hz/16.60129596ms. Clean exits/save5040...64a6 unchanged/fallback0/smc0; controlinvalid/reset/dropped0. Ending player states differ (control hanging/candidate standing near railing), so regression warning not isolated cause. Candidate promotion withheld. Next fixed gameplay savestate/no movement matched comparison to remove route drift; no repeated moving-route timing loops. Suite93992 exit0/repository safety passes generated/check-r351.log. All handles terminal/no Simulator; fullPRD/mobile hold.

R350: candidate real-save title→file select→one-star Observatory works;8movement/jump/Spin cycles issued, visible position change.60s3366VI56.1Hz,CPU16.60129596ms,p9922.181292; not performance acceptance. Clean exit/save5040...64a6 unchanged/fallback0/smc0. Next fresh accepted-control identical real-save route to distinguish candidate regression from scene/host variability; historicalR28959.9Hz not matched. Transition/newsave/relaunch not yet proven. Suite42059 exit0/repository safety passes generated/check-r350.log. All handles terminal/no game/Simulator; candidate unselected/fullPRD/mobile hold.

R349: reverse pair candidate53.033333Hz/CPU18.65572827ms vs control50.4Hz/19.65344951ms. All four runtime/recorder handles exit0; visible movie, saves unchanged,fallback0/smc0/dropped0. Both orders favor candidate; combined52.5vs49.975Hz (~5.05%). Retain d379ff...16a6 unselected for broader real-save Observatory gameplay/transition/save/relaunch regression, not more unchanged movie pairs. No60Hz/audio/G6 acceptance or app promotion. Suite92313 exit0/repository safety passes generated/check-r349.log. All handles terminal/no game/Simulator; full PRD/mobile hold unchanged.

R348: first signed16 runtime pair complete. Candidate33722/top67538 exit0,3118VI/60s51.966667Hz,CPU19.05844075ms,p9922.347708 vs control49.55Hz/19.9890582ms. Both visible movie/cleanexit/save unchanged/fallback0/smc0. Evidence s16-candidate-r346; first-pair gain not promotion proof. Next fresh reverse-order candidate/control to test order/host variability; no third unchanged pair. Suite79459 exit0/repository safety passes generated/check-r348.log. All handles terminal/no runtime/Simulator; installed app unchanged/full PRD/G6/mobile hold.

R347: build71954 exit0/module audit passes; candidate d379ff0b40dffdce5e4df0b3345641838cacfbbeaf2307da655960e431e916a6 (114404600bytes), unselected. Control22962/top4964 completed0, castle→movie/cleanclose/save unchanged/fallback0/smc0. Fixed60s2973VI49.55Hz,CPU19.9890582ms,p9923.381083,invalid/reset0. Evidence generated/runtime/s16-control-r346. Next candidate run using prepared s16-candidate-r346 and same fixed60s trigger; no gain claim from control only. All handles terminal/no game/Simulator. Full PRD/G6/mobile hold unchanged.

R346: isolated --s16-load module build71954 active generated/build-s16-r346.log; verified control reused, flags unchanged, one chunk replacement. Latest ld68620 live~669%CPU. Poll SAME71954 through link/audit; no restart or promotion. Suite43483 exit0/repository safety passes. Prepared matching disposable s16-control-r346/s16-candidate-r346 profiles, slot3aea2...b7ab8/savea574...afa6,Metal1x. No game/booted Simulator. Next candidate audit then sequential matched runtime comparison. Full PRD/G6/mobile hold unchanged.

R345: complete-kernel signed16 specialization passes all four1440case builds/digest882be09b1f38e9ad,4840actual fast hits/build. Exactly16calls changed, remaining decoder byte-identical. Suite7236 exit0/repository safety passes. Benchmark29219 exit0: savedPGO/ThinLTO CPU-time ABBA2.1553%lower, __TEXT-16KiB. Offline only, no in-game speed claim/app promotion. Next isolated single-object module build using existing verified builder/control graph, then audit and matched runtime comparison. All handles terminal. Full PRD/G6/mobile hold unchanged.

R344: isolated signed16 scale-zero paired-load helper preserves sequential reads/original CPU callback state and generic fallback.278528cases/build pass sanitized/O2 including exhaustive operands, four rounding modes, all type/scale/indexed/W/LSQE callback combinations. Suite79933 exit0/repository safety passes generated/check-r344.log. All handles terminal. Next source-pinned full-kernel coverage then savedPGO/ThinLTO timing; no speedup/module/app claim. Full PRD/G6/mobile hold unchanged.

R343: local-state complete-kernel oracle passes all four builds1440cases/digest882be09b1f38e9ad,24actual candidate hits/build. Fixed unique charged-entry targeting after initial assertion failure; outer dispatcher/kernel1 unchanged. Suite88787 exit0/repository safety passes. Benchmark29485 exit0: candidate3.074%slower, __TEXT+16KiB; parked, no module/app promotion or unchanged repeat. Next inspect exact first-pass helper/memory operations for removable work under proven mapped/disjoint guards, not another state-copy/layout variant. Cleanup complete: Devices492MiB/free71GiB/no booted Simulator. All handles terminal. Full PRD/G6/mobile hold unchanged.

R341: exact emitted first-pass oracle passes32comparisons/build. Fixed64-write assumption failed suite91688; diagnosed with24860: DC/quarter/half/regular emit64/112/80/64journal writes, including overwritten intermediates. Corrected suite75082 exit0/repository safety passes generated/check-r341-fixed.log. Seven yields, boundary read-ahead16coeff/8quant bytes, CPU/memory/event-digest/hostflags parity retained. No optimized candidate. Next guarded local-state first-pass with no-journal/direct-mapped/disjoint eligibility and original fallback; add candidate-hit/rejection coverage. No app/game/Simulator/mobile changes.

R340: first-pass contract audit finds final-column read-ahead: baseline coefficient span144bytes and quant264, not logical128/256. Original four backedge/yield points and callbacks remain mandatory. Exact-DOL audit passes generated/thp-boundaries-r340.json; THP-BOUNDARY-AUDIT.md updated. Next exact first-pass oracle80452750..80452970 with boundary callbacks/alias/yields before local-state candidate. No implementation/speed claim/app/module/runtime change; full PRD/mobile hold unchanged. Suite44061 exit0/repository safety passes generated/check-r340.log.

R339: accepted thermal-aligned movie3384VI=56.4Hz,CPU17.55391ms,p9518.52425,p9918.92521. All60contained1Hz thermal samples fair(1)/lowPower0; cannot explain earlier46.68Hz from category alone or exclude frequency changes. Runtime98806/probe17885 exit0/save unchanged/fallback0/smc_failed0/dropped0. No game/Simulator. Suite92934 exit0/repository safety passes generated/check-r339.log. Park unchanged thermal-only captures; next inspect exact THP transform reference for a whole-kernel fast-path contract with original observable-exit fallback, rather than helper micro-tweaks. Full PRD/G6/mobile hold unchanged.

R338: public thermal recorder added/tested20316 exit0. Three idle samples allfair(1),lowPower0, generated/thermal-state-r338.csv; no causal/frequency inference. powermetrics requires root; sudo -n unavailable/password required, no further privileged retry. New1Hz steady-clock probe is read-only with nominal/unsupported caveat. Suite32074 exit0/repository safety passes generated/check-r338.log. Next one accepted-module capture aligning thermal state with VI/CPU times; no NaN-outline repeat. No game/Simulator/app changes; full PRD/mobile hold unchanged.

R337: reverse pair terminal: candidate50.3333Hz/19.6809msCPU versus control46.6833Hz/21.2240msCPU. Opposite R336 result, both second runs slower; no reproducible NaN-outline benefit. PARK candidate56628... unselected, no third unchanged pair. Both save unchanged/exit0/fallback0/smc_failed0/dropped0. No game/Simulator. Suite24978 exit0/repository safety passes generated/check-r337.log. Next inspect available read-only CPU frequency/thermal telemetry to explain accepted control drift; pmset reports AC but no recorded CPU power status, not proof against throttling. Full PRD/performance-first mobile hold unchanged.

R336: build79138 terminal0/auditpasses candidate56628cf5...9fcf3b5,114883432bytes, unselected. Movie pair completed: control54.1333Hz/18.2742msCPU versus candidate48.7667Hz/20.2858msCPU. No improvement/promotion. Both exit0/save unchanged/fallback0/smc_failed0/dropped0. Runtime84433/42218 and timing76559/98926 terminal. No game/linker/Simulator. Next one reverse-order pair with fresh profiles to separate candidate regression from worsening host/run-order conditions; then park if no reproducible gain. Normal app/full PRD/mobile hold unchanged.

R335: verified wait on SAME build79138; ld59059 active at3m06s/~668%CPU, no failure/restart. Candidate final hash/audit still pending. Both prepared r335 profiles now verified identical stateaea2.../savea574..., native1/Metal/Core6/Cubeb; runner856b2e... verified. No game/Simulator or new product edits/tests; latest suite30810 exit0. Next poll79138 and only after terminal audit run sequential comparison. Full PRD/mobile hold unchanged.

R334: isolated NaN-outline module build79138 LIVE, linker59059 verified active at1m34s/~663%CPU. generated/build-add-nan-r334-fixed.log. Cached unchanged control118044...fc631 verified against exact graph/all1329objects/compiler/link argv/response; candidate replaces only float TU, compile flags unchanged. First include-lookup failure terminal1 preserved in generated/add-nan-r334-first-include-failure and build-add-nan-r334.log; fixed relocated quote include only, no ref mutation. Suite30810 exit0/repository safety passes generated/check-r334.log. Fresh add-nan-{control,candidate}-r335 profiles prepared, NOT launched. Poll SAME build handle; no final candidate hash/audit/promotion yet. Normal app/marker unchanged; no game/Simulator; full PRD/performance/mobile hold remains.

R333: NaN-outline full-kernel oracle65326 exit0; all4sanitized/optimized reference/candidate builds1440cases/digest882be09b1f38e9ad with exact callback/journal/interruption parity. Suite1918 exit0/repository safety passes. Pinned module-PGO/ThinLTO CPU-time ABBA68797 exit0: control24980.854 vs candidate24309.2175 aggregate ns (~2.69%lower), same229376-byte fixture text. Evidence generated/add-nan-kernel-bench-r333.log. Offline benefit only; next inspect exact module graph for isolated float-object replacement and byte-identical control proof, then fresh game comparison. No app/module promotion/game/Simulator; full PRD/performance-first mobile hold unchanged.

R332: exact accepted-module FP-helper assembly joined to R310 samples. ni_add carries stack setup/restore on ordinary path, unlike ni_sub; sample attribution is not instruction cost. Added offline source-pinned NaN-branch outline for ni_add only. Scalar88274 exit0:240000cases per sanitized/O2 build,560NaN results, fullCPU/result/exception/hostFP parity across4rounding modes. Not integrated or timed. Suite51065 exit0/repository safety passes generated/check-r332.log. Next extend complete-kernel oracle with this isolated float-TU variant and retained module-PGO/ThinLTO before any timing/module build. Normal app unchanged, no runtime/Simulator; full G6/performance/mobile hold remains.

R331: live scheduling capture complete, runtime45828/observer25505 exit0. All23776valid CPU-thread snapshots policy1(timeshare), current/base31,max63; no observed policy changes. Fixed60s3378VI=56.3Hz, CPU17.57575ms/interval. No scheduling root cause proven; sustained CPU deficit remains. Visible movie advance, save unchanged, fallback0/smc_failed0; no game/Simulator left. Suite7168 exit0/repository safety passes. Evidence generated/runtime/scheduling-r331/{aligned,summary}.json. No app/module changes; park further policy-only captures absent new hypothesis. Next return to R310 sampled FP-helper/native-call costs; inspect linked code before another candidate. Full PRD/performance/mobile hold unchanged.

R330: authorized Simulator erasure already complete; current CoreSimulator492MiB,72GiB filesystem available, no booted device. No repeated deletion. Reused R305/R307 thread recordings: current-priority mostly31, including all observed samples in three worst R307 hitches, but snapshots cannot establish QoS/App Nap or scheduling causality. Alignment now retains priority counts with missing/invalid handling; focused test passes, suite37870 exit0/repository safety passes generated/check-r330.log. No game/app/module changes; performance-first/mobile hold remains. Next resolve effective scheduling policy separately from numeric priority before proposing a scheduling experiment.

R329: module-PGO + ThinLTO normal-entry oracle passes1440cases/digest882be09b1f38e9ad in all4builds, candidate hits816/720. Benchmark control25028.0605 versus candidate25116.4725 aggregate CPU ns (~0.35% slower); fixture text+128KiB. PARK normal-entry candidate, no module build. Suite33676 exit0/repository safety passes. Evidence generated/normal-kernel-pgo-{oracle,bench}-r329.log and generated/check-r329.log.

R328: normal-entry THP copies implemented offline; original resumes/outer dispatch byte-preserved. Oracle69598 exit0: all4sanitized/optimized reference/candidate builds1440cases digest882be09b1f38e9ad, candidate normal hits816/720. Suite86651 exit0/safetypasses. No timing or app/module change yet. Next benchmark with ThinLTO AND pinned saved module PGO retained (existing THP oracle lacks module PGO flag; address before drawing timing conclusion). Original fallback for every interior PC remains; full G6/mobile hold unchanged.

R327: corrected ThinLTO fused-tail coverage28744 exit0/32cases/1008hits; benchmark21850 exit0 control1857.545ns/candidate1832.817ns (~1.33%edge). Fused Huffman tail PARKED, no module build. Next inspect/test separate normal-entry copies of the two extracted THP kernels while retaining exact original helpers for every interior entry; preserve original outer charge/return/backedge behavior. This targets kernels' external-entry joins, not another Huffman fullchunk split or direct-memory cache. No app/runtime/Simulator change; full G6/mobile hold unchanged.

R326: ThinLTO-preserving offline pipeline validated. Identity58397 and no-profile40420 sanitized32cases pass; timed73290 exit0: profiled1851.371ns/no-profile1831.442ns (~1.08%edge), not R32357%. Removing LTO in old fixture degraded control disproportionately. Flags-only candidate577d... parked/unselected, no more same movie/build. Suite94173 exit0/repository safety passes (generated/check-r326.log). Next evaluate existing fused-tail under corrected ThinLTO pipeline before deciding whether any decoder source candidate merits linking. Normal app/no game/Simulator/mobile hold unchanged.

R325: build48846 exit0/auditpassed candidate577d42c9...9c41 (114404072bytes). Real movie control56.1167Hz/17.6205msCPU vs candidate56.1833Hz/17.6179msCPU: effectively unchanged, NOT promoted. Both exit0/save unchanged/fallback0/smc_failed0/dropped0. No runtime/linker/Simulator. Linked chunk disassembly differs (21466vs22426lines); do not assume flag was ignored. Next reproduce benchmark with final ThinLTO pipeline intact before another module build or movie repeat; R323 native-object benchmark gain did not transfer. Normal app and mobile hold unchanged.

R324: sanitized no-profile wholefixture64950 exit0/32cases; suite68691 exit0/repository safety passes. Isolated flags-only build48846 LIVE, linker51811 verified active. generated/build-huffman-no-profile-r324.log; poll SAME handle, do not restart or edit executing builder. Reused control118044...fc631 after exact graph/1329object/compiler/link proof; unchanged chunk1103 source, only saved-PGO compile flag removed. No final candidate hash/audit yet. Fresh huffman-{control,candidate}-r325 profiles prepared/not launched. Next finish audit then sequential matched movie test; normal app/marker untouched, no game/Simulator, mobile hold persists.

R323: offline control identifies saved-PGO penalty in chunk1103. Fused path1008hits/32correct cases; long CPU ABBA ratio~0.4953, short~0.6807. Identical-source same-flags control~0.9977. UNCHANGED source with only candidate -fprofile-instr-use removed ratio~0.4342, better than fusion; next pursue narrower one-chunk compiler-profile experiment, not fusion integration/global PGO removal. All benchmark handles terminal0. Suite79779 exit0/repository safety passes (generated/check-r323.log). Need sanitized no-profile fixture then exact-graph isolated module/runtime comparison before promotion. App/marker unchanged; no game/Simulator; G6/mobile hold persists.

R322: isolated fused Huffman tail prototype implemented, no app/module selection change. Actual-emitted differential passes128000cases each ASanUBSan/O2 across16entries/8modes, fullCPU/memory/callback/journal parity. Full Huffman long-code test56416 exit0/32cases passed (generated/full-huffman-tail-r322.log); suite37340 exit0/repository safety passes (generated/check-r322.log). Next explicit candidate-hit proof, then offline timing before considering any module build. No game/Simulator; G6/mobile hold unchanged.

R321: mapped R310 remaining chunk hotspot to Huffman coefficient tail, not transform math. Added optional aligned per-instruction report plus aggregation tests and compiled CPUState offset assertions; focused tests and suite12050 exit0/repository safety pass (generated/check-r321.log). No game/Simulator/app changes. Next offline fused 80453AAC..53AEC normal-tail prototype with original external/interruption paths retained; prove CPU/memory/cycle/callback parity before any benchmark/build. CLZ-only/R187 whole-chunk split/R320 DC remain parked.

R320: reverse pair complete, candidate57.3333Hz/17.2433msCPU versus control56.15Hz/17.6108msCPU. Combined with R319, only~0.45%average VI edge and opposite pair outcomes: DC candidate PARKED/unselected, no more unchanged repetitions. Both clean exits/save unchanged/fallback0/smc_failed0/dropped0. No game/Simulator. Suite60548 exit0/repository safety passes, generated/check-r320.log. Next map fresh R310 func804530A0 samples to actual remaining decoder operations before choosing another optimization. Normal app/mobile hold unchanged.

R319: first valid movie A/B completed; control56.2167Hz/17.6148msCPU versus candidate55.5333Hz/17.7868msCPU. No demonstrated gain, candidate UNSELECTED. Both clean exit0, savea574... unchanged, fallback0/smc_failed0, dropped0. Initial control discarded due startup buffer exhaustion and preserved separately. No game/Simulator running. Next reverse-order confirmation using fresh disposable profiles and same prompt slot3/trigger/60s timing, then park candidate if no repeatable gain. Normal app/marker intact; mobile/full PRD hold remains.

R317: unchanged control relink is byte-identical to accepted118044...fc631. Build74720 advanced through changed-chunk compile (1profile mismatch warning) into candidate link, ld45973 confirmed active. Poll SAME handle; no final candidate hash/audit yet. Matching dc-control-r317/dc-candidate-r317 save/config profiles prepared but not launched. Normal app/module selection untouched; mobile/full PRD/performance open. Deferred builder header pin only after process ends.

R316: isolated builder prepared from verified accepted module/chunk/header/profile/1329-object graph. Build74720 running unchanged-control relink (ld45160 confirmed active), candidate gated on byte-identical accepted SHA; generated/build-dc-column-r316.log. Suite34276 exit0/repository safety passes. Poll SAME build handle, do not restart. No candidate/app promotion/runtime/mobile acceptance yet; normal marker/app preserved.

R315: both signed-DC kernels pass actual emitted-column/exhaustive signed16 tests and1440-case oracle (96hits per kernel per candidate). CPU-time ABBA32272 exit0: mixed0.9597004 (~4.03% faster). Offline only. Next verified isolated module build, no normal selection, then real movie comparison. Suite2521 exit0/repository safety passes; all handles terminal. No game/Simulator/mobile/publication; full PRD/performance open.

R314: signed-DC/zero-AC extension passes262144 emitted-column comparisons,13guards and1440-case kernel oracle (96hits). Benchmark37493 exit0: zero/DC/sparse ratios0.88665/0.86443/0.88163, mixed0.977533 (~2.25% improvement). Promising offline only; next test corresponding second-kernel path before canonical candidate work. Full suite26160 exit0/repository safety passes; all handles terminal. No module/app/mobile change or whole-game speed claim.

R313: zero-column prototype passes40000 emitted-column state/memory/hostFP cases and1440-case kernel oracle (60hits). Benchmark56268 exit0: kernel0 zero/DC ratios0.89026/0.90317, sparse1.03762; mixed aggregate0.993354. Pattern-specific gain only, insufficient whole-game evidence; no module build. Next extend to nonzero-DC/zero-AC columns, preserving exact multiply and original loop/yields. Suite19297 exit0/repository safety passes; all handles terminal. Normal app/mobile/full PRD unchanged.

R312: guarded DC-store run passes100k segment cases/14guards and1440-case kernel oracle (192fast hits each sanitized/O2). CPU-time ABBA70589 exit0: aggregate0.9955605, changed kernel0.9914648, unchanged kernel0.9996722. Too small to justify module work; unpromoted, no unchanged repeat. Next investigate whole zero-coefficient-column work elimination with exact state/yield/fallback contract. Suite40939 exit0/repository safety passes; all handles terminal. Normal app/performance/mobile/full PRD unchanged.

R311: callback-bounded kernel read cache passes84000 remap/boundary cases, alias-store check and1440-case full-kernel oracle, but200k-repetition CPU-time ABBA is ~3.51% slower; text229376→245760bytes. Rejected/parked, no module build or unchanged repetition. Full suite13112 exit0/repository safety passes; all handles terminal, no game/Simulator. Normal app unchanged; performance/mobile/full PRD open. Next investigate a closed algorithm-level fast path rather than more generic map/helper micro-tuning.

R310: fresh10s movie CPU profile on unchanged accepted module confirms kernels+adjacent decoder42.00% of31256CPU samples; kernel sampled instructions78.14% loads. Not instruction-cost/speed proof. Current source supports investigating callback-bounded kernel state/mapping rereads, not more helper layout changes. Visible film advance/clean close/save unchanged/fallback0/smc_failed0. Trace22MiB; no game/frontend/Simulator. Full suite36507 exit0, all handles terminal. Performance/mobile/full PRD still open.

R309: exact FMA tie-body outline passes960k scalar state/result/flags cases (50k actual corrections), sanitized/O2, plus1440case full-kernel oracle. Short CPU-time ABBA suggested1.93% gain;10x-longer samples instead yield candidate/control1.0046195 (~0.46% slower). Park; no module build or unchanged rerun. Normal app unchanged, performance/mobile gates remain open. Full repository suite72215 exit0/repository safety passes; no live handles/game/Simulator. Next structural decoder work, not helper layout variants.

R308: scheduling-policy source audit completed, not a performance fix. Actual macOS target uses DolphinNoGUI/PlatformMacos.mm; Core::Init creates EmuThread with std::thread, which becomes CPU thread, and creates Video thread separately. No explicit QoS/activity policy found in these paths; absence is not proof of low effective QoS or App Nap. Do not promote a priority change from this finding. Repeated host/thread-only captures remain parked; next work should target the established CPU-execution deficit with a measured, semantics-preserving candidate. No product edits/build/runtime this step;74GiB free, no runner/frontend/booted Simulator. Authorized Simulator erasure was already completed in R283; no further deletion.

R307: combined120s capture7177VI=59.808333Hz reproduces87.51/83.38/79.30ms hitches; measured waits small, observer gaps46.99/57.35ms again. Host100ms counters repeat/cache: published XNU host.c rate-limits/caches third-party host_statistics. Marked freshness unknown; do NOT exclude subsecond pressure from zero deltas or claim exact idle percentages at hitch. Stop identical host-probe repeats; next audit suitable scheduling evidence or materially different CPU-work optimization, no speculative priority/sync changes. Save unchanged/clean close; normal app unchanged/mobile/full performance open.

R306: current idle-host audit finds AC power/low-power off/no recorded thermal warning,74GiB free; swap counters unchanged across check (605.56MiB allocated swap not active thrashing proof). Background WindowServer/logi/kernel activity with78-81% aggregate idle. Added bounded100ms Mach host CPU/VM recorder, sanitizer/CSV/bounds tests pass, no elevated access. Next120s gameplay with existing thread-state and host-pressure probes to correlate paging/aggregate load with hitch; no host-only diagnosis or unrelated process changes. Normal app unchanged/mobile/full performance open.

R305: lightweight cross-process state capture works.120s7187VI=59.891667Hz, hitches58.091209/53.341291ms near60.84s. Contained snapshots7/10 all running/runnable; observer has52.130417ms inter-query gap spanning same pair (query calls themselves short). This suggests shared host scheduling/observer delay deserves investigation; missing coverage prevents excluding unseen waits. No CPU execution/runnable distinction or causal proof. Save unchanged/clean close/no game/frontend/mobile. Next host scheduling/pressure context, not queue/timeout changes or identical state-only repeats. Full PRD/performance open.

R304: new read-only libproc thread-state probe built; controlled sleep/busy self-test and sanitizer/bounds/non-runner tests pass. Records bounded in-memory query start/end/state/raw counters, exports after capture; no task suspension/priority change. Running state does NOT distinguish on-core vs runnable. Next use existing audited wakeup app in120s capture with2ms probe, align observations wholly within hitch intervals and report coverage gaps. Cross-process game access/runtime result unverified. No game/app rebuild/mobile; full performance goal open.

R303: wakeup diagnostic built/audited,120s real-save7189VI=59.908333Hz. Captured87.0895ms hitch at78.109318s:CPU23.011/EFB0.307458/idle0.174345/throttle0.001498/DVD0/gather0/wakeup0.03421ms. Wakeup timer nonzero/valid,total135.974745ms; excludes measured notification as cause of this incident. Stop wakeup-only repeats. Next bounded scheduler-state versus unmeasured-wait discrimination, not timeout/priority changes. Save unchanged/clean close/fallback0/smc_failed0; no game/frontend/Simulator, normal app unchanged/mobile/full performance hold.

R302: wakeup VI configure/read/export/parser complete via ModernGekko0024 (2fab078...16350). Two bootstrap passes/full suite pass; notification-hook threaded tests pass. Old-schema missing/null,13ns delta/reset and70ns CSV export verified. Isolated four-job build started at generated/macos/wakeup-r302/GalaxyPad.app, log generated/build-wakeup-r302.log. Next poll same handle, audit and real-save capture without sampler. Normal runner e86f...22b689 unchanged/no game/frontend; mobile and full performance gates open.

R301: canonical Dolphin0021 notification-only hook installed, Event unchanged. Default Wakeup delegates original notification; RunGpu observer only runs on sleeping-worker notification and times only CPU callers. Separate default-disabled wakeup metric; runtime Configure/VI export pending. Repeated bootstrap/full suite, installed-header threaded completion regression, state and wiring tests pass. No build/runtime/app promotion/mobile. Next recorder wiring then isolated capture; no hitch-cause claim yet.

R300: built-runner disassembly confirms RunGpu+92 sampled return address follows mutex::lock in inlined wakeup Event::Set; lock/unlock/notify stubs verified. Notification-only observer contract passes ASan/UBSan across all four states/enabled-disabled/repeat suppression. Next canonical observer limited to actual notification slow path, CPU-owned timer and VI export; do not clock every FIFO burst or remove handshake. No runtime modification/build yet. Normal app unchanged/no game/Simulator/mobile; full performance goal open.

R299: bounded120s/10ms stack sample completed, no rebuild. CPU tree10679samples includes4 RunGpu->mutex kernel waits, a concrete uncovered wakeup boundary; aggregate/no timestamps does not prove hitch causation. VI59.2167Hz/max249.867ms with small measured waits; sampler perturbation possible, not baseline acceptance. Next source/map and time CPU RunGpu wakeup separately, preserve Event notification handshake. Save unchanged/clean close/fallback0/smc_failed0; no runner/frontend/Simulator. Normal app unchanged/mobile hold/full goal open.

R298: gather diagnostic built/audited;120s real-save capture7186VI=59.8833Hz. Reproduced75.698208ms hitch at9.093723s: CPU17.926334/EFB0.395417/idle0.386586/throttle0.001374/DVD0/gather0ms. Gather counter valid and zero throughout window; stop gather-only repeats. Next remaining async waits or bounded scheduling evidence, not a synchronization change. Visible movement/end ledge, unchanged save, clean close/fallback0/smc_failed0. All handles terminal; normal app unchanged/no game/Simulator/mobile; full PRD/performance/audio remain open.

R297: gather wait runtime VI opt-in/export/parser complete via pinned ModernGekko0023 (c8e580...ca3e0). Both bootstrap passes and full repository suite pass. Old captures remain missing/null; nonzero export and reset checks pass. Isolated app build started at generated/macos/gather-wait-r297/GalaxyPad.app, log generated/build-gather-r297.log, four jobs/existing cache. Next poll current build handle, audit package and capture real-save gameplay; no hitch attribution yet. Normal runner verified e86f...22b689 unchanged; no game/Simulator; mobile/full performance hold remains.

R296: canonical Dolphin0020 gather-wait wrapper/member installed via pinned bootstrap, repeated bootstrap and installed-source boundary/wiring tests pass. Counter remains disabled by default and is NOT yet configured/exported by runtime; no diagnostic build or performance evidence yet. Next extend VI sample/export/parser and runtime opt-in in a new ModernGekko patch, peel it before DVD runtime patch, then isolated build. Normal app/module unchanged; full performance/mobile gates open.

R295: source-derived non-idle GatherPipeBursted wait observer test passes 128 guard/ordering cases with ASan/UBSan, including zero clock reads when disabled. Added to repository suite. Instrumentation is not installed in the runner yet; next wire a separate CPU-owned VI-opt-in counter through pinned patches, then isolated build/capture. This is measurement preparation, not a performance fix. Normal app unchanged; mobile and full performance acceptance remain open.

R293: planned120s diagnostic capture reproduces88.335125ms hitch at82.174217s:CPU23.07175/EFB0.334/idle0.308541/throttle0.001582/DVD0ms. DVD result wait excluded for THIS captured incident; no generic host/GPU cause proven. Overall7189VI=59.9083Hz, CPUmean15.339ms, DVDtotal31.995ms; visible movement/cleanclose/saveunchanged/fallback0/smc_failed0. Stop DVD-only repeat loop. Next audit/instrument remaining non-idle FIFO/async waits or bounded scheduling evidence, preserving synchronization. Normal app unchanged/no runtime/Simulator/mobile; fullPRD/performance/audio open.

R292: isolated DVD diagnostic built/audited (runnerab221c...9c480, module unchanged5c21...e91d); normal runnere86f unchanged. Real-save60s active route3588VI=59.8Hz, CPUmean15.354ms, largestVI25.557ms/DVD0.000209ms. DVDtotal14.478ms overminute; counter valid but prior55–59ms hitch NOT reproduced, so no exclusion for that incident. Visible movement/end hanging ledge, clean exit/saveunchanged/fallback0/smc_failed0. Next one bounded120s same-diagnostic capture to seek large-hitch correlation; no rebuild or normal promotion, park repeated capture if absent. No runtime/Simulator/mobile; fullPRD/performance/audio open.

R291: canonical opt-in DVD wait counter/VI CSV field installed; old CSV missing field stays null. Recorder export, parser reset/missing cases, source-derived queue contract and wiring regressions pass; two bootstrap passes/full suite pass. Initial patch scope-format issue corrected without direct vendor edits. Isolated package build5551 LIVE, generated/build-dvd-r291.log, output generated/macos/dvd-wait-r291/GalaxyPad.app,4jobs/existing cache/accepted module. Last observed23/199, no compile error. Next poll SAME5551, audit package then measure a fresh gameplay window; do not restart/bootstrap while compiling. Normal app unchanged/no game/Simulator/mobile work; fullPRD/performance/audio open.

R290: wait coverage audit identifies unmeasured CPU DVD FinishRead queue wait (not proven cause). Phase logger rejected for this measurement because it locks/writes on path. Source-derived ASanUBSan queue-wrapper test passes map-hit/out-of-order/disabled-enabled semantics. Next wire a separate cumulative DVD-wait field into VI recorder via canonical patches and isolated runner; instrumentation NOT yet installed. Normal app unchanged/no runtime/Simulator/mobile work; fullPRD/performance/audio remain open.

R289: fresh accepted normal-app real-save Observatory measurement after cleanup:3594VI/60s=59.9Hz with repeated movement/Jump/Spin, visible position change, clean exit/save5040...64a6 unchanged/fallback0/smc_failed0. CPUmean15.075ms,p9917.499 versus movie~17.654mean; only188/3593 intervals exceed16.667CPUms. Still two hitches58.929/54.534ms with24.666/22.915CPUms, not fully localized by EFB/idle counters. Distinguish movie saturation from intermittent gameplay stalls; no fullG6/soak/audio acceptance. Next bounded attribution of gameplay hitch waits using existing timing-hook coverage audit, not another identical smoke or helper microbenchmark. App unchanged/mobile hold; no runtime/Simulator.

R288: corrected offline decoder mode to reset cycle accumulator per dispatch, matching host reset policy while retaining aggregate charge comparison (not full scheduler simulation). Compiled wrapper regression passes; sanitized32long-code cases/1646loop reads pass. ABBA snapshot/control1.003645 (~0.36%slower), all length groups non-improving; snapshot stays PARKED, no more unchanged timing/build. Next materially different generated-code optimization must preserve memory alias/callback visibility; do not reinterpret tiny timing noise as progress toward60Hz. Normal app unchanged/mobile hold/fullPRD/performance/audio open.

R287: new long-code Huffman fixtures close coverage gap:32 expected-coefficient/fullstate/memory cases pass sanitized with1646 changed-loop reads, both exhausted and1M starting cycle budgets. Initial256-call fixture cap fixed to4096; no product defect. Mapping snapshot timing ratios1.00203(exhausted)/1.00313(large budget) are effectively tied/slightly slower; PARK candidate, no module build. Full suite passes; all handles terminal. Next use these fixtures for a materially different structural decoder change, not repeat metadata-cache/helper-only timing. Normal app unchanged/mobile hold/fullPRD/performance/audio open.

R286: isolated callback-aware mapping snapshots for15 read-only Huffman loops pass65536 full-chunk cases and205570 callback mapping changes under ASanUBSan/O2ThinLTO. No vendor/module/app edits. Crucial coverage result: existing32 synthetic decoder fixtures hit ZERO cached-loop reads; their0.9948 timing ratio does not evaluate the optimization. Next add valid longer Huffman-code fixtures with nonzero loop coverage before benchmarking/building. All handles terminal; repository suite passes. Candidate unselected, no game/Simulator/mobile work; fullPRD/performance/audio open.

R285: exact ni_add/ni_sub forced-inlining prototype passes whole-kernel oracle (1440 cases, same full-state/memory/exit digest in four sanitizer/optimized variants), but thread-CPU ABBA means candidate24767.3645 vs control24232.437ns (sum12pattern means), ~2.2% slower; text shrinks16KiB. Parked, no module build justified. Added isolated --inline-add-sub oracle mode only; product/vendor/app unchanged. Next structural decoder work rather than more helper-only inlining/widening variants. No game/Simulator; mobile hold/fullPRD/performance/audio remain open.

R284: saved-trace budget analysis identifies sustained CPU-thread saturation in quieter movie controls, separate from outlier stalls. R282 control59.246CPU seconds/59.995wall seconds (98.75%), mean17.654msCPU/VI, p9518.658ms;2911/3356 intervals (86.74%) exceed16.667ms CPU. R283 control similar17.611ms mean. Existing trace, no new runtime/build; counters include host execution, not exclusively guest arithmetic. Added tested full-interval distributions to summarize-vi-timing.py (missing/reset values never zero). Next target substantial generated THP/paired-single execution costs using exact GXRuntime helpers and complete-kernel oracle; isolated hitch work alone cannot restore sustained60Hz. Candidate remains parked; normal app unchanged, no mobile work or goal acceptance.

R283: Chris authorized erasing other projects' Simulator data. All 28 devices were shutdown; simctl erase all succeeded, retaining device definitions/runtimes. Device storage59GiB→492MiB; asynchronous reclamation increased filesystem available14GiB→71GiB. Simulator apps/saves permanently erased; local project inputs/saves/current products preserved. Reverse-order control3364VI/60s=56.0667Hz; candidate3384=56.4Hz, both clean-close/save unchanged/fallback0/smc_failed0. Candidate window overlaps CoreSimulator background reclamation (84.9%CPU in final sample), so NOT a clean BAAB/promotion result. Small first-pair edge remains unproven; candidate parked/default-off, normal app unchanged. Next investigate the substantial decoder cost/non-CPU hitch distinction using existing profiles; do not repeat unchanged A/B loops or start mobile work. No game/Simulator active; full PRD/G6/performance/audio remain open.

R282: first candidate/control pair complete with host-top sampling: candidate3380VI/60s=56.3333Hz, fresh control3357=55.95Hz (~0.685% edge, NOT promotion evidence). Both movie-advance/clean-exit/save unchanged/blockfallback0/smcfailed0. Lower JumpConnect load than R28118Hz collapse; no causal proof or permission to stop other apps. Candidate1b78...2cc2c0 remains isolated/default-off. Next reverse-order control/candidate pair with same instrumentation before retain/park decision; do not mix R281contended baseline into comparison. No active runtime/build/Simulator; mobile hold/fullPRD/G6/audio/performance open.

R281: candidate built/audited (SHA1b78e759...2cc2c0), manifest differs only by dcbz policy; not promoted. Control run completed/closed on Chris's cleanup request: fixed60s1100VI=18.33Hz with heavy concurrent JumpConnect/other host CPU load; unsuitable for attributing candidate benefit (candidate not run). Cleanup removed~12GiB obsolete build/app products, preserving saves/input/current app/candidate/rollback; free space~15GiB. Cleanup repository suite passes; Simulator metadata scan has no GalaxyPad matches. No game/build/Simulator active. Other-project Simulator data left intact. Next fresh comparison after host contention review, not reuse prior57Hz as matched baseline. Full PRD/G6/performance/audio/mobile hold unchanged.

R280: candidate source audit passes1322 chunks,1321 unchanged, sole1103 change matches tested transform SHA783117ca...7be9b. Build62691 remains LIVE in final ThinLTO link (1330/1332; linker observed actively using CPU), not failed/hung. Existing chunk1102 PGO mismatch matches accepted R205 log; modified1103 compiled without new mismatch. Output key6d25f3ee43c19ac3; no final manifest/audit yet. Next poll SAME62691 then audit explicit module path; no restart/bootstrap/game while linking. Normal app unchanged, no Simulator/mobile build; full PRD/G6/performance/audio open.

R279: canonical opt-in policy integrated/pinned; byte-exact C++ transform/guard tests, two bootstrap passes, repository suite and port build pass. Port SHA256c5c54f41...49709f. Isolated module build LIVE session62691, log generated/build-module-dcbz-r279.log, output generated/modules-dcbz-r279, GALAXYPAD_DCBZ_LOOP=1 and accepted PGO. Last observed Wii preflight passed; not a built module yet. Next poll same handle, inspect manifest/profile/identity and audit on completion; do NOT restart/bootstrap while build runs. Normal app hashes unchanged/no game/Simulator/mobile build; full PRD/G6/performance/audio remain open.

R278: completed synthetic Y-decoder benchmark supports loop-preserving line-clear candidate. All32 state/memory cases pass; warmed100k-per-case ABBA thread-CPU sum ratio0.901635 (~9.84% lower time), every case improves. Sparse/dense/mixed inputs and refill boundaries covered, not real movie weighting or ThinLTO runtime proof. Next integrate exact eight-site policy/cache identity through canonical pinned patch and prepare isolated module candidate; no normal-app promotion without fresh movie/gameplay evidence. App/vendor unchanged/no game/build/Simulator/mobile build. Original PRD/G6/audio/performance open.

R277: direct line-clear form invalidates decoder PGO; do not build that form. New unapplied loop-preserving form keeps profile matching (no mismatch warning) and comparable total pre-link instruction count:12,104+64+59 versus12,233. Both helper18,740 and full-chunk65,536 comparisons pass sanitized/optimized. Still no measured speedup. Next completed-decoder benchmark with representative synthetic entropy inputs; do not infer speed from static counts. App/vendor unchanged; no live build/game/Simulator/mobile build. Full PRD/G6/audio/performance open.

R276: new unapplied decoder cache-line-clear candidate passes isolated18,740 cases in ASan/UBSan and O2, then complete chunk65,536 cases in ASan/UBSan and O2ThinLTO (zero capped; matching callbacks/journals/reservations). Replaces eight independently mapped zero stores only for full ordinary mapped lines without journals/state alias; all other paths unchanged. No speed claim yet. Next offline whole-decoder timing/code-shape check before any module build. App runner/module hashes reconfirmed unchanged; no game/build/booted Simulator/mobile build. G6/full PRD/performance/audio open.

R275: execution-loop triage complete; no condition-order patch/build justified. R214 profile attributes 813/31295 leaf samples to Run and 86 to SyncIn/Out, versus 12928 to the two THP kernels plus decoder chunk (not exclusively Huffman). R270 burst exits are only ~1.08% of native dispatches; changing termination check order is not a credible primary lag fix. Sustained decoder CPU cost and R247 intermittent graphics-completion wait remain separate unresolved issues. Next investigate decoder body/dataflow rather than repeat helper microbenchmarks or unchanged hitch captures. App unchanged; no running game/booted Simulator/mobile build. Original PRD/G6/performance/audio remain open.

R274: hardware widening PARKED. Complete-kernel oracle matches all four modes; longer wall-time benchmark noisy, thread-CPU ABBA effectively tied (~0.064% slower candidate), +16KiB text. No module build/promotion justified. Normal app retains verified empty-rel runner e86f2e09...22b689 and unchanged module. Next target a larger structural cost; avoid repeating parked helper/lookup/extraction experiments. No runtime/build/Simulator/mobile build; full PRD/G6/performance/audio open.

R273: unapplied normal-finite hardware-widening prototype passes849152 result/FENV/raw ARM status/control comparisons across four rounding and both runtime flush modes. Exceptional inputs use old path. Isolated normal-input times ~23–27% lower; not a game-speed result. Next exact types.h override in complete-kernel oracle and whole-kernel benchmark before any module build. Normal app/vendor unchanged/no runtime/build/Simulator/mobile build; original PRD/G6/performance/audio open.

R272: promoted normal wrapper discovers bundled module without override and loads original one-star save through real menus; visible Observatory/input response, native-only clean exit, unchanged save. No fixed-window/soak/audio acceptance. Promotion launch check complete; do not repeat unchanged Observatory/guard tests. Next inspect distinct normal-finite float-widening opportunity with host FP-status correctness guards before timing. No runtime/build/booted Simulator/mobile build; full PRD/G6/performance/audio still open.

R271: diagnostics-disabled candidate movie completed into gameplay; movement responsive, clean native-only exit/save unchanged. Audited runner-only normal-app promotion complete: runner e86f2e09...22b689, module unchanged5c21...e91d, wrapper/frontend unchanged. Backup GalaxyPad.app.previous.runner-r271 retained. Next normal-path discovery/real-save reload smoke, then remaining macOS performance/stability. Incremental~1.83% gain does NOT meet60Hz/audio/G6/fullPRD; mobile builds remain held. No runtime/build/booted Simulator.

R270: completed ABBA VI-only movie comparison, counts3365/3424/3406/3342 per60s. Candidate mean56.916667Hz vs control55.891667Hz (+1.8339%); both candidate runs faster than both controls. Native-only/unchanged saves/clean exits. Retain guard, but next diagnostics-disabled movie completion/gameplay smoke before audited normal runner promotion. Still below60Hz; no audio/G6/full PRD acceptance. Normal app unchanged/no runtime/build/booted Simulator/mobile build.

R269: first matched candidate window3424VI/60s=57.066667Hz vs control3365=56.083333Hz (+1.7533%). Native-only/save unchanged/cleanclose; worst interval22.18ms vs35.42ms. Single pair only, NOT causal/performance/audio acceptance. Next fresh reverse-order candidate/control to complete ABBA before promotion. Normal app unchanged/no runtime/build/booted Simulator/mobile build; full PRD/G6 open.

R268: valid control movie window captured in empty-rel-control-r268:3365VI/60s=56.083333Hz, native-only/save unchanged, cleanclose. First control-r267 window REJECTED due Python/C++ clock-origin mismatch; use compiled generated/steady-clock-now for all further anchors. Candidate profile/app from R267 remains unlaunched. Next matched candidate VI-only movie60s run; no speedup yet. No runtime/build/booted Simulator/mobile build; original PRD/G6/performance/audio open.

R267: pinned empty-rel guard integrated through repeatable bootstrap; fullsuite/build58326 FINISHED0. Isolated signed empty-rel-r267 app ready (runner e86f2e09...22b689; module unchanged5c21...e91d); flight-r260 c460...7f7fe is matching control. Disposable R85 control/candidate profiles ready with matching slot3 and native1x/Metal settings, neither launched. Next matched movie comparison; no speedup yet. Normal app unchanged/no runtime/build/booted Simulator/mobile build; full PRD/G6/performance/audio open.

R266: prepared unapplied empty-relocation-list guard for the paired locked-cache pointer hook. Actual resolver has no side effects on an empty list; other eligibility checks unchanged. Existing/experimental host tests and 5,138 actual-resolver comparisons pass; patch applicability checked. Next isolated runner measurement with unchanged module, not normal app promotion. No vendor/app change, runtime/build/booted Simulator/mobile build; full PRD/G6/performance/audio open.

R265: paired-load change is PARKED. Complete-kernel oracle passes all four modes with identical state/memory/callback digest. Longer 200,000-repeat ABBA yields only ~0.068% aggregate improvement, below observed variation, and +16 KiB code. Isolated microbenchmark benefit does not justify a game candidate. No app/vendor change, runtime/build/Simulator/mobile build; original PRD/G6/performance/audio remain open. Select a distinct substantial bottleneck next, not another paired-load/store or extraction retry.

R264: new unapplied type-zero direct-RAM paired-load prototype passes 100,000 ASan/UBSan cases plus CPU alias ordering. Finite-input microbenchmarks improve ~21–29%, but zero-input trials regress up to ~12%; neither is a game-speed result. Next use the exact snippet with complete transform-kernel oracle and broader kernel timing before any module build. Accepted app/vendor unchanged; no game/build/booted Simulator/mobile build; original PRD/G6/performance/audio remain open.

R263: isolated luminance decoder extraction passed 65,536 differential cases under ASan/UBSan and optimized ThinLTO, but is PARKED. Current-profile assembly grows markedly; no-profile control still shows no clear reduction in static instructions/load/store count. No runtime candidate warranted; do not repeat this extraction or rejected decoder PGO training. Accepted app unchanged, stale diagnostic frontend closed, no runtime/build/booted Simulator. Next select a different substantive CPU cost; mobile builds remain held and full PRD/G6/performance/audio remain open.

R262: resumed reproducible movie CPU investigation. Exact-DOL boundary audit identifies complete luminance Huffman region 0x804534B4–0x80453B10 in chunk_1103 as the next isolated extraction experiment. No guest calls/outside direct branches; final LR return. Boundary evidence is not a speedup or execution proof. Next preserve interior-entry cycle charges, callbacks and return dispatch, then differential-test before considering a candidate. Accepted app unchanged; no runtime/build/Simulator; mobile builds held; G6/full PRD open.

R261 fullsuite28033 FINISHED0/check-r261.log ends Repository safety checks passed. No active test/build/runtime/Simulator.

R261: microbenchmark62960 FINISHED0 shows enabled CPU pair~3.3ns/graphics36–38ns, not end-to-end proof. Flight runtime94513/load66013/input37271 FINISHED0; verified Observatory BEFORE logged180s arm,21movementcycles cover120s armed window. Rolling export works but triggered0/no20ms idlewait; not hitch/performance acceptance. Cleanclose/nativeonly/saveunchanged; whole32under8backlognotaudioacceptance. PARK intermittent capture; next reproducible CPU-heavy movie/R214 kernel-decoder profile, no more unchanged near60FPS repeats. Fullsuite check-r261.log launched; no runtime/build/Simulator/mobilebuild/fullPRD/G6 open.

R260 fullsuite34555 FINISHED0/check-r260.log ends Repository safety checks passed. No active test/build/runtime/Simulator.

R260: build51036/signverify6430 FINISHED0. Isolated flight-r260 app runnerc460fd84...7f7fe/moduleunchanged. Flight analyzer metadata/arming/endpoint/paired coverage tests pass, no-trigger/no-response explicit. Fullsuite34555 active/check-r260.log; disposable flight-r260 save5040...64a6 ready/no runtime launched. Next bounded overhead check then explicit-delay capture and --flight analysis. Accepted app untouched/no build/game/Simulator/mobilebuild; fullPRD/G6 open.

R259: canonical rolling recorder integrated: ModernGekko0020 c72c94b2...d3172 / Dolphin0018 c40a8223...8466b. Explicit arm-delay env/logged deadline/20ms trigger; CPU reuses idle timestamps, graphics wall-only, original wait intact. Bootstrap14867 twice and wiring checks pass. Sequential fullsuite/build51036 active/check-r259.log/build-flight-r259.log; poll SAME handle, no bootstrap/duplicatebuild. Next isolated verification/overhead/flight-metadata analysis before capture. Accepted app untouched/no runtime/Simulator/mobilebuild; fullPRD/G6 open.

R258: isolated explicit arming parser, observed idle timestamp-reuse variant and flight forced-write failure test added. Strict delay/overflow validation; disabled wait once/no clocks/noobserver, enabled reuses2timestamps. Focused/fullsuite78209 FINISHED0/check-r258.log pass. Next canonical rolling session/runtime arming/idle observer integration and bootstrap/build; existing vendor/accepted app unchanged. No build/game/Simulator/mobilebuild; fullPRD/G6 open.

R257 fullsuite78620 FINISHED0/check-r257.log ends Repository safety checks passed. No active test/build/runtime/Simulator.

R257: isolated flight recorder/export implemented, NOT vendor-wired. Trigger/graphics-response/arming/threshold/endpoints/overwrite metadata, chronological rings, explicit invalid config, CPU existing timestamps and graphics wall-only clock. Two-writer/no-trigger/no-response/nooverwrite tests35701 FINISHED0; fullsuite78620 active/check-r257.log. Add flight forced-write failure test then canonical arming/timestamp-reuse/session integration and overhead validation. No build/game/Simulator/mobilebuild; accepted app unchanged/fullPRD/G6 open.

R256: isolated rolling trigger protocol implemented/tested, NOT runtime wired. CPU reuses wait timestamps, first long wait after explicit arming boundary freezes CPU/request; graphics owner finishes notification pair then freezes, missing response remains explicit. Pre/cross-arm waits excluded;100 threaded boundary cases and fullsuite74876 FINISHED0/check-r256.log pass. Next recorder/export+runtime arming and timestamp reuse, assess overhead before capture. Accepted app/vendor untouched/no build/game/Simulator/mobilebuild; fullPRD/G6 open.

R255: isolated rolling completion buffer implemented, NOT runtime wired. Latest32768 events/chronological wrap/overwrite count, owner-thread freeze with disabled/frozen clock bypass. Threaded atomic-request test and fullsuite69855 FINISHED0/check-r255.log pass. Next long-wait trigger + explicit gameplay arming + paired graphics freeze metadata, not another first-N capture. Accepted app/vendor unchanged/no build/game/Simulator/mobilebuild; fullPRD/G6 open.

R254: completion capture rejected for coverage. CPU32768events fill0.659s/28.6Mlaterdrops; graphics32768 fill4.465s/27.9Mdrops, long before gameplay. Analyzer correctly refuses window; no wakeup-attribution result. VI full120s7191=59.925Hz/max27.719ms (no53ms idlehitch). Runtime76991/load91137/input2118 FINISHED0, visual movement/cleanclose/nativeonly/saveunchanged; whole46under11backlognotaudioacceptance. Next bounded recent-event freeze on longidlewait with ownership/overhead tests, no unchanged first-N repeat. No runtime/build/Simulator/mobilebuild; fullPRD/G6 open.

R253 fullsuite57844 FINISHED0/check-r253.log ends Repository safety checks passed. No active build/test/runtime/Simulator.

R253: build69922/signverify56660 FINISHED0. Isolated completion-r253 app runnerfeddd353...4589d/moduleunchanged5c21...e91d; accepted runneraffb...e295 independently unchanged. Completion stream coverage/boundary analyzer and focused tests pass. Disposable completion-r253 save5040...64a6 ready/no runtime launched. Fullsuite57844 active/check-r253.log; poll same handle then both-opt-in active capture, validate both streams before attribution. No build/game/Simulator/mobilebuild; fullPRD/G6 open.

R252: completion runtime integration canonical/pinned: ModernGekko0019 01c931eb...71186, Dolphin0017 cba14f51...933c4. Independent GALAXYPAD_COMPLETION_TIMING configure, CPU idle endpoints, opt-in graphics notification observer, post-both-join export. Bootstrap twice36795 FINISHED0 and wiring tests pass. Sequential fullsuite/build69922 active/check-r252.log/build-completion-r252.log; poll SAME handle, no bootstrap/duplicate build. Next isolated capture with stream coverage/drop audit. Accepted app untouched/no runtime/Simulator/mobilebuild; fullPRD/G6 open.

R251 fullsuite5454 FINISHED0/check-r251.log ends Repository safety checks passed. No active test/build/runtime/Simulator.

R251: isolated completion recorder/export implemented/tested35696 FINISHED0, not vendor-wired. Separate writers, opt-in-only allocation/clocks, one exclusive CSV with stream/drop metadata, post-both-join export. Verified emulation scope joins graphics before Shutdown returns. Fullsuite5454 active/check-r251.log. Next canonical Common headers/CPU idle endpoints/Fifo observer/runtime configure+shutdown export. No build/game/Simulator, accepted app untouched/fullPRD/G6 open/mobileheld.

R250 fullsuite2771 FINISHED0/check-r250.log ends Repository safety checks passed; no active test/build/runtime/Simulator.

R250: isolated completion observer patch/test added, not vendor-applied. Pinned-source O2ASanUBSan86687 FINISHED0,100 enabled+100 disabled wait/wakeup/paired-notify/stop runs. Optional null callback only at normal completion notification, no hot payload instrumentation; state/event ordering preserved. Fullsuite2771 active/check-r250.log. Next connect bounded events and post-both-join export before canonical build/runtime. No game/build/Simulator; fullPRD/G6 open/mobileheld.

R249 focused/fullsuite98179 FINISHED0; check-r249.log ends Repository safety checks passed. No running test/build/game/Simulator.

R249: isolated bounded completion event buffers/tests added, NOT runtime wired. Separate CPU/graphics writers, post-both-join reads,32768eventcap/drop counts, disabled/full bypass clocks. Notification timestamps are not exact DONE publication (CPU can observe DONE first); retain boundary/race caveat. Focused+fullsuite sequential98179 active/check-r249.log. Next opt-in notification observer and wait endpoints, not hot payload iteration instrumentation. No build/runtime/Simulator; fullPRD/G6 open/mobileheld.

R248: worker completion audit narrows next measurement. BlockingLoop100ms timeout belongs to worker idle new-work wait, NOT CPU completion wait. Event uses flag/predicate mutex/notify protocol; no obvious lost-wakeup defect established. Worker payload includes FIFO/draw/cache refresh before completion; async cache refresh omits explicit staging wait. Next bounded worker completion + CPU/wall correlation with measured53ms idlewait, preserving notification order and avoiding busy-loop observer overhead. No source/runtime change; fullPRD/G6 open/mobileheld.

R247: large hitch reproduced and localized: complete120s7188VI=59.9Hz;74.399875ms interval includes53.444174ms idle FlushGpu elapsed,16.720458ms CPU,0.325333EFB/0.001208throttle. Boundary now identified; GPU work vs completion/wakeup scheduling still unproven. Samecandidate runtime26644/load73524/input17236 FINISHED0; visible Observatory movement/cleanclose/nativeonly/saveunchanged,344drops AFTER fullwindow. Next inspect BlockingLoop worker completion path, preserve synchronization; no further same-boundary repeats needed. No runtime/build/Simulator; fullPRD/G6 open/mobileheld.

R246: build82837/candidate signing32143/runtime95167/load59888/input14477 FINISHED0. Isolated runner0b6bd1bf...36e209/moduleunchanged; active120s complete7186VI=59.883333Hz. Largest22.661ms wall/20.828CPU/0.332idle; max idle1.175ms acrosswindow. Counter works, but no prior80–96ms hitch reproduced: no causal exclusion or performance fix.940 drops occur AFTER complete window. Visible Observatory movement/cleanclose/nativeonly/saveunchanged; whole34under9backlog not audioacceptance. Next one bounded samecandidate repeat, then pivot back to reproducible movieCPU path if largehitch absent. No runtime/build/Simulator; fullPRD/G6 open/mobileheld.

R245 sequential test/build handle82837 active; poll SAME handle. Do not bootstrap/restart while it runs.

R245: idle-to-FIFO elapsed measurement wired via canonical ModernGekko0018 fd268ed8...75967 and Dolphin0016 63970dcc...776c1; configure before boot/CPU-only counter/exactly one original wait. VI export sixth field and backward-compatible analysis tests pass, bootstrap twice2339 FINISHED0. Sequential fullsuite then macOS runner build launched (check-r245.log/build-idle-wait-r245.log); follow same handle. No app promotion/game/Simulator/mobilebuild; next isolated active capture tests idle-wait contribution. FullPRD/G6 open.

R244 fullsuite50099 FINISHED0/check-r244.log ends Repository safety checks passed. No build/test/runtime/Simulator remains.

R244: isolated idle-wait timing helper implemented, not wired/packaged. O2ASanUBSan50700 FINISHED0 proves exactly-once callback, disabled clock bypass, accumulation/reset/saturation and exception propagation. Fullsuite check-r244.log launched. Next CPU-owned PerformanceMetrics field/session configure, wrap existing CoreTiming::Idle FlushGpu only, extend VI export and canonical patches. No product/runtime change; accepted app untouched, fullPRD/G6 open/mobileheld.

R243: source/config audit identifies enabled idle-to-FIFO wait route independent of SyncGPU=false. StaticRecomp configured idlePC calls Idle; default SyncOnSkipIdle=true calls FlushGpu which waits in dual-core non-deterministic mode. R237 sample also contains3 BlockingLoop waits but not aligned toR242 hitch. See VI-WAIT-AUDIT.md. Next opt-in elapsed counter around existing CPU idle FlushGpu, preserving behavior/disabled bypass; no product changes or new runtime this turn. FullPRD/G6 open/mobileheld.

R242 (2026-09-07): controlled120s capture completes,7173VI=59.775Hz/dropped0. Largest95.934541ms wall interval uses20.374625ms CPU,0.401625ms EFB and0.001374ms throttle; second78.746042/23.397083/0.255291/0.002376. EFB/pacing cannot explain these nonexecuting spans; other waits vs host descheduling still unresolved. Visible Observatory movement, clean runtime15251 exit0/nativeonly/saveunchanged; fullrun49under10backlog not audioacceptance. Next inspect CPU FIFO/other waits and enabled gates, not another unchanged FPS trial. No game/build/Simulator; accepted app untouched/mobileheld/fullgoal open.

R241 suite79768 FINISHED0, check-r241.log ends Repository safety checks passed. No active build/test/runtime/Simulator. Next candidate active-play capture as below.

R241: build54832 FINISHED0; isolated signed/verified macOS app vi-counters-r241 ready (runner77d595cd...e0e73f, module unchanged5c21...e91d). Accepted runner affb...e295 independently unchanged. Complete-window VI counter analyzer and boundary/reset tests added/pass. Disposable vi-counters-r241 profile/one-star save5040...64a6 ready, no runtime launched. Fullsuite79768 active/check-r241.log; poll same handle then controlled120s active gameplay with opt-in recorder/no phase trace. No mobile build, G6/fullPRD open.

R240 isolated macOS runner build active on handle54832, generated/build-vi-counters-r240.log. Added counter retention/reset assertions also pass. Poll same build; do not bootstrap or start another build/runtime while active.

R240: opt-in VI recorder now snapshots existing cumulative EFB elapsed and CPU throttle elapsed alongside wall/thread-CPU time. Disabled guard avoids extra reads; export still after shutdown join. Canonical0017 c5a2da36...02b6e and Dolphin0015 15ae34e6...7f68f pinned/scope-audited; bootstrap twice and fullsuite17291 FINISHED0/check-r240.log pass. No timing/depth semantics changed; accepted app/module untouched. Next isolated macOS runner build and active-play attribution; no performance improvement claimed. iOS/iPadOS builds remain held, full PRD/G6 open.

R239: binary hot-path audit no obvious execution-work change. Accepted/candidate StaticRecompCore::Run each540instructions/sameopcodesequence; HookExternalRead+HookExternalPointer each198/sameopcodes. Non-address operand changes5Run+3hook low-address adds; Mach-O section reads match7nonempty NUL-terminated referenced byte sequences,1emptyinconclusive. Module signedhash5c21...e91d identical. Not fullsemantic/layout/performanceproof and no candidatepromotion. Saved targetedasm runner-compare-r239; initial --macho ignoredsymbolfilter, stopped ownobjdump and replaced oversizedfiles with bounded-d outputs. No runtime/build/Simulator. Next extend memory-only VI sample with existing cumulativeEFB elapsed counter and CPUthrottle elapsed getter, preserving realdepth/pacing; then attribute offCPUhitch before moreFPS-only trials. Fullgoal open/mobileheld.

R238: acceptedrunner control13244/load72123/movement52711 FINISHED0. SamecopiedR237configs/disposableone-starNAND, bothdiagnosticsunset; focusedtitle/ordinaryObservatory/movement screenshots59.9–60FPS. Does not reproduceR23748–52, but shorter/sequentialhostconditions not controlled and R236candidate also59.9; no provenregression/no candidatepromotion. GFXfilesidentical,currentbuildRelease/-O3/-DNDEBUG. HostAC100%,lowpowermode0 forAC/battery; no thermalclockproof. Cleanclose/nativeonly/saveunchanged; whole225.5s2under6backlognotaudioacceptance. Next compare recorded build/runtime identities and bounded paired cadence under same livehost conditions before extra instrumentation; keep specific61mshitch and sustainedCPUslowdown separate. No game/build/Simulator; macOSperformancefirst/fullPRD retained.

R237: disabled diagnosticrunner smoke completes but sustained lowFPS observed: screenshot52.1 then48.2, laterAX49.2 in Observatory. Same runtime53929 resumed across userstatus interruptions; initial unfocused load72962 stayedtitle, focus+load86250 then movement63896 pass. Short sample2228 (1s/10ms) CPU77samples/60chassis_dispatch,3floatfuturewait; video46/77conditionwait. This sustained slowdown appears CPU-side, distinct fromR236 isolatedoffCPUhitch; not exactpercentagecost or hardwarecauseproof. No vi-timing export/file, cleanclose/fallback0/SMCfailed0/saveunchanged. Whole353.5s412underruns14backlogs clearly not audioacceptance. Next acceptedrunner matched control before assuming diagnosticrebuild has no regression; defer extra instrumentation until comparison. No game/build/Simulator. User explicitly keeps iOS/iPadOS builds onhold until macOS performance great; fullPRD retained.

R236: build14159 FINISHED0. Isolated signed app generated/macos/vi-timing-r236/GalaxyPad.app runner02b03bcc176bd84a9e6d98aaf0b71e4b74afeaccacb91bb4bfd0c11d0b31cb51; acceptedrunneraffb...e295 unchanged. Enabled recorder runtime4197/load25984/input28373 FINISHED0; ordinary Observatory/movement/endvisual/cleanclose/nativeonly/saveunchanged. No phase trace/SystemTrace; timingfile absent duringrun then export_result1.16384samples/allCPUclocksvalid,dropped2055 AFTER selectedwindow; fixed120s340472883492916..340592883492916 complete7188VI=59.9Hz. Largest61.630834ms wall/25.207917msCPU at4.671606s: ~36.4ms nonexecuting, not solely guestcompute; no wait-source attribution yet. Next disabled-mode candidate smoke and inspect specific CPU wait boundaries (throttle/GPU/EFB) before additional instrumentation or promotion. No game/build/Simulator; fullgoal open.

R235 active runner build handle14159, generated/build-vi-timing-r235.log; verified live39/182. Poll SAME14159, no restart/bootstrap.

R235: canonical0017-vi-timing-recorder.patch integrated, SHA650db467b1839e43dc1fb0522f0fc8fd6f8ee648241db96a28aebdc0e05b6f46. Embeds tested headers; opt-in GALAXYPAD_VI_TIMING configured beforeboot, sample insideVIcallback, export/resultlog immediately afterCore::Shutdown on normal/destructor paths. Bootstrap27236/repeat69492 FINISHED0; wiring/parity tests and fullsuite10681 FINISHED0/check-r235.log. Runner build launched build-vi-timing-r235.log, targetmoderngekko-run only/parallel4; poll returned handle, no bootstrap during build. Packaged runneraffb...e295 unchanged. Next isolated build audit/enabled+disabled smoke before any app promotion. No game/Simulator; fullgoal open.

R234 fullsuite28209 FINISHED0/generated/check-r234.log ends Repository safety checks passed. No running tests/game/build/Simulator.

R234: isolated vi-timing-recorder.h adds Configure/disabled clock bypass, steady/current-thread CPU samples with validity, exclusive-create CSV export only FlushAfterJoin, idempotence/restart and file-error results. NOT wired/promoted. O2ASanUBSan tests pass24905 then98367 including artificial8byte RLIMIT_FSIZE/fclose failure with limits restored; no diskfill. Fullsuite launched check-r234.log. Next canonical ModernGekko host patch include/copy headers, configure beforeRun/boot, record insideVI CPUcallback, flush+report afterShutdown on normal/destructor paths; verify patch provenance then isolated runner build. Accepted app unchanged/no game/Simulator/build; fullgoal open.

R233 suite31335 FINISHED0/check-r233.log ends Repository safety checks passed. No running test/game/build/Simulator.

R233: isolated memory-only VI timing buffer implemented/tested; NOT wired to game or packaged. patches/experiments/vi-timing-buffer.h fixed16384samples, singleCPUwriter, no clocks/allocations/locks/I/O, dropped-count saturation and explicit CPUclockvalid bit. O2ASanUBSan joined-writer/order/capacity/reset/invalidclock tests pass44399; added suite (active31335/check-r233.log). Source confirms VI/Core::OnFrameEnd CPU-thread boundary; Core::Shutdown joins emuthread. Read/flush only after that join, not merely hook removal. Next opt-in clock callback plus post-Shutdown export via canonical patch, separate runner test before app promotion. No game/build/Simulator; fullgoal open.

R232: full-window System Trace FAILED134 at finalization: Could not expand file / No space left on device. Runtime31536/load90070/input2663/host86828 FINISHED0; cleanclose/nativeonly/SMCfailed0/save5040...64a6 unchanged, end Observatory60FPS. No usable scheduler result. Requested60s/window60s generated incomplete4GiB trace plus orphan4GB temp Apple Trace. Removed only new incomplete scheduler-r232/system.trace and verified no-open-handle instrumentsTorrXu.ktrace (created23:01:28 duringcapture); permanent/nonrecoverable, logs/phase/host retained. Free space restored4.1GiB. Old caches untouched. NO retry heavyweight System Trace. Next lighter in-process bounded wall/thread-CPU timing around VI gaps, memory-only recording and shutdown flush; inspect callback/thread contract and focused tests before changing accepted runner. No game/test/build/Simulator; fullgoal open.

R231 suite45123 FINISHED0/check-r231.log ends Repository safety checks passed. No remaining test/runtime/build/Simulator.

R231: resolved R230 timing discrepancy: form.template records rawstart1788752866.391601/end1788752927.342171/windowstart1788752917.342171. Recording60.95057s, retained LAST10s; discarded first50.95057s. TOC start date is not retained-window start. Added audit-trace-window.py plus reference/order/duration/missing-metadata tests (pass, added suite). Saved scheduler-r230/window.json. Earlier R229 clock-pair extrapolation suggests599VI/10s/max23.735ms in retained interval, but offset varied3.509ms even during earlier sample and no R230 anchors: NOT exact correlation or explanation of big hitches. Next one capture with explicit --window60s and paired wall/raw clock anchors; validate retention before interpretation. Fullsuite launched check-r231.log; no game/build/Simulator, fullgoal open.

R230: System Trace captured/exported, NOT yet causal hitch attribution. Runtime21544/load78066/input44620/capture33451/TOC70765/threadexport97341/parser12315 FINISHED0. Requested60s but TOC actual duration10s (2026-09-06T22:47:46.392-05:00..22:47:56.392); resolve this scope before inference. CPU states sum10s: Running8.973147,Blocked.793207,Runnable.018488,Interrupted.139760,Preempted.075398; longest interval .990026s Running at0. During profiler saving window title27.8FPS, after profiler exit same scene60FPS; strong observer disturbance, not baseline result. Before/end/recovery visuals normal Observatory, cleanclose/nativeonly/SMCfailed0/NANDunchanged. Evidence scheduler-r230/{system.trace,toc.xml,threads.xml,phase.csv,runtime.log,capture.log}; trace344MiB/XML84MiB. Next align actual10s scope to phase hitches and inspect interval completeness before more capture or product changes. No game/build/test/Simulator; fullgoal open.

R229: matched active route WITHOUT midwindow screenshots still hitches. Runtime1685/load83218/input4432/host72776 FINISHED0; before/end visuals show Observatory movement/no warning (end Mario hanging from ledge, no midwindow visibility claim). Fixed120s337919247128041..338039247128041: VI/begin/present7193events=59.9417Hz; presentation max78.475291ms,27gaps>=20ms. VI>=40ms at8.482/89.659/111.036s.24hostintervals zero swap/pageout/compression. Screenshots not necessary for hitch reproduction; not proof zero observer cost. Same acceptedmodule/save, cleanclose/fallback0/SMCfailed0/NANDunchanged; prior R228 fullsuite current (no codechange). Next targeted scheduler/System Trace around active hitch to distinguish CPU work from waiting, including phase logger mutex/I/O as possible observer; no more unchanged FPS trials. No game/test/build/Simulator; fullgoal open.

R228 regression57433 FINISHED0, generated/check-r228.log ends Repository safety checks passed. No game/build/test/Simulator remains.

R228: fresh active-r228 accepted signed module5c21...e91d/disposableNAND normal-profile route. Runtime81976/load95604/input99312/host62588 FINISHED0. Initial load53922 sent before ready title and stayed title; fresh visual check then retry succeeded. Repeated16 movement/jump/Spin smoke cycles, periodic screenshots show distinct Observatory positions/no interruption. Fixed120s starts337515665936416; allthree VI/begin/present7186events=59.8833Hz, minute59.8167/59.95; presentation max89.996ms,29gaps>=20ms. Host24intervals zero swap/pageout/compression. Occasional VI/DMA/input stalls together while audio callbacks remain~10.7ms; no cause proven, capture timing not independently stamped. Cleanclose/nativeonly/SMCfailed0/NAND5040...64a6 unchanged. Fullsuite launched check-r228.log (see journal/returned handle); no game/Simulator. Next isolate observation overhead with a matched active route without midwindow screenshots, exact before/after visuals; not another idle soak or proof that22FPS is solved. Fullgoal open.

R227: idle interruption is consistent with guest auto-sleep, not established as a host input defect. Petari WPAD compares unchanged input age to60*sleepTime; exact RMGE01 generated code initializes matching timer byte to5 (804D767C/804D7680) and compares elapsed time to60*byte at804D6AF8–804D6B04. No trace proves actual warning onset/reason; R223 remains invalid as gameplay acceptance. No sleep bypass/fake keepalive. Fullsuite32643 FINISHED0/check-r227.log. Scene analyzer now separately reports VI/frame_begin/present_done Hz (focused tests pass after change); R223 all35919/600s=59.865Hz, no sustained presentation-count deficit in that interrupted recording. R210 movie likewise3319events for allthree/60s=55.3167Hz. Neither explains historical22FPS. Next bounded active-play route with periodic visual checks and separate presentation/VI rates, retaining accepted app; no repeat unattended idle soak. No game/build/Simulator, fullgoal open.

R226 IMPORTANT: sustained scene test INTERRUPTED by guest WiiRemote communication warning, visible at end; near60FPS bins do NOT prove uninterrupted gameplay. Recorder75477/runtime69826 FINISHED0. Tenbins35919VI=59.865FPS, range59.433–59.95,maxgap107.013ms,133gaps>=20ms;120hostintervals zeroSwapins/Swapouts/Pageouts/Compressions. Warning onset unknown (no midrunvisuals); do not assign laterbins to Observatory. Neutral+A reconnect fixture67503 FINISHED0 clears warning visibly/game resumes; cleanclose/fallback0/SMCfailed0/NAND5040...64a6 unchanged. Next investigate emulated remote idle-disconnect/report contract before another sustained run; no blanket fakeinput keepalive. Fullsuite for new analysis/fixture deferred until nextturn. No game/Simulator/build; G6/fullgoal open.

R225: SAME runtime69826/recorder75477 verified live through bounded45swait, no scenechange. Minute3=59.7333FPS,p9919.804541ms,max107.013334ms; first40hostintervals zeroSwapins/Swapouts/Pageouts/Compressions. VIgaps>=50ms atelapsed1.266/52.682/163.847/164.491s, not proof of causal source. Continue until fixedend336533513367500; no close/restart/build early. Then full10bins/hostsummary, movement and cleanup. G6/fullgoal open.

R224: SAME sustained runtime69826/recorder75477 verified live. Added read-only complete-minute scene analyzer plus focused boundary/incomplete-line tests (pass; fullsuite deferred until runtimeclosed). Firstminute3566VI=59.4333FPS,p9920.928959ms,max94.993667ms,55gaps>=20ms; not full10minresult. Continue SAME run until rawclock336533513367500/recorderterminal; no restart/movement/pause/build. Then final10bins/hostcorrelation, movement/close/NANDcheck. Acceptedapp unchanged, G6/fullgoal open.

R223: ten-minute scene test ACTIVE. Runtime69826, hostrecorder75477 (--seconds600/interval5), load16332 FINISHED0; fresh sustained-r223 normalconfigs/disposableone-starNAND/no savestates, automatic bundledmodule. Observatory visible before timedrecording. Window starts firsthost monotonic_raw_ns335933513367500, intendedend336533513367500; phase.csv uses matching clock. No movement/pause during fixedwindow; test movement after end. Poll SAME75477/69826; no restart, bootstrap/build or secondgame/Simulator. Next per-minuteVI cadence+hostdelta analysis once fullwindow recorded, then movement/close/NANDcheck. Not fullgameplay/60minsoak/G6 acceptance.

R222: automatic module discovery verified without--module or inheritedSTATICRECOMP_MODULE. Fresh discovery-r222 copies normalAppSupport configs plus disposableone-starNAND; onlypipe input profile adapted. Runtime54227/load58445 FINISHED0; bundled module path logged, visible Observatory ordinaryload, cleanclose/NAND5040...64a6 unchanged. Whole115s2underruns3backlogs not sustainedacceptance. Next fresh10minuteObservatory phase+hostpressure run to test time-dependent degradation, with bounded input/snapshots; static scene result cannot prove full gameplay/soak. No game/Simulator/build, app/userconfigs unchanged; G6/fullgoal open.

R221: FP routing benchmark14067 FINISHED0; ABBA totals24590.3/25868.7/24508.7/24697.2ns, firstcandidate disturbed, second only~0.55% below controlmean. Text229376->245760 (+16KiB). No reliable gain; PARKED/no fullmodule/unchangedrepeat. Read-only normal ApplicationSupport settings reconcile: GFX identical to R210; Core/DSP matches apart ordering/generatedIDs; Metal1x/CPUThreadTrue. Runner source prioritizes STATICRECOMP_MODULE override, else bundledmodule thenusercache. Next normal discovery/config-isolated launch without explicit--module to verify real app route, then sustained in-game cadence investigation for unexplained22FPS; preserve actualuserNAND. App unchanged/no game/build/Simulator; G6/fullgoal open.

R220 active benchmark handle:14067. Poll SAME14067; no restart/bootstrap during compile.

R220: FP routing oracle85294 FINISHED0. --kernels --fp-routing uses pinned current kernel reference/candidate with actualhelpers;357directFP-disabled entries (119PCsx3budgets) preservefaultCIA, plus1440wholekernel cases/624yields/480FPfaults/480illegal/192interruptions/96callerreturns/18816callbacks/34688journals. All4sanitized/optimized variants digestee02615b68d66d1e. Not exhaustive arbitrary FP states. OfflineABBA benchmark started generated/fp-routing-bench-r220.log; poll its returned session, no product/module build. Acceptedappunchanged/no game/Simulator, G6/fullgoal open.

R219: isolated checked-entry/FP-ready-fallthrough prototype prepared, NOT compiled/promoted. Source-pinned probe-fp-check-routing.py identifies119 adjacent arithmetic edges inside two kernels only. Normal path sets nextPC then bypasses repeated availability check; original labels/PC assignments/checks remain for every direct entry. Reversing insertions recovers original source exactly. CandidateSHAad83b55033d700b1ce5f57db07dfb66bda2e66bc8bdb839ca3cf407004a28918 at generated/fp-check-routing-r219/candidate.c. Next actual-helper whole-kernel/direct-entry fault equivalence before assembly or timing; no memory/callback/check hoisting. App unchanged/no runtime/build/Simulator; G6/fullgoal open.

R218: offline guarded MEM1 lookup probe passes1.6M actual-header pointer/offset/null-output comparisons O2ASanUBSan for initialized Wii layouts, aliases/edges/nullEXRAM. Exact sourceSHA pinned. Assembly guard replaces EXRAMpointer load with extra address/size comparisons, expands fallback; no compelling simplification, parked without benchmark/fullmodule/productchange. Probe tests/probe-mem1-lookup.py/log generated/mem1-lookup-r218.log. Next inspect repeated FP availability checks across adjacent no-memory/no-callback arithmetic, preserving faultPC and every callback boundary; this is separate from acceptedFPRF classification policy. No game/build/Simulator; G6/fullgoal open.

R217: callback contract regression passes O2 ASanUBSan against actual cpu.h. External read can mutate RAM/MSR; next read must use new mapping. Journal remap occurs after pointer acquisition: current store retains old pointer, subsequent store uses new mapping; reservation clear preserved. Field offsets320=exception,344=reserve_valid confirmed. Blanket metadata hoisting rejected. Fullsuite80741 FINISHED0 before new mapping test; mapping test separately passes/added suite. Next bounded MEM1-vs-MEM2 lookup-order feasibility: current get_ram_ptr always checksEXRAM first even THP MEM1 accesses; inspect guarded semantics and offline code/correctness before product change. App unchanged/no runtime/build/Simulator; G6/fullgoal open.

R216: sampled-PC instruction join added/tested (classify-cpu-instructions.py, test-cpu-instruction-classifier.py added to suite; fullsuite not rerun). All selected PCs resolve in exact asm; kernel load samples6069/7913 (~76.7%), stores334,calls216,branches289,other1003,scalarFP2. These are PC attribution, NOT cost percentages. x19 initialized fromCPUState argument in all3functions; dominant offsets MSR298,RAM/exRAM metadata d80/d88/da0/da8 plus320/344. Next audit alias/callback mutation contract for repeated metadata loads before any guarded reuse; preserve every fault/journal/cycle boundary. No product change/runtime/build; G6/fullgoal open.

R215: exact signed-binary disassembly checked against R214 rawPCs (align low marker bits). Kernel samples diffuse:7913 across2731sites,top10=313 (~4%). Hot kernel0 5789b4c PC/cycle/FP guard,5784738 cycle updates; kernel1 578fd00 PC/cycle/FP guard. Decoder57aff90 follows existingCLZ ladder (already parked);57b0028 PC/cycle then memory access. Sampling skid prevents per-load cost inference. Saved hot-functions.asm for exact5c21...e91d. Next aggregate kernel instruction families/call boundaries across all sampled sites to quantify repeated bookkeeping before a distinct specialization; no repeat CLZ or isolated-PC tweak. No product/runtime change, G6/fullgoal open.

R214: fresh signed-package CPU profile captured/exported/summarized. Runtime93799/trigger36277/capture5912/export63997 FINISHED0. Ten-second CPU Profiler attach PID62089, current movie visibly advancing; clean close/native-only/SMCfailed0/NANDa574...afa6 unchanged. 31295CPU samples: kernel0=5112,kernel1=2801 (~25.3%combined),func804530A0=5015 (~16%),convert_to_double1517,ps_add1372,ps_sub1203;31248Pcore/47Ecore. Inlining shifts attribution, not direct old-profile speed comparison. Evidence runtime/thp-profile-r214/{cpu.trace,cpu.xml,summary.json,capture.log,runtime.log}. Next exact-binary instruction-range attribution inside kernels and decoder before distinct optimization; no blanket QoS/renderer fix or unchanged benchmark repeat. Accepted app unchanged/no runtime/Simulator/build; G6/fullgoal open.

R213: signed packaged module5c21...e91d smoke passes. Fresh real-save profile thp-package-r213, no savestates/phase trace. Runtime3367/load11508/move49481 FINISHED0: title/ordinary one-star Observatory load/visible movement/clean close, fallback0/smc_failed0/NAND5040...64a6 unchanged. Whole153.7s3underruns5backlogs not audio/soak acceptance. Promotion complete; no game/Simulator/build/test remains. Next one targeted CPU profile of current canonical movie to identify residual cost after kernel extraction (not unchanged FPS retest), preserve accepted app. G6/full PRD performance/audio/story/mobile/menu scope remains open.

R212 suite completion: 89902 FINISHED0; generated/check-r212.log ends Repository safety checks passed. No tests/build/game/Simulator remain. Next signed packaged-module save-load smoke.

R212: canonical module PROMOTED locally. Added build-macos-app.sh --module-only: stage existing app, replace selected audited module, sign, require unchanged wrapper/runner/frontend, audit before swap, retain backup. Package26460 FINISHED0/audit/signatures pass; signed module5c21010733a5cb3cf8231853f96963e3d433796c062106fdaf6b4261fe0be91d, unsigned1180...c631. Wrapperdbc8...0124/runneraffb...e295/frontend61de931aafa359c9263d5faecc43a78cff5fee96cac246b00d423804dcbe1750 unchanged. Previousapp generated/macos/GalaxyPad.app.previous.20260907T023102Z. Normal marker now canonical modules-thp-r205/...-daa33a86eff05b70. Fullsuite ACTIVE89902/generated/check-r212.log; poll same, no bootstrap. Next signed packaged-module ordinary save-load smoke after suite completes. No game/Simulator/build; G6 performance/audio/full PRD still open.

R211: fresh accepted control55214/trigger25369 FINISHED0. SameR85/phase-only/native1x/Metal fixedminute3226VIframes=53.7667FPS,p9920.397166ms,80gaps>=20ms,DMA28.6997333kHz. CanonicalR21055.3167 improves2.883%,17longgaps. Supports canonical promotion, not60Hz/audio acceptance; no unchanged third timingrun. Baseline movie visibly completes/plaza, cleanclose/fallback0/smc_failed0/NANDa574...afa6 unchanged; whole218.4s116underruns3backlogs not fixedwindowaudio. Next promote verified canonical module through normal selection/package preserving accepted runner/frontend identities (bootstrap rebuilt desktop tools, do not silently swap runner). Read packaging script fully and verify exact inputs before mutation. Normalapp/marker stillunchanged, no game/build/Simulator; G6/fullgoal open.

R210: canonical1180...c631 fixed R85 movie runtime57735/trigger69378/move1757 FINISHED0. Fixedminute3319frames=55.3167FPS,p9919.602916ms,17VIgaps>=20ms,DMA29.5338667kHz. Movie visibly completes to plaza, movement works, cleanclose/fallback0/smc_failed0/NANDa574...afa6 unchanged. Whole241.5s86underruns7backlogs not fixed-window audio acceptance. This is ~2.85% above R201 accepted53.7833, but not fresh paired control; canonical vs experimental binary differs. Next one fresh accepted control with identical profile/trace/settings to decide canonical promotion; do not repeat canonical unchanged. Normal app unchanged/no game/build/Simulator; G6/full goal open.

R209: canonical build28332 FINISHED0, audit passes ARM64/macOS14/1322chunks/19SMC. Module1180447313459c4c153ca74e5215811e88a9b69a00d15feff940f062148fc631,114404568bytes; manifest FPRF119/THPkernels2/source28d765f74af57637/originalPGO correct, both kernel symbols present. Isolated untraced runtime38114/load65336/move76429 FINISHED0: title to ordinary one-star Observatory load, native pause/resume, visible movement, clean close; fallback0/smc_failed0/NAND5040...64a6 unchanged. Whole137s8underruns9backlogs includes deliberate12.45s pause, NOT performance/audio acceptance. Canonical binary differs from experimental2c29...bbad8 despite exact chunk parity; next fixed R85 movie test on canonical artifact before normal selection/package. No game/Simulator/build, normal app unchanged, G6/full goal open.

R208: SAME28332/59544 verified live through additional bounded waits; linker observed5:22/~626%CPU, no terminal error/restart. Re-hashed accepted wrapper dbc8...0124, runner affb...e295, original PGO f39a...460d and prepared NAND5040...64a6; all unchanged. Runtime test stays one-variable canonical module plus accepted runner. No app selection or runtime change. Next same build poll then artifact audit and prepared-profile launch; G6/full goal open.

R207: verified wait on SAME28332. Compilation reached1330/1332; linker PID59544 confirmed live at3:19 elapsed/~683%CPU/~1GiB RSS, 6.8GiB disk available. No error; single expected out-of-date PGO function warning retained. No restart, bootstrap, runtime or package change. Next poll SAME28332 until terminal, audit artifact and manifest at modules-thp-r205/...-daa33a86eff05b70, then use prepared thp-canonical-r206 profile. G6/full goal open.

R206: SAME build28332 verified live and advancing (701/1332 at check), not restarted. Whole generated-directory diff against accepted FPRF output identifies ONLY chunk1102; headers/SMC/all other generated files unchanged. Fresh isolated runtime/thp-canonical-r206 prepared from midblock-r145 Config/Wii/config.ini, pipe configured, no savestates; NAND SHA5040acdd95157448d660fd02f03c16c17e240523bdfa889ccbd253f9fe5364a6. Settings Metal/native1x/CPUThreadTrue. No game or booted Simulator; normal app/marker unchanged. Next poll28332 through link, audit exact canonical module/manifest/symbols, then launch it explicitly with this isolated profile and accepted packaged runner. G6/full PRD open.

R205: canonical module build ACTIVE session28332, generated/module-thp-r205.log, separate generated/modules-thp-r205 cache key daa33a86eff05b70. Fresh emitted chunk1102 matches tested kernel candidate byte-for-byte after header-include normalization (cmp exits0). Initial comparison accidentally replaced comment line1 instead of include line2; corrected normalization, not a source change. Original PGO retained. Poll SAME28332 through link, then audit exact artifact/manifest before any runtime or selection. No game/Simulator; normal app/marker unchanged. G6/full goal open.

R204: canonical THP policy is now applied through bootstrap. SHA-pinned peel/restore/apply ordering preserves the existing FPRF policy; bootstrap and repeat both pass (generated/bootstrap-r204{,-repeat}.log). New source-level wiring regression verifies ordering, cache identity, manifest, and patch pin. Full repository suite ends with Repository safety checks passed (generated/check-r204.log). Port build completed; a subsequent incremental build exits0 with no compilation remaining (upstream ScmRevGen emits nonfatal bad revision ^master). Canonical module reproduction is the next gate; normal app and normal module selection remain unchanged. G6 performance/audio and full PRD remain open.

R203: canonical policy prepared/tested, NOT applied. thp-kernel-policy.inc exactRMGE01/DOL/C/1024 policy rmge01-thp-kernels-2-v1, postFPRFsourceSHAf2d...bd61 guard,584entry/branch closure and restore checks. test-thp-kernel-policy.py79006FINISHED0 ASanUBSan, byte-exact parity with tested98d...8991 (normalized include); wrongidentity/hash/reapply/label/branch/entry guards pass. New0016-rmge01-thp-kernels.patch SHAef25620e8ec254b1c5eecf2bfa386ad60c06f085ac3cca0a1996cba611cf8f6f adds policy file, cache/manifest thp_policy before lookup, invokes afterApplyGalaxyFprf. Initial zero-context patch rejected; added3linecontext, standard gitapply--check now passes. Next bootstrap pin/peel/restore/apply wiring and idempotency before compiledtool/canonical module build. App/vendor unchanged; no runtime/Simulator/build, G6/fullgoal open.

R202: candidate untraced real-save/lifecycle regression passes. Runtime50119/load91852/move18112allFINISHED0; ordinarytitle/file-select loads one-star Observatory withoutsavestate, pauseindicator appears/resume clears and movementvisibly relocatesMario/camera. Cleanclose/fallback0/smc_failed0/NAND5040...64a6 unchanged. Whole326.6s18underruns17backlogs includes deliberate56.37spause, NOT sustained performance/audio acceptance. Candidate2c29...bbad8 stillunselected/appunchanged. Next canonical kernel policy AFTER existing119siteFPRF transform, separately keyed cache/manifest policy and sourcehashguard; compare generated output with tested98d...8991 before bootstrap/build. Preserve existingFPRFtests/helperpolicy, no copying experimentalbinary into acceptedcache. No runtime/Simulator/build; G6/fullgoal open.

R201: fresh accepted phase-only control91529/trigger20958FINISHED0. SameR85/native1x/Metal fixedminute3227frames=53.7833FPS,p9920.2855ms,65gaps>=20ms,DMA28.7168kHz. CandidateR20055.7833 gains3.7186%, gaps29; supports retaining candidate for regression/integration, not60Hz/audio acceptance. No unchanged third timingrun now. Baseline movie visibly completes/plaza, cleanclose/fallback0/smc_failed0/NANDa574...afa6 unchanged; whole382s108underruns5backlogs not fixedwindowaudio. Candidate stillunselected/appunchanged. Prepared fresh real-one-star runtime/thp-save-r201 from midblock-r145 Config/Wii/config.ini, no savestates, NAND5040acdd95157448d660fd02f03c16c17e240523bdfa889ccbd253f9fe5364a6. Next candidate untraced title/file-select/real-save load/pause-resume/movement/close before canonical integration. No game/Simulator/build; G6/fullgoal open.

R200: same link73103FINISHED0/auditpass; candidate2c29e27fa245b3b4bba41519204b6dca927feee26368a4a27f5876cc2e6bbad8,114421048bytes (+98864 vs accepted), both kernel symbols present. Runtime26619/trigger5906/movement72734 allFINISHED0. FixedR85minute3347frames=55.7833FPS,p9919.84825ms,29gaps>=20ms,DMA29.7813333kHz. Movie visibly completes/plaza, movement changes position/camera, cleanclose/fallback0/smc_failed0/NANDa574...afa6 unchanged. Whole379.8s75underruns7backlogs NOT audio acceptance. Candidate unselected/app unchanged; earlier54.5 control is not fresh paired proof. Next fresh accepted R85/native1x/Metal/phase-only control (no host recorder, matching candidate) before promotion/parking decision. No game/Simulator/build remains; G6/fullgoal open.

R199: caller/fault-PC gates pass and candidate link ACTIVE73103. Expanded wholechunk oracle1440cases/624yields/480FPfaults/480illegal/192interruptions/96callerreturns/18816callbacks/34688journals/1440reservationclears, digest882be09b1f38e9ad, all4variants18609FINISHED0. Initial5421 fixture stopped at internalLR; corrected stopping rule, no product bug. Actual-wrapper ThinLTO ABBA45069FINISHED0 A26793.75/B24823.60/B24719.30/A25894.15:5.97% mean gain, text131072->229376 (+96KiB). New --thp-kernels option in pinned onechunk builder preserves originalPGO/1328objects;73103 compiling/linking generated/thp-kernels-r199/gRMGE01_recomp.dylib. Linker52188 verified38s/~671%CPU; expected1of33function profile mismatch ignored, not suppressed. Poll SAME73103, no restart. Prepared fresh R85 runtime/thp-kernels-r199 slot/NAND hashes verified; no launch until link/audit complete. App unchanged/no game/Simulator; G6/fullgoal open.

R198: private kernel chunk prepared and initial wholechunk oracle passes. extract-thp-kernels.py pins accepted FPRF source;584trampolines preserve original external switch charges, kernels omit duplicate entry charges while retaining original body/loop charges. bool return distinguishes early helper/yield exit from guestblr before original outer return dispatcher. Final generated/thp-kernels-r198-exits/candidate.c SHA98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991; referenceSHAf288241d6699aa3344ed7470bab69edd1b5f54fdae392010038bc786f721327f. Initial void-return r198 artifact superseded/uncompiled. --kernels83114FINISHED0 all4reference/candidate variants864cases/digestaa72b761a9c075fd; actual completechunk used, not extractedbody-only. Tests still sentinelLR, not exhaustive584arbitrary-entry/caller-continuation coverage. Next add returning-into-caller and fault-PC tests before onechunk candidate link; no app/module/runtime/Simulator change. G6/fullgoal open.

R197: separate-TU ThinLTO flatten feasibility passes. --flatten-lto preserves separate actualCPU/float/exception sources, only two transform attributes changed. Benchmark68614FINISHED0 A26997.55/B24434.70/B23704.95/A26947.00:10.76% lower transform time, text98304->196608 (+96KiB). Correctness48937FINISHED0 all4reference/candidate O1sanitized/O2+ThinLTO864cases/digestaa72b761a9c075fd. Logs generated/thp-flatten-lto-{bench-r197,r197}.log (actual correctness name thp-flatten-lto-r197.log). Audit confirms caller80452554 usesinternalgoto: extracted kernels must retain outer external-entry suffix charging, omit duplicate kernelentry charge, set PC on trampoline, preserve return dispatcher/584interior labels, stay noinline at outer boundary while flattening helpers. Next source-pinned isolated kernel extraction+wholechunk dispatch/cycle oracle before module link; no duplicatedglobals. No app/module/runtime/Simulator change; G6/fullgoal open.

R196: transform-local flatten prototype positive offline, unpromoted. --flatten compiles actual CPU/float/exception sources in same TU for both control and candidate, adds flatten attribute only to two extracted transform functions. All864cases/reference+candidate O1sanitized/O2 match digestaa72b761a9c075fd (76534FINISHED0). ABBA93793FINISHED0 A28781.95/B25495.70/B25567.95/A28896.65:11.47% lower transform time. __TEXT81920->180224 (+98304bytes,+120% entire benchmark text), so code footprint is a real risk, not assumed game gain. Logs generated/thp-flatten-r196.log and thp-flatten-bench-r196.log. Next test attribute with separate-TU ThinLTO matching module architecture before designing any isolated module candidate; no naive CPU/global duplication or blanket inline changes. App unchanged/no game/Simulator/build; G6/fullgoal open.

R195: exact force25 identity shortcut tested then parked. --identity-c creates temporary float source only, returns operand unchanged when low28bits arezero; original path retained otherwise.12,582,912 bitpattern checks/6,094,848 guarded identities pass O2 ASanUBSan; standalone initial missing leading-zero helper corrected by extracting actual helper. Full864case transform oracle all4reference/candidate variants unchanged digestaa72b761a9c075fd (98564FINISHED0). ABBA23931FINISHED0 sums A29832.7/B30058.95/B29499.5/A29805.2: only~0.133% average reduction, one candidate sample disturbed, no robust gain. No selective outlier removal/full link/promotion/unchanged repeat. Artifacts generated/{25bit-identity-r195-fixed.log,thp-identity-c-r195.log,thp-identity-c-bench-r195.log}. App unchanged/no runtime/Simulator/build; G6/fullgoal open. Next larger transform-level specialization or measured scope evidence, not more standalone scalar-helper tweaks.

R194: fresh accepted494c...3fbe R85 movie with phase+host correlation. Runtime88867/trigger81216/recorder43772 allFINISHED0. Fixedminute3241frames=54.0167FPS,p9920.416708ms,59gaps>=20ms,DMA28.8405333kHz.13overlapping5s host intervals show zero swapins/swapouts/pageouts/compressions, pressure78–79%, unchanged701.62MiBswap. Active paging does not explain this run; prior22FPS/thermal/background contention not fully attributed. Movie visibly completes to plaza, cleanclose/fallback0/smc_failed0/NANDa574...afa6 unchanged; whole199.1s104underruns5backlogs not audio pass. Added absolute raw/monotonic/wall timestamps to host recorder (raw aligns phase clock). Artifacts runtime/host-correlation-r194/{phase.csv,host.jsonl,measurement.json,correlation.json,runtime.log}. App unchanged/no game/Simulator/build. Next return to larger decoder work; paging workaround not justified,12site candidate remains offline. G6/fullgoal open.

R193: host-resource attribution check/tooling. Current idle-game host16GiBRAM, swap701.62MiB allocated, disk8.0GiBfree. New read-only record-host-pressure.py captures timestamped VM counter deltas/pressure/swap/thermal warnings/process load; parser test passes.6second3sample run15844FINISHED0 shows zero swapins/swapouts/pageouts/compressions, pressure command reports79% throughout. Thus no active paging observed in this idle interval, not evidence about prior22FPS or loaded gameplay. Background reported CPU exists; no unrelated process/settings changed. Private generated/host-pressure-r193.jsonl. Next fresh accepted R85 gameplay with synchronized phase+host samples to distinguish loaded contention from decoder cost before more experiments. No game/Simulator/build; app unchanged, G6/fullgoal open.

R192: offline ABBA timing77709FINISHED0.12equally weighted transform/pattern cases x20000iterations; excludes setup/hash, includes CPU reset/yield/output callbacks. Reference totals30031.95/29899.30ns, candidate29036.65/28943.70ns;3.255% lower transform time, NOT FPS gain or final-PGO evidence. Timing-mode regression11797FINISHED0: all4reference/candidate O1sanitized/O2 variants still864cases/digestaa72b761a9c075fd. Logs generated/thp-merge-bench-r192.log and thp-oracle-r192-regression.log. Candidate retained offline/unpromoted; modest isolated gain does not justify full link alone. Next pursue a larger decoder optimization boundary or establish weighted end-to-end relevance before integrating12sites; no unchanged repeat benchmark. App unchanged/no game/Simulator/build; G6/fullgoal open.

R191: first isolated transform candidate passes oracle. --merge-fprf in probe-thp-oracle.py removes12 additional FPRF classifications across exact register-only ps_merge shapes, stopping at all unrecognized/control/memory boundaries and requiring a later actual writer. Existing arithmetic/helpers/entry charges remain. Reference and candidate each O1 ASan/UBSan and O2 all864cases match digestaa72b761a9c075fd;68000FINISHED0, generated/thp-merge-fprf-r191.log. No app/module change or speedup claim. Next offline matched execution timing excluding harness hashing/setup before deciding whether12sites justify integration; no full link without worthwhile measured benefit. G6/fullPRD open.

R190: extended transform oracle passes864cases under O1 ASan/UBSan and O2 strict-FP:432yields,288FP-unavailable faults,288LSQE-disabled illegal exceptions,96callback interruptions,12480output callbacks,17152pre-write journals,864reservation clears; digestaa72b761a9c075fd. Full normalized CPU state now captured at callbacks/journals/every exit, plus pre-write bytes and final RAM/LC. Two GQR5/6 settings; zero blocks128/255 as expected. 52883FINISHED0, generated/thp-oracle-r190-interrupt.log. No faster implementation or module/appchange. Next bounded transform specialization against this oracle and offline timing before any costly module link; don't repeat entry-split or generic finite-helper experiments. Callback interruption is synthetic host-state mutation, not a modeled architectural memory fault. G6/fullgoal open; no runtime/Simulator/build,7.9Gi free.

R189: offline exact-generated transform oracle now runs. tests/probe-thp-oracle.py pins accepted chunk/CPU/float/header, preserves all interior entry charges and yield paths, uses sentinel LR outside chunk. O1 ASan/UBSan and O2 strict-FP agree:96 cases,84 yields,48 FP-unavailable faults,3072 output callbacks,digest4a471989ef100135. Zero block produces64 neutral128 pixels;48 successful blocks restore stack/f25–31. Initial compile missing generated header fixed; fixture HID2 LSQE missing caused expected illegal instruction, corrected fixture (not game defect). Evidence generated/thp-oracle-r189-lsqe.log,63083FINISHED0. No specialization/performance claim/appchange. Next expand oracle with LSQE-off, GQR variations, memory journals/reservation and callback-exit state before candidate math/local-state specialization. G6/fullgoal open; no game/Simulator launched.

R188: exact-DOL THP boundary audit completed, no runtime change. New script verifies both inverse-DCT regions (804526e8/1164 bytes, 80452b74/1172 bytes): eight conditional branches each, no calls/outside direct edges, only final indirect return. Petari Korean symbols are correspondence guides only. THP-BOUNDARY-AUDIT.md records stack/FPR/GQR/workspace/output/exception/timing contract and exact hashes. Next offline generated-instruction oracle for valid block inputs and observable state before any specialization; no generic decoder swap or arbitrary cycle charge. Audit passes, generated/thp-boundaries-r188.json; accepted package unchanged, no game/build/booted Simulator. G6 performance/audio and full PRD remain open.

R187: fresh accepted control98930/trigger57920 FINISHED0, identical R85/native1x/Metal/phase window.3270frames=54.5FPS,p9920.070333ms,38gaps>=20ms,DMA29.0986667kHz. Candidate55.25 only+1.376% vs currentcontrol (not historical53.6); park/unpromoted, insufficient benefit for extra code/profile complexity. No unchanged third timing run. Baseline movie visibly completes, cleanclose/fallback0/smc_failed0/NANDa574...afa6 unchanged; whole299.8s105underruns/5backlogs not audio acceptance. App stays acceptedFPRF14ea...f184, no game/build/Simulator. Next larger THP decoder-boundary feasibility audit: exactRMGE01 function/ABI/state/memory/timing sideeffects before considering native algorithm-level replacement; no speculative HLE or discarded correctness. Preserve G6 performance/audio and full story/mobile/menu scope.

R186: build1613 FINISHED0/auditpass, candidateSHA aff3f3ec52d7e6cdb9f138fed2b056e77054b1340c5b7ad725cdee970da4a289,114404792bytes vs114322184 (+82608). Isolated runtime54348/trigger11390/move81147 allFINISHED0. Exact R85/native1x/Metal/phase policy fixedminute3315frames=55.25FPS,p9919.627375ms,17gaps>=20ms,DMA29.4954667kHz. Movie visibly completes into plaza, movement works; cleanclose/fallback0/smc_failed0/NANDa574...afa6 unchanged. Whole282.7s93underruns/10backlogs NOT audio pass. Promising vs historical53.6 but not fresh pairedcontrol; next current accepted FPRF module same profile/fixture/policy control before gain or promotion claim. Artifacts runtime/chunk-entry-r185/{phase.csv,runtime.log}; app/normalmarker unchanged/no game/build/Simulator. G6/fullgoal open.

R185: verified existing build1613 live, linker46787 observed1:18→2:22 elapsed/~680–706%CPU, no restart/error. Fullsuite15883 FINISHED0, generated/check-r185.log. Fresh runtime/chunk-entry-r185 copied exact R85Config/Wii/slot3, pipe configured; slotaea2...7ab8/NANDa574...afa6 verified, no launch. Added explicit sourceSHA guards to test-chunk-entry.py so future runs cannot silently compare changed private variants; hash checks and py_compile pass (no semantic harness change).8.3Gi free. Next pollSAME1613 through link/audit, inspect candidate binarySHA/size then single-game matched R85 phase run using accepted runner; no build overlap. App/normalmarker unchanged/no game/Simulator; G6/fullgoal open.

R184: expanded tests/test-chunk-entry.py to32768cases with journal callback snapshots and active reservation state, plus --optimized O2/ThinLTO.82961optimized/83417ASanUBSan bothFINISHED0: capped0,170262journal events/283reservation clears each, fullstate/memory/callback parity. New source-pinned build-chunk-entry-experiment.py preserves accepted module494c...3fbe, candidateSHA d248002b3b8021c79cd6b2c4ea1d15f015dd0b447b31fe060d54354dd45fe32b, originalchunk e6aa...6dcc, originalPGO f39a...60d. Reads exact Ninja flags/1329object graph; reuses1328 and compiles1, records hashes/commands/experimentalmanifest, never selects. Build1613 ACTIVE, generated/chunk-entry-r184-build.log; pollSAME through compile/ThinLTO link/audit. No game/Simulator/appchange. Next linkedsize/identity audit then isolated exactR85movie test only if artifact valid; profile coverage penalty remains, no performance promise. G6/fullgoal open.

R183: added tests/test-chunk-entry.py executing complete reference/candidate chunks in separate TUs against actual CPU/memory headers. Fixed run85607 FINISHED0:16384 comparisons (1024entries x4modes x4trials), fullCPUState/returned PC/downcount/memory bytes/ordered callback snapshots agree, capped=0, ASanUBSan. Callback modes include GPR/XER/exception-field mutation; directRAM-seeded and randomaddress cases, downcount0/-257. Initial76847 failed in unchanged get_ram_ptr because harness RAMnull/size0 violated initialized-MEM1 precondition; corrected allmodes valid4096byteRAM, not product fix. Evidence generated/chunk-entry-r183-fixed-test.log; failedlog retained. No JIT/module/game/promotion. Next extend actual test to optimized compile/journal/reservation coverage or isolated one-chunk link using exact accepted objects/flags; source-body parity plus tests do not prove runtime gain, and R182 profile/code-size penalties remain. App unchanged/no build/game/Simulator; G6/fullgoal open.

R182: scripts/probe-chunk-entry.py isolates exact chunk1103 into intact noinline suffix fallback plus normal copy with195 leader cases (829 interior cases route unchanged fallback;1024 total). Asserts original fallback and all post-entry normal instructions byte-exact; this is NOT whole-CFG execution proof. Source/header/module untouched; outputs generated/chunk-entry-r182. Actual-flag pre-link assembly85259 FINISHED0: reference12233instructions/1441loads/790stores; candidate normal17934/3772/1422 plusfallback21512/5168/2376, compiler reports missing candidate profile. Explicit profile-free control61548 FINISHED0: reference22098/5302/2440, normal17987/3775/1442 +fallback21562/5177/2384. Normal~18.6%smaller but total~79%larger; counts static, not FPS, and -flto removed only for readable pre-link assembly. No candidate module/game/promotion. Next full-chunk differential harness covering1024 entries/callbacks/loop exits/PC/downcount before any isolated link; assess code-size/profile penalty, not automatic promotion. App unchanged/no runtime/build/Simulator; G6/fullscope open.

R181: isolated tests/probe-block-entry.py extracts SHA-pinned actual80453AAC–AB8 instructions+four entry cases, compares existing multi-entry with normal-entry helper/separate suffix fallback.400000 full CPUState/branch-target/cycle comparisons pass ASanUBSan; initial independent expected-cycle assertion had unsigned test arithmetic, corrected cast (implementation parity already passed). generated/block-entry-r181.log has O2 assembly. Static reference65instructions/13loads/8stores, normal37/5/5, routing6/1/0; NOT dynamic speedup (reference counts all suffix paths, helper adds routing). Clear normal-path evidence: cntlzw result retained for cmp rather than reloaded gpr12. No exception/memory/call path in selected block, no full CFG/game proof. Next isolated whole hot-chunk normal/suffix routing prototype, preserving every instruction entry/downcount and existing callbacks/branches; compile/inspect real chunk code size before module build. Actual generator path ref/ModernGekko/vendor/dolphin/DolRecomp/src/backend/{emitter,c_cfg}.c; no ref/DolRecomp root. Product unchanged/no build/game/Simulator, G6/full goal open.

R180 suite update: full regression85982 FINISHED0, generated/check-r180.log. No build/game/Simulator remains.

R180: added offline scripts/summarize-cpu-profile.py with synthetic id/ref/exclusive-leaf/zero-weight/range/empty-export tests, focused pass; added test to suite (fullsuite not rerun yet). R179 raw XML analysis reproducible at summary-r180.json/decoder-r180.json. Selected store helper ranges: entry322, lane0address565/lane1address310 (~2.8% CPU combined), bookkeeping178/233, conversions0/107, epilogue171; sum1886 vs symbol1910 includes other copies. Specific CLZ region827 (~2.7%), flags91/branch152. Samples may skid; zero conversion samples do not mean zero cost. No repeated rejected micro candidate. New structural hypothesis: per-instruction external switch predecessors inhibit normal-path register-state optimization; actual hot block80453AAC–AB8 has external entry at each instruction plus repeated GPR/XER/CR stores/loads. Next isolated emitted-code experiment comparing normal block vs separate interior-entry suffix route, retaining full CPU state, every entry, cycle charges, exceptions and CFG semantics; inspect optimized assembly before broad emitter/module change. No product change/game/build/Simulator; G6 open.

R179: instruction-level profiler route now proven. xctrace CPU Profiler preflight14617 saved trace (exit54 because launched sleep was killed at time limit; export23590 succeeds). Actual game attach46155 FINISHED0/10s capture; runtime6707/trigger80136 FINISHED0, visible advancing movie, clean native-only close/NANDa574...afa6 unchanged. cpu.xml/thermal.xml exports65846/47377 succeed in generated/runtime/movie-instructions-r179. CPU31081samples,31054 P-core/27 E-core (>99.9% P); OS thermal Fair entire10.875s capture, no proof of clock throttling. Top exclusive5031func804530A0/3618func804520A0/1910psq_store_inline, raw PCs now available. Module base0x134a70000, leaf address format has low-bit marker (retain raw; ARM instruction decode aligned separately). Top paired-store raw relative0x578966d=320samples,0x5789601=265: actual aligned instructions load MEM2 pointer and GQR, not epilogue. Decoder0x579cf3d274/0x579cfd5272. Next aggregate actual instruction ranges and cycle weights for decoder/paired memory guards before choosing a distinct candidate; do not repeat rejected CLZ/type0RAM/PGO/global-inline. App unchanged/no game/build/Simulator; G6/full goal open.

R178: fresh untraced post-FPRF movie diagnostic completes. Runtime57312/trigger30876/sample20989 allFINISHED0; movie visibly advances, intentionally closed during movie after capture (not completion test). movie-profile-r178/cpu-sample.txt: CPU7509samples, Run7283 inclusive/dispatch6921; exclusive sum7509, func804530A0=1128/804520A0=896, psq_store_inline443/load_inline334/convert_to_double332/psq_store302/add293/sub292/madd202; full list in PERF. Native-only clean close/savea574...afa6 unchanged,145.2s81underruns/4backlogs, not timing acceptance. Actual signedmodule base0x133f04000; sampled804530A0+79220 resolves0x579cf3c at end of CNTLZW compare cascade, followed by flags and guarded memory lookup. This is the previously investigated coefficient-decode region, NOT a new CLZ hypothesis; retain prior rejected CLZ/PGO decisions. Symbol-collapsed sample groups many instruction offsets, so no exact per-instruction cost proven. Next obtain bounded raw-address CPU sample or equivalent instruction histogram to distinguish hot register/flag/memory overhead within804530A0 before another candidate. No app/source change, runtime/build/Simulator remains; G6/full goal open.

R177: package64332 FINISHED0, audit72877 passes signatures/module/package. Signed runner affbcb51f27f853b0b5ee403b5033c3bd5a6f7ea3e514b969c2ef4272af9e295 unchanged; signed module14ea8867e2b0a47caf761b2ba24ff608cd39a27b1e9290dbc2302f6d4651f184. Previous app preserved at GalaxyPad.app.previous.20260906T232128Z. Actual packaged-wrapper untraced smoke37922 FINISHED0 with fprf-canonical-r175/no savestate: ready title, save-load53317 visibly reaches one-star Observatory, pause indicator/resume animation verified, right45847 moves Mario/camera, clean close. fallback0/smc_failed0/NAND5040acdd...64a6 unchanged. Whole156.4s9underruns/8backlogs includes deliberate12.5s pause; NOT audio/60Hz acceptance. FPRF optimization now packaged/compatibility-validated. No build/game/Simulator remains. Next fresh diagnostic CPU sample in same R85 heavy movie on this exact package to attribute remaining hotspots after119-site change; no more unchanged timing pairs. Korean Petari symbols are clues only, not exact RMGE01 addresses. Full G6/performance/audio and later story/mobile/menu scope remains open.

R176 update: selection82587 FINISHED0/cache-hit27fc425ac63117e7; fullsuite36660 FINISHED0/repository safety passed. Normal module marker now canonical. Package build64332 ACTIVE, generated/package-r176.log; poll same handle, preserve previous app and validate newly packaged runner before acceptance. No game/Simulator.

R176: canonical build2122 FINISHED0; module audit5001 passes. Binary SHA494c2a71d16963cf720af228ff8b9323a1d5b2967776cb759aa11f161beb3fbe is EXACTLY identical to measured R169/R171 experimental module. Manifest source fingerprint28d765f74af57637, policy rmge01-fprf-119-v1, cache27fc425ac63117e7, originalPGO. Thus no redundant explicit-module smoke needed with unchanged accepted runner; packaged-wrapper smoke still required after packaging. Two private experiment tests now pin historical source path+SHA instead of mutable active marker;39259 passes policy and64800 actual-chain comparisons. Copied canonical module/manifest and generated symlink into new normal cache (no old artifact overwritten). Normal selection82587 ACTIVE, generated/module-select-r176.log; fullsuite36660 ACTIVE, generated/check-r176.log. Poll both before packaging/bootstrap. App unchanged; no game/Simulator. G6 performance/audio remain open; current gain53.6 vs51.5/51.6833 does not explain all observed22FPS episodes or prove60Hz. Next finish selection/suite, package (standalone runner was relinked, validate exact packaged artifact), smoke real-save/input/lifecycle.

R175: same canonical build2122 ACTIVE,1275/1332 observed; no restart. Corrected R171/R174 documentation: runtime-source fingerprint lives in cache identity/manifest, NOT module export ABI. module_export.c exposes ABI/game/guest code tables, no source fingerprint. Canonical changedchunkSHAf2d6911016e8e1c9f46caf5ee97dece58689f5b5f51397860bb868383c34bd61. Prepared fresh untraced real-save profile runtime/fprf-canonical-r175/Pipe, NAND5040...64a6 verified, no savestate/no launch. Next same2122 link, manifest/cache/ABI+binaryhash audits, then explicitcanonicalmodule with accepted packagedrunner. App/normal marker unchanged, no game/Simulator; G6 open.

R174: port17259 FINISHED0; toolSHA c83d7fed4abba224a0b9e5e53fbc65cfa3f1e925a3dfc98e54b1f4016dbb3dd1. Its dependency graph also relinked standalone moderngekko-run; packaged runner unchanged and must be used for first canonical validation. Canonical module2122 ACTIVE, generated/module-fprf-r174.log, isolated modules-fprf-r174/RMGE01/<DOL>-27fc425ac63117e7. Newcache/no oldhit, originalPGO. Regeneration diff proves1321chunks identical and only804520A0 changed with119deferredcalls. Normal selection/app untouched. Next pollSAME2122 compile/link/audit, verify published manifest policy/source identity then smoke exactartifact.9.8Gi available beforebuild; no game/Simulator. G6 open.

R173: bootstrap integration applied with peel/restore/order/scope/hash pins. First+repeat pass94019/97618. Initial portbuild38342 failed missing<regex>; fullsuite62132 passed meanwhile, plus canonicalpolicy/exact64800candidate tests. After tests terminal, reversed onlyoldpolicy, addedinclude tocanonicalpatch; NEW policySHA881996463a31728375b651b5cdf96f165f5a087ccc5c85d94851fc4a21421488 supersedesdf640. Fixed bootstrap51517/repeat15819 exit0. Port rebuild17259 ACTIVE, generated/port-r173-fixed-build.log; pollsame. RuntimefloatSHA554149a2...ab934f equals testedcandidate. Three source-only FPRF regressions added to fullsuite. Candidate/app selection unchanged; no runtime/Simulator. Next compiledtool completion/policy-cache verification/canonical module build, then exactartifactsmoke; G6 open.

R172: canonical policy prepared, NOT applied. fprf-module-policy.inc gates exactRMGE01/DOL/C/1024, checks originalchunkSHA, transforms119sites and fails unexpectedcount/boundary; test-fprf-policy.py compiled ASanUBSan passes byte-exact comparison to tested candidate (normalizedinclude), wrongidentity/backend/chunk/reapply/boundary guards. New patches ModernGekko/0015-rmge01-fprf-policy.patch SHAdf640115b80156cb9e46208e6e53bc49d350a07c1f23921419b4ec49293a548c and ModernGekko-dolphin/0014-deferred-fprf-helpers.patch SHA661f2a2452e2240018140fedae6baaeea3b5c3e723d9266e3644f42581d1d019 both gitapply--check pass. Policy cache/manifest field rmge01-fprf-119-v1 prevents oldcache reuse; runtimepatch appends exact4tested helpers. Next bootstrap wiring/peel-restore/idempotency and compiled port tests before canonical build. App/vendor unchanged; no runtime/Simulator/build; G6 open.

R171: candidate untraced real-save smoke4989 FINISHED0. Fresh fprf-save-r171 from one-star NAND (no savestates), fixture84490 loads Observatory visibly; native pause indication appears, resume clears/animation advances, movement80933 changes Mario/camera. fallback0/SMCfailed0/NAND5040...64a6 unchanged. Whole181.4s10underruns/10backlogs includes deliberate21.37s pause, not freeze/cadence proof. Next canonical119-site integration in module preparation with exactDOL/backend/chunk/source guards and explicit cache policy identity; runtime helpers must remain baseline prefix+4tested additions. Do not merely copy experimentalmodule into oldcache (its manifest describes reference sources, not canonical build provenance). Candidate still unselected/app unchanged; no runtime/Simulator/build; G6 open.

R170: accepted reverse control fixed51.6833FPS/p99 20.864ms/DMA27.5904kHz; sequence accepted51.5→candidate53.6→accepted51.6833 supports~3.7–4.1% candidate gain, not60Hz acceptance. No more unchanged timing repeats now. Runtime91740/trigger85181 exit0, movie visibly completes/plaza, fallback0/SMCfailed0/NAND unchanged. Whole234s152underruns/4backlogs. Higher56.9snapshot was scene-dependent, not full-minute regression. powermetrics read denied (requiresroot), no privileged retry; actual thermal-frequency attribution remains unproven. Next candidate G5/pause/real-save smoke and reproducible canonical integration preserving119-site scope/source identity before normal-package promotion. Candidate still unselected; no game/Simulator/build.

R169: candidate build67896 FINISHED0/audit passes; module494c2a71d16963cf720af228ff8b9323a1d5b2967776cb759aa11f161beb3fbe,114322184bytes (+304). Linked decoder exactly119deferred calls. Runtime42140 closes0 after visible movie completion/plaza and right movement29759; trigger87012 once. Fixed minute53.6FPS/p99 20.540ms/DMA28.6144kHz versus acceptedR16351.5/~22.205/27.4944, promising~4.08% but reverse-order confirmation required. Whole234s121underruns/12backlogs; not audio/60Hz acceptance. Native fallback0/SMCfailed0/NAND unchanged; no extra launcher/profiler/build/Simulator overlap. Candidate unselected, normal app unchanged. Next fresh accepted reverse control then decide bounded integration or park; G6 open.

R168: same link67896 ACTIVE, ld33004 observed3:42/~702%CPU. New test-fprf-candidate-sources.py audits exact prepared sources (reverse119call changes restores original; originalfloat prefix plus exactly4expected helper bodies) and executes all43real decoder chains/162suffixes.64800 fullCPUState/hostflag comparisons pass ASanUBSan across4rounding/special+random/FPavailability; run26587 exit0, generated/fprf-r168-source-check.log. Prepared runtime/fprf-r168 from R85Config/Wii/slot3, hashes verified, Pipe ready but NOT launched. Next poll SAME67896 link/audit then linked inspection/movie test with accepted runner. No app/normal selection mutation, no game/Simulator; G6 open.

R167: isolated fprf build67896 ACTIVE; generated/fprf-r167-build.log. Both changed units compiled, linker33004 observed~693%CPU. Reuses1327 of1329 accepted objects (1322chunks+7runtime/export), only hotchunk119calls and appended4deferred helpers changed. Original float prefix retained; no cold-outline candidate combined. Source-pinned build-fprf-experiment.py captures accepted object hashes/exact flags/commands in build-provenance.json; O2/strictFP/ThinLTO/originalPGO preserved. Initial object-count assertion failed before compile, corrected1331→1329. Poll SAME67896 through link/audit, no restart. Candidate sources SHA chunk6b20f948...b5b929/float554149a2...ab934f. Normal app/marker unchanged; no game/Simulator. Next link audit/shape then isolated movie; G6 open.

R166: actual emitter/GXRuntime execution test added: tests/test-fprf-emitted.py.80000 comparisons pass ASan/UBSan for all5entry offsets,4rounding modes,lazy-FP on/off,MSRFP on/off,positive/negative downcount,following MFFS observer; includes actual cpu_exception.c/unavailable helper. Full final state/hostflags/cycle values match. Three focused tests66811 exit0 (also256k arithmetic chains and negative region guards). Hot chunk has224 supported arithmetic calls;119 eligible static first-writer sites (~53%, not dynamic cost). Next source-pinned isolated hot-chunk candidate using accepted objects where unchanged, preserving original PGO/strictFP and normal selection; compare linked structure/game before any promotion.10Gi available; no runtime/Simulator/build, app unchanged/G6 open.

R165: added read-only audit-fprf-regions.py over exact selected generated C. Strict two-instruction body whitelist finds283 candidate writes/69chunks,119 in804520A0. test-fprf-regions.py passes positive adjacent pair and rejects Rc/readers/memory/exception/exit/downcount/loop/MSR/fallback/unknown/chunk boundaries. Source FP availability only tests global lazy flag/MSR; arithmetic helpers do not modify either, unavailable path returns before arithmetic. This is scoped static coverage, not execution-frequency/safety proof for code rewriting. No runtime/source/module mutation. Next actual emitted-chain tests with unavailable FP, external suffix entry, cycles and observation barriers before isolated implementation. G6 still open; no game/Simulator/build.

R164: observer-cost audit uses existing evidence: R153 profile was untraced; R162 traced CPU sample has22/7412 RecordPhase samples (~0.30%), not explanation for dominant deficit (later sample, not full-window bound). No further tracing-only build/run. New isolated tests/test-ps-fprf-chain.py passes256000 consecutive add/sub/mul/madd chains across4rounding modes/special/random inputs/aliases with complete final CPUState+hostflags under UBSan;248110 differ in intermediate FPRF as expected. This supports a dataflow investigation, NOT globally suppressing flags. Generated804527E8 add→804527EC sub is a real consecutive writer pair; memory/exception/Rc/exit boundaries must remain barriers. No product change or performance claim. Next conservative emitter-level dead-FPRF analysis with negative boundary tests and measured coverage before any module build. App unchanged; no game/Simulator.

R163: fresh accepted control closes46172 exit0, movie advances; fixed minute51.5FPS/p99 22.205ms/DMA27.4944kHz versus cold candidate30FPS/p99 84.99ms. Reject cold candidate for promotion; exact regression cause not proven by one order. This reproduces older accepted51.72baseline, does not meet60Hz/audio. LowPowerMode0, no recorded thermal warning, top9samples10s apart no swap delta and runner~116%; host-top.txt retained. Source inspection finds phase trace line-buffered fprintf/shared mutex, so quantify observer cost before further code tuning. SunPad QoS is default-off experiment, not established remedy; don't blindly copy. Accepted Runtime profile accepted-r163, trigger93056 once, no extra launcher, close/fallback0/SMCfailed0/NAND unchanged;152underruns/3backlogs over176s. No game/Simulator/build remains. Next untraced/low-overhead measurement boundary and structural decoder/AOT cost, not another helper micro-optimization.

R162 runtime complete: candidate fixed minute30.0FPS/framep99 84.99ms/DMA16.015kHz, severe failure; user independently reports22FPS. Do NOT select cold candidate or infer causal regression solely against older51.72 baseline. Trigger63277 ran once after visible R85restore; movie visibly advanced, not completed. Later10s sample35677 exit0: CPU6985/7412 under Run,6719dispatch; video6743/7412 condition wait. pmset reports no recorded thermal warning (NOT proof of no throttling); top after window67.4%runner,43%kernel,25.7%Logitech, no swap delta. Need fresh accepted control with host scheduling/thermal/resource observations, then structural CPU/AOT analysis rather than more isolated helper tuning. Source CPU thread entry has no explicit QoS; absence is a hypothesis, not diagnosed cause. Close15389 exit0/fallback0/SMCfailed0/NAND unchanged;423underruns over238.7s. Extra frontend31268 auto-opened by stale CUA startup snapshot, closed before checkpoint/measurement. No game/Simulator remains.

R162: build21911 FINISHED0; audit passes1322chunks/19SMC/arm64macOS14. Candidate SHA54ac7e20643caa5679fdbbe4553c984766d2fd05b6e2f03998c261146ac40a2d. Linked add/sub127instructions each versus196/292; stack80 versus96bytes for add; identical cold handlers linker-folded. Whole module nevertheless115444744 versus114321880bytes (~0.98%larger), so no speed claim. Runtime15389/PID31256 launched with prepared cold-fp-r161 profile/phase trace, not yet observed ready or triggered. CUA game snapshot timed out during startup; retry existing binding, do not getApp/start second launcher. Normal package identity/signature unchanged. Next visible ready title, Load3 then trigger once, complete movie timing and clean shutdown. No Simulator.

R161: same candidate build21911 remains ACTIVE; source compilation reached1330/1332 and ld30839 is doing ThinLTO (observed~705%CPU). Do not restart or benchmark alongside it. Extended test-cold-fp.py compares shared scalar ni_add/sub FPRes.exception, bitwise result, full CPUState and host flags:200k comparisons across4rounding modes pass, alongside1M paired and10k register-mix comparisons, UBSan and unsanitized. Correctness-only run84908 exit0; generated/cold-fp-r161-correctness.log. Prepared isolated runtime/cold-fp-r161 profile from R85Config/Wii/slot3, not launched. Next same21911 link/audit, linked-helper inspection then single-game movie measurement. Normal app untouched; no booted Simulator/game; G6 still open.

R160: isolated full candidate build21911 ACTIVE, generated/cold-fp-r160-build.log (70/1332 observed). Shared source-pinned scripts/cold_fp_transform.py preserves original ni_add/sub symbols and extracts unchanged cold blocks; candidate floatSHA3094efccd08f31c676df672928accfd6af0da6647e6860604bcf028fbc190f2e. Every other copied runtime file byte-checked; tests now consume exact shared transformation,1M+10k state/hostflag comparisons pass. scripts/build-cold-fp-experiment.sh uses accepted corrected generated source, originalPGO on compile+link, O2/ThinLTO, isolated GXRuntime/module-build, no selection mutation. Next poll same21911 through link/audit then inspect linked helper shape and real movie measurement. App/normal marker unchanged; no game/Simulator.

R159: extended cold-FP probe with first24 actual add/sub register calls from804520A0 (call mix, NOT contiguous decoder execution).10k mix CPUState/hostflag comparisons pass4rounding modes, plus prior1M tests. Fixed unsigned-negative benchmark initializer; final unsanitized mix ratios .7857,.7932,.7880,.7845 (~21%gain), add.698–.709. Standalone asm originalhelpers86instruction lines/candidates132/cold34 each reflects different inlining; not linked-size proof. Next isolated runtime-source/cold-block candidate retaining original names and originalPGO, full module build then compare linked shape and real movie; no more micro repetitions. App/vendor unchanged/no runtime/Simulator; G6 open.

R158: prior forced-inline failure specifically ppc_psq_load_inline (+19% representative assembly,+2.3%module,slower); GQR0centralization also rejected. Distinct isolated test-cold-fp.py extracts unchanged ni_add/ni_sub NaN-result blocks into noinline,cold functions, preserving original operation and inf/FI/FR logic; classifier prototype NOT combined.1M CPUState+hostflags/4rounding/aliases tests pass UBSan and unsanitized. Complete normal-add candidate/reference .708,.701,.700,.687 (~29–31% faster micro). No vendor/app edit. Next generated-callsite assembly/code-size verification and broader mixed/helper coverage before whole-module candidate; remember prior finite-path micro gain failed game test. No runtime/Simulator; G6 open.

R157: classification-only actual add/sub/mul/madd helper differential passes1M CPUState+host-FP-flag comparisons over4rounding modes, random/special operands and destination aliases; UBSan and unsanitized pass. Initial add-only unsanitized ratios1.030,1.010,.996,.998 show no gain; expanded uniform-dispatch harness reports add.930–.956/sub.944–.956/mul.922–.927/madd.953–.969. Harness/layout sensitivity and small whole-workload upside mean no module build/promotion yet. tests/test-classify-helpers.py reuses existing strict harness but replaces rejected finite candidate entirely with actual classifier-only helper copies. Next compare emitted helper code and audit exact prior inlining scope before any higher-impact candidate. No app/vendor mutation/runtime/Simulator; G6 open.

R156: signed ps_add disassembly shows long classify/FPRF sequence after arithmetic. New unapplied classify-f32-normal.inc adds integer normal-exponent early return, preserving all original special-value logic. tests/test-classify-f32.py passes exhaustive33,554,432 special exponent/sign/fraction patterns plus normal classes/1Mrandom under UBSan.6 alternating10M normal-result classifier trials ratios .573,.716,.646,.665,.672,.652; warm~33–35% classifier gain, NOT complete-helper/game gain. Next actual full arithmetic-helper/CPUState+host-flags differential and representative helper microbench before any module build. No app/vendor edit or runtime/Simulator; G6 open.

R155: isolated type0 paired-RAM-store prototype added (unapplied).100k actual-helper comparisons pass ASan/UBSan for bit inputs, MEM1/2 mirrors/boundaries, LSQE/type/w fallbacks, callback lane ordering, reservations and CPU-state alias rejection. Six alternating5M-call micro trials candidate/reference .7805,1.1076,1.0039,.9993,.9903,.9877; warm benefit negligible, reject/park without module build. tests/test-psq-ram-pair.py retained standalone (benchmark not suite gate); app/source unchanged. Next inspect sampled arithmetic helper machine instructions for avoidable work distinct from rejected finite-FP/global-inline changes. No game/Simulator; G6 open.

R153–R154: fresh current-package movie sample23410/10s captured in movie-profile-r153/cpu-sample.txt; trigger47932 once, visible advancing movie, close74133 exit0/fallback0/smc_failed0/NANDa574...afa6 unchanged. CPU7982samples,7549Run/7257dispatch; exclusive decoder804530A0=1184,804520A0=1027,ps_add674,madd586,psq_store_inline533,sub470,psq_load_inline369,convert318,psq_store315. Exclusive accounting sums7982, not global-thread summary. Actual store-inline symbol0x5788d64 has full register frame; +632/+640 are epilogue restores, unquantized path repeats RAM bounds/reservation/journal checks per lane. Next isolated type0 paired direct-RAM eligibility/check-sharing prototype with strict sequential value/store semantics and callback/boundary/reservation tests; leave quantized path and journals unchanged. No speculative inlining/FP shortcut applied. No runtime/Simulator; G6 open.

R152: packaged wrapper smoke99899 succeeds using signed in-app module and LC env overrides unset. Readytitle→real one-star Observatory via78409, movement47530 visibly works59.9→60.1FPS snapshots. Close0/fallback0/smc_failed0,NAND5040acdd...64a6 unchanged;139.7s7underruns/5backlogs, not audio acceptance. Correctness update package smoke complete. Reviewed old R94 movie profile: predates pair and timing fixes, so next fresh CPU sample during exact R85 movie in current package (diagnostic not timing run), attribute current hot leaves before choosing another candidate. No repeat rejected finite-FP/PGO/widening/global-inline changes. No game/Simulator/build remains; G6 open.

R151: normal cache-selection35483 exits0/cache-hit da63c951ce4d7349; full suite36917 passes. Package46291 exits0, app/module/signature audit passes. Normal app now contains corrected module signedSHA5f810ae0ed1f056c7ea8b2256d124405b0b05c6a68f4fd9d7c35fda3068d097c; runneraffbcb51...9e295 unchanged. Prior app preserved at generated/macos/GalaxyPad.app.previous.20260906T194009Z. Correctness update packaged, not G6/performance pass. Next fresh packaged-wrapper smoke, then remaining THP/audio investigation; avoid rejected micro/PGO repetitions. No game/Simulator/build remains.

R150: G5 fixture91269 finishes0, Mario file1 correctly pointer-highlighted at59.9FPS. Native pause indicator appears, resume clears it and animation advances, close81007 exit0/fallback0/smc_failed0/save5040acdd...64a6 unchanged. Whole260.1s3underruns/4backlogs;39.4s gap is deliberate pause, not freeze. Correctness fix accepted for packaging, not performance/audio closure. Copied candidate9098890e...cc9de+manifest/generated symlink into normal da63c951ce4d7349 cache without replacing old artifact. Normal originalPGO cache-selection35483 ACTIVE, generated/module-select-r150.log; poll same handle then audit/normal package build (preserve prior app). App unchanged; no runtime/Simulator, G6 open.

R149: candidate heavy-movie trace completes. Same R85slot3/config/native1x/dualcore/fixture71167; fixed minute51.7167FPS/framep99 20.930459ms/DMA27.6096kHz, close to prior51.867–52, no speedup claim. Visible movie advances and returns to plaza59.9. Close24464 exit0/fallback0/smc_failed0,NANDa5743199...afa6 unchanged;223.05s155underruns/4backlogs, audio gate fails. No build/debugger/second game/Simulator overlap. Candidate cycle correctness retained but not promoted; next G5/pause-resume regression then select correctness fix if clean, separately investigate remaining THP/movie cost. No unchanged timing repeats warranted.

R148: original build87320 finishes0; candidate audit passes ARM64/macOS14/1322chunks/19SMC, SHA9098890e25b36e802ab5f793c9ad7800f991190f41e972996937343d84ecc9de. Actual candidate53653 loads real one-star Observatory via inspected ready title/fixture74977, movement47235 visibly works,59.1→59.6FPS snapshots; native close0 and GameData5040acdd...64a6 unchanged. Whole97.4s43underruns/10backlogs,5691frames/97.074s, fallback0/smc_failed0; short smoke not audio/performance acceptance. CUA initially opened extra frontend during runner startup; closed without Play, only one game ran. No game/Simulator remains. Candidate not promoted; next controlled representative heavy-scene timing plus G5/lifecycle regression, preserve correction unless semantic regression found. Normal marker/app unchanged, G6 open.

R147: verified wait on existing87320/linker19705, elapsed52s→4:36 and~682–718%CPU, RSS~1.1GB. Link still active, no reported error or restart. Same candidate/cache/profile; next finish handle then audit/runtime. Package unchanged; no game/Simulator.

R146: verified wait on original87320:942→1330/1332, now linker19705 active (11s,718%CPU), parent ninja16673/port16459. No restart. Generation Broadway/zero unknown, retained SMC warning; candidate645M/free12Gi before link. Next same handle through completion then module audit and prepared midblock-r145 runtime profile. No game/Simulator launched, accepted package unchanged, G6 open.

R145: same module build87320 verified live (ninja16673/compiler children),447→652/1332, no restart. Full1322-chunk comparison against accepted generation passes after removing only new external-case downcount statements (1002284 cases); instruction bodies identical. Fresh isolated generated/runtime/midblock-r145 copies R138 Config/Wii/config.ini, pipe configured, dualcore/native1x/Metal; GameData5040acdd...64a6 matches real one-star save. Profile prepared only, no runtime/Simulator launched. Next poll same build87320 through link/audit, then launch accepted runner with candidate module plus isolated profile, inspect ready title before fixture and validate gameplay/audio timing. App/normal marker unchanged, G6 open.

R144: local-return/embedded-data executable coverage passes; randomized CFG tests now include embedded instructions. Bootstrap hash-pins/applies0002-midblock-entry-cycles.patch (99b2e3b1...7e11e), initial99131/repeat52896 pass; vendor changes limited to c_cfg.c/emitter.c. Recompiler-only build passes, port sibling SHA e569b97d1dabf68d15099ea025be1c0d6b96bcbabbf50b61d6325e83962668aa. Full suite8718 exits0 (generated/check-r144.log). Candidate module build87320 ACTIVE, generated/module-midblock-r144.log, separate generated/modules-midblock-r144/RMGE01/<DOL>-da63c951ce4d7349 cache; originalPGO unchanged. Observed70/1332 compilation. Updated probe extracts actual external switch cases (old hardcoded switch could not verify fix); accepted module still reproduces0, freshly generated candidate80517538 executes3stores+blr and charges4 under UBSan. Next poll same87320 through link/audit then isolated gameplay/audio timing tests; do not restart. Normal active marker/app unchanged; no booted Simulator/game; G6 open.

R143: isolated candidate patches/DolRecomp/0002-midblock-entry-cycles.patch computes per-instruction suffix charges and charges nonleader entries only in the external switch. Patch applicability passes; vendor generator remains clean and package unchanged. tests/test-midblock-cycles.py compiles actual candidate CFG/emitter/generated C with ASan/UBSan: all19 straight-line entries, direct branch/fallthrough and counted-loop interior entries pass; fallback boundary/empty CFG pass.10k randomized CFG comparisons against pinned original preserve leaders, leader charges and outlined-loop boundaries; every suffix agrees with independent original forward scan. Added focused test to suite (full suite not rerun this turn). No game/booted Simulator. Next expand local-return/embedded-data coverage, then canonical bootstrap integration and isolated module regeneration/runtime timing validation. No FPS gain or G6 pass claimed.

R142: SMC bounds prototype parked: OnICacheInvalidate leaf74/7298 (~1.01%) bounds total sampled upside before preserving most work. More important timing defect reproduced from actual selected generated code: dispatch at80517538 executes3stores+blr but subtracts0 cycles; host minimum charges1. Full helper805174fc executes18stores+blr and charges19. Live R140 frequently enters interior address. Probe tests/probe-midblock-charge.py compiles actual snippet/UBSan, reproduces defect (not suite acceptance test). Next fix emitter external-entry suffix cycle accounting without double-charging internal fallthrough; focused control-flow tests before regeneration. Package unchanged; G6 timing open.

R141: cache-op hook already bypasses full interpreter sync when eligible; register save/restore helper executes straight-line to blr, so no simple extra per-register dispatcher exit. New UNAPPLIED smc-outside-bounds.inc prototype rejects ranges outside sorted compiled-code envelope only after existing fallback-JIT invalidation/address resolution.200k actual-body comparisons pass ASan/UBSan for state/counters/callbacks, empty/inactive/relocation/wrapping cases. Next measure whether outside-range traffic/cost warrants host candidate; no performance gain claimed or runtime patch applied. Package unchanged, G6 open.

R140: dispatch-site diagnostic completes real-save Observatory,close84370 exit0/native-only,NAND unchanged. Top sampledPC804a2f14=19744 follows generated cache-instruction fallback at804a2f10;80517538=13971 and80517584=13789 land in register save/restore helper region. Counts are whole-run every4096dispatches (startup included), not CPU cost or unbiased timing. Next inspect these exact helper boundaries/cache instruction semantics for avoidable dispatch exits; preserve per-block timing/memory callbacks. No game remains; package unchanged, G6 open.

R139: mapped sampled host Run offsets to signed ARM64 disassembly.751/7298CPU-thread leaf samples (~10.3%) are Run itself; +988 is optional dispatch-sampling guard, +1224 idle-PC load, neither individually weighted by collapsed sample. Native dispatch counter also controls lockstep start/limit and trace cadence, so cannot drop/coarsen blindly. Per-block timebase division is already constant-strength-reduced (umulh/shift), not hardware divide. m_charged_cycles alone is diagnostic but small; no speculative timing/interrupt/counter patch. Next use existing default-off dispatch-site sampling on real-save Observatory to identify guest PCs behind broad chunk entries, then map source before candidate. No runtime/build launched, package unchanged; G6 open.

R138: promoted app loads real one-star Observatory save through title/fixture60310 once, no savestate. Native1x/dualcore R64 profile; visible60.3 then58.9 snapshots.10s sample13337:6174/7298 CPU-thread samples under StaticRecomp Run,5442 under dispatch;199 float-future wait samples inside dispatch. Whole192.5s88underruns/18backlogs,24388depth peeks,clean31766 exit0/native-only,NAND5040acdd...64a6 unchanged. Sampled diagnostic not acceptance or matched R64 comparison. Next inspect collapsed CPU leaves/generated hot chunk structure; current EFB activity differs from old zero-peek runs, so do not assume old phase equivalence. No game/Simulator remains; G6 open.

R137: paired-store optimization PROMOTED to normal app. Package34200 exit0; package/module/signature audits and full suite80042 pass. Signed runneraffbcb51...9e295/module315d08db...d63b0 exactly match measured candidate. Previous app retained as GalaxyPad.app.previous.20260906T183531Z. Normal wrapper launch14639 with env overrides unset restores R85 and visibly moves Mario, close0/fallback0/smc_failed0,NAND unchanged;4underruns/6backlogs over124.9s not audio acceptance. Config selected=true; explicit0 opt-out preserved. No game/Simulator remains. Next profile remaining representative G6 gameplay cost using promoted package (Observatory/heavier views), not more unchanged pair A/B. G6/60Hz/audio and later platform/menu gates remain open.

R136: original44651 terminal1 after successful module publication (relative-output post-build path issue). Explicit nested module audit passes; normal unsigned modulee8da217b3594c69a0b02546964e07feeef0fab49a0fb369bce3c6d2a88982d00 and runner6dde0e4...9ed6 exactly match measured candidate. Copied verified module/manifest into normal44290ae60c4cad14 cache, linked its generated tree; normal command82303 exit0 cache-hit selects new marker, no rebuild. Wrapper pair default1 added with explicit0 preservation, tests pass. Package build34200 ACTIVE, generated/lc-pair-r116/package-r136.log; same script preserves prior app on replacement. Next finish same package handle, audit/signature/identity then visible wrapper smoke; no game/Simulator running. G6/audio still open.

R135: verified wait on original44651/linker10867. Bounded polls confirm live linker1:51→4:59 elapsed,~697–707%CPU, no reported error; link not complete. Keep same process/cache, no restart. Next completion then explicit nested-cache audit/hash comparison. App/active marker unchanged; no runtime/Simulator launched.

R134: original module44651 verified active,796→1330/1332; no restart. Fresh generated RMGE01_generated tree diff is empty against accepted source. CMake verifies Release/O2/originalPGO and integrated GXRuntime path. Full suite13470 exit0 (check-r134.log). Link/completion not yet verified; same exact nested cache and build handle from R133. Next link/audit/hash comparison then selection/package. No runtime/Simulator, app/active marker unchanged.

R133: normal originalPGO module build44651 ACTIVE, log generated/lc-pair-r116/normal-module-r133.log, progressed30→164/1332 and continuing. New cache suffix44290ae60c4cad14 differs from old. Relative output override exposed cwd mismatch: actual cache is generated/build/moderngekko-desktop/generated/modules-pair-integrated/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-44290ae60c4cad14. Keep this valid build; do not restart. Future build-module output override normalized to repo absolute path, focused default/relative/absolute-with-spaces test passes. Final inspect in running old script may inspect other empty output; audit exact actual cache after build. Normal active marker/app unchanged. Next same handle through link/audit and compare measured candidate, then selection/package.

R132: port build74137 completes0; portSHAcb8f514c0faf0f575f8157bd654ec91b67cba3dbe89791127bfed9445e167ff3. Runtime caller integrated via hash-pinned0013-lc-pair-runtime.patch; cpu.c exact1350d119...edb69 matches measured candidate. Initial/repeat bootstrap pass. Pair/order tests now use hash-checked pinned git original as independent oracle and require actual caller equality. Full stable-source suite39396 passes; earlier concurrent bootstrap/test raced on temporarily peeled overlay, so never run source-reading tests alongside bootstrap. Active module/app unchanged. Next normal module build using originalPGO/new cache key, audit identity then wrapper default/package; G6 open.

R131: canonical0014-module-source-identity.patch hashd3640ee79866a4a48482d90b44410a83d538c4b8be7fa72cc30b192e33278431 wired into bootstrap, port cache key before lookup and manifest. First/repeat bootstrap exit0, full suite89191 exit0; test extracts actual FNV and requires exact integrated collector, verifies content changes alter derived key (hash provider still test double). Port build74137 ACTIVE, log generated/lc-pair-r116/port-build-r131.log observed45/185; shared core dependencies rebuilding. Poll same handle, no restart. Caller/app/active module unchanged; next completed port build then runtime caller integration and independent reference-test adaptation. No game/Simulator launched.

R130: cache-input collector prototype added with compiled ASan/UBSan tests passing. Sorted relative paths plus per-file SHA256 provider cover GXRuntime src/core/include, module-template, StaticRecompABI.h; missing/empty source trees, unreadable files and symlinks reject. Test hash provider is a content double, not SHA verification. NOT wired to port/cache yet. Next wire collector before cache lookup and manifest, test actual key invalidation, canonical overlay/bootstrap integration; caller/package unchanged. No game/Simulator launched.

R129: normal bootstrap now hash-pins/applies accepted pair host patch, peels it before overlapping lower-patch checks, restores on failure, and includes it in dependency scope audit. First75997 and repeat79170 exit0; full suite17322 exit0, actual integrated host tested. Normal vendor host source now contains pair capability (opt-in remains required); runtime cpu.c and app unchanged. Accepted package hashes still d4d0c3c...d8ff53/25e17d0...65393. Next add runtime-source identity to module cache (currently absent), integrate caller with independent reference tests, then normal build/package selection. No game/build active; no new timing runs needed.

R128: reverse OFF46.600FPS/frame p99 23.111875ms/DMA24.881067kHz versus ON52.000/20.703125/27.7632: +11.59% throughput, matching first pair+11.38%. Movie completes, close28766 exit0/native-only,NAND unchanged. Decision: accept guarded pair change for integration as incremental improvement, not G6/audio pass; config records decision but selected=false until normal bootstrap/cache/package integration and audits. No more unchanged timing runs. Next wire canonical host/runtime patches and cache identity into normal build, preserve explicit0 opt-out, verify reproduced artifacts/tests before replacing package. No game remains.

R127: reverse-order confirmation ON half complete: fixed minute52.000FPS, frame p99 20.703125ms, DMA27.7632kHz, close to R12451.867. Same candidate/R85/fixture/trace policy, no debugger/build. Movie visibly completes into plaza; native close22819 exit0,fallback0/smc_failed0,NAND unchanged. Whole229.3s155underruns/3backlogs, not audio acceptance. No game remains. Next OFF half in fresh profile, then decide promotion without further unchanged repetitions. Candidate still unselected; full G6 open.

R126: isolated paired-store candidate passes bounded normal-boot title/file-select pointer regression. Ready title inspected, existing G5 fixture once, Mario file1 visibly highlighted at59.9–60.0FPS. Native close35088 exit0, fallback0/smc_failed0, NAND unchanged;12195frames/203.525s,1underrun/2backlogs,zero backend errors. Not zero-starvation or broad audio acceptance. No game/Simulator remains. Next bounded reverse-order attack confirmation to reduce host/order uncertainty, then promotion decision; candidate still unselected.

R125: untraced pair candidate restores R85, completes attack, and visibly responds to one-second right movement afterward (Mario/camera position changes). Movie snapshot50.6FPS, plaza60.0, moved view58.2: snapshots, not sustained acceptance. Native close93900 exit0, fallback0/smc_failed0, NAND unchanged. Whole219.3s141underruns/4backlogs: audio still open. Candidate unselected; next G5 pointer/file-select regression then bounded matched confirmation before promotion. No game/Simulator remains.

R124: paired-store ON fixed attack minute51.867FPS vs R123 OFF46.567 (+11.38%); frame p99 21.059 vs23.214ms, DMA27.686 vs24.862kHz. Same candidate/checkpoint/fixture/trace policy, no debugger/build overlap. Both visibly complete movie into plaza, close0, fallback0/smc_failed0, NAND unchanged. Promising isolated candidate, not promoted and not60Hz/audio acceptance. No game/Simulator running. Next uninstrumented candidate movement/G5 regressions and bounded confirmation before default selection; normal app untouched, experimental desktop build cache warning still applies.

R123: paired-store OFF control completed the attack and visibly returned to plaza gameplay (59.9 FPS title sample). Fixed attack minute measured 46.567 FPS, frame p99 23.214 ms, DMA 24.862 kHz. Native close41298 exit0, fallback0/smc_failed0. Whole-run 283 underruns/6 backlog drops is not matched-window audio acceptance. Next same candidate explicit pair ON using unused pair-on-r118 profile. No promotion; G6 open.

R122: actual pair activation proven in isolated signed candidate with opt-in1. R85 restored, trigger once, debugger53292 attached PID99616, broke TryGetLockedCachePair and stepped out: x0=0x12047c020 at ppc_psq_store+152, caller func_804520A0+51244. Detached successfully; visible movie resumes. Native close55420 exit0. This debugger run is not performance evidence. Next prepared pair-off-r118/on-r118 same-binary phase comparison; no promotion. No game/debugger running.

R121: original module4915 completed0/audit pass, unsigned modulee8da217b3594c69a0b02546964e07feeef0fab49a0fb369bce3c6d2a88982d00. Isolated signed generated/runtime/Pair-Candidate-r121.app assembled from accepted resources plus candidate runner/module; codesign verify and resource diff pass. Signed runneraffbcb51f27f853b0b5ee403b5033c3bd5a6f7ea3e514b969c2ef4272af9e295, module315d08dbe765d55aeaedf3dd55738c0e7b6a7720a5e863c2692dbdffdaed63b0, descriptor ABI3/1322chunks/19SMC. Not launched. Next R118 activation profile with explicit opt-in; prove successful nonnull cache pointer separately from timing, then same-binary0/1 runs. Accepted app hashes unchanged; no game/build active.

R120: verified original4915/linker99100 live through bounded polls, ~713% CPU at3:14 elapsed; no errors observed,14GiB available. Not complete; do not restart. Same pending activation/on-off plan, no package change or runtime launch.

R119: original module4915 advanced941→1125→1330/1332, now active ThinLTO linker99100 (~724% CPU at first inspection). No errors observed; not complete and not restarted. No game/Simulator. Continue same handle through audit; prepared R118 profiles remain unused. Accepted app unchanged.

R118: original module4915 verified live, advanced352→558/1332 and continuing. Prepared pair-off-r118, pair-on-r118, pair-activation-r118 from R85, all slot3 hashes match aea2b7a3...7ab8. No game/Simulator. Candidate runner symbol TryGetLockedCachePair verified; success pointer formation at symbol+0xd4, shared return+0xdc (requires runtime nonnull proof, not just symbol hit). Next same build handle to audit, isolated app, separate activation proof then same-binary opt-in0/1 comparison. Package unchanged.

R117: isolated matching module build ACTIVE exec4915, generated/lc-pair-r116/module-build.log, observed114/1332 and advancing. Hash-checked script reuses accepted generated chunks/original PGO/strict O2 ThinLTO with copied paired-store runtime; no regeneration or default selection. Full repository suite passes. Next poll same handle through link/audit, then isolated coherent candidate app and activation/performance test. No game or Simulator. Normal package unchanged; desktop runner cache remains experimental until normal rebuild.

R116: experimental host built16456 exit0; saved generated/lc-pair-r116/GalaxyPadRunner SHA6dde0e4dea8621dc1064666e0da6bfb6258535b72e7121def485752521519ed6. Temporary vendor delta reversed, forward patch check passes; normal packaged runner unchanged. Desktop build cache now holds experimental runner: do not package without normal rebuild. Copied GXRuntime actual cpu.c SHA1350d1196b38b147477890ef0dc59d5d9e389a55a169d51913fc033be34edb69, tested actual caller and integrated host; full suite passes. Next isolated module from accepted generated chunks/original PGO with copied runtime, then coherent candidate app. No game or build active.

R115: unapplied host callback prototype and full suite pass sanitizers. Exact GALAXYPAD_LC_PAIR_FAST=1 required; pixel-store tracing disables pair path. Rejects mismatched MSR without propagation, lockstep journaling, non-E segment, relocated either byte; MMU guard handles live translation/debug/cache/sink/bounds. Legacy positive-size requests unchanged. Next assemble isolated coherent runtime+module candidate with existing accepted generated chunks/PGO, keep normal bootstrap/package untouched; verify integrated source before build. No runtime/build active.

R114: unapplied optional type4 pair caller passes 1M actual-quantizer byte/host-FP-flag comparisons plus rejected-request ordering/wrap/GQR/journal/lane/type tests. Uses external_pointer size0 capability request (old hook rejects), not unsafe ordinary range lookup. New host must reject side-effect-free if MSR unsynchronized, journaling/debug/cache guards fail, or opt-in off. Full suite passes; no runtime edits/build. Next implement isolated opt-in host callback against guard prototype, preserve positive-size behavior and verify old-host null fallback before coherent candidate.

R113: isolated pair-pointer eligibility implementation/tests pass ASan/UBSan and full suite. patches/experiments/lc-pair-pointer.inc is NOT applied to runtime. Tests cover every valid cache start, all65536 byte pairs at representative offsets, live remap/DR, page/wrap/end bounds, null/small cache and debug/journal/cache guards. Next integrate opt-in caller only after fallback ordering test; preserve accepted module/package and strict quantization. No game/build active.

R112: paired-store contract traced and source-derived regression added/passes full suite. Naive coalescing changes callback order/live second-lane read, GQR snapshot, wraparound and debugging semantics. Existing external_pointer ABI slot is unused by current GXRuntime memory accesses; current HookExternalPointer lacks live BAT/debug guards, so must not reuse blindly. Next investigate guarded two-byte locked-cache pointer eligibility (live translation, same-page/full-range, debug/cache/journals disabled) with independent tests before any module/runtime implementation. No performance claim or package mutation.

R111: isolated integer float-widening simplification exhaustively matches all 2^32 input encodings but is 6.9–8.1% slower in four alternating mixed-input microbenchmarks. Rejected before module build; runtime source unchanged. Probe tests/probe-f32-widen.c, private results generated/tests/probe-f32-widen-r111.log. Next avoid global inlining/O3/GQR centralization/CLZ/finite-add/PGO/widening repeats; inspect actual decoder memory-access batching boundaries and correctness contract for a larger opportunity. No game/build active.

R110: decoder-PGO candidate rejected for promotion. Final candidate43.933FPS/p9924.679ms vs follow-up accepted47.283/p9922.911ms, -7.08% observed throughput. Host variance prevents exact causal sizing; no demonstrated gain. All candidate/control runs restore/advance and exit0/native-only, NAND unchanged. No more unchanged runs/builds for this profile. Current package remains accepted25e17d0...65393/defaultLC. Next inspect emitted/native hot-decoder structure for a concrete higher-impact change before another build. No runtime/Simulator/build active.

R109: accepted-module reverse control completed47.283FPS/p9922.911ms, versus initial baseline38.733 and candidate40.733. Apparent initial +5.16% gain invalid as causal evidence; host/order variation dominates. Control31325 exit0/native-only, visible restore/movie progression, NAND unchanged. Prepared decoder-confirm-r109 for one candidate confirmation after control (no recent build); if no clear benefit, keep unselected and stop this comparison. No runtime remains.

R108: candidate R103 run completed, visible restore/advancing movie, native close2580 exit0, fallback/smc_failed0, unchanged NAND. Fixed-minute40.733FPS vs first baseline38.733 (+5.16%), but framep99 worsened30.451 vs28.933ms. No promotion; possible host/thermal variance. Prepared fresh decoder-control-r108 R85/Pipe profile for accepted-module follow-up baseline. Next run that control with same trace/trigger before conclusion. No game running.

R107: build1268 completed exit0/audit pass. Candidate decoder-use-r102/gRMGE01_recomp.dylib SHA 2a576018bd862d1426b2ad225cfd14fb70f24c8c99e68a42b9bc3fadcbcdad7b, 99,394,392 bytes, unselected. Prepared R103 baseline run completed: visible R85 restore/attack advances, fixed minute 38.733 FPS /20.6784kHz DMA, p99 28.933ms, clean exit0/native-only. This follows heavy build and is slower than R99 baseline; host thermal/load confound requires follow-up baseline if candidate appears faster. Candidate R103 profile remains unlaunched. No game/build running. Next candidate matched trace then reverse/control check as needed; no promotion.

R106: verified original session1268 still live through repeated bounded polls; linker91424 actively used ~689% CPU, elapsed3:26 at inspected intermediate point, no errors/profile mismatches. Last poll still running. No restart or game launch. Continue same handle through completion/audit, then prepared R103 comparison.

R105: original build1268 reached 1330/1332, active ThinLTO linker PID91424 verified ~688% CPU at 1:35 elapsed. Not hung, not complete; same session/log, do not restart. 15GiB available. No game/booted Simulator. Next same handle through terminal success/audit, then prepared R103 profiles for matched A/B.

R104: verified wait on original build1268, advancing 766→989→1155/1332 with active compiler processes. No errors or profile-CFG mismatch warnings observed; integer helper file has no profile data warning (not decoder mismatch). Accepted runner/module hashes unchanged. No game or Simulator. Next same handle through ThinLTO/audit then prepared R103 A/B; do not restart.

R103: verified original build1268 advancing 311→626/1332, still live; do not restart. Prepared decoder-baseline-r103 and decoder-candidate-r103 disposable R85 profiles, matching slot3 SHA aea2b7a3...7ab8, independent Pipes. No game/Simulator. Moved stray default.profraw (likely module-info trainer inspection output) to ignored generated/pgo/module-info-default-r103.profraw; added profraw/profdata ignore and tracked-file rejection. Suite passes. Next same build through completion/audit, then prepared matched A/B.

R102: decoder training collected successfully. Existing instrumented module restores R85 and visibly advances attack; clean exit 0, fallback/smc_failed zero, unchanged NAND. Decoder counts now 21,516,841 / 40,635,145 with matching CFG hashes. Merged opening+decoder profile SHA b355557fae4d0d826eb131807eca5f6bd95a0f51ac5edec50e15559d8838889b. Isolated unchanged-code profile-only build ACTIVE exec session 1268, last 74/1332; log generated/pgo/decoder-r102-build.log, output generated/pgo/decoder-use-r102. Poll same handle, do not restart or launch game during build. Build script audits on completion but never selects. Repository suite passes; no game/Simulator running. Next completed candidate audit then matched R85 A/B, no FPS claim yet.

R101: verified missing decoder PGO coverage. Accepted profile has zero entry AND all-zero block counts for func_804520A0 (2947 internal counters) and func_804530A0 (2627), despite R94 hot samples. Existing instrument-build module SHA 591ff35e70a1ca20cf3da1d91a72b593f249ab36d63fb043a849e2b3d7e8e033 is reusable: its generated tree exactly matches accepted tree, descriptor RMGE01/1322 chunks/19 SMC, O2 strict-FP ThinLTO instrumentation. Prepared decoder-training-r101 R85 slot-3 profile and pgo/decoder-profiles-r101 directory; NOT launched. Next run existing trainer with LLVM_PROFILE_FILE in that new directory, restore/trigger movie, clean exit, verify nonzero matching decoder counters, then consider isolated profile-only candidate. No new module build needed to collect training; no game/Simulator running.

R100: rejected CLZ experiment removed from normal bootstrap/generator path. Bootstrap reverses only the hash-checked experimental patch, then requires a clean pinned DolRecomp tree; repeat bootstrap passes. Both generator binaries rebuilt, experimental differential test isolated in a temporary tree. Repository suite and standalone codegen_compile/c_execute pass. Accepted package hashes unchanged; no game or booted Simulator. Next: larger decoder/profile hypothesis, not unchanged arithmetic/CLZ retesting. G6 stability/audio remains open.

## Current goal

- Lowest unmet goal: **G6 — macOS first Grand Star loop works**.
- G0: **met**. Host inventory, private boundary, repository safety gate, reviewed pins, clean-state checks, and disabled push URLs are recorded and reproducible.
- G1: **met**. Exact header/partition/DOL identity, two matching deterministic extraction manifests, and the complete executable inventory are recorded.
- G2: **met**. Exact-DOL generation selected Broadway/Wii, emitted the Wii address model, and retained 64 MiB MEM2.
- G3: **met**. The portable C AOT completed with zero unknown instructions, the ARM64 module links at a macOS 14.0 minimum, fallback/SMC inventories are named, and the HOME RSO has a bounded native-adapter plan.
- G4: **met**. Headless and Metal runs loaded the exact module, initialized the Wii runtime and per-run NAND/SYSCONF, executed the AOT entry for sustained native dispatch, and shut down cleanly without fallback or failed SMC handling.
- G5: **met**. Video, file select, absolute IR, independent A+B, fresh-file creation, bounded breadcrumbs, and continuous main-DSP delivery are proven. A cooled, unsampled true-1× C1024 control restored 59.61 Hz/31.97 kHz with zero underruns, one startup-only backlog correction, the accepted projection/input signature, and native-only execution.
- G6–G15: not met.

## Known state

- **R99 finite add/sub candidate rejected:** build 39974 completed 0; audited candidate SHA 89a47ced8d7304c326ea8dc25fdf2a12c5fa8a995697ba3f3fbdc6cbc7a01417 (99,527,128 bytes). Same default LC runner/state/trigger/trace policy: accepted 46.283 FPS vs candidate 45.517 (-1.66%), p99 23.990 vs 25.813 ms. Both visibly restore/advance movie and cleanly exit native-only. No promotion; keep current accepted module and LC default. No build/game/Simulator remains. Next avoid repeating this microbenchmark candidate; investigate whole-decoder optimization/profile effects, and remove rejected CLZ from normal future generator path before any default regeneration.
- **R98 verified link wait:** original build session 39974 still live; source compile finished 1330/1332, linker PID 84814 confirmed active (~678% CPU, 5:03 elapsed at last check). This is active ThinLTO, not a hang; no restart. Prepared isolated ps-baseline-r98 and ps-candidate-r98 profiles, both slot 3 SHA aea2b7a3...7ab8, Pipe configured. Do not launch while link runs. Next poll same handle, audit completed candidate path, then run prepared baseline/candidate with same phase policy. No game/Simulator; accepted app unchanged.
- **R97 build continues / stronger FP check:** same session 39974 confirmed live, last 1247/1332; no restart. Actual candidate passes added host FE_ALL_EXCEPT comparison for one million cases alongside guest-state checks. Microbench numbers from this compiler-overlapped run are excluded from performance evidence. Added explicit unselected experiment manifest and audit support for accepted generated-directory symlink; accepted-module audit/repository suite pass. Next poll same build through link, then audit candidate and compare gameplay. No game/Simulator running; default package unchanged.
- **R96 isolated finite add/sub build running:** actual candidate bodies pass million-case comparison and normal-add probe (ratio ~0.72–0.74). Only ignored copied GXRuntime changed; canonical experimental patch and hash-checked build script added. Reuses accepted generated chunks, not current CLZ generator. Build session 39974 live, last 461/1332; log generated/ps-finite-r96/build.log. Two changed functions have ignored mismatched PGO data; net gameplay benefit unproven. No game/Simulator; accepted app/module untouched. Next poll same handle (do not restart), audit candidate dylib, then matched R85 comparison with current default LC enabled on both.
- **R95 finite add/sub probe passes, not in product:** isolated tests/probe-ps-finite.c includes pinned arithmetic implementation as oracle; finite four-lane guard bypasses exceptional-input handling only for add/sub, preserves force_single/write/FPRF, falls back otherwise. One million full CPU-state comparisons across four host rounding modes, random FPSCR/operands, special-value cross-product and destination aliases pass. Normal-add microbenchmark candidate/reference ratio 0.703–0.726 in latest alternating run (not game FPS). Next turn this into a pinned isolated module candidate, retain exceptional path, test actual emitted helper then R85 movie. Accepted app/module unchanged; no runtime/Simulator.
- **R94 rebuilt default activation verified:** launched packaged wrapper with LC env explicitly unset; exact attack hotspot logs activation, visibly advances ~46.1 FPS, closes cleanly/native-only. Five-second sample: 3619/3940 CPU samples under generated dispatch; remaining leaves include paired-single add/madd/sub (328/302/218 self summary) and convert_to_double (155). Generic pixel MMU work is reduced but not the entire deficit. No new speed claim from sampled run. Next inspect paired-single arithmetic/conversion lowering for bit-exact optimization, retaining NaN/subnormal/FPSCR contracts; do not alter EFB or replay default activation again. No runtime/Simulator remains.
- **R93 incremental default packaged:** disabled G5 control also records 3 underruns/3 backlog corrections at ~59.92 Hz, matching total count but not timing/duration of R92; no clear new regression established. Given R90 measured gain and R91 functional checks, GalaxyPad wrapper now defaults guarded LC fast path on, preserving explicit 0 opt-out. Build/package audit passes; packaged runner d4d0c3c89c7f4534efc90d0fb2b280b62c0d3a0a4256b11a470c212878d8ff53 matches tested candidate, module unchanged 25e17d0...65393. Wrapper inheritance tests pass; new audit checks wrapper byte identity. Next verify activation through rebuilt default package with no explicit LC environment setting. Full G6/audio/60-FPS stability still open; no runtime/Simulator remains.
- **R92 candidate G5 functional regression passes, audio not zero:** normal boot without emulator state, copied R72 profile, A+B/pointer fixture visibly selects Mario file 1 at 59.9 FPS. 15,459 frames/257.983 s (~59.92 Hz), 3 underruns/3 backlog corrections, 30,999 real depth reads; clean exit 0/native-only, NAND unchanged. No LC activation breadcrumb on this route: it does not exercise the optimized store or attribute rare underruns to it. Default stays off; no zero-underrun reproduction claim. Next same candidate disabled to distinguish baseline audio variance, then incremental-promotion decision. No runtime/Simulator remains.
- **R91 untraced candidate regression passes bounded movie/control checks:** same candidate app/accepted module, opt-in on, no phase trace/profiler. R85 restore/trigger, advancing attack ~46.2 FPS, movie completes to plaza ~59.9, lateral movement works, normal exit 0/native-only. 255 whole-run underruns remain; not stable-audio acceptance. Disposable NAND unchanged. Expanded sanitizer test covers 4,194,304 byte stores against canonical rotation/swap/memcpy expression plus BAT_WI and alias/remap cases; full repository suite passes. Default still off. Next candidate G5 file-select/audio regression without emulator states, then promotion decision; no runtime/Simulator remains.
- **R90 LC byte candidate improves measured movie cadence:** same candidate app/accepted module, sequential opt-in off/on, same R85 state/trigger/trace policy. Fixed [A+20,A+80) window improves 42.50→47.50 FPS (+11.76%), DMA 22.688→25.359 kHz; frame-start p99 26.868→22.803 ms. Activation confirmed at exact 80452A2C/e0000000. Candidate visibly finishes movie, returns to plaza and responds to lateral movement; clean native-only exit, unchanged NAND. Still below 60 FPS and trace-on only: retain default-off and accepted package unchanged. Next uninstrumented movie-to-gameplay/G5 regression before promotion, plus fuller memory-equivalence coverage. No game/Simulator remains.
- **R89 build completed:** session 38409 exited 0. Separate signed LC-Byte-Candidate-r89.app runner d4d0c3c89c7f4534efc90d0fb2b280b62c0d3a0a4256b11a470c212878d8ff53 built, signature verified. No runtime test yet. Initial bootstrap scope check exposed missing diff --git metadata in the new overlay; metadata corrected, canonical hash now d980680c30fda3e54593930d6815d78ead4c78cd26a9b074f77fbac77394f126. Next sequential candidate-app off/on comparison, same accepted module/state/trigger; verify activation breadcrumb. No process left running.
- **R89 candidate implemented, build underway:** default-off GALAXYPAD_LC_BYTE_FAST guarded one-byte locked-cache store uses live BAT translation and falls back for page-table/unmapped/non-L1/debug/shadow cases. Source-derived sanitizer guard/value/boundary tests and repository suite pass. Build session 38409, log generated/runtime/lc-byte-r89-build.log; last inspected 108/182 and live, do not restart. No game/Simulator running; accepted package unchanged. Next finish same build, verify bootstrap overlay repeatability after build ends, package separately, then sequential off/on R85 attack comparison and activation breadcrumb. No performance claim.
- **R88 live pixel-store diagnosis confirmed:** bounded default-off exact-PC trace reports one-byte writes to e0000000/e0000020/e0002a00 tile ranges, GQR6=3d043d04, MSR=a032 (DR on). R85 state/trigger visibly reproduces movie, 42.5 FPS; clean native-only exit. Source-derived opt-in/scope/cap tests and repository suite pass; pinned diagnostic overlay built into separate Pixel-Diagnostic-r88.app, normal package unchanged. Next translation-safe locked-cache byte-store candidate with memcheck/lockstep guards, then matched benchmark. No game/Simulator remains.
- **R87 next hotspot localized:** accepted func_804520A0+51244 maps exactly to guest 0x80452A2C, psq_st f9,0(r6),0,6; profile descends through per-byte external writes/MMU. THP source suggests locked-cache tile writes. Live EA/GQR6/MSR remain unmeasured, so no memory fast path implemented. Next bounded default-off address diagnostic at that PC, then one R85-trigger run; preserve translation/memchecks/lockstep journaling. Attack-window analyzer now has interval-boundary/incomplete-window regression coverage. No game or Simulator launched; accepted package unchanged.
- **R86 candidate tested, not promoted:** sequential trace-on runs from R85 slot 3 reproduce attack with the same short fixture. Fixed 60-second window beginning 20 seconds after first A press: accepted 43.667 FPS / 23.311 kHz DMA, CNTLZW candidate 44.300 FPS / 23.648 kHz (+1.45%). Frame-start p99 24.332 vs 24.133 ms. Marginal diagnostic difference does not resolve visible lag; retain accepted package/marker. Both restore correctly, show progressing movie, exit 0 with fallback/failed SMC zero and unchanged disposable NAND. New measure-attack-trace.py makes extraction reproducible. No runtime/Simulator remains. Next inspect larger exact-DOL THP decode costs or lost PGO coverage; do not repeat unchanged CLZ benchmarking or opening navigation.
- **R85 matched pre-attack checkpoint ready:** ignored pre-attack-r85/StateSaves/RMGE01.s03 SHA-256 aea2b7a3fe295b77e409753a216abf8fe6f2f1ec23ee7a8832fc9ac1a27b7ab8. Baseline visibly loads slot 3 before attack, and new g6-r85-trigger-attack.json (left-jump then forward-right) reliably starts the cinematic in the checked replay, ~39.1 FPS. Combined long R81 route FAILED to reproduce endpoint and must not be reused as deterministic benchmark; manual corrections produced this state. No need to replay opening again. Next fresh baseline and candidate runs from copied slot 3, same trigger, matched movie interval/telemetry, no compilation. Current app remains accepted; no runtime/Simulator/build remains.
- **R84 candidate built/audited, no runtime promotion:** build session 80440 completed exit 0. Candidate modules-cntlzw-r82/RMGE01 cache 1fd29a768e1f21dc, SHA-256 4e1464f9bbf00b1f5466fecca0d03ca47ebbbd082c230507bec066420d30ff89, 98,949,544 bytes. Audit passes and disassembly proves native clz at hot r31→r12 operation in func_804530A0 (0x4b99cec). Accepted package module remains 25e17d0...65393. R81 movement calls concatenated into g6-r81-pre-attack-route.json, dry-run only: starts at visible fresh-file Star Festival entry, excludes triggering left-jump and external observation delays; endpoint MUST be checked before saving/triggering. Next establish matching pre-cinematic checkpoint then baseline/candidate runtime comparison. No build/game/Simulator running.
- **R83 candidate linking / THP lead:** existing build session 80440 remains live; 1,330/1,332 steps completed, linker PID 70140 actively doing ThinLTO (~694% CPU at inspection). No restart. Cache suffix 1fd29a768e1f21dc differs from accepted identity. Changed functions report ignored mismatched old PGO data; runtime benefit is therefore unproven. Exact guest coefficient sign-extension/table-store sequence matches THP Huffman decoder logic in Petari, and local PrologueA.thp declares 59.94 FPS/5,591 frames; movie identity at runtime remains indirect. audit-module.sh now accepts an optional absolute candidate path without changing accepted marker; default audit and relative-path rejection checked, repository suite passes. Next poll same build then inspect/audit candidate; no game or Simulator running.
- **R82 CNTLZW candidate underway, not promoted:** exact accepted-binary disassembly maps hot func_804530A0 offsets to guest 0x80453AAC CNTLZW and following work. Existing generated C counts leading zeros with a loop; ARM64 expands it into a branch ladder. New pinned DolRecomp emitter overlay uses zero-guarded __builtin_clz for GCC/Clang and retains portable fallback/record handling. Million-input differential+UBSan/native-clz check, codegen_compile, c_execute and repository checks pass. Isolated full candidate build is live in exec session 80440, log generated/runtime/cntlzw-r82-build.log, output generated/modules-cntlzw-r82. Do not start another build or gameplay while it runs; poll the same handle. Packaged runner/module and accepted marker unchanged. Next finish candidate, verify actual hot-code lowering and candidate identity, then targeted gameplay/performance comparison. No speedup or G6 claim.
- **R81 actual opening regression:** isolated fresh-file route reaches Star Festival, movement/jumps, Star Bit count 3→14, Bowser attack cinematic, and attacked plaza. Most sampled pre-attack views 59.9 FPS (lake 58.8), but cinematic reproducibly 42.0–44.4 FPS; plaza recovers 59.9. Five-second attack sample localizes 3,705/3,988 CPU-thread samples under generated dispatch; video thread waits in 3,685/3,988. Hot generated chunks 804530A0/804520A0 need exact-region code mapping, not Korean Petari address substitution. Whole mixed 926-second run ~57.58 FPS with 371 underruns; no stability promotion. Real depth 110,410, clean exit 0/fallback 0/SMC failed 0. Ignored post-attack state opening-r81/StateSaves/RMGE01.s01 permits continuation, NOT cinematic replay or real-save acceptance. No game/Simulator remains. Next inspect hot exact-DOL generated ranges and semantics-preserving CPU optimization; stop repeating title/frontend checks.
- **R80 launcher responsiveness fixed:** normal Play remembers imported RMGE01 and starts the child. Main-thread blocking SDL_WaitProcess replaced with nonblocking polling, SDL event pumping and 50 ms sleeps, retaining successful/nonzero/error handling. Source-derived compiled regression covers all three terminal outcomes plus stale-error clearing and pending-child pumping. Repeated bootstrap, frontend build, package audit and repository tests pass. Runtime query now reports noWindowsAvailable for the hidden launcher rather than timing out; parent sample shows sleep/event pumping, 0% CPU, not blocking waitpid. Child module boot and TERM cleanup verified; visible child controls still not verified through this tool's same-bundle attachment. No FPS fix claimed. Before-change run independently recorded ~59.9 FPS/two near-shutdown underruns, reinforcing variability rather than a settings defect. No test processes remain. Next slow opening-scene/control interval through the known direct-runtime UI binding; do not spend another turn repeating launcher/title attachment experiments.
- **R79 normal-profile diagnostic:** GFX.ini exactly matches R75; core settings match apart from ordering/window position/IDs. Single direct runtime using normal imported data visibly reaches ready title. FPS sampled 59.9→43.9→59.9; JumpConnect simultaneously reached 326.7% CPU, later disappeared from top consumers. Five-second sample contains 809/3,831 CPU-thread samples in frame pacing waits, not a stuck main thread. Whole run ~54.37 FPS/29.06 kHz, 104 underruns, last at enqueue 12,811 of 23,496; final portion has no new underruns. This is sampled/startup/host-contended diagnostic evidence, not acceptance or proof all dips are external. UI attachment must wait until runtime registers: early getApp spawned an extra launcher, explicitly terminated. Clean UI close exited 0; no game/launcher/Simulator remains. Next use the ready-runtime binding for a normal-entry file-select/control check, then a slow opening-scene interval without concurrent compilation/capture bursts.
- **R78 normal import/handoff verified, performance still open:** keyboard navigation activated Browse, native picker selected the supplied WBFS, Extract and Play completed into the normal GalaxyPad profile and launched the sibling runner, which loaded the bundled module. Automated mouse events reached SDL at the right location but ImGui global mouse state was outside the window; no product mouse fix inferred. UI attachment targeted the hidden waiting frontend, so visible child gameplay remains unverified. Shutdown counters show ~49.94 FPS and 144 underruns over ~77 seconds, with 2,258 real depth reads and zero fallback/failed SMC. This startup run overlapped a frontend rebuild and is not a controlled performance comparison, but is explicitly not acceptance. Temporary diagnostics removed, clean frontend rebuilt/re-signed. Test processes stopped; no Simulator running. Next visible normal-entry gameplay and controlled slow-scene diagnosis; at most one Simulator at a time, per user reminder.
- **R77 frontend controls/import selection corrected:** generated Wii profiles now use Nunchuk left-stick movement, separate A/B, right-stick IR, X shake/Spin, shoulder C and trigger Z, with sideways=False. Focused compiled Wii/GameCube config tests pass; existing Quartz profile preserved. Branded launcher no longer scans Documents/preselects unrelated discs; rebuilt UI visibly shows no selected disc and the Nunchuk label. Canonical hash-pinned overlay and repeated bootstrap/package checks pass. **Browse automation did not open a picker**, so import/launch remains unverified and is the next UI issue. No launcher/game remains.
- **R76 normal frontend wiring improved:** CMake branding/profile now GalaxyPad (was moderngekko), and package provides the sibling `moderngekko-run` alias to GalaxyPadRunner that the frontend expects. Exact RMGE01/DOL restrictions are configured and checked against disc metadata. Normal launcher visibly opens using seeded 120 ms/dual-core defaults; a backed-up legacy profile's invalid 640x456 was corrected to 640x528 without changing controls. **Import/launch still unverified:** generic frontend suggests unrelated discovered discs and offers a sideways-profile replacement. Next make those paths Wii/Nunchuk-safe and test exact input through the frontend. All test processes stopped; G6 open.
- **R75 incremental default improvement:** isolated 120 ms audio reserve (vs R74 80 ms) retained ~59.92 FPS/31.98 kHz, reduced underruns 17→4 and backlog corrections 22→9 over comparable five-minute post-load checks with three control passes. Real depth reads, unchanged save, native-only clean exit. Not a stutter-free/audio-quality pass. New profiles now seed CPUThread=True/AudioBufferSize=120; existing Dolphin.ini files are preserved byte-for-byte, covered by an executable launcher-guard regression. Package rebuild/audit/checks pass. Next validate default frontend entry plus remaining audio/scene timing, not more title-only benchmarking. No runtime remains.
- **R74 five-minute uninterrupted Observatory check:** three visible control passes, no pause/trace/sample, save unchanged and clean native-only close. Whole-process 28,166 frames/470.033 seconds ≈59.92 FPS, DMA ≈31.99 kHz; 73,107 real depth reads. Five-minute post-load interval is verified by wall clock, not separate counters. **17 underruns/22 backlog corrections remain**, so audible/stutter-free acceptance is not claimed. Next investigate the audio queue reserve under near-reference production, not repeat the resolved resource diagnosis or inflate average FPS into completion. No runtime remains.
- **R73 corrected-package gameplay/lifecycle passes its bounded checks:** real one-star save loads without savestates; lateral movement, jump and visible blue Spin effect captured; pause subtitle follows state, resume clears it, and controls work afterward. Closing while paused exits 0 with no fallback/failed SMC. 26,667 depth reads; GameData hash unchanged. Live readings 59.3–59.9 FPS with a 58.8 resume sample; nine underruns remain and deliberate pause invalidates whole-run FPS. Next uninterrupted longer gameplay/audio check, then decide dual-core default; G6 not promoted. No runtime remains.
- **R72 runtime resource/EFB fix verified:** corrected normal package, dual-core, native 1×, untraced G5 fixture visibly selects Mario file 1. **24,966 real depth reads** across 10,600 frames, 59.92 FPS whole-run, about 31.98 kHz DMA, **zero underruns**, one startup-only backlog correction, four input transitions, clean exit 0/fallback 0/failed SMC 0. This closes the packaged missing-settings failure, not G6. Next corrected-package Observatory movement/Spin/pause/resume and sustained timing/audio; do not reuse R62–R71 disabled-depth performance as acceptance. No runtime remains.
- **R71 corrects the actual branch precedence:** compile flags define LINUX_LOCAL_DEV on this macOS build, selecting the first Sys branch before the Apple condition. The R70 iPhone-macro attribution was incomplete and its first patch insufficient; R71 still recorded zero depth reads and was stopped cleanly. Revised overlay excludes Apple from the LINUX_LOCAL_DEV branch and retains TARGET_OS_IPHONE for Apple platform selection. New source-derived preprocessor regression reproduces the old failure under the actual flag combination and passes five platform cases. Repeated bootstrap/build/audit/checks pass. Next run the rebuilt package to establish real depth reads; no runtime remains, performance acceptance still withdrawn.
- **R70 root cause confirmed:** first-depth diagnostic in the rebuilt package resolved `EFB-Diagnostic-r70.app/Sys/`, game RMGE01, configured EFB access=0, active=0, valid x=0/y=0. The Apple source branch tested presence of an iPhone SDK macro rather than actual target platform. New hash-pinned overlay `0010-apple-sys-platform.patch` uses TargetConditionals/TARGET_OS_IPHONE; macOS now selects Resources/Sys as intended. Bootstrap repeat/build/audit/checks pass. Temporary diagnostics removed from source and normal build; no runtime remains. Next runtime must demonstrate real EFB reads with this fix before performance/default promotion. This supersedes the earlier assumption that source inspection alone proved the compiled Resources path.
- **R69 runtime follow-up still unresolved:** the resource-layout fix passes the strengthened package audit, but the new file-select run still records zero EFB reads. Do not equate the corrected file location with proof of effective runtime settings. It exits cleanly with near-60 FPS and two underruns, but performance remains provisional. Next inspect/log the resolved Sys path and effective EFB configuration after game boot, plus the depth-read telemetry path. No runtime remains.
- **R69 packaging defect found; R62–R68 performance is not acceptance evidence:** macOS Dolphin resolves Sys under `Contents/Resources/Sys`, but the app builder copied it under `Contents/MacOS/Sys`. The pinned fallback default for CPU EFB access is False. Presence of RMG.ini at the wrong path did not prove active settings; prior statements implying required packaged EFB semantics were verified are withdrawn. Builder now uses the resolved Resources path, and the strengthened app audit rejects the old package and passes the rebuilt one. Runner/module hashes are unchanged. Dual-core default promotion is suspended pending corrected-runtime validation.
- **R68 untraced G5 functional regression:** dual-core/current package loaded the old zero-star G5 NAND, accepted A+B and pointer fixture, and visibly selected Mario file 1. 59.917 Hz graphics/31.980 kHz DMA, one underrun, four input transitions, clean exit 0 and no fallback/failed SMC. Historical final projection differs; this is fresh behavioral/cadence evidence, not an exact old-signature pass. Next longer untraced Observatory controls/lifecycle/audio coverage before default promotion. No runtime remains.
- **R67 dual-core diagnostic improves the matched scene:** same trace-on 60-second method yields 59.950 Hz frame/present (R66: 55.500), 32.004 kHz DMA (29.628), frame-start p99 17.672 ms (20.490). Visual title/Observatory preconditions passed on one fixture invocation. A short new regression-covered control fixture then demonstrated lateral movement, visible jump, and safe landing; Spin was sent but its effect was not independently isolated. Clean native-only exit; no runtime remains. Next G5 dual-core regression and longer untraced gameplay before any default promotion. Full G6 stability/audio acceptance remains open.
- **R66 corrected baseline:** visually verified title and Observatory, one fixture invocation, then exactly 60 seconds without input/pause. Traced single-core VI/frame/present rate is 55.500 Hz, DMA 29.628 kHz; exact interval and percentiles in PERF.md. This replaces R65 as the usable fixed-window diagnostic control. Next run equivalently traced dual-core for 60 seconds, then uninstrumented movement/G5 validation if warranted. Clean exit 0, fallback/failed SMC zero; no runtime remains. Defaults and G6 are unchanged.
- **R65 follow-up:** single-core Observatory reads 55.7–55.9 FPS (54.9 at close), with 147 whole-run underruns and native-only clean shutdown. The first fixture fired too early and a second invocation was needed; whole-run averages are excluded from A/B. Visual title readiness and post-fixture scene confirmation are now explicit in PERF.md. Dual-core remains a candidate, not a promoted default. Next require those readiness checks for a fixed-duration comparison, followed by movement/G5 regression. No runtime remains.
- **R64 promising isolated candidate, not promoted:** enabling only `Core/CPUThread = True` in a copied private profile reached 59.910 Hz over 156.985 seconds and 31.980 kHz DMA in the real-save Observatory fixture. Six underruns remain; seven frame gaps >=33 ms. Screenshot confirms the same scene; final projection matches R63, fallback/failed SMC are zero, save hash is unchanged, and normal close exits 0. R63 had different host contention and a longer observation interval, so this does not establish a controlled speedup. Next repeat single-core under current host conditions, then dual-core longer/movement and G5 regression before changing product defaults. No runtime remains.
- **R63 unsampled control fails performance acceptance:** the same packaged Observatory fixture loaded correctly, but the user observed 38.5 FPS and obvious lag. Later window readings recovered only to 53.0/52.2 FPS. Uninterrupted whole-run counters report 15,113 frames in 299.998 seconds (50.377 Hz), 837 audio underruns, and zero EFB reads. Concurrent unrelated host load confounds attribution; it does not excuse the failure. Clean close exited 0 with zero fallback/failed SMC. No runtime remains. Next isolate a measurable native-execution candidate against this saved-scene fixture; do not promote G6 or replay the tutorial.
- R62 validates the **argument-driven packaged bootstrap** with its signed module and an isolated copy of the real one-star save, without savestates. New regression-covered fixture `g6-observatory-save-load.json` reproducibly reaches Observatory from title. Uninterrupted diagnostic tracing settles at 55.135 Hz, and CPU sampling again points to native guest execution; this stationary view recorded zero EFB reads. See `PERF.md`. Full G6/D3 stable timing, audio, and default frontend/import coverage remain open. Next is the matching untraced/unsampled control, not another tutorial replay. R62 exited normally with zero fallback/failed SMC; no runtime remains.
- **Newest G6 result (R60/R61): the functional first-Grand-Star save loop passes.** All flipswitches completed, Grand Star obtained, Observatory reached, Terrace unlocked, in-game save confirmed, process exited cleanly, and a fresh process loaded the one-star file into playable Observatory without loading an emulator state. Movement/jump after load are visible. See `SAVE-AND-NAND.md` for exact evidence. Both runs exit 0 with zero fallback/failed SMC. GameData SHA-256 remains `5040acdd95157448d660fd02f03c16c17e240523bdfa889ccbd253f9fe5364a6` after reload. These results supersede the incomplete-progression statements below.
- **Do not promote full G6/D3 acceptance yet:** D3 also requires packaged-app coverage, music/sound-effects evidence, and stable timing. The standalone runner's Observatory title read 51.3–53.3 FPS, and R60/R61 still logged underruns. The new real in-game Observatory save provides a reproducible performance/lifecycle test entry without replaying Gateway or relying on emulator states. Next work is a bounded uninterrupted Observatory baseline/profile and packaged-entry validation, not another manual tutorial replay. G7–G15 remain open. No runtime or Simulator is left active.
- **Newest G6 continuation (R59): second key/cage and pipe interior proven.** Giant defeated, golden key collected, second cage opened, freed Luma reached, and pipe entered. The central flipswitch ring is visibly blue, plus one outer panel; remaining outer switches keep the Grand Star machine active. Resume R57 slot 6 SHA-256 `618a40597704f1234619bd7d20549fc6cf2f1ce21d5026d3807f44f85a11d23a` (two life wedges, central-ring checkpoint). Slot 5 now holds interior arrival, slot 7 second key drop, slot 8 second cage open. These supersede the older slot 5/6 descriptions below. First Grand Star pickup and Observatory in-game save/relaunch remain unproven. R59 exited 0 with `fallback=0`, `smc_failed=0`; no runtime remains.
- Latest host validation (R58): native pause subtitle follows actual core state, clears on resume, and returns on re-pause both at startup and after loading second-planet gameplay. Red close from paused gameplay exits with status 0, `fallback=0`, `smc_failed=0`, and no orphan. The private app rebuild/audit and Wii/Pipe/config/repository regressions pass. Current unsigned runner SHA-256 is `8509cf8b472785564b1272eab5bb8fab6a4794e4ca7f6c353cb05f31fccca2a8`; packaged runner is `9842e3f6b8b14e5d149cd81dcf86eee650c7f6001b09b4ffcf04a4af9c8cd8c6`. These supersede the prior runner hashes below; the accepted module is unchanged. No runtime or Simulator remains active.
- Second-planet continuation is still slot 4 (two life wedges). The bounded attempt defeated a regular enemy but did not prove the giant's defeat, second key, or cage unlock. Slot 5 preserves one regular defeated; slot 6 preserves a giant approach with one wedge, **not a verified stun**. Navigation was parked under the goal loop's unblocking ladder to implement the independently testable pause/freeze clarity fix. G6 remains open; do not repeat unchanged giant-chasing inputs or promote a screenshot animation to a progression claim.
- Latest G6 progression: R57 defeated the first small-planet key carrier, visibly collected its golden key, freed the Luma, completed its Sling Star transformation, and launched to the second gold planet. Current safe continuation is R57 slot 4 SHA-256 `0781718e46961735f601e2bebb41e0ee0ef6be696599857bbd35ce9caa90ba62`, with two life wedges on arrival. Slot 1 preserves the first cage opened; slot 2 preserves the key drop. First Grand Star and in-game save/relaunch remain open. The runtime exited cleanly after restoring slot 4; no game process remains.
- Automation correction: foreground the runtime explicitly before each short Pipe input sequence. A down-stick pulse without foregrounding left Mario stationary; repeating with foreground ownership moved him to the enemy. This is input-test setup, not evidence of a guest freeze. Screenshot/menu calls alone are insufficient to establish focus.

- September 6 resumption audit: PID 99094 has exited; no game process or Simulator was running. Protected R55 slot 3 has full SHA-256 `256b57886f9575b20cd58764c865674b19b4496c7a6c2fad9d709439720a88df`. A separate R57 copy of its NAND/config/state loaded the small-planet gameplay view successfully. The original R55 evidence is preserved. The historical PID/pause description below is superseded.
- Window-close stability fix: pinned overlay `0008-macos-window-close-shutdown.patch` routes the red close button through Quit's existing orderly shutdown, retaining the surface until core shutdown completes. Both running startup (R56) and paused, reloaded gameplay (R57) exited with status 0, `fallback=0`, `smc_failed=0`, and no orphan runtime. This closes the observed close-window orphan defect; it does not establish sustained performance or in-game save acceptance.
- The private macOS app has been rebuilt with that fix and passes package/module/signature audits. Unsigned runner SHA-256: `9f53e1919309097d0bb92b261ae23d6d634416fd10271f0fac79ce085f420448`; packaged signed runner: `13164fdf3598812469792838bc118620a7d137676e596f6bd8cee5d981710c60`. Wii mode, input/configuration, and repository safety regressions pass. No runtime or Simulator is left active after validation.

- Root starting revision: `289a87ae` (`main`, matching `origin/main` at session start).
- User-arranged working tree preserved: the two governing documents moved from the repository root into `docs/`; `ref/` and `.DS_Store` were untracked at session start.
- Host: Apple Silicon arm64, macOS 26.6.2, Xcode 26.6, macOS SDK 26.5.
- Booted Simulators: none at session start.
- GalaxyPad/game processes: none. CoreSimulator services alone were present.
- Free space: 80 GB available on the data volume at session start; approximately 70 GB remained after builds.
- Active disc identity: WBFS SHA-256 `bd0d3d4bc1376a8614fd8f4fee5df86be6bc676e9d617944918fda79ed9e3589`.
- Active disposable NAND evidence: ignored, isolated directories under `generated/runtime/`; fresh RMGE01 file creation is proven, but no Grand Star save/reload has been accepted.
- Stable runtime: arm64 `moderngekko-run`, macOS 14.0 minimum, Metal for visible runs and Null for headless checks, exact RMGE01 profile-guided O2/1,024 indexed-dispatch module SHA-256 `6fba4629eb07e79132a344bc2d68bf9f62627478d5a7dc8a19e1af291942c916` (99,510,616 bytes, cache suffix `1a7fde44f42859a5`). The normal hash-keyed build reproduces the measured candidate byte-for-byte from ignored local profile SHA-256 `f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d`.
- Private package: ad-hoc-signed arm64 `generated/macos/GalaxyPad.app`, bundle ID `com.galaxypad.GalaxyPad.macos`; the accepted PGO module is included, and disc/extracted inputs, profiles, and saves are omitted. Deep signing produces packaged module SHA-256 `25e17d0e730b512f20083db26d3a7f58bc60da126161fe34c227357372c65393` from the audited unsigned build hash.
- Current G6 continuation supersedes the older rabbit checkpoint below: the native-1× R55 lineage has genuinely completed all three Gateway rabbit catches, the tower sequence, Spin unlock, the first Launch Star route, and all five Black Hole planet Star Chips. Mario used the resulting Launch Star and landed on `HeavensDoorSmallZone`. All four roaming `KuriboMini` actors are defeated; protected slot 3 SHA-256 `256b5788...` preserves that four-clear state with two life wedges before the separate key-carrying `ChildKuribo` encounter. The live runtime PID 99094 is deliberately paused at that checkpoint and has survived more than six hours of progression, effects, death/respawn, and repeated state loads. The key carrier, cage unlock, first Grand Star, Observatory in-game save, and clean in-game save/relaunch/load proof remain open.

## Open defects and blockers

- `ref/sunpad` remains clean at `fcdc1411e483a86ca80ec82e7cd53839c51ff865`; the reviewed `efd42ca45457af5950e0558c66703cb766959e11` baseline is reproduced separately without rewriting it.
- The WIT 3.05a arm64 slice exits silently on this host; its x86_64 slice works under Rosetta. This is recorded as the stable invocation until a source-built arm64 tool is proven.
- The G5 sustained audio defect is resolved, not hidden by a larger buffer: cadence telemetry traced the matching frame/DMA deficit to RMGE01's scheduler idle spin. Exact-DOL idle skipping restored 59.884 Hz/31.946 kHz; the reviewed ±2% Apple servo at an 80% reserve then completed the full route with zero underruns across a 156.6 ms producer gap. The accepted O2 identity is unchanged. Perceptual pitch, Wii Remote speaker, gameplay cue, transition, interruption, and soak evidence remain open under G6/G9.
- G6 has fresh visible evidence through the opening story, Peach's letter, Star Festival movement/jumping, pointer-driven Star Bit collection, the village route, the Bowser attack, and Gateway Galaxy. A live September 5 re-audit invalidated the earlier R52/R53 catch labels: their named slot files held collector count 1 and the grass actor in `Hide`, so their screenshots/dialogue do not prove the claimed grass catch. The current native-1x lineage genuinely holds collector count 2/3 with the crater and upper-pipe continuations stopped. On September 6, a depth-valid, uninterrupted Star Bit shot verifiably changed the released grass actor from root `Runaway` to `BlowDamage`; a separately replayed ordinary-input approach reduced actor separation from 1,356 to about 250 world units. Protected slots preserve both the verified stun and the near-contact route. Final Spin/contact and collector 3/3 remain unproven. Spin unlock, first Grand Star, Observatory save, and an in-game save/relaunch/load also remain unproven. These are emulator states, not the required in-game save proof. The older accepted-C1024 true-1x run confirmed the user's visible stutter report: a live title sample fell to 19.4 FPS and then fluctuated mostly from 29 to 38 FPS. Clean shutdown reported only 42.047 frames/s and 22.458 kHz DMA production over 2,213 seconds, 3,620 underruns, a 542.5 ms maximum frame gap, and 62,936 of 93,065 frames (67.63%) separated by at least 20 ms. This is failed G6 playability evidence, not an acceptance pass.
- The September 6 R55 continuation closes the stale progression claims in the preceding historical bullet: collector 3/3, tower activation, Spin, Launch Star use, five Star Chips, and entry to `HeavensDoorSmallZone` are now visibly proven. It does not close G6 until the key carrier, Grand Star, Observatory save, and clean relaunch/load pass.
- Indexed dispatch materially improves but does not yet close G6. On an exact matched Star Festival route it produced 55.104 Hz graphics and 29.434 kHz DMA versus the accepted linear control's 51.528 Hz/27.515 kHz, a 6.94%/6.97% gain; underruns fell from 280 to 155. The visible checkpoint read 45.3 FPS and retained the exact projection and 44 input transitions. A blanket `always_inline` paired-single-load candidate was rejected after regressing the same route by 6.63%/6.75% and dropping visibly to 15.7 FPS. G6 remains unmet because indexed dispatch is still below reference cadence and the required progression/save loop is incomplete.
- Post-indexing experiments did not justify another promotion. Centralized GQR0 paired-single helpers reduced duplicated code but lost 0.33%/0.32% to an immediate control (55.716 Hz/29.733 kHz versus 55.901 Hz/29.830 kHz). Removing the already-vetted chassis entry's duplicate host-call check retained exact state and reached 56.230 Hz/30.019 kHz with 120 underruns, but its 0.59%/0.64% edge is within the rejection band rather than a material playability change. Both temporary source changes are restored.
- Exact per-frame EFB correlation rejects duplicate suppression as the next performance fix. The matched 1× route recorded 31,349 depth reads in 12,377 frames with peeks, at most three per frame. Its 1,473 repeated same-frame coordinates were value-identical but represented only 17.799 ms (0.260%) of 6.840 seconds total EFB time because Dolphin's deferred tile cache already served them cheaply. Default-off tracing now records coordinates, values, latency, guest PC/LR, and frame identity; EFB semantics remain unchanged.
- The live post-attack review confirms the slowdown is scene-dependent. Sparse views reached 59.9 FPS, while the attacked plaza and effects-heavy views commonly ranged from about 40 to 50 FPS. A 10-second sample placed 5,932/7,000 CPU-thread samples in `StaticRecompCore::Run` and 5,336 beneath `chassis_dispatch`; the video thread was waiting in 4,166/7,011 samples and synchronous EFB-depth wait appeared in only 48. A matched phase trace/control found sub-millisecond presentation but 22–24 ms p95/p99 frame intervals, localizing the main deficit before present.
- Profile-guided optimization is accepted as the next semantics-preserving improvement. On a fresh matched 44-transition route, PGO produced 57.444 Hz graphics and 30.784 kHz DMA with 79 underruns, versus 54.961 Hz/29.455 kHz and 175 underruns for the accepted non-PGO control: +4.52%/+4.51%, with the exact projection and native-only signatures. A fresh G5 confirmation retained 59.77 Hz/31.98 kHz with zero underruns. This materially reduces the defect but does not prove consistent 60 Hz playability or complete G6 progression/save criteria.
- A subsequent 86.8-minute visible PGO progression run did not reproduce 18 FPS before the Bowser trigger: inspected views ranged from 47.9 FPS in the densest town/lake composition to 62.5 FPS, usually 55–60. Clean shutdown averaged 56.753 Hz graphics and 30.301 kHz DMA, retained `fallback=0`/`smc_failed=0`, and recorded 64 input transitions. However, 1,678 underruns and 51 backlog drops remained, so this is improved failure evidence rather than G6/audio acceptance. The run reached the lower town route but did not re-trigger Bowser, Gateway, Spin, Grand Star, save, or relaunch/load proof.
- A fresh uninterrupted PGO reproduction triggered Bowser and reached Gateway. The effects-heavy ship cinematic read 42.5–43.0 FPS, active post-attack traversal generally read about 44–53 FPS with a 39.9 FPS checkpoint, and the castle transition repeatedly read 37.0–39.4 FPS. Gateway directional movement and jumping were visibly proven at roughly 45–53 FPS. The user terminated this scale-3 run after it appeared frozen during a tool pause; it did not provide clean-shutdown telemetry or Grand Star/save proof.
- The live Gateway slowdown now has three bounded contributors. A covered/resized game window briefly read 22.3 FPS, while the identical fully foregrounded stationary state recovered to 59.9 FPS and active traversal read 50.3 FPS. Two 10-second profiles placed 1,450/7,401 and 1,629/7,873 CPU-thread samples in synchronous Metal depth-readback waits; moving the pointer to a corner did not reduce them. The run was also discovered to have effective `InternalResolution = 3`, so its screenshots are valid visible-failure evidence but not a 1x baseline. The next relaunch must explicitly prove scale 1 and retain RMG's real EFB/deferred-invalidation semantics.
- The explicit native-1× continuation isolates the dominant configuration failure. Title/story/still frames held 59.8–60.0 FPS, ordinary Star Festival traversal generally read about 49–54 FPS, the Bowser arrival read 41.7–44.9 FPS, and castle abduction read 38.8–39.9 FPS; Gateway then returned to 59.9–60.0 FPS during movement. Clean shutdown after 10,032.273 seconds averaged 57.085 Hz graphics and 30.479 kHz DMA, retained `fallback=0`/`smc_failed=0`, and recorded 302 input transitions. It still logged 57,975 frames at or above 20 ms (10.123%), 2,692 underruns, and 48 backlog drops, so residual effects-scene pacing/audio remain open and G6 is not accepted.
- Fresh runtime profiles previously defaulted to frontend `resolution=1920x1080`, which means Dolphin EFB scale 3 in this frontend and directly caused the reproduced approximately-20-FPS floor. Hash-pinned overlay `0012-native-resolution-default.patch` now creates `640x528`/scale 1 profiles; the packaged seed's invalid `640x456` was corrected to the same value. The frontend regression test, fresh-profile smoke, rebuilt ad-hoc-signed app, and private-package audit all pass. Existing explicit user resolution choices remain untouched.
- The apparent native-1× Gateway freeze was not a guest deadlock: closing the window left the exact runtime process executing near 60 Hz until it was found and stopped. Continuing the same state reproduced a real heavier hotspot instead: Bowser's attack generally read about 31–44 FPS and the castle-abduction sequence sustained roughly 23–36 FPS before Gateway recovered to about 60 FPS. An active Gateway sample placed 4,583/7,038 CPU-thread samples below generated `chassis_dispatch`; synchronous Metal depth-readback wait accounted for 236/7,038 samples (3.35%), so portable AOT guest compute is the primary current limiter and EFB synchronization is secondary.
- A Gateway-inclusive PGO profile was trained and compared from the same native-1× state with the same eight-sweep/130-transition input signature. The accepted module produced 58.059 Hz with 13.081% of frames at or above 20 ms; the candidate produced 57.825 Hz with 13.392% at or above 20 ms. Both had 47 underruns, matching projection `0xf8f6f1fa3d9e4c07`, `fallback=0`, and `smc_failed=0`. The candidate is rejected; accepted module SHA-256 `6fba4629eb07e79132a344bc2d68bf9f62627478d5a7dc8a19e1af291942c916` remains selected.
- The long G6 run above was at EFB scale 3, not native 1×: frontend `config.ini` overrode `Config/GFX.ini`. Matched true-1× dual-core runs measured accepted O2/4,096 at 51.20 Hz/27.34 kHz, O2/1,024 at 53.09 Hz/28.31 kHz, and O2/256 at 52.87 Hz/28.19 kHz. All remained native-only with zero failed SMC. The 1,024 split is the best bounded result (+3.7%) but still about 11% below target. A 61.17 MB `-Oz` candidate regressed to 33.75 Hz/18.04 kHz and 651 underruns and was rejected; its temporary template change is reverted.
- Generated-module cache identity now includes explicit C chunk size and dispatch lookup mode through hash-pinned overlay `0008-module-cache-codegen-options.patch`. The normal script generated distinct suffix `fd7022cf46adb6b9`, recorded both options in its manifest, and reproduced the isolated 1,024 module byte-for-byte. Its G5 file-select regression is closed by the cooled control below; active G6 performance remains open.
- Three immediate post-build G5 reproductions exposed load sensitivity: C1024 single core recorded 13 underruns/31.46 kHz; accepted 4,096 single core recorded 30/30.52 kHz; C1024 dual core recorded 26/30.74 kHz. A cooled sampled diagnostic improved to 10/31.70 kHz and confirmed floating-point/paired-single helpers, not `SelectThread`, as the hot leaves. The decisive cooled unsampled C1024 control then produced zero underruns and 31.97 kHz, so G5 is restored. Dual core remains rejected for the file-select route.
- The package scripts previously hardcoded the 4,096 cache path, allowing the old signed module to survive after the active module changed while the audit still passed. Both now consume the audited absolute active-module marker; the audit independently signs a same-named temporary source copy and requires its hash to match the packaged dylib. The stale package failed this new check before the corrected rebuild passed.
- The native frontend and window still expose ModernGekko branding; original GalaxyPad shell/icon work belongs to G12.
- ModernGekko's SCM metadata step prints non-fatal `fatal: bad revision '^master'` for the pinned detached/patch-only checkout, and ld reports duplicate static libraries. Both builds still complete; neither warning is treated as runtime proof.

## Exact known-good commands

```sh
shasum -a 256 ref/supermariogalaxy.wbfs
arch -x86_64 ref/tools/wit-v3.05a-r8638-mac/bin/wit ID6 ref/supermariogalaxy.wbfs
arch -x86_64 ref/tools/wit-v3.05a-r8638-mac/bin/wit DUMP -l ref/supermariogalaxy.wbfs
./scripts/verify-disc.sh ref/supermariogalaxy.wbfs generated/extracted/run1
./scripts/audit-aot.sh
./scripts/audit-module.sh
GALAXYPAD_PGO_PROFILE=generated/pgo/rmge01.profdata ./scripts/build-module.sh
./scripts/smoke-macos-runtime.sh headless 55
./scripts/build-macos-app.sh
./scripts/audit-macos-app.sh
```
