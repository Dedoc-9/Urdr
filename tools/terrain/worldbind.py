# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""worldbind (URDRWBD1) — an authored world bound to certified ground, exactly or not at all.

THE CLAIM CLASS THIS RUNG MOVES: two repositories hold complementary halves of one world and
have never been joined. Ursprung's `weltwerk` authors CAUSAL TOPOLOGY — a text `.wrk` of zones,
entities and typed relations, with geometry declared downstream as a regenerable projection —
and this tree authors CERTIFIED TERRAIN, seeded and digest-pinned, with no entity layer at all.
The bridge is a PLACEMENT, not an import. But the reconnaissance (docs/ursprung_bridge.md)
found the seam carries two silent corruptions rather than one missing feature, and this rung
is the door that refuses both:

  * THE NUMERIC SEAM. Authored positions are decimal text destined for float32 on the other
    side; this tree refuses floats at its door. Every coordinate is parsed as an EXACT rational
    (integer mantissa, power of ten) and converted by integer arithmetic alone. A position that
    cannot be represented exactly on the lattice is REFUSED, never rounded — because a rounded
    placement is a world that silently disagrees with its own authoring, and the disagreement
    would first surface as a body sunk into a hill.
  * THE AXIS SEAM. The authoring frame is Y-UP with the ground plane (x, z) — measured, not
    assumed: `weltwerk/fps_demo/weltwerk_fps.html` writes `position.set(e.x, h/2, e.z)`, and
    every authored `position X 0 Z` puts zero in the vertical slot. This runtime is Z-UP with
    the ground plane (x, y). The map is DECLARED and its handedness is CHECKED: a permutation
    whose determinant is not +1 mirrors the world, and a mirrored fortress is a different
    fortress that no digest would catch.

What the rung then establishes over that door:

  * GROUND IS SAMPLED FROM THE CANON, AND CHECKED ACROSS LANGUAGES. An entity's height is the
    certified heightfield at its bound tile, computed here through `heightfield.noise16`
    (imported, never copied) under the demo's declared world parameters — and compared against
    a COMMITTED RECORD of the same tiles produced by the Rust demo's own stride-1 height path.
    Python's binder and the renderer's ground agree, or the rung reddens. An entity placed on
    ground the renderer does not draw is the defect this check exists to catch.
  * THE WORLD IS CONTENT-ADDRESSED. Entities partition into fixed chunks by lattice position;
    each chunk canonicalizes to bytes under a total order and is named by its own digest; the
    manifest binds the terrain canon, the authored spec's digest, and every chunk address to
    its digest, under one world digest. Loading is therefore not an act of trust: a record that
    does not hash to its address refuses.
  * AN EDIT DIRTIES WHAT IT TOUCHES AND NOTHING ELSE. Moving one entity changes exactly its
    chunk's digest (or exactly two, when it crosses a boundary) and leaves every other chunk
    byte-identical — the locality property the whole streaming design will rest on, asserted
    here where it is cheap rather than discovered later where it is not.

does_not_show: rendering (no pixel is drawn here — the runtime's adoption of these records is a
later rung with its own before/after); the causal ANALYSIS of the authored graph (reachability,
SCC and bottleneck live in weltwerk's own lint under its own discipline — this rung carries the
relations as data and grades none of them); streaming or persistence at scale (chunk addressing
is established, a loader is not); collision, contact or gameplay meaning of any entity;
whether the authored fortress is a good world.

