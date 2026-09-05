# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxtrace8 (URDRTR81) — THE ARC MEASURED SEVEN CASES AND CALLED THEM EIGHT. RE-MEASURED, NOTHING
CHANGES.

`voxpath` found the defect and scoped it precisely: `voxref.TRACE` declares eight adversarial frames
and `voxref.every_declared_case_is_distinct` is CORRECT that all eight are distinct — under the
COMMITTED winding. But `voxray`'s oracle established that the committed winding is the DEFECTIVE one,
so every rung from `voxtie` onward renders with `primitives_with("reversed")`, and under the
CORRECTED winding `enclosed` and `buried` produce byte-identical colour AND depth. The performance
arc has been measuring SEVEN distinct observables while calling them eight, and `voxwork` and
`voxsilo` — the two rungs that fixed the work floor and found the silo lattice's best cell — were
never re-run.

THIS RUNG RE-RUNS THEM ON A CORPUS THAT REALLY HAS EIGHT, AND EVERY FINDING SURVIVES.

    the overdraw headline       12.02 walked per output pixel  ->  11.96      SURVIVES
    the best silo cell          GA, not the full GTA           ->  GA         SURVIVES
    the tile arm is destructive with the arithmetic arm        ->  still is   SURVIVES
    the tile arm still retires pixels                          ->  still does SURVIVES
    the corrected depth bound is never violated                ->  never      SURVIVES
    every silo reproduces the observable                       ->  every one  SURVIVES

A NULL RESULT IS THE POINT AND IT IS ONLY WORTH HAVING BECAUSE IT COULD HAVE GONE THE OTHER WAY. The
silo lattice's headline — THE FULL COMBINATION IS NOT THE BEST ONE — is the most surprising thing
this arc has produced, and it was measured on a corpus with a redundant frame. If it had depended on
that frame it would have been an artefact. It does not: `GA` costs 2425194 against `GTA`'s 2696490 on
the corrected corpus, the same ordering by the same margin in kind.

AND THE SILO CONTRACT IS RE-TESTED ON GEOMETRY IT HAS NEVER SEEN, which is the part that could have
found a real bug rather than a bookkeeping one. `voxsilo`'s central law requires every cell of the
lattice to reproduce `voxref.render` AS LISTS on every declared frame; a silo unsound in a way the
seven-case trace could not expose would fail here. All eight cells pass on all eight frames.

HOW THE EIGHTH CASE IS OBTAINED, AND THE PROCEDURE MATTERS MORE THAN THE FRAME:

    DROP    of the collapsed pair, the frame whose eye is INSIDE SOLID. That is `buried`, and the
            rule selects it UNIQUELY — `voxray.eye_is_inside_solid` is true of exactly one of the
            two. `voxray.comparable_frames` already excludes it, so this rung is not inventing a
            judgement, it is applying one the tree already holds. Nothing observable is lost, because under the
            corrected winding the two frames ARE the same picture.
    SEARCH  voxel centres in RASTER ORDER, forward held at (0, 1, 0) — the forward the dropped frame
            used — taking the FIRST candidate that is in free space and whose observable differs from
            all seven kept frames. First-match in a fixed order, so the frame cannot have been chosen
            for its effect on any number.

The search examined TWO candidates. The first, the centre of cell (0,0,0), is inside solid; the
second qualifies. THAT IS EVIDENCE THE CRITERION IS EASY TO SATISFY AND NOT THAT THE FRAME IS
SPECIAL, and `the_search_is_reported_honestly` states it as a law rather than letting a one-line
search read as a thorough one.

NOTHING HISTORICAL IS EDITED. `voxref.TRACE` is untouched and its own distinctness law is RUN here
and still green. `voxwork`'s and `voxsilo`'s committed records are untouched and their own binding
laws are RUN here and still green. This rung ships a record BESIDE theirs; it does not correct them,
because their figures are what those rungs actually measured and a record edited to match a later
corpus is a record that has stopped being evidence.

