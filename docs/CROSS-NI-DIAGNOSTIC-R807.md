# R807: NI-capable diagnostic passes source gate; private link active

R806 made progress by observing NI1/RN0 and correcting the bounded source path.
Added explicit --ni mode to scripts/build-cross-diagnostic.py. Its output is
generated/candidates/cross-diagnostic-r807; R804 files are not overwritten.

Before reusing the R804 control, the builder rehashes all1329 objects and the
baseline/control binary, compares complete object inventories, compiler flags,
linker flags/install name and response inputs with retained provenance. All
checks pass, avoiding an unnecessary second unchanged-control link. The helper
hash is checked before expensive work. Normal source/build graph/module selection
remain unchanged.

The generated diagnostic uses r807 counter labels and a rounding-only mode
guard; bounded NI support comes from the tested helper, not a change to the
game's FPSCR. Counter replacement anchors are checked explicitly.

Source SHA8b7996a4b5c74f8f28979cf91ed44920bb766243c434e11927c8843ed9ff349d.
Helper SHA2186c80040d479474785b8c193e494f068b6e518cc37dc7dc5882048ab0fbd4d.
The exact instrumented source regression runs automatically before linking:
262,144 complete CPUState/FPSR cases pass,48,258 accepted paths,256 tie fallbacks,
64 counter records. This is synthetic coverage, not gameplay eligibility.

## Scene-window reporting

Counter summarizer accepts r804/r807 and rejects mixed versions. Added explicit
inclusive --start-line/--end-line bounds so a visually confirmed scene can be
isolated from startup/menu traffic. Results retain whole-log hash and line range;
fractions measure only the first-to-last complete counter observations within
that selection, not exact scene-entry time. Missing/reset/inconsistent windows
and empty/invalid line selections reject. Focused tests pass.

## Exact continuation

Build exec29185 is live; do not restart. It has completed verification, candidate
compile and instrumented-source regression, and is now linking the private
module. Last linker PID46900,parent46899, elapsed2m59s at~677%CPU. Poll the SAME
handle until final platform/signature/hash checks complete. No finished module
or Simulator result claimed yet.

Logs: generated/cross-build-r807.log/.err. Expected stderr includes synthetic
counter lines and profile warnings; do not call it empty. Provenance is in the
new private directory and already records validated control/object/source facts.
generated/cross-synthetic-summary-r807.json is explicitly synthetic.

No Simulator booted, no app/module promotion or save changes. Once this exact
candidate finishes, use the one iPad Simulator with renewed save protection,
verify its loaded path and observe eligibility in a clearly identified scene.
No more testing the old NI-rejecting binary; no FPS claim from diagnostic timing.
Full original PRD/SunPad/gameplay/audio/stability/device objective remains active.
