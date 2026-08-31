# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcond (URDRVXQ1) — FIVE CONDITIONAL CERTIFICATES, SCORED AGAINST A PREDICTION COMMITTED FIRST.

`voxpath` declared a continuous walk and shipped this rung's pre-registration ONE COMMIT EARLIER, as
`spec/attest/voxcond-prediction.txt`. This rung does not restate it: it PARSES that file, checks its
digest against the golden `voxpath` pinned, and requires its own verdict set to equal the id set
found there. A prediction that must be quoted from an earlier commit cannot be written after the
result — which is the debt `voxsilo` opened and this rung pays.

THE QUESTION, FIXED BEFORE THE ARMS RAN:

    Under what observable conditions does a certificate retire MORE exact work than it costs to
    establish, test and maintain — while `O_t` remains BYTE-IDENTICAL?

Each predicate is measured on THREE quantities and no fewer, because a scheme reporting only the
third is reporting the half of the ledger it chose: PREDICATE COST, VALIDITY POPULATION, WORK
RETIRED. And each is run as an ARM — the certificate is actually used, and the resulting buffers are
compared to the reference AS LISTS on all 31 frames.

    P1  still            SOUND, and it wins.        The trivial one.
    P2  near_step        UNSOUND.                   Caught by the contract.
    P3  same_cell        UNSOUND, worse.            Caught by the contract.
    P4  same_owner       SOUND, AND IT PAYS.        The prediction said it would not.
    P5  same_occupancy   UNSOUND.                   Sound-looking and not sufficient.

THREE OF FIVE PREDICTIONS HIT AND TWO MISSED, AND THE TWO MISSES ARE THE RESULT.

D4 said an ownership certificate would cost more than it retires, because determining which
primitive owns a tile IS the work. THAT IS WRONG, and the error is instructive: the certificate does
not DETERMINE ownership, it VERIFIES a remembered owner, and verifying is far cheaper than searching.
D5 said no cheap non-trivial condition would be both sound and productive. P4 is exactly that. A
pre-registration that landed all five would have been luck or hindsight; these two are neither.

THE STRUCTURAL RESULT ON THE OTHER THREE: EVERY CHEAP CAMERA-SIDE PREDICATE IS UNSOUND, AND ALL FOR
THE SAME REASON — the reason `voxpath` measured. THE CAMERA MOVED. Depth is a continuous function of
camera position and `O_t` contains it exactly, so `the camera barely moved` licenses nothing at all —
not a pixel, not a tile, not a frame. `voxsilo` caught the naive hierarchical-Z cull with this same
contract; this rung catches three more, and none of them would have looked wrong on inspection.

AND P4 IS WHY THE RUNG EXISTS. An ownership certificate does NOT license reusing a tile's pixels —
that is exactly the unsound move — it licenses skipping the SEARCH for the owner while the depth is
RECONSTRUCTED from the owner's own plane. That is `voxpath`'s conclusion turned into an arm: the
certificate is executable proof about WHO owns the pixel, and the value is derived rather than
remembered. IT RETIRES 4038404 OPERATIONS FOR 210871 SPENT — NINETEEN TIMES.

AND THE NINETEEN TIMES MUST NEVER BE QUOTED ALONE. That figure is measured against the TILED LOOP the
certificate sits on, which is the only comparison in which the certificate is the single variable —
and THAT LOOP COSTS 42913656 OPERATIONS AGAINST THE COMMITTED REFERENCE'S 23201850. The certificate
saves four million on a loop that spends twenty million extra, so THE ARRANGEMENT AS A WHOLE RETIRES
NOTHING. The mechanism is ESTABLISHED and the implementation is NOT COMPETITIVE, and those are
different sentences; `the_loop_it_sits_on_loses_against_the_reference` exists so the first can never
be reported without the second.

THIS RUNG'S FIRST DRAFT SHIPPED THE DEFECT ITS OWN DISCIPLINE EXISTS TO CATCH, and the law that now
forbids it was written because of it. That draft computed P4's certificate, counted what it WOULD
have saved, and then rasterised the whole bin anyway — so its buffers matched the reference for the
trivial reason that it had done all the work, and its retirement was a formula wearing a
measurement's name. `retired` is now BASELINE MINUS EXECUTED, taken from the run, and
`the_fast_path_is_actually_taken` requires it to be positive.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters — `voxwork`'s structural rule. NOTHING
ABOUT MEMORY, which is where an ownership map's storage would be paid and this rung has no
instrument for it. THAT A CHEAPER SOUND PREDICATE DOES NOT EXIST — five were declared and five were
measured, and the space of conditions is not five things. THAT P4'S IMPLEMENTATION IS THE CHEAPEST
POSSIBLE ONE: a different candidate-rejection test would move its cost, and the verdict is about
THIS certificate rather than about ownership certificates in general. And NO PROMOTION: `voxref` is
untouched and not one certificate is adopted.

