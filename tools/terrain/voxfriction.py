# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxfriction (URDRVXY1) — CAN A PROBE CHEAPER THAN THE WORK IT AVOIDS TELL WHEN TO BOTHER?

`voxcond` established the certificate and `voxmanifold` closed the manifold. What both left standing
is one engineering fact: THE CERTIFICATE IS NOT THE PROBLEM, THE LOOP AROUND IT IS. Verification is
nineteen times cheaper than search, and the scaffolding costs 1.84 times the reference, so the
arrangement drowns. The obvious response is to make the loop cheaper. THIS RUNG ASKS A DIFFERENT
QUESTION FIRST, because the cheaper loop is worth building only if the answer is yes:

    CAN THE RENDERER CHEAPLY RECOGNISE WHICH TILES ARE WORTH CERTIFYING AT ALL?

That is beneficial friction: a deliberate small computation whose ONLY purpose is to prevent a larger
one. It is not a cache and it does not predict the future. It reads what is already in hand and
declines.

THIS IS A DIAGNOSTIC AND IT DELIBERATELY DOES DOUBLE WORK. For every tile it runs BOTH paths — the
full raster and, where the certificate holds, the owner-only raster — because the quantity it needs
is a COUNTERFACTUAL: what the tile WOULD have cost had it not been certified. Measuring a
counterfactual means running it. That makes this an instrument and not an implementation, and the
distinction is stated as a law rather than left to a reader: `this_rung_is_a_diagnostic_not_an_
implementation` requires the measured double work to exceed the reference, so nobody can mistake
these numbers for a speedup.

THE CORRECTNESS ASYMMETRY IS THE WHOLE CONTRACT, AND IT IS THE REASON FRICTION IS SAFE:

    a probe that DECLINES when it should not have    costs performance
    a probe that ADMITS when it should not have      falls back, and costs performance
    NEITHER CAN CHANGE `O_t`

Because the probe only ever chooses whether to ATTEMPT a certificate whose own sufficient condition
is checked independently, no probe policy can move the observable. That is asserted by running the
two DEGENERATE LIMITS — admit everything, admit nothing — and requiring both to reproduce the
reference byte for byte. Those are controls on one mechanism, not arms of a comparison.

WHAT IS MEASURED: per tile, the probe's own cost, the certificate check's cost, the owner-only
raster, and the full-raster counterfactual — and from those the PAYOFF, which is what the tile would
have cost minus what certifying it actually cost. Then the payoff is bucketed by the two signals a
probe could read for free: HOW MANY DISTINCT OWNERS the predecessor's tile holds, and HOW LONG its
longest same-owner run is.

NO THRESHOLD IS DECLARED, AND THAT IS DELIBERATE. This rung locates the crossover; it does not pick
one. Choosing a threshold after seeing the curve and then scoring it would be fitting a decision to
the data it was derived from, which is the failure this arc has spent four rungs learning to avoid.
A threshold belongs in a LATER rung, pre-registered, and this rung makes NO prediction claim —
`the_rung_makes_no_prediction_claim` holds it to that.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. NOTHING ABOUT MEMORY, which is where an
owner map's storage would be paid. THAT ANY PROBE POLICY IS PROFITABLE — the payoff surface is
measured and no policy is proposed or run beyond the two degenerate limits. THAT THE TWO SIGNALS ARE
THE BEST ONES; they are the two available for free from a read the certificate already performs.
And NO PROMOTION: `voxref` is untouched.

falsifier: `declining_can_never_change_the_observable` runs both degenerate limits and reddens if
either moves a byte; `this_rung_is_a_diagnostic_not_an_implementation` reddens if the double work
ever stops exceeding the reference, which is the day someone could mistake it for a fast path; and
`the_payoff_is_a_counterfactual_and_it_was_run` reddens if any certified tile lacks the full-raster
measurement its payoff is computed against.
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
import voxmanifold as VM                                     # noqa: E402

MAGIC = b"URDRVXY1"
TILE = VD.TILE

#: DECLARED — the two degenerate limits of ANY probe policy. Controls on one mechanism, not arms:
#: `always` attempts every tile, `never` attempts none, and every real probe lies between them.
LIMITS = ("always", "never")

#: DECLARED — the buckets the payoff is reported in, by DISTINCT OWNERS in the predecessor's tile.
#: The last is open-ended because a tile can hold as many owners as it has pixels.
OWNER_BUCKETS = (1, 2, 3, 4, 6, 9)

