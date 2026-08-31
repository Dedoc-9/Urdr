# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxstate (URDRVXU1) — A STATE LATTICE, AND FOUR WAYS TO WALK IT. NO CERTIFICATE IS BUILT.

`voxcond` established one sound, productive certificate — ownership, VERIFIED rather than remembered
— and refuted every cheap camera-side condition alongside it. The open question it left is not
whether a certificate can be built but whether CERTIFICATE VALIDITY HAS STRUCTURE: does it form
connected regions in state space that can be traversed more cheaply than solving each state cold?

That is a search experiment, and a search experiment needs a space to search. This rung declares one
and measures its raw geometry. NOT ONE CERTIFICATE IS BUILT, COSTED OR EXPLOITED HERE.

TWO AXES, AND ONLY TWO ARE AVAILABLE. Position along the corridor and orientation in yaw. The
geometry of this world is a PURE HASH OF THE SEED, so geometry mutation and streamed-chunk state
cannot be varied without changing `world_digest` and invalidating every frozen record in the tree.
That is a limitation of the corpus rather than of the idea, and it is RECORDED rather than worked
around — a rung that quietly varied the world would have invalidated `voxref`'s census to make its
own lattice more interesting.

FOUR TRAVERSALS, DIFFERING ONLY IN WHICH ALREADY-VISITED STATE EACH STATE INHERITS FROM:

    Z0  independent    no predecessor; every state cold.            THE BASELINE
    Z1  row-major      the previous state in scan order — at a row wrap, NOT adjacent.
    Z2  zig-zag        the previous state in boustrophedon order — ALWAYS adjacent.
    Z3  nearest        the already-visited lattice NEIGHBOUR, breadth-first from the anchor.

The four are required to be PERMUTATIONS OF ONE STATE SET, so no traversal can win by visiting a
different or smaller lattice. Z1 is kept precisely because its row wraps are NOT adjacent: without a
traversal that sometimes inherits from far away, `adjacency helps` would have nothing to be measured
against.

AND ADJACENCY IS DECLARED GEOMETRY, NEVER A VALIDITY CLAIM. `voxcond` refuted the whole family of
camera-side predicates — `the camera barely moved`, `the same voxel cell`, `unchanged occupancy` —
and proved them unsound at an eighth of a voxel. Neighbours in this lattice are neighbours in the
DECLARED parameterisation and that licenses nothing whatsoever about their observables;
`adjacency_is_not_a_validity_claim` runs `voxcond`'s refutations here so the dead family cannot be
quietly resurrected as an assumption about this lattice.

WHAT IS MEASURED: the raw observable distance across every adjacent pair, and across each
traversal's own predecessor pairs. That is the structure BEFORE any certificate is asked about it,
which is what makes the next rung's answer meaningful rather than circular.

AND THE MEASUREMENT IMMEDIATELY KILLED THIS RUNG'S FIRST LAW, WHICH IS THE USEFUL PART. That law
demanded the lattice span a wide range of observable distance — near-identical states at one end,
unrelated ones at the other — on the assumption that distance is what a certificate tracks. IT IS
NOT. EVERY adjacent pair already differs at 4241 to 6472 of 6912 pixels: A QUARTER OF A VOXEL
SATURATES THE OBSERVABLE, exactly as `voxpath` predicted, because depth is a continuous function of
camera position and a thirty-second of a voxel already moves it almost everywhere. THERE IS NO STEP
SIZE SHORT OF ZERO AT WHICH OBSERVABLE DISTANCE DISCRIMINATES.

That is a constraint on the next rung rather than a defect in this one, and a useful one: since all
distances are comparable, DISTANCE CANNOT CONFOUND a comparison between adjacent and non-adjacent
inheritance. The four traversals are alike in distance — Z1's worst reaches 6480 against Z2's 6420 —
and differ only in STRUCTURE, Z1 carrying three NON-ADJACENT inheritances against Z2's and Z3's
none. Any difference the next rung finds is therefore structural by construction.

THE PREDICTION FOR THE NEXT RUNG SHIPS IN THIS COMMIT, ONE COMMIT BEFORE ANY TRAVERSAL RUNS —
`voxcond`'s precedent, and the only mechanism that actually proves a prediction came first.

does_not_show: NOTHING ABOUT CERTIFICATES — not one is built, costed or exploited. NOTHING ABOUT
TIME, and no wall clock enters. THAT THE STEP SIZES ARE GOOD ONES: a different pair would move every
figure the next rung reports, and its verdicts will be about THIS lattice. THAT TWO AXES ARE ENOUGH
to describe a real engine's state; they are what this corpus admits. And NOTHING IS ALTERED —
`voxref`, `voxpath` and the frozen census are untouched.

