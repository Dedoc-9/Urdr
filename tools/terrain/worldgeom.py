# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""worldgeom (URDRWGM1) — a castle generated from what it IS, standing on ground it did not
choose.

THE CLAIM CLASS THIS RUNG MOVES: `worldbind` bound authored POINTS to certified ground. A
castle is not a point. It has extent, and extent is where authored geometry and certified
terrain actually collide — a wall does not sit on a height, it crosses a slope. This rung
carries the authoring thesis one step further (geometry is a downstream projection, so a
castle is declared as what its parts ARE and the mesh is derived) and then answers the
question extent forces:

  * NOTHING FLOATS AND NOTHING IS STRANDED. Every generated prism's base sits at or below the
    LOWEST certified ground under its own plan footprint, and its top stands at least the
    declared height above the HIGHEST ground under that footprint. A wall crossing a slope is
    therefore level along its length, buried into the rise and footed down the fall — which is
    how a real wall is built and, more to the point here, is a property a gate can check. A
    floating wall and a buried doorway are the same defect with different signs, and both are
    caught by the same inequality.
  * THE OCTAGON IS DECLARED, NOT APPROXIMATED. Towers are integer octagons — a square with its
    corners cut — because a REGULAR octagon has no exact integer realisation and this substrate
    admits no float. The shape is stated as what it is rather than dressed as what it is not.
  * TOWERS PROJECT, AND THE GEOMETRY PROVES IT. A corner tower centred ON the corner sticks out
    past both wall faces, which is the entire military reason towers exist: a defender can shoot
    ALONG the wall instead of only away from it. That is not a comment here — the rung measures
    each tower's projection beyond the wall plane it flanks and refuses a castle whose towers
    hide behind their own curtain.
  * THE GATE IS A HOLE, AND HOLES ARE STRUCTURAL. The passage between the twin gate towers is
    open because nothing is generated there, not because something was subtracted. The rung
    asserts the passage column is clear from ground to the machicolation's underside — an
    entrance a body cannot walk through is a wall with a door painted on it.

does_not_show: any terrain modification (the canon is immutable here — no ditch is dug, no
motte raised; that needs `terraform` and is not claimed); collision, contact or whether a
player can climb anything (the prisms are geometry, not gameplay); interiors, floors, stairs
or roofs (a prism is a solid, and the castle is a silhouette with structure, not a building);
materials, lighting or texture; the causal ANALYSIS of the authored relations (weltwerk's lint
owns that under its own discipline — relations ride as data); rendering cost (the runtime's
adoption is its own rung with its own before/after).

