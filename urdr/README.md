<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `urdr/` — the language

The Urðr language itself: standard-library only, no third-party imports, no circular imports.
Every module stands alone and is unit-tested in isolation (LESSONS L9 — "build for extraction").
The evaluator performs **no I/O** and consults **no** clock, RNG, float, or iteration order.

| Module | Role |
|---|---|
| `lexer.py` | NFC-normalized, closed-alphabet lexer (D1 §2, §4). A glyph and its ASCII digraph lex to the **same token**; confusables are refused (`URDR-LEX-CONFUSABLE`). |
| `parser.py` | Recursive-descent parser + AST (D1 §3). Nodes know their own canonical bytes; λ bodies are α-normalized so spelling is not identity. |
| `check.py` | The static epistemic checker (D1 §5) — **the cage**: over-claiming source does not typecheck (`URDR-INFLATE-STATIC`); source that writes `MEASURED` is refused (`URDR-EVIDENCE-UNEARNED`). |
| `evaluate.py` | The deterministic, fuel-bounded evaluator — the **☉ reference placement** (D1 §6). Fuel exhaustion is a deterministic `URDR-FUEL`. |
| `compiler.py` | The closure compiler — a second, non-reference **placement** (D1 §14b), admitted per gate run only when its digests are bit-identical to ☉. |
| `canon.py` | Canonical bytes → SHA-256 (D1 §7). One canonical form per value; `digest = sha256(canon(v))`. Identity is content. |
| `values.py` | Runtime values + the epistemic ladder. `MEASURED`/`Grounded` is constructable only by the ᛞ verify path; a dynamic no-inflation latch lives here too. |
| `capability.py` | R4 capabilities — the runner side of the *līmes*: reads are recorded inputs, writes are effect-plans; nothing ambient (D1 §16). |
| `modules.py` | R5 import-by-digest (D1 §17): a module is a `.urdr` file addressed by the SHA-256 of its canonical source; a wrong pin is refused statically (`URDR-PIN` / `URDR-MODULE`). |
| `snapshot.py` | R2c runner-level store snapshots — persistence as a *līmes* at the process boundary; `Grounded`/λ do not cross. |
| `errors.py` | The stable error-code API. Codes are matched by tests and the gate, not by prose. |

The public entry points are `../urdr.py` (`run` / `check` / `fmt`) and `../verify.py` (the gate).
Normative behaviour is [`../spec/D1-spec.md`](../spec/D1-spec.md); falsifiers are in [`../tests/`](../tests/).
