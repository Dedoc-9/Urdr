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
| Determinism: same source ⇒ same digest, twice, subprocess-isolated, golden-pinned | IMPLEMENTED | MEASURED | `verify.py` examples stage; green ×2. Cross-host: all four example digests bit-identical on Linux (Python 3.10.12, sandbox) and Windows (PowerShell, `PYTHONUTF8=1`), 2026-07-06. Two named hosts, not "any host" |
| Defined i64 wrap semantics | IMPLEMENTED | MEASURED | `tests/test_determinism.py` |
| Fuel-bounded evaluation, deterministic URDR-FUEL | IMPLEMENTED | MEASURED | `tests/test_determinism.py` |
| Gate red-capability (tamper fixture must fail; red-first transcript kept) | IMPLEMENTED | MEASURED | `verify.py` tamper stage; `docs/transcripts/red.txt` |
| Offline: stdlib-only, no network at any phase | IMPLEMENTED | DECLARED | by construction (no import touches the network); a network-disabled CI run is SCOPED |
| Whole-program totality | — | — | **not claimed**; fuel bound instead (D1 §6) |

## Deferred (the honest remainder)

| Capability | Grade | Rung |
|---|---|---|
| Graded-algebra falsifier (ℤ₂/Clifford relations verified by evaluation; Gates-method learned, our notation) | SCOPED / N/A | R1 |
| α-normalization of λ canonical form (current α-sensitivity pinned by test) | SCOPED / N/A | R1 |
| Base-60 numeric literals (𒁹, 𒌋) | SCOPED / N/A | R1 |
| Provenance/lineage operator (glyph deliberately unassigned; ᛟ excluded by curatorial law) | SCOPED / N/A | R1 |
| Division / modulo with defined zero semantics | SCOPED / N/A | R1 |
| Persistent on-disk store; cross-run anamnesis | SCOPED / N/A | R2 |
| Deterministic actors (canonical `(tick, actor, seq)` order; digest invariant across schedules) | SCOPED / N/A | R2 |
| TLA+ model of membrane/reversal laws | SCOPED / N/A | R2 |
| WHAT/WHERE placement split, *līmes* boundaries, differential oracle, ☉ reference marker | SCOPED / N/A | R3 |
| Effects & capabilities (object-capability discipline); failure model; interop *līmes* | SCOPED / N/A | R4 |
| Rust reference implementation | SPECULATIVE / N/A | R5 |
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
recursion, I/O, clock, RNG, concurrency, modules, or REPL in v0.1 (each graded above or
absent by design law). Performance: no figures published; any future figure will name
its host (`benchmark ≠ universal`).
