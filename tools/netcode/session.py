# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""session — MEMBERSHIP IS A PROPERTY OF THE EVENT, NOT OF THE ROOM (URDRSES1): the Stage 5
SESSION law `compose` declared as its successor, built on a peer set that CHANGES. NO NEW GLYPH
BELOW THE INTERFACE LINE — `Session` is `worldpeer.WorldPeer` with ONE precondition added.

WHAT `compose` LEFT OPEN. Its closing sentence names the successor exactly: "one persistent world
standing on all the slices at once, with actors joining and leaving, which is where concurrency
finally enters and is NOT claimed here." Every slice below is already proved — `authinput` decides
who may write, `rollback` decides what a late input does to time, `worldstep` decides what a tick
means, `worldpeer` composes those three over an authored world. What NONE of them has is a peer set
that changes while the world runs, and the moment it changes there is a new question that none of
them was ever asked.

THE QUESTION, AND IT HAS EXACTLY TWO ANSWERS.

    An event arrives from a peer who WAS a member when the event happened and is NOT one now.

Either membership is evaluated at the EVENT'S tick, or it is evaluated at the RECEIVER'S head. Both
are implementable, both are defensible in prose, and they are not two policies. **One of them is not
a policy at all.** Evaluated at the head, admission depends on WHEN THE ENVELOPE HAPPENED TO ARRIVE,
so two conforming peers holding the identical event set land on different worlds — the composed N5
sentence ("either CONVERGES to the identical witness chain or produces the SAME TYPED REFUSAL")
fails, and it fails silently, because each peer is internally consistent and neither has anything to
compare against.

MEASURED, over one world and four delivery schedules carrying the identical eleven envelopes:

    membership at the EVENT tick     1 distinct chain   == the batch oracle
    membership at the HEAD           3 distinct chains  != the batch oracle

The oracle is INDEPENDENT: `worldstep.simulate` on the calendar-filtered log, a batch simulator that
knows nothing about sessions, rollback or delivery order. The live session, driven out of order
through 22 rollbacks, reproduces it exactly.

THE SECOND WRONG DESIGN LANDS ON THE FIRST WRONG WORLD. Departure can also be implemented by
striking the peer from the ROSTER when its interval ends — a natural move, since the roster is the
thing that says who may write. Measured: it produces the SAME THREE CHAINS as the head-time defect,
digest for digest, on the same schedules. Two designs reached from different intuitions make ONE
mistake, and the only thing that tells them apart is the typed refusal — AUTH-REFUSE from the
eviction, SESSION-REFUSE from the head-time test, on the same events, with the same world. That is
the sharpest argument for typed refusals this tree has measured: the codes carry the information the
state does not. THE ROSTER AND THE CALENDAR ANSWER DIFFERENT QUESTIONS AND CANNOT BE MERGED — a
departed peer's signature must still verify, or the session's own history stops being checkable.

THE ADMITTED SET IS LOAD-BEARING IN BOTH DIRECTIONS IN TIME, AND ONLY ONE DIRECTION IS EASY TO SEE.
The session's resumable state must carry `known`, the admitted-event set. Dropping it from a
snapshot is a hidden-state defect, and the segmentation sweep prices its exposure:

    cuts where an admitted event is still QUEUED (tick >= head)   10 of 10 diverge
    cuts where every admitted event has already been APPLIED       9 of 43 diverge

Forward it is certain; backward it is contingent on a later rollback reaching past the cut. A suite
built on late deliveries alone — the schedule that LOOKS like the interesting one — would meet the
defect at roughly one cut in five. `sample != universal`, priced rather than asserted.

