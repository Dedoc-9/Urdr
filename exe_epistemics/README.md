<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# `exe_epistemics/` — arc home: the predictive READ, and the lineage it closes

This folder is the home of the **executable-epistemics arc** in Urðr — the predictive READ pass in which
every epistemic state is an executable artifact, not a prose claim ([`./PREDICTIONS.md`](./PREDICTIONS.md)).
It also records the **verified lineage** this arc closes, because — read in birth order — `executable-epistemics`
is not an outside tool Urðr borrowed. It is the **root** of the family Urðr descends from, and the predictive
READ is Urðr re-converging with its own great-grandparent.

DESIGN + LINEAGE + REVIEW. No mechanism is built by this file. The lineage below was checked against the
sources this session (four repositories cloned and read, git history included); every edge is graded, carries a
`does_not_show` boundary, and names a falsifier. What was verified against source is stated as verified; what was
read only in one repo's description of another is stated as such. The boundary is at the end.

---

## 1. The reference instrument (repo 1) and its current files

**`executable-epistemics`** — <https://github.com/Dedoc-9/executable-epistemics> — AGPL-3.0-or-later,
version 2.0.0, author Daniel J. Dillberg. Read at HEAD `2026-06-13`. It bills itself as
*"reference instrument: mcl-observer-runtime v2, witness-core architecture."* Three layers, each surviving the
failure of the layer above it: `witness_core/` (claim-boundary governance), `mcl_runtime/` (a deterministic
observer-comparison instrument), `studies/` (registered experiments EXP-000 … EXP-102).

Current source, by layer (links to the live tree):

- Layer 0 — witness_core: [`artifact.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/witness_core/artifact.py) ·
  [`registry.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/witness_core/registry.py) ·
  [`provenance.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/witness_core/provenance.py) ·
  [`errata.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/witness_core/errata.py)
