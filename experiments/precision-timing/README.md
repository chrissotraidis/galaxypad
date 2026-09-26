# Precision timer experiment

Isolated Simulator-only source overlays against the accepted audio-tempo core
and settings/perf host13. `python3 experiments/precision-timing/build.py --build`
now produces `generated/experiments/precision-timing-v2-20260914`, preserving v1.
It verifies and reuses v1's core archive and timer objects, recompiles only CoreHost.mm, then links,
ad-hoc signs and verifies. No installation or launch is performed. Production
sources and released artifacts are unchanged.

Two independent, default-false preferences:

- `GalaxyPadDevPrecisionTimingProbe`: measure existing precision timer calls.
- `GalaxyPadDevDisablePrecisionTiming`: set the existing PrecisionFrameTiming
  configuration false before runtime startup. Control leaves configuration as-is;
  the effective value is logged. The candidate uses existing sleep_until calls.

Measure first with only the probe enabled. For throughput off/on/off comparisons,
disable the probe in every run and toggle only the candidate preference. The
candidate has no precision calls to observe. No clock scaling, skipping,
readback or FIFO synchronization changes are made.

Lane0 is the CPU throttle branch; lane1 is the video presentation branch.
Unrelated PrecisionTimer callers are ignored. The recorder is thread-local with
one writer per lane, valid for this runtime's one CPU/one video thread design.
Measurement-disabled calls read no additional clocks. Enabled calls record wall
and thread CPU duration, requested delay, final yield-loop wall duration, and
deadline overshoot. Already-late calls increment `late` and are excluded from
overshoot totals/histograms. Histogram edges are 10,50,100,250,500,1000,5000 us.
`cpuValid` counts calls with valid monotonic thread CPU readings; `cpuNs` covers
only these calls. Spin wall time includes possible descheduling, and is not CPU
consumption. Requested delay includes the final spin budget. Measurement clock
overhead is not calibrated away; compare throughput with recording disabled.

Each lane publishes cumulative counters no faster than once a second, at most
512 times. The CPU VI callback reads consistent snapshots every120 fields and
uses the existing asynchronous performance logger, at most1024 records. There
is no IO/allocation in the timer itself. The most recent partial interval is
not forcibly exported. Restart the process for a fresh experiment session.

V2 collects both lane strings in one array and calls the single-flight logger
once per VI hook. V1 issued two back-to-back calls, which could drop lane1 while
lane0 was pending. A source contract checks the single-batch hook. The existing
logger returns void, so acceptance cannot be acknowledged without changing its
API; complete batches may still be dropped when another performance writer is
busy. Counters are cumulative, so later accepted snapshots retain their totals.

Contracts cover arithmetic, late-arrival exclusion, invalid CPU readings,
histogram totals, scope restoration, disabled recording, independent lanes,
seqlock rejection and publication cap; build runs ASan/UBSan on these contracts.
They do not establish pacing or gameplay acceptance. A Simulator throughput gain
would not establish a physical-phone gain, especially with thermal state2 in
the current phone report. Reject the candidate if physical wake overshoot or
frame/audio cadence regresses.
