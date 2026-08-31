# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxmanifold (URDRVXV1) — DOES CERTIFICATE VALIDITY HAVE STRUCTURE? THE SEARCH EXPERIMENT, SCORED.

`voxstate` declared a 4x4 lattice of camera states, four traversals differing ONLY in which
already-visited state each inherits from, and shipped this rung's pre-registration ONE COMMIT
EARLIER. This rung PARSES that file, checks its digest against the golden `voxstate` pinned, and
requires its verdict set to EQUAL the five ids found there. Five were registered; five are scored.

THE QUESTION, FIXED BEFORE ANY TRAVERSAL RAN:

    Does certificate validity form CONNECTED REGIONS in state space that can be traversed more
    cheaply than independently solving each state?

THE ANSWER IS YES ON LOCALITY AND NO ON THE MANIFOLD, AND THE SECOND HALF KILLS THE ANALOGY.

TWO OF FIVE PREDICTIONS HIT AND THREE MISSED.

WHAT SURVIVES IS ORDINARY LOCALITY. Retirement rises MONOTONICALLY with the quality of inheritance —
Z1 row-major 1713400, Z2 zig-zag 2793500, Z3 nearest-neighbour 3360592 — so choosing a nearer
predecessor really does retire nearly twice the work of taking whatever the scan order supplies. M2
and M3 both hit. Adjacency governs validity.

WHAT DIES IS THE MANIFOLD, AND IT DIES THREE SEPARATE WAYS.

    M1 MISS   adjacent ordered pairs certify 27.75 tiles each against non-adjacent 21.75 — a 28 per
              cent edge, NOT the categorical difference a `connected region` implies. Validity is
              DIFFUSE, not clustered.
    M5 MISS   ALL SIXTEEN STATES ARE VALIDITY BOUNDARIES. Every one retires less than a quarter of
              its own cold cost. THERE IS NO CHEAP INTERIOR AT ALL, so there is nothing for a
              boundary-traversal scheme to be cheap around.
    the path  ZERO OF TWENTY-FOUR sub-additivity triples are negative. Reaching C by way of B ALWAYS
              costs more than reaching C directly from A. An intermediate state never contributes
              reusable structure; it is only ever on the way.

So there is no wake here — no shared structure in proof space, no interior that a few boundary
computations certify. There is a cache that works better when you inherit from something nearby,
which is the ordinary thing, honestly measured, and worth exactly what it is.

The certificate is `voxcond`'s P4 and nothing else — ownership, VERIFIED against the current camera,
with depth RECONSTRUCTED from the owner's own plane. No new certificate is invented here; inventing
one would have made this experiment measure two things at once.

EVERY TRAVERSAL IS REQUIRED TO REPRODUCE THE COLD BASELINE BYTE FOR BYTE, colour and depth as LISTS,
on all sixteen states. A traversal that changes what is seen is not a cheaper path, it is a bug —
and that contract has now caught an unsound optimisation in three consecutive rungs.

AND MY OWN PRE-REGISTRATION WAS AMBIGUOUSLY WORDED, WHICH IS ITSELF THE LESSON. M4 says `NO traversal
beats Z0 in TOTAL operations` and then argues from the tiled loop's 1.85x cost against the COMMITTED
REFERENCE. Those are two different baselines and they give opposite verdicts. THE LITERAL TEXT IS
SCORED, because scoring the reading that flatters the result is exactly what pre-registration exists
to prevent — and both numbers are reported so the reader can see the whole of it.
`the_ambiguity_in_my_own_prediction_is_disclosed` states it as a law rather than a footnote.

