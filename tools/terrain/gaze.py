# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""gaze — the certified first-person OBSERVER over the terrain (T3.10, Slice 2 of FPS-over-terrain):
a view of the walking actor is ADMITTED iff it reconstructs to the authoritative pose, else REFUSED.

`stance.py` earns the actor's TRAJECTORY — its authoritative pose over time. This is the observer that
watches it. It is the D7–D10 observability construct (`world_host` / `atlas_*`, i.e. exact-integer
Kálmán observability) specialized to the terrain pose: an axis-selection chart observes a subset of the
pose's coordinates; an atlas is COVERING iff every coordinate is observed by some chart (the trivial-
kernel / full-column-rank condition, `rank = n`); a covering atlas RECONSTRUCTS the pose from a frame,
and a frame is admitted iff its reconstruction's digest equals the CURRENT authority's. This module
carries its own `URDRSTANCE1`-style terrain-local canon (`URDRGAZE1` over the pose), exactly as
buoyancy/crossing/stance carry a terrain-local canon rather than the kernel's — the verdicts are the
same reconstruct-or-refuse law `world_host` runs on the kernel state (a kernel cross-check is a clean
next step, `does_not_show`).

THE POSE is `[x, y, ground_height, facing]` — where the actor stands (from `stance`), the exact ground
under it, and the cardinal it faces (N=0 E=1 S=2 W=3). Four exact integers; no float, no `/ // %`.

THE ADMIT LAW (`admit`), pure — it reads the authority, never mutates it (the membrane):
  * NON-COVERING  → REFUSE `GAZE-NONCOVER`: a frame that does not observe every pose axis cannot pin
    the state (a minimap with no facing); the atlas kernel is nontrivial.
  * LAUNDERING    → REFUSE `GAZE-LAUNDER`: a covering frame whose reconstruction's digest ≠ the
    authority's — a *substituted* pose (a teleport that was never valid) OR a *stale* pose (a once-
    valid frame replayed after the authority advanced). Same mechanism, two threat models.
  * else          → ADMIT: bound to the current authority.

REPLAY is caught BY CONSTRUCTION, and the `stale` scene PINS why: the authority is the CURRENT pose.
Advance the authority `pose[j] → pose[k]` (a real walk step) and the once-valid `pose[j]` frame — still
covering, still an honest reconstruction of *a* pose — now reconstructs to a digest ≠ the current
anchor, so it is REFUSED. The SAME frame that ADMITS at `Authority(pose[j])` REFUSES at
`Authority(pose[k])`: if a wiring bug ever anchored on a stale pose, this scene reddens.

GRADE. The admit/reconstruct/refuse is MEASURED (exact, digest-bound, reproducible; a digest-skipping
admitter would launder — the check is load-bearing). The RENDER is DECLARED (pixels are never measured;
this certifies the view→pose binding, not the picture). The pose authority is `stance`'s (measured).
`does_not_show`: visual localization (recovering the pose from the *terrain seen* is a nonlinear
inversion of the field — NOT this linear observer); a true perspective projection (axis-selection charts
only); TEMPORAL replay of a *spatially identical* pose (identity is content — an identical pose is a
valid current frame; catching same-where-different-when needs a sequence, which the netcode N1/N2 stack
binds — gaze certifies WHERE, composing with lockstep certifies WHERE AND WHEN); the kernel `world_host`
cross-check (verdicts agree with the kernel observer where the `urdr` package is importable)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRGAZE1"
POSE_N = 4                                     # [x, y, ground_height, facing]
_FACE = {"N": 0, "E": 1, "S": 2, "W": 3}
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import stance as _ST                                              # the trajectory (T3.9)
import heightfield as _HF                                         # the certified authority (T1)


class GazeError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


# ---- the D10 observability construct (axis-selection charts), specialized to the pose ----------
class Chart:
    """An axis-selection observer chart: it observes a subset of the pose's coordinates."""
    def __init__(self, axes):
        self.axes = tuple(axes)

    def project(self, pose):
        return [pose[i] for i in self.axes]


class Atlas:
    """A chart family (an observer). COVERING iff every axis is observed by some chart — the
    trivial-kernel / full-column-rank injectivity condition for axis-selection charts (D10)."""
    def __init__(self, charts):
        self.charts = tuple(charts)

    def covers(self, n):
        seen = set()
        for ch in self.charts:
            seen.update(ch.axes)
        return all(a in seen for a in range(n))

    def image(self, pose):
        """The rendered frame = concatenation of every chart's projection (the view encoding)."""
        out = []
        for ch in self.charts:
            out.extend(ch.project(pose))
        return tuple(out)

    def recon(self, image, n):
        """Reconstruct the source pose from a frame (needs a covering atlas). Returns the recovered
        tuple, or None if some axis is unobserved (inadmissible)."""
        pos, axis_at = 0, {}
        for ch in self.charts:
            for a in ch.axes:
                if a not in axis_at:
                    axis_at[a] = pos
                pos += 1
        if any(a not in axis_at for a in range(n)):
            return None
        return tuple(image[axis_at[a]] for a in range(n))


