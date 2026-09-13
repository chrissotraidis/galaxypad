# Mobile performance pass 3

The experimental Apple preview was published before this investigation, as
requested. Release `v0.1.0-preview.1` and main commit `55123a4` contain the tested
mobile host, separate Mac package, notices and source supplement. All six GitHub
asset digests matched local files. Later experiments below are separate from that
release and have not been installed on physical devices.

## Resolution experiment

The same build 13 Simulator host and uninstrumented PGO module ran the verified
121-star Observatory scene on one dedicated iPhone 14 Simulator. The sequence was
2x, 1x, 2x internal resolution. Each scene was visually verified before a
90-second observation, with normal low-cost logging and no profiler attached.
Only full logged frame windows wholly within the observation were aggregated.

| Run | Internal scale | Complete window seconds | Frame events/s | Process CPU, one core=100% | EFB service ms/wall second |
| --- | --- | --- | --- | --- | --- |
| A1 | 2x | 79.30 | 44.69 | 118.99% | 239.06 |
| B | 1x | 61.90 | 45.01 | 119.18% | 238.20 |
| A2 | 2x | 78.50 | 44.41 | 117.18% | 245.38 |

All logged thermal states were nominal. The returning control followed a long
interruption, so this is not a tightly contiguous thermal-controlled benchmark.
The 1x result is about 1% above the two-control average: no substantial throughput
benefit is established. Do not reduce product image quality on this evidence or
claim this Simulator result predicts A15 hardware performance. The phone's last
retained log already used 1x.

EFB service remains around 24% of elapsed time in this scene. That counter combines
readback service and waits; it does not identify encoder CPU overhead versus GPU
execution or establish an independently removable cost. The next probe counts
contiguous staging copies without changing rectangles, depth values, ordering,
cache coverage or completion dependencies. It is a measurement experiment, not a
promoted optimization.

Private receipts: `generated/runtime/performance-pass3-20260913/resolution-aba/`
contains source/artifact hashes, before/after logs, visually checked scene images,
observation bounds and `results.json`.

## Hardware evidence available this pass

The fresh iPhone pull has six startup/menu frame windows and ends at 08:00 UTC;
its rotated predecessor has none. A GalaxyPad process is listed, but its current
foreground/game state is not established. This does not capture the owner's
reported 32 FPS gameplay and cannot justify claiming a new phone improvement.
The fresh iPad session contains the long guest-pause controller test; its near-60
frame windows are not a heavy-gameplay benchmark. Device work in this pass was
read-only: no install, launch, termination, settings or save changes.

## Research decisions

The runtime already enables CPU/render overlap and asynchronous hybrid shaders;
the shader worker default is one. Another worker cap would be a no-op. Real EFB
depth must remain enabled for Pull Stars. Previously rejected history reduction,
wait-primitive and vertex experiments remain unpromoted.

