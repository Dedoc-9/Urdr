<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxgrid-separation -->

# `voxgrid` (URDRVXG1) — design brief

*A correction to a sentence this tree published green, and the ladder that shows why the sentence
could not have been right at both ends.*

## Observe

`voxconv` found that nine tenths of the renderer's disagreement was the sample convention, and that
the class which collapsed hardest was `degenerate` — the exact ray crossing two or three lattice
planes at one parameter, where the oracle answers by convention. It then wrote, in a green gate and
a pushed commit, that `voxevent`'s 20.1% edge-or-corner entry rate "is a measurement of the sampling
grid rather than of the lattice."

That was an overstatement. The claim carried **no scale**, and the answer depends on the scale —
which the subdivision ladder was built to expose and which the one-liner threw away.

| scale | corner | centre | artefact share |
|-------|--------|--------|----------------|
| 1     | 1017   | 40     | 96%            |
| 2     | 6742   | 5245   | 22%            |
| 4     | 8496   | 5245   | 38%            |
| 8     | 11119  | 5507   | 50%            |

At the base lattice the degeneracy is almost entirely the sampling grid: integer screen coordinates
are the rays that land on lattice-plane crossings, and offsetting by half a pixel removes 96% of
them. At the finest scale it is half. The mechanism is not mysterious — subdividing by *s*
multiplies the plane density by *s*, so a half-pixel offset that dodged the coarse planes cannot
dodge the fine ones. But it means edge-and-corner entry is a **convention artefact at coarse scales
and a genuine property of the lattice at fine ones**, and no single sentence covers both ends.

## Orient

The corner arm is required to reproduce `voxevent`'s committed ladder exactly — four scales, four
measured columns. The frames are summed *per frame* and not unioned across them, because that is
what `voxevent` does; a union would be a different statistic wearing the same name, and the first
version of this probe made exactly that mistake and was caught by the binding rather than by
reading.

The columns are a deliberate subset of `voxevent`'s. `solid_cells` and `primitives` are properties
of the subdivision and cannot depend on where a ray was aimed; re-deriving them would pad this
rung's agreement with agreement it did not earn, and the exclusion is checked rather than trusted.

The shares are kept as **pairs of counts**, never as a single ratio, so every law compares them by
integer arithmetic. A percentage invented here would be a number this rung would then be tempted to
defend.

## Decide

**`voxevent`'s actual conclusions survive, which is the more important half.** Its headline is the
growth of the visible surface against the growth of the primitives, and that barely moves:

    visible faces  s=1     792 → 779       merged regions  s=1   452 → 441
    visible faces  s=8   17714 → 17496     merged regions  s=8  3079 → 3115
    merged growth s1→s2   +3.3% → +3.4%    faces s1→s8    ×22.4 → ×22.5

Under one convention and the other, the same rung says the same thing: 8× the primitives moves the
merged visible regions about three per cent, and the far end is censored by the ray budget. **The
ray-budget censoring survives exactly** — the hit count is identical at every scale under *both*
conventions, at two different totals (46685 and 46667). The row checks the totals differ, because
"identical at every scale" would otherwise be trivially true of one number.

So the damage is bounded and named: one rate in one row of `voxevent` was convention-conditional and
is now measured at both ends of the ladder. Nothing else that rung claimed moves.

A correction that had stopped at "the degeneracy was the sampling grid" would have been the same
kind of claim that produced the error — a statement with no scale attached, green because nothing
checked the scale. That is the third instance of this shape in four rungs: `voxfill`'s "the bbox
class is empty", `voxfill`'s "nearly all are sub-pixel", and now this. Slack in a claim is where
these keep hiding.

`does_not_show`: anything about performance. Which convention is right — as in `voxconv`, this rung
measures and does not decide. Any claim about scales past 8 or about lattices other than this one,
which is the exact failure being corrected and so is not repeated one ladder further out. Why the
centre-convention count is identical at s=2 and s=4 — it is, at 5245 both times, and a coincidence
noticed is not a mechanism found. And nothing is repaired: `voxref`, `voxray` **and** `voxevent` are
all untouched, and every committed record stays as it is.

## Act

`voxgrid-binding` holds the reproduction of `voxevent`'s ladder and the column exclusion,
`voxgrid-separation` the artefact shares at both ends, `voxgrid-survival` the conclusions that hold,
`voxgrid-selftest` the seven plants.

The falsifier naming this brief: `the_degeneracy_separates_along_the_ladder` demands a *large*
artefact share at the base scale and a *bounded* one at the finest. A rung that had simply restated
`voxconv`'s one-liner reddens there — and so would one that reversed it into "the degeneracy is the
lattice after all." The point is that both ends are real and the ladder is what tells them apart.
