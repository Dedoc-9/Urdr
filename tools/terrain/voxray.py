# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxray (URDRVXR1) — THE GEOMETRIC ORACLE: what does this camera ray actually hit first?

WHY THIS EXISTS, AND IT IS NOT A SECOND RENDERER. `voxref` froze an observable and proved a set of
laws about it — determinism, coverage partition, order-irrelevance, two digest witnesses. Every one
of those is TRUE and every one of them still passes. They are properties of the MACHINERY. Not one
of them asks whether the machinery draws the right thing, because until a second computation exists
there is nothing to be right ABOUT.

The first reduction asked. Face culling changed `O_t` on six of the eight declared frames, and
tracing one differing pixel produced this:

    px(10,0) on `open_air`
      reference winner : voxel (2,1,10) face +z, depth 4223   <- INTERIOR, solid directly above
      culled winner    : voxel (2,1,11) face -y, depth 4275

An interior top face, with a solid voxel sitting on it, beating that voxel's own exposed face. A
ray reaching the z=2816 plane inside y in [256,512] must first pass through voxel (2,1,11), whose
-y face is present in both renders. The ordering is not merely surprising, it is impossible.

Two hypotheses were tested and one survived. The reference's `area <= 0` test SELECTS THE WRONG
WINDING — the screen-space Y inversion reverses projected orientation, so the face pointing at the
camera is discarded and the face pointing away is drawn; a single voxel viewed from six directions
confirms it. That fix is held back, uncommitted, because it does NOT account for the whole
disagreement. Interpolating 1/z instead of z — the obvious perspective-correctness hypothesis —
changes nothing: the same six frames still differ. So a second defect is real and unexplained, and
this module exists because at that point there was nothing in the tree that could say what the
right answer IS.

THE ORACLE'S AUTHORITY IS DELIBERATELY NARROW. It answers one question:

    given a camera ray, which solid voxel does it enter first, through which face, and at what t?

No triangles. No edge functions. No depth buffer. No projection matrix in the rasteriser's sense.
It shares exactly two things with `voxref`, and both are the SCENE rather than the renderer: the
world's occupancy function, and the camera basis, since a camera the two disagreed about would make
any comparison meaningless. Everything else is different machinery with different failure modes,
which is the entire point — a second implementation of the same idea would fail the same way.

IT SAMPLES WHERE THE RASTERISER SAMPLES. The rasteriser tests coverage at INTEGER pixel coordinates,
so the oracle's ray goes through the integer coordinate too, not the pixel centre. Half a pixel of
disagreement would produce differences at every silhouette and drown the real defect in artefacts of
the comparison itself.

EXACT INTEGER TRAVERSAL. `t` is carried as a rational pair and compared by cross-multiplication, so
no rounding decides which plane is crossed first. Python's integers are unbounded; there is no
tolerance anywhere in this file, and there is nothing to tune.

does_not_show: anything about performance. Anything about the observable — the oracle produces
voxel/face/t answers, never a framebuffer, and deliberately cannot be turned into one. And it does
not certify itself: `the_first_hit_is_first`, `the_hit_lies_on_its_face` and the rest are what make
it auditable, because an oracle nobody checked is an opinion.

