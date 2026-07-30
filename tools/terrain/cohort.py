# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cohort — THE COHORT FETCH PROTOCOL, WITH THE GAP DERIVED (URDRCOH1): URDRINP1's taxonomy turned
into enforcement, and the agreement predicate replaced by a theorem. NO NEW GLYPH.

WHAT THIS IS. `inputset` decided that every arc quantity belongs to the coarsest input level that
determines it. That table is documentation until something makes a verifier obey it. Here the tier IS
the fetch plan, read from `inputset` rather than retyped:

    CERT     fetch nothing      verify inline
    LATTICE  fetch your tile    recompute from occupancy
    HISTORY  fetch your log     replay the ledger
    COHORT   fetch peers        recompute the verdict against other parties' submissions

THE AGREEMENT PREDICATE IS MENGER'S THEOREM, AND EVERY THRESHOLD IS GONE. Four candidate measurands
were proposed across this arc and three died by measurement. What survives:

    the verdict is CONNECTIVITY of free space between the two sides of the wall
    the gap is k = min-cut(wall), Menger's minimum vertex cut = max internally disjoint paths
    k = 0 means BREACHED, k >= 1 means INTACT, and no perturbation of fewer than k cells can flip it

MEASURED, and this is the point: a 1-thick spanning wall has k = 1, a 2-thick spanning wall has k = 2.
`THICK = 2` was never a tuned constant — it is min-cut(wall), and Menger computes it from the wall's
own geometry. So the screening law is a THEOREM rather than a threshold: below k, the verdict cannot
move. There is no Jaccard bar, no run-length gap, no persistence Delta, and nothing that grows
permissive with tile size.

    AND THE SHARPEST FORM OF THE COHORT TEST FALLS OUT FOR FREE. If a peer's occupancy differs from
    mine by fewer than k cells inside the wall, Menger says our verdicts MUST agree. A peer that
    disagrees under that condition is not merely an outlier — it is PROVABLY faulty, because the
    theorem forbids the observation. That is an impossibility check, not a tolerance.

WHAT DIED, EACH BY A PINNED WITNESS RATHER THAN AN ARGUMENT.

(1) JACCARD CELL-COUNT OVERLAP is blind to structure. Two peers diverging by identical cell counts,
    one scattered and one contiguous, produce the identical Jaccard verdict at runs 1 and 4 — the
    same wrong-units defect (L21) that `divergence` was built to refute, reproduced one layer up in
    this module's own first draft.

(2) LONGEST-RUN IS INVERTED relative to the truth. A whole wall face removed without opening a
    passage scores run 7; an actual 3-cell breach scores run 3. Run length OVER-FLAGS the
    non-breaching case, so the run-gap this rung was one step from adopting would have been wrong in
    the dangerous direction.

(3) THE BOUNDARY REDUCTION DOES NOT EXIST. The Stokes / Ward-Takahashi proposal would have created a
    tier between CERT and LATTICE by deciding breach from boundary cells alone. Refuted: two
    occupancies with BYTE-IDENTICAL boundary occupancy have opposite breach verdicts — a straight
    interior tunnel against the same face cells with the interior hole displaced. Breach is interior
    reachability and no surface sum determines it, so `inputset`'s four tiers stand and the verdict
    is LATTICE-tier. A peer's claimed verdict, or a hash of its lattice, is therefore a CLAIM; only
    the bytes verify it.

(4) THE HEX / SPERNER Z2 DUALITY IS TWO-DIMENSIONAL. In 2D, either free space crosses or the
    occupied set blocks — exhaustive and exclusive. On this 3D lattice a free tube through a solid
    slab has free space connecting along x AND the occupied set connecting along z, simultaneously.
    So there is no two-valued order parameter of that kind here, and the SSB phase diagram, Goldstone
    classification and criticality curve that rested on it are not adopted. The breach predicate
    itself is untouched — it was never the parity of anything.

