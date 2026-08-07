# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-render: the PRIMITIVE-ID BUFFER (URDRPID1) — a witness at pixel granularity.

`view_witness` cites the live scene digests once per VIEW. This cites per PIXEL: each
covered pixel records the `(instance, primitive)` that owns it, so the question "what
made this pixel" has an answer that can be checked rather than asserted. The buffer's
digest is a function of the geometry and the view integers alone, and the SCENE digest
it cites is a function of the geometry alone — that separation is the whole point and is
the property most easily lost.

## Ownership

Exactly `raster3d`'s rule, with the datum changed: nearest wins by exact rational
comparison, and an EXACT TIE goes to the smaller `(instance, primitive)` pair. The key
IS the written datum, which is what makes the order total ON OUTCOMES — two fragments
equal in `(depth, instance, primitive)` write identical bytes, so the residual tie is
unobservable. Ordering by anything else (submission index, a hash of the vertices) would
be deterministic without being total on what is stored, and the ambiguity would resurface
the moment two primitives shared it.

## The oracle differs in TRAVERSAL, not in arithmetic

`agrees_with_oracle` recomputes every pixel by scanning ALL primitives against ALL pixels
with no bounding box, and compares both directions: no covered pixel left empty, and no
emitted id whose primitive fails to cover its sample point. It shares `raster.edge`
deliberately — the defect class this catches is a bounding-box walk that misses cells
(`voxin` under-reported 20% exactly that way), and an oracle that reimplemented the edge
function would be testing two arithmetics instead of one traversal.

## The firewall

`scene_digest` is computed over the primitive list and the ids. It does NOT read the
resolution, the near plane, the far plane, or anything else a viewer chooses. So
perturbing a knob must move the frame digest and leave the cited scene digest fixed,
while perturbing one scene integer must move both. Stated as two directions because only
the first is the firewall; the second is what stops the firewall from being achieved by a
scene digest that ignores the scene.

## does_not_show

