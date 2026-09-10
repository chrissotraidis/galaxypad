# R812: clean candidate shows no material gain in initial captures

Continued candidate50305/console10535 into the matching neutral Star Festival
starting plaza. Screenshots cross-candidate-r812-plaza.png, -after.png and
-repeat-after.png show unchanged scene/position. Warm-up15seconds, then two
separate45second profiler-free captures; no builds or other game instances.

First capture61536 exit0:996 events/37.399709complete seconds=26.63122events/sec.
Repeat67399 exit0:957 events/36.800112seconds=26.00536events/sec. R811 baseline
was25.92818. First apparent difference2.71%; repeat is approximately0.30% above
that earlier baseline. This is not a material or repeatable end-to-end gain.
The isolated routine improvement must not be described as a gameFPS improvement.

Artifacts: generated/cross-candidate-r812-capture.json and
generated/cross-candidate-r812-repeat.json; raw log cross-candidate-r811.log.
First capture had84system swapins/0swapouts and10522decompressions; repeat20/
0/5233. Updater recentCPU51.1..63.1% at first-capture endpoints, WindowServer
42.5..44%; background activity remains a confounder, not a proven cause of all
lag. No unrelated processes terminated. First raw audio snapshots show158 new
DMA underruns (1224 to1382); output counters unavailable, no audible-output claim.

Candidate terminated and console10535 exit0. Save still99d432...; normal module
unchanged. Same sole Simulator now starts the reverse baseline using the normal
module and identical settings/input file. Log cross-baseline-r812-reverse.log.
Continue that live process to the neutral starting plaza for the final order
check; no new build. Unless that changes the result materially, park this region
and return to dominant CPU work rather than expand a tiny local optimization.
No promotion; full PRD/SunPad/performance/audio/stability/device goal intact.
