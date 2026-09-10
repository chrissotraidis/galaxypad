# R898: reconcile heavy-scene evidence before another optimization

The preceding turn restated R897 and verified shutdown; it did not change
performance. This turn reuses retained evidence and makes the next attribution
question explicit. No app, module, save, or runtime changed.

## Executed analysis

`python3 scripts/summarize-fallback-sample.py generated/plaza-sample-r705.txt --output generated/plaza-heavy-self-r898.json`

The existing parser conserves all 428 CPU-thread wall observations. Its focused
regression, `python3 tests/test-fallback-sample.py`, passes. The R705 capture was
visually identified as invaded plaza, unlike R822's quieter starting plaza.

| Exclusive symbol bucket | Observations |
| --- | ---: |
| Generated chunks, including inline work | 224 |
| Host Run | 42 |
| Module dispatch | 19 |
| Hook routing | 38 |
| Out-of-line PPC helpers | 18 |
| Remaining, including waits | 87 |

131 generated chunks occur; their top ten total 65 observations. The largest,
804B60A0, has 12 exclusive observations, not every inclusive descendant in that
chunk. Separate ancestry grouping recognizes 49 waits and 2 interpreter-stack
observations. These classify the same samples; do not add them to the table.
This older, short wall sample cannot provide current running CPU cost, individual
instruction weights, a quantitative scene delta, or a removable-cost bound.

R822's retained weighted native profile assigns 659,841,358 of 22,315,669,485
CPU-thread cycle-weight units to the entire 804B60A0 chunk: 2.9569%. A hypothetical
7% reduction in that entire self bucket corresponds to only 0.2070% of the total
weights. That is arithmetic illustrating scope, NOT a predicted speedup or a
bound on inlined/out-of-line work. R894 improved only one smaller routine in an
isolated cost screen; transferring its percentage to the whole chunk is unproven.
R895 already rejected broad rollout of that guarded-memory design.

Input SHA256s:

- R705 sample: 61cb2a9f76ca38af72fecf2e947273a3e8fcf7ec2629d57032889adfe3abf7c3
- R822 summary: b23d345dfe9ebbfa3733b193c4307d8256c946d46cc843fb7ded22f35e6ef887
- New report: def84bb5cad920dc38c98a06c2b925ff9ebb3225fa7967fcf5a81dcfce92a47f

## Next experiment and decision it must enable

The remaining attribution question is whether the heavier post-movie scene's
extra CPU work concentrates in different code or amplifies the same generated
memory/arithmetic/dispatch overhead. R897 measures the increase but not its
instruction origin. R705 supplies broad symbol evidence but collapsed offsets;
R822 supplies instruction weights in the wrong scene.

Use one source-matched native run and the already working CPU Profiler attach
path for the invaded plaza. Retain raw PCs, weights, module identity, scene
screenshots, and VI/thread counters. Do not launch under a profiler time limit
that kills the game. Do not repeat R819's failed Simulator attach or R820's
unavailable task-access sampler. Native evidence selects a shared-code hypothesis;
only a matched iPad candidate/control run establishes an iPad improvement.

Compare source-level concentration against retained R822 before choosing code.
Do not assume the two profiles are frequency-controlled, assign collapsed offsets
individual weights, or require a new profiler framework. Stop analysis once a
specific broadly exercised mechanism is identified; implement its correctness
and actual-policy cost experiment before another full module build. No further
tiny normalization/cross/restore variants, unchanged movie throughput captures,
or speculative depth-wait removal are justified by these records.

Simulator list currently shows no booted devices. Disk Avail is 16 GiB; a bounded
trace is feasible, but no full-module rebuild is planned. Full PRD, SunPad,
gameplay/audio/stability/device/packaging/rights requirements remain open.