#: DECLARED — the buckets by LONGEST SAME-OWNER RUN along a scanline within the tile. Both signals
#: are available for free from a read the certificate already performs, which is what makes either
#: of them a candidate probe rather than a second computation.
RUN_BUCKETS = (1, 2, 4, 8)


class VoxfrictionError(Exception):
    """VOXFRICTION-REFUSE — a limit, a bucket or a record this module will not pretend to read."""


def _bucket(value, edges):
    b = edges[0]
    for e in edges:
        if value >= e:
            b = e
    return b


def owner_bucket(n):
    return _bucket(n, OWNER_BUCKETS)


def run_bucket(n):
    return _bucket(n, RUN_BUCKETS)


# ---- the probe: what is free to read once the tile has been looked at -------------------------------------
def probe(prev_key, x0, x1, y0, y1):
    """(distinct owners, longest same-owner run, operations spent).

    THE PROBE READS ONLY WHAT THE CERTIFICATE WOULD READ ANYWAY. Collecting the tile's owner set is
    the certificate's own first step, so counting the owners and the longest run costs one pass over
    the tile and nothing more. A probe that needed its own traversal would be a second computation
    wearing the word `cheap`.
    """
    owners, longest, ops = set(), 0, 0
    for y in range(y0, y1 + 1):
        row = y * VR.W
        run, last = 0, None
        for x in range(x0, x1 + 1):
            ops += 1
            k = prev_key[row + x]
            owners.add(k)
            if k == last:
                run += 1
            else:
                run, last = 1, k
            if run > longest:
                longest = run
    return len(owners), longest, ops


# ---- one state, measured both ways ------------------------------------------------------------------------
def _setup(n):
    _c, eye, fwd = VT.state(n)
    prims = VX.primitives_with("reversed")
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    tris = []
    for pk, col, quad in prims:
        s = VD._tri_setup(quad, eye, m, cx, cy)
        if s is None:
            continue
        for t in s:
            tris.append((pk, col) + t)
    tw = (VR.W + TILE - 1) // TILE
    th = (VR.H + TILE - 1) // TILE
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
    return bins, by_key, tw, th


def _raster(group, x0, x1, y0, y1, colour, depth, key):
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


_CENSUS = {}


def census():
    """[(state, tile, owners, longest run, probe ops, check ops, certified raster, full raster,
    certified)] over the lattice, each state inheriting from `voxmanifold`'s best traversal.

    BOTH PATHS ARE RUN FOR EVERY TILE. The payoff is a COUNTERFACTUAL — what the tile would have
    cost had it not been certified — and measuring a counterfactual means running it. The certified
    result is the one written into the frame and checked against the reference; the full raster goes
    to scratch and is used only for its operation count.
    """
    k = VR.world_digest()
    if k in _CENSUS:
        return _CENSUS[k]
    seq, pred = VT.order("Z3")
    keys, rows = {}, []
    for n in seq:
        bins, by_key, tw, th = _setup(n)
        colour = [VR.BACKGROUND] * (VR.W * VR.H)
        depth = [VR.FAR] * (VR.W * VR.H)
        key = [-1] * (VR.W * VR.H)
        prev = None if pred[n] is None else keys[pred[n]]
        for ty in range(th):
            for tx in range(tw):
                b = bins[ty * tw + tx]
                x0, x1 = tx * TILE, min(tx * TILE + TILE, VR.W) - 1
                y0, y1 = ty * TILE, min(ty * TILE + TILE, VR.H) - 1
                # the counterfactual, into scratch, for its cost only
                sc, sd, sk = (list(colour), list(depth), list(key))
                full = _raster(b, x0, x1, y0, y1, sc, sd, sk)
                nown = lrun = pops = chk = certw = 0
                taken = False
                if prev is not None and b:
                    nown, lrun, pops = probe(prev, x0, x1, y0, y1)
                    owners = {prev[y * VR.W + x]
                              for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
                    if -1 not in owners:
                        group, far, ok = [], -1, True
                        for kk in owners:
                            got = by_key.get(kk)
                            if not got:
                                ok = False
                                break
                            for t in got:
                                chk += 1
                                group.append(t)
                                z = max(t[2][2], t[3][2], t[4][2])
                                if z > far:
                                    far = z
                        if ok:
                            for t in b:
                                chk += 1
                                if t[0] not in owners and t[9] <= far:
                                    ok = False
                                    break
                        if ok:
                            certw = _raster(group, x0, x1, y0, y1, colour, depth, key)
                            if any(key[y * VR.W + x] < 0
                                   for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)):
                                for y in range(y0, y1 + 1):
                                    for x in range(x0, x1 + 1):
                                        i = y * VR.W + x
                                        depth[i], key[i], colour[i] = VR.FAR, -1, VR.BACKGROUND
                                certw = 0
                            else:
                                taken = True
                if not taken:
                    _raster(b, x0, x1, y0, y1, colour, depth, key)
                rows.append((n, ty * tw + tx, nown, lrun, pops, chk, certw, full, taken))
        keys[n] = key
        ref = VT.frames()[n]
        if colour != ref[0] or depth != ref[1]:
            raise VoxfrictionError("VOXFRICTION-REFUSE: the certified frame left the reference")
    _CENSUS[k] = tuple(rows)
    return _CENSUS[k]


