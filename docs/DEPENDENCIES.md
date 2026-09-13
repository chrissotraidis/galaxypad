# Dependencies

## Maintained source graph

GalaxyPad remains the Apple app. A fork is a maintained copy of an upstream
dependency: runtime and compiler changes are committed there so reviewers can
inspect their history directly. Upstream names, author history and notices stay
intact; [credits](../CREDITS.md) identify the original projects and contributors.

| Checkout | Maintained fork | Original upstream |
| --- | --- | --- |
| `ref/ModernGekko` | [chrissotraidis/ModernGekko](https://github.com/chrissotraidis/ModernGekko) | [ExpansionPak/ModernGekko](https://github.com/ExpansionPak/ModernGekko) |
| `ref/ModernGekko/vendor/dolphin` | [chrissotraidis/RecompCore](https://github.com/chrissotraidis/RecompCore) | [ExpansionPak/RecompCore](https://github.com/ExpansionPak/RecompCore) |
| `ref/ModernGekko/vendor/dolphin/DolRecomp` | [chrissotraidis/DolRecomp](https://github.com/chrissotraidis/DolRecomp) | [ExpansionPak/DolRecomp](https://github.com/ExpansionPak/DolRecomp) |

The app pins ModernGekko, ModernGekko pins RecompCore, and RecompCore pins DolRecomp
and its other third-party dependencies. Git submodule references select exact
commits. The [dependency lock](../config/dependencies.lock.json) records the chosen
revisions and upstream bases; it is the current inventory, rather than the dated
patch notes below. SunPad, ModernGekko-Template and Petari remain pinned reference
sources and do not need forks without changes of their own.

The [migration record](../config/dependency-migration.json) maps the former patch
files to fork commits, records their source revisions and hashes, and identifies
the deliberate submodule and Simulator configuration changes. The original
upstream commits remain in each fork's ancestry; their README, license texts and
contributor files are preserved. This record describes source migration, not a new
binary release or gameplay result.

Bootstrap modes:

```sh
# Required Apple dependencies for runtime/app builds.
bash scripts/bootstrap-dependencies.sh

# Only ModernGekko, RecompCore and DolRecomp for the source test suite.
bash scripts/bootstrap-dependencies.sh --sources-only

# Also prepare pinned, unmodified SunPad, Petari and template research references.
bash scripts/bootstrap-dependencies.sh --references
```

`--sources-only` prepares the three fork repositories with their full histories,
but not the third-party libraries required to compile the runtime. The default
mode adds the selected Apple build dependencies, including cubeb's nested
dependencies; it does not download unrelated platform packages such as Qt or
prebuilt FFmpeg. These commands download dependencies, never game data.
Dependency updates must keep the submodule references and lock in agreement.
Local edits must be reviewed and committed to the appropriate fork; bootstrap must
not discard them or apply a second hidden production patch stack. Supported build
configuration belongs in the fork too. Optional experiments remain explicit and
must not silently alter normal builds or release defaults.

For a dependency change, first commit and validate the change in its owning fork,
then update each parent submodule reference up to GalaxyPad and its lock. Run the
complete source suite from the resulting checkout. Follow
[CONTRIBUTING](../CONTRIBUTING.md) for behavioral regressions, performance evidence,
private checks and release provenance. A commit migration is not a fresh device
test or proof that a historical binary can be reproduced.

## Historical patch-stack notes

The entries below describe earlier checkouts and releases. Their patch paths,
hashes and commands are historical evidence, not instructions for the maintained
fork graph. Historical Preview 1 packages retain their original source supplements
and known reproduction limits. For the code review and ARM64 fallback evidence,
see [Upstream integration review](UPSTREAM-REVIEW.md).

### September 7 opt-in decoder line policy (R279)

Dependency revisions unchanged. ModernGekko0021-dcbz-loop-policy.patch SHA256
ef5ce417866cd67f6fd314f8585a6ea7716e50bcf824a044c4b8d4020c3c0e3b is pinned
in bootstrap, including peel/recovery/scope checks. Two bootstrap passes succeed.
Only GALAXYPAD_DCBZ_LOOP=1 enables rmge01-dcbz-loop-8-v1 for the exact supported
RMGE01/C/1024 input. Enabled identity is appended before cache lookup; disabled
identity preserves the existing cache key. Manifest records dcbz_policy. Source
hash/count guards precede replacing eight decoder zero loops. No runtime/app
promotion follows from this integration; see current STATUS for build state.

### September 6 decoder policy integration (R173–R174)

Pins are unchanged. Bootstrap now applies ModernGekko `0015-rmge01-fprf-policy.patch` (SHA-256 `881996463a31728375b651b5cdf96f165f5a087ccc5c85d94851fc4a21421488`) and Dolphin `0014-deferred-fprf-helpers.patch` (`661f2a2452e2240018140fedae6baaeea3b5c3e723d9266e3644f42581d1d019`). The former includes `<regex>`; the earlier draft hash is superseded. Repeated bootstrap passes, including overlay peel/restore and scope checks.

Policy `rmge01-fprf-119-v1` is limited to the accepted RMGE01 DOL, C backend and 1024-instruction chunks, with exact generated decoder SHA/count guards. The policy is part of cache identity and manifest; runtime source fingerprint includes the appended four helper bodies. Applied source is not packaged acceptance: canonical tool/module rebuild and artifact smoke remain required. The current normal app is still the pre-policy accepted package.

### September 4 dependency baseline

| Component | Source | Selected revision/version | License | Purpose/state |
|---|---|---|---|---|
| SunPad reviewed baseline | `https://github.com/chrissotraidis/sunpad.git` | `efd42ca45457af5950e0558c66703cb766959e11` | GPL-3.0 | Apple reference; separate reviewed checkout reproduced |
| SunPad supplied checkout | same | `fcdc1411e483a86ca80ec82e7cd53839c51ff865` | GPL-3.0 | clean, newer local reference; preserved unmodified |
| ModernGekko | `https://github.com/ExpansionPak/ModernGekko.git` | `0514d9f03f8602809f66fc92fdca87d30e752997` | GPL-3.0 | initial SunPad-known runtime track |
| RecompCore/Dolphin vendor | `https://github.com/ExpansionPak/RecompCore.git` | `13e492094902644b0d113c586300d358640f9e19` | mixed Dolphin-derived/GPL | runtime core pinned by the selected graph |
| ModernGekko-Template | `https://github.com/ExpansionPak/ModernGekko-Template.git` | `1ee85bb5e09c38f493a09f5fa6e9dc8228b23e42` | no license declared in reviewed metadata | pipeline reference |
| DolRecomp | `https://github.com/ExpansionPak/DolRecomp.git` | `fa0cf619e8d7eb8cba7eaf55267a12caaebb46aa` | GPL-3.0 | initial C-backend recompiler |
| Petari | `https://github.com/SMGCommunity/Petari.git` | `845164b4faec4703002eb99b4b75ee1788204230` | repository-specific; inspect before use | semantic/source-map reference only |
| Wiimms ISO Tools | `https://wit.wiimm.de/download/wit-v3.05a-r8638-mac.tar.gz` | 3.05a r8638 | GPL-2.0-or-later | read-only Wii image inspection/extraction |

WIT archive SHA-256: `670fd1920eb0390ecdc2553942df71f0ced43c63c8e83588a23705b569d25213`.

The downloaded WIT archive is the official macOS universal release. On macOS 26.6.2 its arm64 slice exits without output, while `arch -x86_64 .../wit` works under Rosetta; all current evidence therefore records the architecture explicitly.

Host versions: CMake 4.4.0, Ninja 1.13.2, Git 2.36.1, Python 3.14.6, Xcode 26.6. The portable C backend is selected and proven; LLVM is not required for the current module.

GalaxyPad adds one narrow ModernGekko overlay after the reviewed Apple patch: `patches/ModernGekko/0002-headless-no-shader-wait.patch`, SHA-256 `60d60d41d792c426f428fc3aaf2fce57962d870cefb181cee7fba90846948ce0`. It prevents a Null-renderer headless boot from entering the shader-progress ImGui path, which has no UI context. Bootstrap peels/reapplies this top patch only to preserve exact idempotency checks for the lower reviewed patch.

The root also applies `patches/ModernGekko/0003-runner-graphics-diagnostics.patch`, SHA-256 `db85b6f6eceab1e3f0d9663f04f0dc5fc5745993d6ee546242865c1fc06978f0`. It exposes the existing final graphics snapshot from the command-line runner and is included in the exact patch-scope audit.

Bounded G5 I/O evidence is provided by `patches/ModernGekko/0004-runner-io-diagnostics.patch` (`69a455e348f79246519a511944b8ed691660d3eea5fae0fd42dfdf7aacfdd79d`) plus Dolphin overlays `0002-galaxypad-runtime-diagnostics.patch` (`17b48cebc5eb1e5f372dda98d0885705bb47d2329ce84ccfa1b809104b118dd0`) and `0003-galaxypad-diagnostics-header.patch` (`e4498014739c15a102ce0e86729f69d7b06e4b1c97fb3ba8a93b47f3bc1757af`). Bootstrap hash-pins and scope-checks all three.

`patches/ModernGekko/0005-headless-explicit-audio.patch`, SHA-256 `ca5b3908ecc2312cf04a0295274d8a3155d0f7013b17dd947f9616ffa7a73ef7`, preserves Null audio as the headless default but honors an explicitly requested valid backend. This enables Cubeb/FIFO diagnostics with Null rendering without changing visible or packaged runtime defaults.

`patches/ModernGekko/0006-runner-cadence-diagnostics.patch`, SHA-256 `73dbe799b0d878edba640ffced0bcb9a0d1451427719371e2d7761c3001d57eb`, adds privacy-bounded active-span and gap-bucket telemetry for frames, audio callbacks, and DMA enqueues. It retains no raw callback history, audio samples, input history, or game memory.

`patches/ModernGekko/0007-rmge01-staticrecomp-idle.patch`, SHA-256 `f432d83b07ffbb11a66d3ef4da10ff7d8a01718099def9a3cb6b3578a55d53d7`, configures StaticRecomp's existing core-timing idle skipper for RMGE01's audited scheduler wait at `0x804AB358`. The match requires both disc ID and the accepted DOL SHA-256; every other title and revision explicitly receives idle PC zero.

`patches/ModernGekko/0008-module-cache-codegen-options.patch`, SHA-256 `03de37c00dee2d4920be17b9489834556c86676606a6b8ce85c3f8da7a714845`, makes the C chunk size and dispatch lookup mode explicit `moderngekko-port` options, folds both into the cache identity and manifest, and invokes DolRecomp with controlled values. This prevents non-default generated C from colliding with the default artifact. GalaxyPad requests 1,024-instruction chunks and indexed dispatch explicitly; the latter supersedes the earlier linear `fd7022cf46adb6b9` artifact after a matched active-gameplay improvement.

`patches/ModernGekko-dolphin/0004-apple-staticrecomp-audio-reserve.patch`, SHA-256 `984481b78034018c67ed2f0ed79c8b86833045a159f47ab924c17af483bffbfe`, enables the reviewed ±2% StaticRecomp DMA queue servo on Apple platforms and targets 80% of the configured reserve. With the 200 ms G5 setting this retains roughly 160 ms against the measured 156.6 ms producer gap without enlarging the queue.

`patches/ModernGekko-dolphin/0005-indexed-module-tables.patch`, SHA-256 `6afff9e65b5ef0664e8a71e11d359f8abb772c806f6b35a96765630c577810c8`, teaches the module-template coverage generator to derive code ranges from DolRecomp's indexed-dispatch run tables. It rejects missing or mismatched boundary arrays, and its output is byte-identical to linear dispatch for the exact RMGE01 input.
