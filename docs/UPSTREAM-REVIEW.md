# Upstream integration review — September 14, 2026

This review separates verified source findings from remaining engineering work.
It is not a claim that upstream maintainers endorse GalaxyPad or that all
runtime defects have been resolved. [Credits and provenance](../CREDITS.md)
identify the tools and their contribution.

## ARM64 JIT fallback concern

A concrete candidate is [RecompCore PR #6](https://github.com/ExpansionPak/RecompCore/pull/6),
“JitArm64: implement the StaticRecomp fallback contract.” The defect could leave
execution in the fallback JIT instead of returning to covered AOT code. The fix
disables fallback block linking, checks whether StaticRecomp wants the next
address, and stores the dispatcher PC before yielding.

The locked RecompCore base is `13e492094902644b0d113c586300d358640f9e19`.
Git ancestry confirms it already includes PR #6's merge commit,
`202704caa71574c9a89a65c7e4f0d35cbb7e1399`. Do not backport this fix again.
The maintainer's exact issue/commit is still needed before equating their report
with this particular defect.

The [Preview 1 release](https://github.com/chrissotraidis/galaxypad/releases/tag/v0.1.0-preview.1)
source archive has SHA-256
`5996996e4e62491cb0c2cdc18b5c67afab3e693e7df75467a787569eb081c3f1`.
The locally audited archive matches the published GitHub asset digest. Its Mac
source contains all three changes above. Its ARM64 fallback creation is excluded
under `__IPHONE_OS_VERSION_MIN_REQUIRED`.

Reproduce the read-only archive check with Python 3.11 or newer:

```sh
python3 scripts/audit-preview-jit-source.py /path/to/GalaxyPad-runtime-source-0.1.0-preview.1.tar.gz
```

The script verifies the exact archive identity and relevant source markers without
extracting or executing its contents. This is not a semantic regression test,
proof of binary execution, or proof of the historical iOS compiler inputs.

## Dependency maintenance

The root bootstrap is 904 lines and reconstructs pinned upstream checkouts with
SunPad baseline patches and GalaxyPad overlays. Its manual peel/reapply ordering
and repeated patch hashes make maintenance difficult. Some tests assert textual
patch order; they supplement, rather than replace, behavior tests.

A pinned fork/submodule design is a reasonable direction. It must preserve the
nested graph: ModernGekko contains RecompCore/Dolphin, which contains DolRecomp.
Changing only the outer checkout will not eliminate changes in those dependencies.

Migration acceptance criteria:

1. Reconstruct a clean source tree from the lock and approved patches in isolation.
   Compare it with the release source and explain every difference. Do not commit
   an arbitrary dirty `ref/` checkout or generated game code into a fork.
2. Put necessary integration changes into reviewable commits on the appropriate
   dependency fork. Separate experiments from release fixes and preserve notices.
3. Pin nested dependency commits, then pin ModernGekko in GalaxyPad. Replace the
   patch-recovery machinery only after a clean recursive checkout reproduces the
   intended source. Publish a base-to-integration diff for each dependency.
4. Rebuild tools, runtime and module with explicit identities; compare matched
   gameplay, audio, input and saves on the affected platforms before promotion.

**This migration has not been performed.** Replacing the dependency graph solely
to change its appearance would not establish correctness or reproducibility.

## Release reproduction gap

The shipped source supplement explicitly states that a fully hashed historical
iOS runtime source snapshot was not captured for every compilation unit. Frozen
audio inputs are preserved, but the current iOS overlay is not a complete
historical source snapshot. Exact clean-room reproduction of that device binary
has not been established.

A future release needs a fresh build from a complete frozen source tree, including
nested dependencies, toolchain/configuration and module-generation inputs. Capture
that tree before compilation and retain its manifest alongside the artifact.
Existing saves and signing identity must survive an in-place device update.
Build success alone does not close physical gameplay/audio acceptance.

## Scope and review standard

GalaxyPad's immediate purpose is an Apple integration for the original supported
Galaxy revision, including Wii input adaptation. New levels are not required for
that purpose. Changes to runtime or input behavior should be justified by a
reproducer and checked for regressions, not added to demonstrate activity.

AI assistance and icon provenance are disclosed in the credits. Concrete quality
reports should identify the code, failing behavior or maintenance problem. The
maintainer remains responsible for understanding and validating accepted changes.
See [contribution guidelines](../CONTRIBUTING.md).
