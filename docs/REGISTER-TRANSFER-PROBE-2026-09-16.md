# Whole register-transfer cost probe

> Session closed: [current build, owner assessment and research handoff](SESSION-CLOSE-2026-09-16.md).
> This document retains the evidence and acceptance limits of its dated experiment.


This is a new isolated cost experiment, not an installed game optimization or a
claim that it closes the iPhone's FPS gap. The installed audio repair is separate.

## Architectural direction

[N64Recomp](https://github.com/N64Recomp/N64Recomp) uses recovered function
boundaries and direct native calls. This reinforces the value of optimizing
larger execution regions, but it does not remove Wii timing, callback and
arbitrary-entry requirements. Earlier GalaxyPad function-local and direct-call
experiments already failed their benefit gates; repeating them is not justified.

The next concrete probe addresses memory work inside generated code. DolRecomp
emits load-multiple (`lmw`) as a loop of independent checked word loads. A normal
stack restore repeatedly translates adjacent addresses. The prototype proves one
whole direct-RAM span, excludes overlap with CPUState, and loads the registers
from that span. Special memory, wrapping, undersized mappings and CPU-state alias
cases fall back to the original ordered loop. It uses existing runtime endian
helpers and introduces no persistent mapping cache or ABI/layout change.

Unlike the earlier four-`lwz` range correctness probe, this pass measures the
complete load-multiple operation, including the range guard, at several widths.
It is still not a complete guest function or whole-game cost measurement.

## Executed results

All 32 register-start positions pass 35,232 complete CPU-state comparisons under
ASan/UBSan, including MEM1/MEM2, mirrors, unaligned and end-of-mapping addresses,
wrapping/unmapped addresses, callback register mutation and explicit source/CPU
aliasing. The prototype handles loads only; it makes no store-journal, reservation,
interrupt, generated-emitter or linked-module equivalence claim.

Six alternating timing repetitions on this Mac use the real maintained memory
helpers, separate non-inlined entries and changing source addresses. Larger
restores (5, 12, 18 and 32 registers) reduced operation elapsed time about 62–89%
in these direct-RAM microbenchmarks. Two-register results were small (2–7%), and
single-register transfers regressed 63–81%. Blanket substitution is rejected.
The final all-width validation source and original six-width timing binary are
retained separately; the report distinguishes their identities.

A static scan of retained device-fresh generated source finds 51 unique `lmw`
addresses, all restoring at least five registers. Two occur in the sampled hot
805170A0 chunk (five and six registers). The other three inspected hot chunks
contain none. Static counts and a hot enclosing chunk do not establish dynamic
coverage: the native sample must land inside the actual load sequence before
this can be called a meaningful contributor. A broad FPS claim is unsupported.

Private source, timing binary, sanitizer binary, timings, source identity and
coverage report: generated/register-transfer-20260916/. No generated game source
is included in this document. No emitter/default/module changed for this probe.

## Next acceptance boundary

Map exact native instruction samples to these multi-load bodies, then test the
selected complete restore/return region, including surrounding state materialization
and runtime exits. Promote only if the whole region is cheaper and dynamically
important. If coverage is small, retain this as a reusable narrow optimization
and continue into adjacent memory-heavy call regions; it cannot justify another
large module build on its own. Stores require separate journal/reservation and
memory-observability proofs, not reuse of the load-only result.
