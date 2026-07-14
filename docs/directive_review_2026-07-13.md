<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Review — the FPS/MMO directive against the repo as it stands (2026-07-13)

Advisory document, prepared in a Cowork session the day before the directive's date. It follows
AGENTS.md and grades its own claims: **MEASURED** here means *demonstrated in this session, on this
host, and re-runnable*; **DECLARED** means *read from the repo's docs/ledger and not independently
re-verified here*; **SPECULATIVE** means *proposal or estimate*. Nothing in this file edits
`spec/D5-ledger.md` — grade changes are the Architecture Office's call, per the directive itself.

---

## 0. Incident report — the working tree was corrupted, and the gate was vacuously green

Found before any measurement, fixed before any baseline. **Grade: MEASURED** (every fact below is
re-checkable against `.git` objects; the damaged originals were backed up in the session sandbox —
temporary, but harmless to lose, since each is exactly reconstructible: `head -c <on-disk bytes>`
of the HEAD blob, plus 369 NULs for `persim.py`).

**What was found.** Twenty files on disk were damaged relative to HEAD (`f9b4713`). Nineteen were
**exact byte-prefixes** of their HEAD versions — pure tail truncation, no edits lost — and one
(`tools/intla/persim.py`) was HEAD content plus **369 trailing NUL bytes**:

| File | on disk / at HEAD (bytes) | Damage |
|---|---|---|
| `verify.py` | 98,728 / 139,528 | truncated — lost `main()` and `__main__` |
| `spec/D5-ledger.md` | 178,275 / 216,945 | truncated |
| `README.md` | 41,069 / 47,586 | truncated |
| `spec/D12-versions.md` | 23,126 / 27,674 | truncated |
| `docs/THEOREMS.md` | 10,058 / 14,494 | truncated (ended mid-word) |
| `tools/netcode/worldstep.py` | 12,336 / 15,463 | truncated |
| `spec/README.md` | 5,445 / 8,764 | truncated |
| `tools/netcode/README.md` | 5,231 / 6,707 | truncated |
| `docs/PAPER.md` | 23,175 / 24,439 | truncated |
| `tools/editor/README.md` | 18,076 / 19,252 | truncated |
| `spec/D13-glyph-probe.md` | 20,357 / 21,416 | truncated |
| `AGENTS.md` | 13,779 / 14,744 | truncated |
| `tools/editor/urdr_designer.html` | 81,225 / 81,941 | truncated |
| `tools/netcode/worldregion.py` | 9,890 / 10,609 | truncated (mid-`def`) |
| `tests/test_worldstep_contact.py` | 4,739 / 5,330 | truncated |
| `tools/netcode/conformance_world.txt` | 584 / 1,006 | truncated — **a pinned corpus** |
| `tools/frontend/canon_ref.py` | 5,727 / 5,944 | truncated |
| `docs/README.md` | 1,965 / 2,162 | truncated |
| `tools/frontend/svg_import.py` | 10,236 / 10,278 | truncated |
| `tools/intla/persim.py` | 6,329 / 5,960 | HEAD + 369 NUL bytes |

**The dangerous part.** The truncation of `verify.py` happened to end on a syntactically *valid*
line inside `frontend_contract()` (`conf = os.path.joi` parses as an attribute read). Everything
after it — including `main()` and the `if __name__` block — was gone. So `python verify.py`
**exited 0, printed nothing, and checked nothing.** A vacuously green gate: L5's failure mode, one
step worse — the gate did not merely fail to redden, it *affirmatively passed* while empty. The CI
workflow (`.github/workflows/verify.yml`) keys on the exit code of `python verify.py`, so a push in
this state would have badged green on both OSes. §3.1 proposes the guardrail this earns.

**Action taken.** All twenty files restored byte-for-byte from `git show HEAD:<path>` (no index
surgery). `tools/intla/persim.py` compiles after restoration. Two items deliberately left alone:

- `.gitignore` — differs from HEAD by three missing tail lines (`tools/editor/runA.json`,
  `runB.json`, `wB.json`) but is *not* a clean prefix, so it may be a real edit. Decide and commit
  deliberately.
- `.git` itself — the index has a null-sha1 cache entry and a stuck `index.lock` that cannot be
  removed through this mount. On the Windows side, with no git process running: delete
  `.git/index.lock`, then `git status` (git rebuilds the index from HEAD + working tree). The
  object store is intact — every restoration above came out of it.

