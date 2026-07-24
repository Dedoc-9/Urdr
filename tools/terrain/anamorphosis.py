# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""anamorphosis — the TUNABLE SEMANTIC FOCAL LENS over witnessed absence (URDRANA1): a server-side,
globally-deployable dial (a "simple patch to all users when needed") that generalizes the perception rung
(URDRPCP1) from a BINARY firewall (absent Ø / full-fidelity 1) to a GRADED one — WITHOUT ever opening a
slot for the hidden. Built as a COMPOSITION over `perception` with NO NEW GLYPH (kernel frozen; see
`docs/anamorphosis_brief.md` for the OODA pass, the researched prior art, and the D1 §20 glyph ruling).

THE KNIFE-EDGE. "Tunable distortion" has a dangerous reading and a sound one, and the closed-world law
(the ∅^∅ hardening) admits only the sound one. The dangerous reading — emit a DEGRADED-BUT-PRESENT record
for a marginally-visible entity ("semi-awareness gives a blurry blip") — REINTRODUCES the exact leak the
perception rung closed: a wallhack reads "an enemy is roughly there", and the client reconstruction is no
longer a closed world. So anamorphosis never distorts WHAT IS HIDDEN. It tunes two things that are already
lawful:
  * THE BOUNDARY of what manifests (a server-tunable focus/nimbus reach), and
  * THE PRECISION of records that ALREADY passed the firewall (coarse near the edge, sharp at the centre).
Below the tuned boundary an entity stays an UN-ADDRESSED ABSENCE; above it, its record may be rendered at
a distance-graded precision. The microscope angle changes the RESOLUTION OF THE LEGITIMATELY-VISIBLE, never
the PRESENCE OF THE HIDDEN.

PRIOR ART (this maps onto established work — no superiority claim). The academic twin is the Spatial Model
of Interaction's FOCUS / NIMBUS (Benford & Fahlén, CSCW 1993): awareness is a GRADED function of an
observer's focus and a target's nimbus, tuned by explicit "focal-length" parameters and by ADAPTERS that
amplify or attenuate — a server-side distortion dial, formalized in 1993. The precision channel is standard
level-of-detail / quantization replication (quantize position by distance to save bandwidth). The seam the
2025 anti-cheat survey leaves under-treated is the residual leak from reduced-precision / graded visibility;
the contribution here is doing graded visibility WITHOUT breaking the closed world.

THE LENS `L = (reach, focus)` — two integers, the whole deployable patch. `reach` widens the manifestation
boundary (a superset dial); `focus` sharpens precision everywhere (a resolution dial). Both are server-set
and CITED into the transcript header, so a client cannot claim a wider/finer lens than it was granted.

THE EXACT-INTEGER SCHEDULE (deterministic, no floats). For a manifested entity, awareness
`a = (range² + margin + reach) − d²` (≥ 0, larger = closer/more central); the grid shift is
`s = clamp(COARSEST − (a >> SCALE) − focus, 0, COARSEST)` and the record's position is floored to the 2ˢ
grid (`quantize(v, s) = (v >> s) << s`). Closer or higher-focus ⇒ smaller shift ⇒ finer; a newly-revealed
boundary entity enters at the coarsest precision and sharpens as it becomes central.

THE GATE-CHECKED LAWS (red-first — the plants bite before the goldens pin):
  * CLOSED-WORLD ACROSS THE DIAL (load-bearing): for EVERY admissible L, the reconstruction under L is
    exactly the manifested-under-L set — no addressable slot for a sub-boundary entity; a wallhack probe
    finds nothing. The `_perceive_graded_leak` plant (the "semi-awareness blip") is proven to let a
    wallhack recover a hidden entity AND to break the closed world.
  * THE MONOTONE DIAL (the anamorphic order): on the product order reach × focus, widening L only ever
    ADDS entities and REFINES precision (shift non-increasing) — never swaps. This is what makes it a
    genuine "angle" and kills the covert channel where tuning could encode data by which entities appear.
  * LOSSY-ONLY: `quantize` is a floor — the low `s` bits are zero and the exact position is unrecoverable.
    The `_perceive_covert` plant that packs the true low bits into a "coarse" record (a reversible
    distortion) is refused by the citation contract and unmasked by a decoder.
  * SERVER-ONLY CITATION: the lens is cited into the header; a client forging a wider reach or finer focus
    is refused (the record's manifested set / quantized positions won't match the true L).
  * CONSTANT-SHAPE across the whole dial: the transcript byte-length is invariant to L AND to the hidden
    set — no lens or count side-channel.
  * REDUCES TO PERCEPTION: at the identity lens (reach matching the client margin, focus saturating the
    schedule to shift 0) the manifested set equals `perception.manifest` and positions are exact —
    anamorphosis is a conservative generalization, perception is the L = ⊤ corner.

