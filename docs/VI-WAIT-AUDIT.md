# VI hitch wait audit

## R372 — no-UI control still has a large tail

No UI inspection after120s window starts; graceful signal stop afterward.
At35.49s,90.357ms wall/19.776msCPU/3.520msEFB/0.379msidle/0DVD/gather/
0.028mswakeup. This refutes UI capture as necessary for large tails, not all
observer overhead or host interference. Mean59.9417VIHz and exact32000/48000
guest/host audio rates do not exclude jitter. Audio endpoint counters straddle
window and shutdown, so do not claim zero active-window underruns. Evidence
generated/runtime/audio-no-ui-r372/correlation.json and original trace/VI/log.
No new scheduling/graphics causation established beyond previous R303-class
localization. Stop unchanged tail probes; preserve synchronization semantics.

## R371 — audio endpoint overlaps a wait-heavy tail

Selected two-range module with existing diagnostic runner/phase+VI recording.
Exact60s window has59.95VIHz, CPUmean15.6748ms, wallp9918.2077ms; longest
23.44ms interval uses21.44msCPU. After that window, last audio underrun at
+78.10s overlaps84.773ms wall/20.071msCPU/48.486ms idleFlushGpu elapsed.
EFB0.613ms, DVD/gather0, wakeup0.031ms. This connects audio starvation with
the previously identified completion-wait boundary, not a new lost-wakeup
finding. End-of-run UI screenshot/query activity is a confound; no claim that
the GPU was executing48ms or the OS scheduler is defective. No policy change.
Evidence generated/runtime/audio-cpu-r371/correlation.json plus original CSV.
Next isolate observer contribution by omitting all UI queries/captures after
measurement starts and ending via existing graceful stop handler. Do not
repeat unchanged phase/VI wait captures or infer all incident causes from one.

## R307 — repeated observer delay, host-counter freshness limitation

87.51/83.38ms hitches again overlap independent observer gaps46.99/57.35ms.
Host snapshots cannot establish subsecond pressure: published Apple XNU
[host.c](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/kern/host.c)
rate-limits/caches host_statistics for third-party apps (1s window,2..10 quota).
Actual capture includes unchanged CPU counters across adjacent queries.
Query start/end is not counter freshness; reported short-bracket idle ratios
or zero swap deltas cannot exclude a short burst. Analysis now labels this.
No exact running-kernel source match claimed. Stop unchanged host probe loop;
need different scheduling evidence, not speculative synchronization changes.

## R305 — observer also delayed across the hitch pair

58.091209ms and53.341291ms VI intervals near60.84s contain7/10 snapshots,
all state1 (running/runnable). An independent read-only libproc observer has
a52.130417ms inter-query gap spanning the same pair, followed by14.570875ms.
This is stronger reason to inspect host scheduling/pressure than another
speculative graphics wait. It is not proof: observer sleeps can overshoot,
state1 is not on-core proof, and missing snapshots can hide waits.
Query durations are recorded; largest across window.302125ms, so distinguish
time inside a query from time between queries. No interpolation/state-duration
claims. No priority/timeout/notification change justified yet.
Evidence runtime/thread-state-r305/{states.csv,aligned.json,summary.json}.

## R303 — measured notification is small during87ms hitch

Audited runner856b2e69...5d2b0e, accepted module unchanged.120s real-save,
7189VI=59.908333Hz. At78.109318208s:87.0895ms wall,23.011CPU,
.307458EFB,.174345idle,.001498throttle,0DVD,0gather,.03421wakeup.
Wakup total135.974745ms/p99.039667ms,7188valid intervals: instrumentation
is active, but notification wait does not explain this incident. Stop repeats.
No scheduler/driver cause proven. Next bounded thread-state discrimination,
not another uncorrelated stack sample or synchronization-policy alteration.

## R300 — wakeup mutex mapped, slow-path observation chosen

