# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""tierview — VISUAL ASYMMETRY, ZERO BY CONSTRUCTION (URDRTIR1): slice S6 of the city-replica arc.
NO NEW GLYPH.

THE PROBLEM, AND WHY THE OBVIOUS MEASUREMENT IS THE WRONG ONE. Clients render at different quality
tiers. A handed-down framework proposed bounding the asymmetry by per-pixel LUMINANCE DELTA. That is
the wrong quantity in BOTH directions, and each failure is easy to construct:

  * LARGE luminance delta, ZERO asymmetry — two tiers with different fog colour differ on every
    pixel, and neither can resolve anything the other cannot.
  * TINY luminance delta, TOTAL asymmetry — one tier draws foliage that hides a silhouette and the
    other culls it. A handful of pixels differ. One client can shoot someone the other cannot see.

Information asymmetry is a question about WHAT IS RESOLVABLE, never about pixel values. So the defect
is a SET DIFFERENCE over lattice cells — `|Vis_high XOR Vis_low|`, an exact integer — and not a
float delta over a framebuffer.

THE RESOLUTION, which is stronger than a bound. C2 already says authority lives in the integer lattice
and the splat is a skin. Applied to visibility rather than to collision, that says: BOTH TIERS QUERY
ONE AUTHORITATIVE PREDICATE OVER THE LATTICE. Then the asymmetry defect is not bounded — it is ZERO,
by construction, because there is only one answer to be had. `visible` takes no tier argument at all,
which makes the decoupling STRUCTURAL rather than a discipline someone has to maintain; the same shape
`horn._honest_band` uses, and checked the same way, by signature.

The consequence is that S6 stops being a measurement problem and becomes an ENFORCEMENT problem, with
a one-line falsifier: find any authority path that reads the render. `_visible_by_tier` is that path,
kept as a plant. MEASURED, it hands a high-tier client cells a low-tier client cannot resolve, which
in a competitive shooter is the difference between seeing an opponent and not.

AND IT MUST REFUSE, NOT WARN. The handed-down framework logged an exceeded asymmetry bound as a
warning and admitted the content anyway ("visual asymmetry is a warning, not a refusal"). For a
competitive shooter that is the one place refusal is mandatory: a tier pair that resolves different
cells is not a cosmetic difference, it is an unequal game. `adjudicate_pair` refuses.

THE VISIBILITY PREDICATE ITSELF is deliberately the arc's existing shape rather than a new one:
integer supercover along the ray from observer to target, refused if any lattice cell on the way is
occupied. Exact integers, no floats, no tolerance — the same discipline `hitbox._on_ray` uses. This
module does not re-derive `perception` (URDRPCP1); it composes the same idea at lattice granularity so
the defect has a codomain to live in.

