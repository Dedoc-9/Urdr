<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D19 — The abductive-gauntlet contract (the hypothesis boundary)

Status: **SPECULATIVE (the pipeline contract, §1–§4); first rung LANDED (W1, §5).** No
proposer module exists and no gate stage enforces the pipeline contract. §5's detector has
landed — `tools/intla/winding.py`, gate stage `winding`, the 8th D17 detector, THEOREMS T23,
graded in [`D5-ledger.md`](D5-ledger.md) — and that stage measures the DETECTOR, never this
contract. The contract remains what it was: written before its implementation — deliberately,
in the D16 pattern (contract first, falsification workload second) — and per AGENTS rule 10,
any document that cites the D19 *pipeline* as an existing capability is a bug. Provenance: authored 2026-07-16
from a design conversation and numbered by the working name it carried there; `D18` is
unassigned (the D-series follows writing order, not a table of contents). `signum ≠ rēs` —
the number records where the idea came from, not what it is worth.

D17 asks the engine's organizing question: *which exact statements about an object remain
true under a declared class of transformations?* D19 asks the question that comes before it:

> **Which statements are worth the gate's time — and how does the engine take a suggestion
> without taking testimony?**

Everything this repository admits today was verified; nothing in the repository *finds* the
statement to verify. A proposer — a human, a search procedure, a large language model, the
`calculationViz` machine shop — can nominate candidates. The entire content of D19 is the
boundary that lets nominations in without letting a single unearned grade in with them.
Deduction is already housed (the gate). Abduction gets a door, not a seat.

## 1. The load-bearing law

> **A proposal is provenance, never evidence.** Every candidate enters at the floor grade —
> maturity `SPECULATIVE`, evidence `N/A` — regardless of who or what proposed it, how
> confident the proposer sounds, or how many rivals were pruned before it. **Elimination is
> measured; survival is not evidence.** Only the gate raises a grade, and it raises it exactly
> as far as a corpus-scoped reproduction earns.

The kernel already contains this law in miniature: `MEASURED` written in source is refused
(`URDR-EVIDENCE-UNEARNED`); `Grounded` is minted only by the verify primitive `ᛞ`. D19 is
that refusal extended across the līmes: **machine-generated text is source.** A proposer's
"this is confirmed" is a string, not a measurement, and it meets the same typed stop a human
writing `MEASURED` in a program meets.

## 2. The pipeline (and what each step may mint)

| Step | Machinery | Determinism | May mint |
|---|---|---|---|
| **PROPOSE** | anything, off-gate (human, search, LLM, `calculationViz`) | may be nondeterministic | a *recorded* candidate batch — nothing else |
| **RECORD** | content-addressed batch artifact at the līmes (the capability discipline: recorded inputs, D1 §16) | the record **is** the determinism boundary | the batch digest |
| **CONSTRAIN** | admitted D17 detectors only; every elimination is a typed, witnessed verdict on a recorded object | deterministic, replayable (`PYTHONHASHSEED=0`) | witnessed *refutations* of eliminated candidates |
| **VERIFY** | the existing gate machinery, unchanged | deterministic, ×2, subprocess-isolated | corpus-scoped confirmation (digest match), witnessed divergence, or typed refusal |
| **GRADE** | [`D5-ledger.md`](D5-ledger.md) | n/a | exactly what the gate earned, never more |

Nondeterminism ends at RECORD. Before it the proposer may be as wild as it likes; after it,
everything must replay bit-for-bit from the recorded batch. This is the `calculationViz`
admission boundary (the shape crosses, the witness stays behind `verify.py`) applied to
statements instead of geometry.

## 3. The contract

> An abductive module is admitted as a proposer **iff** every batch it emits is recorded at
> the līmes as a content-addressed artifact before anything downstream reads it; every
> recorded candidate enters at the floor grade, and a candidate whose grade field exceeds the
> floor is refused whole; every elimination between record and verdict is a typed, witnessed
> verdict from an admitted detector; surviving candidates meet the existing gate unchanged;
> and no path exists from the proposer to the kernel, the ledger, or a frozen surface except
> through the four steps above.

