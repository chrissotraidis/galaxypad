# Performance continuation, September 16

## Current acceptance boundary

Build 7163 is on the iPhone 14 with the UI repair; its core and module are from7162.
The user reports about 43FPS and no visible gain. Saves/settings were preserved.
Detailed frame logging is active. The source/Simulator pause-control repair is
verified and the visible physical + control was checked. Finger calibration,
sustained gameplay 60 FPS, thermal headroom and physical audio acceptance remain open.
[Deployment evidence](IPHONE-FEEDBACK-2026-09-16.md) records hashes/artifact locations.

## Completed hypotheses that must not be recycled

- Conservative state forwarding/dead-store elimination: optimized LLVM IR and
  objects identical in two hot chunks. No speedup.
- Scalar FP state batching: existing R777/R907 tests already tried value/local
  interfaces and longer resident arithmetic. Tested variants were slower.
- Blanket machine outlining: substantially smaller code, tested paths 2.53–4.56x
  slower. Rejected, not in the phone build.
- Void dispatch: equivalence and component savings established; no demanding
  gameplay improvement established. Keep its component/game distinction.
- Depth-read elimination: last 7162 windows only~0.44ms recorded per frame event;
  disabling correct reads would also break pointer interactions.

## New bounded experiment: reuse audio-search sample energy

The installed audio-tempo search already batches four candidate offsets. It still
computes each overlapping input sample's squared stereo energy repeatedly: up to
769 offsets times 128 samples, versus at most 896 distinct input samples. A new
private candidate computes each float squared-energy expression once and reuses
it while retaining the original ordered double sums and tie-breaking. This avoids
changing the audio window, search range, pitch, latency or producer accounting.
It adds 3.5 KiB fixed stack scratch only while searching; no allocation or class
layout change. It must beat the existing batched implementation, not an obsolete
scalar baseline, and preserve PCM and statistics in optimized/sanitized tests.

The shared principle is supported by [Lim and Kim's WSOLA paper](https://www.jask.or.kr/articles/article/DwDR/)
and [Chromium's moving-block energy calculation](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/media/filters/wsola_internals.cc).
Chromium uses rolling sums. Our initial candidate retains sum order because
changed rounding could change the winning offset. This is an independently written
experiment, not imported Chromium code. It is applicable to the shared audio path,
but not a substitute for reducing the saturated game thread's execution cost.

The maintained, default-off candidate passed 80 exact PCM/accounting/provenance
comparisons: 20 scenarios in scalar/batched modes, optimized and ASan/UBSan.
Fixtures include full speed, slowdown, stereo phase, transients, silence, noise,
alternating signals, very small values, stalls, flush/reset, recovery and bursts.
Nine alternating complete-Pull timing pairs against batched search give medians
120.618 ms control and 110.112 ms candidate over the 12-second synthetic scenario:
8.71% less elapsed processing time on this Mac. Earlier screens gave 9.31% and
8.90%. The fixture uses steady_clock, so these are elapsed processing durations,
not hardware CPU-cycle measurements. No game FPS or thermal gain follows.
Both modes compile for arm64 iPhoneOS. No class layout change.

Private evidence: generated/audio-energy-20260916/benchmark-report.json,
expanded-probe.log and device-compile.json. Production source is in the maintained
RecompCore fork; GalaxyPad pins it through ModernGekko. The source-identity gate
correctly rejected the changed header until its audited fingerprint was updated.
The full default repository suite passed after that update.
No performance candidate is installed or selected by default during this probe.

## Fresh 7163 physical CPU profile

QuickTime showed the Observatory with sleeping Mario and 33.0 FPS. Existing live
logs immediately before profiling report about 33 frame events/s, 1x, 145–146% process
CPU and serious thermal state. Attached Time Profiler to the running PID 4539 for
30 seconds without restart or gameplay inputs. Recording completed successfully.
Instruments GUI rounded weights:

| Thread or self-cost | CPU seconds |
| --- | ---: |
| Game CPU thread total |29.33|
| Video thread total |10.78|
| AudioRemoteIO total |2.85|
| Run self, within game thread |4.81|
| Native lookup self, within game thread |1.31|
| Void dispatcher self, within game thread |0.871|

The three self-costs total 23.84% of the game thread. They are not added to their
inclusive parents. Individual hot chunks remain dispersed (804B60A0 self 0.865s,
805170A0 self 0.767s,800180A0 self 0.652s,804330A0 self 0.595s). The narrower
ps_madds1 helper is only 0.278 s self here; it is not a credible sole 60 FPS solution.
These are samples and rounded weights, not instruction counts or removable costs.

At 33 FPS, 60 FPS requires 45% less elapsed frame time in a fixed-work model. Even
hypothetically deleting every sampled runtime/dispatch self-cost would leave
that model near 43 FPS. That is a sizing bound under simplifying assumptions,
not a predicted optimization. This is further evidence to prioritize reducing
translated game-body work, while the audio cache remains a smaller independent
CPU-pressure opportunity. Do not equate its 8.7% component gain with 8.7% game FPS.

Next game-thread gate: choose a connected hot region from the exact 7163 module,
retain actual timing/interior-entry/callback semantics, and prove fewer native
cycles for the complete routine before expanding a new lowering. Existing
scalar-value batching, FP-availability hoisting and narrow vector kernels remain
rejected: simply extending those implementations is not the next experiment.
The newer profile should guide selection rather than another unchanged FPS route.

Trace and source receipt: generated/iphone-7163-cpu-20260916/{cpu.trace,record.log,
gui-summary.json}. The xctrace sample exporter previously crashed; this pass uses
Instruments GUI values and makes no claim of exported per-instruction attribution.
