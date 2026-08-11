# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""retain — WHAT MUST A SNAPSHOT KEEP FOR A REPLAY TO REPRODUCE THE SAME REASONS (URDRRTN1).

`vouch` proved a mid-trajectory snapshot is SUFFICIENT and caught a lossy one by planting the
removal of the vertical velocity. That answers "is this record enough". It does not answer the
harder question, which is the one with a consequence: WHICH PARTS OF IT ARE DOING THE WORK, and
where.

INERT IS THE VERDICT THAT CAN FAKE A RESULT, and an ablation sweep is exactly where it does. Remove
a field, resume, and get the same tail. There are two readings and they are indistinguishable from
that observation alone:

    the field is genuinely NOT OBSERVED here          a finding
    the fixture never exercised it                    a fake finding

`vouch` met this one level down: its first `event_tick` perturbation was aimed at a mid-flight tick,
`stride` correctly ignores air control, the clause read INERT and proved nothing. A minimization
built on unexamined INERT verdicts produces a snapshot that is smaller and LOSSY, and the loss shows
up as a desync in a session nobody can reproduce. So this module refuses to collapse three outcomes
into two:

    REQUIRED    the perturbation moved the trajectory or the reasons — the field is observed HERE
    REFUSED     the perturbation made the resume REFUSE — an authority error, not a divergence
    INERT       the perturbation moved nothing — WHICH IS A STATEMENT ABOUT THIS TICK, NOT ABOUT
                THE FIELD, and is never read as redundancy

AND THE SHARP RESULT IS THAT TWO FIELDS' NECESSITY IS A FUNCTION OF THE STATE RATHER THAN OF THE
SCHEMA, one of which the design did not anticipate.

`vy` is REQUIRED on every airborne tick and INERT on every grounded one — not by choice but by
`contact`'s own law, which says a supported actor's gravity does not accumulate, so the tick
overwrites it before anything reads it.

`y` is sharper, and the sweep found it rather than the design: REQUIRED exactly when the actor is
AIRBORNE or when the NEXT tick carries a movement intent, INERT otherwise — because a one-unit lift
of a grounded actor is ERASED WITHIN ONE TICK (`contact` reads it as AIRBORNE, gravity takes the
unit back, the actor lands on the ground it left), EXCEPT when a step follows, because `stride`
refuses air control and a momentarily airborne actor does not take it. That is the no-air-control
law appearing in a state-retention sweep, which is not where it was written, and both sets are
CHARACTERIZED — predicted from the contact states and the canonical event ticks, then required to
EQUAL the measured ones — rather than counted.

THE MINIMALITY CLAIM IS GRADED, and the grade is the point. What is measured is minimality WITH
RESPECT TO THIS CORPUS: a field REQUIRED nowhere in a corpus of two fixtures is not proved
redundant, it is proved unobserved by two fixtures, and the census reports that as
`REQUIRED_NOWHERE` rather than as permission to delete it. `sample != universal`, and a snapshot
minimization is exactly the place where forgetting that costs a replay.

NO LATENCY CLAIM. The field counts are COUNTS. A grounded snapshot needs three integers per actor
where an airborne one needs four; whether that is worth anything is a question for a benchmark on a
named host, and nothing here says it is. The arc has declined to optimize without a measured target
five times now and this is the sixth.

GRADE (honest, D5): MEASURED — the per-field, per-tick verdicts over a corpus that carries both
grounded and airborne ticks; the state-dependence of `vy` checked against `contact`'s own state
stream rather than against a tick index; the INERT/REQUIRED separation proved to matter by
exhibiting a grounded-only corpus in which `vy` reads INERT everywhere while being REQUIRED in the
full corpus. DECLARED: minimality, which is with respect to this corpus and says so.
`does_not_show`: that an INERT field is REMOVABLE — that is the whole discipline here; that a
smaller snapshot is a faster one (no wall-clock is measured and none is claimed); that the field set
is complete — it is the set `vouch`'s record carries, and a field nobody stores cannot be ablated."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                        # noqa: E402
import stride as SR                                         # noqa: E402
import vouch as VC                                          # noqa: E402

MAGIC = b"URDRRTN1"

