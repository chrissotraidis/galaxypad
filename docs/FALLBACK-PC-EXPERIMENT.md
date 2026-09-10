# R740: identify mobile interpreter work before optimizing it

## Current R754 capture procedure

Table now32768slots/16bounded probes with mixed high address bits. Recorded-key
replay drops0, but unknown omitted R751 keys mean live completeness unproven.
Opt-in FALLBACK_PCS=1 retains immediate capture unless
GALAXYPAD_FALLBACK_START_FILE is set. For phase selection use a unique ABSENT
marker path at launch; after visually confirming the scene, create that marker.
CPU notices it at a1024slice poll boundary and logs capture-start PC/nativecount.
Only subsequent actual interpreter steps enter the census. Marker is not deleted.
Confirm capture-start before timing/stopping; never equate marker creation with
an exact capture timestamp or scene proof. Native Stop flushes; summarize counts
and losses. Current core compiled, not installed. No live phase capture yet.

## R741 integration

Canonical patch0027 adds the identical tested histogram to the vendor core.
GALAXYPAD_FALLBACK_PCS must equal1; allocation/reset happens at Init. Three
pre-interpreter sites record Forced(1), Uncovered(0), InstructionHook(2).
Shutdown emits total/dropped and every occupied PC/path/count, then releases
the table. No per-step output; default path has only a null-pointer check.
Source wiring and histogram sanitizer tests pass, registered in full suite.
Reverse patch and shell syntax checks pass. Incremental Simulator core build
79368 completes exit0, generated/ios-core-r741.log. App not yet provisioned or
installed and no live histogram exists. Earlier "no integration" below is R740.

Previous turn made progress by closing the NI-hint screening experiment and
recording the independent review's measured disposition. No speed gain claimed.

Current Run.cpp has two chassis SingleStepInner sites: explicit forced ranges,
and the no-JIT uncovered loop. HookInstructionFallback has a third actual
interpreter site AFTER its native cache fast path. Instrument these three
pre-step PCs separately; never label all hook_fb counts interpreter work.
Debugger SingleStep and fallback JIT execution are outside this census.

Retained R710b shutdown:160745542 fallback steps,507568864 hook_fb,
3577178 native exceptions. These whole-run counts do NOT identify PCs, establish
exception-vector attribution, or measure interpreter CPU share.

Implemented diagnostic-only fixed histogram in
apple/experiments/fallback-pcs/histogram.h.4096 slots, at most8 probes, no
allocation/I/O/guest reads per record, separate exact PC and path, explicit
dropped count. Collision loss is reported, not silently treated as complete
coverage. Counts are not time weights. No product integration yet.
tests/test-fallback-histogram.cpp passes ASan/UBSan: repeated keys, PC aliases,
three paths, PC zero, saturation, and recorded+dropped conservation.

Next: opt-in ownership/init/shutdown wiring and the three exact pre-step sites;
retain a canonical reproducible patch and test wiring before building mobile.
Dump after CPU shutdown, not per instruction. Disabled path must allocate no
histogram; diagnostic capture is not a performance A/B. Use one existing
Simulator only and preserve installed saves/checkpoint identity checks.
Map captured addresses to current DOL/relocated code before proposing coverage.
If fallback cost is minor, close it; don't infer a large win from step counts.
