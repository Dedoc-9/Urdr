# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""glide — continuous fixed-point movement over the certified terrain (T3.18, MMO Stage B opener):
the sub-cell REFINEMENT of `drive`. Where `drive` folds an input log into whole-cell integer poses,
`glide` folds the SAME log into Q32.32 sub-cell poses — the actor glides between cells instead of
snapping — and does it division-free.

The regime is fixed-point (radix ONE = 2^32, the FIELDFP substrate). Movement is a fixed subdivision
`sub` ∈ {1,2,4,8,16} of a cell: one micro-step advances `ONE >> k` (an EXACT shift, sub = 2^k), so
`sub` micro-steps sum to EXACTLY one cell — no rounding, no `/` `//` `%`. Position floors to a cell by
`fx >> 32`; the ground under the actor is the EXACT floor-sampled cell height `heights[fy>>32][fx>>32]`
(the nearest lower-left cell). A micro-step that would cross into a cell that is off-grid or a rise above
MAX_STEP is refused — the actor stops at the sub-cell boundary, the continuous echo of `drive`'s wall.

THE KEYSTONE (measured): the REFINEMENT BRIDGE. `glide`'s command-boundary poses, floored to cells,
reproduce `drive`'s certified discrete trajectory BIT-FOR-BIT — for every input log and every
subdivision. The continuous regime provably CONTAINS the discrete one (drive ⊑ glide): every certified
fact about the grid transcript is inherited, and the sub-cell poses are the strictly-finer resolution
between them. At sub = 1 glide IS drive lifted to fixed-point (floors to the identical path); at sub =
2^k it interpolates k levels finer without ever leaving a cell drive did not visit.

Two exact facts, bit-reproducible on every host (as `drive`):
  * DETERMINISM — replaying (start, log, sub) reproduces the fixed-point trajectory bit-for-bit.
  * TAMPER-EVIDENCE — the digest binds (start, log, sub, trajectory); a forged / replayed / reordered
    command, or a changed subdivision, moves the digest.

