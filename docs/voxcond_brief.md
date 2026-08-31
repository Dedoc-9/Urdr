<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxcond-owner -->

# `voxcond` (URDRVXQ1) — design brief

*Five conditional certificates, scored against a prediction committed one commit earlier. Two of the
five predictions missed, and the misses are the result.*

## Observe

`voxpath` shipped this rung's pre-registration in the previous commit. This rung does not restate it:
it parses that file, checks its digest against the golden `voxpath` pinned, and requires its own
verdict set to *equal* the id set found there — not a superset, which would be a sixth predicate
smuggled in, and not a subset, which would be a miss quietly dropped. A prediction that must be
quoted from an earlier commit cannot be written after the result. That is the debt `voxsilo` opened,
paid.

Each predicate is measured on three quantities and **run as an arm** — the certificate is actually
used, and the resulting buffers are compared to the reference as lists on all 31 declared frames.

| predicate | sound? | cost | population | retired |
|---|---|---|---|---|
| P1 still | **yes** | 180 | 3 | 2595240 |
| P2 near_step | no | 300 | 8 | — |
| P3 same_cell | no | 360 | 9 | — |
| P4 same_owner | **yes** | 210871 | 555 tiles | 4038404 |
| P5 same_occupancy | no | 933120 | 18 | — |

## Orient

**Three of five predictions hit and two missed, and the two misses are the result.**

D4 said an ownership certificate would cost more than it retires, because determining which primitive
owns a tile *is* the work. That is wrong, and the error is instructive: the certificate does not
**determine** ownership, it **verifies** a remembered owner — and verifying is far cheaper than
searching. D5 said no cheap non-trivial condition would be both sound and productive; P4 is exactly
that. A pre-registration that landed all five would have been luck or hindsight.

**Every cheap camera-side predicate is unsound, and all for the same reason.** The camera moved.
Depth is a continuous function of camera position and `O_t` contains it exactly, so *"the camera
barely moved"* licenses nothing at all — not a pixel, not a tile, not a frame. `voxsilo` caught the
naive hierarchical-Z cull with this same contract; this rung catches three more, and none of them
would have looked wrong on inspection. Each of the three holds on at least one pair where the
observable nonetheless changes, so none is failing merely by never firing — a predicate that never
held would be vacuously unsound and would prove nothing.

**P4 is why the rung exists.** An ownership certificate does not license reusing a tile's pixels —
that is exactly the unsound move, and `voxpath` ruled it out by measuring that depth moves with the
camera. It licenses skipping the **search** for the owner while the depth is **reconstructed** from
the owner's own plane at the current camera. The certificate is executable proof about *who* owns the
pixel; the value is derived rather than remembered. Soundness rests on two conditions, and the tile
falls back to a full rasterisation unless both hold: no primitive outside the owner set can be nearer
than the farthest depth any owner reaches in the tile, judged by `voxsilo`'s **corrected**
conservative bound because the naive one is unsound and that rung proved it; and every pixel must
actually end up owned, which is discovered during the restricted pass rather than assumed away.

It retires 4038404 operations for 210871 spent — **nineteen times**.

**And the nineteen times must never be quoted alone.** That figure is measured against the tiled loop
the certificate sits on, which is the only comparison in which the certificate is the single
variable — and that loop costs 42913656 operations against the committed reference's 23201850. The
certificate saves four million on a loop that spends twenty million extra, so **the arrangement as a
whole retires nothing**. The mechanism is established and the implementation is not competitive, and
those are different sentences. `the_loop_it_sits_on_loses_against_the_reference` exists so the first
can never be reported without the second, and it reddens on the day the tiled loop stops losing.

## Decide

**This rung's first draft shipped the defect its own discipline exists to catch.** That draft computed
P4's certificate, counted what it *would* have saved, and then rasterised the whole bin anyway — so
its buffers matched the reference for the trivial reason that it had done all the work, and its
retirement was a formula wearing a measurement's name. It reported a 32-fold return. `retired` is now
**baseline minus executed**, taken from the run, which is a quantity no unused fast path can earn, and
`the_fast_path_is_actually_taken` requires it to be positive. The second draft then compared the tiled
loop against the *untiled* reference and reported a negative retirement, blaming the certificate for
the cost of the loop it sits on — the single-variable discipline `voxsilo` exists to enforce, applied
to this rung's own instrument. Both corrections are recorded, because a rung that hid them would be
publishing its third number as if it were its first.

`does_not_show`: nothing about time, and no wall clock enters. Nothing about memory, which is where an
ownership map's storage would be paid. **That a cheaper sound predicate does not exist** — five were
declared and five measured, and the space of conditions is not five things. That P4's implementation
is the cheapest possible one: a different candidate-rejection test would move its cost, and the
verdict is about *this* certificate rather than about ownership certificates in general. **That this
is a speedup** — it is not. And no promotion: `voxref` is untouched and not one certificate is
adopted.

## Act

`voxcond-prereg` holds the quotation from the earlier commit and the verdict-set equality,
`voxcond-unsound` the three refutations kept runnable, `voxcond-owner` the ownership certificate and
the two-sided reporting of what it buys, `voxcond-selftest` the record plants.

The falsifier naming this brief: `voxcond-owner` reddens if the fast path stops being taken, if the
certificate stops being sound, or if the tiled loop stops losing against the reference — the last
being the day this rung's honest caveat expires and the result becomes a speedup.
