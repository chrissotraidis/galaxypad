# R800: split-lane FP cache adapter passes transport gate

R799 made progress by qualifying hot arithmetic regions and their observation
boundaries. Current cache inspection found a concrete incompatibility: reference
PowerPCState stores adjacent PS0/PS1 doubles per register, while GalaxyPad
CPUState has separate fpr[32] and ps1[32] arrays. Changing offset macros alone
would make 128-bit loads/stores read or overwrite the neighboring PS0 register.

## Private implementation

- tests/aot-cpu-fpr-layout.h binds both lane offsets to CPUState.
- tests/adapt-arm64-fpr-cache.py verifies the exact reference source hash and
  substitutes five PS0 load/store sites plus the duplicated-value STP site.
  128-bit accesses become two separated64-bit accesses plus lane insert/extract.
  Register allocation/dataflow code is retained; vendor source is unchanged.
- Q31 is reserved for lane-IO scratch after Init. Generated-source assertions
  reject using that register as an IO operand. This reservation is mandatory
  for future users of the adapter, not part of the stock reference cache.
- Exported ordinary static assembly preserves X29/X30 and Q8–Q15 and uses a
  symbolic callback relocation. No executable-memory allocation or runtime JIT.

The probe copies raw paired values, overwrites only the lower lane of a dirty
pair, reloads its preserved upper lane, duplicates lower values, creates enough
resident guest values to cause spills, flushes before a callback, and reloads
callback-modified lower/upper values. The callback mutates every FP lane and
non-FP state. The driver compares the complete CPUState both on callback entry
and after completion, preventing later writes from hiding boundary mistakes.
Random raw64 inputs include NaN encodings; the oracle uses byte copies. Seeded
host FPSR status is also required to remain unchanged through transport.

Final run10516 exit0:100,000 callback-entry/final-state/FPSR comparisons pass;
stderr empty. Initial82394 also passed before boundary/status strengthening.
Changed reference source is rejected. ASan/UBSan instrument the C++ driver,
not emitted assembly. Reproduce: `python3 tests/probe-arm64-fpr-cache.py`.
Artifacts: generated/arm64-fpr-r800-final.json and .err.

Reference cache SHA:
ddb545c1c708066ca19e46dad4fddf788e0ebd11604e5417df402e893c0b825a

Adapted cache SHA:
3f7204bdafcba9bc821958f9aa983d7e060c136842f1d7cc9636bfa030077f3c

## Remaining gate, not a performance claim

This validates Register/LowerPair/Duplicated transport, not Single/
LowerPairSingle/DuplicatedSingle conversion or actual guest arithmetic. Private
host conversion methods still abort explicitly. Reference conversion code at
JitArm64_FloatingPoint.cpp781–922 relies on per-register store-safe facts, far
code and a runtime cstd target for exact special-value conversion. Do not replace
those methods with unconditional host FCVT or copy a live helper address.

Next implement relocatable exact conversion handling with explicit precision
facts and test lane aliasing, NaNs/subnormals, rounding/NI and flushes. Then lower
the qualified whole arithmetic region and compare complete actual-routine
behavior and ThinLTO/PGO cost. Split-lane IO introduces extra instructions and
one reserved register; sustained reuse must pay for that cost. No FPS gain,
complete FP backend, mobile execution, exhaustive ABI proof or app promotion.
No app/module/save/Simulator change. Original PRD/SunPad/gameplay/audio/stability/
physical-device requirements remain active.
