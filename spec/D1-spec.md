<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D1 — Urðr v0.1 core specification

Status of this document: describes the **v0.1 core** ("the smallest core sufficient to pass
three tests": determinism, one no-inflation rejection, one lens round-trip). Everything in
§1–§9 is `IMPLEMENTED` and exercised by the falsifier suite unless a row or section says
otherwise. Grades for every capability: [`D5-ledger.md`](D5-ledger.md).

---

## 1. Design laws (normative)

1. **No-inflation.** Evidence may never exceed what maturity licenses. In the language this
   is a *static* property: over-claiming source does not typecheck (§5). In the runtime it
   is additionally a latch: the constructor of an over-claiming value raises, though the
   checker makes that path unreachable.
2. **Membrane.** Observing never perturbs. A view is a pure function of a store; an edit
   produces a *new* store. If a view could change a digest, the change crossed the membrane
   and is wrong by definition. There is no such API.
3. **Content addressing.** Every value has exactly one canonical byte form (§7);
   `digest(v) = SHA-256(canon(v))`. Identity is content.
4. **Determinism.** Same program + same inputs ⇒ same result and same digest, on any host.
   The core has no clock, no RNG, no float, no iteration-order dependence, no path or
   environment access. Evaluation is fuel-bounded; fuel exhaustion is a deterministic error.
5. **Glyph budget.** Exotic glyphs are spent only where semantics are novel (epistemics,
   membrane, structure). Arithmetic, grouping and literals stay ASCII. Terseness ≠ clarity;
   every glyph must justify itself against its own ASCII digraph (Green's cognitive
   dimensions are the yardstick).
6. **`signum ≠ rēs`.** A glyph's attested historical meaning (column *attested*) is
   documentation of provenance. Its meaning in Urðr is the *assigned* column and nothing
   else. Resemblance between the two columns is a mnemonic courtesy, never a claim about
   history or by history.

## 2. The core lexicon (21 glyphs)

Every glyph is enterable offline via its ASCII digraph; the lexer accepts glyph and digraph
as the *same token* (one token type, two spellings; `urdr.py fmt` canonicalizes to glyphs).
Fonts are needed only to render, never to run.

### 2.1 Epistemic glyphs

| Glyph | Cp | Source system | Attested (scholarly) | ASCII | Arity/role | Assigned semantics (ours) |
|---|---|---|---|---|---|---|
| 𒀭 | U+1202D | Sumero-Akkadian cuneiform | *dingir/an* — "deity/sky"; as a **determinative**, an unpronounced classifier prefixed to divine names | `\an` | prefix, takes ⟨M,E⟩ tag + expr | **Epistemic annotation.** `𒀭⟨M,E⟩ v` wraps `v` in a Claim graded maturity `M`, evidence `E`. The historical role (silent classifier sign) parallels a type tag; the parallel is our reason for *choosing* it, not an appeal to its meaning. |
| ᛞ | U+16DE | Elder Futhark | *dagaz* — "day, daylight" | `\ve` | 2-ary `ᛞ(verifier, claim)` | **Verify.** Runs `verifier` (a λ) on the claim's value. Truthy ⇒ the unique constructor of `Grounded` (evidence `MEASURED`, witness = digest of verifier AST × value). Falsy ⇒ a ↯ conflict value. Nothing else in the language can mint `MEASURED`. |
| ↯ | U+21AF | Math/arrow notation ("electric arrow"; used for contradiction) | downwards zigzag arrow | `\cf` | value form (also printed) | **Conflict.** The result of a failed verification: carries the claim and the verifier digest. Never silently averaged, never coerced; you must branch on it. |
| ⊢ | U+22A2 | Mathematical logic (Frege 1879) | turnstile, "yields/proves" | `\|-` | output-only | **Witness display.** `Grounded` values render as `w ⊢ v`. Not a constructor: there is no source syntax that builds an entailment — that is the point. |
| ⟨ ⟩ | U+27E8/9 | Mathematical notation | angle brackets | `<\|` `\|>` | tag brackets | Delimit the ⟨maturity, evidence⟩ tag of 𒀭. |

Maturity keywords: `SPECULATIVE < SCOPED < IMPLEMENTED`. Evidence keywords: `NA < DECLARED
< MEASURED` (written `NA`, rendered `N/A`). The **ladder** licensing rule is §5.

### 2.2 Membrane glyphs

| Glyph | Cp | Source system | Attested | ASCII | Arity | Assigned semantics |
|---|---|---|---|---|---|---|
| ᚠ | U+16A0 | Elder Futhark | *fehu* — "cattle; movable wealth" | `\st` | store literal `ᚠ{k: v, …}` | **Store constructor.** An immutable, content-addressed record; the program's "estate". Mnemonic courtesy: a store is heritable wealth. Assigned, not attested. |
| ☽ | U+263D | Astronomical/astrological signs | first-quarter Moon | `\vw` | 2-ary `☽(s, 'k)` | **View (get).** Pure projection of a store field. Reflects; never emits. Cannot mutate by construction (law 2). |
| ☿ | U+263F | Astronomical/astrological signs | Mercury (messenger; alchemical quicksilver) | `\ed` | 3-ary `☿(s, 'k, v)` | **Edit (put).** Returns a *new* store with field `k` set to `v`, parent-linked to `s`. The old digest remains fetchable. |
| ↩ | U+21A9 | Arrow notation | leftwards arrow with hook | `\am` | 1-ary `↩(s)` | **Anamnesis.** Returns the parent state of an edited store — the exact prior value; `ᛝ(↩(☿(s,k,v))) = ᛝ(s)` is a falsifier, not a hope. On a root store: error `URDR-ANAMNESIS-ROOT`. |
| ᛝ | U+16DD | Elder Futhark | *ingwaz* — the god Ing; seed/potential | `\di` | 1-ary `ᛝ(x)` | **Digest.** The SHA-256 content address of a value, as a first-class `Digest` value. The "seed" mnemonic (identity from which the value re-derives) is assigned, not attested. |
| ᛃ | U+16C3 | Elder Futhark | *jēra* — "year; harvest; fruitful cycle" | `\pv` | 1-ary `ᛃ(s)` | **Provenance walk** (R1d). The ancestor digests of a store, nearest first; `[]` at a root. Observability for the lineage that is already part of identity (§8): `ᛃ(s)[k] = ᛝ(↩^(k+1)(s))`. The "seasons a value has lived" mnemonic is assigned, not attested. |

### 2.3 Structural glyphs

| Glyph | Cp | Source | Attested | ASCII | Arity | Assigned semantics |
|---|---|---|---|---|---|---|
| ≔ | U+2254 | Mathematical notation | "is defined as" | `:=` | binder | Top-level bind: `name ≔ expr`. Immutable; rebinding a name is a parse error. |
| λ | U+03BB | Greek alphabet (via Church 1932) | letter lambda | `\fn` | binder | Function abstraction: `λ x ↦ body`, `λ x y ↦ body`. First-class, closes over its environment. |
| ↦ | U+21A6 | Mathematical notation | "maps to" | `\|->` | separator | Separates λ parameters from body. |
| ∘ | U+2218 | Mathematical notation | function composition | `\o` | binary | `f ∘ g` = `λ x ↦ f(g(x))`. |
| ᛚ | U+16DA | Elder Futhark | *laguz* — "water, lake" | `\fl` | binary, left-assoc | **Flow.** `x ᛚ f` = `f(x)`; chains read as a pipeline. Water-flow mnemonic assigned, not attested. |
| Σ | U+03A3 | Greek alphabet (math convention) | capital sigma; summation | `\fo` | 3-ary `Σ(xs, init, λ acc x ↦ …)` | **Fold.** The only iteration construct in v0.1. Left fold over a list. |
| ≟ | U+225F | Mathematical notation | questioned equality | `=?` | 2-ary `≟(a, b)` | **Assertion gate.** If `ᛝ(a) = ᛝ(b)`, evaluates to `b`; else deterministic error `URDR-ASSERT`. The in-language red/green primitive. |
| ≠ | U+2260 | Mathematical notation | not equal | `!=` | binary | Structural inequality (by digest), yielding `1`/`0`. |
| ≤ | U+2264 | Mathematical notation | less-or-equal | `<=` | binary | Integer comparison. |
| ≥ | U+2265 | Mathematical notation | greater-or-equal | `>=` | binary | Integer comparison. |

### 2.4 Common ASCII (part of the alphabet by design law 5)

`+ - *` wrapping 64-bit arithmetic · `= < >` comparison (equality is structural, by digest)
· `?(c, t, f)` conditional (lazy branches) · `( )` grouping · `[ ]` lists · `{ } , :`
store/list punctuation · `'name` symbol literal · `name` identifiers (`[a-z_][a-z0-9_]*`)
· integer literals (ASCII digits, optional `-`) · `#` line comment.

### 2.5 Curated but deferred (in the lexicon, not in the grammar)

| Glyph | Cp | Source | Attested | Planned role | Grade |
|---|---|---|---|---|---|
| 𒁹 | U+12079 | Cuneiform numerals | *diš* — unit wedge | base-60 literal digit | `SCOPED / N/A` (R1+) |
| 𒌋 | U+1230B | Cuneiform numerals | *u* — ten | base-60 literal digit | `SCOPED / N/A` (R1+) |
| ☉ | U+2609 | Astronomical signs | Sun | reference-path marker (the authoritative WHAT against which accelerated WHEREs are differentially checked, §R3) | `SCOPED / N/A` (R3) |

### 2.6 Exclusions (curatorial law, binding)

Excluded outright because their dominant modern reading includes organized
hate-appropriation, regardless of their legitimate historical scholarship: **ᛋ** (*sowilō*),
**ᛟ** (*ōthala*), **ᛉ** (*algiz* in its "life-rune" appropriation), **ᛏ** (*tīwaz* in its
appropriated use). This **overrides the directive's own illustrative suggestion** of ᛟ for
the provenance operator — the directive's curatorial law outranks its example. The
provenance operator's glyph therefore waited for review. **R1d completed that review**
and assigned **ᛃ** (*jēra*): it is not among the hate-appropriated runes catalogued by
extremism monitors, and its shape has no ASCII/Greek lookalike in this alphabet
(confusables check: none). Both facts are recorded here as the review's outcome; if
either changes, the assignment is revisited before the meaning ossifies.

Also excluded from v0.1 for **hygiene** (visual confusability with ASCII/Greek used in
programs): ᚱ (~R), ᛒ (~B), ᚺ (~H), ᛁ (~I/l), ᛖ (~M), ᚹ (~P), ᛏ (~↑/T). A future revision
may admit some with a formatter-enforced display policy; until then they are rejected at
the lexer like any unknown character.

APL/J/BQN/Uiua are studied lineage (glyph economy, digraph input, the formatter idea —
Uiua's formatter directly inspired `urdr.py fmt`); no glyph is taken from them (⍝, ⍳ etc.
deliberately absent). Ideas borrowed and credited; expression our own.

## 3. Grammar (EBNF, v0.1 — complete)

```ebnf
program    = { statement } ;
statement  = bind | expr ;
bind       = IDENT "≔" expr ;

expr       = annot ;
annot      = "𒀭" "⟨" MATURITY "," EVIDENCE "⟩" annot
           | flow ;
flow       = cmp { "ᛚ" cmp } ;                    (* x ᛚ f  ≡  f(x); left-assoc *)
cmp        = add [ ( "=" | "≠" | "<" | "≤" | ">" | "≥" ) add ] ;
add        = mul { ( "+" | "-" ) mul } ;
mul        = compose { "*" compose } ;
compose    = unary { "∘" unary } ;                (* right-assoc *)
unary      = [ "-" ] postfix ;
postfix    = primary { "(" [ expr { "," expr } ] ")" } ;
primary    = INT | SYMBOL | IDENT
           | list | store | lambda | cond
           | verify | view | edit | ana | digestop | fold | assertop | prov
           | "(" expr ")" ;
list       = "[" [ expr { "," expr } ] "]" ;
store      = "ᚠ" "{" [ IDENT ":" expr { "," IDENT ":" expr } ] "}" ;
lambda     = "λ" IDENT { IDENT } "↦" expr ;
cond       = "?" "(" expr "," expr "," expr ")" ;
verify     = "ᛞ" "(" expr "," expr ")" ;
view       = "☽" "(" expr "," expr ")" ;
edit       = "☿" "(" expr "," expr "," expr ")" ;
ana        = "↩" "(" expr ")" ;
digestop   = "ᛝ" "(" expr ")" ;
fold       = "Σ" "(" expr "," expr "," expr ")" ;
assertop   = "≟" "(" expr "," expr ")" ;
prov       = "ᛃ" "(" expr ")" ;                   (* R1d *)

MATURITY   = "SPECULATIVE" | "SCOPED" | "IMPLEMENTED" ;
EVIDENCE   = "NA" | "DECLARED" | "MEASURED" ;      (* MEASURED never typechecks in source *)
SYMBOL     = "'" IDENT ;
IDENT      = lowercase ASCII: [a-z_][a-z0-9_]* , excluding keywords ;
INT        = [ "-" ] [0-9]+  (interpreted in i64, wrap semantics) ;
comment    = "#" … end of line ;
```

Every glyph terminal above equally accepts its ASCII digraph (§2). The program's value is
the value of its last statement.

## 4. Lexical hygiene (normative, lexer-enforced)

1. **Normalization.** Source is decoded as UTF-8 (BOM tolerated and stripped) and
   NFC-normalized before tokenization.
2. **Closed alphabet.** A codepoint is legal only if it is (a) a core glyph, (b) printable
   ASCII, or (c) whitespace (space, tab, LF, CR). Anything else ⇒ `URDR-LEX-UNKNOWN`
   naming the codepoint. There is no "unknown but ignored" character.
3. **Confusables.** A curated table maps known lookalikes (Greek Α/Β/Ε/Η/Ι/Κ/Μ/Ν/Ο/Ρ/Τ/Χ,
   Cyrillic а/е/о/р/с/х, fullwidth forms, the hygiene-excluded runes of §2.6, NBSP and
   zero-width characters) to a diagnostic: `URDR-LEX-CONFUSABLE`, which names the intruder
   *and* the ASCII/glyph it imitates. One glyph, one meaning; a token that merely *looks*
   right is rejected, not guessed at.
4. **Max-munch digraphs.** `|->` before `|-`; `<=`/`>=`/`!=`/`=?`/`:=` before their
   prefixes; `<|`/`|>` are tag brackets (unambiguous in v0.1: no unary `|`).

## 5. The epistemic type discipline (static)

Values of interest: `Claim{value, maturity, evidence}`, `Grounded{value, witness}` (a Claim
whose evidence is `MEASURED` by construction), `Conflict{claim, verifier_digest}` (↯).

**The ladder.** Maturity licenses a *ceiling* on evidence:

| maturity | licensed evidence |
|---|---|
| `SPECULATIVE` | `NA` only |
| `SCOPED` | `NA`, `DECLARED` |
| `IMPLEMENTED` | `NA`, `DECLARED`, `MEASURED` |

**Static rules (the checker, `urdr check`):**

- **S1 (no inflation).** An annotation `𒀭⟨M,E⟩ e` with `E` above the ceiling of `M` is
  rejected: `URDR-INFLATE-STATIC`. *(Falsifier: `examples/rejected/inflate_static.urdr`.)*
- **S2 (evidence is earned, not written).** Source may never write `MEASURED` in an
  annotation — even under `IMPLEMENTED`, whose ceiling admits it — because written evidence
  is at most a declaration. Rejected: `URDR-EVIDENCE-UNEARNED`. `MEASURED` enters a program
  through exactly one door: ᛞ at run time. *(Falsifier: `examples/rejected/evidence_unearned.urdr`.)*
- **S3 (Grounded is unforgeable).** No literal, constructor, or operator builds `Grounded`
  except the evaluation of ᛞ. This is syntactic (no such production exists) plus S2 (you
  cannot fake it with a tag). Lineage: Milner's LCF `thm` — the sound kernel is the only
  mint. *(Non-vacuity: the grounding example must produce a Grounded via ᛞ and the suite
  must fail if an alternative mint appears.)*
- **S4 (verify shape).** `ᛞ(v, c)`: `v` must be syntactically a λ (or a name bound to one
  at the top level); `c` any expression. Deeper typing of `v` is dynamic in v0.1
  (`URDR-TYPE-RUN` on misuse) — graded honestly in D5.
- **D1 (verify is licensed, dynamically).** ᛞ mints `MEASURED`; the ladder therefore
  applies *at the mint*: the claim's maturity must be `IMPLEMENTED`. Verifying a
  `SPECULATIVE` or `SCOPED` claim is a deterministic run-time rejection,
  `URDR-VERIFY-UNLICENSED` — measuring what is not built is a category error, and quietly
  downgrading the resulting evidence would be a silent average, which ↯ exists to forbid.
  *(Falsifier: `examples/rejected/verify_unlicensed.urdr`.)*

**Dynamic latch (defense in depth).** The `Claim` constructor re-checks the ladder and
raises `URDR-INFLATE-DYN` if violated. Unreachable if the checker is sound; armed anyway
(LESSONS L2). A verifier returning falsy yields ↯, carrying the claim and the verifier
digest — disagreement is *marked*, never averaged (there is no operation that merges a
Conflict with anything).

**What ᛞ certifies (bound, stated).** `Grounded{v, w}` asserts precisely: *the named
verifier, itself digested into the witness `w`, evaluated truthy on `v` under this
interpreter's deterministic semantics within fuel*. It does not assert the verifier is
meaningful, sufficient, or correctly named. `Grounded ≠ true`; it is `MEASURED ≠ N/A`.

## 6. Evaluation model

- **Order.** Strict left-to-right, call-by-value; `?(c,t,f)` evaluates only the taken
  branch; λ bodies evaluate at application.
- **Integers.** Two's-complement i64 with defined wrap on `+ - *` (Python impl wraps
  explicitly at every operation). Division is absent from v0.1 (no `/`, no `%`): the first
  operation whose "defined semantics" would need a divide-by-zero convention is deferred to
  R1 rather than half-specified.
