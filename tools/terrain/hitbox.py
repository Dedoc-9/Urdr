# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""hitbox — SERVER-AUTHORITATIVE HIT VALIDATION, the ACTIVE channel of the anti-cheat firewall (URDRHIT1):
the third channel after witnessed absence (URDRPCP1, vision) and audible absence (URDRAUD1, audio). Those two
govern what a client may RECEIVE; this one governs what a client may CLAIM. It is the aimbot / wall-shoot
defense: a claimed hit is ADJUDICATED against the AUTHORITATIVE world, so a shot through a wall, a phantom hit
off the real hitbox, an inflated-hitbox claim, an off-ray claim, or an out-of-range claim is REFUSED. The
client cannot manufacture an ADMIT it did not earn — an unearned hit is un-addressed. Composition over
`perception` (its exact-integer occlusion machinery), NO NEW GLYPH — the kernel stays frozen. See
`docs/hitbox_brief.md` for the design pass and the D1 §20 glyph ruling.

THE THESIS. The residency channels answer "never transmit data for what a client should not perceive." The
hit channel answers the dual fault: "never accept an authority claim the world does not support." THE WITNESS
is the authoritative world — targets at integer positions, each carrying the SERVER's hitbox half-extents
(the AABB is the server's, never the client's) and an authority citation, plus the wall set. A CLAIM is a
client assertion "(target, point)": I hit this target at this point. The server re-derives admission from ITS
OWN geometry and emits a PROOF-CARRYING VERDICT; the claim carries no geometry the server trusts.

THE EXACT-INTEGER ADMISSION (deterministic, no floats). A claim (eid, hx, hy) by a shooter at (px,py) aiming
integer (ax,ay) with squared reach `max_range2`, against walls `W`, ADMITS iff ALL hold — in a fixed reason
priority so the verdict is a pure function of the world:
  * ON THE AUTHORITATIVE BOX — `ex-hbx <= hx <= ex+hbx` and `ey-hby <= hy <= ey+hby`, using the SERVER's
    (hbx,hby). A client-claimed extent is never read (the inflated-hitbox cheat gains nothing).
  * ON THE FORWARD AIM RAY — colinear `(hx-px)*ay == (hy-py)*ax` AND forward `(hx-px)*ax + (hy-py)*ay > 0`
    (an exact integer half-line — no atan2/float). An aimbot cannot claim a hit off the line it is aiming.
  * WITHIN RANGE — `(hx-px)² + (hy-py)² <= max_range2`.
  * LINE OF FIRE CLEAR — the integer supercover of shooter→point crosses no wall cell (reuse
    `perception._occluded`). A wall-shot is refused.

