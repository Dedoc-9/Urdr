# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""mould — THE RECORD TAKES THE SHAPE OF THE STATE (URDRMLD1), so the saving is a TYPE rather than
a policy.

`retain` measured that a grounded actor's vertical velocity is INERT and an airborne actor's is
REQUIRED. The obvious next move is to drop it when grounded, and the obvious next move is a POLICY:
a rule someone follows, forgets, or gets wrong in one branch. This rung makes it a SHAPE instead. A
grounded slot has no `vy` FIELD — not a zero, not an ignored value, no field — so writing one is not
discouraged, it is impossible, and a reader cannot consult a value that does not exist.

THE SHAPE IS DERIVED, NOT TAGGED, AND THAT IS THE WHOLE ARITHMETIC. The naive version tags each slot
with its state so a reader knows how many integers to take. It saves NOTHING: a tag costs one value
per actor and `vy` costs one value per actor, so the record is exactly the size it was and now has
a second thing to keep consistent. What makes the shaping pay is that the state is DERIVABLE from
the prefix the record already carries — read `x, y, z`, ask `contact` what state that is in this
world, and the answer tells you whether a fourth integer follows. The record is self-describing
against the world, and carries no field naming its own shape. A falsifier reads the record's own
structure to confirm no tag is present.

TWO MOULDS THAT WOULD BE WRONG, BOTH EXHIBITED. An ALL-AIRBORNE mould is correct and saves nothing —
it is the flat record with extra ceremony. An ALL-GROUNDED mould is smaller and wrong — and it is
caught BY REFUSAL rather than by divergence, which is the outcome that makes this a TYPE rather than
a policy: a 3-integer slot for an airborne actor produces a record whose derived state wants four,
so the shape CONTRADICTS THE WORLD and the record cannot be opened at all. A policy would have
produced a smaller record that silently resumed wrong. The honest mould sits exactly between the two
neighbours, and both are built here so that "it saves something" and "it stays correct" are each
proved against the thing that would violate it.

THE SHAPES ARE READ FROM `retain`, NOT RESTATED. `retain.retained_fields(state)` is the measured
answer to which integers a state needs, and this module imports it rather than carrying a second
copy — a shape table written twice is a table that can disagree with the measurement that justified
it.

THE SAVING IS A COUNT. Over the pinned arc the flat record spends 4 integers per actor-tick and the
moulded one spends 3 on grounded ticks, reported with its denominator and NOT as a rate, a byte
figure, or a latency. Whether a smaller record is a faster one is a question for a benchmark on a
named host; a falsifier checks this module imports no clock.

GRADE (honest, D5): MEASURED — the moulded record resumes BIT-IDENTICALLY to the flat one, in both
the trajectory and the reasons, at every tick of a corpus carrying both states; the shape is derived
from the prefix with no tag, checked structurally; a mis-shaped slot REFUSES; the all-grounded mould
is proved lossy and the all-airborne mould proved to save nothing; the integer counts are exact.
DECLARED: that this is the smallest possible record — it is the smallest one `retain`'s corpus
justifies, which is a different claim and the one made. `does_not_show`: any wall-clock or byte
consequence; that the two shapes are the only ones (a third contact state exists and has no
producer, so it has no mould either, and `mould_for` REFUSES it rather than guessing); durability,
which is `persist`/`resurrect`'s and is untouched."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                        # noqa: E402
import retain as RT                                         # noqa: E402
import stride as SR                                         # noqa: E402
import vouch as VC                                          # noqa: E402

MAGIC = b"URDRMLD1"


class MouldError(Exception):
    def __init__(self, message):
        super().__init__(f"MOULD-REFUSE: {message}")
        self.code = "MOULD-REFUSE"