#: The fields a `vouch` record carries. A field nobody stores cannot be ablated, so this list is
#: DERIVED from the record's shape rather than wished for.
FIELDS = ("x", "y", "z", "vy", "revision")

REQUIRED = "REQUIRED"
REFUSED = "REFUSED"
INERT = "INERT"
OUTCOMES = (REQUIRED, REFUSED, INERT)

#: What a REQUIRED verdict moved. Kept apart because `vouch` established that fusing the trajectory
#: and the reasons loses which one changed.
MOVED_TRAJECTORY = "trajectory"
MOVED_REASONS = "reasons"


class RetainError(Exception):
    def __init__(self, message):
        super().__init__(f"RETAIN-REFUSE: {message}")
        self.code = "RETAIN-REFUSE"


def perturb(snap, field, actor=0):
    """Move ONE field by one unit. A perturbation rather than a deletion, because a deleted field
    has no value to resume from and the resulting refusal would be about the record's SHAPE rather
    than about what the law reads."""
    if field not in FIELDS:
        raise RetainError(f"{field!r} is not a field of the record ({', '.join(FIELDS)})")
    tick, actors, revision = snap
    if field == "revision":
        return (tick, actors, revision + "-perturbed")
    a = list(actors)
    v = list(a[actor])
    v[{"x": SR.AX_X, "y": SR.AX_Y, "z": SR.AX_Z, "vy": 3}[field]] += 1
    a[actor] = tuple(v)
    return (tick, tuple(a), revision)


def verdict_at(world, log, frames, tick, field):
    """(outcome, moved) for one field at one tick. `moved` names WHICH of the two streams the
    perturbation reached — trajectory, reasons, both, or neither."""
    snap = VC.snapshot(world, frames, tick)
    try:
        base_f, _bs, base_w = VC.resume(world, snap, log)
    except VC.VouchError as exc:                            # pragma: no cover - fixture guard
        raise RetainError(f"the unperturbed resume refused at tick {tick}: {exc}")
    try:
        f2, _s2, w2 = VC.resume(world, perturb(snap, field), log)
    except VC.VouchError:
        return (REFUSED, ())
    moved = []
    if f2 != base_f:
        moved.append(MOVED_TRAJECTORY)
    if VC.witness_stream(w2) != VC.witness_stream(base_w):
        moved.append(MOVED_REASONS)
    return ((REQUIRED, tuple(moved)) if moved else (INERT, ()))


# ---- the corpora ---------------------------------------------------------------------------------
def jump_corpus(revision="rev-0"):
    """The `vouch` fixture: a jump, so the arc carries BOTH grounded and airborne ticks."""
    return VC.demo(revision)


def grounded_corpus(revision="rev-0"):
    """A WALK WITH NO JUMP — every tick grounded. This exists to make the INERT trap visible: `vy`
    reads INERT at every tick of it, and a minimization run on this corpus alone would delete a
    field that the jump corpus proves is REQUIRED. It is the control that turns 'INERT is not
    redundancy' from a caution into a measurement."""
    w = SR.world(CT._demo_field(8, 5), [(2, 2)], revision=revision, T=12)
    return w, [SR.event(t, 0, t, 0, "E", 0) for t in (1, 3, 5)]


CORPORA = ("jump", "grounded")


def corpus(name):
    if name == "jump":
        return jump_corpus()
    if name == "grounded":
        return grounded_corpus()
    raise RetainError(f"no corpus named {name!r}")


# ---- the census ------------------------------------------------------------------------------------
def census(name="jump"):
    """PER FIELD, PER TICK — never one verdict per field, because the whole finding is that one
    field's answer changes with the tick. Returns {field: {outcome: (ticks...)}} plus the contact
    state at each tick, so a reader can see WHY a verdict changed rather than only that it did."""
    w, lg = corpus(name)
    frames, sts, _wits = VC.full(w, lg)
    out = {f: {o: [] for o in OUTCOMES} for f in FIELDS}
    states = []
    for tick in range(len(frames) - 1):
        states.append(sts[tick][0])
        for f in FIELDS:
            outcome, _moved = verdict_at(w, lg, frames, tick, f)
            out[f][outcome].append(tick)
    return ({f: {o: tuple(v) for o, v in d.items()} for f, d in out.items()}, tuple(states))