Five clauses, each a checkable obligation:

1. **Recorded batch, or nothing happened.** A proposal that was not recorded does not exist
   to the pipeline. The batch is content-addressed (digest identity, D1 §7) and enters as a
   recorded input in the capability sense: replay starts from the record, and the question
   "what did the proposer actually suggest?" has a digest for an answer. Candidates are
   structured records (statement, declared domain, parameters); free text rides along as
   opaque provenance and is never parsed for meaning.
2. **Floor grade on entry; self-grading is refused, not corrected.** Maturity `SPECULATIVE`,
   evidence `N/A`, whatever the proposer said. A candidate whose grade field claims more is
   not silently downgraded — the batch is refused whole, because a module that self-grades
   once will self-grade again (the house move: refuse, never repair).
3. **Elimination only by witnessed refutation.** CONSTRAIN may remove a candidate only by an
   admitted detector's typed verdict on the recorded object — e.g. `w = −1` with its crossing
   list: *this recorded curve is not in the declared class* — never by heuristic score,
   confidence, or ranking. Heuristics may *order* survivors for verification; ordering is
   presentation (the D15 inertness idea). If verification is budgeted, the unverified
   remainder stays recorded and the report says so; a candidate silently dropped between
   record and verdict violates the contract. No silent caps. Elimination is measured;
   survival is not evidence.
4. **Verification is the gate, unchanged — no new witness class.** A surviving candidate is
   confirmed only as the existing machinery confirms anything: a corpus-scoped, digest-pinned
   reproduction (×2, subprocess-isolated), or refuted by witnessed divergence, or stopped by
   typed refusal. D19 grants no verification power the gate does not already have and
   introduces no new witness class (the D16 standard).
5. **One-way boundary; provenance is metadata, not identity.** The proposer never edits the
   kernel, never writes D5, never touches a frozen surface; which proposer produced a
   candidate is carried as provenance and never enters any digest (D14 clause 5, reused).
   Downstream of RECORD the pipeline cannot tell a human's candidate from a machine's —
   which is what makes the floor grade enforceable rather than aspirational.

## 4. Refusals

`ABDUCT-REFUSE` — a **layer** refusal family in the `PHYS-REFUSE` pattern; the kernel is
frozen and stays frozen. D19 requires no new glyph and no kernel edit — the D13 null
hypothesis holds here too. Total and typed; rejects the batch whole, never repairs. Four
shapes:

- **evidence-unearned** — a candidate's grade field exceeds the floor (the līmes extension of
  `URDR-INFLATE-STATIC` / `URDR-EVIDENCE-UNEARNED`);
- **unrecorded** — a downstream step read a batch with no recorded digest;
- **pruner-unadmitted** — an elimination cites machinery with no D17 admission;
- **silent-drop** — verdicts ∪ survivors ∪ declared-deferred ≠ the recorded batch.

Final code naming lands with the implementation, alongside its rejection fixtures.

## 5. The first rung — `W1`, the winding-number detector

W1 is the only path this document has to a grade, and D19 becomes falsifiable the way D14
did: by its first enforced rung. Note that W1 itself has nothing abductive about it — it is
an ordinary D17 detector, specified here because it is the first *constraint instrument* a
D19 pipeline would be permitted to prune with, and because its defect corpus doubles as this
contract's non-vacuity test.

*Landed 2026-07-16:* `tools/intla/winding.py` + `conformance_winding.txt` (5 scene goldens,
17 Loewner probes) + `tests/test_winding.py` (12 falsifiers) + gate stage `winding` with its
selftest and refusal rows, registered in the D17 lint — **8 detectors**. THEOREMS T23; graded
MEASURED (reference) in D5. The specification below is retained as the record of what the
landing was required to satisfy.

    𝒟_W1 = (Dom, Inv, W, ~, R)

- **Dom** — closed polylines with integer vertices (≥ 3, consecutive vertices distinct — the
  D14 integer-snap law reused) together with an integer probe point not on the trace (exact
  on-segment test). Membership decidable in exact integer arithmetic.
