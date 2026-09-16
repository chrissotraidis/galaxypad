# Optional tail-call dispatch experiment

> Session closed: [current build, owner assessment and research handoff](SESSION-CLOSE-2026-09-16.md).
> This document retains the evidence and acceptance limits of its dated experiment.


This pass implements a runtime/module change, rather than another structural
candidate census. It does not yet establish an iPhone gameplay speedup.

## Rejected first candidate: machine outlining

[LLVM's machine outliner](https://llvm.org/doxygen/MachineOutliner_8cpp.html)
can factor repeated machine instructions into shared routines. The actual hot
805170A0 chunk, compiled with retained iPhoneOS PGO inputs and O2, has 93,896
bytes of executable text by default versus 62,860 with aggressive outlining.
Object file size grows because other sections, including unwind records, grow.
This was an isolated native-object probe, not the final ThinLTO module.

However, six actual save/restore entry paths from the complete chunk took
2.53–4.56 times as long with outlining in alternating Mac ARM64 tests. All
32,768 whole-chunk entry/state/memory/callback comparisons agreed, including
host FP exception flags. Correctness therefore was not the rejection reason.
These warm component tests do not model whole-game instruction-cache behavior,
but the severe added call cost does not justify installing this candidate.
Normal optimization and outlining settings remain unchanged.

Private reproduction scripts, assembly, logs and input commands are retained in
`generated/machine-outline-20260916/`.

## Implemented second candidate

`StaticRecompCore::Run` does not use the integer returned by module dispatch.
The integer dispatcher must nevertheless regain control after the generated
chunk returns to produce its success result. The optional
`staticrecomp_dispatch_void_v1` entry preserves dispatch behavior without that
result, allowing the chunk to return directly to the runtime's caller.

Both module and runtime must be compiled with `GALAXYPAD_VOID_DISPATCH=1`.
The original descriptor ABI, CPUState layout and integer dispatch entry are
unchanged. The runtime resolves the optional symbol once per Run invocation,
after normal module validation. Older modules and attached descriptors use
the existing integer entry. There is no code generation, JIT, function-boundary
assumption, guest-PC specialization, or skipped cycle/exception check.

The new module entry preserves replacement-before-host-hook ordering, PC
materialization before hooks and chunks, mutable-hook effects, and physical
address alias retries. Both hits and misses retain the original guest-state
behavior. Only the unused host return value is removed. The symbol's lifetime
is the already-loaded module's Run lifetime; it is not retained across unload.

The maintained RecompCore change is `59736d1c0591646237c72b7eb7d690fce57aedcd`;
ModernGekko consumes it at `5d982fbe5e8cfe29f375f2fac9fc3066fea1a5ca`.
No bootstrap patch stack or default enablement was added.

## Executed evidence

- 21,504 full CPUState/event-order comparisons in each of four configurations:
  O2 and ASan/UBSan, with and without replacements, totaling 86,016. Cases cover
  misses, unaligned addresses, aliases, mutable hooks, callback replacement,
  exception-field mutation and changing RAM sizes. The fixture uses the actual
  emitted integer call semantics and the actual new module entry.
- A synthetic dispatcher with the real generated lookup tables and stub chunk
  bodies takes 0.27462 seconds versus 0.18135 seconds per 50 million calls
  (medians of nine runs), about 34% less thread CPU time on this Mac. With a
  false-returning, state-mutating host hook, medians are 0.33499 versus 0.19582
  seconds, about 42% less. Exported noinline wrappers retain the integer ABI in
  the control. These are dispatch-only results, not game frame-rate estimates.
- The complete iPhoneOS PGO/ThinLTO module linked using the retained input objects,
  replacing only module_export. Input stamps were unchanged and new input hashes
  were recorded. The retained module's executable-text hash also matches the
  module used by build 7161 before this change.
- Linked iPhone ARM64 code contains a tail branch into the selected chunk. Its
  void entry uses a 48-byte frame, versus the retained integer entry's 64-byte
  frame. Assembly is in `generated/void-dispatch-20260916/linked-void.s`.

The existing profile attributes only part of the game thread to dispatch. A
34–42% dispatch-only reduction cannot be presented as that much overall FPS
improvement, and does not by itself promise 60 FPS on slower iPhones.

## Device candidate

Build 7162 keeps the 7161 host objects, audio and indexed-vertex candidate. One
archive member, StaticRecompCore_Run.cpp.o, is replaced, and the separately linked
module supplies the optional entry. The core header is identical to the baseline
header; no class-layout change is involved. The app and replacement module are
signed with the baseline identity and the app passes deep strict signature and
iPhoneOS platform verification. Private build/signing receipts remain in
`generated/void-dispatch-20260916/`.

The full default repository suite passed. Build 7162 was installed in place on
the attached iPhone 14 and its installed version was read back. All 54 backed-up
Wii save/configuration/preference files were byte-identical immediately after
installation and before launch. The live log reports `void-dispatch=1`, and
QuickTime verified startup and the title screen at 60 FPS. The game remains
running. The demanding hub was not exercised, so its FPS improvement remains
unverified. The redacted startup log still reports one runtime error, also seen
in the retained 7161 startup; its underlying cause was not identified here.
This is binding/startup proof, not comprehensive gameplay or audio acceptance.

Install, preservation and observation receipts are retained privately alongside
the build receipts. No release was published.
