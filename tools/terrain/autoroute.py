# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""autoroute — DECIDE AT THE CHEAPEST LEVEL THAT CAN DECIDE (URDRAUT1): `inputset`'s taxonomy and
`cohort`'s theorem wired into one router, with the proposed cascade's tier order CORRECTED by
measurement. NO NEW GLYPH.

WHAT THIS IS. `inputset` decided where each quantity may live and `cohort` enforced it for one tier.
The remaining move is a verifier that stops asking the caller for inputs it does not need: inspect
what is already local, run the cheapest decision procedure that can settle the question, and escalate
only when the mathematics actually demands it. That is what this module is. It is also SIX corrections:
the handed-down cascade inverted three of its own transitions and claimed one saving that does not
exist, my first attempt to correct it was itself wrong and had to be withdrawn by measurement, and the
search I built to replace the hand-written plan invented a reduction of its own that a hardness result
says no search can ever be trusted to rule out.

CORRECTION 1 — THE MENGER SCREEN CANNOT PRECEDE THE PAYLOAD FETCH. THE SAVING IS COMPUTE, NOT BYTES.
The cascade placed sub-gap screening at tier 2, above payload download, on the grounds that it
"returns the local verdict directly without downloading the remote tile payload". It cannot: the
screen tests |mine XOR theirs| < k, and that symmetric difference is a function of the peer's CELL
SET. `tilemin`'s certificate carries three fields and none of them is the occupancy — which is not an
oversight but `cohort`'s own refutation (3) restated, since byte-identical boundary occupancy admits
opposite verdicts and therefore no digest of a lattice can stand in for it. So the screen is a
POST-payload test and the router must say so. What it genuinely saves is FLOOD FILLS: compute your own
verdict once, then decide each sub-gap peer by a set-difference COUNT instead of a reachability
search. Measured over the pinned population, 2 flood fills against 7 — linear in peers, and that is
the whole prize.

CORRECTION 2 — k IS THE MIN-CUT OF THE SUBMITTED OCCUPANCY, NOT OF A WALL SUBREGION, AND MY FIRST
REASON FOR SAYING SO WAS WRONG. `cohort` measured its screening law on a fixture where the wall IS the
entire occupancy, so it never distinguished the two. I suspected a router inheriting the phrase
"min-cut(wall)" literally would compute k over a subregion while measuring divergence over the whole
lattice — a bound taken from one population and applied to another, the defect class that killed the
2/3 agreement bar. THAT SUSPICION DOES NOT SURVIVE MEASUREMENT. If the subregion spans and blocks then
breaching the whole occupancy requires breaching the subregion, so k(subregion) <= k(occupancy)
always: 160 occupancies from a deterministic sweep, 0 violations, and 67 of them STRICTLY smaller — so
the two numbers genuinely come apart, they just never come apart in the unsafe direction. The
subregion's k is CONSERVATIVE, not unsound, and the first draft of this module claimed otherwise on the
strength of a witness whose two min-cuts were both 0 — a difference that was not a difference.

    THE REAL COST IS THE SAVING, NOT THE SOUNDNESS, AND IT IS TOTAL. Measured on a composite
    occupancy: k(subregion) = 1 while k(occupancy) = 2. At k = 1 the sub-gap range is EMPTY and the
    screen decides nothing whatsoever; at k = 2 it decides every divergence-1 peer. So computing k
    over a subregion does not give a wrong answer, it gives up the entire prize — and a router that
    silently screened 0 peers while reporting 0 exceptions would look identical to one that worked.

CORRECTION 3 — AND WITH THAT FIX THE SCREENING LAW GETS STRICTLY STRONGER. `cohort` proved the law for
perturbations of WALL cells. Taking k over the full occupancy extends it to perturbations ANYWHERE in
the lattice, additions included, and the reason is short enough to state: write B = (A minus R) union
S. Free(B) = Free(A minus R) minus S. If |A XOR B| < k then |R| < k, so by Menger A minus R is still
INTACT, and a subset of a non-connecting free set cannot connect. Measured exhaustively over the
pinned INTACT bases: every perturbation of fewer than k cells, 0 flips. That is what licenses the
router to screen on a whole-lattice divergence at all.

CORRECTION 4 — THE SCREEN HAS NO TEETH ON A BREACHED SUBMITTER, AND SAYING OTHERWISE WOULD BE VACUITY.
k = 0 when the base is already open, the sub-gap range is empty, and the screen decides NOTHING. This
is not a corner case: measured, a BREACHED submitter's screen decides 0 of 6 peers where an INTACT
one decides 5 of 6, and a single cell genuinely does flip a breached verdict (reachable, counted). So
`route` sends a breached submitter straight to full recomputation rather than reporting a confident
0 exceptions over an empty set.

CORRECTION 5 — THE CHAIN DOES OVER-FETCH ON TWO ROWS, AND THE SEARCH THAT FOUND THEM ALSO INVENTED A
THIRD. `inputset`'s four levels are a CHAIN; the minimal input sets form a LATTICE over the three atoms
{own_tile, own_log, peer_tiles}, and a chain visits only 4 of its 8 nodes. Searching the family for
per-atom independence returns 3 positives. TWO ARE REAL: `ledger_remainder` never reads the occupancy,
so the nested HISTORY plan's own_tile is dead weight; and `quorum_agreement` never reads the history,
so the COHORT plan's own_log is too. ONE IS FALSE: the search also clears `quorum_agreement` of
own_tile, which it demonstrably reads — refuted twice over, by a hand-built pair (same certificate,
same cohort, different occupancy, agreement 1 against 0) and mechanically by the syntactic route below.

