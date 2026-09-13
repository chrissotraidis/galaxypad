# GalaxyPad release readiness

Updated 2026-09-13. **Public experimental preview available; stable release not accepted.**

See the [public-preview sanity check](PUBLIC-RELEASE-SANITY-2026-09-13.md) for
current repository, history and published-archive audit results.

The owner explicitly requested the current source on main and an experimental
IPA/macOS release. See [preview notes](PREVIEW-2026-09-13.md) for the current
artifact scope and validation. The historical full-product gates below remain
open and must not be read as a claim that this preview is stable or complete.

The latest [performance and hardware handoff](PERFORMANCE-2026-09-12.md) supersedes
the historical candidate identities below. CPU/render overlap and experimental
audio adaptation improved the fixed Simulator route, and the private iPad build
is installed. The dome Pull Star failure was reproduced and fixed in Simulator by restoring
real depth access; actual level entry passes. Physical acceptance remains pending.
The correct-depth heavy-scene baseline is 45–49 frame events/s. Earlier faster
results used disabled depth and do not establish playable-config acceptance. Remaining physical
slowdowns, Xbox Start retest, audio listening,
long-session behavior and iPhone performance prevent stable-release acceptance.

The remaining detailed audit below was recorded on September 9 (R851).
This is a preliminary evidence index, not a completed release audit. The full
[PRD](GALAXYPAD-PRD.md) remains authoritative. Its Section 12.5 references
D1–D11/rows1–35, but Section2 also requires D12 and the matrix includes row36;
both additional public-candidate gates remain required.

## Candidate identity

- Root HEAD: `289a87a1499c3d0da23c21c472fd16525742208a`.
  Most implementation is untracked/dirty; HEAD does **not** reproduce this build.
- Private Simulator host: `generated/candidates/product-r841/GalaxyPad.app`.
  Executable SHA-256:
  `67fc872a0c3f0256ef6ea6c30329881e12110cbe1c771374dfa94e4863531e2b`.
- Simulator game module SHA-256:
  `3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0`.
- These hashes identify two files, **not** a sealed package manifest or IPA.
  No physical-device artifact is accepted by this record.
- R852 private device staging (not install-signed or runtime-accepted):
  `generated/device-stage.yXz4N2/GalaxyPad.app`, executable SHA-256
  `b2665b801500cf83a8324839b040b8ce6e39f69dcc093b7b854c57fbb58c09b3`,
  embedded device module SHA-256
  `48f455ebc33f8eb2fc58151cd722ea756db77a5738a9573a0a49f0c656110041`.
  Current UI host rebuilt against existing device core/module; source/ABI parity
  with the Simulator core is not established merely by successful linkage.
- R853 supersedes R852 for the private device host after rebuilding226 core
  steps from current source and reprovisioning. Stage:
  `generated/device-stage.EI86W0/GalaxyPad.app`; host SHA-256
  `8824315d07b47cbd21c2821a6645c89e2376e9db4edb5bd02e787a7eb67b1c2e`.
  Core archive SHA-256
  `b1c9def7c0d270b2376de414bbad98793cd0448ca0ede9b309c6cd53e8deeeac`.
  Embedded module remains `48f455eb…6110041` above. No installation signature
  or runtime/ABI acceptance. Local signing inventory reports zero valid identities;
  latest device inventory reports none connected.
- R856 rebuild includes the R854/R855 editor fixes. Latest private device stage:
  `generated/device-stage.RvOFtT/GalaxyPad.app`, host SHA-256
  `23284c78b44b41395fbfdb46309a3152b4c200502c9675e6d121057d662806cf`.
  R853 core and device module unchanged. Simulator candidate executable is now
  `dae0296ec3a2be0ea5c765b222abe8758594de9e31ceb652280694a014584955`.
  These supersede older host hashes for current source; neither updated host has
  actual game-run acceptance. Staging and regression checks are not installation
  signatures, physical testing, or a complete source/package audit.
- Supported input is exact RMGE01 revision0 under
  [disc identity](DISC-IDENTITY.md) and `config/galaxypad-disc.json`.
  Complete package/dependency/source identity and module-match audit remain due.

## Product gates

No D requirement is promoted to complete by this report. Older evidence must be
reconciled against the exact proposed release, not inherited automatically.

| Requirement | Current evidence boundary / work still required |
| --- | --- |
| D1–D2 identity and reproducible AOT | Existing identity/build records; clean-clone end-to-end reproducibility and exact release audit remain due. |
| D3 macOS first play | Historical Grand Star/save/reload evidence exists; exact current packaged candidate with stable timing/audio is not accepted. |
| D4–D5 story and completion content | Complete story, mechanic and completion-content routes are not established by recent runs. |
| D6 timing/rendering/EFB | R849 phone gameplay fell to31–46 engine frame events/s; full rendering/pointer/cadence gates remain open. |
| D7 controls | SunPad-derived shell and tested editor exist; Direct Touch contexts, simultaneous physical touches and all non-motion mechanics remain open. |
| D8 audio/saves/services | iPhone new file persists and loads into plaza; full recovery/multiple-slot/corruption/audio/speaker matrix is not proven. |
| D9 Simulator first play | iPhone plaza/movement is verified, not the complete first-Grand-Star loop; both platform scopes still require full acceptance. |
| D10 Apple shell/branding | Menu/editor/icon improvements exist; remaining phone overlaps, import/privacy/lifecycle scope and branding matrix are open. |
| D11 stability/reproducibility | Brief lifecycle checks do not prove60-minute soak, repeated transitions, memory pressure or clean-clone reproduction. |
| D12 public candidate | Full platform acceptance remains incomplete; private experimental publication was explicitly authorized on September 13. |

Technical matrix rows1–36 are **not accepted for this release candidate** here.
This does not erase historical partial passes. Each row must receive a linked,
artifact-specific acceptance record before any complete/public claim.

## Release checklist

- [ ] Full source/dependency revisions and clean source snapshot.
- [ ] Exact Mac/app/IPA manifests, signatures, module and disc-match audit.
- [ ] D1–D12 and technical rows1–36 reconciled individually.
- [ ] Physical Mac, iPad and iPhone hands-on evidence for exact artifacts.
- [ ] Source/package audits and corresponding-source plan.
- [ ] Complete third-party notices and license/rights decisions.
- [ ] Original icon provenance, editable source and complete platform visual checks.
- [ ] No unresolved severity-1 progression/save/crash/privacy/package/rights issue.
- [ ] Separate explicit source, Mac binary and IPA/module distribution decisions.
- [ ] Chris's final authorization for the exact release action.

See [rights status](RIGHTS-STATUS.md), [current status](STATUS.md),
[performance](PERF.md), [save evidence](SAVE-AND-NAND.md), and
[branding provenance](../apple/branding/PROVENANCE.md).
Do not publish private screenshots, game data, saves or generated modules merely
because this report exists. The active goal remains the full PRD.
