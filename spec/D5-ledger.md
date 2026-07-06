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
| Foreign placement oracle **harness** (R6a): a foreign implementation admitted as another placement iff its digest = the ☉ reference, else refused (`URDR-PLACEMENT-DIVERGENCE`; Rust instance `URDR-RUST-DIVERGENCE`) — the differential oracle (§14b) generalized to any substrate; no foreign code trusted, only agreement. Separate tool, own runner, stdlib-only. Does NOT assert any Rust impl agrees — that is the gap-ledger candidate | IMPLEMENTED | MEASURED | `tools/foreign_placement/test_foreign_oracle.py` (3 falsifiers: agreeing admitted, diverging reddens, no-digest errors) |
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
| Non-Python placements (bytecode VM, Rust) admitted by the same oracle | SPECULATIVE / N/A | R6 |
| Rust production compiler (same oracle admission) | SPECULATIVE / N/A | R6 |
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

| Candidate | Status | Question | Desired law | Falsifier | Promotion condition | observed_pressure |
|---|---|---|---|---|---|---|
| capability_attenuation | SPECULATIVE / N/A | Can a source program derive a *strictly weaker* capability? | Perm(child) ⊆ Perm(parent) | `URDR-CAP-ESCAPE` | a real program needs authority narrowing **and** composition through existing primitives (cap/recorded/plan) is insufficient | 0 |
| foreign_rust_kernel | SPECULATIVE / N/A | Can an *independent* Rust kernel (`urdr-core-rs`) reproduce the reference digest on the corpus? | Rust placement ≡ reference placement | `URDR-RUST-DIVERGENCE` | a Rust kernel matches canon+digest on the pinned corpus **and** a deliberate Rust defect is caught by the harness (`tools/foreign_placement/`); needs a cargo host — absent in the build sandbox | 0 |

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
