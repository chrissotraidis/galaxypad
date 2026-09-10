# R759: bounded vector execution experiment

## Evidence and decision

R755 phase-separated gameplay census:6326386interpreted steps,6271844 in
four exception-vector regions, no drops. This is NOT99%of CPU time. R758
physical vector RAM matches exact RMGE01 DOL templates plus exception numbers.

Current SingleStepInner performs HLE lookup, Read_Opcode, opcode-info lookup,
instruction dispatch, exception handling, last/current-PC update and performance
monitor accounting for EACH instruction. Chassis also checks dispatchability,
host-call membership, budget and CPU state between interpreter instructions.
These are the contracts to preserve, not permission to discard them.

MMU::TryReadInstruction uses instruction-cache ReadInstruction after translation.
Physical RAM equality does not prove fetched instruction equality. Candidate
validation must use the fetch view, preserve fetch exceptions and respect cache
invalidation. Do not bulk-prefetch beyond current instruction if that can change
cache/exception behavior relative to the baseline.

## Existing backend considered

CachedInterpreter emits callback/operand DATA. CachedInterpreterCodeBlock is
CodeBlock<CachedInterpreterEmitter,false>, whose allocation uses ordinary memory
pages, not executable memory. Its name Jit is not proof of host-machine-code
generation. Reusing interpreter operation implementations is attractive.

However, its Run() owns the timing loop and never yields specifically when AOT
coverage resumes. ExecuteOneBlock is private, and the static-recomp core exposes
an EmptyBlockCache, not a transparent cached-interpreter invalidation bridge.
Do not assign it to m_fallback_jit and call Run() as an unmodified replacement.
No backend enabled or new runtime translation introduced by this audit.

## Candidate boundary

Use only four statically compiled instruction plans derived from exact templates,
not runtime-generated machine code or a general mobile cached-code backend.
Retain authoritative interpreter operations for privileged registers, memory,
rfi and branches. Initially preserve instruction fetch at each actual PC and
compare to the expected word; unexpected instruction/entry routes normally.
No hardcoded physical-RAM reads as a substitute for fetch/MMU/cache behavior.

Preserve HLE hooks, debugger stepping/tracing and breakpoints (or explicitly
reject candidate mode when enabled), pending synchronous exceptions, MSR
privilege/translation state, partial budget exits, PC/npc/last-PC, performance
monitor events and cycles. rfi must return immediately to normal chassis routing.
An observed template does not authorize assuming it never changes or that an
instruction's destination/context memory cannot alias vector storage.

The generic path executes34instructions; syscall7 and includes three HID0
operations that existing AOT still sends back to the interpreter. A pure AOT
address alias is not the proposed solution and might increase state synchronization.

## Test and stop gates

1. Fixed plan recognition and every interior entry: exact supported words only,
   mutation/cache-view mismatch rejection, no guest mutation on refusal.
2. Original-versus-candidate execution using actual interpreter operation bodies:
   full state/affected memory, cycles, exception/privilege/translation exits,
   HID0 cache side effects, hooks, stop/budget boundaries and invalidated code.
3. Synthetic host-work/time comparison must show enough gain to justify a core
   build. No whole game-module link is needed for a core-only experiment.
4. Same plaza with diagnostics OFF for timing, matched VI/thread CPU and repeated
   order. Keep original semantics and visuals. If net CPU/VI gain is below8%
   and not repeatable, park this bounded design; don't spend many iterations
   rescuing a tiny result. Never infer net saving from fallback step percentage.

Runtime bytes/provenance are established enough to stop more address hunting.
Remaining question is whether useful overhead can be removed under these
contracts. Full original PRD, SunPad fidelity, mobile/no-JIT, graphics stability,
story/audio/device gates remain unchanged.

## R760 implementation checkpoint

`apple/experiments/vector-execution/plan.h` implements pure recognition of the
current fetched word at all121 supported positions. It does not fetch, execute,
cache, mutate guest state or connect to the product interpreter. Tests compare
against the pinned DOL, reject all3872 single-bit mutations and unsupported
entries/aliases, and pass ASan/UBSan. This completes the recognition portion of
gate1 only; real instruction-cache invalidation and execution gates remain open.

## R761 dispatch-only candidate: rejected before integration

`dispatch.h` stores existing interpreter function pointers for fixed plan words.
It changes no runtime source. The sanitizer test compiles upstream dispatch
tables and instruction definition with spy operation bodies, verifying exact
operation/operand identity. No instruction-semantic proof is claimed.

The optimized dispatch-only ABBA screen measured baseline4.35133ns,
guarded7.07893ns, guarded6.72917ns, baseline4.37446ns per instruction, with
identical checksums. Recognition overhead exceeds the saved opcode dispatch.
This is not a game benchmark or a bound on larger chassis improvements. It is
enough to reject this narrow candidate: no integration, full core build or
microtuning. Establish whole-fallback CPU cost before a broader execution design.