def mould_for(state):
    """WHICH INTEGERS A SLOT IN THIS STATE CARRIES — read from `retain`, which MEASURED it, rather
    than restated here. A shape table written twice is a table that can disagree with the
    measurement that justified it.

    `GEOMETRY_SUPPORTED` has no producer and therefore no mould: `retain` never observed it, so
    guessing a shape for it would be inventing a measurement."""
    if state == CT.GEOMETRY_SUPPORTED:
        raise MouldError("GEOMETRY_SUPPORTED has no producer, so `retain` never observed it and "
                         "there is no measured shape to use — a mould invented for it would be a "
                         "measurement nobody made")
    return RT.retained_fields(state)


def slot_length(state):
    return len(mould_for(state))


# ---- minting and reading -------------------------------------------------------------------------
def mint(world, frames, states, tick, actor_states=None):
    """The moulded record: `(tick, (slot, ...), revision)` where each slot is 3 or 4 integers
    according to ITS OWN actor's contact state. NO SLOT CARRIES A TAG."""
    if not (0 <= tick < len(frames)):
        raise MouldError(f"tick {tick} is outside the recorded trajectory [0, {len(frames)})")
    st = actor_states if actor_states is not None else states[tick]
    slots = []
    for i, a in enumerate(frames[tick]):
        fields = mould_for(st[i])
        slots.append(tuple(int(a[j]) for j in range(len(fields))))
    return (int(tick), tuple(slots), str(world["revision"]))


def derived_state(world, slot):
    """THE SHAPE, DERIVED FROM THE PREFIX. `x, y, z` are always present; `contact` answers what
    state that is in this world; the answer says whether a fourth integer follows. This is why the
    record needs no tag, and it is the entire reason the shaping saves anything."""
    if len(slot) < 3:
        raise MouldError(f"slot {slot!r} is shorter than the three coordinates every shape carries")
    x, y, z = slot[SR.AX_X], slot[SR.AX_Y], slot[SR.AX_Z]
    state, _w = CT.contact_of(world["heights"], (x, z), y, world["revision"])
    return state


def admit(world, record):
    """A MIS-SHAPED SLOT REFUSES. The derived state says how many integers the slot must have; a
    slot that disagrees is not a record with an odd field, it is a record whose shape contradicts
    the world it claims to describe."""
    try:
        tick, slots, revision = record
    except (TypeError, ValueError):
        raise MouldError(f"{record!r} is not a (tick, slots, revision) record")
    if revision != world["revision"]:
        raise MouldError(f"the record was minted against revision {revision!r} and this world is "
                         f"at {world['revision']!r}")
    if len(slots) != world["n"]:
        raise MouldError(f"the record carries {len(slots)} slots and the world has {world['n']}")
    for i, slot in enumerate(slots):
        want = slot_length(derived_state(world, slot))
        if len(slot) != want:
            raise MouldError(f"slot {i} carries {len(slot)} integers and its derived state needs "
                             f"{want} — the shape contradicts the world, which is not a field to "
                             f"ignore but a record that cannot be read")
    return tick


def to_vouch(world, record):
    """Back to the flat `vouch` record, so `resume` runs UNCHANGED. A grounded slot's absent `vy`
    reads as zero, which is not a default filling a gap: `contact` guarantees a supported actor's
    vertical velocity IS zero, and `retain` measured that perturbing it changes nothing."""
    tick = admit(world, record)
    _t, slots, revision = record
    return (tick, tuple(tuple(s) + ((0,) if len(s) == 3 else ()) for s in slots), revision)


def resume(world, record, log):
    return VC.resume(world, to_vouch(world, record), log)


def record_digest(record):
    return hashlib.sha256(MAGIC + repr(record).encode()).hexdigest()


# ---- the neighbours that would be wrong ----------------------------------------------------------
def mint_all_airborne(world, frames, tick):
    """CORRECT AND SAVES NOTHING — the flat record with extra ceremony."""
    st = tuple(CT.AIRBORNE for _ in frames[tick])
    return mint(world, frames, None, tick, actor_states=st)


