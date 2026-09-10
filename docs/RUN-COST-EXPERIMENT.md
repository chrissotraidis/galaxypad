# R763: distinguish native bursts from non-native routing

R762 fresh plaza wall sample has9 interpreter-ancestry samples and236 Run self
samples out of1695. Collapsed offsets and incomplete/tail-call unwinds prevent
an exhaustive fallback CPU-time bound. Do not infer99%CPU from the earlier
99%fallback-step vector concentration.

## Implemented diagnostic

Canonical patch0029 adds RunCost.h and two lexical scopes in Run.cpp:

- Native: SyncIn, entire native burst (generated execution, hooks, bookkeeping,
  state/timing/dispatch checks), SyncOut and pending exception delivery.
- NonNativeRouting: host-call handling, forced fallback or interpreter/JIT
  routing. This is NOT pure interpreter time and includes early continue paths.

Scopes do not overlap. CoreTiming and outer routing checks are outside them.
The denominator is CPU-thread clock time from activation until Run returns.
Use CLOCK_THREAD_CPUTIME_ID only: no wall-clock fallback. Failed/regressing
clocks invalidate evidence. Scope ends and final report run on the CPU thread.

Every opted-in span updates a fixed counter/PRNG; approximately1/256 receives
two clock reads. This is sparse pseudo-random sampling, not periodic capture.
Output gives spans, selected/completed samples, sum/squared sum and maximum
duration per lane. No per-instruction instrumentation, allocation or logging.
Without opt-in there is no recorder allocation or clock access.

## Capture

1. Package existing newly compiled core; no game-module link needed. Keep
   nativeTHP explicitly OFF for this comparison, matching R762's actual build.
2. Launch with GALAXYPAD_RUN_COST=1 and GALAXYPAD_RUN_COST_START_FILE pointing
   to a UNIQUE ABSENT path. Histogram must remain OFF. Missing enable/marker
   leaves the probe inactive. Marker ownership remains with the caller.
3. Visually verify same Star Festival plaza, then create marker. CPU polls at
   1024 timing-slice intervals; confirm capture-start log before measuring.
4. Hold a bounded stable scene window, clean Stop. Reports are per Run call;
   pause/resume may produce multiple reports and must not be silently merged.
   Confirm clock_errors0, completed==selected and enough samples in both lanes.
5. Estimate each lane's CPU cost using sampled durations and inclusion rate;
   report sampling uncertainty/long-tail sensitivity. Measure empty clock-pair
   overhead and repeat at a different inclusion rate before trusting a small
   difference. Do not subtract an assumed clock cost or force totals to100%.

This separates inclusive native/non-native cost, NOT native bookkeeping from
generated execution. Only if non-native cost is material should vector/chassis
acceleration reopen. Otherwise return to AOT shared-state/materialization work;
do not repeat rejected dispatch/direct-call/lookup microtuning.

## Evidence status

Header sanitizer tests cover1million spans, approximate inclusion, sums/squares,
null opt-out, early exits and failed clocks. Source scope checks and temporary
0029 peel/0027 reverse-check/0029 reapply roundtrip pass. Simulator core build6078
exit0, ios-core-r763.log. App not packaged/installed with this change yet. No
CPU split or performance gain claimed. Full original PRD remains unchanged.

## R764 first live result and disposition

Existing M5 Simulator, signed appe2f9c933, coreceda1909. Histogram/nativeTHP OFF.
Fresh marker activated only after visible Star Festival plaza; scene remained
correct. First Run80.602CPU seconds, native14,145/non-native3,426 sampled spans,
zero clock errors. Native menu pause ends first report, then stop confirmation
produces a separate short Run. `summarize-run-cost.py --run 1` selects the plaza
report explicitly. Without selection, multiple reports fail closed.

Raw native estimate101.35% ±4.14percentage points nominal; non-native2.0809%
±0.0872pp nominal, ratio estimate2.1071%. Do NOT normalize or interpret native
above100% as physical utilization: sampling and clock overhead are present.
Host-only empty-pair mean389.457ns is not Simulator calibration and is not
subtracted. Additional inclusion-rate calibration is needed for precise/small
cost differences, but the large separation is sufficient to stop prioritizing
vector acceleration. Native scope includes actual generated execution and
bookkeeping; this does not identify which native instructions are excessive.

Next inspect substantial repeated native state/timing/shared-FP work, not more
vector/table microtuning. Clean Stop failed0 and save unchanged; no FPS gain.
