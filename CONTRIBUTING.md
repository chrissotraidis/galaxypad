# Contributing

For a bug report, include the app version, device/OS, supported game revision,
scene and reproduction steps. Screenshots or reviewed diagnostic logs can help.
An upstream issue or commit link is useful when reporting a dependency regression.
Do not attach game images, extracted assets, generated game code, saves, NAND,
or signing material.

## Where changes belong

GalaxyPad is the Apple app. Its controls, import flow, platform integration and
packaging live here. A fork is a maintained copy of a dependency: changes to the
runtime or compiler belong in the ModernGekko, RecompCore or DolRecomp fork as
reviewable commits. GalaxyPad consumes those commits through pinned submodules.
Do not add another automatic bootstrap patch for a runtime or compiler change.

Preserve [upstream names, author history and attribution](CREDITS.md), including
license texts and per-file notices. Keep original project names visible when
describing the tools. Follow the receiving project's contribution policy for any
upstream proposal; a GalaxyPad change does not imply upstream endorsement.

## What a code review needs

`main` requires a pull request and an up-to-date passing `source-checks` status,
including for administrators. Automated checks support the review requirements
below; they do not establish gameplay or performance acceptance.

Explain the failing behavior, the repair and its validation. Keep changes focused
and consistent with the app. For behavioral fixes, include a regression that
reproduces the failure where feasible. Explain any case requiring manual testing.
Performance changes need comparable before/after measurements with the build,
device, OS and scenario recorded. Keep experiments opt-in; promotion to a default
requires separate review and evidence, not just a successful build.

Dependency updates must pin full commit IDs, including nested submodules, and
update the lock and documentation together. Do not use floating references or
overwrite local modifications to make a check pass.

Prepare the three pinned runtime/compiler repositories for source checks, run the
focused test for the changed component, then the complete repository suite:

```sh
bash scripts/bootstrap-dependencies.sh --sources-only
bash scripts/check-repository.sh
```

The default suite checks source and prepared dependencies without game data.
For an actual runtime/app build, run `bash scripts/bootstrap-dependencies.sh`
without `--sources-only` to initialize the required Apple build dependencies.
`--references` additionally prepares the pinned SunPad, Petari and template
research references; those are optional and remain unmodified.
Historical game-derived experiment checks are explicit:

```sh
bash scripts/check-repository.sh --with-private-evidence
```

That mode requires the recorded local fixtures and fails if they are missing;
it does not download them or silently count unavailable checks as passing.
UIKit tests use a separate isolated app; see `tests/run-mobile-ui.sh`. Do not use
a real save or game install as a test fixture. State unavailable checks in your PR.

Source checks and builds do not establish physical gameplay or audio acceptance.
Preserve existing game data, saves, settings and signing identity during testing.

## New release inputs

Record the app revision, recursive dependency commits, compiler/SDK versions,
build flags, generated-module identity, and hashes of compiled inputs and final
artifacts. Retain redistributable source inputs and third-party notices with
reproduction instructions; identify inputs that users must supply privately.
Missing provenance must be resolved before calling a new release reproducible.
Historical binary reproduction gaps remain documented until independently closed.

AI assistance has been used in this project. Contributors remain responsible for
understanding and reviewing their changes. Follow the receiving project's own
contribution policy when proposing fixes upstream.
