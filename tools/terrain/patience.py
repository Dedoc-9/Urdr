# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""patience — THE PRICE OF THE PRICE (URDRPAT1): the timing hypothesis URDRAUD1's ladder was resting
on without saying so, and the exact integer cost of buying it. NO NEW GLYPH.

THE CONTINGENCY, NAMED. `auditgraph` proved that under a committed audit topology the cost of
undetected equivocation is kappa, the vertex connectivity, and sold that as converting an INVISIBLE
INTEGRITY attack into a VISIBLE AVAILABILITY one. Every word of that rests on "visible", and neither
`splitview` nor `auditgraph` established it — both DECLARED it and moved on. This rung asks what
happens when the server does not exclude anybody at all and simply answers late.

    CHANDRA AND TOUEG, 1996: a crashed process cannot be distinguished from a slow one. No failure
    detector in a purely asynchronous system has any accuracy property, because the observation is
    identical.

That is the same indistinguishability argument `splitview` used for the lonely client, turned from
history onto time — and it is fatal here in a way that is worth measuring rather than asserting.

THE STALL COLLAPSE. Let every honest delay lie in [1, Delta] and let a client wait T before calling a
peer silent. A server that wants a partition does not kick anyone: it answers a CUT of the audit
graph at delay T+1. If T < Delta that delay is inside the honest envelope, so it is not merely
undetected, it is a pattern NATURE COULD HAVE PRODUCED. DECIDED over every delay assignment on the
pinned topologies:

    the auditgraph ladder 1 / 2 / INFINITE holds exactly when T >= Delta, and collapses to
    0 / 0 / 0 the moment T < Delta

Not reduced. Zero — because the cost was denominated in EXCLUDED CLIENTS and a stalling server
excludes none. This is the third scope correction in the chain: `splitview` assumed the audit graph
was exogenous, `auditgraph` assumed exclusion was visible, and each was true in its own model.

AND IT RETURNS A QUANTITY THE PREVIOUS RUNG CALLED A DEFECT. `auditgraph` measured two plants that
priced the attack by lambda (edge connectivity) and delta (least degree) and showed both OVER-price
kappa 15 times each. That verdict stands for the question it asked. But a stalling server does not
remove vertices, it silences EDGES, and the number it must silence is exactly lambda. So lambda was
not a wrong piece of graph theory — it was the right answer to a question nobody had posed yet, and
which of kappa or lambda binds is decided by ONE INEQUALITY: T >= Delta or not. That is the whole
ergonomic content of this rung.

THE COST OF BUYING T >= Delta, AS A CLOSED FORM. If Delta is known, set T = Delta and the ladder is
restored at no recurring cost. Under Dwork-Lynch-Stockmeyer partial synchrony a bound EXISTS but is
UNKNOWN, so no fixed T is safe and patience must grow. Doubling from T0 pays

    false_alarms(Delta, T0) = ceil(log2(ceil(Delta / T0)))     [integer: (q - 1).bit_length()]

false alarms, ONCE, and never again — DECIDED against simulation over every (Delta, T0) in the pinned
ranges with 0 exceptions, and computed with integer division and bit_length so no float ever enters
an authority path. Linear growth also terminates and costs ceil(Delta/T0) - 1, which is the same
quantity before the logarithm: at Delta/T0 = 200 that is 199 false alarms against 8. The linear plant
is NOT INCORRECT — it is unaffordable, which is a plant class the repo had not yet needed a name for.

GRADE. MEASURED: the free-move census and its exact vanishing at T = Delta; the ladder collapse to
0/0/0 under stall, cross-checked against `auditgraph`'s own numbers rather than restated; lambda as
the stall-move count against kappa as the exclusion count on the same topologies; the doubling closed
form against simulation, 0 exceptions; the linear/doubling gap; three plants biting; determinism.
DECLARED: delays are integers in [1, Delta] on a static topology and the honest envelope is uniform
over edges — real networks are neither, and a heavy-tailed delay distribution makes the envelope
larger and the attack cheaper, not smaller; patience is per-client and identical across clients.
does_not_show: WHAT Delta IS for any real deployment — that is a measurement on a named host and this
rung supplies the form, not the datum; that stabilization is enough, since a server may stall only
during the window it needs and go quiet again, and bounding that requires the histories `splitview`
compares rather than the timings compared here; any claim about consensus — this is a detector
accuracy result, not FLP, and the two must not be run together."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb, product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import auditgraph as _AG                                            # noqa: E402

