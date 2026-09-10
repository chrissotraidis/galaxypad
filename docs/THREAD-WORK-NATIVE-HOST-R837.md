# R837: native counter host ready; no game launched

Previous turn progress: R836 complete Simulator CPU-thread evidence. This turn
extends the isolated builder with --native and prepares the matching native
recorder host/profile. Full original PRD/performance priorities remain active.

## Cache/source and control evidence

Desktop compile_commands.json omitted the runtime row, although the actual Ninja
object rule exists. Builder queries that exact rule, removes dependency-output
flags to avoid changing cached depfiles, and redirects only its object output.
The resulting unchanged runtime object is byte-identical to the archived object.
Desktop post-link Sys copy is recognized exactly and never executed against the
normal cache; candidate reuses the R730 bundle's existing resources.

First attempts stop before candidate build: r837 absent compile-database row;
r837b/88715 different post-link shape; r837c/60597 and r837d/31150 unsigned control
metadata mismatch. Each is terminal, retained, and not a game run. Renaming the
control output to original moderngekko-run does not resolve UUID difference.

Control unsigned size21,977,240 matches R730. Exactly18bytes differ:2 in parsed
read-only __LINKEDIT vmsize and16 in LC_UUID. Original UUID
124DCED6-5D2A-35CC-BE5F-5CB858ACEE93 versus relink512DC718-FCD2-344F-B1D6-B7916BFA1C48.
All other bytes, including every code/data byte and other load-command fields,
are identical. Native comparison explicitly permits one structurally valid
LC_UUID and the existing aligned/read-only/sectionless LINKEDIT reservation;
Simulator comparison still requires UUID equality. This is metadata-normalized
content equality, not identical binary identity. Cause of linker UUID difference
is not established. No arbitrary byte mask or instruction differences ignored.
tests/test-host-linkedit-comparison.py verifies opt-in UUID behavior and rejects
changed content or malformed/writable/sectioned reservations.

## Successful build and profile

`python3 scripts/build-thread-work-host.py --native --output generated/candidates/thread-work-native-r837e`
completes39453exit0. Only the runtime object receives private VFS header overlay
and compile define, then replaces the unique member in a copied archive. All
other objects, original archive/app and game module remain untouched. Baseline
archive/app hashes are checked after completion. Existing duplicate-library linker
warnings remain visible, not suppressed. Ad-hoc codesign deep/strict passes.

Ready executable:
`generated/candidates/thread-work-native-r837e/candidate/GalaxyPad.app/Contents/MacOS/GalaxyPadRunner`

SHA9ee5404f6b5a59dde2cb633cadd5e5dda9440ead728d7f21ab19c3ff71c41857.
vtool: MACOS min14.0 SDK26.5 LD1267.0. All exact source/object hashes and compile/
link commands in provenance.json. No app has been launched or selected normally.

Fresh private profile generated/runtime/thread-work-native-r837 copies only R830
Config/Wii/config.ini and advance-story.json, with independently configured Pipe.
No caches/screenshots/states copied. GameData99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f
matches reference and remains unchanged. No Simulator/game running.

## Next exact lane

Launch this executable with R830 explicit game root/module, --user-dir pointing
to thread-work-native-r837, --graphics Metal --audio Cubeb. Set
GALAXYPAD_VI_TIMING=<profile>/vi.csv and GALAXYPAD_THREAD_WORK_TIMING=<profile>/work.csv,
STATICRECOMP_NO_FALLBACK_JIT=1, GALAXYPAD_LC_BYTE_FAST=0, GALAXYPAD_LC_PAIR_FAST=0.
No native-THP mod or direct-call binding. Use existing title/play/story Pipe
fixtures promptly with screenshot verification, then same neutral plaza30s
capture with10s warmup and matching pointer. Resolve CUA by exact running
candidate app path; do not launch another native app via stale identifier.

Clean native Quit exports both recorders. Require complete window and save hash,
then compare CPU-thread instructions/cycles/core-class time with R836, retaining
host/audio/module-target differences and query uncertainty. Do not repeat this
build or the completed Simulator measurement. No performance gain or product
gate is claimed from native build success; full PRD/SunPad/audio/stability/device
objective remains unchanged.