- Layer 1 — mcl_runtime: [`kernel.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/mcl_runtime/kernel.py) ·
  [`runtime.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/mcl_runtime/runtime.py) ·
  [`tools.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/mcl_runtime/tools.py)
- Layer 2 — validity + studies: [`validity_framework/scorer.py`](https://github.com/Dedoc-9/executable-epistemics/blob/main/validity_framework/scorer.py) ·
  [`studies/REGISTRY.json`](https://github.com/Dedoc-9/executable-epistemics/blob/main/studies/REGISTRY.json) ·
  [`studies/errata/ERRATA.json`](https://github.com/Dedoc-9/executable-epistemics/blob/main/studies/errata/ERRATA.json)
- Contract + protocol: [`docs/HANDOFF.md`](https://github.com/Dedoc-9/executable-epistemics/blob/main/docs/HANDOFF.md) ·
  [`docs/CLAIM_CLASSES.md`](https://github.com/Dedoc-9/executable-epistemics/blob/main/docs/CLAIM_CLASSES.md) ·
  [`docs/WITNESS_PROTOCOL.md`](https://github.com/Dedoc-9/executable-epistemics/blob/main/docs/WITNESS_PROTOCOL.md)

`MANIFEST.json` is a stale index — 7 of its 48 fingerprints no longer match the tree (see §4), so treat the live
files above as ground truth, not the manifest.

---

## 2. The lineage — one conservation principle, four projections

Read in the order requested (1→2→3→4), the four repositories are the **birth order**, confirmed by first-commit
dates. All four are AGPL-3.0, single author. Each is a projection of **one** invariant onto a different domain.

| # | repo | first commit | last | commits | domain projected onto |
|---|------|-------------|------|--------:|-----------------------|
| 1 | executable-epistemics (= MCL_OBS2) | 2026-06-11 | 2026-06-13 | 237 | the **audit core** |
| 2 | Dentatus / chronicle (*manius curius*) | 2026-06-13 | 2026-06-19 | 220 | the **determinism backend** |
| 3 | Ursprung | 2026-06-19 | 2026-07-05 | 462 | **rendering** |
| 4 | Urðr | 2026-07-18 | (live) | 154+ | the **terrain gate** |

**The invariant.** Dentatus's `GENEALOGY.md:12` names it at its most general — *"The field allocates attention.
The field does not allocate truth"* — and states that `integrity ≠ truth` is *"merely its special case for the
audit core."* This is the single conservation principle. Urðr's own `ANCESTRY.md` already found that Urðr and
Ursprung's `tre/` are *"two projections of a single conservation principle"*; this file widens the aperture: there
are **four** projections, and the principle is named at the root (Dentatus) and mechanized at the audit core
(executable-epistemics). The `≠`-spine (`integrity ≠ truth`, `declared ≠ verified`, `claim ≠ code`,
`signum ≠ rēs`, `attestation ≠ authority`) is that one distinction wearing a different hat in each repo.

The four projections, each grounded in source:

- **1 · audit** — `witness_core` mechanizes it directly: every `Artifact` carries `validity_scope` +
  `forbidden_interpretations`, the only permitted `claim_class` is `observer_agreement_only`, and
  *"chain hashes certify integrity, never truth"* (`docs/HANDOFF.md:64`). A verdict-shaped key raises
  `WitnessViolation`.
- **2 · determinism backend** — chronicle makes *"the committed hash trajectory the only thing allowed to be
  'true'; everything downstream is allowed only to decide where attention goes"* (`GENEALOGY.md:44`). Observers
  leave the state hash bit-identical; the AetherPulse kernel refuses floats.
- **3 · rendering** — the renderer is *"an attention engine for finite triangles"* (`GENEALOGY.md:41`): it may
  spend budget on an already-visible object, but may not reveal a hidden one. Enforced by CORE/VIEW/ALLOCATOR/
  OBSERVER (`ursprung/registry.py:8-30`, only CORE moves committed state) and graded by `claim_ledger.py`
  (`ESTABLISHED / MEASURED / UNDERDETERMINED / SPECULATIVE / NOT_MEASURED`). `tre/` supplies the boundary
  discipline (*Signum nōn est rēs*).
- **4 · terrain gate** — Urðr projects it onto a byte-identical gate: `declared ≠ verified`, `claim ≠ code`,
  red-first `plants_bite` falsifiers, provenance records that must name a live enforcing row. This repo.

### The edges (coupling type differs on each — this is the sharp part)

**1 ⇄ 2 — shared discipline module (`MCL_OBS2`), not a code import.** Dentatus's development arc is literally
*"Dentatus → MCL_OBS2 → chronicle"* (`docs/LESSONS.md:1`): MCL_OBS2 is the middle stage, the observability
discipline that *"forced an honest accounting of what was real versus narrated"* (`docs/LESSONS.md:13`), after
which *"chronicle is the distillate."* Dentatus's archived game layer imports MCL_OBS2 as an on-disk sibling
(`docs/archive/game/agency/loop.py:30` `_MCL = …/MCL_OBS2`) and emits *"an executable-epistemics Witness
Artifact"* (`loop.py:41`), naming the *"sibling executable-epistemics toolkit (witness_core)"* (`agency/__init__.py:3`).
`ANNEX_I` describes MCL_OBS2's witness_core as the exact five-field Artifact + chain-hash-integrity-never-truth +
`observer_agreement_only` contract that `executable-epistemics` implements. The experiment numbering is one
program: exec-epistemics runs EXP-0xx…2xx and its final commit is the *"Series 200→300 bridge; EXP-301 genesis
reference"*; Dentatus's genesis is *"EXP-301 Series 300 genesis."*
- Grade: **MEASURED** (both repos' sources name the relation).
- `does_not_show`: not byte-proven identical — Dentatus references MCL_OBS2 as an external sibling directory and
  vendors no copy, so "executable-epistemics *is* the published MCL_OBS2" is established by description
  (`ANNEX_I` matches the five-field contract exactly), not by a diff.
- Falsifier: exec-epistemics's witness_core contract diverging from `ANNEX_I`'s MCL_OBS2 description, or the
  absence of the Series-200→300 bridge commit.

**2 → 3 — hard runtime import (read-only consumer).** Ursprung consumes the sealed Reality_Engine
(= Chronicle/Dentatus) through a single seam, `ursprung/_workbench.py`: env var `URSPRUNG_WORKBENCH`, default
`~/Desktop/Reality_Engine` (`:32-35`), `sys.path.insert` + `import kernel/snapshot/fixedpoint` from `AetherPulse/`
(`:58-64`), fail-closed `RuntimeError` if no `AetherPulse/` is found (`:38-50`). `ursprung/__init__.py:3` calls
itself a *"read-only consumer of the sealed Reality_Engine (Chronicle/Dentatus)."*
- Grade: **MEASURED** (import seam read directly).
- `does_not_show`: doesn't show Ursprung couldn't run against a different kernel implementing the same API; the
  module itself flags that "read-only" is *"a convenience boundary, not an enforced one"* (`_workbench.py:24-26`).
- Falsifier: Ursprung importing AetherPulse with no Reality_Engine mounted (it raises — confirmed).

**3 → 4 — discipline only, zero shared code.** Grepped both directions: `opcost`, `URDR`, `terrain/` appear
nowhere in Ursprung; `Ursprung`, `Dentatus`, `tre/` appear in Urðr only in prose (`ANCESTRY.md`, `AGENTS.md`),
never in a module or import. Urðr's `ANCESTRY.md:4` states it *"imports no code from Dentatus/Chronicle or
Ursprung; what it imports is the discipline"*; `AGENTS.md:37` names the claim-inheritance discipline as
*"inherited from the Ursprung `tre/` boundary work, its sibling."* Urðr re-implements the claim-grade ladder, the
CORE/VIEW/ALLOCATOR/OBSERVER split, and the boundary discipline from scratch in the terrain domain.
- Grade: **MEASURED** (bidirectional grep; zero shared symbol).
- `does_not_show`: doesn't show Urðr's mechanisms are novel — they re-instantiate Ursprung's patterns; and it
  does not re-earn Ursprung's measured results (those grades are **routed**, per `ANCESTRY.md:94-96`).
- Falsifier: any shared module or import between the two trees.

**Chronology as a whole**: `2026-06-11 < 06-13 < 06-19 < 07-18`, with Ursprung's milestone-1 commit landing
~1 hour after Dentatus's final commit the same day.
- Grade: **MEASURED** (git first-commit dates).
- `does_not_show`: date order is not by itself derivation order; it is load-bearing here only because each edge
  above carries independent coupling evidence pointing the same way.

---

## 3. One lineage insight worth stating: the gate matured by being applied to itself

The family's central discipline — *the gate must bite* — grows monotonically stricter across the birth order:

- **1** exec-epistemics: `ExperimentRegistry.verify()`, the precommitment-audit method, is **untested and
  inverted** — it hashes over a different field-set than it checks, so it can never return `True` (executed
  proof in §4). It shipped green because nothing calls it.
- **2** Dentatus: `integration/preflight_check.py` runs 36/36 suites with *"PARITY HOLDS"* — a byte-identical
  replay assertion, exercised.
- **3** Ursprung: `DVSM/verify.py` is a LIVE gate — each supported claim is tied to a suite that passed *this
  run*, fails closed on import/receipt errors, prints `GATE PASSED`.
- **4** Urðr: `verify.py` must print `GATE PASSED` **twice byte-identical**, and every module ships a red-first
  `plants_bite` self-test plus provenance records that must name a live enforcing row.

The root's own audit method being the *least*-exercised, and the youngest repo's gate being the most
self-biting, is the discipline discovering itself over four generations. Graded **DESIGN** (a synthesis reading of
the four gates, not a mechanized claim); the exec-epistemics half is **MEASURED** (executed below).

---

## 4. Review of repo 1 (read code, not prose) — findings, executed

Full findings were produced this session by reading and *running* the source. Summary, most-load-bearing first:

- **`registry.verify()` is inverted — can never return `True`.** `register()` hashes the entry *including*
  `status`/`results_hash`; `verify()` recomputes *excluding* them. Verified against both stored entries: the
  register-domain recompute reproduces the stored hashes (`bf53c3a6…`, `bfb43597…`), the verify-domain recompute
  does not (`83a60961…`, `cafed69a…`). No caller, no test round-trips it. One-line fix: hash `register()` over the
  same reduced domain `verify()` checks.
- **`MANIFEST.json` drift** — 7/48 fingerprints stale; all 7 are exactly the files the errata record as edited
  (the five E-011 locale fixes, `ERRATA.json`'s own growth, `WITNESS_PROTOCOL.md`). Nothing regenerates or checks
  the manifest — a checksum index with no live checker behind it.
- **Errata hash placeholders** — 12 of 24 errata hashes match `ErrataLog.record()`'s writer; 12 match nothing any
  writer produces (hand-appended).
- **Firewall is key-shaped, not value-shaped** — the verdict-firewall blocks `{"valid": …}` (a verdict *key*) but
  not `{"classification": "DETECTED"}` (a verdict *value* under a clean key, which `scorer.py` legally emits).
- **Genuinely strong**: the single-truth `kernel.py` (structurally forbids redefinition), `scorer.py`'s frozen
  seeded null + E-004/E-007 dual-baseline, and above all `ERRATA.json` — 29 recorded corrections, most of them
  honest self-refutations (E-009 a self-misclassification, E-010 a small-n degeneracy found by an "impossible"
  test, E-011 a cross-platform determinism violation). A ledger that records falsification is the rarest thing in
  this genre, and this one does.

Every gap found is an *un-run* check — the same lesson Urðr's own gate mechanizes.

---

## 5. The arc in Urðr

[`./PREDICTIONS.md`](./PREDICTIONS.md) is the executable-epistemics ledger: every epistemic state a machine can
turn red, moving through `UNKNOWN → PREDICTED → PREREGISTERED → READ → OBSERVED → SURPRISE → …`, each transition
carrying an executable witness. **P1** for `opcost` is frozen at `PREREGISTERED` (a git commit dated before
`opcost.py` is read). The stages above `OBSERVED` — residual families, a compression engine, law competition, a
discrimination search — are **DEFERRED**, each with an executable earning condition, because building an audit
method over data that does not yet exist reproduces exactly repo 1's `verify()` failure (§4). Two gates are open
(structured observation; the first computed residual); the rest earn their existence from the deltas.

---

## 6. Boundary — what this document does NOT establish

- It does **not** byte-prove `executable-epistemics ≡ MCL_OBS2`; that edge is MEASURED by both repos' descriptions
  (`ANNEX_I`'s five-field contract matches), not by a diff of a vendored copy (there is none).
- It does **not** re-earn any Ursprung or Dentatus measured result; grades routed from their ledgers are labelled
  routed, never earned here. `built ≠ adopted`.
- It does **not** claim the four repos share code except on the one edge that does (2→3, the AetherPulse import);
  1⇄2 is a shared discipline module named across sources, 3→4 is discipline-only.
- The four-repo lineage does **not** capture repo 1's own pre-history — `executable-epistemics` is "v2.0.0", a
  rebuild whose EXP-000 witnesses a `mcl-observer-runtime v1` that predates 2026-06-11 and is not one of these
  four repos.
- License note: repo 1 is AGPL-3.0-**or-later**; repos 2–4 are AGPL-3.0-**only**. Single author throughout.

Cross-link: [`../ANCESTRY.md`](../ANCESTRY.md) carries the 3→4 (Ursprung↔Urðr) projection-pair in depth; this
file widens the same principle to all four.