def mint_all_grounded(world, frames, tick):
    """SMALLER AND LOSSY — it drops the vertical velocity of actors in flight."""
    st = tuple(CT.TERRAIN_GROUNDED for _ in frames[tick])
    return mint(world, frames, None, tick, actor_states=st)


# ---- the counts ------------------------------------------------------------------------------------
def ints_stored(record):
    return sum(len(s) for s in record[1])


def saving_census(name="jump"):
    """FLAT AGAINST MOULDED over the whole arc, in integers, with the denominator. Not a rate, not
    a byte figure, not a latency."""
    w, lg = RT.corpus(name)
    frames, states, _wits = VC.full(w, lg)
    flat = moulded = ticks = 0
    for t in range(len(frames) - 1):
        flat += ints_stored(mint_all_airborne(w, frames, t))
        moulded += ints_stored(mint(w, frames, states, t))
        ticks += 1
    return {"ticks": ticks, "flat_ints": flat, "moulded_ints": moulded,
            "saved_ints": flat - moulded, "actors": w["n"]}


# ---- the laws -----------------------------------------------------------------------------------
def the_mould_resumes_identically(name="jump"):
    """THE LOAD-BEARING LAW. A smaller record that changed a replay would be worthless, so the
    moulded record must reproduce the flat one's trajectory AND its reasons — checked apart, per
    `vouch` — at EVERY tick of a corpus carrying both states."""
    w, lg = RT.corpus(name)
    frames, states, _wits = VC.full(w, lg)
    n = 0
    for t in range(len(frames) - 1):
        flat = VC.resume(w, VC.snapshot(w, frames, t), lg)
        mld = resume(w, mint(w, frames, states, t), lg)
        if flat[0] != mld[0] or VC.witness_stream(flat[2]) != VC.witness_stream(mld[2]):
            return (False, n)
        n += 1
    return (n > 0, n)


def the_shape_is_derived_not_tagged(name="jump"):
    """NO SLOT CARRIES A TAG, checked against the record's own structure rather than promised: a
    slot is exactly 3 or 4 INTEGERS and nothing else, and its state is recovered from the world.
    A tag would cost one value per actor and `vy` costs one value per actor, so a tagged record
    saves nothing and has a second thing to keep consistent."""
    w, lg = RT.corpus(name)
    frames, states, _wits = VC.full(w, lg)
    for t in range(len(frames) - 1):
        _tick, slots, _rev = mint(w, frames, states, t)
        for i, slot in enumerate(slots):
            if len(slot) not in (3, 4) or not all(isinstance(v, int) for v in slot):
                return False
            if derived_state(w, slot) != states[t][i]:
                return False
    return True


def a_mis_shaped_slot_refuses(name="jump"):
    """Structural, not advisory: a grounded slot carrying a fourth integer, and an airborne slot
    missing one, must BOTH refuse. Non-vacuous — the correctly shaped record admits."""
    w, lg = RT.corpus(name)
    frames, states, _wits = VC.full(w, lg)
    gt = next(t for t in range(len(frames) - 1) if states[t][0] in CT.SUPPORTED_STATES)
    at = next(t for t in range(len(frames) - 1) if states[t][0] == CT.AIRBORNE)
    caught = 0
    for rec in ((gt, tuple(s + (7,) for s in mint(w, frames, states, gt)[1]), w["revision"]),
                (at, tuple(s[:3] for s in mint(w, frames, states, at)[1]), w["revision"])):
        try:
            admit(w, rec)
        except MouldError:
            caught += 1
    admit(w, mint(w, frames, states, gt))
    admit(w, mint(w, frames, states, at))
    return caught == 2


