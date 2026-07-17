# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fpface — the FIXED-POINT facing seam (T3.15, Slice 4a of FPS-over-terrain): the exact-integer terrain
facing lifts into the fpquat Q32.32 rotation regime — EXACTLY at the cardinals, rounding between them.

This is where the exact-integer terrain movement stack (`stance`/`drive`/`traj`/`gaze`, whose pose axis
`facing ∈ {N,E,S,W}` is a discrete integer) meets the frozen fixed-point ROTATION regime (`fpquat`,
Stage 2 — Hamilton products + `vrotate`, reproducibility-by-frozen-rounding). It is the FIRST terrain
module deliberately NOT division-free: it consumes `fpquat`'s `_rdiv` rounding on purpose — that IS the
regime change the whole FPS arc has been building toward.

THE EXACT EMBEDDING (MEASURED). The four cardinal facings lift to cardinal yaw quaternions built with NO
trigonometry — the 90°/270° component is `fpquat.rsqrt(2·ONE)` (√2/2 from the frozen integer isqrt) —
and rotating the reference forward `(ONE,0,0)` by each lands on the EXACT cardinal direction vector with
ZERO ulp error, even though the quaternion carries a rounded √2/2 component. The whole cyclic facing
group (E→N→W→S→E under a 90° yaw) permutes exactly. So the discrete facing is an EXACT sub-lattice of the
fixed-point rotation: the two arcs meet with no loss at the cardinals, and the exactness is ROBUST — it
does not depend on the precise √2/2 value (a cardinal axis yawed 90° snaps to the permuted axis).

MOUSE-LOOK (the honest boundary). BETWEEN cardinals the rotation ROUNDS: an intermediate orientation
(`qnlerp`, trig-free) rotates forward to a continuous, rounded direction — NOT a cardinal `±ONE` axis. It
is deterministic and bit-reproducible (frozen rounding), so MEASURED-reproducible, but NO LONGER
exact-integer. And under ACCUMULATION rounding drifts: composing a rotation with itself diverges from the
true multiple by a bounded but non-zero ulp count — exactly why `fppose` renormalizes per compose.
Continuous orientation is the DECLARED model; the reproducible bytes are measured; exactness holds only
on the cardinal lattice.

GRADE. The cardinal lift + cyclic-group exactness are MEASURED (exact, 0 ulp, a defect diverges). The
mouse-look intermediate is MEASURED-reproducible (deterministic ×2) but DECLARED-continuous (it rounds).
`does_not_show`: exactness under ACCUMULATION (composition drifts — bounded, normalize-managed, NOT
claimed exact); trigonometry / angles (the seam is trig-free, on `rsqrt`/`qnlerp`); the continuous
capsule POSE (position + capsule-vs-terrain collision — the `fppose` seam, Slice 4b); any real-time /
animation claim. Refusals typed `FACE-REFUSE`."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRFACE1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _p in (_HERE, _os.path.join(_os.path.dirname(_HERE), "frontfps"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import fpquat as _FQ                                              # the Q32.32 rotation substrate (Stage 2)
from field import ONE                                            # the frozen radix (2^32)

_FACE = {"N": 0, "E": 1, "S": 2, "W": 3}
FORWARD = (ONE, 0, 0)                            # reference forward = E on the ground plane; up = +y
R2 = _FQ.rsqrt(2 * ONE)                          # √2/2 in Q32.32 via the frozen integer isqrt — NO trig

# facing index -> exact cardinal direction vector (grid (x,y) -> world (x, up=y, z=grid-y))
FACING_VEC = {0: (0, 0, -ONE), 1: (ONE, 0, 0), 2: (0, 0, ONE), 3: (-ONE, 0, 0)}
# facing index -> cardinal yaw quaternion rotating FORWARD (E) onto that facing (0/90/180/270°, no trig)
FACING_QUAT = {1: (ONE, 0, 0, 0), 0: (R2, 0, R2, 0), 3: (0, 0, ONE, 0), 2: (-R2, 0, R2, 0)}


class FaceError(Exception):
    def __init__(self, message):
        super().__init__(f"FACE-REFUSE: {message}")
        self.code = "FACE-REFUSE"


def _facing(f):
    if not (type(f) is int and f in FACING_VEC):
        raise FaceError(f"facing {f!r} is not one of 0..3 (N/E/S/W)")
    return f


def facing_quat(f):
    """The cardinal yaw quaternion that rotates FORWARD (E) onto facing `f` — trig-free."""
    return FACING_QUAT[_facing(f)]