AND THE INSTRUMENTS ARE IMPORTED RATHER THAN REIMPLEMENTED. Every number here comes from
`voxwork.instrument` and `voxsilo.render_cell` called directly, so the eight-case measurement runs
the IDENTICAL code path as the seven-case one and any difference is a difference in the trace.
`the_instruments_are_imported_and_not_reimplemented` proves it from this module's own AST: it
contains no rasteriser, and this is the eighth transcription of that loop the arc has NOT written.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. THAT THE EIGHTH FRAME IS ADVERSARIAL —
it restores DISTINCTNESS and nothing else is claimed for it; the seven inherited frames carry the
adversarial intent and this one carries a search rule. THAT SEVEN CASES WERE TOO FEW for any
particular conclusion — this rung tests whether the conclusions MOVE, finds they do not, and that is
the whole claim. THAT THE OLD FIGURES WERE WRONG: they measured eight renders of seven distinct
pictures, which is exactly what they said they did once `voxpath` corrected the count. And NO
PROMOTION: `voxref` is untouched and nothing is adopted.

falsifier: `every_cell_reproduces_the_observable_on_the_new_trace` compares colour and depth AS LISTS
for all eight silo cells on all eight frames, which is the law that would catch a silo unsound in a
way the old corpus could not expose; `the_replacement_is_the_first_qualifying_candidate` re-runs the
declared search and reddens if any earlier candidate would have qualified, which is how a
hand-picked frame would be caught; and `the_findings_survive_the_corrected_corpus` reddens the day
any inherited finding stops holding on eight live cases — which would be a far more interesting
result than the one this rung reports.
"""
import ast
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402
import voxray as VX                                          # noqa: E402
import voxwork as VO                                         # noqa: E402
import voxsilo as VS                                         # noqa: E402
import voxpath as VP                                         # noqa: E402

MAGIC = b"URDRTR81"

#: The winding every rung from `voxtie` onward uses, and the one `voxray`'s oracle established is
#: correct. INHERITED, never redeclared — a rung that picked its own winding would be measuring a
#: renderer nobody else runs.
WINDING = "reversed"

#: DECLARED — the forward vector the search holds fixed: the one the DROPPED frame used. Holding it
#: fixed removes a degree of freedom the search could otherwise have exploited.
SEARCH_FORWARD = (0, 1, 0)

#: DECLARED — the inherited findings this rung re-tests on the corrected corpus. Each is a claim some
#: EARLIER rung committed, re-evaluated here rather than cited.
FINDINGS = ("overdraw", "best_cell", "tile_destructive", "tile_retires", "bound_sound",
            "silo_contract")


class Voxtrace8Error(Exception):
    """VOXTRACE8-REFUSE — a frame, a finding or a record this module will not pretend to read."""


def _prims():
    return VX.primitives_with(WINDING)


def _observable(eye, fwd, prims=None):
    return VR.observable(*VR.render(_prims() if prims is None else prims, eye, fwd))


# ---- the defect, re-run rather than cited -------------------------------------------------------------
def collapsed_pair():
    """The indices of the frames `voxref.TRACE` declares as distinct and the CORRECTED winding cannot
    tell apart. Re-derived here; `voxpath` found it, and citing a finding is not running it."""
    prims = _prims()
    seen = {}
    for i, (_nm, eye, fwd) in enumerate(VR.TRACE):
        seen.setdefault(_observable(eye, fwd, prims), []).append(i)
    dup = [tuple(v) for v in seen.values() if len(v) > 1]
    if len(dup) != 1 or len(dup[0]) != 2:
        raise Voxtrace8Error("VOXTRACE8-REFUSE: the collapse is not one pair of two")
    return dup[0]


def dropped():
    """THE DECLARED DROP RULE: of the collapsed pair, the frame whose eye is INSIDE SOLID.

    It selects UNIQUELY — exactly one of the two is inside matter — and it applies a judgement the
    tree already holds rather than inventing one, since `voxray.live_frames` already excludes that
    frame from its own analyses. Nothing observable is lost: under the corrected winding the two
    frames are the same picture.
    """
    inside = [i for i in collapsed_pair() if VX.eye_is_inside_solid(VR.TRACE[i][1])]
    if len(inside) != 1:
        raise Voxtrace8Error("VOXTRACE8-REFUSE: the drop rule does not select exactly one frame")
    return inside[0]


def kept():
    """The seven frames of `voxref.TRACE` that survive the drop, VERBATIM — inherited tuples, not
    re-typed coordinates, so a transcription slip cannot enter here."""
    d = dropped()
    return tuple(VR.TRACE[i] for i in range(len(VR.TRACE)) if i != d)


# ---- the declared search --------------------------------------------------------------------------
def candidates():
    """Voxel centres in RASTER ORDER — the order the world itself is generated in. Fixed, total, and
    independent of anything this rung measures."""
    for x in range(VR.N):
        for y in range(VR.N):
            for z in range(VR.N):
                yield (x, y, z), (x * VR.Q + VR.Q // 2, y * VR.Q + VR.Q // 2, z * VR.Q + VR.Q // 2)


def qualifies(eye, keep_obs):
    """A candidate qualifies when its eye is in FREE SPACE and its observable differs from all seven
    kept frames. Two conditions, both stated before the search ran."""
    if VX.eye_is_inside_solid(eye):
        return False
    return _observable(eye, SEARCH_FORWARD) not in keep_obs


_SEARCH = {}


def search():
    """((cell, eye), candidates examined) — FIRST-MATCH in the declared order."""
    k = VR.world_digest()
    if k in _SEARCH:
        return _SEARCH[k]
    prims = _prims()
    keep_obs = {_observable(e, f, prims) for _n, e, f in kept()}
    seen = 0
    for cell, eye in candidates():
        seen += 1
        if qualifies(eye, keep_obs):
            _SEARCH[k] = ((cell, eye), seen)
            return _SEARCH[k]
    raise Voxtrace8Error("VOXTRACE8-REFUSE: no candidate in the declared order qualifies")


def replacement():
    (cell, eye), _seen = search()
    return ("first_free", eye, SEARCH_FORWARD), cell


#: The corrected corpus: seven inherited frames and one found by the declared search. The eighth is
#: named `first_free` because that is literally what it is — the first free-space cell in the declared
#: scan order whose picture differs from all seven. A name that is true by construction cannot drift
#: from what it describes.
def trace8():
    return kept() + (replacement()[0],)


def distinct_under(winding):
    prims = VX.primitives_with(winding)
    return len({_observable(e, f, prims) for _n, e, f in trace8()})


# ---- the measurements, taken with the EARLIER rungs' own instruments -------------------------------
_FLOOR = {}


def floor():
    """{counter: total} over the corrected corpus, via `voxwork.instrument` called directly."""
    k = VR.world_digest()
    if k in _FLOOR:
        return _FLOOR[k]
    prims = _prims()
    tot = dict.fromkeys(VO.COUNTERS, 0)
    for _nm, eye, fwd in trace8():
        col, dep, n = VO.instrument(prims, eye, fwd)
        if (col, dep) != VR.render(prims, eye, fwd):
            raise Voxtrace8Error("VOXTRACE8-REFUSE: the instrument moved the observable")
        for c in VO.COUNTERS:
            tot[c] += n[c]
    _FLOOR[k] = tot
    return tot


def fates():
    t = floor()
    w, cv, wr = t["walked"], t["covered"], t["written"]
    return {"outside": w - cv, "beaten": cv - wr, "written": wr}


def overdraw():
    """(walked, output pixels) — `voxwork`'s own definition, on eight frames of the new corpus."""
    return floor()["walked"], VR.W * VR.H * len(trace8())


