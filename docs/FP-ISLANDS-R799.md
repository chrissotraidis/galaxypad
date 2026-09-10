# R799: select sustained floating-point work, not another integer micro-test

R798 was progress: direct-load correctness passed and local cost rejected the
candidate. No reason to build an app or repeat that tiny integer benchmark.

Added source-hash-checked `scripts/rank-fp-islands.py` over retained instruction
coverage. It groups consecutive arithmetic/move instructions, breaking at
memory, other instructions, address gaps or unknown counts. These are inspection
spans, NOT proven basic blocks: each instruction can have an external suffix
entry, and record-form instructions still have CR effects. Entry attempts are
not CPU time, completed operations, or a current scene profile.

`tests/test-fp-island-ranking.py` passes boundaries, unknown versus zero counts,
address gaps, pre-function duplicate labels, helper extraction, and changed-source
rejection. Registered in check-repository; full suite not rerun. Evidence is
generated/fp-islands-r799.json using source-matched R792 FP coverage.

| Inspection span | Instructions | Retained attempts per site | Total site attempts |
| --- | ---: | ---: | ---: |
|804B6BE0–804B6C00, normalization arithmetic|9|22,608,668|203,478,012|
|804B6CCC–804B6CE0, cross-product arithmetic|6|19,279,400|115,676,400|
|804B6C80–804B6C90, scalar refinement|5|4,105,260|20,526,300|
|804B64D8–804B6510, longer paired arithmetic|15|1,240,764|18,611,460|

Longer source length alone is not a better target. The nine-instruction region
is both more frequently reached and substantially more arithmetic work than the
R798 mixed integer fixture. Its sequence is ps_madd, ps_sum0, frsqrte, three
fmuls interspersed with fnmsubs, then two ps_muls0 operations. The six-instruction
cross-product region has four arithmetic helpers and two register merges.

## Concrete state boundaries checked

Current generated chunk_1202_text1_804B60A0.c lines7197–7254 contain the nine
normalization instructions. Every instruction materializes PC and checks FPU
availability; helpers write FPR/paired lanes/FPSCR. The preceding lfs at6BDC and
following psq_st at6C04 are memory/observer boundaries. The entry switch charges
the original suffix budget before execution, including the following stores and
return. Replacing nine instructions must not independently double-charge it.

Actual GXRuntime cpu_interpreter_float.c has materially richer semantics than
native multiply/add alone:

- fmuls force-rounds its C operand to25bits, gates invalid results on VE, writes
  both lanes and clears FI/FR. Paired helpers have different write/gating rules.
- frsqrte uses the reference estimate and may preserve its destination on enabled
  invalid/divide-by-zero exceptions. It is not interchangeable with host sqrt.
- force_single handles NI flushing; arithmetic executes under host rounding and
  accumulates host FP status. Paired sources and destination aliases matter.
- set_fp_exception updates sticky exception summaries. ppc_fpscr_updated updates
  FPSCR locally; the inspected path is not an external memory callback.

This identifies a potential register-lifetime region, not permission to discard
status updates. The final paired helper writes FPRF, but previous R164–R176 already
implemented a bounded dead-FPRF policy elsewhere. Do not restart that lane as a
new discovery. R769 blanket inlining, R780 typed isolated multiply and R787
single checked cross-product multiply also remain rejected for promotion.

## Next implementation gate

Target a whole observed FP arithmetic region with shared operand precision facts
and resident paired values, not independently guarded instruction helpers. The
offline exporter currently adapts only GPR layout and explicitly aborts FP cache
conversion hooks. Adapt/test the actual reference FP cache's paired-lane layout,
conversion, flush/reload and ABI behavior before relying on it for this region.
Then preserve every legal suffix entry, unavailable-FPU behavior, original cycle
charge, FPSCR, all CPU fields and host flags against actual generated code.
Use the complete containing routine with its original ThinLTO/PGO policy for the
cost gate, not the prior standalone -O2 integer screen. A pure arithmetic island
does not justify keeping values across the surrounding memory callbacks.

No product source, app/module, save or Simulator change. No FPS improvement.
Full PRD/SunPad/audio/stability/gameplay/device objective remains active.
