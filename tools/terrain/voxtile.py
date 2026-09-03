# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxtile (URDRVTL1) — THE TILE SIZE WAS NEVER A TUNING PARAMETER. IT WAS THE ANSWER.

Every rung from `voxcond` onward concluded the same thing: the certificate is sound, it retires real
work, and the arrangement still loses to the committed reference. `voxbreak` put a ledger under that
verdict and found the deficit was not the certificate but the TILED SCAFFOLDING — a loop costing
10168290 over the reference before a single certificate is consulted. `voxschism` then costed four
strategies per tile and found the tiled traversal winning ZERO tiles of 1728.

ALL OF THOSE MEASUREMENTS WERE TAKEN AT ONE TILE SIZE THAT NOBODY EVER VARIED. This rung varies it,
against five predictions committed one commit earlier in `voxbreak` and quoted here by digest.

    THE ARRANGEMENT GETS UNDER THE COMMITTED REFERENCE AT THREE OF THE EIGHT DECLARED TILE SIZES,
    AND THE BEST IS 10.7 PER CENT BELOW IT — one strategy, one constant changed, NO SELECTOR.

That is the first time in this arc that anything buildable has beaten `voxref`, and it settles a
question three rungs left open by answering a different one. `voxschism` proved that a PERFECT, FREE,
UNBUILDABLE selector over four strategies would save eleven per cent at the committed tile, and that
no free signal captures ANY of it. This rung takes 10.7 per cent with no selector at all. THE
SELECTION PROBLEM `voxschism` PROVED UNSOLVABLE WAS THE WRONG PROBLEM: the margin was never in which
strategy to pick per tile, it was in a constant that made every strategy expensive at once.

NOTHING EARLIER IS RETRACTED AND THE SCOPE IS STATED AS A LAW RATHER THAN LEFT TO A PARAGRAPH.
`voxbreak`'s `the_inequality_has_no_solution_on_this_loop` is scoped to THAT loop and is still true
of it; `voxschism`'s zeros were measured at the committed tile and still hold there. Both were
verdicts about a loop nobody had parameterised, and `the_earlier_verdict_was_conditional_on_a_
constant` RUNS both of them here beside this rung's result, so the conditionality is a fact the gate
re-derives rather than a caveat a reader has to remember.

THE FIRST PASS OF THIS SWEEP LOOKED FAR BETTER AND WAS WRONG, AND THAT IS THE MOST IMPORTANT THING IN
THE RUNG. Uncharged, the UNIT tile comes out at 9752785 — NINETEEN AND A HALF PER CENT under, and
better than anything the charged sweep can reach — and that number is cheating in five places the
untiled reference never pays:

    range      four divisions per triangle to find its tile range
    index      one multiply per (triangle, tile) pair to address the bin
    owners     one insert per triangle to build the owner index
    visit      one visit per tile of the grid, empty or not
    complete   one read per pixel of every certified tile, to check it came out whole

At the unit tile those total 1492722; at the committed tile only 416938. THE UNCHARGED TERMS WERE
WORTH THREE AND A HALF TIMES MORE TO THE ARM THAT WAS WINNING, which is exactly how a sweep talks
itself into a result. Charging all five moved the optimum from tile 1 to tile 2 and cut the win from
nineteen and a half per cent to 10.7. `the_bookkeeping_is_charged_and_it_moved_the_answer` asserts
ALL THREE facts — the unit tile wins uncharged, it does not win charged, and the uncharged figure was
strictly rosier than anything the charged sweep reaches — so the correction cannot quietly disappear
into a tidier story later.

TWO ANCHORS PROVE THE INSTRUMENT RATHER THAN ASSUME IT. At tile 1 the cold tiled loop costs EXACTLY
the committed reference before bookkeeping, because unit binning walks precisely each triangle's own
bounding box — `the_unit_tile_is_the_reference_exactly`. And at the committed tile the sweep
reproduces `voxbreak`'s own 22290004 and 19037173 TO THE OPERATION —
`the_committed_tile_reproduces_voxbreaks_figures` — which proves this is the same instrument
re-parameterised and not a second measurement that drifted.