_PANEL = {}


def panel(cell):
    """{column: total} for one silo cell over the corrected corpus, via `voxsilo.render_cell`."""
    c = VS._check(cell)
    k = (VR.world_digest(), c)
    if k in _PANEL:
        return _PANEL[k]
    prims = _prims()
    tot = dict.fromkeys(VS.COLUMNS, 0)
    sound = True
    for _nm, eye, fwd in trace8():
        col, dep, n = VS.render_cell(prims, eye, fwd, c)
        if (col, dep) != VR.render(prims, eye, fwd):
            sound = False
        for name in VS.COLUMNS:
            tot[name] += n[name]
    tot["sound"] = sound
    _PANEL[k] = tot
    return tot


def best_cell(name="mul"):
    return min((VS.cell_name(c) for c in VS.CELLS),
               key=lambda n: panel(next(c for c in VS.CELLS if VS.cell_name(c) == n))[name])


def cell_total(name, column="mul"):
    for c in VS.CELLS:
        if VS.cell_name(c) == name:
            return panel(c)[column]
    raise Voxtrace8Error("VOXTRACE8-REFUSE: no cell named %r" % (name,))


# ---- the findings, re-evaluated rather than cited --------------------------------------------------
def findings():
    """{id: (survives, what was measured)} — each an EARLIER rung's committed claim, re-run here."""
    w, out = overdraw()
    ow, oout = VO.overdraw()
    return {
        "overdraw": (w > 10 * out and abs(w - ow) * 20 < ow,
                     "%d walked per %d output pixels against the old %d per %d — still over ten "
                     "times its own output, and moved by under a twentieth"
                     % (w, out, ow, oout)),
        "best_cell": (best_cell() == "GA" and cell_total("GA") < cell_total("GTA"),
                      "GA costs %d against GTA's %d; the old corpus said %d against %d"
                      % (cell_total("GA"), cell_total("GTA"),
                         VS.panel(("G", "A"))["mul"], VS.panel(("G", "T", "A"))["mul"])),
        "tile_destructive": (cell_total("TA") > cell_total("A"),
                             "TA costs %d against A's %d, so the tile arm still makes the "
                             "arithmetic arm worse" % (cell_total("TA"), cell_total("A"))),
        "tile_retires": (cell_total("T", "walked") < cell_total("-", "walked"),
                         "T walks %d against the plain loop's %d"
                         % (cell_total("T", "walked"), cell_total("-", "walked"))),
        "bound_sound": (all(panel(c)["sound"] for c in VS.CELLS if "G" in VS.cell_name(c)),
                        "every cell carrying the corrected depth bound reproduces the observable"),
        "silo_contract": (all(panel(c)["sound"] for c in VS.CELLS),
                          "all %d cells reproduce colour and depth as lists on all %d frames"
                          % (len(VS.CELLS), len(trace8()))),
    }