MAGIC = b"URDRPAT1"
PINNED_DELTA = 4                 # the honest envelope the free-move census is decided over
PINNED_K = 4                     # ...on topologies of this order
DELTA_MAX = 64                   # the closed form is decided over these ranges
T0_MAX = 8


class PatienceError(Exception):
    def __init__(self, message):
        super().__init__(f"PATIENCE-REFUSE: {message}")
        self.code = "PATIENCE-REFUSE"


# ---- the observation ---------------------------------------------------------------------------------
def observed_edges(edges, delays, T):
    """WHAT A CLIENT ACTUALLY SEES: the peers that answered within its patience. An edge whose delay
    exceeds T is SILENT, and silence carries no evidence about its cause."""
    return tuple(e for e, d in zip(edges, delays) if d <= T)


def observation_is_blind_to_cause(delays):
    """THE CHANDRA-TOUEG POINT, made concrete: the observation is a function of the DELAYS ALONE. A
    server that chose these delays and a network that produced them are the same input. There is no
    third field to inspect, which is why this is not a detector that happens to be weak."""
    return tuple(delays)


def _assignments(n, delta):
    return _prod(range(1, delta + 1), repeat=n)


# ---- the free move -----------------------------------------------------------------------------------
def free_moves(k, edges, T, delta=PINNED_DELTA):
    """MEASURED: how many delay assignments inside the honest envelope [1, Delta] leave the OBSERVED
    audit graph disconnected. Each one is a winning move for the server that nature could equally
    have produced, so it is not merely undetected — it is unattributable. Returns (winning, total)."""
    if not edges:
        raise PatienceError("an empty topology has no delays to assign")
    win = total = 0
    for delays in _assignments(len(edges), delta):
        total += 1
        if not _AG.is_connected(k, observed_edges(edges, delays, T)):
            win += 1
    return win, total


def free_moves_vanish_exactly_at_delta(k=PINNED_K, delta=PINNED_DELTA):
    """THE SEPARATION, DECIDED: the server has a free move for every patience below Delta and none at
    or above it. Returns ((T, winning, total), ...) over T = 1 .. Delta+1."""
    edges = _AG.ring_graph(k)
    return tuple((T,) + free_moves(k, edges, T, delta) for T in range(1, delta + 2))


def separation_is_exactly_t_ge_delta(k=PINNED_K, delta=PINNED_DELTA):
    """The law: winning moves exist iff T < Delta. Both directions must be witnessed or the claim is
    half-tested."""
    table = free_moves_vanish_exactly_at_delta(k, delta)
    below = [w for T, w, _t in table if T < delta]
    at_or_above = [w for T, w, _t in table if T >= delta]
    return bool(below) and all(w > 0 for w in below) and \
        bool(at_or_above) and all(w == 0 for w in at_or_above)


# ---- the ladder collapse ----------------------------------------------------------------------------
def stall_price(k, edges, T, delta=PINNED_DELTA):
    """THE PRICE UNDER STALL, denominated the way `auditgraph` denominated it — in EXCLUDED CLIENTS.
    A stalling server excludes none, so when it has a free move the price is 0 and when it has none
    the question reverts to `auditgraph`."""
    win, _total = free_moves(k, edges, T, delta)
    if win:
        return 0
    return _AG.exclusion_price(k, edges)


