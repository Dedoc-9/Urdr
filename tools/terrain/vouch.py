# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""vouch — CAN ROLLBACK REPRODUCE THE EXACT REASON THE ACTOR WAS GROUNDED (URDRVCH1).

`contact` made support a state with a WITNESS: (source, cell, terrain revision, contact height).
`stride` consumed it and proved the witness does not STEER. Neither asked the question that turns a
geometry contract into a replay certificate: given the same snapshot and the same inputs, does a
resumed run reproduce the same REASON — not merely the same position?

WHY RE-RUNNING IS NOT THE ANSWER, and this is the whole design. `stride.simulate` is a pure function
of (world, log), so replaying it from the start and asserting equality restates purity and proves
nothing (L23). The claim only has content when the run RESUMES FROM A MID-TRAJECTORY SNAPSHOT: the
witnesses from tick k onward must equal the full run's, which is false the moment the snapshot omits
anything the witness depends on. This is `splice`'s resumability discipline applied to the reason
rather than to the position, and it fails exactly where a boolean `grounded` would have hidden the
loss.

A DIVERGENCE REPORT THAT NAMES A CELL, WHICH IS THE CAPABILITY THIS ADDS. `lockstep.first_desync`
localizes a chain divergence to a TICK — the strongest thing a digest chain can say, because a
digest has no parts. A witness has parts. `first_witness_divergence` returns the tick, the actor,
and BOTH witnesses, so a desync report reads "at tick 7 actor 0 was grounded at cell (30, 30) under
revision rev-0 and the replay had rev-1" instead of "the chains differ at tick 7". The reason is the
payload, and it was already being computed.

FOUR PERTURBATIONS, AND ONE OF THEM MUST NOT BITE. Changing the terrain revision, the cell, or the
contact height must each move the witness stream. Moving an event to a DIFFERENT TICK must move it
too. But REORDERED DELIVERY of the same logical log must NOT — that is `lockstep.canon`'s absorption
arriving here unchanged, and a rung that only checked the four divergences would be certifying a
witness stream that changed whenever anything did.

THE STALE SNAPSHOT REFUSES RATHER THAN DIVERGING. A snapshot authored against one terrain revision
and resumed against another is not a replay that disagrees; it is a replay that was never entitled
to run. `resurrect` established that law for durable actors and `contact`'s docstring promised it
would arrive at the contact seam for free — here it is exercised rather than promised, and the
refusal is TYPED so a caller cannot read it as a divergence.

GRADE (honest, D5): MEASURED — the mid-trajectory resume is checked to reproduce the witness stream
exactly at every tick of a real jump; each perturbation is checked to move it and delivery reorder
is checked not to; the divergence is checked to LOCALIZE to the perturbed tick and to carry the
witnesses that explain it; the stale snapshot is checked to refuse in both directions. DECLARED:
that a reproduced witness is a CORRECT one — this certifies agreement between two runs, never that
either read the terrain right. `does_not_show`: durability (nothing here writes bytes to disk;
`persist`/`resurrect` own that and this composes with their law rather than replacing it); that
witness equality implies position equality or the converse — both are checked separately here
precisely because a rung that fused them could not tell which had moved."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                        # noqa: E402
import lockstep as L                                        # noqa: E402
import stride as SR                                         # noqa: E402

MAGIC = b"URDRVCH1"


class VouchError(Exception):
    def __init__(self, message):
        super().__init__(f"VOUCH-REFUSE: {message}")
        self.code = "VOUCH-REFUSE"


# ---- the snapshot ------------------------------------------------------------------------------
def snapshot(world, frames, tick):
    """The state a resume needs, and NOTHING ELSE — so an omission is a failure rather than a
    convenience. `(tick, ((x, y, z, vy), ...), revision)`: the revision is IN the record because a
    replay against a different world is a different question, not a different answer."""
    if not (0 <= tick < len(frames)):
        raise VouchError(f"tick {tick} is outside the recorded trajectory [0, {len(frames)})")
    return (int(tick), tuple(tuple(int(c) for c in a) for a in frames[tick]),
            str(world["revision"]))


def snapshot_digest(snap):
    return hashlib.sha256(MAGIC + repr(snap).encode()).hexdigest()


