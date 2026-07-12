<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D13 — The glyph probe: a first-principles review of every primitive candidate

Status: **REVIEW RECORD** (verdicts are graded judgments under the D1 §20 law, not
measurements; nothing here is `MEASURED` and nothing here adds syntax). This document
applies the D6 gap-hunt method to the whole engine and to the recurring foundations of
adjacent fields, asking one question per concept: *does this deserve to be a primitive
glyph, or is it a library?* The null hypothesis, always: **library**. The kernel stays
sealed unless a candidate survives every test below and is then earned through a full
§20 review with cross-placed evidence. Convenience is not evidence. Brevity is not
expressive power.

## 0. The five tests (a candidate must pass ALL to reach a §20 review)

1. **New semantic law.** The concept cannot be faithfully expressed as a composition
   of existing primitives — not "verbose to express", *impossible or unsound* to
   express.
2. **Verifier change.** Certifying correctness would require the checker/evaluator to
   understand something it currently has no judgment for.
3. **New class** of typed refusal, witness, capability, or authority transition — a
   *class*, not a new instance of an existing class.
4. **Cross-placement necessity.** Independent implementations must agree on the
   concept's law for reproducibility to survive — it cannot remain a private detail
   of one placement.
5. **Earned evidence.** A real consumer is under measurable pressure today, and the
   dynamic/library version has been built, gated, and found *insufficient in kind*
   (not merely in ergonomics).

Test 5 is the seal's teeth: this week the engine gained rollback, authenticated
inputs, authored worlds, and their full composition (N2–N5) — **and none of them
required a language change**. Every one entered as a consumer of existing law. That
is the strongest empirical evidence available that the primitive set is adequate so
far, and every verdict below is read against it.

## 1. Verdict summary

