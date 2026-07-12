<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The theorem catalog — what is actually proved, and by what

Short, precise statements, each tied to the evidence that currently supports it.
This document is an **index, not a source of truth**: the graded ledger
([`../spec/D5-ledger.md`](../spec/D5-ledger.md)) governs every grade, the layer
contracts ([`../spec/D11-layer-contracts.md`](../spec/D11-layer-contracts.md)) govern
every obligation, and the versions/freezes ([`../spec/D12-versions.md`](../spec/D12-versions.md))
govern every frozen surface. If this catalog and any of those disagree, this catalog
is the bug. Evidence never exceeds what maturity licenses; a theorem here means *the
gate proves this statement on this code today* — never universal correctness, and
never more than the stated corpus.

Conventions: "×2" = reproduced twice, bit-identically, in fresh subprocesses.
"Defect caught" = a deliberately wrong build/variant provably diverges (the
detector can redden — non-vacuity). "Both placements" = an independent, std-only
implementation sharing no code or SHA-256 with the reference reproduces the digests
on a named host. C99 cross-checks are sandbox instruments validating port logic in
a third language; they are not repo placements.

## Measured theorems

| # | Theorem (scoped statement) | Current evidence |
|---|---|---|
| T1 | **Kernel conformance.** The sealed kernel's accept digests and refusal codes are a property of the specification, not one interpreter. | D8 corpus (36 vectors); `urdr-core-rs` ADMITTED ×2, defect caught. Gate: examples + oracle + rejections stages. |
| T2 | **Exact-math spine, three runtimes.** rank / determinant / floor_divmod + atlas injectivity + exact reconstruction produce identical digests across three languages on two OSes. | 20 digests; `urdr_math_rs` (Windows/rustc) + `urdr_math_c` (Linux/gcc), each ADMITTED ×2, defect caught. Gate: `math-conformance` + selftest. |
| T3 | **Renderer frame reproducibility (corpus-scoped).** `State → Framebuffer` is bit-identical across two placements for the pinned 2D/3D-depth/perspective scenes. | 10 frame digests; `urdr_render_rs` ADMITTED ×2, defect caught 10/10. Does **not** show the full frame law: blending and perspective-correct interpolation remain DECLARED (D11 §4). |
| T4 | **Certified physics solves.** Contact LCP λ (complementarity-certified), joint solves (J·v = 0, rank(A) uniqueness), collisions and CCD produce witnesses or typed refusals, cross-placed. | 18 scene digests over 4 corpora; `urdr_physics_rs` ADMITTED ×2, defect caught 18/18. Gate: `physics*` stages with conservation + refusal selftests. |
| T5 | **Reactive continuum conservation.** Field transport conserves mass exactly in fixed point; the two-way field↔body loop conserves the momentum ledger exactly through LCP contact resolution. | `field`/`marangoni`/`field_coupling`/`field_body_loop` stages; `urdr_physics_rs` ADMITTED 27/27 ×2. FIELDQ backend reference-only (stated). |
| T6 | **Bounded fixed-point dynamics.** The frozen Q32.32 substrate time-steps settling stacks and swinging pendulums deterministically, refusing on overflow — reproducibility-by-frozen-rounding, not exactness. | URDRFPT1 trace goldens (2); `fp_dynamics_rs` ADMITTED ×2, defect caught. Gate: `physics_fp` + settle invariant + selftest. |
| T7 | **The exact/bounded boundary.** Two admitted numeric regimes (exact ℚ with certificates; bounded Q32.32 with frozen rounding) plus typed refusal; crossings explicit; determinism never traded. | D11 §4b (normative contract); enforced by every regime-E/regime-B gate stage plus the rejection fixtures for the refusal codes. |
| T8 | **Lockstep transcript law (N1).** Peers exchanging inputs only reproduce one URDRLST1/URDRLSTT witness chain; reordered/duplicated delivery is absorbed. | `arena3` golden; `lockstep_rs` ADMITTED ×2, defect caught (Windows/rustc; C99-cross-checked). Frozen: `urdr-netcode 0.1`. |
| T9 | **First-desync localization.** A dropped/modified/mis-timed input diverges the chain, and the divergence is named at the first mismatching tick — never silent. | `netcode-desync-selftest` (N1), `test_rollback.py`/`test_worldstep.py`/`test_worldpeer.py` localization falsifiers; each requires the clean run NOT to desync. |
| T10 | **Rollback convergence (N2).** A late-but-valid input rewinds to a canonical snapshot and replays to the *canonical* chain bit-for-bit, at any snapshot cadence; beyond-horizon and identity-conflict inputs are typed refusals. | Converged golden ≡ the N1 golden; `rollback_rs` ADMITTED (Windows/rustc); Python/Rust/C99 agree on the defect digest (`39326ff9…`). Frozen: `urdr-netcode-rollback 0.1`. |
| T11 | **Authenticated admission (N3).** Only an input whose Lamport-OTS envelope verifies against a pre-committed roster pin enters the transcript; a verified log reproduces the canonical chain unchanged; four forgery shapes refuse typed. | Roster root + signed-chain goldens; `authinput_rs` ADMITTED (Windows/rustc); Python/Rust/C99 agree on the forge anchor (dvx+423). Shows the **mechanism**, not operational key secrecy. Frozen: `urdr-netcode-auth 0.1`. |
| T12 | **Authored worlds run under the same laws (N4).** A frozen URDR-WORLD-3 export becomes deterministic netcode state; the runtime's tick with no statics reproduces frozen N1's chain bit-for-bit (the equivalence pin); the authoring boundary is typed (WORLD-REFUSE, never a silent round); instance order is world identity. | Highway golden + arena equivalence; `worldstep_rs` ADMITTED (Windows/rustc); three-language defect anchor (`9c0ad7c5…`). JSON loader reference-gated. Frozen: `urdr-netcode-world 0.1` (+0.2/0.3 additive, digest-preserving). |
| T13 | **World identity law (N5).** URDRWPN1 pins the complete runtime world — including statics an initial witness cannot see — and a pin mismatch refuses before any tick runs. | `world_pin` golden; falsifier proves two worlds differing only in a static share frames[0] but not the pin; both placements reproduce the pin. Frozen: `urdr-netcode-worldpeer 0.1`. |
| T14 | **The composed end-to-end contract (N5).** Same authored world + same authenticated transcript + same initial snapshot → the identical witness chain or the same typed refusal; no intermediate divergence silently persists. | Converged late+signed golden ≡ the N4 golden at two cadences; `worldpeer_rs` ADMITTED (Windows/rustc); Python/Rust/C99 agree on all five anchors including the defect (`d5bc484b…`). Complete per AGENTS rule 11. |
| T15 | **The freeze is machine-checked.** Every frozen digest law, corpus count, and format tag declared in D12 is re-derived independently and compared byte-for-byte on every gate run; doc↔code drift reddens the gate. | `spec-freeze` stage: 6 digest laws + 13 corpora + 1 format tag + a corrupted-manifest selftest; `tests/test_spec_freeze.py`. |
| T16 | **Weave schedule-invariance.** Commuting proposals produce one world digest across any permuted arrival schedule; forks are refused, conflicts isolated. | `world_host` corpus v12; `actors_one_digest`, `structural_history` examples; regional verdict ≡ global verdict (locality result). |
| T17 | **Observer recoverability.** `Recoverable(A) ⟺ ∩ᵢ ker(Aᵢ) = {0}`, computed as a data-parameterized certificate with exact reconstruction or typed refusal. | D10; injectivity + reconstruction digests inside the 20-vector math corpus (T2), cross-placed three-runtime. |

