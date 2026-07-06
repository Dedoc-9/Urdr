<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Urðr (working name) — a glyphic, membrane-native, epistemically-typed language

> **Nihil ultrā probātum — nothing beyond what is proven.**

Urðr is a small programming language in which a program that claims more than it verifies
**does not typecheck**. Every capability claim in this repository carries two orthogonal
grades — **maturity** (`IMPLEMENTED` / `SCOPED` / `SPECULATIVE`) and **evidence**
(`MEASURED` / `DECLARED` / `N/A`) — and evidence never exceeds what maturity licenses.
The full graded inventory lives in [`spec/D5-ledger.md`](spec/D5-ledger.md). Anything this
README says beyond that ledger is a bug; file it.

Successor-in-discipline to the *Dentatus → Ursprung* line (executable epistemic
determinism); standalone in code. The ported laws are in [`LESSONS.md`](LESSONS.md).

## What exists today — `IMPLEMENTED / MEASURED` via the gate (rungs R0–R5 + §18–§20; tag v0.7.1)

- A ~20-glyph core alphabet curated from historical sign systems (Elder Futhark runes,
  a cuneiform determinative, Greek, astronomical signs, mathematical notation), every
  glyph with an ASCII digraph so programs are 100% typeable offline. Lexicon:
  [`spec/D1-spec.md`](spec/D1-spec.md); input methods: [`spec/D4-typeability.md`](spec/D4-typeability.md).