falsifier: `the_orders_are_permutations_of_one_lattice` reddens if any traversal ever visits a
different state set; `the_zigzag_is_always_adjacent_and_the_scan_is_not` reddens if the two stop
differing, which is the day the comparison the next rung depends on becomes vacuous; and
`adjacency_is_not_a_validity_claim` reddens if `voxcond`'s refutations stop biting.
"""
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
import voxpath as VP                                         # noqa: E402
import voxcond as VD                                         # noqa: E402

MAGIC = b"URDRVXU1"
Q = VR.Q

#: DECLARED — the two axes, and the ONLY two this world admits. Geometry mutation and streamed-chunk
#: state cannot be varied without changing `world_digest` and invalidating every frozen record.
AXES = ("position", "orientation")

#: DECLARED — the lattice shape. Sixteen states: small enough to run four traversals over inside a
#: deterministic gate, large enough for a region to be connected rather than a pair.
SHAPE = (4, 4)

#: DECLARED — the steps. Position moves a QUARTER of a voxel, between `voxpath`'s creep and its
#: sprint. Yaw moves 4 parts in 64, about three and a half degrees, between `voxpath`'s pan and its
#: whip. Both straddle the range where the previous rungs found the observable to change materially
#: but not entirely.
POS_STEP = 64
YAW_STEP = 4

#: DECLARED — the anchor, taken from `voxpath`'s corridor so this lattice sits in the world the
#: previous rung already characterised rather than somewhere new and unmeasured.
ANCHOR_EYE = (VP.COLUMN[0] * Q + 128, -6 * Q, VP.COLUMN[1] * Q + 128)

#: DECLARED — the four traversals.
ORDERS = ("Z0", "Z1", "Z2", "Z3")


class VoxstateError(Exception):
    """VOXSTATE-REFUSE — a state, an order or a record this module will not pretend to read."""


def _states():
    out = []
    for i in range(SHAPE[0]):
        for j in range(SHAPE[1]):
            eye = (ANCHOR_EYE[0], ANCHOR_EYE[1] + i * POS_STEP, ANCHOR_EYE[2])
            out.append(((i, j), eye, (j * YAW_STEP, 64, 0)))
    return tuple(out)


#: The frozen lattice. Sixteen states, materialised once so every consumer reads one fixed set.
STATES = _states()
INDEX = {c: n for n, (c, _e, _f) in enumerate(STATES)}


def state(n):
    if not 0 <= n < len(STATES):
        raise VoxstateError("VOXSTATE-REFUSE: no state numbered %r" % (n,))
    return STATES[n]


def adjacent(a, b):
    """Neighbours in the DECLARED parameterisation — one step on exactly one axis. This is geometry
    and it licenses NOTHING about the two observables."""
    ca, cb = STATES[a][0], STATES[b][0]
    return abs(ca[0] - cb[0]) + abs(ca[1] - cb[1]) == 1


def order(name):
    """(visit sequence, {state: predecessor or None}) for a declared traversal."""
    if name not in ORDERS:
        raise VoxstateError("VOXSTATE-REFUSE: no order named %r" % (name,))
    rows, cols = SHAPE
    if name == "Z0":
        seq = list(range(len(STATES)))
        return tuple(seq), {n: None for n in seq}
    if name == "Z1":
        seq = list(range(len(STATES)))
    elif name == "Z2":
        seq = []
        for i in range(rows):
            rng = range(cols) if i % 2 == 0 else range(cols - 1, -1, -1)
            seq += [INDEX[(i, j)] for j in rng]
    else:
        seq, seen, frontier = [], set(), [INDEX[(0, 0)]]
        while frontier:
            n = frontier.pop(0)
            if n in seen:
                continue
            seen.add(n)
            seq.append(n)
            ci, cj = STATES[n][0]
            for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                c = (ci + di, cj + dj)
                if c in INDEX and INDEX[c] not in seen and INDEX[c] not in frontier:
                    frontier.append(INDEX[c])
    pred = {seq[0]: None}
    for k in range(1, len(seq)):
        if name == "Z3":
            done = set(seq[:k])
            cand = [p for p in done if adjacent(seq[k], p)]
            pred[seq[k]] = min(cand) if cand else seq[k - 1]
        else:
            pred[seq[k]] = seq[k - 1]
    return tuple(seq), pred


def the_orders_are_permutations_of_one_lattice():
    """NO TRAVERSAL MAY WIN BY VISITING A DIFFERENT OR SMALLER LATTICE. Every order must be a
    permutation of the same sixteen states — the one property without which the next rung's
    comparison would be between four different experiments."""
    want = sorted(range(len(STATES)))
    return all(sorted(order(o)[0]) == want for o in ORDERS)


def the_baseline_inherits_nothing():
    """Z0 is the cold baseline: every state solved independently, no predecessor anywhere."""
    return all(p is None for p in order("Z0")[1].values())


def the_other_orders_inherit_everywhere_but_the_first():
    return all(sum(1 for p in order(o)[1].values() if p is not None) == len(STATES) - 1
               for o in ORDERS if o != "Z0")


def nonadjacent_inheritances(name):
    """How many of a traversal's predecessor pairs are NOT lattice-adjacent."""
    seq, pred = order(name)
    return sum(1 for n in seq if pred[n] is not None and not adjacent(n, pred[n]))