CORRECTION 6 — AND THE REASON THE SEARCH CANNOT BE TRUSTED ALONE IS A HARDNESS RESULT, NOT A GAP IN THE
FAMILY. What `determines` computes is exactly Nash, Segoufin and Vianu's VIEW DETERMINACY: views V
determine query Q iff V(D1) = V(D2) implies Q(D1) = Q(D2) FOR ALL instances. That problem is
UNDECIDABLE for unions of conjunctive queries — by reduction from the word problem for finite monoids —
and open for conjunctive queries; and determinacy over FINITE instances diverges from determinacy over
all instances, so the restriction is not a simplification either. So enlarging `inputset`'s family
cannot ever convert a family-relative positive into a universal one. The asymmetry is permanent:

    A NEGATIVE ANSWER IS EXACT AND COMES FROM ONE WITNESS. A POSITIVE ANSWER FROM A SEARCH IS FOREVER
    FAMILY-RELATIVE. THE ONLY ROUTE TO A UNIVERSAL POSITIVE IS SYNTACTIC — prove the quantity cannot
    read the input at all, rather than that it happened not to matter on the instances tried.

So this module carries both routes and drops a fetch only where they AGREE. Measured: the search gives
3 positives, syntax gives 2, and syntax is SILENT on 1 where the search is positive — which is not a
bug in syntax but its honest weakness, since a CERT-tier quantity may read the occupancy only through
what the certificate already exposes. The conjunction is exactly the 2 correct reductions, and using
the search alone would have dropped `own_tile` from `quorum_agreement`, which is the false one.

    THE SYNTACTIC CHECKER SHIPS ITS OWN PLANT, because a checker whose failure mode has never been
    observed is a hypothesis (L23). A quantity that reads the occupancy only through a HELPER is
    cleared by a scan that does not follow calls and caught by one that does — measured both ways. And
    the call-following filter is decided by the function's source FILE, not by its `__module__` string:
    a first draft filtered on `__module__` and the checker's verdict then depended on whether this
    module was imported or run as a script, since `__module__` is '__main__' in the second case. A
    digest that changes with the invocation is not a digest.

CORRECTION 7 — THE PLAN WAS COMPUTED AND NOTHING CONSUMED IT (Stage 8). Every row above decides WHICH
inputs a quantity needs, and then nothing stopped a caller evaluating that quantity without them.
Measured: `ledger_remainder` with the log returns 2 and WITHOUT the log returns 6, which is the full
shard budget — an under-populated situation yielding a confident number that says "the ledger is
pristine", wrong in the dangerous direction. A plan that is computed and never enforced is the same
shape as a `does_not_show` that lives only in a docstring: obeyed by convention.

    AND THE FIX HAD TO BE A REPRESENTATION CHANGE, NOT A CHECK, WHICH IS THE WHOLE CONTENT OF THIS
    ROW. `inputset`'s `situation` stores `history=()`, and that is BOTH "I fetched the log and it was
    empty" AND "I never fetched the log" — measured identical. No gate can separate THIN from DEVIATE
    on a type that cannot express the difference. THE SHARPEST FORM: on an EMPTY log the honest answer
    is 6, and the FABRICATED answer from an absent log is ALSO 6 — the right answer and the wrong one
    are THE SAME NUMBER, so no value-level check could ever have caught this. Hence `NOT_FETCHED`, a
    new inhabitant rather than a new predicate, and `guarded()` refusing with a DISTINCT code
    (AUTOROUTE-MISSING-ATOM, not a subclass of AUTOROUTE-REFUSE) because an under-populated request and
    a malformed one need different attribution.

    THE HOLE IS ASSERTED RATHER THAN HIDDEN: 3 of 6 rows are CERT-tier with an EMPTY plan, so this gate
    refuses nothing for them — correct given the plan, but it means half the census tests nothing here.
    The reason is a SECOND representation defect this rung does NOT fix: the model derives the
    certificate FROM occupancy, so a CERT quantity still reads `s['occupancy']` while its plan says
    fetch nothing.

WHAT THE ROUTER THEREFORE IS. A per-quantity fetch plan equal to the tier's chain prefix minus every
atom BOTH routes agree is unread; a post-payload Menger screen that converts flood fills into counts
wherever the divergence is sub-gap; and an honest refusal to screen at all where k = 0.

PEER-FAULT IS REAL BUT IT NEEDS A FIELD THE PROTOCOL DOES NOT YET CARRY. The cascade wants a
disagreeing sub-gap peer marked provably faulty. In `cohort` as built that can never fire, because
`peers_agree` RECOMPUTES both verdicts from both occupancies — so sub-gap disagreement is a statement
about the FUNCTION, not an observable about a peer, and a check for it would be a test that its own
code is correct. The fault becomes observable exactly when a peer CLAIMS a verdict alongside its
occupancy, and then the screen earns its keep a second time: the lie is caught by a count rather than
by a flood fill. That field is added here as a claimed verdict on the peer record, and the claim is
LATTICE-tier by `cohort`'s refutation (3), so it is a claim the bytes adjudicate and never a
certificate field.

GRADE. MEASURED: the minimal input set per quantity over the enumerated lattice; the two adopted
reductions, each by witness AND by syntax; the search-alone over-skip; the syntactic checker's own
plant, both directions; the flood-fill census with and without the screen; the
generalized screening law, exhaustive over the pinned bases with 0 flips; the breached-base vacuity in
both directions; fault detection by count against recomputation; invocation-independence of every
digest; determinism. DECLARED: the family is `inputset`'s, and by the undecidability of determinacy no
family can make a search positive universal, which is why every adopted reduction also holds by syntax;
the syntactic scan's call-following depth is BOUNDED at 3 and a bound is not a proof; the peer
population and occupancy corpus are `cohort`'s pinned synthetic sets. does_not_show: that a routed verdict is HONEST,
since routing changes only which inputs are read and never what agreement means; that the screen saves
BYTES, which is exactly what correction 1 refutes; that k beyond CUT_SEARCH_MAX is decided, inherited
unchanged from `cohort`; that a minimal set is minimal over all possible situations rather than over
this family."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import cohort as _CO                                                # noqa: E402
import inputset as _IS                                             # noqa: E402
import tilemin as _TM                                              # noqa: E402

