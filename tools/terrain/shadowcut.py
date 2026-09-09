# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""shadowcut (URDRSHC1) — THE PROPOSED REMEDY ANSWERS A DIFFERENT QUESTION.

`cohort` decides its min-cut by enumerating every subset of the wall up to `CUT_SEARCH_MAX = 3` and
returns `None` above that. The weak-spots list names the fix: *"the honest fix is a max-flow
formulation on the vertex-split graph — the shape `auditgraph` already uses."* THIS RUNG BUILDS THAT
FORMULATION AND MEASURES IT, AND IT DOES NOT COMPUTE THE QUANTITY `cohort` IS AFTER.

NOTHING IN `cohort` IS CHANGED. `CUT_SEARCH_MAX` is still 3, `min_cut` is still the enumeration, and
this module IMPORTS both rather than transcribing either. A shadow adjudicator that edits its subject
is not a shadow.

    wall            bounded    shortest    maxflow     cross-section
    (n=3, t=1)            1           1          9              9
    (n=4, t=1)            1           1         16             16
    (n=4, t=2)            2           2         16             16
    (n=5, t=1)            1           1         25             25
    (n=5, t=2)            2           2         25             25
    (n=5, t=3)            3           3         25             25
    (n=6, t=2)            2           2         36             36
    (n=6, t=3)            3           3         36             36
    (n=6, t=4)         None           4         36             36

THE MAX-FLOW COLUMN IS THE CROSS-SECTION AND NOTHING ELSE. It does not move when the wall gets
thicker, because it is not measuring the wall — it counts how many INDEPENDENT TUNNELS could be
driven through the cross-section at once, one per cell of a layer. `cohort` asks what ONE tunnel
COSTS. Those are dual questions and the duality is the whole problem.

WHY THE SHAPE IS WRONG, AND `cohort` HAD ALREADY MEASURED THE REASON. The quantity `min_cut` computes
is a minimum-weight PATH: the fewest wall cells lying on any face-to-face route, since deleting
exactly those opens it. Max-flow computes a minimum CUT. Turning a min-weight path into a min cut is
planar duality — and `cohort.hex_duality_fails_in_3d` is an existing law of the very module the
remedy was proposed for, measured on a 7-cube, stating that the two-dimensional Z2 duality does not
lift to three. THE REMEDY REACHED FOR A DUALITY ITS OWN SUBJECT HAD ALREADY REFUTED, one law away in
the same file.

THE ACTUAL FIX IS SMALLER THAN THE PROPOSED ONE. A minimum-weight path over node weights of ZERO for
free and ONE for wall is decided by a 0-1 BFS in linear time with no cap at all. It agrees with the
enumeration on EVERY case the enumeration can decide, and it decides the case the enumeration cannot.

THE BOUND IS INACTIVE ON THE PINNED CORPUS AND ACTIVE IMMEDIATELY OUTSIDE IT. Across the five cases
`cohort.gap_table` actually pins, every answer is decided and the two formulations agree, so the
`None` branch is unreachable there and the pinned figures were never artefacts of the horizon. One
step outside — a wall of thickness four, an ordinary object — the enumeration returns `None` and the
path oracle returns 4. `CUT_SEARCH_MAX` is therefore not a dormant limit; it is one wall away.

EVERY ANSWER IS WITNESSED BY THE SUBJECT'S OWN PRIMITIVE. The path oracle does not merely report a
number: it returns the wall cells it would delete, and `the_witness_is_adjudicated_by_the_subject`
removes exactly that set and asks `cohort.free_reaches` — the production reachability flood fill —
whether the wall opened. The oracle proposes and the SUBJECT decides, so a defect in the oracle's
own bookkeeping cannot certify itself.

does_not_show: NOTHING IS PROMOTED AND NO PRODUCTION LAW MOVES. `cohort` is untouched, its record
still binds, and whether to replace the enumeration, keep it with a stated theorem, or keep it with a
declared corpus bound is the ADJUDICATION rung's decision and not this one's. THAT THE PATH ORACLE IS
OPTIMAL BEYOND THE ENUMERATION'S REACH: its upper bounds are witnessed cell-by-cell by the subject,
and its LOWER bounds are exhaustively confirmed only where the enumeration reaches, which is three.
Past three, minimality rests on the 0-1 BFS reduction being correct — an argument stated here and not
a measurement. THAT MAX-FLOW IS USELESS: it answers the tunnel-COUNT question exactly, and that
question is simply not the one `cohort` asks. NOTHING ABOUT TIME, and no wall clock enters. AND
NOTHING ABOUT NON-SPANNING WALLS beyond the one plant that fixes the sign: a wall with a hole answers
by its GEOMETRY and not by its thickness parameter.

