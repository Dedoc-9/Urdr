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
- **Prelude.** Fourteen names are pre-bound — ten of v0.1 (below), `weave` (R2, §13),
  and the R4 capability trio `cap` / `recorded` / `plan` (§16) — all pure and
  deterministic *at evaluation time* (even the effect surface: a plan is constructed,
  never performed, during evaluation). The original ten:
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
unpersistable value, tampered or malformed snapshot) · `URDR-CAP` (R4: ungranted or
misused authority — an ungranted capability requested, authority of the wrong kind
used, a malformed/duplicate grant, or an ambiguous effect batch at the līmes) ·
`URDR-PIN` (R5: vendored bytes do not hash to their declared digest — a wrong
pin is refused, not resolved) · `URDR-MODULE` (R5: an unvendored, unpinned, or
malformed module resolution; also a `use` with no vendor root) · `URDR-DELTA-UNEARNED` (§19: `transition_witness` on a zero-delta transition — the state did not move, so no evidence was purchased).

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

### 12b. Lattice falsifier — a user-directed conversion, recorded

The request arrived as *"rhombohedral diagonal consolidation"* — not an established
formalism, so it passed through the honest converter (§2 discipline) with the user's
choice recorded. **Assigned meaning:** over the rhombohedral (FCC-primitive) integer
lattice a₁=(1,1,0), a₂=(0,1,1), a₃=(1,0,1), the C₃ rotation about the body diagonal
cycles coordinates, and the *orbit-average* v + Rv + R²v of ANY vector lands on the
invariant diagonal subspace — group-averaging (the Reynolds operator, in exact ℤ) is
the mathematically true content nearest the phrase. Eleven relations verified by
evaluation and sealed at the mint (`examples/rhombo_lattice.urdr`, ⊢ 11): cyclic
permutation closure, R³ = I, the rhombohedral Gram identity ⟨aᵢ,aⱼ⟩ = 2δᵢⱼ + 1(i≠j),
diagonal invariance, and three consolidation instances. Non-vacuity:
`examples/rejected/rhombo_wrong.urdr` claims R fixes a basis vector and must die
(`URDR-ASSERT`). Crystallography inspires; physics is claimed nowhere (`signum ≠ rēs`).

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

**14b. Compiler as placement — `IMPLEMENTED / MEASURED` (falsified by
`tests/test_oracle.py` and the gate's permanent oracle stage; red-first record in
`docs/transcripts/r3b_green.txt`).** The tree-walking
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
network, filesystem, concurrency, actors, placements, effects, capabilities, modules,
or REPL. Each is either landed on a later rung (§§12–17), `SCOPED` to a rung in D5, or
absent by design law. A feature not listed in this spec does not exist, whatever a name
elsewhere may suggest. (Sections 12–17 record the rungs that have landed since; §15
remains the v0.1 baseline: I/O exists only as R4 capabilities and R5 module reads —
the evaluator itself still performs none.)

## 16. Capabilities (R4) — I/O & external state, nothing ambient

The evaluator gains **no** I/O: no clock, no RNG, no network, no filesystem, at any
time. What R4 adds is a *vocabulary of authority* — three value types and three prelude
names — plus a runner protocol at the līmes. Effects are bracketed outside evaluation:
recorded before it, planned during it, executed after it.

- **Authority is a value, and unforgeable.** A `Capability` (one grant: kind `read` or
  `write`, a name, and for reads a recorded payload) and the `CapSet` that carries the
  grants are minted ONLY by the runner (`urdr/capability.py`) from explicit
  `--grant NAME=read:PATH | NAME=write:PATH` flags. No grammar production constructs
  either; no builtin returns a fresh one; the snapshot codec refuses to carry them
  (`URDR-LIMES`: authority is not data), so a recorded input cannot smuggle in a forged
  grant. Lineage: Milner's LCF `thm` mint (S3), applied to authority; the object-
  capability discipline (Dennis & Van Horn's capabilities; Miller's ocap model) —
  learned, credited, expressed our own way.
