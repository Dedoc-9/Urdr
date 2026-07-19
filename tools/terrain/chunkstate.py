# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""chunkstate — the regional state cut (T3.39, MMO Stage I, URDRCHS1): the D16 same-witness law applied to
DYNAMIC state. `chunkload` decomposed the STATIC field into content-addressed chunks whose reassembly
reproduces the canon digest; the actor state stayed monolithic — one `persist` window holding every actor.
At MMO scale each region must checkpoint ITS residents independently. chunkstate certifies the
decomposition: the world snapshot at a boundary, PARTITIONED per region (each actor claimed by the region
its pose floors into, on `chunkload`'s own grid), each region one content-addressed record — and the
REUNIFICATION reproduces the monolithic `persist` window BYTE-FOR-BYTE: same records, same manifest, same
content addresses. Partition, checkpoint regionally, reunify: same witness.

THE CONSISTENT CUT IS FREE. Chandy-Lamport assembles a consistent global snapshot from per-node local
snapshots and spends its machinery on barrier alignment; URDR's tick is already a globally synchronous
barrier (lockstep), so every region snapshots the SAME command boundary by construction — a cut whose
regions carry DIFFERENT boundaries is refused, not aligned. Migration is per-boundary re-partition, not
state mutation: a seam-crossing actor is claimed by region A at boundary b and region B at b+1, and both
cuts reunify exactly.

THE RECORD. region_record(kx, ky, boundary, entries) = MAGIC(8) | kx(4) | ky(4) | boundary(8) | count(4) |
(idx(4) | fx(8) | fy(8) | ground(8) | facing(1))* | SHA-256(32) — so region_record_bytes(m) = 60 + 29*m is
a CLOSED FORM checked EQUAL to real records; the ONE digest is integrity check, content address, and
filename (the `persist` law). Entries carry the GLOBAL actor index — identity survives the partition — and
are strictly ascending; a crafted record with disordered or duplicate indices refuses.

THE AUTHORITY REFUSES (the anti-cheat shape of a distributed snapshot). Reunification refuses, typed
`CHUNKSTATE-REFUSE`: a DOUBLY-CLAIMED actor (one index in two regions — the double-authority exploit), a
LOST actor (an index missing from the cut — no silent despawn), a FOREIGN claim (a pose flooring outside
the claiming region — no annexation), and a MIXED-BOUNDARY cut (not a consistent cut). No actor is doubly
owned, dropped, or annexed; the refuse names which.

THE REGIONAL RESUME. `resume_region` revives ONE region's residents (identity-preserving) and equals the
global resume law filtered to those actors — a region recovers independently, the `resurrect` law
distributed; the never-died equality follows by composition.

GRADE. The record closed form and round-trip, the exhaustive corruption/truncation refuse, the same-witness
reunification (state AND persist records AND persist manifest byte-identical over a corpus including a
seam-crossing migrant and a fractional wall-stopped pose), the migration-by-re-partition law, the four
authority refuses, the regional-resume equality, the envelope closed form, the budget refuse under
`storecost`'s law, and determinism/purity are MEASURED (exact, reproducible, a defect diverges). The REGION
GRID (which C a deployment picks) stays the DECLARED operational parameter it was in `chunkload`; WHICH
region SIMULATES which actor between cuts is DECLARED out of scope — this rung certifies the SNAPSHOT
decomposition, not distributed execution. `does_not_show`: cross-machine transport and clocks (the cut is a
data law, not a network protocol); DYNAMIC REPARTITIONING mid-window (C is fixed per cut — the D5 open
falsification attempt, not begun); a per-region DEATH boundary (inherited by composition — regional records
ride `persist`'s verified restore path; the subprocess falsifier stays `resurrect`'s); live world edits;
and cross-placement (Python reference only until a second placement reproduces these digests)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRCHS1"
CUT_MAGIC = b"URDRCHS1CUT"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # the region grid (frozen CHUNK_SIZES)
import splice as _SP                                            # the memoryless resume (regional recovery)
import storecost as _SC                                         # pose widths + the budget law

IDX_BYTES = 4
ENTRY_BYTES = IDX_BYTES + 3 * 8 + 1                             # 29: idx + fx + fy + ground + facing
REC_OVERHEAD = len(MAGIC) + 4 + 4 + 8 + 4 + 32                  # 60
CUT_OVERHEAD = len(CUT_MAGIC) + 8 + 4 + 4 + 4 + 4 + 32          # 67
SLOT_BYTES = 4 + 4 + 32                                         # 40 per (kx, ky, digest) manifest slot


class ChunkstateError(Exception):
    def __init__(self, message):
        super().__init__(f"CHUNKSTATE-REFUSE: {message}")
        self.code = "CHUNKSTATE-REFUSE"


def _check_c(csize):
    if csize not in _CK.CHUNK_SIZES:
        raise ChunkstateError(f"region size {csize!r} is not one of the frozen {_CK.CHUNK_SIZES}")


def region_record_bytes(m):
    """The EXACT record size of an m-resident region: 60 + 29*m."""
    if not (type(m) is int and m >= 0):
        raise ChunkstateError(f"resident count must be a non-negative int, got {m!r}")
    return REC_OVERHEAD + ENTRY_BYTES * m


def _pack_pose(idx, pose):
    if not (type(idx) is int and 0 <= idx < (1 << 32)):
        raise ChunkstateError(f"actor index must be uint32, got {idx!r}")
    fx, fy, g, facing = pose
    out = idx.to_bytes(IDX_BYTES, "big")
    for v in (fx, fy, g):
        if not (type(v) is int and -(1 << 63) <= v < (1 << 63)):
            raise ChunkstateError(f"pose field {v!r} does not fit signed int64 — refuse, never truncate")
        out += (v & ((1 << 64) - 1)).to_bytes(8, "big")
    if not (type(facing) is int and 0 <= facing <= 3):
        raise ChunkstateError(f"facing must be 0..3, got {facing!r}")
    return out + facing.to_bytes(1, "big")


def region_record(kx, ky, boundary, entries):
    """The canonical durable record of one region's residents at one boundary: MAGIC | kx | ky | boundary |
    count | (idx | pose)* | SHA-256. Entries carry the GLOBAL actor index (identity survives the partition)
    and must be strictly ascending."""
    for v, nm in ((kx, "kx"), (ky, "ky")):
        if not (type(v) is int and 0 <= v < (1 << 32)):
            raise ChunkstateError(f"{nm} must be uint32, got {v!r}")
    if not (type(boundary) is int and 0 <= boundary < (1 << 64)):
        raise ChunkstateError(f"boundary must be uint64, got {boundary!r}")
    pre = MAGIC + kx.to_bytes(4, "big") + ky.to_bytes(4, "big") + boundary.to_bytes(8, "big")
    pre += len(entries).to_bytes(4, "big")
    prev = -1
    for idx, pose in entries:
        if idx <= prev:
            raise ChunkstateError(f"entry indices must be strictly ascending, got {idx} after {prev}")
        prev = idx
        pre += _pack_pose(idx, pose)
    return pre + hashlib.sha256(pre).digest()


def _verified(buf, magic, floor):
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise ChunkstateError("a record must be bytes")
    buf = bytes(buf)
    if len(buf) < floor:
        raise ChunkstateError(f"buffer of {len(buf)} bytes is shorter than the {floor}-byte minimum")
    if buf[:len(magic)] != magic:
        raise ChunkstateError(f"bad magic — not a {magic.decode()} object")
    if hashlib.sha256(buf[:-32]).digest() != buf[-32:]:
        raise ChunkstateError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    return buf


def address(buf):
    """The content address of a verified region record or cut manifest: the hex of its embedded digest."""
    if (type(buf) is bytes or type(buf) is bytearray) and bytes(buf[:len(CUT_MAGIC)]) == CUT_MAGIC:
        return _verified(buf, CUT_MAGIC, CUT_OVERHEAD)[-32:].hex()
    return _verified(buf, MAGIC, REC_OVERHEAD)[-32:].hex()


def restore_region(buf):
    """The inverse of `region_record`: (kx, ky, boundary, entries) BIT-FOR-BIT or a typed refuse. The
    digest is checked first; structure (count vs length, ascending indices, cardinal facing) is re-checked
    against a crafted-but-digested record."""
    buf = _verified(buf, MAGIC, REC_OVERHEAD)
    off = len(MAGIC)
    kx = int.from_bytes(buf[off:off + 4], "big"); off += 4
    ky = int.from_bytes(buf[off:off + 4], "big"); off += 4
    boundary = int.from_bytes(buf[off:off + 8], "big"); off += 8
    count = int.from_bytes(buf[off:off + 4], "big"); off += 4
    if len(buf) != REC_OVERHEAD + ENTRY_BYTES * count:
        raise ChunkstateError(f"record length {len(buf)} does not match its count {count}")
    entries, prev = [], -1
    for _ in range(count):
        idx = int.from_bytes(buf[off:off + IDX_BYTES], "big"); off += IDX_BYTES
        fx = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        fy = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        g = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        facing = buf[off]; off += 1
        if idx <= prev:
            raise ChunkstateError("a record with disordered or duplicate indices is refused")
        if facing > 3:
            raise ChunkstateError(f"facing {facing} is not cardinal — a crafted record is refused")
        prev = idx
        entries.append((idx, (fx, fy, g, facing)))
    return kx, ky, boundary, tuple(entries)


def partition(state, csize, w, h):
    """The partition law: each actor is claimed by the region its pose FLOORS into — (cx // C, cy // C) on
    `chunkload`'s grid. Deterministic; identity (the global index) rides along. A pose off the grid cannot
    be regioned and refuses."""
    _check_c(csize)
    if w % csize or h % csize:
        raise ChunkstateError(f"{w}x{h} is not divisible by C={csize} — refuse, never pad")
    out = {}
    for idx, pose in enumerate(state):
        fx, fy, _g, _f = pose
        cx, cy = fx >> 32, fy >> 32
        if not (0 <= cx < w and 0 <= cy < h):
            raise ChunkstateError(f"actor {idx} floors to ({cx},{cy}), off the {w}x{h} grid")
        out.setdefault((cx // csize, cy // csize), []).append((idx, pose))
    return {k: tuple(v) for k, v in out.items()}


def cut(state, boundary, csize, w, h):
    """The consistent cut: one record per occupied region at ONE boundary, bound by a cut manifest —
    CUT_MAGIC | boundary | W | H | C | count | (kx | ky | record-digest)* | SHA-256, regions in row-major
    (ky, kx) order. Returns (manifest, {address: record})."""
    parts = partition(state, csize, w, h)
    records = {k: region_record(k[0], k[1], boundary, es) for k, es in parts.items()}
    keys = sorted(records, key=lambda k: (k[1], k[0]))
    pre = CUT_MAGIC + boundary.to_bytes(8, "big") + w.to_bytes(4, "big") + h.to_bytes(4, "big")
    pre += csize.to_bytes(4, "big") + len(keys).to_bytes(4, "big")
    for kx, ky in keys:
        pre += kx.to_bytes(4, "big") + ky.to_bytes(4, "big") + records[(kx, ky)][-32:]
    man = pre + hashlib.sha256(pre).digest()
    return man, {address(r): r for r in records.values()}


def parse_cut(man):
    """A verified cut manifest -> (boundary, w, h, csize, ((kx, ky, address-hex), ...))."""
    man = _verified(man, CUT_MAGIC, CUT_OVERHEAD)
    off = len(CUT_MAGIC)
    boundary = int.from_bytes(man[off:off + 8], "big"); off += 8
    w = int.from_bytes(man[off:off + 4], "big"); off += 4
    h = int.from_bytes(man[off:off + 4], "big"); off += 4
    csize = int.from_bytes(man[off:off + 4], "big"); off += 4
    count = int.from_bytes(man[off:off + 4], "big"); off += 4
    _check_c(csize)
    if w % csize or h % csize or len(man) != CUT_OVERHEAD + SLOT_BYTES * count:
        raise ChunkstateError("cut manifest structure does not match its counts")
    slots, prev = [], None
    for _ in range(count):
        kx = int.from_bytes(man[off:off + 4], "big"); off += 4
        ky = int.from_bytes(man[off:off + 4], "big"); off += 4
        key = (ky, kx)
        if prev is not None and key <= prev:
            raise ChunkstateError("cut manifest regions must be strictly row-major ordered")
        prev = key
        slots.append((kx, ky, man[off:off + 32].hex())); off += 32
    return boundary, w, h, csize, tuple(slots)


def reunify_records(records, csize):
    """The reunification law, and the four AUTHORITY REFUSES. All records must share ONE boundary (a
    consistent cut); every entry must floor into its claiming region (no annexation); every global index
    exactly once (no double claim, no lost actor: indices are exactly 0..N-1). Returns the global state
    tuple — gate-pinned BYTE-IDENTICAL, through persist.checkpoint, to the monolith's."""
    _check_c(csize)
    if not records:
        raise ChunkstateError("an empty cut reunifies nothing")
    seen_regions, boundary, claimed = set(), None, {}
    for rec in records:
        kx, ky, b, entries = restore_region(rec)
        if (kx, ky) in seen_regions:
            raise ChunkstateError(f"region ({kx},{ky}) appears twice in the cut")
        seen_regions.add((kx, ky))
        if boundary is None:
            boundary = b
        elif b != boundary:
            raise ChunkstateError(f"mixed boundaries {boundary} and {b} — not a consistent cut, refused "
                                  f"rather than aligned")
        for idx, pose in entries:
            fx, fy, _g, _f = pose
            if ((fx >> 32) // csize, (fy >> 32) // csize) != (kx, ky):
                raise ChunkstateError(f"actor {idx} floors outside region ({kx},{ky}) — an annexed actor "
                                      f"is refused")
            if idx in claimed:
                raise ChunkstateError(f"actor {idx} is claimed by two regions — a doubly-owned actor is "
                                      f"refused")
            claimed[idx] = pose
    n = len(claimed)
    if sorted(claimed) != list(range(n)):
        missing = sorted(set(range(max(claimed) + 1)) - set(claimed)) if claimed else []
        raise ChunkstateError(f"the cut loses actors — indices {missing} are claimed by no region")
    return tuple(claimed[i] for i in range(n))


def reunify_cut(man, lookup):
    """Reunify from a content-addressed store: fetch each manifest slot's record, require the bytes to hash
    to the slot's address and to carry the slot's coords and the cut's boundary, then apply the
    reunification law. Missing / tampered / substituted records refuse."""
    boundary, _w, _h, csize, slots = parse_cut(man)
    records = []
    for kx, ky, dig in slots:
        try:
            rec = lookup[dig]
        except KeyError:
            raise ChunkstateError(f"region ({kx},{ky}) record {dig[:12]}… missing from the store")
        gkx, gky, gb, _es = restore_region(rec)
        if bytes(rec)[-32:].hex() != dig:
            raise ChunkstateError(f"region ({kx},{ky}) bytes do not hash to the manifest address — refused")
        if (gkx, gky) != (kx, ky) or gb != boundary:
            raise ChunkstateError(f"region record claims ({gkx},{gky}) b={gb}, manifest slot is "
                                  f"({kx},{ky}) b={boundary} — refused")
        records.append(rec)
    return reunify_records(tuple(records), csize)


def resume_region(heights, entries, cmds, max_step, sub):
    """ONE region recovers independently: resume each resident from its pose (identity preserved). Equals
    the global resume law filtered to these actors — and therefore, by `resurrect`'s certified law, the
    never-died suffix for each."""
    return tuple((idx, _SP.resume_cells(heights, (fx, fy, facing), cmds, max_step, sub))
                 for idx, (fx, fy, _g, facing) in entries)


def cut_bytes(state, csize):
    """The EXACT durable cost of a cut: Σ region_record_bytes(m_r) + the cut manifest (67 + 40*R). Checked
    EQUAL to real bytes; `storecost.within_storage_budget` gates it."""
    _check_c(csize)
    sizes = {}
    for _idx, (fx, fy, _g, _f) in enumerate(state):
        key = ((fx >> 32) // csize, (fy >> 32) // csize)
        sizes[key] = sizes.get(key, 0) + 1
    return sum(region_record_bytes(m) for m in sizes.values()) + CUT_OVERHEAD + SLOT_BYTES * len(sizes)


def chunkstate_digest(name, boundary, csize, witness_hex, nbytes, verdict):
    """URDRCHS1 canon — SHA-256(MAGIC | name | boundary | C | witness | bytes | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|b:{boundary}|c:{csize}|w:{witness_hex}|n:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _island():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["island"]())[1]


_STARTS = ((14, 4), (2, 2), (30, 40))
_CMDS, _MS, _SUB, _C = "eeee", 30, 4, 16


def _scene_consistent_cut():
    """Three actors in three regions at boundary 4: the cut reunifies to the state AND to the monolithic
    persist record byte-for-byte — the same witness."""
    import persist as _PS
    fld = _island()
    state = _SC.boundary_state(fld, _STARTS, _CMDS, _MS, _SUB, 4)
    man, store = cut(state, 4, _C, 64, 64)
    ok = (reunify_cut(man, store) == state
          and _PS.checkpoint(reunify_cut(man, store), 4) == _PS.checkpoint(state, 4))
    return 4, _C, address(man), cut_bytes(state, _C), ("ADMIT" if ok else "CHUNKSTATE-REFUSE")


def _scene_seam_walker():
    """The migrant: actor 0 starts at x=14 and walks east across the x=16 seam — region (0,0) claims it at
    boundary 0, region (1,0) at boundary 4; BOTH cuts reunify exactly. Migration is re-partition."""
    fld = _island()
    s0 = _SC.boundary_state(fld, _STARTS, _CMDS, _MS, _SUB, 0)
    s4 = _SC.boundary_state(fld, _STARTS, _CMDS, _MS, _SUB, 4)
    p0, p4 = partition(s0, _C, 64, 64), partition(s4, _C, 64, 64)
    r0 = [k for k, es in p0.items() if any(i == 0 for i, _p in es)][0]
    r4 = [k for k, es in p4.items() if any(i == 0 for i, _p in es)][0]
    man0, st0 = cut(s0, 0, _C, 64, 64)
    man4, st4 = cut(s4, 4, _C, 64, 64)
    ok = (r0 != r4 and reunify_cut(man0, st0) == s0 and reunify_cut(man4, st4) == s4)
    return 4, _C, address(man4), cut_bytes(s4, _C), ("ADMIT" if ok else "CHUNKSTATE-REFUSE")


def _scene_double_claim():
    """The double-authority exploit: region B also records region A's actor. Reunification refuses."""
    fld = _island()
    state = _SC.boundary_state(fld, _STARTS, _CMDS, _MS, _SUB, 4)
    parts = partition(state, _C, 64, 64)
    keys = sorted(parts)
    forged = dict(parts)
    forged[keys[1]] = tuple(sorted(forged[keys[1]] + (parts[keys[0]][0],)))
    try:
        reunify_records(tuple(region_record(k[0], k[1], 4, es) for k, es in sorted(forged.items())), _C)
        verdict = "ADMIT"                                        # unreachable if the authority law holds
    except ChunkstateError:
        verdict = "CHUNKSTATE-REFUSE"
    return 4, _C, "0" * 64, cut_bytes(state, _C), verdict


_SCENES = {"consistent_cut": _scene_consistent_cut, "seam_walker": _scene_seam_walker,
           "double_claim": _scene_double_claim}
SCENES = ("consistent_cut", "seam_walker", "double_claim")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    boundary, csize, wit, nbytes, verdict = scene_case(name)
    return chunkstate_digest(name, boundary, csize, wit, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_chunkstate.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ChunkstateError(f"no golden named {name!r}")
