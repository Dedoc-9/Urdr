# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cpredict — continuous client-prediction reconcile (T3.20, MMO Stage A × Stage B): `predict` on `glide`.
Where `predict` reconciles a client's guessed inputs against the authority on the exact-integer GRID
(`drive`), this reconciles them on the CONTINUOUS Q32.32 sub-cell trajectory (`glide`) — and rolls back
using `splice`'s resumption, which certified that a glide is replayable from any boundary pose.

The composition is not a re-implementation; it stands on two already-measured facts. From `splice`: a
glide resumes exactly from the last agreed pose, so the reconstruction keeps the correct prefix and
re-glides only the tail. From `glide`'s refinement bridge (floored glide == drive): the continuous
localizer catches a divergence NO LATER than the discrete one — if two floored trajectories differ at
tick i, the continuous ones already differed at some j ≤ i.

THREE MEASURED FACTS.
  * CONTINUOUS ROLLBACK-REPLAY EQUIVALENCE — for every predicted transcript, `reconstruct` (keep the
    agreed prefix, resume the true suffix from the boundary pose) equals the full continuous re-simulation
    `glide_cells(auth)` BIT-FOR-BIT.
  * REFINES THE DISCRETE RECONCILE — the continuous mispredict tick precedes-or-equals the discrete one
    (`predict`'s), and is STRICTLY earlier on a SUB-CELL misprediction the grid cannot see: a client that
    guesses a walk where the authority sprinted into a wall lands in the SAME cell (drive sees no
    mispredict) but a different SUB-CELL pose (glide does). Continuous prediction is more precise, provably.
  * FLOORS TO DRIVE (the commutation) — the floored continuous reconstruction equals `drive(auth)`, i.e.
    the discrete reconcile `predict` already certified; refining to sub-cell resolution never contradicts
    the grid answer, it only sharpens it.

GRADE. The continuous equivalence, the refinement (tick ≤ discrete, with a sub-cell witness), and the
commutation are MEASURED (exact, reproducible, a defect diverges). `does_not_show`: the input-PREDICTION
policy (how a client guesses is a DECLARED heuristic — this certifies the reconcile for ANY guess);
network transport / jitter / loss (the protocol, not this primitive); and **WALL-CLOCK latency and tick
budget are `NOT_MEASURED`** — no timing or scale claim, none until the sealed bench (Stage H). Refusals are
typed `CPRED-REFUSE` (window mismatch, empty window, bad transcript / subdivision): refuse, never smooth."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRCPRED1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PHYS = _os.path.join(_os.path.dirname(_HERE), "physics")
_NET = _os.path.join(_os.path.dirname(_HERE), "netcode")
for _p in (_HERE, _PHYS, _NET):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import glide as _GL                                               # the continuous mover (T3.18)
import splice as _SP                                              # glide resumption (T3.19)
import lockstep as _N1                                            # the kernel localizer (N1)


class CPredError(Exception):
    def __init__(self, message):
        super().__init__(f"CPRED-REFUSE: {message}")
        self.code = "CPRED-REFUSE"


def _chain(traj):
    """A per-pose-boundary digest chain over CONTINUOUS poses — the witness `first_desync` localizes."""
    return [hashlib.sha256(("URDRCRECW|" + ",".join(str(int(v)) for v in p)).encode()).hexdigest()
            for p in traj]


def _validate(auth_cmds, pred_cmds):
    if not (isinstance(auth_cmds, str) and isinstance(pred_cmds, str)):
        raise CPredError("transcripts must be command strings")
    if len(auth_cmds) != len(pred_cmds):
        raise CPredError(f"reconcile window mismatch: |auth|={len(auth_cmds)} != |pred|={len(pred_cmds)}")
    if len(auth_cmds) < 1:
        raise CPredError("empty reconcile window")


def reconcile(heights, start, auth_cmds, pred_cmds, max_step, sub):
    """Localize the first misprediction between the authoritative and predicted transcripts on the
    CONTINUOUS trajectory (glide command boundaries). Returns (mispredict_tick, reusable_prefix): the
    first pose-boundary index at which the predicted glide diverges from the authoritative one (None if
    pose-correct), and the prefix of authoritative continuous poses the client kept. Pure."""
    _validate(auth_cmds, pred_cmds)
    try:
        t_auth = _GL.glide_cells(heights, start, auth_cmds, max_step, sub)
        t_pred = _GL.glide_cells(heights, start, pred_cmds, max_step, sub)
    except _GL.GlideError as exc:
        raise CPredError(f"dynamics rejected a transcript: {exc}")
    k = _N1.first_desync(_chain(t_pred), _chain(t_auth))          # first divergent boundary index, or None
    reusable = tuple(t_auth) if k is None else tuple(t_auth[:k])
    return k, reusable


def replay(heights, start, reusable, auth_cmds, max_step, sub):
    """Reconstruct the FULL authoritative continuous trajectory from the reusable prefix + the true
    suffix, RESUMING the glide from the last agreed boundary pose (`splice.resume` — the memoryless
    property). The client re-glides only from the mispredict tick, never from the start (unless it
    mispredicted the very first boundary, k == 0)."""
    n = len(auth_cmds) + 1
    if len(reusable) == n:                                        # prediction was correct — nothing to replay
        return tuple(reusable)
    if len(reusable) == 0:                                        # mispredicted boundary 0 — full re-glide
        return _GL.glide_cells(heights, start, auth_cmds, max_step, sub)
    k = len(reusable)                                            # last agreed pose is reusable[k-1]
    fx, fy, _g, facing = reusable[-1]
    resumed = _SP.resume_cells(heights, (fx, fy, facing), auth_cmds[k - 1:], max_step, sub)
    return tuple(reusable) + resumed[1:]                         # cmd k-1 regenerates pose k, …


def reconstruct(heights, start, auth_cmds, pred_cmds, max_step, sub):
    """THE KEYSTONE (continuous rollback-replay equivalence): reconcile then replay reproduces the full
    continuous re-simulation `glide_cells(auth)` BIT-FOR-BIT — the client keeps its correct work, resumes
    only the suffix, and lands exactly on the authority at sub-cell resolution."""
    _k, reusable = reconcile(heights, start, auth_cmds, pred_cmds, max_step, sub)
    return replay(heights, start, reusable, auth_cmds, max_step, sub)


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_START = (2, 8)
_MS = 16
_SUB = 4


def _heights(scene):
    return _GL._heights(scene)


def _cpred_digest(name, scene, auth, pred, k, recon):
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|{scene}|a:{auth}|p:{pred}|sub:{_SUB}|k:{k}".encode())
    for p in recon:
        hh.update(b"|")
        hh.update(",".join(str(int(v)) for v in p).encode())
    return hh.hexdigest()


def _scene(name, scene, start, auth, pred, ms, sub):
    H = _heights(scene)
    k, _r = reconcile(H, start, auth, pred, ms, sub)
    recon = reconstruct(H, start, auth, pred, ms, sub)
    return _cpred_digest(name, scene, auth, pred, k, recon)


def correct():
    """A perfect prediction on `blank` — the client guessed the authority's inputs (k = None, no rollback)."""
    return ("correct", "blank", _START, "eeee", "eeee", _MS, _SUB)


def mispredict():
    """A mid-window misprediction on `blank` — the client guessed `n` where the authority walked `e`."""
    return ("mispredict", "blank", _START, "eeee", "eene", _MS, _SUB)


def subcell():
    """THE REFINEMENT WITNESS. On a `mountains` east wall the client guesses a WALK where the authority
    SPRINTED into the wall — both land in the same CELL (drive sees no mispredict) but different SUB-CELL
    poses, so the continuous reconcile catches a misprediction the grid cannot. `drive` would reuse the
    whole prefix; `glide` rolls back at boundary 1 and reconstructs the true sub-cell trajectory."""
    return ("subcell", "mountains", (2, 0), "E", "e", 20, _SUB)


SCENES = {"correct": correct, "mispredict": mispredict, "subcell": subcell}


def scene_result(name):
    """Run a named continuous reconcile → its URDRCPRED1 digest. Same host, same bytes."""
    nm, scene, start, auth, pred, ms, sub = SCENES[name]()
    return _scene(nm, scene, start, auth, pred, ms, sub)


def golden(name):
    """The pinned digest for a named scene from `conformance_cpredict.txt`."""
    with open(_os.path.join(_HERE, "conformance_cpredict.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CPredError(f"no golden named {name!r}")