- **Truth.** `0` is false; any other integer is true. Comparisons yield `1`/`0`.
  Non-integer condition ⇒ `URDR-TYPE-RUN`.
- **Equality `=` / assertion ≟.** Structural, defined as digest equality — one equality,
  the content-addressed one, everywhere.
- **Environment.** Top-level binds are immutable and lexically scoped; λ closes over its
  definition environment. No shadowing of keywords; rebinding ⇒ `URDR-REBIND`.
- **Fuel.** Every evaluation step costs 1 from a budget of 1,000,000 (CLI-overridable,
  recorded in the run header). Exhaustion ⇒ `URDR-FUEL`, deterministically, at the same
  step on every host. Totality is thereby *not* claimed (README §boundaries).
- **Errors are values of the run, not of the machine.** Every `URDR-*` error carries a
  stable code and source span; the gate matches on codes, not message prose.
- **Prelude.** Exactly ten names are pre-bound, all pure and deterministic:
  `value(c)` (unwrap a Claim/Grounded), `maturity(c)` / `evidence(c)` (→ symbol),
  `grounded(x)` / `conflicted(x)` (→ `1`/`0`), `range(n)` (→ `[0 … n−1]`, fuel-bounded),
  `len(xs)`, and (R1b) `push(xs, x)` / `cat(xs, ys)` / `nth(xs, i)` — list append,
  concatenation, and read, each charging fuel for the copy it performs and failing
  typed (`URDR-TYPE-RUN`, including `nth` bounds). Prelude names are ordinary bindings
  (shadowable is a parse error like any rebind); they are part of the language surface
  and of D4's typeability table.

