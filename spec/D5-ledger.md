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

**D11 §4b + D12 freeze — the exact/bounded boundary contract, and the freeze made mechanical — MEASURED.**
Phase-1 of the authority-layer freeze. Two spec moves + one enforcement mechanism, all gate-backed. (1) **D11
§4b** states the *normative* boundary contract: two admitted numeric regimes — **E, exact ℚ**
(uniqueness-by-certificate: LCP `λ`, joints, collisions, rigidity, urdr-math, FIELDQ) and **B, bounded Q32.32**
(reproducibility-by-frozen-rounding: fields/Marangoni, rung-5 dynamics, lockstep, raster arithmetic) — plus
five boundary rules: exact where affordable; bounded where durational/irrational (with the two standing
precedents: the sqrt-free nD response stays in E, sphere–sphere TOI refuses E); crossing only at the stated
ingress (`FP.unit`) with regimes never mixed in one digest; overflow is a typed refusal in both regimes;
determinism is never traded. **D11 §3.9** adds the urdr-netcode layer contract (MEASURED, both placements).
(2) **D12** freezes the remaining admitted surfaces as v0.1: `urdr-fp-dynamics` (URDRFPD1/URDRFPT1 grammar,
the frozen substrate arithmetic, the stepper constants pinned by the trace goldens), `urdr-netcode` (the
6-tuple event, the canonical dedup+(peer,seq) merge, URDRLST1/URDRLSTT, the `first_desync` law, `digest ≠
MAC` scope), Marangoni+loop (URDRLOOP), and `URDR-WORLD-3` *as consumed* (envelope keys, the float-authoring
→ integer-snap boundary as part of the contract; a consumed-key change is WORLD-4). (3) **The freeze is
enforced, not trusted**: a machine-readable ```freeze-manifest``` block in D12 declares every frozen magic
(6), corpus (9, 31 vectors), and format tag; `tools/specfreeze/freeze_check.py` re-derives each digest law
from the *declared* grammar with its own independent serializers (own i64-BE, own SHA-256) and compares
byte-for-byte against the live code on canonical fixtures — so drift in either the doc or the code reddens
the gate. New gate stage `spec_freeze` (18 rows: magics-distinct + 6 laws + 9 corpus counts + world tag) +
`spec-freeze-selftest` (a corrupted declared magic MUST be caught; baseline must be green first). Red-first:
`tests/test_spec_freeze.py` (9 falsifiers) was written before checker or manifest existed and went RED
(ModuleNotFoundError), and the checker's first run reddened on a real fixture-shape defect (Vec vs list in
the URDRLOOP law) before going green — the detector bites. Unit falsifiers 272 → 281. Also fixed (rule 10):
`lockstep.py`'s stale docstring grade (DECLARED → MEASURED both placements, matching the N1 admission).
**Grade: MEASURED** (gate-enforced; Linux sandbox run ×2; the Windows working-tree gate run accompanies the
commit). **Honest scope:** the freeze certifies the *stated* surfaces — magics, byte grammars on canonical
fixtures, corpus vector counts, the world format tag — not every consumer's use of them, and a byte-grammar
check on a fixture is not a proof of the stepper's semantics (those stay pinned by the trace goldens).
`a frozen interface nobody checks is prose; the manifest makes the doc a falsifiable claim about the code`.

