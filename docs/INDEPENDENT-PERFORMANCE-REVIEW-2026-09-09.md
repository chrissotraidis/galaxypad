# Independent performance review — supplied by Chris, 9 September 2026

The review below is preserved verbatim as external analysis, not established
fact or instructions overriding the PRD. See REVIEW-RESPONSE-2026-09-09.md for
source-checked disposition and the revised execution queue.

I'll start by reading the required docs, then dig into the source, build settings, and the generated artifacts.

Now I'll examine the generated code shape, memory-access helpers, dispatcher run loop, and vendor Dolphin EFB path directly, so the diagnosis is grounded in source rather than journal summaries.

Pulling the remaining independent items: dispatch-loop mechanics, per-frame dispatch counts, the memory-write journal, Simulator PGO build warnings, and the earlier rejected "primary-entry split" experiment.

Now pulling the last pieces: the chassis entry, how `bl` is emitted, the upstream's own documented experiments, the SMC inventory that gates direct calls, and the source of the float future.

Last verification batch: per-dispatch glue path, the fallback-instruction hook cost, the local-vs-exit `bl` ratio across all chunks, the FP compile flags, and where the EFB depth future is raised.

Reading the two prior fallback analyses (R489, R553) and pulling the fallback-address evidence from the live Simulator log before I write up.

I have what I need. Here is the review.

## Diagnosis

**Facts established from source and artifacts, not from the journal's summaries:**

1. **The module exits to the host dispatcher roughly every 13 guest cycles.** Every `bl` whose target lies outside its own 1024-instruction chunk is emitted as `ctx->pc = target; return;` in [emitter.c:378-395](ref/ModernGekko/vendor/dolphin/DolRecomp/src/backend/emitter.c), and the callee's `blr` only resumes inline if the return address is in the same chunk. Counted over all 331 generated chunks:

| Site type | Count | Behavior |
|---|---:|---|
| `bl` exiting to chassis | 150,499 | full host round trip |
| `bl` local goto | 14,721 | inline |
| direct cross-chunk calls | 0 | feature refused by [generate-aot.sh:5-10](scripts/generate-aot.sh) |

   The shutdown counters confirm the dynamic rate. Charged guest cycles divided by native dispatches is 13.2, 12.8, 13.0 on three macOS runs and 13.2 to 14.0 on eight Simulator sessions. At 729 MHz that is about 55 million dispatches per guest second, or roughly 900 thousand per 60 Hz frame. Each one runs the whole path in [StaticRecompCore_Run.cpp:108-190](ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp): downcount flush, timebase update, exception checks, lookup-table dispatchability, host-call hash check, then `chassis_dispatch` → `dolrecomp_call` → replacement check → second host-call check → page-indexed chunk lookup with a division → indirect call → 1024-way switch.

2. **That glue is at least a third of CPU-thread time in the current scene.** In [plaza-sample-r705.txt](generated/plaza-sample-r705.txt) lines 125 to 360, of 428 CPU-thread samples: 49 are waits, and of the remaining 379, about 140 are self time in `Run`, `chassis_dispatch`, `ModManager::Dispatch/HandlesAddress`, `IsHostCallAddress`, and state sync. The switch prologue inside each `func_*` is attributed to generated code, so the true share is higher. This is why every profile looks "flat across chunks": the cost is uniform per dispatch and per instruction, not in any routine.

3. **Per-instruction expansion is the second structural cost.** Every instruction is a `case` in the entry switch at [emitter.c:1913-1935](ref/ModernGekko/vendor/dolphin/DolRecomp/src/backend/emitter.c), PC is materialized before any faulting instruction, and every FP arithmetic op is an out-of-line call that recomputes interpreter-exact FPRF, NaN propagation, and two `force_single` per lane in [cpu_interpreter_float.c](ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu_interpreter_float.c). The compiler therefore cannot keep guest state in registers, which is exactly the signature the agent's own R470 audit found and then dismissed: 61 percent of sampled instructions are loads. R464 measured 2,753 host instructions per call on a 44-instruction FP path. R463 measured 3.8× the process instructions per VI of Dolphin's JIT on the same runner and scene; R424 measured 16.7 ms versus 6.0 ms CPU per VI.

4. **macOS is already at the budget edge, so any Simulator overhead pushes it under.** Good Egg on macOS runs at 16.7 ms CPU per VI. The plaza in the Simulator needs about 23 ms of CPU per frame plus 3 ms of EFB-peek waits, which matches the observed 37.6 Hz. The video thread is idle 53 percent of the time. This is CPU-bound, and the per-thread numbers in [cpu-gameplay-r704.csv](generated/cpu-gameplay-r704.csv) agree.

**Hypotheses, labeled as such:**

- The Simulator's 1.45 to 1.64 percent interpreter fallback steps, stable across eight sessions at 17 to 24 steps per guest exception, are most likely the OS exception-vector stubs at low memory, which the DOL copies there at boot and which the module does not cover. On macOS the JIT absorbs them uncounted. The agent has never produced the fallback PC histogram the PRD requires, so this is unverified.
- The Simulator executing fewer process instructions per VI than native while spending more CPU-thread time suggests lower IPC or clock on that thread. The QoS experiment lacked core-residency evidence, so it did not settle this.