GRADE: the above are MEASURED (exact, reproducible, a defect diverges). DECLARED, honestly: this inherits
every perception-rung boundary (the margin is a real bounded leak; audio/hitbox out of scope; passive-info
cheats only; count hidden via length, not content). The precision channel adds a NEW declared boundary: a
coarse record still reveals an APPROXIMATE position of a LEGITIMATELY-VISIBLE entity (that is the point —
it is data the client is allowed to have); anamorphosis bounds the resolution, it does not encrypt it.
`does_not_show`: continuous line-of-sight (exact integer grid model); cross-placement (Python reference)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                          # the rung this composes over  # noqa: E402

MAGIC = b"URDRANA1"
DIGEST_BYTES = PC.DIGEST_BYTES                                  # 32 — reuse the perception geometry
CAPACITY = PC.CAPACITY                                          # 8 fixed slots (constant-shape)
SLOT_BYTES = PC.SLOT_BYTES                                      # 44 = eid | x | y | cite
PAD_EID = PC.PAD_EID                                            # Ø — the absence sentinel
COARSEST = 3                                                    # max grid shift (2³ = 8-cell blur at edge)
SCALE = 7                                                       # awareness >> SCALE buys one bit of sharpness
_HEADER = len(MAGIC) + 4 + 4 + 4                                # MAGIC | reach | focus | capacity
_PAD_SLOT = PAD_EID.to_bytes(4, "big") + b"\x00" * (SLOT_BYTES - 4)


class AnamorphosisError(Exception):
    def __init__(self, message):
        super().__init__(f"ANAMORPHOSIS-REFUSE: {message}")
        self.code = "ANAMORPHOSIS-REFUSE"


def lens(reach, focus):
    """THE DEPLOYABLE PATCH: a global server-side setting — `reach` widens the manifestation boundary,
    `focus` sharpens precision. Two non-negative integers; no floats (determinism)."""
    for v in (reach, focus):
        if type(v) is not int:
            raise AnamorphosisError(f"lens fields must be int, got {v!r}")
    if reach < 0 or focus < 0:
        raise AnamorphosisError("reach and focus must be non-negative")
    return (reach, focus)


# ---- the tunable boundary (focus/nimbus reach) — a witness read, never a write ----------------
def _visible_lens(entities, walls, cl, L, eid):
    px, py, dx, dy, hw, hh, r2, margin = cl
    reach, _focus = L
    ex, ey, _cite = entities[eid]
    vx, vy = ex - px, ey - py
    dot = vx * dx + vy * dy
    if dot <= 0:
        return False                                           # behind / not in front
    if vx * vx + vy * vy > r2 + margin + reach:
        return False                                           # beyond range + margin + the tuned reach
    if abs(vx * dy - vy * dx) * hw > dot * hh:
        return False                                           # outside the wedge (integer half-angle)
    if PC._occluded(walls, px, py, ex, ey):
        return False                                           # a wall stands between
    return True


def _manifest_under(entities, walls, cl, L):
    """THE RESIDENCY CHANNEL under the lens: the sorted eids this client may perceive at reach L. Exposed
    at module scope so the falsifiers can plant a leak-the-hidden defect and prove the sweep reddens."""
    return sorted(eid for eid in entities if _visible_lens(entities, walls, cl, L, eid))


def manifest_under(entities, walls, cl, L):
    return _manifest_under(entities, walls, cl, L)


# ---- the exact-integer focal schedule (precision of the already-visible) ----------------------
def awareness(entities, cl, L, eid):
    """The exact-integer awareness of a manifested entity: `(range² + margin + reach) − d²` — non-negative
    for a manifested entity, larger the closer/more central it is."""
    px, py, _dx, _dy, _hw, _hh, r2, margin = cl
    reach, _focus = L
    ex, ey, _cite = entities[eid]
    vx, vy = ex - px, ey - py
    a = (r2 + margin + reach) - (vx * vx + vy * vy)
    return a if a > 0 else 0