def an_all_grounded_mould_is_lossy(name="jump"):
    """The neighbour that is smaller and WRONG, built so "it stays correct" is proved against the
    thing that would violate it.

    AND IT IS CAUGHT BY REFUSAL RATHER THAN BY DIVERGENCE, which is the stronger outcome and the
    one that makes this a TYPE. Minting a 3-integer slot for an airborne actor produces a record
    whose derived state wants four, so the shape CONTRADICTS THE WORLD and the record cannot be
    read at all — there is no lossy replay to compare, because there is no replay. A policy would
    have produced a smaller record that silently resumed wrong; a shape produces one that cannot be
    opened. Returns (caught, tick, mechanism)."""
    w, lg = RT.corpus(name)
    frames, states, _wits = VC.full(w, lg)
    for t in range(len(frames) - 1):
        if states[t][0] != CT.AIRBORNE:
            continue
        flat = VC.resume(w, VC.snapshot(w, frames, t), lg)
        try:
            bad = resume(w, mint_all_grounded(w, frames, t), lg)
        except MouldError:
            return (True, t, "REFUSED")           # the shape contradicts the world
        if bad[0] != flat[0]:
            return (True, t, "DIVERGED")
    return (False, -1, "")


def an_all_airborne_mould_saves_nothing(name="jump"):
    """The neighbour that is correct and POINTLESS, built so "it saves something" is proved against
    the thing that would violate it."""
    c = saving_census(name)
    w, lg = RT.corpus(name)
    frames, _s, _wt = VC.full(w, lg)
    allair = sum(ints_stored(mint_all_airborne(w, frames, t)) for t in range(len(frames) - 1))
    return allair == c["flat_ints"] and c["saved_ints"] > 0


def the_shapes_come_from_retain():
    """Imported rather than restated, and checked: this module's shape for each state IS
    `retain.retained_fields`, so a change to the measurement moves the mould instead of leaving a
    private copy behind."""
    return (mould_for(CT.TERRAIN_GROUNDED) == RT.retained_fields(CT.TERRAIN_GROUNDED)
            and mould_for(CT.AIRBORNE) == RT.retained_fields(CT.AIRBORNE)
            and slot_length(CT.TERRAIN_GROUNDED) == 3 and slot_length(CT.AIRBORNE) == 4)


def the_unproduced_state_has_no_mould():
    """`GEOMETRY_SUPPORTED` is declared and has no producer, so `retain` never observed it and this
    module REFUSES to invent a shape for it — the reserved distinction `contact` made, kept."""
    try:
        mould_for(CT.GEOMETRY_SUPPORTED)
        return False
    except MouldError as exc:
        return "measurement nobody made" in str(exc)


# ---- scenes -----------------------------------------------------------------------------------------
SCENES = ("saving", "equivalence", "neighbours")


def scene_case(name):
    if name == "saving":
        return str(sorted(saving_census().items()))
    if name == "equivalence":
        holds, n = the_mould_resumes_identically()
        w, lg = RT.corpus("jump")
        frames, states, _wt = VC.full(w, lg)
        return "%s|%d|%s" % (holds, n, record_digest(mint(w, frames, states, 0)))
    if name == "neighbours":
        lossy, tick, how = an_all_grounded_mould_is_lossy()
        return "lossy=%s@%d/%s|pointless=%s|derived=%s|refuses=%s" % (
            lossy, tick, how, an_all_airborne_mould_saves_nothing(),
            the_shape_is_derived_not_tagged(), a_mis_shaped_slot_refuses())
    raise MouldError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def mould_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_mould.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MouldError(f"no golden named {name!r}")


if __name__ == "__main__":
    print("shapes from retain     :", the_shapes_come_from_retain(),
          mould_for(CT.TERRAIN_GROUNDED), mould_for(CT.AIRBORNE))
    print("unproduced has no mould:", the_unproduced_state_has_no_mould())
    print("saving census          :", saving_census())
    print("resumes identically    :", the_mould_resumes_identically())
    print("derived, not tagged    :", the_shape_is_derived_not_tagged())
    print("mis-shaped refuses     :", a_mis_shaped_slot_refuses())
    print("all-grounded is lossy  :", an_all_grounded_mould_is_lossy())
    print("all-airborne pointless :", an_all_airborne_mould_saves_nothing())
    for n in SCENES:
        print(n, scene_result(n))
    print("mould", mould_digest())
