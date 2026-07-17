# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""drive — the certified movement TRANSCRIPT (T3.11, Slice 3a of FPS-over-terrain): the authoritative
trajectory is a pure, exact-integer function of (initial pose, input log) over the certified terrain.

`stance` walks a DECLARED path; this DRIVES the actor from an input log, the way the netcode lockstep
spine (N1) drives a world from an input transcript — specialized to terrain movement. Each input is a
direction with a GAIT: lowercase = walk (1 cell), UPPERCASE = **sprint** (2 cells). The actor turns to
face the command (free), then advances `gait` cells, each cell gated by `stance`'s step law
(`climb = heights[B] − heights[A] ≤ MAX_STEP`); a cell that is off-grid or too high a rise STOPS the
actor at the last good cell (facing still turns). No float, no `/` `//` `%`.

Two exact facts, both bit-reproducible on every host:

  * DETERMINISM — replaying the same (start, input log) reproduces the trajectory bit-for-bit. The
    trajectory is the netcode lockstep witness, on terrain: state is a pure fold over the input.
  * TAMPER-EVIDENCE — the transcript digest binds (start, input log, trajectory), so changing ANY
    command — a forged input, a replayed one, a reordered one — moves the digest. Input integrity is
    a digest equality, not a promise.

GAIT (the sprint question, answered): sprint is a DERIVED gait in the INPUT — walk = 1 cell, sprint =
2 cells — not a pose axis and not a fixed-point velocity. It is load-bearing: the same directions at
sprint cover twice the ground, and a sprint whose second cell is a wall moves one cell and stops (the
per-cell gate applies under sprint). Velocity/rotation-as-fixed-point are the DECLARED next regime.

D7–D10 SEAM. Each trajectory pose is `[x, y, ground_height, facing]` — exactly what `gaze` observes.
`gaze` certifies a *view* reconstructs to `trajectory[k]`; this module certifies `trajectory[k]` is the
correct derivation from the pinned input at tick k. Together they are WHERE (gaze) AND WHEN (the
transcript): binding the tick into the observed pose closes the temporal-replay gap gaze named — the
clean next composition. `does_not_show`: continuous position / fixed-point rotation (mouse-look is the
Q32.32 regime — `fpquat`/`fppose` — NOT this exact-integer grid); diagonal moves; the kernel lockstep
cross-check.

GRADE. The trajectory + its determinism + tamper-evidence are MEASURED (exact, reproducible, a defect
diverges). The movement MODEL (turn-then-advance-gait-cells, a rise > MAX_STEP walls) is DECLARED, like
buoyancy/crossing/stance. Refusals are typed `DRIVE-REFUSE` (unknown command, empty log, off-grid
start, negative step, non-int): refuse, never clamp the path or invent a footing."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRDRIVE1"
LOG_MAX = 4096
GAIT = {"walk": 1, "sprint": 2}
_FACE = {"N": 0, "E": 1, "S": 2, "W": 3}
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import stance as _ST                                              # the step law + DIRS (T3.9)
import heightfield as _HF                                         # the certified authority (T1)


class DriveError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise DriveError("DRIVE-REFUSE", message)


def _is_int(v):
    return type(v) is int                                        # bool excluded on purpose


def _parse(cmd):
    """A command char → (direction 'N/S/E/W', gait 'walk'|'sprint'). UPPERCASE = sprint, lower = walk."""
    if not (isinstance(cmd, str) and len(cmd) == 1 and cmd.upper() in _FACE):
        _refuse(f"command {cmd!r} is not one of N/S/E/W (upper=sprint, lower=walk)")
    return cmd.upper(), ("sprint" if cmd.isupper() else "walk")


def _grid_dims(heights):
    if not (isinstance(heights, tuple) and heights and isinstance(heights[0], tuple) and heights[0]):
        _refuse("heights must be a non-empty tuple of non-empty rows")
    w = len(heights[0])
    for row in heights:
        if not (isinstance(row, tuple) and len(row) == w):
            _refuse("heights rows must all be the same width (a rectangular field)")
    return w, len(heights)


