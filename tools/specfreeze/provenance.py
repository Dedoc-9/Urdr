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
