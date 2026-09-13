# Code and upstream integration review — September 14, 2026

Reviewed public main `0f79ff5` and the subsequent local repair branch. The review
covered dependency reconstruction, release packaging, Apple input/import/reporting,
native hooks, tests, and Preview 1 source/binary evidence. Findings below distinguish
confirmed defects from design debt and unverified runtime concerns.

## Confirmed defects repaired

All findings below are normal-priority (P2); no new shipped critical defect was
established in this pass.

| Finding and trigger | Repair | Evidence |
| --- | --- | --- |
| Bootstrap accepted an unrelated compiler definition appended to a file already touched by a reviewed patch. A path whitelist could not verify its contents. | Reconstruct the expected patched source in a temporary Git index and compare the checkout. | Original bootstrap accepted the mutation; repaired bootstrap rejects it. Clean, repeated, and Simulator-overlay replays pass. |
| Bootstrap treated an existing checkout with a `.git` file as a missing clone. | Accept the Git metadata file used by submodules and worktrees. | Real temporary worktree regression passes. |
| Packager accepted an unrelated ARM64 dylib under the AOT module filename and produced a successful archive. | Require the StaticRecomp loader export before signing the copy. | Original script packaged a synthetic unrelated library. Repaired script rejects it; a synthetic interface fixture still signs/packages. No library is loaded during inspection. |
| Packaging could write its output inside the input app, overwrite an existing manifest, or overwrite another job's output created after preflight. | Reject output paths inside inputs; require new archive and sidecar; create final outputs exclusively. | Input preservation, existing sidecar, and competing-output regressions pass. |
| Exported diagnostics retained raw controller snapshots and touch samples despite the report UI promising their omission. | Remove the actual producer formats, preserving CPU/memory/thermal summaries; distinguish local logs from exported reports. | Controller and asynchronous touch-log regressions failed before the repairs and pass under ASan/UBSan afterward. |
| A private THP candidate manually emulated `stwu`, then advanced the stack pointer and PC even if the write faulted. | Execute that fallback instruction through the chassis interpreter, retaining its exception/register result. | Original implementation fails the regression; fault, ordinary fallback, accepted decode and charge-ownership cases pass under ASan/UBSan. This candidate remains off by default. |
| About described a public preview as private and unapproved, with no clickable upstream credits. | Show experimental status and separate linked upstream contributions. | Updated About and the existing controls/editor harness pass on an isolated iPhone 14 / iOS 26.5 Simulator. |
| The normal contributor check stopped on absent ignored, game-derived experiment files. | Separate 18 explicit private-evidence commands from the source/prepared-dependency suite. | Default suite completes without game data. Private mode fails clearly when fixtures are unavailable. |

Implementations: [bootstrap](../scripts/bootstrap-dependencies.sh),
[source verifier](../scripts/verify-dependency-tree.py),
[packager](../scripts/package-preview.py),
[report filtering](../apple/shared/GalaxyPadDiagnostics.mm),
[THP fallback](../apple/shared/GalaxyPadTHPPatch.c), and
[About](../apple/ios/GalaxyPadAboutViewController.mm).

The source verifier covers tracked files and nonignored additions against the
pinned base and patches. Git-ignored generated/build inputs are outside that
comparison. It does not establish complete build-input or binary reproducibility.
The packager's export check establishes a loader interface, not a valid game
descriptor or gameplay correctness; the runtime retains its descriptor checks.

## Simplification and validation

Removed six unused `GalaxyPadMenu`, `GalaxyPadStickView`, and
`GalaxyPadTouchOverlay` files: 534 lines of obsolete UI. Repository-wide searches
found no active CMake/script/test references. Production controls remain in
`GalaxyPadGameOverlay`; no button rewiring was needed.

The default `bash scripts/check-repository.sh` completed successfully with 146
explicit test commands, plus source-content, syntax and configuration checks.
Tests include actual compiled code and sanitizer cases as well as source checks;
the count is not a claim about independent behavioral coverage.

The new packager also successfully repackaged the actual Preview 1 Mac app in
isolated temporary storage, with its input files unchanged. This was a local
packaging check, not a new published artifact or game execution.

The dependency replay used isolated clones of the actual pinned Git objects.
External third-party submodule initialization was stubbed for that replay, so it
is not a fresh full runtime build. The UIKit harness used a new isolated Simulator,
which was removed afterward. No game installation, save mutation, new game build,
physical gameplay test, public release or upstream submission was performed.

