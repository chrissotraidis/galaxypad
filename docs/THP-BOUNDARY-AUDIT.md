# THP decoder boundary audit — R188

## R340 — first-pass specialization contract (source evidence only)

R342 implements an offline local-state prototype in scripts/local_thp_columns.py.
It retains the exact phase instructions and intermediate stores. Eligibility
preflights144/264/256mapped disjoint bytes and rejects journal/alias/unsupported
state before mutation; original paths handle rejects. Local CPU is copied back
at every original yield/completion. Initial128candidate comparisons/build pass
with32actual hits, in addition to the original32resume comparisons. Eighteen
explicit rejection tests added. No full-kernel, arbitrary-input, timing or
runtime acceptance yet; candidate is not integrated into a module.

R341 adds executable reference evidence in tests/test-thp-first-pass.py:
32comparisons per sanitized/O2 build across4paths,4rounding modes and direct/
RAM-boundary layouts. Negative-budget runs yield at7taken backedges and match
uninterrupted CPU/memory/normalized callback-journal digest/hostFPflags.
DC/quarter/half/regular runs preserve64/112/80/64workspace journal writes,
including overwritten intermediates, and reservation invalidation. Boundary
callbacks confirm non-DC reads16/8bytes past logical coefficient/quant blocks.
No optimized implementation, alias eligibility or speed evidence yet.

Rechecked accepted extracted source SHA98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991
and exact-DOL boundary scan in generated/thp-boundaries-r340.json. Petari
THPDec.c SHAe93f9299c226f616bd2818f889c5525a66c54c17f25746765444bbfd0dc65ee8
is a reference correspondence, not an independently proven RMGE01 replacement.

The next candidate boundary is the no-Y column phase at80452750 up to, but
excluding,80452970. Keep the original prologue, second pass, output callbacks,
epilogue, every interior entry and caller dispatcher. This phase writes the
256-byte workspace; it does not yet write output pixels. It has four original
backedge/yield checks (DC, quarter, half, regular paths); keep their precise
PC/downcount/CTR observations. Do not charge the phase as a fixed-cost block.

Important read-ahead contract under baseline GQR5 signed16/GQR0 float:

- Regular path804528D4 reads32bits at r3+28;8045292C loads the next coefficient
  pair at r3+16 and updates r3. Both occur before the CTR test at8045296C.
- Quarter and half paths similarly prefetch before their counter tests.
- On the eighth column, r3 is input+112 before these reads. The r3+28 word
  reaches input+143. Thus a direct-memory preflight needs144coefficient bytes,
  not just the logical128. The extra reads may be observable at a boundary.
- Quantization prefetch80452930 loads two floats at r5+32 and updates r5
  before the counter test. On the final column this reaches quant+263:
 264bytes, not the logical256. Do not omit those reads or their register effects.
- These extents assume the initial CTR8 and normal entry. They are not valid
  for arbitrary interior state or unusual GQR types/scales.

Before any local-register/copied-state candidate: prove each complete mapped
span with non-underflowing RAM sizes and no guest wrap; reject active journal,
exceptions, missing FP/LSQE, unsupported GQRs, CPU/global-pointer aliasing and
unsupported input/workspace overlap. Keep ordering of reads/writes and all
reservation effects. Rejecting unusual state must happen before any mutation;
fallback must run the original phase on the original CPU pointer. No callback
may see a copied CPU address. A copied-state result must be committed before
every original yield and before rejoining80452970. These are requirements to
prove, not implemented safeguards or speed evidence.

Next: an exact emitted first-pass oracle with boundary read-ahead callbacks,
aliasing, all four paths and yield states, then one isolated local-state
candidate. Do not introduce a generic JPEG IDCT, skip stack/output memory,
or revive parked normal-entry/helper-inline/DC candidates under a new name.

G6 remains open. This is feasibility evidence, not a replacement implementation
or a performance result. The normal app/module is unchanged.

## Exact-input evidence

`scripts/audit-thp-boundaries.py` reads the staged, SHA-pinned RMGE01 DOL and
reports function bytes' hashes and direct/conditional/indirect branch edges to
ignored `generated/thp-boundaries-r188.json`. It does not modify the input.
Petari's THP source and **RMGK01** symbol map suggest the names below; the Korean
addresses are not used as RMGE01 addresses. Size/call-shape correspondence is
not a proof of semantic equivalence across regions.

| Reference correspondence | RMGE01 start | Bytes | SHA-256 |
| --- | --- | --- | --- |
| Inverse DCT, no Y offset | `804526e8` | 1164 | `6ca70af3cdf7aac89357b1bec5d1421e96db556a0073aff582768987d6d8d5c6` |
| Inverse DCT, Y8 offset | `80452b74` | 1172 | `d4bfc9abc7e6ab3c0e56216f5b566b2a48d202ddf22b90782ab6984f466c7545` |