THE LIMITING-LAW CAUTION IS DISCHARGED RATHER THAN INHERITED. An earlier draft carried a Guggenheim
note: the 1/2 bar was a FITTED law with a declared regime and no derivation. That caution no longer
applies, because the gap is now derived from Menger rather than fitted to a regime. The Blagden
colligative caution still stands one layer down — the defect budget counts cells and is blind to
which cell — and that remains the exchange-rate residual already named.

TWO CONSTANTS REMAIN, BOTH DECLARED AS POLICY AND NEITHER DERIVED. `WALL_MIN_K = 2` refuses to
certify a wall a single cell can open; the theorem supplies the language (k = 1 is one cell from
failing) and the choice of 2 is operational. And the budget charge is `B // max(k, 1)` — MONOTONE, not
peaked at k = 1. The criticality peak borrowed from statistical mechanics is NOT adopted, and the
honest reason is that it was never measured here: this rung measured k across wall thicknesses and did
not measure a charge curve, so "the measurement ruled out the peak" would be an inflation. Monotone is
the conservative default in the absence of the measurement, and the peak remains an open question with
its falsification protocol stated.

GRADE. MEASURED: the fetch plan agreeing with `inputset`'s decided tiers, read cross-module; k derived
per wall thickness with the screening law holding below it, 0 exceptions; the impossibility check
(sub-gap divergence with differing verdicts is forbidden); the three graded outcomes reachable and
distinct; termination of the budget-bounded loop; five plants biting, four of them refuting a proposed
measurand; determinism. DECLARED: the peer population and wall corpus are pinned synthetic sets — this
rung enforces a contract and does not model peer discovery, latency or churn; `WALL_MIN_K` and the
monotone charge are policy numbers, stated as such. does_not_show: that a COHORT_VERIFIED tile is
HONEST — agreement among peers is evidence about a population and never about truth, and a colluding
majority verifies itself, which is `geoquorum`'s residual inherited unchanged; that the criticality
charge peak is absent, since it was not measured; peer discovery latency, which is wall-clock and
outside every gate here; that centrality means anything, since it is measured and deliberately
unwired."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb, product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import budget as _BG                                                # noqa: E402
import inputset as _IS                                              # noqa: E402
import voxlat as _VX                                                # noqa: E402

MAGIC = b"URDRCOH1"
MIN_PEERS = 5                    # geoquorum's MIN_COHORT, inherited rather than re-chosen
WALL_MIN_K = 2                   # POLICY: refuse to certify a wall one cell can open
CUT_SEARCH_MAX = 3               # the min-cut enumeration is decided to this size
EDGE_COST = 1                    # budget charged per peer fetched
BASE_CHARGE = 12                 # B in the monotone charge B // max(k, 1)

BREACHED, INTACT = 0, 1
VERIFIED, UNAVAILABLE, FAILED = "COHORT_VERIFIED", "COHORT_UNAVAILABLE", "COHORT_FAILED"

FETCH_PLAN = {"CERT": (), "LATTICE": ("own_tile",),
              "HISTORY": ("own_tile", "own_log"),
              "COHORT": ("own_tile", "own_log", "peer_tiles")}


class CohortError(Exception):
    def __init__(self, message):
        super().__init__(f"COHORT-REFUSE: {message}")
        self.code = "COHORT-REFUSE"


class TooThin(Exception):
    """A POLICY refusal: the wall's own min-cut is below the certifiable floor. Not an integrity
    fault — the wall is honestly reported and honestly too fragile to certify."""
    def __init__(self, message):
        super().__init__(f"COHORT-TOOTHIN: {message}")
        self.code = "COHORT-TOOTHIN"


# ---- the tier IS the fetch plan ------------------------------------------------------------------------
def fetch_plan_for(quantity):
    """Read the tier from `inputset`. Cross-module on purpose: if that classifier moves, this moves."""
    tier, _witness = _IS.tier_of(quantity)
    return tier, FETCH_PLAN[tier]


def plan_matches_the_classifier():
    return tuple((n, ) + (lambda t: (t, len(FETCH_PLAN[t])))(_IS.tier_of(n)[0])
                 for n, _f in _IS.QUANTITIES)