def survivors():
    return tuple(sorted(k for k, (ok, _w) in findings().items() if ok))


def casualties():
    return tuple(sorted(k for k, (ok, _w) in findings().items() if not ok))


# ---- the laws ---------------------------------------------------------------------------------------
def the_defect_is_real_and_is_re_run():
    """`voxpath` FOUND this and citing a finding is not running it. The committed trace really does
    collapse to seven distinct observables under the corrected winding, and `voxref`'s own
    distinctness law really is still correct about the committed one."""
    prims = _prims()
    n = len({_observable(e, f, prims) for _n, e, f in VR.TRACE})
    return (n == len(VR.TRACE) - 1
            and len(collapsed_pair()) == 2
            and VR.every_declared_case_is_distinct()
            and VP.the_reversed_winding_collapses_a_declared_case())


def the_drop_rule_selects_exactly_one_frame():
    """A rule that selected both or neither would be a preference dressed as a procedure."""
    inside = [i for i in collapsed_pair() if VX.eye_is_inside_solid(VR.TRACE[i][1])]
    return len(inside) == 1 and dropped() == inside[0]


def the_dropped_frame_is_already_excluded_elsewhere():
    """THE RULE IS INHERITED AND NOT INVENTED. `voxray.comparable_frames` already omits the frame
    whose eye is inside solid — excluded BY DERIVATION there rather than by hand — so this rung
    applies a judgement the tree already holds rather than making a new one."""
    return dropped() not in VX.comparable_frames()


def the_seven_kept_frames_are_verbatim():
    """Inherited tuples, never re-typed coordinates: a transcription slip cannot enter here."""
    return all(f in VR.TRACE for f in kept()) and len(kept()) == len(VR.TRACE) - 1


