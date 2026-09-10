# R903: paired-merge record semantics and observer checkpoint

R902 made private lowering progress, not a product performance gain. This turn
extends that same resident-value path to record forms. No app/module/Simulator
or runtime configuration changes.

Decoder now accepts both Rc states for all four merge opcodes. AotRecordCR1
copies FPSCR FX/FEX/VX/OX into packed CR1, preserving all other CR fields and
integer scratch registers. It emits integer loads/extraction/insertion/store;
no FP arithmetic or precision change. Reference PowerPC.h197 UpdateCR1 and
Interpreter_Paired.cpp73–120 define the inspected semantics. Guest availability,
instruction entry, PC and cycle handling remain outside this component.

The fixture now emits256 merges: four selectors,32 destinations, both record
states, aliases and spills. Decoder checks262144 valid register/selector/Rc
combinations, plus wrong-primary and wrong-XO rejections. Random initial CR/XER
and all16 FPSCR high-nibble patterns strengthen state preservation checks.

Added a full-state observer after non-record merges, before recorded merges.
Cache flushes before the ordinary C checkpoint and reloads afterward. This
specifically catches an unwanted CR write that later recorded merges could hide
from final-state-only comparison. The original earlier mutation callback remains.

Executed python3 tests/probe-arm64-fpr-cache.py with --paired-merges plus
--exact-conversion, --paired-merges alone, and unchanged --exact-conversion.
Initial63181exit0; final checkpoint/three-mode sequence55537exit0. Each final
mode passes100000 full CPUState/FPSR/FPCR cases; checkpoint invoked exactly once
per paired-merge case. All final stderr files empty. C++ driver uses ASan/UBSan;
emitted assembly does not. No independent NZCV/full-AAPCS or whole-guest-entry
proof is claimed. Local emitter buffer doubled to32KiB for the larger fixture;
this is offline data storage, not executable allocation.

Evidence: generated/arm64-paired-record-checkpoint-r903,
arm64-paired-record-plain-r903, arm64-fpr-regression-r903 (.json/.err).
JSON retains emitted assembly and reference/cache-adapter identities. Existing
harness cleans its temporary compiler directories. Vendor files are unchanged.

Next add explicit guest entry/availability/PC/cycle contracts to the offline
path, then broader arithmetic with resident values and complete-routine cost
comparison. Do not use this merge fixture as a game-speed benchmark or as proof
of a completed alternate backend. Original PRD/SunPad/gameplay/audio/stability/
device/package gates remain active and incomplete; no new FPS improvement.