def plans_are_nested():
    lv = _IS.LEVELS
    return all(set(FETCH_PLAN[a]) <= set(FETCH_PLAN[b]) for a, b in zip(lv, lv[1:]))


def threshold_is_geoquorums():
    import geoquorum as _GQ
    return MIN_PEERS == _GQ.MIN_COHORT, MIN_PEERS


# ---- the world, the wall, and the verdict --------------------------------------------------------------
def world(n):
    return tuple(_prod(range(n), repeat=3))


def spanning_wall(n, thick):
    """A wall that ACTUALLY spans the cross-section. A first draft's fixture did not, so free space
    walked around it and every min-cut came back 1 — the number was measuring a wall that never
    blocked anything."""
    if not (1 <= thick < n):
        raise CohortError(f"thickness {thick} does not fit a world of {n}")
    return frozenset((x, y, z) for x in range(1, 1 + thick)
                     for y in range(n) for z in range(n))


def free_reaches(occ, n, axis=0):
    """THE MEASURAND: is the low face reachable from the high face through FREE cells. Reachability on
    the integer lattice, one flood fill, no division and no threshold."""
    free = {c for c in world(n) if c not in occ}
    seen, stack = set(), [c for c in free if c[axis] == 0]
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        seen.add(c)
        for d in range(3):
            for s in (-1, 1):
                nb = list(c)
                nb[d] += s
                nb = tuple(nb)
                if 0 <= nb[d] < n and nb in free and nb not in seen:
                    stack.append(nb)
    return any(c[axis] == n - 1 for c in seen)


def verdict(occ, n):
    """BREACHED or INTACT. One bit, and it is LATTICE-tier because it needs interior adjacency —
    the boundary refutation is why no cheaper tier exists."""
    return BREACHED if free_reaches(occ, n) else INTACT


def min_cut(wall, n, cap=CUT_SEARCH_MAX):
    """MENGER'S k, DECIDED: the fewest wall cells whose removal opens a passage, which by the 1927
    duality equals the maximum number of internally vertex-disjoint paths across the wall. Returns 0
    for an already-breached wall and None if no cut of size <= cap exists."""
    if verdict(wall, n) == BREACHED:
        return 0
    for size in range(1, cap + 1):
        for s in _comb(sorted(wall), size):
            if free_reaches(wall - frozenset(s), n):
                return size
    return None


def gap_table(cases=((3, 1), (4, 1), (4, 2), (5, 1), (5, 2))):
    """THE DERIVED GAP, per wall. Returns ((n, thick, k), ...) — and k equals the thickness, which is
    why THICK was never a tuned constant."""
    return tuple((n, t, min_cut(spanning_wall(n, t), n)) for n, t in cases)


def the_gap_is_the_thickness(cases=((3, 1), (4, 1), (4, 2), (5, 1), (5, 2))):
    return all(k == t for _n, t, k in gap_table(cases))


def screening_law_census(n=4, thick=2):
    """THE THEOREM, DECIDED: no perturbation of fewer than k wall cells can flip the verdict. Returns
    (k, sub_gap_perturbations, flips) — flips must be 0, and the count must be positive."""
    wall = spanning_wall(n, thick)
    k = min_cut(wall, n)
    tried = flips = 0
    for size in range(1, max(k, 1)):
        for s in _comb(sorted(wall), size):
            tried += 1
            if verdict(wall - frozenset(s), n) != INTACT:
                flips += 1
    return k, tried, flips


def screening_law_holds(n=4, thick=2):
    k, tried, flips = screening_law_census(n, thick)
    return k is not None and k >= 2 and tried > 0 and flips == 0


# ---- the impossibility check ------------------------------------------------------------------------------
def peers_agree(mine, theirs, n):
    """AGREEMENT IS VERDICT EQUALITY. Not a graded overlap, not a distance — the same structural bit."""
    return verdict(mine, n) == verdict(theirs, n)