def shift_of(entities, cl, L, eid):
    """The grid shift for a manifested entity: coarse near the boundary, fine near the centre; monotone
    (non-increasing) as reach or focus rises. Clamped to [0, COARSEST]."""
    _reach, focus = L
    s = COARSEST - (awareness(entities, cl, L, eid) >> SCALE) - focus
    if s < 0:
        return 0
    if s > COARSEST:
        return COARSEST
    return s


def quantize(v, s):
    """LOSSY-ONLY: floor an integer coordinate to the 2ˢ grid. The low `s` bits are zeroed and the exact
    value is unrecoverable (a many-to-one map). Arithmetic shift floors negatives consistently."""
    return (v >> s) << s


# ---- the constant-shape transcript (the client's graded, closed view) -------------------------
def transcript_bytes_len():
    return _HEADER + CAPACITY * SLOT_BYTES + DIGEST_BYTES


def _slot(eid, x, y, cite_hex):
    return (eid.to_bytes(4, "big") + (x & 0xFFFFFFFF).to_bytes(4, "big")
            + (y & 0xFFFFFFFF).to_bytes(4, "big") + PC._cite_bytes(cite_hex))


def _frame(L, slots):
    reach, focus = L
    body = bytearray(MAGIC) + reach.to_bytes(4, "big") + focus.to_bytes(4, "big") + CAPACITY.to_bytes(4, "big")
    for s in slots:
        body += s
    for _ in range(CAPACITY - len(slots)):
        body += _PAD_SLOT
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def perceive_lens(entities, walls, cl, L):
    """SERVER-AUTHORITATIVE GRADED PERCEPTION: emit the client transcript under lens L — ONLY the
    manifested entities, each at a DISTANCE-GRADED precision, in a CONSTANT-SHAPE record padded to CAPACITY
    with the absence sentinel Ø. The world is never modified (witness-blind). A change confined to
    sub-boundary entities produces byte-identical output."""
    man = _manifest_under(entities, walls, cl, L)
    if len(man) > CAPACITY:
        raise AnamorphosisError(f"{len(man)} manifested entities exceed the transcript capacity {CAPACITY} "
                                f"— refuse rather than silently drop (priority policy is a declared successor)")
    slots = []
    for eid in man:
        ex, ey, cite = entities[eid]
        s = shift_of(entities, cl, L, eid)
        slots.append(_slot(eid, quantize(ex, s), quantize(ey, s), cite))
    return _frame(L, slots)


def _parse(transcript):
    if not (type(transcript) is bytes or type(transcript) is bytearray):
        raise AnamorphosisError("a transcript must be bytes")
    t = bytes(transcript)
    if len(t) != transcript_bytes_len():
        raise AnamorphosisError(f"a transcript must be exactly {transcript_bytes_len()} bytes")
    if t[:len(MAGIC)] != MAGIC:
        raise AnamorphosisError("bad magic — not a URDRANA1 transcript")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise AnamorphosisError("digest mismatch — tampered or truncated")
    reach = int.from_bytes(t[len(MAGIC):len(MAGIC) + 4], "big")
    focus = int.from_bytes(t[len(MAGIC) + 4:len(MAGIC) + 8], "big")
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
    return (reach, focus), slots


def cited_lens(transcript):
    """The lens the transcript CLAIMS (read from its hashed header) — the server-set dial, tamper-evident."""
    (reach, focus), _slots = _parse(transcript)
    return (reach, focus)


def probe(transcript, eid):
    """A WALLHACK PROBE against the client transcript: the graded (x, y, cite) if manifested, or None — an
    UN-ADDRESSED ABSENCE. A sub-boundary entity yields None; there is no byte to read."""
    _L, slots = _parse(transcript)
    for (e, x, y, cite) in slots:
        if e == eid:
            return (x, y, cite)
    return None


def reconstruct_under(transcript):
    """THE CLIENT'S CLOSED WORLD under the lens: {eid: (x, y, cite)} of ONLY the manifested entities, at
    their graded precision. Padding (Ø) is DROPPED — no addressable slot, not even null, for anything
    sub-boundary. Positions may be coarse; the SET is exactly what the lens admits."""
    _L, slots = _parse(transcript)
    return {eid: (x, y, cite) for (eid, x, y, cite) in slots}