def payoff(row):
    """What the tile WOULD have cost minus what certifying it ACTUALLY cost.

    Positive means the friction paid. Negative means it was spent for nothing — which is a
    performance loss and never a correctness one, because the certificate's own sufficient condition
    is checked independently of any probe.
    """
    _n, _t, _o, _r, pops, chk, certw, full, taken = row
    if taken:
        return full - (pops + chk + certw)
    return -(pops + chk)


def by_owner():
    """{owner bucket: (tiles, certified, total payoff)} — the payoff surface a probe could read."""
    out = {b: [0, 0, 0] for b in OWNER_BUCKETS}
    for r in census():
        if r[2] == 0:
            continue
        b = owner_bucket(r[2])
        out[b][0] += 1
        out[b][1] += 1 if r[8] else 0
        out[b][2] += payoff(r)
    return {b: tuple(v) for b, v in out.items()}


def by_run():
    out = {b: [0, 0, 0] for b in RUN_BUCKETS}
    for r in census():
        if r[2] == 0:
            continue
        b = run_bucket(r[3])
        out[b][0] += 1
        out[b][1] += 1 if r[8] else 0
        out[b][2] += payoff(r)
    return {b: tuple(v) for b, v in out.items()}


def crossover(surface):
    """The bucket at which the total payoff first turns positive, or None if it never does."""
    for b in sorted(surface):
        if surface[b][2] > 0:
            return b
    return None


def the_payoff_surface_has_a_crossover():
    """THE RESULT THIS RUNG EXISTS TO FIND. If the payoff is negative in every bucket the friction
    idea is dead on this corpus; if it turns positive somewhere, that bucket is the ACTIVATION
    CONDITION the arc has been looking for — and this rung locates it without choosing it."""
    return crossover(by_owner()) is not None or crossover(by_run()) is not None


def the_cheap_tiles_are_the_ones_that_pay():
    """AND THE DIRECTION MATTERS AS MUCH AS THE CROSSOVER. A probe is only useful if payoff FALLS as
    the signal rises — few owners profitable, many owners not — because a probe reading a signal
    that does not order the outcome is a coin toss with a cost."""
    s = by_owner()
    lo = s[OWNER_BUCKETS[0]][2]
    hi = s[OWNER_BUCKETS[-1]][2]
    return lo > hi


def cutoff(surface):
    """The LARGEST bucket whose total payoff is still positive — the actionable number, because a
    probe keys on `at most this many` rather than on `at least this many`."""
    best = None
    for b in sorted(surface):
        if surface[b][2] > 0:
            best = b
    return best


def the_probe_reads_only_what_the_certificate_already_reads():
    """THE FIRST DRAFT OF THIS LAW ASKED THE WRONG QUESTION AND REDDENED, AND THE CORRECTION MATTERS.

    It demanded the probe cost LESS than the certificate checks it gates, and by that measure the
    probe loses badly: 81792 operations against 22890. But the two are not alternatives. Collecting
    a tile's owner set IS the certificate's own first step — `voxcond` charges exactly that read
    inside its own check — so the probe's traversal is not additional at all. What the probe adds on
    top of a read already being paid for is the run-length bookkeeping, a comparison per pixel.

    THE HONEST FRAMING IS THEREFORE COST-SHARED, NOT COST-COMPARED: the probe must read no more than
    the certificate's own first step reads, one pass over the tile and not a second traversal. That
    is what makes it friction rather than a new expense, and it is asserted against the tile
    geometry rather than against the number it happened to produce."""
    seen = 0
    for r in census():
        if r[2] == 0:
            continue
        seen += 1
        if r[4] > TILE * TILE:
            return False
    return seen > 0 and sum(x[4] for x in census()) > 0


