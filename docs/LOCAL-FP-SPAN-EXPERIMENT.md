# R776: local floating-point state across a pure instruction span

## R777 correction: explicit scalar lanes do not remove the regression

The follow-up `--scalar-span` expands30 fixed-register wrapper/write calls,
uses23 named scalar lane variables and a four-byte FPSCR object, and retains
only status/value helpers. No register array or memcpy remains in the batch.
Value parameters are evaluated once before destination writes; member names
are excluded from parameter substitution. The source guard caught an initial
`ps1` parameter/member-name collision before candidate compilation; corrected
lexical substitution and reran. This is a bounded source transform, not a C parser.

Final51437exit0, generated/scalar-fp-span-r777c.log:22,528 full-transform CPU,
RAM and host-flag comparisons pass, including all44entry points and unavailable
FPU. Actual-policy release comparison: reference~2745–2746instructions/call,
candidate~2949, with baseline190.2–199.4ns versus candidate206.0–206.8ns.
Candidate still reports missing PGO. Not new sanitizer or installed-game proof.

This nearly matches the array variant's instruction cost. **Retract array-copy
overhead as the working explanation**: it was plausible, not established, and
explicit scalar representation did not remove the excess work. Both batching
variants fail the cost gate. Do not continue representation/attribute variants
or claim generic register-local lowering is the demonstrated next solution.

This tests state lifetime, not the rejected per-helper vectorization or blanket
inlining policies. `tests/probe-transform-inline.py --local-span` uses the
complete current1024-instruction chunk and actual macOS build flags, as in R769.
Only the19-instruction span804B62B0–804B62F8 gets a guarded batch entry. Original
labels/instructions remain for every interior entry and unavailable-FPU path.

The script rejects changed span shape, downcount writes, unexpected CPU fields
and control flow. It follows the actual float-helper call graph and verifies
its CPU fields are limited to fpr/ps1/fpscr. The local struct contains those
fields only. It copies incoming lanes, executes unchanged strict arithmetic,
then writes ten destination registers and FPSCR back. No memory instruction or
callback occurs inside the selected span; surrounding memory and entry/cycle
logic remain original. This is a pinned prototype, not a general emitter.

## Executed result: do not promote

Final25795exit0, generated/local-fp-span-r776b.log.22,528 full-transform
CPU/RAM/host-flag comparisons pass across44entries, RN/NI, finite/special/raw
values and varied status. Pattern63 additionally disables MSR.FP; all FP entries
must raise, while the final blr entry still returns normally. This release
whole-chunk run is not a fresh sanitizer run or memory-callback/fault oracle.

Two warmed ABBA sequences show baseline~2743–2750instructions per transform
versus~2948–2951candidate: about7% more work. CPU timing drifts considerably
(baseline220.7–258.6ns, candidate231.0–289.5ns); each adjacent comparison is
slower, but do not infer a precise game-speed percentage. The first run4144
also showed increased instruction work. Retain both logs, not only faster samples.

Actual PGO flags were used, but the new candidate code reports missing profile
data; existing unprofiled integer and one stale CPU-function warnings remain.
This is not matched newly trained PGO or installed-game evidence. It supplies no
material-benefit case for a full module build. State-copy/batch-boundary overhead
is a plausible explanation, not individually measured attribution.

Reject this copy-in/copy-out implementation. A future register-lifetime design
must use explicit live-value/dataflow lowering, not assume a local register-array
copy becomes free. No further attribute tuning, product selection or complete
module rebuild is authorized by these results. Original PRD remains unchanged.
