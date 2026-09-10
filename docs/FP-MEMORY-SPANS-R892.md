# R892: memory-inclusive routine selection

R891 corrected the movie diagnosis; this turn implements a broader source/coverage
query rather than replaying gameplay or changing playback policy. Extended
rank-fp-islands.py with explicit --include-memory. Default arithmetic-only ranking
is unchanged. Memory locations and memory/conversion helpers are now exposed;
unknown coverage, unsupported mnemonics and address gaps still terminate spans.
Tests pass for the original mode and the larger memory-inclusive span. This is
inspection data, not a proven control-flow or fusion transformation.

Actual source-hashed R792 coverage produces generated/fp-memory-spans-r892.json:

| Start–end | Instructions | Memory observers | Retained site attempts |
| --- | ---: | ---: | ---: |
|804B6BCC–804B6C08|16|6|361,738,914|
|804B6CB8–804B6CEC|14|6|269,911,865|
|804B64A4–804B6540|40|11|49,630,684|
|804B6890–804B68DC|20|11|33,615,349|

The top two include the already investigated normalization and cross-product
regions. They are not new arithmetic candidates; do not restart them merely
because surrounding memory operations are now counted. Historical attempts do
not establish current scene CPU share or completed instructions.

## Selected larger implementation boundary

Inspect 804B64A4–804B6544 as one41-instruction containing routine, including its
return. Actual generated source has a41-cycle internal-entry charge at64A4,
paired input loads from r4, a scalar constant load through r2, arithmetic through
f13, and paired output stores through r3. Stores are interleaved with arithmetic;
moving all stores to the end would change observable order. Last store6540 is
followed by blr6544. Every external suffix charge must remain exact.

Before candidate lowering, build the complete routine oracle with original
memory helpers and ordered callbacks. Required distinctions: GQR0 types/scales,
MSR/FP availability, FP rounding/NI/exception gating, both FPR lanes, every legal
suffix, input/output overlap, CPUState/RAM aliasing, and callbacks that mutate
registers/mapping between stores. No assumption that r3/r4 mappings or GQR stay
constant across an arbitrary callback. Normal RAM fast-path qualification must
be explicit and fail to the original routine when its contract is not met.

This is a materially larger boundary than the rejected nine-op scratch region,
not evidence that it will be fast. Keep real CPUState as canonical reference;
do not revive full-state copies or restrict annotations. Inspect final generated
code and actual-policy full-routine cost before any module build. If there is
no material transferable reduction, do not promote a routine-only patch based
on historical counts. No FPS improvement or product acceptance claimed.

No runtime, Simulator, app/module/save change. Full original PRD remains active.
