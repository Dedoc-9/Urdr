# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""audible — AUDIBLE ABSENCE, the audio channel of the anti-cheat firewall (URDRAUD1): witnessed absence
(URDRPCP1) applied to POSITIONAL AUDIO. The perception rung declared audio explicitly out of scope; this
closes it. A publicly-known open problem — footstep / positional-sound leaks in competitive shooters
(VALORANT and CS2 both have ongoing controversies) — is that engines send audio data for sounds a client
should not be able to hear, leaking enemy position at low volume. WITNESSED ABSENCE answers it: a sound
BELOW the audibility threshold (too quiet, too far, or wall-occluded) is an UN-ADDRESSED ABSENCE — an
audio-ESP replayed against the client transcript finds NOTHING, so there is no sub-threshold position leak.
Composition over `perception`, NO NEW GLYPH — the kernel stays frozen. See `docs/audible_brief.md` for the
design pass and the D1 §20 glyph ruling.

THE THESIS. The D15 presentation firewall (`view_witness`) applied to the AUDIO RESIDENCY channel. THE
WITNESS is the authoritative world of sound EVENTS (each at an integer position, with an integer source
loudness and its authority citation), exact and untouched. THE RESIDENCY CHANNEL is a per-listener AUDIBLE
set — which sounds this listener may hear — cited to the witness but walled from it. An inaudible sound is
not a zeroed record with a volume flag; it is an un-addressed absence.

WHAT THE LISTENER LEGITIMATELY GETS (bounded localization, not the source position). For each AUDIBLE sound
the transcript carries a BUCKETED direction (one of 8 integer sectors — ~45°, exact, no atan2/float) and a
QUANTIZED heard loudness — the spatial cue a player is allowed to have — but NEVER the exact source
coordinates. Together they bound the source to an annular sector, not a point; the resolution is a declared,
bounded leak, exactly as the anamorphosis rung bounds visual precision.

THE EXACT-INTEGER AUDIBILITY (deterministic, no floats). A sound of loudness L at squared distance d² across
`w` wall cells is AUDIBLE to a listener iff `L >= MIN_LOUDNESS` and `d² <= L*RANGE_PER_LOUDNESS −
WALL_PENALTY*w` (louder carries further; walls attenuate; sound is OMNIDIRECTIONAL — no wedge, unlike
vision). Everything else is absent.

