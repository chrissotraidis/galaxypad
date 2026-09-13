# Contributing

Changes should be small enough for a reviewer to understand and reproduce. Explain
the failing behavior, why the change fixes it, and the checks actually performed.
Preserve upstream attribution and licenses. See [credits](CREDITS.md).

For runtime reports, include the app version, platform, supported game revision,
scene and reproduction steps. A suspected upstream regression is especially
useful with an issue or commit link. Do not attach game images, extracted assets,
generated game code, saves, NAND, or signing material.

For dependency changes, record the upstream base, effective change, and relevant
upstream issue or fix. Check whether upstream already contains the repair before
adding another patch. Separate diagnostic experiments from release changes.
Include measured before/after evidence for performance claims. A passing source
check or successful build does not establish gameplay correctness.

AI-assisted contributions follow the same review standard: the contributor must
be able to explain the code and its evidence. Do not submit generated changes you
cannot explain, invented test results, or claims of upstream endorsement. Follow
the receiving project's contribution policy when proposing work upstream.

Keep technical criticism specific and respectful. Requests for game-download
links, including requests to exchange them in DMs, do not belong in project
issues or the community server.
