# R897 same-process iPad movie-to-gameplay work comparison

R896 verified readback control flow without a performance change. This turn
reproduced the heavier gameplay scene, using existing private hostbdd8633e,
paired65536 recorder, guest3acdcddd, THP enabled, LC0, QoSexperimentoff and
fallback JIT disabled. Audio output diagnostics and THP timing enabled. No build.
Only iPad DE8E956F running. Boot71633/install82556 complete; runtime84154/PID9986.
Private save99d432d5 verified. Input file intentionally reuses R890's leased
input path; fresh evidence directory generated/runtime/postmovie-ipad-r897.

Title77598/file50560/story+finish14472 complete. Actual navigation needed short
camera-relative corrections, retained in conversation tool calls; final forward
54119 triggers airships. No input during either capture. Movie56741 and plaza
81822 complete. CUA verifies airships before/after first window and stationary
invaded plaza before/after second: life3/lives4/coins0/StarBits4. This differs
from quiet starting plaza and is not a new matched macOS comparison.

## Complete paired windows

All thread and VI summaries pass, exact timestamp pairing, zero drops and no
prefix override. Bounds use process snapshot first-before/last-after:

| Metric | Airship movie | Invaded plaza |
| --- | ---: | ---: |
|Start ns|599010808552666|599115303459500|
|End ns|599040818101791|599145316666291|
|VI events/sec|59.880940|37.150312|
|CPU-thread instructions/VI|55,831,617.210|178,575,832.387|
|CPU-thread cycles/VI|18,308,230.537|52,117,639.322|
|CPU mean ms/VI|6.637013|23.421733|
|EFB elapsed mean ms|0|2.913314|
|Throttle elapsed mean ms|10.559733|0.001194|
|P-core CPU-time share|93.4264%|96.9767%|
|Retained tail margin s|150.098862|45.600297|

VI is not display completion. CPU includes guest and host work on that thread.
Elapsed stage counters overlap and cannot be added as exclusive costs. Relative
to R890's quieter starting plaza, instructions/VI rise approximately27.8% and
CPU time49.6%; platform/context/scene differ, so not a controlled optimization.
Within this same process, native movie completes near60 while heavier gameplay
is CPU limited. Even eliminating off-CPU waits would not bring23.4ms CPU below
16.7ms; roughly29% CPU-time reduction is needed at this observed execution rate.

## Audio delivery

Recorders use a different monotonic origin from host audio logs. Matched nearest
transition-pressure raw/epoch samples to wall-prefixed audio rows, then selected
snapshots at least1second inside each phase. This is conservative phase selection,
not exact equivalence to the30-second thread windows or sample-accurate AV sync.

Movie audio mono597963.073423–597989.473975 (26.400552s):6598 DMA enqueues,
1 underrun/1 backlog drop,2475 callbacks,1267200 output frames,1262570 nonzero,
0 short callbacks. Approximately47999frames/s,99.63% nonzero.
Plaza mono598069.07388–598090.57351 (21.49963s):3407 enqueues,74 underruns,
0 backlog/full drops,2016 callbacks,1032192 output frames,670028 nonzero,
0 short callbacks. Approximately48010frames/s,64.91% nonzero.
Natural silence affects nonzero fraction. These are callback-delivery measurements,
not listening/pitch/speaker-route/perceptual-sync acceptance. Do not call this
movie zero-underrun or use it to promote the decoder default.

## Cleanup and next decision

Host logs54531/59754 complete. Menu Stop exports recorders,5591 native decoder
frames accepted/0fallback, runtime failed0. Console84154terminal0. Restored
85ffc100 via92386exit0; save99d432d5 unchanged. iPad shutdown23488.

This closes the missing same-process heavy-scene workload measurement, not the
performance goal. Do not replay the same movie again merely for these counters.
Next CPU work must target a material whole-workload reduction, not a5% win in
one small routine or EFB wait removal. Reconcile retained instruction profiles
with this heavier scene before selecting a broader transformation; no fresh
whole-game profiling unless it answers a specific remaining attribution question.
Full original PRD/SunPad/audio/story/device/package requirements remain active.