def the_zigzag_is_always_adjacent_and_the_scan_is_not():
    """THE COMPARISON THE NEXT RUNG DEPENDS ON, ASSERTED HERE SO IT CANNOT GO VACUOUS. Z1 is kept
    precisely because its row wraps inherit from a state far away in the lattice; without a
    traversal that sometimes reaches across, `adjacency helps` would have nothing to be measured
    against. If these two ever stop differing, the experiment loses its control."""
    return (nonadjacent_inheritances("Z2") == 0
            and nonadjacent_inheritances("Z3") == 0
            and nonadjacent_inheritances("Z1") > 0)


def adjacency_is_not_a_validity_claim():
    """THE DEAD FAMILY STAYS DEAD. `voxcond` refuted every cheap camera-side predicate — `the camera
    barely moved`, `the same voxel cell`, `unchanged occupancy` — and proved them UNSOUND at an
    eighth of a voxel. Neighbours in this lattice are neighbours in the DECLARED parameterisation
    and that licenses nothing whatsoever about their observables. The refutations are RUN here, not
    cited, so the family cannot be quietly resurrected as an assumption about this lattice."""
    return VD.the_unsound_predicates_are_still_unsound()


def the_world_admits_no_third_axis():
    """RECORDED RATHER THAN WORKED AROUND. The world is a pure hash of its seed, so mutating geometry
    to add an axis would change `world_digest` and invalidate every frozen record in the tree. The
    lattice therefore has two axes, and a rung that quietly varied the world to get a third would
    have broken `voxref`'s census to make its own experiment more interesting."""
    return len(AXES) == 2 and VO.nothing_is_optimised()


# ---- the raw geometry, before any certificate is asked about it ---------------------------------------
_FR = {}


def frames():
    k = VR.world_digest()
    if k not in _FR:
        prims = VX.primitives_with("reversed")
        _FR[k] = [VR.render(prims, e, f) for _c, e, f in STATES]
    return _FR[k]


def distance(a, b):
    """Pixels at which the observable differs. BOTH halves of `O_t`, `voxpath`'s definition."""
    fa, fb = frames()[a], frames()[b]
    return sum(1 for i in range(len(fa[0]))
               if fa[0][i] != fb[0][i] or fa[1][i] != fb[1][i])


def adjacent_pairs():
    return tuple((a, b) for a in range(len(STATES)) for b in range(a + 1, len(STATES))
                 if adjacent(a, b))


def adjacent_span():
    """(nearest, farthest, total) observable distance over every adjacent pair."""
    d = [distance(a, b) for a, b in adjacent_pairs()]
    return (min(d), max(d), VR.W * VR.H)


def order_span(name):
    """(nearest, farthest, total) over one traversal's own predecessor pairs."""
    seq, pred = order(name)
    d = [distance(n, pred[n]) for n in seq if pred[n] is not None]
    if not d:
        raise VoxstateError("VOXSTATE-REFUSE: order %r inherits nothing" % (name,))
    return (min(d), max(d), VR.W * VR.H)


def every_state_is_distinct():
    """The same standard `voxref` and `voxpath` hold their traces to: a state the observable cannot
    tell from another is a state bought and not paid for."""
    return len({VR.observable(*f) for f in frames()}) == len(STATES)


