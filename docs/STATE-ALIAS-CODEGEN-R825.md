# R825: CPUState restrict annotation does not change three whole chunks

Previous turn: progress, corrected and tested exact load attribution. This turn
tests the next compiler hypothesis instead of collecting another unchanged
profile. No game or Simulator launched.

`scripts/probe-state-alias-codegen.py` copies three source-matched generated
chunks and changes only the CPUState parameter of generated chunk/loop
definitions to `__restrict`. It retains the cached O2, strict-FP, ThinLTO and
original PGO compilation flags, then links each whole object privately with
unresolved imports and an explicitly retained chunk root. This is a hypothetical
stronger contract, NOT an authorized shipping assumption. No diagnostic dylib is
executed or packaged. CPUState-as-RAM and externally aliased callback access are
not covered by this hypothetical contract.

Final artifacts: `generated/state-alias-codegen-r825-final`, including source,
build logs, objects, DO-NOT-RUN dylibs, assembly, hashes and report.json.

| Generated chunk | Instructions, both | Loads, both | Stores, both |
| --- | ---: | ---: | ---: |
| 804520A0 | 41,165 | 8,544 | 2,888 |
| 804AB0A0 | 31,934 | 7,066 | 2,788 |
| 804B60A0 | 45,109 | 8,158 | 2,825 |

`tests/test-state-alias-probe.py` verifies annotation-only source differences,
source/binary hashes, retained root presence, matching logs and exact equality
of all disassembled instruction encodings in each pair. Pass. This is stronger
than equal opcode totals but does not prove runtime semantic equivalence.

Initial harness errors were resolved without touching product code: copied
chunks needed their parent header; ThinLTO removed unreferenced hidden roots;
different absolute install-name lengths shifted the linked code. The final
harness uses the real header symlink, explicit root retention and identical
install names. Earlier outputs are retained, not counted as valid experiments.
Both 804520A0 builds warn that one of 33 functions has mismatched PGO data; the
other two pairs have no warnings. Do not claim universal complete PGO coverage
or full-module link equivalence. These are isolated whole-chunk links.

## Decision

Close the simple CPUState restrict-annotation design: no generated instruction
reduction in these three chunks, so no game rebuild or timing run is justified.
This is not proof that alias analysis never matters, or that state caching is
already optimal. In particular, nested memory helpers and mutable callback
observers remain in the generated dataflow.

Next inspect a representative whole region for explicit state retention across
instructions, with a named observation boundary and conservative slow path.
Require a materially different dataflow from the already rejected mapping cache,
not another alias/inline attribute. If the optimized region already retains the
state, reject the design before writing a benchmark. A viable candidate needs
full-state/memory/callback/interior-entry/exception/cycle comparison, actual-policy
cost evidence and then matched gameplay A/B. Static counts are not runtime
frequency, latency or FPS. Full PRD/SunPad/audio/stability/gameplay/device goals
remain open; no app/module/save change or speed improvement is claimed.
