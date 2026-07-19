# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""storecost — the snapshot-storage envelope (T3.35, MMO Stage H, URDRLAT4): the SPACE companion to the latency
guarantee's time bounds. The whole Stage-H arc bounded TIME exhaustively — op-counts (`opcost`), the per-tick
budget (`govern`), priority and aging (`priogov`), the rollback window (`horizon`), the composite and per-class
SLOs (`slo` / `clslo`) — but never bounded SPACE. `horizon` promised a depth-H rollback window and its own
does_not_show deferred exactly this: "the snapshot STORAGE cost of keeping H states (an operational parameter,
not certified here)." storecost certifies it: the exact bytes an H-deep rollback window costs, and a
`STORAGE-REFUSE` when that exceeds a memory budget — the space analog of `opcost.within_budget`.

WHY IT COMPLETES THE GUARANTEE. A time bound with no space bound is half a promise: you cannot retain H
snapshots you cannot afford. A byte-exact engine that guarantees a depth-H reconcile window must also guarantee
the memory that window occupies, or the latency promise silently depends on unbounded storage.

THE MEASURED CORE (exact, checked against a REAL serialization — not asserted):
  * A SNAPSHOT is the boundary state `glide` already yields: N actor poses, each `(fx, fy, ground, facing)` —
    fx/fy the Q32.32 sub-cell position, ground the floor-sampled height, facing in 0..3.
  * `serialize` is a canonical fixed-width encoding: a 4-byte actor count, then per pose 8+8+8 bytes
    (fx, fy, ground as signed big-endian int64) + 1 byte facing = 25 bytes. A field that overflows its width is
    a typed `STORAGE-REFUSE` (reconstruct-or-refuse, never a silent truncation).
  * `snapshot_bytes(n) = 4 + 25*n` is the CLOSED FORM, and the gate checks it EQUALS `len(serialize(state))`
    for real glide states over a corpus, and that `deserialize(serialize(state)) == state` BIT-FOR-BIT. The
    byte count is measured, exact, and a dropped or mis-sized field moves the length.

THE WINDOW (exact integer composition). A depth-H rollback window spans `worst_case_window(H) + 1 = H + 1`
boundary snapshots (roll back to any of boundary n-H .. n), so
    window_storage(H, n) = (H + 1) * snapshot_bytes(n).
`within_storage_budget(bytes, budget)` ADMITS iff the window fits, else `STORAGE-REFUSE`: a config whose H-deep
window would exceed its memory budget is declined, never silently allowed to grow unbounded (shrink H, reduce
N, or raise the budget until it fits — the same refuse-or-fit law `opcost`/`slo` use for work and latency).

GRADE. The snapshot byte count and its equality to a real serialization, the byte-exact serialize/deserialize
round-trip, the overflow `STORAGE-REFUSE`, the window closed form and its monotonicity, the budget
`STORAGE-REFUSE`, the tie to `horizon.worst_case_window`, and determinism are MEASURED (exact, reproducible, a
defect diverges). The RETENTION COUNT (H+1 boundary snapshots for a depth-H window) is a DECLARED buffer-sizing
policy — an operational parameter like rollback's K/H, never a semantic claim — but the arithmetic composing it
with the measured byte count is exact. `does_not_show`: WALL-CLOCK or bandwidth of writing snapshots (this is
BYTES retained, not time — `bench.py` territory, MEASURED-on-named-host); COMPRESSION or delta-encoding (this
is the raw canonical size, the honest upper bound); the FIELD's own storage (the terrain is static and shared,
not per-snapshot — until live world edits); and any guarantee under an adversarial allocator."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRLAT4"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                             # the mover (boundary poses = the snapshot state)
import horizon as _HZ                                           # the rollback window this sizes the storage for
import opcost as _OC                                            # OPCOST-REFUSE family (shared discipline)

# ---- canonical fixed-width snapshot encoding --------------------------------------------
WORD = 8                                                        # fx, fy, ground: signed big-endian int64
FACE_BYTES = 1                                                  # facing in 0..3
HEADER = 4                                                      # actor count, big-endian uint32
POSE_BYTES = 3 * WORD + FACE_BYTES                             # 25 bytes per pose


class StoreError(Exception):
    def __init__(self, message):
        super().__init__(f"STORAGE-REFUSE: {message}")
        self.code = "STORAGE-REFUSE"


def _pack_signed(v, w):
    if not (type(v) is int):
        raise StoreError(f"pose field must be an int, got {v!r}")
    if not (-(1 << (8 * w - 1)) <= v < (1 << (8 * w - 1))):
        raise StoreError(f"value {v} does not fit {w} signed bytes — refuse, never truncate")
    return (v & ((1 << (8 * w)) - 1)).to_bytes(w, "big")


def serialize(state):
    """The canonical byte encoding of a snapshot: a 4-byte actor count, then 25 bytes per pose
    (fx, fy, ground as signed int64, facing as one byte). An out-of-range field is a typed STORAGE-REFUSE."""
    if not (type(state) is tuple):
        raise StoreError("state must be a tuple of poses")
    if len(state) >= (1 << (8 * HEADER)):
        raise StoreError("too many actors for the count header")
    out = bytearray(len(state).to_bytes(HEADER, "big"))
    for pose in state:
        if not (type(pose) is tuple and len(pose) == 4):
            raise StoreError(f"pose must be (fx, fy, ground, facing), got {pose!r}")
        fx, fy, g, facing = pose
        if not (type(facing) is int and 0 <= facing <= 3):
            raise StoreError(f"facing must be 0..3, got {facing!r}")
        out += _pack_signed(fx, WORD) + _pack_signed(fy, WORD) + _pack_signed(g, WORD)
        out += facing.to_bytes(FACE_BYTES, "big")
    return bytes(out)


