# Indexed vertex batch candidate: iPhone build 7161

## Implemented and installed

RecompCore commit `4858407278` adds an opt-in whole-batch software decoder.
ModernGekko commit `3562d469bd907db9f7108d0c0ee8abd9eb9725ef` consumes it;
the app dependency lock records full revisions. No bootstrap patches were added.

The candidate removes per-vertex indirect calls between position, normal, color
and texture-coordinate stages. It matches the complete existing pipeline before
selection: u16-indexed s16 XYZ positions, single s16 normals, optional indexed
RGBA8888 color zero, zero to eight consecutive indexed s16 ST coordinates,
optional position matrix byte, and the terminal vertex-skip stage. Other formats
use the existing software pipeline. No game ID/address is used for selection, so
the implementation can serve other Wii/GameCube ports using these formats.

This is the CPU implementation step from the feasibility assessment, not a Metal
decoder. It preserves the entire decoded output and cache/cursor/skip state.
Normal software builds keep `GALAXYPAD_INDEXED_VERTEX_BATCH=0`; this test build
compiles VertexLoader.cpp with it set to 1. No class layout or shader changes.
The opt-in path reports eligible/total input vertices at roughly million-vertex
intervals on stderr. These counters measure coverage, not GPU time or FPS.

## Validation

`tests/probe-indexed-vertex-batch.py` tests actual converter bodies against the
actual candidate matcher and kernel. Format resolver shims return the real
callbacks for the supported family. Synthetic fixtures exercise both matrix and
color options, 0–8 texture coordinates, 0–128 vertices, unaligned input/output,
random values, final-record position-skip masks, markers and near-match fallback
pipelines. Assertions compare full output buffers, all fixture caches, read/write
cursors, stage order and loader counters/state.

**11,760 cases passed under ASan/UBSan**, and the unsanitized run passed the same
checks. The full default repository suite passed with this regression included.
This is not exhaustive coverage of every format, floating-point mode or scene.

An alternating-order Mac microbenchmark of 128-vertex supported batches measured
candidate/reference median CPU-time ratios of 0.35–0.51 across eight tested
configurations. These figures include the candidate matcher and bounded reporting.
They are component measurements, not iPhone gameplay gains, and do not measure
the distribution of formats or draw sizes encountered in real gameplay.

Reproduce with a fresh output directory (omit --benchmark for correctness only):

```sh
python3 tests/probe-indexed-vertex-batch.py --output generated/indexed-batch-check --benchmark
```

## Device delivery and preservation

Build 7161 was installed in place on the attached iPhone 14, replacing build 7151.
Device app-list readback confirms 7161. The signed app passed deep/strict code-sign
verification and iPhoneOS platform verification. Its signer and entitlements
match the retained 7151 baseline; the provisioning profile's matching team wildcard
was validated. No signing identity or profile change was needed.

The device experiment replaces exactly VertexLoader.cpp.o in the retained 7151
audio-candidate core archive and relinks the same host objects. It retains the
same signed game module and audio implementation. It is not a full rebuild of
every dependency from today's source. Compile/link commands, source/header/object
hashes, base archive and signed host identity are in the private device receipt.

Before installation, 54 files across Wii data, configuration and preferences were
backed up. Readback before launch found every file byte-identical, with no added
or missing files. Game assets and saves were not replaced or cleared.

Private evidence: `generated/indexed-vertex-batch-20260916/`, including
`device/receipt.json`, `preservation.json`, `install.json`, `installed-apps.json`,
`final-check/`, `repository-checks.log` and `device-console.log`.

## Acceptance still open

QuickTime mirroring confirms physical startup and the title screen render normally.
The title screen displays 60 FPS, which is not a new gameplay performance result.
Early title-screen coverage is zero eligible vertices: those formats take the
generic path. That is not evidence about the demanding gameplay formats found
in the earlier CPU profile. The user has been asked to load the usual save.

The next decision depends on coverage and behavior in actual gameplay. If coverage
is low, inspect its exact formats before expanding the kernel; do not attribute
a title-screen reading to the optimization. Even strong decoding savings may
leave the saturated game thread limiting FPS. Sustained gameplay speed, rendering
and audio acceptance are not established by installation or the host benchmark.