WHAT THE SNAPSHOT MUST CARRY IS DERIVED, NOT REMEMBERED. `RESUMABLE | CONFIGURATION` must equal the
`self.X` assignments of `WorldPeer.__init__` AND `Session.__init__` read from the AST — the closure
shape `exempt` uses for briefs, applied to session state, and reaching ACROSS the inheritance seam so
a field added to the base class reddens here. It is not decorative: `pos`, `vel`, `K` and `H` are
assigned ONLY through tuple targets, so the naive `node.targets[0].attr` walk finds neither of the
two fields the whole law is about. That is proved as a property rather than avoided by care.

GRADE (honest, D5). MEASURED: convergence of four schedules to an independent batch oracle (1
distinct chain, 22 rollbacks, 0 refusals); both defect arms, their chain counts and their agreement
with each other; the departed-peer census (5 in-window deliveries arriving after their peer left, so
the sharp case is exercised rather than hypothetical); segmentation over every cut of every schedule
(0 of 53); three plants with distinct failure modes and their exposure counts; the state-population
closure and its tuple-target trap; determinism. DECLARED: one world, one calendar, three peers — one
permanent member, two late joins, one departure — a corpus, not a proof, the same asymmetry
`compose` and `inputset` state
for the same reason. does_not_show: that a peer is a BODY — `w["n"]` is fixed and a peer AUTHORS
inputs to a fixed body set, so joining is not spawning and this rung says nothing about structural
resize; that the CALENDAR is agreed — it is pre-session common knowledge exactly as the roster is,
and a calendar distributed at runtime is a consensus problem not touched here; that convergence
survives the rollback horizon — it does NOT, and the witness is exhibited rather than hidden
(`the_horizon_bounds_the_convergence_claim`): the same event set under a past-horizon schedule
ROLLBACK-REFUSES three events that every in-horizon schedule admits. D12's composed sentence was
conditional on a delivery-schedule property it did not name and NOW NAMES IT — the erratum of
2026-09-11 states the horizon condition and cites this rung's `session-horizon` row as the witness,
and `urdr-netcode-rollback 0.1` §2 had carried the condition exactly all along ("the admitted chain
is identical for every K, H — only the refusal horizon moves"), which is what makes this a qualifier
dropped while composing rather than a new constraint; that peers CONTEST a body — each peer here
drives its own."""
import ast
import hashlib
import inspect
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
_sys.path.insert(0, _os.path.join(_HERE, "..", "physics"))

import authinput as _A                                          # noqa: E402
import lockstep as _L                                           # noqa: E402
import worldpeer as _WP                                         # noqa: E402
import worldstep as _WS                                         # noqa: E402
from rollback import RollbackError                              # noqa: E402

MAGIC = b"URDRSES1"


class SessionError(Exception):
    def __init__(self, message):
        super().__init__(f"SESSION-REFUSE: {message}")
        self.code = "SESSION-REFUSE"


#: THE CALENDAR: (peer, join tick, leave tick), half-open. Peer 0 is present throughout, peer 1
#: joins late and LEAVES, peer 2 joins later and stays — so the corpus carries a join, a departure
#: and a permanent member rather than one shape three times.
CALENDAR = ((0, 0, 120), (1, 8, 64), (2, 40, 120))

#: Events INSIDE their author's interval. One identity per (peer, seq): the Lamport signature is
#: one-time, so this is structural rather than tidy.
IN_WINDOW = (
    (3, 0, 0, 0, 2, 0), (10, 1, 0, 1, -2, 0), (30, 1, 1, 1, 0, 3),
    (45, 2, 0, 2, 3, -2), (50, 0, 1, 0, 0, -4), (60, 1, 2, 1, 4, 0),
    (80, 2, 1, 2, -3, 0), (90, 0, 2, 0, -2, 2),
)
#: Events OUTSIDE it — before a join, after a departure, before a later join. These must refuse at
#: the calendar, and the refusal must not depend on when they arrive either.
OUT_OF_WINDOW = ((2, 1, 3, 1, 5, 0), (70, 1, 4, 1, 5, 0), (20, 2, 2, 2, 5, 0))
EVENTS = IN_WINDOW + OUT_OF_WINDOW

K_CADENCE = 4
H_HORIZON = 16


def member_at(calendar, peer, tick):
    """THE WHOLE LAW, and it takes a TICK rather than a session — a function of the event and the
    calendar, of nothing else, which is exactly why it converges."""
    for p, join, leave in calendar:
        if p == peer:
            return join <= tick < leave
    return False


class Session(_WP.WorldPeer):
    """A `WorldPeer` whose right to write is a CALENDAR rather than a standing roster.

    EVERYTHING BELOW THE MEMBERSHIP QUESTION IS INHERITED, NOT TRANSCRIBED. `deliver_envelope` is
    the base class's, unchanged, so authentication still runs first and the world's own admission
    still runs after it; the calendar plugs into `_admit`, which is the seam the time law already
    entered through. A session that reimplemented admission would be grading its own copy."""

    def __init__(self, w, roster, expected_pin, calendar, K=K_CADENCE, H=H_HORIZON):
        self.calendar = tuple(tuple(r) for r in calendar)
        super().__init__(w, roster, expected_pin, K, H)

    def member_at(self, peer, tick):
        return member_at(self.calendar, peer, tick)

    def _gate(self, e, when):
        """The precondition, with the evaluation instant as an ARGUMENT so the law and its defect
        differ by one expression and cannot differ by anything else."""
        if not self.member_at(e[1], when):
            raise SessionError(
                f"peer {e[1]} is not a member at tick {when} "
                f"(calendar {self.calendar})")
        return _WP.WorldPeer._admit(self, e)

    def _admit(self, e):
        return self._gate(e, e[0])


class HeadTimeSession(Session):
    """THE DEFECT, and it is not a weakened implementation. It is `Session` with the evaluation
    instant moved from the event to the receiver — one expression, proved to be the only difference
    by `the_defect_differs_by_one_expression`. Must fail convergence."""

    def _admit(self, e):
        return self._gate(e, self.head)


# ---- what a resumable session must carry ---------------------------------------------------------
#: DERIVED, not remembered: `RESUMABLE | CONFIGURATION` must EQUAL the `self.X` assignments of the
#: two `__init__` bodies. A field added to either class and to neither tuple reddens.
RESUMABLE = ("frames", "head", "known", "pos", "snapshots", "vel")
CONFIGURATION = {
    "w": "the authored world — pinned by URDRWPN1 and supplied identically on both sides",
    "roster": "the key commitment — pre-session, immutable, and NOT the calendar",
    "calendar": "the membership schedule — pre-session common knowledge, like the roster",
    "K": "snapshot cadence — a construction parameter, not state",
    "H": "rollback horizon — a construction parameter, not state",
    "n": "body count — read out of the pinned world, never carried",
}


def _init_targets(cls):
    """Every `self.X` assigned in this class's `__init__`, INCLUDING tuple targets."""
    out = []
    for node in ast.walk(ast.parse(inspect.getsource(cls).lstrip())):
        if not isinstance(node, ast.FunctionDef) or node.name != "__init__":
            continue
        for n in ast.walk(node):
            if not isinstance(n, (ast.Assign, ast.AnnAssign)):
                continue
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            flat = []
            for t in targets:
                flat.extend(t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t])
            for t in flat:
                if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                        and t.value.id == "self" and t.attr not in out):
                    out.append(t.attr)
    return tuple(sorted(out))


