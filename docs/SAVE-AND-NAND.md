# Save and NAND

## R861 — packaged iPhone file recovery after import

Self-contained Simulator stage7BjbCR (host3de9facf/module32a92fdb) uses private
installed game data from R859 and its bundled module, with no external data/module
arguments. Only diagnostic input-file navigation enabled. Existing Mario file1
with creation time09/09/2026 18:50 is visible; Play reaches story then opening
plaza, and moveY0.7/3s visibly moves Mario. Clean native Stop and post-stop byte
comparison with pre-import save pass: SHA256
50b7290a05b5994115fac2476ed0c39ba60773899cbe14c0f441fce3e45722a4.
Evidence: generated/runtime/product-r861/runtime.log, recovered-file.png and
recovered-plaza.png. This is preserved zero-star file recovery, not new star
writes, corruption/forced-termination recovery, full first-play or touch acceptance.


R374: fresh-profile fix verified in runtime and promoted. StateSaves absent
before launch, automatically created; States Save1 writes39042803bytes,
SHA4a4217264a1968fc6b93fce8fb213eb9e50af1aaebf378cd2f14be9c28f15edb.
Movement changed position/camera; Load1 restored both, and input worked after
restore. Clean exit/fallback0/smc_failed0; slot and real NAND106e...2c90 hashes
unchanged. Evidence generated/runtime/profile-r374. Normal runner671729c6...d762;
rollback generated/macos/GalaxyPad.app.previous.r374. Same-process slot1 proof
only: not all slots, corruption handling, new in-game save or cross-process
state compatibility. Performance/audio/lifecycle matrix remains open.

R373: fresh-profile emulator slot writes previously needed manual StateSaves
creation. Runtime profile initialization omitted UICommon::CreateDirectories,
whose upstream implementation creates that path. Canonical0026 adds the standard
call after SetUserDirectory and before Init, only when runtime owns UICommon.
Structural ordering/pin regression passes; separate candidate build and actual
fresh-profile slot write/reload remain required. Normal app and NAND saves are
unchanged. This is emulator-state setup, not a substitute for in-game save proof.

## R363 dispatcher candidate new-save and fresh-process reload

Candidate5499889a558e44197bb740b3b3c5cc96187bcd80e3a8df097b814cb2703692e1,
diagnostic runner856b2e...2b0e, private profile generated/runtime/dispatch-save-r363.
No emulator states loaded. Source one-star GameData5040...64a6 preserved
outside this disposable profile. Real title/file selection loaded Observatory.
Held Plus0.4s opened the in-game pause menu; Quit→Yes produced the explicit
game-visible saved confirmation. A dismissed it; the final quit confirmation
returned to title. New GameData SHA256
106e8248bd8081404e8258a7ca33c54e0d476d651f139fde5ee2e4aad7302c90.
First process86776 exited0/native4808982602/fallback0/smc_failed0.
Fresh process72217 loaded the same newly saved file from title into one-star
Observatory. Control fixture produced visible movement/camera change. It
exited0/native2682444921/fallback0/smc_failed0; new save hash unchanged.
Evidence runtime.log/reload-runtime.log and named input logs in that profile,
game-visible confirmations captured in task. This proves this save/reload
case, not corruption/termination recovery, every save slot, or full G9.
Initial Plus0.15s did not open pause: reference PauseButtonCheckerInGame
requires12held frames. Corrected fixture0.4s works; no product input rewrite.

Status: **first Grand Star save/clean-relaunch/load proven; broader persistence matrix pending**

## First Grand Star persistence — R60/R61, 2026-09-06

On the accepted native-1× RMGE01 AOT module, R60 completed Gateway's switch machine and Grand Star pickup, reached the Observatory, unlocked the Terrace, and selected Yes in the game's save prompt. The game explicitly confirmed that it had saved, then returned to playable one-star Observatory gameplay.

After an orderly process exit, R61 launched the same runner/disc/module/NAND from the title screen. **No emulator state was loaded.** File select showed Mario slot 1 with one star and two Star Bits. Play This File restored the Observatory; directional movement and jumping were visibly exercised. R61 then exited normally. Both processes returned exit 0, `fallback=0`, and `smc_failed=0`.

- NAND: ignored `generated/runtime/g6-resume-r57/Wii/title/00010000/524d4745/data/GameData.bin`.
- SHA-256 after R60 save and again after R61 shutdown: `5040acdd95157448d660fd02f03c16c17e240523bdfa889ccbd253f9fe5364a6`.
- Logs: ignored `generated/runtime/g6-panels-r60.log`, `generated/runtime/g6-save-reload-r61.log`.
- Screenshots in R57: `05-57-38` save confirmation; `06-00-26` fresh-process one-star file; `06-01-01` loaded Observatory; `06-01-23` movement after load, all dated 2026-09-06.

This proves the first-Grand-Star normal-save and clean-relaunch path. It does not prove crash durability, copy/erase, import/remove separation, recovery/corruption handling, mobile lifecycle, or the full persistence matrix. D3's remaining timing/audio and packaged-entry requirements are not waived: final loaded-Observatory title read 53.3 FPS, with 11 underruns and one backlog drop in the pause-heavy R61 session.

## Historical fresh-file creation

The G5 run used a new isolated, ignored user directory. The guest created `GameData.bin` (48,640 bytes) and `banner.bin` (29,344 bytes) under the expected RMGE01 Wii title-data directory. The private native screenshot visibly shows the newly created Mario file in slot 1.

For local evidence correlation only:

- `GameData.bin` SHA-256: `a5743199ed343b04d2d02069881d8754310194ed2b3012f4ec54152272a2afa6`
- `banner.bin` SHA-256: `bb36d744eb39166f7d8c4c0d182ef7893075034e92473ecbb6aee8c4482e1ef3`
- private screenshot SHA-256: `63fb17e46650e587ac5e79bdb9557490b9182bd82d61a27ff20adcb7e1e658a0` (2501×1368)

The files and screenshot remain under ignored `generated/` storage and must never be committed or uploaded. This proves creation and one game-visible state, not Grand Star progress, relaunch/load, copy/erase, termination durability, backup/recovery, or corruption handling.