**Probable cause.** Interrupted writes around Jul 11–12 (file mtimes), consistent with a cloud-sync
or crash event on a Desktop-synced folder — 19 clean tail truncations plus one NUL-padded tail is a
sync/flush signature, not an editor one. `does_not_show`: which process did it.

**Falsifier.** Re-run the scan: for each tracked file, `git show HEAD:$f | cmp -s - $f`; any
difference should be only `.gitignore` and files you have edited since.

---

## 1. OODA report: baseline (Observe)

**The gate, after repair — grade: MEASURED on this host.**

- `PYTHONHASHSEED=0 PYTHONUTF8=1 python3 -B verify.py` → **`GATE PASSED`**, exit 0.
- Run twice; outputs **bit-identical** (only the unittest wall-time line excluded).
- 412 unit falsifiers green in ~3.1s; 329 `[PASS]` stage rows across every stage in `main()`
  (examples ×2-determinism + goldens, oracle + defect, modules, math/render/physics/fp,
  the N1–N5 + D16 netcode stack, D14/D15/D17 + all seven detectors, spec-freeze, 45 rejection
  fixtures, tamper self-test).
- Host: Linux sandbox (Ubuntu 22.04, CPython 3.10.12), run from a byte-identical copy of the
  repaired tree on local disk. Matches the CI matrix's ubuntu/3.10 cell; it is *not* a new
  named-host admission unless you choose to record it.

**Non-vacuity of this baseline.** The same apparatus reddened loudly on the pre-repair tree
(2 FAIL + 24 ERROR in the unit stage; `spec_freeze` corpus-count failures; import errors naming the
truncated modules). The run that now passes is a run that *can* fail — it did, two hours ago.

**Not exercised here — grade: DECLARED (per D5, on named hosts).** The 13 Rust and 4 C99
placements: the checked-in `.exe` binaries are Windows artifacts and no rustc/gcc cross-check was
attempted in the sandbox. Cross-placement rows stay exactly where the ledger puts them.
Wall-clock performance: not a gate property, **NOT MEASURED** anywhere yet — see §2.

---

## 2. Orient — the directive against the measured floor

Lineage first, because the directive asks what "finished" looks like. **Dentatus** (the sealed
workbench: 2 frozen cores + 27 siblings + 5 apps, one gate, `integrity ≠ truth`) and **Ursprung**
(six arcs; 506-check suite; PO-1…PO-10 closed; a falsified-then-conditional hypothesis honestly
recorded on a sealed ruler; `BOUNDARY_MAP.md`; one *shipped* instrument at `v0.2.1-alpha`) define
the target shape: **a graded index, a consolidated boundary map, falsifications kept as results,
and at least one packaged artifact.** Urðr is visibly on that trajectory (D5 + THEOREMS + D12
freezes are the graded index; "Evidence Against C8" is a boundary map in embryo). The directive's
phase gates should be held to producing those same four artifacts — not slide-deck exit criteria.

Where each department's plan meets the repo (grades are the repo's, per D5/D11/D12; gap classes
mine):

