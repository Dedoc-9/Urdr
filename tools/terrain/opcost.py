# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""opcost — the certified integer-work envelope (T3.29, MMO Stage H opener, URDROPC1): the DETERMINISTIC,
EXACT count of primitive integer operations each core operation performs, as a function of its input. This is
the half of a latency guarantee that CAN be certified in the byte-exact gate — wall-clock cannot (it varies by
host), but the OP-COUNT is a pure function of the input and reproduces bit-for-bit.

WHY THIS IS THE LATENCY FOUNDATION. "Latency" splits into two honestly-separable layers:
  * WORK (this module) — the exact number of integer ops an operation performs. Deterministic, exact, MEASURED,
    gate-certifiable. It BOUNDS the wall-clock: time <= op_count * (per-op cost).
  * WALL-CLOCK (`bench.py`) — the per-op cost on a NAMED host. Non-deterministic, MEASURED-on-named-host,
    never in the gate.
The latency envelope is the product: a certified op-count times a host-tagged per-op time. You cannot guarantee
what you cannot measure, and you cannot certify what is not deterministic — so the guarantee lives in the
op-count and the measurement lives in the bench.

THE COUNTS (each exact and deterministic):
  * glide_micro_count = the exact number of micro-steps a glide takes (len(micro) - 1). Data-dependent — a wall
    stops it early — but a pure function of the input; bounded above by glide_micro_bound = sum over commands of
    GAIT[gait] * sub (the no-wall worst case). count <= bound always; count < bound exactly when a wall bites
    (the bound is non-vacuous).
  * warden_edge_checks = (W-1)*H + W*(H-1) — the exact number of grid adjacencies `warden.components` examines
    (a closed form; MAX_STEP changes the union DECISIONS, never the count of CHECKS).
  * admit_substeps = sum of |dx| + |dy| over a claimed trajectory — the exact sub-step count
    `warden.admit_trajectory` performs.
  * wardhom_columns = n1, the exact number of F2 boundary columns `wardhom` builds (one per legal edge).
  * tick_envelope = the per-tick work: advance N actors by glide, admit each by warden — the quantity a latency
    budget caps and the bench times.

THE REFUSE (seeds the Stage-H hardening). `within_budget(cost, budget)` raises a typed `OPCOST-REFUSE` when the
op-count exceeds a ceiling — the FIELD-REFUSE / TOPOLOGY-REFUSE law lifted from arithmetic overflow to a work
budget: a tick that would exceed its op-budget refuses, never silently overruns.