- **`caps` is a runner input.** Always bound under `run` (empty when nothing is
  granted — an empty grant set is still nothing-ambient), unshadowable
  (`URDR-REBIND`), and deliberately NOT a store: ☽/☿/ᛃ refuse it (`URDR-TYPE-RUN`) —
  editing a capset would be forging a grant. Its single accessor is `cap(caps, 'name)`,
  and an ungranted name is `URDR-CAP`: refused, not defaulted, not prompted for.
- **Reads are recorded inputs.** A read grant's file is loaded ONCE, by the runner,
  through the one snapshot codec (digest-verified: a tampered fixture is `URDR-LIMES`;
  Grounded/λ/Conflict/authority/plans cannot enter). `recorded(cap)` replays that fixed
  value — bit-identically, every run, on every host. The payload is part of the
  capability's canonical form, so inputs sit inside content identity: same program +
  same inputs ⇒ same digest, still (law 4). Using anything but a read capability is
  `URDR-CAP`.
- **Writes are effect-plans.** `plan(cap, v)` with a write capability constructs an
  `EffectPlan{name, value}` — a write *described*, not performed: pure data with a
  canonical form, comparable and digestable like any value. Evaluation cannot write.
  Using anything but a write capability is `URDR-CAP`.
- **The outbox rule.** Plans reach the līmes as the program's RESULT value — the plan
  itself or plans inside (nested) lists, deterministic left-to-right. Anywhere else an
  EffectPlan is inert data (a plan in a store field is a datum ABOUT a write). Precedent:
  the actor outbox (§13) — intent leaves as an explicit result, never as a side channel.
- **Execution at the līmes, all-or-nothing.** After (and only after) successful
  evaluation the runner validates the whole batch — duplicate target: `URDR-CAP`
  (an ambiguous world edit is refused whole); unpersistable value (Grounded, λ, …):
  `URDR-LIMES` through the same one codec that `--save-store` uses; ungranted target:
  `URDR-CAP` (an armed latch, unreachable while the mint is sound — LESSONS L2 style) —
  and only then writes, printing `effect: NAME DIGEST` per target, sorted. A refused
  batch writes nothing: no partial world edit exists. A failed program executes nothing:
  a dead program edits no world.
- **Failure model, stated.** Any `URDR-*` during evaluation ⇒ zero effects. Any refusal
  during validation ⇒ zero effects. Refusals are deterministic (same code, same span).
- **Boundary (binding).** R4 delivers snapshot-file effects only. Clock, RNG, network,
  and live filesystem walking remain absent by design law; if such an effect kind ever
  arrives, it arrives as a recorded/planned capability through this same mint, or not at
  all. `--save-store` (R2c, runner-owned) remains; write capabilities are the
  program-owned counterpart. ASCII names by the glyph budget (law 5): capability
  notation earns a glyph at a later review or not at all — the `weave` precedent.


## 17. Import-by-digest modules (R5)

The language gains dependencies without gaining a network. A **module** is a `.urdr`
file addressed by the **SHA-256 of its canonical source bytes** (utf-8, BOM tolerated,
universal newlines, NFC — the exact text the lexer consumes). This is byte-level content
addressing: the Unison lesson at the *integrity* level. Its honest limit is stated up
front — `source-hash ≠ definition-hash`: it refuses tampered or substituted *bytes*, not
reformatted or renamed *definitions*. Formatting and comments are content here;
α-normalized *semantic* addressing (format/rename-invariant, true Unison) is the `SCOPED`
strengthening (D5).

- **Surface.** A new statement `use @<64-hex-digest> as name` (ASCII `use`/`as` and an
  `@` digest literal — by the glyph budget, law 5; module notation earns a glyph at a
  later review or not at all). The alias binds the **value** the module evaluates to.
- **Offline resolution.** Rooted at the directory of the program file: a `vendor/`
  store of `<digest>.urdr` files (self-certifying: each file is named by its own hash)
  and a `vendor/urdr.lock` manifest of `NAME <digest>` lines. Resolution is a pure
  local lookup; nothing is fetched (`tests/test_modules.py::test_resolver_imports_no_network`
  asserts the resolver imports no network library — offline is structural, not hopeful).
