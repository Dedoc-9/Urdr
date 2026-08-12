# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""pedigree — A CLAIM MAY ONLY CONSUME AN ARTIFACT WHOSE PROVENANCE IS ADMISSIBLE, AND THE ARTIFACT
IS ITS OWN PRIMARY WITNESS (URDRPDG1).

`attest` proves a record is INTERNALLY TRUSTWORTHY: the bytes seal, the plan digest binds, the host
declared its conditions, the format is one this tree can read. It takes on faith that the HARNESS
which produced those bytes was one whose known defects had already been repaired — and that faith is
not idle. Rebuild the graduated record under the PRE-`confound` schedule, changing nothing but `pos`,
re-seal it, and every check `attest` makes passes: the seal verifies, the plan binds, it grades
MEASURED, and `measure.admit_claim` accepts the claim built from it. The record was produced by the
exact instrument defect URDRCNF1 exists to catch, and it graduates.

That is not hypothetical. This tree produced two such logs and both graded MEASURED at the time —
one under the confounded schedule, one from a single execution.

    A RECORD'S INTEGRITY IS NOT ITS PROVENANCE.

THE LAW, and its ORDER is the design rather than an implementation detail:

    ADMISSIBILITY IS DERIVED FROM THE ARTIFACT WHEREVER THE ARTIFACT CAN SHOW IT, AND ONLY THEN
    FROM WHAT THE ARTIFACT DECLARES ABOUT ITSELF.

A retired-fingerprint blacklist as the PRIMARY mechanism would be the same inherited state this tree
keeps removing: every newly-found defect would need somebody to remember to add an old digest. So the
hierarchy is explicit and checked in this order:

    A. DERIVED   — the schedule the rows actually record, the execution count they actually contain,
                   the plan digest, the fields the format requires. Computed from the bytes.
    B. IDENTITY  — the instrument fingerprint the record carries, when it carries one.
    C. REGISTRY  — retired fingerprints. AN ESCAPE HATCH, for defects that CANNOT be reconstructed
                   from the artifact, and it is currently EMPTY because every defect this tree has
                   found so far is derivable. That emptiness is a claim, and a plant proves the
                   mechanism would bite if it were not.

IDENTITY IS NOT REQUIRED, AND UNIDENTIFIED IS NOT REFUSED. The graduated record is a v1 log written
before any harness carried a fingerprint. Refusing it would make this rung's first act the retraction
of the measurement it was built to protect, on a technicality about metadata rather than about the
experiment. So a record that cannot say what produced it is judged on its DERIVED evidence alone,
and reports that it could not say — the same shape as `deeper`'s NOT_ASKED, and the same reason.

`does_not_show` — and this bound is sharper than it looks. THE RECORD IS A WITNESS, NOT A NOTARY.
`pos` records the order the runner claims it used; nothing binds it to when a row was actually taken.
Re-seal a doctored ordering and the schedule check passes, because the check reads what the artifact
says about itself. Detecting THAT needs the structure to be reproducible from the plan rather than
merely plausible, which is `rehearse` (URDRRHS1) and lands beside this. AND THE WIDER BOUND: this is a
FLOOR OVER DEFECTS THIS TREE HAS ALREADY PAID FOR. It cannot see a defect nobody has found yet, and
"known historical defects are covered" is not "the instrument is proven correct".

WHERE THE LIVE ARTIFACT IS GRADED, AND WHY NOT HERE. The scenes pin BEHAVIOUR on fixtures built as
plain dicts, and the COMMITTED record — with the re-sealed pre-`confound` counterexample derived from
it — is graded at the gate, where `attest` already lives. That split is not tidiness: reaching for
`attest` from this module put it at import-depth 14 against a ceiling clause (b) binds to the
enumerated chain at the seal, and that ceiling is a measurement rather than a budget.

GRADE (honest, D5): MEASURED — a record carrying the shipped confounded schedule is REFUSED naming
it, while a balanced one is ADMISSIBLE; a record with too few executions is refused under a
DIFFERENT name; an omitted input is SKIPPED rather than treated as passing; derived evidence
outranks a good fingerprint; UNIDENTIFIED is reported without being punished; and a planted
retirement bites. THE LIVE COUNTEREXAMPLE — the committed artifact re-sealed under the shipped
schedule, admissible to `attest` and refused here — is asserted at the gate. DECLARED: the
registry's membership, currently empty, and that identity is advisory rather than required."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

