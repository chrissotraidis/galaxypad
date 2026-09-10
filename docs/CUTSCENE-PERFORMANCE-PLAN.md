# Cutscene performance: active work queue

## Current priority — R736 shared FP/state after direct-call trial

Guarded direct-call variant is not promoted: first CPU/VI pair improved5.66%,
reverse pair regressed, and instructions/VI rose in both. No reproducible>=8%
gain established. Close this specific design, retain evidence, keep product
binding disabled. Next shared floating-point/state-materialization overhead
with preserved accuracy/observers/exceptions; then identified mobile fallback.
No more direct-call micro-tuning or repeated same-scene benchmarking by default.
All runs cleanly stopped, no simulator booted. R724/R736 records and exact
artifact identities are in DIRECT-CALL-EXPERIMENT.md. Earlier live PIDs below
are historical, not current runtime state. Full original PRD remains unchanged.

## Earlier priority — R711 architectural reset after independent review

The authoritative immediate queue is now REVIEW-RESPONSE-2026-09-09.md:
guarded cross-chunk calls first, shared FP/state work second, identified mobile
fallback overhead third. Matched CPU time/VI, instructions/VI and dispatches/VI
drive decisions; retain visible correctness and frame-time checks. No unchanged
plaza sampling, lookup micro-tuning, movie replay or undo-memory loop by default.
The supplied review and its corrected quantitative/safety claims are recorded.
The old unsafe-direct-call flag remains refused in the product pipeline.
Current candidate d34fe135/PID75679/session11407/logios-runtime-r710b.log.
Live undo-byte release check remains unverified and is parked, not completed.

## Runtime continuation — R707

Candidate84f0fe05 plaza checkpointBFA5 is now same-process AND clean-restart
restore-proven, with visible movement response. CurrentPID71970/session84246,
ios-runtime-r707.log, soleSimulator unchanged. Use this scene for current-build
experiments; cross-build compatibility remains intentionally refused. Restores
retain upstream undo-load buffer, unlike the original no-restore R704 baseline.
Clean shutdown of old66439 flushed nativeTHP5591/0; no need to replay PrologueA
just to recover its final counter. Later movie after restored state is untested.
Original performance/first-play/device/audio and full PRD gates remain open.

## Current priority checkpoint — R704

1. Target representative gameplay CPU execution first. Visually bracketed plaza
   capture:37.62 frame-event Hz, speed0.614–0.687, CPU thread86.50% of one core,
   Video37.66%, no compression/swapout growth. Actual CPU-time counters establish
   substantial computation, not which functions dominate or which cores execute.
   Use current module/current scene evidence, not old native profile percentages.
2. Keep synchronous graphics/readback attribution second; neither all slowdown
   nor all non-CPU time is established as EFB waiting. Preserve depth correctness.
3. Require before/after visual checks. An idle controller-disconnection warning
   raised event cadence to51.38 in the first capture; that is NOT gameplay gain.
   Native movie progress remains preserved; do not restart opening microbenches.

Full original PRD/SunPad/device/audio gates unchanged. Same66439/84f0fe05 live;
candidate plaza checkpoint saved but restore untested. Details STATUS/JOURNAL R704.

## Current priority checkpoint — R696

Same-session evidence now separates workloads: native PrologueA near full speed
(59.92 frame-event Hz, VI59.94, speed~1), followed by stationary invaded plaza
35.51 frame-event Hz and speed0.57–0.64. Movie visibly returned to gameplay.
Keep PID63074 and this useful scene; no further opening restart for routine
instrumentation. Next validate a same-build development checkpoint here, then
target gameplay CPU work/synchronous graphics waits with bounded measurements.
The R693 graphics failure did not reproduce; preserve armed failure logging,
but do not suspend all progress for unchanged crash retries. No graphics-fix,
audio-sync, actual-display cadence or full-performance acceptance claim.

## Current priority checkpoint — R694

1. Resolve the R693 malformed XF graphics-stream failure before timing another
   candidate. Failure-only logging now captures the decoder's input-span offset
   and at most 32 bytes before/after the failing command. Preserve the assertion;
   the byte window is context, not proof of the corrupting producer.
2. Correlate visible scene transitions with VI rate, emulation speed, frame-event
   windows and bounded host deltas. R693 speed estimates of 0.33–0.56 confirm
   simulation slowdown. Frame-event counts are NOT display-completion counts.
   Separate CPU work from synchronous waits before choosing an optimization.
3. Retain native THP progress: both movies completed with 12667 accepted calls
   and zero fallback in the previous long run. This is not audio-sync, exact
   presented cadence or all-output parity acceptance. Avoid repeating the opening
   merely for timing-only changes; same-build development checkpoints still need
   actual save/restore validation after the graphics failure is understood.

