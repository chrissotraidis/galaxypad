# Contributing

For a bug report, include the app version, device/OS, supported game revision,
scene and reproduction steps. Screenshots or reviewed diagnostic logs can help.
An upstream issue or commit link is useful when reporting a dependency regression.
Do not attach game images, extracted assets, generated game code, saves, NAND,
or signing material.

For a code change, explain the failing behavior, the repair and the validation.
Keep changes focused and preserve [upstream attribution](CREDITS.md). Include
before/after measurements for performance changes. Source checks and builds do
not establish physical gameplay or audio acceptance.

Run the focused test for the changed component, then the repository checks:

```sh
bash scripts/check-repository.sh
```

The default suite checks source and prepared dependencies without game data.
Prepare the pinned dependencies with `scripts/bootstrap-dependencies.sh` first.
Historical game-derived experiment checks are explicit:

```sh
bash scripts/check-repository.sh --with-private-evidence
```

That mode requires the recorded local fixtures and fails if they are missing;
it does not download them or silently count unavailable checks as passing.
UIKit tests use a separate isolated app; see `tests/run-mobile-ui.sh`. Do not use
a real save or game install as a test fixture. State unavailable checks in your PR.

AI assistance has been used in this project. Contributors remain responsible for
understanding and reviewing their changes. Follow the receiving project's own
contribution policy when proposing fixes upstream.