falsifier: `the_witness_is_adjudicated_by_the_subject` reddens the day an oracle reports a cut whose
own cells, removed, do not open the wall under `cohort`'s flood fill — which would make every number
here unverified; `the_two_oracles_agree_wherever_the_bound_decides` reddens if the independent
formulation ever contradicts the enumeration inside its horizon, which would mean one of them is
wrong and the rung has found it; and `the_max_flow_formulation_answers_a_different_question` reddens
the day vertex-split max-flow tracks the wall thickness after all, which would reopen the remedy the
weak-spots list proposed.
"""
import ast
import hashlib
import os as _os
import sys as _sys
from collections import deque as _deque

_HERE = _os.path.dirname(_os.path.abspath(__file__))
ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import cohort as CO                                             # noqa: E402

MAGIC = b"URDRSHC1"

#: DECLARED — the module whose production law this rung shadows. IMPORTED, never transcribed.
SUBJECT = "cohort"

#: DECLARED — the three formulations. `bounded` is the SUBJECT'S OWN, called through its module.
ORACLES = ("bounded", "shortest", "maxflow")

#: DECLARED — the one that ships. It is not changed by this rung and not scored against the others;
#: it is the thing being asked about.
PRODUCTION = "bounded"

#: DECLARED — the cases `cohort.gap_table` itself pins. Inside this set the bound's activity is a
#: statement about the shipped corpus; outside it, about the world.
PINNED = ((3, 1), (4, 1), (4, 2), (5, 1), (5, 2))

#: DECLARED — the extension, chosen to straddle the horizon rather than to flatter it: (5,3) and
#: (6,3) sit exactly AT the cap and (6,4) one past it, so the boundary is measured from both sides.
EXTENSION = ((5, 3), (6, 2), (6, 3), (6, 4))

CASES = PINNED + EXTENSION

#: DECLARED — what a comparison can come to. `undecided` is not agreement and is not divergence: the
#: enumeration declining to answer is a third thing, and collapsing it into either would be the
#: inflation this rung exists to avoid.
VERDICTS = ("agree", "undecided", "diverge")


class ShadowcutError(Exception):
    """An oracle, a case or a verdict this module will not pretend to have.

    THE CODE IS PREPENDED IN CODE AND NOT DESCRIBED IN A DOCSTRING. The first draft carried
    `SHADOWCUT-REFUSE` only in this docstring, and `authority.has_typed_refusal` reads `code_only`
    — comments and docstrings stripped — so the module scored NO TYPED REFUSAL and the authority
    contract reddened. The predicate was right: a refusal code that lives only in prose is a
    refusal a reader is told about and a caller never sees.
    """

    def __init__(self, message):
        super().__init__("SHADOWCUT-REFUSE: %s" % message)
        self.code = "SHADOWCUT-REFUSE"


def _neighbours(c, n):
    for d in range(3):
        for s in (-1, 1):
            b = list(c)
            b[d] += s
            if 0 <= b[d] < n:
                yield tuple(b)


# ---- the independent formulations ------------------------------------------------------------------
def shortest_cut(wall, n):
    """(k, witness): the fewest WALL cells on any face-to-face path, and WHICH cells.

    A 0-1 BFS over node weights — ZERO for a free cell, ONE for a wall cell — because deleting
    exactly the wall cells lying on a route is what opens that route, and any deletion that opens the
    wall contains some route's wall cells. Linear, exact, and CAPPED AT NOTHING.
    """
    src = tuple(c for c in CO.world(n) if c[0] == 0)
    dist, prev, dq = {}, {}, _deque()
    for c in src:
        w = 1 if c in wall else 0
        if w < dist.get(c, 1 << 30):
            dist[c], prev[c] = w, None
            (dq.appendleft if w == 0 else dq.append)(c)
    best, end = 1 << 30, None
    while dq:
        c = dq.popleft()
        d = dist[c]
        if c[0] == n - 1 and d < best:
            best, end = d, c
        for b in _neighbours(c, n):
            w = 1 if b in wall else 0
            if d + w < dist.get(b, 1 << 30):
                dist[b], prev[b] = d + w, c
                (dq.appendleft if w == 0 else dq.append)(b)
    if end is None:
        raise ShadowcutError("no face-to-face route exists in a %d-cube" % n)
    cells, c = [], end
    while c is not None:
        if c in wall:
            cells.append(c)
        c = prev[c]
    return best, frozenset(cells)


def maxflow_cut(wall, n):
    """Vertex-split max flow from the low face to the high face, node capacity 1 on a WALL cell.

    THE FORMULATION THE WEAK-SPOTS LIST PROPOSED, built faithfully so the measurement is about the
    formulation and not about a strawman. Each cell becomes an in-node and an out-node joined by an
    arc of its capacity; adjacency arcs are unbounded; a super-source feeds the low face and the high
    face drains to a super-sink. Integer augmenting paths, breadth-first, deterministic.
    """
    big = 1 << 20
    cap = {}

    def arc(u, v, c):
        cap.setdefault(u, {})[v] = cap.setdefault(u, {}).get(v, 0) + c
        cap.setdefault(v, {}).setdefault(u, 0)

    for c in CO.world(n):
        arc((c, 0), (c, 1), 1 if c in wall else big)
        for m in _neighbours(c, n):
            arc((c, 1), (m, 0), big)
        if c[0] == 0:
            arc("S", (c, 0), big)
        if c[0] == n - 1:
            arc((c, 1), "T", big)
    flow = 0
    while True:
        prev, q = {"S": None}, _deque(["S"])
        while q and "T" not in prev:
            u = q.popleft()
            for v, r in cap[u].items():
                if r > 0 and v not in prev:
                    prev[v] = u
                    q.append(v)
        if "T" not in prev:
            return flow
        v, aug = "T", big
        while prev[v] is not None:
            aug = min(aug, cap[prev[v]][v])
            v = prev[v]
        v = "T"
        while prev[v] is not None:
            cap[prev[v]][v] -= aug
            cap[v][prev[v]] += aug
            v = prev[v]
        flow += aug


# ---- the comparison --------------------------------------------------------------------------------
_SWEEP = {}


def _wall(n, thick):
    return CO.spanning_wall(n, thick)


def sweep():
    """Every case under every oracle, with the path oracle's witness carried alongside its number."""
    if not _SWEEP:
        for n, t in CASES:
            w = _wall(n, t)
            k, cells = shortest_cut(w, n)
            _SWEEP[(n, t)] = {"bounded": CO.min_cut(w, n), "shortest": k,
                              "maxflow": maxflow_cut(w, n), "witness": cells,
                              "section": n * n}
    return _SWEEP