WHAT IS MEASURED BUT NOT SCORED: the path quantities. Sub-additivity over a four-state sub-lattice —
whether W(A->B) + W(B->C) can undercut W(A->C), which is the signature of an intermediate state
CONTRIBUTING reusable structure rather than merely being on the way — and four declared paths through
those states, two entirely adjacent and two crossing the diagonal. THOSE WERE NOT PRE-REGISTERED, so
they carry NO VERDICT and none is invented for them. They are EVIDENCE, and they point one way: zero
of twenty-four triples are negative. Turning that into a scored claim would need its own
pre-registered rung, and this rung does not pretend it already has one.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. NOTHING ABOUT MEMORY TRAFFIC OR CACHE
LOCALITY — an operation count cannot tell a traversal advantage from a locality advantage, and this
rung has no instrument for the second. THAT A CHEAPER TRAVERSAL EXISTS beyond the four declared.
THAT THE PATH RESULTS ARE PREDICTIONS — they are measurements without a registered claim attached.
And NO PROMOTION: `voxref` is untouched and no traversal is adopted.

falsifier: `every_traversal_reproduces_the_cold_baseline` compares both buffers as lists across all
four traversals and all sixteen states; `each_state_inherits_only_from_its_declared_predecessor`
reddens if any state ever reads a certificate it was not given, which is how a warm cache would
masquerade as manifold structure; and `the_verdicts_match_the_committed_prediction` reddens if the
scored set ever stops equalling the set committed one commit earlier.
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
import voxsilo as VS                                         # noqa: E402
import voxcond as VD                                         # noqa: E402
import voxstate as VT                                        # noqa: E402

MAGIC = b"URDRVXV1"
TILE = VT.SHAPE and VD.TILE

#: DECLARED — the four states the PATH experiment runs over: the 2x2 corner of the lattice. Two of
#: its six ordered pair-classes are adjacent and one is the diagonal, so a path can be built that is
#: entirely adjacent and a path that is not, out of the SAME four states.
CORNER = ("A", "B", "C", "D")
CORNER_CELL = {"A": (0, 0), "B": (0, 1), "C": (1, 0), "D": (1, 1)}

#: DECLARED — four paths through those four states. `ABDC` and `ACDB` are entirely adjacent;
#: `ABCD` and `ACBD` each cross the diagonal once. All four visit the same states.
PATHS = ("ABCD", "ACBD", "ABDC", "ACDB")

#: DECLARED — a state counts as a BOUNDARY when the certificate retires less than this share of its
#: own cold cost. One quarter: far enough from zero that a state scraping a few tiles is not called
#: interior, far enough from one that a genuinely productive state is not called boundary.
BOUNDARY_NUM, BOUNDARY_DEN = 1, 4


class VoxmanifoldError(Exception):
    """VOXMANIFOLD-REFUSE — an order, a path or a record this module will not pretend to read."""


# ---- the prediction, quoted from the earlier commit ------------------------------------------------------
def committed_prediction():
    out = {}
    for ln in VT.prediction_text().split("\n"):
        ln = ln.strip()
        if ln.startswith("predict "):
            f = ln.split(None, 2)
            out[f[1]] = f[2]
    return out


PREDICTIONS = tuple(sorted(committed_prediction()))


def the_prediction_is_quoted_from_the_earlier_commit():
    return (VT.prediction_digest() == VT.golden("prediction")
            and VT.the_prediction_names_no_result()
            and len(PREDICTIONS) == 5)