falsifier: every invariant below is exercised against a planted defect in the selftest, and the
comparison against `voxref` is REPORTED as a measurement rather than asserted as a law — the
reference is known to be defective, so a gate row demanding agreement would be a gate row demanding
a lie.
"""
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402

MAGIC = b"URDRVXR1"

#: The face index a ray gets when it ENTERS a voxel by stepping along `axis` in direction `sign`.
#: Stepping +x enters through the voxel's -x face, and so on. Declared as data so the mapping can
#: be read rather than inferred, and so `the_face_agrees_with_the_entry_direction` can check it.
ENTRY_FACE = {(0, 1): 1, (0, -1): 0, (1, 1): 3, (1, -1): 2, (2, 1): 5, (2, -1): 4}

#: A generous cap. The world is 12^3 and a ray crosses at most 3*12 interior planes, but a ray may
#: start well outside; exceeding this is a bug, not a legal outcome, so it REFUSES rather than
#: returning "no hit" — a traversal that quietly gave up would look exactly like empty space.
MAX_STEPS = 4096


class VoxrayError(Exception):
    """VOXRAY-REFUSE — a ray or a scene this oracle will not answer for."""


def ray_for_pixel(eye, fwd, px, py):
    """The world-space direction of the ray through INTEGER pixel (px, py).

    Derived by inverting the rasteriser's own projection: it places a camera-space point at
    `cx + cr*FOCAL/cf`, `cy - cu*FOCAL/cf`, so the pixel corresponds to the camera-space direction
    `(px - cx, FOCAL, cy - py)`, which the basis rows carry back into world space. The basis is
    shared with `voxref` ON PURPOSE — it is the camera, which is part of the state, not part of
    the renderer under test.
    """
    r, f, u = VR.basis(fwd)
    a, b, c = px - VR.W // 2, VR.FOCAL, VR.H // 2 - py
    return (r[0] * a + f[0] * b + u[0] * c,
            r[1] * a + f[1] * b + u[1] * c,
            r[2] * a + f[2] * b + u[2] * c)


def _lt(p, q):
    """(num, den) < (num, den), dens strictly positive — exact, by cross-multiplication."""
    return p[0] * q[1] < q[0] * p[1]


def first_hit(eye, direction):
    """The oracle. Returns (voxel, face, (t_num, t_den)) or None if the ray leaves the world.

    `face` is None when the eye STARTS inside a solid voxel: there is no entry crossing, and
    inventing one would be the oracle guessing.
    """
    if direction == (0, 0, 0):
        raise VoxrayError("VOXRAY-REFUSE: a ray needs a direction")
    v = [eye[i] // VR.Q for i in range(3)]
    if all(0 <= v[i] < VR.N for i in range(3)) and VR.solid(*v):
        return (tuple(v), None, (0, 1))
    step, tmax, tdelta = [0, 0, 0], [None, None, None], [None, None, None]
    for i in range(3):
        d = direction[i]
        if d == 0:
            continue
        step[i] = 1 if d > 0 else -1
        boundary = (v[i] + 1) * VR.Q if d > 0 else v[i] * VR.Q
        tmax[i] = (boundary - eye[i], d) if d > 0 else (eye[i] - boundary, -d)
        tdelta[i] = (VR.Q, abs(d))
    if all(t is None for t in tmax):
        raise VoxrayError("VOXRAY-REFUSE: a direction with no non-zero component")
    for _ in range(MAX_STEPS):
        axis = None
        for i in range(3):
            if tmax[i] is None:
                continue
            if axis is None or _lt(tmax[i], tmax[axis]):
                axis = i
        if axis is None:
            return None
        t = tmax[axis]
        v[axis] += step[axis]
        tmax[axis] = (tmax[axis][0] * tdelta[axis][1] + tdelta[axis][0] * tmax[axis][1],
                      tmax[axis][1] * tdelta[axis][1])
        if 0 <= v[axis] < VR.N:
            if all(0 <= v[i] < VR.N for i in range(3)) and VR.solid(*v):
                return (tuple(v), ENTRY_FACE[(axis, step[axis])], t)
        elif (v[axis] < 0) == (step[axis] < 0):
            return None                  # left the slab on the side it was travelling towards
    raise VoxrayError("VOXRAY-REFUSE: traversal exceeded %d steps" % MAX_STEPS)


def point_at(eye, direction, t):
    """The world point at parameter t, as exact rationals (num, den) per axis."""
    n, d = t
    return tuple((eye[i] * d + direction[i] * n, d) for i in range(3))


# ---- the two windings, as DECLARED DATA rather than an uncommitted edit -----------------------
#: `voxref.FACES` as committed, and the same six faces with each corner list REVERSED. The
#: reversal is the isolated winding fix, and carrying it HERE rather than editing `voxref` is what
#: makes the whole finding reproducible from the committed tree: `voxref.render` takes a primitive
#: LIST, so both arms go through the identical rasteriser and differ in nothing but corner order.
#: Nothing in this module decides which winding is correct; the oracle does, by disagreeing.
WINDINGS = ("as-committed", "reversed")


def primitives_with(winding):
    if winding not in WINDINGS:
        raise VoxrayError("VOXRAY-REFUSE: no winding named %r" % winding)
    out = []
    for x in range(VR.N):
        for y in range(VR.N):
            for z in range(VR.N):
                if not VR.solid(x, y, z):
                    continue
                for fi, (_n, corners) in enumerate(VR.FACES):
                    if winding == "reversed":
                        corners = tuple(reversed(corners))
                    key = (((x * VR.N) + y) * VR.N + z) * 6 + fi
                    out.append((key, VR.PALETTE[fi],
                                tuple(((x + a) * VR.Q, (y + b) * VR.Q, (z + c) * VR.Q)
                                      for a, b, c in corners)))
    return out


def _unkey(k):
    fi = k % 6
    r = k // 6
    z = r % VR.N
    r //= VR.N
    return ((r // VR.N, r % VR.N, z), fi)


def render_winners(prims, eye, fwd):
    """WHICH FACE WON EACH PIXEL — the rasteriser's answer in the oracle's vocabulary.

    This is a transcription of `voxref.render`'s inner loop that keeps the winning face KEY instead
    of a colour, because "the colour buffer differs" cannot be compared against "the ray hits voxel
    V through face F". A transcription can drift from the thing it transcribes, so
    `the_winner_pass_agrees_with_the_render` renders BOTH and requires the colours to match.
    """
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    dep = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            continue
        scr = [(cx + c[0] * VR.FOCAL // c[1], cy - c[2] * VR.FOCAL // c[1], c[1]) for c in cam]
        for a, b, c2 in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c2[1] - a[1]) - (b[1] - a[1]) * (c2[0] - a[0])
            if area <= 0:
                continue
            xl = max(min(a[0], b[0], c2[0]), 0)
            xh = min(max(a[0], b[0], c2[0]), VR.W - 1)
            yl = max(min(a[1], b[1], c2[1]), 0)
            yh = min(max(a[1], b[1], c2[1]), VR.H - 1)
            if xl > xh or yl > yh:
                continue
            b0 = VR._top_left_bias(a[0], a[1], b[0], b[1])
            b1 = VR._top_left_bias(b[0], b[1], c2[0], c2[1])
            b2 = VR._top_left_bias(c2[0], c2[1], a[0], a[1])
            for py in range(yl, yh + 1):
                for px in range(xl, xh + 1):
                    w0 = VR._edge(a[0], a[1], b[0], b[1], px, py) + b0
                    w1 = VR._edge(b[0], b[1], c2[0], c2[1], px, py) + b1
                    w2 = VR._edge(c2[0], c2[1], a[0], a[1], px, py) + b2
                    if w0 < 0 or w1 < 0 or w2 < 0:
                        continue
                    d = (a[2] * w1 + b[2] * w2 + c2[2] * w0) // area
                    i = py * VR.W + px
                    if (d, pk) < (dep[i], key[i] if key[i] >= 0 else (1 << 62)):
                        dep[i] = d
                        key[i] = pk
    return key


def the_winner_pass_agrees_with_the_render():
    """The transcription above must paint the same picture `voxref.render` does, or every number
    derived from it is about a renderer nobody else runs."""
    for winding in WINDINGS:
        prims = primitives_with(winding)
        for _name, eye, fwd in VR.TRACE[:3]:
            col, _dep = VR.render(prims, eye, fwd)
            key = render_winners(prims, eye, fwd)
            for i, k in enumerate(key):
                want = VR.BACKGROUND if k < 0 else VR.PALETTE[_unkey(k)[1]]
                if col[i] != want:
                    return False
    return True


# ---- what is comparable, and what is not ------------------------------------------------------
def eye_is_inside_solid(eye):
    v = tuple(e // VR.Q for e in eye)
    return all(0 <= v[i] < VR.N for i in range(3)) and VR.solid(*v)


def comparable_frames():
    """DERIVED, not declared: the frames whose eye is OUTSIDE solid.

    When the eye starts inside occupied space `first_hit` returns that voxel with NO entry face,
    for every ray. That is not wrong — there is no entry crossing to report — but it is an answer
    in a DIFFERENT SEMANTIC DOMAIN from "which surface does the camera see", and comparing the two
    produces a 0% agreement that means nothing at all. Which definition the oracle should use for
    an interior origin is an OPEN QUESTION and the next rung's business; until it is settled, such
    frames are excluded from the correspondence figure BY DERIVATION rather than by hand.
    """
    return tuple(i for i, (_n, eye, _f) in enumerate(VR.TRACE) if not eye_is_inside_solid(eye))


#: A METADATA DEFECT, RECORDED RATHER THAN QUIETLY CORRECTED. `voxref.TRACE`'s labels were written
#: for the adversarial INTENT of each frame and never re-checked after the world was reseeded (the
#: MAGIC collision forced a rename, which changed the occupancy). The frame called `floor_flat` is
#: the one whose eye is buried in solid; the frame called `buried` is not inside anything. The
#: labels are wrong, the geometry is fine, and the fix belongs to the rung that re-freezes the
#: contract — renaming them here would move `voxref`'s pinned scene for a cosmetic reason.
TRACE_LABEL_DEFECT = ("floor_flat", "buried")


def the_trace_labels_are_known_wrong():
    """Asserted so the defect cannot be forgotten: the frame NAMED floor_flat is the buried one."""
    named = {n: eye for n, eye, _f in VR.TRACE}
    return (eye_is_inside_solid(named[TRACE_LABEL_DEFECT[0]])
            and not eye_is_inside_solid(named[TRACE_LABEL_DEFECT[1]]))


# ---- the oracle's own invariants --------------------------------------------------------------
#: DECLARED — the micro-scenes. Each isolates ONE geometric question, and the single-voxel case is
#: the one that caught the winding defect, so the suite starts from what already worked.
def _probe_rays():
    """A spread of (eye, direction) with hand-checkable answers, plus the declared trace's rays."""
    out = []
    for fwd in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (2, 1, -1), (-1, 2, -1)):
        for name, eye, f in VR.TRACE:
            for px, py in ((0, 0), (VR.W // 2, VR.H // 2), (VR.W - 1, VR.H - 1), (10, 0), (33, 41)):
                out.append((eye, ray_for_pixel(eye, f, px, py)))
        break
    for name, eye, f in VR.TRACE:
        for px in range(0, VR.W, 17):
            for py in range(0, VR.H, 13):
                out.append((eye, ray_for_pixel(eye, f, px, py)))
    return out


def the_first_hit_is_first():
    """NO SOLID VOXEL IS INTERSECTED AT A SMALLER t THAN THE ONE REPORTED.

    Checked by an INDEPENDENT method: march the ray in fine sub-steps and confirm that every solid
    voxel sampled before the reported t is the reported voxel itself. Sampling can miss a thin
    sliver, so this is a one-directional check and says so — it can catch a hit that is too LATE,
    which is the failure mode that matters here.
    """
    for eye, d in _probe_rays()[:400]:
        hit = first_hit(eye, d)
        if hit is None:
            continue
        vox, _face, (tn, td) = hit
        for k in range(1, 64):
            n = tn * k
            den = td * 64
            p = [(eye[i] * den + d[i] * n) // den for i in range(3)]
            v = tuple(p[i] // VR.Q for i in range(3))
            if all(0 <= v[i] < VR.N for i in range(3)) and VR.solid(*v) and v != vox:
                return False
    return True


def the_hit_lies_on_its_face():
    """The reported point is ON the reported face's plane, and inside the voxel on the other axes."""
    for eye, d in _probe_rays()[:400]:
        hit = first_hit(eye, d)
        if hit is None or hit[1] is None:
            continue
        vox, face, t = hit
        axis = face // 2
        pt = point_at(eye, d, t)
        num, den = pt[axis]
        want = (vox[axis] + (1 if face % 2 == 0 else 0)) * VR.Q
        if num != want * den:
            return False
        for i in range(3):
            if i == axis:
                continue
            n2, d2 = pt[i]
            if not (vox[i] * VR.Q * d2 <= n2 <= (vox[i] + 1) * VR.Q * d2):
                return False
    return True


def the_face_agrees_with_the_entry_direction():
    """A ray entering through a face must be travelling INTO it: dot(direction, normal) < 0."""
    for eye, d in _probe_rays()[:400]:
        hit = first_hit(eye, d)
        if hit is None or hit[1] is None:
            continue
        n = VR.FACES[hit[1]][0]
        if d[0] * n[0] + d[1] * n[1] + d[2] * n[2] >= 0:
            return False
    return True


def a_miss_really_traverses_nothing():
    """When the oracle reports no hit, fine sampling along the ray must find no solid voxel."""
    misses = 0
    for eye, d in _probe_rays()[:400]:
        if first_hit(eye, d) is not None:
            continue
        misses += 1
        for k in range(1, 400):
            p = [eye[i] + d[i] * k * VR.Q // (abs(d[0]) + abs(d[1]) + abs(d[2]) + 1)
                 for i in range(3)]
            v = tuple(p[i] // VR.Q for i in range(3))
            if all(0 <= v[i] < VR.N for i in range(3)) and VR.solid(*v):
                return False
    return misses > 0


def a_started_inside_voxel_has_no_entry_face():
    """Starting inside solid is a legal answer with NO face — the oracle does not invent one."""
    for x in range(VR.N):
        for y in range(VR.N):
            for z in range(VR.N):
                if VR.solid(x, y, z):
                    eye = (x * VR.Q + VR.Q // 2, y * VR.Q + VR.Q // 2, z * VR.Q + VR.Q // 2)
                    v, f, t = first_hit(eye, (1, 0, 0))
                    return v == (x, y, z) and f is None and t == (0, 1)
    return False


def a_zero_direction_refuses():
    try:
        first_hit((0, 0, 0), (0, 0, 0))
    except VoxrayError:
        return True
    return False


def the_probe_set_is_not_vacuous():
    """Both polarities: the probes must produce hits AND misses, or the invariants prove nothing."""
    hits = misses = 0
    for eye, d in _probe_rays()[:400]:
        if first_hit(eye, d) is None:
            misses += 1
        else:
            hits += 1
    return hits > 0 and misses > 0


# ---- what the oracle says about the reference -------------------------------------------------
#: THE COUNTEREXAMPLE THE CULLING RUNG PRODUCED, carried as data so the answer is checkable rather
#: than narrated. frame index into VR.TRACE, pixel, and what the reference's two arms each claimed.
COUNTEREXAMPLE = (4, (10, 0), ((2, 1, 10), 4), ((2, 1, 11), 3))


def counterexample_verdict():
    """What does the oracle say the ray at the disputed pixel actually hits first?"""
    frame, (px, py), _naive, _culled = COUNTEREXAMPLE
    _name, eye, fwd = VR.TRACE[frame]
    return first_hit(eye, ray_for_pixel(eye, fwd, px, py))


def told():
    hit = counterexample_verdict()
    if hit is None:
        return "the disputed ray hits nothing"
    vox, face, (n, d) = hit
    return ("the disputed ray first enters voxel %s through face %s at t = %d/%d; the reference's "
            "unculled arm claimed %s face %d and its culled arm claimed %s face %d"
            % (vox, face, n, d, COUNTEREXAMPLE[2][0], COUNTEREXAMPLE[2][1],
               COUNTEREXAMPLE[3][0], COUNTEREXAMPLE[3][1]))


# ---- the strongest law: the rays INVERT the projection ----------------------------------------
def round_trip_profile():
    """The exact distribution of (dx, dy) when a pixel's ray is projected back to a pixel.

    DERIVED over every pixel of every declared frame, not sampled.
    """
    prof = {}
    for _name, eye, fwd in VR.TRACE:
        r, f, u = VR.basis(fwd)
        cx, cy = VR.W // 2, VR.H // 2
        for py in range(VR.H):
            for px in range(VR.W):
                d = ray_for_pixel(eye, fwd, px, py)
                cr = (r[0] * d[0] + r[1] * d[1] + r[2] * d[2]) >> 16
                cf = (f[0] * d[0] + f[1] * d[1] + f[2] * d[2]) >> 16
                cu = (u[0] * d[0] + u[1] * d[1] + u[2] * d[2]) >> 16
                if cf <= 0:
                    prof["degenerate"] = prof.get("degenerate", 0) + 1
                    continue
                k = (cx + cr * VR.FOCAL // cf - px, cy - cu * VR.FOCAL // cf - py)
                prof[k] = prof.get(k, 0) + 1
    return tuple(sorted(prof.items(), key=lambda kv: (str(kv[0]))))


def the_rays_invert_the_projection_to_within_one_pixel():
    """THE RAY FOR A PIXEL PROJECTS BACK TO WITHIN ONE PIXEL OF ITSELF — measured, not assumed.

    This is what separates "the oracle has plausible rays" from "the oracle and the rasteriser look
    through the same camera". Without it, a disagreement could always be a disagreement about where
    pixel (10, 0) points and every finding downstream would be worthless.

    IT IS NOT EXACT, AND THE FIRST VERSION OF THIS LAW ASSERTED THAT IT WAS. Composing the Q16
    basis with two floor divisions is not an involution: 70.15% of pixel-rays return exactly, and
    the rest land one pixel away, systematically at (-1, +1), (0, +1) or (-1, 0) — the signature of
    `//` truncating toward negative infinity rather than of anything geometric. The bound is one
    pixel and it is checked as one pixel.

    WHAT THAT COSTS, SAID PLAINLY AND NOT BURIED: up to a pixel of offset between where the oracle
    aims and where the rasteriser samples is folded into every correspondence figure this module
    reports. The residue is therefore an UPPER BOUND on the reference's defect, never a measurement
    of it, and separating the two is the next rung's work rather than a caveat to be waved at.
    """
    for k, _n in round_trip_profile():
        if k == "degenerate":
            return False
        if abs(k[0]) > 1 or abs(k[1]) > 1:
            return False
    return True


def the_round_trip_is_mostly_exact():
    """NON-VACUITY: a law that allowed a pixel of slop would pass on rays that were merely close.
    A clear majority must return EXACTLY, or the coupling is looser than the prose claims."""
    prof = dict(round_trip_profile())
    tot = sum(prof.values())
    return tot > 0 and prof.get((0, 0), 0) * 2 > tot


def a_shifted_ray_fails_the_inversion():
    """The law must BITE: a ray built for the neighbouring pixel must not project back to this one."""
    _name, eye, fwd = VR.TRACE[4]
    r, f, u = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    d = ray_for_pixel(eye, fwd, 31, 25)
    cr = (r[0] * d[0] + r[1] * d[1] + r[2] * d[2]) >> 16
    cf = (f[0] * d[0] + f[1] * d[1] + f[2] * d[2]) >> 16
    return cf > 0 and cx + cr * VR.FOCAL // cf != 32


# ---- the correspondence record ----------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-oracle.txt")

#: The comparison classes, declared and mutually exclusive. A pixel falls in exactly one.
CLASSES = ("agree", "same_voxel_other_face", "other_voxel",
           "ref_empty_oracle_hit", "ref_drew_oracle_miss", "both_empty")


def compare_frame(winding, frame):
    """Classify every pixel of one frame under one winding. Returns a dict over CLASSES."""
    _name, eye, fwd = VR.TRACE[frame]
    key = render_winners(primitives_with(winding), eye, fwd)
    out = dict.fromkeys(CLASSES, 0)
    for py in range(VR.H):
        for px in range(VR.W):
            i = py * VR.W + px
            hit = first_hit(eye, ray_for_pixel(eye, fwd, px, py))
            if key[i] < 0:
                out["both_empty" if hit is None else "ref_empty_oracle_hit"] += 1
                continue
            if hit is None:
                out["ref_drew_oracle_miss"] += 1
                continue
            rv, rf = _unkey(key[i])
            if rv == hit[0] and rf == hit[1]:
                out["agree"] += 1
            elif rv == hit[0]:
                out["same_voxel_other_face"] += 1
            else:
                out["other_voxel"] += 1
    return out


def generate():
    rows = ["# URDRVXR1 oracle correspondence — one row per (winding, frame), emitted by",
            "# voxray.generate(), committed as an artifact, re-derived by the gate.",
            "# columns: winding frame name " + " ".join(CLASSES),
            "# world %s" % VR.world_digest(),
            "# NOT a certification: the reference is KNOWN defective and these numbers measure",
            "# how defective. Nothing here asserts that agreement ought to be high."]
    for winding in WINDINGS:
        for frame, (name, _e, _f) in enumerate(VR.TRACE):
            c = compare_frame(winding, frame)
            rows.append("%s %d %s %s" % (winding, frame, name,
                                         " ".join(str(c[k]) for k in CLASSES)))
    return "\n".join(rows) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if len(f) != 3 + len(CLASSES):
            raise VoxrayError("VOXRAY-REFUSE: a row with %d fields" % len(f))
        counts = dict(zip(CLASSES, (int(v) for v in f[3:])))
        if sum(counts.values()) != VR.W * VR.H:
            raise VoxrayError("VOXRAY-REFUSE: a row whose classes do not sum to the framebuffer")
        rows.append((f[0], int(f[1]), f[2], counts))
    if world is None:
        raise VoxrayError("VOXRAY-REFUSE: the record names no world digest")
    if not rows:
        raise VoxrayError("VOXRAY-REFUSE: the record has no rows")
    return world, rows


def correspondence(winding, rows=None):
    """Agreement over the COMPARABLE frames only, as (agreeing, comparable, percent).

    `both_empty` counts as agreement: the oracle finding nothing and the rasteriser drawing
    nothing is a correspondence, not an absence of one.
    """
    if rows is None:
        _w, rows = parse()
    ok = tot = 0
    comp = set(comparable_frames())
    for w, frame, _n, c in rows:
        if w != winding or frame not in comp:
            continue
        ok += c["agree"] + c["both_empty"]
        tot += sum(c.values())
    if tot == 0:
        raise VoxrayError("VOXRAY-REFUSE: no comparable frames")
    return ok, tot, 100.0 * ok / tot


# ---- the record's laws ------------------------------------------------------------------------
def the_record_is_exactly_the_declared_grid():
    _w, rows = parse()
    want = [(w, i) for w in WINDINGS for i in range(len(VR.TRACE))]
    return [(w, i) for w, i, _n, _c in rows] == want


def the_record_names_this_world():
    world, _rows = parse()
    return world == VR.world_digest()


#: The frame the gate re-renders and re-rays in full to bind the record to the live code.
BIND_FRAME = 4


def the_record_is_bound_to_the_live_code():
    """One whole frame, both windings, recomputed every gate run and matched against the record."""
    _w, rows = parse()
    for winding in WINDINGS:
        want = next(c for w, i, _n, c in rows if w == winding and i == BIND_FRAME)
        if compare_frame(winding, BIND_FRAME) != want:
            return False
    return True


def the_winding_reversal_improves_correspondence():
    """REPORTED AS A LAW ONLY IN ITS DIRECTION, never in its size.

    The committed winding is worse than its reversal. That is the isolated finding, and it is the
    one thing about the comparison that is safe to assert: it does not claim the reversal is
    CORRECT, only that the reference as committed is further from geometric truth than a six-line
    change makes it.
    """
    return correspondence("reversed")[2] > correspondence("as-committed")[2]


def a_tampered_row_refuses():
    text = _read().replace("as-committed 0 ", "as-committed 0 999999 ", 1)
    try:
        parse(text)
    except VoxrayError:
        return True
    return False


def told():
    a_ok, a_tot, a_pc = correspondence("as-committed")
    r_ok, r_tot, r_pc = correspondence("reversed")
    hit = counterexample_verdict()
    vox, face = (hit[0], hit[1]) if hit else (None, None)
    return ("reference/oracle correspondence over the %d comparable declared frames: "
            "as-committed %.1f%% (%d/%d), reversed-winding %.1f%% (%d/%d), residue %.1f%%; the "
            "disputed pixel's ray first enters voxel %s through face %s, which is NEITHER arm"
            % (len(comparable_frames()), a_pc, a_ok, a_tot, r_pc, r_ok, r_tot, 100.0 - r_pc,
               vox, face))


def scene_case(name):
    if name == "oracle":
        rows = []
        for eye, d in _probe_rays()[:120]:
            rows.append((eye, d, first_hit(eye, d)))
        return repr(rows)
    if name == "counterexample":
        return repr((COUNTEREXAMPLE, counterexample_verdict()))
    if name == "correspondence":
        _w, rows = parse()
        return repr((rows, comparable_frames(), correspondence("as-committed"),
                     correspondence("reversed"), TRACE_LABEL_DEFECT))
    raise VoxrayError("VOXRAY-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxray.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxrayError("VOXRAY-REFUSE: no golden named %r" % name)