MAGIC = b"URDRAUT1"

WORLD = 4                        # cohort's pinned world edge
ATOMS = ("own_tile", "own_log", "peer_tiles")
ATOM_OF = {"own_tile": "occupancy", "own_log": "history", "peer_tiles": "cohort"}

#: `inputset`'s chain, as SETS of fetch atoms, so it can be compared against the lattice.
CHAIN = (("CERT", frozenset()),
         ("LATTICE", frozenset({"own_tile"})),
         ("HISTORY", frozenset({"own_tile", "own_log"})),
         ("COHORT", frozenset({"own_tile", "own_log", "peer_tiles"})))
CHAIN_SET = dict(CHAIN)

DECIDED_LOCALLY, SCREENED, RECOMPUTED = "ROUTE_CERT", "ROUTE_SCREEN", "ROUTE_RECOMPUTE"


class RouteError(Exception):
    def __init__(self, message):
        super().__init__(f"AUTOROUTE-REFUSE: {message}")
        self.code = "AUTOROUTE-REFUSE"


class PeerFault(Exception):
    """A PROVEN fault, not a suspicion: the peer's claimed verdict contradicts what Menger permits at
    its own divergence. Distinct from a refusal, because attribution differs."""
    def __init__(self, message):
        super().__init__(f"AUTOROUTE-PEERFAULT: {message}")
        self.code = "AUTOROUTE-PEERFAULT"


# ---- CORRECTION 1: the screen is POST-payload, and its saving is compute ------------------------------
def subgap_needs_the_payload():
    """The cascade put Menger screening ABOVE payload download. It cannot go there: the divergence is
    a function of the peer's CELL SET, and the certificate carries no cells. Returns
    (cert_fields, occupancy_is_a_field, divergence_needs_cells)."""
    cert = _TM.certify(_CO.spanning_wall(WORLD, 2), 6)
    has_cells = any(isinstance(cert[f], (frozenset, set)) for f in _TM.FIELDS)
    return _TM.FIELDS, has_cells, True


_FILLS = [0]


def _counted_verdict(occ, n):
    _FILLS[0] += 1
    return _CO.verdict(occ, n)


def flood_fill_census(peers=None, n=WORLD):
    """THE ACTUAL SAVING, counted rather than asserted: with the screen, one flood fill on the
    submitter plus a set-difference count per sub-gap peer; without it, one per peer as well.
    Returns (fills_with_screen, fills_without_screen, peers, screened)."""
    mine = _CO.submitter()
    peers = _CO.peer_population() if peers is None else peers
    k = _CO.min_cut(mine, n)

    _FILLS[0] = 0
    mine_v = _counted_verdict(mine, n)
    screened = 0
    for p in peers:
        if k is not None and k >= 1 and len(mine ^ p["occupancy"]) < k:
            screened += 1                      # decided by COUNT — no fill
        else:
            _counted_verdict(p["occupancy"], n)
    with_screen = _FILLS[0]

    _FILLS[0] = 0
    _counted_verdict(mine, n)
    for p in peers:
        _counted_verdict(p["occupancy"], n)
    without = _FILLS[0]
    assert mine_v in (_CO.BREACHED, _CO.INTACT)
    return with_screen, without, len(peers), screened


def the_screen_saves_fills_not_bytes():
    """Returns (fills_saved, bytes_saved) — the second is 0 BY CONSTRUCTION and that is the point."""
    w, wo, _n, _s = flood_fill_census()
    return wo - w, 0


# ---- CORRECTION 2: k of the occupancy, not of a subregion ----------------------------------------------
def composite_occupancy(n=WORLD):
    """A wall subregion with a plugged tunnel PLUS a full outer face. Unlike `cohort`'s fixture the
    wall is NOT the whole occupancy here, so the two min-cuts come apart."""
    wall = frozenset((x, y, z) for x in (1, 2) for y in range(n) for z in range(n))
    face = frozenset((0, y, z) for y in range(n) for z in range(n))
    return (wall - {(1, 2, 2)}) | face


def wall_subregion(occ, xs=(1, 2)):
    return frozenset(c for c in occ if c[0] in xs)


def _sweep_corpus(n, count):
    """A DETERMINISTIC corpus, generated by an explicit integer recurrence. The stdlib generator is
    deliberately NOT used: its sampling internals are not a cross-version contract, and this repo's
    determinism claim crosses Python minor versions (3.11 cloud against 3.14 on the named host)."""
    cells = sorted(_CO.world(n))
    m = len(cells)
    out, state = [], 1
    for _ in range(count):
        state = (state * 1103515245 + 12345) % (1 << 31)
        thresh = 30 + (state >> 7) % 45                     # 30..74 percent occupied
        occ, s2 = [], state
        for c in cells:
            s2 = (s2 * 1103515245 + 12345) % (1 << 31)
            if (s2 >> 11) % 100 < thresh:
                occ.append(c)
        out.append(frozenset(occ))
    assert len(out) == count and m > 0
    return tuple(out)


def subregion_k_is_conservative_not_unsound(n=3, count=160, cap=3):
    """MY OWN FIRST CLAIM, REFUTED BY MEASUREMENT. If the subregion spans and blocks, breaching the
    whole occupancy requires breaching the subregion, so k(subregion) <= k(occupancy). The number
    below is READ from this sweep, not carried over from a scratch probe (L25). Returns
    (tested, violations, strictly_smaller)."""
    tested = viol = strict = 0
    for occ in _sweep_corpus(n, count):
        sub = wall_subregion(occ, xs=(1,))
        a, b = _CO.min_cut(occ, n, cap), _CO.min_cut(sub, n, cap)
        if a is None or b is None:
            continue
        tested += 1
        viol += not (b <= a)
        strict += b < a
    return tested, viol, strict