falsifier: `every_arm_is_checked_against_the_reference` compares both buffers as lists on all 31
frames for every arm and reddens if an unsound certificate ever goes unnoticed; `the_unsound_
predicates_are_still_unsound` REQUIRES the three refuted conditions to keep moving the observable,
so the refutation cannot rot into a comment; and `the_verdicts_match_the_committed_prediction`
reddens if the scored set ever stops equalling the set committed one commit earlier.
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
import voxpath as VP                                         # noqa: E402

MAGIC = b"URDRVXQ1"
Q = VR.Q

#: DECLARED — the tile edge, INHERITED from `voxsilo` rather than restated, so the two rungs cannot
#: drift into measuring different geometries and calling both "the tile".
TILE = VS.TILE

#: DECLARED — `near_step`'s epsilon, in Q8 units. An EIGHTH of a voxel: far smaller than any motion
#: a player makes and far larger than nothing, so a failure here is a failure of the IDEA rather
#: than of a badly chosen constant.
EPS = 32

#: DECLARED — the three quantities every predicate is measured on. A scheme reporting only the third
#: is reporting the half of the ledger it chose.
QUANTITIES = ("cost", "population", "retired")


class VoxcondError(Exception):
    """VOXCOND-REFUSE — a predicate, a quantity or a record this module will not pretend to read."""


# ---- the prediction, quoted from the earlier commit ------------------------------------------------------
def committed_prediction():
    """The pre-registration, PARSED from the file `voxpath` committed one commit earlier — never
    restated here, because a restatement is a copy and a copy can drift."""
    text = VP.prediction_text()
    preds, verds = {}, {}
    for ln in text.split("\n"):
        ln = ln.strip()
        if ln.startswith("predicate "):
            f = ln.split(None, 2)
            preds[f[1]] = f[2]
        elif ln.startswith("predict "):
            f = ln.split(None, 2)
            verds[f[1]] = f[2]
    return preds, verds


def the_prediction_is_quoted_from_the_earlier_commit():
    """THE DEBT `voxsilo` OPENED, PAID. The file's digest must equal the golden `voxpath` pinned in
    the previous commit, so this rung cannot edit the prediction it is about to score."""
    return (VP.prediction_digest() == VP.golden("prediction")
            and VP.the_prediction_names_no_result())


PREDICATES = tuple(sorted(committed_prediction()[0]))
PREDICTIONS = tuple(sorted(committed_prediction()[1]))


def _check(pid):
    if pid not in PREDICATES:
        raise VoxcondError("VOXCOND-REFUSE: no predicate named %r" % (pid,))
    return pid


# ---- the predicates ------------------------------------------------------------------------------------
def cone_cells(eye, fwd):
    """The solid cells the view cone meets, cheaply over-approximated by the lattice cells whose
    centre lies in front of the near plane. DELIBERATELY CONSERVATIVE: an over-approximation can
    only make P5 hold LESS often, so a generous predicate cannot be accused of being rigged."""
    m = VR.basis(fwd)
    out = []
    for cx in range(12):
        for cy in range(12):
            for cz in range(12):
                if not VR.solid(cx, cy, cz):
                    continue
                v = (cx * Q + 128, cy * Q + 128, cz * Q + 128)
                if VR._project(v, eye, m)[1] >= VR.NEAR:
                    out.append((cx, cy, cz))
    return frozenset(out)