## 7. Canonical form & digests

`canon(v)` is a type-tagged, length-prefixed byte string; `ᛝ(v) = SHA-256(canon(v))`.

| Value | Encoding |
|---|---|
| Int n | `i` + 8-byte big-endian two's complement |
| Symbol s | `y` + varint len + UTF-8 bytes |
| List xs | `l` + varint count + canon of each element |
| Store | `s` + varint count + (for each field, sorted by symbol bytes: canon(key) + canon(value)) + parent digest (32 bytes, or 32 zero bytes for a root) |
| Claim | `c` + maturity byte + evidence byte + canon(value) |
| Grounded | `g` + canon(value) + witness digest (32 bytes) |
| Conflict | `x` + canon(claim) + verifier digest (32 bytes) |
| Lambda | `f` + canonical AST bytes (structural serialization of params + body, source spans excluded) |
| Digest | `d` + 32 raw bytes |

Notes. Store field order in *source* is irrelevant: canonical form sorts; digests never
see Python iteration order. λ canonical form is **α-normalized** (R1a): λ-bound names
serialize as positional (De Bruijn) indices *in canon only*, so α-equivalent lambdas are
one value with one digest; free/captured names stay named because what a closure captures
is identity, not spelling. `digest ≠ MAC`: SHA-256 here provides content identity against
accident and drift, not authentication against an adversary who can rewrite the files
*and* the digests.

