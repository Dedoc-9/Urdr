<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxcand-arms -->

# `voxcand` (URDRVXD1) — design brief

*Two repairs isolated, neither applied. The distinction between establishing a repair and promoting
one, made mechanical.*

## Observe

`voxmicro` proved the reference defective in a way that admits no argument: 2040 pixels awarded to
faces sandwiched between two solid cells, which no exterior camera can see at any resolution under
any sampling rule. That number needs no oracle, no exclusion and no ray/sample caveat. It has stood
for two rungs.

The obvious next move is to fix it. The trap in the obvious next move is that a repair landed in
`voxref` moves `O_t` on every frame, which invalidates `voxcoarse`'s 1728-state census and
`voxevent`'s subdivision ladder — both of which are measurements *of* the committed observable. A
**partial** repair invalidates them twice: once now, once when the rest arrives. And the four facts
declared as the precondition for regenerating that census were declared precisely so the census
would be regenerated once, against a reference that had earned it.

So this rung establishes the repair and refuses to promote it. `voxref` is asserted untouched every
gate run, and the candidate's digests carry a different MAGIC by construction, so a candidate figure
cannot be pasted where a frozen `O_t` is expected and pass unnoticed.

## Orient

Two fixes, crossed as a 2×2 rather than bundled as a before/after.

**Winding.** `voxray` established it: the screen-space Y inversion reverses projected orientation, so
the reference's `area <= 0` test discards the face pointing *at* the camera and keeps the one
pointing away.

**Weights.** `voxref.render` computes `w = edge(...) + top_left_bias` and then feeds those same
values into `d = (za*w1 + zb*w2 + zc*w0) // area`. The bias exists to decide which of two triangles
owns a shared edge — it is a coverage rule. It is not a barycentric coordinate, and using it as one
displaces the interpolated depth by up to one edge unit, which at grazing incidence is enormous.

The cross refuted the prediction that motivated it, and that is the finding of this rung.

| arm | impossible | agreeing |
|---|---:|---:|
| as-committed + biased (the reference) | 14032 | 8399 |
| as-committed + unbiased | **14655** | 8399 |
| reversed + biased | 2040 | 49030 |
| reversed + unbiased (the candidate) | **661** | 50547 |

Removing the bias while the winding is still wrong makes the impossible population **worse**, and
moves not one agreeing pixel — 8399 either way. Correcting the barycentric coordinates of a renderer
that is drawing the *wrong faces* does not make it draw the right ones; it gives the wrong faces more
accurate depths, and more of them win. The weight fix is conditional on the winding fix. A bundled
before/after would have reported "the repair helps" and hidden that one of its halves is actively
harmful in isolation.

**Perspective correction was tested and is refused.** With the bias still present it looked like the
answer in aggregate — 2040 down to 1430 — but it regressed `oblique` (300 → 577) and `corner`
(100 → 265), and that regression is what sent the search from the interpolation to the weights. Once
the weights are unbiased it changes **no winner at any pixel of any declared frame**; the two arms
are identical frame by frame. On depth *values* measured against the oracle's exact `t` it is a tie:
71.9% within one camera unit either way, mean absolute error 5.89 against 6.10. A tie that costs an
exact rational per pixel is not an improvement. The numbers are pinned so the hypothesis cannot
quietly return.

## Decide

The rung carries three separate identities, and keeping them separate is the design.

**The candidate is not the reference.** `voxref` still declares the committed winding and still
reproduces its own pinned contract digest — asserted, every run. The committed corner of the 2×2 is
required to reproduce `voxref.render`'s colour *and* depth buffers byte for byte, so a drifted
transcription reddens rather than quietly measuring a fourth renderer. And the candidate is required
to *differ* from the committed observable on every frame, because a repair that changed nothing would
otherwise be certified by this row.

**What the candidate buys is measured, not claimed.** Impossible pixels 14032 → 661; oracle
agreement 8399 → 50547 of 55296, 15.2% → 91.4%. Those are measurements of a proposal. Neither is a
correctness claim, and the residue says why.

**Everything that was true before must still be true after.** A repair that fixed visibility and
broke the partition would be a worse renderer with a better number. So `voxref`'s whole structural
chain is re-run through the candidate's own loop: the trace is still deterministic; no pixel of a
quad is claimed twice *while dropping the bias still double-claims on the same sample*, so the
partition holds with its control rather than on a sample that happens to have no shared edges; draw
order is still observationally irrelevant under both declared permutations; and both constructed
witnesses still exhibit their pairs, so neither digest has become a function of the other.

## Act

Against the four declared facts: projection correctness **passes**, unchanged. Face orientation
**passes** — all six single-voxel axis scenes go to zero impossible pixels, which is orientation
correctness demonstrated rather than argued. Preservation **passes**. Visibility correctness
**does not**: 54 impossible pixels survive across three of the twenty-three renderable micro-scenes
— `aperture` 38, `pair_oblique` 12, `world_standing` 4 — and 661 across the declared trace.

`the_third_fact_is_still_red` asserts that failure. The row is green *because* it says the fact is
red, and the law reddens on the day the residual closes — which is the day the frozen census may be
regenerated and not one rung before.

`does_not_show`: anything about performance. That the candidate is correct — it is measurably closer
and measurably still wrong, and those are different claims. That the residual mechanism is known: the
leading hypothesis is the integer flooring of projected vertex positions, which would also account
for the ~6-unit mean depth error and the `not_covered` population, and a named hypothesis with no
controlled experiment behind it is not a finding. And nothing about the observable, by construction.

`voxcand-arms` holds the 2×2 and the refused hypothesis, `voxcand-facts` the four facts with the
third red, `voxcand-preservation` the law chain re-run through the repair, `voxcand-selftest` the
three plants. The falsifier naming this brief: let the committed arm drift from `voxref.render` and
`voxcand-arms` reddens — because every number in the table is a comparison against that arm, and an
arm that is not the reference makes the whole table a measurement of nothing.