def the_observable_distance_is_saturated():
    """THE FIRST DRAFT OF THIS LAW ASKED THE WRONG QUESTION AND REDDENED, AND THE CORRECTION IS THE
    USEFUL PART.

    It demanded that adjacent states span a wide range of observable distance — near-identical at
    one end, unrelated at the other — on the assumption that distance is what a certificate tracks.
    IT IS NOT, AND THE LATTICE SAYS SO: EVERY adjacent pair already differs at 4241 to 6472 of 6912
    pixels. A QUARTER OF A VOXEL SATURATES THE OBSERVABLE, and `voxpath` already showed why — depth
    is a continuous function of camera position and a thirty-second of a voxel moves it almost
    everywhere. THERE IS NO STEP SIZE SHORT OF ZERO AT WHICH OBSERVABLE DISTANCE DISCRIMINATES.

    That is a constraint on the next rung rather than a defect in this one, and a useful one: since
    all distances are comparable, distance CANNOT CONFOUND a comparison between adjacent and
    non-adjacent inheritance. The next rung must measure certificate validity DIRECTLY, and when it
    does, nothing about the geometry will be secretly explaining its answer.
    """
    lo, hi, n = adjacent_span()
    return lo * 5 > 3 * n and hi < n and hi > lo


def the_traversals_are_alike_in_distance_and_differ_in_structure():
    """AND THIS IS THE SAME FINDING FROM THE OTHER SIDE. Because distance is saturated, the four
    traversals' predecessor pairs are nearly indistinguishable by it — so any difference the next
    rung finds between them is STRUCTURAL, which is exactly the variable this lattice was built to
    isolate. Z1 carries 3 NON-ADJACENT inheritances and Z2 and Z3 carry none; that, and not
    distance, is what separates them."""
    z1, z2, z3 = order_span("Z1"), order_span("Z2"), order_span("Z3")
    close = all(abs(a[1] - b[1]) * 20 < a[2] for a, b in ((z1, z2), (z1, z3), (z2, z3)))
    return close and nonadjacent_inheritances("Z1") > 0 == nonadjacent_inheritances("Z2")


def no_certificate_is_built():
    return VO.nothing_is_optimised() and VD.nothing_is_promoted()


