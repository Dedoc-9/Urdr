<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# PREDICTIONS — executable epistemics for the predictive READ pass

Every epistemic state is an **executable artifact**, never a prose claim — the Urðr discipline (a claim is
what a gate can turn red) extended to the research process itself. A candidate moves through a state machine,
and every transition carries an executable **witness**:

    UNKNOWN → PREDICTED → PREREGISTERED → READ → OBSERVED → SURPRISE → [ RECURS? → COMPRESSIBLE? → PROMOTED → EXECUTABLE ]

    transition                   witness
    PREDICTED → PREREGISTERED     an immutable git commit dated BEFORE the READ (the rows below)
    PREREGISTERED → OBSERVED      the design brief + the module's live gate output
    OBSERVED → SURPRISE           a structured delta against the frozen prediction (observation vs reality)
    SURPRISE → COMPRESSIBLE       an independent-recurrence detector          — DEFERRED (needs many rows)
    COMPRESSIBLE → PROMOTED       a promotion rule satisfied                  — DEFERRED
    PROMOTED → EXECUTABLE         a new gate / falsifier / theorem added      — DEFERRED

Only the states an experiment has REACHED are populated. The tail and every metric (discovery /
compression / promotion rate, predictive bias) are functions of MANY rows, so they are DEFERRED until
independent recurrence earns them. By the proposal's own **L3** (no promotion from one observation) and **L4**
(a promotion must REDUCE executable complexity), this ledger cannot grow its own tail on zero data — it obeys
itself from the first row.

Laws (they govern this ledger, not merely describe it):
  - **L1** — observation precedes interpretation; a compression may cite only OBSERVATIONS.
  - **L2** — observations are immutable; interpretations may be rewritten (measurements fixed, explanations improve).
  - **L3** — no promotion from a single observation; independent recurrence is the bar.
  - **L4** — every promotion must reduce EXECUTABLE complexity (fewer gate rows / theorem variants / predicates).
  - **L5** — every promoted law must PREDICT something not previously predicted, or it merely renames.

Outcome classes (what was LEARNED, not whether a surprise happened): CONFIRMED-MODEL · LOCAL-SURPRISE ·
ARCHITECTURAL-SURPRISE · FOUNDATIONAL-SURPRISE. A CONFIRMED-MODEL is evidence, not a null: a prediction
surviving a blind READ is information. Stopping rule for the current run: 5 joints, then the class
distribution decides whether a seam basis has earned existence.

Prior reads, entered post-hoc as the seam hypothesis this experiment now tests forward (NOT preregistered —
labelled after the fact, and marked so): `heightfield` → representation seam · `jurisdiction` → admission
seam · `layertheorem` → propagation seam. Three post-hoc labels are a hypothesis-generator, not a basis.

---

## PREREGISTERED — frozen before the READ

