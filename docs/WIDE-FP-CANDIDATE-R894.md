# R894 guarded whole-routine candidate and limited cost result

R893 completed the reference oracle. This turn implements an actual private
candidate in scripts/wide_fp_candidate.py, selected only by the probe's
--candidate option. Normal app, generator, module and runtime are unchanged.

## Candidate contract

Only entry804B64A4 is accelerated. All other suffixes retain original code.
Eligibility requires available FP, LSQE, zero load/store quantization types,
no pending guest exception or write journal, and complete ordinary MEM1 spans
for input16bytes, output48bytes and constant4bytes. Pointers and sizes are checked
against wrap and CPUState overlap. MEM2 size is constrained so the original
MEM2-first mapper cannot unexpectedly intercept these MEM1 addresses.

Original arithmetic helpers and PC/cycle updates remain. Direct memory accesses
retain original order and conversions, including each store's reservation clear.
No output-store batching or scratch-state copy. Removing memory helper calls and
redundant availability/quantization tests gives the compiler fewer observation
boundaries. External hooks may be installed, but qualified accesses cannot reach
them; disqualified addresses use the original path. This is a private finite-test
contract, not a general proof for arbitrary overlapping runtime/global storage.

## Correctness and cost

- Initial5274exit0:314880 CPUState/memory/callback/FPSR comparisons pass;
 57600 callback cases;96 eligible fast calls. Candidate execution is now required
 by the harness, preventing vacuous all-fallback acceptance.
- Cost18556exit0 repeats full comparisons then eight alternating-order pairs of
 one million calls each. All final CPUState/memory/FPSR comparisons pass.
 Reference185.788–198.592ns/call versus candidate175.375–187.677ns/call; each
 paired CPU reduction approximately5–7%. Instructions roughly3491–3498 versus
2964–2970/call, approximately15% fewer. Includes call/guard/reset overhead.
- After that cost screen, added rejection of a non-null MEM2 mapping smaller
 than4bytes and explicit active-reservation test inputs. Final79600exit0 passes
314880 comparisons/57600 callback cases/96 fast entries again. Do not attribute
 the earlier exact cost figures to this subsequently guarded binary.

Artifacts generated/wide-fp-{candidate,cost,reservation}-r894 and matching logs.
Commands use tests/probe-wide-fp-routine.py --candidate [--benchmark] --output
with a fresh directory. Provenance records source/driver/helper hashes and
actual cached strict-FP/O2/ThinLTO/PGO compile flags. Existing mismatched/unprofiled
PGO warnings persist. This is not a final full-module link or Simulator benchmark;
the extracted-entry call shape differs from a production integrated chunk.

## Decision

No game rebuild or product promotion:5–7% of one routine cannot establish the
needed whole-game improvement. Unlike the rejected scratch-state implementation,
the prevalidated direct-memory design reduces work, so evaluate transferability
on a small set of genuinely different memory-heavy whole routines before deciding
whether it has architectural value. Retain the original arithmetic/observer
contract; do not tune more guards on this one routine to chase a benchmark.
Final integration needs broader correctness, representative cost, then repeated
iPad gameplay/cutscene and sustained audio/input validation. Full PRD remains.
