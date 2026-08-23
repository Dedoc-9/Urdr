# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxref (URDRVXF1) — RUNG ZERO OF THE VOXEL ARC: the observable, frozen before any reduction.

THE MISTAKE THIS RUNG EXISTS TO NOT MAKE. The castle arc's observable — the framebuffer digest —
was inherited by accident from the demo's replay DNA. It happened to be external to every
optimisation that came later, so `recompute -> incremental -> span` each had something they could
not redefine. That was luck. The failure mode when it is not luck is circular and quiet:

    optimise the representation -> define the observable around the optimised representation
    -> prove the optimised representation preserves the observable.

So nothing here is optimised. This module is the REFERENCE: it draws every face of every solid
voxel, including the ones buried inside the world and the ones pressed against a neighbour, and
lets the depth test decide. It is slow ON PURPOSE. Face culling, greedy meshing, occlusion and
span work are the rungs that come AFTER, and each of them will be asked one question — does this
reduced representation produce exactly the frozen observable over the adversarial domain?

THE CONTRACT, FROZEN HERE AND NOT LATER:

    O_t = (H_C(colorbuffer), H_Z(depthbuffer))
    coverage = exact top-left partition
    draw order = observationally irrelevant

Both digests, because colour alone is insufficient: a face wrongly dropped behind a same-coloured
neighbour changes nothing visible and moves the depth buffer, which is precisely the shape an
occlusion bug takes. `the_depth_digest_is_not_redundant` exhibits such a pair rather than assuming
one exists, and `the_colour_digest_is_not_redundant` exhibits the mirror — so neither digest is a
function of the other and the observable has to be the pair. Both witnesses are CONSTRUCTED: the
first version of this claim read the property off the corpus, and a change of hash seed deleted it,
which is the difference between a structural claim and a coincidence.

WHY THE PARTITION, AND WHAT IT COST TO GET RIGHT. The castle rasteriser tests `w >= 0` on all
three edges, which is a COVER: a pixel on an edge shared by two triangles satisfies both. The
castle never noticed because the loser of the tie failed a strict depth test and both triangles
carried the same colour. A voxel world has differently-coloured faces meeting at seams, so the
same cover would paint draw order onto the screen. The top-left rule biases each edge that is
neither top nor left by -1, turning the test into a PARTITION — every pixel claimed exactly once.
Integer, exact, one subtraction per edge.

AND THE PART THE CONTRACT AS FIRST WRITTEN DID NOT COVER, found by building it. A partition fixes
pixels shared by adjacent triangles. It does NOTHING about two DISTINCT faces that are geometrically
COINCIDENT — and the naive reference is full of them, because every pair of adjacent solid voxels
contributes two faces in the same plane. Those tie at exactly equal depth, and under a plain `<`
the winner is whoever was drawn first. Draw order would still be observable, through a door the
top-left rule does not close.

So the depth test compares `(depth, face_key)` where `face_key` is derived from the voxel's own
coordinates and face index — a property of the WORLD, not of traversal. Ties resolve by scene
identity. THAT is what makes `draw order = observationally irrelevant` true rather than aspirational,
and `the_order_permutation_leaves_the_observable_alone` proves it on a corpus that CONTAINS such
coincidences — checked, because the law would pass vacuously on a world that had none.

does_not_show: anything about performance — this renderer is deliberately naive and its cost is not
a measurement of anything. Nor that the observable is FINE ENOUGH: `coarseness` reports how many
distinct world/camera states share an O_t, which is the question the castle arc only got round to
asking ten rungs in, and it is REPORTED rather than promoted to a law. Nor anything about greedy
meshing, T-junctions, or LOD seams — those are named in the README as the first reduction's
problem and are deliberately absent here, because using the first optimisation to validate the
semantic foundation it depends on is the circularity this whole rung is built to avoid.

