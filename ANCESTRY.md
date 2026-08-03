<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# ANCESTRY — what Urðr inherited, and the sibling it rhymes with

Urðr imports **no code** from Dentatus/Chronicle or Ursprung; what it imports is the **discipline** those
projects paid for (LESSONS L5). This file records that lineage — and one thing the lineage made visible: Urðr
and the Ursprung `tre/` boundary work are **two projections of a single conservation principle** onto different
objects. It is **recorded history and synthesis**, not a claim of new measured results. It **routes** the
sibling's witnesses by grade and re-asserts none — the same routing discipline it describes. `declared ≠ verified`.

## Status / grade

DESIGN + LINEAGE. No mechanism is built here. Every Ursprung result named below is graded **in Ursprung's own
ledger** (`STATUS.md`) and inherited at that grade, never upgraded. What was checked *this session* against the
Ursprung source is stated as checked; what was not is stated as routed. See the boundary at the end.

## 1. The sibling — Ursprung's `tre/` (the Boundary Trilogy)

`tre/` answers one question: how to obtain a bit-perfect deterministic authority from a substrate that is
non-deterministic — *without pretending the substrate is deterministic*. Its three contracts (`spec_limes`,
`spec_vestigium`, `spec_constans`) plus the cross-cutting `spec_ordo` are governed by one law — **Signum nōn est
rēs**, the sign is not the thing. Checked against the Ursprung source this session: every mechanism `tre/` calls
built-and-measured maps to a MEASURED row with a falsifiable witness in `STATUS.md`, and every design-bridge /
unbuilt item it marks (the DVS/AER substrate, vector clocks, a keyed `digest→MAC`) maps to a DESIGN-BRIDGE /
NOT-BUILT row. `tre/` overclaims nothing against its own ledger — which is the routing discipline in action.

## 2. One principle, two projections

The two projects are **not the same law**, and calling them so would be the inflation both exist to refuse. They
are one meta-principle landing on two different objects:

- **Urðr — epistemic containment.** A claim may not carry stronger certainty than its evidence justifies. It
  governs how certainty *propagates*. *How much certainty may this claim inherit?* (L57: enforcement ≤ the
  guarantee the evidence class admits; the claim-class registry enforces it.)
- **`tre/` — representational containment.** A claim may not exist on the wrong side of a boundary. It governs
  where certainty *originates*. *Where may this claim legitimately come into existence?* (Determinism begins on
  the digital side of the *līmes* and never crosses back.)

One asks *how much*, the other *where*. Both forbid the same thing:

> **Nothing may become truer, more deterministic, or more authoritative merely because it crossed a boundary.**

That sentence is a **unifying explanation, not a mechanized law** — too abstract to falsify, and by this
project's own rank-minimality (L58) a principle that changes no single decision earns no gate. It explains why
the individual laws exist; it is not one of them.

## 3. One-way authority transfer — and its Urðr dual

The conceptual center of `tre/` is that authority flows in exactly one direction —

    rēs  →  līmes (admission)  →  deterministic authority  →  record  →  verification

— and nothing below the boundary ever reaches back up. The record never authenticates reality; the invariant
never authenticates the trajectory; the View never reaches the Model. Grounded, not asserted: `weltkern`'s P3
membrane makes `SimExport` a **compile-time read-only** window and `CommandSink` the **single write door** (the
borrow checker forbids a tick while a sink is live) — one-way transfer enforced by the typestate, the witness
`membrane_fidelity.rs`; and `DVSM/verify.py` reads **12/12, GATE PASSED** in a clean checkout here.

Urðr forbids the same pathology from the other side. One-way transfer is an **anti-circularity** discipline: if
authority could flow back — the record certifying the reality that produced it — the witness would certify its
own cause, which is precisely **a checker that cannot fail** (L23) and the **neutral-ruler** rule (a verifier
must not read what it is scored against). `tre/` forbids it by *flow direction*; Urðr forbids it by *verifier
independence*. Relate, do not equate: one pathology, two guards.

## 4. The correspondences (routed, exact)

| Ursprung `tre/` | Urðr |
|---|---|
| *Signum nōn est rēs* — the sign is not the thing | *integrity is not truth* (L11, generalized in L56/L57) |
| `declared ≠ verified` | `declared ≠ verified` — the same words in both trees |
| references the witnesses, re-asserts none | enforcement ≤ justification; a relation inherits its enforcer's guarantee, no stronger (L57; the claim-class registry) |
| gate the invariant, not the fragile trajectory (*cōnstāns*) | derive the live theorem, seal the snapshot as history (the proof-lattice pin) |
| the vector-clock bridge is *recorded-not-debt*, summoned the day a second source arrives and not before (*ōrdo* §4) | rank-minimality — build higher-rank machinery only when an instance forces it; the capability poset stays a flat set until a sixth capability earns it (L58) |

The last row is not a rhyme but the **same law** (L58) surfacing independently in a sibling project — evidence it
is not a Urðr-specific tic.

## 5. The lineages

**Internal (epistemic containment, the arc this repo walked).** L11 *integrity is not truth* → L56 the
epistemic-class law stated → L57 its affirmative form (enforcement ≤ justification) → the claim-class registry
(the law made a checker) → L58 the rank-minimality of representation. Each rung refused structure ahead of
evidence and shipped a falsifier with every primitive.

**Intellectual (cited as lineage, never as authority — the `tre/` table).** Cutler (a hard contractual boundary
above the substrate), Peirce (semiosis; index → symbol; `signum ≠ rēs`), Lamport (order over wall-clock), Mead /
Mahowald & Delbrück (compute in the continuum, discretize at the spike), Reenskaug (the Model caged behind View +
Controller). `tre/` says each *anticipated* a move; it never says any *invented* the thing — the same `declared ≠
verified` restraint, turned on history.

## 6. Honest boundary — what this file does NOT establish

- It does **not** claim Urðr and `tre/` are one project or share code — they share a *discipline*, not a
  codebase (L5). Two projections of one principle are not one law (§2).
- It does **not** re-verify Ursprung's measured results. `DVSM/verify.py` (12/12) and the P3 membrane were
  checked against the source this session; the `cargo`/`weltkern` suites and the workbench-gated renderer were
  **not run here** — those grades are **routed from Ursprung's ledger, not earned here**. `built ≠ adopted`.
- It does **not** promote the unifying principle (§2) to a law. It is an explanation; mechanizing it would be the
  premature abstraction L58 forbids.
- This file is itself **DECLARED lineage**, exempt from the prose checkers as recorded history, and carries no
  gate of its own. Its Ursprung references are the falsifiable part — named, graded, and re-runnable in that
  repository. `integrity ≠ truth`.
