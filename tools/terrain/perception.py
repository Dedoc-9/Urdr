# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""perception — WITNESSED ABSENCE as server-authoritative AoI (URDRPCP1): the anti-cheat Band A rung,
and the sound kernel of the operator's Ø (bridge of potential) idea, built as a COMPOSITION with NO NEW
GLYPH (the kernel stays frozen; see `docs/perception_brief.md` for the design pass, the researched
hardenings, and the D1 §20 glyph ruling).

THE THESIS: witnessed absence is the D15 presentation firewall (`view_witness`) applied to RESIDENCY.
Two channels, never one packed word:
  * THE WITNESS — the authoritative world (entities at integer positions, each carrying its authority
    digest), exact and untouched by perception.
  * THE RESIDENCY CHANNEL — a per-client MANIFESTED set (which entities this client may perceive),
    cited to the witness but structurally WALLED from it. This is the "structural instruction" of the
    dual-state scalar, kept in a SEPARATE channel from the value — packing it into the 64-bit word would
    steal range from the exact-i64/refuse-on-overflow law or move the value's content identity, cracking
    determinism.

A hidden entity is therefore not a zeroed record with a visibility flag — it is an UN-ADDRESSED ABSENCE:
there is no byte to read. The CLIENT TRANSCRIPT is a PURE FUNCTION of the manifested set, so a wallhack
replayed against it finds NOTHING for anything out of view. `∅→1` (the operator's manifestation) is
`driftgaze`'s acquire-on-cross: turning to face an entity MINTS it into the manifested set, cited to the
authority.

THE THIRD SEAM THIS TARGETS (aimed at, NOT claimed as surpassed). The literature survey identified the
publicly-described state of the art — server-authoritative visibility systems such as VALORANT's Fog of
War and CS2's Fog of War (per-tick server-side visibility determination, multiple line-of-sight rays,
precomputed visibility structures, conservative velocity margins to reduce pop-in) — and isolated three
remaining seams: (1) the visibility margin is an unavoidable asymmetric information leak; (2) audio
propagation and physics/hitbox interactions are independent channels needing separate treatment; (3)
timing and bandwidth characteristics can themselves reveal impending visibility changes (e.g. a burst of
updates when an entity becomes visible). URDRPCP1 is AIMED at seam (3): the transcript is CONSTANT-SHAPE
— padded to a fixed capacity, so its byte-length is invariant to the hidden set; the traffic shape
carries no information about how many entities are hidden or about to appear — and the one unavoidable
leak (the pre-reveal MARGIN, the peeker's-advantage tradeoff) is made an EXPLICIT, BOUNDED quantity, not
pretended to be zero. Whether this ultimately EXCEEDS existing production systems is a question for
empirical evaluation, NOT something these proofs establish: the proofs establish properties of THIS
protocol, not comparative performance or completeness versus commercial anti-cheat.

THE EXACT-INTEGER AoI (deterministic, no floats): an entity is MANIFESTED to a client iff it is in front
(dot(view, facing) > 0), within the wedge (|cross| · hw ≤ dot · hh — the half-angle as an integer slope
hh/hw), within the squared range plus the declared margin band (d² ≤ range² + margin), and NOT OCCLUDED
(the integer supercover of the segment viewpoint→entity crosses no wall cell). Everything else is absent.

GRADE. Witness-blindness (perception returns a transcript, never a world); hidden-set invariance (a
change confined to out-of-wedge/occluded entities yields a BYTE-IDENTICAL transcript); the constant-shape
transcript (length invariant to the manifested count); the wallhack-probe-finds-nothing property; the
certified margin band; the lawful mint (∅→1) and the citation contract (a forged citation reddens); and a
seeded property sweep are MEASURED (exact, reproducible, a defect diverges — a leak-the-hidden manifest
makes the sweep raise). DECLARED, honestly: the MARGIN is a real, bounded, DECLARED leak — pop-in cannot
be avoided without leaking a margin; the rung bounds and certifies it, it does not eliminate it, and the
peeker's-advantage asymmetry is latency-inherent and NOT solved here. AUDIO and physics-HITBOX channels
are OUT OF SCOPE (this governs the position/state channel). PASSIVE-INFORMATION cheats only — witnessed
absence defeats ESP/wallhacks that read data the client should not have; it does NOT touch aim-assist,
trigger-bots, or any cheat operating on legitimately-visible data (the honest aimbot boundary). The
constant-shape hardening hides the COUNT via length; content-level indistinguishability (padding that
looks like real data) would need an encryption layer, declared out of scope. `does_not_show`: real
line-of-sight over continuous geometry (this is an exact integer grid model); cross-placement (URDRPCP1
Python reference only)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRPCP1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

DIGEST_BYTES = 32
CAPACITY = 8                                                    # fixed transcript slots (constant-shape)
SLOT_BYTES = 4 + 4 + 4 + DIGEST_BYTES                           # eid | x | y | cite = 44
PAD_EID = 0xFFFFFFFF                                            # the absence/padding sentinel — Ø
_HEADER = len(MAGIC) + 4


class PerceptionError(Exception):
    def __init__(self, message):
        super().__init__(f"PERCEPTION-REFUSE: {message}")
        self.code = "PERCEPTION-REFUSE"


def client(px, py, dx, dy, hw, hh, range2, margin):
    """A viewpoint: position (px,py), integer facing (dx,dy), wedge half-angle as the integer slope
    hh/hw, squared range, and an additive margin band on d² (the declared early-reveal leak)."""
    for v in (px, py, dx, dy, hw, hh, range2, margin):
        if type(v) is not int:
            raise PerceptionError(f"client fields must be int, got {v!r}")
    if (dx, dy) == (0, 0):
        raise PerceptionError("a viewpoint needs a facing direction")
    if hw <= 0 or hh <= 0 or range2 < 0 or margin < 0:
        raise PerceptionError("wedge slope must be positive; range/margin non-negative")
    return (px, py, dx, dy, hw, hh, range2, margin)


# ---- the exact-integer AoI (the witness read, never written) -----------------------------
def _supercover(x0, y0, x1, y1):
    """Every integer grid cell the segment (x0,y0)→(x1,y1) passes through — exact integer traversal."""
    cells = {(x0, y0)}
    dx, dy = x1 - x0, y1 - y0
    nx, ny = abs(dx), abs(dy)
    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1
    px, py, ix, iy = x0, y0, 0, 0
    while ix < nx or iy < ny:
        dec = (1 + 2 * ix) * ny - (1 + 2 * iy) * nx
        if dec == 0:
            px += sx; py += sy; ix += 1; iy += 1
        elif dec < 0:
            px += sx; ix += 1
        else:
            py += sy; iy += 1
        cells.add((px, py))
    return cells


def _occluded(walls, x0, y0, x1, y1):
    if not walls:
        return False
    cells = _supercover(x0, y0, x1, y1)
    cells.discard((x0, y0))
    cells.discard((x1, y1))
    return any(c in walls for c in cells)


def _visible(entities, walls, cl, eid):
    px, py, dx, dy, hw, hh, r2, margin = cl
    ex, ey, _cite = entities[eid]
    vx, vy = ex - px, ey - py
    dot = vx * dx + vy * dy
    if dot <= 0:
        return False                                           # behind / not in front
    if vx * vx + vy * vy > r2 + margin:
        return False                                           # beyond range + the declared margin band
    if abs(vx * dy - vy * dx) * hw > dot * hh:
        return False                                           # outside the wedge (integer half-angle)
    if _occluded(walls, px, py, ex, ey):
        return False                                           # a wall stands between
    return True


def _manifest(entities, walls, cl):
    """THE RESIDENCY CHANNEL: the sorted eids this client may perceive. Exposed at module scope so the
    falsifiers can plant a leak-the-hidden defect and prove the sweep reddens."""
    return sorted(eid for eid in entities if _visible(entities, walls, cl, eid))


def manifest(entities, walls, cl):
    return _manifest(entities, walls, cl)


# ---- the constant-shape transcript (the client's view — absence is un-addressed) ---------
def _cite_bytes(cite_hex):
    if not (isinstance(cite_hex, str) and len(cite_hex) == 2 * DIGEST_BYTES):
        raise PerceptionError(f"a citation must be {2 * DIGEST_BYTES} hex chars, got {cite_hex!r}")
    try:
        return bytes.fromhex(cite_hex)
    except ValueError:
        raise PerceptionError("citation is not hex")


def _slot(eid, x, y, cite_hex):
    return (eid.to_bytes(4, "big") + (x & 0xFFFFFFFF).to_bytes(4, "big")
            + (y & 0xFFFFFFFF).to_bytes(4, "big") + _cite_bytes(cite_hex))


_PAD_SLOT = PAD_EID.to_bytes(4, "big") + b"\x00" * (SLOT_BYTES - 4)


def transcript_bytes_len():
    return _HEADER + CAPACITY * SLOT_BYTES + DIGEST_BYTES


def perceive(entities, walls, cl):
    """SERVER-AUTHORITATIVE PERCEPTION: emit the client's transcript — ONLY the manifested entities, in a
    CONSTANT-SHAPE record padded to CAPACITY with the absence sentinel Ø. Returns bytes; the world is
    NEVER modified (witness-blind — this returns a transcript, not a world). A change confined to hidden
    entities produces byte-identical output (the transcript is a pure function of the manifested set)."""
    man = _manifest(entities, walls, cl)
    if len(man) > CAPACITY:
        raise PerceptionError(f"{len(man)} manifested entities exceed the transcript capacity "
                              f"{CAPACITY} — refuse rather than silently drop (priority policy is a "
                              f"declared successor)")
    body = bytearray(MAGIC) + CAPACITY.to_bytes(4, "big")
    for eid in man:
        ex, ey, cite = entities[eid]
        body += _slot(eid, ex, ey, cite)
    for _ in range(CAPACITY - len(man)):
        body += _PAD_SLOT
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(transcript):
    if not (type(transcript) is bytes or type(transcript) is bytearray):
        raise PerceptionError("a transcript must be bytes")
    t = bytes(transcript)
    if len(t) != transcript_bytes_len():
        raise PerceptionError(f"a transcript must be exactly {transcript_bytes_len()} bytes")
    if t[:len(MAGIC)] != MAGIC:
        raise PerceptionError("bad magic — not a URDRPCP1 transcript")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise PerceptionError("digest mismatch — tampered or truncated")
    off = _HEADER
    slots = []
    for _ in range(CAPACITY):
        raw = t[off:off + SLOT_BYTES]; off += SLOT_BYTES
        eid = int.from_bytes(raw[:4], "big")
        if eid == PAD_EID:
            continue                                           # Ø — an absence, not a record
        x = int.from_bytes(raw[4:8], "big", signed=True)
        y = int.from_bytes(raw[8:12], "big", signed=True)
        slots.append((eid, x, y, raw[12:].hex()))
    return slots


def probe(transcript, eid):
    """A WALLHACK PROBE, run against the client transcript: (x, y, cite) if the entity is manifested, or
    None — an UN-ADDRESSED ABSENCE. A hidden entity yields None because there is no byte to read."""
    for (e, x, y, cite) in _parse(transcript):
        if e == eid:
            return (x, y, cite)
    return None


def verify_transcript(entities, walls, cl, transcript):
    """THE CITATION CONTRACT (view_witness): every manifested slot must equal the authority — the right
    manifested set, each at the world's live position and carrying the world's live citation. A forged
    citation, an injected hidden entity, or a dropped visible one returns False."""
    try:
        slots = _parse(transcript)
    except PerceptionError:
        return False
    man = _manifest(entities, walls, cl)
    if sorted(e for (e, _x, _y, _c) in slots) != man:
        return False
    for (e, x, y, cite) in slots:
        ex, ey, ecite = entities[e]
        if (x, y, cite) != (ex, ey, ecite):
            return False
    return True


def forge_citation(transcript, eid):
    """A falsifier tool: rewrite one manifested slot's cited digest (a lie the view_witness contract must
    catch). Never a law."""
    t = bytearray(transcript[:-DIGEST_BYTES])
    off = _HEADER
    for _ in range(CAPACITY):
        e = int.from_bytes(t[off:off + 4], "big")
        if e == eid:
            t[off + 12] ^= 0x01                                # flip one byte of the citation
            break
        off += SLOT_BYTES
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


# ---- digests -----------------------------------------------------------------------------
def world_digest(entities, walls):
    """The witness digest — a content address of the authoritative world (entities + walls)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for eid in sorted(entities):
        ex, ey, cite = entities[eid]
        hh.update(f"|e{eid}:{ex}:{ey}:{cite}".encode())
    for (wx, wy) in sorted(walls):
        hh.update(f"|w{wx}:{wy}".encode())
    return hh.hexdigest()


def transcript_digest(transcript):
    return hashlib.sha256(MAGIC + bytes(transcript)).hexdigest()


def perception_digest(name, world_hex, transcript_hex, manifested, verdict):
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{world_hex}|t:{transcript_hex}|m:{manifested}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) ------------------------------------------------------
def _d(i):
    return ("%064x" % ((0xA11CE + i * 0x9E3779B1) & ((1 << 256) - 1)))[:64]


def _scene(name, entities, walls, cl):
    t = perceive(entities, walls, cl)
    man = _manifest(entities, walls, cl)
    verdict = "ADMIT" if verify_transcript(entities, walls, cl, t) else "PERCEPTION-REFUSE"
    return (world_digest(entities, walls), transcript_digest(t), len(man), verdict)


def _scene_sniper():
    """A narrow wedge (slope 1/10): only the entity dead ahead is manifested; the flanking entities are
    absent — the sniper's tunnel vision, and everything outside it un-addressed."""
    entities = {1: (10, 0, _d(1)), 2: (10, 5, _d(2)), 3: (10, -5, _d(3)), 4: (3, 3, _d(4))}
    return _scene("sniper", entities, frozenset(), client(0, 0, 1, 0, 10, 1, 400, 0))


def _scene_corner():
    """Occlusion: an entity behind a wall is ABSENT; the transcript is byte-identical whether that
    hidden entity is there or moved — the wallhack has nothing to read."""
    entities = {1: (4, 0, _d(1)), 2: (9, 0, _d(2))}            # 2 is behind the wall at (7,0)
    return _scene("corner", entities, frozenset({(7, 0)}), client(0, 0, 1, 0, 2, 2, 400, 0))


def _scene_margin():
    """The certified margin band: an entity beyond exact range but within the declared margin manifests
    EARLY (the peeker pre-reveal); one beyond the margin is absent — the leak is bounded, not zero."""
    entities = {1: (11, 0, _d(1)), 2: (13, 0, _d(2))}         # d²=121 (in margin), d²=169 (beyond)
    return _scene("margin", entities, frozenset(), client(0, 0, 1, 0, 2, 2, 100, 30))


def _scene_wallhack():
    """The verdict IS the defeat: a wallhack probes the transcript for a hidden enemy and finds Ø —
    absence, not a zeroed record. The scene's verdict records that the hidden probe returned nothing."""
    entities = {1: (5, 0, _d(1)), 2: (-8, 0, _d(2))}           # 2 is behind the viewpoint — hidden
    walls = frozenset()
    cl = client(0, 0, 1, 0, 2, 2, 400, 0)
    t = perceive(entities, walls, cl)
    hidden_absent = probe(t, 2) is None and probe(t, 1) is not None
    return (world_digest(entities, walls), transcript_digest(t), 1,
            "ABSENT" if hidden_absent else "LEAK")


_SCENES = {"sniper": _scene_sniper, "corner": _scene_corner,
           "margin": _scene_margin, "wallhack": _scene_wallhack}
SCENES = ("sniper", "corner", "margin", "wallhack")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    w, t, m, v = scene_case(name)
    return perception_digest(name, w, t, m, v)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_perception.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PerceptionError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------
class _LCG:
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + ((self.nxt() >> 16) % (hi - lo + 1))


SWEEP_SEED = 20260721
SWEEP_COUNT = 120


def gen_scenario(r):
    """A random world with a GUARANTEED-visible entity (id 1, dead ahead, no wall), a GUARANTEED-hidden
    entity (id 2, behind the viewpoint), an occlusion probe (id 3, ahead but behind a wall), and random
    extras — so the invariant checks have ground truth independent of `_manifest` (a leak defect cannot
    hide)."""
    cl = client(0, 0, 1, 0, 2, 2, 400, 0)
    entities = {1: (r.rng(2, 8), 0, _d(1)),                    # dead ahead, in range → visible
                2: (-r.rng(2, 9), r.rng(-3, 3), _d(2)),        # behind → hidden by ground truth
                3: (r.rng(9, 14), 0, _d(3))}                   # ahead but behind the wall below
    walls = frozenset({(7, 0)})                                # occludes id 3
    for k in range(4, 4 + r.rng(0, 3)):                        # random extras (may or may not be seen)
        entities[k] = (r.rng(-12, 12), r.rng(-12, 12), _d(k))
    return entities, walls, cl


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random worlds, each asserting witness-blindness, hidden-set
    invariance (a ground-truth-hidden entity's change leaves the transcript BYTE-IDENTICAL), non-vacuity
    (a visible entity's change alters it), constant-shape, and the citation contract. RAISES on the first
    violation OR on non-vacuity failure. Returns the aggregate dict + digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    r = _LCG(seed)
    hidden_checked = visible_seen = occluded_seen = 0
    for s in range(count):
        entities, walls, cl = gen_scenario(r)
        before = world_digest(entities, walls)
        base = perceive(entities, walls, cl)
        if world_digest(entities, walls) != before:
            raise PerceptionError(f"scenario {s}: perception mutated the witness")
        if len(base) != transcript_bytes_len():
            raise PerceptionError(f"scenario {s}: transcript length {len(base)} is not constant-shape")
        if not verify_transcript(entities, walls, cl, base):
            raise PerceptionError(f"scenario {s}: the transcript fails its own citation contract")
        # HIDDEN-SET INVARIANCE — mutate the ground-truth-hidden entity (id 2, behind): byte-identical
        moved = dict(entities); moved[2] = (entities[2][0], entities[2][1], _d(2000 + s))
        if perceive(moved, walls, cl) != base:
            raise PerceptionError(f"scenario {s} (seed {seed}): a change to a HIDDEN entity altered the "
                                  f"transcript — the wallhack can read it; witnessed absence FALSIFIED")
        hidden_checked += 1
        # NON-VACUITY — mutate the visible entity (id 1): the transcript must change
        man = _manifest(entities, walls, cl)
        if 1 in man:
            vis = dict(entities); vis[1] = (entities[1][0], entities[1][1], _d(3000 + s))
            if perceive(vis, walls, cl) == base:
                raise PerceptionError(f"scenario {s}: a change to a VISIBLE entity did not alter the "
                                      f"transcript — the sweep is vacuous")
            visible_seen += 1
        if _visible(entities, frozenset(), cl, 3) and 3 not in man:
            occluded_seen += 1                                 # id 3 would be visible but for the wall
        hh.update(f"|{s}:{transcript_digest(base)}:{len(man)}".encode())
    if hidden_checked == 0:
        raise PerceptionError("NON-VACUITY: no hidden entity was ever checked")
    if visible_seen == 0:
        raise PerceptionError("NON-VACUITY: no scenario had a visible entity")
    if occluded_seen == 0:
        raise PerceptionError("NON-VACUITY: occlusion was never exercised")
    return {"scenarios": count, "hidden_checked": hidden_checked, "visible_seen": visible_seen,
            "occluded_seen": occluded_seen, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_perception.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise PerceptionError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    """Reseed the sweep; return counterexamples (normally empty — the off-gate→pinned discipline)."""
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except PerceptionError as exc:
            found.append((seed, str(exc)))
    return found


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 300
        found = explore(base, n)
        print(f"EXPLORE: {'no counterexample' if not found else str(len(found)) + ' counterexample(s)'} "
              f"across {n} reseeded sweeps from base {base}.")
        for seed, msg in found:
            print(f"  seed={seed}: {msg}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} worlds, hidden_checked {rep['hidden_checked']}, visible_seen "
          f"{rep['visible_seen']}, occluded_seen {rep['occluded_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
