# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""measure — A PERFORMANCE CLAIM IS VALID ONLY WHEN ITS WORKLOAD, HOST, DENOMINATOR AND BASELINE
ARE NAMED (URDRMSR1). The admission law, the harness, and the part of the answer that can be
settled without a stopwatch.

`mould` made the snapshot smaller by a type. The tempting next sentence is "and therefore rollback
is faster", and it is not available: moulding TRADES something for something. Restoring a moulded
record must read `x, y, z`, ask `contact` what state that is, derive the width, and only then take
the optional fourth integer. The flat record just takes four integers. Fewer integers, more work
per integer — and which wins is a wall-clock question that elegance is not entitled to answer.

THIS CONTAINER IS NOT A NAMED HOST, so no time is measured here and none is claimed. What ships is
the LAW that governs the claim, the HARNESS that will produce it, and the DECOMPOSITION IN EXACT OP
COUNTS that narrows what the stopwatch still has to decide. A falsifier asserts that no wall-clock
figure appears in this module or its conformance file.

AND THE OP COUNTS ALREADY SETTLE THE SHAPE OF THE ANSWER, which is the result worth having before
any host runs anything:

    MOULDING MOVES THE INTERCEPT AND CANNOT MOVE THE SLOPE.

A rollback of depth R costs `restore + R * tick`. The three representations differ ONLY in
`restore` — the per-tick replay is byte-identical work, because `to_vouch` hands `stride` the same
flat state either way. So `cost(R) = intercept + slope*R` with the SLOPE SHARED, proved here in
counts. A host measurement that reports a different slope for the two representations is measuring
something other than the record, and that is now a falsifiable statement about the benchmark rather
than a hope about the result.

THE EXACT TRADE, per actor, per restore:

    grounded actor      -1 integer stored      +1 terrain read
    airborne actor       0 integers stored     +1 terrain read

An airborne actor pays the derivation and saves nothing. That is not a defect — it is the price of
having a shape rather than a policy — and it means the benefit is a function of the WORKLOAD, which
is exactly why a claim must name one.

FOUR CONTROLS, AND THE THIRD IS THE ONE THAT MAKES THE EXPERIMENT MEAN ANYTHING.

    flat        the conventional slot, four integers, no derivation
    moulded     the shipped representation
    narrowed    the SAME integers as moulded with NO derivation — its widths arrive through a side
                channel that is DELIBERATELY NOT COUNTED. It is an unfair control by construction
                and says so: it is an UPPER BOUND on the memory-only benefit, and the gap between
                `narrowed` and `moulded` is exactly what the derivation costs.

Without `narrowed`, a host result showing moulded faster could not distinguish "fewer integers
helped" from "the derivation was free".