def no_wall_clock_enters_this_rung():
    import ast
    with open(os.path.join(_HERE, "voxstate.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


# ---- the prediction, shipped one commit before the traversals -------------------------------------------
PREDICTION_RECORD = os.path.join("spec", "attest", "voxmanifold-prediction.txt")


def prediction_text():
    with open(os.path.join(ROOT, PREDICTION_RECORD), encoding="utf-8") as fh:
        return fh.read()


def prediction_digest():
    return hashlib.sha256(MAGIC + b"|pred|" + prediction_text().encode()).hexdigest()


def the_prediction_ships_before_the_traversals():
    """`voxcond`'s precedent: COMMIT ORDER is the only mechanism that proves a prediction came
    first. The five predictions `voxmanifold` must score are committed HERE with their digest pinned
    as this rung's golden; the traversals land in a LATER commit."""
    t = prediction_text()
    ids = [p for p in ("M1", "M2", "M3", "M4", "M5") if ("predict %s " % p) in t]
    return len(ids) == 5 and prediction_digest() == golden("prediction")


def the_prediction_names_no_result():
    return all(not ln.startswith("verdict ") for ln in prediction_text().split("\n"))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-lattice.txt")


def lattice_digest():
    body = "\n".join("%d %s %s %s" % (n, c, e, f) for n, (c, e, f) in enumerate(STATES))
    body += "\n" + "\n".join("%d %d %d" % (a, b, distance(a, b)) for a, b in adjacent_pairs())
    body += "\n" + "\n".join("%s %s" % (o, order(o)[0]) for o in ORDERS)
    return hashlib.sha256(MAGIC + b"|lat|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXU1 a state lattice and four ways to walk it — emitted by voxstate.generate(),",
            "# committed as an artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# NOT ONE CERTIFICATE IS BUILT, COSTED OR EXPLOITED HERE. This rung declares the space",
            "# the next one searches and measures its RAW geometry, so the next rung's answer is",
            "# meaningful rather than circular.",
            "#   state <n> <cell> <eye> <forward>",
            "#   near  <a> <b> <observable distance>      adjacent pairs only",
            "#   walk  <order> <non-adjacent inheritances> <nearest> <farthest> <total>",
            "#   span  <nearest> <farthest> <total>       over every adjacent pair",
            "#   digest <lattice digest>"]
    for n, (c, e, f) in enumerate(STATES):
        rows.append("state %d %d,%d %d,%d,%d %d,%d,%d" % ((n,) + tuple(c) + tuple(e) + tuple(f)))
    for a, b in adjacent_pairs():
        rows.append("near %d %d %d" % (a, b, distance(a, b)))
    for o in ORDERS:
        if o == "Z0":
            rows.append("walk Z0 0 0 0 %d" % (VR.W * VR.H))
            continue
        rows.append("walk %s %d %d %d %d" % ((o, nonadjacent_inheritances(o)) + order_span(o)))
    rows.append("span %d %d %d" % adjacent_span())
    rows.append("digest %s" % lattice_digest())
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
        if f[0] == "state" and len(f) != 5:
            raise VoxstateError("VOXSTATE-REFUSE: a state row of the wrong arity")
        if f[0] == "near" and len(f) != 4:
            raise VoxstateError("VOXSTATE-REFUSE: a near row of the wrong arity")
        if f[0] == "walk" and (len(f) != 6 or f[1] not in ORDERS):
            raise VoxstateError("VOXSTATE-REFUSE: a walk row naming no declared order")
        if f[0] == "span" and len(f) != 4:
            raise VoxstateError("VOXSTATE-REFUSE: a span row of the wrong arity")
        if f[0] not in ("state", "near", "walk", "span", "digest"):
            raise VoxstateError("VOXSTATE-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxstateError("VOXSTATE-REFUSE: the record names no world digest")
    if not rows:
        raise VoxstateError("VOXSTATE-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for r in rows:
        if r[0] == "near" and int(r[3]) != distance(int(r[1]), int(r[2])):
            return False
        if r[0] == "walk" and r[1] != "Z0":
            if tuple(int(x) for x in r[2:]) != (nonadjacent_inheritances(r[1]),) + order_span(r[1]):
                return False
        if r[0] == "span" and tuple(int(x) for x in r[1:]) != adjacent_span():
            return False
    return next(r[1] for r in rows if r[0] == "digest") == lattice_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("walk Z1"):
            text = text.replace(ln, "walk Z9 " + " ".join(ln.split()[2:]), 1)
            break
    try:
        parse(text)
    except VoxstateError:
        return True
    return False


def told():
    lo, hi, n = adjacent_span()
    z1, z2 = order_span("Z1"), order_span("Z2")
    return ("A %dx%d LATTICE OF %d CAMERA STATES ON THE ONLY TWO AXES THIS WORLD ADMITS — position "
            "and orientation — because the geometry is a PURE HASH OF ITS SEED and mutating it to "
            "add a third would change `world_digest` and invalidate every frozen record in the "
            "tree, a limitation RECORDED rather than worked around. Four traversals differing ONLY "
            "in which already-visited state each inherits from, all four required to be "
            "PERMUTATIONS OF ONE STATE SET so none can win by visiting a smaller lattice. Adjacent "
            "states differ at %d to %d of %d pixels: A QUARTER OF A VOXEL SATURATES THE "
            "OBSERVABLE, exactly as `voxpath` predicted it would, and THERE IS NO STEP SIZE SHORT "
            "OF ZERO AT WHICH OBSERVABLE DISTANCE DISCRIMINATES. That is a constraint on the next "
            "rung and a useful one — since all distances are comparable, distance CANNOT CONFOUND a "
            "comparison between adjacent and non-adjacent inheritance. Z1's worst inheritance "
            "reaches %d against Z2's %d, near enough to be the same number, so the traversals are "
            "ALIKE IN DISTANCE AND DIFFER IN STRUCTURE: Z1 carries %d NON-ADJACENT inheritances "
            "against Z2's and Z3's none, and that is the control the next rung depends on. AND ADJACENCY IS DECLARED GEOMETRY, "
            "NEVER A VALIDITY CLAIM: `voxcond` refuted every cheap camera-side predicate and its "
            "refutations are RUN here, not cited, so the dead family cannot be resurrected as an "
            "assumption about this lattice"
            % (SHAPE[0], SHAPE[1], len(STATES), lo, hi, n, z1[1], z2[1],
               nonadjacent_inheritances("Z1")))


def scene_case(name):
    if name == "lattice":
        return repr((STATES, tuple((o, order(o)) for o in ORDERS)))
    if name == "geometry":
        return repr((tuple((a, b, distance(a, b)) for a, b in adjacent_pairs()),
                     adjacent_span(),
                     tuple((o, order_span(o)) for o in ORDERS if o != "Z0"),
                     tuple((o, nonadjacent_inheritances(o)) for o in ORDERS)))
    if name == "prediction":
        return prediction_text()
    raise VoxstateError("VOXSTATE-REFUSE: no scene named %r" % name)


def scene_result(name):
    if name == "prediction":
        return prediction_digest()
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("lattice", "geometry", "prediction")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxstate.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxstateError("VOXSTATE-REFUSE: no golden named %r" % name)