## 8. The membrane, precisely

A `Store` is immutable. `☿(s, 'k, v)` returns `s′` with field `k` = `v` and
`parent(s′) = s` (held by reference; the parent digest participates in `canon(s′)`, so
lineage is part of identity). `☽` reads; it is a pure function; there is no variant of ☽
with a side effect, and no aliasing path by which a view handle can reach a mutation —
this is law 2 *by construction*, not by review.

**Lens laws (falsifiers, run by the gate):**

- get-put: `☿(s, 'k, ☽(s, 'k))` has the digest of `s`… **No.** It has a *new* parent link —
  stated honestly: in Urðr the get-put law holds *up to lineage*: the **content fields** of
  `☿(s,'k,☽(s,'k))` equal those of `s`, and `↩` of it returns exactly `s`. The falsifier
  asserts both: field-equality via views, and `ᛝ(↩(☿(s,'k,☽(s,'k)))) = ᛝ(s)`. (A design
  that silently dropped the parent link would satisfy textbook get-put and destroy audit
  lineage; we choose lineage and state the deviation. `textbook ≠ this system`.)
- put-get: `☽(☿(s, 'k, v), 'k) = v`, exactly.
- anamnesis: `↩(☿(s, 'k, v))` is *the* prior state: digest-identical to `s`.

