# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""dirward — directed-reachability structural anti-cheat (T3.26, MMO Stage E): the topological anti-cheat
refined from UNDIRECTED reachability (URDRWARD1/2) to DIRECTED reachability, so a ONE-WAY cliff is modelled
honestly. `warden` joined adjacent cells with an UNDIRECTED edge — a step legal BOTH ways (`|Δground| <=
MAX_STEP`). That criterion is blind to direction: a cliff you can descend but not climb has `|Δ| > MAX_STEP`,
so the undirected warden sees NO edge at all and treats the one-way cliff as a SOLID WALL.

TWO THINGS THE UNDIRECTED WARDEN GETS WRONG ON ONE-WAY TERRAIN (both measured):
  * IT FALSE-REFUSES THE LEGAL DESCENT. An actor drops off a ledge — a legal move (`Δground = -100 <=
    MAX_STEP`). `warden.admit_position(top, bottom)` sees no undirected edge, calls them different components,
    and REFUSES `WARD-UNREACH` — it would kick an honest player. `dirward.admit_move(top, bottom)` ADMITS: a
    directed path exists.
  * IT CANNOT DISTINGUISH A ONE-WAY CLIFF FROM A WALL. For the illegal climb `bottom -> top` AND for a genuine
    impassable wall, the undirected warden returns the SAME `WARD-UNREACH`. `dirward` separates them: the
    climb is `WARD-ONEWAY` (you may go the other way), the wall is `WARD-UNREACH` (no directed path either
    way).

THE INVARIANT. The DIRECTED walkable graph has an edge `a -> b` iff the step is enterable that way (`field[b]
- field[a] <= MAX_STEP`; descending always legal, ascending only within the step law). `can_reach` is its
transitive closure — ASYMMETRIC: on the pinned plateau-over-plain world, `can_reach(top, bottom)` is true and
`can_reach(bottom, top)` is false. `reach_asymmetry` counts the ordered pairs reachable only one way; it is
0 exactly when reachability is symmetric (flat or gently-sloped terrain, every adjacent step legal both ways)
and positive whenever a one-way drop or a raised wall is present (a raised wall is itself one-way — you may
drop off it but not climb onto it) — so the directed refinement is non-vacuous where it matters and collapses
to the undirected picture on gentle terrain.

HONEST SCOPE ON THE SCC COUNT. `num_scc` (strongly-connected = mutual-reachability classes) is the directed
analog of β₀. Because a both-ways edge is a 2-cycle, every undirected component sits inside one SCC, so
`num_scc <= betti0` always; on these worlds they are EQUAL (a strict coarsening needs a directed cycle
BRIDGING undirected components, not shown here). The live directed structure is therefore the REACHABILITY
ASYMMETRY, not a component-count gap — `dirward` binds both but rests its claim on the former.

THE GAP IS TOPOLOGICAL, NOT KINEMATIC. A claimed climb-back TRAJECTORY is already refused per-step (the uphill
step is a `warden`/`glide` `WARD-TUNNEL`). `dirward` closes only the BARE-POSITION hole: a move asserted as
(anchor, claim) with no path to inspect.

GRADE. The directed reachability and its asymmetry, the one-way / unreachable refusals, the two
undirected-warden failure witnesses (false-refused descent; one-way-vs-wall conflation), and their
determinism are MEASURED (exact, reproducible, a defect diverges). `does_not_show`: the KINEMATIC trajectory
case (already covered by the `warden` step law); a strict `num_scc < betti0` coarsening (needs a bridging
directed cycle, not built here); variable / weighted step costs (a single `MAX_STEP`); the URDRPD1 homology
CROSS-PLACEMENT (computed directly here); and any WALL-CLOCK cost (`NOT_MEASURED` until a sealed bench, Stage
H). Refusals are typed `WARD-REFUSE` with a sub-code (`WARD-ONEWAY`, `WARD-UNREACH`, `WARD-MALFORMED`)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRWARD3"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import warden as _W                                              # undirected reachability (the contrast)
import glide as _GL                                              # the continuous mover (for honest descents)


def _dims(field):
    if not (isinstance(field, tuple) and field and isinstance(field[0], tuple) and field[0]):
        raise _W.WardError("WARD-MALFORMED", "field must be a non-empty rectangular grid")
    w = len(field[0])
    for row in field:
        if len(row) != w:
            raise _W.WardError("WARD-MALFORMED", "field rows must be equal width")
    return w, len(field)


def _reach_from(field, src, max_step):
    """The set of cells reachable from `src` by a DIRECTED walk — an edge `a -> b` iff `field[b] - field[a]
    <= max_step` (descending always legal, ascending only within the step law). Exact, division-free BFS."""
    w, h = _dims(field)
    seen = {src}
    stack = [src]
    while stack:
        cx, cy = stack.pop()
        base = field[cy][cx]
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and field[ny][nx] - base <= max_step:
                seen.add((nx, ny))
                stack.append((nx, ny))
    return seen


