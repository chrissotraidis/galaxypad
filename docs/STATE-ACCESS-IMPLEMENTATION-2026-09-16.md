# State-access pass implemented; standalone speed hypothesis rejected

> Session closed: [current build, owner assessment and research handoff](SESSION-CLOSE-2026-09-16.md).
> This document retains the evidence and acceptance limits of its dated experiment.


The maintained DolRecomp fork now contains an explicitly invoked state-access
pass, a ROM-free differential test and offline corpus/object probes. It is not
called by normal C or LLVM generation. The installed iPhone uses the C backend
and is unchanged.

## Actual transformation

The pass computes conservative state-slot liveness over forward CFG edges to
remove writes overwritten on every continuation before observation. Within a
block, it forwards known values instead of re-reading guest state. Every block
remains independently enterable. Backedges, loop-header budget exits, unknown
exits, all helpers and all memory operations expose the full state. It preserves
arithmetic, block addresses, cycle charges and terminators. Unknown helper effects
are not treated as pure; per-helper slot summaries are not implemented yet.

PHIs, cross-block SSA uses and noncanonical state accesses are refused before
transformation. This respects the current LLVM emitter's per-block SSA table.
The pass contains no game identity, addresses, native replacements or precision
shortcuts. It applies to the shared DolIR layer, but other games are untested.

## Executed evidence

- 48,000 IR-state/observer/cycle comparisons in each of optimized and ASan/UBSan
  builds: 96,000 total. Integer state and raw FP-state values, every fixture entry,
  both conditional outcomes, looping budget exits, mutating helpers/memory
  observers and callback side exits are covered. These are IR executor tests,
  not floating-point arithmetic validation or full-game correctness tests.
- All 17 non-LLVM compiler CTests passed in the initial implementation build.
  The later input-validation additions passed the focused optimized/sanitizer
  tests again. The new tests are also registered in GalaxyPad's default suite.
- The complete default `bash scripts/check-repository.sh` suite passed with the
  new tests and updated maintained-fork pins.
- Applied to 1,350,400 non-embedded decoded instructions from the private DOL:
  161,063 of 1,487,356 IR state reads forwarded; 453 of 1,065,040 state writes
  removed. These are static counts, not saved host instructions.

## Decisive machine-code result

Using LLVM 20.1.8, the existing O2 backend pipeline and an explicit experimental
macOS ARM64 target, compiled complete 1,024-instruction chunks before and after
the pass:

| Profile-selected chunk | Reads forwarded | Writes removed | Object result |
| --- | ---: | ---: | --- |
| Integer-heavy 805170A0 | 121 | 0 | Byte-identical, 862,984 bytes |
| FP-heavy 804B60A0 | 36 | 0 | Byte-identical, 2,396,064 bytes |

Both optimized LLVM IR pairs are also byte-identical. This is stronger than
matching instruction totals: the existing LLVM optimizations already remove
this redundant work in these chunks. Reject this conservative cleanup pass as
a demonstrated performance improvement. Do not spend another phone comparison
or whole-module build on it unchanged.

These probes do not use the installed C/PGO/ThinLTO pipeline and do not establish
LLVM-versus-C performance, iPhone correctness, or universal lack of opportunity.
They establish that this proposed extra DolIR cleanup adds no machine-code benefit
for two relevant chunks under the tested backend.

The maintained fork's `DOLRECOMP_LLVM_ARM64_PROBE=1` permits offline macOS ARM64
object emission only; production target defaults and iPhoneOS restrictions stay
unchanged. Unset and `0` both failed closed in executed checks. Probe mode is
included in the codegen cache fingerprint. LLVM 20 was installed because the
existing LLVM 22 is outside this backend's declared supported version range.

Private source identities, object hashes and gate results are recorded in
`generated/state-access-20260916/machine-code-result.json`; build logs, raw IR,
objects, corpus counts and tests are in the same ignored directory.

## Consequence for the architecture

The broad idea of retaining guest state is still plausible, but merely adding
read forwarding/dead-store elimination duplicates existing host-compiler work.
The next implementation must change the dataflow that the compiler cannot
currently optimize: exact FP helpers accepting mutable CPUState, and memory
observers forcing state synchronization. Audited value-based arithmetic/helper
interfaces and a safe ordinary-RAM path are materially different work. The
conservative pass and probes provide a reusable baseline for assessing that work;
they are not a faster port or completion of the larger region compiler design.

Changes reside in maintained forks and pinned gitlinks, with no new patch stack,
release, device installation or production optimization enabled.