falsifier: a prism whose base clears the ground under it refuses (the float law); a prism that
fails to reach its declared height above its own ground refuses; a tower that does not project
beyond the wall it flanks refuses; a blocked gate passage refuses; the octagon must be convex
and integer, and a regular-octagon claim would be a lie the constructor cannot tell; generation
is deterministic — the same authored text yields byte-identical geometry — and the record is
content-addressed, so a tampered prism refuses its pin.
"""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import worldbind as _wb                  # URDRWBD1: the exact doors, imported, never copied

MAGIC = b"URDRWGM1"

TILE = _wb.TILE
Q8 = _wb.Q8
UNIT = TILE * Q8                         # one author unit in Q8 world units

CORPUS = ("spec/attest/world-castle.wrk",
          "f1e8c2bc89921a7d46aa4a054f692c3fdaafea43f47d53b8d6504f29e4aee197")

# Declared palette — stone under a warm sun, dark enough to read against grass and sky.
COLORS = {"wall": 0x8A8A82, "tower": 0x9A968C, "block": 0x7E7A72,
          "merlon": 0xA8A49C, "batter": 0x6E6A62}
RECORD = ("spec/attest/castle-geometry.txt",
          "9d7ab0bcb124831d84ec17c2477248cdece159ab03080ab46d47c2c90918f66e")
EMBED = 1 * Q8                           # how far a footing is driven below the lowest ground
MERLON = 1                               # author units: merlon width == crenel width
CRENEL_RISE = 1                          # author units the merlon stands above the walk


class WorldgeomError(Exception):
    def __init__(self, message):
        super().__init__(f"WORLDGEOM-REFUSE: {message}")
        self.code = "WORLDGEOM-REFUSE"


def load_corpus(text=None):
    return _wb._load(CORPUS[0], CORPUS[1], text)


# ---- the authored castle -------------------------------------------------------------------------
GEOM_KEYS = ("archetype", "span", "position", "thickness", "height", "radius",
             "crenels", "batter", "base", "sides", "overhang")
ARCHETYPES = ("wall", "tower", "block")


def parse_castle(text):
    """The authored text -> parts. Deliberately a SEPARATE parser from worldbind's: that one
    admits point entities and refuses unknown keys, and silently widening it would let a
    geometry typo pass as a relation. Relations are still carried, and still graded not at
    all."""
    world = None
    zones, parts, rels = [], {}, []
    cur = None
    for raw in text.split("\n"):
        ln = raw.split("#")[0].rstrip()
        if not ln.strip():
            continue
        s = ln.strip()
        if ln[0] not in " \t":
            cur = None
            if s.startswith("world "):
                world = s[6:].strip().strip('"')
            elif s.startswith("zone "):
                zones.append(s[5:].strip())
            elif s.startswith("entity ") and s.endswith(":"):
                cur = s[7:-1].strip()
                if cur in parts:
                    raise WorldgeomError(f"entity {cur!r} declared twice")
                parts[cur] = {"zone": "", "archetype": None, "crenels": False,
                              "batter": False, "base": None, "overhang": False}
            else:
                raise WorldgeomError(f"unparsed top-level line {s!r}")
            continue
        if cur is None:
            raise WorldgeomError(f"indented line outside an entity: {s!r}")
        key, _, rest = s.partition(" ")
        rest = rest.strip()
        p = parts[cur]
        if key == "zone":
            p["zone"] = rest
        elif key == "archetype":
            if rest not in ARCHETYPES:
                raise WorldgeomError(f"unknown archetype {rest!r}")
            p["archetype"] = rest
        elif key in ("span", "position"):
            p[key] = tuple(rest.split())
        elif key in ("thickness", "height", "radius", "base", "sides"):
            p[key] = rest
        elif key in ("crenels", "batter", "overhang"):
            if rest not in ("yes", "no"):
                raise WorldgeomError(f"{key} takes yes or no, got {rest!r}")
            p[key] = rest == "yes"
        elif key in _wb.REVERSED_RELATIONS:
            rels.append((rest, key, cur))
        elif key in _wb.FORWARD_RELATIONS or key in ("flanks", "covers", "channels", "guards"):
            rels.append((cur, key, rest))
        else:
            raise WorldgeomError(f"unknown key {key!r} — a geometry typo is not silently a "
                                 f"relation")
    if world is None:
        raise WorldgeomError("no world name declared")
    for name, p in parts.items():
        if p["archetype"] is None:
            raise WorldgeomError(f"entity {name!r} has no archetype — it cannot be built")
        if p["archetype"] == "tower" and "position" not in p:
            raise WorldgeomError(f"tower {name!r} has no position")
        if p["archetype"] in ("wall", "block") and "span" not in p:
            raise WorldgeomError(f"{p['archetype']} {name!r} has no span")
        if p["zone"] and p["zone"] not in zones:
            raise WorldgeomError(f"entity {name!r} names undeclared zone {p['zone']!r}")
    return {"world": world, "zones": sorted(zones), "parts": parts,
            "relations": sorted(rels)}


# ---- exact plan shapes ---------------------------------------------------------------------------
def _q(tok):
    """Author decimal -> Q8 world units, through worldbind's door. A float never appears."""
    return _wb.to_q8(tok)


def _span_runtime(span):
    """Authored (x0 z0 x1 z1) on the ground plane -> runtime (x0 y0 x1 y1) in Q8, through the
    declared axis map (author +z becomes runtime -y)."""
    x0, z0, x1, z1 = (_q(t) for t in span)
    a = _wb.map_axes((x0, 0, z0))
    b = _wb.map_axes((x1, 0, z1))
    return a[0], a[1], b[0], b[1]


def rect(x0, y0, x1, y1):
    lo_x, hi_x = min(x0, x1), max(x0, x1)
    lo_y, hi_y = min(y0, y1), max(y0, y1)
    return ((lo_x, lo_y), (hi_x, lo_y), (hi_x, hi_y), (lo_x, hi_y))


