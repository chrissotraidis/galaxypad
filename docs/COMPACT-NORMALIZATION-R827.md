# R827: compact state works in isolation; whole-chunk flags gate fails

Previous turn: progress, real normalization-region oracle passed but full
CPUState scratch remained large. This turn implements a distinct compact ABI,
not another annotation on CPUState.

`scripts/compact_fp_state.py` extracts the source-pinned dependency closure for
the six normalization helper entry points:25 functions. It changes only state
type and symbol names, with exact reversible body checks. The closure accesses
only fpr/ps1/fpscr and permits no memory or CPU callback. CompactFPState has seven
lanes per bank and FPSCR (120 bytes including padding). This is a private,
source-pinned transform, not a general C parser or production recompiler pass.

`tests/test-compact-fp-state.py` passes closure/field/changed-source guards.
`tests/probe-normalization-state.py --compact` and `--compact --optimized` each
pass294,912 complete CPUState/raw-FPSR comparisons, including73,728 unavailable
cases and all9suffixes/internal-external entries. Generated helper bodies and
manifests are in generated/normalization-compact-r827-checked and
generated/normalization-compact-r827-optimized. Initial closure guard omitted
the C return keyword; fixed before compilation, not a guest-code change.

Optimized `_local_state` allocates0xc0 bytes on its work path, versus the prior
0xdd0+0x50 frame. This removes the large full-CPUState scratch; it does NOT prove
all values stay in registers or establish a speed gain. Stack loads remain.

## Real-policy containing-routine gate: FAILED, no timing

Extended existing `tests/probe-transform-inline.py --normalization-compact` to
build independent full chunk1202 control/candidate dylibs with cached production
O2/strict-FP/ThinLTO/PGO flags and actual CPU helper objects. The driver executes
the complete17-instruction normalization routine804B6BCC–804B6C0C, including
loads, stores and return. Candidate inserts only an FP-enabled entry path at
6BE0; other entries and surrounding memory/exception code remain original.

The first integration run aborts on host FP flag comparison before benchmarking.
A diagnostic rerun and retained rerun both reproduce:

```
pattern=3 rn=0 ni=0 entry=3 (guest entry804B6BD8)
host flags expected=0x15 actual=0x1
full CPUState memcmp=0
FPSCR=a3211710/a3211710
PC=81234564/81234564
```

Complete state equality does not waive the failed host-flag gate. No assertion
was removed, no comparison masked, no timing result obtained. Memory comparison
occurs after that gate, so this failed case does NOT yet prove memory equality.
The isolated oracle uses FENV_ACCESS ON, while this whole-chunk compile follows
the existing production policy; this is an investigation lead, not a proven
cause. Do not add a flag mask or silently change either reference policy.

Retained source, helper objects, both dylibs and executable:
`generated/normalization-compact-whole-r827-czpxyahy`.
Final log: `generated/normalization-compact-retained-r827.log`.
Earlier logs: normalization-compact-cost-r827.log and
normalization-compact-failure-r827.log. Initial ephemeral build directories were
removed by the existing harness; the compact mode now explicitly retains its
builds for investigation. No rerun of the game is needed to reproduce this case.

PGO boundaries: cpu_interpreter_integer has no profile; control51functions and
candidate55functions each report one mismatched function. The common nested-
comment warning remains. These warnings are not hidden or called full PGO parity.

## Next

Use the retained whole-chunk failing case to identify which operations generate
the differing host flags and whether local-state dead-code elimination or FP
environment policy is responsible. Preserve full guest state, raw flags and
memory observations. Only after the real-policy correctness gate passes may the
prepared containing-routine ABBA cost screen run; only a material repeatable
gain justifies integration or gameplay A/B. Compact code alone is not acceptance.

No normal app/module/save change, game-speed claim or product promotion. All
process handles are terminal; no game or Simulator launched. Full original
PRD/SunPad/audio/stability/gameplay/device goal remains active.
