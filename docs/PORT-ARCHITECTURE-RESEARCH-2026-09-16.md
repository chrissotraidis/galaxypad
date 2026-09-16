# What other ports suggest for GalaxyPad

Research date: 2026-09-16. This is a feasibility assessment, not a new device
performance result. No phone installation or production setting changed.

## Decision

Broaden the performance program from generated-code cleanup to eliminating
repeated console work at subsystem boundaries. The conservative state-access
pass produced identical optimized objects for both tested chunks; see
[the implementation result](STATE-ACCESS-IMPLEMENTATION-2026-09-16.md).
That experiment does not disprove more capable compilation, but it gives no
reason to keep extending that particular pass as the immediate FPS lever.

The most concrete bounded target is batched, ahead-of-time vertex decoding.
The larger architectural investigation is reusable geometry/display-list
processing plus selected native engine services. A whole renderer replacement
is not yet justified. A standalone matrix replacement was already investigated
and lacked meaningful sample coverage (STATUS.md, R685–R687).

## External evidence and its limits

### Dolphin: specialize the entire vertex conversion

[Dolphin's January 2015 report](https://dolphin-emu.org/blog/2015/02/01/dolphin-progress-report-january-2015/)
reports up to 50% faster execution in vertex-loader-limited Rogue Squadron II
scenes after its x86-64 vertex-loader rewrite. The transferable idea is converting
a batch through code specialized for its format. The reported percentage is
specific to those scenes and hardware, not an estimate for GalaxyPad.

Our selected software loader runs a vector of function pointers for every vertex
in `ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/VertexLoader.cpp`.
The existing 90-second iPhone capture attributes 16.774 CPU-seconds of leaf time
to RunVertices and four position/normal/texcoord/color conversion functions.
That is about 47% of the video thread's 35.933 seconds, assuming the expected
thread ownership; these are distinct leaf rows, not inclusive stack totals.
The CPU thread consumed 86.076 seconds, so video savings alone do not establish
a proportional frame-rate gain. Thermal headroom is a plausible secondary benefit.

An iOS-compatible adaptation is a bounded family of ordinary compiled decoders,
selected once per vertex format, with generic fallback. It must fuse conversion
work, not just unroll the function-pointer loop already tried. Descriptor/VAT
coverage and binary size determine feasibility. Reference equivalence must include
sentinel indices, output bytes, matrix caches and consumed source length.

### Aurora: work at the GameCube/Wii graphics abstraction

[Aurora](https://github.com/encounter/aurora) is a source-level GameCube/Wii
compatibility layer with GX support through Dawn/WebGPU, including Metal and
iOS support. This makes it a relevant architecture reference; its native API
does not directly accept our recompiled guest ABI or guest pointers.

At inspected commit `a906fc210dd9ab870a0f2348631180e942383989`,
[dl.cpp](https://github.com/encounter/aurora/blob/a906fc210dd9ab870a0f2348631180e942383989/lib/gx/dl.cpp)
contains a display-list optimizer. It combines compatible draws, converts supported
primitives to triangles, and flushes batches at intervening commands or format/size
boundaries. This is concrete source evidence of batching, not evidence of a
measured Galaxy speedup or a ready-made decoded-geometry cache.

Our pinned Dolphin `VideoCommon/OpcodeDecoding.cpp` explicitly notes that Galaxy
uses display lists for nearly all geometry and more than half its state. It also
warns that vertex formats determine command lengths, so lists cannot generally
be precompiled independently of state. This historical source observation is a
lead, not a measurement of our present scene's reuse rate.

Proposed application: treat a repeated display list as a reusable graphics
workload. Start by reusing its decoded command structure under an exact format
key. Later, retain converted vertex data when its referenced arrays also remain
unchanged. Transforms and genuinely dynamic attributes remain dynamic. Adjacent
compatible draws may be batched without changing ordering or state effects.

Correctness requires more than hashing list bytes: indexed attributes refer to
external memory; array bases/strides, VAT/VCD, matrix selection, writes, nested
lists and command side effects all matter. Reusing topology/command parsing is
a smaller first step than caching complete transformed geometry. Hashing all
inputs every frame may cost as much as decoding; measure validation overhead.
Page generations would require complete CPU/DMA/write coverage, not a partial
dirty bit implementation. Bound memory use and retain the ordinary decoder.

### UnleashedRecomp: replace the rendering boundary

[UnleashedRecomp](https://github.com/hedge-dev/UnleashedRecomp#high-performance-renderer)
describes a custom renderer translating game draw calls to modern APIs, removal
of unneeded hardware behavior, shader specialization, and elimination of redundant
texture copies. It also integrates pipeline preparation with asset loading.
These are architectural changes beyond CPU recompilation. The project is a PC
port; it provides no evidence of GalaxyPad's prospective iPhone performance.

GalaxyPad could eventually intercept a verified GX/engine submission boundary
and submit native batches, saving some guest command-building and host decoding.
However, inlined FIFO stores and game-visible GX state mean hooking GXBegin alone
is insufficient. Mixing native submissions with Dolphin's queue also requires
ordering, fences, EFB behavior and frame timing to agree. Prototype one bounded
submission path using the existing backend before contemplating a renderer swap.

Pipeline preparation during asset loading is a separate stutter improvement.
There is no evidence that it solves our sustained saturated CPU thread.

### N64ModernRuntime: replace console services, preserve game logic

[N64ModernRuntime](https://github.com/N64Recomp/N64ModernRuntime) supplies native
implementations of libultra services such as threads, queues, timers, audio and
task handling, with wrappers between generated code and the runtime.

The reusable Wii counterpart would be a native service library with per-game,
verified bindings. GalaxyPad's native THP path already demonstrates this style
of integration at a substantial subsystem boundary. It does not demonstrate
that another arbitrary SDK function is a useful gameplay target.

Candidate classes include animation/skinning batches, decompression and substantial
graphics submission routines. First attribute existing native samples to actual
guest function boundaries and aggregate by service, including outlined code.
Large generated chunks do not identify a hot SDK function. Replacing guest
thread scheduling first would introduce difficult interrupt, queue and timing
semantics without demonstrated payoff. Choose a substantial self-contained
service only after coverage is established; preserve unknown-revision fallback.

## Practical feasibility order

1. **Bounded vertex-decoder specialization:** known sampled work, reusable across
   games, existing reference implementation for differential checking. Success
   means lower total conversion cost including dispatch and output handling,
   with exact required side effects and acceptable binary size.
2. **Display-list reuse and batching:** promising Galaxy-specific source evidence
   and a concrete Aurora batching reference. Establish repeat rate and dependency
   stability before building a cache. Success means validation plus reuse is
   cheaper than full decode, and altered inputs/state reliably invalidate it.
3. **Native service coverage:** use retained profiles and verified semantic
   boundaries to select a large CPU-thread service. Do not revive matrix-only
   replacement or call an entire generated chunk a service. This work is needed
   alongside graphics preparation if the main thread remains the limiting stage.
4. **Direct native graphics submissions:** potentially removes work on both sides
   of the guest/host boundary, but has the largest integration and correctness
   burden. An isolated path is the feasibility gate; Aurora is a reference, not
   an assumed drop-in replacement.

Offline differential tests and replay of privately retained inputs can reject
bad candidates without another manual gameplay comparison. Captures must carry
the required guest memory and graphics state; a command stream alone may be
insufficient. These component results still cannot establish sustained iPhone FPS.

## Required scale of improvement

As a simplified fixed-work illustration, 35 to 60 FPS requires about 42% less
critical-path time per frame (1 - 35/60). Even a 2x improvement in a component
occupying 20% of that path removes only 10% overall. This explains why impressive
small microbenchmarks have not transformed the port. Thermal effects and parallel
threads make this a planning model, not a prediction.

The research changes what deserves investment; it does not change the acceptance
status. Sustained iPhone gameplay improvement remains unproven. Implementations
belong in maintained runtime/compiler forks, consumed through pinned commits,
without rebuilding the historical patches folder.
