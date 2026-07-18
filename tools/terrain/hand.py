# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""hand — seamless cross-region authority handoff (T3.23, MMO Stage D opener): an actor glides across a
region boundary and authority transfers between shards WITHOUT a desync. ATOMIC, by the project's law: a
handoff is a two-field `splice` — region A glides the prefix, region B RESUMES the suffix from the boundary
pose (`splice.resume`, certified memoryless). It is seamless not because two authorities blend (that hides
float drift URDR does not have) but because the handoff pose is BIT-IDENTICAL to what a single authority
over the merged world would produce.

THE MODEL. Two shards hold fields `F_A`, `F_B` of the same world; they must have SYNCED their scalar
potential Φ in a boundary BAND `[split-band, split+band)` (a shard that has not synced is refused). The
canonical world is the merge `F_merged = F_A` west of `split`, `F_B` east of it — the two agree across the
band, so the merge is seamless. An east-crossing actor is authoritative under A up to a handoff tick `at`
somewhere in the band, then under B.

THE KEYSTONE (measured): HANDOFF EQUIVALENCE. `handoff` — glide the prefix over `F_A`, resume the suffix
over `F_B` — equals `glide` over `F_merged` BIT-FOR-BIT. The seam is provably invisible. Two dimensions the
bridge is proved across:
  * ONE POINT and MANY POINTS — a single actor and a whole batch crossing together each reconstruct exactly
    (the scale case; correctness is measured, THROUGHPUT is NOT_MEASURED).
  * LATENCY-INVARIANCE — the handoff is bit-identical for ANY handoff tick `at` within the band, so the
    bridge survives handoff latency; the actor may hand off early or late and lands on the same trajectory.
    (The correctness-under-latency is measured; the WALL-CLOCK latency of a handoff is NOT_MEASURED.)

Non-vacuity: `F_B` genuinely differs from `F_A` EAST of the band, so the handoff (which resumes over `F_B`)
diverges from a glide that stayed on `F_A` — proving B's terrain is really used, not A's. And the SEAM
AGREEMENT is load-bearing: a handoff across a band where `F_A ≠ F_B`, or at a tick outside the band, is a
typed `HAND-REFUSE` — the exactness holds only because the shards agree at the seam.

GRADE. The handoff equivalence (one point, many points, every in-band latency), the uses-B-terrain
non-vacuity, and the seam-agreement refusal are MEASURED (exact, reproducible, a defect diverges).
`does_not_show`: NON-MONOTONE boundary crossings (an actor that recrosses west of the band mid-suffix — this
certifies the east-crossing case); the network TRANSPORT of the handoff payload (who sends the boundary pose
to whom); overlapping/blended authority (rejected by construction — it imports drift); and **WALL-CLOCK
latency and per-handoff / batch THROUGHPUT are `NOT_MEASURED`** until a sealed bench (Stage H). Refusals are
typed `HAND-REFUSE` (unsynced seam, out-of-band handoff, mismatched field dims, bad split): refuse, never
blend."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRHAND1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                              # the continuous mover (T3.18)
import splice as _SP                                             # glide resumption (T3.19)


class HandError(Exception):
    def __init__(self, message):
        super().__init__(f"HAND-REFUSE: {message}")
        self.code = "HAND-REFUSE"


def _dims(field, what):
    if not (isinstance(field, tuple) and field and isinstance(field[0], tuple) and field[0]):
        raise HandError(f"{what} must be a non-empty field")
    return len(field[0]), len(field)


def _band(split, band):
    return split - band, split + band                           # [lo, hi)


def seam_ok(field_a, field_b, lo, hi):
    """The two shards agree on columns [lo, hi) across every row — the synced boundary band."""
    wa, ha = _dims(field_a, "field_a")
    wb, hb = _dims(field_b, "field_b")
    if (wa, ha) != (wb, hb):
        raise HandError(f"shards differ in size {wa}x{ha} vs {wb}x{hb}")
    lo = max(0, lo)
    hi = min(wa, hi)
    for y in range(ha):
        for x in range(lo, hi):
            if field_a[y][x] != field_b[y][x]:
                return False
    return True


def seam_digest(field_a, field_b, lo, hi):
    """SHA-256 of the shared band (both shards must agree; a mismatch means the shards desynced)."""
    _dims(field_a, "field_a")
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|seam:{lo},{hi}".encode())
    for y in range(len(field_a)):
        for x in range(max(0, lo), min(len(field_a[0]), hi)):
            hh.update(f"|{field_a[y][x]}".encode())
    return hh.hexdigest()