def required_somewhere(name="jump"):
    """Which fields the corpus can justify AT ALL. A field REQUIRED nowhere is not proved
    redundant — it is proved unobserved by this corpus, and the two are named differently."""
    c, _s = census(name)
    return tuple(f for f in FIELDS if c[f][REQUIRED] or c[f][REFUSED])


def required_nowhere(name="jump"):
    c, _s = census(name)
    return tuple(f for f in FIELDS if not c[f][REQUIRED] and not c[f][REFUSED])


# ---- the laws -------------------------------------------------------------------------------------
def every_field_is_justified(name="jump"):
    """Every field the record carries must be REQUIRED or REFUSED somewhere in the corpus, or the
    record is carrying something this corpus cannot justify — which is a finding either way."""
    return required_nowhere(name) == ()


def vy_is_required_exactly_on_airborne_ticks(name="jump"):
    """THE SHARP RESULT, and it is checked against `contact`'s OWN STATE STREAM rather than against
    a tick index, so it is a claim about the law and not about this fixture's timing.

    `contact` says a supported actor's gravity does not accumulate — the tick overwrites `vy`
    before anything reads it — so the vertical velocity is load-bearing in the air and inert on the
    ground. The first field in this stack whose retention requirement depends on the STATE rather
    than on the schema. Returns (holds, airborne_ticks, grounded_ticks)."""
    c, states = census(name)
    air = tuple(t for t, s in enumerate(states) if s == CT.AIRBORNE)
    gnd = tuple(t for t, s in enumerate(states) if s in CT.SUPPORTED_STATES)
    holds = (set(c["vy"][REQUIRED]) == set(air) and set(c["vy"][INERT]) == set(gnd)
             and len(air) > 0 and len(gnd) > 0)
    return (holds, air, gnd)


def y_is_required_when_airborne_or_before_a_step(name="jump"):
    """A SECOND STATE-DEPENDENCE THE SWEEP FOUND RATHER THAN THE DESIGN ANTICIPATED, and it is
    sharper than `vy`'s.

    The vertical coordinate is REQUIRED exactly when the actor is airborne OR when the NEXT tick
    carries a movement intent — and INERT otherwise, because a one-unit lift of a grounded actor is
    ERASED WITHIN ONE TICK: `contact` reads it as AIRBORNE, gravity takes one unit back, and the
    actor lands on the same ground it left. The exception is a tick followed by a step, because
    `stride` refuses air control, so a momentarily airborne actor does not take it — the
    no-air-control law showing up in a state-retention sweep, which is not where it was written.

    Characterized rather than counted: the predicted set is built from the contact states and the
    canonical event ticks, and must EQUAL the measured one."""
    import lockstep as _L
    w, lg = corpus(name)
    frames, sts, _wt = VC.full(w, lg)
    by_tick = _L.canon(list(lg))
    predicted = set()
    for tick in range(len(frames) - 1):
        nxt = by_tick.get(tick + 1, [])
        if sts[tick][0] == CT.AIRBORNE or any(e[4] for e in nxt):
            predicted.add(tick)
    c, _s = census(name)
    measured = set(c["y"][REQUIRED])
    return (predicted == measured and bool(predicted) and bool(set(c["y"][INERT])),
            tuple(sorted(predicted)), tuple(sorted(measured)))


def inert_is_not_redundancy():
    """THE DISCIPLINE, MEASURED RATHER THAN CAUTIONED. On the grounded-only corpus `vy` reads INERT
    at EVERY tick — and it is REQUIRED on the jump corpus. A minimization that read INERT as
    permission to delete would have produced a smaller, LOSSY record from a green sweep.

    Returns (holds, inert_everywhere_on_grounded, required_on_jump)."""
    cg, _sg = census("grounded")
    cj, _sj = census("jump")
    inert_all = (len(cg["vy"][INERT]) > 0 and not cg["vy"][REQUIRED] and not cg["vy"][REFUSED])
    needed = bool(cj["vy"][REQUIRED])
    return (inert_all and needed, tuple(cg["vy"][INERT]), tuple(cj["vy"][REQUIRED]))