def ladder_under_stall(k=PINNED_K, delta=PINNED_DELTA):
    """The `auditgraph` ladder recomputed under a stalling adversary, at an impatient T and a patient
    one. Returns ((T, path, ring, complete), ...) for T = Delta-1 and T = Delta. The first row must
    be all zeros and the second must reproduce auditgraph's 1 / 2 / INFINITE EXACTLY — cross-checked
    against that module rather than restated here."""
    out = []
    for T in (delta - 1, delta):
        out.append((T,
                    stall_price(k, _AG.path_graph(k), T, delta),
                    stall_price(k, _AG.ring_graph(k), T, delta),
                    stall_price(k, _AG.complete_graph(k), T, delta)))
    return tuple(out)


def ladder_collapses_then_returns(k=PINNED_K, delta=PINNED_DELTA):
    """The theorem in one predicate, and it is cross-module: impatient => 0/0/0, patient => exactly
    what `auditgraph` decided independently."""
    impatient, patient = ladder_under_stall(k, delta)
    if impatient[1:] != (0, 0, 0):
        return False
    want = (_AG.exclusion_price(k, _AG.path_graph(k)),
            _AG.exclusion_price(k, _AG.ring_graph(k)),
            _AG.exclusion_price(k, _AG.complete_graph(k)))
    return patient[1:] == want and want == (1, 2, _AG.INFINITE)


# ---- kappa and lambda are two questions, and T decides which one binds --------------------------------
def stall_move_count(k, edges):
    """HOW MANY EDGES a stalling server must silence: a minimum EDGE cut, lambda. `auditgraph` proved
    lambda OVER-prices the exclusion question, and that verdict stands — this is a different question,
    and lambda is its right answer."""
    return _AG.edge_connectivity(k, edges)


def which_quantity_binds(k=PINNED_K, delta=PINNED_DELTA):
    """THE ERGONOMIC STATEMENT, decided on the pinned topologies: at T < Delta the binding quantity is
    lambda edges silenced at a VISIBLE cost of 0 clients; at T >= Delta it is kappa clients excluded.
    Returns ((name, kappa, lambda_, visible_cost_impatient, visible_cost_patient), ...)."""
    out = []
    for name, edges in (("path", _AG.path_graph(k)), ("ring", _AG.ring_graph(k)),
                        ("complete", _AG.complete_graph(k))):
        out.append((name, _AG.vertex_connectivity(k, edges), stall_move_count(k, edges),
                    stall_price(k, edges, delta - 1, delta),
                    stall_price(k, edges, delta, delta)))
    return tuple(out)


def lambda_was_the_answer_to_another_question(k=PINNED_K):
    """THE SHARPEST ROW IN THE RUNG, and it lands on the topology `auditgraph` called UNBREAKABLE.
    On the complete graph no exclusion budget suffices — kappa is INFINITE — and yet a stalling
    server needs only lambda = k-1 edges silenced, at a visible cost of zero clients. The quantity a
    previous rung measured as a plant is EXACT for the move that rung did not model, so the two are
    not rival answers to one question but answers to two, and the inequality T >= Delta decides which
    is live. On the ring and the path they happen to COINCIDE, which is why the complete graph is the
    witness that has to be shown. Returns (kappa_complete, lambda_complete, kappa_ring, lambda_ring,
    coincide_on_ring)."""
    comp, ring = _AG.complete_graph(k), _AG.ring_graph(k)
    return (_AG.vertex_connectivity(k, comp), stall_move_count(k, comp),
            _AG.vertex_connectivity(k, ring), stall_move_count(k, ring),
            _AG.vertex_connectivity(k, ring) == stall_move_count(k, ring))


def the_unbreakable_topology_is_stall_breakable(k=PINNED_K, delta=PINNED_DELTA):
    """Stated so it can be false: `auditgraph`'s only unbreakable topology falls to a stalling server
    that excludes nobody. Returns (exclusion_price, stall_visible_cost, edges_silenced); the first
    must be INFINITE, the second 0, the third finite."""
    comp = _AG.complete_graph(k)
    return (_AG.exclusion_price(k, comp), stall_price(k, comp, delta - 1, delta),
            stall_move_count(k, comp))


