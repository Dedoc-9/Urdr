# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""stance — the MEASURED foundation of first-person movement over the terrain (T3.9): an exact,
integer, grounded walk across the certified heightfield.

`buoyancy.py` reads a raft's waterline on the wavefield; `crossing.py` reads a moving agent through
the wavefield. This is their solid-ground sibling: a first-person actor STANDS and WALKS on the
`heightfield.py` (URDRHF1) authority. Two exact facts, no float, no `/` `//` `%`:

  * GROUNDED — at grid cell (x, y) the actor's feet rest at the exact ground height
    `g = heights[y][x]`; its capsule spans `[g, g + PLAYER_HEIGHT]`. Standing IS reading the field.
  * STEP GATE — a cardinal step from cell A to the adjacent cell B is TRAVERSABLE iff the climb
    `heights[B] - heights[A] <= MAX_STEP`. This is the integer collapse of a character controller's
    two knobs (step-offset = max climbable rise, slope-limit = max walkable angle): on a unit grid a
    "slope" over one cell IS a rise, so both become one exact comparison. Descending is always
    traversable (you can always walk or drop downhill); a rise above `MAX_STEP` is a WALL.

The declared walk is a start cell plus a string of cardinal moves (N/S/E/W). The measured event,
exactly like `crossing`'s first-overtop tick, is the FIRST step BLOCKED by an unclimbable rise:

    result = the first step index i in [0, len(moves)) whose rise exceeds MAX_STEP,
             else len(moves)  (== the whole declared path was walked)

`MAX_STEP` is load-bearing: a wall of rise `MAX_STEP` is walked, a wall of `MAX_STEP + 1` blocks —
two scenes share a path and differ only in `MAX_STEP`, pinning that the gate is the terrain, not the
model. Everything is exact integers over the frozen heightfield, so `result` and the ground profile
reproduce bit-for-bit on every host; cross-placement is a clean next step (asserted division-free).

D7-D10 SEAM (why this is the foundation, not the finish). The walked path is a STATE TRAJECTORY —
the actor's authoritative pose over time. The observer/atlas engine (`world_host` / `atlas_*`, i.e.
exact-integer Kalman observability: a state is recoverable iff its observation charts have full
column rank) certifies a *view* of that trajectory reconstructs to it, or refuses it — the moving
first-person camera as a certified observer. This module earns the trajectory; the observer that
watches it is the next slice.

GRADE. The computation is MEASURED (`result` + the ground profile are exact and reproducible; a
defect diverges). The movement MODEL — "an actor climbs a rise of at most MAX_STEP, walls otherwise"
— is DECLARED, like the buoyancy and crossing laws: the heightfield it reads is authority, the model
is declared, the reproducible walk is measured. Refusals are typed `STANCE-REFUSE` (start off the
grid, a path that leaves the grid, an unknown move, a non-positive actor, a negative step, non-int
incl. bool): refuse, never clamp the path or invent a footing."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRSTANCE1"
STEP_MAX = 4096                       # the declared-path length ceiling, a typed boundary
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import heightfield as _HF                                         # the certified authority (T1)

# Cardinal unit moves on the grid (x = column east, y = row south). No diagonals: a diagonal has no
# exact integer length, and the step gate is a per-cell rise — one cell per move keeps it exact.
DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}


class StanceError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise StanceError("STANCE-REFUSE", message)


def _is_int(v):
    return type(v) is int                                        # bool excluded on purpose


def _pair(v, what):
    if not (isinstance(v, tuple) and len(v) == 2 and _is_int(v[0]) and _is_int(v[1])):
        _refuse(f"{what} must be an integer (x, y), got {v!r}")
    return v


def _grid_dims(heights):
    """(w, h) of a rectangular height grid — refuse a ragged or empty grid (not a field)."""
    if not (isinstance(heights, tuple) and heights and isinstance(heights[0], tuple) and heights[0]):
        _refuse("heights must be a non-empty tuple of non-empty rows")
    h = len(heights)
    w = len(heights[0])
    for row in heights:
        if not (isinstance(row, tuple) and len(row) == w):
            _refuse("heights rows must all be the same width (a rectangular field)")
    return w, h


