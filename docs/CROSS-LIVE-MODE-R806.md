# R806: live mode mismatch found; bounded NI support passes local gates

## Build and bounded Simulator observation

Continued session5301 to exit0. Private module platform IOSSIMULATOR/min16 and
code signature verify. Module SHA5d0796bbd5fab91429acfc30bd02878db54b159ab76a620cc46db93907410c64;
unchanged control still exactly matches normal3acdcddc...1bac0. A process sample
attempt found the linker had just exited; re-polling the same handle confirmed
successful completion, not a build restart.

Booted only M5 iPad DE8E956F-6B29-4FF3-AF4A-77034CE8588A. Installed app binary
matches private R791 native-movie host SHA85ffc100...dbcc; no install needed.
Launch43849/PID46206 explicitly selects the private module via Simulator-only
arguments. GameData.bin copied to candidate directory before launch. Module-load
log confirms the intended path. Title then file-select visibly rendered; one
leased A+B input advanced the title. Screenshots cross-r806-title.png and
cross-r806-select.png record scene scope. No gameplay-level eligibility claimed.

2,544 counter observations end at10,420,224 calls, all mode-rejected, zero fast,
range or tie outcomes. Window delta10,416,128 likewise100% mode-rejected.
generated/cross-eligibility-r806-final.json and cross-runtime-r806.log record
the evidence. This candidate cannot help those observed menu scenes.

A bounded one-shot LLDB observation at cross_island_try entry, session92764exit0,
reads CPUState FPSCR at offset660:0x86004004, followed by MSR0x0000a032.
FPSCR NI=1, RN=0. Debugger detached and resumed the process. This is an actual
sample, not an assumption from platform defaults; it does not establish every
scene's mode. See generated/cross-mode-r806.log.

Stopped via simctl terminate and shut down the Simulator,41212exit0; console
43849exit0. No clean native-stop callback claim. No Simulator remains booted.
Save hash remains99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f,
matching backup and prelaunch. No save restore/overwrite needed. Normal module
selection/app remain unchanged.

## Source candidate corrected for bounded NI inputs

The magnitude/precision guard already excludes nonzero subnormal intermediates:
binary32 operands have magnitudes [2^-30,2^31), their products/differences remain
well within normal binary32 range (or exact zero). On that bounded path, NI's
subnormal handling need not force rejection. Removed NI from the mode guard;
other RN modes still use original code, and original input/tie guards remain.
No global NI setting is changed and no arbitrary subnormal case bypasses helpers.

Standalone25357exit0:262,144 complete-state/FPSR comparisons,48,258 fast paths
and256 tie fallbacks across RN/NI. Previous counts were24,129/128 with NI disabled.
False-return preservation checks remain. Expanded full-context workload driver
explicitly sets NI before host control update and each call.

Full-context8994exit0:12,000 callback/alias cases,7,680 suffix/RN/NI/unavailable
cases, and512 workload/NI cases pass. NI-enabled ordinary workload mean44.574
versus35.992ns/call, about19% less local CPU time; small-input work also benefits.
Rejection/tie overhead remains. Existing profile mismatch warnings retained;
these timings are not Simulator FPS. Logs cross-ni-r806.log/.err and
cross-ni-context-r806.log/.err. New helper SHA:
2186c80040d479474785b8c193e494f068b6e518cc37dc7dc5882048ab0fbd4d.

## Next

R804 diagnostic binary contains the OLD NI-rejecting helper and must not be reused
to judge the new path. Prepare a distinct NI-capable diagnostic, reusing the now
verified unchanged control/objects with identity checks. Update source-hash and
counter-injection guards explicitly; the old builder is pinned and should reject
changed input. Measure actual mode/range/tie mix before an uninstrumented scene
A/B or promotion. Full original PRD/SunPad/audio/stability/device gates remain.