GRADE. Server-authority (the verdict is a pure function of the authoritative world + claim, never of any
client-supplied extent), determinism (byte-identical verdicts), the five refusals (phantom / off-ray /
out-of-range / wall-shot / inflated-hitbox — each PLANTED and proven to bite), the clean admit (non-vacuity),
the constant-shape verdict, and the PROOF-CARRYING contract (a self-consistent forged ADMIT still fails
`verify_verdict`, because a fresh authoritative adjudication disagrees) are MEASURED. DECLARED, honestly: this
is INSTANTANEOUS validation against the CURRENT authoritative snapshot — TEMPORAL LAG-COMPENSATION (rewinding
target positions to the shooter's view-time) is the DECLARED SUCCESSOR, not solved here; without it a
legitimately-aimed shot at a moving target can be wrongly refused. It governs the HIT-CLAIM channel only. It
does NOT touch aim ASSISTANCE on a legitimately-hittable target — if you are genuinely aimed at a visible,
in-range, unoccluded target, the geometric hit is lawful and the rung admits it; it cannot distinguish a
human's lawful aim from an aimbot's lawful aim (the honest aimbot boundary, shared with URDRPCP1).
`does_not_show`: continuous geometry / sub-cell precision (this is an exact integer grid); real ballistics
(penetration, drop, ricochet); lag-compensation (the successor); cross-placement (URDRHIT1 Python reference
only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                            # reuse the exact-integer occlusion machinery  # noqa: E402

MAGIC = b"URDRHIT1"
DIGEST_BYTES = PC.DIGEST_BYTES

# reason codes (fixed priority — the verdict is a pure function of the world)
R_ADMIT = 0
R_OFFBOX = 1
R_OFFRAY = 2
R_RANGE = 3
R_WALL = 4
R_NOTARGET = 5
_REASON_NAME = {R_ADMIT: "ADMIT", R_OFFBOX: "OFFBOX", R_OFFRAY: "OFFRAY",
                R_RANGE: "RANGE", R_WALL: "WALL", R_NOTARGET: "NOTARGET"}

VERDICT_ADMIT = 1
VERDICT_REFUSE = 0

# MAGIC(8) | eid(4) | hx(4) | hy(4) | vcode(4) | reason(4) | cite(32) | sha256(32) = 92
_HEADER = len(MAGIC)
VERDICT_BYTES = _HEADER + 4 * 5 + DIGEST_BYTES + DIGEST_BYTES
_ZERO_CITE = "00" * DIGEST_BYTES


class HitboxError(Exception):
    def __init__(self, message):
        super().__init__(f"HITBOX-REFUSE: {message}")
        self.code = "HITBOX-REFUSE"


def shooter(px, py, ax, ay, max_range2):
    """A shooter: position (px,py), integer aim direction (ax,ay), squared max reach."""
    for v in (px, py, ax, ay, max_range2):
        if type(v) is not int:
            raise HitboxError(f"shooter fields must be int, got {v!r}")
    if (ax, ay) == (0, 0):
        raise HitboxError("a shooter needs an aim direction")
    if max_range2 < 0:
        raise HitboxError("max_range2 must be non-negative")
    return (px, py, ax, ay, max_range2)


def target(ex, ey, hbx, hby, cite):
    """An authoritative target: position (ex,ey), AABB half-extents (hbx,hby), authority citation."""
    for v in (ex, ey, hbx, hby):
        if type(v) is not int:
            raise HitboxError(f"target fields must be int, got {v!r}")
    if hbx < 0 or hby < 0:
        raise HitboxError("hitbox half-extents must be non-negative")
    PC._cite_bytes(cite)                                          # validate the citation shape
    return (ex, ey, hbx, hby, cite)


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "big")


# ---- the exact-integer admission predicates (the witness read, never written) -----------------
def _on_box(hx, hy, ex, ey, hbx, hby):
    """The claimed point lies on the AUTHORITATIVE integer AABB (the server's extent, not the client's)."""
    return (ex - hbx <= hx <= ex + hbx) and (ey - hby <= hy <= ey + hby)


def _on_ray(px, py, ax, ay, hx, hy):
    """The claimed point lies on the FORWARD aim half-line: exact-integer colinear AND in front."""
    rx, ry = hx - px, hy - py
    return rx * ay == ry * ax and rx * ax + ry * ay > 0


def _in_range(px, py, hx, hy, max_range2):
    return (hx - px) ** 2 + (hy - py) ** 2 <= max_range2


def _clear_los(walls, px, py, hx, hy):
    """The line of fire crosses no wall cell (reuse perception's exact-integer supercover occlusion)."""
    return not PC._occluded(walls, px, py, hx, hy)


def _reason(targets, walls, sh, claim):
    """The FIRST failing predicate in fixed priority (no-target, off-box, off-ray, range, wall), or ADMIT —
    the single source of truth. Exposed at module scope so the falsifiers can plant a skipped check and
    prove the sweep reddens."""
    eid, hx, hy = claim
    if eid not in targets:
        return R_NOTARGET
    ex, ey, hbx, hby, _cite = targets[eid]
    px, py, ax, ay, mr2 = sh
    if not _on_box(hx, hy, ex, ey, hbx, hby):
        return R_OFFBOX
    if not _on_ray(px, py, ax, ay, hx, hy):
        return R_OFFRAY
    if not _in_range(px, py, hx, hy, mr2):
        return R_RANGE
    if not _clear_los(walls, px, py, hx, hy):
        return R_WALL
    return R_ADMIT


def admit(targets, walls, sh, claim):
    """SERVER-AUTHORITATIVE ADMISSION: True iff the claim earns a hit against the authoritative world. A pure
    function of (world, claim) — it never reads a client-supplied extent."""
    return _reason(targets, walls, sh, claim) == R_ADMIT


# ---- the proof-carrying verdict (constant-shape; the client cannot forge an ADMIT) ------------
def verdict_bytes_len():
    return VERDICT_BYTES


def adjudicate(targets, walls, sh, claim):
    """SERVER-AUTHORITATIVE ADJUDICATION: emit the sealed, CONSTANT-SHAPE verdict for a claim — the verdict
    code, the fixed-priority reason, and (on ADMIT only) the target's authority citation; a REFUSE carries a
    zero-cite. Witness-blind (never mutates the world). The verdict is a pure function of the authoritative
    world + claim; a client cannot make the server say ADMIT for an unearned hit."""
    eid, hx, hy = claim
    reason = _reason(targets, walls, sh, claim)
    admitted = reason == R_ADMIT
    cite_hex = targets[eid][4] if admitted else _ZERO_CITE
    body = bytearray(MAGIC)
    body += _u32(eid) + _u32(hx) + _u32(hy)
    body += _u32(VERDICT_ADMIT if admitted else VERDICT_REFUSE) + _u32(reason)
    body += PC._cite_bytes(cite_hex)
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(verdict):
    if not (type(verdict) is bytes or type(verdict) is bytearray):
        raise HitboxError("a verdict must be bytes")
    t = bytes(verdict)
    if len(t) != VERDICT_BYTES:
        raise HitboxError(f"a verdict must be exactly {VERDICT_BYTES} bytes")
    if t[:_HEADER] != MAGIC:
        raise HitboxError("bad magic — not a URDRHIT1 verdict")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise HitboxError("digest mismatch — tampered or truncated")
    off = _HEADER
    eid = int.from_bytes(t[off:off + 4], "big"); off += 4
    hx = int.from_bytes(t[off:off + 4], "big", signed=True); off += 4
    hy = int.from_bytes(t[off:off + 4], "big", signed=True); off += 4
    vcode = int.from_bytes(t[off:off + 4], "big"); off += 4
    reason = int.from_bytes(t[off:off + 4], "big"); off += 4
    cite = t[off:off + DIGEST_BYTES].hex()
    return (eid, hx, hy, vcode, reason, cite)


def read_verdict(verdict):
    """The client's view: (eid, hx, hy, admitted, reason, cite). Raises on a tampered/truncated packet."""
    eid, hx, hy, vcode, reason, cite = _parse(verdict)
    return (eid, hx, hy, vcode == VERDICT_ADMIT, reason, cite)


def verify_verdict(targets, walls, sh, verdict):
    """THE PROOF-CARRYING CONTRACT: a verdict is lawful iff it is BYTE-IDENTICAL to the authoritative
    adjudication of its own claim. A forged ADMIT (even one re-sealed with a valid self-digest) fails, because
    a fresh authoritative adjudication of the same claim disagrees — the server, not the client, decides."""
    try:
        eid, hx, hy, _v, _r, _c = _parse(verdict)
    except HitboxError:
        return False
    return bytes(verdict) == adjudicate(targets, walls, sh, (eid, hx, hy))


# ---- the falsifier tools (NOT laws — each a distinct forgery the server-authoritative law refuses) ---------
def _admit_no_box(targets, walls, sh, claim):
    """THE PHANTOM-HIT MISTAKE: skip the on-box test — admits a fabricated hit at a point that is not on the
    target at all. The server-authoritative law must refuse where this admits."""
    eid, hx, hy = claim
    if eid not in targets:
        return False
    px, py, ax, ay, mr2 = sh
    return _on_ray(px, py, ax, ay, hx, hy) and _in_range(px, py, hx, hy, mr2) and _clear_los(walls, px, py, hx, hy)


def _admit_no_ray(targets, walls, sh, claim):
    """THE OFF-RAY (AIMBOT) MISTAKE: skip the aim-ray test — admits a hit on a target the shooter is not
    actually aiming at (a snapped corner of the box off the line of fire)."""
    eid, hx, hy = claim
    if eid not in targets:
        return False
    ex, ey, hbx, hby, _c = targets[eid]
    px, py, ax, ay, mr2 = sh
    return _on_box(hx, hy, ex, ey, hbx, hby) and _in_range(px, py, hx, hy, mr2) and _clear_los(walls, px, py, hx, hy)


def _admit_no_range(targets, walls, sh, claim):
    """THE OUT-OF-RANGE MISTAKE: skip the range test — admits a hit beyond the weapon's reach."""
    eid, hx, hy = claim
    if eid not in targets:
        return False
    ex, ey, hbx, hby, _c = targets[eid]
    px, py, ax, ay, mr2 = sh
    return _on_box(hx, hy, ex, ey, hbx, hby) and _on_ray(px, py, ax, ay, hx, hy) and _clear_los(walls, px, py, hx, hy)


def _admit_no_occlusion(targets, walls, sh, claim):
    """THE WALL-SHOOT MISTAKE: skip the line-of-fire occlusion test — admits a shot THROUGH a wall."""
    eid, hx, hy = claim
    if eid not in targets:
        return False
    ex, ey, hbx, hby, _c = targets[eid]
    px, py, ax, ay, mr2 = sh
    return _on_box(hx, hy, ex, ey, hbx, hby) and _on_ray(px, py, ax, ay, hx, hy) and _in_range(px, py, hx, hy, mr2)


def _admit_client_extent(targets, walls, sh, claim_ext):
    """THE INFLATED-HITBOX MISTAKE: trust a CLIENT-SUPPLIED hitbox extent (chbx,chby) instead of the server's
    — the classic 'my hitbox is bigger' cheat. Admits an off-real-box point that lies on the client's inflated
    box. The server-authoritative law reads only ITS OWN extent, so it refuses where this admits."""
    eid, hx, hy, chbx, chby = claim_ext
    if eid not in targets:
        return False
    ex, ey, _hbx, _hby, _c = targets[eid]
    px, py, ax, ay, mr2 = sh
    return (_on_box(hx, hy, ex, ey, chbx, chby)                   # <-- CLIENT extent, the bug
            and _on_ray(px, py, ax, ay, hx, hy)
            and _in_range(px, py, hx, hy, mr2)
            and _clear_los(walls, px, py, hx, hy))


def forge_admit(verdict):
    """A falsifier tool: rewrite a REFUSE verdict into a sealed ADMIT (flip the code and reason and re-seal
    the self-digest). `verify_verdict` must STILL refuse it — the forgery is internally consistent but
    disagrees with the authoritative adjudication. Never a law."""
    t = bytearray(verdict[:-DIGEST_BYTES])
    off = _HEADER + 12                                            # past MAGIC | eid | hx | hy
    t[off:off + 4] = _u32(VERDICT_ADMIT)
    t[off + 4:off + 8] = _u32(R_ADMIT)
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


# ---- digests ----------------------------------------------------------------------------------
def world_digest(targets, walls):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for eid in sorted(targets):
        ex, ey, hbx, hby, cite = targets[eid]
        hh.update(f"|t{eid}:{ex}:{ey}:{hbx}:{hby}:{cite}".encode())
    for (wx, wy) in sorted(walls):
        hh.update(f"|w{wx}:{wy}".encode())
    return hh.hexdigest()


def verdict_digest(verdict):
    return hashlib.sha256(MAGIC + bytes(verdict)).hexdigest()


def hitbox_digest(name, world_hex, verdict_hex, reason, verdict_name):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|w:{world_hex}|v:{verdict_hex}|r:{reason}|d:{verdict_name}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------------
def _d(i):
    return PC._d(i)


def _scene(name, targets, walls, sh, claim):
    v = adjudicate(targets, walls, sh, claim)
    reason = _reason(targets, walls, sh, claim)
    return hitbox_digest(name, world_digest(targets, walls), verdict_digest(v), reason, _REASON_NAME[reason])


def _scene_clean():
    """A legitimate shot — on the authoritative box, on the forward ray, in range, no wall between — ADMITS."""
    targets = {1: (10, 0, 1, 1, _d(1))}
    return _scene("clean", targets, frozenset(), shooter(0, 0, 1, 0, 400), (1, 10, 0))


def _scene_wallshot():
    """A wall stands on the line of fire: the shot through it is REFUSED (R_WALL), though it is on-box,
    on-ray, and in range."""
    targets = {1: (10, 0, 1, 1, _d(1))}
    return _scene("wallshot", targets, frozenset({(5, 0)}), shooter(0, 0, 1, 0, 400), (1, 10, 0))


def _scene_phantom():
    """A phantom hit: a point on the forward ray but PAST the authoritative box is REFUSED (R_OFFBOX) — there
    is no target there to hit."""
    targets = {1: (10, 0, 1, 1, _d(1))}
    return _scene("phantom", targets, frozenset(), shooter(0, 0, 1, 0, 400), (1, 13, 0))


def _scene_offray():
    """An aimbot claim: a corner of the box that is NOT on the line the shooter is aiming is REFUSED
    (R_OFFRAY) — on-box but off the forward ray."""
    targets = {1: (10, 0, 1, 1, _d(1))}
    return _scene("offray", targets, frozenset(), shooter(0, 0, 1, 0, 400), (1, 10, 1))


def _scene_inflated():
    """The inflated-hitbox cheat gains nothing: a point OFF the server's real box is REFUSED (R_OFFBOX) even
    though a larger client-claimed extent would accept it — the server reads only its own geometry. The
    extent-independence teeth are exercised in the law and the sweep."""
    targets = {1: (12, 0, 1, 1, _d(1))}
    return _scene("inflated", targets, frozenset(), shooter(0, 0, 1, 0, 400), (1, 15, 0))


_SCENES = {"clean": _scene_clean, "wallshot": _scene_wallshot, "phantom": _scene_phantom,
           "offray": _scene_offray, "inflated": _scene_inflated}
SCENES = ("clean", "wallshot", "phantom", "offray", "inflated")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_hitbox.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise HitboxError(f"no golden named {name!r}")


# ---- the seeded property sweep ----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 120


def gen_scenario(r):
    """A random arena with a GUARANTEED-admit target (id 1, on the +x ray, near, unoccluded), a
    GUARANTEED-wall-shot target (id 2, on the +x ray, far, with a wall between it and the shooter), and random
    OFF-AXIS extra targets and walls (never on the y=0 firing lanes, so the guaranteed claims keep their
    ground truth independent of the admission code — a skipped check cannot hide)."""
    sh = shooter(0, 0, 1, 0, 400)
    x1 = r.rng(5, 7)                                              # id 1: admit target, near on +x
    x2 = r.rng(13, 16)                                            # id 2: wall-shot target, far on +x
    wx = r.rng(x1 + 2, x2 - 1)                                    # a wall strictly between id1 and id2
    targets = {1: (x1, 0, 1, 1, _d(1)), 2: (x2, 0, 1, 1, _d(2))}
    walls = frozenset({(wx, 0)})
    for k in range(3, 3 + r.rng(0, 3)):                           # off-axis extra targets (y != 0)
        ey = r.rng(2, 12) * (1 if (r.nxt() & 1) else -1)
        targets[k] = (r.rng(-12, 12), ey, 1, 1, _d(k))
    for _w in range(r.rng(0, 2)):                                 # off-axis extra walls (y != 0)
        wy = r.rng(2, 10) * (1 if (r.nxt() & 1) else -1)
        walls = walls | frozenset({(r.rng(-12, 12), wy)})
    return targets, walls, sh, x1, x2


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random arenas asserting server-authority (the verdict is a pure
    function of the world, never a client extent), determinism, the constant-shape verdict, the PROOF-CARRYING
    contract (a forged ADMIT never verifies), the guaranteed admit ADMITS, the guaranteed wall-shot is REFUSED
    (occlusion honoured), an off-ray corner is REFUSED, and an off-real-box point that a client's inflated box
    would accept is REFUSED. RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    admit_seen = wall_seen = offray_seen = inflated_seen = 0
    for s in range(count):
        targets, walls, sh, x1, x2 = gen_scenario(r)
        before = world_digest(targets, walls)
        # ADMIT lane — a legitimate hit
        admit_claim = (1, x1, 0)
        v_admit = adjudicate(targets, walls, sh, admit_claim)
        if world_digest(targets, walls) != before:
            raise HitboxError(f"scenario {s}: adjudication mutated the witness")
        if len(v_admit) != verdict_bytes_len():
            raise HitboxError(f"scenario {s}: the verdict is not constant-shape")
        if adjudicate(targets, walls, sh, admit_claim) != v_admit:
            raise HitboxError(f"scenario {s}: adjudication is not deterministic")
        if not verify_verdict(targets, walls, sh, v_admit):
            raise HitboxError(f"scenario {s}: an honest verdict failed its own contract")
        if not admit(targets, walls, sh, admit_claim):
            raise HitboxError(f"scenario {s}: a legitimate hit was refused")
        admit_seen += 1
        # WALL lane — a wall-shot must be REFUSED, and a forged ADMIT must never verify
        wall_claim = (2, x2, 0)
        v_wall = adjudicate(targets, walls, sh, wall_claim)
        if admit(targets, walls, sh, wall_claim):
            raise HitboxError(f"scenario {s} (seed {seed}): a wall-shot was admitted — the line-of-fire "
                              f"occlusion was bypassed; server authority FALSIFIED")
        if verify_verdict(targets, walls, sh, forge_admit(v_wall)):
            raise HitboxError(f"scenario {s}: a forged ADMIT verified — the proof-carrying contract broke")
        wall_seen += 1
        # OFF-RAY — an on-box corner off the aim line is refused
        if admit(targets, walls, sh, (1, x1, 1)):
            raise HitboxError(f"scenario {s}: an off-ray claim was admitted")
        offray_seen += 1
        # INFLATED — an off-real-box point a client's bigger extent would accept is refused (extent-blind)
        infl = (1, x1 - 2, 0)                                     # off the real box, but LoS clear and on-ray
        if admit(targets, walls, sh, infl):
            raise HitboxError(f"scenario {s}: an off-real-box point was admitted")
        if not _admit_client_extent(targets, walls, sh, (1, x1 - 2, 0, 3, 3)):
            raise HitboxError(f"scenario {s}: the inflated-extent plant did not admit (vacuous)")
        inflated_seen += 1
        hh.update(f"|{s}:{verdict_digest(v_admit)}:{verdict_digest(v_wall)}".encode())
    if admit_seen == 0 or wall_seen == 0 or offray_seen == 0 or inflated_seen == 0:
        raise HitboxError(f"NON-VACUITY: admit {admit_seen}, wall {wall_seen}, offray {offray_seen}, "
                          f"inflated {inflated_seen}")
    return {"scenarios": count, "admit_seen": admit_seen, "wall_seen": wall_seen,
            "offray_seen": offray_seen, "inflated_seen": inflated_seen, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_hitbox.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise HitboxError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except HitboxError as exc:
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
    print(f"SWEEP: {rep['scenarios']} arenas, admit_seen {rep['admit_seen']}, wall_seen {rep['wall_seen']}, "
          f"offray_seen {rep['offray_seen']}, inflated_seen {rep['inflated_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