The gate enforcing all of the above: **318 unit falsifiers + per-layer conformance
stages, each with a non-vacuity self-test, + 45 typed rejection fixtures + the
tamper self-test** — `PYTHONHASHSEED=0 python verify.py` → `GATE PASSED`, ×2,
on Windows and Linux. Ten std-only Rust placements, one C99 third runtime.

## Design targets (not theorems — do not cite as proved)

Full frame law (blending, perspective-correct interpolation) · Coulomb friction,
rotation, convex shapes, sphere-sphere CCD · body-body contact in the authored
runtime (N4.1 — instance mass is loaded and inert) · N2/N3 composition falsifiers
beyond the N5 canonical scenario · operational key management and cross-session
replay protection · interest management and regional authority · gameplay scripting
· metatheory (progress/preservation, no-inflation soundness) remains CONJECTURED.

## The development path (agreed, in order)

1. **Phase 1 — close simulation capability: N4.1 body-body contact.** No
   architectural content; a capability rung on the established ladder. Wakes the
   inert instance mass.
2. **Phase 2 — observability: the debugger reads authority.** Witness-chain
   timeline, first-desync visualization, λ/impulse inspection, momentum/energy
   accounting, rollback visualization, digest diffing, refusal explanation — all
   *surfacing recorded authoritative state*, never reconstructing it. The editor
   remains a consumer; it inherits guarantees, it does not create them.
3. **Phase 3 — world scale, contract first.** The regional-authority contract
   (regional witnesses that compose to the global witness, or refusal) must be
   written and falsifiable **before** streaming/large-world implementation begins.
   If the invariant cannot be stated precisely, the implementation waits. Seed:
   the measured regional-locality result (T16).
4. **Phase 4 — gameplay as admitted consumers.** Scripting that bypasses the
   deterministic authority would make every guarantee beneath it conditional;
   scripting admitted into the same deterministic/refusal framework strengthens
   it. Urðr the language is the intended scripting layer — gameplay logic as
   programs the existing gate admits.
5. **Every future subsystem rides the same ladder** (AGENTS rule 11): prototype →
   specification → red-first falsifiers → reference → corpus → independent
   placement → admission → freeze. Complete means reproduced, not merely passing.

`Nihil ultrā probātum` — the catalog lists what survived the attempt to falsify it,
and nothing else.
