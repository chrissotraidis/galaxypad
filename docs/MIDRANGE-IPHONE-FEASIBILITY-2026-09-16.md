# Mid-range iPhone: implementation feasibility pass

> Session closed: [current build, owner assessment and research handoff](SESSION-CLOSE-2026-09-16.md).
> This document retains the evidence and acceptance limits of its dated experiment.


This continues [the port architecture research](PORT-ARCHITECTURE-RESEARCH-2026-09-16.md).
No installed app changed. The new result is a bounded CPU-cache equivalence
experiment, not a frame-rate improvement.

## What changed in this assessment

GPU vertex conversion has a smaller CPU-state obstacle than a first reading
suggests. The current software loader retains the final three input positions
and matrix indices, plus normal state from the final input record. The renderer
uses these for depth-slope and missing-attribute state. It does not follow that
the CPU must decode every vertex to preserve those particular caches.

The experiment in `scripts/probe-vertex-tail-state.py` checks this proposition
using extracted, hash-verified current Dolphin converter bodies and RunVertices.
It compares full-batch cache results with decoding only the final min(count,3)
records from the same starting caches. Both execute the original converters.

Result: **5,376 comparisons passed under ASan/UBSan**. Cases cover 1–8 texture
coordinates; 0, 1, 2, 3, 4, 17 and 128 vertices; input offsets 0, 1 and 7;
random indexed data; all eight skip masks for the final three records; and
per-vertex position matrix IDs. The format family is u16-indexed s16 XYZ,
s16 normal, RGBA8888 color and s16 ST coordinates. The reused fixture also
passes its 819 full-loop control/candidate comparisons before this experiment.

The position cache is indexed by remaining input records, not the final three
successfully emitted vertices. A skipped position leaves its cache slot unchanged;
normal and matrix cache effects must follow their own rules. A generic "take the
last three visible vertices" implementation would be wrong.

Limits: fixed initial cache patterns and scale settings, ordinary single normals,
no texture-matrix stage, no NTB/three-index normals, no direct/float vertex formats,
no cross-draw state-transition coverage. This proves neither full decoded output
nor skip compaction, GPU arithmetic, culling, complete device behavior or speed.
The initial historical fixture rejected changed source pins and an obsolete fmt
include location. The new script uses explicit reviewed current pins and the
maintained fmt location; the historical probe remains unchanged.

Reproduce with a new, nonexistent output directory:

```sh
python3 scripts/probe-vertex-tail-state.py --output generated/vertex-tail-state-check
```

Private output for this run: `generated/vertex-tail-state-20260916-verified/`.
The test uses synthetic inputs and does not read the game image or a save.

## A concrete bulk-conversion design

1. Resolve the current vertex format and input record stride once per draw.
   Keep the generic decoder for unsupported formats and edge cases.
2. Preserve guest input memory at the same observation point as the current
   decoder. Snapshot required data into owned upload buffers; neither unified
   memory nor a shared Metal buffer makes later guest writes safe automatically.
3. Decode the small CPU cache tail with the established remaining-record rules.
   Handle sentinel indices and output primitive/index construction explicitly.
   The tail test does not remove the need to scan indices or compact skipped
   vertices when those cases occur.
4. Convert the bulk data with a specialized AOT CPU function first. This produces
   a full-output reference path and a bounded fallback useful on every platform.
5. Explore a Metal compute conversion for sufficiently large batches, or vertex
   pulling that decodes attributes in the vertex shader. Compute can produce the
   existing native layout; pulling avoids that intermediate buffer but requires
   deeper shader/layout integration and may repeat attribute decoding.
6. Retain buffers until GPU completion and preserve command ordering. Avoid a
   CPU wait for converted vertices. Where CPU culling or other consumers require
   the complete decoded batch, retain the reference path initially.

Per-draw compute dispatch is not automatically useful: tiny draws can lose to
submission costs, additional passes and memory traffic. Aggregate compatible
work where ordering permits, and make the threshold depend on total measured
conversion/upload/encoding cost. Do not guess a universal vertex-count threshold.

