# R765: deferred timebase arithmetic and observer audit

## Why screened

R764 establishes native-burst dominance, not specifically timebase dominance.
Current Run updates timebase quotient/remainder after each native dispatch.
The exact R762 assembly contains the constant-division, remainder and stores.
Deferred materialization could remove repeated work only if all observers are
covered. No product change or module build is justified by those facts alone.

## Actual source boundaries

- The current Simulator module uses GXRuntime/src/core/cpu.c, NOT DolRecomp's
  similarly named cpu.c. Its build uses ThinLTO and the existing PGO profile.
- GXRuntime ppc_mftb directly reads CPUState.timebase. The selected generated C
  has six calls in two chunks:804AC0A0 (CIA804AC368/36C/370/380) and8052B0A0
  (CIA8052B4DC/4E0). These are static sites, not dynamic frequencies. They do not
  establish a safe complete observer whitelist for arbitrary modules/callbacks.
- GXRuntime cpu_interpreter_integer.c ppc_mfspr reads268/269 directly; ppc_mtspr
  writes284/285 before calling the external SPR-write path. These cannot bypass
  pending materialization. Generated fallback and callbacks need separate proof.
- StaticRecompCore::SyncIn overwrites cached TB and remainder from CoreTiming;
  SyncOut flushes mid-dispatch cycle charges but does not transfer cached TB.
  Lockstep Prepare copies the complete CPUState and Check pins entry_state TB.
  Run's dispatch trace reads TB. All are observer/reset boundaries to preserve.
- Do not substitute GetFakeTimeBase blindly: GetTicks uses DowncountToCycles
  and CoreTiming state, whereas current intra-burst TB uses exact charged-cycle
  increments. Overclock conversion, mid-dispatch hooks, and TB writes require
  explicit equivalence. LLVM IR also directly reads the TB state slot.
- Any eventual core-only chunk whitelist needs exact-module identity and proof
  of all indirect helper/callback paths. No address-only shortcut is enabled.

## Isolated implementation and tests

apple/experiments/deferred-timebase/accounting.h accumulates pending cycles and
materializes on reads/writes/snapshots. Overflow handling preserves the original
uint64 addition-wrap behavior even for extreme charges, rather than assuming
arbitrarily large additions are mathematically unbounded. No CPUState integration.

ASan/UBSan tests pass62,208 boundary triples across starting TB/remainders and
one million mixed charge/read/high-write/low-write/reset events. This proves
arithmetic at explicit observers, NOT coverage of actual runtime observers.

## Cost screen and decision

Optimized host-only ABBA benchmark, generated/deferred-timebase-r765.txt:
at one read per8 charges, eager2.73–2.77ns versus deferred0.87–0.88ns;
one per64: eager2.70–2.73ns versus deferred0.91ns. At every charge the advantage
does not repeat. Checksums match. This excludes module operations, CPUState
aliasing, callbacks, instruction-cache/memory effects and guard costs.

The isolated saving is roughly1.8ns/charge; no material whole-game8%benefit case
has been established. Keep the tested building block, but do not build an
observer-guard/ABI/module change for this standalone tweak without stronger
evidence. Next prioritize broader native state materialization/shared execution
work, rather than polishing this arithmetic or reopening vector/direct-call
variants. The full original PRD remains unchanged and unfinished.