def can_reach(field, a, b, max_step):
    """True iff there is a DIRECTED walkable path from `a` to `b` (a may descend to b even if b cannot climb
    back to a)."""
    w, h = _dims(field)
    for c in (a, b):
        if not (isinstance(c, tuple) and len(c) == 2 and 0 <= c[0] < w and 0 <= c[1] < h):
            raise _W.WardError("WARD-MALFORMED", f"cell {c!r} off the {w}x{h} field")
    return b in _reach_from(field, a, max_step)


def _all_reach(field, max_step):
    w, h = _dims(field)
    cells = [(x, y) for y in range(h) for x in range(w)]
    return cells, {c: _reach_from(field, c, max_step) for c in cells}


def scc(field, max_step):
    """A cell -> SCC-root map. Two cells share a strongly-connected component iff they are MUTUALLY reachable
    (a -> b AND b -> a). Root = lexicographically smallest cell of the class (deterministic). Exact."""
    cells, reach = _all_reach(field, max_step)
    root = {}
    for c in cells:
        if c in root:
            continue
        cls = [d for d in cells if d in reach[c] and c in reach[d]]
        r = min(cls)
        for d in cls:
            root[d] = r
    return root


def num_scc(field, max_step):
    """The number of strongly-connected (mutual-reachability) components — the directed analog of β₀. Always
    <= warden.betti0; equal on terrain without a bridging directed cycle (see the module's honest scope)."""
    return len(set(scc(field, max_step).values()))


def reach_asymmetry(field, max_step):
    """The count of ORDERED pairs (a, b), a != b, with `a -> b` reachable but NOT `b -> a` — the live measure
    of one-way structure. 0 exactly when reachability is symmetric (flat, or a symmetric wall); positive on a
    one-way cliff. This is the non-vacuity number the directed refinement rests on."""
    cells, reach = _all_reach(field, max_step)
    n = 0
    for a in cells:
        ra = reach[a]
        for b in ra:
            if b != a and a not in reach[b]:
                n += 1
    return n


def mutually_reachable(field, a, b, max_step):
    """True iff `a` and `b` are in the same SCC (each can reach the other)."""
    return can_reach(field, a, b, max_step) and can_reach(field, b, a, max_step)


def admit_move(field, anchor, claim, max_step):
    """ADMIT iff `claim` is reachable FROM `anchor` by a directed path. Else `WARD-ONEWAY` when only the
    REVERSE path exists (a one-way cliff asserted backward — the case the undirected warden conflates with a
    wall), or `WARD-UNREACH` when there is no directed path either way (a genuine wall). Pure."""
    if not can_reach(field, anchor, claim, max_step):
        if can_reach(field, claim, anchor, max_step):
            raise _W.WardError("WARD-ONEWAY", f"{claim} is reachable from {anchor} only in reverse — a one-way climb")
        raise _W.WardError("WARD-UNREACH", f"no directed path between {anchor} and {claim}")
    return "WARD-OK"


def dirward_digest(name, field, max_step, verdict):
    """The URDRWARD3 canon — SHA-256(MAGIC | name | nscc | asym | verdict). Binds the directed component count
    AND the reachability asymmetry, so a changed cliff (a new one-way edge) or a changed verdict moves it."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|nscc:{num_scc(field, max_step)}|asym:{reach_asymmetry(field, max_step)}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
# A one-way world: west plateau (x < 8) at height 100, east plain (x >= 8) at height 0. With MAX_STEP = 40 the
# boundary is a one-way drop — plateau -> plain descends (legal), plain -> plateau climbs a wall (illegal), so
# reach is asymmetric. `_wall_field` is a genuine full barrier (height 500 column): no directed path either
# way, the WARD-UNREACH case the undirected warden cannot tell apart from the cliff.
_MS = 40
_TOP, _BOTTOM = (5, 8), (9, 8)                                   # a plateau cell; a plain cell


def _cliff_field():
    return tuple(tuple(100 if x < 8 else 0 for x in range(16)) for _y in range(16))


def _wall_field():
    return tuple(tuple(500 if x == 8 else 0 for x in range(16)) for _y in range(16))


def honest_descent():
    """An actor descends the cliff top -> bottom -> ADMIT (a legal move the undirected warden false-refuses)."""
    fld = _cliff_field()
    return "honest_descent", fld, admit_move(fld, _TOP, _BOTTOM, _MS)


def climb_back():
    """A bare claim to be back on the plateau, asserted from the plain -> refused WARD-ONEWAY (distinct from
    the wall's WARD-UNREACH; the undirected warden conflates the two)."""
    fld = _cliff_field()
    try:
        v = admit_move(fld, _BOTTOM, _TOP, _MS)
    except _W.WardError as exc:
        v = exc.sub
    return "climb_back", fld, v


SCENES = {"honest_descent": honest_descent, "climb_back": climb_back}


def scene_result(name):
    """Run a named directed-reachability scenario -> its URDRWARD3 digest. Same host, same bytes."""
    nm, fld, verdict = SCENES[name]()
    return dirward_digest(nm, fld, _MS, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_dirward.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise _W.WardError("WARD-MALFORMED", f"no golden named {name!r}")