def answer(case, oracle):
    if case not in CASES:
        raise ShadowcutError("no declared case %r" % (case,))
    if oracle not in ORACLES:
        raise ShadowcutError("no oracle named %r" % (oracle,))
    return sweep()[case][oracle]


def witness(case):
    if case not in CASES:
        raise ShadowcutError("no declared case %r" % (case,))
    return sweep()[case]["witness"]


def cross_section(case):
    if case not in CASES:
        raise ShadowcutError("no declared case %r" % (case,))
    return sweep()[case]["section"]


def compare(case):
    """`agree`, `undecided` or `diverge` — the enumeration against the independent path oracle."""
    b, s = answer(case, "bounded"), answer(case, "shortest")
    if b is None:
        return "undecided"
    return "agree" if b == s else "diverge"


def verdict_census():
    return tuple((v, sum(1 for c in CASES if compare(c) == v)) for v in VERDICTS)


# ---- the laws --------------------------------------------------------------------------------------
def the_witness_is_adjudicated_by_the_subject():
    """THE ORACLE PROPOSES AND THE SUBJECT DECIDES. Every reported cut is handed back to `cohort` as
    a set of cells: removing exactly those must open the wall under the PRODUCTION flood fill, and
    the set's size must equal the number reported. An oracle that scored its own arithmetic would be
    certifying itself."""
    for (n, t) in CASES:
        w = _wall(n, t)
        cells = witness((n, t))
        if len(cells) != answer((n, t), "shortest"):
            return False
        if not cells <= w:
            return False
        if not CO.free_reaches(w - cells, n):
            return False
        if cells and CO.free_reaches(w - frozenset(list(cells)[1:]), n):
            return False          # a strictly smaller subset of the witness must NOT open it
    return True


def the_two_oracles_agree_wherever_the_bound_decides():
    return all(compare(c) == "agree" for c in CASES if answer(c, "bounded") is not None)


def the_bound_is_inactive_on_the_pinned_corpus():
    """Across the cases `cohort` itself pins, the enumeration decides every one and agrees — so the
    pinned gap figures were never artefacts of the search horizon."""
    return all(answer(c, "bounded") is not None and compare(c) == "agree" for c in PINNED)