def sub_gap_disagreement_is_impossible(n=4, thick=2):
    """THE SHARPEST FORM, and it falls out of Menger for free: if a peer's occupancy differs from mine
    by FEWER THAN k wall cells, the theorem FORBIDS our verdicts differing. A peer that disagrees
    under that condition is provably faulty rather than merely an outlier. Returns
    (k, sub_gap_peers, impossible_observations) — the last must be 0."""
    wall = spanning_wall(n, thick)
    k = min_cut(wall, n)
    peers = impossible = 0
    for size in range(1, max(k, 1)):
        for s in _comb(sorted(wall), size):
            peers += 1
            if not peers_agree(wall, wall - frozenset(s), n):
                impossible += 1
    return k, peers, impossible


def at_or_above_the_gap_disagreement_becomes_possible(n=4, thick=2):
    """Validity-not-outcome: the impossibility above is only meaningful if disagreement IS possible at
    or above k. Returns (k, at_gap_peers, disagreements) — the last must be positive."""
    wall = spanning_wall(n, thick)
    k = min_cut(wall, n)
    peers = disagree = 0
    for s in _comb(sorted(wall), k):
        peers += 1
        if not peers_agree(wall, wall - frozenset(s), n):
            disagree += 1
    return k, peers, disagree


def certifiable(wall, n):
    """POLICY: a wall whose own min-cut is below the floor is refused. TooThin is not an integrity
    fault — the report is honest and the wall is fragile."""
    k = min_cut(wall, n)
    if k is None:
        return True
    if k < WALL_MIN_K:
        raise TooThin(f"min-cut {k} below the certifiable floor {WALL_MIN_K}")
    return True


def thin_walls_are_refused():
    """Returns (thin_refused, thick_admitted) — the dimensional guard, derived from Menger rather than
    from Mermin-Wagner, which concerns continuous symmetry at finite temperature and supplies no
    number here."""
    try:
        certifiable(spanning_wall(4, 1), 4)
        thin = False
    except TooThin:
        thin = True
    return thin, certifiable(spanning_wall(4, 2), 4)


# ---- the budget charge: monotone, and the peak NOT adopted --------------------------------------------------
def charge_for_gap(k, base=BASE_CHARGE):
    """B // max(k, 1) — integer division, monotone, no peak. A robust wall costs less because
    perturbations are screened. The criticality peak is NOT adopted and NOT refuted; it was never
    measured here, and monotone is the conservative default in the absence of that measurement."""
    if k is None:
        return 0
    if type(k) is not int or k < 0:
        raise CohortError(f"gap must be a non-negative int or None, got {k!r}")
    return base // max(k, 1)


def charge_table(ks=(0, 1, 2, 3, 4, 6, 12)):
    return tuple((k, charge_for_gap(k)) for k in ks)


def charge_is_monotone_non_increasing(ks=(0, 1, 2, 3, 4, 6, 12)):
    vals = [c for _k, c in charge_table(ks)]
    return all(a >= b for a, b in zip(vals, vals[1:]))


def the_peak_is_not_adopted():
    """Stated so it can be false: the charge at k=1 is not strictly greater than every other charge,
    because the schedule is monotone rather than peaked. Returns (charge_at_1, charge_at_0, peaked)."""
    c1, c0 = charge_for_gap(1), charge_for_gap(0)
    peaked = c1 > max(charge_for_gap(k) for k in (0, 2, 3, 4))
    return c1, c0, peaked


# ---- the peers and the protocol -----------------------------------------------------------------------------
def _peer(prefix, occupancy):
    return {"prefix": prefix, "occupancy": frozenset(occupancy)}


def peer_population(n=4, thick=2):
    """Honest peers report the same VERDICT with capture noise below the gap; the liar reports a
    breached wall."""
    wall = spanning_wall(n, thick)
    cs = sorted(wall)
    return (_peer(1, wall),
            _peer(2, wall - {cs[0]}),
            _peer(3, wall - {cs[5]}),
            _peer(4, wall - {cs[9]}),
            _peer(5, wall - {cs[13]}),
            _peer(6, frozenset()))


