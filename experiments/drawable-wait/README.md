# Isolated drawable acquisition measurement

Build with `python3 experiments/drawable-wait/build.py --build` after other timing
work releases the host. Without `--build` the script only prepares source copies,
VFS mappings, frozen probe/test inputs and exact commands. No install or launch.
Output: `generated/experiments/drawable-wait-20260913/GalaxyPad.app`.

Default-off Simulator startup preference: `GalaxyPadDevDrawableWaitProbe`.
Use the same binary with the preference off/on for an instrumentation overhead
control. Do not enable batching or infer physical-iPhone performance from this
Simulator probe. The observed phone EFB service time is materially lower than the
Simulator's; this probe has not established the owner's hardware bottleneck.

Only MTLGfx.mm and CoreHost are recompiled. The original accepted audio-isolated
core is copied and its single MTLGfx.mm.o archive member replaced. All other core
members and host13 objects are retained. Existing audio VFS inputs are retained.
MTLGfx original size18691 and nanosecond mtime1789050312855623107 match the accepted
core recipe's source stamp; this is bounded continuity evidence, not a historical
full-source hash claim. Prepared source and input hashes are in recipe.json.
No batch or EFB instrumentation is included.

The wrapper invokes nextDrawable exactly once in both modes. Disabled mode reads
only the enabled flag: no clock or state accessor. Enabled mode samples existing
HasUnflushedData/GPUBusy, clocks the acquisition alone, then resamples state.
It never calls GetRenderCmdBuf or changes encoder/submission behavior.
GPUBusy is a completion-counter proxy; it does not directly measure GPU activity.
No claim about display completion follows from acquiring a drawable.

Cumulative snapshots publish every120 acquisitions, at most128 times. The CPU VI
hook checks every120 fields and asynchronously logs only a changed snapshot, so
some publication boundaries may be coalesced. `calls` counts acquisitions,
including nil returns, rather than displayed frames. Each record has:

- calls, totalNs, maxNs, nil, pendingAfter, busyAfter.
- busyToIdle and busyToIdleNs: acquisition samples whose completion-counter state
  changes from busy to idle; not the duration spent GPU-idle.
- pendingChanged: should normally remain zero across acquisition.
- hist0..7: elapsed ns in [0,10000), [10000,50000), [50000,100000),
  [100000,500000), [500000,1000000), [1000000,5000000),
  [5000000,16000000), [16000000,infinity).
- stateCount0..3, stateNs0..3, stateMax0..3 group the before-state by
  `2*pending + busy`: 0 neither, 1 busy only, 2 pending only, 3 both.

Use cumulative deltas for counts/times/histograms. Maxima are lifetime maxima and
cannot be subtracted to obtain interval maxima. Significant acquisition time with
pending work would justify precise command scheduling correlation; it would not
alone justify changing submission. Presenter::Present also intentionally sleeps
before final submission, outside this probe's timing interval.

Built successfully on2026-09-13. Host SHA256:
`7000615f8816c4eafa24c21591ea8e1287ba1ac1ad8e045a4d75daf427d1f760`.
Core SHA256:
`7e20c06c1d8faf1a5d2ac0593387eb7028004f3660a87a85134bfa16024ec478`.
ASan/UBSan contract passed disabled-mode clock/state exclusion, single acquisition,
aggregation, histogram boundary examples, nil/transition handling and bounded
publication. Compile/link/archive member scope/sign/strict verification passed.
Existing vendor unused-parameter and deprecated-Metal-option warnings remain.
Symbol inspection confirms one shared enabled/publication state between host/core.
Startup preference wiring compiled; actual startup and log delivery are untested
until the owning session launches the app. No simulator runtime was performed.


The owning session subsequently verified startup and log delivery in the fixed
1x Observatory scene. A2,400-acquisition interval measured38.990ms total over
51.262wall seconds (16.246us/acquisition); all interval acquisitions were below
50us. This does not support a drawable-wait optimization for that scene. No
submission behavior was changed. See the pass3 report for hardware limitations.
