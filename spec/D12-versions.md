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
| `urdr-field`   | **0.1 (FROZEN)** | 4 field digests (3 FIELDFP + 1 FIELDQ) | reference + `urdr-physics-rs` (ADMITTED 3/3 FIELDFP; FIELDQ reference-only) | this doc |
| `urdr-field` (Marangoni + loop) | **0.1 (FROZEN)** | 3 Marangoni digests + 3 URDRLOOP digests | reference + `urdr-physics-rs` (ADMITTED 27/27) | this doc |
| `urdr-fp-dynamics` (rung 5) | **0.1 (FROZEN)** | 2 URDRFPT1 trace digests | reference + `fp_dynamics_rs` (ADMITTED, Windows/rustc) | this doc |
| `urdr-netcode` (N1) | **0.1 (FROZEN)** | 1 URDRLSTT trace digest | reference + `lockstep_rs` (ADMITTED, Windows/rustc; C99-cross-checked) | this doc |
| `urdr-netcode-rollback` (N2) | **0.1 (FROZEN)** | 1 converged URDRLSTT trace digest | reference + `rollback_rs` (ADMITTED, Windows/rustc; C99 port agrees on golden AND defect digest) | this doc |
| `URDR-WORLD-3` (authored-world format) | **3 (FROZEN as consumed)** | tag-checked canonical scene | consumed by `replay.py --world` / `--fp world` / `load_world.py` | this doc |
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

## The urdr-field v0.1 frozen surface

The scalar-transport bedrock is frozen the same way. Immutable under
`urdr-field 0.1` except through a versioned successor:

1. **Serialization grammar.** `Digest(Field) = SHA-256(canon)` where `canon` is
   `[MAGIC "URDRFLD1"][BACKEND 8B "FIELDFP " | "FIELDQ  "][W u32 BE][H u32 BE]
   [per-cell payload]`. The **backend tag is part of state identity** — `FIELDFP`
   and `FIELDQ` are distinct computations and never share a digest. Cell payload:
   `FIELDFP` = one i64 BE; `FIELDQ` = num i64 BE + den i64 BE (reduced, den > 0).
2. **FixedPoint arithmetic parameters (FROZEN).** Radix **2³²** (Q32.32);
   **round-to-nearest, ties away from zero** (`_rdiv`), applied to every coefficient
   multiply — so every compiler/CPU truncates identically. `FIELD-REFUSE` on i64
   overflow, never a wrap.
3. **The step semantics.** A **conservative flux form** (each edge flux computed
   once, applied +to one cell / −to its neighbor) so total mass is conserved
   EXACTLY even in fixed-point; first-order **upwind** advection; **zero-flux**
   (adiabatic, edge-clamped) boundary; the caller must respect the monotonicity/CFL
   bound `4k + vx + vy ≤ 1` (an out-of-bound scene overflows and refuses).
4. **Backends.** `FixedPoint` (bounded, rounds — the cross-placed real-time path)
   and `Exact` (reuses the physics `Q`, exact, refuses when denominators grow — a
   scoped-tiny, reference-only option). Both are deterministic and cross-placeable;
   the choice trades exactness↔scale, never determinism.
5. **Conformance corpus (4 digests).** `conformance_field.txt`:
   `diffuse, advect, adv_diff` (FIELDFP, reproduced by `urdr-physics-rs`) + `exactq`
   (FIELDQ, reference-only).

Reproducibility (bit-identical across placements) is the invariant future field
work may never compromise; exactness is *not* claimed for FIELDFP (it rounds,
honestly). Surface-tension/Marangoni coupling and adaptive/LOD grids arrive as new
versioned rungs, each down the same ladder.

## The urdr-fp-dynamics v0.1 frozen surface (rung 5 — bounded fixed-point dynamics)

Immutable under `urdr-fp-dynamics 0.1` except through a versioned successor:

1. **Serialization grammar.** `URDRFPD1` state: `magic | each column's Q32.32 words as
   signed i64 big-endian, columns in call order` (`fp_dynamics.state_digest`).
   `URDRFPT1` trace: `SHA-256(magic | the ORDERED per-tick hex digests as UTF-8 text)`
   (`fp_dynamics.trace_digest`) — the hex *strings* are hashed, not raw bytes; this is
   pinned mechanically (see the freeze manifest below).
2. **Arithmetic.** The frozen `FixedPoint` substrate (D9, `field.py`): radix 2³²
   (Q32.32), round-to-nearest ties-away-from-zero (`_rdiv`) on every rational-coefficient
   multiply, `FIELD-REFUSE` on i64 overflow — never a wrap or saturate.
3. **Step semantics.** The goldens pin the whole stepper — bounded PGS contact passes +
   ground-up projection + the sleep clamp (`stack3`), and the Baumgarte feedback on the
   *squared* rod length, sqrt-free (`swing`). Constants (gravity/tick, sleep threshold,
   Baumgarte gain, iteration counts) are part of the frozen behavior: changing any is a
   version bump, because the trace digests change.
4. **Conformance corpus (2 trace digests).** `conformance_fp.txt`: `stack3`, `swing` —
   reproduced by the reference and by `fp_dynamics_rs` (ADMITTED on Windows/rustc).

**Honest scope:** bounded and deterministic, *not* exact — the substrate rounds (stated
in D9). Exactness lives in the certified solvers; this surface trades exactness for
unbounded duration, and refuses on overflow instead of wrapping.

## The urdr-netcode v0.1 frozen surface (N1 — deterministic lockstep)

Immutable under `urdr-netcode 0.1` except through a versioned successor:

1. **The input event.** A 6-tuple of ints `(tick, peer, seq, body, dvx, dvy)`; `(peer,
   seq)` is unique in a valid log and is the identity a receiver dedups on; `dvx/dvy`
   are an additive control impulse in whole Q32.32 units.
2. **The canonical merge.** Exact-duplicate deliveries are DEDUPED (load-bearing);
   each tick's events apply in `(peer, seq)` order. Honest scope: for these *additive*
   impulses order-independence follows from commutativity — the canonical sort is
   hygiene; only dedup is load-bearing. Reorder/duplicate delivery is absorbed;
   a dropped/modified/tick-moved event is a desync.
3. **Serialization grammar.** `URDRLST1` per-tick witness: `magic | per body pos.x,
   pos.y, vel.x, vel.y as Q32.32 signed i64 big-endian` (`lockstep._digest`).
   `URDRLSTT` whole-run trace: `SHA-256(magic | the ORDERED per-tick hex digests as
   UTF-8 text)` (`lockstep.trace_digest`).
4. **The desync law.** `first_desync(a, b)` = the index of the first mismatching
   witness (a length mismatch desyncs at the shorter length; identical chains → none).
   A desync is DETECTED and LOCALIZED, never silent.
5. **Refusal semantics.** The substrate's `FIELD-REFUSE` on overflow — a peer refuses
   rather than wraps. `digest ≠ MAC`: witnesses catch *accidental* divergence, not a
   signing adversary; authenticated inputs arrive as an additive, versioned successor.
6. **Conformance corpus (1 trace digest).** `conformance_netcode.txt`: `arena3` —
   reproduced by the reference and by `lockstep_rs` (ADMITTED on Windows/rustc; port
   logic independently C99-cross-checked).

## The urdr-netcode-rollback v0.1 frozen surface (N2 — rollback as deterministic replay)

Immutable under `urdr-netcode-rollback 0.1` except through a versioned successor:

1. **No new serialization — contractually.** N2 reuses the frozen `URDRLST1` per-tick
   witness and `URDRLSTT` trace laws unchanged. A rollback implementation that needs a
   new wire format is not this version.
2. **The snapshot contract.** A snapshot is the complete Q32.32 state at a tick
   boundary; a restored snapshot MUST reproduce the `URDRLST1` witness pinned at its
   tick (restore is exact, gate-checked). Snapshot cadence `K` and retention `H` are
   **operational parameters, not semantics**: the admitted chain is identical for every
   `K, H` — only the refusal horizon moves.