GRADE. Witness-blindness, hidden-set invariance (a change confined to inaudible sounds yields a
BYTE-IDENTICAL transcript), the constant-shape transcript, the AUDIO-WALLHACK-PROBE-FINDS-NOTHING property,
the certified audibility band, the citation contract, and the closed-world reconstruction are MEASURED.
DECLARED, honestly: the AUDIBLE localization (sector + loudness) is a real, bounded, DECLARED leak — a player
who can legitimately hear an enemy can roughly place them (that is spatial audio, fair play); the rung bounds
it, it does not eliminate it. This governs the POSITIONAL-AUDIO channel only; occlusion is a simple integer
wall-attenuation model, not acoustic propagation (reverb, diffraction). `does_not_show`: continuous acoustics
(exact integer grid); the visual/hitbox channels (their own rungs); cross-placement (URDRAUD1 Python
reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                          # reuse the exact-integer occlusion machinery  # noqa: E402

MAGIC = b"URDRAUD1"
DIGEST_BYTES = PC.DIGEST_BYTES
CAPACITY = PC.CAPACITY                                          # fixed transcript slots (constant-shape)
SLOT_BYTES = 4 + 4 + 4 + DIGEST_BYTES                           # eid | direction | heard_loudness | cite = 44
PAD_EID = PC.PAD_EID
_HEADER = len(MAGIC) + 4
_PAD_SLOT = PAD_EID.to_bytes(4, "big") + b"\x00" * (SLOT_BYTES - 4)

MIN_LOUDNESS = 1                                                # a sound quieter than this is never audible
RANGE_PER_LOUDNESS = 25                                         # squared-range each unit of loudness carries
WALL_PENALTY = 200                                             # squared-range a wall cell steals
LOUD_QUANT = 50                                                # the quantum of heard loudness (bounded cue)
HERE_SECTOR = 8                                                # co-located (d = 0) — the ninth "sector"


class AudibleError(Exception):
    def __init__(self, message):
        super().__init__(f"AUDIBLE-REFUSE: {message}")
        self.code = "AUDIBLE-REFUSE"


def listener(lx, ly):
    """A listener position (omnidirectional hearing — no facing)."""
    for v in (lx, ly):
        if type(v) is not int:
            raise AudibleError(f"listener fields must be int, got {v!r}")
    return (lx, ly)


# ---- the exact-integer audio AoI (the witness read, never written) ----------------------------
def _sector(dx, dy):
    """One of 8 integer compass sectors (exact, no atan2/float): a bounded directional cue. d = 0 → the
    co-located sector 8."""
    if dx == 0 and dy == 0:
        return HERE_SECTOR
    if dx >= 0 and dy >= 0:
        return 0 if abs(dx) >= abs(dy) else 1                  # E-ish / N-ish
    if dx < 0 and dy >= 0:
        return 2 if abs(dy) >= abs(dx) else 3                  # N-ish / W-ish
    if dx < 0 and dy < 0:
        return 4 if abs(dx) >= abs(dy) else 5                  # W-ish / S-ish
    return 6 if abs(dy) >= abs(dx) else 7                      # S-ish / E-ish


def _walls_crossed(walls, x0, y0, x1, y1):
    if not walls:
        return 0
    cells = PC._supercover(x0, y0, x1, y1)
    cells.discard((x0, y0)); cells.discard((x1, y1))
    return sum(1 for c in cells if c in walls)


def _reach2(loudness, walls, lx, ly, sx, sy):
    """The squared audible reach of a sound at (sx,sy): louder carries further, each wall cell steals
    WALL_PENALTY of squared range."""
    return loudness * RANGE_PER_LOUDNESS - WALL_PENALTY * _walls_crossed(walls, lx, ly, sx, sy)


def _audible(sounds, walls, lis, eid):
    lx, ly = lis
    sx, sy, loudness, _cite = sounds[eid]
    if loudness < MIN_LOUDNESS:
        return False
    d2 = (sx - lx) ** 2 + (sy - ly) ** 2
    return d2 <= _reach2(loudness, walls, lx, ly, sx, sy)


def _heard_loudness(sounds, walls, lis, eid):
    """The quantized loudness the listener hears — the margin of audibility, floored to LOUD_QUANT: a
    bounded cue, never the exact source loudness or position."""
    lx, ly = lis
    sx, sy, loudness, _cite = sounds[eid]
    d2 = (sx - lx) ** 2 + (sy - ly) ** 2
    margin = _reach2(loudness, walls, lx, ly, sx, sy) - d2     # >= 0 for an audible sound
    return (margin // LOUD_QUANT) * LOUD_QUANT


def _direction(sounds, lis, eid):
    lx, ly = lis
    sx, sy, _l, _c = sounds[eid]
    return _sector(sx - lx, sy - ly)


def _manifest(sounds, walls, lis):
    """THE AUDIO RESIDENCY CHANNEL: the sorted eids this listener may hear. Module scope so a leak plant can
    be planted and the sweep proven to redden."""
    return sorted(eid for eid in sounds if _audible(sounds, walls, lis, eid))


def manifest(sounds, walls, lis):
    return _manifest(sounds, walls, lis)


# ---- the constant-shape transcript (the listener's view — inaudible is un-addressed) ----------
def transcript_bytes_len():
    return _HEADER + CAPACITY * SLOT_BYTES + DIGEST_BYTES


def _slot(eid, direction, loud, cite_hex):
    return (eid.to_bytes(4, "big") + (direction & 0xFFFFFFFF).to_bytes(4, "big")
            + (loud & 0xFFFFFFFF).to_bytes(4, "big") + PC._cite_bytes(cite_hex))


def perceive(sounds, walls, lis):
    """SERVER-AUTHORITATIVE HEARING: emit the listener transcript — ONLY the audible sounds, each as
    (direction sector, quantized heard loudness, citation), in a CONSTANT-SHAPE record padded to CAPACITY
    with Ø. Witness-blind (never mutates the world); a change confined to inaudible sounds is byte-identical."""
    man = _manifest(sounds, walls, lis)
    if len(man) > CAPACITY:
        raise AudibleError(f"{len(man)} audible sounds exceed the transcript capacity {CAPACITY} — refuse "
                           f"rather than silently drop (priority policy is a declared successor)")
    body = bytearray(MAGIC) + CAPACITY.to_bytes(4, "big")
    for eid in man:
        cite = sounds[eid][3]
        body += _slot(eid, _direction(sounds, lis, eid), _heard_loudness(sounds, walls, lis, eid), cite)
    for _ in range(CAPACITY - len(man)):
        body += _PAD_SLOT
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(transcript):
    if not (type(transcript) is bytes or type(transcript) is bytearray):
        raise AudibleError("a transcript must be bytes")
    t = bytes(transcript)
    if len(t) != transcript_bytes_len():
        raise AudibleError(f"a transcript must be exactly {transcript_bytes_len()} bytes")
    if t[:len(MAGIC)] != MAGIC:
        raise AudibleError("bad magic — not a URDRAUD1 transcript")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise AudibleError("digest mismatch — tampered or truncated")
    off = _HEADER
    slots = []
    for _ in range(CAPACITY):
        raw = t[off:off + SLOT_BYTES]; off += SLOT_BYTES
        eid = int.from_bytes(raw[:4], "big")
        if eid == PAD_EID:
            continue
        direction = int.from_bytes(raw[4:8], "big")
        loud = int.from_bytes(raw[8:12], "big")
        slots.append((eid, direction, loud, raw[12:].hex()))
    return slots


def probe(transcript, eid):
    """AN AUDIO-ESP PROBE against the transcript: (direction, loudness, cite) if the sound is audible, or
    None — an UN-ADDRESSED ABSENCE. An inaudible sound yields None; there is no byte to read."""
    for (e, d, loud, cite) in _parse(transcript):
        if e == eid:
            return (d, loud, cite)
    return None


def verify_transcript(sounds, walls, lis, transcript):
    """THE CITATION CONTRACT: every slot cites the authority and carries the lawful bucketed direction and
    quantized loudness for exactly the audible set. A forged citation, an injected inaudible sound, or a
    dropped audible one returns False."""
    try:
        slots = _parse(transcript)
    except AudibleError:
        return False
    man = _manifest(sounds, walls, lis)
    if sorted(e for (e, _d, _l, _c) in slots) != man:
        return False
    for (e, d, loud, cite) in slots:
        if (d, loud, cite) != (_direction(sounds, lis, e), _heard_loudness(sounds, walls, lis, e),
                               sounds[e][3]):
            return False
    return True


def reconstruct(transcript):
    """THE LISTENER'S CLOSED WORLD (∅^∅): {eid: (direction, loudness, cite)} of ONLY the audible sounds — no
    addressable slot, not even null, for anything inaudible."""
    return {eid: (d, loud, cite) for (eid, d, loud, cite) in _parse(transcript)}


def is_closed_world(sounds, walls, lis, transcript):
    return set(reconstruct(transcript)) == set(_manifest(sounds, walls, lis))


def forge_citation(transcript, eid):
    t = bytearray(transcript[:-DIGEST_BYTES])
    off = _HEADER
    for _ in range(CAPACITY):
        e = int.from_bytes(t[off:off + 4], "big")
        if e == eid:
            t[off + 12] ^= 0x01
            break
        off += SLOT_BYTES
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


def _perceive_leak(sounds, walls, lis, near2):
    """THE FOOTSTEP-LEAK MISTAKE (a falsifier tool, NOT a law): send a record for INAUDIBLE sounds that are
    merely NEAR (within `near2`), at a quantized-to-zero loudness — the "you can barely hear it" data real
    engines leak. The closed-world / hidden-set-invariance laws must catch that an audio-ESP can now read a
    sub-threshold enemy's direction."""
    lx, ly = lis
    man = set(_manifest(sounds, walls, lis))
    body = bytearray(MAGIC) + CAPACITY.to_bytes(4, "big")
    slots = []
    for eid in sorted(sounds):
        sx, sy, _l, cite = sounds[eid]
        if eid in man:
            slots.append(_slot(eid, _direction(sounds, lis, eid),
                               _heard_loudness(sounds, walls, lis, eid), cite))
        elif (sx - lx) ** 2 + (sy - ly) ** 2 <= near2:         # a sub-threshold "whisper" — the leak
            slots.append(_slot(eid, _direction(sounds, lis, eid), 0, cite))
    slots = slots[:CAPACITY]
    for s in slots:
        body += s
    for _ in range(CAPACITY - len(slots)):
        body += _PAD_SLOT
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


# ---- digests -----------------------------------------------------------------------------------
def world_digest(sounds, walls):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for eid in sorted(sounds):
        sx, sy, loud, cite = sounds[eid]
        hh.update(f"|s{eid}:{sx}:{sy}:{loud}:{cite}".encode())
    for (wx, wy) in sorted(walls):
        hh.update(f"|w{wx}:{wy}".encode())
    return hh.hexdigest()


def transcript_digest(transcript):
    return hashlib.sha256(MAGIC + bytes(transcript)).hexdigest()


def audible_digest(name, world_hex, transcript_hex, manifested, verdict):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|w:{world_hex}|t:{transcript_hex}|m:{manifested}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------------
def _d(i):
    return PC._d(i)


def _scene(name, sounds, walls, lis, verdict):
    t = perceive(sounds, walls, lis)
    man = _manifest(sounds, walls, lis)
    return audible_digest(name, world_digest(sounds, walls), transcript_digest(t), len(man), verdict)


def _scene_near():
    """A loud sound nearby is audible with a direction; a quiet sound far away is inaudible (un-addressed)."""
    sounds = {1: (3, 0, 20, _d(1)), 2: (40, 0, 2, _d(2))}      # near loud / far quiet
    lis = listener(0, 0)
    aud = 1 in _manifest(sounds, frozenset(), lis) and 2 not in _manifest(sounds, frozenset(), lis)
    return _scene("near", sounds, frozenset(), lis, "HEARD" if aud else "SILENT")


def _scene_wall():
    """A wall between listener and source attenuates: a sound audible in the open becomes inaudible behind a
    wall — and the transcript is byte-identical whether the muffled sound is there or moved."""
    sounds = {1: (9, 0, 20, _d(1))}                            # loudness 20 → reach 500; d²=81
    lis = listener(0, 0)
    open_aud = 1 in _manifest(sounds, frozenset(), lis)
    walled = 1 in _manifest(sounds, frozenset({(5, 0), (6, 0), (7, 0)}), lis)   # 3 walls → -600 reach
    return _scene("wall", sounds, frozenset({(5, 0), (6, 0), (7, 0)}), lis,
                  "MUFFLED" if (open_aud and not walled) else "THROUGH")


def _scene_direction():
    """Bounded localization: four equally-loud sounds around the listener resolve to distinct sectors, but
    none reveals an exact position."""
    sounds = {1: (5, 0, 20, _d(1)), 2: (0, 5, 20, _d(2)), 3: (-5, 0, 20, _d(3)), 4: (0, -5, 20, _d(4))}
    lis = listener(0, 0)
    dirs = {_direction(sounds, lis, e) for e in _manifest(sounds, frozenset(), lis)}
    return _scene("direction", sounds, frozenset(), lis, "LOCALIZED" if len(dirs) == 4 else "BLURRED")


def _scene_esp():
    """The verdict IS the defeat: an audio-ESP probes for a sub-threshold enemy's footstep and finds Ø."""
    sounds = {1: (2, 0, 20, _d(1)), 2: (30, 0, 3, _d(2))}      # 2 is a distant quiet footstep → inaudible
    lis = listener(0, 0)
    t = perceive(sounds, frozenset(), lis)
    defended = probe(t, 2) is None and probe(t, 1) is not None
    return _scene("esp", sounds, frozenset(), lis, "ABSENT" if defended else "LEAK")


_SCENES = {"near": _scene_near, "wall": _scene_wall, "direction": _scene_direction, "esp": _scene_esp}
SCENES = ("near", "wall", "direction", "esp")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_audible.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AudibleError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 120


def gen_scenario(r):
    """A random soundscape with a GUARANTEED-audible sound (id 1, near & loud), a GUARANTEED-inaudible one
    (id 2, far & quiet), a wall-muffled probe (id 3, loud but behind a wall), and random extras."""
    lis = listener(0, 0)
    sounds = {1: (r.rng(1, 4), r.rng(-1, 1), r.rng(15, 25), _d(1)),          # near & loud → audible
              2: (r.rng(30, 45), r.rng(-5, 5), r.rng(1, 3), _d(2)),          # far & quiet → inaudible
              3: (r.rng(9, 12), 0, 20, _d(3))}                               # loud but behind the wall below
    walls = frozenset({(6, 0), (7, 0), (8, 0)})                              # muffles id 3
    for k in range(4, 4 + r.rng(0, 3)):
        sounds[k] = (r.rng(-30, 30), r.rng(-30, 30), r.rng(1, 25), _d(k))
    return sounds, walls, lis


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random soundscapes asserting witness-blindness, hidden-set
    invariance (a ground-truth-inaudible sound's change leaves the transcript BYTE-IDENTICAL — the audio-ESP
    has nothing to read), the closed-world reconstruction, constant-shape, and the citation contract. RAISES
    on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    inaudible_checked = audible_seen = muffled_seen = closed_checked = 0
    for s in range(count):
        sounds, walls, lis = gen_scenario(r)
        before = world_digest(sounds, walls)
        base = perceive(sounds, walls, lis)
        if world_digest(sounds, walls) != before:
            raise AudibleError(f"scenario {s}: hearing mutated the witness")
        if len(base) != transcript_bytes_len():
            raise AudibleError(f"scenario {s}: transcript is not constant-shape")
        if not verify_transcript(sounds, walls, lis, base):
            raise AudibleError(f"scenario {s}: the transcript fails its citation contract")
        if not is_closed_world(sounds, walls, lis, base):
            raise AudibleError(f"scenario {s}: the listener reconstruction is not a closed world")
        closed_checked += 1
        # HIDDEN-SET INVARIANCE: move the ground-truth-inaudible sound (id 2, far & quiet) → byte-identical
        moved = dict(sounds); moved[2] = (sounds[2][0] + 1, sounds[2][1], sounds[2][2], _d(2000 + s))
        if perceive(moved, walls, lis) != base:
            raise AudibleError(f"scenario {s} (seed {seed}): a change to an INAUDIBLE sound altered the "
                               f"transcript — the audio-ESP can read it; audible absence FALSIFIED")
        inaudible_checked += 1
        man = _manifest(sounds, walls, lis)
        if 1 in man:
            audible_seen += 1
        if _audible(sounds, frozenset(), lis, 3) and 3 not in man:
            muffled_seen += 1                                  # id 3 would be audible but for the wall
        hh.update(f"|{s}:{transcript_digest(base)}:{len(man)}".encode())
    if inaudible_checked == 0 or audible_seen == 0 or muffled_seen == 0:
        raise AudibleError(f"NON-VACUITY: inaudible {inaudible_checked}, audible {audible_seen}, muffled "
                           f"{muffled_seen}")
    return {"scenarios": count, "inaudible_checked": inaudible_checked, "audible_seen": audible_seen,
            "muffled_seen": muffled_seen, "closed_checked": closed_checked, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_audible.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise AudibleError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except AudibleError as exc:
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
    print(f"SWEEP: {rep['scenarios']} soundscapes, inaudible_checked {rep['inaudible_checked']}, "
          f"audible_seen {rep['audible_seen']}, muffled_seen {rep['muffled_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
