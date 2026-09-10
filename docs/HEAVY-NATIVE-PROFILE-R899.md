# R899: invaded-plaza instruction capture completed

R898 made evidence-analysis progress, not a speed improvement. This turn executes
its missing heavy-scene profile. No product binary or module is changed.

## Identity and execution

Existing host generated/candidates/thread-work-native-r888/candidate/GalaxyPad.app:
runner SHA256 2cf50e8a47399981a78dbc134e41ae23c89ed5987fd5347cceaab86294f014dc.
Explicit native module c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939
from generated/modules-scale-r387, unchanged source/profile used in R822.
Trace binary UUID6AF26467-764C-3048-8B17-878BC714B679 matches dwarfdump;
trace load base0x131d70000 and module path match the selected file.

Fresh generated/runtime/heavy-native-r899 copies only R837 Config/Wii/config.ini;
independent Pipe configured. Metal/Cubeb, background input explicit, no mods,
fallback JIT disabled, LC byte/pair0, existing VI/thread recorders enabled.
This uses original native movie decoding, not the private iPad THP replacement.
R822 used LC byte/pair1 and an older host; do not treat relative profile changes
as a controlled scene-only/platform-only experiment.

PID12287/session63375 navigated the existing Mario file through story and movie.
CUA screenshots before/after profiling show invaded plaza, same Mario position
near its entrance, life3/lives4/coins0/StarBits8. Images are in the conversation
tool record, not saved local PNGs. R897 iPad had StarBits4 and a different precise
view; these are the same scene class, not a pixel-identical workload fixture.
All Pipe helpers finished with released buttons/neutral stick. Input fixture
files are retained in the profile directory. Camera-relative route needed
corrections around terrain and a lamp/Toad; not a deterministic accepted route.

`xcrun xctrace record --template 'CPU Profiler' --attach 12287 --time-limit 10s --output generated/runtime/heavy-native-r899/cpu.trace --no-prompt`

Capture22058 exits0. TOC33318 and cpu-profile export98842 exit0. Summary uses
scripts/summarize-cpu-profile.py with --binary gRMGE01_recomp.dylib and
--thread-prefix 'CPU thread '. No profiler --launch or target killing at limit.

## Instruction evidence

27,445 CPU samples,24,057,933,218 cycle-weight units;27,237 observations on P cores.
Run3,658samples/3,315,256,421units; dispatch1,131/1,031,307,084;
largest generated chunk804B60A0 is834/743,593,643. These are exclusive sampled
symbol weights, not exact removable costs.

Extended existing map-plaza-instructions.py with optional --profile; original
default and exact module-SHA check stay unchanged. The new summary maps all577
sampled chunks to exact baseline disassembly, with count/weight/origin conservation.
Mapper17063 exit0; instruction-classifier and load-origin regressions pass.
No new profiling framework or compiler/runtime change.

| Family within generated chunks | Cycle-weight units |
| --- | ---: |
| Loads | 8,613,986,511 |
| Stores | 1,511,409,986 |
| Integer/other | 5,210,252,042 |
| Branch | 384,011,577 |
| FP move/conversion | 580,852,491 |
| Scalar FP | 119,587,322 |
| Calls | 4,955,702 |
| Total | 16,425,055,631 |

Loads account for about52.44% of generated weights versus R823's51.6%.
6,937,000,446 load weights remain unresolved by the conservative local-origin
recognizer; exact adjacent lazy-FP global571,014,965, stack494,100,578,
branch-table324,143,251, journal-global287,727,271. Inlined work remains inside
chunks; out-of-line helper weights are outside this family table. Sampling skid,
unrecognized SIMD, and load provenance prevent interpreting these as latency,
dynamic instruction counts, or guaranteed eliminable state traffic.

Artifacts: generated/runtime/heavy-native-r899/{cpu.trace,cpu.xml,toc.xml,
summary.json,runtime.log,vi.csv,work.csv}; generated/plaza-instructions-r899/
{report.json,context.asm}. Raw per-PC weights remain available for code selection.

## Separate timing window and caveat

First capture-process-work attempt rejected the relative launch path before
measurement. Retry62445 checked the exact executable and completed. Its window
600724926025083–600754934415041 has complete paired counters and zero drops:
1653 guaranteed VI intervals,151.887M CPU-thread instructions/VI,44.642M cycles/VI,
16.843ms CPU/VI,96.21% P-core CPU-time share; retained tail40.029s.

This window had no live profiler, but overlapped XML analysis/offline disassembly.
It is NOT a clean performance comparison or an optimization result. Do not use
the near60 title-counter screenshots to claim sustained60. Do not subtract it
from R897's different platform/view/config to infer a Simulator penalty. It does
show why raw instruction work and precise scene identity must accompany timing.
No redundant retry was made solely to obtain a cleaner baseline number.

## Cleanup and decision

Exact-PID SIGTERM invoked RequestStop; session63375 exits0. Both recorders export
successfully, smc_failed0. Shutdown native11,502,449,382/fallback165,852,510: fallback
is nonzero interpreter work despite JIT disabled. Whole-run473underruns/57backlog
drops span navigation/original movie/profiling, not fixed-window audio acceptance.
Save SHA99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f
is unchanged. All helpers/profiler/map sessions terminal; no game or Simulator.

Heavy-scene instruction attribution is now available. It reinforces broad
generated-code/state/memory work, rather than exposing one new dominant movie
decoder routine during gameplay. Next use this exact disassembly to select a
shared lowering/data-lifetime mechanism with meaningful workload coverage and
explicit observer/entry/exception semantics. Require actual-policy differential
and cost evidence, then matched iPad gameplay A/B. Do not repeat another profile,
small guarded-memory/normalization/restore variant, QoS guess or depth-wait removal
without new causal evidence. Full PRD/SunPad/audio/story/device/release gates
remain active; this turn provides attribution, not an FPS improvement.