| Directive track | Already real (grade) | Gap to the directive's Phase I–II |
|---|---|---|
| **Physics** | Exact dynamics, n-contact LCP, joints — frozen `urdr-physics 1.0`; rung-5 Q32.32 bounded steppers (`fp_dynamics`) MEASURED, cross-placed | Friction, rotation/shapes, sphere-sphere CCD are the *declared* next rungs (D11 §3.5) — the directive's M5 (CCD for 500-unit/ms movers) sits **two rungs above** the current frontier. Broadphase, SIMD, PGS-style iterative solving: **nonexistent — SPECULATIVE**. |
| **Netcode** | N1–N5 + N4.1 + D16 frozen at 0.1, MEASURED, **three placements agree including the failure modes**; canonical snapshots + rollback convergence (N2); field-level desync localization (`first_field_desync`) MEASURED | Prediction-*primary* loop, UDP transport, sub-tick timestamps, lag compensation, interest management: **SPECULATIVE** (design prose only; `docs/network_bridge.md` is the sketch). The <2KB/100-player snapshot budget is a number with no measurement behind it. |
| **Animation** | D9 Q32.32 ops (add/sub/mul/div/floor/sqrt) MEASURED, division-free, both placements | **The entire department is greenfield.** No quaternion type, no rsqrt (the directive's "Newton-Raphson, no sqrt in hot path" implies *new D9 ops* — a D12-versioned extension, not a tweak), no keyframes, no state machine, no IK. |
| **Rendering** | Fixed-point rasterizer, 3D depth, exact perspective — frozen `urdr-render 1.0`; **D15 view-export frozen: the renderer structurally cannot feed back** | Directive aligns with the roadmap's pixels-vs-state boundary. GPU/PBR/post work is by design non-authoritative and **not gate-able in this repo** (roadmap §4) — it is native-side engineering, graded by its own integration tests. |
| **Tools/editor** | Browser designer + deterministic replay (exploratory consumer); D14 front-end contract MEASURED — two independent canons reproduce the browser goldens; integer-snap refusals in place | FBX/GLTF rigs, timeline, state-graph editor: **SPECULATIVE**. The directive's "editor stays SPECULATIVE, outputs MEASURED" is exactly D14/D15 as already enforced — keep that sentence, it is the one place the directive and the ledger already coincide perfectly. |
| **QA/infra** | The gate *is* CI (two OSes × two Pythons); red-first + tamper self-test; desync localization to (tick, body, field) | Chaos/fuzz generation, perf-regression tracking, certificate automation: **nonexistent**. Fuzzing is the natural continuation of the C8-falsification program the README already commits to — see §3.4. |

**Contract frictions the directive should resolve before Phase I** (each small now, expensive
later):

1. **Grading vocabulary drift.** The directive's grade table (one ladder + "who decides") is not
   the repo's two-axis `maturity × evidence` system, and its proposed use of `SCOPED` for
   "deterministic algorithm, nondeterministically invoked" recycles an existing *maturity* word as
   a *prediction semantics* — the same ladder-conflation LESSONS warns about. The distinction it
   wants is real (predicted-input ticks are exact math on guessed inputs) but belongs in the
   *evidence scope*, e.g. `MEASURED (on predicted input; converges to the N1 chain on arrival)` —
   which is precisely what the N2 rollback rows already say. No new grade needed.
2. **The async one-tick-late digest** changes the witness contract of frozen versions. D12's law:
   extend via a versioned successor (`URDRLST2` or a pipeline flag inside a new version), never
   mutate an admitted digest's semantics. The directive's own grading of the realtime path is
   honest — hold onto it.
3. **Tiered certification at scale** ("digest-only ≥500 bodies = DECLARED") understates itself:
   digest agreement across independent placements *is* MEASURED evidence — a weaker *mechanism*
   than exact re-solve, not a lower grade. Record the mechanism per tier; don't blur it into the
   grade word.
4. **One-tick-late IK** is fine *only* as a witnessed contract (reads tick T−1 collision state,
   writes tick T transforms, lag visible in the witness). That is a spec rung with red-first
   falsifiers, not an implementation detail.
5. **The ten "ambitious designs."** The load-bearing subset — verifiable replay, permanent
   tournament archives, patch auditing — rests on properties that are already measured (content
   identity, witness chains, replay determinism) and needs only packaging. The chain/NFT/token
   layers import external trust systems this discipline cannot gate; keep them permanently outside
   authority claims, whatever the business does.
6. **Every performance number in the directive is currently unfalsifiable.** 4ms ping, 240Hz,
   <3ms tick, <0.5ms broadphase, <2KB snapshots — the repo has no timing harness, and roadmap §4
   is explicit that real-time performance is *not gate-able here*. Until a bench protocol exists
   (named host, native placement, sealed ruler), these are aspirations, not budgets. Ursprung's
   own history is the warning: the M3 promotion gate passed on a self-scored metric and the strong
   claim was later **falsified on a neutral ruler** (M6b/c). Define the ruler before the numbers.

---

## 3. Decide — a first OODA cycle that is small, red-first, and earned by today

1. **Gate self-integrity guardrail** (earned by §0; cheapest, do first).
   (a) CI asserts the literal `GATE PASSED` tail line, not exit code alone.
   (b) `report()` refuses to pass below a pinned row-count floor (the gate red-tests its own
   completeness, not just its checks).
   Red-first proof: truncate a scratch copy of `verify.py` exactly as found today → CI/gate must
   fail loudly. Today's incident is the falsifier that already fired.
2. **Repair the repo state on Windows.** Delete the stale `.git/index.lock` (no git running), let
   `git status` rebuild, confirm the tree is clean except `.gitignore` (and commit that choice
   explicitly). Consider `git fsck` for peace of mind — every object needed today was intact.
3. **Physics M1 pre-work — define the ruler before optimizing** (Observe before Act). Write the
   bench protocol: named host, native placement, equal-budget comparison, sealed metric (the
   Ursprung lesson in §2.6). Only then do broadphase/SIMD numbers mean anything.
4. **Fuzz stage prototype** (directive QA-M5, promoted to *first*, not last). Seeded random scene
   generator → `fp_dynamics` + N4.1 tick; assert REFUSE-totality (overflow refuses, never wraps),
   bounded iteration, and ×2 determinism per seed; wire as a gate stage with a deliberate-defect
   self-test. This is the C8-falsification program the README already commits to, aimed at the
   directive's adversarial-input worry.
5. **Animation rung 0** — Q32.32 quaternion prototype by the D9 method (Python proto → property
   falsifiers → division-free ops → corpus → cross-place later). The directive's Animation M1
   without the deadline theater.

Everything else in the directive's Phase I stays behind these five. `No report, no milestone
closure` cuts both ways: none of the directive's Q3-2026 milestones has an Observe baseline yet,
so none of them can honestly open, let alone close.

---

## 4. Act — what this session changed

Twenty files restored byte-for-byte to HEAD content (§0 table); nothing else in the tree touched;
no spec or ledger edited; damaged originals preserved; the gate run twice green with bit-identical
output on the repaired tree (§1). This document added at `docs/directive_review_2026-07-13.md`.

---

## 5. This review's own claims, graded

| Claim | Grade | Falsifier / boundary |
|---|---|---|
| 20 files were exact-prefix-or-NUL-padded corruptions of HEAD | MEASURED | `git show HEAD:$f \| cmp - $f` per file; backups retained |
| Truncated `verify.py` exited 0 silently (vacuous green) | MEASURED | reproduce: `head -c 98728` of HEAD's verify.py → run it |
| Gate green ×2, bit-identical, 412 + 329 rows, this host | MEASURED | re-run; `does_not_show`: named-host claims, Rust/C99 placements, any perf property |
| Rust/C99 cross-placement status | DECLARED | taken from D5/AGENTS; not re-run here (Windows `.exe`, no compilers attempted) |
| Directive perf budgets currently unfalsifiable | MEASURED (absence) | show me a timing harness in-tree and this row dies |
| §3's five-step cycle is the right order | SPECULATIVE | it is a proposal; the OODA reports it produces are its test |
| Corruption cause = interrupted sync/flush | SPECULATIVE | mtime + signature circumstantial; no process identified |

---

## Addendum (2026-07-13, later the same session) — the cause was found, and §0 needs reframing

While extending the gate, the same truncation signature reproduced **live, in a
file grown seconds earlier**: the Cowork session's sandbox mount serves reads of
files changed *outside the session* clipped (or NUL-padded) to a **stale cached
size**. Everything in §0 reconciles under this single mechanism:

- the 19 "truncations" were files the Jul-12 commits had **grown** natively; the
  mount clipped each read at its previously-cached (smaller) size;
- `persim.py`'s "369 trailing NULs" was the reverse: a stale **larger** cached size
  (a pre-commit draft) padding a smaller native file;
- `.gitignore`'s "possible edit" was a stale pre-edit size — the user's 3 added
  lines were real and native; nothing was ever ambiguous on disk;
- the owner's Windows-side evidence (clean `git status --porcelain`, `git fsck`
  clean, `GATE PASSED` with digests bit-identical to the sandbox run) is exactly
  what a **never-damaged** working tree looks like.

**Corrected claims.** "The working tree was corrupted" → downgraded: the *session's
view* of the working tree was corrupted; the disk was in all likelihood never
damaged, and the §0 restorations were byte-level no-ops that refreshed the stale
cache (MEASURED for every file the owner's gate run exercised; the WIP-loss risk
flagged for `persim.py` is correspondingly withdrawn to negligible). The
"interrupted sync/flush" speculation is **retired** in favor of a mechanism that
was directly observed (MEASURED: a file grown via the session's file API
immediately re-read 40,800 bytes short through the session's shell mount, tail cut
mid-string at the exact pre-edit byte length).

**What does NOT change.** The vacuous-green hazard was demonstrated end-to-end and
is layer-independent: a truncated `verify.py` — wherever the truncation lives —
parses, runs nothing, and exits 0. The §3.1 guardrail (row floor + tamper-row
presence + CI grep of the literal tail line) is now implemented, and its red-first
falsifier (`tests/test_gate_guard.py`) caught a stale-mount artifact in the wild on
its first day. `exit-0 ≠ ran` was never about the disk.

**Operational rule for future sessions in this repo.** Trust the file-tool layer
and the owner's native runs; treat shell-mount reads of files modified outside or
grown inside the session as suspect; verify any suspicious truncation against
`git show HEAD:<file>` (the object store's content-addressing survives every cache
layer — L1 doing its job).