- **Inv** — the winding number `w(γ, p) ∈ ℤ`: cast a horizontal ray from `p`; each directed
  edge crossing it contributes ±1 under the half-open rule (`a_y ≤ p_y < b_y` upward, the
  reverse downward), the side test an exact orientation determinant. The two half-open
  inequalities make vertex-on-ray cases unambiguous with no perturbation, no epsilon, no
  float. *Terminology guard:* Albers–Tabachnikov say "rotation number of γ around x" for
  this quantity; it is the winding number about a point, **not** the Whitney turning number
  of the tangent — a different invariant. Do not build the wrong detector.
- **W** — the crossing list `(edge index, sign)`; anyone can recount; the sum is the
  invariant.
- **~** — cyclic rotation of the vertex list and insertion/removal of collinear subdivision
  vertices (trace- and orientation-preserving reparametrization). Orientation reversal is
  deliberately **not** in `~`: it negates `w`, a documented covariance the corpus must
  exhibit.
- **R** — `WIND-REFUSE`: probe on the trace; degenerate polyline (fewer than 3 vertices, a
  repeated consecutive vertex — closure is implicit, so "open" is unrepresentable; this
  wording was corrected at landing to match the code); non-integer input, bool included.
  The Python reference is exact on all of Dom (bigint); an eventual placement refuses on
  overflow rather than wrapping, per house law.

Axes at landing (D17 §3a): reproduction `REFERENCE`; separation `PARTIAL` — many curves
share a winding number, and `w` does not recover the curve.

**The Loewner corpus (theorem-backed goldens, honestly scoped).** Loewner proved, in a 1948
*Annals of Mathematics* paper recently revived by Albers–Tabachnikov: for monic real
polynomials `P` (degree n+1) and `Q` (degree n) with interlacing real roots and any smooth
periodic `f`, the closed curve `γ(t) = (P(d/dt)f, Q(d/dt)f)` has non-negative rotation
number about every point not on it — simplest cases `(f′, f)` and `(f″ − f, f′)`. The corpus
pins integer polylines *authored from* that construction (sampled, scaled, snapped; the
authoring script and parameters recorded as provenance metadata, never identity), plus
pinned probe points, with golden `w ≥ 0` at every probe. Honest scope, stated twice because
it is the part a hurried reader inflates:

- the gate checks **exact winding numbers of frozen integer objects** — a corpus-scoped
  fact, T3's kind of claim, not a proof of the smooth theorem;
- the smooth theorem is the *author's reason the corpus looks like it does*; a coarse
  sampling can break the discrete↔smooth correspondence, which is exactly why the samples
  are pinned rather than derived at gate time;
- symmetrically, a W1 refutation eliminates **the recorded candidate object**, never the
  unrecorded smooth ideal behind it. Constraints prune recorded candidates, not platonic
  hypotheses; any tie back to a smooth hypothesis carries the declared sampling assumption.

**Red-first (the falsifiers W1 must ship with).**

1. a pinned non-Loewner curve — a clockwise loop or a figure-eight lobe — whose golden is
   `w = −1` at a pinned probe: the detector separates sign, not merely parity;
2. a defect variant that drops the crossing sign (parity-only count) and **must** redden;
3. `WIND-REFUSE` fixtures: probe on the trace; open polyline;
4. the `~`-invariance corpus (cyclic rotations + collinear subdivisions), and the reversal
   case exhibiting `w → −w`.

**Ladder** (AGENTS §5, unchanged): prototype → `tools/intla/winding.py` (basename must be
globally unique across `tools/` per rule 9 — verify before landing) →
`conformance_winding.txt` → `tests/test_winding.py` → gate stage `winding` +
`winding-selftest` → grade in D5 → cross-place when load-bearing. Only when that stage is
green may any document — including this one — say "Loewner-constrained" about anything, and
then only for candidates in Dom.

## 6. Lineage (informative — recorded so the provenance is exact; proves nothing)

