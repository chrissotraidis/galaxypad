# Fixed chunk-boundary census

This is a source/profile investigation, with no product changes or runtime
instrumentation. The C generator cuts text every 1,024 instructions in
`DolRecomp/src/app/pipeline.c:1006–1045`. A cut can split a straight-line sequence
and return through `StaticRecompCore::Run`, although the guest has no branch there.
CFG-aligned boundaries could avoid some transitions without increasing all chunk
sizes or introducing the rejected recursive direct-call ABI. Benefit and timing
correctness are unproven.

## Current result: no runtime probe justified for the first target

The accepted Simulator module SHA is
`90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f`.
Its UUID `CAA7A519-7F65-3D02-AC4E-AF56D7CCFCF2` matches the retained pass-3
Observatory stack sample. The census reads the source inventory and profile path
from that build's compile commands, hashes all sources, and finds 1,319 adjacent
cuts among 1,322 chunks. Of those, 977 have a non-control-flow predecessor and
are not a known direct branch target. This is a conservative syntactic screen,
not complete CFG analysis: indirect entries and additional observer boundaries
remain unknown.

The highest-ranked pair by combined self observations is
`804B50A0 → 804B60A0` (78 and 131 observations). Source chunk 1201 ends after
`lfs` at `804B609C`; chunk 1202 continues with `ps_muls0`. Both chunks were live
in historical PGO training, with 4,548,885 and 11,947,928 function entries.
Neither samples nor function entries identify executions of that particular cut.

`map-pgo-tail.py` resolves this ambiguity without launching a runtime. It emits
front-end LLVM instrumentation text for the unchanged SHA-pinned source chunk,
using its real compile command with profile-use/optimization replaced by
instrumentation and disabled LLVM passes. This is compiler analysis only: no
object, module, executable or app is linked. The function's instrumentation hash
`ddb4aec2ff46b2d8` and 2,396 counters match the existing PGO profile. The final
instruction label has counter 2339; its sole FPU-unavailable exit has counter
2340. The retained LLVM fragment verifies that the successful arm flows to the
tail return. Their counts are 14,669 and zero, yielding **14,669 tail crossings**
over the training input, about 0.32% of this source chunk's entries. Unexpected
nonlocal host exits would invalidate this subtraction; ordinary lfs callbacks
return to the shown flow. This count is not a present-scene rate or CPU cost.

This weakens the first target substantially. A second warning against treating
hot chunks as hot cuts: `805170A0` has 149 self observations and 56,930,084 PGO
entries, but its tail destination `805180A0` has zero profile entries. Do not
promote, rebuild a module or add a runtime tail probe from these rankings alone.
The remaining cuts are unqualified, not proven useless.

## Reproduce

From the repository root, using a new output path on each invocation:

```sh
python3 experiments/chunk-boundaries/census.py \
  --compile-commands generated/build/ios-simulator-pgo-use-20260912/compile_commands.json \
  --module generated/build/ios-simulator-pgo-use-20260912/gRMGE01_recomp.dylib \
  --profile generated/runtime/ipad-iteration-1/pgo-profile-route-20260912/current-input.profdata \
  --sample generated/runtime/performance-pass3-20260913/probe-on-1x/thread-stacks.txt \
  --output generated/runtime/performance-pass3-20260913/chunk-boundary-census/report.json

python3 experiments/chunk-boundaries/map-pgo-tail.py \
  --output generated/runtime/performance-pass3-20260913/chunk-boundary-census/pgo-tail
```

The census is read-only apart from its new report. The second command additionally
emits one private LLVM text file and proof fragment. Existing outputs are not
overwritten. Both commands passed on the retained inputs. Source hashes, compiler
command, profile identity and exact counter mapping are in the private receipts.
The matched profile CFG hash strengthens the one-chunk source correlation;
compile commands alone do not prove every current source equals the old binary.

## Gate before any boundary shift

First map another genuinely frequent edge from matching archived instrumentation,
then establish its rate in the actual target workload only if that evidence
justifies a small probe. A probe must count selected tail exits only, have a
recording-off control, and preserve the original return and all guest behavior.

Any proposed shifted boundary must retain every legal external entry and suffix
charge, callbacks, FP/exception state, SMC/host-call behavior and charged cycles.
Test stop/pause, exhausted budgets and timebase observers at the old cut: losing
a host return can change these even when guest instructions are unchanged. A
boundary shift is not automatically correct because other chunk sizes worked.
Only a complete-region differential and actual-policy instruction/CPU cost win
would justify a separate module comparison. Changed CFG requires matched profile
training; missing PGO is not an equivalent control. Physical device performance
and audio acceptance remain separate.