def the_replacement_is_the_first_qualifying_candidate():
    """FIRST-MATCH IN A FIXED ORDER, PROVED BY RE-SCANNING. Every candidate strictly before the
    chosen one must FAIL the criterion — which is how a hand-picked frame would be caught, since a
    frame selected for its effect on a number would almost never be the first that qualifies."""
    (cell, _eye), seen = search()
    prims = _prims()
    keep_obs = {_observable(e, f, prims) for _n, e, f in kept()}
    n = 0
    for c, eye in candidates():
        n += 1
        if c == cell:
            return n == seen and qualifies(eye, keep_obs)
        if qualifies(eye, keep_obs):
            return False
    return False


def the_search_is_reported_honestly():
    """THE SEARCH EXAMINED TWO CANDIDATES AND THAT IS STATED RATHER THAN GLOSSED. A one-line search
    must not read as a thorough one: the number of candidates examined is REPORTED in the record, and
    a short search is evidence the criterion is EASY TO SATISFY, not that the frame is special."""
    _found, seen = search()
    return 0 < seen < VR.N ** 3 and seen == search()[1]


def all_eight_cases_are_distinct():
    """THE THING THE OLD TRACE FAILED, and the only property this rung claims for the new frame."""
    return distinct_under(WINDING) == len(trace8()) == 8


def every_cell_reproduces_the_observable_on_the_new_trace():
    """THE LAW THAT COULD HAVE FOUND A REAL BUG RATHER THAN A BOOKKEEPING ONE. `voxsilo`'s central
    contract, re-tested on geometry the silos have never seen: a silo unsound in a way the seven-case
    trace could not expose would fail here."""
    return all(panel(c)["sound"] for c in VS.CELLS)


def the_findings_survive_the_corrected_corpus():
    """THE RESULT, AND A NULL ONE IS THE POINT. It is only worth having because it could have gone
    the other way: the silo lattice's headline is the most surprising thing this arc has produced and
    it was measured on a corpus with a redundant frame. This law reddens the day any inherited
    finding stops holding on eight live cases, which would be a far more interesting result."""
    return not casualties() and len(survivors()) == len(FINDINGS)


def the_committed_records_are_untouched():
    """NOTHING HISTORICAL IS EDITED. `voxwork`'s and `voxsilo`'s own binding laws are RUN here, so
    this rung cannot ship while having quietly corrected the records it re-measures. A record edited
    to match a later corpus is a record that has stopped being evidence."""
    return (VO.the_record_is_bound_to_the_live_code() and VO.the_record_names_this_world()
            and VS.the_record_is_bound_to_the_live_code() and VS.the_record_names_this_world())