v0.1 scope note: `↩` reaches the in-memory parent chain of the current run. A persisted
store surviving across runs (true epochal time travel on disk) is `SCOPED` (R2+).

## 9. Error codes (stable API, tested by code not prose)

`URDR-LEX-UNKNOWN` · `URDR-LEX-CONFUSABLE` · `URDR-PARSE` · `URDR-REBIND` ·
`URDR-INFLATE-STATIC` · `URDR-EVIDENCE-UNEARNED` · `URDR-VERIFY-UNLICENSED` ·
`URDR-NAME` · `URDR-TYPE-RUN` · `URDR-ASSERT` · `URDR-FUEL` · `URDR-ANAMNESIS-ROOT` ·
`URDR-INFLATE-DYN` (latch; reachable only if the checker is unsound — its firing in the
suite is itself a red) · `URDR-LIMES` (R2c: fail-closed process-boundary refusal —
unpersistable value, tampered or malformed snapshot).

## 10. Metatheory obligations (declared now, discharged by grade)

| Theorem | Statement | Grade |
|---|---|---|
| No-inflation soundness | No well-typed program constructs a Claim whose evidence exceeds its maturity ceiling, nor any `MEASURED` evidence except via ᛞ | `TESTED` (falsifiers S1/S2/S3); `CONJECTURED` as a theorem |
| Determinism | Same program + inputs ⇒ same digest, any host | `TESTED` (gate, two isolated runs + recorded goldens); `CONJECTURED` as a theorem |
| Lens laws | put-get exact; get-put up to lineage with exact `↩` recovery (§8) | `TESTED`; `CONJECTURED` as theorems |
| Reversibility | `↩` after ☿ returns the digest-identical prior store | `TESTED` |
| Progress & preservation | For the v0.1 dynamic typing discipline | `CONJECTURED` (no formal type soundness claimed in v0.1) |
| Schedule invariance | Placements do not change digests | `SPECULATIVE / N/A` — no placements exist yet (R3) |
| TLA+ membrane/reversal model | Exhaustive small-state check of §8 laws | `SCOPED / N/A` (R2) |

