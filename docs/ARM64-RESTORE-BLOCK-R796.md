# R796: real-DOL block export with callback and entry semantics

The private offline exporter now reads the exact DOL's words for80517584–80517590:
three lwz instructions restoring r29–r31 followed by blr. It validates opcode,
register and displacement correspondence to the hash-pinned generated source.
Unsupported opcodes reject before output. All four legal suffixes export as
ordinary assembly symbols using the actual reference ARM64 emitter/GPR cache.

The dispatch adapter accepts exactly those four aligned entry PCs, applies the
original generated switch's4/3/2/1 cycle charge, and invokes the corresponding
symbol. Five outside/misaligned PC cases reject without state/callback changes.
The exported loads call a statically linked helper using current mem_read32.
Each helper receives the exact instruction PC; pending GPR state is visible.
Return uses the current LR, including mutations made by a load callback.

Two state bindings were exercised:

- Initial aligned byte frame using reference PowerPCState GPR offsets, copying
  GPRs to/from the canonical CPUState at callback boundaries.
- Direct CPUState GPR offsets supplied through a private compile-time layout
  header. This eliminates those copies and the reference-layout frame. The
  reference allocator implementation is unchanged. CR/FP offsets are NOT adapted;
  supported opcode rejection confines this exporter to lwz/blr.

Reference behavior comes from the current generated C bodies and exact suffix
switch cases, not a separately guessed instruction model. The test compares the
complete CPUState and ordered callback PC/address traces. Cases cover all four
entries, MEM1/MEM2 and mirrors, boundaries, wrap, absent EXRAM, missing callbacks,
and a callback changing every GPR, base r11, RAM base/size, LR, FPSCR, exception
and downcount. Original lwz exception-continuation behavior is preserved.

Initial frame51861exit0 and direct39727exit0:30,464 comparisons each. Final direct
adapter69376exit0 includes rejected-entry tests; empty stderr. C++ helpers/driver
compiled with ASan/UBSan; emitted assembly is not instrumented by those tools.
Artifacts generated/arm64-block-r796-final.json/.err; earlier frame artifact
generated/arm64-block-r796.json. Run:

`python3 tests/probe-arm64-restore-block.py --direct-cpu`

The DOL hash is2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09;
generated chunk hash9b221ad3e1b417287e425640cc318e30fc5a6378e2956bf65a929be455acfd94.
Artifacts contain exact words/assembly. They stay private in generated/.

Limits: this is a four-instruction integration scaffold, not promotion of the
previously narrow restore optimization. Loads still call a conservative helper;
no performance test or game-speed claim is justified yet. No FP/CR lowering,
full instruction set, SMC/module dispatch integration, mobile execution, full
state adapter, arbitrary-address relocation or complete-game proof. RAM aliasing
with CPUState is not covered by this fixture. No shipping code/artifact changed.

Next extend decoded arithmetic and memory handling across a complete mixed block
while retaining explicit flushes at callbacks and exact suffix/exit accounting.
Then prove the broader state contract and evaluate code work under real compiler
policy before any whole-module build. Full original PRD/SunPad/device goal stays
active; movie/output proof does not need another unchanged replay.
