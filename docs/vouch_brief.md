<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: vouch-resume -->
# `vouch` — design brief (URDRVCH1)

## The question

`contact` made support a state with a witness — `(source, cell, revision, contact_height)`. `stride`
consumed it and proved the witness does not *steer*. Neither asked the one that turns a geometry
contract into a replay certificate:

> Given the same snapshot and the same inputs, does a resumed run reproduce the same **reason** —
> not merely the same position?

## Why re-running is not the answer

`stride.simulate` is a pure function of `(world, log)`. Replaying it from the start and asserting
equality restates purity and proves nothing. The claim has content only when the run **resumes from
a mid-trajectory snapshot**: the witnesses from tick *k* onward must equal the full run's, which is
false the moment the snapshot omits anything a witness depends on.

This is `splice`'s resumability discipline applied to the *reason* rather than the position, and it
fails exactly where a boolean `grounded` would have hidden the loss. Checked at **every tick** of the
arc, not one — a snapshot sufficient at tick 3 and lossy at tick 9 would pass a single-point check.
The plant: drop the vertical velocity from the record and the resumed reasons diverge, where a
from-the-start replay would still have agreed.

## A divergence report that names a cell

`lockstep.first_desync` localizes to a **tick**. That is the strongest thing a digest chain can say,
because a digest has no parts. **A witness has parts.**

    at tick 8 actor 0: grounded at cell (3, 2) under 'rev-0' at height 5
                   vs  grounded at cell (4, 2) under 'rev-0' at height 5

The reason is the payload, and it was already being computed. This is the capability the rung adds:
a desync report that says *which cell and which revision*, not *which tick*.

## Four perturbations move the reasons; two must not

    revision            REFUSED    (not a divergence — see below)
    cell                moved
    contact height      moved
    event moved a tick  moved
    delivery reordered  absorbed
    delivery duplicated absorbed

The last two are the clause that must **not** bite. `lockstep.canon`'s absorption arrives here
unchanged, and a rung that checked only the divergences would be certifying a witness stream that
changed whenever anything did.

**A fixture defect this rung found in itself.** The first `event_tick` perturbation was aimed at a
mid-flight tick — which `stride` correctly ignores, because there is no air control — so the clause
read `INERT` and proved nothing. A perturbation that cannot reach the law it is aimed at is a green
result with no content. The fixture was the defect, and the step moved to a grounded tick.

## The stale snapshot refuses rather than diverging

A snapshot authored against one terrain revision and resumed against another is not a replay that
disagrees; it is a replay that was **never entitled to run**. `resurrect` established that law for
durable actors and `contact`'s docstring promised it would arrive at the contact seam for free — here
it is exercised rather than promised, the refusal is typed `VOUCH-REFUSE`, and it says in as many
words that it is not a divergence. Checked in both directions: the same snapshot against its own
world resumes green, or the door would be one that is always shut.

## Grade

**MEASURED**: the mid-trajectory resume reproduces the witness stream at every tick of a real jump;
each perturbation moves it and delivery reorder does not; the divergence localizes and carries the
witnesses that explain it; the stale snapshot refuses both ways. **DECLARED**: that a reproduced
witness is a *correct* one — this certifies agreement between two runs, never that either read the
terrain right.

`does_not_show`: durability — nothing here writes bytes to disk, `persist`/`resurrect` own that and
this composes with their law rather than replacing it; that witness equality implies position
equality or the converse, both being checked separately here precisely because a rung that fused them
could not tell which had moved.

Rows `vouch-resume`, `vouch-perturbations`; falsifiers in `tests/test_vouch.py`.
