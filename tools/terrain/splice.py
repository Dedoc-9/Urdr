# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""splice — glide resumption: the memoryless property that makes continuous movement ROLLBACK-ABLE
(T3.19, MMO Stage B foundation). `glide` folds an input log from an integer-cell start; this proves the
fold is RESUMABLE from any command boundary — a glide's future depends only on its current Q32.32 pose,
not on the history that produced it — and that is the primitive continuous rollback-replay (Stage B ∘
Stage A) is built on.

The capability is a sub-cell START: `glide._fold_from` folds from an arbitrary `(fx, fy, facing)` pose
(the current cell re-derived `cx = fx >> 32`, the fold's invariant). `resume` exposes it; `splice` cuts a
glide at a command boundary and re-glides the tail from the boundary pose.

THE KEYSTONE (measured): SPLICE EQUIVALENCE. For every log, every interior split `at`, and every
subdivision, `splice` — glide the prefix `cmds[:at]`, then RESUME the suffix `cmds[at:]` from the
boundary pose — reproduces `glide_cells(full)` BIT-FOR-BIT. The glide is command-boundary memoryless:
`glide(start, cmds) == glide(start, cmds[:at]) ++ resume(boundary_at, cmds[at:])`. This is exactly what a
rollback needs — keep the agreed prefix, re-simulate only the tail from the last agreed pose, and land on
the same trajectory — now at CONTINUOUS sub-cell resolution, including a resume from a SUB-CELL boundary
(a wall-stopped pose mid-cell), not just cell-aligned ones.

GRADE. The splice equivalence, `resume`'s determinism, and its tamper-evidence are MEASURED (exact,
reproducible, a defect diverges). `does_not_show`: the client-prediction RECONCILE itself (localizing the
mispredict tick and choosing the rollback point is `glide ∘ predict`, the next slice — this certifies only
that the rollback, once chosen, reconstructs exactly); interpolation and continuous facing (glide's own
`does_not_show`, unchanged); and any timing claim (`NOT_MEASURED`). Refusals are typed `SPLICE-REFUSE`
(off-grid or non-integer resume pose, bad facing, a non-interior split, empty/short log, bad subdivision):
refuse, never clamp the pose or invent a boundary."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRSPLICE1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                              # the continuous mover (T3.18)


class SpliceError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise SpliceError("SPLICE-REFUSE", message)


def _is_int(v):
    return type(v) is int                                        # bool excluded on purpose


def check_resume(heights, pose, cmds, max_step, sub):
    """Membership in the resume domain — every violation a typed `SPLICE-REFUSE` (glide's own grammar
    checks are reused but their `GLIDE-REFUSE` is converted, so splice speaks with one voice). The resume
    pose is a Q32.32 `(fx, fy, facing)`; its floor cell must be on the grid, `facing` a cardinal 0..3."""
    try:
        w, h = _GL._grid_dims(heights)                         # reuses glide's rectangular-grid check
    except _GL.GlideError as exc:
        _refuse(str(exc).split(": ", 1)[-1])
    if not (isinstance(pose, tuple) and len(pose) == 3 and all(_is_int(v) for v in pose)):
        _refuse(f"resume pose must be an integer (fx, fy, facing), got {pose!r}")
    fx, fy, facing = pose
    if fx < 0 or fy < 0:
        _refuse(f"resume pose {(fx, fy)!r} must be non-negative Q32.32 coordinates")
    if facing not in (0, 1, 2, 3):
        _refuse(f"facing {facing!r} must be a cardinal 0..3 (N/E/S/W)")
    if not (0 <= (fx >> 32) < w and 0 <= (fy >> 32) < h):
        _refuse(f"resume pose floors to cell {(fx >> 32, fy >> 32)!r}, off the {w}x{h} grid")
    if not (isinstance(cmds, str) and 1 <= len(cmds) <= _GL.LOG_MAX):
        _refuse(f"input log must be a str of 1..{_GL.LOG_MAX} commands, got {cmds!r}")
    if not _is_int(max_step) or max_step < 0:
        _refuse(f"max_step must be a non-negative int, got {max_step!r}")
    try:
        _GL._shift(sub)                                        # raises on a bad subdivision
        for c in cmds:
            _GL._parse(c)                                      # raises on an unknown token
    except _GL.GlideError as exc:
        _refuse(str(exc).split(": ", 1)[-1])