# ---- the closed form -----------------------------------------------------------------------------------
def false_alarms_doubling_sim(delta, t0):
    """SIMULATION: patience doubles after each false alarm until it covers the true bound."""
    if delta < 1 or t0 < 1:
        raise PatienceError("delta and t0 must be positive")
    T, n = t0, 0
    while T < delta:
        n += 1
        T *= 2
    return n


def false_alarms_doubling(delta, t0):
    """THE CLOSED FORM: ceil(log2(ceil(delta / t0))), in pure integer arithmetic. `.bit_length()` is
    the repo's ceil-log2 (the same move `horn` uses for pitch), so no float ever touches this path."""
    if delta < 1 or t0 < 1:
        raise PatienceError("delta and t0 must be positive")
    q = (delta + t0 - 1) // t0
    return (q - 1).bit_length()


def false_alarms_linear_sim(delta, t0):
    T, n = t0, 0
    while T < delta:
        n += 1
        T += t0
    return n


def false_alarms_linear(delta, t0):
    """The linear growth closed form: ceil(delta/t0) - 1 — the same quantity BEFORE the logarithm."""
    if delta < 1 or t0 < 1:
        raise PatienceError("delta and t0 must be positive")
    return (delta + t0 - 1) // t0 - 1


def closed_form_census(delta_max=DELTA_MAX, t0_max=T0_MAX):
    """DECIDED: both closed forms reproduce their simulations over every (delta, t0) in range.
    Returns (agreements, exceptions, total)."""
    agree = exc = total = 0
    for delta in range(1, delta_max + 1):
        for t0 in range(1, t0_max + 1):
            total += 1
            ok = (false_alarms_doubling(delta, t0) == false_alarms_doubling_sim(delta, t0) and
                  false_alarms_linear(delta, t0) == false_alarms_linear_sim(delta, t0))
            agree += 1 if ok else 0
            exc += 0 if ok else 1
    return agree, exc, total


def closed_forms_hold(delta_max=DELTA_MAX, t0_max=T0_MAX):
    _a, exc, total = closed_form_census(delta_max, t0_max)
    return exc == 0 and total > 0


def stabilization_is_finite_and_permanent(delta_max=DELTA_MAX, t0_max=T0_MAX):
    """The DLS payoff: the count is FINITE for every bound, and once patience exceeds Delta it never
    falls back — so the false alarms are paid once, not per epoch. Returns (max_count, all_finite)."""
    worst = 0
    for delta in range(1, delta_max + 1):
        for t0 in range(1, t0_max + 1):
            n = false_alarms_doubling(delta, t0)
            worst = max(worst, n)
            T = t0 * (2 ** n)
            if T < delta:
                return worst, False
    return worst, True


def the_gap(pairs=((200, 1), (1000, 1), (64, 1), (64, 8))):
    """The linear plant is not incorrect, it is UNAFFORDABLE. Returns
    ((delta, t0, linear, doubling), ...)."""
    return tuple((d, t, false_alarms_linear(d, t), false_alarms_doubling(d, t)) for d, t in pairs)


# ---- the plants -----------------------------------------------------------------------------------------
def _fixed_patience(delta, t0, rounds):
    """A FALSIFIER TOOL: never grow the timeout. If t0 < Delta every round is a false alarm forever —
    the count is not large, it is UNBOUNDED, which is the difference that matters."""
    return rounds if t0 < delta else 0


def fixed_patience_never_stabilizes(delta=64, t0=1):
    """The plant BITES: its cost grows with the number of rounds while the doubling cost does not.
    Returns (at_100_rounds, at_10000_rounds, doubling_cost)."""
    return (_fixed_patience(delta, t0, 100), _fixed_patience(delta, t0, 10000),
            false_alarms_doubling(delta, t0))


def _assume_delta_is_known(guess):
    """A FALSIFIER TOOL: pick a fixed patience and declare the ladder restored. Sound exactly when the
    guess is not exceeded — which under DLS partial synchrony is precisely what cannot be assumed."""
    return guess


