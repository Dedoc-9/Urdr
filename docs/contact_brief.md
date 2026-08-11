<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: contact-cycle -->
# `contact` — design brief (URDRCON1)

## The decision it records

The 3D tick has to decide what gravity does to an actor standing on terrain. `glide` answers that
implicitly — the ground under an actor is whatever `heights[fy>>32][fx>>32]` says, and being on it
is not a state the simulation carries. That is exactly right for a 2D walk and not enough for a
world with a vertical axis, because **standing and falling then differ in what the tick does**.

The rung this brief records is the contract, not the tick. The tick does not exist yet; the law it
will need is written where it can be falsified before it has a caller.

## Three states, and the third is declared rather than produced

    AIRBORNE            gravity integrates the vertical component
    TERRAIN_GROUNDED    the vertical component is constrained by the terrain under the actor
    GEOMETRY_SUPPORTED  the vertical component is constrained by collision support that is not
                        terrain — a platform, a ramp, an exported static, a future primitive

Nothing in this engine can produce the third, and it exists anyway. Terrain ground and arbitrary
collision support are **not the same thing**, and a contract that collapsed them would have to be
un-collapsed by whoever first stands on a platform. `geometry_support_is_unproduced` asserts the
current absence and is written to flip when a producer arrives.

This is deliberately **not** the shape L65 records. An unsatisfiable law is one that *gates* on a
condition nothing can meet. This state gates nothing — both movement laws branch on membership in
`SUPPORTED_STATES`, never on the name `TERRAIN_GROUNDED`, and a falsifier empties that membership
to prove it. The reservation costs one tuple entry and buys the distinction.

## The support witness

Grounding does not record a boolean. It records **why**: source, cell, the terrain revision it was
authored against, and the contact height. Rollback asks *given the same inputs and snapshot, did I
reach the same grounded state?* — and a witness makes that a comparison rather than an inference.

The revision field is the part that composes. An edit under a parked actor bumps the revision and
therefore the witness, so `resurrect`'s stale-snapshot law arrives at the contact seam without new
mechanism. A witness that dropped the field would make that claim unable to fail, so the falsifier
plants exactly that and requires it to redden.

## The walk and the contact law disagree — measured, not discovered later

`stance` and `glide` hold that downhill is always traversable and the actor is on the destination
ground the instant it crosses. They are right: **an actor with no vertical axis cannot fall.** The
contact law says a drop *loses support* — the actor keeps its height and gravity takes it down over
ticks, because snapping it to the lower ground is the authority moving an actor with no record.

Over every ordered adjacent pair of the island preset:

    16 128 steps      5 177 blocked by both laws      8 791 agree      7 337 differ

and the divergence is **characterized, not merely counted**: the admission decisions agree
*everywhere* (`walk_contact_divergence` refuses outright if any pair disagrees about admission), and
the resulting state differs on **exactly the strict drops** — no more, no fewer. A flat field
diverges nowhere, which is what makes the 7 337 a property of terrain rather than of the comparison.

This is `worldbasis`'s sample-convention finding one layer up. Neither law is a bug. The defect
would have been letting the 3D tick silently contradict a frozen movement law; instead it supersedes
a **known** one, with the gap on the record before anything depends on either.

## The cost denominator, before any cache

Every terrain read in the module goes through one counted door, so the terrain-lookup component of
an operation is an exact reproducible integer rather than a swept number:

    contact_of 1        step_vertical 1        step_horizontal 2        run_cycle == its tick count

`step_vertical` reading **once** was written red and immediately caught the first version reading
the same cell twice — once inside `contact_of`, once for the landing test. That is the whole
argument for counting: it found a defect in the module it was measuring, on the first run.

A count is not a cost. It is the denominator a cost claim would have to be divided by, and it exists
*before* the cache the arc has repeatedly declined to build without one.

## Grade

**MEASURED.** The transition laws are exact integer state machines checked over the complete
`ground -> jump -> airborne -> fall -> ground` cycle read as a **sequence** — a final-state assertion
would pass for a run that never left the ground. Gravity is asserted not to accumulate while
grounded; the witness is asserted reproducible under replay and different under a changed revision;
the walk/contact divergence is counted against its denominator and characterized; the lookup counts
are exact. Five planted defects — accumulating gravity, a revision-blind witness, a doubled read, a
snap-down, and a name-tested reserved state — were each proved to redden before the goldens pinned.

**DECLARED:** `GEOMETRY_SUPPORTED`, which no producer exists for.

`does_not_show`: that the 3D tick exists; that terrain is the only possible support; that a witness
proves the terrain was *correct*, only that two runs agreed about it; that a lookup **count** is a
lookup **cost** — the wall-clock question is `bench.py`'s and stays there.

Rows `contact-cycle`, `contact-witness`, `contact-seam`, `contact-cost`; falsifiers in
`tests/test_contact.py`.
