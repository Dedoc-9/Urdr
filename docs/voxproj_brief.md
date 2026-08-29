<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxproj-refusal -->

# `voxproj` (URDRVXP1) — design brief

*The candidate law, predicted before it ran, and refused on evidence. Two hits, three misses, and
the misses are the useful part.*

## Observe

The diagnosis closed at `voxwin`: 374 coverage, 2 tie, 2 phantom. `voxslack` split the coverage
class by signed distance — 215 failing by exactly −1, which is the top-left convention, and 103
failing by a real but sub-pixel amount, which is the floored projected vertex.

This rung takes the second of those and proposes **one** change to the coordinate construction:

    control      the committed integer vertex quantisation — floor
    candidate    round-to-nearest, exact, at the same sub-pixel denominator

One variable. No fill-rule change, no convention change, no combination. The two arms differ by at
most one sub-pixel unit and agree wherever the division is exact — checked on constructed camera
points in both directions, not argued from the formula — which is what makes this a single step
rather than a different renderer. The control is required to reproduce `voxtie.render_level` at BEST
exactly, or the candidate would be measured against a stranger.

**The prediction was written into the module before a frame was rendered**, and is pinned as data in
the module and again in the record, so the committed artifact carries what was *claimed* as well as
what was measured.

## Orient

| | prediction | verdict | measured |
|---|---|---|---|
| **P1** | the sub-pixel misses largely close, more than half | **MISS** | 12 of 103 |
| **P2** | the on-surface misses do **not** close | **HIT** | 0 of 215 |
| **P3** | the winner-side misses fall in rough proportion | **MISS** | 5.4% against 11.7% |
| **P4** | no regression: gains exceed losses | **MISS** | +23 against −34 |
| **P5** | the ties and phantoms are not swallowed | **HIT** | both unchanged |

Every prediction is scored. `every_prediction_has_a_verdict` requires the verdict set to equal the
declared set, so a rung cannot report its hits and lose its misses somewhere between the measurement
and the record, and each verdict is computed from the arm rather than from the prediction's own text.

The law also requires the record to carry misses *at all*. A rung whose every prediction landed
would either be lucky or would have written its predictions after the fact.

## Decide

**Two hits, three misses, and the candidate is refused.** Net agreement goes 45550 → 45539 — eleven
pixels *worse*. Impossible faces move 152 → 151. Twelve of the 103 sub-pixel misses close and
thirty-four pixels elsewhere break. A repair that costs more than it buys is not a repair, however
good its motivation.

`the_candidate_is_refused_on_evidence` asserts the refusal *as the measurement*. It reddens on the
day the candidate starts winning, which is the day this rung must be reopened rather than quietly
kept.

**And the miss is the informative part.** Round-to-nearest halves the worst-case quantisation error
and removes its systematic direction, and **91 of the 103 survive it**. So the sub-pixel residue is
not a rounding-direction defect. The vertex being floored rather than rounded is not what puts those
samples on the wrong side of the edge — something else about the coordinate construction is, and the
most obvious candidate for it has now been eliminated by measurement rather than by argument.

**P2 is the hit worth keeping.** Not one of the 215 on-surface misses closed, exactly as predicted,
because they fail by the top-left convention and not by quantisation at all. A candidate that had
closed them would have been evidence the mechanism reading was wrong. It did not.

`does_not_show`: anything about performance. **That more precision would help** — a finer sub-pixel
denominator is a different single variable, and running it here would have made this two, so it is
named as the next rung and not attempted. Any mechanism for the surviving 91. And nothing is
adopted: `voxref` and `voxray` are untouched, the candidate is not promoted, the two ties are not
used to tune anything, and the two phantoms stay **red** rather than being folded into a carve-out —
a clean repair does not get to claim success by silently changing the oracle.

## Act

`voxproj-arm` holds the single variable and its validity checks, `voxproj-prediction` the five
statements and their verdicts, `voxproj-refusal` the measured refusal and what the miss eliminates,
`voxproj-selftest` the eight plants.

The falsifier naming this brief: `the_candidate_is_refused_on_evidence` states the refusal as a
measurement, not a policy. If the candidate ever gains more than it loses, the row reddens and the
rung reopens — which is the only honest way to hold a negative result.