| Year | Source | What it actually says | What D19 takes |
|---|---|---|---|
| 1878 / 1903 | C. S. Peirce | abduction (retroduction) named as the inference that *proposes* | the word, and the floor grade |
| 1918 | E. Noether | differentiable symmetry ⇒ conservation law | a candidate future detector family — no code exists |
| 1948 | C. Loewner, *Annals of Mathematics* | interlacing-operator curves of smooth periodic functions wind non-negatively about every off-curve point | the W1 corpus |
| 1952 | B. D. H. Tellegen, *Philips Research Reports* | network topology alone forces ⟨v, i⟩ = 0 for **any** two admissible flow assignments — a constraint above every constitutive law | a candidate future detector family — no code exists |
| 1958 | N. R. Hanson, *Patterns of Discovery* | philosophy of science studied the finished research report; the finding of hypotheses has a logic of its own (d. 1967) | the PROPOSE/VERIFY split as a *boundary*, not a blur |
| 1977 | I. Prigogine (Nobel, chemistry) | order arises from non-equilibrium dissipation | framing for "structure that survives filtration" — DECLARED, not machinery |
| 1977 | M. Serres, *La Naissance de la physique* | structure emerges from flow; mediation (the angel figure is his later *Hermes* / *Angels* period) | framing only — DECLARED |
| 2021 | P. Albers, S. Tabachnikov, arXiv:2109.03051; *The Mathematical Intelligencer* (doi:10.1007/s00283-021-10144-z) | the revival of Loewner 1948 ("forgotten": the original drew ~4 citations) | the working reference for W1 |

Corrections this table bakes in, so they are never re-imported from conversation: Loewner's
theorem is **1948, not 1955**. There were **no "formal theorems of abduction" in the 1950s**
to be dismissed — Peirce named the mode, Hanson argued it philosophically, and formalization
came decades later in AI. "The topological machinery wasn't mature" is false — winding
numbers long predate 1948; the result was simply little-cited. The theorem concerns winding
about points, not turning numbers.

**What D19 does not claim** (the negative results are kept because they are correct):
nothing about chaos becoming predictable; nothing about P vs NP — a pruned finite candidate
set is smaller, not asymptotically easier; nothing about inverting or weakening SHA-256;
survival of pruning confers no grade; an LLM is a proposer, never an oracle, never a
witness.

## 7. Honest scope — what exists on the day this was written

Zero proposer modules. Zero recorded batches. No `ABDUCT-REFUSE` anywhere, kernel or layer.
**W1 is the one thing that now exists**: `tools/intla/winding.py`, gated (`winding`, the 8th
D17 detector), graded MEASURED (reference) in D5, THEOREMS T23 — a constraint instrument,
measured as a detector; its green rows say nothing about the pipeline above it. The Tellegen
and Noether rows above remain names, not designs. The "`calculationViz` becomes an explorer"
scenario remains a consumer sketch (`DECLARED`), not an obligation of this contract. The
pipeline contract (§1–§4) earns `MEASURED` status the way D14 did — when a gate stage
enforces its checkable core (the recorded-batch boundary, the floor grade, `ABDUCT-REFUSE`) —
and that stage does not exist. Nothing above §5 rose because W1 landed.

## See also

- [`D14-frontend-contract.md`](D14-frontend-contract.md),
  [`D15-view-contract.md`](D15-view-contract.md),
  [`D16-regional-authority.md`](D16-regional-authority.md) — the three existing one-way
  boundaries (assets in, views out, authority partitioned); D19 is drafted as the fourth
  (hypotheses in)
- [`D17-invariant-detectors.md`](D17-invariant-detectors.md) — the admission law every D19
  pruner must already hold
- [`D1-spec.md`](D1-spec.md) §5, §16, §19 — the epistemic type discipline this extends
  across the līmes; [`R4-dipole_quantum_ratchet.md`](R4-dipole_quantum_ratchet.md) — the
  provenance-vs-meaning precedent (`signum ≠ rēs`)
- [`../docs/THEOREMS.md`](../docs/THEOREMS.md) — the measured floor this document must never
  be confused with
- P. Albers, S. Tabachnikov, *Loewner's "forgotten" theorem* — arXiv:2109.03051; *The
  Mathematical Intelligencer* (2021), doi:10.1007/s00283-021-10144-z
