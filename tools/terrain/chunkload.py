# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""chunkload — the chunk loader (T3.37, MMO Stage I opener, URDRCHK1): the certified terrain authority cut
into content-addressed CHUNKS and streamed back under an EQUAL-OR-REFUSE law. `persist` (URDRLAT5) made the
DYNAMIC state durable — the rollback window as digest-named records; both `storecost` and `persist` deferred
the STATIC half in their does_not_show: "the FIELD's own storage (static and shared)." An MMO-scale world
cannot hold the whole field resident; it must load the part an actor needs. chunkload certifies exactly that:
the field's storage priced, its identity decomposed, and movement over a PARTIAL world provably identical to
movement over the whole one — or refused.

THE CUT (identity decomposed). `cut(field, C)` splits a W x H field into (W/C)*(H/C) chunks (C in the frozen
CHUNK_SIZES; non-divisible dims are a typed `CHUNK-REFUSE`, never a pad). Each chunk is a canonical record —
    MAGIC(8) | kx(4) | ky(4) | cw(4) | ch(4) | cells (8 bytes each, row-major, signed big-endian) | SHA-256
so chunk_bytes(C) = 56 + 8*C*C is a CLOSED FORM checked EQUAL to real records; the ONE digest is integrity
check, content address, and filename (the `persist` law). `field_manifest` binds the chunk-digest grid —
    MAP_MAGIC(11) | W(4) | H(4) | C(4) | digest grid (32 each, row-major) | SHA-256
— and `reassemble` reproduces the original field BYTE-FOR-BYTE from verified chunks, with the gate tying the
reassembled field to its pinned URDRHF1 canon digest: cutting and streaming provably do not touch terrain
identity (the D16 pattern — partition, reunify, same witness — applied to the terrain authority).

THE LOADER (equal-or-refuse). A `view` is a partial residency: dims + chunk size + the loaded chunks.
`glide_partial` re-runs the frozen mover's fold against the view, reading heights ONLY through
`height_at` — and a probe into an unloaded chunk refuses the WHOLE glide (`CHUNK-REFUSE`). It never treats
unloaded terrain as a wall: the full mover PROBES a destination cell before deciding it is blocked, so a
view that cannot see that cell cannot honestly reproduce the stop — it refuses instead. The fold here is a
REIMPLEMENTATION (the frozen `glide` is consumed, never edited — the `rollback` pattern), and the gate pins
its output EQUAL to `glide.glide` / `glide.glide_cells` bit-for-bit over a corpus: the equality IS the
anti-drift detector, covering the mirrored facing map and gait law too.

THE DEMAND SET (locality made exact). `demand_chunks` runs the same fold over the FULL field with a recording
getter: every cell the mover READS (occupied cells + probed destinations, including blocked ones) maps to a
chunk. The gate proves the set is SUFFICIENT (a view of exactly the demand set reproduces the full glide
bit-for-bit) and NECESSARY (dropping ANY chunk of it turns that glide into `CHUNK-REFUSE`) — so "which
chunks does this transcript need" has an exact, certified answer, not a heuristic radius.

THE ENVELOPE. field_storage(W, H, C) = nchunks*chunk_bytes(C) + manifest_bytes(W, H, C) and
resident_bytes(k, C) = k*chunk_bytes(C) are closed forms checked EQUAL to real bytes, and
`storecost.within_storage_budget` gates residency under the same `STORAGE-REFUSE` law — the static field now
priced exactly as the dynamic window was.

