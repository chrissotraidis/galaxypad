# R823: broad weighted instruction map points to loads, not isolated arithmetic

R822 provided a usable actual plaza CPU profile. This turn joins its raw
binary-relative PCs to disassembly of the SHA/UUID-verified macOS module, without
launching or rebuilding anything. Existing classifier now supports explicit
cycle weights without substituting sample counts for missing weights; focused
alignment/zero/missing-weight tests pass.

scripts/map-plaza-instructions.py streams disassembly of all574 sampled generated
chunk symbols and retains sampled instructions plus bounded neighboring context.
It checks module SHA, preserves compiler disassembly, and requires every selected
sample to resolve. Count and cycle-weight conservation pass. Final artifacts:
generated/plaza-instructions-r823-final/{context.asm,report.json}. Initial report
in plaza-instructions-r823 is retained; final additionally includes load-base
and load-opcode grouping. These are the same capture, not repeated measurements.

CPU thread total25,462samples /22,315,669,485cycle-weight units. Selected generated
chunks17,459samples /15,556,989,061units; remaining CPU symbols are outside this
instruction-family table, not silently assigned to generated work.

| Opcode family | Samples | Cycle-weight units |
| --- | ---: | ---: |
| Loads | 8,975 | 8,026,677,275 |
| Stores | 1,697 | 1,503,820,451 |
| Integer or other | 5,731 | 5,073,794,796 |
| FP moves/conversions | 585 | 534,875,831 |
| Branches | 332 | 292,244,393 |
| Scalar FP | 138 | 124,576,179 |
| Calls | 1 | 1,000,136 |

Loads have about51.6% of selected chunk weights. This is sampled-PC attribution,
not measured load latency, instruction execution frequency, cache-miss rate or
removable CPU work. Sampling skid applies. Out-of-line callees are excluded;
the low call/scalar-FP counts cannot prove those operations cost nothing. SIMD
instructions not recognized by the simple classifier may be in integer-or-other.

Mechanical load-base grouping gives x0:3,632,443,835units; x19:2,356,157,479;
x8:901,871,835; x9:488,401,595; sp:433,612,551. Remaining bases are retained in
the report. The register name alone is NOT proof of CPUState/guest-memory origin.
Top individual sites are dispersed; examples include compact dispatch-table ldrh
and loads at offsets0xd98/0xda0/0xda8/0xd88, plus stack restore ldp. Do not assign
all these categories to one tiny function or claim a host-register cache is safe.

## Next implementation prerequisite

Use retained neighboring instructions plus exact containing-function disassembly
to establish load origin and callback/mutation boundaries for repeated x0/x19
patterns. Resolve CPUState field offsets from the actual ABI and prove register
origin, rather than assuming it. Aggregate only recognized patterns, retaining
unknowns. Then choose a broad lowering/data-lifetime change with a falsifiable
correctness/cost gate. Existing mapping-cache, dead-FPRF, blanket-inline, direct-
call and cross-product failures remain binding evidence; another tiny predicate
variant is not justified by this map. All original PRD/SunPad/audio/stability/
gameplay/device gates remain active. No app/module/save change or speedup claim.
