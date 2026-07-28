# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""auditgraph — THE EXCLUSION PRICE (URDRAGR1): what URDRSPV1 assumed away, and the reason its
cheapest recommendation is the wrong one to ship. NO NEW GLYPH.

WHAT THE PREVIOUS RUNG ASSUMED. `splitview` decided that undetected equivocation is possible exactly
when the gossip graph is disconnected, that the minimum edge count for a guarantee is k-1, and
therefore that a spanning tree suffices and all-pairs gossip buys nothing. Every one of those
statements is true and the last one is true ONLY AGAINST AN ADVERSARY WITH NO MEMBERSHIP CONTROL.
The gossip graph there is exogenous — it is given, and the server plays against it.

    IN AN MMO THE SERVER BUILDS THE GRAPH. MATCHMAKING IS THE ATTACK SURFACE.

An OFFICIAL global server decides who shares a session, who shards with whom, who is admitted at all.
If it also chooses the audit topology it does not need to hope for a disconnection: it constructs one.
DECIDED: over the Bell(k) ways to partition k clients into sessions, Bell(k) - 1 leave the audit graph
disconnected, and the server picks. Committing the topology to client identity removes that lever
entirely — 0 of 1. What survives is ADMISSION, and that is the whole content of this rung.

THE EXCLUSION PRICE THEOREM. Under a committed topology T the server's only remaining move is to
exclude clients until the survivors fall into two or more non-communicating groups.

    the price of undetected equivocation is exactly kappa(T), the VERTEX connectivity

DECIDED by running the attack — enumerate every subset of clients the server might exclude, ask
whether the survivors split — and comparing it against kappa computed by MAX-FLOW under Menger's
theorem, over every connected labelled graph to order 5. They agree everywhere, 0 exceptions of 771.

    AND THE FIRST VERSION OF THAT SENTENCE WAS A LIE, WHICH IS RECORDED HERE RATHER THAN REPAIRED IN
    SILENCE. This rung originally compared `exclusion_price` against `vertex_connectivity` and sold
    the agreement as "two computations agreeing is a measurement; one computation is a definition
    restated." Those two functions are the SAME loop over the SAME subsets calling the SAME
    `components`, separated only by a `len(alive) < 2` guard that provably cannot change the answer.
    The claim shipped three times before an audit caught it. It was refuted BY MUTATION, not by
    argument: corrupt `components` and the old census still reports 0 exceptions, merely shrinking
    its own denominator, while the Menger census reports 181. A checker that cannot fail is not
    evidence, and `cross_check_is_falsifiable` now runs exactly that mutation on every gate pass so
    the property is asserted rather than believed. The NUMBERS below never changed; only the reason
    to trust them did.

    AND THAT FIX ONLY REACHED THE NUMERATOR. `connected_graphs` — the DENOMINATOR of every census
    here — is built entirely from `is_connected`, which is the same flood fill. Under the same
    planted fault the family at order 5 silently shrinks from 728 to 476 and raises NOTHING, so a
    fault that narrowed the world without causing disagreements would still have passed. `is_connected`
    is now cross-checked against MAX-FLOW connectivity over every labelled graph to order 5 (1099 of
    1099, 0 exceptions, 772 connected), that check bites under the fault, and `validate_graph` turns
    an out-of-range endpoint, a negative index or a self-loop from a SILENTLY DROPPED edge into a
    typed refusal — because returning a plausible False to a caller who asked about a different graph
    is the same defect one layer down.

AND THE COMPLETE GRAPH HAS NO PRICE, WHICH REVERSES THE PREVIOUS RUNG'S RECOMMENDATION. Enumerated:
the connected graphs on k vertices that the server can NEVER split, at any exclusion budget, are
EXACTLY the complete ones. A spanning tree costs 1 exclusion. A ring costs 2. All-pairs costs
infinity. So `splitview`'s "all-pairs gossip buys nothing" was correct in its own model and would be
a bad thing to build, because the value of redundant gossip is INVISIBLE until the adversary's
membership control is modelled. The two rungs are not in conflict; the scope of the cheaper one is.
That is recorded here rather than quietly fixed, because a reader who saw only the first would ship a
spanning tree a server dismantles with one kick.