def the_bound_is_active_immediately_outside_it():
    """And it is one ordinary wall away: at thickness four the enumeration returns `None` while the
    path oracle answers. A limit that bites on the next object is not a dormant limit."""
    return any(answer(c, "bounded") is None and answer(c, "shortest") > CO.CUT_SEARCH_MAX
               for c in CASES)


def the_max_flow_formulation_answers_a_different_question():
    """THE FINDING. Vertex-split max flow returns the CROSS-SECTION on every case and does not move
    with the thickness — it counts how many independent tunnels fit at once, where `cohort` asks what
    ONE tunnel costs."""
    if not all(answer(c, "maxflow") == cross_section(c) for c in CASES):
        return False
    by_n = {}
    for (n, t) in CASES:
        by_n.setdefault(n, set()).add(answer((n, t), "maxflow"))
    thick_varies = any(len({t for (m, t) in CASES if m == n}) > 1 for n in by_n)
    return thick_varies and all(len(v) == 1 for v in by_n.values())


def the_duality_it_needed_was_already_refuted():
    """The reason, and it is the SUBJECT'S OWN law rather than an argument invented here: converting
    a minimum-weight path into a minimum cut is planar duality, and `cohort` measured on a 7-cube
    that the two-dimensional Z2 duality does not lift to three.

    UNPACKED RATHER THAN RETURNED. `hex_duality_fails_in_3d` returns a TRIPLE — free crosses,
    occupied crosses, both — and a non-empty tuple is truthy whatever it contains, so a law that
    handed it straight back could never fail. The first draft of this function did exactly that.
    What the refutation needs is the THIRD element: BOTH crossings true at once is the state 2D
    excludes, and it is asserted here explicitly.
    """
    free_crosses, occupied_crosses, both = CO.hex_duality_fails_in_3d()
    return bool(free_crosses and occupied_crosses and both)


def the_oracles_track_geometry_and_not_the_thickness_parameter():
    """THE PLANT THAT FIXES THE SIGN. A thickness-2 wall with ONE cell removed is answered by its
    geometry: the route through the hole crosses a single wall cell, so both the enumeration and the
    path oracle must say 1 where the parameter still says 2."""
    n, t = 5, 2
    holed = _wall(n, t) - frozenset({(1, 2, 2)})
    k, cells = shortest_cut(holed, n)
    return (k == 1 and CO.min_cut(holed, n) == 1 and len(cells) == 1
            and CO.free_reaches(holed - cells, n))


def a_breached_wall_is_zero_under_both():
    """The degenerate end, checked rather than assumed: a wall that never spanned costs nothing to
    open, which is the defect `cohort`'s own fixture docstring records having shipped once."""
    n = 4
    partial = frozenset((1, y, z) for y in range(n - 1) for z in range(n))
    return CO.verdict(partial, n) == CO.BREACHED and CO.min_cut(partial, n) == 0 \
        and shortest_cut(partial, n)[0] == 0


def the_production_law_is_untouched():
    """`CUT_SEARCH_MAX` still 3 and the enumeration still the subject's. A shadow that edits its
    subject is not a shadow."""
    return CO.CUT_SEARCH_MAX == 3 and CO.min_cut.__module__ == SUBJECT


