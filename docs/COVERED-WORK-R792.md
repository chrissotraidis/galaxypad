# R792: execution-frequency ranking across two retained hot chunks

Previous turn made progress: R791 established matched movie audio delivery and
continuing gameplay starvation. No game or Simulator was running at entry.

Extended tests/probe-chunk-coverage.py to select another exact generated chunk.
The second chunk exposed two measurement bugs: outlined helpers can duplicate
labels outside the selected function, and entries with dead PC assignments can
begin with comments. The probe now restricts labels to the selected function and
queries its first executable statement. Comments are not missing-count evidence.
The ranker verifies the source SHA and excludes outlined-loop internal execution.

Final coverage builds69192/38353 exit0, accepted only the expected newer-object
timestamp warning. No code executed, module rebuilt or app selected. Exact source
and retained profile hashes are recorded in the JSON artifacts.

| Chunk | Known entry attempts | Leading instruction families |
| --- | ---: | --- |
|804B60A0|1,034,646,642|psq_l155,669,813; psq_st133,152,042; lfs105,709,489|
|805170A0|1,583,700,587|lwz595,113,765; stw512,594,769; blr211,834,380|

First chunk has no unmapped entries after the comment-location fix. Second has
one outlined loop excluded; its internal repetitions are not counted. These are
historical training entry attempts, not current scene CPU costs or completed
instructions. Exceptions can terminate entries. Helpers have conditional paths.

Register saves80517538/3C/40 each have104,545,529 attempts; corresponding restores
80517584/88/8C each104,545,523. This qualifies them as frequent paths, but does not
make another three-load specialization a material whole-game optimization.
R451 already found that changing its CFG lost PGO application; the old chunk
profile represented only about2.5% of CPU leaves. R311 broader callback-bounded
mapping cache regressed, and R452/453 page-table designs lacked repeatable gain.
Those are different rejection reasons; the restore prototype itself was not
demonstrated slower. Keep the distinction when selecting work.

Artifacts:
- generated/chunk-coverage-r792-fp.json
- generated/covered-instructions-r792-fp-final.json
- generated/chunk-coverage-r792c.json
- generated/covered-instructions-r792-stack-final.json

Commands: run tests/probe-chunk-coverage.py with default or --chunk805170A0
(separate option/value), then scripts/rank-covered-instructions.py on its JSON.
Earlier r792/r792b outputs precede the comment-location fix and are superseded.
R784's selected hot arithmetic counts remain; its one unknown entry is now mapped.

Next: enumerate the concrete writers and callback boundaries of RAM/EXRAM base
and size in the selected host/runtime. Determine whether stable mapping can be
represented once per execution interval without new checks on every access.
Existing per-access snapshot/page-table and three-load variants remain closed.
Require a substantive shared-work reduction and representative cost evidence
before another module build. R791 movie replay is not needed. Original PRD,
SunPad controls/menu, stability and physical-device completion remain open.
