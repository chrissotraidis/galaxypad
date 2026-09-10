# R909–R910 — positive whole-routine screen, private Simulator build

R909 implemented the R908 plan in
`patches/experiments/normalization-vector.inc`, using local paired/scalar values,
not the rejected scalar emitter or scratch CPUState. Entry6BE0 alone tries the
whole9-op region; original suffixes remain. The original estimate/25-bit scalar
rounding are retained. Inputs are guarded exact singles; unsupported values,
norms and halfway cases reject before guest writes and restore speculative
FPSR. The initial upper madd still executes for rounding/status effects.

## Executed checks

- Initial45446 exited0:261120 full17-op normalization-routine CPUState/memory/
  callback/FPSR comparisons,69120 callback cases,456 accepted candidates.
  `generated/normalization-vector-r909`.
- Expanded47050 exited0: same matrix with randomized raw inputs/FPSCR and
  direct-entry fixtures;1804 accepted calls. Ordinary3/4/0 normalization has
  independent near0.6/0.8/0 expected checks. Zero norms and deliberate halfway
  fixtures explicitly require rejection. `normalization-vector-fixtures-r910`.
- These are actual independent whole-chunk libraries with module flags. They
  are not exhaustive floating-point proof, sanitizer coverage, or device tests.
  PGO warnings are retained; training applicability is not falsely equated.

## Complete-routine cost

Initial35195 and varied61669 exited0. Final15255 (modes-r910) includes correctness
before timing and8 alternating pairs per workload. Mean ns/routine:

| Input | NI off control/candidate | NI on control/candidate |
|---|---:|---:|
| Ordinary existing fixture |82.376 /48.808|86.168 /49.126|
|3/4/0, constants0.5/3 |83.335 /48.683|86.113 /48.528|
| Large, guard rejection |83.095 /97.250|85.467 /99.292|
| Zero norm, rejection |99.955 /106.225|104.975 /110.697|

Ordinary-input benefit is material (~40–44%), but rejection costs remain. This
is not a game FPS prediction: measured eligibility and clean scene comparison
are required. The benchmark retained full final CPUState/memory/FPSR equality.
No repeated app baseline or previous scalar candidate was rebuilt.

## Private build completed; real-scene gate in R911

`scripts/build-normalization-diagnostic.py` reuses the R804 byte-verified
unchanged Simulator control, verifies every1329 original object hash and current
compile/link fields, and compiles only the changed chunk from a passing fixture.
Its arithmetic body is unchanged; test configuration shim is removed, original
chunk visibility restored, and read-only fast/attempt counter getters retained.
Counters are diagnostic, not a production UI or timing acceptance claim.

Command:

```
python3 scripts/build-normalization-diagnostic.py --test generated/normalization-vector-modes-r910 --output generated/candidates/normalization-diagnostic-r910
```

Session34260 exited0 after verified control/objects and one explicit profile
mismatch warning. Candidate d966417b is IOSSIMULATOR min16/sdk26.5 and signature
verified; original baseline3acdcddd remains unchanged. Log
`generated/normalization-build-r910.log`; provenance and link command are inside
the candidate directory. R911 records actual iPad staging and runtime evidence.

Next use one Simulator to verify the real scene and candidate eligibility via
the retained counters, outside any timed window. If eligibility supports it,
measure clean matched gameplay CPU/VI/audio and visible scene behavior. Account
for diagnostic counter overhead; do not claim local40% as global improvement.

Installed app, normal module selection, disc/save and Simulator state are
unchanged.19GiB available before this build. Latest actual iPad results remain
37.15 VI/s heavy plaza and59.88 VI/s movie. Full original PRD remains active.