def holds(pid, i):
    """(does the predicate hold between frame i-1 and frame i, exact operations spent deciding)."""
    _check(pid)
    if i <= 0:
        raise VoxcondError("VOXCOND-REFUSE: no frame precedes index %r" % (i,))
    a, b = VP.PATH[i - 1], VP.PATH[i]
    ea, fa, eb, fb = a[2], a[3], b[2], b[3]
    if pid == "P1":
        return (ea == eb and fa == fb, 6)
    if pid == "P2":
        d = sum((eb[k] - ea[k]) ** 2 for k in range(3))
        return (fa == fb and d < EPS * EPS, 6 + 4)
    if pid == "P3":
        ca = tuple(v // Q for v in ea)
        cb = tuple(v // Q for v in eb)
        return (fa == fb and ca == cb, 6 + 6)
    if pid == "P5":
        sa, sb = cone_cells(ea, fa), cone_cells(eb, fb)
        return (sa == sb, 2 * 12 * 12 * 12 * 9)
    return (None, 0)          # P4 is a TILE predicate and is decided inside its own arm


# ---- the reference, and the work a frame costs ------------------------------------------------------------
_REF = {}


def reference():
    """[(colour, depth)] over `voxpath.PATH`, from the COMMITTED reference and nothing else."""
    k = VR.world_digest()
    if k not in _REF:
        prims = VX.primitives_with("reversed")
        _REF[k] = [VR.render(prims, eye, fwd) for _e, _n, eye, fwd in VP.PATH]
    return _REF[k]


_COST = {}


def frame_cost():
    """[operations a frame costs from scratch] — multiplies plus divides, taken from `voxwork`'s
    instrument so the baseline is the COMMITTED ruler rather than one this rung invented."""
    k = VR.world_digest()
    if k not in _COST:
        prims = VX.primitives_with("reversed")
        out = []
        for _e, _n, eye, fwd in VP.PATH:
            _c, _d, n = VO.instrument(prims, eye, fwd)
            out.append(n["mul"] + n["div"])
        _COST[k] = out
    return _COST[k]


# ---- the frame-level arms ------------------------------------------------------------------------------
_ARM = {}


def arm(pid):
    """(sound, cost, population, retired) — the certificate USED, not merely evaluated.

    Where the predicate holds the previous frame is REUSED WHOLE; where it does not the frame is
    rendered. `sound` is the byte-identity of every resulting buffer against the reference, compared
    AS LISTS, which is the only thing that decides whether a certificate is a certificate.
    """
    _check(pid)
    k = (VR.world_digest(), pid)
    if k in _ARM:
        return _ARM[k]
    if pid == "P4":
        _ARM[k] = _owner_arm()
        return _ARM[k]
    ref, cost = reference(), frame_cost()
    out = [ref[0]]
    sound, spent, pop, retired = True, 0, 0, 0
    for i in range(1, len(VP.PATH)):
        ok, c = holds(pid, i)
        spent += c
        if ok:
            pop += 1
            retired += cost[i]          # the whole frame is skipped: executed is zero for it
            out.append(out[i - 1])
        else:
            out.append(ref[i])
    for i in range(len(ref)):
        if out[i][0] != ref[i][0] or out[i][1] != ref[i][1]:
            sound = False
            break
    _ARM[k] = (sound, spent, pop, retired)
    return _ARM[k]


# ---- P4: the ownership certificate ----------------------------------------------------------------------
def _tri_setup(quad, eye, m, cx, cy):
    """The two projected triangles of a quad, or None where the reference would reject it."""
    cam = [VR._project(v, eye, m) for v in quad]
    if any(c[1] < VR.NEAR for c in cam):
        return None
    scr = [(cx + c[0] * VR.FOCAL // c[1], cy - c[2] * VR.FOCAL // c[1], c[1]) for c in cam]
    out = []
    for p, q, r in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
        area = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        if area <= 0:
            continue
        b0 = VR._top_left_bias(p[0], p[1], q[0], q[1])
        b1 = VR._top_left_bias(q[0], q[1], r[0], r[1])
        b2 = VR._top_left_bias(r[0], r[1], p[0], p[1])
        out.append((p, q, r, area, b0, b1, b2,
                    VS.corrected_bound(p, q, r, area, b0 + b1 + b2)))
    return out


def _owner_pass(use_cert):
    """P4, AND THE ONLY INTERESTING ONE. Returns (sound, cost, population, retired).

    AN OWNERSHIP CERTIFICATE DOES NOT LICENSE REUSING A TILE'S PIXELS. That is precisely the unsound
    move `voxpath` ruled out: depth moves with the camera, so a remembered depth is a wrong depth.
    What it licenses is skipping the SEARCH — the coverage tests across every primitive whose box
    touches the tile — while the depth is RECONSTRUCTED from the owner's own plane at the current
    camera. The certificate is executable proof about WHO owns the pixel; the value is derived.

    THE CERTIFICATE IS ACTUALLY TAKEN, AND THE RETIREMENT IS MEASURED RATHER THAN MODELLED. The
    first version of this arm computed the certificate, counted what it WOULD have saved, and then
    rasterised the whole bin anyway — so its buffers matched the reference for the trivial reason
    that it had done all the work, and its `retired` figure was a formula. `retired` is now
    BASELINE MINUS EXECUTED, taken from the run, which is a quantity no unused fast path can earn.

    Soundness rests on two conditions, and the tile falls back to a full rasterisation unless BOTH
    hold. First, no primitive outside the owner set can be nearer than the FARTHEST depth any owner
    reaches in the tile — judged by `voxsilo`'s CORRECTED conservative bound, because the naive one
    is unsound here and that rung proved it. Second, every pixel of the tile must actually end up
    owned; a pixel the owners no longer cover could be won by a non-owner that is farther away, and
    that is discovered during the restricted pass rather than assumed away.
    """
    prims = VX.primitives_with("reversed")
    ref = reference()
    cx, cy = VR.W // 2, VR.H // 2
    tw = (VR.W + TILE - 1) // TILE
    th = (VR.H + TILE - 1) // TILE
    spent = pop = executed = 0
    sound = True
    prev_key = None
    for fi, (_e, _n, eye, fwd) in enumerate(VP.PATH):
        m = VR.basis(fwd)
        colour = [VR.BACKGROUND] * (VR.W * VR.H)
        depth = [VR.FAR] * (VR.W * VR.H)
        key = [-1] * (VR.W * VR.H)
        tris = []
        for pk, col, quad in prims:
            executed += VO.MUL_PER_QUAD
            s = _tri_setup(quad, eye, m, cx, cy)
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
            """The committed inner loop over one group of triangles and one tile."""
            n = 0
            for pk, col, p, q, r, area, b0, b1, b2, _z in group:
                for y in range(y0, y1 + 1):
                    row = y * VR.W
                    for x in range(x0, x1 + 1):
                        n += VO.MUL_PER_WALK
                        w0 = VR._edge(p[0], p[1], q[0], q[1], x, y) + b0
                        w1 = VR._edge(q[0], q[1], r[0], r[1], x, y) + b1
                        w2 = VR._edge(r[0], r[1], p[0], p[1], x, y) + b2
                        if w0 < 0 or w1 < 0 or w2 < 0:
                            continue
                        n += VO.MUL_PER_COVER + VO.DIV_PER_COVER
                        d = (p[2] * w1 + q[2] * w2 + r[2] * w0) // area
                        i = row + x
                        if (d, pk) < (depth[i], key[i] if key[i] >= 0 else (1 << 62)):
                            depth[i], key[i], colour[i] = d, pk, col
            return n

        for ty in range(th):
            for tx in range(tw):
                b = bins[ty * tw + tx]
                x0, x1 = tx * TILE, min(tx * TILE + TILE, VR.W) - 1
                y0, y1 = ty * TILE, min(ty * TILE + TILE, VR.H) - 1
                taken = False
                if use_cert and prev_key is not None and b:
                    owners = {prev_key[y * VR.W + x]
                              for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
                    spent += (y1 - y0 + 1) * (x1 - x0 + 1)
                    if -1 not in owners:
                        group, far, ok = [], -1, True
                        for k in owners:
                            got = by_key.get(k)
                            if not got:
                                ok = False
                                break
                            for t in got:
                                spent += 1
                                group.append(t)
                                z = max(t[2][2], t[3][2], t[4][2])
                                if z > far:
                                    far = z
                        if ok:
                            for t in b:
                                spent += 1
                                if t[0] not in owners and t[9] <= far:
                                    ok = False
                                    break
                        if ok:
                            # TAKE THE FAST PATH: the owners only, depth RECONSTRUCTED
                            executed += raster(group, x0, x1, y0, y1)
                            if any(key[y * VR.W + x] < 0
                                   for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)):
                                # a pixel the owners no longer cover: the certificate does not hold
                                for y in range(y0, y1 + 1):
                                    for x in range(x0, x1 + 1):
                                        i = y * VR.W + x
                                        depth[i], key[i] = VR.FAR, -1
                                        colour[i] = VR.BACKGROUND
                            else:
                                taken = True
                                pop += 1
                if not taken:
                    executed += raster(b, x0, x1, y0, y1)
        if colour != ref[fi][0] or depth != ref[fi][1]:
            sound = False
        prev_key = key
    return (sound, spent, pop, executed)


def _owner_arm():
    """P4 measured against a TILED BASELINE, so the certificate is the ONLY variable.

    The first measurement compared `tiled loop + certificate` against the UNTILED reference and
    reported a NEGATIVE retirement — which conflated two changes and blamed the certificate for the
    cost of the loop it sits on. That is the single-variable discipline `voxsilo` exists to enforce,
    applied to this rung's own instrument. The same tiled loop is now run TWICE, once with the
    certificate disabled and once enabled, and the retirement is the difference. The tiling overhead
    against the committed reference is reported SEPARATELY as `tiling_overhead`, because a reader
    is owed the fact that this fast path sits on a costlier loop than the one it is meant to beat.
    """
    base = _owner_pass(False)
    cert = _owner_pass(True)
    return (base[0] and cert[0], cert[1], cert[2], base[3] - cert[3])


def tiling_overhead():
    """(operations the tiled loop executes with no certificate, operations the committed reference
    executes) — reported as a PAIR so the cost of the loop is never netted into the certificate's
    ledger."""
    return (_owner_pass(False)[3], sum(frame_cost()))


# ---- the verdicts --------------------------------------------------------------------------------------
def sound(pid):
    return arm(pid)[0]


def panel(pid):
    _check(pid)
    s, c, p, r = arm(pid)
    return {"cost": c, "population": p, "retired": r}


def quantity(name):
    if name not in QUANTITIES:
        raise VoxcondError("VOXCOND-REFUSE: no quantity named %r" % (name,))
    return {p: panel(p)[name] for p in PREDICATES}


def verdicts():
    out = {}
    p1 = panel("P1")
    out["D1"] = (sound("P1") and p1["retired"] > 100 * p1["cost"],
                 "P1 sound, %d operations retired for %d spent" % (p1["retired"], p1["cost"]))
    out["D2"] = (not sound("P2"), "P2 %s" % ("UNSOUND as predicted" if not sound("P2")
                                             else "held sound, against the prediction"))
    out["D3"] = (not sound("P3"), "P3 %s" % ("UNSOUND as predicted" if not sound("P3")
                                             else "held sound, against the prediction"))
    p4 = panel("P4")
    out["D4"] = (sound("P4") and p4["cost"] > p4["retired"],
                 "P4 sound, %d spent against %d retired" % (p4["cost"], p4["retired"]))
    cheap = [p for p in PREDICATES if p != "P1" and sound(p) and panel(p)["retired"] > 0]
    out["D5"] = (len(cheap) == 0,
                 "no cheap non-trivial predicate is both sound and productive (%d found)"
                 % len(cheap))
    return out


def hits():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if ok))


def misses():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if not ok))


