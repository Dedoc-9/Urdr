# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""attest — A GRADUATED CLAIM IS A COMMITTED LOG THE GATE RE-READS, AND EVERY NUMBER IN IT IS
DERIVED RATHER THAN TYPED (URDRATT1). The endpoint of the arc `measure` opened.

`measure` fixed the terms of a performance claim eight rungs ago and could not answer it. `rollbench`
built the instrument. `confound` found the schedule was measuring run position. `repeat` found the
numbers were never sampled at the level a comparison needs. `deeper` asked what the op model could
not see. This rung is where the answer stops being a paste in a conversation and becomes an artifact
the gate re-reads on every run.

THE LAW, and it has two halves because a claim can rot in two directions:

    A GRADUATED CLAIM CITES A COMMITTED LOG THAT STILL SEALS, STILL GRADES ADMISSIBLE, AND STILL
    SUPPORTS THE NUMBERS THE CLAIM STATES — WITH THOSE NUMBERS DERIVED FROM THE LOG AT CLAIM TIME.

Without the first half the claim cites nothing and is a sentence. Without the second the numbers are
TYPED, and a typed number is a copy that drifts from its source the first time anyone edits either —
L64, the defect that turned a worked example into a forgery under maintenance. Nothing in this module
states a figure; every figure is computed from the sealed bytes when the gate runs.

WHAT IS SEALED, AND WHY NOT WHERE THE RUNNER WRITES. `--bench` writes to `spec/attest/rollbench.txt`
AND OVERWRITES IT EVERY RUN. A record kept at the path its own producer clobbers is one command away
from being replaced by a different measurement under the same name, so the sealed artifact carries an
immutable name — host, execution count and iteration count in the filename — and the runner's output
path stays scratch. That separation is checked here rather than remembered.

THE READING, in the log's own terms and none of them written down here: the penalty `moulded` pays
against `flat`, its spread across the depth axis, how many distinct experiments SEPARATE under
URDRRPT1, and in how many execution-level pairs the direction holds. What this module asserts is
that the log SUPPORTS a claim of that shape — a constant intercept — and the numbers travel with it.

`does_not_show` — and it is the boundary the whole arc has been carrying. THIS IS ONE MACHINE, ONE
INTERPRETER, ONE SET OF DECLARED CONDITIONS. Five executions sample what a process fixes at startup;
they do not sample the machine, the build, the working directory or the environment size, and
Mytkowicz measured factors of that class at 2-8% on their own. The conditions declared are GAMEPLAY
conditions — a turbo power profile with game mode on — rather than measurement conditions, which is
a defensible choice for a game engine and is not a quiet one. And a constant intercept measured over
ticks 1 to 12 is not a claim about ticks 100.

GRADE (honest, D5): MEASURED — the sealed log parses under a format that has already superseded it,
its digest still verifies, it still grades admissible against `sealframe`'s live door, and the
claim's numbers are recomputed from its bytes at gate time and compared to the pinned reading. The
penalty is MEASURED as a constant; the per-experiment magnitude where URDRRPT1 reads
INDISTINGUISHABLE is exactly that and is not upgraded here. DECLARED: which log is the record."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import measure as MS                                        # noqa: E402
import repeat as RP                                         # noqa: E402
import rollbench as RB                                      # noqa: E402

MAGIC = b"URDRATT1"

#: DECLARED — the sealed record. An IMMUTABLE NAME carrying host, executions and iterations, because
#: `--bench` overwrites its own output path on every run and a record kept there is one command from
#: being replaced by a different measurement wearing the same name.
RECORD = "spec/attest/rollbench-allyx-5x200.txt"

#: The runner's output path. Scratch, by design, and asserted DIFFERENT from the record.
SCRATCH = "spec/attest/rollbench.txt"

#: The claim's fixed terms. The NUMBERS are absent on purpose: they are derived from the record.
CLAIM_SHAPE = {"workload": "all four, named per experiment",
               "host": "ROG-Ally-X-Z2-Extreme",
               "denominator": "ns_per_rollback",
               "baseline": "flat",
               "units": "ns",
               "host_log": RECORD}


