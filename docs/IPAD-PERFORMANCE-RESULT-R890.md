# R890 iPad Simulator baseline and next implementation gate

User explicitly prioritizes making the iPad Simulator run well and finishing
the original product. R889 changed the platform-attribution decision. This run
tests current execution conditions on iPad, not a new optimization.

## Executed

Private thread-work-ipad-r890 builder29486exit0, paired capacity65536, original
control/archive checks pass; unchanged Simulator guest module3acdcddd. This is
the existing performance host with private counters, not current UI acceptance.
Only iPad DE8E956F booted (66100exit0). Launch38101/PID6719 uses explicit THPoff,
CPUQoSexperimentoff, LC0, fallback JIT disabled. Original app85ffc100 preserved.
Commands are retained in process-work.json/provenance.json.

Landscape verified, title83682/file44333/story93735/finish90963 complete. Actual
pre/post screenshots show stationary starting plaza, life3/lives4/coins0/
StarBits0. Pointer lease15609 and capture88738 complete. No movement or UIKit
input acceptance claim. Host logging86416 and lightweight probe55138 complete.

## Complete 30-second result

Artifacts: generated/runtime/thread-work-ipad-r890, including vi.csv, work.csv,
process-work.json, host.csv, host-pressure.jsonl and runtime.log.
Window596522744964083–596552755448875; zero drops, exact paired samples and
complete coverage, tail margin63.124s. All three summaries pass without override.

- 1684 VI events,56.113722 VI/sec; not display completion.
- CPU-thread139,704,528.425 instructions and42,117,683.428 cycles/VI interval.
- CPU mean15.660069ms, p95 17.776709ms, p99 19.773958ms.
- Wall mean17.822682ms, p95 20.807917ms, p99 24.270459ms.
- Performance-core CPU-time share98.378451%; E-core1.621549%.
- EFB elapsed mean1.727499ms; throttle0.000897ms. Elapsed scopes overlap.
- Independent CPU clock total26.355896708s versus thread counter26.355896875s.
- Process-wide226,224,246.123 instructions/VI; not CPU-thread work.

This does not reproduce historical6–22FPS, establish stable60FPS or prove any
new product speedup. R83649.379 versus R89056.114 with similar work again shows
context variability. CPU work is near the16.667ms budget even in this better run;
there is insufficient headroom for heavier scenes and stalls.

## Host evidence and limits

Lightweight host.csv fully brackets the measured window: zero swapins/swapouts,
2470 compressions/4520 decompressions,2881 pageins/122 pageouts, approximately50%
aggregate idle ticks. Cached aggregate counters cannot exclude short pressure
bursts or prove individual-core availability. Five-second process/memory log
ends10.67s before window end; do not claim whole-window per-process coverage.
Available snapshots show memory-pressure free percentage41%, significant
Logitech updater/WindowServer/SimMetalHost load. No causal process attribution,
no unrelated process killed, no thermal/frequency claim. Low Power Mode0.

Menu Stop Game exports both recorders, runtime failed0. Then terminate stopped
app, restore85ffc100, rehash save99d432d5 unchanged, shut down iPad. Console38101
terminal0, restore65016exit0, no game or Simulator left running.

## Implementation plan — no more unchanged baseline loops

1. CPU headroom is the gameplay priority. Review closed shared-state/alias/FP
   experiments before selecting a broader code-generation intervention; require
   a correctness-qualified, material instruction reduction before another full
   module build. Existing blind QoS and duplicate-EFB-peek lanes stay closed.
   Keep simulator as the acceptance platform, not a reason to accept low FPS.
2. Cutscenes have a distinct existing native-THP candidate. Continue its open
   audio producer/starvation and transition correctness gate; do not promote
   default-on merely because the movie counter is fast. Both video cadence and
   audible/audio continuity matter. This is a material existing lever, not another
   tiny arithmetic tweak or unrelated controls pass.
3. Compare any qualified change in repeated iPad baseline/candidate windows,
   then a sustained movement-heavy route and movie-to-game transition. Report
   frame tails, CPU work, audio underruns and visual/input correctness together.
4. Resume remaining SunPad controls/menu polish and packaging/device verification
   without dropping full-story, physical hardware, audio or original PRD gates.

Do not keep rebuilding instrumentation, repeating title screens, or interpret
one56FPS stationary scene as finishing the user's request.