def state_population():
    """The population the closure law closes over, read ACROSS the inheritance seam."""
    seen = []
    for cls in (_WP.WorldPeer, Session):
        for name in _init_targets(cls):
            if name not in seen:
                seen.append(name)
    return tuple(sorted(seen))


def the_state_population_is_closed():
    """`RESUMABLE | CONFIGURATION` == the derived population, EXACTLY. Returns
    (closed, population, undeclared, invented)."""
    pop = set(state_population())
    declared = set(RESUMABLE) | set(CONFIGURATION)
    return (pop == declared, len(pop),
            tuple(sorted(pop - declared)), tuple(sorted(declared - pop)))


def tuple_only_targets():
    """Fields assigned ONLY through a tuple target anywhere in the two classes — the ones a
    `node.targets[0].attr` walk silently misses."""
    single, tup = set(), set()
    for cls in (_WP.WorldPeer, Session):
        for n in ast.walk(ast.parse(inspect.getsource(cls).lstrip())):
            if not isinstance(n, ast.Assign):
                continue
            for t in n.targets:
                if isinstance(t, (ast.Tuple, ast.List)):
                    for x in t.elts:
                        if isinstance(x, ast.Attribute):
                            tup.add(x.attr)
                elif isinstance(t, ast.Attribute):
                    single.add(t.attr)
    return tuple(sorted(tup - single))


