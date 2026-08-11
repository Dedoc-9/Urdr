<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: retain-census -->
# `retain` — design brief (URDRRTN1)

## The question `vouch` left open

`vouch` proved a mid-trajectory snapshot is *sufficient*, and caught a lossy one by planting the
removal of the vertical velocity. That answers "is this record enough". It does not answer the one
with a consequence: **which parts of it are doing the work, and where.**

## `INERT` is the verdict that can fake a result

Remove a field, resume, get the same tail. Two readings, indistinguishable from that observation:

    the field is genuinely not observed here      a finding
    the fixture never exercised it                a fake finding

`vouch` met this one level down — its first `event_tick` perturbation was aimed at a mid-flight
tick, `stride` correctly ignores air control, the clause read `INERT` and proved nothing. A
minimization built on unexamined `INERT` verdicts produces a record that is smaller **and lossy**,
and the loss surfaces as a desync nobody can reproduce. So three outcomes, never two:

    REQUIRED   the perturbation moved the trajectory or the reasons
    REFUSED    the perturbation made the resume refuse — an authority error, not a divergence
    INERT      the perturbation moved nothing — A STATEMENT ABOUT THIS TICK, NOT ABOUT THE FIELD

## The trap is exhibited, not warned about

A grounded-only control corpus reads `vy` **`INERT` at every one of its eleven ticks**, while the
jump corpus proves it **`REQUIRED` at eight**. A minimization run on the control alone would have
deleted a load-bearing field from a green sweep. That is the measurement that turns the caution into
a result.

## Two fields whose necessity is a function of the state, not the schema

**`vy`** — `REQUIRED` on every airborne tick, `INERT` on every grounded one. Not by choice but by
`contact`'s own law: a supported actor's gravity does not accumulate, so the tick overwrites it
before anything reads it. Checked against `contact`'s **state stream**, not a tick index, so it is a
claim about the law rather than about this fixture's timing.

**`y`** — sharper, and the sweep found it rather than the design. `REQUIRED` exactly when the actor
is airborne **or when the next tick carries a movement intent**, `INERT` otherwise. A one-unit lift
of a grounded actor is *erased within one tick* — `contact` reads it as airborne, gravity takes the
unit back, the actor lands on the ground it left — **except** when a step follows, because `stride`
refuses air control and a momentarily airborne actor does not take it.

That is the no-air-control law appearing in a state-retention sweep, which is not where it was
written. Both sets are **characterized**: predicted from the contact states and the canonical event
ticks, then required to *equal* the measured sets, on both corpora. `x` and `z` are `REQUIRED`
everywhere, which is the contrast that makes state-dependence a finding rather than noise.

## The counts are counts

    TERRAIN_GROUNDED   x, y, z        3 integers
    AIRBORNE           x, y, z, vy    4 integers

No byte figure, no rate, and **no claim that a smaller record is a faster one**. That is a question
for a benchmark on a named host, and a falsifier checks the module imports no clock. The arc has
declined to optimize without a measured target five times; this is the sixth.

## Grade

**MEASURED**: the per-field, per-tick verdicts over both corpora; both state-dependences,
characterized and required to equal their predictions; the `INERT`/`REQUIRED` separation proved to
matter by the control. **DECLARED**: minimality, which is with respect to *this corpus* and says so —
a field `REQUIRED` nowhere is proved unobserved by two fixtures, not proved redundant.

`does_not_show`: that an `INERT` field is removable — that is the whole discipline here; that a
smaller snapshot is faster; that the field set is complete, it being the set `vouch`'s record
carries and a field nobody stores cannot be ablated; and this corpus never *separates* the trajectory
from the reasons — every `REQUIRED` verdict moves both — so it cannot distinguish a field one needs
from a field the other does.

Rows `retain-census`, `retain-state`; falsifiers in `tests/test_retain.py`.