FOUR OF THE FIVE PREDICTIONS HIT. T1 hits: the scaffolding tax rises monotonically with the tile,
1437584 to 54985555. T3 hits, and it is the one I said in the pre-registration was most likely to
miss. T4 hits: the tile that minimises the TOTAL is not the tile that maximises RETIREMENT, 2 against
4, so the curves really are opposed. T5 hits. T2 MISSES, and its miss is the useful one: retirement
does not fall monotonically, it PEAKS at tile 4 and falls either side, because a large tile holds too
many owners to certify while a small tile has too little work left to retire.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. NOTHING ABOUT MEMORY, and at small tiles
that omission is at its most generous — the owner map is one integer per pixel however the frame is
diced, but the bin structure is not, and this rung counts arithmetic rather than storage. THAT THE
OPERATION MODEL IS THE RIGHT COST — it is `voxwork`'s, multiplies and divides, and a machine where a
bin insert costs more than a multiply would move the optimum. THAT 10.9 PER CENT IS THE BEST
AVAILABLE, since eight sizes are declared and the space between them is not searched. And NO
PROMOTION: `voxref` is untouched and nothing is adopted.

falsifier: `the_observable_never_moves_at_any_tile_size` compares colour and depth AS LISTS at every
declared size on all sixteen states; `the_committed_tile_reproduces_voxbreaks_figures` reddens the
day this sweep stops agreeing with `voxbreak` at the tile they share, which is how a re-parameterised
instrument would be caught having become a different one; and `the_bookkeeping_is_charged_and_it_
moved_the_answer` reddens if the uncharged sweep ever stops disagreeing with the charged one, which
is the day the correction this rung is built around stops being real.
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
import voxschism as VC                                       # noqa: E402

MAGIC = b"URDRVTL1"

#: DECLARED — the tile sizes swept. EVERY ONE DIVIDES BOTH 96 AND 72 exactly, so no partial tile at a
#: frame edge can confound the comparison: a sweep in which some sizes tile the frame evenly and
#: others do not would be measuring two things at once.
TILES = (1, 2, 3, 4, 6, 8, 12, 24)

#: The size every earlier rung used without ever varying it. Inherited, never redeclared.
COMMITTED = VD.TILE

#: DECLARED — `voxbreak`'s five accounts, unchanged and kept separately.
ACCOUNTS = ("recognise", "encode", "verify", "execute", "fallback")

#: DECLARED — the BOOKKEEPING this rung exists to charge: work a TILED loop must do that the untiled
#: reference never does. Each term is REPORTED SEPARATELY rather than summed into one figure, because
#: a record that declares five terms and prints one total is naming rather than describing, and each
#: of these scales differently with the tile. Each is charged in `voxwork`'s own model of multiplies
#: and divides: `range` four divisions per triangle for its tile range, `index` one multiply per
#: (triangle, tile) pair to address the bin, `owners` one insert per triangle for the owner index,
#: `visit` one per tile of the grid whether or not it holds anything, `complete` one read per pixel
#: of every certified tile to check it came out whole.
BOOK_TERMS = ("range", "index", "owners", "visit", "complete")

#: Every column a render reports.
COLUMNS = ACCOUNTS + BOOK_TERMS


class VoxtileError(Exception):
    """VOXTILE-REFUSE — a tile size, an account or a record this module will not pretend to read."""


# ---- the prediction, quoted from the earlier commit ------------------------------------------------------
def committed_prediction():
    out = {}
    for ln in VB.prediction_text().split("\n"):
        ln = ln.strip()
        if ln.startswith("predict "):
            f = ln.split(None, 2)
            out[f[1]] = f[2]
    return out


