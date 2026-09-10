# Audio

## R876 packaged menu and config retention

Actual iPhone Simulator native menu: muted during startup, selected50% while
muted, stopped normally, relaunched, observed50%/checked mute, then unmuted and
stopped normally again. Runtime Dolphin.ini saved True/50 then False/50;
both runtime exits failed=0 and existing save unchanged. Signed stageO35wDl;
logs/screenshots generated/runtime/product-r876. This validates UI retention,
configuration delivery and these two stop paths, not backend measured gain,
audible silence, AV sync, arbitrary shutdown races or physical hardware.

## R875 main-volume candidate

Native Audio menu exposes Main Volume (0/25/50/75/100%) and independent Mute Game
Audio. Settings persist, clamp to0..100, and reject nonnumeric/nonfinite saved
volume. Muting never overwrites the selected level. Touch input clears on changes.
Startup config is set after Runtime::Create and before Run; AudioCommon applies
the configured gain before starting output. Live changes use the existing250ms
lifecycle tick and Core::QueueHostJob, checking session ownership, stopping and
current state before touching the stream. No UIKit access to the audio unit,
backend rewrite or buffer-size change. Shutdown discards normal queued jobs.

Simulator Release host build passed; isolated UIKit mobile-ui.cEj0ZR passed
menu selection/mute retention/clamps/corrupt preferences and existing UI checks.
These do not execute the audio host adapter or prove audible output. Candidate
not installed in the product container yet; next actual mute/unmute and
pause/stop/relaunch tests with unchanged accepted module. Speaker-specific
volume, output gain measurement, perceptual sync and physical-device gates open.

## R874 RemoteIO volume capability check

The native menu still lacks the PRD Audio group. Before wiring it, inspected
CoreAudioSound::SetVolume: it sets kHALOutputParam_Volume on RemoteIO output
scope/element0 without checking return status. A suspected unsupported parameter
was **refuted on iPhone17Pro Simulator/iOS26.5**: standalone probe creates the
same unit, sets0 before Initialize, then reads back0; both OSStatus results0.
No stream starts, no app preferences change, no audible-mute proof is claimed.

Reproduce with tests/remoteio-volume-probe.mm, clang++ arm64-apple-ios16.0-simulator,
Foundation/AudioToolbox, ad-hoc sign, then simctl spawn on the sole booted device.
Probe exits nonzero only on unit creation failure; inspect printed set/get status
before interpreting its result. It is not a product volume regression test.

Runtime's public API currently lacks volume adjustment; AudioCommon exposes
volume/mute helpers internally. Next implement a lifecycle-safe host/runtime
adapter and persistence, then test measured/audible output. No buffer, gain-DSP,
speaker-routing or backend rewrite is justified by this capability result.

## R791 completed delivery measurement

See MOVIE-AUDIO-R791.md for exact artifacts/identities and reproduction. Native
movie36.9s matched window:59.946 frame events/sec,1,771,520 nonzero output frames,
approximately48kHz delivery,zero new DMA underruns/backlog/full drops or short
callbacks. Post-movie21.5s:31.953 events/sec,104 underruns,only563,402 of1,032,192
output frames nonzero. This locates a continuing producer starvation problem,
not missing RemoteIO callbacks. Natural silence means nonzero fraction is not
itself an exact dropout measure. No perceptual pitch/AV-sync/device acceptance.
Movie completed5591 native calls/0fallback; clean stop/save unchanged. Do not
repeat this movie just to recover these counters. Gameplay native execution
cost remains the next performance lane; do not enlarge buffers to mask it.

## R791 live deployment and phase summarizer

R790 full suite passed (94352), core65936 and private app33555 built successfully.
Signed candidate85ffc100...bcc has one shared outputCounters global. Corrected
Simulator launch explicitly supplies unchanged module3acdcddc...bac0 and game
paths; first missing-module screen was an omitted development argument, not a
module defect. Current log generated/ios-runtime-r791b.log records RemoteIO48000Hz,
availability1, increasing callbacks and nonzero PCM. Slower scenes still record
DMA underruns, so callback delivery alone is not successful audio playback.