def check_log(heights, start, cmds, max_step):
    """Membership in the drive domain — every violation a typed `DRIVE-REFUSE`. The commands are NOT
    pre-walked (unlike stance): the actor may legitimately be stopped by the terrain mid-log; only the
    INPUTS are validated here (start on the grid, every token a known command, bounds)."""
    w, h = _grid_dims(heights)
    if not (isinstance(start, tuple) and len(start) == 2 and _is_int(start[0]) and _is_int(start[1])):
        _refuse(f"start must be an integer (x, y), got {start!r}")
    if not (isinstance(cmds, str) and 1 <= len(cmds) <= LOG_MAX):
        _refuse(f"input log must be a str of 1..{LOG_MAX} commands, got {cmds!r}")
    if not _is_int(max_step) or max_step < 0:
        _refuse(f"max_step must be a non-negative int, got {max_step!r}")
    if not (0 <= start[0] < w and 0 <= start[1] < h):
        _refuse(f"start {start!r} is off the {w}x{h} grid")
    for i, c in enumerate(cmds):
        _parse(c)                                                # raises DRIVE-REFUSE on an unknown token


def step(heights, pose, cmd, max_step):
    """Advance one command. Turn to face its direction (free), then move `gait` cells; each cell is
    entered only if it is on-grid AND its rise is at most MAX_STEP (stance's step law). A blocked cell
    stops the actor there — refuse to walk through a wall, never clamp past it."""
    x, y, _grd, _fc = pose
    w, h = len(heights[0]), len(heights)
    dl, gait = _parse(cmd)
    dx, dy = _ST.DIRS[dl]
    for _ in range(GAIT[gait]):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            break                                                # off-grid → stop
        if heights[ny][nx] - heights[y][x] > max_step:
            break                                                # a rise above MAX_STEP is a wall → stop
        x, y = nx, ny
    return (x, y, heights[y][x], _FACE[dl])


def drive(heights, start, cmds, max_step):
    """The authoritative trajectory: fold `step` over the input log from the start pose. Returns the
    tuple of `[x, y, ground_height, facing]` poses (len == len(cmds) + 1), a pure function of the
    inputs — the terrain lockstep witness."""
    check_log(heights, start, cmds, max_step)
    x, y = start
    pose = (x, y, heights[y][x], _FACE[_parse(cmds[0])[0]])       # initial facing = first command's dir
    traj = [pose]
    for c in cmds:
        pose = step(heights, pose, c, max_step)
        traj.append(pose)
    return tuple(traj)


def transcript_digest(name, start, cmds, trajectory):
    """The URDRDRIVE1 canon — SHA-256(MAGIC | name | start | input log | trajectory). Binds the INPUT
    and its RESULT, so a forged, replayed, or reordered command moves the digest (tamper-evidence)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|s:{start[0]},{start[1]}|c:{cmds}".encode())
    for p in trajectory:
        hh.update(b"|")
        hh.update(",".join(str(int(v)) for v in p).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _heights(scene):
    return _HF.scene_digest(_HF.SCENES[scene]())[1]


def stroll():
    """A walk east across the `blank` canvas — the plain transcript (walk gait, 1 cell/command)."""
    return ("blank", (2, 8), "eeee", 16)


def sprint_run():
    """The SAME directions at SPRINT gait — twice the ground per command. Gait is load-bearing: the
    only difference from `stroll` is lowercase→uppercase, and the actor ends two columns further."""
    return ("blank", (2, 8), "EEEE", 16)


def sprint_wall():
    """A northward sprint on `mountains` into the 21-high ridge face. The stride distances are
    [2,2,2,1,0,0]: three full sprints, then a PARTIAL stride — the actor takes the first cell but the
    second is a rise above MAX_STEP, so it stops mid-stride — then walled. The per-cell step gate
    applies under sprint, not just walk: sprint does not vault a wall."""
    return ("mountains", (6, 24), "NNNNNN", 20)


SCENES = {"stroll": stroll, "sprint_run": sprint_run, "sprint_wall": sprint_wall}


def scene_result(name):
    """Run a named drive → (final pose, digest). Same host, same bytes."""
    scene, start, cmds, ms = SCENES[name]()
    traj = drive(_heights(scene), start, cmds, ms)
    return traj[-1], transcript_digest(name, start, cmds, traj)


def golden(name):
    """The pinned digest for a named scene from `conformance_drive.txt`."""
    with open(_os.path.join(_HERE, "conformance_drive.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise DriveError("DRIVE-REFUSE", f"no golden named {name!r}")
