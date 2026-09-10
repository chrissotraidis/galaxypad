# R815: optional native-loop specialization audit and differential

The R814 source audit supports a private specialization experiment, not a
product change or predicted frame-rate gain. No Simulator, game, or host build
was launched. The failed cross-product candidate remains parked.

## Configuration versus live state

In the checked StaticRecomp sources, dispatch sampling is assigned in Init
(StaticRecompCore.cpp:150); direct-boundary enablement is assigned in Init and
cleared in Shutdown (211,239); REL presence is assigned by private LoadModule
(360), whose only core call is Init (198). Forced fallback ranges are populated
in Init (175). Lockstep enablement is assigned in verifier Init (66); Run already
captures IsEnabled at entry. The trace file is local to Run. These are lifecycle
configuration, not guest-dispatch toggles in the checked source. This is a
source audit, not independent proof of concurrent lifecycle safety.

In contrast, chunk states can be invalidated by callbacks; module activity,
guest exceptions, Dolphin exceptions, CPU state, and host-hook eligibility must
remain live. ModManager::HandlesAddress also checks dynamic pending returns.
Do not snapshot those results or assume every native continuation is safe.
The candidate retains the entire eligibility lambda, including its REL/forced
fallback branches, and retains all charging, timebase, idle and exception code.
It even retains direct-segment charging/state stores: no additional arithmetic
or state-lifetime optimization is bundled into this experiment.

## Implemented private test

tests/test-run-quiet-specialization.py extracts the exact current complete inner
native do/while loop and its eligibility lambda. Six checked textual replacement
sites gate trace, lockstep, dispatch sampling, two REL translations and direct
boundary setup behind a compile-time Quiet parameter. Both general and quiet
instantiations are compared with the unmodified loop. Quiet is only valid when
all those optional features are disabled; production selection is not implemented.

5,376 cases pass separately under ASan/UBSan -O1 and optimized -O2. Callback-entry
guest snapshots, final guest/PPC state, dispatch/hook/slow-path counts, cycles,
timebase/remainder, exception counters, idle calls, chunk state and direct state
match. Cases vary exit dispatch, every timebase remainder, forced-fallback lookup,
host-call presence and idle configuration. Callback mutations cover invalidated
and failed chunks, dynamic hook entry, synchronous and asynchronous exceptions,
interrupt masking, pause, inactive module, guest exception clearing, out-of-range
PC, EXRAM continuation, exhausted downcount and changed lookup entry.

Services and the guest callback are explicit stubs. This proves the extracted
inner-loop differential on these cases, NOT complete Run integration, real guest
execution, diagnostic-enabled behavior, concurrent lifecycle safety or speed.
The general-template case here also uses disabled diagnostics; it is not a
replacement for enabled-feature integration tests.

Existing test-direct-call-boundary.py passes its actual boundary/transfer/charge
regressions. No installed app, reference runtime source, normal module, save or
disc was edited. Free space was 30 GiB; no Simulator was booted.

## Next gate

Measure the complete burst under actual host compile flags with representative
out-of-line guest callbacks and short/long/exception/hook exits, preserving the
original body and exact candidate identity. Prevent constant propagation through
the reference callback/configuration from turning this into an empty-loop test.
Inspect emitted code and account for the specialization-entry branch and code
size. This stub correctness harness by itself is not an acceptable cost screen.
Only material, repeatable savings justify a private host build and sequential
matched plaza comparison. The 698/6004 Run self observations are a limit on the
sampled lane, not a predicted FPS gain. All original PRD/SunPad/audio/stability/
gameplay/device requirements remain open and unchanged.
