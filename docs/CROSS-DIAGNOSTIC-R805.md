# R805: control identity verified; exact diagnostic source passes state test

R804 made progress by starting the private build and testing counter parsing.
Continued the SAME exec5301. The unchanged control relink completed and exactly
matches the normal Simulator module:
3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0.
provenance.json contains both baseline/control hashes and object identities.

The script then compiled the one diagnostic chunk successfully and started
linking its private candidate. Last observed candidate linker PID45352,parent
45351, elapsed4m48s at~637%CPU. Session5301 remains live; no restart. Final link,
platform/signature verification and candidate hash are not yet available.

## Instrumentation verified independently

Extended tests/test-cross-island-vector.py with --diagnostic-source to extract
and test the exact emitted helper/counters from the candidate source, rather
than a separately reconstructed instrumented helper. It includes cross_report
after each attempted region, exercising real logging when the threshold fires.

Run41402exit0:262,144 complete CPUState/FPSR cases pass, including24,129 fast
paths and128 tie rejections. False-return state/status checks remain enabled.
64 counter summaries are emitted. The actual summarizer accepts their totals
and monotonicity. Its resulting fraction is from the SYNTHETIC rounding/input
test distribution, NOT gameplay and must not guide promotion.

Diagnostic source SHA:
531e5f05f9fc4b1788ec89a970abb97b49b28a6c6025c32e1aaeb3215a04443c

Evidence: generated/cross-diagnostic-test-r805.log/.err (stderr contains expected
counter reports, not an empty-error-file claim). The C test uses ASan/UBSan;
this macOS helper test is not Simulator execution of the complete module.

## Continuation

Poll SAME5301 for the private link/check result. Inspect final provenance/hash
and keep the normal module selected. Then launch only the existing M5 iPad
Simulator for a bounded eligibility observation, with save protection and
visible scene confirmation. No app installation, Simulator boot or gameplay
measurement occurred this turn.

Existing Simulator GameData.bin was rehashed at its recorded A90E3BBD container:
99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f,
unchanged from R791. Development input supports short leased snapshots through
GalaxyPadDevInputFile; stale R791 input is expired. Revalidate paths/state before
launch. Normal app/module/save unchanged; full original PRD remains active.
