# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""mantle — THE TILE PATH: GEOMETRY FROM `vista`, APPEARANCE FROM A FLAT TILE, AND THE IDENTITY TILE IS THE
CERTIFIED FRAME (URDRMNT1).

TWO EXPERIMENTS SAID WHERE APPEARANCE MAY COME FROM. A generator asked to overpaint the certified frame kept its
topology and lost its metric geometry — the far corridor drawn shorter, every boundary wandering by the width of
a brush (`launcher/assets`, v1, v2, v2s; the ledger's LANDSCAPE-2 entries) — and the conclusion was ratified in
these words: generative overpaint is a useful appearance generator but is not a geometry-preserving renderer
input. This module is the other route. `vista` already knows, per column, the voxel, the entered face and the
exact ray parameter, and per floor pixel the exact world point; it discards them after choosing a class. Here
they are kept one step longer: each becomes an exact rational texture coordinate `(u, v)` on a FLAT tile, the
texel replaces the table's base colour, and the table's own operations — depth tint, the floor's near-darkening,
haze by band — are applied to it unchanged. A generator's job becomes an orthographic square with no geometry
to keep; the geometry is `vista`'s and is never asked of anyone.

WHAT THIS IS, IN THE D24 §1 TERMS: A VIEW OVER A VIEW. It reads a `vista` frame and the view that made it, and
returns RGB bytes. It mints no state, calls no transition, draws from no stream, and its signature cannot receive
a `D_n`, a stream or a log — the one-way discipline `kinema`, `chorus`, `cue` and `vista` carry, read off this
module's own AST by `the_membrane_is_one_way`. It never writes the index frame: the URDRFB1 digest is the same
object before and after a picture (`the_lookup_moves_no_index`, with the one-index write shown to move it).

THE IDENTITY IS THE LAW THIS RUNG SHIPS WITH. The table's flat colours, taken as tiles, reproduce
`vista.png_bytes`' pixels EXACTLY (`the_identity_tiles_reproduce_the_frame`, the planted one-unit perturbation
caught). The certified emission is therefore the tile path at the identity, the tile path is a strict
generalisation of it, and a missing tile IS the identity (`a_missing_tile_is_the_identity`): no file, no
crash, no different geometry — the asset contract the measurement batch found absent (LANDSCAPE-2, M1).

THE COORDINATE LAW IS EXACT AND VIEW-INDEPENDENT. A wall texel's `u` is the world coordinate along the face,
modulo the cell, with a sign fixed per face so it grows to the right of the viewer who faces that face head-on
(each face is only ever entered from its outside); its `v` is the world height below the wall's top edge. A
floor texel is the world point's fractional cell coordinate. All of it is integer arithmetic over the rationals
`vista` already holds; a texel is one world unit (`T = Q`). `a_texel_is_seen_where_its_face_is` reads the
consequences off a frame: `u` monotone across every wall primitive, falling exactly at every coplanar seam,
`v` growing downward, and the floor's texel wrapping at a cell change and nowhere else in the rows one screen
row samples finely enough — with the mirrored sign table caught.