GRADE. The fixed-point trajectory, its determinism, its tamper-evidence, and the refinement bridge
(glide ⊒ drive, exact) are MEASURED (exact, reproducible, a defect diverges). The movement MODEL
(constant sub-cell speed, turn-then-advance, floor-sampled ground, a rise > MAX_STEP walls) is DECLARED,
like drive/stance. `does_not_show`: SMOOTH height interpolation (bilinear over the four corner cells —
the DECLARED presentation regime; the floor-sample is the measured authority here), CONTINUOUS facing
(mouse-look is the Q32.32 `fpquat`/`fpface` rotation, not this discrete turn), sub-cell START poses
(the actor begins cell-aligned), continuous PREDICTION reconcile (glide ∘ predict is the next slice),
and diagonal movement. Refusals are typed `GLIDE-REFUSE` (unknown command, empty log, off-grid start,
bad subdivision, negative step, non-int): refuse, never clamp the path or invent a footing."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRGLIDE1"
LOG_MAX = 4096
GAIT = {"walk": 1, "sprint": 2}
SUBDIV = (1, 2, 4, 8, 16)                                         # frozen: sub = 2^k, an exact shift
_FACE = {"N": 0, "E": 1, "S": 2, "W": 3}                         # identical to drive._FACE (asserted)
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PHYS = _os.path.join(_os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import stance as _ST                                              # the step law + DIRS (T3.9)
import heightfield as _HF                                         # the certified authority (T1)
from field import ONE                                            # the FROZEN Q32.32 radix (FIELDFP)


class GlideError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise GlideError("GLIDE-REFUSE", message)


def _is_int(v):
    return type(v) is int                                        # bool excluded on purpose


def _parse(cmd):
    """A command char → (direction 'N/S/E/W', gait 'walk'|'sprint'). UPPERCASE = sprint, lower = walk."""
    if not (isinstance(cmd, str) and len(cmd) == 1 and cmd.upper() in _FACE):
        _refuse(f"command {cmd!r} is not one of N/S/E/W (upper=sprint, lower=walk)")
    return cmd.upper(), ("sprint" if cmd.isupper() else "walk")


def _shift(sub):
    """sub → k with sub == 2^k, refusing any subdivision not in the frozen SUBDIV set. The micro-step
    is `ONE >> k`, so it is EXACT (a shift) and `sub` of them sum to exactly one cell."""
    if sub not in SUBDIV:
        _refuse(f"subdivision {sub!r} is not one of {SUBDIV} (must be a frozen power of two)")
    return sub.bit_length() - 1


def _grid_dims(heights):
    if not (isinstance(heights, tuple) and heights and isinstance(heights[0], tuple) and heights[0]):
        _refuse("heights must be a non-empty tuple of non-empty rows")
    w = len(heights[0])
    for row in heights:
        if not (isinstance(row, tuple) and len(row) == w):
            _refuse("heights rows must all be the same width (a rectangular field)")
    return w, len(heights)


def check_log(heights, start, cmds, max_step, sub):
    """Membership in the glide domain — every violation a typed `GLIDE-REFUSE`. Inputs only (not
    pre-walked): the actor may legitimately be stopped by the terrain mid-log."""
    w, h = _grid_dims(heights)
    if not (isinstance(start, tuple) and len(start) == 2 and _is_int(start[0]) and _is_int(start[1])):
        _refuse(f"start must be an integer cell (x, y), got {start!r}")
    if not (isinstance(cmds, str) and 1 <= len(cmds) <= LOG_MAX):
        _refuse(f"input log must be a str of 1..{LOG_MAX} commands, got {cmds!r}")
    if not _is_int(max_step) or max_step < 0:
        _refuse(f"max_step must be a non-negative int, got {max_step!r}")
    _shift(sub)                                                  # raises on a bad subdivision
    if not (0 <= start[0] < w and 0 <= start[1] < h):
        _refuse(f"start {start!r} is off the {w}x{h} grid")
    for c in cmds:
        _parse(c)                                               # raises GLIDE-REFUSE on an unknown token


def cell_of(fx, fy):
    """The integer cell a Q32.32 position floors to (nearest lower-left cell). Division-free: `>> 32`."""
    return fx >> 32, fy >> 32


def _fold_from(heights, fx, fy, facing, cmds, max_step, sub):
    """The pose-start fold CORE: fold `cmds` from an arbitrary Q32.32 pose `(fx, fy, facing)`. The
    current cell is re-derived `cx = fx >> 32` (the fold's INVARIANT: `cx == fx >> 32` always, because a
    micro-step updates `cx` iff the floor changes) — so a mid-trajectory boundary pose fully determines
    the future, which is what makes a glide RESUMABLE (`splice`). Returns (micro, cells): `micro` is
    every micro-step pose, `cells` one pose per command boundary (len == len(cmds) + 1). A pose is
    `[fx, fy, ground_height, facing]`, fx/fy in Q32.32. The integer-cell entry `_fold` is the special
    case `fx = x·ONE, fy = y·ONE`, `facing` = the first command's direction."""
    k = _shift(sub)
    mstep = ONE >> k
    w, h = len(heights[0]), len(heights)
    cx, cy = fx >> 32, fy >> 32
    seed = (fx, fy, heights[cy][cx], facing)
    micro = [seed]
    cells = [seed]
    for c in cmds:
        dl, gait = _parse(c)
        dx, dy = _ST.DIRS[dl]
        facing = _FACE[dl]                                      # turn to face (free), even if blocked
        sfx, sfy = mstep * dx, mstep * dy
        for _ in range(GAIT[gait] * sub):
            nfx, nfy = fx + sfx, fy + sfy
            ncx, ncy = nfx >> 32, nfy >> 32
            if (ncx, ncy) != (cx, cy):                         # crossing a cell boundary → gate it
                if not (0 <= ncx < w and 0 <= ncy < h):
                    break                                      # off-grid → stop at the sub-cell boundary
                if heights[ncy][ncx] - heights[cy][cx] > max_step:
                    break                                      # a rise above MAX_STEP is a wall → stop
                cx, cy = ncx, ncy
            fx, fy = nfx, nfy
            micro.append((fx, fy, heights[cy][cx], facing))
        cells.append((fx, fy, heights[cy][cx], facing))
    return tuple(micro), tuple(cells)


def _fold(heights, start, cmds, max_step, sub):
    """The shared fold from an integer-cell start (the certified entry). Initial facing = the first
    command's direction; position is cell-aligned `x·ONE, y·ONE`. Delegates to `_fold_from`."""
    x0, y0 = start
    return _fold_from(heights, x0 * ONE, y0 * ONE, _FACE[_parse(cmds[0])[0]], cmds, max_step, sub)


def glide(heights, start, cmds, max_step, sub):
    """The full sub-cell trajectory: every micro-step pose from the start, a pure function of
    (start, log, max_step, sub). The continuous terrain-lockstep witness."""
    check_log(heights, start, cmds, max_step, sub)
    return _fold(heights, start, cmds, max_step, sub)[0]


def glide_cells(heights, start, cmds, max_step, sub):
    """One pose per command boundary (len == len(cmds) + 1). Floored to cells, this reproduces
    `drive`'s trajectory bit-for-bit — the refinement bridge."""
    check_log(heights, start, cmds, max_step, sub)
    return _fold(heights, start, cmds, max_step, sub)[1]


def floored(cells):
    """A command-boundary trajectory projected to the integer grid: (fx>>32, fy>>32, ground, facing).
    This is the object that equals `drive(...)` — the measured refinement equality."""
    return tuple((fx >> 32, fy >> 32, g, f) for (fx, fy, g, f) in cells)


def glide_digest(name, start, cmds, sub, trajectory):
    """The URDRGLIDE1 canon — SHA-256(MAGIC | name | start | log | sub | trajectory). Binds the INPUT
    (including the subdivision) and its RESULT, so any tamper — a forged command or a changed sub —
    moves the digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|s:{start[0]},{start[1]}|c:{cmds}|sub:{sub}".encode())
    for p in trajectory:
        hh.update(b"|")
        hh.update(",".join(str(int(v)) for v in p).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _heights(scene):
    return _HF.scene_digest(_HF.SCENES[scene]())[1]


def glide_stroll():
    """A walk east across `blank` at sub = 4 — the plain sub-cell glide: four cells, sixteen
    micro-steps, each a quarter-cell. Its cell samples floor to `drive.stroll`."""
    return ("blank", (2, 8), "eeee", 16, 4)


def glide_sprint():
    """The SAME directions at SPRINT gait, sub = 4 — twice the ground per command, eight micro-steps
    per command. Cell samples floor to `drive.sprint_run`."""
    return ("blank", (2, 8), "EEEE", 16, 4)


def glide_wall():
    """A northward sprint on `mountains` into the ridge, sub = 4 — the actor glides sub-cell toward the
    wall and stops one micro-step short of the too-high cell. Floors to `drive.sprint_wall`: the
    sub-cell stop is the continuous echo of the grid wall."""
    return ("mountains", (6, 24), "NNNNNN", 20, 4)


SCENES = {"glide_stroll": glide_stroll, "glide_sprint": glide_sprint, "glide_wall": glide_wall}


def scene_result(name):
    """Run a named glide → (final micro pose, digest). Same host, same bytes."""
    scene, start, cmds, ms, sub = SCENES[name]()
    traj = glide(_heights(scene), start, cmds, ms, sub)
    return traj[-1], glide_digest(name, start, cmds, sub, traj)


def golden(name):
    """The pinned digest for a named scene from `conformance_glide.txt`."""
    with open(_os.path.join(_HERE, "conformance_glide.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise GlideError("GLIDE-REFUSE", f"no golden named {name!r}")
