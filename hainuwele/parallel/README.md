<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `hainuwele/parallel/` — parallel substrates

Structures explored **alongside** the Euclidean arc, never disturbing it. The arc's geometry
modules (`heightfield`, `perception`'s supercover, `hitbox`'s AABB and integer aim-ray,
`chunkload`'s demand sets) all assume Euclidean ℤ². Anything that changes that assumption is built
here as a *parallel* substrate with its own gate stage, so the existing pinned goldens never move.

## Queued: `URDRCHB1` — the discrete Chebyshev net (designed, not built)

**Motivation.** The arc establishes order-independence *by checking*: `commute` builds both orders
and compares them; `rannull` proves parallel equals every serial; `nway` does it for N! orders.
Discrete integrable systems obtain the same property **by construction** — multidimensional
consistency ("consistency around the cube") makes the diamond commute because of what the equation
*is*, not because a prover confirmed this instance. Bianchi permutability is its algebraic form,
and it is exactly the arc's "zero rebases."

**The structure.** A discrete Chebyshev net is `r: ℤ² → ℝ³` with `(Δ₁r)² = f(n₁)`,
`(Δ₂r)² = g(n₂)` — opposite edges of each quad equal in squared length, each depending on one
lattice index only; equivalently `Δ₁₂r ∥ N̂`. Two facts make this a fit for this repository:

1. The condition is stated on **squared** edge lengths, which this arc already computes in exact
   integers everywhere. The *discretisation* is what makes it exact — this is not a numerical
   approximation of a smooth surface.
2. `f` and `g` are **arbitrary functions of one lattice index each** — the discrete residue of the
   reparametrisation freedom `u → U(u)`, `v → V(v)` on asymptotic lines. That is the
   arbitrary-function (gauge) symmetry Noether's *second* theorem requires, and which a uniform
   grid does not have.

**Why Dini.** Dini's surface has constant Gaussian curvature `K = −1`, and the Dini family arises
from the 1-soliton (kink) solution of sine-Gordon — pseudospherical surfaces correspond to
sine-Gordon solutions, and Bäcklund transformations generate new ones from old.

**Open before building — stated honestly.** Noether's second theorem is an *iff*: no
arbitrary-function symmetry, no identity. The Chebyshev freedom is *geometric*; whether it descends
to a **variational** symmetry of a discrete Lagrangian on this net is unestablished, and the whole
programme rests on it. A negative answer is a valid result and would close the line cleanly.

**References.** Schief, *Discrete Chebyshev nets and a universal permutability theorem*;
Bobenko & Suris, *Discrete differential geometry: consistency as integrability*; Hydon & Mansfield,
*Extensions of Noether's Second Theorem: from continuous to discrete systems* (Thm 5.1:
`D̃ᵅᵣ Ẽᵅ(L) ≡ 0`, identically, off-shell).