def the_walk_would_miss_the_fields_the_law_is_about():
    """NON-VACUITY OF THE WALK. `pos`, `vel`, `K` and `H` reach `self` ONLY through tuple targets,
    so a naive walk finds neither of the two fields the session's state IS. Returns
    (tuple_only, all_in_population, state_fields_covered)."""
    only = tuple_only_targets()
    pop = state_population()
    return (only, all(f in pop for f in only),
            "pos" in only and "vel" in only)


# ---- the fixture ----------------------------------------------------------------------------------
_KEYS = {}


def keys_and_roster():
    """One Lamport keypair per (peer, seq), from PUBLISHED seeds — the mechanism is the one-time
    signature, not key secrecy, and `authinput`'s brief says so first."""
    if not _KEYS:
        keys, roster = {}, {}
        for e in EVENTS:
            ident = (e[1], e[2])
            keys[ident] = _A.keygen(_A.fixture_seed(ident[0], ident[1]))
            roster[ident] = _A.roster_pin(_A.pubkey_bytes(keys[ident]))
        _KEYS["keys"], _KEYS["roster"] = keys, roster
    return _KEYS["keys"], _KEYS["roster"]


def admissible_log():
    """The log the calendar admits — the ORACLE's input, filtered by nothing but `member_at`."""
    return [e for e in EVENTS if member_at(CALENDAR, e[1], e[0])]


def oracle_trace():
    """THE INDEPENDENT ORACLE: `worldstep.simulate` in batch on the calendar-filtered log. It knows
    nothing about sessions, delivery order, rollback or membership — which is what makes it one."""
    return _L.trace_digest(_WS.simulate(_WS.arena_world(), admissible_log()))


def _advance(t):
    return ("advance", t)


def _deliver(i):
    return ("deliver", i)


#: Four IN-HORIZON schedules over the identical eleven envelopes, plus one that leaves the horizon.
#: `ordered` takes no rollback at all; `departed` delivers peer 1's in-window events after peer 1
#: has left, which is the case this rung exists for.
SCHEDULES = {
    "ordered": (_deliver(0), _advance(8), _deliver(1), _advance(28), _deliver(2),
                _advance(44), _deliver(3), _advance(48), _deliver(4), _advance(58),
                _deliver(5), _advance(78), _deliver(6), _advance(88), _deliver(7),
                _advance(120)),
    "late": (_advance(12), _deliver(0), _deliver(1), _advance(34), _deliver(2),
             _advance(50), _deliver(3), _deliver(4), _advance(64), _deliver(5),
             _advance(84), _deliver(6), _advance(96), _deliver(7), _advance(120)),
    "departed": (_advance(40), _deliver(0), _deliver(3), _advance(70), _deliver(1),
                 _deliver(2), _deliver(5), _advance(84), _deliver(4), _deliver(6),
                 _advance(110), _deliver(7), _advance(120)),
    "interleaved": (_advance(20), _deliver(1), _deliver(0), _advance(52), _deliver(4),
                    _deliver(2), _advance(66), _deliver(3), _deliver(5), _advance(92),
                    _deliver(7), _deliver(6), _advance(120)),
    "past_horizon": (_advance(96), _deliver(7), _deliver(6), _deliver(5), _deliver(4),
                     _deliver(3), _deliver(2), _deliver(1), _deliver(0), _advance(120)),
}
#: The schedules the convergence law is stated over. `past_horizon` is EXCLUDED and exhibited
#: separately: it is not a counterexample to the law, it is the law's scope boundary.
IN_HORIZON = ("ordered", "late", "departed", "interleaved")


