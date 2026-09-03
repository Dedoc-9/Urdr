# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxschism (URDRVXX1) — THE POPULATIONS ARE REAL AND NO FREE SIGNAL SELECTS THEM.

The proposal this rung tests is an architecture rather than an optimisation: stop making one strategy
universally better, let several SPECIALISE against each other's failure modes, and let measured local
conditions decide which one runs. `voxfriction`'s sharp phase boundary at four owners is what makes
that idea worth testing here rather than merely restating.

THIS RUNG IS A CENSUS AND BUILDS NO COMPETING IMPLEMENTATION, because the question comes first:

    DOES THE WORKLOAD PARTITION INTO POPULATIONS WHERE DIFFERENT ALGORITHMS HAVE DIFFERENT POSITIVE
    NET MARGINS — AND CAN ANYTHING CHEAP TELL WHICH POPULATION A TILE IS IN?

THE TWO HALVES GET OPPOSITE ANSWERS, AND THAT IS THE RESULT.

YES ON THE POPULATIONS. Four strategies are costed on every tile of the lattice. Three of them win
somewhere, and their winning sets are DISJOINT BY OWNER COUNT: `steno1` wins 349 tiles and every one
has exactly ONE owner; `stenoN` wins 35 and every one has TWO OR THREE; `reference` wins the other
1344. The differentiation the architecture predicts is visible, measured, and not a metaphor.

AND `normal` — THE TILED TRAVERSAL — WINS ZERO TILES OF 1728. It is not merely dominated on the
total, which `voxbreak` already showed; it is not the best strategy for a SINGLE TILE anywhere in the
lattice. `the_tiled_traversal_is_dominated_everywhere` states it, and it is the mechanism behind
`voxbreak`'s scaffolding tax: the tax is not an overhead on a good idea, it is the cost of a
traversal that is never the right answer.

NO ON THE SELECTION, AND THE NUMBER IS EXACTLY ZERO. A HINDSIGHT ORACLE that picks the winning
strategy per tile costs 10788308 against the reference's 12121714 — ELEVEN PER CENT UNDER, and the
first arrangement in this whole arc to get under the reference at all. But the oracle reads the
OUTCOME. Replace it with the best FIXED rule per group, for every signal this architecture makes
free, and the margin it captures is:

    by owner cardinality           7 groups     ZERO of 1333406
    by longest same-owner run      4 groups     ZERO
    by both, bucketed             16 groups     ZERO
    by both, EXACT and unbucketed 68 groups     ZERO

In every group of every partition, at every resolution, the best fixed strategy is `reference`.

AND THE MECHANISM IS VISIBLE INSIDE THE BEST POPULATION THERE IS. Among the 571 ONE-OWNER tiles,
`steno1` wins 349 and wins them by 1235531 — then loses the other 222 by 1700567, for a net of
-465036. A certificate that FAILS does not merely forgo its saving: it pays the read, the encode, the
verify and its own owner-only raster, and THEN pays the full tile anyway. Each losing tile costs
about twice what each winning tile saves, so the most favourable population that exists here is
itself net NEGATIVE. THE SIGNAL IS NOT WEAK — THE POPULATION IT IDENTIFIES IS UNPROFITABLE — and no
sharper reading of the same signal can repair that. It is `voxbreak`'s refutation arriving a second
time from a completely different direction.

THE ZERO IS A MEASUREMENT AND NOT AN INABILITY, AND THERE IS A PLANT THAT PROVES IT. Handed the FRAME
INDEX — which is not a property of a tile at all but a name for which picture you are drawing — the
same partition machinery returns +280476 across 323 groups. So the apparatus CAN find margin. It
finds none in the geometry because there is none to find in the signals available, and it finds some
in the frame index because that is MEMORISING THE BENCHMARK. The frame index is declared as a PLANT
and never as a signal, and `the_frame_index_is_memorisation_and_is_scored_as_a_control` keeps it out
of every claim.

SO THE ARCHITECTURE'S TWO LEVELS COME APART, AND SEPARATING THEM IS THIS RUNG'S CONTRIBUTION.
`voxfriction` established that owner cardinality predicts WHETHER THE CERTIFICATE FIRES, sharply and
usefully. This rung establishes that the same signal carries NO information about WHICH STRATEGY
WINS. Those were the same question until they were measured apart, and a regime-selective renderer
needs the second one answered, not the first.

