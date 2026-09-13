# Credits and provenance

GalaxyPad depends on the work of the following projects and their contributors.
The Apple integration does not replace or claim authorship of their tools.

| Project | Contribution |
| --- | --- |
| [ModernGekko — Hyperway, ExpansionPak and contributors](https://github.com/ExpansionPak/ModernGekko) | Runtime integration and game-port tooling |
| [DolRecomp — ExpansionPak and contributors](https://github.com/ExpansionPak/DolRecomp) | Ahead-of-time PowerPC code generation |
| [RecompCore — ExpansionPak and contributors](https://github.com/ExpansionPak/RecompCore) | Dolphin-derived static-recompilation runtime; includes GXRuntime |
| [Dolphin Emulator contributors](https://github.com/dolphin-emu/dolphin) | Underlying Wii/GameCube hardware, graphics, audio, and input implementation |
| [ModernGekko-Template](https://github.com/ExpansionPak/ModernGekko-Template) | Pipeline reference |
| [SunPad](https://github.com/chrissotraidis/sunpad) | Apple integration and touch-control foundation |
| [Petari — SMGCommunity and contributors](https://github.com/SMGCommunity/Petari) | Galaxy semantic and source-map reference |
| [Wiimms ISO Tools](https://wit.wiimm.de/) | Game-image inspection and extraction |

ModernGekko's [upstream credits](https://github.com/ExpansionPak/ModernGekko#credits)
also acknowledge SpecialK / aharonahdoot for RecompCore and Literally God /
MrPoloGit for the recompilation template and macOS support, alongside the Dolphin
team. Those credits and the upstream contributor histories remain authoritative.

Exact upstream base revisions are in [the dependency lock](config/dependencies.lock.json).
Effective source also includes integration patches; the base revision alone does
not describe every compiled input. See [the upstream review](docs/UPSTREAM-REVIEW.md)
and [third-party notices](THIRD-PARTY-NOTICES.md). This page supplements original
licenses and per-file attribution; it does not replace them.

## AI assistance and artwork

GalaxyPad development has used AI assistance. The project maintainer remains
responsible for understanding, reviewing, and validating accepted changes. That
assistance does not imply upstream involvement, endorsement, or authorship.

The app icon was AI-generated; its retained prompt and process are documented in
[branding provenance](apple/branding/README.md). README gameplay screenshots are
owner-supplied captures, as described there. Nintendo's game, characters, and
trademarks belong to their respective rights holders; no affiliation is implied.