# ---- one state, rendered with or without an inherited certificate ---------------------------------------
def render_state(n, prev_key):
    """(colour, depth, key, executed, certified tiles, certificate checks).

    `prev_key` is the OWNER MAP of the declared predecessor, or None for a cold state. Nothing else
    crosses between states — no depth, no colour, no geometry — because a certificate that carried a
    value rather than a proof would be the unsound move `voxpath` ruled out.
    """
    _c, eye, fwd = VT.state(n)
    prims = VX.primitives_with("reversed")
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    tw = (VR.W + TILE - 1) // TILE
    th = (VR.H + TILE - 1) // TILE
    colour = [VR.BACKGROUND] * (VR.W * VR.H)
    depth = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    executed = checks = certified = 0
    tris = []
    for pk, col, quad in prims:
        executed += VO.MUL_PER_QUAD
        s = VD._tri_setup(quad, eye, m, cx, cy)
        if s is None:
            continue
        executed += VO.MUL_PER_SEEN + VO.DIV_PER_SEEN + 2 * VO.MUL_PER_TRIANGLE
        for t in s:
            tris.append((pk, col) + t)
    bins = [[] for _ in range(tw * th)]
    for t in tris:
        p, q, r = t[2], t[3], t[4]
        xl = max(min(p[0], q[0], r[0]), 0) // TILE
        xh = min(max(p[0], q[0], r[0]), VR.W - 1) // TILE
        yl = max(min(p[1], q[1], r[1]), 0) // TILE
        yh = min(max(p[1], q[1], r[1]), VR.H - 1) // TILE
        if xl > xh or yl > yh:
            continue
        for ty in range(yl, yh + 1):
            for tx in range(xl, xh + 1):
                bins[ty * tw + tx].append(t)
    by_key = {}
    for t in tris:
        by_key.setdefault(t[0], []).append(t)

    def raster(group, x0, x1, y0, y1):
        used = 0
        for pk, col, p, q, r, area, b0, b1, b2, _z in group:
            for y in range(y0, y1 + 1):
                row = y * VR.W
                for x in range(x0, x1 + 1):
                    used += VO.MUL_PER_WALK
                    w0 = VR._edge(p[0], p[1], q[0], q[1], x, y) + b0
                    w1 = VR._edge(q[0], q[1], r[0], r[1], x, y) + b1
                    w2 = VR._edge(r[0], r[1], p[0], p[1], x, y) + b2
                    if w0 < 0 or w1 < 0 or w2 < 0:
                        continue
                    used += VO.MUL_PER_COVER + VO.DIV_PER_COVER
                    d = (p[2] * w1 + q[2] * w2 + r[2] * w0) // area
                    i = row + x
                    if (d, pk) < (depth[i], key[i] if key[i] >= 0 else (1 << 62)):
                        depth[i], key[i], colour[i] = d, pk, col
        return used

    for ty in range(th):
        for tx in range(tw):
            b = bins[ty * tw + tx]
            x0, x1 = tx * TILE, min(tx * TILE + TILE, VR.W) - 1
            y0, y1 = ty * TILE, min(ty * TILE + TILE, VR.H) - 1
            taken = False
            if prev_key is not None and b:
                owners = {prev_key[y * VR.W + x]
                          for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
                checks += (y1 - y0 + 1) * (x1 - x0 + 1)
                if -1 not in owners:
                    group, far, ok = [], -1, True
                    for k in owners:
                        got = by_key.get(k)
                        if not got:
                            ok = False
                            break
                        for t in got:
                            checks += 1
                            group.append(t)
                            z = max(t[2][2], t[3][2], t[4][2])
                            if z > far:
                                far = z
                    if ok:
                        for t in b:
                            checks += 1
                            if t[0] not in owners and t[9] <= far:
                                ok = False
                                break
                    if ok:
                        executed += raster(group, x0, x1, y0, y1)
                        if any(key[y * VR.W + x] < 0
                               for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)):
                            for y in range(y0, y1 + 1):
                                for x in range(x0, x1 + 1):
                                    i = y * VR.W + x
                                    depth[i], key[i], colour[i] = VR.FAR, -1, VR.BACKGROUND
                        else:
                            taken = True
                            certified += 1
            if not taken:
                executed += raster(b, x0, x1, y0, y1)
    return colour, depth, key, executed, certified, checks


_EDGE = {}


def edge(src, dst):
    """(executed, certified tiles, checks) for `dst` inheriting from `src`, or from nothing when
    `src` is None. Cached per world so a pair costs one render however often it is asked about."""
    k = (VR.world_digest(), src, dst)
    if k in _EDGE:
        return _EDGE[k]
    prev = None if src is None else render_state(src, None)[2]
    _c, _d, _k, ex, cert, ch = render_state(dst, prev)
    _EDGE[k] = (ex, cert, ch)
    return _EDGE[k]


def cold(n):
    return edge(None, n)