NO RULE IS FROZEN HERE, and that is the discipline rather than modesty. Choosing a threshold on the
workload it was derived from is fitting; the honest sequence is measure, freeze the population,
declare the rule, then test it on a SUBSEQUENT workload. This rung performs the first two steps and
STOPS, because the third has nothing to declare: every candidate rule measured to exactly zero.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. NOTHING ABOUT MEMORY. THAT NO SIGNAL
EXISTS — four partitions of two free signals are measured, and a signal nobody has thought of is not
ruled out; what is ruled out is the two this architecture makes free. THAT THE FOUR STRATEGIES ARE
THE RIGHT FOUR. THAT THE ORACLE'S ELEVEN PER CENT IS REACHABLE — it is a CEILING, and the whole point
of the rung is that nothing cheap reaches it. And NO PROMOTION: `voxref` is untouched.

falsifier: `every_strategy_was_run_for_every_tile` reddens if any strategy's cost is a formula rather
than a measurement, which is the defect `voxcond` shipped once; `no_free_signal_captures_any_of_the_
margin` reddens the day any declared partition finds margin, which is the result the architecture
needs and would be the best possible failure of a law; and `the_zero_is_a_measurement_and_not_an_
inability` reddens if the frame-index plant ever stops finding margin, which is the day the zeros
above stop being informative.
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
import voxfriction as VF                                     # noqa: E402
import voxbreak as VB                                        # noqa: E402

MAGIC = b"URDRVXX1"
TILE = VD.TILE
TW = (VR.W + TILE - 1) // TILE
TH = (VR.H + TILE - 1) // TILE

#: DECLARED — the four strategies costed on EVERY tile. `reference` is the committed untiled raster's
#: own inner work attributed to this tile; `normal` is the tiled bin raster; `steno1` attempts the
#: ownership certificate ONLY at one owner and otherwise declines after the read; `stenoN` attempts
#: it at any owner count. The certificate is `voxcond`'s P4 and nothing else.
STRATEGIES = ("reference", "normal", "steno1", "stenoN")

#: DECLARED — the partitions a real selector could key on, in increasing resolution. All four are
#: built from the two signals `voxfriction` established are FREE, because collecting a tile's owner
#: set is the certificate's own first step.
SIGNALS = ("owners", "run", "owners_x_run", "exact")

#: DECLARED — the PLANT, and it is not a signal. The frame index is not a property of a tile; it is a
#: name for which picture is being drawn. It is partitioned on solely to prove the apparatus can find
#: margin when a partition is allowed to MEMORISE, so that the zeros on the real signals are a
#: measurement rather than an inability.
PLANT = "frame"


class VoxschismError(Exception):
    """VOXSCHISM-REFUSE — a strategy, a signal or a record this module will not pretend to read."""


# ---- the census ------------------------------------------------------------------------------------------
def _setup_and_tris(n):
    """(setup operations, triangles). THE SETUP IS COMMON TO EVERY STRATEGY — the same primitives,
    the same projection, the same per-triangle constants — so it is computed once per state, kept
    OUT of every strategy's cost, and reported separately. Excluding a term every strategy pays
    identically cannot change which strategy wins a tile, and including it would flatten every
    comparison toward zero."""
    _c, eye, fwd = VT.state(n)
    prims = VX.primitives_with("reversed")
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    setup, tris = 0, []
    for pk, col, quad in prims:
        setup += VO.MUL_PER_QUAD
        s = VD._tri_setup(quad, eye, m, cx, cy)
        if s is None:
            continue
        setup += VO.MUL_PER_SEEN + VO.DIV_PER_SEEN + 2 * VO.MUL_PER_TRIANGLE
        for t in s:
            tris.append((pk, col) + t)
    return setup, tris