Both actual regions have eight conditional branches, no linked branches, no
direct branches outside the region, and exactly one indirect branch: the final
unconditional `blr`. The scanner asserts these properties. This does **not**
exclude external entry into an interior instruction, memory faults, floating
point unavailability, or host scheduling exits in generated execution.

The surrounding row routines call the Huffman routines and these transforms,
then cache-transfer helpers. A whole-frame host decoder would additionally need
bitstream, restart/predictor, cache/DMA, frame progression, and audio coordination
contracts. That is not the smallest next experiment.

## Observed state contract

The accepted generated chunk `chunk_1102_text1_804520A0.c` supplies the current
execution oracle. Its chunk entry is not the logical transform entry.

- Input correspondence: r3 coefficient pointer; r4 X position.
- Both functions allocate a 128-byte guest stack frame. Scalar and paired
  saves/restores of f25–f31 are observable memory operations, not disposable ABI
  bookkeeping.
- No-Y setup loads five constants via r2 offsets 8408–8424 and a quantization
  pointer via r13-9056. Workspace address construction resolves to `806243a0`.
- Caller sets r13-9024 from the literal width 512 (or chroma 256), and
  r13-8992 from the output pointer. The transform consumes those as width/base.
  These are verified relative locations, not assumed absolute SDA addresses.
- Paired loads use GQR5 for coefficients and GQR0 for float data; output stores
  use GQR6. Reference setup uses GQR5 `00070007`, GQR6 `3d043d04`; a future fast
  path must validate actual runtime state rather than presume setup always ran.
- Workspace, destination, stack, GPRs, paired FPR contents, CR, CTR, FPSCR,
  exception state, PC and downcount belong in the comparison. Memory callbacks,
  write journals, reservation invalidation, translation/locked-cache behavior,
  and early returns must not silently disappear.
- Sparse/DC, half, quarter and general paths change executed work and cycle
  charging. Replacing the entire call with one arbitrary cycle charge is not
  equivalent to the current runtime.

## Next falsifiable step

R198 prepares the actual private chunk overlay with `extract-thp-kernels.py`.
Final candidate lives in generated/thp-kernels-r198-exits (the initial r198
void-return artifact is superseded and was never compiled). All584labels become
PC-setting trampolines into two static noinline+flatten kernels. Original outer
switch charges and return dispatcher are byte-preserved; kernel switch charges
are removed, original instruction-body charges remain. A restore assertion
proves the original outer source outside these two regions is unchanged.

Kernels return false for early helper/yield exits and true only through their
guest-return dispatcher. This distinction is necessary even if a callback sets
an exception while changing PC to a valid outer return target; blindly invoking
the outer dispatcher after every kernel exit would incorrectly continue.

`--kernels` uses the actual full reference/candidate chunks in the oracle.
864cases match the established digest under both variants' sanitized/O2 builds
(candidate O2 includes ThinLTO). Unrelated cross-chunk callees abort if reached;
none is reached by this fixture. These tests cover real transform entries and
their timed resumes, **not** every arbitrary interior state or return into caller.
Add bounded caller-return and fault-PC cases before a one-chunk module link.

R197 separate-source ThinLTO timing retains the gain: A26997.55/B24434.70/
B23704.95/A26947.00ns across12means,10.76% lower candidate time. Benchmark text
98304->196608bytes (+96KiB). This uses no combined-source CPU globals, but still
lacks final module PGO/layout and whole-game evidence.

Integration audit found an important distinction: the caller at80452554 uses
an **internal goto** to804526e8, not a host call through the chunk's entry switch.
The original switch separately charges external nonleader entries. Any extracted
kernel must preserve both routes:

- Keep original outer entry charges. Do not charge them again in the kernel's
  entry switch; kernel block-leader/loop charges remain original.
- Trampolines must set the correct PC before calling a kernel, since the internal
  goto does not necessarily leave ctx->pc at the transform entry.
- Retain the original outer return dispatcher after a kernel returns. A guest LR
  in the caller must continue there; negative-budget yields must return to the
  chassis. Do not replace every return with an unconditional outer return.
- All584instruction labels across the two regions need preserved external entry
  behavior; arbitrary interior entries cannot be silently remapped to the start.
- Keep kernels out of line at the outer chunk boundary while flattening their
  helpers, avoiding duplication at hundreds of entry sites. Verify that compile
  shape with the oracle before linking. Do not duplicate CPU globals.