def submitter(n=4, thick=2):
    return spanning_wall(n, thick)


def verify_cohort(mine, peers, budget, n=4, min_peers=MIN_PEERS):
    """Fetch peers in deterministic order, charge per fetch, terminate on a THRESHOLD of agreeing
    peers or on budget exhaustion — never on the first success."""
    if min_peers < 1:
        raise CohortError("a cohort threshold below one verifies nothing")
    remaining, agreeing, fetched = budget, 0, 0
    for p in sorted(peers, key=lambda q: q["prefix"]):
        try:
            remaining = _BG.charge(remaining, EDGE_COST)
        except _BG.Overdrawn:
            break
        fetched += 1
        if peers_agree(mine, p["occupancy"], n):
            agreeing += 1
        if agreeing >= min_peers:
            return VERIFIED, agreeing, fetched, remaining
    if fetched == 0:
        return UNAVAILABLE, 0, 0, remaining
    return (UNAVAILABLE if agreeing == fetched else FAILED), agreeing, fetched, remaining


def _verify_first_agreement(mine, peers, budget, n=4):
    """A FALSIFIER TOOL: terminate as soon as ONE peer agrees."""
    remaining = budget
    for p in sorted(peers, key=lambda q: q["prefix"]):
        try:
            remaining = _BG.charge(remaining, EDGE_COST)
        except _BG.Overdrawn:
            return FAILED, 0
        if peers_agree(mine, p["occupancy"], n):
            return VERIFIED, 1
    return FAILED, 0


def first_agreement_is_cherry_picking():
    """The plant BITES on an adversary controlling ONE peer."""
    mine, single = submitter(), (peer_population()[0],)
    fo, fc = _verify_first_agreement(mine, single, _BG.SHARD_BUDGET)
    to, ta, _f, _r = verify_cohort(mine, single, _BG.SHARD_BUDGET)
    return fo, fc, to, ta


def outcome_census():
    mine, full = submitter(), peer_population()
    liars = tuple(_peer(i, frozenset()) for i in range(1, 7))
    return (("full population", ) + verify_cohort(mine, full, 20)[:3],
            ("no peers", ) + verify_cohort(mine, (), 20)[:3],
            ("all disagree", ) + verify_cohort(mine, liars, 20)[:3])


def all_three_outcomes_are_reachable():
    return {r[1] for r in outcome_census()} == {VERIFIED, UNAVAILABLE, FAILED}


def unavailable_is_not_failure():
    rows = {r[0]: r[1] for r in outcome_census()}
    return rows["no peers"], rows["all disagree"], rows["no peers"] != rows["all disagree"]


def loop_terminates(budget=_BG.SHARD_BUDGET):
    many = tuple(_peer(i, frozenset()) for i in range(1, 100))
    _o, _a, fetched, _r = verify_cohort(submitter(), many, budget)
    return fetched, budget, fetched <= budget


# ---- the four refuted measurands, each pinned as a witness ---------------------------------------------------
def jaccard_is_blind_to_structure():
    """(1) L21 REPRODUCED ONE LAYER UP, in this module's own first draft. Two peers diverging by the
    SAME cell count, one scattered and one contiguous, share the identical Jaccard verdict and differ
    in run. Returns (scattered_run, contiguous_run, same_diff_size, same_jaccard)."""
    base = frozenset((i, 0, 0) for i in range(12))
    scat = (base - {(0, 0, 0), (3, 0, 0), (6, 0, 0), (9, 0, 0)}) | \
        {(20, 0, 0), (40, 0, 0), (60, 0, 0), (80, 0, 0)}
    cont = (base - {(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)}) | \
        {(20, 0, 0), (21, 0, 0), (22, 0, 0), (23, 0, 0)}

    def run(a, b):
        diff = sorted(x for (x, _y, _z) in (a ^ b))
        best = cur = 1
        for p, q in zip(diff, diff[1:]):
            cur = cur + 1 if q == p + 1 else 1
            best = max(best, cur)
        return best if diff else 0

    def jac(a, b):
        return (len(a & b), len(a | b))
    return run(base, scat), run(base, cont), \
        len(base ^ scat) == len(base ^ cont), jac(base, scat) == jac(base, cont)