GRADE (honest, D5). MEASURED: the corpus pictures reproduce (pixel sha256 pinned beside the URDRFB1 digest,
two witnesses side by side, never one), hash-seed-independent; the identity law with its planted control; the
no-write law with its planted control; the coordinate law with its mirrored control; the class law with its
swapped control; the missing-tile contract; the gate's live-core row shows `D_n` byte-identical with a picture
made every turn. ESTABLISHED: the AST is one-way; no CORE module imports `mantle`. DECLARED: the texel size
(one world unit), the per-face sign table, the light scaling derived from the table's own wall families, the
synthetic tiles the corpus pins. does_not_show: any GENERATED tile (none is consumed here — a tile is bytes,
its file is the launcher's), filtering (one screen column covers from a sixth of a texel to fifty on one frame,
and one row skips more than half a cell of far floor: an unfiltered lookup aliases there, and a filtered level
is its own rung, not this one), stairs (`<`/`>` stay the table's), the sky, pitch, yaw, any wall-clock."""
import ast
import hashlib
import os as _os
import struct as _struct
import zlib as _zlib

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_RENDER = _os.path.join(_os.path.dirname(_HERE), "render")
for _p in (_HERE, _RENDER):
    if _p not in __import__("sys").path:
        __import__("sys").path.insert(0, _p)
import gamegen as _G                                                    # noqa: E402  (the level, READ)
import vista as _V                                                      # noqa: E402  (the frame and its geometry)
import raster as _RS                                                    # noqa: E402  (the URDRFB1 frame type)

MAGIC = b"URDRMNT1"

LAYER = "VIEW"
D24_ANSWER = "colours a vista frame from flat tiles by exact texture coordinates — a one-way view over a view (the identity tile is the certified frame; the index frame is read, never written)"
ALLOWED_IMPORTS = ("ast", "hashlib", "os", "struct", "zlib", "gamegen", "vista", "raster")

#: DECLARED. A texel is one world unit: a tile is Q x Q texels, the size of a cell's face. Written as an
#: expression so it is not a bare literal.
T = _V.Q
TILE_BYTES = T * T * 3
W, H, Q, CX, CY, FOCAL, EYE_Y, BANDS = _V.W, _V.H, _V.Q, _V.CX, _V.CY, _V.FOCAL, _V.EYE_Y, _V.BANDS
CLASSES = ("wall", "floor")
LIGHTS = len(_V.WALL_RGB)

#: DECLARED sign of `u` per entered face: the world axis along the face, oriented to the RIGHT of the viewer
#: who faces the face head-on (voxray's ENTRY_FACE: 0 = the +x face, entered moving -x; 1 = the -x face; 4 =
#: the +z face; 5 = the -z face). A face is only ever entered from its outside, so the table is view-free.
U_SIGN = {1: 1, 0: -1, 5: -1, 4: 1}
U_AXIS = {0: 2, 1: 2, 4: 0, 5: 0}                       # the world axis `u` runs along: z for x-faces, x for z-faces

#: Read off THIS module's full AST by `the_membrane_is_one_way`.
_FORBIDDEN_MODULES = frozenset({"move", "descend", "loot", "enact", "statecanon", "rerun", "savegame", "lockstep",
                                "actionlog", "rngstream", "entity", "cue", "chorus", "descent", "voxray"})
_FORBIDDEN_ATTRS = frozenset({"step", "dispatch", "apply", "d_n", "d_n_preimage", "serialize", "restore"})


class MantleError(Exception):
    def __init__(self, message):
        super().__init__(f"MANTLE-REFUSE: {message}")
        self.code = "MANTLE-REFUSE"


# ---- the light families, derived from the table, never invented -------------------------------------------
def _lum(c):
    return (54 * c[0] + 183 * c[1] + 19 * c[2]) // 256


#: The table's four wall families as brightness relative to the brightest, in permille — what a single wall
#: tile is scaled by, once per light class, so that the emission below applies exactly the table's operations.
LIGHT_PERMILLE = tuple(1000 * _lum(c) // _lum(_V.WALL_RGB[0]) for c in _V.WALL_RGB)


# ---- tiles --------------------------------------------------------------------------------------------------
def _check_tile(tile, what):
    if not isinstance(tile, (bytes, bytearray)):
        raise MantleError(f"{what} tile must be bytes, got {type(tile).__name__}")
    if len(tile) != TILE_BYTES:
        raise MantleError(f"{what} tile must be {T}x{T} RGB ({TILE_BYTES} bytes), got {len(tile)} bytes")
    return bytes(tile)


def flat_tile(rgb):
    """A T x T tile of one colour."""
    if not (isinstance(rgb, tuple) and len(rgb) == 3 and all(isinstance(v, int) and 0 <= v <= 255 for v in rgb)):
        raise MantleError(f"a flat tile needs an RGB triple of bytes, got {rgb!r}")
    return bytes(rgb) * (T * T)


def _scaled(tile, permille):
    if permille == 1000:
        return tile
    return bytes((v * permille) // 1000 for v in tile)


def identity_tiles():
    """The table's own colours as tiles: four flat wall tiles (one per light family, the table's WALL_RGB) and
    the flat FLOOR_RGB. `picture` with these is `vista.png_bytes` pixel for pixel — the law below."""
    return {"wall": tuple(flat_tile(c) for c in _V.WALL_RGB), "floor": flat_tile(_V.FLOOR_RGB)}


def tile_set(wall=None, floor=None):
    """A material: a wall tile (scaled once per light family, by the table's own brightness ratios) and a floor
    tile. A MISSING tile is the identity for its class — no file, no crash, no different geometry."""
    ident = identity_tiles()
    if wall is None:
        walls = ident["wall"]
    else:
        wall = _check_tile(wall, "wall")
        walls = tuple(_scaled(wall, p) for p in LIGHT_PERMILLE)
    floor_t = ident["floor"] if floor is None else _check_tile(floor, "floor")
    return {"wall": walls, "floor": floor_t}


def _check_tiles(tiles):
    if not (isinstance(tiles, dict) and set(tiles) == set(CLASSES)):
        raise MantleError(f"tiles must be a tile set over {CLASSES} (see tile_set), got {type(tiles).__name__}")
    walls = tiles["wall"]
    if not (isinstance(walls, tuple) and len(walls) == LIGHTS):
        raise MantleError(f"a tile set carries {LIGHTS} wall tiles, one per light family")
    for i, t in enumerate(walls):
        _check_tile(t, f"wall[{i}]")
    _check_tile(tiles["floor"], "floor")


def tiles_digest(tiles):
    """The material's identity: sha256 over MAGIC and the tile bytes in class order."""
    _check_tiles(tiles)
    h = hashlib.sha256(MAGIC)
    for t in tiles["wall"]:
        h.update(t)
    h.update(tiles["floor"])
    return h.hexdigest()


def oriented_tile(a, b):
    """The DECLARED synthetic tile the corpus pins: a checker of T/8 squares in colours `a`/`b`, a red block at
    (u, v) = (0, 0), a green band along the u axis (v small) and a yellow band along the v axis (u small) — so a
    picture shows where each face's and each cell's origin and axes landed."""
    sq, corner, band = T >> 3, T >> 2, T >> 4
    red, green, yellow = (220, 40, 40), (40, 200, 60), (230, 220, 40)
    out = bytearray()
    for j in range(T):
        for i in range(T):
            col = a if ((i // sq) + (j // sq)) % 2 == 0 else b
            if i < corner and j < corner:
                col = red
            elif j < band:
                col = green
            elif i < band:
                col = yellow
            out += bytes(col)
    return bytes(out)


WALL_ORIENTED = (90, 120, 200), (60, 85, 160)              # a blue family, like the table's walls
FLOOR_ORIENTED = (200, 140, 70), (160, 105, 50)            # a warm family, like the table's floor


# ---- the coordinate law ---------------------------------------------------------------------------------------
def _strips(level, pos, facing):
    """Per column: (vox, face, tn, td, top, bot, band, dx, dz) — what `vista` holds at selection, kept."""
    out = []
    for c in range(W):
        vox, face, (tn, td), top, bot, band = _V.strip(level, pos, facing, c)
        dx, dz = _V._direction(facing, c)
        out.append((vox, face, tn, td, top, bot, band, dx, dz))
    return out


def wall_u(eye, s, usign=U_SIGN):
    """(num, den): the fraction of a cell along the face at this column's hit point, `u` in [0, 1) — the world
    coordinate along the face (P = E + t*D, exact), signed per face, modulo the cell."""
    vox, face, tn, td, _top, _bot, _band, dx, dz = s
    ex, _ey, ez = eye
    along = ez * td + tn * dz if U_AXIS[face] == 2 else ex * td + tn * dx      # P_along * td
    if usign[face] < 0:
        along = -along
    return along % (Q * td), Q * td


def wall_v(s, row):
    """(num, den): the fraction of the wall's height below its top edge at this row's centre — the row centre
    projects to world height y = EYE_Y + (2*CY - 2*row - 1) * t, and v = (Q - y) / Q."""
    _vox, _face, tn, td, _top, _bot, _band, _dx, _dz = s
    y_num = EYE_Y * td + (2 * CY - 2 * row - 1) * tn                          # y * td
    return Q * td - y_num, Q * td


def floor_point(eye, s, row):
    """(px_num, pz_num, den): the exact world point the floor pixel sees, `E + D*EYE_Y/kk` for the row centre
    `kk/2` below the horizon — `vista`'s own inverse projection; its floor is the cell, its fraction the texel."""
    _vox, _face, _tn, _td, _top, _bot, _band, dx, dz = s
    ex, _ey, ez = eye
    kk = 2 * (row - CY) + 1
    return ex * kk + dx * EYE_Y, ez * kk + dz * EYE_Y, kk * Q


def texel(num, den):
    """floor(T * num / den), clamped into the tile — an integer division of integers."""
    i = (num * T) // den
    return T - 1 if i >= T else 0 if i < 0 else i


# ---- the picture ----------------------------------------------------------------------------------------------
def _band_tables(depth):
    """Per depth band, the table's per-channel operations as 256-entry maps — exact because haze is achromatic
    and the depth tint is one factor, so every channel goes through the same integer function. `wall[band][v]`
    is `_mix(_scale(v, tint), haze, band)`; `floor[band][v]` adds the floor's near-darkening in between. These
    are the LUT's own formulas, evaluated for every byte instead of for one base colour."""
    t_tint = min(_V.DEPTH_TINT_CELLS, depth - 1)
    haze = _V._scale(_V.HAZE, 100 * _V.DEPTH_TINT_CELLS - 30 * t_tint, 100 * _V.DEPTH_TINT_CELLS)
    lum_n, lum_d = 100 * _V.DEPTH_TINT_CELLS - 25 * t_tint, 100 * _V.DEPTH_TINT_CELLS
    wall, floor = [], []
    for band in range(BANDS):
        f_n, f_d = _V.HAZE_MAX_PERMILLE * band, 1000 * (BANDS - 1)
        near_n, near_d = 75 * (BANDS - 1) + 25 * band, 100 * (BANDS - 1)
        wall.append(bytes(_V._mix(_V._scale((v, v, v), lum_n, lum_d), haze, f_n, f_d)[0] for v in range(256)))
        floor.append(bytes(_V._mix(_V._scale(_V._scale((v, v, v), lum_n, lum_d), near_n, near_d), haze, f_n, f_d)[0]
                           for v in range(256)))
    return tuple(wall), tuple(floor)


def _emit(fb, level, pos, facing, tiles, strips=None):
    """RGB bytes. The index frame is READ for class, light and band; (u, v) come from the geometry; the texel
    replaces the table's base colour and receives exactly the table's own operations (per-band maps). Nothing
    is written to `fb`, `level` or anywhere."""
    table = _V.lut(level.depth)
    wall_map, floor_map = _band_tables(level.depth)
    strips = _strips(level, pos, facing) if strips is None else strips
    eye = _V._eye(pos)
    ex, _ey, ez = eye
    buf = fb.buf
    walls, floor_t = tiles["wall"], tiles["floor"]
    WALL0, FLOOR0, DOWN0 = _V.WALL0, _V.FLOOR0, _V.DOWN0
    out = bytearray(W * H * 3)
    for c in range(W):
        s = strips[c]
        top, bot = s[4], s[5]
        u_n, u_d = wall_u(eye, s)
        ti = texel(u_n, u_d)
        tn, td, dx, dz = s[2], s[3], s[7], s[8]
        v_base = Q * td - EYE_Y * td - (2 * CY - 1) * tn                      # v numerator at row 0, +2*tn per row
        v_den = Q * td
        for r in range(0, top):
            o = (r * W + c) * 3
            out[o:o + 3] = bytes(table[buf[r * W + c]])
        for r in range(top, bot + 1):
            idx = buf[r * W + c]
            o = (r * W + c) * 3
            if idx < WALL0:
                out[o:o + 3] = bytes(table[idx])                               # ink rows keep the table
                continue
            light, band = (idx - WALL0) // BANDS, (idx - WALL0) % BANDS
            k = (texel(v_base + 2 * r * tn, v_den) * T + ti) * 3
            tile, m = walls[light], wall_map[band]
            out[o] = m[tile[k]]
            out[o + 1] = m[tile[k + 1]]
            out[o + 2] = m[tile[k + 2]]
        for r in range(bot + 1, H):
            idx = buf[r * W + c]
            o = (r * W + c) * 3
            if idx < FLOOR0 or idx >= DOWN0:
                out[o:o + 3] = bytes(table[idx])                               # stairs stay the table's
                continue
            kk = 2 * (r - CY) + 1
            den = kk * Q
            k = (texel((ez * kk + dz * EYE_Y) % den, den) * T + texel((ex * kk + dx * EYE_Y) % den, den)) * 3
            m = floor_map[idx - FLOOR0]
            out[o] = m[floor_t[k]]
            out[o + 1] = m[floor_t[k + 1]]
            out[o + 2] = m[floor_t[k + 2]]
    return bytes(out)


def picture(level, pos, facing, tiles=None):
    """(frame, rgb): the certified `vista` frame of the view and its picture through the tiles (the identity
    when `tiles` is None). The frame is `vista`'s object, unwritten; the picture is bytes, W*H*3."""
    tiles = identity_tiles() if tiles is None else tiles
    _check_tiles(tiles)
    fb = _V.frame(level, pos, facing)
    return fb, _emit(fb, level, pos, facing, tiles)


def pixel_sha256(rgb):
    """The picture's identity: sha256 of its RGB bytes — never of a PNG file (containers differ by host)."""
    return hashlib.sha256(bytes(rgb)).hexdigest()


def table_pixels(fb, depth):
    """`vista.png_bytes`' pixels, without the container: the certified emission the identity must equal."""
    table = _V.lut(depth)
    out = bytearray()
    for v in fb.buf:
        out += bytes(table[v])
    return bytes(out)


def png_bytes(rgb, w=W, h=H):
    """RGB bytes as a PNG — a CONTAINER, not an identity (zlib output is a library's; see pixel_sha256)."""
    if len(rgb) != w * h * 3:
        raise MantleError(f"png_bytes needs {w * h * 3} RGB bytes for {w}x{h}, got {len(rgb)}")
    rows = bytearray()
    for r in range(h):
        rows.append(0)
        rows += rgb[r * w * 3:(r + 1) * w * 3]

    def chunk(tag, data):
        c = tag + data
        return _struct.pack(">I", len(data)) + c + _struct.pack(">I", _zlib.crc32(c) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", _struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", _zlib.compress(bytes(rows), 6)) + chunk(b"IEND", b""))


# ---- laws -------------------------------------------------------------------------------------------------------
def _ctx_of(level, pos, facing, ctx):
    """(frame, strips): shared by the laws of one scene, so a scene pays one frame and one strip pass."""
    if ctx is not None:
        return ctx
    return _V.frame(level, pos, facing), _strips(level, pos, facing)


def the_identity_tiles_reproduce_the_frame(level, pos, facing, _ctx=None):
    """(reproduces, planted_caught). The table's colours as tiles give `vista.png_bytes`' pixels EXACTLY — the
    certified emission is the tile path at the identity. Positive control: every flat tile perturbed by one
    unit of red is not the frame."""
    fb, strips = _ctx_of(level, pos, facing, _ctx)
    rgb = _emit(fb, level, pos, facing, identity_tiles(), strips)
    same = rgb == table_pixels(fb, level.depth)
    planted = {"wall": tuple(flat_tile((min(255, c[0] + 1), c[1], c[2])) for c in _V.WALL_RGB),
               "floor": flat_tile((min(255, _V.FLOOR_RGB[0] + 1),) + tuple(_V.FLOOR_RGB[1:]))}
    return same, _emit(fb, level, pos, facing, planted, strips) != rgb


def the_lookup_moves_no_index(level, pos, facing, tiles=None, _ctx=None):
    """(frame_unmoved, level_unmoved, a_written_index_moves_the_digest). After a picture, the frame it was made
    from has the URDRFB1 digest of a FRESH `vista.frame` and the level's canonical bytes are unchanged; the
    positive control writes ONE index into a copy of the frame and the digest moves — the witness is not
    vacuous."""
    tiles = identity_tiles() if tiles is None else tiles
    _check_tiles(tiles)
    before = _G.canon_bytes(level)
    fb, strips = _ctx_of(level, pos, facing, _ctx)
    _emit(fb, level, pos, facing, tiles, strips)
    fresh = _V.frame_digest(_V.frame(level, pos, facing))
    frame_ok = _V.frame_digest(fb) == fresh
    level_ok = _G.canon_bytes(level) == before
    cp = _RS.Framebuffer(fb.w, fb.h)
    cp.buf = list(fb.buf)
    cp.buf[0] = _V.INK if cp.buf[0] != _V.INK else _V.SKY0
    return frame_ok, level_ok, _V.frame_digest(cp) != fresh


def _well_sampled_from(eye, s):
    """The first row at this column from which one row step moves the floor point by at most half a cell on
    both axes: |D_axis| * EYE_Y * 4 <= kk * (kk + 2) * Q."""
    _vox, _face, _tn, _td, _top, _bot, _band, dx, dz = s
    need = 4 * EYE_Y * max(abs(dx), abs(dz))
    r = CY + 1
    while r < H - 1:
        kk = 2 * (r - CY) + 1
        if need <= kk * (kk + 2) * Q:
            return r
        r += 1
    return H


def _coordinate_law(level, pos, facing, usign, strips=None):
    strips = _strips(level, pos, facing) if strips is None else strips
    eye = _V._eye(pos)
    prims = []
    for c in range(W):
        key = (strips[c][0], strips[c][1])
        if not prims or prims[-1][0] != key:
            prims.append([key, c, c])
        else:
            prims[-1][2] = c
    mono = True
    for _key, c0, c1 in prims:
        prev = None
        for c in range(c0, c1 + 1):
            n, d = wall_u(eye, strips[c], usign)
            if prev is not None and n * prev[1] < prev[0] * d:          # u fell inside a face
                mono = False
            prev = (n, d)
    seams_ok = True
    for i in range(1, len(prims)):
        (va, fa), _c0, cl = prims[i - 1]
        (vb, fbf), cr, _c1 = prims[i]
        axis = 0 if fa in (4, 5) else 2
        if fa == fbf and va[axis] == vb[axis]:                           # coplanar neighbours: u must fall
            ln, ld = wall_u(eye, strips[cl], usign)
            rn, rd = wall_u(eye, strips[cr], usign)
            if not rn * ld < ln * rd:
                seams_ok = False
    v_down = True
    for _key, c0, c1 in prims:
        c = (c0 + c1) // 2
        top, bot = strips[c][4], strips[c][5]
        if bot - top >= 4:
            tn_, td_ = wall_v(strips[c], top + 1)
            bn_, bd_ = wall_v(strips[c], bot - 1)
            if not tn_ * bd_ < bn_ * td_:
                v_down = False
    floor_ok = True
    half = T >> 1
    for c in range(0, W, W >> 8):
        s = strips[c]
        start = max(s[5] + 1, _well_sampled_from(eye, s) + 2)
        prev = None
        for r in range(start, H):
            px, pz, den = floor_point(eye, s, r)
            cur = (px // den, pz // den, texel(px % den, den), texel(pz % den, den))
            if prev is not None:
                changed = cur[:2] != prev[:2]
                jumped = abs(cur[2] - prev[2]) > half or abs(cur[3] - prev[3]) > half
                if changed != jumped:
                    floor_ok = False
            prev = cur
    return mono, seams_ok, v_down, floor_ok


def a_texel_is_seen_where_its_face_is(level, pos, facing, _ctx=None):
    """(u_monotone, seams_fall, v_grows_down, floor_wraps_at_cells_only, mirrored_caught). Read off the
    geometry of a frame: across every wall primitive `u` never falls; at every coplanar seam it falls (the
    wrap is where the voxel edge is); `v` grows downward on every primitive tall enough to ask; on the floor,
    in the rows one screen row samples finely enough, the texel wraps at a cell change and nowhere else.
    Positive control: the mirrored sign table fails the monotone or the seam law."""
    _V._check(level, pos, facing)
    _fb, strips = _ctx_of(level, pos, facing, _ctx)
    mono, seams, vdown, floor_ok = _coordinate_law(level, pos, facing, U_SIGN, strips)
    mirrored = {f: -s for f, s in U_SIGN.items()}
    m_mono, m_seams, _mv, _mf = _coordinate_law(level, pos, facing, mirrored, strips)
    return mono, seams, vdown, floor_ok, not (m_mono and m_seams)


def _readback(fb, rgb):
    wc = wt = fw = ft = 0
    buf = fb.buf
    for i in range(W * H):
        cl = buf[i]
        if cl >= _V.WALL0:
            wt += 1
            wc += rgb[i * 3 + 2] > rgb[i * 3]
        elif _V.FLOOR0 <= cl < _V.DOWN0:
            ft += 1
            fw += rgb[i * 3] > rgb[i * 3 + 2]
    return (wc == wt and wt > 0), (fw == ft and ft > 0)


def the_classes_stay_apart(level, pos, facing):
    """(every_wall_pixel_cool, every_floor_pixel_warm, swapped_caught). With a flat blue wall tile and a flat
    warm floor tile, EVERY wall pixel reads cool and EVERY floor pixel warm after light and haze — a wall tile
    never lands on a floor pixel nor the reverse. Positive control: the tiles swapped fail both."""
    blue, warm = flat_tile(WALL_ORIENTED[0]), flat_tile(FLOOR_ORIENTED[0])
    fb, rgb = picture(level, pos, facing, tile_set(wall=blue, floor=warm))
    cool, warm_ok = _readback(fb, rgb)
    _fb2, rgb2 = picture(level, pos, facing, tile_set(wall=warm, floor=blue))
    s_cool, s_warm = _readback(fb, rgb2)
    return cool, warm_ok, not (s_cool or s_warm)


def a_missing_tile_is_the_identity():
    """(none_is_identity, missing_class_is_identity, malformed_refused). `tile_set()` is `identity_tiles()`
    byte for byte; a set with only a wall tile keeps the identity floor and the reverse; a tile of the wrong
    size or type is refused typed, never silently substituted."""
    ident = identity_tiles()
    none_ok = tile_set() == ident
    w = oriented_tile(*WALL_ORIENTED)
    only_wall = tile_set(wall=w)
    only_floor = tile_set(floor=w)
    partial_ok = (only_wall["floor"] == ident["floor"] and only_wall["wall"] != ident["wall"]
                  and only_floor["wall"] == ident["wall"] and only_floor["floor"] == w)
    refused = 0
    for bad in (b"\x00" * (TILE_BYTES - 3), "not bytes", 7, w + b"\x00"):
        try:
            tile_set(wall=bad)
        except MantleError as exc:
            refused += exc.code == "MANTLE-REFUSE"
    return none_ok, partial_ok, refused == 4


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
    """STRUCTURAL, read off this module's OWN full AST, function-local imports included: exactly the declared
    substrate (`gamegen` read, `vista`, `raster`, stdlib), no transition/identity/log/stream authority in any
    scope — not even `descent` or `voxray`, which `vista` already answers for — and no `.step`/`.dispatch`/
    `.apply`/`.d_n`/`.serialize`/`.restore`. Positive controls: sources that step, dispatch, ingest `D_n`,
    draw a stream, restore a save or reach the oracle directly are each REJECTED; the frame path is accepted."""
    with open(_os.path.join(_HERE, "mantle.py"), encoding="utf-8") as fh:
        own = fh.read()
    clean = _source_is_one_way(own)
    bad = (
        "import vista\ndef k(l, p, c):\n    import move as _M\n    return _M.step(l, p, c)\n",
        "import vista\ndef f(s, t):\n    import enact as _E\n    return _E.dispatch(s, t)\n",
        "import vista\ndef h(t):\n    import statecanon as _S\n    return _S.d_n(*t)\n",
        "import vista\ndef d(s):\n    import rngstream as _R\n    return _R.draw(s)\n",
        "import vista\ndef g(r):\n    import savegame as _V\n    return _V.restore(r)\n",
        "import vista\nimport voxray\ndef o(e, d):\n    return voxray.first_hit(e, d)\n",
        "z = w.d_n(1)\n",
        "y = x.apply(1)\n",
    )
    bites = all(not _source_is_one_way(b) for b in bad)
    allows = _source_is_one_way(
        "import vista\nimport raster\ndef h(l, p, f):\n    return vista.frame(l, p, f), raster.Framebuffer(2, 2)\n")
    return clean and bites and allows


def refuse_is_total():
    """Every listed malformed input is typed: a malformed tile set, a tile of the wrong size, a bad PNG length,
    a bad flat colour, an unpinned golden name are MANTLE-REFUSE; a view `vista` refuses stays VISTA-REFUSE."""
    lvl, pos, _facing = _V.scene_view("corridor")
    ident = identity_tiles()
    mine = (
        lambda: picture(lvl, pos, "N", {"wall": ident["wall"]}),
        lambda: picture(lvl, pos, "N", {"wall": ident["wall"][:3], "floor": ident["floor"]}),
        lambda: picture(lvl, pos, "N", {"wall": ident["wall"], "floor": ident["floor"][:-1]}),
        lambda: tile_set(floor=b"short"),
        lambda: flat_tile((1, 2)),
        lambda: flat_tile((1, 2, 999)),
        lambda: png_bytes(b"\x00" * 7),
        lambda: tiles_digest("not tiles"),
        lambda: golden("not-a-scene"),
    )
    for case in mine:
        try:
            case()
        except MantleError as exc:
            if exc.code != "MANTLE-REFUSE":
                return False
            continue
        return False
    wall = next((x, y) for y in range(lvl.h) for x in range(lvl.w) if lvl.cells[y][x:x + 1] == b"#")
    theirs = (
        lambda: picture(lvl, wall, "N"),
        lambda: picture(lvl, pos, "NE"),
        lambda: picture("not a level", pos, "N"),
    )
    for case in theirs:
        try:
            case()
        except _V.VistaError as exc:
            if exc.code != "VISTA-REFUSE":
                return False
            continue
        return False
    return True


# ---- scenes -----------------------------------------------------------------------------------------------------
#: `vista`'s four views, unchanged — the tile path is measured over the frames the frame rung pinned. Each scene
#: makes two pictures: the identity (which must be the certified pixels) and the DECLARED oriented tiles.
SCENES = tuple(_V.SCENES)


def scene_view(name):
    if name not in SCENES:
        raise MantleError(f"no scene named {name!r}")
    return _V.scene_view(name)


_SCENE_MEMO = {}


def scene_case(name):
    """A scene's row string: the view, the URDRFB1 frame digest and the identity picture's pixel sha256 (two
    witnesses, side by side), the oriented picture's pixel sha256 and its tile digest, and the laws over the
    same frame. Memoised per process (a scene costs two frames, one strip pass and four pictures)."""
    if name in _SCENE_MEMO:
        return _SCENE_MEMO[name]
    lvl, pos, facing = scene_view(name)
    oriented = tile_set(wall=oriented_tile(*WALL_ORIENTED), floor=oriented_tile(*FLOOR_ORIENTED))
    fb = _V.frame(lvl, pos, facing)
    ctx = (fb, _strips(lvl, pos, facing))
    rgb_id = _emit(fb, lvl, pos, facing, identity_tiles(), ctx[1])
    rgb_or = _emit(fb, lvl, pos, facing, oriented, ctx[1])
    row = ("view=%d/%d/%s/%s|frame=%s|identity=%s|oriented=%s|tiles=%s|identity_law=%s|lookup=%s|texel=%s"
           % (lvl.seed, lvl.depth, pos, facing, _V.frame_digest(fb), pixel_sha256(rgb_id), pixel_sha256(rgb_or),
              tiles_digest(oriented)[:16], the_identity_tiles_reproduce_the_frame(lvl, pos, facing, ctx),
              the_lookup_moves_no_index(lvl, pos, facing, oriented, ctx),
              a_texel_is_seen_where_its_face_is(lvl, pos, facing, ctx)))
    _SCENE_MEMO[name] = row
    return row


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|" + scene_case(name).encode()).hexdigest()


def mantle_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n) for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_mantle.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MantleError(f"no golden named {name!r}")


def emitted_matches_pinned():
    return (all(scene_result(n) == golden(n) for n in SCENES)
            and mantle_digest() == golden("mantle"))


def an_unpinned_name_refuses():
    try:
        golden("not-a-scene")
    except MantleError as exc:
        return exc.code == "MANTLE-REFUSE"
    return False


def main():
    print("MANTLE — the tile path: geometry from vista, appearance from a flat tile; the identity tile is the certified frame (URDRMNT1)")
    print("layer %s: %s" % (LAYER, D24_ANSWER))
    print("texel = one world unit (T=%d, a tile is %d bytes); light families %s permille; u sign per face %s"
          % (T, TILE_BYTES, LIGHT_PERMILLE, U_SIGN))
    print()
    for n in SCENES:
        print(n, scene_case(n))
    lvl, pos, facing = scene_view("corridor")
    print()
    print("the classes stay apart          :", the_classes_stay_apart(lvl, pos, facing))
    print("a missing tile is the identity  :", a_missing_tile_is_the_identity())
    print("the membrane is one-way         :", the_membrane_is_one_way())
    print("refuse is total                 :", refuse_is_total())
    print()
    for n in SCENES:
        print(n, scene_result(n))
    print("mantle", mantle_digest())
    print()
    print("does_not_show: any generated tile (a tile is bytes; its file is the launcher's), filtering (its own rung),")
    print("stairs, the sky, pitch, yaw, any wall-clock. A picture is the certified frame wearing a tile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
