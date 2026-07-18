# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""horizon — the rollback-horizon reconcile window (T3.32, MMO Stage H, URDRLAT1): the worst-case
RECONCILIATION latency of a client correction, made a certified hard bound. This is the OPODIS 2025 insight
turned concrete — because URDR reconciles byte-exactly (the immersion-consistency distance delta = 0), the only
cost of a late input is HOW FAR BACK it rolls, and that is bounded by the snapshot horizon.

THE MODEL. A client predicted a transcript; the authority disagrees from some boundary. `cpredict` localizes
the first mispredict boundary `k` and replays only the suffix (resuming from the last agreed pose — memoryless,
byte-exact). The ROLLBACK DEPTH is `n - k`: how many command-boundaries the client must re-glide. `horizon`
bounds it:
  * ADMIT — depth <= H: the reconcile replays at most H boundaries, and `cpredict.reconstruct` lands on the
    authority BIT-FOR-BIT (delta = 0). Its op-cost is bounded by H x per-boundary work (an `opcost` bound).
  * REFUSE — depth > H: the misprediction is OLDER than the snapshot window; there is no state to roll back
    to, so it is a typed `HORIZON-REFUSE` (refuse, never silently accept a stale correction).

So the worst-case reconcile latency is EXACTLY the horizon H: an admitted correction never replays more than H
boundaries, and a correction that would need more is refused rather than served late. That is the certified
latency window — the rollback horizon as a hard limit, not a hope.

THE COMPOSITION. `rollback_depth` reads `cpredict.reconcile`; `admit_reconcile` gates it and, on admit, returns
`cpredict.reconstruct` (byte-exact); `reconcile_cost` is the exact `opcost` of the replayed suffix. All exact
integer work, so the whole thing reproduces bit-for-bit.

GRADE. The rollback-depth measure, the byte-exact reconstruction on admit (delta = 0), the depth <= H bound,
the `HORIZON-REFUSE` beyond H, the cost bound (reconcile_cost <= depth x per-boundary micro-steps), and
determinism are MEASURED (exact, reproducible, a defect diverges). `does_not_show`: WALL-CLOCK of the reconcile
(bounds the WORK; the time follows via `bench.py`, MEASURED-on-named-host); the snapshot STORAGE cost of
keeping H states (an operational parameter, not certified here); NON-MONOTONE or multi-authority corrections
(this certifies the single-authority east-crossing reconcile `cpredict` covers); and the network TRANSPORT of
the late input."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRLAT1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import cpredict as _CP                                          # continuous rollback-replay reconcile
import glide as _GL                                             # the mover (byte-exact reference)
import opcost as _OC                                            # the op-cost of the replayed suffix


class HorizonError(Exception):
    def __init__(self, message):
        super().__init__(f"HORIZON-REFUSE: {message}")
        self.code = "HORIZON-REFUSE"


def rollback_depth(heights, start, auth_cmds, pred_cmds, max_step, sub):
    """The number of command-boundaries a reconcile must replay = n - k (0 if the prediction was correct),
    where k is the first mispredict boundary. This IS the rollback depth — how far back the client rolls."""
    n = len(auth_cmds) + 1
    _k, reusable = _CP.reconcile(heights, start, auth_cmds, pred_cmds, max_step, sub)
    return n - len(reusable)


def reconcile_cost(heights, start, auth_cmds, pred_cmds, max_step, sub):
    """The EXACT op-cost of the reconcile's replay: the glide micro-steps re-run from the mispredict boundary.
    Bounded by the rollback depth times the per-boundary micro-count (an `opcost` bound)."""
    _k, reusable = _CP.reconcile(heights, start, auth_cmds, pred_cmds, max_step, sub)
    k = len(reusable)
    if k >= len(auth_cmds) + 1:                                  # correct prediction — no replay
        return 0
    if k == 0:                                                  # full re-glide from the start
        return _OC.glide_micro_count(heights, start, auth_cmds, max_step, sub)
    fx, fy, _g, facing = reusable[-1]
    return _OC.glide_micro_count(heights, (fx >> 32, fy >> 32), auth_cmds[k - 1:], max_step, sub)


def admit_reconcile(heights, start, auth_cmds, pred_cmds, max_step, sub, horizon):
    """ADMIT a client reconcile iff its rollback depth is within `horizon`; else `HORIZON-REFUSE`. On admit,
    returns the reconstructed authoritative trajectory (byte-exact — the delta = 0 property). GUARANTEE: an
    admitted reconcile replays <= horizon boundaries."""
    if not (type(horizon) is int and horizon >= 0):
        raise HorizonError(f"horizon must be a non-negative int, got {horizon!r}")
    depth = rollback_depth(heights, start, auth_cmds, pred_cmds, max_step, sub)
    if depth > horizon:
        raise HorizonError(f"rollback depth {depth} exceeds horizon {horizon} — misprediction beyond the window")
    return _CP.reconstruct(heights, start, auth_cmds, pred_cmds, max_step, sub)


def worst_case_window(horizon):
    """The certified worst-case reconcile latency: an admitted correction rolls back at most `horizon`
    boundaries. The rollback horizon as a hard limit."""
    return horizon


def horizon_digest(name, depth, verdict):
    """URDRLAT1 canon — SHA-256(MAGIC | name | depth | verdict). Binds the rollback depth and the admit/refuse
    verdict, so a changed misprediction or a moved horizon moves it."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|depth:{depth}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4
_START = (2, 8)


def _flat16():
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


# auth is a 4-command east glide; the predictions diverge at different boundaries, giving different depths.
_AUTH = "eeee"
_SCENES = {
    "correct": ("eeee", 5),      # pred == auth -> depth 0, admitted under horizon 5
    "recent": ("eeen", 5),       # diverges at the LAST boundary -> shallow depth, admitted
    "deep": ("neee", 2),         # diverges at the FIRST boundary -> deep depth, REFUSED under horizon 2
}
SCENES = ("correct", "recent", "deep")


def scene_case(name):
    """(depth, verdict) for a named scenario — verdict is WARD-OK-analog 'ADMIT' or 'HORIZON-REFUSE'."""
    fld = _flat16()
    pred, hz = _SCENES[name]
    depth = rollback_depth(fld, _START, _AUTH, pred, _MS, _SUB)
    try:
        admit_reconcile(fld, _START, _AUTH, pred, _MS, _SUB, hz)
        verdict = "ADMIT"
    except HorizonError:
        verdict = "HORIZON-REFUSE"
    return depth, verdict


def scene_result(name):
    depth, verdict = scene_case(name)
    return horizon_digest(name, depth, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_horizon.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise HorizonError(f"no golden named {name!r}")