def run_length_is_inverted(n=7):
    """(2) THE RUN-GAP THIS RUNG WAS ONE STEP FROM ADOPTING, refuted. A whole wall face removed
    WITHOUT opening a passage outscores an actual breach. Returns
    (deepen_run, deepen_breached, breach_run, breach_breached)."""
    wall = frozenset((x, y, z) for x in (1, 2, 3) for y in range(n) for z in range(n))
    deepen = wall - {(3, y, z) for y in range(n) for z in range(n)}
    breach = wall - {(1, 3, 3), (2, 3, 3), (3, 3, 3)}
    return (len(wall ^ deepen), verdict(deepen, n) == BREACHED,
            len(wall ^ breach), verdict(breach, n) == BREACHED)


def boundary_does_not_determine_breach(n=7):
    """(3) THE STOKES / WARD-TAKAHASHI REDUCTION, REFUTED — and with it the proposed tier between
    CERT and LATTICE. Two occupancies with BYTE-IDENTICAL boundary occupancy, opposite verdicts.
    Returns (boundary_identical, verdict_a, verdict_b)."""
    slab_x = (1, 2, 3)
    slab = frozenset((x, y, z) for x in slab_x for y in range(n) for z in range(n))

    def shell(region):
        return frozenset(c for c in region if c[0] in (slab_x[0], slab_x[-1])
                         or c[1] in (0, n - 1) or c[2] in (0, n - 1))
    a = slab - {(1, 3, 3), (2, 3, 3), (3, 3, 3)}
    b = slab - {(1, 3, 3), (3, 3, 3), (2, 1, 1)}
    return shell(slab) & a == shell(slab) & b, verdict(a, n), verdict(b, n)


def hex_duality_fails_in_3d(n=7):
    """(4) THE Z2 ORDER PARAMETER, REFUTED IN 3D. In 2D either free space crosses or the occupied set
    blocks — exhaustive and exclusive. Here a free tube through a solid slab gives BOTH. Returns
    (free_crosses_x, occupied_crosses_z, both)."""
    slab = frozenset((x, y, z) for x in (1, 2, 3) for y in range(n) for z in range(n))
    tube = slab - {(x, 3, 3) for x in (1, 2, 3)}

    def occ_crosses(occ, axis):
        seen, stack = set(), [c for c in occ if c[axis] == 0]
        while stack:
            c = stack.pop()
            if c in seen:
                continue
            seen.add(c)
            for d in range(3):
                for s in (-1, 1):
                    nb = list(c)
                    nb[d] += s
                    nb = tuple(nb)
                    if 0 <= nb[d] < n and nb in occ and nb not in seen:
                        stack.append(nb)
        return any(c[axis] == n - 1 for c in seen)
    fx = free_reaches(tube, n, 0)
    oz = occ_crosses(tube, 2)
    return fx, oz, fx and oz


# ---- the cohort graph, kept as an observable and wired to nothing ---------------------------------------------
def edge_log():
    peers = peer_population()
    shift = 3 * (_VX.LEVELS - 2)
    return tuple(sorted((a["prefix"], b["prefix"],
                         _VX.lca_depth(a["prefix"] << shift, b["prefix"] << shift))
                        for a, b in _comb(peers, 2)))


def centrality(prefix):
    return sum(1 for a, b, _d in edge_log() if prefix in (a, b))


def centrality_dividend_pump(alpha_values=(0, 1, 2, 3), edges=40, edge_cost=EDGE_COST):
    """THE REFUND PUMP, still refuted: budget scaling with centrality gives budget BACK, and
    `budget`'s soundness rests on monotone non-increasing."""
    out = []
    for alpha in alpha_values:
        remaining = _BG.SHARD_BUDGET
        for _ in range(edges):
            remaining = remaining - edge_cost + alpha
        out.append((alpha, remaining, remaining > _BG.SHARD_BUDGET))
    return tuple(out)