GRADE. MEASURED: the zero defect over every observer/target pair on the pinned lattices; the plant's
exact asymmetry; the structural absence of a tier parameter; determinism. DECLARED: the tier model is
a culling fraction over occupancy — a bounded model, decided completely within its bounds; richer
tier semantics (shadow detail, LOD geometry swaps) are NOT claimed, though the argument is unchanged
for any of them, because the argument is about WHO ANSWERS rather than about how the answer looks.
does_not_show: audio asymmetry (the same argument applies and is not made here); frame timing;
anything about what the client CHOOSES to draw once the server has answered — the claim is that the
authoritative answer is tier-independent, not that two screens look alike; cross-placement."""
import hashlib
import inspect as _inspect
import os as _os
import sys as _sys
from itertools import product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRTIR1"
GRID = 6                                       # lattice extent the census is decided over
TIERS = ("low", "medium", "high")
_CULL = {"low": 3, "medium": 2, "high": 1}     # the plant's tier model: keep 1 cell in N

R_ADMIT = 0
R_ASYMMETRIC = 1
_REASON_NAME = {R_ADMIT: "ADMIT", R_ASYMMETRIC: "TIERVIEW-ASYMMETRIC"}


class TierviewError(Exception):
    def __init__(self, message):
        super().__init__(f"TIERVIEW-REFUSE: {message}")
        self.code = "TIERVIEW-REFUSE"


# ---- the authoritative predicate: note the absence of a tier argument ------------------------
def _steps(ax, ay, bx, by):
    """Integer supercover from a to b — every lattice cell the segment touches. No floats."""
    dx, dy = abs(bx - ax), abs(by - ay)
    sx, sy = (1 if bx > ax else -1), (1 if by > ay else -1)
    err = dx - dy
    x, y = ax, ay
    out = [(x, y)]
    while (x, y) != (bx, by):
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x += sx
        elif e2 < dx:
            err += dx; y += sy
        else:
            err -= dy; err += dx; x += sx; y += sy
        out.append((x, y))
    return out


def visible(observer, target, occupied):
    """THE AUTHORITATIVE PREDICATE. It takes no tier and cannot take one — that is the whole content
    of S6. Exact integer supercover; a target is resolvable iff no occupied cell lies strictly
    between observer and target."""
    for c in (observer, target):
        if type(c) is not tuple or len(c) != 2 or not all(type(v) is int for v in c):
            raise TierviewError(f"coordinates must be integer pairs, got {c!r}")
    path = _steps(observer[0], observer[1], target[0], target[1])
    return not any(p in occupied for p in path[1:-1])


def _visible_by_tier(observer, target, occupied, tier):
    """A FALSIFIER TOOL (not the law): a predicate that reads the RENDER. Lower tiers cull occluders,
    so a low-tier client resolves targets a high-tier client cannot — cover that exists for one
    player and not the other. This is the authority path that must not exist."""
    if tier not in _CULL:
        raise TierviewError(f"unknown tier {tier!r}")
    keep = _CULL[tier]
    thinned = {c for i, c in enumerate(sorted(occupied)) if i % keep == 0}
    path = _steps(observer[0], observer[1], target[0], target[1])
    return not any(p in thinned for p in path[1:-1])


# ---- the defect -------------------------------------------------------------------------------
def resolvable(observer, occupied, grid=GRID, _pred=None, tier=None):
    """The SET of cells in which an opponent is resolvable from `observer`. The codomain of the
    defect: integer cells, not pixels."""
    cells = [(x, y) for x, y in _prod(range(grid), repeat=2) if (x, y) != observer]
    if _pred is None:
        return frozenset(c for c in cells if visible(observer, c, occupied))
    return frozenset(c for c in cells if _pred(observer, c, occupied, tier))


def asymmetry(observer, occupied, t1, t2, grid=GRID, _pred=None):
    """THE DEFECT: |Vis_t1 XOR Vis_t2|, an exact integer count of cells one tier resolves and the
    other does not. Zero on the authoritative path because the tier never reaches the predicate."""
    a = resolvable(observer, occupied, grid, _pred, t1)
    b = resolvable(observer, occupied, grid, _pred, t2)
    return len(a ^ b)


def walls(grid=GRID):
    """Two pinned occupancy sets — a straight wall and an L — fixed, never sampled."""
    straight = frozenset((grid // 2, y) for y in range(1, grid - 1))
    ell = straight | frozenset((x, grid // 2) for x in range(1, grid - 1))
    return (straight, ell)


def census(grid=GRID, _pred=None):
    """EXHAUSTIVE over every observer on every pinned wall and every ordered tier pair. Returns the
    total defect in cells — the one number S6 is about."""
    total = 0
    for occ in walls(grid):
        for obs in _prod(range(grid), repeat=2):
            if obs in occ:
                continue
            for t1, t2 in _prod(TIERS, repeat=2):
                if t1 < t2:
                    total += asymmetry(obs, occ, t1, t2, grid, _pred)
    return total


def defect_is_zero(grid=GRID):
    """THE LAW: on the authoritative path the asymmetry is ZERO, not bounded. Decided, not sampled."""
    return census(grid) == 0


def plant_defect(grid=GRID):
    """MEASURED: what a tier-reading authority path actually costs, in cells."""
    return census(grid, _pred=_visible_by_tier)


def decoupling_is_structural():
    """THE STRONGEST FORM of the claim: the tier cannot reach the predicate through ANY argument,
    because `visible` has none. A signature, not a promise — the same shape `horn` uses."""
    return list(_inspect.signature(visible).parameters) == ["observer", "target", "occupied"]


def adjudicate_pair(observer, occupied, t1, t2, grid=GRID, _pred=None):
    """AND IT REFUSES. A tier pair that resolves different cells is not a cosmetic difference, it is
    an unequal game, so the verdict is a refusal rather than the warning a handed-down framework
    proposed. Returns (reason, defect)."""
    d = asymmetry(observer, occupied, t1, t2, grid, _pred)
    return (R_ADMIT if d == 0 else R_ASYMMETRIC), d


def luminance_delta_is_the_wrong_quantity():
    """The construction that refutes the handed-down measure, in both directions at once. Returns
    (large_delta_zero_asymmetry, small_delta_large_asymmetry) as (delta, defect) pairs — the first
    must have a big delta and zero defect, the second a small delta and a positive defect."""
    grid, occ = GRID, walls()[0]
    obs = (0, 0)
    # (a) a uniform tint shifts every pixel and resolves nothing differently
    tint_delta = grid * grid                     # every pixel differs
    tint_defect = asymmetry(obs, occ, "low", "high", grid)
    # (b) culling one occluder cell changes few pixels and flips real visibility
    thin = frozenset(sorted(occ)[1:])
    cull_delta = len(occ ^ thin)                 # one cell's worth of pixels
    cull_defect = len(resolvable(obs, occ, grid) ^ resolvable(obs, thin, grid))
    return (tint_delta, tint_defect), (cull_delta, cull_defect)


# ---- digests + scenes -------------------------------------------------------------------------
def tv_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_zero():
    return tv_digest("zero", f"{census()}:{defect_is_zero()}:{decoupling_is_structural()}")


def _scene_plant():
    return tv_digest("plant", f"{plant_defect()}:"
                              f"{adjudicate_pair((0,0), walls()[0], 'low', 'high', GRID, _visible_by_tier)}")


def _scene_wrong_quantity():
    return tv_digest("wrong_quantity", f"{luminance_delta_is_the_wrong_quantity()}")


_SCENES = {"zero": _scene_zero, "plant": _scene_plant, "wrong_quantity": _scene_wrong_quantity}
SCENES = ("zero", "plant", "wrong_quantity")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_tierview.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise TierviewError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"authoritative defect {census()} (zero {defect_is_zero()}) | "
          f"tier-reading plant {plant_defect()} cells")
    print(f"structural decoupling {decoupling_is_structural()} | "
          f"luminance refutation {luminance_delta_is_the_wrong_quantity()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
