# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""vantage — THE FIRST-PERSON FRAME, AND THE EYE IS TAKEN RATHER THAN DERIVED (URDRVAN1).

`worldbasis` built an exact integer camera two rungs ago and NOTHING HAS EVER CALLED IT. A search
of the tree for `camera_project` outside the module that defines it returns nothing: orthogonality
proved, the scale proved to cancel, the horizon computed — and no frame. An edge nobody can break
is an edge nobody has evidence for, and a camera nobody calls is the same claim one layer up. This
module is the caller, and calling it immediately surfaced two things nothing else could.

THE EYE IS TAKEN FROM THE TICK, NEVER RE-DERIVED FROM THE TERRAIN, and this is the whole point of
the rung rather than an implementation detail. An eye that computed its own height from the
heightfield would agree with the authority EXACTLY while the actor is standing — both put the eye
one head above the ground — and would diverge the instant the actor left it. The defect is
invisible until someone jumps. It is the steering-witness shape from `stride` arriving at the
camera, and it is guarded the same two ways: STRUCTURALLY, because `eye_of` takes a POSITION and
its signature cannot receive a heightfield; and OPERATIONALLY, because a deriving eye is built here
and shown to produce identical frames on grounded ticks and different ones in the air.

THE CYCLE CLOSES IN PIXELS. `contact.run_cycle` closes on the ground it left, so a frame rendered
before the jump and a frame rendered after the landing must be BIT-IDENTICAL — not similar, equal.
That is an end-to-end certificate over authored world -> 3D tick -> eye -> camera -> rasterizer,
and every stage is exact integer arithmetic, so it either holds exactly or something moved.

AND THE VERTICAL EXAGGERATION WAS NEVER DECLARED BY ANYONE. `worldbasis.SCALE` says ONE world unit
per terrain cell. `heightfield.island` generates heights over a range of 420 across a 64-cell span.
Nothing was wrong with either number and nothing had to reconcile them, because until now no
consumer read both — a top-down picture does not care how tall a mountain is. A first-person camera
does, and the island is 6.5 times taller than it is wide. THE NUMBER IS REPORTED AND THE ANCHOR IS
OBEYED: rescaling the world to flatter a picture would be the view editing the authority, which is
the seam `worldbasis` settled and this module is not entitled to reopen. What is added is the
measurement and the name.

NO NEAR-PLANE CLIPPING, declared rather than discovered. A triangle with any vertex behind the eye
is DROPPED WHOLE rather than clipped — `fpclip` is where clipping lives and it is not wired here.
The consequence is measured (`dropped` is a reported count, not a silence) rather than left to be
found by a hole in a frame.

GRADE (honest, D5): MEASURED — the frames are exact integers end to end, the closed cycle is
bit-identical, the deriving-eye defect is proved to be invisible while grounded and caught in the
air, the pixel classes are populated (a blank frame would satisfy any digest), and the horizon
agrees with `worldbasis.horizon_row`. DECLARED: the vertical exaggeration, which is reported and
obeyed rather than corrected. `does_not_show`: that the frame is BEAUTIFUL or even legible — it
certifies that the picture is a function of the authority and moves with it; that clipping is
handled (it is not, and the drop count says so); that this is a renderer with a budget (wall-clock
stays `bench.py`'s, counts stay here)."""
import hashlib
import os as _os
import struct as _struct
import sys as _sys
import zlib as _zlib

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "physics"),
           _os.path.join(_os.path.dirname(_HERE), "render"),
           _os.path.join(_os.path.dirname(_HERE), "netcode")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                        # noqa: E402
import heightfield as HF                                    # noqa: E402
import stride as SR                                         # noqa: E402
import worldbasis as WB                                     # noqa: E402
import pixid as PX                                          # noqa: E402
import sealframe as SF                                      # noqa: E402

MAGIC = b"URDRVAN1"

#: World units from the actor's feet to the eye. DECLARED here because nothing else had reason to
#: have an opinion, and pinned so a frame cannot move by a parameter nobody is watching.
EYE_HEIGHT = 6

#: Frame geometry. Small on purpose: this is a certificate, not a viewer.
WIDTH, HEIGHT, FOCAL = 160, 96, 96
PITCH = "level"


class VantageError(Exception):
    def __init__(self, message):
        super().__init__(f"VANTAGE-REFUSE: {message}")
        self.code = "VANTAGE-REFUSE"