def deserialize(buf):
    """The inverse of `serialize` — reconstructs the pose tuple BIT-FOR-BIT. Refuses a truncated buffer."""
    if not (type(buf) is (bytes) or type(buf) is bytearray):
        raise StoreError("buffer must be bytes")
    if len(buf) < HEADER:
        raise StoreError("buffer too short for the header")
    n = int.from_bytes(buf[:HEADER], "big")
    if len(buf) != HEADER + POSE_BYTES * n:
        raise StoreError(f"buffer length {len(buf)} != header + {POSE_BYTES}*{n}")
    poses = []
    off = HEADER
    for _ in range(n):
        fx = int.from_bytes(buf[off:off + WORD], "big", signed=True); off += WORD
        fy = int.from_bytes(buf[off:off + WORD], "big", signed=True); off += WORD
        g = int.from_bytes(buf[off:off + WORD], "big", signed=True); off += WORD
        facing = buf[off]; off += FACE_BYTES
        poses.append((fx, fy, g, facing))
    return tuple(poses)


def snapshot_bytes(n_actors):
    """The EXACT serialized size of an N-actor snapshot: HEADER + POSE_BYTES * n. The closed form the gate
    checks EQUALS len(serialize(state))."""
    if not (type(n_actors) is int and n_actors >= 0):
        raise StoreError(f"n_actors must be a non-negative int, got {n_actors!r}")
    return HEADER + POSE_BYTES * n_actors


def retained_snapshots(horizon):
    """The number of boundary snapshots a depth-H rollback window retains: worst_case_window(H) + 1 = H + 1
    (roll back to any of boundary n-H .. n). DECLARED buffer-sizing policy; the byte count it multiplies is
    measured."""
    if not (type(horizon) is int and horizon >= 0):
        raise StoreError(f"horizon must be a non-negative int, got {horizon!r}")
    return _HZ.worst_case_window(horizon) + 1


def window_storage(horizon, n_actors):
    """The EXACT bytes a depth-H rollback window costs for N actors: retained_snapshots(H) * snapshot_bytes(N).
    The space envelope — monotone in both H and N."""
    return retained_snapshots(horizon) * snapshot_bytes(n_actors)


def within_storage_budget(nbytes, budget):
    """The Stage-H storage-budget law: ADMIT iff the retained window fits `budget` bytes, else a typed
    STORAGE-REFUSE — the within_budget discipline of `opcost` lifted from work to memory. A window that would
    exceed its budget refuses; it never silently grows unbounded."""
    if not (type(nbytes) is int and type(budget) is int and budget >= 0 and nbytes >= 0):
        raise StoreError(f"bytes and budget must be non-negative ints, got {nbytes!r}, {budget!r}")
    if nbytes > budget:
        raise StoreError(f"window storage {nbytes} bytes exceeds the budget {budget}")
    return True


# ---- soundness ground truth (real glide states) — used by the gate / tests ----
def boundary_state(field, starts, cmds, max_step, sub, boundary):
    """A REAL N-actor snapshot: each actor glides `cmds` from its start; the state is their poses at the given
    command boundary (clamped to the last). This is the object serialize / snapshot_bytes bind."""
    state = []
    for s in starts:
        cells = _GL.glide_cells(field, s, cmds, max_step, sub)
        state.append(cells[min(boundary, len(cells) - 1)])
    return tuple(state)


def serialize_is_exact(state):
    """True iff snapshot_bytes(N) EQUALS the real serialized length AND deserialize round-trips byte-exact —
    the byte count checked against reality, not assumed."""
    buf = serialize(state)
    return len(buf) == snapshot_bytes(len(state)) and deserialize(buf) == state


def storecost_digest(name, n_actors, horizon, snap_bytes, window_bytes, verdict):
    """URDRLAT4 canon — SHA-256(MAGIC | name | n | horizon | snapshot_bytes | window_bytes | verdict). Binds
    the whole storage envelope and its verdict, so a changed pose width, retention, or budget outcome moves
    it."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|n:{n_actors}|h:{horizon}|snap:{snap_bytes}|win:{window_bytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4
_CMDS = "eeee"


def _flat16():
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


# (n_actors, horizon, budget_bytes) -> window = (H+1) * (4 + 25*n)
_SCENES = {
    "one_h4":      (1, 4, 10000),   # window = 5 * 29  = 145  <= 10000 -> ADMIT
    "five_h8":     (5, 8, 10000),   # window = 9 * 129 = 1161 <= 10000 -> ADMIT
    "over_budget": (5, 8, 1000),    # window = 1161 > 1000            -> STORAGE-REFUSE
}
SCENES = ("one_h4", "five_h8", "over_budget")


def scene_case(name):
    """(snapshot_bytes, window_bytes, verdict) for a named config — verdict ADMIT or STORAGE-REFUSE."""
    n, hz, budget = _SCENES[name]
    snap = snapshot_bytes(n)
    win = window_storage(hz, n)
    try:
        within_storage_budget(win, budget)
        verdict = "ADMIT"
    except StoreError:
        verdict = "STORAGE-REFUSE"
    return snap, win, verdict


def scene_result(name):
    n, hz, _budget = _SCENES[name]
    snap, win, verdict = scene_case(name)
    return storecost_digest(name, n, hz, snap, win, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_storecost.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise StoreError(f"no golden named {name!r}")