def facing_vec(f):
    """The exact cardinal direction vector for facing `f` (a rounding-free ±ONE axis)."""
    return FACING_VEC[_facing(f)]


def lift(f):
    """Lift the discrete facing into the fixed-point rotation: rotate FORWARD by the facing's cardinal
    yaw quaternion. EQUALS `facing_vec(f)` EXACTLY (0 ulp) — the exact embedding at the cardinals."""
    return _FQ.vrotate(_FQ.qnormalize(facing_quat(f)), FORWARD)


def aim(t):
    """A mouse-look orientation between E (t=0) and N (t=ONE): the shortest-path normalized lerp of the
    two cardinal quaternions — trig-free (nlerp needs no angles). BETWEEN the cardinals it ROUNDS."""
    return _FQ.qnlerp(FACING_QUAT[1], FACING_QUAT[0], t)


def look(t):
    """The forward vector under mouse-look orientation aim(t): a continuous, rounded direction for
    0 < t < ONE (not a cardinal axis) — the fixed-point regime past the exact lattice."""
    return _FQ.vrotate(aim(t), FORWARD)


def lift_is_exact():
    """The MEASURED claim: every cardinal facing lifts to its exact direction vector, 0 ulp."""
    return all(lift(f) == facing_vec(f) for f in range(4))


def cyclic_is_exact():
    """The cyclic facing group E→N→W→S→E under a 90° yaw permutes the direction vectors exactly."""
    q90 = _FQ.qnormalize(FACING_QUAT[0])
    order = [1, 0, 3, 2]                          # E, N, W, S
    return all(_FQ.vrotate(q90, FACING_VEC[order[i]]) == FACING_VEC[order[(i + 1) % 4]]
               for i in range(4))


def compose_drift():
    """The honest boundary, made concrete. Composing a NON-cardinal (~45°) mouse-look rotation with
    itself eight times is a full turn, but rounding makes the forward vector DRIFT from its exact start
    by a bounded, NON-zero, DETERMINISTIC ulp count — exactness does not survive accumulation (the
    cardinal `q90^4` happens to be exact because 90° composes through 180° exactly; a non-cardinal step
    does not). This is why `fppose` renormalizes per compose. Returns the drift vector (reproducible)."""
    a45 = aim(ONE // 2)
    acc = a45
    for _ in range(7):                            # (~45°)^8 = a full turn (back to +E, ideally)
        acc = _FQ.qmul(acc, a45)
    got = _FQ.vrotate(acc, FORWARD)
    return tuple(g - e for g, e in zip(got, FORWARD))


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _cardinals():
    """The four exact lifts + the cyclic group — the MEASURED exact embedding."""
    rows = []
    for f in range(4):
        rows.append(("lift", f, lift(f), facing_vec(f)))
    q90 = _FQ.qnormalize(FACING_QUAT[0])
    order = [1, 0, 3, 2]
    for i in range(4):
        rows.append(("cyc", order[i], _FQ.vrotate(q90, FACING_VEC[order[i]]),
                     FACING_VEC[order[(i + 1) % 4]]))
    return rows


def _mouselook():
    """A mouse-look sweep E->N at t = 0, 1/4, 1/2, 3/4, ONE — the continuous (rounding) regime — plus
    the accumulation-drift witness (a bounded, deterministic, non-zero divergence after a full turn)."""
    rows = [("look", t, look(t)) for t in (0, ONE // 4, ONE // 2, 3 * ONE // 4, ONE)]
    rows.append(("drift", 8, compose_drift()))
    return rows


SCENES = {"cardinals": _cardinals, "mouselook": _mouselook}


def _ser(v):
    return int(v).to_bytes(8, "big", signed=True)


def scene_digest(name):
    """SHA-256(MAGIC | name | ordered scene payload). Same host, same bytes."""
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(b"|" + name.encode() + b"|")
    for row in SCENES[name]():
        h.update(str(row[:2]).encode())
        for tup in row[2:]:
            for v in tup:
                h.update(_ser(v))
    return h.hexdigest()


def scene_result(name):
    """Run a named scene → digest (deterministic; same host, same bytes)."""
    return scene_digest(name)


def golden(name):
    """The pinned digest for a named scene from `conformance_fpface.txt`."""
    with open(_os.path.join(_HERE, "conformance_fpface.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FaceError(f"no golden named {name!r}")