- An **epistemic annotation** `𒀭⟨maturity, evidence⟩ v` checked statically: source that
  rates evidence above maturity is rejected (`URDR-INFLATE-STATIC`); source that writes
  `MEASURED` at all is rejected (`URDR-EVIDENCE-UNEARNED`) — `MEASURED` is constructable
  only by the verify primitive **ᛞ**, which is the sole constructor of `Grounded` values
  (Milner's `thm` discipline, applied to evidence).
- A **membrane** over an immutable content-addressed store: **☽** view (pure), **☿** edit
  (new store, new digest), **↩** `anamnesis` (return to the exact prior state; digest
  equality is the test). Lens laws (get-put, put-get) are falsifiers, not prose.
- **Deterministic evaluation**: 64-bit wrapping integer semantics, no ambient
  nondeterminism, fuel-bounded; same program + inputs ⇒ same digest — verified
  bit-identical on two named hosts (Linux + Windows), not "any host" (D5).
- A **gate** (`verify.py`): re-runs every example twice in isolated subprocesses,
  asserts recorded digests, requires the must-reject programs to be rejected and the
  deliberately tampered fixture to fail (a gate that cannot go red proves nothing).
- **I/O as capabilities** (R4): nothing ambient. The runner mints unforgeable grants
  (`--grant NAME=read:PATH | NAME=write:PATH`) into the input `caps`; reads are
  **recorded inputs** (loaded once through the snapshot codec, digest-verified,
  replayed bit-identically, inside program identity); writes are **effect-plans** —
  pure values the runner executes at the līmes after success, all-or-nothing; anything
  ungranted or misused is `URDR-CAP`. The evaluator performs no I/O at any time.
  Spec: D1 §16; falsifiers: `tests/test_capability.py`.
- **Import-by-digest modules** (R5): dependencies are named by the SHA-256 of their
  canonical source, resolved offline from a `vendor/` store + `urdr.lock` the gate
  verifies; a wrong pin or tampered file is refused *statically* (`URDR-PIN`), an
  unvendored/unpinned digest too (`URDR-MODULE`). Byte-level addressing — the honest
  limit is `source-hash ≠ definition-hash` (D5). Spec: D1 §17.
- **Deterministic actors & persistence līmes** (R2): `weave` delivers messages in a
  canonical multiset order — one digest across every permuted schedule — and an actor
  that over-claims dies inside its own handler; runner snapshots re-verify digests and
  refuse to carry `Grounded`/λ across the boundary. Spec: D1 §13.
- **Compiler as a differential placement** (R3): a closure compiler (`--via compiled`)
  is admitted per gate run only when its digests are bit-identical to the ☉ tree-walk
  reference on the whole corpus; a deliberately defective path (`--via defect`) must be
  caught or the gate reddens. One shared kernel — the mint is singular. Spec: D1 §14.
- **User-directed conversion falsifiers** (exact integer algebra, ᛞ-sealed, no floats):
  the rhombohedral C₃ lattice (D1 §12b, ⊢11) and the centering / quotient operator
  M = nI−J (D1 §18, ⊢6). Each documents its provenance apart from its assigned meaning
  (`signum ≠ rēs`); neither claims anything about physics or society.
- **Evidence transitions** (D1 §19): an action earns a knowledge claim only by a
  *recorded state transition* a verifier can inspect (`claim-transition ≤ measured-delta`).
  `transition_witness(before, after)` — the first **library function** (spelled
  `transition_witness`, `⟿`, or `\tw`, all one digest) — witnesses a real passage and
  refuses a zero-delta one (`URDR-DELTA-UNEARNED`); it never mints `Grounded` (only ᛞ
  does). Falsifiers: `examples/evidence_transition.urdr`, `tests/test_transition.py`.
- **The glyph review** (D1 §20): a glyph is *earned*, not declared — a lossless alias of
  a proven operation, or `URDR-GLYPH-NOT-EARNED`. First glyph earned: `⟿`. Machinery:
  `tools/glyph_review.py`. See **Glyphs — creation laws and reference** below.
- **`voi_gate`** (`tools/voi_gate/` — a *separate* tool: float, not the integer core, its
  own runner): a Value-of-Information decision gate (`value_per_bit·VoI − Cost > ρ`, VoI =
  mutual information in bits) that *proposes* claims and never mints them. The engine is
  tested; the claim it *improves outcomes* is `SPECULATIVE` behind a calibration ledger.

## Quickstart (offline; Python ≥ 3.10, stdlib only)

```powershell
# Windows PowerShell
$env:PYTHONUTF8 = "1"          # UTF-8 at the console boundary (see LESSONS L4)
python .\urdr.py run examples\lens_roundtrip.urdr
python .\verify.py             # the gate: GATE PASSED or a nonzero exit
```

```bash
# Linux / macOS
python3 urdr.py run examples/lens_roundtrip.urdr
python3 verify.py
```

`urdr.py check FILE` typechecks only; `urdr.py fmt FILE` rewrites ASCII digraphs to glyphs.
No third-party dependency at author-, compile-, or run-time. The only external asset is a
covering font *for rendering* (Noto Sans Runic / Cuneiform / Symbols 2 / Math) — rendering,
not execution: the suite passes on a machine that cannot display a single rune.

## The three honest conversions (directive §2, stated as bounds)

1. **"M-theory capable"** is converted to: *membrane-native* (the ☽/☿/↩ primitive) plus
   *graded-algebra-expressive* — the ability to represent a ℤ₂-graded algebra as a value
   and verify its defining relations by evaluation. The algebra falsifier landed at **R1**
   (`IMPLEMENTED / MEASURED`: ℤ₂ closure ⊢64, Cl(3) ⊢9, wrong-relation dies). This is a claim about a type system, **never about physics**.
2. **"Symbolic alphabet"** is an original curated glyph set; each glyph's attested
   historical meaning is documented *separately* from its assigned semantics
   (`signum ≠ rēs`). We learned the graphical-algebra *method* from S. J. Gates Jr. &
   Michael Faux's adinkras and will not reproduce their notation (`learned ≠ copied`).
3. **"Observation and editing as one dataflow"** is a reversible lens over a
   content-addressed store, with `anamnesis` as the return operator. Lens laws are tested;
   the live-session editor over that dataflow is `SCOPED`.

## Glyphs — creation laws and reference

Urðr's alphabet is curated scholarship, not decoration. Every glyph is enterable
**offline** via an ASCII digraph, and the lexer treats a glyph and its digraph as the
*same token* (so a program can be written, diffed, and emailed in pure ASCII, then
canonicalized with `urdr.py fmt`). Fonts are needed only to *render*; the suite passes on
a machine that cannot display a single rune (`typeable ≠ renderable`).

### The glyph creation laws

1. **Glyph budget** (design law 5). A glyph is spent **only where semantics are novel** —
   epistemics, the membrane, structure. Arithmetic, grouping, and literals stay ASCII, and
   every glyph must justify itself against its own digraph. New *operations* arrive as
   ASCII prelude functions first (the `weave` / `cap` / `transition_witness` precedent) and
   earn a glyph later, or never.
2. **`signum ≠ rēs`** (design law 6). A glyph's *attested* historical meaning is provenance
   only; its meaning in Urðr is the *assigned* column and nothing else. The two are recorded
   separately in D1; resemblance is a mnemonic courtesy, never a claim about (or by) history.
3. **Exclusions** (D1 §2.6, binding). Glyphs whose dominant modern reading includes
   organized hate-appropriation are excluded outright (ᛋ, ᛟ, ᛉ, ᛏ), as are runes visually
   confusable with ASCII / Greek / Cyrillic. The confusables table names each intruder and
   what it imitates; a look-alike is rejected (`URDR-LEX-CONFUSABLE`), never guessed at.
4. **The glyph review** (D1 §20). A glyph is **earned, not declared** — the *final* artifact
   of a proof trail, the shortest faithful spelling of an operation already proven:
   `ASCII function → measured law → falsifier → stable semantics → glyph alias`. The review
   (`tools/glyph_review.py`) can **reject** with `URDR-GLYPH-NOT-EARNED`, checking five
   mechanical criteria: *lossless* (glyph-program digest = ASCII-program digest — a spelling,
   not new behaviour), *not confusable*, *not an excluded rune*, *has a digraph*, and
   *provenance recorded*. A failed review is a successful gate result, and the ASCII function
   stays valid either way. That asymmetry keeps the budget honest.

### How developers use them

Type the ASCII digraph and run `urdr.py fmt FILE` to canonicalize to glyphs, or type the
glyphs directly (OS pickers / editor snippets — see [`spec/D4-typeability.md`](spec/D4-typeability.md)).
Both spellings lex to one token and produce **one digest**; spelling is never identity. In
the tables below the ASCII column is what you type; `&#124;` shown in a digraph is a literal
`|` character.

### Epistemic glyphs — claims, evidence, verification

| Glyph | ASCII | Purpose | In code |
|---|---|---|---|
| 𒀭 | \an | Wrap a value in a graded **Claim** `⟨maturity, evidence⟩` | `c ≔ 𒀭⟨IMPLEMENTED, DECLARED⟩ 42` |
| ᛞ | \ve | **Verify** — run a λ on a claim's value; the **sole** mint of `MEASURED`/`Grounded` | `ᛞ(λ v ↦ v = 42, c)` |
| ↯ | \cf | **Conflict** — the value a failed verification yields; branch on it, never average | *(output value; `conflicted(x)`)* |
| ⊢ | \&#124;- | **Witness display** — how a `Grounded` value renders (output only, no constructor) | `w ⊢ 42` *(printed)* |
| ⟨ ⟩ | <&#124;  &#124;> | **Tag brackets** delimiting the ⟨maturity, evidence⟩ pair | `⟨SCOPED, NA⟩` |

### Membrane glyphs — state as an immutable, content-addressed store

| Glyph | ASCII | Purpose | In code |
|---|---|---|---|
| ᚠ | \st | **Store** literal — an immutable, content-addressed record | `s ≔ ᚠ{x: 1, y: 2}` |
| ☽ | \vw | **View** (get) — pure read of a field; never perturbs | `☽(s, 'x)` |
| ☿ | \ed | **Edit** (put) — returns a *new* store with a field set, parent-linked | `☿(s, 'x, 5)` |
| ↩ | \am | **Anamnesis** — return to the exact prior state (digest-identical) | `↩(s)` |
| ᛝ | \di | **Digest** — the SHA-256 content address of any value, first-class | `ᛝ(s)` |
| ᛃ | \pv | **Provenance walk** — ancestor digests, nearest first (`[]` at a root) | `ᛃ(s)` |

### Structural glyphs — binding, functions, iteration, comparison

| Glyph | ASCII | Purpose | In code |
|---|---|---|---|
| ≔ | := | **Bind** a name (immutable; rebinding is a parse error) | `answer ≔ 42` |
| λ | \fn | **Function** abstraction, closing over its environment | `inc ≔ λ x ↦ x + 1` |
| ↦ | \&#124;-> | **Maps-to** — separates λ parameters from body | `λ x y ↦ x + y` |
| ∘ | \o | **Compose** — `f ∘ g` = `λ x ↦ f(g(x))` | `twice ≔ inc ∘ inc` |
| ᛚ | \fl | **Flow** — `x ᛚ f` = `f(x)`; chains read as a pipeline | `5 ᛚ inc ᛚ twice` |
| Σ | \fo | **Fold** — the only iteration in v0.1 (left fold) | `Σ(xs, 0, λ a x ↦ a + x)` |
| ≟ | =? | **Assertion gate** — equal by digest ⇒ the value, else dies `URDR-ASSERT` | `≟(a, b)` |
| ≠ | != | **Structural inequality** by digest, yielding `1`/`0` | `a != b` |
| ≤ ≥ | <=  >= | **Integer comparison** | `x <= 3` |

### Library glyphs earned by review (D1 §20)

| Glyph | ASCII | Purpose | In code |
|---|---|---|---|
| ⟿ | \tw | **Transition witness** — a lossless alias of `transition_witness(before, after)`: witnesses a *real* state passage, refuses a zero-delta one (`URDR-DELTA-UNEARNED`), and **never** mints `Grounded` (only ᛞ does). The dual of `≟`. | `⟿(before, after)` |

### The ASCII surface (part of the alphabet by the glyph budget)

`+ - *` wrapping 64-bit arithmetic · `= < >` comparison · `?(c, t, f)` conditional (lazy
branches) · `( )` grouping · `[ ]` lists · `{ } , :` store/list punctuation · `'name`
symbol literal · integer literals · `#` line comment · `@<64-hex>` module pin (R5, e.g.
`use @<digest> as lib`). These stay ASCII because their semantics are not novel.

### Reserved / deferred (curated, not yet in the grammar)

`𒁹` (U+12079) and `𒌋` (U+1230B) are cuneiform base-60 numeral digits (`SCOPED`, R1+);
`☉` (U+2609, Sun) is the reference-path marker for the differential oracle — it appears in
the gate's output (`compiled ≡ ☉ …`) but is not yet source syntax (`SCOPED`, R3). Each will
pass a glyph review before it enters the grammar, or it will not enter.


## Roadmap (rungs; each = spec → std-only impl → red-capable test → honest grade)

| Rung | Content | Grade today |
|---|---|---|
| R0 | Core lexicon, epistemic checker, membrane, determinism gate | `IMPLEMENTED / MEASURED` |
| R1 | α-normalized canon; list prelude; **graded-algebra falsifiers** (ℤ₂ closure ⊢64, Cl(3) relations ⊢9, wrong-relation program dies); provenance ᛃ; CI (4 jobs: 2 OS × 2 Python, pinned in D5) | `IMPLEMENTED / MEASURED` |
| R2 | Deterministic actors (`weave`; canonical multiset order; one digest across permuted schedules; actor-local cage), persistence *līmes* (snapshots; Grounded does not cross), TLA+ membrane model (`DECLARED`) | `IMPLEMENTED / MEASURED` |
| R3 | WHAT/WHERE landed: closure compiler admitted **only** by differential oracle vs the ☉ tree-walk reference (singular kernel — one mint; defect fixture proves the oracle can redden); verbose keyword profile (three spellings, one digest) | `IMPLEMENTED / MEASURED` |
| R4 | I/O & external state as **capabilities**: nothing ambient; reads are recorded inputs replayed bit-identically; writes are effect-plans executed at the līmes; ungranted use rejected (`URDR-CAP`) | `IMPLEMENTED / MEASURED` |
| R5 | Modules & packaging without a network: **import-by-digest** (Unison lesson, byte-level), vendor dir + lockfile verified by the gate; a wrong pin is refused, not resolved (`URDR-PIN`/`URDR-MODULE`) | `IMPLEMENTED / MEASURED` |
| R6 | Rust production compiler — admitted by the same differential oracle, or not at all | `SPECULATIVE / N/A` |

## Honest boundaries (§9, in our own words)

- Urðr is **not physics**. It can check (R1, landed) that a finite graded-algebra value
  satisfies stated relations under its own evaluator. It does not model, simulate, or
  validate M-theory, and no green test here says anything about the universe.
- A glyph's ancient meaning is **not** its programming meaning; both are documented,
  separately, in D1. The alphabet is scholarship, not iconography; glyphs with a dominant
  modern hate-appropriation are excluded outright (see D1 §exclusions — this includes
  overriding the directive's own illustrative ᛟ example, per its curatorial law).
- `digest ≠ MAC` (integrity against accident, not against an adversary). `declared ≠
  verified`. `Grounded` means *a named verifier passed under this evaluator* — never "true".
- A green gate certifies execution of these tests on this code — never that a name means
  what it says, and never universal performance (`benchmark ≠ universal`).
- Totality is **not claimed**: evaluation is fuel-bounded; exhaustion is a deterministic
  error, not a proof of termination.
- Metatheory (progress/preservation, no-inflation soundness as a theorem, lens laws as
  theorems) is `CONJECTURED`; what is `TESTED` is the falsifier suite. See D5.

## License

AGPL-3.0-only. Copyright (C) 2026 Daniel J. Dillberg.
