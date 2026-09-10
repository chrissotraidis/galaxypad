# R793: mapping contract and offline ARM64 direction

R792 made progress by correcting coverage and ranking executed work. R793 reads
the current implementation before choosing a broader compiler experiment.
No game, Simulator, product binary or save was changed.

## Memory lifetime findings

The selected generated header includes cpu/cpu.h; actual Ninja include order
resolves that to GXRuntime/include/cpu/cpu.h, which includes core/cpu.h.
This matters: other compiler/runtime headers are not the selected implementation.

| Boundary | Current source behavior | Consequence |
| --- | --- | --- |
|StaticRecompCore_Run.cpp106–109|Copies RAM/EXRAM base and real sizes at Run entry|Backing metadata normally lasts across many dispatches|
|Memmap.cpp88–119,547–563|Initializes real sizes; physical-region pointer indirection allocates/releases views|A regex for direct field assignment alone misses pointer writers|
|StaticRecompCore_Sync.cpp47–88|Copies architectural state, then calls module on_state_loaded with mutable guest pointer|SyncIn is an extension boundary, not proof metadata is immutable|
|StaticRecompCore_Hooks.cpp43–48|Passes mutable CPUState to module host_call|A module can change mapping fields|
|HookExternalRead/Write/Pointer|Translate addresses, propagate MSR, invoke MMU or gather pipe; do not directly assign mapping fields|No direct writer is not a transitive immutability proof|
|mod_abi.h30, mod_loader.cpp|Mod functions receive CPUState*|A stable-map fast path needs an explicit host/module contract|
|core/cpu.h stores|Acquire pointer, clear reservation, journal, then write using acquired pointer|Refreshing before the same store after journaling changes established behavior|
|GXRuntime/src/core/cpu.c reset/free|Preserves mapping fields across reset; free clears RAM pointer|Standalone runtime lifecycle differs from Dolphin ownership|

Production direct mappings may be stable, but deleting reads or checks based on
Run entry alone would break the general mutable-CPU/callback contract. A proposed
restricted fast path must verify backing ranges do not overlap CPUState, handle
all external callbacks and module hooks, and retain original acquired-pointer
store semantics. Host teardown cannot run concurrently with native execution.
This audit does not establish those conditions for arbitrary modules.

Existing R311 callback-bounded caching regressed. R452/453 per-access/table
variants failed their benefit gates. R451 restore specialization instead lost
PGO and had narrow scope; it was not proven slower. Keep these reasons distinct.
The new source audit does not justify reopening those implementations.

## Larger candidate: offline use of reference ARM64 lowering

The reference JitArm64_RegCache.h dedicates X29 to PowerPCState and X28 to memory
base. RegType distinguishes paired doubles, duplicated lanes, single lanes and
paired singles. PPCAnalyst supplies block analysis before emission. This is a
substantive dataflow difference from independently calling C instruction helpers.

An existing JIT code dump is not a loadable AOT module. Source inspection found:

- JitArm64_Compile.cpp85 analyzes live memory;251 specializes unmodified GQRs
  using the current runtime value. Offline specialization needs an explicit
  precondition/guard or a generic lowering, including interior entry handling.
- Jit.cpp230/277 embeds logical/physical memory addresses; helper calls pass live
  System objects. Those must become relocation symbols or runtime-context loads.
- JitArm64_RegCache.h uses PowerPCState offsets, not GalaxyPad CPUState layout.
  A state adapter is mandatory; raw struct interchange is invalid.
- JitArm64_Compile.cpp57 and129 use writable code-cache scope/block finalization.
  Jit.cpp exits branch to generated dispatcher/timing code. An offline exporter
  needs immutable linked text and explicit dispatcher/timing interfaces.
- BackPatch load/store code has a non-arena BAT-table route. It still uses live
  mapping/slow-call conventions; compiling it offline does not make them static.

scripts/audit-arm64-aot-boundaries.py records source hashes and concrete lines in
generated/arm64-aot-boundaries-r793.json:22 pointer-materialization sites,
35 helper-call sites,13 cache/mutation matches,26 live-state references.
These are textual source occurrences, not exhaustive relocation records, runtime
frequencies, or an estimate of porting effort. Multiline/call-indirect dependencies
require compiler-level inspection. No exported code has been linked or executed.

## Next implementation gate

Build one private offline block-export harness with explicit relocatable helper
symbols and a PowerPCState adapter. Use original DOL bytes, reference block
analysis and exact FP settings. Disable compile-time assumptions about unknown
GQR/MSR/memory state. Keep output as ordinary object code compiled/signed before
launch; no mobile code generation or runtime patching.

First prove a complete block with loads, arithmetic and a callback/exit can link
at different addresses and match architectural state, memory, exceptions and
charged cycles. Then measure the same whole block under actual build policy
against current AOT. Only a material reduction justifies wider opcode coverage
or a full game module. Small assembly snippets and opcode-count estimates are
insufficient. Preserve original CPU fallback and all original PRD goals.

This gate is an unimplemented next step, not a working backend claim. It should
resolve portability and state-contract risks before spending a full build cycle.
