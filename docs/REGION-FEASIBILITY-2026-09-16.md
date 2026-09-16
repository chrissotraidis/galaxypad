# Reusable compiler optimization: initial feasibility evidence

> Session closed: [current build, owner assessment and research handoff](SESSION-CLOSE-2026-09-16.md).
> This document retains the evidence and acceptance limits of its dated experiment.


This is an executed structural analysis and source review, not an optimized
game build. No phone, Simulator or gameplay comparisons were run.

## Prototype and result

`scripts/analyze-region-feasibility.py` reads DolRecomp's emitted annotations,
deduplicates identical loop-specialization copies, verifies entry labels and
classifies a conservative explicit opcode set. Unknown instructions, control
transfers, status operations and address gaps split windows. It writes hashes
for every input. It contains no game addresses or game-ID checks and accepts
any directory using this generated format. Five regression tests cover memory
boundaries, unknown/status/control barriers, integer gaps, address gaps and
malformed/duplicated annotations. It is registered in the default suite.
The complete default `bash scripts/check-repository.sh` suite passed after
integration. This validates the analysis tooling and repository checks, not an
optimized execution path.

Executed against the selected iPhone module's 1,322 generated source chunks:

| Static category | Instructions |
| --- | ---: |
| Recognized integer arithmetic | 460,279 |
| Recognized memory operations | 389,284 |
| Recognized FP arithmetic/moves | 34,646 |
| Other/control/status/unknown barriers | 467,903 |

These are source inventory counts, not dynamic operation frequencies. The
barrier category includes conservatively unclassified operations; it is not
a count of unavoidable runtime exits. Embedded text-section data can also
contribute annotations. This tool does not prove reachability or legality.

With memory operations splitting windows, 3,457 recognized FP instructions
(10.0%) occur in windows containing at least eight FP instructions. If memory
is hypothetically allowed within a window, that rises to 10,140 (29.3%). Eight
is a descriptive screening threshold, not an established profitability cutoff.
Every emitted instruction still has an external entry; these windows are not
single-entry optimization regions and do not establish precision or liveness.

Among four hot chunks from the existing iPhone profile:

| Chunk | FP operations | Memory operations | Maximum FP/window, memory splits / hypothetical transparent memory |
| --- | ---: | ---: | ---: |
| 804B60A0 | 378 | 493 | 25 / 33 |
| 805170A0 | 3 | 322 | 2 / 2 |
| 800180A0 | 10 | 323 | 3 / 3 |
| 804330A0 | 89 | 387 | 11 / 14 |

Thus a paired-FP-only design cannot address all the observed hot code. Retained
instruction samples in 805170A0 include entry PC loads, switch-table lookup,
stack setup and register restoration. These samples support investigating
execution boundaries; they do not attribute the whole chunk's cost to them.

Private per-chunk details and receipts remain in
`generated/region-feasibility-20260916/census.json`.

## Existing infrastructure makes this feasible, but not automatic

The maintained DolRecomp fork already has `DolIRStateSlot`, scalar/vector types,
`STATE_READ`, `STATE_WRITE`, PHI operations, effect flags, helper descriptors and
explicit branch/exit terminators. Its LLVM emitter already allocates local state
and tracks used/dirty slots. A new IR or from-scratch compiler is unnecessary.

However, `llvm_runtime_lowering.cpp::emitExactPaired` synchronizes source/destination
pairs and FPSCR to CPUState, calls exact helpers, then reloads destination/status.
Consequently local-state support alone does not preserve residency across the
important arithmetic path. Some C helpers inline in the linked product, so
these source observations are not a claim about universal call overhead.

The memory lowering already distinguishes ordinary RAM and external callbacks.
External reads materialize state and reload used values after callbacks.
GXRuntime stores additionally handle reservations and a potentially mutating
write journal. R825 already rejected a simple `restrict` annotation: the final
instructions were identical. We need an explicit dataflow contract, not another
aliasing hint or cached RAM pointer experiment.

[QEMU's helper contracts](https://www.qemu.org/docs/master/devel/tcg-ops.html#helpers)
are a useful general precedent: helpers specify whether they read or modify
guest state, permitting the translator to avoid unnecessary synchronization.
Its liveness analysis removes dead work. Our implementation would need audited
per-slot effects, not merely mark existing stateful FP helpers pure.

[LLVM MemorySSA](https://llvm.org/docs/MemorySSA.html) can support reasoning
about memory dependencies; it does not prove guest memory is independent of
CPUState or make callback side effects disappear. These remain runtime/compiler
contracts that we must establish ourselves.

## Concrete implementation boundary

Proceed incrementally in DolRecomp/RecompCore, with a reusable pass rather than
game-specific substitutions:

1. Audit and encode helper read/write sets, possible exceptions and observers.
   Unknown helper or callback means full state visibility. Reuse DolIR descriptors
   and existing semantic tests rather than add a parallel instruction decoder.
2. Build actual predecessor/entry information and backwards register liveness.
   Optimize a normal entry while retaining general interior-entry fallbacks.
   Initially stay within bounded regions; cross-chunk native recursion is not
   required to establish whether retained state lowers actual execution cost.
3. Keep integer and FP state local. Lower arithmetic using value operands/results
   with explicit status effects where justified. Track precision only under
   proven successful-write conditions; do not infer it from opcode names.
4. Retain values across ordinary RAM access only when the access and alias contract
   permit it. At a callback, journal, exception or unsupported mode, materialize
   exact PC/cycles/live state and use the existing path. Do not prevalidate later
   accesses across a callback that can change pointers or memory.
5. Preserve original timing checks and invalidation boundaries. Profitability
   must account for entry guards, fallback frequency, added code size, register
   pressure and spills. More local variables can make code slower.

The next meaningful prototype is a generic state/effect pass operating on both
integer-heavy and FP-heavy regions, with before/after machine code inspection.
The present census is an opportunity screen, not that pass. Do not expand opcode
coverage or build a whole game until the selected regions show that actual
redundant work is removed. Existing differential oracles cover callbacks,
interior entries, unusual FP modes and state aliasing and can be reused.

## Assessment

- **Feasible foundation:** existing IR, runtime boundaries and correctness
  harnesses avoid a full rewrite.
- **Material benefit remains unproven:** source prevalence is not execution time;
  neither a static census nor prior routine gains justify an FPS prediction.
- **Cross-game usefulness is plausible for PPC/GameCube/Wii titles:** analyses
  depend on instructions, control flow and runtime contracts, not Galaxy symbols.
  No second game's corpus was assessed here; portability is not demonstrated.
- **Main engineering risk:** maintaining exact state at observers while allowing
  enough connected work to amortize guards. The prior rejected micro-optimizations
  show that locally valid transformations can still lose overall.

The implementation priority is shared state/effect analysis spanning integer,
FP and ordinary memory operations. Vector arithmetic is one consumer of that
infrastructure, not the entire strategy. Product defaults and installed app
remain unchanged; compiler/runtime changes will use maintained forks and pins.