def merge(field_a, field_b, split):
    """The canonical merged world: `field_a` west of `split`, `field_b` at/east of it. The single-authority
    reference the handoff must reproduce."""
    wa, ha = _dims(field_a, "field_a")
    wb, hb = _dims(field_b, "field_b")
    if (wa, ha) != (wb, hb):
        raise HandError(f"shards differ in size {wa}x{ha} vs {wb}x{hb}")
    rows = []
    for y in range(ha):
        rows.append(tuple(field_a[y][x] if x < split else field_b[y][x] for x in range(wa)))
    return tuple(rows)


def merged_glide(field_a, field_b, start, cmds, max_step, sub, split):
    """The single-authority reference: a glide over the merged world `F_merged`."""
    return _GL.glide_cells(merge(field_a, field_b, split), start, cmds, max_step, sub)


def handoff(field_a, field_b, start, cmds, max_step, sub, at, split, band):
    """Atomic cross-region handoff: glide the prefix `cmds[:at]` under shard A (`field_a`), then RESUME the
    suffix `cmds[at:]` under shard B (`field_b`) from the boundary pose. Requires an INTERIOR handoff, a
    SYNCED seam band, and the handoff cell to lie IN the band. Returns the handed-off command-boundary
    trajectory — bit-identical to `merged_glide` (the seam is invisible)."""
    if not (isinstance(cmds, str) and len(cmds) >= 2):
        raise HandError(f"handoff needs a log of >= 2 commands, got {cmds!r}")
    n = len(cmds)
    if not (isinstance(at, int) and type(at) is int and 1 <= at <= n - 1):
        raise HandError(f"handoff tick must be interior 1..{n - 1}, got {at!r}")
    w, h = _dims(field_a, "field_a")
    lo, hi = _band(split, band)
    if not seam_ok(field_a, field_b, lo, hi):
        raise HandError(f"shards disagree on the seam band [{lo},{hi}) — a desynced handoff is refused")
    prefix = _GL.glide_cells(field_a, start, cmds[:at], max_step, sub)
    bx, by, _bg, bfacing = prefix[-1]
    cell_x = bx >> 32
    if not (lo <= cell_x < hi):
        raise HandError(f"handoff cell x={cell_x} is outside the seam band [{lo},{hi}) — unsound")
    suffix = _SP.resume_cells(field_b, (bx, by, bfacing), cmds[at:], max_step, sub)
    return prefix + suffix[1:]


def batch_handoff(field_a, field_b, starts, cmds, max_step, sub, at, split, band):
    """MANY POINTS: hand off a whole batch of actors (one per start) across the boundary together. Each is
    an independent atomic handoff; the tuple of results is what a scale test pins."""
    return tuple(handoff(field_a, field_b, s, cmds, max_step, sub, at, split, band) for s in starts)


def hand_digest(name, trajectory):
    """The URDRHAND1 canon — SHA-256(MAGIC | name | handed-off trajectory)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}".encode())
    for p in trajectory:
        hh.update(b"|")
        hh.update(",".join(str(int(v)) for v in p).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
# Two shards of the `blank` world synced on a band around split=8; shard B's terrain EAST of the band
# (columns >= 10) is bumped, so the merged world differs there and the handoff must use B's ground.
_MS, _SUB, _SPLIT, _BAND = 16, 4, 8, 2
_START, _CMDS, _AT = (2, 8), "eeeeeeeeeeeee", 5                  # east crossing; handoff at tick 5 (cell 7)
_STARTS = ((2, 6), (2, 8), (2, 10))                             # a 3-actor batch


def _shards():
    base = _GL._heights("blank")
    field_a = base
    field_b = tuple(tuple(v + 3 if x >= 10 else v for x, v in enumerate(row)) for row in base)
    return field_a, field_b


def one_point():
    fa, fb = _shards()
    return "one_point", handoff(fa, fb, _START, _CMDS, _MS, _SUB, _AT, _SPLIT, _BAND)


def many_points():
    fa, fb = _shards()
    trajs = batch_handoff(fa, fb, _STARTS, _CMDS, _MS, _SUB, _AT, _SPLIT, _BAND)
    flat = tuple(p for tr in trajs for p in tr)
    return "many_points", flat


SCENES = {"one_point": one_point, "many_points": many_points}


def scene_result(name):
    """Run a named handoff scenario → its URDRHAND1 digest. Same host, same bytes."""
    nm, traj = SCENES[name]()
    return hand_digest(nm, traj)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_hand.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise HandError(f"no golden named {name!r}")