Private game-derived checks remain explicit:

```sh
bash scripts/check-repository.sh --with-private-evidence
```

They require the recorded local fixtures and do not silently skip missing inputs.

## ARM64 JIT allegation

A relevant candidate is [RecompCore PR #6](https://github.com/ExpansionPak/RecompCore/pull/6),
which repairs returning from ARM64 fallback JIT execution to covered AOT code.
The locked base `13e492094902644b0d113c586300d358640f9e19` already descends from
its merge `202704caa71574c9a89a65c7e4f0d35cbb7e1399`:

```sh
git -C ref/ModernGekko/vendor/dolphin merge-base --is-ancestor \
  202704caa71574c9a89a65c7e4f0d35cbb7e1399 \
  13e492094902644b0d113c586300d358640f9e19
```

The [Preview 1 release](https://github.com/chrissotraidis/galaxypad/releases/tag/v0.1.0-preview.1)
source archive matches the published SHA-256
`5996996e4e62491cb0c2cdc18b5c67afab3e693e7df75467a787569eb081c3f1`.
Its Mac source includes the fallback linking guard, yield check and PC store.

The actual released Mac archive also matches its published SHA-256,
`488a9c6cc9e5b00a38956f33d015e47d1b9dc7a8b60e5be4fdb8c03a43e247e9`.
Its `GalaxyPadRunner` SHA-256 is
`9667a03be86f8ee28502e63bbb1e158085c8ad18c17d0b438f9d725be8ee59b5`.
Symbol/disassembly inspection finds the fallback guard in
`JitArm64::SetBlockLinkingEnabled`; `GenerateAsm` calls the enable check, emits
the call targeting `StaticRecompShouldYieldAt` at `0x100234384`, then emits the
PC store before the conditional exit (`0x100271b98` through `0x100271be8`).
This is stronger than source-only evidence that the repair was compiled in.
It is not proof that every runtime configuration or game path is correct.

There is no basis to backport PR #6 again. The original reporter's exact issue or
commit is still needed to establish whether they meant a different JIT bug.
iOS excludes this ARM64 fallback creation path; complete historical iOS build
provenance remains a separate gap below.

## Remaining engineering work, in order

1. **Simplify the dependency graph with pinned forks.** There are 60 patch files
   across the three main directories, not all active, plus experiments. Preserve
   the verified applied source while committing necessary DolRecomp changes,
   then RecompCore with its child pin, then ModernGekko with its child pin.
   Only after those comparisons and builds pass should the root switch to the
   pinned fork/submodule graph and remove patch recovery. Template/Petari need
   no fork merely because they are references. This migration is not implemented.
2. **Build the next release from a complete frozen source tree.** The current
   supplement explicitly lacks a full historical iOS snapshot for every compiled
   source. Frozen audio inputs do not close that gap. Capture all source,
   generated build inputs, toolchain/configuration and artifact identities before
   promotion, then validate an in-place update with saves preserved.
3. **Expose retained import storage.** `GalaxyPadImportActivation.h` preserves
   previous multi-GB imports in recovery directories; removal intentionally keeps
   recovery copies. Repeated imports can consume storage without an in-app way to
   inspect and remove those copies. Add explicit recovery/storage management with
   save isolation and confirmation; automatic deletion is not the repair.
4. **Validate audio and private optimizations on hardware.** The Apple audio
   reserve/resampling policy is a deliberate tradeoff needing matched listening
   and gameplay evidence. The THP candidate still needs wider state/timing parity
   before any default activation. Neither should be retuned based on speculation.

## What the project actually changes

The code is more than a renamed launcher: it has Galaxy-specific touch/controller
integration, pointer ownership and reacquisition work, a guarded exact-DOL virtual
Wiimote idle-disconnection policy, Apple audio adaptations, and AOT timing work.
The input and import code reviewed also contains meaningful release/ownership,
finite-value, atomic activation and save-preservation safeguards.

The review supports concrete correctness and maintainability criticism. It does
not support a blanket conclusion that every subsystem is badly written or that
new game content is required to justify the integration. Upstream attribution
and [AI/artwork provenance](../CREDITS.md) are explicit; accepted changes remain
the project maintainer's responsibility.