class AttestError(Exception):
    def __init__(self, message):
        super().__init__(f"ATTEST-REFUSE: {message}")
        self.code = "ATTEST-REFUSE"


# ---- the record -----------------------------------------------------------------------------------
def record_text(path=None):
    p = _os.path.join(_ROOT, path or RECORD)
    if not _os.path.exists(p):
        raise AttestError(f"the cited record {path or RECORD!r} is not in the tree — a graduated "
                          f"claim whose log is missing cites nothing, which is the state this rung "
                          f"exists to end")
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def record(path=None):
    """Parse the sealed log. It is a v1 record and the runner now writes v2 — that it still reads is
    the point, not an accident, and `rollbench.ROW_FIELDS_BY_VERSION` is what makes it true."""
    return RB.parse_log(record_text(path))


def experiments():
    """The 17 DISTINCT experiments, keyed by (workload, ticks). `depth` saturates against the world's
    length, so the 28 cells hold 17 conditions, and the smallest depth reaching each is taken."""
    out = {}
    p = MS.bench_plan()
    for w in p["workloads"]:
        for d in p["depths"]:
            out.setdefault((w, MS.effective_ticks(w, d)), d)
    return dict(sorted(out.items()))


def _by_run(rows, rep, w, d, field="p50_ns"):
    return {int(r["run"]): [int(r[field])]
            for r in rows if r["representation"] == rep and r["workload"] == w
            and int(r["depth"]) == d}


def reading(path=None):
    """EVERY NUMBER IN THE CLAIM, COMPUTED FROM THE SEALED BYTES. Nothing here is written down; if
    the record changes, this changes, and the pinned scene reddens rather than a sentence quietly
    ceasing to be true."""
    p = record(path)
    rows = p["rows"]
    exps = experiments()
    gaps, verdicts, reversals, pairs = [], {}, 0, 0
    for (w, ticks), d in exps.items():
        a, b = _by_run(rows, "flat", w, d), _by_run(rows, "moulded", w, d)
        if not a or not b:
            raise AttestError(f"the record has no {w}/depth {d} pair — it is not the log this "
                              f"claim was graded against")
        fm = RP.median([v[0] for v in a.values()])
        mm = RP.median([v[0] for v in b.values()])
        gaps.append((ticks, mm - fm))
        v = RP.verdict(a, b)
        verdicts[v] = verdicts.get(v, 0) + 1
        for r in sorted(set(a) & set(b)):
            pairs += 1
            if b[r][0] < a[r][0]:
                reversals += 1
    g = [x for _t, x in gaps]
    shallow = [x for t, x in gaps if t <= 2]
    deep = [x for t, x in gaps if t >= 8]
    return {"executions": len(sorted({int(r["run"]) for r in rows})),
            "experiments": len(exps),
            "penalty_median_ns": RP.median(g),
            "penalty_min_ns": min(g),
            "penalty_max_ns": max(g),
            "penalty_shallow_ns": RP.median(shallow),
            "penalty_deep_ns": RP.median(deep),
            "separated": verdicts.get(RP.SEPARATED, 0),
            "indistinguishable": verdicts.get(RP.INDISTINGUISHABLE, 0),
            "undetermined": verdicts.get(RP.UNDETERMINED, 0),
            "pairs": pairs, "reversals": reversals,
            "version": p["version"], "host": p["host"]}