def dividend_has_no_safe_useful_setting():
    rows = centrality_dividend_pump()
    pumping = tuple(a for a, _r, grew in rows if grew)
    draining = tuple(a for a, r, grew in rows if not grew and r <= _BG.SHARD_BUDGET)
    return pumping, draining, tuple(a for a in pumping if a in draining)


def the_graph_is_unwired():
    import inspect
    cp = tuple(inspect.signature(_BG.charge).parameters)
    vp = tuple(inspect.signature(verify_cohort).parameters)
    return cp, vp, any("central" in p for p in cp + vp)


# ---- digests + scenes ------------------------------------------------------------------------------------------
def co_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_gap():
    return co_digest("gap", f"{gap_table()}:{the_gap_is_the_thickness()}:"
                            f"{screening_law_census()}:{screening_law_holds()}:"
                            f"{sub_gap_disagreement_is_impossible()}:"
                            f"{at_or_above_the_gap_disagreement_becomes_possible()}:"
                            f"{thin_walls_are_refused()}:{charge_table()}:"
                            f"{charge_is_monotone_non_increasing()}:{the_peak_is_not_adopted()}")


def _scene_protocol():
    return co_digest("protocol", f"{plan_matches_the_classifier()}:{plans_are_nested()}:"
                                 f"{threshold_is_geoquorums()}:{outcome_census()}:"
                                 f"{all_three_outcomes_are_reachable()}:"
                                 f"{unavailable_is_not_failure()}:{loop_terminates()}:"
                                 f"{first_agreement_is_cherry_picking()}")


def _scene_refuted():
    return co_digest("refuted", f"{jaccard_is_blind_to_structure()}:{run_length_is_inverted()}:"
                                f"{boundary_does_not_determine_breach()}:"
                                f"{hex_duality_fails_in_3d()}:{centrality_dividend_pump()}:"
                                f"{dividend_has_no_safe_useful_setting()}:{the_graph_is_unwired()}")


_SCENES = {"gap": _scene_gap, "protocol": _scene_protocol, "refuted": _scene_refuted}
SCENES = ("gap", "protocol", "refuted")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_cohort.txt"), encoding="utf-8") as fh:
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
    raise CohortError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"GAP TABLE (n, thick, k) {gap_table()} -> k == thickness {the_gap_is_the_thickness()}")
    print(f"screening law (k, tried, flips) {screening_law_census()} -> holds {screening_law_holds()}")
    print(f"sub-gap disagreement IMPOSSIBLE {sub_gap_disagreement_is_impossible()}")
    print(f"at the gap it becomes possible {at_or_above_the_gap_disagreement_becomes_possible()}")
    print(f"thin walls refused {thin_walls_are_refused()}")
    print(f"charge table {charge_table()} monotone {charge_is_monotone_non_increasing()} "
          f"peak-not-adopted {the_peak_is_not_adopted()}")
    for row in outcome_census():
        print(f"  {row[0]:18} -> {row[1]:20} agreeing {row[2]} fetched {row[3]}")
    print(f"three outcomes {all_three_outcomes_are_reachable()} | unavail != failed "
          f"{unavailable_is_not_failure()} | terminates {loop_terminates()}")
    print(f"first-agreement cherry-picks {first_agreement_is_cherry_picking()}")
    print(f"REFUTED (1) jaccard blind {jaccard_is_blind_to_structure()}")
    print(f"REFUTED (2) run inverted {run_length_is_inverted()}")
    print(f"REFUTED (3) boundary undetermines {boundary_does_not_determine_breach()}")
    print(f"REFUTED (4) hex duality in 3D {hex_duality_fails_in_3d()}")
    print(f"dividend pump {centrality_dividend_pump()} no-safe-alpha "
          f"{dividend_has_no_safe_useful_setting()} unwired {the_graph_is_unwired()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
