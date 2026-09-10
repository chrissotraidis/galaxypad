# R821: source-matched macOS module and isolated live runtime

Previous turn was progress: a bounded macOS CPU Profiler workload produced usable
per-PC weights, whereas Simulator attach and ordinary raw-task access failed.
This turn audits the real macOS inputs and starts one isolated game runtime.

## Verified inputs and limits

- Runner: generated/macos/direct-calls-r730/GalaxyPad.app/Contents/MacOS/GalaxyPadRunner,
  SHA256 871f4f8726cf1e12c56022a61dfbd013cbfa6614ce68ee6873982e869a9f4faf.
  This is the R730 host, not the R791 Simulator host. Do not equate host-loop cost.
- Module selected explicitly from the normal active-module marker:
  generated/modules-scale-r387/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-c4cbfba1bd04990b/gRMGE01_recomp.dylib,
  SHA256 c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939.
- Both module build descriptions point at the same RMGE01_generated tree and
  saved PGO file. Effective O2, ThinLTO, no-fast-math and fp-contract=off match.
  Target differences remain: macOS14 versus Simulator16/SDK26.5. These are not
  byte-identical binaries or proof of identical machine-code layout.
- Recomputed current ModuleSourceIdentity over all38 sorted helper/header/template/
  ABI inputs using the checked FNV1a procedure:3535c2dc0243bc7a, exactly the module
  manifest. PGO SHA256 f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d
  also matches its manifest. This helper-source identity does not hash generated
  game code; generated-source/build provenance is a separate check above.

## Isolated profile and current live handle

Fresh generated/runtime/plaza-profile-r821 contains copied desktop Config/config.ini
and a copy of the Simulator Wii directory, not the normal macOS save. Copied
GameData SHA99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f
matches the untouched original. Only this profile enables BackgroundInput.
Private Pipes/galaxypad FIFO uses the existing Pipe/0/galaxypad controller mapping.
No save-state copied: navigate the existing Mario file to the same starting plaza.

Launch has STATICRECOMP_NO_FALLBACK_JIT=1, GALAXYPAD_LC_BYTE_FAST=1 and
GALAXYPAD_LC_PAIR_FAST=1, explicit module/game/user-dir, Metal/Cubeb. Direct-call
binding is not enabled. Full command is retained in this turn's tool call.

Runtime session10913, PID55020 is LIVE. Do not restart it. At56seconds it was
running and log confirmed the exact module loaded at entry8000403C. Log:
generated/runtime/plaza-profile-r821/runtime.log. Native UI subsequently resolves
org.galaxypad.directcalls.diagnostic with window 'GalaxyPad — plaza CPU profile'.
Window title currently has an FPS counter, not a gameplay/performance acceptance.
No plaza screenshot or CPU capture yet. Initial UI timeout preceded initialization;
process evidence prevented an unnecessary restart.

## Continue this runtime

Use existing scripts/wii-pipe.py and this profile's FIFO for title A+B, existing
Mario file and story-page input. Confirm actual starting plaza visually, neutral
input, then attach CPU Profiler to PID55020 for a bounded10second recording.
Do not use profiler --launch (it kills launched targets at the limit). Export
cpu-profile, retain exact module load base/relative PCs, then clean native Quit.
One desktop game only; no Simulator device is booted. All original product
requirements remain active; this is a cross-platform code-cost hypothesis lane,
not mobile acceptance or a new FPS improvement claim.
