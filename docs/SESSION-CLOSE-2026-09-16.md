# September 16 session close: iPhone performance and next IPA

## Preview 3 release authorization and iPad feedback

The owner subsequently reported build 7166 working great on the iPad and explicitly
authorized a new IPA, README update, publication and main-branch merge. This
supersedes earlier publication-pending and iPad-feedback-pending statements below.
[Preview 3 notes](PREVIEW-2026-09-16.md) define the approved tested-build scope and
remaining limitations. The release workflow retains the tested app/module rather
than silently rebuilding gameplay code. Historical evidence below is unchanged.


This is the current handoff for future agents. Read it before continuing older
performance plans. Work is paused at the owner's request; no new IPA is authorized
for publication. The latest public release remains Preview 2, build 15 (verified
with GitHub on September 16). The latest private iPhone build is 7166.

## Subsequent authorized iPad test

The owner then requested a hardware iPad test. The same 7166 app is now installed
and running on the iPad Pro, with all 33 protected files unchanged and startup
frame activity verified. [Deployment and acceptance boundary](IPAD-7166-2026-09-16.md).
This supersedes the iPad-not-updated statements in the original checkpoint below.
Owner gameplay feedback is pending; no public release is authorized.

## Owner assessment and acceptance

At session close the owner describes the iPhone 14 result as pretty good and
working decently well, and is content to stop here for today. Treat 7166 as the
current usable checkpoint. Earlier feedback includes roughly 40–43 FPS, deeper
heavy-scene dips and severe audio chopping. The positive overall assessment does
not specifically establish that the audio complaint is repaired or that sustained
60 FPS is achieved. Game Mode is owner-confirmed on, with at most a slight,
uncertain improvement. Finger tracking accuracy remains open.

The owner called this as good as it can currently be on this phone. Record that
as the practical stopping point, not proof of an absolute hardware ceiling.
No matched whole-game performance gain has been established for this session.
There were real code fixes, component improvements and useful rejected hypotheses.

## Current code and artifact identity

- Working checkout: sibling worktree `galaxypad-refinement`, branch
  `codex/refinement-20260915`. Preserve the separate original checkout and any
  concurrent changes. Root implementation checkpoint: `ec6c32d`; subsequent
  session-close documentation does not rebuild the app.
- Maintained ModernGekko: `34c628eff7c064991503ea5bf61dc05c7617d339`.
- Nested RecompCore: `8b5cc3dfea61f1ca35c156d7581fe46a0bc03e71`.
- DolRecomp: `acb8e7b472f9a000ee98fbc52033f536c5e4bf4c`.
- Device: iPhone 14, iOS 26.6.2; bundle `org.galaxypad.GalaxyPad`, build 7166.
  The last installation preserved all 54 backed-up save/config/preference files
  byte-for-byte before launch. The iPad was not updated in this pass.
- Private artifact and receipt: `generated/game-mode-7166-20260916/GalaxyPad.app`
  and `receipt.json`. Read installation/readback evidence alongside the receipt;
  its pre-install note was retained. This is a personally signed local app, not a public IPA.
  Preserve the retained receipts for builds 7162–7166 and their input artifacts.
- 7166 changes only packaged metadata over 7165. The host derives from 7163 with
  one mixer object replaced for 7164/7165; the generated game module is retained
  from 7162. Current source HEAD alone is not an exact full-build recipe.
- Audio build flags explicitly enabled: `GALAXYPAD_AUDIO_BATCHED_SEARCH=1`,
  `GALAXYPAD_AUDIO_CACHED_ENERGY=1`, `GALAXYPAD_AUDIO_LOW_SPEED=1`.
  Retained module/runtime experiments include void/tail dispatch and indexed
  vertex batching. Consult their individual receipts for exact compile flags.
  Experiments remain opt-in in maintained sources, not silently promoted defaults.
- Render scale 1x and detailed performance logging were enabled. Rediscover live
  device/process state before any future operation; historical PIDs are not stable.

## What actually changed

| Change | Evidence and honest release wording |
| --- | --- |
| One Plus control instead of duplicate Pause controls | Installed since 7163; isolated UIKit checks passed and physical Plus control was visible. Say simplified pause controls; do not claim finger tracking was fixed. |
| Game Mode packaging repair | 7165 lacked three opt-in/category keys despite source declarations. 7166 restores them. Actual-package validator now runs during staging/packaging. Owner confirms Game Mode on. No meaningful FPS improvement established. |
| Audio search batching and cached sample energy | Exact-output checks passed; cached energy reduced complete synthetic Pull processing time by 8.71% versus already-batched search on the Mac. Say reduced audio processing overhead; never advertise 8.7% higher game FPS. |
| Low-speed audio starvation repair | Old 60% stretch floor could consume faster than the roughly 57% supplied input. Opt-in repair passed 42 standalone and 58 actual-mixer cases. A later live interval had no new counted gaps, but owner still reported poor sound. Say improved low-speed buffer handling; do not say choppy audio is fixed. |
| Indexed vertex batching and void/tail dispatch | Correctness/component evidence and private deployment recorded. No proven demanding-scene FPS improvement. Keep experimental qualification. |
| WBFS import compatibility, since public Preview 2 | Valid supported game content can be accepted across differing bounded single-disc WBFS layouts instead of requiring one container hash/size. Actual extractor accepted a padded variant with all 2,382 exported files matching. Other revisions/regions, ISO and split/multidisc WBFS remain unsupported. No reporter-specific acceptance or measured launch-time improvement. |
| Simulator configuration and regression checks | Overrides preserve experiment settings; useful development correctness, not an end-user speed feature. |

