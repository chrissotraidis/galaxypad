# R904 — static resident merge region, actual routine entry contract

The iPad gameplay bottleneck remains open. Last measured heavy plaza was
37.15 VI/s (23.42 ms CPU/VI); movie playback reached 59.88 VI/s in R897.
Nothing in this experiment changes either measurement or the installed app.

## Change

`scripts/stage_resident_merges.py` reads the hash-pinned local DOL and emits
four static ARM64 suffix functions for the actual paired merges at
804B651C–804B6528. The original chunk and switch retain all entry-cycle charges.
Each replacement entry sets PC and checks FP availability before calling its
suffix. The emitter materializes executed PCs, retains merge operands in its
FPR cache, flushes state before returning, and rejoins original code at 652C.
Arithmetic, stores, callbacks, and return afterward remain original code.
No runtime executable-memory allocation or normal builder integration exists.

The complete original chunk and candidate are compiled as independent libraries
using the recorded module flags. Only the candidate links the assembly object.
The probe retains all 41 entry points of the selected 804B64A4–6544 routine;
this is not coverage of every entry in the surrounding chunk.

## Evidence

Initial run `generated/resident-merges-whole-r904/result.log`: 629760 complete
CPUState/memory/callback/FPSR comparisons pass, including 172800 callback cases.
The matrix covers lazy availability both ways, enabled/disabled FP, guest RN/NI,
GQR modes/scales, overlapping buffers, external callbacks, journal mutation,
boundary accesses, and CPUState-backed RAM. Original unavailable-entry SRR0
and no-callback cycle charges have independent assertions.

The final rerun `generated/resident-merges-final-r904` exited0 with the same
629760 comparisons and172800 callback cases; its report records
commands, source/object/assembly/library hashes, raw DOL words, and exit status.
Exporter rejection checks cover unsupported opcode, blank input, misaligned
entry, and oversized address. Compiler reports existing helper profile mismatch
and unprofiled integer/whole source warnings: no exact PGO-equivalence claim.

The legacy `fast-path accepted calls: 0` line is the unused memory-candidate
counter, not an indication this assembly candidate was skipped.

## Decision and next gate

Correctness integration only. Do not benchmark this four-instruction fragment
as a performance solution: ABI transitions dominate tiny regions. Extend the
same resident execution mechanism across a substantial arithmetic region,
retaining strict result/status semantics and observer boundaries. Then run the
complete-routine cost gate; only a repeatable gain justifies a module build and
same-scene iPad comparison. Do not reopen rejected guard/memory micro-tuning.

No runtime, Simulator, app installation, module selection, disc or save changed.
Full PRD gameplay/audio/device/UI/package acceptance remains required.
