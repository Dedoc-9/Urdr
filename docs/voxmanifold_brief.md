<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxmanifold-structure -->

# `voxmanifold` (URDRVXV1) — design brief

*The search experiment, scored. Yes on locality, no on the manifold — and the analogy dies three
separate ways.*

## Observe

`voxstate` declared the lattice, the four traversals, and this rung's pre-registration one commit
earlier. This rung parses that file, checks its digest against the golden `voxstate` pinned, and
requires its verdict set to *equal* the five ids found there. Five were registered; five are scored.

The certificate is `voxcond`'s P4 and nothing else — ownership, verified against the current camera,
depth reconstructed from the owner's plane. Inventing a new one would have made this experiment
measure two things at once.

| order | executed | certified tiles | retired vs Z0 |
|---|---|---|---|
| Z0 cold | 22,290,004 | 0 | — |
| Z1 row-major | 20,576,604 | 273 | 1,713,400 |
| Z2 zig-zag | 19,496,504 | 346 | 2,793,500 |
| Z3 nearest | 18,929,412 | 422 | 3,360,592 |

## Orient

**What survives is ordinary locality, and it is real.** Retirement rises monotonically with the
quality of inheritance. Choosing a nearer predecessor retires nearly twice what taking whatever the
scan order supplies does. M2 and M3 both hit. Adjacency governs validity; the zig-zag idea works.

**What dies is the manifold, and it dies three separate ways.**

**M1 missed.** Adjacent ordered pairs certify 27.75 tiles each against non-adjacent 21.75 — a 28%
edge. Real, but not the categorical difference a *connected region* implies. Validity is diffuse.

**M5 missed, badly.** All sixteen of the sixteen states are validity boundaries: every one retires
less than a quarter of its own cold cost. There is no cheap interior at all, so there is nothing for
a boundary-traversal scheme to be cheap *around*.

**Sub-additivity is zero of twenty-four.** Reaching C by way of B always costs more than reaching C
directly from A. An intermediate state never contributes reusable structure; it is only ever on the
way.

So there is no wake here — no shared structure in proof space, no interior that a few boundary
computations certify. There is a cache that works better when you inherit from something nearby,
which is the ordinary thing, honestly measured, and worth exactly what it is.

## Decide

**My own pre-registration was ambiguously worded, and that is itself the lesson.** M4 reads *"no
traversal beats Z0 in total operations"* and then argues from the tiled loop's 1.85× cost against the
**committed reference**. Two different baselines, opposite verdicts. The literal text is scored —
scoring the reading that flatters the result is exactly what pre-registration exists to prevent — so
M4 misses, and both numbers are reported:

| | operations |
|---|---|
| committed reference over these 16 states | 12,121,714 |
| Z0, tiled loop cold | 22,290,004 — **1.84× scaffolding** |
| Z3, best traversal | 18,929,412 — **1.56× the reference** |

Even the best traversal is half again dearer than `voxref`. The 1.84× independently reproduces
`voxcond`'s 1.85× on a different workload, which is the one thing here that generalises.

**And the first draft of that disclosure compared the wrong baselines** — it set this lattice against
`voxcond`'s reference figure, measured over `voxpath`'s *31* frames. The reference is now re-measured
on the sixteen states this rung actually visits. The correction is recorded because a rung that hid
it would be publishing its second number as if it were its first.

**The cold-start control is a law**, and it is what separates manifold structure from a warm cache.
Nothing crosses between states but the declared predecessor's owner map — no depth, no colour, no
geometry, no memo. Proved by re-running states in isolation with only that map and requiring the
identical executed count.

The path quantities carry **no verdict** and none is invented for them. They were not in the
committed pre-registration. They are evidence, and they point one way, but turning that into a scored
claim would need its own pre-registered rung.

`does_not_show`: nothing about time. Nothing about memory traffic or cache locality — an operation
count cannot tell a traversal advantage from a locality advantage. That a cheaper traversal exists
beyond the four declared, or that a larger lattice behaves as this one does. **That this is a
speedup** — it is not. And no promotion.

## Act

`voxmanifold-prereg` holds the quotation and the verdict-set equality, `voxmanifold-structure` the
locality that survives and the manifold that dies, `voxmanifold-baseline` the two baselines and the
cold-start control, `voxmanifold-selftest` the record plants.

The falsifier naming this brief: `voxmanifold-structure` reddens if retirement ever stops rising with
inheritance quality, or if a cheap interior ever appears — which would mean the manifold framing had
become measurable after all, and would reopen a direction this rung closed.