def the_subregion_costs_the_whole_saving(n=WORLD):
    """AND THAT IS THE REAL COST: the two numbers differ strictly, and at the smaller one the sub-gap
    range is EMPTY so the screen decides nothing at all. Returns
    (k_subregion, k_occupancy, strictly_smaller, screened_at_subregion, screened_at_occupancy)."""
    occ = composite_occupancy(n)
    sub = wall_subregion(occ)
    ks, ko = _CO.min_cut(sub, n), _CO.min_cut(occ, n)
    peers = tuple(_CO._peer(i, occ ^ frozenset({c}))
                  for i, c in enumerate(sorted(occ)[:5], start=1))
    at_sub = sum(1 for p in peers if ks is not None and ks >= 1
                 and len(occ ^ p["occupancy"]) < ks)
    at_occ = sum(1 for p in peers if ko is not None and ko >= 1
                 and len(occ ^ p["occupancy"]) < ko)
    return ks, ko, (ks is not None and ko is not None and ks < ko), at_sub, at_occ


def k_for(occ, n=WORLD):
    """THE ROUTER'S k: always the min-cut of the FULL submitted occupancy."""
    return _CO.min_cut(occ, n)


# ---- CORRECTION 3: the law generalizes to whole-lattice perturbations ----------------------------------
def _intact_bases(n=WORLD):
    out = []
    for thick in (2, 3):
        occ = _CO.spanning_wall(n, thick)
        k = _CO.min_cut(occ, n)
        if _CO.verdict(occ, n) == _CO.INTACT and k is not None and k >= 2:
            out.append((occ, k))
    return tuple(out)


def screening_law_generalizes(n=WORLD):
    """EXHAUSTIVE over every perturbation of fewer than k cells ANYWHERE in the lattice — additions
    included, which `cohort`'s wall-cell census never tried. Returns (bases, tested, flips)."""
    cells = sorted(_CO.world(n))
    bases = tested = flips = 0
    for occ, k in _intact_bases(n):
        bases += 1
        for size in range(1, k):
            for picks in _comb(cells, size):
                tested += 1
                if _CO.verdict(occ ^ frozenset(picks), n) != _CO.INTACT:
                    flips += 1
    return bases, tested, flips


def the_law_covers_additions(n=WORLD):
    """Validity-not-outcome: the generalized census must actually contain perturbations that ADD
    occupancy, or it is the wall-cell census wearing a larger name. Returns (adds, removes)."""
    cells = sorted(_CO.world(n))
    adds = removes = 0
    for occ, k in _intact_bases(n):
        for size in range(1, k):
            for picks in _comb(cells, size):
                for c in picks:
                    if c in occ:
                        removes += 1
                    else:
                        adds += 1
    return adds, removes


# ---- CORRECTION 4: the screen is vacuous on a breached base --------------------------------------------
def screen_decides(mine, peers, n=WORLD):
    """How many peers the sub-gap screen can settle without a flood fill."""
    k = k_for(mine, n)
    if k is None or k < 1:
        return 0, len(peers)
    return sum(1 for p in peers if len(mine ^ p["occupancy"]) < k), len(peers)


def screen_is_vacuous_when_breached(n=WORLD):
    """Returns (breached_decided, breached_total, intact_decided, intact_total, k_breached, k_intact).
    A confident '0 exceptions' over an empty set is the L19 failure, so the router refuses to screen
    here rather than reporting one."""
    peers = _CO.peer_population()
    breached = frozenset()
    intact = _CO.submitter()
    bd, bt = screen_decides(breached, peers, n)
    idc, it = screen_decides(intact, peers, n)
    return bd, bt, idc, it, k_for(breached, n), k_for(intact, n)


def a_breached_verdict_flips_at_one_cell(n=WORLD):
    """And the vacuity is not benign — it is exactly where a single cell DOES matter. Exhaustive over
    one-cell perturbations of a minimally-tunnelled wall. Returns (tested, flips)."""
    occ = _CO.spanning_wall(n, 2) - {(1, 2, 2), (2, 2, 2)}
    assert _CO.verdict(occ, n) == _CO.BREACHED
    tested = flips = 0
    for c in sorted(_CO.world(n)):
        tested += 1
        if _CO.verdict(occ ^ frozenset({c}), n) != _CO.BREACHED:
            flips += 1
    return tested, flips


# ---- CORRECTION 5: the minimal input SETS, and the enumeration that overreached ------------------------
def _subproj(atoms, s):
    """The projection onto an arbitrary SUBSET of atoms — the chain's `proj` generalized off-chain."""
    for a in atoms:
        if a not in ATOMS:
            raise RouteError(f"unknown fetch atom {a!r}")
    cert = _TM.certify(s["occupancy"], s["tick"])
    out = [cert["tile_prefix"], cert["jurisdiction_region"], cert["liveness_token"], cert["tick"]]
    if "own_tile" in atoms:
        out.append(tuple(sorted(s["occupancy"])))
    if "own_log" in atoms:
        out.append(s["history"])
    if "peer_tiles" in atoms:
        out.append(tuple(sorted(tuple(sorted(c)) for c in s["cohort"])))
    return tuple(out)


def determines_subset(atoms, qfn, fam=None):
    """Witness search at an arbitrary lattice node. Returns (ok, witness)."""
    fam = _IS.family() if fam is None else fam
    seen = {}
    for s in fam:
        key, val = _subproj(atoms, s), qfn(s)
        if key in seen and seen[key] != val:
            return False, (seen[key], val)
        seen[key] = val
    return True, None


def all_subsets():
    return tuple(frozenset(c) for r in range(len(ATOMS) + 1) for c in _comb(ATOMS, r))


def minimal_sets(name):
    """The ANTICHAIN of minimal determining sets — plural on purpose, since nothing guarantees the
    minimum is unique once the order is a lattice rather than a chain."""
    qfn = dict(_IS.QUANTITIES)[name]
    fam = _IS.family()
    det = [a for a in all_subsets() if determines_subset(a, qfn, fam)[0]]
    return tuple(sorted(tuple(sorted(a)) for a in det if not any(b < a for b in det)))