scripts/summarize-audio-window.py accepts explicit monotonic start/end bounds
from an observed uninterrupted phase. Requires two complete available snapshots,
rejects decreasing counters, non-monotonic time and gaps over7seconds. Reports
counter deltas, snapshot-time uncertainty and nonzero-frame fraction. Tests cover
boundary exclusion, reset/gap/availability rejection and rates; registered suite.
DMA enqueues count mixer granules, not PCM frames; do not label them sample Hz.
Caller must still verify scene/lifecycle boundaries. No listening, pitch or AV
sync claim is inferred. Targeted movie measurement remains in progress.

## R790 RemoteIO output telemetry implemented, not deployed

Opt-in GALAXYPAD_AUDIO_OUTPUT_DIAGNOSTICS=1 is read during CoreAudio Init,
before starting the audio unit. Shared OutputCounters records requested/mixed
stereo frames, nonzero frames, signed16 peak and short-buffer callbacks after
the existing Mix call. Buffer reads are bounded by min(requested, available);
null buffer produces zero delivered frames. The existing early return for no
AudioBufferList/buffers remains, so these are not an exhaustive invalid-callback
counter. No sample modification, buffer/rate/decoder policy change.

Callback work has no file I/O, clocks, allocations or mutexes. Required atomics
are compile-time lock-free; peak update relies on the single callback writer.
Start/reset is permitted only before that writer starts. Main-thread snapshots
are separately atomic fields, not a coherent transaction; compare complete
phase-bracketed windows, respecting lifecycle/reset boundaries. Counter
availability means instrumentation enabled, not audible output or Init success.

Header apple/shared/GalaxyPadAudioOutputCounters.h is mirrored byte-identically
into Common by canonical0030-remoteio-output-counters.patch, SHA
496f03aadca777baaefb46cf30842400c7051eeab54393b9dd9a475203448514.
Host audioCounters and optional five-second logs now include output availability,
callbacks/requested/actual/nonzero/short/peak fields alongside existing DMA
counts. With instrumentation disabled, output counts remain explicitly unavailable.

ASan/UBSan counter tests pass: silence, -32768 peak, short/null/zero buffers,
opt-out/reset,100000 callback writes with concurrent reads, and shared-storage
visibility between separate app/runtime translation units. Registered suite.
Host compile64813exit0 after bootstrap; main and RemoteIO actual Ninja-policy
syntax checks previously36110exit0. No linked app or live audio proof yet.

Bootstrap exposed older missing0026/0027 peel ordering, optional Simulator fetch
overlay handling, and unified-patch file-list parsing. Corrected these while
preserving installed overlay state on exit. Initial failures restored edits;
final46754 and repeat38174 exit0. Logs bootstrap-r790e/f.log. Reverse application
check for0030 and header parity pass. Full regression94352 is ACTIVE, log
generated/check-r790.log; poll same handle, do not restart on observation timeout.
Next complete regression, build private nativeTHP-enabled diagnostic candidate,
then one targeted movie/audio window. Perceptual sync/device/full PRD gates open.

## R789 mobile native-movie measurement gap and host counters

Retained R695/R696 log has RemoteIO initialization and first callback only;
it cannot establish continuous output rate, nonzero output or movie underruns.
Near60 frame-event/VI rates in movie-r696.json do not prove audio delivery.
Current Mixer.cpp already records DMA enqueue/underrun/backlog/full-drop events
through GalaxyPadDiagnostics. Unlike CubebStream.cpp, CoreAudioSoundStream.cpp
does not call RecordAudio. Do not interpret its zero output counters as silence
or as successful zero-error playback. Earlier G5/macOS evidence below is not
mobile acceptance.

Added main-thread audioCounters accessor under the existing runtime lifecycle
mutex, reading Runtime::GetDiagnosticsSnapshot. Within optional five-second
GalaxyPadLogFrameRateWindows logging, emit cumulative DMA counts with before/
after monotonic timestamps and explicit output_counters_available=0. No realtime
callback, mixer buffering, sample rate or decoder policy changed. Missing runtime
produces invalid snapshot, not valid zero counts. Counter deltas must stay within
one uninterrupted run/phase; snapshots across fields are not atomic transactions.

check-ios-host.sh95898exit0 with Werror; main.mm actual Ninja-policy syntax check
passes. Compile-only, not link/launch proof. Not yet installed or measured in a
new native movie. Next optional RemoteIO output-callback counters wired into
existing diagnostics, bounded/no file logging on audio thread, plus focused
buffer/count tests and reproducible source patch. Then one specifically
instrumented movie/audio run rather than unchanged opening/throughput replay.
Audio synchronization/perceptual/device and full PRD gates remain open.