No control-layout work is on this immediate queue. Original PRD, SunPad shell,
physical-device and first-play acceptance requirements remain unchanged.

## Current priority checkpoint — R682

Native opt-in movie decoding has now shown complete first-movie5591/0 acceptance,
near60FPS windows and visible return, plus castle-to-Gateway transition. Audio,
exact cadence/duration, broad output parity and device acceptance remain open.
Do not repeat opening navigation or decoder microbenchmarks as the default task.
Current gameplay is still~31FPS at Gateway. The new bounded scene capture records
zero swap/compression growth over30s, so that interval does not justify blaming
disk swap. Next performance work targets measured CPU execution and synchronous
graphics/readback costs, with output/depth correctness preserved. Keep the current
live first-play state instead of restarting it for routine instrumentation.
Use scripts/capture-live-slowdown.py for paired scene/log/host evidence; no build
or profiler during its baseline window. Full PRD and movie/audio gates unchanged.

Updated 2026-09-08, R653, at Chris's explicit request. This adjusts priorities,
not the original PRD, supported input, no-JIT boundary, or G0–G15 completion bar.

## Evidence and diagnosis boundaries

- The local PrologueA.thp header declares59.9399986FPS,5591frames and93.2766s.
  Slow playback cannot be dismissed as an intentional30FPS movie. File247732512
  bytes, THP1.1. Match actual playback source before using this as an end-to-end
  duration oracle; do not conflate presented counters with decoded source frames.
- Mobile byte-cache default is deployed and activation-proven. Earlier sequential
  enabled40–41FPS versus disabled35–36FPS supports an incremental change, not
  complete performance or a perfectly controlled percentage estimate.
- Latest default run drops to9.12,12.21 and6.41FPS before recovering toward34FPS.
  On this16GB host, top observed15GB used, about7.0–7.7GB compressor; swap counters
  increased across observations. GalaxyPad reported393MB footprint/316MB compressed.
  Codex Renderer1598MB and ChatGPT1249MB were larger processes. These snapshots
  motivate interval measurements; cumulative swap totals alone do not prove cause.
- Historical R406 native profile attributed43.77% of samples to coefficient and
  transform regions. It is an older module/native measurement, not current mobile
  attribution. Existing THP policy extracts generated instruction kernels; it does
  not replace the whole video decoder with a native media implementation.
- Reference sources: ref/petari/src/RVL_SDK/thp/THPDec.c exposes THPVideoDecode;
  ref/petari/src/Game/Screen/THPSimplePlayerWrapper.cpp calls it with Y/U/V buffers
  and work area, then updates frameNumber. Exact DOL identity/ABI and all side
  effects must be audited before replacing this boundary.
- FFmpeg's primary source has a distinct THP decoder in its MJPEG implementation:
  https://ffmpeg.org/doxygen/trunk/mjpegdec_8c_source.html . It is a candidate
  benchmark/reference, not yet an approved dependency or pixel-parity proof.
  Do not assume direct hardware VideoToolbox support for THP or transcode assets
  by default. Tooling/licensing and output semantics need explicit review.

## Ranked actions

1. **Whole-frame native decoder feasibility and isolated benchmark.** Read the
   player/decoder contract, identify exact call boundary and representative local
   frames. Benchmark native decoding without game or Simulator running. Compare
   full output planes/layout and errors against the existing decoder, including
   rounding, chroma, tiling, work memory and observable guest state. Target ample
   headroom below the16.68ms source-frame budget, not merely a faster inner loop.
   Pin/license public tooling; protected inputs and outputs remain local. A native
   benchmark that cannot meet cadence rules out that candidate before integration.
2. **Playback pipeline and audio synchronization.** Add bounded per-stage timings
   only where needed: disc/read queue, decode, buffer availability, upload, present
   and audio producer/consumer. Measure decode-ahead depth and starvation. Preserve
   source cadence, audio pitch/sync, guest clock, skip/cancel/end events and return
   to gameplay. Do not fix slow playback by speeding guest clocks or skipping work.
3. **Host-stall isolation.** Capture simultaneous short-window frame gaps, CPU time,
   compression/decompression, swap I/O and competing process load. Use a paused or
   stopped game for standalone work; no concurrent builds. Ask before stopping
   unrelated software. Keep bounded buffers/memory; do not accumulate videos or
   compressed-frame caches without limits. Recheck physical iOS when device/signing
   become available; Simulator timing is not hardware acceptance.
4. **Measured graphics costs, then broader gameplay.** Reduce redundant copies,
   conversion/upload or synchronous waits only if measurements implicate them.
   Historic movie tests showed zero EFB activity, so world-pointer EFB fixes are
   not presumed to fix this movie. Profile dense gameplay separately afterward.

## Execution and acceptance