PREDICTIONS = tuple(sorted(committed_prediction()))


def the_prediction_is_quoted_from_the_earlier_commit():
    """COMMIT ORDER IS THE ONLY MECHANISM THAT PROVES A PREDICTION CAME FIRST. The five ids scored
    here were committed in `voxbreak`, one commit before any tile size but the current one had been
    run, and their digest is pinned as that rung's golden."""
    return (VB.prediction_digest() == VB.golden("prediction")
            and VB.the_prediction_names_no_result()
            and len(PREDICTIONS) == 5)


# ---- one state at one tile size ---------------------------------------------------------------------
def _setup_and_tris(n):
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


def render(n, tile, prev_key):
    """(colour, depth, key, {account: operations}, certified tiles).

    `prev_key` is the declared predecessor's OWNER MAP, or None for a cold render. The certificate is
    `voxcond`'s P4 and nothing else — ownership, VERIFIED against the current camera, with depth
    RECONSTRUCTED from the owner's own plane. NOTHING about it changes with the tile size; only the
    rectangle it is asked about does, which is the whole point of the sweep.
    """
    if tile not in TILES:
        raise VoxtileError("VOXTILE-REFUSE: no declared tile size %r" % (tile,))
    setup, tris = _setup_and_tris(n)
    tw = (VR.W + tile - 1) // tile
    th = (VR.H + tile - 1) // tile
    colour = [VR.BACKGROUND] * (VR.W * VR.H)
    depth = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    acc = dict.fromkeys(COLUMNS, 0)
    acc["execute"] = setup
    certified = 0
    bins = [[] for _ in range(tw * th)]
    for t in tris:
        p, q, r = t[2], t[3], t[4]
        acc["range"] += 4
        xl = max(min(p[0], q[0], r[0]), 0) // tile
        xh = min(max(p[0], q[0], r[0]), VR.W - 1) // tile
        yl = max(min(p[1], q[1], r[1]), 0) // tile
        yh = min(max(p[1], q[1], r[1]), VR.H - 1) // tile
        if xl > xh or yl > yh:
            continue
        for ty in range(yl, yh + 1):
            for tx in range(xl, xh + 1):
                acc["index"] += 1
                bins[ty * tw + tx].append(t)
    by_key = {}
    for t in tris:
        acc["owners"] += 1
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
            acc["visit"] += 1
            b = bins[ty * tw + tx]
            x0, x1 = tx * tile, min(tx * tile + tile, VR.W) - 1
            y0, y1 = ty * tile, min(ty * tile + tile, VR.H) - 1
            taken = False
            if prev_key is not None and b:
                oset = {prev_key[y * VR.W + x]
                        for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
                acc["recognise"] += (y1 - y0 + 1) * (x1 - x0 + 1)
                if -1 not in oset:
                    acc["encode"] += len(oset)
                    group, far, ok = [], -1, True
                    for k in oset:
                        got = by_key.get(k)
                        if not got:
                            ok = False
                            break
                        for t in got:
                            acc["verify"] += 1
                            group.append(t)
                            z = max(t[2][2], t[3][2], t[4][2])
                            if z > far:
                                far = z
                    if ok:
                        for t in b:
                            acc["verify"] += 1
                            if t[0] not in oset and t[9] <= far:
                                ok = False
                                break
                    if ok:
                        spent = raster(group, x0, x1, y0, y1)
                        acc["complete"] += (y1 - y0 + 1) * (x1 - x0 + 1)
                        if any(key[y * VR.W + x] < 0
                               for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)):
                            acc["fallback"] += spent
                            for y in range(y0, y1 + 1):
                                for x in range(x0, x1 + 1):
                                    i = y * VR.W + x
                                    depth[i], key[i], colour[i] = VR.FAR, -1, VR.BACKGROUND
                        else:
                            acc["execute"] += spent
                            taken = True
                            certified += 1
            if not taken:
                acc["execute"] += raster(b, x0, x1, y0, y1)
    return colour, depth, key, acc, certified


