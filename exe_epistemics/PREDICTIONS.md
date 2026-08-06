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

## CHECKPOINT — the frozen gauntlet, EXECUTED (2026-08-04, after P5; the instrument predates the data)

**Test A — COMPRESSION, by replay over all eight read joints** (3 post-hoc + 5 preregistered; an
exception = a joint whose observed core law the basis cannot classify without a per-module patch):

    joint          observed core law                        B-A (seam-type)      B-B (role×substrate)
    heightfield    canon; identity ⊥ presentation           representation ✓     measure × representation ✓
    jurisdiction   lattice predicate ⊥ certificate          admission ✓          police × canonical state ✓
    layertheorem   one-way authority flow                   propagation ✓        EXCEPTION (no flow axis)
    opcost   (P1)  cost ≤ envelope, refuse over             cost ✓               measure counts + police budget ✓
    terraform(P2)  chunked ≡ monolith + anamnesis, CAS      representation ✓     police CAS × measure equiv ✓
    stance   (P3)  admission-FORM gate; blocking MEASURED   EXCEPTION (axis      measure × terrain ✓ (native)
                                                            silent on semantics)
    warden   (P4)  claim-admission, typed refuse; 2 certs   admission ✓          police × claims ✓
    budget   (P5)  well-founded descent + COMPOSITION       EXCEPTION            EXCEPTION
                                                            (composition)        (composition)
    exceptions:                                             2                    2
    VERDICT: BOTH FAIL Test A's zero-exception bar. Neither is a basis; both are structured lists.

**Test B — PREDICTION**: both bases froze one derivation each for P5 → partially confirmed (C-AB).
The cost pattern recurred preregistered (opcost → budget) under B-A's reading. Weak pass, both.

**Test C — STABILITY**: unique families invoked after each preregistered READ: 1, 2, 3, 3, 4 →
G(n) = 1, 1, 1, 0.75, 0.8. New-family arrivals per READ (v_D) = 1, 1, 1, 0, 1. G is NOT decreasing
(composition arrived at joint five); two consecutive zero-arrival READs never occurred. FAIL — the
architecture is still teaching new families at the frontier; the continuation criterion says run 2
proceeds.

**Test D — COUNTERFACTUAL**: one instance adjudicated PASSED — P4's refuse-not-measure semantics are
traceable to P3's residual, not to warden's role prose ("anti-cheat" does not entail the semantics).

**CHECKPOINT VERDICT (from the frozen outcome space): NO-PROMOTION.** Promotion required surviving
all four tests; both rivals failed A and C. The negative is recorded, no abstraction is minted, and
the basis question stays OPEN — which the evidence demands: promoting a basis while G still rises
would freeze a model mid-enrichment. The rivals survive as CANDIDATES via mutation:

    lineage: B-A → B-A′   reason: the P5 composition residual. appeared: a composition axis (laws
                          carry a composition signature: subadditive-priced / exact-on-disjoint).
                          disappeared: nothing. REPLAY: 1 exception remains (stance semantics —
                          deliberately NOT repaired this rung; one mutation per residual, and the
                          semantics strain awaits its own recurrence).
    lineage: B-B → B-B′   reason: the same residual. appeared: the same composition axis grafted
                          onto role×substrate. disappeared: nothing. REPLAY: 1 exception remains
                          (layertheorem's flow — no role/substrate cell carries direction).
    Pareto panel (exceptions | predictions-made | confirmed | unexplained-residuals):
        B-A  2|1|partial|1   →  B-A′ 1|1|partial|0   (dominates parent)
        B-B  2|1|partial|1   →  B-B′ 1|1|partial|0   (dominates parent)
    Both mutants REPLAY-survive and DOMINATE their parents. Replay can only kill, never promote
    (the mutation was derived from the residual it explains): each mutant's Test B discharges only
    via FORWARD frozen predictions at run 2's freezes. B-C (composition-primary) is NOT minted —
    one observation cannot found a rival (L3); it becomes mintable if composition recurs.

**Run-2 instruments, decided here** (proposed across the session, adjudicated at the checkpoint):
    ADOPTED — the Marangoni interface atom: Γ(e) = |Φ(u)−Φ(v)| over the import graph from
      ATTENTION-INDEPENDENT integer components only; the SELECTOR STAYS in-degree (L59) so the
      test cannot self-fulfill; falsifier per the Discovery Interface Theorem: an interface that
      stays maximal under the frozen selector while adjacent residual density rises is structurally
      active; residual emergence indistinguishable from background falsifies it for that edge.
    ADOPTED — the SIGNED continuation rule: track v_D's sign (new-family arrivals per READ);
      direction only, no numeric thresholds (thresholds at n=5 are numerology).
    ADOPTED — graded credences: run-2 freezes attach integer-percent credences to each frozen
      outcome class, Brier-scored at resolution (a measurement of the predictor, not a fused
      verdict; P5 scored at implicit 50/50/0 would have priced the composition blindness exactly).
    ADOPTED — the coupling coefficient (URDRQPR1 §5): C(A,B) = |F_A ∩ F_B| / |F_A ∪ F_B| over
      theorem-family feature sets — computed as a checkpoint statistic (descriptive at n=8:
      does cost co-occur with typed refusal? composition with admission?), and FALSIFIABLE across
      run 2 via frozen co-occurrence predictions.
    ADOPTED — the frozen weight-update rule (URDRQPR1 §6–7): a running posterior over the rival
      bases, updated per-resolution by a rule frozen at run 2's opening (Brier-scored). REPORTING
      ONLY — the weights never decide anything; promotion runs exclusively through the gauntlet
      (panel ≠ scalar).
    DEFERRED — URDRQPR1 as a module, with two findings recorded at adjudication:
      (1) THE BOOLEAN IDENTITY — at Boolean feature granularity the projection formalism IS the
          executed replay table: ‖r‖² = the Test-A exception count (verified against budget:
          x = {cost, flow, composition}, P_{B-A} spans {rep, adm, prop, cost}, ‖r‖² = 1 = the
          recorded exception), and the Organizational Projection Theorem restates this rung's
          mutation-admissibility rule clause for clause. By L5 it renames executed machinery;
          the module earns existence only when a RICHER embedding demonstrably out-predicts the
          plain exception count — the proposal's own closing criterion, adopted as the bar.
      (2) THE DICTIONARY HORIZON — a feature must be NAMED before it can be a coordinate, so
          r = x − P_B x can only point within the span of recognized features. Pre-P5, budget
          would have embedded as {cost, flow} and ρ would have read SMALL at the exact moment
          reality carried the run's largest unexplained structure; same for refuse ≠ measure
          pre-P3. Any future URDRQPR1 carries this as its does_not_show: small ρ certifies the
          basis explains NAMED structure, never that nothing unnamed remains — the out-of-
          dictionary channel is and stays L60's mandatory catch-all class, which by construction
          cannot be embedded. `integrity ≠ truth`, in vector clothing.
    DEFERRED — the synthesis/tournament engine (earns when hand-mutation patterns recur in
      lineage); URDRDF1 as a module (the umbrella enters as its atoms only); B-C (above).

**Run 2 opens next**: target selection by in-degree under L59; the mutants' forward predictions,
the interface atom's Γ table and edge predictions, and graded credences are frozen TOGETHER at the
first run-2 freeze, before any seal breaks. Continuation per the signed rule; the next checkpoint
fires when the frozen continuation criterion is met, and this gauntlet re-runs with the enlarged
history.

## RUN 2 — OPENING FREEZE (2026-08-04; everything below binds BEFORE wire.py is read)

**URDRMT1 adopted — modus tollens as elimination semantics.** The checkpoint verdict was already MT
in contrapositive form (complete → four passes; A∧C failed; ∴ ¬complete); what MT adds is that
`fails_if` becomes an EXECUTABLE KILL: a rival whose frozen refutation condition realizes is REMOVED
from the admissible space, not down-weighted. Kill conditions, frozen and decidable:
  - B-A′ is ELIMINATED when TWO run-2 resolutions land R-O naming a new family axis (its fails_if —
    "a sixth independent family is needed" — realized; composition was the fifth).
  - B-B′ is ELIMINATED when a SECOND flow-type exception accrues (layertheorem is the standing
    first; its fails_if — role/substrate cells cannot carry direction — realized twice).
  - the interface instrument is ELIMINATED (for this Φ) when run-2 residual emergence at
    high-Γ-adjacent joints is ≤ the rate at non-high joints over the full run.
  BOUNDARY (Duhem–Quine, recorded): a refuted prediction eliminates the CONJUNCTION of basis +
  auxiliaries (classification, dictionary, selector); each resolution records where the failure
  lodged, and a kill fires only when it lodges in the basis.

**URDRQOE1 adjudicated.** (1) The organizational-entanglement inequality R(A)+R(B) ≥ R(A,B) is
residual SUBADDITIVITY — structurally identical to budget's composition law: the axis the rivals
lack keeps reappearing as a law of the epistemic layer itself. Recorded as a rhyme (n=1, not
promoted). (2) The organizational Hamiltonian H = R+E+C is scalar fusion — REFUSED (panel ≠
scalar); the terms remain panel axes. (3) The decoherence law (dim R monotonically decreases under
successful replay) is REFUTED BY THE RUN'S OWN HISTORY via MT: the dictionary grew at P3 and P5.
Its conditional form — monotone within a FIXED dictionary — survives, and is the dictionary-horizon
finding restated. (4) The L1 integer distance is house-compatible and waits with the embedding.

**The weight posterior, frozen.** w(B-A′) = w(B-B′) = 1/2. Update rule (frozen now, applied at each
resolution): multiply each rival's weight by its frozen likelihood on the REALIZED class,
renormalize; Brier scores reported alongside. REPORTING ONLY — promotion and elimination run through
the gauntlet and MT, never through w.

**The interface instrument, frozen numbers** (Φ = total degree over import edges; import lines only;
103 modules, 242 edges): top-decile threshold Γ ≥ 17; high-interface-adjacent set (26 modules):
chunkload chunkstate commute cpredict crosswarden dirward driftgaze drive fpcap gaze glide hand
heightfield layertheorem meshattest panelight predict quintessence resurrect sealframe sealwrit
storm testament traj view_witness wireattest. CAVEAT recorded: under this Φ the top edges are
dominated by heightfield's hub contrast — the instrument tests THIS Φ's interfaces, nothing more.
PREDICTION (direction-only, comparative): run-2 residual emergence concentrates at high-Γ-adjacent
joints. Run-1 base rate: 2 of 5. **wire is NOT high-adjacent (max incident Γ = 16, one under
threshold — borderline noted): the instrument predicts BACKGROUND for P6.**

### P6 — `wire`
    state:            PREREGISTERED
    target:           wire — top of the briefless frontier by the FROZEN selector (in-degree 5;
                      lease 4, horizon 4). L59: import lines only, body unread, no history scan.
    provenance:       role-only — the index line "EQUAL-OR-REFUSE REPLICATION (T3.47, wire-phase
                      opener)" (URDRWIR1). Ambient disclosed: panewire ("THE WIRED WINDOW", T3.53)
                      is family; stage names wireattest / wirephase_placement appear in gate logs.
                      wire.py and its git history are UNREAD.
    rival predictions (both frozen; they disagree about the central row):
      B-A′:           PROPAGATION-central — replication is state TRANSPORT: the central row
                      certifies source-authority / direction / ordering of replicated state, with
                      equality as transport's verification instrument.
      B-B′:           POLICE × REPRESENTATION-central — an equality-ADJUDICATION predicate: a
                      replica equal to the source ADMITS, divergence typed-REFUSES — the
                      jurisdiction pattern pointed at replicas.
    outcome partition (EXHAUSTIVE, L60):
                      P6-C-A   transport/propagation law central (B-A′)
                      P6-C-B   equality-adjudication predicate central (B-B′)
                      P6-C-AB  one central row certifies both inseparably
                      P6-R-M   measure-not-refuse semantics central (the stance pattern)
                      P6-R-O   OTHER — catch-all; names a new axis if one appears
    credences (frozen, integer %):
                      author:  C-A 30 · C-B 30 · C-AB 20 · R-M 5 · R-O 15
                      B-A′ likelihoods: 55 · 15 · 20 · 3 · 7
                      B-B′ likelihoods: 15 · 55 · 20 · 3 · 7
    secondary (META — exhaustive): M-0 ∈{C-A,C-B,C-AB} with ≥1 unnamed dimension · M-1 same set,
                      none · M-2 ∈{R-M,R-O}. The meta predicts ¬M-1 (the signature is 5 for 5).
    interface instrument: predicts BACKGROUND (wire not high-adjacent) — this resolution feeds the
                      instrument's comparative cell, and its Brier is scored like the rivals'.
    residual_format:  if R-M / R-O — (predicted: A′=<transport> B′=<equality-adjudication>;
                      observed: <actual>; delta: <R-M | R-O:<named-after-reading>>).
    witness:          the git commit introducing this row — dated before wire.py is read.