GRADE. The record closed form and round-trip, the exhaustive corruption/truncation `CHUNK-REFUSE`, the
byte-exact reassembly and its URDRHF1 canon tie, the partial-glide equality over the corpus, the demand set's
sufficiency AND necessity, the store-fetch refusals (tampered / substituted / missing / coord-forged), the
storage closed forms, the budget refuse, and determinism are MEASURED (exact, reproducible, a defect
diverges). The CHUNK SIZE choice is a DECLARED operational parameter (identity and equality hold for every
frozen C; which C a host picks is sizing policy, like rollback's K/H); the residency POLICY (which chunks to
keep) is DECLARED — the demand set certifies what a given transcript NEEDS, not what a server should cache.
`does_not_show`: EVICTION (when to drop a chunk — operational); PREFETCH or async load latency (`bench.py`
territory, MEASURED-on-named-host); LIVE EDITS (the field is still static — a mutable chunked world is the
next stage's problem); INTEREST-relevance composition (`interest` says who must be TOLD, this says what must
be LOADED — composing them is future work); and cross-placement (Python reference only until a second
placement reproduces these digests)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRCHK1"
MAP_MAGIC = b"URDRCHK1MAP"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                             # the frozen mover (the equality pin)
import stance as _ST                                            # DIRS — the step-direction law (public)
import storecost as _SC                                         # the shared STORAGE-REFUSE budget law

CHUNK_SIZES = (4, 8, 16, 32)                                    # frozen: C must divide both dims
CELL_BYTES = 8                                                  # signed big-endian int64 per height
COORD_BYTES = 4
DIGEST_BYTES = 32
REC_OVERHEAD = len(MAGIC) + 4 * COORD_BYTES + DIGEST_BYTES      # 56
MAP_OVERHEAD = len(MAP_MAGIC) + 3 * COORD_BYTES + DIGEST_BYTES  # 55
_FACE = {"N": 0, "E": 1, "S": 2, "W": 3}                        # mirror of glide's map — equality-pinned


class ChunkError(Exception):
    def __init__(self, message):
        super().__init__(f"CHUNK-REFUSE: {message}")
        self.code = "CHUNK-REFUSE"


def _check_grid(field, csize):
    if csize not in CHUNK_SIZES:
        raise ChunkError(f"chunk size {csize!r} is not one of the frozen {CHUNK_SIZES}")
    if not (isinstance(field, tuple) and field and isinstance(field[0], tuple) and field[0]):
        raise ChunkError("field must be a non-empty tuple of non-empty rows")
    w, h = len(field[0]), len(field)
    if w % csize or h % csize:
        raise ChunkError(f"{w}x{h} is not divisible by C={csize} — refuse, never pad")
    return w, h


# ---- canonical chunk record --------------------------------------------------------------
def chunk_bytes(csize):
    """The EXACT record size of a CxC chunk: 56 + 8*C*C. The closed form the gate checks EQUAL to real
    records."""
    if csize not in CHUNK_SIZES:
        raise ChunkError(f"chunk size {csize!r} is not one of the frozen {CHUNK_SIZES}")
    return REC_OVERHEAD + CELL_BYTES * csize * csize


def chunk_record(kx, ky, cells):
    """The canonical durable record of one chunk: MAGIC | kx | ky | cw | ch | cells | SHA-256. Cells are
    signed int64 (an out-of-range height refuses); the trailing digest is integrity check AND content
    address."""
    cw, ch = len(cells[0]), len(cells)
    pre = bytearray(MAGIC)
    for v in (kx, ky, cw, ch):
        if not (type(v) is int and 0 <= v < (1 << (8 * COORD_BYTES))):
            raise ChunkError(f"coords/dims must be uint32, got {v!r}")
        pre += v.to_bytes(COORD_BYTES, "big")
    for row in cells:
        if len(row) != cw:
            raise ChunkError("chunk rows must be rectangular")
        for v in row:
            if not (type(v) is int and -(1 << 63) <= v < (1 << 63)):
                raise ChunkError(f"height {v!r} does not fit signed int64 — refuse, never truncate")
            pre += (v & ((1 << 64) - 1)).to_bytes(CELL_BYTES, "big")
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def _verified(buf, magic, floor):
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise ChunkError("a record must be bytes")
    buf = bytes(buf)
    if len(buf) < floor:
        raise ChunkError(f"buffer of {len(buf)} bytes is shorter than the {floor}-byte minimum")
    if buf[:len(magic)] != magic:
        raise ChunkError(f"bad magic — not a {magic.decode()} object")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise ChunkError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    return buf