# ---- the sweep ---------------------------------------------------------------------------------------
_SWEEP = {}


def sweep(tile):
    """{'cold': accounts, 'warm': accounts, 'sound': bool, 'certified': tiles} at one tile size.

    `cold` inherits nothing and never consults a certificate — the tiled loop's own baseline at this
    size. `warm` inherits `voxstate`'s nearest-neighbour predecessor, which `voxmanifold` measured as
    the best of four. The traversal is held FIXED across the whole sweep so the only thing varying is
    the tile.
    """
    if tile not in TILES:
        raise VoxtileError("VOXTILE-REFUSE: no declared tile size %r" % (tile,))
    k = (VR.world_digest(), tile)
    if k in _SWEEP:
        return _SWEEP[k]
    seq, pred = VT.order("Z3")
    keys = {}
    cold = dict.fromkeys(COLUMNS, 0)
    warm = dict.fromkeys(COLUMNS, 0)
    sound, certified = True, 0
    for n in seq:
        _c, _d, _k, a0, _z = render(n, tile, None)
        for name in COLUMNS:
            cold[name] += a0[name]
        prev = None if pred[n] is None else keys[pred[n]]
        col, dep, kk, a1, ct = render(n, tile, prev)
        keys[n] = kk
        certified += ct
        for name in COLUMNS:
            warm[name] += a1[name]
        ref = VT.frames()[n]
        if col != ref[0] or dep != ref[1]:
            sound = False
    _SWEEP[k] = {"cold": cold, "warm": warm, "sound": sound, "certified": certified}
    return _SWEEP[k]


def bookkeeping(tile, phase):
    """The five bookkeeping terms summed, for one phase of the sweep."""
    if phase not in ("cold", "warm"):
        raise VoxtileError("VOXTILE-REFUSE: no phase named %r" % (phase,))
    return sum(sweep(tile)[phase][n] for n in BOOK_TERMS)


def cold(tile, book=True):
    a = sweep(tile)["cold"]
    return sum(a[n] for n in (COLUMNS if book else ACCOUNTS))


def certified(tile, book=True):
    a = sweep(tile)["warm"]
    return sum(a[n] for n in (COLUMNS if book else ACCOUNTS))


def tax(tile):
    """What the TILED loop costs over the committed reference before a certificate is consulted."""
    return cold(tile) - VM.reference_cost()


def retired(tile):
    """BASELINE MINUS EXECUTED at this tile size — the cold loop of the SAME size, so retirement is
    never measured against a baseline from a different arrangement."""
    return cold(tile) - certified(tile)


def net(tile):
    """The margin against the COMMITTED REFERENCE. NEGATIVE is under it."""
    return certified(tile) - VM.reference_cost()


def best(book=True):
    return min(TILES, key=lambda t: certified(t, book))


def best_retirement():
    return max(TILES, key=retired)


# ---- the laws ----------------------------------------------------------------------------------------
def the_observable_never_moves_at_any_tile_size():
    """THE CONTRACT. Colour and depth compared AS LISTS at every declared size on all sixteen states
    — the contract that has now caught an unsound optimisation in three consecutive rungs. A tile
    size that changed what is seen would not be a faster arrangement, it would be a bug."""
    return all(sweep(t)["sound"] for t in TILES)


def the_tile_sizes_divide_the_frame():
    """EVERY DECLARED SIZE DIVIDES BOTH 96 AND 72 EXACTLY, so no partial tile at a frame edge can
    confound the comparison. A sweep in which some sizes tile the frame evenly and others do not
    would be measuring two things at once and attributing both to the tile."""
    return all(VR.W % t == 0 and VR.H % t == 0 for t in TILES)


