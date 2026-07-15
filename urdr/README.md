<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `urdr/` — the language kernel

## Index

Standard-library only, no third-party imports, no circular imports; every module stands alone
and is unit-tested in isolation (LESSONS L9, "build for extraction").

| Module | Role |
|---|---|
| `lexer.py` | NFC-normalized, closed-alphabet lexer (D1 §2, §4). A glyph and its ASCII digraph lex to the **same token**; confusables are refused (`URDR-LEX-CONFUSABLE`). |
| `parser.py` | Recursive-descent parser + AST (D1 §3). Nodes know their canonical bytes; λ bodies are α-normalized so spelling is not identity. |
| `check.py` | The static epistemic checker (D1 §5) — **the cage**: over-claiming source does not typecheck (`URDR-INFLATE-STATIC`); source that writes `MEASURED` is refused (`URDR-EVIDENCE-UNEARNED`). |
| `evaluate.py` | The deterministic, fuel-bounded evaluator — the **☉ reference placement** (D1 §6). Fuel exhaustion is a deterministic `URDR-FUEL`. |
| `compiler.py` | The closure compiler — a second, non-reference **placement** (D1 §14b), admitted per gate run only when its digests are bit-identical to ☉. |
| `canon.py` | Canonical bytes → SHA-256 (D1 §7). One canonical form per value; `digest = sha256(canon(v))`. Identity is content. |
| `values.py` | Runtime values + the epistemic ladder. `MEASURED`/`Grounded` is constructable only by the ᛞ verify path; the dynamic no-inflation latch lives here. |
| `capability.py` | R4 capabilities — the runner side of the *līmes*: reads are recorded inputs, writes are effect-plans; nothing ambient (D1 §16). |
| `modules.py` | R5 import-by-digest (D1 §17): a module is a `.urdr` file addressed by the SHA-256 of its canonical source; a wrong pin is refused statically. |
| `snapshot.py` | R2c runner-level store snapshots — persistence as a *līmes* at the process boundary; `Grounded`/λ do not cross. |
| `errors.py` | The stable error-code API. Codes are matched by tests and the gate, not by prose. |

## Whitepaper

The kernel is the sealed heart of the project: a small, closed-alphabet, epistemically-typed
language whose evaluator performs **no I/O** and consults **no** clock, RNG, float, or
iteration order — so identical program + inputs give an identical content digest, always.
Its distinctive law is the **epistemic cage**: the type system forbids a program from
*claiming* more certainty than it has earned (`MEASURED` cannot be written in source; only the
ᛞ verify path mints it). Identity is content (`digest = sha256(canon(v))`), which is what lets
every downstream placement and tool be cross-checked bit-for-bit. The kernel is **frozen**;
new surface enters only through the D1 §20 glyph-review (`tools/glyph_review.py`) or a spec
amendment, never casually.

## Dev notes

- Entry points: `../urdr.py` (`run` / `check` / `fmt`) and `../verify.py` (the gate).
  Normative behaviour is [`../spec/D1-spec.md`](../spec/D1-spec.md); falsifiers are in
  [`../tests/`](../tests/).
- The evaluator is the **reference**; the compiler is a *placement* that must agree with it
  each gate run. Do not let the compiler diverge "temporarily" — divergence voids admission.
- Do not add I/O, floats, clocks, or RNG to any kernel module: determinism is the whole
  contract, and the epistemic ladder depends on it. New glyphs require the §20 review.