def snapshot(s, drop_known=False, perturb=False, perturb_all=False):
    """The resumable state, and the three plants that damage it. `perturb` moves one word of the
    LIVE state only; `perturb_all` moves it in the retained snapshots too."""
    pos = [list(p) for p in s.pos]
    if perturb or perturb_all:
        pos[0][0] += 1
    snaps = [(t, [list(p) for p in sp], [list(v) for v in sv])
             for (t, sp, sv) in s.snapshots]
    if perturb_all:
        for (_t, sp, _sv) in snaps:
            sp[0][0] += 1
    return {"pos": pos, "vel": [list(v) for v in s.vel], "head": s.head,
            "frames": list(s.frames),
            "known": {} if drop_known else dict(s.known), "snapshots": snaps}


def restore(cls, roster, pin, state):
    s = cls(_WS.arena_world(), roster, pin, CALENDAR, K_CADENCE, H_HORIZON)
    s.pos = [list(p) for p in state["pos"]]
    s.vel = [list(v) for v in state["vel"]]
    s.head = state["head"]
    s.frames = list(state["frames"])
    s.known = dict(state["known"])
    s.snapshots = [(t, [list(p) for p in sp], [list(v) for v in sv])
                   for (t, sp, sv) in state["snapshots"]]
    return s


def _evict(s):
    """DEPARTURE BY ROSTER REMOVAL — the second wrong design, implemented as its author would."""
    for p, _join, leave in s.calendar:
        if s.head >= leave:
            for ident in [k for k in s.roster if k[0] == p]:
                del s.roster[ident]


def run(name, cls=Session, cut=None, evict=False, drop_known=False,
        perturb=False, perturb_all=False):
    """Drive one schedule. Returns (trace, refusals, rollbacks, queued_at_cut)."""
    if name not in SCHEDULES:
        raise SessionError(f"unknown schedule {name!r}")
    keys, roster = keys_and_roster()
    w = _WS.arena_world()
    pin = _WP.world_pin(w)
    s = cls(w, roster, pin, CALENDAR, K_CADENCE, H_HORIZON)
    refusals, rollbacks, queued = [], 0, None
    for i, (kind, arg) in enumerate(SCHEDULES[name]):
        if cut is not None and i == cut:
            queued = sum(1 for e in s.known.values() if e[0] >= s.head)
            s = restore(cls, roster, pin,
                        snapshot(s, drop_known=drop_known, perturb=perturb,
                                 perturb_all=perturb_all))
        if kind == "advance":
            s.advance(arg)
            continue
        e = EVENTS[arg]
        if evict:
            _evict(s)
        try:
            outcome = s.deliver_envelope(_A.envelope(e, keys[(e[1], e[2])]))
            rollbacks += isinstance(outcome, tuple)
        except (SessionError, RollbackError, _A.AuthError) as exc:
            refusals.append((arg, exc.code))
    return s.trace(), tuple(refusals), rollbacks, queued


# ---- the laws -------------------------------------------------------------------------------------
#: The three sweeps below each drive 53 full sessions, and the gate, the scene digests and the
#: falsifiers all read them. Memoized because they are PURE — same inputs, no clock, no environment
#: (`no_wall_clock_enters_this_rung`) — so a cache cannot change an answer, only how often it is
#: computed. `cutpin` pins an expensive proof to a FILE because regenerating its inputs is hostile;
#: this one is affordable once per process, so it is cached in memory and never written down.
_MEMO = {}


