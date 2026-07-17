# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""buoyancy — the MEASURED consumer of the wave seam (T3.5): exact integer flotation.

`wavefield.py` (T3.3) certifies an exact traveling height field; the WebGL2 view (T3.2) is the
DECLARED consumer that displaces a Gerstner surface from it. This is the field's OTHER consumer,
the one the wavefield docstring named and never built: a *gameplay* reader that turns the certified
sea into a certified effect. A rigid flat raft floats on the field; at each tick the raft settles to
the integer waterline `z*` where its displaced measure balances its weight (a discrete Archimedes):

    Δ(z) = Σ_cells max(0, h(x, y, t) − z)              (submerged depth summed over the footprint)
    z* = the LARGEST z with Δ(z) ≥ weight              so   Δ(z*) ≥ weight > Δ(z*+1)

Δ is non-increasing in z, so `z*` is found by integer BISECTION — division-free (`<<`, `>>`, `+`,
`−`, comparisons only; midpoint `lo + ((hi−lo) >> 1)`), so like `wavefield` the result is EXACT (no
rounding) and cross-placement is a clean next step (the winding_rs recipe). Same components + tick +
body → the same `z*` and the same URDRBUOY1 digest on every host.

GRADE. The *computation* is MEASURED: given the certified field and the (declared) buoyancy model,
`z*` reproduces bit-for-bit and a defect diverges. The buoyancy LAW itself — "displaced integer
depth balances integer weight" — is a DECLARED model (a discrete Archimedes, not a claim about real
hydrostatics), exactly as the D20–D23 budget laws are declared models walled off from the D5 ledger.
The boundary holds: the field it reads is authority, the flotation law is a model, the reproducible
`z*` is measured. Refusals are typed `BUOY-REFUSE` (empty/oversized/out-of-grid footprint, weight
non-positive or heavier than the raft can ever displace, non-integer incl. bool): refuse, never fake
a float."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRBUOY1"
FOOTPRINT_MAX = 4096
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import wavefield as _WF                                          # the certified authority (T3.3)


class BuoyError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise BuoyError("BUOY-REFUSE", message)


def _is_int(v):
    return type(v) is int                                        # bool excluded on purpose


def check_body(w, h, footprint, weight):
    """Membership in the flotation domain — every violation is a typed `BUOY-REFUSE`. The grid
    `(w, h)` itself is validated by `wavefield` (WAVE-REFUSE) when the field is built."""
    if not (isinstance(footprint, (list, tuple)) and 1 <= len(footprint) <= FOOTPRINT_MAX):
        _refuse(f"footprint must be 1..{FOOTPRINT_MAX} cells, got {footprint!r}")
    seen = set()
    for k, cell in enumerate(footprint):
        if not (isinstance(cell, tuple) and len(cell) == 2 and _is_int(cell[0]) and _is_int(cell[1])):
            _refuse(f"footprint cell {k} must be an integer (x, y), got {cell!r}")
        x, y = cell
        if not (0 <= x < w and 0 <= y < h):
            _refuse(f"footprint cell {k} = {cell!r} is outside the {w}x{h} grid")
        if cell in seen:
            _refuse(f"footprint cell {k} = {cell!r} is a duplicate")
        seen.add(cell)
    if not (_is_int(weight) and weight >= 1):
        _refuse(f"weight must be a positive int, got {weight!r}")


def _displacement(field, footprint, z):
    """Δ(z) = Σ max(0, h − z) over the footprint — the exact submerged measure at waterline z."""
    total = 0
    for (x, y) in footprint:
        d = field[y][x] - z
        if d > 0:
            total += d
    return total


def _displacement_defect(field, footprint, z):
    """THE DEFECT (non-vacuity): the UNCLAMPED sum Σ (h − z) — it lets a cell that is *above* the
    waterline subtract displacement, as if the hull sucked the raft down where it should be dry.
    Identical to `_displacement` only when every cell is submerged; on a real swell (some cells
    above z*) it moves the equilibrium, so the heave diverges from the golden."""
    total = 0
    for (x, y) in footprint:
        total += field[y][x] - z
    return total


def _bounds(field, footprint):
    """The z search range: `zlo` (every cell submerged, Δ maximal) and `zhi` (Δ = 0)."""
    hs = [field[y][x] for (x, y) in footprint]
    return min(hs) - 1, max(hs)                                  # Δ(zlo) is the max; Δ(zhi) == 0


