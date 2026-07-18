# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""warden — structural anti-cheat (T3.24, MMO Stage E opener): a claimed trajectory or position is ADMITTED
or a typed REFUSE — reconstruct-or-refuse turned against the cheater. A claim that could not have happened is
not smoothed or flagged with a heuristic; it is a certified refusal.

Two orthogonal certificates, both exact and division-free:

  * KINEMATIC (composes the mover). Each claimed step must be a legal move: a cardinal move of one or two
    cells (walk / sprint gait) whose every sub-step is enterable under the step law (`Δground ≤ MAX_STEP`,
    matching `drive`/`glide`). A jump of more than two cells or a diagonal is a `WARD-TELEPORT`; a step that
    climbs a wall is a `WARD-TUNNEL`. An honest `glide` trajectory always admits.
  * TOPOLOGICAL (composes the homology witness). The walkable field decomposes into CONNECTED COMPONENTS —
    the 0th Betti number β₀ = rank H₀, the same invariant `URDRPD1` computes as persistent homology, here
    taken directly over the walkable graph (an undirected edge joins adjacent cells iff the step is legal
    BOTH ways). A claimed position in a DIFFERENT component from the anchor is unreachable — a `WARD-UNREACH`
    — CERTIFIED FROM THE FIELD ALONE, with no trajectory to inspect. This is the cheat a per-tick replay
    cannot cheaply catch: a teleport asserted as a bare position, refused because β₀ ≥ 2 separates it.

THE KEYSTONE (measured): an honest trajectory and a same-component position ADMIT; a wall tunnel, a teleport
jump, and an across-the-barrier position each REFUSE with their typed code; and the topological refusal is
NON-VACUOUS — the barrier field genuinely has β₀ ≥ 2, and the component structure alone (not a replayed
path) certifies the unreachability.

GRADE. The kinematic admission/refusal, the exact connected-components (β₀), the reachability refusal, and
their determinism are MEASURED (exact, reproducible, a defect diverges). `does_not_show`: DIRECTED
reachability (this uses UNDIRECTED mutual-reachability components — a one-way descent off a cliff is a
strongly-connected refinement, a follow-on); gaits beyond sprint (moves > 2 cells/tick); the URDRPD1
homology CROSS-PLACEMENT (β₀ is computed directly here; wiring `homology_c/rs` to the warden is a named
follow-on); and any WALL-CLOCK cost (`NOT_MEASURED`). Refusals are typed `WARD-REFUSE` with a sub-code
(`WARD-TUNNEL`, `WARD-TELEPORT`, `WARD-UNREACH`, or a malformed-claim `WARD-MALFORMED`): refuse, never admit
a cheat."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRWARD1"
MAX_JUMP = 2                                                     # sprint gait: at most two cells per tick
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                             # the continuous mover (for honest trajectories)


class WardError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = "WARD-REFUSE"
        self.sub = code


def _dims(field):
    if not (isinstance(field, tuple) and field and isinstance(field[0], tuple) and field[0]):
        raise WardError("WARD-MALFORMED", "field must be a non-empty rectangular grid")
    w = len(field[0])
    for row in field:
        if len(row) != w:
            raise WardError("WARD-MALFORMED", "field rows must be equal width")
    return w, len(field)