def _memo(key, fn):
    if key not in _MEMO:
        _MEMO[key] = fn()
    return _MEMO[key]


def the_convergence_law():
    """THE LAW. The identical envelopes under four delivery schedules must land on ONE chain, and
    that chain must be the batch oracle's. Returns (distinct_chains, equals_oracle, rollbacks,
    refusals)."""
    oracle = oracle_trace()
    seen, rolls, refused = set(), 0, 0
    for name in IN_HORIZON:
        tr, ref, rb, _q = run(name)
        seen.add(tr)
        rolls += rb
        refused += len(ref)
    return len(seen), all(t == oracle for t in seen), rolls, refused


def the_head_time_defect():
    """Membership asked of the HEAD. Returns (distinct_chains, equals_oracle, codes)."""
    oracle = oracle_trace()
    seen, codes = set(), []
    for name in IN_HORIZON:
        tr, ref, _rb, _q = run(name, cls=HeadTimeSession)
        seen.add(tr)
        codes.append((name, tuple(c for _i, c in ref)))
    return len(seen), all(t == oracle for t in seen), tuple(codes)


def the_eviction_defect():
    """Departure by striking the peer from the ROSTER. Returns (distinct_chains, equals_oracle,
    codes)."""
    oracle = oracle_trace()
    seen, codes = set(), []
    for name in IN_HORIZON:
        tr, ref, _rb, _q = run(name, evict=True)
        seen.add(tr)
        codes.append((name, tuple(c for _i, c in ref)))
    return len(seen), all(t == oracle for t in seen), tuple(codes)


def the_two_defects_agree_on_the_world_and_differ_on_the_reason():
    """THE FINDING THAT ARGUES FOR TYPED REFUSALS. Two designs reached from different intuitions
    produce the SAME chain on every schedule and DIFFERENT codes wherever either refuses at all.
    Returns (schedules, chains_equal, codes_differ, codes_silent)."""
    equal = differ = silent = 0
    for name in IN_HORIZON:
        h_tr, h_ref, _r, _q = run(name, cls=HeadTimeSession)
        e_tr, e_ref, _r2, _q2 = run(name, evict=True)
        equal += h_tr == e_tr
        h_codes = tuple(c for _i, c in h_ref)
        e_codes = tuple(c for _i, c in e_ref)
        if not h_codes and not e_codes:
            silent += 1
        elif h_codes != e_codes:
            differ += 1
    return len(IN_HORIZON), equal, differ, silent


def the_departed_peer_census():
    """NON-VACUITY OF THE SHARP CASE. How many deliveries in each schedule carry an IN-WINDOW event
    whose author had already left by the time it arrived. A law about departed peers proved on a
    corpus containing none would be a law about nothing. Returns ((name, count), ...)."""
    out = []
    for name in SCHEDULES:
        head, n = 0, 0
        for kind, arg in SCHEDULES[name]:
            if kind == "advance":
                head = max(head, arg)
                continue
            e = EVENTS[arg]
            if not member_at(CALENDAR, e[1], e[0]):
                continue
            leave = [lv for p, _j, lv in CALENDAR if p == e[1]][0]
            n += head >= leave
        out.append((name, n))
    return tuple(out)


def the_membership_refusals():
    """Every OUT-OF-WINDOW event refuses at the calendar, under every schedule, with SESSION-REFUSE
    — and the refusal does not depend on arrival either. Returns (events, refused, codes)."""
    keys, roster = keys_and_roster()
    w = _WS.arena_world()
    pin = _WP.world_pin(w)
    refused, codes = 0, set()
    for e in OUT_OF_WINDOW:
        for head in (0, 20, 64, 100):
            s = Session(_WS.arena_world(), roster, pin, CALENDAR, K_CADENCE, H_HORIZON)
            s.advance(head)
            try:
                s.deliver_envelope(_A.envelope(e, keys[(e[1], e[2])]))
            except SessionError as exc:
                refused += 1
                codes.add(exc.code)
    return len(OUT_OF_WINDOW) * 4, refused, tuple(sorted(codes))


