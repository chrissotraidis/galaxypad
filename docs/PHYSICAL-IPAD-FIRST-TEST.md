# First private physical-iPad test

Purpose: establish actual hardware behavior before extrapolating Simulator FPS.
This is an exploratory test, not shipping, full-story or device acceptance.

## Verified starting point, 2026-09-10

R913 supersedes the older stage for the next signing attempt:
generated/device-stage.ZaTANc/GalaxyPad.app. Host SHA
27b37908b9884d2ece7f064772127d11bc073de52cdc43cff25f1223ab8a3753;
module remains48f455ebc33f8eb2fc58151cd722ea756db77a5738a9573a0a49f0c656110041.
Release build/staging pass and include R912 report fields. Unsigned/uninstalled;
older artifact below preserved for rollback. No device-speed or UI acceptance.

- Existing Release stage: generated/device-stage.E7pIDj/GalaxyPad.app.
- Host SHA70b573b177d56e30d1d8054e17b34bc0f2f626ead44b91fe947926c1eaed0958;
  IOS/min16/sdk26.5 verified with vtool.
- Bundled module SHA48f455ebc33f8eb2fc58151cd722ea756db77a5738a9573a0a49f0c656110041.
- No device detected by devicectl; security find-identity reports0 valid signing
  identities. Stage is not install-signed. Do not claim install readiness.
- Product UI includes current volume/mute, Stop/Restart and accessibility changes.
  Phone Back/story control overlap, ergonomics, broader menu/lifecycle and audio
  acceptance remain open. Current Simulator diagnostic host is a different build.

## Preparation once iPad is connected

1. Record model, OS, available storage and device identifier. User unlocks/trusts
   the Mac and enables Developer Mode if required. Do not reset or erase anything.
2. Establish user's Xcode development team/profile and valid signing identity.
   Do not create paid accounts or accept agreements on their behalf. Sign a new
   private copy, nested module before app; verify profile/device/entitlement match.
   Preserve the unsigned stage and original hashes; no public upload.
3. Use the stable physical module above, not Simulator dylib or unproven R910
   optimization. Confirm imported user-owned data matches exact supported DOL.
   Keep local disc and existing saves untouched; use a separate backed-up test save.
4. Audit available diagnostics in this exact device build before timing. Simulator
   development launch flags and private recorder availability are not device proof.
   Instrument only if necessary, then identify the resulting exact candidate.

## Short first test

R912 source improves report context (platform/OS/thermal and cumulative DMA
counters with availability). Device/Simulator compile checks pass, but the
existing R884 stage does not include it; R913 stage does. Verify preview/export
on the actual signed copy. These report snapshots
are not a timed FPS window or CPU profile and must not be presented as either.

- Visible boot/import, title, pointer file selection and starting plaza.
- Stationary starting plaza, then invaded plaza: retain scene images, 30-second
  timing windows, device temperature/thermal state and audio observations.
- Distinguish emulation VI rate, CPU time and displayed frames. If only an FPS
  label exists, report it as provisional; never fabricate CPU/presentation data.
- User checks simultaneous move+jump, spin, pointer/shoot, crouch/camera, native
  menu dismissal, controls releasing on background, and audible music/effects.
- Stop using native menu, verify exported logs, then exit/relaunch. Any save test
  needs explicit visible reload, not merely a changed file hash.

## Decision

If hardware runs near full speed but Simulator does not, focus remaining work on
device stability/UI and keep Simulator useful for functional checks. If the same
heavy scene remains slow on hardware, profile that exact device build before
selecting another CPU transformation. Either outcome preserves all original PRD
requirements, including iPhone, full progression, saves, audio and release gates.
