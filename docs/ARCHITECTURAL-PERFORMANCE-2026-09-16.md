# Architectural performance review — 16 September 2026

Research and source inspection only. No new gameplay comparisons, builds,
installations, or performance claims. This changes the proposed investigation
priority from the dispatcher-wrapper candidate to the compiler's execution model.

## What the existing evidence supports

The last iPhone capture assigns 86.076 sampled seconds to the game CPU thread
over 90 seconds, including 64.438 seconds of generated-module leaf samples.
Run self time is 13.065 seconds; dispatcher self time is 6.025 seconds and is
already included in module time. See CPU-DEEP-DIVE-2026-09-15.md.
This prioritizes CPU execution but does not identify every load or prove cache
misses. Thermal state was serious; the amount of thermal throttling is unknown.

At 35 FPS, reaching 60 means approximately 42% less time per frame under fixed
conditions. Removing the entire observed dispatcher self cost would remove only
about 7% of sampled game-thread CPU work. That is illustrative arithmetic, not
an FPS forecast. The wrapper experiment cannot plausibly be the whole solution.

## External evidence and applicability

1. [XenonRecomp](https://github.com/hedge-dev/XenonRecomp#optimizations)
   describes making guest registers local using ABI knowledge, removing redundant
   context stores and register save/restore operations. Its reported executable
   size and frame-time improvements concern Unleashed Recompiled, not GalaxyPad.
   The useful principle is retaining values across substantial translated regions.
   Its exception and ABI assumptions cannot simply be imported into Wii execution.
2. [N64Recomp](https://github.com/N64Recomp/N64Recomp#how-it-works)
   builds native functions from function metadata, emits direct calls for known
   calls, and uses runtime lookup for indirect targets. This motivates recovering
   meaningful control flow instead of treating fixed-size chunks as functions.
3. [QEMU translator internals](https://www.qemu.org/docs/master/devel/tcg.html)
   explain direct block chaining and returning to the main loop when interrupt
   handling requires it. Transfer the execution model into static code; do not
   introduce runtime executable-code generation into the mobile port.
4. [Dolphin ARM64 register cache](https://github.com/dolphin-emu/dolphin/blob/master/Source/Core/Core/PowerPC/JitArm64/JitArm64_RegCache.cpp)
   and our pinned JitArm64_Paired.cpp provide a concrete reference for register
   residency, precision facts and paired arithmetic. This is a design reference,
   not a drop-in AOT backend. Our source includes explicit exceptional-value and
   fused-rounding handling that a naive NEON replacement would miss.
5. [RT64](https://github.com/rt64/rt64) defers graphics operations and uses GPU
   compute for vertex transformations and texture decoding. It illustrates moving
   entire classes of work off the CPU. Its N64 pipeline is different: GalaxyPad's
   CPU vertex-format decoding is not identical to RT64's RSP transformation work.
6. [Dolphin's block lookup report](https://dolphin-emu.org/blog/2023/11/25/dolphin-progress-report-august-september-and-october-2023/)
   shows reducing lookup indirection. This supports minimizing necessary lookups,
   but its large virtual-address table is not the first investment for our port.

## Priority 1: optimize regions, including their exits

The selected generated iPhone sources have a switch permitting entry at each
guest instruction, CPUState-backed register expressions, FP availability checks
and helper calls. Linked helpers can inline: source calls alone do not prove
machine-call overhead. StaticRecompCore_Run.cpp then reconciles cycles/timebase,
exceptions and dispatchability between native dispatches; state synchronization
is at burst boundaries, not necessarily every chunk.

The proposed unit is a verified control-flow region with explicit entry state,
local register values and explicit exits. Start with a connected hot arithmetic
region from the existing physical profile. Build register read/write and precision
facts across its blocks; emit paired operations where facts allow; keep known
internal branches inside it. Materialize guest state at externally observable
boundaries and retain the general path for unsupported entries or modes.

The key difference from previous attempts is a shared analysis of control flow,
register lifetime, precision and exit behavior. Neither bigger chunks nor calling
the same chunks directly supplies that analysis. Nor does renaming the existing
all-entry representation LLVM IR make it cheaper.

First engineering deliverable: an offline region analysis for existing hot chunks
that reports entry edges, register liveness, precision facts, helper side effects,
and mandatory exits. It must identify a meaningful connected region before a new
backend is expanded. Unknown indirect edges keep a fallback. Memory callbacks,
aliasing, exceptions, code invalidation and timing deadlines remain explicit
barriers. Preserve event boundaries with cheap local checks and cold exits;
do not merely enlarge the timing budget or ignore intermediate exceptions.

Historical constraints: R736's guarded calls lacked repeatable benefit; R907's
resident scalar lowering was slower; R908 records unsuccessful helper and
cross-product vectorization; R910's normalization improvement was only a local
routine result. Existing dead-FPRF and helper-inlining work must not be rebranded
as new. A region proposal must explain which retained cost those designs failed
to remove. This is a compiler workstream, not a promise of a quick FPS fix.

## Priority 2: precompiled vertex-format decoders

The physical profile also contains substantial position, normal and texcoord
decoding. VertexLoader::RunVertices iterates over function pointers for every
vertex. VertexLoaderBase can select an ARM64 code-generating loader elsewhere,
but that is not evidence that runtime-generated code is usable in our mobile lane.

Generate a bounded set of ordinary, ahead-of-time compiled decoding functions for
common descriptor/VAT combinations. Select once per format; decode a batch in one
function so byte swapping, scaling, indexing and stores can optimize together.
Keep the generic decoder for other formats. This differs from merely unrolling
the existing function-pointer loop. Bound specialization to avoid a code-size
explosion. Preserve index sentinels, array bounds, matrix indices, scaling and
output layout. GPU decoding is a later option: copied/snapshotted source lifetime
and synchronization costs must be resolved before it can replace CPU work.

This is secondary because reducing video-thread work does not automatically
shorten the saturated game thread. Reduced shared CPU demand may help thermal
headroom, but no such gain has been measured.

## Longer-term option and decisions

Function recovery can enable selective native implementations of substantial
engine services. [Petari](https://github.com/SMGCommunity/Petari) provides useful
structural research, but currently documents Korean RMGK01 support; addresses
cannot be applied directly to our RMGE01. It is not a ready native port. Begin
with semantic identification, not importing source or replacing a whole engine.

Do not prioritize more audio tuning, resolution changes, QoS guesses, lookup
microbenchmarks, or blanket fast-math. The current evidence supports reducing
the quantity of emulation work per game frame. Runtime/compiler implementation
belongs in maintained forks, not patches. No production defaults change here.
Future correctness and physical acceptance remain necessary; this research pass
does not request another manual comparison from the user.