def address(buf):
    """The content address of a verified chunk record or field manifest: the hex of its embedded digest.
    Identity is content; no address for corrupt bytes."""
    if (type(buf) is bytes or type(buf) is bytearray) and bytes(buf[:len(MAP_MAGIC)]) == MAP_MAGIC:
        return _verified(buf, MAP_MAGIC, MAP_OVERHEAD)[-DIGEST_BYTES:].hex()
    return _verified(buf, MAGIC, REC_OVERHEAD + CELL_BYTES)[-DIGEST_BYTES:].hex()


def restore_chunk(buf):
    """The inverse of `chunk_record`: (kx, ky, cells) BIT-FOR-BIT, or a typed CHUNK-REFUSE. The digest is
    checked first (every flipped byte and every truncation refuses); the structural length must match the
    embedded dims exactly."""
    buf = _verified(buf, MAGIC, REC_OVERHEAD + CELL_BYTES)
    off = len(MAGIC)
    kx, ky, cw, ch = (int.from_bytes(buf[off + i * COORD_BYTES:off + (i + 1) * COORD_BYTES], "big")
                      for i in range(4))
    off += 4 * COORD_BYTES
    if len(buf) != REC_OVERHEAD + CELL_BYTES * cw * ch or cw == 0 or ch == 0:
        raise ChunkError(f"record length {len(buf)} does not match its {cw}x{ch} dims")
    cells = []
    for _y in range(ch):
        row = []
        for _x in range(cw):
            row.append(int.from_bytes(buf[off:off + CELL_BYTES], "big", signed=True))
            off += CELL_BYTES
        cells.append(tuple(row))
    return kx, ky, tuple(cells)