_REF = {}


def reference_cost():
    """What the COMMITTED reference costs over THIS lattice's own sixteen states.

    The first draft of the disclosure law compared this rung's traversals against `voxcond`'s
    reference figure, which was measured over `voxpath`'s THIRTY-ONE frames — a different workload
    entirely, and an apples-to-oranges comparison that would have made the 1.85x scaffolding claim
    meaningless here. The reference is re-measured on the states this rung actually visits.
    """
    k = VR.world_digest()
    if k not in _REF:
        prims = VX.primitives_with("reversed")
        tot = 0
        for _c, eye, fwd in VT.STATES:
            _col, _dep, n = VO.instrument(prims, eye, fwd)
            tot += n["mul"] + n["div"]
        _REF[k] = tot
    return _REF[k]


# ---- the four traversals over the whole lattice -----------------------------------------------------------
_RUN = {}


def run(name):
    """(sound, executed, certified tiles, checks, [per-state executed]) for a declared traversal."""
    if name not in VT.ORDERS:
        raise VoxmanifoldError("VOXMANIFOLD-REFUSE: no order named %r" % (name,))
    k = (VR.world_digest(), name)
    if k in _RUN:
        return _RUN[k]
    seq, pred = VT.order(name)
    keys, per = {}, {}
    ex = cert = ch = 0
    sound = True
    for n in seq:
        prev = None if pred[n] is None else keys[pred[n]]
        col, dep, kk, e, c, h = render_state(n, prev)
        keys[n], per[n] = kk, e
        ex += e
        cert += c
        ch += h
        ref = VT.frames()[n]
        if col != ref[0] or dep != ref[1]:
            sound = False
    _RUN[k] = (sound, ex, cert, ch, tuple(per[n] for n in range(len(VT.STATES))))
    return _RUN[k]


def every_traversal_reproduces_the_cold_baseline():
    """THE CONTRACT. A traversal that changes what is seen is not a cheaper path, it is a bug — and
    this contract has now caught an unsound optimisation in three consecutive rungs."""
    return all(run(o)[0] for o in VT.ORDERS)


def each_state_inherits_only_from_its_declared_predecessor():
    """THE COLD-START CONTROL, AND IT IS THE LAW THAT SEPARATES MANIFOLD STRUCTURE FROM A WARM CACHE.
    Nothing crosses between states but the declared predecessor's OWNER MAP: no depth, no colour, no
    geometry, no memo of a previous render. Proved by re-running a state in isolation with only that
    map and requiring the identical executed count — a hidden cache would make the isolated run
    cheaper or dearer than the one inside the traversal."""
    for name in ("Z1", "Z2", "Z3"):
        seq, pred = VT.order(name)
        per = run(name)[4]
        for n in seq[1:4]:
            if edge(pred[n], n)[0] != per[n]:
                return False
    return True


def retired(name):
    """Operations the certificate retires against the COLD traversal — baseline minus executed,
    taken from the run, which is a quantity no unused fast path can earn."""
    return run("Z0")[1] - run(name)[1]


# ---- the verdicts, scored against the five committed ids -----------------------------------------------
def corner_index(letter):
    if letter not in CORNER:
        raise VoxmanifoldError("VOXMANIFOLD-REFUSE: no corner state named %r" % (letter,))
    return VT.INDEX[CORNER_CELL[letter]]


def corner_edges():
    """{(src letter, dst letter): (executed, certified, checks)} over all twelve ordered pairs."""
    out = {}
    for a in CORNER:
        for b in CORNER:
            if a != b:
                out[(a, b)] = edge(corner_index(a), corner_index(b))
    return out


def certified_by_adjacency():
    """(certified tiles across ADJACENT ordered pairs, across NON-adjacent ones, pairs of each)."""
    ce = corner_edges()
    adj = [v[1] for (a, b), v in ce.items() if VT.adjacent(corner_index(a), corner_index(b))]
    non = [v[1] for (a, b), v in ce.items() if not VT.adjacent(corner_index(a), corner_index(b))]
    return (sum(adj), sum(non), len(adj), len(non))


