<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D12 — Subsystem versions & the physics v1.0 freeze

Status: **MEASURED** (a record of what is frozen, not a claim). This document
gives every certified subsystem an explicit **semantic version** and **corpus
version**, so future changes are tracked without ambiguity, and it declares the
**physics v1.0 freeze**: the serialization, witnesses, digest law, refusal codes,
public API, and conformance corpus are immutable except through a versioned
successor. Future capability *extends*; it never silently mutates admitted
behavior. `a frozen interface is the precondition for a second implementation`
(D8) — and physics now has one (`urdr-physics-rs`), so it is time to freeze.

## Version manifest

| subsystem      | semver | corpus | placements agreeing (bit-identical) | evidence |
|----------------|--------|--------|-------------------------------------|----------|
| `urdr-core`    | 1.0    | D8 v1–v12 (36 vectors) | reference ☉ + `urdr-core-rs` | D8 |
| `urdr-math`    | 0.1    | oracle-tested          | reference (+ witness cross-placement) | D5 |
| `urdr-render`  | 1.0    | 8 frame digests (4 2D + 4 3D-depth) | reference + `urdr-render-rs` (ADMITTED 8/8) | D11 §4 |
| `urdr-physics` | **1.0 (FROZEN)** | 18 scene digests (4 corpora) | reference + `urdr-physics-rs` | this doc |
| `urdr-field`   | 0.1    | 4 field digests (3 FIELDFP + 1 FIELDQ) | reference + `urdr-physics-rs` (3 FIELDFP; FIELDQ reference-only) | D5 |
| capabilities R4 | 1.0   | network_read + registry | reference | `network_bridge` |

`semver` = the public API/behaviour version; `corpus` = the pinned
conformance-vector set. A change that would alter any admitted digest requires a
**major** bump and a new corpus version; a purely additive capability is a
**minor** bump that adds vectors without touching existing ones.

## The physics v1.0 frozen surface

The following are immutable under `urdr-physics 1.0`. Any change here is a new
major version, not an edit:

1. **Serialization grammar (digest law).** `Digest = SHA-256(canon)` where `canon`
   is the byte layout with these magics and fields:
   - `URDRPH1`  (1D)   : `magic | i32 count | per body { x.n,x.d, r.n,r.d, v.n,v.d (i64 BE ×6), m (i64 BE) }`
   - `URDRPN1`  (n-D)  : `magic | i32 dim | i32 count | per ball { x.c[] (n,d), r (n,d), v.c[] (n,d), m }`
   - `URDRLCP1` (LCP)  : `magic | i32 count | λ[] (n,d) | w[] (n,d)`
   - `URDRJNT1` (joint): `magic | i32 |vels| | i32 |λ| | vels.c[] (n,d) | λ[] (n,d)`
   All integers signed big-endian; rationals reduced with denominator > 0.
2. **Exact substrate.** Exact rational `Q` over ℤ, gcd-reduced, i64-bounded; **no
   float, no clock, no RNG, no iterative tolerance, no heuristic ordering** in the
   authority path.
3. **Refusal semantics.** `PHYS-REFUSE` on: i64 overflow, division by zero, zero
   denominator, non-positive mass, a degenerate/inconsistent LCP (no feasible
   nonsingular active set), or a singular constraint system (redundant/conflicting
   joints). Refusal is total — never a wrapped, saturated, or guessed result.
4. **Witnesses / certificates.** Momentum conservation (structural), the
   kinetic-energy witness (elastic exact / inelastic non-increasing), the LCP
   complementarity certificate (`λ,w ≥ 0 ∧ λ·w = 0`), the joint certificate
   (`Jv_new = 0`), and `rank(A)` as the uniqueness certificate.
5. **Public API.** `dynamics` (Body, integrate, resolve_contact, time_of_impact,
   step, state_digest); `dynamics_nd` (Ball, resolve_spheres, toi_wall, step,
   state_digest); `contact_lcp` (lin_solve, solve_lcp, complementary, delassus,
   resolve, lcp_digest); `articulated` (build_system, solve, satisfied,
   distance_row, pin_rows, joint_digest). Signatures and semantics are frozen.
6. **Conformance corpus (18 pinned digests).** `conformance.txt` (5),
   `conformance_nd.txt` (5), `conformance_lcp.txt` (4), `conformance_joint.txt`
   (4) — each reproduced by the reference and by `urdr-physics-rs`.

## What may still change under 1.0

Only *additive, digest-preserving* work: more adversarial property tests
(`tests/test_physics_properties.py`), performance optimization that leaves every
digest identical (roadmap step 7), and documentation. New capability (friction,
rotation, convex bodies, continuous sphere-sphere CCD) arrives as **new versioned
subsystems or a physics 2.0**, each following the same ladder: prototype →
reference proof → conformance corpus → independent second placement → admission →
freeze.

## Honest scope

Freezing certifies *stability of the admitted surface*, not universal
correctness. The digests are agreements on the stated corpora across two
placements; the property suite raises confidence beyond them; neither claims
continuum physical accuracy nor completeness for all inputs. `admitted ≠ trusted`.