RunGpu symbol0x10054bb84 plus sampled92bytes is0x10054bbe0.
The preceding call at0x10054bbdc resolves via Mach-O stub0x100cf6f40
to std::mutex::lock; following calls resolve unlock/notify_one. Matches
inlined sleeping-state Wakeup -> Event::Set. Not a timestamp attribution.
Notification-only observer tests preserve state/guards/call counts with zero
disabled clocks. Instrument this slow path, not every RunGpu invocation.
Default callers and Event handshake must remain unchanged; CPU ownership
must be explicit before writing the VI counter. Runtime wiring still pending.

## R299 — stack sampling identifies a wakeup mutex boundary

Bounded120s/10ms sample on audited gather runner, real-save active route.
CPU-thread tree has10679samples; four are under FifoManager::RunGpu+92,
std::mutex::lock and __psynch_mutexwait. Source RunGpu wakes BlockingLoop;
Wakeup can call m_new_work_event.Set, which locks a mutex to prevent lost
notifications. This is not a completion wait and is outside current gather/idle
counters unless nested under another measured path. Verify disassembly before
attributing the exact mutex; aggregate sample has no per-stack timestamps.

VI max249.867ms with small existing counters; sampling perturbation possible.
Do not infer exact hitch cause or remove Event handshake. Next CPU-only wakeup
elapsed measurement justified by observed stack, not another blind wait probe.
Evidence runtime/wait-sample-r299/stacks.txt CPU tree lines477..2175.

## R298 — non-idle gather wait does not explain captured75.7ms hitch

Isolated runner f4873728...9418a1, accepted module unchanged. Runtime wiring
and exported schema verified. Gather counter remains zero over120s active
real-save route (7185valid intervals). At9.093723s:75.698208ms wall,
17.926334CPU,0.395417EFB,0.386586idle,0.001374throttle,0DVD,0gather.
This boundary does not explain that incident. Do not claim GPU or scheduler
causation from remaining elapsed time. Stop gather-only repeats; next other
async blocking requests or bounded scheduler evidence.
Source default MAIN_SYNC_GPU is false; no explicit SyncGPU override found in
selected profile/default/RMG settings. This is not a runtime configuration dump.

## R294 — remaining boundaries and next measurement

Pinned source audit: CommandProcessor.cpp:356 calls FlushGpu in the CPU's
unlinked FIFO path; Fifo.cpp:398 waits on worker completion. Measure this
specific caller next, not every FlushGpu call (shutdown also calls it).
AsyncRequests.h:48 waits on a packaged-task future. VideoBackendBase.cpp:141
and :178 invoke it for performance queries and bounding-box reads outside
the existing EFB counters; :284 is state serialization, not used by R293's
real-save route. Fifo.cpp:556 also waits on the sync-distance event when
sync-GPU mode is enabled. Effective configuration needs verification before
excluding that path. None of these source locations proves runtime causation.

Use a separate CPU-thread-owned, VI-opt-in timer at the non-idle caller;
preserve original call count, guards and ordering. No timeout/priority changes.

## R293 — reproduced large hitch with zero DVD wait

Same diagnostic runner/module,120s active route. At82.174217s interval:
88.335125ms wall,23.071750ms CPU,0.334000ms EFB,0.308541ms idle,
0.001582ms throttle,0.000000ms DVD. All counters valid/no resets.
DVD-result waiting does not explain this captured hitch. It does not prove
the cause of older incidents or eliminate other disc-processing CPU work.
Do not subtract overlapping elapsed counters to label a precise blocked state.

Overall7189VI=59.908333Hz, DVD31.995288ms over120s; saveunchanged/cleanclose.
Stop repeated DVD-only captures. Remaining candidates include non-idle CPU
FlushGpu callers, async request future waits outside measured EFB, and host
scheduling. Next narrow coverage gap before changing any queue/priority/timeout.
Evidence generated/runtime/dvd-wait-r293/{vi.csv,summary.json,host-top.txt}.

## R292 — first instrumented real-save capture, no large hitch