Next concrete action (R654): native throughput feasibility passed. Establish the
existing decoder's complete-frame output oracle and exact guest-state contract,
then compare native output, including tiled layout and IDCT rounding. Do not wire
in FFmpeg based on throughput alone. No new title/navigation benchmark loop.
Current diagnostic runtime remains stopped; save unchanged.

Promote only after output/contract tests plus complete in-game movie playback at
correct duration/cadence, audio sync/pitch, bounded memory, no cumulative drift,
and clean gameplay return. Then regression through save/reload/lifecycle and the
original platform matrix. A standalone speed number, tiny helper test, screenshot,
or successful compile cannot close the PRD performance gate.

## R654: isolated native throughput result

Built an isolated ARM64 FFmpeg 8.0.1 command-line benchmark from the official
https://ffmpeg.org/releases/ffmpeg-8.0.1.tar.xz archive. Download SHA256:
`05ee0b03119b45c0bdb4df654b96802e909e0a752f72e4fe3794f487229e5a41`.
This records the HTTPS download identity; no independent release-signature
verification was performed. Source LICENSE.md and configure report LGPL 2.1+;
no GPL/nonfree/external codecs enabled. This is private benchmark tooling, not a
new shipped product dependency. Source/archive/build stay under ignored
`generated/tools/ffmpeg-thp-r654/`.

Configure: `--disable-everything --disable-autodetect --disable-network
--disable-doc --disable-debug --disable-ffplay --enable-ffmpeg --enable-ffprobe
--enable-demuxer=thp --enable-decoder=thp --enable-protocol=file
--enable-muxer=null --enable-encoder=wrapped_avframe --enable-filter=null,anull`.
Built with Apple clang 21.0.0, four build jobs, no game/Simulator; compilation
completed before measurement. FFmpeg ARM64 executable SHA256:
`9edb4b47d240075659882cd5be18356b3f6ab8c15b16228e57bb35c1c3c2a9c8`.

Reproduce from repository root:

```sh
python3 scripts/benchmark-native-thp.py \
  --ffmpeg generated/tools/ffmpeg-thp-r654/ffmpeg-8.0.1/ffmpeg \
  --movie generated/extracted/run1/files/MovieData/PrologueA.thp \
  --frames 5591 --runs 3
```

The harness uses one decoder thread, one filter thread, no audio, passthrough
timestamps, null output and a 120-second per-run timeout. It fails on decode error
or unexpected frame count. No decoded movie files are written. ffprobe identifies
640x368 full-range YUV420 video, 5591 frames / 93.276612 seconds; audio is stereo
32kHz ADPCM THP but was not decoded in this measurement.

| Run | Frames | End-to-end process wall time | Throughput | Wall ms/frame |
| --- | ---: | ---: | ---: | ---: |
| 1 | 5591 | 4.2196s | 1325.0 FPS | 0.7547 |
| 2 | 5591 | 3.9718s | 1407.7 FPS | 0.7104 |
| 3 | 5591 | 3.9850s | 1403.0 FPS | 0.7128 |

All three exited successfully. Log: `generated/native-thp-r654.log`. These are
whole-movie averages including demux/read/CLI overhead, not frame-tail latency.
FFmpeg's maxrss label is not used: its getmaxrss multiplies ru_maxrss by 1024,
which makes its printed units unsuitable for interpreting Darwin memory usage.

Decision: native software THP video decoding has substantial average throughput
headroom on this host (source budget about 16.68ms/frame). Proceed to correctness
and integration feasibility, not further inner-kernel tuning. This is not a
matched speedup versus the running game and does not eliminate host stalls,
prove output equivalence, include audio/upload, or prove Simulator/device cadence.

## R655: exact decoder boundary audit

Extended `scripts/audit-thp-boundaries.py` to include header parsing, complete
video decode, decompression, initialization and audio. Exact DOL hash is checked
before reading; each range ends in blr. Entry/decompression byte hashes and the
call edge are asserted. Fresh output: `generated/thp-contract-r655.json`.
Petari's symbol file is RMGK01, not our RMGE01: those symbol addresses are not
valid hook addresses. The matching RMGE01 instruction flow is:

- THPVideoDecode correspondence: 0x804514ec, size0x2c0, SHA256
  `8573a49a6cb7b069206289b877cda05a8492588d503eaeb4616d493ab12056a2`.
  Generated instructions preserve r3=input,r4=Y,r5=U,r6=V,r7=work in r26–r30.
- Call at0x8045174c goes to decompression0x80452398, size0x104, SHA256
  `9f3d32a0928d77d0d1a761e4ba784e125ae8fba5f99063d446a3367d5cd15464`.
  Direct calls match bitstream prep and the512/640/general MCU-row routines.
- Initialization correspondence0x80454820; audio0x804548bc is separate.