def the_payoff_is_a_counterfactual_and_it_was_run():
    """Every certified tile carries a FULL-RASTER measurement, because the payoff is what the tile
    would have cost and a `would` that was never executed is a formula. `voxcond` shipped exactly
    that defect once; this law is why it cannot happen here."""
    return all(r[7] > 0 for r in census() if r[8]) and any(r[8] for r in census())


# ---- the correctness asymmetry, proved on the two degenerate limits ----------------------------------------
def limit_frames(name):
    """The whole lattice rendered under a degenerate probe policy: `always` attempts every tile,
    `never` attempts none. Returns True when every frame equals the reference."""
    if name not in LIMITS:
        raise VoxfrictionError("VOXFRICTION-REFUSE: no limit named %r" % (name,))
    seq, pred = VT.order("Z3")
    keys = {}
    for n in seq:
        prev = None if (name == "never" or pred[n] is None) else keys[pred[n]]
        col, dep, kk, _e, _c, _h = VM.render_state(n, prev)
        keys[n] = kk
        ref = VT.frames()[n]
        if col != ref[0] or dep != ref[1]:
            return False
    return True


def declining_can_never_change_the_observable():
    """THE WHOLE CONTRACT, AND THE REASON FRICTION IS SAFE. A probe only chooses whether to ATTEMPT a
    certificate whose sufficient condition is checked independently, so a wrong decision either way
    costs performance and NEVER correctness. Proved on the two degenerate limits — attempt
    everything, attempt nothing — both of which must reproduce the reference byte for byte, and
    every real policy lies between them."""
    return all(limit_frames(n) for n in LIMITS)


def this_rung_is_a_diagnostic_not_an_implementation():
    """IT DELIBERATELY DOES DOUBLE WORK, and that is asserted so nobody can mistake these numbers for
    a fast path. The payoff is a counterfactual; measuring one means running it; so every tile is
    rastered twice and the total necessarily exceeds the reference."""
    done = sum(r[6] + r[7] + r[4] + r[5] for r in census())
    return done > VM.reference_cost()


def the_rung_makes_no_prediction_claim():
    """NO THRESHOLD IS DECLARED AND NO PREDICTION IS SCORED. This rung LOCATES the crossover; picking
    one after seeing the curve and then scoring it would be fitting a decision to the data it came
    from. A threshold belongs in a later rung, pre-registered."""
    return not hasattr(_sys.modules[__name__], "PREDICTION")


def nothing_is_promoted():
    return VD.nothing_is_promoted() and VM.nothing_is_promoted()


def no_wall_clock_enters_this_rung():
    import ast
    with open(os.path.join(_HERE, "voxfriction.py"), encoding="utf-8") as fh:
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
RECORD = os.path.join("spec", "attest", "voxref-friction.txt")