The WBFS and initial batching work began September 15 in this extended session;
do not label every change as authored September 16. Maintained forks, credits,
patch-stack removal and earlier Pull Star repairs already existed in public
Preview 2 and must not be presented as new features again.

## Research conclusions and rejected paths

The fresh 7163 Observatory profile had 29.33 seconds of game-thread CPU work in
30 seconds, 33 FPS, serious thermal state and 1x resolution. Runtime/lookup/dispatch
self costs totaled 23.84% of that thread; they are not all removable. Going from
40 to 60 FPS requires about one-third less frame time under fixed work. This is
larger than the demonstrated component savings. Lowering resolution or enabling
Game Mode does not eliminate the translated game-body work.

Do not repeat unchanged: aggressive machine outlining (smaller but slower),
conservative state forwarding (identical optimized objects), scalar FP state
batching, earlier lookup caches or naive helper vectorization. Disabling EFB depth
reads breaks Pull Stars and removes too little work. The earlier tiny ARM64 native
block prototype was slower despite correctness. The newer register-transfer probe
has only isolated savings and no dynamic coverage or gameplay proof; it is not
installed and does not justify another phone build by itself.

Remaining substantial option: compile a connected, frequently executed region
with register values retained across ordinary RAM operations and internal calls,
materializing state at required callback, timing, exception and exit boundaries.
Keep fallbacks for unsupported entries. Existing IR analysis is a starting point;
renaming registers or enlarging chunks alone is insufficient. A feasibility gate
must measure the complete region, demonstrate correctness and establish enough
actual runtime coverage before broader backend work or another claimed speedup.
Selective native replacements of expensive game routines are a separate,
more game-specific route. No architecture option currently guarantees iPhone 14
60 FPS. Waiting for complete decompilation is not a prerequisite for better AOT.

Primary external references and their relevance:

- [XenonRecomp](https://github.com/hedge-dev/XenonRecomp#optimizations): local guest
  registers and ABI-aware save/restore optimization; its gains are not ours.
- [N64Recomp](https://github.com/N64Recomp/N64Recomp#how-it-works): function-oriented
  static translation and direct known calls; different console assumptions.
- [QEMU TCG](https://www.qemu.org/docs/master/devel/tcg.html): block chaining with
  explicit event exits; use the principle offline, not runtime iOS JIT.
- [Dolphin ARM64 register cache](https://github.com/dolphin-emu/dolphin/blob/master/Source/Core/Core/PowerPC/JitArm64/JitArm64_RegCache.cpp): backend design reference, not a drop-in AOT implementation.
- [Petari](https://github.com/SMGCommunity/Petari): incomplete Galaxy decompilation,
  not a finished native port. Its Korean-version offsets cannot be blindly applied
  to our USA build. Respect the project's contribution policy.
- [Apple Game Mode](https://developer.apple.com/videos/play/wwdc2025/209/): opt-in
  and scheduling support; no documented public force-on/state-query API found in
  our investigation. Plist eligibility is not proof of active state.

## Proposed next IPA discussion, not publication approval

An experimental follow-up to Preview 2 has concrete value: WBFS compatibility,
simpler Plus controls, verified Game Mode packaging and audio processing changes.
It should be described as a refinement preview, not a 60 FPS breakthrough or a
confirmed audio-quality fix. Preview 3 is a possible name, not a reserved/published
release. Build 7166 identifies the private test app, not an existing public IPA.

Before packaging/release, agree which opt-in runtime changes to include, especially
the low-speed audio path with unresolved listening feedback. Record exact app,
recursive dependency, SDK/compiler, flags, module and compiled-input identities;
retain corresponding redistributable source and notices; audit the final archive
and recipient-signing procedure. Recheck the chosen candidate on iPad before
extending the phone feedback to that platform. Do not distribute personal signing
material, saves or game assets. Preserve in-place update identity and data.
No new IPA was produced, uploaded or published at session close.

## Evidence map and resumption order

1. This handoff and [status](STATUS.md): current owner assessment and build.
2. [Continuation](PERFORMANCE-CONTINUATION-2026-09-16.md),
   [phone feedback](IPHONE-FEEDBACK-2026-09-16.md),
   [audio slowdown](AUDIO-SLOWDOWN-2026-09-16.md),
   [Game Mode](GAME-MODE-2026-09-16.md): deployments, tests and acceptance history.
3. [Architecture](ARCHITECTURAL-PERFORMANCE-2026-09-16.md),
   [native functions](NATIVE-FUNCTION-FEASIBILITY-2026-09-16.md),
   [regions](REGION-FEASIBILITY-2026-09-16.md),
   [register transfer](REGISTER-TRANSFER-PROBE-2026-09-16.md): completed feasibility
   work and boundaries. Older future-tense proposals are historical; do not restart
   already completed experiments without new evidence.
4. [Refinement review](REFINEMENT-2026-09-15.md): GitHub/Discord complaint review,
   importer validation and maintained-fork decisions. Reports were not closed.
5. Read AGENTS.md and CONTRIBUTING.md. Runtime/compiler repairs belong in pinned
   maintained forks, never a new bootstrap patch stack. Keep all private evidence
   and concurrent work intact. Ask for current direction at the next session;
   there is no outstanding instruction to continue a background optimization loop.

## Documentation checkpoint validation

The complete default `bash scripts/check-repository.sh` suite passed at session
close, along with changed-document local-link checks, public-content checks and
`git diff --check`. This documentation update did not rebuild, install or publish
an app and does not add new physical performance evidence. Private validation
log: `generated/session-close-20260916/repository-check.log`.