R196 tests whole-transform compilation locality rather than another scalar
helper change. With all actual helpers visible in one TU, flattening just the
two transforms preserves the864case oracle and reduces offline execution time
11.47%, while raising entire benchmark text120% (+96KiB). This is a meaningful
candidate hypothesis with an instruction-cache tradeoff, not a promotion.
First verify separate-TU ThinLTO behavior matching the module architecture;
any eventual extraction must preserve original return dispatch/caller behavior,
all interior entries and global memory-journal state without duplicating globals.

R192's offline A/B/B/A benchmark gives3.255% lower time for the 12-site candidate
across equally weighted synthetic patterns, including state reset/yield dispatch,
excluding initialization and oracle hashing. It does not measure movie weights,
final-link/PGO effects or host runtime. See PERF.md. Do not turn that number into
an FPS promise or promote without evidence of worthwhile end-to-end impact.

R191 introduces an isolated candidate (`--merge-fprf`) at these 12 PCs:
`804527c4,80452850,80452858,80452914,8045291c,8045293c,80452c50,80452cdc,80452ce4,80452da0,80452da8,80452dc8`.
It changes only existing arithmetic calls to their already-tested deferred-FPRF
versions when a later actual FPRF writer is reachable through exact paired-merge
instruction shapes and optional existing deferred operations. Unrecognized
instructions, memory, branches and other effects terminate the search. The first
arithmetic's successful FP-availability check and absence of intervening MSR
writes make intervening availability guards non-observing on that path.

Reference/candidate each pass O1 ASan/UBSan and O2: all864cases match the R190
digest. This is a bounded extension of the accepted classification policy, not
a whole-decoder replacement. No product source/module is changed. Next measure
offline execution excluding harness hashing and setup; reject if negligible.

R190 expands the oracle to 864 cases. O1 ASan/UBSan and O2 agree on digest
`aa72b761a9c075fd`: 432 yields, 288 FP-unavailable exceptions, 288 LSQE-disabled
program exceptions, 96 interrupted-output cases, 12,480 output callbacks,
17,152 pre-write journal calls and 864 reservation clears. Quantization varies
GQR5 load scale and GQR6 output scale; GQR0 remains the baseline float setting.
The zero block verifies both 128 and saturated-255 outputs under these settings.

Snapshots now include normalized full CPU state at each callback, pre-write
journal and generated exit, with journal pre-image bytes and final RAM/LC.
The interruption callback sets the exception field after the first output byte;
this tests the generated helper's observable early-exit behavior, **not** a
real MMU exception model. No callback identity/pointer alias equivalence is
established for a hypothetical copied-CPU fast path. Guard it out or prove it.

This is enough infrastructure to begin a bounded candidate comparison rather
than expanding fixtures indefinitely. A candidate must retain original paths
for unsupported state and preserve these observations. Demonstrate an offline
gain before another full module link, then require matched visible gameplay.

R189 implements the first slice in `tests/probe-thp-oracle.py`: accepted source
and CPU/helper/header hashes pinned, exact bodies and all external switch entry
charges extracted. An outside-chunk sentinel LR permits the return dispatcher
to be reduced to return without executing the caller. Yielded interior PCs are
resumed with a fresh zero downcount; each exit's PC/downcount is hashed.

Both O1 ASan/UBSan and O2 strict-FP pass 96 cases (two routines, six coefficient
patterns, two X offsets, two initial downcounts, FP available/unavailable).
They agree on digest `4a471989ef100135`, 84 yields, 48 FP faults and 3072 output
callbacks. All 48 completed blocks write 64 bytes, restore stack/f25–31; zero
coefficients produce 64 neutral pixels of value 128. Hash covers normalized final
CPUState, RAM/LC contents and callback PC/downcount/GPR/address/value/size.
This is cross-optimization consistency of the existing implementation, **not**
an independent mathematical decoder comparison or a replacement correctness test.

Initial fixture omission of HID2 LSQE correctly produced program exception at
vector 700; enabling LSQE fixed the test. Keep that requirement in the contract.
LSQE-off cases, varied GQR state, journals/reservations and more complete
callback/early-exit snapshots remain next. No product code changed.

Build an offline exact-generated-instruction oracle for these two entries with
valid coefficient/quantization/workspace/output/stack regions. Exercise zero,
DC-only, sparse, dense and extreme coefficients, both output offsets, GQR/FP
availability, callback and negative-downcount cases. Record all returned state,
memory and exits. Keep interior entries on the original path unless separately
proven. Only then evaluate a bounded specialization against that oracle.

Do not substitute a generic JPEG decoder, relax paired-single rounding, remove
guest cycle accounting, or install a runtime hook based on this audit. Existing
profiles locate substantial cost in this decoder family but do not yet measure
the exclusive cost of these two logical functions; no speedup is promised.