def is_closed_world_under(entities, walls, cl, L, transcript):
    """THE CLOSED-WORLD PROPERTY across the dial: the reconstruction under L contains EXACTLY the
    manifested-under-L set — no addressable slot for any sub-boundary entity, at ANY precision. The graded
    lens changes RESOLUTION, never MEMBERSHIP."""
    return set(reconstruct_under(transcript)) == set(_manifest_under(entities, walls, cl, L))


def verify_lens(entities, walls, cl, L, transcript):
    """THE CITATION CONTRACT for the tunable lens: the transcript must CLAIM exactly the server's lens L,
    manifest exactly the lawful set, and carry each record at the LAWFUL graded precision — the quantized
    world position and the world's live citation. A forged lens (wider reach / finer focus), an injected
    sub-boundary entity, a dropped one, or a covert too-precise record returns False."""
    try:
        (reach, focus), slots = _parse(transcript)
    except AnamorphosisError:
        return False
    if (reach, focus) != tuple(L):
        return False                                           # a client claiming a lens it was not granted
    man = _manifest_under(entities, walls, cl, L)
    if sorted(e for (e, _x, _y, _c) in slots) != man:
        return False
    for (e, x, y, cite) in slots:
        ex, ey, ecite = entities[e]
        s = shift_of(entities, cl, L, e)
        if (x, y, cite) != (quantize(ex, s), quantize(ey, s), ecite):
            return False                                       # wrong precision (too fine = covert) or forged cite
    return True


def is_lossy(entities, walls, cl, L, transcript):
    """LOSSY-ONLY: every manifested record's transmitted position has its low `s` bits ZERO under the
    lawful shift — the distortion only ever discards low bits, it never smuggles them. A covert record that
    keeps the true low bits (a reversible 'blur') violates this."""
    try:
        _L, slots = _parse(transcript)
    except AnamorphosisError:
        return False
    for (e, x, y, _cite) in slots:
        if e not in entities:
            return False
        s = shift_of(entities, cl, L, e)
        mask = (1 << s) - 1
        if (x & mask) != 0 or (y & mask) != 0:
            return False
    return True


# ---- falsifier tools (NOT laws) ---------------------------------------------------------------
def _perceive_graded_leak(entities, walls, cl, L, near2):
    """THE DANGEROUS MISTAKE: 'semi-awareness gives a blurry blip'. Emit a HEAVILY-COARSE record for
    sub-boundary entities that are merely NEAR (within `near2`), leaking their approximate position. The
    closed-world property must catch that the client can now address a hidden entity."""
    px, py = cl[0], cl[1]
    man = set(_manifest_under(entities, walls, cl, L))
    slots = []
    for eid in sorted(entities):
        ex, ey, cite = entities[eid]
        if eid in man:
            s = shift_of(entities, cl, L, eid)
            slots.append(_slot(eid, quantize(ex, s), quantize(ey, s), cite))
        else:
            d2 = (ex - px) ** 2 + (ey - py) ** 2
            if d2 <= near2:                                    # a "radar blip" for a nearby hidden entity
                slots.append(_slot(eid, quantize(ex, COARSEST), quantize(ey, COARSEST), cite))
    slots = slots[:CAPACITY]
    return _frame(L, slots)


def _perceive_covert(entities, walls, cl, L):
    """THE LOSSY-ONLY VIOLATION: emit records at the LAWFUL shift but keep the EXACT low bits (a reversible
    'blur') — the record looks coarse but a decoder recovers the exact position. `verify_lens` refuses it
    (too precise) and `is_lossy` unmasks it."""
    man = _manifest_under(entities, walls, cl, L)
    slots = []
    for eid in man:
        ex, ey, cite = entities[eid]
        slots.append(_slot(eid, ex, ey, cite))                 # exact position, but claimed at a coarse shift
    return _frame(L, slots)


def _shift_nonmonotone(entities, cl, L, eid):
    """A falsifier schedule (NOT a law): INVERTED — fine at the edge, coarse at the centre. Breaks the
    anamorphic monotone-dial order, which the monotonicity check must catch."""
    return COARSEST - shift_of(entities, cl, L, eid)


# ---- digests ----------------------------------------------------------------------------------
def transcript_digest(transcript):
    return hashlib.sha256(MAGIC + bytes(transcript)).hexdigest()


def anamorphosis_digest(name, world_hex, lens_t, transcript_hex, manifested, verdict):
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{world_hex}|L:{lens_t[0]}:{lens_t[1]}|t:{transcript_hex}"
              f"|m:{manifested}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------------
def _d(i):
    return PC._d(i)


