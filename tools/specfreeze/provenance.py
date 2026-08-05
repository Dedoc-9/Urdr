# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""provenance — the discovery-provenance substrate (READ-2, step 1 of the reordered pipeline).

`LESSONS.md` records transferable rules; `SURPRISES.md` records research redirections; this records,
for each DISCOVERY, the structured tuple that makes discoveries themselves analyzable:

    (id, operator, artifact, contradicted, evidence, repair, permanence, enforces)

The load-bearing field is PERMANENCE, and it is OPERATIONAL rather than a label. A discovery that
claims to have ELIMINATED a defect class (or built a lasting MECHANISM) must name a LIVE gate row that
enforces it — checked against this run's rows exactly as a brief-falsifier marker is checked. A boast
that some class "can no longer happen", with no living gate behind it, is refused. That is the whole
point: `brief-falsifiers` did not merely fix stale prose, it made the stale-evidence class
IMPOSSIBLE, and the record has to prove that against the row that does the forbidding. The
qualitatively different discovery (eliminate a class) is thereby distinguished from an ordinary one
(correct an instance) by a check, not by adjective.

The immediate measurable is the operator x permanence DISTRIBUTION, derived here and emitted by the
`provenance` gate row. It answers with data rather than narrative: which operators produce durable
findings, and how many discoveries ELIMINATED a class versus CORRECTED an instance versus merely
CONFIRMED the module was already right. (Recent history is dominated by CONFIRMATION — the READ pass
finding clean modules — which is the convergence signal stated as a number.)

