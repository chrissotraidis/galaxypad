# R795: offline reference GPR register cache across a callback

Implemented tests/probe-arm64-static-cache.py and its exporter/driver. It compiles
the unmodified pinned JitArm64_RegCache.cpp with the actual reference headers and
ARM64 emitter. A private include-path host supplies the emitter and the original
ConstantPropagation object without constructing the runtime JIT. Unsupported FP
conversion methods abort explicitly; no floating-point implementation is claimed.
The private header is under tests/aot-support and is not on product build paths.

The exported sequence computes guest r3=r3+r4 and r7=r3+r6 through the real cache,
flushes all pending values, calls a symbolic helper, and computes r5=r3+r6 after
that helper changes every guest GPR. The cache must reload the changed values.
All callee-saved GPRs potentially used by the reference allocator are saved and
restored in the generated function. Assembly becomes an ordinary linked executable;
the exporter only writes an ordinary non-executable array.

The test uses compiler-derived PowerPCState GPR offsets in aligned byte storage.
PowerPCState itself owns noncopyable InstructionCache state, so blindly memcpying
or fabricating the C++ object is inappropriate. The final test never constructs
one. It checks all bytes against expected storage after100,000 randomized cases,
including callback observations of both pending writes and callback mutations
of every GPR. Bytes outside the GPR array retain their sentinel pattern.

Initial45271 failed for missing GXRuntime include path.70607 then exposed the
noncopyable object/destructor issue.95202 passed after switching to byte-layout
storage, with a warning pragma typo. Final44457exit0, empty stderr after fixing
the pragma. Evidence generated/arm64-cache-r795d.json and corresponding.err.
Reference cache SHA ddb545c1c708066ca19e46dad4fddf788e0ebd11604e5417df402e893c0b825a.

This proves reference GPR allocation, flush and reload work in offline statically
linked output. It is not yet a PPC decoder or complete block exporter, actual
CPUState/PowerPCState adapter, FP cache, memory callback implementation, exception/
cycle model, unwinding proof or performance result. Broad app regressions were
not rerun for this private harness. No game/app/core/module/save changed and no
Simulator was started.

Next connect decoded PPC instructions and the explicit architectural-field
adapter, then include a memory slow path and complete block exit/cycle behavior.
Preserve the existing module ABI and fallback until that implementation passes
whole-block differential checks. Do not benchmark this synthetic cache sequence
as evidence of gameplay speed or repeat the unchanged transport checks.