That the image is CORRECT, or that the ids name anything real — this records which
submitted primitive owns a pixel, not that the primitive belongs there. No shading, no
blending, no perspective (this consumes screen-space primitives, as `raster3d` does).
CROSS-PLACEMENT: URDRPID1 is a Python reference with no Rust or C99 port, so every figure
here is single-implementation. Performance at any scale: the oracle is O(pixels x
primitives) by construction and is a checker, not a path. A buffer that cites is not a
buffer that is right. `integrity != truth`.
"""
import hashlib

from raster import SUB, HALF, edge, RenderError, _top_left
from renderbound import admits, depth_intermediate_max

MAGIC = b"URDRPID1"
EMPTY = 0xFFFFFFFF                 # the sentinel; ids are refused at and above it
ID_MAX = EMPTY - 1


def _int(name, v):
    if not isinstance(v, int) or isinstance(v, bool):
        raise RenderError("PIXID-REFUSE", f"{name} must be an integer (got {v!r})")
    return v


def _check_id(name, v):
    _int(name, v)
    if v < 0 or v > ID_MAX:
        raise RenderError("PIXID-REFUSE",
                          f"{name} out of range: {v} not in [0, {ID_MAX}] "
                          f"({EMPTY:#x} is the EMPTY sentinel and may not be an id)")
    return v


def _check_primitive(p):
    """A primitive is `(v0, v1, v2, (z0,z1,z2), instance, primitive)` in SUBPIXEL screen
    coordinates. Quantization is the CALLER's declared act — a float here would give a
    float pixel in this placement and an integer one in any conforming port."""
    try:
        v0, v1, v2, zs, iid, pid = p
    except (TypeError, ValueError):
        raise RenderError("PIXID-REFUSE", f"malformed primitive: {p!r}")
    for v in (v0, v1, v2):
        if not isinstance(v, (tuple, list)) or len(v) != 2:
            raise RenderError("PIXID-REFUSE", f"vertex must be a 2-tuple: {v!r}")
        for c in v:
            _int("vertex component", c)
    if not isinstance(zs, (tuple, list)) or len(zs) != 3:
        raise RenderError("PIXID-REFUSE", f"depths must be a 3-tuple: {zs!r}")
    for z in zs:
        _int("depth", z)
    _check_id("instance", iid)
    _check_id("primitive", pid)
    return (tuple(v0), tuple(v1), tuple(v2), tuple(zs), iid, pid)


def scene_digest(primitives):
    """THE CITATION. A function of the geometry and the ids, and of NOTHING a viewer
    chooses — no resolution, no near or far plane. Order-invariant by construction
    (canonical sort), so a scene is its multiset of primitives."""
    rows = sorted(_check_primitive(p) for p in primitives)
    h = hashlib.sha256()
    h.update(b"URDRPIDSCENE1")
    h.update(len(rows).to_bytes(4, "big"))
    for (v0, v1, v2, zs, iid, pid) in rows:
        for c in (v0[0], v0[1], v1[0], v1[1], v2[0], v2[1], zs[0], zs[1], zs[2]):
            h.update(c.to_bytes(9, "big", signed=True))
        h.update(iid.to_bytes(4, "big"))
        h.update(pid.to_bytes(4, "big"))
    return h.hexdigest()


class IdFramebuffer:
    """A W x H buffer of `(instance, primitive)` ownership with an exact rational depth
    buffer. `oob` counts attempted out-of-bounds writes and must stay 0."""

    def __init__(self, w, h, znear, zfar):
        for v in (w, h, znear, zfar):
            _int("framebuffer parameter", v)
        if w <= 0 or h <= 0:
            raise RenderError("PIXID-REFUSE", f"framebuffer size out of range ({w}x{h})")
        # The i64 admission bound is READ from `renderbound`, not restated. This buffer
        # runs the same depth arithmetic rung 2 does, so it inherits the same envelope;
        # a bound written in two places is a bound that can disagree with itself.
        if not admits(w, h, znear, zfar):
            raise RenderError("PIXID-REFUSE",
                              f"depth path exceeds i64: "
                              f"{depth_intermediate_max(w, h, znear, zfar)} > {(1 << 63) - 1}")
        if w * h > (1 << 22):
            raise RenderError("PIXID-REFUSE",
                              f"allocation policy: {w}x{h} exceeds the DECLARED "
                              f"{1 << 22}-pixel limit (a policy, not a theorem)")
        self.w, self.h = w, h
        self.znear, self.zfar = znear, zfar
        self.iid = [EMPTY] * (w * h)
        self.pid = [EMPTY] * (w * h)
        self.znum = [None] * (w * h)
        self.zden = [None] * (w * h)
        self.oob = 0

    # -- ownership --------------------------------------------------------------------
    def _own(self, x, y, num, den, iid, pid):
        if not (0 <= x < self.w and 0 <= y < self.h):
            self.oob += 1
            return
        i = y * self.w + x
        cn, cd = self.znum[i], self.zden[i]
        if cn is None:
            win = True
        else:
            lhs, rhs = num * cd, cn * den
            # EXACT TIE -> the smaller written datum. The key is the id pair itself,
            # so fragments equal in the key write identical bytes and the order is
            # total on OUTCOMES rather than merely deterministic.
            win = (iid, pid) < (self.iid[i], self.pid[i]) if lhs == rhs else lhs < rhs
        if win:
            self.iid[i], self.pid[i] = iid, pid
            self.znum[i], self.zden[i] = num, den

    def draw(self, primitive):
        (x0, y0), (x1, y1), (x2, y2), (z0, z1, z2), iid, pid = _check_primitive(primitive)
        if edge(x0, y0, x1, y1, x2, y2) < 0:
            (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
            z1, z2 = z2, z1
        area = edge(x0, y0, x1, y1, x2, y2)
        if area == 0:
            return                                   # degenerate: covers no sample
        minx = max(0, min(x0, x1, x2) // SUB)
        maxx = min(self.w - 1, max(x0, x1, x2) // SUB)
        miny = max(0, min(y0, y1, y2) // SUB)
        maxy = min(self.h - 1, max(y0, y1, y2) // SUB)
        for py in range(miny, maxy + 1):
            sy = py * SUB + HALF
            for px in range(minx, maxx + 1):
                sx = px * SUB + HALF
                hit = _covers(x0, y0, x1, y1, x2, y2, sx, sy)
                if hit is None:
                    continue
                ea, eb, ec = hit
                num = eb * z0 + ec * z1 + ea * z2
                if not (self.znear * area <= num <= self.zfar * area):
                    continue
                self._own(px, py, num, area, iid, pid)

    def render(self, primitives):
        for p in primitives:
            self.draw(p)
        return self

    # -- identity ---------------------------------------------------------------------
    def serialize(self):
        out = bytearray(MAGIC)
        out += self.w.to_bytes(4, "big") + self.h.to_bytes(4, "big")
        for i in range(self.w * self.h):
            out += self.iid[i].to_bytes(4, "big") + self.pid[i].to_bytes(4, "big")
        return bytes(out)

    def digest(self):
        return hashlib.sha256(self.serialize()).hexdigest()

    def instances(self):
        return frozenset(v for v in self.iid if v != EMPTY)

    def owner(self, x, y):
        i = y * self.w + x
        return None if self.iid[i] == EMPTY else (self.iid[i], self.pid[i])


def _covers(x0, y0, x1, y1, x2, y2, sx, sy):
    """The three edge weights if the sample is inside (top-left rule), else None. The
    triangle must already be positively oriented."""
    ea = edge(x0, y0, x1, y1, sx, sy)
    eb = edge(x1, y1, x2, y2, sx, sy)
    ec = edge(x2, y2, x0, y0, sx, sy)
    for e, (ax, ay, bx, by) in ((ea, (x0, y0, x1, y1)),
                                (eb, (x1, y1, x2, y2)),
                                (ec, (x2, y2, x0, y0))):
        if e > 0:
            continue
        if e == 0 and _top_left(bx - ax, by - ay):
            continue
        return None
    return (ea, eb, ec)


# -- the witness ----------------------------------------------------------------------
def witness(primitives, w, h, znear, zfar):
    """The pixel-granularity witness: the frame digest, the SCENE digest it cites, and
    the instances actually visible. The scene digest is computed from the primitives
    alone — the view integers are passed to the framebuffer and never to the citation."""
    fb = IdFramebuffer(w, h, znear, zfar).render(primitives)
    return {"scene": scene_digest(primitives),
            "frame": fb.digest(),
            "instances": fb.instances(),
            "oob": fb.oob}


# -- the pinned scene -----------------------------------------------------------------
def _t(ax, ay, bx, by, cx, cy, zs, iid, pid):
    return ((ax * SUB, ay * SUB), (bx * SUB, by * SUB), (cx * SUB, cy * SUB), zs, iid, pid)


#: Instance 7 is a near quad (two primitives); instance 3 is a far triangle it partly
#: hides; instance 9 is BEHIND instance 7 and fully covered by it, so it must vanish
#: from the buffer while remaining in the submitted set — the proper-subset witness.
SCENE = (
    _t(1, 1, 14, 1, 1, 14, (4, 4, 4), 7, 0),
    _t(14, 1, 14, 14, 1, 14, (4, 4, 4), 7, 1),
    _t(2, 8, 13, 8, 2, 15, (9, 9, 9), 3, 0),
    _t(3, 3, 6, 3, 3, 6, (12, 12, 12), 9, 0),
)
VIEW = (16, 16, 0, 100)


# -- the laws -------------------------------------------------------------------------
def digest_is_permutation_invariant(primitives=SCENE, view=VIEW):
    """The buffer is a function of the SET of primitives. Every rotation must agree."""
    prims = list(primitives)
    base = IdFramebuffer(*view).render(prims).digest()
    for i in range(len(prims)):
        rotated = prims[i:] + prims[:i]
        if IdFramebuffer(*view).render(rotated).digest() != base:
            return False
    return True


def oracle_owner(primitives, x, y, w, h, znear, zfar):
    """Recompute one pixel's owner by scanning ALL primitives with NO bounding box —
    the traversal the rasterizer does not use."""
    sx, sy = x * SUB + HALF, y * SUB + HALF
    best = None
    for p in primitives:
        (x0, y0), (x1, y1), (x2, y2), (z0, z1, z2), iid, pid = _check_primitive(p)
        if edge(x0, y0, x1, y1, x2, y2) < 0:
            (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
            z1, z2 = z2, z1
        area = edge(x0, y0, x1, y1, x2, y2)
        if area == 0:
            continue
        hit = _covers(x0, y0, x1, y1, x2, y2, sx, sy)
        if hit is None:
            continue
        ea, eb, ec = hit
        num = eb * z0 + ec * z1 + ea * z2
        if not (znear * area <= num <= zfar * area):
            continue
        cand = (num, area, iid, pid)
        if best is None:
            best = cand
        else:
            lhs, rhs = num * best[1], best[0] * area
            if lhs < rhs or (lhs == rhs and (iid, pid) < (best[2], best[3])):
                best = cand
    return None if best is None else (best[2], best[3])


def agrees_with_oracle(primitives=SCENE, view=VIEW):
    """BOTH DIRECTIONS, EXECUTED over the pinned view rather than proved for all
    geometry: no covered pixel left empty, and no emitted id whose primitive fails to
    own its sample point."""
    w, h, znear, zfar = view
    fb = IdFramebuffer(*view).render(primitives)
    for y in range(h):
        for x in range(w):
            if fb.owner(x, y) != oracle_owner(primitives, x, y, w, h, znear, zfar):
                return False
    return True


def occlusion_only_removes(primitives=SCENE, view=VIEW):
    """`instances(buffer)` is a SUBSET of `instances(submitted)` — rasterization can
    hide an instance, never invent one."""
    submitted = frozenset(_check_primitive(p)[4] for p in primitives)
    return IdFramebuffer(*view).render(primitives).instances() <= submitted


def the_subset_is_proper(primitives=SCENE, view=VIEW):
    """NON-VACUITY (L61): subset-of would hold trivially if nothing were ever occluded.
    The pinned scene hides instance 9 entirely behind instance 7."""
    submitted = frozenset(_check_primitive(p)[4] for p in primitives)
    return IdFramebuffer(*view).render(primitives).instances() < submitted


#: Every knob here must ACTUALLY MOVE THE FRAME on the pinned scene. An inert knob would
#: satisfy the firewall's "scene digest unchanged" half for free and quietly weaken the
#: check to nothing, so `knobs_do_not_reach_the_citation` demands both halves per knob.
#: That demand caught its own first fixture: `zfar=50` and `zfar=10` are inert here —
#: the scene's depths are 4, 9 and 12, so 50 clips nothing, and 10 clips only instance 9,
#: which instance 7 already hides. A knob that changes nothing proves nothing.
KNOBS = ((32, 16, 0, 100),      # wider
         (16, 32, 0, 100),      # taller
         (16, 16, 6, 100),      # near plane past instance 7 (depth 4)
         (16, 16, 0, 8))        # far plane in front of instances 3 and 9 (depths 9, 12)


def knobs_do_not_reach_the_citation(primitives=SCENE):
    """THE FIREWALL. Perturbing a view knob must move the FRAME and leave the cited
    SCENE digest fixed — both halves, for every knob."""
    base = witness(primitives, *VIEW)
    for view in KNOBS:
        alt = witness(primitives, *view)
        if alt["scene"] != base["scene"] or alt["frame"] == base["frame"]:
            return False
    return True


def every_knob_is_live(primitives=SCENE):
    """Stated separately so the failure is legible: which knobs move the frame at all."""
    base = witness(primitives, *VIEW)["frame"]
    return tuple(witness(primitives, *v)["frame"] != base for v in KNOBS)


def the_scene_reaches_the_citation(primitives=SCENE):
    """The other direction, and it is not decoration: a `scene_digest` that ignored the
    scene would satisfy the firewall perfectly. One integer moved must move BOTH."""
    base = witness(primitives, *VIEW)
    prims = list(primitives)
    v0, v1, v2, zs, iid, pid = prims[0]
    prims[0] = ((v0[0] + SUB, v0[1]), v1, v2, zs, iid, pid)
    alt = witness(prims, *VIEW)
    return alt["scene"] != base["scene"] and alt["frame"] != base["frame"]


def the_door_closes():
    """Three typed refusals: an id at the EMPTY sentinel, a float coordinate, and a view
    past the bound `renderbound` decided."""
    bad = (
        lambda: scene_digest([_t(0, 0, 2, 0, 0, 2, (1, 1, 1), EMPTY, 0)]),
        lambda: scene_digest([((0, 0), (2.0, 0), (0, 2), (1, 1, 1), 0, 0)]),
        lambda: IdFramebuffer(4096, 2, 0, 1 << 40),
    )
    for fn in bad:
        try:
            fn()
            return False
        except RenderError as exc:
            if exc.code != "PIXID-REFUSE":
                return False
    return True