def admit_resume(world, snap):
    """THE DOOR. A snapshot authored against another revision is REFUSED, not rebased and not
    silently replayed — a replay that was never entitled to run is a different thing from a replay
    that disagrees, and fusing them would report an authority error as a desync."""
    try:
        tick, actors, revision = snap
    except (TypeError, ValueError):
        raise VouchError(f"{snap!r} is not a (tick, actors, revision) record")
    if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
        raise VouchError(f"tick {tick!r} is not a non-negative integer")
    if len(actors) != world["n"]:
        raise VouchError(f"the snapshot carries {len(actors)} actors and the world has "
                         f"{world['n']} — a resume that padded or truncated would be inventing "
                         f"state nobody recorded")
    if revision != world["revision"]:
        raise VouchError(f"the snapshot was authored against terrain revision {revision!r} and "
                         f"this world is at {world['revision']!r} — a stale snapshot is REFUSED "
                         f"rather than rebased, and this is NOT a divergence: the replay was never "
                         f"entitled to run")
    return tick


# ---- the resume -------------------------------------------------------------------------------
def resume(world, snap, log):
    """Run forward FROM the snapshot. Returns (frames, states, witnesses) covering ticks
    `snap.tick .. T`, so the slices line up with a full run's tail without any re-indexing."""
    tick = admit_resume(world, snap)
    _t, actors, _rev = snap
    pos = [[a[SR.AX_X], a[SR.AX_Y], a[SR.AX_Z]] for a in actors]
    vy = [a[3] for a in actors]
    by_tick = L.canon(list(log))
    frames, sts, wits = [], [], []
    for t in range(tick + 1, world["T"]):
        st, wt = SR.advance(world, pos, vy, by_tick.get(t, []))
        frames.append(tuple(tuple(p) + (v,) for p, v in zip(pos, vy)))
        sts.append(st)
        wits.append(wt)
    return tuple(frames), tuple(sts), tuple(wits)


def witness_stream(wits):
    """The reasons, as digests — `-` where an actor is airborne and carries none."""
    return tuple(tuple("-" if w is None else CT.witness_digest(w) for w in row) for row in wits)


def stream_digest(wits):
    return hashlib.sha256(MAGIC + b"|W|"
                          + "|".join(",".join(r) for r in witness_stream(wits)).encode()
                          ).hexdigest()


def first_witness_divergence(a, b):
    """THE CAPABILITY THIS RUNG ADDS. `lockstep.first_desync` localizes to a TICK, which is the
    most a digest chain can say because a digest has no parts. A WITNESS has parts, so this returns
    `(tick, actor, witness_a, witness_b)` and a desync report can name the CELL and the REVISION
    that explain it. `None` when the streams agree."""
    for t in range(min(len(a), len(b))):
        for i in range(min(len(a[t]), len(b[t]))):
            if a[t][i] != b[t][i]:
                return (t, i, a[t][i], b[t][i])
    return None if len(a) == len(b) else (min(len(a), len(b)), -1, None, None)


def divergence_report(a, b, base_tick=0):
    """A sentence a human can act on, built from the witness rather than from the tick alone."""
    d = first_witness_divergence(a, b)
    if d is None:
        return "the reasons agree"
    t, i, wa, wb = d
    if i < 0:
        return "the streams have different lengths at tick %d" % (base_tick + t)
    return ("at tick %d actor %d: %s vs %s"
            % (base_tick + t, i,
               "AIRBORNE" if wa is None else "grounded at cell (%d, %d) under %r at height %d"
               % (wa[1], wa[2], wa[3], wa[4]),
               "AIRBORNE" if wb is None else "grounded at cell (%d, %d) under %r at height %d"
               % (wb[1], wb[2], wb[3], wb[4])))


# ---- the fixture -------------------------------------------------------------------------------
def demo(revision="rev-0"):
    """A jump on a small pinned field, so the arc contains grounded ticks (which carry witnesses)
    AND airborne ticks (which carry none) — a stream of one kind would make every comparison
    below vacuous.


    THE SECOND STEP IS DELIBERATELY ON A GROUNDED TICK. The first fixture put it at tick 5, which
    is mid-flight, and `stride` correctly refuses air control — so moving that event to another
    tick changed nothing and the `event_tick` clause read INERT. A perturbation that cannot reach
    the law it is aimed at is a green result with no content, and the fixture was the defect."""
    w = SR.world(CT._demo_field(8, 5), [(2, 2)], revision=revision, T=16)
    return w, [SR.event(0, 0, 0, 0, "E", 1), SR.event(10, 0, 10, 0, "E", 0)]