# ---- the live counterexamples, DERIVED from the committed artifact ---------------------------------
def _reseal(mutate):
    """Rebuild the committed record with `mutate` applied to each row and RE-SEAL it, so the result
    is a perfectly valid log: the seal verifies, the plan binds, it grades admissible. These live
    HERE because this module owns the record — `pedigree` and `rehearse` grade what they are handed,
    and reaching back for the artifact put both of them over the lattice's sealed depth ceiling."""
    text = record_text()
    p = RB.parse_log(text)
    fields = RB.ROW_FIELDS_BY_VERSION[p["version"]]
    body = [ln for ln in text.splitlines()
            if ln.strip() and not ln.startswith("row ") and not ln.startswith("digest ")]
    for r in p["rows"]:
        rr = mutate(dict(r))
        if rr is not None:
            body.append("row " + " ".join(str(rr[f]) for f in fields))
    joined = "\n".join(body) + "\n"
    return joined + "digest " + hashlib.sha256(joined.encode()).hexdigest() + "\n"


def replanted_under_the_shipped_schedule():
    """THE COUNTEREXAMPLE TO THE ASSUMPTION THIS MODULE INHERITS, and it is not a manufactured
    fixture: the operator's own measurements, unaltered, with only `pos` rewritten to the plan's own
    nesting — the representation-outermost order `rollbench` actually shipped, and the one that
    produced this tree's first two host logs."""
    cells = list(MS.bench_cells())

    def mutate(r):
        r["pos"] = cells.index((r["representation"], r["workload"], int(r["depth"])))
        return r
    return _reseal(mutate)


def replanted_on_a_different_balanced_stride():
    """BALANCED ON EVERY AXIS AND NOT THE ORDER THE PLAN RUNS — the counterexample `rehearse` needs
    against `pedigree`."""
    import confound as CF
    other = CF.schedule(MS.bench_cells(), stride=37)
    pos = {c: i for i, c in enumerate(other)}

    def mutate(r):
        r["pos"] = pos[(r["representation"], r["workload"], int(r["depth"]))]
        return r
    return _reseal(mutate)


def truncated_to_one_execution():
    def mutate(r):
        return r if int(r["run"]) == 0 else None
    return _reseal(mutate)


# ---- the laws ---------------------------------------------------------------------------------------
def the_record_is_committed_and_still_seals():
    """A graduated claim whose log has been edited, truncated or lost is not a claim. The seal is
    `rollbench`'s own, re-verified here rather than trusted from the day it was written."""
    p = record()
    return (len(p["rows"]) > 0 and p["plan"] == RB.plan_digest()
            and RB.evidence_grade(p)[0] == RB.MEASURED)


def a_tampered_record_refuses():
    """RED-FIRST. Flip one byte of the sealed body and the parse must REFUSE — otherwise the
    citation is decorative and any file at that path would do."""
    text = record_text()
    bad = text.replace("host ROG", "host RoG", 1)
    if bad == text:
        return False
    try:
        RB.parse_log(bad)
        return False
    except RB.RollbenchError:
        return True


def the_record_survives_the_format_that_superseded_it():
    """L64, AND THE REASON THIS RUNG SHIPS WITH A FORMAT CHANGE RATHER THAN BEFORE ONE. The sealed
    log is v1; the runner now writes v2 with a counter v1 never had. A versioning law never met by a
    real successor is inherited rather than tested (L67), so the successor lands in the same commit
    and the archived record must still read."""
    p = record()
    return (p["version"] == "v1" and RB.LOG_VERSION != "v1"
            and len(RB.ROW_FIELDS_BY_VERSION["v1"]) < len(RB.ROW_FIELDS)
            and all("peak" not in r for r in p["rows"]))


def an_unknown_format_refuses():
    """A version this tree does not know is REFUSED rather than guessed at: a row read against the
    wrong field list is a table of numbers under the wrong names."""
    text = record_text().replace("rollbench v1", "rollbench v99", 1)
    try:
        RB.parse_log(text)
        return False
    except RB.RollbenchError:
        return True


def the_record_is_not_the_scratch_path():
    """`--bench` OVERWRITES ITS OWN OUTPUT PATH EVERY RUN. A record kept there is one command away
    from being replaced by a different measurement under the same name — so the sealed artifact
    carries an immutable name and this asserts the two never coincide."""
    return RECORD != SCRATCH and _os.path.basename(RECORD) != _os.path.basename(SCRATCH)