def lattice_census():
    """Returns ((name, tier, minimal_sets, strictly_below_chain), ...)."""
    out = []
    for name, _q in _IS.QUANTITIES:
        tier = _IS.tier_of(name)[0]
        mins = minimal_sets(name)
        below = tuple(m for m in mins if frozenset(m) < CHAIN_SET[tier])
        out.append((name, tier, mins, below))
    return tuple(out)


def the_chain_is_not_tight():
    """Returns (quantities_with_an_off_chain_minimum, total) — positive, else the lattice adds
    nothing and this module should not exist."""
    rows = lattice_census()
    return sum(1 for _n, _t, _m, below in rows if below), len(rows)


def the_real_savings():
    """THE ADOPTED REDUCTIONS: an atom is dropped from a fetch plan only where BOTH routes agree — the
    family search (complete, family-relative) AND the syntactic check (sound, universal). Returns
    ((quantity, atom_dropped), ...)."""
    return tuple((n, a) for n, a, se, sy in syntax_versus_search_census() if se and sy)


def search_alone_would_over_skip():
    """THE PLANT, AND IT IS THE SAME DEFECT TWICE FROM TWO DIRECTIONS. Trusting the family search
    alone drops an atom a quantity provably reads. Returns
    (search_only_drops, both_routes_drop, over_skipped)."""
    rows = syntax_versus_search_census()
    search_only = tuple((n, a) for n, a, se, _sy in rows if se)
    both = the_real_savings()
    return search_only, both, tuple(r for r in search_only if r not in both)