falsifier: remove the top-left bias and `the_coverage_is_a_partition` reddens with double-claimed
pixels; drop the face-key tiebreak and the order-permutation law reddens; render the trace twice
and the determinism law compares the two; hash only one buffer and the corresponding witness
exhibits the pair that observable would miss. Each is exercised in the selftest, not asserted, and
both witnesses REFUSE typed if they render nothing at all — which is how the depth witness first
read green, by comparing two empty buffers.
"""
import hashlib
import os

_HERE = os.path.dirname(os.path.abspath(__file__))

MAGIC = b"URDRVXF1"

#: DECLARED — the world is deliberately tiny. Rung zero is a CONTRACT, not a game: everything here
#: exists to make the observable well-defined and checkable inside the gate, and a bigger world
#: would buy nothing but runtime. 12^3 voxels in 4^3 sections, so section seams exist to stand on.
N = 12
SECTION = 4
SEED = 20260823
Q = 1 << 8                      #: voxel units are Q8, matching the castle's world scale
W, H = 96, 72                   #: framebuffer, small enough that the gate can render the trace
NEAR = 64                       #: near plane in camera Q8 units
FOCAL = H * 2

#: DECLARED — the six faces as (normal, four corners in unit-cube coordinates), wound so that the
#: outward normal is counter-clockwise seen from outside. The reference does NOT cull by winding:
#: a face pointing away is projected, found to have non-positive area, and skipped by the
#: degenerate-area rule — which is arithmetic, not a visibility decision.
FACES = (
    ((1, 0, 0), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((-1, 0, 0), ((0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1))),
    ((0, 1, 0), ((1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 0, 1), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
    ((0, 0, -1), ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0))),
)

#: DECLARED — one colour per face index and material, so that adjacent voxels' coincident faces
#: carry DIFFERENT colours. That is not decoration: if every face were the same colour the
#: order-permutation law would pass without the tiebreak doing any work, and the corpus would be
#: silently vacuous for the one property this rung exists to establish.
PALETTE = (0x00C04030, 0x00A03828, 0x0030C040, 0x0028A038, 0x004030C0, 0x003828A0)

BACKGROUND = 0x00101018
FAR = (1 << 30)


class VoxrefError(Exception):
    """VOXREF-REFUSE — a scene or a camera this reference will not pretend to render."""


# ---- the world ------------------------------------------------------------------------------
def solid(x, y, z):
    """A voxel's occupancy, DERIVED from a seeded hash — no table, no file, no drift.

    The floor slab at z == 0 exists so the adversarial trace has a surface to stand on and a
    wall-flat case to face; everything above it is the hash.
    """
    if not (0 <= x < N and 0 <= y < N and 0 <= z < N):
        return False
    if z == 0:
        return True
    d = hashlib.sha256(b"URDRVXF1|%d|%d|%d|%d" % (SEED, x, y, z)).digest()
    return d[0] < 110


def world_digest():
    bits = bytearray()
    for x in range(N):
        for y in range(N):
            for z in range(N):
                bits.append(1 if solid(x, y, z) else 0)
    return hashlib.sha256(MAGIC + b"|world|" + bytes(bits)).hexdigest()


def primitives():
    """EVERY face of EVERY solid voxel, in canonical order. No culling of any kind.

    The key is the face's identity in the WORLD — (x, y, z, face index) — and it is what breaks a
    depth tie between two coincident faces. Deriving it from traversal position instead would make
    the tiebreak depend on the very order this rung declares irrelevant.
    """
    out = []
    for x in range(N):
        for y in range(N):
            for z in range(N):
                if not solid(x, y, z):
                    continue
                for fi, (_n, corners) in enumerate(FACES):
                    key = (((x * N) + y) * N + z) * 6 + fi
                    quad = tuple(((x + cx) * Q, (y + cy) * Q, (z + cz) * Q)
                                 for cx, cy, cz in corners)
                    out.append((key, PALETTE[fi], quad))
    return out


# ---- the camera -----------------------------------------------------------------------------
def _isqrt(n):
    if n < 0:
        raise VoxrefError("VOXREF-REFUSE: isqrt of a negative")
    x = n
    y = (x + 1) // 2
    while y < x:
        x, y = y, (y + n // y) // 2
    return x


def basis(fwd):
    """A Q16 integer camera basis from an integer forward vector, up fixed at +z.

    DECLARED, not derived from trigonometry: these three rows ARE the camera, and whatever depth
    they produce is the definition. No floats appear anywhere in this module.
    """
    fx, fy, fz = fwd
    n = _isqrt((fx * fx + fy * fy + fz * fz) * (1 << 32))
    if n == 0:
        raise VoxrefError("VOXREF-REFUSE: a camera cannot look along the zero vector")
    f = (fx * (1 << 16) * (1 << 16) // n, fy * (1 << 16) * (1 << 16) // n,
         fz * (1 << 16) * (1 << 16) // n)
    rx, ry, rz = f[1] * 1 - f[2] * 0, f[2] * 0 - f[0] * 1, f[0] * 0 - f[1] * 0
    rn = _isqrt((rx * rx + ry * ry + rz * rz))
    if rn == 0:
        raise VoxrefError("VOXREF-REFUSE: forward is parallel to up; not in the declared set")
    r = (rx * (1 << 16) // rn, ry * (1 << 16) // rn, rz * (1 << 16) // rn)
    ux = (r[1] * f[2] - r[2] * f[1]) >> 16
    uy = (r[2] * f[0] - r[0] * f[2]) >> 16
    uz = (r[0] * f[1] - r[1] * f[0]) >> 16
    return (r, f, (ux, uy, uz))


#: DECLARED — the adversarial trace, written to visit the configurations the COMING reductions are
#: most likely to break, rather than recorded from someone wandering around. The castle arc's
#: evidence was 43 checkpoints of a human walk, and `armpair`'s does_not_show says so; a reduction
#: that is wrong only where the trace never goes passes forever. Each entry is
#: (name, eye in Q8 world units, integer forward vector).
TRACE = (
    #: INSIDE the solid: a face pressed against the eye, one depth across the whole screen. The
    #: degenerate end of the domain, and the one where a wrong reduction is least visible.
    ("buried",     (6 * Q + 128, 6 * Q + 128, 3 * Q + 128), (0, 1, 0)),
    #: STANDING ON THE FLOOR looking along it — grazing incidence, where the fill rule is most
    #: exercised and where cracks would appear first.
    ("floor_flat", (1 * Q + 128, 5 * Q + 128, 1 * Q + 128), (0, 1, 0)),
    #: AT A SECTION SEAM, looking along it. Nothing in rung zero knows about sections; this frame
    #: exists so the reductions that WILL know about them are already covered by the corpus.
    ("seam",       (SECTION * Q, -9 * Q, 6 * Q + 128), (0, 1, 0)),
    #: FACING A FLAT WALL from the adjacent air voxel: maximal occlusion, minimal visible surface.
    ("wall_flat",  (1 * Q + 128, 4 * Q + 128, 2 * Q + 128), (1, 0, 0)),
    #: OPEN AIR above the world looking down: minimal occlusion, most of the depth range live.
    ("open_air",   (6 * Q + 128, -14 * Q, 20 * Q), (0, 1, -1)),
    #: OBLIQUE, so that no face is either screen-aligned or exactly edge-on — an axis-aligned-only
    #: corpus would test the fill rule at its two most degenerate angles and nowhere else.
    ("oblique",    (-8 * Q, -8 * Q, 18 * Q), (2, 2, -1)),
    ("corner",     (-6 * Q, 18 * Q, 18 * Q), (1, -2, -1)),
    #: EDGE-ON to the floor slab, the other degenerate angle.
    ("edge_on",    (6 * Q + 128, -10 * Q, 1 * Q + 128), (0, 1, 0)),
)


# ---- the rasteriser -------------------------------------------------------------------------
def _edge(ax, ay, bx, by, px, py):
    return (bx - ax) * (py - ay) - (by - ay) * (px - ax)


def _top_left_bias(ax, ay, bx, by):
    """0 for a top or left edge, -1 otherwise — the whole of the partition rule.

    With this bias the interior test `w >= 0` claims a shared edge for exactly ONE of the two
    triangles that meet on it. Without it both claim it, and which one survives depends on the
    order they were drawn in, which is the semantic variable this rung exists to delete.
    """
    dy = by - ay
    dx = bx - ax
    if dy > 0 or (dy == 0 and dx < 0):
        return 0
    return -1


def _project(v, eye, m):
    dx, dy, dz = v[0] - eye[0], v[1] - eye[1], v[2] - eye[2]
    r, f, u = m
    cr = (r[0] * dx + r[1] * dy + r[2] * dz) >> 16
    cf = (f[0] * dx + f[1] * dy + f[2] * dz) >> 16
    cu = (u[0] * dx + u[1] * dy + u[2] * dz) >> 16
    return cr, cf, cu


def render(prims, eye, fwd, collect=None, bias=True):
    """The reference. Returns (colorbuffer, depthbuffer) as lists of length W*H.

    `collect`, when given a dict, receives per-pixel claim counts for the partition law — an
    OBSERVER in the four-layer sense, which must not be able to change a single output byte.
    """
    m = basis(fwd)
    cx, cy = W // 2, H // 2
    color = [BACKGROUND] * (W * H)
    depth = [FAR] * (W * H)
    key = [-1] * (W * H)
    for pkey, col, quad in prims:
        cam = [_project(v, eye, m) for v in quad]
        if all(c[1] < NEAR for c in cam):
            continue
        if any(c[1] < NEAR for c in cam):
            continue          # DECLARED: the reference does not clip; see the README
        scr = [(cx + c[0] * FOCAL // c[1], cy - c[2] * FOCAL // c[1], c[1]) for c in cam]
        for a, b, c in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if area <= 0:
                continue      # backfacing or degenerate: arithmetic, not a visibility decision
            x_lo = max(min(a[0], b[0], c[0]), 0)
            x_hi = min(max(a[0], b[0], c[0]), W - 1)
            y_lo = max(min(a[1], b[1], c[1]), 0)
            y_hi = min(max(a[1], b[1], c[1]), H - 1)
            if x_lo > x_hi or y_lo > y_hi:
                continue
            if bias:
                b0 = _top_left_bias(a[0], a[1], b[0], b[1])
                b1 = _top_left_bias(b[0], b[1], c[0], c[1])
                b2 = _top_left_bias(c[0], c[1], a[0], a[1])
            else:
                b0 = b1 = b2 = 0        # the COVER — the castle's rule, kept only as a falsifier
            for py in range(y_lo, y_hi + 1):
                row = py * W
                for px in range(x_lo, x_hi + 1):
                    w0 = _edge(a[0], a[1], b[0], b[1], px, py) + b0
                    w1 = _edge(b[0], b[1], c[0], c[1], px, py) + b1
                    w2 = _edge(c[0], c[1], a[0], a[1], px, py) + b2
                    if w0 < 0 or w1 < 0 or w2 < 0:
                        continue
                    d = (a[2] * w1 + b[2] * w2 + c[2] * w0) // area
                    i = row + px
                    if collect is not None:
                        collect[i] = collect.get(i, 0) + 1
                    # THE TIEBREAK IS SCENE IDENTITY, NOT ARRIVAL ORDER. Coincident faces between
                    # adjacent solid voxels tie at exactly equal depth; without this the winner
                    # would be whoever was drawn first and draw order would be observable.
                    if (d, pkey) < (depth[i], key[i] if key[i] >= 0 else (1 << 62)):
                        depth[i] = d
                        key[i] = pkey
                        color[i] = col
    return color, depth


def observable(color, depth):
    """O_t = (H_C(colorbuffer), H_Z(depthbuffer)) — two digests, deliberately not one."""
    cb = b"".join(c.to_bytes(4, "big") for c in color)
    db = b"".join((d & 0xFFFFFFFF).to_bytes(4, "big") for d in depth)
    return (hashlib.sha256(MAGIC + b"|C|" + cb).hexdigest(),
            hashlib.sha256(MAGIC + b"|Z|" + db).hexdigest())


def render_trace(prims=None, order=None):
    """The whole declared trace as a list of (name, O_t)."""
    if prims is None:
        prims = primitives()
    if order is not None:
        prims = [prims[i] for i in order]
    out = []
    for name, eye, fwd in TRACE:
        color, depth = render(prims, eye, fwd)
        out.append((name, observable(color, depth)))
    return out


# ---- the laws -------------------------------------------------------------------------------
def the_reference_is_deterministic():
    """Same world, same camera, same trace — the same O_t, twice. The floor of everything else."""
    return render_trace() == render_trace()


def _claims(prims, eye, fwd, bias):
    got = {}
    render(prims, eye, fwd, collect=got, bias=bias)
    return got


def partition_report(quads=64):
    """For a sample of face quads rendered ALONE: how many pixels does each claim twice?

    Scoped to ONE quad on purpose. Across the whole scene a pixel is legitimately claimed by
    several primitives — that is what a depth buffer is for. The PARTITION claim is about the two
    triangles a quad is split into, and about the shared edge between them, which is exactly where
    a cover double-counts.
    """
    prims = primitives()
    step = max(1, len(prims) // quads)
    eye, fwd = TRACE[5][1], TRACE[5][2]          # the oblique frame: no degenerate angles
    doubled = single = 0
    for i in range(0, len(prims), step):
        got = _claims([prims[i]], eye, fwd, True)
        for n in got.values():
            if n > 1:
                doubled += 1
            else:
                single += 1
    return doubled, single


def cover_report(quads=64):
    """The same sample WITHOUT the top-left bias — the castle's rule, kept only as a control."""
    prims = primitives()
    step = max(1, len(prims) // quads)
    eye, fwd = TRACE[5][1], TRACE[5][2]
    doubled = single = 0
    for i in range(0, len(prims), step):
        got = _claims([prims[i]], eye, fwd, False)
        for n in got.values():
            if n > 1:
                doubled += 1
            else:
                single += 1
    return doubled, single


def the_coverage_is_a_partition():
    """No pixel of a quad is claimed twice, and the sample is not empty."""
    doubled, single = partition_report()
    return doubled == 0 and single > 0


def a_cover_double_claims_and_a_partition_does_not():
    """THE FALSIFIER, AND IT IS THE CONTROL THAT MAKES THE LAW ABOVE MEAN SOMETHING.

    Dropping the bias must produce double-claimed pixels on the SAME sample. Without this the
    partition law could be passing because the sample happens to contain no shared edges at all,
    which would make it a statement about the sample rather than about the rule.
    """
    return cover_report()[0] > 0 and partition_report()[0] == 0


def _coincident_pairs():
    """Faces that are geometrically coincident — the case the top-left rule does NOT close."""
    seen = {}
    n = 0
    for key, _col, quad in primitives():
        c = tuple(sorted(quad))
        if c in seen:
            n += 1
        seen[c] = key
    return n


def the_corpus_contains_coincident_faces():
    """NON-VACUITY FOR THE LAW BELOW. Every pair of adjacent solid voxels contributes two faces in
    the same plane; if the world had none, the order-permutation law would pass without the
    scene-identity tiebreak ever being consulted, and would be evidence of nothing."""
    return _coincident_pairs() > 0


def the_order_permutation_leaves_the_observable_alone():
    """DRAW ORDER IS OBSERVATIONALLY IRRELEVANT — the third line of the frozen contract, proved.

    The permutation is DECLARED (a reversal and a stride shuffle), not random, so this law is the
    same law on every run and on every machine.
    """
    prims = primitives()
    n = len(prims)
    base = render_trace(prims)
    for order in (list(range(n - 1, -1, -1)),
                  [i for r in range(7) for i in range(r, n, 7)]):
        if render_trace(prims, order) != base:
            return False
    return True


def a_shuffled_order_is_a_real_shuffle():
    """The permutations must actually permute, or the law above is a tautology (L61)."""
    n = len(primitives())
    rev = list(range(n - 1, -1, -1))
    strided = [i for r in range(7) for i in range(r, n, 7)]
    ident = list(range(n))
    return (sorted(rev) == ident and sorted(strided) == ident
            and rev != ident and strided != ident)


def depth_witness():
    """A CONSTRUCTED pair where the colour buffers agree exactly and the depth buffers do not.

    Two quads of the SAME colour subtending the SAME screen rectangle at DIFFERENT distances: the
    far one is scaled so that half/distance is identical, which under an integer projection makes
    the projected corners equal to the pixel. With both present the near one wins every pixel;
    with only the far one the picture is byte-identical and the depth buffer is not.

    That is the exact shape of an occlusion bug that drops a face behind a same-coloured
    neighbour — and a colour-only observable would call it a pass. Hence two digests, not one.

    DECLARED: this is CONSTRUCTED, not found in the trace. It shows the two digests are
    INDEPENDENT in one direction; `colour_witness` shows the other, and the pair of them is what
    establishes that neither digest is a function of the other. Neither shows that such a
    configuration occurs in the declared corpus.
    """
    eye, fwd = (0, -8 * Q, 0), (0, 1, 0)

    def quad(dist, half):
        #: wound for a POSITIVE projected area under this camera. The reference culls nothing by
        #: visibility, but a non-positive area is degenerate arithmetic and is skipped — and a
        #: witness that silently rendered nothing would "pass" by comparing two empty buffers,
        #: which is exactly how this law first read green for no reason at all.
        y = dist - 8 * Q
        return tuple((sx * half, y, sz * half)
                     for sx, sz in ((-1, 1), (1, 1), (1, -1), (-1, -1)))

    near = (10, PALETTE[3], quad(8 * Q, 1 * Q))
    far = (11, PALETTE[3], quad(12 * Q, 3 * Q // 2))      # same half/dist, so the same rectangle
    cb, db = render([near, far], eye, fwd)
    cf_, df = render([far], eye, fwd)
    if all(x == BACKGROUND for x in cb):
        raise VoxrefError("VOXREF-REFUSE: the depth witness rendered nothing; it proves nothing")
    return observable(cb, db), observable(cf_, df)


def the_depth_digest_is_not_redundant():
    both, only = depth_witness()
    return both[0] == only[0] and both[1] != only[1]


def colour_witness():
    """The mirror: colour buffers DIFFER while the depth buffers agree exactly.

    Two quads at the SAME distance, same rectangle, different colours, rendered one at a time.
    Depth is byte-identical; colour is not. Together with `depth_witness` this establishes that
    NEITHER digest is a function of the other, so `O_t` has to be the pair.

    WHY THIS IS CONSTRUCTED AND NOT READ OFF THE CORPUS. It was read off the corpus first: two
    declared frames happened to share a depth digest, and the brief said so as evidence. Then the
    module's MAGIC had to change (it collided with `voxlat`'s, which the tree's own `magicuniq`
    stage caught), the world seed string changed with it, and the coincidence evaporated — the
    prose was asserting a property of one hash, not a property of the observable. A witness that a
    reseed can delete was never evidence for a structural claim.
    """
    eye, fwd = (0, -8 * Q, 0), (0, 1, 0)
    corners = ((-1, 1), (1, 1), (1, -1), (-1, -1))
    quad = tuple((sx * Q, 0, sz * Q) for sx, sz in corners)
    ca, da = render([(20, PALETTE[0], quad)], eye, fwd)
    cb, db = render([(20, PALETTE[2], quad)], eye, fwd)
    if all(x == BACKGROUND for x in ca):
        raise VoxrefError("VOXREF-REFUSE: the colour witness rendered nothing; it proves nothing")
    return observable(ca, da), observable(cb, db)


def the_colour_digest_is_not_redundant():
    a, b = colour_witness()
    return a[1] == b[1] and a[0] != b[0]


def coarseness():
    """REPORTED, NEVER A LAW: how discriminating is the observable actually?

    The castle arc asked this ten rungs after it started trusting its digest, and the answer —
    2564 states collapsing to 2309 digests — was interesting enough that asking first is worth a
    rung. Returns (frames, distinct O_t, distinct colour digests, distinct depth digests).
    """
    obs = [o for _n, o in render_trace()]
    return (len(obs), len(set(obs)), len({c for c, _z in obs}), len({z for _c, z in obs}))


def every_declared_case_is_distinct():
    """The adversarial trace must not contain two frames the observable cannot tell apart — that
    would be a case bought and not paid for."""
    frames, distinct, _c, _z = coarseness()
    return frames == distinct == len(TRACE)


# ---- scenes ---------------------------------------------------------------------------------
def scene_case(name):
    if name == "contract":
        return repr((N, SECTION, SEED, W, H, NEAR, FOCAL, BACKGROUND, PALETTE,
                     world_digest(), len(primitives()), render_trace()))
    if name == "laws":
        return repr((partition_report(), cover_report(), _coincident_pairs(),
                     coarseness(), depth_witness(), colour_witness()))
    raise VoxrefError("VOXREF-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxref.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxrefError("VOXREF-REFUSE: no golden named %r" % name)


def told():
    frames, distinct, dc, dz = coarseness()
    return ("%d voxels, %d primitives, %d coincident face pairs; %d adversarial frames -> %d "
            "distinct O_t (%d colour, %d depth); partition claims no pixel twice where the cover "
            "claims %d" % (N ** 3, len(primitives()), _coincident_pairs(), frames, distinct,
                           dc, dz, cover_report()[0]))
