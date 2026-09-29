# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""bearing — THE HEADING REFINEMENT OF THE FIRST-PERSON FRAME: ANY BEARING, THE EYE STILL AT A CELL CENTRE (URDRBRG1).

`vista` RENDERS FROM A CELL AND ONE OF FOUR CARDINALS, AND ITS BRIEF NAMES "A HEADING REFINEMENT" AS THE NEXT
CAMERA RUNG. This module is that rung, admitted against the preregistration `spec/D26-bearing-boundary.md`
(written and committed before this file existed). A bearing is an integer id in [0, 360000) — millidegrees
clockwise from north, `frontfps`'s yaw identity and refusal law — and it names ONE canonical primitive
Pythagorean triple (A, B, C), A² + B² = C²: forward (A/C, B/C), screen-right (−B/C, A/C). The renderer consumes
the triple, never an angle, so every quantity stays a floor of a rational exactly as in `vista`.

THE VOCABULARY IS DATA, AND THE CHECKER IS NOT THE PROVER. The octant 0..45000 is committed as (p, q) pairs in
`bearing_octant.txt` (the stereographic parameter t = p/q ≈ tan(θ/2)) with its sha256 pinned here; ids
45000 < k < 90000 are the octant's mirror, every id beyond is an exact quarter turn. The program that chose the
pairs (`studio/bearing_octant_gen.py`, an off-gate driver like the studio arc's others) is provenance: nothing here or in the gate runs it. `the_table_holds` checks the
committed pairs by their own invariants — canonical and primitive, the anchors, strictly clockwise order over
all 360,000 ids including every symmetry seam and the wrap — and bites five planted table defects without
leaning on the sha pin. A missing or altered file REFUSES; it is never regenerated and never skipped.

THE LAW (D26 §3). The ray at column c is D = (A·b − B·a, B·b + A·a), a = 2c + 1 − W, b = 2·FOCAL: an integer
vector, C times the unit ray. Four expressions see C — the depth 2·FOCAL·C·t (strip edges), the depth band, the
wall's row height EYE_Y + (2·CY − 2r − 1)·C·t, and the floor point E + D·EYE_Y/(kk·C) — and everything else is
`vista`'s and `mantle`'s arithmetic unchanged, reused from them where it takes no facing. At C = 1 each is the
frozen expression: `the_anchors_are_the_frozen_frames` shows the four anchors reproduce `vista`'s frames and
`mantle`'s pictures byte for byte, and `the_c_law_reads_back` recomputes every strip and a registered set of
floor cells from the hit point by the dot-product definition — a second computation — with the planted
"frozen depth at a non-anchor bearing" caught.

WHAT THIS IS, IN THE D24 §1 TERMS: A VIEW. It reads a `Level`, an integer cell `pos` and a bearing, and returns a
frame or a picture. The bearing is view state beside the run, never in it; the identity folds the table's
digest, so an id means nothing without its table (D26 F4).

GRADE (honest, D5). MEASURED: the table law over all 360,000 ids with its five planted defects caught; the
anchor law over the corpus; the C law read back over the adversarial corpus with its plant caught; the corpus
frames and pictures reproduce (pinned). ESTABLISHED: the AST is one-way; no CORE module imports `bearing`.
DECLARED: the quarter-millidegree angle bound of the octant (its endpoints are irrational; the gate does not
evaluate them), and everything `vista` and `mantle` declare. does_not_show: movement between cell centres,
pitch, eye height, motion, any frame budget, that the table is the best possible, a second placement (the Rust
placement is its own row), and any wall-clock."""
import ast
import hashlib
import math as _math
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_RENDER = _os.path.join(_os.path.dirname(_HERE), "render")
for _p in (_HERE, _RENDER):
    if _p not in __import__("sys").path:
        __import__("sys").path.insert(0, _p)
import gamegen as _G                                                    # noqa: E402  (the level, READ)
import descent as _D                                                    # noqa: E402  (traversability, READ)
import voxray as _VX                                                    # noqa: E402  (the certified ray oracle)
import raster as _RS                                                    # noqa: E402  (the URDRFB1 frame)
import vista as _V                                                      # noqa: E402  (the frozen frame: anchors, constants, table)
import mantle as _M                                                     # noqa: E402  (the frozen picture: tiles, maps, coordinates)

MAGIC = b"URDRBRG1"

LAYER = "VIEW"
D24_ANSWER = "renders the first-person frame and picture of the certified level from a cell and a registered bearing — a one-way view (the eye is taken, the bearing is view state, the direction is a registered rational triple)"
ALLOWED_IMPORTS = ("ast", "fractions", "hashlib", "math", "os", "tempfile", "gamegen", "descent", "voxray", "raster",
                   "vista", "mantle")

#: The vocabulary (D26 §2). Millidegrees clockwise from north; the octant file and its pinned sha256.
YAW_MOD = 360000
QUARTER = YAW_MOD // 4
OCTANT = QUARTER // 2
ANCHORS = {0: "N", QUARTER: "E", 2 * QUARTER: "S", 3 * QUARTER: "W"}
OCTANT_FILE = "bearing_octant.txt"
OCTANT_SHA256 = "f70b2fc20ba8ea8fde7f802ae0f1180ae003d2de5acb963524ca58421405a82c"

W, H, CY, FOCAL, Q, EYE_Y, BANDS = _V.W, _V.H, _V.CY, _V.FOCAL, _V.Q, _V.EYE_Y, _V.BANDS

_FORBIDDEN_MODULES = frozenset({"move", "descend", "loot", "enact", "statecanon", "rerun", "savegame", "lockstep",
                                "actionlog", "rngstream", "entity", "cue", "chorus"})
_FORBIDDEN_ATTRS = frozenset({"step", "dispatch", "apply", "d_n", "d_n_preimage", "serialize", "restore"})


class BearingError(Exception):
    def __init__(self, message):
        super().__init__(f"BEARING-REFUSE: {message}")
        self.code = "BEARING-REFUSE"


# ---- the vocabulary ---------------------------------------------------------------------------------------------
_OCTANT_MEMO = []


def _read_octant(path=None):
    """The committed pairs, refused unless the file is present, byte-exact to the pin and well formed. Never
    regenerated: the program that chose them is provenance, not authority."""
    path = _os.path.join(_HERE, OCTANT_FILE) if path is None else path
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        raise BearingError(f"the octant file is missing ({exc.__class__.__name__}); it is never regenerated")
    if hashlib.sha256(raw).hexdigest() != OCTANT_SHA256:
        raise BearingError("the octant file is not the pinned one (sha256 differs)")
    pairs = []
    for ln in raw.decode("ascii").splitlines():
        parts = ln.split(" ")
        if len(parts) != 2 or not all(x.isdigit() for x in parts):
            raise BearingError(f"a malformed octant line {ln!r}")
        pairs.append((int(parts[0]), int(parts[1])))
    return tuple(pairs)


def octant():
    if not _OCTANT_MEMO:
        _OCTANT_MEMO.append(_read_octant())
    return _OCTANT_MEMO[0]


def _check_id(k):
    if not isinstance(k, int) or isinstance(k, bool):
        raise BearingError(f"a bearing is an integer id, got {type(k).__name__}")
    if not 0 <= k < YAW_MOD:
        raise BearingError(f"bearing {k} outside [0, {YAW_MOD}) — refused, never normalized")


def _triple_of(pairs, k):
    """(A, B, C) for id k from a list of octant pairs: the octant, its mirror, then quarter turns."""
    turns, r = divmod(k, QUARTER)
    if r <= OCTANT:
        p, q = pairs[r]
        a, b, c = 2 * p * q, -(q * q - p * p), p * p + q * q
    else:
        p, q = pairs[QUARTER - r]
        a, b, c = q * q - p * p, -2 * p * q, p * p + q * q
    g = _math.gcd(_math.gcd(a, b), c)
    a, b, c = a // g, b // g, c // g
    for _ in range(turns):
        a, b = -b, a
    return a, b, c


def direction(k):
    """The registered triple (A, B, C) of bearing k."""
    _check_id(k)
    return _triple_of(octant(), k)


def _table_rows(pairs):
    for k in range(YAW_MOD):
        yield _triple_of(pairs, k)


def table_digest():
    """The identity of the whole vocabulary: every id's triple in order (D26 F4 folds it into URDRBRG1)."""
    h = hashlib.sha256(MAGIC + b"|table|")
    for a, b, c in _table_rows(octant()):
        h.update(b"%d,%d,%d;" % (a, b, c))
    return h.hexdigest()


def the_table_holds(pairs=None):
    """(canonical_pairs, anchors, pythagorean_primitive, clockwise_everywhere) for a list of octant pairs —
    the committed one by default. Read off the pairs themselves, never by re-choosing them: every pair is
    0 <= p < q with gcd 1 and there are exactly OCTANT + 1 of them; id 0 is (0, 1) and the four anchors are the
    cardinals; every triple is Pythagorean and primitive with C >= 1; and every consecutive pair of the 360,000
    ids, the wrap 359999 -> 0 included, turns clockwise by less than a right angle (exact cross and dot
    products) — which crosses every mirror seam and quarter-turn seam of the expansion."""
    pairs = octant() if pairs is None else tuple(pairs)
    canonical = (len(pairs) == OCTANT + 1
                 and all(isinstance(p, int) and isinstance(q, int) and 0 <= p < q and _math.gcd(p, q) == 1
                         for p, q in pairs))
    if not canonical:
        return False, False, False, False
    anchors = (pairs[0] == (0, 1)
               and all(_triple_of(pairs, k)[:2] == _V._FWD[f] and _triple_of(pairs, k)[2] == 1
                       for k, f in ANCHORS.items()))
    prim, clockwise = True, True
    first = prev = _triple_of(pairs, 0)
    for k in range(YAW_MOD):
        a, b, c = _triple_of(pairs, k) if k else first
        if not (c >= 1 and a * a + b * b == c * c and _math.gcd(_math.gcd(a, b), c) == 1):
            prim = False
        if k:
            pa, pb, _pc = prev
            if not (pa * b - pb * a > 0 and pa * a + pb * b > 0):
                clockwise = False
        prev = (a, b, c)
    pa, pb, _pc = prev
    a, b, _c = first
    clockwise = clockwise and pa * b - pb * a > 0 and pa * a + pb * b > 0
    return canonical, anchors, prim, clockwise


def planted_table_defects_are_caught():
    """(dropped, non_primitive, swapped, sign_flipped, exchanged): each planted defect in a COPY of the pairs is
    refused by `the_table_holds` alone — the structural checker bites without the sha pin."""
    good = list(octant())

    def refused(pairs):
        return not all(the_table_holds(pairs))
    i = 12345
    dropped = good[:i] + good[i + 1:]
    nonprim = list(good)
    nonprim[i] = (good[i][0] * 2, good[i][1] * 2)
    swapped = list(good)
    swapped[i] = (good[i][1], good[i][0])
    flipped = list(good)
    flipped[i] = (-good[i][0], good[i][1])
    exchanged = list(good)
    exchanged[i], exchanged[i + 1] = good[i + 1], good[i]
    return tuple(refused(x) for x in (dropped, nonprim, swapped, flipped, exchanged))


# ---- admission ----------------------------------------------------------------------------------------------------
def _check(level, pos, k):
    if not isinstance(level, _G.Level):
        raise BearingError(f"level must be a gamegen.Level, got {type(level).__name__}")
    if not (isinstance(pos, tuple) and len(pos) == 2
            and all(isinstance(v, int) and not isinstance(v, bool) for v in pos)):
        raise BearingError(f"pos must be an integer cell (x, y), got {pos!r}")
    if not _D.traversable(level, pos[0], pos[1]):
        raise BearingError(f"the eye stands on a non-traversable cell {pos!r}; a frame from inside rock is not a view")
    _check_id(k)


# ---- the camera at a bearing ---------------------------------------------------------------------------------------
def ray(triple, column):
    """D = (A·b − B·a, B·b + A·a): the column's pixel-centre ray, C times the unit ray, integer."""
    a_, b_, _c = triple
    a, b = 2 * column + 1 - W, 2 * FOCAL
    return a_ * b - b_ * a, b_ * b + a_ * a


def strip(level, pos, triple, column):
    """(voxel, face, (t_num, t_den), top_row, bottom_row, band) — `vista.strip` with the depth 2·FOCAL·C·t."""
    c_ = triple[2]
    dx, dz = ray(triple, column)
    hit = _VX.first_hit(_V._eye(pos), (dx, 0, dz), occ=_V._occupancy(level), origin="opaque", n=_V.LATTICE, q=Q)
    if hit is None or hit[1] is None:
        raise BearingError(f"the ray at column {column} left the world or started inside rock")
    vox, face, (tn, td) = hit
    h2n, h2d = FOCAL * EYE_Y * td, 2 * FOCAL * c_ * tn
    top = CY - (2 * h2n + h2d) // (2 * h2d)
    bot = CY + (2 * h2n - h2d) // (2 * h2d)
    band = min(BANDS - 1, (2 * FOCAL * c_ * tn) // (td * Q))
    return vox, face, (tn, td), max(0, top), min(H - 1, bot), band


def _strips(level, pos, triple):
    out = []
    for c in range(W):
        vox, face, (tn, td), top, bot, band = strip(level, pos, triple, c)
        dx, dz = ray(triple, c)
        out.append((vox, face, tn, td, top, bot, band, dx, dz))
    return out


def floor_cell(eye, d, c_, row):
    """The cell a floor pixel sees: floor((E·kk·C + D·EYE_Y) / (kk·C·Q)) per axis — `vista`'s at C = 1."""
    ex, _ey, ez = eye
    kk = 2 * (row - CY) + 1
    return (ex * kk * c_ + d[0] * EYE_Y) // (kk * c_ * Q), (ez * kk * c_ + d[1] * EYE_Y) // (kk * c_ * Q)


def _frame_from(level, pos, triple, strips):
    fb = _RS.Framebuffer(W, H)
    buf = fb.buf
    cells, rows, cols = level.cells, level.h, level.w
    eye = _V._eye(pos)
    prev = None
    for c in range(W):
        vox, face, _tn, _td, top, bot, band, dx, dz = strips[c]
        widx = _V.WALL0 + _V.FACE_LIGHT[face] * BANDS + band
        key = (vox, face)
        for r in range(0, top):
            buf[r * W + c] = _V.SKY0 + min(_V.SKY_BANDS - 1, ((CY - r) * _V.SKY_BANDS) // CY)
        v = _V.INK if key != prev else widx
        for r in range(top, bot + 1):
            buf[r * W + c] = v
        if top < bot:
            buf[top * W + c] = _V.INK
            buf[bot * W + c] = _V.INK
        for r in range(bot + 1, H):
            kk = 2 * (r - CY) + 1
            wx, wz = floor_cell(eye, (dx, dz), triple[2], r)
            fband = min(BANDS - 1, (2 * FOCAL * EYE_Y) // (kk * Q))
            cc = cells[wz][wx:wx + 1] if 0 <= wz < rows and 0 <= wx < cols else b"#"
            if cc == b">":
                buf[r * W + c] = _V.DOWN0 + fband
            elif cc == b"<":
                buf[r * W + c] = _V.UP0 + fband
            else:
                buf[r * W + c] = _V.FLOOR0 + fband
        prev = key
    return fb


def frame(level, pos, k):
    """ONE FIRST-PERSON FRAME at bearing k as a URDRFB1 index image: `vista.frame`'s construction at the
    registered triple."""
    _check(level, pos, k)
    triple = direction(k)
    return _frame_from(level, pos, triple, _strips(level, pos, triple))


def _emit(fb, level, pos, triple, tiles, strips):
    """RGB bytes: `mantle._emit` at the registered triple — the wall's row height and the floor point carry C."""
    table = _V.lut(level.depth)
    wall_map, floor_map = _M._band_tables(level.depth)
    eye = _V._eye(pos)
    ex, _ey, ez = eye
    c_ = triple[2]
    buf = fb.buf
    walls, floor_t = tiles["wall"], tiles["floor"]
    WALL0, FLOOR0, DOWN0, T, texel = _V.WALL0, _V.FLOOR0, _V.DOWN0, _M.T, _M.texel
    out = bytearray(W * H * 3)
    for c in range(W):
        s = strips[c]
        top, bot = s[4], s[5]
        u_n, u_d = _M.wall_u(eye, s)
        ti = texel(u_n, u_d)
        tn, td, dx, dz = s[2], s[3], s[7], s[8]
        v_base = Q * td - EYE_Y * td - (2 * CY - 1) * c_ * tn                  # v numerator at row 0, +2·C·tn per row
        v_den = Q * td
        for r in range(0, top):
            o = (r * W + c) * 3
            out[o:o + 3] = bytes(table[buf[r * W + c]])
        for r in range(top, bot + 1):
            idx = buf[r * W + c]
            o = (r * W + c) * 3
            if idx < WALL0:
                out[o:o + 3] = bytes(table[idx])
                continue
            light, band = (idx - WALL0) // BANDS, (idx - WALL0) % BANDS
            kx = (texel(v_base + 2 * r * c_ * tn, v_den) * T + ti) * 3
            tile, m = walls[light], wall_map[band]
            out[o] = m[tile[kx]]
            out[o + 1] = m[tile[kx + 1]]
            out[o + 2] = m[tile[kx + 2]]
        for r in range(bot + 1, H):
            idx = buf[r * W + c]
            o = (r * W + c) * 3
            if idx < FLOOR0 or idx >= DOWN0:
                out[o:o + 3] = bytes(table[idx])
                continue
            kk = 2 * (r - CY) + 1
            den = kk * c_ * Q
            kx = (texel((ez * kk * c_ + dz * EYE_Y) % den, den) * T + texel((ex * kk * c_ + dx * EYE_Y) % den, den)) * 3
            m = floor_map[idx - FLOOR0]
            out[o] = m[floor_t[kx]]
            out[o + 1] = m[floor_t[kx + 1]]
            out[o + 2] = m[floor_t[kx + 2]]
    return bytes(out)


def picture(level, pos, k, tiles=None):
    """(frame, rgb) at bearing k: the frame and `mantle`'s tile path over it (the identity tiles when None)."""
    tiles = _M.identity_tiles() if tiles is None else tiles
    _M._check_tiles(tiles)
    _check(level, pos, k)
    triple = direction(k)
    strips = _strips(level, pos, triple)
    fb = _frame_from(level, pos, triple, strips)
    return fb, _emit(fb, level, pos, triple, tiles, strips)


# ---- the laws -------------------------------------------------------------------------------------------------------
def the_anchors_are_the_frozen_frames(level, pos, tiles_sets=None):
    """(frames_equal, pictures_equal): at each of the four anchors the frame's URDRFB1 digest equals `vista`'s at
    that facing and the picture's bytes equal `mantle`'s, for every given tile set — the frozen modules computed
    LIVE beside this one."""
    tiles_sets = (_M.identity_tiles(),) if tiles_sets is None else tiles_sets
    frames_eq, pics_eq = True, True
    for k, f in ANCHORS.items():
        frames_eq = frames_eq and _V.frame_digest(frame(level, pos, k)) == _V.frame_digest(_V.frame(level, pos, f))
        for tiles in tiles_sets:
            pics_eq = pics_eq and picture(level, pos, k, tiles)[1] == _M.picture(level, pos, f, tiles)[1]
    return frames_eq, pics_eq


def _mirrored_frame(level, pos, k):
    """The plant for the anchor law: screen-right mirrored to (B, −A)."""
    a_, b_, c_ = direction(k)
    triple = (a_, b_, c_)
    out = []
    for c in range(W):
        a, b = 2 * c + 1 - W, 2 * FOCAL
        d = (a_ * b + b_ * a, b_ * b - a_ * a)                                   # right = (B, −A): mirrored
        hit = _VX.first_hit(_V._eye(pos), (d[0], 0, d[1]), occ=_V._occupancy(level), origin="opaque", n=_V.LATTICE, q=Q)
        vox, face, (tn, td) = hit
        h2n, h2d = FOCAL * EYE_Y * td, 2 * FOCAL * c_ * tn
        top = CY - (2 * h2n + h2d) // (2 * h2d)
        bot = CY + (2 * h2n - h2d) // (2 * h2d)
        band = min(BANDS - 1, (2 * FOCAL * c_ * tn) // (td * Q))
        out.append((vox, face, tn, td, max(0, top), min(H - 1, bot), band, d[0], d[1]))
    return _frame_from(level, pos, triple, out)


def a_mirrored_camera_is_caught(level, pos):
    """True when a module with screen-right mirrored to (B, −A) fails the anchor law at this view: its frame
    differs from `vista`'s at some anchor. (A view whose geometry is mirror-symmetric at an anchor cannot tell a
    mirror there, so the law is asked of the four anchors together, as it is stated.)"""
    return any(_V.frame_digest(_mirrored_frame(level, pos, k)) != _V.frame_digest(_V.frame(level, pos, f))
               for k, f in ANCHORS.items())


#: The registered floor rows the C law reads back (below the horizon, near to far).
READBACK_ROWS = (CY + 1, CY + 7, CY + 40, CY + 200, H - 1)


def _readback(level, pos, k, frozen_depth=False):
    """(strips_ok, floors_ok) for bearing k: every column's strip edges and band, and the floor cells of
    READBACK_ROWS, recomputed from the hit point by the dot-product definition — the forward distance
    (P − E)·(A, B)/C — against the module's own shortcut (or a planted one that drops C from the depth)."""
    from fractions import Fraction
    triple = direction(k)
    a_, b_, c_ = triple
    eye = _V._eye(pos)
    strips_ok, floors_ok = True, True
    for col in range(W):
        if frozen_depth:
            got = strip(level, pos, (a_, b_, 1), col)                             # the plant: C dropped from the depth
        else:
            got = strip(level, pos, triple, col)
        dx, dz = ray(triple, col)
        t = Fraction(got[2][0], got[2][1])
        px, pz = eye[0] + t * dx, eye[2] + t * dz
        dist = ((px - eye[0]) * a_ + (pz - eye[2]) * b_) / c_                       # (P − E)·f̂, the second computation
        h = Fraction(FOCAL * EYE_Y) / dist
        top = max(0, CY - _math.floor(h + Fraction(1, 2)))
        bot = min(H - 1, CY + _math.floor(h - Fraction(1, 2)))
        band = min(BANDS - 1, _math.floor(dist / Q))
        if (top, bot, band) != (got[3], got[4], got[5]):
            strips_ok = False
        for r in READBACK_ROWS:
            kk = 2 * (r - CY) + 1
            fwd = Fraction(2 * FOCAL * EYE_Y, kk)                                   # the forward distance the row sees
            unit_fwd = Fraction(dx * a_ + dz * b_, c_)                               # D·f̂
            s_ = fwd / unit_fwd
            want = (_math.floor((eye[0] + s_ * dx) / Q), _math.floor((eye[2] + s_ * dz) / Q))
            have = floor_cell(eye, (dx, dz), 1 if frozen_depth else c_, r)
            if want != have:
                floors_ok = False
    return strips_ok, floors_ok


def the_c_law_reads_back(level, pos, ids):
    """(holds, plant_caught): the C law read back at every id given, and the planted frozen depth caught at
    every non-anchor id among them."""
    holds = all(_readback(level, pos, k) == (True, True) for k in ids)
    caught = all(_readback(level, pos, k, frozen_depth=True) != (True, True) for k in ids if k not in ANCHORS)
    return holds, caught


def _import_top(tree):
    top = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            top.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            top.add((node.module or "").split(".")[0])
    return top


def _source_is_one_way(src):
    tree = ast.parse(src)
    top = _import_top(tree)
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    return (top <= set(ALLOWED_IMPORTS)
            and not (top & _FORBIDDEN_MODULES)
            and not (attrs & _FORBIDDEN_ATTRS))


def the_membrane_is_one_way():
    """STRUCTURAL, read off this module's OWN full AST: exactly the declared substrate, no transition/identity/
    log/stream authority in any scope. Positive controls as `vista`'s."""
    with open(_os.path.join(_HERE, "bearing.py"), encoding="utf-8") as fh:
        own = fh.read()
    clean = _source_is_one_way(own)
    bad = (
        "import gamegen\ndef k(l, p, c):\n    import move as _M\n    return _M.step(l, p, c)\n",
        "import gamegen\ndef f(s, t):\n    import enact as _E\n    return _E.dispatch(s, t)\n",
        "import gamegen\ndef h(t):\n    import statecanon as _S\n    return _S.d_n(*t)\n",
        "import gamegen\ndef d(s):\n    import rngstream as _R\n    return _R.draw(s)\n",
        "z = w.d_n(1)\n",
    )
    bites = all(not _source_is_one_way(b) for b in bad)
    allows = _source_is_one_way("import vista\nimport voxray\ndef h(e, d):\n    return voxray.first_hit(e, d)\n")
    return clean and bites and allows


def refuse_is_total(seed=0, depth=1):
    """Every listed malformed input is a typed BEARING-REFUSE: an id out of range or not an integer, a bool, a
    wall cell, not a Level, a malformed cell, and a missing or altered octant file."""
    import tempfile
    lvl = _G.generate(seed, depth)
    pos = _D.endpoints(lvl)[0]
    wall = next((x, y) for y in range(lvl.h) for x in range(lvl.w) if lvl.cells[y][x:x + 1] == b"#")

    def altered():
        with tempfile.TemporaryDirectory() as td:
            p = _os.path.join(td, OCTANT_FILE)
            with open(_os.path.join(_HERE, OCTANT_FILE), "rb") as src, open(p, "wb") as dst:
                dst.write(src.read().replace(b"\n1 ", b"\n2 ", 1))
            _read_octant(p)

    def missing():
        _read_octant(_os.path.join(_HERE, "no-such-" + OCTANT_FILE))
    cases = (
        lambda: direction(YAW_MOD),
        lambda: direction(-1),
        lambda: direction(1.0),
        lambda: direction(True),
        lambda: frame(lvl, wall, 0),
        lambda: frame("not a level", pos, 0),
        lambda: frame(lvl, (pos[0], "1"), 0),
        lambda: frame(lvl, pos, YAW_MOD + 5),
        missing,
        altered,
    )
    for case in cases:
        try:
            case()
        except BearingError as exc:
            if exc.code != "BEARING-REFUSE":
                return False
            continue
        return False
    return True


# ---- the corpus -------------------------------------------------------------------------------------------------------
#: The adversarial bearings (D26 F6): beside every anchor, the diagonal and its neighbours, and two generic ids.
ADVERSARIAL = (1, 89999, 90001, 179999, 180001, 269999, 270001, 359999, 44999, 45000, 45001, 30000, 123457)
#: The views the corpus renders them from: `vista`'s witness view and its corridor scene.
VIEWS = {"witness": (0xABCDE, 1, (34, 28)), "corridor": None}


def view(name):
    if name not in VIEWS:
        raise BearingError(f"no view named {name!r}")
    if VIEWS[name] is None:
        lvl, pos, _f = _V.scene_view(name)
        return lvl, pos
    seed, depth, pos = VIEWS[name]
    return _G.generate(seed, depth), pos


_CASE_MEMO = {}


def case(name, k):
    """A corpus row: the view, the bearing, its triple, the frame digest and both pictures' pixel sha256."""
    key = (name, k)
    if key in _CASE_MEMO:
        return _CASE_MEMO[key]
    lvl, pos = view(name)
    oriented = _M.tile_set(wall=_M.oriented_tile(*_M.WALL_ORIENTED), floor=_M.oriented_tile(*_M.FLOOR_ORIENTED))
    fb, rgb = picture(lvl, pos, k)
    _fb2, rgb2 = picture(lvl, pos, k, oriented)
    row = ("view=%s/%d/%d/%s|bearing=%d|triple=%d,%d,%d|frame=%s|identity=%s|oriented=%s"
           % (name, lvl.seed, lvl.depth, pos, k, *direction(k), _V.frame_digest(fb), _M.pixel_sha256(rgb),
              _M.pixel_sha256(rgb2)))
    _CASE_MEMO[key] = row
    return row


def case_result(name, k):
    return hashlib.sha256(MAGIC + b"|" + case(name, k).encode()).hexdigest()


def bearing_digest():
    """URDRBRG1's identity: the table's digest folded with every corpus case (D26 F4)."""
    parts = [table_digest()] + [case_result(n, k) for n in sorted(VIEWS) for k in ADVERSARIAL]
    return hashlib.sha256(MAGIC + b"|" + "|".join(parts).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_bearing.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise BearingError(f"no golden named {name!r}")


def emitted_matches_pinned():
    return (table_digest() == golden("table")
            and all(case_result(n, k) == golden("%s:%d" % (n, k)) for n in sorted(VIEWS) for k in ADVERSARIAL)
            and bearing_digest() == golden("bearing"))


def an_unpinned_name_refuses():
    try:
        golden("not-a-case")
    except BearingError as exc:
        return exc.code == "BEARING-REFUSE"
    return False


def main():
    print("BEARING — the heading refinement of the first-person frame; any bearing, the eye at a cell centre (URDRBRG1)")
    print("layer %s: %s" % (LAYER, D24_ANSWER))
    pairs = octant()
    print("vocabulary: %d ids, octant %d pairs (sha256 %s...), largest hypotenuse %d"
          % (YAW_MOD, len(pairs), OCTANT_SHA256[:16], max(_triple_of(pairs, k)[2] for k in range(OCTANT + 1))))
    print("the table holds                    :", the_table_holds())
    print("planted table defects are caught   :", planted_table_defects_are_caught())
    lvl, pos = view("witness")
    print("the anchors are the frozen frames  :", the_anchors_are_the_frozen_frames(lvl, pos))
    print("a mirrored camera is caught        :", a_mirrored_camera_is_caught(lvl, pos))
    print("the C law reads back               :", the_c_law_reads_back(lvl, pos, (45000, 30000, 1)))
    print("the membrane is one-way            :", the_membrane_is_one_way())
    print("refuse is total                    :", refuse_is_total())
    print()
    print("table", table_digest())
    for n in sorted(VIEWS):
        for k in ADVERSARIAL:
            print("%s:%d" % (n, k), case_result(n, k))
    print("bearing", bearing_digest())
    print()
    print("does_not_show: movement between cell centres, pitch, eye height, motion, a frame budget, that the table is")
    print("the best possible, and any wall-clock. A frame at a bearing is a photograph of the certified level.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