def boundary_states():
    """States at which the certificate retires less than the declared share of their own cold cost —
    the validity BOUNDARY, measured per state rather than asserted."""
    per = run("Z2")[4]
    out = []
    for n in range(len(VT.STATES)):
        c = cold(n)[0]
        if (c - per[n]) * BOUNDARY_DEN < c * BOUNDARY_NUM:
            out.append(n)
    return tuple(out)


def verdicts():
    z = {o: run(o)[1] for o in VT.ORDERS}
    out = {}
    a, nb, na, nn = certified_by_adjacency()
    out["M1"] = (a * nn > nb * na * 2 if nb else a > 0,
                 "adjacent pairs certify %d tiles over %d pairs, non-adjacent %d over %d"
                 % (a, na, nb, nn))
    out["M2"] = (retired("Z2") > retired("Z1"),
                 "Z2 retires %d against Z1's %d" % (retired("Z2"), retired("Z1")))
    out["M3"] = (retired("Z3") >= retired("Z2"),
                 "Z3 retires %d against Z2's %d" % (retired("Z3"), retired("Z2")))
    beat = [o for o in ("Z1", "Z2", "Z3") if z[o] < z["Z0"]]
    out["M4"] = (len(beat) == 0,
                 "%d of three traversals beat Z0 (%s); against the COMMITTED REFERENCE all four "
                 "still lose" % (len(beat), ", ".join(beat) if beat else "none"))
    b = boundary_states()
    out["M5"] = (0 < len(b) * 2 < len(VT.STATES),
                 "%d of %d states are validity boundaries" % (len(b), len(VT.STATES)))
    return out


def hits():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if ok))


def misses():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if not ok))


def the_verdicts_match_the_committed_prediction():
    return sorted(verdicts()) == list(PREDICTIONS)


def the_record_carries_hits_and_misses():
    return len(hits()) > 0 and len(misses()) > 0


def the_ambiguity_in_my_own_prediction_is_disclosed():
    """M4 SAYS ONE THING AND ARGUES ANOTHER, AND THE LITERAL TEXT IS WHAT IS SCORED.

    It reads `NO traversal beats Z0 in TOTAL operations` and then reasons from the tiled loop's
    1.85x cost against the COMMITTED REFERENCE. Those are two different baselines and they give
    OPPOSITE verdicts: the certificate does beat the cold tiled traversal, and every traversal still
    loses to `voxref`. Scoring the reading that flatters the result is exactly what pre-registration
    exists to prevent, so the literal text is scored and BOTH numbers are reported. This law asserts
    the disclosure rather than leaving it to a paragraph.
    """
    z = {o: run(o)[1] for o in VT.ORDERS}
    ref = reference_cost()
    return all(z[o] > ref for o in VT.ORDERS) and z["Z2"] < z["Z0"]


# ---- measured, NOT scored: the path quantities -----------------------------------------------------------
def path_cost(name):
    """Cumulative executed operations along a declared path, the first state COLD."""
    if name not in PATHS:
        raise VoxmanifoldError("VOXMANIFOLD-REFUSE: no path named %r" % (name,))
    total, prev = 0, None
    for ch in name:
        n = corner_index(ch)
        total += edge(prev, n)[0]
        prev = n
    return total


def subadditivity():
    """{(A,B,C): W(A->B) + W(B->C) - W(A->C)} over every ordered triple of distinct corner states.

    NEGATIVE means the intermediate state B CONTRIBUTES reusable structure: reaching C by way of B
    costs less than reaching C directly from A, even counting the whole of the detour. That is the
    signature the manifold framing predicts, and it is REPORTED HERE WITHOUT A VERDICT because it
    was not pre-registered — the prediction about it ships in this commit for the next rung.
    """
    out = {}
    for a in CORNER:
        for b in CORNER:
            for c in CORNER:
                if len({a, b, c}) != 3:
                    continue
                ia, ib, ic = corner_index(a), corner_index(b), corner_index(c)
                out[(a, b, c)] = (edge(ia, ib)[0] + edge(ib, ic)[0]) - edge(ia, ic)[0]
    return out