FOUR WORKLOADS, AND THEY ARE PROVED TO DIFFER. all-grounded, all-airborne, alternating, and
frequent-landing — with their contact-state censuses required to be DISTINCT, because a workload
family whose members exercise the same states is one workload wearing four names, and the saving
would then be a property of the fixture (`retain`'s lesson, one layer up).

GRADE (honest, D5): MEASURED — the admission law refuses a claim missing any of its four fields and
refuses a timed claim with no host log, each proved separately; the op-count decomposition and the
exact per-actor trade; the shared-slope result; the four workloads proved distinct by their state
censuses; the three representations proved to store what they claim. NOT_MEASURED: every wall-clock
figure, structurally — there is no clock in this module and the harness refuses to grade its own
output. `does_not_show`: that moulding is faster OR slower — that is the question this rung
EXISTS to hand to a host with its terms fixed; that op counts predict time (they bound what can
differ, which is a weaker and true claim); that these four workloads are representative of play."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                        # noqa: E402
import mould as MD                                          # noqa: E402
import stride as SR                                         # noqa: E402
import vouch as VC                                          # noqa: E402

MAGIC = b"URDRMSR1"

#: THE LAW, as data. A performance claim missing any of these is not a weak claim, it is not a
#: claim — there is nothing to reproduce and nothing to compare against.
CLAIM_FIELDS = ("workload", "host", "denominator", "baseline")

#: Units that make a claim a TIMED one, and a timed claim must cite a host log. Counts may be
#: asserted from a gate run; milliseconds may not, and the difference is the whole of L65's
#: "counts on-gate, wall-clock off".
TIMED_UNITS = ("ms", "us", "ns", "s", "fps", "ms/tick")

REPRESENTATIONS = ("flat", "moulded", "narrowed")
WORKLOADS = ("all_grounded", "all_airborne", "alternating", "frequent_landing")
DEPTHS = (1, 2, 4, 8, 16, 32, 64)


class MeasureError(Exception):
    def __init__(self, message):
        super().__init__(f"MEASURE-REFUSE: {message}")
        self.code = "MEASURE-REFUSE"


# ---- the admission law ---------------------------------------------------------------------------
def admit_claim(claim):
    """A PERFORMANCE CLAIM IS VALID ONLY WHEN ITS WORKLOAD, HOST, DENOMINATOR AND BASELINE ARE
    NAMED — and a TIMED claim must additionally cite a host log, because a number in milliseconds
    asserted from a gate run is a number from an unnamed machine under an unknown scheduler."""
    if not isinstance(claim, dict):
        raise MeasureError(f"{claim!r} is not a claim record")
    for f in CLAIM_FIELDS:
        v = claim.get(f)
        if not isinstance(v, str) or not v.strip():
            raise MeasureError(f"the claim names no {f} — a performance claim missing one of "
                               f"{', '.join(CLAIM_FIELDS)} is not a weak claim, it is not a claim: "
                               f"there is nothing to reproduce and nothing to compare against")
    units = claim.get("units", "")
    if units in TIMED_UNITS and not str(claim.get("host_log", "")).strip():
        raise MeasureError(f"a claim in {units!r} cites no host log — counts may be asserted from a "
                           f"gate run and WALL-CLOCK MAY NOT, because a millisecond from an "
                           f"unnamed machine under an unknown scheduler is not a measurement")
    return True


def claim_fault(claim):
    try:
        admit_claim(claim)
    except MeasureError as exc:
        return str(exc)
    return ""


# ---- the workloads -------------------------------------------------------------------------------
def workload(name, revision="rev-0"):
    """(world, log). Four shapes, and they are proved DISTINCT below — a family whose members
    exercise the same states is one workload wearing four names."""
    field = CT._demo_field(8, 5)
    if name == "all_grounded":
        w = SR.world(field, [(2, 2)], revision=revision, T=12)
        return w, [SR.event(t, 0, t, 0, "E", 0) for t in (1, 3, 5)]
    if name == "all_airborne":
        w = SR.world(field, [(2, 2)], revision=revision, T=12)
        w["pos"][0][SR.AX_Y] = 60                       # dropped in from a height
        return w, []
    if name == "alternating":
        w = SR.world(field, [(2, 2)], revision=revision, T=16, jump=2)
        return w, [SR.event(t, 0, t, 0, "", 1) for t in (0, 4, 8, 12)]
    if name == "frequent_landing":
        w = SR.world(field, [(2, 2)], revision=revision, T=15, jump=1)
        return w, [SR.event(t, 0, t, 0, "E", 1) for t in range(15)]
    raise MeasureError(f"no workload named {name!r}")


def state_census(name):
    _f, states, _w = VC.full(*workload(name))
    return {s: sum(1 for row in states for x in row if x == s)
            for s in sorted({x for row in states for x in row})}


def the_workloads_differ():
    """Proved DISTINCT by their contact-state censuses. Without this the saving could be a property
    of one fixture repeated four times — `retain`'s lesson one layer up."""
    seen = [tuple(sorted(state_census(n).items())) for n in WORKLOADS]
    return len(set(seen)) == len(WORKLOADS)


# ---- the three representations -------------------------------------------------------------------
def record_for(rep, world, frames, states, tick):
    """`narrowed` stores the SAME integers as `moulded` and derives nothing: its widths arrive
    through a side channel that is DELIBERATELY NOT COUNTED. Unfair by construction, and that is
    the point — it is an UPPER BOUND on the memory-only benefit."""
    if rep == "flat":
        return VC.snapshot(world, frames, tick)
    if rep == "moulded":
        return MD.mint(world, frames, states, tick)
    if rep == "narrowed":
        rec = MD.mint(world, frames, states, tick)
        return (rec[0], rec[1], rec[2], tuple(len(s) for s in rec[1]))   # widths: NOT counted
    raise MeasureError(f"no representation named {rep!r}")


def ints_stored(rep, record):
    if rep == "flat":
        return sum(len(a) for a in record[1])
    return sum(len(s) for s in record[1])               # `narrowed`'s widths are uncounted


def restore_reads(rep, world, record):
    """TERRAIN READS SPENT RESTORING — counted through `contact`'s own door, so this is the same
    denominator `contact` and `stride` already report against."""
    CT.reset_lookups()
    if rep == "flat":
        VC.admit_resume(world, record)
    elif rep == "moulded":
        MD.to_vouch(world, record)
    elif rep == "narrowed":
        pass                                            # the width is given; nothing is derived
    else:
        raise MeasureError(f"no representation named {rep!r}")
    return CT.lookup_count()


def restore_cost(rep, name="all_grounded", tick=3):
    w, lg = workload(name)
    frames, states, _wt = VC.full(w, lg)
    rec = record_for(rep, w, frames, states, tick)
    return {"ints": ints_stored(rep, rec), "reads": restore_reads(rep, w, rec)}


def the_exact_trade(name="alternating"):
    """PER ACTOR, PER RESTORE: a grounded actor saves one integer and pays one terrain read; an
    airborne actor pays the read and saves nothing. Returns the per-tick table, so the trade is
    read off the states rather than argued."""
    w, lg = workload(name)
    frames, states, _wt = VC.full(w, lg)
    rows = []
    for t in range(len(frames) - 1):
        f = restore_cost("flat", name, t)
        m = restore_cost("moulded", name, t)
        rows.append((states[t][0][0], f["ints"] - m["ints"], m["reads"] - f["reads"]))
    return tuple(rows)


def the_trade_is_one_for_one(name="alternating"):
    """A grounded restore is (-1 integer, +1 read) and an airborne restore is (0, +1), for every
    tick and both states present — the shape of the whole latency question in two numbers."""
    rows = the_exact_trade(name)
    kinds = {r[0] for r in rows}
    return (all((r[1], r[2]) == ((1 if r[0] == "T" else 0), 1) for r in rows)
            and kinds == {"T", "A"} and len(rows) > 4)


# ---- the depth ladder ------------------------------------------------------------------------------
def depth_cost(rep, name, depth, tick=1):
    """THE OP COUNT of a rollback of `depth` ticks: the restore, then the replay. Exact, and the
    only part of `cost(R)` this container is entitled to report."""
    w, lg = workload(name)
    frames, states, _wt = VC.full(w, lg)
    rec = record_for(rep, w, frames, states, tick)
    reads = restore_reads(rep, w, rec)
    flat = rec if rep == "flat" else MD.to_vouch(w, (rec[0], rec[1], rec[2]))
    CT.reset_lookups()
    pos = [[a[SR.AX_X], a[SR.AX_Y], a[SR.AX_Z]] for a in flat[1]]
    vy = [a[3] for a in flat[1]]
    import lockstep as _L
    by_tick = _L.canon(list(lg))
    steps = 0
    for t in range(tick + 1, min(tick + 1 + depth, w["T"])):
        SR.advance(w, pos, vy, by_tick.get(t, []))
        steps += 1
    return {"restore_ints": ints_stored(rep, rec), "restore_reads": reads,
            "replay_reads": CT.lookup_count(), "replayed_ticks": steps}


def first_grounded_tick(name):
    _f, states, _w = VC.full(*workload(name))
    for t, row in enumerate(states):
        if row[0] in CT.SUPPORTED_STATES:
            return t
    raise MeasureError(f"{name!r} never touches the ground — no grounded restore to compare")


def slope_and_intercept(rep, name="alternating", tick=None):
    """`cost(R) = intercept + slope*R` IN OP COUNTS. The intercept is the restore; the slope is the
    per-tick replay, taken as the exact difference between two depths so it is measured rather than
    divided out."""
    t0 = first_grounded_tick(name) if tick is None else tick
    a = depth_cost(rep, name, 2, t0)
    b = depth_cost(rep, name, 6, t0)
    dr = (b["replay_reads"] - a["replay_reads"])
    dt = (b["replayed_ticks"] - a["replayed_ticks"])
    if dt <= 0:
        raise MeasureError("the two depths replayed the same number of ticks — no slope is "
                           "recoverable from a difference of zero")
    return {"intercept_ints": a["restore_ints"], "intercept_reads": a["restore_reads"],
            "slope_reads_per_tick": dr // dt}


def moulding_moves_the_intercept_only(name="alternating"):
    """THE RESULT WORTH HAVING BEFORE ANY HOST RUNS ANYTHING. The three representations differ ONLY
    in the restore: the per-tick replay is identical work, because `to_vouch` hands `stride` the
    same flat state either way. So the SLOPE IS SHARED and only the INTERCEPT moves — proved here
    in exact counts, which makes "a host reports different slopes" a falsifiable statement about
    the BENCHMARK rather than a hope about the result."""
    s = {r: slope_and_intercept(r, name) for r in REPRESENTATIONS}
    slopes = {s[r]["slope_reads_per_tick"] for r in REPRESENTATIONS}
    intercepts = {(s[r]["intercept_ints"], s[r]["intercept_reads"]) for r in REPRESENTATIONS}
    # THE INTERCEPTS ARE COMPARED AT A GROUNDED TICK, because at an airborne one all three
    # representations store four integers and the comparison would be a tie that means nothing.
    return (len(slopes) == 1 and len(intercepts) == len(REPRESENTATIONS), s)


def the_narrowed_control_isolates_the_derivation(name="alternating", tick=None):
    """Without it, a host result showing moulded faster could not distinguish "fewer integers
    helped" from "the derivation was free". `narrowed` stores what `moulded` stores and derives
    nothing, so the gap between them IS the derivation."""
    t0 = first_grounded_tick(name) if tick is None else tick
    f = restore_cost("flat", name, t0)
    m = restore_cost("moulded", name, t0)
    n = restore_cost("narrowed", name, t0)
    return (n["ints"] == m["ints"] and n["reads"] == 0 and m["reads"] > 0
            and f["ints"] > m["ints"], {"flat": f, "moulded": m, "narrowed": n})


# ---- the harness ------------------------------------------------------------------------------------
def bench_plan():
    """WHAT THE OPERATOR RUNS, as data rather than as instructions in prose: every cell the host
    benchmark must fill, with the denominators named in advance so a result cannot be reported
    against a denominator chosen after seeing it."""
    return {"representations": REPRESENTATIONS, "workloads": WORKLOADS, "depths": DEPTHS,
            "denominators": ("snapshot_ints", "snapshot_bytes", "ms_per_rollback",
                             "ms_per_replayed_tick"),
            "quantiles": ("p50", "p95", "p99"),
            "baseline": "flat",
            "prediction": "the slope is shared; only the intercept may move",
            "status": "NOT_MEASURED — requires a named host log"}


def the_plan_names_its_terms():
    """The plan must satisfy the law it exists to serve, or this module would be exempting itself
    from its own rule."""
    p = bench_plan()
    return (p["baseline"] in REPRESENTATIONS and len(p["denominators"]) >= 2
            and len(p["quantiles"]) == 3 and p["status"].startswith("NOT_MEASURED")
            and set(p["workloads"]) == set(WORKLOADS))


def no_wall_clock_is_claimed():
    """STRUCTURAL. There is no clock in this module and no timed figure in its conformance file, so
    a wall-clock claim cannot be smuggled in behind a count."""
    import ast as _ast
    with open(_os.path.join(_HERE, "measure.py"), encoding="utf-8") as fh:
        src = fh.read()
    # READ CODE, NOT PROSE. The banned names occur in this very predicate, so a text scan would
    # find its own guard list — the `authority-reads-code` defect, in the checker that forbids it.
    banned = {"time", "timeit", "resource"}
    for node in _ast.walk(_ast.parse(src)):
        if isinstance(node, (_ast.Import, _ast.ImportFrom)):
            names = [getattr(node, "module", None)] + [a.name for a in node.names]
            if any((n or "").split(".")[0] in banned for n in names):
                return False
        if isinstance(node, _ast.Call):
            fn = node.func
            nm = fn.id if isinstance(fn, _ast.Name) else getattr(fn, "attr", "")
            if nm in ("perf_counter", "monotonic", "process_time", "time", "default_timer"):
                return False
    path = _os.path.join(_HERE, "conformance_measure.txt")
    if _os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        import re as _re
        if _re.search(r"\d+(\.\d+)?\s*(ms|us|ns|fps)\b", body):
            return False
    return True


# ---- scenes ---------------------------------------------------------------------------------------
SCENES = ("law", "trade", "slope", "plan")


def scene_case(name):
    if name == "law":
        good = {"workload": "alternating", "host": "named-host", "denominator": "ints/restore",
                "baseline": "flat", "units": "ints"}
        faults = []
        for f in CLAIM_FIELDS:
            bad = dict(good)
            bad.pop(f)
            faults.append("%s:%s" % (f, claim_fault(bad)[:40]))
        timed = dict(good, units="ms")
        faults.append("timed:%s" % claim_fault(timed)[:40])
        return "%s||%s" % (claim_fault(good) == "", "|".join(faults))
    if name == "trade":
        return "%s||%s" % (the_trade_is_one_for_one(), the_exact_trade())
    if name == "slope":
        holds, s = moulding_moves_the_intercept_only()
        return "%s|%s" % (holds, sorted((r, sorted(s[r].items())) for r in REPRESENTATIONS))
    if name == "plan":
        return "%s||%s" % (sorted(bench_plan().items()),
                           sorted((w, sorted(state_census(w).items())) for w in WORKLOADS))
    raise MeasureError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def measure_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_measure.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MeasureError(f"no golden named {name!r}")


if __name__ == "__main__":
    if "--plan" in _sys.argv:
        # THE PLAN AS DATA, for the operator's host run. The timing itself is deliberately NOT here:
        # a clock in this module would let a wall-clock figure be asserted from a gate run.
        import json as _json
        print(_json.dumps({"plan": bench_plan(),
                           "state_census": {w: state_census(w) for w in WORKLOADS},
                           "op_counts": {r: {w: restore_cost(r, w, first_grounded_tick(w))
                                             for w in WORKLOADS} for r in REPRESENTATIONS}},
                          indent=1, sort_keys=True))
        raise SystemExit(0)
    print("workloads differ :", the_workloads_differ())
    for wname in WORKLOADS:
        print("   %-18s %s" % (wname, state_census(wname)))
    _gt = first_grounded_tick("alternating")
    print("\nrestore cost (alternating, first grounded tick %d):" % _gt)
    for rep in REPRESENTATIONS:
        print("   %-10s %s" % (rep, restore_cost(rep, "alternating", _gt)))
    print("\ntrade one-for-one:", the_trade_is_one_for_one())
    holds, s = moulding_moves_the_intercept_only()
    print("intercept only   :", holds)
    for rep in REPRESENTATIONS:
        print("   %-10s %s" % (rep, s[rep]))
    print("narrowed isolates:", the_narrowed_control_isolates_the_derivation())
    print("plan names terms :", the_plan_names_its_terms(),
          " no wall clock:", no_wall_clock_is_claimed())
    for n in SCENES:
        print(n, scene_result(n))
    print("measure", measure_digest())
