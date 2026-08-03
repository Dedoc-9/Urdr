<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# PREDICTIONS — executable epistemics for the predictive READ pass

Every epistemic state is an **executable artifact**, never a prose claim — the Urðr discipline (a claim is
what a gate can turn red) extended to the research process itself. A candidate moves through a state machine,
and every transition carries an executable **witness**:

    UNKNOWN → PREDICTED → PREREGISTERED → READ → OBSERVED → SURPRISE → [ RECURS? → COMPRESSIBLE? → PROMOTED → EXECUTABLE ]

    transition                   witness
    PREDICTED → PREREGISTERED     an immutable git commit dated BEFORE the READ (the rows below)
    PREREGISTERED → OBSERVED      the design brief + the module's live gate output
    OBSERVED → SURPRISE           a structured delta against the frozen prediction (observation vs reality)
    SURPRISE → COMPRESSIBLE       an independent-recurrence detector          — DEFERRED (needs many rows)
    COMPRESSIBLE → PROMOTED       a promotion rule satisfied                  — DEFERRED
    PROMOTED → EXECUTABLE         a new gate / falsifier / theorem added      — DEFERRED

Only the states an experiment has REACHED are populated. The tail and every metric (discovery /
compression / promotion rate, predictive bias) are functions of MANY rows, so they are DEFERRED until
independent recurrence earns them. By the proposal's own **L3** (no promotion from one observation) and **L4**
(a promotion must REDUCE executable complexity), this ledger cannot grow its own tail on zero data — it obeys
itself from the first row.

Laws (they govern this ledger, not merely describe it):
  - **L1** — observation precedes interpretation; a compression may cite only OBSERVATIONS.
  - **L2** — observations are immutable; interpretations may be rewritten (measurements fixed, explanations improve).
  - **L3** — no promotion from a single observation; independent recurrence is the bar.
  - **L4** — every promotion must reduce EXECUTABLE complexity (fewer gate rows / theorem variants / predicates).
  - **L5** — every promoted law must PREDICT something not previously predicted, or it merely renames.

Outcome classes (what was LEARNED, not whether a surprise happened): CONFIRMED-MODEL · LOCAL-SURPRISE ·
ARCHITECTURAL-SURPRISE · FOUNDATIONAL-SURPRISE. A CONFIRMED-MODEL is evidence, not a null: a prediction
surviving a blind READ is information. Stopping rule for the current run: 5 joints, then the class
distribution decides whether a seam basis has earned existence.

Prior reads, entered post-hoc as the seam hypothesis this experiment now tests forward (NOT preregistered —
labelled after the fact, and marked so): `heightfield` → representation seam · `jurisdiction` → admission
seam · `layertheorem` → propagation seam. Three post-hoc labels are a hypothesis-generator, not a basis.

---

## PREREGISTERED — frozen before the READ

### P1 — `opcost`
    state:            PREREGISTERED
    target:           opcost  — next unbriefed articulation joint, import in-degree 7 (centrality-selected)
    provenance:       predicted from opcost's ROLE only (AGENTS.md §7: "op-cost envelopes" bounding tick
                      time); its code is UNREAD. Only its import in-degree was computed, to select it.
    hypothesis:       a COST / BUDGET boundary — a NEW seam (not representation / admission / propagation):
                      an operation is admissible iff its measured op-cost fits a bounded envelope, else a
                      typed refusal.
    refutation risks: named in advance, both real — (a) ADMISSION in disguise: a permission predicate over
                      cost, i.e. the jurisdiction pattern REPEATING, not a new seam; (b) CONSERVED: cost is
                      an invariant quantity rather than a bounded envelope, REFINING the seam into a
                      conservation fact.
    success_rule:     classify opcost's core seam from its LIVE gate rows and core law (the `opcost*` rows),
                      never from prose. CONFIRMED-MODEL iff the core law is "cost ≤ envelope, refuse
                      otherwise"; a SURPRISE (residual recorded) if it is an admission predicate (a) or a
                      conservation invariant (b).
    residual_format:  if SURPRISE, record the delta as a triple — (predicted: bounded envelope; observed:
                      <opcost's actual core law>; delta: <admission (a) | conservation (b)>). The observed
                      half is immutable, the delta label revisable (L1/L2); it is the Stage-C delta the
                      OBSERVED→SURPRISE transition emits — so the blind READ has zero ambiguity in shape.
    witness:          the git commit introducing this row — dated before opcost.py is read.

## OBSERVED / RESOLVED — the delta ledger

### P1 — resolved: **CONFIRMED-MODEL** (the frozen block above stays byte-intact as the witness)
    read:             2026-08-03, the blind READ (Rung A). Classified from the LIVE gate rows and core
                      law per the frozen success_rule — never from prose.
    observed:         opcost's core law IS "cost <= envelope, refuse otherwise", as two inequalities:
                      (1) ENVELOPE — glide_micro_count <= glide_micro_bound, STRICT on the wall scene
                          (`opcost-bound`; the bound is non-vacuous, a wall witness);
                      (2) BUDGET — within_budget(cost, budget) admits at/under the ceiling and raises a
                          typed OPCOST-REFUSE over it (`opcost-budget`: "refuse, never overrun").
                      Plus one structure the prediction did not anticipate: the WORK / WALL-CLOCK split —
                      the certified half is the deterministic exact op-count (a pure function of input,
                      byte-exact digests); wall-clock lives in bench.py, host-tagged, never gated. The
                      seam certifies only the deterministic half of latency.
    refutation risks: both named risks measured FALSE from the rows —
                      (a) NOT admission-in-disguise: the predicate input is a measured resource quantity
                          of the operation itself (an exact op-count), not canonical lattice state.
                          jurisdiction refuses on WHERE truth lives; opcost refuses on HOW MUCH WORK the
                          operation performs. Same refusal DISCIPLINE (typed, fail-closed), different
                          measured object — a distinct seam, not the admission pattern repeating.
                      (b) NOT conserved: cost is BOUNDED, not invariant — count < bound strictly when a
                          wall bites. (Conservation appears downstream in govern: admitted + deferred ==
                          all — a different quantity, actors not cost.)
    delta:            none — CONFIRMED-MODEL; the residual_format goes unused, as designed.
    outcome:          the COST seam exists as predicted. Seam labels now: representation / admission /
                      propagation (post-hoc) + cost (PREREGISTERED, confirmed). Still a
                      hypothesis-generator, not a basis — one preregistered confirmation and three
                      post-hoc labels do not earn a seam taxonomy (L3).
    contamination:    DISCLOSED — after the prediction text was frozen and gate-tested (2026-08-03
                      ~19:43 UTC) but before the witness commit was pushed, a lineage chronology scan
                      printed opcost's first-commit SUBJECT ("certified integer-work envelope +
                      host-tagged wall-clock"), leaking the phrase "work envelope" into the session. The
                      frozen text predates the leak (file mtime + session order); the commit witness
                      ALONE would not prove that. Recorded per L1/L2: the leak is the immutable
                      observation, the priority of the freeze is the interpretation. Rule forward: freeze
                      commits land BEFORE any history scan of the target module.
    law note:         the candidate Attentional-Epistemics law's UNLESS clause (a conserved gradient in
                      unobserved regions) was bound to refutation risk (b) as its first discriminating
                      test; (b) measured FALSE, so the law's first datapoint is NEGATIVE — no
                      conserved-cost mechanism earned. The law stays stated-not-mechanized.
