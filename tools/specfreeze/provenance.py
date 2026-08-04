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
