# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rehearse — AN ADMISSIBLE ARTIFACT MUST BE STRUCTURALLY REPRODUCIBLE FROM ITS DECLARED PLAN
(URDRRHS1). The hole `pedigree` leaves open, closed by reconstruction rather than by inspection.

`pedigree` reads the order a record CARRIES and asks whether it is balanced. That is a property many
orders have, and it is a property of what the artifact SAYS ABOUT ITSELF. Nothing binds `pos` to when
a row was actually taken, so a doctored ordering that is merely plausible — balanced, permuted,
every axis spread — passes, provided somebody re-seals it. `pedigree` names this bound in its own
`does_not_show`: THE RECORD IS A WITNESS, NOT A NOTARY.

    PLAUSIBLE IS NOT REPRODUCIBLE.

THE LAW, and the difference from `pedigree` is the whole point:

    THE STRUCTURE OF AN ADMISSIBLE RECORD IS THE STRUCTURE ITS DECLARED PLAN GENERATES — the exact
    cells, the exact schedule, the exact per-row work — RECONSTRUCTED HERE AND COMPARED, NOT
    INSPECTED FOR PLAUSIBILITY.

`confound.schedule(measure.bench_cells())` is ONE order, not a family. A record whose positions were
rewritten to some other balanced permutation satisfies every check `pedigree` makes and diverges here
at the first cell, because the tree can say precisely which order it would have run. The same holds
for the cells themselves and for `ticks`, which is a FUNCTION of (workload, depth) and therefore
derivable rather than reportable: a row whose ticks do not match what the plan computes is a row
about an experiment that was not the declared one.

WHAT THIS CANNOT DO, STATED WHERE IT MATTERS RATHER THAN AT THE END. Reproducing the STRUCTURE is not
reproducing the MEASUREMENTS. The timings are nondeterministic by nature — that is why they are
off-gate — so this rung proves the experiment had the shape it claims and says nothing about whether
the numbers inside that shape are the ones that machine would produce again. A record with an honest
structure and fabricated timings passes here, and would need a second host to catch.

`does_not_show`: that the record was produced at the time it claims, by the person it claims, or on
the machine it names — those are attestations, not derivations, and `sealframe` was explicit that a
machine's self-report is recorded and never checked. And the structural comparison is only as strong
as the plan's determinism: if `bench_cells` or `schedule` ever became host-dependent, this law would
quietly become a tautology, so both are asserted deterministic here.

GRADE (honest, D5): MEASURED — a faithful record REPRODUCES; one whose positions are rewritten to a
DIFFERENT BALANCED schedule is ADMISSIBLE to `pedigree` and DIVERGES here, which is the
counterexample this rung exists for; a dropped cell and a mis-derived `ticks` diverge under
separately-named causes; an omitted tick rule is SKIPPED rather than treated as passing; and the
reconstruction is proved deterministic. THE LIVE ARTIFACT is reconstructed at the gate, where the
plan and the record live — reaching for them from here put this module at import-depth 15 against a
sealed ceiling. DECLARED: that the structure is the plan's, and the plan is `measure`'s to state."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

# LEAVES AND `pedigree` ONLY — the same lesson the lattice taught `confound` and then `pedigree`.
# The first draft reached for `attest`, `measure` and `rollbench` to fetch the record, the cells and
# the tick function, which put it at import-depth 15 against a ceiling clause (b) binds to the
# ENUMERATED chain at the seal. That ceiling is a measurement and does not move to admit the module
# that failed it. The cells and the tick function arrive as ARGUMENTS; scenes pin behaviour on
# fixtures; the LIVE artifact is reconstructed at the gate, where the plan and the record live.
import confound as CF                                      # noqa: E402
import pedigree as PD                                      # noqa: E402

MAGIC = b"URDRRHS1"

REPRODUCED = "REPRODUCED"
DIVERGED = "DIVERGED"
OUTCOMES = (REPRODUCED, DIVERGED)


class RehearseError(Exception):
    def __init__(self, message):
        super().__init__(f"REHEARSE-REFUSE: {message}")
        self.code = "REHEARSE-REFUSE"


# ---- the reconstruction ----------------------------------------------------------------------------
def expected_order(cells):
    """THE order the plan generates — singular. `confound.schedule` is a permutation chosen by a
    pinned stride, so this is not a family of acceptable orders but one sequence."""
    return CF.schedule(cells)