### P1 — `opcost`
    state:            PREREGISTERED
    target:           opcost  — next unbriefed articulation joint, import in-degree 7 (centrality-selected)
    provenance:       predicted from opcost's ROLE only (AGENTS.md §7: "op-cost envelopes" bounding tick
                      time); its code is UNREAD. Only its import in-degree was computed, to select it.
    hypothesis:       a COST / BUDGET boundary — a NEW seam (not representation / admission / propagation):
                      an operation is admissible iff its measured op-cost fits a bounded envelope, else a
                      typed refusal.
    refutation risks: named in advance, both real — (a) ADMISSION in disguise: a permission predicate over
                      cost, i.e. the jurisdiction pattern REPEATING, not a new seam; (b) CONSERVED: cost is
                      an invariant quantity rather than a bounded envelope, REFINING the seam into a
                      conservation fact.
    success_rule:     classify opcost's core seam from its LIVE gate rows and core law (the `opcost*` rows),
                      never from prose. CONFIRMED-MODEL iff the core law is "cost ≤ envelope, refuse
                      otherwise"; a SURPRISE (residual recorded) if it is an admission predicate (a) or a
                      conservation invariant (b).
    residual_format:  if SURPRISE, record the delta as a triple — (predicted: bounded envelope; observed:
                      <opcost's actual core law>; delta: <admission (a) | conservation (b)>). The observed
                      half is immutable, the delta label revisable (L1/L2); it is the Stage-C delta the
                      OBSERVED→SURPRISE transition emits — so the blind READ has zero ambiguity in shape.
    witness:          the git commit introducing this row — dated before opcost.py is read.

### P2 — `terraform`
    state:            PREREGISTERED
    target:           terraform — the highest-in-degree briefless joint (import in-degree 9). SELECTION
                      PROCEDURE (the P1 contamination rule, applied): in-degree computed by scanning
                      IMPORT LINES only across tools/terrain; module bodies unread; NO git-history scan
                      of the target before this freeze.
    provenance:       role-only. terraform is known to this session as: (i) AGENTS.md roles — "the CAS
                      edit record" (the WRITE CALCULUS) and "the neutral monolith oracle"; (ii) the index
                      line "The mutable chunked world (T3.40) — the membrane's edit-law"; and (iii)
                      DISCLOSED secondhand exposure: nway's brief (written earlier this session) cites
                      terraform as the independent lift used for nway's shard-head == global-head
                      cross-check. terraform.py itself and its git history are UNREAD.
    hypothesis:       a REPRESENTATION-EQUIVALENCE seam: the core law is chunked-apply ≡ monolith-apply
                      (world identity independent of chunking — the heightfield pattern lifted from
                      static terrain to the MUTABLE world), guarded by a CAS admission check (an edit is
                      admitted iff its declared parent address matches canonical state).
    refutation risks: named in advance — (a) ADMISSION-dominant: the CAS parent-address predicate IS the
                      core law (the jurisdiction pattern on versions), with equivalence merely its test
                      harness; (b) PROPAGATION: the core law is edit commutation / ordering across chunks
                      (the commute family's object), not representation.
    success_rule:     classify terraform's core seam from its LIVE gate rows and core law (the
                      `terraform*` rows), never from prose. CONFIRMED-MODEL iff the central row certifies
                      chunked ≡ monolith equivalence; a SURPRISE (residual recorded) if the central row
                      is the CAS admission predicate (a) or a commutation/ordering law (b).
    residual_format:  if SURPRISE — (predicted: representation-equivalence; observed: <actual core law>;
                      delta: <admission (a) | propagation (b)>). Observed half immutable, label revisable.
    witness:          the git commit introducing this row — dated before terraform.py is read, and before
                      any history scan of it.

### P3 — `stance`
    state:            PREREGISTERED
    target:           stance — the highest-in-degree briefless joint (import in-degree 7). Selection per
                      L59: in-degree from import LINES only, bodies unread, NO history scan of the
                      target before this freeze.
    provenance:       role-only — (i) the index line "The grounded step law (T3.9)" (URDRSTANCE1);
                      (ii) AGENTS.md: the movement-chain opener (`stance` → `gaze` → `drive` → `traj`),
                      named with "sprint gating by terrain, stride gaits, stance checks,
                      walk-through-wall detection (`stance`/`drive`/`glide`, the warden family)".
                      stance.py and its git history are UNREAD.
    hypothesis:       an ADMISSION seam instance — the first preregistered test of a seam family
                      RECURRING: the core law is a per-step admissibility predicate evaluated against
                      canonical terrain (grounded: the step's height transition within a bound), with a
                      typed refusal for ungrounded / wall-crossing steps. The jurisdiction pattern
                      (admissibility from canonical state, never from the claimant) applied to
                      locomotion.
    refutation risks: named in advance — (a) REPRESENTATION: the central row is an equivalence /
                      digest-canon law (stance as a derived canon reproducing pinned digests), not an
                      admissibility predicate; (b) COST-or-COMPOSITION: the central row is a stride/gait
                      envelope (the opcost pattern on movement) or a chain-composition law binding
                      stance to its downstream consumers.
    success_rule:     classify stance's core seam from its LIVE gate rows and core law (the `stance*`
                      rows), never from prose. CONFIRMED-MODEL iff the central row certifies a
                      step-admissibility predicate over terrain state with typed refusal; a SURPRISE
                      (residual recorded) if the central row is (a) or (b).
    secondary:        META, frozen with this row — the P1/P2 signature recurs: the resolution will
                      CONFIRM the predicted core law AND surface >=1 structural dimension the
                      hypothesis did not name. Falsified two ways: a clean (a)/(b) surprise (primary
                      wrong), or a total confirmation with NO unanticipated structure (meta wrong).
                      First second-order prediction in the ledger: the prediction process itself under
                      test.
    residual_format:  if SURPRISE — (predicted: step-admission; observed: <actual core law>;
                      delta: <representation (a) | cost/composition (b)>). Observed half immutable.
    witness:          the git commit introducing this row — dated before stance.py is read, before any
                      history scan of it.

### P4 — `warden`
    state:            PREREGISTERED
    target:           warden — the highest-in-degree briefless joint (import in-degree 6). Selection per
                      L59: import LINES only, bodies unread, no history scan before this freeze.
    provenance:       role-only — (i) the index line "Structural anti-cheat (T3.24, Stage E opener)"
                      (URDRWARD1); (ii) AGENTS.md: "wardens (topology-grade police)", "warden regions
                      as the interest filter", "teleports, speed-hacks, or wall-clips, reusing warden's
                      gait bound + walkable-component β₀". DISCLOSED secondhand exposure from opcost's
                      read (Rung A): warden.components examines (W-1)H + W(H-1) grid adjacencies
                      (MAX_STEP changes union decisions, never the check count); warden.admit_trajectory
                      performs Σ|dx|+|dy| sub-step checks over a CLAIMED trajectory. warden.py and its
                      git history are UNREAD.
    hypothesis:       the TRUE jurisdiction-pattern recurrence, sharpened by P3's residual: warden
                      polices CLAIMS, not walks — so unlike stance (which MEASURES where terrain blocks
                      an honest walk), warden's core law is claim-admission WITH TYPED REFUSAL: a
                      client-claimed trajectory is admitted iff every sub-step obeys the gait/step
                      bound over canonical terrain, else a typed refusal (a teleport, speed-hack, or
                      wall-clip is REFUSED, not measured). The walkable-component structure (β₀) is
                      the derived support (a teleport crosses components), not the central law.
    outcome partition (EXHAUSTIVE — the P3 meta-finding, applied; every resolution maps to exactly one):
                      W-C0  CONFIRMED-MODEL — the central row certifies claim-admission with typed
                            refusal (admit iff the claimed trajectory obeys the bound; violation
                            refuses, typed).
                      W-R1  MEASURE-not-refuse — the central law marks or measures claims (the stance
                            semantics) rather than refusing them.
                      W-R2  REACHABILITY-central — the central law is the components/β₀ structure (a
                            derived representation law), with admission peripheral.
                      W-R3  OTHER — anything else; residual recorded free-form, delta named after the
                            reading and marked post-hoc.
    secondary (META — exhaustive this time):
                      M-0   resolution = W-C0 AND >=1 structural dimension surfaced that this
                            hypothesis did not name (the P1/P2 signature recurs).
                      M-1   resolution = W-C0 with NO unanticipated structure (a perfectly clean
                            confirmation).
                      M-2   resolution ∈ {W-R1, W-R2, W-R3} (a primary residual).
                      The meta PREDICTS: outcome ∈ {M-0, M-2} — no blind prediction in this run lands
                      perfectly clean. Falsified iff M-1. The partition is total: M-0/M-1/M-2 cover
                      every possible resolution.
    residual_format:  if W-R1/W-R2/W-R3 — (predicted: claim-admission-with-typed-refusal; observed:
                      <actual core law>; delta: <R1 | R2 | R3:<named-after-reading>>).
    witness:          the git commit introducing this row — dated before warden.py is read, before any
                      history scan of it.

## DECISION INSTRUMENT — frozen BEFORE P5 resolves (the five-joint checkpoint's procedure)

The run's stopping rule (header) is IMPLEMENTED here, not replaced: "the class distribution decides"
was underspecified, and this section — frozen while one joint remains unread — is the decision
procedure that rung will run. Choosing it after P5 would be post-hoc model selection; the L59/L60
logic applied to the decision layer itself.

**The four-test promotion gauntlet** (a candidate basis is promoted only if it survives all four):
  A COMPRESSION      each candidate basis must classify EVERY read joint (post-hoc and preregistered)
                     with ZERO per-module exceptions; exceptions are counted; a basis with exceptions
                     is a list, not a basis.
  B PREDICTION       at least one basis-DERIVED frozen prediction confirmed before promotion. P5 is
                     the live instance: both bases below derive a prediction for `budget`, frozen
                     here, and the resolution scores both.
  C STABILITY        G(n) = unique seam families / preregistered READs, computed over the run;
                     promotion requires G decreasing by the checkpoint. CONTINUATION RULE (governs
                     runs AFTER this one, never this one retroactively): keep freezing joints until
                     two consecutive READs introduce no new family AND compression holds — then stop.
  D COUNTERFACTUAL   operationalized (the "delete the basis" test made checkable): the basis must
                     hold >=1 CONFIRMED prediction whose content is traceable to the BASIS and not to
                     the target's role prose. Candidate instance on record: P4's refuse-not-measure
                     semantics came from P3's residual, not from "anti-cheat" prose. The decision
                     rung adjudicates.
**Checkpoint outcome space (exhaustive, L60)**: PROMOTE-A · PROMOTE-B · KEEP-BOTH-AS-RIVALS (neither
dominates; both stay alive, scored against the next run) · NO-PROMOTION (a failed gauntlet is a
recorded negative — the basis question stays open without an abstraction being minted).

**The competing bases** (executable objects; rivals, not cumulative discoveries):

    basis: B-A ("seam-type")
      members:   representation · admission · propagation · cost
      supports:  heightfield(rep, post-hoc) · jurisdiction(adm, post-hoc) · layertheorem(prop,
                 post-hoc) · opcost(cost, P1) · terraform(rep, P2) · warden(adm, P4);
                 STRAIN on stance (P3): the type axis is silent on refuse-vs-measure — the residual
                 had to be patched in as a semantics note, which is an exception Test A counts.
      predicts:  budget → COST-family recurrence: the central row is a bounded-envelope /
                 exhaustion-refusal law (the opcost within_budget pattern; the cost family's second
                 preregistered member — the L3 recurrence test).
      fails_if:  P5 lands C-B (the role axis load-bearing where the type axis is silent); a sixth
                 independent family is needed; G(n) non-decreasing at the checkpoint.

    basis: B-B ("role × substrate")
      members:   role ∈ {police-the-question, measure-the-answer} × substrate ∈ {canonical state,
                 measured resource, claims, representation}
      supports:  jurisdiction (police × canonical state) · stance (measure × terrain) · warden
                 (police × claims) · opcost (measure counts, police budget — factors with no
                 exception) · terraform (police CAS, measure equivalence). B-B explains P3's surprise
                 NATIVELY: stance-vs-warden is an axiom of the basis, not an anomaly.
      predicts:  budget → the MONOTONE ONE-WAY law central: "a refund voids the bound" is the
                 load-bearing clause — allowance flows one way (pure subtraction), a credit attempt
                 is structurally forbidden (the layertheorem flow pattern on a resource), with
                 spend-refusal as the guard.
      fails_if:  P5 lands C-A with monotonicity absent or peripheral; role assignment needs
                 per-module exceptions; a third role is required immediately.

    scoring (both): modules-explained · predictions-made · predictions-confirmed ·
                    residuals-unexplained. The gate is the tournament; no scorer engine is built
                    (L58) — two ledger objects and their frozen predictions are the n=2 embryo.

### P5 — `budget` (the run's final freeze; the first BASIS-DISCRIMINATING experiment)
    state:            PREREGISTERED
    target:           budget — frontier tie at in-degree 5 (budget, wire); TIE-BREAK RULE, frozen:
                      lexicographic ascending on module name. Selection per L59: import LINES only,
                      bodies unread, no history scan before this freeze.
    provenance:       role-only — the index line "The defect budget as a first-class resource — pure
                      subtraction, a refund voids the bound" (URDRBGT1). Ambient disclosed exposure:
                      AGENTS.md prose elsewhere associates budget-bounded testing with "the OPCOST
                      discipline" (a phrase about another module's test harness). budget.py and its
                      git history are UNREAD.
    hypothesis:       DERIVED FROM THE BASES, not authored fresh — B-A and B-B disagree about the
                      central row (above), and P5's job is to discriminate.
    outcome partition (EXHAUSTIVE, L60 — every resolution maps to exactly one):
                      P5-C-A   central row = exhaustion/envelope refusal (cost recurrence), with
                               refund-forbidding peripheral or absent → B-A's prediction.
                      P5-C-B   central row = the monotone/no-refund one-way law, with exhaustion
                               refusal as guard → B-B's prediction.
                      P5-C-AB  ONE central row certifies both inseparably → both partially right,
                               NOT discriminating (the tie is recorded as such).
                      P5-R-M   the semantics are MEASURE-not-refuse (the stance pattern: budget
                               reports; only the domain refuses) → surprises BOTH bases.
                      P5-R-O   OTHER — catch-all; residual free-form, delta named after reading.
    secondary (META — exhaustive): M-0 resolution ∈ {C-A, C-B, C-AB} AND >=1 unnamed structural
                      dimension surfaced · M-1 same set with NONE · M-2 resolution ∈ {R-M, R-O}.
                      The meta predicts ¬M-1 (the signature is 4 for 4).
    residual_format:  if R-M / R-O — (predicted: A=<cost-envelope> B=<monotone-flow>; observed:
                      <actual>; delta: <R-M | R-O:<named-after-reading>>).
    witness:          the git commit introducing this row — dated before budget.py is read, before
                      any history scan of it.

### P5 — resolved: **P5-C-AB (the tie, recorded as the partition anticipated)** · meta: **M-0 (5 for 5)**
    read:             2026-08-04, the fifth and final blind READ of the run (Rung F). Classified from
                      the LIVE `budget*` rows.
    observed:         ONE central row — `budget-descent` — certifies BOTH bases' predictions
                      inseparably: "MONOTONE NON-INCREASING by pure integer subtraction with no
                      clamp: exactly 6 succeed and the 7th refuses, the remainder never goes
                      negative … A NEGATIVE CHARGE IS REFUSED AS A REFUND." The well-founded descent
                      on (ℕ, <) IS both halves at once: never-up (B-B's monotone one-way law) and
                      bottom-refusal (B-A's exhaustion envelope) are one law, not two. The module's
                      own derivation order favors B-B's READING — "a quantity that can go back up has
                      no termination argument and THEREFORE no bound" (monotonicity grounds the
                      refusal) — and the refund PUMP is measured, not argued (`budget-selftest`:
                      4 clean submissions buy a cost-4 violating block; reachable budget unbounded in
                      submissions, 100→100, 1000→1000, against an honest cap of 6). But by the FROZEN
                      central-row criterion the outcome is the tie class, and it is recorded as such.
    unnamed structure (the M-0 half — the run's largest): NEITHER basis predicted budget's
                      distinctive law: COMPOSITION-SOUNDNESS. `jurisdiction` proved
                      defect(A∪B) ≤ defect(A)+defect(B) and left it a theorem; budget SPENDS it —
                      per-part charging can only OVER-charge (55 pairs, 0 under-charges), the
                      conservatism is PRICED (2 pairs over by at most 1 cell), and on PREFIX-DISJOINT
                      shards it is EXACT (49/49, sum == union, no covariance term — what makes tiled
                      city budgets compose). Also unnamed: "the cost is COMPUTED, never passed"
                      (charge_for's signature admits no submitted number — the structural firewall),
                      and the two measured design-refusals (modality credits; privilege as a
                      firewall). A composition axis exists in the seam space and NO basis carries it
                      — Test A evidence for the decision rung.
    basis scoring:    B-A — prediction partially confirmed (C-AB); the cost pattern (bounded
                      resource, typed refusal at exhaustion) has now RECURRED preregistered
                      (opcost, budget). B-B — prediction partially confirmed (C-AB); the module's
                      derivation order and the computed-never-passed substrate read natively in
                      B-B's axes. BOTH leave the composition dimension unexplained. The
                      discrimination P5 was designed for did not occur; the tie plus the shared
                      unexplained residual is itself the datapoint the decision rung inherits.
    secondary (META): M-0 — decidable, and the signature is now 5 for 5: every blind prediction in
                      the run was right about the law it named and blind to at least one structural
                      dimension of it.
    outcome:          THE RUN IS COMPLETE. Five preregistered joints: P1 cost CONFIRMED · P2
                      representation CONFIRMED · P3 admission-of-walks LOCAL-SURPRISE
                      (refuse ≠ measure) · P4 admission-of-claims CONFIRMED (the loop closed) · P5
                      the C-AB tie with the composition dimension unexplained by both bases. The
                      five-joint checkpoint now fires: the next rung RUNS THE FROZEN GAUNTLET
                      (A compression · B prediction · C stability/G(n) · D counterfactual) over this
                      distribution and decides among PROMOTE-A / PROMOTE-B / KEEP-BOTH-AS-RIVALS /
                      NO-PROMOTION.
    contamination:    none — L59, sixth application; the freeze commit predates the READ.

## THEOREM CANDIDATES — stated, with executable witnesses

### W1 — the Wagenburg Bound (stated, NOT mechanized; witness: `seamgame.py`)
    statement:        (1) SATISFIABILITY — a seam constraint system admits a perfect head-free strategy
                      iff it is globally satisfiable (Cleve–Mittal); the canonical head achieves 1 on
                      every satisfiable system by publishing the global section. (2) GAP — for an
                      unsatisfiable system the head-free value is exactly computable and < 1; the head
                      still achieves 1 by constructing a PER-ROUND LOCAL SECTION (it never needs the
                      global one). (3) AUDIT — on a declared head-free run, an observed rate above the
                      exact bound convicts an undeclared channel from the scoreboard alone.
    measured (T1):    magic-square seam — 0/512 global sections, 9/9 context pairs locally satisfiable;
                      head-free value EXACTLY 8/9 (4096 deterministic pairs enumerated, 144 optimal);
                      head-ful 9/9; audit plant bites both directions (honest 8/9 not convicted,
                      covert-channel 9/9 convicted). MEASURED — exhaustive, deterministic, rerun
                      byte-identical: PYTHONHASHSEED=0 python exe_epistemics/seamgame.py
    measured (T3):    N-party parity seam, N=2..5 — head-free values 1, 3/4, 3/4, 5/8, each EXACT and
                      equal to the known classical bound 1/2 + 2^-ceil(N/2); the head holds 1 at every N.
                      The worldscale reading: the seed-only ceiling FALLS as shards multiply; the
                      canonical head's margin grows. MEASURED, same witness.
    preregistered (T2): expectation — Urðr's LIVE seams (nway / geoquorum / worldregion seam2) are
                      globally SATISFIABLE constraint systems (the CORE exists and publishes the
                      section), so clause (3) has no live unsatisfiable seam to police. Deferred to its
                      own rung; if a live seam measures UNSATISFIABLE, that is an architectural surprise
                      worth its own S-row.
    promotion rule:   W1 stays stated-not-gated (L58) until a live head-free seam run exists for the
                      audit clause to police. The witness is executable today; the gate row is earned by
                      a real seam, not by the plant.

## OBSERVED / RESOLVED — the delta ledger

### P1 — resolved: **CONFIRMED-MODEL** (the frozen block above stays byte-intact as the witness)
    read:             2026-08-03, the blind READ (Rung A). Classified from the LIVE gate rows and core
                      law per the frozen success_rule — never from prose.
    observed:         opcost's core law IS "cost <= envelope, refuse otherwise", as two inequalities:
                      (1) ENVELOPE — glide_micro_count <= glide_micro_bound, STRICT on the wall scene
                          (`opcost-bound`; the bound is non-vacuous, a wall witness);
                      (2) BUDGET — within_budget(cost, budget) admits at/under the ceiling and raises a
                          typed OPCOST-REFUSE over it (`opcost-budget`: "refuse, never overrun").
                      Plus one structure the prediction did not anticipate: the WORK / WALL-CLOCK split —
                      the certified half is the deterministic exact op-count (a pure function of input,
                      byte-exact digests); wall-clock lives in bench.py, host-tagged, never gated. The
                      seam certifies only the deterministic half of latency.
    refutation risks: both named risks measured FALSE from the rows —
                      (a) NOT admission-in-disguise: the predicate input is a measured resource quantity
                          of the operation itself (an exact op-count), not canonical lattice state.
                          jurisdiction refuses on WHERE truth lives; opcost refuses on HOW MUCH WORK the
                          operation performs. Same refusal DISCIPLINE (typed, fail-closed), different
                          measured object — a distinct seam, not the admission pattern repeating.
                      (b) NOT conserved: cost is BOUNDED, not invariant — count < bound strictly when a
                          wall bites. (Conservation appears downstream in govern: admitted + deferred ==
                          all — a different quantity, actors not cost.)
    delta:            none — CONFIRMED-MODEL; the residual_format goes unused, as designed.
    outcome:          the COST seam exists as predicted. Seam labels now: representation / admission /
                      propagation (post-hoc) + cost (PREREGISTERED, confirmed). Still a
                      hypothesis-generator, not a basis — one preregistered confirmation and three
                      post-hoc labels do not earn a seam taxonomy (L3).
    contamination:    DISCLOSED — after the prediction text was frozen and gate-tested (2026-08-03
                      ~19:43 UTC) but before the witness commit was pushed, a lineage chronology scan
                      printed opcost's first-commit SUBJECT ("certified integer-work envelope +
                      host-tagged wall-clock"), leaking the phrase "work envelope" into the session. The
                      frozen text predates the leak (file mtime + session order); the commit witness
                      ALONE would not prove that. Recorded per L1/L2: the leak is the immutable
                      observation, the priority of the freeze is the interpretation. Rule forward: freeze
                      commits land BEFORE any history scan of the target module.
    law note:         the candidate Attentional-Epistemics law's UNLESS clause (a conserved gradient in
                      unobserved regions) was bound to refutation risk (b) as its first discriminating
                      test; (b) measured FALSE, so the law's first datapoint is NEGATIVE — no
                      conserved-cost mechanism earned. The law stays stated-not-mechanized.

### P2 — resolved: **CONFIRMED-MODEL** (frozen block above byte-intact; the under-prediction recorded)
    read:             2026-08-03, the second blind READ (Rung C). Classified from the LIVE `terraform*`
                      rows per the frozen success_rule — never from prose.
    observed:         the central row (`terraform-edit`, the module's namesake "membrane's edit-law")
                      certifies the predicted equivalence: an edit equals the DIRECT MUTATION
                      byte-for-byte, and moves EXACTLY the containing chunk's manifest slot
                      (☿-locality). Plus a half the prediction did not anticipate: ANAMNESIS — an edit
                      never mutates in place; it mints a new chunk record + manifest, and BOTH the
                      parent and the edited world reassemble bit-for-bit from ONE shared store.
                      Identity-by-address; "an address, not an undo". The CAS (stale parent /
                      old-height, typed TERRAFORM-REFUSE) is the GUARD, exactly as predicted; the chain
                      law (replay == head, order structural) and the certified blast radius live in
                      `terraform-chain`; the refusal battery in `terraform-refuse`.
    refutation risks: neither materialized — (a) the CAS is a guard row, not the central law; (b)
                      ordering is structural inside the chain row, and commutation proper is the
                      separate `commute` module, already briefed.
    delta:            none under the frozen rule (neither (a) nor (b) occurred; the central row
                      certifies the equivalence). Honest note: the hypothesis captured the CORRECTNESS
                      half of the ☿-law and missed the PERSISTENCE half (anamnesis / structural
                      sharing) — recorded as unanticipated structure, the P1 pattern repeating: both
                      blind predictions so far were right about the law and blind to one structural
                      dimension of it.
    outcome:          CONFIRMED-MODEL. Census: 2 preregistered resolutions (cost, representation), both
                      confirmed; representation now holds 1 preregistered + 1 post-hoc member
                      (heightfield). Still below L3's bar — independent PREREGISTERED recurrence per
                      family — so no taxonomy and no promotion.
    contamination:    none — the freeze-before-history rule (L59) was applied structurally: the target
                      was selected from import LINES alone, no git command touched it before the freeze,
                      and the only pre-exposure was the role prose + nway's secondhand citation, both
                      DISCLOSED in the frozen provenance.

### P3 — resolved: **LOCAL-SURPRISE** — the ledger's first residual (frozen block byte-intact)
    read:             2026-08-04, the third blind READ (Rung D). Classified from the LIVE `stance*`
                      rows per the frozen success_rule.
    observed:         the central row (`stance-properties`) certifies the predicted PREDICATE exactly —
                      a per-step admissibility gate over canonical terrain (a step is walled iff its
                      rise exceeds MAX_STEP; "the gate is the terrain, not the model", pinned by one
                      path that clears at MAX_STEP 40 and walls at 20) — but NOT the predicted
                      semantics: a wall does not REFUSE. Blocking is a MEASURED EVENT — the result is
                      the first walled step index, the walk returns where the terrain stopped it. The
                      typed refusal (STANCE-REFUSE, 8/8 total) guards ONLY the domain boundary:
                      malformed declarations refuse; walls MEASURE. Grading in the module's own terms:
                      the movement MODEL is DECLARED, the walk is MEASURED — stance is the
                      solid-ground sibling of buoyancy/crossing, a measurement instrument, not a court.
    residual:         (predicted: admission-with-typed-refusal; observed: admission-FORM predicate
                      whose blocking is a measured event, typed refusal only at the domain boundary;
                      delta: REFUSE → MEASURE — a class NEITHER named risk covered; risks (a)
                      representation-central and (b) cost/composition-central both measured FALSE).
                      The residual's content: this repo separates ADMISSION OF THE QUESTION (domain
                      membership — refuses) from THE ANSWER (a measured event — never refused).
                      jurisdiction refuses inadmissible claims; stance measures where terrain blocks.
    secondary (META): INDETERMINATE BY ITS OWN TERMS. Neither frozen falsifier fired (the resolution
                      is not a clean (a)/(b) surprise, and not a total confirmation) — but the positive
                      condition did not cleanly hold either: a named sub-claim was WRONG, which is
                      stronger than a missed dimension. The meta's outcome partition was INCOMPLETE.
                      Methodological finding, to be applied at P4's freeze: a frozen prediction must
                      partition its outcome space EXHAUSTIVELY — every possible resolution maps to
                      exactly one frozen class. (One instance; a LESSONS row waits for its application.)
    outcome:          census: 3 preregistered resolutions — cost CONFIRMED-MODEL, representation
                      CONFIRMED-MODEL, admission → LOCAL-SURPRISE (refuse ≠ measure). The ledger's
                      first Stage-C residual object exists. Two freezes remain before the stopping
                      rule's five-joint decision.
    contamination:    none — L59 applied (import lines only; the freeze commit predates the READ and
                      any history scan; role prose was the only declared exposure).

### P4 — resolved: **W-C0, CONFIRMED-MODEL** · meta: **M-0, the first second-order confirmation**
    read:             2026-08-04, the fourth blind READ (Rung E). Classified from the LIVE `warden*`
                      rows under the run's first EXHAUSTIVE outcome partition — the verdict is
                      decidable by construction, and it decided.
    observed:         the predicted core law holds exactly: a claimed trajectory or position is
                      ADMITTED or typed-REFUSED — "reconstruct-or-refuse turned against the cheater."
                      An honest walk and an honest glide admit (`warden-kinematic`); a wall-climbing
                      step is WARD-TUNNEL, a diagonal or >2-cell jump WARD-TELEPORT; the refusal
                      battery is total and typed (`warden-refusal`: 4/4 sub-codes under one
                      WARD-REFUSE code). P3's residual, used PREDICTIVELY in this freeze, held:
                      warden polices CLAIMS and refuses; stance measures WALKS and never does. The
                      question/answer split has its first predictive success.
    unnamed structure (the M-0 half): the hypothesis framed β₀ as derived SUPPORT for
                      trajectory-checking. The rows show it is a SECOND, ORTHOGONAL CERTIFICATE for a
                      different claim TYPE: `admit_position` refuses a BARE POSITION claim from the
                      component structure alone — no trajectory to inspect — "the cheat a per-tick
                      replay cannot cheaply catch" (`warden-topological`: β₀ = 3, structural,
                      non-vacuous). Kinematic certifies claimed PATHS; topological certifies claimed
                      STATES. Also unnamed: the one-code/four-sub-codes refusal attribution, and the
                      undirected (mutual-reachability) boundary with directed reachability deferred.
    residual:         none — W-C0; the residual_format goes unused. Risks R1 (measure-not-refuse) and
                      R2 (reachability-central) both measured FALSE; R3 (the catch-all) unneeded —
                      but its EXISTENCE is what made the verdict total (L60).
    secondary (META): M-0 — the resolution is W-C0 AND unnamed structure surfaced. The meta predicted
                      outcome ∈ {M-0, M-2} (¬M-1: no blind prediction in this run lands perfectly
                      clean); M-0 occurred. The first DECIDABLE second-order verdict, and it is a
                      confirmation: the missed-dimension signature is now 4 for 4.
    outcome:          census: 4 preregistered resolutions — cost CONFIRMED, representation CONFIRMED,
                      admission-of-walks → LOCAL-SURPRISE (refuse ≠ measure), admission-of-claims
                      CONFIRMED. One freeze remains (P5), then the stopping rule's five-joint
                      decision. The run's first residual→prediction→confirmation loop closed this
                      rung (n=1 — noted, not promoted; L3).
    contamination:    none — L59, fifth application; the freeze commit predates the READ.