def the_outcomes_are_populated(name="jump"):
    """L61 on the sweep: a census reading one outcome throughout certifies nothing. All three must
    appear, and REFUSED must be reached only by the revision — an authority error is a different
    kind of finding from a divergence and a sweep that fused them would report one as the other."""
    c, _s = census(name)
    seen = {o for f in FIELDS for o in OUTCOMES if c[f][o]}
    only_revision = all(not c[f][REFUSED] for f in FIELDS if f != "revision") \
        and bool(c["revision"][REFUSED])
    return seen == set(OUTCOMES) and only_revision


def the_perturbation_reaches_both_streams(name="jump"):
    """`vouch` established that the trajectory and the reasons must be checked apart, so this
    reports WHICH of them each REQUIRED verdict moved.

    THE MEASURED ANSWER IS THAT THEY NEVER SEPARATE HERE: every perturbation this corpus admits
    moves BOTH, so this sweep does NOT distinguish a field the trajectory needs from one only the
    reasons need. That is a boundary on the result and it is reported rather than dressed up as
    agreement — a corpus that separated them would say something this one cannot."""
    w, lg = corpus(name)
    frames, _s, _wt = VC.full(w, lg)
    seen = set()
    for tick in range(len(frames) - 1):
        for f in FIELDS:
            outcome, moved = verdict_at(w, lg, frames, tick, f)
            if outcome == REQUIRED:
                seen.add(moved)
    return seen


def retained_fields(state):
    """THE COUNT, AND IT IS A COUNT. Which integers a record must keep for an actor in this contact
    state — three on the ground, four in the air, plus the revision the record carries once. No
    byte figure, no rate, and no claim that a smaller record is a faster one: that is a question for
    a benchmark on a named host and this module does not answer it."""
    if state in CT.SUPPORTED_STATES:
        return ("x", "y", "z")
    if state == CT.AIRBORNE:
        return ("x", "y", "z", "vy")
    raise RetainError(f"{state!r} is not a contact state ({', '.join(CT.STATES)})")


def field_count_by_state(name="jump"):
    _c, states = census(name)
    return {s: len(retained_fields(s)) for s in sorted(set(states))}


# ---- scenes -----------------------------------------------------------------------------------------
SCENES = ("census", "state_dependence", "inert_control")


def scene_case(name):
    if name == "census":
        c, states = census("jump")
        return "|".join("%s:%s" % (f, sorted((o, c[f][o]) for o in OUTCOMES)) for f in FIELDS) \
            + "||" + ",".join(s[0] for s in states)
    if name == "state_dependence":
        holds, air, gnd = vy_is_required_exactly_on_airborne_ticks()
        yh, yp, ym = y_is_required_when_airborne_or_before_a_step()
        return "%s|air%s|gnd%s|%s||y %s|%s|%s" % (holds, air, gnd,
                                                  sorted(field_count_by_state().items()),
                                                  yh, yp, ym)
    if name == "inert_control":
        holds, inert, needed = inert_is_not_redundancy()
        return "%s|inert%s|required%s" % (holds, inert, needed)
    raise RetainError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def retain_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_retain.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RetainError(f"no golden named {name!r}")


if __name__ == "__main__":
    for cname in CORPORA:
        c, states = census(cname)
        print("== %s ==  states: %s" % (cname, " ".join(s[0] for s in states)))
        for f in FIELDS:
            print("   %-9s REQUIRED %-22s INERT %-26s REFUSED %s"
                  % (f, c[f][REQUIRED], c[f][INERT], c[f][REFUSED]))
    print("\nevery field justified :", every_field_is_justified())
    print("vy state-dependent    :", vy_is_required_exactly_on_airborne_ticks())
    print("y  state-dependent    :", y_is_required_when_airborne_or_before_a_step())
    print("INERT is not redundancy:", inert_is_not_redundancy())
    print("outcomes populated    :", the_outcomes_are_populated())
    print("streams reached       :", the_perturbation_reaches_both_streams())
    print("fields by state       :", field_count_by_state())
    for n in SCENES:
        print(n, scene_result(n))
    print("retain", retain_digest())