def resume(heights, pose, cmds, max_step, sub):
    """The full sub-cell trajectory folded from an arbitrary Q32.32 pose `(fx, fy, facing)` — a glide
    that BEGINS mid-terrain. The ground is re-derived by floor-sampling; the current cell is `fx >> 32`."""
    check_resume(heights, pose, cmds, max_step, sub)
    fx, fy, facing = pose
    return _GL._fold_from(heights, fx, fy, facing, cmds, max_step, sub)[0]


def resume_cells(heights, pose, cmds, max_step, sub):
    """One pose per command boundary, resumed from `pose` (len == len(cmds) + 1; the seed is `pose`)."""
    check_resume(heights, pose, cmds, max_step, sub)
    fx, fy, facing = pose
    return _GL._fold_from(heights, fx, fy, facing, cmds, max_step, sub)[1]


def boundary(heights, start, cmds, max_step, sub, at):
    """The command-boundary pose at index `at` of a glide from an integer-cell `start` (0..len(cmds))."""
    cells = _GL.glide_cells(heights, start, cmds, max_step, sub)
    if not (_is_int(at) and 0 <= at <= len(cmds)):
        _refuse(f"boundary index {at!r} out of range 0..{len(cmds)}")
    return cells[at]


def splice(heights, start, cmds, max_step, sub, at):
    """Reconstruct the full command-boundary trajectory by GLIDING the prefix `cmds[:at]`, then RESUMING
    the suffix `cmds[at:]` from the boundary pose. Requires an INTERIOR split `1 <= at <= len(cmds)-1`
    (both halves non-empty). SPLICE EQUIVALENCE (measured): equals `glide_cells(full)` bit-for-bit."""
    if not (isinstance(cmds, str) and len(cmds) >= 2):
        _refuse(f"splice needs a log of >= 2 commands to cut, got {cmds!r}")
    n = len(cmds)
    if not (_is_int(at) and 1 <= at <= n - 1):
        _refuse(f"splice needs an interior boundary 1..{n - 1}, got at={at!r}")
    prefix = _GL.glide_cells(heights, start, cmds[:at], max_step, sub)
    b = prefix[-1]                                              # the boundary pose (fx, fy, ground, facing)
    resumed = resume_cells(heights, (b[0], b[1], b[3]), cmds[at:], max_step, sub)
    return prefix + resumed[1:]                                 # drop the duplicate seed (resumed[0] == b)


def splice_digest(name, start, cmds, sub, at, trajectory):
    """The URDRSPLICE1 canon — SHA-256(MAGIC | name | start | log | sub | split | resumed trajectory).
    Binds the resumed sub-cell trajectory to its cut, so a forged pose or a moved split moves the digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|s:{start[0]},{start[1]}|c:{cmds}|sub:{sub}|at:{at}".encode())
    for p in trajectory:
        hh.update(b"|")
        hh.update(",".join(str(int(v)) for v in p).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _heights(scene):
    return _GL._heights(scene)


def splice_stroll():
    """Cut a walk east on `blank` after two commands and resume from the cell-aligned boundary."""
    return ("blank", (2, 8), "eeee", 16, 4, 2)


def splice_sprint():
    """Cut a SPRINT east after two commands (a two-cell-per-command gait) and resume the tail."""
    return ("blank", (2, 8), "EEEE", 16, 4, 2)


def splice_wall():
    """THE HARD CASE. Cut at at=1, right after a sprint EAST into a `mountains` wall that stops the
    actor 3/4 of a cell in — a genuinely SUB-CELL boundary pose (moving +x accumulates within the cell
    before the walled crossing; only +x/+y walls do this, floor rounds toward -inf). Resuming the tail
    from that fractional pose still reproduces the whole trajectory — resumption is not limited to
    cell-aligned cuts."""
    return ("mountains", (2, 0), "Ene", 20, 4, 1)


SCENES = {"splice_stroll": splice_stroll, "splice_sprint": splice_sprint, "splice_wall": splice_wall}


def scene_result(name):
    """Run a named splice → the digest of the RESUMED sub-cell trajectory (the new artifact: a glide
    that began mid-terrain). Same host, same bytes."""
    scene, start, cmds, ms, sub, at = SCENES[name]()
    H = _heights(scene)
    b = boundary(H, start, cmds, ms, sub, at)
    resumed = resume(H, (b[0], b[1], b[3]), cmds[at:], ms, sub)
    return splice_digest(name, start, cmds, sub, at, resumed)


def golden(name):
    """The pinned digest for a named scene from `conformance_splice.txt`."""
    with open(_os.path.join(_HERE, "conformance_splice.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise SpliceError("SPLICE-REFUSE", f"no golden named {name!r}")
