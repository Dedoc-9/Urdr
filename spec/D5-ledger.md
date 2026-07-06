<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D5 — Boundaries ledger (every claim graded)

Grades: **maturity** `IMPLEMENTED` / `SCOPED` / `SPECULATIVE` × **evidence** `MEASURED` /
`DECLARED` / `N/A`. Evidence never exceeds maturity's ceiling — the same ladder the
language enforces, applied to the language's own claims. `MEASURED` below means: a
falsifier exercising the capability is green in `verify.py` on a named host (see
`docs/transcripts/green.txt`); it never means universally proven.

## Capability inventory (v0.1)

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
| Determinism: same source ⇒ same digest, twice, subprocess-isolated, golden-pinned | IMPLEMENTED | MEASURED | `verify.py` examples stage; green ×2. Cross-host: all four example digests bit-identical on Linux (Python 3.10.12, sandbox) and Windows (PowerShell, `PYTHONUTF8=1`), 2026-07-06. Two named hosts, not "any host" |
| Defined i64 wrap semantics | IMPLEMENTED | MEASURED | `tests/test_determinism.py` |
| Fuel-bounded evaluation, deterministic URDR-FUEL | IMPLEMENTED | MEASURED | `tests/test_determinism.py` |
| Gate red-capability (tamper fixture must fail; red-first transcript kept) | IMPLEMENTED | MEASURED | `verify.py` tamper stage; `docs/transcripts/red.txt` |
| Offline: stdlib-only, no network at any phase | IMPLEMENTED | DECLARED | by construction (no import touches the network); a network-disabled CI run is SCOPED |
| Whole-program totality | — | — | **not claimed**; fuel bound instead (D1 §6) |

## Deferred (the honest remainder)

| Capability | Grade | Rung |
|---|---|---|
| Base-60 numeric literals (𒁹, 𒌋) | SCOPED / N/A | R1 |
| Division / modulo with defined zero semantics | SCOPED / N/A | R1 |
| Effect kinds beyond snapshot files (clock, RNG, network, live filesystem) — each arrives as a recorded/planned capability through the same mint, or not at all | SPECULATIVE / N/A | — |
| Actor glyph assignment (weave stays ASCII until semantics prove stable) | SCOPED / N/A | R3 review |
| WHAT/WHERE placement split, *līmes* boundaries, differential oracle, ☉ reference marker | SCOPED / N/A | R3 |
| Non-Python placements (bytecode VM, Rust) admitted by the same oracle | SPECULATIVE / N/A | R6 |
| Import-by-digest modules, vendor dir + lockfile verified by the gate | SCOPED / N/A | R5 |
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
recursion, clock, RNG, network, modules, or REPL (each graded above or absent by design
law). I/O exists ONLY as R4 capabilities — recorded reads and planned writes of snapshot
files at the līmes; live or ambient I/O does not exist, and the evaluator performs none
at any time. A recorded input is digest-verified, never authenticated (digest ≠ MAC
applies to fixtures too). Performance: no figures published; any future figure will name
its host (`benchmark ≠ universal`).