def the_segmentation_law():
    """Cut a live session after ANY step, snapshot it, resume a FRESH session from the snapshot, and
    the final chain must be unchanged. `compose` proved this over a fixed log; here the log arrives
    out of order, through rollbacks, under a changing peer set. Returns ((name, divergences,
    cuts), ...)."""
    def compute():
        oracle = oracle_trace()
        out = []
        for name in IN_HORIZON:
            cuts = len(SCHEDULES[name]) - 1
            bad = 0
            for c in range(1, cuts + 1):
                if run(name, cut=c)[0] != oracle:
                    bad += 1
            out.append((name, bad, cuts))
        return tuple(out)
    return _memo("segmentation", compute)


def _plant_sweep(**kw):
    oracle = oracle_trace()
    bad = total = 0
    for name in IN_HORIZON:
        cuts = len(SCHEDULES[name]) - 1
        total += cuts
        for c in range(1, cuts + 1):
            if run(name, cut=c, **kw)[0] != oracle:
                bad += 1
    return bad, total


def the_plants():
    """THREE PLANTS, NO TWO SHARING A FAILURE MODE.

      drop_known    the admitted set is dropped from the snapshot — the hidden-state defect the
                    law exists to catch, and the one whose exposure is CONTINGENT.
      perturb_live  one word of the live state is moved, the retained snapshots left alone — so the
                    plant is ERASED wherever a later rollback restores from one of them, and the
                    bite rate measures exactly that.
      perturb_all   the same word moved in the live state AND every retained snapshot — nothing can
                    erase it, so a comparison sensitive to what it compares must bite EVERYWHERE.

    Returns ((name, divergences, cuts), ...)."""
    return _memo("plants", _compute_plants)


def _compute_plants():
    return (("drop_known",) + _plant_sweep(drop_known=True),
            ("perturb_live",) + _plant_sweep(perturb=True),
            ("perturb_all",) + _plant_sweep(perturb_all=True))


def the_admitted_set_is_load_bearing_in_both_directions():
    """`known` holds the pending FUTURE and the replayable PAST, and the two are exposed at wildly
    different rates. A cut with an admitted event still QUEUED loses it outright; a cut where every
    admitted event has already been applied only diverges if a LATER rollback reaches past the cut.
    Returns (queued_bad, queued_cuts, applied_bad, applied_cuts)."""
    def compute():
        oracle = oracle_trace()
        qb = qt = ab = at = 0
        for name in IN_HORIZON:
            for c in range(1, len(SCHEDULES[name])):
                tr, _ref, _rb, queued = run(name, cut=c, drop_known=True)
                if queued:
                    qt += 1
                    qb += tr != oracle
                else:
                    at += 1
                    ab += tr != oracle
        return qb, qt, ab, at
    return _memo("both_directions", compute)


def the_horizon_bounds_the_convergence_claim():
    """THE SCOPE, EXHIBITED RATHER THAN STATED. The same eleven envelopes under a schedule that
    delivers everything from the far end of the run leave the rollback horizon, and three events
    every in-horizon schedule ADMITS are ROLLBACK-REFUSED instead. D12's composed sentence — the
    identical chain OR the same typed refusal — is therefore conditional on a delivery-schedule
    property the sentence does not name. Not a defect: `worldpeer` grades K/H as operational. A
    boundary, with a witness. Returns (admitted_in_horizon, refused_past_horizon, codes,
    chain_differs)."""
    oracle = oracle_trace()
    tr, ref, _rb, _q = run("past_horizon")
    return (len(admissible_log()), len(ref),
            tuple(sorted({c for _i, c in ref})), tr != oracle)