falsifier: a coordinate that cannot be represented exactly refuses; a rounding convenience
changes the world digest and is caught; an axis map whose determinant is not +1 refuses; a
manifest naming different terrain refuses; a tampered chunk digest refuses at load; a shuffled
entity order produces IDENTICAL bytes (canonicity, the identity control); an edit that dirties
an untouched chunk is caught; and the Python ground must equal the committed Rust ground at
every bound tile.
"""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import heightfield as _hf                # URDRHF1, imported: the canon's own noise

MAGIC = b"URDRWBD1"
FORMAT_REVISION = 1

# ---- the declared frames -------------------------------------------------------------------------
# AUTHOR frame: y-up, ground plane (x, z), decimal text, 1 author unit = 1 tile.
# RUNTIME frame: z-up, ground plane (x, y), exact integers, Q8 world units, TILE units per tile.
TILE = 3                                 # world units per tile (the demo's own constant)
Q8 = 256
WORLD_UNITS_PER_AUTHOR = TILE            # DECLARED: one authored unit is one tile
# author (ax, ay, az) -> runtime (ax, -az, ay). Right-handed y-up to right-handed z-up.
AXIS_MAP = ((1, 0, 0),
            (0, 0, -1),
            (0, 1, 0))
CHUNK_TILES = 16

# the demo's declared world parameters (mirrored constants, checked against the Rust record)
W_SEED = 1958
W_HS = 420
W_LAYERS = ((48, 5), (12, 3), (6, 2), (3, 1))
W_RAWMAX = 11 * 0xFFFF
H_SCALE = 16

CORPUS = ("spec/attest/world-fortress.wrk",
          "c8417af7c82ce6cba8df706c0a0110b7135677cc5371e00a0749799dd11aadbd")
GROUND_RECORD = ("spec/attest/world-fortress-ground.txt",
                 "f8d3621e6bc13d9e85569410be541fa2f202dd5c9d0c6c8ce139632a26ec295b")


class WorldbindError(Exception):
    def __init__(self, message):
        super().__init__(f"WORLDBIND-REFUSE: {message}")
        self.code = "WORLDBIND-REFUSE"


def _load(path, pin, text=None):
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    if hashlib.sha256(text.encode()).hexdigest() != pin:
        raise WorldbindError(f"{path} does not hash to its pin — tampered or wrong file")
    return text


def load_corpus(text=None):
    return _load(CORPUS[0], CORPUS[1], text)


def load_ground_record(text=None):
    return _load(GROUND_RECORD[0], GROUND_RECORD[1], text)


# ---- the numeric door ----------------------------------------------------------------------------
def parse_exact(token):
    """Decimal text -> (mantissa, exponent) with value == mantissa / 10**exponent. NO FLOAT IS
    CONSTRUCTED — not even transiently — because a float that touches the value has already
    decided what is representable."""
    t = token.strip()
    if not t or t in ("+", "-", ".", "+.", "-."):
        raise WorldbindError(f"{token!r} is not a coordinate")
    neg = t[0] == "-"
    if t[0] in "+-":
        t = t[1:]
    if t.count(".") > 1 or not t.replace(".", "").isdigit():
        raise WorldbindError(f"{token!r} is not an exact decimal — no float is accepted here")
    if "." in t:
        whole, frac = t.split(".")
    else:
        whole, frac = t, ""
    mant = int(whole + frac) if (whole + frac) else 0
    return (-mant if neg else mant), len(frac)


def to_q8(token):
    """Author decimal -> exact Q8 world units, or REFUSE. value * TILE * 256 must be an integer:
    the door is `10**exp divides mant * TILE * 256`, checked by remainder, never by rounding."""
    mant, exp = parse_exact(token)
    num = mant * WORLD_UNITS_PER_AUTHOR * Q8
    den = 10 ** exp
    if num % den != 0:
        raise WorldbindError(
            f"{token!r} is not representable on the lattice "
            f"({WORLD_UNITS_PER_AUTHOR} world units per author unit, Q8) — refused rather "
            f"than rounded, because a rounded placement is a world that disagrees with its "
            f"own authoring")
    return num // den


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def check_axis_map(m=AXIS_MAP):
    """A frame change must be a rotation, not a reflection: determinant +1. A mirrored world is
    a different world that no content digest would ever notice."""
    if _det3(m) != 1:
        raise WorldbindError("the axis map is not right-handed (det != +1) — it mirrors the "
                             "world")
    return True


def map_axes(v, m=AXIS_MAP):
    check_axis_map(m)
    return tuple(sum(m[r][c] * v[c] for c in range(3)) for r in range(3))


# ---- the certified ground ------------------------------------------------------------------------
def ground_at(tx, ty, cache=None):
    """The canon's own height at a lattice tile, through heightfield.noise16 — the demo's
    stride-1 path, mirrored in exact integers."""
    cache = {} if cache is None else cache
    raw = 0
    for li, (cell, amp) in enumerate(W_LAYERS):
        raw += amp * _hf.noise16(W_SEED, li, cell, tx, ty, cache)
    return (raw * W_HS // W_RAWMAX) // H_SCALE


def parse_ground_record(text):
    out = {}
    for ln in text.rstrip("\n").split("\n"):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.split()
        if len(p) != 4 or p[0] != "ground":
            raise WorldbindError("ground record line malformed")
        out[(int(p[1]), int(p[2]))] = int(p[3])
    if not out:
        raise WorldbindError("empty ground record")
    return out


def ground_agrees_across_languages():
    """The load-bearing cross-language check: this binder's ground equals the Rust demo's own
    stride-1 height at every recorded tile. An entity placed on ground the renderer does not
    draw is exactly the defect this catches."""
    rec = parse_ground_record(load_ground_record())
    cache = {}
    return all(ground_at(tx, ty, cache) == h for (tx, ty), h in sorted(rec.items()))


# ---- the authored spec ---------------------------------------------------------------------------
FORWARD_RELATIONS = ("emits", "blocks", "protects", "feeds", "defends", "consumes",
                     "sustains", "controls", "powers", "contains", "supplies")
REVERSED_RELATIONS = ("depends_on", "powered_by", "fed_by", "sustained_by", "needs")
ATTR_KEYS = ("zone", "position", "health")


def parse_wrk(text):
    """The authored text -> entities and relations. Faithful to weltwerk's format: `world`,
    `zone X`, `entity NAME:` then indented `key value` lines; REVERSED relations point from
    target to entity (editing the target can affect the entity)."""
    world_name = None
    zones, ents, rels = [], {}, []
    cur = None
    for raw in text.split("\n"):
        ln = raw.split("#")[0].rstrip()
        if not ln.strip():
            continue
        indented = ln[0] in " \t"
        s = ln.strip()
        if not indented:
            cur = None
            if s.startswith("world "):
                world_name = s[6:].strip().strip('"')
            elif s.startswith("zone "):
                zones.append(s[5:].strip())
            elif s.startswith("entity ") and s.endswith(":"):
                cur = s[7:-1].strip()
                if cur in ents:
                    raise WorldbindError(f"entity {cur!r} declared twice")
                ents[cur] = {"zone": "", "pos": None, "health": 0}
            else:
                raise WorldbindError(f"unparsed top-level line {s!r}")
            continue
        if cur is None:
            raise WorldbindError(f"indented line outside an entity: {s!r}")
        key, _, rest = s.partition(" ")
        rest = rest.strip()
        if key == "zone":
            ents[cur]["zone"] = rest
        elif key == "health":
            ents[cur]["health"] = int(rest)
        elif key == "position":
            parts = rest.split()
            if len(parts) != 3:
                raise WorldbindError(f"position needs three coordinates, got {rest!r}")
            ents[cur]["pos"] = tuple(parts)
        elif key in REVERSED_RELATIONS:
            rels.append((rest, key, cur))
        elif key in FORWARD_RELATIONS:
            rels.append((cur, key, rest))
        else:
            raise WorldbindError(f"unknown key {key!r} — an unrecognised relation is not "
                                 f"silently data")
    if world_name is None:
        raise WorldbindError("no world name declared")
    for name, e in ents.items():
        if e["pos"] is None:
            raise WorldbindError(f"entity {name!r} has no position — it cannot be bound")
        if e["zone"] and e["zone"] not in zones:
            raise WorldbindError(f"entity {name!r} names undeclared zone {e['zone']!r}")
    return {"world": world_name, "zones": sorted(zones), "entities": ents,
            "relations": sorted(rels)}


# ---- binding -------------------------------------------------------------------------------------
def bind(spec, ground=ground_at):
    """Authored spec -> bound entities in exact runtime coordinates on certified ground."""
    check_axis_map()
    cache = {}
    out = {}
    for name in sorted(spec["entities"]):
        e = spec["entities"][name]
        aq = tuple(to_q8(c) for c in e["pos"])          # exact, or refused
        rx, ry, rz_off = map_axes(aq)
        if rx % (TILE * Q8) or ry % (TILE * Q8):
            raise WorldbindError(
                f"entity {name!r} does not land on a tile centre — sub-tile placement is a "
                f"later contract, refused rather than assumed")
        tx, ty = rx // (TILE * Q8), ry // (TILE * Q8)
        g8 = ground(tx, ty, cache) * Q8
        out[name] = {"tile": (tx, ty), "x8": rx, "y8": ry, "z8": g8 + rz_off,
                     "ground8": g8, "zone": e["zone"], "health": e["health"]}
    return out


def chunk_of(tile):
    return (tile[0] // CHUNK_TILES, tile[1] // CHUNK_TILES)


# ---- canonical records ---------------------------------------------------------------------------
def chunk_bytes(bound, rels, addr):
    """One chunk's canonical bytes: a total order over its entities and over the relations whose
    SOURCE lives in it. Sorted, fixed-form, no dict order anywhere — two processes that disagree
    about iteration order still produce the same bytes."""
    lines = [f"CHUNK {addr[0]} {addr[1]}"]
    members = sorted(n for n, b in bound.items() if chunk_of(b["tile"]) == addr)
    for n in members:
        b = bound[n]
        lines.append(f"E {n} {b['zone']} {b['x8']} {b['y8']} {b['z8']} {b['health']}")
    mset = set(members)
    for (src, rel, dst) in sorted(rels):
        if src in mset:
            lines.append(f"R {src} {rel} {dst}")
    return ("\n".join(lines) + "\n").encode()


def chunk_digest(raw):
    return hashlib.sha256(MAGIC + b"|chunk|" + raw).hexdigest()


def chunk_addresses(bound):
    return sorted({chunk_of(b["tile"]) for b in bound.values()})


def build_world(spec, bound):
    chunks = {}
    for addr in chunk_addresses(bound):
        raw = chunk_bytes(bound, spec["relations"], addr)
        chunks[addr] = (raw, chunk_digest(raw))
    return chunks


def content_bytes(spec, chunks):
    """WHAT THE WORLD IS — invariant under how it was written. The gate's own reconcile line
    splits `rowset` from `content` for exactly this reason: a digest that mixes what a thing
    IS with how it was PRODUCED can answer neither question."""
    lines = [f"WORLD {spec['world']}",
             f"format_revision {FORMAT_REVISION}",
             f"terrain canon mountains seed {W_SEED} hs {W_HS} hscale {H_SCALE} tile {TILE}",
             f"axis_map {AXIS_MAP[0]}{AXIS_MAP[1]}{AXIS_MAP[2]}".replace(" ", ""),
             f"units_per_author {WORLD_UNITS_PER_AUTHOR}",
             f"chunk_tiles {CHUNK_TILES}"]
    for addr in sorted(chunks):
        lines.append(f"chunk {addr[0]} {addr[1]} {chunks[addr][1]}")
    return ("\n".join(lines) + "\n").encode()


def manifest_bytes(spec, chunks, wrk_text):
    """The content, plus PROVENANCE: which exact authored text produced it. Re-ordering the
    authoring changes this and MUST NOT change the content digest — the shuffle law asserts
    both halves, because a record that cannot tell an edit from a reformat is as broken as one
    that cannot tell two worlds apart."""
    prov = f"authoring wrk {hashlib.sha256(wrk_text.encode()).hexdigest()}\n"
    return content_bytes(spec, chunks) + prov.encode()


def content_digest(cb):
    return hashlib.sha256(MAGIC + b"|content|" + cb).hexdigest()


def world_digest(mb):
    return hashlib.sha256(MAGIC + b"|world|" + mb).hexdigest()


def save(text=None):
    """The whole pipeline: authored text -> exact binding -> canonical chunks -> manifest."""
    wrk = load_corpus(text) if text is None else text
    spec = parse_wrk(wrk)
    bound = bind(spec)
    chunks = build_world(spec, bound)
    cb = content_bytes(spec, chunks)
    mb = manifest_bytes(spec, chunks, wrk)
    return {"spec": spec, "bound": bound, "chunks": chunks, "content": cb, "manifest": mb,
            "content_digest": content_digest(cb), "digest": world_digest(mb)}


def load(world):
    """Loading is not an act of trust: every chunk must hash to the address the manifest gives
    it, or the load refuses."""
    declared = {}
    for ln in world["manifest"].decode().rstrip("\n").split("\n"):
        p = ln.split()
        if p and p[0] == "chunk":
            declared[(int(p[1]), int(p[2]))] = p[3]
    if sorted(declared) != sorted(world["chunks"]):
        raise WorldbindError("manifest chunk set != stored chunk set")
    for addr, dig in declared.items():
        raw, _stored = world["chunks"][addr]
        if chunk_digest(raw) != dig:
            raise WorldbindError(f"chunk {addr} does not hash to its manifest address")
    if world_digest(world["manifest"]) != world["digest"]:
        raise WorldbindError("world digest does not match its manifest")
    return True


# ---- the laws ------------------------------------------------------------------------------------
def round_trip_is_byte_identical():
    a = save()
    b = save()
    return (a["manifest"] == b["manifest"] and a["digest"] == b["digest"]
            and a["content"] == b["content"] and a["content_digest"] == b["content_digest"]
            and all(a["chunks"][k][0] == b["chunks"][k][0] for k in a["chunks"])
            and load(a))


def canonical_under_shuffle():
    """The identity control: re-order the authored entity blocks and the bytes must not move.
    Canonicity that is never attacked is a claim, not a property."""
    wrk = load_corpus()
    lines = wrk.split("\n")
    head, blocks, cur = [], [], None
    for ln in lines:
        starts = ln.startswith("entity ") and ln.rstrip().endswith(":")
        if starts:
            cur = [ln]
            blocks.append(cur)
        elif cur is not None:
            cur.append(ln)
        else:
            head.append(ln)
    shuffled = "\n".join(head + [l for b in reversed(blocks) for l in b])
    a = save()
    b = save(shuffled)
    same_content = (a["content_digest"] == b["content_digest"]
                    and set(a["chunks"]) == set(b["chunks"])
                    and all(a["chunks"][k][0] == b["chunks"][k][0] for k in a["chunks"]))
    # and the PROVENANCE half must differ, or the manifest is not recording what produced it
    return same_content and a["digest"] != b["digest"]


def an_edit_dirties_only_what_it_touches():
    """Move one entity WITHIN its chunk: exactly that chunk's digest moves, every other chunk
    stays byte-identical."""
    base = save()
    moved = load_corpus().replace("position 14 0 -6", "position 15 0 -6")
    after = save(moved)
    tgt = chunk_of(base["bound"]["generator"]["tile"])
    changed = [k for k in base["chunks"]
               if k in after["chunks"] and base["chunks"][k][1] != after["chunks"][k][1]]
    return (changed == [tgt] and base["digest"] != after["digest"]
            and set(base["chunks"]) == set(after["chunks"]))


def bound_entities_stand_on_canon_ground():
    w = save()
    rec = parse_ground_record(load_ground_record())
    for b in w["bound"].values():
        if rec.get(b["tile"]) is None:
            return False
        if b["ground8"] != rec[b["tile"]] * Q8:
            return False
    return True


# ---- the plants ----------------------------------------------------------------------------------
def an_inexact_coordinate_refuses():
    """0.1 of a tile is not representable in Q8 world units: 1*3*256/10 = 76.8."""
    try:
        to_q8("0.1")
    except WorldbindError:
        return True
    return False


def a_representable_fraction_admits():
    """The door must ADMIT what it can represent, or it is a wall rather than a door: half a
    tile is 384 exact Q8 units."""
    return to_q8("0.5") == 384 and to_q8("-0.5") == -384 and to_q8("2") == 1536


def placement_is_injective():
    """THE PROPERTY SILENT ROUNDING WOULD DESTROY: distinct authored coordinates never bind to
    one runtime coordinate. A binder that rounded would map 14 and 14.4 to the same tile and
    two different authored worlds would share a digest — indistinguishable forever. Here the
    representable ones stay distinct and the rest refuse, so the collision cannot be built."""
    seen = {}
    for tok in ("14", "14.5", "14.25", "13.75", "-3", "-3.5", "0", "0.5"):
        q = to_q8(tok)
        if q in seen:
            return False
        seen[q] = tok
    for tok in ("14.4", "0.1", "0.01", "13.9"):
        try:
            to_q8(tok)
            return False                     # a value we cannot place must never be placed
        except WorldbindError:
            continue
    return True


def a_mirrored_axis_map_refuses():
    mirror = ((1, 0, 0), (0, 0, 1), (0, 1, 0))          # det = -1
    try:
        check_axis_map(mirror)
    except WorldbindError:
        return True
    return False


def a_tampered_chunk_refuses_at_load():
    w = save()
    addr = sorted(w["chunks"])[0]
    raw, dig = w["chunks"][addr]
    w["chunks"] = dict(w["chunks"])
    w["chunks"][addr] = (raw + b"E ghost nowhere 0 0 0 1\n", dig)
    try:
        load(w)
    except WorldbindError:
        return True
    return False


def a_float_coordinate_refuses():
    """Not merely 'a float is converted' — the parser refuses the token shape entirely, so no
    float ever exists to be converted."""
    for bad in ("1e3", "nan", "inf", "0x10", "1.2.3"):
        try:
            to_q8(bad)
            return False
        except WorldbindError:
            continue
    return True


def a_subtile_placement_refuses():
    """Half-tile placement is exactly representable but is NOT yet a declared contract, so it
    refuses at binding rather than being quietly admitted — the door and the contract are
    separate things."""
    try:
        bind(parse_wrk(load_corpus().replace("position 14 0 -6", "position 14.5 0 -6")))
    except WorldbindError:
        return True
    return False


# ---- scenes --------------------------------------------------------------------------------------
def scene_case(name):
    w = save()
    if name == "fortress":
        rows = [(n, b["tile"], b["x8"], b["y8"], b["z8"], b["ground8"], b["zone"], b["health"])
                for n, b in sorted(w["bound"].items())]
        return repr((w["spec"]["world"], w["spec"]["zones"], w["spec"]["relations"], rows,
                     sorted((a, d) for a, (_r, d) in w["chunks"].items()),
                     w["content_digest"], w["digest"]))
    raise WorldbindError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_worldbind.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise WorldbindError(f"no golden named {name!r}")
