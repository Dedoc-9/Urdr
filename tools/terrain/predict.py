# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""predict — the client-prediction RECONCILE primitive (T3.17, Stage A of the MMO roadmap): given the
authoritative input transcript and a client's PREDICTED one, localize the first misprediction and prove
that keeping the correctly-predicted prefix and re-simulating only the suffix reproduces the authority
BIT-FOR-BIT. Client-side prediction, made reconstruct-or-refuse.

A modern shooter hides latency by letting the client predict inputs it has not yet heard the authority
resolve, simulating locally with `drive`. When the authority reveals the true inputs, most of that work is
correct — the client only needs to roll back to the first tick the two trajectories diverge and replay the
suffix. This module certifies that partial rollback is EXACT: because `drive` is a pure fold, the
trajectory after the divergence tick is a pure function of the last agreed pose and the true suffix, so
re-simulating from the mispredict point reproduces the full authoritative trajectory. The client never
drifts from the authority — it reconstructs, or (if a prefix claimed correct is actually wrong) is refused.
This is the exact-arithmetic answer to client prediction: no float reconciliation, no drift to smooth.

MECHANISM (shared with the dynamics cross-check T3.14 — reused, not reinvented): the first divergence is
localized by the kernel netcode's own `lockstep.first_desync` over the two per-tick pose-digest chains, the
same localizer that certifies a lockstep desync. What is NEW here, and MEASURED, is the RECONCILE
semantics: (a) the reusable prefix is the client work that is provably correct (bit-identical to the
authority), and (b) ROLLBACK-REPLAY EQUIVALENCE — replaying the true suffix from the last agreed pose
reproduces the authoritative trajectory exactly, so a client re-simulates only from the mispredict tick,
never from the start, and never desyncs. Reconcile is POSE-level, not input-level: a client whose guessed
inputs differ but whose POSES coincide (both blocked, say) needs no rollback — its predicted state was
already right.

GRADE. The localization, the reusable-prefix correctness, and the rollback-replay equivalence are MEASURED
(exact, reproducible, a defect diverges). `does_not_show`: network transport / jitter / loss (the protocol,
not this primitive); WALL-CLOCK latency and tick budget (NOT_MEASURED until the sealed bench protocol,
Stage H — this module makes NO timing claim); the input-PREDICTION policy (how a client guesses inputs is a
DECLARED client heuristic — this certifies the reconcile is correct for ANY prediction); continuous
positions (the exact-integer grid `drive`; the fixed-point regime is Stage B); server authority, interest
management, and cross-region handoff (Stages C–D). No float, no clock. Refusals typed `PRED-REFUSE`."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRPRED1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _p in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import drive as _DR                                                # the pure exact-integer fold (T3.11)
import lockstep as _N1                                             # the kernel netcode localizer (first_desync)
import heightfield as _HF                                          # the certified terrain authority


class PredError(Exception):
    def __init__(self, message):
        super().__init__(f"PRED-REFUSE: {message}")
        self.code = "PRED-REFUSE"


def _chain(traj):
    """A per-tick pose-digest chain — the witness the kernel `first_desync` localizes over."""
    return [hashlib.sha256(("URDRPREDW|" + ",".join(str(int(v)) for v in p)).encode()).hexdigest()
            for p in traj]


def _validate(auth_cmds, pred_cmds):
    if not (isinstance(auth_cmds, str) and isinstance(pred_cmds, str)):
        raise PredError("transcripts must be command strings")
    if len(auth_cmds) != len(pred_cmds):
        raise PredError(f"reconcile window mismatch: |auth|={len(auth_cmds)} ≠ |pred|={len(pred_cmds)}")
    if len(auth_cmds) < 1:
        raise PredError("empty reconcile window")


