# R822: successful source-matched macOS plaza CPU capture

Continued R821's existing PID55020/session10913 without restarting. Pipe input
selected the copied Mario file and advanced story pages. Short taps did not
consistently advance every page; one-second A pulses with screenshot verification
completed navigation. Final input neutral, Mario at the same starting plaza with
life3, coins0, StarBits0. CUA screenshots before/after profiling show the scene
unchanged apart from normal animation. These images are in the conversation tool
record, not new local PNG files. No movement/route-completion claim.

CPU Profiler attached to55020 for10seconds, session32426 exit0. CPU export19470
exit0. Artifacts in generated/runtime/plaza-profile-r821:

- cpu-r822.trace (23MiB), cpu-r822.xml, summary-r822.json
- runtime.log and bounded title/play/story/advance diagnostic input fixtures

The summary selects CPU thread leaves:25,462 observations, cycle-weight sum
22,315,669,485. Run3,233samples/2,923,783,979cycles; chassis_dispatch1,033/
936,749,090; largest chunk804B60A0726/659,841,358. Do not equate weights with
removable work or counts with exact instruction latency. Per-PC offsets and cycle
weights are retained, unlike the R813 collapsed sample.

Trace module path is exactly the R821 selected macOS module, load base0x136c20000.
Trace UUID6AF26467-764C-3048-8B17-878BC714B679 matches dwarfdump on that module.
Its SHA and helper-source/PGO provenance are recorded in MAC-PROFILE-PROVENANCE-R821.md.
Mac host/platform differences from Simulator remain; no mobile timing inference.

Native Cmd-Q closed the game. The following UI-state call timed out because the
window disappeared, but authoritative session10913 exited0 and PID is absent.
Shutdown records smc_failed0, native4,118,451,064, fallback69,702,002. The run was
configured with fallback JIT disabled; these are nonzero interpreter fallback
steps, not proof of pure-native execution. Copied GameData remains SHA99d432...64f.
Whole-run graphics/audio totals span title/story/plaza/profiling; they do not
establish fixed-window60Hz, audibility, continuity or a new performance gain.
No profiler, game or Simulator device remains active.

## Next action

Join weighted leaf PCs to the exact module disassembly, across sampled chunks.
Classify observed instruction families without guessing state-object provenance
from a load/store mnemonic alone. Separate entry/dispatch, helper calls, arithmetic
and potential state traffic with explicit recognized patterns and an unmatched
bucket. Prior tiny helper/dispatch/FPRF/cross-product lanes remain closed absent
a materially different broad mechanism. No rebuild is needed to analyze this
capture. Full original PRD, SunPad, performance/audio/stability/progression/device
requirements remain active and uncompleted.