| # | Candidate | Fields where it recurs | Verdict |
|---|---|---|---|
| C1 | Witness chain / transcript fold | Merkle trees, git, event sourcing, TLA+ behaviors, blockchains | **standard library** (exists: `trace_digest`; frozen in D12) |
| C2 | Reified / catchable refusal | exceptions (ML, Java), conditions (Lisp), `Result` (Rust) | **reject** — un-catchability is load-bearing |
| C3 | Snapshot / rewind (time travel) | DB transactions, STM, OS checkpointing, delimited continuations | **domain library** (exists: N2/N5; convergence is a theorem, not a law) |
| C4 | Linear / one-time resources | linear logic (Girard), Rust ownership, session types, quantum no-cloning | **defer — the one live candidate** (§3; pre-registered triggers) |
| C5 | Temporal trace assertions (always/eventually) | LTL, TLA+, runtime verification | **standard library** (fold a predicate over the transcript; the gate already is this) |
| C6 | Lattice-join merge (CRDTs) | CRDTs (Shapiro et al.), Dynamo-style reconciliation | **reject** — the R2 weave's canonical form is strictly stronger |
| C7 | Signature verification / authenticated identity | PKI, TLS, signed commits | **domain library** (exists: N3; ᛞ's named-verifier law already covers "verify mints trust") |
| C8 | Region / frame-scoped authority | separation logic (frame rule), sharding, OS address spaces | **reject as premature** — Phase-3 contract must exist first (§4) |
| C9 | Error-bounded numerics (intervals) | validated numerics, interval arithmetic | **reject** — frozen rounding gives bit-identity, which is the property the engine actually needs |
| C10 | Algebraic effects & handlers | Plotkin–Pretnar, Koka, OCaml 5 | **reject** — user-interceptable effects would launder the līmes |
| C11 | Bidirectional views / lenses | Foster–Pierce lenses, DB view-update | **already present** (lens laws are R1 falsifiers; atlases are D7/D10) |
| C12 | Durable commitment (WAL / ACID durability) | databases, filesystems | **reject as glyph** — durability is a host property the evaluator cannot certify; effect-plan annotation at most |
| C13 | Randomness (deterministic beacons) | VRFs, commit-reveal, game RNG | **standard library recipe** — a seed is a recorded input (R4 law already covers it) |
| C14 | Quotient / canonical-form types | quotient types (provers), hash-consing | **already primitive** — `canon → digest` IS the kernel's quotient law; new canonicalizers are libraries feeding it |
| C15 | Ambient time / tick as primitive | real-time systems, OS clocks | **reject** — clocks are banned from authority; a tick index is data |
| C16 | Dependent / refinement types | Martin-Löf, Coq/Lean, Liquid Haskell | **reject** — the witness discipline (check the certificate, don't trust the prover) is the engine's answer, and it cross-places at a fraction of the checker size |

Zero admissions. One deferral with teeth (C4). The seal holds.

## 2. The investigations

Each candidate: where it applies · expressible today? · law or syntax? · what it
would cost (corpus, refusals) · what it would enable · verdict.

### C1 — Witness chain / transcript as a first-class value
Applies: netcode, replay, persistence, audit. **Expressible today:** yes —
`SHA-256(magic | ordered digests)` is a two-line fold over existing primitives;
`URDRLSTT`/`URDRFPT1` are frozen instances. A glyph would shorten syntax only; the
verifier already understands hashing and ordering. The interesting adjacent law —
"no intermediate divergence silently persists" — is a *theorem about deterministic
replay* (T14), proven by the gate, not a primitive. **Cost if primitivized:** a new
corpus duplicating what four netcode corpora already pin. **Verdict: standard
library**, already frozen. No glyph.

### C2 — Refusal as a catchable value
Applies: everywhere, seductively. Every mainstream language reifies errors so
programs can recover. Urðr's refusals are *terminal and typed* — and that absence of
a handler is a semantic law, not a gap: a program that could catch `URDR-ASSERT` or
`URDR-EVIDENCE-UNEARNED` and continue could convert a failed verification into
control flow, which is inflation with extra steps. The engine's refusal classes
(`PHYS-REFUSE`, `AUTH-REFUSE`, `WORLD-REFUSE`, `ROLLBACK-*`) all inherit their force
from being un-launderable. **What a handler glyph would enable:** exactly the
constructions the type system exists to make impossible. **Verdict: reject.** The
missing feature is the feature.

### C3 — Snapshot / rewind as a language primitive
Applies: netcode (N2/N5), editors (undo), speculative AI search. Cross-domain this
recurs as transactions, STM retry, continuations. **Expressible today:** proven —
N2 built rewind entirely as a consumer: copy pure state, truncate the transcript,
replay the same deterministic tick. Convergence-to-canonical is *earned by
determinism*, not granted by a primitive; a `rewind` glyph would add no law the
verifier doesn't already certify (purity + replay). Where languages make this
primitive (STM, continuations), it is because their state is ambient and mutable —
Urðr's is neither. **Verdict: domain library**, frozen at `urdr-netcode-rollback
0.1`. No glyph.

### C4 — Linear / one-time resources (THE live candidate)
Applies: N3's Lamport keys (signing twice leaks preimages), single-shot effect
plans, capability hand-off to untrusted code (Phase 4), session endpoints.
Prior art is deep and convergent: linear logic, Rust's affine ownership, session
types, cryptographic one-time primitives, quantum no-cloning — the same
"use-exactly-once" law surfaces as an irreducible foundation in five unrelated
fields. **Expressible today?** Dynamically, yes — N3/N5 enforce the one-time rule
at admission via the identity law, and it is gated. Statically, **no**: nothing in
the current type discipline can refuse a program *before evaluation* for using a
value twice. That is a genuine expressive-power gap, and it passes tests 1–4:
usage-multiplicity is a new judgment form (new law); the checker would need to
count uses through evaluation (verifier change); it introduces a static refusal
class (`URDR-LINEAR`, distinct from every dynamic refusal); and placements would
have to agree on the counting law (cross-placement necessity). **What it would
enable:** capabilities that provably cannot be duplicated by user scripts; keys
whose reuse is a compile-time refusal; effect plans that cannot be replayed.
**Why it is NOT admitted today:** test 5 fails. The only consumer under real
pressure (OTS reuse) is solved, gated, and cross-placed dynamically; the static
version currently buys assurance-in-kind for a hazard that has no open instance.
**Verdict: defer, with pre-registered triggers** — see §3. This is the only
candidate in the probe whose eventual admission would be unsurprising.

### C5 — Temporal assertions over traces (□/◇, "always/eventually")
Applies: physics invariants (mass conserved every tick), netcode (eventually
converges), gate stages. **Expressible today:** a fold of a predicate over the
transcript — the gate's conservation stages *are* hand-rolled LTL-□. A glyph would
be syntax; the verifier learns nothing new (predicates and folds exist). LTL earns
primitive status in model checkers because they *search*; Urðr replays one
deterministic behavior, where □ degenerates to "check every frame". **Verdict:
standard library** — a `trace_invariant` combinator in `tools/` if a third consumer
wants it; not before (YAGNI).

### C6 — Lattice-join merge (CRDT convergence)
Applies: multiplayer state sync, offline edits. CRDTs converge by *algebraic trust*:
the type is correct only if join is commutative/associative/idempotent, which the
runtime cannot check. Urðr already holds the stronger card: R2's weave converges by
**canonical form** — sort into one order, apply deterministically — making
convergence a *theorem of the gate* rather than a property the implementor promises.
N1's `(peer, seq)` merge is the netcode instance. Admitting join-as-primitive would
import the weaker discipline alongside the stronger one. **Verdict: reject.**
Specific CRDTs, if ever wanted, are libraries whose merge must *reduce to* a
canonical-form weave to be admitted.

### C7 — Authenticated identity / signature verification
Applies: netcode (done), persistence, distribution. The instructive fact: N3 built
an actual signature scheme — keygen, commitment, sign, verify — from **zero new
primitives**, because the kernel's only crypto assumption (SHA-256 as the digest
law) is already sufficient, and ᛞ's law ("trust is minted only by a named verifier")
already describes what `verify` does. A signature glyph would freeze one scheme into
the language; the library lets Ed25519 arrive later as another named verifier with
its own corpus. **Verdict: domain library**, frozen at `urdr-netcode-auth 0.1`.

### C8 — Region-scoped authority (the frame rule)
Applies: Phase-3 world scale. Separation logic's frame rule — *reason locally,
conclude globally* — is the deepest prior art here, and the engine already holds a
measured seed: the regional-locality result (T16, local verdict ≡ global verdict).
The Phase-3 question is whether "regional witnesses compose to the global witness"
needs a new witness *class* (composite/frame witnesses) with its own algebra. It
might — and if it does, it will pass tests 1–4. But the standing Phase-3 rule
applies with full force: **the contract must be statable and falsifiable before any
implementation, let alone a primitive.** A glyph admitted before the contract would
be syntax in search of a law. **Verdict: reject as premature**; re-open only after
the D-series regional-authority contract exists and its library realization has been
measured against it.

### C9 — Error-bounded numerics (interval arithmetic)
Applies: physics regime B. Intervals answer "how wrong can the rounded value be?" —
a scientific question. The engine's question is "is the rounded value *identical
everywhere*?" — answered by the frozen rounding law, bit-for-bit, cross-placed.
Bounds tracking would double regime-B cost to serve a consumer that does not exist.
**Verdict: reject**; if a verified-numerics consumer ever arrives, intervals are a
library over exact ℚ endpoints (regime E), no new primitive required.

### C10 — Algebraic effects and handlers
Applies: scripting (Phase 4), I/O. Handlers let user code intercept and reinterpret
effects — precisely the power the līmes exists to withhold. Urðr's effect story is
deliberately *less* expressive: reads are recorded inputs, writes are effect-plans
executed after success, and no program observes or redirects its own effects. A
handler glyph would reintroduce ambient effect authority through the front door.
**Verdict: reject.** Phase-4 scripting gets capabilities, not handlers.

### C11 — Bidirectional views (lenses)
Already present: lens laws (get-put, put-get) are R1 falsifiers; charts/atlases
(D7, D10) are the engine-scale generalization with injectivity as a *computed
certificate*. Nothing to add. **Verdict: already present** — new optics variants
(prisms, traversals) are libraries, admitted only with law-falsifiers per R1
precedent.

### C12 — Durable commitment (ACID durability)
Applies: persistence, saves. Durability is a claim about hardware surviving events
the evaluator cannot observe. The gate's epistemology — *a green gate certifies
these tests on this code* — cannot certify a disk; a `durable` glyph would mint a
claim no verifier backs, violating no-inflation at the specification level.
**Verdict: reject as glyph.** The honest shape: an effect-plan *annotation* whose
runner-side fsync discipline is graded operationally (like CI hosts), never
language-level truth.

### C13 — Randomness
Applies: gameplay, procedural generation. Every deterministic-replay system
rediscovers the same answer: randomness is an *input*. A seed is a recorded input
(R4 law, unchanged); a fairness-critical seed is a signed recorded input (N3,
unchanged); a multi-party seed is commit-reveal over existing hashing (unchanged).
**Verdict: standard library recipe** — document the pattern; zero new law.

### C14 — Quotient / canonical-form types
The probe's mirror: this one is *already the kernel's deepest primitive*. `canon →
SHA-256` is a quotient construction — identity up to the canonicalizer — and it is
why weave (C6), dedup (N1), and content addressing all come out as theorems.
New equivalences (canonical vertex orderings, normalized worlds) are new
canonicalizers: libraries that feed the existing law. **Verdict: already
primitive**; extensions are libraries.

### C15 — Time as a primitive
Rejected on sight by D7: a clock in the authority path destroys replay. Tick
indices are ordinary data; wall time, where ever needed, is a recorded input at the
līmes. **Verdict: reject.**

### C16 — Dependent / refinement types
The heavyweight. Refinements would let `λ : {q // q ≥ 0}` be *typed* rather than
*witnessed*. But the engine's architecture already made the opposite bet, and the
bet is measured: solvers **propose**, certificates are **checked** (LCP
complementarity, J·v = 0, rank uniqueness), and the checker is small enough that it
has been cross-placed in three languages. A dependent checker is a large trusted
kernel; under the two-placement rule it would have to be independently reimplemented
bit-for-bit — a cost no current consumer justifies, for a guarantee the witness
discipline already delivers at runtime with cross-placed evidence. **Verdict:
reject.** `checking a certificate ≠ trusting a prover — and the engine only ever
needs the former.`

## 3. The C4 deferral — pre-registered triggers and falsifiers

Linearity is deferred, not dismissed. To prevent relitigating from scratch, the
§20 review re-opens **iff** one of these becomes true, and its red-first falsifiers
are fixed now:

- **Trigger A (Phase 4):** user scripts receive capabilities or one-time
  credentials, and the dynamic identity law is shown insufficient — i.e., a gated
  falsifier demonstrates a duplication/laundering construction the admission layer
  cannot refuse without static usage tracking.
- **Trigger B:** a second, unrelated consumer (beyond OTS keys) independently
  requires use-exactly-once semantics, and its dynamic enforcement measurably
  distorts its design (not merely its ergonomics).

Pre-registered falsifiers for the eventual review: a linear value used twice is
refused **statically** (`URDR-LINEAR`) with the use sites named; a linear value
used exactly once passes; discarding an unused linear value is a stated decision
(affine vs strictly linear — the review must choose and falsify both directions);
the counting law survives α-normalized canon (linearity must be a property of the
canon, not the surface text); and an independent placement reproduces
accept/refuse verdicts over a pinned corpus of programs, twice, with a
deliberately-miscounting checker caught. Until a trigger fires, the dynamic law
stands and is sufficient — `admitted ≠ trusted`, and *wanted ≠ needed*.

**STATUS — apparatus DONE (the glyph is NOT).** The staging package this section
pre-registered has been built and gated: `tools/linear/linear_core.py` (the
reference multiplicity judgment over a minimal linear core — its own term language,
zero Urðr syntax), `tools/linear/corpus_linear.txt` (14 programs, verdicts pinned,
both modes), and `tests/test_linear_core.py` (9 falsifiers, red-first). Every
pre-registered falsifier is realized and green: double-use refuses **statically**
naming both sites; exactly-once accepts; the affine/linear fork is falsified in
both directions (unconsumed-at-END refuses linear / accepts affine; explicit DROP
satisfies linear); DUP refuses in both modes (no-cloning); IF branch-consistency
compares consumption status, not site provenance (a real defect caught during
staging — the naive comparison over-refused matching arms); linearity is a canon
property (case/whitespace noise quotients to one digest, one verdict); and the
miscounting defect checker accepts what the real judgment refuses (the detector
bites). What remains for the eventual §20 review, exactly as before: a fired
trigger, generalization to Urðr's binder structure, the affine-vs-linear DECISION
(both stay falsified until then), and an independent placement reproducing the
corpus verdicts twice with the defect caught. **C4's verdict is unchanged:
deferred.** The apparatus existing does not lower the bar; it removes the excuse
that the bar was too expensive to approach.

## 4. Standing conclusions

1. **The seal is holding under load.** Five netcode rungs, a signature scheme, an
   authoring pipeline, and a composed end-to-end contract entered the system this
   week as pure consumers. When a sealed language absorbs that much new capability
   without a syntax change, the burden of proof on any new glyph rises accordingly.
2. **The kernel's three deep primitives keep paying:** canon→digest (C14 shows
   everything canonical reduces to it), the ᛞ named-verifier mint (C7 shows crypto
   reduces to it), and the līmes (C10/C13 show effects and randomness reduce to
   it). Candidates that *reduce to* a deep primitive are libraries by definition.
3. **One candidate is worth watching** (C4 linearity), with its review conditions
   now written down so that neither enthusiasm nor fatigue decides it later.
4. **Two rejections are load-bearing absences** (C2 catchable refusals, C10
   handlers): the language's power here is what it refuses to express. Any future
   proposal that reintroduces them under a new name should be tested against this
   document first.

`A glyph is earned as a lossless alias of a measured law, or refused. This probe
earned none, deferred one, and found the alphabet sufficient for everything the
gate can currently prove.`

## See also

- `D1-spec.md` §20 (the glyph review law), §21b (glyph-as-missing-constraint)
- `D6-gap-probe.md` (the method this document applies)
- `D5-ledger.md` (grades; this document asserts none above REVIEW)
- `docs/THEOREMS.md` (the measured floor these verdicts stand on)
