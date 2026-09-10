# Wii subsystems

## G2/G4 substrate and boot state

| Subsystem | State | Evidence |
|---|---|---|
| Platform detection | boot-proven | `boot.bin` Wii magic selects `GamePlatform::Wii`; runtime title is `SUPER MARIO GALAXY [RMGE01]` |
| CPU profile | generation and runtime proven | explicit Broadway guard; exact AOT entry executes with sustained native dispatch |
| MEM1 | boot-proven | retail 24 MiB model is selected by the Wii platform path |
| MEM2 | boot-proven | 64 MiB at physical `0x10000000`, cached `0x90000000`, uncached `0xd0000000`; exact Wii module runs beyond boot |
| Disc interface | boot-proven | exact extracted disc root boots and continues native guest execution |
| IOS/ES/NAND/SYSCONF | boot-proven | isolated run creates `Wii/sys/uid.sys`, `Wii/shared2/sys/SYSCONF`, WC24 state, and `fst.bin` |
| DSP/audio | initialized | headless reports Null audio; Metal reports Cubeb and shuts it down cleanly |
| GX/EFB | initialized | Null and Metal backends both pass renderer initialization; Metal run sustains 436,246,556 native dispatches |
| WPAD/KPAD | initialization path passed | boot proceeds past controller initialization; actual pointer/button behavior is deliberately deferred to G5 |

The pinned DolRecomp has a dangerous behavior: when `database/titles.txt` is absent, it announces a GameCube-mode fallback. ModernGekko's port tool explicitly supplies `--cpu broadway`, which preserves the CPU profile, but naming and title semantics can still degrade. GalaxyPad's wrapper requires an exact `RMGE01` entry, supplies Broadway explicitly, requires the Wii-named output folder, checks the emitted CPU macro, and rejects fallback text.

The reproducible headless smoke is `./scripts/smoke-macos-runtime.sh headless 55`. Its latest recorded shutdown had 116,469,500 native calls, zero interpreter fallback, and zero failed SMC events. A separate Metal run reached 436,246,556 native calls with the same zero counts. These satisfy boot initialization only; they do not claim title visibility, correct EFB behavior, input, audio quality, file creation, or gameplay.