def check_walk(heights, start, moves, max_step, player_height):
    """Membership in the stance domain — every violation is a typed `STANCE-REFUSE`. Crucially the
    WHOLE declared path must stay on the grid for its length (refuse, never clamp), so the only event
    the walk reports is the terrain blocking — never an out-of-bounds read faked as a footing."""
    w, h = _grid_dims(heights)
    x0, y0 = _pair(start, "start")
    if not (isinstance(moves, str) and 1 <= len(moves) <= STEP_MAX):
        _refuse(f"moves must be a str of 1..{STEP_MAX} cardinal steps, got {moves!r}")
    if not _is_int(max_step) or max_step < 0:
        _refuse(f"max_step must be a non-negative int, got {max_step!r}")
    if not _is_int(player_height) or player_height <= 0:
        _refuse(f"player_height must be a positive int, got {player_height!r}")
    if not (0 <= x0 < w and 0 <= y0 < h):
        _refuse(f"start {start!r} is off the {w}x{h} grid")
    x, y = x0, y0
    for i, m in enumerate(moves):
        if m not in DIRS:
            _refuse(f"move {i} is {m!r}, not one of {''.join(sorted(DIRS))}")
        dx, dy = DIRS[m]
        x += dx
        y += dy
        if not (0 <= x < w and 0 <= y < h):
            _refuse(f"path leaves the {w}x{h} grid at move {i}: cell ({x}, {y})")


def _profile(heights, start, moves):
    """The exact ground-height sequence along the (pre-validated, in-grid) path: the footing at the
    start cell, then after each move. len == len(moves) + 1."""
    x, y = start
    prof = [heights[y][x]]
    for m in moves:
        dx, dy = DIRS[m]
        x += dx
        y += dy
        prof.append(heights[y][x])
    return tuple(prof)


def _first_blocked(profile, max_step, blind=False):
    """The first step whose rise exceeds `max_step` (a wall), else `len(profile) - 1` (whole path
    walked). Division-free: one subtraction and one comparison per step. `blind=True` is THE DEFECT
    — an actor that ignores the step gate and walks through walls, so it never blocks; it exists only
    to pin that the gate is load-bearing (the selftest diverges a blocked scene against it)."""
    if blind:
        return len(profile) - 1
    for i in range(len(profile) - 1):
        if profile[i + 1] - profile[i] > max_step:
            return i
    return len(profile) - 1


def walk(heights, start, moves, max_step, player_height=1, blind=False):
    """The exact step index first blocked by an unclimbable rise, or `len(moves)` if the whole
    declared path is walked. Pure integers over the frozen heightfield. `blind=True` is the
    walk-through-walls defect."""
    check_walk(heights, start, moves, max_step, player_height)
    return _first_blocked(_profile(heights, start, moves), max_step, blind)


def walk_trace(heights, start, moves, max_step, player_height=1, blind=False):
    """(result, ground-profile) — the blocking event plus the footing the digest binds."""
    check_walk(heights, start, moves, max_step, player_height)
    prof = _profile(heights, start, moves)
    return _first_blocked(prof, max_step, blind), prof


def stance_digest(name, result, profile):
    """The URDRSTANCE1 canon — SHA-256(MAGIC | name | first-blocked step | ground profile). Binds
    BOTH the blocking event and the exact footing the actor stood on along the way."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|r:{result}".encode())
    hh.update(b"|")
    hh.update(",".join(str(v) for v in profile).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
# Each names a terrain scene from heightfield.SCENES, a start cell, a cardinal path, and MAX_STEP.
def _heights(scene):
    return _HF.scene_digest(_HF.SCENES[scene]())[1]               # the certified height grid


def plain_walk():
    """A straight east stroll across the rolling `blank` canvas — every rise on the path is at most
    MAX_STEP, so the whole route is walked (result == len(moves), the 'cleared' case)."""
    return ("blank", (2, 8), "EEEEEEEEEEEE", 16, 2)


def ridge_clear():
    """A northward climb up the `mountains` ridge with MAX_STEP high enough to top every rise on the
    path — the actor walks the whole declared route (result == len(moves))."""
    return ("mountains", (6, 25), "NNNNNNNNNNNN", 40, 2)


def ridge_blocked():
    """The SAME climb as `ridge_clear` at a lower MAX_STEP — after eight cells of gentle ridge a
    21-high face now walls the actor, who stops there (result == 8 < len). MAX_STEP is load-bearing:
    the ONLY difference from ridge_clear is how tall a step the actor can take, and the terrain, not
    the model, decides where the walk ends."""
    return ("mountains", (6, 25), "NNNNNNNNNNNN", 20, 2)


SCENES = {"plain_walk": plain_walk, "ridge_clear": ridge_clear, "ridge_blocked": ridge_blocked}


def scene_result(name):
    """Run a named walk → (result, digest). Same host, same bytes."""
    scene, start, moves, max_step, ph = SCENES[name]()
    r, prof = walk_trace(_heights(scene), start, moves, max_step, ph)
    return r, stance_digest(name, r, prof)


def golden(name):
    """The pinned digest for a named scene from `conformance_stance.txt`."""
    with open(_os.path.join(_HERE, "conformance_stance.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise StanceError("STANCE-REFUSE", f"no golden named {name!r}")