def the_bounded_search_is_not_transcribed_here():
    """Called through the subject, never reimplemented: this module imports no combinatorial
    enumerator and never builds subsets of a wall. Checked on this module's own AST."""
    with open(_os.path.join(_HERE, "shadowcut.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] == "itertools" for a in node.names):
                return False
        if isinstance(node, ast.ImportFrom) and node.module == "itertools":
            return False
    return True


def nothing_is_promoted():
    """No production law moves. The replace-or-retain decision belongs to the adjudication rung."""
    with open(_os.path.join(_HERE, "shadowcut.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) \
                        and tgt.value.id == "CO":
                    return False
    return True


def no_wall_clock_enters_this_rung():
    with open(_os.path.join(_HERE, "shadowcut.py"), encoding="utf-8") as fh:
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
RECORD = _os.path.join("spec", "attest", "shadowcut-comparison.txt")


def generate():
    lines = ["# URDRSHC1 the shadow comparison — emitted by shadowcut.py. The subject is UNCHANGED.",
             "# world %s" % world_digest(), ""]
    for c in CASES:
        lines.append("case %d %d %s %d %d %s %s"
                     % (c[0], c[1], answer(c, "bounded"), answer(c, "shortest"),
                        answer(c, "maxflow"), cross_section(c),
                        "pinned" if c in PINNED else "extension"))
    for v, k in verdict_census():
        lines.append("verdict %s %d" % (v, k))
    lines.append("digest %s" % comparison_digest())
    return "\n".join(lines) + "\n"


def world_digest():
    return hashlib.sha256(MAGIC + b"|world|"
                          + repr((SUBJECT, ORACLES, PINNED, EXTENSION, VERDICTS,
                                  CO.CUT_SEARCH_MAX)).encode()).hexdigest()


def comparison_digest():
    return hashlib.sha256(MAGIC + b"|comparison|" + repr(
        tuple((c, tuple((o, answer(c, o)) for o in ORACLES), cross_section(c))
              for c in CASES)).encode()).hexdigest()


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
        if f[0] == "case" and ((int(f[1]), int(f[2])) not in CASES or f[7] not in
                               ("pinned", "extension")):
            raise ShadowcutError("a case row naming no declared case or no declared scope")
        if f[0] == "verdict" and f[1] not in VERDICTS:
            raise ShadowcutError("a verdict row naming no declared verdict")
        if f[0] not in ("case", "verdict", "digest"):
            raise ShadowcutError("a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise ShadowcutError("the record names no world digest")
    if not rows:
        raise ShadowcutError("the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for r in rows:
        if r[0] == "case":
            c = (int(r[1]), int(r[2]))
            if (str(answer(c, "bounded")) != r[3] or int(r[4]) != answer(c, "shortest")
                    or int(r[5]) != answer(c, "maxflow") or int(r[6]) != cross_section(c)):
                return False
        if r[0] == "verdict" and int(r[2]) != dict(verdict_census())[r[1]]:
            return False
    return next(r[1] for r in rows if r[0] == "digest") == comparison_digest()


def a_tampered_row_refuses():
    text = _read().replace("verdict agree ", "verdict thrived ", 1)
    try:
        parse(text)
    except ShadowcutError:
        return True
    return False


def told():
    cs = dict(verdict_census())
    return ("THE PROPOSED REMEDY ANSWERS A DIFFERENT QUESTION. `cohort`'s weak-spots list named the "
            "fix for `CUT_SEARCH_MAX = 3` as a max-flow formulation on the vertex-split graph; built "
            "faithfully and measured, VERTEX-SPLIT MAX FLOW RETURNS THE CROSS-SECTION ON EVERY CASE "
            "AND DOES NOT MOVE WITH THE THICKNESS — it counts how many independent tunnels fit at "
            "once, where `cohort` asks what ONE tunnel costs. THE REASON IS THE SUBJECT'S OWN LAW: "
            "converting a minimum-weight PATH into a minimum CUT is planar duality, and "
            "`hex_duality_fails_in_3d` measured on a 7-cube that the two-dimensional Z2 duality does "
            "not lift to three — the remedy reached for a duality its own subject had already "
            "refuted, one law away in the same file. THE ACTUAL FIX IS SMALLER: a 0-1 BFS over node "
            "weights of zero for free and one for wall decides the same quantity in linear time with "
            "NO CAP, and it AGREES with the enumeration on all %d cases the enumeration can decide "
            "while deciding the %d it cannot. THE BOUND IS INACTIVE ON THE PINNED CORPUS AND ACTIVE "
            "IMMEDIATELY OUTSIDE IT: every case `cohort.gap_table` pins is decided and agreed, so "
            "those figures were never artefacts of the horizon, but one ordinary wall further — "
            "thickness four — the enumeration returns None. EVERY ANSWER IS WITNESSED BY THE "
            "SUBJECT'S OWN PRIMITIVE: the path oracle returns the cells it would delete and "
            "`cohort.free_reaches` adjudicates, so a defect in the oracle's bookkeeping cannot "
            "certify itself. AND NOTHING IS PROMOTED — `CUT_SEARCH_MAX` is still 3, `min_cut` is "
            "still the enumeration, and replace-or-retain is the adjudication rung's decision"
            % (cs["agree"], cs["undecided"]))


def scene_case(name):
    if name == "comparison":
        return repr(tuple((c, tuple((o, answer(c, o)) for o in ORACLES), cross_section(c))
                          for c in CASES))
    if name == "witnesses":
        return repr(tuple((c, tuple(sorted(witness(c)))) for c in CASES))
    if name == "verdicts":
        return repr(verdict_census())
    if name == "record":
        return generate()
    raise ShadowcutError("no scene named %r" % (name,))


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode()
                          + b"|" + scene_case(name).encode()).hexdigest()


SCENES = ("comparison", "witnesses", "verdicts", "record")


def golden(name):
    with open(_os.path.join(_HERE, "conformance_shadowcut.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ShadowcutError("no golden named %r" % (name,))