# THIS MODULE IMPORTS ONLY LEAVES, AND THE LATTICE IS WHY — FOR THE THIRD TIME IN THIS ARC. The
# first draft reached for `attest` to fetch the committed record and for `rollbench` to fetch the
# plan digest, which put it at import-depth 14 against a sealed ceiling of 13, and clause (b) binds
# that ceiling to the ENUMERATED chain at the seal: it is a measurement, not a budget, so it does
# not move to admit the module that just failed it. The proof was right about more than depth. A
# DETECTOR SHOULD BE HANDED WHAT IT GRADES RATHER THAN IMPORT THE WORLD TO FETCH IT — `confound`
# learned this, and the same shape applies here. The record, the plan digest and the field table
# arrive as ARGUMENTS; the caller that owns them supplies them, the scenes pin behaviour on
# fixtures, and the LIVE artifact is graded at the gate where `attest` already lives.
import confound as CF                                      # noqa: E402
import repeat as RP                                        # noqa: E402

MAGIC = b"URDRPDG1"

ADMISSIBLE = "ADMISSIBLE"
REFUSED = "REFUSED"
UNIDENTIFIED = "UNIDENTIFIED"
OUTCOMES = (ADMISSIBLE, REFUSED, UNIDENTIFIED)

#: THE ESCAPE HATCH, AND IT IS EMPTY ON PURPOSE. fingerprint -> (defect, why it is not derivable).
#: A blacklist as the PRIMARY mechanism would be inherited state: every new defect would need
#: somebody to remember an old digest. Every defect this tree has found so far IS derivable from the
#: artifact, so nothing is listed — and a plant proves the mechanism would bite if something were.
RETIRED_INSTRUMENTS = {}


class PedigreeError(Exception):
    def __init__(self, message):
        super().__init__(f"PEDIGREE-REFUSE: {message}")
        self.code = "PEDIGREE-REFUSE"


# ---- A. derived from the artifact ------------------------------------------------------------------
def recorded_schedule(parsed, run=None):
    """THE ORDER THE ROWS ACTUALLY RECORD, rebuilt from `pos`. Not the order the harness's current
    code would produce — the order this artifact says it used."""
    runs = sorted({int(r["run"]) for r in parsed["rows"]})
    if not runs:
        raise PedigreeError("the record contains no rows")
    pick = runs[0] if run is None else run
    mine = [r for r in parsed["rows"] if int(r["run"]) == pick]
    order = [None] * len(mine)
    for r in mine:
        i = int(r["pos"])
        if not 0 <= i < len(mine) or order[i] is not None:
            raise PedigreeError(f"run {pick} has a duplicate or out-of-range position {i} — a "
                                f"record whose positions are not a permutation cannot report an "
                                f"order at all")
        order[i] = (r["representation"], r["workload"], int(r["depth"]))
    return tuple(order)


def derived_faults(parsed, plan_digest=None, fields=None):
    """Every admissibility failure the ARTIFACT ITSELF demonstrates, each NAMED. A refusal without a
    named cause is an opinion, and the caller is handed the causes rather than a boolean.

    `plan_digest` and `fields` are supplied by whoever owns the plan and the format table. Omitted,
    those two checks are SKIPPED rather than assumed to pass — a detector that silently treats a
    missing input as a passing one is the vacuity this tree keeps removing."""
    faults = []
    runs = sorted({int(r["run"]) for r in parsed["rows"]})
    if len(runs) < RP.MIN_EXECUTIONS:
        faults.append(("too-few-executions",
                       f"{len(runs)} execution(s) against a minimum of {RP.MIN_EXECUTIONS}: the "
                       f"between-execution spread does not exist, so no difference in this record "
                       f"can be claimed at all (URDRRPT1)"))
    for run in runs:
        try:
            order = recorded_schedule(parsed, run)
        except PedigreeError as exc:
            faults.append(("unreadable-order", f"run {run}: {exc}"))
            continue
        for axis in CF.AXES:
            v = CF.verdict(order, axis)
            if v != CF.BALANCED:
                faults.append((f"schedule-{v.lower()}",
                               f"run {run}: the {axis} axis reads {v} in the order this record "
                               f"itself carries — a factor correlated with run position is not "
                               f"measured, it is confounded (URDRCNF1)"))
    if plan_digest is not None and parsed.get("plan") != plan_digest:
        faults.append(("plan-mismatch",
                       "the record's plan digest is not this tree's: its cells were chosen under "
                       "terms that are no longer the ones a claim would be graded against"))
    if fields is not None:
        for r in parsed["rows"][:1]:
            missing = [f for f in fields if f not in r]
            if missing:
                faults.append(("incomplete-rows", f"rows lack {', '.join(missing)} for "
                                                  f"{parsed.get('version', '?')}"))
    return tuple(faults)