DVD diagnostic runnerab221c...9c480/accepted module5c21...e91d audited.
Window360596065858166..360656065858166:3588VI=59.8Hz,3587valid complete
intervals. DVD elapsed total14.477747ms,p950.029208,p990.090457ms.
LargestVI25.556834ms:22.237125CPU/1.203542EFB/0.366717idle/
0.000209DVD ms. Prior55–59ms hitch absent; cannot rule out DVD during a
different incident. Counter is nonzero and remains valid across the window.
Clean-close/saveunchanged; no new performance acceptance or normal promotion.
Next one bounded120s capture, then park repeated captures if no large incident;
do not loop indefinitely on unchanged fast windows.

## R291 — canonical DVD counter wired; runtime evidence pending

Separate IdleWaitTiming member in PerformanceMetrics, configured from VI
recorder Enabled before CPU start. Measures only FinishRead WaitForData;
retains original queue Pop/map ordering. No observer/flight trigger attached.
DVD cumulative nanoseconds appended to bounded VI samples and post-join CSV.
Older schemas parse as missing/null, not zero. Source-derived queue contract,
header parity, export, parser missing/reset and bootstrap/wiring checks pass.
Pinned patches ModernGekko0022 and Dolphin0019; repeated bootstrap passes.
Isolated macOS package build running; no DVD wait measurement exists yet.
Normal app unchanged, no disc behavior/timing policy change.

## R290 — R289 remaining coverage gap: DVD completion queue

R289 hitches58.929/54.534ms are not explained by their small measured idle/EFB
durations. DVDThread::FinishRead waits for the requested result on the CPU
thread (`Core/HW/DVD/DVDThread.cpp`), caching out-of-order results in a map.
Its WaitForData call is outside existing EFB/idle/throttle counters. This is a
candidate boundary, not proof that the scene read disc during either hitch.

The existing phase logger is unsuitable for low-perturbation attribution:
Common/GalaxyPadDiagnostics.h:131 takes a shared mutex and writes line-buffered
CSV on each event. Do not enable phase logging merely to time this wait.
Video_OutputXFB uses nonblocking PushEvent in this source; do not label every
presentation submission a synchronous GPU wait. Query results still have a
separate PushBlockingEvent path. These facts do not exhaust all CPU waits.

Source-derived tests/test-dvd-wait-boundary.py wraps only the existing
WaitForData using IdleWaitTiming and compares unchanged result-loop behavior:
map-hit/no-wait, out-of-order queue, same pop/wait counts, disabled zero clocks,
enabled expected elapsed sum. ASan/UBSan passes. Fake-queue testing does not
prove real scheduling or concurrency behavior.

Next implementation: separate CPU DVD-wait timing member beside
GetCPUIdleWaitTiming in VideoCommon/PerformanceMetrics.h; configure before CPU
start under existing VI recorder opt-in, wrap exactly one original WaitForData,
append its cumulative elapsed field to VI samples/CSV, retain old-schema parser
compatibility, and package an isolated diagnostic runner through canonical
patches. No queue/timing policy change, no clocks in disabled mode, no file I/O
on the measured path. DVD field/runtime wiring is NOT implemented yet.

## R248 — graphics completion boundary

R247 captured 53.444174 ms inside the CPU idle FlushGpu call during a
74.399875 ms VI interval. This is localization, not proof of GPU execution time.

- `Common/BlockingLoop.h:125` executes the payload before checking its state.
  On the final execution it changes state toward DONE and signals `m_done_event`.
  The CPU Wait checks IsDone and otherwise waits under a single-waiter mutex.
- The `100` passed by `VideoCommon/Fifo.cpp` becomes milliseconds for the
  **worker's new-work idle wait**, not a timeout on the CPU completion event.
  Do not attribute the 53 ms interval to a 100 ms CPU timer or shorten it as a fix.
- `Common/Event.h` sets the atomic flag, passes through the predicate mutex,
  then notifies. The wait uses the same mutex and rechecks the flag. This source
  inspection does not expose an obvious lost-notification race; it is not a
  formal concurrency proof or a measurement of wakeup latency.