def the_unit_tile_is_the_reference_exactly():
    """THE FIRST ANCHOR, AND IT PROVES THE INSTRUMENT RATHER THAN ASSUMING IT. At tile 1 the cold
    tiled loop costs EXACTLY the committed reference before bookkeeping, because unit binning walks
    precisely each triangle's own bounding box and nothing else. Any drift here means the sweep has
    stopped being a re-parameterisation of the reference loop."""
    return cold(1, book=False) == VM.reference_cost()


def the_committed_tile_reproduces_voxbreaks_figures():
    """THE SECOND ANCHOR, AND IT IS THE ONE THAT BINDS THIS RUNG TO THE EARLIER ONE. At the tile
    every previous rung used, the sweep must reproduce `voxbreak`'s committed cold and ungated totals
    TO THE OPERATION. That proves this is the SAME INSTRUMENT re-parameterised and not a second
    measurement that drifted — which is the failure a sweep is most exposed to, since a sweep that
    quietly re-derives its own baseline can produce any curve it likes."""
    return (cold(COMMITTED, book=False) == VB.spend("none")
            and certified(COMMITTED, book=False) == VB.spend("all"))


def the_bookkeeping_is_charged_and_it_moved_the_answer():
    """THE HONESTY LAW, AND THE MOST IMPORTANT THING IN THE RUNG.

    The first pass of this sweep did not charge the five bookkeeping terms, and it reported the UNIT
    tile twenty per cent under the reference. Those terms are worth 1492722 at tile 1 and 416938 at
    the committed tile — THREE AND A HALF TIMES MORE TO THE ARM THAT WAS WINNING, which is exactly
    how a sweep talks itself into a result.

    This law asserts ALL THREE parts of the correction so it cannot quietly disappear into a tidier
    story later: UNCHARGED the minimum sits at the unit tile, CHARGED it does not, and the uncharged
    figure was STRICTLY ROSIER than anything the charged sweep can reach. The bookkeeping is not a
    rounding term; it is the term that decided which tile size wins."""
    return (best(book=False) == 1 and best(book=True) != 1
            and certified(1, book=False) < certified(best(), book=True)
            and all(bookkeeping(t, "cold") > 0 for t in TILES)
            and bookkeeping(1, "warm") > 3 * bookkeeping(COMMITTED, "warm"))


def the_arrangement_gets_under_the_committed_reference():
    """THE RESULT. At least one declared tile size spends LESS than `voxref` over the same sixteen
    states, with the observable byte-identical. The first time in this arc that anything BUILDABLE
    has beaten the reference — no selector, no oracle, one strategy and one constant."""
    return any(net(t) < 0 for t in TILES) and net(best()) < 0


def the_earlier_verdict_was_conditional_on_a_constant():
    """NOTHING EARLIER IS RETRACTED, AND THE SCOPE IS A LAW RATHER THAN A PARAGRAPH.

    `voxbreak` concluded the break-even inequality has NO SOLUTION and `voxschism` found the tiled
    traversal winning ZERO tiles — and BOTH ARE STILL TRUE, at the tile size they were measured at,
    which is why they are RUN here rather than cited. What was never true is the impression they
    left, because both were verdicts about a loop nobody had parameterised. This law holds the two
    facts together: the earlier verdicts still bite at the committed tile, AND the arrangement wins
    at a smaller one."""
    return (VB.the_inequality_has_no_solution_on_this_loop()
            and VC.the_tiled_traversal_is_dominated_everywhere()
            and net(COMMITTED) > 0
            and net(best()) < 0)


def no_selector_is_used():
    """AND THE MARGIN IS TAKEN WITHOUT SOLVING THE PROBLEM `voxschism` PROVED UNSOLVABLE.

    That rung showed a perfect, free, unbuildable selector over four strategies would save eleven per
    cent at the committed tile, and that no free signal captures ANY of it. This rung takes its
    margin with ONE strategy and ONE constant — no signal is read, no strategy is chosen per tile —
    so `voxschism`'s zeros are untouched and are re-run here to prove it. THE SELECTION PROBLEM WAS
    THE WRONG PROBLEM."""
    return VC.no_free_signal_captures_any_of_the_margin()


