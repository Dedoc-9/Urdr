<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D10 — The observer / manifold engine: measured theorem map (capstone)

Status: `CONSOLIDATION` — this document makes **no new claim**. It is the invariant map of
what is already `MEASURED` (both placements) in D5/D8/D9, drawn once so future work does not
re-prove a measured theorem under a new name. Every row it cites is green in `verify.py` on
two named hosts AND reproduced by the independent `urdr-core-rs` kernel (D8 conformance,
29/29 twice, defect caught 13/13, Windows/`rustc 1.96.1`, 2026-07-07). `a map is not a
territory; a capstone is not a new stone`.

## 0. Why freeze now

After the linear-chart generalization, the *provable* core of the observer architecture is
complete: a deterministic numeric substrate, digest identity, the witness firewall, the
atlas injectivity theorem (axis-selection AND integer-linear), observation bound to a
witnessed transition path — all measured on both placements. The remaining directions
either need a genuinely new capability (exact `divmod` → general-n rank), or are host
engineering that *consumes* these invariants (the shared-world runtime), or are chart swaps
that add no new invariant (perspective, curved optics). The risk now is not a missing proof;
it is losing the invariant map by adding examples the measured theorem already implies. This
document is the guard against that.

## 1. The architecture boundary

```
authoritative state
        │
        ▼
witnessed transition history        (deterministic transitions; W = [ᛝ(S0),…,ᛝ(Sn)])
        │
        ▼
digest anchor  ᛝ                    (content identity = state + history)
        │
        ▼
chart family  A = {Πᵢ}              (observers; charts as DATA)
        │
        ▼
injectivity predicate  ∩ᵢ ker(Aᵢ)  (computed, not assumed)
        │
        ├── trivial kernel  → admissible view (separates, reconstructs)
        │
        └── kernel collision → URDR-ASSERT   (refused, never resolved)
```

Three layers, and the boundary between them is the whole design:

- **Kernel** (Layer 1, sealed): values, digests, transition validity, atlas admissibility.
  It owns *authority*, never *appearance*.
- **Observer** (Layer 2, this capstone): charts, projections, reconstruction, the
  injectivity predicate. It produces *views*, never *authority*.
- **Host** (Layer 3, NOT built): networking, scheduling, spatial partitioning, prediction,
  GPU rendering, replication. It *consumes* the invariants; it proves none.

`the kernel never owns a camera or a pixel`.

## 2. The measured theorem

For an admissible chart family `A = {Πᵢ}` over a state domain `X`:

```
Recoverable(A)  ⟺  ∩ᵢ ker(Aᵢ) = {0}
```

The only state-difference invisible to every observer is the zero difference. Two measured
instances of the *same* theorem (both placements):

| Instance | Injectivity certificate | Positive | Falsifier |
|---|---|---|---|
| Axis-selection charts (charts as axis-index data) | `covers(family,n)` — every axis observed by some chart | `atlas_algebra.urdr` | `atlas_algebra_deficient_wrong` (uncovered axis ⇒ kernel collision) |
| Integer-linear charts `Aᵢ(x)=Mᵢx` (charts as matrix data) | square case: `det(M) ≠ 0` (division-free cofactor) | `linear_atlas.urdr` | `linear_atlas_singular_wrong` (det=0 ⇒ kernel vector collides) |

The n=4 hand-picked precursor (`atlas_injective` / `atlas_deficient_wrong`) is the worked
example these generalize; it is not double-counted. Dimension `n` and the family are
**parameters** (data), so 4D/5D/nD, world-streaming, and sensor-fusion are data choices, not
new code.

## 3. Observation bound to an authenticated path

Static consensus (many views, one digest) is *vacuously* enforced by immutability — the type
system forbids a non-pure observer, so it is not a runtime property. The non-vacuous property
is the **binding** of a view to a witnessed transition history
(`witnessed_transition_atlas.urdr`): a rendered frame is admissible only if it reconstructs to
the state whose digest is the authenticated chain endpoint. Two attacks a shared world
actually faces are refused, non-vacuously:

- **View laundering** (`view_launder_wrong`) — a frame of a *different* state carrying the
  real endpoint digest dies `URDR-ASSERT`.
- **Forked history** (`transition_fork_wrong`) — two children of one parent have divergent
  digests and cannot be equated.

`many observers may differ in representation, never in authority`.

## 4. The measured red frontier

Both placements agree not only on accepted digests but on the **accept/reject boundary** — the
part a name cannot fake. The observer-layer falsifiers (all `URDR-ASSERT`, all non-vacuous):
`atlas_deficient_wrong`, `atlas_algebra_deficient_wrong`, `view_launder_wrong`,
`transition_fork_wrong`, `linear_atlas_singular_wrong`. The substrate falsifiers (D9 §5) and
the kernel falsifiers (D8 §3) sit below them. A boundary two independent kernels agree on is
the strongest form of this project's claim.

## 5. What this does NOT show (and the honest next steps)

- **General-n injectivity — CLOSED (reference).** The rectangular `rank[M₁;…;M_k]=n` case is
  now measured: `tools/intla/atlas_injective.py` certifies an over-determined atlas injective
  iff its stacked matrix has **full column rank** (`rank==n`) via the frozen fraction-free
  Bareiss `rank` (`urdr-math` v0.1, the "genuine new capability" this note called for — exact
  integer `divmod` → Bareiss elimination), and returns an exact `nullspace` collision witness
  `v` (`Mv=0`, `v≠0`, so states `0` and `v` are indistinguishable under every chart) when the
  atlas is deficient. Gate stage `atlas_injective` (fullrank / collision / non-vacuity
  self-test). Grade: **MEASURED (reference)** — this is a Python-reference certificate over
  frozen exact math, *not* yet a both-placements result like the two rows in §2; a Rust
  cross-placement of `urdr-math` (and hence this certificate) remains a separate DECLARED item.
- **Reconstruction / inversion — CLOSED (reference).** Recovering `x` from `Mx` is now measured
  as the constructive sibling of injectivity: `tools/intla/atlas_reconstruct.py` returns `x`
  **exactly** (reduced rational `num/den`) via Cramer's rule over the frozen `determinant` on an
  independent square subsystem (no matrix-inverse detour needed — the fraction-free determinant
  suffices), with a self-checking witness `M·num = den·y`. Over-determination is the forgery
  detector: the state solved from `n` rows is verified against **all** `Σk_i` rows, so an
  observation off the column space is refused `INCONSISTENT` and a deficient atlas is refused
  `NOT_INJECTIVE` (state not unique — the injectivity collision). Gate stage `atlas_reconstruct`.
  Grade: **MEASURED (reference)** — a Python-reference certificate over frozen exact math, *not*
  yet a both-placements result; a Rust cross-placement of `urdr-math` remains a separate DECLARED
  item (same as the general-n injectivity certificate above).
- **Perspective / curved / non-linear charts.** A perspective chart `(x,y,z,w) ↦ (x/z, y/z)`
  is a chart *swap* — measurable now that `div` is both-placements — but it adds no new
  *invariant*; it is a renderer feature, graded as such if built.
- **Continuum physics (Marangoni etc.).** A transport module `state_{t+1} = Verify(state_t,
  F(state_t, Δt))` that must *preserve the witness relation* — an application of the measured
  boundary, not a new foundation.
- **The shared-world runtime (Milestone 7).** Rust host; graded by integration tests, not the
  URDR gate. It consumes §2–§3; it proves nothing here.

## 6. Grades

Every claim in §2–§4 is `MEASURED (both placements)` — see the corresponding D5 rows and the
D8 conformance corpus (v6 = atlas injectivity, v7 = atlas algebra, v8 = witnessed transition
atlas, v9 = linear-chart atlas), each ADMITTED by `urdr-core-rs` on the named Windows host.
This document itself is `CONSOLIDATION` — it asserts nothing beyond that map. `Nihil ultrā
probātum`.
