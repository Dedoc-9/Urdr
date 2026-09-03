<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxtile-result -->

# `voxtile` (URDRVTL1) — design brief

*The tile size was never a tuning parameter. It was the answer.*

## Observe

Every rung from `voxcond` onward reached the same verdict: the certificate is sound, it retires real
work, and the arrangement still loses to the committed reference. `voxbreak` put a ledger under that
and found the deficit was not the certificate but the **tiled scaffolding** — 10,168,290 operations
over the reference before a single certificate is consulted. `voxschism` costed four strategies per
tile and found the tiled traversal winning **zero** tiles of 1,728.

Every one of those measurements was taken at one tile size that nobody ever varied. This rung varies
it, against five predictions committed one commit earlier in `voxbreak` and quoted here by digest.

| tile | cold + book | **certified + book** | tax | retired | vs reference | certified tiles |
|---|---|---|---|---|---|---|
| 1 | 13,559,298 | 11,245,507 | 1,437,584 | 2,313,791 | **−876,207** | 54,056 |
| **2** | 13,961,755 | **10,820,264** | 1,840,041 | 3,141,491 | **−1,301,450** | 12,581 |
| 3 | 15,065,545 | 11,672,193 | 2,943,831 | 3,393,352 | **−449,521** | 5,148 |
| 4 | 16,321,495 | 12,712,731 | 4,199,781 | **3,608,764** | +591,017 | 2,684 |
| 6 | 19,338,330 | 16,000,725 | 7,216,616 | 3,337,605 | +3,879,011 | 918 |
| 8 | 22,678,590 | 19,454,111 | 10,556,876 | 3,224,479 | +7,332,397 | 422 |
| 12 | 31,076,035 | 29,005,299 | 18,954,321 | 2,070,736 | +16,883,585 | 89 |
| 24 | 67,107,269 | 67,201,708 | 54,985,555 | −94,439 | +55,079,994 | 0 |

Reference: **12,121,714**. Every declared size divides both 96 and 72, so no partial tile at a frame
edge can confound the comparison.

## Orient

**Three of the eight sizes spend less than the committed reference.** The best, tile 2, is
**10.7% below it** — colour and depth byte-identical as lists on all sixteen states. One strategy,
one constant, **no selector**. It is the first time in this arc that anything buildable has beaten
`voxref`.

**The first pass looked far better and was wrong, and that is the most important thing in the rung.**
Uncharged, the *unit* tile comes out at 9,752,785 — nineteen and a half per cent under, and better
than anything the charged sweep can reach. That number cheats in five places the untiled reference
never pays:

| term | what it is | tile 1 | tile 8 |
|---|---|---|---|
| `range` | four divisions per triangle for its tile range | 276,028 | 276,028 |
| `index` | one multiply per (triangle, tile) pair | 981,957 | 41,823 |
| `owners` | one insert per triangle for the owner index | 69,007 | 69,007 |
| `visit` | one per tile of the grid, empty or not | 110,592 | 1,728 |
| `complete` | one read per pixel of every certified tile | 55,138 | 28,352 |
| | **total** | **1,492,722** | **416,938** |

The uncharged terms were worth **three and a half times more to the arm that was winning** — which is
exactly how a sweep talks itself into a result. Charging all five moved the optimum from tile 1 to
tile 2 and cut the win from 19.5% to 10.7%. They are reported *separately* rather than summed,
because a record that declares five terms and prints one total is naming rather than describing, and
each scales differently: `range` and `owners` are per-triangle constants, `index`, `visit` and
`complete` are what the tile size actually moves.

**Two anchors prove the instrument rather than assume it**, which a sweep needs more than most
measurements do, since a sweep that quietly re-derives its own baseline can produce any curve it
likes. At tile 1 the cold loop costs **exactly 12,121,714** before bookkeeping — the committed
reference, to the operation — because unit binning walks precisely each triangle's own bounding box.
At tile 8 the sweep reproduces `voxbreak`'s own **22,290,004** and **19,037,173** to the operation.

## Decide

**Nothing earlier is retracted, and the scope is a law rather than a paragraph.** `voxbreak`'s
`the_inequality_has_no_solution_on_this_loop` is still true *of that loop*; `voxschism`'s zeros still
hold *at that tile*. Both are **run** here beside this rung's result rather than cited, so the
conditionality is a fact the gate re-derives. What was never true is the impression they left — both
were verdicts about a loop nobody had parameterised.

**And the selection problem was the wrong problem.** `voxschism` proved a perfect, free, unbuildable
selector over four strategies would save eleven per cent at the committed tile, and that no free
signal captures any of it. This rung takes 10.7% with no selector at all. The margin was never in
*which* strategy to pick per tile; it was in a constant that made every strategy expensive at once.

**Four of five predictions hit.** T1 (tax rises monotonically, 1.4M → 55.0M). T3 — the one the
pre-registration itself named as most likely to miss. T4 (total minimises at 2, retirement maximises
at 4; the curves really are opposed). T5. **T2 misses**, and its miss is the useful one: retirement
does not fall monotonically, it *peaks at tile 4* and falls either side — a large tile holds too many
owners to certify, a small tile has too little work left to retire.

## Act

`tools/terrain/voxtile.py`, gate stage `voxtile` (four rows: sweep / anchors / result / selftest),
red-first `tests/test_voxtile.py` (47 falsifiers), and the committed record
`spec/attest/voxref-tile.txt`.

`does_not_show`: nothing about time, and no wall clock enters. Nothing about memory — and at small
tiles that omission is at its most generous, since the owner map is one integer per pixel however the
frame is diced but the bin structure is not. Not that the operation model is the right cost: it is
`voxwork`'s, multiplies and divides, and a machine where a bin insert costs more than a multiply
would move the optimum. Not that 10.7% is the best available — eight sizes are declared and the space
between them is unsearched. And no promotion: `voxref` is untouched and nothing is adopted.