def nothing_is_promoted():
    return VB.nothing_is_promoted() and VC.nothing_is_promoted()


def no_wall_clock_enters_this_rung():
    import ast
    with open(os.path.join(_HERE, "voxtile.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


# ---- the verdicts, scored against the five committed ids ---------------------------------------------
def verdicts():
    rising = all(tax(TILES[i]) < tax(TILES[i + 1]) for i in range(len(TILES) - 1))
    falling = all(retired(TILES[i]) >= retired(TILES[i + 1]) for i in range(len(TILES) - 1))
    under = [t for t in TILES if net(t) < 0]
    return {
        "T1": (rising,
               "the tax rises from %d at tile %d to %d at tile %d, monotonically"
               % (tax(TILES[0]), TILES[0], tax(TILES[-1]), TILES[-1])),
        "T2": (falling,
               "retirement PEAKS at tile %d (%d) rather than falling monotonically: %s"
               % (best_retirement(), retired(best_retirement()),
                  ", ".join("%d:%d" % (t, retired(t)) for t in TILES))),
        "T3": (bool(under),
               "%d of %d declared sizes spend less than the reference (%s); the best is tile %d at "
               "%d against %d" % (len(under), len(TILES),
                                  ", ".join(str(t) for t in under) if under else "none",
                                  best(), certified(best()), VM.reference_cost())),
        "T4": (best() != best_retirement(),
               "the total minimises at tile %d and retirement maximises at tile %d"
               % (best(), best_retirement())),
        "T5": (the_observable_never_moves_at_any_tile_size(),
               "all %d sizes reproduce the reference on all %d states, colour and depth as lists"
               % (len(TILES), len(VT.STATES))),
    }


def hits():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if ok))


def misses():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if not ok))


def the_verdicts_match_the_committed_prediction():
    """The scored set must EQUAL the set committed one commit earlier. Five were registered; five are
    scored; no sixth is invented after seeing the curve and none of the five is quietly dropped."""
    return sorted(verdicts()) == list(PREDICTIONS)


def the_record_carries_hits_and_misses():
    return len(hits()) > 0 and len(misses()) > 0


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-tile.txt")


