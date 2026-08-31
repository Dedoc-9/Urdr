<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxstate-geometry -->

# `voxstate` (URDRVXU1) — design brief

*A search experiment needs a space to search. This rung declares one, measures its raw geometry, and
builds no certificate at all.*

## Observe

`voxcond` established one sound, productive certificate — ownership, verified rather than remembered
— and refuted every cheap camera-side condition alongside it. The open question it left is not
whether a certificate can be built but whether **certificate validity has structure**: does it form
connected regions in state space that can be traversed more cheaply than solving each state cold?

Two axes, and only two are available. Position along the corridor and orientation in yaw. The
geometry of this world is a pure hash of its seed, so geometry mutation and streamed-chunk state
cannot be varied without changing `world_digest` and invalidating every frozen record in the tree.
That is a limitation of the corpus rather than of the idea, and it is recorded rather than worked
around — a rung that quietly varied the world would have broken `voxref`'s census to make its own
lattice more interesting.

| order | predecessor | non-adjacent inheritances |
|---|---|---|
| Z0 | none — every state cold | — |
| Z1 | previous in scan order | **3** |
| Z2 | previous in boustrophedon order | 0 |
| Z3 | nearest already-visited neighbour, breadth-first | 0 |

All four are required to be permutations of one state set, so no traversal can win by visiting a
different or smaller lattice. Z1 is kept *precisely* because its row wraps are not adjacent: without
a traversal that sometimes inherits from far away, "adjacency helps" would have nothing to be
measured against.

## Orient

**The measurement immediately killed this rung's first law, and that is the useful part.**

That law demanded the lattice span a wide range of observable distance — near-identical states at one
end, unrelated ones at the other — on the assumption that distance is what a certificate tracks. It
is not:

| | |
|---|---|
| nearest adjacent pair | 4241 of 6912 pixels differ |
| farthest adjacent pair | 6472 of 6912 |

**A quarter of a voxel saturates the observable**, exactly as `voxpath` predicted, because depth is a
continuous function of camera position and a thirty-second of a voxel already moves it almost
everywhere. There is no step size short of zero at which observable distance discriminates.

That is a constraint on the next rung rather than a defect in this one, and a useful one: since all
distances are comparable, **distance cannot confound** a comparison between adjacent and non-adjacent
inheritance. The four traversals are alike in distance — Z1's worst predecessor pair reaches 6480
against Z2's 6420, near enough to be the same number — and differ only in structure. Any difference
the next rung finds between them is therefore structural by construction, and nothing about the
geometry will be secretly explaining its answer.

**And adjacency is declared geometry, never a validity claim.** `voxcond` refuted the whole family of
camera-side predicates and proved them unsound at an eighth of a voxel. Neighbours in this lattice are
neighbours in the declared parameterisation and that licenses nothing about their observables.
`adjacency_is_not_a_validity_claim` *runs* `voxcond`'s refutations rather than citing them, so the
dead family cannot be quietly resurrected as an assumption about this lattice.

## Decide

The prediction for the next rung ships in this commit, one commit before any traversal runs —
`voxcond`'s precedent, and the only mechanism that actually proves a prediction came first. Five
predictions are committed as `spec/attest/voxmanifold-prediction.txt` with their digest pinned as
this rung's golden, and the pre-registration is asserted to carry no verdict row of any kind. One of
the five predicts that **no traversal beats the cold baseline in total operations**, because the
tiled loop the certificate needs costs 1.85× the reference and no rearrangement of inheritance
changes that scaffolding. This experiment answers the structure question, not the speed one.

`does_not_show`: nothing about certificates — not one is built, costed or exploited. Nothing about
time, and no wall clock enters. **That the step sizes are good ones** — a different pair would move
every figure the next rung reports, and its verdicts will be about this lattice. That two axes are
enough to describe a real engine's state; they are what this corpus admits. And nothing is altered.

## Act

`voxstate-lattice` holds the state set, the four orders and the permutation law,
`voxstate-geometry` the saturated distances and the structural difference between the traversals,
`voxstate-prereg` the pre-registration and the dead family, `voxstate-selftest` the record plants.

The falsifier naming this brief: `voxstate-geometry` reddens if observable distance ever stops being
saturated across the lattice — which would mean depth had stopped depending on the camera, and would
reopen the whole family of camera-side predicates `voxcond` closed.
