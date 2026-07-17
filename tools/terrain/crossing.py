# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""crossing — the second MEASURED consumer of the wave seam (T3.7): exact wave-crossing timing.

`buoyancy.py` reads a FIXED cell over time (a raft bobbing in place). This reads a MOVING trajectory
through the traveling field — the other consumer the wavefield docstring named. An agent crosses the
sea in a straight line at integer velocity; at each tick it is at cell `(x0 + vx*t, y0 + vy*t)`, and
the exact integer wave height there at THAT tick is `h(x(t), y(t), t)`. The agent rides at a fixed
`clearance` above still water; it is OVERTOPPED the first tick a crest exceeds it:

    overtop(t)  iff  h(x0+vx*t, y0+vy*t, t) > clearance
    result = the FIRST t in [0, T) with overtop(t), else T  (== cleared the whole window)

Because both the agent AND the wave move, the result is a joint space-time event: freeze the wave
(evaluate every tick at t=0) and the first-overtopping tick generally changes — wave travel is
load-bearing, which the selftest pins. Everything is exact integers (multiply/compare + the
division-free wavefield), so `result` reproduces bit-for-bit on every host and cross-placement is a
clean next step (no `/`, `//`, `%`; asserted by the conformance test).

GRADE. The computation is MEASURED (`result` is exact and reproducible; a defect diverges). The
crossing MODEL — "a crest above clearance overtops a straight-line constant-velocity agent" — is a
DECLARED model, like the buoyancy law and the D20–D23 budgets: the field it reads is authority, the
model is declared, the reproducible event time is measured. Refusals are typed `CROSS-REFUSE` (zero
velocity, a path that leaves the grid, non-positive window, non-integer incl. bool): refuse, never
clamp the path or fake an event."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRCROSS1"
T_MAX = 4096
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import wavefield as _WF                                          # the certified authority (T3.3)


class CrossError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise CrossError("CROSS-REFUSE", message)


def _is_int(v):
    return type(v) is int                                        # bool excluded on purpose


def _pair(v, what):
    if not (isinstance(v, tuple) and len(v) == 2 and _is_int(v[0]) and _is_int(v[1])):
        _refuse(f"{what} must be an integer (x, y), got {v!r}")
    return v


def check_agent(w, h, ticks, components, start, vel, clearance):
    """Membership in the crossing domain — every violation is a typed `CROSS-REFUSE`. The wave grid
    `(w, h)` and the tick are validated by `wavefield`; here we validate the agent and, crucially,
    that its whole straight-line path stays inside the grid for the window (refuse, never clamp)."""
    if not (_is_int(ticks) and 1 <= ticks <= T_MAX):
        _refuse(f"window must be an int in 1..{T_MAX}, got {ticks!r}")
    x0, y0 = _pair(start, "start")
    vx, vy = _pair(vel, "velocity")
    if vx == 0 and vy == 0:
        _refuse("velocity must be non-zero — a stationary agent is not a crossing")
    if not _is_int(clearance):
        _refuse(f"clearance must be an int, got {clearance!r}")
    for t in range(ticks):
        x = x0 + vx * t
        y = y0 + vy * t
        if not (0 <= x < w and 0 <= y < h):
            _refuse(f"path leaves the {w}x{h} grid at tick {t}: cell ({x}, {y})")


def _trace(w, h, ticks, components, start, vel, frozen):
    """The exact integer wave height under the agent at each tick. `frozen=True` evaluates every
    tick at t=0 (THE DEFECT: a wave that does not travel)."""
    x0, y0 = start
    vx, vy = vel
    out = []
    for t in range(ticks):
        wt = 0 if frozen else t
        out.append(_WF.height(x0 + vx * t, y0 + vy * t, wt, components))
    return tuple(out)


def _first_overtop(trace, clearance):
    """The first tick a crest exceeds clearance, else `len(trace)` (== cleared)."""
    t = 0
    for v in trace:
        if v > clearance:
            return t
        t += 1
    return t


def crossing(w, h, ticks, components, start, vel, clearance, frozen=False):
    """The exact integer tick the agent is first overtopped, or `ticks` if it clears the window.
    `frozen=True` is the wave-does-not-travel defect."""
    _WF.check_components(w, h, ticks - 1 if ticks > 0 else 0, components)  # validate components/tick
    check_agent(w, h, ticks, components, start, vel, clearance)
    return _first_overtop(_trace(w, h, ticks, components, start, vel, frozen), clearance)


def crossing_trace(w, h, ticks, components, start, vel, clearance):
    """(result, height-trace) — the crossing event plus the per-tick heights the digest binds."""
    check_agent(w, h, ticks, components, start, vel, clearance)
    tr = _trace(w, h, ticks, components, start, vel, False)
    return _first_overtop(tr, clearance), tr


def cross_digest(name, result, trace):
    """The URDRCROSS1 canon — SHA-256(MAGIC | name | first-overtop tick | height trace). Binds BOTH
    the event tick and the wave heights the agent actually met."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|r:{result}".encode())
    hh.update(b"|")
    hh.update(",".join(str(v) for v in trace).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
W = H = 24


def ferry_clear():
    """A ferry crossing east that meets a full crest of 48 but rides exactly at the amplitude bound —
    so `h > clearance` is never true and it just clears the whole window (result == T)."""
    return (_WF.swell(), (0, 3), (1, 0), 48)


def ferry_swamped():
    """The SAME crossing at a lower clearance — the 48 crest overtops it (result < T). Clearance is
    load-bearing: the only difference from ferry_clear is how high the agent rides."""
    return (_WF.swell(), (0, 3), (1, 0), 27)


def swimmer_north():
    """A low swimmer crossing north — a TRAVELLING crest catches it partway (result < T); freezing the
    wave changes when (the selftest), so wave travel is load-bearing."""
    return (_WF.swell(), (6, 0), (0, 1), 5)


SCENES = {"ferry_clear": ferry_clear, "ferry_swamped": ferry_swamped, "swimmer_north": swimmer_north}
SCENE_TICKS = {"ferry_clear": 12, "ferry_swamped": 12, "swimmer_north": 12}


def scene_result(name):
    """Run a named crossing → (result, digest). Same host, same bytes."""
    comps, start, vel, clr = SCENES[name]()
    r, tr = crossing_trace(W, H, SCENE_TICKS[name], comps, start, vel, clr)
    return r, cross_digest(name, r, tr)


def golden(name):
    """The pinned digest for a named scene from `conformance_cross.txt`."""
    with open(_os.path.join(_HERE, "conformance_cross.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CrossError("CROSS-REFUSE", f"no golden named {name!r}")