def the_gate_only_adds_a_precondition():
    """`Session._admit` ADDS the calendar and changes nothing else: its body is one statement, and
    that statement delegates. The membership law is a refinement of admission, not a replacement
    for it — proved on the live AST rather than promised."""
    tree = ast.parse(inspect.getsource(Session).lstrip())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_admit":
            return (len(node.body) == 1 and isinstance(node.body[0], ast.Return)
                    and ast.unparse(node.body[0]) == "return self._gate(e, e[0])")
    return False


def the_defect_differs_by_one_expression():
    """ANTI-STRAWMAN. The defect is not a worse implementation — it is THIS implementation with the
    evaluation instant moved. Both `_admit` bodies unparse to `return self._gate(e, X)`, and
    substituting the law's X into the defect's makes them EQUAL. Returns (law, defect, equal)."""
    bodies = {}
    for cls in (Session, HeadTimeSession):
        tree = ast.parse(inspect.getsource(cls).lstrip())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_admit":
                bodies[cls.__name__] = ast.unparse(node.body[0])
    law = bodies.get("Session", "")
    defect = bodies.get("HeadTimeSession", "")
    return (law, defect, defect.replace("self.head", "e[0]") == law and law != defect)


def the_subject_is_untouched():
    """NOTHING BELOW THE INTERFACE LINE MOVED. `Session` inherits `deliver_envelope` rather than
    defining one, and its admission delegates to `WorldPeer._admit` by name."""
    own = {n for n, _v in inspect.getmembers(Session, inspect.isfunction)
           if n in Session.__dict__}
    delegates = "WorldPeer._admit" in inspect.getsource(Session._gate)
    return ("deliver_envelope" not in own and "advance" not in own
            and delegates and own == {"__init__", "member_at", "_gate", "_admit"})


def no_wall_clock_enters_this_rung():
    """No timing call reaches any measurement here — every number is a count or a digest."""
    src = inspect.getsource(_sys.modules[__name__])
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Attribute) and node.attr in (
                "time", "perf_counter", "monotonic", "process_time"):
            return False
    return True


# ---- scenes ---------------------------------------------------------------------------------------
def se_digest(name, payload):
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(b"|" + name.encode() + b"|" + payload.encode())
    return h.hexdigest()


def _scene_converge():
    return se_digest("converge", f"{oracle_trace()}:{the_convergence_law()}:"
                                 f"{the_departed_peer_census()}")


def _scene_defects():
    return se_digest("defects", f"{the_head_time_defect()}:{the_eviction_defect()}:"
                                f"{the_two_defects_agree_on_the_world_and_differ_on_the_reason()}:"
                                f"{the_membership_refusals()}")


def _scene_segment():
    return se_digest("segment", f"{the_segmentation_law()}:{the_plants()}:"
                                f"{the_admitted_set_is_load_bearing_in_both_directions()}")


def _scene_state():
    return se_digest("state", f"{state_population()}:{the_state_population_is_closed()}:"
                              f"{the_walk_would_miss_the_fields_the_law_is_about()}:"
                              f"{the_horizon_bounds_the_convergence_claim()}")


SCENES = ("converge", "defects", "segment", "state")
_SCENES = {"converge": _scene_converge, "defects": _scene_defects,
           "segment": _scene_segment, "state": _scene_state}


def scene_result(name):
    if name not in _SCENES:
        raise SessionError(f"unknown scene {name!r}")
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_session.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                out.append(ln)
    return tuple(out)


def emitted_matches_pinned():
    return conformance_lines() == pinned_lines()


def golden(name):
    for ln in pinned_lines():
        nm, dig = ln.split()
        if nm == name:
            return dig
    raise SessionError(f"no golden named {name!r}")


def _main():
    if "--emit" in _sys.argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    ok = all(scene_result(n) == golden(n) for n in SCENES) and emitted_matches_pinned()
    print("session selfcheck:", "OK" if ok else "MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main())
