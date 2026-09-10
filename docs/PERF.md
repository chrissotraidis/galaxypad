# Performance and runtime telemetry

## R706 — presentation telemetry platform boundary verified

MTLGfx.mm:PresentBackbuffer currently presents through either presentDrawable
or a scheduled-handler drawable present. Neither proves display completion.
Apple's MTLDrawable presentedTime describes onscreen host time (zero for an
unpresented/skipped drawable); addPresentedHandler is the corresponding callback.
However the installed iPhoneSimulator.sdk Metal/Headers/MTLDrawable.h omits BOTH
declarations. iPhoneOS.sdk and MacOSX.sdk expose them. The Simulator header's
typedef comment mentions presentedTime but does not declare the API. Do not
infer Simulator support from that comment or physical-iOS documentation, inject
an undeclared selector, or rename command-buffer completion as screen FPS.
No renderer mutation/build made. Mac/device callback telemetry remains feasible;
Simulator presentation-rate proof remains separate from after_frame_event/VI.
Reference: https://developer.apple.com/documentation/metal/mtldrawable/presentedtime

Read-only physical-target refresh: devicectl list devices exited0, No devices
found; security find-identity -v -p codesigning reports0 valid identities.
This limits hardware validation, not ongoing CPU/runtime implementation work.

## R705 — current gameplay wall-stack sample

Live66439/84f0fe05; screenshot before5s/10ms sample verified unobstructed invaded
plaza. sample38272 exited0, generated/plaza-sample-r705.txt. CPU428 samples,
37 float-future waits and12 BlockingLoop waits; ModManager::Dispatch15 leaves.
Generated chunk804B60A0 has12 direct samples under primary dispatch,805170A0
has8 there plus1 elsewhere. These are address-range chunks, not semantic SDK
functions; collapsed offset lists do not provide per-instruction weights.
Broad generated work remains; no single hot routine or major new dispatch win
established. Existing R450/R466/R470 already constrain matrix, restore, mapping
and compiler proposals. Do not repeat these unchanged from this short sample.

## R703 — candidate preserves native movie path, no major gameplay gain

Same84f0fe05/66439: movie45s capture59.952020 frame-event Hz, VI~59.94/speed~1;
visibly returned to invaded-plaza gameplay. Eighteen emitted timing windows5415
calls/0fallback,weighted rounded mean1.654606ms wall; last partial unflushed.
Post-movie stationary30s37.557276Hz,speed0.577–0.696, versus historical35.51Hz
not controlled enough to prove a gain. No build/profiler during captures.
VM movie/post compressions8631/631,decompressions10404/2485,swapin/out0/0.
Candidate plaza checkpointBFA5E5B8 retained for repeat work, not restore-proven yet.
Do not keep tuning dispatch or movie decoder as if they explain the remaining
deficit. Representative CPU execution and host scheduling/memory effects remain
open, with graphics waits a contributor rather than an established sole cause.
Evidence candidate-movie-r703.json,candidate-postmovie-r703.json/.png,R700log.

## R701 — no major dispatch gain; quiet interval remains slow

Selected-file sample after0030:10ModDispatch/254CPU samples versus12/254 before;
20future waits versus21. Video20EFB completion/253 versus18/254,71condition waits
versus68. Small sampled wall-stack differences are not a controlled/significant
CPU-time reduction. This path is not established as the major deficit.

After full regression suite PASS and native resume, quiet45s capture with no
intermediate tool/screenshot/build/profiler activity:1704events/37.000734s=
46.053140Hz; rolling speed0.573–1.0025. Systemcompression0,swapouts0,swapins4,
decompressions1447. Simply making observation quiet did not cure slowdown; host
scheduling remains uncontrolled. Keep native movie decoder progress; prioritize
representative gameplay instead of repeating this file-select experiment.
Artifacts dispatch-selected-sample-r701.txt,quiet-selected-r701.json,check-r701.log.

## R700 — dispatch candidate live result inconclusive

Installed84f0fe05/PID66439 after clean stop of old4942411a, which is backed up in
generated/candidates/r695-baseline with its checkpoint/preferences. Same module
and runtime flags. Selected-file30s capture:1251events/26.899989s=46.505595Hz,
zero systemswapin/out/compression,1297decompressions. No build/profiler during
window. This does not establish a gain over old selected-file54.4Hz or a controlled
regression: host state and scene animation timing were not matched. Candidate
gameplay/movie hook exercise and dispatch attribution remain pending.
Old checkpoint correctly refused on new app identity; no guard bypass. Keep
baseline and candidate evidence distinct. generated/dispatch-file-selected-r700.json.

## R698 — compression churn and missing dispatch range rejection

Retained invaded-plaza scene, same63074/4942411a:30s capture71581 yielded570 events
over21.200065s=26.886710Hz. System counters increased298743 compressions/124514
decompressions, with zero swapins/out. At16KiB/page that is4.895GB compression
activity, NOT net growth or disk traffic. First snapshot ChatGPT111%CPU, renderer
63%; no unrelated processes changed. pmset had no recorded thermal warning;
that is not clock-frequency proof. generated/plaza-r698.json.

Separate3s10ms sample15437:259/thread, CPU11 float-future waits,32 ModManager::Dispatch
under chassis_dispatch+348; Video134 timed condition waits,9 PeekEFBDepth/Metal
completion,45 RunVertices. Not exclusive CPU percentages or complete frame costs.
vmmap91240:521.3M footprint,841.1M peak; writable403.9M in swapped category,
not proof those bytes went to disk. Snapshot's corpse label did not mean game
death: PID and subsequent logs verified live. No profiler during baseline.

Source showed0029 fast range reject only in HandlesAddress, not Dispatch. Added
same rejection AFTER startup callbacks and dynamic pending returns to avoid two
negative hash lookups outside all static hooks/patches. Tests cover null/startup,
preserved register state, patch hits, negative holes/endpoints, pending returns
outside range with wrong/correct SP, and reload. ASan/UBSan PASS. Candidate84f0fe05
built, not deployed; no gameplay benefit proven. Canonical0030/bootstrap hash.

Checkpoint restore also retains uncompressed undo state until shutdown/next load.
Saved header reports114630753bytes (~109.3MiB), source SaveToBuffer retains its
buffer. Exact live undo size not measured. This diagnostic overhead cannot explain
slowdowns predating checkpoints; no speculative undo-lifetime change applied.

## R696 — same-session movie full speed, post-movie gameplay slow

Same R695 app4942411a, module3acdcddc, PID63074, settings and sole Simulator.
After visible Star Festival traversal, PrologueA visibly advanced and returned to
the invaded plaza. No rebuild, profiler or setting changes during captures.

- Movie45s capture: seven wholly contained frame windows,2241 events/37.400666s
  =59.918719Hz, VI59.939–59.940, speed0.997942–1.000006.
- Eighteen emitted decoder windows:5415 calls, zero fallback, weighted rounded
  means1.552835ms wall/1.540969ms CPU. Worst call18.624ms wall paired2.679ms CPU:
  15.945ms outside active CPU, not enough to distinguish scheduling from waits.
  Final partial window is not flushed; do not assert5591 accepted from this log.
- Post-movie stationary plaza30s capture: four whole windows,767 events/21.599933s
  =35.509369Hz, VI35.017–36.584, speed0.570135–0.635698.
- System VM movie/post:swapins0/8,swapouts0/0,compressions3358/10625,
  decompressions217/4033. Host pressure is not excluded; these sequential scenes
  are not a controlled host A/B. No unrelated processes changed.

Evidence: generated/{movie-r696,post-movie-r696}.json, post-movie-r696.png and
ios-runtime-r695.log. Frame events are not display completions; screenshots show
movie progression/return, not audio sync or measured presentation cadence.
Interpretation: this movie decoder is not the dominant sustained slowdown in
this run. Prioritize CPU work and graphics synchronization in the retained plaza
scene; do not repeat movie navigation or decoder microbenchmarks without a new
failure. R693 malformed XF remains intermittent/unresolved, absent so far here.

## R693 — live VI/speed estimates confirm simulation slowdown

Installed43b624f6,61558reachesfilelist. Five-secondengineframewindows~23–32Hz,
upstreamVIrolling20–33Hz,speed0.33–0.56. Startup~60events/59.94VI/speed1.
This supports real emulation slowdown, not just misseddisplaycounterobservations;
CPUexecutionandblockingwaits remaincandidates. Newlogios-runtime-r693.log.
No profiler/build duringmeasurement. RunendedonmalformedXFcommandassertion
cmd2=61E30E70 at22:37:46; notstabilityacceptance. Checkpointsneverinvoked.

## R689 — correction: historical 'presented' counter counts engine frame events

Runtime diagnostic_frame_count increments in after_frame_event. It is not a
display-completion counter; historical 'presented FPS' claims in this journal
must be read as engine frame-event cadence. Visible screenshots/transitions are
separate evidence and do not establish display timing. Candidate logs now label
counter_source=after_frame_event while retaining presentedkey for compatibility.
Added existing any-thread rolling GetVPS/GetSpeed estimates to5sopt-in summaries;
not exactVIcounts over those windows. Candidate02711110 built,notinstalled.
Installed c00098d3/live52374 unchanged. Next justified deployment can distinguish
simulation rate from frame-event rate. No performance improvement claimed.

## R684 — converter benchmark insufficient for runtime promotion

Unsanitized native extracted-reader benchmark8 alternating-order pairs,50Mcalls
each, full-output checksums identical/nonzero. Candidate wins6/8pairs but loses2,
with substantial host/order variation. Original4.54–7.30ns/call,candidate4.06–6.47.
Evidence generated/normal-output-benchmark-r684b.csv. This is not full indexed
vertex-loader or Simulator timing. Keep isolated; no app rebuild/default change
or FPS claim. Initialr684.csv uses ineffective lowbytechecksum and is superseded.
Further tiny converter timing loops are not the main performance queue.

## R683 — normal-reader redundant cursor work removed in isolated codegen

R676 sample's13 normal and10texcoord leaf observations motivate software-loader
work, not enabling executable-code-generating loaders. Actual Simulator object
Normal_ReadIndex<u16,s16,1> has repeated global output pointer updates. Isolated
local-pointer candidate removes them:63→55staticinstructions in real translation
unit with original flags.500000 sanitizer comparisons match normal reader bytes,
caches/cursor/guards. Caller-owned separate output allocation required; arbitrary
aliasing is not covered. Harness tests/probe-normal-output.py; staged output under
generated/normal-output-r683. No product source change, measured throughput or FPS
gain yet. Benchmark before integration; whole-loader/depth/render gates unchanged.

## R680 — live wall/CPU comparison identifies a non-compute outlier

Eighteen native movie windows5409calls, zero reported fallback, weighted wall
2.791ms/CPU2.767ms. Worst emitted call25.990ms wall but2.091ms thread CPU, in
window ending epoch1788920046.422117. Roughly23.899ms was not active CPU execution.
Wait/descheduling is supported; exact wait source and the previous63ms incident
are not identified. No expensive decoder arithmetic change justified by this
outlier. Movie returned to gameplay; remaining partial window unflushed while
session stays live. Do not infer full movie duration/audio or all5591calls from
these summaries. Gameplay14–29FPS remains a separate major blocker. Evidence
generated/ios-runtime-r679.log, no build or sampling profiler during playback.

## R677 — native movie usually has headroom, rare wall-time stall remains

R676run movie5591native/0fallback, visible return, clean stop. Window means
2.333–3.884ms for validation+decode+copy. Worst63.209ms at epoch1788918573.546146
window, overlapping presented54.423FPS/min43.636 then60.004 recovery. Remaining
movie windows mostly~60FPS. Do not describe cutscene stutter as fully solved.
Native wall time includes descheduling. New opt-in CPU-time diagnostic pairs CPU
time with the maximum wall-time call, so next spike can distinguish elapsed wait
from execution cost. Builtb8bf6d05, not installed. Audio timing remains unverified.
CLOCK_MONOTONIC decoder and CACurrentMediaTime UI origins differ; join via epoch
and dated host logs. Final unload window includes idle after movie, so seconds
are not source-duration proof. Prior R458–R470 reject repeating broad dispatch/
layout experiments without a new falsifiable discrepancy. Vertex software path
is intentional no-JIT, not a configuration mistake; replacement requires parity.

## R676 — deployed fast-rejection candidate, no broad speed claim

At Star Festival spawn on f55578e4 app, five-second windows31.66–37.27FPS,
minimum roughly-one-second observations24.55–25.00. These are different scene/
host observations fromR674 and do not establish a causal optimization percentage.
Live log generated/ios-runtime-r676.log; CPU sample ios-gameplay-r676.sample.txt.
CPU18/250futurewait samples pair with video18/250PeekEFBDepth→Metalcompletion;
video42/250vertexloader, hooklookup6/250. Remaining work is broader than mod
lookup. Sampling perturbs its own window; unsampled windows also remain slow.
Across140s covering files/story/gameplay, system swap-in/out and compression
counters did not grow;15205pages decompressed. No attribution to disk swap growth
for that interval, but no claim that host contention or memory pressure is absent.

## R674 — live gameplay sample separates non-movie costs

**Live native movie breakthrough:** same R672 candidate logs first native frame
acceptance, and invasion movie visibly advances. Complete movie-only presented
windows ending20:20:30.654 and20:21:01.454 are1827/30.599504=59.706850FPS and
1847/30.800243=59.967060FPS. Historical byte-only mobile movie windows were40–41;
not a simultaneous controlled A/B. `generated/ios-native-movie-r674.sample.txt`
confirms actual native decode stacks67/256 CPU-thread samples, with47/256 in
PrecisionTimer sleep/yield/time checking. Captured movie image
`generated/ios-native-movie-r674.png`. This is sustained in-game presentation
evidence, not yet exact source-frame duration, full audio or completion acceptance.

Final: movie returned to gameplay; following full window24.935638FPS. Clean
shutdown20:22:47.440failed0 reports5591 native accepted/0 fallback, matching the
source movie frame count. This closes first live candidate eligibility/playback
and return evidence, not exact frame uniqueness, duration or audio synchronization.

Earlier in this same R672 native-THP opt-in run, before movie callback acceptance:
Story windows roughly57–60FPS; hill/village windows31.655,26.928,27.746FPS.
Bounded `sample 46228 3 10` at20:16:02.676local produced250 samples/thread,
`generated/ios-gameplay-r674.sample.txt`. Sampling can perturb its overlapping
window; subsequent unsampled windows25.747/26.020FPS also remain slow.

CPU thread:29/250 samples wait on a float future below chassis_dispatch;
video thread:28/250 wait in PeekEFBDepth→StagingTexture::Flush→Metal completion.
This supports synchronous depth-readback cost, not permission to fake depth.
Video thread143/250 waits on a timed condition;27/250 are vertex-loader stacks.
CPU work otherwise spans generated chunks and dispatch;36/250 land directly in
StaticRecompCore::Run and8/250 in ModManager::HandlesAddress below host-call lookup.
These are sampled wall-stack counts, not exclusive CPU percentages or frame-time
accounting. No single generated gameplay kernel dominates this short sample.
Prioritize dispatch/core costs and correct readback synchronization after native
movie integration; do not infer pure GPU saturation or physical-device speed.

## R652 — deployed default-path verification

Fullsuite passed, installed6f41c070 launched without byte override. Normal route
reaches invasion movie and activationpc80452a2c/eae0000000 appears. This verifies
the default, not a new benchmark result. Pair remains0; VI recorder disabled for
long gameplay. Screenshot generated/ios-default-byte-r652-movie.png; log
generated/ios-runtime-r651.log. Continue same31065/27754 beyond movie for broader
stability/progression; no repeated identical timing loop. Full60Hz/audio gates open.

## R650 — enabled confirmation supports byte-only mobile default

Same enabled28264/app54786759/module3acdcddc repeats decoder byte activation.
Movie-only1264/30.699525=41.173276FPS and1247/30.500521=40.884548FPS;
prior enabled40.195, disabled35.387/36.053. This supports an incremental default
decision, not exact causal percentage: movie phases and host conditions differ.
Still below60Hz. No further identical benchmarking planned. Source now sets
GALAXYPAD_LC_BYTE_FAST=1 before mobile UIApplicationMain without overwriting an
inherited setting; paired-store remains off unless explicitly requested. Compiled
default/opt-out/pair-isolation test passes; both platform app builds pass.
New candidate not installed yet; next actual default-path activation proof.
Log generated/ios-runtime-r649.log; screenshot lc-byte-confirm-r650-movie.png.
VI dropped17321; no late CPU timing. Clean stop/save unchanged; Simulatoroff.

## R648 — byte-disabled movie control is slower; confirmation needed

Same app54786759/module3acdcddc/save and settings except byte0 (pair0/QoSNO).
Full movie windows1097/31.000029=35.387064FPS and1096/30.400043=36.052580FPS,
ending18:21:28.096 and18:21:58.497. R647enabled40.195464 is roughly11–14%
higher. This is a promising sequential comparison, not an exact causal estimate:
navigation duration, host scheduling and movie phases differ. No default change;
next one enabled confirmation before deciding. No byte activation in control.
Screenshots generated/lc-byte-control-r648-movie.png and movie-window-end.png;
log generated/ios-runtime-r648.log. VI dropped26209, no late CPU-timing result.
Clean stop18:23:34.642failed0/session76274exit0, Simulatoroff, save unchanged.

## R647 — mobile byte-cache activation, not yet a paired gain

Same Simulator app54786759/module3acdcddc, byte1/pair0, QoS experimentNO.
Normal zero-star route reaches invasion movie. Activation at pc80452a2c/ea
e0000000 proves the guarded byte path runs on iOS. Full presented window ending
18:03:53.137:1234frames/30.699982s=40.195464FPS. Movie inspected before and after;
screenshots generated/lc-byte-r647-movie.png and movie-window-end.png. No disabled
comparison yet; no speed attribution or default promotion. Still below60Hz.

VI trace capacity16384 was exhausted during navigation (dropped23207 at shutdown),
so no movie CPU timings can be extracted. Log generated/ios-runtime-r646.log;
trace generated/runtime/lc-byte-simulator-r646-vi.csv contains early data only.
Clean stop18:05:15.662 failed0/session6596exit0, soleSimulatoroff. Save unchanged.
Next same-artifact byte0 movie comparison with complete presented windows.

## R642 — same-build QoS off control; park priority tuning

Installed54786759/module3acdcddc, explicitCPUflagNO: requested21→21/setResult-1.
Same LC0 and visible stationary center pointer/file selection. Helper69514exit0:
1534VI/30.014613s=51.108439Hz, CPU15.778782ms/VI, EFBelapsed2.304858ms/VI,
process179.223517M instructions/54.993684Mcycles perVI. EnabledR64152.610632Hz,
CPU15.718705ms. Roughly3% frame-rate difference, essentially unchanged CPU time;
not convincing against prior variability. Simulator outer window is smaller in
R642; internal drawable remains1210x834. Host/thermal/display differences prevent
strong causal attribution. Park QoS tuning, keep defaultOFF, no promotion or
further generic priority sampling. This does not prove priority never matters.
Evidence runtime/qos-cpu-control-r642/{vi.csv,process-work.json,work-summary.json,
timing-summary.json}, qos-control-r642-file-select.png, ios-runtime-r642.log.
No dropped rows; runtime8598/session27787 cleanexit0/failed0 at17:22:45.067.
Simulator shut down. No game/Simulator running during subsequent build.

Zoom-out next lane: real-device performance, not additional touch verification.
devicectl again no devices; requested optional connection from user. Current
app CMake/provision/module scripts hard-code Simulator. Started isolated
iphoneos core build via GALAXYPAD_IOS_SDK=iphoneos, session85533,
generated/build-ios-device-core-r642.log, buildroot generated/build/ios-device-core.
Existing script default staysSimulator; explicit allowlist rejects invalidSDK
exit2. Separate unsigned device toolchain; same pinned runtime/source, Release,
fourjobs.41Gi free at preflight. Device framebuffer fetch retains existing native
branch; Simulator-only patch is guarded TARGET_OS_SIMULATOR. No device execution,
signing, provisioning or performance claim. Next poll same85533, audit iOS platform
objects, then adapt provisioning/module/app paths without replacing existing lanes.

## R641 — queue hint rejected; actual guest-thread request verified

Same d5871ba7 candidate explicit queue flagNO (7066/session49342) versusYES
(7288/session5004) both log worker25/CPU21. These are REQUESTED QoS classes:
SDK sys/qos.h documents qos_class_self accordingly; old actualQoS label was
misleading, not evidence of effective scheduler priority, frequency or core.
25=USER_INITIATED,21=DEFAULT. Queue setting did not affect CPU request; rejected
before claiming any FPS comparison. Both clean stop failed0/export1, sessionsexit0.
Logs generated/ios-runtime-r641-{control,enabled}.log; optional VI traces in
generated/runtime/qos-{control,enabled}-r641/ are not matched performance windows.

Removed ineffective queue setting. New Simulator-only default-off
GalaxyPadDevCPUUserInitiatedQoS applies pthread_set_qos_class_self_np on the first
CPU-thread VI, once only. No guest time/clock changes; logs before/after/result.
New build49965exit0, SHA547867590b1388dbbfe9a70b17e82a3700435818e04206cc97bf3ffc7457ed9b.
Installed on sole iPad. Enabled launch7767/session98543 logs at17:12:02.343:
CPU experiment1 requestedBefore21 requestedAfter25 setResult0. Worker remains25.
This verifies intervention reaches the intended thread, NOT a performance win.
Log ios-runtime-r641-cpu.log; VI path runtime/qos-cpu-r641/vi.csv (flush onexit).
Next visible-pointer file-selection work capture, then same artifact explicitNO
control/reverse repeat; do not compare startup counters as a performance result.
Save99d432d5…ab64f unchanged; current data containerC54A766E-6E23-4A16-8B92-
9E3C212C15CE. Original PRD goal and performance acceptance remain open.

Enabled CPU candidate file-selection capture completed: helper2574exit0,
30.0129447s/1579VI=52.610632Hz, CPU15.718705ms/VI, EFBelapsed2.565921ms/VI,
process164.763575M instructions/VI and51.751098Mcycles/VI. No dropped trace rows.
Work/timing summaries beside qos-cpu-r641/vi.csv. Retained visible-pointer scene
in generated/qos-cpu-r641-file-select.png; diagnostic A+B helpers9016/17285 then
neutral. Later AX35FPS observation reinforces fluctuation, not a selected mean.
No evident large improvement over R64053.014Hz, but different binary/run and
host conditions mean this is NOT a matched off/on causal result. Do not promote.
Next same54786759 explicit CPU flagNO with identical scene/work collection,
then reject/park if no repeatable gain; no further queue-only experiments.
Runtime cleanstop17:16:44.989failed0, session98543exit0, soleSimulator shutdown.

## R640 — Simulator work comparison and default-off QoS candidate

R639 full suite64026 exit0, Repository safety checks passed. Then soleSimulator
5921/session32327, unchanged installedbf6da365/module3acdcddc, LC byte/pair0.
Diagnostic A+B helper84416 then neutral entered file selection; actual center
tap retained visible stationary pointer (no held buttons). Screenshot
generated/simulator-file-select-r640.png. Work helper82246 exit0.

30.010771s/1591VI=53.0143VI/s; process178.9348M instructions/VI and55.4094M
cycles/VI versus nativeR639192.7767M/58.2437M. Simulator CPU-thread15.2081ms/VI
versus native11.1011ms; EFBelapsed2.2095 versus0.3184ms. Whole-process work is
LOWER, so these data do not support gross extra instruction work as the primary
explanation. They do not isolate guest-thread work, core placement or clocks:
Simulator also has external SimMetalHost work outside its process counters.
Current core/frequency scheduling and host contention remain discriminators.
The brief43FPS pointer observation recovered; no pointer-causality claim.
Trace dropped0; paths generated/runtime/platform-simulator-r640/{vi.csv,
process-work.json,work-summary.json,timing-summary.json}, ios-runtime-r640.log.
Clean stop failed=0 at17:01:09.523/export1, session32327exit0, device shut down.

New bounded intervention follows SunPad's QoS-only experiment, not its clock
scaling: Simulator-only GalaxyPadDevUserInitiatedQoS defaultsNO; whenYES, runtime
serial queue explicitly requests USER_INITIATED. Both control and candidate log
qos_class_self once on worker and first CPU-thread VI. No guest timing changes,
no per-frame clock reads. CPU hook only accesses its flag on the CPU thread.
Queue inheritance is a hypothesis: actual CPU log must prove whether it changes.
This differs from R331's unchanged native priority-only observation.

App build12379 exit0 after correcting initial pthread API arity error in87509.
Candidate SHA d5871ba78702b9f46f10c2e55080e62e1dac4f935c489b1f0ef05773976a86e5,
not installed or enabled. Standalone check-ios-host.sh is stale: it
omits generated GalaxyPadDiscIdentity.h include path; actual CMake app build
compiled and linked successfully. R639 full suite predates scheduling edit.
Next install candidate, run explicit NO then YES (ideally reversed repeat),
same visible file selection and counter capture. If CPU QoS is unchanged or
performance gain does not repeat, reject the hypothesis instead of promoting.
Original PRD gates remain open; no speedfix claimed.

## R639 — native file-selection work baseline

Same runner671729c6/current modulec0021b9f, LC byte/pair0, Metal1x, profile
platform-native-r638. Pipe profile configured before launch; first A+B during
strap screen only advanced toward title, second after visible title entered file
selection. No inputs during measured window. Center pointer visible on native;
R638 Simulator pointer invisible, so input workload is NOT exactly matched yet.
Pre/post screenshots native-file-select[-post]-r639.png show same scene,59.9FPS.

PID4315/session5785, work helper31266, both clean exit0. Fixed30.0051000835s
snapshot window covers1795VI (minimum=maximum),59.823163VI/s. Whole-process work
346034242166instructions/104547438758cycles =192776736.58instructions/VI and
58243698.47cycles/VI. These include graphics/audio/host, NOT guest-thread-only.
CPU-thread mean11.1011ms/VI, wall16.7163ms, EFBelapsed0.3184ms,
throttle5.8237ms. No dropped VI samples. Native near60 extends beyond title to
file selection, not proof for village or full-game acceptance.

Artifacts: generated/runtime/platform-native-r639-{vi.csv,work-summary.json,
timing.json,log}, snapshots in platform-native-r638/process-work.json.
Next collect Simulator work with matching pointer visibility and same helper,
then determine whether extra work or scheduling explains the CPU-time difference.
Do not compare process-wide counts to guest-only profiles or claim causality from
cross-platform FPS alone.

capture-process-work.py now supports an exact --executable identity for Simulator
while retaining native profile validation. Removed scripted focus mutation: caller
establishes foreground/scene, measurement leaves them unchanged. New native/mobile
mocked identity/no-focus regression passes; integrated into repository checks.
Full repository suite running session64026, generated/check-r639.log; do not
restart merely because observation times out. No game or Simulator running.

## R638 — sequential platform benchmark; slowdown is not a fixed Simulator ceiling

Stopped R635 game cleanly (failed=0), shut its Simulator down, then ran native
runner671729c6 with current macOS modulec0021b9f and a disposable Config/Wii copy
from the current Simulator data container. LC byte/pair fast paths explicitly0
on BOTH targets; Metal1x, PGO/ThinLTO/effectiveO2 preserved. Native capture visibly
shows title59.9FPS. Runner3003/session40402 exited0 before Simulator3504/session96470
started. No concurrent games; no unrelated user process killed.

Complete retained VI windows (seconds relative to first recorded VI):

| Target / scene | Window | VI/s | Mean CPU-thread ms/VI | Mean EFB elapsed ms/VI |
| --- | --- | --- | --- | --- |
| Native title | 60–120 | 59.933 | 10.126 | 0.322 |
| Simulator title | 60–120 | 53.350 | 15.598 | 1.475 |
| Simulator file selection | 150–210 | 50.717 | 16.194 | 2.143 |

Simulator presented windows: title57.48/56.67, file selection51.33/50.07/51.87.
No product rebuild/change accounts for improvement over older~35FPS observations.
This REFUTES a fixed35FPS platform ceiling, not the user's gameplay slowdown.
Title versus file selection are separate workloads; native file selection remains
unmeasured. Same generated source/profile does not mean identical platform binary.
Different audio/input backends, renderer surfaces, host load/core scheduling and
cache warmup remain confounders. CPU duration is on-thread time, not instruction
count; it cannot alone distinguish slower cores from more work. Elapsed counters
overlap and are not additive exclusive states. VI is not display scanout.

Evidence: generated/runtime/platform-native-r638/{vi.csv,summary-60-120.json},
generated/runtime/platform-simulator-r638-{vi.csv,title.json,file-select.json},
generated/{native-title-r638.png,simulator-title-r638.png,simulator-file-select-r638.png,
host-platform-simulator-r638.txt,ios-runtime-r638.log}. Native recorder dropped4247
TAIL samples after its fixed capacity; selected60–120s window fully retained.
Simulator dropped0. Focused VI-summary and recorder/buffer regressions passed.

Compiler driver probes select apple-m1 with matching feature lists for BOTH
arm64-macos14 and arm64-ios16-simulator: no evidence for a default A7 target bug.
Mac launcher enables LC byte/pair optimizations while iOS leaves them disabled;
both forced off here. That is a separate THP/movie parity experiment, not an
explanation for this title result and not promoted without mobile regression.

Next: finish native file-selection comparison; then compare instructions/cycles
per VI and core residency for matched runs to distinguish generated execution cost
from scheduling, before another AOT rewrite. Do not resume touch-stick checks as
the primary lane. Do not repeat R331's policy-only sample as a causal test.
Physical hardware is the additional performance lane: devicectl currently finds
no devices. Apple explicitly requires actual-device performance tuning:
https://developer.apple.com/documentation/metal/developing-metal-apps-that-run-in-simulator
Simulator results neither prove nor disprove actual iPad speed.

Simulator clean Stop Game exited failed=0 at16:48:46.409; trace export_result=1.
Session96470 exit0, device shut down. No game/booted Simulator left. No speedfix
or G6/G15 acceptance claim; original goal unchanged.

## R637 — severe village slowdown coincides with remote-desktop contention

Same installedbf6da365/module3acdcddc/PID99791, unchanged village scene during
measurement. Frames220/30.500797=7.212926FPS then440/30.898688=14.240087FPS.
Immediate host snapshot JumpConnectPID1697=284.4%CPU, WindowServer73.1%, game47.1%.
Subsequent top3/5s ends Jump8.6%, game137.3%, aggregateidle46.60%, swapdeltas0;
frame windows recover22.63 then27.73FPS without app settings/code changes.
Contention is a serious contributor hypothesis for the catastrophic dip, not
controlled causal proof or resolution of ordinary30–35FPS deficit. Do not stop
Jump Desktop: it may be user's remote connection. No unrelated processes changed.
Five-second10ms sample generated/ios-r637-village-slow.sample.txt has399CPU-thread
observations:344underRun+1072,327nestedunderchassis including27floatfuture waits;
44Run body+1224/1612/... . Compiled chunk work dispersed. Video24PeekEFBDepth/
StagingFlush observations. Do not sum nested counts or equate samples with on-core
CPU time under contention. Source loop retains per-block downcount/timebase and
interrupt boundaries; no unsafe batching/priority change made.
User explicitly redirected away from touch checks. Next: matched nativeMac versus
Simulator workload/identity/settings comparison to quantify platform overhead;
then substantive AOT guest-state/dispatch cost work. Existing narrow failed
guard/cache experiments remain rejected. Physical-device performance separate.

## R632 — resolve memory-write journal loads by exact numeric address

Retained macOS module1fb635f7…01dc7a and profile28822 CPU samples, not current
Simulator timing. At0x679a580, adrp x9,page0x6c24000 then ldr[x9,+8] reads
_g_mem_write_journal at0x6c24008 (nm), NOT the nearest annotation's lazy-FP flag.
Classifier now requires exact adjacent page/base/offset and caller-supplied
same-binary symbol table; wrong symbol/base/address tests fail closed.
Reaudited top20:4776 loads =3590unresolved+640lazyFP+214journal+185stack+147table.
214/28822=0.7425% sampled leaves, not dynamic counts/removable time or a forecast.
No justification to remove required write observation or rebuild the product.
Evidence generated/shared-aot-work-r632.json; classifier tests pass. This closes
one provenance gap only; current35FPS deficit and full performance gate remain.

## R631 — current host contention, not a sole-cause diagnosis

Installed app0037f222/runtime95966 resumed existing file details15:47:31.316.
MacBookAir10,1,16GiB,8logical CPUs. `top -l 3 -s 5` captured in
generated/host-perf-r631.txt: subsequent samples GalaxyPad134.4/158.5%CPU,
Logitech updater67.2/74.7%CPU, aggregate idle29.85/41.51%. Last SimMetalHost41.2%,
WindowServer42.9%. Percent process CPU is per-core scale, not total-machine usage.
Swap deltas0 throughout; compressed memory5.8GiB, not evidence of active swapping.
pmset reports no recorded thermal/performance warning; this does not exclude
throttling or per-core contention. No unrelated process was stopped.
Corresponding first full frame window1078/30.800160=34.999818FPS. Background load
is a possible contributor, not measured causal attribution or sole explanation.
Current host queue uses default serial attributes; no new QoS inference. Earlier
R331 policy-only captures explicitly parked: do not repeat without new hypothesis.
No product change or speed gain. Candidate paused again; investigate measured
CPU execution cost with a falsifiable hypothesis, not another generic profile.

## R618 — exact normal-module build and sampled-PC check

R617 sample image UUID EFDD0591-6DA6-3B40-B32D-505977B60142 matches dwarfdump
of current normal Simulator module3acdcddc. Current Ninja graph has profile use,
ThinLTO and final-O2 after Release-O3, strictFP; not a debug-build explanation.
This verifies graph and image identity, not a clean reconstructed build.

Subtracting sampled image base0x12b51c000 resolves two explicitly listed PCs in
804B60A0 to0x5f62ba8 and0x5f66404. Both are ldrb of g_ppc_lazy_fp_enabled after
adrp, followed by availability/MSR checks. The sample's13 observations aggregate
multiple PCs; do not attribute13 to these two instructions. 803A30A0 listed
PCs0x48335d8/0x4833610 are stack prologue/x19 CPU pointer copy, not arithmetic.
R449's rejected narrow availability experiment remains parked. No new product
change, full-module rebuild or performance claim is justified by this check.

## R617 — current normal Simulator module baseline

App b853f060/module3acdcddc with movement trace0, pointer experimentsNO: visible
file list latest pre-profile window1148frames/30.500377s=37.638879FPS. This is not
gameplay or physical-device acceptance. Three-second10ms sample records246CPU
observations,200nestedunderchassis including23float-future waits; compiled chunk
work is distributed (largest listed chunk13observations). Nested stack counts
must not be added. Video includes23PeekEFBDepth and48RunGpuLoop leaf observations.
No new optimization or speed gain. Files generated/ios-runtime-r617.log and
ios-r617-file-select.sample.txt; screenshot ui-r617-file-select-native.png.
The normal module remains slow with the experimental input instrumentation off.

## R606 — sampled dispatch tables identified conservatively

Exact retained module1fb635f7…01dc7a:805170A0 entry0x6798c94 reads x0+0x280,
CPUState.pc;0x6798cc4 loads halfword dispatch table followed by code-base add/br.
804AB0A0 at0x5e61d00 reads EXRAM base x0+0xda0. Retained offsetof probe and
entry path establish these particular roles, not every similarly named register.

New local load_origin rule requires entire adjacent adrp/add/adr/ldrh/add/br
pattern with exact operands. Focused negative tests cover missing/wrong registers
and shifts. Refreshed top20 audit yields147 PC-relative table samples,640 adjacent
lazy-FP-global,185stack,3804unresolved.147/28822~0.51% CPU leaves; sampled locations
are not cost or executed-instruction counts. No evidence for a broad dispatch
rewrite from this result. Remaining load-base provenance still open. Private
report generated/shared-aot-work-r606.json; no new runtime or FPS gain.

## R605 — effective CPU flags and retained load origins

R562 current Ninja graph uses finalO2 overriding earlier ReleaseO3, ThinLTO,
PGO rmge01.profdata and strictFP flags. No debug-build explanation supported;
this graph inspection is not independently reconstructed binary provenance.
Prior R460 counter comparison and R469 snapshot rejection remain in force.

Existing audit-shared-aot-work.py verifies retained macOS module1fb635f7…01dc7a
and exact profile, then resolves top20 chunk PCs. R605 report adds conservative
origins to prior R470 families:4776loads =640 adjacent lazy-FP-global +185stack
+3951unresolved.640 is~2.22% of28822 CPU leaves, not removable time. Most selected
loads still lack base provenance; do not call them redundant mapping accesses.
This is old exact macOS evidence, not a current mobile sample or speed gain.
Next establish remaining high-weight load origins before choosing a shared
transformation. No new runtime/build; report generated/shared-aot-work-r605.json.

## R594 — context reader/mapper disabled, slowdown persists

Same app ff855d69…cb34e4/module c1c06e0a…d521421, rehashed. Changed only
DevPointerContext to NO from R593. Native observer and legacy hooks remain NO;
pitch22 remains YES. CoreHost requires pointerProbe for experimental mapper
installation, so context flag also disables that mapper; verified source gate.
No context/mapper-enabled logs. Same instrumented module null-check still exists.
Sole iPad Sim, runtime72759/session21376, no profiler/build.

Visually reached title; one-second diagnostic A+B then neutral stationary file
list. Clean later windows (ignore transition-containing11:36:15):
11:36:45.946=869/30.500283=28.491538FPS;
11:37:16.447=1142/30.500313=37.442239;
11:37:47.448=1083/30.999810=34.935698;
11:38:18.048=1067/30.599984=34.869300.
CUA one-second display briefly59FPS, not sustained acceptance. Native capture
ui-r594-context-off-native.png; ios-runtime-r594.log retains measurements.

No consistent large gain versus R59334–37FPS or R59131–36FPS. These separate,
short, animated-scene runs do not quantify precise diagnostic overhead. They
refute diagnostics removal as a sufficient cure for this reproduced slowdown.
Do not continue flipping unrelated UI flags hoping for60FPS. Return to exact
native CPU execution/readback costs; preserve existing correctness contracts.
No source/build/save changes, no gameplay or physical-device acceptance.

## R593 — native observer detached, slowdown persists

Same app ff855d69…cb34e4 and module c1c06e0a…d521421 (hashes rechecked), sole
iPad Sim, runtime72333/session21546. Changed only launch argument
GalaxyPadDevNativePointerObserver from YES to NO; legacy hooks remain NO.
CoreHost's guarded attachment branch is therefore skipped; no attached log.
Pitch22/context/calibrated-touch remain enabled. Instrumented module still has
the callback-null check: this is not an uninstrumented-module comparison.

After title A+B, stable FileSelect0114 at11:30:21.012. No pointer/held buttons,
controls visible, no profiler/build during measured windows:

-11:31:13.609:1136/30.500213=37.245642FPS.
-11:31:44.309:1043/30.699304=33.974711FPS.
-11:32:14.810:1077/30.500687=35.310680FPS.

Exclude earlier transition-containing window. R591 attached visible windows
31.0/36.1/34.8 overlap this range. Separate runs/animated scene/host variation
prevent a precise causal cost estimate; do not claim zero overhead or a gain.
Native observer attachment is not the sole cause: detached file select still
runs far below60. Context reader and mixer remain, so diagnostic-free baseline
is not yet established. Next isolate context reader (and dependent experimental
mapper) by disabling DevPointerContext with other R593 settings unchanged.
Evidence ios-runtime-r593.log and ui-r593-observer-off-native.png; CUA verified
stationary file list. Native stop11:33:15.626 failed=0. No save/gameplay acceptance.

## R592 — exact native sample sites, no broad rewrite justified

Verified R591 loaded module UUID72DA0235-496F-375D-A9BA-B76DD1D28111 and current
SHA c1c06e0a03ab0822120f855291abf195139299b924e9363eb71408a15d521421 match.
Read nm symbol starts and narrow llvm-objdump ranges from that exact module;
saved six generated/r592-*.asm slices. These are generated4096-byte guest
chunks, NOT one-to-one source functions. Explicit sample offsets resolve to:

| Chunk + decimal offset | Module-relative PC | Observed native operation |
|---|---|---|
|803A30A0+2732|048340f8|load lazy-FP flag; neighboring FPSCR classification is not this sampled instruction|
|803A30A0+5956|04834d90|shift in double-to-single bit conversion before guest store|
|804B60A0+190976|05f8f8c4|FP-register bit transfer into nonfinite checking block|
|804B60A0+112|05f60f34|halfword load from chunk-entry jump table|
|804440A0+2720|055b1cc8|form mapped guest byte-store address|
|804440A0+3084|055b1e34|load RAM base in checked byte-store path|
|805170A0+184|06798de4|load RAM size in checked word-load path|
|805170A0+252|06798e28|load EXRAM size in checked word-load path|

Counts7/7/6/4 on those sample lines aggregate multiple PCs and include ellipses;
do not assign each aggregate to either displayed offset or extrapolate a weighted
hotspot percentage. No debug-line identity or exact original function established.
Mixed work is consistent with older R427/R470 attribution and does not reopen
their rejected mapping-cache or broad FP rewrite unchanged.

Next controlled experiment: same app/module/scene with only native observer
attachment disabled (DevNativePointerObserver NO); keep pitch/context and other
settings fixed. Establish diagnostic overhead before interpreting observed native
cost as a production baseline. No code optimization promoted, no FPS gain.

## R591 — hiding touch views does not cure file-select slowdown

Installed app ff855d69067bc1cac94d53ce2770f807d760ee3510f18ce0aea0a243b9cb34e4,
same R562 observer module and pitch22/context/calibrated flags. Sole iPad Sim,
runtime71366/session32084. Stationary file list, no pointer/buttons during frame
windows; native Controls menu pauses/reset windows between visibility changes.
No build/profile changes. Thirty-second windows in ios-runtime-r591.log:

- Visible: 11:18:57.868,950/30.599585=31.046172FPS;
  11:19:28.770,1115/30.900608=36.083433FPS.
- Hidden after resume11:19:57.761: 11:20:29.271,
  1029/30.700211=33.517685FPS;11:21:00.072,982/30.800333=31.882772FPS.
- Restored after resume11:21:28.412:11:21:59.174,
  1060/30.500379=34.753667FPS.

No consistent visibility benefit. This is a short same-scene comparison with
animated background, not frame-identical replay or proof all host UI overhead is
zero. Hidden views do not remove UI timer/input mixer/observer work. Neither
state approaches60FPS, so hiding controls is not the speed fix.

Separate post-window sample: sample71366 for1s at5ms (session82716 completed0),
generated/ios-r591-file-select.sample.txt,142 samples per thread. CPU120 under
StaticRecompCore::Run+1072,110 in its chassis_dispatch subtree including19 float
future waits. Video19 PeekEFBDepth→MetalStagingTexture::Flush→waitUntilCompleted,
37 timed waits,24 RunGpuLoop. Cross-thread counts overlap; not additive cost or
recoverable FPS. Supports returning to native compute/readback attribution,
not interpreter dominance or a broad optimization claim. Sampling occurred
after comparison and its transient FPS drop is excluded.

Live hidden view/menu restoration verified; fresh actual Touch aim and explicit
A selected file1 after restore. Clean native stop11:23:54.574 failed=0.

## R553 — fallback totals are not interpreter time

Rechecked current core source after R549 shutdown totals. R489 caveat still
applies: m_fallback_steps counts SingleStepInner, not the macOS JIT branch.
Additionally HookInstructionFallback increments hook_fb BEFORE its native cache
operation fast path. With dcache off, eligible dcbf/dcbst/dcbi/icbi perform cache
invalidation and return without SyncOut/SingleStepInner/SyncIn. Thus R549's
260286803 hook_fb calls cannot be labelled interpreter executions. This is
existing behavior, not a new optimization; raw call totals are not a time budget.

Bounded sample of unchanged R552 PID50620, one second/5ms interval, completed
via handle16840: generated/ios-r553-file-select.sample.txt.144 samples per thread.
CPU:117 under native-dispatch Run+1072 (including21 float-future waits),12 at
other Run offsets, two explicit SingleStepInner subtrees. Video:21 depth-peek
→MetalStagingTexture::Flush→waitUntilCompleted,46 timed waits,32 GPU-loop samples.
Counts across threads overlap; do not add wait shares or infer recoverable FPS.
This short sample does not attribute exact fallback PCs or all fallback cost,
but does not support interpreter dominance in this stationary file-select view.
Native execution and synchronous depth-readback remain substantial candidates,
consistent with R543 gameplay sampling. No new build/settings/performance claim.

## R489 — macOS/mobile fallback counters are not equivalent

StaticRecompCore_Run.cpp increments m_fallback_steps for interpreter stepping,
but the alternate m_fallback_jit->Run branch does not increment it. A macOS
fallback=0 log therefore does not prove no fallback execution. Mobile disables
fallback JIT and exposes interpreter counts; R487 totals cannot be compared
directly as a regression. HookInstructionFallback has a separate call counter.
Exact PC/reason attribution remains required; no performance acceptance implied.

## R470 — broader sampled instruction attribution, no new candidate

Read-only audit-shared-aot-work.py verifies installed module1fb635f7, reuses
R423/R422 exact profile and disassembles each of20 hottest chunks independently.
All7782 selected samples map to instructions (27.0002% of28822 CPU leaves).
No full-module dump retained. Per-chunk hashes and weighted instruction details
in generated/shared-aot-work-r470-final.json. Original intermediate report also
retained; final uses corrected diagnostic family distinction for FP transfers.

Families:4776loads,1775integer/other,524FP move/conversion,416stores,224branches,
64other scalarFP,3calls. Of588 previously labelled scalarFP,513 were fmov and11
fcvt, not floating arithmetic. Classifier now explicitly separates those; focused
alignment/weight/missing-PC/family regression passes. Samples weight occupied
instruction locations, not dynamic counts or a cost model; no CPU/GPU or memory
stall conclusion follows directly. Top20 is not whole-module coverage.

Compiled actual runtime CPUState offsetof probe (size3528). Offset0xd98 is
downcount, NOT a RAM pointer;0xd80/0xd88 are RAM/size,0xda0/0xda8 EXRAM/size.
Mechanical x19 grouping contains236 samples at downcount and423 across those
four mapping fields. Separate base-register proof is still required; do not call
these counts removable time or confuse all4776loads with mapping overhead.
Evidence generated/cpu-field-offsets-r470.log and tests/probe-cpu-field-offsets.c.

Decision: no broad float-helper rewrite or memory-map cache justified by this
breakdown. Next classify the remaining high-weight load sites by actual base
provenance (guest data, CPUState or dispatch/global table) before selecting a
shared transformation. Existing page-table, lookup-snapshot, LLVM and narrow
precision candidates remain parked. No product/runtime/module/save change or
FPS gain. Offline audit handles67069/21541 exit0, no game; full suite already
passed R469, focused classifier test rerun for this diagnostic change.

## R469 — reverse-order test rejects lookup snapshot promotion

Reused exact R468 runners/module, fresh Config/Wii/slot2 from R462, same native1x
settings. Candidate first then control, visible same rim scene before/after each
10s warmup+30s low-overhead window. Candidate55.784217Hz/258.078million process
instructions perVI/71.487million cycles perVI; control55.889693Hz/258.017million/
71.415million. Work reduction and cadence improvement did not reproduce.
Candidate wall median/p95/p99/worst17.814875/19.227833/20.076833/26.509208ms;
control17.752125/19.130833/19.879959/25.622458ms. CPU means16.427595 vs16.385704ms.
Complete windows, counts1674/1677; no droppedVI or missingCPU intervals.

Decision: park run-lookup-snapshot, no canonical integration or normal-runner
promotion. R468's favorable pair is not a repeatable product improvement. Do not
run an unchanged third pair or tune this snapshot's compiler/register allocation.
Phase/order/host variation remain; observed Logitech updater~38.5%CPU at startup.
This rejects the candidate's demonstrated value, not the existence of AOT overhead.

Both games56693/43454 and capture18348/62576 exit0, fallback0/smc_failed0;
save106e unchanged. Whole-session underruns69/74 and backlogs2/1 span unequal
durations: no audio pass or improvement claim. Normal installed runner unchanged.
Evidence generated/runtime/lookup-{candidate,control}-r469/{runtime.log,vi.csv,
process-work.json,work-summary.json,timing-summary.json}; four corresponding
generated/lookup-{candidate,control}-{pre,post}-r469.png images. No game/Simulator.
Full repository regression28233 exits0, generated/check-r469.log ends Repository
safety checks passed. Next revisit shared AOT helper expansion across sampled chunks
using retained profiles, not another local four-site or metadata-hoisting probe.

## R468 — first same-graph gameplay comparison, preliminary positive signal

Linked isolated runners using the same cached archives, substituting only the
R467 Run object in a copied libcore.a. tests/link-run-lookup-snapshot.py verifies
all original link-input hashes unchanged. Control68207f703ccff4d9c3eae1fce297742e20a2da3012f386866d154ba977b4c82c;
candidateb53edfc152d0e17c8f026da2cb12cf6ede8c6c78fb0e6946002a003d8b468898.
Both private app copies use unchanged module1fb635f7. Normal runner671729c6
unchanged. Link commands/hashes: generated/run-lookup-r468/report.json.

Sequential control→candidate, native1x/Metal/dualcore/LCbyte+pair/no mods/VI-only,
slot2 SHA74e453b5, save106e. Native menu load verified visually in both: same
hanging-Mario rim scene, life3/StarBits4; pre/post ambient animation advances.
Low-overhead whole-process snapshots after10s warmup,30s window, no Instruments.
Control55.2931Hz/260.562million instructions perVI/71.920million cycles perVI;
candidate56.4910Hz/254.784million instructions perVI/70.746million cycles perVI.
About2.17% higher cadence,2.22% fewer instructions/VI in this pair only.

Control wall median/p95/p99/worst17.871833/19.3495/20.48675/69.683625ms;
candidate17.600792/19.027125/19.732916/25.26175ms. CPU means16.532396 vs
16.193847ms. Full-window VI counts1659/1695; guaranteed/possible counts agree.
No droppedVI/missingCPU samples. These are VI intervals, not display scanout.
Background Logitech updater observed~43%CPU before control; no thermal control,
single-order pair, independently timed scene phases. Not a repeatability claim.

Both game handles65368/51788 and capture94897/77662 exit0; fallback0/smc_failed0,
save106e unchanged. Whole-session audio counts118underruns/3backlogs versus81/1
have unequal durations and include startup/restore/shutdown; not audio acceptance
or a valid underrun comparison. No input/action/transition regression pass claimed.
Evidence generated/runtime/lookup-{control,candidate}-r468/{runtime.log,vi.csv,
process-work.json,work-summary.json,timing-summary.json}; screenshots
generated/lookup-{control,candidate}-{pre,post}-r468.png. Tests for process-work
summary pass. No game/Simulator left. Full suite deferred pending candidate
decision; no installed promotion. Next reverse-order candidate→control pair on
fresh profiles, then broader regression only if this real-game gain repeats.

## R467 — run-scoped lookup candidate passes differential checks

Writer audit: forced fallback ranges populate in Init; REL mode and chunk vector
allocation occur in LoadModule (called from Init); lookup sizes/table populate
only in InitLookupTable at Run entry. ClearCache fills existing verification
bytes; SMC invalidation/verification and REL refresh change elements, not vector
storage. No cached verification result is allowed. Module-active remains live.
Source files: StaticRecompCore.cpp, StaticRecompCore_SMC.cpp and _Run.cpp.

Staged patches/experiments/run-lookup-snapshot.inc snapshots only mode, table
pointer/count, RAM sizes and verification-array pointer for one Run invocation.
Original address arithmetic/bounds, live chunk byte, module-active and general
REL/forced-fallback path remain. Timing/interrupt/stop/host-call code untouched.
No live product source modified. Future lifecycle changes that resize/reload
these structures during Run would invalidate this design and require revision.

tests/test-run-lookup-snapshot.py extracts actual current reference lambda and
compares staged candidate:4787968cases each at O1 ASan/UBSan and O2 pass. Includes
misaligned/boundary/random addresses, holes, empty table, disabled module,
live chunk-state changes and identical slow-path call counts. Mock slow-path
result tests routing only, not complete REL semantics or lifecycle concurrency.
Evidence generated/run-lookup-snapshot-r467.log.

tests/build-run-lookup-snapshot.py builds isolated control/candidate full Run
objects using exact cached runner compile flags. Build76883 exit0; source,
normal cached object and installed runner671729c6 unchanged. Private objects,
assembly and hash/command report in generated/run-lookup-r467; log
generated/run-lookup-build-r467.log. Candidate stack frame0x120 vs control0xf0:
compiler hoists metadata but spills some values; static inspection is not a gain.
Next link an isolated runner with this one object changed and use matched real
scene work/VI and pacing comparison. No module rebuild or new synthetic timing
lane. No installed product/FPS/gate change; no game/Simulator remains.

## R466 — precision lane parked; execution-loop attribution

Completed tests/audit-single-provenance.py against source38d5085e and installed
module1fb635f7. All44 suffixes begin with unknown state; memory callbacks clear
facts, gated scalar writes discard them. Four candidate factor-rounding sites
exist after successful path-local producers:804B62D4,62D8,62DC,62F4. None has a
fact on direct external entry to itself. Assertions pin exact source and expected
scope. No general float identity or rewritten helper correctness is claimed.
Retained profile gives the entire1024-instruction chunk1143/28822CPU leaves
(3.966%). Four sites are only a subset with unproven dynamic cost. Decision:
park this local specialization, no module build or runtime tracking system.
This does not rule out broader precision optimization with new impact evidence.
Evidence generated/single-scope-r466-final.json; audit exits0.

Reused R422 XML and verified installed runner671729c6; extracted only actual
StaticRecompCore::Run disassembly with xcrun llvm-objdump. Existing profile parser
joins aligned binary-relative PCs to disjoint inspected assembly ranges:
pre-dispatch799, REL/counter271, charge/timebase352, idle-check432,
exceptions322, dispatchability472, host/exit308, lookup746 samples. These sum3702
of3711 Run leaves (28822 total CPU leaves). Lookup plus dispatchability is1218
leaves,4.226% of CPU samples. All counts describe sampled instructions, not
removable cost; callees are excluded and sampling skid is not resolved.
Artifacts generated/runner-{sites,loop-ranges}-r466.json and runner-loop-r466.asm.
No new runtime capture, compiler change or game speedup.

Source next question: can invariant mode/lookup metadata be kept out of the
per-dispatch path without caching mutable chunk verification or weakening
exception, timebase, host-call and stop checks? Audit actual writers and callback
boundaries first. Do not bypass SMC validation or batch timing checks. This
targets shared runtime work across guest chunks rather than four isolated sites.
Existing CPU-profile and footprint regression tests pass; full suite/runtime
smoke not repeated for read-only attribution. No game or Simulator running.

## R465 — canonical-single identity and invalidation boundary

Re-read R195: guarded force_25bit_c shortcut already parked; not repeated.
New test-single-provenance.py compiles actual current float helpers with strict
FP semantics/UBSan and checks800000 random/special double inputs over4rounding
modes and NI on/off. After an original force_single result is widened, repeating
the same force_single under unchanged control produces identical bits and no new
host FP exceptions. Includes NaNs/infinities/signed zeros/subnormal boundaries.
This is a sampled oracle for an identity property, not a proof over all bit patterns.
Explicit counterexample: canonical nonzero single subnormal at NI0 becomes zero
at NI1, so a provenance fact cannot survive arbitrary FPSCR changes. Log
generated/single-provenance-r465.log; exit0. No product transform or timing run.

Source constraints for R464 path: each instruction label is an external dispatch
entry, so earlier producer execution cannot be assumed at that label. Scalar
single helpers may suppress destination writes on enabled invalid exceptions;
successful output provenance cannot be assigned unconditionally. Memory/helper
callbacks may change registers/FPSCR; stores are not automatically safe barriers
to cross. Thus annotating every apparent single producer and deleting later
conversions would be incorrect. No broad conversion removal authorized.

Next inspect the actual path's successful-producer/control-flow facts separately
for normal entry and every suffix entry. Only a specialization that preserves
those entry joins and callback/exception invalidation warrants a code experiment;
measure scope before adding a dynamic tracking scheme. No renewed scalar25bit,
FP-guard or LLVM experiment and no module build justified by this oracle alone.

## R464 — installed-module arithmetic work fixture, no compiler experiment

Reused R443's bounded synthetic44-instruction804B6278..804B6324 path, but new
probe-installed-block-work.c dlopens exact installed module1fb635f7 and calls its
exported module descriptor dispatch. No standalone C/LLVM object or module build.
Checks ABI/CPUState size/gameID and all44interior-entry final PC/cycle/exception
outcomes. Finite synthetic vector/constants only; not full gameplay-state parity
or callback/NaN/rounding regression. Driver/loop/assertions included in counts.

Four1million-call runs report2753.413/2753.389/2758.304/2763.427 process instructions
per call, cycles551.092/550.304/569.305/573.058.92473 exit0. Actual installed module
SHA unchanged. This establishes a measured installed-code harness, not a speedup,
not proof all cost belongs to arithmetic or that this path dominates gameplay.
Artifact generated/installed-block-work-r464.log; isolated driver only.

Pinned reference JitArm64_Paired.cpp482–550 ps_sumX explicitly tracks IsSingle,
selects32/64bit registers, FixSinglePrecision and live FPRF. Current runtime
cpu_interpreter_float.c798–832 ps_sum/muls use double CPUState lanes plus repeated
force_single/force_25bit_c. This suggests precision provenance as a concrete
source distinction, not permission to delete rounding/NaN/NI/FPSCR behavior.
Next audit provably-single operands within this path and whether specialization
can preserve external entry, alias, callback and exception observations. Preserve
all existing rejected vector/FP-guard/LLVM/cache experiments; don't repeat them.

## R463 — reference work-per-VI comparison: substantial execution expansion

Fresh work-reference-r463 copies prior accuracy-enabled JIT Config and R462
Wii/config.ini/slot2. Save106e/slot2 74e453b5 rehashed; GFX.ini identical. Diagnostic
runner34e96be1 rehashed, explicit reference selector logged, LC1/no mods/VI-only,
no Instruments/build/concurrent runtime. SinglePID87388 actual LoadState2 shows
same hanging scene/life3/StarBits4, ambient advancement before/after. Snapshot
helper93621 exit0, native quit86600 exit0, save106e unchanged.

Reference30.008733s/1799VI=59.949215Hz, both snapshot bounds same count. Process
delta124214893259instructions/50045517625cycles:69.046633million instructions and
27.818520million cycles per VI. Query brackets12.834us/9.916us. Compare R462 AOT
263.149236million instructions and73.146159million cycles per VI at54.487574Hz:
about3.81x process instructions and2.63x process cycles per VI. These are not
guest PPC instruction counts or CPU-thread-only measurements. Fixed-scene,
single-order runs, unlike diagnostic/normal binaries, absent host-pressure/
thermal measurements and differing execution contracts limit attribution.
Nevertheless the large instructions-per-VI gap supports substantial extra
dynamic work, not merely identical work waiting longer for instruction delivery.
No optimization or product change has been made from this evidence yet.

Next source step: quantify instruction expansion in a representative already-
sampled generated block using the existing actual-chunk execution harness and
these process counters, then inspect required versus redundant state/flag work.
Preserve callback/exception/external-entry observability. Do not rerun parked
FP-guard, return-selector, LLVM, page-cache or blanket compiler experiments;
do not start another full module solely to reconfirm aggregate slowdown.
Artifacts generated/runtime/work-reference-r463/{process-work.json,vi.csv,
work-summary.json,runtime.log}; work-reference-{pre,post}-r463.png. No game or
Simulator remains; original PRD/G6/macOS-first/mobile acceptance still unchanged.

## R462 — low-overhead AOT process work baseline

Verified snapshot CLOCK_MONOTONIC_RAW falls inside bracketing C++ steady_clock
reads1000times on this host; VI recorder uses steady_clock. Existing snapshot
API/identity tests still pass. Added capture-process-work.py (exact profile/PID
check, frontmost,10s warm-up then two snapshots30s apart, no overwrite) and
summarize-process-work.py (identity, monotonic counters/clock, complete ordered
VI data, dropped0 required, minimum/maximum counts across query uncertainty).
Synthetic identity/reset/coverage/uncertain-boundary tests pass.

Fresh work-aot-r462 profile from R459, same slot2/save106e; normal runner671729c6/
module1fb635f7 rehashed,1x/Metal/dualcore/LC1/no mods, VI-only/no Instruments.
PID87099 actual LoadState2, same visible hanging Mario/life3/StarBits4 before/
after. Capture76704 exit0; query brackets10.250us and11.459us. Window30.006842s
has1635VI in both minimum/maximum counts:54.487574Hz. Process delta430249000811
instructions/119593970061cycles =263149235.97instructions and73146159.06cycles
per VI. This is WHOLE PROCESS including host/renderer/audio, not guest instruction
count, not CPU-thread-only count, and not an optimization gain. Query uncertainty
does not change VI count in this capture. Next matched reference work/VI window.

Native Command-Q runtime72610 exit0, save106e unchanged. No game/Simulator left.
Artifacts generated/runtime/work-aot-r462/{runtime.log,vi.csv,process-work.json,
work-summary.json}; work-aot-{pre,post}-r462.png. No product/build change. Capture
does not include thermal/host-pressure samples, so do not infer clock-frequency
or host-load equivalence. No G6/performance/audio acceptance claimed.

## R461 — time-weighting correction and low-overhead process work probe

Installed RecountDT Resources/Analysis/bottleneck.json specifies time-weighted
averages, not cycle-weighted averages, for the four bandwidth categories. Existing
reported values remain correctly labelled cycle-weighted derived quantities;
added explicit time weighting and included/excluded durations. Recomputed retained
captures: P-core AOT delivery38.2422%, processing6.2995%, discarded7.7411%,
useful47.7172%; reference44.6968%,15.6341%,10.7599%,28.9092%. This does not change
R460's decision. Tests distinguish equal-duration/different-cycle weighting.
Outputs both profiles' weighted-r461.json. No new game run.

Raw R459 timer-counter export succeeds (95246 exit0) but its12-value arrays are
unnamed in the exported schema. Do not assume array index1 is retired instructions:
local as1 kpep fixed-counter numbering alone does not prove trace serialization
or thread attribution. No reverse-engineered counter claim follows.

Better bounded alternative: SDK libproc.h/sys/resource.h expose proc_pid_rusage
RUSAGE_INFO_V4 instruction/cycle totals. Apple XNU fill_task_rusage at
https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/kern/bsd_kern.c
assigns both from task power info. New process-work-snapshot.c makes one read-only
query bracketed by CLOCK_MONOTONIC_RAW, records PID/start identity and process-wide
instructions/cycles/user/system totals. No injection, sampling thread or Instruments.
Actual self-work test sees advancing instruction/cycle counters; external-current-
test-process snapshots, identity/time ordering and invalid-argument tests pass.
Compiled ignored generated/process-work-snapshot-r461, product unmodified.

Next use beginning/end snapshots with existing VI timing on matched normal-AOT
and diagnostic-reference late-scene windows. Validate PID/start identity, counter
monotonicity, bracket-to-VI timing, frame coverage and unchanged renderer/settings;
report instructions per VI and process scope explicitly. It includes GPU/audio/
host threads and cannot alone identify the guest CPU thread's instruction count.
Do not infer prior-run per-frame work from these new self-tests. This replaces
another disruptive counter capture, not the full PRD acceptance gates.

## R460 — validated counters; reference refutes a larger delivery fraction

Extended counter parser to reject overlapping intervals across cores for a
thread, invalid bounds/counts/nonfinite or out-of-range fractions; synthetic XML
reference/sentinel/filter tests pass. Actual R459 intervals do not overlap.
Initial strict sum-to-one assumption failed on exported fractions: retain their
original values and report discrepancies, never normalize. P-core1interval/
116cycles and E-core6intervals/1457cycles have nonunit totals. Previous weighted
R459 fractions unchanged; validated-r460.json records exclusions/discrepancies.

Reference runner34e96be1 (diagnostic JIT selector, not installed/mobile route),
fresh counters-reference-r460 profile, same slot2 74e453b5/save106e, matching GFX
and normal config except CPUCore4 and explicit FPRF/AccurateNaNsTrue, FP exceptions
False as in R425. LC1, --no-mods. PID86223 actual LoadState2 asynchronously restores
same hanging scene; initial immediate screenshot is still strap screen, later
ready screenshot proves load, no duplicate command.10s CPU Counters90687 exit0;
final scene/life3/StarBits4 and ambient animation intact, title59.9. Native quit
runtime89063 exit0/save106e unchanged. No runtime/Simulator remains.

Export54181 exit0; interval validation passes. P-core7767649806cycles:
delivery46.0566%, processing12.9871%, discarded10.6162%, useful30.3401%.
Missing2intervals/6927cycles; nonunit3/376cycles. E-core141354836cycles kept
separate. Compare AOT P-core delivery38.1003%, processing6.2825%, discarded7.7400%,
useful47.8773%. Faster reference has HIGHER delivery fraction. This does not
prove code layout cannot help, but rejects the proposed larger-relative-delivery
bottleneck explanation and does not justify a layout/compiler/module rebuild.
Raw cycle totals are not per-guest-frame comparisons; profiling overhead, unlike
runner binaries and differing execution contracts remain confounds. No FPS fix.

Next examine existing capture raw counter definitions for retired-work quantities
and how to normalize them to guest progress before any additional capture. The
question is excess dynamic execution work, not another code-footprint statistic.
Do not infer instruction counts from cycles or bandwidth percentages, and do
not repeat an unchanged CPU Counters comparison. Artifacts
generated/runtime/counters-reference-r460/{cpu.trace,metrics.xml,aggregate.json,
runtime.log,capture.log,export.log}; counters-reference-{pre,ready,post}-r460.png.

## R459 — first hardware bottleneck capture supports delivery investigation

Installed CPU Counters template selects bottleneck counting mode at1ms; three-
second /bin/sleep capability trace exported actual per-thread delivery/processing/
discarded/useful metrics. xctrace capability exit54 despite saved usable trace;
not treated as game evidence. Native Instruments launch initially timed out;
process later confirmed, no duplicate launch, closed after work.

Fresh counters-r459 profile copies R422 Config/Wii/config.ini and only slot2
74e453b5, save106e; own Pipe. Normal runner671729c6/module1fb635f7, native1x,
LC byte/pair1, --no-mods. Actual States/Load State2 shows hanging Mario/life3/
StarBits4.10s CPU Counters attach85638 completes5332 exit0. Final screenshot
same scene/ambient advancement; title24FPS versus immediate restore59.9, with
profiler activity, so no ordinary performance benchmark. Command-Q runtime69265
exit0, native1319397444/fallback0/smc_failed0; save106e unchanged. Whole113audio
underruns and max366ms graphics gap include restore/instrumentation/shutdown.

Export MetricTableForThread to private metrics.xml; resolve XML references and
join five metrics by thread/core/timestamp/duration. Weight fractions by matching
cycle count, never mix cores or treat missing averages as zero. P-core29037595232
cycles/36377 intervals: delivery.381003, processing.062825, discarded.077400,
useful.478773. Excluded532 missing/zero intervals/4372502cycles. E-core22105026
cycles, separately delivery.661096; negligible compared with P-core total.
These are Instruments instruction-bandwidth categories, NOT wall-time fractions,
cache-miss rates or promised recoverable CPU time. Large delivery fraction
supports a matched reference counter comparison; does not authorize a code-layout
or compiler change. Validate interval non-overlap/aggregation and compare the
same checkpoint/reference settings next. No repeat cycle-only capture.

Artifacts generated/runtime/counters-r459/{cpu.trace,capture.log,runtime.log,
metrics.xml,metrics.json,aggregate.json}; screenshots counters-{pre,post}-r459.png.
New summarizer focused cycle-weight/duplicate/incomplete/missing-value tests pass.
An accidental raw JSON cat was excessively verbose; use aggregate.json only for
future output. No product code, build or package changed; no G6 promotion.

## R458 — quantify sampled code footprint before a counter capture

R457 delivered startup feedback only; CPU/audio blocker remains. Re-read R420,
R422, R424, R427 and R139: dispatcher overhead and register/mapping hypotheses
already investigated. Do not repeat those probes. New question is whether the
large generated instruction footprint creates material instruction-delivery
stalls, as distinct from the semantic execution work already measured.

Retained R422 cpu.trace schema has CORE_ACTIVE_CYCLE sampling only; no retired
instruction or cache-miss counters. Therefore it cannot answer that question.
Current signed module UUID6AF26467-764C-3048-8B17-878BC714B679 matches the trace.
New summarize-code-footprint.py aggregates only selected-module sampled offsets:
22822 samples,14885 aligned PCs,12263 distinct64-byte regions,3593 distinct4KiB
regions. Smallest ranked set covering90% is9981 64-byte regions or1794 4KiB
regions;50% needs2048 or179 respectively. These are address bins, not assumed
hardware cache geometry, dynamic working-set size, cache misses or removable CPU
time. Sampling skid and the whole capture's save/profile context still apply.
Private output generated/code-footprint-r458.json. Synthetic alignment,
aggregation, coverage, empty input and invalid-size checks pass and are wired
into the repository suite. No product source/module/package mutation or runtime.

Next: inspect/configure installed CPU Counters template and obtain one bounded
late-scene counter capture with the accepted AOT artifact and isolated profile.
First confirm available events can distinguish retired work from instruction
delivery stalls; avoid another cycle-only capture. Compare reference only if
the first capture provides usable counter evidence. Do not change chunk size,
compiler options, semantics or module layout from footprint alone. G6 stays open.

## R453 — boundary-only page lookup remains inconclusive; park prototype

Source callback inventory includes external read/write at widths1/2/4/8,
write journal, SPR read/write, cache control, instruction fallback, host call,
external pointer and reset/state transitions. Refresh-after-callback alone is
insufficient for reentrant accesses. Extended isolated table fixture disables
cached lookup while callback_depth>0 and refreshes at outermost return; nested
remaps and the current journal store's already-acquired pointer pass.635520
original pointer/offset cases still pass ASan/UBSan. Actual runtime callback
coverage/CPUState-alias writes are NOT integrated or proven by this fixture.

Optimistic stable-map timing excludes mapping checks/rebuild/callback costs but
retains callback-depth rejection.2M ABBA range4.267/3.168ns, table3.605/3.128ns.
One changed10M BAAB confirmation: table2.482/1.521ns, range2.023/1.732ns.
Order/run variability prevents a repeatable benefit claim, even before real
integration overhead. No further unchanged comparison or full module warranted.
Artifacts generated/{probe,bench}-memory-page-table-r453 and
bench-memory-page-table-r453-long; source supports explicit timing labels/count/order.

Park this page-table design; do not conclude that all possible table designs
are slower or that memory access is ruled out. Next take the concrete R448
current-product startup visibility defect: roughly40s with the launcher hidden
before child window appears can look frozen. Inspect bounded launch-status fix
in existing parent wait path without a game-module rebuild. This is G6 usability/
stability work, NOT an AOT throughput fix or waiver of the performance blocker.

## R452 — data-page mapping oracle; per-access coherence costs more

Pinned JitArm64_BackPatch.cpp85–95 non-arena path emits BAT-page pointer lookup,
null slow-path check and page offset. Current AOT cpu.h get_ram_ptr resolves
MEM2 then MEM1 on every access. This differs from the already accepted two-range
CODE dispatcher specialization; InitLookupTable in StaticRecomp is SMC/code
lookup, not a reusable data-memory table. R427 already excludes arena-only fix.

New product-immutable probe-memory-page-table.c uses128KiB data pages populated
through the original resolver, with partial/cross-page fallback, original mapping
precedence and exact MEM1 write-journal offsets. Every access compares current
pointer/size snapshot, rebuilding only when changed.635520 pointer/offset cases
pass ASan/UBSan across mapped/unmapped addresses, mirrors, ends, wrap, partial
pages, absent EXRAM and pointer/size changes. Existing callback-remap/journal/
reservation test also passes. No runtime ABI/table integrated or game launched.

Separate unsanitized O2 2M-lookup ABBA (mixed normal MEM1/MEM2, threadCPU):
range3.393/2.207ns, table7.366/5.426ns. Variation is substantial; both table runs
are slower. This synthetic resolver comparison is not game timing. Do not build
a module with this per-access-coherence design. Files generated/
probe-memory-page-table-r452 and bench-memory-page-table-r452 are isolated tools.

Next causal boundary: enumerate actual host/callback mapping mutations and
reentrancy before considering refresh only at those boundaries. Such placement
is NOT proven by this pointer oracle; blindly deleting per-access refresh would
reintroduce R217/R311 stale-mapping bugs. Preserve journal's already-acquired
store pointer, refresh before subsequent accesses, and account for arbitrary
module helper callbacks/CPUState aliasing. No guard removal or shipping change
authorized by this result. Full PRD/performance/G6/mobile hold unchanged.

## R451 — full restore chunk loses PGO; no promotion

tests/audit-restore-profile.py stages the complete exact805170A0 source and
inserts the R450 range fast path only at80517584, leaving all external suffix
charges, middle entries, original fallbacks and return dispatcher text unchanged.
Actual cached Ninja compile/PGO flags emit private IR; current source/profile/
canonical module hashes verified unchanged. Session4002 exits0 for compilation.

Control function_entry_count238389378; candidate absent. IR1,844,876 versus
1,826,149bytes is NOT code-size/speed proof with different profile application.
Compiler diagnostics did not flag this lost count, so inspect IR metadata rather
than trusting successful compilation or quiet warnings. Evidence
generated/restore-profile-r451/report.json and per-variant IR/logs.

Do not benchmark profiled control versus unprofiled candidate or copy counters
onto changed CFG. A fair candidate needs new representative training or a
profile-compatible implementation, plus full-block entry/callback/return tests.
This is not proof the optimization is slower. Nevertheless park this narrow
three-load candidate: the entire chunk is only721/28822 (~2.5%) CPU leaf samples,
and the proposed path is only part of it. Spending a full training/module cycle
here lacks evidence for the substantial required improvement. The figure is a
scope estimate, not an upper bound on inclusive helper or end-to-end cost.

Next investigate a broader causal distinction in AOT versus reference execution:
the generated memory-access contract across hot code, using current runtime
and reference source to identify repeatable excess work. Preserve the rejected
R311 caching and R427 arena-only conclusions; do not simply reorder checks or
start another isolated tiny-helper optimization. No game/performance promotion.

## R450 — actual register-restore range prototype, isolated correctness only

Current signed-module disassembly generated/hot-805170-r450.asm maps top three
sample PCs to function prologue/PC load/jump-table access (37/46/40samples).
These are not a new justification for parked entry splitting. Interior sampled
range6799a80..6799b94 restores r29–r31 from r11-12/-8/-4, with repeated mapping
checks before each read. Exact generated labels80517584/88/8C confirm behavior;
prior R142–R150 suffix-cycle correction remains intact.

New tests/probe-restore-range.py hash-checks the exact current chunk, extracts
those three original load bodies, and compares a separate prototype resolving
one whole12-byte normal-RAM span. Retains ordered PC/register writes; rejects
CPUState overlap, mapping boundaries/size underflow and falls back to the original
body for callback paths. No metadata cache survives a callback. No original code
or installed module changed. This is distinct from R311 general callback-bounded
mapping caching and must not be generalized from this result.

7616 fullCPUState/callback-count comparisons pass ASan/UBSan across MEM1/MEM2,
cached/uncached mirrors, offsets including boundaries/wrap, optional external
callbacks that mutate base/mapping, and absent EXRAM. Source SHA9b221ad3…cfd94.
No timing measured, no FPS claim. Entry cycles and local return dispatch are not
part of this three-load fixture and need full-block validation before adoption.
Next establish profiled full-block code shape and a quiet benefit check before
any full module; reject if setup/alias guards consume the saving. Do not broaden
to writes, which carry reservation/journal semantics, or waive mobile safety.

## R449 — reject narrow FP-availability guard optimization before rebuild

Reused R422 samples/R423 exact-module disassembly after R448 product-path smoke.
New read-only audit-fp-guard-samples.py checks current module SHA1fb635f7 and
joins aligned retained sample PCs to contiguous explicitly recognized lazy-FP
load/compare/branch plus MSR bit13 test sequences. Parser synthetic positive,
wrong-symbol/offset/bit/base/branch/discontinuous/truncated rejection checks pass.
No original game/source/module/profile modified and no game/build launched.

Result generated/fp-guard-samples-r449.json:800180A0 has52 sequences/147 guard
samples out of1130 chunk samples;804B60A0 has73/91 out of1143. Combined238 of
28822 CPU samples (~0.826%). This is recognized shapes in two functions, not
all checks, dynamic counts, removable time, or a whole-module upper bound.
Actual runtime cpu.h395–398 tests lazy-FP/MSR and raises the unavailable
exception; generated80018A98..80018AA4 crosses memory callbacks, so guards
cannot be dropped merely because an earlier instruction accepted FP.

Decision: no guard-elision candidate or module rebuild on this evidence.
Keep availability/exception semantics. Next examine the next substantial guest
chunk805170A0's sampled sites and exact-region behavior to distinguish game work
from avoidable translation/host transitions. Do not extrapolate a whole-chunk
sample total to a proposed operation's savings or repeat parked entry splitting.
Full PRD/G6/mobile hold unchanged; no delivered FPS gain this turn.

## R446 — quiet profiled selector comparison fails confirmation; parked

build-profiled-return-probe.py validates R445 audit inputs/profile count and
lowers audited profiledIR to isolated native objects. Control symbol renamed
only after profile application. Original module/source/profile unchanged. This
retains IR branch weights but is not the installed whole-module ThinLTO link.
Artifacts generated/profiled-return-r446/report.json and IR/objects.

No game, ninja, clang build or repository suite running alongside timing.
Combined20614 exit0:11k merge/store and44k arithmetic full-state/RAM/flag/return/
cycle checks pass. ABBA1M calls:
merge control26.866/26.985ns, selector27.499/27.472ns;
arithmetic control231.058/231.696ns, selector214.301/226.660ns.
Arithmetic variability prompted ONE changed-order/longer confirmation, not
promotion. Added bounded --iterations and --reverse-order to the same harness.

BAAB5M calls,26823 exit0, both correctness corpora still pass:
arithmetic selector232.301/231.748ns, control225.675/232.383ns;
merge selector27.215/27.717ns, control27.087/27.144ns.
No reproducible arithmetic gain; merge slightly worse both orders. Synthetic
data/isolated link remain limited evidence, not actual FPS. Logs
profiled-return-{build,merge,arithmetic,arithmetic-reverse,merge-reverse}-r446.log.

Decision: PARK selector/guard without game rebuild. Do not repeat unchanged or
broaden to all chunks. LLVM remains parked too. Return to original macOS G6
gameplay/stability acceptance audit and accepted-runtime evidence before choosing
another performance hypothesis; preserve story/controls/mobile/full-shell goals.
No product source, module, app, save or dependency was changed by this experiment.
Full repository suite6080 exit0 (generated/check-r446.log), run only after
all performance measurements completed; no live work remains.

## R445 — real compile/PGO audit rejects direct guard, retains selector candidate

New audit-return-guard-profile.py reads actual active-module cache/Ninja compdb-x
command, resolves response quoting, verifies exact profileSHAf39a..., and stages
copies with only explicit original-header include resolution. Original source,
profile and module hashes rechecked unchanged. O2/strictFP/ThinLTO/profile flags
retained for emitted-IR audit; diagnostics explicitly enable profile warnings.

Direct guard: control function_entry_count65272501, candidate absent and
Wprofile-instr-unprofiled. Reject this form rather than silently losing PGO.
Evidence generated/return-profile-r445/report.json, run5508 exit0.

Equivalent --selector variant leaves the caller sparse switch/cases/default CFG
intact: an always_inline, no_profile_instrument_function pure helper maps PCs
outside the legal envelope to0 (not a valid target). It does not modify ctx->pc.
Both control/candidate retain65272501entry count and no missing-profile warning;
no counters fabricated or merged. Helper introduces no independently trained
branch profile; matching caller count is necessary, not proof of all downstream
LTO layout/performance. Evidence return-selector-profile-r445/report.json,
52955 exit0. Optimized IR retains selector work, not merely a source-only edit.

Updated standalone C guard prototype supports same selector.327680 target checks
and11k merge/store+44k arithmetic full-state/RAM/flag cases pass (93183 exit0).
Logs c-return-selector-r445.log, selector-merge-r445.log, selector-arithmetic-r445.log.
Their incidental unprofiled timings ran alongside full repository suite; reject
them as performance evidence. No current-candidate speedup or regression claim.

Next quiet execution comparison from the actual profiled compiler settings,
preserving branch-profile provenance and separating any standalone-link versus
installed ThinLTO limitation. No module build unless this candidate has material
support. Installed module/app and full original PRD/G6/mobile hold unchanged.
Full repository suite90645 exit0 (generated/check-r445.log); no live work remains.

## R444 — history audit rejects repeated host lane; narrow C return guard candidate

No retained CSV found with STATICRECOMP_TRACE_FILE header under runtime. More
importantly, R139/R140 already sampled guest PCs using the separate4096-dispatch
histogram; R420 explicitly rejects repeating generic host-loop attribution.
Re-read those records and current Run source. No new runtime/profile capture.

Selected distinct bounded question: generated local-return sparse switch can
reject outside-envelope PCs before traversing the existing return-target tree.
Initial label-table idea simplified to one unsigned range guard, preserving
every original switch case/default, cycle guard and instruction byte-for-byte.
No cross-chunk direct calls, new local destinations or validation suppression.

New probe-c-return-guard.py transforms only the cached exact sampled C chunk,
checks original object hash, records source/candidate identities, and emits
private candidate under generated/c-return-guard-r444. Guard envelope uses18
existing return targets.327680 enumerated target comparisons pass across full
low16bit domain at relevant/surrounding/wrap highwords. Since all original
targets lie in envelope, early rejection cannot remove a valid switch case;
inside-envelope defaults remain handled by unchanged switch.

Existing exact-chunk execution harness now labels non-IR candidate accurately.
Merge/store11k and arithmetic44k selected-entry fullCPUState/RAM/hostflag plus
return/cycle/exception cases pass. This C/C comparison also passes the synthetic
interior case that the LLVM candidate failed. Combined26561 exit0.
ABBA1M calls each, threadCPU time:
merge/store control36.301/37.274ns, candidate35.657/35.597ns;
arithmetic control240.657/234.862ns, candidate224.460/226.857ns.
Synthetic finite data, externalLR, no game-state distribution or installed
PGO/LTO parity. No FPS claim. Files c-return-guard-r444.log,
return-merge-r444.log, return-arithmetic-r444.log and private report.json.

Next audit installed generated chunk and cached compile/profile metadata before
any full-module candidate. Guard changes CFG and may invalidate PGO; do not
silently attribute a profile change to the guard. Prior blanket entry splitting,
fixed-size sweeps and host counter/timebase shortcuts remain parked. Product
unchanged, full original PRD/G6/macOS-first and mobile hold preserved.
Full repository suite20240 exit0 (generated/check-r444.log); no current-artifact
gameplay or FPS acceptance claimed.

## R443 — arithmetic execution comparison; LLVM candidate parked

Extended cached-object execution harness with --arithmetic for the44instruction
path0x804B6278..0x804B6324, mapped vector1/2/3 and constants0.5/3, finite seeded
FP registers, FP/LSQE/PSE enabled, external fixed LR. No chunk/object rebuild.
Full selected-entry test fails atentry23/sample0, firstdifferentCPUbyte131,
samePC/cycles/hostflags. Preserve generated/game-arithmetic-r443.log. Source
shows a possible precision boundary: IR PS_NEG usesV2F64 FNEG whereas C converts
through paired-single bit helpers. This is a hypothesis for the interior-state
failure, not a diagnosed architectural error or justification for masking it.

Separate explicit --full-entry mode tests only routine start.1000 full-state/
RAM/hostflag plus expectedreturn/cycles/exception cases pass. It cannot satisfy
the failed interior-entry equivalence. ABBA1M normal-entry calls with fixed
vector/constants and reset scalar inputs eachcall: C242.361ns, IR324.104ns,
IR307.270ns, C227.914ns. No captured-gameplay distribution, installedPGO/LTO
parity or FPS claim. Cached objects unchanged. Run93212 exit0, evidence
generated/game-arithmetic-full-r443.log (its old output label says interior-entry;
CLI --full-entry is authoritative; corrected future output to normal-entry).

Decision: PARK R439–R442 LLVM candidate, no full module. Both tested normal
paths regress; size/stack fixes did not deliver execution gains, and remaining
semantic discrepancies cannot be ignored. This is not a universal LLVM verdict.
Do not keep expanding this prototype absent a new evidence-backed mechanism.

Next C execution-path question: profile includes shared entry/return dispatch
and chassis overhead, but exact dynamic guest-entry distribution is missing.
Inspect existing bounded trace before adding instrumentation; retain safe SMC
validation/cycle accounting and don't repeat rejected fixed-size chunk sweeps,
unsafe calls, the R184–187 primary-entry split, or mapping caches. Existing
STATICRECOMP_TRACE_FILE writes PC/LR/CTR/CR/timebase/downcount every2^20 native
dispatches (Run.cpp:117–123), so it can suggest entries but not prove unbiased
frequency or cycle cost. Inspect prior artifacts before a new run. Normal app
remains unchanged.
R443 full repository suite53709 exit0 (generated/check-r443.log); this does not
include or override the deliberately failing interior arithmetic comparison.

## R442 — direct-context state controls size; first execution path slower than C

Added mutually exclusive --context-state staging option. State slots point to
actual CPU context fields instead of duplicate allocas; existing sync/reload
becomes same-location operations that LLVM may eliminate. Entry/guard/cycle/
exception/dispatch logic remains. Unlike memory-state, no volatile accesses
added. This can affect intermediate observability and requires explicit boundary
tests; no blanket equivalence claim.

Fresh generated/llvm-arm64-probe-r442 stage/provenance, strictFP/O2 build and
88k memory,32k exception policy,30k baseline and actual chunk emission19795 all
exit0. ARM64 target/range-table/ABI/execution guards pass. C object byte-identical
4b0734ed. IR object975f6daea01745a95eb62585c35cdb0df0178773cebaf7327e81713089a5fce1;
__TEXT187112bytes versus C134452 (1.39×), stack0xb90=2960bytes. Code growth is
substantially reduced; this alone says nothing about speed.

New probe-llvm-game-execute.py checks object hashes against report and links
both complete1024-instruction chunks to the same actual GXRuntime helper sources.
Fixture enters0x804B6224..0x804B624C (11 entries), finite seeded FPRs,256byte
mapped RAM/GQR0, external fixed LR, FP and HID2.LSQE/PSE enabled. 11000 comparisons
pass whole CPUState/RAM/host flags plus explicit returnPC/cycle/exception checks.
This is a controlled interior merge/store path inside the sampled chunk, NOT a
recorded dynamic gameplay entry or representative gameplay-state distribution.

First link identified missing actual reciprocal tables; added unmodified
cpu_interpreter_table.c, not stubs. First execution then correctly hit program
exception because fixture omitted HID2.LSQE; both PCs700, different precharge
policies. Corrected fixture to explicitly enable paired load/store state. No
backend patch or masked comparison was used to make the fixture execute.

ABBA1M calls each, thread CPU time, full objects, resetPC/downcount per call,
fixed repeated finite data: C36.375ns, IR109.899ns, IR109.827ns, C37.467ns.
Includes chunk dispatch/helper overhead, excludes per-call CPU struct copying.
Not installed PGO/LTO parity, captured gameplay inputs, real-time frame tails
or FPS. Reject speedup claim for this path. Before deciding the whole experiment,
reuse these SAME objects for one arithmetic-heavy path with explicit fixture/
state oracle; no full module or unchanged compile. Existing game remains unchanged.
Evidence generated/game-execute-{r442,fixed-r442,enabled-r442}.log,
game-chunk-r442/report.json and differential/exception-policy/check-llvm-r442 logs.
Full repository suite67481 exit0 (generated/check-r442.log). No installed
gameplay or FPS claim; no live work remains from this step.

## R441 — cached-state promotion isolated; stack improves, code still unacceptable

Added diagnostic --memory-state to staging script. It marks only direct
load/store accesses to private `state*` allocas volatile before optimization,
preventing SSA promotion. Guest memory, CPU context, cycles, instruction entry
points and synchronization rules are not marked volatile or removed. This is
not a shipping optimization and adds mandatory local-memory traffic.

Fresh generated/llvm-arm64-probe-r441 with reservation fix; pinned originals
rehashed unchanged and patch provenance saved. StrictFP/O2 build plus88k memory,
32k exception policy,30k baseline and exact1024-instruction chunk emission all
finish exit0 (same44041). No unchanged full-module build or game launch.

Exact sampled chunk comparison, C object byte-identical across runs:
R440 IR __TEXT2,405,424bytes, stack0x17140=94,528bytes;
R441 IR __TEXT1,243,140bytes, stack0xb80=2,944bytes;
C __TEXT134,452bytes. R441 remains9.25× C code size. IR object SHA
0e62fa7de6d6e3386db45d1a655b085380bbb1bcf2fbb95d396f1f1c78bf1eba;
full identities in generated/game-chunk-r441/report.json, matching C SHA4b0734ed.

Interpretation: changing cached-slot promotion alone removes most pathological
stack growth, supporting the state-merge hypothesis. It does not establish a
runtime speedup, viable whole-module size or all-opcode correctness. Current
form remains NO-GO for full module. FunctionEmitter::materialize writes every
function-wide dirty slot at each boundary; next bounded test should remove
duplicated cache/context state traffic, preserve every entry/exit and rerun the
same semantic corpus and sampled chunk. No expansion to an unrelated compiler.
Evidence configure/build-llvm-r441.log, differential-{memory,baseline}-r441.log,
exception-policy-r441.log, game-chunk-r441.log and game-chunk-r441/ artifacts.
Full repository suite60076 exit0 (generated/check-r441.log); installed app remains
unchanged and no live compiler/runtime remains.

## R440 — actual sampled chunk exposes IR scaling failure; no full-module go

Used existing R422 profile and matching R423 disassembly. func800180A0's top
sites include shared entry/return dispatch, so no arbitrary tiny helper was
presented as the dominant guest block. Selected sampled chunk0x804B60A0:
1143/28822CPU leaves,1024guest instructions. Whole-chunk sample count does not
identify a single semantic function or its dynamic entry distribution.

New tests/probe-llvm-game-chunk.py reads only the exact locally supplied DOL,
verifies SHA2c680585..., maps the range through the DOL section table, decodes
and emits both C and R439fixed IR with cross-chunk range table absent. All code,
words, objects and assembly stay under an explicitly required generated/ output
directory. No game bytes in test source. Run24283 exit0;1024decoded/unknown0.
No runtime execution, full module, profile capture or installed-app mutation.

Both paths use O2/strictFP, but C uses AppleClang and IR uses LLVM20; neither
reproduces installed PGO/ThinLTO/all compiler policy. Object identities and probe
provenance recorded in generated/game-chunk-r440/report.json. C object175752bytes,
IR2426376bytes. llvm-size __TEXT: C134452 versus IR2405424bytes (17.89×).
IR text file~21MiB. Entry prologue saves0xa0bytes then subtracts0x17000+0xa0
fromSP: total0x17140 =94528bytes (~92.3KiB).
This is static code/stack evidence, not measured cycles or whole-game memory.

Decision: current all-entry chunk form is not a defensible full-module candidate.
Inspect state merging/all-instruction entry lowering using this exact artifact;
require a bounded structural improvement before expansion or claiming a tiny
fixture represents gameplay. No FPS gain can be inferred from size alone, and
none is claimed. Existing C/IR correctness corpora remain required for any fix.
Evidence generated/game-chunk-r440/{report.json,c.asm,ir.asm,ir.ll,chunk.c},
generated/game-chunk-r440.log and block-sites{,-804b}-r440.json.
Full repository suite20864 exit0 (generated/check-r440.log). No live compiler
or game remains. emitEntry's every-instruction switch plus cached state slots
is the next source hypothesis; attribution of the stack growth is not yet proven.

## R439 — staged reservation correction passes matched memory corpus

stage-llvm-arm64-probe.py now has explicit --reservation-fix. It remains an
offline experiment, not a production patch. Fresh
generated/llvm-arm64-probe-r439-fixed/staged/probe-provenance.json records source
and staged hashes/diffs; original files are rehashed unchanged. Correction:
normalize both reservation/store addresses, move clearing inside mapped MEM1/
MEM2 stores, sync reservation valid/address before journal and reload them after.
The acquired RAM pointer remains valid for the current write even if remapped.
External writes retain their callback-owned reservation behavior.

Initial staging stopped on an ambiguous load/store text anchor; scoped the edit
to emitGuestStore, then staged into a fresh path. The unused initial
generated/llvm-arm64-probe-r439/staged is a partial public-source copy, not a build.
Correct stage configured with LLVM20, strict FP, O2; build31891 exit0,32steps.
No default toolchain, reference source, normal module or app changes.

Added a journal-mutation mode (new reservation valid/address) to the memory
corpus:88k total. Fixed stage exits0 with zero full-state/RAM/event/flag mismatches.
Same expanded test against unfixed R433 exits1; no comparison masks or weakened
assertions. Also fixed-stage baseline30k, exception-policy32k and probe target/
range-table/ABI/16-block execution checks pass (combined9585 exit0).
Evidence generated/differential-memory-r439.log,
generated/differential-memory-control-r439.log,
generated/differential-baseline-r439.log, generated/exception-policy-r439.log,
generated/check-llvm-r439.log and build/configure-llvm-r439.log.

Boundary: these three reservation defects are fixed in this prototype only.
The separate fault-cycle policy difference remains explicit; broad callback
state/exception semantics, all opcode coverage and full chassis integration are
not accepted. Next one measured R422 gameplay block with a defensible fixture
for C/IR work/cost comparison. No full module unless that bounded experiment
supports meaningful gain; no installed FPS claim or mobile promotion.
Full repository suite84455 exit0 (generated/check-r439.log). Unfixed control
has34000failures on the same88k corpus, versus zero for the staged correction.

## R438 — memory corpus isolates three LLVM reservation-boundary defects

Added --runtime --memory-boundaries to the same public synthetic C/IR probe.
It is mutually exclusive with FP modes. Ten modes ×4entries ×2000seeded states
exercise lwz/stw/addi/blr over128byte MEM1,128byte MEM2 and128byte replacement
RAM: cached/uncached mirrors, final mapped word with following external store,
external read remapping RAM and changing GPR5/GPR6, write callback GPR7 change,
journal remapping (current write retains acquired pointer), and opposite-mirror
reservations. Entire CPUState, all384memory bytes, host flags and ordered callback
address/width/value or journal reservation observations are compared. No masks.

First8mode64k run exits1 with10k failures: external-store reservation state only.
Added journal observation and opposite-mirror cases; complete80k run exits1 with
30k failures, none downcount-only. Source-correlated categories:

- modes4/5 entries0/1 and mode6entry1: C leaves reserve_valid true for external
  writes; IR clears it before mapping or callback.10k cases.
- modes0/1/7 entries0/1: final states match, but C journal sees cleared reservation
  and IR journal sees old true value.12k cases.
- modes8/9 entries0/1: C normalizes bit0x40000000 and clears the matching physical
  line; IR compares raw reserved/store addresses, leaving it true.8k cases.

Actual core/cpu.h:clear_matching_reservation normalizes both addresses;
mem_write32 returns from external route before clearing, and clears mapped
stores before invoking the journal. LLVM llvm_memory_lowering.cpp:139 compares
raw addresses, emitGuestStore:219 clears before mapping, journal:151ff invokes
callback without synchronizing the cached reservation state. These explain the
observed categories. Existing remap test remains the contract reference.

Next staged-only correction: clear only mapped stores, normalize reservation
line comparison, and expose/reload reservation state at journal boundary while
preserving its acquired memory pointer. Add journal mutation coverage before
claiming the boundary fixed. Do not alter production/reference source or mask
the failing test. Other journal-observed CPU state/cycle semantics and memory
exception exits remain broader follow-up boundaries, not proven by this corpus.

Evidence generated/differential-memory-{r438,scope-r438,observer-r438}.log.
Final observer run3416 exit1. Baseline actual-runtime30000cases exit0 in
generated/differential-baseline-r438.log. No gameplay speed or gate claim.
Standalone baseline30k and original callback-remap ASan/UBSan test pass;
full repository suite44758 exit0 (generated/check-r438.log). The failing opt-in
memory corpus is separate and still blocks prototype integration.

## R437 — exception cycle policy resolved narrowly against pinned runtime source

StaticRecompCore_Run.cpp:155–162 consumes negative guest downcount, clamps a
zero-charge dispatch to one, subtracts it from Dolphin downcount and advances
guest timebase/remainder. The R436 difference is observable scheduling state,
not disposable test noise.

Pinned Interpreter.cpp SingleStepInner sets FP-unavailable and checks exceptions,
then returns the faulting opcode's num_cycles. PPCTables.cpp:179–184 gives ps_sub
and ps_add one cycle. JitArm64_Compile.cpp:289 accumulates each opcode's cost
before emitting its first FP check; the failure calls WriteExceptionExit at425ff.
Jit.cpp:624–662 ends that exit with DoDownCount, which subtracts the accumulated
cost (161–165). These source paths support charge-through-fault rather than
charging later unexecuted instructions. This is source evidence, not a new
Dolphin runtime differential or proof of cycle-exact Wii hardware timing.

Added separate --runtime --exception-policy-oracle mode to the existing probe.
It selects only the two paired-op entries with FP disabled, 8 rounding/NI modes
×2000 states each. Expected exception state comes from the actual runtime helper;
expected cycle costs are independently stated: one for IR, remaining suffix for
C. Both entire expected CPU structures, unchanged RAM and host flags are checked.
32000 cases pass (exception-policy-r437.log); normal30000-case differential also
passes (differential-baseline-r437.log). This separate oracle does not suppress
the failing --fp-boundaries comparison or assert C/IR equivalence. Shared helper
use isolates emitter exit behavior; it is not independent validation of that helper.

Decision: retain IR's charge-through-fault; do not blindly match C's overcharge.
No product patch, full module, or performance claim. The existing C policy is
recorded as a distinct correctness issue, not a demonstrated cause of sustained
lag. Next expand memory/callback boundaries, then the bounded measured gameplay
block experiment. Future integration must explicitly accept/reference-test timing
differences rather than hiding downcount in a comparison mask.
Full repository suite91262 exit0 (generated/check-r437.log); this excludes the
deliberately failing broad FP differential and does not establish equivalence.

## R436 — FP boundary differential exposes cycle-accounting mismatch

Extended tests/probe-llvm-c-differential.py with --fp-boundaries: four guest
rounding modes, NI on/off, MSR.FP enabled/disabled, 13 special double bit patterns
(signed zeros, subnormals, boundary normals, infinities, signaling/quiet NaNs)
plus seeded raw bits. Both executions set host mode through actual runtime
ppc_fpscr_control_updated before clearing host flags. The same four public
blocks and every instruction entry are used; no game data or source mutation.

Actual-runtime scope run66343 exits1, as intended for a discovered discrepancy:
480000 cases, 32000 failures, every failure downcount-only. Classification
does not mask fields or turn failures green. First failing case mode8/block3/
entry0/sample0: PC0x800 for both, Cdowncount9997 versus IR9999, host flags0/0,
identical RAM and all other CPU bytes. 8 FP-disabled modes ×2 paired instruction
entries ×2000 samples explain all32000 failures. FP-enabled modes and other
block entries complete without mismatch in this corpus. This is not broad
floating-point opcode or exception coverage.

Source explanation: C emitter.c:1952 precharges cfg.block_cycles at the block
leader (and its external-entry switch charges suffixes); dolir_builder.c:1388
sets each instruction block's cycle_cost. LLVM FunctionEmitter::emitBlock
charges that individual cost, and emitFPAvailable materializes it then returns
on the exception. Thus a fault at the first of two paired operations plus blr
charges3 in C and1 in IR; neither executes the remaining operations.

Do NOT infer that changing IR to reproduce C precharge is architecturally
correct. The actual chassis timing/exception contract and prior C cycle fixes
must decide the expected behavior. Next inspect that boundary and build a
focused expected-cycle oracle. No full module or performance acceptance yet.
Original baseline rerun exits0:30000 cases, zero failures. Logs:
generated/differential-fp-r436.log (first failure),
generated/differential-fp-scope-r436.log (complete scope),
generated/differential-baseline-r436.log. Normal app unchanged.
Full repository suite62530 completed exit0 (generated/check-r436.log).
The opt-in discrepancy probe is not part of that green-suite claim.

## R434 — actual-runtime layout and first C/IR differential corpus pass

New audit-llvm-runtime-layout.py extracts ALL30CPUState fields referenced
by offsetof in the LLVM emitter and compiles independent probes against
standalone and real GXRuntime headers. All30offsets/field sizes match.
Complete structs DO NOT: standalone7608bytes versus runtime3528; cache_control
is at7600versus3520 (not directly referenced by current emitter). Never
copy/cast complete structs as interchangeable. generated/llvm-layout-r434.json
contains compiler-derived results. Helper behavior/module ABI remain separate.

New tests/probe-llvm-c-differential.py reuses R433's staged build and actual
C emitter. Identical decoded synthetic words go through C and ARM64 IR;
C symbols are renamed only at compile time. No direct-call range tables.
Four blocks cover integer add/compare, a local conditional branch, MEM1
load/store/update and paired add/sub.2000seeded cases at every instruction
entry yield30000comparisons of complete CPUState (including PC/downcount),
the128byte RAM payload and host FP flags. No fields are masked out; both
runs use the same host RAM pointer with payload reset between executions.
Standalone run passes (differential-llvm-r434.log).

--runtime uses the real core/cpu.h plus unmodified GXRuntime cpu.c,
cpu_interpreter_float.c and cpu_exception.c, strict FP flags and dead stripping.
It also passes30000cases (differential-runtime-r434.log). This is stronger
than using the standalone helpers, but not Dolphin/chassis integration or
all-opcode/interrupt/SMC/exception coverage. Corpus uses finite FP inputs,
MSR.FP enabled, mapped MEM1 and fixed external return; no broad performance
claim, MEM2/boundary/callback fault or FP-mode proof. Existing nested-comment
warning is unchanged. No original source/app/module modified.

Next extend this SAME differential harness to exception exits, FP modes/
special values and memory/callback boundaries before selecting a measured
gameplay block for code-generation/performance comparison. Do not jump to a
whole-game module from30k narrow cases. Original PRD/G6/mobile hold intact.


## R433 — offline ARM64 IR feasibility probe passes synthetic execution

Pinned DolRecomp requires LLVM19/20, not installed LLVM22. Installed versioned
keg-only llvm@20 20.1.8 using Homebrew without auto-update/cleanup/dependent
upgrades. Default AppleClang21 and product build selection unchanged. Public
Homebrew arm64_tahoe bottle from ghcr.io/v2/homebrew/core/llvm/20, verified
SHA b95ac9e58b54a35797d89b3ac9ec2d56411b47d3942851567a6eb169e5dc9c09;
license Apache-2.0 WITH LLVM-exception; installed footprint1.5GB. No game
data downloaded. install84236 exit0/install-llvm20-r433.log.

scripts/stage-llvm-arm64-probe.py copies public source/tests/tools/license
to a fresh ignored directory and records original/staged hashes and diffs.
Pinned source is not patched. Staged experimental backend requires exact
GALAXYPAD_LLVM_ARM64_PROBE=1 for macOS ARM64 and REJECTS nonzero range
tables, forcing cross-chunk dispatcher returns. A pre-optimization pass adds
zeroext to this pinned interface's unsigned narrow parameters/returns on
declarations AND direct/indirect calls, skipping LLVM intrinsics. This is
not a generic signed-argument ABI solution or a production port. Object
cache reuse is not exercised. Initial staging failed closed because there
are two verifyModule calls; fixed to insert only before the first and staged
fresh. Original source files rehashed unchanged; existing C-emitter overlays
remain untouched.

Configured staged source against installed LLVM20.1.8; build42000 exit0,
then reconfigured both C/C++ with -ffp-contract=off -fno-fast-math and rebuilt
strict25590 exit0. test_llvm_backend emits16 public synthetic blocks to
Mach-O ARM64, and test_llvm_execute passes its expected-value assertions,
including FP/system/memory helpers and bounded loop reentry. Staged final
cross-chunk test explicitly returns to the caller before the next chunk;
it no longer expects chained direct calls to consume an entire budget.

scripts/check-llvm-arm64-probe.py verifies opt-in absence fails with no
objects, supplied range tables fail closed, positive emission succeeds,
16 wrappers call only their own body and no body calls another budget body,
representative mfspr unsigned ABI, and standalone execution exit0
(86iterations/downcount-258). generated/check-llvm-r433.log records success.
This is the STANDALONE DolRecomp CPU oracle, not Galaxy's GXRuntime/chassis
CPU ABI, differential equivalence, all-opcode coverage, iOS execution or FPS.
Next add actual C-backend versus IR block differential tests and audit the
real CPU layout/helper contract before any game-module prototype. No change
to the installed app, production pins or G6/mobile acceptance.


## R432 — vector candidate has no meaningful measured Good Egg gain; park

Fresh prelaunch thermal0/0 and no game/Simulator. Candidate runner671729c6,
signed module220f6aed, prepared vector-candidate-r430 profile. Runtime33740/
PID59889 loaded its exact packaged module before CUA. LoadState2 initially
and final screenshot show the matching hanging scene/life3/Star Bits4 with
ambient animation. Helper40735 exit0:10s warm-up then30s quiet scene.

| Metric | R431 control | R432 vector candidate |
|---|---:|---:|
| VI events / Hz |1652 /55.066667|1653 /55.100000|
| Mean CPU ms |16.651327|16.660554|
| Mean wall ms |18.160719|18.155982|
| p99 wall ms |20.181458|20.127209|
| Mean EFB ms |1.241117|1.232572|
| Worst wall ms |34.577625|27.099292|

Candidate window422173567377541..422203567377541. Worst interval at
+4.965919584s includes9.321871ms idle wait/16.662583msCPU. Both windows
complete/dropped0/invalid0/reset0 and31thermal0/0 rows; no frequency proof.
One additional VI event and unchanged CPU are not meaningful improvement.
The final window title briefly read60FPS; that is not the anchored-window
cadence and must not be reported as the candidate benchmark.

ExactPID SIGTERM/runtime33740 exit0, native2249106054/fallback0/smc_failed0,
real save106e unchanged. No live game/Simulator remains. Evidence in
generated/runtime/vector-candidate-r430 and previous control directory.
No movement-route or whole-game/audio acceptance; normal app untouched.

Decision: PARK this candidate. Its~4% offline THP improvement did not carry
to this measured gameplay scene; do not promote, enlarge the helper patch,
or repeat unchanged timings. Retain the tested experiment/evidence locally.
Next architectural feasibility step: evaluate a SMALL dispatcher-preserving
ARM64 LLVM-IR prototype with actual Apple helper ABI and differential guest
block tests. R426's barriers must be resolved explicitly; no target-guard-only
port, direct-call bypass, precision reduction, full-module build or production
dependency switch. This is a bounded investigation of a different execution
strategy, not replacing the full PRD with a compiler experiment.


## R431 — matched vector control measured; candidate pending

R429 pair linked and packaged successfully; original inputs protected by
hash assertions. Same normal runner671729c6 in both. Control signed module
aa23fc0eb958a5f7658f9e6166dd268f889f8f96c715737c6e7cd7a3404328c0;
candidate220f6aed42c6f36d3346e6b00ad1ed812c86b39925af936c9c305f8a92cc414a.
Candidate's linked ppc_ps_add_op contains fadd.2d (initial disassembly regex
expected GNU operand suffix syntax and missed Apple's mnemonic suffix;
inspection confirmed the actual instruction). No benchmark from that alone.

After build cooldown returned nominal, normal-runner control app loaded its
own module and slot2 visibly restored hanging Mario/life3/Star Bits4. Final
view retained scene with ambient animation. Profile vector-control-r430,
runtime30466/PID59555, helper89761, both exit0 after exactPID close.
10s warm-up then30s window421879666701833..421909666701833:
1652VI55.066667Hz, CPUmean16.651327ms, wallmean18.160719ms,
p95wall19.484209ms/p9920.181458ms, EFBmean1.241117ms.
Worst34.577625ms wall at+1.679537s includes16.615841ms idle wait and
16.523583ms CPU; not a clean smoothness pass. Dropped0/invalid0/reset0,
31thermal rows nominal-or-unsupported/lowpower0. Save106e unchanged;
native1810930177/fallback0/smc_failed0. Static scene, not control-route proof.

This matches earlier R424 AOT55.066667Hz/16.683192msCPU closely, but is
not a randomized original-versus-wrapped-control equivalence proof.
Post-shutdown thermal state was Fair; between-run probe82247 runs60s to
vector-build-r429/between-r431.csv. Candidate profile/package ready but
not launched. Next recover and run candidate with identical method; do not
rebuild or interpret the offline4% result as actual gameplay gain.


## R428 — guarded paired-vector add/sub: correctness and contextual timing

Reference source JitArm64_Paired.cpp:99–115 tracks single-precision values
and operates on both lanes; PPCAnalyst.cpp:820–848 also tracks flag liveness.
These are structural differences, not proof of their individual contribution.
Do not resume the already parked tiny FPRF-site extension. New isolated
ps-vector-addsub.inc instead combines the two finite double-lane additions/
subtractions with NEON, retaining original force_single, lane writes and FPRF
classification. Every nonfinite input takes the original helper; source
cpu_interpreter_float.c remains SHA554149a2...ab934f and is not modified.

tests/test-ps-vector-addsub.py passes640000 whole-CPUState and host FP-flag
comparisons under UBSan/O2: all13^4 special-operand combinations plus random
bits, all4rounding modes, NI off/on and destination aliases. This is bounded
oracle evidence, not a universal proof, hardware trap-handler test or game
acceptance. Its optional isolated CPU-time ABBA uses noinline wrappers and a
compiler memory barrier; three finite payloads measured candidate3.06–3.49ns
versus control6.51–6.88ns (first warm control8.88ns). Not game speed.

Existing full-kernel oracle now supports mutually isolated --vector-add-sub:
it stages a changed float translation unit only, uses the identical extracted
kernel for control/candidate and preserves pinned source/fixtures. Command
`python3 tests/probe-thp-oracle.py --kernels --vector-add-sub` passed all four
sanitized/optimized control/candidate builds:1440cases each, digest
882be09b1f38e9ad,624yields/480FPfaults/480illegal/192interruptions/
96callerreturns/18816callbacks/34688journals/1440reservations.

With --benchmark --cpu-time, CPU-time ABBA summed12case means:
control24900.817, candidate24228.860, candidate23827.126, control25159.357ns;
candidate/control0.959964 (~4.00% less CPU work in this offline workload).
This THP workload checks context; it does not establish the Good Egg speedup
or solve the full10ms reference gap. No installed module/app changed.
Evidence generated/oracle-vector-r428.log and bench-vector-r428.log;
sessions71452/33423 exit0. Full repository suite34575 exit0/check-r428.log,
including the640000-case test. No game/Simulator remains.

Next bounded step: audit cached-module compile/link and PGO provenance for
an isolated same-graph control/candidate using this helper change. Avoid a
regeneration or normal-module promotion; reject a comparison that silently
changes compiler/profile coverage. If a valid pair can be built, measure the
existing visibly verified Good Egg checkpoint and movement route before
deciding whether this deserves promotion. No further unchanged microbench.


## R427 — gameplay state-traffic audit and reference BAT-table comparison

Exact R422 CPU sample/disassembly join (existing R423 assembly of normal
module1fb635f7): func800180A0 has1130 leaves,805loads/14stores; func804B60A0
has1143 leaves,639loads/48stores. Only8stack-memory samples each. These are
sampled PCs, not dynamic instruction counts or removable time. Mechanical
x0/x19-offset grouping points to RAM/EXRAM metadata, downcount, MSR and
exception checks as well as guest registers; base provenance must be checked
at each site before calling it a CPU field. This does not support a dominant
stack-spill hypothesis. R217's actual-header callback/journal-remapping and
field-offset test rerun passes ASan/UBSan. R311 already tested/rejected
callback-bounded mapping caching (~3.51% slower); do not repeat it unchanged.

New bounded experiment changes only Fastmem=False in a separate clone of
R425's accuracy-enabled reference profile. Actual JitBase.cpp:143 and
JitArm64_BackPatch.cpp:78–95 show this selects a BAT-table pointer lookup
rather than the arena path, NOT disabling every optimized memory access.
Same runner34e96be1/slot2 SHA74e453b5/Metal1x/dualcore/Cubeb, FPRF and
AccurateNaNsTrue, exceptionsFalse. No profiler/build during measurement.
Initial and final views show hanging Mario/life3/Star Bits4/ambient movement.

After10s warm-up, window420061904541333..420091904541333:
1798VI/59.933333Hz, CPUmean6.827720ms, wallmean16.683333ms,
wallp9916.709458ms, worst16.761708ms, EFBmean1.603460ms,
throttlemean9.386090ms. Dropped0/invalid0/reset0. This compares with R425
CPU6.257124ms and R424 AOT16.683192ms. Single-order measurements do not
establish an exact causal0.571ms cost, but the large gap survives without
arena fastmem. Do not claim memory access is ruled out: BAT lookup, register
allocation, liveness, helper and execution contracts still differ.

Evidence generated/runtime/reference-nofast-r427/{vi.csv,start-ns.txt,
thermal.csv,runtime.log,Config/Dolphin.ini}; helper51945 exit0 and runtime
31495/PID56843 exact validated SIGTERM/exit0.31thermal rows nominal-or-
unsupported/lowpower0, not clock-frequency proof. Save106e unchanged;
whole-run2underruns/3backlogs is not matched audio acceptance. Normal app
unchanged. No full-module/backend/caching candidate warranted by this test.
Next examine reference versus AOT generated block work (state liveness and
helper boundaries), rather than treating an arena-memory port as the fix.


## R426 — alternate LLVM backend is not a safe drop-in

Read-only audit at DolRecomp fa0cf619e8d7eb8cba7eaf55267a12caaebb46aa:

- src/backend/llvm/llvm_backend.cpp:250 rejects Apple ARM64. Its Mach-O
  cache check at489 checks magic only, not CPU architecture; lifting the
  target gate requires a real target/cache identity audit.
- llvm_runtime_lowering.cpp constructs i8/i16 helper declarations/calls
  without parameter extension attributes. New read-only
  `python3 scripts/audit-apple-helper-abi.py` includes the actual cpu/cpu.h
  and asks Apple Clang21 for macOS ARM64 and iOS ARM64 Simulator IR.
  Both show zeroext on ppc_mfspr's u16 and all three ppc_lswx u8 arguments.
  Tool exit0 confirms this ABI requirement, not backend compatibility.
  No runtime fault is claimed from this source discrepancy alone.
- src/app/pipeline.c:636–643,722–723 supplies the full range table to LLVM
  jobs unconditionally. llvm_control_flow.cpp:26–57 emits direct calls to
  func_*_budget across these ranges. emitBudgetGuard at
  llvm_function_emitter.cpp:430 checks cycle/step budgets, not mutable guest
  code. This does not inherit the C backend's unsafe-direct-call opt-in
  at pipeline.c:1084–1096. A target-port prototype would therefore also need
  safe dispatch/validation boundaries, not merely ABI/target changes.

Decision: do not build a full ARM64 LLVM Galaxy module or loosen the target
guard. Existing Homebrew LLVM22.1.8 is available but is not the accepted
Clang21 toolchain; no install/update or product build performed. The potential
execution gain remains real diagnostic motivation, not evidence that this
backend is faster under the required safety contract. Next inspect C backend
state materialization/helper boundaries in the existing gameplay hotspots
for a structural optimization with measured scope, preserving dispatch.


## R425 — accuracy-enabled reference retains substantial CPU headroom

Same R424 diagnostic runner/checkpoint/settings, now FPRF=True and
AccurateNaNs=True; FloatExceptions/DivByZeroExceptions=False, Core4.
Window419263739438583..419293739438583 after10s warm-up gives1798VI,
59.933333Hz, meanCPU6.257124ms, meanwall16.683334ms, p99wall16.712042ms,
worstwall16.765917ms, meanEFB1.563234ms, meanthrottle10.153434ms.
The corresponding R424 AOT meanCPU was16.683192ms. These accuracy options
do not explain away the gap, but exception handling and execution contracts
still differ; do not attribute the entire difference to compiler quality.

Evidence: generated/runtime/reference-fp-r425/{vi.csv,start-ns.txt,
thermal.csv,runtime.log,Config/Dolphin.ini}. Initial/final scene inspected;
helper41609 exit0; runtime27460 exit0 after exactPID55947 SIGTERM.
Save106e unchanged. Requested window retained, invalid/reset0; overall
buffer dropped5741 later events because shutdown was delayed beyond the
measurement. Not a dropped0 whole-run capture, audio acceptance or product
improvement. Target AOT execution/code generation next; do not ship JIT or
resume fractional helper changes without new dominant evidence.

## R424 — same-runner AOT/JIT reference: large execution gap, precision caveat

Diagnostic signed runner34e96be1/module1fb635f7; prepared independent profiles
reference-aot-r423 and reference-jit-r423, identical slot2 SHA74e453b5 and
save106e. Metal1x/CPUThreadTrue/Cubeb/no mods/VI-only/no profiler or build.
Flag unset selectsStaticRecomp, flag1 selectsJITARM64; actual selection logged,
JIT profile persistsCPUCore4. JIT bypasses the AOT module execution and is not
native-AOT/fallback/coverage acceptance. No shipping app/source was changed.

Both slot2 reloads visually restored hanging Mario at the darker-side rim,
life3/Star Bits4; both final views retain scene/state with advancing ambient
animation. No movement input during timing: stable-scene diagnostic, not a
full control route. Same helper validates exactPID/profile, sets frontmost,
waits10s, takes prospective steady-clock anchor, samples thermal for30s.

| Measured30s | AOT | JIT reference |
|---|---:|---:|
| VI events / Hz |1652 /55.066667|1798 /59.933333|
| Mean CPU ms |16.683192|6.048078|
| Mean wall ms |18.166553|16.683337|
| p95 wall ms |19.426125|16.697083|
| p99 wall ms |20.068375|16.735625|
| Worst wall / CPU ms |23.555292 /22.156834|16.918542 /5.321958|
| Mean EFB elapsed ms |1.222187|1.543843|

AOT window418462854253750..418492854253750; JIT418671414513958..
418701414513958. Complete, dropped0/invalid0/reset0. Each31thermal samples
nominal-or-unsupported/lowpower0; not frequencies or host-load equivalence.
JIT mean throttle10.347942ms, consistent with headroom in this scene. VI is
not display scanout; elapsed counters overlap. Single-order comparison, not
a benchmark of every scene or proof that all historical20–40FPS is explained.

Large CPU-execution-subsystem difference is supported; shared renderer/host
can reach reference cadence here. But source audit identifies a major fidelity
confound: MAIN_FPRF and MAIN_ACCURATE_NANS defaultFalse; no local/profile or
packaged RMG.ini override. AccurateFmadds defaultsTrue. JitBase loads these
settings; SetFPRFIfNeeded also performs per-operation liveness analysis.
Thus the entire10.64ms CPU gap cannot be called avoidable AOT compiler overhead.
No global FPRF/NaN omission or relaxed AOT semantics is authorized by this test.

Prepared reference-fp-r425 with FPRF/AccurateNaNsTrue for next same-runner
measurement. Initially considered enabling FloatExceptions/DivByZeroExceptions
as well, but actual JitArm64 floating/paired emitters FALLBACK_IF those modes;
they would mix interpreter cost into a different comparison. Prepared profile
therefore explicitly retains bothFalse. Even next test is not full semantic
equivalence. Normal user configuration unchanged; no candidate promoted.

Runtimes75083/PID55244 and91196/PID55427 cleanexit0; helpers70485/40245 exit0.
AOT native2340568939/fallback0/smc_failed0. Both save106e unchanged; whole-run
audio95underruns/6backlogs AOT and2/2 JIT include startup/restore/close and
unequal durations, not matched-window audio claims. Evidence respective
profiles/{runtime.log,vi.csv,start-ns.txt,summary.json,thermal.csv} plus ignored
generated/measure-reference-r424.py. No runtime/Simulator remains.

## R423 — reject coarse FPRF gain inference; prepare same-runner JIT reference

Read-only source/profile join gives164eligible sites/68chunks with5065/28822
whole-chunk CPU leaf samples (17.573%). These samples include all chunk work,
not only candidate sites. Exact signed-module disassembly maps80018C04's
classification main range0x22fc9c..0x22fcf4 to5samples and zero/subnormal branch
0x2302e8..0x230318 to0. Materialized PC uses w22=80018B8C plus78; next PC plus7C.
Largest contiguous eligible chain804B6128..804B615C maps to native
0x5f6c6c4..0x5f6ca28 (w23=804B6CE4 minusBBC..B88). Inclusive CPU-stack search,
including out-of-line helper callers, finds0samples. Sampling/unwinding may
miss work; neither zero execution nor exact instruction-cost savings follows.
No high-impact extension justified. Park rather than build from17.57% figure.
Evidence generated/fprf-{coverage,site,stack}-r423.{py,json} and exact asm files
fprf-800180-r423.asm/fprf-804b60-r423.asm; site summary uses existing CLI.

Next discriminator: same cached renderer/runtime, same copied scene/settings,
same diagnostic runner, AOT versus Dolphin JITARM64 on macOS only. This asks
whether shared host/GX/audio work can meet reference cadence when guest CPU
execution changes; it is not a mobile solution or a shipping optimization.
Existing runtime hardcodesStaticRecomp. Unapplied macos-reference-jit.patch
adds exact environment1 opt-in only under Apple+ARM64+notIOS; otherwiseAOT.
Selection is explicitly logged. No clock/EFB/guest-code-validation shortcuts.

Isolated one-object compile/archive replacement/relink succeeded; normal
source053fa674 and all original linked archive/object hashes unchanged.
Unsigned runner7d84ed9ca368c195ffef6c330518b8f6211f45fbda035a611598543b9b8d257b;
signed diagnostic34e96be1bba0441eff255f03b031f0285ea183239cea2f91c4249ab4cd2e09df,
module1fb635f7. Provenance generated/reference-jit-r423/provenance.json.
Audit68742/fullsuite7572 exit0. Actual selector test covers24 cases across
AppleARM64/iOS/otherOS/otherarch and unset/empty/0/1/true/11; this is conditional
selection proof, not an iOS build or JIT gameplay proof. Both disposable
reference-aot-r423/reference-jit-r423 profiles have identical late slot2/save106e.
No launch yet. Use off/on in this same diagnostic binary, not normal-runner
versus new-library comparison; verify warm-up and state reload before timing.

## R422 — late-route normal-app profile and optimization-history audit

Same accepted runner671729c6/module1fb635f7 and arrival slota30fd3ed,
independent late-good-egg-r422 profile, native1x/dual core/VI-only. Foreground
input fixture completed; screenshot shows Mario hanging at darker-side rim,
life3/Star Bits4. Saved local slot2 then requested10s CPU Profiler capture.
Save is asynchronous (first immediate hash check found no file; later file
appeared, no duplicate save requested). Slot2 SHA74e453b5fd20b6a603a9811dfb363c9b66903662bda83971c558f57493adfe01,
reload pending. Capture started after save request; not a benchmark interval
or a guarantee of complete exclusion of save activity.

Export28822 CPU-thread leaf samples: Run3711 (12.88%), chassis_dispatch1256
(4.36%), func_804B60A01143, func_800180A01130, func_805170A0721,
func_8001C0A0594.81 E-core samples/remainder P cores. Same broad distribution
as R419, no new dominant late-route hotspot. Do not repeat unchanged capture.
Native3216200603/fallback0/smc_failed0; save106e unchanged; VI dropped0.
Whole111underruns/6backlogs include startup/restore/save/profile/close and
cannot establish audio acceptance. Evidence late-good-egg-r422/{cpu.trace,
cpu.xml,summary.json,capture.log,input.log,runtime.log,vi.csv,StateSaves}.

Historical O3, Oz, blanket-inline and Gateway-PGO candidates already rejected.
Current profile contains substantial training counts for both top guest chunks;
not a missing-PGO-coverage finding. Upstream capability discovery checked
https://github.com/ExpansionPak/DolRecomp/actions and then authoritative pinned
source: direct cross-chunk calls explicitly bypass chassis mutable-code
validation (pipeline.c1084/emitter.c344); not a safe shortcut. Pinned LLVM
backend explicitly accepts x86-64 Linux/Windows only, not a ready ARM64 switch.
No upstream revision/source graph changed or unsupported option enabled.

Read-only current FPRF audit:164 remaining eligible adjacent first-writer sites
across68chunks (accepted119 decoder sites already transformed); largest37 in
804220A0,23 in804B60A0,16 in804B50A0. Eligibility is not measured savings.
Next quantify aggregate current gameplay contribution before any candidate;
do not spend a rebuild on a small contribution or broaden across observers.

## R421 — normal installed app Good Egg gameplay measurement

Normal runner671729c6/module1fb635f7 rehashed; fresh normal-good-egg-r421
profile copied R418 Config/Wii/StateSaves, regenerated private Pipe. Same
slota30fd3ed and save106e. Metal1x/CPUThreadTrue/CPUCore6/Cubeb, LC byte/pair1,
VI-only, no profiler/compiler. Default host foreground input (no diagnostic
flag); exact-PID frontmost activation followed by short movement visibly
worked. Restored arrival again before the timed fixture. PersistedFalse on
clean exit confirms no background-input policy promotion.

Window416115332054833..416175332054833:3464VI=57.733333Hz, CPUmean16.022547ms,
wallmean17.323149ms/p9518.842ms/p9920.41575ms, EFBmean.571624ms.
Worst interval57.276458ms at+1.162s contains38.383125ms CPU and2.270958ms
EFB: a real hitch remains despite the near58Hz average, not a smoothness pass.
Complete/no drops/invalid/reset. Five-second bins55.8–60.4Hz, final15s
56.0–56.4Hz with CPU17.037–17.200ms, versus early lower CPU14.4–15.2ms.
Frame-time and CPU counters overlap; VI is not scanout. No20–40FPS interval
at five-second scale. Thermal snapshot (two readings only) nominal/unsupported,
low-power0, not continuous frequency/thermal equivalence to R418 Fair.

Final screenshot shows actual movement to the darker-side rim (Mario hanging,
life3, Star Bits1→2). R419 ended nearby but collected6, so scripts do not
prove deterministic trajectories. Normal app not dramatically slower than
diagnostic56.25Hz, but no causal build-speed comparison or improvement claim.
Native3681150059/fallback0/smc_failed0, save106e unchanged, clean exit.
Whole76underruns/13backlogs includes startup/two restores/close; no audio pass.
Evidence normal-good-egg-r421/{measure.py,start-ns.txt,input.log,vi.csv,
summary.json,bins.jsonl,thermal-snapshot.csv,runtime.log}. Next profile normal
runner's late darker-side workload, where sustained CPU exceeds frame budget,
not another early/transient or movie-decoder sample.

## R420 — exact runtime offsets; avoid repeating the R139 lane

Extended the existing offline CPU summary with --binary selection and output
identity; default module behavior retained. Synthetic reference/range tests
cover runner selection, nonselected binaries, aligned raw PCs and unchanged
CPU-thread totals. Actual signed runnerb4df2afa rehashed; Run symbol at
0x100239da4, profiler binary offsets normalized with Mach-O base0x100000000.
Only align raw sample PCs to four bytes; sampling skid remains possible.

Exact disassembly-derived, disjoint Run ranges account for3527 of3549 Run
leaf samples: trace/lockstep234, sampling guard202, call/REL/counter528,
cycle/timebase289, idle check529, exception269, backedge policy774,
chunk validation702. Evidence good-egg-profile-r419/{runner-run.asm,
runner-summary.json,runner-ranges.json}. Idle-check samples do not establish
time spent idle; most land on the configured-PC load. No expensive variable
division: timebase /12 remains multiply-high/shift/remainder arithmetic.
Module dispatch hot offsets map to table lookup, entry checks and epilogue;
guest chunk samples are dispersed across large generated address-range
functions, including entry dispatch and FP-availability checks. These are
not proof that an individual check can be removed or its sample share saved.

Cross-check found R139/R140 already investigated host overhead and dispatch
frequency. Do not replay that lane or remove timebase/interrupt/SMC/lockstep
semantics. No high-impact candidate justified by this profile alone. Next
close the normal-runner versus diagnostic-runner measurement gap using the
same Good Egg checkpoint/visible input route, then choose from actual slow
normal-app frames. This is attribution progress, not a performance fix.

## R419 — Good Egg gameplay CPU attribution lead

CPU Profiler requested10s during repeatable movement input on diagnostic
runnerb4df2afa/module1fb635f7. Arrival reload and post-input movement/Star Bit
collection visibly verified. Export summary has29,266 CPU-thread leaf samples:
StaticRecompCore::Run3549 (12.1%), chassis_dispatch1285 (4.4%),
func_804B60A01115 and func_800180A01076.119 E-core samples, remainder P cores.
These are sampling shares, not exclusive frame-time costs or promised gains.
Profile identifies runtime execution/dispatch as the next attribution target;
it does not identify the user's20–40FPS cause or establish a speedup.

Next inspect exact binary offsets/call paths before changing code. Use matched
unprofiled gameplay for any candidate and reconcile diagnostic versus normal
runner library identities. No return to parked movie optimizations without a
dominant gameplay justification. Evidence good-egg-profile-r419/{cpu.trace,
cpu.xml,summary.json}; native-only clean exit, unchanged save106e, VI dropped0.
Whole-run audio79underruns/6backlogs is not window-scoped acceptance. Full PRD
and macOS-before-mobile acceptance remain unchanged.

## R418 — Good Egg sustained deficit, complete bounded window

Exact arrival slota30fd3ed reload visibly verified; diagnosticb4df2afa runner/
accepted1fb635f7module, native1x/dual core/VI-only/explicit background-input.
60s3375VI=56.25Hz; meanCPU16.127178ms, meanwall17.780783ms;
wallp9519.787375/p9920.885375; EFBmean.883000ms. Worst26.886708ms wall
contains23.516458ms CPU and1.031375ms EFB. Complete/no drops/invalid/reset.
All61thermal samples Fair. Whole-runcolor reads81939 versus depth14354;
counts are not exact-window attribution. Readback elapsed alone is not the
dominant explanation for this window's deficit; counters overlap.
Control input ran42.8s, but no final screenshot before automatic75s clean
stop: post-input position/health remains unverified. Save106e unchanged,
native-only exit. Whole81underruns/5backlogs not window audio acceptance.
No normal-app A/B or20–40FPS reproduction claim. Evidence good-egg-r418.
Next bounded CPU profile in Good Egg, not another opening-movie microbenchmark.

## R414 — input gate isolated; short moving route does not reproduce sustained lag

R415 correction: the host defaults RuntimeConfig background_input=false and
overwrites the INI policy. Thus R414's INI-only change does NOT isolate a
persistent input policy or prove why that run accepted input. Its observed
movement and timing data remain valid; the causal interpretation is limited.
Explicit runner opt-in is prepared/unapplied, not a performance optimization.

Normal current671729c6/1fb635f7 app, Metal1x/dual core/VI-only. BackgroundInput
False produced no button samples despite AX window raise; disposable profile
True allowed same title→real-save fixture and movement. Normal settings unchanged.
Foreground appearance is not itself proof that the runtime's input gate is open.
60s Observatory control segment:59.95VIHz, CPUmean15.1955ms, wallp9517.3236/
p9918.3626ms, meanEFB.5333ms, no drops/invalid/reset.61thermal snapshots Fair.
Visually moved to railing; repeated input lasts42.8s, not continuous locomotion
throughout window. Whole-run7underruns/7backlogs do not establish window audio.
No sustained20–40FPS reproduced, no universal performance or stability claim.
Evidence generated/runtime/scheduler-r413/gameplay-summary-r414.json and original
VI/log/anchor/thermal records. User normal profile is also Metal1x/dual core;
next target actual reported slow scene and broaden gameplay, not tiny helpers.

## R412 — full scheduler capture unusable; reduce instrumentation

Explicit30s retention did not cure expensive System Trace finalization. Storage
watchdog stopped recorder after observed free-space drop exceeded4GiB; child
eventually killed after grace, wrapper exit1. No form.template was written,
so retained timing cannot be audited. No thread-state or performance conclusion.
Failed3.3GiB trace removed after terminal checks; watchdog/log/VI/clock evidence
retained in generated/runtime/scheduler-r411. Normal app and settings unchanged.
Apple's installed package lists standalone Thread State Trace separately from
system calls and VM tracing. Test a1s disposable-process capture before deciding
whether this smaller instrument offers a usable next diagnostic.

## R410 — checked-pair real movie result, parked

Same normal runner, explicit audited controlc002/candidate566 modules, exact
pre-attack slot3, atomic trigger→60s→close, native1x/dual core/VI-only.
Control56.85VIHz/CPU17.412765ms/p99wall18.9525ms.
Candidate57.166667VIHz/CPU17.313438ms/p99wall19.108917ms.
Both complete/dropped0/validCPU/no reset/zero EFB in window; before/after
thermal snapshots allFair, not continuous frequency or host-equivalence proof.
Clean native-only exits/savea574 unchanged; no normal app change.

Park candidate: +.557% cadence/-.570%CPU is marginal and p99 is worse.
No promotion, further unchanged movie pair or claimed gameplay regression pass.
Current worst windows22.7/27.5ms largely CPU; historic80–90ms low-CPU hitches
were not reproduced here. Earlier3% kernel benchmark is not a game gain.

Evidence generated/runtime/s16-pair-{control,candidate}-r408. Next audit
clock/retention/disk controls before collecting scheduler evidence for the
remaining historical hitch class. Old polling cannot distinguish runnable
from on-core, and prior full-window SystemTrace failed before disk cleanup;
any new trace must fix those limitations and remain diagnostic, not FPS proof.

## R407 — checked four-byte signed16 pair, offline only

New scoped pair mapping replaces16 coefficient-load call sites. Fully mapped
four-byte span/type7/scale0/LSQE and bounded sizes required; lane0 assignment
precedes lane1 read, original helper handles all fallback paths. No global
load-helper change or cross-callback metadata cache.

278906 helper cases perASanUBSan/O2 pass including all signed16 values,
rounding modes, boundary/mirror/remap/CPU-alias/oversized declaration cases.
Whole1440-case kernel oracle matches digest882be09b1f38e9ad and callback,
journal, fault, yield and reservation counters; candidate hits4840 each.
Both sides use current05e221CPU helper; fixture equals currentfa455chunk
except include path. Full repository suite84886 passes.

Saved-PGO strictFP/ThinLTO CPU-time ABBA benchmark32926 completed:
control totals24130.576/24163.039ns versus23553.004/23314.597ns candidate
(sum of12pattern means). Mean reduction2.9528%; text229376→212992bytes.
One candidate profile mismatch of34functions is reported. No FPS prediction,
actual input weighting, or gameplay nonregression implied.

Evidence generated/s16-pair-{final,kernels,bench}-r407.log. Next isolated
current-module one-chunk build/audit, then corrected atomic movie and fixed
gameplay checks. Prior per-lane S16 regression remains a warning, not waived.
Normal app/default100 unchanged; no runtime/Simulator left active.

## R406 — current module CPU attribution refresh

Exact signed1fb635f7 module, normal671729c6runner, native1x/dual core/interval100.
Bounded10s CPU Profiler follows pre-attack trigger automatically; visible
checkpoint and subsequent movie advancement verified. Clean exit/fallback0/
smc_failed0/savea574 unchanged. This is a diagnostic, not unprofiled FPS.

31807CPU samples:31772P-core/35E-core. Coefficient chunk5752 and transform
kernels5223+2946 total43.77%. convert_to_double1519, ps_add1328,ps_sub1165,
ps_madd1085,psq_store1060 remain notable. Exact-binary disassembly joins all
selected PCs; kernels6302/8169samples on loads (~77.15%), not proof of load
latency or removable cost. Existing CLZ/PC/mapping hotspots remain; no reason
to repeat parked CLZ, lookup-order, cached-map or blanket inlining probes.

Next new contract question: can two signed16 coefficient lanes share one
checked four-byte mapping while preserving lane order, CPUState aliasing,
callback/fault/GQR/LSQE/boundary behavior? Prior scoped S16 candidate remains
parked; original type0 eight-byte paired load is only a reference for guards.
Require focused oracle and whole-kernel timing before considering a build.
Evidence generated/runtime/decoder-profile-r406; normal app unchanged.

## R404–405 — submission setting does not improve heavy movie

R404 excluded from A/B: screenshots introduced variable post-trigger delay,
candidate crossed into following gameplay (881ms EFB) while control remained
in movie (zero EFB). Persisted windows alone do not prove matched workload.

R405 corrected protocol executes trigger→anchor→60s→validated process stop
atomically, no intervening UI. Same normal671729c6runner/1fb635f7module,
native1x/dual core/LC byte-pair1/VI-only, identical slot3aea2 and savea574.
Control100:56.933333VIHz/CPU17.390578ms/p99wall18.831834ms.
Candidate50:56.816667VIHz/CPU17.397787ms/p99wall19.2825ms.
Both complete60s windows have zero EFB elapsed, dropped0, valid CPU/counters;
clean native-only exits, unchanged saves. Candidate has80.56ms wall hitch with
21.84ms CPU and zero EFB; this setting cannot be credited with removing it.

Park50: approximately-.205% cadence/+.041%CPU, no material overall benefit.
Source OnEndFrame does not schedule readback-driven kicks without CPU access;
this movie's sustained CPU deficit remains. No normal config change, further
unchanged pair or promotion. R403 depth equivalence/service reduction stands
as a narrower diagnostic result, not general stutter acceptance.

Evidence: generated/runtime/submit-movie{100,50}-r405 and atomic helper
generated/run-submit-movie-r405.sh. Next refresh exact current-module CPU
attribution after two-range/store-scale promotions; older R310 profile is a
guide, not current-binary address evidence. Preserve all prior rejected
transformations and require a new measured hypothesis before another build.

## R403 — fixed-scene command submission comparison

Existing R400 diagnostic runner52104227 and signed1fb635f7 module; Metal1x,
dual core, identical slot1 SHA4a421726 restored with no movement. Candidate50
then control100, independent profiles, identical phase/EFB/dispatch/VI tracing.
Automatic60s windows, complete coverage/dropped0. First overflowed untimed
control excluded and retained, not cherry-picked retrospectively.

| Setting | VI Hz | Mean CPU ms | p99 wall ms | Mean depth service ms |
|---|---:|---:|---:|---:|
| 50 | 59.933333 | 15.464545 | 17.568958 | .131727896 |
| 100 | 59.900000 | 15.412025 | 17.845666 | .163288206 |

All matched read rows preserve exact coordinates/callers and three returned
depth values (320,194=f919a9;0,0=fa49df;0,2=fa82e9). Mean service falls~19.3%,
but overall cadence is essentially unchanged and CPU increases~.341%.
Service includes framebuffer CPU/Metal completion wait, not GPU time alone.
Candidate zero window audio events versus control one underrun/two backlogs
near the start; unequal settling and host scheduling prevent causal claims.
Both retain hitches where EFB elapsed is~.4ms (candidate56ms/control93ms wall).
This does not resolve general stutter or justify normal-setting promotion.

Original logs, persisted prospective anchors, complete summaries and stage/depth
analysis: generated/runtime/submit-comparison-r403.json and associated profiles.
Both clean native-only exits/save106e unchanged; no source/app/default change.
Next existing pre-attack movie fixture with VI-only instrumentation, same normal
app and explicit100/50 profiles, to test CPU-heavy regression risk before any
further candidate decision. Do not rerun this quiet scene unchanged.

## R369 — selected normal-package functional verification

Normal bundled two-range module75db...323c passed title→real one-star save→
Observatory movement→native pause/resume→movement→clean close, without a
STATICRECOMP_MODULE override. Runtime14607 exit0/fallback0/smc_failed0 and
save106e...2c90 unchanged; evidence generated/runtime/package-r369. This
closes the installed-package smoke gap, not performance acceptance. Whole-run
182s counters include18s pause and startup/transitions:9831 frames,4 audio
underruns/7 backlog corrections are not steady-state performance measures.
Next isolate uninterrupted selected-package gameplay/audio; R362 movie
approximately56Hz remains unresolved. No new dispatcher gain claim.

## R362 — dispatcher movie regression comparison

Fresh private copies of pre-attack slot3aea2...b7ab8 and savea574...afa6;
same runner/settings, single game, established g6-r85-trigger-attack fixture.
Candidate first window387980120059708..388040120059708:3384VI56.4Hz,
CPU17.550668613ms, wallp9518.794416/p9919.409917ms.
Control second388243450410583..388303450410583:3380VI56.333333Hz,
CPU17.572339819ms, wallp9518.801125/p9919.604875ms.
Evidence generated/runtime/dispatch-movie-{candidate,control}-r362 contains
vi.csv/window-summary.json/runtime.log/trigger.log/host-top.txt/window-start.txt.
Pre-trigger checkpoint and running movie visibly verified for both. Runtime
44944/21506 and trigger-recorder35214/1746 exited0; savea574...afa6 unchanged,
fallback0/smc_failed0/dropped0/invalid-reset0. No game/Simulator remains.
Difference is negligible (~0.12%CPU); no meaningful regression seen in this
pair, not a reproducible movie gain or60Hz/audio pass. No more unchanged
movie pairs needed for a gain claim we are not making. New in-game
save/relaunch regression remains before candidate integration/selection.

## R360 — reverse-order dispatcher gameplay pair

Fresh copies of exact R352 checkpoint/save, same runner/settings and no input.
Candidate first: window386609302514083..386669302514083,
3596VI59.933333Hz, meanCPU15.617004961ms, wallp9516.989625/p9918.887875ms.
Control second:386791748189500..386851748189500,
3597VI59.950000Hz, meanCPU15.718986385ms, wallp9517.297292/p9919.043083ms.
Evidence generated/runtime/dispatch-{candidate,control}-r360, same filenames
as R359. Runtime37107/33168 and recorder68645/19034 exited0; save5040...64a6
unchanged, fallback0/smc_failed0/dropped0/invalid0/reset0. Same hanging scene
visually verified before/after. No game or Simulator remains.

Both orders favor candidate mean CPU (R3590.72%, R3600.65%); combined means
control15.728598252/candidate15.620957250ms, about0.68% lower. Tail timing
also slightly lower in both pairs. All near reference cadence, so this is
small headroom, not a large FPS gain or full stability/audio acceptance.
Stop unchanged timing pairs. Retain unselected549988...692e1 for broader
real-save gameplay, transition, save/relaunch and movie regression before
canonical integration or selection. Host variability not fully excluded.

## R359 — first fixed-gameplay dispatcher pair

R358 build3365 exited0/audit passed; candidate SHA256
5499889a558e44197bb740b3b3c5cc96187bcd80e3a8df097b814cb2703692e1,
114,404,424bytes. Accepted module unchanged. Both profiles copy R352 slot4
406a1cd20209e00852ad3d9a3450e6869c33cdd9a9b8e9dda2abb3d8a1f30e09
and real one-star save5040acdd95157448d660fd02f03c16c17e240523bdfa889ccbd253f9fe5364a6.
Runner856b2e...2b0e, Metal1x, CPUThread=True, CPUCore6, Cubeb120ms.
Visible identical hanging railing position/camera, no input during measurement.

| 60-second window | Accepted control | Two-range candidate |
|---|---:|---:|
| VI events / Hz | 3595 / 59.916667 | 3596 / 59.933333 |
| Mean CPU ms | 15.738210119 | 15.624909539 |
| Wall p95 ms | 17.381625 | 16.896500 |
| Wall p99 ms | 18.612458 | 17.786167 |
| CPU p99 ms | 17.514291 | 16.833125 |

Control interval386110377447541..386170377447541, candidate
386287119935541..386347119935541. Evidence generated/runtime/dispatch-{control,candidate}-r359:
vi.csv, window-summary.json, runtime.log, host-top.txt, window-start.txt.
Runtime30107/18058 and top86930/19671 exit0, saves unchanged,
fallback0/smc_failed0, invalid/reset counters0. Both scenes visually verified
before and after; no profiler or input during measurement. Whole-run underruns
9/5 include boot/load and are not fixed-window audio acceptance. About0.72%
lower mean CPU in this first pair is not reproducible-gain proof. Next one
reverse-order pair with fresh copies, then decide broader gameplay regression
or park; do not promote or run unchanged third pairs.

## R357 — complete-dispatch synthetic benchmark

Recovered completed output in generated/two-range-bench-r357.log; no benchmark
process remains. Original module_export.c and saved PGO/ThinLTO compile flags,
native non-LTO opaque guest stubs, actual module descriptor, 5M calls per mode,
control/candidate/candidate/control order. All expected hit counts pass.
Candidate lookup produces a PGO mismatch warning for one of eight functions;
that function's old profile is ignored, so this is not identical profile coverage.
Control/candidate mean nanoseconds per dispatch: virtual 12.146/6.674,
physical alias 13.931/10.598, mixed misaligned 4.111/3.387,
host-handled 2.895/2.845, host-declined 14.300/9.526,
repeated hot address with host-declined 5.080/3.994. Synthetic binary TEXT
98,304/81,920 bytes. Variation across runs is visible; these are not game FPS
or whole-module size results. Correctness evidence is R355/R356. Next build
an isolated actual module, preserving callbacks and guest timing, then test
the fixed gameplay fixture before selecting or packaging any change.

## R354 — gameplay hotspot shifts to dispatch, not THP

Accepted fixed railing scene10s CPU Profiler:29459CPU-thread samples,
29351P-core/108E-core. Run3391+chassis_dispatch2184 (~18.92%leaf samples).
THP kernels/804530A0 absent; convert_to_double2. This is attribution, not
instruction costs/FPS. Exact dispatcher join:1724load/343branch/78store/39other.
Actual generated lookup has two contiguous ranges but uses page/run metadata.
Next isolate two-range lookup specialization with exact guards/callback/alias
semantics and exhaustive address tests. No timing change/promotion. Evidence
generated/runtime/gameplay-profile-r354 summary.json/dispatch.asm/dispatch-sites.json.

## R353 — fixed-scene gameplay warning persists; signed16 candidate parked

Exact slot4 checkpoint/no movement: control3501VI58.35Hz/CPU16.21918581ms
versus candidate3304VI55.066667Hz/CPU17.34333067ms. Same hanging position/camera,
cleanexit/save unchanged/fallback0/smc_failed0/dropped0. Logs fixed-{control,candidate}-r353.
Route drift removed; host/order effects still possible. Movie gain does not
establish overall improvement. Park d379ff...16a6, no promotion or further
unchanged comparison loops. Next target accepted gameplay CPU hotspot, not
another movie-only helper change. Sustained60Hz/audio/soak remain unresolved.

## R351 — fresh gameplay control faster; candidate promotion withheld

Same real-save/input-script control3515VI58.583333Hz/CPU15.48811081ms vs
candidate3366VI56.1Hz/CPU16.60129596ms. Control cleanexit/save unchanged,
fallback0/smc_failed0/invalid/reset/dropped0. Both below60Hz; ending positions
differ slightly (standing vs hanging at railing), so moving wall-clock inputs
do not isolate identical guest work. Treat as regression warning; do not promote.
Next fixed gameplay savestate without movement to remove route drift, one
matched comparison. Evidence generated/runtime/s16-gameplay-control-r351.

## R350 — candidate real-save Observatory below60Hz; matched control needed

Candidate d379ff...16a6 loaded real one-star save without savestate; visible
position change after8movement/jump/Spin input cycles.60s3366VI56.1Hz,
CPUmean16.60129596ms,p9922.181292; wallp9923.069166. Save unchanged, cleanexit,
fallback0/smc_failed0. Evidence generated/runtime/s16-gameplay-r350.
R28959.9Hz is historical and not a matched regression comparison. Next fresh
accepted-control same route, not promotion from movie-only gains. Audio and
performance remain unmet; transition/save-write/relaunch still unverified.

## R349 — both runtime orders favor signed16 candidate; gameplay gate next

Reverse candidate3182VI53.033333Hz/CPU18.65572827ms vs control3024VI50.4Hz/
CPU19.65344951ms. Fixed60s each, recorded in s16-{candidate,control}-r349.
Both clean exit/save unchanged/fallback0/smc_failed0/dropped0. Combined with
first pair: candidate6300VI/120s52.5Hz vs control5997VI/120s49.975Hz (~5.05%).
Retain isolated d379ff...16a6 for real-save gameplay regressions; no third
unchanged movie pair. No60Hz/audio/soak acceptance, no installed-app promotion.

## R348 — first signed16 runtime pair favors candidate; not promoted

Fresh fixed60s control2973VI49.55Hz/CPU19.9890582ms; candidate3118VI51.966667Hz/
CPU19.05844075ms. Both movie advancement, clean exit, save unchanged, fallback0,
smc_failed0; invalid/reset0. Evidence generated/runtime/s16-{control,candidate}-r346.
Candidate p95CPU20.670333ms,p9922.347708ms. Both still below60Hz; whole-run audio
underruns remain. Reverse order required before retain/park; host variability
has reversed earlier small gains. No installed-app promotion or G6 acceptance.

## R345 — signed16 coefficient-load candidate warrants isolated module test

Complete-kernel oracle all four builds1440cases/digest882be09b1f38e9ad,
4840actual fast hits per candidate build. Only16GQR5 load calls changed.
SavedPGO/ThinLTO CPU-time ABBA aggregate control25064.4065/candidate24524.1995ns
(sum12pattern means),2.1553%lower; __TEXT229376→212992 (-16KiB).
One mismatched profile function warning per build retained. Logs:
generated/s16-kernels-r345.log and generated/s16-bench-r345.log.
No module build or in-game gain yet. Next verified single-object module
experiment and matched runtime evidence before retain/park decision.

## R343 — guarded local-state columns parked

Complete-kernel oracle:1440cases/build, matching882be09b1f38e9ad digest,
24actual eligible hits in each candidate correctness build. CPU-time ABBA
with saved PGO and ThinLTO: aggregate control25048.9935/candidate25818.91ns
(sum of12pattern means), candidate3.074%slower; __TEXT+16384bytes.
Logs generated/local-columns-kernels-r343-retry.log and
generated/local-columns-bench-r343.log. Compiler reports one mismatched profile
function per variant; saved profile use does not mean every function is covered.
Candidate parked; no full module build, app change, gameplay or speedup claim.
Next target removable first-pass helper/memory work, preserving exact exits.

## R339 — fair thermal category alongside recovered56.4Hz baseline

Accepted module60s:3384VI=56.4Hz, meanCPU17.55391ms,p9518.52425,p9918.92521.
60contained1Hz snapshots allfair(1)/lowPower0; no state transition. Reports in
generated/runtime/thermal-r339. Clean exit/save unchanged/fallback0/dropped0.
Current coarse category cannot explain prior46.68Hz by itself; that prior
window lacked thermal data. Frequency is unmeasured, and no throttle exclusion
is justified. Park repeated thermal-only runs. Sustained CPU deficit remains;
next structural transform work needs an exact observable-exit contract.

## R338 — thermal pressure observable without administrator access

CPU-frequency powermetrics requires root; non-interactive elevation unavailable.
Public NSProcessInfo thermalState queried with1Hz bounded read-only recorder.
Three idle samples reportfair(1),lowPower0; generated/thermal-state-r338.csv.
This is actual thermal-pressure evidence, not proof of frequency reduction or
the prior slowdown's cause. Nominal0 can mean unsupported; API caveat retained.
Next align this new signal with accepted-module VI/CPU timings in one run.

## R337 — NaN outline parked after reverse result

Reverse pair candidate50.3333Hz/19.6809msCPU versus control46.6833Hz/
21.2240msCPU, opposite R336. Both second runs slower, so no reproducible
candidate benefit established. Both clean/save unchanged/fallback0/dropped0.
Evidence generated/runtime/add-nan-{candidate,control}-r337. No third pair.
Normal app remains selected. Accepted baseline also drifts substantially;
next inspect CPU-frequency/thermal observability before another micro-variant.
pmset after run reports AC but no CPU power status; absent warnings do not
exclude throttling. No system power or third-party process changes made.

## R336 — NaN-outline module first game pair is slower

Candidate56628cf5...9fcf3b5 passes module audit;114883432bytes (+478864).
Final LTO has no standalone ni_add symbol; cold NaN helper remains.
Fixed60s movie control54.1333Hz/18.2742msCPU versus candidate48.7667Hz/
20.2858msCPU. CPU p95/p99:20.9260/21.8563 versus23.0776/25.3745ms.
Evidence generated/runtime/add-nan-{control,candidate}-r335/{summary.json,host-top.txt,runtime.log}.
Both save unchanged, clean exit, fallback0/smc_failed0/dropped0. Not promoted.
Control is also below recent runs; one reverse-order pair is next to test
run-order/host drift, not an assumption that the entire difference is code.

## R333 — NaN outline passes complete kernels; modest offline benefit

All4reference/candidate sanitized/O2 builds1440cases digest882be09b1f38e9ad,
including callback/journal/interruption parity. With pinned module profile and
ThinLTO retained,200000repetitions per12patterns CPU ABBA averages control
24980.854ns versus candidate24309.2175ns (sum of pattern means): ~2.69%lower.
Fixture __TEXT unchanged229376bytes. Evidence generated/add-nan-kernel-{oracle,bench}-r333.log.
Not a game gain; next exact-graph isolated float-object module experiment and
paired runtime test before promotion. Normal module/app remain unchanged.

## R332 — ni_add NaN outline, correctness only

Exact linked helper assembly and R310 sample join retained in fp-helpers-r332.asm
and fp-sites-r332.json beside the profile. ni_add's875samples include222 at
stack setup and221 at restoration; these are not exact costs. Unlike ni_sub,
it has a frame on its ordinary path. Offline prototype moves only the exact
NaN branch to a cold helper, retaining computed result and exception semantics.
240000comparisons per sanitized/O2 build pass,560NaN results,4rounding modes.
No speed claim or app change. Complete-kernel and module-profile/ThinLTO tests
required before considering a build; prior blanket inlining remains rejected.

## R331 — live policy capture, sustained CPU deficit unchanged

Accepted-module fixed60s movie:3378VI=56.3Hz; CPU17.57575ms versus
wall17.76071ms mean, CPUp9518.55646/p9919.40917. All23776 valid observer
snapshots: policy1(timeshare), current/base31,max63. No policy transition
observed; this does not establish QoS class, App Nap or a scheduling cause.
No product scheduling changes. Evidence generated/runtime/scheduling-r331.
Clean exit, native-only dispatch, save unchanged. Full-run audio still has
underruns; no stability/performance acceptance. Further policy-only captures
parked absent a new hypothesis; focus returns to measured CPU execution cost.

## R329–R330 — normal-entry candidate parked; priority snapshots retained

With saved module PGO and ThinLTO retained, normal-entry copies are ~0.35%
slower offline and add128KiB __TEXT. All1440oracle cases pass; no app change.
See generated/normal-kernel-pgo-bench-r329.log. Candidate parked.

Existing R305/R307 thread recordings already contain pth_curpri. Updated
alignment retains histogram counts, not inferred durations or QoS classes.
R305:31=46995,0=335,46=1; R307:31=47021,0=244. No invalid samples.
Evidence: corresponding runtime directories' priority-r330.json. These
snapshots do not prove App Nap, on-core execution, or a scheduling cause.

## R328 — normal-entry transform copies correct so far; timing pending

Exact instruction bodies copied without entry switches for two normal PCs;
all original interior-entry helpers and outer dispatch preserved. Four oracle
builds match1440cases/digest882be09b1f38e9ad, normal hits816/720. Source grows
355161→497346bytes; no native size or gain claim. Evidence
generated/normal-kernel-oracle-r328-fixed.log. Next add pinned module-PGO mode
to THP oracle and retain ThinLTO for timing; do not infer app speed from a
pipeline omitting saved PGO. No module/app build or promotion yet.

## R327 — corrected fused-tail timing also insufficient

ThinLTO coverage:32sanitizedcases/1008hits pass. Uninstrumented CPU ABBA:
control1857.545ns/fused1832.817ns (~1.33%edge);dense3510.380/3473.971.
Park fused Huffman tail without full-module build. Evidence
generated/huffman-thin-fused-{coverage,bench}-r327.log.
Next investigate normal-entry versus interior-entry joins in the two already
extracted transform kernels, preserving exact fallback/charge/callback contracts;
not another whole-Huffman-chunk split or speculative memory-cache repeat.

## R326 — correcting the offline link pipeline removes the large profile gap

New --thinlto mode preserves optimized IR through final linking and keeps the
harness native/opaque. Sanitized identity and profile-free32-case checks pass.
CPU ABBA profiled1851.371ns versus profile-free1831.442ns (~1.08%edge).
R323's native-object control was4249.01ns: omitting ThinLTO disproportionately
degraded the control. The~57% number is NOT representative of the game pipeline.
This reduced graph still is not exact full-module proof; R325 game remains
effectively unchanged. Park flags-only candidate, keep normal app. Evidence
generated/huffman-thin-{identity,no-profile,bench}-r326.log. Next evaluate fused
source candidate only with this corrected pipeline before any link decision.

## R325 — linked no-profile candidate has no material movie gain

Final candidate577d42c9...9c41 audit passed. Matched60s movie:
control56.116667Hz/17.620464msCPU, candidate56.183333Hz/17.617940msCPU.
Both valid/dropped0/clean exits/unchanged saves/fallback0/smc_failed0.
Evidence generated/runtime/huffman-{control,candidate}-r325. Not promoted.
Exact linked chunk disassemblies differ; flag-ignored attribution is unsupported.
R323 strips ThinLTO for assembly renaming; its~57% synthetic gain did NOT
transfer. Next preserve final ThinLTO pipeline in paired offline test before
another build. No additional unchanged movie repeat or global profile removal.

## R323 — saved-PGO penalty isolated offline

Full Huffman fixture confirms1008fused-tail hits. Long-code CPU-time ABBA
control4245.49ns/fused2102.90; short1818.97/1238.18. However zero-AC paths
also improve, so fusion alone is not established as the cause.
Identical-source/same-flags control4253.29/4243.48 (~0.23%difference).
Unchanged source, removing only candidate chunk's saved-PGO flag:
4249.01/1844.75ns (~56.58%lower),32expected coefficient/state/memory cases pass.
Object __TEXT60096→92952. Evidence generated/huffman-{tail-coverage,
tail-bench,tail-short-bench,identity-bench,no-profile-bench}-r323.log.
This is pre-link CPU microbenchmark evidence, not final ThinLTO/game speed.
Next sanitized no-profile check and isolated one-chunk flags-only module
comparison; prefer that simpler route over fusion or global PGO removal.

## R321 — remaining Huffman tail localized

R310 func804530A0:5048 samples,2324load/759store/1864integer/101branch.
Exact prologue and compiled offsets identify1170 x19 memory-map-metadata samples,
335 downcount samples. Hottest sites57b0028/57aff90 map to guest80453AC8
coefficient table load and80453AAC count-leading-zero result, respectively.
Attribution is sampled PCs, not costs or dynamic counts. Report is
generated/runtime/decoder-profile-r310/chunk1103-sites-r321.json.
CLZ-only and wholechunk splitting remain parked; next test a bounded combined
coefficient-output tail against emitted semantics, with original exceptional and
interior-entry routes preserved. No runtime change or performance claim.

## R320 — DC candidate parked after reverse-order check

Candidate-first57.333333Hz/17.243299msCPU; control-second56.150000Hz/17.610817msCPU.
Both60s windows valid, dropped0, clean exits, unchanged saves and fallback0/smc_failed0.
Together with R319 the pair direction disagrees, combined mean VI edge only~0.45%.
This is not repeatable promotion evidence; candidate remains unselected/parked.
No more unchanged runs. Evidence generated/runtime/dc-{candidate,control}-r320.
Next resolve actual operations behind R310 func804530A0 hotspot before another
semantics-preserving experiment; no mobile or sustained60Hz acceptance.

## R319 — first real-module DC comparison does not show gain

Same runner/native settings, explicit unchanged control versus isolated candidate,
slot3 movie trigger and60s windows. Control56.216667Hz/meanCPU17.614763ms;
candidate55.533333Hz/17.786801ms. Both zero dropped samples, CPU-invalid/reset
intervals, interpreter fallbacks and SMC failures; saves unchanged/clean exits.
Evidence generated/runtime/dc-{control,candidate}-r317/{vi.csv,summary.json,
host-top.txt,runtime.log}. Initial control startup overflow is preserved separately
and excluded. Different wall-window movie progress and run order/background work
limit causal inference. Offline4.03% gain has NOT transferred in this pair;
candidate remains unselected pending reverse-order check. No performance/mobile
acceptance or normal package change.

## R315 — both signed-DC kernels justify isolated module testing

Second-kernel emitted-column test passes262144 comparisons; full combined
1440-case oracle preserves digest/counters, with96 verified hits per kernel in
both sanitized and O2 candidates.200k-per-case CPU-time ABBA mixed ratio0.9597004
(~4.03% faster); kernel0 0.9513120, kernel1 0.9681504. No real-game speed claim.
Next verify current accepted build graph/objects/flags and build an isolated
candidate without replacing normal app/module; then matched movie timing.
Evidence generated/{check-second-dc-r315,oracle-both-dc-r315,bench-both-dc-r315}.log.

## R314 — signed-DC column extension improves bounded fixtures

All65536 signed16 DC values×4rounding modes pass emitted-column whole-state,
memory and hostFP comparisons;1440-case full oracle matches with96fast hits.
Exact paired multiply remains, with original loop/yield/fallback semantics.
200k-per-case CPU-time ABBA ratios: kernel0 zero0.886648/DC0.864432/sparse0.881626,
mixed across both kernels0.977533 (~2.25%). Dense1.007310; no whole-game gain
inferred from synthetic weighting. Next test second-kernel equivalent before
canonical/module work. Evidence generated/bench-dc-column-r314.log and
oracle-dc-column-r314.log; normal app unchanged.

## R313 — zero-column shortcut has pattern-specific benefit, unpromoted

Guarded whole-column fast path keeps exact paired multiply, final guest state,
ordered stores and the original loop/yield boundary.40000 emitted-column state/
memory/hostFP comparisons across4rounding modes pass, including input/output
overlap;1440-case full oracle matches with60fast hits in sanitized/O2 builds.
200k-per-case CPU-time ABBA: kernel0 zero/DC ratios0.890256/0.903165; sparse
1.037620, mixed aggregate0.993354. Not a whole-game speedup claim; no module
build. Next nonzero-DC/zero-AC handling, not repeating the all-zero predicate.
Evidence generated/{check-zero-column-r313,oracle-zero-column-r313,bench-zero-column-r313}.log.

## R312 — guarded repeated DC stores remain unpromoted

One exact three-pair store segment preserves the original fallback and six-store
order while reusing conversion/mapping only on guarded direct RAM.100k emitted
segment cases/14reject guards pass; full1440case oracle matches with192 verified
fast-path hits in each sanitized/O2 candidate.200k-per-case CPU-time ABBA gives
aggregate0.9955605, changed kernel0.9914648 and unchanged kernel0.9996722.
The small apparent gain does not justify a module build. No accepted speedup;
next consider whole-column work elimination, not this segment unchanged.
Evidence generated/{check-dc-store-r312,oracle-dc-store-coverage-r312,bench-dc-store-r312}.log.

## R311 — callback-bounded kernel mapping cache rejected

Exact two-kernel prototype caches pointer/size metadata only between reads;
all94stores and slow helpers invalidate, external reads invalidate before callback.
84000 mapped/remapped/boundary cases, CPUState-alias store, and full1440case
kernel oracle pass.200k-repetition CPU-time ABBA nevertheless regresses about
3.51% (control24595.800/24618.835ns summed case means; candidate25625.517/
25315.953). Text229376→245760bytes. Park without module build. This does not
establish why the candidate is slower, but refutes a speed claim for this design.
Evidence generated/bench-cached-kernel-r311.log and oracle-cached-kernel-r311.log.

## R310 — current decoder hotspot refresh

Bounded10s CPU Profiler on signed module5c2101...e91d:31256 CPU-thread samples,
31198P/58E. Kernel0 5239,kernel1 2839,func804530A0 5048:42.00% combined.
Exact-binary instruction join puts6312/8078 kernel samples on loads (78.14%).
These are sampled-PC attributions, not a claim that loads consume that fraction
of execution time. Current evidence supports structural state/mapping-read work;
callback/alias invalidation must remain correct. No speed improvement claimed.
Film advance/clean close/save unchanged/native-only verified.22MiB trace and
exports under generated/runtime/decoder-profile-r310. Whole-run audio counters
include profiler/state-load effects and do not establish acceptance.

## R309 — exact FMA tie-body outlining parked

Offline source-pinned candidate preserves the single-precision FMA correction,
moving only its guarded body into a cold noinline helper.960000 scalar cases
pass result/exception/whole-state/host-flags comparisons under sanitizers and O2,
including50000 actual tie corrections.1440-case full-kernel oracle also matches.
Short CPU-time ABBA suggested1.93% improvement; increasing repetitions10x
removed it: candidate/control1.0046195 (about0.46% slower). No reproducible
benefit, no module build, no normal-app change. Logs generated/bench-madd-tie-r309.log
and bench-madd-tie-r309-long.log; do not repeat this candidate unchanged.

## R303 — wakeup notification not the captured87ms hitch

120s,7189VI=59.908333Hz,CPUmean15.477628ms,p9917.813375ms.
87.0895ms worst interval includes23.011ms CPU but only.03421ms wakeup;
DVD/gather zero, EFB.307458/idle.174345ms. Wakeup total135.974745ms,
p99.039667ms. Measured notification path excluded for this incident, not a
performance fix or scheduler attribution. No normal promotion/mobile progress.
Save unchanged/clean close; evidence runtime/wakeup-r303.

## R298 — gather wait excluded for captured gameplay hitch

Real-save120s diagnostic:7186VI=59.883333Hz,CPUmean15.4097995ms,
p9917.86625ms. Worst75.698208ms at9.093723s has17.926334CPU,
0.395417EFB,0.386586idle,0.001374throttle,0DVD,0gather ms.
Gather counter valid/zero throughout window; stop repetitions of this boundary.
Next other async waits or scheduling evidence. Save unchanged/clean close;
whole-run audio counters do not establish fixed-window audio acceptance.
No normal-app promotion or mobile acceptance. Evidence runtime/gather-wait-r298.

## R293 — 88ms gameplay hitch is not DVD-result waiting

Fixed120s7189VI=59.908333Hz,7188complete/valid intervals. CPUmean15.339435ms,
p9917.742208ms; wallp9919.098958ms. At82.174217s,88.335125ms wall versus
23.071750CPU,0.334EFB,0.308541idle,0.001582throttle,zeroDVD. Small measured
waits do not account for long interval; do not infer GPU/scheduler causality.
DVDtotal31.995288ms,p990.09825. Clean close/save5040...64a6 unchanged,
native4105704564/fallback0/smc_failed0. Whole245s3underruns/8backlogdrops is
not window-specific audio acceptance. End screenshot shows changed Mario
position; no movie/soak/fullG6 acceptance. Same isolated runner, normal app
unchanged. Stop DVD-only repeats; next remaining FIFO/async/scheduling boundary.

## R292 — DVD wait instrumentation runtime check

Isolated runnerab221c...9c480, unchanged signed module5c21...e91d. Real-save
eight movement/Jump/Spin cycles, before/end screenshots show movement and
end hanging ledge (different exact end position fromR289, not matched overhead
measurement). Fixed60s3588VI=59.8Hz,CPUmean15.353678ms,p9918.4255ms.
LargestVI25.556834ms (no55ms incident); DVDtotal14.477747ms/minute,
largestVI's DVD0.000209ms. All3587interval counters valid/no resets.
Normal app unchanged; no regression/performance promotion inferred. Save
unchanged/clean exit/native3302073185/fallback0/smc_failed0. Whole209s
34underruns/7backlogdrops is not window-specific audio acceptance. Evidence
generated/runtime/dvd-wait-r292. Next bounded120s larger-hitch capture only.

## R289 — accepted gameplay sustains average rate, hitches remain

Current accepted runner e86f...22b689/signed module5c21...e91d, native1x Metal,
real one-star Observatory save, VI-only recorder and low-frequency host top.
Eight movement/Jump/Spin input cycles, visible before/after position change.
Window359517108479958..359577108479958:3594VI=59.9Hz,3593complete intervals,
zero invalid/reset. CPUmean15.075371ms,p5015.557083,p9516.694833,p9917.498791;
188/3593 above16.667ms CPU. Wallp9918.806375ms. This scene has more headroom
than the movie's~17.654ms mean CPU, not a whole-game guarantee.

Worst at31.786s:58.928667ms wall/24.665792CPU/0.183624EFB/4.340656idle.
Next31.841s:54.534458wall/22.915458CPU/4.719875EFB/0.295166idle.
These elapsed counters overlap and do not fully localize non-CPU time.
Last host sample runner137.1%,WindowServer46.0%,kernel43.6%,logi28.5%.
Whole258s run2underruns/6backlog drops is not fixed-window audio acceptance.
Clean close/native3803902777/fallback0/smc_failed0/saveunchanged. No source
or artifact promotion. Evidence generated/runtime/gameplay-r289. Next bounded
wait attribution/hook-coverage audit, not repeating this smoke unchanged.

## R288 — host charge-reset policy confirms no mapping-cache gain

Actual host flushes and zeros module downcount after each dispatch. Added
--runtime-charge-reset fixture mode (exact native aggregate charge retained
for parity). It does not emulate timers/interrupts/minimum host charge/timebase.
Compiled actual-wrapper regression covers reset and legacy behavior.
Sanitized32long-code cases/1646loop reads pass. Warmed ABBA128timing rows:
candidate/control1.003645, perlength6:1.004736,8:1.002325,12:1.007242,
16:1.000928. Snapshot stays parked; no module build or repeated identical test.
Artifacts generated/huffman-reset-{check,bench}-r288.log. App unchanged.

## R287 — long-code coverage closes gap; mapping snapshot parked

Synthetic canonical singleton codes at6/8/12/16bits, sparse/EOB versus dense+1
coefficients, starting bit counts1/27/29/32. All32 cases pass independently
expected coefficients plus fullCPU/6MBmemory parity under ASanUBSan. Both
exhausted and1M initial cycle-budget modes record1646 changed-loop reads.
Bounded re-entry cap4096 accommodates long exhausted-budget decoding; initial
256-call harness assertion was not a product failure.

Warmed10000-call ABBA percase: candidate/control1.00202893 exhausted budget,
1.00312855 large budget. Large-budget perlength ratios6:1.00980,8:0.99884,
12:1.00822,16:0.99842. No convincing speed benefit even with exercised loops;
park snapshot variant, do not build/promote or repeat unchanged. Synthetic
distributions are not movie weighting; timing is pre-link acceptedPGO, not game.
Evidence generated/huffman-long-{coverage-r287b,bench-r287,budget-check-r287,
budget-bench-r287}.log. Full suite passes; normal app unchanged.

## R286 — read-loop mapping snapshot requires representative fixtures

Exact15 read-only search loops snapshot four RAM/EXRAM metadata fields;
every slow read refreshes all four after callback. Outer code/entries/cycles
unchanged. ASanUBSan and O2ThinLTO pass65536 full-chunk comparisons and
205570 callback-driven mapping changes (pointer/size/next address).

Existing32 one-bit synthetic Huffman fixtures report cached_loop_reads=0.
Their candidate/control0.9947955 timing ratio is therefore not evidence of
the proposed reuse benefit. Source still changes layout, so even a small timing
shift cannot be assigned to the loop fast path. Add valid long-code tables and
prove nonzero loop coverage before further timing or any module build.
Artifacts generated/cached-loop-{reads,remap,remap-o2,bench,coverage}-r286.log.
No app change/promotion or mobile work. Repository suite passes.

## R285 — exact add/sub scalar helper inlining parked

Only always_inline attributes added to ni_add/ni_sub in a temporary float TU;
same accepted extracted kernel on both sides, no arithmetic-body changes.
All four oracle variants match1440cases/digest882be09b1f38e9ad. Thread-CPU
ABBA sum12pattern mean control24232.437ns versus candidate24767.3645ns,
~2.2% slower, with text229376→212992bytes. Short batches show variation;
not a precise slowdown estimate, but no evidence supporting a module build.
Park this helper-only variant, do not repeat unchanged. Logs generated/
thp-inline-add-sub{,-bench}-r285.log. No PGO-linked runtime claim or promotion.

## R284 — sustained CPU budget, not only worst-hitch summaries

Added nearest-rank p50/p95/p99, mean, total, known/missing count and strict
16.667ms budget count over all complete retained intervals. CPU validity and
counter resets remain null, never zero; elapsed wait counters are not disjoint.
Recorder uses CLOCK_THREAD_CPUTIME_ID at vi_end_field_event, not process CPU.

Quieter accepted R282:3356 intervals,59.246212s CPU/59.994651s wall (98.75%).
MeanCPU17.653818ms,p5017.790875,p9518.657542,p9919.177708;
2911/3356 (86.74%) above1000/60ms. Idle-wait total0.570579s (overlapping
elapsed instrumentation, not subtracted). R283 accepted meanCPU17.611376ms,
p9518.640709ms corroborates the sustained budget problem. Minimum mean CPU
reduction to fit16.667ms is about5.59% on R282, ignoring remaining overhead;
this is a budget calculation, not a predicted achievable improvement.

Contended R281 control:meanCPU32.817492ms versus54.580026ms wall, and36.066s
CPU/59.983s wall. Thus the severe collapse includes both increased CPU time per
VI and time not accounted as thread CPU; it cannot be called just GPU wait or
just scheduler starvation. Different scene progress under slowdown limits direct
per-VI work equivalence. Frequency, core placement and contention remain leads.

Artifacts:generated/runtime/dcbz-*/budget-r284.json (five recorded windows).
No fresh runs, product changes or candidate promotion. Next use exact GXRuntime
paired-single helpers/complete-kernel oracle to target sustained CPU execution;
the R214 profile points at THP kernels/decoder, not a new runtime attribution.

## R283 — cleanup interrupts confirmation; no promotion

Second control3364VI/60s=56.066667Hz, candidate3384=56.4Hz. Both zero invalid
CPU/reset counters, save unchanged, clean exit, fallback0/smc_failed0. Candidate
worst87.184959ms wall/25.607833CPU/0EFB/0.275961idle. Simulator erasure was
explicitly authorized between these runs; asynchronous reclamation continued
during candidate (CoreSimulator84.9%CPU in last host sample). Do not aggregate
as a clean BAAB or infer that storage cleanup/candidate fixed the lag. Candidate
remains parked/default-off; normal app unchanged. Evidence under
generated/runtime/dcbz-{control,candidate}-r283. Next larger-cost investigation
from existing decoder/VI profiles, not another unchanged helper/A-B loop.

## R282 — fresh first runtime pair: small edge, not accepted

Candidate56.3333Hz (3380VI/60s), accepted control55.95Hz (3357),~0.685% edge.
Same runner, fixture, settings, VI recorder and low-frequency host-top sampling.
Both save-unchanged/clean-close/blockfallback0; no movie completion/audio acceptance.
R28118.33Hz control under heavy host load is excluded. Current~7.7%JumpConnect
versus prior315% is a contention lead, not proof of causation or identical scheduling.
Both have~90ms worst intervals mostly not CPU execution and not explained by
measured EFB/idle waits. Next reverse order under same instrumentation; no promotion.

## R278 — completed synthetic Huffman blocks improve offline

Loop-preserving line clear:32 synthetic Y-decoder fixtures pass full-state/memory
parity. Warmed100k ABBA thread-CPU batches give aggregate candidate/control
ratio0.901635, all32 improving. Zero/dense/mixed pattern ratios0.571/0.940/0.906/
0.909. Includes identical fixture reset/assertions; output checks outside timing.
Accepted PGO retained; decoder objects are pre-link (no ThinLTO) to permit symbol
renaming after PGO. No real-movie weighting or app-speed claim. This supports an
isolated runtime candidate next, not promotion. Logs generated/huffman-throughput-
{check,benchmark,long}-r278.log and source-only tests/fixtures/huffman-throughput.c.

## R277 — line-clear compiler profile guard

Removing the generated loop invalidates its PGO and grows the decoder body;
that form is not a build candidate. Keeping the loop while preparing a guarded
RAM pointer retains profile matching. Total pre-link ARM64 instructions12,227
versus12,233, with more loads and helper calls: no performance claim. Both
focused and complete-chunk differential suites pass. Next benchmark completed
decoder work; app unchanged. See JOURNAL R277 and generated/dcbz-loop-*-r277.log.

## R276 — decoder cache-line clear candidate: correctness only

Eight dcbz sites in accepted decoder chunk expand to eight mem_write32 calls
each. An isolated guarded full-line clear passes18,740 helper cases and65,536
whole-chunk cases in sanitized and optimized configurations. Journals, partial
mapping, external writes and CPU-state overlap retain original ordered stores.
No timing, module build, app change, or speedup claim yet. Next whole-decoder
offline timing/code-shape check; see JOURNAL R276 and generated/dcbz-*-r276.log.

## R238 — accepted control does not reproduce sustained deficit

Acceptedrunner, copiedR237configs/ordinarysave, diagnosticsunset: screenshot
59.9–60FPS across Observatoryload/movement. Sequential/shorter run does not
prove candidate regression (candidateR236also59.9Hz). GFXidentical; current
desktopRelease/-O3; hostAC100%/lowpowermode0. No clock/thermal equivalence proof.
Candidate remainsisolated. Cleanclose/saveunchanged; no broad performance pass.

## R237 — sustained slowdown with recorder disabled

Candidate02b0...cb51 Observatory screenshots52.1/48.2FPS,laterAX49.2.
One-second10ms stack sample:77CPU samples,60underchassis_dispatch (including
3floatfuturewait); video46/77conditionwait. Supports primarilyCPU-side work
in this shortsample, not exact cost attribution or hardware limit proof.
No timingfile/export, ordinaryload/movement/cleanclose/saveunchanged.
Next acceptedrunner matchedcontrol before excluding candidatebuildregression.
Separate this sustained deficit from R236's isolated61.6ms mixedwork/wait hitch.

## R236 — memory-only timing captures work versus nonexecuting time

Isolated diagnostic runner02b0...cb51, no streamingphase/profiler. Selected120s
340472883492916..340592883492916 contains7188VI=59.9Hz. Longest interval
61.630834ms wall versus25.207917ms current-thread CPU:~36.4ms was not CPU
execution. Could be blocking or descheduling; no specific wait source proven.
CSV16384samples/allclockvalid,2055laterdrops; selectedwindow ends before last
retainedsample. Export only aftershutdown confirmed, cleanexit/saveunchanged.
Not acceptedapp promotion, physical performance, or fixedwindowaudio proof.

## R232 — full System Trace parked after disk exhaustion

Explicit60s retention capture failed134 during finalization, consuming4GiB
incomplete trace plus4GB orphan kernel trace. No usable scheduler attribution.
Only those newly generated failed-capture artifacts were permanently removed;
logs/phase/host/crash evidence retained, free space restored4.1GiB.
Runtime closed cleanly/nativeonly/saveunchanged. No performance fix claimed.
Do not retry heavyweight capture. Next inspect bounded memory-only in-process
wall/thread-CPU timing with shutdown flush, to classify gaps without trace I/O.

## R231 — R230 kept the last10seconds, not the first

Saved raw timing metadata: recording60.95057s, discarded prefix50.95057s,
retained last10s. audit-trace-window.py validates these values; focusedtests pass.
TOC start date alone is an invalid anchor for retained relative timestamps.
Earlier-run wall/raw clock extrapolation suggests retained interval missed major
hitches (599VI,max23.735ms), but is not exact alignment. No causal inference.
Next capture requires explicit --window60s plus contemporaneous clock anchors.

## R230 — scheduler trace scope must be reconciled

Requested60s System Trace, but exportedTOC/thread-state rows cover10s only.
CPU thread Running8.973s/Blocked.793s/other.234s is attribution within that
interval, not yet aligned to any phase hitch. Saved scheduler-r230 trace/XML.
Profiler finalization visibly coincides with27.8FPS; after exit same scene60FPS.
Do not use profiler-disturbed cadence as baseline or infer historical22FPS cause.
Next verify actual capture timeline and phase correspondence before changing code.

## R229 — hitches persist without midwindow screenshots

Matched active-r229 ordinary save/16 control-smoke cycles and120second host
recording, no CUA in timed window.7193 VI/begin/present events=59.9417Hz;
presentation max78.475291ms,27gaps>=20ms versus R22889.996ms/29gaps.
VI gaps68.832/69.483/58.334ms occur at8.482/89.659/111.036seconds.
No swap/pageout/compression. Screenshots are not necessary to reproduce these
hitches; this does not establish their cause or zero capture overhead.
Before/end scene proof only; end Mario hangs from ledge, no remote warning.
Next scheduler capture distinguishes busy CPU from blocked/descheduled time;
phase logger mutex/line-buffered I/O remains a possible diagnostic observer.
No claim of fixed22FPS, stable60FPS, full soak, or audio acceptance.

## R228 — active Observatory test, near60 average but hitches remain

Accepted packaged module5c21...e91d; active-r228 uses disposable ordinary
one-star save and16 repeated movement/jump/Spin smoke sequences. Before,
two intermediate, and end screenshots show active Observatory/no interruption.
Fixed120s starts337515665936416:7186 VI/begin/present events each=59.8833Hz.
Minute presentation rates59.8167/59.95; p9919.240709/18.779458ms;
max89.996/66.040542ms and29gaps>=20ms.24host intervals have zero swap,
pageout or compression. VI/DMA/input gaps coincide near elapsed41/82seconds,
audio callbacks remain~10.7ms. This is hitch evidence, not a cause diagnosis.
Midwindow screenshot timing was not independently stamped; next isolate
observation overhead using matched active input with before/after visuals only.
No claim that historical22FPS or heavy movie55FPS is resolved. Runtime/input/
recorder closed0; save unchanged. Whole-run audio totals are not window results.

## R227 — distinguish emulation and presentation cadence

Window FPS uses PerformanceMetrics::GetFPS, counted by Core's after_present
callback; VI ticks are a separate counter. Scene analysis now reports
vi_end_field/frame_begin/present_done counts and Hz independently. Focused
event-separation and boundary tests pass. R210 fixed movie records3319 of each
in60s (55.3167Hz). R223 records35919 of each in600s (59.865Hz), saved in
runtime/sustained-r223/cadences-r227.json. No sustained presentation-count
deficit appears in these windows, but callback timing is not display scanout
proof. R223's guest warning still invalidates uninterrupted gameplay acceptance.
Exact RMGE01 code corroborates a default five-minute remote-idle timer;
actual warning reason/onset was not recorded. No timer bypass added.
Next active-play test needs periodic visual checks, not another unattended idle
soak. Historical22FPS remains unexplained; machine-only blame is unwarranted.

## R226 — ten-minute cadence result invalid as sustained gameplay

Ten-minute fixedwindow35919VI=59.865FPS, perminute59.4333–59.95,
maxgap107.013334ms,133gaps>=20ms.120host intervals have zero swapping,
pageouts and compression. HOWEVER end screenshot shows guest remote
communications-interrupted overlay; onset unknown. These counts include an
unknown amount of interrupted gameplay and cannot satisfy scene/soak acceptance.
Neutral+A clears the warning; cleanexit/native-only/NAND unchanged. Next remote
idle-disconnect investigation, not another unchanged timing run. Evidence
runtime/sustained-r223/{minutes.json,host.jsonl,phase.csv,runtime.log}.

## R221 — FP-check route parked

OfflineABBA24590.3/25868.7/24508.7/24697.2ns; firstcandidate disturbed,
secondcandidate only~0.55% belowcontrolmean. Text grows16KiB. No reliable
gain, so no fullmodule build/promotion/unchangedrepeat. Existing app unchanged.
Read-only current normal graphics/Core settings match controlled1x/Metal setup;
that does not explain the historical22FPS episode. Next verify normal module
discovery and sustained gameplay behavior using disposable state.

## R217 — metadata reuse constrained by callback semantics

Actual-header O2ASanUBSan regression demonstrates mutable external-read metadata
and journal ordering: current store uses its pre-callback pointer; following
access observes remapping. Blanket cross-callback caching is invalid. Exact
field offsets320/344 identify exception/reservation state in prior samples.
Next inspect EXRAM-first lookup overhead on MEM1 accesses as a narrower,
semantics-preserving branch-layout experiment; no product change yet.

## R216 — sampled instruction families

Exact-disassembly join resolves all selected kernel/decoder PCs. Kernels:
6069/7913 samples land on loads (~76.7%),334stores,216calls,289branches,
1003integer/other,2scalarFP. This is sampled-PC attribution, not instruction
cost: helper arithmetic appears under other symbols and sampling skid applies.
Frequent x19-relative reads cover MSR and RAM/exRAM mapping metadata. Next
audit mutation/alias contracts before considering reuse across instructions;
preserve callback, exception, journal and timing semantics. New classifier has
focused tests; full repository suite remains to rerun. No product change.

## R214 — updated movie CPU profile

Ten-second CPU Profiler capture on signed5c21...e91d:31295CPU-thread samples,
31248Pcore/47Ecore. Kernel0 5112 and kernel1 2801 (~25.3% combined),
func804530A0 5015 (~16%), convert_to_double1517, ps_add1372, ps_sub1203.
Inlining shifts leaf attribution; these percentages do not measure the prior
optimization's gain. Exact instruction offsets and cycle weights in
runtime/thp-profile-r214/summary.json will guide the next targeted experiment.
No new FPS acceptance, blanket threading or renderer inference. Runtime closed
cleanly/native-only/NAND unchanged; accepted package untouched.

## R213 — signed package smoke passes

Bundled signed5c21...e91d loads ordinary one-star Observatory save, responds to
movement and closes cleanly with fallback0/SMCfailed0/NAND unchanged. No savestate
or phase trace in this run. Whole153.7s3underruns5backlogs are not an audio/soak
pass. Module promotion is verified; sustained60Hz remains unmet. Next profile
residual movie CPU cost on the updated artifact, not another unchanged FPS run.

## R212 — canonical module packaged locally

Normal app now contains signed canonical module5c21010733a5cb3cf8231853f96963e3d433796c062106fdaf6b4261fe0be91d,
derived from unsigned1180...c631. Package/signature audits pass; wrapper, runner
and frontend remain byte-identical via --module-only packaging. Previous app
retained at GalaxyPad.app.previous.20260907T023102Z. Fullsuite89902 is running;
signed package runtime smoke remains next. This retains the measured2.883%
movie gain without claiming sustained60Hz/audio or the broader G6 gate.

## R211 — fresh comparison supports canonical promotion

Accepted control fixedminute53.7666667FPS,p9920.397166ms,80VIgaps>=20ms,
DMA28.6997333kHz. Canonical R21055.3166667FPS gains2.883%, with17longgaps.
Same R85/native1x/Metal/phase-only policy and runner. Baseline completes movie,
closes cleanly/native-only/NAND unchanged. Whole218.4s116underruns3backlogs
are not fixed-window audio acceptance. No unchanged third timingrun planned.

Proceed to package canonical module while preserving verified runner/frontend.
Normal app remains unchanged until packaging/audit; sustained60Hz/audio open.

## R210 — canonical movie result

Canonical1180...c631 fixed R85 minute:3319VIframes,55.3166667FPS,
p9919.602916ms,17gaps>=20ms,DMA29.5338667kHz. Phase-only trace,
accepted runner/native1x/Metal. Movie completes, post-movie movement works,
clean shutdown/fallback0/SMCfailed0/NAND unchanged. Whole241.5s86underruns and
7backlogs are not fixed-window audio acceptance. Evidence runtime/thp-movie-r210.

About2.85% above older accepted R201, not fresh paired proof. Next one fresh
accepted control to decide canonical promotion; no unchanged candidate repeat.
Normal app unchanged, sustained60Hz/audio still unmet.

## R209 — canonical build and real-save regression pass

Canonical module1180447313459c4c153ca74e5215811e88a9b69a00d15feff940f062148fc631
is114404568bytes; architecture/chunk/SMC audit passes. Both kernel symbols and
expected policy/source/PGO manifest entries are present. It differs from the
experimental linked binary, so prior movie timing is not transferred blindly.

Untraced canonical runtime loads one-star Observatory via normal file selection,
passes native pause/resume and visible movement, closes cleanly with fallback0,
SMCfailed0 and unchanged NAND. Whole137s8underruns9backlogs include deliberate
12.45s pause, not audio acceptance. Next fixed R85 movie on this exact artifact
before normal package promotion. App unchanged; G6 remains open.

## R206 — canonical source scope verified

Fresh generation differs from accepted FPRF output only in chunk1102; all other
generated files, headers and SMC data compare equal. Chunk1102 matches the tested
kernel candidate after include normalization. Canonical compilation remains
active (session28332); isolated real-save profile thp-canonical-r206 is prepared,
not launched. No new timing result or package promotion.

## R204 — canonical bootstrap integration passes

Patch0016 is now applied through SHA-pinned bootstrap, after the existing FPRF
policy. Two bootstrap passes and repository checks pass. The port tool links;
an incremental verification build exits0. Source-level regression checks ensure
the THP policy participates in cache identity before lookup and follows FPRF.
Canonical module reproduction and packaging remain unverified; the normal app
is unchanged. This integration adds no new performance measurement or G6 claim.

## R203 — reproducible extraction policy prepared

The new C++ policy produces byte-identical source to the tested kernel candidate
(normalizing only the generated header include). ASanUBSan policy test passes
identity/hash refusal, reapplication, missing-label, outside-branch and missing
entry guards. Policy applies only to exact RMGE01/DOL/C/1024 and requires the
accepted post-FPRF chunk hash before writing fresh generated output.

Prepared0016-rmge01-thp-kernels.patch adds a separately keyed
`thp_policy=rmge01-thp-kernels-2-v1` to cache identity/manifest before lookup and
runs extraction after the unchanged FPRF policy. SHAef25620e8ec254b1c5eecf2bfa386ad60c06f085ac3cca0a1996cba611cf8f6f;
standard gitapply--check passes. NOT applied: bootstrap pin/order/idempotency and
compiled tool/canonical module/package validation remain. No new FPS result.

## R202 — candidate real-save/lifecycle compatibility

Untraced candidate2c29...bbad8 with acceptedrunner, fresh one-star NAND and no
savestates. Ordinary title/file-select/load reaches Observatory; pause indicator
appears, resume clears it, movement visibly changes Mario/camera.50119runtime,
91852load,18112movement all exit0; fallback0/SMCfailed0/saveSHA5040...64a6 unchanged.
Whole326.6s18underruns/17backlogs include deliberate56.37spause and are not a
sustained cadence/audio pass. Evidence generated/runtime/thp-save-r201/runtime.log.

Proceed to separately keyed canonical kernel extraction after the accepted
119-site FPRF policy, not experimental binary copying into an old cache. Exact
transformed-source parity and bootstrap/module/package verification remain.

## R201 — fresh accepted control supports kernel candidate

Accepted494c...3fbe, same R85/native1x/Metal/phase-only policy as R200candidate.
Fixedminute3227VIframes=53.7833FPS,p9920.2855ms,65gaps>=20ms,DMA28.7168kHz.
Candidate55.7833FPS is3.7186% higher, with29gaps>=20ms and29.7813kHz DMA.
Retain for regression and canonical integration work; neither run reaches60Hz.
Do not repeat an unchanged third timingrun now or declare audio fixed.

Control91529/trigger20958exit0, visible movie completion/plaza, clean native-only
shutdown/SMCfailed0/NANDa574...afa6 unchanged. Whole382s108underruns5backlogs
cannot substitute for matched audio counters. Evidence generated/runtime/
thp-control-r201/{measurement.json,phase.csv,runtime.log}. Candidate unselected.
Next untraced real-save/lifecycle regression using prepared thp-save-r201.

## R200 — linked kernel candidate movie result

Original73103 link completes/audit passes; module SHA
2c29e27fa245b3b4bba41519204b6dca927feee26368a4a27f5876cc2e6bbad8,
114421048bytes (+98864 from accepted). Both static kernel symbols present.
Accepted runner, isolatedR85/native1x/Metal/phase-only run26619:
3347VIframes/60s=55.7833FPS,p9919.84825ms,29gaps>=20ms,DMA29.7813333kHz.
Movie visibly completes; movement72734 changes Mario/camera; clean exit0,
fallback0/SMCfailed0/NANDa574...afa6 unchanged. Trigger5906once.

Whole379.8s75underruns/7backlogs are not fixed-window audio acceptance. Earlier
accepted54.5 is not a fresh paired control; R194host-recorder54.0167 also has a
different instrumentation policy. Next fresh accepted phase-only control before
gain/promotion decision. Candidate remains unselected, app unchanged. Evidence
generated/runtime/thp-kernels-r199/{measurement.json,phase.csv,runtime.log}.

## R199 — caller gates and actual-wrapper timing; candidate linking

Wholechunk caller continuation and changed-PC fault cases expand the oracle to
1440cases, including96returns into the original caller. All4reference/candidate
sanitized/optimized variants match digest882be09b1f38e9ad. Initial test stopped
on internalLR like an outside sentinel; corrected harness continuation rule.
No product defect inferred from that fixture failure.

Actual extracted-wrapper benchmark, ThinLTO both variants: ABBA26793.75/
24823.60/24719.30/25894.15ns totals. Means26343.95/24771.45, **5.97% lower time**.
The second control improves3.36%, but both candidate runs beat both controls.
Entire benchmark text131072->229376bytes (+96KiB). The wrapper reduces the
earlier kernel-only gain; no game FPS claim follows from either number.

One isolated game-module link now runs via build-chunk-entry-experiment.py
--thp-kernels,73103,generated/thp-kernels-r199-build.log. Same originalPGO and
1328unchanged objects, only chunk1102 replaced. Compiler reports1of33functions
has mismatched profile data that is ignored, retaining that performance risk.
Wait for this same link/audit before ready-title/isolatedR85movie validation.
Accepted app remains unchanged. Correctness log thp-kernels-r199-fixed.log,
timing thp-kernels-bench-r199.log. No runtime launched while linker is active.

## R198 — actual kernel chunk passes initial oracle

The source-pinned extraction now emits a private complete chunk with two
noinline+flatten kernels,584entry trampolines and preserved outer dispatch.
Kernel entry charges are not duplicated; early exits and guest returns remain
distinct. All864existing fullchunk oracle cases match under reference/candidate
sanitized and optimized builds,83114exit0. This actual wrapper shape has not yet
been benchmarked or linked into the game. Caller-return coverage remains next.
Final candidate SHA98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991,
generated/thp-kernels-r198-exits/candidate.c; test log generated/thp-kernels-r198-test.log.

## R197 — separate-TU ThinLTO retains transform gain

`--flatten-lto` keeps CPU/float/exception sources separate and applies ThinLTO to
both control and candidate. ABBA totals26997.55/24434.70/23704.95/26947.00ns
give10.76% lower candidate transform time. __TEXT98304->196608bytes (+96KiB).
All864cases under reference/candidate O1sanitized and O2 with ThinLTO agree with
the established digestaa72b761a9c075fd.68614benchmark/48937correctness both exit0;
generated/thp-flatten-lto-bench-r197.log and thp-flatten-lto-r197.log.

This removes the combined-source requirement, not the final-module PGO/layout
and instruction-cache risk. Next isolated extraction must preserve internal
goto versus external-entry cycle accounting and original caller return dispatch;
see THP-BOUNDARY-AUDIT.md. No game/module promotion yet.

## R196 — transform-local flattening, promising with a code-size cost

The `--flatten` experiment places actual CPU/float/exception sources in the same
translation unit for **both** control and candidate. Only the candidate's two
extracted transforms receive the flatten attribute. No math, availability,
memory, callback, journal or yield semantics are edited. Reference/candidate
O1ASanUBSan/O2 all864cases preserve digestaa72b761a9c075fd.

ABBA totals A28781.95/B25495.70/B25567.95/A28896.65ns across12means give mean
28839.30 versus25531.825: **11.47% lower transform execution time**. Entire
benchmark __TEXT rises81920->180224bytes (+98304,+120%). These are segment sizes,
not exact function sizes; __PAGEZERO in `size` output is not resident memory.

This same-TU result is not equivalent to the module's separate-TU PGO/ThinLTO
build. Next test whether function-local flattening works with that architecture,
before any isolated module integration. Do not paste cpu.c into a module chunk
and duplicate global state, or repeat the rejected blanket paired-load inlining.
Evidence generated/thp-flatten-r196.log (76534exit0), thp-flatten-bench-r196.log
(93793exit0). No app/module change or FPS claim.

## R195 — already-rounded operand shortcut parked

The temporary `--identity-c` candidate changes force_25bit_c only: low28bits zero
means the original mask/round operation is an identity, including the shifted
subnormal mask (whose discarded/round bits are a subset of those zero bits).
It retains the original operation otherwise; this is not finite-only arithmetic.
12,582,912 bit-pattern checks spanning all sign/exponent combinations and random,
guarded and single-bit fractions pass, including6,094,848 guarded identities.
The864case transform oracle also matches under reference/candidate O1sanitized/O2.

ABBA totals A29832.70/B30058.95/B29499.50/A29805.20ns across12means: average
29818.95 versus29779.225, only0.133% reduction. First candidate's first pattern
is conspicuously disturbed, but removing it selectively is not justified.
There is no robust aggregate gain; park without module link or promotion.
Logs generated/25bit-identity-r195-fixed.log, thp-identity-c-r195.log and
thp-identity-c-bench-r195.log. No app change. Stop standalone scalar-helper tweaks
as the next lane; they are not resolving the G6 shortfall.

## R194 — loaded movie is slow without paging

Accepted module494c...3fbe, same R85/native1x/Metal profile and trigger. Phase
measurement:3241VIframes in60s=54.0167FPS,p9920.416708ms,59gaps>=20ms,
DMA28.8405333kHz. Movie visibly completes into the attacked plaza; title/plaza
snapshots near60 are not substitutes for this fixed movie minute.

Added absolute CLOCK_MONOTONIC_RAW, monotonic and wall timestamps to the recorder.
The raw clock aligns with the runtime phase timestamps (the ordinary Python
monotonic epoch differs here).13overlapping5s host intervals cover the measured
minute, including edge intervals: zero swapins, swapouts, pageouts, compressions;
pressure command78–79%; swap allocation unchanged701.62MiB. Active paging is
therefore not the cause of this measured shortfall. This does not reproduce or
explain every historical22FPS episode, prove absence of thermal throttling, or
eliminate background contention. Reported game process CPU roughly109–113%, with
WindowServer/updater activity also present; no unrelated process was changed.

Runtime88867/trigger81216/recorder43772 all exit0. Fallback0/SMCfailed0, isolated
NANDa574...afa6 unchanged. Whole199.1s104underruns/5backlogs not audio acceptance.
Artifacts generated/runtime/host-correlation-r194/{phase.csv,host.jsonl,
measurement.json,correlation.json,runtime.log}. No app change; return to decoder
work rather than speculative paging fixes. No game/Simulator remains.

## R193 — host contention evidence boundary

Fresh no-game audit:16GiBRAM, swap701.62MiB allocated,8.0GiBfree disk. The new
read-only host recorder sampled for6seconds at3second intervals: zero swapins,
swapouts, pageouts and compressions; pressure command reported79% throughout.
File pageins79 then5 are not swapins. `pmset` had no recorded warning, which is
not a clock or thermal-throttling measurement. WindowServer and a Logitech
updater reported background CPU use; this does not attribute the old slowdown.
No unrelated process was terminated or priority/settings modified.

`scripts/record-host-pressure.py --seconds 90 --interval 5` emits private JSONL
with timestamps/raw output/deltas for correlation with the next accepted-game
phase trace. The queries themselves have some overhead; treat this as diagnostic
instrumentation, not an uninstrumented performance acceptance run. Parser test
passes; private idle proof generated/host-pressure-r193.jsonl. Next loaded-game
correlation is still required. Do not blame swap allocation or free-page count
alone for the user's22FPS observation.

## R192 — transform-only ABBA timing

`probe-thp-oracle.py --merge-fprf --benchmark` compiles strict O2 reference and
candidate and runs A/B/B/A. Each sample repeats each of12routine/pattern pairs
20,000times. Input initialization, RAM clearing and all oracle hashing are outside
the timed work; CPU reset, generated yield dispatch and output callbacks remain.
The workload reuses hot memory and has equal pattern weights, not measured movie
weights. It has no final-module PGO/ThinLTO layout or emulator host overhead.

Sum of the12mean ns/transform values: reference30031.95, candidate29036.65,
candidate28943.70, reference29899.30. Averaging by variant gives29965.625 versus
28990.175, **3.255% lower transform time**. This is not a game FPS estimate.
Evidence generated/thp-merge-bench-r192.log;77709FINISHED0. The small candidate
remains unpromoted, pending a broader-impact decision rather than another
expensive full link solely on this microbenchmark.

## R191 — candidate correctness, timing pending

An isolated 12-site deferred-FPRF extension crosses only exact register-only
paired merges in the two inverse transforms. Reference/candidate under sanitized
O1 and strict O2 match the full864case oracle digest. No speedup measured yet;
next offline matched timing without hash/setup overhead before any full link.
App/module remain unchanged. Evidence generated/thp-merge-fprf-r191.log.

## R190 — observable-state oracle coverage

864 cases now agree under sanitized O1 and strict O2, including paired-load
enable faults, changed quantization, write-journal preimages, reservation clears
and interrupted output. Evidence: generated/thp-oracle-r190-interrupt.log,
digestaa72b761a9c075fd. This closes the initial harness coverage step, not G6 or
a performance optimization. Next candidate must beat the existing transform
offline while matching the oracle before module linking and visible comparison.

## R189 — initial transform oracle green

Exact accepted generated transforms execute offline under O1 ASan/UBSan and O2
with identical state/memory/exit/callback digests across96cases,84timed yields,
48FPfaults. Zero-block pixel check passes. See THP-BOUNDARY-AUDIT.md for scope and
remaining oracle gaps. No faster candidate exists yet; no runtime performance
result or normal module change. Fixture LSQE omission was a test setup issue,
not evidence explaining the user's lag.

## R188 — larger decoder boundary, not another helper promotion

Read-only exact-input audit identifies two call-free inverse-DCT regions with
closed direct control flow and final LR return. See THP-BOUNDARY-AUDIT.md for
addresses, hashes, observable state and the next oracle test. Scanner now
includes signed conditional destinations and LR/CTR branches, not merely BL
counts. Actual-DOL assertions pass. This is a potential optimization boundary,
not a proven performance gain or semantic replacement. App unchanged; G6 open.

## R187 — fresh control limits entry-split benefit; park candidate

Accepted signedFPRFmodule14ea...f184/unchangedrunner, fresh chunk-control-r187 from exactR85profile; trigger57920once aftervisible restore, identical native1x/Metal/phase policy. Fixedminute3270frames=54.5FPS,p95=19.467167ms,p99=20.070333ms,38gaps>=20ms,DMA29.0986667kHz. R186candidate55.25 is only+1.376% over this freshcontrol, not the larger apparent historical53.6 delta. Insufficient evidence to promote extra code/entry/profile complexity. Parkcandidateaff3...a289 unselected; no unchanged third run or blanket entry-split rollout.

Movie visibly completes/plaza, runtime98930clean0/fallback0/SMCfailed0/NANDa574...afa6 unchanged. Whole299.8s105underruns/5backlogs not matched audioquality or fixedwindow counters. App remains accepted. Next investigate larger THP algorithm boundary using exactRMGE01 ABI/sideeffect/timing contract; do not turn speculative native replacement into an assumed legal/correct drop-in. No game/build/Simulator remains.

## R186 — first linked entry-split movie result

Same build1613 finishes0/module audit passes. Candidate aff3f3ec52d7e6cdb9f138fed2b056e77054b1340c5b7ad725cdee970da4a289,114404792bytes vs accepted114322184 (+82608bytes/.0723%). Original app remains selected. Accepted runner with explicit candidate, isolated chunk-entry-r185 exactR85slot/config/native1x/Metal/phase policy, trigger11390once after visible restore. Fixedminute3315VI/frame/presents=55.25Hz,framep95=19.103ms,p99=19.627375ms,17gaps>=20ms; DMA29.4954667kHz. Earlier FPRF53.6 is historical, not current pairedcontrol. Fresh accepted control required before attributing gain.

Movie visibly completes into plaza; move81147 changes Mario/camera; runtime54348 clean0/fallback0/SMCfailed0/NANDa574...afa6 unchanged. Whole282.7s93underruns/10backlogs includes startup/restore/gameplay, not audio acceptance or fixedwindow counters. No build/profiler/secondgame/Simulator overlapped measurement. Next matched accepted control, not promotion. Artifacts generated/runtime/chunk-entry-r185/{runtime.log,phase.csv}; no live runtime/build/Simulator.

## R184 — optimized/journal/reservation parity and isolated link

Extended whole-chunk harness to8modes x4trials x1024entries=32768cases. Ordered callback records include reservation address/valid bit; write journal is active in half modes and may mutate GPR/XER/exception state just like other callbacks. Both O2/ThinLTO82961 and O1ASanUBSan83417 exit0: capped0,170262journal callbacks and283reservation clears each. Actual full CPUState/memory/callback ordering agree. Logs chunk-entry-r184-{optimized,sanitized}.log. No hardware/gameplay proof implied.

build-chunk-entry-experiment.py pins accepted module494c...3fbe, candidate sourced248002b3b8021c79cd6b2c4ea1d15f015dd0b447b31fe060d54354dd45fe32b, originalchunke6aa...6dcc and originalPGOf39a...60d. Reads actual Ninja flags/object graph, hashes1329objects, substitutes1/reuses1328, preserves strictFP/O2/ThinLTO. Provenance+experimentalmanifest in generated/chunk-entry-r184, no selection. Build1613 ACTIVE (chunk-entry-r184-build.log), poll same; next link audit/size and bounded real-game comparison. Do not ignore changed CFG/missing-profile penalty; this is one isolated candidate, not an accepted optimization. App unchanged/no runtime/Simulator.

## R183 — whole-chunk differential execution

tests/test-chunk-entry.py compiles private reference/candidate as separate renamed TUs with actual CPU/memory headers and ASanUBSan O1.16384 cases cover all1024instruction entries under4modes/4trials: random and directRAM-seeded registers, downcount0/-257, callback reads/writes with ordered pre-callback PC/GPR/CR/XER/downcount/value snapshots, optional GPR/XER/exception-field mutation every7callbacks. Compares fullCPUState, memory bytes, callback sequence and cap status. Fixed run85607 exits0/capped0, generated/chunk-entry-r183-fixed-test.log. This is synthetic memory/CPU input, not game-state or hardware exception acceptance; write-journal/reservation-active and optimized/LTO execution remain untested.

Initial76847 failed in unchanged reference get_ram_ptr on RAMnull/size0: unsigned size subtraction allowed a bogus direct address. Harness now obeys initialized MEM1 precondition with4096byteRAM in every mode. No runtime patch or claim that this causes gameplay lag. Failedlog retained. Candidate remains isolated; R182 missing-profile/static-code-size penalty still applies. Next optimized/journal/reservation tests before bounded one-chunk link and real gameplay comparison; no app/module selection change or game/Simulator remains.

## R182 — complete-chunk structural assembly probe

scripts/probe-chunk-entry.py reads SHA-pinned accepted1103/generated header and actual build.ninja flags. Private candidate retains whole original function as noinline entry_suffix_804530A0; normal public copy retains195 no-suffix-charge entry cases, routes829 others to fallback. All1024 entries represented; fallback body and normal code after initial dispatch byte-assert unchanged, shared15loop helpers unchanged. This is source-preservation evidence, not execution/callback/loop proof. Outputs generated/chunk-entry-r182/{reference,candidate}.c/.s; no source overlay or module selection change.

Actual flags except -flto (removed to emit native assembly instead of IR), originalPGO: reference12233 static instructions/1441loads/790stores; normal17934/3772/1422 plus fallback21512/5168/2376. Compiler says no candidate profile. One changed-variable control --no-profile: reference22098/5302/2440, normal17987/3775/1442 plus fallback21562/5177/2384. Normal18.6% fewer staticinstructions/28.8%fewerloads/40.9%fewerstores, combined39549instructions vs22098 (+79%). These are static code counts including alternate paths, not dynamic execution or linked size. Profile/layout influence is substantial; no game-speed prediction or promotion.

Next whole-chunk differential execution across all1024entries and callback/loop/return/PC/downcount cases before any isolated module link. Retain oldprofile rejection knowledge: changing CFG invalidates its coverage; do not silently describe missing profile as equivalent optimization. This prototype may be rejected on linked-size/runtime cost even if normal path is simpler. No game/runtime/Simulator remains.

## R181 — isolated multi-entry register-propagation probe

tests/probe-block-entry.py extracts real chunk1103 SHAe6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc, block80453AAC–AB8 (cntlzw/subfic/cmp/branch) and actual four external cases. Reference uses original labels/suffix charge; candidate routes leader to label-free noinline normal helper and other PCs to original reference.400000 randomized fullCPUState/output-branch/cycle comparisons pass ASanUBSan across all entries, negative/positive downcount and leading-zero specials. First expected-charge assertion failed due unsigned test subtraction, fixed signed cast; not a runtime defect. This block has no memory callback or exception path, so those remain untested here.

O2 isolated assembly in generated/block-entry-r181.log: static reference65instructions/13loads/8stores; normal37/5/5; routing6/1/0. These count ALL alternate-entry code, not dynamic normal-path work or game speed. Reference normal path reloads gpr12 before cmp; normal helper retains it in w8. New routing adds a compare/branch/tailcall. No claim that small isolated probe predicts whole-chunk benefit, especially with real PGO/ThinLTO/layout. Next complete hot-chunk entry-route experiment must retain every external PC, suffix cycle charge, original internal CFG, callbacks/exceptions and full state, then inspect real code size and assembly before another module build. No product generator/module change.

## R180 — bounded range accounting and structural next hypothesis

Offline summarize-cpu-profile.py resolves XML id/ref chains, reports only CPU-thread leaf samples/cycles/cores/raw module PCs, and optionally matches disassembly-defined half-open aligned ranges. Synthetic tests prove references, excluded non-CPU thread, no inclusive parent double-counting, zero weights, boundary matching and empty export refusal; added to suite, fullsuite not rerun. Outputs in movie-instructions-r179/summary-r180.json and decoder-r180.json retain source trace.

Selected paired-store body1886 samples (vs1910 symbol aggregate containing other copies): entry322; first conversion0/address565/bookkeeping178; second conversion107/address310/bookkeeping233; epilogue171. Address regions875/31081=2.815%. Specific decoder CLZ cascade827/31081=2.661%, following flags91 and branch152. These are sampled-PC regions, not causal cost boundaries; skid can attribute preceding work to a subsequent load and zero samples do not prove zero cost. No basis for another unchanged CLZ/type0RAM-pair experiment.

Structural hypothesis from actual generated chunk1103 and binary: every guest instruction has an external switch predecessor, even straight-line arithmetic; joins can inhibit register-state propagation. Hot80453AAC–AB8 contains cntlzw/subfic/cmp and repeated CPUState loads/stores in native assembly. Investigate separating normal full-block execution from interior-entry suffixes in an isolated emitted-code test. Preserve every external entry and precise cycle accounting (including accepted midblock fix), full register/flag state, callbacks, exceptions, branch/loop semantics. First establish assembly/code-size benefit and differential correctness; no product emitter/module changes justified yet.

## R179 — instruction samples and core/thermal evidence

Local sample help/man cannot recover collapsed offsets. xctrace CPU Profiler 3s launched-sleep preflight records/export succeeds (record exit54 reflects launched-process SIGKILL at time limit, not permission refusal). Actual 10s attach to game PID44844 exits0, generated/runtime/movie-instructions-r179/cpu.trace. Exports cpu.xml/thermal.xml succeed. No privilege changes or all-process capture. Same exact package/R85scene/one trigger80136; movie visibly advancing, runtime6707 clean0/fallback0/SMCfailed0/NANDa574...afa6 unchanged.162.8s whole diagnostic79underruns/3backlogs; no performance acceptance.

CPU-thread31081 raw samples; P-core31054/E-core27, >99.9% sampled activity on performance cores. Thermal table reports Fair for full10.875094890s capture, not induced. This rules against efficiency-core residency dominating THIS run; it does not explain historical22FPS episodes or measure actual clocks/throttling. CPU summed cycle weight29902144243 (first row0). Exclusive frame counts:804530A0=5031,804520A0=3618,psq_store_inline1910,psq_load_inline1330,ps_add1305,convert1238,ps_sub1187,psq_store1164,ps_madd979,804540A0=872,Run786,ni_madd_msub767,HookExternalPointer749,TryGetLockedCachePair714,deferred_sub649. Resolve XML id/ref entries before aggregating; top-of-backtrace only, not inclusive stack sums.

Module loadbase0x134a70000, UUID4229EFF0-9703-3CC6-825B-808A3DFE882F. Raw leaf offsets include low bit: paired-store0x578966d320samples and0x5789601=265; decode aligned0x578966c/0x5789600 as MEM2-pointer/GQR loads. Decoder0x579cf3d274/0x579cfd5272. Do not confuse these with previously sampled epilogue offsets or assert sampled loads themselves cause all preceding pipeline stalls. Next aggregate hot instruction ranges/cycle weights to distinguish guard/flag/register traffic, preserving prior rejected CLZ/RAM-pair/PGO/inlining decisions. No app mutation or runtime/Simulator remains.

## R178 — fresh post-FPRF CPU attribution

Exact promoted signedmodule14ea...f184/runneraffb...e295, isolated movie-profile-r178 copied R85Config/Wii/slot3; verified slotaea2...7ab8 and NANDa574...afa6. Ready title and restored scene inspected; trigger30876 once. Untraced runtime57312, 10s sample20989 on PID44316 during visibly advancing movie. All exit0; native fallback0/SMCfailed0/NAND unchanged. Closed during movie after useful sample, no movie-completion claim. Whole145.2s81underruns/4backlogs diagnostic-only.

CPU-thread7509 samples, exclusive tree subtraction totals7509 with no negative residuals. Inclusive Run7283, dispatch6921. Exclusive leaves: func804530A0=1128,804520A0=896,psq_store_inline443,psq_load_inline334,convert_to_double332,psq_store302,ps_add293,ps_sub292,804540A0=202,ps_madd202,Run196,TryGetLockedCachePair186,ni_madd_msub175,HookExternalPointer171,ni_add169,ps_mul151,deferred_sub147,dispatch124,deferred_madd123,deferred_add114,ni_sub113,psq_load91,psynch_cvwait77,OnICacheInvalidate59. Do not compare raw counts to different-duration/sample-count historical profiles as gains.

Signed module loadbase0x133f04000. 804530A0+79220 address0x1396a0f3c maps binary0x579cf3c: store after CNTLZW compare cascade, then carry/CR handling and guarded byte lookup/halfword store. Matches previously investigated coefficient region (PERF R81/R83 notes); intrinsic CLZ and decoder PGO were already rejected, so do not repeat unchanged experiments. Current collapsed symbol entry aggregates offsets and cannot weight the first printed PC independently. Next bounded raw-address sample/histogram needed before deciding whether integer/flag/register traffic or guarded memory dominates this chunk. Artifact generated/runtime/movie-profile-r178/cpu-sample.txt; app untouched, no runtime/Simulator remains.

## R177 — packaged optimization smoke

Package64332 and audit72877 exit0. Signed runner affbcb51f27f853b0b5ee403b5033c3bd5a6f7ea3e514b969c2ef4272af9e295 unchanged; signed module14ea8867e2b0a47caf761b2ba24ff608cd39a27b1e9290dbc2302f6d4651f184 matches canonical source after signing. Previous app retained at generated/macos/GalaxyPad.app.previous.20260906T232128Z. Untraced packaged-wrapper37922 loads actual one-star Observatory (53317), pause/resume and movement45847 visibly work, shutdown0/fallback0/smc_failed0/NAND5040...64a6 unchanged. Evidence: generated/runtime/fprf-canonical-r175/runtime.log and current CUA captures. Whole156.4s8585frames,9underruns/8backlogs includes deliberate12.5s pause and startup; not a matched-window FPS/audio pass. No runtime/Simulator remains. Next fresh CPU diagnostic for remaining heavy-movie hotspots after optimization, not another unchanged timing pair; preserve all FP/timing/EFB semantics. Current RMGK01 Petari symbols cannot be treated as exact RMGE01 mapping.

## R176 — canonical binary reproduction

Full source build2122 exits0. Canonical module SHA494c2a71d16963cf720af228ff8b9323a1d5b2967776cb759aa11f161beb3fbe matches R169/R171 experiment byte for byte, not merely source similarity. Audit passes ARM64/macOS14/1322chunks/19SMC. Manifest source fingerprint28d765f74af57637 and fprf_policy=rmge01-fprf-119-v1 identify new canonical cache27fc425ac63117e7 with originalPGO. Existing exact-binary gameplay/save evidence applies with unchanged accepted runner; another explicit-module smoke would be redundant, but new packaged runner/wrapper requires smoke. No new FPS measurement or stability claim. Normal cache selection82587 and fullsuite36660 started; package unchanged. Private experiment comparison tests anchored to SHA-checked historical source, both pass (64800 exact-chain comparisons). No runtime/Simulator;9.4Gi free observed.

## R175 — identity correction and canonical validation preparation

Source fingerprint is a cache-key/manifest field, not embedded in StaticRecompModuleDesc. Inspected module_export.c and audit-module.sh: binary audit checks game/ABI/entry/chunk/SMC tables, while build provenance and final binary SHA connect sources to artifact. Earlier embedded-fingerprint wording corrected; do not imply an ABI guarantee that does not exist. Canonical transformedchunkSHAf2d6911016e8e1c9f46caf5ee97dece58689f5b5f51397860bb868383c34bd61. Fresh fprf-canonical-r175 one-star profile/Pipe prepared, NAND verified, no runtime yet; same2122 compilation continues.

## R171 — untraced real-save/lifecycle compatibility

Exact candidate494c...3fbe plus accepted runner, fresh fprf-save-r171 copied one-star NAND, no savestate and no phase trace. Fixture84490 selects file/Play and visibly reaches Observatory with one star. Native pause indication appears, resume clears and animation advances, right80933 visibly changes position/camera. Close4989 exit0/fallback0/SMCfailed0, NAND5040...64a6 unchanged. Whole181.4s10underruns/10backlogs includes intentional21.37s pause (not freeze); not timing/audio acceptance. This verifies save-load/pause/input continuity, not a new save write or full G5 pointer-target matrix.

Integration boundary: experimental manifest records the baseline source fingerprint, so copying it into the normal old cache is invalid. Canonical preparation must carry exact DOL/backend/chunk/source guards for119sites, runtime source additions in the source collector, and explicit policy identity in cache/manifest. Preserve tested helper bodies and scope, then regenerate/rebuild/audit and smoke the resulting canonical artifact before normal packaging.

## R170 — reverse control supports incremental FPRF gain

Fresh fprf-control-r170 with accepted signedmodule5f810...097c/runneraffb...9e295, identical R85slot3/native1x/Metal/phase trigger85181once. Fixed minute3101frames=51.683333FPS, framep95 20.426125ms/p99 20.864417ms,696gaps>=20ms, DMA27.5904kHz. Bracketing sequence accepted51.5→candidate53.6→accepted51.6833 supports~3.7–4.1%incremental gain, not a precise hardware-independent causal estimate. Higher56.9snapshot does not replace complete-window evidence. Stop unchanged timing repeats; proceed bounded G5/lifecycle/save checks and canonical integration if they pass.

Movie visibly completes/plaza; nativeclose91740 exit0/fallback0/SMCfailed0/NANDa574...afa6 unchanged. Whole234s152underruns/4backlogs is not audio acceptance. No compiler/profiler/extra launcher/Simulator overlap. powermetrics read after fixed window refused non-root invocation; no privileged retry. Post-build heat remains possible confounder, not established explanation; do not blame machine or reverse previous failed-candidate decisions without new evidence. Candidate still unselected; stable60Hz/audio remains open.

## R169 — deferred-FPRF candidate first gameplay measurement

Build67896 exit0, module audit passes1322chunks/19SMC/arm64macOS14. SHA494c2a71d16963cf720af228ff8b9323a1d5b2967776cb759aa11f161beb3fbe,114322184bytes versus accepted114321880 (+304). Disassembly fprf-r169-decoder.asm has exactly119calls to deferred helpers; helper assembly retained separately. Original ni_* arithmetic remains, deferred helpers have different inlining choices; only real workload decides benefit.

Fresh fprf-r168 profile, accepted runner/native1x/Metal/phase policy, title ready before CUA binding (no extra launcher), visible R85restore and trigger87012 once. Complete fixed60s:3216frames/53.6FPS; framep95 19.78425ms/p99 20.540417ms,83gaps>=20ms; DMA28.6144kHz. Recent acceptedR16351.5FPS/~22.205ms/27.4944kHz gives~4.08%cadence improvement, but no reverse-order confirmation yet. Candidate remains unselected.

Movie visibly completes to plaza59.9; right input29759 changes Mario/camera position, snapshot60.0. Native close42140 exit0/fallback0/SMCfailed0/NANDa574...afa6 unchanged. Whole234s121underruns/12backlogs includes title/loading/movie/plaza/movement and is not comparable audio totals against shorter control; audio/60Hz remains unmet. Next accepted reverse control before deciding integration; no game/build/Simulator left running.

## R168 — exact candidate chains verified while link runs

test-fprf-candidate-sources.py reads actual prepared fprf-r167 artifacts. Reversing only119helper-call renames plus declared include/prototypes restores original chunk byte-for-byte; new float is original prefix plus exactly4expected flag-deferred helper bodies. Extracts all43maximal modified decoder chains and executes162suffixes with actual register assignments.64800 comparisons pass complete CPUState+hostFPflags under ASanUBSan across4rounding modes/special+random operands/lazy-FP+MSR states. Tests do not benchmark while linker is active. Build67896 still running at latest poll; no artifact speed result. Prepared fprf-r168 profile/NAND/state unchanged for eventual movie test.

## R166 — execute emitted suffix/exception/observer paths

tests/test-fprf-emitted.py compiles actual current emitter/CFG/decoder, emits NOP→PS_ADD→PS_SUB→PS_MUL→MFFS, applies isolated deferral only at whitelist-approved first two writers, and executes reference/candidate against actual GXRuntime arithmetic/availability/exception code.80000 comparisons across5external entries/4rounding/lazy-FP+MSRFP combinations/positive and negative downcount pass ASan+UBSan. Full state includes PC/SRR/exception/FPRF/MFFSresult/cycles; host FP flags agree. Disabled FP independently asserts unavailable exception/SRR0; successful paths assert endPC and bit-exact MFFS observation. Boundary/256kchain tests also pass, session66811 exit0.

Hot804520A0 has224 supported arithmetic calls,119 static eligible writes (~53%). This does not measure dynamic coverage or speed. Next isolated single-hot-chunk candidate should preserve all other generated chunks and baseline arithmetic, append separate deferred helpers (no cold outlining/classification shortcut), and reuse unchanged accepted object files where possible. Audit compilation/link flags and hashes before real workload. Normal module selection must remain untouched. No performance promotion from these tests.

## R165 — conservative emitted-region coverage

Read-only scripts/audit-fprf-regions.py accepts only adjacent primary-function labels with PC materialization, exact non-recording add/sub/mul/madd-family annotation, availability check and arithmetic call, no other statement.283 first-writer sites across69chunks;119 in hot804520A0,37 in804220A0. These are static sites, not dynamic counts or predicted frame-rate gain. tests/test-fprf-regions.py rejects Rc, FPSCR reader/update, memory/callback, exception return, return/goto, leader charge, outlined loop, MSR write, fallback, unknown helper, address mismatch and cross-function text. Outlined loops excluded.

Availability check tests g_ppc_lazy_fp_enabled/MSR[FP]; unavailable slow path takes exception and returns false. Existing arithmetic helpers update floating-point state, not MSR/lazy enable; no new exception delivery may be elided. Still require emitted-code execution tests for external suffix entry, unavailable FP, cycle counts and observer boundaries. Current audit is not a production transformation and does not prove safety under unsupported asynchronous observation/debug stepping. No build or gameplay claim.

## R164 — tracing audit and guest-state dataflow boundary

R153 CPU profile was already untraced, so tracing cannot explain its dominant native guest-execution cost. R162 later traced sample shows22/7412 CPU-thread samples in RecordPhase (~0.30%); not an upper bound on overhead/transient stalls across the earlier fixed minute, but no evidence justifies a tracing-only rebuild. Keep phase tracing diagnostic-only.

Investigate generated guest-state traffic rather than another common-path arithmetic shortcut: paired add/sub/mul/madd always classify and write FPRF even when a consecutive arithmetic operation overwrites those bits before any observer. New isolated test-ps-fprf-chain.py extracts actual helpers, omits ONLY first writer's classification, retains second unchanged.256000 chains cover all16operation pairs,4rounding modes, random/special operands/FPSCR, destination/source aliases, madd variants. UBSan passes full final CPUState and host flags; intermediate state differs only in FPRF,248110cases actually differ. No microbenchmark or game-speed claim.

Exact generated example:804527E8 ps_add followed804527EC ps_sub, then804527F0 psq_stu. The store is an observation/exception barrier; never defer across it. Emitter currently emits FP-availability checks and Rc handling individually. Before any implementation, require negative tests for Rc/FPSCR readers, memory callbacks, host exits, exception paths, CFG/chunk boundaries and entry suffixes. Availability/MSR invariance across a proposed pair must be proven; do not remove exception behavior or intermediate state that an observer can see. No runtime/generated source mutation yet.

## R163 — fresh accepted control and observer-cost boundary

Accepted signed module5f810...097c/runneraffb...9e295, fresh R85profile accepted-r163, same native1x/Metal/phase policy/slot3/trigger93056 once. Complete fixed minute51.5FPS (3090frames), framep95 20.566ms/p99 22.205ms, DMA27.4944kHz. Reproduces old accepted51.72 closely; candidate30FPS is not evidence of a fixed machine ceiling. Reject candidate for promotion, without claiming exact causal regression from single-order runs with host variation. Current accepted still fails60Hz/audio.

Host-top.txt samples every10s through window: runner~116%, kernel~48–53%, Logitech~29%, no swap delta; Low Power Mode0 and pmset no recorded warning. These do not establish actual core residency/frequency or exclude transient throttling. No profiler/build/extra launcher. Visible checkpoint and advancing movie, not whole movie completion; native close46172 exit0/fallback0/SMCfailed0/NAND unchanged. Whole176s152underruns/3backlogs not matched audio totals against candidate.

Broader diagnostic finding: Common/GalaxyPadDiagnostics.h opens phase CSV line-buffered and serializes fprintf under shared mutex across producers. Previously both paired comparisons shared it, but current bottleneck analysis must quantify observer overhead rather than assume negligible. Next use existing untraced telemetry or bounded in-memory/sampled measurement; preserve cadence/guest state. CPU thread source lacks explicit QoS; SunPad reference uses QoS only in default-off experiments. No priority or emulated-clock change is justified yet. Runtime hardcodes StaticRecomp, so a JIT reference would require an explicit diagnostic build and is not the mobile solution.

## R162 — cold-exception candidate fails real workload; broaden diagnosis

Candidate54ac7e20...40a2d builds/audits successfully and preserves focused semantics; linked add/sub shrink to127instructions each but entire module grows0.98%. Fixed attack minute in cold-fp-r161/phase.csv:30.0FPS, framep95 68.867ms/p99 84.991ms, DMA16.0149kHz. User separately observes22FPS. Old accepted51.72FPS is not a contemporaneous control; no causal attribution/promotion from this comparison. Startup CUA auto-opened unused frontend; closed before checkpoint/trigger, no extra game. Native1x/accepted runner, trigger63277 once, sample taken AFTER measured window. Movie advances visibly but not completed; close15389 exit0, fallback0/SMCfailed0, NANDa574...afa6 unchanged. Whole238.7s423underruns/6backlogs.

Later10s slow-sample.txt: CPU7412samples,6985 under Run/6719dispatch; video6743 condition waits. This still favors guest-execution/CPU-side deficit over GPU saturation, but sample is later than fixed window. pmset no recorded thermal/performance warning does not exclude throttling. Two-snapshot top:runner67.4%,kernel43%,Logitech25.7%,no swap delta; cumulative disk/page-in counters are not current pressure evidence. No compiler/game overlap. Next fresh accepted-artifact control with host scheduling/thermal observations and broader AOT/decoder cost analysis. CPU thread source entry currently has no explicit QoS; investigate actual scheduling before any policy change. No more micro-only performance promotions.

## R150–R151 — correctness packaging, performance still open

G5 pointer/file1 and native pause/resume pass visibly, clean exit/native fallback0/SMCfailure0/NAND unchanged. Whole260.1s3underruns/4backlogs includes deliberate39.4s pause; not a freeze or cadence comparison. Normal cache selection and full suite pass, package46291 exit0 and signature/app audits pass. Corrected signed module5f810ae0ed1f056c7ea8b2256d124405b0b05c6a68f4fd9d7c35fda3068d097c packaged with unchanged runneraffbcb51...9e295. Prior app retained20260906T194009Z. This promotes cycle correctness only; movie51.72FPS/audio failures remain. Next wrapper smoke then concrete remaining THP-cost investigation, not another unchanged timing comparison.

## R149 — corrected-cycle movie measurement

Candidate9098890e...cc9de with accepted runner, identical R85slot3/trigger/native1x/dualcore/phase policy. Fixed minute51.716667FPS, frame p95/p99 20.432708/20.930459ms, DMA27.6096kHz. Prior pair-enabled51.867–52.000 gives no material speed gain; noncontemporaneous comparison is not precise regression attribution. Correction still fixes proven undercharge, not the movie bottleneck. Movie visibly completes to plaza59.9; close24464 exit0/fallback0/smc_failed0, unchanged NANDa5743199...afa6. Whole223.05s155underruns/4backlogs; audio remains unmet. No debugger/build/extra launcher/Simulator overlap. Candidate unpromoted pending G5/lifecycle checks. Private midblock-movie-r149.log and phase.csv.

## R148 — candidate build and real-save smoke

Build87320 exit0, module audit ARM64/macOS14/1322chunks/19SMC passes; module SHA9098890e25b36e802ab5f793c9ad7800f991190f41e972996937343d84ecc9de. Accepted runner plus explicit candidate module, prepared midblock-r145 real-save profile. Title59.9, Observatory59.1, visible movement59.6 snapshots. Close53653 exit0, fallback0/smc_failed0, real-save hash unchanged. Whole97.4s43underruns/10backlogs and5691frames/97.074s include title/loading; not matched throughput/audio acceptance. Extra CUA-opened frontend closed without starting a game; do not treat startup as uncontended measurement. Next representative heavy-scene timing and G5/lifecycle checks before package selection. Candidate still unpromoted, G6 open.

## R144 — cycle fix integrated, candidate compiling

Pinned bootstrap now applies external-entry suffix accounting. Focused ASan/UBSan tests include local returns and embedded data, with10k original/candidate CFG comparisons. Full repository suite passes. Actual generated save-helper probe now extracts its real switch cases: accepted module interior80517538 charges0, newly generated candidate charges4 for3stores+blr. Prior hardcoded probe switch was sufficient to reproduce original behavior but could not validate the switch-based fix; corrected before candidate evaluation. Generator SHA e569b97d1dabf68d15099ea025be1c0d6b96bcbabbf50b61d6325e83962668aa, separate candidate cache da63c951ce4d7349, originalPGO. Build87320 still compiling; no runtime/performance result or package promotion.

## R142 — interior-entry cycle accounting defect

Parked SMC bounds experiment: entire OnICacheInvalidate leaf74/7298 (~1.01%) limits sample-based upside, shortcut affects only part. Actual generated save helper exposes a more important issue: external dispatch80517538 skips leader805174fc's charge, executes3stores+blr with zero generated cycles (host forces1), whereas full18store+blr path charges19. Compiled actual-snippet probe reproduces with UBSan; R140 confirms this interior entry is used. Correct external-entry suffix accounting must avoid double-charging internal fallthrough. No performance claim; package unchanged pending tested emitter fix.

## R139 — dispatch-loop source attribution

Run leaf samples751/7298CPU thread (~10.3%). Signed symbol base100238748: sampled+988 maps sampling flag load, +1224 idle-PC load; collapsed offset lists do not provide per-instruction counts. Actual timebase division uses multiply-high/shift, not expensive variable divide. Native-dispatch count is consumed by lockstep start/limit and trace/sample cadence, so it cannot simply be removed as telemetry. Generated805170A0 is an address-range switch, not one semantic function. Next existing dispatch-PC sampling to locate frequent entries, cross-check against CPU cost; no speculative patch from aggregate counts alone.

## R138 — promoted-package Observatory diagnostic

Real one-star save loaded from ready title once, R64-derived dualcore/native1x profile. Visible60.3→58.9 snapshots,10s sample:6174/7298 CPU-thread samples under StaticRecomp Run,5442 under dispatch,199 float-future wait samples inside dispatch. CPU execution remains the main sampled subtree, not proof all time there is compute. Footprint732.6M/peak1.8G. Whole192.5s88underruns/18backlogs,24388depth peeks,6transitions,clean native-only exit/NAND unchanged. Sampled diagnostic not matched throughput/soak acceptance; current depth activity differs from historical zero-peek Observatory runs. Private observatory-r138.log and observatory-r138/cpu-sample.txt. Next inspect hot leaves/chunk structure while preserving readback semantics.

## R136–R137 — paired-store normal-package promotion

Normal build reproduces measured unsigned modulee8da217b...82d00 and runner6dde0e4...9ed6 byte-for-byte. Source-aware normal cache44290ae60c4cad14 selected via verified cache hit, manifest fingerprintcabf2f59c72309c2. Package audit/signature/full suite pass; signed runneraffbcb51...9e295/module315d08db...d63b0 identical to tested candidate. Wrapper enables pair1 alongside byte1 and preserves explicit0. Original package retained with timestamp20260906T183531Z.

Fresh normal-wrapper smoke without env overrides restores R85 and visibly moves Mario, clean native-only exit, unchanged NAND.124.9s4underruns/6backlogs is not audio acceptance. No new movie timing claim beyond R123–R128's two-order~11.5%gain. Optimization promoted; remaining~52FPS movie and broader G6/audio deficits open. Next remaining gameplay profiling, not repeated pair comparisons.

## R128 — paired-store confirmation and integration decision

Reverse-order OFF fixed minute46.600FPS/frame p99 23.111875ms/DMA24.881067kHz; prior ON52.000/20.703125/27.7632. Gain11.59%, agreeing with first OFF46.5667→ON51.8667 (+11.38%). Same signed candidate/checkpoint/fixture/trace policy; no debugger/build. Wall-time rather than exact guest-frame alignment and host variability still limit precision, but both orders agree materially.

Movie completes, close0/native-only,NAND unchanged. Whole246.9s280underruns/4backlogs not audio acceptance. Private pair-confirm-off-r128.log and pair-confirm-off-r128/phase.csv. Accept for incremental integration; not yet normal-app selection and not G6/60Hz/audio closure. No more unchanged timing repetitions. Normal bootstrap/cache/package integration and audits are next.

## R127 — reverse-order confirmation ON half

Same candidate/R85/fixture/phase policy with pair1, no debugger/build. Complete fixed minute52.000VI/frameHz, frame p95/p99 20.302292/20.703125ms, present52.0167Hz (one boundary event), DMA27.7632kHz. Prior ON51.867 is similar; OFF half pending, no final causal confirmation yet. Movie visibly completes into plaza; native close0/fallback0/smc_failed0, unchanged NAND. Whole229.3s155underruns/3backlogs not acceptance. Private pair-confirm-on-r127.log and pair-confirm-on-r127/phase.csv. Candidate remains unselected.

## R126 — candidate G5 pointer regression

Normal boot of pair candidate1/byte1, R72-derived profile with no states/tracing/debugger. Ready title inspected before existing G5 fixture once; pointer highlights Mario file1 at59.9–60.0FPS. Clean exit0/native-only, NAND unchanged.12195frames/203.525490625s (~59.92Hz),50932DMAblocks/203.824798750s (~31.98kHz),1underrun/2backlogs,zero audio backend errors,24018depth reads,4button transitions. Private g5-pair-r126.log. Bounded title/file-select regression passes; no zero-starvation/audio-quality claim or direct unequal-duration underrun comparison. Next reverse-order attack confirmation before selection.

## R125 — uninstrumented candidate gameplay continuation

Pair-Candidate-r121 explicitpair1/byte1, fresh R85 profile, no phase tracing/debugger/build. Exact trigger once, visible movie completes, one-second right fixture changes Mario and camera position in plaza. Snapshots50.6movie/60.0plaza/58.2moved view are not a sustained rate. Native close0/fallback0/smc_failed0, unchanged NAND. Whole219.3s141underruns/4backlogs; audio remains unsatisfied. Private pair-untraced-r125.log. Candidate remains unselected pending G5 regression and bounded confirmation.

## R123–R124 — paired-store first matched comparison

Same signed Pair-Candidate-r121.app, original R85 slot3 in independent R118 profiles, exact trigger once, byte fast1, pair0 then1. No debugger/compiler overlap. Analyzer uses first nonzero input+20s through+80s, both complete. OFF46.5667FPS/24.861867kHz DMA/frame p99 23.214125ms; ON51.8667FPS/27.6864kHz/frame p99 21.058750ms. Observed throughput gain11.38%. Windows align wall time rather than exact guest frames; host variability still applies.

Both visibly advance movie and return to plaza, native close0, fallback0/smc_failed0, unchanged NAND a5743199ed343b04d2d02069881d8754310194ed2b3012f4ec54152272a2afa6. OFF283underruns/6backlogs over296.7s, ON152/3 over187.6s are unequal whole-run totals, not audio acceptance. Private pair-off-r123.log/pair-on-r124.log and pair-off-r118/phase.csv/pair-on-r118/phase.csv. Candidate remains unselected; next uninstrumented movement/G5 regressions and bounded confirmation. Below60Hz, G6 still open.

## R122 — integrated paired-store activation proven

Signed Pair-Candidate-r121.app opt-in1 with pair-activation-r118, no phase trace. R85state3 visibly restored and exact trigger80389 exits0. LLDB batch attach to PID99616, breakpoint on PowerPC::MMU::TryGetLockedCachePair(unsigned int), continue, thread step-out, register read x0, bt4, process detach. Session53292 exits0. Nonnull x0=0x12047c020 at ppc_psq_store+152 (cbz return guard); caller func_804520A0+51244, then chassis_dispatch/StaticRecompCore::Run. This confirms successful acquisition, not just method entry. Private pair-activation-r122-lldb.log.

Movie visibly resumes after detach; native close55420 exits0. Private pair-activation-r122.log, disposable NAND unchanged. Debugger run and title-bar samples excluded from performance acceptance. Next identical candidate binaries with opt-in0/1 and prepared R118 profiles, same phase window, no profiler/debugger. Accepted app remains unchanged.

## R121 — paired-store candidate linked and packaged privately

Original module4915 exits0; module audit passes. Unsigned SHAe8da217b3594c69a0b02546964e07feeef0fab49a0fb369bce3c6d2a88982d00. Copied accepted app to ignored generated/runtime/Pair-Candidate-r121.app, replaced only runner/module, ad-hoc signed and deep/strict verified. Resource trees identical. Signed runneraffbcb51f27f853b0b5ee403b5033c3bd5a6f7ea3e514b969c2ef4272af9e295; signed module315d08dbe765d55aeaedf3dd55738c0e7b6a7720a5e863c2692dbdffdaed63b0. Descriptor RMGE01 ABI3/CPU3528/1322chunks/19SMC. Accepted packaged hashes reverified unchanged.

No runtime launch yet. Next explicit GALAXYPAD_LC_PAIR_FAST=1 using pair-activation-r118, successful nonnull pointer proof required, not just entry symbol hit. Any debugger/profile diagnostic kept separate from same-binary opt-in0/1 phase comparisons using pair-off-r118/pair-on-r118. No performance or stability claim from packaging.

## R115 — host capability guard prototype tested

Unapplied lc-pair-host.inc inserted into actual HookExternalPointer only in test compilation. Size0 request requires exact GALAXYPAD_LC_PAIR_FAST=1 and disables when exact pixel-store tracing is enabled, preserving diagnostic observability. Rejects non-E address, lockstep journaling, unsynchronized MSR without propagating it, and relocation of either byte. Successful request delegates to R113 MMU eligibility. Legacy positive-size body remains untouched.

test-lc-pair-host.py compiles actual callback plus snippet under ASan/UBSan with host stubs, checks unset/0/true/10 rejection, exact1 enable, diagnostic exclusion, side-effect-free MSR/journal/relocation fallback, MMU rejection and legacy request behavior. Full repository suite passes. This is prototype contract verification, not integrated Dolphin or runtime performance evidence. Next assemble isolated coherent candidate from these pieces using unchanged accepted generated code/profile; keep normal bootstrap/app unmodified until matched runtime evidence.

## R114 — optional paired-store caller prototype

Unapplied lc-pair-store.inc limits acquisition to type4/two lanes/no host write journal. Requests external_pointer with size0, which existing HookExternalPointer explicitly rejects; it does not use old unguarded positive-size pointer behavior. New host contract requires exact opt-in, synchronized MSR, no lockstep/debug/cache/journal/sink state, and R113 eligibility. Rejection must have no side effects; do not propagate MSR before first quantization on a rejected request. Fast stores use unchanged psq_quantize_int sequentially and immediate-use pointer, no cached mapping.

test-lc-pair-store.py extracts actual reference ppc_psq_store and quantizer, injects snippet only in test. One million double-bit operand pairs with all64 GQR scales match two bytes and FE_ALL_EXCEPT flags. Null capability and journaling fallback preserve observable callback order/live lane1/GQR snapshot/wrap; one-lane and other types never request pointer. ASan/UBSan and full repository suite pass. Source assertion verifies old hook size0 rejection, not integrated old-host runtime proof. No runtime/module mutation or speed claim. Next implement/test optional host callback coherently before any full build.

## R113 — isolated two-byte eligibility prototype

Unapplied patches/experiments/lc-pair-pointer.inc returns an immediate-use pointer only for same-BAT-page, fully bounded two-byte physical locked-cache range, with live BAT translation and existing memcheck/cache/LC-journal/HW-sink guards. Caller still must propagate MSR and reject host/lockstep journaling; no pointer caching authorized. No raw effective-address shortcut.

test-lc-pair-pointer.py reuses byte-method stubs and actual promoted byte implementation; ASan/UBSan check every cache start, all65536 byte pairs at four offsets, per-pair parity, boundaries/wrap/page crossing, null and size0/1/2 cache, debug/cache/journal guards, mapped flags, remap and DR-off behavior. Full suite passes. These tests prove isolated stub-model eligibility/parity, not integrated caller order, hardware behavior, or speed. No runtime patch/module build. Next optional caller integration with canonical fallback and source-derived quantization/order tests before a runtime experiment.

## R112 — paired-store batching contract

Exact ppc_psq_store calls psq_store_value for lane0 before reading lane1; it snapshots GQR type/scale once, wraps ea+size as u32, respects w, and rejects disabled/invalid stores. New test-psq-store-order.py extracts actual function and uses observable store callbacks to verify these properties under UBSan; full repository suite passes. This is pinned-source behavioral contract, not a hardware oracle.

Quantized type4 lane stores separately call mem_write8→HookExternalWrite→PropagateGuestMSR→guarded TryWriteLockedCacheByte. Existing CPUState external_pointer slot is not used by these memory accesses. HookExternalPointer currently returns a raw effective locked-cache range without live BAT/debug guards and has addition-based range checking; it must not simply be enabled as the shortcut. Potential bounded design: guarded same-page two-byte physical locked-cache pointer acquisition, no caching, with all debugger/cache/journal conditions rejected and canonical sequential stores retained otherwise. Before implementation, prove range/wrap/remap/fallback semantics in isolation. No module rebuild or default change made.

## R111 — integer widening simplification rejected without module build

Current generated decoder retains per-instruction helper/state traffic; historical blanket inlining/O3/GQR centralization were already rejected and not retried. Tested convert_to_double normal path via exponent-bias addition and existing integer fallback for zero/subnormal/infinity/NaN. tests/probe-f32-widen.c calls actual pinned types.h reference. Exhaustive 4,294,967,296 encodings match, including every signaling/quiet NaN payload and signed subnormal/zero. No hardware FP cast or relaxed FP used.

Compile: clang -O2 -ffp-contract=off -fno-fast-math -I ref/ModernGekko/vendor/dolphin/GXRuntime/include tests/probe-f32-widen.c -o generated/tests/probe-f32-widen. Run exits0; private generated/tests/probe-f32-widen-r111.log. Four alternating 10M mixed-bit-input trials candidate/reference ratios1.073/1.075/1.069/1.081. This uniform input distribution is not measured decoder operand distribution, but gives no reason to pay for a whole-game build. Reject candidate, preserve runtime source. Next inspect actual memory-hook/batching contracts for a larger concrete opportunity; do not repeat prior global/codegen candidates.

## R110 — decoder-PGO confirmation rejects promotion

Candidate in decoder-confirm-r109, exact R85 restore/trigger52789, same trace/current runner/defaultLC. Visible restored scene and advancing movie, clean runtime44966 exit0/native-only, unchanged NANDa5743199...afa6. Fixed [299028685092125,299088685092125): VI/frame/presents2636=43.933333FPS,DMA10996=23.4581333kHz,framep95/p99=24.022083/24.678792ms,2594gaps>=20ms. Whole9574frames/190.873s,317underruns3backlogs,6063depthreads,2transitions,fallback0/smc_failed0. Private phase.csv and decoder-confirm-r109.log.

Final candidate43.933 versus immediately preceding accepted47.283 (-7.08%) and worse p99. Four-run order: accepted38.733,candidate40.733,accepted47.283,candidate43.933. Uncontrolled host/thermal variation prevents precise causal regression sizing, but there is no demonstrated gain sufficient for promotion. Retain accepted original profile/module and stop unchanged candidate tests. Manifest marks rejected; training evidence retained privately. Next inspect generated/native decoder structure for a concrete higher-impact hypothesis before any new full build. No runtime/Simulator remains.

## R109 — reverse control exposes host/order variation

Accepted module in decoder-control-r108, same trace/default LC/R85/trigger. Visible restore and advancing movie; runtime31325 and input70078 both exit0. Fixed [298734216169791,298794216169791): VI/frame2837=47.283333FPS,presents2836,DMA11831=25.2394667kHz; framep95/p99=22.195/22.910625ms,2414gaps>=20ms. Whole9194frames/177.507s,258underruns3backlogs,5623depthreads,2transitions,fallback0/smc_failed0; NANDa5743199...afa6 unchanged. Private phase.csv and decoder-control-r108.log.

Same accepted code now47.283 versus initial38.733, larger than candidate's apparent improvement40.733. First A/B cannot establish benefit; no promotion or definitive causal regression claim. Prepared decoder-confirm-r109 from R85 for one candidate confirmation after control, without recent build. If no clear advantage, keep unselected rather than repeat uncontrolled runs indefinitely. All runtimes closed; no Simulator.

## R108 — decoder candidate measured, control still required

Audited candidate2a576018...ad7b launched in prepared decoder-candidate-r103 with same current runner/default LC/trace. R85state3 visibly restored, exact trigger78102 exits0, movie advances at two observations, native close2580 exits0. Fixed window [298437817482541,298497817482541): VI/frame/presents2444=40.733333FPS; DMA10193=21.7450667kHz; framep95/p99=26.678084/30.450916ms;2434gaps>=20ms. Initial analyzer invocation correctly refused incomplete window; waited on same runtime, final trace passes. Private phase.csv and decoder-candidate-r103.log.

Compared first baseline38.733FPS: +5.16% throughput but worse p99 (baseline28.932584ms). Prior baseline followed linker load, so no causal speedup/promotion. Fresh decoder-control-r108 copied from R85/Pipe configured for reverse-order accepted-module control; not launched yet. Whole candidate8789frames/186.337s,374underruns3backlogs,5035depthreads,2transitions,fallback0/smc_failed0, NANDa5743199...afa6 unchanged. Unequal whole-run durations prohibit raw-underrun comparison. No game remains; accepted package unchanged.

## R107 — candidate complete, first matched baseline

Build1268 finished0 after active ThinLTO, audit passes RMGE01/ARM64/macOS14/1322chunks/19SMC. Candidate SHA 2a576018bd862d1426b2ad225cfd14fb70f24c8c99e68a42b9bc3fadcbcdad7b, size99,394,392. Not selected.

Accepted package run uses decoder-baseline-r103 and trace, R85 slot3 visible restoration, exact trigger once, advancing movie observed twice, native close/runtime11545 exit0; input88164 exit0. Initial pre-restore screenshot was black, so no fresh title-visibility claim. Fixed interval [298177869152291,298237869152291): VI/frame2324=38.733333FPS, presents2323, DMA9693=20.6784kHz, frame p95/p99=27.970125/28.932584ms, 2319gaps>=20ms. Private phase.csv and sibling decoder-baseline-r103.log. Whole-run6900frames/147.699s,313underruns5backlogs,4287depthreads,2buttontransitions,fallback0/smc_failed0. Not audio acceptance.

Baseline started after heavy link, no simultaneous build/profiler; unmeasured thermal state and host variance remain possible explanations for lower cadence than R99. Post-close highest observed other processes WindowServer17.9%,ChatGPT16.9%,Logitechupdater14.3%. Do not attribute a subsequent gain solely to candidate without follow-up baseline. Candidate profile prepared but not launched. Next candidate then reverse/control check if faster; accepted artifacts unchanged.

## R102 — decoder training recorded, profile-only candidate building

Launched existing trainer through current package with LLVM_PROFILE_FILE=generated/pgo/decoder-profiles-r101/attack-%p.profraw and disposable decoder-training-r101 user directory. Native title, state3 restored at flowers/lake, one R85 trigger, visible advancing attack movie at two observations. Closed natively, exec70563 exit0; fallback=0/smc_failed=0, LC activation correct. Raw attack-87494.profraw, private log generated/runtime/decoder-training-r101.log. Instrumentation speed/underruns are not shipping metrics. NAND remains a5743199...afa6.

llvm-profdata merge produced decoder-r102.profdata SHA b104996c07b61e7f65edec7d068c1e54da8d7695b904e8a2a21c5a5e3257d911. func_804520A0 entry 21,516,841, hash f933e25f9c38a25c; func_804530A0 entry 40,635,145, hash afb452bf05cdd1f5. Merge with unchanged accepted profile gives opening-decoder-r102.profdata SHA b355557fae4d0d826eb131807eca5f6bd95a0f51ac5edec50e15559d8838889b. No arbitrary counter synthesis or weighting.

scripts/build-decoder-pgo-experiment.sh checks inputs, reuses accepted generated source and unchanged helper, O2/ThinLTO/strict FP/arm64/macOS14; both compile and link receive merged profile. Config manifest explicitly unselected. Build session1268 live at 74/1332, log generated/pgo/decoder-r102-build.log; output decoder-use-r102. No game/build overlap during collection, no Simulator. Repository suite passes. Next poll same build through link/audit, then matched movie comparison; no promotion until runtime evidence.

## R101 — exact decoder absent from accepted compiler profile

Read current rmge01.profdata using llvm-profdata show --counts --function. func_804520A0: entry 0, 2947 internal counters all zero, CFG hash f933e25f9c38a25c. func_804530A0: entry 0, 2627 internal counters all zero, CFG hash afb452bf05cdd1f5. These are R94 sample's two hottest generated functions (462/528 self samples). ppc_ps_add_op has 90,172,284 calls, so the file is not generally empty. The previous opening+Gateway profile also reports decoder func_804520A0 entry 0. This gives a different hypothesis from repeating rejected Gateway training: train the actual movie decoder, retain unchanged code and strict FP, then measure a profile-only candidate.

Existing generated/pgo/instrument-build/gRMGE01_recomp.dylib SHA 591ff35e70a1ca20cf3da1d91a72b593f249ab36d63fb043a849e2b3d7e8e033 has RMGE01 ABI3/1322 chunks/19 SMC descriptor. Its CMake source is cache 7f703e89efc28f0b; recursive diff -qr of that generated tree vs accepted 1a7fde44f42859a5 tree exits 0 with no differences. Build flags include O2, fprofile-instr-generate, ThinLTO, strict FP, arm64/macOS14. Current helper source matches prior reference SHA 3026eb10...4806c. This supports reusing training artifact, not performance acceptance. Prepared isolated decoder-training-r101 from R85 Config/Wii/config.ini and slot 3 (aea2b7a3...7ab8), Pipe configured. No runtime launched yet. Next use LLVM_PROFILE_FILE under generated/pgo/decoder-profiles-r101, visually restore and trigger attack, clean exit, then check decoder coverage before any costly candidate build. Never benchmark instrumented runtime as shipping speed.

## R100 — rejected generator experiment removed from defaults

Normal bootstrap now removes only the pinned CLZ patch and requires a clean DolRecomp checkout. Its million-input/UBSan/lowering test applies the retained patch in a disposable tree. Rebuilt desktop generator SHA fc8dcee4836b3347f7d1ac30c1cf13716302b916612e040eb0ad7a5559a7abf8 and standalone SHA 4094146c03bc0c0fdfede953dadfcb59bce824bc569313db93b671aa0f4a2b57. No game-module regeneration or performance claim. Accepted runner d4d0c3c...d8ff53 and module 25e17d0...65393 unchanged. Repository checks and standalone codegen_compile/c_execute pass; first test invocation used desktop cache without built test executables and failed as missing fixtures, corrected by using existing standalone test cache. Bootstrap repeated successfully; no booted Simulator.

## R99 — finite add/sub module audited and rejected by gameplay result

Build session 39974 completed 0. Candidate generated/ps-finite-r96/module-build/gRMGE01_recomp.dylib SHA-256 89a47ced8d7304c326ea8dc25fdf2a12c5fa8a995697ba3f3fbdc6cbc7a01417, 99,527,128 bytes. Module audit passes RMGE01, 1322 chunks, 19 SMC ranges, macOS14/arm64. Selected marker/package unchanged.

Sequential ps-baseline-r98 / ps-candidate-r98 runs use same packaged runner with default LC enabled, same R85 slot 3/config/NAND, same short trigger and tracing. Both visibly restore at flowers/lake and advance attack. No compilation/profiler overlap; host variance remains uncontrolled. Extract with measure-attack-trace.py:

- Baseline [295942804951750,296002804951750): 2777 frame starts/VI, 2776 presents, 46.283 FPS, 11582 DMA blocks / 24.708 kHz. Frame-start p95/p99 23.362/23.990 ms.
- Candidate [296291384241583,296351384241583): 2731 frame starts/VI/presents, 45.517 FPS, 11391 DMA blocks / 24.301 kHz. Frame-start p95/p99 23.569/25.813 ms.

Candidate -1.66% frame rate, no usable improvement; rejected for promotion. Microbenchmark benefit is insufficient, and ignored PGO data/whole-module code layout/host load are possible contributors, not established causes. Both normal close exit 0, fallback=0/smc_failed=0, two button transitions, real depth reads. Whole-run underruns 310/324 over unequal 286.5/276.0 s and differing final scenes are not matched state/audio-quality comparisons. No runtime/build/Simulator remains. Keep accepted module and promoted LC path; do not repeat unchanged add/sub candidate. Next pursue a larger decoder route or controlled profile/code-layout hypothesis, and correct normal generator workflow so rejected CLZ isn't silently regenerated into future defaults.

## R97 — host exception parity / experiment audit preparation

Extended probe clears and compares FE_ALL_EXCEPT independently around reference/candidate execution. Actual extracted candidate bodies pass all one million cases across four rounding modes, now including host floating-point exception flags as well as complete guest CPU state. This supersedes R95's missing-host-flags limitation; full Dolphin lockstep remains untested. The probe ran alongside compilation, so its incidental printed microbenchmark timings are not accepted performance evidence.

config/ps-finite-experiment.txt records accepted-generation, source/patch/profile hashes and strict compile flags, explicitly selected=false. Build script checks PGO hash and writes this manifest, adds a symlink to accepted generated chunks without modifying them, and audits candidate on completion. audit-module.sh follows only the explicit generated-directory root symlink (-H); accepted default audit passes. Current live build 39974 was at 1247/1332 when recorded, not yet a completed artifact. No game/Simulator running; do not restart it or run bootstrap/build in parallel.

## R96 — actual finite add/sub helper candidate building

Copied GXRuntime into ignored generated/ps-finite-r96/GXRuntime; only cpu_interpreter_float.c changed. Each add/sub helper checks four finite input lanes, computes same operation/force_single/write/FPRF on success, otherwise executes untouched original body. Candidate source SHA-256 707f6d0a1330e7ab5a9ee815cc9ba39a3f678f398e0b7fd4a27a9a8ca67b34ba, original 3026eb10f63667a85dccb6e1fc7df1d2c299058cd636cae6b2c0ca7b02a4806c. Experimental patch SHA-256 45cdbc809b05099eac50b52845f0ec6a9dccd7379a62cf7d00fc4651c90120b2. No source overlay/default change in pinned runtime.

test-ps-finite-candidate.py extracts actual modified bodies into the pinned reference probe. One million full-state comparisons pass; four normal-add candidate/reference timings 0.742/0.719/0.726/0.725. Same limitations as R95; not a gameplay gain. Repro script scripts/build-ps-finite-experiment.sh checks original/patch/candidate/accepted-module hashes and never selects the output. It reuses the accepted 1a7fde44f42859a5 generated directory to exclude rejected CLZ change. Actual build flags verified -O2 (last optimization flag), strict FP, ThinLTO, original PGO, macOS14/arm64. Two of 83 helper functions have mismatched profile data ignored; this is expected but may offset microbenchmark benefit.

Build session 39974 live at 461/1332 when journaled, output target generated/ps-finite-r96/module-build/gRMGE01_recomp.dylib. Do not run build script concurrently or overwrite accepted cache. Next wait same handle, audit exact output, then baseline/candidate gameplay with accepted LC runner default on for both. Repository tests pass; no runtime/Simulator running.

## R95 — isolated finite paired-add/sub probe

`bash tests/probe-ps-finite.sh` builds a standalone probe including the pinned cpu_interpreter_float.c as reference. No engine/default changes. Candidate checks all four input lanes finite, then performs the same double add/sub, force_single, ps_write_both and set_fprf/classify_f32. Nonfinite input invokes the original helper. Finite input can overflow, but original ni_add/ni_sub only clears FI/FR for infinite inputs or handles NaN results; this candidate retains the same casts/host rounding and guest output path.

One million full CPUState comparisons pass: four host rounding modes, deterministic random bit patterns/FPSCR, special-value pair cross-product, signed zero/subnormal/infinity/NaN cases and destination aliases. Host floating-point exception flags and a complete Dolphin interpreter lockstep are not covered. CPUState matching is stronger than numeric result only but not full-platform acceptance.

Four alternating five-million-call normal-add microbenchmarks in latest run: reference 0.027205/0.027118/0.027572/0.028182 CPU seconds; candidate 0.019294/0.019185/0.020005/0.019806, ratios 0.709/0.707/0.726/0.703. This uses stable finite operands and a volatile indirect call; not decoder operand distribution, whole-helper mixed workload, or game FPS. Subtraction speed not separately measured. Candidate is promising enough for isolated module work, not default promotion. Next implement pinned helper delta and source-derived candidate regression, build separately with accepted generator/PGO settings, then matched R85 test. Do not combine rejected CLZ changes or relax FP contracts. Accepted package unchanged; no game/Simulator remains.

## R94 — default activation and remaining decoder profile

Launched current packaged wrapper via env -u GALAXYPAD_LC_BYTE_FAST, isolated default-lc-r94 copied R85 checkpoint/config/NAND. Module unchanged. Correct scene restored; exact trigger starts movie, activation logs pc=80452a2c/ea=e0000000 without explicit opt-in. Visible 46.1 FPS before sampling, 49.2 at close. This confirms argument-driven packaged default, not a new frontend Play interaction or performance average. Five-second sample captured under default-lc-r94/attack.sample.txt, then normal close exit 0, fallback/failed SMC zero. Whole-run 129 underruns remain; sampled/mixed run is not acceptance.

CPU thread 3940 samples, 3730 beneath Run, 3619 under chassis_dispatch. Self-summary: func_804530A0 528; func_804520A0 462; ppc_ps_add_op 328, madd 302, sub 218, convert_to_double 155, TryWriteLockedCacheByte 132. Those aggregate self counts do not identify exact operand distributions. Pixel-store callsite +51244 now 53 inclusive samples versus historical R81 89, but different runs/movie times preclude a precise before/after attribution.

Next inspect paired-single arithmetic and conversion fast paths, with bit-exact NaN payload/signalling, subnormal, rounding and FPSCR behavior. GXRuntime types.h convert_to_double is integer-exact and preserves signalling NaNs; blindly substituting a hardware float cast could change them. Prior failed blanket inlining and CLZ candidates remain rejected. Do not loosen FP semantics or disable rendering correctness to chase the residual ~47-FPS gap. No runtime/Simulator remains.

## R93 — disabled G5 control and incremental package default

R89 candidate with LC=0, identical R72 profile and G5 fixture, no state/trace. Visible title/file-select/pointer success at 59.9 FPS; normal exit 0/native-only, unchanged NAND. 11,881 frames/198.286 s (~59.92 Hz), 49,622 DMA blocks/198.640 s (~31.98 kHz), 3 underruns/3 backlog corrections, 20,553 depth reads. Underruns cluster at enqueue 9566, unlike R92's later incidents. Unequal run durations and uncontrolled host load prohibit a precise rate comparison; matching totals alone do not prove identical causes. No LC activation expected. Private log generated/runtime/g5-lc-off-r93.log.

Decision: package guarded LC path as an incremental default based on R90 +11.76% movie gain, R91 untraced movie/control/clean exit, byte guard/value tests and no clear G5 functional/cadence regression. This does not close G6 or audio stability. Wrapper exports GALAXYPAD_LC_BYTE_FAST default 1 while honoring 0; runtime library remains default-off outside this wrapper. Child inheritance/default/opt-out tests pass. Package audit now compares wrapper identity. Rebuilt signed runner d4d0c3c89c7f4534efc90d0fb2b280b62c0d3a0a4256b11a470c212878d8ff53 matches tested candidate; accepted module remains 25e17d0e730b512f20083db26d3a7f58bc60da126161fe34c227357372c65393. Build/audit passes, prior app preserved by normal packaging backup. Next runtime activation check through default wrapper with no explicit LC environment setting. No game/Simulator remains.

## R92 — candidate normal-boot G5 regression

Copied R72 Config/Wii/config.ini into g5-lc-r92; no StateSaves. Same R89 candidate/accepted module, LC opt-in on, no trace/profiler. Ready title visually verified, then g5-title-file-select.json once. A+B reaches file select, pointer highlights Mario file 1, inspected 59.9 FPS. Normal close exit 0/native-only. Whole run 15,459 frames/257.983 s (~59.92 Hz), 64,546 DMA blocks/258.341 s (~31.98 kHz), 3 underruns/3 backlog drops, nonzero PCM and zero backend errors, 30,999 depth reads, four button transitions. Three underruns are not a zero-starvation/audio-quality pass. No LC activation breadcrumb occurs on this route; the optimized write path itself is not exercised here. Mixed duration differs from historical R72, so no direct underrun-rate regression attribution. Next same runner opt-in off for baseline comparison before promotion decision.

Private log generated/runtime/g5-lc-r92.log. GameData remains a5743199ed343b04d2d02069881d8754310194ed2b3012f4ec54152272a2afa6, matching R72 source. Repository suite passes. No runtime/Simulator remains, accepted package unchanged.

## R91 — untraced candidate regression and expanded byte test

Same R89 candidate runner and accepted module, GALAXYPAD_LC_BYTE_FAST=1, no phase trace or CPU profiler. Isolated lc-untraced-r91 uses copied R85 state/config/NAND. Ready title, visible pre-attack restore, one exact trigger, advancing attack at 46.2 FPS, movie completion to plaza at 59.9 FPS, then g6-left-jump.json visibly relocates Mario left; airborne phase not independently captured. Normal close exits 0, fallback/failed SMC zero, activation at exact hotspot confirmed. No default promotion yet.

Whole run 16,268 frames / 295.321 s, 255 underruns/3 backlog corrections, 22,836 real depth reads, four button transitions, final projection 0x1d78cebeb09305ae. These mixed startup/state-load/movie/gameplay totals do not replace R90 matched intervals and do not establish audible/stutter-free operation. GameData hash unchanged a5743199ed343b04d2d02069881d8754310194ed2b3012f4ec54152272a2afa6. Private log generated/runtime/lc-untraced-r91.log. No runtime or Simulator remains.

Expanded test-lc-byte-fast.py checks all 256 byte values across every offset of its 16 KiB stub cache (4,194,304 writes) against canonical byte rotation/swap/memcpy output, with BAT_WI set. Additional alias translation/remapping checks pass. This is byte-expression and guard coverage in stubs, not full Dolphin MMU/exception/lockstep integration coverage. Full repository suite passes. Next file-select/audio regression with candidate and no emulator state, then conservative promotion decision.

## R90 — LC byte off/on measurement, promising but experimental

Same signed LC-Byte-Candidate-r89.app runner d4d0c3c...d8ff53 and accepted signed module 25e17d0...65393. Isolated lc-off-r90/lc-on-r90 profiles copied from R85, identical slot 3 and trigger, native 1x/dual-core/audio120/Metal. GALAXYPAD_LC_BYTE_FAST differs (0/1); both enable identical phase tracing. No compile/profiler/Simulator overlaps. Both visually restore before attack; candidate activation breadcrumb proves pc=80452a2c/ea=e0000000. Trigger-relative wall windows, not exact guest-frame alignment; host contention remains uncontrolled.

`python3 scripts/measure-attack-trace.py generated/runtime/lc-off-r90/phase.csv generated/runtime/lc-on-r90/phase.csv`

- Off window [292289757008291,292349757008291): 2550 VI/frame/present events, **42.50 FPS**; 10635 DMA blocks, **22.688 kHz**. Frame-start p95/p99 25.913/26.868 ms, 2543 gaps >=20 ms.
- On window [292553173663333,292613173663333): 2850 VI/frame/present events, **47.50 FPS**; 11887 DMA blocks, **25.359 kHz**. Frame-start p95/p99 22.117/22.803 ms, 2420 gaps >=20 ms.
- Observed gain **11.76% FPS / 11.77% DMA**, substantially larger than R86 CLZ candidate. Still short of reference cadence; one trace-on pair does not establish sustained acceptance.

On-run visibly completes movie, returns to attacked plaza at 59.9 FPS, and moves left after g6-left-jump.json; the brief airborne phase was not independently captured. Both close normally, exit 0, fallback=0/smc_failed=0. Whole-run underruns 356 off/251 on are unequal-duration totals (186.7/307.3 s), not matched-window audio metrics. Real depth reads 5228/25055. Both NAND GameData hashes remain a5743199ed343b04d2d02069881d8754310194ed2b3012f4ec54152272a2afa6. Final projection differs because off ended in movie and on ended in gameplay; do not treat it as a same-state comparison. Next uninstrumented movie-to-gameplay/G5 regression and additional equivalence coverage before default promotion. No runtime or Simulator remains; accepted package unchanged.

## R89 — guarded locked-cache byte candidate implemented, not promoted

Build completed and separate LC-Byte-Candidate-r89.app is signed/verified (runner d4d0c3c89c7f4534efc90d0fb2b280b62c0d3a0a4256b11a470c212878d8ff53). Added required diff --git metadata after bootstrap scope validation: final overlay hash d980680c30fda3e54593930d6815d78ead4c78cd26a9b074f77fbac77394f126 supersedes the original hash below. Bootstrap now passes. No runtime comparison yet.

GALAXYPAD_LC_BYTE_FAST=1 opts into a runner-only candidate after PropagateGuestMSR and relocation translation. It only attempts one-byte effective 0xE-region writes outside native lockstep journaling. MMU::TryWriteLockedCacheByte rejects active memchecks, emulated data cache, shadow cache journals and hardware-write sinks. With DR on, it requires a live BAT entry marked mapped/physical and resolves the physical address using the same masks as TranslateBatAddress; page-table/fault paths fall back unchanged. It checks actual L1 pointer/range before storing exactly one byte. With DR off it checks the physical address directly. No translation/pointer cache or guest code replacement is introduced; GQR quantization remains unchanged. A single activation breadcrumb proves whether runtime reaches the fast path.

Canonical overlay 0012-lc-byte-fast.patch SHA-256 84059b0236e5d76de6140aaf4e5b03346aa3fa3de2a59dda1de28b3c6dc1ab84. Source-derived sanitizer test checks 256 byte values at representative tile/boundary offsets, rejected ranges/null storage, all fallback guards, incomplete BAT flags, remapping and DR-off behavior. These stubbed tests establish the method's bounds/guards, not full Dolphin equivalence or gameplay acceptance. Repository suite passes. Runtime benchmark and promotion remain unproven; accepted package/module unchanged.

## R88 — live locked-cache writes confirmed

Default-off GALAXYPAD_PIXEL_STORE_TRACE=1 diagnostic logs at most 16 external writes from exact PC 0x80452A2C, before address translation; it does not alter the MMU path. Pinned overlay 0011-pixel-store-trace.patch SHA-256 5f49e731e9c72d6231fe2030c31db7b9a5b60e77a9d16b456597987e1118e023. Source-derived compiled tests cover missing/false/malformed opt-in, exact PC scope, fields and cap; repository checks pass.

Separate Pixel-Diagnostic-r88.app signed runner SHA-256 3a62a5b8218ca6814e9d2e8aa6974971df0ebf7aaa9129d98bdf0997a1df0a94 uses accepted signed module 25e17d0...65393. R85 slot 3 restored visibly and short trigger starts attack. All 16 records are size=1, GQR6=3d043d04, MSR=0000a032; EAs are e0000000..e0000005, e0000020..e0000025, e0002a00..e0002a03. This confirms the proposed locked-cache tile stores at this hotspot. MSR.DR is enabled, so a raw effective-address pointer shortcut remains insufficient without checking live translation.

Private log generated/runtime/pixel-r88.log; movie visibly advances at 42.5 FPS. Diagnostic-only run, not a matched benchmark. Native close exit 0, fallback=0/smc_failed=0, 5450 real depth reads. Accepted packaged runner remains 6b354a3c...539. Next implement a default-off byte-store cache fast path only after proving translation maps to L1 and retaining memcheck/lockstep behavior; compare with R86 baseline methodology. No game or Simulator remains.

## R87 — exact pixel-store hotspot localized

R81 sample's 89-sample callsite func_804520A0+51244 maps to accepted binary 0x4bdc350 (base 0x4bcfb24). The preceding call at 0x4bdc34c is ppc_psq_store_inline. Native w23 is 0x80452558; adding 0x4d4 proves guest PC **0x80452A2C**, not 0x80452CD4. Exact generated C names psq_st f9,0(r6),0,6. Other large neighboring callsites also descend through quantized stores into HookExternalWrite/WriteToHardware. This is a larger candidate cost than CLZ alone.

Pinned Petari THPDec.c uses GQR6=0x3D043D04 (unsigned byte, scale -3); THPInit initializes its work tiles at 0xE0000000; IDCT writes those tiles before LCStoreData copies to output. These source matches strongly suggest locked-cache pixel writes, but the current runtime effective address/GQR/MSR at this exact PC still needs measurement. Wrong-region symbol addresses are not used.

GXRuntime get_ram_ptr currently admits MEM1/MEM2 only, so locked-cache stores enter external_write one byte at a time. HookExternalPointer already exposes locked-cache storage, but blindly using it would skip MMU translation, memchecks, and locked-cache shadow journaling. MMU_Tables.cpp translates first and journals before its cache memcpy; preserve those contracts. Next add a default-off bounded diagnostic for exact guest 0x80452A2C external writes (EA, width, GQR6, MSR), reproduce R85 trigger once, then choose a translation/journal-safe optimization from actual addresses. Do not broaden RAM mapping speculatively or launch a full module build before that evidence.

## R86 — bounded CNTLZW comparison, no promotion

Sequential accepted/candidate runs use the current signed runner (6b354a3c...), identical copied R85 slot 3/NAND/native-1x dual-core/audio120 configurations and g6-r85-trigger-attack.json. Both visually restore the yellow-flower position, then show the attack movie advancing. No build or profiler runs concurrently. Both enable phase tracing, so these are diagnostic results, not uninstrumented acceptance.

Run `python3 scripts/measure-attack-trace.py generated/runtime/cntlzw-control-r86/phase.csv generated/runtime/cntlzw-candidate-r86/phase.csv`. The extraction anchors to first nonzero input sample (fixture's A press), then selects [20,80) seconds afterward. This matches trigger-relative wall time, not an exact guest-frame range; independent host load remains a confounder.

Accepted interval [290806222197083,290866222197083): 2620 frame starts/VI/presents, 43.667 FPS, 10927 DMA blocks / 23.311 kHz. Frame-start p95/p99 24.012/24.332 ms; 2611 gaps >=20 ms.

Candidate interval [291042431895291,291102431895291): 2658 frame starts/VI, 2657 presents, 44.300 FPS, 11085 DMA blocks / 23.648 kHz. Frame-start p95/p99 23.592/24.133 ms; 2647 gaps >=20 ms. Candidate module remains 4e1464f9...30ff89, accepted package 25e17d0...65393.

The +1.45% frame/DMA difference does not materially close the roughly-44-FPS movie deficit; do not promote the candidate. Both exit 0, fallback=0/smc_failed=0, two button transitions, final projection 0x1d78cebeb09305ae, real depth reads 4460/5570. Whole-run underruns 267/285 are not comparable due unequal startup/observation durations. Both disposable GameData hashes remain a5743199ed343b04d2d02069881d8754310194ed2b3012f4ec54152272a2afa6. No runtime or Simulator remains. Next inspect larger THP decode cost/lost PGO coverage, not another unchanged small-CLZ comparison.

Status: **G5 accepted; G6 active-gameplay cadence remains below reference**

**Packaged-run correction (R70/R71): R62–R71 timing does not qualify for required-semantics acceptance.** The package placed Sys incorrectly, and the desktop build's LINUX_LOCAL_DEV define selected a bundle-root Sys path before the Apple branch. R70 directly logged valid depth coordinates with both configured/active EFB access disabled. Zero read counters therefore did not establish that readback was unnecessary. Builder now uses Resources/Sys; the hash-pinned FileUtil overlay excludes Apple from the Linux selector and uses TARGET_OS_IPHONE for the Apple split. A source-derived preprocessor regression covers the actual desktop flags. Revalidate performance after runtime depth reads return; do not promote dual-core on the earlier disabled-EFB comparisons. Historical standalone evidence remains separate.

All values below are from the exact RMGE01 arm64 AOT path on Apple Silicon macOS. They are not device, soak, or release claims. A configuration audit found that the frontend `resolution=1920x1080` setting overrides `Config/GFX.ini` and maps to Dolphin EFB scale 3; therefore older measurements are labeled by route rather than treated as native-resolution baselines. The matched chunk-size comparison uses frontend `resolution=640x528`, which maps to EFB scale 1 (the Wii native-class baseline).

## Native-1x rabbit continuation

Newest corrected-package check, R72: untraced dual-core G5/file select produces 12,149 frames / 202.752240625 seconds = 59.920 Hz and 50,740 DMA blocks / 203.108046625 seconds = 31.976 kHz. Zero underruns; one startup-only backlog correction at enqueue 51. Crucially, 24,966 depth reads across 10,600 frames now execute (3.175 seconds total CPU read time, 11.638 ms max); these no longer silently return through the disabled-access path. Pointer hover and slot details are visible. Four transitions, final projection `0xa838adff8d9a2b08`, zero fallback/failed SMC, clean close. This validates the resource fix and fresh G5 continuity; Observatory/gameplay performance must be revalidated with the corrected settings.

The long screenshot-gated R49 continuation caught the pipe-hidden rabbit and shut down at 78,490 frames over 1,310.215 seconds (59.906 Hz), 31.973 kHz DMA, six underruns, 4,116 frame gaps at or above 20 ms (5.244%), `fallback=0`, and `smc_failed=0`. A fresh R50 process loaded the caught-rabbit state and ran at 59.885 Hz with two underruns before clean shutdown. This is useful save-state/relaunch and native-execution evidence, but it is not an in-game save acceptance result.

R51 continued route discovery for 2,297.440 seconds and produced 132,541 frames (57.690 Hz), 30.796 kHz DMA, 523 underruns, and 20,567 frame gaps at or above 20 ms (15.517%). It retained `fallback=0`, `smc_failed=0`, and 28 input transitions. The route included repeated camera rotation, crater traversal, state loading, and grass searches, so it is not a matched optimization comparison. It does confirm that native 1x removes the former approximately-20-FPS floor while leaving visibly uneven frame pacing and audio starvation in a long active session.

R52 was originally labeled as a completed grass-rabbit intercept, but a later live collector/nerve audit invalidated that progression claim. Its performance counters remain usable as long exploratory telemetry: 192,276 frames over 3,233.909 graphics-active seconds (59.456 Hz), 31.735 kHz DMA, 170 underruns, 49 backlog drops, and 23,430 frame gaps at or above 20 ms (12.186%). Native execution remained exact (`native=41,443,890,491`, `fallback=0`, `smc_failed=0`), with 34 input transitions and a 161.483 ms maximum graphics gap. This heavily state-loaded exploration is not a matched performance comparator. It confirms that the native-1x configuration continues to avoid the old 18–20 FPS floor while also confirming that tail pacing and audio continuity are not accepted.

## Instrumented packaged run

The private app sustained 8,313 presented frames through safety/title/file-select interaction and shut down with `native=1556836850`, `fallback=0`, and `smc_failed=0`. The final graphics snapshot had a nonzero projection hash, 4 draws, 12 primitives, 177 BP loads, 28 CP loads, 68 XF loads, 116 textures created, 57 textures alive, 32 vertex shaders, and 63 pixel shaders.

Cubeb delivered 16,864 callbacks and 8,634,368 output frames in the initial signal run. Subsequent FIFO instrumentation rejected audio stability: in the corrected file-select signature run, 26,812 DMA granules were enqueued, 196 running-state underruns continued through enqueue 26,179, one startup backlog correction occurred, and no hard queue-full drop occurred. The 200 ms reserve and existing ±2% adaptive Apple path could not cover the persistent producer deficit. Further resampling would risk pitch and was not accepted as a fix.

The isolated O3 candidate also failed. Under the same restored 80 ms/no-adaptive runtime, copied NAND starting state, scripted route, and file-select projection signature, accepted O2 produced 6,169 frames and 26,119 DMA enqueues with 268 underruns; O3 produced 5,828 frames and 24,734 enqueues with 270 underruns. O3 reduced the maximum producer gap from 151.7 ms to 131.4 ms but reduced frame throughput by 5.5% and DMA throughput by 5.3%, while its last underrun still occurred near shutdown. O3 is not selected; the accepted O2 module and package identity remain unchanged.

The accepted-O2 Null-renderer discriminator required explicit Cubeb because normal headless mode intentionally disables audio. With Cubeb kept active, Null reached the same file-select signature and produced 6,436 frames, 27,104 DMA enqueues, and 216 underruns through enqueue 26,762. This is 4.3% more frames, 3.8% more enqueues, and 19.4% fewer underruns than Metal, but it does not clear the audio gate. Null also incurred a 1.80-second maximum depth-peek stall, so the result shows that Metal load contributes while also proving it is not the sole source of sustained starvation.

The first long G6 active-play route proved that the exact `SelectThread` hint is scene-specific. Across 3,197.898 seconds, graphics produced 156,955 frames (49.081 Hz, 81.88% of 59.94). Across 3,198.984 seconds, the DSP produced 655,035 overlapping 128-frame granules (26.210 kHz, 81.91% of 32 kHz), while the output callback remained correct at 48.000 kHz. The matching deficits point upstream of the mixer. The run recorded 3,109 underruns through almost the entire route, so an experimental 90%-reserve target was rejected and the proven G5 80% policy restored. The next bounded discriminator is a CPU sample during visible Star Festival gameplay, followed by exact-symbol resolution of any dominant guest wait PC.

That long route was rendered at EFB scale 3, not 1×. Correcting the frontend override improved the absolute rate but did not clear the defect. From identical copied Star Festival state at true 1× and dual core, the accepted O2/4,096-instruction C module produced 15,706 frames in 306.750 seconds (51.20 Hz) and 65,692 DMA granules in 307.567 seconds (27.34 kHz), with 271 underruns. Splitting generated C at 1,024 instructions reduced the module from 100,762,840 to 93,190,792 bytes and improved the route to 19,097 frames in 359.711 seconds (53.09 Hz) and 79,973 granules in 361.515 seconds (28.31 kHz), with 254 underruns. A 256-instruction split was slightly worse at 52.87 Hz and 28.19 kHz. The 1,024 candidate is a measured 3.7% improvement, but remains approximately 11% short of reference video and DSP cadence.

Minimum-size optimization is decisively rejected. Recompiling the 1,024 generated sources with `-Oz` reduced the module to 61,174,312 bytes but visibly reduced Star Festival play to about 21–22 FPS. Clean aggregate telemetry reported 10,480 frames in 310.506 seconds (33.75 Hz), 44,029 DMA granules in 312.476 seconds (18.04 kHz), and 651 underruns, with `fallback=0` and `smc_failed=0`. Its CPU sample shifted heavily into uninlined floating-point/runtime helpers. The temporary template allowance for `-Oz` was reverted.

The chunk experiment also exposed a reproducibility defect: the current module cache key does not include the effective C chunk size or dispatch lookup environment. Separate output roots protected these runs, but a non-default chunk artifact cannot become the accepted identity until that key is corrected and the normal scripted build reproduces it.

That cache defect is now fixed by overlay `0008-module-cache-codegen-options.patch`. The normal script generated a distinct `fd7022cf46adb6b9` suffix, recorded `c_chunk_instructions=1024` and `dispatch_lookup=linear`, and reproduced the isolated 93,190,792-byte module byte-for-byte at SHA-256 `34488efb37e30502f1e40e047d91bc69e78c709d129ece39c8b7089e6095a59c`. The strengthened module audit cross-checks descriptor chunk ranges against the generated source inventory instead of assuming 331.

The immediate post-build G5 regression did not reproduce the earlier zero-underrun result. At true 1×, C1024 single core reached the accepted projection/input state and produced 7,307 frames/125.263 seconds (58.34 Hz) and 31,062 DMA granules/126.379 seconds (31.46 kHz), with 13 underruns. A matched accepted-4,096 comparator produced 7,089 frames/124.877 seconds (56.77 Hz) and 29,906 granules/125.415 seconds (30.52 kHz), with 30 underruns. C1024 dual core produced 7,252 frames/125.620 seconds (57.73 Hz) and 30,841 granules/128.423 seconds (30.74 kHz), with 26 underruns, so dual core is rejected for this route. The host is a fanless MacBookAir10,1 and had just completed a sustained ThinLTO build; no thermal warning or Low Power Mode was reported. The comparison still favors C1024, but absolute continuity is not accepted until a cooled-host rerun reproduces it.

A cooled sampled C1024 diagnostic improved to 31.70 kHz/10 underruns and showed that the scheduler idle loop was no longer a hot leaf; exact floating-point and paired-single helpers dominated. The decisive unsampled cooled control then produced 7,466 frames/125.242 seconds (59.61 Hz) and 31,591 DMA granules/126.470 seconds (31.97 kHz), with zero underruns, one startup backlog correction, zero hard drops, and the accepted projection/input/native-only signatures. This restores G5 and promotes C1024 to the accepted module identity. It does not solve the separate Star Festival result of 53.09 Hz/28.31 kHz.

The next accepted-C1024 true-1x G6 run reached the Bowser attack transition but confirmed severe user-visible stutter. A 20-s live window-title sample began at 19.4 FPS and then ranged from 29.1 to 38.6 FPS. Clean shutdown after 2,213.350 seconds reported 93,065 frames (42.047 Hz), 388,554 128-frame DMA granules over 2,214.593 seconds (22.458 kHz), 3,620 underruns, five backlog drops, and no queue-full drops. Of those frames, 62,936 (67.63%) had gaps of at least 20 ms, 7,214 (7.75%) at least 33 ms, 1,803 (1.94%) at least 50 ms, and 192 at least 100 ms; the maximum gap was 542.5 ms. The exact native path remained intact (`fallback=0`, `smc_failed=0`).

A concurrent 12-s CPU sample and aggregate EFB telemetry separate two costs. The CPU-GPU thread saturated approximately one host core. Synchronous depth reads spent 50.566 seconds in total across 232,732 peeks (2.28% of graphics active time), peaked at 12.871 ms, and appeared as 273 samples waiting in `Metal::StagingTexture::Flush`/`MTLCommandBuffer::waitUntilCompleted`. This is a real hitch source but is too small in aggregate to explain the full 29.9% cadence deficit. The remaining hot work is native guest execution, especially generated paired-single/float helpers (`ppc_psq_load_inline`, `dolrecomp_f32_from_bits`, `ppc_fmuls`, madd helpers) plus vertex/display-list work. The host reported no thermal or performance warning and Low Power Mode was off. Do not disable correct EFB depth semantics to improve the number.

The accepted module is already a Release ThinLTO build (`-O2`, `-flto=thin`, strict floating-point contraction/fast-math disabled), so merely enabling LTO or raising the global optimization level is not an untried fix. The generated bit conversion and unquantised paired-single load paths are source-inline, yet the linked image and profile still contain materialised helper bodies; `ppc_fmuls` remains an out-of-line routine that performs 25-bit operand rounding, non-IEEE result handling, exception gating, FPR/FPSCR updates, and paired-lane writes. Any helper specialization must therefore be instruction-specific and oracle-tested, not a blanket fast-math or force-inline change.

That warning was tested directly. Forcing the common `ppc_psq_load_inline` helper to `always_inline` grew a representative chunk's assembly by about 19% and the complete dylib by 2.3%. On the exact matched 317-second Star Festival route, the candidate fell to 48.110 Hz graphics and 25.658 kHz DMA with 337 underruns, versus the linear control's 51.528 Hz/27.515 kHz and 280 underruns. The visible title fell to 15.7 FPS. The change is rejected and the runtime header was restored.

Indexed dispatch is accepted as a meaningful but incomplete improvement. DolRecomp's indexed mode divides the 1,322 chunks into two contiguous runs and uses a page table so each address lookup walks at most one run. The initial build exposed a module-table generator incompatibility; the pinned fix derives the same two coverage ranges from the indexed boundary arrays and produces byte-identical coverage metadata to the linear header. On the same pristine-state, dual-core, true-1×, 44-transition route, indexed dispatch produced 17,060 frames in 309.595 seconds (55.104 Hz) and 71,610 DMA granules in 311.413 seconds (29.434 kHz), with 155 underruns. This improves graphics by 6.94%, DMA production by 6.97%, and underruns by 44.6% over the matched linear control. Projection remained `0x190cf1d3666f1e56`; `fallback=0` and `smc_failed=0`. A live Star Festival screenshot read 45.3 FPS.

The normal build reproduced the measured indexed dylib byte-for-byte at SHA-256 `80411bfa49266f23c44657f03e79d53f6ed1b660a406c0a0b1b051e3f08f97d1` (93,207,368 bytes, cache suffix `7f703e89efc28f0b`). Its module and private-app audits pass. The established G5 regression then produced 7,419 frames in 124.180 seconds (59.744 Hz), 31,158 DMA granules in 124.738 seconds (31.977 kHz), zero underruns, one startup-only backlog correction, exact projection `0x14564ea8ed5a5f20`, four input transitions, and native-only execution. This promotes indexed dispatch without reopening G5, but 55.104 Hz/29.434 kHz remains short of the G6 reference target and is not a playability completion claim.

Two post-indexing hot-path experiments were then rejected. Centralizing the overwhelmingly common GQR0 paired-single loads/stores reduced the dylib by 172,272 bytes and collapsed 197 duplicated inline helper bodies to 14, but its exact route produced 55.716 Hz graphics, 29.733 kHz DMA, and 129 underruns. The immediate accepted-indexed control produced 55.901 Hz, 29.830 kHz, and 124 underruns, so the candidate lost by 0.33%/0.32%; all temporary emitter/runtime changes were restored. Skipping the redundant host-call check at the already-vetted chassis entry retained exact projection, 44 inputs, and native-only execution, and produced 56.230 Hz/30.019 kHz with 120 underruns. That 0.59%/0.64% edge is too small for acceptance, and the measured `hook_fb` field was not evidence for the hypothesis because it counts instruction fallback rather than host callbacks. The template change was restored. The indexed module/package identity therefore remains unchanged.

An exact per-read EFB trace then ruled out same-frame duplicate suppression as a useful next optimization. The 1× matched route recorded 31,349 depth reads across 12,377 frames with peeks, at most three per frame. Median/p95/p99/max read times were 0.079/0.847/0.976/7.644 ms. All 1,473 repeated same-frame coordinates returned the same value, but together consumed only 17.799 ms—0.260% of the 6.840-second total—because Dolphin's deferred tile cache had already paid the synchronization cost. No readback shortcut was enabled. The reproducible default-off trace now records frame, channel, coordinates, returned value, latency, guest PC, and guest LR.

Cadence instrumentation then showed the Metal baseline itself was running slow: 50.590 frames/s and 27.282 kHz DMA production versus 59.94 Hz and 32 kHz targets, while Cubeb requested 48.004 kHz. Two 10-second CPU samples identified RMGE01's scheduler idle spin at `0x804AB358` as the dominant active main-thread stack (287/1,000 early and 215/1,000 at file select). The US symbol map names the containing function `SelectThread`; pinned Petari `OSThread.c` corroborates the idle loop semantics. The exact-DOL StaticRecomp idle hint restored 59.884 frames/s and 31.946 kHz DMA production without changing projection or AOT fallback state.

With the remaining 0.17% producer deficit now inside the reviewed ±2% queue servo's range, retaining 80% of the configured 200 ms reserve absorbed the measured 156.6 ms maximum producer gap. The final full route produced 7,096 frames, 30,059 DMA enqueues, zero underruns, zero queue-full drops, `fallback=0`, and `smc_failed=0`. The one backlog correction occurred at enqueue 53 during startup. This closes the sustained G5 performance/audio defect, but does not substitute for later perceptual pitch, gameplay, transition, device, or soak evidence.

The correlated file-select run recorded 25,967 P1 input samples, 403 button-active samples, four button transitions, and IR visibility for every sample. The last sensor coordinates were `(655,529)` after the deterministic host pointer command. File select itself recorded zero CPU EFB peeks. A separate instrumented scene recorded 2,221 depth peeks, 2.147 seconds cumulative wait and a 16.554 ms maximum; a cold headless scene recorded a 2.265-second maximum. Scene identity, per-frame distribution, and cache-warm comparisons remain required before optimization.

A fresh 10-second sample after the Bowser attack further narrows the remaining G6 defect. The CPU thread spent 5,932 of 7,000 samples in `StaticRecompCore::Run`, with 5,336 below `chassis_dispatch`; no individual generated guest function dominated. The video thread was waiting for 4,166 of 7,011 samples, while synchronous EFB-depth wait accounted for only 48. Sparse views reached 59.9 FPS, while ship, fire, fountain, and plaza views commonly ranged from about 40 to 50 FPS. The remaining stutter is therefore scene-dependent portable-AOT CPU throughput, with secondary rendering hitches, rather than a universal 18 FPS cap or continuously saturated Metal thread.

Default-off correlated phase tracing is now available through `GALAXYPAD_PHASE_TRACE`; see `PHASE-TRACE.md`. A Null/headless smoke validated 31,408 cross-thread rows spanning VI, frame begin/end, present queue/completion, input, DMA production, and audio callbacks. Because line-buffered tracing perturbs timing, those counts validate instrumentation only. An exact Metal active-gameplay capture plus an uninstrumented control remains required before using its interval distributions to select another optimization.

## Matched phase trace and profile-guided module

The matched phase trace/control pair establishes that presentation is not the limiting stage. Traced graphics/DMA were 54.397 Hz/29.091 kHz versus 54.649 Hz/29.279 kHz uninstrumented, only 0.46%/0.64% observer cost. Frame intervals were 17.002/22.645/23.504 ms median/p95/p99, and 29.21% exceeded 20 ms. Nearest present queue-to-completion was 0.119/0.167/0.953 ms, while first-draw-to-frame-end was 13.064/21.177/22.237 ms. During the final 120-second active scene, VI/frame-end/present cadence converged at 47.932/47.670/47.873 Hz. This localizes the primary work before present in native generated execution and FIFO/render preparation.

An ignored Clang instrumentation run of that exact route produced local profile SHA-256 `f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d`, covering 32,550 functions and 3,750,116 blocks. The highest counts independently matched the CPU sample: exact float/paired-single helpers, chassis dispatch, generated memory access, and hot guest loops. Applying that profile at O2 with ThinLTO, `-ffp-contract=off`, `-fno-fast-math`, 1,024-instruction chunks, and indexed dispatch produced 57.444 Hz graphics and 30.784 kHz DMA with 79 underruns. Its fresh sequential non-PGO control produced 54.961 Hz/29.455 kHz with 175 underruns. The +4.52%/+4.51% improvement retained projection `0x190cf1d3666f1e56`, all 44 input transitions, `fallback=0`, and `smc_failed=0`.

The first G5 regression recorded one shutdown-edge underrun at enqueue 42,738 while otherwise sustaining 59.41 Hz/31.95 kHz. The single allowed confirmation from another fresh twin produced 59.77 Hz graphics, 31.98 kHz DMA, zero underruns, the exact `0x14564ea8ed5a5f20` projection, four transitions, `fallback=0`, and `smc_failed=0`. The normal `GALAXYPAD_PGO_PROFILE=generated/pgo/rmge01.profdata ./scripts/build-module.sh` path then reproduced the isolated 99,510,616-byte dylib byte-for-byte at SHA-256 `6fba4629eb07e79132a344bc2d68bf9f62627478d5a7dc8a19e1af291942c916`; its cache and manifest include the profile hash. The profile and generated artifact remain ignored/private and are not packaged. PGO is accepted as an improvement, but G6 remains unmet because the route is still below the reference 59.94 Hz/32 kHz target and the Grand Star/save/relaunch proof is incomplete.

A fresh 86.8-minute visible PGO progression run did not reproduce the reported 18 FPS state before the Bowser transition. Sparse Star Festival views held 59.9–60.0 FPS; the densest observed town/lake composition read 47.9 FPS, and inspected route views otherwise ranged from about 50 to 62.5 FPS. Aggregate clean-shutdown telemetry produced 295,583 frames in 5,208.246 seconds (56.753 Hz) and 1,233,012 DMA granules in 5,208.612 seconds (30.301 kHz), with 1,678 underruns and 51 backlog drops. Of all frames, 11.858% had gaps of at least 20 ms, 0.141% at least 33 ms, and 0.043% at least 50 ms; the maximum gap was 447.0 ms. Execution remained native-only (`fallback=0`, `smc_failed=0`) and 64 input transitions were observed. This is materially better than the old 19.4–38.6 FPS failure, but the sustained DMA deficit and approximately 19.3 underruns/minute prevent a G6 or audio-stability acceptance claim.

A subsequent uninterrupted visible PGO run reproduced the complete Bowser attack and reached Gateway Galaxy. The pre-transition checkpoint read 60.4 FPS, but the effects-heavy ship cinematic read 43.0 and 42.5 FPS; post-attack plaza traversal generally read about 44–53 FPS and reached 39.9 FPS under the ship. The castle transition was worse: independently captured points read 37.0, 39.4, 38.1, and 39.1 FPS. Gateway control then ran at 45.1–53.3 FPS, with visible directional movement and jumping. These title-bar samples do not establish a distribution, and the user terminated this scale-3 run when a tool pause looked like a freeze, but they are direct visual evidence of the reported stutter. Effects and transition workloads were roughly 35–38% below the 59.94 FPS reference target at that incorrect scale.

The live Gateway review separated three effects that must not be conflated. With the game fully foregrounded and stationary, the same state recovered to 59.9 FPS; active traversal read 50.3 FPS, while a partially covered/resized game window briefly read 22.3 FPS. Two independent 10-second CPU samples still found a real scene-specific stall: 1,450 of 7,401 and 1,629 of 7,873 CPU-thread samples blocked in `FramebufferManager::PeekEFBDepth` through `Metal::StagingTexture::Flush` and `MTLCommandBuffer::waitUntilCompleted`. Moving the pointer to a corner did not reduce the wait, so this is Gateway's active Star Pointer depth path rather than cursor placement. The run's `Config/GFX.ini` also records `InternalResolution = 3`; this evidence therefore cannot be labeled a 1x baseline. The next matched run must use scale 1, preserve the required RMG deferred-invalidation semantics, and compare the same Gateway route before any readback optimization is considered.

## Native-1× default and continuation

The matched continuation explicitly recorded frontend `resolution=640x528` and Dolphin `InternalResolution = 1`. Static title/story/Gateway views held 59.8–60.0 FPS; ordinary Star Festival movement generally read 49–54 FPS; Bowser arrival read 41.7–44.9 FPS; and castle abduction remained the worst observed native scene at 38.8–39.9 FPS. Gateway movement returned to 59.9–60.0 FPS. A five-second Gateway sample found 2,477/3,599 CPU-thread samples executing `StaticRecompCore::Run`, 2,236 below `chassis_dispatch`, and only 78 synchronous EFB-depth waits. Correct EFB semantics remain enabled; the readback is measurable but does not explain the effects-transition deficit.

Clean shutdown after 10,032.273 seconds reported 572,694 frames (57.085 Hz), 2,388,834 overlapping 128-frame DMA granules (30.479 kHz), 2,692 underruns, 48 backlog drops, 302 input transitions, `fallback=0`, and `smc_failed=0`. Of all frames, 57,975 (10.123%) were separated by at least 20 ms. This decisively improves the accidental scale-3 approximately-20-FPS floor but does not satisfy consistent reference cadence or audio continuity.

The root cause for fresh profiles was a frontend default of `1920x1080`, which maps to EFB scale 3 here rather than merely selecting a window size. Overlay `0012-native-resolution-default.patch` changes only missing-profile creation to `640x528`/scale 1 and adds regression coverage; the packaged seed's invalid `640x456` is corrected to `640x528`. Existing explicit choices are preserved. The frontend test, fresh-profile smoke, rebuilt app, code signature, and private-app audit pass.

The longer native-1× continuation narrowed the remaining defect. Bowser's attack commonly read about 31–44 FPS and the castle-abduction sequence sustained roughly 23–36 FPS, then Gateway dialogue and play recovered to about 60 FPS. In a clean active-Gateway sample, 5,143/7,038 CPU-thread samples were in `StaticRecompCore::Run`, 4,583 were below generated `chassis_dispatch`, and only 236 (3.35%) were in `FramebufferManager::PeekEFBDepth` through Metal staging-texture completion. The remaining native-1× cost is therefore dominated by distributed portable-AOT guest work, with EFB readback still a secondary cost rather than the freeze cause.

A second PGO experiment added an eight-sweep Gateway training run to the accepted opening profile. The instrumented trainer was correctly excluded from performance judgment; it produced private profile SHA-256 `a8f42ab70fab0b0da57643ed9b0499645d4218df02c15b6fc1f56ead69ac434`. A native-1× A/B then required matching 130 input transitions, projection `0xf8f6f1fa3d9e4c07`, `fallback=0`, and `smc_failed=0`. The accepted module produced 12,300 frames in 211.854 seconds (58.059 Hz), with 1,609 gaps at or above 20 ms (13.081%) and 47 underruns. The Gateway-trained candidate produced 11,888 frames in 205.587 seconds (57.825 Hz), with 1,592 such gaps (13.392%) and 47 underruns. Its -0.40% throughput change and slightly worse frame-gap share reject it; the accepted opening-trained PGO identity remains unchanged.

R53 used repeated short debugger stops only for read-only Mario/rabbit position telemetry while resolving the Gateway chase topology. A later live audit invalidated its two-catch save labels, but not its aggregate runtime counters: clean shutdown produced 312,648 frames over 5,682.418 seconds (55.020 Hz), 29.370 kHz DMA, 522 underruns, 107 backlog drops, and 42,324 gaps at or above 20 ms (13.537%), with `fallback=0` and `smc_failed=0`. The 8.209-second maximum graphics gap is caused by those deliberate stops, so R53 is failure evidence and not a valid optimization comparator. It does confirm that the old accidental-scale-3 18–20 FPS floor remained absent across the long native-1× session while residual pacing and audio continuity remain open.

## R62 packaged Observatory diagnostic — 2026-09-06

The genuine one-star NAND now enables `tests/fixtures/g6-observatory-save-load.json`: start at title, A+B, select Mario slot 1, Play This File, wait for Observatory, center the pointer and neutralize movement. Its exact encoded input has regression coverage. No savestate is needed.

R62 invoked the packaged `Contents/MacOS/GalaxyPad` bootstrap with explicit runner arguments and the packaged signed module. An isolated profile copied only Wii NAND/config, not StateSaves. Package audit passed; frontend resolution is 640×528 and InternalResolution is 1. The app's RMG.ini retains CPU EFB access, deferred invalidation, and arbitrary mipmap detection. The fixture visibly restored one-star Observatory. This validates the argument-driven packaged entry, not the default frontend/import UX or full D3 acceptance.

The run was never deliberately paused. Phase tracing and a ten-second CPU sample make it **diagnostic**, not an acceptance baseline. The final 30-second trace window, ending one second before the last event, recorded:

- VI/frame-end/presentation: approximately 55.135 Hz each.
- Frame-end interval median/p95/p99: 18.068/21.809/23.050 ms; 16.45% at least 20 ms.
- Present-completion interval median/p95/p99: 18.084/19.185/21.022 ms.
- DMA production: 230.027 blocks/s (about 29.443 kHz at 128 frames/block).

Window steady timestamps: `278375518256375` through `278405518256375`. The CPU-GPU thread had 7,199 samples; the dominant StaticRecomp Run subtree held 4,954, including 4,425 below chassis dispatch. Another 687 were in Run's own code. Work is distributed across generated chunks; no single guest chunk dominates. Whole-run diagnostics recorded **zero EFB reads**, so EFB stalls cannot explain this stationary-view deficit. This is not evidence that pointer-heavy scenes need no EFB work.

The final title read 54.5 FPS. Shutdown returned 0, fallback 0, failed SMC 0, 228 underruns/three backlog drops over roughly 190 seconds. Private evidence: `generated/runtime/observatory-r62.log`, `observatory-r62/phase.csv`, `observatory-r62/cpu-sample.txt`, and screenshot `RMGE01_2026-09-06_06-07-26.png`. No emulation/renderer/AOT policy was changed.

Follow-up R63 without instrumentation still failed: 50.377 Hz over 299.998 seconds, 837 underruns, zero EFB reads, and a user-observed 38.5 FPS dip. Concurrent host load prevents a clean observer-cost comparison.

R65 single-core follow-up reached the same visible Observatory and read 55.7, 55.9, then 54.9 FPS. It logged 147 underruns, zero EFB reads, and clean native-only shutdown. Its whole-run average is **excluded from the A/B**: the first fixture invocation happened before the title was input-ready, and a screenshot caught it still at title. A second invocation from the visibly ready title succeeded. Twelve transitions instead of six independently mark the extra input sequence. This supports further dual-core evaluation but does not repair the unmatched comparison.

Observatory fixture precondition: focus the runtime and capture/inspect the actual `Press both A and B` title before sending the sequence. Window existence or a fixed startup delay is insufficient. After the fixture, capture/inspect one-star Observatory before starting the comparison interval. If either precondition fails, reject whole-run timing as an A/B rather than retrying input and treating the aggregate as matched. The fixture regression verifies command encoding, not title readiness or successful navigation.

R66 supplies the corrected **single-core diagnostic baseline**. Inspected ready title at `06-32-08`, ran the fixture once, and inspected Observatory at `06-33-16`. No pauses or inputs during the measured interval. In `generated/runtime/observatory-r66/phase.csv`, select `279871552632333 <= steady_ns < 279931552632333` (exactly 60 seconds). VI, frame_begin, and present_done each count 3,330 events = **55.500 Hz**. Frame-begin spacing median/p95/p99 is 17.967/18.877/20.490 ms (nearest-rank percentiles of consecutive selected timestamps); 40 of 3,329 gaps are >=20 ms. Present completion p95/p99 is 18.898/20.474 ms. DMA counts 13,888 blocks = **29.628 kHz** at 128 samples/block. This is trace-on diagnostic evidence; compare only with an equivalently traced candidate before uninstrumented acceptance testing. No EFB reads, six input transitions, matching final projection, zero fallback/failed SMC, clean close. Host snapshot: game 100.9%, updater 37.6%, WindowServer 22.7%; unrelated processes untouched. Next obtain the dual-core interval using identical visual readiness and 60-second window rules.

R64 changed only the isolated profile to `Core/CPUThread = True`, retaining the same package/module/save fixture. It reached 59.910 Hz over 156.985 seconds and 31.980 kHz DMA, with six underruns and seven frame gaps >=33 ms. Final projection matches R63; fallback/failed SMC remain zero. This is promising but not a controlled speedup: duration and transient host load differed. Next repeat single-core under comparable conditions, then a longer dual-core movement/G5 regression if warranted. Do not promote defaults or G6 from this stationary sample. Do not revisit EFB duplicate suppression or replay Gateway as the default comparator.

## Required next measurements

- R81/R83 attack cinematic: investigate THP decoding, not just rendered fire effects. Exact RMGE01 code at 0x80453AAC counts leading zeros for signed coefficient extension, then 0x80453AC8/0x80453AD0 performs byte natural-order lookup and 16-bit coefficient storage. This sequence matches Petari THPDec.c's Huffman coefficient decoding logic (semantic correspondence, not reuse of RMGK01 addresses). The supplied PrologueA.thp header declares 59.94 FPS and 5,591 frames. Runtime identification of the exact playing movie remains indirect. The pinned CNTLZW intrinsic candidate is isolated and unpromoted; old PGO data mismatches changed function CFGs, so any speed comparison includes that compiler/profile consequence and may require retraining.
- perceptual/reference pitch comparison and broader music/voice/effects/cue coverage during the G6 path;
- an exact Metal active-gameplay phase trace and uninstrumented control using the new VI/frame/render/present/input/audio event stream, plus a focused O2 helper profile;
- pointer target identity and caller-resolved EFB traces in Gateway/Pull Star and other pointer-heavy scenes;
- CPU/GPU time, memory high-water, thermal behavior, transitions, and 60-minute soak;
- the same exact candidate on Simulator and physical devices at their later gates.
# R263 — luminance decoder extraction parked

The isolated 0x804534B4–0x80453B10 extraction passes 65,536 differential whole-chunk cases under O1 ASan/UBSan and O2 ThinLTO, including positive/negative cycle budgets and memory callbacks. It is not promoted. Pre-link ARM64 inspection with current profile increases the counted outer-plus-helper instructions from 12,233 to 23,084, with a mismatched-profile warning. Without profile data, original/candidate counts are 22,098/22,659, loads 5,302/5,327, stores 2,440/2,485. These are static counts, not dynamic cost or runtime speed measurements. No clear lower-work case justifies a module build. Scripts and exact evidence are recorded in JOURNAL R263; normal app and measured movie performance remain unchanged.
# R264 — paired direct-RAM loads: isolated candidate, not promoted

The type-zero load-only prototype reuses one checked eight-byte RAM mapping and preserves sequential lane conversion/assignment, with original fallback behavior. Unlike the parked store-pair prototype, this path has no reservation or journal bookkeeping. Actual inline-helper differential tests pass 100,000 random cases plus a CPU-alias case under ASan/UBSan. Six alternating five-million-call finite-float trials yield candidate/reference times .785–.793 for MEM1 and .714–.753 for MEM2. Earlier zero-filled trials yield .996–1.047 and 1.076–1.120 respectively. Payload sensitivity precludes a runtime gain claim. Complete transform-kernel validation and timing are next; normal app unchanged. See JOURNAL R264 and generated/psq-ram-pair-load*-r264.log.
# R265 — paired-load candidate parked after whole-kernel timing

All four reference/candidate sanitized/optimized complete-kernel oracle variants match (1,440 cases per variant; digest 882be09b1f38e9ad). Longer ABBA runs use 200,000 transforms per each of 12 kernel/pattern combinations, including CPU reset and yield dispatch. Aggregate control mean is 24574.445 ns, candidate 24557.7125 ns: only ~0.068% lower, smaller than pattern/run variation. Candidate text grows 16 KiB. This supersedes the isolated load-only microbenchmark as the decision evidence: park, do not build/promote this candidate. Logs and detailed coverage are in JOURNAL R265.
# R268–R269 — empty-relocation guard: first runtime pair

Same module/native1x/Metal/VI-only instrumentation and original R85 state/trigger: control3365VI in60s (56.083333Hz), candidate3424VI (57.066667Hz), +1.7533% in this pair. Worst intervals35.416792/22.1835ms respectively. Both visibly advancing movies, native-only, cleanclose, unchanged NAND. Unequal whole-run audio counts are not acceptance. First invalid control-r267 clock-origin window excluded; valid control is control-r268 using the recorder's exact C++ steady clock. Reverse-order fresh candidate/control remains required before deciding promotion. See JOURNAL R268/R269 for identities, windows and evidence.
# R270 — empty-relocation guard reverse-order confirmation

ABBA 60-second VI counts:3365/3424/3406/3342. Control mean55.891667Hz; candidate56.916667Hz (+1.8339%). Both candidate runs outperform both controls in these matched scripted windows. Second-pair worst intervals candidate21.515ms/control23.654125ms. Both saves unchanged, native-only, visibly advancing movies, clean exits. This supports retaining the guard, not 60Hz/audio/stability acceptance. Normal runner promotion awaits a diagnostics-disabled movie-completion and gameplay smoke. See JOURNAL R270 and runtime empty-rel-{candidate,control}-r270 evidence.
# R271 — guard runner promoted after uninstrumented movie completion

The tested candidate completed the opening movie into responsive plaza gameplay with all timing diagnostics unset, native-only execution, clean exit and unchanged NAND. Normal app now contains runner e86f2e09d27f69a41d1f10c2513cde14898557bc379fa787be013b5f0122b689; signed AOT module, wrapper and frontend are unchanged. Staged/final package audits pass, old app retained as GalaxyPad.app.previous.runner-r271. This promotes the bounded ABBA-supported improvement only; 60Hz, audio and broader stability remain unresolved. Normal-path launch/reload verification is next. JOURNAL R271 records scope and evidence.
# R274 — hardware widening parked

Normal-finite hardware widening passes complete-kernel differential tests, but its isolated conversion benefit does not survive complete-kernel timing. At200,000 repeats per kernel/pattern, thread-CPU ABBA means are control24771.121ns versus candidate24786.851ns (sum12pattern means), effectively tied with candidate~0.064% slower; code grows16KiB. Wall-time trials are noisy and insufficient to override this decision. Keep the prototype unselected; no module build or promotion. JOURNAL R273/R274 records exact FP-status coverage, source pins and logs.
## R380 — exact quantized-store scale, timing pending

Pinned CPU quantizer currently calls ldexpf(1,scale); GQR store scales are
signed six-bit values, whose powers of two are exact normal floats. Offline
psq_scale.py substitutes exponent bits only for[-32,31], retains libm outside,
and preserves the original conversion/multiply/clamp and sequential stores.
672816 quantizer cases per sanitized/O2 build match values/hostflags/errno
across4rounding modes/4types/321scales. Full-kernel1440case comparisons also
match all state/memory/callback/yield/fault digests; full repository suite passes.
Isolated finite scale-3 CPU ABBA is faster, but not whole-game evidence.
SavedPGO/ThinLTO strictFP whole-kernel CPU ABBA19629 currently running in
generated/psq-scale-kernel-bench-r380.log. Normal app/module untouched; no
FPS/audio acceptance. Poll same handle before judging or building a module.
## R381 — scale kernel timing supports an isolated module test

R380 benchmark19629 completed0. SavedPGO/ThinLTO strictFP CPU ABBA sums of
12pattern means: control25023.774/25113.937ns; candidate24531.101/24532.800ns.
Mean25068.8555 versus24531.9505 (~2.1417%lower); both229376byte text.
Same1of33kernel profile mismatch and unprofiled harness; not FPS evidence.
Isolated module build35607 changes only cpu.c quantizer scale factor; unchanged
control reuse verifies graph,1329objects,compiler/link inputs and exact549988hash.
Candidate compile has1of51profile mismatch, recorded rather than suppressed.
Runtime gain remains unproven; normal app unchanged, performance gate open.
## R382 — scale candidate first movie pair, not promoted

Same normal runner671729c6, explicit control549988/candidatec0021b9f module,
Metal1x, exact slot3/trigger, VI-only fixed60s, no overlapping build/profiler:
control56.233333Hz/CPUmean17.578963163ms/p99wall19.214042ms;
candidate56.966667Hz/CPUmean17.378905656ms/p99wall19.088209ms.
Approximately1.304%cadence gain and1.138%less CPU in this sequential pair.
Both dropped/invalid/reset0, visibly advancing movie, native-only clean close,
savea574unchanged. Whole-run audio counts are not fixed-window acceptance.
Require reverse-order comparison then gameplay regression before promotion.
Still below60Hz; full performance/audio/PRD goals remain open. Evidence:
generated/runtime/psq-scale-{control,candidate}-r381/window-summary.json.
## R383 — reverse order supports a small scale improvement

Same protocol/artifacts, candidate first:56.85Hz/17.390125526ms CPU;
control second:56.416667Hz/17.542845597ms CPU. Wallp99 19.3165/19.405333ms.
Reverse edge0.768%cadence/0.871%CPU; both orders favor candidate, combined
equal-window cadence means56.908333 versus56.325 (~1.036%gain). Both traces
complete/dropped0/invalid0/reset0, movies advancing/clean native-only exits,
unchanged save. No fixed-window audio acceptance; no third unchanged pair.
Next real-save gameplay/lifecycle and gameplay timing regression before
integration; installed app unchanged and reference60Hz/performance gate open.
Evidence: generated/runtime/psq-scale-{candidate,control}-r381/reverse-r383.
## R384 — candidate gameplay interval and lifecycle compatibility

Real106e save→Observatory→control smoke on candidatec0021b9f with normal
671729c6runner/Metal1x/VI-only. Fixed398648943739125..398708943739125:
3597VI59.95Hz, CPUmean15.669609589ms, wallp9918.299375ms, invalid/reset0.
After window, native pause/resume and subsequent movement visibly work;
cleanexit/saveunchanged/fallback0/SMCfailed0. Individual jump/Spin not captured.
Whole302s includes23.4spause and328late recorder drops. Append-only buffer's
last retained398801281769708 is92.338s after window end, so selected interval
is complete, not whole-run trace. Audio7underruns/11backlogs is not acceptance.
Next matched real-save control timing before integration. No app change.
## R385 — matching gameplay control

Real-save/load/control route matches R384 platform-edge camera, same normal
runner/Metal1x/VI-only. Control window399115807471083..399175807471083:
3597VI59.95Hz/CPUmean15.659909912ms/wallp9917.69525ms, dropped/invalid/reset0.
Candidate59.95Hz/15.669609589ms/18.299375ms: meanCPU~0.062%higher,
not a material cadence/mean regression; p99higher0.604ms, so no tail improvement
claim. Both clean native-only exits/saveunchanged. One gameplay pair supports
integration testing of the separately confirmed movie gain, not G6/performance
or audio acceptance. Unapplied exact-candidate source overlay prepared; normal
app unchanged. Evidence generated/runtime/psq-scale-gameplay-control-r384.
## R389 — tested scale optimization incorporated

Canonical module c0021b9f...c7939 reproduces isolated runtime-tested candidate
byte-for-byte, with identical generated game source, strictFP and savedPGO.
Cache reuse verified. Module-only audited promotion preserves671729c6runner;
signed installed module1fb635f7...1dc7a, previous app retained. R382/383 movie
gain (~1%) and R384/385 gameplay checks support this incremental change,
not full60Hz/audio/soak acceptance. Postpromotion suite and installed no-override
smoke remain required. No public release or mobile promotion.