# ---- the eye ----------------------------------------------------------------------------------
def eye_of(pos, eye_height=EYE_HEIGHT):
    """THE EYE, AS A PURE FUNCTION OF THE TICK'S POSITION.

    This signature is the structural half of the guard: it takes a POSITION and cannot receive a
    heightfield, so an implementation that wanted to re-derive the eye's height from the terrain
    would have to change the argument list, which is visible in a diff. A comment saying `does not
    read the terrain` is not enforcement."""
    x, y, z = pos[SR.AX_X], pos[SR.AX_Y], pos[SR.AX_Z]
    return (x, y + int(eye_height), z)


def deriving_eye(world, pos, eye_height=EYE_HEIGHT):
    """THE DEFECT, BUILT SO IT CAN BE CAUGHT. An eye that asks the terrain how high it is instead
    of asking the actor. Identical to `eye_of` for a grounded actor — both put the eye one head
    above the ground — and wrong the moment the actor leaves it. Never called by `frame`."""
    g = CT.ground_height(world["heights"], SR.cell_of(pos))
    return (pos[SR.AX_X], g + int(eye_height), pos[SR.AX_Z])


# ---- the frame ---------------------------------------------------------------------------------
def orientation(facing, pitch=PITCH):
    """World -> camera. Yaw first, then pitch; both integer, both orthogonal, and orthogonality
    survives the composition because the scales multiply."""
    if facing not in WB.YAW:
        raise VantageError(f"{facing!r} is not one of the walker's four facings "
                           f"({', '.join(sorted(WB.YAW))})")
    if pitch not in WB.PITCH:
        raise VantageError(f"{pitch!r} is not a declared pitch ({', '.join(sorted(WB.PITCH))})")
    return WB.compose(WB.PITCH[pitch][0], WB.YAW[facing])


def _terrain_primitives(heights, eye, m, w, h, focal):
    """Every terrain quad, projected. A vertex BEHIND the eye kills its triangle whole — no
    near-plane clipping, declared above and counted here."""
    n = len(heights)
    cx, cy = w // 2, h // 2
    prims, pid, dropped = [], 0, 0
    proj = {}
    for z in range(n):
        for x in range(n):
            v = (x - eye[0], heights[z][x] - eye[1], z - eye[2])
            cam_z = m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]
            proj[(x, z)] = (WB.camera_project(v, m, focal, cx, cy), cam_z)
    for z in range(n - 1):
        for x in range(n - 1):
            q = ((x, z), (x + 1, z), (x, z + 1), (x + 1, z + 1))
            for idx in ((0, 1, 2), (1, 3, 2)):
                pts = [proj[q[i]] for i in idx]
                if any(p is None for p, _d in pts):
                    dropped += 1
                    continue
                tri = tuple((p[0] * PX.SUB, p[1] * PX.SUB) for p, _d in pts)
                zs = tuple(max(1, d) for _p, d in pts)
                prims.append(tri + (zs, 1 + (heights[q[idx[0]][1]][q[idx[0]][0]] % 63), pid))
                pid += 1
    return tuple(prims), dropped