Integration candidate: retain guest header validation/setup and player flow,
substitute full-frame native decompression at the inner boundary. This avoids
reimplementing all validation returns at the outer function, though FFmpeg needs
the original compressed-frame start and size, not just the advanced entropy
cursor. No hook has been installed. Original path must remain available until
eligibility, bounds and output correctness are proven.

Reference contract details requiring oracle coverage: null input/output/work
return25/27/26; disabled locked cache28; uninitialized29; malformed markers and
header-table errors; work area32-byte alignment and table state. Decompression
sets destination cursors, changes entropy/DC predictor/restart state and uses
locked-cache row transfers; quantization registers are saved/restored. Output
is not directly interchangeable with FFmpeg's linear planar buffers. The MCU
path writes four8x8 Y blocks and one U/V block per16x16 region, then row transfers.
For PrologueA640x368, that is40MCUs/row and23rows, with320x184 chroma planes.
IDCT uses paired floating-point operations and quantized stores; byte parity
against a generic integer IDCT is not established by format compatibility.

Next: obtain a complete-frame reference execution/capture for the exact module,
including destinations/work/state at this call boundary; compare native planes
after explicit layout conversion. Keep files private and bounded. Static call
and byte-range checks are preparation, not executed ABI or pixel-parity proof.

## R664: native compatibility prototype has headroom

The offline original-module harness now completes frames with tested DMA/guards.
Full frame0 raw coefficients match native; first Y/U/V quant tables match after
SDK AAN scaling. Final floor conversion removes native brightness bias. An
isolated AC1-only row reproduces the SDK quarter-path middle-output reversal;
native compatibility now applies that ordering to eligible first-pass rows.

Frames0/1000/3000 differ in1/11/3bytes respectively, all by1, of353280bytes/frame.
This is not exact parity or all-frame output coverage. Standalone native prototype
with tracing disabled decoded all5591frames in5.847835seconds (956.08FPS,
1.04594ms/frame average), without audio/upload. Evidence and limitations are in
STATUS/JOURNAL R657–R664; benchmark log generated/thp-native-sparse-bench-r664.log.

Prototype sources: tests/probe-thp-native-frame.c and probe-thp-floor-idct.c,
compiled against private pinned FFmpeg8.0.1 sources/static libraries with
THP_FLOOR_IDCT, THP_SPARSE_IDCT and THP_BENCH. The private MJpegDecodeContext hook
is a diagnostic mechanism, not a stable product ABI. Next residual rounding
coverage and scoped integration at the validated guest boundary, with bounded
memory, original error/fallback behavior, guest/player/audio timing and full
in-game movie completion still required. No further stock-decoder throughput
or title-navigation loop is needed to establish feasibility.
## R767: bounded additional output coverage

Current-source offline probes additionally compared PrologueA frames
1/500/2000/4000/5000/5590:0/0/1/0/2/1 differing bytes respectively, all magnitude1.
Original DMA coverage and boundary guards pass for each frame. This extends
sampled fidelity only; audio, duration, device and full parity are not established.
Do not repeat throughput or unchanged opening runs to rediscover feasibility.
Keep private opt-in policy and return to the measured gameplay-native bottleneck.

# R673: correlate visible stalls with bounded logs

Keep the native-decoder integration as the active performance experiment. Pair
scene observations with five-second presentation summaries (including the lowest
roughly one-second FPS observation and longest UI observation interval). The UI
interval is not a per-frame presentation gap. Native candidate diagnostics are
separately opt-in via `GALAXYPAD_THP_TIMING=1`: summarize calls, rejection count,
mean/max dispatch wall time every five active seconds and at unload. Dispatch
includes eligibility validation and decode/copy on acceptance; rejected dispatch
does not include the original decoder that executes afterward. No per-frame logs.
Use epoch timestamps to correlate decoder summaries with the dated host log;
retain monotonic timestamps for durations. Neither counter proves audio cadence.

Compare visible movie progression and completion against source duration, then
attribute remaining stalls to decode, presentation or host contention. Capture
timed memory/swap deltas, not just a high-memory snapshot. Do not run builds while
taking performance measurements. Title/file-selection regressions are a separate
non-movie bottleneck: R672 live windows fell from roughly57–59 to49–52FPS before
any native movie frame was accepted. Full PRD acceptance remains unchanged.
# R674 live result and next priority

Native candidate completed all5591 movie decodes with0 fallback, two complete
presented windows59.7/60.0FPS and visible return to gameplay. Keep it opt-in until
exact duration/audio/correctness checks pass. Avoid another offline throughput
loop: the next substantive optimization target is gameplay CPU dispatch/core
overhead, alongside measured synchronous depth-readback cost without changing
depth semantics. Gameplay stayed around25–32FPS before/after the movie. Use the
R673 diagnostic build on the next justified launch; no default promotion yet.