**urdr-netcode N2 — ROLLBACK as a deterministic replay primitive — MEASURED (reference); cross-placement
DECLARED.** `tools/netcode/rollback.py` removes N1's honest limitation (a late input could only desync)
without touching the frozen module. A `Peer` keeps **canonical snapshots** of its Q32.32 state every `K`
ticks (retaining the last `H`); a **late-but-valid** input rewinds to the newest snapshot at-or-before its
tick, re-simulates to the present with the enlarged input set, and the witness chain **CONVERGES bit-for-bit
to the canonical timeline** — `lockstep.simulate` over the full log is the oracle, and the gate pins the
converged `URDRLSTT` trace EQUAL to N1's `arena3` golden (`fea3b967…`, `conformance_rollback.txt`), at
`K=4` and `K=8` (**cadence-invariance**: K/H are operational, not semantic — only the refusal horizon
moves). Everything else is typed: `ROLLBACK-REFUSE` (input older than the oldest retained snapshot; the
event is rejected WHOLE, the chain untouched) and `ROLLBACK-CONFLICT` (a second event with the same
`(peer, seq)` identity but different payload — a forgery or tick-moved replay — refused naming the
identity; an EXACT duplicate is absorbed, as in N1). An input that never arrives still desyncs against the
canonical chain, localized by `first_desync`. **Design ruling (freeze-respecting):** `lockstep.py` (frozen
0.1) is consumed — `_digest`/`trace_digest`/`event`/`first_desync` — never edited; the per-tick physics is
reimplemented, and the oracle-equality invariant doubles as the anti-drift detector between the two ticks
(any divergence reds every vector). **Snapshot contract:** every retained snapshot must reproduce the
`URDRLST1` witness pinned at its tick (restore is exact — gated). Gate stage `netcode_rollback` (5 rows):
golden ×2, converges (K=4/K=8 ≡ oracle), snapshots-exact, refusals (both codes, chain untouched), and the
**apply-at-head defect** (the classic wrong implementation) MUST diverge — non-vacuity. Red-first:
`tests/test_rollback.py` (9 falsifiers) went RED (`ModuleNotFoundError: rollback`) before the module
existed; the late-input falsifier additionally requires the PROVISIONAL chain to differ from the oracle
before delivery (rollback demonstrably rewrote history — convergence is not vacuous). Unit falsifiers
281 → 290. **Grade: MEASURED (reference)** — convergence, cadence-invariance, snapshot exactness, both
refusals, localization, and the caught defect are gate-enforced. **Honest scope:** this is rollback as a
*replay primitive* over the frozen transcript — not prediction/rollforward UX, not interest management;
`digest ≠ MAC` still (identity conflicts are detected; signatures are not claimed; authenticated inputs
remain a declared successor). **Second placement — written + C-cross-checked, SPECULATIVE pending host.**
`tools/netcode/rollback_rs/rollback.rs` (std-only Rust, hand-rolled SHA-256, no crates; `i128`
intermediates; mirrors the admitted N1 placement's arithmetic) implements the full rollback peer —
snapshots every K (retain H), rewind + replay on late delivery, both typed refusals, the apply-at-head
defect — against the pinned late-delivery schedule (each event gated tick+3). Its logic was cross-checked
**bit-identical by an independent C99 port** (`__int128`, its own SHA-256, clean `-Wall -Wextra` compile)
in the sandbox: golden `fea3b967…` reproduced at K=4 (×2) and K=8, `horizon=-2 untouched=1 duplicate=0
conflict=-1`, and `--defect` diverging (`39326ff9…`) — the port logic is validated; only a host `rustc`
run separates it from admission. Per the admission ladder the rollback/snapshot contracts freeze in D12
only after that `ADMITTED`. `history is rewritten only by rewinding it: a late truth replays to the same
chain, and everything else is named — too old, or a lie`.

**N2 admission + freeze — MEASURED (both placements); `urdr-netcode-rollback 0.1` FROZEN.** **CONFIRMED on
host:** on Windows (`rustc -O rollback.rs`) `rollback.exe` printed `URDR-ROLLBACK-RS: ADMITTED` — the
golden `fea3b967…` reproduced at K=4 (×2) and K=8, refusals typed (`ROLLBACK-REFUSE` with the chain
untouched; exact duplicate absorbed; `ROLLBACK-CONFLICT`) — and `--defect` diverged at `39326ff9…`, the
SAME divergent digest the independent C99 port produced in the sandbox: **three implementations agree on
the canonical chain AND on the defect's exact divergence.** The Windows gate reproduced 290/0 with all
five rollback rows green (commits `7ece2c8`, `7226891`). D12 accordingly freezes `urdr-netcode-rollback
0.1`: N2 introduces **no new serialization** (URDRLST1/URDRLSTT reused — itself contractual); the
snapshot contract (a restored snapshot reproduces the pinned URDRLST1 witness; K/H are operational, only
the refusal horizon moves), the rollback law (rewind to the newest snapshot at-or-before the input's
tick, replay, converge to the N1 canonical timeline), and both refusal codes are immutable except through
a versioned successor; `conformance_rollback.txt` joins the mechanically-checked freeze manifest. D11
§3.9/§4b updated (rollback leaves the DECLARED lists — rule 10). Honest scope unchanged: a replay
primitive over the frozen transcript; `digest ≠ MAC`; authenticated inputs remain the declared next piece.
`three languages, one history: rewound, replayed, and named the same everywhere`.

**urdr-netcode N3 — AUTHENTICATED INPUTS (Lamport one-time signatures) — MEASURED (reference);
cross-placement DECLARED.** `tools/netcode/authinput.py` answers `digest ≠ MAC` with an actual signature
built from the ONLY primitive every placement already hand-rolls (SHA-256) — no new dependency, no new
crypto primitive. The structural separation is enforced by composition: `AuthedPeer` wraps the N2
authority, and an event reaches `rollback.Peer.deliver` ONLY after its envelope verifies — authentication
decides WHO may submit; the deterministic authority decides WHAT results; witnesses prove what happened.
**The scheme:** message digest `SHA-256("URDRAIN1" | six signed i64 BE)`; keypair = 256 preimage pairs
`sk[i][b] = SHA-256("URDRKEY1"|seed|u32BE(i)|u8(b))`; pubkey `"URDRPUB1" | 256 hash pairs` (16,392 B);
roster pin = `SHA-256(pubkey)` committed pre-session; sign = reveal one preimage per digest bit
(MSB-first — the frozen indexing law); verify = pubkey-hashes-to-pin, then 256 hash comparisons. Why a
SIGNATURE and not a MAC: the verifier holds only hashes, so no verifier — including a malicious fellow
peer — can forge. The OTS one-time rule (reuse leaks preimages) is enforced STRUCTURALLY at admission by
N2's identity-uniqueness law: one keypair per `(peer, seq)`, a second distinct envelope is refused.
**Gated** (`netcode_auth`, 4 rows): the fully signed canonical log reproduces the N1 golden `fea3b967…`
×2 (authentication changes eligibility, never state law — the strongest single check in the stage); the
roster root reproduces its pin `847292e2…` ×2 (pins keygen + pubkey serialization + ordering,
`conformance_auth.txt`); four forgery shapes — bit-flipped signature, stolen signature on an altered
payload, unregistered identity, rogue self-consistent pubkey — each a typed `AUTH-REFUSE`, rejected
whole; and non-vacuity: a defect verifier checking only the FIRST digest byte ACCEPTS a deterministic
tail-collision forgery the real verifier refuses (all 256 bits are load-bearing). Red-first:
`tests/test_authinput.py` (9 falsifiers) went RED (`ModuleNotFoundError: authinput`) before the module
existed; also gated: a late SIGNED envelope still rewinds and converges (N3 composes with N2). Unit
falsifiers 290 → 299. **Grade: MEASURED (reference).** **Honest scope:** the gate pins the MECHANISM —
verification gates admission — on fixture keys from PUBLISHED seeds (deterministic on purpose);
operational key secrecy, key distribution, and cross-session replay protection are OUT of scope and not
claimed; envelopes are large (8 KB sig / 16 KB pubkey — the price of hash-based signatures, irrelevant at
gate scale, stated). **Second placement — written + C-cross-checked, SPECULATIVE pending host.**
`tools/netcode/authinput_rs/authinput.rs` (std-only Rust, hand-rolled SHA-256; scope stated in its header:
it pins the AUTH surfaces — keygen/pubkey/roster/sign/verify laws, eligibility gating, four refusal
shapes, the first-byte defect — while the transcript law it feeds is the already-cross-placed N1/N2
machinery). Its logic was cross-checked **bit-identical by an independent C99 port** (`__int128`, own
SHA-256, clean `-Wall -Wextra`): roster root `847292e2…` ×2, signed chain `fea3b967…` ×2, refusals
`bitflip=1 stolen=1 rogue_pubkey=1 genuine_ok=1`, and the deterministic tail-collision forge landing at
**dvx offset 423** with real=refuse / defect=accept — a value the Rust must reproduce exactly, giving the
placements a shared anchor even on the forgery. Only a host `rustc` run separates it from admission; the
envelope/roster contracts freeze in D12 only after that `ADMITTED`. `who may speak is a hash question
now; what happens next never was one`.

**N3 admission + freeze — MEASURED (both placements); `urdr-netcode-auth 0.1` FROZEN.** **CONFIRMED on
host:** on Windows (`rustc -O authinput.rs`) `authinput.exe` printed `URDR-AUTH-RS: ADMITTED` — roster
root `847292e2…` ×2, signed chain `fea3b967…` ×2, refusals `bitflip/stolen/rogue_pubkey/genuine` all
correct — and `--defect` found the tail-collision forgery at **dvx offset 423**, the SAME value the
independent C99 port found, with real=refuse / defect=accept in both: the placements agree on the
goldens, the refusal shapes, AND the exact forgery (commit `8018473`). D12 accordingly freezes
`urdr-netcode-auth 0.1`: the message-digest law (`URDRAIN1`), pubkey serialization (`URDRPUB1`), roster
pin + root laws (`URDRROS1`), the MSB-first bit-indexing, sign/verify semantics, seeded key derivation
(`URDRKEY1`/`URDRSEED`, normative for deterministic keys), `AUTH-REFUSE` whole-rejection, and the
structural one-time rule — immutable except through a versioned successor; `conformance_auth.txt` (2
vectors) joins the mechanically-checked manifest (the auth laws are pinned BEHAVIORALLY by
`roster3`/`arena3_signed` — a keygen, serialization, indexing, or verify change moves those digests and
reds the gate). Rule-10 combing: the `digest ≠ MAC` "declared successor" notes in `lockstep.py`,
`rollback.py`, and D11 flip to delivered. The netcode story is now complete through its trust boundary:
`N1 proves the same inputs make the same history; N2 proves a late truth replays into it; N3 proves only
the entitled may write it — and all three are two-placement laws`.

**urdr-netcode N4 — AUTHORED WORLDS in the deterministic netcode loop — MEASURED (reference);
cross-placement DECLARED.** `tools/netcode/worldstep.py` takes the architecture from deterministic demos
to user-authored deterministic scenes with ZERO authority semantics changed: a frozen `URDR-WORLD-3`
export becomes the initial state of an input-driven bounded fixed-point runtime whose chains obey the
frozen laws unchanged (`URDRLST1` witnesses via `lockstep._digest`, `URDRLSTT` traces via
`lockstep.trace_digest`, the N1 canonical merge via `lockstep.canon`) — new capability as a new CONSUMER.
**The anti-drift pin is an equivalence theorem, gated:** on the canonical arena (same bodies, box,
gravity, restitution, no statics) `worldstep.simulate` reproduces `lockstep.simulate`'s chain
**bit-for-bit** over the canonical log — the N4 tick mirrors the frozen N1 tick exactly, and statics are
a pure extension proven inert where absent. **What N4 adds:** static AABB obstacles (authored medians/
walls) with a deterministic least-penetration face resolution (fixed tie order top/bottom/left/right,
position clamp + toward-guarded restitution reflection, exact FP-word comparisons); a **typed authoring
boundary** — a non-integer coordinate in the export is `WORLD-REFUSE`, never a silent round (D11 §4b
made operational); and the stated law that **instance file order is content** (it fixes body indexing —
reordering is a different world, gated). Loader mapping law pinned in the docstring: dynamics →
(ground_x, ground_z) bodies with (vel.x, vel.z), radius = scale·max|coord|; statics → AABBs; 640×360
box, margin 24, top-down gravity (0,1), e=3/4, T=120; mass loaded but INERT until body-body contact
arrives (DECLARED, stated). **Gated** (`netcode_world`, 5 rows): the `highway` golden `e72e75c3…` ×2
(`conformance_world.txt`; the no-statics defect run diverges to `9c0ad7c5…` — the median is
load-bearing); the equivalence pin; the boundary row (float refused + order matters); peers-agree on
authored state; and the selftest (no-statics defect diverges AND a dropped input desyncs localized while
the clean run does not). Red-first: `tests/test_worldstep.py` (7 falsifiers) went RED
(`ModuleNotFoundError: worldstep`) before the module existed. Unit falsifiers 299 → 306. **Grade:
MEASURED (reference).** **Honest scope:** regime B (rounds honestly, refuses on overflow); body-body
contact and rollback/auth composition over authored worlds are the natural next slices (the runtime
shares `simulate(w, log)` shape with N1, so N2/N3 composition is mechanical, but it is NOT claimed until
gated); cross-placement DECLARED — freeze after admission, per the ladder. **Second placement — written +
C-cross-checked, SPECULATIVE pending host.** `tools/netcode/worldstep_rs/worldstep.rs` (std-only Rust,
hand-rolled SHA-256; honest scope in its header: it pins the RUNTIME — the N4 tick, the static-AABB
least-penetration law, the frozen witness laws — on the mapped canonical scene; the JSON loader's mapping
law stays reference-gated, its mapped output being exactly the constants the placement embeds). Its logic
was cross-checked **bit-identical by an independent C99 port** (`__int128`, own SHA-256, clean
`-Wall -Wextra`): arena equivalence `fea3b967…` (the N4 tick reproduces the FROZEN N1 chain in a third
language), highway `e72e75c3…` ×2, and `--defect` diverging to **exactly `9c0ad7c5…`** — the same
divergent digest as the Python reference, a three-way anchor on the failure mode itself. Only a host
`rustc` run separates it from admission and the D12 freeze. `the editor draws a world; the loop makes it
law: same scene, same inputs, same witnesses, on every machine`.

**N4 admission + freeze — MEASURED (both placements); `urdr-netcode-world 0.1` FROZEN.** **CONFIRMED on
host:** on Windows (`rustc -O worldstep.rs`) `worldstep.exe` printed `URDR-WORLD-RS: ADMITTED` — arena
equivalence `fea3b967…` (the N4 tick reproduces the FROZEN N1 chain on a third host/second language),
highway `e72e75c3…` ×2 — and `--defect` diverged to exactly `9c0ad7c5…`, matching the Python reference
and the C99 port: a three-way anchor on the failure mode (commit `20ae01c`). D12 accordingly freezes
`urdr-netcode-world 0.1`: no new witness serialization (URDRLST1/URDRLSTT reused — contractual); the
loader mapping law (dynamics → bodies at (ground_x, ground_z) with (vel.x, vel.z), radius =
scale·max|coord|; statics → AABBs; 640×360/margin-24 box; top-down gravity; e=3/4; T=120); the typed
authoring boundary (`WORLD-REFUSE` on non-integer coordinates — never a silent round); instance file
order as world identity; and the static-AABB least-penetration resolution law (fixed tie order, clamp +
toward-guarded reflection) — immutable except through a versioned successor; `conformance_world.txt`
joins the mechanically-checked manifest. **Honest scope unchanged:** runtime cross-placed on the mapped
scene; the JSON loader itself is reference-gated (Python); mass inert until body-body contact arrives.
Netcode now runs four two-placement rungs deep: `the transcript is law (N1), late truth replays into it
(N2), only the entitled write it (N3), and the world it governs is yours to draw (N4)`.

**Front-end OODA pass — the editor meets the gated runtime — worldstep 0.2 (additive) MEASURED; editor
layer SPECULATIVE as ever.** One explicit Observe–Orient–Decide–Act cycle over `tools/editor/` under
YAGNI + the no-gloss guardrail, kills stated: input/scenario-track authoring KILLED (no gated consumer of
a scenario format yet — earns its rung when one exists); all renderer/shader gloss KILLED on sight.
Three increments survived adversarial review, all landed red-first where gate-able. (1) **The known
`replay.py --world` bug is dead** — the handoff's `resolve()` NameError was a missing import of the
FROZEN `contact_lcp.resolve` (the λ→velocity mapping it feared was already built and cross-placed at
rung 3); fixed one-line, verified live: the canonical highway export runs 91 exact frames, momentum
conserved, 2 LCP contacts resolved, chain deterministic ×2. (2) **`worldstep 0.1 → 0.2` (additive,
minor):** `simulate_trace` returns the identical frames plus display-only per-frame `(pos, vel)`
snapshots; digest-preservation proven the strong way — every 0.1 gate vector (highway golden, arena
equivalence, defect) byte-identical, plus a new falsifier pinning `simulate_trace ≡ simulate`
(red-first: `AttributeError` before implementation; unit falsifiers 306 → 307). (3) **`replay.py
--net <export>`** runs the authored scene in the GATED N4 runtime and emits a `URDR-REPLAY-1` doc the
editor scrubs — URDRLST1 witnesses, the URDRLSTT trace printed, deterministic ×2 self-checked
in-process; display floats derive from the Q32.32 words (drawing only), display mass 1 with the
momentum overlays explicitly disclaimed — the witness chain is the authority. (4) **The authoring
boundary closed at the source:** the designer exported `scale` as a 3-decimal float — the one
runtime-consumed field that escaped `Math.round` — so a scaled object produced exports the N4 loader
correctly `WORLD-REFUSE`d; the export now integer-snaps `scale` like every other consumed field and
says so in its export message (authoring snaps; the runtime never rounds — D11 §4b, both sides).
**Grades:** worldstep 0.2 additive `MEASURED` (gate 307/0 ×2, byte-identical runs); `replay.py --net` /
designer changes remain `SPECULATIVE`/exploratory (the editor is a consumer, not a rung — its value is
that what it *feeds* and *reads* is now the measured runtime). `the front end earns nothing; it borrows
everything from the gate — and now it borrows from the right engine`.

**urdr-netcode N5 — AUTHENTICATED ROLLBACK OVER AUTHORED WORLDS — MEASURED (reference);
cross-placement DECLARED.** The platform sentence, composed and gated: *given the same authored world,
the same authenticated input transcript, and the same initial snapshot, every conforming implementation
either converges to the identical witness chain or produces the same typed refusal — no intermediate
divergence silently persists.* `tools/netcode/worldpeer.py` builds nothing below the interface line — it
COMPOSES the four admitted rungs, importing their laws rather than restating them (N2's `RollbackError`
type, N3's `verify`, N4's tick via `worldstep.step_tick`, N1's witness laws), and adds exactly ONE new
law: the **world pin** (`URDRWPN1` — SHA-256 over the canonical runtime world: bodies, radii, statics,
bounds, gravity, restitution, T), because "wrong world refuses BEFORE simulation" needs identity coverage
`frames[0]` cannot give (two worlds differing only in a static share their initial witness — the
falsifier proves the pin distinguishes them). **worldstep 0.2 → 0.3 (additive):** `step_tick` extracts
the one tick law for incremental consumers; digest-preservation proven by every existing vector passing
byte-identical. **Gated** (`netcode_worldpeer`, 6 rows): world pin `8c4fe8d4…` + scenario roster root
`d30e7279…` pinned (`conformance_worldpeer.txt`); the late+signed canonical scenario converges to
**the N4 highway golden `e72e75c3…`** at K=4 (×2) and K=8 — authentication decides eligibility, rollback
replays the canonical timeline, neither touches state law; refusals row (wrong-pin `WORLD-REFUSE` before
any tick, tampered envelope `AUTH-REFUSE`, beyond-horizon `ROLLBACK-REFUSE` with the chain untouched);
and the defect: a **verified** late envelope applied at the head (auth passes — the failure is
rollback's alone) MUST diverge. Red-first: `tests/test_worldpeer.py` (11 falsifiers) went RED
(`ModuleNotFoundError: worldpeer`); unit falsifiers 307 → 318. Also adopted this rung, AGENTS.md rule
11 — **the completion rule**: no capability is complete until its transcript is frozen, its refusals
specified, its corpus exists, and an independent implementation reproduces it. **Honest scope:**
inherited whole from N1–N4 (published fixture seeds — mechanism, not key secrecy; regime B rounding;
inert mass; K/H operational); cross-placement DECLARED — the composed contract freezes in D12 only
after an independent placement reproduces the converged golden + the defect on a named host. **Second
placement — written + C-cross-checked, SPECULATIVE pending host.** `tools/netcode/worldpeer_rs/
worldpeer.rs` (std-only Rust; machinery composed from the four ADMITTED placements — SHA-256/Q32.32
from all, Lamport from `authinput_rs`, the N4 tick + highway constants from `worldstep_rs`, the
snapshot/rewind peer from `rollback_rs`; only the URDRWPN1 pin is new). Cross-checked **bit-identical by
an independent C99 port** (`__int128`, own SHA-256, clean `-Wall -Wextra`): pin `8c4fe8d4…`, roster
root `d30e7279…`, converged late+signed trace `e72e75c3…` at K=4 (×2) and K=8, refusals
`world/auth/horizon/untouched/conflict` all typed, and `--defect` (a VERIFIED envelope applied at the
head) diverging to **exactly `d5bc484b…`** — the same divergent digest as the Python reference: three
implementations agree on the composed contract's success AND its failure mode. A host `rustc` run is
the admission; the D12 freeze follows it. `five rungs, one sentence: your world, your signed inputs,
one history — or a refusal that says its name`.

**N5 admission + freeze — MEASURED (both placements); `urdr-netcode-worldpeer 0.1` FROZEN — the first
rung completed under rule 11 after rule 11 was written.** **CONFIRMED on host:** on Windows
(`rustc -O worldpeer.rs`) `worldpeer.exe` printed `URDR-WORLDPEER-RS: ADMITTED` — pin `8c4fe8d4…`,
roster `d30e7279…`, converged late+signed trace `e72e75c3…` at K=4 (×2) and K=8, all five refusal flags
true — and `--defect` diverged to exactly `d5bc484b…`, matching the Python reference and the C99 port:
three implementations agree on the composed contract's success and its failure mode (commit `1ad5034`).
D12 accordingly freezes `urdr-netcode-worldpeer 0.1`: the URDRWPN1 world-pin law; the verify-then-admit
order (authentication strictly before the authority, world identity strictly before authentication's
first delivery); the inherited snapshot/rewind/replay and refusal laws (named, not restated); no new
witness serialization; `conformance_worldpeer.txt` (3 vectors) joins the mechanically-checked manifest.
By rule 11's own definition N5 is COMPLETE: transcript frozen, refusals specified, corpus exists,
independently reproduced. The netcode stack closes at five two-placement rungs; the platform sentence —
authored world, authenticated transcript, one witnessed history or a named refusal — is now a frozen,
machine-checked, cross-placed property of this repository rather than a description of it.

**D13 — the glyph probe — REVIEW RECORD (asserts no grade above REVIEW; adds no syntax).** A
first-principles D6-method sweep of sixteen primitive candidates from the engine and the recurring
irreducibles of adjacent fields (linear logic, separation logic, LTL/TLA+, CRDTs, algebraic effects,
dependent types, ACID durability, interval numerics, lenses, quotient types, and the rest), each tested
against five admission criteria — new semantic law, verifier change, new refusal/witness/capability
class, cross-placement necessity, earned pressure — with the sealed kernel as the null hypothesis.
**Outcome: zero admissions.** One deferral with teeth: C4 linearity (use-exactly-once), the only
candidate passing tests 1–4, deferred on test 5 with pre-registered re-open triggers (Phase-4 capability
hand-off, or a second consumer distorted by dynamic enforcement) and pre-registered falsifiers
(`URDR-LINEAR` static refusal naming use sites; linearity as a property of the canon; a cross-placed
accept/refuse program corpus with a miscounting checker caught). Two rejections recorded as
load-bearing absences: catchable refusals (C2) and effect handlers (C10) would each launder the
no-inflation and līmes laws. Empirical anchor: N2–N5 plus a full signature scheme entered the system
this week as pure consumers of existing law — the strongest available evidence the alphabet is
sufficient for everything the gate currently proves. `the probe earned no glyph, deferred one honestly,
and wrote down the conditions under which it would change its mind`.

**C4 staging apparatus (D13 §3) — IMPLEMENTED / MEASURED as a staging study; the glyph remains
UNADMITTED and ungraded.** Built ahead of need so a fired trigger meets a measured floor, and
explicitly NOT an admission — the request to "create the glyph" was refused per D13's own
pre-registered triggers (unfired) and the §20 law; what was created is the review instrument.
`tools/linear/linear_core.py`: the reference multiplicity judgment over a deliberately minimal core
(NEW/USE/DROP/DUP/IF/SKIP/END — its own term language, zero Urðr syntax, kernel untouched), with
static `URDR-LINEAR` refusals that NAME their sites, the affine/linear fork implemented as a mode so
both directions stay falsified until the review decides, canon-quotiented program identity
(`URDRLIN1` digest law; case/whitespace noise → one digest, one verdict), and deterministic
first-refusal-wins walking. `corpus_linear.txt`: 14 programs, verdicts pinned across both modes.
Red-first: `tests/test_linear_core.py` (9 falsifiers) went RED (`ModuleNotFoundError: linear_core`)
before the module existed — and the staging itself caught a real law defect: the naive IF
branch-consistency comparison over-refused matching arms by comparing site provenance instead of
consumption status (two corpus programs reddened; the law was corrected to status-multiset equality
with canonical arm-A merge). The miscounting defect probe (counts only first use) accepts what the
real judgment refuses — the detector bites. Unit falsifiers 318 → 327. **Honest scope:** this core
isolates multiplicity + branch splitting only — no functions, no data flow, no borrows; the Urðr
binder generalization, the affine-vs-linear decision, and an independent placement are §20 review
work, gated on D13's triggers, which remain unfired. `the bar did not move; the runway to it did`.

**Editor ⨀ Walk mode — SPECULATIVE / exploratory (no gate claim; the editor layer as ever).** A
first-person preview in `urdr_designer.html`: pointer-lock WASD+mouselook over the authored world
(silhouettes standing on the road, the `load_world.py` base-at-ymax convention) or, with a replay
loaded, over the ENGINE'S WITNESSED FRAMES — bodies drawn at recorded positions, the frame's URDR
digest on the HUD, R/[ ] transport. Eye height / speed / focal / replay-scale sliders (the "scaling"
surface); same pinhole family as the exact projector; input guards keep Walk from touching the
editing handlers. Honest scope stated on-screen, in the README, and here: a FLOAT projection that
edits nothing and simulates nothing — the deterministic runtime and witness chain remain the sole
authority. Concept provenance: the first-person/"render is a projection of authority" ideas from the
Weltwerk workbench demos, admitted only in their discipline-compatible form; splat rendering and the
manifold panels stayed where they were (renderer gloss — the standing guardrail). Verified: the walk
block parses standalone (node --check); interactive behavior is the exploratory layer's to confirm in
a browser — claimed accordingly, which is to say: not.

**Editor→exact-render seam — the consumer-side smoke test — MEASURED.** The last unwatched seam in
the authoring pipeline, now a gate row: the canonical `URDR-WORLD-3` export (`demo/world_highway.json`)
rendered through `load_world.render` (float authoring snapped to integers — the canonical scene has NO
rotations, so composition is bit-deterministic IEEE add/multiply/round) and the EXACT floor-division
projector must reproduce its pinned `URDRFB1` digest ×2 (`highway_frame 162a6204…`,
`tools/editor/conformance_editor.txt`, in the D12 freeze manifest — 14 corpora). Red-first paid twice
before the golden existed: (1) `load_world.render` **crashed on the canonical scene**
(`KeyError: 'edges'` — hand-authored hulls carry no edges, which D12 marks optional; fixed with a
stated default, the closed vertex loop — never a silent guess); (2) the moved-median divergence probe
exposed that the **uncentered camera rendered the median and east car off-screen** — the pin could not
see two-thirds of the scene it certified (fixed: integer scene-centering onto the optical axis;
rehearsal now shows every instance's movement diverges the digest). Falsifiers:
`tests/test_load_world.py` (3 — golden ×2, moved-instance divergence, perturbed-vertex divergence).
Unit falsifiers 327 → 330. **Honest scope:** certifies the PIPELINE on the canonical export; the
browser editor stays SPECULATIVE; scenes WITH rotations bring float trig into composition and are not
covered by this pin. `an unwatched seam broke twice on first watching — which is the whole argument
for watching`.

**Observability rung 1 — A/B replay compare in the editor — SPECULATIVE / exploratory (the editor
layer as ever; no gate claim).** ▷ Replay gains a second slot: load run B beside run A and the
first-desync law becomes visible — a per-frame divergence strip (green ≡ / rust ≠ over the RECORDED
chains), the first-desync tick marked with a jump-to button, B's bodies ghosted over A's, and both
witness digests side by side at the scrubbed frame. The browser's comparison mirrors
`lockstep.first_desync` exactly and was behaviorally spot-checked against the reference semantics
(identical → none; first differing index; length mismatch → shorter length) under node; the display
compares recorded strings and re-simulates NOTHING — chains in, pixels out. Honest scope: ghost
positions are display-fit coordinates (comparable for same-scene runs; the chains, not the pixels, are
the authority — stated on-panel); the strip visualizes what N1–N5 already prove. `two runs walk in; the
first lie between them gets a timestamp`.

**photo_trace — photo/still → wireframe design tracer — deterministic core MEASURED; aesthetics not
claimed.** `tools/tracer/photo_trace.py` turns a silhouette in an image into a content-addressed
`URDROBJ2` design the browser editor opens directly (⤒ Open). Stdlib-only, no dependencies: PNG is
decoded FROM SCRATCH via `zlib` (IHDR/IDAT/IEND chunks, all five scanline filters, grayscale/RGB/RGBA
8-bit), netpbm (PGM/PPM) by hand; a format the stdlib cannot decode (JPEG needs a DCT, GIF needs LZW)
is a typed `TRACE-REFUSE` — refuse, never a silent dependency (the project's stdlib discipline held
under direct pressure: the request was "based on a photo", photos are JPEG, and the answer was still
refuse-and-convert). Pipeline, every step deterministic: decode → Otsu threshold → largest 8-connected
component → Moore boundary trace → Ramer–Douglas–Peucker simplify (deterministic ε binary-search to a
target vertex count) → integer snap. **The load-bearing, gate-checked invariant:** identity is minted
by the SAME canon the editor uses — `SHA-256("URDROBJ2|v{n}|x,y,z|…|e{m}|a-b|…")`, edges min-first +
lex-sorted — pinned to the digest the ACTUAL browser `canonBytes` produces (computed in node,
`square_canon dc086bf1…`, `conformance_tracer.txt`), so a CLI-traced design and the editor agree
bit-for-bit. Gate stage `photo_trace` (4 rows): the browser-canon match, edge order-invariance, a
decode+refusal spine (PGM round-trips, JPEG magic `TRACE-REFUSE`d), and the non-vacuity defect (an
un-normalized-edge canon MUST diverge — the min-sort is load-bearing). Red-first:
`tests/test_photo_trace.py` (9 falsifiers, incl. a synthesized-PNG decode exercising the from-scratch
zlib path) went RED (`ModuleNotFoundError: photo_trace`). Unit falsifiers 330 → 339. **Grade:** the
DETERMINISTIC CORE (decode, canon-law identity, refusals, integer output) is MEASURED; the AESTHETIC
QUALITY of a trace is NOT gate-able and is NOT claimed — the tool is an authoring aid, SPECULATIVE like
the editor it feeds. Honest scope: single image → one design (multi-frame/animation is a declared
extension); the trace is a silhouette outline, not interior structure. `the stdlib draws the outline
the photo already had; identity is minted the one lawful way, so the tool and the editor never disagree
about what they made`.

**D14 — the front-end admission contract — MEASURED (the checkable core).** When multiple independent
authoring modalities converge on one authoritative representation, the convergence itself becomes a
law. `spec/D14-frontend-contract.md` states the single admission criterion — deterministic
normalization → reproduce the `URDROBJ2` canon through the front end's OWN implementation →
integer-snapped geometry → typed refusals → **provenance is metadata, not identity** — with a 7-step
admission ladder (the placement discipline, D8, applied to front ends). `tools/frontend/canon_ref.py`
is the executable form: the reference canon + the integer/`CONTRACT-REFUSE` obligation + the
geometry-only identity extractor. **Gated** (`frontend-contract`, 4 rows): the reference canon
reproduces the BROWSER goldens over a four-shape corpus (`conformance_frontend.txt`
square/tri/penta/hex6, each cut from the actual designer `canonBytes` in node); the photo tracer's
INDEPENDENT `design_digest` reproduces the same corpus (three implementations — browser, reference,
tracer — one identity law); **provenance-independence** — identical geometry with differing provenance
yields the identical digest, so downstream physics/render/replay/netcode cannot tell which front end
made an object; and the non-vacuity defect (a provenance-folding canon MUST diverge; non-integer
geometry MUST `CONTRACT-REFUSE`). Red-first: `tests/test_frontend_contract.py` (6 falsifiers) went RED
(`ModuleNotFoundError: canon_ref`). Unit falsifiers 339 → 345. **Grade: MEASURED** for the identity
law and the admission obligations; the AESTHETIC quality of any front end's extraction is out of scope
and not claimed. The two admitted modalities today (designer + tracer) are honestly two, not more —
the designer's procedural primitives are internal to it; SVG/CAD/procedural importers are `DECLARED`,
each to arrive down this ladder. `any modality that deterministically normalizes to the canon is a
first-class asset source, inheriting physics, rendering, replay, and witnesses without touching the
engine — the importer is interchangeable; the object is not`.

**SVG → canonical — the first front end admitted down the D14 ladder — MEASURED (deterministic core).**
`tools/frontend/svg_import.py` imports a declared SVG subset — `<line>/<polyline>/<polygon>/<rect>` and
`<path>` with `M/L/H/V/Z` + cubic `C` — to a canonical `URDROBJ2` design the editor opens (⤒ Open),
using the shared `canon_ref` law so CLI ≡ editor identity. SVG is the ideal first exercise of the
contract because it is MORE deterministic than the photo tracer: vector paths are already
integer-snappable polylines, so there is no threshold/contour/aesthetic step — only stdlib
`xml.etree` parsing, fixed-tolerance cubic flattening (`FLATTEN_SEGS=16`, a frozen part of the format,
not a runtime knob), integer snap, and the canon. **Gated** (`svg_import`, 3 rows): **three SVG
constructs of one square** (`<polygon>`, `<rect>`, `<path M/L/H/V/Z Z>`) reproduce the shared D14
`square` golden — one canonical object from three inputs, the convergence made literal at the SVG
level; a cubic-bezier arch path flattens deterministically to its pinned `arch` golden
(`conformance_svg.txt`); and the four out-of-subset constructs (arc `A`, element `transform`, the
`<circle>` primitive, a malformed path) are each typed `SVG-REFUSE` — refuse, never approximate (D14
obligation 4). Red-first: `tests/test_svg_import.py` (10 falsifiers) went RED
(`ModuleNotFoundError: svg_import`); staging caught one honest spec point — a `<polyline>` is OPEN by
SVG semantics (n verts, n−1 edges), so it is NOT closed-by-guess (my first test wrongly expected a
loop; corrected to match SVG, not convenience). Unit falsifiers 345 → 355. **Grade: MEASURED** for the
deterministic core; D14's aesthetic-quality exclusion applies. The importer entered as a pure consumer
under the contract — **the first proof that the D14 ladder works: a new authoring modality became a
first-class asset source without touching the engine, the canon, or any other front end.** `SVG says
square four ways; the canon says square once`.

**Observability — rigidity verdict for canonical objects — MEASURED (and it IS authority, not a display
float).** Phase-2 observability, the increment the architecture makes uniquely cheap: every canonical
`URDROBJ2` object is a 2D rigidity framework `(n, d=2, edges, coords)`, so `tools/frontend/
rigidity_verdict.py` answers — over ℤ, exactly — *is this structure RIGID or does it FLEX, by how many
degrees of freedom, and which vertices move?* It consumes the exact-integer rigidity layer
(`tools/intla/rigidity`, cross-placed via urdr-math), so the verdict is a CERTIFICATE reproducible on
every conforming host — unlike the replay overlays, which draw float projections of Q32.32 words, this
is authoritative. **Gated** (`rigidity_verdict`, 3 rows): the classic frameworks classify to pinned
certificates (`conformance_rigidity.txt`) — triangle RIGID (dof 0), bare square FLEXIBLE (dof 1, the
shear mode), square+diagonal RIGID, square+2-diagonals RIGID (over-braced, rank saturates at 5 with a
self-stress); a FLEXIBLE verdict NAMES its moving vertices (the internal-flex vector); and the
non-vacuity defect — a checker comparing rank to the FULL dimension `d·n` instead of the rigid rank
`d·n − d(d+1)/2` misclassifies the rigid triangle, proving the trivial-motion subtraction is
load-bearing. Red-first: `tests/test_rigidity_verdict.py` (7 falsifiers) went RED
(`ModuleNotFoundError: rigidity_verdict`). Unit falsifiers 355 → 362. **The architecture's law held on
the display side too:** the AUTHORITY computes (Python, exact, gated), the editor DISPLAYS — a
recorded verdict badge (● rigid / ◍ flexible+dof / ⊘ refuse) in the designs palette, read from a
`rigidity` field the CLI's `annotate` writes, never recomputed in browser float. **Grade: MEASURED**;
the verdict inherits urdr-math's overflow `REFUSE`. `the engine already knew which structures hold and
which shear — observability just asked it out loud, and it answered with a certificate`.

**D15 — the view-export contract (authority → renderer) — MEASURED (checkable core); NOT frozen.**
Layer 2 of the three-layer split (Authority / View contract / replaceable Presentation renderer): the
bridge that lets photorealism live entirely in layer 3 without touching the moat. `tools/frontend/
view_export.py` derives a `URDR-VIEW-1` frame from an authoritative frame + declared static scene
metadata (obj/material/light/camera), and the frame CARRIES the authoritative witness — the view is
bound to, and subordinate to, the authority it depicts; body transforms are READ from authority (a
scene cannot relocate a body the authority placed) and a body-count mismatch is `VIEW-REFUSE`. **The
load-bearing invariant, now a checked law:** *presentation outputs are observational only* — encoded
as a falsifier (`view-export-observational`): a material change moves the VIEW digest (presentation is
visible to renderers) but leaves the carried witness UNCHANGED (presentation cannot touch authority),
and the non-vacuity defect — an exporter that folds material INTO the witness — is detectably
different. **Gated** (`view_export`, 4 rows): deterministic export to a pinned golden
(`conformance_view.txt canonical 28f821fe…`), the binding (a view claiming a different authoritative
frame fails), the observational-only invariant + defect, and the refusal. Red-first:
`tests/test_view_export.py` (6 falsifiers) went RED (`ModuleNotFoundError: view_export`). Unit
falsifiers 362 → 368. **Grade: MEASURED** for the contract's core; **NOT frozen** — per the ladder
(and the human's step 3) the schema freezes only once an INDEPENDENT consumer (a three.js reference
viewer) reproduces the exported state. Renderer quality (PBR/HDR/GI/RT) is layer 3, out of scope; D15
says WHAT to draw and binds it, never how well. The distinctive, gate-provable property: `replacing or
upgrading the renderer never changes gameplay or replay validity — because the renderer was never a
source of truth`.

**D15 step 2 — the independent viewer (a placement of the view contract) — reproduces the export.**
`tools/frontend/view_viewer.html` is the reference presentation consumer AND an independent placement:
a **self-contained** viewer (no CDN, no Web Crypto — it **hand-rolls SHA-256** like the Rust/C
placements and renders on a plain canvas, so it runs from a double-clicked `file://`) that loads a
`URDR-VIEW-1` document, **recomputes each frame's `view_digest` with its own code** (byte-identical to
`view_export.py`'s — confirmed in node over every frame of the real 121-frame highway export, all 121
verified / 0 refused), verifies the witness binding, and REFUSES to render any document with an
unverified frame — turning the viewer into a participant in the verification story (its report emits
contract version / frame count / witnesses verified / frames refused / export digest / viewer version,
the human's "viewer-as-placement" idea). Observational-only by construction: it never writes back. The
reference viewer is dependency-free like the whole repo; heavy renderers (three.js/Unreal/Godot/Vulkan)
are downstream clients of the same documents, made safe precisely because D15 proves none can leak
upward. (First cut used a CDN three.js + Web Crypto and silently failed on `file://` — both hazards
removed; the self-contained rewrite is the disciplined, offline-consistent form.)

**D15 admission + freeze — CONFIRMED on host; `urdr-view 1` FROZEN.** The independent viewer reported
**121/121 frames verified, 0 refused** on Windows, reproducing the exported state through its own
hand-rolled SHA-256 and canonical serializer — the D8 named-host admission applied to the view layer,
and the human's "viewer-as-placement" idea realized: the consumer is a checker, not a display. D12
accordingly freezes `urdr-view 1`: the `URDR-VIEW-1` schema, the canonical serialization + digest, the
binding law (`VIEW-REFUSE`), and the observational-only invariant — immutable except through a
versioned successor. The symmetry is now complete and both boundaries are provably one-way: **D14
converges many authoring modalities to one canonical object; D15 fans one authoritative state to many
interchangeable renderers** — the input side and the output side of an engine whose notion of truth
never fragments regardless of which tools or renderers are plugged in. `the engine never knows which
tool authored an object or which renderer draws it — and that ignorance is the guarantee`. `view_export.py` gained
`export_doc` (per-frame `view_digest`, gated: `view-export-doc` round-trip) + a `--doc` CLI. Unit
falsifiers 368 → 369. **D15 is at step 2** (an independent placement reproduces the digest in node);
per the ladder and the human's step 3, **the freeze waits for the browser viewer to report
all-frames-verified on a host** — the D8 named-host admission, applied to the view layer. `the input
side converges many tools to one object (D14); the output side fans one authority to many renderers
(D15) — and the first renderer proved it can only ever read`.

**N4.1 — body-body contact in the authored runtime — MEASURED (reference); cross-placement DECLARED.**
N4 shipped authored worlds with one honest debt, stated in its own grade: dynamic bodies collided with
static AABBs but NOT with each other, so instance mass was inert (DECLARED, not hidden). N4.1 pays that
debt down as an **opt-in, additive** capability — worlds set `contact: True`; everything already frozen
runs contact-OFF, byte-identical. The resolution is a **sqrt-free Q32.32 impulse**: the un-normalized
normal `d` cancels its own `|d|` (the exact `d/|d|` trick ported from `dynamics_nd.resolve_spheres` into
fixed point), so no square root is ever taken and the whole pass is exact integer arithmetic over the
frozen `field.FixedPoint`. One deterministic pass in canonical `(i<j)` order; equal unit mass ⇒ the
inverse-mass sum is 2, folded into the divisor. **Red-first:** `tests/test_worldstep_contact.py` (6
falsifiers) went RED before the pass existed. **What the gate pins** (`netcode_world`, 3 new rows):
`netcode-world-contact:collide2` reproduces the pinned trace golden `04bdeec4…`
(`conformance_world.txt`, now 2 vectors) deterministically; `netcode-world-contact-loadbearing` shows
contact-ON and contact-OFF diverge (the pass is load-bearing, not decorative);
`netcode-world-contact-momentum` is the **physics witness** — over the wall-free `collide2` scene
x-momentum `v0.x + v1.x` is conserved EXACTLY (`{0}`) while the closing velocity reverses sign (a real
collision, restitution e=3/4), **and** the asymmetric-impulse defect (impulse applied to one body only)
BREAKS momentum, proving the witness is not vacuous. **Frozen surface preserved and gate-proven:** the
arena-equivalence pin (`worldstep ≡ frozen lockstep`, bit-for-bit) and the highway golden
`e72e75c3…` are unchanged — contact defaults off, so the frozen 0.1 tick is byte-identical, and the
`test_highway_golden_unchanged` falsifier asserts the authored world never silently enables it. Unit
falsifiers 368 → 374; full gate GREEN, deterministic ×2 (byte-identical modulo wall-clock). **Grade:**
the Python reference is MEASURED (the impulse law, its determinism, momentum conservation, and the
non-vacuity defect are all gate-checked); **cross-placement is DECLARED, not yet done** — the Rust/C99
placements still run the frozen N4 tick without contact, so `urdr-netcode-world` stays FROZEN at 0.1
(the opt-in pass is a reference-only successor pending its second placement). Honest scope: equal-mass,
discrete (per-tick overlap test, no continuous CCD), one pass per tick — enough to make authored worlds
physically interactive, not yet a general contact solver. `the debt N4 named out loud is now paid in the
reference and witnessed by the gate; it is not yet cross-placed, and the ledger says so`.

**D16 — the regional-authority contract (one simulation, partitioned in space) — MEASURED
(reference); cross-placement DECLARED; NOT frozen.** The Phase-3 milestone D13 §C8 parked
until "the D-series regional-authority contract exists and its library realization has been
measured against it." N4.1 was the precondition: only once authored worlds had COMPLETE
physical interaction (body-body contact) was there a complete authoritative simulation to
partition. `spec/D16-regional-authority.md` states the contract; `tools/netcode/worldregion.py`
is the reference; the `netcode_region` gate stage is the measurement. **The law (Seam
Composition Theorem):** for ANY valid partition of a world into spatial regions cut by
integer x-seams, if each region evolves its interior by the FROZEN N4.1 tick from its
admitted boundary conditions alone (read-only ghosts — the neighbour bodies close enough to
touch an owned body this tick), then the deterministic reunification of the regional
interiors reproduces the monolithic URDRLST1/URDRLSTT witness BIT-FOR-BIT. **No new witness
class is minted** (the human's call, and the disciplined one): composition is the frozen
state law recomputed over the reunified interiors — the standing "reuse existing laws unless
one is demonstrably unable to carry the law" rule, and it carried. A region is a **one-way
consumer of its boundary** — the spatial mirror of D14 (authoring→canon) and D15
(authority→view); it reads ghosts, never a neighbour's interior, and writes only what it
owns (a cross-seam pair is resolved by both regions computing the IDENTICAL Q32.32 impulse
and each applying it to its own body — the monolith's single symmetric update, reproduced).
The engine's stated principle made executable: *admissible boundary conditions determine the
evolution of the interior state; internal computation is the deterministic response to
boundary conditions.* **Red-first:** `tests/test_worldregion.py` (10 falsifiers). **What the
gate pins** (`netcode_region`, 5 rows): `netcode-region:seam2` — the composed trace equals
the monolith AND the pinned golden `6d6f6ee3…` (`conformance_region.txt`), deterministically
twice; `netcode-region-invariance` — six different valid partitions (trivial one region, four
single-seam cuts, one three-region cut) all compose to the ONE monolithic witness (the cut's
LOCATION is not content); `netcode-region-boundary` — dropping the ghost exchange makes
cross-seam contact silently vanish, so the chain DIVERGES localized to the exact contact tick
(11) — the boundary is load-bearing; `netcode-region-refusal` — a float / non-monotone / bool
seam is REGION-REFUSEd before a single tick runs, a valid partition accepted;
`netcode-region-nonvacuity` — the seam2 scene really straddles the seam at contact AND a body
really hands off across it (both the ghost-contact and the handoff exercised). The `seam2`
scene: body 0 (fast) catches body 1 (slow), they collide ACROSS the seam at x=191 (momentum
exchanged per N4.1), then body 0 hands off. Unit falsifiers 374 → 384; full gate GREEN,
deterministic ×2. **Grade:** the Python reference is MEASURED (composition, partition-
invariance, the localized dropped-boundary divergence, and the malformed-partition refusal
are all gate-checked); **cross-placement is DECLARED, not done** — a second placement (Rust/C99
reproducing the seam2 composed digest and the dropped-boundary divergence) has not been built,
so D16 is **not frozen** and the D13 §C8 glyph stays parked. Honest scope: synchronous (regions
advance in lockstep, reunify each tick), single-axis (integer x-seams), exact for one cross-seam
contact pair per region per tick (the 2-body scene); multi-pair seam ordering, multi-axis seams,
asynchronous regional clocks, and a composite/frame witness that verifies a region WITHOUT
reunifying are declared successors. `the input side converges many tools to one object (D14); the
output side fans one authority to many renderers (D15); the authority side itself now splits into
many regions that recompose to the one witness (D16) — and none of the three boundaries can leak`.

**D16 second placement (C99) — ADMITTED, self-verified; Rust authored for the Windows host; N4.1
cross-placement UPGRADED.** The freeze precondition (D13 §C8 / the human's step 1) is an independent
placement reproducing `seam2`. `tools/netcode/worldregion_c/worldregion.c` is a self-contained C99
build — its OWN Q32.32 backend, its OWN SHA-256, the N4/N4.1 tick, and the region partition — with no
dependency on the Python. Compiled and run IN THIS SESSION (`cc -O2 -std=c99`, gcc 11.4, Ubuntu 22.04)
it reproduces, **bit-for-bit**: the `seam2` MONOLITH trace == golden `6d6f6ee3…` (an independent build
of N4.1 body-body contact), the `seam2` COMPOSED regional trace == monolith == golden (an independent
build of D16 composition), and the DROPPED-BOUNDARY divergence localized to the same contact tick (11).
Two independent placements (Python reference + C99) now agree on every `seam2` digit — a real
cross-placement, not an assertion, and on a DIFFERENT host and toolchain than the Python gate.
**Consequence for N4.1:** its cross-placement was DECLARED; the C99 `seam2` monolith reproduces the
N4.1 contact impulse bit-for-bit, so **N4.1 body-body contact is now cross-placed (C99), MEASURED** (a
Rust `worldstep_rs` contact extension is still the third-placement follow-on, but the DECLARED debt is
paid). `tools/netcode/worldregion_rs/worldregion.rs` is the Rust placement — the frozen Q32.32 backend
and hand-rolled SHA-256 are reused **verbatim** from the already-admitted `worldstep_rs`; only the
contact pass and the partition are new. It is **authored, not yet run here** (no `rustc` in the session)
— per the D8 discipline it awaits ADMISSION on the named Windows host (`rustc -O worldregion.rs`), which
is the human's stated freeze vehicle. **D16 status:** cross-placed (C99, self-verified) and reference-
MEASURED; **FREEZE at `urdr-netcode-region 0.1` upon the Windows/rustc admission of the Rust placement**
— exactly as D15 waited for its named-host report before freezing. Until then D16 is measured and
cross-placed but not frozen, and the D13 §C8 glyph stays parked. `two placements on two toolchains agree
on seam2 to the last bit; the third, on the house host, is what flips the freeze bit — and the ledger
will not flip it early`.

**D16 FROZEN — `urdr-netcode-region 0.1`; the Rust placement ADMITTED on Windows.** The freeze
vehicle landed: `worldregion_rs` (`rustc -O`, Windows) reproduced the `seam2` monolith, the composed
trace, and the dropped-boundary divergence at tick 11 — bit-for-bit, printing `URDR-REGION-RS: ADMITTED`
(commit `39baacc`). Three independent placements on three toolchains — Python (the gate), C99 (gcc 11.4,
self-verified in-session), and Rust (Windows/rustc) — now agree on every `seam2` digit AND on the failure
mode. Per the D8 named-host discipline the schema, partition/boundary law, and composition law are frozen
at `urdr-netcode-region 0.1` (D12); D16 status flips MEASURED → **FROZEN**. This closes the Phase-3
milestone D13 §C8 opened: the contract was stated, a library was measured against it, and the realization
is independently reproduced — and the answer to *do regional witnesses compose to the global witness?* is
**yes, with no new witness class**, which is precisely why the C8 glyph STAYS parked. The result did not
weaken the seal; it strengthened it — the strongest argument for a primitive (that regional authority
might need one) was tested and refuted. What re-opens C8 is not another theorem but a *workload* — a real
consumer (interest management, authority migration, streaming chunks, sleeping regions, distributed
latency) that repeatedly cannot be expressed without duplicating or weakening an invariant. Until then the
standing discipline holds: every consumer that composes cleanly on the existing laws is one more datum
against C8. `the milestone is closed by three placements agreeing to the last bit; the glyph is refused by
the same evidence that froze the contract`.

**Observability (Phase 2) — field-level desync localization — MEASURED (reference); observational-only.**
`lockstep.first_desync` names the first mismatching TICK from two witness (digest) chains;
`tools/netcode/observe.py`'s `first_field_desync` goes one level finer — given the two per-tick STATE
chains, it names the exact **body and field** at which they first disagree, scanned in `URDRLST1`
serialization order (`pos.x, pos.y, vel.x, vel.y` per body). Because that order IS the witness byte
order, the field it returns is byte-for-byte the cause of the first digest divergence, so the two
diagnostics agree on the tick by construction and this one adds the field. To feed it, `worldregion`
gained `region_simulate_trace` — the **additive, digest-preserving** surface (mirrors
`worldstep.simulate_trace`): identical frames to `region_simulate` (gated — the seam2 golden
`6d6f6ee3…` is unchanged) plus the reunified `(pos, vel)` state per tick for display-only consumers;
nothing feeds back. **The honest diagnostic (the load-bearing correction to a gamedev assumption):**
the authority tick is exact integer arithmetic and deterministic, so there is NO float accumulation in
the witnessed state and two chains cannot "drift." A field divergence is therefore a *proof* that
exactly one of two things happened upstream — a differing admitted input, or a non-conforming
placement — and *never* rounding; `describe()` says so instead of guessing a source line. **Red-first:**
`tests/test_field_desync.py` (6 falsifiers). **What the gate pins** (dedicated stage `netcode_field_desync`,
4 rows): `field-desync:seam2` — the D16 dropped-ghost divergence localizes to **(tick 11, body 0, vel.x)**
and that tick equals `first_desync`; `field-desync-identity` — identical chains → `None` (no false
positive); `field-desync-general` — a plain worldstep dropped-input divergence localizes too (tick 3),
proving it is not seam2-specific; `field-desync-selftest` — a position-only scan slips to tick 12 while
the full scan catches tick 11 (the velocity scan is load-bearing; gate can redden). Also proved:
`region_simulate_trace`'s reunified states equal the monolith's — composition holds at *field*
granularity, not only the digest. Unit falsifiers 384 → 390. **Grade:** MEASURED reference; pure
consumer (reads recorded state, writes nothing — D15 observational-only); the editor view that consumes
it is layer-3 follow-on. `the debugger names the field, and the exact substrate makes the name a proof
of where to look — an input or a placement, never a rounded number`.

**urdr-criticality — a deterministic branching-diffusion (reactor-kinetics) field — MEASURED
(reference); bounded regime; cross-placement DECLARED; not frozen.** The reactor-physics reading of
*"keff = 2.0 × Galton board + Doppler"*, built on the frozen `field.FixedPoint` in the urdr-field family.
Three coupled operators (`tools/physics/criticality.py`): **transport** — the Galton board's binomial
left/right peg step IS a discrete diffusion kernel, implemented in EXACT-CONSERVATIVE FLUX FORM (per
edge `f = ¼(n_i − n_{i+1})`, `n_i −= f; n_{i+1} += f`), so total population is conserved bit-for-bit
regardless of rounding (vacuum boundaries leak — leakage is part of criticality); **multiplication** —
each generation × keff, where `keff > 1` is SUPERCRITICAL and, under the bounded substrate, RAISES
`FIELD-REFUSE` at the i64 ceiling rather than wrapping; **Doppler** — the reactor negative-temperature
feedback `k_eff = k0·n_ref/(n_ref + n)`, driving `k_eff → 1` as density rises, so a supercritical `k0`
self-limits to a bounded steady state `n* = (k0−1)·n_ref`. **The physical punchline (and why the three
pieces are one experiment):** `keff = 2.0` alone explodes and honestly refuses at the bound; the Doppler
module is *exactly* the feedback that tames it into a stable, witnessed critical state — reactor
stability, deterministic and reproducible. **Red-first:** `tests/test_criticality.py` (9 falsifiers).
**What the gate pins** (`criticality` stage, 5 rows): `criticality:galton` — a point source under pure
transport reproduces the pinned binomial-spread trace `064f7cfc…` (`conformance_criticality.txt`),
deterministically twice; `criticality:doppler` — supercritical `k0 = 2.0` WITH Doppler reproduces the
regulated-steady-state trace `8439d5a6…` and the tail totals are constant (converged); `criticality-conserve`
— flux-form transport conserves total population EXACTLY over 50 generations of a non-round IC (reflecting);
`criticality-eigenvalue` — `keff = 1` stationary, `keff < 1` decays, `keff = 2` with no regulator
`FIELD-REFUSE`s at the bound; `criticality-selftest` (non-vacuity) — the same supercritical start stays
bounded WITH Doppler and explodes to `FIELD-REFUSE` WITHOUT it, so the regulator is load-bearing. Unit
falsifiers 390 → 399. **Grade:** MEASURED reference, **bounded regime B** (rounds honestly, refuses on
overflow, never wraps), deterministic; **cross-placement DECLARED** (a Rust/C99 placement, as for the
other field modules, is the follow-on); **not frozen**. Honest scope: 1D, one-group, and a RATIONAL
Doppler law — the physical Doppler defect ∝ √T is irrational and would itself live in the refuse regime
(DECLARED, not modelled). `the Galton board is the diffusion kernel, keff is the multiplication, Doppler
is the stability; keff=2.0 either refuses or is regulated — and either way it replays to the last bit`.

**D17 structural lint — the invariant-detector admission law made executable — MEASURED.** D17 (the
meta-contract) is now enforced, not just documented: `verify.py`'s `invariant_detectors` stage carries an
explicit **manifest** in which each admitted detector *declares* which recorded rows fill its four roles
(reference / invariance / defect / refusal), and the lint checks — **mechanically, never by inferring from
row-name conventions** (which drift) — that every role is declared, every named row was actually recorded,
and every such row PASSED. Per the human's design: the roles are declared data, resilient to naming
changes; the lint verifies (1) every referenced row exists, (2) every role is present, (3) no detector is
missing one of the four. Building it surfaced and fixed a real gap — **rigidity had no gated refusal**, so
a `rigidity-verdict-refusal` row was added (an overflow framework returns `REFUSE`, the bounded-regime
domain boundary), making rigidity fully D17-compliant. Rows: `invariant-detectors:{D14,D15,D16,rigidity,
criticality}` (each = all four roles present + recorded + passing), a non-vacuity `-selftest` (the checker
rejects a missing role, a dangling row name, and a failed row — so the lint can redden), and the aggregate
`invariant-detectors`. Gate 399 (unchanged — a stage lint, not a unit falsifier), deterministic ×2. **Grade:**
MEASURED. This is rung 2 of D17's ladder — the meta-rule is now executable *before* the next detector
(the toric code) relies on it, so every future detector inherits the admission discipline by construction.
`the admission law stopped being a table and became a gate row that reddens if a detector is authored
without its counterexample or its refusal`.

**Toric code — the first NEW detector admitted under D17; D17 held UNCHANGED — MEASURED (reference).**
The test of whether D17 is a genuine abstraction or a post-hoc description: admit a detector from a
domain the project had never touched, under the *same* six conditions. `tools/intla/toric.py` (with a
new exact substrate `tools/intla/gf2.py` — 𝔽₂ linear algebra by mod-2 elimination, the cleanest exact
arithmetic in the repo: bits, no overflow, no bound) computes the **𝔽₂ homology** of a cellulated
surface: a closed surface is a chain complex `C₂ →∂₂ C₁ →∂₁ C₀` over 𝔽₂ with `∂₁∂₂ = 0`, and Kitaev's
toric/surface code on it has `n = |E|` physical qubits and `k = dim H₁ = |E| − rank ∂₁ − rank ∂₂`
logical qubits (`= 2·genus`). **The invariant is `k`** — a topological invariant: it depends only on the
genus, not the cellulation. This pressured D17 in three fresh directions at once — an ALGEBRAIC (not
geometric) invariant, a NEW exact substrate (𝔽₂, not ℤ / Q32.32), and a MULTI-PART topological witness
(boundary matrices → ranks → `dim H₁`) — and **D17 admitted it with no flex**: the `invariant_detectors`
lint demanded its four roles and it supplied them; the manifest now enforces **6 detectors**. **Red-first:**
`tests/test_toric.py` (7 falsifiers). **Gate stage `toric` (4 D17 roles):** `toric:torus3` — the 3×3 torus
is `k=2` (two logical qubits) with the pinned boundary witness `391e49e5…` (`conformance_toric.txt`);
`toric-genus` (invariance) — `k` tracks genus not the mesh: torus 2×2/3×3/4×4 all `k=2`, the sphere
(octahedron) `k=0`; `toric-selftest` (non-invariance) — a wrong homology that forgets to subtract
`rank ∂₂` reports `dim ker ∂₁ = 10 ≠ 2` (misclassifies); `toric-refusal` — a non-chain-complex
(`∂₁∂₂ ≠ 0`) is `TORIC-REFUSE`d. Unit falsifiers 399 → 406. **Grade:** MEASURED (reference); cross-placement
DECLARED; the invariant is exact over 𝔽₂. **Honest scope:** `k` (code dimension) is always exact and cheap;
the code DISTANCE is exact only for the toric family (`L×L → L`) and `TORIC-REFUSE`s otherwise, because the
general minimum-distance problem is NP-hard — a clean D17 domain boundary, not an approximation. `a domain
the engine had never seen — quantum error correction — entered under the same admission law as rigidity and
a highway, which is the strongest evidence yet that the law is real`.

**Persistent homology (persim) — a D17 detector — MEASURED (reference).** `tools/intla/persim.py`
computes the persistence barcode of a filtered simplicial complex over 𝔽₂ by the standard
boundary-matrix reduction, reusing the 𝔽₂ substrate (`gf2`). The invariant is the barcode. Gate stage
`persim`, four D17 roles: reference — the circle (4 vertices at t=0, 4 edges at t=1) reproduces the
pinned barcode digest `bb17a756…` (`conformance_persim.txt`) with Betti `b0=1, b1=1`; invariance —
reordering simplices within one filtration value gives the same barcode, and the disk (a filled
triangle, whose H₁ loop is killed at t=2) is distinguished from the circle; defect — the un-reduced
pairing (colliding lows left unresolved) misclassifies the barcode; refusal — a non-monotone filtration
is `PH-REFUSE`d. Red-first `tests/test_persim.py` (6 falsifiers). The `invariant_detectors` lint now
enforces **7 detectors**. Unit falsifiers 406 → 412. Grade: MEASURED (reference); cross-placement
declared; exact over 𝔽₂. Scope: the equivalence checked is exact barcode equality — metric stability
(bottleneck distance) is a separate theorem, not claimed here; the detector certifies a given complex's
barcode and is not wired into any tick loop.

**Winding number (winding) — a D17 detector; the W1 rung of D19 — MEASURED (reference).**
`tools/intla/winding.py` computes the winding number of a closed integer polyline about an
off-curve probe by the exact signed crossing count (half-open rule, orientation determinants —
the classical algorithm; nothing here is novel except the gate). The invariant is `w ∈ ℤ`; the
witness is the crossing list, which recounts to `w` and re-derives independently
(`check_witness`). Gate stage `winding`, four D17 roles: reference — both Loewner scenes
reproduce pinned `(w, digest)` ×2 (`loewner_wave` w=+1; `loewner_second` w=+2 — the golden
separates 1 from 2, not merely sign), plus three sign controls (ccw +1 / cw −1 / figure-eight
lobe −1, exterior probe 0); invariance — cyclic rotation + integer collinear subdivision
preserve `w`, orientation reversal NEGATES it (the documented covariance); defect — the
unsigned parity count misreads every negatively-wound curve; refusal — 4/4 `WIND-REFUSE` typed
and total (short / degenerate / non-integer incl. bool / probe-on-trace). Plus the
theorem-backed corpus property: all 17 pinned probes on both Loewner scenes wind
non-negatively — Loewner (Annals of Mathematics 1948; revived by Albers–Tabachnikov,
arXiv:2109.03051, Math. Intelligencer 2021: curves `(P(d/dt)f, Q(d/dt)f)` with monic
interlacing P, Q wind non-negatively about every off-curve point); the corpus pins integer
samples of `(f′, f)` and `(f″−f, f′)`, authored OFFLINE and audited (independent float
angle-sum + 10× dense resample, all probes agreeing) before pinning — the pinned integers are
the object, the formula is provenance. Red-first `tests/test_winding.py` (12 falsifiers). The
`invariant_detectors` lint now enforces **8 detectors**. Unit falsifiers 537 → 549. Grade:
MEASURED (reference); cross-placement not claimed. `does_not_show`: the smooth theorem (the
corpus is corpus-scoped — a coarse sampling can break the discrete↔smooth correspondence,
which is why samples are pinned rather than derived at gate time); metric robustness; any D19
pipeline behavior — the abductive contract itself remains SPECULATIVE, with no proposer, no
recorded batch, and no `ABDUCT-REFUSE` anywhere in the tree.

**W1 Slice-3 expansion + cross-placement — Axis A: REFERENCE → CROSS-PLACED (Linux).** The
first higher-degree interlacing family (P = x³ − x, Q = x² − ¼, strictly interlaced monic;
f = 6·sin t + 2·cos 2t + sin 3t, N = 48, S = 1000) pins a doubly-wound core —
`loewner_cubic` w = +2, golden `2176649b…` — and adversarial near-curve probes
(vertex + (13, 7), ≈15 units off the trace, each admitted at authoring by exact off-trace
check + dual-method + 10× dense agreement) join all three grids: 35 pinned probes, all
w ≥ 0, with the five pre-existing goldens byte-identical (the frozen-surface check ran at
regeneration). `tools/intla/winding_rs/winding.rs` (std-only Rust, own SHA-256 verbatim
from worldstep_rs, checked i64 with typed overflow refusal — the placement's bounded
domain is the documented difference from the reference's bigint Dom) reproduces GOLDEN
AND DEFECT: all six `(w, digest)` pairs bit-for-bit, 35/35 grid probes non-negative, and
the parity defect's wrong answer on the clockwise square; ADMITTED ×2 with bit-identical
output on a Linux sandbox host (rustc 1.95). Placement count rises to 23 Rust / 13 C99.
Windows/rustc owner attestation pending → the Windows column stays DECLARED. Unit
falsifiers 549 → 550. `does_not_show`: unchanged from the W1 entry above.

**Tellegen orthogonality (tellegen) — a D17 detector; D19's second constraint instrument —
MEASURED (reference).** `tools/intla/tellegen.py` pairs an integer potential against a
conservative integer flow on a shared directed multigraph: `S = Σ vₖ·iₖ` with
`vₖ = p[head] − p[tail]`; Tellegen (Philips Research Reports, 1952) forces `S = 0` on all of
Dom — ANY admissible pair, independent of constitutive laws (the one-line reason: the sum
regroups to `Σₙ p[n]·(inflow − outflow)`, zero exactly when KCL holds). Gate stage
`tellegen`, four D17 roles: reference — `bridge6`/`bridge6_alt`/`cycle5`/`parallel_loop` pin
`(S = 0, digest)` ×2 with recounting per-edge product witnesses (parallel edges and
self-loops admitted and documented: a self-loop has `v = 0`); invariance — gauge shift,
simultaneous (edges, flow) permutation, reorientation-with-negation; defect — the
orientation-blind (min-first) pairing is nonzero on all four pinned scenes; refusal —
`TELL-REFUSE` total, a leaky flow refused NAMING its first violating node and exact net
imbalance. Plus the theorem-backed property row: the 3×3 any-potential ×
any-conservative-flow grid on the bridge topology pairs to zero 9/9 — corpus-scoped; the
1952 theorem is provenance, not a gate claim. Red-first `tests/test_tellegen.py`
(11 falsifiers). The `invariant_detectors` lint now enforces **9 detectors**. Unit
falsifiers 551 → 562. Grade: MEASURED (reference); cross-placement not claimed.
`does_not_show`: constitutive behavior (no component laws exist here); flow FEASIBILITY
under fixed boundary conditions (the Hoffman-cut candidate is a session note, not code);
any "map the codebase's pipelines to circuits" consumer story — DECLARED at best; and the
D19 pipeline itself, unchanged and SPECULATIVE (no proposer, no recorded batch, no
`ABDUCT-REFUSE`).

**Terrain heightfield canon (URDRHF1) — T1 of the terrain ladder; the D14 procedural
modality — MEASURED (canon-level reference).** `tools/terrain/heightfield.py`: SHA-seeded
lattice noise (`sha256(MAGIC|seed|layer|xi|yi)` — stateless, host-independent), Q16 quintic
interpolation with floor rounding (the D9 discipline: deterministic, rounds, stated), an
exact FBM rescale to `[0, height_scale]`, and a sqrt-free island falloff linear in d² —
same (seed, params) → the SAME heightmap bytes on every host, the promise float-based
studios cannot make. Gate stage `terrain`: three preset goldens ×2 (the island pins the
operator's zyfod session parameters — seed 2920741843, 420/72, width 90/256 — as
provenance, never identity), validity rows (heights bounded; island corners exactly zero;
the mask never raises a height; sea level moves the CANON, never the FIELD — presentation
can never alter terrain identity), the linear-fade defect diverging from all three goldens
while staying bounded, and `TERRAIN-REFUSE` total — refuse, never clamp (dims 4..512,
layers 1..12, Q8 falloff width). Red-first `tests/test_terrain.py` (11 falsifiers,
including byte-level lattice pins). Unit falsifiers 562 → 573. Deliberately NOT a D17
detector — a generator authors, it does not detect — so no `invariant_detectors` manifest
entry. Grade: MEASURED (reference) for the URDRHF1 canon only. `does_not_show`: the
URDROBJ2 admission (rung T2 — D14 §3 steps 3–5 remain the obligation); anything rendered
(T3, under the idle law: an idle view draws zero frames); erosion / splines / tiles (T4
names); cross-placement. Plan of record: `docs/terrain_studio_brief.md`.

**Terrain → URDROBJ2 bridge (T2) — the D14 admission completed — MEASURED (reference).**
`tools/terrain/terrain_bridge.py`: a URDRHF1 heightfield becomes an integer wireframe grid
under the ONE identity law every front end shares — height on z, x/y scaled exactly,
decimation EXACT (the stride must divide dim−1 so the border is included, or
`TERRAIN-REFUSE`; never a silently dropped edge). D14 clause 2 discharged the strong way:
`own_canon` re-implements the URDROBJ2 string law without importing the referee, and the
gate checks OWN ≡ `canon_ref.canon` on every pinned grid (island 8×8 / 64 verts / 112
edges, golden `3caa092a…`; blank 4×4, golden `77910ea7…`) plus `check_design` → ADMIT.
Clause 5 checked, not assumed: differing provenance dicts yield one identity, and the
max-first edge-normalization defect diverges (gate can redden). Gate rows
`terrain:object` / `terrain-object-provenance` / `terrain-object-selftest`; refusal row now
6/6. Red-first additions in `tests/test_terrain.py` (16 falsifiers total). Unit falsifiers
573 → 578. Grade: MEASURED (reference) — the D14 §4 procedural row is now MEASURED on both
halves; cross-placement (§3 step 6) escalates with importance. `does_not_show`: anything
rendered or world-loaded (the editor consumes URDROBJ2 objects by the existing measured
machinery, but no terrain object has been walked through the editor yet — T3); water,
biomes, tiles (T3/T4); the smooth-terrain aesthetics of any decimation choice.

**The terrain sea (S1) — certified field state over a coastline domain — MEASURED
(reference).** `tools/terrain/sea.py`: the bathymetry adapter (URDRHF1 heights + the
declared sea level → sea mask + exact depth field; empty seas `TERRAIN-REFUSE`) and the
masked flux-form step — the frozen `field.py` law with ONE addition: an edge carries flux
only if both endpoints are sea, so the coastline is boundary exactly as the grid edge
already is. `urdr-field 0.1` is untouched (imported, not edited) and the evolved state
digests under the frozen `URDRFLD1` law — NO new witness class (a C8 datum). Gate stage
`sea`: the pinned island sea (drop at the deepest sea cell (0,0) — a documented selection
rule — 40 masked diffusion ticks at k=1/8) reproduces its digest ×2; total mass EXACT
across the evolution and the field genuinely moves; land identically zero at init and
after; an all-sea mask reproduces the frozen step BIT-FOR-BIT, advection included (the
masked law is the frozen law plus a boundary, nothing more); the UNMASKED evolution wets
2449 land cells and diverges (the mask is load-bearing); refusals split and typed —
adapter/scene `TERRAIN-REFUSE`, structural/overflow `FIELD-REFUSE`. Red-first
`tests/test_sea.py` (8 falsifiers). Unit falsifiers 578 → 586. Honest bathymetry note:
the island's declared sea level yields a coastal-ring sea (4% of cells) — the scene
certifies the law, not ocean aesthetics. Grade: MEASURED (reference). `does_not_show`:
Marangoni surface tension and body coupling on this domain (S2); anything rendered (T3,
idle law); waves, tides, erosion (names); cross-placement.

**The Marangoni sea (S2) — surface tension on the coastline domain — MEASURED
(reference).** `sea.py` gains `step_marangoni_masked` (the house `marangoni_step` law —
diffusion `k·Δc` plus the nonlinear up-gradient flux `κ·Δc·c_upwind`, flux-form, mass
exact — gated on both-endpoints-sea) and the adapter gains `scene_sea_level`: a SCENE may
pin its own water line as authority-side scene structure while the terrain field and its
canon stay untouched (checked by the T1 law, not assumed). The pinned wide-sea scene:
scene level 130 by the documented rule (first of 100..140 giving 30–60% sea → 37%), depth
scaled 1/64, drop at the deepest cell, 30 Marangoni+diffusion ticks. HONESTY NOTE, paid
for in the authoring audit: the naive CFL estimate UNDERESTIMATES — Marangoni
self-amplifies (the sharpening peak grows its own gradients) and κ = 1/4 went negative
mid-run; the pinned κ = 1/16 was verified monotone TICK-BY-TICK across all 30 ticks, and
the gate re-verifies that audit on every run (the audit, not the estimate, is the law).
Gate rows: `sea:wide` (Marangoni golden ×2), `sea-marangoni` (mass EXACT + monotone 30/30
+ the peak persists above pure diffusion — the Marangoni content — + land dry),
`sea-marangoni-selftest` (the over-bound κ = 1/1 overshoots negative in 4 ticks yet
conserves mass — the CFL bound is load-bearing). Red-first additions in `tests/test_sea.py`
(12 falsifiers total). Unit falsifiers 586 → 590. Grade: MEASURED (reference).
`does_not_show`: field↔body coupling on this domain (still open); waves/tides (names);
full free-surface Navier–Stokes (the house Marangoni honesty boundary, inherited);
anything rendered (T3, idle law); cross-placement.

**The terrain view-export firewall (T3.0) — the measurable half of the presentation layer —
MEASURED (reference).** `tools/terrain/terrain_view.py`: D15's view contract applied to a
certified terrain/sea state, minting NO new authority class (the `view_digest` is a
presentation digest). A view descriptor carries the recorded `island_sea_wide` witness as a
bound, subordinate field and a `view_digest` over the witness + declared presentation knobs.
Gate stage `terrain_view`: bind (the view carries the authority digest verbatim),
observational (all 6 declared knobs move the view digest and NONE moves the witness; knob
order inert — presentation is observational only), selftest (the fold-into-witness defect
diverges — the firewall is load-bearing), refusal (non-hex witness / malformed presentation
`VIEW-REFUSE`). Red-first `tests/test_terrain_view.py` (6 falsifiers). Unit falsifiers
590 → 596. The elegant inversion (see `docs/presentation_doctrine.md` §4): we do not measure
the pixels and we do not measure the budget — we measure that the budget cannot touch the
truth. Grade: MEASURED (reference) for the FIREWALL only. `does_not_show`: anything the
`terrain_view.html` renderer draws (presentation — declared, off-gate, browser float, NOT
measured, and unmeasurable in principle); the budget laws D20–D23 (declared weighting models,
never in this ledger as physics); the visual gap (T3.1–T3.4). The boundary never moves:
`semel` the authority is measured, `et iterum` the presentation is declared, `idem` the
boundary is fixed.

**The wave-seam authority (T3.3) — an EXACT integer traveling-wave field — MEASURED
(reference).** `tools/terrain/wavefield.py`: the measurable core of the OODA-picked wave seam
(`docs/POSITIONING.md` §6). A stronger choice than the roadmap's first sketch: a true Gerstner
surface needs `sin`/`cos` (irrational → the bounded Q32.32 regime + a fixed-point-trig
sub-slice), so instead the field is built from a **periodic parabolic profile in pure
integers** — `profile(p) = A − (8A/P²)·(p mod P)·(P − p mod P)` with `P² | 8A` — making it
EXACT (no rounding), trig-free, DIVISION-FREE (no `/`, `//`, or `%` operator anywhere — the
phase wrap and the exact curvature `8A/P²` use shift-based DOUBLING, so cross-placement parity
is STRUCTURAL, not a documented caveat about negative-operand `/`/`%` divergence; a
rounding Q16-reciprocal `>>16` is deliberately NOT used, as it could not claim EXACT), and
trivially cross-placeable, the stronger grade in the
`exact where affordable` spirit. It is NOT a sinusoid; the sinusoidal *look* is the GPU's
declared job (two grades, never conflated). Height superposes the components' profiles; phase
uses documented FLOOR MOD so a truncating-`%` placement agrees; same (components, tick) → same
bytes on every host. Gate stage `wavefield`: reference (swell + still reproduce URDRWAV1
digests ×2 at every pinned tick), properties (every cell within the exact amplitude bound
Σ|A|; a moving field travels while a zero-speed field is static across ticks; superposition is
EXACT — `field(Σcomp) == Σ field(comp)`, the no-rounding flex that a bounded sinusoid could not
claim), selftest (the reversed-travel defect matches t=0 and diverges at t≥1 — travel is
load-bearing), refusal (non-exact `(A,P)` / odd or sub-2 period / zero direction / negative
speed / bool / bad dims → `WAVE-REFUSE`, refuse never round). Red-first `tests/test_wavefield.py`
(9 falsifiers — one TOKENIZES the source and asserts no division/modulo operator exists, so
the placement guarantee is enforced structurally). Unit falsifiers 596 → 605. Grade: MEASURED
(reference) — EXACT (not bounded), and division-free.
`does_not_show`: the presentation half (the WebGL2 3D Gerstner-shaded view, T3.2/T3.3 — now
BUILT: `terrain_view3d.html`, declared, off-gate, its citation certified by T3.6 view-witness);
a gameplay consumer of the field (buoyancy/wave-crossing — now BUILT: T3.5 URDRBUOY1 + T3.7
URDRCROSS1); ocean realism (the parabolic profile is deterministic authority, not a physical
spectrum); cross-placement (a clean next step — exact integers, the winding_rs recipe).

**Wave-field buoyancy (URDRBUOY1) — T3.5, the first MEASURED consumer of the wave seam.**
`tools/terrain/buoyancy.py`: the consumer half the wavefield entry named and did not build. A
rigid raft floats on the exact traveling field; each tick it settles to the integer waterline
`z*` where displaced depth balances weight (a discrete Archimedes) — `Δ(z) = Σ max(0, h(x,y,t) −
z)`, `z*` the largest `z` with `Δ(z) ≥ weight`, so `Δ(z*) ≥ weight > Δ(z*+1)`. `Δ` is
non-increasing, so `z*` is found by DIVISION-FREE integer bisection (`<<`, `>>`, midpoint `lo +
((hi−lo) >> 1)`), EXACT and cross-placeable (no `/`, `//`, `%` — tokenizer-asserted). The digest
binds `z*` AND the wetted per-cell profile. Gate stage `buoyancy`: reference (`raft_swell` +
`raft_still` reproduce URDRBUOY1 digests ×2 at every pinned tick), properties (the exact
Archimedes bracket holds; `Δ` is monotone; the raft heaves on the swell and rests dead-flat on
the zero-speed still), selftest (the UNCLAMPED-displacement defect — a hull that sucks itself
down where it should be dry — diverges; the `max(0,·)` clamp is load-bearing), refusal
(empty/out-of-grid/duplicate footprint, weight ≤ 0 or heavier than the raft can displace, bool →
`BUOY-REFUSE`). Red-first `tests/test_buoyancy.py` (10 falsifiers incl. the no-division tokenizer
assertion). Unit falsifiers 605 → 615. Grade: the COMPUTATION is MEASURED (exact, reproducible,
a defect diverges); the flotation LAW is a DECLARED model (a discrete Archimedes, not real
hydrostatics) — the field it reads is authority, the law is a model, the reproducible `z*` is
measured, exactly as the D20–D23 budgets are declared models walled from this ledger.
`does_not_show`: real hydrostatics (the buoyancy law is a declared model); more than one pinned
raft geometry; cross-placement (a clean next step — exact integers, the winding_rs recipe).

**View-witness citation contract (T3.6) — the declared view must honestly CITE the measured
authority — MEASURED (the citation, never the render).** `tools/terrain/view_witness.py`: the
DECLARED WebGL2 studio view (`terrain_view3d.html`, 15 knobs, off the exact gate) embeds two
authority digests it claims to display (`hf_witness` = URDRHF1 island, `wave_witness` = URDRWAV1
swell@0). We do NOT measure its pixels — that boundary never moves. But nothing stopped a
careless or dishonest edit from printing a FORGED digest there and staying green. This stage
certifies the CITATION: the embedded digests must equal the LIVE digests recomputed from the
modules (`heightfield.py`, `wavefield.py`); and the FIREWALL: the declared knob ids are a
namespace disjoint from the authority fields, and the presentation `view_digest` is anchored on
the authority witness — so a knob moves the view, never the witness. The dual of
`terrain-view-observational` / D15: the view cannot contaminate the authority, and now cannot
MISQUOTE it. Gate stage `view-witness`: cite (`terrain_view3d.html` cites the live island +
swell@0 digests ×2), firewall (knobs disjoint; view anchored on the witness), selftest (a
one-hex-flip forgery of a cited witness fails the citation check — load-bearing), refusal (no
authority blob / non-hex or wrong-length witness / missing citation → `VIEW-REFUSE`). Red-first
`tests/test_view_witness.py` (9 falsifiers). Unit falsifiers 615 → 624. `VIEWS` is a list, so
every future fidelity overlay inherits the guarantee (versioned overlays). Grade: MEASURED — the
CITATION is an exact digest equality (a forgery reddens it); NO claim is made that the render is
measured (it stays declared).
`does_not_show`: the render (pixels are declared, never measured); a dynamic knob sweep (the
firewall is a structural namespace + anchor proof, not a runtime sweep); views beyond
`terrain_view3d.html` (the contract is a list, currently one entry).

**Wave-crossing timing (URDRCROSS1) — T3.7, the second MEASURED consumer.**
`tools/terrain/crossing.py`: where buoyancy reads a FIXED cell over time, this reads a MOVING
trajectory through the traveling field — the other consumer the wavefield entry named. A
straight-line constant-velocity agent crosses; at tick `t` it is at `(x0+vx·t, y0+vy·t)` and the
exact height there at THAT tick is `h`; riding at a fixed `clearance`, `result` is the first `t`
with `h > clearance`, else `T` (cleared). Because both the agent AND the wave move, the event is
a joint space-time reading — freeze the wave (every tick at `t=0`) and the first-overtopping tick
moves, so wave TRAVEL (not just profile) is load-bearing. Exact integers (multiply/compare + the
division-free wavefield), so `result` reproduces bit-for-bit and cross-placement is a clean next
step (no `/`, `//`, `%` — tokenizer-asserted). The digest binds `result` AND the per-tick height
trace. Gate stage `crossing`: reference (`ferry_clear` + `ferry_swamped` + `swimmer_north`
reproduce URDRCROSS1 digests ×2), properties (the trace is `wavefield.height` at the moving cell
AND moving tick; `result` is the FIRST overtop; clearance is load-bearing — `ferry_clear` and
`ferry_swamped` share ONE path and only the clearance differs, so one clears and one is swamped),
selftest (the frozen-wave defect diverges — travel is load-bearing), refusal (zero velocity /
path leaves the grid / non-positive window / bool / non-integer → `CROSS-REFUSE`). Red-first
`tests/test_crossing.py` (10 falsifiers incl. the no-division tokenizer assertion). Unit
falsifiers 624 → 634. Grade: the COMPUTATION is MEASURED; the crossing LAW (a crest above
clearance overtops a straight-line constant-velocity agent) is a DECLARED model, like the
buoyancy law.
`does_not_show`: fluid dynamics (the crossing law is a declared model); curved or accelerating
paths (straight-line constant-velocity only); more than three pinned scenes; cross-placement (a
clean next step — the winding_rs recipe).

**Terrain heightfield canon cross-placed (URDRHF1) — REFERENCE → CROSS-PLACED.**
`tools/terrain/heightfield_rs/heightfield.rs` is an independent std-only Rust build (own
hand-rolled SHA-256 verbatim from `worldstep_rs`, own seeded lattice noise, own Q16 quintic FBM,
own sqrt-free island falloff — no shared code with `heightfield.py`) that reproduces the three
pinned URDRHF1 scene digests — `island 7243652e…`, `blank 7cc67f67…`, `mountains c57c56be…` —
bit-for-bit, verified in-session on `rustc 1.95.0`. The hazard the port had to EARN: the
value-noise interpolation `(v10 − v00)·u // FRAC` has a NEGATIVE numerator on ~half the lattice
edges, where Python `//` floors and Rust `/` truncates toward zero — a `floordiv` restores the
floor so the placements agree (the exact negative-operand divergence the division-free
discipline avoids by construction elsewhere, met head-on and matched here). The 24th std-only
Rust placement; `doc-currency` Rust 23 → 24. Trust from independent reproduction (D17 Axis A) —
the winding_rs recipe applied to the terrain canon. The URDROBJ2 bridge (`island_obj` /
`blank_obj`) is a separate canon, a clean next cross-placement.

**Reconstructibility — the 10th D17 detector (information-security).** The exact-reconstruction
machinery (`tools/intla/atlas_reconstruct.py`) is admitted as a certified invariant-detector under
the UNCHANGED D17 admission law (Dom, Inv, W, ~, R): Domain = an observation atlas (charts of
integer rows) + an observation `y`; Invariant = UNIQUE RECONSTRUCTIBILITY — the hidden state is
recoverable exactly iff the stacked M is injective (full column rank); Witness = the reduced
rational `(num, den)` with `M·num == den·y`, independently checkable; ~ = reordering the
observations (permuting the rows of M and y TOGETHER — order is not content); R = typed refusal
(`NOT_INJECTIVE` when the state is not unique, `INCONSISTENT` when `y` leaves the column space).
The information-security reading: a system whose state is NOT reconstructible from its public
observations HIDES a private component (the firewall holds); one that IS reconstructible LEAKS it.
The four roles map to gate rows recorded by `atlas_reconstruct`: reference = `reconstruct-roundtrip`
(integer states recover exactly; a half-integer state recovers as the exact reduced rational —
reconstruction, not rounding), invariance = `reconstruct-invariance` (NEW: reorder preserves the
recovered state AND the injectivity verdict; a MISPAIRED reorder breaks it — non-vacuity), defect =
`reconstruct-forgery-selftest` (an observation bumped off the column space is refused INCONSISTENT
while the genuine one is accepted), refusal = `reconstruct-deficient` (a deficient atlas refuses
NOT_INJECTIVE). Red-first `tests/test_atlas_reconstruct.py` gains the reorder-invariance pair (+2
falsifiers). doc-currency 634 → 636 unit falsifiers / 428 → 430 rows; D17 now 9 → 10 detectors,
each declaring 4 roles, every role recorded + passing. Grade: MEASURED — the detector admits the
existing machinery under the D17 lint; no new witness class, no field mutated. The ambitious pivot
the architecture promised: information-security enters the detector library under the same
admission law as rigidity, toric, winding, and tellegen.

**Toric detector cross-placed — Axis A: REFERENCE → CROSS-PLACED.** `tools/intla/toric_c/toric.c` is an
independent C99 build (own SHA-256, own GF(2) rank, own complex construction) that reproduces the `torus3`
boundary digest `391e49e5…` and `k = dim H₁` (torus 2/3/4 → 2, sphere → 0) bit-for-bit; compiled and
self-verified in-session (`cc -O2 -std=c99`, gcc 11.4). `tools/intla/toric_rs/toric.rs` is the Rust mirror
(SHA-256 reused verbatim from `worldstep_rs`) for admission on the Windows/rustc host. So the toric
detector is now **CROSS-PLACED** on D17's reproduction axis (Axis B / separation unchanged: COMPLETE for
surface homeomorphism). This is Phase IV item 2 — trust from independent reproduction, before the atlas.

**Rigidity detector cross-placed end-to-end — Phase IV item 3.** Rigidity's rank engine (`urdr_math`)
was already cross-placed, but the detector's own matrix assembly + verdict was not independently built.
`tools/intla/rigidity_c/rigidity.c` is a dedicated C99 placement — its own i128 Bareiss rank and its own
rigidity-matrix construction — that reproduces all four pinned certificates (triangle RIGID 3/0, square
FLEXIBLE 4/1, square_diag RIGID 5/0, square_2diag RIGID 5/0) and the 1e9-coordinate `REFUSE` bit-for-bit;
compiled and self-verified in-session (`cc -O2 -std=c99`, gcc 11.4). `tools/intla/rigidity_rs/rigidity.rs`
is the Rust mirror for the Windows/rustc host. So rigidity's CROSS-PLACED grade (D17 Axis A) is now earned
end-to-end, not only through the shared rank engine. **Port note (the trap avoided):** the reference's
bound law checks each Bareiss *product* against the i64 ceiling (`_mul = _fit(a*b)`), and two i64 operands
give a product up to ~2^126 — so the placements compute it in **i128** and then compare to i64. A naive
i64 multiply would *wrap before the check* and silently diverge exactly on the overflow-`REFUSE` case;
i128 (sufficient, since operands ≤ i64) makes the placement refuse identically.

**frontfps — the consolidated FPS/MMO authoring front end (Stages 1–4), graded.** `tools/frontfps/` is one
consolidated module line carrying the authority-side authoring surface of a shooter/MMO: world canon
(`frontfps.py`, URDR-FPSW-1), the Q32.32 rotation substrate (`fpquat.py`, URDRFPQ1), the pose/clip canon
(`fpclip.py`, URDRCLP1), and posed transforms + hitbox capsules (`fppose.py`, URDRPSE1), and the display-only view stream (`frontfps_view.py`, URDR-FPSW-VIEW-2). Each is
**MEASURED (reference)** via its own gate stage (`frontfps`, `frontfps_quat`, `frontfps_clip`,
`frontfps_pose`, `frontfps_view`) with red-first falsifiers; the substrate reuses the frozen FIELDFP laws (ONE = 2³²,
`_rdiv` round-to-nearest ties-away, i64 refusal ceiling) — nothing reinvented. Cross-placement (Axis A):
`fpquat` and `fpclip` are three placements each (Python + C99 self-verified in-session, gcc 11.4 + Rust
owner-attested on Windows/rustc), golden AND defect digest parity. **`fppose` is now cross-placed:**
`fppose_c/fppose.c` self-verified in-session (`cc -O2 -std=c99 -Wall -Wextra` clean) — posed golden
`fee3c118…` ×2, coverage on walk + reach, the swapped-compose defect `04f23abe…` and the local-offset
coverage defect both bite, 77-op budget proxy, refusals total → **MEASURED (C99)**; `fppose_rs/fppose.rs`
**ADMITTED ×2 + `--defect` caught on the owner's Windows host** (rustc -O, 2026-07-13; golden `fee3c118…`,
defect `04f23abe…`) → **MEASURED**. So fppose is three placements, two OSes, golden AND defect parity. The
interior point-in-capsule test multiplies two ~2⁸⁰ integers, so the placements carry a small u256
mul/add/compare (i128 tops out at 2¹²⁷); all operands are non-negative on that branch.

**Stage 5 — the display-only view stream (`frontfps_view.py`, URDR-FPSW-VIEW-2), MEASURED (reference).**
A binary, delta-framed successor of D15's `to_view`: one keyframe then delta frames encoding only the
actors whose quantized transform changed since a named base. Three laws, each a gate row that can redden:
(1) *recompute* — encode is byte-identical twice and decode∘encode reproduces the display sequence with the
bound witness recomputed; (2) *no-feedback* — the bound authority witness is invariant under presentation
(the LOD shift), a fold defect that binds the witness to the quantized display MUST move it, and the decoded
display is a proven **lossy** projection (two distinct authority states collapse to one display, so there is
no inverse back to authority — the firewall is structural, the decoder returns a display frame, never a
Scene); (3) *bandwidth* — bytes per authored scene are host-independent, pinned (`view_stream bc60023…`,
`view_bytes 332`) like the op-count proxies, never fps. A delta referencing a base never sent — or a stream
opening on a delta — is `VIEW-REFUSE`d. Gate stage `frontfps_view` (5 rows) + `tests/test_frontfps_view.py`
(11 falsifiers) → gate **485 unit falsifiers / 356 rows**. Cross-placed: `fpview_c/frontfps_view.c` self-verified in-session (`-Wall -Wextra`, golden `bc60023…` ×2,
332 bytes, decode 4 frames, 3 VIEW-REFUSE, fold-defect `d5ea65e…` parity) → **MEASURED (C99)**;
`fpview_rs/frontfps_view.rs` **ADMITTED ×2 + `--defect` caught on the owner's Windows host** (rustc -O,
2026-07-13) → **MEASURED**. The native layer-3 renderer stays outside the gate by its own law
(frontfps README §6 / roadmap §4).

**Stage 6 — the LLM authoring surface (`frontfps_text.py`, URDR-FPSW-TEXT-1), MEASURED (reference).**
A line-oriented ASCII form of the URDR-FPSW-1 canon — the surface a model emits and edits as plain text —
with the authoring loop as a gate property (emit → `admit_text` → typed refusal reason → re-emit). It is a
surface, not a new identity: a parsed world's digest is exactly the frontfps `world_digest`, provenance
still excluded. Four laws, each a gate row: round-trip (canonical / idempotent / digest-preserving),
identity (parsed == frontfps digest; a `prov` model tag never moves it), **totality** (a seeded adversarial
fuzz corpus of 257 inputs — every one typed-admits or typed-refuses, never a bare exception or a silent
half-admit; outcome digest `e57dfaea…`, 74 admit / 183 refuse), and repair (a refusal names its 1-based
line; dropping it re-admits — the loop closes). `auto_arena` joins the §4 auto family (mirror symmetry
certified; an asymmetric defect violates it). Gate stage `frontfps_text` (7 rows) + `tests/test_frontfps_text.py`
(12 falsifiers) → gate **497 unit falsifiers / 363 rows**. Cross-placement SPECULATIVE. `does_not_show`:
that any particular model emits valid worlds — that is a model property, not a gate property; the gate proves
the surface is total, typed, round-tripping, and repair-signalling.

**Stage 1 world canon cross-placed — the foundation reaches the 2-OS parity bar.** The URDR-FPSW-1 world
canon (`frontfps.py`, the identity law under everything above) previously had no second placement. It now
does: `frontcanon_c/frontcanon.c` is a generic serializer (name-keyed maps sorted, edge lists normalized
min-first then sorted, authored sequences kept in order) that builds the canon from hardcoded world DATA —
not a pre-baked string — and reproduces `world_digest(crate_solo)=6c4c807f…` and
`world_digest(arena_duel)=0c9ec33a…` bit-for-bit ×2, plus the provenance-folding defect
(`6464df51…` / `259094eb…`), self-verified in-session (`cc -O2 -std=c99 -Wall -Wextra`) → **MEASURED (C99)**;
`frontcanon_rs/frontcanon.rs` **ADMITTED ×2 + fold defect caught on the owner's Windows host** (rustc -O,
2026-07-13) → **MEASURED**. This unblocks a
faithful `frontfps_text` cross-placement (its fuzz-outcome digest hashes admitted worlds' `world_digest`,
which now has an independent implementation to agree with).

**Stage 6 cross-placed end-to-end — the LLM authoring surface holds across two languages.** With the world
canon placed, `frontfps_text_c/frontfps_text.c` (an independent parser + checker + canon + emitter + the
seeded fuzz harness) reproduces, bit-for-bit: `text_canon` (`2718c63e…`), round-trip parity on both demo
worlds, the four refusal canaries' TEXT-REFUSE / FPSW-REFUSE classification, AND the **full fuzz-outcome
digest** (`e57dfaea…`) — every one of 257 seeded adversarial inputs classifying identically (74 admit /
85 FPSW / 98 TEXT), self-verified in-session (`cc -O2 -std=c99 -Wall -Wextra`) → **MEASURED (C99)**;
`frontfps_text_rs/frontfps_text.rs` **ADMITTED on the owner's Windows host** (rustc -O, 2026-07-13),
reproducing the full fuzz-outcome digest `e57dfaea…` + defect → **MEASURED**; so the 257-input fuzz
classification now agrees across THREE implementations (Python + C99 + Rust) and two OSes. A porting
lesson worth keeping: the one classification that first diverged was a duplicated `hitbox` line — hitboxes
are a *name-keyed map* (a repeat overwrites), and the C initially appended; the fuzz digest caught it on
input 96 of 257. Every functional stage of the frontfps ladder (1–6) is now cross-placed on the
reproduction axis — C99 self-verified, Rust owner-attested as each run lands.

**Stage 7 opened — work accounting MEASURED, performance NOT_MEASURED by law.** `frontbench.py`
(URDR-FPSW-BENCH-1) composes the measured per-module proxies into the exact frozen-division count for the
canonical 100-biped sim tick — `sim_tick_divisions(100) = 100 × (fpclip 55 + fppose 77) = 13200` — pinned
and cross-checked against real instrumented execution (the model equals the work), with a drop-animation
defect that underestimates the tick. The bench protocol's host-independent bridge (`docs/bench_protocol.md`
§4) is now the composed count, not a single proxy: multiply 13200 by a once-measured cost-per-frozen-division
on the named host and the 3 ms sim budget becomes an audit. **The honesty boundary is a gate row:**
`frontbench-budget` asserts that no ms/fps entry in the budget manifest reads MEASURED without a §3 host log,
and that a manifest claiming one is caught — so no performance number can silently graduate. Grade: work
accounting **MEASURED** (exact, host-independent, gated); all performance (ms / fps / 1080–1440p / BF6)
**NOT_MEASURED** with the named-host precondition. Gate stage `frontbench` (4 rows) +
`tests/test_frontbench.py` (7 falsifiers) → gate **504 / 367**. The wall-clock `--measure` runs on any host
but its output is labelled NOT_MEASURED; only the `bench_protocol.md` §3 run on the ROG Ally X turns the
pinned counts into milliseconds — and that run, not this module, is what would move the perf grades.
First reference reading (2026-07-14, `ROG-Ally-X-Z2-Extreme`, Turbo 17→35 W floating): median
**~715 ns/frozen-division (~9.4 ms/tick)**, wattage-insensitive; p95 ≤11.4 ms; max 16.2 ms sustained —
an informational upper bound (Python reference), **NOT_MEASURED** for the native target
(`bench_protocol.md` §4a). The median's power-insensitivity says the native placement, not more watts,
is the budget lever.

**Native sim-tick placement — the Python upper bound falls ~70× natively (sandbox datum, still
NOT_MEASURED for the target).** `frontbench_c/frontbench.c` runs the canonical tick natively — per biped:
fpclip sample → fppose pose, merging the already-cross-placed Q32.32 substrate + sampler + poser —
self-verified in-session (`cc -O2 -std=c99 -Wall -Wextra`): `sim_tick_digest == fee3c118` (the fppose
posed golden — sample→pose reproduces it) ×2 and `sim_tick_count(100) == 13200` frozen divisions →
**MEASURED (C99, correctness)**; `frontbench_rs/frontbench.rs` mirrors it for the Windows host (owner-run).
Its `--measure` on the Linux sandbox reports ~0.125 ms/tick median (100 bipeds) — ~70× under the Python
reference's ~9.4 ms and well inside the 3 ms budget — but that is a **sandbox datum, NOT the Ally and
NOT_MEASURED for the target**: only the `bench_protocol.md` §3 run on the ROG Ally X
(`frontbench_rs --measure`, cold + soak) turns it into a native millisecond that could move the sim-tick
grade. Correctness is cross-placed; performance still waits on the named host. **First native Ally reading**
(2026-07-14, cold, `frontbench_rs --measure`, Turbo-35W): sim tick **~0.072 ms median** (100 bipeds,
p95 0.076 / max 0.111) — ~41× under the 3 ms budget, ~130× under the Python reference on the same
hardware. Cold + soak both recorded (median 0.0723 / 0.0730 ms — cold ≈ sustained; the tail widens to max 0.34 ms
sustained, still ~9× under budget), so the **sim-tick budget row is now MEASURED (named host)** — this
project's first performance grade, carrying `bench_protocol.md` §4b as its host log. The
`frontbench-budget` gate row evolved with it: from *no perf MEASURED* to *no perf MEASURED without a
host-log reference* — an unlogged MEASURED still reddens. Scope held: this is the **sim-tick component
only** — the end-to-end input→photon budget (and all fps / 1080–1440p / BF6) stays **NOT_MEASURED** until
the layer-3 renderer + capture exist.

The auto-affordance admission law (`auto_capsule`, `auto_loopable`) requires every `auto_*` to ship
derivation + witness + certificate + a defect that MUST violate the certificate — the same shape as D17;
automation proposes, the gate disposes, nothing enters authority ungated. Performance/visual targets
(competitive-FPS latency, 1080/1440p at 60–140 fps, BF6-class fidelity) are **NOT_MEASURED** and, for
visuals, never gate-provable: the renderer is a layer-3 consumer downstream of D15 that cannot feed
authority, so its bench needs the sealed protocol (`docs/bench_protocol.md`, named host) before any number
is quoted. The one-tick-late IK contract is **DECLARED** (fppose docstring); its red-first fixture waits
on physics wiring.

**The gate vacuity guard (incident 2026-07-13).** A sync-truncated `verify.py` once parsed cleanly, ran
zero checks, and exited 0 — a vacuously green gate. `report()` now refuses below a pinned row floor
(`ROWS_FLOOR = 300`, a deliberate underestimate of the live count) and refuses if the terminal
`tamper-selftest` row never ran; CI greps the literal `^GATE PASSED$` line, never the exit code alone
(`exit-0 ≠ ran`). `tests/test_gate_guard.py` proves the guard red-first by truncating a scratch copy of
`verify.py` at `def main(` and confirming it silently exits 0 with no tail line — the exact failure the
CI grep now catches.

**urdr-homology — a division-free 𝔽₂ persistent-homology witness + a topological OOB / anti-cheat
layer (URDRPD1), MEASURED (reference).** `tools/homology/urdr_homology.py` computes Betti numbers (β0
components, β1 tunnels, β2 voids) and a persistence diagram over a Vietoris–Rips filtration built from
EXACT integer squared distances (no square root, no division), reducing the boundary matrices over 𝔽₂ —
XOR only, entries never leave {0,1}, zero coefficient growth, so the reduction is bit-identical across
silicon with no overflow surface of its own. It is deliberately **NOT** integer Smith Normal Form: Betti
numbers are ranks over a field, and 𝔽₂ delivers them without division or coefficient explosion; SNF over ℤ
is needed only for TORSION, which no use case here asks for, so it is absent (an honest omission, stated
not hidden). Betti numbers are field-dependent (ℝP² reads β1=1 over 𝔽₂, 0 over ℚ), so the witness RECORDS
its field — an untagged diagram is unfalsifiable, the way an un-hosted latency number is. Five gate rows,
each red-first: **known-answer** (β of hollow-triangle S¹ `[1,1,0]`, disk `[1,0,0]`, tetrahedron-boundary
S² `[1,0,1]` with its β2 void, two components `[2,0,0]` — all match textbook, validity not outcome — and
the fundamental lemma ∂²=0 on each); **two-counts** (rank-β equals the persistence essential-class count
on the square filtration, `[1,0,1]` — two independent computations of the same invariant, non-vacuity);
**witness** (the URDRPD1 persistence digest pinned ×2, a retagged field diverges); plus **oob** and
**refuse**. The overflow/refuse surface is relocated honestly: 𝔽₂ cannot overflow, but the squared-distance
arithmetic can and the Rips simplex count explodes combinatorially, so both hit a hard `TOPOLOGY-REFUSE`
at the i64 ceiling / a simplex cap (field.py's FIELD-REFUSE precedent), never a silent wrap. Grade:
**MEASURED (reference)**; cross-placement (C99 self-verify + Rust owner-attest) is the stated next step,
**SPECULATIVE** until run. `does_not_show`: torsion, performance, sub-tick timing.

**The anti-cheat / OOB tailoring — topology builds the map, a cheap parity read uses it.** Persistent
homology is the WRONG tool for per-frame clip detection (≈O(simplices³), and it does not localize the
offending frame — a per-frame parity test is O(faces) and does), so the module does NOT compute homology
of a trajectory per frame. Instead it computes ONCE the connected-component / void decomposition of the
static free space (β0 of the complement), labelling every cell authorized / sealed-pocket / exterior; per
frame it is an O(1) `locate` — a body in the authorized component is `OK`, in a bounded pocket a
`CLIP-IN-POCKET` (teleported inside closed geometry), on a border-touching component `OOB`. The engine's
own law, applied: the topological boundary is the ACTIVE CONSTRAINT, the per-frame verdict the interior's
deterministic response. Net defense reuses the frozen *peers-agree-or-localize* pattern, not a new
composition algebra: each peer recomputes the static-decomposition witness (`URDROOB1` — an altered map
yields a different digest = `TOPOLOGY-DESYNC`) and a per-tick occupancy signature (`URDROCC1` over the
bodies' component ids — a clipped body flips it, localizing the id). The `homology:oob` row pins all four
verdicts and both defect divergences (a punched wall merges the pocket, β0 3→2; a body teleported into the
pocket flips the signature). Gate stage `homology` (5 rows) + `tests/test_homology.py` (15 falsifiers) →
gate **519 unit falsifiers / 372 rows**.

**Cross-placed — three placements, two OSes (C99 self-verified; Rust owner-attested).** `homology_c/homology.c` is an
independent placement — its own 𝔽₂ XOR reduction, square-Rips persistence, and free-space flood
decomposition, own SHA-256 — reproducing all ten pinned goldens bit-for-bit (betti 110/100/101/200,
betti_square 101, `pd_square befa487a…`, `oob_arena 44460896…`, `oob_defect 9d356475…`, `occ_ok 6cc3d5e5…`,
`occ_clip efe6e2db…`), self-verified in-session (`cc -O2 -std=c99 -Wall -Wextra`, zero warnings), with
`--defect` diverging (sphere β2 goes wrong when the rank-∂2 subtraction is dropped) → **MEASURED (C99)**.
`homology_rs/homology.rs` **ADMITTED on the owner's Windows host** (std-only Rust, rustc -O, 2026-07-14):
10/10 goldens reproduced and `--defect` diverges (disk 111, sphere 134) → **MEASURED**. So urdr-homology
is three placements (Python + C99 + Rust), two OSes, golden AND defect parity — the frontfps ladder's
cross-placement bar, now met by the first post-frontfps module. The pinned set is golden AND defect
(`oob_defect`, `occ_clip`, the `--defect` betti), so parity is proven on both sides of each falsifier.

**doc-currency — the headline counts must match reality (mechanical enforcement), MEASURED.**
`tools/specfreeze/doc_currency.py` (the count-sibling of `freeze_check`) re-derives the project's
headline numbers from ground truth — placement counts from the filesystem (`tools/**/*_rs` = 21,
`*_c` = 12), the unit-falsifier count from the gate's OWN runtime `testsRun`, and the row total from
the live gate — and the `doc-currency` gate row reddens if any tracked README/paper quotes a
different number. Markdown emphasis is stripped before scanning, so a bold `**519**` cannot hide a
stale count, and a planted stale number is caught (`doc-currency-selftest`); the stage runs last so
the row total is final. On introduction it immediately earned its keep — it caught stale counts a
hand comb had missed (`13 Rust + 4 C99` deep in the root README and `docs/PAPER.md`, plus a
bold-split `**519** unit falsifiers`), which drove the reconciliation to the live totals. Gate stage
`doc-currency` (2 rows) + `tests/test_doc_currency.py` (5 falsifiers) → gate **524 unit falsifiers /
374 rows**. Scope: only current-state docs are enforced; historical ledgers (this file, the frontfps
OODA reports) keep their point-in-time counts by design. "Remember to update the docs" is now a
falsifier, not a hope — the same anti-rot move as `spec_freeze`, applied to counts instead of digests.

**Optimistic verification — a witness-chain dispute settled by re-executing ONE tick
(`tools/netcode/fraud.py`), MEASURED (reference).** The reference for `docs/fraud_proof.md`'s core
law: a light referee adjudicates a dispute between two `URDRLSTT` chains over a fixed world + input
log by re-executing exactly the single tick where they first diverge — never the whole run. It
reuses the frozen surface entirely (`worldstep.step_tick`, `lockstep._digest` / `first_desync` /
`canon`); the only new logic is the adjudicator and the no-fabrication (pre-state digest) check —
so **no new witness class** (one more datum for C8: a protocol *over* the frozen `URDRLST1`/
`URDRLSTT`, not a new authority law). Four gate rows: **verdicts** (the honest chain wins both role
orders; identical → no dispute; two liars → NEITHER; scenario pinned to `fraud_trace c90de767…`);
**one-tick** (the load-bearing property — the referee re-executes `step_tick` exactly ONCE, not the
T-tick run, proven by a call counter); **refusal** (a fabricated pre-state that does not hash to the
agreed frame is FRAUD-REFUSEd before any re-execution); **selftest** (the dispute localizes to the
first divergence, agreeing with `first_desync`; identical → None, non-vacuity). Red-first: dropping
the pre-state bind OR the re-execution each reddens a falsifier. Gate stage `netcode_fraud` (6 rows)
+ `tests/test_fraud.py` (13 falsifiers) → gate **537 unit falsifiers / 380 rows** — and the
`doc-currency` guard caught the stale counts on this very increment and forced the reconciliation
(the anti-rot tool policing the build that grew it). **Novelty (graded):** the mechanism is
established (optimistic rollups — Arbitrum, Optimism; verification games — Truebit, Canetti–Riva–
Rothblum); the novel part is the real-time deterministic game-tick application, possible only
because the tick is exact-integer + hash-committed. No known shipping-FPS prior art, but first-ness
is **DECLARED, not MEASURED** (a first is unprovable without a prior-art survey). Honest scope:
settles COMPUTATION correctness given an agreed input log; input legitimacy (aimbots) is out by law
(`integrity ≠ truth`); the fraud path's performance is `NOT_MEASURED` — the 0.073 ms is the native
*sim*-tick, a different tick. Increments 1 (single-round referee) and 2 (Merkle commitment +
O(log T) bisection — a propagated-divergence dispute settled by revealing **8 of 41 frames**
instead of the full chain, each cryptographically bound to the committed root via inclusion proofs;
`netcode-fraud-merkle` + `netcode-fraud-bisect` rows) are both built and gated. **Cross-placed
(increment 3):** `fraud_c/fraud.c` self-verified (`cc -O2 -std=c99 -Wall -Wextra`, own SHA-256) and
`fraud_rs/fraud.rs` (std-only, owner-attest) reproduce the NEW crypto layer bit-for-bit over the
reference's collide chains — Merkle root `fraud_merkle 8e5d341b…`, the O(log T) bisection
`fraud_bisect_tick 8` (8 of 41 frames), and the inclusion-proof accept / forged-leaf-sibling-position
reject — each with its own SHA-256. The **simulation beneath** is already cross-placed
(`worldstep_rs` / `worldregion_c` / `lockstep_rs`), so the rung is reproducible across three
languages / two OSes **by composition** (sim placement + crypto placement) rather than by re-placing
the sim. So the fraud placement count rises to 22 Rust / 13 C99.

**The referee itself is reproducible by composition — an inheritance argument, not a fourth
placement.** Its `adjudicate` is exactly `first_desync` (locate the divergence) + `worldstep.step_tick`
(re-execute one tick) + `lockstep._digest` (compare) over the cross-placed crypto layer — every
primitive it touches is already placed in C99 + Rust, and it adds no un-cross-placed computation, so a
dedicated native referee would be redundant. That reproducibility is therefore **`DECLARED`** (an
inheritance argument), NOT a bit-for-bit native re-run. The referee's own wall-clock stays
**`NOT_MEASURED`**: it is off the competitive path (dispute settlement runs on-challenge, not
per-frame) and has no dedicated bench. The competitive path is the *sim* tick, already MEASURED at
~0.073 ms — but that is `frontbench_rs` (the frontfps sim tick), a *different* tick than the referee's;
`worldstep_rs` cross-places the worldstep tick's *correctness*, not that number. The layer-3 renderer
remains unbuilt, which is what keeps the full input→photon latency stack `NOT_MEASURED`. `does_not_show`:
input legitimacy, zero-knowledge, performance.

## Evidence Against C8 — the sealed-alphabet hypothesis, tracked

C8 (D13 §C8, "region-scoped authority / the frame rule") is PARKED, and treated not as a deferred
feature but as a **falsifiable hypothesis**: *the existing witness algebra (`URDRLST1` state,
`URDRLSTT` trace) can express every composition the engine needs without a new witness class.* Each
subsystem that composes cleanly on the frozen laws is one datum against admitting the glyph, and the
seal grows *empirically* stronger with each — additions become rarer because the core keeps absorbing
new domains unchanged. This section is the running evidence; new subsystems append one honest line.

The precise claim under test is narrow: not "nothing new was ever added" (N3 added cryptography, N5
added an identity digest), but **"no new WITNESS class / composition algebra was ever required."** That
is the thing C8 would introduce, and the thing that has not been needed.

- **N2 (rollback):** late delivery + rewind/replay composed on `URDRLST1`/`URDRLSTT` unchanged; no new witness class.
- **N3 (auth):** added Lamport-OTS signatures + a roster (an authentication layer), but the witness chain law was untouched — auth decides *who*, not *what is witnessed*.
- **N5 (worldpeer):** added one identity law (`URDRWPN1` world pin, an entry gate), yet witness COMPOSITION stayed the frozen `URDRLSTT` — no composite-witness algebra.
- **N4.1 (contact):** body-body contact reused the witness laws entirely; only the tick grew.
- **D14 (front-end contract):** every authoring modality became a consumer of the `URDROBJ2` canon; identity is geometry-only, no new law.
- **D15 (view contract):** the view frame CARRIES the authoritative witness as a bound reference; presentation moves a separate `VIEW` digest, the authority witness class is unchanged.
- **D16 (regional authority):** the direct test of C8's own question — regional composition reproduces the monolithic `URDRLST1`/`URDRLSTT` bit-for-bit with **no new witness class**, across three placements (Python + C99 + Rust). C8's hypothesis (*regional witnesses may need a new class*) was tested and **refuted**.
- **frontfps (Stages 1–4):** the consolidated FPS/MMO authoring surface reused the `URDROBJ2`/geometry-identity canon, the D15 view law, and D16 seams unchanged; motion added a numeric substrate (quaternions on the frozen FIELDFP laws), not a new witness class. Authoring, animation, and hitboxes composed on the frozen alphabet — one more datum, no language pressure.
- **urdr-homology (topological analysis + OOB defense):** the honest split. It DOES mint new witness classes — `URDRPD1` (persistence diagram), `URDROOB1`/`URDROCC1` (static decomposition + occupancy) — for a genuinely new quantity, the topological structure of geometry. But, exactly like D15's VIEW digest, these are *downstream, non-authority* observables: the OOB net-defense reuses the frozen *peers-agree-or-localize* pattern over the new digest, and the `URDRLST1`/`URDRLSTT` authority composition algebra is untouched. So this is transparent counter-evidence on the WIDE reading ("nothing new was ever added") and one more datum FOR the seal on the NARROW claim under test (no new AUTHORITY-composition class) — a new observable, not a new authority language.

**Designed falsification attempts (open).** Each is a genuine try to BREAK D16, valuable precisely
because it is expected to compose — a clean pass is more evidence for the seal, a genuine failure is the
only thing that re-opens C8:

1. **Dynamic repartitioning** — regions split/merge mid-simulation; the witness must stay identical across a re-partition on a live tick (today's partition-invariance is proven only across *static* seams).
2. **Interest-management migration** — thousands of bodies migrating authority every few ticks.
3. **Distributed authority graph** — regions on different machines, delayed ghost updates, boundary conditions still deterministic.

**Re-open bar.** Not "a glyph would be cleaner," but a measured workload that produces a stated
inexpressibility — *"there is no way to express this without duplicating authority semantics,"* *"the
same invariant now exists in two incompatible forms,"* or *"witness composition cannot be stated on
`URDRLST1`/`URDRLSTT`."* **Verdict to date: no language pressure observed** — every composition the
engine has needed has been expressible on the frozen alphabet. `the burden of proof to admit C8 rises
with each clean composition recorded here; the seal is not an assumption but an accumulating measurement`.
