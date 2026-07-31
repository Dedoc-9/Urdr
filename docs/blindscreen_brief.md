# Cheapness is not soundness (URDRBLS1): a design pass

<!-- brief-falsifier: blindscreen-blind -->

A screen that is cheap and blind is worse than no screen, because it converts an unknown into a
confident wrong answer. This module refutes four cheap invariants, their conjunction, and a fifth
candidate, and records each refutation in a form that cannot be quietly reconsidered.

## OODA

**Observe.** `cohort`'s verdict is a flood fill. A cheaper proxy — a cell count, a boundary occupancy,
a tile prefix, an occupancy defect — would decide many peers without one, if any of them tracked the
verdict.

**Orient.** "Tracks the verdict" is falsifiable: exhibit two situations with the SAME invariant and
OPPOSITE verdicts. One such pair kills the candidate outright, and the kill is exact rather than
statistical.

**Decide — the law.** An invariant may gate a fetch only if no equal-invariant opposite-verdict pair
exists. Cheapness is irrelevant to admission.

**Act.** All four cheap invariants REFUTED, at divergences 4, 2, 16 and 16. Their CONJUNCTION refuted
by a single pair — they are blind in the same direction, so stacking them does not converge. A fifth
candidate, `free_components`, refuted by a hand-built pair. Rows: `blindscreen:scenes`,
`blindscreen-blind`, `blindscreen-conjunction`, `blindscreen-cost`, `blindscreen-valuation`.

## The laws

1. **Equal invariant, opposite verdict, one pair, dead.** A negative is exact from a single witness.
2. **The conjunction is closed, not the members.** No conjunction of the cheap four may gate a fetch —
   proved by one pair, not inferred from the members failing individually.
3. **The cost is counted in PEERS WRONGLY CLEARED**, not in cycles saved. A screen's price is the
   soundness it spends.
4. **Status is a closed vocabulary, mechanically checked.** `STATUS_VOCABULARY = ("FALSIFIED",
   "OPEN")` — there is no CONFIRMED, no PROVED and no IMPOSSIBLE, because what exists here is a
   counterexample per candidate and not an impossibility theorem.
5. **A refutation is a durable ROW**: `(candidate, status, witness, failure_mode, impact)`. All six
   rows currently read FALSIFIED; `OPEN` has no live instance.

## The glyph verdict: NO new glyph (kernel frozen)

Refutation of a proxy is a measurement about a verifier. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

Every refutation here is exactly a counterexample. **It is not an impossibility theorem**, and the
distinction is load-bearing: "`free_components` is not an invariant, as demonstrated by the following
witness" is what the evidence supports; "no cheap invariant can work" is not. The corpus is 545
occupancies built to separate verdicts, so a candidate surviving it is UNREFUTED rather than sound.
The valuation census reports cheapness alongside blindness precisely so nobody reads a low cost as a
recommendation.

## Where this sits

Beside `cohort`, whose verdict it tried and failed to proxy, and beneath `autoroute`, whose fetch
plans may not cite any of the refuted quantities.
