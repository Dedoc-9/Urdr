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

## The manifold / observer engine (D7–D10) — a second arc, both placements

Beyond the language core, the repo now carries a **measured theorem map** for a deterministic,
verification-first manifold / observer engine (capstone: [`spec/D10-observer-engine-capstone.md`](spec/D10-observer-engine-capstone.md)).
Every row below is `MEASURED` on **two independent placements** — the ☉ Python reference AND the
independent `urdr-core-rs` Rust kernel — agreeing on the exact accept/reject frontier (D8
conformance: 29/29 vectors reproduced twice, defect caught 13/13).

- **Independent Rust kernel (D8, Stage 4).** `urdr-core-rs` — one std-only Rust file, hand-rolled
  SHA-256, no crates, no cargo — reproduces the reference digests and rejection codes for the whole
  conformance corpus; a deliberately-defective build is caught. The R6a "Rust substrate" is no longer
  speculative — it is **ADMITTED** at a named host scope
  ([`tools/urdr_core_rs/`](tools/urdr_core_rs/), [`spec/D8-portable-kernel.md`](spec/D8-portable-kernel.md)).
- **Deterministic numeric substrate (D9, Q32.32).** A fixed-point `Int` discipline —
  `add/sub/neg/from_int/mul/div/floor_int/sqrt` — deterministic *by construction* (no float, no host
  rounding), with overflow / div-by-zero / INT_MIN / sqrt-of-negative **refused** and floor rounding
  everywhere. Each op was proven by a faithful Python prototype ([`tools/fixpoint_proto/`](tools/fixpoint_proto/))
  before being encoded **division-free** in Urðr and measured on both placements
  ([`spec/D9-numeric-substrate.md`](spec/D9-numeric-substrate.md)).
- **The atlas / observer theorem (D10).** `Recoverable(A) ⟺ ∩ᵢ ker(Aᵢ) = {0}` — an observer atlas
  determines the state iff its charts span. Measured as: axis-selection charts (a computed `covers`
  predicate); a **data-parameterized** theorem (dimension n and the chart family are inputs, so
  4D/5D/nD are data choices); general integer **linear** charts (`det(M) ≠ 0` via a division-free
  cofactor); and **observation bound to a witnessed transition path** (view-laundering and forked
  history refused). No new primitive, no glyph — it composes Layer-1.
- **Shared-world runtime reference (host track, Python, Steps 1–3).** [`tools/world_host/`](tools/world_host/)
  — the smallest enforcement loop that *consumes* the measured invariants: authority = the kernel
  digest, an admissible observer = a covering atlas, a frame is admitted iff it reconstructs to the
  authority. Static world views → a transition-history chain (reorder / missing / fork refused) → a
  deterministic multi-actor scheduler (arrival-order invariant; speculative branch refused). Graded by
  its own integration tests, **not** the URDR gate — it extends no theorem.

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
| R6a | **Verified foreign execution boundary**: a foreign implementation (Rust) admitted as another *placement* iff `digest = reference`, else `URDR-RUST-DIVERGENCE` — no substrate trusted, only agreement (the §14b oracle generalized to N placements). Harness proven cargo-free (`tools/foreign_placement/`); an independent Rust kernel agreeing on the corpus is the remainder | harness `IMPLEMENTED / MEASURED`; Rust substrate now **ADMITTED** (see R6b) |
| R6b | **Independent Rust kernel ADMITTED** (D8): `urdr-core-rs` reproduces the conformance corpus bit-for-bit, twice, with a defect build caught — the R6a remainder discharged at a named host scope | `IMPLEMENTED / MEASURED` |
| M5 | **Deterministic numeric substrate** (D9, Q32.32): `add/sub/neg/from_int/mul/div/floor_int/sqrt`, division-free, refusal law; `sqrt` on a documented domain | `IMPLEMENTED / MEASURED (both placements)` |
| M6 | **Atlas / observer theorem** (D10): injectivity as a computed, data-parameterized predicate; axis-selection + general integer-linear charts; observation bound to a witnessed transition path | `IMPLEMENTED / MEASURED (both placements)` |
| M7 | **Shared-world runtime reference** (`tools/world_host/`, host track): static views → transition history → deterministic scheduler; a Python executable spec, Steps 1–3 | `IMPLEMENTED (host track) / integration-test green` |

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

## Repo map

Each main-tree folder carries its own README with the detail.

| Path | What lives there | README |
|---|---|---|
| [`urdr/`](urdr/) | The language: lexer, parser, checker, evaluator, canon, store, capabilities, modules, compiler — stdlib-only, no circular imports | [`urdr/README.md`](urdr/README.md) |
| [`spec/`](spec/) | Normative specs D1–D10 (design laws, grammar, membrane, portable kernel, numeric substrate, observer capstone), the D5 graded ledger, the TLA+ membrane model | [`spec/README.md`](spec/README.md) |
| [`examples/`](examples/) | The corpus the gate runs: accepted `.urdr` fixtures + golden `.digest`, `rejected/` must-die programs + `MANIFEST.txt`, `must_fail/` the tamper self-test, `vendor/` import-by-digest modules | [`examples/README.md`](examples/README.md) |
| [`tests/`](tests/) | Unit falsifiers (pytest / unittest), one per subsystem — each designed to be able to go red | [`tests/README.md`](tests/README.md) |
| [`tools/`](tools/) | Separate tools: `fixpoint_proto/` (proven numeric prototypes), `foreign_placement/` (the differential-oracle harness), `urdr_core_rs/` (the independent Rust kernel), `world_host/` (the runtime reference), `voi_gate/` (a float decision gate), `glyph_review.py` | [`tools/README.md`](tools/README.md) |
| [`docs/`](docs/) | Design briefs and session transcripts (narrative, not normative) | [`docs/README.md`](docs/README.md) |
| `urdr.py` | CLI: `run` / `check` / `fmt` a program | — |
| `verify.py` | The gate: unit falsifiers + examples (×2) + oracle + modules + rejections + tamper self-test | — |
| [`LESSONS.md`](LESSONS.md) | The 12 inherited discipline laws, each with where it is enforced | — |