- **Static pin verification.** For each `use`, at *check* time (no evaluation): the
  vendored file must exist (`URDR-MODULE` else), its bytes must hash to the declared
  digest (`URDR-PIN` else — a wrong pin or tampered file is refused, not resolved), and
  the digest must be pinned in the lockfile (`URDR-MODULE` else). A wrong pin therefore
  dies before the module ever runs.
- **Determinism & identity.** A module is evaluated once, by the ☉ reference (so every
  placement binds the identical value — the mint/kernel stays singular, §14b), with a
  fresh fuel budget, prelude only, and no capabilities or inputs: a pure, deterministic
  constant. The bound value participates in the program's digest, so `same program +
  same vendored modules ⇒ same digest` (law 4 extends across the module boundary).
- **Cycles are unconstructible.** Import-by-content-hash admits no cycle: a module's
  address is the hash of bytes that would have to contain that same address — no hash is
  a fixpoint of a body naming it. Mutual import cannot be built, so it needs no runtime
  guard beyond the resolver's (armed, unreachable).
- **Boundary.** `digest ≠ MAC`: a pin is integrity against accident and substitution of
  bytes, not authentication against an adversary who rewrites the vendor file, the
  lockfile, *and* the program together. Falsifiers: `examples/modules_demo.urdr`
  (`⊢ 42`, a vendored λ library across the boundary), `examples/rejected/module_wrong_pin.urdr`
  (`URDR-PIN`), `examples/rejected/use_unvendored.urdr` (`URDR-MODULE`),
  `tests/test_modules.py`, and the gate's `modules` stage (lockfile ≡ vendor, plus a
  mis-pin self-test that must redden).


## 18. Centering / quotient invariant over ℤ (R5.x) — a user-directed conversion, recorded

Like §12b, this arrived as a request to ground an "esoteric pivot" in mathematics. It
passed through the honest converter with the collaborators' choice recorded — and, unlike
the √2 / oloid material it grew out of (transcendental, and refuted by direct computation:
max curvature was 3π/2 ≈ 4.712, not the claimed √2), it reduces to **exact integer linear
algebra**, so it can be sealed by evaluation rather than merely asserted.

**The algebra that is sealed (it stands on its own).** For x ∈ ℤⁿ the centering operator is
M = nI − J (J the all-ones matrix), acting as (Mx)ᵢ = n·xᵢ − Σx; its scaled companion J
acts as (Jx)ᵢ = Σx. `examples/centering_quotient.urdr` verifies six relations by evaluation
and seals the count at the mint (⊢ 6):

1. scaled orthogonal decomposition  n·x = Mx + Jx;
2. orthogonality  ⟨Mx, Jx⟩ = 0;
3. exact Pythagoras  |Mx|² + |Jx|² = n²·|x|²;
4. the all-ones vector is in the kernel:  M·1 = 0;
5. contrasts are mean-zero:  Σ(Mx) = 0;
6. idempotent up to scale:  M²x = n·Mx.

Every one is an integer identity — no division, no floats. Non-vacuity:
`examples/rejected/centering_wrong.urdr` claims M is a *true* projection over ℤ (M² = M)
and **must die** with `URDR-ASSERT` — over ℤ the operator satisfies M² = nM, so
M(Mx) = n·Mx ≠ Mx. The true projection is P = M/n (P² = P over ℚ); the gate stays in ℤ and
seals the *scaled* facts, so the honest name of the sealed relation is M² = nM, never
P² = P (`signum ≠ rēs` — the certified relation is the integer one, not the rational one it
evokes). Falsifiers: `tests/test_centering.py` (6).

**Interpretation (design provenance only — certified by no test).** The economically
meaningful part of an effort vector is the contrasts Px = Mx/n; the common mode
span{1} = ker M is invisible to a positional reward U (which factors through the quotient
ℝⁿ/span{1}) but not to a cost C computed in the ambient ℝⁿ. The sharpest form of the
discussed *neijuan / 内卷* reading is a **mismatch of symmetries**, Sym(U) ⊋ Sym(C): the
reward is gauge-invariant under x ↦ x + α·1, the cost is not, so equilibrium is driven up
ker M — motion the reward cannot distinguish yet the cost still charges (the deadweight of
"everyone moves, nothing changes"). An observable-fraction invariant L = |Πx| / |x| (Π any
projector onto the observable subspace) measures the share of effort surviving the
quotient. **None of this is asserted by a green test.** The algebraic facts above stand on
their own; this reading is built on top of them, never derived from them, and as an
empirical/social claim it is `SPECULATIVE / N/A`.

**Design influence (lineage, not authority).** The gauge-invariance framing, the
identification of M as the statistician's *centering matrix* (demeaning / within-transform;
the quotient as the space of *contrasts*), and the Sym(U) ⊋ Sym(C) compression arose in
collaborative discussion during R5. Recorded as lineage; `cited ≠ implemented` — the
enforcement is `tests/test_centering.py`, not this paragraph.


## 19. Evidence transitions (the pipeline as a native source of evidence)

A companion discipline to the epistemic ladder, arrived at in collaborative
design: an *action* earns a knowledge claim only by recording a **state
transition** that a verifier can inspect. The pipeline does not ask "is this
good?"; it asks **"what evidence transition did this action purchase?"**. This
extends the core law `claim ≤ evidence` to `claim-transition ≤ measured-delta`,
enforced by the mint that already exists — nothing here mints `Grounded` except
ᛞ (D1 §14b, the singular mint).

**The law.** No new knowledge claim without a recorded state transition. An
observation that leaves the live-hypothesis set unchanged purchased **zero
bits** and cannot be graded. Falsifier: `examples/evidence_transition.urdr`
(⊢ 1 — an observation that at least *halved* a candidate set, i.e. bought ≥ 1
bit, sealed at the mint) and `examples/rejected/evidence_unpurchased.urdr`
(an observation that filters nothing dies `URDR-ASSERT`). The integer criterion
sealed is `2·|kept| ≤ |before|` (≥ 1 bit, uniform-prior reading) — **no floats,
no log**. Shannon bits for arbitrary priors are the *float* `voi_gate` tool's
job (`tools/voi_gate/`): provenance, not a core seal (`signum ≠ rēs`).

**`transition_witness` — the first library function (ASCII, glyph deferred).**
`transition_witness(before, after)` is the **dual of ≟**: where ≟ asserts
*sameness* and returns the value, `transition_witness` asserts a *real
difference* and packages its endpoints as a first-class witness store
`ᚠ{from: ᛝ(before), to: ᛝ(after)}`. Two binding laws, each with a falsifier
(`tests/test_transition.py`):

1. **It never mints `Grounded`.** It returns a witness (a store); ᛞ alone
   adjudicates any claim about that witness. The pipeline *proposes*; the mint
   *decides*.
2. **A zero-delta transition is refused** (`URDR-DELTA-UNEARNED`): if
   `ᛝ(before) = ᛝ(after)` the state did not move, so no evidence was purchased.
   A symbol without a red state is decoration (LESSONS L5);
   `examples/rejected/transition_unearned.urdr` is that red state, and the guard
   was verified to bite (a defect that removes it reddens the gate).

By the glyph budget (design law 5) the function is **ASCII now**. A glyph is the
*final artifact of a proof trail*, not its start: `transition_witness` earns one
only at a later review that shows the name and behaviour have stabilised, that it
cannot be reduced to existing primitives (it cannot — no source can raise
`URDR-DELTA-UNEARNED`, and ≟ has no difference-asserting dual), and that a glyph
would merely compress an already-proven operation rather than invent meaning —
the same review path the provenance operator walked before becoming ᛃ. Until
then the ASCII spelling is the truth and the glyph is a hypothesis.

**The Urðr ↔ pipeline mapping (recorded, not asserted).** `DECLARED` = "this
check *should* reduce uncertainty"; `MEASURED` = a verifier *observed* the
reduction; `Grounded` = ᛞ *accepted* the evidence path; a `Digest` is exact
artifact identity; a capability is permission to create observations; the
membrane preserves the state history; `↩` replays the exact prior state
(*returning is not knowing* — `↩` proves identity, never semantic correctness,
so ancestry-verification is the existing one-line idiom
`≟(ᛝ(↩(☿(A,'k,v))), ᛝ(A))`, not a new primitive). The pipeline is therefore not
a new *metric* bolted onto Urðr; it is a new *source of evidence* adjudicated by
the existing mint.

**R6, expressed this way.** The Rust backend problem becomes an evidence
transition with no benchmark and no trust: `CLAIM: Rust backend preserves
evaluator semantics; OBSERVATION: Rust digest = Python reference digest over
corpus C; VERIFIER: the differential oracle`. Same input + same digest ⇒
admitted equivalence under the stated verifier — exactly what the R3b oracle
already does; §19 only names the pattern the oracle embodies.

**Design influence (lineage, not authority).** The "evidence transition" and
"attempted claim vs. adjudicated grade" framing, and the glyph-as-final-artifact
process, arose in collaborative design. Recorded as lineage; `cited ≠
implemented` — the enforcement is the falsifiers above, not this prose.


## 20. The glyph review (a falsifiable promotion event) — and the first glyph earned

The glyph budget (design law 5) is enforced by a **review**, not a declaration.
A glyph is the *final artifact of a proof trail* — the shortest faithful
spelling of an operation already proven — never its start. The promotion path is
`ASCII function → measured law → falsifier → stable semantics → glyph alias`.
The review can **reject** (`URDR-GLYPH-NOT-EARNED`); a failed review is a
successful gate result, and the ASCII function remains a valid capability either
way. That asymmetry is what keeps the budget honest.

**Five mechanical criteria** (`tools/glyph_review.py`, `tests/test_glyph_review.py`):

1. **Lossless** — `digest(glyph program) = digest(ASCII program)`: the glyph is a
   *spelling*, not new evaluator behaviour. (Falsifier: a non-lossless candidate
   is refused.)
2. **Not confusable** — absent from the `CONFUSABLES` table and not a collision
   with a core glyph. (Falsifier: Greek `Α` is refused.)
3. **Not an excluded rune** (D1 §2.6 hate-appropriation exclusion).
4. **Typeable** — has an ASCII digraph (offline-enterable).
5. **Provenance recorded** — attested meaning kept separate from assigned
   (`signum ≠ rēs`). (Falsifier: missing provenance is refused.)

**First glyph earned: `⟿` for `transition_witness`.** *Freeze*:
`transition_witness/2` shipped and tested (v0.7.0) — the semantics stopped
moving before review (the observation is implicit in `before → after`, not a
third argument). *Non-redundancy*: the operation cannot be composed from existing
primitives — no source raises `URDR-DELTA-UNEARNED` and `≟` has no
difference-asserting dual, so `glyph meaning ≠ old primitives composed`. *Choice
from the operation shape, not metaphor*: the forbidden register (truth, wisdom,
destiny, memory, revelation) was rejected; `⟿` (U+27FF) was chosen for a *traced
passage* between two differing states, distinct from `↦` (clean map) and `↩`
(return).

| Glyph | Cp | Attested (scholarly) | ASCII | Assigned semantics (ours) |
|---|---|---|---|---|
| ⟿ | U+27FF | *Long rightwards squiggle arrow* — mathematical arrow notation | `\tw` | **Transition witness.** A lossless alias of `transition_witness(before, after)`: witnesses a real state passage; refuses zero-delta (`URDR-DELTA-UNEARNED`); **never** mints `Grounded`. The squiggle-arrow's math usage is provenance; the assigned meaning is the witness (`signum ≠ rēs`). |

Lossless proof: `transition_witness`, `⟿`, and `\tw` are three spellings of one
token — one digest (`tests/test_glyph_review.py::test_three_spellings_one_digest`).
Deferred nicety: `fmt` does not yet canonicalize the word/digraph to `⟿`; the
glyph is an accepted input spelling, and canonicalization can follow at leisure.

**Design influence (lineage).** The glyph-review-as-falsifiable-event process
(freeze → non-redundancy → operation-shape choice → lossless alias → review with
a red state) arose in collaborative design; recorded as lineage, `cited ≠
implemented` — the enforcement is `tools/glyph_review.py`, not this prose.
