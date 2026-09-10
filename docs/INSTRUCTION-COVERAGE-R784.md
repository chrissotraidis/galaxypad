# R784: instruction-level retained profile corrects target selection

Previous turn: progress, shared RAM-load range prerequisite passed; dynamic
coverage remained missing. No live game or full module build this turn.

tests/probe-chunk-coverage.py builds a temporary coverage-mapping object for
the exact current chunk under its actual Ninja defines/includes/compiler flags,
substituting instrumentation/coverage generation for PGO use and ThinLTO. It
does not execute that object. llvm-cov export applies retained frontend profile
data. Function count65272501 matches llvm-profdata show for func_804B60A0.
Only the expected freshly-built-object timestamp warning is allowed and
recorded; other diagnostics fail the probe. No counter mismatch reported.

Source SHA38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac;
profile SHAf39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d.
Final91102exit0: generated/chunk-coverage-r784e.json. Initial14399 rejected
expected timestamp diagnostic;25950 produced selected-location counts. An
all-label extension correctly encountered a gap; final output marks one
unmapped label null rather than claiming zero, with1023 labels mapped.
Use LLVM's resolved source segments at instruction start, not enclosing raw
regions (which overlap extensively in generated goto-heavy code).

Retained training results:

- Four R783 lwz sites804B66A0/A4/A8/AC:0 each. Do not benchmark/promote that
  specific span as a hot target based on the containing chunk's call count.
- R768–R780 transform804B6278:9787 executions. Its synthetic cost was real for
  that fixture, but it was not demonstrated representative of chunk CPU work.
-804B6BCC:22608894; subsequent804B6BD0 onward22608668 across the hot sequence.
  Source is a vector-normalization sequence: paired input loads, squared sum,
  reciprocal-square-root estimate/refinement and scaled output. This is the
  better-qualified region for further source/assembly analysis in this chunk.

These are retained training execution counts, not fresh Simulator phase counts,
CPU time shares or proof of gameplay speedup. Do not generalize a single chunk
to whole game or ignore scene differences. No new profiling run is needed just
to repair this known target-selection error. Before changing the hot sequence,
check previous normalization/FP experiments and require a distinct substantive
lowering mechanism under exact load/callback/rounding/exception contracts.
Full original PRD and all unproven runtime/device/product gates remain open.
