<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: mould-equivalence -->
# `mould` — design brief (URDRMLD1)

## A shape, not a policy

`retain` measured that a grounded actor's vertical velocity is `INERT` and an airborne actor's is
`REQUIRED`. The obvious next move is to drop it when grounded, and the obvious next move is a
**policy** — a rule someone follows, forgets, or gets wrong in one branch.

This rung makes it a **shape**. A grounded slot has no `vy` *field*: not a zero, not an ignored
value, no field. Writing one is not discouraged, it is impossible, and a reader cannot consult a
value that does not exist.

## The shape is derived, not tagged — and that is the whole arithmetic

The naive version tags each slot with its state so a reader knows how many integers to take. **It
saves nothing.** A tag costs one value per actor; `vy` costs one value per actor. The record is
exactly the size it was and now has a second thing to keep consistent.

What makes the shaping pay is that the state is **derivable from the prefix the record already
carries**: read `x, y, z`, ask `contact` what state that is in this world, and the answer tells you
whether a fourth integer follows. The record is self-describing *against the world* and carries no
field naming its own shape. A falsifier reads the record's own structure to confirm no tag is there.

## Both wrong neighbours are built

**All-airborne** is correct and pointless — the flat record with extra ceremony. Proved to save
nothing.

**All-grounded** is smaller and wrong, and it is caught **by refusal, not by divergence**. That is
the outcome that makes this a type: a 3-integer slot for an airborne actor produces a record whose
derived state wants four, so the shape *contradicts the world* and the record cannot be opened at
all. There is no lossy replay to compare, because there is no replay. A policy would have produced a
smaller record that silently resumed wrong.

The honest mould sits exactly between them, so "it saves something" and "it stays correct" are each
proved against the thing that would violate it.

## The shapes are read from `retain`, not restated

`retain.retained_fields(state)` is the measured answer to which integers a state needs, and this
module imports it. A shape table written twice is a table that can disagree with the measurement
that justified it. `GEOMETRY_SUPPORTED` is declared, has no producer, was therefore never observed
by `retain` — and `mould_for` **refuses** it rather than guessing, because a mould invented for it
would be a measurement nobody made.

## The saving is a count

    ticks 15   actors 1   flat 60 integers   moulded 53   saved 7

Reported with its denominator, and not as a rate, a byte figure, or a latency. Whether a smaller
record is a faster one is a question for a benchmark on a named host; a falsifier checks this module
imports no clock.

A grounded slot's absent `vy` reads back as zero, and that is not a default filling a gap: `contact`
guarantees a supported actor's vertical velocity *is* zero, and `retain` measured that perturbing it
changes nothing. The reconstructed flat record is asserted **equal** to the one `vouch` would have
minted.

## Grade

**MEASURED**: the moulded record resumes bit-identically to the flat one — trajectory and reasons
checked apart, per `vouch` — at every tick of a corpus carrying both states; the shape is derived
with no tag, checked structurally; a mis-shaped slot refuses in both directions with the correctly
shaped one admitted; both neighbours behave as claimed; the integer counts are exact.

**DECLARED**: that this is the *smallest possible* record. It is the smallest one `retain`'s corpus
justifies — a different claim, and the one made.

`does_not_show`: any wall-clock or byte consequence; that the two shapes are the only ones;
durability, which is `persist`/`resurrect`'s and is untouched.

Rows `mould-equivalence`, `mould-shape`; falsifiers in `tests/test_mould.py`.