def reconcile(heights, start, auth_cmds, pred_cmds, max_step):
    """Localize the first misprediction between the authoritative and predicted transcripts over the same
    (terrain, start, max_step). Returns (mispredict_tick, reusable_prefix): the first POSE index at which
    the predicted trajectory diverges from the authoritative one (None if the prediction was pose-correct),
    and the prefix of authoritative poses the client kept correctly. Pure — mutates nothing."""
    _validate(auth_cmds, pred_cmds)
    try:
        t_auth = _DR.drive(heights, start, auth_cmds, max_step)
        t_pred = _DR.drive(heights, start, pred_cmds, max_step)
    except _DR.DriveError as exc:
        raise PredError(f"dynamics rejected a transcript: {exc}")
    k = _N1.first_desync(_chain(t_pred), _chain(t_auth))           # first divergent pose index, or None
    reusable = tuple(t_auth) if k is None else tuple(t_auth[:k])
    return k, reusable


def replay(heights, start, reusable, auth_cmds, max_step):
    """Reconstruct the FULL authoritative trajectory from the reusable prefix + the true suffix, re-folding
    `drive.step` from the last agreed pose. The client re-simulates only from the mispredict tick — never
    from the start (unless it mispredicted the very first tick, k == 0)."""
    n = len(auth_cmds) + 1
    if len(reusable) == n:                                         # prediction was correct — nothing to replay
        return tuple(reusable)
    if len(reusable) == 0:                                         # mispredicted tick 0 — full re-simulation
        return _DR.drive(heights, start, auth_cmds, max_step)
    k = len(reusable)                                              # last agreed pose is reusable[k-1]
    pose = reusable[-1]
    out = list(reusable)
    for c in auth_cmds[k - 1:]:                                    # cmd k-1 regenerates pose k, …
        pose = _DR.step(heights, pose, c, max_step)
        out.append(pose)
    return tuple(out)


def reconstruct(heights, start, auth_cmds, pred_cmds, max_step):
    """THE KEYSTONE (rollback-replay equivalence): reconcile then replay reproduces the full authoritative
    re-simulation `drive(auth)` BIT-FOR-BIT — the client keeps its correct work, replays only the suffix,
    and lands exactly on the authority. Returns the reconstructed trajectory."""
    _k, reusable = reconcile(heights, start, auth_cmds, pred_cmds, max_step)
    return replay(heights, start, reusable, auth_cmds, max_step)


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_HF_SCENE = "blank"
_START = (2, 8)
_MS = 16


def _heights(scene):
    return _HF.scene_digest(_HF.SCENES[scene]())[1]


def _scene_row(name, auth, pred):
    H = _heights(_HF_SCENE)
    k, reusable = reconcile(H, _START, auth, pred, _MS)
    recon = replay(H, _START, reusable, auth, _MS)
    auth_traj = _DR.drive(H, _START, auth, _MS)
    return name, (-1 if k is None else k), len(reusable), (1 if recon == auth_traj else 0)


def correct():
    """The client predicted the true inputs exactly → no misprediction, full reusable prefix, no rollback."""
    return _scene_row("correct", "eeee", "eeee")


def mispredict():
    """The client mispredicted command 2 (e→N) → diverges mid-trajectory; the prefix is kept and the suffix
    replayed to reproduce the authority."""
    return _scene_row("mispredict", "eeee", "eeNe")


def early():
    """The client mispredicted the FIRST command (initial facing differs) → k == 0, empty prefix, full
    re-simulation still reconstructs the authority."""
    return _scene_row("early", "eeee", "Neee")


SCENES = {"correct": correct, "mispredict": mispredict, "early": early}


def _ser_row(row):
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(f"|{row[0]}|{row[1]}|{row[2]}|{row[3]}".encode())
    return h.hexdigest()


def scene_result(name):
    """Run a named scene → digest binding (name, mispredict_tick, reusable_len, reconstruct==authority).
    Same host, same bytes."""
    return _ser_row(SCENES[name]())


def golden(name):
    """The pinned digest for a named scene from `conformance_predict.txt`."""
    with open(_os.path.join(_HERE, "conformance_predict.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PredError(f"no golden named {name!r}")
