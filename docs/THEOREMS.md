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
| T15 | **The freeze is machine-checked.** Every frozen digest law, corpus count, and format tag declared in D12 is re-derived independently and compared byte-for-byte on every gate run; doc↔code drift reddens the gate. | `spec-freeze` stage: 6 digest laws + 20 corpora + 1 format tag + a corrupted-manifest selftest; `tests/test_spec_freeze.py`. |
| T16 | **Weave schedule-invariance.** Commuting proposals produce one world digest across any permuted arrival schedule; forks are refused, conflicts isolated. | `world_host` corpus v12; `actors_one_digest`, `structural_history` examples; regional verdict ≡ global verdict (locality result). |
| T17 | **Observer recoverability.** `Recoverable(A) ⟺ ∩ᵢ ker(Aᵢ) = {0}`, computed as a data-parameterized certificate with exact reconstruction or typed refusal. | D10; injectivity + reconstruction digests inside the 20-vector math corpus (T2), cross-placed three-runtime. |
| T18 | **Body-body contact stays deterministic and conservative (N4.1).** An opt-in **sqrt-free Q32.32 impulse** (the exact `d/\|d\|` cancellation) collides authored dynamic bodies: x-momentum conserved *exactly*, closing velocity reverses (restitution), and the frozen contact-OFF surface is byte-identical. | `netcode-world-contact` (`collide2` golden); asymmetric-impulse defect breaks momentum; **cross-placed** — C99 `worldregion_c` + Rust `worldregion_rs` reproduce the `seam2` monolith bit-for-bit. |
| T19 | **Regional composition = the monolith witness (D16 — the Seam Composition Theorem).** For any valid partition by integer x-seams, each region evolving its interior by the frozen N4.1 tick from admitted read-only ghosts alone, the deterministic reunification reproduces the monolithic `URDRLST1`/`URDRLSTT` witness **bit-for-bit** — with **no new witness class**. | `netcode_region`: `seam2` golden == monolith, partition-invariance over 6 partitions, dropped-boundary divergence localized to the contact tick, malformed-partition `REGION-REFUSE`. **FROZEN** `urdr-netcode-region 0.1`; three placements (Python + C99 + Rust) agree incl. the failure mode. Answers D13 §C8 (no glyph needed). |
| T20 | **Criticality is deterministic, conservative, and self-limiting (urdr-criticality).** A branching-diffusion field (Galton-board flux-form transport, keff multiplication, Doppler feedback): transport conserves population EXACTLY; keff=1 stationary / keff<1 decays / keff=2 unregulated `FIELD-REFUSE`s at the bound; and Doppler feedback regulates a supercritical `k0=2.0` to a bounded steady state — reactor stability, reproducibly. | `criticality`: Galton golden `064f7cfc…` + Doppler steady-state golden `8439d5a6…`; exact-conservation over 50 gens; the non-vacuity defect (drop Doppler → explode → `FIELD-REFUSE`). MEASURED reference; bounded regime; cross-placement DECLARED. Honest scope: 1D, one-group, rational Doppler (physical √T Doppler is irrational → refuse regime). |
| T21 | **The admission law is a real abstraction, not a description (D17 + toric code).** Every gated detector satisfies one meta-contract — `(Dom, Inv, W, ~, R)` with a decidable domain, exact witnessed invariant, invariance on a declared equivalence class, and total typed REFUSE — enforced mechanically by the `invariant_detectors` lint (declared roles, not name-inferred). Its truth-test: admit a detector from a domain the project never touched under the *same* six conditions. The toric code (`k = dim H₁` over 𝔽₂ = logical qubits = 2·genus) was admitted with **no flex** to the contract. | `invariant_detectors` (10 detectors, each 4 roles, + a non-vacuity selftest); `toric` (`torus3` k=2 witness `391e49e5…`, genus-invariance, wrong-homology defect, non-complex `TORIC-REFUSE`). New exact substrate GF(2) (`gf2.py`); toric + rigidity cross-placed (C99 + Rust). MEASURED. Honest scope: `k` exact always; distance exact only for the toric family (general min-distance is NP-hard → REFUSE). |
| T22 | **A diagram-valued invariant admits unchanged (persistent homology).** The persistence barcode of a filtered simplicial complex over 𝔽₂ (standard boundary-matrix reduction) is exact and admits under D17 as the first NON-scalar invariant — no flex to the contract. The equivalence checked is exact barcode equality; metric stability (bottleneck distance) is a separate theorem, not claimed. | `persim`: circle barcode `bb17a756…` (b₀=1, b₁=1), reorder-invariance + the disk (filled H₁) distinguished, un-reduced-pairing defect, non-monotone `PH-REFUSE`. MEASURED (reference). |
| T23 | **A classical winding invariant admits unchanged, with a theorem-backed corpus (W1, D19 §5).** The winding number of a closed integer polyline about an off-curve probe — exact signed ray-crossing count (half-open rule, orientation determinants), a crossing-list witness that recounts to the invariant, cyclic-rotation + integer-subdivision `~`-invariance with orientation reversal as a documented covariance, total `WIND-REFUSE` — admits under D17 as the 8th detector with no flex to the contract. Its corpus is the first THEOREM-BACKED one: pinned integer samples of Loewner-1948 curves — `(f′, f)`, `(f″−f, f′)`, and the cubic-family `(f‴−f′, f″−f/4)` (P = x³−x, Q = x²−¼, interlacing) — wind non-negatively at all 35 pinned probes, adversarial near-curve probes included; two goldens pin `w = 2` (the `(f″−f, f′)` probe and the cubic family's doubly-wound core). | `winding`: 6 scene goldens ×2 (`conformance_winding.txt`), the 35-probe non-negativity row, parity-defect selftest (gate can redden), 4/4 typed refusals; `tests/test_winding.py` (13 falsifiers). MEASURED (reference); **cross-placed** — `winding_rs` (std-only Rust, own SHA-256) reproduces GOLDEN AND DEFECT, ADMITTED ×2 bit-identically on a Linux host; Windows owner attestation pending. Honest scope: corpus-scoped facts about frozen integer objects — the smooth theorem is provenance, not a gate claim. |
| T24 | **Tellegen orthogonality admits as the first graph-theoretic detector (D19's second constraint instrument).** On a shared directed multigraph, ANY integer potential against ANY conservative integer flow pairs to `S = Σ vₖ·iₖ = 0` exactly (Tellegen 1952) — the universal constraint above every constitutive law, where KCL checks one assignment on one network. Dom is decided exactly (per-node KCL; a leaky flow is refused NAMING its node and exact imbalance); the per-edge product witness recounts to the pairing; `S` is invariant under gauge shift, simultaneous (edges, flow) permutation, and reorientation-with-negation. | `tellegen`: 4 scene goldens ×2 (bridge ×2, cycle5, a parallel-edge/self-loop multigraph), the 3×3 any-p × any-i grid (9/9 zero — corpus-scoped; the 1952 theorem is provenance, not a gate claim), the orientation-blind defect nonzero on all 4 scenes, 4/4 `TELL-REFUSE`; `tests/test_tellegen.py` (11 falsifiers). MEASURED (reference); cross-placement not claimed. Honest scope: `S ≡ 0` on all of Dom by theorem — maximally PARTIAL as a separator; the discriminating power is the boundary. |
| T25 | **The Integer Scalar Potential Layer Theorem (URDRISPL1).** The terrain studio's seven layers are one authority-rooted manifold: a single exact-integer scalar potential Φ: ℤ²→ℤ (`heightfield`) whose certified projections — Consumer (`stance`), Observer (`gaze`), Transcript (`drive`), Horizon (`traj`) — derive behavior, observation, and temporal evolution, and a Firewall (`view_witness`) certifying the DECLARED Presentation cites Φ, all WITHOUT altering it. Measured cross-layer, beyond any single layer's stage: SINGLE SOURCE (the declared `terrain_view3d.html` embeds exactly Φ's live digest), OUTWARD FLOW (a one-cell perturbation of Φ moves every downstream layer — each genuinely depends on it), MEMBRANE (no downstream op alters Φ; a forged citation is refused). | `layertheorem` (URDRISPL1): 4 rows (7-strata presence, single-source, outward-flow + membrane, conservation); composite theorem digest `36829b10…`; `tests/test_layertheorem.py` (7 falsifiers). MEASURED — the URDR terrain INSTANTIATION of the theorem. Honest scope: the general theorem over an ARBITRARY integer manifold is DECLARED (this certifies the instantiation, not the universal claim); the manifold is exact-integer and deterministic throughout and division-free DOWNSTREAM (`//`-free, tokenizer-asserted across `drive`/`gaze`/`traj`/`stance`), but the authority's FBM uses one exact-integer normalization (`raw·height_scale // rawmax`, rawmax = Σamp·65535, **not** a power of two) beside its Q16 shifts — so the epilogue's "entirely division-free" is narrowed to "float-free, exact-integer, deterministic; shift-only and `//`-free downstream; one exact-integer normalization at the authority." Presentation is DECLARED (certified only by the firewall's citation). |

The gate enforcing all of the above: **761 unit falsifiers + per-layer conformance
stages, each with a non-vacuity self-test, + 45 typed rejection fixtures + the
tamper self-test** — `PYTHONHASHSEED=0 python verify.py` → `GATE PASSED`, ×2,
on Windows and Linux. 24 std-only Rust placements, 13 C99 runtimes.

## Design targets (not theorems — do not cite as proved)

Full frame law (blending, perspective-correct interpolation) · Coulomb friction,
rotation, convex shapes, sphere-sphere CCD · N2/N3 composition falsifiers
beyond the N5 canonical scenario · operational key management and cross-session
replay protection · the D16 scale-out falsification workloads — **dynamic
repartitioning** (seams that move on a live tick), **interest-management / authority
migration**, and a **distributed authority graph** (regions on separate hosts,
delayed ghosts) · gameplay scripting · the **D19
abductive-gauntlet contract** (the hypothesis boundary: proposals recorded at the līmes,
elimination only by admitted D17 detectors, survival confers no grade — the PIPELINE remains
a written contract with no proposer, no recorded batch, and no `ABDUCT-REFUSE` in the tree;
its first rung, the `W1` winding detector, has graduated to theorem T23 above) ·
metatheory (progress/preservation,
no-inflation soundness) remains CONJECTURED. *(Body-body contact (N4.1) and the
regional-authority contract (D16) have graduated to theorems T18/T19 above.)*

## The development path (agreed, in order)

1. **Phase 1 — close simulation capability: N4.1 body-body contact. ✓ DONE** (T18,
   cross-placed, contact-OFF surface byte-identical). Woke the inert instance mass.
2. **Phase 2 — observability: the debugger reads authority.** *Partly landed* — A/B
   replay compare with first-desync visualization; recorded rigidity-verdict badges;
   and the **field-level desync localizer** (`observe.first_field_desync`, gated
   `netcode_field_desync`): names the exact body+field of a divergence in witness order,
   with the honest diagnostic that in an exact deterministic engine the cause is an
   upstream input or a non-conforming placement, never rounding. Remaining: λ/impulse
   inspection, momentum/energy accounting, rollback visualization, refusal explanation,
   and the editor *view* over the field localizer — all *surfacing recorded authoritative
   state*, never reconstructing it. The editor remains a consumer.
3. **Phase 3 — world scale, contract first. ✓ CONTRACT LANDED (D16, FROZEN, T19).**
   The regional-authority contract was written, falsifiable, and *measured* before any
   large-world implementation — and answered its own question: regional witnesses
   compose to the global witness with no new witness class (three placements agree).
   What remains is the *scale-out implementation* pursued as falsification of the seal
   (dynamic repartitioning → migration → distributed authority), each recorded in
   D5 § "Evidence Against C8." Seed: the measured regional-locality result (T16).
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