This is the substrate the later rungs need: emergent theorem mining cannot grade a theorem's
durability, and architecture curvature cannot test whether discoveries cluster at composition
boundaries, without a structured, checkable record of where discoveries actually came from. It adds NO
new operator and NO new mechanism of its own — it is a projection of history the gate keeps honest.
"""
import collections

#: The operator that PRODUCED a discovery (L52's fixed set; DERIVE = the derive-not-declare mismatch).
OPERATORS = ("READ", "MEASURE", "MUTATE", "SEVER", "DECOMPOSE", "DERIVE")

#: What the discovery did to the future. ELIMINATION/MECHANISM are the durable ones and must name a
#: live enforcing row; CORRECTION fixed an instance; CONFIRMATION found the artifact already right.
PERMANENCE = ("CONFIRMATION", "CORRECTION", "ELIMINATION", "MECHANISM")


def _d(id, operator, artifact, contradicted, evidence, repair, permanence, enforces=""):
    return {"id": id, "operator": operator, "artifact": artifact, "contradicted": contradicted,
            "evidence": evidence, "repair": repair, "permanence": permanence, "enforces": enforces}


#: The discoveries this ledger can attest firsthand (LESSONS L5, L48-L55; the READ-2 clean reads). A
#: one-time structuring of history; new discoveries append a record natively, derived-forward.
DISCOVERIES = (
    _d("L5", "MEASURE", "verify.py", "a green gate proves the suite ran",
       "a sync-truncated verify.py ran zero checks and exited 0", "the gate red-tests itself",
       "MECHANISM", "tamper-selftest"),
    _d("L48", "SEVER", "edgeattr", "the declared dependency graph (imports)",
       "storecost.serialize carries a law it is not imported for",
       "attribute by severance; the declared-vs-severed wall", "MECHANISM", "edgeattr-walls"),
    _d("L50", "MEASURE", "doc_currency", "'87 modules have no brief' — a stale count of an ABSENCE",
       "the claim sat at 87 for a full rung after five briefs landed",
       "recompute the complement from the filesystem", "ELIMINATION", "doc-staleness"),
    _d("L52", "DERIVE", "brief-falsifiers evidence", "the hand-maintained arc description",
       "the evidence string went stale 5 -> 7 -> 11", "derive the count and enumeration from the set",
       "ELIMINATION", "brief-falsifiers"),
    _d("L53", "READ", "hainuwele/README.md", "the arc modules carry 'NOT ONE' brief",
       "blindscreen, the module the sentence named, already had a brief", "correct the stale narrative",
       "CORRECTION", ""),
    _d("L55", "READ", "rollstore_brief", "'not begun' vocabulary is safe in a brief",
       "doc-staleness reddened on the brief before it shipped", "reword deferred work as 'deferred'",
       "CORRECTION", "doc-staleness"),
    _d("read:persist", "READ", "persist", "a dense storage module hides a defect",
       "the realization identity was already gated and honest", "brief written", "CONFIRMATION"),
    _d("read:resurrect", "READ", "resurrect", "the through-death recovery has an unstated gap",
       "revival from the store alone was already gated across a real subprocess", "brief written",
       "CONFIRMATION"),
    _d("read:glide", "READ", "glide", "the refinement bridge is looser than claimed",
       "floored glide == drive over 640 cases; the module even keeps its own bool==1 scar",
       "brief written", "CONFIRMATION"),
    _d("read:splice", "READ", "splice", "memorylessness is only for cell-aligned cuts",
       "the sweep resumes from genuinely fractional wall-stopped poses", "brief written", "CONFIRMATION"),
    _d("read:disjoint", "READ", "disjoint", "a high-density module hides a defect",
       "the polarity hazard was documented as a class, not a slip", "brief written", "CONFIRMATION"),
    _d("read:storm", "READ", "storm", "the DST claim is imprecise",
       "the typed-chaos two-teeth invariant and prefix property were exact", "brief written",
       "CONFIRMATION"),
    _d("read:voxlat", "READ", "voxlat", "the overflow bound is estimated, not decided",
       "4*B^3 decided exhaustively; the 57-vs-84-bit hazard is the module's own plant", "brief written",
       "CONFIRMATION"),
    _d("read:nway", "READ", "nway", "the n-way theorem is asserted, not cross-checked",
       "shard-head == global-head against terraform's independent lift", "brief written", "CONFIRMATION"),
    _d("read:commute", "READ", "commute", "the diamond is argued from geometry",
       "both orders discharged constructively in bytes over the corpus", "brief written", "CONFIRMATION"),
    _d("verify:storm-flink", "MEASURE", "storm_brief", "trust the module's Flink/DST characterization",
       "Carbone 2015 'effectively-once' confirms it; storm sharpens it to cross-host bytes",
       "cite the anchor precisely", "CONFIRMATION"),
    _d("read:heightfield", "READ", "heightfield", "the most-depended-on hub is the likeliest carrier of a latent defect",
       "the T1 canon reads clean: exact-integer bytes, typed refusals, bool excluded on purpose, its own "
       "linear-fade non-vacuity plant, and terrain identity independent of presentation — the S11 datapoint",
       "brief written", "CONFIRMATION"),
    _d("read:jurisdiction", "READ", "jurisdiction", "admissibility attaches to the declaration a claim arrives with",
       "the joint holds AND already carries a graded authority-seam law: jurisdiction is a LATTICE predicate "
       "(defect in cells) refusing regardless of the certificate, closing provbind's metadata-only lift attack, "
       "and the Kleene filtration is honestly graded forgeable — a one-sided screen, not integrity", "brief "
       "written", "CONFIRMATION"),
    _d("read:layertheorem", "READ", "layertheorem",
       "a potential-field reading: conservative circulation, monotone equipotential strata, its own type guard",
       "the source refutes the field model — the seven 'layers' are ARCHITECTURAL roles and the theorem is "
       "one-way authority flow (single source, outward, membrane/no-feedback), the Urðr certified instance of "
       "the ANCESTRY principle, not a field-circulation claim", "brief written", "CONFIRMATION"),
    _d("read:opcost", "READ", "opcost",
       "P1's frozen refutation risks: the cost seam is admission-in-disguise, or cost is a conserved invariant",
       "the live rows measure both false — within_budget admits at/under and OPCOST-REFUSEs over (the budget "
       "law), count <= bound STRICT on the wall scene (the envelope is non-vacuous), and the predicate input "
       "is measured work, not canonical state; the first READ resolved against a frozen pre-registration "
       "(P1: CONFIRMED-MODEL, the contamination note disclosed in the ledger)",
       "brief written; P1 resolved in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:terraform", "READ", "terraform",
       "P2's frozen hypothesis: representation-equivalence is the WHOLE core law (chunked-apply == "
       "monolith-apply, CAS-guarded)",
       "the central row certifies the equivalence (edit == direct mutation byte-for-byte, exactly one "
       "manifest slot moves) AND a half the prediction missed — anamnesis: parent and edited world "
       "reassemble from ONE shared store, mint-never-mutate; the CAS stayed the guard (risk a did not "
       "materialize) and ordering is structural in the chain row with commutation in the commute module "
       "(risk b did not); the second blind READ under the freeze-before-history rule, resolved "
       "CONFIRMED-MODEL with the under-prediction recorded",
       "brief written; P2 resolved in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:stance", "READ", "stance",
       "P3's frozen hypothesis: an admission seam whose wall-crossing steps carry a TYPED REFUSAL",
       "the rows confirm the predicate and refute the refusal semantics — a wall never refuses: blocking "
       "is a MEASURED event (the first walled step index) and STANCE-REFUSE guards only the domain "
       "boundary (8/8 typed, malformed declarations); the third blind READ produced the ledger's FIRST "
       "residual (delta: refuse -> measure, a class neither pre-named risk covered) and the second-order "
       "meta-prediction resolved INDETERMINATE by its own terms — its outcome partition was incomplete, "
       "the exhaustive-partition rule now queued for P4's freeze",
       "brief written; P3 resolved LOCAL-SURPRISE in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:warden", "READ", "warden",
       "P4's frozen hypothesis under the first exhaustive outcome partition: claim-admission with typed "
       "refusal, beta_0 as derived support for trajectory-checking",
       "the core law held exactly (admit-or-typed-refuse, 4/4 sub-codes; honest walk and glide admit) and "
       "P3's residual used PREDICTIVELY held too — warden refuses CLAIMS where stance measures WALKS; the "
       "unnamed structure (meta M-0): beta_0 is not support but a SECOND ORTHOGONAL certificate refusing "
       "BARE POSITION claims from the component structure alone, no trajectory to inspect — the fourth "
       "blind READ, the first decidable second-order verdict, the first residual->prediction->confirmation "
       "loop",
       "brief written; P4 resolved W-C0 / meta M-0 in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:budget", "READ", "budget",
       "P5's frozen rival predictions: B-A exhaustion-envelope central (cost recurrence) vs B-B "
       "monotone/no-refund central (one-way flow) — the first basis-discriminating experiment",
       "the discrimination did NOT occur and the frozen partition recorded it honestly: ONE central row "
       "(budget-descent) certifies both inseparably — a well-founded descent on (N,<): never up (a refund "
       "is refused; the pump is measured, 4 clean submissions buy a violating block) and bottom-refusal "
       "(exactly 6 unit charges succeed, the 7th raises) are one law; and the run's LARGEST unnamed "
       "dimension surfaced — composition-soundness (subadditivity spent as enforcement: 0 under-charges "
       "over 55 pairs, EXACT on 49 prefix-disjoint pairs, conservatism priced) which NEITHER basis "
       "carried; the fifth blind READ closes the run (meta M-0, 5 for 5)",
       "brief written; P5 resolved C-AB in exe_epistemics/PREDICTIONS.md; the checkpoint fires next",
       "CONFIRMATION"),
    _d("read:wire", "READ", "wire",
       "P6's frozen rival predictions: B-A' transport/ordering central vs B-B' equality-adjudication "
       "central — run 2's first READ, frozen with credences, MT kills, and the interface instrument's "
       "risked background call",
       "the second consecutive C-AB: the central row fuses byte-equality adjudication (a verifier, not "
       "a believer; refuse-purity) with derived-never-shipped transport and structural ordering (the "
       "parent chain as sequence number, RAN-0 nullity as interleaving invariance) — now COUPLING data; "
       "the mutants' P5-derived composition axis classified wire's mints-nothing structure correctly on "
       "its FIRST forward outing; the interest law (sound and necessary-with-detection) noted as an "
       "attention axis neither rival carries; the interface instrument's background prediction was "
       "RIGHT (no new family); weights unchanged at 1/2 each; v_D = 0, run 2 continues",
       "brief written; P6 resolved C-AB in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:horizon", "READ", "horizon",
       "P7's frozen rival predictions: B-A' time-envelope central vs B-B' time-adjudication central — "
       "the first READ on which the rivals genuinely discriminated",
       "the rows chose B-A': the central row certifies the ENVELOPE (admitted depth <= H, worst-case "
       "window EQUALS H — tight) with the typed refusal as its enforcement, and the reusable "
       "discriminator is earned — a predicate reading a MEASURED MAGNITUDE against a DECLARED CEILING "
       "is cost (opcost, budget, horizon), one reading STATE-LAWFULNESS is admission (jurisdiction, "
       "warden); the cost family's THIRD preregistered instance (L3 recurrence satisfied); unnamed: the "
       "OPODIS dependency (the envelope exists because delta=0 collapsed every cost but depth — the "
       "window rides the representation seam) and mints-nothing composition again; weights separate "
       "3/4 vs 1/4; v_D = 0 twice consecutively — the signed rule CLOSES run 2; checkpoint 2 fires",
       "brief written; P7 resolved C-A in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:lease", "READ", "lease",
       "P8's three-way frozen predictions: the parents (converging) called an interval-admission gate "
       "central; the merged basis B-M distinctively priced a structural EXCLUSIVITY/COMMUTATION "
       "invariant",
       "the module names its own keystone and the central row certifies it — INTERVAL COMMUTATION "
       "(the leased edit admits at every insertion position, bytes unchanged, one head: RAN-0's diamond "
       "iterated without re-proving) plus AMORTIZATION (cheap admit == full reproof bit-for-bit), gates "
       "as guards — B-M's first FORWARD confirmation (C-INV 35 vs the parents' 15), and the frozen MT "
       "kill fired: an order-free structural law needs the invariant cell B-B' lacks (second structural "
       "exception) — B-B' ELIMINATED, the tournament's first death; unnamed: the LOST-UPDATE cross-law "
       "hazard (anamnesis composing adversely with admission, repaired by two jointly-load-bearing "
       "layers, plants proving both-gutted lands it); weights B-M 0.61 / B-A' 0.39; meta M-0, 8 for 8",
       "brief written; P8 resolved C-INV in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:drive", "READ", "drive",
       "P9's frozen rival predictions (the first batch freeze): B-A' transcript-identity central vs B-M "
       "splitting identity/measurement — with the interface instrument's FIRST high-Gamma cell at stake",
       "transcript identity central, B-A' right: the module's two NOVEL facts are DETERMINISM (the "
       "trajectory is a pure fold over the input log — the lockstep witness on terrain) and "
       "TAMPER-EVIDENCE (the digest binds start+log+trajectory; a forged, replayed, or reordered command "
       "moves it — anti-cheat moved down to the command stream), the step law inherited from stance; the "
       "second consecutive v_D zero CLOSED run 3; the instrument's first high cell CONTRADICTED its "
       "elevated-emergence call (clean confirmation delivered); weights tightened to B-M 0.51 / B-A' 0.49",
       "brief written; P9 resolved C-REP in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:govern", "READ", "govern",
       "P10, declared NON-SCORING before the seal broke: the stage docstring had been read in an earlier "
       "rung, so the core law was exposed and no tournament evidence could be earned",
       "the disclosed law confirmed (refuse-or-defer never overrun; serve-in-order never starve; "
       "conservation admitted+deferred==all) AND the watched thing materialized: govern-progress-wait "
       "certifies genuine SCHEDULER laws — progress (every tick admits >= 1) and bounded-wait (drain <= N "
       "ticks, FIFO, no starvation) — a SCHEDULING-axis candidate no basis carries, first sighting "
       "recorded for checkpoint 3; read for the brief pass, weights untouched",
       "brief written; P10 recorded non-scoring in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:liveness", "READ", "liveness",
       "P11's frozen rival predictions: B-A' timeout-envelope central vs B-M the crashed-slow "
       "indistinguishability as the central theorem",
       "C-AB, the third under-priced tie: the TITLE conjoins the two certified laws — the KEYED heartbeat "
       "(possession not recomputability: unkeyed forged 12/12, keyed 0/12, the counterfeit reset closed, "
       "bound to clockauth's attested tick) and the WELL-FOUNDED countdown (pure subtraction on (N,<), "
       "PATIENCE-1 survivors then the fault — the budget-descent pattern verbatim on time); B-M's "
       "indistinguishability call was the module's DECLARED BOUNDARY, not its law (overfit to the lease "
       "win, recorded); unnamed: the BaseException gate-law measurement, the masking ladder, the exact "
       "1-tick replay window; weights B-M 0.58 / B-A' 0.42; meta M-0 on both scoring joints (10 for 10)",
       "brief written; P11 resolved C-AB in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:wavefield", "READ", "wavefield",
       "P12 (batch 2, post-promotion): canon-identity vs superposition-invariant central, tie priced 30 "
       "under the new rule",
       "C-AB — wavefield-properties fuses the physics invariant (bounded by sum|A|; swell travels, still "
       "is static; SUPERPOSITION EXACT, field(sum)==sum(field), no rounding) with the scenes canon (same "
       "components+tick -> same bytes); unnamed: shift-based doubling arithmetic (exact O(log), where a "
       "Q16 reciprocal would round), the 8A=cP^2 admissibility tie, and the tokenizer assertion making "
       "cross-placement parity STRUCTURAL; the tie rule paid on its first outing (Briers ~0.65-0.72)",
       "brief written; P12 resolved C-AB in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:frontier", "READ", "frontier",
       "P13: both bases predicted fast-path == slow-path equivalence for the admission accelerator",
       "R-O — the first residual since P3, minting the APPROXIMATION axis's first sighting: the module "
       "is a VERIFIED Galois connection (adjunction 63/63; sound, reductive, deliberately incomplete) "
       "whose precision loss is the COUNTED obligation signature — frontier-law certifies component "
       "commutation against the SEMANTICS (not the predicate that built the graph), conservation "
       "(proved + obligations == total, nothing silently dropped) and monotonicity; neither basis "
       "carries sound-over-approximation-with-obligation-accounting; the suspended interface instrument "
       "received its first emergence event AT A NON-HIGH JOINT (cells: high 1/0, non-high 7/1 — against "
       "the interface hypothesis)",
       "brief written; P13 resolved R-O in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:gaze", "READ", "gaze",
       "P14: the batch's genuine discrimination — the promoted basis read the observer police-first "
       "(reconstruct-or-refuse), the challenger identity-first",
       "C-R — B-M's win as working basis, on the axis that created it: a frame is ADMITTED iff covering "
       "(the Kalman full-column-rank condition — coverage decided by linear algebra) AND its "
       "reconstruction's digest equals the CURRENT authority's, else typed refuse (GAZE-NONCOVER / "
       "GAZE-LAUNDER — one mechanism, two threat models); the advancing authority is load-bearing (the "
       "same once-valid frame admits at its own pose, refuses at the advanced one — replay by "
       "construction); weights B-M 0.73 / B-A' 0.27; meta not-M-1 stands 13 for 13",
       "brief written; P14 resolved C-R in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:panelight", "READ", "panelight",
       "P15 (batch 3): view-firewall vs idle-economy centrality — which of the V-phase opener's laws "
       "is the law",
       "C-AB, three laws in three rows with no single center: INTERACTIVE == BATCH (the tick transcript "
       "equals glide_cells bit-for-bit — playing it and folding it agree, the trust theorem of the "
       "visible world), the ACCUMULATOR (alpha bounded; total ticks conserve time; each input consumed "
       "EXACTLY ONCE with refusal on shortfall; the DECOUPLING law — render cadence never moves the "
       "authority) and the INTERPOLATION FIREWALL (the witness over tick poses only — D15 on time); the "
       "second consecutive v_D zero CLOSED run 4 here",
       "brief written; P15 resolved C-AB in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:wardhom", "READ", "wardhom",
       "P16 (post-closure): equivalence-vs-invariant centrality for the stated identity",
       "C-EQ — wardhom-tie certifies warden.betti0 (union-find) == URDRPD1 F2-rank beta0 on every pinned "
       "world including the 16x16 barrier, with the F2 computation CROSS-PLACED (Python == C99 == Rust, "
       "digest bit-for-bit) and non-vacuity pinned in the topology itself (barrier beta0=3, cliff 2, "
       "flat 1; the defect mode inflates beta0 and moves the digest) — the neutral-oracle pattern at the "
       "anti-cheat's foundation",
       "brief written; P16 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:ashdepth", "READ", "ashdepth",
       "P17 (post-closure): floor-gate vs measurement centrality for the vacuity floor",
       "C-FLOOR — and the handed-down design REFUTED by measurement: soundness NEVER breaks under "
       "coarsening (0 unsound at every level; the proposed coarse-end k* passes vacuously at maximum "
       "burn), so the guarded bound is INVERTED to k_min (the fast path must still distinguish "
       "something), with VacuityError instead of quiet zeros and EMPTY_CORPUS pinned as a tripwire; the "
       "module names the arc's characteristic-failure law after its fourth appearance — wrong answers "
       "are rare, empty answers are common, and an empty answer is indistinguishable from a correct one "
       "unless something asserts non-emptiness; approximation-axis CONTENT without the frozen R-O "
       "trigger — the letter-vs-spirit question recorded for checkpoint 4",
       "brief written; P17 resolved C-FLOOR in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:auditgraph", "READ", "auditgraph",
       "P18 (batch 4): kappa-price vs topology-theorem centrality for the exclusion price",
       "C-PRICE — auditgraph-law is the theorem chain: splitview's gossip graph was EXOGENOUS but an "
       "official server BUILDS its own (matchmaking is the attack surface; Bell(k)-1 partitions "
       "disconnect and the server picks), committing topology to CLIENT IDENTITY collapses that to 0/1 "
       "leaving only ADMISSION, and the price of undetected equivocation is exactly kappa the VERTEX "
       "connectivity (attack census == Menger max-flow, 771 graphs to order 5, 0 exceptions; all-pairs "
       "uniquely unbreakable, reversing splitview); the RECORDED LIE (a cross-check comparing two copies "
       "of one loop, shipped 3x, refuted BY MUTATION and now falsified every gate pass) is L23 "
       "self-applied, and the denominator defect is the VACUITY LAW's fifth carrier; challenger pricing "
       "wins, weights 0.614/0.386",
       "brief written; P18 resolved C-PRICE in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:cpredict", "READ", "cpredict",
       "P19, NON-SCORING: horizon's read had exposed reconcile/reconstruct and delta=0",
       "the disclosed law certified — cpredict-equivalence (reconstruct == authoritative glide "
       "bit-for-bit, delta=0, which is what makes rollback cost purely a function of depth) and "
       "cpredict-refines (localize the first mispredict boundary, replay only the suffix, memoryless "
       "byte-exact resume); read for the brief pass, weights untouched",
       "brief written; P19 recorded non-scoring in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:driftgaze", "READ", "driftgaze",
       "P20: shift-admission vs resident-set-conservation centrality for the client that MOVES",
       "C-AB — driftgaze-shift fuses the two: the mover CHUNK-REFUSEs on unloaded demand then runs on "
       "the resident view EQUAL to the full-field glide bit-for-bit after the verified acquire, interest "
       "following the gaze over a resident set that changes beneath the walk (police + equality in one "
       "law); mints nothing (wire replica + grid dims); unnamed: re-acquisition carries history "
       "(catching up is a FETCH not a replay), the stale-acquisition split (fetch checks integrity not "
       "currency, caught at the CAS), and the gap repair paying the storm's declared W4 debt; the second "
       "scoring v_D zero CLOSED run 5; meta not-M-1 18 for 18",
       "brief written; P20 resolved C-AB in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:geoquorum", "READ", "geoquorum",
       "P21 (batch 5): single-predicate vs the coverage/integrity DISTINCTION as the central law",
       "C-SPLIT — geoquorum-law is a distinction with a decided theorem under it: a self-consistent "
       "DOCTORED capture has the SAME internal divergence (zero) as an honest one (self-consistency is "
       "the one property a liar can always supply), so intent is invisible to any per-submission bound; "
       "the only evidence a liar does not control is other people's captures (oobprior's excluded cohort "
       "via voxlat Morton-prefix), and strict-majority consensus flips exactly at ceil(k/2) DECIDED by "
       "enumeration (a floor(k/2)+1 draft was REFUSED), even cohorts buying nothing; the two refusals "
       "UNAVAILABLE (coverage) vs FAILED (integrity) are the discriminability-of-refusal axis, watched "
       "not minted; MIN_COHORT=5 is L61's seventh carrier, non-STARVED; weights 0.634/0.366",
       "brief written; P21 resolved C-SPLIT in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:ghostsnap", "READ", "ghostsnap",
       "P22: equal-or-refuse admission vs ghost-state identity centrality for the actor wire",
       "C-R — ghostsnap-admit: a ghost is a 112-byte content-addressed per-tick pose record chained by "
       "parent digest (terraform's chain law on the movement plane), admitted under the SAME "
       "equal-or-refuse discipline as the terrain wire (tampered / foreign-parent genesis / "
       "out-of-interest / out-of-order refuse ghost-map-byte-identical; duplicate refuses; in-order "
       "retry admits) — a ghost that CANNOT LIE; police x representation, the wire pattern's third "
       "instance (wire, driftgaze, ghostsnap); order-is-structural, no sequence numbers; weights "
       "0.68/0.32",
       "brief written; P22 resolved C-R in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:hand", "READ", "hand",
       "P23 (the batch's genuine discrimination): B-M' structural-invariant reading vs B-A'' admission "
       "predicate for the cross-region handoff",
       "C-INV — hand-equivalence is HANDOFF EQUIVALENCE: glide the prefix over F_A, resume the suffix "
       "over F_B (a two-field splice, memoryless) EQUALS a single glide over the merged world "
       "BIT-FOR-BIT (seamless not by blending — which hides float drift URDR lacks — but by being "
       "bit-identical to one authority), with latency-invariance (any in-band tick) and one/many-point "
       "scale, seam-agreement load-bearing (F_A != F_B or out-of-band is typed HAND-REFUSE); a "
       "structural continuity invariant (no-gap/no-overlap, the lease/migration pattern) — B-M''s "
       "founding axis, forward; the discrimination goes to B-M', weights 0.74/0.26; run-6 triple zero "
       "CLOSED run 6; meta 21 for 21",
       "brief written; P23 resolved C-INV in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:interest", "READ", "interest",
       "P24 (batch 6): relevance-predicate vs broad/narrow-equivalence centrality for AoI",
       "C-EQ (bases agreed) - interest-soundness: the BROAD phase (bucket 3x3, bucket = x >> k, an exact "
       "shift) CONTAINS the NARROW phase (Chebyshev <= R) for R <= 2^k, so the acceleration NEVER MISSES "
       "a relevant actor (a miss is a desync; an extra is only wasted bandwidth); R<=2^k load-bearing "
       "(the R>2^k miss is planted), strict>0 the non-vacuity floor (L61's eighth carrier); the "
       "approximation axis's THIRD carrier (frontier, ashdepth, interest), strengthening not minting; "
       "retirement-neutral",
       "brief written; P24 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:mesh", "READ", "mesh",
       "P25: the role states MESH == MONOLITH - equivalence-vs-invariant centrality",
       "C-EQ (bases agreed) - mesh-law: a concurrent multi-steward simulation with authority MIGRATING "
       "equals the monolith BIT-FOR-BIT (a theorem re-derived in bytes, not best-effort convergence), a "
       "composition of nway (one independence round) + migrate (witness-neutral authority move) + "
       "terraform as the MONOLITH ORACLE that ignores custody so a meshed bug cannot hide in its own "
       "answer; generalizes reunify==monolith from static to MIGRATING partition, reject-whole; "
       "retirement-neutral",
       "brief written; P25 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:panewire", "READ", "panewire",
       "P26 (the retirement discrimination): B-M' police/AB vs B-A'' representation-first for the wired window",
       "C-AB - panewire-concord: two windows one authority, the same (input,edits) run twice lands the "
       "IDENTICAL composed witness (an edit in one view seen in the other) while a different stream "
       "diverges, and a tampered edit refuses mid-loop replica-byte-unchanged (equal-or-refuse UNDER "
       "PLAY); the whole arc composed (panelight tick + wire admission + driftgaze acquisition); B-M' won "
       "the discrimination, B-A'' third consecutive loss at w=0.198<0.20 so BOTH retirement conditions "
       "met: B-A'' RETIRES and the tournament collapses to B-M' sole; second consecutive triple zero "
       "CLOSED run 7; meta 24 for 24",
       "brief written; P26 resolved C-AB in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:priogov", "READ", "priogov",
       "P27 (batch 7, the convergence-gating joint): certified-priority-ORDER vs govern-variant "
       "centrality for the priority governor",
       "C-ORD - priogov-priority-fair certifies a CERTIFIED priority order (fresh: top priority served "
       "tick 1, lowest last, a priority-ordered PREFIX where no lower jumps a deferred higher) plus "
       "NO-STARVATION (aging: effective priority = base + age_step*wait, every actor served <= N ticks), "
       "with priogov-never-overrun (govern's cost law preserved) and a single-over-budget OPCOST-REFUSE; "
       "the digest binds the served schedule so the ORDER is MEASURED not a policy knob. THE FROZEN MINT "
       "CONDITION FIRES: govern (P10, carrier 1) + priogov (carrier 2) reach the two-carrier bar - THE "
       "SCHEDULING AXIS MINTS, the arc's SECOND minted seam family after approximation; v_D=1",
       "brief written; P27 resolved C-ORD, scheduling axis MINTS in exe_epistemics/PREDICTIONS.md",
       "CONFIRMATION"),
    _d("read:recirc", "READ", "recirc",
       "P28: soundness-of-absence vs fixed-point-invariant centrality for the Kleene recirculation",
       "C-FLOOR - recirc refutes two attached claims and both INVERT: (1) gamma.alpha is a closure "
       "operator so idempotent BY THE ADJUNCTION - the Kleene iteration is ONE step for every input "
       "(step counts 1,1,1,1,1,1,0,0), the count a CONSTANT that cannot encode a per-capture defect; "
       "(2) the closure is COARSER so 400 raw sets collapse to 5 fixed points and an honest capture "
       "collides with a doctored one - fixed-point equality is a STRICTLY WEAKER integrity check that "
       "would raise false negatives on geoquorum's omission attack. THERE IS NO LOOP - forward-only is "
       "sound, the residue a terminal hand-off; the ashdepth inversion (P17) recurring, a second "
       "vacuity carrier (v_D=0); dangerous-elegance watched not minted",
       "brief written; P28 resolved C-FLOOR in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:slo", "READ", "slo",
       "P29 (run 8 closes): composite-latency-BOUND vs composition-equivalence centrality for the SLO",
       "C-PRICE - slo composes the Stage-H arc into ONE certified worst-case number: slo-composition "
       "(worst_case == admission_wait + rollback window, an EXACT identity), slo-soundness "
       "(admission_wait UPPER-BOUNDS the governor's actual drain - a sound over-approximation, the "
       "number a real guarantee) and slo-refuse (an over-target config is SLO-REFUSE, a promise kept or "
       "declined never broken); the cost/latency family's FOURTH instance (opcost, horizon, govern, "
       "slo), touching the approximation axis a fourth time; uses the FIFO uniform bound NOT priogov's "
       "order so NOT a scheduling carrier (v_D=0). run-8 v_D=1,0,0 CLOSES run 8; CONVERGENCE DECLARED "
       "(single-basis, caveated); meta 27 for 27",
       "brief written; P29 resolved C-PRICE, convergence declared in exe_epistemics/PREDICTIONS.md",
       "CONFIRMATION"),
    _d("read:testament", "READ", "testament",
       "P30 (batch 8): durability/continuity INVARIANT vs recovery EQUIVALENCE centrality for durable "
       "intent - the author's leading credence (C-INV 40) tested against its own second call (C-EQ 22)",
       "C-EQ - testament-death: a REAL successor given nothing but the store and an address performs "
       "probate over a disk-only channel and its output is BIT-IDENTICAL to the never-died admission, "
       "twice; testament-probate states it inward (probate == living admission == global reproof) so "
       "the lease law's guarantees are INHERITED; the testament is 144 bytes and nothing more because "
       "the lease is DERIVABLE; exactly-once is free (the admission moves the authority the testament "
       "names); the refusal SPEAKS in three flavors earned from RETAINED evidence, never guessed; the "
       "executor is PURE. THE LEADING CALL LOST: 'survives its writer' is the motivation, the certified "
       "law is a recovery equivalence - claim != code turned on the author's own prediction; v_D=0",
       "brief written; P30 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:traj", "READ", "traj",
       "P31: trajectory REPRESENTATION vs observer ADMISSION centrality - the observer family had split "
       "C-REP/C-R before, so the partition was frozen near-flat",
       "C-R - traj-properties: a sequence of partial views is ADMITTED iff every innovation "
       "nu = image - H.trajectory is exactly the zero vector, else the first nonzero tick is a typed "
       "REFUSE; exact integers, divisibility-free (confirmed or fought, never rounded); the observer "
       "reconstructs the authoritative trajectory ITSELF by folding lockstep inputs with the authority's "
       "own law, so frames are checked against LOCALLY-DERIVED truth - the neutral-ruler pattern a 4th "
       "time; partial coverage becomes admissible (gaze refuses each such frame) and TEMPORAL REPLAY is "
       "caught (same-where-different-WHEN: a content-valid frame from another tick is refused, closing "
       "the gap gaze deferred). Leading call missed again (C-REP 32 vs C-R 25); v_D=0",
       "brief written; P31 resolved C-R in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:view_witness", "READ", "view_witness",
       "P32 (run 9 closes): citation-police vs firewall-invariant centrality for the view contract",
       "C-R - view-witness:cite: a DECLARED view may not MISQUOTE the authority it names - the digests "
       "the view prints as measured must EQUAL the live digests recomputed from the authority modules "
       "(a one-hex-flip forgery reddens), typed VIEW-REFUSE for a missing blob / malformed witness / "
       "missing citation; view-witness-firewall holds the structural half (knobs a namespace DISJOINT "
       "from the authority, the presentation digest anchored on the authority witness, so a knob moves "
       "the view never the witness), versioned overlays inheriting. THE DUAL: D15 proves the view cannot "
       "CONTAMINATE the authority, this proves it cannot MISQUOTE it - neither alone suffices. First "
       "joint from the four TRUE CONFORMANCE GAPS and nothing hid there: the citation equality is "
       "exogenous to any corpus BY CONSTRUCTION, so the missing corpus is a design choice not a debt. "
       "The batch's only clean leading call (45); run-9 triple zero, meta 30 for 30; v_D=0",
       "brief written; P32 resolved C-R in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("checkpoint9:multinull", "MEASURE", "exe_epistemics/multinull.py",
       "L62's open question: that the incumbent basis B-M' might beat its rivals while losing to a "
       "null - explanatory power unearned, and invisible to head-to-head scoring",
       "Delta_null = +553208846 > 0 over 22 scoring joints (integer Brier): the incumbent BEATS a "
       "rolling empirical marginal (alpha=1, counting only outcomes strictly before each joint - no "
       "future leakage), winning 15 joints, losing 7, tying 0, with leading-class accuracy 15/22 vs "
       "the null's 4/22 and near-equal sharpness (0.380 vs 0.357), so the advantage comes from being "
       "RIGHT not bolder. The spec was frozen and COMMITTED before the witness was written. Two "
       "honest counter-findings recorded: the preregistration's own claim that the catch-all would "
       "bite at P21 was FALSIFIED (it never fired - P21's partition did name C-SPLIT), which means "
       "the anti-incumbent safeguard cost the incumbent nothing; and the basis is systematically "
       "UNDERCONFIDENT (mean max probability 0.380 against 0.68 leading-class accuracy), so its Brier "
       "is beatable by sharpening alone - a structured residual, the first direct evidence the "
       "engine's errors are predictable rather than noise. No significance claimed at n=22; "
       "retrospective, so degrees of freedom were protected but blindness was not",
       "checkpoint 9 resolved in exe_epistemics/PREDICTIONS.md; convergence's predictive-adequacy leg "
       "now evidenced rather than assumed; Rung 2 (the error surface) frozen as the successor",
       "CONFIRMATION"),
    _d("checkpoint10:orbitprobe", "MEASURE", "exe_epistemics/orbitprobe.py",
       "a proposed ORBIT-RETURN scalar Omega_t = min_j d(S_t,S_j) over (bases, predictions, resolved "
       "signature, minted lineage), to separate a predictive fixed point from a sterile single-basis "
       "orbit - and the reading that three consecutive triple-zero runs evidence convergence",
       "TWO results. (1) DISPROOF: Omega as specified is DEGENERATE in this engine. The ledger is "
       "append-only (L2), so R_j subset R_t and d_R = |R_t \\ R_j| >= 3 per batch, forcing "
       "Omega_t >= 3(l+1) > 0 always - it can never return to zero, and its minimizer is always the "
       "most recent admissible j, so it measures ELAPSED BATCHES not recurrence. The defect is the "
       "state vector, not the idea: a return detector may not contain monotone-accumulating "
       "components. (2) CONFIRMATION of the proposal's premise, measured: per-batch G = null - "
       "incumbent over the checkpoint-9 corpus is NOT monotone across the three triple-zero runs "
       "(21.8M, 48.9M, 11.7M per joint) and v_D does NOT separate G (v_D=0 batches span 8.5M-48.7M, "
       "containing both the worst and nearly the best) - so the engine's own convergence census is "
       "BLIND to predictive performance, and 'three triple-zero runs' is weaker evidence for "
       "convergence than it reads. Sharpest case: b5 and b7 are predictively indistinguishable "
       "(both 3/3 leading, G/joint within 0.6%) while v_D calls them different",
       "NOT ADOPTED - the repaired configuration-space Omega is stated, not built, with a prospective "
       "falsifier frozen (>= 6 future v_D=0 batches, rolling leak-free near-return threshold, STARVED "
       "if under-supplied); the suspended Gamma instrument is the precedent refused",
       "CONFIRMATION"),
    _d("checkpoint10:blockers", "MEASURE", "exe_epistemics/orbitprobe.py",
       "that the two blockers were design inconveniences to be repaired silently - and that v_D "
       "(new-family arrival) could stand proxy for predictive gain",
       "BOTH hard-grounded. (1) W2, APPEND-ONLY ORBIT IMPOSSIBILITY, a negative theorem: any "
       "recurrence metric carrying a strictly append-only coordinate at positive weight satisfies "
       "Omega_t >= w(|c_t|-|c_{t-l-1}|) > 0 with the minimum always at the most recent admissible j, "
       "so it is monotone in ELAPSED HISTORY and can never certify return - a recurrence metric "
       "containing an append-only coordinate is a CLOCK. Plant bites both directions: two synthetic "
       "histories with identical live configuration and ledger lengths 0 vs 30 give specified "
       "distance 30 and live-quotient distance 0. Corollary adopted as framing: LINEAGE IS NOT STATE "
       "- the ledger is demoted to an immutable path label. (2) CENSUS-PREDICTION NON-EQUIVALENCE, "
       "decided by leave-one-batch-out over 7 batches with exact rational fits: null MAE 17854727, "
       "census(v_D) 19036400 (WORSE than null), history(G-1) 17498120, combined 28959563 (the "
       "overfit signature) - seating v_D makes held-out prediction of G worse than predicting the "
       "mean, so v_D is structurally informative but NOT predictively informative. Positive coupling "
       "REJECTED; threshold relation STARVED (no batch has v_D>=2); full orthogonality CONSISTENT "
       "but NOT established at n=7. Tempering finding: history beats null by only ~2%, so G is nearly "
       "unpredictable at BATCH granularity - the structure lives at the joint level",
       "W2 recorded as a stated theorem with witness (not a gate row, L58); the live-state probe "
       "corpus Q and its behaviour vector Psi frozen as the next experiment, Q to be sealed BEFORE "
       "Psi is ever computed; nothing adopted",
       "CONFIRMATION"),
    _d("rung2:residuals", "MEASURE", "exe_epistemics/prediction_residuals.py",
       "that the engine's near-unpredictable batch-level gain was an AGGREGATION artifact - that "
       "signal destroyed at checkpoint granularity would reappear at the JOINT, earning a synthesis "
       "operator; and the standing hypothesis that a low first-to-second margin predicts a miss",
       "REFUTED, and the frozen rule fired against the interesting answer. Error surface over 22 "
       "joints: CLEAN 15, RANKING 7, SUPPORT 0, PARTITION 0 - every miss is a RANKING miss (the "
       "observed class was always named and always carried real mass). Leave-one-JOINT-out Brier on "
       "the miss event: seated null 2380, topmass 2560, margin 2626, nclass 2663 - NO joint-level "
       "covariate beats the null, and the margin hypothesis fails DIRECTIONALLY (mean margin 883 on "
       "hits vs 928 on misses, the wrong way round). So the errors are unpredictable at BOTH "
       "granularities and changing the statistical unit recovers nothing. Checkpoint 9's frozen "
       "condition therefore REFUSES the synthesis operator Gamma, and with it the theory-algebra "
       "program that would have stood on it. The precise reading: the residual is a GLOBAL "
       "CALIBRATION OFFSET (systematic underconfidence, 0.380 mean max probability vs 0.68 accuracy) "
       "and NOT a conditional signal - sharpening would improve Brier but nothing says where to "
       "spend it, and a recalibration is a POST-PROCESSOR that changes confidence never ordering, so "
       "it cannot produce a discrimination and is not a challenger",
       "Rung 2 resolved in exe_epistemics/PREDICTIONS.md; Gamma refused by the frozen rule; Psi "
       "accepted as the OBSERVATIONAL QUOTIENT on the W2 + census-prediction grounds ONLY, explicitly "
       "NOT on the refuted granularity argument; L63 (empirical admissibility) minted from four "
       "carriers and applied in the INSTRUMENT REGISTRY",
       "CONFIRMATION"),
    _d("rung3:probes", "MEASURE", "exe_epistemics/probes.py",
       "that the repeated-measures questions Rung 2 left UNTESTED (persistent bottlenecks, "
       "calibration on hard joints, whether aggregation masks joint-level signal) could be answered "
       "from the READ corpus - which has n=1 per joint and therefore cannot answer them at all",
       "Q FROZEN and Psi_0 EMITTED, in two commits in that order (the corpus sealed with PSI empty "
       "before any operator was emitted against it - a probe set chosen after seeing an operator is "
       "tunable to the answer, the same discipline the checkpoint-9 null spec followed). Ten "
       "SYNTHETIC probes (QP prefix, fabricated modules never to be built, so no answer exists and "
       "none can leak - a probe from a READ module would measure recall, one from a module about to "
       "be read would contaminate the READ pass under L59), each written to sit on a seam the engine "
       "has historically SPLIT on, because L61 turned on the corpus says a probe every operator "
       "answers identically cannot detect drift. ONE fixed class space across all probes so Psi_t is "
       "a point in a common simplex and L1 distance is well defined. All ten Psi_0 vectors valid; the "
       "corpus discriminates as designed - six distinct leading classes, margins from 200 (QP06, "
       "representation vs police, near-tied) to 2000 (QP05, the scheduling axis). The attractor "
       "radius r_t now lives ENTIRELY in behaviour space, so the measurement W2/RST proved impossible "
       "in checkpoint space is well-posed - the reframe passes its own test",
       "drift, attractor radius and W3 identifiability now have a domain; Psi is AUTHOR-EMITTED so "
       "every credence is DECLARED not measured, and the resulting noise floor is not estimable from "
       "one emission - recorded before any drift number exists. STATUS: EXPERIMENTAL under L63, "
       "computable and reportable but NOT reasonable-from until it beats a seated incumbent",
       "CONFIRMATION"),
    _d("read:bombtest", "READ", "bombtest",
       "P33 (batch 9, NON-SCORING - contamination declared before the freeze): that interaction-free "
       "detection imports something from the physics",
       "bombtest-law: 'interaction-free' means exactly one MEASURED thing - the audit path invokes "
       "the rule EXACTLY ZERO times, instrumented as a call count - a claim about ACCESS AND COST, "
       "never about physics. Re-execution is the detonation (the Replay Court's bit-for-bit re-run is "
       "unpayable for embargoed data, a licensed model, a week of cluster time). Soundness is a "
       "NEVER-CLAIM in Holzmann's SPIN shape, discharged EXHAUSTIVELY: 4096 states, 13824 legal "
       "transitions, 0 acceptances; one-sided, so firing certifies and SILENCE IS INCONCLUSIVE. Plant "
       "bites: a non-conserved arm accepts 4608 times against 0 honest. Scores nothing - no census, "
       "no meta, no weight movement - so the exclusion is auditable rather than invisible",
       "brief written; P33 recorded NON-SCORING in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:buoyancy", "READ", "buoyancy",
       "P34: exact-identity vs characterizing-bracket centrality for integer flotation - the author's "
       "leading credence (C-EQ 30) tested against C-INV 25",
       "C-INV - buoyancy-properties certifies the exact ARCHIMEDES BRACKET Delta(z*) >= W > "
       "Delta(z*+1) (the characterizing property of the integer waterline) plus Delta's monotonicity "
       "(which licenses the division-free bisection) and the non-vacuity pair (the raft HEAVES on "
       "swell, RESTS on still); selftest makes the clamp load-bearing, refusals total and typed 6/6. "
       "THE LEADING CALL MISSED: 'exact integer flotation' names the ARITHMETIC not the semantics. "
       "The QUESTION/ANSWER split's THIRD carrier (stance, traj, buoyancy) - blocking is a MEASURED "
       "event and typed refusals guard only the domain boundary; the LAW is a DECLARED model while "
       "the COMPUTATION is measured; v_D=0",
       "brief written; P34 resolved C-INV in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:cayley", "READ", "cayley",
       "P35 (run 10 closes): coordinate-free INVARIANT vs verified IDENTITY centrality for the "
       "Cayley-Menger realizability law - the author priced C-INV 35 and C-EQ third at 22",
       "C-EQ - cayley-law certifies EQUALITIES against INDEPENDENTLY computed quantities: Heron in "
       "determinant form reproduces a separately computed area (-det = 16*area^2, 3-4-5 -> 576), the "
       "simplex volume reproduces a separately computed volume (288*vol^2 -> 373248), and any 5 "
       "points in 3-space give a VANISHING 6x6 determinant - a tautology holding without exception "
       "and without any coordinate frame, broken exactly by a forged distance (ring scene 0 -> -8944). "
       "THE LEADING CALL MISSED AND THE WINNER WAS PRICED THIRD. Unnamed: bareiss and leibniz_det as "
       "ORACLES FOR EACH OTHER (the neutral-ruler pattern a 5th time); the Leibniz form travels "
       "because integer division semantics differ across languages for negative operands, so "
       "division-freeness is a CROSS-PLACEMENT property; and the check asks a strictly WEAKER "
       "question than every other admission - not 'is your POSITION lawful' but 'is your set of "
       "RELATIONSHIPS possible', needing no coordinates, frame or trusted origin; v_D=0",
       "brief written; P35 resolved C-EQ in exe_epistemics/PREDICTIONS.md; run 10 closes, meta 32/32",
       "CONFIRMATION"),
    _d("rung4:repeatability", "MEASURE", "exe_epistemics/probes.py",
       "that Psi drift could be read at all before the author-emission noise floor was measured - and "
       "that accumulating more batches would eventually make a drift number interpretable",
       "eps_author = ||Psi_0' - Psi_0||_1 = 2800 over a corpus carrying 100000 total mass (2.8%), "
       "measured by re-emitting against the SAME engine state with the corpus traversed in scrambled "
       "order. Standard practice requires a repeatability coefficient before any change is called "
       "real (CR = 2.77 x SEM; a difference below it is indistinguishable from the tool's own error), "
       "so until this existed EVERY drift number was uninterpretable no matter how many batches "
       "accumulated. The confound was frozen BEFORE the number: same-session emission means anchoring "
       "is unavoidable and pushes the difference DOWN, so the reading rule was made asymmetric - "
       "eps>0 INFORMATIVE (disagreement surviving anchoring is real noise, a genuine lower bound), "
       "eps=0 UNINFORMATIVE (a zero is what perfect anchoring produces). The informative branch fired. "
       "SHARP FINDING: a leading-class FLIP at QP06 (C-REP -> C-R), the probe whose margin was the "
       "corpus's narrowest at 200 - on a low-margin probe the leading class is NOT STABLE under "
       "re-emission. Deliberately NOT inflated to a 2.77x CR: one anchored pair supports no SEM "
       "estimate, and manufacturing a coefficient would fabricate precision the control cannot supply",
       "smallest detectable drift = 2800 recorded in the registry; the KILL CONDITION is NOT YET "
       "EVALUABLE (it needs the scale of real dispositional shifts, unknown until two genuine "
       "post-work emissions exist) so Psi is neither cleared nor killed; the valid unanchored control "
       "requires a FRESH SESSION with no access to Psi_0, named and NOT claimed",
       "CONFIRMATION"),
    _d("rung4:mdl-rescore", "MEASURE", "exe_epistemics/multinull.py",
       "the frozen resolution-efficiency metric E = dG/(dC+dR) - a RATIO of INCOMMENSURABLE units "
       "(Brier points over structural counts) that diverges when a batch makes no structural change",
       "MDL expresses the complexity/fit tradeoff as an ADDITIVE code length in common units (bits), "
       "not a ratio, and log loss IS code length by Kraft-McMillan - so the same corpus was re-scored "
       "under log loss: incumbent 40535 mb vs null 61178 mb, Delta_null = +20643 millibits. IT AGREES "
       "WITH THE BRIER VERDICT (logloss_agrees_with_brier -> True), which matters more than the "
       "number: had it reversed, checkpoint 9's conclusion would have been an artifact of the scoring "
       "rule and needed re-grading. The incumbent-beats-null finding survives a change of proper "
       "scoring rule - a robustness check the original measurement never had",
       "E re-frozen as E = dL_data - lambda*dL_model, both in millibits, lambda = 1 (the canonical "
       "two-part code; a free lambda is a knob that could be tuned until any structural change looked "
       "efficient). dL_model stays OPEN and must be a real code length, never a count of edits; E "
       "remains uncomputed and EXPERIMENTAL under L63",
       "CONFIRMATION"),
    _d("read:clslo", "READ", "clslo",
       "P36 (batch 10): per-class BOUND vs certified per-class ORDER - the batch's live mint risk, "
       "since an ORDER would have given the scheduling axis a third carrier",
       "C-PRICE (leading credence 38 CORRECT) - clslo-refinement: a higher-priority class carries a "
       "TIGHTER-OR-EQUAL bound and the ONE-CLASS case reduces EXACTLY to the composite slo's uniform "
       "number (a strict generalization, checked not claimed); clslo-soundness: the per-class bound "
       "EQUALS priogov's actual per-class drain (exact for equal-cost), so the promise is derived from "
       "the scheduler that keeps it; clslo-refuse: a tier exceeding ITS OWN target is CLSLO-REFUSE, so "
       "a config cannot meet the aggregate while failing a class. THE MINT RISK RESOLVED NEGATIVE: "
       "priogov certifies the ORDER work is admitted in, clslo certifies that the resulting BOUNDS "
       "respect the class ordering - monotonicity of prices is NOT a certified order, so the "
       "scheduling axis STAYS AT TWO CARRIERS; cost/latency family's 5th instance; v_D=0",
       "brief written; P36 resolved C-PRICE in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:commuteprop", "READ", "commuteprop",
       "P37: the diamond property itself vs the falsifier's own NON-VACUITY as the central law - a "
       "property-based falsifier that never generates a biting case proves nothing (L61's shape)",
       "C-EQ (leading credence 40 CORRECT) - commute-property: across the seeded adversarial sweep "
       "EVERY ORDER LANDS ONE HEAD+FIELD, verified against a BRUTE-PERMUTATION ORACLE enumerating the "
       "orders independently, with closure agreeing and predict matching independent chunk geometry - "
       "nothing in the verification path consults the thing verified. The C-FLOOR alternative resolved: "
       "commute-property-selftest shows a mutated commute.predict (always rank 0) makes the sweep raise "
       "COMMUTEPROP-FALSIFIED and the module clean after revert, so non-vacuity is ESTABLISHED rather "
       "than CENTRAL. Neutral-ruler pattern's SIXTH instance; v_D=0",
       "brief written; P37 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:crossing", "READ", "crossing",
       "P38 (run 11 closes): a characterizing BRACKET (the buoyancy shape, which the freeze explicitly "
       "primed on) vs an IDENTITY as the central law for wave-crossing timing",
       "C-EQ - crossing-properties: the trace IS wavefield.height at the MOVING cell and tick (not a "
       "snapshot, not the start cell), the result is the FIRST overtop, and clearance is load-bearing; "
       "crossing-selftest pins it - FREEZING THE WAVE changes when the agent is overtopped, so travel "
       "is load-bearing and a static-field implementation is detectably different; 6/6 CROSS-REFUSE. "
       "AN HONEST NEGATIVE ABOUT CROSS-JOINT LEARNING: the freeze DISCLOSED moving weight to C-INV 32 "
       "on P34's lesson (this layer certifies brackets, 'exact' names the arithmetic) and the lesson "
       "TRANSFERRED BADLY - buoyancy's row is a two-sided INEQUALITY, crossing's an EQUALITY, same "
       "layer and vocabulary. Legitimate learning from a CLOSED joint, but it moved the credence the "
       "wrong way - a datapoint about the VALUE of cross-joint learning, the first this ledger has "
       "measured. What DID transfer: the question/answer split, 4th carrier; run-11 triple zero, meta "
       "35/35, leading calls 2/3; v_D=0",
       "brief written; P38 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("rung3:psi1-drift", "MEASURE", "exe_epistemics/probes.py",
       "that the first post-work operator drift would be readable as a dispositional shift - and "
       "specifically that QP06's leading-class flip after batch 10 was evidence the engine moved",
       "||Psi_1 - Psi_0||_1 = 3000 against the Rung-4 floor eps_author = 2800: it clears the frozen bar "
       "by 7%, so drift_is_interpretable returns True BY THE LETTER, but eps_author is a LOWER BOUND "
       "(the control was anchored, pushing it down) so the true floor is very likely above 3000 - "
       "technically above the floor, SUBSTANTIVELY indistinguishable from noise, and nothing is "
       "concluded about the operator having moved. THE CONTROL EARNED ITS KEEP IMMEDIATELY: QP06's "
       "leading class flipped C-REP->C-R between Psi_0 and Psi_1, which without Rung 4 reads as a "
       "headline dispositional shift on the representation-vs-police probe - but the SAME probe "
       "flipped identically in the repeatability control under ZERO intervening work, so the flip is a "
       "property of its 200-point margin, not of batch 10. Per-probe: QP08 800, four at 400, three at "
       "200, and QP03/QP10 exactly 0 (so the emission is not uniformly jittering everything)",
       "the drift reading was declared UNINTERPRETABLE-IN-SUBSTANCE and a candidate finding was "
       "DISQUALIFIED by the control one rung after it was built; Psi stays EXPERIMENTAL under L63 with "
       "its floor attached, pending an unanchored floor from a fresh session",
       "CONFIRMATION"),
    _d("rung5:w3-identifiability", "MEASURE", "exe_epistemics/probes.py",
       "that the anchored noise floor was useless for every question - and that a finite probe corpus "
       "resolving a named axis does so with the whole corpus rather than with one row",
       "THE FLOOR IS ONE-SIDED AND THAT UNBLOCKED THE RUNG: eps_author = 2800 is a LOWER BOUND, so "
       "d > eps licenses nothing (eps_true may exceed d - why Psi_1 was uninterpretable) but d <= eps "
       "licenses INDISTINGUISHABLE, since d <= eps <= eps_true however the floor is later tightened. "
       "W3 needs exactly an indistinguishable pair, so the anchored floor suffices for it. The "
       "contrast was an ABLATION (the seated basis minus the scheduling axis - B-M' as it stood at "
       "checkpoint 6), a configuration the engine genuinely occupied; explicitly NOT the retired "
       "challenger B-A'', because L63's no-zombies clause forbids reasoning from a retired diagnostic "
       "and emitting Psi under it would sail close to that. RESULT: ||Psi_abl - Psi_1||_1 = 5200 > "
       "2800, INCONCLUSIVE - W3 gains no support and the pair is NOT licensed as distinguishable "
       "either. Both frozen calls fired (author: total > 2800; directional: QP05 moves most by >= 800, "
       "it moved 3800). THE ACTUAL FINDING IS ABOUT THE INSTRUMENT: QP05 alone carries 73% of the "
       "difference, and leave-one-out shows removing that single probe FLIPS the verdict to SUPPORTED "
       "(1400 < 2800) - Q's ability to resolve the scheduling axis rests entirely on ONE PROBE",
       "the verdict recorded as ONE-PROBE FRAGILE; the generalization is that a probe corpus needs "
       "REDUNDANCY PER AXIS or every identifiability verdict is hostage to a single row - and the two "
       "design goals pull against each other, since Q's ten probes were each written on a DISTINCT "
       "seam (L61) and that distinctness is exactly what left each axis with one witness. Q stays "
       "FROZEN (a corpus edited in response to its own verdict is tunable to the answer); a successor "
       "Q' with >= 2 probes per named axis is named and UNBUILT (L58)",
       "CONFIRMATION"),
    _d("read:crosswarden", "READ", "crosswarden",
       "P39 (batch 11): admission vs equivalence vs invariant centrality at the region seam - the "
       "warden family had produced ALL THREE shapes (warden C-R, wardhom C-EQ, hand C-INV), so the "
       "joint was genuinely open",
       "C-R (leading credence 35 CORRECT) - crosswarden-insufficient is the distinguishing row: a "
       "SHARD-LOCAL warden ADMITS both boundary exploits that crosswarden refuses, so the module "
       "certifies the NECESSITY OF ITS OWN EXISTENCE by measurement rather than argument; desynced "
       "seam is WARD-SEAM, 4/4 typed sub-codes. crosswarden-kinematic: honest crossing admits, "
       "through-wall sprint is WARD-TUNNEL, honest handoff admits AND EQUALS THE MERGED GLIDE (Stage D "
       "to E). crosswarden-topological: merge == hand.merge, beta0 RISES across the merge so the "
       "topological evidence for the wall exists in NEITHER region alone; v_D=0",
       "brief written; P39 resolved C-R in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:dirward", "READ", "dirward",
       "P40: the deferred boundary warden's own does_not_show named at P4 - and the C-FLOOR tail risk "
       "that a deferred boundary turns out not to need closing (the recirc shape)",
       "C-R (leading credence 38 CORRECT; the C-FLOOR tail risk did NOT fire - it needed closing) - "
       "dirward-insufficient: the undirected warden fails in BOTH directions at once, FALSE-REFUSING "
       "the legal descent (rejecting a legitimate move, worse than a miss) and returning ONE "
       "WARD-UNREACH for both a one-way cliff and a genuine wall; dirward admits the descent and "
       "SEPARATES WARD-ONEWAY from WARD-UNREACH. dirward-asymmetry: directed reach is genuinely "
       "asymmetric on the cliff and COLLAPSES to 0 with num_scc == betti0 on FLAT terrain, so the "
       "refinement reduces exactly to its predecessor where terrain is symmetric. AXIS SIGHTING NOT A "
       "MINT: ONEWAY vs UNREACH is geoquorum's discriminability-of-refusal shape a second time, but "
       "the axis was NOT named in this joint's frozen partition so under L3 a post-hoc recurrence "
       "cannot promote it - a mint needs a FUTURE FROZEN prediction naming it in advance; v_D=0",
       "brief written; P40 resolved C-R in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:divergence", "READ", "divergence",
       "P41 (run 12 closes): that the module's JOB (supplying a defect measure, C-PRICE 30) is what "
       "its central row certifies - against C-FLOOR 28, the refutation reading",
       "C-FLOOR, a TWO-POINT MISS - divergence-law: the defect is measured in CELLS as the LARGEST "
       "CONNECTED RUN of flipped cells BECAUSE AN ADVERSARY DOES NOT ATTACK THE MEAN; two "
       "perturbations with the IDENTICAL RATE 2/35 have runs 1 and 2 and only one breaches the wall. "
       "divergence-selftest states the refutation as a plant: the rate plant assigns the SAME defect "
       "to a perturbation that leaves the wall standing and one that opens it; and the maximum is "
       "ENUMERATED not sampled because a sampled MEAN run is strictly below the attained worst case. "
       "The module supplies a measure but the gate CERTIFIES that the intuitive measure is WRONG - the "
       "ashdepth shape's THIRD carrier (ashdepth, recirc, divergence). Enumerate-don't-sample is a "
       "family habit (voxlat, cayley, divergence) - L20 turned into code three times; v_D=0",
       "brief written; P41 resolved C-FLOOR in exe_epistemics/PREDICTIONS.md; run 12 closes on a "
       "triple zero, meta 38/38, leading calls 2/3 - the miss again a two-pointer from weighing the "
       "module's JOB over what the ROW certifies, three instances in four batches, recorded and NOT "
       "acted on since no frozen prediction has named the failure mode in advance",
       "CONFIRMATION"),
    _d("read:fpcap", "READ", "fpcap",
       "P42 (batch 12): that a 'seam' module is POLICED (C-R 30) rather than certifying a containment",
       "C-EQ, leading call MISSED - fpcap-collision: the capsule COVERS its joints with the boundary "
       "exact and load-bearing (a point just inside the radius is covered, one just outside is not, by "
       "fppose's exact division-free certificate) and A SHRUNK RADIUS UNCOVERS A JOINT, the non-vacuity "
       "witness. A containment certified with a strictness witness is interest's broad-phase shape "
       "(P24 C-EQ), not warden's; the refusals guard the DOMAIN not the answer. Unnamed: it is a "
       "THREE-WAY binding - the capsule answers to the joints below (collision), the terrain beneath "
       "(the foot rests at exact ground, stance's step law biting at rise > MAX_STEP) and the pose "
       "above (cardinal pitch exact, mouse-look pitch ROUNDS - the exactness boundary stated); v_D=0",
       "brief written; P42 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:fpface", "READ", "fpface",
       "P43: whether 'exact integer' in a role line predicts the semantics - P34 had shown it is weak "
       "evidence, so C-EQ was priced only narrowly ahead",
       "C-EQ (leading credence 32 CORRECT - the batch's only clean leading call) - fpface-exact: the "
       "four cardinal facings lift to their exact direction vectors at ZERO ulp and the cyclic group "
       "E-N-W-S-E PERMUTES EXACTLY over drive's facing map, group structure preserved under the lift. "
       "fpface-boundary states where exactness ENDS: mouse-look interiors round deterministically, "
       "accumulation drifts a BOUNDED non-zero ulp count, and sqrt2/2 is a trig-free frozen isqrt so no "
       "transcendental enters the authority path - cayley's cross-placement reasoning again. The module "
       "MEASURES its own imprecision rather than claiming it away. Logged as the COUNTER-INSTANCE to "
       "P34's caution so the caution is held with the right strength; v_D=0",
       "brief written; P43 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:horn", "READ", "horn",
       "P44 (run 13 closes): the index role line states a CONSERVATION ('rung count conserved, only "
       "the pitch changes') and the freeze let it drive C-INV to 40 with C-PRICE priced FOURTH at 10",
       "C-PRICE - THE SESSION'S LARGEST MISS. horn-law: the geometric ladder is the EXHAUSTIVE MINIMAX "
       "OPTIMUM over every integer anchor schedule at each pinned (T,B), DECIDED not sampled; the "
       "continuous bound max-ratio-1 is STRICT on the integer lattice rather than an identity AND THE "
       "CHECK REFUSED THE EQUALITY AN EARLIER DRAFT ASSERTED (the gate caught the author's own "
       "overclaim); the closed form agrees with an INDEPENDENT BRUTE-FORCE ORACLE sweeping every depth "
       "(neutral ruler, 7th instance); reach is EXPONENTIAL in slot count (8 slots reach 64 ticks where "
       "a fixed window reaches 8). THE CAUSE is the failure mode the freeze itself named: the role line "
       "is horn-TWIST verbatim while the -law row carries the theorem. The tie-break was applied "
       "MECHANICALLY (<module>-law is central, consistent with mesh/recirc/cayley/divergence/bombtest) "
       "precisely so the reading was not selectable after seeing which answer flattered the author - "
       "under the alternative reading it would have been a hit, and the rule decided it. Second "
       "theorem: under starvation the ladder TWISTS rather than grows, rung count CONSERVED, reach = "
       "W*r^(B-W) exactly with the price strictly under r-1 BY THE THEOREM rather than dialled, "
       "REMOVABLE as EQUALITY OF LADDERS not merely equivalent behaviour, and DECOUPLED from the view "
       "band (zero extra view-ticks vs clockauth's band while the coupling plant buys four, so THE ZERO "
       "IS A RESULT NOT A REASSURANCE). Insufficiency proof a 3rd time in two batches; v_D=0",
       "brief written; P44 resolved C-PRICE in exe_epistemics/PREDICTIONS.md; run 13 closes on a fifth "
       "consecutive triple zero, meta 41/41, leading calls 1/3 - and the role-prose-over-row failure "
       "now has FIVE consecutive instances, which is the recurrence that licenses a FROZEN FORWARD "
       "PREDICTION: batch 13's freeze is OBLIGED to name it in advance (does the role prose point at a "
       "different class than the -law row, and does the row win), converting a recorded complaint into "
       "a testable claim - the path the approximation axis took to its mint",
       "CONFIRMATION"),
    _d("read:magicdiv", "READ", "magicdiv",
       "P45 (batch 13): whether an 'exact and exhaustively proven' role line predicts the semantics - "
       "role-reading and row-reading BOTH said C-EQ, so the joint is non-discriminating for FP-ROW",
       "C-EQ (leading credence 48 CORRECT) - magicdiv-law: floor(n/d) == (m*n) >> s DECIDED "
       "EXHAUSTIVELY over the whole word, every divisor x every dividend, 0 failures - a decided finite "
       "statement, not a sampled sweep; and the handed-down corollaries are GRADED rather than "
       "repeated, the Hausdorff-dimension claim REFUTED by definition. The selftest is the point: the "
       "floor-instead-of-ceil multiplier fails on some divisors WHILE REMAINING CORRECT FOR POWERS OF "
       "TWO, so the plant is exactly the one a sampled check would have passed. Enumerate-don't-sample "
       "on its FOURTH carrier (voxlat, cayley, divergence, magicdiv); v_D=0",
       "brief written; P45 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:membrane", "READ", "membrane",
       "P46: FP-ROW's live test - role-reading C-FLOOR ('advisory' as the recirc/ashdepth shape) vs "
       "row-reading C-INV (a -law row carrying a positive structural law, 'unable to starve')",
       "C-EQ, PRICED FOURTH AT 12, AND NEITHER PRE-DECLARED READING WAS RIGHT - membrane-law: EVERY "
       "LAWFUL MEMBRANE PRODUCES THE IDENTICAL ADMITTED SET, decided against NINE including reversed, "
       "both-ends-interleaved adversarial, and one that puts a chosen obligation last every time to "
       "STARVE it, so an adaptive layer changes how efficiently truth is reached and never what truth "
       "is. The same-quantity-under-nine-orderings shape is commuteprop's and mesh's, both C-EQ; "
       "'advisory' is the CONSEQUENCE of the invariance and 'unable to starve' its non-vacuity "
       "witness, neither being the law. membrane-selftest refuses three plants EACH WITH ITS OWN NAME - "
       "the filtering membrane DROPS obligations, named as the accelerator's characteristic failure "
       "since silently discarding what you cannot handle looks exactly like handling it. FP-ROW's "
       "OUTCOME SPACE WAS INCOMPLETE: not falsified (the role-reading did not win) and not correct "
       "(not the row-reading either) - the L60 failure P3's meta suffered, recurring at a new level, "
       "since the prediction assumed the true class must be one of the two readings on offer; v_D=0",
       "brief written; P46 resolved C-EQ in exe_epistemics/PREDICTIONS.md; the frozen FP-ROW text "
       "STANDS and the successor freeze must carry a mandatory NEITHER-READING branch, exactly as P4 "
       "carried R3",
       "CONFIRMATION"),
    _d("read:meshattest", "READ", "meshattest",
       "P47 (run 14 closes): FP-ROW discriminating - role-reading C-R (an attestation admits or "
       "refuses) vs row-reading C-EQ (the arc's attestation pattern is an equivalence across a real "
       "transport), classified from meshattest:laws, the row the FROZEN FALLBACK named before any "
       "content was read since this module has NO <module>-law row",
       "C-EQ - FP-ROW'S FIRST GENUINE WIN, the row-reading beating the role-reading on a joint where "
       "they differed. meshattest:laws: the synthetic handoff (A->B, usurper refused, disjoint region "
       "untouched) and the relay (A->B->C custody chain, mid-chain usurper refused) each REPLAY LAWFUL "
       "UNDER THE UNMODIFIED MIGRATE LAW, deterministically, and THE MIGRATION CERTIFICATE THE CHECKER "
       "RE-MINTS MATCHES REALITY'S RECORD - the law is not adapted for the real transport, the real "
       "transport is shown to satisfy it already. meshattest:forges under one principle, REALITY MAY "
       "NOT OVERRULE THE LAW: seven attacks each refusing typed. A second TRUE-CONFORMANCE-GAP module "
       "EXPLAINED rather than listed (after view_witness): an attestation whose subject is a live "
       "socket run cannot have its evidence pinned in advance without ceasing to be an attestation, so "
       "the missing corpus is a consequence of what the module IS, not a debt; v_D=0",
       "brief written; P47 resolved C-EQ in exe_epistemics/PREDICTIONS.md; run 14 closes on a sixth "
       "consecutive triple zero, meta 44/44, leading calls 2/3, and FP-ROW scores one "
       "NON-DISCRIMINATING / one CORRECT / one NEITHER - PARTIALLY SUPPORTED, its directional claim "
       "(role never beats row) standing at 1-for-1 while its precision failed on membrane",
       "CONFIRMATION"),
    _d("read:meshsession", "READ", "meshsession",
       "FP-ROW's directional claim that where the ROLE-reading and the ROW-reading differ, the ROW "
       "wins - declared role C-AB (a capstone composes, the panelight/panewire shape) vs row C-EQ "
       "(Phase M had resolved C-EQ twice running at mesh and meshattest)",
       "C-AB - THE ROLE-READING WON, so FP-ROW's DIRECTIONAL CLAIM IS FALSIFIED by its own frozen "
       "terms. meshsession:sessions: concurrency (M1), migration (M2) and a partition episode (M4) "
       "COMPOSED into one attested timeline, the campaign and skirmish multi-authority playthroughs "
       "reproducing checkpoint-chain digests deterministically - the distinctive claim is the "
       "COMPOSITION, not that each law holds. meshsession:forges carries meshattest's principle "
       "forward (reality may not overrule the COMPOSED mesh law on any axis) with five forgeries "
       "refusing. The five-batch pattern that motivated FP-ROW does NOT generalize; one counter- "
       "instance ends a claim stated that strongly. LADDER DEFECT recorded because the selection was "
       "load-bearing: the frozen ladder excludes rows NAMED :scenes, but meshsession:sessions IS this "
       "module's scenes row under another name - it excludes by NAME where it meant to exclude by "
       "ROLE. Applied AS FROZEN anyway, since a ladder rewritten after seeing which row flatters the "
       "prediction is not a ladder; a corrected ladder would have reached :forges, plausibly C-R. "
       "Leading call missed by four (C-EQ 34 vs C-AB 30); v_D=0",
       "brief written; P48 resolved C-AB in exe_epistemics/PREDICTIONS.md; the ladder defect is the "
       "SUCCESSOR's obligation, not this rung's licence to re-pick",
       "CONFIRMATION"),
    _d("read:patience", "READ", "patience",
       "P49 (NON-SCORING, contamination declared at the freeze under the P33 rule): auditgraph's sale "
       "that pricing equivocation at kappa converts an INVISIBLE INTEGRITY attack into a VISIBLE "
       "AVAILABILITY one",
       "patience-law: every word of that trade rests on 'visible', WHICH BOTH auditgraph AND splitview "
       "DECLARED RATHER THAN ESTABLISHED. Chandra-Toueg is the reason - a crashed process and an "
       "arbitrarily slow one are indistinguishable to an asynchronous observer - so a server that "
       "STALLS rather than excludes takes the same partition at a VISIBLE COST OF ZERO; the exclusion "
       "ladder holds only at T >= Delta and below the envelope 1/2/infinity collapses to 0/0/0. "
       "patience-selftest names a class this repo had no cell for: LINEAR patience growth is SOUND (it "
       "terminates, and the test asserts it) and LOSES ON PRICE ALONE - 63 false alarms where doubling "
       "costs 6, 199 against 8 at Delta/T0 = 200 - so a correct alternative rejected purely on cost is "
       "a different refutation from a wrong one. This is the ashdepth/recirc/divergence refutation "
       "shape aimed at a SIBLING RUNG rather than at handed-down literature, the first such instance. "
       "Scores nothing: no census, no meta, no FP-ROW entry",
       "brief written; P49 recorded NON-SCORING in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:predict", "READ", "predict",
       "P50 (run 15 closes): FP-ROW discriminating - role C-R ('reconcile' as adjudicating a client "
       "claim) vs row C-EQ, with the freeze DISCLOSING that the row name leaks its class so this is a "
       "weaker test than P48",
       "C-EQ (leading credence 46 CORRECT; FP-ROW = ROW at the reduced weight the freeze declared) - "
       "predict-equivalence: reconstruct == drive(auth) for every prediction, and the sharper half, "
       "THE REUSABLE PREFIX IS BIT-IDENTICAL TO THE AUTHORITY so PARTIAL ROLLBACK == FULL "
       "RE-SIMULATION - the optimization that makes prediction affordable proven equal to the "
       "exhaustive alternative, which is exactly the claim an implementation is most tempted to "
       "assume. predict-localize: reconcile IS lockstep.first_desync, a correct prediction needs no "
       "rollback, and a DIFFERENT-INPUT SAME-POSE prediction needs none either - the reconcile is "
       "POSE-level not input-level, so a client that reached the right place by a different route is "
       "not punished for the route, which is what splice's memorylessness needs downstream; v_D=0",
       "brief written; P50 resolved C-EQ in exe_epistemics/PREDICTIONS.md; run 15 closes with no new "
       "family (the seventh consecutive), meta 46/46. FP-ROW v2 FINAL: directional claim FALSIFIED "
       "(P48), precision one NEITHER (P46), two wins one of them weakened by a leaking row name - the "
       "instrument was built to be falsifiable and was falsified in two rungs, which beats a third "
       "confirmation because the alternative was carrying an unfrozen five-batch grievance "
       "indefinitely. What survives is narrower and true: role prose and central rows disagree often "
       "enough to be worth declaring separately and NEITHER dominates. FP-ROW is RETIRED under L63, "
       "irreversibly, and may not be reinstated by adjusting its wording",
       "CONFIRMATION"),
    _d("rung6:ladder-repair", "DERIVE", "the fallback ladder",
       "P48's defect: the ladder excluded reference rows by NAME (:scenes) where it meant to exclude "
       "them by ROLE, wrongly selecting meshsession:sessions as a central row",
       "REPAIRED BEFORE THE NEXT READ, by a structural content-free signature: a reference/scenes row "
       "is recorded TWICE in its gate method (once in the except branch, once in the success branch). "
       "Verified across every module read - magicdiv:scenes, predict:scenes, provbind:scenes, "
       "quintessence:scenes, sea:island, sea:wide and meshsession:sessions all record twice, while "
       "meshattest:laws, predict-equivalence and magicdiv-law record once - so the signature separates "
       "them exactly while reading the SHAPE of the gate method, never a row's content. IT CHANGED THE "
       "BATCH: the old ladder would have selected the reference row sea:island; the repaired one "
       "selects sea-conservation",
       "ladder v2 recorded in the batch-15 freeze; the successor obligation P48 created is discharged",
       "CORRECTION", ""),
    _d("read:provbind", "READ", "provbind",
       "P51 (batch 15): whether a role line saying 'bound to its lattice, OR REFUSED' predicts an "
       "admission predicate",
       "C-R (leading credence 42 CORRECT) - provbind-law: the certificate is BOUND to the geometry by "
       "H(cert | lattice_digest) with the lattice digest RECOMPUTED AT SERVE TIME, so THE BINDING "
       "CANNOT BE ASSERTED BY WHOEVER SUPPLIED IT, and every carried field including the capture-time "
       "buffer distance enters the digest. provbind-selftest: the metadata-only digest - THE "
       "HANDED-DOWN FORM - matches a DIFFERENT block's geometry, so a permissive certificate lifted "
       "off a public-domain block and stapled to a restricted capture is ADMITTED; the inherited design "
       "admits exactly the attack the layer exists to stop. Recompute-rather-than-trust is the "
       "neutral-ruler pattern's EIGHTH instance, and grade-what-you-inherit its fourth; v_D=0",
       "brief written; P51 resolved C-R in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:quintessence", "READ", "quintessence",
       "P52: that a REPRESENTATION THEOREM's central row certifies the equivalence it enables (C-EQ "
       "38) rather than the representation itself (C-REP 26)",
       "C-REP, leading call MISSED - quintessence-essence: the extractor is TOTAL and DETERMINISTIC "
       "over the five families with FULL-TUPLE INJECTIVITY, so nothing that distinguishes two records "
       "is discarded; within a family history and validity are the SAME ADDRESS AT A SCOPE (the RAN-0 "
       "rebinding, visible in the tuple) and the scope difference PREDICTS the transport theorem. The "
       "equivalence IS there - quintessence-lineage has heads in BIJECTION with lineages, the lineage "
       "being the equivalence class not the path - but in a SEPARATE row: the arc splits "
       "representation from the equivalence it enables. quintessence-refuse adds the FIVE-AXIS "
       "CONSERVATION ABLATION: degrade any ONE axis (parent/region/height/currency/byte) and admission "
       "refuses, so the conservation is not a conjunction anyone can partially satisfy; v_D=0",
       "brief written; P52 resolved C-REP in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:sea", "READ", "sea",
       "P53 (run 16 closes): the conservation reading, DISCLOSED IN ADVANCE as an easy call since the "
       "row is named sea-conservation and the name leaks its class",
       "C-INV (leading credence 44 correct, scored at the reduced weight the freeze declared) - "
       "sea-conservation: total mass EXACT across 40 masked ticks AND THE FIELD GENUINELY MOVED, the "
       "second clause being L61's non-vacuity witness against a frozen field satisfying conservation "
       "trivially; sea-coast has land identically zero and an all-sea mask BIT-FOR-BIT identical to the "
       "frozen step; sea-selftest makes the mask load-bearing. THE FINDING: THE ARC ALREADY HAS A "
       "MARANGONI LAW - sea-marangoni certifies mass EXACT + monotone 30/30 ticks (AUDITED, NOT "
       "ESTIMATED) + THE PEAK PERSISTS ABOVE PURE DIFFUSION + land dry, surface tension on the masked "
       "domain, the peak clause being the Marangoni signature proper. A substantial part of the "
       "URDRMRG1 proposal authored earlier this session ALREADY EXISTS, gated - the strongest argument "
       "yet for finishing the READ pass before proposing new theory, since the proposal was written "
       "against an incomplete map of what was already built. sea-marangoni-selftest plants the sharp "
       "case: an over-bound kappa that overshoots negative YET CONSERVES MASS, so a defect satisfying "
       "the headline invariant would pass a conservation-only check - AN INVARIANT A DEFECT CAN SATISFY "
       "IS NOT SUFFICIENT EVIDENCE, the same reasoning as magicdiv's powers-of-two multiplier and "
       "divergence's identical-rate perturbations, now on a physical bound; v_D=0",
       "brief written; P53 resolved C-INV in exe_epistemics/PREDICTIONS.md; run 16 closes on a triple "
       "zero, the eighth consecutive run with no new family, meta 49/49, leading calls 2/3",
       "CONFIRMATION"),
    _d("read:sealframe", "READ", "sealframe",
       "P54 (batch 16): that a SEALED frame is something POLICED (C-R 32) rather than certifying an "
       "identity - and that a renderer's cost model necessarily sits beside the code that pays it",
       "C-EQ, leading call MISSED - sealframe-envelope: the op envelope IS the loop's ACTUAL work, "
       "micro-steps == the glide trajectory's own count, MODEL == EXECUTION, so the budget cannot "
       "drift from the thing it budgets; sprint costs EXACTLY twice the walk and the envelope FITS the "
       "60Hz budget under the measured native tick rate. THE FINDING: sealframe-honesty turns this "
       "repository's own CLAIM-GRADING LADDER into a gate row - every MEASURED frame-budget entry must "
       "cite a NAMED-HOST log (the unlogged-MEASURED defect is caught), input->photon stays "
       "NOT_MEASURED until a section-3 run exists, and a host log GRADUATES a claim to MEASURED only "
       "when it NAMES a host AND its input->photon is under target, with the selftest refusing a "
       "tampered log on its self-digest and refusing an anonymous log the graduation. The discipline "
       "the entire arc is written under is here ENFORCED BY THE GATE rather than by the author's care "
       "- everywhere else the ladder is a convention prose obeys, in this module it is a row that "
       "reddens; the strongest instance of attestation != authority made executable; v_D=0",
       "brief written; P54 resolved C-EQ in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:sealsession", "READ", "sealsession",
       "P55: whether the visible-world CAPSTONE certifies a lawfulness admission (the row is named "
       "-lawful) or COMPOSITION - with the prior transferred from resolved P48 and DISCLOSED",
       "C-AB (leading credence 34 CORRECT) - sealsession-lawful: a genuine movement session, a wired "
       "session (live edits + streaming) and a multiplayer session (ghost stream) each REPLAY THROUGH "
       "THE UNMODIFIED loop, wire and ghost laws TO THEIR OWN RECORDED WITNESSES, the whole visible "
       "world attested in one trace, deterministically. sealsession-forge refuses a forged avatar / "
       "world / ghost witness and a cheater's MALICE-CLAIMED EDIT (an illegal edit dressed as "
       "admitted). CROSS-JOINT TRANSFER PAID here having COST at P38, so the practice now stands at 1 "
       "hurt / 1 helped - the honest state of it, not a vindication. BOTH capstones certify "
       "COMPOSITION rather than a new mechanism and phrase it identically (laws UNMODIFIED, composed "
       "into ONE attested trace): a capstone in this arc is the claim that existing laws do not "
       "interfere; v_D=0",
       "brief written; P55 resolved C-AB in exe_epistemics/PREDICTIONS.md", "CONFIRMATION"),
    _d("read:sealwrit", "READ", "sealwrit",
       "P56 (run 17 closes): the role states WHO may write x WHAT may change, literally naming two "
       "dimensions, which is C-AB's signature (priced 30) against the provenance-as-admission reading",
       "C-R (leading credence 36 CORRECT) - sealwrit-provenance: an unregistered, wrong-keyed, "
       "mis-signed or tail-collision-forged writ REFUSES BEFORE THE STATE LAW with replica and ledger "
       "BYTE-IDENTICAL, and the genuine writ still admits - A FAILED SIGNATURE BLOCKS NOTHING HONEST; "
       "the plant is pointed, the first-byte defect verifier ACCEPTS the forgery the real one refuses. "
       "THE ORDERING IS THE THEOREM: sealwrit-order proves ELIGIBILITY PRECEDES ADMISSION (a writ both "
       "mis-signed and state-unlawful refuses SEAL, since a state-first system would report the other "
       "code), A SIGNATURE CANNOT LAUNDER STATE (a perfectly signed stale record refuses WIRE), and "
       "ELIGIBILITY IS CONSUMED BY ADMISSION NEVER BY ATTESTATION - closing the attack of presenting a "
       "writ, having it refused on state, and treating the signature as spent-and-verified. So WHO x "
       "WHAT is real but NOT a two-law join: the axes are kept in a strict ORDER with a proof the "
       "order holds. sealwrit-reuse: the first admission SEALS THE KEYPAIR TO ITS DIGEST, so an "
       "identical redelivery rides free to the CAS while a verified-DISTINCT state-lawful record under "
       "a sealed keypair refuses on the ledger - the reuse leak's exact exploit contained; v_D=0",
       "brief written; P56 resolved C-R in exe_epistemics/PREDICTIONS.md; run 17 closes on a triple "
       "zero, the ninth consecutive run with no new family, meta 52/52, leading calls 2/3",
       "CONFIRMATION"),
)


def provenance_problems(row_names, records=None):
    """Each discovery record checked. Returns a list of (id, kind, got, want) problems.

    (1) `operator` in OPERATORS; (2) `permanence` in PERMANENCE; (3) an ELIMINATION or MECHANISM must
    name an `enforces` row that is LIVE this run — the class it claims to forbid has a living
    forbidder, or the claim is refused; (4) any non-empty `enforces` must be a live row (no citing a
    dead gate). `records` defaults to DISCOVERIES; the self-test injects a bad record."""
    records = DISCOVERIES if records is None else records
    out = []
    for d in records:
        i = d.get("id", "?")
        if d.get("operator") not in OPERATORS:
            out.append((i, "operator", str(d.get("operator")), "OPERATORS")); continue
        if d.get("permanence") not in PERMANENCE:
            out.append((i, "permanence", str(d.get("permanence")), "PERMANENCE")); continue
        enf = d.get("enforces", "")
        if d["permanence"] in ("ELIMINATION", "MECHANISM") and not enf:
            out.append((i, "unenforced", d["permanence"], "a live enforcing row")); continue
        if enf and enf not in row_names:
            out.append((i, "dead-enforcer", enf, "a live row")); continue
    return out


def distribution():
    """The operator x permanence census — the measurable this rung exists to produce."""
    byop = collections.Counter(d["operator"] for d in DISCOVERIES)
    byperm = collections.Counter(d["permanence"] for d in DISCOVERIES)
    return {"n": len(DISCOVERIES),
            "by_operator": dict(sorted(byop.items())),
            "by_permanence": dict(sorted(byperm.items()))}


def plants_bite(row_names):
    """RED-FIRST: the check must bite in each independent direction or a clean provenance means
    nothing (L23). Each planted against a single synthetic record:
      (1) an ELIMINATION whose enforcing row is DEAD  -> dead-enforcer;
      (2) a MECHANISM with NO enforcing row            -> unenforced;
      (3) a bad operator                               -> operator;
      (4) a bad permanence                             -> permanence.
    Returns True iff every direction reddens."""
    base = dict(DISCOVERIES[0])
    mk = lambda **kw: [dict(base, **kw)]
    d1 = any(p[1] == "dead-enforcer" for p in provenance_problems(
        row_names, mk(permanence="ELIMINATION", enforces="no-such-row-000")))
    d2 = any(p[1] == "unenforced" for p in provenance_problems(
        row_names, mk(permanence="MECHANISM", enforces="")))
    d3 = any(p[1] == "operator" for p in provenance_problems(row_names, mk(operator="NONSENSE")))
    d4 = any(p[1] == "permanence" for p in provenance_problems(row_names, mk(permanence="MAYBE")))
    return d1 and d2 and d3 and d4