def guessing_delta_bites(guess=8, delta_max=DELTA_MAX):
    """The plant BITES: over the pinned range, how many true bounds exceed the guess and therefore
    leave the server a free move the deployment believes it has closed. Returns (exceeded, total)."""
    exceeded = sum(1 for d in range(1, delta_max + 1) if _assume_delta_is_known(guess) < d)
    return exceeded, delta_max


def linear_plant_is_unaffordable_not_wrong(delta=DELTA_MAX, t0=1):
    """A PLANT CLASS THE REPO HAD NOT NAMED: one that terminates, is sound, and loses anyway on cost.
    Returns (linear, doubling, both_terminate) — the third must be True, which is the point."""
    lin, dbl = false_alarms_linear(delta, t0), false_alarms_doubling(delta, t0)
    return lin, dbl, (false_alarms_linear_sim(delta, t0) == lin and
                      false_alarms_doubling_sim(delta, t0) == dbl)


# ---- the refusal ------------------------------------------------------------------------------------------
def require_patience_covers(delta, T):
    """THE AUTHORITATIVE CALL: an audit deployment whose patience does not cover the delay envelope
    has no exclusion price at all, so it RAISES rather than reporting a reduced guarantee. Reporting
    kappa there would be the inflation this whole rung exists to prevent."""
    if T < delta:
        raise PatienceError(f"patience {T} below the delay envelope {delta}: the price is 0, not kappa")
    return True


def refuses_an_impatient_deployment():
    try:
        require_patience_covers(10, 9)
    except PatienceError as exc:
        return exc.code == "PATIENCE-REFUSE"
    return False


def admits_a_patient_one():
    return require_patience_covers(10, 10) is True


# ---- digests + scenes ---------------------------------------------------------------------------------------
def pt_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_separation():
    return pt_digest("separation", f"{free_moves_vanish_exactly_at_delta()}:"
                                   f"{separation_is_exactly_t_ge_delta()}")


def _scene_collapse():
    return pt_digest("collapse", f"{ladder_under_stall()}:{ladder_collapses_then_returns()}:"
                                 f"{which_quantity_binds()}:"
                                 f"{lambda_was_the_answer_to_another_question()}:"
                                 f"{the_unbreakable_topology_is_stall_breakable()}")


def _scene_form():
    return pt_digest("form", f"{closed_form_census()}:{closed_forms_hold()}:"
                             f"{stabilization_is_finite_and_permanent()}:{the_gap()}:"
                             f"{fixed_patience_never_stabilizes()}:{guessing_delta_bites()}:"
                             f"{linear_plant_is_unaffordable_not_wrong()}")


_SCENES = {"separation": _scene_separation, "collapse": _scene_collapse, "form": _scene_form}
SCENES = ("separation", "collapse", "form")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_patience.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PatienceError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"free moves by patience {free_moves_vanish_exactly_at_delta()}")
    print(f"separation is exactly T>=Delta {separation_is_exactly_t_ge_delta()}")
    print(f"ladder under stall {ladder_under_stall()} | collapses then returns "
          f"{ladder_collapses_then_returns()}")
    print(f"which binds {which_quantity_binds()}")
    print(f"lambda was another question {lambda_was_the_answer_to_another_question()}")
    print(f"the unbreakable topology is stall-breakable "
          f"{the_unbreakable_topology_is_stall_breakable()}")
    print(f"closed form {closed_form_census()} (exceptions must be 0) | "
          f"stabilization {stabilization_is_finite_and_permanent()}")
    print(f"gap linear vs doubling {the_gap()}")
    print(f"plants: fixed {fixed_patience_never_stabilizes()} | guess {guessing_delta_bites()} | "
          f"linear {linear_plant_is_unaffordable_not_wrong()}")
    print(f"refuses impatient {refuses_an_impatient_deployment()} | admits patient "
          f"{admits_a_patient_one()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