def the_verdicts_match_the_committed_prediction():
    """The scored set must EQUAL the set committed one commit earlier — not a superset, which would
    be a sixth predicate smuggled in, and not a subset, which would be a miss quietly dropped."""
    return sorted(verdicts()) == list(PREDICTIONS) and len(PREDICTIONS) == 5


def the_record_carries_hits_and_misses():
    return len(hits()) > 0 and len(misses()) > 0


def every_arm_is_checked_against_the_reference():
    """THE CONTRACT, AND IT IS THE ONLY THING THAT DECIDES WHETHER A CERTIFICATE IS A CERTIFICATE.
    Every arm's buffers are compared to the committed reference AS LISTS on every one of the 31
    declared frames — a certificate that changes what is seen is not a fast path, it is a bug."""
    return all(isinstance(arm(p)[0], bool) for p in PREDICATES) and sound("P1")


def the_unsound_predicates_are_still_unsound():
    """THE REFUTATIONS, KEPT RUNNABLE. Three cheap conditions that look reasonable on inspection
    move the observable, and this law requires them to keep doing so, because a refutation that
    stops being executable stops being evidence."""
    return not sound("P2") and not sound("P3") and not sound("P5")


def the_unsound_predicates_fail_for_one_reason():
    """AND IT IS THE REASON `voxpath` MEASURED: THE CAMERA MOVED. Each of the three holds on at
    least one pair where the observable nonetheless changes, so none of them is failing because it
    never fires — a predicate that never held would be vacuously unsound and would prove nothing."""
    return all(panel(p)["population"] > 0 for p in ("P2", "P3", "P5"))


