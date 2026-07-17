# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fpcap — the CAPSULE / body seam (T3.16, Slice 4b of FPS-over-terrain): the actor's capsule stands on
the certified terrain, and its collision is EXACT even in the fixed-point regime — rounding is confined
to continuous mouse-look POSING, never the body.

This is the close of the FPS arc, the position/body half of the fixed-point seam that `fpface` opened for
facing. The actor is a vertical capsule (foot → head, radius r) resting on the exact heightfield ground;
its position lifts from the terrain grid to fixed-point world coordinates EXACTLY (integers × ONE), and
its collision reuses `fppose`'s certified `_in_capsule` — an EXACT-INTEGER, DIVISION-FREE point-to-segment
test (`ap²·d·d − (ap·d)² ≤ r²·d·d`, cross-multiplication, no rounding). So the whole COLLISION stays
exact-integer in the fixed-point regime: the body does not round.

THE BODY IS EXACT (MEASURED, division-free). The capsule covers its own joints (foot/mid/head) exactly;
a point just inside the radius is covered and one just outside is not — the certificate is load-bearing,
and it never rounds (it is the same division-free integer test `fppose` proves). The actor rests foot at
the EXACT ground (`heightfield[y][x]`), and the terrain step law is `stance`'s: a neighbour cell is a WALL
iff its rise exceeds `MAX_STEP` — the capsule cannot enter it. Movement over the terrain is exact.

THE ORIENTATION ROUNDS (the honest boundary, inherited from `fpface`). POSING the capsule — pitching the
head offset by an `fpquat` rotation for mouse-look — is exact at the cardinals (upright, and a 90° pitch
lands the head on an exact axis) and ROUNDS for a non-cardinal (mouse-look) pitch. So the actor's *body*
is exact and its *continuous orientation* is the declared, reproducible-but-rounding part — the rounding
is quarantined to orientation, it never reaches the collision.

GRADE. The capsule collision + coverage certificate + the terrain rest/step law are MEASURED (exact,
division-free, a defect diverges). The posed head offset is MEASURED-exact at cardinals and
MEASURED-reproducible-but-DECLARED-continuous off them. `does_not_show`: contact RESPONSE / resolution
(this is the collision PREDICATE, not the solver — a rise > `MAX_STEP` is refused, not slid along); a
swept/continuous-time capsule (the test is per-tick static); ragdoll / IK / animation; exactness of a
non-cardinal posed capsule (it rounds — the same bounded, normalize-managed drift `fpface` names); any
real-time claim. Refusals typed `CAP-REFUSE`. The COLLISION is division-free; the POSE path delegates to
`fpquat` (which rounds) — the module straddles the regime boundary on purpose, and grades each side."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRCAP1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _p in (_HERE, _os.path.join(_os.path.dirname(_HERE), "frontfps"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import fppose as _PS                                              # the EXACT division-free capsule test
import fpquat as _FQ                                             # the Q32.32 rotation (posing rounds off-cardinal)
import stance as _ST                                             # the step law + DIRS
import heightfield as _HF                                        # the certified terrain authority
from field import ONE                                           # the frozen radix (2^32)

_R2 = _FQ.rsqrt(2 * ONE)                                         # √2/2 via the frozen isqrt — no trig


class CapError(Exception):
    def __init__(self, message):
        super().__init__(f"CAP-REFUSE: {message}")
        self.code = "CAP-REFUSE"


def _is_int(v):
    return type(v) is int                                       # bool excluded


def _pos_int(v, what):
    if not (_is_int(v) and v >= 1):
        raise CapError(f"{what} must be an int ≥ 1, got {v!r}")
    return v


def ground_at(heights, x, y):
    """The EXACT ground height under grid cell (x, y) — the heightfield authority, no rounding."""
    if not (_is_int(x) and _is_int(y) and 0 <= y < len(heights) and 0 <= x < len(heights[0])):
        raise CapError(f"cell ({x!r},{y!r}) off the grid")
    return heights[y][x]


def capsule(x, y, ground, height, r):
    """The actor's vertical capsule at grid (x, y): foot at the ground, head `height` above, radius `r`.
    Endpoints lift the integer grid coordinates into fixed-point world space EXACTLY (× ONE); world axes
    are (x = east, up = +y, z = grid-y)."""
    for v, w in ((x, "x"), (y, "y"), (ground, "ground")):
        if not _is_int(v):
            raise CapError(f"{w} must be an int, got {v!r}")
    _pos_int(height, "height")
    _pos_int(r, "r")
    foot = (x * ONE, ground * ONE, y * ONE)
    head = (x * ONE, (ground + height) * ONE, y * ONE)
    return {"a": foot, "b": head, "r": r * ONE}


