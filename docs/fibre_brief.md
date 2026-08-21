<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: fibre-reproduce -->

# `fibre` (URDRFBR1) — design brief

*The object beside the digest, and only one claim made of it.*

## Observe

A replay folds an input word into a state and renders it. The digest chain has always been an
identity instrument here — two runs agree or they do not — but nobody had asked what it
identifies. When two frames carry the same digest, is that because the state repeated, or
because the render map threw something away?

The question became live when the castle A/B showed castle-off and castle-on frames with
identical digests, and that identity was read as evidence the castle drew nothing. It was, but
only by accident of the walk. Nothing in the tree knew how coarse the digest actually is.

## Orient

Three things had to be decided before the instrument could say anything.

The object is READ OUT OF THE CODE, not chosen. `step_cam`'s camera is `(px, py, q, pitch_acc)`,
and to that the wanderer adds `av_state` and its elapsed frames since the last transition —
because `av_start = frame` is what makes concatenating two trace segments legal at all. Choosing
the object would have made the census a statement about the choice.

The harness is DERIVED, not written twice. `fibre_build.py` slices the demo between the
exact-integer helpers and the entry door — every renderer, the clipper, the digest, the loader,
unedited — and appends a replay main. Only that main is authored, and it is a transcription of
the demo's per-frame sequence, which means it can drift. The 43-checkpoint reproduction is what
catches drift, which is why the reproduction is the claim and everything else is output.

And the claim is deliberately NARROW. What a gate can certify here is that two records produced
on different operating systems by different compilers agree — a cross-placement reproduction of
exactly the kind this tree already makes. The census is interesting; it is not an invariant, and
promoting it to one would be claiming a property of renderers from a single walk.

## Decide

The census says something the tidy version of this question did not anticipate. 2564 frames
carry 2564 distinct objects and 2309 distinct digests; 31 digest classes hold more than one
object, 29 differing in the clip phase alone. The obvious repair — declare phase irrelevant and
coarsen — immediately fails: seven coarse states then carry more than one digest. Inspecting the
two remaining classes shows a camera standing still while the quaternion drifts by ONE ULP per
frame, some of those frames rendering identically and some not.

So the equivalence is not `forget a coordinate`. It is the fibres of the render map: the state
advances in increments so small that the framebuffer changes only when one of them pushes a
projected vertex across a pixel boundary. RENDER-INDUCED OBSERVATIONAL EQUIVALENCE is the honest
name — not a kernel, since no group structure is demonstrated, and not a projection, since it
forgets no nameable field uniformly. The tempting structural quotient is refuted by the corpus
rather than argued away, and that refutation ships as a predicate.

The temporal-skip ceiling rides along because it falls out of the same bytes and it decides
whether an optimisation is worth designing: a perfect free predictor could skip 215 of 2563
frame pairs, 8.4%, against a near-plane clip that cost 4–7% and was accepted without argument.
That is a property of a WALKING workload — position changes in 83.6% of these frames — and
quoting it without the workload attached would be the inflation this ladder exists to refuse.

`does_not_show`: that the digest is injective on the object (there are strictly more objects than
digests, so it cannot be); that equal objects give equal digests, which this corpus cannot test
because every object is distinct, so the converse is UNTESTED rather than passed; or anything
about another walk, reach, resolution, or a configuration with the castle on.

## Act

`fibre-reproduce` holds the one claim; `fibre-census` reports the quotient and its declared
boundaries; `fibre-selftest` proves the plants bite. The falsifier naming this brief: move one
checkpoint digest in the observation record, or delete one of its frames, and `fibre-reproduce`
refuses — the claim depends on the bytes and on nothing else.
