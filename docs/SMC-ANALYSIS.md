# RMGE01 self-modifying-code analysis

Status: **static candidates interpreted; dynamic verification pending**

DolRecomp emits 19 candidate ranges for the exact RMGE01 DOL. They are program
counter ranges containing possible patching instructions, not proven destination
ranges and not proof that the game rewrites itself at runtime. GalaxyPad preserves
all 19 in the module descriptor and preserves ModernGekko's chunk-hash demotion
guard. No range is globally ignored.

## What the detector means

The pinned detector flags every `icbi` instruction. It also linearly propagates
known register constants through each complete text section and flags a store when
the calculated address overlaps a DOL code section. It does not construct a
control-flow graph and does not reset state at branches or function boundaries.
Consequently, a flagged ordinary store can be a conservative false positive caused
by a stale propagated constant. Runtime chunk hashes, invalidation telemetry, and
interpreter demotion remain authoritative.

## Candidate interpretation

- `0x80004320`, `0x800046C8`, `0x804A3020`, and `0x80529968` are actual `icbi`
  instructions. The first is the startup `__flush_cache` routine; the others are
  SDK/debug/cache paths. They execute through the named cache-operation fallback,
  which feeds ModernGekko's exact icache invalidation and chunk re-verification path.
- The other 15 reported ranges contain ordinary `stw` operations or bounded `stw`
  loops with an indirect destination. Static inspection does not establish that any
  destination is executable at runtime. They remain candidates until trace evidence
  records their effective addresses.
- The HOME-menu RSO is a separate confirmed dynamic-code path. Its handling is the
  narrow native replacement in `HOME-MENU-ADAPTER.md`, not an SMC exemption.

## Coverage and fallback interpretation

The exact generation has 331 chunks and zero unknown instructions. There are 419
explicit fallback call sites covering 102 named mnemonics. The reproducible audit
writes every `PC: mnemonic operands` row to the ignored
`generated/aot/rmge01-fallbacks.txt`; the build fails if any fallback call lacks a
matching name. These are modeled interpreter/cache/SPR compatibility sites, not
unidentified decoder failures. Runtime hit counts are still required to distinguish
boot-only, cold, and hot paths.

## Dynamic acceptance still required

- Record the effective address and hit count for every candidate store and `icbi`.
- Record chunk re-verifications and every hash mismatch/demotion.
- Demonstrate that no unexplained candidate is hot and no modified chunk silently
  returns to native execution.
- Run with fallback telemetry and name every actually hit PC before mobile closure.