### P6 — resolved: **P6-C-AB (the second consecutive tie)** · meta: **M-0 (6 for 6)**
    read:             2026-08-04, run 2's first blind READ (Rung H). Classified from the LIVE
                      `wire*` rows.
    observed:         the central row (`wire-replicate`) again certifies BOTH rivals inseparably:
                      per-step BYTE EQUALITY of replica and authority — the client admits each
                      104-byte essence-record under the authority's own laws, "a verifier, not a
                      believer", every refusal typed and leaving the replica byte-identical
                      (B-B′'s adjudication) — fused with DERIVED-NEVER-SHIPPED transport and
                      ordering law (B-A′): in-region order is STRUCTURAL (terraform's parent chain
                      on the wire; duplicates refuse at-most-once for free), cross-region order is
                      provably IRRELEVANT (RAN-0 nullity as the wire's interleaving invariance).
    the tie as data:  TWO consecutive C-AB resolutions are input to the adopted coupling
                      coefficient: the police/equality axes and the transport/ordering axes have
                      co-occurred in every replication-adjacent central law read so far. A COMPOUND
                      basis element ("verified essence-replication": adjudicated admission +
                      derived transport + byte-equality as one pattern) becomes a MINTABLE mutation
                      if a third C-AB accrues (L3 — two occurrences noted, not promoted).
    unnamed structure (M-0): (1) "THE MODULE MINTS NOTHING" — pure composition, each absence a
                      theorem already paid for (no snapshots ← the frame property; no sequence
                      numbers ← the chain law + nullity; the filter ← the essence's spatial axis).
                      The COMPOSITION AXIS RECURRED — and the mutants' P5-derived axis classified
                      it correctly ON ITS FIRST FORWARD OUTING: the parents would have logged an
                      exception here; B-A′/B-B′ did not. The mutation paid off prospectively.
                      (2) the INTEREST law — the filter is sound AND necessary-with-DETECTION
                      (a withheld relevant update is caught by the next admission's CAS; drift
                      refused, never absorbed): an attention axis neither rival carries. Noted,
                      not minted (L3). (3) refuse-purity (never half-applies) and at-most-once-
                      for-free — refinements of refusal semantics.
    weights:          realized class C-AB — both rivals' frozen likelihoods equal (20): posterior
                      UNCHANGED at 1/2, 1/2. Brier: B-A′ 0.9708, B-B′ 0.9708, author 0.8450.
                      Lesson recorded for the next freeze: C-AB has realized twice while credenced
                      at 20% — the tie class is systematically underweighted; future credences
                      must price the co-occurrence the coupling data now shows.
    instrument cell:  the interface atom predicted BACKGROUND for wire (not high-adjacent, max
                      Γ = 16) and was RIGHT: no new family emerged (composition recurred — already
                      in the mutants' dictionary; interest noted-not-minted). First cell: non-high
                      joint, no emergence.
    kills:            none fired — the resolution is C-AB (not R-O), no staked zero realized, no
                      second flow-type exception.
    census:           run-2 v_D = 0 (first zero-arrival READ). The signed continuation rule needs
                      TWO consecutive zeros to stop: run 2 CONTINUES.
    contamination:    none — L59, seventh application; the freeze commit predates the READ.

### P7 — `horizon`
    state:            PREREGISTERED
    target:           horizon — frontier tie at in-degree 4 (horizon, lease); the FROZEN tie-break
                      (lexicographic ascending) selects horizon. L59: import lines only, body
                      unread, no history scan.
    provenance:       role-only — the index line "Rollback-horizon reconcile window (T3.32)"
                      (URDRLAT1); ambient disclosed: horizon sits in the Stage-H latency family
                      ("opcost/govern/priogov/horizon/slo/clslo for time"); "rollback" associates
                      with the reconcile arc (splice/predict) and rollstore. horizon.py and its git
                      history are UNREAD.
    stakes:           v_D stands at ONE consecutive zero. If this READ mints no new family, the
                      signed continuation rule STOPS run 2 and checkpoint 2 fires on the enlarged
                      history.
    rival predictions (frozen; the disagreement is arithmetic-vs-adjudication):
      B-A′:           COST-central — the window is a bounded ENVELOPE on the time axis: reconcile
                      depth ≤ horizon, the opcost pattern pointed at rollback reach (the cost
                      family's third preregistered instance if confirmed).
      B-B′:           POLICE × TIME-CLAIMS central — the window is an ADMISSION predicate on
                      history: a reconcile claim within the horizon admits, beyond it typed-REFUSES
                      (jurisdiction on the time axis).
    outcome partition (EXHAUSTIVE, L60):
                      P7-C-A   envelope/bound arithmetic central (B-A′)
                      P7-C-B   claim-adjudication on the time axis central (B-B′)
                      P7-C-AB  one central row certifies both inseparably
                      P7-R-M   measure-not-refuse semantics central
                      P7-R-O   OTHER — catch-all; names a new axis if one appears
    credences (frozen, integer % — the P6 lesson APPLIED: the tie class priced at the measured
                      co-occurrence, 20 → 30):
                      author:  C-A 25 · C-B 25 · C-AB 30 · R-M 10 · R-O 10
                      B-A′ likelihoods: 45 · 15 · 30 · 4 · 6
                      B-B′ likelihoods: 15 · 45 · 30 · 4 · 6
    secondary (META — exhaustive): M-0 ∈{C-A,C-B,C-AB} with ≥1 unnamed dimension · M-1 same set,
                      none · M-2 ∈{R-M,R-O}. The meta predicts ¬M-1 (the signature is 6 for 6).
    interface instrument: horizon is NOT in the frozen high-Γ set → BACKGROUND predicted (cell 2).
    residual_format:  if R-M / R-O — (predicted: A′=<time-envelope> B′=<time-adjudication>;
                      observed: <actual>; delta: <R-M | R-O:<named-after-reading>>).
    witness:          the git commit introducing this row — dated before horizon.py is read.

### P7 — resolved: **P7-C-A (B-A′ right — the first discrimination)** · meta: **M-0 (7 for 7)** · RUN 2 CLOSES
    read:             2026-08-04, run 2's second blind READ (Rung I). Classified from the LIVE
                      `horizon*` rows.
    observed:         the central row (`horizon-bound`) certifies the ENVELOPE: an admitted
                      reconcile's depth ≤ H, and the worst-case reconcile window EQUALS H — a tight
                      bound, not an inequality with slack. The refusal (`horizon-refuse`: a rollback
                      deeper than the horizon is typed HORIZON-REFUSE — a stale correction is never
                      served late) is the ENFORCEMENT of the envelope, exactly as in opcost. The
                      DISCRIMINATOR the run has now earned, stated as a reusable rule: a predicate
                      that reads a MEASURED MAGNITUDE against a DECLARED CEILING is the cost
                      pattern (opcost, budget-exhaustion, horizon); one that reads STATE-LAWFULNESS
                      is admission (jurisdiction, warden). Depth is computed (n − k via cpredict),
                      never claimed; H is a policy number. B-A′'s prediction confirmed — the COST
                      FAMILY'S THIRD PREREGISTERED INSTANCE (L3 recurrence satisfied for cost).
    unnamed structure (M-0): (1) the OPODIS dependency — the envelope EXISTS BECAUSE reconciliation
                      is byte-exact (`horizon-reconstruct`: δ = 0 on admit): byte-exactness
                      collapsed every cost of a late input EXCEPT depth, so the window law RIDES on
                      the representation seam. Neither rival named the dependency. (2) pure
                      composition again — horizon mints nothing (cpredict's reconcile + opcost's
                      counts), the mutants' composition axis classifying it natively a SECOND time.
    weights:          realized C-A — B-A′ likelihood 45, B-B′ 15: posterior w(B-A′) = 3/4,
                      w(B-B′) = 1/4. THE FIRST SEPARATION. Brier: B-A′ 0.4202, B-B′ 1.0202,
                      author 0.7350.
    instrument cell:  background predicted (horizon not high-adjacent) — RIGHT again (no new
                      family). HONEST NOTE: both run-2 cells are non-high joints; the comparative
                      claim still has an EMPTY high-Γ cell — the instrument is consistent, not yet
                      tested on the side that could falsify it.
    kills:            none fired (C-A is no rival's staked-zero or fails_if class).
    census:           run-2 v_D = 0, 0 — TWO consecutive zero-arrival READs: the signed
                      continuation rule STOPS RUN 2 at n = 2. CHECKPOINT 2 fires next, over ten
                      read joints, with the gauntlet re-run, the coupling table updated, the weight
                      posterior at 3/4 vs 1/4, and the cost family carrying three preregistered
                      instances.
    contamination:    none — L59, eighth application; the freeze commit predates the READ.

## CHECKPOINT 2 — the gauntlet re-run over TEN joints (2026-08-04, after run 2 closed at v_D = 0, 0)

**Test A — COMPRESSION, by replay over all ten read joints** (checkpoint 1's eight + wire + horizon;
the candidates are the mutants — the parents are retired lineage):

    joint          B-A′ (seam-type + composition)       B-B′ (role×substrate + composition)
    heightfield    representation ✓                      measure × representation ✓
    jurisdiction   admission ✓                           police × canonical state ✓
    layertheorem   propagation ✓                         EXCEPTION (standing — no flow axis)
    opcost         cost ✓                                measure counts + police budget ✓
    terraform      representation ✓                      police CAS × measure equivalence ✓
    stance         EXCEPTION (standing — semantics)      measure × terrain ✓
    warden         admission ✓                           police × claims ✓
    budget         cost + composition ✓ (REPAIRED)       police × resource + composition ✓ (REPAIRED)
    wire           propagation+representation compound ✓ police × replica-claims compound ✓
    horizon        cost ✓ (the confirmed discrimination) police × measured-depth ✓ (classifies,
                                                         though its central-row prediction was wrong)
    exceptions:    1 (stance)                            1 (layertheorem)
    VERDICT: both still fail the zero-exception bar — each carries exactly the exception the OTHER
    repairs natively. The failure is no longer diffuse; it is a pointer.

**Test B — PREDICTION**: B-A′ PASSES — P7 was a full basis-derived frozen discrimination, confirmed
(plus the P6 forward classification of mints-nothing composition). B-B′ WEAK — one partial (P6),
one refuted central-row call (P7). **Test C — STABILITY**: families after P1..P7 = 1,2,3,3,4,4,4 →
G = 1, 1, 1, .75, .8, .667, .571 — STRICTLY DECREASING over the last three READs; v_D ended 0, 0.
PASSES. **Test D — COUNTERFACTUAL**: two instances now — P4 (refuse≠measure from the residual, not
prose) and P7 (both rivals held the same role prose and predicted DIFFERENTLY; the confirmed call is
traceable to B-A′'s cost axis, by construction of the experiment). PASSES.

**CHECKPOINT VERDICT (frozen outcome space): NO-PROMOTION — again, and for the last simple reason.**
B-A′ survives B, C, D and fails A by exactly one localized exception. No kill fired (MT conditions
unmet: one flow exception, zero R-O resolutions in run 2).

**The MERGE mutation — minted, because the convergence is now bidirectional.** B-A′'s one exception
(stance) is repaired by B-B′'s semantics axis; B-B′'s one exception (layertheorem) is repaired by
B-A′'s family axis. Two rivals that each patch precisely the other's failure are one basis seen from
two sides:

    lineage: B-A′ + B-B′ → B-M ("input × semantics")
      axes:      predicate-INPUT family {representation · admission (state-lawfulness) ·
                 propagation (flow) · cost (measured magnitude vs declared ceiling)}
                 × SEMANTICS {refuse (police) · measure · structural-invariant}
                 + the composition signature.
                 The P7 discriminator is B-M's first axis, verbatim; P3's residual is its second.
      appeared:  the semantics axis (from B-B′); the structural-invariant value (earned by
                 layertheorem: a theorem, not a gate). disappeared: nothing.
      REPLAY over ten joints: ZERO exceptions — stance = cost-input × measure; layertheorem =
                 propagation × structural-invariant; horizon = cost × refuse; wire = compound ×
                 refuse; budget = cost × refuse + composition. First candidate to replay clean.
      HONEST LIMIT: B-M was assembled FROM all ten observations — replay can only kill, never
                 promote (the retrofit rule). B-M has ZERO forward confirmations; its promotion
                 path runs exclusively through run-3 frozen predictions.

**Weights (rule frozen at entry):** a new entrant takes 1/3; incumbents split the remaining 2/3 by
the standing posterior → w(B-M) = 1/3, w(B-A′) = 1/2, w(B-B′) = 1/6.

**Coupling table (adopted instrument, first computation, 10 joints):** composition co-occurs with
cost in 2 of its 3 sightings (budget, horizon) and with replication-compounds once (wire);
refuse-semantics co-occurs with EVERY family except representation-alone; the two C-AB ties both
paired {adjudication, transport} — the pairing B-M's product structure now explains rather than
records. **Interface instrument:** both run-2 cells were non-high joints (both correct); the
high-Γ cell is STILL EMPTY — and the run-3 frontier joint (`drive`, in-degree 3, lexicographic
tie-break over govern/liveness) IS in the frozen high-Γ set: P8 finally tests the instrument's
falsifying side.

**RUN 3 OPENS NEXT** with three candidates (B-M must out-predict its parents, not just out-replay
them), the epistemic continuation criteria unmet (compression holds only for a candidate with no
forward record — the basis question stays open), and P8 on `drive` as the next freeze.

### ERRATUM (2026-08-04, pre-P8): checkpoint 2's closing line named `drive` as run 3's frontier
    joint. WRONG — the frozen selector, recomputed at freeze time, says `lease` (in-degree 4)
    stands alone above drive (3). The error is instructive and recorded: drive was ATTRACTIVE
    because it sits in the interface instrument's high-Γ set — the exact operator drift toward
    instrument-convenient targeting the frozen-selector design exists to forbid. The selector
    caught it because selection is RECOMPUTED, never carried from prose. The instrument's high-Γ
    cell honestly stays empty until a high-Γ joint tops the frontier on its own. The hainuwele
    sentence is corrected in this rung's commit.

### P8 — `lease` (run 3's opening freeze; THREE candidates, every outcome moves the tournament)
    state:            PREREGISTERED
    target:           lease — top of the briefless frontier by the frozen selector (in-degree 4;
                      drive/govern/liveness at 3). L59: import lines only, body unread, no history
                      scan.
    provenance:       role-only — the index line "The standing lease (T3.43) — RAN-0's temporal
                      extension" (URDRLSE1); AGENTS.md ambient, disclosed: "`lease` (proof as an
                      interval)"; "lease interval arithmetic" named alongside the cost cluster
                      (storecost/opcost/slo); Phase M's "certified authority migration as lease
                      transfer". Chain position rannull → lease → testament. lease.py and its git
                      history are UNREAD.
    rival predictions (the tournament's first three-way freeze):
      B-A′ + B-B′:    the parents CONVERGE here (their axes do not distinguish this target —
                      honest, and itself evidence for the merge): the central row is an
                      INTERVAL-ADMISSION gate — a claim admits iff within the claimant's standing
                      lease, expired or foreign claims typed-refuse (jurisdiction on the temporal
                      holder).
      B-M:            distinctively prices its STRUCTURAL-INVARIANT value: the central row is an
                      EXCLUSIVITY / TRANSFER invariant — no-overlap (at most one holder per region
                      per moment), no-gap or clean-handoff on transfer, disjoint-lease operations
                      commuting (RAN-0's nullity lifted to time as a STRUCTURAL law), with the
                      admission gate as its guard.
    outcome partition (EXHAUSTIVE, L60):
                      P8-C-R     interval-admission gate central, refuse semantics
                      P8-C-INV   exclusivity/transfer invariant central (structural; gates guard)
                      P8-C-ARITH interval arithmetic/envelope central (the cost pattern on time)
                      P8-R-M     measure-semantics central
                      P8-R-O     OTHER — catch-all
    credences (frozen, integer %):
                      author:  C-R 35 · C-INV 25 · C-ARITH 20 · R-M 5 · R-O 15
                      B-A′:    C-R 55 · C-INV 15 · C-ARITH 15 · R-M 5 · R-O 10
                      B-B′:    C-R 55 · C-INV 15 · C-ARITH 15 · R-M 5 · R-O 10
                      B-M:     C-R 35 · C-INV 35 · C-ARITH 15 · R-M 5 · R-O 10
    MT kills (frozen): B-A′ ELIMINATED if R-M realizes (a SECOND measure-semantics central row its
                      taxonomy cannot express — stance was the first). B-B′ ELIMINATED if C-INV
                      realizes with a classification requiring the structural-invariant cell it
                      lacks (its SECOND structural exception — layertheorem was the first). B-M has
                      no standing exception; its kill is inherited fails_if only.
    secondary (META — exhaustive): M-0 / M-1 / M-2 as before; the meta predicts ¬M-1 (7 for 7).
    interface instrument: lease is NOT in the frozen high-Γ set → BACKGROUND predicted (cell 3);
                      the high cell remains empty, per the erratum above.
    residual_format:  if R-M / R-O — (predicted: parents=<interval-admission> B-M=<exclusivity
                      invariant>; observed: <actual>; delta: <R-M | R-O:<named-after-reading>>).
    witness:          the git commit introducing this row — dated before lease.py is read.

### P8 — resolved: **P8-C-INV — B-M's first forward confirmation** · **B-B′ ELIMINATED (MT)** · meta: **M-0 (8 for 8)**
    read:             2026-08-04, run 3's first blind READ (Rung K). Classified from the LIVE
                      `lease*` rows.
    observed:         the module names its own keystone and the central row certifies it:
                      `lease-interval` — INTERVAL COMMUTATION (the leased edit admits at EVERY
                      insertion position of a disjoint-authority chain, bytes unchanged, ONE final
                      head — "RAN-0's diamond, iterated without re-proving": the nullity lifted to
                      time as a STRUCTURAL law) plus AMORTIZATION (the cheap admission equals the
                      full global reproof bit-for-bit at every interval head — the proof paid once
                      at mint, admissions inheriting it). The admission machinery (`lease-validity`
                      state-free in one manifest slot; `lease-refuse`, six-way typed) is the GUARD,
                      exactly as B-M's frozen wording had it. Self-expiry completes the exclusivity
                      content: a lease dies at its own use, renewal is the chain, the chain is the
                      region's write history.
    tournament:       B-M's structural-invariant value did distinctive, confirmed, forward work —
                      the merge out-predicted its parents at the first opportunity (C-INV 35 vs
                      their 15). MT KILL FIRED: classifying an order-free structural law requires
                      the invariant cell B-B′ lacks — its second structural exception (layertheorem
                      standing) — B-B′ IS ELIMINATED from the admissible space per the frozen
                      condition. B-A′ survives with a wrong central-row call (C-R 55, Brier 1.06)
                      and a strained-but-expressible classification (order-free files under
                      propagation, no new axis). The structural-invariant axis gains its second
                      member (layertheorem, lease).
    weights:          Bayes on C-INV (15/15/35), then MT-removal of B-B′, renormalized:
                      w(B-M) = 0.61, w(B-A′) = 0.39. Brier: B-M 0.58, B-A′ 1.06, B-B′ 1.06
                      (final), author 0.75.
    unnamed structure (M-0): THE LOST-UPDATE LAW — the run's first CROSS-LAW HAZARD: anamnesis
                      (P2's celebrated virtue — the store retains old chunks forever) COMPOSES
                      ADVERSELY with admission: fetching by the lease's own digest would find stale
                      bytes, apply cleanly, and silently revert the interval's edits. The repair is
                      two individually-redundant, jointly-load-bearing layers (valid()'s cheap
                      manifest check + the shard CAS), with plants proving both-gutted lands the
                      lost update. Composition's ADVERSE face: two certified virtues composing into
                      a hazard — an enrichment of the composition axis, noted not minted. Also
                      unnamed: state-free O(1) validity; single-shot self-expiry.
    instrument cell:  background predicted (lease not high-adjacent) — RIGHT (3 for 3, all cells
                      still non-high; the high cell stays empty per the erratum).
    census:           v_D = 0 (no new family; the composition axis absorbs the hazard as
                      enrichment). Run 3 continues (one zero; the rule needs two).
    contamination:    none — L59, ninth application; the freeze commit predates the READ.

## BATCH FREEZE — P9 + P10 + P11 (2026-08-04; the first multi-joint freeze, all sealed before any READ)

**Batch rules, frozen**: targets are the entire in-degree-3 frontier in selector order (drive,
govern, liveness — L59, import lines only, no history scans, bodies unread except as disclosed).
Evaluation order = selector order. Weights update sequentially on SCORING joints only. If the
stopping rule (two consecutive v_D zeros; currently at ONE from P8) fires mid-batch, run 3 CLOSES
at that joint but the batch completes — post-closure resolutions are read, briefed, and recorded
as post-closure. MT kills: standing conditions, plus one frozen here: **B-A′ is ELIMINATED if P9
resolves measure-semantics-central (C-M)** — its second inexpressible measure row (stance was the
first).

### P9 — `drive` (SCORING; the interface instrument's FIRST high-Γ cell)
    provenance:       role-only + disclosed ambient: index "Certified movement TRANSCRIPT (T3.11)"
                      (URDRDRIVE1); the movement chain stance → gaze → drive → traj; warden's "the
                      drive/glide step law (Δground ≤ MAX_STEP)"; glide's brief evidence "floored
                      glide == drive over 640 cases" (drive is glide's discrete reference). Body
                      and history UNREAD.
    predictions:      B-A′ — REPRESENTATION-central: the certified transcript as an identity law
                      (replay reproduces the transcript byte-exact, digest-bound — the canon
                      pattern). B-M — splits its mass: transcript-identity as
                      representation × structural-invariant OR the stance cell
                      (cost-input × measure) for the driven walk.
    partition:        C-REP (transcript/replay identity central) · C-M (driven-walk measurement
                      central — the stance cell; KILLS B-A′) · C-R (gate-refuse central) ·
                      C-AB (identity + measurement fused in one row) · R-O (catch-all).
    credences:        author: C-REP 30 · C-M 25 · C-R 10 · C-AB 20 · R-O 15
                      B-A′:   C-REP 45 · C-M 15 · C-R 15 · C-AB 15 · R-O 10
                      B-M:    C-REP 30 · C-M 30 · C-R 5  · C-AB 25 · R-O 10
    instrument:       drive IS in the frozen high-Γ set — the FIRST high cell: ELEVATED emergence
                      predicted (a new family or R-class surprise). A clean confirmation with no
                      new structure logs the high cell as no-emergence — evidence AGAINST the
                      interface hypothesis. Either way the empty cell finally fills.

### P10 — `govern` (NON-SCORING — contamination declared)
    contamination:    DISCLOSED IN FULL: govern's gate-stage docstring was read during Rung A (it
                      sits directly below opcost's stage): "the opcost envelope turned into LIVE
                      enforcement — admit a FIFO prefix within the tick op-budget, defer the rest,
                      refuse a single over-budget actor … never-overrun … progress-wait …
                      admitted + deferred == all". The core law is effectively KNOWN. Per the
                      frozen batch rule this joint moves NO weights and its resolution carries no
                      tournament evidence — it is read for the brief pass and the record.
    for the record:   expected: cost-input × refuse central (the envelope enforced live), with the
                      progress/starvation content (progress-wait; conservation) as the thing to
                      WATCH — if the central row is the scheduler's progress law rather than the
                      budget enforcement, that hints a SCHEDULING axis no basis carries.
    partition:        same five-class shape (C-COST · C-SCHED · C-R · C-AB · R-O), non-scoring.

### P11 — `liveness` (SCORING)
    provenance:       role-only — index: "Denial versus outage — the crashed-slow
                      indistinguishability, authenticated to clockauth" (URDRLIV1); the authority
                      arc's ladder line ("the horizon cannot be moved by the party it constrains");
                      ambient disclosed: budget's docstring cites "the same well-founded descent on
                      (ℕ, <) that liveness needed one rung earlier". Body and history UNREAD.
    predictions:      B-A′ — COST-central: a timeout envelope (declared down iff silence exceeds a
                      declared horizon — magnitude-vs-ceiling on the time axis). B-M —
                      distinctively prices its invariant value again: the CRASHED-SLOW
                      INDISTINGUISHABILITY itself as the central law (an impossibility theorem —
                      structural-invariant), with the authenticated horizon as guard.
    partition:        C-COST (timeout-envelope central) · C-INV (indistinguishability theorem
                      central) · C-R (refusal-adjudication central) · C-AB · R-O.
    credences:        author: C-COST 25 · C-INV 30 · C-R 10 · C-AB 20 · R-O 15
                      B-A′:   C-COST 45 · C-INV 15 · C-R 15 · C-AB 15 · R-O 10
                      B-M:    C-COST 25 · C-INV 40 · C-R 5  · C-AB 20 · R-O 10
    instrument:       liveness is NOT in the high-Γ set → background predicted.

    secondary (META, batch-wide, exhaustive): per scoring joint, M-0/M-1/M-2 as before; the meta
                      predicts ¬M-1 on BOTH scoring joints (the signature is 8 for 8).
    witness:          the git commit introducing these rows — dated before any of the three
                      modules is read.

### P9 — resolved: **C-REP (B-A′ right)** · **RUN 3 CLOSES** · instrument's first high cell CONTRADICTS
    observed:         drive's two NOVEL exact facts are transcript identity: DETERMINISM (the
                      trajectory is a pure fold over the input log — "the netcode lockstep witness,
                      on terrain") and TAMPER-EVIDENCE (the digest binds start + log + trajectory;
                      "input integrity is a digest equality, not a promise"). The step law is
                      explicitly INHERITED from stance as the fold's per-cell gate (composition).
                      Central row `drive-properties`; the kill did not fire (C-M did not realize).
    tournament:       B-A′ right at 45 vs B-M's 30 — the incumbent wins a joint; weights tighten
                      to B-M 0.51 / B-A′ 0.49. Brier: B-A′ 0.38, B-M 0.655, author 0.625.
    unnamed (M-0):    input-integrity as anti-cheat (a forged, replayed, or reordered COMMAND moves
                      the digest — warden polices claimed trajectories, drive makes the input log
                      itself tamper-evident); gait as derived-in-input (sprint = 2 cells, not a
                      pose axis, per-cell gated); the WHERE/WHEN seam with gaze.
    instrument:       the FIRST high-Γ cell: ELEVATED emergence predicted, CLEAN CONFIRMATION
                      delivered — the cell contradicts the interface hypothesis. Cells now: high
                      1 (0 emergence), non-high 3 (0 emergence) — the comparison is degenerate
                      (nothing has emerged anywhere), so the MT kill does not fire on 0 ≤ 0 with
                      n = 1, but the instrument's only directional call on its own ground was
                      wrong. Checkpoint 3 adjudicates.
    census:           v_D = 0 — the SECOND consecutive zero: RUN 3 CLOSES AT DRIVE. govern and
                      liveness proceed as post-closure batch reads per the frozen rule.

### P10 — resolved (NON-SCORING, post-closure): the disclosed law, plus a SCHEDULING-axis sighting
    observed:         exactly as the contamination predicted — "refuse-or-defer, never overrun;
                      serve-in-order, never starve": `govern-never-overrun` (spent ≤ budget across
                      budgets), `govern-refuse` (a single over-budget actor is OPCOST-REFUSE;
                      admitted + deferred == all, in-order — conservation). AND the watched thing
                      materialized: `govern-progress-wait` certifies genuine SCHEDULER laws —
                      progress (every tick admits ≥ 1), bounded-wait (drain ≤ N ticks, FIFO
                      non-decreasing, no starvation) — liveness properties no basis carries. A
                      SCHEDULING-axis candidate, FIRST sighting recorded; non-scoring, so nothing
                      mints and no weights move. Checkpoint 3 inherits it.

### P11 — resolved: **C-AB (the third under-priced tie)** · meta: **M-0 on both scoring joints (10 for 10)**
    observed:         the module's TITLE conjoins its two certified laws: THE KEYED HEARTBEAT
                      (`liveness-auth` — possession, not recomputability: unkeyed tokens forged
                      12 of 12 by any observer, keyed 0 of 12 — the counterfeit reset closed;
                      bound to clockauth's server-attested tick) and THE WELL-FOUNDED COUNTDOWN
                      (`liveness-descent` — pure integer subtraction over the naturals, no
                      defensive clamp, exactly PATIENCE−1 survivors then the fault — the
                      budget-descent pattern VERBATIM on the time axis). Claim-adjudication fused
                      with cost-descent: C-AB. B-M's C-INV 40 was WRONG — the crashed-slow
                      indistinguishability is the module's DECLARED BOUNDARY ("indistinguishable
                      in CAUSE; this rung makes the CONSEQUENCE deterministic"), not its law.
                      B-M overfit to its lease win; recorded.
    tournament:       C-AB likelihoods 15 (B-A′) / 20 (B-M): weights B-M 0.58 / B-A′ 0.42.
                      Brier: B-M 0.875, B-A′ 0.98, author 0.825. THE TIE LESSON RECURS: C-AB has
                      now realized THREE times (P5, P6, P11), under-priced every time — the next
                      freeze must price it as the modal outcome for conjunction-shaped modules.
    unnamed (M-0):    the BaseException measurement — a law about THE GATE ITSELF (a BaseException
                      subclass ABORTS the process instead of reddening a row, silently destroying
                      the byte-identity spine; pinned as data, the anti-swallowing guarantee
                      obtained by plant + assertion instead); the masking ladder (what each
                      relaxation buys an adversary holding one intercepted token: 4 ticks honest,
                      8 windowed, 40 any-historical); the exact 1-tick replay window ("the
                      adversary gains no tick he did not already have"); emit-pin-compare on the
                      goldens (L23 applied to conformance itself).
    instrument:       background predicted (liveness non-high) — right; cells: high 1/0,
                      non-high 5/0.
    batch summary:    run 3 CLOSED at P9; the batch completed per the frozen rule; CHECKPOINT 3
                      fires next over THIRTEEN read joints, inheriting: the tightened tournament
                      (B-M 0.58 / B-A′ 0.42, one kill each side of even), the scheduling-axis
                      first sighting, the thrice-realized under-priced tie class, and the
                      interface instrument's contradicted high cell.

## CHECKPOINT 3 — the gauntlet over THIRTEEN read joints (2026-08-04) — **THE FIRST PROMOTION**

**Test A — compression replay (14 modules incl. non-scoring govern):**
    B-A′: TWO exceptions — stance (measure semantics, standing) and govern's scheduler laws
          (progress / bounded-wait / fairness fit no axis in {rep, adm, prop, cost} + composition).
          FAILS.
    B-M:  ZERO exceptions, TWO recorded strains — govern's scheduling filed as cost-input ×
          structural-invariant (the drain bound as a process invariant; a strain, not a patch) and
          drive filed as representation × invariant. All fourteen classify. PASSES.
**Test B — prediction:** B-A′ two forward wins (P7, P9); B-M one (P8) plus tie-shares. Both PASS.
**Test C — stability:** families over eleven preregistered READs: 1,2,3,3,4,4,4,4,4,4 →
    G(n) → 4/11 ≈ 0.36, strictly decreasing since P5; runs 2 and 3 each closed on double zeros.
    PASSES. **Test D — counterfactual:** three instances (P4 refuse≠measure; P7 same-prose
    divergent predictions; P8 the invariant call traceable to the axis, not lease's prose). PASSES.

**VERDICT (frozen outcome space): PROMOTE B-M.** The first basis to survive all four tests over
the full history. What promotion MEANS, bounded honestly (L58): B-M becomes the WORKING BASIS —
the default seam vocabulary for future briefs and freezes — and nothing more: no gate row is
minted, MT stays armed (promotion is not immunity; B-M's fails_if survive), and **B-A′ is retained
as the live challenger** (the discriminability criterion: a promoted basis without a rival is a
narrative). The tournament continues: weights B-M 0.58 / B-A′ 0.42.

**Also adjudicated here:**
    TIE-PRICING RULE, frozen forward: C-AB is priced ≥ 30 for any target whose role prose names
      two laws or composes two certified patterns — three realizations (P5, P6, P11), under-priced
      all three times, end here.
    SCHEDULING AXIS: one sighting (govern) — not minted (L3); the checkpoint's re-scan found no
      second carrier among the fourteen. priogov, when its turn comes, is the natural test.
    INTERFACE INSTRUMENT: SUSPENDED — not killed, starved. Runs 2–3 produced ZERO emergence
      events, so its comparative claim is untestable on this corpus tail, and its single
      directional call (drive's high cell: elevated predicted, clean delivered) was wrong. The Γ
      table remains data; the instrument revives if an emergence event ever accrues. Recorded as
      the honest fate of a hypothesis the world declined to feed.

## BATCH 2 FREEZE — P12 + P13 + P14 (all sealed before any READ; B-M now predicts as working basis)

**Batch rules**: as batch 1 (selector order wavefield → frontier → gaze; sequential scoring;
run-4 v_D starts fresh; mid-batch closure completes the batch post-closure). MT: standing
conditions. The suspended instrument makes no calls. Meta predicts ¬M-1 on all three (10 for 10).

### P12 — `wavefield` (SCORING; heavy role-prose exposure disclosed)
    provenance:       the AGENTS.md index entry is unusually detailed and was read twice this
                      session (DISCLOSED): "the EXACT integer traveling-wave field (periodic
                      parabolic profile, floor-mod phase, superposition; same components + tick →
                      same bytes, no rounding) the GPU's declared Gerstner sinusoid draws from —
                      DIVISION-FREE (tokenizer-asserted)". This is the sanctioned role-prose
                      channel, but rich; the discrimination below is about what is CENTRAL, which
                      the prose does not rank. Body and history UNREAD.
    partition:        C-REP (exact-integer canon identity central — the heightfield pattern on a
                      time-varying field) · C-INV (superposition linearity / division-free as the
                      central structural law) · C-AB · R-M · R-O.
    credences:        author: C-REP 30 · C-INV 20 · C-AB 30 · R-M 5 · R-O 15
                      B-A′:   C-REP 45 · C-INV 10 · C-AB 30 · R-M 5 · R-O 10
                      B-M:    C-REP 35 · C-INV 20 · C-AB 30 · R-M 5 · R-O 10

### P13 — `frontier` (SCORING)
    provenance:       role-only — the hygiene-rung line "frontier (the admission accelerator)".
                      Body and history UNREAD. The candidates largely AGREE here (recorded: weak
                      discrimination expected — an accelerator's honest law is usually
                      fast-path ≡ slow-path).
    partition:        C-EQ (accelerated ≡ unaccelerated equivalence central) · C-ADM
                      (admission-gate central) · C-AB · R-M · R-O.
    credences:        author: C-EQ 35 · C-ADM 20 · C-AB 30 · R-M 5 · R-O 10
                      B-A′:   C-EQ 40 · C-ADM 20 · C-AB 30 · R-M 3 · R-O 7
                      B-M:    C-EQ 45 · C-ADM 15 · C-AB 30 · R-M 3 · R-O 7

### P14 — `gaze` (SCORING; partial exposure disclosed — the stage docstring's first line leaked
                      during an earlier Read: "the certified first-person OBSERVER over the
                      terrain"; stance/drive prose adds "certifies a view reconstructs to
                      trajectory[k], or refuses it")
    partition:        C-R (view-admission central: reconstruct-or-refuse — the warden pattern on
                      observers) · C-REP (view-reconstruction identity central) · C-AB · R-M · R-O.
    credences:        author: C-R 30 · C-REP 25 · C-AB 30 · R-M 5 · R-O 10
                      B-A′:   C-REP 40 · C-R 20 · C-AB 30 · R-M 3 · R-O 7
                      B-M:    C-R 40 · C-REP 20 · C-AB 30 · R-M 3 · R-O 7
                      GENUINE DISCRIMINATION: the promoted basis reads the observer as police ×
                      representation; the challenger as identity-first.
    witness:          the git commit introducing these rows — dated before any of the three
                      modules is read.

### P12 — resolved: **C-AB** (the tie rule pays on its first outing)
    observed:         `wavefield-properties` fuses the physics-invariant half — cells bounded by
                      Σ|A|, swell travels while still is static, and SUPERPOSITION IS EXACT
                      (field(Σcomp) == Σfield(comp), no rounding — linearity as a structural law)
                      — while `wavefield:scenes` pins the canon identity (same components + tick →
                      same bytes). Representation fused with invariant: C-AB, priced 30 by all
                      three predictors under the new rule (Brier: author 0.645, B-M 0.665,
                      B-A′ 0.715 — versus the 0.9+ the old 20-pricing produced on ties).
    unnamed (M-0):    the shift-based DOUBLING arithmetic (curvature and phase wrap computed with
                      << >> + − comparisons only, exact and O(log) — a Q16 reciprocal would round
                      and could not claim EXACT); the 8A = cP² admissibility tie; the tokenizer
                      assertion as STRUCTURAL cross-placement parity (operator absence proven, not
                      documented). Weights unchanged (equal likelihoods).

### P13 — resolved: **R-O — the APPROXIMATION AXIS, first sighting** (the first residual since P3)
    observed:         "the admission accelerator" is a VERIFIED GALOIS CONNECTION: α(P) ≤ O ⟺
                      P ≤ γ(O) holds 63/63; the abstraction is SOUND, REDUCTIVE, and deliberately
                      NOT COMPLETE, with the precision loss COUNTED as the obligation signature.
                      The central row (`frontier-law`): edits in different connected components of
                      the conflict graph commute — checked against the commutation SEMANTICS, not
                      the predicate that built the graph — and the obligation signature CONSERVES
                      (proved + obligations == total: nothing silently dropped, "the failure an
                      accelerator invites") and is MONOTONE (refinement moves pairs obligation →
                      proved). The module's own prior-art scoping names the discipline: abstract
                      interpretation, Cousot & Cousot 1977 — NOT claimed, verified locally.
    residual:         (predicted: fast-path ≡ slow-path equivalence (both bases); observed:
                      sound-incomplete order-theoretic abstraction with conserved, monotone,
                      COUNTED residue; delta: R-O — the APPROXIMATION axis: neither basis carries
                      "sound over-approximation with obligation accounting"). First sighting;
                      mintable at the second (L3). Weights unchanged (equal R-O likelihoods);
                      Briers poor for all (author 1.065, B-A′ 1.156, B-M 1.181) — the honest cost
                      of an axis nobody had.
    instrument note:  the suspended interface instrument finally receives an emergence event — at
                      a NON-high joint. Cells: high 1/0 emergence, non-high 7/1. The first
                      non-degenerate datapoint points AGAINST the interface hypothesis.

### P14 — resolved: **C-R — the promoted basis WINS the genuine discrimination** · meta ¬M-1: 13 for 13
    observed:         gaze is reconstruct-or-refuse on views, exactly as B-M read it: a frame is
                      ADMITTED iff it is COVERING (the atlas observes every pose axis — the
                      Kálmán full-column-rank condition) AND its reconstruction's digest equals
                      the CURRENT authority's; else typed refuse (GAZE-NONCOVER / GAZE-LAUNDER —
                      one mechanism, two threat models: a substituted pose and a stale one).
                      `gaze-selftest` pins the advancing authority as load-bearing: the same
                      once-valid frame admits at its own pose and refuses at the advanced one —
                      replay caught by construction.
    tournament:       B-M 40 vs B-A′ 20 on C-R → weights w(B-M) = 0.73, w(B-A′) = 0.27 (Brier:
                      B-M 0.496, B-A′ 0.896, author 0.655). The promoted basis's first win AS the
                      working basis, on the exact axis that created it (police × representation —
                      the P3/P4 split, now predicting observers).
    unnamed (M-0):    the RANK condition as admissibility (observability = full column rank — a
                      linear-algebra criterion deciding coverage); same-mechanism-two-threats;
                      membrane purity (admit never mutates authority or frame). P12 M-0, P13 M-2,
                      P14 M-0 — the meta's ¬M-1 stands 13 for 13.
    census:           run-4 v_D: 0 (P12), 1 (P13 — the approximation axis), 0 (P14). One
                      consecutive zero; run 4 CONTINUES. Checkpoint 4 waits for the closure rule.

## BATCH 3 FREEZE — P15 + P16 + P17 (all sealed before any READ)

**Batch rules**: as before (selector order panelight → wardhom → ashdepth; sequential scoring;
run-4 v_D stands at one zero from P14; mid-batch closure completes post-closure). MT standing.
The APPROXIMATION AXIS watch: any R-O with approximation content is its second sighting and MINTS
it. Meta predicts ¬M-1 on all three (13 for 13). The suspended instrument makes no calls
(panelight sits in the old high-Γ set; recorded as data only).

### P15 — `panelight` (SCORING) — role: "THE WINDOWED LOOP (T3.52, V1)"; ambient: the V-phase
    opener; the D15 view-firewall pattern and the idle law ("zero frames while idle") are known
    from AGENTS prose. Body and history UNREAD.
    partition:        C-R (witness-binding/admission central — the view firewall as police ×
                      representation) · C-COST (the idle/frame-economy law central) · C-AB ·
                      R-M · R-O.
    credences:        author: C-R 30 · C-COST 25 · C-AB 30 · R-M 5 · R-O 10
                      B-A′:   C-R 25 · C-COST 30 · C-AB 30 · R-M 5 · R-O 10
                      B-M:    C-R 35 · C-COST 20 · C-AB 30 · R-M 5 · R-O 10

### P16 — `wardhom` (SCORING) — role states the identity outright: "Warden β₀ IS certified
    F2-homology β₀, cross-placed (T3.27)"; ambient: opcost counts its F2 boundary columns (n1, one
    per legal edge). Body and history UNREAD. The candidates converge (recorded): a stated
    equivalence is hard to disagree about; the discrimination here is only equivalence-vs-invariant
    centrality.
    partition:        C-EQ (two independent computations agree — the neutral-oracle equivalence
                      central) · C-INV (the homology invariant itself central) · C-AB · R-M · R-O.
    credences:        author: C-EQ 45 · C-INV 15 · C-AB 25 · R-M 5 · R-O 10
                      B-A′:   C-EQ 50 · C-INV 12 · C-AB 25 · R-M 3 · R-O 10
                      B-M:    C-EQ 45 · C-INV 17 · C-AB 25 · R-M 3 · R-O 10

### P17 — `ashdepth` (SCORING) — role: "The VACUITY FLOOR — a level that distinguishes nothing is
    not a result" (URDRASH1, a hygiene rung). Body and history UNREAD.
    partition:        C-FLOOR (a threshold gate central: measured discrimination depth vs a
                      declared floor, refuse below — the cost discriminator inverted) · C-MEAS
                      (the vacuity measurement central, stance semantics) · C-AB · C-INV
                      (a structural non-vacuity invariant central) · R-O.
    credences:        author: C-FLOOR 30 · C-MEAS 20 · C-AB 30 · C-INV 5 · R-O 15
                      B-A′:   C-FLOOR 40 · C-MEAS 15 · C-AB 30 · C-INV 5 · R-O 10
                      B-M:    C-FLOOR 35 · C-MEAS 20 · C-AB 30 · C-INV 5 · R-O 10
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P15 — resolved: **C-AB** · RUN 4 CLOSES HERE (second consecutive zero, after P14)
    observed:         panelight ADDS three laws, certified in three rows — no single center:
                      `panelight-equiv` (INTERACTIVE == BATCH: the tick transcript equals
                      glide_cells BIT-FOR-BIT on a pure-move log — the theorem that lets a live
                      game be trusted: playing it and folding it agree), `panelight-accum` (the
                      integer-ms accumulator: alpha always in range; total ticks == floor(Σdt/TICK)
                      — no time lost or invented; each input consumed EXACTLY ONCE; and the
                      DECOUPLING law — two dt-logs with the same total ticks land the IDENTICAL
                      authority witness: render cadence never moves the authority), and
                      `panelight-firewall` (D15 on TIME: the witness is over tick poses only,
                      invariant to the frame schedule; interpolation smooths the view, never the
                      transcript). Weights unchanged (equal 30s); Briers ~0.65 all.
    unnamed (M-0):    exactly-once as a refusal (a schedule short of the input refuses — no silent
                      skip); the fixed-timestep anchoring (Source/Overwatch); the mints-nothing
                      composition (glide._fold_from clocked, not reimplemented).

### P16 — resolved (post-closure): **C-EQ** — the stated identity, certified
    observed:         `wardhom-tie`: warden.betti0 (union-find) == URDRPD1 F2-rank β₀ on every
                      pinned world including the 16×16 barrier — two independent methods, one
                      invariant; and the F2 computation is CROSS-PLACED (Python == C99 == Rust,
                      digest bit-for-bit). The neutral-oracle equivalence central, as everyone
                      predicted (B-A′ 50 best; weights drift to ~0.71/0.29).
    unnamed (M-0):    β₁ (independent cycles) certified alongside; the non-vacuity pins (barrier
                      β₀=3, cliff β₀=2, flat β₀=1 — genuinely different topology the digest must
                      separate); the URDRPD1 defect mode (dropping the rank subtraction inflates
                      β₀ and moves the digest).

### P17 — resolved (post-closure): **C-FLOOR** — and the handed-down design REFUTED by measurement
    observed:         `ashdepth-law`: SOUNDNESS NEVER BREAKS as an abstraction coarsens (coarsening
                      is strictly more conservative by level monotonicity — 0 unsound at every
                      level) — so the proposed coarse-end guard k* passes VACUOUSLY at maximum burn,
                      the exact point it was built to catch. THE INVERSION is the rung: the bound
                      worth guarding is k_min (the finest level at which α still DISTINGUISHES
                      something — fast path non-empty), guarded by a floor gate that refuses below
                      it, with `VacuityError` raised rather than a zero quietly returned and
                      EMPTY_CORPUS pinned as a hard tripwire asset. The module names the arc's
                      characteristic-failure LAW after its FOURTH appearance: "wrong answers are
                      rare and empty answers are common, and an empty answer is indistinguishable
                      from a correct one unless something asserts non-emptiness."
    axis tension (recorded for checkpoint 4): ashdepth is APPROXIMATION-AXIS CONTENT through and
                      through (the precision/vacuity structure of the frontier/disjoint Galois
                      stack) — but the frozen mint trigger was "an R-O with approximation content",
                      and this resolved C-FLOOR. The letter is unmet; the spirit is a second
                      sighting. The trigger is NOT bent mid-run; checkpoint 4 adjudicates the
                      letter-vs-spirit question with both facts on the table. Note the resonance:
                      the vacuity law is ALSO the interface instrument's fate (starved of events —
                      an empty answer read as consistency) and W1's plant discipline.
    tournament:       weights after the batch: w(B-M) = 0.68, w(B-A′) = 0.32 (P16 and P17 both
                      mildly favored the challenger's sharper pricing). Meta ¬M-1: 16 for 16.
    census:           run 4 CLOSED at P15; the batch completed post-closure. CHECKPOINT 4 fires
                      next over NINETEEN read joints, inheriting: the approximation letter-vs-
                      spirit question, the scheduling axis still at one sighting, the vacuity law
                      as a cross-cutting candidate, and a tournament at 0.68/0.32 with the
                      promoted basis unbeaten on discriminations but outpriced twice.

## CHECKPOINT 4 — over NINETEEN read joints (2026-08-04): the approximation axis MINTS; both bases mutate

**Test A — replay (20 modules):** B-A′ THREE exceptions (stance semantics; govern scheduling;
frontier approximation). B-M ONE exception — frontier: the approximation axis is now B-M's ONLY
gap. Both fail the zero bar; B-M's failure is a single pointer.
**Test B:** both pass (B-M forward wins P8/P14; B-A′ wins P7/P9 and out-priced P16/P17).
**Test C:** unique families 1,2,3,3,4,…,5(P8),…,6(P13) → G(17) = 6/17 ≈ 0.35, decreasing at the
tail (6/15, 6/16, 6/17); runs 2–4 each closed on double zeros. Passes. **Test D:** four instances.

**THE APPROXIMATION MINT — adjudicated MINTED.** The frozen trigger ("an R-O with approximation
content") was met once by the letter (frontier, P13) and once by the spirit (ashdepth, P17: a
C-FLOOR resolution whose entire subject is the abstraction stack's precision/vacuity structure).
L3's real requirement is independent recurrence of CONTENT, and the trigger's letter was a proxy
drafted too narrowly — recorded as a drafting lesson: FUTURE TRIGGERS NAME CONTENT, NOT OUTCOME
CLASSES. Two independent carriers ⇒ the axis mints:
    lineage: B-M → B-M′   appeared: approximation joins the input-family axis {representation ·
             admission · propagation · cost · approximation}. disappeared: nothing.
             REPLAY: ZERO exceptions over all twenty modules (frontier now classifies:
             approximation × invariant + composition). Forward obligation inherited.
    lineage: B-A′ → B-A″  the challenger takes the same repair (its frontier exception clears;
             stance and govern remain — 2 exceptions). The tournament stays two-sided.
    weights: inherited (additive mutation, no retroactive prediction change): B-M′ 0.68, B-A″ 0.32.
**THE VACUITY RULE — adopted as a freeze requirement** (ashdepth's law lifted to the epistemic
layer, first application at the batch-4 freeze below): every scoring instrument or prediction
names its STARVATION MODE — what event stream feeds it, and that a starved resolution reads
STARVED, never confirmed. The interface instrument's fate is the motivating instance; a LESSONS
row waits for the rule's second application. **Scheduling axis:** still one sighting; holds.

## BATCH 4 FREEZE — P18 + P19 + P20 (all sealed before any READ)

**Batch rules**: as before (order auditgraph → cpredict → driftgaze; run-5 v_D starts fresh).
Vacuity rule applied: each scoring resolution below must either cite non-empty censuses or read
STARVED. Meta predicts ¬M-1 on both scoring joints (16 for 16).

### P18 — `auditgraph` (SCORING) — role: "The exclusion price (kappa) — all-pairs is the only
    unbreakable audit topology" (URDRAGR1); ambient disclosed: liveness's docstring ("auditgraph
    priced undetected equivocation at kappa — converting an invisible INTEGRITY attack into a
    visible AVAILABILITY one") and the ladder ("the server BUILDS the audit graph, so matchmaking
    is the attack surface"). Body and history UNREAD.
    partition:        C-PRICE (the κ bound central — the cost pattern on equivocation) · C-INV
                      (a structural topology theorem central — all-pairs as the unique unbreakable
                      audit graph) · C-AB · R-M · R-O.
    credences:        author: C-PRICE 30 · C-INV 25 · C-AB 30 · R-M 5 · R-O 10
                      B-A″:   C-PRICE 40 · C-INV 20 · C-AB 30 · R-M 3 · R-O 7
                      B-M′:   C-PRICE 30 · C-INV 30 · C-AB 30 · R-M 3 · R-O 7
### P19 — `cpredict` (NON-SCORING — contamination declared: horizon's read exposed
    reconcile/reconstruct and the δ = 0 byte-exact property; the core law is effectively known).
    Read for the brief pass; watched: the suffix-replay economy and the localization law.
### P20 — `driftgaze` (SCORING) — role: "Interest shift (T3.50, W4) — the client that MOVES"
    (URDRDGZ1); ambient disclosed: wire DEFERRED interest shift here ("chunkload's verified fetch
    is the mechanism, the policy is operational"). Body and history UNREAD.
    partition:        C-R (shift-admission central: regions acquired by verified fetch, releases
                      typed — police) · C-CONS (a resident-set coverage/conservation invariant
                      central) · C-AB · R-M · R-O.
    credences:        author: C-R 30 · C-CONS 25 · C-AB 30 · R-M 5 · R-O 10
                      B-A″:   C-R 35 · C-CONS 25 · C-AB 30 · R-M 3 · R-O 7
                      B-M′:   C-R 30 · C-CONS 30 · C-AB 30 · R-M 3 · R-O 7
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P18 — resolved: **C-PRICE** — the challenger's sharper pricing wins
    observed:         `auditgraph-law` is the theorem chain entire: splitview's gossip graph was
                      EXOGENOUS and an official server BUILDS its own — matchmaking is the attack
                      surface (Bell(k)−1 of the Bell(k) session partitions leave the audit graph
                      disconnected, and the server picks); committing the topology to CLIENT
                      IDENTITY collapses that to 0 of 1, leaving only ADMISSION; and under a
                      committed topology THE PRICE OF UNDETECTED EQUIVOCATION IS EXACTLY κ(T), the
                      vertex connectivity — decided by RUNNING THE ATTACK over every exclusion set
                      and comparing against Menger max-flow, 771 connected labelled graphs to
                      order 5, 0 exceptions. Corollary reversing splitview's recommendation: the
                      graphs the server can NEVER split are EXACTLY the complete ones — all-pairs
                      costs the adversary infinity. Weights: B-A″ 40 vs B-M′ 30 → 0.614 / 0.386.
    unnamed (M-0):    THE RECORDED LIE — the first cross-check compared two copies of the same
                      loop and "shipped three times before an audit caught it"; refuted BY
                      MUTATION (corrupt `components`: the old census still reports 0 exceptions,
                      merely SHRINKING ITS OWN DENOMINATOR, while the Menger census reports 181),
                      and `cross_check_is_falsifiable` now runs that mutation ON EVERY GATE PASS —
                      L23 self-applied inside a module. And the denominator defect is the VACUITY
                      LAW'S FIFTH CARRIER (a fault that narrows the world without causing
                      disagreements — an empty answer wearing a clean census's clothes), now
                      guarded by max-flow cross-check (1099/1099) and typed refusals in
                      validate_graph. Vacuity rule: censuses non-empty, cited — satisfied.

### P19 — resolved (NON-SCORING): the disclosed law, certified
    observed:         `cpredict-equivalence` and `cpredict-refines` certify what horizon's read had
                      exposed: reconcile localizes the first mispredict boundary, replays only the
                      suffix, and reconstruct lands on the authority byte-exactly (δ = 0). Read
                      for the brief pass; no weights moved.

### P20 — resolved: **C-AB** · RUN 5 CLOSES (two consecutive scoring zeros) · meta ¬M-1: 18 for 18
    observed:         `driftgaze-shift` fuses the two predicted centers: the mover CHUNK-REFUSEs
                      on unloaded demand, then runs on the resident view EQUAL to the full-field
                      glide BIT-FOR-BIT after the verified acquire, with interest following the
                      gaze — police and equality in one law, over a resident set that changes
                      beneath the walk, driven by the walk's own demand. `driftgaze-fetch` (five
                      refusal shapes, all pure) and `driftgaze-repair` (the gap repair) guard it.
                      Weights unchanged (equal 30s): B-M′ 0.614 / B-A″ 0.386.
    unnamed (M-0):    RE-ACQUISITION CARRIES HISTORY (missed updates are never replayed — they
                      arrive as already-history and refuse at the CAS; catching up is a FETCH, not
                      a replay); the stale-acquisition split (the fetch checks INTEGRITY, not
                      CURRENCY — currency is state, caught by the next admission's CAS); and the
                      GAP REPAIR as cross-module debt settlement — the storm's declared W4 debt,
                      paid on schedule and cited both ways.
    census:           run-5 v_D = 0, 0 (P18, P20) — RUN 5 CLOSES. CHECKPOINT 5 fires next over
                      twenty-two read joints, with B-M′ replay-clean, the tournament at
                      0.614/0.386, and the vacuity law now at five carriers.

## CHECKPOINT 5 — over TWENTY-TWO joints (2026-08-04): promotion holds; the vacuity law mints L61; NOT converged

**Gauntlet:** A — B-M′ replays CLEAN over all 21 scored modules (zero exceptions); B-A″ keeps two
(stance, govern). B — both pass. C — G(20) = 6/20 = 0.30, decreasing; runs 2–5 each double-zero.
D — B-A″ is a LIVE rival (it out-priced B-M′ on P16/P17/P18 — the discriminability criterion is
doing real work, not a formality). **Verdict: promotion HOLDS (B-M′ working basis, B-A″ retained);
no basis change.**

**Convergence — explicitly NOT declared, and why (the honest call over an easy one):** three of the
four epistemic stopping criteria are met (prediction, stability, discriminability), and B-M′ passes
compression. But convergence requires the BASIS to be stable, and it is not: the approximation axis
minted only one checkpoint ago (a basis that grew last round has not shown it won't grow again), and
the SCHEDULING axis is a live mint candidate at one sighting — `priogov`, when the frozen selector
reaches it, is its decisive second test. Declaring convergence now would be the L58 premature-
abstraction trap wearing a stopping rule's clothes. Convergence is PENDING the scheduling question.

**L61 MINTED** (vacuity law → LESSONS): the rule adopted at checkpoint 4 and applied at the batch-4
and (below) batch-5 freezes now has FIVE independent module carriers (disjoint, frontier, ashdepth,
the level-table corpus, auditgraph's denominator) plus two freeze-applications — past L3's bar. See
LESSONS L61. The interface instrument is its self-referential sixth carrier: an instrument starved
of emergence events reads CONSISTENT, which is an empty answer wearing a confirmation's clothes.

## BATCH 5 FREEZE — P21 + P22 + P23 (all sealed before any READ)

**Batch rules**: order geoquorum → ghostsnap → hand (frozen selector: in-degree 1, lex). Run-6 v_D
fresh. Vacuity rule (L61) applied: each scoring resolution cites non-empty censuses or reads STARVED.
Meta predicts ¬M-1 on all three (18 for 18).

### P21 — `geoquorum` (SCORING) — role: "Multi-observer capture consensus (S4) — coverage refusal
    vs INTEGRITY refusal" (URDRGEO1); ambient disclosed: cohort's brief cited geoquorum's
    THIN-vs-DEVIATE split (UNAVAILABLE = coverage vs FAILED = integrity). The role LINE already
    names two refusal kinds — a strong C-AB / two-law signal (tie priced ≥ 30 per the rule). Body
    and history UNREAD.
    partition:        C-R (a single admission/consensus predicate central) · C-SPLIT (the
                      coverage-vs-integrity DISTINCTION itself as the central law — a two-refusal
                      taxonomy) · C-AB · R-M · R-O.
    credences:        author: C-R 20 · C-SPLIT 30 · C-AB 35 · R-M 5 · R-O 10
                      B-A″:   C-R 25 · C-SPLIT 30 · C-AB 35 · R-M 3 · R-O 7
                      B-M′:   C-R 20 · C-SPLIT 35 · C-AB 35 · R-M 3 · R-O 7
### P22 — `ghostsnap` (SCORING) — role: "The actor wire (T3.54, V3) — equal-or-refuse ghosts"
    (URDRGHS1); ambient disclosed: the V3 actor-wire; wire's equal-or-refuse pattern named. Body
    and history UNREAD. Candidates converge toward the wire pattern (recorded).
    partition:        C-R (equal-or-refuse replica admission central — police × representation,
                      the wire pattern on actors) · C-REP (ghost-state identity central) · C-AB ·
                      R-M · R-O.
    credences:        author: C-R 30 · C-REP 25 · C-AB 30 · R-M 5 · R-O 10
                      B-A″:   C-REP 35 · C-R 25 · C-AB 30 · R-M 3 · R-O 7
                      B-M′:   C-R 35 · C-REP 20 · C-AB 30 · R-M 3 · R-O 7
### P23 — `hand` (SCORING) — role: "Seamless cross-region authority handoff (T3.23)" (URDRHAND1);
    ambient disclosed: the mesh phase's "certified authority migration as lease transfer"; chain
    position near crosswarden/dirward. Body and history UNREAD.
    partition:        C-INV (a handoff exclusivity/continuity invariant central — no-gap/no-overlap
                      authority transfer, the lease/migration structural pattern) · C-R
                      (handoff-admission predicate central) · C-AB · R-M · R-O.
    credences:        author: C-INV 30 · C-R 25 · C-AB 30 · R-M 5 · R-O 10
                      B-A″:   C-R 35 · C-INV 20 · C-AB 30 · R-M 3 · R-O 7
                      B-M′:   C-INV 35 · C-R 20 · C-AB 30 · R-M 3 · R-O 7
                      DISCRIMINATION: B-M′ prices the structural-invariant reading (its founding
                      strength); B-A″ the admission-predicate reading.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P21 — resolved: **C-SPLIT** — the coverage/integrity DISTINCTION is the law (a fifth-family probe)
    observed:         `geoquorum-law` is not one predicate but a distinction with a THEOREM under it:
                      a self-consistent DOCTORED capture has the SAME internal divergence (zero) as
                      an honest one — "self-consistency is the one property a liar can always
                      supply" — so intent is invisible to any per-submission bound; the only
                      evidence a liar does not control is OTHER PEOPLE's captures (oobprior's
                      structurally-excluded cohort, applied to geometry via voxlat's Morton-prefix
                      "same place"), and strict-majority consensus flips exactly at ceil(k/2),
                      DECIDED by enumeration (a first draft asserted floor(k/2)+1 and the enumeration
                      REFUSED it) with the operational corollary EVEN COHORTS BUY NOTHING. The two
                      refusals are categorically distinct: UNAVAILABLE (coverage — too few
                      observers) vs FAILED (integrity — the cohort disagrees). Weights: B-M′ 35 vs
                      B-A″ 30 → 0.634/0.366. Vacuity rule: MIN_COHORT = 5 is the module's OWN
                      non-vacuity floor (a lone liar cannot frame an honest contributor) — L61's
                      seventh carrier, and it read non-STARVED.
    axis note:        C-SPLIT is close to the APPROXIMATION axis (sound-vs-complete → coverage-vs-
                      integrity) but is really a distinct thing: the DISCRIMINABILITY-of-refusal
                      axis (why a refusal fired: absence vs contradiction). Both bases classified
                      it via existing cells (admission with a typed sub-reason), so NO new family —
                      recorded as a candidate to watch, not a mint (L3).

### P22 — resolved: **C-R** — the wire pattern on actors; the promoted basis wins
    observed:         `ghostsnap-admit`: a ghost is a 112-byte content-addressed per-tick POSE
                      record chained by parent digest (terraform's chain law on the movement
                      plane), admitted under the SAME equal-or-refuse discipline as the terrain wire
                      — "not a cheaper ghost, a ghost that CANNOT LIE." Tampered / foreign-parent
                      genesis / out-of-interest / out-of-order each refuse with the ghost map
                      byte-identical; a duplicate refuses (the parent moved); the in-order retry
                      admits. Police × representation, central. Weights: B-M′ 35 vs B-A″ 25 →
                      0.68/0.32.
    unnamed (M-0):    order-is-structural (no sequence numbers — the parent chain IS the order, the
                      wire pattern's signature a third time: wire, driftgaze, ghostsnap); the
                      genesis-from-all-zeros spawn; the kinematic gate (ghostsnap-kinematic) reusing
                      warden's step law on ghost motion.

### P23 — resolved: **C-INV** — B-M′'s founding axis, forward; and the DISCRIMINATION goes to B-M′ · RUN 6 CLOSES
    observed:         `hand-equivalence` is HANDOFF EQUIVALENCE: glide the prefix over F_A, resume
                      the suffix over F_B (a two-field `splice`, memoryless) EQUALS a single glide
                      over the merged world BIT-FOR-BIT — "seamless not because two authorities
                      blend (that hides float drift URDR does not have) but because the handoff pose
                      is bit-identical to what a single authority would produce." Latency-invariance
                      (bit-identical for ANY in-band handoff tick — the bridge survives handoff
                      latency) and one-point/many-points scale it; seam-agreement is load-bearing
                      (F_A ≠ F_B at the seam, or an out-of-band tick, is typed HAND-REFUSE). A
                      structural CONTINUITY invariant (no-gap/no-overlap authority transfer), the
                      lease/migration pattern — B-M′'s founding structural-invariant reading, priced
                      35 vs B-A″'s admission reading 20. Weights: w(B-M′) = 0.74, w(B-A″) = 0.26.
    unnamed (M-0):    uses-B-terrain non-vacuity (the handoff diverges from a glide that stayed on
                      F_A — B's terrain is really used); the Φ-band sync precondition; the refuse-
                      never-blend discipline (blending imports the drift the arc structurally lacks).
    tournament:       after batch 5 — w(B-M′) = 0.74, w(B-A″) = 0.26. B-M′ took both discriminations
                      it was offered (P22, P23) on its founding axes; B-A″'s pricing edge did not
                      recur. Meta ¬M-1: 21 for 21.
    census:           run-6 v_D = 0, 0, 0 (P21, P22, P23 — no new family; C-SPLIT watched, not
                      minted) — RUN 6 CLOSES on a triple zero, the run's cleanest convergence signal
                      yet. CHECKPOINT 6 fires next over TWENTY-FIVE joints, with the promoted basis
                      at 0.74 and the scheduling axis STILL the only open mint question.

## CHECKPOINT 6 — over TWENTY-FIVE joints (2026-08-04): L61 turned on the tournament; B-A″ retirement frozen

**Gauntlet:** A — B-M′ clean (0 exceptions over 24 scored modules); B-A″ two (stance, govern).
B, C, D pass. G(23) = 6/23 ≈ 0.26. **Verdict: promotion HOLDS; no basis change; convergence still
pending** (scheduling axis unminted).

**THE DISCRIMINABILITY CRITERION, AUDITED BY L61 — the checkpoint's real finding.** Test D of the
epistemic stopping rule ("a plausible competing basis testable against future READs") can be
satisfied TRIVIALLY by keeping a dead rival on life support — which is L61's vacuity law
(an answer that cannot lose is empty) turned on the discovery engine's own convergence criterion.
So the criterion must itself carry a non-vacuity precondition: **a rival must be able to LOSE its
rival status, or the tournament is theater.** Frozen retirement condition for B-A″:

    B-A″ RETIRES from the tournament when BOTH hold: (i) it has lost ≥ 3 CONSECUTIVE discriminations
    (joints where the two bases predicted different central rows and the resolution matched B-M′),
    and (ii) w(B-A″) < 0.20. Current: B-A″ has lost 2 consecutive (P22, P23) at w = 0.26 — NOT yet
    retired, but one more losing discrimination plus a small weight drop triggers it.
    ON RETIREMENT: convergence becomes declarable with B-M′ as the sole surviving basis, carrying
    the honest caveat that single-basis convergence is STRICTLY WEAKER than rival-tested
    convergence (no live alternative remains to falsify it) — recorded as such, never as a
    stronger result than it is. A fresh challenger (adversarial synthesis) is the DEFERRED
    alternative; it is not built speculatively (L58).

So convergence now waits on TWO frozen questions, both decidable by future READs, neither bendable:
the scheduling-axis mint (priogov) and B-A″'s rival-status (its next losing discrimination). The
engine cannot declare victory by fiat; it must be driven there by the data or by a rule firing.

## BATCH 6 FREEZE — P24 + P25 + P26 (all sealed before any READ)

**Batch rules**: order interest → mesh → panewire (frozen selector). Run-7 v_D fresh. L61 vacuity
rule applied. Meta predicts ¬M-1 on all three (21 for 21).

### P24 — `interest` (SCORING) — role: "Deterministic Area-of-Interest relevance (T3.21, Stage C)"
    (URDRAOI1); ambient disclosed: wire's `relevant` filter and driftgaze's "interest follows the
    gaze" both compose interest; it is the AoI relevance predicate the wire family cites. Body and
    history UNREAD.
    partition:        C-R (a relevance/admission predicate central — police) · C-EQ (an
                      irrelevant-edit ≡ unchanged equivalence central — the wire soundness pattern) ·
                      C-AB · R-M · R-O.
    credences:        author: C-R 25 · C-EQ 35 · C-AB 30 · R-M 5 · R-O 5
                      B-A″:   C-R 30 · C-EQ 35 · C-AB 30 · R-M 2 · R-O 3
                      B-M′:   C-R 25 · C-EQ 35 · C-AB 30 · R-M 5 · R-O 5   (NOT a discrimination —
                      the bases agree; recorded so, so it cannot count toward retirement either way)
### P25 — `mesh` (SCORING) — role states the identity: "THE MESHED SIMULATION (M3) — MESH ==
    MONOLITH" (URDRMSH1); ambient: Phase M's certified mesh, nway/migrate/partition family. Body and
    history UNREAD. A stated equivalence — convergence expected.
    partition:        C-EQ (mesh == monolith equivalence central — the nway/hand bit-identity
                      pattern at simulation scale) · C-INV (a mesh-composition structural invariant
                      central) · C-AB · R-M · R-O.
    credences:        author: C-EQ 40 · C-INV 20 · C-AB 30 · R-M 3 · R-O 7
                      B-A″:   C-EQ 45 · C-INV 15 · C-AB 30 · R-M 3 · R-O 7
                      B-M′:   C-EQ 40 · C-INV 20 · C-AB 30 · R-M 3 · R-O 7   (agree — not a
                      discrimination)
### P26 — `panewire` (SCORING) — role: "THE WIRED WINDOW (T3.53, V2)" (URDRPNW1); ambient: the
    V-phase; panelight (V1, the windowed loop) is family; wire's equal-or-refuse over a live window.
    Body and history UNREAD.
    partition:        C-R (the windowed wire's equal-or-refuse admission central — police ×
                      representation) · C-AB (the loop's interactive==batch fused with the wire's
                      equal-or-refuse — a two-law join) · C-REP · R-M · R-O.
    credences:        author: C-R 25 · C-AB 40 · C-REP 20 · R-M 5 · R-O 10
                      B-A″:   C-REP 30 · C-R 25 · C-AB 35 · R-M 3 · R-O 7
                      B-M′:   C-R 30 · C-AB 40 · C-REP 20 · R-M 3 · R-O 7   (DISCRIMINATION: B-A″
                      prices representation-first; B-M′ police/AB — a retirement-eligible joint)
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P24 — resolved: **C-EQ** (bases agreed — no discrimination) · the broad/narrow soundness law
    observed:         `interest-soundness` is the keystone: the BROAD phase (bucket 3×3 neighborhood,
                      bucket = x >> k, an exact shift) CONTAINS the NARROW phase (Chebyshev
                      max(|Δx|,|Δy|) ≤ R) for any R ≤ 2^k — the acceleration NEVER MISSES a relevant
                      actor (a missed relevant actor is a desync; an extra candidate is only wasted
                      bandwidth the narrow phase filters). The R ≤ 2^k precondition is load-bearing
                      (the gate plants the R > 2^k miss). `interest-exactness` adds symmetry +
                      tamper-evidence. Sound-over-approximation with the narrow phase as the exact
                      filter — the APPROXIMATION AXIS'S THIRD CARRIER (frontier, ashdepth, interest),
                      but already-minted, so it strengthens the axis rather than minting. Both bases
                      priced C-EQ 35; not a discrimination (retirement-neutral). Weights unchanged.
    vacuity:          `strict > 0` is the module's OWN non-vacuity floor (the broad phase must
                      strictly over-approximate somewhere, else the containment is vacuous) — L61's
                      eighth carrier, non-STARVED.

### P25 — resolved: **C-EQ** (bases agreed) — MESH == MONOLITH, the capstone theorem
    observed:         `mesh-law`: a concurrent multi-steward simulation with authority MIGRATING
                      equals the monolith BIT-FOR-BIT — "not a best-effort convergence, but a
                      THEOREM, re-derived in bytes." A composition (nway schedules the concurrent
                      writes as one independence round; migrate moves authority witness-neutrally;
                      terraform is the monolith oracle / neutral ruler that ignores custody so a
                      meshed bug cannot hide in its own answer), generalizing regionprop's
                      reunify==monolith from a STATIC partition to a MIGRATING one. Reject-whole
                      refusal (non-steward write / overlapping batch / theft migration each refuse
                      the WHOLE tick). C-EQ 40 both bases; not a discrimination. Weights unchanged.
    unnamed (M-0):    the neutral-ruler oracle (terraform ignores custody entirely — Goodhart
                      resistance built into the check's structure); work-partition fixed while
                      authority-partition migrates, the witness invariant to both.

### P26 — resolved: **C-AB** — the retirement DISCRIMINATION: B-M′ right, B-A″ loses its THIRD · RUN 7 CLOSES
    observed:         `panewire-concord`: two windows, one authority — the same (input, edits) run
                      twice lands the IDENTICAL composed witness (an edit in one view seen in the
                      other) while a different edit stream diverges, AND a tampered edit woven into
                      the stream refuses mid-loop with the replica byte-unchanged and the avatar's
                      walk unperturbed — "equal-or-refuse under play." The whole arc composed:
                      panelight's tick + wire's equal-or-refuse + driftgaze's verified acquisition —
                      interactive==batch FUSED with equal-or-refuse, the two-law C-AB join B-M′
                      priced 40. B-A″ priced representation-first (C-REP 30) and LOST.
    tournament / RETIREMENT: this was a retirement-eligible discrimination and B-M′ won it — B-A″'s
                      THIRD consecutive losing discrimination (P22, P23, P26). Weights: B-M′ ~0.78,
                      B-A″ ~0.22 — now BELOW the 0.20-adjacent floor... EXACTLY: recompute — C-AB
                      likelihoods B-A″ 35 / B-M′ 40 give w(B-A″) = 0.22 × 35 / (0.22×35 + 0.78×40) =
                      0.198 < 0.20. BOTH retirement conditions MET (≥3 consecutive losses AND
                      w < 0.20). **B-A″ RETIRES.** The tournament collapses to a single surviving
                      basis, B-M′.
    census:           run-7 v_D = 0,0,0 (P24/P25/P26 — approximation strengthened not minted; no new
                      family) — RUN 7 CLOSES on a second consecutive triple zero. Meta ¬M-1: 24 for
                      24. CHECKPOINT 7 fires next and faces the CONVERGENCE DECISION: B-A″ retired
                      (one of the two blocking questions resolved), leaving only the scheduling-axis
                      mint (priogov) between the engine and a declared — single-basis, honestly
                      caveated — convergence.

## CHECKPOINT 7 — the CONVERGENCE DECISION opens (2026-08-04): sole basis, one mint question

**Gauntlet.** B-M′ is now the SOLE surviving basis (B-A″ retired at P26 under its frozen dual
condition: ≥3 consecutive losing discriminations AND w < 0.20). Test A (compression): B-M′ clean —
0 exceptions over the scored joints. Tests B (prediction) and C (stability, G(n) turning) pass. Test
D — "a plausible competing basis testable against future READs" — is now VACUOUS BY RETIREMENT: no
live rival remains to falsify B-M′, which is exactly L61's empty answer turned on the engine's own
convergence criterion. **This is the honest cost of the retirement, recorded as such: single-basis
convergence is STRICTLY WEAKER than rival-tested convergence — nothing alive can now contradict the
sole basis, so its survival is cheap.** The retirement was earned by rule (three losses + weight
floor), not chosen; the weakness it introduces is stated, not hidden.

**The last open mint question.** Convergence had TWO frozen blockers; the retirement cleared one. The
other is the SCHEDULING-AXIS mint. That axis has ONE preregistered sighting — `govern` (P10,
non-scoring: "a per-tick conservation of work, admitted + deferred == all"). By the SAME mint rule the
approximation axis was held to (checkpoint 4: TWO independent preregistered carriers → mint), the
scheduling axis needs a SECOND carrier. Computed fresh this checkpoint (never carried from prose — the
operator drift the P8 erratum caught): the frozen selector's next joint is `priogov` (URDROPC3,
"PRIORITY work governor"), in-degree 1, lex-first of the six in-degree-1 unbriefed modules {priogov,
recirc, slo, testament, traj, view_witness} — the OPC family's THIRD member (opcost → govern →
priogov) and the natural second carrier. So the convergence decision is DECIDABLE by the very next
READ, neither bendable nor pre-decidable:

    FROZEN MINT CONDITION (scheduling axis). The scheduling axis MINTS iff `priogov` reads as an
    INDEPENDENT carrier of a scheduling seam — a PRIORITY/DEADLINE-ordered admission of work, distinct
    from opcost's cost-ENVELOPE (a bound on total work) and from govern's CONSERVATION (admitted +
    deferred == all): priogov must certify that work is admitted in a CERTIFIED ORDER (priority or
    deadline is provably honoured), not merely bounded or conserved. If it does, govern (carrier 1) +
    priogov (carrier 2) reach the two-carrier bar and the axis mints — the arc's SECOND minted seam
    family after approximation. If priogov reads as a govern-VARIANT (the same conservation law with
    priority as an uncertified policy knob), it is NOT a second carrier, the axis does NOT mint, and
    convergence stays blocked pending a later scheduling carrier (schedule / slo / clslo). Recorded
    either way; the engine may not declare the mint by fiat.

    ON MINT: with the sole-basis caveat already carried, convergence becomes DECLARABLE — both frozen
    blockers cleared (B-A″ retired, scheduling axis minted). The declaration is single-basis, honestly
    weaker than rival-tested, and names its DEFERRED strengthening: a fresh adversarial challenger,
    NOT built speculatively (L58).

Checkpoint 7 does not declare convergence; it FRAMES the decision and freezes its one remaining input.
Batch 7 reads that input.

## BATCH 7 FREEZE — P27 + P28 + P29 (all sealed before any READ)

**Batch rules**: order priogov → recirc → slo (frozen selector: in-degree 1 each, lex asc, priogov <
recirc < slo). Sole basis B-M′ (B-A″ retired) — no discrimination is possible, so every joint is
retirement-neutral by construction and is scored only on the v_D (new-family) census and the meta.
Run-8 v_D fresh. L61 vacuity rule applied. Meta predicts ¬M-1 on all three (24 for 24).

### P27 — `priogov` (SCORING) — role: "PRIORITY work governor (T3.31)" (URDROPC3); ambient disclosed:
    the OPC family (opcost URDROPC1 cost-envelope — P1; govern URDROPC2 conservation — P10, the
    scheduling-axis first sighting); `schedule` (age-first, starvation-free) is family; the LAT chain
    (horizon/slo/clslo) is adjacent. Body and history UNREAD. **THE CONVERGENCE-GATING JOINT.**
    partition:        C-ORD (a certified priority/deadline ORDER of admitted work central — the
                      scheduling axis's second carrier; v_D=1, MINTS the axis) · C-PRICE (a per-tick
                      work PRICE/budget central — the cost family repeating, a govern-variant; v_D=0,
                      no mint) · C-EQ (a priority-schedule ≡ reference-schedule equivalence central) ·
                      C-INV (a work-conservation structural invariant central — govern's law verbatim;
                      v_D=0) · R-M · R-O.
    credences:        author (= B-M′, sole basis): C-ORD 45 · C-PRICE 25 · C-EQ 10 · C-INV 12 · R-M 4 ·
                      R-O 4. The role's word "PRIORITY" and the distinct URDROPC3 code weight C-ORD over
                      the govern-variant readings — but the mint is EARNED only if the source certifies
                      an ORDER, not merely a priority-labeled budget. Frozen so the READ decides, not
                      the credence.
    mint call:        v_D=1 (scheduling axis mints) is the author's call at 0.45; the FROZEN condition
                      above, not this number, adjudicates it on the READ.

### P28 — `recirc` (SCORING) — role: "Kleene recirculation — THERE IS NO LOOP, and closing it would
    weaken fraud detection" (URDRRCC1); ambient: `jurisdiction`'s Kleene fixed point (four predicates
    one object) is family; the role STATES a negative. Body and history UNREAD.
    partition:        C-FLOOR (a soundness-of-absence result central — "no loop is the correct answer
                      and a closed loop would be worse"; the ashdepth/vacuity-law inversion pattern) ·
                      C-INV (a fixed-point structural invariant central — the closure already sits at
                      its least fixed point) · C-R (a refusal/admission predicate central) · R-M · R-O.
    credences:        author (= B-M′): C-FLOOR 45 · C-INV 30 · C-R 12 · R-M 6 · R-O 7. The role states a
                      negative, so soundness-of-absence leads; v_D=0 expected — recirc strengthens L61's
                      vacuity carriers rather than minting a family.

### P29 — `slo` (SCORING) — role: "Composite worst-case latency SLO (T3.33)" (URDRLAT2); ambient: the
    LAT family (horizon URDRLAT1 — P7, the cost family's third instance; clslo URDRLAT3;
    storecost/persist/resurrect LAT4–6); a COMPOSITE bound. Body and history UNREAD.
    partition:        C-PRICE (a worst-case latency BOUND/price central — the cost family, a fourth
                      preregistered instance; v_D=0) · C-EQ (a composite-bound ≡ sum-of-parts
                      equivalence central — the composition pattern) · C-ORD (if slo certifies a
                      scheduling ORDER, a third scheduling carrier; v_D=1) · C-INV · R-M · R-O.
    credences:        author (= B-M′): C-PRICE 40 · C-EQ 30 · C-ORD 10 · C-INV 8 · R-M 6 · R-O 6. A
                      "composite worst-case bound" reads as cost/price composition — the LAT family's
                      bound arithmetic; v_D=0 expected. If the composite bound is EXACT (worst-case of
                      the composite == the composed worst-cases), C-EQ; else C-PRICE.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P27 — resolved: **C-ORD** — the SCHEDULING AXIS MINTS · the arc's second minted seam family
    read:             2026-08-04, the blind READ (run 8, the convergence-gating joint). Classified from
                      the LIVE `priogov*` gate rows per the frozen partition — never from prose.
    observed:         `priogov` certifies a CERTIFIED PRIORITY ORDER, not a govern-variant. The rows:
                      `priogov:scenes` (three schedules reproduce URDROPC3 digests); `priogov-never-
                      overrun` (every admitted tick's work <= budget across budgets a..5a — govern's
                      cost law, preserved); `priogov-priority-fair` (the NEW law: with fresh priorities
                      the top actor is served tick 1 and the lowest last, a priority-ordered PREFIX
                      where no lower jumps a deferred higher; and NO-STARVATION — aging raises effective
                      priority = base + age_step*wait without bound, so every actor is served in <= N
                      ticks); `priogov-refuse` (a single over-budget actor is a hard OPCOST-REFUSE). The
                      `priogov_digest` binds the per-actor served schedule, so a defect in the ORDER
                      moves it — the order is MEASURED, not an uncertified policy knob.
    mint:             THE FROZEN MINT CONDITION FIRES. priogov admits work in a CERTIFIED ORDER
                      (priority provably honoured: top served tick 1, digest-bound) with a BOUNDED WAIT
                      (<= N via aging) — distinct from opcost's cost-ENVELOPE (a bound on total work)
                      and govern's CONSERVATION (admitted + deferred == all). govern (P10, carrier 1,
                      the scheduling sighting) + priogov (carrier 2, the certified-order carrier) reach
                      the TWO-CARRIER bar the approximation axis was held to (checkpoint 4). **THE
                      SCHEDULING AXIS MINTS — the arc's SECOND minted seam family after approximation.**
                      v_D = 1.
    unnamed (M-0):    priority-buys-ORDER-never-EXCLUSION (aging converts a priority preference into a
                      liveness guarantee — structural, not a tuned anti-starvation patch); the
                      clean-PREFIX discipline (a non-fitting actor STOPS the tick, it is not skipped for
                      a lower one — the schedule stays a priority prefix, not a budget-filling packing).

### P28 — resolved: **C-FLOOR** — "there is no loop"; the ashdepth inversion, a second vacuity carrier
    read:             2026-08-04, the blind READ (run 8). Classified from the LIVE `recirc*` rows.
    observed:         `recirc` refutes TWO claims attached to an elegant proposal, and both INVERT. The
                      rows: `recirc:scenes` (closure/collapse/plants/salvage reproduce URDRRCC1
                      digests); `recirc-law` (extensive + monotone + IDEMPOTENT — γ∘α is a closure
                      operator by the adjunction, so the Kleene iteration reaches its fixed point in AT
                      MOST ONE STEP for every input: step counts 1,1,1,1,1,1,0,0, a CONSTANT that cannot
                      encode a per-capture defect; AND the COLLAPSE — 400 distinct raw capture-sets to 5
                      fixed points, an honest capture and a doctored one with a single obligation
                      dropped sharing the SAME closure); `recirc-selftest` (the plants bite: the
                      step-count-as-defect is constant, and fixed-point equality conflates the
                      honest/doctored pair raw equality distinguishes). The salvage (refine the LEVEL
                      when the iteration stalls) is genuinely multi-step, bounded by the level ladder and
                      floored at ashdepth's k_min.
    class:            C-FLOOR — the soundness-of-absence result: THERE IS NO LOOP. The elegant
                      recirculation collapses to a single forward step (idempotence) AND closing it
                      would be DANGEROUS (fixed-point equality is a strictly WEAKER integrity check,
                      raising false negatives on the omission attack geoquorum catches). The absence of
                      a loop is the correct architecture; the residue is a terminal hand-off, not a
                      queue. The ashdepth pattern (P17) recurring — a handed-down elaboration refuted by
                      measurement, the empty answer made non-vacuous by MEASURING that the loop would
                      HARM. v_D = 0: a second vacuity carrier (strengthens L61), does not mint.
    unnamed (M-0):    the DANGEROUS-ELEGANCE observation (the more-principled-looking check is a
                      regression) — a candidate to WATCH (like C-SPLIT), not a mint: it is the arc's
                      measurement-refutes-seduction method, not a distinct seam family (L3).

### P29 — resolved: **C-PRICE** — the Stage-H latency closer; the cost family's fourth instance · RUN 8 CLOSES
    read:             2026-08-04, the blind READ (run 8). Classified from the LIVE `slo*` rows.
    observed:         `slo` composes the Stage-H arc into ONE certified worst-case number. The rows:
                      `slo:scenes` (meets/tight/fails reproduce URDRLAT2 digests); `slo-composition`
                      (worst_case_latency == admission_wait + rollback window — the two bounded parts,
                      an EXACT identity); `slo-soundness` (admission_wait UPPER-BOUNDS the governor's
                      actual drain over a config corpus — a SOUND over-approximation, so the number is a
                      real guarantee, not an optimistic estimate — and a within-target config admits);
                      `slo-refuse` (an over-target config is SLO-REFUSE: a promise is kept or declined,
                      never broken).
    class:            C-PRICE — a composite worst-case latency BOUND with a refuse, the cost/latency
                      family's FOURTH preregistered instance (opcost, horizon, govern, slo). Two
                      supporting characters, neither minting: the composition is an EXACT identity
                      (C-EQ-flavored assembly — worst_case == the sum of its two bounded parts), and the
                      soundness is the APPROXIMATION axis touched a fourth time (admission_wait ⊇ actual
                      drain). slo uses the FIFO governor's UNIFORM bound, NOT priogov's per-class order
                      (stated in its does_not_show) — so it is NOT a scheduling-ORDER carrier. v_D = 0.
    census:           run-8 v_D = 1, 0, 0 (P27 MINTS the scheduling axis; P28/P29 no new family) — RUN 8
                      CLOSES. Meta ¬M-1: 27 for 27 (each of the three surfaced unanticipated structure —
                      priogov's liveness-from-aging, recirc's dangerous-elegance, slo's approximation
                      touch the frozen partition did not name). The scheduling axis is the arc's SECOND
                      minted seam family, and B-A″ retired at P26 — so BOTH frozen convergence blockers
                      are now cleared.

## CONVERGENCE — DECLARED (single-basis, honestly caveated): the frozen conditions fired

The two frozen blockers checkpoint 6 and checkpoint 7 named are both cleared, by RULE not fiat:
  (1) B-A″ RETIRED at P26 — its dual condition fired (≥ 3 consecutive losing discriminations AND
      w < 0.20). Sole surviving basis: B-M′ ("input × semantics").
  (2) The SCHEDULING AXIS MINTED at P27 — govern (carrier 1) + priogov (carrier 2) reached the
      two-carrier bar, the same bar the approximation axis met at checkpoint 4.

The discovery engine has reached a FIXED POINT under its own frozen rules: a stable working basis
(B-M′), a seam-family taxonomy with TWO members earned by independent preregistered recurrence
(approximation, scheduling), and a meta signature 27-for-27 (¬M-1: no blind prediction lands perfectly
clean — the missed-dimension law held across the whole run). **CONVERGENCE IS DECLARED.**

THE HONEST CAVEATS, carried in the declaration, never traded away:
  * SINGLE-BASIS. B-A″'s retirement means NO live rival remains to falsify B-M′; single-basis
    convergence is STRICTLY WEAKER than rival-tested convergence (L61 — an answer nothing can
    contradict is cheap). The DEFERRED strengthening is a fresh adversarial challenger, generated to
    attack B-M′ on its own axes; it is NOT built speculatively (L58), and until it exists the
    convergence is provisional against exactly that.
  * A SMALL TAXONOMY. Two minted families is convergence of the ENGINE (it has stopped surfacing new
    families under the frozen selector at this cadence), NOT a claim that the Urðr architecture is
    fully mapped. Modules remain unread; the selector will keep proposing joints, and a future READ
    that mints a THIRD family would REOPEN the engine — the convergence is falsifiable by its own
    continued operation.
  * WHAT CONVERGED. The DISCOVERY ENGINE converged, not the arc. The claim, MEASURED and gradable:
    reading modules in frozen-selector order, under a single surviving basis, no longer changes the
    basis or the family set — the predictions have become routine confirmations (the 27-for-27 meta).
    That is all that is claimed.

The engine does not stop; it changes PHASE. Post-convergence, further READs are CONFIRMATIONS under
B-M′ until either a third family mints (reopening discovery) or the deferred challenger is built
(re-arming the tournament). Both are frozen, decidable, and unbuilt — recorded, not performed.

## CHECKPOINT 8 — the DEFERRED CHALLENGER, attempted and FAILED by measurement (2026-08-04)

Checkpoint 7 declared convergence with one named deferred strengthening: a fresh adversarial
challenger, to convert single-basis convergence into rival-tested convergence. **Checkpoint 8
attempted it. The attempt failed, mechanically, and the failure is the checkpoint's finding.**
Witness: `nullbase.py` (stdlib-only, exhaustive over the pinned joints, rerun byte-identical).

**The construction, frozen before scoring.** Two challengers were built to attack B-M′ at its weakest
RECORDED point — C-AB is the MODAL outcome (11 conjunctive of 27 scoring joints) yet B-M′ prices it
with an auxiliary TIE RULE rather than a cell of its (input × semantics) grid. Each predicts the
CONJ/SINGLE sub-question from data B-M′ does not use, so neither is a relabeling:

    B-C1  TOPOLOGICAL (arity) — a central law preserving >= 2 already-certified laws is conjunctive;
                               mechanized as import out-degree over tools/terrain (outdeg >= 2 -> CONJ).
    B-C2  PHASE-POSITION     — a module at an arc boundary (its OWN docstring declaring opener /
                               capstone / closes) is conjunctive; mid-phase rungs are single-semantics.

Both scored MECHANICALLY — the prediction comes from the import graph or the module's own
self-description, never from the author's judgment, which is precisely the bias the mechanization
exists to remove. Scoring a rival I invented, by a rule I apply case-by-case, would be theater.

**THE NULL BASELINE — the actual finding, and it is pointed at the method, not the rivals.** A
tournament between bases says which RIVAL is better; it never says whether ANY of them is good. The
trivial baseline is the CONSTANT PREDICTOR (always answer the majority class). MEASURED:

    NULL (always SINGLE)   16/27 = 59%   <-- the bar
    B-C2 phase-position    15/27 = 56%
    B-C1 topological       10/27 = 37%

**BOTH CONSTRUCTED CHALLENGERS SCORE BELOW THE CONSTANT PREDICTOR.** They are not weak rivals; they
are anti-informative on this task. The challenger construction failed by MEASUREMENT — not by the
author declining to build it (L58 would have licensed declining; it did not license pretending).

**What this does and does not establish** — the boundary, stated before anyone can overread it:
  * It does NOT upgrade the convergence. No live rival was produced, so B-M′ still stands
    unfalsified-because-unopposed, exactly as checkpoint 7 recorded. Convergence remains SINGLE-BASIS.
  * It DOES convert "no rival exists" from an ASSUMPTION into a MEASUREMENT over a named, frozen lens
    set. Two independent structural readings were built to attack, and both landed below baseline.
  * It does NOT prove no rival exists. Two lenses of unboundedly many, and both STRUCTURAL (graph
    topology, declared phase position). SEMANTIC lenses are untested HERE precisely because scoring
    them needs the author's judgment — the bias mechanization removed. An absence measured over two
    lenses is evidence, not proof. `declared ≠ verified`.

**L62 — THE NULL-ENTRANT LAW (minted, n=1 and applied in the same breath).** The ledger has scored
bases against EACH OTHER since run 1 — Brier, posteriors, discriminations, retirement — and never once
against a trivial baseline. A basis that beats its rivals while losing to the constant predictor has
explanatory power that is UNEARNED, and no amount of head-to-head scoring can reveal it: the
tournament is a RELATIVE instrument reporting an ABSOLUTE-sounding verdict. This is L61's vacuity law
one level up — L61 asked whether a rival can LOSE; L62 asks whether a winner beats NOTHING-AT-ALL.
The null entrant belongs in the tournament from the start.

    APPLIED IMMEDIATELY, and the honest limit stated: B-M′ has NOT been scored against a null on its
    OWN task. B-M′ predicts a multi-class CELL scored by Brier over frozen credences — not this binary
    — so the 59% bar does not transfer, and claiming B-M′ passed or failed it would be a category
    error. What is now known: the two challengers lose to the null on the binary task; whether B-M′
    beats a null on its multi-class task is an OPEN, DECIDABLE question requiring a maximum-marginal
    null (always predict the modal cell) scored by the same Brier rule over the same 27 joints. That
    measurement is FROZEN as checkpoint 9's obligation and deliberately NOT run here — running it in
    the same breath that minted the lesson would let the lesson's author choose its first verdict.

**Selector edge case, ruled BEFORE it arrives (freeze-before-history applied to the selector itself).**
The frozen selector's frontier after batch 8 falls to in-degree 0, where the ordering signal is gone
and the order is pure lex. First in that tail is `bench` — which is DELIBERATELY UNGATED (wall-clock,
MEASURED-on-named-host, and it may never enter a byte-identical gate). Ruling, frozen now while it is
inconvenient rather than later when it is convenient: **`bench` is NOT READ-ELIGIBLE.** Classification
in this pass is from LIVE GATE ROWS, and a module with no rows is unclassifiable — reading it would
force classification from prose, which is the one thing this pass forbids (`claim ≠ code`). It is
skipped with this reason recorded, not silently passed over. The in-degree-0 tail also means the
centrality ordering has been EXHAUSTED — a structural fact about the read pass worth its own note at
checkpoint 9.

## BATCH 8 FREEZE — P30 + P31 + P32 (all sealed before any READ)

**Batch rules**: order testament → traj → view_witness (frozen selector, recomputed fresh: in-degree 1
each — the LAST three in-degree-1 modules — lex asc; `lease`=4 recalibrated the method against the P8
erratum). Sole basis B-M′; no discrimination is possible, so all three are scored on the v_D
(new-family) census and the meta only. Run-9 v_D fresh. L61 vacuity rule applied. Meta predicts ¬M-1
on all three (27 for 27).

### P30 — `testament` (SCORING) — role: "Durable intent (T3.44) — the write that survives its writer"
    (URDRTST1); ambient disclosed: the lease/rannull authority family (`lease` — P8, C-INV, the standing
    lease; `rannull` RAN-0 authority nullity); durable-intent sits after the lease in the named chain.
    Body and history UNREAD.
    partition:        C-INV (a durability/survival structural invariant central — the write outlives the
                      authority that made it, the lease family's continuation) · C-EQ (a
                      replay/recovery equivalence central — the persist/resurrect pattern) · C-R (a
                      typed admission of the durable write central) · C-AB · R-M · R-O.
    credences:        author (= B-M′, sole basis): C-INV 40 · C-EQ 22 · C-R 20 · C-AB 10 · R-M 4 · R-O 4.
                      "Survives its writer" reads as a structural continuity invariant — B-M′'s founding
                      axis (hand, lease) — but the durable half could equally be a recovery equivalence.
                      v_D=0 expected (the authority/continuity family is long established).

### P31 — `traj` (SCORING) — role: "Certified TRAJECTORY OBSERVER (T3.12)" (URDRTRAJ1); ambient: the
    observer family (`gaze` — P14, C-R, the certified first-person observer; `drive` — P9, C-REP, the
    movement transcript; `view_witness` the citation contract). An OBSERVER, and the arc's observers
    have been police (gaze) and representation (drive) in different rungs. Body and history UNREAD.
    partition:        C-REP (a trajectory REPRESENTATION/transcript central — the drive pattern) · C-R
                      (an observer-admission predicate central — the gaze pattern) · C-EQ (an
                      observed-trajectory ≡ executed-trajectory equivalence central) · C-INV · R-M · R-O.
    credences:        author (= B-M′): C-REP 32 · C-R 25 · C-EQ 25 · C-INV 10 · R-M 4 · R-O 4. The
                      genuinely open one of this batch — the observer family has split C-REP/C-R before,
                      and "certified observer" underdetermines which. Frozen deliberately near-flat so
                      the READ decides. v_D=0 expected.

### P32 — `view_witness` (SCORING) — role: "The citation contract (T3.6) — the declared view must CITE"
    (URDRTVW1); ambient: the D15 view-export FIREWALL (`terrain_view`, same URDRTVW1 code — the MAGIC
    collision the index pass found); the firewall/citation family. Body and history UNREAD. NOTE: one of
    the four TRUE CONFORMANCE GAPS (gate stage + falsifiers, no pinned corpus of its own) — a
    structurally different rung from the 29 read so far, and the first such joint in the pass.
    partition:        C-R (a citation/admission predicate central — the declared view REFUSES without a
                      citation) · C-INV (a firewall structural invariant central — no view escapes
                      uncited) · C-EQ · C-FLOOR (a soundness-of-absence result) · R-M · R-O.
    credences:        author (= B-M′): C-R 45 · C-INV 28 · C-EQ 10 · C-FLOOR 8 · R-M 4 · R-O 5. "Must
                      CITE" reads as police over representation — B-M′'s founding cell. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P30 — resolved: **C-EQ** — death is invisible to the ANSWER; the author's leading call LOST
    read:             2026-08-04, the blind READ (run 9). Classified from the LIVE `testament*` rows.
    observed:         `testament-death` is the central row and it is an EQUALITY: a REAL successor
                      process, given nothing but the store and an address, performs probate over a
                      disk-only channel and its output is BIT-IDENTICAL to the never-died admission,
                      twice. `testament-probate` states it inward — probate == the living admission ==
                      the global reproof — so everything the lease law proved is INHERITED (lost-update
                      impossibility, amortized == reproved, interval transport). The testament is 144
                      bytes (MAGIC | regional record | SHA-256) and NOTHING more, because the lease is
                      DERIVABLE from the record's parent digest + region. EXACTLY-ONCE is free rather
                      than added (the admission moves the very authority the testament names, so a
                      second probate refuses), and the refusal SPEAKS in three flavors — executed /
                      distributed / unadjudicable — each earned from evidence, never guessed from its
                      absence. `testament-refuse` holds the corruption battery; the executor is PURE (a
                      refused probate leaves the store byte-identical).
    class:            C-EQ. The author priced C-INV 40 (a durability/continuity structural invariant —
                      B-M′'s founding axis) and C-EQ 22. **The leading credence LOST to its own
                      second-place call.** Recorded plainly: "survives its writer" is the MOTIVATION;
                      the certified law is a recovery EQUIVALENCE (persist/resurrect) extended from
                      state to INTENT. A role sentence saying WHY a rung exists is weak evidence for
                      WHAT its central row certifies — `claim ≠ code`, turned on the author's own
                      prediction. v_D = 0 (the recovery-equivalence family is long established).
    unnamed (M-0):    the three-flavor refusal adjudicated from RETAINED evidence (the geoquorum
                      discipline — a refusal must say which kind it is — reaching the durability
                      layer); the derivable-lease minimality (carrying it would invite incoherence;
                      derived data is checkable data); executor purity.

### P31 — resolved: **C-R** — the horizon observer polices; the second leading-class miss
    read:             2026-08-04, the blind READ (run 9). Classified from the LIVE `traj*` rows.
    observed:         `traj-properties` certifies an ADMISSION verdict: a sequence of partial views is
                      admitted iff EVERY innovation ν(k) = image(k) − H(k)·trajectory(k) is exactly the
                      zero vector, else the first nonzero tick is a typed REFUSE (`traj-refusal`). Exact
                      integers, divisibility-free — confirmed or fought, never rounded. The observer
                      reconstructs the authoritative trajectory ITSELF (the Φ-fold of lockstep inputs,
                      the same law the authority runs), so a frame is checked against a LOCALLY-DERIVED
                      truth, not a trusted one. Two things `gaze` structurally cannot do follow:
                      PARTIAL COVERAGE is admissible (the dynamics carry unobserved axes into observed
                      ones over the horizon; `gaze` refuses each such frame GAZE-NONCOVER) and TEMPORAL
                      REPLAY is caught.
    class:            C-R — police over representation, the `gaze` pattern extended from a SNAPSHOT to a
                      HORIZON observer. The author priced C-REP 32 · C-R 25 · C-EQ 25, frozen
                      deliberately near-flat because the observer family had split C-REP/C-R before;
                      the leading call missed again, the batch's second. v_D = 0.
    unnamed (M-0):    SAME-WHERE-DIFFERENT-**WHEN** — a frame that is entirely content-valid (a faithful
                      view of a pose the actor genuinely held at ANOTHER tick, which is `gaze`'s own
                      does_not_show, "identity is content") is REFUSED, because Φ predicts a different
                      pose at this tick. The sequence IS Φ, closing a gap `gaze` explicitly deferred.
                      Also: the locally-derived truth is the NEUTRAL-RULER pattern a fourth time
                      (mesh's monolith oracle, wardhom's cross-language identity, terraform-as-oracle) —
                      the checker structurally denied the option of trusting what it checks.

### P32 — resolved: **C-R** — the citation contract; the leading call lands · RUN 9 CLOSES
    read:             2026-08-04, the blind READ (run 9). Classified from the LIVE `view-witness*` rows.
    observed:         `view-witness:cite` certifies that a DECLARED view may not MISQUOTE the authority
                      it names: the digests the view prints as measured must EQUAL the live digests
                      recomputed from the authority modules (an exact equality; a one-hex-flip forgery
                      reddens), with typed VIEW-REFUSE for a missing blob, a non-hex or wrong-length
                      witness, or a missing required citation. `view-witness-firewall` certifies the
                      structural half: the declared knobs are a namespace DISJOINT from the authority
                      and the presentation digest is anchored on the authority witness, so a knob moves
                      the view and never the witness. Versioned overlays inherit the guarantee (VIEWS
                      is a list). The render itself is NOT certified and is not claimed to be.
    class:            C-R — police over representation, B-M′'s founding cell; the author's 45 landed,
                      the batch's ONLY clean leading call. v_D = 0.
    unnamed (M-0):    THE DUAL — D15/`terrain_view` proves the view cannot CONTAMINATE the authority
                      (nothing flows inward); this proves it cannot MISQUOTE it (nothing false flows
                      outward). Neither alone suffices: an honest one-way membrane still permits a lie
                      about what is on the other side. Also structural: this is the first joint drawn
                      from the arc's four TRUE CONFORMANCE GAPS (stage + falsifiers, no pinned corpus),
                      and the read found nothing hiding there — the citation equality is exogenous to
                      any corpus BY CONSTRUCTION (it recomputes the authority live rather than
                      comparing to a pinned digest), so the missing corpus is a design choice, not a
                      debt. One of the four named gaps is thereby explained rather than merely listed.
    census:           run-9 v_D = 0, 0, 0 — RUN 9 CLOSES on a THIRD consecutive triple zero, the
                      strongest convergence signal the census can emit. Meta ¬M-1: 30 for 30 (all three
                      surfaced unanticipated structure). **BATCH SIGNATURE, recorded because it cuts
                      against the incumbent: TWO of three leading credences MISSED (P30 C-INV→C-EQ,
                      P31 C-REP→C-R).** Under a live tournament those two joints would have been
                      discriminations with real information in them; with B-A″ retired and the
                      checkpoint-8 challengers dead below baseline, there was no rival positioned to
                      profit. That is the single-basis weakness made concrete rather than abstract — the
                      sole basis mispriced two joints in a row and paid nothing for it.

## CHECKPOINT 9 — PREREGISTRATION (frozen BEFORE any score exists): the incumbent against its own null

L62 obliged this and deliberately left it unrun, because minting a lesson and choosing its first
verdict in the same breath is the conflict the lesson forbids. This block is the SPEC, frozen and
committed before `multinull.py` is written or executed. Everything below is decided in advance; the
verdict section is empty until the run fills it.

**Unavoidable disclosure, stated first.** This is a RETROSPECTIVE scoring of already-resolved joints,
so the outcomes were necessarily known to the author before the spec was written — the blindness L59
protects cannot apply here and is not claimed. What CAN be protected is the DEGREES OF FREEDOM: the
pseudocount, the class space, the catch-all mapping, the incumbent selection rule, the corpus, and the
reporting are all fixed HERE, so the one thing the author cannot do is tune them until the answer is
agreeable. That is the honest form of preregistration available to a retrospective measurement, and it
is weaker than a blind freeze. `declared ≠ verified`.

**THE CORPUS — 22 scoring joints, and why exactly these.** Every joint carrying BOTH a frozen credence
vector and a resolved outcome: P9, P11–P18, P20–P32. P10 (`govern`) and P19 (`cpredict`) are excluded
because the LEDGER declared them NON-SCORING for disclosed contamination at their own freeze — the
exclusion is the ledger's rule applied, not a selection made now. P1–P8 carry no multiclass credence
vector (run-1 predates the credence format; the format was adopted at run 2) and are excluded as
UNSCORABLE-BY-FORMAT, not as inconvenient. The corpus is thereby determined by two pre-existing rules
and contains no case-by-case admission.

**THE INCUMBENT — the B-M-lineage vector of record at each freeze.** P9–P17 use `B-M`; P18–P26 use
`B-M′`; P27–P32 use the sole-basis line the ledger itself labels `author (= B-M′)`. No joint's
incumbent is chosen; each is the merged basis's own frozen row at that time. Where a vector's integer
percents do not sum to 100 it is NORMALIZED by its own total, and any such joint is REPORTED (a
malformed frozen vector is a data-quality fact, not something to silently repair).

**THE NULL — a rolling empirical marginal, no future leakage.** For joint j in chronological order,
over that joint's OWN frozen class set C_j:

    q_j(c) = ( N_{j-1}(c) + α ) / ( Σ_{c' ∈ C_j} N_{j-1}(c') + α·|C_j| )   for c ∈ C_j,  **α = 1**

where N_{j-1}(c) counts how often class c was the OBSERVED outcome across joints strictly BEFORE j.
The null therefore knows only the frozen partition (available pre-outcome) and the history to date. It
is explicitly NOT the retrospective modal class over all 22 — that would leak later outcomes into
earlier predictions, and the first joint's null is deliberately uniform because nothing precedes it.
α = 1 (Laplace) is fixed now and is not tuned.

**THE CATCH-ALL MAPPING, frozen because it cuts against the incumbent.** L60 mandates a catch-all
OTHER in every partition. If a joint's observed class is NOT among its frozen named classes, it maps
to that catch-all (`R-O`, else `R-M` if `R-O` is absent). This is known to bite at least once — P21
resolved C-SPLIT, a class its own partition never named — and the rule PENALIZES the incumbent there
(it priced the catch-all at 5). Frozen in this direction deliberately: the alternative (crediting the
incumbent for a class it did not name) would be scoring the author's hindsight, not the basis.

**THE RULE — the same proper score for both, no exceptions.** Brier over C_j:

    BS(p_j, y_j) = Σ_{c ∈ C_j} ( p_j(c) − 1[c = y_j] )²        Δ_null = Σ_j BS(q_j,y_j) − Σ_j BS(p_j,y_j)

**THE VERDICT PARTITION (exhaustive, L60), frozen with its meaning:**
  * **Δ_null > 0** — the incumbent carries earned predictive value over class frequencies. Convergence
    keeps its predictive-adequacy leg; the structural leg was already recorded.
  * **Δ_null = 0** — no earned predictive value; the basis is a redescription of the class prior.
  * **Δ_null < 0** — the basis is WORSE than ignorance-with-frequencies. Convergence would then be
    largely CLASS-PRIOR EXPLOITATION, and the declaration of checkpoint 7 would have to be re-graded
    on its predictive leg — the structural findings (two minted families) would stand, since they rest
    on recurrence, not on scoring.

**ALSO REPORTED, because a single scalar hides the failure modes** (`panel ≠ scalar`): leading-class
accuracy for both; per-joint paired differences and the SIGN COUNT (joints won/lost/tied), so a total
driven by one outlier is visible; calibration and sharpness reported SEPARATELY, since a basis can beat
the null while being badly calibrated. **No significance claim is made at n = 22** — the numbers are
DESCRIPTIVE, and calling a 22-joint retrospective difference significant would be the inflation this
ledger exists to refuse (L20 sample ≠ universal).

**NON-VACUITY (L61).** The corpus must contain more than one distinct observed class, or "the null
wins" would be an artifact of a one-class corpus rather than a result; the witness asserts this and
reads STARVED if it fails.

**Witness**: `exe_epistemics/multinull.py` — stdlib-only, deterministic, exhaustive over the corpus,
parsing the frozen vectors from this ledger rather than from any hand-copied table, rerun
byte-identical. **VERDICT: recorded in the resolution block below, written only after the run.**

### CHECKPOINT 9 — resolved: **Δ_null > 0** — the incumbent carries EARNED predictive value

    run:              2026-08-04, after the spec commit. Integer Brier (/10⁸ units), 22 joints.
    verdict:          **Δ_null = null − incumbent = 1 889 667 650 − 1 336 458 804 = +553 208 846 > 0.**
                      By the frozen partition this is branch one: **the incumbent carries earned
                      predictive value over class frequencies.** The apparent convergence is NOT
                      largely class-prior exploitation — the branch the preregistration named as the
                      one that would have forced a re-grade of checkpoint 7's predictive leg.
    panel (never one scalar): per-joint sign count **incumbent won 15, lost 7, tied 0** — so the total
                      is not an outlier artifact; it is carried by a majority of joints.
                      Leading-class accuracy: **incumbent 15/22, null 4/22.**
                      Losses (the seed of the next rung's error corpus): P11, P12, P13, P15, P20,
                      P26, P30.
    THE PREREGISTRATION'S OWN CLAIM, FALSIFIED — recorded because it was wrong in this ledger's
                      favour-checking direction: the spec asserted the catch-all mapping "bites at
                      least once — P21 resolved C-SPLIT, a class its own partition never named."
                      **It never bit.** P21's frozen partition DID name C-SPLIT (vector: C-SPLIT 35 ·
                      C-AB 35 · C-R 20 · R-M 3 · R-O 7), and across all 22 joints the catch-all fired
                      ZERO times. The rule stays frozen and correctly implemented; the factual
                      parenthetical was simply false, and it is corrected here rather than edited out
                      of the spec (the ledger is append-only; a freeze is refuted by a successor,
                      never rewritten — the L23→L24 pattern). Consequence, stated because it cuts the
                      right way: the anti-incumbent safeguard cost the incumbent NOTHING, so the
                      favourable verdict is not an artifact of a lenient mapping.
    calibration — the finding that matters for the next rung: the incumbent's mean maximum
                      probability is **0.380** while its leading class is right **15/22 = 0.68**. The
                      basis is **systematically UNDERCONFIDENT**: it is substantially more accurate
                      than it claims to be. Its Brier is therefore beatable WITHOUT any new
                      structural insight — a pure sharpening of the frozen vectors would improve it.
                      That is a structured, mechanical residual, and it is the first direct evidence
                      that the engine's errors are PREDICTABLE rather than noise.
    sharpness:        incumbent 0.380, null 0.357 — the two are close, so the incumbent's advantage
                      comes from being RIGHT, not from being bolder. (A basis can beat a null by
                      confidence alone; this one did not.)
    data quality:     TWO frozen vectors do not sum to 100 — P22 and P23 both sum to 95. They are
                      normalized by their own totals and REPORTED rather than silently repaired; the
                      defect is in the frozen record and stays visible there.
    non-vacuity (L61): more than one observed class occurs, and the corpus is asserted
                      ASSEMBLED-BY-RULE-ONLY by the witness (`corpus_is_by_rule` → True), so no joint
                      was admitted or dropped case-by-case.
    what this does NOT establish, stated at the same volume as the verdict:
                      * NO SIGNIFICANCE. n = 22, retrospective. The numbers are DESCRIPTIVE; calling
                        this difference significant would be the inflation the ledger refuses (L20).
                      * NOT a blind test. The outcomes were known when the spec was written; only the
                        DEGREES OF FREEDOM were protected. Strictly weaker than an L59 freeze.
                      * NOT a validation of Urðr. This measures the DISCOVERY ENGINE's predictions,
                        not the arc's correctness.
                      * NOT a rival. Beating a null is a floor, not a tournament — L62's whole point
                        is that clearing the floor and having no live rival are different facts, and
                        both remain true simultaneously.
    convergence status: the review's two legs are now BOTH addressed — structural saturation (three
                      consecutive triple-zero runs, two minted families) and **predictive adequacy
                      above the null (measured here)**. The declaration stands, still single-basis,
                      and now with its predictive leg evidenced rather than assumed. The underconfidence
                      finding is the honest crack in it: a basis that is beatable by sharpening alone
                      has residual structure left to harvest.
    next (frozen):    Rung 2 — the ERROR SURFACE. Build `prediction_residuals.py`: a canonical,
                      byte-identical residual table over the 22 joints carrying, per joint, the frozen
                      vector, observed class, both Brier losses, leading-class hit, first-to-second
                      margin, whether unnamed structure appeared, and the mechanical error TYPE
                      (ranking / support / partition / resolution / calibration miss). The seven
                      recorded losses and the measured underconfidence are its first content. Only
                      after that table exists — and only if a frozen predictor of the engine's own
                      misses beats a null — does a synthesis operator earn existence (L58).

## CHECKPOINT 10 — the ORBIT SCALAR, researched: one disproof, one confirmation, NOT adopted

A reviewer proposed pairing the structural cost H = (R,F,D,C) with an ORBIT-RETURN scalar
Ω_t = min_{j<t−ℓ} d(S_t,S_j) over S_t = (𝓑_t, Π_t, 𝓡_t, 𝓜_t), plus a predictive-gain scalar
G_t = L_null − L_engine, combining into a STERILE-ORBIT detector: the engine returns near an earlier
organizational state AND has not improved against the null. The motivating question is exactly the one
this ledger could not answer after three triple-zero runs — **predictive fixed point, or single-basis
orbit with no available opponent?** Witness: `orbitprobe.py` (stdlib-only, rerun byte-identical).

**FINDING 1 — Ω AS SPECIFIED IS DEGENERATE HERE. A disproof, not a preference.** This ledger is
APPEND-ONLY by L2: a freeze is never rewritten and a resolution never retracted. So for every j < t,
𝓡_j ⊂ 𝓡_t and 𝓜_j ⊆ 𝓜_t, hence d_R = |𝓡_t \ 𝓡_j| = the joints resolved between them ≥ 3 per batch.
Therefore

    Ω_t ≥ 3(ℓ+1) > 0 for all t — the scalar can NEVER return to zero,

and since d_R grows strictly with distance, the minimizing j is ALWAYS the most recent admissible one.
**Ω_t measures ELAPSED BATCHES, not recurrence** — a clock wearing a topologist's clothes. The defect
is in the STATE VECTOR, not the idea: a return detector may not contain monotone-accumulating
components. THE REPAIR, stated and NOT built: define the state over the non-accumulating
CONFIGURATION — the multiset of error TYPES (not instances), live-basis identity/count, the minted
family SET, and the calibration shape. Return becomes possible then, because "sole basis,
underconfident, v_D=0, error-types {ranking, ranking, clean}" is a configuration that CAN recur.

**FINDING 2 — THE PROPOSAL'S PREMISE IS CONFIRMED BY MEASUREMENT.** Per-batch G, computed from the
checkpoint-9 corpus under the same frozen proper score (G/joint, /10⁸ units):

    b1 3.5M(—) · b2 10.1M(v_D=1) · b3 35.2M(1) · b4 8.5M(0) · b5 48.7M(0) · b6 21.8M(0) ·
    b7 48.9M(1) · b8 11.7M(0)

Across the three consecutive triple-zero runs G/joint is **21.8M → 48.9M → 11.7M — not monotone**, and
the v_D=1 and v_D=0 batches OVERLAP almost completely (v_D=0 spans 8.5M–48.7M, containing both the
worst and nearly the best). `vd_separates_gain()` → **False**. So the engine's own convergence census
is BLIND to its predictive performance: v_D=0 is compatible with the best batch on record and with one
of the worst. The gap the orbit proposal names is real and is now measured rather than asserted.

**FINDING 3 — A NEAR-RETURN ALREADY EXISTS, and the census misclassifies it.** The closest
non-adjacent pair under the repaired configuration projection is **b5 vs b7**: both 3/3 leading-class
hits, G/joint 48 658 932 vs 48 932 240 — a 0.6% difference, predictively indistinguishable — yet v_D
calls them DIFFERENT (0 vs 1). Minting a family and predicting well are ORTHOGONAL in the observed
data. That pair is the repaired instrument's first test case if it is ever built.

**NOT ADOPTED — and the precedent is why.** The arc already adopted an instrument mid-run before it
earned existence: the coupling/interface Γ table (URDRQPR1 §5), ADOPTED at run 2 and SUSPENDED at
checkpoint 3, starved of emergence events with its one directional call wrong. L58 (representation is
earned, not designed) and L3 (no promotion without independent preregistered recurrence) both bind
here, and this rung refuses to repeat the Γ mistake with a more elegant scalar. What is adopted today
is NOTHING; what is recorded is a disproof, a confirmed premise, and a frozen prospective test.

    FROZEN FALSIFIER for the REPAIRED orbit scalar (prospective — resolvable only by future batches,
    never by refitting these eight). Ω-repaired earns existence IFF, over the next SIX v_D=0 batches
    (n = 6 minimum, so no verdict can be bought with two noisy points): batches it classifies as
    NEAR-RETURN show G/joint at or below the median of batches it classifies as DISTANT, with the
    two groups NON-OVERLAPPING at their quartiles. If near-return and distant batches show
    indistinguishable predictive improvement, the scalar carries no information and is REMOVED — not
    retained as descriptive colour, which is how the Γ instrument survived three rungs past its
    usefulness. If fewer than six v_D=0 batches occur before the engine stops, the test reads STARVED
    (L61), never CONFIRMED.
    ALSO FROZEN, so the classifier cannot be tuned to the answer: "near-return" means the repaired
    configuration distance to some non-adjacent prior batch is ≤ the 25th percentile of all such
    distances computed over the batches available AT THAT TIME — a rolling, leak-free threshold, the
    same discipline checkpoint 9's null used.

### CHECKPOINT 10, HARD-GROUNDED — the two blockers turned into a theorem and a decided test

**BLOCKER 1 → W2, a negative THEOREM with a red-first plant (below, in THEOREM CANDIDATES).** The
degeneracy is not "Ω needs tuning"; it is an impossibility with a proof and a witness. The plant the
law required is built and BITES IN BOTH DIRECTIONS: two synthetic histories with IDENTICAL live
organizational configuration (same sole basis, same two minted families, same frozen predictor) and
ledger lengths 0 vs 30 archived resolutions —

    specified metric d(A,B) = 30   ← nonzero PURELY from archived rows; the states are operationally
                                     indistinguishable and the metric says otherwise
    repaired live metric  =  0   ← the correct answer

`append_only_plant_bites()` → True. A metric that reports distance 30 between two engines that
predict identically on everything is not measuring organizational state.

**THE ARCHITECTURAL CORRECTION, adopted as framing (not as an instrument): LINEAGE IS NOT STATE.**
Split what the proposal fused:

    S_live_t = (𝓑_t active bases, Π_t current frozen predictor, 𝓐_t active axes/families)
    L_t      = (𝓡_≤t resolved signature, 𝓜_≤t minted lineage)     ← immutable PATH LABEL, not a coordinate

The ledger is not discarded — it is demoted from state coordinate to path witness. Two live states may
be equal while carrying different histories (S_live_i = S_live_j, L_i ≠ L_j); in a historical system
that IS what recurrence means. This costs the ledger nothing it was using: no gate row, no claim, and
no resolution depends on 𝓡 being a coordinate of a distance.

**BLOCKER 2 → DECIDED, and it goes against the census.** Rather than eyeballing the b5/b7 pair, the
four preregistered models were fitted LEAVE-ONE-BATCH-OUT over the 7 batches with a known v_D and a
predecessor (exact rational least squares — no float enters the verdict). Mean absolute held-out error
on G/joint:

    null (mean)        17 854 727        ← the bar (L62: the null is seated from the start)
    census (v_D)       19 036 400        ← WORSE than the null
    history (G_{b−1})  17 498 120        ← best, and only ~2% better than the null
    combined           28 959 563        ← far worse; the overfitting signature at n = 7

`census_adds_predictive_information()` → **False.** Seating v_D makes held-out prediction of G WORSE
than predicting the mean. The grounded statement, in the exact strength the evidence supports:

    **CENSUS–PREDICTION NON-EQUIVALENCE.** New-family arrival (v_D) and gain over the null (G) measure
    different properties, and neither may be substituted for the other. Equal predictive performance
    coexists with different v_D (b5 vs b7: 3/3 leading hits each, G/joint within 0.6%, v_D 0 vs 1),
    and v_D carries NO out-of-sample information about G on this corpus.

**The four frozen relations, and their status now** — recorded so the claim cannot later be inflated:
  * **Positive coupling** (v_D↑ ⇒ G↑) — **REJECTED** on this corpus (census model loses to the null
    out-of-sample; the b5/b7 pair is a direct counterexample).
  * **Negative coupling** (v_D↑ ⇒ G↓) — not supported either; the census model is worse than the null
    in BOTH directions, which is what "no information" looks like.
  * **Threshold relation** (only emergence above some count moves G) — **UNTESTED.** No batch in the
    corpus has v_D ≥ 2, so the relation has never had an opportunity to show itself. STARVED (L61),
    not refuted.
  * **Operational orthogonality** (v_D adds nothing beyond batch identity and null structure) —
    **CONSISTENT WITH the evidence, NOT ESTABLISHED.** n = 7, retrospective. One pair and one small
    LOBO do not license an independence claim, and saying so would be the inflation L20 forbids.

**A finding that tempers the whole thing, stated because it cuts against the engine:** the
history-only model beats the null by roughly 2% — so G is very nearly UNPREDICTABLE at batch
granularity from either the census or its own past. Whatever structure the underconfidence result
(checkpoint 9) exposed lives at the JOINT level, not the batch level. Any future orbit instrument
that predicts batch-level G must beat 17 498 120, and nothing currently does.

**THE NEXT EXPERIMENT, frozen and NOT built: the live-state probe corpus.** The orbit question is
worth answering, and the repaired metric still cannot reach zero if the incumbent's credences drift
continuously. So the object to build is not another scalar over names but a BEHAVIOUR VECTOR over a
frozen probe set Q:

    Ψ_t = ( Π_t(q₁), …, Π_t(q_n) )   for a FROZEN set Q of probe joints,   Ω^Q_t = min_{j<t−ℓ} ‖Ψ_t − Ψ_j‖₁

Two engine states occupy the same orbit position when they PREDICT THE SAME on every frozen probe —
not when their accumulated records match. Because Ψ excludes append-only history it can actually
return, and because it uses full distributions it captures more than active basis names.
    FROZEN DECISIVE QUESTION (prospective; resolvable only by future batches, never by refitting
    these eight): do batches with LOW behavioural orbit distance produce less gain over the null than
    batches with HIGH behavioural orbit distance? Same evidentiary bar as the earlier freeze — ≥ 6
    future v_D=0 batches, a rolling leak-free near-return threshold, non-overlapping quartiles, and
    STARVED rather than CONFIRMED if under-supplied. If the two groups are indistinguishable, the
    orbit instrument carries no information and is REMOVED, not retained as descriptive colour —
    which is precisely how the Γ instrument survived three rungs past its usefulness.
    Q MUST BE FROZEN BEFORE Ψ IS EVER COMPUTED, or the probe set becomes tunable to the answer.

**What this changes about convergence: nothing yet, and that is the honest answer.** Checkpoint 9
established the predictive-adequacy leg (Δ_null > 0). Checkpoint 10 establishes that the STRUCTURAL
leg's own instrument (v_D) does not track predictive performance — so "three triple-zero runs" is
weaker evidence for convergence than it reads, because triple-zero says nothing about G. The
declaration still stands on checkpoint 9's measurement, not on the census. The distinction the orbit
proposal exists to draw remains OPEN and is now frozen as a decidable question rather than an
intuition.

## RUNG 2 — the ERROR SURFACE, resolved: the residual is a CONSTANT, not a SIGNAL

Built to the plan frozen at checkpoint 9, and it answers checkpoint 10's open question in the
direction that blocks the ambitious path. Witness: `prediction_residuals.py`, rerun byte-identical.

**The surface.** 22 joints, error types assigned by rule: **CLEAN 15, RANKING 7, SUPPORT 0,
PARTITION 0.** Every miss is a RANKING miss — the observed class was always named and always carried
real mass; the engine never missed by failing to consider a class, only by ordering it second. That
is a narrower failure mode than the partition was built to allow.

**THE GRANULARITY TEST — and reading (b) is REFUTED.** Checkpoint 10 left two readings of the
near-unpredictable batch-level G: (a) the errors are noise, or (b) aggregation destroyed a signal that
lives at the joint. Four preregistered covariates, leave-one-JOINT-out Brier on the miss event
(×10⁴, lower better):

    null (seated)  2380      ← the bar
    topmass        2560
    margin         2626
    nclass         2663

**No joint-level covariate beats the null.** `joint_level_beats_null()` → False. Worse for the
standing hypothesis: "low margin ⇒ higher miss probability" fails DIRECTIONALLY — mean margin is
**883 on hits and 928 on misses**, so misses ran slightly WIDER margins than hits. The hypothesis was
flagged at freeze as carrying genuine failure risk (P30 missed at a margin of 18), and it failed.
Reading (b) is not supported: the errors are unpredictable at BOTH granularities, and changing the
statistical unit does not recover signal.

**THE FROZEN RULE FIRES: Γ DOES NOT EARN EXISTENCE.** Checkpoint 9 froze it exactly: "only after that
table exists — and only if a frozen predictor of the engine's own misses beats a null — does a
synthesis operator earn existence (L58)." The table exists; no predictor beat the null. **So the
synthesis operator is refused, and with it the theory-algebra program that would have stood on it.**
This is the engine's own stopping rule working against the interesting answer, which is the only
evidence that it was ever a rule.

**THE PRECISE DISTINCTION, because two true findings look contradictory.** Checkpoint 9 measured a
real exploitable residual: the basis is systematically UNDERCONFIDENT (mean max probability 0.380 vs
0.68 leading-class accuracy). Rung 2 measures that nothing predicts WHICH joints miss. Both hold,
because they are different objects:

    the residual is a GLOBAL CALIBRATION OFFSET (a constant), not a CONDITIONAL SIGNAL (a function).

Sharpening every frozen vector by one fixed transform would improve the Brier; no available covariate
says where to spend the sharpening. **And a recalibration is a POST-PROCESSOR, not a rival basis** —
it changes confidence, never the ordering, so it cannot produce a discrimination, cannot lose a
tournament joint, and is not a challenger in L62's sense. The engine's one measured improvement path
is therefore explicitly NOT the one that would re-arm the tournament.

## THE ARCHITECTURAL REFRAME — Ψ as the OBSERVATIONAL QUOTIENT (corrected from a stronger claim)

**A correction recorded rather than silently applied.** This section first stated "Ψ as the canonical
state — Ψ IS the engine." That is too strong and is withdrawn. Ψ maps live organization to predictive
behaviour over a frozen probe corpus, so it is the **observable image** of the engine, not the engine:

    S₁ ∼ S₂  ⟺  Ψ(S₁) = Ψ(S₂)          canonical object: **S/∼**, the observational quotient

The distinction is load-bearing, not pedantic. "Ψ is the engine" asserts that two organizations with
identical probe behaviour ARE identical; "Ψ is the quotient" says only that they are
**experimentally indistinguishable over the current Q** — which leaves room for a larger Q to separate
them later, and makes the identifiability question below meaningful instead of vacuous. Adopting the
stronger form would have quietly converted a limit of the instrument into a claim about the world,
which is the exact move `integrity ≠ truth` exists to block. The over-claim survived roughly one
checkpoint; it is recorded because a correction that leaves no trace teaches nothing (L2).

A reviewer proposed elevating the predictive operator Ψ (the engine's distribution over a frozen probe
corpus Q) to the canonical engine state, with live organization EXPLAINING Ψ, history explaining how Ψ
came to be, and v_D / G / drift demoted to diagnostics OF those objects. **Accepted as framing**, on
exactly two grounds, both measured in this ledger:

  1. **W2** — history cannot serve as a state coordinate (append-only ⇒ any recurrence metric
     containing it is a clock). So state must be live or behavioural.
  2. **Census–prediction non-equivalence** — structural census does not predict predictive
     performance out-of-sample (v_D loses to the null under LOBO). So structure cannot stand proxy
     for behaviour, and the two need separate homes.

    QUOTIENT:   Ψ_t = ( Π_t(q₁), …, Π_t(q_n) ) over a FROZEN corpus Q — the engine's observable image.
    EXPLANANS:  S_live = (bases, predictor, active axes) explains Ψ; L = (𝓡, 𝓜) explains its history.
    DIAGNOSTICS: v_D, G, and any drift quantity Δ_Ψ(t,k) = d(Ψ_t, Ψ_{t−k}) — never the objects.

**THE THREE-CLASS PARTITION (RST's operational content).** Every variable in the engine belongs to
exactly one class, and the class fixes what it may be used for:

    class                evolution     admissible use
    ─────────────────    ──────────    ─────────────────────────────────────────
    live state           reversible    operational distance
    behavioural (Ψ)      observable    predictive equivalence / the quotient
    ledger (𝓡, 𝓜)       monotone      PROVENANCE ONLY — never operational geometry

Mixing classes inside one metric is the defect W2/RST proves fatal. This is a stronger and cleaner
constraint than "don't use append-only coordinates," because it says WHY and says what each coordinate
is FOR.

**DYNAMICS, replacing the scalar (frozen, unbuilt).** Recurrence is not scalar, so the checkpoint
sequence is treated as a path in operator space Ψ₀, Ψ₁, …, Ψ_t with local drift d(Ψ_t, Ψ_{t−1}),
cumulative drift d(Ψ_t, Ψ₀), velocity Ψ_t − Ψ_{t−1}, and acceleration (Ψ_t − Ψ_{t−1}) − (Ψ_{t−1} −
Ψ_{t−2}). **And the orbit intuition survives if what orbits is changed**: with several checkpoints
inducing near-identical Ψ, their centroid A = mean(Ψ_i) is an ATTRACTOR and r_t = d(Ψ_t, A) measures
repeated approach to the same PREDICTIVE REGIME. That metric lives entirely in behaviour space, so it
evades W2/RST by construction rather than by patching — which is the test of whether the reframe is
real: it makes the previously impossible measurement well-posed.

**A SCOPE LIMIT ON RUNG 2'S NEGATIVE, stated so the refutation cannot overreach.** Rung 2 refuted one
specific claim: that joint-level COVARIATES (margin, top-mass, class count) predict a miss. It CANNOT
address the repeated-measures questions — which joints are persistent bottlenecks, whether calibration
improves on hard joints while flat elsewhere, whether seam families affect the same regions — because
**the corpus has n = 1 per joint**: every joint is read exactly once and never re-measured. Those
questions require Ψ over a FIXED Q evaluated at multiple t, which is precisely what does not exist
yet. So "aggregation masks signal" is UNTESTED at the repeated-measures level, not refuted; only the
covariate reading is dead. That distinction is the whole reason Q is the next build.

**RESOLUTION EFFICIENCY — the replacement objective (frozen, denominator NOT yet fixed).** Replace
"did we mint a family?" with "how much predictive gain per unit structural change?": E = ΔG /
(ΔC + ΔR) for a preregistered structural-cost denominator. This evaluates whether structural changes
PAY RENT, and it is a more stable research quantity than novelty — which v_D's LOBO failure already
demonstrated. NOT computed here: the denominator must be frozen before E is ever evaluated, or the
cost basis becomes tunable to the answer, the same trap the null and the probe corpus each carry.

**NOT accepted on the reviewer's granularity argument**, and the difference matters: the case for Ψ
was partly that batch aggregation destroyed signal recoverable at the joint. Rung 2 just refuted that.
Ψ is adopted because the two blockers force a separation of concerns, NOT because a harvest is
waiting. Adopting it for the refuted reason would have been the inflation this ledger exists to catch.

**What is adopted today is still NOTHING executable.** Ψ requires Q, and Q must be FROZEN BEFORE Ψ is
ever computed or the probe set becomes tunable to the answer. The drift quantities replace the word
"orbit" (which carried geometric intuition that may not survive) with a measurable: evolution of the
predictive operator itself. All of it remains frozen-and-unbuilt, under the same prospective bar.

**W3 CANDIDATE — the FINITE PROBE IDENTIFIABILITY THEOREM.** The b5/b7 pair already hints at it, and
the quotient formulation above is what makes it a real question rather than a definition:

    STATEMENT: for any FINITE probe corpus Q there may exist distinct live organizations inducing
    identical predictive operators on Q — S_live₁ ≠ S_live₂ while Ψ_Q(S₁) = Ψ_Q(S₂).
    FALSIFIER: construct two live configurations that differ on at least one PREREGISTERED probe.
    READING BOTH WAYS: if such pairs are found, Q's resolving power is bounded and the honest response
    is to ENLARGE or REDESIGN Q — the theorem is then a stated LIMIT ON THE INSTRUMENT, not a defect
    in the engine. If repeated attempts find none, the live representation is REDUNDANT: it carries
    coordinates the behaviour does not have, which is W2/RST's lesson one level up (structure that no
    measurement can see is provenance, not state).
    This is why "Ψ IS the engine" had to be withdrawn: under that reading the theorem is vacuous —
    indistinguishable would MEAN identical, and the limit could never be stated, let alone tested.

## BATCH 9 FREEZE — the SELECTOR SUCCESSOR, and P33 + P34 + P35 (sealed before any READ)

**THE CENTRALITY SIGNAL IS EXHAUSTED, and the successor rule is frozen before the candidates were
ranked.** Recomputed fresh this rung (`lease` = 4 recalibrates the method against the P8 erratum):
all 32 remaining unbriefed modules have **in-degree 0**. The ordering that drove P1–P32 has no
remaining signal — a structural fact checkpoint 8 anticipated and deferred to here.

    FROZEN SUCCESSOR RULE: pure LEX order over read-eligible unbriefed modules.

**Why lex and not out-degree, stated because the alternative was tempting.** Out-degree (how many
certified laws a module composes) is also computable and would surface the composed capstones — which
is exactly the problem. Preferring it would smuggle in an untested claim ("composed modules are more
informative to read"), and under L63 an untested claim has NO STANDING. The selector's purpose was
never to be optimal; it was to REMOVE OPERATOR DISCRETION, and the P8 erratum exists because
discretion crept toward the instrument-convenient joint. Pure lex preserves that purpose exactly while
carrying zero theoretical content. It is arbitrary — and it is arbitrary in a way no argument of mine
can bend, which is the property that matters.

    READ-ELIGIBILITY, applied mechanically (checkpoint 8's rule): a module with NO gate method has no
    rows, and classification in this pass is from LIVE ROWS never prose (`claim ≠ code`), so it is
    unclassifiable and SKIPPED with the reason recorded. `bench` is lex-first and was confirmed
    ineligible by that test (no gate method — verified, not assumed). It is skipped, not passed over
    silently. All three joints below were confirmed to carry gate rows before selection closed.

**Batch rules**: order bombtest → buoyancy → cayley (pure lex, `bench` skipped). Sole basis B-M′; no
discrimination is possible, so scoring is on the v_D census and the meta only. Run-10 v_D fresh. L61
vacuity rule applied. Meta predicts ¬M-1 on all scoring joints (30 for 30).

### P33 — `bombtest` — **NON-SCORING, CONTAMINATION DECLARED.** Role: "Interaction-free tamper
    detection — certify an illegal step WITHOUT running it" (URDRBMB1). **The contamination is
    substantial and disclosed rather than absorbed**: `hainuwele/README.md`'s "Weak spots, named"
    section — read in full this session, before this freeze — states the module's central finding
    outright ("`bombtest`'s screen is evadable by anyone who reads it… an adversary who knows the
    invariants picks a kernel delta and is caught 0 of 70 times. It is a screen, never a verdict").
    A prediction authored after reading the resolution is not a prediction. Recorded NON-SCORING under
    the same rule that excluded P10 (`govern`) and P19 (`cpredict`); it is read and briefed, but it
    scores nothing and enters no census. The exposure is the immutable observation; the exclusion is
    the interpretation (L1/L2).

### P34 — `buoyancy` (SCORING) — role: "Exact integer flotation over the wave seam (T3.5)"
    (URDRBUOY1); ambient disclosed: the foundation wave family (`sea` field state, `wavefield` — P12,
    C-AB exact superposition, `crossing` wave-crossing timing); conformance lives under a different
    name (`conformance_buoy.txt`), a naming fact from the index, not a body fact. Body and history
    UNREAD.
    partition:        C-EQ (an exact flotation identity central — the wavefield exact-arithmetic
                      pattern) · C-INV (a displacement/conservation structural invariant central) ·
                      C-R (a typed admission of float state central — `buoyancy-refusal` exists) ·
                      C-AB · R-M · R-O.
    credences:        author (= B-M′): C-EQ 30 · C-INV 25 · C-R 25 · C-AB 8 · R-M 6 · R-O 6. Frozen
                      near-flat across the leading three: "exact integer flotation" names the
                      ARITHMETIC, not the law's semantics, and the foundation layer has produced all
                      three shapes. v_D=0 expected (the wave family is long established).

### P35 — `cayley` (SCORING) — role: "The Cayley-Menger determinant as a coordinate-free
    realizability law" (URDRCAY1); ambient: the exact-arithmetic substrate (`magicdiv` division by an
    invariant constant); a hygiene rung, not a chain member. Body and history UNREAD.
    partition:        C-INV (a coordinate-free structural invariant central — realizability
                      independent of embedding) · C-R (an admission predicate central — a distance
                      matrix is realizable or REFUSED) · C-EQ (a determinant identity central) ·
                      C-FLOOR · R-M · R-O.
    credences:        author (= B-M′): C-INV 35 · C-R 25 · C-EQ 22 · C-FLOOR 8 · R-M 5 · R-O 5.
                      "Coordinate-free realizability" reads as a structural invariant — B-M′'s
                      founding axis — but a determinant test that gates admission is equally the
                      police reading, and the arc has resolved that split both ways. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P33 — resolved (NON-SCORING, contamination declared): the one-sided screen, and a COST claim
    observed:         `bombtest-law` certifies that "interaction-free" means exactly one MEASURED
                      thing — **the audit path invokes the rule EXACTLY ZERO times, instrumented as a
                      call count** — a claim about ACCESS AND COST, not about physics. Re-execution is
                      the detonation: the Replay Court's bit-for-bit re-run is unpayable for embargoed
                      data, a licensed model, or a week of cluster time. Soundness is a NEVER-CLAIM
                      (Holzmann's SPIN shape: a detector wired so the honest case cannot fire, an
                      accepting run IS the counterexample) discharged EXHAUSTIVELY — 4096 states,
                      13824 legal transitions, 0 acceptances. One-sided: firing certifies, SILENCE IS
                      INCONCLUSIVE. `bombtest-selftest`: a planted non-conserved arm accepts 4608
                      times against 0 honest.
    scoring:          NONE. The freeze declared this joint non-scoring because the README's
                      weak-spots section (read before the freeze) states the finding outright. No
                      census entry, no meta entry, no weight movement — recorded so the exclusion is
                      auditable rather than invisible.
    noted:            the module corrects its own arithmetic in place (a first draft said 24576 =
                      4096 × 6, every state times every rule, counting boundary-blocked moves that
                      never fire) on the stated grounds that writing a product instead of reading the
                      counter is the same class of error as reporting a sample as a universal.

### P34 — resolved: **C-INV** — the Archimedes bracket; the question/answer split's THIRD carrier
    read:             2026-08-05, the blind READ (run 10). Classified from the LIVE `buoyancy*` rows.
    observed:         `buoyancy-properties` certifies the **exact Archimedes bracket**
                      Δ(z*) ≥ W > Δ(z*+1) — the characterizing property of the integer waterline —
                      together with Δ's monotonicity (which is what licenses the bisection) and the
                      behavioural pair that keeps it non-vacuous (the raft HEAVES on swell, RESTS on
                      still). z* is found by division-free integer bisection, so the result is EXACT.
                      `buoyancy-selftest` makes the clamp load-bearing (an unclamped-displacement
                      defect diverges from the heave); `buoyancy-refusal` is total and typed (6/6
                      BUOY-REFUSE: empty · out-of-grid · duplicate · weight ≤ 0 · bool · non-int).
    class:            C-INV. The author priced C-EQ 30 · C-INV 25 · C-R 25 and **the leading call
                      missed**: "exact integer flotation" names the ARITHMETIC, not the semantics, and
                      the freeze mistook one for the other. What is certified is a BRACKET
                      characterizing a measured answer, not an equality between two computations.
                      v_D = 0.
    unnamed (M-0):    THE QUESTION/ANSWER SPLIT, third carrier. Blocking is not refused — z* is a
                      MEASURED EVENT and the typed refusals guard only the DOMAIN boundary. That is
                      P3's `stance` residual recurring (`stance` measures where terrain blocks, `traj`
                      measures innovation, `buoyancy` measures where water holds). Also: the LAW is a
                      DECLARED model (a discrete Archimedes) walled off from the D5 ledger while the
                      COMPUTATION is measured — the grading split stated inside the module.

### P35 — resolved: **C-EQ** — identities verified, not quoted · RUN 10 CLOSES
    read:             2026-08-05, the blind READ (run 10). Classified from the LIVE `cayley*` rows.
    observed:         `cayley-law` certifies EQUALITIES against INDEPENDENTLY computed quantities:
                      Heron in determinant form reproduces a separately computed area (−det = 16·area²,
                      3-4-5 → 576), the simplex volume reproduces a separately computed volume
                      (det = 288·vol² → 373248), and the operative identity — any 5 points in 3-space
                      span at most a degenerate 4-simplex, so their 6×6 determinant VANISHES
                      IDENTICALLY, a tautology holding without exception and without reference to any
                      coordinate frame. `cayley-property` holds it exactly across the whole sweep (one
                      non-zero residue would falsify the implementation) with a forged distance
                      breaking it every time; `cayley-selftest` shows a credulous verifier admitting
                      what the determinant refuses, so the law is a live falsifier.
    class:            C-EQ. The author priced C-INV 35 · C-R 25 · C-EQ 22 — **the leading call missed
                      and the winner was priced THIRD**, the batch's second miss. "Coordinate-free
                      realizability" read as a structural invariant; the row certifies identities,
                      which is the arc's C-EQ signature (wardhom's three languages, mesh == monolith).
                      An identity that happens to police, not a police predicate built on an identity.
                      v_D = 0.
    unnamed (M-0):    two independent algorithms as ORACLES FOR EACH OTHER (`bareiss`, fraction-free
                      but dividing, vs `leibniz_det`, division-free) required to agree on every
                      configuration with neither reading the other's intermediate state — the
                      neutral-ruler pattern a FIFTH time; the Leibniz form is "the one that travels"
                      because integer division semantics differ between languages for negative
                      operands, so division-freeness is a CROSS-PLACEMENT property not an aesthetic
                      one; and the check asks a strictly WEAKER question than every other admission in
                      the arc — not "is your claimed POSITION lawful?" but "is your claimed set of
                      RELATIONSHIPS even possible?", needing no coordinates, frame, or trusted origin.
    census:           run-10 v_D = 0, 0 (two scoring joints; P33 non-scoring) — RUN 10 CLOSES with no
                      new family. Meta ¬M-1: 32 for 32.
    BATCH SIGNATURE, recorded because it repeats batch 8's: **BOTH scoring leading calls MISSED**
                      (P34 C-EQ→C-INV, P35 C-INV→C-EQ — and note they missed in OPPOSITE directions,
                      which is not a consistent bias that could be corrected by a fixed transform).
                      Batches 8 and 9 have now produced four leading-class misses in six scoring
                      joints. An obvious story is available — the successor selector moved the
                      frontier from central chain modules to foundation/hygiene rungs, and the basis
                      was formed on the former — but that story is POST HOC and unfrozen, and under
                      L63 it has no standing. It is recorded as an observation with a decidable
                      forward test (do misses stay elevated on lex-selected joints?) and nothing is
                      concluded from it here.

## RUNG 3 — Q FROZEN, Ψ₀ EMITTED: the repeated-measures instrument now exists

Witness: `probes.py`. Two commits, in the order the discipline requires — Q sealed with `PSI` empty,
then Ψ₀ emitted against the sealed corpus. The same spec-then-run split checkpoint 9 used, for the
same reason: a probe set chosen after seeing an operator is tunable to the answer.

**Q — ten SYNTHETIC probes, one fixed class space.** Every probe is a fabricated module (QP prefix)
that does not exist and will never be built, so no answer exists and none can leak. A probe drawn
from a READ module would measure recall, not disposition; a probe drawn from a module about to be
read would contaminate the READ pass itself (L59). Each is written to sit on a seam the engine has
historically SPLIT on — price/admission, equivalence/police, invariant/admission, order/price,
representation/police, floor/equivalence — because L61 turned on the corpus says **a probe every
operator answers identically cannot detect drift**. One fixed class vocabulary across all ten (unlike
the per-joint partitions of the READ freezes), so Ψ_t is a point in a common simplex and L1 distance
between operators is well defined.

**Ψ₀ — the seated basis, on the record.** All ten vectors valid (cover the class space, sum to 10⁴).
Leading classes: QP01 C-PRICE, QP02 C-EQ, QP03 C-INV, QP04 C-EQ, QP05 C-ORD, QP06 C-REP, QP07
C-FLOOR, QP08 C-EQ, QP09 C-PRICE, QP10 C-R. The corpus discriminates as designed — six distinct
leading classes, and margins spanning 200 (QP06, representation vs police, near-tied) to 2000 (QP05,
the scheduling axis, where the engine is most committed). A corpus that produced one leading class
everywhere would have been the vacuous instrument L61 warns of.

**What is now possible that was not.** Drift Δ_Ψ(t,k), the attractor radius r_t = d(Ψ_t, A), and W3's
identifiability test all have a domain. Critically, r_t lives ENTIRELY IN BEHAVIOUR SPACE, so it
evades W2/RST by construction rather than by patching — which is the test of whether the reframe was
real, and it passes: the measurement RST proved impossible in checkpoint space is well-posed here.

**The honest boundary, recorded before any drift number exists.** Ψ is AUTHOR-EMITTED — B-M′ is a
reading heuristic, not executable code — so every emitted credence is **DECLARED, not MEASURED**. The
arithmetic over recorded vectors is what `probes.py` measures. A re-emitted Ψ can therefore drift for
reasons that have nothing to do with the engine (memory, phrasing, the day), and that noise floor is
NOT estimable from a single emission. The mitigation is structural rather than hopeful: fixed public
probes, a fixed class space, and each emission committed before the next is computed, so any drift
claim is auditable against the record that produced it. A future emission that moves less than this
unmeasured floor means nothing, and a first drift reading will not distinguish the two.

**Status: EXPERIMENTAL under L63.** Ψ and every quantity derived from it may be computed and reported
but MAY NOT be reasoned from until one of them beats a seated incumbent on a declared objective. The
registry below records it as such. Nothing about convergence changes on this rung.

## BATCH 10 FREEZE — P36 + P37 + P38 (sealed before any READ)

**Selector**: the frozen successor rule (pure LEX over read-eligible unbriefed modules) reapplied
without amendment → `clslo` → `commuteprop` → `crossing`. `bench` remains lex-first and remains
SKIPPED by the same mechanical test that disqualified it at batch 9 (no gate method ⇒ no rows ⇒
unclassifiable), re-verified this rung rather than carried forward on memory.

**Ψ₁ IS PLANNED NOW, not after seeing the results.** On this batch's completion Ψ₁ will be emitted
against the sealed corpus Q, giving the drift series its first post-work reading. Rung 4 measured the
floor at ε_author = 2800, so the reading is already decidable: **‖Ψ₁ − Ψ₀‖₁ ≤ 2800 is uninterpretable
and may not be reasoned from; only a drift exceeding it is a candidate signal.** Declaring this before
the batch closes prevents the floor from being reinterpreted once a number exists.

**Batch rules**: sole basis B-M′; no discrimination possible, so scoring is the v_D census and the
meta only. Run-11 v_D fresh. L61 vacuity rule applied. Meta predicts ¬M-1 on all three (32 for 32).

### P36 — `clslo` (SCORING) — role: "Per-CLASS worst-case latency SLO (T3.34)" (URDRLAT3); ambient
    disclosed: `slo` (P29, C-PRICE, the composite worst-case) whose own `does_not_show` NAMED this as
    the follow-on ("priority-class latency — uses the FIFO governor's uniform bound, not `priogov`'s
    per-class one"); the LAT family (`horizon` LAT1, `slo` LAT2). Row NAMES seen during eligibility
    checking (`clslo-refinement`, `clslo-soundness`, `clslo-refuse`) — disclosed as exposure, though
    no row CONTENT was read. Body and history UNREAD.
    partition:        C-PRICE (a per-class worst-case BOUND central — the cost/latency family's fifth
                      preregistered instance) · C-EQ (a refinement IDENTITY central — per-class bounds
                      composing to the uniform one) · C-ORD (a certified per-class ORDER central — the
                      scheduling axis's third carrier, which would be a mint) · C-R · R-M · R-O.
    credences:        author (= B-M′): C-PRICE 38 · C-EQ 24 · C-ORD 14 · C-R 14 · R-M 5 · R-O 5.
                      v_D=0 expected; but C-ORD is the live mint risk — if clslo certifies a per-class
                      ORDER rather than a per-class BOUND, the scheduling axis gains a third carrier.

### P37 — `commuteprop` (SCORING) — role: "Property-based falsifier for the commute diamond (Tier-2)"
    (URDRCPS1); ambient: `commute` (T3.41, the commutation certificate, "the proof-object turn",
    itself unbriefed). A module whose PURPOSE is to falsify another module's law. Body and history
    UNREAD.
    partition:        C-EQ (the diamond itself central — both orders agree, an equivalence) · C-FLOOR
                      (a non-vacuity/coverage result central — a property-based falsifier that never
                      generates a biting case proves nothing, the L61 shape) · C-INV (a structural
                      invariant central) · C-R · R-M · R-O.
    credences:        author (= B-M′): C-EQ 40 · C-FLOOR 20 · C-INV 20 · C-R 10 · R-M 5 · R-O 5.
                      The genuinely interesting one: a falsifier module's central law could equally be
                      the property it checks (C-EQ) or the demonstration that its generator BITES
                      (C-FLOOR). v_D=0 expected.

### P38 — `crossing` (SCORING) — role: "Wave-crossing timing (T3.7)" (URDRCROSS1); ambient: the
    foundation wave family (`sea`, `wavefield` — P12 C-AB, `buoyancy` — P34 C-INV); conformance under
    a different name (`conformance_cross.txt`). Body and history UNREAD.
    partition:        C-INV (a characterizing bracket/invariant central — the `buoyancy` shape one
                      layer over) · C-EQ (an exact timing identity central) · C-R (a typed admission
                      central) · C-PRICE · R-M · R-O.
    credences:        author (= B-M′): C-INV 32 · C-EQ 30 · C-R 22 · C-PRICE 6 · R-M 5 · R-O 5.
                      **Prior updated from a RESOLVED joint, disclosed as such**: P34 (`buoyancy`)
                      taught that this layer certifies BRACKETS characterizing measured answers rather
                      than identities, and that "exact" names the arithmetic not the semantics. Using
                      a resolved outcome to price a later freeze is legitimate learning, not
                      contamination — the two modules are independent and P34 is closed. v_D=0.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P36 — resolved: **C-PRICE** — a price refined by class; the mint risk did NOT fire
    read:             2026-08-05, the blind READ (run 11). Classified from the LIVE `clslo*` rows.
    observed:         `clslo-refinement` certifies that a higher-priority class carries a
                      TIGHTER-OR-EQUAL bound (premium beats free) and that the ONE-CLASS CASE REDUCES
                      EXACTLY to the composite `slo`'s uniform number — a strict generalization, not a
                      replacement. `clslo-soundness` makes the bound real rather than optimistic: the
                      per-class bound EQUALS `priogov`'s actual per-class drain over the config corpus
                      (exact for equal-cost), so the promise is derived from the scheduler that keeps
                      it. `clslo-refuse`: a tier exceeding ITS OWN target is CLSLO-REFUSE, named — a
                      config cannot meet the aggregate while failing a class.
    class:            C-PRICE; the author's leading credence (38) CORRECT. The cost/latency family's
                      FIFTH preregistered instance (opcost, horizon, govern, slo, clslo). v_D = 0.
    THE MINT RISK, resolved NEGATIVE: the freeze named C-ORD as the outcome that would give the
                      scheduling axis a third carrier. It did not fire, for a structural reason worth
                      recording: `priogov` certifies the ORDER work is admitted in; `clslo` certifies
                      that the resulting BOUNDS respect the class ordering. Monotonicity of prices
                      across classes is NOT a certified order. **The scheduling axis stays at two
                      carriers.**
    unnamed (M-0):    the reduction-to-`slo` clause — a refinement that does not reproduce its
                      predecessor at the degenerate case is a different guarantee wearing the same
                      name, and this one is CHECKED rather than claimed.

### P37 — resolved: **C-EQ** — the diamond against a brute-permutation oracle
    read:             2026-08-05, the blind READ (run 11). Classified from the LIVE `commute-property*`
                      rows (note the row names are `commute-property*`, not `commuteprop-*`).
    observed:         `commute-property`: across the seeded adversarial sweep EVERY ORDER LANDS ONE
                      HEAD + FIELD, verified against a BRUTE-PERMUTATION ORACLE that enumerates the
                      orders independently; closure agrees; `predict` matches independent chunk
                      geometry; every same-cell pair is checked. `commute-property-selftest`: a
                      mutated `commute.predict` (always rank 0) makes the sweep raise
                      COMMUTEPROP-FALSIFIED, and the module reads clean after the revert — the
                      generator provably bites, on a real mutation of the module it guards.
    class:            C-EQ; the author's leading credence (40) CORRECT. v_D = 0.
    the C-FLOOR alternative, resolved: the freeze priced C-FLOOR at 20 on the reasoning that a
                      property falsifier which never generates a biting case proves nothing (L61's
                      shape). The module answers that directly with the mutation test, so its
                      non-vacuity is ESTABLISHED rather than CENTRAL, and the equivalence keeps the
                      joint.
    unnamed (M-0):    the brute-permutation oracle — the NEUTRAL-RULER pattern's SIXTH instance (mesh's
                      monolith, wardhom's three languages, traj's locally-derived truth, cayley's two
                      algorithms, terraform-as-oracle, this) — the checker structurally denied the
                      option of trusting what it checks.

### P38 — resolved: **C-EQ** — the moving-sample identity · RUN 11 CLOSES
    read:             2026-08-05, the blind READ (run 11). Classified from the LIVE `crossing*` rows.
    observed:         `crossing-properties`: **the trace IS `wavefield.height` at the MOVING cell and
                      tick** — the agent samples the field along its trajectory at the tick it is
                      actually there, not a snapshot and not the start cell — with the result being
                      the FIRST overtop and CLEARANCE LOAD-BEARING (one path clears high and swamps
                      low, so the predicate distinguishes something). `crossing-selftest` pins the
                      identity: FREEZING THE WAVE (every tick at t=0) changes when the agent is
                      overtopped, so travel is load-bearing and a static-field implementation is a
                      detectably different module. `crossing-refusal`: 6/6 CROSS-REFUSE, typed, total.
    class:            C-EQ. The author priced C-INV 32 · C-EQ 30 — **a two-point miss**. v_D = 0.
    AN HONEST NEGATIVE ABOUT CROSS-JOINT LEARNING, recorded because it cuts against the practice:
                      the freeze DISCLOSED that it moved weight toward C-INV on the strength of P34
                      (`buoyancy` had just taught that this layer certifies BRACKETS characterizing
                      measured answers, and that "exact" names the arithmetic not the semantics). The
                      lesson was real and it TRANSFERRED BADLY — buoyancy's central row is a two-sided
                      INEQUALITY, crossing's is an EQUALITY; same layer, same vocabulary, different
                      shape. The disclosure stands (using a CLOSED joint to price a later freeze is
                      legitimate learning, not contamination) but the update moved the credence the
                      wrong way. That is a datapoint about the VALUE of cross-joint learning, not its
                      propriety, and it is the first time this ledger has measured one.
    what DID transfer: the question/answer split — the answer (a tick, a waterline) is MEASURED and
                      never refused; typed refusals guard only the domain. Fourth carrier (stance,
                      traj, buoyancy, crossing).
    census:           run-11 v_D = 0, 0, 0 — RUN 11 CLOSES on a triple zero. Meta ¬M-1: 35 for 35.
                      Leading calls 2/3 correct (P36, P37 landed; P38 missed by two points) — an
                      improvement on batch 9's 0/2, and NOT read as a trend: two batches under the lex
                      selector is not a series, and under L63 the elevated-miss story from batch 9
                      still has no standing either way.

## RUNG 8 — the post-pass instruments: one term CLOSED, one corpus SEALED, one measurement REFUSED

Three items were directed after the READ pass closed. Two were executed; **one was refused, and the
refusal is the substantive result.**

### REFUSED — the unanchored Ψ floor cannot be produced by this session

The instruction was to execute a fresh-session evaluation establishing an unbiased Ψ baseline.
**This session authored Ψ₀.** Any emission it produces against Q is anchored by construction — the
original vectors are in its context — which is precisely the contamination that made ε_author = 2800 a
LOWER BOUND rather than a floor. Running it here would produce a number that LOOKS like an unanchored
baseline and is in fact a second anchored control, and recording it as the former would be the exact
inflation this ledger exists to refuse. **No number is produced.**

What is produced instead is the protocol: `UNANCHORED_FLOOR_PROTOCOL.md`, written to be executed by a
session that has NOT seen Ψ₀ and structured so that following it does not contaminate it — step 1 is
an explicit instruction not to read the recorded vectors or the Rung 3/4/5 sections. Its reading rule
is frozen in both directions, including the surprising one (ε_unanchored ≤ ε_author would REFUTE the
reasoning that made the anchored figure a lower bound, and must be recorded as such rather than
explained away). It also names the stronger variant it is not: **emission by a DIFFERENT AGENT**, which
measures operator variance rather than session variance and is the only form that would let Ψ be called
an instrument rather than one author's habit.

### CLOSED — ΔL_model, E's last open term (`mdl.py`)

Rung 4 left E as `ΔL_data − λ·ΔL_model` with λ = 1 and one constraint on the open term: it must be a
REAL CODE LENGTH, never an edit count wearing a bit's clothing. Closed by the standard two-part code —
the engine's model is a categorical predictor, minting a family ENLARGES its class vocabulary, and the
parametric complexity of a multinomial over K classes fitted on n observations is Rissanen's

    L_model(K, n) = ((K−1)/2)·log2(n) bits    ⇒    ΔL_model = ((K′−K)/2)·log2(n)

Measured for the arc's two mints: **approximation axis 2043 mb** (K 7→8, n 17), **scheduling axis
2378 mb** (K 8→9, n 27). The property that matters is decided rather than asserted: **a family
explaining NOTHING still costs, so E goes NEGATIVE for a mint that buys no predictive improvement** —
behaviour the refuted ratio form could not express at all.

**ΔL_data is NOT computed, and that is a discipline point.** Measuring it for a past mint requires a
COUNTERFACTUAL pre-mint model, and how that counterfactual redistributes the minted class's mass is a
modelling choice that would decide the answer. The protocol is frozen — proportional (max-entropy)
redistribution, scope restricted to joints scored strictly AFTER the mint (including earlier ones would
credit a family for the outcomes it was minted FROM, the retrofit trap L58 names), log loss in
millibits — and left unrun. **E remains uncomputed and EXPERIMENTAL.**

### SEALED — Q′, the successor corpus with per-axis redundancy (`probes2.py`)

Rung 5 found Q ONE-PROBE FRAGILE: QP05 alone carried 73% of the W3 ablation difference, and removing it
flips the verdict. Q′ carries **16 probes, two per named axis**, and the pairs are deliberately **not
paraphrases** — each pair places its axis in two structurally different settings (authority vs
measurement, concurrency vs serialization, resource vs latency), because two probes differing only in
wording give redundancy of form without redundancy of evidence and would fail together. `corpus_is_sealed()`
enforces both conditions mechanically, including the no-paraphrase check. **Q is NOT edited** — a corpus
revised in response to a verdict it produced is tunable to the answer — and both are retained so they
can be compared rather than one quietly replacing the other. `PSI2` is empty, as Q's was at sealing.

**THE L63 TENSION IS RECORDED, NOT STEPPED AROUND.** Batch 11 explicitly REFUSED to build Q′ on the
grounds that it is more Ψ apparatus while Ψ holds no standing. **That objection is not answered here.**
What changed is narrower and is all that is claimed: the READ pass is complete, so the competing use of
effort the refusal partly rested on no longer exists. Q′ is EXPERIMENTAL, may be computed and reported,
and may NOT be reasoned from. A successor that quietly outgrew a refusal would be worse than the
refusal.

## BATCH 18 FREEZE — P60–P63, THE FINAL BATCH; and the closing ruling on `bench`

**A DECLARED DEVIATION: this batch is FOUR joints, not three.** Every prior batch was three by
convention. Four eligible modules remain, and splitting them 3+1 would leave a final rung whose single
joint carries no batch-level census. The deviation is stated here, before any read, rather than
discovered in the closing prose — it changes nothing about how each joint is frozen or scored.

**THE CLOSING RULING ON `bench`, and why the pass ends with a module unbriefed.** `bench` is the fifth
remaining module and it will NOT be briefed. The ruling was first frozen at checkpoint 8 and is now
MEASURED rather than assumed: **no gate stage imports `bench`**, so it records no rows, so there is
nothing to classify from — and classification in this pass is from LIVE ROWS, never prose
(`claim ≠ code`). That is not a gap in the pass; it is the pass respecting its own rule. `bench`
measures WALL-CLOCK, which is MEASURED-on-named-host and may never enter a byte-identical gate, so its
ungatedness is a deliberate design property. **The arc ends at 1 of 103 unbriefed, and that 1 is a
decision, not a debt.**

**Selector**: lex over read-eligible unbriefed → `terrain_view` → `tierview` → `tilecert` →
`wireattest`. Ladder v3 applied mechanically; central rows **`terrain-view:bind`**, **`tierview-law`**
(step 1), **`tilecert-taxonomy`**, **`wireattest:laws`** (step 2). Row names are structural exposure;
contents UNREAD.

**Batch rules**: sole basis B-M′; scoring is the v_D census and the meta. FP-ROW stays retired. Run-19
v_D fresh. L61 applied. Meta predicts ¬M-1 on all four (54 for 54).

### P60 — `terrain_view` (SCORING) — role: "The D15 view-export FIREWALL (T3.0)" (URDRTVW1); ambient
    DISCLOSED and substantial: `view_witness` (P32, C-R) is this rung's DUAL and its brief states the
    pairing outright — D15 proves the view cannot CONTAMINATE the authority, `view_witness` that it
    cannot MISQUOTE it. That is exposure to this module's ROLE in a pair, not to its central row's
    content; the joint stays SCORING under P41's ruling. Central row: `terrain-view:bind`. Body UNREAD.
    partition:        C-INV (a one-way firewall structural invariant central — nothing flows inward) ·
                      C-R (an export admission predicate central) · C-EQ (a bind identity: the exported
                      view ≡ the authority it cites) · C-REP · R-M · R-O.
    credences:        C-INV 34 · C-R 28 · C-EQ 24 · C-REP 8 · R-M 3 · R-O 3. v_D=0 expected.

### P61 — `tierview` (SCORING) — role: "Visual asymmetry ZERO BY CONSTRUCTION (S6) — the predicate
    cannot take a tier" (URDRTIR1); ambient: the city arc. The role states the mechanism outright —
    zero BY CONSTRUCTION, because the predicate cannot receive a tier. Central row: `tierview-law`
    (ladder step 1). Body UNREAD.
    partition:        C-FLOOR (a soundness-of-absence result central — the asymmetry is zero and the
                      zero is STRUCTURAL, the `splitview`/`ashdepth` shape) · C-INV (a structural
                      invariant central) · C-EQ (an equality across tiers) · C-R · R-M · R-O.
    credences:        C-FLOOR 32 · C-INV 30 · C-EQ 26 · C-R 6 · R-M 3 · R-O 3. Frozen near-flat across
                      the leading three: "zero by construction" is genuinely between a measured absence
                      (C-FLOOR), a structural invariant (C-INV), and an equality across tiers (C-EQ),
                      and the arc has resolved all three. v_D=0 expected.

### P62 — `tilecert` (SCORING) — role: "The tile certificate and what it actually proves — attribution,
    not verification" (URDRTIL1); ambient DISCLOSED: the README states this module's finding ("the
    estimator that looked correlated was an artifact of the fixture and is refuted twice"), which is
    the P33/P49 situation → **NON-SCORING**. Read and briefed; enters no census, no meta.
    reading (unscored): C-FLOOR — an inherited claim (that a certificate verifies) refuted, leaving
                      attribution as what survives.

### P63 — `wireattest` (SCORING) — role: "THE REALITY ATTESTATION (T3.51, W5) — real sockets"
    (URDRWAT1); ambient: `meshattest` (P47, C-EQ) is its Phase-M sibling and resolved on exactly the
    attestation question — real transport shown to satisfy the unmodified law. Central row:
    `wireattest:laws` (ladder step 2). Body UNREAD. **PRIOR TRANSFERRED from resolved P47 and
    DISCLOSED**; transfer stands at 1 hurt / 2 helped, so it is priced ahead but not confidently.
    partition:        C-EQ (a real-transport run ≡ the in-process law — the `meshattest` shape) · C-R
                      (an attestation as admission) · C-AB · C-INV · R-M · R-O.
    credences:        C-EQ 42 · C-R 28 · C-AB 16 · C-INV 8 · R-M 3 · R-O 3. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the four is read.

### P60 — resolved: **C-EQ** — carrying verbatim is an identity; the D15 pair closes
    observed:         `terrain-view:bind`: **the view carries the recorded witness VERBATIM — bound,
                      and subordinate** — the authority's own bytes carried through unchanged, so the
                      view is structurally a READER rather than a second source.
                      `terrain-view-observational` states the firewall as a measurement: **6/6 declared
                      knobs move the view digest, NONE moves the witness, knob order inert.** Both
                      halves load-bearing — that the knobs move the VIEW digest is the non-vacuity
                      witness, that none moves the WITNESS is the firewall. The selftest bites (the
                      fold-into-witness defect diverges); 4/4 typed VIEW-REFUSE.
    class:            C-EQ. Author priced C-INV 34 · C-R 28 · C-EQ **third at 24** — leading call
                      missed. The invariant is real but lives in the observational row; `:bind`
                      asserts an equality. v_D = 0.
    THE D15 PAIR CLOSES: with `view_witness` at P32, **one rung proves the view cannot CONTAMINATE the
                      authority, the other that it cannot MISQUOTE it.** An honest one-way membrane
                      still permits a lie about the far side; an honest citation still permits
                      contamination. The arc needed both and built them separately.

### P61 — resolved: **C-FLOOR** — zero by construction, and the zero is EARNED
    observed:         `tierview-law`: **the authoritative visibility predicate takes NO TIER ARGUMENT,
                      so asymmetry between quality tiers is ZERO BY CONSTRUCTION rather than bounded by
                      a budget** — decided over every observer on both pinned walls and every ordered
                      tier pair — and **the decoupling is STRUCTURAL rather than disciplinary**: the
                      predicate cannot read a tier because it cannot receive one.
    class:            C-FLOOR; leading credence (32) CORRECT, narrowly, over a partition frozen flat
                      across C-FLOOR/C-INV/C-EQ. v_D = 0.
    THE ZERO IS EARNED: `tierview-selftest` shows **a tier-reading authority path costs 1152 CELLS of
                      asymmetry across the very census the law scores zero on** — so the zero is a
                      result, not an artifact of a census too weak to show anything — and that path is
                      **REFUSED rather than warned about**, on the stated ground that a tier pair
                      resolving different cells is AN UNEQUAL GAME, not a cosmetic difference. The
                      handed-down luminance measure is refuted in the same row. The gap between 1152
                      and 0 is the content; neither number means anything alone.
    unnamed (M-0):    STRUCTURAL beats DISCIPLINARY — a bounded asymmetry needs enforcement, an
                      auditor, and a story about exceeding the bound; a predicate that cannot take a
                      tier needs none, and the policy question DISAPPEARS rather than being answered.
                      The same move as `autoroute`'s capability projection and `provbind`'s serve-time
                      recomputation: **deny the input rather than police the use.**

### P62 — resolved (NON-SCORING, contamination declared): a signed claim is not a proof
    observed:         `tilecert-taxonomy`: **Necula's proof-carrying code has one defining property —
                      the consumer CHECKS the proof against the artifact and trusts the producer for
                      nothing — and a certificate asserting a property of data the verifier DOES NOT
                      HAVE is not a proof but a SIGNED CLAIM**, where a signature establishes who said
                      it. `tilecert-attribution`: what the certificate buys is **ATTRIBUTION** — a
                      bound, signed certificate whose recomputable field later disagrees with the
                      lattice is **NON-REPUDIABLE EVIDENCE of server misbehaviour, reproducible by any
                      third party** — real value, arriving after the fact and evidentiary rather than
                      preventive.
    scoring:          NONE — declared at the freeze under the P33/P49 rule.
    unnamed:          **THE ESTIMATOR IS REFUTED TWICE** — it saves no work (reading every occupied
                      cell's prefix depth IS the same single pass `charge_for` already makes, measured
                      at equal visits, saving **0**, so "refuse before processing" processes), and it
                      predicts nothing about the charged defect. Two independent refutations of one
                      appealing mechanism, kept rather than deleted. The self-directed extreme of the
                      ashdepth/recirc/divergence/horn shape — and the arc's clearest refusal of a
                      BORROWED WORD, since "proof" would have imported guarantees the mechanism lacks.

### P63 — resolved: **C-EQ** — reality replays lawful · **RUN 19 CLOSES · THE READ PASS ENDS**
    observed:         `wireattest:laws`: the **synthetic gale** (chaos + malice, zero stalls), the
                      **tempest** (real loss with a verified repair fetch), and the **stalled
                      no-repair variant** each **replay LAWFUL under the UNMODIFIED wire law**,
                      deterministically — **the checker accepts exactly what the law admits.** Not a
                      relaxed law for real conditions, and not a checker tuned until reality passes.
                      `wireattest:forges` — reality may not overrule the law on any axis — refuses a
                      forged admission, a drifted witness, a double admission, an untyped outcome, a
                      corrupt delivery claiming admission, **a stalled client claiming the authority's
                      witness**, and a consistent wrong-address fetch, each typed.
    class:            C-EQ; leading credence (42) CORRECT. v_D = 0.
    TRANSFER PAID A THIRD TIME: the prior from P47 (`meshattest`) was disclosed and priced ahead
                      without confidence, and it held. **An attestation in this arc is an EQUIVALENCE,
                      not a certificate** — both carriers phrase it identically (real transport,
                      UNMODIFIED law, replay lawful, re-derived evidence matching the record) with the
                      refusal battery as guard rather than law. **Cross-joint transfer closes the pass
                      at 1 hurt / 3 helped** — small enough to state honestly, not large enough to
                      license the practice.
    census:           run-19 v_D = 0, 0, 0 (three scoring; P62 non-scoring) — **RUN 19 CLOSES with no
                      new family, the eleventh consecutive run.** Meta ¬M-1: **57 for 57.** Leading
                      calls 2/3.

## THE READ PASS IS COMPLETE — 63 preregistered joints, 19 runs

**Final state.** 102 of 103 terrain modules carry a design brief whose falsifier the gate ENFORCES.
The one remaining, `bench`, is **not a debt**: no gate stage imports it, so it records no rows, so
there is nothing to classify from — and it measures WALL-CLOCK, which is MEASURED-on-named-host and
may never enter a byte-identical gate. Its ungatedness is a design property and its unbriefedness
follows from the pass's own rule.

**What the pass produced, stated at the strength the evidence licenses.** Two minted seam families
(approximation, scheduling), both earned by independent preregistered recurrence and neither by fiat.
A convergence DECLARED at checkpoint 7 and evidenced at checkpoint 9 — Δ_null > 0 under both Brier and
log loss, so the incumbent basis carries predictive value over class frequencies, descriptively and at
n = 22, with no significance claimed. Eleven consecutive runs closing with no new family. And a meta
signature of 57 for 57: **no blind prediction in this entire pass landed perfectly clean** — every one
surfaced structure its frozen partition did not name.

**What it did NOT produce, recorded with equal weight.** No live rival basis: two constructed
challengers scored below a constant predictor, and the retirement of B-A″ left the convergence
single-basis and therefore strictly weaker than a rival-tested one. FP-ROW, the pass's one prediction
about the READER, was falsified and retired. Ψ remains EXPERIMENTAL with an anchored noise floor that
licenses only one direction of inference. Of roughly twenty registered diagnostics, **three are
seated** — one of them the null itself.

## BATCH 17 FREEZE — P57 + P58 + P59; the ladder repaired TWICE more, and one module RECOVERED

**Continued use found two more defects, and the pattern is now the finding.** The ladder has needed
repair at P48 (excluded by NAME where it meant by ROLE) and twice again here. **Every defect was found
by USING the instrument, never by inspecting it** — which is the same lesson `sea-marangoni` taught at
a different level: an invariant nobody exercises is not evidence.

**DEFECT 2 — the double-record signature has a FALSE POSITIVE.** Batch 15 established that a
reference/scenes row is recorded twice. True, but so is a law row whose name is reused by the module's
IMPORT GUARD. `stormprop` has exactly two rows — `storm-property` (recorded twice) and its selftest —
so the v2 ladder excluded everything and returned **no central row at all**. The discriminator, still
structural because it reads only GUARD BOILERPLATE and never a law's meaning:

    an IMPORT guard's detail begins  "import failed"
    a REFERENCE guard's detail begins "reference failed"  or  "<...> scene failed"
    → a row is a REFERENCE row iff one of its records carries a REFERENCE guard.
      A row whose only duplicate is an IMPORT guard is a LAW row.

Verified: `magicdiv:scenes`, `sea:island` (reference failed) and `sea:wide` (wide scene failed) are
reference rows; `storm-property` and `commute-property` are law rows. **This retroactively vindicates
P37**, where `commute-property` was chosen as central by judgment before any ladder existed — the rule
now derives what judgment had reached, which is the right direction for a rule to travel.

**DEFECT 3 — the eligibility test was wrong, and it had silently EXCLUDED a briefable module.**
Read-eligibility was "the module has its own gate method". `terrain_bridge` has none — it is covered by
the shared `terrain` stage — so it was skipped this rung as if unclassifiable. But that stage IMPORTS
`terrain_bridge` and records `terrain:object`, `terrain-object-provenance` and `terrain-object-selftest`,
which are its rows; and the brief-falsifier check's binding condition (the citing stage imports the
module) is satisfiable. **Corrected rule: a module is READ-ELIGIBLE iff some gate stage imports it and
records rows.** `bench` is imported by NO stage and stays ineligible — now for a reason that is
measured rather than assumed.

**This changes the batch.** Under the corrected rule `terrain_bridge` re-enters the frontier ahead of
`terrain_view` lexically, so batch 17 is `splitview` → `stormprop` → `terrain_bridge`. Recorded because
a corrected instrument that quietly changed a selection without saying so would be worse than the
defect.

    LADDER v3 (step 1–2 unchanged; step 3 amended; step 4 added):
    3. else the FIRST substantive row in gate-method SOURCE ORDER, excluding the import-guard row,
       `-selftest`, and REFERENCE rows (identified by the guard idiom above).
    4. else, if exactly ONE non-selftest row remains, it is central.          → storm-property

**Selector**: lex over read-eligible unbriefed → `splitview` → `stormprop` → `terrain_bridge`.
**Batch rules**: sole basis B-M′; scoring is the v_D census and the meta. FP-ROW stays retired. Run-18
v_D fresh. L61 applied. Meta predicts ¬M-1 on all three (52 for 52).

### P57 — `splitview` (SCORING) — role: "The official server's own audit — the lonely-client and cut
    theorems" (URDRSPV1); ambient DISCLOSED: the authority arc's first rung, and the README summarises
    it ("a fork is detectable only by comparison, never by verification"). That states the FINDING,
    which is the P33/P49 situation → **NON-SCORING**. Read and briefed; enters no census, no meta.
    reading (unscored): C-FLOOR — a detectability guarantee shown absent for a lonely client.

### P58 — `stormprop` (SCORING) — role: "Property-based falsifier for the storm's PREFIX PROPERTY"
    (URDRSTP1); ambient: `storm` (W2, the adversarial-transport loom, UNREAD) and the sibling
    `commuteprop` (P37, C-EQ — a property falsifier whose central law was the property itself, with
    non-vacuity established rather than central). Central row: **`storm-property`** (ladder step 4).
    Body UNREAD.
    partition:        C-EQ (the prefix property itself central — the `commuteprop` precedent) · C-INV
                      (a structural invariant of the prefix) · C-FLOOR (the falsifier's own
                      non-vacuity central) · C-R · R-M · R-O.
    credences:        C-EQ 40 · C-INV 22 · C-FLOOR 20 · C-R 10 · R-M 4 · R-O 4. **Prior transferred
                      from resolved P37 and DISCLOSED** — the sibling falsifier module resolved C-EQ
                      with C-FLOOR established-not-central. Transfer stands at 1 hurt / 1 helped, so it
                      is priced ahead but not confidently. v_D=0 expected.

### P59 — `terrain_bridge` (SCORING) — role: "heightfield → URDROBJ2 bridge (T2, the D14 admission
    rung)" (URDRDOBJ2); ambient: `heightfield` (P-series, the T1 canon, briefed) shares its gate stage.
    Central row by ladder step 3 over the SHARED `terrain` stage, restricted to rows this module owns:
    **`terrain:object`** — the first substantive object-row in source order. Body UNREAD.
    partition:        C-R (an ADMISSION rung — the role says "the D14 admission rung" outright) ·
                      C-EQ (a bridge identity: the object view ≡ the heightfield) · C-REP (the object
                      as a certified representation) · C-INV · R-M · R-O.
    credences:        C-R 40 · C-EQ 24 · C-REP 20 · C-INV 10 · R-M 3 · R-O 3. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P57 — resolved (NON-SCORING, contamination declared): the zero is a property of the INPUT
    observed:         `splitview-law`: a forked server is **NOT detectable by verification and IS
                      detectable only by comparison** — the strongest solo detector flags **0 of 240**
                      forks while one crossing comparison flags **240 of 240** — and the decisive
                      clause, **the zero is a property of the INPUT, not a weakness of the detector**:
                      a confined client's transcript is BIT-IDENTICAL to the honest one, so there is
                      nothing in it to find and no cleverer verifier helps.
    scoring:          NONE — declared at the freeze under the P33/P49 rule.
    unnamed:          two plants worth naming. The **root-inequality detector is INVERTED**, crying
                      fork on **258 of 258 HONEST pairs** because differing roots are the resting state
                      rather than evidence — anti-correlated, and it would have looked SENSITIVE to
                      anyone who never ran it against honest input (L62's null-entrant lesson arriving
                      from a different direction). And **the cut theorem stated without its depth
                      hypothesis over-claims 3232 times** — true, and true only with the hypothesis.
    pattern:          the arc's cleanest instance of A ZERO THAT IS A RESULT: `sea-marangoni` insisted
                      a zero be earned by a plant that could have made it nonzero; here it is earned by
                      showing the INPUT is bit-identical, so no detector could have done better. *The
                      evidence is absent* versus *my instrument missed it* is the whole rung.

### P58 — resolved: **C-EQ** — lossy storms yield a PREFIX, not a corruption
    read:             2026-08-05, the blind READ (run 18). Classified from `storm-property` (ladder
                      step 4 — the row the v3 repair recovered).
    observed:         **loss-free storms converge to the authority witness (exactly-once); lossy storms
                      EQUAL THE AUTHORITY PREFIX**, verified against **`storm.prefix_witness`, an
                      independent oracle**, **with the prefix STRICTLY BELOW the full log**. The lossy
                      clause is the content: a client that missed messages gets a genuine PREFIX —
                      everything it has is true, it simply has less — not a corrupted or best-effort
                      view. The strictness clause is L61: a prefix equal to the full log would hold
                      trivially. `storm-property-selftest`: replacing the honest prefix oracle with the
                      FULL-LOG witness makes a lossy storm raise STORMPROP-FALSIFIED, and the module is
                      clean after the revert.
    class:            C-EQ; leading credence (40) CORRECT. v_D = 0.
    TRANSFER PAID AGAIN: the freeze disclosed the prior from P37 (`commuteprop`, the sibling falsifier,
                      C-EQ with non-vacuity established-not-central) and priced it ahead but not
                      confidently. **Cross-joint transfer now stands at 1 hurt (P38) / 2 helped (P55,
                      P58)** — kept as a record precisely because it is still small enough to state
                      honestly.
    unnamed (M-0):    the two falsifier modules are structurally identical — property as the central
                      law, non-vacuity discharged in the SELFTEST rather than the law row, and an
                      INDEPENDENT ORACLE (brute-permutation there, `prefix_witness` here). The
                      neutral-ruler pattern's NINTH instance.

### P59 — resolved: **C-EQ** — identity behind an admission rung · RUN 18 CLOSES
    read:             2026-08-05, the blind READ (run 18). Classified from `terrain:object` (ladder
                      step 3 over the SHARED `terrain` stage — the module the eligibility repair
                      recovered).
    observed:         the island and blank presets **bridge to pinned URDROBJ2 goldens ×2, the bridge's
                      OWN canon is IDENTICAL to `canon_ref`, and D14 ADMITs.** The middle clause is
                      load-bearing: the bridge produces an object whose canonical form equals the
                      independently held reference canon, so the conversion cannot drift into a private
                      notion of canonical. `terrain-object-provenance` carries the sharper law —
                      **identical geometry with DIFFERING PROVENANCE yields ONE URDROBJ2 identity**
                      (D14 clause 5), reddening on "provenance leaked into the object identity".
                      `terrain-refusal` is 6/6 typed under a stated principle: **refuse, never clamp**.
    class:            C-EQ. Author priced C-R 40 · C-EQ 24 — **the leading call missed**, on the role
                      line's word "admission"; the admission verdict is the CONSEQUENCE of the identity
                      holding, not the law. Recorded descriptively only: the prediction that tried to
                      generalize this recurrence (FP-ROW) was falsified and retired, so no claim is
                      drawn from it. v_D = 0.
    unnamed (M-0):    **IDENTITY MUST NOT ENCODE HISTORY.** A bridge that let provenance into the digest
                      would make two byte-identical terrains non-interchangeable, quietly breaking every
                      downstream comparison — and the gate NAMES that failure rather than trusting the
                      implementation to avoid it.
    LADDER DEFECT 4, found by use again: `terrain:object` is guarded by `f"bridge failed: {exc}"`, which
                      matches NEITHER frozen reference-guard idiom ("reference failed", "<...> scene
                      failed"), so v3 treated it as a law row. **Applied AS FROZEN** — and here the
                      frozen rule happened to select the row a corrected rule would also want, since
                      `terrain:object` carries the bridge identity rather than a bare digest
                      reproduction. The enumeration of guard idioms is nonetheless incomplete, and that
                      is the successor's obligation. Fourth defect, fourth time found by USING the
                      instrument rather than inspecting it.
    census:           run-18 v_D = 0, 0 (two scoring; P57 non-scoring) — RUN 18 CLOSES with no new
                      family, the tenth consecutive run. Meta ¬M-1: 54 for 54. Leading calls 1/2.

## BATCH 16 FREEZE — P54 + P55 + P56 (sealed before any READ)

**Selector**: lex successor reapplied → `sealframe` → `sealsession` → `sealwrit`. `bench` skipped by
the same mechanical test. **Ladder v2 applied mechanically**, all three at step 3 (no `-law`, no
`:laws`, reference rows excluded by the double-record signature): central rows are
**`sealframe-envelope`**, **`sealsession-lawful`**, **`sealwrit-provenance`**. Row names are structural
exposure as always; contents UNREAD.

**Batch rules**: sole basis B-M′; scoring is the v_D census and the meta. FP-ROW remains retired and is
not run. Run-17 v_D fresh. L61 applied. Meta predicts ¬M-1 on all three (49 for 49).

### P54 — `sealframe` (SCORING) — role: "THE SEALED FRAME (T3.55, V4)" (URDRSFR1); ambient: the
    visible phase (`panelight` V1 — P15 C-AB, `panewire` V2 — P26 C-AB, `ghostsnap` V3 — P22 C-R).
    Central row: `sealframe-envelope`. Body UNREAD.
    partition:        C-R (an admission of a sealed frame central) · C-EQ (a seal/replay identity) ·
                      C-INV (a structural invariant of the envelope) · C-PRICE (an ENVELOPE in
                      `opcost`'s sense — a bound on frame cost) · R-M · R-O.
    credences:        C-R 32 · C-EQ 26 · C-INV 20 · C-PRICE 14 · R-M 4 · R-O 4. **The word "envelope"
                      is genuinely ambiguous here** and the freeze refuses to resolve it: `opcost` used
                      "envelope" for a COST bound, while a sealing context invites the CONTAINER
                      reading. Frozen flat rather than guessing which sense the row means. v_D=0.

### P55 — `sealsession` (SCORING) — role: "THE ATTESTED SESSION (T3.56, V5) — visible-world CAPSTONE"
    (URDRSSN1); ambient: the visible phase above it. Central row: `sealsession-lawful`. Body UNREAD.
    partition:        C-AB (a CAPSTONE composing already-certified laws central — the
                      `meshsession`/`panewire` shape) · C-R (a lawfulness admission — the row is named
                      `-lawful`) · C-EQ · C-INV · R-M · R-O.
    credences:        C-AB 34 · C-R 30 · C-EQ 20 · C-INV 12 · R-M 2 · R-O 2.
                      **PRIOR TRANSFERRED FROM A RESOLVED JOINT, disclosed**: P48 (`meshsession`, the
                      OTHER capstone) resolved C-AB — a capstone composes — and that moves weight here.
                      Legitimate learning from a closed joint, but P38 recorded that such transfer can
                      hurt (`buoyancy` → `crossing` moved the credence the wrong way), so it is priced
                      only four points ahead of the row-name reading rather than confidently.

### P56 — `sealwrit` (SCORING) — role: "THE SIGNED WIRE (T3.49, W3) — WHO may write × WHAT may change"
    (URDRSWT1); ambient: the wire phase (`wire` P6 C-AB, `storm` W2, `driftgaze` W4 — P20 C-AB).
    Central row: `sealwrit-provenance`. Body UNREAD.
    partition:        C-R (an admission predicate — WHO may write, the `provbind` shape one phase
                      over) · C-AB (the role states a PRODUCT of two authorities, WHO × WHAT, which is
                      a two-law join) · C-EQ · C-INV · R-M · R-O.
    credences:        C-R 36 · C-AB 30 · C-EQ 18 · C-INV 12 · R-M 2 · R-O 2. The role's "×" is the
                      honest tension: it literally names two dimensions, which is C-AB's signature,
                      while the central row is named for provenance, which at P51 meant admission.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P54 — resolved: **C-EQ** — MODEL == EXECUTION; and the honesty ladder MECHANIZED
    read:             2026-08-05, the blind READ (run 17). Classified from `sealframe-envelope`.
    observed:         **the op envelope IS the loop's ACTUAL work — micro-steps == the glide
                      trajectory's own count, MODEL == EXECUTION** — so the budget cannot drift from
                      the thing it budgets. Two consequences ride on the identity: sprint costs
                      EXACTLY twice the walk, and the envelope FITS the 60Hz budget under the measured
                      native tick rate, stated as an inequality.
    class:            C-EQ. Author priced C-R 32 · C-EQ 26 — the leading call missed; "sealed frame"
                      read as something policed, and the row certifies an identity. v_D = 0.
    **THE FINDING — `sealframe-honesty` turns this repository's own CLAIM-GRADING LADDER into a gate
                      row.** Every MEASURED frame-budget entry must cite a NAMED-HOST log (the
                      unlogged-MEASURED defect is caught); `input→photon` stays NOT_MEASURED until a §3
                      run exists; and a host log GRADUATES a claim to MEASURED only when it NAMES a
                      host AND its input→photon is under target. `sealframe-selftest` bites: a tampered
                      host log refuses on its self-digest, an anonymous log cannot graduate a MEASURED
                      claim. **The discipline this entire arc is written under — no claim exceeding
                      what its evidence licenses — is here ENFORCED BY THE GATE rather than by the
                      author's care.** Everywhere else the ladder is a convention prose obeys; in this
                      module it is a row that reddens. The strongest instance in the arc of
                      `attestation ≠ authority` made executable.

### P55 — resolved: **C-AB** — the visible-world capstone composes
    read:             2026-08-05, the blind READ (run 17). Classified from `sealsession-lawful`.
    observed:         a genuine movement session, a wired session (live edits + streaming) and a
                      multiplayer session (ghost stream) **each replay through the UNMODIFIED loop,
                      wire and ghost laws to their OWN recorded witnesses — the whole visible world
                      attested in one trace, deterministically.** `sealsession-forge`: a forged avatar
                      / world / ghost witness (a session claiming an outcome the recorded input does
                      not produce) and **a cheater's malice-claimed edit — an illegal edit dressed as
                      admitted** — each refuse. `sealsession-selftest`: a tampered session refuses on
                      its self-digest, an anonymous one on the named-host law.
    class:            C-AB; leading credence (34) CORRECT. v_D = 0.
    CROSS-JOINT TRANSFER PAID, having cost at P38: the freeze DISCLOSED moving weight on P48
                      (`meshsession`, the other capstone, C-AB) while pricing it only four points ahead
                      because P38 recorded the same practice moving a credence the wrong way. **Transfer
                      between resolved joints now stands at 1 hurt, 1 helped** — the honest state of
                      that practice, not a vindication of it.
    unnamed (M-0):    BOTH capstones certify COMPOSITION rather than a new mechanism, and both phrase
                      it identically — laws UNMODIFIED, composed into ONE attested trace. A capstone in
                      this arc is not a new law; it is the claim that the existing ones do not
                      interfere.

### P56 — resolved: **C-R** — provenance refuses before the state law · RUN 17 CLOSES
    read:             2026-08-05, the blind READ (run 17). Classified from `sealwrit-provenance`.
    observed:         an unregistered, wrong-keyed, mis-signed or tail-collision-forged writ **refuses
                      BEFORE the state law with replica and ledger BYTE-IDENTICAL**, and the genuine
                      writ still admits — **a failed signature blocks nothing honest**. The plant is
                      pointed: **the first-byte defect verifier ACCEPTS the forgery the real one
                      refuses.**
    class:            C-R; leading credence (36) CORRECT. v_D = 0.
    **THE ORDERING IS THE THEOREM.** `sealwrit-order`: **eligibility precedes admission** — a writ that
                      is BOTH mis-signed and state-unlawful refuses SEAL (the ordering proof, since a
                      state-first system would have reported the other code); a perfectly signed stale
                      record refuses WIRE, because **a signature cannot launder state**; and neither
                      refusal seals anything — **eligibility is consumed by admission, never by
                      attestation**, which closes the attack of presenting a writ, having it refused on
                      state, and treating the signature as spent-and-therefore-verified. So the role's
                      "WHO × WHAT" is real but is NOT a two-law join: the axes are kept in a strict
                      ORDER with a proof that the order holds — which is why the central row reads as
                      admission rather than composition.
    unnamed (M-0):    `sealwrit-reuse` — the first admission SEALS THE KEYPAIR TO ITS DIGEST, so an
                      identical redelivery rides free to the CAS (at-most-once, inherited from the
                      wire) while a verified-DISTINCT state-lawful record under a sealed keypair
                      refuses on the ledger: the reuse leak's exact exploit, contained rather than
                      argued away.
    census:           run-17 v_D = 0, 0, 0 — RUN 17 CLOSES on a triple zero, the ninth consecutive run
                      with no new family. Meta ¬M-1: 52 for 52. Leading calls 2/3.

## BATCH 15 FREEZE — P51 + P52 + P53; the ladder defect REPAIRED by role, not by name

**THE SUCCESSOR OBLIGATION, discharged.** P48 recorded that the fallback ladder excluded reference rows
by NAME (`:scenes`) where it meant to exclude them by ROLE, and that `meshsession:sessions` — a
reference row wearing another name — was wrongly selected as central. That defect is repaired here,
BEFORE any of this batch is read, with a test that is **structural and content-free**:

    A reference/scenes row is recorded TWICE in its gate method — once in the `except` branch
    ("reference failed: {exc}") and once in the success branch. **Any row recorded more than once is
    a reference row and is excluded from ladder step 3.**

Verified against every module read so far: `magicdiv:scenes`, `predict:scenes`, `provbind:scenes`,
`quintessence:scenes`, `sea:island`, `sea:wide` and **`meshsession:sessions` all record twice**, while
`meshattest:laws`, `predict-equivalence`, `magicdiv-law` and every other substantive row records once.
The signature separates them exactly, and it reads the SHAPE of the gate method rather than any row's
content. **It changes this batch**: the old ladder would have selected `sea:island` (a reference row);
the repaired one selects `sea-conservation`.

    THE LADDER, v2 (steps 1 and 2 unchanged):
    1. `<module>-law` if present.                                            → provbind
    2. else `<module>:laws` if present.
    3. else the FIRST substantive row in gate-method SOURCE ORDER, excluding the import guard,
       `-selftest`, and ANY ROW RECORDED MORE THAN ONCE.                     → quintessence-essence · sea-conservation

**FP-ROW IS NOT RUN.** It was retired irreversibly at batch 14 and may not be reinstated by rewording;
no role-vs-row readings are declared below. What survives from it is the narrow true statement already
recorded — the two disagree often enough to be worth distinguishing, and neither dominates — and that
statement makes no prediction, so it licenses none.

**Selector**: lex successor reapplied → `provbind` → `quintessence` → `sea`. `bench` skipped by the
same mechanical test. **Batch rules**: sole basis B-M′; scoring is the v_D census and the meta. Run-16
v_D fresh. L61 applied. Meta predicts ¬M-1 on all three (46 for 46).

**CONTAMINATION DISCLOSED for P53.** `sea` carries rows named `sea-marangoni` and
`sea-marangoni-selftest` (names seen during the ladder computation; contents UNREAD). Earlier in this
session the operator proposed a "Discrete Marangoni Interface Theorem (URDRMRG1)" as NEW work, in
ignorance that the arc already had a Marangoni row. That is prior exposure to a Marangoni FRAMING from
the conversation — but not to this module's finding, since the proposal was a new construction rather
than a description of what `sea` certifies. Recorded, and the joint stays SCORING under P41's ruling.

### P51 — `provbind` (SCORING) — role: "Provenance binding (S3) — a certificate bound to its lattice,
    or refused" (URDRPRV1); ambient: the city arc (`voxlat` S1, `divergence` S2 — P41 C-FLOOR,
    `geoquorum` S4 — P21 C-SPLIT). Central row: **`provbind-law`** (ladder step 1). Body UNREAD.
    partition:        C-R (a binding predicate that admits or REFUSES central — the role says "or
                      refused" outright) · C-INV (a binding structural invariant) · C-EQ (a
                      certificate ≡ lattice identity) · C-FLOOR · R-M · R-O.
    credences:        C-R 42 · C-INV 20 · C-EQ 18 · C-FLOOR 10 · R-M 5 · R-O 5. v_D=0 expected.

### P52 — `quintessence` (SCORING) — role: "ID-0 representation theorem (T3.46) — the fifth essence"
    (URDRQNT1); ambient: the named chain after `testament` (P30, C-EQ) and before the wire phase.
    Central row: **`quintessence-essence`** (ladder step 3). Body and history UNREAD.
    partition:        C-EQ (a REPRESENTATION THEOREM states an equivalence between two descriptions —
                      the strongest reading) · C-REP (a certified representation central) · C-INV ·
                      C-R · R-M · R-O.
    credences:        C-EQ 38 · C-REP 26 · C-INV 16 · C-R 12 · R-M 4 · R-O 4. The honest tension: a
                      "representation theorem" in mathematics IS an equivalence (every object of a
                      class is isomorphic to a canonical one), but this arc has a live C-REP class that
                      the words invite. v_D=0 expected.

### P53 — `sea` (SCORING) — role: "Terrain sea as certified field state (S1/S2)" (URDRFLD1); ambient:
    the foundation wave family (`wavefield` P12 C-AB, `buoyancy` P34 C-INV, `crossing` P38 C-EQ).
    Central row: **`sea-conservation`** (ladder step 3, repaired). Body UNREAD.
    partition:        C-INV (a CONSERVATION invariant central) · C-EQ (a field identity) · C-R ·
                      C-PRICE · R-M · R-O.
    credences:        C-INV 44 · C-EQ 20 · C-R 16 · C-PRICE 10 · R-M 5 · R-O 5. **Disclosed weakness of
                      this call**: the row is NAMED `sea-conservation`, so its name leaks its class,
                      exactly as `predict-equivalence` did at P50. Recorded as an easy joint in
                      advance; a hit here is worth less than a hit at P52. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P51 — resolved: **C-R** — bound by a digest the supplier cannot assert
    read:             2026-08-05, the blind READ (run 16). Classified from `provbind-law` (ladder 1).
    observed:         the provenance certificate is **BOUND to the geometry it certifies by
                      H(cert | lattice_digest) with the lattice digest RECOMPUTED AT SERVE TIME**, so
                      **the binding cannot be asserted by whoever supplied it**; every carried field,
                      including the capture-time buffer distance, enters the digest.
                      `provbind-selftest`: the **metadata-only digest — the handed-down form — matches
                      a DIFFERENT block's geometry**, so a permissive certificate lifted off a
                      public-domain block and stapled to a restricted capture is **ADMITTED**. The
                      inherited design admits exactly the attack the layer exists to stop.
    class:            C-R; leading credence (42) CORRECT. v_D = 0.
    unnamed (M-0):    RECOMPUTE-RATHER-THAN-TRUST — the neutral-ruler pattern's EIGHTH instance (mesh's
                      monolith, traj's locally-derived truth, cayley's two algorithms, commuteprop's
                      brute-permutation oracle, horn's independent sweep, meshattest's re-minted
                      certificate, wardhom, this); and grade-what-you-inherit a fourth time, the
                      handed-down form refuted by exhibiting the admission it permits.

### P52 — resolved: **C-REP** — the extractor is faithful; the equivalence is downstream
    read:             2026-08-05, the blind READ (run 16). Classified from `quintessence-essence`
                      (ladder step 3).
    observed:         **the extractor is TOTAL and DETERMINISTIC over the five families with FULL-TUPLE
                      INJECTIVITY** — every record has an essence, the same record always yields the
                      same one, and distinct records never collide, so nothing that distinguishes two
                      records is discarded. Within a family, **history and validity are the SAME
                      address at a SCOPE** (world vs chunk, the RAN-0 rebinding, visible in the tuple),
                      and **the scope difference PREDICTS the transport theorem**.
                      `quintessence-lineage` carries the theorem's other half: every order of one edit
                      set carries the same essence set to the same head — **the lineage is the
                      equivalence class, not the path** — with **heads in BIJECTION with lineages**.
                      `quintessence-refuse`: nothing is guessed outside the five families, and the
                      **five-axis conservation ablation** holds — degrade any ONE axis (parent /
                      region / height / currency / byte) and admission refuses. No authority without
                      every axis.
    class:            C-REP. The author priced C-EQ 38 · C-REP 26 — **the leading call missed**. The
                      reasoning that "a representation theorem IS an equivalence" is sound about the
                      THEOREM, and the bijection in `-lineage` is exactly that; but the row the ladder
                      selects certifies the extractor's FAITHFULNESS. The arc splits representation
                      from the equivalence it enables, into separate rows. v_D = 0.
    unnamed (M-0):    the ablation — five axes each individually load-bearing, so the conservation is
                      not a conjunction anyone can partially satisfy.

### P53 — resolved: **C-INV** — exact conservation · and a MARANGONI law already in the arc · RUN 16 CLOSES
    read:             2026-08-05, the blind READ (run 16). Classified from `sea-conservation` (ladder
                      step 3, **repaired** — the old ladder would have selected the reference row
                      `sea:island`).
    observed:         **total mass EXACT across 40 masked ticks — and the field genuinely moved**, the
                      second clause being the L61 non-vacuity witness that stops a frozen field from
                      satisfying conservation trivially. `sea-coast`: land identically zero at init and
                      after evolution, and an **all-sea mask is bit-for-bit identical to the frozen
                      step**. `sea-selftest`: the UNMASKED evolution wets land and diverges, so the
                      mask is load-bearing. 4/4 typed refusals.
    class:            C-INV; leading credence (44) correct — and **disclosed in advance as an EASY
                      call**, since the row name leaks its class. Scored as the freeze said: worth less
                      than P52's. v_D = 0.
    **THE FINDING: THE ARC ALREADY HAS A MARANGONI LAW.** `sea-marangoni` certifies **mass EXACT +
                      monotone 30/30 ticks (audited, not estimated) + THE PEAK PERSISTS ABOVE PURE
                      DIFFUSION + land dry — surface tension on the masked domain.** The peak clause is
                      the Marangoni signature proper: surface-tension-driven transport sustaining a
                      concentration peak that diffusion alone would flatten. Earlier this session the
                      operator proposed a "Discrete Marangoni Interface Theorem (URDRMRG1)" as NEW
                      work; the freeze disclosed the exposure, and the READ now supplies the correction
                      — **a substantial part of that proposal already exists, gated, in `sea`.**
                      Recorded as a finding about the ARC's inventory, and it is the strongest argument
                      yet for finishing the READ pass before proposing new theory: the proposal was
                      authored against an incomplete map of what was already built.
    unnamed (M-0):    `sea-marangoni-selftest` plants the sharp case — **the over-bound κ overshoots
                      negative YET CONSERVES MASS.** A defect that satisfies the headline invariant
                      would pass a conservation-only check, so the CFL bound is tested by a plant
                      conservation cannot catch. **An invariant a defect can satisfy is not sufficient
                      evidence** — the same reasoning as `magicdiv`'s powers-of-two multiplier and
                      `divergence`'s identical-rate perturbations, now on a physical bound.
    census:           run-16 v_D = 0, 0, 0 — RUN 16 CLOSES on a triple zero, the eighth consecutive run
                      with no new family. Meta ¬M-1: 49 for 49. Leading calls 2/3, one of them
                      pre-disclosed as easy.

## BATCH 14 FREEZE — P48 + P49 + P50; FP-ROW re-frozen with the branch `membrane` proved it needed

**ERRATUM, the SECOND of its exact kind — and the pattern is now the finding.** The previous rung's
closing note stated batch 14 would be `meshsession` → `oobprior` → `patience`. **`oobprior` is already
briefed**; the recomputed selector returns `meshsession` → `patience` → `predict`. Batch 12's freeze
recorded the identical failure (naming `disjoint`, already briefed). Two consecutive rungs, same
mechanism: **the operator states a joint from recollection in the CLOSING PROSE, where no gate looks.**
Both were caught by the next rung's mandatory recomputation, so nothing was ever frozen wrong — but the
concentration is the point. Every error of this class in the whole pass (P8's drift, batch 12's, this
one) has occurred in narrative text outside the frozen artifacts. The gate covers the ledger; nothing
covers the summary. Recorded, and the operational fix is stated rather than promised: **a closing note
may not name the next batch unless the selector was recomputed to produce it.**

**FP-ROW v2 — re-frozen with the mandatory catch-all.** `membrane` (P46) resolved to a class NEITHER
pre-declared reading named, an outcome FP-ROW v1's partition did not cover — L60's own lesson landing
on L60's own instrument. The successor carries the branch, exactly as P4 carried R3:

    FP-ROW v2, per joint: declare a ROLE-reading and a ROW-reading in advance. Outcomes are TOTAL:
      ROW      — resolves to the ROW-reading            → supports the directional claim
      ROLE     — resolves to the ROLE-reading           → FALSIFIES the directional claim
      NEITHER  — resolves to some third class           → directional claim UNTOUCHED, PRECISION fails
      SAME     — the two readings agree                 → NON-DISCRIMINATING, tests nothing
    Standing after batch 13: directional 1-for-1 (P47 ROW); precision 1 NEITHER (P46), 1 SAME (P45).

**THE FALLBACK LADDER, extended and frozen BEFORE any content is read.** Two of this batch's three
modules have no `<module>-law` row, and `meshsession` has no `:laws` row either, so the P47 fallback is
insufficient. The ladder is fixed now, while it is still inconvenient — and each step is STRUCTURAL
(row names and source order), never content:

    1. `<module>-law` if present.                              → patience
    2. else `<module>:laws` if present.                        → (meshattest, P47)
    3. else the FIRST substantive row in the gate method's SOURCE ORDER, excluding the import guard,
       `:scenes` and `-selftest` — the author's own sequencing of the module's claims.
                                                               → meshsession:sessions · predict-equivalence

**Selector**: lex successor reapplied → `meshsession` → `patience` → `predict`. `bench` skipped by the
same mechanical test. **Batch rules**: sole basis B-M′; scoring is v_D, the meta, and FP-ROW v2.
Run-15 v_D fresh. L61 applied. Meta predicts ¬M-1 on all three (44 for 44).

### P48 — `meshsession` (SCORING) — role: "Attested mesh session (M5) — the Phase M capstone"
    (URDRMSS1); ambient: Phase M (`nway` M1, `migrate` M2, `meshattest` M2.5 — P47 C-EQ, `mesh` M3 —
    P25 C-EQ, `partition` M4). Central row by ladder step 3: **`meshsession:sessions`**. Body UNREAD.
    ROLE-reading:     **C-AB** — a CAPSTONE composes previously-certified laws and shows them holding
                      together, which is `panelight`/`panewire`'s shape (both C-AB).
    ROW-reading:      **C-EQ** — the Phase M family has resolved C-EQ twice running (`mesh`,
                      `meshattest`), and a `:sessions` row over an attested session most plausibly
                      certifies that a full session replays equal to its law.
    FP-ROW status:    **DISCRIMINATING.** FP-ROW v2 predicts C-EQ.
    partition:        C-EQ · C-AB · C-R · C-INV · R-M · R-O.
    credences:        C-EQ 34 · C-AB 30 · C-R 18 · C-INV 10 · R-M 4 · R-O 4. v_D=0 expected.

### P49 — `patience` (SCORING) — role: "The price of the price — the exclusion ladder holds only at
    T ≥ Δ" (URDRPAT1); ambient DISCLOSED and substantial: the authority arc's third rung, and
    `hainuwele/README.md` summarises it ("a server that STALLS rather than excludes gets the same
    partition at a visible cost of zero, collapsing the 1/2/∞ ladder to 0/0/0 below the delay
    envelope"). That is a statement of the FINDING, not merely a boundary — the P33 (`bombtest`)
    situation. **Recorded NON-SCORING for FP-ROW and for the v_D census**; it is read and briefed, and
    it enters no count. The line stays auditable: README text that states a finding ⇒ non-scoring;
    README text that states a `does_not_show` ⇒ scoring (P41's ruling).
    reading (unscored): C-FLOOR — a ladder collapsing to 0/0/0 is an inherited guarantee refuted.

### P50 — `predict` (SCORING) — role: "Client-prediction RECONCILE primitive (T3.17, Stage A)"
    (URDRPRED1); ambient: `cpredict` (P19, NON-SCORING, the continuous sibling), `glide`, `splice`.
    Central row by ladder step 3: **`predict-equivalence`**. Body and history UNREAD.
    ROLE-reading:     **C-R** — "reconcile" suggests adjudicating a client claim, i.e. admission.
    ROW-reading:      **C-EQ** — the row NAME is `predict-equivalence`, and step 3 of the ladder
                      selects it; a reconcile primitive whose central row is named for an equivalence
                      most plausibly certifies that predicted-then-reconciled equals authoritative.
    FP-ROW status:    **DISCRIMINATING** — though weakly, since the row NAME leaks its own class here,
                      which is disclosed: this joint is an easier test than P48 and is scored as such.
    partition:        C-EQ · C-R · C-REP · C-INV · R-M · R-O.
    credences:        C-EQ 46 · C-R 24 · C-REP 14 · C-INV 8 · R-M 4 · R-O 4. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P48 — resolved: **C-AB** — the capstone composes · **FP-ROW's DIRECTIONAL CLAIM FALSIFIED**
    read:             2026-08-05, the blind READ (run 15). Classified from `meshsession:sessions`, the
                      row the frozen fallback ladder selected before any content was read.
    observed:         **concurrency (M1), migration (M2) and a partition episode (M4) COMPOSED into one
                      attested timeline** — the campaign and skirmish multi-authority playthroughs
                      reproducing URDRMSS1 checkpoint-chain digests, deterministically. The distinctive
                      claim is the COMPOSITION: not that each law holds, which its own rung
                      established, but that a session exercising all three produces one chain no member
                      contradicts. `meshsession:forges` carries `meshattest`'s principle forward —
                      **reality may not overrule the COMPOSED mesh law on any axis** — with five
                      forgeries refusing; `meshsession-selftest` refuses a single byte flip.
    class:            C-AB (the `panelight`/`panewire` capstone shape). Author priced C-EQ 34 · C-AB 30
                      — the leading call missed by four. v_D = 0.
    **FP-ROW v2 = ROLE. THE DIRECTIONAL CLAIM IS FALSIFIED** by its own frozen terms ("FALSIFIED iff
                      any joint where the two differ resolves to the ROLE-reading"). The freeze
                      declared role C-AB (a capstone composes) against row C-EQ (Phase M had resolved
                      C-EQ twice running). **The role prose was the better guide.** The five-batch
                      pattern that motivated FP-ROW does NOT generalize into "the row always wins", and
                      one counter-instance stated that strongly is enough to end the claim. Standing:
                      2 ROW (P47, P50) · 1 ROLE (P48) · 1 NEITHER (P46) · 1 SAME (P45).
    LADDER DEFECT, recorded because the selection was load-bearing: the frozen ladder takes the first
                      substantive row in source order **excluding rows NAMED `:scenes`** — and
                      `meshsession:sessions` IS this module's scenes row under another name, carrying
                      the digest-reproduction pattern verbatim. **The ladder excludes by NAME where it
                      meant to exclude by ROLE.** It was applied AS FROZEN (a ladder rewritten after
                      seeing which row flatters the prediction is not a ladder), but a corrected ladder
                      would have reached `meshsession:forges` — plausibly C-R — and the FP-ROW verdict
                      could have differed. The defect is the successor's obligation, not this rung's
                      licence to re-pick.

### P49 — resolved (NON-SCORING, contamination declared): the visibility auditgraph sold was DECLARED
    observed:         `patience-law`: `auditgraph` priced undetected equivocation at kappa and sold it
                      as converting an INVISIBLE INTEGRITY attack into a VISIBLE AVAILABILITY one —
                      **and every word rests on "visible", which both it and `splitview` DECLARED
                      rather than established.** Chandra–Toueg is the reason: a crashed process and an
                      arbitrarily slow one are indistinguishable to an asynchronous observer, so a
                      server that STALLS rather than excludes takes the same partition at a visible
                      cost of ZERO. The ladder holds only at T ≥ Δ; below the envelope 1/2/∞ collapses
                      to **0/0/0**.
    scoring:          NONE — declared at the freeze under the P33 rule (the README states the FINDING,
                      not a boundary). No census, no meta, no FP-ROW entry.
    unnamed:          `patience-selftest` names a class the repo had no cell for — **LINEAR patience
                      growth is SOUND** (it terminates, and the test asserts it) **and loses on PRICE
                      ALONE**: 63 false alarms where doubling costs 6, and 199 against 8 at Δ/T₀ = 200.
                      A correct alternative rejected purely on cost is a different refutation from a
                      wrong one. Also: this is the ashdepth/recirc/divergence refutation shape aimed at
                      a SIBLING RUNG rather than at handed-down literature — the first such instance.

### P50 — resolved: **C-EQ** — rollback-replay equivalence · FP-ROW's second win · RUN 15 CLOSES
    read:             2026-08-05, the blind READ (run 15). Classified from `predict-equivalence`, the
                      row the frozen ladder selected.
    observed:         **`reconstruct == drive(auth)` for every prediction**, and the sharper half —
                      **the reusable prefix is BIT-IDENTICAL to the authority, so partial rollback ==
                      full re-simulation**: the optimization that makes prediction affordable is proven
                      to equal the exhaustive alternative, which is the claim an implementation is most
                      tempted to assume. `predict-localize`: **reconcile IS `lockstep.first_desync`**; a
                      correct prediction needs no rollback; and a **different-input, same-pose**
                      prediction needs none either — the reconcile is POSE-level, not input-level.
                      `predict-refusal`: the lazy-reconcile defect diverges, 3/3 typed PRED-REFUSE.
    class:            C-EQ; leading credence (46) CORRECT.
    FP-ROW v2 = ROW, at REDUCED WEIGHT as disclosed at the freeze: the row is NAMED
                      `predict-equivalence`, so its name leaks its class and the test was easier than
                      P48's. Counted as a win, weighted as the freeze said it would be.
    unnamed (M-0):    the POSE-LEVEL clause — a reconcile comparing INPUTS would refuse a client whose
                      different keystrokes produced an identical pose, punishing the route rather than
                      the destination; certifying at pose level is exactly what `splice`'s
                      memorylessness needs downstream.
    census:           run-15 v_D = 0, 0 (two scoring joints; P49 non-scoring) — RUN 15 CLOSES with no
                      new family, the seventh consecutive run without one. Meta ¬M-1: 46 for 46.
                      Leading calls 1/2 scoring.
    **FP-ROW v2, FINAL SCORE AND WHAT IT BOUGHT.** Directional claim: **FALSIFIED** (P48). Precision:
                      one NEITHER (P46). Wins: two, one of them weakened by a leaking row name (P50).
                      The instrument was built to be falsifiable and it was falsified in two rungs —
                      which is a better outcome than a third confirmation, because the alternative was
                      carrying an unfrozen five-batch grievance indefinitely. **What survives is
                      narrower and true: role prose and central rows disagree often enough to be worth
                      declaring separately, and NEITHER one dominates.** FP-ROW is RETIRED under L63 —
                      irreversibly, and it may not be reinstated by adjusting its wording. A successor
                      would need a fresh preregistration with a genuinely different claim.

## BATCH 13 FREEZE — P45 + P46 + P47, and FP-ROW: the first prediction about the READER

**FP-ROW — the frozen forward prediction the previous rung obliged.** The role-prose-over-row failure
recurred in five consecutive batches (P34, P38, P41, P42, P44), which is the recurrence that licenses
a frozen claim rather than a recorded complaint. It is stated here as **two SEPARATELY PRE-DECLARED
readings per joint** — a role-based class and a row-based class — so the adjudication is between two
predictions made in advance, never between a resolution and a story told afterwards:

    FP-ROW: where the ROLE-reading and the ROW-reading differ, the ROW-reading wins.
    CORRECT iff every joint resolves to its declared ROW-reading.
    FALSIFIED iff any joint where the two differ resolves to the ROLE-reading.
    (A joint where both readings agree tests nothing and is marked NON-DISCRIMINATING.)

This is the pass's **first prediction about the reader rather than the code**, and it can fail: if the
role prose is actually a good guide and the last five batches were a run of bad luck, FP-ROW loses.

**THE `-law` FALLBACK, frozen BEFORE reading because P47 forces it.** The tie-break used through P44
was "`<module>-law` is the central row". `meshattest` has NO such row — its rows are `meshattest:laws`,
`:forges`, `:trace`, `-selftest` (names seen during eligibility checking; contents UNREAD, disclosed as
exposure exactly as batch 11 disclosed `clslo`'s). The fallback is fixed now, while it is still
inconvenient: **absent a `<module>-law` row, the central row is the one whose NAME denotes the module's
laws — here `meshattest:laws`.** Frozen in advance so the choice cannot be made after seeing which row
flatters the prediction.

**Selector**: lex successor reapplied → `magicdiv` → `membrane` → `meshattest`. `bench` skipped by the
same mechanical test, re-verified. **Batch rules**: sole basis B-M′; scoring is the v_D census, the
meta, and FP-ROW. Run-14 v_D fresh. L61 applied. Meta predicts ¬M-1 on all three (41 for 41).

### P45 — `magicdiv` (SCORING) — role: "Division by an invariant constant, exact and exhaustively
    proven" (URDRMAG1); ambient: the exact-arithmetic substrate alongside `cayley` (P35, C-EQ). Body
    and history UNREAD.
    ROLE-reading:     **C-EQ** — "exact and exhaustively proven" names an identity discharged by
                      exhaustion (the multiply-shift equalling true division).
    ROW-reading:      **C-EQ** — `magicdiv-law` would carry that same identity.
    FP-ROW status:    **NON-DISCRIMINATING** (the two agree; this joint tests the meta and v_D only).
    partition:        C-EQ · C-PRICE (a cost/speed claim central) · C-INV · C-FLOOR · R-M · R-O.
    credences:        C-EQ 48 · C-INV 16 · C-PRICE 14 · C-FLOOR 12 · R-M 5 · R-O 5. v_D=0 expected.

### P46 — `membrane` (SCORING) — role: "The semantic membrane — advisory, structural, and unable to
    starve" (URDRMEM1); ambient: a hygiene rung alongside `frontier` (P13, R-O, the approximation
    axis's first sighting) and `ashdepth` (P17, C-FLOOR). Body and history UNREAD.
    ROLE-reading:     **C-FLOOR** — the leading adjective is ADVISORY, i.e. it deliberately does NOT
                      decide, which is the shape `recirc` ("there is no loop") and `ashdepth` ("a void
                      is sound") both resolved: an inherited expectation of enforcement, refused.
    ROW-reading:      **C-INV** — a row named `membrane-law` should carry a POSITIVE structural law,
                      and the role's own third clause ("unable to STARVE") is a liveness invariant.
                      The advisory framing would then be `does_not_show` material rather than the law.
    FP-ROW status:    **DISCRIMINATING — the batch's live test.** FP-ROW predicts C-INV.
    partition:        C-INV · C-FLOOR · C-R · C-EQ · R-M · R-O.
    credences:        C-INV 32 · C-FLOOR 30 · C-R 16 · C-EQ 12 · R-M 5 · R-O 5. Frozen near-flat on
                      purpose: FP-ROW is what carries the call here, not the credence spread. v_D=0.

### P47 — `meshattest` (SCORING) — role: "Mesh reality attestation (M2.5) — real sockets, real
    processes" (URDRMAT1); ambient: Phase M (`nway` M1, `migrate` M2, `mesh` M3 — P25 C-EQ); the arc's
    sibling `wireattest` (W5, "THE REALITY ATTESTATION — real sockets") is UNREAD. One of the four
    TRUE CONFORMANCE GAPS (gate stage + falsifiers, no pinned corpus). Body and history UNREAD.
    ROLE-reading:     **C-R** — an ATTESTATION reads as a certificate that admits or refuses.
    ROW-reading:      **C-EQ** — under the frozen fallback the central row is `meshattest:laws`, and
                      the arc's attestation pattern is an EQUIVALENCE (what a real-socket, real-process
                      run computes equals what the in-process run computes), the `mesh`/`hand`
                      bit-identity shape carried across a real transport.
    FP-ROW status:    **DISCRIMINATING.** FP-ROW predicts C-EQ.
    partition:        C-EQ · C-R · C-AB · C-INV · R-M · R-O.
    credences:        C-EQ 35 · C-R 30 · C-AB 15 · C-INV 10 · R-M 5 · R-O 5. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P45 — resolved: **C-EQ** — the identity decided over the whole word (NON-DISCRIMINATING for FP-ROW)
    read:             2026-08-05, the blind READ (run 14). Classified from the LIVE `magicdiv*` rows.
    observed:         `magicdiv-law`: **floor(n/d) == (m*n) >> s, DECIDED EXHAUSTIVELY over the whole
                      word** — every divisor × every dividend, 0 failures, "a decided finite statement,
                      not a sampled sweep". The row also GRADES the handed-down corollaries rather than
                      repeating them: the Hausdorff-dimension claim that arrived with the technique is
                      **REFUTED by definition**. `magicdiv-selftest`: the floor-instead-of-ceil
                      multiplier fails on some divisors **while remaining CORRECT for powers of two** —
                      the plant is chosen to be exactly the one a sampled check would have passed.
    class:            C-EQ; leading credence (48) CORRECT. Both pre-declared readings said C-EQ, so
                      this joint is NON-DISCRIMINATING for FP-ROW by its own frozen terms. v_D = 0.
    unnamed (M-0):    enumerate-don't-sample on its FOURTH carrier (voxlat, cayley, divergence,
                      magicdiv) — L20 turned into code four times; and GRADE-WHAT-YOU-INHERIT, the same
                      move `divergence` made against the rate metric and `horn` against the continuous
                      bound.

### P46 — resolved: **C-EQ** — invariance of the admitted set; **NEITHER pre-declared reading was right**
    read:             2026-08-05, the blind READ (run 14). Classified from the LIVE `membrane*` rows.
    observed:         `membrane-law`: **every lawful membrane produces the IDENTICAL admitted set** —
                      decided against NINE, including a reversed order, a both-ends-interleaved
                      adversarial order, and **one that puts a chosen obligation last every time
                      specifically to starve it** — so "an adaptive layer changes how efficiently truth
                      is reached and never what truth is". `membrane-selftest` refuses three plants
                      EACH WITH ITS OWN NAME rather than tolerating them: the FILTERING membrane drops
                      obligations (named as the accelerator's characteristic failure, since silently
                      discarding what you cannot handle looks exactly like handling it), the INJECTING
                      membrane creates state, and the third likewise reddens.
    class:            C-EQ, **priced FOURTH at 12**. The same-quantity-under-nine-orderings shape is
                      `commuteprop`'s (every order lands one head+field) and `mesh`'s — both C-EQ.
                      "Advisory" is the CONSEQUENCE of the invariance, not the law; "unable to starve"
                      is the adversarial witness that the invariance is non-vacuous, not a separate
                      claim. v_D = 0.
    **FP-ROW: THE OUTCOME ITS OWN PARTITION DID NOT NAME.** The freeze declared role-reading C-FLOOR
                      and row-reading C-INV, and predicted the row wins. The joint resolved to
                      **NEITHER**. Under the frozen rule this is not FALSIFIED (the role-reading did
                      not win) and not CORRECT (it did not resolve to the row-reading) — the outcome
                      space was **INCOMPLETE**. That is precisely the L60 failure P3's meta suffered,
                      recurring at a new level: the pass's first prediction ABOUT THE READER was itself
                      non-exhaustive, because it assumed the true class must be one of the two readings
                      on offer. **L60's own lesson, applied to L60's own instrument.** Recorded, not
                      repaired: the frozen text stands and the successor freeze must carry a
                      mandatory third branch (NEITHER-READING), exactly as P4 carried R3.

### P47 — resolved: **C-EQ** — reality replays lawful · FP-ROW's FIRST WIN · RUN 14 CLOSES
    read:             2026-08-05, the blind READ (run 14). Classified from `meshattest:laws`, the row
                      the FROZEN FALLBACK named before any content was read.
    observed:         the synthetic handoff (A→B, a usurper refused, a disjoint region untouched) and
                      the relay (A→B→C custody chain, a mid-chain usurper refused) **each replay LAWFUL
                      under the UNMODIFIED migrate law, deterministically** — and the decisive clause,
                      **the migration certificate the checker re-mints MATCHES reality's record**. The
                      law is not adapted for the real transport; the real transport is shown to satisfy
                      it already. `meshattest:forges` supplies the adversarial half under one principle
                      — **reality may not overrule the law** — with seven attacks each refusing typed;
                      `meshattest-selftest` shows a single byte flip refusing on the self-digest and an
                      anonymized re-seal refusing on the named-host law.
    class:            C-EQ; leading credence (35) correct.
    **FP-ROW: CORRECT, and genuinely discriminating.** Role-reading C-R (an attestation reads as
                      something that admits or refuses) vs row-reading C-EQ (the arc's attestation
                      pattern is an equivalence across a real transport). The ROW WON. This is the
                      first joint where the two readings differed and the row-reading was vindicated —
                      the claim about the reader earning its first evidence.
    unnamed (M-0):    a second TRUE-CONFORMANCE-GAP module explained rather than merely listed (after
                      `view_witness`, P32): an attestation whose subject is a live socket run cannot
                      have its evidence pinned in advance without ceasing to be an attestation, so the
                      missing corpus is a consequence of what the module IS, not a debt.
    census:           run-14 v_D = 0, 0, 0 — RUN 14 CLOSES on a sixth consecutive triple zero. Meta
                      ¬M-1: 44 for 44. Leading calls 2/3. **All three joints resolved C-EQ** — the
                      pass's first uniform batch, and worth noting only as a description: with the
                      selector now lex and the frontier drawn from substrate and hygiene rungs, exact
                      identities are what these modules mostly certify.
    **FP-ROW, SCORED HONESTLY:** one NON-DISCRIMINATING (P45), one CORRECT (P47), one NEITHER (P46).
                      Not falsified — the role-reading won nowhere — but not correct either, and its
                      partition was incomplete. Verdict: **PARTIALLY SUPPORTED, and the instrument
                      needs its own catch-all before it is scored again.** The successor obligation is
                      exact: batch 14's freeze carries FP-ROW with a mandatory NEITHER branch, and a
                      joint resolving there counts against the prediction's PRECISION (it named the
                      wrong two candidates) while leaving its DIRECTIONAL claim (role never beats row)
                      still standing at 1-for-1.

## BATCH 12 FREEZE — P42 + P43 + P44 (sealed before any READ)

**ERRATUM, recorded because it is the P8 pattern recurring in miniature.** The closing note of the
previous rung stated batch 12 would be `disjoint` → `fpcap` → `fpface`, from memory. **`disjoint` is
already briefed** (its record sits in the provenance ledger), so the recomputed selector returns
`fpcap` → `fpface` → `horn`. Nothing was frozen on the wrong list and no prediction was contaminated —
the drift lived only in a prose sentence — but it is the identical failure the P8 erratum caught: an
operator naming a joint from recollection instead of from the computation. Recorded rather than
silently corrected, because the ledger's rule is that the selector is RECOMPUTED FRESH every rung and
prose is never its source.

**Selector**: the frozen lex successor reapplied → `fpcap` → `fpface` → `horn`. `bench` skipped by the
same mechanical eligibility test, re-verified.

**Batch rules**: sole basis B-M′; scoring is the v_D census and the meta only. Run-13 v_D fresh. L61
applied. Meta predicts ¬M-1 on all three (38 for 38).

**A standing caution carried INTO this freeze, and deliberately not "corrected" for.** Three of the
last four batches produced a leading-class miss whose cause was the same — weighing the module's JOB
(what the rung is *for*) over what its central ROW certifies. Under L63 that observation has no
standing (no frozen prediction has named it in advance), so the credences below are NOT adjusted to
compensate. What is done instead is legitimate: where the role prose underdetermines the semantics,
the partition is frozen FLAT rather than confidently, so the READ decides rather than the recollection.

### P42 — `fpcap` (SCORING) — role: "Capsule/body seam (T3.16)" (URDRCAP1); ambient disclosed: the
    first-person foundation seam (`fpface` T3.15 — this batch's sibling, `gaze` P14 C-R, `stance` P3
    the refuse≠measure residual, `drive` P9 C-REP). Body and history UNREAD.
    partition:        C-R (an admission predicate over a claimed capsule pose central — the gaze/warden
                      shape) · C-EQ (a capsule ≡ body equivalence central — the two representations
                      agreeing) · C-INV (a structural invariant of the seam central) · C-REP (the
                      capsule as a certified REPRESENTATION of the body — the drive shape) · R-M · R-O.
    credences:        author (= B-M′): C-R 30 · C-EQ 25 · C-INV 22 · C-REP 13 · R-M 5 · R-O 5. Frozen
                      flat across the leading three: "seam" names a JOINT, not a semantics, and this
                      layer has produced measure, police and equivalence readings. v_D=0 expected.

### P43 — `fpface` (SCORING) — role: "Exact-integer facing seam (T3.15)" (URDRFACE1); ambient: the same
    foundation seam; `traj` (P31, C-R) recorded that "facing is the direction of the position delta
    when the actor moves", which is secondhand exposure to the CONCEPT and is disclosed as such — the
    module's own rows are UNREAD. Body and history UNREAD.
    partition:        C-EQ (an exact facing IDENTITY central — facing computed two ways agreeing) ·
                      C-R (an admission of a claimed facing central) · C-INV (a structural invariant —
                      facing preserved under some transformation) · C-REP · R-M · R-O.
    credences:        author (= B-M′): C-EQ 32 · C-R 28 · C-INV 20 · C-REP 10 · R-M 5 · R-O 5. "Exact
                      integer" names the ARITHMETIC and P34 already taught that this is weak evidence
                      about semantics — so C-EQ leads only narrowly. v_D=0 expected.

### P44 — `horn` (SCORING) — role: "The Gabriel anchor ladder — rung count conserved, only the pitch
    changes" (URDRHRN1); ambient: the city arc, alongside `disjoint`; the name invokes Gabriel's horn
    (finite volume, infinite surface). The role STATES a conservation outright. Body and history UNREAD.
    partition:        C-INV (a CONSERVATION/structural invariant central — the rung count preserved
                      while pitch varies, exactly as the role states) · C-EQ (an identity between
                      ladders at different pitches central) · C-FLOOR (a soundness-of-absence or a
                      refuted handed-down intuition — the Gabriel paradox shape, where the intuitive
                      quantity misleads) · C-PRICE · R-M · R-O.
    credences:        author (= B-M′): C-INV 40 · C-EQ 25 · C-FLOOR 15 · C-PRICE 10 · R-M 5 · R-O 5.
                      The role states the invariant outright, so C-INV leads — but a module named for a
                      PARADOX is a live C-FLOOR candidate (`ashdepth`/`recirc`/`divergence` all
                      refuted an inherited intuition), which is why C-FLOOR is priced above noise.
                      v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P42 — resolved: **C-EQ** — a containment with a strict witness, not a police predicate
    read:             2026-08-05, the blind READ (run 13). Classified from the LIVE `fpcap*` rows.
    observed:         `fpcap-collision`: **the capsule COVERS its joints**, with the boundary exact and
                      load-bearing — a point just inside the radius is covered and one just outside is
                      not (`fppose`'s exact division-free certificate), and **a shrunk radius uncovers
                      a joint**, the non-vacuity witness. `fpcap-terrain` binds downward (the foot
                      rests at the exact ground · ONE; `stance`'s step law bites at the exact
                      rise > MAX_STEP boundary). `fpcap-pose` binds upward (upright and 90° cardinal
                      pitch EXACT, ~45° mouse-look pitch ROUNDS — the exactness boundary stated) with
                      5/5 typed CAP-REFUSE.
    class:            C-EQ. The author priced C-R 30 · C-EQ 25 — **the leading call missed**. A
                      containment certified with a strictness witness is `interest`'s broad-phase
                      shape (P24, C-EQ), not `warden`'s. The refusals guard the domain, not the answer.
                      v_D = 0.
    unnamed (M-0):    it is a THREE-WAY binding — the capsule answers to the joints below, the terrain
                      beneath and the pose above, and the gate checks all three seams rather than only
                      the one the module is named for.

### P43 — resolved: **C-EQ** — the exact embedding, and its boundary measured
    read:             2026-08-05, the blind READ (run 13). Classified from the LIVE `fpface*` rows.
    observed:         `fpface-exact`: the four cardinal facings lift to their exact direction vectors
                      at **ZERO ulp**, and the cyclic group E→N→W→S→E **permutes EXACTLY** over
                      `drive`'s facing map — the exact embedding, with group structure preserved under
                      the lift. `fpface-boundary` states where exactness ENDS: mouse-look interiors
                      round (deterministically), accumulation drifts a **bounded non-zero ulp count**,
                      and **√2/2 is a trig-free frozen `isqrt`** so no transcendental enters the
                      authority path. 5/5 typed FACE-REFUSE.
    class:            C-EQ; leading credence (32) CORRECT — the batch's only clean leading call. v_D=0.
    counter-instance, recorded: the freeze noted P34 had shown "exact integer" in a role line is weak
                      evidence about semantics, and priced C-EQ only narrowly ahead. Here it DID
                      predict. One joint does not overturn the caution; it is logged as the
                      counter-instance so the caution is held with the right strength.
    unnamed (M-0):    the module MEASURES its own imprecision rather than claiming it away; and the
                      trig-free constant is `cayley`'s cross-placement reasoning again — a seam that
                      avoids sin/cos cross-places with no rounding question to answer.

### P44 — resolved: **C-PRICE** — the exhaustive minimax optimum · RUN 13 CLOSES · the session's worst call
    read:             2026-08-05, the blind READ (run 13). Classified from the LIVE `horn*` rows.
    observed:         `horn-law`: **the geometric ladder is the EXHAUSTIVE MINIMAX OPTIMUM over every
                      integer anchor schedule at each pinned (T,B) — decided, not sampled.** The
                      continuous bound max-ratio−1 is **STRICT on the integer lattice rather than an
                      identity, and the check REFUSED THE EQUALITY AN EARLIER DRAFT ASSERTED** (the
                      gate caught the author's own overclaim); the closed form for the discrete
                      supremum **agrees with an independent brute-force oracle** sweeping every depth;
                      reach is **exponential in slot count** (8 slots reach 64 ticks where a fixed
                      window reaches 8), ladder monotone and covering.
    class:            **C-PRICE, priced FOURTH at 10** against C-INV 40. The session's largest miss.
    THE CAUSE, and it is the failure mode this very freeze named: the index role line — "rung count
                      conserved, only the pitch changes" — is `horn-twist` VERBATIM, and the freeze let
                      it drive C-INV to 40. The `-law` row certifies an OPTIMALITY result.
                      **The tie-break was applied mechanically**: `<module>-law` is central, consistent
                      with `mesh`, `recirc`, `cayley`, `divergence` and `bombtest` — chosen that way
                      precisely so the reading was not selectable after seeing which answer flattered
                      the author. Under the alternative reading (twist central) the call would have
                      been a hit; the rule decided it, not the author.
    the second theorem (horn-twist): under starvation the ladder **TWISTS rather than grows** — rung
                      count B−W CONSERVED, only pitch changes, a flat ribbon becoming a cylinder with
                      the same material and a different rise; reach = W·r^(B−W) exactly and the price
                      is strictly under r−1 **by the same integer-lattice bound, so the twist is PRICED
                      BY THE THEOREM rather than dialled**; REMOVABLE by two independent paths **as
                      equality of ladders, not merely equivalent behaviour**; and DECOUPLED from the
                      view band — a stressed client is bought ZERO extra view-ticks against
                      `clockauth`'s band while the coupling plant buys four, **so the zero is a result
                      and not a reassurance**.
    unnamed (M-0):    the insufficiency proof a THIRD time in two batches (crosswarden, dirward, horn):
                      the fixed-window policy REFUSES starvations of 9, 40 and 300 ticks the ladder
                      anchors — the cliff becomes a slope — while **past the ladder's reach the ladder
                      ALSO refuses, so the boundary is EXTENDED rather than REMOVED**. Also the
                      independent brute-force oracle: the NEUTRAL-RULER pattern's SEVENTH instance.
    census:           run-13 v_D = 0, 0, 0 — RUN 13 CLOSES on a triple zero (the fifth consecutive).
                      Meta ¬M-1: 41 for 41. **Leading calls 1/3 — the worst of the pass.**
    THE OBSERVATION IS NOW RIPE TO FREEZE, and that is the rung's methodological result. The
                      role-prose-over-row failure has now recurred in FIVE consecutive batches (P34,
                      P38, P41, P42, P44). This freeze DECLINED to correct for it — correctly, since
                      under L63 an unfrozen observation has no standing and adjusting credences on it
                      would be tuning. But five instances is exactly the recurrence that licenses a
                      FROZEN FORWARD PREDICTION, the same path the approximation axis took to its mint
                      at checkpoint 4. **Batch 13's freeze is obliged to name it in advance**: for each
                      joint, state whether the role prose and the `-law` row point at DIFFERENT classes
                      and predict the row wins. That is falsifiable, decidable on the next READ, and it
                      converts a recorded complaint into a testable claim.

## BATCH 11 FREEZE — P39 + P40 + P41 (sealed before any READ)

**Why the READ arc and not more Ψ infrastructure — the decision recorded, because it is the project's
own rules deciding it rather than preference.** Three model-laboratory continuations were available
and each is blocked by something the ledger already established:
  * **Q′ (per-axis redundancy)** — would build MORE Ψ apparatus while Ψ is still EXPERIMENTAL and has
    never beaten a seated incumbent on any declared objective. Under L63 that is precisely the
    accumulation the law exists to stop: a diagnostic earns standing before it earns successors.
  * **The unanchored floor** — requires a FRESH SESSION emitting against Q before reading the ledger.
    Structurally unavailable from inside the session that authored Ψ₀, and naming it again does not
    make it reachable.
  * **E / ΔL_model** — has no seated incumbent to beat, and Rung 4 measured G as very nearly
    unpredictable at BATCH granularity (history beats the null by ~2%), so E computed per batch would
    be noise-dominated by construction.
Meanwhile 26 modules carry documentation debt the gate enforces and the D5 ledger still owes. The
model-laboratory arc is PARKED on a named external precondition, not abandoned.

**Selector**: the frozen lex successor reapplied → `crosswarden` → `dirward` → `divergence`. `bench`
remains skipped by the same mechanical eligibility test, re-verified this rung.

**Batch rules**: sole basis B-M′; scoring is the v_D census and the meta only. Run-12 v_D fresh. L61
applied. Meta predicts ¬M-1 on all three (35 for 35).

### P39 — `crosswarden` (SCORING) — role: "Cross-region structural anti-cheat (T3.25)" (URDRWARD2);
    ambient disclosed: the warden family — `warden` (P4, CONFIRMED-MODEL, admission-of-claims with
    typed refusal), `wardhom` (P16, C-EQ, β₀ IS certified F₂-homology β₀ across three languages),
    `hand` (P23, C-INV, cross-region handoff equivalence). Body and history UNREAD. **The family has
    produced all three shapes, so this is genuinely open rather than rhetorically open.**
    partition:        C-R (a cross-region admission/refusal predicate central — the warden pattern
                      extended) · C-EQ (a cross-region ≡ single-region equivalence central — the
                      hand/mesh bit-identity pattern) · C-INV (a structural invariant spanning regions
                      central) · C-AB · R-M · R-O.
    credences:        author (= B-M′): C-R 35 · C-EQ 25 · C-INV 22 · C-AB 8 · R-M 5 · R-O 5. v_D=0
                      expected (the anti-cheat family is long established).

### P40 — `dirward` (SCORING) — role: "Directed-reachability structural anti-cheat (T3.26)"
    (URDRWARD3); ambient disclosed AND load-bearing: `warden`'s own `does_not_show` NAMED this as the
    deferred follow-on ("the undirected (mutual-reachability) boundary, with directed reachability
    deferred"), recorded at P4. Body and history UNREAD.
    partition:        C-R (a directed-reachability admission predicate central) · C-INV (a directed
                      structural invariant central) · C-EQ (directed ≡ undirected on some class, or a
                      stated identity) · C-FLOOR (an honest negative — directed reachability turning
                      out strictly weaker, or catching nothing undirected misses) · R-M · R-O.
    credences:        author (= B-M′): C-R 38 · C-INV 25 · C-EQ 18 · C-FLOOR 9 · R-M 5 · R-O 5.
                      C-FLOOR is the live tail risk: a follow-on that closes a deferred boundary
                      sometimes finds the boundary did not need closing (the `recirc` shape). v_D=0.

### P41 — `divergence` (SCORING) — role: "The quantization defect in CELLS (S2) — the largest
    connected RUN, never a rate" (URDRDVG1); ambient: the city arc (`voxlat` S1, `provbind` S3,
    `geoquorum` S4 — P21 C-SPLIT). **EXPOSURE DISCLOSED**: `hainuwele/README.md`'s weak-spots section,
    read earlier this session, states this module's DATA BOUNDARY ("the number in the repo bounds a
    synthetic wall; it is not a prediction about a real one"). That is a `does_not_show` statement,
    NOT the central law, so the joint stays SCORING — unlike P33 (`bombtest`), where the README stated
    the finding itself. The distinction is recorded so the scoring/non-scoring line stays auditable
    rather than discretionary. Body and history UNREAD.
    partition:        C-PRICE (a defect MAGNITUDE/measure central — the largest connected run as a
                      priced quantity) · C-FLOOR (a handed-down metric REFUTED by measurement — "never
                      a rate" as the load-bearing negative, the `ashdepth`/`recirc` shape) · C-INV (a
                      structural invariant of the quantization central) · C-EQ · R-M · R-O.
    credences:        author (= B-M′): C-PRICE 30 · C-FLOOR 28 · C-INV 18 · C-EQ 12 · R-M 6 · R-O 6.
                      Frozen near-flat across the leading two: the role's "never a rate" reads as a
                      refutation of a rate metric (C-FLOOR), but the module's job is to SUPPLY a
                      measure (C-PRICE), and the arc has resolved both shapes. v_D=0 expected.
    witness:          the git commit introducing these rows — dated before any of the three is read.

### P39 — resolved: **C-R** — police at the seam, with an INSUFFICIENCY PROOF as the instrument
    read:             2026-08-05, the blind READ (run 12). Classified from the LIVE `crosswarden*` rows.
    observed:         `crosswarden-insufficient` is the distinguishing row: **a shard-local warden
                      ADMITS both boundary exploits that crosswarden refuses** — the module certifies
                      the NECESSITY OF ITS OWN EXISTENCE by measurement rather than by argument. A
                      desynced seam is WARD-SEAM; 4/4 typed WARD-REFUSE sub-codes.
                      `crosswarden-kinematic`: an honest seam crossing admits, a through-wall sprint is
                      WARD-TUNNEL, and an honest handoff admits AND EQUALS THE MERGED GLIDE (binding
                      Stage D to Stage E). `crosswarden-topological`: merge == `hand.merge`, β₀ RISES
                      across the merge (B's wall becomes visible only in the merged field), so a
                      beyond-wall position is WARD-UNREACH from the merged field ALONE.
    class:            C-R; leading credence (35) CORRECT. The family had produced all three shapes
                      (warden C-R, wardhom C-EQ, hand C-INV), so the joint was genuinely open. v_D = 0.
    unnamed (M-0):    THE INSUFFICIENCY PROOF — running the WEAKER predecessor against the same
                      exploits and showing it admit them, converting "this rung is necessary" from a
                      design claim into a measured one; and the β₀-rises-across-merge detail, where the
                      topological evidence for the wall exists in NEITHER region alone.

### P40 — resolved: **C-R** — the deferred boundary closed; refusal gains a sub-reason
    read:             2026-08-05, the blind READ (run 12). Classified from the LIVE `dirward*` rows.
    observed:         `dirward-insufficient`: the undirected warden fails in BOTH directions at once —
                      it **FALSE-REFUSES the legal descent** (rejecting a legitimate move, worse than a
                      miss) and returns **one WARD-UNREACH for both a one-way cliff and a genuine
                      wall**. `dirward` admits the descent and SEPARATES WARD-ONEWAY from WARD-UNREACH.
                      `dirward-admission` holds the law (descent admits, climb-back is WARD-ONEWAY, a
                      wall is WARD-UNREACH, an honest glide descent admits kinematically).
                      `dirward-asymmetry` supplies the structure: directed reach is genuinely
                      asymmetric on the cliff and **collapses to 0 with num_scc == betti0 on FLAT
                      terrain** — the refinement reduces exactly to its predecessor where terrain is
                      symmetric.
    class:            C-R; leading credence (38) CORRECT. The C-FLOOR tail risk (a deferred boundary
                      that turns out not to need closing) did NOT fire — it needed closing. v_D = 0.
    axis sighting, NOT a mint: WARD-ONEWAY vs WARD-UNREACH is the DISCRIMINABILITY-OF-REFUSAL shape
                      `geoquorum` (P21) recorded as a candidate to WATCH — a typed sub-reason turning
                      one verdict into two, exactly as UNAVAILABLE vs FAILED did. **Second sighting,
                      and it may not mint**: the axis was NOT named in this joint's frozen partition,
                      so under L3 a post-hoc recurrence cannot promote it. A mint requires a FUTURE
                      FROZEN prediction naming the axis in advance — the bar the approximation axis
                      cleared at checkpoint 4. Recorded so the temptation is visible and refused.
    unnamed (M-0):    the insufficiency proof AGAIN (second in two rungs — a family habit, not a
                      flourish); and the flat-terrain collapse, which is `clslo`'s reduction move.

### P41 — resolved: **C-FLOOR** — the rate metric REFUTED · RUN 12 CLOSES
    read:             2026-08-05, the blind READ (run 12). Classified from the LIVE `divergence*` rows.
    observed:         `divergence-law`: the quantization defect is measured in CELLS and specifically
                      as the **LARGEST CONNECTED RUN** of flipped cells, **because an adversary does
                      not attack the mean** — two perturbations with the IDENTICAL RATE 2/35 have runs
                      1 and 2, and only one breaches the wall. `divergence-selftest` states the
                      refutation as a plant: **the rate plant assigns the SAME defect to a perturbation
                      that leaves the wall standing and one that opens it**. It also records why the
                      maximum is ENUMERATED rather than sampled — a sampled MEAN run is strictly below
                      the attained worst case.
    class:            C-FLOOR. The author priced C-PRICE 30 · C-FLOOR 28 — **a two-point miss**. The
                      module SUPPLIES a measure, but what the gate CERTIFIES is that the intuitive
                      measure is WRONG; the negative is the load-bearing content. v_D = 0.
    pattern:          the `ashdepth` shape's THIRD carrier (ashdepth: a void is sound, the handed-down
                      guard refuted; recirc: there is no loop, and closing it would harm; divergence:
                      the rate metric cannot distinguish a breach from a non-breach). Measurement
                      overturning an inherited design, three times.
    unnamed (M-0):    enumerate-don't-sample as a family habit — `voxlat` decided its overflow bound
                      exhaustively, `cayley` swept every configuration, `divergence` enumerates the
                      maximum. L20 (sample ≠ universal) turned into code three times.
    census:           run-12 v_D = 0, 0, 0 — RUN 12 CLOSES on a triple zero. Meta ¬M-1: 38 for 38.
                      Leading calls 2/3 — the SECOND consecutive batch at 2/3 with the miss being a
                      TWO-POINT one (P38 C-INV/C-EQ 32-30, P41 C-PRICE/C-FLOOR 30-28). Both misses
                      came from weighing "the module's JOB" over "what the ROW certifies", which is
                      also P34's error. Three instances in four batches. NOT minted and NOT acted on:
                      no frozen prediction has named this failure mode in advance, so under L3 and L63
                      it is a recorded observation with a decidable forward test, nothing more.

## RUNG 5 FREEZE — the W3 IDENTIFIABILITY PROBE (spec sealed before the ablated operator is emitted)

**The insight that unblocks this, stated first because it is the whole reason the rung is possible.**
ε_author = 2800 is a LOWER BOUND on emission noise (ε_true ≥ 2800). That makes it **useless in one
direction and valid in the other**:

    d > 2800  ⇒  NOTHING follows. ε_true may exceed d, so apparent movement may still be noise.
                 (This is why Ψ₁'s 3000 was declared substantively uninterpretable.)
    d ≤ 2800  ⇒  INDISTINGUISHABLE, and this IS licensed: d ≤ 2800 ≤ ε_true, so the difference is
                 inside the instrument's own error however the floor is later tightened.

W3 asks whether distinct live organizations can induce identical predictive operators over a finite Q.
Supporting it requires exhibiting a pair that is INDISTINGUISHABLE — **exactly the direction the
anchored floor licenses.** No better floor is needed for this one question.

**THE TWO CONFIGURATIONS.** The contrast must be a real structural difference, not one manufactured to
match. It is an **ABLATION**: the seated basis with the scheduling axis removed — i.e. B-M′ exactly as
it stood at checkpoint 6, before P27 minted that axis. That is a configuration this engine genuinely
occupied, so the difference is historical fact rather than invention.

    S_full   = B-M′ as seated now (input × semantics + the approximation and scheduling axes)  → Ψ₁
    S_ablate = the same basis WITHOUT the scheduling axis (its checkpoint-6 form)              → Ψ_abl

**Why an ablation and not the retired challenger B-A″.** L63's no-zombies clause forbids reasoning
from a retired diagnostic as explanatory evidence. Emitting Ψ under B-A″ would sail close to that even
if framed as structural rather than evidential, so the contrast is drawn against a PRIOR FORM OF THE
SEATED BASIS instead. The rule is respected in substance, not just in letter.

    FROZEN READING RULE (one-sided by construction, and labelled so):
      * ‖Ψ_abl − Ψ₁‖₁ ≤ 2800 → **W3 SUPPORTED**: a real structural difference that Q cannot see. The
        scheduling axis would then be carrying organizational structure with NO behavioural content
        over this corpus — v_D's fate one level up, and a result about the REPRESENTATION.
      * ‖Ψ_abl − Ψ₁‖₁ > 2800 → **INCONCLUSIVE**, never "distinguishable". Reported with the per-probe
        pattern as description only. Q's resolving power on this axis would be UNREFUTED, not shown.
    FROZEN DIRECTIONAL PREDICTION (falsifiable, and the author expects it to fire): QP05 — the cadence
    probe, "work admitted in a certified deadline order with a proven bound on the wait" — is the only
    probe squarely on the scheduling seam, so if the axis carries behavioural content QP05 must move
    MOST, and by ≥ 800. If the axis is behaviourally inert, QP05 moves like the others.
    AUTHOR'S CALL, frozen: total > 2800 (INCONCLUSIVE) with QP05 moving most. Recorded so the rung can
    embarrass the author rather than confirm him.

    CONTAMINATION NOTE: the ablated emission is authored by someone who knows Ψ₁ and knows what the
    scheduling axis is for. Anchoring applies here exactly as it did to Ψ₀′, and it biases the
    difference DOWNWARD — i.e. TOWARD the "supported" verdict. That cuts against the author's own
    frozen call, so the bias and the prediction point in opposite directions, which is the most
    honest configuration available in a single-author setting. It is disclosed, not neutralised.

### RUNG 5 RESOLVED — W3 not supported here, and the corpus turns out ONE-PROBE FRAGILE

    ‖Ψ_abl − Ψ₁‖₁ = 5200        floor ε = 2800        VERDICT: **INCONCLUSIVE**

**Both frozen calls fired.** The author's call (total > 2800, hence inconclusive) and the directional
prediction (QP05 moves most, by ≥ 800) were both correct — QP05 moved **3800**, an order above every
other probe. So the scheduling axis is NOT shown invisible to Q: W3 gains no support from this pair,
and the ablation is *not* licensed as "distinguishable" either. The one-sided rule was honoured in
both directions; the rung produces no identifiability claim at all, which is the correct outcome when
a difference lands on the unlicensed side of the floor.

**THE ACTUAL FINDING, which is about the INSTRUMENT rather than the engine.** QP05 alone carries
**73%** of the total difference (3800 of 5200). So the leave-one-out check was run, and it is decisive:

    probes whose REMOVAL flips the verdict to SUPPORTED: ['QP05']    → the verdict is ONE-PROBE FRAGILE

Dropping the single probe on the scheduling seam leaves 1400 — comfortably *under* the floor — and the
ablation would then read as INDISTINGUISHABLE. **Q's ability to resolve the scheduling axis rests
entirely on one probe.** That is a corpus-design defect, not an engine finding, and it generalizes:
a probe corpus needs REDUNDANCY PER AXIS, or every identifiability verdict it issues is hostage to a
single row. The ten probes were each written to sit on a distinct seam (L61: a probe everyone answers
identically detects nothing), and that very distinctness is what left each axis with a single witness.
The two design goals — discriminating breadth and per-axis redundancy — pull against each other, and
Q was built for the first without noticing the second.

**Consequence, recorded and NOT acted on speculatively (L58).** Q is FROZEN and stays frozen; a corpus
edited in response to a verdict it produced is tunable to the answer, which is the trap the freeze
exists to prevent. The honest response is a SUCCESSOR corpus Q′ designed with ≥ 2 probes per named
axis, frozen before use, with Q retained so the two can be compared. Q′ is named here and unbuilt.

**A note on the contamination that did NOT rescue the author.** The freeze disclosed that anchoring
biases the ablated emission DOWNWARD, i.e. toward the "supported" verdict, and against the author's
own frozen call. The result went the author's way despite that bias — which is the strongest form
available in a single-author setting, and it is why the disclosure was worth making in advance rather
than after.

### Ψ₁ — the first post-work drift, read against the floor declared in advance

    ‖Ψ₁ − Ψ₀‖₁ = 3000        floor ε_author = 2800        ratio 1.07

**The frozen rule says this clears the bar. The honest reading says it is not a signal, and both are
recorded.** `drift_is_interpretable("1","0")` → True by the letter of the rule declared in the
batch-10 freeze. But ε_author is a **LOWER BOUND** (Rung 4's control was anchored, which pushes the
measured floor DOWN), so the true floor is very likely above 2800 — and a drift exceeding a
lower-bound floor by 7% is exactly the region where the instrument cannot distinguish movement from
its own error. **Verdict: technically above the floor, substantively indistinguishable from noise.**
Nothing is concluded about the operator having moved. This is the intended behaviour of the rule, not
a disappointment: the alternative — reporting 3000 as "measurable drift after batch 10" — is precisely
what the floor exists to prevent.

**THE CONTROL EARNED ITS KEEP IMMEDIATELY, and this is the rung's real result.** QP06's leading class
flipped C-REP → C-R between Ψ₀ and Ψ₁. Without Rung 4 that is a headline: *the engine's disposition
shifted on the representation-vs-police probe after reading batch 10*. With Rung 4 it is nothing —
**QP06 flipped identically in the repeatability control**, under zero intervening work. The flip is a
property of that probe's 200-point margin, not of anything batch 10 did. A control that disqualifies a
finding one rung after being built is a control doing its job.

**Per-probe**: QP08 800 (the braid/interleaving probe, where `commuteprop`'s oracle-verified diamond is
the closest live analogue), QP01/QP02/QP05/QP09 400 each, QP04/QP06/QP07 200, **QP03 and QP10 exactly
0**. Two probes did not move at all, which is itself a small non-vacuity check on the corpus: the
emission is not uniformly jittering everything.

**What would make the next reading decisive**: an unanchored floor from a FRESH SESSION (named at Rung
4, still unbuilt), or a drift large enough that no plausible tightening of the floor could swallow it.
Neither exists yet, so Ψ stays EXPERIMENTAL under L63 with its floor attached.

## RUNG 4 — the REPEATABILITY CONTROL, and the MDL re-score

Two results, one of which corrects a quantity this ledger had already frozen. Witnesses: `probes.py`
(the control) and `multinull.py` (the re-score), both rerun byte-identical.

### The noise floor: ε_author = 2800, and it is INFORMATIVE

Standard measurement practice requires a repeatability coefficient before any observed change can be
called real: **CR = 2.77 × SEM**, and a difference below it "might simply be due to the inherent
mechanical inaccuracy of the tool." Ψ is author-emitted, therefore it has measurement error, and until
that floor was measured **every drift number was uninterpretable no matter how many batches
accumulated** — which is why Batch 10 was not the right next move.

    eps_author = ||Ψ_0' − Ψ_0||₁ = 2800   over a corpus carrying 100000 total mass  (2.8%)

**The confound was frozen before the number.** The control was emitted in the SAME session that
produced Ψ₀, so the originals were visible; anchoring is unavoidable and pushes the difference DOWN.
The frozen reading rule was therefore asymmetric: **ε > 0 is INFORMATIVE** (disagreement that survives
anchoring is real emission noise, hence a genuine lower bound), while **ε = 0 would have been
UNINFORMATIVE** (a zero is exactly what perfect anchoring produces). The result is ε = 2800 > 0, so
the informative branch fired and the floor is a real lower bound.

**THE SHARP FINDING — a leading-class FLIP inside the noise.** QP06 (the echo-transcript probe,
representation vs police) led **C-REP at 3200 in Ψ₀ and C-R in Ψ₀′**, its margin having been the
corpus's narrowest at 200. So on a low-margin probe **the leading class is not stable under
re-emission**. Recorded as measured. The tempting connection — that batches 8–9's four leading-class
misses were concentrated where the basis was near-tied — is POST HOC and unfrozen, and under L63 has
no standing; it is an observation with a decidable forward test, not a finding.

**Deliberately NOT inflated to a CR.** The 2.77 multiplier presumes an SEM estimated from many
independent pairs; one anchored pair supports no such estimate, so the smallest detectable drift is
recorded as the raw ε. Manufacturing a coefficient here would fabricate precision the control cannot
supply.

**The kill condition is NOT YET EVALUABLE, and that is recorded rather than resolved favourably.**
Retiring Ψ requires knowing ε is large *relative to the dispositional shifts Ψ must detect* — and that
scale is unknown until at least two genuine (post-work) emissions exist. Ψ is neither cleared nor
killed; it stays EXPERIMENTAL with a floor attached.

**The valid experiment is named, not claimed.** An unanchored control requires a FRESH SESSION with no
access to Ψ₀ — emitted before the ledger is read — or emission by a different agent. Until then 2800
is a lower bound and is labelled one.

### The MDL re-score: the seated verdict is NOT rule-dependent

The frozen E = ΔG/(ΔC+ΔR) was malformed twice: a RATIO where MDL's tradeoff is an additive code
length, and a quotient of INCOMMENSURABLE units (Brier points over structural counts), diverging when
a batch makes no structural change. MDL requires both terms in the same unit, and log loss IS code
length by Kraft–McMillan. So the corpus was re-scored under log loss:

    TOTAL incumbent 40535 mb   ·   null 61178 mb   ·   Δ_null = +20643 millibits  (>0)

**It agrees with the Brier verdict** (`logloss_agrees_with_brier()` → True). This matters more than
the number: had the verdict reversed, checkpoint 9's conclusion would have been an artifact of the
scoring rule and would have needed re-grading. It did not. The incumbent-beats-null finding survives a
change of proper scoring rule, which is a robustness check the original measurement never had.

    FROZEN E SPEC (form and units fixed; one term still open):
        E = ΔL_data − λ·ΔL_model,   both in millibits,   **λ = 1** (the canonical two-part code).
    λ is fixed at 1 deliberately: a free λ is a knob that could be tuned until any structural change
    looked efficient, which is the discretion the ratio form already smuggled in. ΔL_model — the code
    length of a structural modification — is the OPEN term, and it must be a real code length (bits to
    DESCRIBE the change), never a count of edits wearing a bit's clothing. E is not computed here and
    is EXPERIMENTAL under L63.

**A corpus note, because the witnesses recompute live.** Batch 9 added P34/P35, so the scoring corpus
is now **24 joints** and a fresh run reports Δ_null = +569 905 364 (Brier). Checkpoint 9's recorded
+553 208 846 stands as the measurement **as of its date over 22 joints** — the ledger records
measurements at their date; the scripts report the live corpus. P33 is now named explicitly in
`NON_SCORING` so its exclusion is asserted by rule rather than resting on its freeze happening to
carry no credence block.

## INSTRUMENT REGISTRY — every diagnostic's status under L63 (empirical admissibility)

L63 is worthless as a declaration; it is only real if every instrument in the engine carries a status
and the statuses were assigned by measurement. Each row registers ONE objective, its scoring rule, the
incumbent it had to beat, and what happened. **EXPERIMENTAL** may be computed and reported but NOT
reasoned from; **SEATED** is the current best on its objective; **RETIRED** is irreversible.

| instrument | objective | scoring · incumbent | status | evidence |
|---|---|---|---|---|
| B-M′ (the basis) | joint-class prediction | Brier · rolling marginal null | **SEATED** | Δ_null = +553 208 846 over 22 joints; 15 won / 7 lost; leading 15/22 vs 4/22 (ck 9) |
| rolling marginal null | — (the floor) | Brier · — | **SEATED** (as the bar) | seated by construction per L62; it is what everything must beat |
| `v_D` (new-family census) | predict batch gain G | LOBO MAE · null (mean) | **RETIRED** from predictive use | 19 036 400 vs null 17 854 727 — worse than the mean (ck 10) |
| history predictor G_{b−1} | predict batch gain G | LOBO MAE · null | **SEATED** (weakly) | 17 498 120 vs 17 854 727 — beats the null by ~2%, so it holds the seat |
| combined (v_D + history) | predict batch gain G | LOBO MAE · history | **RETIRED** | 28 959 563 — the overfit signature at n = 7 |
| B-C1 topological challenger | CONJ/SINGLE class form | accuracy · constant predictor | **RETIRED** | 10/27 vs 16/27 (ck 8) |
| B-C2 phase-position challenger | CONJ/SINGLE class form | accuracy · constant predictor | **RETIRED** | 15/27 vs 16/27 (ck 8) |
| margin (1st−2nd credence) | predict a leading-class miss | LOJO Brier · seated null | **RETIRED** | 2626 vs 2380, and fails DIRECTIONALLY (883 hits vs 928 misses) — Rung 2 |
| top-mass | predict a leading-class miss | LOJO Brier · seated null | **RETIRED** | 2560 vs 2380 — Rung 2 |
| class count | predict a leading-class miss | LOJO Brier · seated null | **RETIRED** | 2663 vs 2380 — Rung 2 |
| Γ (synthesis operator) | generate a live challenger | ck-9 frozen gate · — | **RETIRED before construction** | its frozen precondition (a miss-predictor beating the null) failed at Rung 2 |
| Γ coupling/interface table | predict emergence events | — · — (never set) | **RETIRED** | suspended at ck 3, starved, one directional call wrong — the L63 archetype |
| Ω (specified orbit scalar) | certify state recurrence | — · — | **RETIRED (impossible)** | W2/RST: contains a monotone coordinate; Ω ≥ 3(ℓ+1) > 0 always |
| Ω_live (live-quotient) | certify state recurrence | — · — | **EXPERIMENTAL** | non-degenerate (plant: 0 vs 30) but never shown INFORMATIVE |
| Ψ (the operator over Q) | observational quotient | — · — | **EXPERIMENTAL** | Q frozen + Ψ₀ emitted (Rung 3); author-emitted, so DECLARED not measured |
| Q (the probe corpus) | resolve named axes | leave-one-out · — | **EXPERIMENTAL, defect recorded** | Rung 5: ONE-PROBE FRAGILE — removing QP05 flips the W3 verdict; needs ≥2 probes per axis |
| FP-ROW (role vs row) | predict the reader's own miss | resolution class · role-reading | **RETIRED** | batch 14: directional claim FALSIFIED at P48 (role won); 2 ROW · 1 ROLE · 1 NEITHER · 1 SAME |
| the `-law` fallback ladder | select the central row | — · — | **EXPERIMENTAL, defect recorded** | P48: excludes by NAME (`:scenes`) where it meant to exclude by ROLE; selection was load-bearing |
| Ψ drift Δ_Ψ(t,k) | detect operator evolution | — · — | **EXPERIMENTAL** | floor MEASURED at Rung 4: ε_author = 2800 (lower bound, anchored). Drift ≤ 2800 is uninterpretable |
| E (resolution efficiency) | value structural change | log loss (millibits) · — | **EXPERIMENTAL** | form frozen as ΔL_data − λ·ΔL_model, λ=1; ΔL_model still undefined, so uncomputed |
| log loss (MDL rescore) | joint-class prediction | log loss · rolling marginal null | **SEATED** (co-rule) | Δ_null = +20643 mb; AGREES with Brier, so the verdict is not rule-dependent |
| attractor radius r_t | detect predictive-regime return | — · — | **EXPERIMENTAL** | domain now exists; needs ≥ 3 emissions for a meaningful centroid |
| resolution efficiency E | value structural change | — · — | **EXPERIMENTAL** | unbuilt; denominator not yet frozen |

**Two readings this table forces, both uncomfortable and both recorded.** First, the engine's own
convergence census (`v_D`) is RETIRED from predictive use while remaining structurally informative —
so every past sentence of the form "three triple-zero runs evidence convergence" was reasoning from an
unseated diagnostic, and stands only as a STRUCTURAL claim, never a predictive one. Second, of
seventeen registered instruments only **three are seated**, one of them the null itself and one
beating it by ~2%. That is the honest inventory of what this engine has actually earned, and it is
much smaller than the volume of prose about it would suggest — which is precisely the accumulation
L63 exists to stop.

**Zombie check (L63's no-zombies clause), applied to this ledger's own history:** retired instruments
appear above as documented negative results and may not be cited as explanatory evidence going
forward. Where earlier checkpoints reasoned from `v_D` or the Γ table, those inferences are hereby
downgraded to structural observations; they are not retracted (the record is append-only) and they are
not load-bearing.

## THEOREM CANDIDATES — stated, with executable witnesses

### W2 — the REPRESENTATION SEPARATION THEOREM (RST) (a NEGATIVE theorem; witness: `orbitprobe.py`)
    general form:     If a coordinate is MONOTONE UNDER THE TRANSITION RELATION, then no metric
                      including that coordinate with positive weight can represent operational
                      recurrence. Append-only is the special case that occurs here; the proof only
                      needs monotonicity, so the theorem covers any coordinate that cannot decrease
                      (accumulated evidence, minted lineage, spent budget, elapsed rungs).
    corollary (the operational content): every variable partitions into exactly one class —
                      LIVE STATE (reversible → admissible for operational distance), BEHAVIOURAL
                      (observable → admissible for predictive equivalence), LEDGER/HISTORY (monotone →
                      PROVENANCE ONLY). Mixing classes inside one metric is the fatal defect. This is
                      stronger than "avoid append-only coordinates" because it says why, and says
                      what each coordinate IS FOR.
    statement (the instance proved here): Let d be a recurrence metric over engine states whose
                      coordinates include a STRICTLY APPEND-ONLY component c (c_j ⊆ c_t for all
                      j < t, with |c_t| strictly increasing in t) carried with positive weight w.
                      Then for every lookback exclusion ℓ ≥ 0:
                          Ω_t = min_{j < t−ℓ} d(S_t, S_j)  ≥  w · ( |c_t| − |c_{t−ℓ−1}| )  >  0,
                      and since |c_t| − |c_j| is strictly increasing in (t − j), the minimum is
                      attained at the MOST RECENT admissible j. Therefore Ω_t can never certify
                      return (it is never 0) and is monotone in ELAPSED HISTORY rather than in
                      organizational similarity. **A recurrence metric containing an append-only
                      coordinate is a clock.**
    corollary:        Recurrence must be defined on the LIVE quotient — S_live = (active bases,
                      current predictor, active axes) — with the ledger (𝓡, 𝓜) retained as an
                      immutable PATH LABEL rather than a state coordinate. Lineage is not state.
    measured:         the plant, both directions. Two synthetic histories with identical live
                      configuration and ledger lengths 0 vs 30: the specified metric returns 30, the
                      live-quotient metric returns 0. `append_only_plant_bites()` → True. Also
                      instantiated on the real engine: with 3 joints appended per batch, the bound
                      gives Ω_t ≥ 3(ℓ+1) — 6 at ℓ=1 — matching the degeneracy observed.
                      MEASURED, deterministic, rerun byte-identical:
                      PYTHONHASHSEED=0 python3 exe_epistemics/orbitprobe.py
    does_not_show:    that the LIVE-quotient metric is USEFUL — only that it is not impossible; a
                      metric can be non-degenerate and still carry no information, which is the
                      separate prospective test frozen at checkpoint 10. Nor does it show that
                      append-only ledgers are a design error: the append-only property is what makes
                      L2/L59 enforceable, and the theorem says only that such a coordinate may not
                      appear inside a RECURRENCE metric.
    promotion rule:   W2 stays a stated theorem with a witness, NOT a gate row, until a live orbit
                      instrument exists for it to constrain (L58; the W1 precedent). It is a
                      NEGATIVE result, and negative results are recorded, never built upon
                      speculatively.

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


## RUNG 9 — the ADJUDICATOR was naming the wrong winner, and the defect was invisible until the answer changed (2026-08-05)

WHAT HAPPENED. A theoretical review proposed eleven candidate extensions to the discovery engine
(basis lattices, a detector interaction algebra, seam hypergraphs, fork ensembles, minimal-witness
search, detector mutation, an evidence simplicial complex, detector Shapley values, a counterfactual
repository generator, an architecture phase diagram, and combinatorial shadowing). Before evaluating
any of them the existing instruments were RE-RUN against the grown corpus, on the principle that a
proposal to extend an instrument is worth nothing until the instrument is known to be sound. It was
not.

    prediction_residuals.joint_level_beats_null:
        best = min(k for k in res if k != "null")        # WRONG: lexicographic min of the KEY NAMES

The line answers the question L63 exists to adjudicate -- WHICH diagnostic beat the seated
incumbent -- and it answered it by alphabetical order. It returns "margin" for every corpus that has
ever existed or ever could.

WHY NO RUN COULD HAVE CAUGHT IT. The value was CONDITIONALLY DEAD. While no covariate beat the null,
`beats` was False and nothing consulted `best`; a wrong label with no reader has no observable
consequence, so every previous green run is silent evidence. The defect became load-bearing at the
FIRST run that flipped `beats` to True -- and that same run reported the winner wrongly. The
instrument went from correct to incorrect with no code change, purely because the data moved.

    n = 33 scoring joints (was 22 at Rung 8)
    null 2539   margin 2651   nclass 2586   topmass 2433        (LOJO Brier on the miss event, /10000)

    reported by the defective line : margin   -- LOSES to the null by 112
    true argmin                    : topmass  -- BEATS the null by 106

The mis-naming was maximally unlucky: it crowned the one covariate whose standing hypothesis this
corpus had already embarrassed, in the run that first produced a genuine winner.

REPAIRED, with the falsifier the line never had. `best` is now `min(others, key=lambda k: (res[k],
k))` -- argmin by score, ties broken lexicographically so the answer is deterministic. A red-first
plant (`winner_is_named_by_score`) supplies a synthetic result whose alphabetically-first covariate
is the WORST and demands the reported winner be the lowest-scoring one; the pre-repair implementation
returns "aaa" and fails it. Rerun byte-identical under PYTHONHASHSEED=0.

THE L63 CONSEQUENCE, stated so it is NOT over-read. `topmass` -- the probability assigned to the
leading class -- now holds ONE out-of-sample win over the seated null, the first any joint-level
covariate has recorded. Under L63 that is NOT STANDING: the law requires REPEATED and PREREGISTERED
improvement over the seated incumbent, and one win on a retrospective corpus is a single
observation. `topmass` therefore stays EXPERIMENTAL -- computable and reportable, NOT reasonable-from
-- and the INSTRUMENT REGISTRY entry that says so is unchanged by this rung. Rung 2's recorded
finding ("the residual is a CONSTANT, not a SIGNAL") was true at n=22 and is NOT retro-edited; what
is added is that it did not survive to n=33, which is exactly what an append-only ledger is for.
Note also that the "low margin => miss" hypothesis is now DIRECTIONALLY correct (mean margin: hits
967, misses 800) while `margin` remains a WORSE predictor than the constant null -- direction is not
prediction, and a corpus can supply the first without the second.

THE LAW CANDIDATE, tracked and NOT MINTED. The shape -- *an output consulted only under a condition
that has never held is untested by every run made so far, and the run that first makes it
load-bearing is also the first run that can be wrong* -- is distinct from L61 (empty DATA read as a
confirmation), from L62 (a tournament with no baseline) and from L23 (a checker that cannot fail):
here the check was sound, the data non-empty, and the tournament properly seated. What was wrong was
a LABEL nobody had yet had reason to read. It has ONE carrier. Under L3 that is not a lesson, and
minting it on a single instance is the precise error this rung was created by. It is recorded as a
CANDIDATE and earns L-status only on an independently discovered second carrier -- and if none
appears, its absence is the result. `vacuous != correct`.

THE ELEVEN PROPOSALS, ruled on by the same law they would be judged under. L63: architectural
concepts are downstream of empirical winners, never upstream. Four of the eleven are separable:
  * BASIS LATTICE -- ADMISSIBLE, and the only one that needs no new epistemics. It is not a new
    concept requiring standing; it is a LARGER TOURNAMENT in a format that already has a seated
    incumbent (B-M') and a declared objective (log loss / integer Brier against the rolling null).
    Its one constraint is decisive: the 63 joints are RESOLVED, so scoring new bases on them is
    retrodiction. The lattice can earn standing only on joints not yet read -- so it must be FROZEN
    NOW and scored on the successor corpus, which makes it a natural fit for the portability rung
    rather than a competitor with it.
  * COMBINATORIAL SHADOWING -- cheapest, and the substrate already exists: the shadow (classes
    PRICED but never OBSERVED) is the complement of the PARTITION error type already computed here,
    over a partition L60 guarantees is exhaustive. It can be run on data in hand and contaminates
    nothing. It buys a null cheaply in the S11 tradition; it cannot earn standing retrospectively.
  * DETECTOR INTERACTION ALGEBRA -- the MEASUREMENT is admissible, the ALGEBRA is not yet.
    `D : Repository -> Evidence` does not compose with itself: `D_j . D_i` is a type error as
    stated, since Evidence is not a Repository. What is well-typed is a FACTORIAL design over joint
    application (redundancy, subsumption, and interaction of detectors applied together), which is a
    contingency table, not an algebra. Calling it an algebra before a composition law is exhibited
    is L21 (wrong units) dressed as elegance (L22).
  * FORK ENSEMBLE -- real, and BLOCKED on the same thing as the unanchored Psi floor. Independence
    cannot be manufactured by the author: five forks made here are five anchored controls, exactly
    as a second same-session emission was. It becomes available only for repositories with
    genuinely independent fork histories, i.e. AFTER portability, never before it.
The remaining seven are not refused, they are UNRANKED: each would add another EXPERIMENTAL object
to a registry in which zero challengers currently hold standing, and L63 exists because Gamma was
seated by adoption rather than evidence and survived three rungs past its usefulness.

GRADE. MEASURED: the defect (exhibited, with the pre-repair line returning "margin" on every input),
the repair, the red-first plant, the LOJO table at n=33, determinism. DECLARED: that the eleven
proposals divide as above -- a reading of their type structure, not a measurement of their value.
does_not_show: that `topmass` predicts anything (one retrospective win); that the other seven
proposals are bad (they are unranked, which is not a verdict); that no OTHER conditionally-dead
output exists in the arc -- one was found by running one instrument, and `sample != universal`.

FALSIFIER. `winner_is_named_by_score()` in `prediction_residuals.py`: it plants a result whose
alphabetically-first covariate scores worst and demands the reported winner be the argmin by score.
If that plant ever passes with the naming line restored to `min(k for k in res ...)`, the falsifier
is vacuous and this rung's central claim dies with it.


## RUNG 10 — SELECTION made explicit, and the winner made VERIFIABLE (2026-08-05)

THE LICENCE, stated first because it is the only reason this rung is not an L63 violation. A review
of Rung 9 proposed six extensions built on one observation: between `tournament` and `winner` there
was always a FUNCTIONAL, and it was never an object. The observation is correct. It is also, unlike
the eleven proposals ruled on at Rung 9, NOT A NEW CLAIM -- and that distinction is doing all the
work here:

    L63 governs objects that CLAIM TO EXPLAIN OR PREDICT. A selector explains nothing and predicts
    nothing. It was ALREADY OPERATING, in every tournament this arc has ever run, as an unnamed
    call to `min`. Making an already-operating mechanism EXPLICIT adds no claim; it makes an
    existing one checkable. That is apparatus in the L5/L15 sense, and the bar apparatus must clear
    is that it BITES, never that it wins.

Rung 9 is the proof the mechanism was operating and unaudited: `argmin(score)` was silently
substituted by `argmin(name)` and there was nothing to diff, nothing to hash, nothing to audit.

BUILT (`selection.py`, stdlib-only, off-gate, 1.2s, rerun byte-identical):
  * THE SELECTOR AS DATA. `objective`, `metric`, `tie_break`, `exclude`, `baseline` -- every field a
    decision that was previously implicit in a call to `min`. A change of direction is now a change
    of DATA and appears in a diff. `metric` names what is being minimised, so a selector cannot be
    silently reused against a score it was not written for.
  * THE CERTIFICATE. The winner is never returned alone: it arrives with the winning score, the
    closest competitor, the baseline it must also beat, the declared field, and the selector used.
  * VERIFICATION BY PROPERTY, NOT BY PROCEDURE -- and this is the load-bearing design choice. L23 is
    explicit that two computations agreeing is a measurement only when they share no primitive; one
    computation restated is a definition. So `verify` does NOT call `select` again and compare. It
    checks the DEFINING PROPERTY of an argmin directly: the winner lies in the declared field, no
    candidate scores strictly better, and among ties the winner is lexicographically first. **A
    certificate that passes is correct even if `select` is wrong** -- which is the independence the
    neutral-ruler discipline asks for, applied to the adjudicator rather than to a policy.
  * THREE RED-FIRST PLANTS, each a defect this arc has actually suffered in some form: a FORGED
    winner (the certificate must refuse a loser, a tie-loser, and an excluded candidate swapped into
    the winner field); the BASELINE CANNOT WIN (L62 made structural -- the seated null is scored and
    displayed but excluded from the field, and the plant makes it the best number on the table and
    demands it still not be crowned); and FRAGILITY IS DETECTABLE (or "STABLE" means nothing, L61).

THE MEASUREMENT, and it is the interesting part. WINNER STABILITY is Rung 5's instrument transferred
one level up: Rung 5 deleted each PROBE and asked whether the W3 verdict flipped, finding it
ONE-PROBE FRAGILE with QP05 carrying 73% of the ablation difference. Here each JOINT is deleted, the
whole leave-one-joint-out table recomputed, and the WINNER re-selected.

    winner (full corpus)  topmass          joints  33
    winner census         {topmass: 33}    flips   0
    VERDICT               STABLE

The same instrument returns the OPPOSITE verdict one level up. `topmass` wins on all 33 single-joint
deletions and continues to beat the baseline on every one of them -- so Rung 9's recorded win is not
carried by any single joint, which is precisely what Q's W3 verdict could not say about itself.

WHAT THIS DOES NOT BUY, stated because the temptation is exactly here. Stability is NOT standing.
L63 requires REPEATED and PREREGISTERED improvement over the seated incumbent, and a verdict that is
robust to deletion within ONE retrospective corpus is still one corpus, read after the fact. A
stable wrong answer is stable. `topmass` remains EXPERIMENTAL, and the INSTRUMENT REGISTRY is
unchanged by this rung. What the measurement supplies is a BOUNDARY on Rung 9's claim -- a
`does_not_show` made numerical -- which is why it, too, needs no standing.

REFUSED, from the same six proposals:
  * TOURNAMENT MORPHISMS -- refused on the Rung 9 ruling, unchanged. Four tournaments sharing a TYPE
    (objects, objective, comparator, winner) does not give morphisms CONTENT. A morphism earns its
    name by preserving something non-trivially, on an exhibited non-identity instance; none exists,
    so none is claimed. This is the detector "algebra" defect a second time, and recognising it
    twice is worth more than building it once.
  * SELECTOR EQUIVALENCE -- the same shape, deferred with it.
  * OPTIMIZATION PROVENANCE -- not refused, ABSORBED. A provenance chain (selector + metric + corpus
    + tie rule -> hash) is the certificate plus the selector object, serialized. Building it as a
    separate object would multiply the apparatus without adding a check, and the arc has a standing
    preference against that (L58: representation earned, not designed).

REDUCED, and this one is worth a successor rung. DORMANT-STATE ANALYSIS -- "values whose correctness
is never exercised because every reachable execution keeps some guarding predicate false" -- names
Rung 9's defect exactly and is UNDECIDABLE in general (it is reachability). A sound approximation
over-reports every error branch and every fallback, and this arc has retired four heuristics for
guessing at prose already. The DECIDABLE restriction is not "which values are dormant" but "which
values did THIS RUN not exercise", and it lands on a measured hole: there is NO COVERAGE
INSTRUMENTATION ANYWHERE IN THIS REPOSITORY (verified this rung -- every `coverage` hit in the tree
is a capsule-containment certificate or prose, and there is no `.coveragerc`, no `pytest-cov`, no
`trace.Trace`). 854 gate rows and zero measurement of what they exercise. A dormancy detector
restricted to output-exercise over the gate's own run would have caught Rung 9's defect, and it is
buildable. NOT BUILT HERE, and named so a successor tests it rather than inherits it.

GRADE. MEASURED: the certificate and its property-based verification, the three red-first plants
(all bite), the stability census over 33 deletions, determinism (stdlib-only, exact integer/rational
arithmetic, rerun byte-identical). DECLARED: that a selector is apparatus rather than a diagnostic --
the argument for the licence above, which is a reading of L63's scope, not a measurement.
does_not_show: that `topmass` predicts anything; that stability implies validity (a stable wrong
answer is stable); that a retrospective verdict survives prospectively; that no OTHER inline
selection functional remains unaudited in the arc -- one was found and made explicit, and
`sample != universal`.

FALSIFIER. `forged_winner_is_caught()` and `baseline_cannot_win()` in `selection.py`. If a
certificate ever verifies with a losing candidate swapped into its winner field, or a tournament
ever crowns its own excluded baseline, the certificate certifies nothing and every verdict resting
on one -- including this rung's stability verdict -- is unsupported.


## RUNG 11 — the Rung 9 verdict is METRIC-DEPENDENT, and the brake reports 0/10 (2026-08-05)

TWO INSTRUMENTS, AND THE FIRST ONE FALSIFIED THE HEADLINE OF THE RUNG BEFORE IT.

### 1. SELECTOR SENSITIVITY — perturbing the SELECTOR instead of the corpus

Rung 10 measured WINNER STABILITY by deleting each joint: `topmass` won all 33 deletions, verdict
STABLE. That perturbs the DATA. This perturbs the SELECTOR, over a polytope DECLARED BEFORE IT WAS
EXPLORED -- and the declaration is most of the result, because nearly every apparent degree of
freedom is already pinned by laws on the books:

    objective   FIXED by the metric. Both scores are losses; `max` is not a variant, it is an error.
    exclude     FIXED by L62. A baseline that can win its own contest is the defect L62 names.
    baseline    FIXED. The rolling empirical marginal null is the seated incumbent (checkpoint 9).
    metric      FREE, 2 values -- Brier and log loss, both PROPER scoring rules.
    tie_break   FREE, 2 values -- both arbitrary but deterministic.

FOUR admissible selectors, not dozens. The smallness is a measurement of how much the existing laws
already determine.

                                        BRIER (x10000)      LOG LOSS (millibits)
        null   (seated)                        2539                      1013
        margin                                 2651                      1050
        nclass                                 2586                      1033
        topmass                                2433                      1043

        BRIER    -> beats the null: topmass          LOG LOSS -> beats the null: NONE

**MIN SELECTOR EDIT DISTANCE TO A DIFFERENT WINNER: 1.** Changing the metric alone -- Brier to log
loss, both proper, neither privileged -- moves the winner from `topmass` to `nclass` AND removes the
win entirely: under log loss NO covariate beats the seated null, and `topmass` falls from FIRST of
three to THIRD, scoring worse than the null it was recorded as beating.

    Rung 9 recorded: "`topmass` holds ONE out-of-sample win, the first any joint-level covariate has
    recorded." That sentence is TRUE UNDER BRIER AND FALSE UNDER LOG LOSS, and Rung 9 did not say so
    because the check was never run. The claim is hereby BOUNDED, not withdrawn: it was correctly
    scored under the rule it named, and it is now known to be rule-dependent.

WHY THIS IS A RECURRENCE OF L20 AND NOT A NEW LAW. `multinull` established at checkpoint 9 that the
INCUMBENT verdict is not rule-dependent -- Brier and log loss agree that the incumbent beats the
null -- and printed "the seated verdict is NOT rule-dependent". That agreement was measured on ONE
comparison and, without anyone claiming it, functioned as background permission to report a DIFFERENT
comparison under a single rule. A property measured on one sample, operating as though universal:
that is L20 exactly, and the arc's own apparatus was sitting one file away the whole time. Recorded
as a recurrence (L3), not minted.

THE TWO ROBUSTNESS AXES ARE ORTHOGONAL, and this is the general finding worth keeping:

        perturb the DATA     (leave-one-joint-out)  -> STABLE          (33/33, no flips)
        perturb the SELECTOR (admissible polytope)  -> SENSITIVE       (1 edit suffices)

A verdict can be robust to every observation and fragile to the rule that read them. Neither axis
substitutes for the other, and reporting only the first -- which Rung 10 did -- overstates
robustness while being entirely correct about what it measured.

### 2. APPARATUS — the cost side measured, the gain side REFUSED

The only proposal in a long sequence that could return an instruction to STOP, so it was built among
its batch rather than after it.

        10 modules      2625 lines      2091 code      112 defs
        GATE COVERAGE OF THIS ARC: 0/10

`exe_epistemics` appears ZERO times in `verify.py`. The arc that scores the gate is itself ungated --
defensible, since gating the scorer would close the loop it exists to open, but it means every
falsifier in this directory is enforced by nothing except an author choosing to run it, and that
unenforced surface is now 2625 lines.

THE GAIN SIDE IS REFUSED, NOT DEFERRED. Any numerator -- claims enabled, quantities produced, defects
found -- would be chosen by the author of the apparatus being scored, with outcomes known. That is
the freedom checkpoint 9's preregistration exists to remove, and a ratio with a fabricated numerator
is WORSE than no ratio because it looks like a measurement. The licence is named instead: a numerator
PREREGISTERED and frozen before anything is scored against it. `count != value`.

THE BRAKE WAS WRONG ABOUT ITSELF TWICE, WHICH IS RECORDED RATHER THAN TIDIED AWAY. (a) It measures
every module in its directory BY RUNNING IT, and it lives in that directory -- the first run spawned
itself recursively and hung. (b) Its gate-coverage test searched `verify.py` for the bare module
STEM and reported 2 of 10 gated; both hits were unrelated prose ("all n_probes pinned probes across
the Loewner scenes"; "adaptive representation selection"). **The instrument built to prevent
overstatement overstated enforcement by exactly two on its first run.** Both are repaired, the second
with a red-first plant (`gated_test_rejects_bare_prose`) that fails on the shipped version. A brake
that has been wrong about itself twice in one rung is the correct amount of evidence that brakes
need falsifiers too.

### RULINGS on the remaining proposals

  * APPARATUS DEPENDENCY GRAPH -- ALREADY EXISTS, and naming it would duplicate machinery. The
    evidence graph carries FORMULATED_FROM and SUPPORTED_BY; `claim-class-registry` is a live gate
    row that TYPE-CHECKS those relations, requiring each to declare its epistemic class and the row
    that ENFORCES it, and forbidding a HISTORICAL relation from advertising a DERIVED one's
    guarantee; `provenance.py` requires any ELIMINATION or MECHANISM to name a LIVE gate row. The
    proposed rule -- reasoning may cite only downstream objects -- is what those three already
    enforce. This is renaming, not structure.
  * CERTIFICATE LATTICE -- PREMATURE. There is ONE tournament and ONE certificate; a partial order
    over a single element is trivial, and designing the lattice before the elements exist is L58
    inverted (representation designed, not earned). It earns its name at three or more certificates
    over comparable fields.
  * WITNESS COMPRESSION / MINIMAL WITNESS -- REDUCED and not built. Exact minimality over 33 joints
    is a subset search; the decidable cheap form is a GREEDY CORE (drop joints while the verdict
    holds), which yields an upper bound on the core, never the minimum. Worth a successor, and the
    approximation must be labelled as one.
  * OBSERVER FUNCTORS -- the TYPE FIX IS CORRECT and the ADOPTION IS UNEARNED. Composing over a
    shared observation schema genuinely repairs the `Repository -> Evidence` non-composition Rung 9
    named; that is a real diagnosis. But a unifying abstraction adopted across the whole arc on zero
    measured need is exactly what Gamma was -- seated by appeal rather than by evidence, and L63
    exists because it survived three rungs that way. The licence is stated so a successor can earn
    it rather than argue for it: TWO DISTINCT OBSERVERS whose composition over a shared schema
    yields something neither yields alone, EXHIBITED. One instance, and the abstraction is earned.

GRADE. MEASURED: the four-point sensitivity table, both LOJO scorings, the min edit distance, the
apparatus census, the gate coverage (0/10), and every red-first plant (all bite). DECLARED: the
admissibility of the polytope's axes -- an argument from the existing laws, not a measurement; and
that lines are a proxy for cost, stated as crude. does_not_show: that `nclass` is any better than
`topmass` (it loses to the null too); that either scoring rule is the RIGHT one -- the point is that
the verdict differs between two defensible rules, not that one is correct; that the arc's apparatus
is too large or too small, which no number here measures.

FALSIFIER. `sensitivity_can_report_sensitivity()` and `gated_test_rejects_bare_prose()`. If the
sensitivity analysis can no longer return SELECTOR-SENSITIVE on a tie-broken plant, INVARIANT means
nothing; if bare prose again counts as enforcement, the gate-coverage number is unsupported and the
brake's headline dies with it.


## RUNG 12 — three consecutive rungs shipped the SAME defect, and the paradox that hid it was false (2026-08-06)

A review of Rung 11 found two blockers. Both are real, both were verified before repair, and the
second is worse than the review knew.

### BLOCKER 1 — the fragility falsifier did not test fragility

    def stability_detects_a_knife_edge():
        ...
        return isinstance(out.get("n_flips"), int)          # TRUE of every possible result

It asserted the RETURN TYPE while its name promised the DETECTION OF FRAGILITY. Rung 10's claim that
fragility was provably detectable therefore rested on a check that could not fail (L23). It happened
to run on a fragile fixture, which is luck rather than evidence -- confirmed by evaluating the same
predicate against a zero-flip result, where it still returns True.

THE DEEPER CAUSE WAS COUPLING. The ablation was welded to `prediction_residuals.lojo`, so the only
fixtures available were REAL ones, and a fixture whose behaviour cannot be stated in advance cannot
falsify anything. The repair is the review's: `ablation_stability(items, score_fn, selector)` takes
the scorer as a PARAMETER, so the combinatorial instrument is testable independently of the
statistical model. The plant now supplies a scorer whose answers are known exactly -- `alpha` leads,
deleting the single item `KNIFE` and only `KNIFE` hands the lead to `beta` -- and demands exactly one
flip, NAMED, plus a constant control that must report zero. A second plant catches the other form of
death: the winner does not move but STOPS BEATING THE BASELINE, which an ablation watching only the
crown calls stable.

### BLOCKER 2 — "gate coverage" measured string co-occurrence, and the plant guarded a copy

`_gated` returned `"exe_epistemics" in src and stem in src` -- co-occurrence anywhere in a
one-megabyte file, sharing no expression, import, statement or executable path. It returned the right
number only because the arc's name appears in `verify.py` zero times, so nothing could co-occur with
anything. And `gated_test_rejects_bare_prose` never called it: the plant reimplemented the substring
logic inline against two local strings, so the function could have been arbitrarily wrong while the
plant passed. **A falsifier that does not execute the thing it falsifies guards a copy of it.**

**WORSE THAN THE REVIEW KNEW.** The strong claim -- "every falsifier in this directory is enforced by
nothing except an author choosing to run it" -- was not merely unlicensed, it was FALSE by a
one-hop search never run:

    tools/specfreeze/doc_currency.py    names the arc  2 times   (the _HISTORY exemption)
    tools/specfreeze/provenance.py      names the arc 77 times   (evidence strings, P1..P63)

Both are imported by `verify.py`. The gate DOES touch this arc. Renamed to what it measures --
DIRECT TEXTUAL PATH REFERENCES FROM verify.py: 0/10 -- with the transitive census reported beside
it, and the plant now RUNS `_directly_referenced` against six synthetic sources (prose-only stem;
name and stem co-occurring but unrelated; a real path; a dotted reference; neither; the stem inside
a longer identifier).

### THE THIRD INSTANCE, AND THE PATTERN

`selection.verify` checked `winner`, `score` and `field` and ignored `runner_up`,
`runner_up_score`, `baseline`, `baseline_score` and `beats_baseline` -- so a certificate could pass
with an AUTHENTIC WINNER AND FORGED SURROUNDINGS, which is precisely what a certificate exists to
prevent. It now checks every advertised field, and the plant forges NINE of them in turn.

    Rung  9  a selector whose NAME said argmin-by-score and whose RETURN was argmin-by-name
    Rung 10  a falsifier whose NAME said detects-fragility and whose RETURN was is-an-int
    Rung 11  a verifier whose NAME said verify-certificate and whose RETURN checked one field

Three consecutive rungs, one shape: **a function whose name claims more than its return checks**, in
the machinery that adjudicates every other claim in the arc. Each was found by a READER, never by a
run. That is now enough carriers to say what the tracked candidate could not say at one: the
recurrence is not about conditionally-dead outputs specifically, it is `claim != code` applied to
FUNCTION NAMES, and the reason the arc kept producing it is structural -- an ungated instrument is
proof-read, and prose review catches what the author already believes.

### THE PARADOX WAS FALSE, AND THAT IS THE RUNG'S REAL CONTENT

Rung 11 wrote that gating the scorer "would close the loop it exists to open." That conflates two
separable things, and the review is right that the split is clean:

    OFF-GATE, and must stay so -- the arc's EMPIRICAL VERDICTS. A row certifying that `topmass`
        beats the null would be the engine grading its own homework.
    GATEABLE, and now gated -- the arc's MECHANICAL OBLIGATIONS. That the selector picks by score,
        that an excluded baseline cannot be crowned, that forged certificates fail, that ties break
        deterministically, that the ablation can exhibit fragility in both its forms.

Those are apparatus laws provable on fixtures whose answers are known in advance. They touch no
corpus and certify no empirical claim. **`epistemics_apparatus` is now a live gate stage, 4 rows,
and the gate stands at 858.**

    epistemics-selector             argmin by score; the alphabetically-first candidate still wins
                                    when it genuinely wins (the repair is not an inverted hard-code);
                                    deterministic ties; an excluded baseline cannot be crowned
    epistemics-certificate          nine forgeries refused, including three surrounding-field forgeries
    epistemics-ablation             a planted knife edge found and NAMED, a constant control at zero,
                                    a lost baseline caught, sensitivity able to report SENSITIVE
    epistemics-apparatus-selftest   each repair proved to BITE against the code it replaced

THE COUPLING IS FORBIDDEN, NOT MERELY AVOIDED: the stage imports `selection` and `apparatus` only,
never `prediction_residuals`, and opens no ledger. If a future edit makes it read the corpus, the
gate begins moving whenever PREDICTIONS.md is appended and determinism dies quietly.

ONE SELECTION FUNCTIONAL, NOT A COPY PER TOURNAMENT. `prediction_residuals.joint_level_beats_null`
held its own argmin, which is how it came to hold its own bug; it now delegates to
`selection.select`. There is exactly one place for this defect class to live and it is gated.

### WHAT DOES NOT CHANGE

The Rung 11 empirical result stands unaltered, and the review's closing statement of it is adopted
verbatim as the honest form: **the Rung 9 `topmass` result is stable under single-joint deletion but
sensitive to one admissible selector edit -- the proper scoring rule. It is a Brier-specific
retrospective observation, not a rule-robust diagnostic win.**

GRADE. MEASURED: every repair and every plant (all bite, all gated), the transitive reference census,
GATE PASSED twice byte-identical at 858 rows / 0 FAIL. DECLARED: that the four gated obligations are
the RIGHT set -- they are the ones whose absence produced the three defects above, which is a reason,
not a proof of completeness. does_not_show: that the apparatus is now correct -- three defects of one
shape were found by readers in three rungs and the fourth is not ruled out by gating the first three;
that direct-reference counting establishes unreachability; anything empirical whatever.

FALSIFIER. The `epistemics-apparatus-selftest` row: a certificate whose winner and score are
authentic but whose beats-baseline verdict is inverted must pass the shipped winner-only criterion
and be REFUSED by the current verifier. If that row ever passes with the repairs reverted, the stage
is decorative.


## RUNG 13 — the FOURTH instance, found inside the repair of the third (2026-08-06)

Rung 12 closed with an explicit does_not_show: *"three defects of one shape were found by readers in
three rungs, and a fourth is not ruled out by gating the first three."* The fourth was in that
rung's own repair, and a reviewer found it the same day. The boundary was correct and it was not
idle caution.

### THE FOURTH INSTANCE — a certificate that verified its winner and TRUSTED ITS SELECTOR

`selection.verify` was rewritten at Rung 12 to check "every advertised field". It checked every
top-level RESULT field and interpreted only three of the five SELECTOR fields (`objective`,
`exclude`, `baseline`), leaving `tie_break` and `metric` carried but unchecked. Worse, the tie test
hard-coded `<` while the certificate advertised `tie_break` -- **the advertised rule and the enforced
rule were different rules.** Measured before repair, every one of these forgeries VERIFIED with the
winner and all scores authentic:

    tie_break flipped to reverse_lexicographic   -> verify TRUE
    metric replaced by a fabricated name         -> verify TRUE
    an unknown key smuggled into the selector    -> verify TRUE
    the `baseline` key removed entirely          -> verify TRUE

So the pattern is now at four, and the fourth is the sharpest because it occurred *in the act of
fixing the third*, with the docstring asserting completeness:

    Rung  9  NAME said argmin-by-score,       RETURN was argmin-by-name
    Rung 10  NAME said detects-fragility,     RETURN was is-an-int
    Rung 11  NAME said verify-certificate,    RETURN checked one field
    Rung 13  NAME said verify-EVERY-field,    RETURN checked every RESULT field and 3 of 5 SELECTOR fields

REPAIRED: `validate_selector` enforces the schema by EXACT key equality (a subset check is how a
field stops being checked), `_tie_precedes` makes verification follow the DECLARED rule, `certify`
computes its runner-up under that rule too, and `select` now validates before selecting so the
schema cannot be bypassed by the producer.

**AND ONE DESIGN CORRECTION THE REVIEW DID NOT ASK FOR BUT THE PATTERN DEMANDED.** The first repair
gave `verify` an optional `expect_metric=None`, unchecked when omitted. That is the same defect
wearing a keyword argument: an optional check defaults to OFF, so the field stays unverified in every
existing call site while the signature advertises otherwise. `expect_metric` is now REQUIRED. A
verifier cannot check that a score table came from a declared metric -- scores carry no provenance --
so the caller must state which metric it believes produced them, and the belief is checked against
the certificate rather than assumed.

### THE PREFIX HOLE, in the scanner repaired at Rung 12

`_directly_referenced` matched the bare needle `exe_epistemics/<stem>`, so:

    exe_epistemics/probes_extra.py   counted as a reference to probes.py
    exe_epistemics/probes2.py        counted as a reference to probes.py   <- A REAL SIBLING MODULE
    exe_epistemics/probes.md         counted as a reference to probes.py
    exe_epistemics/probesque         counted as a reference to probes.py

Substring containment is not path equality, and the two modules whose names NEST (`probes`,
`probes2`) are precisely the two most likely to be confused. Now boundary-aware, with the reviewer's
three fixtures plus two more and a positive control -- eleven in total, all run against the real
scanner.

### "FORBIDDEN" WAS A PREFERENCE, AND IS NOW A MECHANISM

Rung 12 wrote that corpus coupling was "forbidden, not merely discouraged" while NOTHING prevented a
later edit from adding a module-scope `import prediction_residuals`. A prohibition with no mechanism
is a preference, and saying "forbidden" louder does not supply the mechanism -- which is the same
`claim != code` failure as the other four, applied to a policy instead of a function.

`corpus_coupling()` now walks the AST of the modules the gate stage loads and reports any
MODULE-SCOPE import of a ledger-reading module. Scope is the entire distinction -- `selection`
legitimately imports `prediction_residuals` INSIDE `winner_stability`, which is what keeps the
live-corpus application available without dragging the corpus into every import -- and a text search
cannot see scope, which is why this is an AST walk. `coupling_guard_bites()` proves it on a synthetic
module carrying exactly the banned import, and proves it does NOT fire on the legal function-local
form.

WHAT IS STILL NOT ENFORCED, stated rather than glossed: an indirect read through a helper the scan
does not follow, or a corpus dependency introduced transitively. The bounded claim, adopted from the
review nearly verbatim: **this gate stage currently executes only synthetic apparatus paths and
contains no module-scope corpus import** -- not that a corpus read is impossible.

### WHAT THE FOUR INSTANCES NOW SUPPORT

Four carriers, each independently discovered, each in the arc's own adjudication machinery, and every
one found by a READER rather than by a run. Two structural readings, and the second is the one worth
keeping:

  1. The defects cluster where the code was UNGATED. Three of the four lived in modules no row
     exercised; the mechanism now exists (Rung 12, extended here).
  2. **A name is a claim, and it is the only claim in a codebase that no test checks by
     construction.** A test asserts what the author wrote down; the NAME asserts what the author
     believed. When they diverge the test still passes, because the test was written from the same
     belief. That is why every one of these was found by a reader and none by a run -- and why the
     repair is not "write more tests" but "make the name's claim explicit enough to be falsifiable",
     which is what a schema, a required argument and a declared tie rule each do.

STILL NOT MINTED as a lesson. Four carriers is enough for the pattern to be real and NOT enough to
know its repair generalises: every instance so far is in ONE directory, written by ONE author, in
ONE arc, over three days. `sample != universal` (L20) is exactly the law that would be violated by
minting now, and it is the law this arc has broken most often. The candidate stands with its carrier
count recorded, and the honest next test is whether the same shape appears in a module NOT written
during this sequence.

GRADE. MEASURED: all four selector forgeries verified before repair and are refused after; the four
prefix false positives; the AST coupling guard biting on the banned form and not on the legal one;
GATE PASSED twice byte-identical, 858 rows, 0 FAIL. DECLARED: the two structural readings above, and
that the gated obligation set is the right one. does_not_show: that a FIFTH instance does not exist
-- the fourth was found inside the repair of the third, which is the strongest available evidence
that this boundary should stay open; that the coupling guard makes a corpus read impossible.

FALSIFIER. `forged_selector_is_caught()` and `tie_rule_is_the_declared_one()` in `selection.py`,
`coupling_guard_bites()` in `apparatus.py`, all three on `epistemics-certificate` /
`epistemics-apparatus-selftest`. If a certificate ever verifies while carrying a forged tie rule or a
fabricated metric, or the AST guard stops firing on a module-scope corpus import, these rows redden
and this rung's central claim dies with them.