- The FIFO worker payload (`Fifo.cpp:287`) handles queued events, decodes FIFO,
  then calls VertexManager::Flush and RefreshPeekCache before returning.
  RefreshPeekCache (`FramebufferManager.cpp:536`) can populate cached tiles
  asynchronously and flush command buffers. Its async population omits the
  explicit staging-texture completion wait; do not label it synchronous just
  because it does graphics work. Other transitive draw/driver paths can still
  block. The CPU EFB peek counter does not time this entire worker payload.

Next discriminating measurement: correlate worker completion timestamps and
worker thread CPU/wall time with the already measured CPU idle wait. Prefer
bounded per-thread storage with reads only after both threads join; no locks or
file writes on the measurement path. Avoid timing every iteration of a busy
worker loop blindly: establish sampling frequency/overhead and preserve the
original state transitions and notification order. A late completion indicates
worker-side delay; early completion with a late CPU return indicates waiter
rescheduling or another wait iteration. Neither alone proves a driver defect.

Do not change synchronization, event semantics, timeout, rendering settings or
thread priority based only on this inspection. No runtime repeated in R248.

## R243 — 2026-09-07

R242 measured a 95.934541 ms VI interval with 20.374625 ms thread CPU,
0.401625 ms EFB elapsed and 0.001374 ms throttle elapsed. This excludes those
measured EFB/throttle durations as explanations of most of that interval, not
all graphics waits or host scheduling. No synchronization change is justified yet.

Source paths below are relative to `ref/ModernGekko/vendor/dolphin/Source/Core`.

| Boundary | Gate and evidence | Implication |
| --- | --- | --- |
| `VideoCommon/Fifo.cpp:535` WaitForGpuThread | `MAIN_SYNC_GPU` defaults false (`Core/Config/MainSettings.cpp:207`); captured Config and packaged RMG settings have no override | Not the leading normal-profile candidate; no live effective-config trace yet |
| `VideoCommon/Fifo.cpp:147` SyncGPU | Waits only with deterministic GPU threading; default mode auto, Core::UpdateWantDeterminism derives want from movie input recording/playback or netplay | Ordinary save route used neither; game cutscene is not Dolphin Movie mode |
| `VideoCommon/Fifo.cpp:391` FlushGpu | Waits in ordinary dual-core, non-deterministic mode; independent of SyncGPU option | Remains a plausible unmeasured wait |
| `Core/CoreTiming.cpp:574` Idle | `SyncOnSkipIdle` defaults true (`MainSettings.cpp:67`), no captured override; calls FlushGpu before zeroing downcount | Direct route into that wait |
| `Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp:165` | Calls Idle when guest PC equals configured idle PC; profile explicitly sets `0x804ab358` | Idle shortcut provides an enabled source route; invocation during a particular hitch still unmeasured |
| `VideoCommon/CommandProcessor.cpp:356` | GatherPipeBursted may FlushGpu for unlinked multibuffer FIFO with pending bytes | Other CPU caller; preserve correctness condition |
| `Core/HW/DVD/DVDThread.cpp:249` | FinishRead waits for result queue | Still possible; no aligned disc-wait measurement yet |

`Common/BlockingLoop.h:53` Wait first checks IsDone, then takes a wait mutex and
waits on a completion event. R237's CPU sample contains three samples in this
BlockingLoop wait, separately from the EFB future wait. Sampling/inlining does
not establish which caller, exact elapsed cost, or correspondence to R242 hitches.

## Next bounded experiment

Measure elapsed time around **the existing CPU-thread idle FlushGpu call**,
using an opt-in bounded/cumulative counter captured by the existing VI recorder.
This narrows one active route without instrumenting every BlockingLoop waiter
or timing graphics-thread/shutdown calls. Disabled mode must avoid clocks and
counter updates; enabled mode must preserve exactly one original FlushGpu call.
Use canonical patches, focused disabled/enabled/reset/export tests and an
isolated runner. Do not change idle skipping, SyncOnSkipIdle, EFB access, FIFO
gates, or pacing. If the counter remains small through a hitch, inspect other
CPU waits or obtain lightweight scheduling evidence instead of repeating it.

The accepted app and game module are unchanged. No mobile performance or G6
acceptance claim follows from this audit.
