# GalaxyPad documentation

## Playing the current release

**GalaxyPad 0.2.3 (7219)** is the current iPhone/iPad release. Use **PadMint 0.5.2
or newer** on an Apple silicon Mac to build your personal IPA, then import your
own USA RMGE01 revision 0 WBFS image in the app. There is no public prebuilt IPA.

| Read | Purpose |
| --- | --- |
| [Get GalaxyPad](../README.md#get-galaxypad) | Short build and install path |
| [Install on iPhone or iPad](INSTALL_IPAD.md) | Xcode, PadMint, signing, import and updates |
| [0.2.2 release notes](RELEASE-0.2.2.md) | Files folder and import guidance repair, validation and remaining limits |
| [0.2.1 release notes](RELEASE-0.2.1.md) | Menu repair, exact revisions, checks and remaining limits |
| [0.2.0 release notes](RELEASE-0.2.0.md) | Introduction of the New engine and device performance evidence |
| [Status](STATUS.md) | Current handoff followed by dated history |
| [Input and pointer](INPUT-AND-POINTER.md) | Current controls followed by Old engine findings |
| [Gyro cursor](GYRO-CURSOR.md) | Motion aiming and its validation limits |
| [Ride controls](RIDE-CONTROLS.md) | New engine main-stick behavior versus historical manual modes |
| [Save handling](SAVE-AND-NAND.md) | Safe updates and the two engine save locations |
| [Disc identity](DISC-IDENTITY.md) | Accepted region/revision and WBFS validation policy |

## Development and release records

- [Contributing](../CONTRIBUTING.md) and [agent instructions](../AGENTS.md) cover
  ownership, validation, private data and release checks.
- [Dependencies](DEPENDENCIES.md), [credits](../CREDITS.md) and
  [third-party notices](../THIRD-PARTY-NOTICES.md) distinguish the New engine
  (MacioGalaxy/Petari) from the Old engine (ModernGekko/RecompCore/DolRecomp).
- [Release readiness](RELEASE-READINESS.md) and [publication scope](RIGHTS-STATUS.md)
  describe what is public and what remains a personal build.
- [Engine integration](ENGINE-SWITCH-PLAN.md) and [native engine research](NATIVE-ENGINE-PLAN.md)
  retain the implementation sequence. Their current-outcome sections supersede
  earlier proposal and private-probe status statements.
- [Journal](JOURNAL.md) preserves the detailed development history.

## Reading historical documentation

Most files in this folder are dated September research or numbered experiment
records for the **Old engine**, which is now [deprecated](OLD-ENGINE-DEPRECATION.md).
Their build IDs, performance numbers, private-module requirements, release holds,
and "current" or "next" actions apply to the session they record. They are not
instructions for the current PadMint build. Some retired scripts remain named as
historical evidence; the deprecation record explains where to recover them.

The original PRD, goal loop, execution queue and Mac development records remain
available for context. The current mobile release does not imply completion of
every original macOS, full-game, device or audio acceptance gate. Use the current
release notes for tested artifacts and outstanding checks.