def full(world, log):
    return SR.simulate(world, log)


# ---- the laws ----------------------------------------------------------------------------------
def the_resume_reproduces_the_reasons(world=None, log=None, at=None):
    """THE LAW, and it has content only because the resume starts MID-TRAJECTORY. Replaying from
    the start would restate that `simulate` is a pure function (L23); resuming from tick k fails
    the moment the snapshot omits anything a witness depends on.

    Checked at EVERY tick of the arc, not one, so a snapshot that happened to be sufficient at a
    convenient moment cannot pass. Returns (holds, ticks_checked)."""
    w, lg = demo() if world is None else (world, log)
    frames, _sts, wits = full(w, lg)
    ticks = range(len(frames) - 1) if at is None else (at,)
    n = 0
    for k in ticks:
        _f, _s, rw = resume(w, snapshot(w, frames, k), lg)
        if witness_stream(rw) != witness_stream(wits[k + 1:]):
            return (False, n)
        n += 1
    return (n > 0, n)


def the_positions_and_the_reasons_are_checked_apart(world=None, log=None, at=3):
    """A rung that fused them could not say which had moved. Both are asserted, separately, and a
    stream carrying BOTH grounded and airborne ticks is required — one kind throughout would make
    every comparison here vacuous (L61)."""
    w, lg = demo() if world is None else (world, log)
    frames, sts, wits = full(w, lg)
    rf, _rs, rw = resume(w, snapshot(w, frames, at), lg)
    kinds = {("-" if x == "-" else "W") for row in witness_stream(wits) for x in row}
    return (rf == frames[at + 1:] and witness_stream(rw) == witness_stream(wits[at + 1:])
            and kinds == {"-", "W"})


# ---- the perturbations --------------------------------------------------------------------------
def perturb_revision(snap, other="rev-9"):
    return (snap[0], snap[1], other)


def perturb_cell(snap, actor=0, dx=1):
    a = list(snap[1])
    v = list(a[actor])
    v[SR.AX_X] += dx
    a[actor] = tuple(v)
    return (snap[0], tuple(a), snap[2])


def perturb_height(snap, actor=0, dy=1):
    a = list(snap[1])
    v = list(a[actor])
    v[SR.AX_Y] += dy
    a[actor] = tuple(v)
    return (snap[0], tuple(a), snap[2])


def the_perturbations_bite(at=2):
    """FOUR MUST MOVE THE REASONS AND ONE MUST NOT.

    A changed CELL and a changed contact HEIGHT move the witness stream; a moved event TICK moves
    it; and a changed REVISION does not merely move it, it REFUSES — a stale snapshot was never
    entitled to run, which is a different finding from a replay that disagrees. But REORDERED
    DELIVERY of the same logical log must NOT move anything: `lockstep.canon`'s absorption arrives
    here unchanged, and a rung that checked only the divergences would be certifying a witness
    stream that changed whenever anything did.

    Returns a dict of verdicts, so a reader sees WHICH clause held rather than one boolean."""
    w, lg = demo()
    frames, _s, _wt = full(w, lg)
    snap = snapshot(w, frames, at)
    base = witness_stream(resume(w, snap, lg)[2])
    out = {}
    try:
        resume(w, perturb_revision(snap), lg)
        out["revision"] = "ADMITTED"                    # a stale snapshot ran: the door is open
    except VouchError as exc:
        out["revision"] = "REFUSED" if "stale snapshot" in str(exc) else "REFUSED-OTHER"
    out["cell"] = ("moved" if witness_stream(resume(w, perturb_cell(snap), lg)[2]) != base
                   else "inert")
    out["height"] = ("moved" if witness_stream(resume(w, perturb_height(snap), lg)[2]) != base
                     else "inert")
    moved = L.move_event_tick(lg, 1, lg[1][0] + 2)
    out["event_tick"] = ("moved" if witness_stream(resume(w, snap, moved)[2]) != base else "inert")
    out["delivery_reorder"] = ("absorbed"
                               if witness_stream(resume(w, snap, L.reorder_delivery(lg))[2]) == base
                               else "leaked")
    out["delivery_duplicate"] = ("absorbed"
                                 if witness_stream(
                                     resume(w, snap, L.duplicate_delivery(lg))[2]) == base
                                 else "leaked")
    return out


