<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: shadowcut-remedy -->

# `shadowcut` (URDRSHC1) — design brief

*Does the vertex-split formulation produce the same answer as the bounded search, and does it expose
cases where the bounded search declared a cut optimal merely because it stopped searching?*

## Observe

`cohort` decides its min-cut by enumerating every subset of the wall up to `CUT_SEARCH_MAX = 3` and
returning `None` above that. The weak-spots list names the fix:

> the honest fix is a max-flow formulation on the vertex-split graph — the shape `auditgraph`
> already uses

This rung builds that formulation faithfully and measures it. **Nothing in `cohort` changes.**
`CUT_SEARCH_MAX` is still 3, `min_cut` is still the enumeration, and this module *imports* both
rather than transcribing either. A shadow adjudicator that edits its subject is not a shadow, and one
that reimplements the law it is checking is grading its own copy.

## Orient

| wall | bounded | shortest | maxflow | cross-section | scope |
|---|---|---|---|---|---|
| n=3, t=1 | 1 | 1 | 9 | 9 | pinned |
| n=4, t=1 | 1 | 1 | 16 | 16 | pinned |
| n=4, t=2 | 2 | 2 | 16 | 16 | pinned |
| n=5, t=1 | 1 | 1 | 25 | 25 | pinned |
| n=5, t=2 | 2 | 2 | 25 | 25 | pinned |
| n=5, t=3 | 3 | 3 | 25 | 25 | extension — **at** the cap |
| n=6, t=2 | 2 | 2 | 36 | 36 | extension |
| n=6, t=3 | 3 | 3 | 36 | 36 | extension — **at** the cap |
| n=6, t=4 | **None** | **4** | 36 | 36 | extension — **past** the cap |

**agree 8 · undecided 1 · diverge 0**

**The max-flow column is the cross-section and nothing else.** It does not move when the wall gets
thicker, because it is not measuring the wall. It counts how many *independent tunnels* could be
driven through the cross-section at once, one per cell of a layer. `cohort` asks what **one** tunnel
costs.

## Decide

**Why the shape is wrong — and `cohort` had already measured the reason.**

The quantity `min_cut` computes is a minimum-weight **path**: the fewest wall cells lying on any
face-to-face route, since deleting exactly those opens it, and any deletion that opens the wall
contains some route's wall cells. Max-flow computes a minimum **cut**. Turning a min-weight path into
a min cut is planar duality — and `cohort.hex_duality_fails_in_3d` is an existing law *of the very
module the remedy was proposed for*, measured on a 7-cube, stating that the two-dimensional Z₂
duality does not lift to three.

**The remedy reached for a duality its own subject had already refuted, one law away in the same
file.**

That refutation is *unpacked* rather than handed back: `hex_duality_fails_in_3d` returns a triple,
and a non-empty tuple is truthy whatever it contains, so a law that returned it directly could never
fail. The first draft of `the_duality_it_needed_was_already_refuted` did exactly that.

**The actual fix is smaller than the proposed one.** A minimum-weight path over node weights of zero
for free and one for wall is decided by a 0-1 BFS in linear time with no cap at all. It agrees with
the enumeration on all eight cases the enumeration can decide, and decides the one it cannot.

## The horizon, measured from both sides

**The bound is inactive on the pinned corpus and active immediately outside it.**

Across every case `cohort.gap_table` actually pins, the enumeration decides and the path oracle
agrees — so the `None` branch is unreachable there, and **the pinned gap figures were never artefacts
of the search horizon**. That is the reassurance this shadow was built to be able to *withhold*, and
it happens to be earned.

One step outside, at a wall of thickness four — an ordinary object — the enumeration returns `None`
while the path oracle answers 4. `CUT_SEARCH_MAX` is not a dormant limit; it is one wall away. The
extension cases were chosen to straddle it from **both** sides, two sitting exactly *at* the cap and
one past it, rather than to flatter either verdict.

## Every answer is witnessed by the subject's own primitive

The path oracle does not merely report a number. It returns the wall cells it would delete, and the
law removes exactly that set and asks `cohort.free_reaches` — the production flood fill — whether the
wall opened; then removes **one cell fewer** and requires that it did not. Both the sufficiency and
the minimality of every witness are adjudicated by the subject. **The oracle proposes and the subject
decides**, so a defect in the oracle's own bookkeeping cannot certify itself.

`undecided` is kept distinct from both agreement and divergence. An enumeration declining to answer
is a third thing, and collapsing it into agreement is exactly the inflation a shadow exists to avoid.

## Act

`tools/terrain/shadowcut.py`, gate stage `shadowcut` (four rows: comparison / horizon / remedy /
selftest), red-first `tests/test_shadowcut.py` (40 falsifiers), and the committed record
`spec/attest/shadowcut-comparison.txt`.

`does_not_show`: **nothing is promoted and no production law moves.** `cohort` is untouched and its
record still binds; whether to replace the enumeration, keep it with a stated theorem, or keep it
with a declared corpus bound is the **adjudication** rung's decision and not this one's. **Not that
the path oracle is optimal beyond the enumeration's reach**: its upper bounds are witnessed
cell-by-cell by the subject, but its lower bounds are exhaustively confirmed only where the
enumeration reaches, which is three — past three, minimality rests on the 0-1 BFS reduction being
correct, an argument stated here rather than a measurement taken here. **Not that max-flow is
useless**: it answers the tunnel-count question exactly, and a formulation is not wrong for answering
what it answers. **Nothing about time**, and no wall clock enters. And nothing about walls other than
the declared spanning slab, beyond the one plant that fixes the sign — a corpus of irregular
geometries is a different rung.

`falsifier`: `the_witness_is_adjudicated_by_the_subject` reddens the day an oracle reports a cut
whose own cells, removed, do not open the wall under `cohort`'s flood fill, which would leave every
number here unverified; `the_two_oracles_agree_wherever_the_bound_decides` reddens if the independent
formulation ever contradicts the enumeration inside its horizon, which would mean one of them is
wrong and the rung has found it; and `the_max_flow_formulation_answers_a_different_question` reddens
the day vertex-split max-flow tracks the wall thickness after all, which would reopen the remedy the
weak-spots list proposed.