def _scene(name, entities, walls, cl, L, verdict):
    t = perceive_lens(entities, walls, cl, L)
    man = _manifest_under(entities, walls, cl, L)
    return anamorphosis_digest(name, PC.world_digest(entities, walls), L, transcript_digest(t), len(man), verdict)


def _scene_focal():
    """The focal lens: a close entity is SHARP (shift 0, exact) and a far manifested entity is COARSE
    (shift > 0) under the same lens — the microscope's depth of field."""
    entities = {1: (3, 0, _d(1)), 2: (18, 1, _d(2))}           # close vs far, both manifested
    cl = PC.client(0, 0, 1, 0, 4, 1, 400, 0)
    L = lens(0, 0)
    t = perceive_lens(entities, {}, cl, L)
    near_sharp = shift_of(entities, cl, L, 1) == 0
    far_coarse = shift_of(entities, cl, L, 2) > 0
    return _scene("focal", entities, frozenset(), cl, L,
                  "GRADED" if (near_sharp and far_coarse) else "FLAT")


def _scene_widen():
    """The boundary dial: an entity beyond the base range is ABSENT at reach 0 and MANIFESTS (coarse) once
    the server widens reach — a superset, entering at the coarsest precision."""
    entities = {1: (5, 0, _d(1)), 2: (21, 0, _d(2))}           # 2 at d²=441 > range² 400
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    absent0 = 2 not in _manifest_under(entities, {}, cl, lens(0, 0))
    present1 = 2 in _manifest_under(entities, {}, cl, lens(80, 0))
    return _scene("widen", entities, frozenset(), cl, lens(80, 0),
                  "SUPERSET" if (absent0 and present1) else "BROKEN")


def _scene_defended():
    """The leak stays defended under the lens: a hidden entity behind the viewpoint is ABSENT (not a blurry
    blip); a wallhack probe finds Ø; the reconstruction is a closed world."""
    entities = {1: (5, 0, _d(1)), 2: (-9, 0, _d(2))}           # 2 behind — hidden
    cl = PC.client(0, 0, 1, 0, 2, 2, 400, 0)
    L = lens(50, 1)
    t = perceive_lens(entities, {}, cl, L)
    closed = probe(t, 2) is None and is_closed_world_under(entities, {}, cl, L, t)
    return _scene("defended", entities, frozenset(), cl, L, "CLOSED" if closed else "LEAK")


def _scene_reduce():
    """Reduces to perception: at the identity lens (reach = margin already folded in, focus saturating the
    schedule) the manifested set equals perception's and positions are EXACT — perception is L = ⊤."""
    entities = {1: (5, 0, _d(1)), 2: (3, 2, _d(2)), 3: (-4, 0, _d(3))}
    cl = PC.client(0, 0, 1, 0, 2, 2, 400, 0)
    L = lens(0, COARSEST)                                       # focus saturates → every shift 0 → exact
    t = perceive_lens(entities, {}, cl, L)
    same_set = _manifest_under(entities, {}, cl, L) == PC._manifest(entities, frozenset(), cl)
    exact = all(shift_of(entities, cl, L, e) == 0 for e in _manifest_under(entities, {}, cl, L))
    return _scene("reduce", entities, frozenset(), cl, L, "MATCH" if (same_set and exact) else "DIVERGE")


_SCENES = {"focal": _scene_focal, "widen": _scene_widen,
           "defended": _scene_defended, "reduce": _scene_reduce}
SCENES = ("focal", "widen", "defended", "reduce")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_anamorphosis.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AnamorphosisError(f"no golden named {name!r}")


# ---- the seeded property sweep (worlds × lens settings) ---------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 120
_LENSES = (lens(0, 0), lens(40, 0), lens(40, 1), lens(120, 0))  # a dial slice (product order reach × focus)


