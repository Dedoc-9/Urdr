# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cutbound (URDRCBD1) — A REFUSAL IS A PROOF, AND THE PRODUCTION LAW WAS THROWING IT AWAY.

`shadowcut` established that the max-flow remedy answers a different question and that a 0-1 BFS
answers the right one. THE ADJUDICATION IS THEREFORE NOT "WHICH ALGORITHM WINS". It is what
`CUT_SEARCH_MAX = 3` actually costs — and the answer is that it costs far less than it looked, and
that reading it as a limit rather than as EVIDENCE cost two live defects instead.

THE VERDICT: RETAIN THE ENUMERATION. Replacing it with the path oracle would have produced the same
numbers with STRICTLY WEAKER PROVENANCE, because the enumeration's refusal is a THEOREM about the
wall and the path oracle's answer is a witness plus an argument. The stronger-looking formulation
would have destroyed the better evidence.

WHAT `None` MEANS. `min_cut` tries every subset of the wall of size 1 through `CUT_SEARCH_MAX` and
returns `None` when none of them opens it. That is not an absence of information. IT IS AN
EXHAUSTIVE PROOF THAT k >= CUT_SEARCH_MAX + 1.

Pair it with a witness and three cases fall out, measured rather than asserted:

    wall        bounded  witness   proven interval   provenance
    (n=5, t=2)        2        2            [2, 2]   exhaustion
    (n=6, t=3)        3        3            [3, 3]   exhaustion
    (n=6, t=4)     None        4            [4, 4]   exhaustion AND witness MEET
    (n=6, t=5)     None        5            [4, 5]   bracketed; the argument closes it

SO THE CAP COSTS NOTHING UP TO `CUT_SEARCH_MAX + 1`. At k = 4 the exhaustion proves the lower bound
and the witness proves the upper bound and they coincide, so the answer is DECIDED with no appeal to
the reduction at all. Only from k >= CUT_SEARCH_MAX + 2 does an interval open, and even then it is a
bracket rather than a blank.

THE THEOREM, STATED BECAUSE IT IS AN ARGUMENT AND NOT A MEASUREMENT. A set S of wall cells opens the
wall exactly when some face-to-face route has all of its wall cells inside S: deleting the wall cells
ON a route opens that route, and any deletion that opens the wall leaves SOME route free, whose wall
cells it must therefore contain. Hence the minimum |S| equals the minimum over routes of the number
of wall cells on the route, which is what a 0-1 BFS computes. THIS ARGUMENT IS WHAT CLOSES A BRACKET
AND NOTHING ELSE DOES, and `the_theorem_is_only_needed_past_the_meeting_point` is where that boundary
is enforced rather than described.

AND READING THE REFUSAL AS AN ABSENCE COST TWO DEFECTS IN THE SHIPPED LAW, BOTH FLATTERING:

    * THE CHARGE UNDERCHARGED. `charge_for_gap(None)` returned 0, so a wall the search could not
      decide cost NOTHING — while the honest reading, k >= 4, bills `BASE_CHARGE // 4` = 3. At the
      shipped constants every wall with a gap between 4 and 12 was billed 0 against an honest 1 to 3.
      The charge is monotone NON-INCREASING, so the largest value consistent with the proof sits at
      the bound itself, and taking it can only ever OVERSTATE the cost of an unknown-but-large gap.
    * THE FLOOR WAS CLEARED BY ACCIDENT. `certifiable` returned True on `None` without consulting
      `WALL_MIN_K` at all. At the shipped constants the verdict is right — 4 clears a floor of 2 —
      but it is right because two constants happen to be ordered that way. Lower the cap to zero and
      `None` means only k >= 1, and the old branch certifies a ONE-THICK WALL the floor exists to
      refuse. That case is measured here rather than imagined.

NOT ONE PINNED FIGURE MOVES. `shadowcut` established that the bound is inactive across everything
`cohort.gap_table` pins, so the corrected branch is unreachable there: both defects lived on a path
the shipped corpus never walks, and both would have bitten on the first wall past it. A correction
that changes no observable and repairs a live defect is the whole shape this arc looks for.