WHAT THIS BUYS, STATED PRECISELY. It does not make equivocation impossible — nothing here does. It
converts an INVISIBLE INTEGRITY attack into a VISIBLE AVAILABILITY one: a server that wants to fork
must first remove kappa named clients, and being removed is the one thing a client can observe about
itself without comparing anything. The attack is not prevented, it is made to cost something the
victims can see.

GRADE. MEASURED: price == kappa over every connected labelled graph to order 5, 0 exceptions, by
attack simulation (subset enumeration) against Menger max-flow — two algorithms sharing no primitive,
with the independence itself asserted by a mutation that makes the check go red; the DENOMINATOR
cross-checked the same way, flood fill against max-flow over 1099 labelled graphs with 0 exceptions
and a typed refusal for malformed input; the unbreakable set is exactly the complete graphs; the Bell(k)-1 assignment census and its collapse to 0 under commitment; the path/ring/complete
price ladder 1/2/infinity, attained; three plants biting, including two that OVER-price by using
lambda or delta where kappa is the truth and so understate the threat; determinism. DECLARED: the
audit topology is a static undirected graph over a fixed identity set, and clients gossip truthfully
(a sybil population reporting fabricated heads is geoquorum's problem, not this one); exclusion is
modelled as vertex removal, so a server that DEGRADES rather than drops a client is out of scope.
does_not_show: that exclusion is actually noticed — that inherits `splitview`'s liveness residual
unchanged, and a client which cannot tell denial from outage cannot raise the alarm; WHO to believe
after a fork is detected; any bound on a server that can mint identities, which would let it buy back
the assignment lever it lost."""
import hashlib
import os as _os
import sys as _sys
from collections import deque as _deque
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRAGR1"
MAX_ORDER = 5            # every labelled graph to this order is enumerated
LADDER_MIN = 4           # ...starting HERE: on three clients the ring IS the complete graph
LADDER_MAX = 8           # the path/ring/complete price ladder is decided to here
INFINITE = None          # "no exclusion budget suffices" — never a large integer


class AuditGraphError(Exception):
    def __init__(self, message):
        super().__init__(f"AUDITGRAPH-REFUSE: {message}")
        self.code = "AUDITGRAPH-REFUSE"


# ---- graphs ----------------------------------------------------------------------------------------
def _neighbours(k, edges, alive):
    adj = {v: set() for v in alive}
    for u, v in edges:
        if u in alive and v in alive:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def components(k, edges, alive=None):
    """Connected components over the SURVIVING vertices."""
    alive = frozenset(range(k)) if alive is None else frozenset(alive)
    adj, seen, out = _neighbours(k, edges, alive), set(), []
    for s in sorted(alive):
        if s in seen:
            continue
        comp, stack = set(), [s]
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(n for n in adj[x] if n not in comp)
        seen |= comp
        out.append(frozenset(comp))
    return tuple(out)


def validate_graph(k, edges):
    """HARDENING THE PRIMITIVE EVERY CENSUS RESTS ON. `_neighbours` only wires an edge when BOTH
    endpoints are alive, which means a vertex index outside range(k), a negative index, or a typo
    was SILENTLY DROPPED and `is_connected` returned a plausible False instead of refusing. A
    malformed edge raised a bare ValueError rather than a typed refusal. Both are now errors: a
    caller that hands this module a graph it did not mean gets told, rather than getting an answer
    to a different question."""
    if not isinstance(k, int) or k < 0:
        raise AuditGraphError(f"vertex count must be a non-negative int, got {k!r}")
    for e in edges:
        try:
            u, v = e
        except (TypeError, ValueError):
            raise AuditGraphError(f"edge {e!r} is not a pair")
        if not isinstance(u, int) or not isinstance(v, int):
            raise AuditGraphError(f"edge {e!r} has a non-integer endpoint")
        if not (0 <= u < k) or not (0 <= v < k):
            raise AuditGraphError(f"edge {e!r} references a vertex outside range({k})")
        if u == v:
            raise AuditGraphError(f"edge {e!r} is a self-loop, which carries no connectivity")
    return True


def is_connected(k, edges):
    validate_graph(k, edges)
    return k > 0 and len(components(k, edges)) == 1


def is_connected_by_flow(k, edges):
    """CONNECTIVITY BY MAX-FLOW, sharing nothing with `components`. Fix a root and demand a unit of
    flow reaches every other vertex. This exists because the Menger fix de-circularized the NUMERATOR
    of every census while leaving the DENOMINATOR — `connected_graphs`, built entirely from
    `is_connected` — resting on the same flood fill. Measured: with `components` corrupted the family
    silently shrinks from 728 to 476 at order 5 and raises nothing, so a fault that narrows the family
    without causing disagreements would have passed unseen."""
    validate_graph(k, edges)
    if k <= 0:
        return False
    if k == 1:
        return True
    cap = {}

    def _add(a, b, c):
        cap.setdefault(a, {})
        cap[a][b] = cap[a].get(b, 0) + c

    for u, v in edges:
        _add(u, v, 1)
        _add(v, u, 1)
    return all(_maxflow({a: dict(b) for a, b in cap.items()}, 0, t) >= 1 for t in range(1, k))


def family_census(max_k=MAX_ORDER):
    """THE DENOMINATOR, CROSS-CHECKED. Flood fill against max-flow over EVERY labelled graph to order
    `max_k` — not merely the connected ones, since the question is precisely which graphs enter the
    family. Returns (agreements, exceptions, total, connected)."""
    agree = exc = total = conn = 0
    for k in range(1, max_k + 1):
        for edges in _all_graphs(k):
            total += 1
            a = is_connected(k, edges)
            b = is_connected_by_flow(k, edges)
            conn += 1 if a else 0
            if a == b:
                agree += 1
            else:
                exc += 1
    return agree, exc, total, conn


def min_degree(k, edges):
    adj = _neighbours(k, edges, frozenset(range(k)))
    return min((len(adj[v]) for v in range(k)), default=0)


def vertex_connectivity(k, edges):
    """kappa(G): the fewest vertices whose removal leaves two or more components. A complete graph
    has NO vertex cut at all, and this returns INFINITE for it rather than the textbook k-1 — because
    the quantity being measured here is an ADVERSARY'S BUDGET, and k-1 would say 'expensive but
    possible' where the truth is 'impossible'. Using the textbook convention would have inflated a
    guarantee into a price."""
    if not is_connected(k, edges):
        return 0
    for size in range(0, k):
        for cut in _comb(range(k), size):
            alive = frozenset(range(k)) - frozenset(cut)
            if len(components(k, edges, alive)) >= 2:
                return size
    return INFINITE


def edge_connectivity(k, edges):
    """lambda(G). Kept only so the plant that uses it can be counted."""
    if not is_connected(k, edges):
        return 0
    E = list(edges)
    for size in range(0, len(E) + 1):
        for drop in _comb(range(len(E)), size):
            keep = tuple(E[i] for i in range(len(E)) if i not in set(drop))
            if len(components(k, keep)) >= 2:
                return size
    return INFINITE


def _all_graphs(k):
    pairs = list(_comb(range(k), 2))
    for mask in range(1 << len(pairs)):
        yield tuple(pairs[i] for i in range(len(pairs)) if mask >> i & 1)


def connected_graphs(k):
    return tuple(e for e in _all_graphs(k) if is_connected(k, e))


def complete_graph(k):
    return tuple(_comb(range(k), 2))


def path_graph(k):
    return tuple((i, i + 1) for i in range(k - 1))


def ring_graph(k):
    if k < 3:
        raise AuditGraphError("a ring needs at least three clients")
    return tuple((i, (i + 1) % k) for i in range(k))


# ---- the attack ---------------------------------------------------------------------------------------
def server_wins_after_excluding(k, edges, excluded):
    """THE ATTACK, SIMULATED. After removing `excluded`, can the server serve two or more histories
    that no surviving client can compare? Yes exactly when the survivors fall into two or more
    components. A survivor set of size one is NOT a win — a server with one client has one view to
    serve and cannot equivocate at all, which is `splitview`'s k=1 vacuity inherited rather than
    re-earned."""
    alive = frozenset(range(k)) - frozenset(excluded)
    if len(alive) < 2:
        return False
    return len(components(k, edges, alive)) >= 2


def _maxflow(cap, s, t):
    """Edmonds-Karp on integer capacities. BFS augmentation — it shares NO machinery with
    `components`, which is the entire reason it is here."""
    res = {u: dict(v) for u, v in cap.items()}
    flow = 0
    while True:
        par, q = {s: None}, _deque([s])
        while q:
            u = q.popleft()
            for v, c in res.get(u, {}).items():
                if c > 0 and v not in par:
                    par[v] = u
                    q.append(v)
        if t not in par:
            return flow
        b, v = None, t
        while par[v] is not None:
            c = res[par[v]][v]
            b = c if b is None else min(b, c)
            v = par[v]
        v = t
        while par[v] is not None:
            u = par[v]
            res[u][v] -= b
            res.setdefault(v, {})[u] = res.get(v, {}).get(u, 0) + b
            v = u
        flow += b


def vertex_connectivity_menger(k, edges):
    """kappa(G) BY MENGER'S THEOREM: the minimum, over NON-ADJACENT pairs, of the maximum number of
    internally vertex-disjoint paths — computed as a max-flow on the vertex-split graph, where each
    client v becomes v_in -> v_out with capacity 1 (capacity INF for the two endpoints, which cannot
    be excluded) and each audit link becomes an infinite-capacity arc. A complete graph has no
    non-adjacent pair, hence no cut, hence INFINITE.

    THIS EXISTS BECAUSE THE ORIGINAL CROSS-CHECK WAS CIRCULAR. `exclusion_price` and
    `vertex_connectivity` are the SAME loop over the SAME subsets calling the SAME `components`,
    differing only by a guard that provably cannot change the answer, so their agreement was a
    tautology sold as a measurement. Proved by mutation rather than by argument: with `components`
    deliberately corrupted the old census still reported 0 exceptions and merely shrank its own
    denominator, while this one reports 181. A checker that cannot fail is not evidence."""
    adjacent = {(min(u, v), max(u, v)) for u, v in edges}
    INF = k + 10
    best = None
    for s, t in _comb(range(k), 2):
        if (s, t) in adjacent:
            continue
        cap = {}

        def _add(a, b, c):
            cap.setdefault(a, {})
            cap[a][b] = cap[a].get(b, 0) + c

        for v in range(k):
            _add(2 * v, 2 * v + 1, INF if v in (s, t) else 1)
        for u, v in edges:
            _add(2 * u + 1, 2 * v, INF)
            _add(2 * v + 1, 2 * u, INF)
        f = _maxflow(cap, 2 * s + 1, 2 * t)
        best = f if best is None else min(best, f)
    return INFINITE if best is None else best


def exclusion_price(k, edges):
    """THE PRICE: the fewest clients a server must exclude before it can equivocate undetected.
    INFINITE when no budget suffices. Computed by RUNNING THE ATTACK over every exclusion set. Its
    agreement with `vertex_connectivity` is NOT evidence — those two share `components` and cannot
    disagree; the load-bearing check is `menger_census`, which uses max-flow instead."""
    if not is_connected(k, edges):
        return 0
    for size in range(0, k):
        for excl in _comb(range(k), size):
            if server_wins_after_excluding(k, edges, excl):
                return size
    return INFINITE


def price_census(max_k=MAX_ORDER):
    """A CONSISTENCY CHECK, NOT EVIDENCE, and labelled that way after it was caught being sold as the
    latter. `exclusion_price` and `vertex_connectivity` are the same enumeration over the same
    subsets calling the same `components`; the only difference is a `len(alive) < 2` guard which at
    size k-1 leaves one vertex, and a one-vertex graph has one component, so `>= 2` is False on both
    paths. They CANNOT disagree. This is retained because it is cheap and would catch a regression in
    that guard — but it is not a measurement of anything. Returns (agreements, exceptions, total)."""
    agree = exc = total = 0
    for k in range(2, max_k + 1):
        for edges in connected_graphs(k):
            total += 1
            if exclusion_price(k, edges) == vertex_connectivity(k, edges):
                agree += 1
            else:
                exc += 1
    return agree, exc, total


def menger_census(max_k=MAX_ORDER):
    """THE LOAD-BEARING CHECK: the simulated attack price against kappa computed by MAX-FLOW under
    Menger's theorem. Subset enumeration versus flow augmentation — no shared primitive, so the two
    can genuinely disagree, and under a planted fault they do. Returns
    (agreements, exceptions, total)."""
    agree = exc = total = 0
    for k in range(2, max_k + 1):
        for edges in connected_graphs(k):
            total += 1
            if exclusion_price(k, edges) == vertex_connectivity_menger(k, edges):
                agree += 1
            else:
                exc += 1
    return agree, exc, total


def price_is_vertex_connectivity(max_k=MAX_ORDER):
    _a, exc, total = menger_census(max_k)
    return exc == 0 and total > 0


def cross_check_is_falsifiable(max_k=4):
    """L15 APPLIED TO A CHECKER RATHER THAN TO A CLAIM. Corrupt the primitive the attack simulation
    depends on and demand that each census react. The circular one does NOT — it keeps reporting 0
    exceptions and quietly shrinks its denominator, which is exactly how it passed review three times.
    The Menger one does. Returns (circular_exceptions_under_fault, menger_exceptions_under_fault);
    the first is 0 and the second must be positive, and that CONTRAST is the evidence that the second
    check is worth anything."""
    real = globals()["components"]

    def _broken(k, edges, alive=None):
        return real(k, tuple(edges)[1:] if edges else edges, alive)

    globals()["components"] = _broken
    try:
        _a1, circular_exc, _t1 = price_census(max_k)
        _a2, menger_exc, _t2 = menger_census(max_k)
        _a3, family_exc, _t3, _c3 = family_census(max_k)
    finally:
        globals()["components"] = real
    return circular_exc, menger_exc, family_exc


# ---- the unbreakable set ---------------------------------------------------------------------------------
def unbreakable_graphs(k):
    """Every connected topology on k clients the server can NEVER split, at any budget."""
    return tuple(e for e in connected_graphs(k) if exclusion_price(k, e) is INFINITE)


def family_check_is_falsifiable(max_k=4):
    """The denominator check must react to the same planted fault, or the family is still resting on
    an unaudited primitive."""
    return cross_check_is_falsifiable(max_k)[2] > 0


def circular_check_cannot_fail(max_k=4):
    """Named separately so the defect is a first-class object rather than a comment: the
    original cross-check reports 0 exceptions even with the primitive it depends on
    corrupted. Returns True when that is still so — and it is expected to be True, because
    the point is that this check is inert, not that it was fixed."""
    return cross_check_is_falsifiable(max_k)[0] == 0


def unbreakable_are_exactly_complete(max_k=MAX_ORDER):
    """THE RESULT THAT REVERSES THE PREVIOUS RUNG'S RECOMMENDATION: the unbreakable set is EXACTLY
    the complete graphs — one per order, no others. Returns
    ((k, count, is_just_the_complete_graph), ...)."""
    out = []
    for k in range(2, max_k + 1):
        ub = unbreakable_graphs(k)
        out.append((k, len(ub), set(ub) == {complete_graph(k)}))
    return tuple(out)


def price_ladder(max_k=LADDER_MAX, min_k=LADDER_MIN):
    """The three topologies a deployment would actually consider, priced. DECIDED, and the point is
    that the ladder is 1 / 2 / INFINITE regardless of how many clients there are — redundancy here is
    not a matter of degree but of kind. It starts at FOUR clients, for the reason below."""
    out = []
    for k in range(min_k, max_k + 1):
        out.append((k, exclusion_price(k, path_graph(k)), exclusion_price(k, ring_graph(k)),
                    exclusion_price(k, complete_graph(k))))
    return tuple(out)


def ladder_is_one_two_infinite(max_k=LADDER_MAX, min_k=LADDER_MIN):
    return all(p == 1 and r == 2 and c is INFINITE for _k, p, r, c in price_ladder(max_k, min_k))


def the_triangle_is_both(k=3):
    """WHY THE LADDER STARTS AT FOUR, kept as a live measurement rather than a footnote. A FIRST
    DRAFT RAN IT FROM k=3 AND THE LAW CAME BACK FALSE: on three clients the ring IS the complete
    graph, so the middle and top rungs are the same topology and the ring's price is INFINITE rather
    than 2. The universal had been asserted from a mental sample of one — the five-client picture —
    and the enumeration refused it. Returns (ring_equals_complete, ring_price, complete_price); the
    first must be True and the prices must agree, which is exactly the degeneracy."""
    r, c = ring_graph(k), complete_graph(k)
    return (frozenset(map(frozenset, r)) == frozenset(map(frozenset, c)),
            exclusion_price(k, r), exclusion_price(k, c))


def spanning_tree_falls_to_one_exclusion(max_k=LADDER_MAX):
    """THE CONCRETE WARNING. `splitview` proved a spanning tree is the minimum-edge topology that
    guarantees detection, which is true and is a bad thing to build: it costs the server ONE kick.
    Returns ((k, price), ...) — every entry must be 1."""
    return tuple((k, exclusion_price(k, path_graph(k))) for k in range(LADDER_MIN, max_k + 1))


# ---- the assignment lever, and its removal -----------------------------------------------------------------
def _set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for parts in _set_partitions(rest):
        for i in range(len(parts)):
            yield parts[:i] + [[first] + parts[i]] + parts[i + 1:]
        yield [[first]] + parts


def server_choice_census(k):
    """A server that also picks the sessions picks the audit graph. Over every way to partition k
    clients into sessions — audit edges existing only WITHIN a session — how many leave the graph
    disconnected. Returns (disconnecting, total); total is Bell(k) and disconnecting is Bell(k) - 1,
    so the server always has a winning choice for k >= 2."""
    dis = total = 0
    for parts in _set_partitions(range(k)):
        total += 1
        edges = tuple(e for blk in parts for e in _comb(sorted(blk), 2))
        if not is_connected(k, edges):
            dis += 1
    return dis, total


def committed_census(k, topology=None):
    """A topology COMMITTED to client identity leaves the server no assignment at all: one option,
    connected. Returns (disconnecting, total) = (0, 1)."""
    edges = ring_graph(k) if topology is None else topology
    return (0 if is_connected(k, edges) else 1), 1


def commitment_removes_the_assignment_lever(max_k=MAX_ORDER):
    """The contrast, and the denominators are what keep the 0 from being vacuous."""
    for k in range(3, max_k + 1):
        dis, total = server_choice_census(k)
        if not (dis == total - 1 and dis > 0):
            return False
        if committed_census(k) != (0, 1):
            return False
    return True


def _committed_by_server_index(k, perm):
    """A FALSIFIER TOOL: 'commit the topology to the client INDEX' — which the server assigns. It
    re-acquires the lever it was supposed to have lost, because relabelling is free."""
    ring = ring_graph(k)
    return tuple(tuple(sorted((perm[u], perm[v]))) for u, v in ring)


def index_commitment_is_not_commitment(k=5):
    """The plant BITES in the way that matters: relabelling preserves connectivity, so the topology
    still looks safe — and the server has instead chosen WHICH REAL CLIENT sits at each degree-2
    position, so it selects the victims of the two exclusions it must pay. Returns
    (still_connected, distinct_victim_pairs) — the first True is exactly why the defect is easy to
    miss, and the second must exceed one."""
    victims, connected_everywhere = set(), True
    for perm in _perms(range(k)):
        edges = _committed_by_server_index(k, perm)
        connected_everywhere = connected_everywhere and is_connected(k, edges)
        for excl in _comb(range(k), 2):
            if server_wins_after_excluding(k, edges, excl):
                victims.add(tuple(sorted(excl)))
    return connected_everywhere, len(victims)


def _perms(xs):
    xs = list(xs)
    if len(xs) <= 1:
        yield tuple(xs)
        return
    for i in range(len(xs)):
        for rest in _perms(xs[:i] + xs[i + 1:]):
            yield (xs[i],) + rest


# ---- the plants that OVER-price ------------------------------------------------------------------------------
def _price_by_edge_connectivity(k, edges):
    """A FALSIFIER TOOL: price the attack in CUT LINKS instead of EXCLUDED CLIENTS. Whitney gives
    kappa <= lambda, so this never under-states the price — it OVER-states it, which is the dangerous
    direction: it tells a deployment the server must work harder than it does."""
    return edge_connectivity(k, edges)


def _price_by_min_degree(k, edges):
    """A FALSIFIER TOOL: price by the least-connected client's degree. kappa <= lambda <= delta, so
    this over-states at least as badly."""
    return min_degree(k, edges)


def overprice_census(max_k=MAX_ORDER):
    """MEASURED: how often each plant reports a price ABOVE the truth, and how often BELOW. The
    below-count must be 0 — the failure of these plants is entirely in the optimistic direction, so a
    deployment trusting them believes it is safer than it is. Returns
    (lambda_over, lambda_under, delta_over, delta_under, total)."""
    lo = lu = do = du = total = 0
    for k in range(2, max_k + 1):
        for edges in connected_graphs(k):
            true = exclusion_price(k, edges)
            if true is INFINITE:
                continue
            total += 1
            for fn, over, under in ((_price_by_edge_connectivity, "l", "l"),
                                    (_price_by_min_degree, "d", "d")):
                got = fn(k, edges)
                if got is INFINITE:
                    got = k
                if fn is _price_by_edge_connectivity:
                    lo += 1 if got > true else 0
                    lu += 1 if got < true else 0
                else:
                    do += 1 if got > true else 0
                    du += 1 if got < true else 0
    return lo, lu, do, du, total


def plants_only_fail_optimistically(max_k=MAX_ORDER):
    lo, lu, do, du, total = overprice_census(max_k)
    return total > 0 and lo > 0 and do > 0 and lu == 0 and du == 0


def kappa_below_lambda_witness(max_k=MAX_ORDER):
    """L19 — if kappa == lambda everywhere in the family, the plants can never bite and the census
    above is decoration. An explicit witness count, which must be positive."""
    n = 0
    for k in range(2, max_k + 1):
        for edges in connected_graphs(k):
            kap, lam = vertex_connectivity(k, edges), edge_connectivity(k, edges)
            if kap is not INFINITE and lam is not INFINITE and kap < lam:
                n += 1
    return n


# ---- the refusal --------------------------------------------------------------------------------------------
def require_price_at_least(k, edges, floor):
    """THE AUTHORITATIVE CALL: refuse an audit topology whose exclusion price is below the policy
    floor. It RAISES; a topology that is too cheap is not a warning."""
    p = exclusion_price(k, edges)
    if p is INFINITE:
        return True
    if p < floor:
        raise AuditGraphError(f"exclusion price {p} below floor {floor}")
    return True


def refuses_a_spanning_tree(k=6, floor=2):
    try:
        require_price_at_least(k, path_graph(k), floor)
    except AuditGraphError as exc:
        return exc.code == "AUDITGRAPH-REFUSE"
    return False


def admits_a_ring(k=6, floor=2):
    return require_price_at_least(k, ring_graph(k), floor) is True


# ---- digests + scenes ----------------------------------------------------------------------------------------
def ag_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_price():
    return ag_digest("price", f"{price_census()}:{menger_census()}:{family_census()}:"
                              f"{price_is_vertex_connectivity()}:{cross_check_is_falsifiable()}:"
                              f"{unbreakable_are_exactly_complete()}")


def _scene_ladder():
    return ag_digest("ladder", f"{price_ladder()}:{ladder_is_one_two_infinite()}:"
                               f"{spanning_tree_falls_to_one_exclusion()}:"
                               f"{the_triangle_is_both()}")


def _scene_lever():
    return ag_digest("lever", f"{[server_choice_census(k) for k in range(2, MAX_ORDER + 1)]}:"
                              f"{commitment_removes_the_assignment_lever()}:"
                              f"{index_commitment_is_not_commitment()}:"
                              f"{overprice_census()}:{kappa_below_lambda_witness()}")


_SCENES = {"price": _scene_price, "ladder": _scene_ladder, "lever": _scene_lever}
SCENES = ("price", "ladder", "lever")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_auditgraph.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AuditGraphError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"circular consistency (NOT evidence) {price_census()}")
    print(f"attack vs MENGER max-flow  {menger_census()} (exceptions must be 0)")
    print(f"family (flood fill vs max-flow) {family_census()}")
    print(f"falsifiable (circular, menger, family) {cross_check_is_falsifiable()}")
    print(f"unbreakable are exactly complete {unbreakable_are_exactly_complete()}")
    print(f"ladder path/ring/complete {price_ladder()[:3]} ... 1/2/inf "
          f"{ladder_is_one_two_infinite()} | triangle degeneracy {the_triangle_is_both()}")
    print(f"spanning tree price {spanning_tree_falls_to_one_exclusion()[:4]}")
    print(f"server choice {[server_choice_census(k) for k in range(2, MAX_ORDER + 1)]} "
          f"| committed {committed_census(5)} | lever removed "
          f"{commitment_removes_the_assignment_lever()}")
    print(f"index commitment is not commitment {index_commitment_is_not_commitment()}")
    print(f"overprice (l_over, l_under, d_over, d_under, total) {overprice_census()} "
          f"| optimistic-only {plants_only_fail_optimistically()}")
    print(f"kappa < lambda witnesses {kappa_below_lambda_witness()}")
    print(f"refuses spanning tree {refuses_a_spanning_tree()} | admits ring {admits_a_ring()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