def gen_scenario(r):
    """A random world with a GUARANTEED-visible near entity (id 1), a GUARANTEED-hidden entity (id 2,
    behind), a boundary entity (id 3, just beyond base range — absent at reach 0, present when widened),
    and random extras — ground truth independent of `_manifest_under`."""
    cl = PC.client(0, 0, 1, 0, 3, 2, 400, 0)
    entities = {1: (r.rng(2, 6), 0, _d(1)),                    # close, dead ahead → visible & sharp
                2: (-r.rng(2, 9), r.rng(-3, 3), _d(2)),        # behind → hidden by ground truth
                3: (r.rng(21, 26), 0, _d(3))}                  # d² > 400 → absent at reach 0
    for k in range(4, 4 + r.rng(0, 3)):
        entities[k] = (r.rng(-14, 14), r.rng(-14, 14), _d(k))
    return entities, cl


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep over worlds × lens settings, asserting: witness-blindness; CLOSED-WORLD
    under every lens; CONSTANT-SHAPE across the dial; the citation contract and LOSSY-ONLY; hidden-set
    invariance (a change to a ground-truth-hidden entity leaves the transcript byte-identical under every
    lens); and the MONOTONE DIAL (widening L adds entities & refines precision, never swaps). Non-vacuous:
    coarse & fine records and boundary crossings are all exercised. RAISES on the first violation."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    r = PC._LCG(seed)
    hidden_checked = coarse_seen = fine_seen = crossed_seen = mono_pairs = 0
    for s in range(count):
        entities, cl = gen_scenario(r)
        walls = frozenset()
        for L in _LENSES:
            before = PC.world_digest(entities, walls)
            base = perceive_lens(entities, walls, cl, L)
            if PC.world_digest(entities, walls) != before:
                raise AnamorphosisError(f"scenario {s} lens {L}: perception mutated the witness")
            if len(base) != transcript_bytes_len():
                raise AnamorphosisError(f"scenario {s} lens {L}: transcript is not constant-shape")
            if not verify_lens(entities, walls, cl, L, base):
                raise AnamorphosisError(f"scenario {s} lens {L}: the transcript fails its citation contract")
            if not is_lossy(entities, walls, cl, L, base):
                raise AnamorphosisError(f"scenario {s} lens {L}: a record kept low bits — not lossy-only")
            if not is_closed_world_under(entities, walls, cl, L, base):
                raise AnamorphosisError(f"scenario {s} lens {L}: the reconstruction is not a closed world "
                                        f"— a hidden entity is addressable")
            moved = dict(entities); moved[2] = (entities[2][0], entities[2][1], _d(5000 + s))
            if perceive_lens(moved, walls, cl, L) != base:
                raise AnamorphosisError(f"scenario {s} lens {L}: a change to a HIDDEN entity altered the "
                                        f"transcript — witnessed absence FALSIFIED under the lens")
            for e in _manifest_under(entities, walls, cl, L):
                sh = shift_of(entities, cl, L, e)
                if sh > 0:
                    coarse_seen += 1
                else:
                    fine_seen += 1
            hh.update(f"|{s}:{L[0]}:{L[1]}:{transcript_digest(base)}".encode())
        hidden_checked += 1
        # THE MONOTONE DIAL: reach 0 → 120 and focus 0 → 1 both only add entities and refine precision
        for (La, Lb) in ((lens(0, 0), lens(120, 0)), (lens(40, 0), lens(40, 1))):
            ma = set(_manifest_under(entities, walls, cl, La))
            mb = set(_manifest_under(entities, walls, cl, Lb))
            if not ma.issubset(mb):
                raise AnamorphosisError(f"scenario {s}: widening the lens {La}->{Lb} DROPPED an entity — "
                                        f"the dial is not monotone")
            for e in ma:
                if shift_of(entities, cl, Lb, e) > shift_of(entities, cl, La, e):
                    raise AnamorphosisError(f"scenario {s}: widening the lens {La}->{Lb} COARSENED entity "
                                            f"{e} — the dial is not monotone")
            if mb - ma:
                crossed_seen += 1                              # id 3 crosses in when reach widens
            mono_pairs += 1
    if hidden_checked == 0 or coarse_seen == 0 or fine_seen == 0 or crossed_seen == 0 or mono_pairs == 0:
        raise AnamorphosisError(f"NON-VACUITY: hidden {hidden_checked}, coarse {coarse_seen}, fine "
                                f"{fine_seen}, crossed {crossed_seen}, mono_pairs {mono_pairs}")
    return {"scenarios": count, "hidden_checked": hidden_checked, "coarse_seen": coarse_seen,
            "fine_seen": fine_seen, "crossed_seen": crossed_seen, "mono_pairs": mono_pairs,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_anamorphosis.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise AnamorphosisError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except AnamorphosisError as exc:
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
    print(f"SWEEP: {rep['scenarios']} worlds × {len(_LENSES)} lenses, coarse {rep['coarse_seen']}, fine "
          f"{rep['fine_seen']}, crossed {rep['crossed_seen']}, mono_pairs {rep['mono_pairs']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