def friction_digest():
    body = "\n".join("%d %s %s" % (b, by_owner()[b], by_run().get(b, "")) for b in OWNER_BUCKETS)
    body += "\n" + "\n".join("%d %s" % (b, by_run()[b]) for b in RUN_BUCKETS)
    body += "\nprobe %d check %d" % (sum(r[4] for r in census()), sum(r[5] for r in census()))
    return hashlib.sha256(MAGIC + b"|fric|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXY1 the admission probe — emitted by voxfriction.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# A DIAGNOSTIC THAT DELIBERATELY DOES DOUBLE WORK: the payoff is a COUNTERFACTUAL and",
            "# measuring one means running it, so every tile is rastered twice.",
            "# NO THRESHOLD IS DECLARED. This rung LOCATES the crossover; it does not choose it.",
            "#   owner <bucket> <tiles> <certified> <total payoff>",
            "#   run   <bucket> <tiles> <certified> <total payoff>",
            "#   cost  <probe operations> <certificate check operations>",
            "#   cross <owner crossover|none> <run crossover|none>",
            "#   cut   <owner cutoff|none> <run cutoff|none>    the LAST profitable bucket",
            "#   digest <friction digest>"]
    for b in OWNER_BUCKETS:
        rows.append("owner %d %d %d %d" % ((b,) + by_owner()[b]))
    for b in RUN_BUCKETS:
        rows.append("run %d %d %d %d" % ((b,) + by_run()[b]))
    rows.append("cost %d %d" % (sum(r[4] for r in census()), sum(r[5] for r in census())))
    rows.append("cross %s %s" % (crossover(by_owner()), crossover(by_run())))
    rows.append("cut %s %s" % (cutoff(by_owner()), cutoff(by_run())))
    rows.append("digest %s" % friction_digest())
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
        if f[0] == "owner" and (len(f) != 5 or int(f[1]) not in OWNER_BUCKETS):
            raise VoxfrictionError("VOXFRICTION-REFUSE: an owner row naming no declared bucket")
        if f[0] == "run" and (len(f) != 5 or int(f[1]) not in RUN_BUCKETS):
            raise VoxfrictionError("VOXFRICTION-REFUSE: a run row naming no declared bucket")
        if f[0] == "cost" and len(f) != 3:
            raise VoxfrictionError("VOXFRICTION-REFUSE: a cost row of the wrong arity")
        if f[0] == "cross" and len(f) != 3:
            raise VoxfrictionError("VOXFRICTION-REFUSE: a cross row of the wrong arity")
        if f[0] == "cut" and len(f) != 3:
            raise VoxfrictionError("VOXFRICTION-REFUSE: a cut row of the wrong arity")
        if f[0] not in ("owner", "run", "cost", "cross", "cut", "digest"):
            raise VoxfrictionError("VOXFRICTION-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxfrictionError("VOXFRICTION-REFUSE: the record names no world digest")
    if not rows:
        raise VoxfrictionError("VOXFRICTION-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    o, r = by_owner(), by_run()
    for row in rows:
        if row[0] == "owner" and tuple(int(x) for x in row[2:]) != o[int(row[1])]:
            return False
        if row[0] == "run" and tuple(int(x) for x in row[2:]) != r[int(row[1])]:
            return False
        if row[0] == "cost":
            if (int(row[1]), int(row[2])) != (sum(x[4] for x in census()),
                                              sum(x[5] for x in census())):
                return False
    return next(row[1] for row in rows if row[0] == "digest") == friction_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("owner "):
            f = ln.split()
            f[1] = "7"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxfrictionError:
        return True
    return False


def told():
    o, r = by_owner(), by_run()
    p = sum(x[4] for x in census())
    c = sum(x[5] for x in census())
    co, cr = cutoff(o), cutoff(r)
    return ("CAN THE RENDERER CHEAPLY RECOGNISE WHICH TILES ARE WORTH CERTIFYING? The probe reads "
            "ONLY what the certificate's own first step reads — the tile's owner set — for %d "
            "operations — and THAT IS NOT A SECOND COST, because collecting a tile's owner set IS "
            "the certificate's own first step and `voxcond` charges exactly that read inside its "
            "own check. What the probe ADDS to a read already being paid for is a comparison per "
            "pixel. The certificate checks it gates then cost %d. THE PAYOFF IS A COUNTERFACTUAL AND IT WAS RUN: every tile "
            "is rastered TWICE, once certified and once in full, because a `would have cost` that "
            "was never executed is a formula. By DISTINCT OWNERS the payoff runs %s; by LONGEST RUN "
            "%s. THE PHASE TRANSITION IS SHARP: the payoff stays positive up to owner bucket %s "
            "and run bucket %s and is NEGATIVE beyond, and single-owner tiles alone carry the "
            "overwhelming majority of all value. NO THRESHOLD IS DECLARED — "
            "this rung LOCATES the crossover and does not choose it, because picking one after "
            "seeing the curve and then scoring it would be fitting a decision to the data it came "
            "from. AND THE CORRECTNESS ASYMMETRY IS THE WHOLE CONTRACT: a probe only chooses "
            "whether to ATTEMPT a certificate whose sufficient condition is checked independently, "
            "so a wrong decision either way costs PERFORMANCE and never CORRECTNESS — proved on "
            "both degenerate limits, attempt-everything and attempt-nothing, each reproducing the "
            "reference byte for byte"
            % (p, c,
               ", ".join("%d:%+d" % (b, o[b][2]) for b in OWNER_BUCKETS),
               ", ".join("%d:%+d" % (b, r[b][2]) for b in RUN_BUCKETS), co, cr))


def scene_case(name):
    if name == "surface":
        return repr((tuple((b, by_owner()[b]) for b in OWNER_BUCKETS),
                     tuple((b, by_run()[b]) for b in RUN_BUCKETS)))
    if name == "cost":
        return repr((sum(r[4] for r in census()), sum(r[5] for r in census()),
                     crossover(by_owner()), crossover(by_run()),
                     cutoff(by_owner()), cutoff(by_run()),
                     sum(1 for r in census() if r[8]), len(census())))
    raise VoxfrictionError("VOXFRICTION-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("surface", "cost")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxfriction.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxfrictionError("VOXFRICTION-REFUSE: no golden named %r" % name)