## Top three opportunities

**1. Guarded direct cross-chunk calls. Highest impact, high confidence in the mechanism.** The pinned generator already implements it: `emit_cross_chunk_call` in [emitter.c:356-376](ref/ModernGekko/vendor/dolphin/DolRecomp/src/backend/emitter.c) with depth-bounded recursion via `dolrecomp_call_enter` in [RMGE01.h:33-43](generated/aot/c/RMGE01_generated/RMGE01.h). The agent rejected it in R422 as unsafe without ever measuring it. The bypass concerns are all guardable: chunk verification becomes one load of the chassis chunk-state byte before the call, host-call hooks become a bitmap test instead of two hash lookups, and interrupt latency is already bounded by the 256-cycle budget check the local-return path uses today.
   - Decisive experiment: macOS diagnostic runner only, one module built with the env var, same slot2 scene and 30 s method as R424. Read three numbers: native dispatches from the shutdown line, CPU ms per VI, process instructions per VI.
   - Expected distinguishing result: dispatches drop several-fold and CPU ms per VI drops by 20 percent or more. If it drops under 8 percent, the dispatcher model is wrong and this lane closes.
   - Correctness risks: the 19 SMC candidates in [SMC-ANALYSIS.md](docs/SMC-ANALYSIS.md), mod hook addresses, lockstep verifier, host stack depth beyond 24 frames falling back to the chassis. None affect the measurement run; all must be guarded before promotion.
   - Stop condition: below 8 percent on macOS, or a chunk-entry differential failure that guards cannot explain.

**2. Inline FP arithmetic with Dolphin-JIT default semantics. Large impact, medium confidence.** The helpers mirror the interpreter, but the correctness reference this game has actually run under for years is the JIT, whose defaults leave FPRF and accurate NaNs off; R425 shows enabling them costs the JIT only 0.2 ms per VI because it computes them lazily. Emitting paired-single ops inline on the `fpr`/`ps1` lanes with the same policy, keeping frC 25-bit rounding, and falling back to the exact helper when FPSCR exception enables are set removes the call and the escape on every FP instruction.
   - Decisive experiment: rebuild the one chunk the R464 harness already executes, using the existing single-chunk substitution scripts, and rerun [probe-installed-block-work.c](tests/probe-installed-block-work.c). Then one macOS A/B by instructions per VI.
   - Expected: instructions per call on that path drop from 2,753 to well under 1,000; module-wide CPU per VI drops 10 to 25 percent.
   - Risks: code reading FPRF via `mffs`/`mcrfs` after arithmetic, which the existing FPRF-site audit can enumerate, and NaN sign differences the JIT already exhibits.
   - Stop condition: under 2× reduction on the harness path, or lockstep divergences not attributable to the FPRF/NaN policy.

**3. Mobile-only chassis tax. Moderate impact, high confidence on two of three items.**
   - Per-dispatch mod address checks cost about 8 percent of CPU-thread samples in R705 even after patches 0029/0030; replace [ModManager::HandlesAddress](ref/ModernGekko/src/runtime/mod_loader.cpp:639-649) hash lookups with a one-bit-per-instruction bitmap.
   - Name the interpreter fallback PCs with a histogram like the existing dispatch-sample facility in the Run loop. If they are the exception vectors, register that area as relocated copies of the DOL templates through the REL mechanism in [StaticRecompCore_SMC.cpp](ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_SMC.cpp), which already hash-verifies runtime-relocated code.
   - Confirm CPU-thread core residency with one System Trace of the Simulator process. Either it lands on E-cores and USER_INTERACTIVE QoS is justified, or the hypothesis dies.
   - Stop: each item is a day; drop any that does not show in a matched instruction-per-VI comparison.

The synchronous EFB depth peek is real at about 9 percent of CPU-thread wall, but it is inflated by the Simulator's XPC GPU path and has no semantics-preserving large fix. Leave it.

## Accepted, disputed, and what to change

Accepted: the frame-counter caveats, the controller-dialog artifact, the native THP result, the memory-pressure exclusion, the LLVM park in R440 to R443. That IR carried the same all-entry design, so it could not win and says nothing about a better emitter.

Disputed: "not a safe shortcut" for direct calls was a judgment, not a measurement. "No broad float-helper rewrite justified" in R470 misreads the load-dominated profile, which is the state-in-memory signature. "No relaxed AOT semantics authorized" treats the interpreter as the reference when the PRD's reference behavior is Dolphin's RMG configuration, which runs the JIT with those features off. "No single hot routine" is correct and is precisely the reason routine-level tuning has produced nothing.

The iteration history shows the failure mode: pick a sub-5-percent target from a wall-stack sample, spend a multi-hour link, run an A/B with 3 percent noise, park. Change the process to: require a predicted effect of at least 15 percent of CPU ms per VI before any module build, use dispatch counts and instructions per VI as primary metrics instead of frame-event Hz, prove it on the macOS diagnostic runner first since the generated source is identical, and work one architectural lever at a time with a written stop condition.

Stop taking more wall-stack samples of the plaza, stop dispatcher lookup micro-tuning, and stop revisiting the movie path. The best next action is the opportunity 1 measurement: one macOS module with direct calls enabled, one 30 s comparison on the R424 scene, three numbers.