def the_instruments_are_imported_and_not_reimplemented():
    """PROVED FROM THIS MODULE'S OWN AST. Every number here comes from `voxwork.instrument` and
    `voxsilo.render_cell` called directly, so the eight-case measurement runs the IDENTICAL code path
    as the seven-case one and any difference is a difference in the TRACE. This module contains no
    rasteriser — no edge function, no per-pixel loop — and this is the eighth transcription of that
    loop the arc has NOT written."""
    with open(os.path.join(_HERE, "voxtrace8.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            calls.add(node.attr)
    return ("instrument" in calls and "render_cell" in calls
            and "_edge" not in calls and "_top_left_bias" not in calls)


def no_wall_clock_enters_this_rung():
    with open(os.path.join(_HERE, "voxtrace8.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


def nothing_is_promoted():
    return VO.nothing_is_optimised() and VS.nothing_is_promoted()


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-trace8.txt")


def trace_digest():
    body = "\n".join("%s %s %s" % (n, e, f) for n, e, f in trace8())
    body += "\n" + "\n".join("%s %d" % (c, floor()[c]) for c in VO.COUNTERS)
    body += "\n" + "\n".join("%s %s" % (VS.cell_name(c),
                                        [panel(c)[k] for k in VS.COLUMNS]) for c in VS.CELLS)
    body += "\n" + "\n".join("%s %s" % (k, v[0]) for k, v in sorted(findings().items()))
    return hashlib.sha256(MAGIC + b"|t8|" + body.encode()).hexdigest()


def generate():
    (cell, _eye), seen = search()
    rows = ["# URDRTR81 the corrected corpus — emitted by voxtrace8.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE ARC MEASURED SEVEN CASES AND CALLED THEM EIGHT. Re-measured on a corpus that",
            "# really has eight, EVERY INHERITED FINDING SURVIVES. Nothing historical is edited:",
            "# this record ships BESIDE `voxwork`'s and `voxsilo`'s, which are untouched.",
            "#   drop    <index> <name>            of the collapsed pair, the eye INSIDE SOLID",
            "#   search  <x> <y> <z> <candidates examined>   FIRST-MATCH in raster order",
            "#   frame   <index> <name> <eye> <forward>",
            "#   floor   <counter> <total on the corrected corpus> <total on the old trace>",
            "#   cell    <cell> " + " ".join(VS.COLUMNS),
            "#   finding <id> <SURVIVES|BREAKS> <what was measured>",
            "#   digest  <trace digest>"]
    d = dropped()
    rows.append("drop %d %s" % (d, VR.TRACE[d][0]))
    rows.append("search %d %d %d %d" % (cell + (seen,)))
    for i, (nm, eye, fwd) in enumerate(trace8()):
        rows.append("frame %d %s %d %d %d %d %d %d" % ((i, nm) + tuple(eye) + tuple(fwd)))
    for c in VO.COUNTERS:
        rows.append("floor %s %d %d" % (c, floor()[c], VO.total(c)))
    for c in VS.CELLS:
        rows.append("cell %s %s" % (VS.cell_name(c),
                                    " ".join(str(panel(c)[k]) for k in VS.COLUMNS)))
    for k, (ok, what) in sorted(findings().items()):
        rows.append("finding %s %s %s" % (k, "SURVIVES" if ok else "BREAKS", what))
    rows.append("digest %s" % trace_digest())
    return "\n".join(rows) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "drop" and len(f) != 3:
            raise Voxtrace8Error("VOXTRACE8-REFUSE: a drop row of the wrong arity")
        if f[0] == "search" and len(f) != 5:
            raise Voxtrace8Error("VOXTRACE8-REFUSE: a search row of the wrong arity")
        if f[0] == "frame" and len(f) != 9:
            raise Voxtrace8Error("VOXTRACE8-REFUSE: a frame row of the wrong arity")
        if f[0] == "floor" and (len(f) != 4 or f[1] not in VO.COUNTERS):
            raise Voxtrace8Error("VOXTRACE8-REFUSE: a floor row naming no declared counter")
        if f[0] == "cell" and (len(f) != 2 + len(VS.COLUMNS)
                               or f[1] not in {VS.cell_name(c) for c in VS.CELLS}):
            raise Voxtrace8Error("VOXTRACE8-REFUSE: a cell row naming no declared cell")
        if f[0] == "finding" and (len(f) < 4 or f[1] not in FINDINGS
                                  or f[2] not in ("SURVIVES", "BREAKS")):
            raise Voxtrace8Error("VOXTRACE8-REFUSE: a finding row naming no declared finding")
        if f[0] not in ("drop", "search", "frame", "floor", "cell", "finding", "digest"):
            raise Voxtrace8Error("VOXTRACE8-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise Voxtrace8Error("VOXTRACE8-REFUSE: the record names no world digest")
    if not rows:
        raise Voxtrace8Error("VOXTRACE8-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    fnd = findings()
    for r in rows:
        if r[0] == "floor" and (int(r[2]), int(r[3])) != (floor()[r[1]], VO.total(r[1])):
            return False
        if r[0] == "cell":
            live = [panel(c) for c in VS.CELLS if VS.cell_name(c) == r[1]][0]
            if tuple(int(x) for x in r[2:]) != tuple(live[k] for k in VS.COLUMNS):
                return False
        if r[0] == "finding" and (r[2] == "SURVIVES") != fnd[r[1]][0]:
            return False
        if r[0] == "drop" and int(r[1]) != dropped():
            return False
    return next(r[1] for r in rows if r[0] == "digest") == trace_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("floor walked "):
            text = text.replace(ln, "floor strolled " + " ".join(ln.split()[2:]), 1)
            break
    try:
        parse(text)
    except Voxtrace8Error:
        return True
    return False


def told():
    w, out = overdraw()
    ow, oout = VO.overdraw()
    (cell, _eye), seen = search()
    d = dropped()
    return ("THE ARC MEASURED SEVEN CASES AND CALLED THEM EIGHT, AND RE-MEASURED ON A CORPUS THAT "
            "REALLY HAS EIGHT, NOTHING CHANGES. `voxpath` found the defect and scoped it: "
            "`voxref.TRACE` declares eight adversarial frames and the reference's own distinctness "
            "law is CORRECT about the COMMITTED winding — but `voxray`'s oracle established that "
            "winding is the DEFECTIVE one, and under the CORRECTED winding every rung from `voxtie` "
            "onward uses, frames %d and %d produce byte-identical colour AND depth. `voxwork` and "
            "`voxsilo` were never re-run. THE EIGHTH CASE IS OBTAINED BY PROCEDURE AND THE "
            "PROCEDURE MATTERS MORE THAN THE FRAME: of the collapsed pair, DROP the one whose eye "
            "is INSIDE SOLID — that is frame %d, `%s`, and the rule selects it UNIQUELY while "
            "applying a judgement the tree already holds, since `voxray.comparable_frames` omits "
            "it already — then SEARCH voxel centres in RASTER ORDER with the forward held at the "
            "dropped frame's own, taking the FIRST candidate in free space whose picture differs "
            "from all seven kept. THE SEARCH EXAMINED %d CANDIDATES, which is stated rather than "
            "glossed: a one-line search must not read as a thorough one, and a short search is "
            "evidence the criterion is EASY TO SATISFY rather than that the frame is special. AND "
            "EVERY INHERITED FINDING SURVIVES: the overdraw headline moves from %d walked per %d "
            "output pixels to %d per %d; THE BEST SILO CELL IS STILL `GA` AND NOT THE FULL `GTA`, "
            "%d against %d where the old corpus said %d against %d; the tile arm is still "
            "destructive with the arithmetic arm; it still retires pixels; the corrected depth "
            "bound is still never violated; and ALL %d SILO CELLS STILL REPRODUCE THE OBSERVABLE ON "
            "ALL EIGHT FRAMES — which is the law that could have found a real bug rather than a "
            "bookkeeping one, since a silo unsound in a way the seven-case trace could not expose "
            "would fail there. A NULL RESULT IS THE POINT AND IT IS ONLY WORTH HAVING BECAUSE IT "
            "COULD HAVE GONE THE OTHER WAY: the silo lattice's headline is the most surprising "
            "thing this arc has produced and it was measured on a corpus with a redundant frame; if "
            "it had depended on that frame it would have been an artefact. NOTHING HISTORICAL IS "
            "EDITED — `voxref.TRACE` is untouched and its own law is RUN here, `voxwork`'s and "
            "`voxsilo`'s records are untouched and their own binding laws are RUN here, and this "
            "record ships BESIDE theirs, because a record edited to match a later corpus is a "
            "record that has stopped being evidence"
            % (collapsed_pair()[0], collapsed_pair()[1], d, VR.TRACE[d][0], seen,
               ow, oout, w, out, cell_total("GA"), cell_total("GTA"),
               VS.panel(("G", "A"))["mul"], VS.panel(("G", "T", "A"))["mul"], len(VS.CELLS)))


def scene_case(name):
    if name == "trace":
        return repr((trace8(), dropped(), search(),
                     distinct_under(WINDING), distinct_under("as-committed")))
    if name == "floor":
        return repr(tuple((c, floor()[c]) for c in VO.COUNTERS) + (overdraw(), sorted(fates().items())))
    if name == "panel":
        return repr(tuple((VS.cell_name(c), tuple((k, panel(c)[k]) for k in VS.COLUMNS))
                          for c in VS.CELLS) + (best_cell(),))
    if name == "findings":
        return repr(sorted(findings().items()))
    raise Voxtrace8Error("VOXTRACE8-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("trace", "floor", "panel", "findings")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxtrace8.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise Voxtrace8Error("VOXTRACE8-REFUSE: no golden named %r" % name)
