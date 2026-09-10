# R788: load-range/type sharing cost screen, closed for promotion

Previous turn progress: general checked multiply failed useful cost screen.
Private cross-range-prefix.inc plus --cross-range probe binds two12-byte direct
input ranges for the actual six-instruction prefix804B6CB8–804B6CCC. Requires
FP, LSQE, type0 loads, NIclear and no pending guest exception; rejects address
wrap, undersized/null RAM and CPU-state overlap. No persistent mapping cache.
Original first-entry cycle charge occurs before interception. Original suffix,
memory stores, callback paths and all interior labels remain available.

Within proven inputs, four generated load operations share those range checks;
original bit conversions and state-write order remain. Source precision now
comes from these loads, so multiply checks only finiteness instead of four
integer precision round trips. This is not blanket no-alias or relaxed FP.

86334exit0, generated/cross-range-r788.log:7680full-routine CPU/RAM/hostflag
comparisons pass in the complete chunk under actual Ninja ThinLTO/PGO policy.
Original and candidate compile warnings retained, including a candidate function
profile mismatch. This integration corpus is release and primarily valid RAM;
it does not independently prove every guard/callback/alias boundary. Do not
promote on these tests. Earlier load-span alias tests are not this full oracle.

Eight alternating windows: reference43.271–44.051ns, candidate41.659–42.601ns;
about3.4% mean local improvement, instructions865→933. Still insufficient for
material whole-game expectation. Close this implementation without a module
build, broader emitter changes or further guard/attribute micro-tuning.
Square result remains separately scoped; no app FPS gain this turn.

Next prioritize an unmet delivery gate on the substantially faster private
native movie path: quantify remaining timing/audio evidence before normal-use
promotion. Do not repeat unchanged decoder throughput/pixel tests or opening
replays merely to recover already-established5591-frame completion. First inspect
retained native movie logs and determine the specific missing measurement.
Gameplay CPU deficit, XF stability fault and full original PRD remain open.