Status: **G5 continuous delivery accepted; G6 gameplay cadence defect open**

R393 event-capable separate app real-save test: fixed60s Observatory window
59.933333VIHz,31997.8667guestframes/s,48000hostframes/s; exact zero running
underrun/backlog/full-drop events. Complete contiguous phase ordinals and
VI dropped0; whole47underruns/10backlogs match shutdown counts, all outside
window (44underruns before/3after). CPU15.611282ms mean,p99wall18.554708ms;
maxDMAgap17.425416ms/callback11.223459ms. Evidence/provenance in
generated/runtime/audio-events-r393. This is one quiet instrumented window,
not a stutter fix or perceptual/speaker/soak acceptance. Earlier transient
starvation and sustained movie deficit remain; no buffering policy changed.

R392: actual underrun/backlog/full-drop counters now also emit opt-in phase
events with the observed enqueue ordinal. Patch d0f1d941...bc89 and resulting
header9c11e94e...f772b are pinned; exact original/patched-header tests cover
sanitized and optimized counters, repeated events, opt-out and reversal.
Separate diagnostic app build and private audit passed, full suite passed;
runnerfa9adfa5...14102 provenance is recorded beside the app. Diagnostic
runtime recording is next; normal package and buffering unchanged.
Future window analysis must record event-capable runner/header provenance:
older traces without these hooks cannot establish zero interior underruns.
Enabled phase tracing adds clock/mutex/file overhead and is not acceptance.

R370 selected-package diagnostic: a no-pause Observatory60s window produced
~31995.7 guest frames/s versus48000 host frames/s and59.933VIHz, yet the last
underrun occurred about19.4s into active play. DMA production stalled69.36ms,
VI stalled89.06ms, and queue depth fell24→6→2 while host callbacks stayed
regular (largest11.38ms). A backlog correction followed at20.69s. Thus a
near-target mean rate does not rule out transient gameplay starvation.
Evidence generated/runtime/audio-active-r370 includes original phase.csv,
runtime.log, window-summary.json and stall-summary.txt. Trace overhead remains
a confound; this is localization, not performance/audio acceptance or proof of
host scheduling versus guest execution. No buffer/servo change made. Next
correlate CPU-time/wall-time VI tails with audio endpoints. Cleanexit/fallback0,
save unchanged; full perceptual, speaker, lifecycle and soak gates remain open.

The G4 and G5 Metal runs initialized Cubeb and sustained the title/file-select runtime without an audio initialization failure. The packaged configuration leaves the selected runtime's normal DSP-to-Cubeb path enabled. The instrumented package run delivered 16,864 callbacks and 8,634,368 frames, with 5,810,776 nonzero frames, peak magnitude 21,011, and zero Cubeb error states.

Main-DSP telemetry now includes queue depth, running-state underruns, latency backlog corrections, hard queue-full drops, producer gap, and first/last event ordinals. The corrected file-select run recorded 26,812 enqueues, 196 underruns extending through enqueue 26,179, one startup backlog correction, zero hard queue-full drops, and a 142.7 ms worst producer gap. Raising the Apple reserve from 80 to 120 and then 200 ms reduced but did not eliminate starvation; enabling the existing bounded ±2% Apple adaptive path also remained insufficient.

An identical-snapshot O2/O3 comparison then rejected compiler optimization as the fix. With the restored 80 ms macOS baseline and no adaptive resampling, O2 recorded 26,119 enqueues, 268 underruns through enqueue 26,037, and a 151.7 ms maximum producer gap. O3 recorded 24,734 enqueues, 270 underruns through enqueue 24,530, and a 131.4 ms maximum gap. Both reached the same file-select projection signature with zero runtime fallback or failed SMC handling. O3 reduced the single worst gap but produced 5.3% fewer DMA enqueues and did not reduce sustained starvation, so the accepted O2 module remains unchanged.

Aggregate active-span telemetry located the sustained fault upstream of Cubeb. The pre-fix Metal route ran 6,005 frame intervals in 118.698 seconds (50.590 Hz, 84.40% of 59.94) and generated 25,523 overlapping 128-frame DMA granules in 119.749 seconds (27.282 kHz, 85.25% of 32 kHz), while Cubeb requested 48.004 kHz. A late CPU sample then placed 215/1,000 main-thread samples in RMGE01's `SelectThread` idle poll at `0x804AB358`. Configuring StaticRecomp's existing core-timing idle skipper for that exact DOL restored 59.884 Hz and 31.946 kHz and reduced underruns from 186 to three.