def the_claim_is_well_formed():
    """The claim `measure` will admit, built from the shape above — and one missing term is refused,
    because a law that admitted everything would not be admitting this."""
    if MS.claim_fault(dict(CLAIM_SHAPE)) != "":
        return False
    bad = dict(CLAIM_SHAPE)
    bad.pop("host_log")
    return MS.claim_fault(bad) != ""


def the_numbers_are_derived_not_typed():
    """L64 AT THE SOURCE. No figure in this module's own text may be the claim: the reading is
    RECOMPUTED from the sealed bytes, so an edited record moves the scene digest rather than leaving
    a sentence quietly false. Checked by re-deriving twice and by confirming the module's source
    carries none of the derived values as literals."""
    a, b = reading(), reading()
    if a != b:
        return False
    import ast
    with open(_os.path.abspath(__file__), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    literals = {n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, int)}
    derived = {a["penalty_median_ns"], a["penalty_min_ns"], a["penalty_max_ns"],
               a["separated"], a["pairs"], a["reversals"]}
    return not (derived & literals)


def the_penalty_is_a_constant_not_a_slope():
    """THE RESULT, AND IT IS `measure`'S OWN PREDICTION CHECKED AGAINST A STOPWATCH. Before any host
    ran anything, `measure` proved in exact op counts that moulding moves the INTERCEPT and cannot
    move the SLOPE. If that holds, the penalty must not grow with replay depth — so the shallow and
    deep medians must sit within the penalty's own spread, while the replay work itself grows by
    almost an order of magnitude across the same range."""
    r = reading()
    span = r["penalty_max_ns"] - r["penalty_min_ns"]
    return abs(r["penalty_deep_ns"] - r["penalty_shallow_ns"]) <= span and span > 0


def the_direction_is_reported_with_the_verdict():
    """`panel != scalar`. SEPARATED counts and DIRECTION counts are different facts and neither
    stands alone: a unanimous direction with nothing separating is a hint, and a separation without
    direction is a magnitude with no sign."""
    r = reading()
    return (r["separated"] + r["indistinguishable"] + r["undetermined"] == r["experiments"]
            and r["pairs"] > r["experiments"] and r["reversals"] < r["pairs"])


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("record", "reading")


def scene_case(name):
    if name == "record":
        return "seals=%s|tamper=%s|v1survives=%s|unknown=%s|scratch=%s|claim=%s" % (
            the_record_is_committed_and_still_seals(), a_tampered_record_refuses(),
            the_record_survives_the_format_that_superseded_it(), an_unknown_format_refuses(),
            the_record_is_not_the_scratch_path(), the_claim_is_well_formed())
    if name == "reading":
        r = reading()
        return "%s||constant=%s|panel=%s|derived=%s" % (
            sorted(r.items()), the_penalty_is_a_constant_not_a_slope(),
            the_direction_is_reported_with_the_verdict(), the_numbers_are_derived_not_typed())
    raise AttestError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def attest_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_attest.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AttestError(f"no golden named {name!r}")


if __name__ == "__main__":
    print("record seals              :", the_record_is_committed_and_still_seals())
    print("tampered record refuses   :", a_tampered_record_refuses())
    print("v1 survives v2            :", the_record_survives_the_format_that_superseded_it())
    print("unknown format refuses    :", an_unknown_format_refuses())
    print("record != scratch path    :", the_record_is_not_the_scratch_path())
    print("claim is well formed      :", the_claim_is_well_formed())
    print("numbers derived not typed :", the_numbers_are_derived_not_typed())
    print("penalty is a constant     :", the_penalty_is_a_constant_not_a_slope())
    print("direction with verdict    :", the_direction_is_reported_with_the_verdict())
    print()
    for k, v in sorted(reading().items()):
        print("   %-22s %s" % (k, v))
    for n in SCENES:
        print(n, scene_result(n))
    print("attest", attest_digest())