Source anchors in the selected Dolphin tree:

- `VideoCommon/VertexLoader.cpp`: RunVertices and PosMtx_ReadDirect_UByte.
- `VideoCommon/VertexLoader_Position.cpp`: indexed sentinel/cache behavior.
- `VideoCommon/VertexLoader_Normal.cpp`: final-record normal cache behavior.
- `VideoCommon/VertexLoaderManager.cpp`: format refresh, CPU culling, draw splitting,
  output allocation and indices. It already caches loaders by VertexLoaderUID.
- `VideoCommon/VertexManagerBase.cpp`: depth slope and normal fallback consumers.
- `VideoBackends/Metal/MTLStateTracker.mm`: existing shared upload resources and
  command completion handling; a new conversion path must fit their lifetimes.

## What other projects teach about this design

[RT64](https://github.com/rt64/rt64#architecture) defers rendering operations,
performs RSP vertex transformations on GPU compute, and decodes textures on the
GPU. The transferable pattern is preserving necessary game-visible state while
moving bulk work to the GPU. Its N64 transformations are not the same operation
as our Wii vertex unpacking; neither its implementation nor its gains transfer
automatically.

[Apple's GPU performance guidance](https://developer.apple.com/videos/play/wwdc2020/10632/)
explains why unnecessary pass dependencies and attachment load/store traffic
hurt Apple GPUs. A compute conversion should therefore be assessed within the
whole render schedule, not timed as an isolated kernel. A faster kernel that
adds stalls or pass breaks can still make the frame slower.

[Dolphin's 2023 report](https://dolphin-emu.org/blog/2023/02/12/dolphin-progress-report-december-2022-january-2023/)
provides a useful counterexample: CPU culling improved some titles but made
Galaxy slower, with roughly 2–3% added CPU work and insufficient draw-call savings.
Our source default is false; this is not a readback of the installed phone's
effective settings. Do not enable it as a generic optimization. The report also
describes VBI Skip improving playability on weak devices without directly raising
FPS, with title-specific failures. That would require an explicit timing-policy
experiment and is not evidence of correct full-speed Galaxy gameplay.

## Display-list caching: narrower than previously suggested

The runtime already caches format loaders and batches draws. A new cache must
avoid actual repeated parsing or conversion, not duplicate those facilities.
Start with decoded command structure keyed by list bytes and relevant incoming
format state. Preserve all command state effects on replay. Converted geometry
requires additionally validating external attribute arrays, bases, strides and
other interpretation state. Transforms can change while source geometry remains
stable, but some titles also rewrite positions/normals through CPU skinning.

Cross-frame reuse rate is still unknown. A useful capture must include draw
format, referenced memory and ordering, not just native stack samples. A Simulator
capture could establish those semantics and supply replay fixtures. It could not
establish iPhone performance, memory bandwidth or thermal behavior.

## What is needed for the phone target

Mid-range is not a fixed hardware specification. Record the actual target model,
OS, resolution and thermal state before making a supported-device claim. The
retained saturated CPU-thread capture remains the performance evidence for this
assessment; no fresh phone run was necessary for the cache-state experiment.

The first acceptance milestone is an end-to-end conversion implementation that
matches required output/state, has bounded memory use and actually reduces total
work. Then a physical run should answer whether CPU savings survive upload,
GPU execution and sustained thermal limits. A dedicated replay harness can
screen candidates without repeatedly asking the user to navigate identical scenes.
Only later gameplay validates broader compatibility and sustained frame rate.

The main game thread is still a separate constraint. Bulk graphics improvements
may reduce power and shared CPU pressure, but cannot be assumed to solve it.
Keep function-level recovery/native service selection alongside this work; the
previous matrix-only candidate lacked coverage. No 60 FPS or supported-device
claim follows from this feasibility pass.
