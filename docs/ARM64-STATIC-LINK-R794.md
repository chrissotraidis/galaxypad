# R794: reference emitter to statically linked Apple code

Implemented a private transport prerequisite for the R793 offline compiler.
tests/export-arm64-link-probe.cpp uses the pinned Dolphin ARM64XEmitter in an
ordinary stack byte array. It exports six ARM64 instructions as assembly, with
the helper call represented as a symbolic branch relocation. The buffer is never
executable; no allocator for executable memory or runtime patching is used.
The helper is test arithmetic, not a PowerPC memory or emulator callback.

tests/probe-arm64-static-link.py compiles the actual reference emitter, exports
assembly, assembles a Mach-O object, verifies its external BR26 relocation and
links two ordinary dylibs with different helper implementations. A C driver
loads both simultaneously at different function addresses and verifies200,000
calls against expected unsigned arithmetic. Both linked libraries pass signature
verification. A second exporter process must produce identical assembly.

The same assembly compiles into arm64 IOS16 and IOSSIMULATOR16 objects, each
retaining the symbolic helper relocation. These objects were not executed on
mobile, linked into the app or device-signed. No Simulator was started.

Initial45621exit0 exposed a deployment-target mismatch warning in the assembler
invocation. Corrected all macOS compile targets to14.0; final95240exit0 has empty
stderr. Final rerun59375exit0 also passes export determinism across two processes.
Evidence generated/arm64-static-link-r794c.json and corresponding.err. Reference
emitter SHA1ac6f4c091373a61dbf1c5b4525c54967c3dba3158aebb54347b4aa5b72057d5.

Scope: this proves simple emitter output can use static helper relocations and
normal Apple object formats. It is not PPC compilation, reference register-cache
integration, CPUState adaptation, arbitrary relocation discovery, memory/exception/
cycle correctness, unwind support, performance or a completed backend. No game
code or data was needed. Temporary compiled artifacts are removed by the probe.

Next implement a complete PPC block exporter/state adapter. Reference RegCache
currently binds Init to JitArm64, GPR constant propagation to GetConstantPropagation,
and FP conversion to JitArm64 methods. That coupling must be handled explicitly
while preserving reference allocation/precision behavior. Do not extrapolate a
speed gain from the six-instruction transport test or replay it without changes.
Original goal, stable app and private movie candidate remain unchanged.