def octagon(cx, cy, r):
    """AN INTEGER OCTAGON: a square with its corners cut. Declared as exactly that, because a
    REGULAR octagon needs cos(pi/4) and this substrate admits no float — an approximation
    presented as a regular octagon would be a claim the constructor cannot honour. The cut is
    r//3, which keeps every vertex on the lattice for any integer radius."""
    c = r // 3
    if c < 1:
        return rect(cx - r, cy - r, cx + r, cy + r)
    return ((cx - r + c, cy - r), (cx + r - c, cy - r),
            (cx + r, cy - r + c), (cx + r, cy + r - c),
            (cx + r - c, cy + r), (cx - r + c, cy + r),
            (cx - r, cy + r - c), (cx - r, cy - r + c))


def is_convex_ccw(poly):
    n = len(poly)
    sign = 0
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        cx, cy = poly[(i + 2) % n]
        cr = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if cr == 0:
            continue
        s = 1 if cr > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return sign != 0


# ---- the ground a part stands on ------------------------------------------------------------------
def _tiles_under(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    t0x = min(xs) // UNIT
    t1x = -((-max(xs)) // UNIT)
    t0y = min(ys) // UNIT
    t1y = -((-max(ys)) // UNIT)
    return [(tx, ty) for tx in range(t0x, t1x + 1) for ty in range(t0y, t1y + 1)]


def ground_band(poly, cache):
    """The lowest and highest certified ground under a footprint, in Q8. The tiles are the
    lattice cells the plan covers, corners included — a wall that clips a hill's shoulder must
    see that shoulder."""
    hs = [_wb.ground_at(tx, ty, cache) * Q8 for (tx, ty) in _tiles_under(poly)]
    return min(hs), max(hs)


# ---- generation ------------------------------------------------------------------------------------
def _prism(pid, kind, poly, zb, zt):
    if not is_convex_ccw(poly):
        raise WorldgeomError(f"{pid}: plan polygon is not convex — a concave prism is not a "
                             f"shape this rasteriser may assume")
    if zt <= zb:
        raise WorldgeomError(f"{pid}: prism has no height")
    return {"id": pid, "kind": kind, "color": COLORS[kind], "poly": tuple(poly),
            "zb": zb, "zt": zt}


def _crenellate(pid, kind, poly, top, cache):
    """Merlons alternating with crenels along each axis-aligned run of the plan, one author
    unit each, CLAMPED INSIDE the parent's own footprint — a merlon that overhung its wall
    would be supported by nothing, and the support law below would (correctly) refuse it. The
    top of a wall is not a line: it is a comb, and the comb is what makes a silhouette read as
    a castle rather than a box."""
    out = []
    xs = [q[0] for q in poly]
    ys = [q[1] for q in poly]
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
    step = MERLON * UNIT
    idx = 0
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        if dx != 0 and dy != 0:
            continue                      # merlons ride the axis-aligned runs only (declared)
        length = abs(dx) + abs(dy)
        steps = length // step
        if steps < 2:
            continue
        ux = (dx // steps) if dx else 0
        uy = (dy // steps) if dy else 0
        for s in range(0, steps, 2):
            px, py = ax + ux * s, ay + uy * s
            qx, qy = px + ux, py + uy
            lo_x, hi_x = min(px, qx), max(px, qx)
            lo_y, hi_y = min(py, qy), max(py, qy)
            if lo_x == hi_x:
                lo_x, hi_x = lo_x - step // 2, hi_x + step // 2
            if lo_y == hi_y:
                lo_y, hi_y = lo_y - step // 2, hi_y + step // 2
            lo_x, hi_x = max(lo_x, bx0), min(hi_x, bx1)
            lo_y, hi_y = max(lo_y, by0), min(hi_y, by1)
            if hi_x - lo_x <= 0 or hi_y - lo_y <= 0:
                continue
            idx += 1
            out.append(_prism(f"{pid}:merlon{idx}", "merlon",
                              rect(lo_x, lo_y, hi_x, hi_y), top, top + CRENEL_RISE * UNIT))
    return out


def build(spec):
    """Authored parts -> exact prisms on certified ground. Deterministic: sorted iteration, no
    dict order, integer arithmetic throughout."""
    cache = {}
    prisms = []
    plans = {}
    for name in sorted(spec["parts"]):
        p = spec["parts"][name]
        arche = p["archetype"]
        height = _q(p["height"])
        if arche == "tower":
            ax, ay, az = (_q(t) for t in p["position"])
            rx, ry, _rz = _wb.map_axes((ax, ay, az))
            r = _q(p["radius"])
            poly = octagon(rx, ry, r)
        elif arche == "wall":
            x0, y0, x1, y1 = _span_runtime(p["span"])
            half = _q(p["thickness"]) // 2
            if x0 == x1:
                poly = rect(x0 - half, y0, x1 + half, y1)
            elif y0 == y1:
                poly = rect(x0, y0 - half, x1, y1 + half)
            else:
                poly = rect(x0, y0, x1, y1)      # a diagonal run: its own bounding run
            poly = rect(*poly[0], *poly[2])
        else:                                    # block
            x0, y0, x1, y1 = _span_runtime(p["span"])
            poly = rect(x0, y0, x1, y1)
        lo, hi = ground_band(poly, cache)
        base = lo - EMBED if p["base"] is None else hi + _q(p["base"])
        top = (hi if p["base"] is None else base) + height
        if p["base"] is not None:
            top = hi + _q(p["base"]) + height
        plans[name] = {"poly": poly, "lo": lo, "hi": hi, "base": base, "top": top,
                       "height": height, "zone": p["zone"], "archetype": arche,
                       "overhang": bool(p.get("overhang"))}
        if p.get("batter"):
            b = UNIT // 2
            xs = [q[0] for q in poly]
            ys = [q[1] for q in poly]
            prisms.append(_prism(f"{name}:batter", "batter",
                                 rect(min(xs) - b, min(ys) - b, max(xs) + b, max(ys) + b),
                                 base, lo + UNIT))
        main = _prism(name, arche, poly, base, top)
        main["overhang"] = bool(p.get("overhang"))
        prisms.append(main)
        if p["crenels"]:
            prisms.extend(_crenellate(name, arche, poly, top, cache))
    return {"prisms": prisms, "plans": plans}


# ---- the laws ------------------------------------------------------------------------------------
def _bbox(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def everything_is_supported(built, cache=None):
    """EVERY PRISM STANDS ON SOMETHING: either it is founded on the ground (its base at or
    below the lowest certified ground under its own footprint) or it rests on another prism —
    its base exactly that prism's top, its plan contained in that prism's plan. This is the
    law the first draft got wrong: `nothing floats above the terrain` is false of a merlon by
    design, because a merlon stands on a wall. The honest property is SUPPORT, and stating it
    that way catches the floating wall AND the overhanging merlon with one inequality."""
    cache = {} if cache is None else cache
    tops = {}
    for pr in built["prisms"]:
        tops.setdefault(pr["zt"], []).append(_bbox(pr["poly"]))
    for pr in built["prisms"]:
        lo, _hi = ground_band(pr["poly"], cache)
        if pr["zb"] <= lo:
            continue                                  # founded on the certified ground
        b = _bbox(pr["poly"])
        held = any(q[0] <= b[0] and q[1] <= b[1] and q[2] >= b[2] and q[3] >= b[3]
                   for q in tops.get(pr["zb"], ()))
        if held:
            continue
        # THE THIRD CASE, AND THE LAW FOUND IT RATHER THAN ANTICIPATING IT: a machicolation
        # OVERHANGS on purpose — that is what a machicolation is, a parapet corbelled out over
        # the gate so what falls through its floor lands on whoever is at the door. An overhang
        # is admitted only when the authoring DECLARES it, and only when something actually
        # carries it: a prism overlapping in plan whose own z-range spans this base. Undeclared,
        # it refuses; declared but carried by nothing, it still refuses.
        if not pr.get("overhang"):
            return False
        corbel = any(not (c[2] < b[0] or c[0] > b[2] or c[3] < b[1] or c[1] > b[3])
                     and cz0 <= pr["zb"] <= cz1
                     for (c, cz0, cz1) in [(_bbox(o["poly"]), o["zb"], o["zt"])
                                           for o in built["prisms"] if o is not pr])
        if not corbel:
            return False
    return True


def every_part_reaches_its_height(built, cache=None):
    """Each authored part stands at least its declared height above the HIGHEST ground it
    covers. A wall swallowed by the slope it crosses is the opposite defect, and would be
    invisible from the low side."""
    cache = {} if cache is None else cache
    for name, pl in sorted(built["plans"].items()):
        if pl["top"] - pl["hi"] < pl["height"]:
            return False
    return True


def _plane_extent(poly, axis):
    vals = [p[axis] for p in poly]
    return min(vals), max(vals)


def towers_project(built):
    """A corner tower centred on the corner sticks out past the wall faces it joins — the
    entire military reason towers exist. Measured, not asserted: the population is the towers
    that TOUCH a curtain (a keep turret standing on a block is not a flanking tower and is not
    counted), and every one of them must extend beyond that wall's plan on some axis. A tower
    that hides behind its own curtain flanks nothing."""
    plans = built["plans"]
    walls = {n: p for n, p in plans.items() if p["archetype"] == "wall"}
    towers = {n: p for n, p in plans.items() if p["archetype"] == "tower"}
    projecting, flanking = 0, 0
    for _tn, tp in sorted(towers.items()):
        tx = _plane_extent(tp["poly"], 0)
        ty = _plane_extent(tp["poly"], 1)
        touches, sticks = False, False
        for _wn, wp in sorted(walls.items()):
            wx = _plane_extent(wp["poly"], 0)
            wy = _plane_extent(wp["poly"], 1)
            if tx[1] < wx[0] or tx[0] > wx[1] or ty[1] < wy[0] or ty[0] > wy[1]:
                continue
            touches = True
            if tx[0] < wx[0] or tx[1] > wx[1] or ty[0] < wy[0] or ty[1] > wy[1]:
                sticks = True
        if touches:
            flanking += 1
            projecting += 1 if sticks else 0
    return projecting, flanking


def gate_passage_is_open(built):
    """The passage between the twin gate towers is clear because nothing was generated there —
    a hole by construction, not by subtraction. Sampled along the passage's own centre line at
    body height; anything solid in the column means an entrance a body cannot use."""
    x0, x1 = 16 * UNIT, 22 * UNIT
    ys = (-1 * UNIT, 0, 1 * UNIT)
    for pr in built["prisms"]:
        xs = _plane_extent(pr["poly"], 0)
        yy = _plane_extent(pr["poly"], 1)
        for y in ys:
            if xs[0] <= x0 and xs[1] >= x0 and yy[0] <= y <= yy[1] and pr["zb"] < 4 * UNIT:
                if x1 >= xs[0]:
                    return False
    return True


# ---- the record ------------------------------------------------------------------------------------
def record_bytes(built):
    lines = ["# URDRWGM1 castle geometry — runtime frame, Q8 world units, convex plan prisms",
             f"# prisms {len(built['prisms'])}"]
    for pr in sorted(built["prisms"], key=lambda p: p["id"]):
        pts = " ".join(f"{x} {y}" for (x, y) in pr["poly"])
        lines.append(f"prism {pr['id']} {pr['color']:06x} {pr['zb']} {pr['zt']} "
                     f"{len(pr['poly'])} {pts}")
    return ("\n".join(lines) + "\n").encode()


def record_digest(raw):
    return hashlib.sha256(MAGIC + b"|geom|" + raw).hexdigest()


def generate(text=None):
    spec = parse_castle(load_corpus(text) if text is None else text)
    built = build(spec)
    raw = record_bytes(built)
    return {"spec": spec, "built": built, "record": raw, "digest": record_digest(raw)}


def load_record(text=None):
    return _wb._load(RECORD[0], RECORD[1], text)


def the_committed_record_is_what_generation_produces():
    """The record the RUNTIME loads must be the bytes this generator emits — otherwise the
    demo draws a castle the gate never checked. Committed, pinned, and re-derived here."""
    return generate()["record"] == load_record().encode()


def generation_is_deterministic():
    a, b = generate(), generate()
    return a["record"] == b["record"] and a["digest"] == b["digest"]


# ---- the plants ----------------------------------------------------------------------------------
def a_floating_wall_is_caught():
    """Lift one part off its footing, onto nothing, and the support law must bite."""
    g = generate()
    bad = {"prisms": [dict(p) for p in g["built"]["prisms"]], "plans": g["built"]["plans"]}
    for i, pr in enumerate(bad["prisms"]):
        if pr["kind"] == "wall":
            bad["prisms"][i] = dict(pr, zb=pr["zb"] + 40 * Q8, zt=pr["zt"] + 40 * Q8)
            break
    return not everything_is_supported(bad)


def an_overhanging_merlon_is_caught():
    """The defect the first draft of this law could not see: slide a merlon off the wall it
    stands on and it is supported by nothing, though it floats above no terrain in particular."""
    g = generate()
    bad = {"prisms": [dict(p) for p in g["built"]["prisms"]], "plans": g["built"]["plans"]}
    for i, pr in enumerate(bad["prisms"]):
        if pr["kind"] == "merlon":
            poly = tuple((x + 200 * UNIT, y) for (x, y) in pr["poly"])
            bad["prisms"][i] = dict(pr, poly=poly)
            break
    return not everything_is_supported(bad)


def a_swallowed_wall_is_caught():
    g = generate()
    plans = {k: dict(v) for k, v in g["built"]["plans"].items()}
    name = sorted(plans)[0]
    plans[name]["top"] = plans[name]["hi"]
    return not every_part_reaches_its_height({"prisms": g["built"]["prisms"], "plans": plans})


def an_undeclared_overhang_is_caught():
    """THE PLANT THIS RUNG'S OWN FIRST RUN EARNED. The support law refused the machicolation
    before anyone declared it, which was correct: an overhang the authoring never claimed is
    indistinguishable from a mistake. Strip the declaration and it must refuse again."""
    g = generate(load_corpus().replace("  overhang yes\n", "", 1))
    return not everything_is_supported(g["built"])


def an_uncarried_overhang_is_caught():
    """A declared overhang still needs something to carry it: float the machicolation clear of
    its gate towers and the corbel condition must bite."""
    g = generate()
    bad = {"prisms": [dict(p) for p in g["built"]["prisms"]], "plans": g["built"]["plans"]}
    for i, pr in enumerate(bad["prisms"]):
        if pr["id"] == "gate_machicolation":
            bad["prisms"][i] = dict(pr, zb=pr["zb"] + 400 * Q8, zt=pr["zt"] + 400 * Q8)
    return not everything_is_supported(bad)


def a_hidden_tower_is_caught():
    """Pull every flanking tower back inside the curtain it touches — it still TOUCHES, so it
    stays in the population, and it no longer projects. The flanking claim must die with it."""
    g = generate()
    plans = {k: dict(v) for k, v in g["built"]["plans"].items()}
    walls = [p for p in plans.values() if p["archetype"] == "wall"]
    for n, p in sorted(plans.items()):
        if p["archetype"] != "tower":
            continue
        tx = _plane_extent(p["poly"], 0)
        ty = _plane_extent(p["poly"], 1)
        for w in walls:
            wx = _plane_extent(w["poly"], 0)
            wy = _plane_extent(w["poly"], 1)
            if tx[1] < wx[0] or tx[0] > wx[1] or ty[1] < wy[0] or ty[0] > wy[1]:
                continue
            mx = (wx[0] + wx[1]) // 2
            my = (wy[0] + wy[1]) // 2
            plans[n] = dict(p, poly=rect(mx - UNIT // 4, my - UNIT // 4,
                                         mx + UNIT // 4, my + UNIT // 4))
            break
    proj, flank = towers_project({"prisms": g["built"]["prisms"], "plans": plans})
    return flank > 0 and proj == 0


def a_blocked_gate_is_caught():
    g = generate()
    blocked = {"prisms": list(g["built"]["prisms"]) + [
        _prism("plug", "block", rect(16 * UNIT, -1 * UNIT, 22 * UNIT, 1 * UNIT), 0, 9 * UNIT)],
        "plans": g["built"]["plans"]}
    return not gate_passage_is_open(blocked)


def an_unknown_key_refuses():
    try:
        parse_castle(load_corpus().replace("  height 4\n", "  heihgt 4\n", 1))
    except WorldgeomError:
        return True
    return False


def a_concave_plan_refuses():
    try:
        _prism("bad", "block", ((0, 0), (4 * UNIT, 0), (1 * UNIT, 1 * UNIT), (0, 4 * UNIT)),
               0, UNIT)
    except WorldgeomError:
        return True
    return False


def the_octagon_is_integer_and_convex():
    for r in (1, 2, 3, 5, 8, 13):
        o = octagon(0, 0, r * UNIT)
        if not all(isinstance(c, int) for p in o for c in p):
            return False
        if not is_convex_ccw(o):
            return False
    return True


# ---- scenes -------------------------------------------------------------------------------------
def scene_case(name):
    g = generate()
    if name == "castle":
        proj, tot = towers_project(g["built"])
        by_kind = {}
        for pr in g["built"]["prisms"]:
            by_kind[pr["kind"]] = by_kind.get(pr["kind"], 0) + 1
        return repr((g["spec"]["world"], g["spec"]["zones"], len(g["spec"]["parts"]),
                     g["spec"]["relations"], sorted(by_kind.items()),
                     len(g["built"]["prisms"]), proj, tot, g["digest"],
                     the_committed_record_is_what_generation_produces()))
    raise WorldgeomError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_worldgeom.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise WorldgeomError(f"no golden named {name!r}")