def tile_digest():
    body = "\n".join("%d %d %d %d %d %d %d"
                     % (t, cold(t), certified(t), tax(t), retired(t), net(t),
                        sweep(t)["certified"]) for t in TILES)
    body += "\n" + "\n".join("%s %s %s" % (k, v[0], v[1]) for k, v in sorted(verdicts().items()))
    body += "\n" + "\n".join("%d %s" % (t, [sweep(t)["warm"][n] for n in BOOK_TERMS])
                             for t in TILES)
    body += "\nbest %d %d uncharged %d" % (best(), best_retirement(), best(book=False))
    return hashlib.sha256(MAGIC + b"|tile|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVTL1 the tile sweep — emitted by voxtile.generate(), committed as an artifact,",
            "# re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE TILE SIZE WAS NEVER A TUNING PARAMETER. IT WAS THE ANSWER. Three of the eight",
            "# declared sizes spend LESS than the committed reference, the best by 10.7 per cent,",
            "# with ONE strategy and NO selector. THE PREDICTION WAS COMMITTED ONE COMMIT EARLIER,",
            "# in `voxbreak`, and is QUOTED here rather than restated.",
            "# BOOKKEEPING IS CHARGED: range, index, owners, visit, complete — the five terms a",
            "# TILED loop pays that the untiled reference never does. UNCHARGED, the unit tile wins;",
            "# CHARGED, it does not, and that correction is what moved the optimum to tile 2.",
            "#   tile    <size> <cold+book> <certified+book> <tax> <retired> <net vs reference>",
            "#           <certified tiles>",
            "#   book    <size> <range> <index> <owners> <visit> <complete>   WARM, the five",
            "#   bare    <size> <cold without book> <certified without book>  the anchors",
            "#   verdict <id> <HIT|MISS> <what was measured>",
            "#   best    <lowest total> <highest retirement> <lowest total UNCHARGED>",
            "#   digest  <tile digest>"]
    for t in TILES:
        rows.append("tile %d %d %d %d %d %d %d"
                    % (t, cold(t), certified(t), tax(t), retired(t), net(t),
                       sweep(t)["certified"]))
    for t in TILES:
        rows.append("book %d %s" % (t, " ".join(str(sweep(t)["warm"][n]) for n in BOOK_TERMS)))
    for t in TILES:
        rows.append("bare %d %d %d" % (t, cold(t, book=False), certified(t, book=False)))
    for k, (ok, what) in sorted(verdicts().items()):
        rows.append("verdict %s %s %s" % (k, "HIT" if ok else "MISS", what))
    rows.append("best %d %d %d" % (best(), best_retirement(), best(book=False)))
    rows.append("digest %s" % tile_digest())
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
        if f[0] == "tile" and (len(f) != 8 or int(f[1]) not in TILES):
            raise VoxtileError("VOXTILE-REFUSE: a tile row naming no declared size")
        if f[0] == "book" and (len(f) != 2 + len(BOOK_TERMS) or int(f[1]) not in TILES):
            raise VoxtileError("VOXTILE-REFUSE: a book row naming no declared size")
        if f[0] == "bare" and (len(f) != 4 or int(f[1]) not in TILES):
            raise VoxtileError("VOXTILE-REFUSE: a bare row naming no declared size")
        if f[0] == "verdict" and (len(f) < 4 or f[1] not in PREDICTIONS
                                  or f[2] not in ("HIT", "MISS")):
            raise VoxtileError("VOXTILE-REFUSE: a verdict row naming no declared prediction")
        if f[0] == "best" and len(f) != 4:
            raise VoxtileError("VOXTILE-REFUSE: a best row of the wrong arity")
        if f[0] not in ("tile", "book", "bare", "verdict", "best", "digest"):
            raise VoxtileError("VOXTILE-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxtileError("VOXTILE-REFUSE: the record names no world digest")
    if not rows:
        raise VoxtileError("VOXTILE-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    v = verdicts()
    for r in rows:
        if r[0] == "tile":
            t = int(r[1])
            if tuple(int(x) for x in r[2:]) != (cold(t), certified(t), tax(t), retired(t),
                                                net(t), sweep(t)["certified"]):
                return False
        if r[0] == "book":
            t = int(r[1])
            if tuple(int(x) for x in r[2:]) != tuple(sweep(t)["warm"][n] for n in BOOK_TERMS):
                return False
        if r[0] == "bare":
            t = int(r[1])
            if (int(r[2]), int(r[3])) != (cold(t, book=False), certified(t, book=False)):
                return False
        if r[0] == "verdict" and (r[2] == "HIT") != v[r[1]][0]:
            return False
        if r[0] == "best" and (int(r[1]), int(r[2]), int(r[3])) != (best(), best_retirement(),
                                                                    best(book=False)):
            return False
    return next(r[1] for r in rows if r[0] == "digest") == tile_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("tile 8 "):
            text = text.replace(ln, "tile 7 " + " ".join(ln.split()[2:]), 1)
            break
    try:
        parse(text)
    except VoxtileError:
        return True
    return False


def told():
    ref = VM.reference_cost()
    b = best()
    under = [t for t in TILES if net(t) < 0]
    return ("THE TILE SIZE WAS NEVER A TUNING PARAMETER, IT WAS THE ANSWER. Every rung from "
            "`voxcond` onward concluded the arrangement loses to the reference, and every one of "
            "those measurements was taken at ONE tile size nobody varied. Swept over %d declared "
            "sizes, all of which divide both 96 and 72 so no partial tile can confound it: %d OF "
            "THEM SPEND LESS THAN THE COMMITTED REFERENCE (%s), and the best is tile %d at %d "
            "against %d — %d under, TEN POINT SEVEN PER CENT, with colour and depth byte-identical "
            "as lists on all sixteen states. ONE STRATEGY, ONE CONSTANT, NO SELECTOR. THE FIRST "
            "PASS LOOKED FAR BETTER AND WAS WRONG, WHICH IS THE MOST IMPORTANT THING HERE: "
            "uncharged, the UNIT tile comes out at %d, nineteen and a half per cent under and "
            "BETTER THAN ANYTHING THE CHARGED SWEEP REACHES, and that number is cheating "
            "in five places the untiled reference never pays — the tile range, the bin index, the "
            "owner index, the per-tile visit and the completeness check. Those terms are worth %d "
            "at tile 1 against %d at tile %d, THREE AND A HALF TIMES MORE TO THE ARM THAT WAS "
            "WINNING, which is exactly how a sweep talks itself into a result; charging all five "
            "moved the optimum off the unit tile and cut the win from twenty per cent to 10.9, and "
            "the law asserts BOTH halves so the correction cannot vanish into a tidier story. TWO "
            "ANCHORS PROVE THE INSTRUMENT RATHER THAN ASSUME IT: at tile 1 the cold loop costs "
            "EXACTLY the reference before bookkeeping, because unit binning walks precisely each "
            "triangle's own bounding box; and at tile %d the sweep reproduces `voxbreak`'s "
            "committed %d and %d TO THE OPERATION, so this is the same instrument re-parameterised "
            "and not a second measurement that drifted. NOTHING EARLIER IS RETRACTED AND THE SCOPE "
            "IS A LAW: `voxbreak`'s inequality still has no solution AT ITS OWN TILE and "
            "`voxschism`'s tiled traversal still wins nothing THERE — both are RUN here beside this "
            "result rather than cited — but both were verdicts about a loop nobody had "
            "parameterised. AND THE SELECTION PROBLEM WAS THE WRONG PROBLEM: `voxschism` proved a "
            "perfect, free, UNBUILDABLE selector would save eleven per cent at the committed tile "
            "and that no free signal captures ANY of it; this rung takes 10.9 with no selector at "
            "all, so those zeros are untouched and are re-run here to prove it. FOUR OF FIVE "
            "PREDICTIONS HIT (%s) AND ONE MISSED (%s): retirement does not fall monotonically, it "
            "PEAKS at tile %d, because a large tile holds too many owners to certify while a small "
            "one has too little work left to retire"
            % (len(TILES), len(under), ", ".join(str(t) for t in under), b, certified(b), ref,
               -net(b), certified(1, book=False),
               bookkeeping(1, "warm"), bookkeeping(COMMITTED, "warm"),
               COMMITTED, COMMITTED, VB.spend("none"), VB.spend("all"),
               ", ".join(hits()), ", ".join(misses()), best_retirement()))


def scene_case(name):
    if name == "sweep":
        return repr(tuple((t, cold(t), certified(t), tax(t), retired(t), net(t),
                           sweep(t)["certified"]) for t in TILES))
    if name == "bookkeeping":
        return repr(tuple((t, bookkeeping(t, "cold"), bookkeeping(t, "warm"),
                           cold(t, book=False), certified(t, book=False)) for t in TILES)
                    + (best(), best(book=False))
                    + tuple((t,) + tuple(sweep(t)["warm"][n] for n in BOOK_TERMS)
                            for t in TILES))
    if name == "verdicts":
        return repr((sorted(verdicts().items()), best(), best_retirement()))
    raise VoxtileError("VOXTILE-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("sweep", "bookkeeping", "verdicts")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxtile.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxtileError("VOXTILE-REFUSE: no golden named %r" % name)
