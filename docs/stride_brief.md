<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: stride-tick -->
# `stride` — design brief (URDRSTR1)

## What this rung is

`worldbasis` decided what a coordinate means. `contact` decided what support *is*, and did it
without a caller so the semantics could be falsified before anything implemented them. **This is
the caller.** It invents nothing: every support question is asked of `contact` and every answer is
taken. That is the whole return on having written the contract first — a tick that reimplemented
the vertical law would have been free to disagree with it, and nothing would have noticed.

"Consumes rather than reimplements" is not left as prose. Severing `contact.step_vertical`,
`step_horizontal` or `contact_of` must **kill** the tick, and three falsifiers check exactly that.
A tick carrying a private copy would keep running.

## The order is a decision

**Horizontal resolves before vertical.** The grounded step law is written against the support state
an actor is standing in, so support must still be the state it had when the tick began.

The counterfactual is *executed*, not described: resolving vertical first leaves a jumping actor
airborne, `contact` then refuses the horizontal step as air control, and the tick would have to
either invent air control or drop the input. Either way "you may not move on the tick you jump"
arrives as a gameplay law nobody chose. So: step, then jump — and a step and a jump on one tick
both happen, which is the pinned `leap` scene.

## Three boundaries the tick owns

**No air control.** An actor airborne when the tick begins does not move horizontally. `contact`
refuses to answer for one; the tick honours the refusal rather than inventing an answer. The same
rule settles a case that looks like a third thing and is not: a step that walks *off* a ledge leaves
the actor airborne, so a jump requested on that same tick does not fire. You may not jump off ground
you have already left, and that follows from the order rather than from a special case written to
produce it.

**The world edge is a wall.** `contact.ground_height` refuses an out-of-field query — correctly,
since it has no record to make. The tick has one, and it is `glide`'s: a step off the grid is
blocked. The refusal is not caught and reinterpreted; the tick simply does not ask a question it
already knows is outside the world.

**A contested intent refuses.** Two *different* intents for one actor on one tick is not an input to
reconcile — it is two authorities claiming one actor, which is `authinput`'s question — and taking
the last silently would be a decision with no record. Two *identical* intents are absorbed, because
that is delivery, not conflict.

## The witness explains; it does not steer

The invariant named when `contact` landed. A support witness answers *why* an actor is supported. It
must never become *therefore move it here.* Guarded twice, independently:

**Structurally** — no function on the trajectory path can receive a witness. The signatures cannot
take one. This is the sealed-observer discipline the repo already applies to metrics: enforce it
where a comment cannot be ignored.

**Operationally** — blanking the witness leaves the trajectory digest bit-identical while the
witness stream itself demonstrably moves. Both halves are asserted, because a comparison of
trajectories alone would pass vacuously if the blanking did nothing.

And the operational guard is shown to **catch a tick that genuinely steers**. A tick that reads the
witness's contact height and places the actor there is indistinguishable from the honest one while
the witness is truthful — both put the actor on the ground. Blank the witness and it teleports below
the terrain, which is exactly the failure the guard exists to see. The honest tick, under the same
blanking, does not move at all.

## Measured, not optimized

    per actor-tick    1 support probe + 1 vertical law          = 2
    per horizontal attempt (supported, in-field, intended)      + 2

Checked against `contact`'s counted door over the pinned scenes and a three-actor walk on the 64×64
island: **198 reads predicted, 198 actual**, across 72 actor-ticks and 27 attempts. The prediction is
derived from the *public trajectory* and spends no reads of its own — an actor's support state
entering tick *t* is the state tick *t−1* left it in, because nothing moves between ticks, so the
predictor reads the returned state stream instead of asking the terrain again. A measurement that
had to touch the thing it measures would be measuring itself.

**60 of those 72 actor-ticks are redundant**: the support probe and the vertical law read the same
cell whenever the actor did not change cells. That is reported and **left in place.** There is no
measured cost target yet, and removing it now would be an optimization chosen by inspection — the
habit this arc keeps declining. What the next rung inherits is a number, not a hunch.

## The schema door learned to name its law

`worldstep` refused a 3D world with "the LAW has not migrated." That sentence was written as if there
were one tick. There are two now, and it stops being a fact about the repository and becomes a fact
about *which law was asked.* `arena` is `step_tick` — two components, unmigrated and unmoved.
`stride` steps three and cannot step two. **Neither is a successor to the other**; they have
different domains, and one global `tick_supports` would have made the walker's arrival read as the
arena tick migrating, which it did not. The refusal now says not "nothing can step this" but "the law
you asked cannot, and here is the one that can."

## The first conformer

`worldbasis`'s census has recorded, since it was written, that **nothing conforms** — the honest
starting state, since a census showing everything already conforming would mean the contract had been
written to fit. `stride.world` is the first entry that does, and the conformance is judged by
`worldbasis` reading the world rather than by `stride` asserting it, because a subsystem grading its
own conformance certifies nothing. The other four entries are unchanged and still do not conform.

## Grade

**MEASURED**: determinism, peer agreement under reordered and duplicated delivery, the five pinned
scenes, the complete jump/step/fall behaviour, every refusal, both witness-inertness guards, and the
read-count closed form checked against execution. **DECLARED**: that this is a *complete* 3D tick —
it walks actors over terrain and does not do actor-actor collision, statics, or sub-cell motion, none
of which it claims.

`does_not_show`: that the arena tick migrated; that a read **count** is a read **cost**; that a
trajectory is *correct*, only that it is reproducible and that its support states are the ones
`contact` certifies.

Rows `stride-tick`, `stride-witness`, `stride-inputs`, `stride-cost`, `stride-schema`; falsifiers in
`tests/test_stride.py`.
