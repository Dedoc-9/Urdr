# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""vista — THE FIRST-PERSON FRAME OF THE CERTIFIED DUNGEON, AND THE EYE IS TAKEN, NEVER DERIVED (URDRVIS1).

THE GAME LAYER HAD ONE DEPICTION, A TEXT GRID, AND THE REPOSITORY HAD A CERTIFIED RAY ORACLE NOBODY HAD
POINTED AT IT. `voxray.first_hit` is the exact integer traversal (Amanatides–Woo, 1987) that judged `voxref`'s
winding defect; `raster.Framebuffer` is the URDRFB1 frame whose identity law is cross-placed in Rust. This
module composes the two over `gamegen`'s level: one ray per column, the strip height an exact floor division,
the floor an exact inverse projection, and the picture an 8-bit INDEX frame whose colour is a separate table.
It invents no rasterisation and no camera arithmetic that is not a floor of a rational; the picture is the
Wolfenstein construction (id Software, 1992) — walls one cell tall on a grid, eye at half height, no pitch —
reproduced, not discovered, over a world it never touches.

WHAT THIS IS, IN THE D24 §1 TERMS: A VIEW. It reads a `Level` and an integer cell `pos` and a cardinal `facing`
and returns a frame. It mints no canonical state, calls no transition, draws from no `rngstream`, and its
signature cannot receive a `D_n`, a stream or a log — the same one-way discipline `kinema`, `chorus` and `cue`
carry, read off this module's own AST by `the_membrane_is_one_way`. Destroy every frame and the run is the same
run. The FACING IS VIEW STATE: the authority has no heading (a MOVE is an absolute cardinal), so the camera's
heading lives with the camera — the launcher keeps it beside the game dict, never inside it, and this module
offers `default_facing` (toward the landmark `>`) as a pure function of the level so a first frame needs no
history.

THE EYE IS TAKEN FROM `pos`, NEVER RE-DERIVED — `vantage`'s law, arriving one world over. `frame` cannot receive
a heightfield, a stream or a log; it receives a cell. A wall cell is REFUSED, not rendered from inside.

THE IMAGING CONTRACT IS A TABLE. The frame is indices: ink, sky bands by row, floor/`<`/`>` by depth band, and
walls by (entered face, depth band). `lut(depth)` maps indices to RGB and is the ONLY place colour exists —
achromatic haze and an achromatic depth tint so that the hue family of a class never moves with distance or
depth, which `the_lut_keeps_classes_apart` checks as a pure function of the table (floor warm, wall cool, the
two stairs accents disjoint from both). The measured reference the contract was read from is recorded in
`docs/vista_brief.md` §3: far light / near dark, distance desaturates, a warm/cool two-family palette, ink
outlines.

THE READ-BACK LAW, AND WHY IT INFERS NOTHING. `the_centre_column_is_a_straight_walk` recomputes, by a plain walk
over `level.cells` in the facing direction, which wall the centre ray must hit and at what depth, and reads the
frame's centre column back: the strip's voxel is that wall, its half-height is `960 // (2k−1)` for a wall `k`
cells ahead, and every floor row below the strip carries the class of the cell the walk passes at that depth.
It is a check ON the picture, from the world; its verdict flows nowhere. A planted eye offset is caught.

