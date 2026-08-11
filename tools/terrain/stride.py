# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""stride — THE 3D DETERMINISTIC TICK (URDRSTR1): the first law that consumes `contact`.

`worldbasis` decided what a coordinate means. `contact` decided what support IS, and did it without
a caller so the semantics could be falsified before anything implemented them. This is the caller.
It invents nothing: every support question is asked of `contact` and every answer is taken, which
is the whole point of having written the contract first — a tick that reimplemented the vertical
law would be free to disagree with it, and nothing would notice.

WHAT THIS TICK IS. An actor occupies an exact integer cell on a heightfield and a height above it.
A tick applies at most one INTENT per actor — a cardinal direction, a jump, or both — and produces
the next position. Exact integers throughout; no float enters the path.

THE ORDER IS A DECISION AND IS RECORDED AS ONE: HORIZONTAL RESOLVES BEFORE VERTICAL. The grounded
step law is written against the support state an actor is standing in, so support must still be
the state it had when the tick began. Resolving vertical first would make a jump and a step on the
same tick IMPOSSIBLE — the jump would leave the ground and `contact` would then refuse the step as
air control — and "you may not move on the tick you jump" is a gameplay law nobody chose. Choosing
the other order gives it to a player by accident. So: step, then jump.

THREE BOUNDARIES THE TICK OWNS, EACH DECLARED RATHER THAN DISCOVERED:

  * NO AIR CONTROL. An actor AIRBORNE when the tick begins does not move horizontally. `contact`
    refuses to answer for one, and the tick honours the refusal instead of inventing an answer.
    The same rule decides a case that looks like a third thing and is not: a step that walks OFF a
    ledge leaves the actor airborne, so a jump requested on that same tick does NOT fire. You may
    not jump off ground you have already left, and that follows from the order rather than from a
    special case written to produce it.
  * THE WORLD EDGE IS A WALL. `contact.ground_height` refuses an out-of-field query — correctly,
    since it has no record to make. The tick has one: a step off the grid is BLOCKED, exactly as
    `glide` stops at the boundary. The refusal is not caught and re-interpreted; the tick simply
    does not ask a question it already knows is outside the world.
  * A CONTESTED INTENT REFUSES. Two DIFFERENT intents for one actor on one tick is not an input to
    reconcile, it is two authorities claiming one actor — `authinput`/`fraud` territory — and
    taking the last one silently would be a decision with no record. Identical intents delivered
    twice are ABSORBED, because that is delivery, not conflict.

THE WITNESS DOES NOT STEER, and this is the invariant the operator named when the contract landed.
`contact`'s support witness answers WHY an actor is supported. It must never become THEREFORE MOVE
IT HERE. Guarded twice and independently: STRUCTURALLY, because no function on the trajectory path
can receive a witness — the signatures cannot take one, which is the sealed-observer discipline
this repo already applies to metrics; and OPERATIONALLY, because blanking the witness leaves the
trajectory digest BIT-IDENTICAL while the witness stream itself demonstrably moves. A witness that
steered would change the trajectory when it changed.

INPUTS, NEVER STATE. The delivery discipline is `lockstep.canon` UNCHANGED, imported rather than
restated: exact-duplicate deliveries absorbed, each tick ordered by (peer, seq), so any arrival
permutation of one logical log yields one application order. Two peers assembling the same input
union in different orders produce the same trajectory, checked.

MEASURED, NOT OPTIMIZED. `read_cost` reports the tick's terrain reads through `contact`'s counted
door against a closed form in (actors, ticks, moves), and names the REDUNDANT ones — the support
probe and the vertical law reading the same cell on any tick the actor did not change cells. That
redundancy is REPORTED AND LEFT IN PLACE. There is no measured cost target yet, and removing it
now would be an optimization chosen by inspection, which is the habit this arc keeps declining.