## 11. Cost model (v0.1, honest)

Evaluation is a tree walk: each AST node visit costs O(1) fuel; `☿` copies the field map —
O(n) in field count (persistent structural sharing is `SCOPED`); `canon`/`ᛝ` are O(size of
value) and **not cached** (memoization `SCOPED`); `Σ` is O(len · body). No performance
number is published for the interpreter, and none will be except as *measured on a named
host* (`benchmark ≠ universal`).

## 12. Graded-algebra notation (R1c) — the honest "M-capable" conversion

The directive's "M-theory capable" converts to a *testable* capability (D1 §1 of the
directive; README §conversions): represent a ℤ₂-graded / Clifford structure as a value
and verify its defining relations **by evaluation**. Urðr's notation is textual and
original; the *method* — a notation that carries grading and closure mechanically — is
learned from **S. J. Gates Jr. & Michael Faux's adinkras**, credited here, with none of
their graphs, glyphs, or notation reproduced (`learned ≠ copied`).

- A **basis blade** of Cl(n) is its 0/1 characteristic vector `[b0 … b(n-1)]` (a plain
  list value). The scalar is the zero vector.
- A **signed element** is `[sign, blade]` with `sign ∈ {1, −1}` — integers only; the
  metric is e_i² = +1, so no rationals arise.