## Use cases

Urðr is a research language and a worked example of a discipline; these are the shapes it fits.

- **Honest capability / claim tracking.** The epistemic type system (`𒀭⟨maturity, evidence⟩` + the
  no-inflation ladder + the ᛞ verify mint) is a reusable pattern for any system where *a claim must
  not outrun its evidence* — audit ledgers, provenance chains, grant/report pipelines.
- **Deterministic, cross-platform numeric kernels.** The Q32.32 substrate (D9) is a fixed-point core
  that reproduces bit-for-bit on every host and placement — the property physics, multiplayer
  simulation, and replay/debug need and that IEEE floats cannot promise across CPUs/GPUs.
- **Verification-first engine architecture.** The atlas/observer theorem + `world_host` demonstrate a
  design where *many renderers share one authoritative, cross-checked state*: multiplayer consensus,
  scientific visualization, spectator/AI views, deterministic replay — the kernel owns authority, the
  renderer owns appearance, and a laundered or forked view is refused, not repaired.
- **A template for reproducible research claims.** Red-first, prototype-first, two-placement,
  honestly-graded — every result here is a small case study in making a verifiable claim about code.
- **Teaching.** A small language whose entire point is that over-claiming does not typecheck.

## Further development

Graded honestly — what is *not* yet done, and what kind of work each is.

- **The one remaining kernel proof:** exact integer `divmod` → fraction-free (Bareiss) rank →
  general-*n* injectivity certificate, lifting the linear-chart theorem past the square/`det` case
  (noted in D5 and D10 §5). This is a genuine proof, gate-able here.
- **Reconstruction / inversion** (solving `Mx = image`): needs rational arithmetic on the fix
  substrate now that `div` exists — a substrate-heavy but honest extension.
- **Perspective / curved charts** (`(x,y,z,w) ↦ (x/z, y/z)`): a chart swap, now possible since `div`
  is both-placements — a renderer feature, adds no new invariant.
- **Continuum-physics transport modules** (e.g. Marangoni surface flow) as deterministic field updates
  `state_{t+1} = Verify(state_t, F(state_t, Δt))` that must *preserve the witness relation* — an
  application of the measured boundary, never a new foundation.
- **World-host Steps 4–5:** a Rust port of the runtime against the same Python fixtures, then the
  large systems surfaces (networking, persistence, replication, renderer/GPU, spatial streaming).
- **More independent placements** of the kernel (other languages) to widen the conformance frontier
  beyond one Rust kernel on one host.
- **Metatheory** (progress/preservation, no-inflation soundness, lens laws) is `CONJECTURED`; the
  falsifier suite is what is `TESTED` (D5 §metatheory).

## Development discipline (dev rules)

The workflow that produced everything above, in order. The full lesson list with enforcement points
is [`LESSONS.md`](LESSONS.md); the normative language rules are [`spec/D1-spec.md`](spec/D1-spec.md) §1–§2.

1. **Red-first.** Write the falsifier before the feature; confirm it dies with the *exact* error code;
   confirm it is **non-vacuous** — a deliberately broken build must fail the harness (L5).
2. **Prototype-first for hard algorithms.** Prove the algorithm in a faithful prototype
   ([`tools/fixpoint_proto/`](tools/fixpoint_proto/)) using only the operations the target actually has,
   *then* encode it. `algorithm proven ≠ measured`.
3. **Grade every claim** on the maturity × evidence ladder; evidence never exceeds maturity; record it
   in [`spec/D5-ledger.md`](spec/D5-ledger.md). No inflation (L2, L6).
4. **Gate twice.** `python verify.py` green, deterministically, in isolated subprocesses (L3).
5. **Cross-placement.** A numeric / observer result earns *both placements* only once `urdr-core-rs`
   reproduces it in the D8 conformance corpus — two kernels agreeing on the accept/reject frontier.
6. **No glyph without a review.** New *operations* arrive as ASCII prelude functions; a glyph is
   *earned* later as a lossless alias via `tools/glyph_review.py` (§20), or never (design law 5).
7. **Determinism is an environment:** `PYTHONHASHSEED=0`, `PYTHONUTF8=1` on redirected output; no
   clock, RNG, float, or iteration-order dependence in the core (L3, L4, L8).
8. **Keep the sayings honest:** `signum ≠ rēs`, `declared ≠ verified`, `digest ≠ MAC`,
   `Grounded ≠ true`, `typeable ≠ renderable`, `cited ≠ implemented`.

## License

AGPL-3.0-only. Copyright (C) 2026 Daniel J. Dillberg.
