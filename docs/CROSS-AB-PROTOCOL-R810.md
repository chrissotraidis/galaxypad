# R810: matched plaza comparison protocol

R809 build53784 finished exit0 in R810; platform IOSSIMULATOR/min16/sdk26.5
and codesign verification pass. Counter-free module SHA256:
59e9fd166068a10b41b942fe1f32e9f3cef89b621d6ea15bb5684690b3cd418e.
Normal module hash unchanged. Baseline Simulator console58553 is now running
with generated/input-r810.json and generated/cross-baseline-r810.log. Save
backup GameData.before-r810.bin in the R809 directory matches99d432... .
No comparative speed result yet. Continue SAME live baseline, not another boot.

Question: does the R809 counter-free cross-product region improve end-to-end
plaza throughput compared with the unchanged module? R808 eligibility alone
does not answer this; its diagnostic frame-event windows remain16.6..26FPS.

Use the existing private R791 THP host in the one iPad Simulator. Baseline is
generated/build/ios-simulator-module/gRMGE01_recomp.dylib, SHA256
3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0.
Candidate is generated/candidates/cross-uninstrumented-r809/gRMGE01_recomp.dylib;
its finished signature/platform/hash checks are a prerequisite, not yet met.
Do not run either runtime while the linker remains active.

Keep game root, disc, host, native THP flag, frame-window logging, Simulator
device and pre-run save identical. Back up and hash GameData.bin before each
run; preserve any changed save separately rather than silently overwriting it.
Never select the instrumented R807 candidate for this speed comparison.

Route: A+B title, hover slot1 at normalized(.37,.67), then A; hover Play This
File at(.73,.88), then A. Hover must precede A so IR settles. Advance the story
pages with short A pulses. Wait for the visibly confirmed playable Star
Festival plaza. Do not move Mario during the comparison; the R808 movement
demonstration is not the matched starting pose. Let the scene settle15seconds.

Use scripts/capture-live-slowdown.py for45seconds, with the exact live PID, log,
unique generated output path and scene label. It rejects boundary frame windows
and records process identity, busiest host processes and system VM deltas.
Its three focused tests pass in R810. Capture screenshots immediately before
and after; discard a window if scene, focus or lifecycle changes. Record audio
DMA counter deltas separately; output counters unavailable means no audio
delivery claim. These legacy frame counts are after_frame_event, not display
completion; do not rename them as physical refresh measurements.

Run baseline then candidate as the first screen. If the apparent difference is
small or inconsistent, reverse order before drawing a conclusion. Any proposed
promotion requires reversed-order repeatability, no correctness/visual/input
regression, and retained host-load evidence. Do not promote from a single pair,
an isolated routine result or a faster title screen. If the effect is negligible,
park this region and use the measured dominant CPU work for the next target.

This protocol is not a result. Original PRD/SunPad UI, full gameplay, movie/audio,
stability and physical-device requirements remain open and unchanged.
