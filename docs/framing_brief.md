<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: framing-corpus -->
# `framing` — design brief (URDRFRM1)

## The same 93% arrived three times

    a pitch rotating the wrong way    93% sky      found by looking
    a pitch too steep for the focal   100% ground  found by looking
    a ten-unit jump                   93.7% sky    found by looking

`horizon_row` predicts the first two, because both are **pitch** problems and it is a statement
about where one line falls. It cannot predict the third, and nothing else could either — because
nothing in this repository answered the coverage question at all: *given a camera and a world, is
either class about to swamp the picture?*

## The math is trivial and that is deliberate

Ground at distance `d` and height `y`, seen from an eye at `e`, projects to
`row = cy + focal*(e - y)/d`. It lands inside the frame's lower half iff

    d > focal * (e - y) / rows_below

Everything here is that inequality rearranged in exact integers. **The value is in the census rule,
not the calculation.**

## Three clauses, three failures

**Structural.** `rows_below ≤ 0` means no ground can ever be in frame; `rows_above ≤ 0` means no sky
can. Pure functions of pitch and focal — no world, no triangles, no rasterizer. Between them they
catch both historical pitch failures before anything is projected, and they are reproduced at the
parameters they *happened* at: a 320-pixel frame at focal 320, horizons **+400** and **−80**, the
values `worldbasis`'s brief records. A failure re-staged at convenient numbers is a different event
wearing the same name.

**Entry.** `ground_entry(focal, drop, rows_below) = focal*drop // rows_below` — the nearest distance
at which ground `drop` below the eye lands inside the frame. **Linear in the drop**, which is the
whole explanation of the third failure: with a level camera, every unit of altitude pushes ground
further down the image, so the world leaves the frame from the bottom edge upward.

    drop  entry  ground px
       6     12       8797
      10     20       6234
      13     26       3175
      15     30       1580
      16     32        975

**Dominance.** A rendered frame in which one class holds at least **900 permille** is degenerate, and
is named by the class that swamped it. The threshold is a *choice* and is pinned as data, so a frame
cannot be re-graded by a number nobody is watching — and it is proved load-bearing: at 1 permille
every frame is degenerate, at 1000 only a wholly empty class is, and the standing frame moves
between them.

## The honest boundary

**The apex is not predictable from geometry.** The entry clause reads `FITS` — 32 against an extent
of 34 — while the rendered frame is 936 permille sky. Tuning `extent` until the clause fired would be
fitting the law to the answer. So the law says instead: two failures are caught before a triangle
exists, the third is caught by the census, and what the closed form supplies for it is the
**explanation** rather than the verdict.

That explanation is a claim that can be wrong, so it is checked against execution: over a real
`stride` jump the entry distance must be non-decreasing and the rendered ground count
non-increasing, in lockstep, by cross-multiplied integer comparison. A drop-blind `ground_entry` is
planted and leaves the claim with nothing to say.

## It must accept

A framing law that called every frame degenerate would catch all three failures and be worthless. The
corpus carries a `WELL_FRAMED` case and the law is required to admit it; a census that always refuses
is planted and reddens exactly there. All three verdicts must appear across the four cases.

## Grade

**MEASURED**: the structural clauses against both historical pitch failures; the dominance verdicts
against rendered pixel counts; the monotonicity of ground against eye height over a real jump.
**DECLARED**: the dominance threshold.

`does_not_show`: that the third failure is predictable without rendering — it is not, and the law
says so; that a `WELL_FRAMED` frame is a *good* frame — this bounds degeneracy, never composition;
that the three clauses are exhaustive, they are the three that were paid for; that a frame passing
here is *correct*, which is `vantage`'s compass law and not this one.

Rows `framing-corpus`, `framing-arc`; falsifiers in `tests/test_framing.py`.
