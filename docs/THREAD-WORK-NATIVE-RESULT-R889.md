# R889: complete native comparison and within-run slowdown

R888 fixed private paired-buffer capacity. R889 uses host2cf50e8a, original
native modulec0021b9f, explicit background input, LC0, fallback JIT disabled,
Metal/Cubeb, private R837 profile. No Simulator was running. PID5830/session63996
exited0 through SIGTERM/RequestStop. Save99d432d5 unchanged.

Title/file15220, Play/story55724 and finish74159 completed. CUA screenshots before
and after capture verify stationary starting plaza, life3/lives4/coins0/StarBits0,
same Mario location and lower-right pointer. Capture18177 completed. Artifacts:
generated/runtime/thread-work-native-r889/{runtime.log,vi.csv,work.csv,process-work.json}.

## Accepted coverage, not an optimization result

Outer window595993491664166–596023496408541. Both recorders dropped0, exact
timestamp pairing passes, retained tail margin21.002419s. All three summarizers
pass without a prefix override. Thread CPU total24.462820792s agrees with
independent VI CPU clock24.462820000s. 1596 samples/1595 guaranteed intervals.

| Metric | Native R889 | Simulator R836 |
| --- | ---: | ---: |
| VI events/sec |53.191588|49.378979|
| CPU-thread instructions/VI interval |142,990,058.492|140,436,806.290|
| CPU-thread cycles/VI interval |45,516,990.246|41,619,280.387|
| CPU-thread ms/VI interval |15.337192|17.941337|
| Performance-core CPU-time share |95.3650%|98.3333%|
| Wall p99 ms |40.065625|27.277375|

Simulator has1.79% fewer thread instructions and8.56% fewer cycles, but16.98%
more CPU time in these two runs. This supports similar-work/slower-execution,
not materially greater CPU-thread instruction work on Simulator. These are not
simultaneous, binary-identical or frequency-controlled trials; host/runtime/audio
and guest platform compilation differ. No universal platform penalty or speedup
is proven. VI is not display completion.

## Native slowdown within this run

Six consecutive5-second bins from the same outer start, all completely covered:

| Seconds | VI/sec | Instructions/VI (million) | CPU ms/VI | P-core time share |
| --- | ---: | ---: | ---: | ---: |
|0–5|60.0|141.140|14.382|98.45%|
|5–10|60.0|144.395|14.502|98.47%|
|10–15|59.0|144.391|14.570|98.31%|
|15–20|60.4|142.934|14.344|98.26%|
|20–25|47.6|143.171|16.047|92.56%|
|25–30|32.2|141.146|20.867|83.15%|

Game instructions remain similar while CPU execution slows and core-class share
changes. Wall outliers reach119.7ms with30.3ms thread CPU. EFB/DV​​D/wait counters
are overlapping elapsed scopes, not additive exclusive attribution. We did not
capture synchronized host pressure/frequency/activity state, so cannot name
thermal throttling, other processes, focus policy or paging as the cause.

## User-directed next gate: iPad Simulator

Prioritize actual iPad slow gameplay/cutscene acceptance. Use existing private
Simulator recorder plus synchronized lightweight host-pressure measurements to
separate instruction growth, slower execution and off-CPU stalls during a visible
slowdown. Preserve fresh outputs and original save. Inspect existing scheduling
experiments before changes; do not repeat blind QoS/core-affinity tweaks.
Choose one material intervention from that result and measure baseline/candidate
in repeated matched gameplay and cutscene windows. Controls, menu, audio,
physical devices, packaging and full original PRD remain required, not substitutes
for performance. No recent product FPS improvement is claimed.
