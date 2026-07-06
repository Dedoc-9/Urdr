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

## What exists today (v0.1 core) — `IMPLEMENTED / MEASURED` via the gate

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
  nondeterminism, fuel-bounded; same program + inputs ⇒ same digest, on any host.
- A **gate** (`verify.py`): re-runs every example twice in isolated subprocesses,
  asserts recorded digests, requires the must-reject programs to be rejected and the
  deliberately tampered fixture to fail (a gate that cannot go red proves nothing).

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
   and verify its defining relations by evaluation. The algebra falsifier is rung **R1**
   (`SCOPED / N/A` today). This is a claim about a type system, **never about physics**.
2. **"Symbolic alphabet"** is an original curated glyph set; each glyph's attested
   historical meaning is documented *separately* from its assigned semantics
   (`signum ≠ rēs`). We learned the graphical-algebra *method* from S. J. Gates Jr. &
   Michael Faux's adinkras and will not reproduce their notation (`learned ≠ copied`).
3. **"Observation and editing as one dataflow"** is a reversible lens over a
   content-addressed store, with `anamnesis` as the return operator. Lens laws are tested;
   the live-session editor over that dataflow is `SCOPED`.

## Roadmap (rungs; each = spec → std-only impl → red-capable test → honest grade)

| Rung | Content | Grade today |
|---|---|---|
| R0 | Core lexicon, epistemic checker, membrane, determinism gate | `IMPLEMENTED / MEASURED` |
| R1 | α-normalized canon; list prelude; **graded-algebra falsifiers** (ℤ₂ closure ⊢64, Cl(3) relations ⊢9, wrong-relation program dies); provenance ᛃ; CI on two OSes | `IMPLEMENTED / MEASURED` |
| R2 | Deterministic actors (`weave`; canonical multiset order; one digest across permuted schedules; actor-local cage), persistence *līmes* (snapshots; Grounded does not cross), TLA+ membrane model (`DECLARED`) | `IMPLEMENTED / MEASURED` |
| R3 | WHAT/WHERE + the first real placement: a bytecode compiler admitted **only** by differential oracle against the tree-walk reference (☉ spent here); verbose keyword profile (third spelling, one token stream, one digest) | `SCOPED / N/A` |
| R4 | I/O & external state as **capabilities**: nothing ambient; reads are recorded inputs replayed bit-identically; writes are effect-plans executed at the līmes; ungranted use rejected (`URDR-CAP`) | `SCOPED / N/A` |
| R5 | Modules & packaging without a network: **import-by-digest** (Unison lesson), vendor dir + lockfile verified by the gate; a wrong pin is refused, not resolved | `SCOPED / N/A` |
| R6 | Rust production compiler — admitted by the same differential oracle, or not at all | `SPECULATIVE / N/A` |

## Honest boundaries (§9, in our own words)

- Urðr is **not physics**. It can (once R1 lands) check that a finite graded-algebra value
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
