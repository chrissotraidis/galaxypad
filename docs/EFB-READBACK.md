# EFB readback evidence

## R604 — common-clock completion gap and scope limit

[Apple GPUEndTime](https://developer.apple.com/documentation/metal/mtlcommandbuffer/gpuendtime)
specifies seconds relative to system mach time. Host probe now explicitly uses
mach_absolute_time/timebase, records domain and both GPU endpoints, and reads
GPU values after original wait. Matcher only compares same-buffer contained
handler and mach_absolute domain; missing/negative ordering stays unavailable
or invalid, not zero. Tests pass. Candidate9c59d87a…1a4ab0.

File-select armed12:31:13local.4096 records over5.699802s,198/198 waits matched,
all198 GPU-end/handler intervals ordered. GPU-end→handler-entry median0.731249485ms,
max4.325499991. Host wait median1.306229ms,total619.03521ms; GPU execution median
0.069666683ms. Handler-end→wait-end median0.0263125ms. Reported completion delivery
gap exists in this Simulator capture; logging in other callbacks and platform
reporting may affect it. Not proof of a specific driver/scheduler defect.

Important scope limit: summed measured waits are0.619035s of5.699802s (~10.9%).
This is an aggregate-duration/wall ratio, not CPU utilization or an FPS forecast.
It does not support readback waits as the sole explanation for the total cadence
deficit. A broader3s sample after cap retains substantial native dispatch work
(see JOURNAL R604). Prioritize whole-runtime balance before more callback probes.
No fake depth, wait removal, or lock rewrite justified. Clean stop12:32:54.247;
normal app restored/stopped. Full summary generated/metal-staging-summary-r604.json.

## R603 — matched waits mostly precede handler entry

Candidate e3f42670…a28c5b adds command-buffer pointer token to wait and original
render-handler spans. Same monotonic host clock. Match only a unique handler
with identical token contained within wait; this bounds pointer reuse and avoids
cross-command aggregate attribution. Tests cover ambiguity/reuse/old schemas.

File-select marker armed12:24:19local after visible settled scene.4096 records:
190 waits, all uniquely matched. Median wait-start→handler-start1.642437ms;
handler-end→wait-end0.0341665ms,max0.142458ms. Host wait median1.677187/max15.011875,
total710.834625ms. GPU190 valid median0.083895837/max0.485625002ms.3335 handler
spans median0.000375/max0.074084,total1.593148ms. Full private summary at
generated/metal-staging-summary-r603.json; runtime ios-runtime-r603.log.

Most matched wait interval precedes original handler entry. This is compatible
with queueing, GPU work ahead of the buffer, and/or callback delivery delay; it
does not distinguish them. Post-handler portion includes trace I/O and remaining
callback return as well as wakeup, not pure scheduler time. Do not subtract GPU
median or add unrelated medians. Logging/Simulator perturbation remains. Next
examine submission/queue timing before changing synchronization; handler mutex
rewrite and spin-polling are not supported by this evidence.

Runtime76911 native clean exit12:25:23.817 failed=0; normal app restored/stopped.
No FPS gain, physical-device evidence, or completed gameplay/stability gate.

## R602 — original render handler body is short

R601 candidate6140e4be…149faed ran on sole iPad Simulator with R600 settings.
Fresh marker armed12:18:06local after visible settled file select.4096 rows span
6.347338s. Handler3232 rows,total1.340432ms,median0.000375/max0.024041ms. Wait216
rows,total732.696535ms,median1.4488955/max13.885709ms. GPU216/216 valid,median
0.073770847/max0.387499982ms. Copy432,total10.224385ms,median0.0190205/max0.152791;
submit216,total0.030377ms,median0.000125/max0.000792ms. Summary is ignored artifact
generated/metal-staging-summary-r602.json; runtime log ios-runtime-r602.log.

This rejects expensive original render handler body as the dominant observed
wait explanation in this short capture, not every callback or driver path.
No per-command IDs:3232 handlers are not216 matched waits. Queue delay, callback
delivery and waiter wakeup cannot be separated. Handler logging itself happens
before callback return and outside handler measured span; it perturbs outer wait.
Do not subtract or add overlapping spans. Tiny handler duration does not prove
zero lock contention in other scenes. Preserve synchronization and depth reads.

Visible file list still intact before native Stop, clean exit12:18:57.898; normal
app restored/stopped. No performance gain or gameplay/stability acceptance.

## R601 — completion-handler probe prepared

Optional hash-gated MTLStateTracker render completion wrapper measures original
handler body (including its mutex acquisition), then records after lock release.
Existing staging wrapper and handler share process-wide4096 cap and arm gate.
Concurrent CSV regression validates unique contiguous IDs despite output ordering.
Candidate6140e4be…149faed built, not run. Next same-scene armed measurement can
reject expensive handler body as the main explanation if those spans are small.

Limitations: callback scheduling before entry is not measured. Handler I/O occurs
outside its recorded span but before callback return, so it can inflate host wait.
Handler and wait spans overlap and must not be added as independent costs. No
per-command correlation exists; do not subtract aggregate durations or infer lock
contention specifically. Only render handler is instrumented, not every Metal
callback. Preserve all existing synchronization until evidence supports a change.

## R600 — scene-armed file-select trace

Diagnostic marker gate now prevents title from consuming cap. Settled file list
visually confirmed, then unique marker armed12:05:32local. Candidate efcb2fb8…754ea
with same module/settings as R599.4096 records: copy_setup2050 total42.165969ms
median0.0174795/max0.216292ms; submit1023 total0.192304ms median0.000125/max0.020833;
wait1023 total3081.201533ms median1.710834/max14.111125. GPU1023 valid,0 unavailable,
median0.066875014/max0.324958353ms. Generic staging, not uniquely EFB; whole command
buffer GPU interval, not copy-only. Do not subtract medians or call this physical
GPU evidence. Logging perturbs subsequent operations; final stage sequence can
be truncated by4096 cap. Summary generated/metal-staging-summary-r600.json.

[Apple waitUntilCompleted contract](https://developer.apple.com/documentation/metal/mtlcommandbuffer/waituntilcompleted())
includes completion-handler completion, not GPU execution alone. Verified via
Apple documentation JSON after markdown endpoint failed. Actual MTLStateTracker
FlushEncoders handler takes backref->mtx, updates last_finished_draw and optionally
returns perf query results. Thus host wait can include handler work/lock waiting;
this trace does not attribute that cost. Next instrument those boundaries in an
isolated candidate, preserving existing waits. Tiny submit spans are consistent
with an already-submitted buffer but command status was not captured.

Runtime75316 clean native exit12:11:05.229 failed=0, normal app restored/stopped.
File list visibly intact at stop, but12:08:27.966 FIFO Unknown Opcode0xff logged:
stability remains unaccepted. No performance improvement claimed.

## R599 — Simulator GPU timestamps available at title

Installed R598 candidated5e0855f…b8f20, runtime74816/session59524 on sole iPad
Simulator. Same module/settings as R597, trace metal-staging-r599.csv. Title
visually confirmed before cap reached; no A+B or file select this run. This
confirms initial4096-record capture can exhaust at title, so R597 must not be
retrospectively called a settled file-select trace.

All1024 wait rows have valid completed-command GPU intervals,0 unavailable.
Reported GPU duration median.054687465ms/max2.174416673ms. Host wait median
.779208ms/max10.6555ms,total1568.959681ms. Copy setup2048rows,total30.976352ms;
submit1024rows,total12.572878ms. Full summary metal-staging-summary-r599.json.
These medians do not share interval boundaries and must not be subtracted to
compute scheduler cost. Reported command-buffer duration is not copy-only;
Simulator evidence is not physical-GPU performance. Nevertheless, title host
waiting is substantially longer than reported GPU work in this capture.

Next add explicit post-scene capture arming, then repeat on visibly settled
file select. Do not optimize the wrong scene from this availability test.
Clean native stop recorded in ios-runtime-r599.log; normal app restoration
follows. No save/gameplay or performance acceptance, no source change this run.

## R598 — GPU interval extension built, availability unproven

Reviewed installed Simulator26.5 MTLCommandBuffer.h GPUStartTime/GPUEndTime and
[Apple's timestamp contract](https://developer.apple.com/documentation/metal/mtlcommandbuffer/gpustarttime).
Read after existing waitUntilCompleted, require Completed status plus finite,
positive start and ordered end; zero/malformed/error results are unavailable,
not zero GPU work. Wrapper adds no wait; timestamp getter runs only when tracing
and below the shared cap, after the measured host interval.

CSV now adds gpu_valid/gpu_ms to the wait row. Summarizer reports GPU intervals
separately, preserves old traces as unrecorded, and rejects malformed durations.
Whole command-buffer GPU duration is NOT staging-copy-only duration, and may
start before host wait. Do not subtract it from wait to invent scheduling cost.
Simulator timestamp availability remains unverified until live capture.

Sanitizer tests cover zero/NaN/infinite/reversed/error rejection, valid interval,
unavailable-vs-unrecorded summaries and malformed CSV. Staged source compiles;
isolated candidate relinks. Object8aecad8b5b4baa788efca02fa24f969693f8bf4337a90d6d3bd2c211cb5407d6,
appd5e0855f3ed65ddb5f1fe418f3caf780f651be4705c39648e44aa4227e0b8f20.
Not installed/run; normal app ff855d69…cb34e4 remains installed/stopped.

## R597 — first staging trace: host completion wait dominates measured spans

Separate CMake build ios-metal-staging-probe uses explicit diagnostic object
before core archive. Link map assigns Metal::StagingTexture::Flush to object1
generated/metal-staging-probe/MTLTexture.mm.o, not original archive member.
Candidate SHA982e944795fbbe36d4c6a60f9a289a3e9c1c2ea1052438826d46276680128d2f;
normal app ff855d69…cb34e4 remained intact. Runtime74135/session45565 on sole
iPad Sim, same R594 game/module/settings plus GALAXYPAD_METAL_STAGING_TRACE.

Title→diagnostic A+B→file select visibly reached. Captured first4096 records
over approximately17.225s from first begin to last end. Trace has no scene/frame
marker: do NOT assert every sample is settled file select or EFB-only. No precise
depth result comparison made. Generic staging measurements:

| Stage | Count | Total ms | Median ms | Max ms |
|---|---:|---:|---:|---:|
|copy_setup|2048|32.114775|.011209|1.125084|
|submit|1024|14.617679|.008625|.103334|
|wait|1024|2225.350730|1.025584|18.755625|

Wait dominates these measured spans, not proof it dominates whole-game time.
Host wall wait includes GPU/Simulator execution, scheduling and wakeup; no GPU
timestamps yet. Per-record fflush can perturb subsequent work. Cap reached,
so this is bounded capture, not total run accounting or a benchmark speedup.
New summarize-metal-staging.py rejects empty/gapped/duplicate/invalid time/stage
records; wrapper/parser sanitizer tests pass. Evidence metal-staging-r597.csv,
metal-staging-summary-r597.json, ios-runtime-r597.log and candidate link map.
Clean stop11:52:30.616 failed=0. Next distinguish GPU command-buffer execution
intervals from host completion waits, with explicit unavailable/zero handling.

## R596 — isolated staging timing probe prepared

scripts/prepare-metal-staging-probe.py requires exact MTLTexture SHA
fcca51b4c765721fd242cb2f25620418bd3d98be69cbd82df1814985c7fb4ace and stages
generated/metal-staging-probe/MTLTexture.mm with three operation wrappers.
copy_setup encloses CopyFromTexture; submit encloses FlushEncoders plus
NotifyOfCPUGPUSync; wait encloses waitUntilCompleted. All original calls and
conditions remain. Wrappers do not change pixels, synchronization or return paths.
This is generic staging, not uniquely EFB; upload-related waits can appear too.

GALAXYPAD_METAL_STAGING_TRACE opt-in writes sample/stage/begin_ns/end_ns, bounded
to4096 records shared across wrapper instantiations. No clocks/output when off;
enabled logging/fflush happens after each interval and can perturb later work.
These are host wall spans, not GPU execution timestamps or unperturbed FPS.
Test covers exact-source rejection, preserved call counts, operation/clock/log
order, disabled clocks, shared cap and monotonic CSV. ASan/UBSan pass.

--compile reuses exact Simulator compilation database entry but changes source
and output to isolated generated paths. Object SHA
f6935f3fa231f654f0f8ec6100198d114b9e674ca2fbf3eadca15b9f4123adc0 built successfully.
No link/install/run yet; stable app and pinned source unchanged. Next isolated
link and bounded trace, then attribute service stages without inferring GPU-only cost.

## R595 — flush ownership checked, duplicate-wait shortcut rejected

Current Simulator compile_commands references vendor/dolphin/Source/Core, not
dolphin_legacy. Inspected PeekEFBDepth, PopulateEFBCache, RefreshPeekCache,
Metal StagingTexture::CopyFromTexture/Flush and StateTracker::FlushEncoders.
Synchronous population calls staging Flush and clears needs_flush; the following
PeekEFBDepth check does not flush again. Async refresh sets needs_flush and
submits copies, then first consumer waits once. Cached subsequent reads have
no additional Flush unless new pending work exists. Metal Flush also skips
completed command buffers and FlushEncoders does not submit a missing render
buffer. The observed wait is not evidence of an unconditional duplicate wait.

New tests/test-efb-peek-flush.py extracts actual PeekEFBDepth and compiles it
against bounded texture/cache doubles with ASan/UBSan. Tests one miss flush,
cached no-repeat, async-first-consumer wait, flag clear, returned value forwarding
and lower-left origin forwarding. Passes; added to check-repository.sh.
PopulateEFBCache's synchronous postcondition is modeled, not compiled; this is
caller control-flow coverage, NOT Metal/GPU/depth correctness or speed proof.

No readback optimization or default changed. R403/R405 submission-interval
experiments remain parked; avoid repeating them unchanged. Next useful metric
is actual Simulator cache-population/copy/completion service timing, distinguishing
required GPU completion from host encoder/setup cost; preserve real depth.

Status: **1× Star Festival baseline measured; no readback shortcut accepted**

R394: R393 post-file-confirmation15s window has mean EFB6.2676ms/VI
(4.262s total), mean wall22.0339ms/CPU14.7148ms,45.4VIHz and39underruns.
Quiet Observatory window in same run has EFB.4776ms/VI and no underruns.
This localizes an expensive route phase, not a GPU-execution diagnosis.
Actual timer wraps HardwareEFBInterface::PeekDepthInternal including blocking
AsyncRequests/future, video-side cache population and possible Metal completion.
Next use existing EFB_TRACE coordinate/value/PC/LR/frame data on that route;
preserve depth semantics. Phase tracing and host scheduling remain confounders.
Evidence generated/runtime/audio-events-r393/cluster-analysis-r394.json.

GalaxyPad retains Dolphin's required `RMG` defaults: CPU EFB access enabled, deferred invalidation enabled, and arbitrary mipmap detection enabled. The runtime never returns a constant, fabricated, or multi-frame-stale depth value for performance.

## Instrumentation

R401 stage split:21519 paired dispatch/depth rows with matching coordinates
and live callers; all four timestamps ordered. Whole dispatch80.959ms,
service3481.351ms,resume192.951ms (~92.71% service). Slowest11.078ms
pointer read is11.071ms service and only.007ms dispatch+resume. This localizes
this run's cost inside framebuffer handling, not request queue; service is not
GPU execution alone and prior40ms outlier did not reproduce. Existing early
command-buffer submission (actual default100draw interval) is the next scoped
experiment; preserve true depth/ordering/default until compared. Evidence
generated/runtime/efb-dispatch-r401/stage-summary.json.

R398 correction verified: live-context runner09353ce1 records16896reads,
allPC804ba23c, verified exact lwz r0,0(r6). Return addresses80385be0 and
8029e6e4 follow actual bl804ba228 instructions at80385bdc and8029e6e0;
zero unattributed rows. First group10262reads/2513.990454ms/max10.243458ms;
second6634reads/595.306540ms/max39.980625ms. Whole-run sums are not a
fixed-window benchmark. Coordinates and output-object offsets support
StarPointerPeekZ and TalkPeekZ behavioral matches to Petari, not region-address
substitution. Both depth consumers remain enabled. Evidence
generated/runtime/efb-context-r398/caller-verification.json; clean runtime/save
smoke passed, no stutter/audio/soak acceptance inferred.

R395 attribution correction: under AOT, existing guest_pc/guest_lr fields are
NOT reliable exact read callers. EFBInterface reads Dolphin's mirrored PPCState,
but HookExternalRead receives live CPUState and propagates only MSR before MMU
access. Common reported PC804a3c9c disassembles to mfmsr, proving it is not the
read instruction. Coordinates/value/elapsed remain valid observations; caller
claims require scoped live-AOT diagnostic context, not global state synchronization.

R395 added per-read trace reproduces loading route at60VIHz rather than45.4;
elevated R393 readback delay is intermittent. Matched15s has2529 selected reads,
843each at482,378 and0,0 and0,2; pointer reads544.399ms (~96.3% of565.412ms).
Maximum12.245625ms. Do not infer host scheduling or shader/cache causality.
Evidence generated/runtime/efb-loading-r395; clean exit/save unchanged.

The normal shutdown snapshot records color/depth peek totals, aggregate and maximum latency, the last coordinate/value, the number of presented frames containing peeks, and the maximum peeks in one presented frame. Setting `GALAXYPAD_EFB_TRACE` to an ignored output path additionally writes one CSV record per read:

```text
ordinal,frame,channel,x,y,value,elapsed_ns,guest_pc,guest_lr
```

Tracing is default-off because file output perturbs timing. `frame` is the completed-frame ordinal visible to the CPU at the read; `guest_pc` and `guest_lr` make SDK and caller sites separable in future scene inventories. The trace contains no disc data or save payload.

## Star Festival 1× baseline

The accepted RMGE01 O2/1,024 indexed module was run with Metal, Cubeb, no mods, native-class `640x528` frontend configuration, and the exact 44-transition Star Festival fixture. The run retained projection `0x190cf1d3666f1e56`, `fallback=0`, and `smc_failed=0`.

- 31,349 depth peeks and zero color peeks occurred in 12,377 presented frames.
- 2,165 frames contained one peek, 1,452 contained two, and 8,760 contained three; three was the maximum.
- Total measured peek latency was 6.840 seconds. Per-read latency was 0.079 ms median, 0.847 ms p95, 0.976 ms p99, and 7.644 ms maximum.
- Coordinates were not constant: the trace contained moving real pointer positions as well as `(0,0)` reads. The most frequent nonzero positions in this deterministic route were `(541,412)` and `(274,298)`.
- 1,473 reads repeated an earlier coordinate within the same presented frame. Every repeated coordinate returned the same depth, but the repeated reads accounted for only 17.799 ms, or 0.260% of total EFB-read time.

## Interpretation

Dolphin already batches the expensive work at the EFB-tile level. The first access populates and flushes the readback texture; later reads from that tile use the populated cache. The exact same-frame repeats therefore cost only a few microseconds and cannot explain the remaining gameplay deficit. Suppressing them would add correctness risk for no material gain, so no caching or P2/Co-Star shortcut is accepted.

The first real-coordinate read remains the relevant synchronization cost. Aggregate EFB time is measurable but substantially smaller than the native guest-execution bottleneck identified by the active CPU profile. Future pointer-heavy scenes must repeat this trace with caller LR resolution and target-selection evidence before any default-off experiment is proposed.

## Remaining matrix

- Gateway/Pull Star and Launch Star target selection;
- Star Bit collection and shooting with deliberate pointer sweeps;
- cannon, sling pod, bubble, talk interaction, cutscenes, and transitions;
- Observatory and dense-galaxy scenes;
- renderer recreation plus iPad Simulator/device behavior;
- matching target/depth outcomes against a reference implementation.