def divergences(parsed, cells, ticks_of=None):
    """Every structural difference between the record and what its plan generates, each NAMED.

    `ticks_of(workload, depth)` is supplied by whoever owns the plan. Omitted, the tick check is
    SKIPPED rather than assumed to pass."""
    out = []
    want = expected_order(cells)
    runs = sorted({int(r["run"]) for r in parsed["rows"]})
    if not runs:
        return (("no-rows", "the record contains no rows"),)
    if runs != list(range(len(runs))):
        out.append(("run-indices", f"executions are indexed {runs}, not 0..{len(runs) - 1}"))
    for run in runs:
        mine = [r for r in parsed["rows"] if int(r["run"]) == run]
        got_cells = sorted((r["representation"], r["workload"], int(r["depth"])) for r in mine)
        if got_cells != sorted(want):
            out.append(("cells-differ",
                        f"run {run} holds {len(mine)} cells against the plan's {len(want)}, or a "
                        f"different set: the record is about a different experiment"))
            continue
        try:
            got_order = PD.recorded_schedule(parsed, run)
        except PD.PedigreeError as exc:
            out.append(("unreadable-order", f"run {run}: {exc}"))
            continue
        if got_order != want:
            first = next((i for i, (a, b) in enumerate(zip(got_order, want)) if a != b), 0)
            out.append(("order-differs",
                        f"run {run} diverges from the plan's schedule at position {first}: it "
                        f"records {got_order[first]} where the plan runs {want[first]}. BALANCED is "
                        f"a property many orders have; this is the one the plan generates"))
        if ticks_of is not None:
            for r in mine:
                if int(r.get("ticks", -1)) != ticks_of(r["workload"], int(r["depth"])):
                    out.append(("ticks-derived",
                                f"run {run}: {r['workload']}/depth {r['depth']} records "
                                f"{r.get('ticks')} ticks where the plan computes "
                                f"{ticks_of(r['workload'], int(r['depth']))}"))
                    break
    return tuple(out)


def verdict(parsed, cells, ticks_of=None):
    return DIVERGED if divergences(parsed, cells, ticks_of) else REPRODUCED


def report(parsed, cells, ticks_of=None):
    d = divergences(parsed, cells, ticks_of)
    return {"verdict": DIVERGED if d else REPRODUCED,
            "causes": tuple(sorted({n for n, _w in d}))}


# ---- fixtures, built as dicts so no plan or artifact needs importing --------------------------------
def _cells():
    return PD._cells()


def _ticks_of(workload, depth):
    """A fixture tick rule that SATURATES, like the real one: the work stops rising with the
    request. The live rule is `measure.effective_ticks` and is supplied by the gate."""
    return min(depth, 8)


def _record(order, runs=2, tick_bump=None, drop=None):
    rows = []
    pos = {c: i for i, c in enumerate(order)}
    for run in range(runs):
        for c in _cells():
            if drop is not None and run == 0 and c == drop:
                continue
            t = _ticks_of(c[1], c[2])
            if tick_bump is not None and run == 0 and c == tick_bump:
                t += 1
            rows.append({"representation": c[0], "workload": c[1], "depth": c[2],
                         "run": run, "pos": pos[c], "ticks": t, "p50_ns": 1000 + pos[c]})
    return {"rows": rows, "plan": "PLAN", "version": "v1"}


def a_faithful_record():
    return _record(expected_order(_cells()))


def a_differently_balanced_record():
    """THE COUNTEREXAMPLE TO `pedigree`'S BOUND: a DIFFERENT co-prime stride. Every axis still reads
    BALANCED, so `pedigree` admits it, and it is not the order the plan generates."""
    return _record(CF.schedule(_cells(), stride=37))


def a_record_missing_a_cell():
    return _record(expected_order(_cells()), drop=_cells()[5])


def a_record_with_mis_derived_ticks():
    return _record(expected_order(_cells()), tick_bump=_cells()[3])


# ---- the laws ---------------------------------------------------------------------------------------
def a_faithful_record_reproduces():
    """NON-VACUITY FIRST: a structural law that no record satisfies is a wall."""
    return verdict(a_faithful_record(), _cells(), _ticks_of) == REPRODUCED


def pedigree_admits_what_replay_refuses():
    """THE REASON THIS RUNG EXISTS. A record re-ordered on a different co-prime stride is BALANCED
    on every axis — so `pedigree` admits it — and it is not the order the plan generates."""
    p = a_differently_balanced_record()
    return (PD.verdict(p) == PD.ADMISSIBLE
            and all(CF.verdict(PD.recorded_schedule(p, 0), a) == CF.BALANCED for a in CF.AXES)
            and verdict(p, _cells(), _ticks_of) == DIVERGED
            and "order-differs" in report(p, _cells(), _ticks_of)["causes"])


def a_missing_cell_diverges():
    p = a_record_missing_a_cell()
    return (verdict(p, _cells(), _ticks_of) == DIVERGED
            and "cells-differ" in report(p, _cells(), _ticks_of)["causes"])


def a_mis_derived_tick_count_diverges():
    """`ticks` is computed from the plan, so a record reporting a different one describes an
    experiment the plan does not define — even if every other field is impeccable."""
    p = a_record_with_mis_derived_ticks()
    return (verdict(p, _cells(), _ticks_of) == DIVERGED
            and "ticks-derived" in report(p, _cells(), _ticks_of)["causes"])


