<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# LESSONS — the discipline this repo inherits (as text, not as a dependency)

Urðr is a **standalone** project. It imports no code from Dentatus/Chronicle or Ursprung.
What it imports is the discipline those projects paid for. Each lesson below is stated as a
law of *this* repo, with where it is enforced. Lessons are cited as lineage, not authority:
`cited ≠ implemented` — the enforcement column is what counts.

| # | Lesson (paid for upstream) | Law here | Enforced by |
|---|---|---|---|
| L1 | Canonical bytes → SHA-256; identity *is* content. | Every value has one canonical byte form; `digest = sha256(canon(v))`. No digest is ever computed over non-canonical bytes. | `urdr/canon.py`; determinism falsifiers |
| L2 | No-inflation: evidence may never exceed maturity. Compile it to an unrepresentable state, don't police it after the fact. | Over-claiming source is **rejected by the static checker** (`URDR-INFLATE-STATIC`); `MEASURED` is unwritable in source (`URDR-EVIDENCE-UNEARNED`) and constructable only by the verify primitive ᛞ. A dynamic guard (`URDR-INFLATE-DYN`) remains as an unreachable-but-armed latch. | `urdr/check.py`, `urdr/values.py`; non-vacuous rejection tests |
| L3 | Determinism is an environment, not a hope: `PYTHONHASHSEED=0`, UTF-8 forced on Windows (`PYTHONUTF8=1`), no wall-clock, no unseeded RNG, no set/dict-order dependence, no absolute paths in results. | The interpreter core never calls a nondeterminism source; the gate re-runs programs in isolated subprocesses with a pinned env and compares digests bit-for-bit. | `verify.py` |
| L4 | Windows is a first-class host; Unicode dies at the console unless you force UTF-8 at every boundary. | All file I/O is explicit `encoding="utf-8"`; stdout is reconfigured to UTF-8; runner docs give the PowerShell incantation. | every `open()`; `urdr.py`; README |
| L5 | Validity, not outcome: a test that cannot fail proves nothing; a gate must contain a case that is *supposed* to go red. | The suite ships must-reject programs (checker must refuse them) and a deliberately tampered digest fixture the gate must fail. If the tamper case passes, the gate itself is broken and reddens. | `examples/rejected/`, `examples/must_fail/`, `verify.py` |
| L6 | Grade every claim; a green test certifies execution, never that a name means what it says. | Every capability is graded maturity × evidence in the boundaries ledger; README claims link to the ledger; no capability is described above its grade. | `spec/D5-ledger.md` |
| L7 | Capture nondeterminism at the boundary, never fake it away (clocks, RNG, floats, external reads are *inputs*). | The core stays pure and effect-free. Effects arrived (R4) exactly as promised: typed capabilities — reads recorded at the boundary as inputs inside content identity, writes planned in-language and executed at the līmes. | `urdr/capability.py`; `tests/test_capability.py`; D1 §16 |
| L8 | Bounded execution: an interpreter without a fuel meter is a nondeterministic halt oracle in disguise. | Evaluation carries a deterministic fuel budget; exhaustion is a *deterministic* error (`URDR-FUEL`), identical on every host. | `urdr/evaluate.py` |
| L9 | Build for extraction: every component must stand alone. | Lexer, parser, checker, evaluator, store, canon are separate stdlib-only modules with no circular imports; each is unit-tested in isolation. | `urdr/` layout; `tests/` |
| L10 | Arrival-order-independent canonical ordering is how you tame concurrency without lying about it. | Ported later as the deterministic-actor rung (canonical `(tick, actor, seq)` delivery order). Not implemented yet; graded `SPECULATIVE / N/A`. | ledger (R2 rung) |
| L11 | Integrity is not truth: reproducibility proves a record is unforged and re-derivable, never that the decision it records was wise. | Stated in README and ledger; the language's own vocabulary (`Grounded`, `MEASURED`) is defined as *verifier-passed*, not *true*. | README §honest boundaries; D1 §semantics |
| L12 | The membrane: if a read perturbs authoritative state, the change crossed the membrane and is wrong by definition. | ☽ (view) is a pure function of the store; the store is immutable; ☿ (edit) returns a *new* store with a new digest. There is no API through which a view can mutate. | `urdr/values.py` (immutable store); lens-law falsifiers |

Roadblocks met upstream that this design routes around **by construction** rather than by
assuming they have vanished:

1. **Float drift across hosts/accelerators** — v0.x core is integer-only with defined wrap;
   floats, if they ever arrive, arrive as a differential-checked accelerator path, never as
   the source of truth (directive §5c; the trilemma is surrendered honestly: leak-explicit,
   not leak-free).
2. **Hash/dict iteration order** — canonical serialization sorts keys; digests never touch
   Python iteration order; `PYTHONHASHSEED=0` is set anyway (belt and braces).
3. **Actor message-order nondeterminism** — not inherited; deferred to R2 with the canonical
   logical order already proven upstream. Until then, no concurrency syntax exists at all.
4. **Windows console encoding** — UTF-8 forced programmatically; ASCII digraphs make every
   program typeable and diffable even where glyphs cannot render (`typeable ≠ renderable`).
5. **A green gate hiding a vacuous suite** — the gate red-tests itself (L5).
