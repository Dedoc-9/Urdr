<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D5 — Boundaries ledger (every claim graded)

Grades: **maturity** `IMPLEMENTED` / `SCOPED` / `SPECULATIVE` × **evidence** `MEASURED` /
`DECLARED` / `N/A`. Evidence never exceeds maturity's ceiling — the same ladder the
language enforces, applied to the language's own claims. `MEASURED` below means: a
falsifier exercising the capability is green in `verify.py` on a named host (see
`docs/transcripts/green.txt`); it never means universally proven.

## Capability inventory (current: v0.7.1)

| Capability | Maturity | Evidence | Where falsified |
|---|---|---|---|
| Core lexicon: 21 glyphs, glyph⇄digraph identity | IMPLEMENTED | MEASURED | `tests/test_hygiene.py` (pair-by-pair subTests) |
| Formatter `fmt` (ASCII → glyph, token-stream preserving) | IMPLEMENTED | MEASURED | `tests/test_hygiene.py` |
| Lexical hygiene: NFC, closed alphabet, confusables named, invisibles rejected | IMPLEMENTED | MEASURED | `tests/test_hygiene.py`, `examples/rejected/confusable.urdr` |
| Static no-inflation S1 (ladder) | IMPLEMENTED | MEASURED | `tests/test_no_inflation.py`, `examples/rejected/inflate_static.urdr` |
| Static no-inflation S2 (MEASURED unwritable) | IMPLEMENTED | MEASURED | `examples/rejected/evidence_unearned.urdr` |
| Grounded mintable only via ᛞ (S3) + witness required structurally | IMPLEMENTED | MEASURED | `tests/test_no_inflation.py` (mint + latch tests) |
| Dynamic ladder at the mint (ᛞ on non-IMPLEMENTED refused) | IMPLEMENTED | MEASURED | `examples/rejected/verify_unlicensed.urdr` |
| Conflict ↯ on failed verification, never averaged | IMPLEMENTED | MEASURED | `tests/test_no_inflation.py` |
| Dynamic latch URDR-INFLATE-DYN (armed, unreachable if checker sound) | IMPLEMENTED | MEASURED | `tests/test_no_inflation.py::TestDynamicLatch` |
| Membrane: pure ☽, fresh-store ☿, exact ↩ (digest-identical) | IMPLEMENTED | MEASURED | `tests/test_lens_laws.py`, `examples/lens_roundtrip.urdr` |
| Lens laws: put-get exact; get-put up to lineage w/ exact ↩ recovery | IMPLEMENTED | MEASURED | same; deviation stated in D1 §8 |
| Content addressing: canonical bytes → SHA-256, sorted, order-free | IMPLEMENTED | MEASURED | `tests/test_determinism.py` (store order, glyph/digraph one-digest) |
| α-normalized λ canon (De Bruijn in canon only; free names stay named) | IMPLEMENTED | MEASURED | `tests/test_determinism.py` α-tests; `docs/transcripts/r1a_alpha_normalization.txt` (red-first record) |
| List prelude `push`/`cat`/`nth` (fuel-charged copies, typed failures) | IMPLEMENTED | MEASURED | `tests/test_prelude_lists.py` (9 falsifiers incl. fuel and bounds) |
| Graded algebra: ℤ₂ grading closure (64 pairs) + Cl(3) relations {ei,ej}=2δij (9 pairs), verified by evaluation, ᛞ-sealed; wrong-relation program dies | IMPLEMENTED | MEASURED | `examples/z2_grading.urdr` (⊢64), `examples/clifford_relations.urdr` (⊢9), `examples/rejected/clifford_wrong.urdr` (URDR-ASSERT), `tests/test_graded_algebra.py`. Algebra only — not physics |
| Provenance walk ᛃ (ancestor digests, nearest first; agrees with iterated ↩) | IMPLEMENTED | MEASURED | `tests/test_provenance.py`, `examples/lineage.urdr` |
| Deterministic actors `weave`: canonical order = sort by (target, ᛝ(payload)) per tick — pure function of the message multiset; one digest across permuted schedules; actor-local no-inflation cage | IMPLEMENTED | MEASURED | `tests/test_actors.py` (8 falsifiers), `examples/actors_one_digest.urdr` (⊢37), `examples/rejected/actor_overclaim.urdr` (URDR-VERIFY-UNLICENSED inside the handler) |
| Persistence līmes: runner snapshots with digest re-verification; Grounded/λ refused; cross-run anamnesis reaches the fresh root's address | IMPLEMENTED | MEASURED | `tests/test_snapshot.py` (6 falsifiers incl. tamper + 3-process identity) |
| TLA+ model of membrane laws (view-stutter, put-get, ana-exact, lineage) | IMPLEMENTED | DECLARED | `spec/membrane.tla` + `.cfg` written; NOT TLC-checked by the gate (Java outside stdlib law). Upgrades to MEASURED only if TLC joins CI |
| Verbose keyword profile (12 reserved words; three spellings, one token stream, one digest) | IMPLEMENTED | MEASURED | `tests/test_verbose.py` (incl. reserved-bind rejection and fmt words→glyphs) |
| Compiler as placement: closure compiler (`--via compiled`) admitted per gate run only by digest match vs ☉ on the full corpus; singular kernel (one mint, one prelude, one weave); tick-for-tick fuel parity; defect path (`--via defect`) must be rejected somewhere or the gate reds | IMPLEMENTED | MEASURED | `tests/test_oracle.py` (6 falsifiers), `verify.py` oracle stage (admissions + defect self-test, permanent) |
| Rhombohedral lattice falsifier: C₃ permutation closure, R³=I, Gram identity, diagonal invariance, orbit-average consolidation onto the diagonal (user-directed conversion, D1 §12b); wrong-fixation claim dies | IMPLEMENTED | MEASURED | `examples/rhombo_lattice.urdr` (⊢11), `examples/rejected/rhombo_wrong.urdr` (URDR-ASSERT), `tests/test_lattice.py` (4 falsifiers incl. both-placements agreement) |
| Capabilities (R4): I/O & external state, nothing ambient — unforgeable `Capability`/`CapSet`/`EffectPlan` (runner-minted only; no source syntax; codec-refused as data); reads = recorded inputs loaded once through the one codec, digest-verified, replayed bit-identically, inside content identity; writes = effect-plans executed at the līmes after success, validate-all-then-write-all (no partial world edit; outbox rule: result value or nested lists only); `caps` a protected runner input, not a store; `URDR-CAP` on ungranted or misused authority; kernel-dispatched, so both placements share one semantics | IMPLEMENTED | MEASURED | `tests/test_capability.py` (17 falsifiers; suite proven non-vacuous by two injected defects each caught then reverted), `examples/caps_roundtrip.urdr` (⊢ 42 + executed effect with lineage), `examples/rejected/cap_ungranted.urdr` (URDR-CAP), gate examples+oracle stages grant-aware (`.grants` sidecar; granted write target must exist after the run) |
| In-language capability-gated persistence (R4): write capabilities move the runner līmes into the value discipline — a program persists by RETURNING a plan it was granted the authority to make; `--save-store` (R2c, runner-owned) remains as the runner's own door | IMPLEMENTED | MEASURED | `tests/test_capability.py::TestEffectLimes` (execution, fail-closed, all-or-nothing, Grounded refused outward, buried-plan inert, no effect on a failed run) |
| Import-by-digest modules (R5): offline dependencies addressed by the SHA-256 of canonical source bytes; `vendor/` store + `urdr.lock` manifest, gate-verified; wrong pin/tampered file refused STATICALLY (`URDR-PIN`), unvendored/unpinned refused (`URDR-MODULE`); module value reference-evaluated so placements agree; import cycles unconstructible by content-address. Byte-level: `source-hash ≠ definition-hash` (rename/format-invariance is the SCOPED strengthening) | IMPLEMENTED | MEASURED | `tests/test_modules.py` (13 falsifiers; non-vacuity re-proven by a live pin-check defect caught then reverted), `examples/modules_demo.urdr` (⊢ 42, vendored λ library), `examples/rejected/module_wrong_pin.urdr` (URDR-PIN), `examples/rejected/use_unvendored.urdr` (URDR-MODULE), gate `modules` stage (lockfile≡vendor + mis-pin self-test) |
| Centering / quotient invariant over ℤ (D1 §18, user-directed conversion): M = nI−J sealed by evaluation — M·1=0 (all-ones in ker), M²=nM (idempotent up to scale), scaled orthogonal split n·x=Mx+Jx with ⟨Mx,Jx⟩=0 and |Mx|²+|Jx|²=n²|x|², mean-zero contrasts; wrong-projection (M²=M) dies. Exact integer algebra, no floats. The neijuan/gauge reading (Sym(U)⊋Sym(C)) is docs-provenance ONLY, certified by no test (signum≠rēs); as a social claim it is SPECULATIVE/N/A | IMPLEMENTED | MEASURED | `examples/centering_quotient.urdr` (⊢6), `examples/rejected/centering_wrong.urdr` (URDR-ASSERT), `tests/test_centering.py` (6 falsifiers) |
| VoI decision gate (`tools/voi_gate/` — a SEPARATE tool: float, not the integer core, not sealed by `verify.py`): `Decision = [value_per_bit·VoI − Cost > ρ]`; VoI = mutual information `I(X;O)` in bits (≥0, expected — the single-observation-negativity fix); dimensionally honest via an explicit bits→cost exchange rate; η = V/(V+Co) flow-efficiency; a decision ledger collects (decision, outcome) as its falsifier surface | IMPLEMENTED | MEASURED | `tools/voi_gate/test_voi_gate.py` (13 falsifiers; gate goes GREEN and RED; margin bites; non-vacuity re-proven by a flipped-inequality defect caught then reverted). Own runner, NOT verify.py |
| VoI gate *improves software outcomes* (GREEN actions prevent failures; RED ones save effort) | SPECULATIVE | N/A | requires longitudinal deployment data; `Pipeline.calibration()` collects it but no data exists yet — `declared ≠ verified`, `built ≠ adopted` |
| Evidence transition law (D1 §19): an action earns a claim only by a recorded state transition; an observation buying ≥1 bit (`2·|kept|≤|before|`, integer, uniform-prior) can be ᛞ-sealed, zero-gain dies. Extends `claim≤evidence` to `claim-transition≤measured-delta`. Float ΔH bits = voi_gate provenance, not sealed | IMPLEMENTED | MEASURED | `examples/evidence_transition.urdr` (⊢1), `examples/rejected/evidence_unpurchased.urdr` (URDR-ASSERT), `tests/test_evidence.py` (6 falsifiers incl. zero-delta→Conflict, unbuilt→URDR-VERIFY-UNLICENSED) |
| `transition_witness` (D1 §19) — FIRST library function, ASCII by the glyph budget: dual of ≟ (asserts a real transition, returns witness store `{from,to}`); NEVER mints Grounded (ᛞ alone does); zero-delta refused `URDR-DELTA-UNEARNED`. Glyph deferred to a later review (final artifact of the proof trail, not the start) | IMPLEMENTED | MEASURED | `examples/transition_witness.urdr` (⊢1), `examples/rejected/transition_unearned.urdr` (URDR-DELTA-UNEARNED), `tests/test_transition.py` (6 falsifiers; guard-removal defect caught then reverted) |
| Glyph review (D1 §20): a falsifiable promotion event — a glyph is earned as a LOSSLESS alias of a proven operation, never declared; the review can reject (`URDR-GLYPH-NOT-EARNED`). First glyph earned: `⟿` (U+27FF, `\tw`) for `transition_witness` — three spellings, one digest; confusables/core-collision/non-lossless/missing-provenance all refused | IMPLEMENTED | MEASURED | `tools/glyph_review.py`, `tests/test_glyph_review.py` (6 falsifiers incl. lossless three-spelling proof + four rejection modes) |
| Foreign placement oracle **harness** (R6a): a foreign implementation admitted as another placement iff its digest = the ☉ reference, else refused (`URDR-PLACEMENT-DIVERGENCE`; Rust instance `URDR-RUST-DIVERGENCE`) — the differential oracle (§14b) generalized to any substrate; no foreign code trusted, only agreement. Separate tool, own runner, stdlib-only. Does NOT assert any Rust impl agrees — that is the row below | IMPLEMENTED | MEASURED | `tools/foreign_placement/test_foreign_oracle.py` (3 falsifiers: agreeing admitted, diverging reddens, no-digest errors) |
| **Independent Rust kernel `urdr-core-rs` (Stage 4, D8)**: one self-contained, std-only Rust file — hand-rolled SHA-256, no crates, no cargo — implementing the five D8 §1 obligations (canon→SHA-256 byte grammar, immutable transition, ᛞ mint, deterministic replay, transport rejection) and nothing more; ADMITTED against the frozen conformance vectors: 4/4 accept digests bit-identical to ☉, 4/4 rejects refused `URDR-ASSERT`, **twice identically**; non-vacuity: a deliberately-defective build (`--defect`, Int canon tag corrupted) caught 4/4 (LESSONS L5); 18 unit vectors — every canon path incl. α-normalized λ bodies, captured-builtin closures, store parent-links, the witness mint — generated from ☉ by `gen_vectors.py`, green serially. Scope: agreement on THESE 8 vectors on ONE named host (Windows, `rustc 1.96.1` stable-x86_64-pc-windows-gnu, 2026-07-07); own runner, not `verify.py`; whole-corpus admission through `foreign_oracle.py` is the SCOPED strengthening. `admitted ≠ trusted`; `these vectors ≠ the language` | IMPLEMENTED | MEASURED | `tools/urdr_core_rs/urdr_core.rs` (`conformance` mode + `--defect` red-first + `rustc --test`, 18 falsifiers), `tools/foreign_placement/conformance.txt` (frozen targets), `tools/urdr_core_rs/gen_vectors.py` (vector provenance from ☉) |
| Per-generator equivariance corpus (oracle localization): the differential oracle (§14b) checked PER language generator — each probe's `reference ≡ compiled ≡ golden` (the commuting square commutes for that generator) AND the built-in `+`-defect placement diverges on exactly the generators that exercise `+` (localization); a non-commuting square, a mislocalized defect, or a defect that breaks nowhere reddens the gate | IMPLEMENTED | MEASURED | `examples/oracle_generators/` (5 probes + goldens + MANIFEST), `verify.py` oracle_generators stage; non-vacuity proven by three injected defects (wrong golden, mismarked localization, dropped `+`-probe) each caught then reverted |
| Manifold equivalence under an invariant witness: a finite complex as integer lists; χ = V−E+F (Euler characteristic, label-invariant). Safe transforms (vertex relabel, Pachner 2-2 flip) give DIFFERENT digests but EQUAL χ — equivalence under the witness (`≟`); false transforms (puncture χ 1→0, disconnected merge χ 1→2) change χ and die `URDR-ASSERT`. Exact integer combinatorics, not geometry (`signum ≠ rēs`); χ is a COARSE witness — strengthened to the Betti vector below | IMPLEMENTED | MEASURED | `examples/manifold_equivalence.urdr` (⊢4), `examples/rejected/manifold_puncture_wrong.urdr` + `manifold_merge_wrong.urdr` (URDR-ASSERT) |
| Sheaf gluing / Čech obstruction: local sections over a loop-cover with overlap transitions gᵢⱼ ∈ ℤ glue to a GLOBAL section iff the winding class (signed loop-sum, an integer H¹) vanishes — `≟(loop, 0)`; Case 1 (local agreement, GLOBAL failure = nonzero monodromy) dies `URDR-ASSERT`. The cohomological DUAL of the chain-complex boundary law (§22, ∂∂=0) | IMPLEMENTED | MEASURED | `examples/sheaf_gluing.urdr` (⊢0), `examples/rejected/sheaf_monodromy_wrong.urdr` (URDR-ASSERT) |
| Holonomy / transport-history identity (#10): a frame transported around a loop returns to the same base POSITION (`≟` on the viewed `pt`) yet is a DISTINCT object — Urðr's digest is already state+history (measured: two edit-paths to the same field give different digests; provenance `ᛃ` differs), and the holonomy element itself is a computed transport sum witnessed by `≟`; a false holonomy-equivalence claim (same base point, different holonomy) dies `URDR-ASSERT` | IMPLEMENTED | MEASURED | `examples/holonomy_witness.urdr` (⊢3), `examples/rejected/holonomy_collision_wrong.urdr` (URDR-ASSERT) |
| Witness strength — Betti vector refines χ: the Euler characteristic is a lossy compression `χ = Σ(−1)ᵏβₖ`, so a torus (β=(1,2,1)) and a cylinder (β=(1,1,0)) collide at χ=0; Euler–Poincaré ties each β to real face-counts, the coarse χ-witness collides, and the finer Betti-vector witness separates them. Which invariant is the contract is the programmer's choice — the witness must be strong enough for the identity claimed | IMPLEMENTED | MEASURED | `examples/manifold_betti_refinement.urdr` (⊢4), `examples/rejected/manifold_chi_too_coarse_wrong.urdr` (URDR-ASSERT) |
| Temporal invariant / transactional evolution: a conserved quantity carried THROUGH a discrete evolution — each tick proposes an integer affine delta, the contract commits it iff the invariant `Q` is preserved else reverts to the prior state; over N ticks an unlawful injection is reverted, `Q(final)=Q(initial)`. The buildable heart of a tri-partite `(O,W,E)` engine — witness read from state, effect proposed separately, `W ∉ E`. Reduces to `\fo` (fold) + `≟` + `?` — no new primitive | IMPLEMENTED | MEASURED | `examples/temporal_invariant.urdr` (⊢ [6,[5,0,1]]), `examples/rejected/temporal_drift_wrong.urdr` (URDR-ASSERT) |
| Projection under-determination (Yoneda / anamorphosis refutation, by construction): two DISTINCT 3D affine maps (identity vs a z-shear) share the SAME 2D projection yet differ in 3D — one projection's kernel hides a whole family, so it does NOT uniquely encode the map. Yoneda is faithful over the WHOLE category (all probes, incl. `1_X`); a restricted lower-dim subcategory is not dense. `truth under a chosen invariant ≠ the totality` | IMPLEMENTED | MEASURED | `examples/projection_underdetermined.urdr` (⊢ [[3,1],1]), `examples/rejected/projection_collapse_wrong.urdr` (URDR-ASSERT) |
| Depth perception (constructive complement of projection under-determination): a SECOND spanning view recovers the depth one view lost — two orthogonal projections `π_xy, π_xz` determine the 3D point (kernels meet only at 0), so `recon` round-trips, and the depth view SEES the z-shear the front view was blind to. An incomplete (non-spanning) set fails to reconstruct (`URDR-ASSERT`). Tested as a primitive candidate → it is the LENS round-trip (§8) over a complete witness set, `≟`-verified — no new primitive | IMPLEMENTED | MEASURED | `examples/depth_perception.urdr` (⊢ [[3,1,2],[3,1],1]), `examples/rejected/depth_incomplete_wrong.urdr` (URDR-ASSERT) |
| Observer atlas injectivity (well-posedness made EXPLICIT; generalizes depth_perception to n=4): a chart family `A={Π_i}` determines the state IFF its charts jointly span the coordinates — `A(S1)=A(S2) ⟹ S1=S2`. The SPANNING atlas `{p_xy,p_zw}` (all four axes) SEPARATES distinct states (injective), RECONSTRUCTS via the lens round-trip (§8), and each chart is a witness-carrying frame binding its DIFFERENT image to the ONE authoritative digest `ᛝ(s)` (multi-observer consensus — a renderer/camera/LOD may vary freely while every observer agrees on one digest). A DEFICIENT (non-spanning) atlas COLLIDES two distinct states, so claiming injectivity dies — non-vacuous (a spanning atlas does not collide). The observer/rendering layer's first result: observation is referentially transparent, and an atlas is sufficient ONLY when it spans (the well-posedness condition, encoded explicitly, not assumed). Reuses charts + recon + `ᛝ`; no new primitive, no glyph; distinct from depth_perception (that was one recovery example — this is the injectivity biconditional with the spanning condition falsified) | IMPLEMENTED | MEASURED (both placements) | `examples/atlas_injective.urdr` (⊢ [1,1,[3,1,4,1],1]), `examples/rejected/atlas_deficient_wrong.urdr` (URDR-ASSERT, non-vacuous); cross-placement MEASURED — `urdr-core-rs` ADMITTED 22/22 twice, defect caught 10/10, Windows/`rustc 1.96.1` (corpus v6, 2026-07-07) |
| General atlas algebra (Milestone 6 — the theorem PARAMETERIZED): the chart family is DATA (a list of axis-index charts) and injectivity is a COMPUTED predicate `covers(family,n)` — a fold deciding whether every axis is observed by some chart, which for axis-selection charts IS the intersected-kernel condition `∩ᵢ ker(Aᵢ)={0}`. Dimension n and the family are PARAMETERS (fixture at n=5), so 4D/5D/nD/world-streaming/sensor-fusion become data choices, not new code. A covering family CERTIFIES injectivity (covers=1), SEPARATES a witness pair, and RECONSTRUCTS; a DEFICIENT family's computed kernel COLLIDES two distinct states so claiming injectivity dies (non-vacuous). Generalizes 5B's hand-picked atlas to the atlas-as-data theorem — the engine's reusable spine. General for axis-selection charts; general LINEAR charts (matrix rank) = SCOPED strengthening. Reuses folds + nth + range; no new primitive, no glyph | IMPLEMENTED | MEASURED (both placements) | `examples/atlas_algebra.urdr` (⊢ [1,1,[3,1,4,1,5]]), `examples/rejected/atlas_algebra_deficient_wrong.urdr` (URDR-ASSERT, non-vacuous); cross-placement MEASURED — `urdr-core-rs` ADMITTED 24/24 twice, defect caught 11/11, Windows/`rustc 1.96.1` (corpus v7, 2026-07-07) |
| Witnessed transition atlas (Milestone 6.5 — the bridge to an evolving world): COMPOSES the digest witness-chain (cf. lineage), replay determinism (cf. manifold_runtime), and the atlas algebra (M6). A state evolves S0→S1→S2 by deterministic transitions; the witness chain W=[ᛝ(S0),ᛝ(S1),ᛝ(S2)] records each digest; a covering atlas observes the ENDPOINT and its reconstruction is PROVENANCE-BOUND — ᛝ(recover(A,S2))=W[2]. The genuinely-new content is the BINDING (observation tied to an authenticated transition path), NOT the parts (already MEASURED): view-laundering (a frame of a different state claiming the endpoint digest) and forked history (same parent, divergent digest) are both refused — the multiplayer anti-cheat: a client cannot pass off a fake state as authoritative. Reuses folds + nth + ᛝ; no new primitive, no glyph | IMPLEMENTED | MEASURED (both placements) | `examples/witnessed_transition_atlas.urdr` (⊢ [1,1,[2,2,4,1,5]]), `examples/rejected/view_launder_wrong.urdr` + `transition_fork_wrong.urdr` (URDR-ASSERT, non-vacuous); cross-placement MEASURED — `urdr-core-rs` ADMITTED 27/27 twice, defect caught 12/12, Windows/`rustc 1.96.1` (corpus v8, 2026-07-07) |
| Linear-chart atlas generalization (the last kernel proof): the atlas injectivity theorem lifted from axis-selection to arbitrary integer LINEAR charts `Aᵢ(x)=Mᵢx` (axis-selection = the special case of selection matrices). Injective IFF the stacked matrix has trivial kernel; for the square case this is `det(M)≠0`, computed by the DIVISION-FREE 3×3 cofactor expansion (the core has no division). A full-rank M certifies injectivity (det≠0) and separates a witness pair; a SINGULAR M (det=0) sends a nonzero kernel vector to 0 and collides two states, so claiming injectivity dies (non-vacuous). Perspective, sensor-fusion, and arbitrary integer projections are now instances of ONE theorem. General n (fraction-free/Bareiss rank) and reconstruction (inversion, needs division) = SCOPED strengthening. Reuses folds + nth + range + len; no new primitive, no glyph. **Future proof noted**: general-n injectivity needs exact integer `divmod` → fraction-free (Bareiss) rank — a real extension, not yet built | IMPLEMENTED | MEASURED (both placements) | `examples/linear_atlas.urdr` (⊢ [1,2,1,[4,5,7]]), `examples/rejected/linear_atlas_singular_wrong.urdr` (URDR-ASSERT, non-vacuous); cross-placement MEASURED — `urdr-core-rs` ADMITTED 29/29 twice, defect caught 13/13, Windows/`rustc 1.96.1` (corpus v9, 2026-07-07) |
| urdr-math v0.1 — the deterministic exact-integer math library (Layer-2, seed of `urdr-math`): exact `floor_divmod`, Bareiss `rank`/`det`/`nullspace`, `gcd`/`extended_gcd`/`modinv`, `transpose`/`matmul` — deterministic (same input → same output), i64-bounded with overflow-as-REFUSAL (larger = a bignum substrate, later). Bareiss is deterministic MATH, not search: it lives in the math library, held to the same proven→cross-placement→grade discipline as `urdr-core-rs`; the sealed language stays frozen. Three layers: research PROPOSES / math COMPUTES / kernel CERTIFIES | IMPLEMENTED (library) | algorithm-proven — one runner `tools/intla/test_urdr_math.py` green (divmod 60k, rank 40k, det 20k, nullspace 7620 witnesses, gcd/extgcd/modinv 60k, matmul 25k) vs exact oracles; `not a URDR-gate MEASURED` (proven reference; the kernel certifies its witnesses) |
| urdr-rigidity — infinitesimal rigidity → Connelly superstability (first `urdr-math` CONSUMER, `tools/intla/rigidity.py` + `superstability.py`): builds the rigidity matrix R of a bar framework and asks the frozen library for `rank`/`nullspace`/`transpose`/`determinant` — reimplements NO linear algebra. The full ladder: trivial-motion separation (internal flex = `ker([R;T])`), self-stress `ω = nullspace(Rᵀ)`, stress matrix Ω (Connelly's certificate), exact PSD of Ω (**all principal minors ≥ 0** — NOT Sylvester's leading-minor test, which proves only PD; Ω is singular), and **Connelly superstability** (`Ω⪰0 ∧ rank(Ω)=n−d−1 ∧ no affine flex`, the affine-flex check itself a rank condition). Global (universal) rigidity certified EXACTLY over ℤ, no float. Batteries green: triangle rigid, square flexible (genuine shear flex), doubly-braced square SUPERSTABLE, minimal braced square not superstable. No new kernel primitive; the kernel certifies the cheap witnesses (e.g. `Rᵀω=0` is a nullspace witness). SCOPED to i64-sized frameworks (bignum later) | IMPLEMENTED (library) | algorithm-proven — `superstability.py` + `rigidity.py` batteries green vs exact oracles; `not a URDR-gate MEASURED` (library consumer of urdr-math) |
| urdr-physics — the admissible-transition loop (INTEGRATION: urdr-math → urdr-rigidity → urdr-core, `tools/intla/physics.py`): a transition before→after is ADMITTED iff it is a real change (`ᛝ(before) ≠ ᛝ(after)`, else URDR-DELTA-UNEARNED) AND the candidate is structurally admissible (infinitesimally rigid, via urdr-rigidity/urdr-math). Structural collapse (loss of rigidity) is a REFUSAL, not a NaN. The FIRST place all three layers compose in one certified transition. Battery green: brace-add ADMITTED (transition witness), collapse REFUSED, no-op REFUSED. The digest is the kernel's canon→SHA-256 | IMPLEMENTED (library) | algorithm-proven — `tools/intla/physics.py` battery green; `not a URDR-gate MEASURED` (integration reference) |
| Multi-actor certified structural timeline — Track 1 (`urdr-physics × world_host`, `tools/world_host/structural_world.py`): many actors submit structural mutation proposals `{actor, parent, mutation}`; the scheduler canonicalizes by intent digest `ᛝ(canon([actor,parent,mutation]))` (the weave rule — a pure function of the multiset, preserving the actor's cryptographic intent, arrival-order-independent), applies each through urdr-physics admissibility, and COMMITS a non-forking transition history or emits a deterministic structural CONFLICT (↯). Composes the measured parts (scheduler canonical order, physics admissibility, transition chain + provenance binding, kernel digest) — no new foundations. Battery green: independent braces commit (arrival-order invariant), duplicate proposal conflicts (URDR-DELTA-UNEARNED), collapse (brace removal→flexible) conflicts (inadmissible), stale-parent refused (provenance), non-vacuity (arrival-order scheduler is order-dependent). The engine's authority spine — deterministic multiplayer structural physics | IMPLEMENTED (library) | algorithm-proven — `tools/world_host/structural_world.py` battery green (5/5); `not a URDR-gate MEASURED` (host runtime reference) |
| Regional (local) rigidity certification — the COMPRESSION for multi-actor structural physics (`tools/world_host/regional_rigidity.py`): a region-confined mutation is certified by the LOCAL region's pinned rigidity (`rank(R_local) = d·|interior|`, boundary vertices fixed) at O(region³), not the global O(n³) matrix. SOUNDNESS verified on a 6-vertex two-square truss: for a globally-rigid world, local verdict == global verdict for region-confined mutations (add-redundant-brace stays rigid; remove-brace/side collapses — both), at local 4×4/6×4 vs global 8×12/10×12 cost. A cross-region mutation is not locally certifiable → escalates to a global check (honest boundary). The atlas / regional-chart decomposition (D10) applied to rigidity — the O(region) vs O(world) compression that unlocks concurrent verification. Verified on these cases; general soundness needs the region's complement rigid | IMPLEMENTED (library) | algorithm-proven — `regional_rigidity.py` battery green (local==global on region-confined cases; cross-region escalates); `not a URDR-gate MEASURED` (host runtime reference) |
| Persistent multi-tick structural world — Track 1 deepened (`tools/world_host/persistent_world.py`): chains certified ticks — the committed world digest of Tick_N is the mandatory parent authority for Tick_N+1. Conflicts are ISOLATED (a deterministic structural conflict is logged and skipped; valid proposals still commit; the ticker never halts; no actor penalty — a host policy, not a kernel invariant). Yields a replay-deterministic world-digest timeline. Battery green (5/5): 4-tick chain, tick-2 collapse conflict isolated (world unchanged), ticker continues, replay-identical. Composes structural_world + the transition chain | IMPLEMENTED (library) | algorithm-proven — `persistent_world.py` battery green; `not a URDR-gate MEASURED` (host runtime reference) |
| Persistent world history chain, cross-placed (multi-actor timeline ↔ kernel boundary, MEASURED): the chain digest binds the committed sequence of world states W0→W1→W2 (edges+coords), `D_{k+1}=ᛝ([D_k,W_{k+1}])`; a reorder yields a different head → a fork, refused. Both placements settle on the same chain — the 'both kernels agree on the whole world history' property. Reuses `ᛝ`; no new primitive, no glyph | IMPLEMENTED | MEASURED | `examples/structural_history.urdr` (⊢ [1,1]), `examples/rejected/structural_history_fork_wrong.urdr` (URDR-ASSERT, non-vacuous); cross-placement MEASURED — `urdr-core-rs` ADMITTED 36/36 twice, defect caught 16/16, Windows/`rustc 1.96.1` (corpus v12, 2026-07-07) |
| Kernel certifies a superstable framework's self-stress equilibrium (rigidity ↔ kernel boundary, MEASURED): given `transpose(R)` and a claimed self-stress `w` from urdr-rigidity, the kernel certifies `transpose(R)·w = 0 ∧ w ≠ 0` (nodal equilibrium — the equilibrium half of Connelly superstability), refusing a forged non-equilibrium stress. The doubly-braced square's self-stress, certified over ℤ. Reuses matvec + `≟`; no new primitive, no glyph | IMPLEMENTED | MEASURED | `examples/certify_selfstress.urdr` (⊢ [1,1]), `examples/rejected/certify_selfstress_forged_wrong.urdr` (URDR-ASSERT); cross-placement MEASURED — `urdr-core-rs` ADMITTED 34/34 twice, defect caught 15/15, Windows/`rustc 1.96.1` (corpus v11, 2026-07-07) |
| Kernel certifies a nullspace witness (the math-library ↔ authority-kernel boundary): the kernel does NOT run elimination — given a matrix M and a claimed kernel vector v from urdr-math, it certifies `M·v = 0 ∧ v ≠ 0` (deficiency certified), refusing a forged (`v ∉ ker`) or trivial (`v = 0`) witness. Generalizes `atlas_algebra_deficient_wrong` to ARBITRARY integer matrices from a library witness; the library computes, the kernel certifies. Reuses matvec + `≟`; no new primitive, no glyph | IMPLEMENTED | MEASURED (both placements) | `examples/certify_kernel_witness.urdr` (⊢ [1,1]), `examples/rejected/certify_kernel_forged_wrong.urdr` + `certify_kernel_zero_wrong.urdr` (URDR-ASSERT); cross-placement MEASURED — `urdr-core-rs` ADMITTED 32/32 twice, defect caught 14/14, Windows/`rustc 1.96.1` (corpus v10, 2026-07-07) |
| Shared-world runtime reference — Milestone 7 Step 1 (HOST TRACK, consumes the theorem): the smallest host enforcement loop, an executable spec (NOT production). Owns authoritative state; authority = the kernel's `ᛝ` content digest (the one both placements agree on); an observer is a COVERING chart atlas (D10 admissibility); a frame is ADMITTED iff it reconstructs to the authoritative state, else REFUSED (never repaired). Green: two observers render DIFFERENT frames yet bind to the ONE authority. Red: a laundered frame (mutated source, claimed authority) and a non-covering atlas are both REFUSED. Extends NO invariant — networking/graphics/concurrency/optimization are Steps 3–5, not built. **Graded by its OWN integration test, NOT the URDR gate** | IMPLEMENTED (host track) | integration-test green — `tools/world_host/test_world_host.py` (7/7, incl. non-vacuity: a broken admit-all host fails the harness), Python sandbox host; `not a URDR-gate MEASURED` (host code that consumes the measured kernel) |
| Shared-world runtime — Milestone 7 Step 2 (HOST TRACK): transition HISTORY. A path-dependent chain digest `D_{n+1}=H(D_n,opₙ)` (kernel canon→SHA-256, parent bound via `DigestV`), genesis `D₀=ᛝ(S₀)` — STRONGER than the content digest: a reorder landing on the same final value still breaks the chain. Green: replay reproduces the authoritative head; two observers agree; views differ but final-state authority agrees. Red: reordered history, missing transition (broken parent), and a fork (two candidate heads, no merge rule) are all REFUSED — the runtime analogue of the witness firewall. Graded by its own integration test, NOT the URDR gate | IMPLEMENTED (host track) | integration-test green — `tools/world_host/test_transition_history.py` (9/9, incl. non-vacuity: a broken accept-any-history host fails), Python sandbox host; `not a URDR-gate MEASURED` |
| Shared-world runtime — Milestone 7 Step 3 (HOST TRACK): deterministic multi-actor SCHEDULER. Many actors propose transitions concurrently; the canonical order is a pure function of the proposal MULTISET — sort by proposal content digest (the kernel `weave` rule) — so arrival order cannot change the authoritative history. Green: canonical head + final state invariant under arrival order; the committed segment is a valid Step-2 history; deterministic. Red: a non-canonical / speculative branch has a different head and CANNOT be promoted (`branch != authority`). CONSUMES the measured convergence property (kernel `weave`/`parallel_runtime`), does not re-prove it. Graded by its own integration test, NOT the URDR gate | IMPLEMENTED (host track) | integration-test green — `tools/world_host/test_scheduler.py` (9/9, incl. non-vacuity: an arrival-order scheduler is not invariant), Python sandbox host; `not a URDR-gate MEASURED` |
| Witness firewall / validator integrity (the "causal firewall" `W ∉ E`): the criterion is PINNED as an immutable, content-addressed value BEFORE any transform; a new state is judged against that anchor, never a criterion the transform supplies. An unlawful transform cannot rewrite the anchor (bindings immutable; rebinding is a parse error), so it dies against the real criterion; observation never mutates the judged state. Achieved by immutability + content-addressing, not a memory guard | IMPLEMENTED | MEASURED | `examples/witness_firewall.urdr` (⊢ [6,6]), `examples/rejected/witness_firewall_forge_wrong.urdr` (URDR-ASSERT) |
| Controlled state transition under an invariant constraint — glyph review of `x ⊣ C` (the deepest candidate): "move, verify, commit-or-revert as one step" has precise semantics `cproj(x,f,pred) = ?(pred(x,f(x)), f(x), x)` (apply · conditional · select), DIGEST-IDENTICAL to that composition — a lossless alias, a shorter spelling not new semantics, so it FAILS the Isomorphic Closure Threshold (§20). Atomicity is not lost by composition (immutability provides it); the "project to nearest / minimal counterexample" reading is a SEARCH Urðr does not do (a false projection dies). `URDR-GLYPH-NOT-EARNED` | IMPLEMENTED | MEASURED | `examples/contract_project.urdr` (⊢ [[3,2,1],[4,1,1],[3,2,1]]), `examples/rejected/contract_project_search_wrong.urdr` (URDR-ASSERT) |
| Layer-2 reference runtime (D7): the domain-agnostic geometry-of-execution kernel — transport-under-contract (`⇒_C`), deterministic replay (fold of transport over a schedule), observer projections (charts of one state), and the invariant witness (`preserved` = `≟` on a *supplied* invariant) — vendored as an R5 module (`manifold_kernel`) and exercised by a program run AS a constrained traversal. Composed from Layer-1 (`?`, `Σ`, `≟`, `☽`, `ᛞ`); the invariant is a CHOICE, not built in (no physics, D7 §3); no new glyph. An unlawful transition is reverted (claiming it committed dies) | IMPLEMENTED | MEASURED | `examples/manifold_runtime.urdr` (⊢ [[3,1,2],6,[[3,1],[1,2]]], imports the vendored kernel), `examples/rejected/manifold_transport_wrong.urdr` (URDR-ASSERT), gate `modules` stage (kernel pinned, vendor≡lock) |
| Stage-3 frequency invariance (temporal reparameterization): the SAME object advanced at different UPDATE RATES is the same object — a slow schedule (one big step), a fast schedule (many small steps), and an interpolated one, equal in net, all reach one state through the Stage-2 kernel `replay` (`rate ≠ identity`). Aliasing (an under-sampled, lossy rate) is a DIFFERENT object and claiming otherwise dies. Frequency is a Layer-2 temporal chart, not a glyph — transport-under-contract on the time axis; CLOSED = a monoid transport (net subdivision-independent) + the kernel + witness-completeness for aliasing | IMPLEMENTED | MEASURED | `examples/frequency_invariance.urdr` (⊢ [[14,0],[14,0],[14,0]], imports the kernel), `examples/rejected/frequency_aliasing_wrong.urdr` (URDR-ASSERT) |
| Stage-3B parallel transport of computation (concurrency): does changing the ORDER of execution change identity? For INDEPENDENT (commuting) transitions, no — different worker orders converge (`≟` on the two orders), async completion order is a chart not a mutation, and batch = the fold; for NON-commuting transitions order IS identity and a race is exposed (`race_condition_wrong` dies). Concurrency = `weave`-style order-invariance + `≟` race check + fold; no glyph. `commuting ⇒ order is a chart; non-commuting ⇒ order is identity` — the digest answers it | IMPLEMENTED | MEASURED | `examples/parallel_runtime.urdr` (⊢ [[1,2,0],[1,2,0],[2,2,0]], imports the kernel), `examples/rejected/race_condition_wrong.urdr` (URDR-ASSERT) |
| Stage-3C speculative transport (possible vs actual): explore multiple futures without mistaking an uncommitted possibility for reality. Three branches are computed PURELY (hypotheses), one is SELECTED by a witness and COMMITTED; discarded futures leave no residue (immutability), and an uncommitted branch is NOT the actual state (`possible ≠ actual`). Only the committed branch becomes `Grounded`. CLOSED = pure branches (immutability) + select/commit (`?`) + the possible/actual boundary IS the no-inflation ladder + `ᛞ` (a hypothesis is not `Grounded` until witnessed — `Nihil ultrā probātum`); no glyph | IMPLEMENTED | MEASURED | `examples/speculative_runtime.urdr` (⊢ [[5,0],[5,0],1], imports the kernel), `examples/rejected/speculation_wrong.urdr` (URDR-ASSERT) |
| Deterministic numeric substrate — Q32.32 fixpoint FOUNDATION (D9, Milestone 5A): a `fix` is a plain `Int` (n/2³²); `from_int`/`add`/`sub`/`neg` with the refusal law — i64 overflow and INT_MIN **die** (`≟`→`URDR-ASSERT`), never wrap-as-truth; comparison already correct on the monotone representation. Deterministic by construction (only i64 `+ − ×` + comparisons). Vendored `fixpoint` R5 module; `mul`+`div`+`floor_int`+`sqrt` now MEASURED (rows below). No float, no glyph. Grades in D9 §6 | IMPLEMENTED | MEASURED | `examples/fixpoint_arithmetic.urdr` (⊢…), `examples/rejected/fixpoint_overflow_wrong.urdr` (URDR-ASSERT), D8 conformance corpus v2 |
| Q32.32 `mul` — division-free multi-precision (D9 §4): 16-bit-limb schoolbook product with limb extraction via place-value folds (no `÷`/shift/recursion), floor toward −∞, overflow refused. Algorithm proven (`tools/fixpoint_proto/mul_algorithm.py`), then encoded in Urðr and matched to the prototype on a battery (positive/negative/fractional/floor). Now in the vendored `fixpoint` module (v2) | IMPLEMENTED | MEASURED (both placements) | `examples/fixpoint_mul.urdr` (⊢…), `examples/rejected/fixpoint_mul_overflow_wrong.urdr` (URDR-ASSERT), oracle-agree; D8 corpus v3 |
| Q32.32 `div` — restoring long division (D9 §4): the 95-bit dividend `|a|·2³²` (63 magnitude bits + 32 zeros, `bits_of` fold) divided by `|b|` bit-serially, floor toward −∞, div-by-zero + i64-overflow refused. Because the quotient is built MSB-first and Urðr i64 wraps (Python's oracle does not), an **in-fold guard refuses once the running quotient reaches 2⁶²** — proven to fire on exactly the overflow cases and never on a representable result (`tools/fixpoint_proto/div_algorithm.py` + a 40k-random-case faithful simulation, 0 misfires). Encoded in the vendored `fixpoint` module (v3) | IMPLEMENTED | MEASURED (both placements) | `examples/fixpoint_div.urdr` (⊢ [17179869184, 15032385536, −1431655766, 1431655765, 12884901888]), `examples/rejected/fixpoint_div_zero_wrong.urdr` + `fixpoint_rounding_wrong.urdr` (URDR-ASSERT), oracle-agree; cross-placement MEASURED — `urdr-core-rs` ADMITTED 15/15 twice, Windows/`rustc 1.96.1`, corpus v4 |
| Q32.32 `floor_int` — floor(a/2³²) toward −∞ (D9 §2), a plain Int: integer part for a≥0, one-less for a negative non-integer. A single place-value `fdiv` by 2³²; INT_MIN refused. Algorithm proven (`tools/fixpoint_proto/floor_int_algorithm.py`). Vendored `fixpoint` v4 | IMPLEMENTED | MEASURED (both placements) | `examples/fixpoint_floor.urdr` (⊢ [7,7,−7,−8,0]), `examples/rejected/fixpoint_floor_wrong.urdr` (URDR-ASSERT), oracle-agree; cross-placement MEASURED — `urdr-core-rs` ADMITTED 20/20 twice, Windows/`rustc 1.96.1` |
| Q32.32 `sqrt` — isqrt(a·2³²), floor (D9 §2/§4): bit-by-bit MSB-first, each candidate verified by the EXACT `umul` limb-pair compare (Q<a ∨ (Q=a ∧ R=0)); a<0 and a≥2⁶² refused. Domain a∈[0,2⁶²) (value<2³⁰); full domain = SCOPED strengthening. ~250k ticks/call (48 umuls). Algorithm proven (`tools/fixpoint_proto/sqrt_algorithm.py`, 0 in-domain umul refusals over 4000 randoms). Vendored `fixpoint` v4 | IMPLEMENTED | MEASURED (both placements) | `examples/fixpoint_sqrt.urdr` (⊢ [8589934592,6074000999,12884901888]), `rejected/fixpoint_sqrt_negative_wrong.urdr` + `fixpoint_sqrt_domain_wrong.urdr` (URDR-ASSERT), oracle-agree; cross-placement MEASURED — `urdr-core-rs` ADMITTED 20/20 twice, Windows/`rustc 1.96.1` |
| urdr-physics rung 5 — BOUNDED fixed-point dynamics, the real-time path (`tools/physics/fp_dynamics.py`): where the exact rungs 1–4 REFUSE on any long/iterated sim (ℚ denominators overflow i64 — a gravity drop dies in a handful of steps, a joint sim in ~2), this time-steps the FROZEN Q32.32 substrate (`field.FixedPoint`), BOUNDED (refuses, never wraps) and DETERMINISTIC. Two reference steppers, each the fixed-point port of an exact solver: a settling contact stack (sequential-impulse + ground-up projection + sleep → comes to REST) and an articulated pendulum (distance constraint + squared-length Baumgarte, no sqrt → SWINGS without drift). Uniqueness-by-certificate is replaced by reproducibility-by-frozen-rounding | IMPLEMENTED | **MEASURED (both placements)** — reproducibility (frozen `URDRFPT1` golden) **and** cross-placement: the independent Rust `tools/physics/fp_dynamics_rs/fp_dynamics.rs` (std-only, hand-rolled SHA-256, same frozen `frdiv`) reproduced BOTH goldens **ADMITTED 2/2 twice identically**, `--defect` caught 2/2 (red-first), on Windows/`rustc` — two placements, one on a named host (integer logic also C-cross-checked bit-for-bit, 2330 state words). The FixedPoint substrate FIELDFP is separately cross-placed in `urdr-physics-rs` | `tools/physics/fp_scenes.py` + `conformance_fp.txt` (frozen `URDRFPT1` trace goldens `stack3`/`swing`), `verify.py` `physics_fp` stage (determinism + golden + settle invariant + non-vacuous defect self-test — no-sleep / no-Baumgarte reddens), `tests/test_fp_dynamics.py` (5 falsifiers) |
| Chain-complex falsifier (D1 §22, user-directed conversion): homology's founding law ∂∘∂ = 0 (d1∘d2 on a filled triangle) sealed by exact integer evaluation; a boundary is a cycle; equivalence-mod-boundary = subtraction + ≟; orientation-lost boundary (∂∂ ≠ 0) dies. Integer algebra, no topology claimed (signum ≠ rēs). The SFH-style 'identity modulo a certified transformation space' is ABSORBED (Σ over the witness chain asserting ≟ on an invariant — §21a lifted; red states → URDR-ASSERT), so no primitive, no glyph | IMPLEMENTED | MEASURED | `examples/chain_complex.urdr` (⊢4), `examples/rejected/chain_wrong.urdr` (URDR-ASSERT), `tests/test_chain.py` (6 falsifiers incl. the witnessed-deformation absorption proof) |
| Determinism: same source ⇒ same digest, twice, subprocess-isolated, golden-pinned | IMPLEMENTED | MEASURED | `verify.py` examples stage; green ×2. Cross-host: every example digest in the corpus bit-identical on Linux (Python 3.10.12, sandbox) and Windows (PowerShell, `PYTHONUTF8=1`), through v0.7.x (143-falsifier gate green on both). Two named hosts, not "any host" |
| Defined i64 wrap semantics | IMPLEMENTED | MEASURED | `tests/test_determinism.py` |
| Fuel-bounded evaluation, deterministic URDR-FUEL | IMPLEMENTED | MEASURED | `tests/test_determinism.py` |
| Gate red-capability (tamper fixture must fail; red-first transcript kept) | IMPLEMENTED | MEASURED | `verify.py` tamper stage; `docs/transcripts/red.txt` |
| Offline: stdlib-only, no network at any phase | IMPLEMENTED | DECLARED | by construction (no import touches the network); a network-disabled CI run is SCOPED |
| Continuous-integration matrix (`.github/workflows/verify.yml`): the gate re-run on every push/PR across os {ubuntu-latest, windows-latest} × python {3.10, 3.12} = **4 jobs** — two OS families × two interpreters, stdlib-only, `PYTHONHASHSEED=0`/`PYTHONUTF8=1`. Four jobs on two hosts — **not "six environments", not "any host"** | IMPLEMENTED | DECLARED | workflow present and pushed (matrix pinned here so the count cannot drift); green runs on a given commit are per-run evidence on those runners, not observed in this ledger. Cross-host digest-identity is separately MEASURED on two named hosts — see the Determinism row |
| Whole-program totality | — | — | **not claimed**; fuel bound instead (D1 §6) |

## Deferred (the honest remainder)

| Capability | Grade | Rung |
|---|---|---|
| Base-60 numeric literals (𒁹, 𒌋) | SCOPED / N/A | R1 |
| Division / modulo with defined zero semantics | SCOPED / N/A | R1 |
| Effect kinds beyond snapshot files (clock, RNG, network, live filesystem) — each arrives as a recorded/planned capability through the same mint, or not at all | SPECULATIVE / N/A | — |
| Dipole/Hale involution falsifier (ℤ₂ double cover; C₂ sibling of the rhombohedral C₃ rung) — user-directed conversion, designed in `spec/R4-dipole_quantum_ratchet.md` (form precedes code). Clifford-level, **zero magic**: anchors the *contrast* to Cao et al. (arXiv:2403.07056, PRX Quantum 2025), never a non-Clifford/magic simulation. Claims nothing about the sun. Breach reuses `URDR-ASSERT`; no new code, no new glyph | SCOPED / N/A | R1-family |
| Non-Clifford / magic (T-gate, nonstabilizerness) fragment — would require complex amplitudes outside the integer stdlib core | SPECULATIVE / N/A | — |
| α-normalized *definition*-hash module addressing (format/rename-invariant, true Unison) — the strengthening of R5's byte-level `source-hash` | SCOPED / N/A | R5+ |
| Actor glyph assignment (weave stays ASCII until semantics prove stable) | SCOPED / N/A | R3 review |
| WHAT/WHERE placement split, *līmes* boundaries, differential oracle, ☉ reference marker | SCOPED / N/A | R3 |
| Non-Python placements admitted by the same oracle — the Rust **kernel** is now MEASURED on the D8 conformance vectors (see inventory); remaining: whole-corpus Rust admission via `foreign_oracle.py`, bytecode VM | SCOPED / N/A | R6 |
| Rust production compiler (same oracle admission; a kernel is not a compiler) | SPECULATIVE / N/A | R6 |
| Live view↔edit session UI over the one dataflow | SPECULATIVE / N/A | — |
| Self-hosting | SPECULATIVE / N/A | — |

## Metatheory obligations (D1 §10 restated with grades)

type safety (progress+preservation): CONJECTURED · no-inflation soundness: TESTED
(falsifiers), CONJECTURED (as theorem) · determinism: TESTED on two named hosts
(Linux + Windows, digests bit-identical), CONJECTURED (as theorem) ·
lens laws: TESTED, CONJECTURED (as theorems) · reversibility: TESTED ·
schedule-invariance: SPECULATIVE (nothing to schedule yet).

## Does-not-do (binding)

Not physics; no claim about M-theory or the universe survives in any green test. Not a
proof assistant: `Grounded` = *this verifier passed under this evaluator within fuel*.
digest ≠ MAC. declared ≠ verified. cited ≠ implemented. A green gate certifies execution
of these tests on this code — never that a name means what it says. No strings, floats,
recursion, clock, RNG, network, or REPL (each graded above or absent by design law).
Modules exist as R5 import-by-digest (offline, gate-verified pins); a network does not.
I/O exists ONLY as R4 capabilities and R5 module reads — recorded reads and planned writes of snapshot
files at the līmes; live or ambient I/O does not exist, and the evaluator performs none
at any time. A recorded input is digest-verified, never authenticated (digest ≠ MAC
applies to fixtures too). Performance: no figures published; any future figure will name
its host (`benchmark ≠ universal`).


## Gap ledger (pressure candidates — not promises)

A candidate is a *question the language cannot yet answer from existing
primitives*, recorded so the next primitive is **discovered by pressure, not
invented** (D1 §21b). A candidate has no syntax, no glyph, and no test until a
real program forces it; `observed_pressure` counts programs that actually needed
it. A count of 0 means: not yet earned — not even as a function.

**The review rule.** A candidate enters the semantic search space only if a
substrate guarantee does NOT already imply an expressible Urðr law:
`substrate guarantee ≠ language primitive`. Classify before implementing:

- **CLOSED** — already expressible (an idiom), substrate-only, or it violates a
  design law. Not a candidate.
- **OPEN** — inexpressible by existing primitives, has a stated falsifier, AND has
  repeated pressure. Earns a function review (D1 §21b).
- **DEFERRED** — plausibly inexpressible but no pressure yet, or contentless on the
  current model. Recorded, not built.

| Candidate | Class | Why |
|---|---|---|
| invariant preservation | CLOSED | already expressible: `≟(I(x), I(y))` (D1 §21a) |
| canonicalization | CLOSED | substrate-only: absorbed in `canon`/`ᛝ` |
| orchestrate / N-placement | CLOSED | already expressible: the differential oracle generalized (§14b) |
| ownership / borrow | CLOSED | substrate-only: no mutation to alias; conflicts refused at the līmes (`URDR-CAP`) |
| resource lifetime | CLOSED | out of bounds: `eventually released` is a termination claim, not made |
| zero-copy identity | CLOSED | violates design law 3: identity is canonical bytes, not memory layout |
| `capability_attenuation` | DEFERRED | inexpressible today AND currently contentless: caps are atomic (`\|Perm\| ∈ {1,0}`), no delegation target |
| `foreign_rust_kernel` | CLOSED (measured 2026-07-07) | promotion condition met: `urdr-core-rs` reproduces the D8 conformance vectors (8/8, ×2) and a deliberate defect is caught — see the inventory row; whole-corpus admission = the SCOPED strengthening |
| intertwiner / equivariant compiler | CLOSED | already expressible: the oracle IS the commuting square `digest(E_ref(P)) = digest(E_comp(P))` (§14b); per-generator verification is corpus-completeness, not a primitive — now a permanent gate stage (`examples/oracle_generators/`, MEASURED); a defect localizes to `g=+` |
| transport + witness set | CLOSED | already expressible: `≟(I(x), I(Φ(x)))` folded over the witness set — single-invariant = §14b oracle, multi-invariant = `examples/chain_complex.urdr` |
| dimensional witness | DEFERRED | reduces to transport+witness with a rank/adjacency/orientation invariant; the one non-reducible form (dimension as a *static* type axis) has `observed_pressure = 0` — the manifold code now added (`manifold_equivalence`, `sheaf_gluing`) collapses into `≟`, no pressure for a static dimension type |
| equiv_witness (same object under a witness) | CLOSED | measured: `≟` on an invariant (`examples/manifold_equivalence.urdr` + 2 rejected); proposed `URDR-EQUIV-UNPROVEN` / `URDR-INVARIANT-DRIFT` / `URDR-MAP-NONCOMMUTING` all rename `URDR-ASSERT` |
| sheaf gluing / Čech obstruction | CLOSED | measured: a COMPUTED integer obstruction (winding / H¹) + `≟`, cohomological dual of §22; `URDR-SHEAF-NO-GLOBAL-SECTION` / `URDR-GLUE-FAIL` = `URDR-ASSERT`. Unbounded-search obstructions = DEFERRED (Dehn-class) |
| holonomy / transport history (#10) | CLOSED | measured: identity is already state+history (digest carries the parent-link; provenance `ᛃ` observes it); pure-position = `☽`; the holonomy element = computed transport + `≟`. The equivalence is *witness-selected* ('equivalent for what purpose?'), not a glyph |
| boundary-at-infinity / asymptotic class (#11) | CLOSED (founding law) | a finitely-computable asymptotic class (winding, rational endpoint) is a computed witness + `≟`; one needing the actual infinite limit has no finite witness, so Urðr withholds `Grounded` (`Nihil ultrā probātum`) — not a gap. Unbounded-limit case = DEFERRED (search) |
| change-cage / measurement ≠ mutation | CLOSED | 'allowed change' is `ΔI = 0` on a chosen witness (transport+witness, strong enough — χ→β); `W ∉ E` (the effect cannot rewrite its own witness) is already the membrane (law 2: view pure, edit→new store) + R4 read/write capability separation + Grounded-refused-outward; 'the action cannot be its own proof' = `ᛞ`'s witness is minted from verifier×value |
| universal validator (Matiyasevich / Hilbert 10) | CLOSED (founding law) | Urðr never promises `C(v)`; every check is `C(v; Λ)` — the verifier λ IS Λ, the bounded domain. Totality not claimed (D1 §6); the undecidable / 'all completions' case = DEFERRED (search), withheld not faked |
| temporal / transactional invariance | CLOSED (discrete) | 'carry an invariant through evolution' = `\fo` over the tick schedule, each tick a `≟`-gated commit-or-revert (`?`); reversion = keep-prior-state (or anamnesis `↩`). The invariant lives on the STATE, threaded by the fold accumulator (transition-invariants close by state augmentation, cf. holonomy). Asymptotic / trajectory-global / continuous remainder = DEFERRED (search) or out-of-scope (no floats) |

| Candidate | Status | Question | Desired law | Falsifier | Promotion condition | observed_pressure |
|---|---|---|---|---|---|---|
| capability_attenuation | SPECULATIVE / N/A (DEFERRED) | Can a source program derive a *strictly weaker* capability? | Perm(child) ⊆ Perm(parent) | `URDR-CAP-ESCAPE` | **currently contentless**: a Capability is atomic `(kind, name, payload)` so `\|Perm\| ∈ {1,0}` (no proper sub-lattice), and no capability is delegated to a sub-agent — so it earns meaning only if caps FIRST gain internal structure AND become delegable, neither of which has pressure | 0 |
| foreign_rust_kernel | IMPLEMENTED / MEASURED — **promoted 2026-07-07** | Can an *independent* Rust kernel (`urdr-core-rs`) reproduce the reference digest on the corpus? | Rust placement ≡ reference placement | `URDR-RUST-DIVERGENCE` | **condition MET**: `tools/urdr_core_rs/urdr_core.rs` (std-only, hand-rolled SHA-256, no crates) built with `rustc 1.96.1` (stable-x86_64-pc-windows-gnu, Windows) reproduced 8/8 D8 conformance vectors **twice identically**, the `--defect` build was caught 4/4, and 18 ☉-generated unit vectors ran green — see the inventory row. Remaining SCOPED strengthening: whole-corpus admission via `foreign_oracle.py` | 1 (Stage 4 itself) |
| dimensional_witness | SPECULATIVE / N/A (DEFERRED) | Does a transform preserve meaning across a change of dimensional context (embedding / rank / locality)? | `I(x) = I(Φ(x))` for each declared `I` (incl. rank, adjacency, orientation) | none new — collapses to `URDR-ASSERT` | reduces to transport+witness today; earns meaning only if *dimension* must become a STATIC type axis (a mismatch a compile error, as authority is for caps), which needs a real manifold substrate producing repeated friction — none exists | 0 |

Closed by existing mechanism (recorded so they are not re-proposed): invariant
preservation (= `≟` on an invariant, D1 §21a); canonicalization (absorbed in
`canon`/`ᛝ`); evidence transition (§19); placement equivalence (differential
oracle, §14b); order admissibility (`weave`, §13). Rust-flavoured candidates are
closed too, being guarantees of a substrate Urðr does not share: **ownership /
borrow** — Urðr is immutable (no mutable aliasing to check) and conflicting write
authority is refused at the līmes (`URDR-CAP`), so the exclusivity law holds
vacuously; **resource lifetime** — no manual resources, and `eventually released`
is a termination claim Urðr does not make; **zero-copy identity** — identity is
canonical bytes, not memory layout (design law 3), so it is a law violation, not a
gap. Rust improves the *substrate*, not the *semantics* — it stays a placement (R6a).
**Identity modulo a certified transformation space** (SFH / homology equivalence,
D1 §22): CLOSED — a witnessed deformation is `Σ` over the witness chain asserting `≟`
on a declared invariant (§21a lifted); its red states collapse to `URDR-ASSERT`.
`digest = same object`; `≟-on-invariant = same class after allowed deformation`.
**The topology/geometry convergence — all closed, mostly already sealed.** Homotopy,
cobordism, Seifert fibers, BMY, Kaluza–Klein, Mayer–Vietoris, and Lawrence–Krammer /
braid representations all converge on one computational abstraction: *one object, many
constrained representations, an invariant preserved.* Each is CLOSED — and the sharper
finding is that each is already exercised by an existing falsifier:
- **structure-preserving map** `f(a∘b)=f(a)⋆f(b)` (a representation / homomorphism) =
  the ℤ₂ grading law `grade(aΔb)=grade(a)⊕grade(b)`, sealed over 64 pairs in
  `examples/z2_grading.urdr` (R1, §12);
- **projection round-trip** `recombine(project(X))=X` (Kaluza–Klein) = the lens laws
  (put-get / get-put), `examples/lens_roundtrip.urdr` (§8);
- **boundary witness** `∂W = A−B` (cobordism) = the chain boundary (§22) + `≟`;
- **many realizations → one invariant** (Mayer–Vietoris seam / Seifert fibers) = the
  differential oracle (§14b, N placements, one digest).
`A representation earns trust only by carrying the laws it preserves` is the *definition*
of `Grounded` (a named verifier passed). The topology chain rediscovers, from the
geometric side, the primitives Urðr already has — `ᛞ` (verify a law), `≟` (assert an
invariant), the digest (identity), the placement oracle (many realizations, one truth).
No new primitive, no glyph.
**T-duality / representation correspondence / GKPW** (identity across *representations*,
not executions): CLOSED, already sealed. A reversible correspondence preserving an
invariant is the lens round-trip (§8) + `≟` on the invariant (§21a); *two descriptions,
one invariant* is the differential oracle (§14b). A broken dual dies `URDR-ASSERT`
(so `URDR-DUALITY-BROKEN` renames nothing). Demonstrated by evaluation.
**Dehn function / witness complexity** ('how expensive was the proof?'): DEFERRED. The
cost of a GIVEN witness is `fuel` (deterministic, bounded — a costly proof exceeds a
small budget and gives `URDR-FUEL`); the *minimal* cost over all witnesses is a proof
SEARCH Urðr deliberately does not do (D1 §6, totality not claimed), and no program has
needed it. `proof existence ≠ proof complexity`; the first is `ᛞ`, the second is `fuel`.

**The intertwiner / equivariance reading of the oracle — CLOSED (design theorem).** With
`f` = compile, `ρ` = evaluation, and the digest the observable, the differential oracle
(§14b) is the commuting square `digest(f∘E_ref)(P) = digest(E_comp∘f)(P)` — *map then run
= run then map*, the intertwiner law `f(ρ_V(g)·v) = ρ_W(g)·f(v)` instantiated on
placements. Put under load with five single-generator probes (`+`, `*`, `☽`, `Σ`, `ᛞ`):
reference ≡ compiled on every generator (the square commutes per-operation), and the
defect placement breaks on exactly `g=+` and nowhere else — the square fails for precisely
the generator it perturbs, and the failure localizes. So "compilation preserves the action
across a family of operations" is not a new primitive; it is the oracle. Its stronger
reading (verify each generator, not only the composite) is a corpus-completeness
obligation — one probe per generator — plus, if wanted, a second observable (per-tick
`fuel`, already tracked, currently unexposed by the CLI). Design theorem for future
placements (compiled, Rust, any Φ), verified by the oracle; `commuting square = the
oracle`, `more generators = more corpus`, no glyph.
**Transport + witness set — CLOSED.** An agnostic map Φ plus a set of independently-checked
invariants, accepted iff each verifies, is this same pattern generalized: `≟(I(x),
I(Φ(x)))` folded over the witness set. Single-invariant is the oracle; multi-invariant is
already `examples/chain_complex.urdr`, which folds `=?` over `{r1..r4}` (its own r4 note
records why "same class after allowed deformation" earns no glyph). It may one day earn a
library combinator (`preserves(Φ, [I…], x)`); it earns no symbol — `new spelling ≠ new
semantics`.
**Dimensional witness / "semantic magnitude changes with dimensional dependency" —
DEFERRED (zero pressure).** Reduces to transport+witness with a rank / adjacency /
orientation / locality invariant. Its only non-reducible form — making *dimension* a
static type axis so a dimension mismatch is a compile error (as authority is for
capabilities) — has `observed_pressure = 0`: there is no manifold code in the repo, so it
fails the Reality wheel (D6) and cannot be minted under the project's own law. **The
manifold engine as a pressure chamber** is the right *method* (build a substrate that
stresses the language until a law must be named — the way I/O forced the capability
līmes), and it is recorded here as the intended next pressure source. But the method's
first rule is Reality: nothing is minted until real friction repeats. `pain observed ≠
imagined pain`; build the wheel before naming the road.

**Manifold equivalence & sheaf gluing — tested under load, both CLOSED (measured).** Two
adversarial suites were built to put real pressure on the "identity across representations"
/ `equiv_witness(A,B,invariants)` candidate and on the sheaf-cohomology "do local proofs
compose into a global proof?" candidate — not to assert their disposition.
- *Equivalence under a witness*: "same object in the sense I care about" is `≟` on an
  invariant. Safe transforms (relabel, Pachner flip) give different digests but equal χ
  (equivalence under the χ-witness); false transforms (puncture, disconnected merge) change
  χ and die `URDR-ASSERT`. `equiv_witness` reduces to `≟` folded over the declared
  invariants; `URDR-EQUIV-UNPROVEN` / `URDR-INVARIANT-DRIFT` / `URDR-MAP-NONCOMMUTING` all
  rename `URDR-ASSERT`. No new primitive.
- *Sheaf gluing*: "do local truths compose into a global one?" is answered by a COMPUTED
  obstruction, not a search. Over a loop-cover, local sections glue iff the Čech winding
  class (an integer H¹) vanishes — `≟(loop, 0)`. Case 1 (every overlap locally consistent,
  yet no global section) is a nonzero monodromy caught by `URDR-ASSERT`. This is the
  cohomological DUAL of the chain-complex boundary law already sealed (§22, `∂∂=0`). The
  "genuinely new epistemic category" — *local `Grounded` ⇏ global `Grounded`* — is real as
  a concept but expressed today as `ᛞ` over an obstruction-computing verifier: global
  `Grounded` is minted only when the obstruction verifier passes. `URDR-SHEAF-NO-GLOBAL-
  SECTION` / `URDR-GLUE-FAIL` = `URDR-ASSERT`. No new primitive, no glyph.
The DEFERRED remainder is the one Dehn already named: an obstruction requiring UNBOUNDED
SEARCH (non-finite covers, undecidable coefficients, "safe for ALL completions") is a proof
search Urðr deliberately does not do (D1 §6). A COMPUTABLE obstruction (finite cover, ℤ
coefficients) is not a gap — it is arithmetic + `≟`. `computed obstruction ≠ searched
obstruction`; the first is `≟`, the second is out of scope.

**Holonomy & the horocycle / boundary-at-infinity question — measured, CLOSED.** The sharp
form: *does Urðr identify an object by state, or by state + transport history?* Measured
answer — **state + history, already.** Two stores reaching the identical current field by
different edit-paths have different digests (the parent-link is in the canonical bytes) and
different provenance `ᛃ`; `holonomy_witness.urdr` shows two loops with the same base position
(`≟` on the viewed `pt`) that are nonetheless distinct objects, and a false
holonomy-equivalence claim (same coordinate, different holonomy) dies `URDR-ASSERT`. So the
programmer *selects* the equivalence by choosing the witness — pure position (`☽`), full
identity (digest = state+history), or the holonomy element (a computed transport sum + `≟`).
That IS the "equivalent for what purpose?" / witness-selection layer: mathematics supplies
candidate invariants; the program picks which one is the contract. The **horocycle /
boundary-at-infinity** case is the elegant limit — an asymptotic class that is *finitely
computable* (a winding number, a rational endpoint) is another computed witness + `≟`; one
that genuinely needs the infinite limit has **no finite witness**, so Urðr withholds
`Grounded` — the founding law doing its job, not a missing primitive (the "point you never
reach" is exactly where evidence is not earned). `finite witness ⇒ ≟; no finite witness ⇒
no Grounded`.
**The 30-contract table — one shape, mostly already sealed.** The contracts span
geometry/topology/physics/learned manifolds, but the repeated semantic shape is one: *a claim
that a transformation preserves a declared invariant across a change of representation, scale,
or context* — `compute witness → ≟` (refused as `URDR-ASSERT`), or a computed obstruction for
global assembly, or a withheld `Grounded` for the infinite/undecidable. Several are already
measured falsifiers: Euler-χ (#27) and Pachner invariance (#25) = `manifold_equivalence`;
cohomological obstruction (#15) = `sheaf_gluing`; homology `∂∂=0` (#14) = `chain_complex`
(§22); holonomy (#10) = `holonomy_witness`; structure-preserving map (#2/#18) = `z2_grading`;
projection round-trip (#24) = the lens laws. A contract earns language surface only on the D6
terms — a *recurring* real failure existing primitives cannot state safely: `math supplies
invariants; experiments expose missing witnesses; applications reveal which witnesses matter;
glyphs encode only the recurring unavoidable ones`. None has yet cleared that bar; every
tested contract reduced to `≟` + a computed witness, or to the founding law's refusal.

**The Euler characteristic is too coarse — witness strengthened, measured.** χ is a *lossy
compression* of the Betti vector (`χ = Σ(−1)ᵏβₖ`), so a torus (β=(1,2,1)) and a cylinder
(β=(1,1,0)) both have χ=0 — the χ-witness of `manifold_equivalence` would wrongly accept them
as the same object. `manifold_betti_refinement` makes this legible: Euler–Poincaré ties each
Betti vector to real face-counts, the coarse χ-witness collides (χ=0=χ), the finer Betti-vector
witness separates them, and a false Betti-equality claim dies `URDR-ASSERT`. This is not a gap
— it is the witness-selection principle biting: `coarse witness ≠ wrong witness` (χ is exactly
right for "same Euler class," too weak for "same homology"). The contract must name a witness
strong enough for the identity it claims.
**"Change cage, not no-change cage" — CLOSED.** The invariant is not "nothing changed" but
"change is a *constrained* transformation," `ΔI(Mₜ, Mₜ₊₁) = 0` on a chosen witness — the
transport+witness pattern with the witness picked per contract. Large internal change with a
preserved invariant is `≟` on the invariant, not on the state.
**measurement ≠ mutation (`W ∉ E`) — CLOSED, already the architecture.** "The system cannot use
a state it may modify as the unquestioned witness of its own correctness" is enforced by three
existing laws together: the **membrane** (design law 2 — a view is pure, an edit yields a *new*
store, so observation cannot mutate), the **R4 capability split** (read and write authority are
separate unforgeable caps; a program cannot manufacture write authority), and the **mint** (a
`Grounded` witness is the digest of `verifier × value`, minted once at `ᛞ` and refused outward
into effect-plans). So the action cannot be its own proof: an effect-plan is inert data that
cannot rewrite the witness that authorized it. `E ↛ W`; only `W → decision → E`. R4 + the
membrane, already MEASURED — no new primitive.
**Matiyasevich / Hilbert's tenth — a design law Urðr already obeys.** There is no universal
validator; Urðr never writes `C(v)`, only `C(v; Λ)` — every falsifier carries its law Λ (the
verifier λ), and totality is not claimed (D1 §6). "Does every completion preserve the property?"
is the undecidable/search case, `DEFERRED` and withheld, not faked. `a cage enforces boundaries;
it cannot contain the mathematical universe` is `Nihil ultrā probātum` from the negative side.
**The last static frontier — time — is now built, and it resolves.** Every witness above is *after-the-fact* —
an invariant on a static pair. The place a real primitive could still appear is *carrying* an
invariant *through* an evolving system, where after-the-fact checking is insufficient: a
deterministic step function with a conserved quantity over many ticks, a golden over the whole
trajectory, and a drift-injection that must redden — the first test of whether the invariant
belongs to the *state* or to the *transition*. Now built: `temporal_invariant` carries a conserved `Q`
through a discrete evolution — each tick proposes an integer affine delta, the contract
commits iff `Q` survives else reverts, and an unlawful injection is reverted, not committed
(`temporal_drift_wrong` shows that removing the contract lets `Q` drift and dies
`URDR-ASSERT`). *State or transition?* — the invariant lives on the STATE, threaded by the
fold accumulator; a transition-invariant closes by augmenting the state (as holonomy did).
So "carry an invariant through evolution" = `\fo` + `≟` + `?` (commit-or-revert) = the
change-cage iterated over time, **no new primitive**. What stays out of reach is the usual
boundary: a *trajectory-global* or *asymptotic* invariant (a long-run average, a Lyapunov
bound, behaviour at t→∞) has no finite per-tick witness, so it is `DEFERRED` (search), and
*continuous* evolution is out of Urðr's integer scope (design law 4) — the founding law, not
a gap. `discrete transactional invariance = measured; asymptotic/continuous = deferred`.
**The Èṣù / tri-partite engine, scoped honestly.** Its transactional core — the `(O,W,E)`
split (1.1), the invariant contract `𝕀` (1.7), the atomic reversion (1.10), and `W ∉ E` — is
exactly the measured example above (`\fo`+`≟`+`?`+the membrane). Its continuous machinery —
the cohomology Frobenius loss (1.12), the metric-curvature integral (1.14), the `arg min`
(1.15) — is `SCOPED / N/A`: no floats, no `∫`, no gradient descent, by design law 4.
Stochastic integer rounding (`⌊·⌉`) is a non-issue: Urðr is integer-native, so there is
nothing to round — the discrete discipline the engine wants is the default, not an
approximation.
**Refutation by construction — "a fully faithful functor makes lower-dim projections the
totality" is false.** The Yoneda embedding `𝒴(X)=Hom(−,X)` is fully faithful over the
*whole* category — it recovers `X` from *all* probes, including `X` itself (`1_X ∈ Hom(X,X)`
is what makes it bite). It does not say a restricted family of lower-dimensional projections
determines `X`: such a subcategory is generally not dense, so its restricted Yoneda is not
faithful. `projection_underdetermined` shows it by evaluation — two distinct 3D affine maps
(identity and a z-shear) share one 2D projection yet differ in 3D (the projection's kernel
hides the z-shear); claiming full equality from projection-agreement dies `URDR-ASSERT`. The
colimit reconstruction the claim invokes is real, but only over the *full* viewing family
(the density theorem) — the complete witness set, not "lower-dim structures." So the original
statement stands: `functor = truth under a chosen invariant`, incomplete about the larger
object — the same lesson as χ vs the Betti vector: one witness collides, only a
complete-enough witness set determines. `one projection ≠ the object`.
**Depth perception — the hypothesis tested, and it closes to the lens laws.** The paired
question: if one projection under-determines, does *reconstructing* the lost dimension from
multiple views earn a primitive? `depth_perception` measures it — two orthogonal, spanning
projections recover the full 3D point (`recon` round-trips) and the second (depth) view
distinguishes the two maps the front view conflated, while an incomplete, non-spanning set
fails to reconstruct (`depth_incomplete_wrong`, `URDR-ASSERT`). But the recovery operation is
exactly the **lens round-trip** (§8, `recombine(project(X)) = X`) over a *complete* witness
set, `≟`-verified: `recon` is a λ, completeness is the round-trip succeeding, and the
reconstruction is unique iff the views span (a computable rank condition). The pair brackets
the witness-completeness boundary — `one view collides; spanning views determine` — and
neither side earns a symbol. The only remainder is the usual one: for *nonlinear* projections
"is the preimage unique?" is a search, `DEFERRED`. `stereo = lens round-trip over a spanning
witness set`.

**The causal firewall — tested, and it is Urðr's founding rationale, not a new primitive.**
The sharpest form of the whole hunt: not a geometric measure but an *absolute causal
firewall* so "the mutation plan cannot rewrite the rules used to evaluate it" (`Γ ∩ E = ∅`,
an append-only immutable witness ledger). `witness_firewall` measures it — the criterion is
pinned as an immutable, content-addressed value *before* any transform; an unlawful transform
that breaks the invariant dies against the *pinned* anchor (`URDR-ASSERT`), because it cannot
rewrite an immutable binding (rebinding is a parse error) and observation never mutated the
judged state. The firewall is real and necessary — but in Urðr it is not a primitive to
*add*; it is the **consequence of immutability + content-addressing**, the same laws that
already give the membrane, provenance `ᛃ` (the append-only hash-chain history = `Γ`), and
`Grounded refused outward` (R4 — a witness cannot be laundered through an effect). The
distinction worth stating: the engine seeks a *causal / memory-isolation* firewall (`Γ` and
`E` in separate address spaces); Urðr achieves the same guarantee **epistemically** —
evidence is content-addressed (SHA-256), so the validator cannot be overwritten because
*nothing* can be overwritten, and a witness transparently records the verifier it was earned
by (`signum ≠ rēs`: a program may self-grade with a trivial verifier, but the grade names
that verifier and cannot claim a stronger one). `content-addressing ⇒ the firewall for free`;
no memory guard, no new glyph. The continuous machinery (the Hodge / cohomology / metric
lines) stays `SCOPED / N/A`. And the two follow-ups answer themselves: concurrent affine
changes are safe because nothing mutates (the `weave` schedule-invariance, already sealed),
and the append-only `∥` is exactly the content-addressed provenance chain — neither needs a
hardware guard, because the guarantee is cryptographic, not physical. The hunt arrived, from
the systems side, at *why* Urðr is immutable and content-addressed in the first place.

**The controlled-transition primitive — the deepest candidate, reviewed and not earned.** The
strongest glyph proposal of the arc, and the best-framed: a one-step "move, verify, commit-or-
reject" operation (`x ⊣ C`) with an explicit irreducibility checklist. `contract_project`
submits it to the glyph review (§20). Its precise operational semantics — written so two
placements must agree — are `?(pred(x, f(x)), f(x), x)`: apply the move, evaluate the contract,
select commit-or-revert. The candidate is **digest-identical to that composition** (measured),
which is exactly the lossless-alias / Isomorphic-Closure failure: naming it `⊣` adds a spelling,
not a relation no composition expresses. And the property it is meant to protect —
*indivisibility* — is **not lost by composition** in Urðr: immutability makes `?(C(f(x)), f(x),
x)` already atomic (the move yields a fresh value; no intermediate state is observable), and at
the one boundary where atomicity is non-vacuous — the effect līmes — R4 already guarantees
validate-all-then-write-all. The reading that *would* be irreducible — "project to the
**nearest** valid state" / "emit a **minimal** counterexample" — is a SEARCH Urðr deliberately
does not do (`cproj` reverts, it does not project; the false-projection fixture dies), the same
`DEFERRED` boundary as Dehn. Verdict: `URDR-GLYPH-NOT-EARNED`. The honest concession that
matters: in a language *with mutation* this operation **would** earn a primitive — atomicity is
genuinely lost by composition there, which is why transactional constructs exist — and Urðr's
immutability + content-addressing is exactly what pays for it in advance. The checklist was
right; the substrate already satisfies it. `move-verify-commit = ?(C∘f, f, id)`; `atomicity =
immutability`; `nearest = search`.

**Stage 3 — frequency invariance (the first middleware stress test) — CLOSED, and it confirms the
frame.** The proposal: can the runtime preserve identity while changing rate, phase, and resolution? `frequency_invariance` measures it — three update rates (slow one-step, fast many-step, interpolated), equal in net, reach ONE object through the Stage-2 kernel's `replay`; `rate ≠ identity`. The failure is aliasing: an under-sampled, lossy rate is a DIFFERENT object, and `frequency_aliasing_wrong` dies `URDR-ASSERT` when it claims otherwise. But temporal reparameterization is not a new primitive: rate-invariance holds because the transport is a MONOID action (net independent of subdivision, the `z2_grading` homomorphism pattern), the traversal is the kernel's transport-under-contract on the *time* axis, and aliasing is witness-completeness (`projection_underdetermined`/`depth_perception`) applied to sampling. So `frequency` is a Layer-2 temporal chart, exactly as proposed — `controlled reparameterization under invariant preservation` = the kernel, no glyph. `rate ≠ identity` is `representation ≠ identity` on the time axis — the whole arc's lesson, one more axis.

**Stage 3B — parallel transport of computation (concurrency) — CLOSED, and it is the sharpest
confirmation.** Where frequency asked *does changing the rate change identity?*, concurrency asks *does changing the order change identity?* — the harder question. `parallel_runtime` measures it: two INDEPENDENT (commuting) worker transitions reach one object regardless of order (worker convergence + async order-invariance), and batch equals the fold. The failure is a race — two NON-commuting transitions diverge, and `race_condition_wrong` dies `URDR-ASSERT` when it claims they converge. No new primitive: order-invariance of commuting operations is exactly `weave`'s schedule-invariance (one digest across permuted schedules, Layer-1 MEASURED), a race is a failed `≟`, batching is `Σ`, and the digest itself answers *is order part of identity?* — no for commuting operations (order is a chart the digest collapses), yes for non-commuting ones (different orders, different digests). The user's decomposition holds exactly: `task identity = content addressing; convergence = weave; ordering = a schedule projection; race = ≟ failure; determinism = replay`. `order ≠ identity ⟺ the operations commute` — decided, not assumed. The manifold runtime is now a verified *concurrent* state geometry, still with no glyph beyond the core.

**Stage 3C — speculative transport (possible vs actual) — CLOSED, and it lands on the founding
law itself.** The Epictetus boundary: change is unavoidable, but the system must not add a false state on top of it. `speculative_runtime` measures it — three futures computed purely (hypotheses), one selected by a witness and committed, the discarded ones leaving no residue (immutability), and an uncommitted branch is not the actual state (`speculation_wrong` dies `URDR-ASSERT` when a hypothesis claims to be committed reality). No new primitive, and the sharpest reduction of the whole battery: branching is pure values (the membrane — a computed-but-unused value perturbs nothing), select/commit is `?`, and *the possible/actual boundary is the no-inflation ladder*: a hypothesis is a `DECLARED` value; committed reality is `Grounded` (`MEASURED`); crossing from possible to actual requires `ᛞ`. `possible → actual without a witness` is exactly the inflation that does not typecheck. The Stage-3 stress battery (rate, order, possibility) all reduce to the kernel plus one Layer-1 law — which is the *good* answer to "new abstraction or vocabulary?": the runtime is a real abstraction because it generalizes to every axis without new parts. `explore freely; commit only what is witnessed` = `Nihil ultrā probātum`.

**I/O adversarial pass (R4).** The capability/effect subsystem was stress-tested on
five paths — delegation, lifetime, effect composition, observation provenance,
conservation — and every one collapses into an existing refusal or a design law
(runs recorded): read-cap→write and ungranted → `URDR-CAP`; persist-a-cap →
`URDR-LIMES` (no stale cap can exist); two-plans-one-target → `URDR-CAP`, distinct
targets sorted (the outbox IS the effect algebra); read-42 ≡ computed-42 by content
addressing (law 3 — origin lives in the program's inputs, R4, not the value). Authority
transformation (delegation / attenuation / revocation) is the interesting *dimension*
but is **contentless** in Urðr's model (caps are unforgeable, non-delegable,
non-persistable) — CLOSED/DEFERRED, not a glyph. No new I/O gap.

**Stable-core note.** After this pass, **no OPEN candidate remains**: every proposed
expansion is CLOSED (already-present, substrate-only, or law-violating) or DEFERRED
(no pressure / no current content). That is itself a milestone — the core has reached
a stable point, and future growth should come from *use cases that generate repeated
friction*, not from expansion. A glyph is the visible trace of a missing constraint
(D1 §21b); there is no missing constraint under pressure right now. The core LAWS were
then probed the same way (time/ordering, identity vs behavioural equivalence, proof
reuse across a world change, multi-party merge) and all four closed too — causal order
invisible by design (§13), identity is structure not behaviour (law 3), a proof is
value-pinned (`URDR-LIMES`, R2c), merge is explicit / unpressured. Two subsystems
adversarially hunted, zero gaps. The reusable method is `spec/D6-gap-probe.md`.
`Nihil ultrā probātum.`

**The network bridge (R4 at the līmes) — the internet meets the deterministic kernel — MEASURED
(reference), SPECULATIVE (live socket), and it needed no new language part.** The competitive-engine
question was: can Urðr use third-party packages, API calls, live updates, and online assets without
surrendering determinism? The answer is the līmes, and it falls straight out of R4: *a network
response is just a recorded input whose provenance is a URL.* You **cannot** have one execution that
is both live and deterministic — but you can have the runner fetch **once** at the boundary, **record**
the response as a content-addressed digest-verified snapshot, and thereafter **replay** it
bit-identically inside the kernel, which never opens a socket. `examples/network_read.urdr` measures
it: a modeled API response, captured as a recorded input, replays to one golden digest, and the
compiled placement agrees (`oracle:network_read`) — MEASURED. The falsifiers bite: an **ungranted**
network read is `URDR-CAP` (`network_read_ungranted` — nothing is ambient), and a **tampered** recording
is `URDR-LIMES` (the one codec — refused, not repaired). The package/asset UX is the R5 shape extended
from *code* to *data*: `tools/registry/` gives a `pip`/`npm`/`cargo`-like **name→digest registry** and a
**fetch-and-pin** tool — fetch once, record content-addressed (`<digest>.urdrsnap`), pin a name in
`urdr.registry`; thereafter `resolve(name)` is **offline-reproducible**, digest-verified. The gate
enforces it (`registry-pins` + `registry-mispin-selftest` non-vacuity; `tests/test_registry.py`
falsifiers: round-trip replay, unpinned→`URDR-CAP`, tamper→`URDR-LIMES`, pin-mismatch refused,
injected-fetcher offline core, and re-fetch-of-different-bytes = a different digest = an explicit new
pin — a name never slides silently onto new content). Grading is honest to the tier: the recorded-replay
and registry paths are MEASURED (gate); the *capability plumbing* is reference-runner-only by design
(`urdr-core-rs` exits loudly on `--grant` — capabilities/snapshots are not the portable kernel's job, D8),
so the network fixture is ☉-reference, not both-placements; the *real live socket* is SPECULATIVE — a host
capability at the runner tier, never in the evaluator, graded only where exercised (its deterministic
record+pin core is tested with an injected fetcher). The design note is `docs/network_bridge.md`. This is
the enabler: online assets and live updates enter through **pins**, every build stays **bit-identical**,
and a program that "claims more than it verifies does not typecheck" can still ship with the whole
internet behind it — the internet just leaves its authority at the door, as a digest.
`the digest is the authority; the name is UX; the URL is provenance` · `live = recorded input` ·
`you cannot have live AND deterministic for one execution — you CAN pin the live world into a replayable one`.

**Inter-layer contracts (D11) — spec-before-implementation, graded per layer.** With authority /
deterministic-computation / I/O now cleanly separated, the highest-leverage work is no longer new
primitives (the core is stable; no glyph is under pressure, D5 stable-core note) but **stable
interfaces** — the precondition D8 proved for the kernel (a second placement is only possible
because the contract was frozen first), generalized up the stack. `spec/D11-layer-contracts.md`
writes the engine stack as contracts, each in six fields (GUARANTEES / REQUIRES / MAY-ASSUME /
REFUSES / DETERMINISM / GRADE), grounded in the ACTUAL API surface: capabilities (R4) →
urdr-core (sealed, portable) → urdr-math v0.1 (frozen names: `floor_divmod, rank, determinant,
nullspace, transpose, matmul, gcd, extended_gcd, modinv`; overflow=`REFUSE`) → urdr-rigidity
(rigidity/stress/Connelly certificates) → urdr-physics → urdr-world → urdr-render → applications,
each depending only on the layer beneath and assuming only its *written* guarantees (`Nihil ultrā
probātum` for interfaces). Graded honestly: the layers that exist are MEASURED (capabilities,
core+portable, math, rigidity-library, physics-admissibility, world); physics' **general
constraint solver** is DECLARED (today it is only rigidity-admissibility — `admit iff digest
changed AND rigid`); the live socket is SPECULATIVE. The **deterministic renderer is the DECLARED
centerpiece and the biggest remaining milestone**: `State ⟶ Renderer ⟶ Framebuffer` exists only as
a shape; `State_t ⟹ Framebuffer_t` *bit-identical across placements* is not yet demonstrated — a
strictly stronger property than deterministic simulation, and unusual among engines (most inherit
GPU float variance). §4 pins the **frame-digest law** — `Digest(Frame_t)=SHA-256(canonical_serialize(Frame_t))`
— into eight exact, falsifiable obligations (fixed-point coords, integer edge functions, a top-left
fill rule, fixed-point barycentric, deterministic depth tie-break, exact-integer blend with
over-range=refusal, canonical row-major serialization, content-derived primitive order), so a later
red-first gate can MEASURE conformance the same way D8 admits a second kernel: reproduce every frame
digest twice bit-identically, defect caught, over a `(state → expected-frame-digest)` corpus. No new
glyph; kernel frozen; this is contract work, not a primitive. `I/O proposes · math computes · the
kernel certifies · the renderer projects` · `every frame is a witness`.

**Renderer rung 1 — the first frame-digest witnesses — MEASURED (reference placement), red-first.**
The D11 §4 renderer was the biggest DECLARED gap; this converts its first slice to MEASURED. A
deterministic, integer-only, fixed-point rasterizer (`tools/render/raster.py`) realizes five of the
eight §4 obligations *within the reference*: a fixed-point viewport transform (NDC→subpixel through
`urdr-math.floor_divmod`), exact integer edge functions, the **top-left fill rule** (a shared edge
covered EXACTLY once — proven by two triangles tiling a square with 0 gaps and 0 double-draws; the
`closed` no-tie-break rule double-covers 8 diagonal pixels, the non-vacuity control), pixel-center
sampling in a fixed scan order, and **canonical framebuffer serialization** →
`Digest(Frame)=SHA-256(MAGIC|W|H|C|row-major pixels)`; plus integer, endpoint-symmetric line
rasterization (red-first caught a real direction-dependence bug — `line(A,B)≠line(B,A)` on a slanted
segment — fixed by canonicalizing endpoints, a genuine determinism repair, not a weakened test).
Overflow in raster math is `RENDER-REFUSE`, never a saturate. The `render` gate stage reproduces
each of four scene frame digests (`tri, tri_ndc, line_box, quad_two_tri`) **twice bit-identically**
and matches `tools/render/conformance.txt`; a corner-sample defect is forced to diverge
(`render-defect-selftest`, non-vacuity); nine falsifiers in `tests/test_render.py`. **Scope, stated
honestly (the distinction the reviewer flagged — implementation-evidence vs semantic-claim):** this
is agreement on a stated corpus + refusal set *within the reference placement*. It does NOT yet show
a *second independent* rasterizer agreeing (the D8 cross-placement rung — the next step), NOR GPU
determinism (there is no GPU), NOR completeness for all scenes; depth/blend/perspective remain
DECLARED. `every frame is a witness` is now true for four frames, in one placement. No new glyph;
kernel frozen; render consumes urdr-math, touches no core. `State_t ⟹ Framebuffer_t bit-identical
across placements` stays the scoped next milestone.

**Renderer rung 2 — the independent rasterizer (D8 cross-placement, for pixels) — SPECULATIVE
until compile+paste, then MEASURED.** The rung-1 grade was honest but weak: *one* implementation
signed the four frame digests, so they could be an artifact of Python. Rung 2 does for rendering
exactly what D8 did for the kernel — a SECOND, independent implementation. `tools/render/urdr_render_rs/urdr_render.rs`
is a single std-only Rust file (no crates, no cargo, hand-rolled SHA-256 lifted from urdr-core-rs,
FIPS-checked at startup) that faithfully re-implements the rung-1 rasterizer — `fdiv`, integer edge
functions, top-left rule, orientation normalization, endpoint-canonical line rasterization, the
`MAGIC|W|H|C|row-major` serialization — in a different language / compiler / runtime, judged solely
by `tools/render/conformance.txt`. Its **port logic is cross-checked**: mirroring the Rust exactly
(its `fdiv`, byte layout, MAGIC) in Python reproduces all four goldens and the `--defect`
MAGIC-corruption diverges on all four — but that is still the reference language, so the *convergence*
grade is honestly **SPECULATIVE**: an authoring sandbox without `rustc` cannot measure it. On a host
with a toolchain the protocol is red-first — `.\urdr_render.exe --defect` (every frame MUST diverge,
the harness can redden) then `.\urdr_render.exe` twice (identical) — and `URDR-RENDER-RS: ADMITTED`
twice + defect caught flips the grade to **MEASURED on that named host**. What it establishes: the
four frame digests are a property of the *specification*, not of one interpreter — the exact
reproducibility theorem the architecture is aiming at, now extended from state digests (D8) to frame
digests. What it does NOT: GPU determinism (no GPU), all scenes, or depth/blend/perspective (DECLARED).
`admitted ≠ trusted`; `a second certifier that agrees is the proof the certification is real`.
**CONFIRMED (grade now MEASURED on a named host).** On Windows with `rustc` (edition 2021) the
red-first protocol ran green: `.\urdr_render.exe --defect` caught all four frames (MAGIC-corruption
divergence), and `.\urdr_render.exe` printed `URDR-RENDER-RS: ADMITTED` **twice, identically**, with
every frame digest matching the reference goldens (`line_box bc9a85d6…`, `quad_two_tri 8594205b…`,
`tri d71089cf…`, `tri_ndc 62f1efe1…`). Two independent implementations — Python reference and a
std-only Rust file with its own hand-rolled SHA-256, sharing no code — now agree bit-for-bit on the
four frame digests. The reproducibility theorem extends from state digests (D8) to frame digests:
for this corpus, the rendered output is a property of the specification, not of one interpreter.

**urdr-physics rung 1 — from static geometry to dynamic mechanics — MEASURED (reference), red-first.**
The core loop shifts from validating a static rigidity matrix to executing a deterministic,
time-linked equation of motion, exact over ℤ: `(X_t,V_t) + F ⟶ (X_t+1,V_t+1)` via semi-implicit
(symplectic) Euler + an exact 1-contact LCP impulse + CCD, all in `tools/physics/` (`rational.py`
exact ℚ over ℤ with i64-refusal; `dynamics.py` the step). The four themes land at a provable 1D
foundation: **(1) state-space expansion** — phase space `(X,V)` with mass, momentum `p=Σ m·v` an
exact rational; **(2) deterministic constraint solver** — the 1×1 LCP `w=Mz+q, w,z≥0, w·z=0` solved
exactly (impulse applied only when approaching, non-negative, leaving the bodies separating/resting);
**(3) conservation-law falsifiers** — the honest subtlety that momentum is conserved *structurally*
by the equal-and-opposite impulse (so a **wrong** impulse still conserves momentum), which makes the
**kinetic-energy witness** the discriminating falsifier (conserved iff elastic, strictly decreasing
iff inelastic) — the `physics-defect-selftest` fires exactly here; **(4) CCD as geometric witness** —
`time_of_impact` returns the **exact rational** edge-meets-edge time, so a fast body **cannot tunnel**
a thin wall (`step` advances to the fractional impact time, resolves, integrates the remainder). Five
post-step **state digests** (`free, gravity, elastic, inelastic, ccd_tunnel`) are pinned in
`tools/physics/conformance.txt`, reproduced twice by the `physics` gate stage; nine falsifiers in
`tests/test_physics.py` (determinism+golden, elastic momentum+energy exact, inelastic energy
strictly-lost + rel-vel→0, wrong-impulse energy-violation non-vacuity, CCD non-tunneling + no-impact
control, i64/zero-mass refusal). **Scope, stated honestly:** 1D, single earliest contact per step,
restitution ∈[0,1] — implementation-agreement on a stated corpus *within the reference placement*; it
is NOT continuum physical accuracy, NOT all scenes, NOT yet a second placement. The **general
n-contact LCP** (Lemke/principal pivoting over exact ℚ), 2D/3D + rotational inertia, and a Rust
`urdr-physics-rs` reproducing the state digests (the D8 move for dynamics) are the DECLARED next rungs.
No new glyph; kernel frozen; physics consumes exact rationals, touches no core. `momentum is
structural; energy is the witness; the impact time is exact` · `change is cheap; a certified transition
is the scarce resource`.

**urdr-physics rung 2 — exact 2D & 3D dynamics (the step toward game / VR) — MEASURED (reference),
red-first.** Generalizes the 1D step to vectors, staying exact over ℤ, via ONE dimension-agnostic
implementation (`tools/physics/vecq.py` exact rational `Vec`; `dynamics_nd.py`) that is *the same code
for 2D and 3D*. The load-bearing result: **a ball collision RESPONSE is exact in any dimension without
a square root.** The contact normal is the center-difference vector `d = c₂−c₁`; the `|d|` from
projecting the relative velocity onto the unit normal cancels the `|d|` from the impulse being along
that unit normal, leaving `P = −(1+e)(v_rel·d)/((d·d)(1/m₁+1/m₂))·d` — only `d·d` survives, exact over
ℚ. So the momentum **vector** and kinetic energy are conserved EXACTLY for 2D and 3D, head-on and
oblique (verified for a genuinely diagonal normal `d=(3,3)`: tangential velocity untouched, energy
equal to the last bit), and inelastic strictly loses energy — momentum is again structural, energy the
discriminating witness (`physics-nd-defect-selftest`). **Honest exactness boundary (a real finding,
recorded not hidden):** a *continuous* sphere-sphere time-of-impact solves `|d₀+w·t|² = (r₁+r₂)²`, a
quadratic whose root carries a square root and is therefore generally **irrational** — exact rational
CCD is unavailable for curved-vs-curved continuous collision. So ball-ball uses **discrete** overlap
(`d·d ≤ (r₁+r₂)²`, exact) + exact response, while exact CCD (anti-tunneling) is provided for **linear**
impact conditions — a ball vs an axis-aligned wall, TOI a rational linear solve (a fast ball provably
cannot tunnel; `wall2d` bounces at the exact half-step). Five 2D/3D scene state-digests
(`head2d, oblique2d, inelastic2d, oblique3d, wall2d`) pinned in `conformance_nd.txt`, reproduced twice
by the `physics_nd` gate stage; nine falsifiers in `tests/test_physics_nd.py`. (Also: caught and closed
a module-name collision class — `tools/render/scenes.py` vs `tools/physics/scenes.py` shared the gate's
one sys.path; renamed to `phys_scenes`/`nd_scenes`, tool module basenames now globally unique.) **Scope:**
spheres + axis-aligned walls, single earliest event per step, restitution ∈[0,1] — implementation-
agreement on a stated corpus *within the reference placement*. DECLARED next rungs: general n-contact
LCP (Lemke over exact ℚ), rotational inertia + arbitrary convex shapes, continuous sphere-sphere CCD,
and a Rust `urdr-physics-rs` reproducing the state digests. No new glyph; kernel frozen; touches no core.
`the sphere normal is d; the |d| cancels; only d·d survives — 2D and 3D are exact` · `exactness has a
geometric boundary: curved continuous impact is irrational`.

**urdr-physics rung 3 — the exact n-contact constraint solver (simultaneous contacts) — MEASURED
(reference), red-first.** Pairwise rungs resolved one contact at a time; a real world has coupled
simultaneous contacts (resting stacks, multi-body impacts) whose impulses must be solved together. That
is a linear complementarity problem — find normal impulses `λ ≥ 0` with `w = Aλ + b ≥ 0` and `w·λ = 0`
— and `tools/physics/contact_lcp.py` *certifies* the solution rather than assuming it (the
uniqueness-by-certificate principle the reviewer articulated): it returns a `λ` that provably satisfies
every LCP condition, or it **REFUSES**. Exact and direct, honoring every stated constraint: normals are
**un-normalized** (the center-difference `d` for a sphere, an axis for a wall — rational for both, so
`A` (the Delassus operator) and `b` stay rational and the square root never appears); the solver is an
**active-set** method — enumerate candidate active sets in a **canonical** order (increasing size, then
lexicographic), solve the equality subsystem `A_SS λ_S = −b_S` by exact rational Gaussian elimination
with a **deterministic** first-nonzero pivot, return the first set with `λ_S ≥ 0` and `w ≥ 0` — so there
is **no iterative loop, no convergence tolerance, no heuristic ordering** in the authority path; a
singular subsystem is skipped and a degenerate/inconsistent LCP `PHYS-REFUSE`s (refused, not guessed).
Momentum is conserved by construction (each impulse `λ_k d_k` is equal-and-opposite). The canonical
witness is **frictionless constraint propagation**: a resting 3-stack under gravity solves to the exact
`λ = [3, 2, 1]` (the bottom contact carries the whole stack) and every ball comes exactly to rest, and a
2D ball driven into a corner activates both wall contacts at once (`λ=[1,1]`, stops exactly). Four scenes
(`rest2, rest3, separating, corner2d`) pinned in `conformance_lcp.txt` as certified-solution digests,
reproduced twice by the `physics_lcp` gate stage; nine falsifiers in `tests/test_contact_lcp.py` (known
LCPs, stack propagation + rest, complementarity certificate, wrong-λ non-vacuity, all-dynamic-chain
momentum conservation, determinism, inconsistent-LCP + i64 refusal). **Scope:** frictionless normal
contacts, small contact counts (enumeration is exponential — Lemke/principal pivoting is the same exact
answer, faster: a later optimization, not a correctness change) — implementation-agreement on a stated
corpus *within the reference placement*. DECLARED next rungs: friction, rotational inertia + arbitrary
convex shapes, continuous sphere-sphere CCD, and a Rust `urdr-physics-rs` reproducing all the physics
digests (state + LCP). No new glyph; kernel frozen; the solver consumes exact rationals + vectors,
touches no core. `the LCP is not solved, it is certified — λ,w≥0 and λ·w=0 or REFUSE` · `the bottom of
the stack carries the whole stack, exactly`.

**urdr-physics rung 4 — exact articulated / joint constraints (skeletons, mechanisms) — MEASURED
(reference), red-first.** The reviewer's steer — articulated systems before friction — is the better
fit for the exactness discipline, because joints are EQUALITY (bilateral) constraints, not the LCP's
inequalities: the constraint velocity must be exactly zero, so there is no complementarity, only a plain
exact LINEAR solve. `tools/physics/articulated.py`: build the Jacobian `J` (one row per scalar
constraint), form the constraint-space mass `A = J M⁻¹ Jᵀ`, solve `A λ = −Jv` exactly (reusing
`contact_lcp.lin_solve`), apply `v += M⁻¹ Jᵀ λ`, and **certify** `J v_new = 0` — the joint holds to the
last bit. The uniqueness-by-certificate principle is literal here (exactly the Implicit-Function-Theorem
argument the reviewer wrote out): **rank(A) decides local uniqueness** — full rank gives a unique λ that
holds every constraint; a rank-deficient `A` means redundant or conflicting constraints and the solver
**REFUSES** (PHYS-REFUSE), that singular `A` being the witness of non-uniqueness rather than an arbitrary
choice. Exact over ℚ, no tolerance, no heuristic ordering: gradients are un-normalized (a distance
constraint's gradient is `pₐ − p_b`, rational) — and that gradient row *is exactly a rigidity-matrix
row*, so this rung **bridges static rigidity and dynamics** (roadmap items 4↔5): a rigid triangle is
three distance constraints whose Jacobian is `R(G,p)`, and solving it holds every edge length rigid.
Momentum is conserved for all-dynamic systems (equal-and-opposite impulses). Four witnessed scenes
(`rod` — both bodies move together at v=½, λ=¼; `pendulum` — a bob pinned to a static anchor is driven to
rest; `chain3` — a struck 3-link chain propagates; `triangle` — a rigid 3-rod frame stays rigid) pinned
in `conformance_joint.txt`, reproduced twice by the `physics_joint` gate stage; seven falsifiers in
`tests/test_articulated.py` (satisfied certificate, rod-moves-together + momentum, pendulum held, rigid
triangle, unsolved-is-not-held non-vacuity, redundant-constraint refusal, i64 refusal). **Scope:**
velocity-level holonomic equality constraints, frictionless, no drift stabilization (Baumgarte),
translational (no rotational inertia yet) — implementation-agreement on a stated corpus *within the
reference placement*. DECLARED next rungs: friction, rotational inertia + arbitrary convex shapes,
continuous sphere-sphere CCD, and a Rust `urdr-physics-rs` reproducing all physics digests. No new
glyph; kernel frozen; the solver consumes exact rationals + vectors, touches no core. `a joint is an
equality — its velocity is exactly zero or it does not typecheck` · `rank(A) certifies uniqueness; the
same matrix that says a truss is rigid says a mechanism is solvable`.

**Physics cross-placement — urdr-physics-rs (D8 move for dynamics) — SPECULATIVE until compile+paste,
then MEASURED.** The four physics rungs were all reference-only; this earns physics the same
cross-placement status the kernel (state) and renderer (pixels) already hold. `tools/physics/urdr_physics_rs/urdr_physics.rs`
is a single std-only Rust file (no crates, no cargo, hand-rolled SHA-256 from urdr-core-rs, FIPS-checked
at startup) that faithfully re-implements ALL FOUR rungs — exact rational `Q` (i128 intermediates,
gcd-reduced, i64-bounded), vectors, 1D dynamics (step/contact/CCD), 2D/3D sphere dynamics + plane CCD,
the n-contact LCP (active-set enumeration in itertools order, exact rational elimination), and the
articulated equality-constraint solver — in a different language / compiler / runtime, judged solely by
the four physics conformance corpora (18 scene digests across `URDRPH1/PN1/LCP1/JNT1`). Its **port logic
is cross-checked**: mirroring the Rust exactly (its `Q` arithmetic, byte-for-byte serialization, scene
setups, and all four solvers) in Python reproduces **all 18 goldens** and the `--defect` MAGIC-bump
diverges on all 18 — but that is still the reference language, so the *convergence* grade is honestly
**SPECULATIVE**: an authoring sandbox without `rustc` cannot measure it. On a host with a toolchain the
protocol is red-first — `.\urdr_physics.exe --defect` (every digest MUST diverge) then
`.\urdr_physics.exe` twice (identical) — and `URDR-PHYSICS-RS: ADMITTED` twice + defect caught flips the
grade to **MEASURED on that named host**. What it establishes: the physics digests (momentum, contacts,
joints) are a property of the *specification*, not of one interpreter — the D8 reproducibility theorem now
spanning state (kernel), frames (renderer), AND physics. What it does NOT: add capability (friction,
rotation, convex shapes, sphere-sphere CCD stay DECLARED) or claim continuum accuracy. No new glyph;
kernel frozen. `three placements now agree: state, pixels, and motion` · `admitted ≠ trusted; a second
certifier that agrees is the proof`.
**CONFIRMED (grade now MEASURED on a named host).** On Windows with `rustc` (edition 2021) the
red-first protocol ran green: `.\urdr_physics.exe --defect` caught all 18 digests (MAGIC-bump
divergence), and `.\urdr_physics.exe` printed `URDR-PHYSICS-RS: ADMITTED` **twice, identically**, with
every digest matching the reference goldens across all four corpora (1d, nd, lcp, joint). Two independent
implementations — the Python reference and a std-only Rust file with its own hand-rolled SHA-256, sharing
no code — now agree bit-for-bit on all 18 physics digests. **The D8 reproducibility theorem now spans the
whole engine: state (kernel, 36 vectors), pixels (renderer, 4 frames), and motion (physics, 18 digests)
are each bit-identical across two independent placements.** `state, pixels, and motion all agree`.

**Physics v1.0 freeze + adversarial hardening + version manifest (roadmap steps 1–3) — MEASURED.** With
physics cross-placed, the disciplined move is to freeze before extending — the same order that worked for
the language and the renderer. `spec/D12-versions.md` gives every certified subsystem an explicit
**semantic version + corpus version** (core 1.0 / math 0.1 / render 1.0 / physics 1.0 / R4 1.0) and
declares the **physics v1.0 frozen surface** immutable except through a versioned successor: the four
serialization magics + byte grammar (the digest law), the exact-ℚ substrate (no float/clock/RNG/tolerance/
heuristic ordering), the `PHYS-REFUSE` semantics, the witnesses/certificates (momentum, energy,
complementarity, `Jv=0`, `rank(A)`-uniqueness), the public API, and the 18-scene corpus — future
capability *extends*, never mutates. Then, per step 2 (expand the corpus/confidence before features),
adversarial **property hardening** in `tests/test_physics_properties.py` (deterministic fixed-seed LCG —
no real RNG in any authority path): 300 random 2D/3D collisions conserve the momentum vector ALWAYS and
kinetic energy EXACTLY when elastic / non-increasing when inelastic (155 actually collided — non-vacuity);
deep resting stacks propagate to the exact `λ=[n,…,1]` and stay complementary through **n=12**; long
articulated chains are held exactly (`Jv=0`) and conserve momentum through **k=15 links**; degenerate
systems (redundant joints, inconsistent LCPs) and i64 overflow all `PHYS-REFUSE`; a generated scene
digests identically twice. A visible `physics_stress` gate stage records the computed certificates
(deep rest-8 stack `λ=[8..1]`, a 12-link chain held) with a perturbed-λ non-vacuity control. **Scope:**
hardening raises confidence beyond the pinned corpus; it does not claim universal correctness or continuum
accuracy — `admitted ≠ trusted`. No new pinned cross-placement vectors (the freeze stays clean; no Rust
churn); no new glyph; kernel frozen. `freeze the interface, then harden it — capability comes only after,
each feature down the same ladder` · `confidence in what exists before reach for what does not`.

**Docs consolidation + OSDI-style systems paper (`docs/PAPER.md`) — no new claims, only a faithful
account of the measured ones.** With the pipeline frozen through physics, the architecture is written up
as a systems paper (problem → design → architecture → implementation → evaluation → discussion → related
work → conclusion), framed — per external review — as an *architectural* contribution (deterministic
layer contracts, admissibility/refusal boundaries, cross-implementation reproducibility), NOT as new
mathematics or a language manifesto. Every number is drawn from the gate and host runs (36 kernel + 4
frame + 18 physics digests reproduced bit-for-bit by three independent single-file Rust placements, twice
each with defect caught; 208 unit falsifiers; 42 examples; 45 typed rejection fixtures; 18 `URDR-*`
refusal codes + `PHYS-REFUSE`/`RENDER-REFUSE`), and claims are scoped exactly to the evidence: **agreement
on stated corpora across two placements, not universal reproducibility nor mathematical uniqueness for all
inputs** — the distinction the reviewer flagged, stated explicitly in the abstract and §6. The paper also
records the *minimal API surface* (App. A — the sealed glyph core + frozen per-layer function APIs) and a
*stack-compaction design consideration* (App. B — unify the exact substrate, one physics facade, a shared
Rust core — each a digest-preserving refactor to be admitted the same way as a feature, not yet done) and
a reproducibility package (App. C). The root README and `docs/README.md` now point to it; `spec/D11`
(layers) and `spec/D12` (versions/freeze) remain the normative contracts. No code, no gate change, no new
glyph. `the novelty is the combination — contracts, certification boundaries, and reproducible
cross-implementation evaluation — not the manifold as new math` · `claim exactly what the corpus shows`.

**Renderer rung 2 — exact 3D depth (z-buffer occlusion + clipping) — MEASURED (reference); Rust
cross-placement SPECULATIVE until recompile.** The renderer moves from flat 2D coverage to true 3D depth
— objects correctly occlude what is behind them — while staying EXACT and DETERMINISTIC with **no float
and no division**. `tools/render/raster3d.py` (`DepthFramebuffer`): per-vertex integer depth; per-pixel
depth is the exact rational barycentric interpolation `(w0·z0+w1·z1+w2·z2)/(w0+w1+w2)` with the
edge-function weights (sum = doubled area > 0); the **depth test is a cross-multiplication**
`num·den' < num'·den` (denominators positive) — the z-buffer is exact, never a rounded float. Near/far
clip keeps a fragment iff `znear·den ≤ num ≤ zfar·den`; screen clip never writes out of bounds (an `oob`
tally the gate asserts is 0). The load-bearing property is that **occlusion is ORDER-INDEPENDENT for
distinct depths** (draw A,B ≡ draw B,A — the nearest fragment wins regardless of submission order), with a
sharp non-vacuity: **equal-depth ties ARE order-dependent**, proving the depth values (not just coverage)
decide (`render3d-selftest`). Four scenes (`occlusion, gradient, nearfar, screenclip`) pinned in
`conformance3d.txt` reusing the rung-1 `URDRFB1` color-frame law (a 3D frame is still just an image);
`render3d` gate stage + `tests/test_raster3d.py`. The Rust placement `urdr_render_rs` was extended with a
`DepthFb` + the four 3D scenes (a `C3D` corpus); its **port logic is cross-checked** (mirrored in Python:
all four goldens reproduced, zero oob, defect-magic diverges on all) but the *convergence* grade is
SPECULATIVE until the host recompiles — then `URDR-RENDER-RS: ADMITTED` on 8 frames (4 2D + 4 3D) flips it
to MEASURED. **Scope:** orthographic screen-space depth; perspective-correct interpolation, blending, and
geometric Sutherland-Hodgman re-triangulation (with w-clip) arrive with perspective projection, a later
rung. No new glyph; kernel frozen; render rung-1 2D corpus unchanged (additive). `the z-buffer test is a
cross-multiplication, not a division — depth stays exact` · `nearest wins regardless of draw order; the
frame is a function of the SET of triangles`.
**CONFIRMED — 3D cross-placement MEASURED.** On Windows (`rustc` edition 2021) the recompiled
`urdr_render_rs` printed `URDR-RENDER-RS: ADMITTED` twice on **8 frames** (4 2D + 4 3D depth) with the
defect caught 8/8. The renderer's exact 3D depth (occlusion + near/far/screen clip) is now bit-identical
across two independent placements, joining state, motion, and 2D frames. `the occluded 3D frame is a
cross-placement witness now, not just a reference result`.

**urdr-field rung 1 — deterministic scalar-field transport with a USER-OPTIONAL backend — MEASURED
(reference); FIELDFP cross-placement SPECULATIVE until recompile.** The reactive-environment substrate (a
heat/chemical grid for the "responsive fluid" gameplay direction) forced an honest substrate decision:
exact-ℚ fields OVERFLOW (an iterated stencil grows denominators — measured: they double every step and
refuse at step ~24-31). Rather than bury the choice, it is exposed as an **explicit, user-selectable
backend** — the four-rule discipline: (1) the backend tag is part of state identity (`URDRFLD1 | FIELDFP |
… ` vs `… FIELDQ …`), so the two never conflate; (2) the `FixedPoint` radix (2³²) and rounding
(round-to-nearest ties-away) are FROZEN spec; (3) BOTH backends are deterministic and cross-placeable —
the choice trades exactness↔scale, never determinism; (4) `FixedPoint` is the load-bearing real-time path
(bounded, rounds), `Exact` (reusing the physics `Q`) is exact but scoped-tiny (refuses when big).
`tools/physics/field.py` implements a **conservative FLUX-FORM** advection-diffusion (first-order upwind):
each edge flux is computed once and applied +to one cell / −to its neighbor, so total mass is conserved
**EXACTLY even in fixed-point** (integer add/sub cancel the rounded flux) — a strong witness, not just
"bounded drift"; zero-flux (adiabatic) boundary. A real red-first catch: an initial scene picked unstable
parameters (`4k+vx+vy = 5/4 > 1`) and overflowed — fixed by enforcing the monotonicity/CFL bound
`4k+vx+vy ≤ 1`. Four scenes (`diffuse, advect, adv_diff` FIELDFP + a tiny `exactq` FIELDQ) pinned in
`conformance_field.txt`; `field` gate stage (determinism+golden, mass-conserved-exactly, and a
**rounding-drift non-vacuity** — a truncation backend diverges from round-to-nearest, so a divergent
rounding implementation is caught cross-placement); falsifiers in `tests/test_field.py`. The 3 FIELDFP
scenes are cross-placed: `urdr_physics_rs` extended with the fixed-point stencil (`CFIELD`), port logic
cross-checked (all 3 goldens reproduced, defect diverges) — grade SPECULATIVE until recompile, then
`URDR-PHYSICS-RS: ADMITTED` flips it to MEASURED. FIELDQ is reference-only (exact, scoped-tiny). **Scope:**
this is DETERMINISTIC + REPRODUCIBLE, not continuum-accurate; fixed-point ROUNDS (honest); surface-tension/
Marangoni coupling (curvature → √) is a later, partly-boundary rung. No new glyph; kernel frozen; consumes
rational, touches no core. `exact and real-time are at odds over iterated stencils; reproducibility bridges
both — so the backend is an explicit knob` · `flux form conserves mass exactly even when the flux rounds`.
**CONFIRMED — FIELDFP cross-placement MEASURED.** On Windows (`rustc` edition 2021) the recompiled
`urdr_physics_rs` printed `URDR-PHYSICS-RS: ADMITTED` twice on **21 digests** (18 physics + 3 FIELDFP
field) with the defect caught 21/21. The fixed-point advection-diffusion field is now bit-identical across
two independent placements, joining state, motion, and frames — so a reactive fluid/heat field computes
identically on every conforming host (the substrate the deterministic-lockstep gameplay direction needs).
FIELDQ remains reference-only (exact, scoped-tiny). `the field is a cross-placement witness now — the same
heat map on every machine, bit-for-bit`.
**FROZEN — urdr-field v0.1.** With the reference MEASURED and FIELDFP cross-placed, the field is frozen
under `spec/D12`: the `URDRFLD1` serialization grammar (with the backend tag in identity), the radix-2³²
round-to-nearest-ties-away FixedPoint parameters, the conservative-flux-form step semantics + zero-flux
boundary + CFL bound, the two backends, and the 4-scene corpus are immutable except through a versioned
successor. Future field work (surface tension, adaptive/LOD grids) extends, never mutates — same ladder.
`the scalar-transport bedrock is now an unmoving law of the repo`.

**General-n observer-atlas injectivity certificate (Rigor) — MEASURED (reference).** Closes the last
outstanding atlas-injectivity item: the linear-chart theorem (D10, corpus v9) only certified the SQUARE
case via `det ≠ 0`; this lifts it to ANY rectangular (typically over-determined) atlas. An observer atlas
is a family of linear charts `C_i` (each `k_i × n`); it recovers an n-dim state (is injective) iff the
stacked matrix `M` (`Σk_i × n`) has trivial column kernel, i.e. **full COLUMN rank**: `injective ⟺
rank(M) = n`. `tools/intla/atlas_injective.py` computes this with the **frozen** fraction-free Bareiss
`rank` (urdr-math v0.1), exact over ℤ, i64-overflow refused. The non-injectivity certificate is exact and
constructive: when the atlas is deficient, `urdr-math.nullspace(M)` returns a nonzero integer `v` with
`M v = 0`, so the states `0` and `v` are **indistinguishable under every chart** (`M·0 = M·v`) — a
witnessed COLLISION, not a guess. Two exact engines agree by construction (`rank==n ⟺ no nullspace
witness`); a disagreement refuses the verdict. Gate stage `atlas_injective` (a 5×3 over-determined atlas is
injective; a deficient atlas that never observes the z-axis collides with witness `v=[0,0,1]`) + red-first
falsifiers in `tests/test_atlas_injective.py`, including the non-vacuity that adding the missing chart
restores injectivity. Grade: **MEASURED (reference)** — the certificate is gate-tested and the underlying
`rank`/`nullspace` are oracle-MEASURED urdr-math; a Rust cross-placement of urdr-math (and hence this
certificate) is a separate DECLARED item. No new glyph; kernel frozen; consumes only the frozen exact-math
primitives. `injective iff full column rank; the nullspace vector IS the collision — exact, at any n`.

**Observer-atlas reconstruction / inversion (Rigor) — MEASURED (reference).** The constructive sibling of
the injectivity certificate: injectivity proves the atlas *can distinguish* states; this recovers the state
itself. Given an observation `y = M x` under an injective atlas (`rank(M)=n`), `tools/intla/atlas_reconstruct.py`
returns `x` **exactly** as a reduced rational `(num, den)`. Method, exact and division-free until the final
rational: full column rank ⇒ some `n` rows of `M` form an invertible submatrix `S`, chosen deterministically
by a greedy walk that keeps a row iff it raises the **frozen Bareiss `rank`**; solve `S x = y_S` by Cramer's
rule over the **frozen `determinant`** (`x_j = det(S with col j ← y_S) / det(S)`), giving `x = N/D`,
`D = det(S) ≠ 0`. The recovered pair is its own **witness**: `M·num = den·y`, `den > 0`, checkable by anyone
without redoing the solve — the recover-direction analogue of the collision witness. The load-bearing move is
**over-determination as a forgery detector**: a genuine observation satisfies *every* chart, so the state
solved from `n` rows is verified against **all** `Σk_i` rows (exact integer identity `M N = D y`); an
observation nudged off the column space fails a redundant row and is **refused `INCONSISTENT`** (an
impossible/forged view), while a deficient atlas is **refused `NOT_INJECTIVE`** (the state is not unique —
exactly the injectivity collision). Gate stage `atlas_reconstruct` (round-trip: an integer state recovers
with `den=1`, a half-integer state recovers as the exact rational `[1,1]/2`, `den>1` — reconstruction, not
rounding; witness; forgery-refused non-vacuity; deficient-refused) + red-first falsifiers in
`tests/test_atlas_reconstruct.py`; a mutant that drops the all-rows consistency check reddens the forgery
falsifier, proving over-determination is load-bearing. Grade: **MEASURED (reference)** — gate-tested over the
oracle-MEASURED frozen `rank`/`determinant`; i64 overflow inside `determinant` propagates as a `REFUSE`. A
Rust cross-placement of urdr-math (and hence this certificate) remains a separate DECLARED item. No new
glyph; kernel frozen. `the atlas doesn't just tell states apart — it hands you the state, with a receipt, or
refuses the forgery`.

**urdr-math cross-placement — MEASURED (cross-placed).** The lift that turns both atlas certificates above
from reference-proven into *bit-for-bit-across-two-runtimes*.
A new standalone conformance corpus, `tools/intla/conformance_math.txt` (20 scenes), serializes the RESULT
of every exact-integer primitive and both certificates to a SHA-256 digest: `rank`, `determinant`,
`floor_divmod` (each with its i64-overflow/`b=0` REFUSE encoded in the result as a status byte), the
injectivity verdict **plus the exact nullspace collision witness**, and the reconstruction state / typed
refusal (`OK`/`NOT_INJECTIVE`/`INCONSISTENT`). `tools/intla/math_scenes.py` is the reference generator;
gate stage `math_conformance` PINS it (the live reference must still hash to every golden) with a non-vacuity
self-test (a wrong rank diverges from its pin). An independent single-file `std`-only Rust placement,
`tools/intla/urdr_math_rs/urdr_math.rs` (hand-rolled SHA-256, i64-bounded i128 arithmetic, fraction-free
Bareiss rank/det, exact-rational RREF nullspace, Cramer reconstruction), reproduces the same 20 digests and
refuses the same cases; `--defect` corrupts the digest MAGIC so every scene must diverge (red-first).
**CONFIRMED on host.** On Windows (`rustc -O`, single file, no crates) `urdr_math.exe` printed
`URDR-MATH-RS: ADMITTED (20/20 digests)` **twice** and `defect caught (20/20 diverged)` under `--defect` —
the independent Rust placement reproduces every exact-math digest bit-for-bit and the corrupt-magic defect is
caught. It compiled clean on the first pass; it had been de-risked beforehand by an independent Python
re-implementation (reusing none of urdr-math/atlas) that already reproduced all 20 goldens and diverged under
the defect. **Grades now:** the *corpus + gate pin* is **MEASURED** (green in the gate) and the *Rust
placement* is **MEASURED (cross-placed)** on this host. With it, the **general-n injectivity certificate** and
the **exact reconstruction solver** are lifted from reference to **cross-placement MEASURED** — the
mathematical spine (rank, determinant, floor_divmod, the injectivity verdict + exact nullspace collision
witness, and Cramer reconstruction with its witness) is now verified across two independent runtimes. No new
glyph; kernel frozen; consumes only the frozen exact-math surface. This makes **four** independent Rust
placements (core, render, physics, math). `the math spine is no longer a property of one interpreter — it is
a law two runtimes agree on, bit for bit`.

**urdr-math THIRD-runtime placement (C) — MEASURED (cross-placed), three runtimes.** The single
highest-leverage rigor move: `tools/intla/urdr_math_c/urdr_math.c` — a single-file, std-only **C99**
re-implementation (hand-rolled SHA-256, `__int128` wide multiplies, i64-bounded with REFUSE encoded in the
result) that shares no code with the Python reference *or* the Rust placement. It reproduces all **20**
exact-math digests bit-for-bit and refuses the same cases; `--defect` corrupts the MAGIC so every scene
diverges. **CONFIRMED on host:** compiled and run on Linux (`gcc 11.4.0`, `x86_64`), it printed
`URDR-MATH-C: ADMITTED (20/20 digests)` **twice** and `defect caught (20/20 diverged)`. This lifts the
mathematical spine — rank/determinant/floor_divmod, the general-n injectivity verdict + exact nullspace
collision witness, and Cramer reconstruction — from two-runtime to **three-runtime** agreement: three
independent languages (Python, Rust, C), three compilers, and now **two operating systems** (Windows for the
Rust placements, Linux for this one), all bit-identical. `three implementations, three languages, two OSes —
and the same digest on all of them; the spine is a law, not an artifact of one toolchain`.

**Perspective projection (Rendering rung 3) — MEASURED (reference).** The projective chart swap: a pinhole
camera maps `(x,y,z) → (f·x/z, f·y/z)`. The real screen position is irrational, but rasterization needs only
the integer PIXEL, and the floor of a rational is **exact** — so `tools/render/perspective.py` projects to
the pixel grid with the frozen, now-cross-placed `floor_divmod` (via `raster._fdiv`): `px = cx + floor(f·x/z)`,
`py = cy − floor(f·y/z)`. This is a key honesty point: unlike the continuous fixed-point substrate,
**perspective-to-pixel introduces no rounding** — it is exact and reproducible; the only stops are i64
overflow (`RENDER-REFUSE`) and the **near-plane clip** (`z < znear` refuses, never wraps). The defining
property is exact here: two parallel receding rails project to a pixel gap
`floor(f·h/z) − floor(−f·h/z)` that is **monotone non-increasing in z** and shrinks toward the vanishing
pixel (2000→1 over the tested depths), while an orthographic projector keeps the gap constant at 40 — the
non-vacuity control that makes the division load-bearing. Gate stage `render_perspective` (2 wireframe frame
digests `persp_rails`/`persp_cube` reproduced twice vs pinned goldens; vanishing-point convergence;
near-plane clip self-test) + red-first falsifiers in `tests/test_perspective.py` (exact pixels, clip refusal
with a front-vertex non-vacuity, rails-converge-but-orthographic-does-not, near-face-wider-than-far
foreshortening). Grade: **MEASURED (reference)** — reproduces the frame goldens in the gate; a Rust
cross-placement (extend `urdr_render_rs` with the 2 perspective frames) is the DECLARED next step that will
flip it to cross-placed. No new invariant (a chart swap over the both-placements `div`); no new glyph; kernel
frozen. `the rails meet at the horizon — exactly, on the pixel grid, no float in sight`.

**Perspective cross-placement — MEASURED (cross-placed).** `urdr_render_rs/urdr_render.rs` is extended with
the exact floor-division projection (`fdiv`, the same one the 2D viewport uses) and the two wireframe
perspective scenes, reproducing `persp_rails`/`persp_cube`; `--defect` corrupts the framebuffer MAGIC so both
frames diverge. **CONFIRMED on host:** on Windows (`rustc -O --edition 2021`) `urdr_render.exe` printed
`URDR-RENDER-RS: ADMITTED` **twice** over **10 frames** (4 2D + 4 3D + 2 perspective) and `--defect` caught
divergence 10/10; it had been de-risked by an independent Python mirror of the Rust (trunc-then-adjust `fdiv`
+ transcribed geometry) reproducing both goldens. Renderer rung 3 is therefore **MEASURED (cross-placed)** —
perspective vanishing points are now bit-identical across two independent runtimes, and the render placement
covers **10** frames. `the rails converge to the same pixel on every conforming machine`.

**Marangoni surface-tension transport (Continuum) — MEASURED (reference).** The reactive-environment
nonlinearity, built by *extending* the frozen `urdr-field` v0.1 (never mutating it). Where the frozen `step`
advects with a *uniform* velocity, `tools/physics/marangoni.py` derives the velocity from the field itself:
with a linear surface-tension law `σ(c)=c`, the Marangoni velocity across an edge is `v = κ·(σ[b]−σ[a]) =
κ·(c[b]−c[a])`, dragging fluid toward higher surface tension; the advective flux `v·c_upwind` is applied
**conservatively** (`+`/`−` across the edge), so **total mass is conserved EXACTLY even though the coupling
is nonlinear (quadratic in c)** — the headline invariant. The nonlinear term needs a Q32.32 value×value
multiply (`_fp_mul`, round-to-nearest ties-away, the frozen rule; i64 overflow → `FIELD-REFUSE`), on top of
the frozen field's value×rational `mul_k`. Physically it is anti-diffusion: a concentration peak decays
*slower* than under pure diffusion because κ transports mass back up-gradient toward the peak. Gate stage
`marangoni` (3 frame digests `marangoni_sharpen`/`peak2d`/`ridge` reproduced twice vs goldens;
`marangoni-conservation` = mass bit-exact + monotone + κ-keeps-peak-above-diffusion; `marangoni-selftest` =
an over-bounded κ overshoots into **negative** concentration, still mass-conserving — the CFL bound is
load-bearing) + red-first falsifiers in `tests/test_marangoni.py` (mass exact 1-D/2-D, up-gradient transport
on a 2-cell pair, κ=0 non-vacuity, CFL monotonicity + overshoot, overflow refusal). Grade: **MEASURED
(reference)** — reproduces the goldens in the gate on the frozen fixed-point substrate. Honest boundaries:
mass is exact but the field *values* round (fixed-point); monotonicity holds only under the CFL bound; this
is a Marangoni-TYPE scalar transport (linear σ, single field), not free-surface Navier–Stokes. Next
(DECLARED): a Rust cross-placement of the 3 Marangoni frames, and field→body momentum coupling into the LCP.
No new glyph; kernel and `urdr-field` v0.1 frozen; extends, never mutates. `the environment pushes back — the
field flows up its own tension gradient, and not one unit of mass is lost doing it`.

**Marangoni cross-placement — Rust written, SPECULATIVE (pending host).** `urdr_physics_rs/urdr_physics.rs`
is extended with the value×value fixed-point multiply (`fp_mul`) and the Marangoni step, reproducing the 3
scenes (`marangoni_sharpen`/`peak2d`/`ridge`) against embedded goldens; the shared `--defect` MAGIC bump
diverges them. De-risked by an independent Python mirror of the Rust (frdiv-based `fp_mul`/`fmul_k` +
transcribed geometry) reproducing all 3 goldens and diverging under the defect. Grade: **SPECULATIVE** until
a host recompiles `urdr_physics.exe` and prints `ADMITTED` with the 3 Marangoni frames twice + defect caught;
then it flips to **MEASURED (cross-placed)** and the physics placement covers **24** digests (18 physics + 3
FIELDFP + 3 Marangoni). **CONFIRMED on host:** on Windows (`rustc -O --edition 2021`) `urdr_physics.exe`
printed `URDR-PHYSICS-RS: ADMITTED` **twice** over all **24** digests including `marangoni/{sharpen,peak2d,
ridge}`, and `--defect` caught divergence 24/24. Marangoni surface-tension transport is therefore
**MEASURED (cross-placed)** — the nonlinear self-advection is bit-identical across two independent runtimes.

**Field→body momentum coupling (Continuum) — MEASURED (reference).** The complement of Marangoni
self-advection and the piece the original ledger called for (surface-tension force as momentum injection):
`tools/physics/field_coupling.py` has the field's surface-tension gradient push a rigid BODY, `F = μ·∇σ`
(central difference over the frozen fixed-point field, zero-flux clamp), impulse `J = F·Δt`. The load-bearing
property is **exact bookkeeping**: momentum is carried as Q32.32 integers, so `apply_impulse` is an integer
add and the body's momentum change equals the injected impulse **exactly** (`Δp = J`, no drift) — the same
discipline that makes the field's mass exact, carried to the body. A **uniform** field has zero gradient
hence zero force (the non-vacuity that makes the gradient load-bearing); a field rising in +x pushes the body
up-gradient (toward higher σ). Gate stage `field_coupling` (`field-coupling-impulse` = Δp==J + up-gradient
direction; `field-coupling-selftest` = uniform-field-no-force vs gradient-does-force) + red-first falsifiers
in `tests/test_field_coupling.py` (exact bookkeeping both axes, up-gradient, zero-gradient non-vacuity,
monotone push, determinism, overflow refusal). Grade: **MEASURED (reference)**. Honest scope: this is
**one-way** forcing (the field pushes the body; the body does not yet stir the field back), and the force
ROUNDS (fixed-point) while the accounting is exact; wiring `J` as an external term into the LCP contact solve
and the body→field reaction are the next rungs. No new glyph; `urdr-field` v0.1 frozen; extends, never
mutates. `the surface-tension gradient is a force now — and every unit of impulse it spends lands on the body,
exactly`.

**Two-way field↔body loop (Continuum) — MEASURED (reference).** Closes the feedback the one-way rung left
open — `body motion → field update → body motion` — with an exact conservation law spanning field and bodies.
`tools/physics/field_body_loop.py` runs a coupled step in four parts: (1) **field → body** — each in-field
body takes the surface-tension impulse on its predicted velocity (the `Q`-converted fixed-point force);
(2) **contacts** — the predicted velocities are resolved by the **exact** contact LCP (`contact_lcp`), so the
field force enters the constraint solve (a body pushed into a contact is held, `λ` counteracting it);
(3) **body → field reaction (Newton's 3rd law)** — the total impulse the field handed to bodies is DEBITED
from a field-momentum *reservoir*, so `Σ(m·v) + reservoir` is conserved **exactly** in `Q`; (4) **body →
field state** — the body's motion advects the field via the frozen, cross-placed `field.step` (mass exact,
flux form), feeding the next gradient. Gate stage `field_body_loop`: `loop-momentum-conserved` (two free
bodies + contact: total momentum exact + a valid complementary LCP), `loop-lcp-resolves` (a body pushed into
a wall rests with `λ` exactly balancing the field impulse; a field pushing away releases the contact `λ=0`
and the body accelerates off), `loop-selftest` (dropping the reservoir debit makes the total **drift** — the
third-law term is load-bearing) + red-first falsifiers in `tests/test_field_body_loop.py` (incl. field mass
exact under body-driven advection). Grade: **MEASURED (reference)**. Honest scope: the **momentum ledger and
contact resolution are EXACT** (rational); the force conversion and body-driven advection ROUND (fixed-point);
the reservoir is a **bookkeeping** quantity (the scalar field carries no mechanical momentum of its own) — the
exact claim is the *ledger* `Σp_body + reservoir`, whose non-vacuity is that omitting the reaction drifts it.
No new glyph; `urdr-field` v0.1 frozen; consumes the frozen field + exact LCP; extends, never mutates. `the
loop is closed: the field moves the body, the contacts hold, the body stirs the field, and the books balance
to the last unit`.

**Loop conformance corpus + Rust cross-placement — corpus MEASURED; Rust SPECULATIVE (pending host).** Three
canonical coupled-state scenes (`tools/physics/loop_scenes.py`, `conformance_loop.txt`): `loop_push2` (two
free bodies + contact), `loop_wall` (body held against a static wall), `loop_chain3` (three bodies, two
contacts — the field pushes the first and the impulse propagates so all three move together at `1/48`,
multi-contact). Each serializes the exact-`Q` coupled state (new velocities + contact impulses `λ` +
reservoir) to a `URDRLOOP` digest; the gate stage records `loop:*` against the pins. `urdr_physics_rs/
urdr_physics.rs` is extended with `field_impulse`/`coupled_step`/`apply_impulses`/`loop_digest` and the 3
scenes, reproducing the goldens over the *already cross-placed* exact LCP (`solve_lcp`); the frictionless
Delassus system is positive-definite so its solution `λ` is **unique** — independent of active-set search
order — which is why the two placements must agree. `--defect` bumps the `URDRLOOP` magic so all 3 diverge.
Grade: **corpus MEASURED** + **Rust MEASURED (cross-placed)**. **CONFIRMED on host:** on Windows
(`rustc -O --edition 2021`) `urdr_physics.exe` printed `URDR-PHYSICS-RS: ADMITTED` **twice** over all **27**
digests including `loop/{push2,wall,chain3}`, with `--defect` catching divergence 27/27. The two-way
field↔body loop — force → exact LCP contact resolve → reaction reservoir — is now bit-identical across two
independent runtimes; the physics placement covers 27 digests (18 physics + 3 FIELDFP + 3 Marangoni + 3
loop). `the reactive loop is a two-runtime law now: same push, same contact, same books, on every machine`.

**urdr-netcode — the deterministic LOCKSTEP spine — MEASURED (reproducibility, single placement).**
`tools/netcode/lockstep.py` is the smallest honest demonstration of the architecture's one unusual
advantage: two peers that begin from the same canonical world and exchange ONLY timestamped input events
(never state) independently reproduce the same per-tick witness chain (`URDRLST1`) and final state digest.
`simulate(world, log)` steps the frozen Q32.32 substrate (`../physics/field.py`); each tick applies that
tick's inputs (additive control impulses) in a canonical `(peer, seq)` order, then integrates under gravity
in an elastic box. Two load-bearing behaviours, split honestly: (a) **delivery is robust** — the same logical
log delivered REORDERED or DUPLICATED yields the same chain, because exact-duplicate deliveries are DEDUPED
(load-bearing) and additive impulses COMMUTE (so per-tick order is irrelevant; the canonical sort is a
canonical-form nicety here, not the property relied on — stated, not overclaimed); (b) **corruption diverges
detectably** — a DROPPED, MODIFIED, or TICK-MOVED event changes the log, so the chains diverge, and
`first_desync` LOCALIZES it to the first mismatching tick (the desync is detected + explained, never silent).
Gated (`verify.py` stage `netcode_lockstep`): the canonical `arena3` trace reproduces twice and matches its
frozen golden (`conformance_netcode.txt` `URDRLSTT`); two peers assembling the input union in different
arrival orders AGREE; and a `netcode-desync-selftest` requires a dropped input to be caught while the clean
run is not (non-vacuity — the detector can redden, confirmed by a blind-detector probe). Falsifiers in
`tests/test_lockstep.py` (6). Runnable proof: `demo/lockstep_demo.py`. **Grade: MEASURED** — the lockstep
chain's reproducibility is gated on the *already cross-placed* FixedPoint substrate. **Honest scope:** this is
reproducibility-by-frozen-rounding (fixed-point ROUNDS, not exact); and `digest ≠ MAC` — the witnesses catch
*accidental* divergence, not a signing adversary, so **authenticated inputs are a separate, declared piece**.
**Second placement — written + C-cross-checked, SPECULATIVE pending host.** `tools/netcode/lockstep_rs/
lockstep.rs` (std-only Rust, hand-rolled SHA-256, no crates; `i128` intermediates so `2p+d`/`a·kn` never
overflow before the final `_g` check) reproduces the `arena3` `URDRLSTT` golden 2/2 and diverges under
`--defect` (a dropped input). Its integer logic + byte layout were cross-checked **bit-identical by an
independent C99 port** (`__int128`, its own SHA-256) that prints `fea3b967…` twice + a divergent defect
(`31ca3029…`) in the sandbox — so the port logic is validated. **CONFIRMED on host:** on Windows
(`rustc -O lockstep.rs`) `lockstep.exe` printed `URDR-NETCODE-RS: ADMITTED` (arena3 reproduced 2/2, bit-for-bit)
and `--defect` was caught, so N1 is now **MEASURED (both placements)** — the lockstep transcript is bit-identical
across Python and Rust. `two languages, one witness chain: the same inputs make the same digests on both`.
No new glyph; kernel frozen; consumes the frozen substrate; extends, never mutates. `peers trade inputs, not
state; the same inputs make the same witnesses, and a corrupted one is named by the first tick it breaks`.
