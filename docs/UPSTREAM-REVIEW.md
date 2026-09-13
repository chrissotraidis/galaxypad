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
| A queued import/extraction progress block referenced a C++ worker capture after that worker was released. Hosted ASan exposed an intermittent use-after-free. | Copy the progress callback into an independently owned local block before enqueueing it. | A serial-worker/delayed-main-queue regression deterministically reproduces the original ASan failure; repeated sanitized runs pass after repair. |
| Packager accepted an unrelated ARM64 dylib under the AOT module filename and produced a successful archive. | Require the StaticRecomp loader export before signing the copy. | Original script packaged a synthetic unrelated library. Repaired script rejects it; a synthetic interface fixture still signs/packages. No library is loaded during inspection. |
| Packaging could write its output inside the input app, overwrite an existing manifest, or overwrite another job's output created after preflight. | Reject output paths inside inputs; require new archive and sidecar; create final outputs exclusively. | Input preservation, existing sidecar, and competing-output regressions pass. |
| Exported diagnostics retained raw controller snapshots and touch samples despite the report UI promising their omission. | Remove the actual producer formats, preserving CPU/memory/thermal summaries; distinguish local logs from exported reports. | Controller and asynchronous touch-log regressions failed before the repairs and pass under ASan/UBSan afterward. |
| A private THP candidate manually emulated `stwu`, then advanced the stack pointer and PC even if the write faulted. | Execute that fallback instruction through the chassis interpreter, retaining its exception/register result. | Original implementation fails the regression; fault, ordinary fallback, accepted decode and charge-ownership cases pass under ASan/UBSan. This candidate remains off by default. |
| About described a public preview as private and unapproved, with no clickable upstream credits. | Show experimental status and separate linked upstream contributions. | Updated About and the existing controls/editor harness pass on an isolated iPhone 14 / iOS 26.5 Simulator. |
| The normal contributor check stopped on absent ignored, game-derived experiment files. | Separate 18 explicit private-evidence commands from the source/prepared-dependency suite. | Default suite completes without game data. Private mode fails clearly when fixtures are unavailable. |

Implementations: [bootstrap](../scripts/bootstrap-dependencies.sh),
[dependency verifier](../scripts/dependency-lock.py),
[packager](../scripts/package-preview.py),
[report filtering](../apple/shared/GalaxyPadDiagnostics.mm),
[THP fallback](../apple/shared/GalaxyPadTHPPatch.c), and
[About](../apple/ios/GalaxyPadAboutViewController.mm).

The initial replay verifier has now been replaced by direct pinned-fork validation.
It checks declared submodule URLs/paths, gitlinks, checked-out commits, tracked
files and nonignored additions. Git-ignored generated/build inputs are outside that
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

## Completed fork migration

The runtime/compiler changes now live in maintained forks with original upstream
history. GalaxyPad tracks ModernGekko as a Git submodule; its nested gitlinks pin
RecompCore and DolRecomp. Bootstrap checks out these commits without applying or
recovering a production patch stack. Existing dirty dependency trees are preserved.

| Fork | Initial migration commit |
| --- | --- |
| [ModernGekko](https://github.com/chrissotraidis/ModernGekko) | `ab9044b7ce4b8f859423029b05e1ecc398723efc` |
| [RecompCore](https://github.com/chrissotraidis/RecompCore) | `5d535c77501148c58511a82a13fd678e89615502` |
| [DolRecomp](https://github.com/chrissotraidis/DolRecomp) | `448e98f2caa4cec7938dedd3fd43448d5a348004` |

[The migration manifest](../config/dependency-migration.json) maps every migrated
patch to its source revision, hash, integration commit and changed paths. Tracked
source blobs/modes were compared against the applied baseline: no unexplained
changes. Deliberate differences are the nested graph declarations and the existing
Simulator framebuffer compatibility patch, now committed so a Simulator build
cannot dirty its dependency checkout. Upstream attribution files are unchanged.
Unused experiments remain opt-in and are not applied by bootstrap.

The complete default source suite passes against fresh checkouts from the public
forks. Eleven real-Git fixtures cover mismatched pins, missing declarations, wrong
paths/URLs, local mirror overrides, missing checkouts and dirty source rejection.
The public-content gate permits only the exact ModernGekko gitlink under `ref/`;
it rejects ordinary files at that path and other tracked reference material.

[Contribution policy](../CONTRIBUTING.md), [agent instructions](../AGENTS.md), a
pull-request template and the source-check CI workflow require explainable changes,
focused regression evidence, exact dependency pins, preserved attribution and
explicit release/device evidence. CI runs the default suite and checks afterward
that dependency sources remain unchanged. The first hosted run exposed a missing
`rg` prerequisite: the old gate could report success without scanning. A regression
reproduced that failure; the gate now rejects the missing tool and CI installs it.

A fresh default bootstrap also initialized the required Apple build dependencies.
`bash scripts/build-desktop-tools.sh` then successfully built `moderngekko-port`,
`moderngekko-run` and `moderngekko-module-info` using Xcode 26.6 (17F113), Apple
Clang 21.0.0, with dependency sources verified clean afterward. This is a desktop
runtime/tool build, not generated-game-module or physical gameplay acceptance,
and it does not close the historical iOS release provenance gap.

## iPad source reconciliation after the migration

A reinstall audit found that the deployed build 13 iOS host used the later frozen
v8 audio implementation, while the old production patch stack reconstructed the
older Apple resampling path. The migration faithfully preserved that stack, but
it did not make it equivalent to the installed iOS binary.

The maintained RecompCore fork now contains the exact preserved iOS Mixer/Tempo
sources. CMake selects that variant only for iOS; the public header selects the
same layout from the iPhoneOS/Simulator SDK. Desktop keeps its prior implementation.
All consumers must be rebuilt together; swapping a single Mixer object is unsafe.
The source hashes and deployed-core linkage evidence are retained in the fork's
`Source/Core/AudioCommon/IOS/README.md`.

A source-only regression checks source identities, CMake selection, all three SDK
header paths and compiled frozen-tempo accounting/state behavior with sanitizers.
The separate offline mixer suite covers pitch, latency bounds, pause, restore,
stalls and unsupported input rate. This iOS policy supports the game's 32 kHz DMA
input; it is not a general audio-policy change for other games or desktop builds.

The full device app build also exposed a missing `GraphicsSettings.aspect_ratio_mode`
field/application path used by the app. The exact prior implementation is restored
in ModernGekko, with a compiled sanitizer regression for unset, standard, wide,
stretch and invalid values. CI now builds the iOS runtime and host without private
game inputs, in addition to the source suite, so this API mismatch cannot recur
without a build failure.

The reinstall retains the module from the actual build 13 installation receipt.
An older prepared folder with the same build number contains different code;
file-backed Mach-O section comparison distinguishes those artifacts. Source/build
checks do not substitute for physical playback or gameplay acceptance.

## Remaining engineering work, in order

1. **Build the next release from a complete frozen source tree.** The current
   supplement explicitly lacks a full historical iOS snapshot for every compiled
   source. Frozen audio inputs do not close that gap. Capture all source,
   generated build inputs, toolchain/configuration and artifact identities before
   promotion, then validate an in-place update with saves preserved.
2. **Expose retained import storage.** `GalaxyPadImportActivation.h` preserves
   previous multi-GB imports in recovery directories; removal intentionally keeps
   recovery copies. Repeated imports can consume storage without an in-app way to
   inspect and remove those copies. Add explicit recovery/storage management with
   save isolation and confirmation; automatic deletion is not the repair.
3. **Validate audio and private optimizations on hardware.** The Apple audio
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
