# Performance continuation, September 16

> Current checkpoint: [September 16 session close](SESSION-CLOSE-2026-09-16.md).
> The dated evidence below is retained; older build identities and next steps are historical.


## Acceptance boundary before the 7164 deployment

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

## Requested phone test: build 7164

The owner explicitly requested deployment of the latest performance candidate.
Build 7164 enables GALAXYPAD_AUDIO_CACHED_ENERGY=1 alongside the existing batched
search. Recompiled the actual retained mixer recipe against the maintained header,
replaced only Mixer.cpp.o in the 7162 core archive, and relinked the unchanged 7163
host objects. The exact signed game module is unchanged. Flags, source/header,
object/archive/module hashes and link map are recorded in the private receipt.
The new Synthesize symbol is present in the linked host. This is build activation
proof; no per-search runtime hit counter or demanding-gameplay speed gain is claimed.

Verified baseline 7163 on the rediscovered iPhone 14; same signer/entitlements and
profile compatibility; deep strict signature and iPhoneOS platform checks passed.
Backed up 54 save/configuration/preference files and installed in place. Readback
before launch found all 54 byte-identical. CoreDevice reads back build 7164.
The title screen rendered with one + control; startup frame windows reached about
60 events/s. Render scale1 and detailed logging1 remain enabled. This is startup
proof, not gameplay acceptance. The prior redacted runtime error event recurred.

Opening a fresh QuickTime mirror caused an audio interruption and runtime pause.
Closed the newly opened preview without recording, then relaunched the app to
clear that interruption. The existing 7163 artifacts and backups are preserved.
The resumed process stayed unpaused through the 18:12:08 log window, reporting
59.997 frame events/s with native_menu, ui_blocked and pause_requested all zero.
This remains title-screen evidence rather than demanding-gameplay acceptance.
Private evidence: generated/audio-energy-7164-20260916/ (build.py, receipt.json,
link.map, signature/platform results, preservation.json, installed app readback,
and initial/resumed device consoles). No release/default promotion.

The next major performance work must address game-body execution: the latest
profile's saturated thread and dispersed hot chunks make another small helper
rewrite insufficient. A complete connected hot routine must first beat current
native code under exact entry, timing and observer semantics; older scalar-state
and narrow-vector candidates are not re-enabled by this audio deployment.


## Owner's 7164 audio report and 7165 repair

The reported chopping was confirmed by new underrun deltas, not dismissed as
subjective. Measured input supply was below the minimum permitted stretch rate.
[Reproduction, rejected variants, repaired controller and 7165 deployment](AUDIO-SLOWDOWN-2026-09-16.md)
record the fix and its limits. The installed app preserves all 54 protected files.
No gameplay-FPS improvement is claimed from the audio repair.

The larger CPU pass also produced an [executed register-transfer cost probe](REGISTER-TRANSFER-PROBE-2026-09-16.md):
one checked span can reduce complete multi-register-load cost substantially,
while single-register cases regress. This is evidence for selective memory-work
fusion, not permission to blanket-rewrite loads. Dynamic attribution and complete
restore/return-region equivalence remain the next gates before a module build.


## Investigation reset after owner rejection

The owner reports days of work have not produced a perceptibly faster iPhone game,
and rejects 7165's audio quality under load. That is the current acceptance result.
The register-transfer experiment is not promoted and does not justify another phone
build. Stop presenting isolated speedups or lower diagnostic counters as user benefit.

The strongest architectural evidence remains the historical R424/R427 execution
comparison in PERF.md: about 16.68 ms AOT CPU work versus 6.83 ms reference execution
in a retained Mac scene, even with reference arena Fastmem=False (BAT fast lookup
still enabled). This is old, single-order, cross-engine evidence, not a controlled
current-iPhone ratio or a guarantee of 60 FPS. It supports investigating execution
contracts rather than repeating settings or dispatch-only changes.

ARM64-DIRECT-LOAD-R798.md already records why the existing offline exporter loses:
full callee-save prologues for tiny blocks, flushes at every memory instruction,
and store/return helper calls. Calling it a native backend does not remove that
work. Do not repeat its ten-instruction tuning. A meaningful successor needs a
whole connected region with values retained across the ordinary RAM path and
explicit slow-path state materialization, plus exact suffix/timing/callback exits.
Whole-region cost and dynamic coverage must support enough total work reduction
before another game-module/device candidate. This remains substantial unimplemented
compiler/runtime work; there is currently no proven iPhone-14 60-FPS solution.
