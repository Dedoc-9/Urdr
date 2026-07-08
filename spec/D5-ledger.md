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
| Observer atlas injectivity (well-posedness made EXPLICIT; generalizes depth_perception to n=4): a chart family `A={Π_i}` determines the state IFF its charts jointly span the coordinates — `A(S1)=A(S2) ⟹ S1=S2`. The SPANNING atlas `{p_xy,p_zw}` (all four axes) SEPARATES distinct states (injective), RECONSTRUCTS via the lens round-trip (§8), and each chart is a witness-carrying frame binding its DIFFERENT image to the ONE authoritative digest `ᛝ(s)` (multi-observer consensus — a renderer/camera/LOD may vary freely while every observer agrees on one digest). A DEFICIENT (non-spanning) atlas COLLIDES two distinct states, so claiming injectivity dies — non-vacuous (a spanning atlas does not collide). The observer/rendering layer's first result: observation is referentially transparent, and an atlas is sufficient ONLY when it spans (the well-posedness condition, encoded explicitly, not assumed). Reuses charts + recon + `ᛝ`; no new primitive, no glyph; distinct from depth_perception (that was one recovery example — this is the injectivity biconditional with the spanning condition falsified) | IMPLEMENTED | MEASURED | `examples/atlas_injective.urdr` (⊢ [1,1,[3,1,4,1],1]), `examples/rejected/atlas_deficient_wrong.urdr` (URDR-ASSERT, non-vacuous) |
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