def _reference_by_tile(tris):
    """WHERE THE UNTILED REFERENCE'S INNER WORK ACTUALLY LIVES, TILE BY TILE — a decomposition no
    rung in this arc has had. Each walked pixel of a triangle's own bounding box belongs to exactly
    one tile, so the attribution is a partition and not an estimate, and
    `the_reference_attribution_sums_to_the_committed_total` proves it."""
    out = [0] * (TW * TH)
    for _pk, _col, p, q, r, _area, b0, b1, b2, _z in tris:
        xl = max(min(p[0], q[0], r[0]), 0)
        xh = min(max(p[0], q[0], r[0]), VR.W - 1)
        yl = max(min(p[1], q[1], r[1]), 0)
        yh = min(max(p[1], q[1], r[1]), VR.H - 1)
        if xl > xh or yl > yh:
            continue
        for y in range(yl, yh + 1):
            base = (y // TILE) * TW
            for x in range(xl, xh + 1):
                i = base + x // TILE
                out[i] += VO.MUL_PER_WALK
                w0 = VR._edge(p[0], p[1], q[0], q[1], x, y) + b0
                w1 = VR._edge(q[0], q[1], r[0], r[1], x, y) + b1
                w2 = VR._edge(r[0], r[1], p[0], p[1], x, y) + b2
                if w0 < 0 or w1 < 0 or w2 < 0:
                    continue
                out[i] += VO.MUL_PER_COVER + VO.DIV_PER_COVER
    return out


def _bins(tris):
    out = [[] for _ in range(TW * TH)]
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
                out[ty * TW + tx].append(t)
    return out


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
    """[(state, tile, owners, run, recognise, encode, verify, certified raster, held, normal raster,
    reference inner)] over the whole lattice, plus (reference total, setup total).

    EVERY STRATEGY IS RUN FOR EVERY TILE. The comparison is between COUNTERFACTUALS — what each
    strategy would have cost on this tile — and a `would have cost` that was never executed is a
    formula, which is the defect `voxcond` shipped once. So the tiled raster goes to scratch for its
    cost, the certificate raster goes to scratch for its cost, the reference walk is attributed, and
    only the committed arrangement writes the frame that is checked against `voxref`.
    """
    k = VR.world_digest()
    if k in _CENSUS:
        return _CENSUS[k]
    seq, pred = VT.order("Z3")
    keys, rows = {}, []
    ref_total = setup_total = 0
    for n in seq:
        setup, tris = _setup_and_tris(n)
        setup_total += setup
        refb = _reference_by_tile(tris)
        ref_total += sum(refb)
        bins = _bins(tris)
        by_key = {}
        for t in tris:
            by_key.setdefault(t[0], []).append(t)
        prev = None if pred[n] is None else keys[pred[n]]
        colour = [VR.BACKGROUND] * (VR.W * VR.H)
        depth = [VR.FAR] * (VR.W * VR.H)
        key = [-1] * (VR.W * VR.H)
        for ty in range(TH):
            for tx in range(TW):
                ti = ty * TW + tx
                b = bins[ti]
                x0, x1 = tx * TILE, min(tx * TILE + TILE, VR.W) - 1
                y0, y1 = ty * TILE, min(ty * TILE + TILE, VR.H) - 1
                sc, sd, sk = list(colour), list(depth), list(key)
                normal = _raster(b, x0, x1, y0, y1, sc, sd, sk)
                owners = run = pops = enc = ver = cert = 0
                held = False
                oset = None
                if prev is not None and b:
                    owners, run, pops = VF.probe(prev, x0, x1, y0, y1)
                    oset = {prev[y * VR.W + x]
                            for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
                    if -1 not in oset:
                        enc = len(oset)
                        group, far, ok = [], -1, True
                        for kk in oset:
                            got = by_key.get(kk)
                            if not got:
                                ok = False
                                break
                            for t in got:
                                ver += 1
                                group.append(t)
                                z = max(t[2][2], t[3][2], t[4][2])
                                if z > far:
                                    far = z
                        if ok:
                            for t in b:
                                ver += 1
                                if t[0] not in oset and t[9] <= far:
                                    ok = False
                                    break
                        if ok:
                            gc, gd, gk = list(colour), list(depth), list(key)
                            cert = _raster(group, x0, x1, y0, y1, gc, gd, gk)
                            held = not any(gk[y * VR.W + x] < 0
                                           for y in range(y0, y1 + 1)
                                           for x in range(x0, x1 + 1))
                rows.append((n, ti, owners, run, pops, enc, ver, cert, held, normal, refb[ti]))
                if held:
                    group = []
                    for kk in oset:
                        group.extend(by_key.get(kk, []))
                    _raster(group, x0, x1, y0, y1, colour, depth, key)
                else:
                    _raster(b, x0, x1, y0, y1, colour, depth, key)
        keys[n] = key
        ref = VT.frames()[n]
        if colour != ref[0] or depth != ref[1]:
            raise VoxschismError("VOXSCHISM-REFUSE: the committed arrangement left the reference")
    _CENSUS[k] = (tuple(rows), ref_total, setup_total)
    return _CENSUS[k]


def rows():
    return census()[0]


def reference_inner():
    return census()[1]


def setup_common():
    return census()[2]


# ---- the four strategies, costed on every tile -------------------------------------------------------
def strategy_cost(row):
    """{strategy: operations} for one tile. A strategy that declines still pays the READ that told it
    to decline, and a strategy that attempts and falls back pays BOTH its attempt and the full raster
    it then has to do — because a fast path that is not taken is a cost and never a saving."""
    _n, _t, owners, _run, pops, enc, ver, cert, held, normal, refb = row
    out = {"reference": refb, "normal": normal}
    if owners == 0:
        out["steno1"] = out["stenoN"] = normal
        return out
    if owners == 1:
        out["steno1"] = pops + enc + ver + cert + (0 if held else normal)
    else:
        out["steno1"] = pops + normal
    out["stenoN"] = pops + enc + ver + cert + (0 if held else normal)
    return out


def strategy_total(name):
    if name not in STRATEGIES:
        raise VoxschismError("VOXSCHISM-REFUSE: no strategy named %r" % (name,))
    return sum(strategy_cost(r)[name] for r in rows())


def winner(row):
    """The strategy that WOULD have won this tile, ties broken by declaration order. THIS IS AN
    ORACLE AND NOT A POLICY: it reads the outcome of every strategy to choose one, so it cannot be
    built. Its only use is as a CEILING on what any selector could reach."""
    c = strategy_cost(row)
    return min(STRATEGIES, key=lambda s: (c[s], STRATEGIES.index(s)))


def oracle_total():
    return sum(min(strategy_cost(r).values()) for r in rows())


def wins():
    """{strategy: tiles it would have won}."""
    out = dict.fromkeys(STRATEGIES, 0)
    for r in rows():
        out[winner(r)] += 1
    return out


# ---- the partitions a real selector could key on -----------------------------------------------------
def _group(row, signal):
    owners, run = row[2], row[3]
    if signal == "owners":
        return VF.owner_bucket(owners) if owners else 0
    if signal == "run":
        return VF.run_bucket(run) if owners else 0
    if signal == "owners_x_run":
        return (VF.owner_bucket(owners) if owners else 0,
                VF.run_bucket(run) if owners else 0)
    if signal == "exact":
        return (owners, run)
    if signal == PLANT:
        return (owners, run, row[0])
    raise VoxschismError("VOXSCHISM-REFUSE: no signal named %r" % (signal,))


def partition(signal):
    """(groups, best-fixed-strategy total, margin over the reference).

    THE BEST FIXED STRATEGY PER GROUP is what a real selector can actually do: it reads the signal,
    looks up one strategy, and runs it — the same strategy for every tile in the group. It is still
    generous, because the lookup is chosen with the whole workload in hand, which is why even a
    POSITIVE result here would be a ceiling rather than a rule."""
    groups = {}
    for r in rows():
        groups.setdefault(_group(r, signal), []).append(r)
    total = 0
    for sub in groups.values():
        per = {s: sum(strategy_cost(r)[s] for r in sub) for s in STRATEGIES}
        total += min(per[s] for s in STRATEGIES)
    return len(groups), total, strategy_total("reference") - total


def margin(signal):
    return partition(signal)[2]


def by_owner_bucket():
    """{bucket: (tiles, {strategy: wins}, oracle margin over the reference)} — the populations."""
    out = {}
    for r in rows():
        b = VF.owner_bucket(r[2]) if r[2] else 0
        d = out.setdefault(b, [0, {}, 0])
        d[0] += 1
        w = winner(r)
        d[1][w] = d[1].get(w, 0) + 1
        c = strategy_cost(r)
        d[2] += c["reference"] - c[w]
    return {b: (v[0], tuple(sorted(v[1].items())), v[2]) for b, v in out.items()}


# ---- the laws --------------------------------------------------------------------------------------
def the_reference_attribution_sums_to_the_committed_total():
    """THE LAW THAT MAKES EVERY PER-TILE COMPARISON HONEST. The reference's inner work is attributed
    tile by tile, and attributed work plus the common setup must equal `voxmanifold`'s committed
    reference figure EXACTLY. An attribution that did not add up would be an invented denominator."""
    return reference_inner() + setup_common() == VM.reference_cost()


def the_setup_is_common_to_every_strategy_and_is_large():
    """IT IS COMPUTED ONCE PER STATE, OUTSIDE THE TILE LOOP, AND APPEARS IN NO STRATEGY'S COST.
    Excluding a term every strategy pays identically cannot change which one wins a tile; including
    it would flatten every comparison toward zero and make the census say nothing.

    AND THE EXCLUDED TERM IS NOT SMALL, WHICH IS WHY THE EXCLUSION IS DISCLOSED AS A LAW RATHER THAN
    A FOOTNOTE: the shared setup exceeds half of everything being compared. A reader who takes a
    per-tile margin here and scales it against the committed reference without adding the setup back
    will overstate it by that ratio, so both figures are always reported together."""
    return (setup_common() * 2 > reference_inner()
            and reference_inner() + setup_common() == VM.reference_cost())


def every_strategy_was_run_for_every_tile():
    """THE COUNTERFACTUAL LAW, INHERITED FROM `voxfriction` AND WIDENED TO FOUR STRATEGIES. A `would
    have cost` that was never executed is a formula, and `voxcond` shipped exactly that defect once.
    Every tile carries a measured normal raster and a measured reference attribution, and every tile
    that certified carries a measured certificate raster."""
    seen = rows()
    return (len(seen) == len(VT.STATES) * TW * TH
            and all(r[9] > 0 or r[10] == 0 for r in seen)
            and all(r[7] > 0 for r in seen if r[8]))


def the_committed_arrangement_reproduces_the_observable():
    """Colour and depth as LISTS on all sixteen states — the contract that has now caught an unsound
    optimisation in three consecutive rungs. `census()` refuses rather than returning if it fails."""
    return len(rows()) > 0


def the_workload_does_partition_into_populations():
    """YES ON THE POPULATIONS. At least two strategies win somewhere, and their winning sets are
    disjoint by owner count — `steno1` only at one owner, `stenoN` only above it. That is the
    differentiation the architecture predicts, measured rather than asserted."""
    w = wins()
    live = [s for s in STRATEGIES if w[s] > 0]
    if len(live) < 3:
        return False
    o1 = {r[2] for r in rows() if winner(r) == "steno1"}
    on = {r[2] for r in rows() if winner(r) == "stenoN"}
    return o1 == {1} and on and 1 not in on


def the_tiled_traversal_is_dominated_everywhere():
    """AND `normal` WINS ZERO TILES OF ALL OF THEM. Not merely dominated on the total, which
    `voxbreak` already showed — never the best strategy for a SINGLE TILE anywhere. That is the
    mechanism behind the scaffolding tax: it is not an overhead on a good idea, it is the cost of a
    traversal that is never the right answer."""
    return wins()["normal"] == 0


def the_hindsight_oracle_beats_the_reference():
    """THE CEILING, AND THE FIRST TIME ANYTHING IN THIS ARC HAS GONE UNDER THE REFERENCE. It is worth
    stating plainly because every previous rung's answer was `no by a wide margin`, and this one is
    `yes, by eleven per cent, to something that cannot be built`."""
    return oracle_total() < strategy_total("reference")


def the_oracle_is_not_a_policy():
    """IT READS THE OUTCOME, AND THAT IS THE POINT RATHER THAN A DEFECT. `winner` calls
    `strategy_cost`, which is a measurement of what each strategy actually DID on that tile, so the
    oracle cannot be built and is only ever a CEILING. By construction it is bounded above by the
    best single strategy and below by nothing a selector can reach, and the gap between it and the
    best fixed rule per group is exactly what the next law measures."""
    return (oracle_total() <= min(strategy_total(s) for s in STRATEGIES)
            and oracle_total() <= min(partition(s)[1] for s in SIGNALS))


def no_free_signal_captures_any_of_the_margin():
    """THE HEADLINE, AND THE NUMBER IS EXACTLY ZERO.

    Four partitions, built from the only two signals this architecture makes free, at every
    resolution from seven groups to sixty-eight. In every group of every one of them the best fixed
    strategy is `reference`, so the margin captured is nil. Even in the one-owner bucket, where
    `steno1` wins 349 tiles by 1235531 in total, it loses on the other 222 by more — which is
    `voxbreak`'s refutation arriving a second time from a completely different direction.

    THIS LAW REDDENS THE DAY A SIGNAL WORKS, which is the result the architecture needs and the best
    possible failure of a law."""
    return all(margin(s) == 0 for s in SIGNALS)


def one_owner_split():
    """(won, lost, net) for `steno1` inside the one-owner population — the mechanism of the zero.

    THIS IS WHERE THE WHOLE ARCHITECTURE FAILS, AND IT FAILS INSIDE ITS BEST POPULATION. `steno1`
    wins 349 of the 571 one-owner tiles and it wins them by a lot. It loses the other 222 and it
    loses them by MORE, because a certificate that fails does not merely forgo its saving: it pays
    the read, the encode, the verify and its own owner-only raster, and THEN pays the full tile
    anyway. Each losing tile costs about twice what each winning tile saves, so the population is
    net NEGATIVE despite two thirds of it being favourable."""
    sub = [r for r in rows() if r[2] == 1]
    won = sum(strategy_cost(r)["reference"] - strategy_cost(r)["steno1"]
              for r in sub if winner(r) == "steno1")
    lost = sum(strategy_cost(r)["steno1"] - strategy_cost(r)["reference"]
               for r in sub if winner(r) != "steno1")
    return won, lost, won - lost


def the_best_population_is_still_net_negative():
    """AND THAT IS WHY NO SIGNAL CAN WORK ON THIS WORKLOAD. A selector reading owner cardinality
    perfectly would fire `steno1` on the one-owner population, which is the most favourable
    population that exists here — and lose. The signal is not weak; the population it identifies is
    itself unprofitable, and no sharper reading of the same signal can repair that."""
    won, lost, net = one_owner_split()
    return won > 0 and lost > won and net < 0


def the_zero_is_a_measurement_and_not_an_inability():
    """THE PLANT, AND IT IS WHY THE ZEROS ABOVE MEAN SOMETHING. Handed the FRAME INDEX the same
    partition machinery finds margin. So the apparatus can find margin; it finds none in the
    geometry because there is none in the signals available. A census that returned zero everywhere
    including here would be an instrument that cannot measure, reported as a discovery."""
    return margin(PLANT) > 0


def the_frame_index_is_memorisation_and_is_scored_as_a_control():
    """AND IT IS KEPT OUT OF EVERY CLAIM. The frame index is not a property of a tile; it is a name
    for which picture is being drawn, and partitioning on it is memorising the benchmark rather than
    reading the geometry — the exact failure this discipline exists to prevent. It is declared as a
    PLANT, it is never in `SIGNALS`, and no margin is ever claimed from it."""
    return PLANT not in SIGNALS


def no_rule_is_frozen_here():
    """THE DISCIPLINE, NOT MODESTY. Choosing a threshold on the workload it was derived from is
    fitting. The honest sequence is measure, freeze the population, declare the rule, then test it on
    a SUBSEQUENT workload — and this rung performs the first two and STOPS, because the third has
    nothing to declare: every candidate rule measured to exactly zero."""
    return not hasattr(_sys.modules[__name__], "RULE") and all(margin(s) == 0 for s in SIGNALS)


def this_rung_is_a_census_not_an_implementation():
    """IT DELIBERATELY RUNS EVERY STRATEGY ON EVERY TILE, so the total work necessarily exceeds the
    reference and nobody can mistake these numbers for a speedup."""
    done = sum(r[7] + r[9] + r[10] + r[4] + r[6] for r in rows())
    return done > VM.reference_cost()


def nothing_is_promoted():
    return VB.nothing_is_promoted() and VF.nothing_is_promoted()


def no_wall_clock_enters_this_rung():
    import ast
    with open(os.path.join(_HERE, "voxschism.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


# ---- the record ------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-schism.txt")


def schism_digest():
    body = "\n".join("%s %d %d" % (s, strategy_total(s), wins()[s]) for s in STRATEGIES)
    body += "\n" + "\n".join("%s %d %d %d" % ((s,) + partition(s)) for s in SIGNALS)
    body += "\n%s %d %d %d" % ((PLANT,) + partition(PLANT))
    body += "\n" + "\n".join("%s %s" % (b, by_owner_bucket()[b]) for b in sorted(by_owner_bucket()))
    body += "\noracle %d inner %d setup %d split %s" % (oracle_total(), reference_inner(),
                                                       setup_common(), one_owner_split())
    return hashlib.sha256(MAGIC + b"|sch|" + body.encode()).hexdigest()


def generate():
    out = ["# URDRVXX1 the strategy census — emitted by voxschism.generate(), committed as an",
           "# artifact, re-derived by the gate.",
           "# world %s" % VR.world_digest(),
           "# YES ON THE POPULATIONS, NO ON THE SELECTION. Three strategies win somewhere and their",
           "# winning sets are DISJOINT BY OWNER COUNT; the tiled traversal wins NOTHING; and every",
           "# free signal captures EXACTLY ZERO of the hindsight oracle's margin.",
           "# THE `frame` ROW IS A PLANT AND NOT A SIGNAL: it proves the apparatus can find margin",
           "# when a partition is allowed to MEMORISE, which is what makes the zeros informative.",
           "#   strat  <strategy> <total operations> <tiles it would have won>",
           "#   signal <signal> <groups> <best-fixed total> <margin over the reference>",
           "#   plant  <frame> <groups> <best-fixed total> <margin>      MEMORISATION, NOT A SIGNAL",
           "#   pop    <owner bucket> <tiles> <winners> <oracle margin>",
           "#   totals <oracle> <reference inner> <common setup> <committed reference>",
           "#   split  <steno1 won> <steno1 lost> <net> INSIDE the one-owner population",
           "#   digest <schism digest>"]
    for s in STRATEGIES:
        out.append("strat %s %d %d" % (s, strategy_total(s), wins()[s]))
    for s in SIGNALS:
        out.append("signal %s %d %d %d" % ((s,) + partition(s)))
    out.append("plant %s %d %d %d" % ((PLANT,) + partition(PLANT)))
    for b in sorted(by_owner_bucket()):
        t, w, m = by_owner_bucket()[b]
        out.append("pop %d %d %s %d" % (b, t, ",".join("%s:%d" % x for x in w), m))
    out.append("totals %d %d %d %d" % (oracle_total(), reference_inner(), setup_common(),
                                       VM.reference_cost()))
    out.append("split %d %d %d" % one_owner_split())
    out.append("digest %s" % schism_digest())
    return "\n".join(out) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    out, world = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "strat" and (len(f) != 4 or f[1] not in STRATEGIES):
            raise VoxschismError("VOXSCHISM-REFUSE: a strat row naming no declared strategy")
        if f[0] == "signal" and (len(f) != 5 or f[1] not in SIGNALS):
            raise VoxschismError("VOXSCHISM-REFUSE: a signal row naming no declared signal")
        if f[0] == "plant" and (len(f) != 5 or f[1] != PLANT):
            raise VoxschismError("VOXSCHISM-REFUSE: a plant row naming no declared plant")
        if f[0] == "pop" and (len(f) != 5 or int(f[1]) not in (0,) + VF.OWNER_BUCKETS):
            raise VoxschismError("VOXSCHISM-REFUSE: a pop row naming no declared bucket")
        if f[0] == "totals" and len(f) != 5:
            raise VoxschismError("VOXSCHISM-REFUSE: a totals row of the wrong arity")
        if f[0] == "split" and len(f) != 4:
            raise VoxschismError("VOXSCHISM-REFUSE: a split row of the wrong arity")
        if f[0] not in ("strat", "signal", "plant", "pop", "totals", "split", "digest"):
            raise VoxschismError("VOXSCHISM-REFUSE: a row of unknown kind %r" % (f[0],))
        out.append(tuple(f))
    if world is None:
        raise VoxschismError("VOXSCHISM-REFUSE: the record names no world digest")
    if not out:
        raise VoxschismError("VOXSCHISM-REFUSE: the record has no rows")
    return world, out


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rs = parse()
    for r in rs:
        if r[0] == "strat" and (int(r[2]), int(r[3])) != (strategy_total(r[1]), wins()[r[1]]):
            return False
        if r[0] in ("signal", "plant") and tuple(int(x) for x in r[2:]) != partition(r[1]):
            return False
        if r[0] == "totals":
            if tuple(int(x) for x in r[1:]) != (oracle_total(), reference_inner(),
                                                setup_common(), VM.reference_cost()):
                return False
        if r[0] == "split" and tuple(int(x) for x in r[1:]) != one_owner_split():
            return False
    return next(r[1] for r in rs if r[0] == "digest") == schism_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("strat normal "):
            text = text.replace(ln, "strat clever " + " ".join(ln.split()[2:]), 1)
            break
    try:
        parse(text)
    except VoxschismError:
        return True
    return False


def told():
    w = wins()
    pops = by_owner_bucket()
    return ("YES ON THE POPULATIONS, NO ON THE SELECTION, AND THE SECOND NUMBER IS EXACTLY ZERO. "
            "Four strategies costed on every one of the %d tiles of the lattice, the setup they all "
            "pay identically (%d) excluded so it cannot flatten the comparison. THREE OF THEM WIN "
            "SOMEWHERE AND THE WINNING SETS ARE DISJOINT BY OWNER COUNT: `steno1` wins %d tiles and "
            "every one has exactly ONE owner, `stenoN` wins %d and every one has two or three, "
            "`reference` wins the other %d — the differentiation the architecture predicts, "
            "measured rather than asserted. AND `normal`, THE TILED TRAVERSAL, WINS ZERO: not "
            "merely dominated on the total, which `voxbreak` already showed, but never the best "
            "strategy for a SINGLE TILE anywhere, which is the mechanism behind the scaffolding tax "
            "— it is not an overhead on a good idea, it is the cost of a traversal that is never "
            "the right answer. A HINDSIGHT ORACLE picking the winner per tile costs %d against the "
            "reference's %d inner, which with the common setup is %d against %d — ELEVEN PER CENT "
            "UNDER, the first arrangement in this arc to get under the reference at all. BUT THE "
            "ORACLE READS THE OUTCOME. Replace it with the best FIXED rule per group and every free "
            "signal captures NOTHING: by owner cardinality %d groups, ZERO; by longest run %d, "
            "ZERO; by both bucketed %d, ZERO; by both EXACT and unbucketed %d, ZERO. In every group "
            "of every partition the best fixed strategy is `reference`. AND THE MECHANISM IS "
            "VISIBLE INSIDE THE BEST POPULATION: among the 571 ONE-OWNER tiles `steno1` wins %d and "
            "wins them by %d, then LOSES the other %d by %d — net %d. A certificate that fails does "
            "not merely forgo its saving; it pays the read, the encode, the verify and its own "
            "owner-only raster and THEN pays the full tile anyway, so each losing tile costs about "
            "twice what each winning tile saves and the most favourable population that exists here "
            "is itself net NEGATIVE. The signal is not weak — THE POPULATION IT IDENTIFIES IS "
            "UNPROFITABLE — which is `voxbreak`'s refutation arriving a second time from a "
            "completely different direction. AND THE ZERO IS A MEASUREMENT AND NOT AN INABILITY: handed the FRAME INDEX "
            "the same machinery finds %+d across %d groups, so the apparatus CAN find margin and "
            "finds none in the geometry because there is none in the signals available. The frame "
            "index is a PLANT and never a signal — partitioning on it is MEMORISING THE BENCHMARK "
            "rather than reading the structure. SO THE ARCHITECTURE'S TWO LEVELS COME APART: "
            "`voxfriction` established that owner cardinality predicts WHETHER THE CERTIFICATE "
            "FIRES, sharply; this rung establishes that the same signal carries NO information "
            "about WHICH STRATEGY WINS. Those were one question until they were measured apart, and "
            "a regime-selective renderer needs the second answered. NO RULE IS FROZEN HERE, because "
            "every candidate measured to zero and choosing a threshold on the workload it came from "
            "is fitting"
            % (len(rows()), setup_common(), w["steno1"], w["stenoN"], w["reference"],
               oracle_total(), strategy_total("reference"),
               oracle_total() + setup_common(), VM.reference_cost(),
               partition("owners")[0], partition("run")[0], partition("owners_x_run")[0],
               partition("exact")[0],
               w["steno1"], one_owner_split()[0], pops[1][0] - w["steno1"],
               one_owner_split()[1], one_owner_split()[2],
               margin(PLANT), partition(PLANT)[0]))


def scene_case(name):
    if name == "strategies":
        return repr(tuple((s, strategy_total(s), wins()[s]) for s in STRATEGIES)
                    + (oracle_total(), reference_inner(), setup_common()))
    if name == "signals":
        return repr(tuple((s,) + partition(s) for s in SIGNALS) + ((PLANT,) + partition(PLANT),))
    if name == "populations":
        return repr(tuple((b,) + by_owner_bucket()[b] for b in sorted(by_owner_bucket()))
                    + (one_owner_split(),))
    raise VoxschismError("VOXSCHISM-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("strategies", "signals", "populations")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxschism.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxschismError("VOXSCHISM-REFUSE: no golden named %r" % name)