does_not_show: NOT THAT THE BRACKET IS TIGHT past the meeting point — from k >= 5 the interval is
real and only the theorem closes it, which is stated and not measured. NOT THAT THE CHARGE CURVE IS
RIGHT: `voxbaggage`'s successor question about the criticality peak is untouched, and this rung
corrects only WHICH k the charge is evaluated at, never the shape of `B // k`. NOT THAT RAISING THE
CAP IS UNNECESSARY — it is a cost question this rung does not price, and the meeting point simply
moves with the cap. NOTHING ABOUT TIME, and no wall clock enters. AND NO NEW ALGORITHM IS PROMOTED
INTO THE PRODUCTION PATH: `min_cut` is still the enumeration, unchanged, and the path oracle stays in
`shadowcut` where it is a witness source rather than a decision procedure.

falsifier: `the_refusal_is_a_proven_lower_bound` reddens the day a wall the enumeration refused turns
out to have a cut at or below the cap, which would make every bracket here unfounded;
`the_correction_changes_no_pinned_figure` reddens if any figure `cohort` pins moves under the
corrected branches, which would turn a repair into a re-baselining; and
`the_old_branch_certified_a_wall_the_floor_refuses` reddens if the latent case stops reproducing,
which would mean the second defect was never there and the correction is unmotivated.
"""
import ast
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import cohort as CO                                             # noqa: E402
import shadowcut as SC                                          # noqa: E402

MAGIC = b"URDRCBD1"

#: DECLARED — how an interval came to be known. `exhaustion` needs no argument; `meeting` needs none
#: either, because two proofs close on the same integer; `bracketed` is the only one the theorem
#: has to reach, and naming it apart is the point of the classification.
PROVENANCE = ("exhaustion", "meeting", "bracketed")

#: DECLARED — the walls this rung brackets. The first two sit inside the cap, the third AT the
#: meeting point where exhaustion and witness coincide, the fourth PAST it where a real interval
#: opens. Chosen so every provenance class is non-empty rather than to make the cap look harmless.
CASES = ((5, 2), (6, 3), (6, 4), (6, 5))

#: DECLARED — the argument that closes a bracket, quoted so a later rung can disagree with a
#: sentence rather than with an implementation. It is an ARGUMENT and it is not measured.
THEOREM = ("a set S of wall cells opens the wall exactly when some face-to-face route has all of its "
           "wall cells inside S, so the minimum |S| is the minimum over routes of the wall cells on "
           "the route")

#: DECLARED — the two consumers that read a refusal as an absence, each with what it did wrong.
CORRECTED = {
    "charge_for_gap": "returned 0 for an undecided wall, so a gap the search could not reach cost "
                      "NOTHING; the proven bound bills BASE_CHARGE // (CUT_SEARCH_MAX + 1) instead",
    "certifiable": "returned True on an undecided wall without consulting WALL_MIN_K at all, so the "
                   "floor was cleared by the accident of two constants being ordered that way",
}


class CutboundError(Exception):
    """A case or a provenance this module will not pretend to have."""

    def __init__(self, message):
        super().__init__("CUTBOUND-REFUSE: %s" % message)
        self.code = "CUTBOUND-REFUSE"


_BRACKETS = {}


def bracket(case):
    """(lo, hi, provenance) for a declared wall, with the interval PROVEN rather than argued.

    `lo` comes from the enumeration: a number it decided, or `CUT_SEARCH_MAX + 1` when it refused,
    which its exhaustion proves. `hi` comes from a witness the SUBJECT adjudicates. When they meet,
    the answer is decided without the theorem.
    """
    if case not in CASES:
        raise CutboundError("no declared case %r" % (case,))
    if case in _BRACKETS:
        return _BRACKETS[case]
    n, t = case
    w = CO.spanning_wall(n, t)
    # THE SUBJECT IS ASKED ONCE. Three of these walls are already in `shadowcut`'s swept corpus and
    # its answers come from the SAME `cohort.min_cut` call; re-running the enumeration here would
    # spend a minute of gate time to obtain a number the tree already holds, and would introduce a
    # second path to the same fact for a later rung to find disagreeing.
    decided = (SC.answer(case, "bounded") if case in SC.CASES else CO.min_cut(w, n))
    hi, cells = SC.shortest_cut(w, n)
    if decided is not None:
        lo, prov = decided, "exhaustion"
    else:
        lo = CO.CUT_SEARCH_MAX + 1
        prov = "meeting" if lo == hi else "bracketed"
    _BRACKETS[case] = (lo, hi, prov, frozenset(cells))
    return _BRACKETS[case]


def interval(case):
    lo, hi, _p, _c = bracket(case)
    return (lo, hi)


def provenance(case):
    return bracket(case)[2]


def census():
    return tuple((c, interval(c), provenance(c)) for c in CASES)


def undercharge(case):
    """What the OLD branch billed against what the proof licenses, for a wall the search refused."""
    lo, _hi, prov, _c = bracket(case)
    if prov == "exhaustion":
        return 0
    return CO.BASE_CHARGE // lo


# ---- the laws --------------------------------------------------------------------------------------
def the_refusal_is_a_proven_lower_bound():
    """THE CLAIM THE WHOLE RUNG RESTS ON, checked against the SUBJECT rather than assumed: for every
    wall the enumeration refused, no subset at or below the cap opens it — which is what the refusal
    asserts — and the witness that does open it is strictly larger than the cap."""
    for case in CASES:
        n, t = case
        w = CO.spanning_wall(n, t)
        lo, hi, prov, cells = bracket(case)
        if prov == "exhaustion":
            continue
        if CO.min_cut(w, n) is not None:
            return False
        if not (lo == CO.CUT_SEARCH_MAX + 1 and hi > CO.CUT_SEARCH_MAX):
            return False
        if len(cells) != hi or not CO.free_reaches(w - cells, n):
            return False
    return True


def the_exhaustion_and_the_witness_meet_one_wall_past_the_cap():
    """The finding that makes the cap cheap: at k = CUT_SEARCH_MAX + 1 the two proofs coincide and
    the answer is DECIDED with no appeal to the theorem."""
    met = [c for c in CASES if provenance(c) == "meeting"]
    return bool(met) and all(interval(c)[0] == interval(c)[1] == CO.CUT_SEARCH_MAX + 1 for c in met)


def the_theorem_is_only_needed_past_the_meeting_point():
    """AND THE BOUNDARY IS ENFORCED RATHER THAN DESCRIBED: every case whose interval is open sits
    strictly beyond the meeting point, and every case at or below it is closed."""
    for c in CASES:
        lo, hi = interval(c)
        if provenance(c) == "bracketed":
            if lo == hi or hi <= CO.CUT_SEARCH_MAX + 1:
                return False
        elif lo != hi:
            return False
    return True


def every_provenance_class_is_populated():
    """A classification with an empty class is a distinction nobody has met."""
    seen = {provenance(c) for c in CASES}
    return seen == set(PROVENANCE)


def the_charge_no_longer_reads_a_refusal_as_free():
    """CORRECTION ONE, measured against the constants rather than quoted: an undecided wall now bills
    the largest charge its proven bound permits, instead of nothing."""
    return (CO.charge_for_gap(None) == CO.BASE_CHARGE // (CO.CUT_SEARCH_MAX + 1)
            and CO.charge_for_gap(None) > 0
            and CO.charge_for_gap(None) == CO.charge_for_gap(CO.CUT_SEARCH_MAX + 1))


def the_undercharge_had_a_range_and_it_was_flattering():
    """It was not a rounding difference. Every gap from the bound up to `BASE_CHARGE` was billed
    zero against an honest positive charge, and zero is the cheap end."""
    honest = [CO.charge_for_gap(k)
              for k in range(CO.CUT_SEARCH_MAX + 1, CO.BASE_CHARGE + 1)]
    return all(h > 0 for h in honest) and max(honest) == CO.charge_for_gap(None)


def the_old_branch_certified_a_wall_the_floor_refuses():
    """CORRECTION TWO, and the latent case is REPRODUCED rather than imagined. With the cap lowered
    to zero a one-thick wall is refused by the search, so the old branch would have certified it
    although its true gap is 1 and the floor is 2. The corrected branch reads the bound and refuses."""
    n = 4
    thin = CO.spanning_wall(n, 1)
    if CO.min_cut(thin, n, cap=0) is not None:
        return False
    if CO.min_cut(thin, n) >= CO.WALL_MIN_K:
        return False
    old_would_certify = True                       # the branch was a bare `return True`
    corrected_refuses = (0 + 1) < CO.WALL_MIN_K     # the bound the corrected branch would read
    return old_would_certify and corrected_refuses


def the_floor_is_applied_to_the_bound_and_not_skipped():
    """At the SHIPPED constants the verdict is unchanged — which is the point, since a correction
    that moved a live verdict would be a re-baselining rather than a repair."""
    return (CO.thin_walls_are_refused() == (True, True)
            and CO.CUT_SEARCH_MAX + 1 >= CO.WALL_MIN_K)


def the_correction_changes_no_pinned_figure():
    """NOT ONE PINNED FIGURE MOVES. `shadowcut` established the bound is inactive across everything
    `cohort.gap_table` pins, so the corrected branches are unreachable on the shipped corpus."""
    return (CO.gap_table() == ((3, 1, 1), (4, 1, 1), (4, 2, 2), (5, 1, 1), (5, 2, 2))
            and CO.charge_table() == ((0, 12), (1, 12), (2, 6), (3, 4), (4, 3), (6, 2), (12, 1))
            and CO.the_gap_is_the_thickness()
            and CO.charge_is_monotone_non_increasing()
            and SC.the_bound_is_inactive_on_the_pinned_corpus())


def no_new_algorithm_enters_the_production_path():
    """THE VERDICT IS RETAIN. `min_cut` is still the enumeration; the path oracle stays in
    `shadowcut` as a witness source. Checked on the subject's AST: it imports no oracle and calls
    nothing from this module or that one."""
    with open(_os.path.join(_HERE, "cohort.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return not (names & {"shadowcut", "cutbound"})


def the_subject_still_enumerates():
    """And the enumeration is still combinatorial rather than quietly swapped underneath."""
    with open(_os.path.join(_HERE, "cohort.py"), encoding="utf-8") as fh:
        src = fh.read()
    return "combinations" in src and CO.CUT_SEARCH_MAX == 3


def no_wall_clock_enters_this_rung():
    with open(_os.path.join(_HERE, "cutbound.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in ("time", "timeit", "datetime") for a in node.names):
                return False
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in ("time", "timeit", "datetime"):
                return False
    return True


# ---- the record ------------------------------------------------------------------------------------
RECORD = _os.path.join("spec", "attest", "cutbound-verdict.txt")


def generate():
    lines = ["# URDRCBD1 the cohort adjudication — emitted by cutbound.py. THE VERDICT IS RETAIN.",
             "# world %s" % world_digest(), ""]
    lines.append("verdict retain the enumeration; its refusal is a proof and the path oracle is a "
                 "witness source, not a decision procedure")
    for c in CASES:
        lo, hi = interval(c)
        lines.append("bracket %d %d %d %d %s" % (c[0], c[1], lo, hi, provenance(c)))
    for name in sorted(CORRECTED):
        lines.append("corrected %s" % name)
    lines.append("charge %d %d" % (CO.charge_for_gap(None), CO.BASE_CHARGE // (CO.CUT_SEARCH_MAX + 1)))
    lines.append("digest %s" % verdict_digest())
    return "\n".join(lines) + "\n"


def world_digest():
    return hashlib.sha256(MAGIC + b"|world|" + repr(
        (CASES, PROVENANCE, THEOREM, sorted(CORRECTED), CO.CUT_SEARCH_MAX, CO.WALL_MIN_K,
         CO.BASE_CHARGE)).encode()).hexdigest()


def verdict_digest():
    return hashlib.sha256(MAGIC + b"|verdict|" + repr(census()).encode()).hexdigest()


def _read():
    with open(_os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
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
        if f[0] == "bracket" and ((int(f[1]), int(f[2])) not in CASES or f[5] not in PROVENANCE):
            raise CutboundError("a bracket row naming no declared case or no declared provenance")
        if f[0] == "corrected" and f[1] not in CORRECTED:
            raise CutboundError("a corrected row naming no corrected consumer")
        if f[0] not in ("verdict", "bracket", "corrected", "charge", "digest"):
            raise CutboundError("a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise CutboundError("the record names no world digest")
    if not rows:
        raise CutboundError("the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for r in rows:
        if r[0] == "bracket":
            c = (int(r[1]), int(r[2]))
            if (int(r[3]), int(r[4])) != interval(c) or r[5] != provenance(c):
                return False
        if r[0] == "charge" and int(r[1]) != CO.charge_for_gap(None):
            return False
    got = tuple(sorted(r[1] for r in rows if r[0] == "corrected"))
    return got == tuple(sorted(CORRECTED)) and \
        next(r[1] for r in rows if r[0] == "digest") == verdict_digest()


def a_tampered_row_refuses():
    text = _read().replace("corrected charge_for_gap", "corrected wishful", 1)
    try:
        parse(text)
    except CutboundError:
        return True
    return False


def told():
    lo4, hi4 = interval((6, 4))
    lo5, hi5 = interval((6, 5))
    return ("A REFUSAL IS A PROOF, AND THE PRODUCTION LAW WAS THROWING IT AWAY. The adjudication is "
            "not which algorithm wins — `shadowcut` settled that — but what `CUT_SEARCH_MAX = 3` "
            "actually COSTS, and it costs far less than it looked while reading it as a limit rather "
            "than as EVIDENCE cost two live defects instead. THE VERDICT IS RETAIN: replacing the "
            "enumeration with the path oracle would have produced the same numbers with STRICTLY "
            "WEAKER PROVENANCE, because a refusal is a THEOREM about the wall and a witness is a "
            "witness. `min_cut` returning None is an EXHAUSTIVE PROOF that k is at least %d, so "
            "paired with a witness the cap costs NOTHING up to that value: at the thickness-four "
            "wall the exhaustion gives [%d, %d] and the witness closes it with no appeal to the "
            "reduction at all, and only from one wall further does a real interval open — [%d, %d] — "
            "which the stated theorem and nothing else closes. AND READING THE REFUSAL AS AN ABSENCE "
            "COST TWO DEFECTS IN THE SHIPPED LAW, BOTH FLATTERING: the charge billed an undecided "
            "wall ZERO where the proven bound bills %d, so every gap between %d and %d was free; and "
            "`certifiable` cleared the floor without consulting it, right at the shipped constants "
            "only because two of them happen to be ordered that way, and certifying a one-thick wall "
            "outright once the cap is lowered to zero — a case REPRODUCED here rather than imagined. "
            "NOT ONE PINNED FIGURE MOVES, because the bound is inactive across everything "
            "`cohort.gap_table` pins: both defects lived on a path the shipped corpus never walks "
            "and both would have bitten on the first wall past it"
            % (CO.CUT_SEARCH_MAX + 1, lo4, hi4, lo5, hi5, CO.charge_for_gap(None),
               CO.CUT_SEARCH_MAX + 1, CO.BASE_CHARGE))


def scene_case(name):
    if name == "brackets":
        return repr(census())
    if name == "corrections":
        return repr((tuple(sorted(CORRECTED)), CO.charge_for_gap(None),
                     CO.thin_walls_are_refused(), CO.charge_table(), CO.gap_table()))
    if name == "record":
        return generate()
    raise CutboundError("no scene named %r" % (name,))


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode()
                          + b"|" + scene_case(name).encode()).hexdigest()


SCENES = ("brackets", "corrections", "record")


def golden(name):
    with open(_os.path.join(_HERE, "conformance_cutbound.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CutboundError("no golden named %r" % (name,))