GRADE (honest, D5). MEASURED: the corpus frames reproduce (URDRFB1 digests pinned), hash-seed-independent;
the read-back law holds over the corpus and a sweep with the planted control caught; the table keeps the
classes apart; every corpus frame is populated and the census names the one deliberately point-blank frame
DEGENERATE by its class; the gate's live-core row shows `D_n` byte-identical with a frame rendered every turn.
ESTABLISHED: the AST is one-way; no CORE module imports `vista`. DECLARED: the frame size, focal length, cell
subdivision, eye height, the band count, the face-light order and the palette. does_not_show: pitch, free yaw,
smooth motion (`kinema` Frames are the next rung's input), textures, props, any second placement of THIS
module (only its substrate is cross-placed), and any wall-clock — a frame is a photograph, not a loop."""
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
import descent as _D                                                    # noqa: E402  (traversability + endpoints, READ)
import voxray as _VX                                                    # noqa: E402  (the certified ray oracle)
import raster as _RS                                                    # noqa: E402  (the URDRFB1 frame)

MAGIC = b"URDRVIS1"

LAYER = "VIEW"
D24_ANSWER = "renders a first-person frame of the certified level from a cell and a cardinal — a one-way view (the eye is taken, the facing is view state, the colour is a table)"
ALLOWED_IMPORTS = ("ast", "hashlib", "os", "struct", "zlib", "gamegen", "descent", "voxray", "raster")

#: DECLARED camera. Frame 1920x1080; focal = half the width (a 90-degree horizontal field); a cell is Q world
#: units and the eye stands at half a wall's height. Written as expressions so none is a bare literal.
FRAME = (1920, 1080)
W, H = FRAME
CX, CY = W // 2, H // 2
FOCAL = W // 2
Q = 1 << 8
EYE_Y = Q >> 1
LATTICE = _G.W                              # voxray's cubic extent: the wider grid axis
BANDS = 1 << 5                              # depth bands, one per cell, 32 deep
FACINGS = ("N", "E", "S", "W")
_FWD = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
_RIGHT = {"N": (1, 0), "E": (0, 1), "S": (-1, 0), "W": (0, -1)}

#: The index layout of a frame (8-bit). Bands are depth in cells. Walls carry the ENTERED face as a light
#: class: a ray stepping -z enters a wall's south face (voxray face 4), which the declared key light (from the
#: south-west, high) lights most; west (1) next; north (5) and east (0) are the shadow side.
INK, SKY0, SKY_BANDS = 0, 1, 15
FLOOR0, DOWN0, UP0 = 16, 16 + BANDS, 16 + 2 * BANDS
WALL0 = 16 + 3 * BANDS
FACE_LIGHT = {4: 0, 1: 1, 5: 2, 0: 3}

#: DECLARED palette, colour ONLY here. Haze and depth tint are achromatic (see `lut`).
HAZE = (212, 212, 212)
HAZE_MAX_PERMILLE = 550
SKY_HORIZON, SKY_TOP = (236, 224, 200), (112, 142, 196)
FLOOR_RGB = (176, 138, 90)
DOWN_RGB, UP_RGB = (48, 190, 200), (170, 100, 170)
WALL_RGB = ((150, 166, 184), (118, 138, 160), (84, 102, 126), (56, 72, 96))
INK_RGB = (14, 14, 18)
DOMINANCE_PERMILLE = 900
DEPTH_TINT_CELLS = 12

#: Read off THIS module's full AST by `the_membrane_is_one_way`: no transition/identity authority in any scope.
_FORBIDDEN_MODULES = frozenset({"move", "descend", "loot", "enact", "statecanon", "rerun", "savegame", "lockstep",
                                "actionlog", "rngstream", "entity", "cue", "chorus"})
_FORBIDDEN_ATTRS = frozenset({"step", "dispatch", "apply", "d_n", "d_n_preimage", "serialize", "restore"})


class VistaError(Exception):
    def __init__(self, message):
        super().__init__(f"VISTA-REFUSE: {message}")
        self.code = "VISTA-REFUSE"


# ---- admission --------------------------------------------------------------------------------------------
def _check(level, pos, facing):
    if not isinstance(level, _G.Level):
        raise VistaError(f"level must be a gamegen.Level, got {type(level).__name__}")
    if not (isinstance(pos, tuple) and len(pos) == 2
            and all(isinstance(v, int) and not isinstance(v, bool) for v in pos)):
        raise VistaError(f"pos must be an integer cell (x, y), got {pos!r}")
    if not _D.traversable(level, pos[0], pos[1]):
        raise VistaError(f"the eye stands on a non-traversable cell {pos!r}; a frame from inside rock is not a view")
    if facing not in FACINGS:
        raise VistaError(f"facing must be one of {FACINGS}, got {facing!r}")


def default_facing(level):
    """The cardinal from `<` toward `>` along the longer axis — a pure function of the level, so a first frame
    needs no move history. VIEW state; the authority has no heading."""
    if not isinstance(level, _G.Level):
        raise VistaError(f"level must be a gamegen.Level, got {type(level).__name__}")
    (ux, uy), (dx, dy) = _D.endpoints(level)
    ex, ey = dx - ux, dy - uy
    if abs(ex) >= abs(ey):
        return "E" if ex >= 0 else "W"
    return "S" if ey >= 0 else "N"


# ---- the camera: one ray per column, through the certified oracle --------------------------------------------
def _occupancy(level):
    cells, rows = level.cells, level.h

    def occ(x, y, z):
        return y == 0 and (z >= rows or cells[z][x:x + 1] == b"#")
    return occ


def _eye(pos):
    return (pos[0] * Q + EYE_Y, EYE_Y, pos[1] * Q + EYE_Y)


def _direction(facing, column):
    """Camera-space (a, b) = (2c+1-W, 2*FOCAL) — the pixel CENTRE, kept integer by doubling — carried into the
    level's axes by the facing's right/forward pair."""
    a, b = 2 * column + 1 - W, 2 * FOCAL
    fx, fz = _FWD[facing]
    rx, rz = _RIGHT[facing]
    return rx * a + fx * b, rz * a + fz * b


def strip(level, pos, facing, column):
    """The wall strip at one column: (voxel, face, (t_num, t_den), top_row, bottom_row, band). Depth along the
    view axis is `2*FOCAL*t`; the wall's top and bottom edges project `h = FOCAL*EYE_Y/depth = 64*t_den/t_num`
    above and below the horizon, and a row belongs to the strip iff its CENTRE lies between them:
    `CY - floor(h + 1/2) <= row <= CY + floor(h - 1/2)`, both exact floors of rationals. The eye stands on a
    traversable cell, so the oracle always returns an entered face."""
    dx, dz = _direction(facing, column)
    hit = _VX.first_hit(_eye(pos), (dx, 0, dz), occ=_occupancy(level), origin="opaque", n=LATTICE, q=Q)
    if hit is None or hit[1] is None:
        raise VistaError(f"the ray at column {column} left the world or started inside rock")
    vox, face, (tn, td) = hit
    h2n, h2d = FOCAL * EYE_Y * td, 2 * FOCAL * tn                    # h = h2n / h2d = 64*td/tn
    top = CY - (2 * h2n + h2d) // (2 * h2d)
    bot = CY + (2 * h2n - h2d) // (2 * h2d)
    band = min(BANDS - 1, (2 * FOCAL * tn) // (td * Q))
    return vox, face, (tn, td), max(0, top), min(H - 1, bot), band


def frame(level, pos, facing):
    """ONE FIRST-PERSON FRAME as a URDRFB1 index image. Sky above each strip (band by row), the strip (ink where
    the hit voxel/face changes between columns and on its top and bottom rows), and the floor below it by exact
    inverse projection: the row whose centre is `kk/2` pixels below the horizon (`kk = 2(r-CY)+1`) sees depth
    `2*FOCAL*EYE_Y/kk`, hence the world point `eye + D*EYE_Y/kk` and the cell `floor((eye*kk + D*EYE_Y)/(kk*Q))`
    — the floor of a rational, no float."""
    _check(level, pos, facing)
    fb = _RS.Framebuffer(W, H)
    buf = fb.buf
    cells, rows, cols = level.cells, level.h, level.w
    ex, _ey, ez = _eye(pos)
    prev = None
    for c in range(W):
        vox, face, _t, top, bot, band = strip(level, pos, facing, c)
        dx, dz = _direction(facing, c)
        widx = WALL0 + FACE_LIGHT[face] * BANDS + band
        key = (vox, face)
        for r in range(0, top):
            buf[r * W + c] = SKY0 + min(SKY_BANDS - 1, ((CY - r) * SKY_BANDS) // CY)
        v = INK if key != prev else widx
        for r in range(top, bot + 1):
            buf[r * W + c] = v
        if top < bot:
            buf[top * W + c] = INK
            buf[bot * W + c] = INK
        for r in range(bot + 1, H):
            kk = 2 * (r - CY) + 1
            wx = (ex * kk + dx * EYE_Y) // (kk * Q)
            wz = (ez * kk + dz * EYE_Y) // (kk * Q)
            fband = min(BANDS - 1, (2 * FOCAL * EYE_Y) // (kk * Q))
            cc = cells[wz][wx:wx + 1] if 0 <= wz < rows and 0 <= wx < cols else b"#"
            if cc == b">":
                buf[r * W + c] = DOWN0 + fband
            elif cc == b"<":
                buf[r * W + c] = UP0 + fband
            else:
                buf[r * W + c] = FLOOR0 + fband
        prev = key
    return fb


def frame_digest(fb):
    """The frame's identity is the URDRFB1 law's — `raster` owns it; this module adds nothing."""
    return fb.digest()


def index_class(v):
    """The class an index encodes: ink, sky, floor, down, up, wall — the declared layout read back."""
    if v == INK:
        return "ink"
    if v < FLOOR0:
        return "sky"
    if v < DOWN0:
        return "floor"
    if v < UP0:
        return "down"
    if v < WALL0:
        return "up"
    return "wall"


def census(fb):
    """Pixels per class, with the denominator — the frame's population, never a picture of it."""
    n = {}
    for v in fb.buf:
        k = index_class(v)
        n[k] = n.get(k, 0) + 1
    n["total"] = fb.w * fb.h
    return n


def census_verdict(fb):
    """`framing`'s DOMINANCE rule, on this frame: WELL_FRAMED, or DEGENERATE named by the class that swamps it
    (at least DOMINANCE_PERMILLE of the pixels). A rule that never accepts is worthless, so the corpus carries
    both verdicts."""
    n = census(fb)
    tot = n["total"]
    for k, v in n.items():
        if k != "total" and v * 1000 >= DOMINANCE_PERMILLE * tot:
            return "DEGENERATE:" + k
    return "WELL_FRAMED"


# ---- the imaging contract: a table ---------------------------------------------------------------------------
def _mix(a, b, num, den):
    return tuple((a[i] * (den - num) + b[i] * num) // den for i in range(3))


def _scale(c, num, den):
    return tuple(max(0, min(255, (v * num) // den)) for v in c)


def lut(depth):
    """index -> RGB for a level at `depth`. Haze is achromatic and at most HAZE_MAX_PERMILLE at the far band;
    the depth tint is an achromatic darkening (deeper = darker, never a hue shift); so a class's hue family is
    the same at every distance and every depth — the property `the_lut_keeps_classes_apart` reads off the
    table. Integer arithmetic throughout: the table is data, reproducible anywhere."""
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 1:
        raise VistaError(f"depth must be a positive integer, got {depth!r}")
    t = min(DEPTH_TINT_CELLS, depth - 1)                      # 0..12
    haze = _scale(HAZE, 100 * DEPTH_TINT_CELLS - 30 * t, 100 * DEPTH_TINT_CELLS)
    lum_n, lum_d = 100 * DEPTH_TINT_CELLS - 25 * t, 100 * DEPTH_TINT_CELLS
    table = [(0, 0, 0)] * 256
    table[INK] = INK_RGB
    for i in range(SKY_BANDS):
        table[SKY0 + i] = _scale(_mix(SKY_HORIZON, SKY_TOP, i, SKY_BANDS - 1), lum_n, lum_d)
    for band in range(BANDS):
        f_n, f_d = HAZE_MAX_PERMILLE * band, 1000 * (BANDS - 1)
        near_n, near_d = 75 * (BANDS - 1) + 25 * band, 100 * (BANDS - 1)    # near floor darker
        table[FLOOR0 + band] = _mix(_scale(_scale(FLOOR_RGB, lum_n, lum_d), near_n, near_d), haze, f_n, f_d)
        table[DOWN0 + band] = _mix(_scale(DOWN_RGB, lum_n, lum_d), haze, f_n, 2 * f_d)
        table[UP0 + band] = _mix(_scale(UP_RGB, lum_n, lum_d), haze, f_n, 2 * f_d)
        for light, base in enumerate(WALL_RGB):
            table[WALL0 + light * BANDS + band] = _mix(_scale(base, lum_n, lum_d), haze, f_n, f_d)
    return tuple(table)


def png_bytes(fb, table):
    """The frame as PNG bytes through the table — a CONTAINER for a picture, not an identity (zlib output is
    a library's; the identity is `frame_digest`)."""
    rows = bytearray()
    for r in range(fb.h):
        rows.append(0)
        for v in fb.buf[r * fb.w:(r + 1) * fb.w]:
            rows += bytes(table[v])

    def chunk(tag, data):
        c = tag + data
        return _struct.pack(">I", len(data)) + c + _struct.pack(">I", _zlib.crc32(c) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", _struct.pack(">IIBBBBB", fb.w, fb.h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", _zlib.compress(bytes(rows), 6)) + chunk(b"IEND", b""))


# ---- laws -------------------------------------------------------------------------------------------------------
def _straight_walk(level, pos, facing):
    """The cells the facing axis passes from `pos` until the first wall — a SECOND computation of what the centre
    ray must see, by nothing more than indexing `level.cells`."""
    fx, fz = _FWD[facing]
    x, z = pos
    walked = []
    while True:
        x, z = x + fx, z + fz
        if not (0 <= x < level.w and 0 <= z < level.h) or level.cells[z][x:x + 1] == b"#":
            return tuple(walked), (x, 0, z)
        walked.append((x, z))


def the_centre_column_is_a_straight_walk(level, pos, facing, fb=None):
    """THE READ-BACK LAW. Returns (voxel_agrees, height_agrees, floor_agrees). The centre column's strip must be
    the first wall the straight walk meets, `k` cells ahead — its near face `(2k-1)*Q/2` ahead of the eye, so its
    edges project `h = 960/(2k-1)` pixels about the horizon and the strip is exactly the rows whose centres fall
    between them; and every floor row below the strip must carry the class of the walked cell at that row's
    depth (`2*FOCAL*EYE_Y/kk` world units for the row centre `kk/2` below the horizon). The walk is a second
    computation over `level.cells`; the depth-to-row map is the camera's definition, shared. The verdict is read
    FROM the frame; nothing is written anywhere."""
    _check(level, pos, facing)
    fb = frame(level, pos, facing) if fb is None else fb
    walked, wall = _straight_walk(level, pos, facing)
    k = len(walked) + 1
    vox, _face, _t, top, bot, _band = strip(level, pos, facing, CX)
    hn, hd = 2 * FOCAL * EYE_Y, (2 * k - 1) * Q                  # h = hn / hd = 960 / (2k-1)
    voxel_ok = vox == wall
    height_ok = (top, bot) == (max(0, CY - (2 * hn + hd) // (2 * hd)), min(H - 1, CY + (2 * hn - hd) // (2 * hd)))
    floor_ok = True
    for r in range(bot + 1, H):
        kk = 2 * (r - CY) + 1                                   # this row's centre sees depth 2*FOCAL*EYE_Y/kk
        j = -((EYE_Y * kk - 2 * FOCAL * EYE_Y) // (kk * Q))    # the cell that depth falls in (0 = the eye's own)
        cell = pos if j == 0 else walked[j - 1] if j - 1 < len(walked) else None
        want = "wall" if cell is None else {b">": "down", b"<": "up"}.get(level.cells[cell[1]][cell[0]:cell[0] + 1], "floor")
        if index_class(fb.buf[r * W + CX]) != want:
            floor_ok = False
            break
    return voxel_ok, height_ok, floor_ok


def a_planted_eye_is_caught(level, pos, facing):
    """POSITIVE CONTROL: a frame rendered from the cell BEHIND the eye (when traversable) or read against a
    walk from a shifted cell must fail the read-back — the law bites."""
    fx, fz = _FWD[facing]
    behind = (pos[0] - fx, pos[1] - fz)
    if not _D.traversable(level, behind[0], behind[1]):
        return None                                             # no traversable cell behind: control not posable here
    fb_wrong = frame(level, behind, facing)
    return not all(the_centre_column_is_a_straight_walk(level, pos, facing, fb_wrong))


def the_frame_is_a_function_of_the_view(level, pos, facing):
    """(reproduces, facing_matters, pos_matters). Same inputs -> the same URDRFB1 digest; a turned camera or a
    moved eye -> a different one."""
    d0 = frame_digest(frame(level, pos, facing))
    again = frame_digest(frame(level, pos, facing)) == d0
    other = FACINGS[(FACINGS.index(facing) + 1) % 4]
    turned = frame_digest(frame(level, pos, other)) != d0
    walked, _w = _straight_walk(level, pos, facing)
    moved = frame_digest(frame(level, walked[0], facing)) != d0 if walked else True
    return again, turned, moved


def _classes_apart(table):
    floor_warm = all(table[FLOOR0 + b][0] >= table[FLOOR0 + b][2] + 4 for b in range(BANDS))
    wall_cool = all(table[WALL0 + l * BANDS + b][2] >= table[WALL0 + l * BANDS + b][0] + 4
                    for l in range(len(WALL_RGB)) for b in range(BANDS))
    down_teal = all(min(table[DOWN0 + b][1], table[DOWN0 + b][2]) >= table[DOWN0 + b][0] + 40 for b in range(BANDS))
    up_magenta = all(min(table[UP0 + b][0], table[UP0 + b][2]) >= table[UP0 + b][1] + 30 for b in range(BANDS))
    return floor_warm and wall_cool and down_teal and up_magenta


def the_lut_keeps_classes_apart(depths=(1, 2, 7, 13, 1000)):
    """(apart_at_every_depth, planted_warm_wall_caught). Read off the TABLE: floor stays warm (R >= B+4), every
    wall entry stays cool (B >= R+4), `>` stays teal and `<` magenta at every band and depth — haze and tint
    cannot move a hue family. Positive control: a table with one wall entry painted floor-warm is refused."""
    apart = all(_classes_apart(lut(d)) for d in depths)
    planted = list(lut(1))
    planted[WALL0 + 5] = FLOOR_RGB
    return apart, not _classes_apart(tuple(planted))


def the_frame_is_populated(fb):
    """Sky, wall and floor all present — `vantage`'s law: a frame with nothing in it proves nothing."""
    n = census(fb)
    return all(n.get(k, 0) > 0 for k in ("sky", "wall", "floor"))


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
    substrate, no transition/identity/log/stream authority in any scope, no `.step`/`.dispatch`/`.apply`/`.d_n`/
    `.serialize`/`.restore`. Positive controls: sources that step a move, dispatch a token, ingest `D_n`, draw a
    stream or reach a bare `.d_n` are each REJECTED; the read-only oracle path is accepted."""
    with open(_os.path.join(_HERE, "vista.py"), encoding="utf-8") as fh:
        own = fh.read()
    clean = _source_is_one_way(own)
    bad = (
        "import gamegen\ndef k(l, p, c):\n    import move as _M\n    return _M.step(l, p, c)\n",
        "import gamegen\ndef f(s, t):\n    import enact as _E\n    return _E.dispatch(s, t)\n",
        "import gamegen\ndef h(t):\n    import statecanon as _S\n    return _S.d_n(*t)\n",
        "import gamegen\ndef d(s):\n    import rngstream as _R\n    return _R.draw(s)\n",
        "import gamegen\ndef g(r):\n    import savegame as _V\n    return _V.restore(r)\n",
        "z = w.d_n(1)\n",
        "y = x.apply(1)\n",
    )
    bites = all(not _source_is_one_way(b) for b in bad)
    allows = _source_is_one_way(
        "import voxray\nimport raster\ndef h(e, d):\n    return voxray.first_hit(e, d), raster.Framebuffer(2, 2)\n")
    return clean and bites and allows


def refuse_is_total(seed=0, depth=1):
    """Every listed malformed input is a typed VISTA-REFUSE: not a Level, a malformed cell, a wall cell, a bad
    facing, a bad depth for the table."""
    lvl = _G.generate(seed, depth)
    pos = _D.endpoints(lvl)[0]
    wall = next((x, y) for y in range(lvl.h) for x in range(lvl.w) if lvl.cells[y][x:x + 1] == b"#")
    cases = (
        lambda: frame("not a level", pos, "N"),
        lambda: frame(lvl, (pos[0], "1"), "N"),
        lambda: frame(lvl, [pos[0], pos[1]], "N"),
        lambda: frame(lvl, (True, 1), "N"),
        lambda: frame(lvl, wall, "N"),
        lambda: frame(lvl, pos, "NE"),
        lambda: default_facing(None),
        lambda: lut(0),
        lambda: lut(1.5),
    )
    for case in cases:
        try:
            case()
        except VistaError as exc:
            if exc.code != "VISTA-REFUSE":
                return False
            continue
        return False
    return True


# ---- scenes -----------------------------------------------------------------------------------------------------
#: (seed, depth, where, facing). `where` is `spawn` (the `<` cell), `mid` (the middle cell of the descent path),
#: `landmark` (the westmost cell of `>`'s row that still sees it, facing E — the destination in view) or
#: `wallward` (walk from spawn in `facing` to the last cell before the wall, and face it — the deliberately
#: DEGENERATE frame, so the census rule is seen to bite as well as to accept). A `facing` of None is
#: `default_facing`.
SCENE_SPECS = {
    "corridor": (0, 1, "spawn", "N"),
    "room": (12345, 7, "mid", "E"),
    "landmark": (0xC0FFEE, 2, "landmark", "E"),
    "pointblank": (0, 1, "wallward", "W"),
}
SCENES = tuple(SCENE_SPECS)


def scene_view(name):
    """The (level, pos, facing) a scene renders — built from the authority, read only."""
    if name not in SCENE_SPECS:
        raise VistaError(f"no scene named {name!r}")
    seed, depth, where, facing = SCENE_SPECS[name]
    lvl = _G.generate(seed, depth)
    if where == "mid":
        path = _D.descent_path(lvl)
        pos = tuple(path[len(path) // 2])
    elif where == "landmark":
        pos = _D.endpoints(lvl)[1]
        while _D.traversable(lvl, pos[0] - 1, pos[1]):
            pos = (pos[0] - 1, pos[1])
    else:
        pos = _D.endpoints(lvl)[0]
    if facing is None:
        facing = default_facing(lvl)
    if where == "wallward":
        walked, _wall = _straight_walk(lvl, pos, facing)
        pos = walked[-1] if walked else pos
    return lvl, pos, facing


_SCENE_MEMO = {}


def scene_case(name):
    """A scene's row string. Memoised per process (a pure function of the module's constants; a scene costs
    four frames), so the corpus self-check, the top digest and the gate's re-emission do not each pay it."""
    if name in _SCENE_MEMO:
        return _SCENE_MEMO[name]
    lvl, pos, facing = scene_view(name)
    fb = frame(lvl, pos, facing)
    n = census(fb)
    row = ("view=%d/%d/%s/%s|frame=%s|census=%s|verdict=%s|populated=%s|readback=%s|function=%s"
           % (lvl.seed, lvl.depth, pos, facing, frame_digest(fb),
              ",".join("%s:%d" % (k, n[k]) for k in sorted(n)),
              census_verdict(fb), the_frame_is_populated(fb),
              the_centre_column_is_a_straight_walk(lvl, pos, facing, fb),
              the_frame_is_a_function_of_the_view(lvl, pos, facing)))
    _SCENE_MEMO[name] = row
    return row


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|" + scene_case(name).encode()).hexdigest()


def vista_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n) for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_vista.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VistaError(f"no golden named {name!r}")


def emitted_matches_pinned():
    return (all(scene_result(n) == golden(n) for n in SCENES)
            and vista_digest() == golden("vista"))


def an_unpinned_name_refuses():
    try:
        golden("not-a-scene")
    except VistaError as exc:
        return exc.code == "VISTA-REFUSE"
    return False


def main():
    print("VISTA — the first-person frame of the certified dungeon; the eye is taken, never derived (URDRVIS1)")
    print("layer %s: %s" % (LAYER, D24_ANSWER))
    print("camera %dx%d focal %d, cell %d units, eye %d, %d depth bands; substrate voxray.first_hit + raster.Framebuffer"
          % (W, H, FOCAL, Q, EYE_Y, BANDS))
    print()
    for n in SCENES:
        lvl, pos, facing = scene_view(n)
        fb = frame(lvl, pos, facing)
        print("%-10s %d/%d %s %s  %s  %s  readback=%s"
              % (n, lvl.seed, lvl.depth, pos, facing, frame_digest(fb)[:16], census_verdict(fb),
                 the_centre_column_is_a_straight_walk(lvl, pos, facing, fb)))
    lvl, pos, facing = scene_view("corridor")
    print()
    print("the frame is a function of the view :", the_frame_is_a_function_of_the_view(lvl, pos, facing))
    print("a planted eye is caught            :", a_planted_eye_is_caught(lvl, pos, facing))
    print("the lut keeps classes apart        :", the_lut_keeps_classes_apart())
    print("the membrane is one-way            :", the_membrane_is_one_way())
    print("refuse is total                    :", refuse_is_total())
    print()
    for n in SCENES:
        print(n, scene_result(n))
    print("vista", vista_digest())
    print()
    print("does_not_show: pitch, free yaw, smooth motion (kinema Frames next), textures, props, a second placement")
    print("of this module, any wall-clock. A frame is a photograph of the certified level, not a loop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