# ---- B. what the artifact declares about itself ----------------------------------------------------
def identity(parsed):
    """The instrument fingerprint, or UNIDENTIFIED. A record written before any harness carried one
    cannot say, and that is reported rather than punished: refusing it would make this rung's first
    act the retraction of the measurement it exists to protect, over metadata rather than the
    experiment."""
    fp = str(parsed.get("harness", "")).strip()
    return fp or UNIDENTIFIED


# ---- the verdict -----------------------------------------------------------------------------------
def verdict(parsed, plan_digest=None, fields=None):
    """ADMISSIBLE or REFUSED, with the causes available from `derived_faults` and `identity`."""
    if derived_faults(parsed, plan_digest, fields):
        return REFUSED
    fp = identity(parsed)
    if fp != UNIDENTIFIED and fp in RETIRED_INSTRUMENTS:
        return REFUSED
    return ADMISSIBLE


def report(parsed, plan_digest=None, fields=None):
    fp = identity(parsed)
    faults = derived_faults(parsed, plan_digest, fields)
    retired = RETIRED_INSTRUMENTS.get(fp) if fp != UNIDENTIFIED else None
    return {"verdict": REFUSED if (faults or retired) else ADMISSIBLE,
            "identity": fp,
            "derived_faults": tuple(n for n, _w in faults),
            "retired": bool(retired)}


# ---- fixtures: parsed records as DICTS, so no plan or artifact needs importing ---------------------
def _cells():
    """A plan-shaped cell list. Same SHAPE as the live one (3 x 4 x 7) so the schedule transfers."""
    return tuple((r, w, d) for r in ("A", "B", "C")
                 for w in ("w0", "w1", "w2", "w3") for d in (1, 2, 4, 8, 16, 32, 64))


def _record(order_of, runs=2, version="v1", **extra):
    """A parsed record, built directly. `order_of` maps a cell to its run position, so a fixture can
    carry ANY schedule — the balanced one, the shipped confounded one, or a doctored permutation."""
    cells = _cells()
    rows = []
    for run in range(runs):
        for c in cells:
            rows.append({"representation": c[0], "workload": c[1], "depth": c[2],
                         "run": run, "pos": order_of(c), "p50_ns": 1000 + order_of(c)})
    out = {"rows": rows, "plan": "PLAN", "version": version}
    out.update(extra)
    return out


def a_balanced_record(runs=2, **extra):
    sched = CF.schedule(_cells())
    pos = {c: i for i, c in enumerate(sched)}
    return _record(lambda c: pos[c], runs=runs, **extra)


def a_confounded_record(runs=2, **extra):
    """THE SHIPPED DEFECT'S SHAPE: the plan's own nesting, representation-outermost."""
    pos = {c: i for i, c in enumerate(_cells())}
    return _record(lambda c: pos[c], runs=runs, **extra)


# ---- the laws ---------------------------------------------------------------------------------------
def a_balanced_record_is_admissible():
    """NON-VACUITY FIRST. A provenance law that refused a well-formed record would be a wall rather
    than a door, and every refusal below would prove nothing."""
    return verdict(a_balanced_record()) == ADMISSIBLE


def the_shipped_schedule_is_refused():
    """THE COUNTEREXAMPLE'S SHAPE. A record whose order is the plan's own nesting — the order
    `rollbench` actually shipped, and the one that produced this tree's first two host logs — is
    REFUSED, naming the schedule. The LIVE instance of this, built from the committed artifact and
    re-sealed so that `attest` accepts it, is asserted at the gate where the artifact lives."""
    p = a_confounded_record()
    names = [n for n, _w in derived_faults(p)]
    return verdict(p) == REFUSED and any(n.startswith("schedule-") for n in names)


def the_two_historical_defects_refuse_by_different_names():
    """A detector reporting one cause for two defects has fused them. The confounded schedule and
    the single execution are different findings and are named differently."""
    a = [n for n, _w in derived_faults(a_confounded_record())]
    b = [n for n, _w in derived_faults(a_balanced_record(runs=1))]
    return ("too-few-executions" in b and not any(n.startswith("schedule-") for n in b)
            and any(n.startswith("schedule-") for n in a)
            and "too-few-executions" not in a)


def every_refusal_names_a_cause():
    """A refusal without a named cause is an opinion. Each fault carries a code AND a sentence
    explaining what the artifact demonstrated."""
    for p in (a_confounded_record(), a_balanced_record(runs=1)):
        for name, why in derived_faults(p):
            if not name or not str(why).strip():
                return False
    return True


def derived_evidence_outranks_declared_identity():
    """THE HIERARCHY, ASSERTED RATHER THAN DOCUMENTED. A record carrying a perfectly good
    fingerprint is still REFUSED when its own rows demonstrate a defect — otherwise the registry
    would be the foundation and the artifact an afterthought."""
    p = a_confounded_record(harness="a-fingerprint-nobody-has-retired")
    return identity(p) != UNIDENTIFIED and verdict(p) == REFUSED


