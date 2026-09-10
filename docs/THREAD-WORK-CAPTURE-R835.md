# R835: analysis implemented; first game capture fails coverage

Previous turn progress: private host ready. This turn adds strict sidecar
analysis and tests, then actually runs the private host in one iPad Simulator.
No speed or CPU-core attribution result is accepted from the incomplete capture.

`scripts/summarize-thread-work.py` checks exact retained VI/sidecar pairing,
per-level topology, configuration/errors, query brackets, counter resets and
complete requested-window coverage. Raw Mach ticks convert using recorded
numerator/denominator. Results retain query uncertainty, selected boundary
omissions, drop metadata and numeric core levels. Invalid interior queries are
validated before boundary trimming, never silently excluded by corrupt timestamps.
tests/test-thread-work-summary.py passes positive/negative cases; registered in
check-repository.sh. Full repository suite not run during game measurement.

## Live attempt

Artifacts: generated/runtime/thread-work-r835. Private24002e50 app installed;
unchanged module3acdcddd, THPoff/LC0/QoSexperimentoff/fallback JIT disabled.
Both recorder paths set to this directory. Boot64944 completes; console63085,
PID62865. Runtime command in process-work.json; app identity verified live.
Host sysctl: level0 Performance, level1 Efficiency, hw.nperflevels2.

CUA initially retained an outdated menu tree; Escape did not dismiss it. After
reconnection, exposed Cancel action recovered the actual window tree; fresh
Rotate19 produced landscape title. This delay consumed recording capacity.
Do not reuse pre-reconnect AX indices. Title/file/play inputs complete96434,
33268,84127; finish58267. Pre/post screenshots show starting plaza life3/lives4/
coins0/StarBits0. No movement input. The earlier screenshot catches starting
camera/animation settling; capture has10s neutral warmup. Pointer lease47393
completes; process capture3090 completes its requested30s window.

Requested first-before567498776637791, last-after567528786018166.
Both recorders retain16384initial samples and drop1228later samples. Last retained
VI567527366866791 ends **1.419151375seconds before** the requested window end.
Both process-work and thread-work summaries correctly reject incomplete coverage,
even with verified-prefix-capacity16384. No shorter retroactive window substituted,
no drop header edited, and no frame/work/core-share claim made from this attempt.
The sidecar exports successfully with2levels, timebase125/3, config_error0; that
proves in-game collection/flush availability, not a complete measurement.

Menu Stop Game gives runtime failed=0 and both export_result1. Stopped app
terminated, original85ffc100 app reinstalled, Simulator shut down (87054 exit0).
Reinstallation relocates containers: restored app now under Bundle/Application/
280E043F-4E9F-4872-ABAC-D5A9A1A1E4C0; data under Data/Application/
043D40C4-845F-4F26-9B4B-031ABB5F3F89. Old data-path absence was container relocation,
not deletion; exact GameData found in the new container and rehashed.

## Next

Use same ready private host, no rebuild. Fresh runtime directory and live-resolved
containers; protect current save. Simulator connection now has working fresh-tree
and Cancel recovery. Navigate promptly after verified title, use existing bounded
story/finish fixtures, and take same30s plaza capture before capacity fills. The
lost1.419s was avoidable startup/UI delay, not grounds for loosening coverage.
Restore original app/save identity and shut down after collection. Preserve full
original performance/PRD/SunPad/gameplay/audio/stability/device scope.