GRADE. The op-counts (exactness, determinism, the closed forms matching the real work, count <= bound with a
non-vacuous wall witness) are MEASURED (exact, reproducible, a defect diverges). `does_not_show`: WALL-CLOCK
time (that is `bench.py`, MEASURED-on-named-host, not here); the constant factor per op-count unit (host- and
compiler-dependent); cache / memory effects; and any guarantee under an adversarial scheduler (the op-count
bounds the WORK, not the OS's willingness to run it)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDROPC1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                              # the mover (micro-step work)
import warden as _W                                              # the anti-cheat (edge / sub-step work)
import wardhom as _WH                                            # the homology bridge (F2 column work)


class OpcostError(Exception):
    def __init__(self, message):
        super().__init__(f"OPCOST-REFUSE: {message}")
        self.code = "OPCOST-REFUSE"


def _dims(field):
    if not (isinstance(field, tuple) and field and isinstance(field[0], tuple) and field[0]):
        raise OpcostError("field must be a non-empty rectangular grid")
    return len(field[0]), len(field)


def glide_micro_count(field, start, cmds, max_step, sub):
    """The EXACT number of micro-steps a glide takes — a pure function of the input (a wall stops it early).
    This IS the glide's integer-work count: each micro-step is a fixed set of exact-shift / compare ops."""
    return len(_GL.glide(field, start, cmds, max_step, sub)) - 1


def glide_micro_bound(cmds, sub):
    """The no-wall WORST-CASE micro-step count: sum over commands of GAIT[gait] * sub. glide_micro_count is
    always <= this, and strictly less exactly when a wall or edge stops the actor early."""
    total = 0
    for c in cmds:
        _dl, gait = _GL._parse(c)
        total += _GL.GAIT[gait] * sub
    return total


def warden_edge_checks(field, max_step):
    """The EXACT number of grid adjacencies `warden.components` examines: (W-1)*H + W*(H-1). A closed form,
    independent of MAX_STEP (which changes union decisions, not the count of checks)."""
    w, h = _dims(field)
    return (w - 1) * h + w * (h - 1)


def admit_substeps(cells):
    """The EXACT number of step sub-checks `warden.admit_trajectory` performs over a claimed trajectory:
    sum of |dx| + |dy| across consecutive claimed cells."""
    if not (isinstance(cells, tuple) and len(cells) >= 1):
        raise OpcostError("a claim must be a non-empty tuple of cells")
    return sum(abs(cells[i + 1][0] - cells[i][0]) + abs(cells[i + 1][1] - cells[i][1])
               for i in range(len(cells) - 1))


def wardhom_columns(field, max_step):
    """The EXACT number of F2 boundary columns `wardhom` builds for beta0: n1, the legal-edge count."""
    return _WH.counts(field, max_step)[1]


def tick_envelope(field, starts, cmds, max_step, sub):
    """The per-tick integer-work envelope: advance each actor by glide and admit each by warden. Returns the
    total EXACT op-count = sum over actors of (glide micro-steps + admit sub-steps) — the quantity a latency
    budget caps and `bench.py` times against a named host's per-op cost."""
    total = 0
    for s in starts:
        g = _GL.glide_cells(field, s, cmds, max_step, sub)
        cells = tuple((p[0] >> 32, p[1] >> 32) for p in g)
        total += glide_micro_count(field, s, cmds, max_step, sub) + admit_substeps(cells)
    return total


def within_budget(cost, budget):
    """The Stage-H work-budget law: ADMIT iff the op-count is within budget, else a typed `OPCOST-REFUSE` —
    the FIELD-REFUSE / TOPOLOGY-REFUSE discipline lifted from arithmetic overflow to a tick's work ceiling. A
    tick that would exceed its budget refuses; it never silently overruns."""
    if not (type(cost) is int and type(budget) is int and budget >= 0):
        raise OpcostError(f"cost and budget must be non-negative ints, got {cost!r}, {budget!r}")
    if cost > budget:
        raise OpcostError(f"op-count {cost} exceeds the tick budget {budget}")
    return True


def opcost_digest(name, costs):
    """URDROPC1 canon — SHA-256(MAGIC | name | the sorted op-count vector). Binds the exact work envelope, so a
    changed cost (a defect in an op, or a re-tuned scene) moves the digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}".encode())
    for k in sorted(costs):
        hh.update(f"|{k}:{costs[k]}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4


def _flat16():
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


def _wall_scene():
    """A flat row with a wall at x=8 (height 200): a glide east from (2,8) STOPS at the wall, so its
    micro-count is strictly below the no-wall bound (the bound is non-vacuous)."""
    return tuple(tuple(200 if x == 8 else 0 for x in range(16)) for _y in range(16))


def scene_costs(name):
    """The exact op-count vector for a named scenario (all deterministic integers)."""
    if name == "glide_open":
        fld = _flat16()
        cnt = glide_micro_count(fld, (2, 8), "eeee", _MS, _SUB)
        bnd = glide_micro_bound("eeee", _SUB)
        return {"micro": cnt, "bound": bnd}
    if name == "glide_wall":
        fld = _wall_scene()
        cnt = glide_micro_count(fld, (2, 8), "eeeeeeee", _MS, _SUB)
        bnd = glide_micro_bound("eeeeeeee", _SUB)
        return {"micro": cnt, "bound": bnd}
    if name == "warden_flat16":
        fld = _flat16()
        return {"edges": warden_edge_checks(fld, _MS),
                "admit": admit_substeps(((2, 8), (3, 8), (4, 8), (5, 8)))}
    if name == "wardhom_barrier8":
        return {"columns": wardhom_columns(_WH._barrier8(), _WH._MS)}
    if name == "tick3_flat16":
        return {"work": tick_envelope(_flat16(), ((2, 6), (2, 8), (2, 10)), "eeee", _MS, _SUB)}
    raise OpcostError(f"no scene named {name!r}")


SCENES = ("glide_open", "glide_wall", "warden_flat16", "wardhom_barrier8", "tick3_flat16")


def scene_result(name):
    """A named scenario's URDROPC1 digest over its exact op-count vector."""
    return opcost_digest(name, scene_costs(name))


def golden(name):
    with open(_os.path.join(_HERE, "conformance_opcost.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise OpcostError(f"no golden named {name!r}")