def _settle(field, footprint, weight, disp):
    """The largest z with `disp(z) >= weight`, by division-free integer bisection. Caller guarantees
    `disp(zlo) >= weight > disp(zhi)` so the bracket is real; the midpoint is `lo + ((hi-lo) >> 1)`
    (a shift, no `/`), and Δ's monotonicity makes the search exact."""
    lo, hi = _bounds(field, footprint)                          # disp(lo) maximal, disp(hi) == 0
    hi += 1                                                       # disp(hi) is strictly < weight
    while hi - lo > 1:
        mid = lo + ((hi - lo) >> 1)
        if disp(field, footprint, mid) >= weight:
            lo = mid
        else:
            hi = mid
    return lo


def max_displacement(w, h, t, components, footprint):
    """Δ at full submersion — the most the raft can ever displace. `weight` above this cannot float."""
    _WF.check_components(w, h, t, components)
    check_body(w, h, footprint, 1)
    field = _WF.field(w, h, t, components)
    lo, _hi = _bounds(field, footprint)
    return _displacement(field, footprint, lo)


def waterline(w, h, t, components, footprint, weight, disp=_displacement):
    """The exact integer equilibrium waterline `z*` of the raft on the field at tick t. Raises
    `BUOY-REFUSE` if the raft is too heavy to float (weight exceeds max displacement)."""
    _WF.check_components(w, h, t, components)                    # WAVE-REFUSE on a bad field
    check_body(w, h, footprint, weight)                         # BUOY-REFUSE on a bad body
    field = _WF.field(w, h, t, components)
    lo, _hi = _bounds(field, footprint)
    if disp(field, footprint, lo) < weight:
        _refuse(f"weight {weight} exceeds the raft's maximum displacement "
                f"{disp(field, footprint, lo)} — it cannot float (sinks)")
    return _settle(field, footprint, weight, disp)


def submerged_profile(w, h, t, components, footprint, z):
    """The per-cell submerged depths `max(0, h − z)` at waterline z, footprint order — the wetted
    state the digest binds (so a wrong waterline OR a wrong per-cell depth both redden)."""
    _WF.check_components(w, h, t, components)
    check_body(w, h, footprint, 1)
    field = _WF.field(w, h, t, components)
    return tuple(max(0, field[y][x] - z) for (x, y) in footprint)


def heave(w, h, ticks, components, footprint, weight, disp=_displacement):
    """The raft's waterline over a sequence of ticks — its heave. EXACT and deterministic."""
    return tuple(waterline(w, h, t, components, footprint, weight, disp) for t in ticks)


def buoy_digest(name, t, zstar, profile):
    """The URDRBUOY1 canon — SHA-256(MAGIC | name,t | z* | submerged profile). Binds BOTH the
    equilibrium waterline and the wetted per-cell depths."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|t:{t}|z:{zstar}".encode())
    hh.update(b"|")
    hh.update(",".join(str(v) for v in profile).encode())
    return hh.hexdigest()


# ---- raft + scenarios (pinned by the gate) ----------------------------------------------
W = H = 24


def raft():
    """A 5×5 flat raft centred on the 24×24 field — 25 footprint cells at (10..14, 10..14)."""
    return tuple((x, y) for y in range(10, 15) for x in range(10, 15))


RAFT_WEIGHT = 100                                                # floats mid-range on every pinned tick


def raft_swell():
    return _WF.swell(), raft(), RAFT_WEIGHT


def raft_still():
    return _WF.still(), raft(), RAFT_WEIGHT


SCENES = {"raft_swell": raft_swell, "raft_still": raft_still}
SCENE_TICKS = {"raft_swell": (0, 3, 7), "raft_still": (0, 5)}


def scene_state(name, t):
    """Settle a named scene at tick t → (z*, digest). Same host, same bytes."""
    comps, fp, wt = SCENES[name]()
    z = waterline(W, H, t, comps, fp, wt)
    prof = submerged_profile(W, H, t, comps, fp, z)
    return z, buoy_digest(name, t, z, prof)


def golden(name, t):
    """The pinned digest for a named scene at tick t from `conformance_buoy.txt`."""
    key = f"{name}@{t}"
    with open(_os.path.join(_HERE, "conformance_buoy.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == key:
                    return dig
    raise BuoyError("BUOY-REFUSE", f"no golden named {key!r}")
