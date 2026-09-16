# Working on GalaxyPad

Keep changes simple, focused and consistent with the existing application design.
Recheck controls and navigation after changing their wiring. Do not suggest Figma.
Read [CONTRIBUTING.md](CONTRIBUTING.md) before implementation.

## Ownership and dependencies

- GalaxyPad owns its Apple app, controls, import flow and packaging. Runtime and
  compiler changes belong in the maintained ModernGekko, RecompCore or DolRecomp
  fork, with reviewable commits. Update the app's pinned submodule reference to
  consume them; do not recreate a bootstrap patch stack.
- Preserve upstream names, author history, license texts and per-file attribution.
  Describe GalaxyPad's changes separately from upstream work. Follow an upstream
  project's contribution policy before preparing a submission to it.
- Pin dependencies and nested dependencies to full commit IDs. Keep the dependency
  lock, submodule references and documentation consistent. Never use a floating
  branch or tag as a release input or reset a dirty dependency checkout silently.

## Changes and validation

- Understand and explain each accepted change. Fix a concrete problem; avoid
  unrelated refactors, duplicate implementations and speculative optimizations.
- For a behavioral repair, reproduce the failure and add a focused regression
  where feasible. Keep experiments opt-in and outside normal build defaults.
  Moving an experiment into the default path requires separate review and evidence.
- Run focused checks and the complete default `scripts/check-repository.sh` suite
  with prepared dependencies. Report failures or unavailable checks directly;
  do not weaken a gate or substitute source-string checks for runtime behavior.
- Private game-derived checks use `--with-private-evidence` explicitly. A build,
  Simulator run or synthetic input test does not prove physical gameplay, audio
  quality or performance. Record device, OS, build and scenario for device claims.
- Preserve game data, saves, settings, signing identity, existing installations
  and concurrent work. Use isolated test data and checkouts. Never publish game
  images, extracted assets, saves, NAND, credentials or signing material.

## Release evidence

For each new release, record the app revision, recursive dependency commits,
compiler/SDK versions, build flags, generated-module identity, and hashes of all
compiled inputs and final artifacts. Retain redistributable source inputs and
third-party notices with reproduction instructions. Identify inputs users must
supply privately. Missing provenance is unfinished release work; an old binary
cannot acquire a complete source history by updating today's checkout.

Do not describe a change as merged, published or device-validated before it is.

## Current performance handoff

Before resuming performance work, read
[the September 16 session-close handoff](docs/SESSION-CLOSE-2026-09-16.md) and
[STATUS](docs/STATUS.md). They distinguish the latest private phone build, public
release, owner feedback, rejected experiments and unresolved architectural work.
Do not treat historical plans or component benchmarks as current gameplay gains.