- **Product law:** `e_A · e_B = (−1)^crossings(A,B) · e_(A Δ B)`, where Δ is elementwise
  XOR (symmetric difference) and `crossings(A,B) = Σ_i A[i] · (Σ_{j<i} B[j])` — the
  anticommutation sign as an inversion count. All computed in-language with `Σ`, `nth`,
  and wrap arithmetic.
- **ℤ₂ grade** = bit-parity of the blade; closure law `grade(aΔb) = grade(a) ⊕ grade(b)`.

Falsifiers (all run by the gate): `examples/z2_grading.urdr` checks the grading law over
all 64 blade pairs of Cl(3) and seals the count with ᛞ (a Grounded `⊢ 64`);
`examples/clifford_relations.urdr` checks `{e_i, e_j} = 2δ_ij` for all nine pairs plus
direct anticommutation and square spot-checks, sealed `⊢ 9`;
`examples/rejected/clifford_wrong.urdr` claims commutation and **must die** with
`URDR-ASSERT` (`≟ breach: 1 ≠ -1`) — the non-vacuity of the whole rung. Boundary
restated: these verify *algebra relations under this evaluator*. They say nothing about
physics, supersymmetry, or the universe (`sign ≠ thing`).

## 13. Deterministic actors (R2) — active truth without inherited nondeterminism

- An **actor** is an ordinary store with fields `state` (any value) and `handler`
  (a λ `st msg ↦ [st′, outbox]`; outbox = list of `[target, payload]`).
- A **world** is a list of actors; an actor's id is its index.
- **`weave(world, inbox, ticks)`** — prelude builtin, ASCII name on purpose: the glyph
  budget (design law 5) spends exotic glyphs only on settled semantics. Actor notation
  earns a glyph at the R3 review or not at all.