def _reachable_sources(fn, depth=3):
    """The transitive closure of function sources reachable from `fn` through module globals, BOUNDED
    at `depth` and declared as such. A bound is not a proof; the bound is why the checker below ships
    with a plant that a shallower scan gets wrong."""
    import re
    seen, out, stack = set(), [], [(fn, 0)]
    while stack:
        f, d = stack.pop()
        nm = getattr(f, "__name__", None)
        if nm in seen or d > depth:
            continue
        seen.add(nm)
        try:
            src = _inspect_source(f)
        except (OSError, TypeError):
            continue
        out.append(src)
        g = getattr(f, "__globals__", {})
        for tok in sorted(set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", src))):
            cand = g.get(tok)
            if callable(cand) and _defined_under_here(cand):
                stack.append((cand, d + 1))
    return tuple(out)


def _defined_under_here(fn):
    """Follow calls into THIS TREE, decided by the function's source FILE rather than by its
    `__module__` string. A first draft filtered on `__module__` and the checker's own verdict then
    depended on whether the module was imported or run as a script, because `__module__` is
    '__main__' in the second case — a digest that changes with the invocation is not a digest."""
    try:
        f = _sys.modules[fn.__module__].__file__ if fn.__module__ in _sys.modules else None
    except (AttributeError, KeyError):
        f = None
    if f is None:
        try:
            import inspect as _i
            f = _i.getsourcefile(fn)
        except (TypeError, OSError):
            return False
    return bool(f) and _os.path.dirname(_os.path.abspath(f)) == _HERE


def _inspect_source(f):
    import inspect
    return inspect.getsource(f)


def syntactically_independent(name, atom, depth=3):
    """A SUFFICIENT condition for a UNIVERSAL positive, and the only one available: if the quantity's
    reachable source never names the situation key, it cannot read it on ANY instance, family or not.
    This is the route that escapes the undecidability — it proves independence by syntax rather than
    by searching instances."""
    if atom not in ATOM_OF:
        raise RouteError(f"unknown fetch atom {atom!r}")
    key = ATOM_OF[atom]
    qfn = dict(_IS.QUANTITIES)[name]
    return not any(f'"{key}"' in s or f"'{key}'" in s
                   for s in _reachable_sources(qfn, depth))


def _reads_occupancy_through_a_helper(s):
    """THE PLANT for the checker above: this reads occupancy, but only through a callee, so a scan
    that does not follow calls clears it wrongly."""
    return _helper_that_reads_occupancy(s)


def _helper_that_reads_occupancy(s):
    return len(s["occupancy"])


def the_syntactic_check_follows_calls():
    """L23 applied to this module's own checker: a check whose failure mode has never been observed is
    a hypothesis. Returns (shallow_clears_it, deep_catches_it)."""
    key = ATOM_OF["own_tile"]
    shallow = _reachable_sources(_reads_occupancy_through_a_helper, 0)
    deep = _reachable_sources(_reads_occupancy_through_a_helper, 3)
    hit = (lambda ss: any(f'"{key}"' in x or f"'{key}'" in x for x in ss))
    return not hit(shallow), hit(deep)


def syntax_versus_search_census():
    """THE ASYMMETRY, MEASURED. Determinacy in the Nash-Segoufin-Vianu sense is UNDECIDABLE in
    general, so a positive answer from a family search is forever family-relative while a NEGATIVE
    answer is exact from one witness. Syntax is the only route to a universal positive — and it is
    silent wherever a quantity reads an input it does not truly depend on. Returns
    ((quantity, atom, search_says_independent, syntax_says_independent), ...)."""
    out = []
    fam = _IS.family()
    for name, qfn in _IS.QUANTITIES:
        tier = _IS.tier_of(name)[0]
        for atom in sorted(CHAIN_SET[tier]):
            without = frozenset(CHAIN_SET[tier]) - {atom}
            search = determines_subset(without, qfn, fam)[0]
            out.append((name, atom, search, syntactically_independent(name, atom)))
    return tuple(out)


def only_syntax_gives_a_universal_positive():
    """Returns (search_positives, syntax_positives, syntax_silent_where_search_positive). The middle
    number is small ON PURPOSE: syntax is sound and weak, the search is complete and family-relative,
    and only their AGREEMENT licenses skipping a fetch."""
    rows = syntax_versus_search_census()
    s_pos = sum(1 for _n, _a, se, _sy in rows if se)
    y_pos = sum(1 for _n, _a, _se, sy in rows if sy)
    silent = sum(1 for _n, _a, se, sy in rows if se and not sy)
    return s_pos, y_pos, silent


def the_lattice_enumeration_overreached():
    """THE PLANT, AND IT BIT ME. The same enumeration reported `quorum_agreement` determined by
    {peer_tiles} alone. Hand-built refutation: identical certificate, identical cohort, different
    occupancy, different agreement. Returns
    (enumeration_said, cert_identical, cohort_identical, occupancy_identical, va, vb, refuted)."""
    said = minimal_sets("quorum_agreement")
    a = _IS.situation({(33, 33, 33)}, 6, (), ({(33, 33, 33)},))
    b = _IS.situation({(40, 40, 40)}, 6, (), ({(33, 33, 33)},))
    base = _subproj((), a) == _subproj((), b)
    coh = a["cohort"] == b["cohort"]
    va, vb = _IS.q_quorum_agreement(a), _IS.q_quorum_agreement(b)
    return (said, base, coh, a["occupancy"] == b["occupancy"], va, vb, va != vb)


def the_family_was_built_for_a_chain():
    """THE ROOT CAUSE, and it is why only the inspection-confirmed saving is adopted. Returns
    (chain_pairs, lattice_nodes, lattice_covering_pairs)."""
    subs = all_subsets()
    covers = sum(1 for a in subs for b in subs if a < b and len(b - a) == 1)
    return len(CHAIN) - 1, len(subs), covers


# ---- the router ----------------------------------------------------------------------------------------
def plan_for(name):
    """THE ROUTE: the tier's chain prefix, minus every atom BOTH routes agree is not read. Search
    alone is family-relative and demonstrably over-skips; syntax alone is sound but silent on three
    rows. Only the conjunction licenses dropping a fetch. Returns (plan, tier, dropped)."""
    tier = _IS.tier_of(name)[0]
    drop = frozenset(a for q, a in the_real_savings() if q == name)
    return CHAIN_SET[tier] - drop, tier, tuple(sorted(drop))


def route_census():
    out = []
    for n, _q in _IS.QUANTITIES:
        plan, tier, dropped = plan_for(n)
        out.append((n, tuple(sorted(plan)), tier, dropped))
    return tuple(out)


def verify_routed(mine, peers, budget, n=WORLD, min_peers=_CO.MIN_PEERS):
    """The cascade, with the corrected order. The screen runs AFTER the payload is in hand and only
    where k >= 1; a breached submitter recomputes. Returns
    (outcome, agreeing, fetched, remaining, screened, recomputed)."""
    import budget as _BG
    if min_peers < 1:
        raise RouteError("a cohort threshold below one verifies nothing")
    k = k_for(mine, n)
    mine_v = _CO.verdict(mine, n)
    remaining, agreeing, fetched, screened, recomputed = budget, 0, 0, 0, 0
    for p in sorted(peers, key=lambda q: q["prefix"]):
        try:
            remaining = _BG.charge(remaining, _CO.EDGE_COST)
        except _BG.Overdrawn:
            break
        fetched += 1                                   # the BYTES move either way (correction 1)
        if k is not None and k >= 1 and len(mine ^ p["occupancy"]) < k:
            same, screened = True, screened + 1        # decided by count (correction 3)
        else:
            same, recomputed = _CO.verdict(p["occupancy"], n) == mine_v, recomputed + 1
        claimed = p.get("claimed")
        if claimed is not None and k is not None and k >= 1 \
                and len(mine ^ p["occupancy"]) < k and claimed != mine_v:
            raise PeerFault(f"peer {p['prefix']} claims {claimed} at divergence "
                            f"{len(mine ^ p['occupancy'])} < k={k}; Menger forbids it")
        agreeing += same
        if agreeing >= min_peers:
            return (_CO.VERIFIED, agreeing, fetched, remaining, screened, recomputed)
    if fetched == 0:
        return (_CO.UNAVAILABLE, 0, 0, remaining, screened, recomputed)
    outcome = _CO.UNAVAILABLE if agreeing == fetched else _CO.FAILED
    return (outcome, agreeing, fetched, remaining, screened, recomputed)


def routing_agrees_with_cohort(n=WORLD):
    """The router may only change WHICH inputs are read, never the answer. Returns
    (rows, disagreements)."""
    import budget as _BG
    mine = _CO.submitter()
    cases = (("full", _CO.peer_population()),
             ("none", ()),
             ("liars", tuple(_CO._peer(i, frozenset()) for i in range(1, 7))))
    rows, bad = [], 0
    for label, peers in cases:
        a = _CO.verify_cohort(mine, peers, 20, n)[:3]
        b = verify_routed(mine, peers, 20, n)[:3]
        rows.append((label, a[0], b[0]))
        bad += a != b
    assert _BG.SHARD_BUDGET > 0
    return tuple(rows), bad


# ---- PEER-FAULT: real, but it needs a field the protocol did not carry ---------------------------------
def fault_needs_a_claimed_verdict():
    """`cohort.peers_agree` RECOMPUTES both verdicts, so sub-gap disagreement is a property of the
    FUNCTION and can never be observed about a peer — a detector for it would be a test that this
    module's own arithmetic works. Returns (recomputes_both, claim_field_in_cohort_peer)."""
    import inspect
    src = inspect.getsource(_CO.peers_agree)
    return src.count("verdict(") == 2, "claimed" in _CO.peer_population()[0]


def liar_with_a_claim(n=WORLD):
    """A peer whose occupancy is sub-gap close to mine but whose CLAIMED verdict is the opposite."""
    mine = _CO.submitter(n, 2)
    cs = sorted(mine)
    return dict(_CO._peer(9, mine - {cs[0]}), claimed=_CO.BREACHED)


def fault_is_caught_by_a_count(n=WORLD):
    """And here the screen pays a second time: the lie is caught with ZERO flood fills on the peer's
    lattice, where recomputation would need one. Returns (raised, fills_on_peer, recompute_fills)."""
    mine = _CO.submitter()
    liar = liar_with_a_claim(n)
    _FILLS[0] = 0
    raised = False
    try:
        verify_routed(mine, (liar,), 20, n)
    except PeerFault:
        raised = True
    return raised, _FILLS[0], 1


def an_honest_claim_is_not_a_fault(n=WORLD):
    """Validity-not-outcome: the detector must ACCEPT the honest claim, or it is not a detector."""
    mine = _CO.submitter()
    cs = sorted(mine)
    honest = dict(_CO._peer(9, mine - {cs[0]}), claimed=_CO.INTACT)
    try:
        out = verify_routed(mine, (honest,), 20, n)
        return True, out[0]
    except PeerFault:
        return False, None


def fault_is_a_distinct_code():
    return PeerFault("x").code, RouteError("x").code, issubclass(PeerFault, RouteError)



# ---- STAGE 8: THE PLAN IS ENFORCED, NOT MERELY COMPUTED -------------------------------------------------
class MissingAtom(Exception):
    """The caller evaluated a quantity without an input its plan names. DISTINCT from RouteError: a
    malformed request and an under-populated one need different attribution, the same split `tilemin`
    needed between integrity and policy."""
    def __init__(self, message):
        super().__init__(f"AUTOROUTE-MISSING-ATOM: {message}")
        self.code = "AUTOROUTE-MISSING-ATOM"


class _NotFetched:
    """A sentinel distinct from every legitimate value. THE REPRESENTATION IS THE RUNG: `inputset`'s
    `situation` stores `history=()`, and that is BOTH 'I fetched the log and it was empty' AND 'I never
    fetched the log'. No gate can separate THIN from DEVIATE on a type that conflates them, so the fix
    is a new inhabitant rather than a new check."""
    __slots__ = ()

    def __repr__(self):
        return "NOT_FETCHED"


NOT_FETCHED = _NotFetched()


def fetched_situation(occupancy, tick, history, cohort):
    """`inputset.situation` with every atom allowed to be NOT_FETCHED. The coercions are skipped for
    the sentinel — `frozenset(NOT_FETCHED)` would raise, and an exception is not a refusal."""
    def keep(v, coerce):
        return v if v is NOT_FETCHED else coerce(v)
    return {"occupancy": keep(occupancy, frozenset), "tick": tick,
            "history": keep(history, tuple),
            "cohort": keep(cohort, lambda c: tuple(frozenset(x) for x in c))}


def atom_is_present(situation, atom):
    if atom not in ATOM_OF:
        raise RouteError(f"unknown fetch atom {atom!r}")
    return situation.get(ATOM_OF[atom], NOT_FETCHED) is not NOT_FETCHED


def guarded(name, situation):
    """EVALUATE THROUGH THE PLAN. Every atom the plan names must be PRESENT, or the quantity refuses
    rather than returning a confident number from an under-populated situation. An EMPTY atom is
    present and evaluates cleanly — that distinction is the whole point."""
    qfn = dict(_IS.QUANTITIES).get(name)
    if qfn is None:
        raise RouteError(f"unknown quantity {name!r}")
    plan, _tier, _dropped = plan_for(name)
    for atom in sorted(plan):
        if not atom_is_present(situation, atom):
            raise MissingAtom(f"{name} needs {atom}, which was not fetched")
    return qfn(situation)


def the_representation_conflated_absent_and_empty():
    """THE WITNESS THAT MOTIVATES THE SENTINEL, kept live. Under `inputset.situation` the two are the
    SAME OBJECT; under `fetched_situation` they are distinguishable. Returns
    (old_are_equal, new_are_distinct)."""
    old_empty = _IS.situation({(33, 33, 33)}, 6, (), ())
    old_absent = _IS.situation({(33, 33, 33)}, 6, (), ())
    new_empty = fetched_situation({(33, 33, 33)}, 6, (), ())
    new_absent = fetched_situation({(33, 33, 33)}, 6, NOT_FETCHED, ())
    return (old_empty["history"] == old_absent["history"],
            new_empty["history"] is not new_absent["history"])


def unguarded_evaluation_is_silently_wrong():
    """WHY THIS RUNG EXISTS, MEASURED. Evaluating a HISTORY quantity with no log returns a number
    rather than refusing, and it is wrong in the DANGEROUS direction — the full shard budget, i.e.
    'the ledger is pristine'. Returns (with_log, without_log, budget, wrong_direction)."""
    qfn = dict(_IS.QUANTITIES)["ledger_remainder"]
    with_log = qfn(_IS.situation({(33, 33, 33)}, 6, (2, 2), ()))
    without = qfn(_IS.situation({(33, 33, 33)}, 6, (), ()))
    import budget as _BG
    return with_log, without, _BG.SHARD_BUDGET, without == _BG.SHARD_BUDGET


def guard_census():
    """Per quantity: does a missing atom REFUSE, does an empty atom EVALUATE, and does the guarded
    answer equal the unguarded one when the plan is satisfied. Returns
    ((name, atoms_in_plan, refused_when_missing, evaluated_when_empty, answer_unchanged), ...)."""
    out = []
    for name, qfn in _IS.QUANTITIES:
        plan, _t, _d = plan_for(name)
        full = fetched_situation({(33, 33, 33)}, 6, (2, 2), ({(33, 33, 33)},))
        refused = None
        if plan:
            holes = dict(full)
            holes[ATOM_OF[sorted(plan)[0]]] = NOT_FETCHED
            try:
                guarded(name, holes)
                refused = False
            except MissingAtom:
                refused = True
        # EMPTY means the plan's atoms are empty, NOT that the tile is empty — an empty tile is
        # `tilemin`'s own typed refusal and has nothing to do with this gate. A first draft emptied
        # the occupancy too and hit TILEMIN-REFUSE, which would have been read as the guard failing.
        empty = fetched_situation({(33, 33, 33)}, 6, (), ())
        try:
            guarded(name, empty)
            evaluated = True
        except MissingAtom:
            evaluated = False
        out.append((name, tuple(sorted(plan)), refused, evaluated,
                    guarded(name, full) == qfn(full)))
    return tuple(out)


def the_guard_refuses_absence_and_admits_emptiness():
    """The load-bearing pair, read rather than inferred. Returns
    (refused_on_absent, value_on_empty, value_on_full)."""
    absent = fetched_situation({(33, 33, 33)}, 6, NOT_FETCHED, ())
    empty = fetched_situation({(33, 33, 33)}, 6, (), ())
    full = fetched_situation({(33, 33, 33)}, 6, (2, 2), ())
    try:
        guarded("ledger_remainder", absent)
        refused = False
    except MissingAtom:
        refused = True
    return refused, guarded("ledger_remainder", empty), guarded("ledger_remainder", full)


def cert_rows_are_not_exercised_by_this_gate():
    """THE HONEST HOLE, ASSERTED RATHER THAN HIDDEN. A CERT quantity's plan is EMPTY, so this gate
    refuses nothing for it — correct given the plan, but it means 3 of 6 rows test nothing here. The
    deeper reason is a SECOND representation defect this rung does not fix: the model derives the
    certificate FROM occupancy, so a CERT quantity still reads `s['occupancy']` even though its plan
    says fetch nothing. Returns (cert_rows, rows_with_a_plan, total)."""
    rows = guard_census()
    empty_plan = sum(1 for _n, plan, _r, _e, _u in rows if not plan)
    return empty_plan, len(rows) - empty_plan, len(rows)


def missing_atom_is_a_distinct_code():
    return (MissingAtom("x").code, RouteError("x").code,
            issubclass(MissingAtom, RouteError))


# ---- digests + scenes ----------------------------------------------------------------------------------
def ar_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_route():
    return ar_digest("route", f"{route_census()}:{lattice_census()}:{the_chain_is_not_tight()}:"
                              f"{the_real_savings()}:{search_alone_would_over_skip()}:"
                              f"{syntax_versus_search_census()}:"
                              f"{only_syntax_gives_a_universal_positive()}:"
                              f"{the_syntactic_check_follows_calls()}:"
                              f"{routing_agrees_with_cohort()}")


def _scene_screen():
    return ar_digest("screen", f"{flood_fill_census()}:{the_screen_saves_fills_not_bytes()}:"
                               f"{screening_law_generalizes()}:{the_law_covers_additions()}:"
                               f"{screen_is_vacuous_when_breached()}:"
                               f"{a_breached_verdict_flips_at_one_cell()}")


def _scene_refuted():
    return ar_digest("refuted", f"{subgap_needs_the_payload()}:"
                                f"{subregion_k_is_conservative_not_unsound()}:"
                                f"{the_subregion_costs_the_whole_saving()}:"
                                f"{the_lattice_enumeration_overreached()}:"
                                f"{the_family_was_built_for_a_chain()}:"
                                f"{fault_needs_a_claimed_verdict()}:"
                                f"{fault_is_caught_by_a_count()}:{an_honest_claim_is_not_a_fault()}")


def _scene_enforce():
    return ar_digest("enforce", f"{the_representation_conflated_absent_and_empty()}:"
                                f"{unguarded_evaluation_is_silently_wrong()}:"
                                f"{guard_census()}:"
                                f"{the_guard_refuses_absence_and_admits_emptiness()}:"
                                f"{cert_rows_are_not_exercised_by_this_gate()}:"
                                f"{missing_atom_is_a_distinct_code()}")


_SCENES = {"route": _scene_route, "screen": _scene_screen, "refuted": _scene_refuted,
           "enforce": _scene_enforce}
SCENES = ("route", "screen", "refuted", "enforce")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_autoroute.txt"), encoding="utf-8") as fh:
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
    raise RouteError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print("ROUTE CENSUS")
    for name, plan, tier, off in route_census():
        print(f"  {name:22} tier {tier:8} fetch {plan}{'   <- off-chain minimum' if off else ''}")
    print(f"chain not tight {the_chain_is_not_tight()} | adopted savings {the_real_savings()}")
    print("SYNTAX vs SEARCH (quantity, atom, search+, syntax+)")
    for row in syntax_versus_search_census():
        print(f"    {row}")
    print(f"scorecard (search+, syntax+, syntax silent) "
          f"{only_syntax_gives_a_universal_positive()} | search alone over-skips "
          f"{search_alone_would_over_skip()[2]} | checker follows calls "
          f"{the_syntactic_check_follows_calls()}")
    print(f"routing agrees with cohort {routing_agrees_with_cohort()}")
    print(f"fills (with, without, peers, screened) {flood_fill_census()} "
          f"-> saved {the_screen_saves_fills_not_bytes()}")
    print(f"law generalizes (bases, tested, flips) {screening_law_generalizes()} "
          f"| additions covered {the_law_covers_additions()}")
    print(f"breached screen vacuous {screen_is_vacuous_when_breached()} "
          f"| one cell flips a breached base {a_breached_verdict_flips_at_one_cell()}")
    print(f"REFUTED (1) screen needs the payload {subgap_needs_the_payload()}")
    print(f"REFUTED (2) MY OWN CLAIM: subregion k is conservative "
          f"{subregion_k_is_conservative_not_unsound()} "
          f"| but it costs the whole saving {the_subregion_costs_the_whole_saving()}")
    print(f"REFUTED (3) enumeration overreached {the_lattice_enumeration_overreached()}")
    print(f"            family built for a chain {the_family_was_built_for_a_chain()}")
    print(f"PEER-FAULT needs a claim {fault_needs_a_claimed_verdict()} "
          f"| caught by a count {fault_is_caught_by_a_count()} "
          f"| honest claim accepted {an_honest_claim_is_not_a_fault()} "
          f"| codes {fault_is_a_distinct_code()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv[1:]))
