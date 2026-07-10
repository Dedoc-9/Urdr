# tools/physics — exact dynamic mechanics (urdr-physics, rungs 1 & 2)

The jump from **static geometry** (rigidity certificates) to **dynamic
mechanics**: a deterministic, time-linked equation of motion, exact over ℤ.
**Rung 1** is 1D (`rational.py`, `dynamics.py`); **rung 2** is n-dimensional —
2D & 3D balls (`vecq.py`, `dynamics_nd.py`), the step toward game / VR; **rung 3**
is the exact **n-contact constraint solver** (`contact_lcp.py`) — simultaneous
contacts, resting stacks, frictionless constraint propagation.

## Rung 3 — the exact n-contact LCP (simultaneous contacts)

Pairwise rungs resolved one contact at a time; real worlds have coupled
simultaneous contacts (a resting stack, a multi-body impact). That is a linear
complementarity problem — find normal impulses `λ ≥ 0` with `w = Aλ + b ≥ 0` and
`w·λ = 0` — and the solver *certifies* the answer rather than assuming it: it
returns a `λ` that provably satisfies every LCP condition, or it **refuses**.

Exact and direct: normals are **un-normalized** (rational for spheres and walls,
so `A`,`b` stay rational — no square root), and the solve is an **active-set**
method (enumerate candidate active sets in a canonical order, solve the equality
subsystem by exact rational elimination with a deterministic pivot, return the
first feasible set) — **no iterative loop, no tolerance, no heuristic ordering**
in the authority path. A singular subsystem is skipped; a degenerate/inconsistent
LCP `PHYS-REFUSE`s. Momentum is conserved by construction. The canonical
constraint-propagation witness: a resting `n`-stack solves to `λ = [n, n−1, …, 1]`
(the bottom contact carries the whole stack) and every body comes exactly to rest
— pinned in `conformance_lcp.txt`, gated by `physics_lcp`, falsified in
`tests/test_contact_lcp.py`. Scope: frictionless normal contacts, small contact
counts (enumeration is exponential — Lemke/principal pivoting is the same exact
answer, faster, a later optimization). Friction, rotational inertia, and a Rust
second placement are later rungs.

    (X_t, V_t) + F  --semi-implicit Euler + exact 1-contact LCP + CCD-->  (X_t+1, V_t+1)

## Rung 2 — exact 2D & 3D vector dynamics

One dimension-agnostic implementation covers both 2D and 3D (a `Vec` is a tuple
of exact rationals). The key result: a **ball collision response is exact in any
dimension without a square root** — the contact normal is the center-difference
vector `d`, and the `|d|` from projecting the relative velocity onto the unit
normal cancels the `|d|` from the impulse direction, leaving only `d·d` (exact):

    P = -(1+e) (v_rel · d) / ( (d·d)(1/m₁ + 1/m₂) ) · d          (exact over ℚ)

Momentum is now a conserved **vector**; kinetic energy is the discriminating
witness (conserved iff elastic, strictly decreasing iff inelastic); the
**tangential** velocity is untouched (correct oblique physics). Proven for 2D and
3D, head-on and oblique, in `tests/test_physics_nd.py` and the `physics_nd` gate.

### The exactness boundary (honest)

A **continuous** sphere-sphere time-of-impact solves `|d₀ + w·t|² = (r₁+r₂)²`, a
quadratic whose root carries a square root and is therefore generally
**irrational** — exact rational CCD is *not* available for curved-vs-curved
continuous collision. So ball-ball collision uses **discrete** overlap detection
(exact: `d·d ≤ (r₁+r₂)²`) + exact response, while exact CCD (the anti-tunneling
witness) is provided for **linear** impact conditions — a ball vs an axis-aligned
wall, whose TOI is a rational linear solve. That boundary is a real property of
exact arithmetic, recorded rather than hidden.

No floating point anywhere — positions, velocities, and impulses are exact
rationals (`rational.Q`, gcd-reduced over ℤ). Any i64 overflow is `PHYS-REFUSE`,
never a wrap. Consumes `urdr-math`'s discipline; touches no core; no new glyph.

## The four layers, at rung-1 scope

- **State-space expansion (momentum).** State is phase space `(X, V)` with mass;
  momentum `p = Σ m·v` is an exact rational. Integrator: semi-implicit
  (symplectic) Euler.
- **Deterministic constraint solver (LCP kernel).** `resolve_contact` solves the
  1×1 LCP for a single normal contact exactly: `w = M z + q`, `w,z ≥ 0`, `w·z = 0`
  — an impulse is applied **only** when approaching, is non-negative, and leaves
  the bodies separating (elastic) or resting (plastic).
- **Conservation-law invariants (falsifiers).** Momentum is conserved
  *structurally* by the equal-and-opposite impulse — so a **wrong** impulse still
  conserves momentum; the **kinetic-energy witness** is what catches it
  (conserved iff elastic, strictly decreasing iff inelastic). That is the
  non-vacuity control.
- **CCD as a geometric witness.** `time_of_impact` finds the **exact rational**
  time an edge meets an edge, so a fast body **cannot tunnel** a thin wall:
  `step` advances to the fractional impact time, resolves, then integrates the
  remainder.

## What is proven (rung 1)

Each scene's post-step **state digest** (`SHA-256` of the canonical serialization
of the exact rational `(X, V)`) is a reproducible witness, pinned in
`conformance.txt` and checked twice by the `physics` gate stage; conservation
witnesses hold on elastic/inelastic contacts; the CCD tunneling case is caught;
overflow refuses. Falsifiers in `tests/test_physics.py`.

## What is NOT claimed (honest scope)

Rung 1 is **1D, single earliest contact per step, restitution ∈ [0,1]**, and is
*implementation-agreement on a stated corpus within the reference placement*. It
is **not** continuum physical accuracy, **not** completeness for all scenes, and
**not** yet a second-placement (cross-language) result. The following are the
declared next rungs:

- **general n-contact LCP** (Lemke / principal pivoting over exact ℚ) — the full
  deterministic constraint solver for simultaneous contacts;
- **2D / 3D** bodies, rotational inertia;
- **cross-placement** (a Rust `urdr-physics-rs` reproducing the state digests,
  the D8 move applied to dynamics).

## Files

- `rational.py` — exact rational over ℤ (`Q`, gcd-reduced, i64-refusal).
- `dynamics.py` — `Body`, `integrate`, `resolve_contact`, conservation
  witnesses, `time_of_impact`, `step`, `state_digest`.
- `phys_scenes.py` / `conformance.txt` — the corpus + pinned state-digest goldens
  (named `phys_scenes`, not `scenes`, so it never collides with `render/scenes.py`
  on the gate's shared sys.path).
- `../../tests/test_physics.py` — the falsifiers.
- Gate: the `physics` stage in `verify.py`.

## Run

    python3 tools/physics/scenes.py       # print each scene's post-step state digest
    python3 -m unittest tests.test_physics
    python3 verify.py                     # full gate (includes the physics stage)

`(X_t, V_t) + F → (X_t+1, V_t+1)`, exact and reproducible — for this corpus, in
this placement.