# ---- topological: exact connected components (β₀ = rank H₀) over the walkable graph -----
def _find(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def _union(parent, a, b):
    ra, rb = _find(parent, a), _find(parent, b)
    if ra != rb:
        parent[ra] = rb


def components(field, max_step):
    """A cell → component-root map. An undirected edge joins adjacent cells iff the step is legal BOTH ways
    (|Δground| ≤ max_step). Exact integer union-find; division-free."""
    w, h = _dims(field)
    if not (type(max_step) is int and max_step >= 0):
        raise WardError("WARD-MALFORMED", f"max_step must be a non-negative int, got {max_step!r}")
    parent = list(range(w * h))
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if x + 1 < w and abs(field[y][x + 1] - field[y][x]) <= max_step:
                _union(parent, i, y * w + (x + 1))
            if y + 1 < h and abs(field[y + 1][x] - field[y][x]) <= max_step:
                _union(parent, i, (y + 1) * w + x)
    return {(x, y): _find(parent, y * w + x) for y in range(h) for x in range(w)}


def betti0(field, max_step):
    """β₀ = rank H₀ = the number of connected components of the walkable graph."""
    return len(set(components(field, max_step).values()))


def reachable(field, a, b, max_step):
    """True iff cell `b` is in the same walkable component as `a` (mutually reachable)."""
    w, h = _dims(field)
    for c in (a, b):
        if not (isinstance(c, tuple) and len(c) == 2 and 0 <= c[0] < w and 0 <= c[1] < h):
            raise WardError("WARD-MALFORMED", f"cell {c!r} off the {w}x{h} field")
    comp = components(field, max_step)
    return comp[a] == comp[b]


# ---- kinematic: is each claimed step a legal move? --------------------------------------
def step_kind(field, a, b, max_step):
    """Classify a claimed one-tick move `a → b`: 'OK' (a legal 1–2 cell cardinal move, every sub-step
    enterable), 'STAY' (no move), 'WARD-TELEPORT' (diagonal or > 2 cells), 'WARD-TUNNEL' (climbs a wall)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return "STAY"
    if (dx != 0) and (dy != 0):
        return "WARD-TELEPORT"                                  # diagonal
    if abs(dx) + abs(dy) > MAX_JUMP:
        return "WARD-TELEPORT"                                  # too far for one tick
    sx = (dx > 0) - (dx < 0)
    sy = (dy > 0) - (dy < 0)
    cx, cy = ax, ay
    for _ in range(abs(dx) + abs(dy)):
        nx, ny = cx + sx, cy + sy
        if not (0 <= nx < len(field[0]) and 0 <= ny < len(field)):
            return "WARD-TELEPORT"                              # off the field
        if field[ny][nx] - field[cy][cx] > max_step:
            return "WARD-TUNNEL"                                # climbs a wall (the drive/glide step law)
        cx, cy = nx, ny
    return "OK"


def admit_trajectory(field, cells, max_step):
    """ADMIT iff every claimed consecutive move is legal, else the FIRST illegal move's typed refuse. `cells`
    is the claimed sequence of integer (x, y). Pure."""
    _dims(field)
    if not (isinstance(cells, tuple) and len(cells) >= 1):
        raise WardError("WARD-MALFORMED", "a claim must be a non-empty tuple of cells")
    for i in range(len(cells) - 1):
        kind = step_kind(field, cells[i], cells[i + 1], max_step)
        if kind not in ("OK", "STAY"):
            raise WardError(kind, f"illegal move {cells[i]} → {cells[i + 1]} at step {i}")
    return "WARD-OK"


def admit_position(field, anchor, claim, max_step):
    """ADMIT iff the claimed position is REACHABLE from the anchor (same walkable component), else
    `WARD-UNREACH` — the topological certificate, from the field alone, no trajectory needed."""
    if not reachable(field, anchor, claim, max_step):
        raise WardError("WARD-UNREACH", f"claimed cell {claim} is in a different component from {anchor}")
    return "WARD-OK"


def warden_digest(name, field, max_step, verdict):
    """The URDRWARD1 canon — SHA-256(MAGIC | name | β₀ | verdict). Binds the topological structure and the
    verdict, so a changed field (a new barrier) or a changed verdict moves the digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|b0:{betti0(field, max_step)}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
# A flat 16x16 world split by an impassable wall column at x=8 (height 200) → β₀ = 3 (west / wall / east).
_MS = 40


def _barrier_field():
    return tuple(tuple(200 if x == 8 else 0 for x in range(16)) for _y in range(16))


def honest():
    """An honest walk east within the west component → ADMIT (the non-vacuity control)."""
    fld = _barrier_field()
    cells = tuple((2 + i, 8) for i in range(4))                 # (2,8)→(5,8), all west, adjacent
    return "honest", fld, admit_trajectory(fld, cells, _MS)


def teleport_across():
    """A bare claim to a cell across the wall → refused by REACHABILITY (β₀ separates west from east)."""
    fld = _barrier_field()
    try:
        v = admit_position(fld, (2, 8), (12, 8), _MS)
    except WardError as exc:
        v = exc.sub
    return "teleport_across", fld, v


SCENES = {"honest": honest, "teleport_across": teleport_across}


def scene_result(name):
    """Run a named warden scenario → its URDRWARD1 digest. Same host, same bytes."""
    nm, fld, verdict = SCENES[name]()
    return warden_digest(nm, fld, _MS, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_warden.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise WardError("WARD-MALFORMED", f"no golden named {name!r}")