def the_perturbation_verdicts_hold(at=2):
    v = the_perturbations_bite(at)
    return (v["revision"] == "REFUSED" and v["cell"] == "moved" and v["height"] == "moved"
            and v["event_tick"] == "moved" and v["delivery_reorder"] == "absorbed"
            and v["delivery_duplicate"] == "absorbed")


def the_divergence_localizes(at=2):
    """AND IT NAMES A CELL. A perturbation at the resume tick must be reported at the FIRST tick it
    changed a reason, with both witnesses attached — a desync report that says which cell and which
    revision, rather than which tick. Returns (tick, report)."""
    w, lg = demo()
    frames, _s, _wt = full(w, lg)
    snap = snapshot(w, frames, at)
    base = witness_stream(resume(w, snap, lg)[2])
    bad = witness_stream(resume(w, perturb_cell(snap), lg)[2])
    d = first_witness_divergence(base, bad)
    _fb, _sb, wb = resume(w, snap, lg)
    _fc, _sc, wc = resume(w, perturb_cell(snap), lg)
    return (d, divergence_report(wb, wc, base_tick=at + 1))


def a_clean_resume_does_not_diverge(at=2):
    """NON-VACUITY: the detector must be silent on an honest replay, or every verdict above is a
    checker that always fires."""
    w, lg = demo()
    frames, _s, _wt = full(w, lg)
    snap = snapshot(w, frames, at)
    a = witness_stream(resume(w, snap, lg)[2])
    b = witness_stream(resume(w, snap, L.reorder_delivery(lg))[2])
    _f, _s2, wa = resume(w, snap, lg)
    return (first_witness_divergence(a, b) is None
            and divergence_report(wa, wa) == "the reasons agree")


def the_stale_snapshot_refuses_both_ways():
    """The composition with `resurrect`'s law, in BOTH directions: a snapshot from another revision
    refuses, and the SAME snapshot against its own world resumes green. One direction alone would
    be a door that is always shut."""
    w, lg = demo("rev-0")
    frames, _s, _wt = full(w, lg)
    snap = snapshot(w, frames, 3)
    other, _lg2 = demo("rev-1")
    try:
        resume(other, snap, lg)
        return False
    except VouchError as exc:
        if "stale snapshot" not in str(exc):
            return False
    return len(resume(w, snap, lg)[0]) == w["T"] - 4


# ---- scenes --------------------------------------------------------------------------------------
SCENES = ("resume", "perturbations", "localization")


def scene_case(name):
    if name == "resume":
        w, lg = demo()
        frames, _s, wits = full(w, lg)
        holds, n = the_resume_reproduces_the_reasons()
        return "%s|%d|%s" % (holds, n, stream_digest(wits))
    if name == "perturbations":
        return "|".join("%s=%s" % kv for kv in sorted(the_perturbations_bite().items()))
    if name == "localization":
        d, report = the_divergence_localizes()
        return "%s|%s" % (d, report)
    raise VouchError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def vouch_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_vouch.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VouchError(f"no golden named {name!r}")


if __name__ == "__main__":
    w, lg = demo()
    frames, sts, wits = full(w, lg)
    print("arc:", " ".join(s[0][0] for s in sts))
    print("resume reproduces the reasons:", the_resume_reproduces_the_reasons())
    print("positions and reasons apart :", the_positions_and_the_reasons_are_checked_apart())
    print("perturbations:", the_perturbations_bite())
    print("verdicts hold:", the_perturbation_verdicts_hold())
    d, report = the_divergence_localizes()
    print("localizes to:", d[:2], "\n  ", report)
    print("clean resume silent:", a_clean_resume_does_not_diverge())
    print("stale refuses both ways:", the_stale_snapshot_refuses_both_ways())
    for n in SCENES:
        print(n, scene_result(n))
    print("vouch", vouch_digest())