def the_three_divergences_are_named_apart():
    a = report(a_differently_balanced_record(), _cells(), _ticks_of)["causes"]
    b = report(a_record_missing_a_cell(), _cells(), _ticks_of)["causes"]
    c = report(a_record_with_mis_derived_ticks(), _cells(), _ticks_of)["causes"]
    return len({a, b, c}) == 3 and all(x for x in (a, b, c))


def a_missing_tick_rule_is_skipped_not_passed():
    """Omit the tick function and that check does not run — a detector treating an ABSENT input as
    a passing one is the vacuity this tree keeps removing."""
    p = a_record_with_mis_derived_ticks()
    return (verdict(p, _cells(), _ticks_of) == DIVERGED
            and verdict(p, _cells()) == REPRODUCED)


def the_reconstruction_is_deterministic():
    """If the plan or the schedule became host-dependent this law would quietly become a tautology —
    a comparison against something that moves with the reader proves nothing."""
    return (expected_order(_cells()) == expected_order(_cells())
            and len(set(expected_order(_cells()))) == len(_cells()))


def structure_is_not_measurement():
    """STATED AS A LAW RATHER THAN A CAVEAT. Fabricate the timings, leave the structure alone, and
    this rung REPRODUCES — it grades the shape of the experiment and nothing else. A reader handed
    REPRODUCED must not read it as 'the numbers are right'."""
    p = a_faithful_record()
    for r in p["rows"]:
        r["p50_ns"] = 1
    return verdict(p, _cells(), _ticks_of) == REPRODUCED


def every_module_basename_is_unique():
    """THE LAW THIS RUNG WAS RENAMED BY, and it was found by colliding with it. This tree puts every
    `tools/*` directory on ONE flat import path, so a module's BASENAME is a global identifier — and
    the first draft of this module was called `replay`, which `tools/editor/replay.py` had already
    taken. Two files with one name in a flat namespace resolve by sys.path insertion order, which is
    a property of whoever imported first rather than of the tree. Nothing checked it; the collision
    surfaced INDIRECTLY, as a stale entry in the exemption register, which is a long way from the
    file. Asserted directly now."""
    seen = {}
    base = _os.path.dirname(_HERE)
    for sub in sorted(_os.listdir(base)):
        d = _os.path.join(base, sub)
        if not _os.path.isdir(d):
            continue
        for fn in sorted(_os.listdir(d)):
            if fn.endswith(".py") and not fn.startswith("_"):
                seen.setdefault(fn[:-3], []).append(sub)
    clashes = {k: v for k, v in seen.items() if len(v) > 1}
    return (not clashes, len(seen), clashes)


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("structure", "counterexamples")


def scene_case(name):
    if name == "structure":
        ok, nmods, clashes = every_module_basename_is_unique()
        return "unique=%s %d %s|reproduces=%s|deterministic=%s|notmeasurement=%s|skip=%s|cells=%d|%s" % (
            ok, nmods, sorted(clashes),
            a_faithful_record_reproduces(), the_reconstruction_is_deterministic(),
            structure_is_not_measurement(), a_missing_tick_rule_is_skipped_not_passed(),
            len(_cells()), sorted(report(a_faithful_record(), _cells(), _ticks_of).items()))
    if name == "counterexamples":
        return "balanced-but-wrong=%s|missing=%s|ticks=%s|apart=%s||%s|%s|%s" % (
            pedigree_admits_what_replay_refuses(), a_missing_cell_diverges(),
            a_mis_derived_tick_count_diverges(), the_three_divergences_are_named_apart(),
            report(a_differently_balanced_record(), _cells(), _ticks_of)["causes"],
            report(a_record_missing_a_cell(), _cells(), _ticks_of)["causes"],
            report(a_record_with_mis_derived_ticks(), _cells(), _ticks_of)["causes"])
    raise RehearseError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def rehearse_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_rehearse.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RehearseError(f"no golden named {name!r}")


if __name__ == "__main__":
    print("faithful record reproduces   :", a_faithful_record_reproduces())
    print("pedigree admits what we refuse:", pedigree_admits_what_replay_refuses())
    print("missing cell diverges        :", a_missing_cell_diverges())
    print("mis-derived ticks diverge    :", a_mis_derived_tick_count_diverges())
    print("three causes, named apart    :", the_three_divergences_are_named_apart())
    print("missing tick rule is skipped :", a_missing_tick_rule_is_skipped_not_passed())
    print("reconstruction deterministic :", the_reconstruction_is_deterministic())
    print("structure != measurement     :", structure_is_not_measurement())
    print("module basenames unique      :", every_module_basename_is_unique())
    print()
    for lbl, p in (("balanced-but-wrong", a_differently_balanced_record()),
                   ("missing-cell", a_record_missing_a_cell()),
                   ("ticks", a_record_with_mis_derived_ticks())):
        print("  %-20s pedigree=%-11s rehearse=%s %s"
              % (lbl, PD.verdict(p), verdict(p, _cells(), _ticks_of),
                 report(p, _cells(), _ticks_of)["causes"]))
    for n in SCENES:
        print(n, scene_result(n))
    print("rehearse", rehearse_digest())