def pose_digest(pose):
    """The URDRGAZE1 pose canon — SHA-256(MAGIC | comma-joined integer pose). The authority anchor."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(b"|")
    hh.update(",".join(str(int(v)) for v in pose).encode())
    return hh.hexdigest()


class Authority:
    """Owns the CURRENT authoritative pose and its digest — the moving actor's world-host. `admit`
    reads it; it is never mutated by admission (the membrane: presentation cannot feed the authority)."""
    def __init__(self, pose):
        if not (isinstance(pose, tuple) and len(pose) == POSE_N and all(type(v) is int for v in pose)):
            raise GazeError("GAZE-REFUSE", f"pose must be {POSE_N} ints, got {pose!r}")
        self.pose = pose
        self.anchor = pose_digest(pose)


def admit(authority, atlas, image):
    """ADMIT iff the atlas is COVERING and the frame RECONSTRUCTS to the CURRENT authority pose; else
    a typed REFUSE, never repaired. Returns (verdict, code). Pure: touches nothing on `authority`."""
    if not isinstance(authority, Authority):
        raise GazeError("GAZE-REFUSE", "authority must be an Authority")
    if not atlas.covers(POSE_N):
        return ("REFUSE", "GAZE-NONCOVER")
    src = atlas.recon(image, POSE_N)
    if src is None:
        return ("REFUSE", "GAZE-NONCOVER")
    if pose_digest(src) != authority.anchor:
        return ("REFUSE", "GAZE-LAUNDER")
    return ("ADMIT", "GAZE-OK")


def full_atlas():
    """The covering observer — one chart that sees all four pose axes."""
    return Atlas([Chart((0, 1, 2, 3))])


def blind_atlas():
    """A NON-COVERING observer — it omits the facing axis (3), so it cannot pin the pose."""
    return Atlas([Chart((0, 1, 2))])


def trajectory(scene):
    """The authoritative pose sequence along a `stance` walk: `[x, y, ground_height, facing]` at each
    cell visited (facing = the walk's cardinal at that cell). len == len(moves) + 1."""
    sc, start, moves, _ms, _ph = _ST.SCENES[scene]()
    heights = _HF.scene_digest(_HF.SCENES[sc]())[1]
    x, y = start
    faces = [moves[0]] + list(moves)                             # initial facing = first step's cardinal
    poses = []
    step = 0
    for i in range(len(moves) + 1):
        poses.append((x, y, heights[y][x], _FACE[faces[i]]))
        if i < len(moves):
            dx, dy = _ST.DIRS[moves[i]]
            x += dx
            y += dy
    return tuple(poses)


# ---- scenarios (pinned by the gate) -----------------------------------------------------
# All four run on the ridge_clear trajectory over `mountains`; k is the CURRENT authority tick.
_SCENE = "ridge_clear"
_K = 8                                                            # the current authority pose index
_J = 3                                                            # an earlier (once-valid) pose index


def _traj():
    return trajectory(_SCENE)


def genuine():
    """An honest covering frame OF THE CURRENT pose → ADMIT (this is also the non-vacuity control)."""
    t = _traj()
    a = Authority(t[_K])
    return a, full_atlas(), full_atlas().image(t[_K])


def noncover():
    """A frame from a NON-COVERING atlas (no facing axis) → REFUSE GAZE-NONCOVER."""
    t = _traj()
    a = Authority(t[_K])
    return a, blind_atlas(), blind_atlas().image(t[_K])


def forged():
    """A covering frame carrying a FABRICATED pose (the current cell teleported +5 east — never a valid
    pose on this path) → REFUSE GAZE-LAUNDER. The substitution threat."""
    t = _traj()
    a = Authority(t[_K])
    x, y, g, f = t[_K]
    fake = (x + 5, y, g, f)
    return a, full_atlas(), full_atlas().image(fake)


def stale():
    """A covering, ONCE-VALID frame of an earlier pose replayed after the authority advanced
    (pose[_J] → pose[_K]) → REFUSE GAZE-LAUNDER. The replay threat; the flip (it ADMITS at its own
    Authority(pose[_J])) is asserted by the properties row — pinning that the anchor is the CURRENT pose."""
    t = _traj()
    a = Authority(t[_K])                                          # authority has advanced to _K
    return a, full_atlas(), full_atlas().image(t[_J])            # replay the _J frame


SCENES = {"genuine": genuine, "noncover": noncover, "forged": forged, "stale": stale}


def scene_verdict(name):
    """Run a named scene → (verdict, code, digest). Same host, same bytes."""
    authority, atlas, image = SCENES[name]()
    verdict, code = admit(authority, atlas, image)
    return verdict, code, gaze_digest(name, verdict, code, image)


def gaze_digest(name, verdict, code, image):
    """The URDRGAZE1 verdict canon — SHA-256(MAGIC | name | verdict | code | frame image). Binds the
    admission decision AND the frame it was made on, so a silent change of either reddens."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|{verdict}|{code}".encode())
    hh.update(b"|")
    hh.update(",".join(str(int(v)) for v in image).encode())
    return hh.hexdigest()


def golden(name):
    """The pinned digest for a named scene from `conformance_gaze.txt`."""
    with open(_os.path.join(_HERE, "conformance_gaze.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise GazeError("GAZE-REFUSE", f"no golden named {name!r}")
