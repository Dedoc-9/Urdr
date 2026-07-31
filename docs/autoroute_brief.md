# Decide at the cheapest level that can decide (URDRAUT1): a design pass

<!-- brief-falsifier: autoroute-enforce -->

`inputset` decided where every quantity may live; `cohort` enforced it for one tier. This module makes
the taxonomy UNBYPASSABLE — a verifier that refuses to compute a quantity without the inputs its plan
designates, structurally rather than by convention. It is also the module in this arc that has been
corrected the most times, and the corrections are the content.

## OODA

**Observe.** A verifier that always fetches everything is correct and wasteful. The handed-down
cascade proposed inspecting what is local, running the cheapest procedure that can settle the
question, and escalating only when the mathematics demands it.

**Orient.** Three things had to be measured rather than assumed: which inputs a quantity actually
reads, whether dropping one is SAFE, and whether the plan is obeyed. Each turned out to have a
counterexample in the handed-down design.

**Decide — the laws.** The plan is the tier's chain prefix minus every atom BOTH a witness search and
a syntactic independence proof agree is unread. Enforcement is by CAPABILITY PROJECTION rather than by
checking. And the screen runs AFTER the payload is in hand, because it cannot precede it.

**Act.** Rows: `autoroute:scenes`, `-plan`, `-screen`, `-law`, `-vacuity`, `-determinacy`, `-fault`,
`-enforce`. Measured, one tier per line:

```
CERT     no certificate -> exclusion_membership: AUTOROUTE-MISSING-ATOM
LATTICE  no occupancy   -> occupancy_defect:     AUTOROUTE-MISSING-ATOM
HISTORY  no log         -> ledger_remainder:     AUTOROUTE-MISSING-ATOM
COHORT   no peers       -> quorum_agreement:     AUTOROUTE-MISSING-ATOM
```

## The laws

1. **Projection, not checking.** `guarded` verifies the plan then hands over the WHOLE situation —
   ambient authority in the object-capability sense, where a quantity reaches an input because it is
   in a broadly visible environment rather than because anything designated it. `projected` hands over
   ONLY the designated atoms, every other replaced by `NOT_FETCHED`, which refuses on USE. A quantity
   reading an undesignated input therefore refuses BY CONSTRUCTION and nobody enumerates reads.
2. **An atom leaves a plan only where TWO routes agree.** View determinacy (Nash–Segoufin–Vianu) is
   UNDECIDABLE for unions of conjunctive queries, so a family-search POSITIVE is forever
   family-relative while a NEGATIVE is exact from one witness. Syntax is the only route to a universal
   positive and is silent where a quantity reads an input the certificate already exposes. Only the
   conjunction licenses a drop. Measured: search 7 positives, syntax 5, silent on 2.
3. **The screen saves FLOOD FILLS, not bytes.** It tests `|mine XOR theirs| < k`, a function of the
   peer's cell set, so it cannot precede the payload fetch. Measured: 2 fills with the screen against
   7 without, 5 of 6 peers decided by count, BYTES SAVED 0.
4. **The screen is vacuous on a breached base, and the router refuses to run it there.** k = 0 when
   the base is already open; a breached submitter decides 0 of 6 peers where an intact one decides 5
   of 6. The vacuity is not benign — 4 of 64 one-cell perturbations DO flip a breached verdict.
5. **Three invariants, asserted rather than described.** Provenance (6, 0, 12, 0); guard transparency
   (24, 0); error partition (54, 16, 4, 0, True, 34) — DISJOINT and EXHAUSTIVE, so nothing escapes as
   an untyped third class.
6. **Typed, distinct refusals.** `AUTOROUTE-REFUSE`, `AUTOROUTE-MISSING-ATOM` and
   `AUTOROUTE-PEERFAULT` are distinct codes, not subclasses: a malformed request, an undesignated
   read and a proven Byzantine peer need different attribution.

## The glyph verdict: NO new glyph (kernel frozen)

Routing is a property of a verifier, not a construct in the language. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

Every search positive is family-relative and always will be — that is the hardness result, not a
corpus gap. Measured today the family's separation basis spans 2 of 8 semantic axes, so the positives
are weaker than their count suggests; `liveness_horizon` takes a single distinct value across all 54
members, so projecting onto nothing determines it by CONSTANCY and the search reports it droppable.
Syntax vetoes the drop, so the plan is right and the search is not. `projection_is_stricter_than_
checking` now reads (6, 6, 6): with the ambient-reader defect closed the two gates agree on this
corpus, so strictness is demonstrated by a PLANTED ambient reader rather than by a live one. This does
not show that a routed answer is HONEST, only that it used no input it did not designate.

## Where this sits

Above `inputset` (the taxonomy) and `cohort` (one tier's enforcement); below any deployment that wants
the taxonomy obeyed structurally rather than by convention.
