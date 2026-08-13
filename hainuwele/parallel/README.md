<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `hainuwele/parallel/` — parallel substrates

Structures explored **alongside** the Euclidean arc, never disturbing it. The arc's geometry
modules (`heightfield`, `perception`'s supercover, `hitbox`'s AABB and integer aim-ray,
`chunkload`'s demand sets) all assume Euclidean ℤ². Anything that changes that assumption is built
here as a *parallel* substrate with its own gate stage, so the existing pinned goldens never move.

## `URDRPRS1` — the present probe (`present_probe.rs`, wall-clock class, deliberately ungated)

The first §3 instrument for the visible loop: a real Win32 window, a real present path, QPC stamps
at every `sealframe` instant software can reach, and a click-triggered white flash so a phone
camera can measure the one segment software cannot. Raw FFI, std-only, integer nanoseconds
throughout; the entry door refuses unknown flags; `--defect` plants a 50 ms stall the instrument
must catch in its own numbers or exit red. Like `bench.py` it reads a wall clock and therefore
never enters the gate — its LOG is what the repo will grade, under the `sealframe-honesty`
admission pattern, and a log without `--host` cannot graduate anything.

First named-host reading (Ally X, 2026-08-13, v0): frame work p50 0.50 ms / p99 2.03 ms at
1280x729 against an 8.33 ms slot — and the instrument's first catch was ITSELF: 176 of 723
deadlines missed with 0.5 ms of work, the classic Sleep(1)-under-15.6ms-timer-resolution pacing
defect. v0.1 requests 1 ms resolution, logs whether it was granted, and records lateness as a
magnitude rather than a count. The red-first plant was caught on the same host before any real
run was trusted.

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

## Built, and DELIBERATELY UNGATED: `URDRRPI1` — `rpimm.py`, the degree-dimension problem for RP^n

**Status.** Built with its own falsifiers and its own runner; **no stage in `verify.py`**, by design.
Run it with `python3 hainuwele/parallel/rpimm.py`. It stays ungated until there is either a
constructive family that survives the corrected tangent-space test or an obstruction genuinely beyond
the blockwise case. Ungated means it **can rot**, and that is stated rather than hidden — the same
treatment `bench.py` gets for wall-clock. Selfcheck: 16/16.

**What it is.** The question is whether a bounded-degree *even* polynomial map can immerse `RP^n` in a
target dimension approaching the topological one, and the module holds the corrected machinery for
asking. Exact rational arithmetic throughout; no float ever decides a rank.

**Three errors pinned as witnesses, because each was made in the design that preceded it.**

1. **A parity category error, not a missing proof.** The original construction was antipodally ODD and
   was asked to induce a map on `RP^n`. It cannot: descending to `S^n/{±1}` needs `Φ(-x) = Φ(x)`, and
   an odd map satisfying that is identically zero. Only EVEN maps descend, so the linear block `x` is
   inadmissible from the start rather than "lost to the quotient". Measured `(True, False, True)`.
2. **The identity block made the original obstruction vacuous.** The argument was "one block's
   differential dies, therefore the rank drops." Measured, at exactly the points where `DQ_k = 0` the
   map with an identity block still has FULL rank `n` — `n = 2,3,4,5` all give `n`, not `n-1`. A
   vanishing sub-block is not a rank deficit until you count what survives.
3. **"Positive-dimensional" failed at a boundary case.** The vanishing locus is exactly
   `S^(n-|B_k|)`, so a *proper* block missing one coordinate gives `S^0` — two points. The exact
   dimension formula replaces the adjective; `(n,|B|) = (5,4) → S^1` but `(5,5) → S^0`.

**The lemma that survives, in its general form.** For an even variable-separable map with blocks
partitioning the coordinates and every monomial of degree ≥ 2, let `Z` be the union of blocks
vanishing *entirely* at `x`. Every direction supported in `Z` is tangent and in the kernel, so

    rank DΦ|T_xS^n  ≤  n − |Z|

Measured on 6 cases, holds on 6, **attained** on 6, and below `n` on 6 — so it is a bound that bites
rather than a slack inequality. It recovers both special cases: block-supported points give
`rank ≤ |B_1| − 1` (measured `(2,1)→0`, `(3,2)→1`, `(4,2)→1`, `(5,3)→2`), and `{x_Bj = 0}` gives
`rank ≤ n − |B_j|`. **The obstruction is factorization through independent coordinate projections —
locality — not the degree:** raising the degree from 2 to 4 to 6 leaves the rank at 2 against a needed
4. That is what later constructions must avoid.

**The rank test was the most dangerous error available.** The immersion condition is the rank of the
differential *restricted* to `T_xS^n`. Two sound routes are implemented and cross-checked — project
onto a tangent basis, or stack the normal row `xᵀ` and subtract one, since
`ker([A; xᵀ]) = ker(A) ∩ T_x` gives `rank(A|T_x) = rank([A; xᵀ]) − 1` identically. They agree on 12
of 12 cases, and a **mutation probe** proves the agreement can fail: a variant using the ambient basis
disagrees on 12 of 12, so the cross-check is measuring something (L23).

**And the naive ambient test is off by exactly one, for a reason.** Euler's relation `A x = d·Φ(x)`
puts one unit of rank in the radial direction, verified on every case. Measured, there are points
where the ambient rank reaches `n` while the true tangent rank is `n−1`: `(n, ambient, tangent)` =
`(3,3,2)`, `(4,4,3)`, `(5,5,4)`. **The naive test certifies an immersion that is not one.** Kept live.

**The algebraic certification has a real-versus-complex trap.** Sound direction only:
`I_minors + I_sphere = (1)` ⟹ immersion. The converse fails, because the Nullstellensatz is about
algebraically closed fields while immersion is a real question. Witness in exact Gaussian integers:
`f = x₀² + x₁² + 2x₂² + 2x₃²` is positive definite so `V_R(f)` misses the sphere entirely, yet
`z = (1,1,0,i)` gives `Σz_i² = 1` and `f(z) = 0`. A pipeline reading "ideal ≠ (1) ⟹ not an immersion"
returns a false negative here.

**Positive control, and the gap that shows where the difficulty is.** The Veronese returns rank exactly
`n` at every point tested for `n = 2…5`, so the rank routine is measuring separability and not a bug.
Its target dimension is `(n+1)(n+2)/2` = 6, 10, 15, 21 — **quadratic**, against topological targets
linear in `n`. The open question is whether any bounded-degree family closes a quadratic-to-linear gap.

**Refutations only, never a certified positive.** A refutation is exact from ONE witness: if the
tangent rank drops below `n` anywhere, the map is not an immersion. A positive is not available by
search, so the subset census reports `RPIMM_REFUTED` or `RPIMM_CANDIDATE` and **never "immersion"** —
enforced in the return vocabulary, not in a comment. This is the same asymmetry `autoroute` inherited
from view determinacy (L27), arriving from a different direction. Measured over monomial subsets of the
degree-2 Veronese at `n = 2`: size 3 → **20 refuted, 0 candidates** (a real negative), size 4 → 13
refuted, **2 candidates**, size 5 → 3 refuted, 3 candidates.

**Two invariants, kept separate.** `m_d^imm(n)` and `m_d^emb(n)`. Conflating them would let the
Veronese's *embedding* bound masquerade as an immersion bound.

**Open, stated honestly.** The asymptotics of `m_d` are untouched — this module only makes the question
askable. The subset search ranges over MONOMIAL subsets rather than general linear projections, so its
CANDIDATE verdicts are weaker than they look. The point sets used for refutation are pinned and finite.
Whether this optimization problem is already known under another formulation has **not** been
established by a literature review, so it is a natural question here and not a claimed open problem.
