# R814: separate thread costs and source-correlated host-loop map

Read the exact R813 sample and checked the unchanged R791 host disassembly.
No runtime, build or product policy changed. Previous turn was progress: the
cross-product experiment failed its end-to-end gate and produced a fresh sample.

## What the sample supports

CPU thread8350029 has6004 observations. Run's dispatch-call branch has4748
inclusive observations;4070 lie beneath chassis_dispatch+152. Run itself has
698 leaf observations (11.63% of this thread's sampled observations). This is
not a cycle-weighted profile and cannot prove time saved by removing that code.
The largest generated chunk beneath that branch has138 observations, not a
dominant whole-game routine. The cross-product region is only part of that chunk.

Video thread8350086 has6001 observations. Its top-level condition-variable
wait branch has3374 (56.22%). VertexLoader::RunVertices has637 child observations
plus193 self at this level (830,13.83%). Depth peek has219 observations beneath
Metal staging Flush/waitUntilCompleted. CPU dispatch's float-future wait has220
observations; the matching counts suggest a readback dependency worth recognizing,
but are not proof of exact paired events. These counts must not be combined with
CPU-thread totals or used to claim GPU hardware saturation. Most video samples
are waiting, so a vertex-only rewrite is not justified as the primary fix.

## Exact source correlation

Host image load base100af0000, unslid base100000000. atos resolves symbols but
not source lines; disassembly provides the checked mapping instead:

- Sample Run+2516 maps to unslid100286a8c, immediately after the indirect module
  dispatch call at100286a88. Its inclusive count is callee work, not host-loop self.
- Run+2396 maps to100286a14, loading the dispatch-sampling enable flag. Do not
  attribute all698 aggregated self observations to this one address.
- Run+2716 maps to100286b54, loading the idle-loop PC after exact timebase update.
-100286abc..100286b4c implements downcount flush, charged-cycle counters and
  divide-by12 timebase/remainder update. Division is already lowered to umulh
  and shifts, not an expensive library divide.
-100286bd8..100286bec performs the host-call check before continuing a burst.

Source: ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/
StaticRecompCore_Run.cpp, especially185..274. StaticRecompCore.cpp116..125 checks
host callbacks, including physical-address aliasing. mod_loader.cpp639..648
already bounds static hook lookup, but always checks dynamic pending returns.
Do not bypass that dynamic behavior or reintroduce an unsafe stale address cache.
VertexLoader.cpp256..275 is a per-vertex pipeline-function loop with mutable
stage indices; whole-draw specialization would require actual format frequency
and full output equivalence, not a blind replacement of the indirect calls.

## Next implementation question

The bounded next candidate is a production fast path for the shared native Run
loop when optional diagnostics/direct-boundary/lockstep features are disabled,
with a retained general path and all guest cycle/interrupt/SMC/hook semantics.
First inspect which flags can change during a dispatch callback; only proven
stable configuration can be specialized. Measure the entire loop under actual
host flags and representative callback/exit patterns, not one flag or arithmetic
instruction. Require state/exit/cycle equivalence and a material full-loop cost
gain before another host rebuild. The698 self observations are a ceiling on
this lane's sampled opportunity, not a predicted FPS gain. Existing failed
cross-chunk/direct-call experiments remain closed; this is not permission to
repeat them. If the flags are not stable or loop savings are negligible, stop
this candidate and return to wider native code generation.

All original PRD/SunPad/gameplay/audio/stability/device requirements remain.
