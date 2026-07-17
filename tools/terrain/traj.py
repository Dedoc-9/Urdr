# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""traj — the certified TRAJECTORY OBSERVER over the terrain (T3.12, Slice 3b of FPS-over-terrain):
a *sequence* of partial views is ADMITTED iff every frame reconstructs to the pose the dynamics
predict at that tick, else REFUSED — the innovation ν = y − H·Φ·x̂ decided in exact integers.

Where `gaze` (Slice 2) is a SNAPSHOT observer — one covering frame, `rank = n` at a single instant —
this is a HORIZON observer. It couples the deterministic dynamics Φ (`drive.step`, T3.11) with the
axis-selection observation H (`gaze`'s Chart/Atlas) across n steps, so two things `gaze` cannot do
become possible:

  * PARTIAL COVERAGE is admissible. A frame need not see every axis; over the horizon the dynamics
    carry the unobserved axes into the observed ones. Position-only frames reconstruct the full pose
    because ground is a pure function of position (`heightfield[y][x]`) and facing is the direction of
    the position delta when the actor moves. `gaze` REFUSES each such frame (`GAZE-NONCOVER`); the
    trajectory observer ADMITS the sequence.
  * TEMPORAL REPLAY is caught. A frame that is a faithful view of a pose the actor genuinely held at
    ANOTHER tick — `gaze`'s own `does_not_show`, "identity is content" — is refused here, because the
    dynamics predict a DIFFERENT pose at this tick and the innovation is nonzero. This closes the
    same-where-different-WHEN gap `gaze` deferred to "a sequence": the sequence is Φ.

THE INNOVATION, exactly. The observer reconstructs the authoritative trajectory locally (the Φ-fold of
the lockstep inputs from the start — the SAME law the authority runs, `drive.drive`, so the frame is
checked against a locally-derived truth, not a trusted one). For each tick the residual
ν(k) = image(k) − H(k)·trajectory(k) is formed in exact integers; the witness ADMITS iff every ν is
the zero vector, else the first nonzero tick is a typed REFUSE. Zero divides nothing: the verdict is a
divisibility-free equality, so it is either confirmed or fought, never rounded.

MEASURED (exact, reproducible, a defect diverges): the reconstruction from partial frames, the exact
innovation verdict (admit iff every ν == 0), the replay/teleport discrimination (a witness whose every
frame is content-valid — a pose that occurs in the trajectory — yet is REFUSED), facing-from-motion,
determinism, tamper-evidence, typed refusals. DECLARED: the general linear Kálmán observability MATRIX
O = [H; H·Φ; H·Φ²; …; H·Φⁿ⁻¹] and its rank test — `drive.step` is input-driven and terrain-gated, NOT
an LTI operator, so the horizon observability is computed OPERATIONALLY on this dynamics and the linear
matrix is the MODEL, not the measured object. The pose authority is `drive`'s (measured); the render is
`gaze`'s declared view.

`does_not_show`: facing UNOBSERVABLE-from-position when the actor is BLOCKED (a stationary step — it
needs the facing axis observed, or the input); input INFERENCE (the inputs are lockstep-known, N1, not
inferred from the frames); visual localization (recovering the pose from the terrain *seen* is a
nonlinear field inversion — the `gaze` barrier); continuous / fixed-point Φ (the Q32.32 regime,
`fpquat`/`fppose`, is the Slice-4 enrichment of Φ, not this exact-integer grid); the kernel `world_host`
cross-check (verdicts agree with the kernel observer where the `urdr` package is importable). No float,
no `/` `//` `%`."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRTRAJ1"
POSE_N = 4                                        # [x, y, ground_height, facing]
LOG_MAX = 4096
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import gaze as _GZ                                # the snapshot observer: Chart / Atlas / covers / recon
import drive as _DR                               # the dynamics Φ = step; the trajectory fold (T3.11)
import stance as _ST                              # DIRS (cardinal deltas)
import heightfield as _HF                         # the certified authority (T1)


class TrajError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise TrajError("TRAJ-REFUSE", message)


def _is_int(v):
    return type(v) is int                         # bool excluded on purpose


def _atlas(axes):
    """A gaze observer that sees exactly `axes` — reuses gaze's covering / reconstruction law."""
    return _GZ.Atlas([_GZ.Chart(axes)])


def covers(axes):
    """True iff `axes` observes every pose coordinate (gaze's full-column-rank condition, rank = n)."""
    return _atlas(axes).covers(POSE_N)


def _project(pose, axes):
    """H·pose: the observed coordinates of a pose (a frame's image), in axis order."""
    return tuple(pose[i] for i in axes)


def frame_of(pose, axes):
    """An honest frame = (axes, H·pose). What a client SHOULD send when observing `axes` of `pose`."""
    return (tuple(axes), _project(pose, axes))


def facing_from_motion(prev_xy, xy):
    """The observability coupling made concrete: recover the cardinal FACING from a position delta.
    Returns the facing index (N=0 E=1 S=2 W=3) when the actor moved 1..2 cells along a cardinal, None
    when it did not move (facing is NOT observable from a stationary step — a `does_not_show`), and a
    typed refuse for an impossible motion (diagonal, or > 2 cells: no valid Φ-step produces it)."""
    mx, my = xy[0] - prev_xy[0], xy[1] - prev_xy[1]
    if mx == 0 and my == 0:
        return None                               # stationary: facing unobservable from position alone
    for d, (dx, dy) in _ST.DIRS.items():
        for s in (1, 2):                          # walk (1) or sprint (2); division-free membership test
            if mx == dx * s and my == dy * s:
                return _DR._FACE[d]
    _refuse(f"motion {(mx, my)} is not a cardinal 1..2-cell step (no Φ-transition produces it)")


def reconstruct(heights, start, cmds, max_step):
    """The observer's independent state reconstruction over the horizon: the Φ-fold of the lockstep
    inputs from the start. Identical to the authority's `drive.drive` — same law, same bytes — so the
    observation is checked against a LOCALLY-DERIVED truth, not a trusted one."""
    return _DR.drive(heights, start, cmds, max_step)


def innovation(image, predicted):
    """ν = y − H·x̂ elementwise, exact integers. The frame is consistent iff every component is 0."""
    if len(image) != len(predicted):
        _refuse("frame width does not match the observed axes")
    return tuple(a - b for a, b in zip(image, predicted))


def content_valid(axes, image, trajectory):
    """The tickless SNAPSHOT predicate ('identity is content'): a COVERING frame that reconstructs to
    SOME pose the actor genuinely holds in `trajectory`. This is what a snapshot admits with no clock —
    the trajectory observer refuses it anyway when the tick is wrong (that gap is the whole point)."""
    a = _atlas(axes)
    if not a.covers(POSE_N):
        return False
    src = a.recon(image, POSE_N)
    return src is not None and src in set(trajectory)


def _check_witness(frames, n):
    """Membership in the witness domain — every violation a typed `TRAJ-REFUSE`."""
    if not (isinstance(frames, tuple) and len(frames) == n):
        got = len(frames) if isinstance(frames, tuple) else type(frames).__name__
        _refuse(f"witness must be a tuple of {n} frames (one per tick), got {got}")
    for fr in frames:
        if not (isinstance(fr, tuple) and len(fr) == 2
                and isinstance(fr[0], tuple) and isinstance(fr[1], tuple)):
            _refuse(f"each frame must be (axes, image) tuples, got {fr!r}")
        axes, image = fr
        if len(axes) != len(image) or not all(_is_int(a) and 0 <= a < POSE_N for a in axes):
            _refuse(f"frame axes malformed (ints in 0..{POSE_N - 1}, width == image): {fr!r}")
        if not all(_is_int(v) for v in image):
            _refuse(f"frame image must be integers: {image!r}")


def observe(heights, start, cmds, max_step, frames):
    """ADMIT iff every frame's observed axes equal the pose the dynamics PREDICT at that tick (every
    innovation ν == 0), else the first-failing tick is a typed REFUSE `TRAJ-INNOVATE` — the future
    fought the past. Pure: reconstructs locally, mutates nothing. Returns (verdict, code)."""
    try:
        traj = reconstruct(heights, start, cmds, max_step)
    except _DR.DriveError as exc:                  # bad dynamics inputs surface as a trajectory refusal
        _refuse(f"dynamics rejected the inputs: {exc}")
    _check_witness(frames, len(traj))
    for k, (axes, image) in enumerate(frames):
        predicted = _project(traj[k], axes)
        if any(v != 0 for v in innovation(image, predicted)):
            return ("REFUSE", "TRAJ-INNOVATE")
    return ("ADMIT", "TRAJ-OK")


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_HF_SCENE = "blank"
_START = (2, 8)
_CMDS = "eeee"                                     # walk four cells east; poses x=2..6 at y=8, all facing E
_MS = 16


def _heights(scene):
    return _HF.scene_digest(_HF.SCENES[scene]())[1]


def _honest(axes_per_tick):
    """Build an honest witness of the `_CMDS` trajectory, observing `axes_per_tick[k]` at tick k."""
    traj = _DR.drive(_heights(_HF_SCENE), _START, _CMDS, _MS)
    return traj, tuple(frame_of(traj[k], axes_per_tick[k]) for k in range(len(traj)))


def honest_full():
    """Every tick a COVERING frame of the true pose → ADMIT (the reference + non-vacuity control)."""
    _t, frames = _honest([(0, 1, 2, 3)] * 5)
    return (_HF_SCENE, _START, _CMDS, _MS, frames)


def honest_partial():
    """Every tick a POSITION-ONLY frame (axes 0,1 — NON-covering) → ADMIT. The observability claim:
    `gaze` refuses each of these (`GAZE-NONCOVER`); the horizon observer admits the sequence because Φ
    carries facing (from the motion) and the field carries ground."""
    _t, frames = _honest([(0, 1)] * 5)
    return (_HF_SCENE, _START, _CMDS, _MS, frames)


def replay():
    """Honest covering frames EXCEPT tick 2 replays the tick-0 pose — a faithful view of a pose the
    actor genuinely held, at the WRONG tick → REFUSE `TRAJ-INNOVATE`. Every frame is content-valid, so
    a tickless snapshot would ADMIT; the dynamics refuse it. (same-where-different-WHEN)"""
    traj, frames = _honest([(0, 1, 2, 3)] * 5)
    frames = frames[:2] + (frame_of(traj[0], (0, 1, 2, 3)),) + frames[3:]     # tick 2 ← pose[0]
    return (_HF_SCENE, _START, _CMDS, _MS, frames)


def teleport():
    """Honest covering frames EXCEPT tick 2 shows an UNREACHABLE pose (x = 99, off the path) → REFUSE
    `TRAJ-INNOVATE`. Unlike `replay`, this pose is NOT in the trajectory (content-INVALID) — caught even
    by a snapshot; included to pin that an impossible transition also reddens."""
    traj, frames = _honest([(0, 1, 2, 3)] * 5)
    _x, y, g, f = traj[2]
    frames = frames[:2] + (frame_of((99, y, g, f), (0, 1, 2, 3)),) + frames[3:]
    return (_HF_SCENE, _START, _CMDS, _MS, frames)


SCENES = {"honest_full": honest_full, "honest_partial": honest_partial,
          "replay": replay, "teleport": teleport}


def scene_result(name):
    """Run a named scene → (verdict, code, digest). Same host, same bytes."""
    hf, start, cmds, ms, frames = SCENES[name]()
    verdict, code = observe(_heights(hf), start, cmds, ms, frames)
    return verdict, code, traj_digest(name, verdict, code, frames)


def traj_digest(name, verdict, code, frames):
    """The URDRTRAJ1 verdict canon — SHA-256(MAGIC | name | verdict | code | every frame). Binds the
    decision AND the witness it was made on, so a forged / replayed / reordered frame moves the digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|{verdict}|{code}".encode())
    for axes, image in frames:
        hh.update(b"|a:")
        hh.update(",".join(str(int(a)) for a in axes).encode())
        hh.update(b";v:")
        hh.update(",".join(str(int(v)) for v in image).encode())
    return hh.hexdigest()


def golden(name):
    """The pinned digest for a named scene from `conformance_traj.txt`."""
    with open(_os.path.join(_HERE, "conformance_traj.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise TrajError("TRAJ-REFUSE", f"no golden named {name!r}")
