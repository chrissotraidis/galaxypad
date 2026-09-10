# R826: real normalization region state-isolation oracle

Previous turn made progress by closing the restrict-annotation hypothesis with
identical whole-chunk machine instructions. Current source inspection selected
the existing R799 nine-instruction normalization region, not another mapping
cache, availability-only guard or cross-product variant.

`tests/probe-normalization-state.py` extracts exact generated 804B6BE0–804B6C00
instructions from chunk1202 SHA38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac.
Reference execution uses those bodies and their real external suffix charges.
An internal-entry mode bypasses the charge as original intra-chunk entry does.
The region ends before the following memory stores.

The private candidate checks availability on the original CPU once, copies FP
registers/paired lanes0–6 and FPSCR into a local CPUState, executes the original
arithmetic helpers with unchanged operands, and commits those fields plus final
PC at the region boundary. Unavailable entry uses the original exception path.
It does not change arithmetic, estimate tables, exception enables, FPRF updates
or FP rounding policy. There is no memory/callback inside this selected region;
that is not permission to extend the boundary across memory or host observers.

## Executed evidence

- ASan/UBSan O2:294,912 complete CPUState/raw ARM64 FPSR comparisons pass.
- O2/ThinLTO without sanitizers:294,912 comparisons pass as well.
- Each covers9suffixes, internal/external entry,4rounding modes, NI0/1, lazy-FP
  on/off, MSR-FP on/off, random/special/ordinary finite values, FPSCR exception
  enables, initial host flags and positive/negative downcount.
- Each includes73,728 unavailable cases with independent SRR0 assertion.
- Artifacts: generated/normalization-state-r826-linked and
  generated/normalization-state-r826-optimized. The latter records helper-source
  hashes, compile command, extracted region and output. Initial build lacked the
  real reciprocal-estimate table; fixed by including cpu_interpreter_table.c.

These are region correctness results, not full-chunk integration, actual PGO
cost, callbacks/aliases at surrounding stores, game-speed or device acceptance.

## Code-generation warning changes the next action

Inspecting the optimized executable shows `_local_state` still allocates
0xdd0 bytes plus its0x50-byte save area; reference `_original` saves0x30 bytes.
The complete CPUState scratch has NOT become a small resident-register state.
Do not call this a performance improvement, integrate it, or spend a full app
build on it. The helper ABI still permits the large object to escape scalar
replacement despite the region's flatten attribute.

Next use this executable oracle to evaluate compact FP-state/helper dataflow,
not further CPUState copies or attribute variants. Keep original helpers as the
reference and preserve all nine entries and observed state. First establish
small state/code generation, then actual-policy containing-routine cost before
gameplay A/B. If that cannot beat state-transfer overhead, close this design.
The local CPUState version remains a correctness scaffold only.

No product source, normal app/module selection or saves changed. No game,
Simulator, profiler or build remains. Full original PRD/SunPad/performance/audio/
stability/gameplay/device goals stay active.