def the_only_sound_cheap_predicate_is_the_trivial_one():
    """THE STRUCTURAL RESULT. Of the five declared conditions exactly one cheap one is sound, and it
    is the one that fires when nothing has changed at all."""
    cheap = [p for p in PREDICATES if p != "P4" and sound(p)]
    return cheap == ["P1"]


def the_fast_path_is_actually_taken():
    """THE GUARD AGAINST THE DEFECT THIS RUNG SHIPPED IN ITS FIRST DRAFT. That draft computed P4's
    certificate, counted what it WOULD have saved, and then rasterised the whole bin anyway — so its
    buffers matched the reference for the trivial reason that it had done all the work, and its
    retirement was a formula rather than a measurement. `retired` is now BASELINE MINUS EXECUTED,
    taken from the run, and this law requires it to be POSITIVE: a fast path that is never taken
    cannot earn it, and a certificate that saves nothing is not a certificate."""
    return all(panel(p)["retired"] > 0 for p in PREDICATES if sound(p))


def the_certificate_wins_against_the_loop_it_sits_on():
    """P4 RETIRES NINETEEN TIMES WHAT IT COSTS — against the tiled loop it runs on, which is the
    only comparison in which the certificate is the single variable."""
    p = panel("P4")
    return sound("P4") and p["retired"] > 15 * p["cost"]


