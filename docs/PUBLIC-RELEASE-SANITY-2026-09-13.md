# Public preview sanity check — September 13, 2026

Scope: public main at `55123a4d30c4d2d5e29012314924aaa439d0dc85`, reachable
Git history, and the six published `v0.1.0-preview.1` assets. This audit supports
the experimental preview description; it does not establish stable or full-game
acceptance. No runtime code, installed app, signing identity, or save was changed.

## Corrections

- Added the community Discord badge and support link. The supplied invite resolved
  successfully with no reported expiration.
- Corrected current README, installation, preview, readiness and status text to
  reflect the public repository. Historical development entries remain dated.
- Moved the existing tracked-content audit ahead of dependency-dependent tests,
  exposed it as `bash scripts/check-public-content.sh`, and added isolated positive
  and negative fixtures. It reports filenames rather than matching secret values.
- Added mixed-case game-image ignore coverage, GCM and GameData.bin protection;
  the tracked-file gate also rejects certificate and environment files.

## Results

- Current tracked-content and ignore checks pass. Pattern/path inspection of 1,203
  historical blobs found no credential-pattern or prohibited-file matches. One
  historical document contains a personal filesystem path already removed from
  current main; history was not rewritten. Pattern scanning is not exhaustive.
- Downloaded all six release assets. All five entries in SHA256SUMS.txt match.
  Both app archives pass protected-content and ZIP integrity checks. All 2,718
  iOS and 2,724 macOS manifest file hashes match the downloaded archive contents.
- The source supplement has 27,418 files and no prohibited game/save/signing
  filenames. Credential-pattern matches were inspected: upstream curl/mbedTLS
  example certificates and key parser/writer literals, plus a zlib compression
  test-data false positive. These are source fixtures, not project credentials.
- License notices and corresponding-source instructions are included. The app
  archives explicitly include the game-derived AOT module. They exclude the
  original game image, extracted assets and saves. This audit does not determine
  redistribution rights or certify source-reproduction completeness.
- All five pinned repository revisions resolve through GitHub. Public entry-point
  documentation has no missing local Markdown targets. Dependency versions were
  kept pinned to the tested runtime.
- Privacy, archive rejection, controller/pause, input/settings/import and focused
  audio-interruption and guarded Wiimote checks pass. The repository suite still
  stops at `tests/test-thp-dead-pc.py` because the ignored experimental input
  `generated/thp-kernels-r198-exits/candidate.c` is absent. The full suite is not
  green. A clean checkout additionally needs bootstrapped runtime dependencies;
  the broad run here used the existing local ModernGekko checkout.

## Remaining limits

Latest-build iPhone gameplay, sustained performance/audio, long sessions and
full-game coverage remain open as documented in [preview notes](PREVIEW-2026-09-13.md).
The Mac app is not notarized; the IPA requires recipient signing. Historical iOS
module/PGO inputs still limit clean-source reproduction. Existing archive notices
retain their original private-preview wording and disclose possible build-machine
paths in compiled diagnostics; the audited binaries and checksums were preserved.
No new device or gameplay acceptance is claimed by this repository audit.