def covers(cap, pt):
    """EXACT-INTEGER, DIVISION-FREE: is world point `pt` inside the capsule? Reuses `fppose._in_capsule`
    (the certified point-to-segment certificate) — never rounds, even in the fixed-point regime."""
    return _PS._in_capsule(pt, cap)


def stand(heights, x, y, height, r):
    """The actor's capsule resting on the certified terrain at grid (x, y) — foot at the exact ground."""
    return capsule(x, y, ground_at(heights, x, y), height, r)


def wall_between(heights, x, y, nx, ny, max_step):
    """`stance`'s step law on the capsule: the neighbour (nx, ny) is a WALL iff its rise exceeds MAX_STEP
    — the capsule cannot enter it. Exact-integer."""
    if not _is_int(max_step) or max_step < 0:
        raise CapError(f"max_step must be a non-negative int, got {max_step!r}")
    return ground_at(heights, nx, ny) - ground_at(heights, x, y) > max_step


def head_offset(height, pitch_quat):
    """The head offset (straight up, length `height`) POSED by a pitch rotation — the mouse-look path.
    Exact at the cardinals (upright / 90°), rounds for a non-cardinal pitch (via `fpquat.vrotate`)."""
    return _FQ.vrotate(pitch_quat, (0, height * ONE, 0))


def pitch_quat(t):
    """A trig-free pitch orientation between upright (t=0) and a 90° pitch (t=ONE) — `qnlerp`, no angles.
    The cardinals are exact; interior t is a rounded (mouse-look) pitch."""
    return _FQ.qnlerp((ONE, 0, 0, 0), _FQ.qnormalize((_R2, _R2, 0, 0)), t)


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _heights(scene):
    return _HF.scene_digest(_HF.SCENES[scene]())[1]


def _collision():
    """The EXACT capsule collision: coverage of the joints + the load-bearing radius certificate."""
    H = _heights("blank")
    cap = stand(H, 2, 8, 4, 1)
    g = ground_at(H, 2, 8)
    foot, head = cap["a"], cap["b"]
    mid = (2 * ONE, (g + 2) * ONE, 8 * ONE)
    inside = (2 * ONE, (g + 2) * ONE, 8 * ONE + (ONE - 1))       # just inside radius 1·ONE
    outside = (2 * ONE, (g + 2) * ONE, 8 * ONE + (ONE + 1))      # just outside
    return [("cover", covers(cap, foot), covers(cap, head), covers(cap, mid)),
            ("radius", covers(cap, inside), covers(cap, outside))]


def _terrain():
    """The capsule on the terrain: resting on exact ground, and stance's step law biting — at this ridge
    cell (max_step 4) the E/S neighbours are WALLS (rise > 4) and N/W are walkable, so the capsule may
    enter N/W and is refused E/S. Exact-integer."""
    H = _heights("mountains")
    x, y, ms = 2, 1, 4
    cap = stand(H, x, y, 4, 1)
    rows = [("rest", cap["a"][1], ground_at(H, x, y) * ONE)]     # foot y == ground·ONE (exact)
    for d in ("N", "E", "S", "W"):
        dx, dy = _ST.DIRS[d]
        nx, ny = x + dx, y + dy
        rows.append(("step", d, 1 if wall_between(H, x, y, nx, ny, ms) else 0))
    return rows


def _pose():
    """The head offset upright / cardinal-pitch (exact) / mouse-look pitch (rounds) — the boundary."""
    up = head_offset(4, (ONE, 0, 0, 0))
    card = head_offset(4, _FQ.qnormalize((_R2, _R2, 0, 0)))      # 90° pitch — exact axis
    mouse = head_offset(4, pitch_quat(ONE // 2))                 # ~45° — rounds
    return [("up", up), ("cardinal", card), ("mouselook", mouse)]


SCENES = {"collision": _collision, "terrain": _terrain, "pose": _pose}


def _ser(v):
    return int(v).to_bytes(8, "big", signed=True)


def scene_digest(name):
    """SHA-256(MAGIC | name | ordered scene payload). Same host, same bytes."""
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(b"|" + name.encode() + b"|")
    for row in SCENES[name]():
        for field in row:
            if isinstance(field, tuple):
                for v in field:
                    h.update(_ser(v))
            elif isinstance(field, bool):
                h.update(b"\x01" if field else b"\x00")
            elif isinstance(field, int):
                h.update(_ser(field))
            else:
                h.update(str(field).encode())
    return h.hexdigest()


def scene_result(name):
    """Run a named scene → digest (deterministic; same host, same bytes)."""
    return scene_digest(name)


def golden(name):
    """The pinned digest for a named scene from `conformance_fpcap.txt`."""
    with open(_os.path.join(_HERE, "conformance_fpcap.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CapError(f"no golden named {name!r}")