def the_loop_it_sits_on_loses_against_the_reference():
    """AND THIS LAW EXISTS SO THE NINETEEN TIMES CAN NEVER BE QUOTED ALONE. The tiled loop the
    certificate needs costs 1.85 times the committed reference, so the ARRANGEMENT AS A WHOLE
    retires nothing: the certificate saves four million operations on a loop that spends twenty
    million extra. The certificate is ESTABLISHED and the IMPLEMENTATION IS NOT COMPETITIVE, and
    reporting the first without the second would be exactly the inflation this tree forbids. The
    row reddens on the day the tiled loop stops losing, which is the day this becomes a real
    speedup rather than a real mechanism."""
    tiled, ref = tiling_overhead()
    return tiled > ref and tiled - panel("P4")["retired"] > ref


def the_ownership_certificate_is_sound():
    """P4 IS THE ONE THAT WORKS, AND IT WORKS BECAUSE IT RECONSTRUCTS RATHER THAN REMEMBERS. It does
    not reuse a tile's pixels — that is the unsound move — it skips the SEARCH for the owner while
    the depth is derived from the owner's own plane at the current camera."""
    return sound("P4")


def nothing_is_promoted():
    return VO.nothing_is_optimised() and VS.nothing_is_promoted()


def no_wall_clock_enters_this_rung():
    import ast
    with open(os.path.join(_HERE, "voxcond.py"), encoding="utf-8") as fh:
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
RECORD = os.path.join("spec", "attest", "voxref-cond.txt")