- **Canonical order law.** Each tick processes all pending messages in the order
  `sort by (target, ᛝ(payload))` — a *pure function of the message multiset*. No
  sequence number encoding arrival exists anywhere in the semantics. (The directive's
  illustrative key `(tick, actor_id, seq)` reaches the same goal; the digest tiebreaker
  is chosen because a `seq` still encodes arrival, and independence should hold by
  construction, not by discipline. Two equal payloads to one target are literally
  indistinguishable, so their relative order cannot matter.)
- Deliveries left-fold the target's handler; outboxes join the **next** tick's pending.
  Result value: `[final_states, leftover_messages]` — both inside the digest.
- **Local cage.** Handlers evaluate under the unchanged rules: ᛞ stays the only mint,
  the latch stays armed. An actor that tries to raise evidence above maturity dies
  *inside its own handler* — no-inflation enforced by the entity, not by a central
  checker after the fact (Hewitt's agency, Milner's kernel, one cage).
- **Quarantine note.** v0.3 contains no nondeterministic delivery to quarantine — no
  effect syntax exists yet. The falsifier is therefore *schedule permutation*: every
  permutation of the inbox must yield one digest
  (`examples/actors_one_digest.urdr`, `tests/test_actors.py`), and the over-claiming
  actor must die (`examples/rejected/actor_overclaim.urdr`).

### 13b. Runner snapshots (R2c) — persistence as a līmes

The language gains no I/O. Persistence lives at the **process boundary**, owned by the
CLI: `urdr.py run FILE --save-store PATH` writes the result value (with its full lineage
chain and its digest) to a snapshot; `--load-store PATH` re-derives the value, verifies
the recorded digest (mismatch ⇒ `URDR-LIMES`, refused not repaired), and binds it as the
runner-provided input `loaded` — which a program may not shadow (`URDR-REBIND`). Data
crosses; **behavior and verdicts do not**: λ, compositions, builtins, Conflict, and above
all `Grounded` are refused (`URDR-LIMES`) — a witness certifies a verification in *this*
process under *this* evaluator, so `MEASURED` is re-earned after load, never imported.
Falsifier: three interpreters, one address (`tests/test_snapshot.py`). Capability-gated
in-language persistence remains R4.

## 14. The verbose profile (R3a) and the compiler oracle (R3b)

**14a. Verbose profile — `IMPLEMENTED / MEASURED`.** Twelve reserved words are a *third
spelling* of existing token kinds: `annot verify view edit recall digest store flow fn
fold expect after lineage`. One token stream, one digest, three spellings — falsified by
`tests/test_verbose.py`; `fmt` canonicalizes words → glyphs. Reserved words cannot be
identifiers (rejected at parse). A profile is spelling, never semantics.

**14b. Compiler as placement — `SCOPED / N/A`, design fixed now.** The tree-walking
interpreter is the ☉ **reference**. A closure/bytecode compiler is a *placement* (WHERE),
admitted per run **only** by differential oracle: bit-identical digests against ☉ on the
full example corpus, or the fast path is rejected — never averaged, never trusted.
Design laws already fixed:
1. **The mint is singular.** `ᛞ`'s verification semantics and the builtin kernel
   (including `weave`) are extracted into one shared kernel used by *both* executors.
   Two mints would be an attack surface, not a check; the oracle's job is to compare
   *evaluation strategies*, not to fork evidence semantics.
2. **Non-vacuity fixture.** The runner ships a deliberately defective path
   (`--via defect`, e.g. `+` off by one) that the gate REQUIRES to disagree with ☉ on
   at least one example. An oracle that cannot redden proves nothing (LESSONS L5).
3. Values, canon, and fuel are shared; only the execution strategy differs. λ bodies
   compile at first call and cache; `V.Lambda` and its canon are untouched.

## 15. Does-not-do (v0.1)

No physics (see README). No strings, floats, division, recursion, I/O, clock, RNG,
network, filesystem, concurrency, actors, placements, effects, capabilities, module
system, or REPL. Each is either `SCOPED` to a rung in D5 or absent by design law. A
feature not listed in this spec does not exist, whatever a name elsewhere may suggest.