def frame(world, pos, facing="E", pitch=PITCH, w=WIDTH, h=HEIGHT, focal=FOCAL,
          eye_height=EYE_HEIGHT, eye=None):
    """ONE FIRST-PERSON FRAME. `eye` is an escape used ONLY by the falsifiers, to render the same
    world from a deliberately wrong eye and show the difference; `frame` itself never computes one
    from the terrain."""
    e = eye_of(pos, eye_height) if eye is None else eye
    m = orientation(facing, pitch)
    prims, dropped = _terrain_primitives(world["heights"], e, m, w, h, focal)
    far = max((max(p[3]) for p in prims), default=1)
    r = SF.raster_ops_culled(prims, w, h, 1, far)
    fb = r["fb"]
    owned = sum(1 for v in fb.iid if v != PX.EMPTY)
    sky = 0
    for row in range(h):
        for col in range(w):
            if fb.iid[row * w + col] == PX.EMPTY:
                sky += 1
    return {"eye": e, "facing": facing, "pitch": pitch, "w": w, "h": h,
            "primitives": len(prims), "dropped": dropped, "samples": r["samples"],
            "fragments": r["fragments"], "owned": owned, "sky": sky,
            "ground": owned, "horizon": WB.horizon_row(pitch, focal, h // 2), "fb": fb}


def frame_digest(f):
    hh = hashlib.sha256(MAGIC)
    hh.update(("%d,%d,%s,%s|" % (f["w"], f["h"], f["facing"], f["pitch"])).encode())
    hh.update(bytes(bytearray(v & 0xFF for v in f["fb"].iid)))
    hh.update(("|%d/%d/%d" % (f["owned"], f["sky"], f["dropped"])).encode())
    return hh.hexdigest()


def frame_census(f):
    """Everything a reader needs EXCEPT the framebuffer — the counts, with their denominator."""
    return {k: f[k] for k in ("primitives", "dropped", "samples", "fragments", "owned", "sky",
                              "horizon")}


# ---- the world under the camera -----------------------------------------------------------------
def demo_world(preset="island", cells=((30, 30),), T=24):
    p = getattr(HF, preset)()
    return SR.world(HF.generate(**p), cells, T=T)


_JUMP_MEMO = {}


def jump_frames(world=None, facing="E", ticks=14):
    """A STRIDE JUMP, RENDERED TICK BY TICK. The actor's Y is the tick's; the eye is the actor's;
    the frame is the eye's. Nothing in this chain asks the terrain a second time."""
    key = (facing, ticks, WIDTH, HEIGHT, FOCAL, EYE_HEIGHT, PITCH) if world is None else None
    if key is not None and key in _JUMP_MEMO:
        return _JUMP_MEMO[key]                   # deterministic inputs; the memo cannot disagree
    w = world if world is not None else demo_world()
    log = [SR.event(0, 0, 0, 0, "", 1)]
    frames_, sts, _wt = SR.simulate(w, log)
    # THE FIRST ENTRY IS THE PRE-TICK STANDING FRAME. Tick 0 applies the jump, so `frames_[0]` is
    # already airborne — the frame the cycle has to close back onto is the one BEFORE it, and
    # comparing against a post-jump frame would have been a closure test that could not close.
    start = tuple(w["pos"][0])
    out = [(CT.TERRAIN_GROUNDED, start[SR.AX_Y], frame(w, start, facing))]
    for t in range(min(ticks, len(frames_))):
        pos = frames_[t][0][:3]
        out.append((sts[t][0], pos[SR.AX_Y], frame(w, pos, facing)))
    res = tuple(out)
    if key is not None:
        _JUMP_MEMO[key] = res
    return res


# ---- the laws -----------------------------------------------------------------------------------
def the_eye_cannot_receive_a_terrain():
    """THE STRUCTURAL HALF. `eye_of` and `frame`'s eye path take a POSITION. A parameter that could
    carry a heightfield is what a re-deriving implementation would need, and it is not there."""
    import inspect
    return tuple(inspect.signature(eye_of).parameters) == ("pos", "eye_height")


def the_eye_is_taken_not_derived(world=None):
    """THE OPERATIONAL HALF, and the one that catches a real implementation.

    A deriving eye is INDISTINGUISHABLE from the honest one while the actor is grounded — both put
    the eye one head above the ground — and diverges the moment it leaves. Returns (grounded_same,
    airborne_differ, ticks_compared): the first must hold or the defect would be visible for the
    wrong reason, and the second must hold or the guard sees nothing."""
    w = world if world is not None else demo_world()
    log = [SR.event(0, 0, 0, 0, "", 1)]
    frames_, sts, _wt = SR.simulate(w, log)
    probes = [(CT.TERRAIN_GROUNDED, tuple(w["pos"][0]))]                 # the pre-jump standing tick
    probes += [(sts[t][0], frames_[t][0][:3]) for t in range(3)]         # ...and the air
    same_grounded, differ_air, n = True, False, 0
    for st, pos in probes:
        honest = frame_digest(frame(w, pos))
        derived = frame_digest(frame(w, pos, eye=deriving_eye(w, pos)))
        n += 1
        if st in CT.SUPPORTED_STATES:
            same_grounded = same_grounded and honest == derived
        elif honest != derived:
            differ_air = True
    return (same_grounded, differ_air, n)


def the_cycle_closes_in_pixels(world=None):
    """END TO END, AND EXACT. `contact`'s cycle closes on the ground it left, so a frame taken
    before the jump and a frame taken after the landing must be BIT-IDENTICAL — authored world, 3D
    tick, eye, camera and rasterizer are all exact integer arithmetic, so equality is available and
    'similar' would be an admission that something is not."""
    w = world if world is not None else demo_world()
    fr = jump_frames(w)
    first = fr[0]
    landed = [i for i, (st, _y, _f) in enumerate(fr)
              if i > 1 and st == CT.TERRAIN_GROUNDED and fr[i - 1][0] == CT.AIRBORNE]
    if not landed:
        return (False, 0)
    i = landed[0]
    return (frame_digest(first[2]) == frame_digest(fr[i][2]) and first[1] == fr[i][1], i)


def the_vertical_axis_is_visible(world=None):
    """A JUMP MOVES THE PICTURE. Over the arc the ground-pixel count must take at least two
    distinct values, or the vertical axis reaches the tick and stops there. NON-VACUITY the other
    way: a run with NO jump must leave the census CONSTANT, so the movement is the jump's and not
    the renderer's."""
    w = world if world is not None else demo_world()
    moving = {f["owned"] for _s, _y, f in jump_frames(None if world is None else w)}
    flat = [SR.simulate(w, [])[0][t][0][:3] for t in range(3)]
    digests = {frame_digest(frame(w, p)) for p in flat}
    return (len(moving) > 1, len(digests) == 1, len(flat))


def compass_probe(facing="E"):
    """A LANDMARK TO THE LEFT AND A LANDMARK TO THE RIGHT, rendered, and their screen columns
    reported. This is the probe that found the camera pointing the wrong way: `worldbasis`'s yaw
    table looked SOUTH when the walker faced north and put the actor's LEFT on the right of the
    screen for east and west, and NO existing row could see either, because a backwards look is a
    rotation and a mirror is a reflection and both satisfy `M M^T = k^2 I` exactly.

    Two spikes of DIFFERENT heights so the rasterizer's instance ids tell them apart, placed on the
    walker's declared left and right at a distance the field of view actually contains. Returns
    (left_column, right_column, centre)."""
    d = WB.walker_directions_3d()
    fwd, right = d[facing], d[WB.COMPASS_RIGHT[facing]]
    n, c = 41, 20
    field = [[10] * n for _ in range(n)]
    for sign, h in ((-1, 30), (1, 18)):                       # -1 = the actor's LEFT
        ox, oz = c + fwd[SR.AX_X] * 18 + sign * right[SR.AX_X] * 6, \
            c + fwd[SR.AX_Z] * 18 + sign * right[SR.AX_Z] * 6
        for dz in (-1, 0, 1):
            for dx in (-1, 0, 1):
                field[oz + dz][ox + dx] = h
    w = SR.world(tuple(tuple(r) for r in field), [(c, c)], T=4)
    f = frame(w, w["pos"][0], facing, "level")
    cols = {}
    for row in range(f["h"]):
        for col in range(f["w"]):
            i = f["fb"].iid[row * f["w"] + col]
            if i != PX.EMPTY:
                cols.setdefault(i, []).append(col)
    out = []
    for h in (30, 18):
        got = cols.get(1 + h % 63)
        out.append(sum(got) // len(got) if got else None)
    return (out[0], out[1], f["w"] // 2)


def the_view_agrees_with_the_compass():
    """THE END-TO-END COMPASS LAW, for all four facings. A landmark on the walker's declared LEFT
    must render LEFT of centre and one on its right must render RIGHT of centre. This is the claim
    the camera's five existing rows could not make: they checked that the matrices were orthogonal,
    that the scale cancelled, that a shear was refused, that the horizon was where it said, and
    that the four yaws had the same NAMES as the walker's facings — and a yaw named "E" pointing
    the wrong way passes every one of them."""
    for facing in sorted(WB.YAW):
        left, right, centre = compass_probe(facing)
        if left is None or right is None or not (left < centre < right):
            return False
    return True


def the_frame_is_populated(world=None):
    """L61 ON A PICTURE. A frame that is all sky or all ground would satisfy any digest assertion —
    the render arc has produced both by accident and only looking found them. Sky AND ground must
    each own pixels, and the drop count must be reported rather than silent."""
    f = jump_frames(world)[0][2] if world is None else frame(world, world["pos"][0])
    return f["sky"] > 0 and f["owned"] > 0 and f["sky"] + f["owned"] == f["w"] * f["h"]


def the_horizon_agrees_with_the_basis(pitch=PITCH):
    """The camera's horizon is `worldbasis`'s, read on the run rather than recomputed here — the
    two would otherwise be free to drift, which is the class this arc keeps closing."""
    return jump_frames()[0][2]["horizon"] == WB.horizon_row(pitch, FOCAL, HEIGHT // 2)


def vertical_exaggeration(preset="island"):
    """THE NUMBER NOBODY HAD TO RECONCILE UNTIL A CAMERA STOOD IN THE WORLD. `worldbasis.SCALE` is
    ONE world unit per terrain cell; `heightfield` generates heights over `height_scale`. Reported
    with its denominator (L44) and OBEYED rather than corrected: rescaling the world to flatter a
    picture would be the view editing the authority."""
    p = getattr(HF, preset)()
    hs = HF.generate(**p)
    lo = min(min(r) for r in hs)
    hi = max(max(r) for r in hs)
    span = (p["w"] - 1) * WB.SCALE
    return {"height_scale": p["height_scale"], "observed_low": lo, "observed_high": hi,
            "cells": p["w"], "units_per_cell": WB.SCALE, "horizontal_span": span,
            "relief": hi - lo, "relief_per_span_permille": (hi - lo) * 1000 // span}


def the_exaggeration_is_read_not_chosen():
    """Both numbers come from the modules that own them. If `worldbasis.SCALE` moved, this moves;
    nothing here carries a private copy of either."""
    v = vertical_exaggeration()
    return (v["units_per_cell"] == WB.SCALE and v["height_scale"] == HF.island()["height_scale"]
            and v["relief"] > 0 and v["relief_per_span_permille"] > 1000)


# ---- the picture ---------------------------------------------------------------------------------
def png(f):
    """The frame as PNG bytes — sky, and land shaded by the instance id the rasterizer owned."""
    w, h, fb = f["w"], f["h"], f["fb"]
    rows = bytearray()
    for row in range(h):
        rows.append(0)
        for col in range(w):
            i = fb.iid[row * w + col]
            if i == PX.EMPTY:
                rows += bytes((28, 34, 58))
                continue
            t = (i * 4) & 0xFF
            rows += bytes((60 + t // 3, 100 + t // 2, 50 + t // 4))

    def _chunk(tag, data):
        c = tag + data
        return _struct.pack(">I", len(data)) + c + _struct.pack(">I", _zlib.crc32(c) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", _struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + _chunk(b"IDAT", _zlib.compress(bytes(rows), 9))
            + _chunk(b"IEND", b""))


# ---- scenes -------------------------------------------------------------------------------------
SCENES = ("standing", "apex", "landed", "compass", "exaggeration")


def scene_case(name):
    if name in ("standing", "apex", "landed"):
        fr = jump_frames()
        if name == "standing":
            f = fr[0][2]
        elif name == "apex":
            f = max(fr, key=lambda r: r[1])[2]
        else:
            idx = [i for i, (st, _y, _f) in enumerate(fr)
                   if i > 1 and st == CT.TERRAIN_GROUNDED and fr[i - 1][0] == CT.AIRBORNE]
            if not idx:
                raise VantageError("the jump never landed — the fixture is broken")
            f = fr[idx[0]][2]
        return "%s|%s" % (frame_digest(f), sorted(frame_census(f).items()))
    if name == "compass":
        return "|".join("%s:%s" % (fc, compass_probe(fc)) for fc in sorted(WB.YAW))
    if name == "exaggeration":
        return str(sorted(vertical_exaggeration().items()))
    raise VantageError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def vantage_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_vantage.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VantageError(f"no golden named {name!r}")


if __name__ == "__main__":
    print("exaggeration:", vertical_exaggeration())
    for st, y, f in jump_frames():
        print("%-16s y=%-4d sky=%-6d ground=%-6d dropped=%-5d %s"
              % (st, y, f["sky"], f["owned"], f["dropped"], frame_digest(f)[:12]))
    print("eye taken not derived:", the_eye_is_taken_not_derived())
    print("cycle closes in pixels:", the_cycle_closes_in_pixels())
    print("vertical axis visible:", the_vertical_axis_is_visible())
    print("compass:", the_view_agrees_with_the_compass(),
          {fc: compass_probe(fc) for fc in sorted(WB.YAW)})
    print("frame populated:", the_frame_is_populated(),
          " horizon agrees:", the_horizon_agrees_with_the_basis())
    for n in SCENES:
        print(n, scene_result(n))
    print("vantage", vantage_digest())