The accepted follow-up keeps the reviewed DMA servo clamped to ±2%, enables it on Apple platforms, and targets 80% of the configured 200 ms reserve. The same full Metal/title/file-select/pointer route then completed 30,059 DMA enqueues across 120.433 seconds with **zero underruns**, one bounded startup backlog correction, zero queue-full drops, a 156.6 ms maximum producer gap, nonzero output, the unchanged projection signature, and zero runtime fallback or failed SMC handling. This proves continuous main-DSP delivery for G5; perceptual pitch comparison, Wii Remote speaker cues, interruption recovery, gameplay sound coverage, and soak remain later G9 evidence.

An ordinary headless run was inconclusive because the runtime deliberately selected Null audio and therefore never pulled the mixer. A default-preserving diagnostic override then kept Cubeb active with Null rendering. Under the same route, accepted O2 produced 27,104 enqueues and 216 underruns through enqueue 26,762, versus Metal's 26,119 enqueues and 268 underruns through enqueue 26,037. Removing Metal improved throughput and underrun count, but starvation remained sustained. Null also introduced a separate 1.80-second depth-peek/producer stall, so this is directional evidence rather than a renderer benchmark.

The first 53-minute G6 opening/gameplay exploration did not preserve the G5 cadence result. Cubeb continued requesting 48.000 kHz, but visible play generated only 26.210 kHz of DMA data and 49.081 video frames per second. The run accumulated 3,109 running-state underruns from enqueue 20,923 through 654,765, plus 31 bounded backlog corrections and no hard queue-full drop. Its 178.0 ms worst producer gap remained inside the configured 200 ms queue, proving that a still-larger retained reserve cannot repair the sustained 18.1% production deficit. A 90% target was therefore rejected and reverted to the G5-proven 80%; gameplay CPU cadence, not mixer policy, is the next investigation.

The long route above was subsequently found to use EFB scale 3 because frontend `config.ini` overrode `Config/GFX.ini`. At true 1×, accepted O2/4,096 generated 27.34 kHz with 271 underruns; O2/1,024 improved to 28.31 kHz with 254 underruns; O2/256 produced 28.19 kHz with 225 underruns. The 1,024 split is directionally better but still about 11.5% below the 32 kHz guest-production target. A 1,024 `-Oz` size experiment collapsed production to 18.04 kHz with 651 underruns and was reverted. These runs retain the proven G5 queue policy and show that the remaining fault is active-gameplay CPU throughput, not Apple callback rate or reserve depth.

No controlled pitch comparison has been recorded. Wii Remote speaker decoding/routing remains separate. The original G5 title/file-select audio route passed, but the later reproducibility result below reopens its stability claim; G6 continuous gameplay audio is also not accepted.

A later reproducibility check reopened G5 continuity. Immediately after the collision-safe C1024 rebuild, matched true-1× file-select routes recorded 13 underruns/31.46 kHz for C1024 single core and 30 underruns/30.52 kHz for accepted 4,096 single core. Enabling dual core as the only additional variable produced 26 underruns/30.74 kHz and was rejected. Every run retained the accepted projection/input signature, nonzero output, zero Cubeb errors, `fallback=0`, and `smc_failed=0`, so this is a cadence/stability regression rather than a routing or AOT-coverage failure. The fanless host had just completed sustained ThinLTO and its load average was still falling, but macOS reported no thermal or Low Power warning. A cooled-host reproduction and CPU sample are required before attributing the deficit or restoring G5 acceptance.

The cooled follow-up resolves that temporary reopening. A sampled diagnostic reached 31.70 kHz with 10 underruns and confirmed that `SelectThread` was no longer hot; floating-point conversion/multiply and paired-single helpers dominated instead. Because sampling adds overhead, the decisive control repeated C1024 single core at true 1× with no profiler or screenshot work. It produced 31,591 DMA granules across 126.470 seconds (31.97 kHz), **zero underruns**, one startup-only backlog correction at enqueue 53, zero hard drops, a 130.7 ms maximum producer gap, nonzero output, the accepted projection/input signature, `fallback=0`, and `smc_failed=0`. G5 continuity is restored; active-gameplay G6 cadence remains separately open.