GRADE (honest, D5): MEASURED — determinism, peer agreement under reordered and duplicated delivery,
the four pinned scenes, the complete jump/step/fall behaviour, every refusal, the structural and
operational witness-inertness guards, and the read-count closed form checked against execution over
a corpus. DECLARED: that this is a COMPLETE 3D tick — it walks actors over terrain and does not do
actor-actor collision, statics, or sub-cell motion, none of which it claims. `does_not_show`: that
the arena tick (`worldstep.step_tick`) migrated — it did not, and the schema door now names WHICH
law it is refusing for; that a read COUNT is a read COST (the wall-clock question is `bench.py`'s);
that a trajectory is CORRECT, only that it is reproducible and that its support states are the ones
`contact` certifies."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                       # noqa: E402  the contract, consumed
import lockstep as L                                       # noqa: E402  delivery, unchanged
import stance as ST                                        # noqa: E402  the four facings

MAGIC = b"URDRSTR1"
WORLD_FORMAT = "URDR-WORLD-4"

#: The basis's axis order, restated as indices rather than remembered: X horizontal, Y vertical,
#: Z horizontal. Read from `worldbasis` on demand (see `obeys_the_basis`), never duplicated as law.
AX_X, AX_Y, AX_Z = 0, 1, 2
DIRS = ST.DIRS                                             # the walker's four facings, not a copy


class StrideError(Exception):
    def __init__(self, message):
        super().__init__(f"STRIDE-REFUSE: {message}")
        self.code = "STRIDE-REFUSE"


def _int(name, v):
    if not isinstance(v, int) or isinstance(v, bool):
        raise StrideError(f"{name} must be an exact integer, got {v!r} ({type(v).__name__})")
    return v


# ---- the world -------------------------------------------------------------------------------
def world(heights, cells, revision="rev-0", max_step=CT.MAX_STEP, jump=4, grav=1, T=120):
    """A URDR-WORLD-4 walker world. `pos` is in BASIS ORDER (X, Y, Z) so `worldbasis` can read it
    directly rather than through a translation nobody maintains; `grav` is a 3-vector touching the
    vertical axis ALONE, which is the property the basis actually checks."""
    h, w = len(heights), len(heights[0])
    pos, vy = [], []
    for (cx, cz) in cells:
        _int("cell x", cx)
        _int("cell z", cz)
        if not (0 <= cx < w and 0 <= cz < h):
            raise StrideError(f"actor cell {(cx, cz)} is outside the {w}x{h} field")
        p = [0, 0, 0]
        p[AX_X], p[AX_Z] = cx, cz
        p[AX_Y] = heights[cz][cx]                          # actors start standing, not floating
        pos.append(p)
        vy.append(0)
    g = [0, 0, 0]
    g[AX_Y] = -_int("grav", grav)                           # +Y is up, so gravity is negative Y
    return {"format": WORLD_FORMAT, "heights": heights, "n": len(pos),
            "pos": pos, "vy": vy, "grav": tuple(g), "revision": str(revision),
            "max_step": _int("max_step", max_step), "jump": _int("jump", jump),
            "w": w, "h": h, "T": _int("T", T)}


def cell_of(p):
    return (p[AX_X], p[AX_Z])


def obeys_the_basis(w):
    """Read from `worldbasis` rather than re-asserted here — a world that claimed conformance in
    its own vocabulary would be grading its own homework."""
    import worldbasis as WB
    return WB.obeys_the_basis(w)


# ---- inputs ------------------------------------------------------------------------------------
def event(tick, peer, seq, actor, direction, jump=0):
    """(tick, peer, seq, actor, direction, jump) — the same arity and the same delivery semantics
    as a lockstep event, so `canon` applies UNCHANGED."""
    return (tick, peer, seq, actor, direction, jump)


def admit_event(w, e):
    """The typed door in front of the tick. Every class the tick would otherwise have absorbed in
    silence: a malformed shape, an unknown facing, an out-of-range actor, a tick past the horizon."""
    if not isinstance(e, tuple) or len(e) != 6:
        raise StrideError(f"event {e!r} is not a 6-tuple (tick, peer, seq, actor, dir, jump)")
    t, p, s, a, d, j = e
    for nm, v in (("tick", t), ("peer", p), ("seq", s), ("actor", a), ("jump", j)):
        _int(nm, v)
    if not (0 <= t < w["T"]):
        raise StrideError(f"tick {t} is outside the horizon [0, {w['T']}) — a dropped tick is a "
                          f"decision with no record")
    if not (0 <= a < w["n"]):
        raise StrideError(f"actor {a} is not a body of this world (n={w['n']})")
    if d != "" and d not in DIRS:
        raise StrideError(f"facing {d!r} is not one of {sorted(DIRS)} — an unknown direction is "
                          f"refused rather than read as 'no move'")
    if j not in (0, 1):
        raise StrideError(f"jump {j!r} is not 0 or 1")
    return e


def intents(w, evs):
    """This tick's canonical events -> {actor: (direction, jump)}.

    A CONTESTED INTENT REFUSES. Two different intents for one actor on one tick is not an input to
    reconcile — it is two authorities claiming one actor, which is `authinput`'s question — and
    taking the last would be a decision with no record. Two IDENTICAL intents are absorbed."""
    out = {}
    for e in evs:
        admit_event(w, e)
        _t, _p, _s, a, d, j = e
        want = (d, j)
        if a in out and out[a] != want:
            raise StrideError(f"actor {a} was given two different intents on tick {e[0]} "
                              f"({out[a]} and {want}) — a contested actor is an AUTHORITY question, "
                              f"and resolving it here by arrival order would decide it silently")
        out[a] = want
    return out


# ---- the tick ----------------------------------------------------------------------------------
def advance(w, pos, vy, evs):
    """ONE TICK. Mutates `pos`/`vy` in canonical actor order and returns (states, witnesses).

    THE WITNESS IS AN OUTPUT AND CANNOT BE AN INPUT: this signature has no parameter that could
    carry one, which is the structural half of the inertness guard — a comment saying "does not
    read the witness" is not enforcement, an argument list that cannot receive one is."""
    heights, rev = w["heights"], w["revision"]
    intent = intents(w, evs)
    states, wits = [], []
    for i in range(w["n"]):
        d, jmp = intent.get(i, ("", 0))
        cell = cell_of(pos[i])
        st, _w0 = CT.contact_of(heights, cell, pos[i][AX_Y], rev)      # the support probe: 1 read
        if d and st in CT.SUPPORTED_STATES:                            # NO AIR CONTROL
            dx, dz = DIRS[d]
            nx, nz = cell[0] + dx, cell[1] + dz
            if 0 <= nx < w["w"] and 0 <= nz < w["h"]:                  # THE EDGE IS A WALL
                out, c2, y2, _v2, _s2, _w2 = CT.step_horizontal(       # the step law: 2 reads
                    heights, cell, pos[i][AX_Y], rev, (nx, nz), w["max_step"])
                if out == CT.ADMITTED:
                    pos[i][AX_X], pos[i][AX_Z] = c2
                    pos[i][AX_Y] = y2
        y, v, st2, wit = CT.step_vertical(                             # the vertical law: 1 read
            heights, cell_of(pos[i]), pos[i][AX_Y], vy[i], rev,
            grav=-w["grav"][AX_Y], jump=w["jump"] if jmp else 0)
        pos[i][AX_Y], vy[i] = y, v
        states.append(st2)
        wits.append(wit)
    return tuple(states), tuple(wits)


def simulate(w, log):
    """The whole run from inputs alone. Returns (frames, states, witnesses).

    `frames` is the TRAJECTORY — positions and vertical velocities, and nothing else. The support
    states and the witnesses are returned BESIDE it, never inside it, so a consumer that wants the
    trajectory cannot accidentally take a dependency on the explanation."""
    by_tick = L.canon(list(log))
    pos = [list(p) for p in w["pos"]]
    vy = list(w["vy"])
    frames, sts, wits = [], [], []
    for t in range(w["T"]):
        st, wt = advance(w, pos, vy, by_tick.get(t, []))
        frames.append(tuple(tuple(p) + (v,) for p, v in zip(pos, vy)))
        sts.append(st)
        wits.append(wt)
    return tuple(frames), tuple(sts), tuple(wits)


def trajectory_digest(frames):
    hh = hashlib.sha256(MAGIC)
    for f in frames:
        hh.update(("|".join("%d,%d,%d,%d" % a for a in f)).encode())
    return hh.hexdigest()


def witness_stream_digest(wits):
    hh = hashlib.sha256(MAGIC + b"W")
    for row in wits:
        hh.update(("|".join("-" if x is None else CT.witness_digest(x) for x in row)).encode())
    return hh.hexdigest()


def state_digest(sts):
    hh = hashlib.sha256(MAGIC + b"S")
    for row in sts:
        hh.update(("|".join(row)).encode())
    return hh.hexdigest()


# ---- the witness does not steer ----------------------------------------------------------------
def the_tick_cannot_receive_a_witness():
    """THE STRUCTURAL HALF. Every function on the trajectory path is checked to have no parameter
    that could carry a support witness. This is the sealed-observer discipline the repo already
    applies to metrics — enforce it in the signature, where a comment cannot be ignored."""
    import inspect
    bad = ("witness", "wit", "wits", "support", "reason")
    for fn in (advance, simulate, intents, trajectory_digest):
        names = tuple(inspect.signature(fn).parameters)
        if any(n in bad for n in names):
            return False
    return True


def the_witness_does_not_steer(w, log):
    """THE OPERATIONAL HALF, and the stronger one. Blank the witness and the TRAJECTORY must be
    bit-identical while the WITNESS STREAM demonstrably moves. A witness that steered would change
    the trajectory when it changed; a check that only compared trajectories would pass vacuously if
    the blanking did nothing, so both halves are asserted."""
    real = CT.witness
    base_traj = trajectory_digest(simulate(w, log)[0])
    base_wits = witness_stream_digest(simulate(w, log)[2])
    try:
        CT.witness = lambda src, cell, rev, h: ("BLANK", 0, 0, "", 0)
        f2, _s2, w2 = simulate(w, log)
        moved = witness_stream_digest(w2) != base_wits
        same = trajectory_digest(f2) == base_traj
    finally:
        CT.witness = real
    return same and moved


# ---- the cost denominator ----------------------------------------------------------------------
def read_cost(w, log):
    """THE TICK'S TERRAIN READS, EXACT, against a closed form computed independently of the
    counter — a prediction that can be WRONG, not the count restated (L23).

      per actor-tick   1 support probe + 1 vertical law                       = 2
      per admitted-or-blocked horizontal attempt                              + 2

    `redundant` names the reads the support probe and the vertical law spend on the SAME cell — an
    actor that did not change cells this tick. REPORTED AND LEFT IN PLACE: there is no measured
    cost target yet, and removing it now would be an optimization chosen by inspection.

    THE PREDICTION IS DERIVED FROM THE PUBLIC TRAJECTORY AND SPENDS NO READS OF ITS OWN — no second
    probe, no reach into `contact`'s internals. An actor's support state ENTERING tick t is the
    state it was left in by tick t-1, because nothing moves between ticks; so the predictor reads
    the returned state stream instead of asking the terrain again. A measurement that had to touch
    the thing it measures would be measuring itself."""
    CT.reset_lookups()
    frames, sts, _wits = simulate(w, log)
    actual = CT.lookup_count()
    by_tick = L.canon(list(log))
    start = [cell_of(p) for p in w["pos"]]
    attempts = redundant = 0
    for t in range(w["T"]):
        intent = intents(w, by_tick.get(t, []))
        before = start if t == 0 else [(f[AX_X], f[AX_Z]) for f in frames[t - 1]]
        for i in range(w["n"]):
            d, _j = intent.get(i, ("", 0))
            supported = True if t == 0 else sts[t - 1][i] in CT.SUPPORTED_STATES
            if not d or not supported:
                continue
            dx, dz = DIRS[d]
            nx, nz = before[i][0] + dx, before[i][1] + dz
            if 0 <= nx < w["w"] and 0 <= nz < w["h"]:
                attempts += 1
        redundant += sum(1 for i in range(w["n"])
                         if (frames[t][i][AX_X], frames[t][i][AX_Z]) == before[i])
    predicted = 2 * w["n"] * w["T"] + 2 * attempts
    return {"actual": actual, "predicted": predicted, "actor_ticks": w["n"] * w["T"],
            "attempts": attempts, "redundant": redundant}


def the_read_law_holds(w, log):
    c = read_cost(w, log)
    return (c["actual"] == c["predicted"] and c["actual"] > 0
            and c["attempts"] > 0 and c["redundant"] > 0)


# ---- inputs only: the delivery discipline, imported rather than restated -----------------------
def peers_agree(w, log):
    """Two peers assembling the SAME input union in DIFFERENT orders produce the SAME trajectory,
    and a reordered or duplicated delivery of one logical log is ABSORBED. `lockstep`'s own helpers
    are used, so a drift in the delivery law would show up here rather than be re-implemented past."""
    base = trajectory_digest(simulate(w, log)[0])
    return (trajectory_digest(simulate(w, L.reorder_delivery(log))[0]) == base
            and trajectory_digest(simulate(w, L.duplicate_delivery(log))[0]) == base)


def a_different_input_is_not_absorbed(w, log):
    """NON-VACUITY for the row above: dedup must absorb DELIVERY, never CONTENT. One genuinely
    different intent — a new seq, so not an exact duplicate — must move the trajectory, or
    'reordering changed nothing' would be a statement about inputs not mattering."""
    t, p, s, a, d, j = log[0]
    other = "W" if d == "E" else "E"
    extra = list(log) + [event(t, p, s + 9991, a, other, j)]
    try:
        simulate(w, extra)
    except StrideError as exc:                 # a CONTESTED intent is the stronger outcome
        return "two different intents" in str(exc)
    return False


# ---- fixtures ----------------------------------------------------------------------------------
def _field():
    """A rise of 2 (walkable), a wall of 5, and a drop of 6 — the three step outcomes plus a pit,
    so no scene below can pass by never meeting one of them."""
    return ((5, 5, 5, 5, 5, 5),
            (5, 5, 7, 7, 5, 5),
            (5, 7, 12, 12, 7, 5),
            (5, 5, 7, 7, 1, 5),
            (5, 5, 5, 5, 5, 5),
            (5, 5, 5, 5, 5, 5))


def _log(actor, steps, peer=0):
    return [event(t, peer, t, actor, d, j) for t, (d, j) in enumerate(steps)]


SCENES = ("walk", "wall", "leap", "fall", "peers")


def scene_case(name):
    """(world, log) for each pinned scene — the fixtures, so a golden addresses something a reader
    can run rather than a number that arrived from somewhere."""
    f = _field()
    if name == "walk":                       # flat ground, four steps east
        return world(f, [(0, 0)], T=8), _log(0, [("E", 0)] * 4)
    if name == "wall":                       # climb the rise, then meet the 5-rise wall
        return world(f, [(0, 2)], T=8), _log(0, [("E", 0)] * 4)
    if name == "leap":                       # step and jump on the SAME tick, then land
        return world(f, [(0, 0)], T=12), _log(0, [("E", 1)] + [("", 0)] * 8)
    if name == "fall":                       # walk off the ledge into the pit at (4, 3)
        return world(f, [(2, 3)], T=10), _log(0, [("E", 0)] * 3)
    if name == "peers":                      # two actors, two peers, interleaved
        w = world(f, [(0, 0), (5, 5)], T=8)
        return w, (_log(0, [("E", 0)] * 3, peer=0) + _log(1, [("W", 0)] * 3, peer=1))
    raise StrideError(f"no scene named {name!r}")


def scene_result(name):
    w, log = scene_case(name)
    frames, sts, wits = simulate(w, log)
    return hashlib.sha256(
        MAGIC + b"|" + name.encode() + b"|" + trajectory_digest(frames).encode()
        + b"|" + state_digest(sts).encode() + b"|" + witness_stream_digest(wits).encode()
    ).hexdigest()


def stride_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n) for n in SCENES).encode()
                          ).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_stride.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise StrideError(f"no golden named {name!r}")


def _island_world(T=24):
    import heightfield as HF
    return world(HF.generate(**HF.island()), [(8, 8), (20, 20), (33, 41)], T=T)


def cost_case():
    w = _island_world()
    log = []
    for i, seq in enumerate(("EESSWWNN", "SSEENNWW", "NNWWSSEE")):
        for t, d in enumerate(seq * 3):
            if t < w["T"]:
                log.append(event(t, i, t, i, d, 1 if t % 7 == 0 else 0))
    return w, log


if __name__ == "__main__":
    for n in SCENES:
        w, log = scene_case(n)
        fr, st, _wt = simulate(w, log)
        print("%-6s %s  end=%s" % (n, " ".join(s[0] for s in (r[0] for r in st)),
                                   tuple(fr[-1][0])))
    w, log = cost_case()
    print("cost", read_cost(w, log))
    print("read law", the_read_law_holds(w, log))
    print("witness inert", the_witness_does_not_steer(*scene_case("leap")),
          the_tick_cannot_receive_a_witness())
    for n in SCENES:
        print(n, scene_result(n))
    print("stride", stride_digest())
