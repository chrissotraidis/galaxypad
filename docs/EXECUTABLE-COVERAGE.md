# Executable coverage

Status: **exact AOT/module proven; gameplay coverage pending**

## Exact executable inventory

| Path | Size | SHA-256 | Classification |
|---|---:|---|---|
| `sys/main.dol` | 6,283,264 | `2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09` | primary Wii executable; AOT target |
| `files/ModuleData/HomeButtonMenuWrapperRSO.rso` | 194,816 | `13dd2229f88b5af0f18875b3db15f4d3a52ea583085606a50e4b760a2e68194e` | dynamically loaded HOME-menu code; must be replaced by a bounded native adapter on mobile |
| `files/ModuleData/product.sel` | 5,600 | `c37a0ff9bf9b86f8d46b0ac5c360f747add24178c2a81951ad4ecd06a65d6730` | RSO symbol-selection metadata; contains symbol names but is not standalone executable code |

The deterministic 2,386-file manifest contains no other `.dol`, `.rel`, `.rso`, or `.elf` path. A large-file host `file(1)` scan found no additional recognized executable/object container; because DOL/RSO are not reliably recognized by host `file(1)`, this is supporting evidence, not a proof by itself.

## Current coverage

- AOT input: exact `sys/main.dol` SHA-256 `2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09`.
- Entry point: `0x8000403c`.
- Portable C output: 331 chunks; zero unknown instructions.
- Explicit interpreter-capable inventory: 419 named PCs covering 102 named mnemonics. The complete ignored manifest is `generated/aot/rmge01-fallbacks.txt`; `scripts/audit-aot.sh` fails if any row is unnamed.
- SMC guards: 19 conservative candidate ranges. Four are `icbi` sites; the other 15 are bounded stores selected by DolRecomp's linear known-address analysis. All remain guarded; see `SMC-ANALYSIS.md`.
- Module: arm64 Mach-O dylib, 100,762,840 bytes, SHA-256 `91efc5269d76feb9e6b5f31dc07bd4cbfe5720a238a84d1d6954d7a5617f2f9f`, macOS minimum 14.0, module/CPU ABI 3, CPU state size 3528 bytes.
- Module descriptor: game `RMGE01`, two executable ranges, 19 SMC ranges, 331 chunks, exact entry `0x8000403c`.
- Accepted performance module: O2 C output split at 1,024 instructions with indexed dispatch, 1,322 chunks, 93,207,368-byte arm64 dylib, SHA-256 `80411bfa49266f23c44657f03e79d53f6ed1b660a406c0a0b1b051e3f08f97d1`, macOS 14.0, the same ABI/state/entry/code/SMC metadata, zero unknown instructions, and distinct cache suffix `7f703e89efc28f0b`. The normal scripted build is byte-identical to the measured candidate; its matched Star Festival route improves graphics/DMA cadence by 6.94%/6.97% over the prior linear module without fallback or failed SMC handling.
- Reproducible 55-second headless smoke: `native=116469500`, `fallback=0`, `native_exc=36485`, `hook_fb=7680158`, `smc_failed=0`, `verifications=374`, `reverify_events=82`.
- Metal smoke: `native=436246556`, `fallback=0`, `smc_failed=0`; clean Cubeb shutdown.
- G5 title/file-select run: 5,231 frames with `projection_hash=0x4ba25c5f93433d51`, 4 final-snapshot draws, 12 primitives, 177 BP loads, 28 CP loads, 68 XF loads, 74 textures created, 42 textures alive, 26 vertex shaders, and 55 pixel shaders. Dispatch ended with `native=905716466`, `fallback=0`, `native_exc=319665`, `hook_fb=37791256`, and `smc_failed=0`.
- Instrumented package rerun: 8,313 frames, active IR ending at `(655,529)`, nonzero Cubeb signal, and `native=1556836850`, `fallback=0`, `native_exc=568797`, `hook_fb=58473126`, `smc_failed=0`. See `PERF.md` for bounded I/O counters and limitations.
- Executed guest-address range coverage is not yet scene-mapped. Zero runtime fallback in these boot smokes does not prove later gameplay paths.
- HOME-menu replacement: bounded semantic/native plan recorded in `HOME-MENU-ADAPTER.md`; implementation remains a later shell goal.
- Mobile compatibility: the module itself contains no runtime compiler step and has a macOS 14.0 load target; Simulator/device execution remains unproven.

Petari is semantic guidance only for this input. Its pinned `RMGK01` DOL hash does not match the `RMGE01` DOL.
