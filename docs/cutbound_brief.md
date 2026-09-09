<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: cutbound-correction -->

# `cutbound` (URDRCBD1) — design brief

*Replace the bounded search, or formally retain it with an explicit theorem?*

## Observe

`shadowcut` settled which algorithm computes the right quantity: vertex-split max-flow answers a
different question, and a 0-1 BFS answers `cohort`'s. So the adjudication is **not** "which algorithm
wins." It is what `CUT_SEARCH_MAX = 3` actually **costs**.

It costs far less than it looked. Reading it as a limit rather than as **evidence** cost two live
defects instead.

## Orient

**What `None` means.** `min_cut` tries every subset of the wall from size 1 to `CUT_SEARCH_MAX` and
returns `None` when none of them opens it. That is not an absence of information. **It is an
exhaustive proof that k ≥ CUT_SEARCH_MAX + 1.**

Pair that proof with a witness and three classes fall out:

| wall | bounded | witness | proven interval | provenance |
|---|---|---|---|---|
| n=5, t=2 | 2 | 2 | [2, 2] | exhaustion |
| n=6, t=3 | 3 | 3 | [3, 3] | exhaustion |
| n=6, t=4 | **None** | 4 | **[4, 4]** | **meeting** — the two proofs coincide |
| n=6, t=5 | **None** | 5 | [4, 5] | bracketed — only the theorem closes it |

**So the cap costs nothing up to `CUT_SEARCH_MAX + 1`.** At the thickness-four wall the exhaustion
proves the floor, the witness proves the ceiling, and they land on the same integer — decided with no
appeal to the reduction at all. Only one wall further does a real interval open, and even then it is
a **bracket** rather than a blank.

Every provenance class is populated, because a classification with an empty class is a distinction
nobody has met.

**The theorem, stated because it is an argument and not a measurement.** A set S of wall cells opens
the wall exactly when some face-to-face route has all its wall cells inside S: deleting the wall cells
*on* a route opens that route, and any deletion that opens the wall leaves *some* route free, whose
wall cells it must therefore contain. Hence min |S| is the minimum over routes of the wall cells on
the route — what a 0-1 BFS computes. **This argument is what closes a bracket and nothing else does**,
and the boundary is enforced by a law rather than described in a sentence.

## Decide

**The verdict is RETAIN.** Replacing the enumeration with the path oracle would have produced the same
numbers with **strictly weaker provenance**: a refusal is a theorem about the wall, a witness is a
witness. The stronger-looking formulation would have destroyed the better evidence — the opposite of
what "the honest fix" sounded like two rungs ago.

**And reading the refusal as an absence cost two defects in the shipped law, both flattering.**

**The charge undercharged.** `charge_for_gap(None)` returned 0, so a wall the search could not decide
cost *nothing*, where the proven bound bills `BASE_CHARGE // (CUT_SEARCH_MAX + 1)` = 3. At the shipped
constants every gap from 4 to 12 was billed 0 against an honest 1 to 3. The charge is monotone
non-increasing, so the largest value the proof permits sits at the bound itself; taking it can only
ever *overstate* what an unknown-but-large gap costs, which is the conservative direction.

**The floor was cleared by accident.** `certifiable` returned True on `None` without consulting
`WALL_MIN_K` at all. At the shipped constants the verdict is right — 4 clears a floor of 2 — but only
because two constants happen to be ordered that way. Lower the cap to zero and `None` means merely
k ≥ 1, and the old branch certifies a **one-thick wall the floor exists to refuse**. That case is
reproduced here rather than imagined.

**Not one pinned figure moves.** `shadowcut` established that the bound is inactive across everything
`cohort.gap_table` pins, so both corrected branches are unreachable on the shipped corpus: the defects
lived on a path the corpus never walks, and both would have bitten on the first wall past it. A
correction that changes no observable and repairs a live defect is what makes this a repair rather
than a re-baselining.

**The subject is asked once.** Three of these walls are already in `shadowcut`'s swept corpus and its
answers come from the same `cohort.min_cut` call. Re-running the enumeration here would spend a minute
of gate time to obtain a number the tree already holds — and would create a second path to the same
fact for a later rung to find disagreeing.

## Act

`tools/terrain/cutbound.py`, gate stage `cutbound` (four rows: bracket / correction / verdict /
selftest), red-first `tests/test_cutbound.py` (33 falsifiers), the committed record
`spec/attest/cutbound-verdict.txt`, and two corrected branches in `cohort` itself.

`does_not_show`: **not that the bracket is tight** past the meeting point — from k ≥ 5 the interval is
real and only the theorem closes it, which is stated and not measured. **Not that the charge curve is
right**: the criticality-peak question is untouched, and this rung corrects only *which* k the charge
is evaluated at, never the shape of `B // k`. **Not that raising the cap is unnecessary** — that is a
cost question this rung does not price, and the meeting point simply moves with the cap. **Nothing
about time**, and no wall clock enters. And **no new algorithm enters the production path**: `min_cut`
is still the enumeration, and the path oracle stays in `shadowcut` as a witness source rather than a
decision procedure.

`falsifier`: `the_refusal_is_a_proven_lower_bound` reddens the day a wall the enumeration refused
turns out to have a cut at or below the cap, which would leave every bracket here unfounded;
`the_correction_changes_no_pinned_figure` reddens if any figure `cohort` pins moves under the
corrected branches, which would turn a repair into a re-baselining; and
`the_old_branch_certified_a_wall_the_floor_refuses` reddens if the latent case stops reproducing,
which would mean the second defect was never there and the correction is unmotivated.