def cond_digest():
    body = "\n".join("%s %d %s %d %d %d" % ((p, 1 if sound(p) else 0, "-",
                                             panel(p)["cost"], panel(p)["population"],
                                             panel(p)["retired"])) for p in PREDICATES)
    body += "\n" + "\n".join("%s %s %s" % (k, v[0], v[1]) for k, v in sorted(verdicts().items()))
    body += "\nloop %d %d" % tiling_overhead()
    return hashlib.sha256(MAGIC + b"|cond|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXQ1 conditional certificates — emitted by voxcond.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE PREDICTION WAS COMMITTED ONE COMMIT EARLIER, in `voxpath`, and is QUOTED here",
            "# rather than restated. Its digest is checked against the golden that rung pinned.",
            "# Each predicate is measured on THREE quantities and run as an ARM, with the resulting",
            "# buffers compared to the reference AS LISTS on all 31 declared frames.",
            "#   arm     <predicate> <SOUND|UNSOUND> <cost> <population> <retired>",
            "#   loop    <tiled-loop operations> <committed-reference operations>",
            "#   verdict <id> <HIT|MISS> <what was measured>",
            "#   digest  <lattice digest>"]
    for p in PREDICATES:
        rows.append("arm %s %s %d %d %d" % (p, "SOUND" if sound(p) else "UNSOUND",
                                            panel(p)["cost"], panel(p)["population"],
                                            panel(p)["retired"]))
    rows.append("loop %d %d" % tiling_overhead())
    for k, (ok, what) in sorted(verdicts().items()):
        rows.append("verdict %s %s %s" % (k, "HIT" if ok else "MISS", what))
    rows.append("digest %s" % cond_digest())
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
        if f[0] == "arm" and (len(f) != 6 or f[1] not in PREDICATES
                              or f[2] not in ("SOUND", "UNSOUND")):
            raise VoxcondError("VOXCOND-REFUSE: an arm row naming no declared predicate")
        if f[0] == "verdict" and (len(f) < 4 or f[1] not in PREDICTIONS
                                  or f[2] not in ("HIT", "MISS")):
            raise VoxcondError("VOXCOND-REFUSE: a verdict row naming no declared prediction")
        if f[0] == "loop" and len(f) != 3:
            raise VoxcondError("VOXCOND-REFUSE: a loop row of the wrong arity")
        if f[0] not in ("arm", "loop", "verdict", "digest"):
            raise VoxcondError("VOXCOND-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxcondError("VOXCOND-REFUSE: the record names no world digest")
    if not rows:
        raise VoxcondError("VOXCOND-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    v = verdicts()
    for r in rows:
        if r[0] == "arm":
            if (r[2] == "SOUND") != sound(r[1]):
                return False
            if tuple(int(x) for x in r[3:]) != tuple(panel(r[1])[q] for q in QUANTITIES):
                return False
        if r[0] == "loop" and (int(r[1]), int(r[2])) != tiling_overhead():
            return False
        if r[0] == "verdict" and (r[2] == "HIT") != v[r[1]][0]:
            return False
    return next(r[1] for r in rows if r[0] == "digest") == cond_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("arm "):
            f = ln.split()
            f[2] = "MAYBE"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxcondError:
        return True
    return False


def told():
    p1, p4 = panel("P1"), panel("P4")
    tiled, refops = tiling_overhead()
    bad = [p for p in PREDICATES if not sound(p)]
    return ("FIVE CONDITIONS DECLARED ONE COMMIT EARLIER AND SCORED HERE, each measured on PREDICATE "
            "COST, VALIDITY POPULATION and WORK RETIRED, each RUN AS AN ARM with its buffers "
            "compared to the reference AS LISTS on all %d declared frames. %d of the five are "
            "UNSOUND — %s — and they fail for ONE reason, the reason `voxpath` measured: THE CAMERA "
            "MOVED, depth is a continuous function of camera position, and `O_t` contains it "
            "exactly, so `the camera barely moved` licenses nothing at all. OF FIVE PROPOSED "
            "CONDITIONS EXACTLY ONE CHEAP ONE IS SOUND AND IT IS THE TRIVIAL ONE: P1 retires %d "
            "operations for %d spent, and a scheme that cannot win when nothing moves cannot win "
            "anywhere. AND P4 IS THE ONE THAT MATTERS — an ownership certificate does NOT license "
            "reusing a tile's pixels, which is the unsound move; it licenses skipping the SEARCH "
            "while the depth is RECONSTRUCTED from the owner's own plane, which is `voxpath`'s "
            "conclusion turned into an arm. IT IS SOUND AND IT RETIRES %d OPERATIONS FOR %d SPENT "
            "— nineteen times — measured against the TILED LOOP it sits on, which is the only "
            "comparison in which the certificate is the single variable. AND THE NINETEEN TIMES "
            "MUST NEVER BE QUOTED ALONE: that loop costs %d operations against the reference's %d, "
            "so the ARRANGEMENT AS A WHOLE RETIRES NOTHING — the certificate saves four million on "
            "a loop that spends twenty million extra. THE MECHANISM IS ESTABLISHED AND THE "
            "IMPLEMENTATION IS NOT COMPETITIVE, and those are different sentences"
            % (len(VP.PATH), len(bad), ", ".join(bad), p1["retired"], p1["cost"],
               p4["retired"], p4["cost"], tiled, refops))


def scene_case(name):
    if name == "arms":
        return repr(tuple((p, sound(p), tuple((q, panel(p)[q]) for q in QUANTITIES))
                          for p in PREDICATES))
    if name == "verdicts":
        return repr((sorted(verdicts().items()), tiling_overhead()))
    raise VoxcondError("VOXCOND-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("arms", "verdicts")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxcond.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxcondError("VOXCOND-REFUSE: no golden named %r" % name)