# ---- the cut and the manifest ------------------------------------------------------------
def cut(field, csize):
    """The field decomposed: {(kx, ky): record} over the full chunk grid. Deterministic — same field, same
    C, same records, same digests."""
    w, h = _check_grid(field, csize)
    out = {}
    for ky in range(h // csize):
        for kx in range(w // csize):
            cells = tuple(tuple(field[ky * csize + y][kx * csize + x] for x in range(csize))
                          for y in range(csize))
            out[(kx, ky)] = chunk_record(kx, ky, cells)
    return out


def field_manifest(field, csize):
    """The chunked field's identity as ONE object: MAP_MAGIC | W | H | C | the chunk-digest grid (row-major)
    | SHA-256. A changed cell moves its chunk digest and therefore the manifest."""
    w, h = _check_grid(field, csize)
    chunks = cut(field, csize)
    pre = bytearray(MAP_MAGIC)
    for v in (w, h, csize):
        pre += v.to_bytes(COORD_BYTES, "big")
    for ky in range(h // csize):
        for kx in range(w // csize):
            pre += chunks[(kx, ky)][-DIGEST_BYTES:]
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def parse_manifest(man):
    """A verified manifest -> (W, H, C, ((kx, ky) -> address-hex)). Structural length re-checked."""
    man = _verified(man, MAP_MAGIC, MAP_OVERHEAD)
    off = len(MAP_MAGIC)
    w, h, csize = (int.from_bytes(man[off + i * COORD_BYTES:off + (i + 1) * COORD_BYTES], "big")
                   for i in range(3))
    off += 3 * COORD_BYTES
    if csize not in CHUNK_SIZES or csize == 0 or w % csize or h % csize:
        raise ChunkError(f"manifest dims {w}x{h} / C={csize} are not an admissible grid")
    nk = (w // csize) * (h // csize)
    if len(man) != MAP_OVERHEAD + DIGEST_BYTES * nk:
        raise ChunkError(f"manifest length {len(man)} does not match its {nk}-chunk grid")
    grid = {}
    for ky in range(h // csize):
        for kx in range(w // csize):
            grid[(kx, ky)] = man[off:off + DIGEST_BYTES].hex()
            off += DIGEST_BYTES
    return w, h, csize, grid


def _fetch(man, lookup, wanted):
    """Fetch + verify `wanted` chunks against the manifest: served bytes must verify, hash to the manifest's
    address for that slot, and carry the slot's own coords. Missing / tampered / substituted / coord-forged
    all refuse."""
    w, h, csize, grid = parse_manifest(man)
    loaded = {}
    for key in sorted(wanted):
        if key not in grid:
            raise ChunkError(f"chunk {key} is outside the manifest grid")
        dig = grid[key]
        try:
            rec = lookup[dig]
        except KeyError:
            raise ChunkError(f"chunk {key} ({dig[:12]}…) missing from the store")
        kx, ky, cells = restore_chunk(rec)
        if bytes(rec)[-DIGEST_BYTES:].hex() != dig:
            raise ChunkError(f"chunk bytes for {key} do not hash to the manifest address — refused")
        if (kx, ky) != key or len(cells) != csize or len(cells[0]) != csize:
            raise ChunkError(f"chunk record claims {(kx, ky)}/{len(cells[0])}x{len(cells)}, manifest slot is "
                             f"{key}/C={csize} — a coord forgery is refused")
        loaded[key] = cells
    return w, h, csize, loaded


def reassemble(man, lookup):
    """The whole field back BYTE-FOR-BYTE from verified chunks — or one typed refuse. The inverse of `cut`;
    the gate ties the result to the pinned URDRHF1 canon digest."""
    w, h, csize, grid = parse_manifest(man)
    _w, _h, _c, loaded = _fetch(man, lookup, frozenset(grid))
    rows = []
    for y in range(h):
        row = []
        for kx in range(w // csize):
            row.extend(loaded[(kx, y // csize)][y % csize])
        rows.append(tuple(row))
    return tuple(rows)


# ---- the partial view and the equal-or-refuse mover -------------------------------------
def view_of(field, csize, keys):
    """A partial residency built from a full in-memory field (the test/gate path): dims + C + only the chunks
    in `keys`."""
    w, h = _check_grid(field, csize)
    chunks = {}
    for key in keys:
        kx, ky = key
        if not (0 <= kx < w // csize and 0 <= ky < h // csize):
            raise ChunkError(f"chunk {key} is outside the {w}x{h} grid at C={csize}")
        chunks[key] = tuple(tuple(field[ky * csize + y][kx * csize + x] for x in range(csize))
                            for y in range(csize))
    return {"w": w, "h": h, "c": csize, "chunks": chunks}


def view_from(man, lookup, keys):
    """A partial residency STREAMED from a content-addressed store: fetch + verify exactly `keys` (the
    demand set), refuse anything tampered, substituted, missing, or coord-forged."""
    w, h, csize, loaded = _fetch(man, lookup, frozenset(keys))
    return {"w": w, "h": h, "c": csize, "chunks": loaded}


def height_at(view, cx, cy):
    """The height under a cell, THROUGH the residency: the resident value, or a typed CHUNK-REFUSE naming the
    unloaded chunk. Never a default, never a guess."""
    csize = view["c"]
    key = (cx // csize, cy // csize)
    cells = view["chunks"].get(key)
    if cells is None:
        raise ChunkError(f"cell ({cx},{cy}) needs unloaded chunk {key} — refuse, never guess a height")
    return cells[cy % csize][cx % csize]


def _parse(cmd):
    if not (isinstance(cmd, str) and len(cmd) == 1 and cmd.upper() in _FACE):
        raise ChunkError(f"command {cmd!r} is not one of N/S/E/W (upper=sprint, lower=walk)")
    return cmd.upper(), ("sprint" if cmd.isupper() else "walk")


def _fold_via(getter, w, h, start, cmds, max_step, sub):
    """The frozen mover's fold, re-run against an ABSTRACT height getter — the ONE algorithm behind
    glide_partial (getter refuses on unloaded) and demand_chunks (getter records reads on the full field).
    Semantics mirror `glide._fold` exactly; the gate pins the output EQUAL to the frozen mover bit-for-bit
    over a corpus (the equality is the anti-drift detector)."""
    if sub not in _GL.SUBDIV:
        raise ChunkError(f"subdivision {sub!r} is not one of {_GL.SUBDIV}")
    if not (isinstance(cmds, str) and 1 <= len(cmds) <= _GL.LOG_MAX):
        raise ChunkError(f"input log must be a str of 1..{_GL.LOG_MAX} commands, got {cmds!r}")
    if not (isinstance(start, tuple) and len(start) == 2
            and type(start[0]) is int and type(start[1]) is int and 0 <= start[0] < w and 0 <= start[1] < h):
        raise ChunkError(f"start {start!r} is not an on-grid integer cell of the {w}x{h} field")
    if not (type(max_step) is int and max_step >= 0):
        raise ChunkError(f"max_step must be a non-negative int, got {max_step!r}")
    for c in cmds:
        _parse(c)
    k = sub.bit_length() - 1
    mstep = _GL.ONE >> k
    fx, fy = start[0] * _GL.ONE, start[1] * _GL.ONE
    facing = _FACE[_parse(cmds[0])[0]]
    cx, cy = fx >> 32, fy >> 32
    seed = (fx, fy, getter(cx, cy), facing)
    micro = [seed]
    cells = [seed]
    for c in cmds:
        dl, gait = _parse(c)
        dx, dy = _ST.DIRS[dl]
        facing = _FACE[dl]
        sfx, sfy = mstep * dx, mstep * dy
        for _ in range(_GL.GAIT[gait] * sub):
            nfx, nfy = fx + sfx, fy + sfy
            ncx, ncy = nfx >> 32, nfy >> 32
            if (ncx, ncy) != (cx, cy):
                if not (0 <= ncx < w and 0 <= ncy < h):
                    break
                if getter(ncx, ncy) - getter(cx, cy) > max_step:
                    break
                cx, cy = ncx, ncy
            fx, fy = nfx, nfy
            micro.append((fx, fy, getter(cx, cy), facing))
        cells.append((fx, fy, getter(cx, cy), facing))
    return tuple(micro), tuple(cells)


def glide_partial(view, start, cmds, max_step, sub):
    """The frozen mover over a PARTIAL world: every micro-step pose, EQUAL to `glide.glide` on the full field
    BIT-FOR-BIT — or a typed CHUNK-REFUSE the moment any read (occupied or probed) needs an unloaded chunk.
    Equal or refuse; never unloaded-terrain-as-wall."""
    return _fold_via(lambda cx, cy: height_at(view, cx, cy),
                     view["w"], view["h"], start, cmds, max_step, sub)[0]


def glide_partial_cells(view, start, cmds, max_step, sub):
    """One pose per command boundary over the partial world — EQUAL to `glide.glide_cells` or CHUNK-REFUSE."""
    return _fold_via(lambda cx, cy: height_at(view, cx, cy),
                     view["w"], view["h"], start, cmds, max_step, sub)[1]


def demand_chunks(field, start, cmds, max_step, sub, csize):
    """The EXACT chunk set this transcript needs: run the same fold over the FULL field, record every cell
    READ (occupied cells and probed destinations, including blocked ones), map to chunks. Gate-proved
    sufficient (a view of exactly this set reproduces the full glide) and necessary (dropping any member
    refuses)."""
    w, h = _check_grid(field, csize)
    reads = set()

    def getter(cx, cy):
        reads.add((cx // csize, cy // csize))
        return field[cy][cx]

    _fold_via(getter, w, h, start, cmds, max_step, sub)
    return frozenset(reads)


# ---- the envelope ------------------------------------------------------------------------
def manifest_bytes(w, h, csize):
    """The EXACT manifest size: 55 + 32 * nchunks."""
    if csize not in CHUNK_SIZES or w % csize or h % csize:
        raise ChunkError(f"{w}x{h} / C={csize} is not an admissible grid")
    return MAP_OVERHEAD + DIGEST_BYTES * (w // csize) * (h // csize)


def field_storage(w, h, csize):
    """The EXACT durable cost of the whole chunked field: nchunks * chunk_bytes(C) + manifest_bytes — the
    'field's own storage' that storecost and persist deferred, now a closed form checked against real
    bytes."""
    if csize not in CHUNK_SIZES or w % csize or h % csize:
        raise ChunkError(f"{w}x{h} / C={csize} is not an admissible grid")
    return (w // csize) * (h // csize) * chunk_bytes(csize) + manifest_bytes(w, h, csize)


def resident_bytes(k, csize):
    """The EXACT memory k resident chunks cost: k * chunk_bytes(C). `storecost.within_storage_budget` gates
    it — the same STORAGE-REFUSE law, now covering the static field."""
    if not (type(k) is int and k >= 0):
        raise ChunkError(f"k must be a non-negative int, got {k!r}")
    return k * chunk_bytes(csize)


def chunkload_digest(name, w, h, csize, witness_hex, nbytes, verdict):
    """URDRCHK1 canon — SHA-256(MAGIC | name | WxH | C | witness | bytes | verdict). Binds the grid, the
    bound witness (a manifest or glide digest), the priced bytes, and the verdict."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|{w}x{h}|c:{csize}|w:{witness_hex}|b:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _heights(scene):
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES[scene]())[1]


def _scene_island16():
    """The island cut at C=16: the manifest digest witnesses the decomposition; verdict ADMIT iff the
    reassembly is byte-for-byte the original."""
    fld = _heights("island")
    man = field_manifest(fld, 16)
    store = {address(r): r for r in cut(fld, 16).values()}
    verdict = "ADMIT" if reassemble(man, store) == fld else "CHUNK-REFUSE"
    return 64, 64, 16, address(man), field_storage(64, 64, 16), verdict


def _scene_walk_demand():
    """The mountains wall-walk over exactly its demand set: the glide digest witnesses trajectory equality
    with the frozen mover; the bytes are the residency the demand set costs."""
    fld = _heights("mountains")
    start, cmds, ms, sub = (6, 24), "NNNNNN", 20, 4
    demand = demand_chunks(fld, start, cmds, ms, sub, 16)
    micro = glide_partial(view_of(fld, 16, demand), start, cmds, ms, sub)
    full = _GL.glide(fld, start, cmds, ms, sub)
    verdict = "ADMIT" if micro == full else "CHUNK-REFUSE"
    wit = _GL.glide_digest("walk_demand", start, cmds, sub, micro)
    return 64, 64, 16, wit, resident_bytes(len(demand), 16), verdict


def _scene_cold_start():
    """A glide over an EMPTY residency: the very first read (the start cell) must CHUNK-REFUSE."""
    fld = _heights("island")
    try:
        glide_partial(view_of(fld, 16, frozenset()), (10, 10), "eeee", 30, 4)
        verdict = "ADMIT"                                        # unreachable if the refuse law holds
    except ChunkError:
        verdict = "CHUNK-REFUSE"
    return 64, 64, 16, "0" * 64, resident_bytes(0, 16), verdict


_SCENES = {"island16": _scene_island16, "walk_demand": _scene_walk_demand, "cold_start": _scene_cold_start}
SCENES = ("island16", "walk_demand", "cold_start")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    w, h, csize, wit, nbytes, verdict = scene_case(name)
    return chunkload_digest(name, w, h, csize, wit, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_chunkload.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ChunkError(f"no golden named {name!r}")
