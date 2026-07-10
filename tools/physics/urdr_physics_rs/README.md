<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# urdr-physics-rs — the independent physics placement (D8 cross-placement, for dynamics)

One self-contained Rust file (`urdr_physics.rs`), std-only, **no crates, no cargo,
hand-rolled SHA-256** (from `urdr-core-rs`, FIPS-checked at startup). A faithful
re-implementation, in a **different language / compiler / runtime**, of the four
exact physics rungs, judged solely by whether it reproduces the four physics
conformance corpora:

| corpus | file | MAGIC | scenes |
|--------|------|-------|--------|
| 1D dynamics    | `../conformance.txt`       | `URDRPH1`  | free, gravity, elastic, inelastic, ccd_tunnel |
| 2D/3D dynamics | `../conformance_nd.txt`    | `URDRPN1`  | head2d, oblique2d, inelastic2d, oblique3d, wall2d |
| n-contact LCP  | `../conformance_lcp.txt`   | `URDRLCP1` | rest2, rest3, separating, corner2d |
| articulated    | `../conformance_joint.txt` | `URDRJNT1` | rod, pendulum, chain3, triangle |

This is the physics analog of `urdr-core-rs` (state) and `urdr-render-rs`
(pixels): it turns *"the momentum/contacts/joints are deterministic in our
reference"* into *"they are bit-identical across independent implementations"* —
so the physics digests are a property of the specification, not of Python.

## Grade — read this before believing anything

- The Rust source existing: `IMPLEMENTED / DECLARED`.
- **Port logic cross-checked:** the exact algorithm here (its rational `Q`
  arithmetic, byte-for-byte serialization, scene setups, and all four solvers)
  was mirrored in Python and reproduces **all 18 goldens** — but that is still
  the reference language.
- **Convergence (`urdr-physics-rs`): `SPECULATIVE` until the run below is green on
  a host with a toolchain.** An authoring sandbox without `rustc` cannot measure
  it. `declared ≠ verified`; `admitted ≠ trusted`.

## The run protocol (red-first — order matters)

PowerShell, from the repo root, `rustc >= 1.56` (any edition-2021 toolchain):

```powershell
# 0. build (plain rustc; no cargo, no crates)
rustc -O --edition 2021 -o urdr_physics.exe tools\physics\urdr_physics_rs\urdr_physics.rs

# 1. RED FIRST — every corpus digest MUST diverge under a bumped MAGIC (exit 0 = caught)
.\urdr_physics.exe --defect

# 2. the verdict — run it TWICE, identically
.\urdr_physics.exe
.\urdr_physics.exe
```

Expected: `--defect` prints `[PASS] defect:<scene> divergence caught` for all 18
and `URDR-PHYSICS-RS: defect caught`; the plain runs print
`[PASS] accept:<scene> …` for all 18 and `URDR-PHYSICS-RS: ADMITTED`, identically
both times.

`URDR-PHYSICS-RS: ADMITTED` twice + defect caught ⇒ **physics cross-placement
MEASURED** on that named host: a second, independent implementation reproduces
every physics digest (1D dynamics, 2D/3D momentum, exact LCP, articulated joints),
and the harness can redden. Paste the output back and the D5/D11 grade flips from
`SPECULATIVE` to `MEASURED`.

## What this establishes / does not

- **Does:** all 18 physics digests are reproduced by an implementation sharing no
  code, language, or SHA-256 with the reference — the D8 reproducibility theorem
  extended from state digests and frame digests to *physics* digests.
- **Does not:** add capability (friction, rotation, convex shapes, sphere-sphere
  CCD remain DECLARED), nor claim continuum accuracy.

## Files

- `urdr_physics.rs` — the independent physics (Q, Vec, 1D/nD/LCP/joints) + embedded
  corpora + `--defect`.
- Reference: `../dynamics.py`, `../dynamics_nd.py`, `../contact_lcp.py`,
  `../articulated.py`; contract: `spec/D11-layer-contracts.md` §3.5.
