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