def unidentified_is_not_refused():
    """A record predating any harness fingerprint is judged on derived evidence and SAYS it could
    not identify itself — the same shape as `deeper`'s NOT_ASKED, for the same reason: 'could not
    say' and 'said something wrong' are different findings."""
    r = report(a_balanced_record())
    return r["identity"] == UNIDENTIFIED and r["verdict"] == ADMISSIBLE


def a_planted_retirement_bites():
    """THE ESCAPE HATCH, PROVED TO WORK WHILE EMPTY. The registry lists nothing because every defect
    found so far is derivable; plant one and a record carrying that fingerprint is refused."""
    p = a_balanced_record(harness="planted-defective-harness")
    real = dict(RETIRED_INSTRUMENTS)
    try:
        RETIRED_INSTRUMENTS["planted-defective-harness"] = (
            "a defect that leaves no trace in the rows", "not derivable from the artifact")
        return verdict(p) == REFUSED and report(p)["retired"]
    finally:
        RETIRED_INSTRUMENTS.clear()
        RETIRED_INSTRUMENTS.update(real)


def the_registry_is_empty_and_that_is_a_claim():
    """DECLARED, and checkable. Emptiness here is the STRONGEST form of the hierarchy — it says
    every defect this tree has paid for is visible in the artifact — so it is asserted rather than
    left to be noticed, and an entry added later must carry why it is not derivable."""
    return (len(RETIRED_INSTRUMENTS) == 0
            and all(len(v) == 2 and all(str(x).strip() for x in v)
                    for v in RETIRED_INSTRUMENTS.values()))


def a_missing_input_is_skipped_not_passed():
    """A detector that treats an ABSENT input as a passing check is vacuous. Omit the plan digest
    and the plan check does not run; supply a wrong one and it refuses."""
    p = a_balanced_record()
    return (verdict(p) == ADMISSIBLE
            and verdict(p, plan_digest="a-different-plan") == REFUSED
            and "plan-mismatch" in [n for n, _w in
                                    derived_faults(p, plan_digest="a-different-plan")])


def a_record_whose_positions_are_not_a_permutation_refuses():
    """`pos` must be a permutation of the run's rows or it reports no order at all — a duplicate
    position is not a schedule with a small error in it."""
    p = a_balanced_record(runs=1)
    p["rows"][1]["pos"] = p["rows"][0]["pos"]
    try:
        recorded_schedule(p)
        return False
    except PedigreeError:
        return True


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("verdicts", "hierarchy")


def scene_case(name):
    if name == "verdicts":
        return "balanced=%s|shipped=%s|apart=%s|named=%s|perm=%s|skip=%s" % (
            a_balanced_record_is_admissible(), the_shipped_schedule_is_refused(),
            the_two_historical_defects_refuse_by_different_names(), every_refusal_names_a_cause(),
            a_record_whose_positions_are_not_a_permutation_refuses(),
            a_missing_input_is_skipped_not_passed())
    if name == "hierarchy":
        return "derived>identity=%s|unident=%s|planted=%s|empty=%s||%s||%s" % (
            derived_evidence_outranks_declared_identity(), unidentified_is_not_refused(),
            a_planted_retirement_bites(), the_registry_is_empty_and_that_is_a_claim(),
            sorted(report(a_balanced_record()).items()),
            sorted(report(a_confounded_record()).items()))
    raise PedigreeError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def pedigree_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_pedigree.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PedigreeError(f"no golden named {name!r}")


if __name__ == "__main__":
    print("balanced record admissible  :", a_balanced_record_is_admissible())
    print("shipped schedule refused    :", the_shipped_schedule_is_refused())
    print("two defects, two names      :", the_two_historical_defects_refuse_by_different_names())
    print("every refusal names a cause :", every_refusal_names_a_cause())
    print("derived outranks identity   :", derived_evidence_outranks_declared_identity())
    print("UNIDENTIFIED is not refused :", unidentified_is_not_refused())
    print("planted retirement bites    :", a_planted_retirement_bites())
    print("registry empty, as a claim  :", the_registry_is_empty_and_that_is_a_claim())
    print("missing input is skipped    :", a_missing_input_is_skipped_not_passed())
    print("bad permutation refuses     :", a_record_whose_positions_are_not_a_permutation_refuses())
    print()
    print("  balanced   :", report(a_balanced_record()))
    print("  confounded :", report(a_confounded_record()))
    for n in SCENES:
        print(n, scene_result(n))
    print("pedigree", pedigree_digest())