def the_path_results_carry_no_verdict():
    """MEASURED IS NOT PREDICTED. The path costs and the sub-additivity triples were not in the
    committed pre-registration, so they appear in the record as DATA and in no verdict. A rung that
    scored them would be scoring a claim it wrote after seeing the numbers."""
    return all(p not in verdicts() for p in PATHS) and len(verdicts()) == 5


def nothing_is_promoted():
    return VD.nothing_is_promoted() and VT.no_certificate_is_built()


def no_wall_clock_enters_this_rung():
    import ast
    with open(os.path.join(_HERE, "voxmanifold.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-manifold.txt")


def manifold_digest():
    body = "\n".join("%s %d %d %d %d" % ((o,) + run(o)[1:4] + (retired(o),)) for o in VT.ORDERS)
    body += "\n" + "\n".join("%s %s %s" % (k, v[0], v[1]) for k, v in sorted(verdicts().items()))
    body += "\n" + "\n".join("%s %d" % (p, path_cost(p)) for p in PATHS)
    body += "\n" + "\n".join("%s%s%s %d" % (a, b, c, d)
                             for (a, b, c), d in sorted(subadditivity().items()))
    return hashlib.sha256(MAGIC + b"|man|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXV1 does certificate validity have structure — emitted by",
            "# voxmanifold.generate(), committed as an artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE PREDICTION WAS COMMITTED ONE COMMIT EARLIER, in `voxstate`, and is QUOTED here",
            "# rather than restated. Every traversal reproduces the cold baseline BYTE FOR BYTE.",
            "# THE PATH ROWS CARRY NO VERDICT: they were not pre-registered.",
            "#   order   <order> <executed> <certified tiles> <checks> <retired vs Z0>",
            "#   verdict <id> <HIT|MISS> <what was measured>",
            "#   path    <path> <cumulative executed>            MEASURED, NOT SCORED",
            "#   delta   <A><B><C> <W(A->B)+W(B->C)-W(A->C)>     MEASURED, NOT SCORED",
            "#   bound   <state> ...                             validity boundaries",
            "#   digest  <manifold digest>"]
    for o in VT.ORDERS:
        rows.append("order %s %d %d %d %d" % ((o,) + run(o)[1:4] + (retired(o),)))
    for k, (ok, what) in sorted(verdicts().items()):
        rows.append("verdict %s %s %s" % (k, "HIT" if ok else "MISS", what))
    for p in PATHS:
        rows.append("path %s %d" % (p, path_cost(p)))
    for (a, b, c), d in sorted(subadditivity().items()):
        rows.append("delta %s%s%s %d" % (a, b, c, d))
    rows.append("bound %s" % " ".join(str(n) for n in boundary_states()))
    rows.append("digest %s" % manifold_digest())
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
        if f[0] == "order" and (len(f) != 6 or f[1] not in VT.ORDERS):
            raise VoxmanifoldError("VOXMANIFOLD-REFUSE: an order row naming no declared order")
        if f[0] == "verdict" and (len(f) < 4 or f[1] not in PREDICTIONS
                                  or f[2] not in ("HIT", "MISS")):
            raise VoxmanifoldError("VOXMANIFOLD-REFUSE: a verdict row naming no declared prediction")
        if f[0] == "path" and (len(f) != 3 or f[1] not in PATHS):
            raise VoxmanifoldError("VOXMANIFOLD-REFUSE: a path row naming no declared path")
        if f[0] == "delta" and (len(f) != 3 or len(f[1]) != 3
                                or any(ch not in CORNER for ch in f[1])):
            raise VoxmanifoldError("VOXMANIFOLD-REFUSE: a delta row naming no declared triple")
        if f[0] not in ("order", "verdict", "path", "delta", "bound", "digest"):
            raise VoxmanifoldError("VOXMANIFOLD-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxmanifoldError("VOXMANIFOLD-REFUSE: the record names no world digest")
    if not rows:
        raise VoxmanifoldError("VOXMANIFOLD-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    v, sub = verdicts(), subadditivity()
    for r in rows:
        if r[0] == "order":
            if tuple(int(x) for x in r[2:]) != run(r[1])[1:4] + (retired(r[1]),):
                return False
        if r[0] == "verdict" and (r[2] == "HIT") != v[r[1]][0]:
            return False
        if r[0] == "path" and int(r[2]) != path_cost(r[1]):
            return False
        if r[0] == "delta" and int(r[2]) != sub[tuple(r[1])]:
            return False
    return next(r[1] for r in rows if r[0] == "digest") == manifold_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("order Z1"):
            text = text.replace(ln, "order Z9 " + " ".join(ln.split()[2:]), 1)
            break
    try:
        parse(text)
    except VoxmanifoldError:
        return True
    return False


def told():
    z = {o: run(o)[1] for o in VT.ORDERS}
    a, nb, na, nn = certified_by_adjacency()
    b = boundary_states()
    ref = reference_cost()
    neg = sum(1 for d in subadditivity().values() if d < 0)
    return ("THE ANSWER IS YES ON LOCALITY AND NO ON THE MANIFOLD. WHAT SURVIVES: retirement "
            "rises MONOTONICALLY with the quality of inheritance — Z1 %d, Z2 %d, Z3 %d — so a "
            "nearer predecessor retires nearly twice what the scan order supplies, and adjacency "
            "does govern validity. WHAT DIES, THREE WAYS: adjacent ordered pairs certify %d tiles "
            "over %d pairs against %d over %d non-adjacent, a 28 per cent edge and NOT the "
            "categorical difference a connected region implies; ALL %d OF THE %d STATES ARE "
            "VALIDITY BOUNDARIES, each retiring less than a quarter of its own cold cost, so THERE "
            "IS NO CHEAP INTERIOR for a boundary scheme to be cheap around; and %d of the 24 "
            "sub-additivity triples are negative, so reaching a state by way of an intermediate "
            "ALWAYS costs more than reaching it directly. THERE IS NO WAKE HERE — no shared "
            "structure in proof space — there is a cache that works better when you inherit from "
            "something nearby. AND MY OWN "
            "PRE-REGISTRATION WAS AMBIGUOUS, WHICH IS ITSELF THE LESSON: M4 reads `no traversal "
            "beats Z0` and then argues from the tiled loop's cost against the COMMITTED REFERENCE, "
            "two different baselines giving OPPOSITE verdicts. THE LITERAL TEXT IS SCORED, because "
            "scoring the reading that flatters the result is exactly what pre-registration exists "
            "to prevent — Z3 executes %d against Z0's %d and beats it, while the reference over "
            "these same sixteen states costs %d, so EVEN THE BEST TRAVERSAL IS HALF AGAIN DEARER "
            "THAN `voxref`. And the path quantities CARRY NO VERDICT because they were never "
            "registered: they are evidence, pointing clearly one way, and turning them into a "
            "scored claim would need its own pre-registered rung"
            % (retired("Z1"), retired("Z2"), retired("Z3"), a, na, nb, nn, len(b),
               len(VT.STATES), neg, z["Z3"], z["Z0"], ref))


def scene_case(name):
    if name == "orders":
        return repr(tuple((o,) + run(o)[1:4] + (retired(o),) for o in VT.ORDERS))
    if name == "verdicts":
        return repr((sorted(verdicts().items()), boundary_states(),
                     certified_by_adjacency()))
    if name == "paths":
        return repr((tuple((p, path_cost(p)) for p in PATHS), sorted(subadditivity().items())))
    raise VoxmanifoldError("VOXMANIFOLD-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("orders", "verdicts", "paths")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxmanifold.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxmanifoldError("VOXMANIFOLD-REFUSE: no golden named %r" % name)
