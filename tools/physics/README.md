# tools/physics — exact dynamic mechanics (urdr-physics, rung 1)

The jump from **static geometry** (rigidity certificates) to **dynamic
mechanics**: a deterministic, time-linked equation of motion, exact over ℤ.

    (X_t, V_t) + F  --semi-implicit Euler + exact 1-contact LCP + CCD-->  (X_t+1, V_t+1)

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
