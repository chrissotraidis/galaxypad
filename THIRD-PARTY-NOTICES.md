# Third-party code and source

See [Credits and provenance](CREDITS.md) for linked upstream projects and their roles.

GalaxyPad integration files retain their per-file SPDX identifiers and attribution.
GPL-3.0-or-later integration code is distributed under the accompanying LICENSE.
Other upstream files retain their own licenses.

The runtime adapts ModernGekko, its Dolphin/RecompCore and GXRuntime dependencies,
and Apple integration patterns from SunPad. DolRecomp generates ahead-of-time
modules. Exact pinned references are in `config/dependencies.lock.json`; local
runtime changes are recorded under `patches/` and in release source supplements.

Binary previews include PreviewNotices with original license texts from the runtime
and its bundled third-party dependencies. The release source supplement contains
runtime source and frozen audio inputs; the matching GalaxyPad integration source
is available at the release tag. Consult its corresponding-source instructions for
build inputs and known reproduction limits.

Game images, extracted game assets, and saves are not included. The binary packages
do include an AOT game-code module. The project does not grant rights in the original
game. Rebuilding that module requires the supported user-supplied input.
