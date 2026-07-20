# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""ghostsnap — THE ACTOR WIRE (T3.54, V3, URDRGHS1): equal-or-refuse ghosts. `wire` replicated the
TERRAIN; this replicates the ACTORS. The industry's ghost-snapshot pattern (Unity's
Netcode-for-Entities) streams server-authoritative entities to clients as per-tick snapshots the
client TRUSTS, interpolating and predicting from bytes it cannot check. Hainuwele's counterpart
makes a ghost a CONTENT-ADDRESSED per-tick POSE RECORD chained by parent digest (terraform's chain
law, on the movement plane), admitted under the SAME equal-or-refuse discipline the terrain wire
uses. The differentiated claim, unchanged: not a cheaper ghost — a ghost that CANNOT LIE.

THE GHOST SNAPSHOT (112 bytes): MAGIC | actor_id | tick | parent_addr | fx | fy | facing | SHA-256.
Content-addressed (the tail digest is its address AND its integrity check). Chained: each
snapshot's parent is the actor's PREVIOUS snapshot address, so an actor's history is a hash chain
(the genesis snapshot chains from all-zeros — the spawn). No sequence numbers: order is structural,
exactly as in the terrain wire.

THE LAWS. EQUAL-OR-REFUSE GHOSTS — a snapshot admits iff it VERIFIES (digest), the actor is IN
INTEREST (within the observer's area-of-interest radius — `interest`'s Chebyshev AoI, reused), and
it CHAINS from the client's current ghost for that actor (parent CAS). A forged, tampered, stale,
duplicated, or out-of-interest ghost is a typed GHOST-REFUSE with the client's ghost state
byte-unchanged — never a silent teleport. CHAIN ORDER + AT-MOST-ONCE — an out-of-order snapshot
refuses on the parent then admits on the in-order retry; a duplicate refuses (its admission moved
the parent). INTEREST FOLLOWS THE OBSERVER — an actor outside the radius is filtered; a delivered
out-of-interest ghost refuses. TWO CLIENTS, ONE TRUTH — two clients admitting the same stream reach
the IDENTICAL ghost witness. THE INTERPOLATION FIREWALL — a rendered ghost is interpolated between
two snapshots (declared, exact integer lerp, bounded); the witness is over the snapshot poses only
(D15 on actors — ghosts smooth the VIEW, never the witness; loop_witness-style, the witness
function's domain is the ghost addresses alone).

GRADE. The record round-trip and tamper-refusal, equal-or-refuse purity, chain order with
at-most-once, interest-follows-the-observer, two-clients-one-truth (with a storm-style chaotic
relay converging), and the interpolation firewall are MEASURED. DECLARED, honestly: WHO authors a
ghost is `sealwrit`'s signature (a ghost admits whoever relays a lawful chain; a signed-ghost
successor is the composition, not re-proven here); PREDICTION of the LOCAL actor is
`predict`/`cpredict`/`splice` (certified already — the local player is predicted, remote actors are
ghosts); the interest POLICY (radius, buckets) is operational (`interest`'s AoI is the mechanism);
wall-clock interpolation timing is `panelight`'s accumulator, OFF-GATE. THE KINEMATIC LAW, LANDED
(Tier-2b, the pre-mesh hardening review's one correctness fix): a WARDED client — one holding the
terrain replica — now runs `ghost_reachable` inside `ghost_admit`, refusing a ghost whose pose is
not reachable from its parent under the SAME movement law the local actor obeys (the `warden`'s
gait bound + walkable-component β₀, reused). A remote ghost can no longer teleport, speed-hack, or
wall-clip and still admit — "a ghost that cannot lie" now covers its MOTION, not only its BYTES. THE
RESIDUAL, declared and made executable (`unwarded_teleport`): the law is TERRAIN-GATED — a bytes-
only subscriber that holds no terrain checks only bytes; the authoritative server always holds the
terrain, so this is a weaker DECLARED posture, never a silent one. `does_not_show`: fps/latency
(bench §3); the depicting client; DIRECTED reachability (`warden` uses undirected mutual-reachability
components — a one-way drop is a follow-on); cross-placement (URDRGHS1 joins the frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRGHS1"
GENESIS = "0" * 64
GHOST_LEN = 8 + 8 + 8 + 32 + 8 + 8 + 8 + 32                     # 112 bytes
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PHYS = _os.path.join(_os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import interest as _AOI                                         # the AoI interest filter (reused)
import warden as _WARD                                         # the movement law (gait + β₀ reachability)
from field import ONE                                          # the frozen Q32.32 radix


class GhostError(Exception):
    def __init__(self, message):
        super().__init__(f"GHOST-REFUSE: {message}")
        self.code = "GHOST-REFUSE"


def _i64(v):
    return int(v).to_bytes(8, "big", signed=True)


def _h(b):
    return hashlib.sha256(b).digest()


def ghost_record(actor_id, tick, parent_hex, fx, fy, facing):
    """A ghost snapshot: the actor's pose at a tick, chained to its parent, content-addressed."""
    if not (isinstance(parent_hex, str) and len(parent_hex) == 64):
        raise GhostError("parent must be a 32-byte hex address (GENESIS for a spawn)")
    pre = bytearray(MAGIC)
    pre += _i64(actor_id) + _i64(tick) + bytes.fromhex(parent_hex)
    pre += _i64(fx) + _i64(fy) + _i64(facing)
    return bytes(pre) + _h(bytes(pre))


def restore_ghost(snap):
    """(actor_id, tick, parent, fx, fy, facing) from a verified snapshot; a bad digest refuses."""
    if len(snap) != GHOST_LEN or snap[:8] != MAGIC:
        raise GhostError(f"a ghost snapshot is exactly {GHOST_LEN} bytes under {MAGIC!r}")
    if _h(snap[:GHOST_LEN - 32]) != snap[GHOST_LEN - 32:]:
        raise GhostError("the snapshot does not hash to its own address — tampered, refused")
    g = lambda o: int.from_bytes(snap[o:o + 8], "big", signed=True)
    return (g(8), g(16), snap[24:56].hex(), g(56), g(64), g(72))


def address(snap):
    """The snapshot's content address — its tail SHA-256, hex."""
    return snap[GHOST_LEN - 32:].hex()


def cell_of(fx, fy):
    return (fx >> 32, fy >> 32)


def relevant(snap, observer_cell, radius):
    """THE INTEREST FILTER: the actor is in interest iff its snapshot cell is within the observer's
    Chebyshev AoI radius (`interest`'s ground-truth distance, reused)."""
    _aid, _tick, _p, fx, fy, _f = restore_ghost(snap)
    ax, ay = cell_of(fx, fy)
    ox, oy = observer_cell
    return _AOI._cheby(ox, oy, ax, ay) <= radius


def subscribe_ghosts(observer, radius, field=None, max_step=0):
    """A ghost client: its observer cell, its AoI radius, the (empty) per-actor ghost map, and —
    OPTIONALLY — the terrain replica it holds (the walkable `field` + its step law `max_step`). A
    client that holds terrain is WARDED: `ghost_admit` enforces the movement law (Tier-2b) so a
    remote ghost cannot teleport or wall-clip. A `field=None` client is bytes-only — the pre-
    hardening behaviour, preserved for callers that do not hold a terrain replica."""
    if not (isinstance(observer, tuple) and len(observer) == 2):
        raise GhostError("observer must be an (x, y) cell")
    if field is not None and not (isinstance(field, tuple) and field and isinstance(field[0], tuple)):
        raise GhostError("a warded client's terrain replica must be a non-empty rectangular grid")
    if not (type(max_step) is int and max_step >= 0):
        raise GhostError(f"max_step must be a non-negative int, got {max_step!r}")
    return {"observer": observer, "radius": radius, "ghosts": {}, "field": field, "max_step": max_step}


def ghost_reachable(field, max_step, parent_snap, child_snap):
    """THE KINEMATIC LAW (Tier-2b hardening): a child pose is admissible from its parent iff the move
    obeys the SAME movement law the LOCAL actor obeys — the `warden`'s certificate, reused on the
    ghost plane. Three exact, division-free checks:

      * TIME — Δtick ≥ 1 (a ghost may not move backward, nor stand still in time; snapshots along a
        chain advance the clock).
      * REACHABILITY (topological, β₀) — the destination cell is in the parent cell's walkable
        COMPONENT (`warden.reachable`): a wall-clip into a separated region refuses even when it is
        SLOW enough to pass the speed bound — the cheat a per-tick replay cannot cheaply catch.
      * GAIT + STEP (kinematic) — the cardinal cell span is at most `MAX_JUMP` cells per tick
        (`|Δx|+|Δy| ≤ MAX_JUMP·Δtick`), and for a single-tick move the exact `warden.step_kind`
        (cardinal, ≤2 cells, every sub-step's rise ≤ max_step) is OK/STAY — no teleport, no tunnel.

    Raises `GhostError` on any violation (the ghost that lied about its MOTION); returns
    (from_cell, to_cell, dt) on OK. Pure — reads the field, mutates nothing."""
    _pa, ptick, _pp, pfx, pfy, _pf = restore_ghost(parent_snap)
    _ca, ctick, _cp, cfx, cfy, _cf = restore_ghost(child_snap)
    dt = ctick - ptick
    if dt < 1:
        raise GhostError(f"a ghost may not move backward or stand still in time (Δtick={dt}) — refused")
    a = cell_of(pfx, pfy)
    b = cell_of(cfx, cfy)
    try:
        ok = _WARD.reachable(field, a, b, max_step)
    except _WARD.WardError as exc:
        raise GhostError(f"ghost pose off the terrain replica ({a}→{b}): {exc.sub}")
    if not ok:
        raise GhostError(f"ghost pose {b} is unreachable from {a} — a different walkable component "
                         f"(a wall-clip the byte digest cannot see)")
    span = abs(b[0] - a[0]) + abs(b[1] - a[1])
    if span > _WARD.MAX_JUMP * dt:
        raise GhostError(f"ghost moved {span} cells in {dt} tick(s) — over the gait bound "
                         f"{_WARD.MAX_JUMP}/tick (a teleport / speed-hack the byte digest cannot see)")
    if dt == 1:
        kind = _WARD.step_kind(field, a, b, max_step)
        if kind not in ("OK", "STAY"):
            raise GhostError(f"ghost move {a}→{b} is a {kind} — refused by the per-tick movement law")
    return (a, b, dt)


def ghost_admit(client, snap):
    """THE VERIFIER: admit one ghost snapshot under the equal-or-refuse law — it verifies
    (identity), the actor is IN INTEREST, it CHAINS from the client's current ghost for that actor
    (parent CAS: genesis if unseen), and — if the client is WARDED (holds a terrain replica) — its
    pose is KINEMATICALLY REACHABLE from its parent (Tier-2b: gait bound + walkable component).
    Returns a NEW client; every refuse leaves the ghost map byte-identical."""
    aid, _tick, parent, _fx, _fy, _f = restore_ghost(snap)     # bad digest → GHOST-REFUSE
    if not relevant(snap, client["observer"], client["radius"]):
        raise GhostError(f"actor {aid} is outside the observer's area of interest — filtered")
    held = client["ghosts"].get(aid)
    expected = address(held) if held is not None else GENESIS
    if parent != expected:
        raise GhostError(f"actor {aid}'s snapshot parent {parent[:12]}… does not chain from the "
                         f"current ghost {expected[:12]}… — stale, reordered, or duplicated")
    field = client.get("field")
    if field is not None and held is not None:                 # WARDED: the ghost must MOVE lawfully
        ghost_reachable(field, client.get("max_step", 0), held, snap)
    ghosts = dict(client["ghosts"])
    ghosts[aid] = snap
    return {"observer": client["observer"], "radius": client["radius"], "ghosts": ghosts,
            "field": field, "max_step": client.get("max_step", 0)}


def ghost_witness(client):
    """The ghost authority: SHA-256 over the per-actor (id → current ghost address) map in actor
    order. What 'two clients, one truth' pins down to one hex. Domain: the ghost map alone — no
    interpolated frame can enter it (the firewall's type)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for aid in sorted(client["ghosts"]):
        hh.update(f"|{aid}:{address(client['ghosts'][aid])}".encode())
    return hh.hexdigest()


def interpolate_ghost(snap_a, snap_b, alpha, tick_ms):
    """THE DECLARED GHOST FRAME (presentation, walled from the witness): an exact integer lerp of a
    ghost's position between two snapshots by alpha/tick_ms — bounded, deterministic, OUTSIDE the
    authority (the witness never sees it)."""
    if not (0 <= alpha < tick_ms):
        raise GhostError(f"alpha {alpha} out of the frame window [0,{tick_ms})")
    _a1, _t1, _p1, fxa, fya, _f1 = restore_ghost(snap_a)
    _a2, _t2, _p2, fxb, fyb, _f2 = restore_ghost(snap_b)
    fx = fxa + (fxb - fxa) * alpha // tick_ms
    fy = fya + (fyb - fya) * alpha // tick_ms
    return (fx, fy)


def run_relay(observer, radius, delivery):
    """A storm-style chaotic ghost relay: deliver snapshots in the given (possibly shuffled) order
    through a retry loom — out-of-order refuse and requeue, passes to fixpoint. Returns {client,
    admitted, refusals, stalled}. The client is `ghost_admit`, UNMODIFIED."""
    client = subscribe_ghosts(observer, radius)
    queue = list(delivery)
    admitted = refusals = 0
    while True:
        retry = []
        progressed = False
        for snap in queue:
            try:
                client = ghost_admit(client, snap)
                admitted += 1
                progressed = True
            except GhostError:
                refusals += 1
                retry.append(snap)
        if not progressed or not retry:
            return {"client": client, "admitted": admitted, "refusals": refusals,
                    "stalled": len(retry) if retry else 0}
        queue = retry


def ghostsnap_digest(name, witness_hex, snaps, refusals, verdict):
    """URDRGHS1 canon — SHA-256(MAGIC | name | witness | snaps | refusals | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{witness_hex}|n:{snaps}|r:{refusals}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _chain(actor_id, xs, ys):
    snaps = []
    parent = GENESIS
    for i, (x, y) in enumerate(zip(xs, ys)):
        snap = ghost_record(actor_id, i, parent, x * ONE, y * ONE, 1)
        snaps.append(snap)
        parent = address(snap)
    return snaps


def _scene_muster():
    """Three actors' ghost chains admitted in-order to one observer, all within interest — the
    ghost witness over the resulting cohort."""
    a = _chain(1, [2, 3, 4], [8, 8, 8])
    b = _chain(2, [5, 6], [9, 9])
    c = _chain(3, [3, 3], [7, 6])
    client = subscribe_ghosts((4, 8), 16)
    for snap in (a[0], b[0], c[0], a[1], b[1], a[2], c[1]):
        client = ghost_admit(client, snap)
    ok = len(client["ghosts"]) == 3
    return ghost_witness(client), 7, 0, ("ADMIT" if ok else "GHOST-REFUSE")


def _scene_interloper():
    """Five forgery/interest violations — a tampered snapshot, a foreign-parent genesis, a
    duplicate, an out-of-interest actor, and an out-of-order snapshot — each refuse with the ghost
    map byte-identical; the genuine chain then admits."""
    a = _chain(1, [2, 3, 4], [8, 8, 8])
    client = subscribe_ghosts((3, 8), 4)
    before = ghost_witness(client)
    tampered = bytearray(a[0]); tampered[50] ^= 0x01
    foreign = ghost_record(1, 0, "f" * 64, 2 * ONE, 8 * ONE, 1)
    far = ghost_record(9, 0, GENESIS, 40 * ONE, 40 * ONE, 1)
    refused = 0
    for probe in (bytes(tampered), foreign, far, a[1]):        # a[1] is out-of-order (parent unheld)
        try:
            ghost_admit(client, probe)
        except GhostError:
            refused += 1
    pure = ghost_witness(client) == before
    client = ghost_admit(client, a[0])
    try:
        ghost_admit(client, a[0])                              # duplicate refuses
        dup_refused = False
    except GhostError:
        dup_refused = True
    ok = refused == 4 and pure and dup_refused
    return ghost_witness(client), 5, refused + (1 if dup_refused else 0), \
        ("GHOST-REFUSE" if ok else "ADMIT")


def _scene_relay():
    """A shuffled ghost delivery converges under the retry loom — out-of-order snapshots refuse and
    requeue, all admit to the same witness the in-order stream reaches."""
    chain = _chain(1, [2, 3, 4, 5], [8, 8, 8, 8])
    ordered = subscribe_ghosts((4, 8), 16)
    for snap in chain:
        ordered = ghost_admit(ordered, snap)
    out = run_relay((4, 8), 16, [chain[2], chain[0], chain[3], chain[1]])
    ok = (out["refusals"] > 0 and out["admitted"] == len(chain)
          and ghost_witness(out["client"]) == ghost_witness(ordered))
    return ghost_witness(out["client"]), len(chain), out["refusals"], \
        ("ADMIT" if ok else "GHOST-REFUSE")


def _scene_concord():
    """Two clients, one truth: the same ghost stream admitted by two independent observers reaches
    the identical ghost witness — every byte admitted, never trusted."""
    a = _chain(1, [2, 3, 4], [8, 8, 8])
    b = _chain(2, [5, 6], [9, 9])
    stream = (a[0], b[0], a[1], b[1], a[2])
    c1 = subscribe_ghosts((4, 8), 16)
    c2 = subscribe_ghosts((4, 8), 16)
    for snap in stream:
        c1 = ghost_admit(c1, snap)
    for snap in stream:
        c2 = ghost_admit(c2, snap)
    ok = ghost_witness(c1) == ghost_witness(c2)
    return ghost_witness(c1), len(stream), 0, ("ADMIT" if ok else "GHOST-REFUSE")


# ---- warded scenes: the kinematic law (Tier-2b) -----------------------------------------
def _flat16():
    """A flat 16×16 walkable canvas — one component; only the gait/speed bound can bite here."""
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


def _barrier16():
    """A flat 16×16 world split by an impassable wall column at x=8 (height 200); at max_step 40 the
    wall separates west from east — `warden`'s β₀ barrier reused for the ghost reachability check."""
    return tuple(tuple(200 if x == 8 else 0 for x in range(16)) for _y in range(16))


_WMS = 40                                                       # the warded step law (matches warden)


def _scene_warded_muster():
    """A WARDED client (holding the flat terrain replica) admits an honest ghost walking one cell per
    tick — the kinematic law does not refuse LAWFUL motion (the non-vacuity control)."""
    client = subscribe_ghosts((4, 8), 16, field=_flat16(), max_step=_WMS)
    parent = GENESIS
    for i, (x, y) in enumerate([(2, 8), (3, 8), (4, 8), (5, 8)]):
        snap = ghost_record(1, i, parent, x * ONE, y * ONE, 1)
        client = ghost_admit(client, snap)
        parent = address(snap)
    ok = len(client["ghosts"]) == 1
    return ghost_witness(client), 4, 0, ("ADMIT" if ok else "GHOST-REFUSE")


def _scene_warded_teleport():
    """A WARDED client REFUSES a ghost that jumps 12 cells in one tick — a teleport / speed-hack the
    byte digest cannot see; the ghost map is byte-identical after the refusal (equal-or-refuse, on
    MOTION). The honest genesis snapshot admitted first."""
    client = subscribe_ghosts((8, 8), 16, field=_flat16(), max_step=_WMS)
    g0 = ghost_record(1, 0, GENESIS, 2 * ONE, 8 * ONE, 1)
    client = ghost_admit(client, g0)
    g1 = ghost_record(1, 1, address(g0), 14 * ONE, 8 * ONE, 1)  # 12-cell jump in one tick
    before = ghost_witness(client)
    refused = 0
    try:
        ghost_admit(client, g1)
    except GhostError:
        refused = 1
    ok = refused == 1 and ghost_witness(client) == before
    return ghost_witness(client), 2, refused, ("GHOST-REFUSE" if ok else "ADMIT")


def _scene_warded_wallclip():
    """A WARDED client on the barrier field REFUSES a ghost that crosses the wall SLOWLY — (6,8) at
    tick 0 to (10,8) at tick 4: a span of 4 over 4 ticks PASSES the gait bound, but the destination
    is in a different walkable component (β₀ separates west from east), so REACHABILITY refuses. The
    wall-clip a per-tick speed replay cannot cheaply catch."""
    client = subscribe_ghosts((8, 8), 16, field=_barrier16(), max_step=_WMS)
    g0 = ghost_record(1, 0, GENESIS, 6 * ONE, 8 * ONE, 1)
    client = ghost_admit(client, g0)
    g1 = ghost_record(1, 4, address(g0), 10 * ONE, 8 * ONE, 1)
    before = ghost_witness(client)
    refused = 0
    try:
        ghost_admit(client, g1)
    except GhostError:
        refused = 1
    ok = refused == 1 and ghost_witness(client) == before
    return ghost_witness(client), 2, refused, ("GHOST-REFUSE" if ok else "ADMIT")


def _scene_unwarded_teleport():
    """THE HONEST BOUNDARY (the does_not_show, made executable): an UNWARDED client — one holding NO
    terrain replica — ADMITS the very 12-cell teleport the warded client refuses. The kinematic law
    is terrain-gated: a client that does not hold the world can check only BYTES, not MOTION. The
    authoritative server always holds the terrain; a bytes-only subscriber is a DECLARED weaker
    posture, not a silent one."""
    client = subscribe_ghosts((20, 20), 10 ** 9)               # no field → bytes-only
    g0 = ghost_record(1, 0, GENESIS, 2 * ONE, 8 * ONE, 1)
    g1 = ghost_record(1, 1, address(g0), 14 * ONE, 8 * ONE, 1)
    client = ghost_admit(client, g0)
    client = ghost_admit(client, g1)                           # admits — no terrain to check against
    ok = len(client["ghosts"]) == 1
    return ghost_witness(client), 2, 0, ("ADMIT" if ok else "GHOST-REFUSE")


_SCENES = {"muster": _scene_muster, "interloper": _scene_interloper,
           "relay": _scene_relay, "concord": _scene_concord,
           "warded_muster": _scene_warded_muster, "warded_teleport": _scene_warded_teleport,
           "warded_wallclip": _scene_warded_wallclip, "unwarded_teleport": _scene_unwarded_teleport}
SCENES = ("muster", "interloper", "relay", "concord",
          "warded_muster", "warded_teleport", "warded_wallclip", "unwarded_teleport")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    wit, snaps, refusals, verdict = scene_case(name)
    return ghostsnap_digest(name, wit, snaps, refusals, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_ghostsnap.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise GhostError(f"no golden named {name!r}")