Three remaining hypotheses need measurements before changes: sharing blit encoder
setup across truly adjacent EFB copies; reducing FIFO worker idle spinning if CPU
residency proves it significant; and submitting pending offscreen commands before
drawable acquisition only when drawable waits actually leave work unsubmitted.
Apple's [Metal analysis guidance](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app),
[scheduling guidance](https://developer.apple.com/videos/play/tech-talks/110147/), and
[drawable guidance](https://developer.apple.com/library/archive/documentation/3DDrawing/Conceptual/MTLBestPracticesGuide/Drawables.html)
explain the distinct costs. They do not establish that any proposed change improves
GalaxyPad. The [EFB probe](../experiments/efb-batching/README.md) implements only the
first hypothesis's observation gate.

## Readback and worker observations

The initial 1x copy probe found 1,080 refresh copies across 360 copy-bearing
refreshes in one 120-field interval. Of these, 720 consecutive pairs retained
both resources with no observed intervening GPU operation: typical refreshes
contain three adjacent direct copies. This establishes an encoder-reuse
opportunity, not a measured speed improvement.

A separate 30-second thread CPU-counter capture of that instrumented scene
measured 21.93 CPU-seconds for the CPU thread (73.14% of one core) and 8.55 for
the video thread (28.51%). The video thread was waiting in 918 of 1,270 sampled
states. A simultaneous ten-second stack sample showed depth-readback completion
waits and vertex conversion prominently. Stack counts include blocked time and
must not be interpreted as CPU percentages. The thread-counter API's waiting
and busy-worker calibration passed before capture.

Empty cache-refresh polling occurs millions of times per second, but that count
alone does not establish dominant CPU cost. It also exposed a measurement issue:
the first probe published atomics every 64 refresh calls, including empty calls.
Its throughput is therefore not an overhead-controlled baseline. Publication is
being restricted to copy-bearing refreshes before timing comparisons. Neither
this instrumentation nor a sleep-policy change is promoted to physical builds.

The matched 2x scene produced the same 1,080 copies per 120 fields, but all used
an intermediate rendering path and none were contiguous: max run length one.
Simple encoder reuse therefore targets the 1x path only. It cannot be advertised
as an iPad 2x improvement. Both scene screenshots were visually checked; these
counter samples were from the initial probe and establish structure only.

An independent CPU-stack review attributed 3,715 of 7,402 self observations to
broad generated code, 806 to the native run loop, 334 to dispatch, 398 to all PPC
helpers and 1,634 to condition waits (including 1,566 float-future waits). These
are wall-stack observations, not CPU percentages. No single generated chunk
exceeded 149 self samples. This argues against repeating a tiny helper patch
without instruction-level coverage. Existing rejected quiet-loop, lookup,
rounding and fused-vertex experiments remain rejected.

## Direct-copy batching candidate

An isolated default-off candidate reuses a blit encoder only for adjacent direct
copies within one real refresh, with identical command buffer, source texture
and destination buffer. Rendering, compute, upload, flush, resource changes and
refresh exit close the encoder. Production sources and released artifacts remain
unchanged. The same binary supports batch-off/on timing with recording disabled.

The shared Metal helper passed 112 native Metal API Validation trials comparing
all staging bytes, spatially varying D32F values and untouched regions, including
partial bottom tiles and render/compute/blit/resource/command-buffer boundaries.
The harness used 336 control versus 224 candidate encoders across all cases.
ASan/UBSan scope and recorder contracts also passed. An independent source review
found no concrete lifecycle blocker. The harness explicitly closes encoders at
boundaries, so these results do not replace runtime integration or Pull Star
acceptance on hardware. Timing results follow only after the matched comparison.

### Timing result: not promoted

The same candidate binary, recording disabled, ran 1x off/on/off with the same
module and visually checked scene. Each observation was 90 seconds; the table
uses complete logged windows wholly inside those bounds. No profiler or compiler
ran during the observations, and all thermal states were nominal.

| Batch switch | Complete seconds | Frame events/s | Mean process CPU |
| --- | --- | --- | --- |
| Off A1 | 63.00 | 49.76 | 122.73% |
| On B | 63.70 | 46.63 | 121.18% |
| Off A2 | 62.30 | 48.51 | 123.44% |

The enabled case underperformed both controls. These short Simulator trials do
not quantify a hardware regression, but clearly provide no promotion evidence.
The candidate remains an inactive experiment, not a device update. A separate
recording-enabled integration run confirmed actual reuse: one interval had1,152
copies with384 encoders, retaining all copies. Metal API Validation was enabled;
no explicit Metal validation failure appeared. Generic privacy-redacted runtime
errors occurred, including a later count10; their cause is unresolved and this
run is not a claim of completely error-free gameplay. All three timing runs also
contained the baseline's startup generic error count1.

### New physical logs

A later read-only pull supersedes the earlier hardware-evidence limitation. The
iPhone now has a newer session ending12:21:50UTC. Four unblocked windows average
57.465 frame events/s; the slowest full window is52.453 with a sparse minimum
39.994. At1x and thermal state0, one15.9-second window adds56 DMA underruns and50
frame gaps>=33ms; CPU rises from89.10% to137.04%. EFB service in that interval is
about41.65ms/wall second, far below the Simulator's roughly240ms/s. The next
window has140.78% CPU and69.46ms/s EFB service. Simulator EFB-dominated reasoning
therefore cannot simply be applied to this physical phone session. Latest phone
state is inactive/paused/menu-blocked; visual scene identity remains unavailable.

The recent iPad interval through13:17:52UTC averages59.940 frame events/s over
1,115.7seconds at2x/thermal0 with no new underruns or>=33ms gaps. Its older rotated
file still includes a48.15FPS window and178 gaps over a much longer interval.
These logs do not prove heavy-scene stability or identify what scene was played.
Private current/previous logs and novelty comparison are retained in
`generated/runtime/performance-pass3-20260913/hardware-refresh-1315/`.