3. **The rollback law.** A late-but-valid input (tick < head, identity fresh) rewinds
   to the NEWEST retained snapshot at-or-before its tick, voids the provisional
   suffix (frames and newer snapshots), and re-simulates to the present with the
   enlarged input set. The converged chain equals the canonical timeline — the N1
   lockstep oracle over the full log — bit-for-bit; the converged trace golden IS the
   N1 golden by construction.
4. **Refusal semantics.** `ROLLBACK-REFUSE`: the input is older than the oldest
   retained snapshot — rejected WHOLE, the chain untouched. `ROLLBACK-CONFLICT`: a
   second event with the same `(peer, seq)` identity but a different payload (forgery
   or tick-moved replay) — refused naming the identity. An EXACT duplicate is
   absorbed. `digest ≠ MAC` still: identity conflicts are detected; signatures are a
   declared, additive successor.
5. **Conformance corpus (1 converged trace).** `conformance_rollback.txt`:
   `arena3_late3` (the pinned tick+3 late-delivery schedule) — reproduced by the
   reference and by `rollback_rs` (ADMITTED on Windows/rustc), with the apply-at-head
   defect diverging to the same digest (`39326ff9…`) in Rust and the C99 cross-check.

## The URDR-WORLD-3 authored-world format (frozen as consumed)

The editor→runtime world serialization, frozen at the keys the deterministic runtime
*consumes* (a consumed-key change is `URDR-WORLD-4`, never an edit):

1. **Envelope.** JSON, `"format": "URDR-WORLD-3"`. `objects[]`: `{digest, verts:
   [[x,y](,z)…], edges?}` with integer vertices. `instances[]`: `{id, object → an
   object digest, ground_x, ground_z, scale, rot_deg?, body: "dynamic"|"static",
   mass, vel: {x, z}, parent?, local?}`.
2. **The authoring boundary (part of the contract).** Scene composition (float
   place/rotate/scale) is *float authoring* whose result is **snapped to the integer
   grid**; everything the deterministic runtime consumes is integer after the snap.
   Given the integer world, the witness chain / frame digest is the scene's
   deterministic identity on every conforming host.
3. **Consumers.** `replay.py --world` (exact ℚ dynamics), `replay.py --fp world`
   (bounded fixed-point runtime), `load_world.py` (exact perspective projection).
   Unknown keys are inert to the runtime (authoring conveniences), and the format is
   backward-compatible with its consumers as pinned by the canonical scene.
4. **Canonical instance.** `demo/world_highway.json` — its tag is checked mechanically.

## The freeze manifest (checked by the gate)

The declarations above are enforced, not trusted: `tools/specfreeze/freeze_check.py`
re-derives every frozen digest law from the grammar declared here with its own
independent serializers and compares byte-for-byte against the live code
(`spec-freeze` gate stage + `tests/test_spec_freeze.py`), so drift in either the doc
or the code reddens the gate. A corrupted-manifest selftest proves the checker can
redden. One block, machine-readable:

```freeze-manifest
magic URDRFPD1 fp_dynamics state
magic URDRFPT1 fp_dynamics trace
magic URDRLST1 lockstep state
magic URDRLSTT lockstep trace
magic URDRLOOP loop_scenes loop
magic URDRFLD1 field field
corpus tools/physics/conformance.txt 5
corpus tools/physics/conformance_nd.txt 5
corpus tools/physics/conformance_lcp.txt 4
corpus tools/physics/conformance_joint.txt 4
corpus tools/physics/conformance_fp.txt 2
corpus tools/physics/conformance_field.txt 4
corpus tools/physics/conformance_marangoni.txt 3
corpus tools/physics/conformance_loop.txt 3
corpus tools/netcode/conformance_netcode.txt 1
corpus tools/netcode/conformance_rollback.txt 1
format URDR-WORLD-3 demo/world_highway.json
```

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
