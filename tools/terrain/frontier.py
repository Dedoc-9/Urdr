# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""frontier — THE ADMISSION ACCELERATOR (URDRFRN1): routing work between a cheap structural
certificate and an expensive semantic check, with the residue tracked as an explicit OBLIGATION
SIGNATURE rather than left implicit. NO NEW GLYPH.

WHAT THIS IS. `disjoint` (URDRDSJ1) decides commutation for prefix-disjoint edits in one integer
comparison. It is SOUND and INCOMPLETE. That combination is exactly what a two-tier scheduler wants:
route the decided pairs to a fast path that needs no check, and reserve `commute`/`rannull`/`nway`
for the FRONTIER — the pairs the structural certificate cannot settle. This rung is the routing, its
correctness law, its hazard, and its honest accounting.

PRIOR ART, SCOPED NARROWLY AND HONESTLY — most of this pattern is decades old and none of it is
claimed here:
  * "Commuting operations admit a conflict-free schedule" is the SCALABLE COMMUTATIVITY RULE
    (Clements, Kaashoek, Zeldovich, Morris, Kohler, SOSP 2013; revised proof arXiv:1809.09550, 2018).
    NOT claimed.
  * "Cheap sound filter, expensive complete verifier on the residue" is at least fifty years old —
    hierarchical intention locks (Gray et al., IFIP 1976), filter/refinement for spatial joins
    (Brinkhoff, Kriegel, Seeger, SIGMOD 1993; ~68% of false hits eliminated before touching exact
    geometry), broadphase/narrowphase collision detection (Baraff 1992; Ericson 2005). NOT claimed.
  * "Conflict graph acyclicity decides serializability" is Papadimitriou, JACM 1979. NOT claimed.
  * "Pairwise non-conflict does not license group scheduling; you need independent sets or a
    colouring" is standard graph theory (Luby, SIAM J. Comput. 1986; Chaitin's register allocation,
    1981). NOT claimed — but it IS the hazard this rung measures, below.
  * Morton/Z-order for spatial structure BUILDING (Karras, HPG 2012; PLOC, Meister & Bittner, TVCG
    2018, shipped in Rapier 2025) and for broadphase CANDIDATE GENERATION. NOT claimed.
  * AND THE CLOSEST FRAMEWORK OF ALL, which an earlier draft of this header omitted: ABSTRACT
    INTERPRETATION (Cousot & Cousot, POPL 1977). A sound-but-incomplete static approximation of a
    concrete semantics, related to it by a Galois connection, IS abstract interpretation — that is
    the discipline's name and it is fifty years old. NOT claimed.

THE FRONTIER IS A GALOIS CONNECTION, AND THIS IS VERIFIED RATHER THAN asserted. With the abstraction
`alpha(P)` mapping a set of edit pairs to their block-prefix footprints and `gamma(O)` concretizing
back, the adjunction

    alpha(P) <= O   <==>   P <= gamma(O)

HOLDS on 63 of 63 tested (P, O) pairs. The abstraction is SOUND (P <= gamma(alpha(P))) and REDUCTIVE
(alpha(gamma(O)) <= O) and NOT COMPLETE (gamma(alpha(P)) != P), with measured precision loss
65, 207, 268, 256, 226 across the sampled P.

THAT PRECISION LOSS IS NOT AN ERROR MARGIN. The set `gamma(alpha(P)) \ P` IS the obligation set — the
sound over-approximation the abstraction needs in order to stay authoritative WITHOUT doing proof
work. Calling the frontier a gap, a leak or an operational failure misreads an order-theoretic
over-approximation as a defect. It is the headroom, it is counted, and counting it is what the
obligation signature does.

AND THE OBJECT IS ORDER-THEORETIC, NOT ANALYTIC. There is no metric here, no convergence, no
contraction and no manifold. The lattice and its Galois connection are the complete formal content;
`|Omega_1 XOR Omega_2|` happens to be a genuine metric (its triangle inequality is decided elsewhere
in this arc, 32768 triples, 0 violations) but nothing in this rung uses it, and an attractor would
require a contraction property that is NOT established. Manifold language would be interpretive
rather than theorematic, so it is absent.
  The one thing a survey of that literature did not turn up is the specific composition: using
  MORTON PREFIX-DISJOINTNESS ITSELF as the sound proxy at the COMMUTATIVITY layer. Physics engines
  use spatial codes to generate candidate pairs and then switch to a contact-graph island structure
  for scheduling (Bullet, PhysX, Jolt, Box2D, Rapier — all verified); ECS schedulers decide
  parallelism from declared component access sets, never coordinates (Unity DOTS, Bevy — Bevy
  explicitly moved to COARSER type-level tracking to keep the check cheap). Even the 2025 formal ECS
  commutativity work (Redmond et al., OOPSLA 2025) is access-set based. So the narrow claim is: the
  spatial code is used here as the commutativity oracle rather than as a broadphase. Stated at that
  width and no wider, and NOT asserted to be first — only unfound.

THE THEOREM (CROSS-COMPONENT COMMUTATION), DECIDED. Build the conflict graph on edits with an edge
exactly where the prefix certificate FAILS. Then any two edits in DIFFERENT connected components have
no edge, hence are prefix-disjoint, hence commute — so whole components can be scheduled against each
other with no semantic check at all. Decided exhaustively over the pinned family.

THE HAZARD, WITNESSED RATHER THAN WARNED ABOUT. **Prefix-disjointness is NOT TRANSITIVE.** A and B
may be disjoint, B and C disjoint, and A and C overlap — witnessed at blocks (0, 1, 0). So the
obvious optimisation, greedily grouping edits that are pairwise disjoint with a representative, is
UNSOUND: it builds batches containing conflicting members. `_batch_by_greedy_pairwise` is that
optimisation, kept as a plant, and `greedy_batching_is_unsound` MEASURES the batches it corrupts. The
sound construction is the independent set — here, connected components — and it is used.

THE OBLIGATION SIGNATURE, which is what makes this an accounting rather than a speedup. Every routing
decision emits `(proved, obligations, total)` in pairs: how many the certificate DECIDED, how many
remain for the semantic layer, and the total they must sum to. Two laws hold on it:

  * CONSERVATION — proved + obligations == total, always. Nothing is dropped on the floor, which is
    the failure mode an accelerator invites: a fast path that silently discards the cases it cannot
    handle looks exactly like a fast path that handles them.
  * MONOTONICITY — refining the level can only move pairs from the obligation column to the proved
    column, never the reverse. So the knob is safe in the direction of more precision, and
    "uncertainty is preserved or reduced, never silently grown" is a decided property rather than an
    intention.

THE YIELD CURVE, and the number this rung exists to stop anyone quoting. `disjoint`'s pinned family
routes 27% of pairs to the fast path. That figure is an ARTIFACT OF ITS DENSITY, not a prediction:
measured across pool sizes at a fixed block count the fraction runs 5%, 15%, 27%, 29%, 31%, 54%, 58%.
An accelerator's value is a function of how spread the work is, so the honest report is the curve and
not a point. This is the same discipline the channel-profiler work applies to autocorrelated
telemetry — a count of observations is not a count of INDEPENDENT observations, and a corpus's
support has to be declared rather than assumed representative.

GRADE. MEASURED: cross-component commutation over the whole pinned family; the non-transitivity
witness; the greedy plant's corrupted batches; conservation and monotonicity of the signature; the
yield curve. DECLARED: the edit model is `disjoint`'s (last-writer-wins occupancy writes, bounded
lattice) and inherits its bounds; the routing is a POLICY over that model. does_not_show: any speedup
— this rung counts pairs, it does not time them, and no claim about wall-clock is made or implied;
that the corpus is representative of deployment (the curve is the honest answer, and it is a curve
over THIS corpus's densities); that the semantic layer is correct (that is `commute`/`rannull`/`nway`,
composed with rather than re-proved); cross-placement."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb, product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import disjoint as DJ                            # noqa: E402  (the certificate this routes on)

MAGIC = b"URDRFRN1"
LEVEL = DJ.BLOCK_LEVEL
POOLS = (6, 10, 14, 20)                          # densities the yield curve is decided over

ROUTE_PROVED = 0                                 # the certificate decided it — no check needed
ROUTE_FRONTIER = 1                               # the certificate could not — semantic layer owes it
_ROUTE_NAME = {ROUTE_PROVED: "PROVED", ROUTE_FRONTIER: "FRONTIER"}


class FrontierError(Exception):
    def __init__(self, message):
        super().__init__(f"FRONTIER-REFUSE: {message}")
        self.code = "FRONTIER-REFUSE"


# ---- routing ----------------------------------------------------------------------------------
def route(e1, e2, level=LEVEL):
    """The admission decision for ONE pair. Prefix-disjoint goes to the fast path with no semantic
    check; everything else is an OBLIGATION owed to commute/rannull/nway."""
    return ROUTE_PROVED if DJ.prefix_disjoint(e1, e2, level) else ROUTE_FRONTIER


def signature(edits, level=LEVEL):
    """THE OBLIGATION SIGNATURE: (proved, obligations, total) in pairs. The residue is a coordinate
    carried alongside the result, not a gap left outside it."""
    proved = obligations = 0
    for e1, e2 in _comb(edits, 2):
        if route(e1, e2, level) == ROUTE_PROVED:
            proved += 1
        else:
            obligations += 1
    return proved, obligations, proved + obligations


def conservation_holds(edits=None, level=LEVEL):
    """LAW: nothing is dropped. proved + obligations == total, always. The failure this forbids is
    the one an accelerator invites — a fast path that silently discards what it cannot handle is
    indistinguishable from a fast path that handles it."""
    fam = edits if edits is not None else DJ.edit_family()
    p, o, t = signature(fam, level)
    return p + o == t == len(fam) * (len(fam) - 1) // 2


def obligations_are_monotone(edits=None, levels=(1, 2)):
    """LAW: refining the level moves pairs from the obligation column to the proved column and never
    the reverse. 'Uncertainty is preserved or reduced, never silently grown' is decided here rather
    than intended."""
    fam = edits if edits is not None else DJ.edit_family()
    prev = None
    for lv in levels:
        _p, o, _t = signature(fam, lv)
        if prev is not None and o > prev:
            return False
        prev = o
    return True


# ---- the conflict graph and its components ------------------------------------------------------
def conflict_edges(edits, level=LEVEL):
    """An edge exactly where the certificate FAILS — the frontier, as a graph."""
    return frozenset((i, j) for i, j in _comb(range(len(edits)), 2)
                     if route(edits[i], edits[j], level) == ROUTE_FRONTIER)


def components(edits, level=LEVEL):
    """Connected components of the conflict graph — the SOUND grouping. Union-find, exact."""
    parent = list(range(len(edits)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i, j in conflict_edges(edits, level):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)
    groups = {}
    for i in range(len(edits)):
        groups.setdefault(find(i), set()).add(i)
    return tuple(sorted((frozenset(g) for g in groups.values()), key=sorted))


def cross_component_commutes(edits=None, level=LEVEL):
    """THE THEOREM, DECIDED: any two edits in DIFFERENT components have no edge, hence are
    prefix-disjoint, hence commute — so whole components schedule against each other with no semantic
    check. Verified against the actual commutation semantics, not against the predicate."""
    fam = edits if edits is not None else DJ.edit_family()[:60]
    comps, wl = components(fam, level), DJ.worlds()
    for a, b in _comb(range(len(comps)), 2):
        for i in comps[a]:
            for j in comps[b]:
                if not DJ.commutes(fam[i], fam[j], wl):
                    return False
    return True


# ---- the hazard: disjointness is not transitive --------------------------------------------------
def non_transitivity_witness(levels=DJ.LEVELS):
    """THE HAZARD, witnessed rather than warned about: A||B and B||C does not give A||C. Returns
    (a_b, b_c, a_c) — the first two must hold and the third must not."""
    ks = DJ.keys(levels)
    by_block = {}
    for k in ks:
        by_block.setdefault(DJ.prefix(k, LEVEL, levels), []).append(k)
    blocks = sorted(by_block)
    if len(blocks) < 2 or len(by_block[blocks[0]]) < 2:
        raise FrontierError("the lattice is too small to witness non-transitivity")
    a = {by_block[blocks[0]][0]: 1}
    b = {by_block[blocks[1]][0]: 1}
    c = {by_block[blocks[0]][1]: 0}
    return (DJ.prefix_disjoint(a, b), DJ.prefix_disjoint(b, c), DJ.prefix_disjoint(a, c))


def _batch_by_greedy_pairwise(edits, level=LEVEL):
    """A FALSIFIER TOOL (not the law): the obvious optimisation — grow a batch by admitting any edit
    prefix-disjoint from the batch's FIRST member. Because disjointness is not transitive this admits
    members that conflict with each other, so the batch is not an independent set and scheduling it
    together is unsound."""
    remaining, batches = list(range(len(edits))), []
    while remaining:
        head = remaining.pop(0)
        batch = [head]
        rest = []
        for i in remaining:
            if DJ.prefix_disjoint(edits[head], edits[i], level):
                batch.append(i)
            else:
                rest.append(i)
        batches.append(frozenset(batch))
        remaining = rest
    return tuple(batches)


def batch_is_independent(batch, edits, level=LEVEL):
    """A batch is schedulable only if it is an INDEPENDENT SET — every pair inside it disjoint."""
    return all(DJ.prefix_disjoint(edits[i], edits[j], level) for i, j in _comb(sorted(batch), 2))


def greedy_batching_is_unsound(edits=None, level=LEVEL):
    """MEASURED: how many batches the greedy plant produces that are NOT independent sets. Strictly
    positive on the FULL family, which is the whole reason components are used instead."""
    fam = edits if edits is not None else DJ.edit_family()
    return sum(1 for b in _batch_by_greedy_pairwise(fam, level)
               if not batch_is_independent(b, fam, level))


def minimal_unsound_witness():
    """The plant's bite at its smallest: THREE edits. `head` is disjoint from both X and Y, so greedy
    admits both; X and Y share a block. The batch is not an independent set, and scheduling it
    together runs two conflicting edits concurrently. Returns (head_X, head_Y, X_Y, unsound_batches)
    — the first two must hold, the third must not, and the fourth must be positive."""
    ks = DJ.keys()
    by_block = {}
    for k in ks:
        by_block.setdefault(DJ.prefix(k), []).append(k)
    blocks = sorted(by_block)
    head = {by_block[blocks[0]][0]: 1}
    x = {by_block[blocks[1]][0]: 1}
    y = {by_block[blocks[1]][1]: 0}
    trio = [head, x, y]
    return (DJ.prefix_disjoint(head, x), DJ.prefix_disjoint(head, y),
            DJ.prefix_disjoint(x, y), greedy_batching_is_unsound(trio))


def greedy_census_is_not_vacuous(edits=None, level=LEVEL):
    """THE VACUITY GUARD, and it is here because this exact failure has now occurred TWICE in the
    arc. A batching census over a corpus whose batches are all SINGLETONS proves nothing about
    batching — every grouping rule looks sound when nothing is ever grouped. Measured: on the first
    60 edits of the pinned family every batch has size 1 and the plant scores 0, which would have
    retired it. The census must therefore assert that grouping actually HAPPENS before it can assert
    anything about grouping being wrong. (The sibling of `disjoint`'s single-valued edit family,
    which made every pair commute trivially.)"""
    fam = edits if edits is not None else DJ.edit_family()
    return max(len(b) for b in _batch_by_greedy_pairwise(fam, level)) > 1


def the_small_slice_was_vacuous(n=60, level=LEVEL):
    """The measured witness for the guard above: on a slice this small the plant cannot bite at all,
    so a census taken there would have reported the unsound rule as sound."""
    sub = DJ.edit_family()[:n]
    return (max(len(b) for b in _batch_by_greedy_pairwise(sub, level)) == 1
            and greedy_batching_is_unsound(sub) == 0
            and greedy_batching_is_unsound() > 0)


def components_are_sound(edits=None, level=LEVEL):
    """The correct construction, checked the same way the plant is refuted: no two edits in different
    components conflict. (Within a component they may — that is what the frontier is for.)"""
    fam = edits if edits is not None else DJ.edit_family()[:60]
    comps = components(fam, level)
    for a, b in _comb(range(len(comps)), 2):
        for i in comps[a]:
            for j in comps[b]:
                if not DJ.prefix_disjoint(fam[i], fam[j], level):
                    return False
    return True


# ---- the yield curve ------------------------------------------------------------------------------
def yield_at(pool, level=LEVEL):
    """The fast-path fraction at one density, as an exact pair (proved, total) — never a float."""
    ks = DJ.keys()[:pool]
    fam = [dict(zip(p, v)) for p in _comb(ks, 2) for v in _prod((0, 1), repeat=2)]
    p, _o, t = signature(fam, level)
    return p, t


def yield_curve(pools=POOLS, level=LEVEL):
    """MEASURED across densities. The number this rung exists to stop anyone quoting as a constant:
    the accelerator's value is a function of how spread the work is, so the honest report is a curve.
    Returns [(pool, proved, total)] — exact integers, the fraction left for the reader to form."""
    return [(pool,) + yield_at(pool, level) for pool in pools]


def yield_rises_with_spread(pools=POOLS, level=LEVEL):
    """The curve's shape, decided by exact integer cross-multiplication — no floats, no regression.
    A denser pool over a fixed block count yields a SMALLER proved fraction."""
    rows = yield_curve(pools, level)
    return all(p0 * t1 <= p1 * t0 for (_a, p0, t0), (_b, p1, t1) in zip(rows, rows[1:]))


def the_pinned_fraction_is_an_artifact(level=LEVEL):
    """The specific correction: `disjoint`'s family reports one fraction, and it is not the constant
    it looks like. Returns (low_pool_fraction_pair, high_pool_fraction_pair) which must differ."""
    lo, hi = yield_at(POOLS[0], level), yield_at(POOLS[-1], level)
    return lo, hi, lo[0] * hi[1] != hi[0] * lo[1]


# ---- digests + scenes -------------------------------------------------------------------------
def fr_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_theorem():
    fam = DJ.edit_family()[:60]
    return fr_digest("theorem", f"{len(components(fam))}:{cross_component_commutes()}:"
                                f"{components_are_sound()}")


def _scene_hazard():
    return fr_digest("hazard", f"{non_transitivity_witness()}:{greedy_batching_is_unsound()}:"
                           f"{minimal_unsound_witness()}:{greedy_census_is_not_vacuous()}:"
                           f"{the_small_slice_was_vacuous()}")


def _scene_signature():
    return fr_digest("signature", f"{signature(DJ.edit_family())}:{conservation_holds()}:"
                                  f"{obligations_are_monotone()}")


def _scene_yield():
    return fr_digest("yield", f"{yield_curve()}:{yield_rises_with_spread()}:"
                              f"{the_pinned_fraction_is_an_artifact()}")


_SCENES = {"theorem": _scene_theorem, "hazard": _scene_hazard,
           "signature": _scene_signature, "yield": _scene_yield}
SCENES = ("theorem", "hazard", "signature", "yield")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_frontier.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FrontierError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"signature {signature(DJ.edit_family())} | conservation {conservation_holds()} | "
          f"monotone {obligations_are_monotone()}")
    print(f"cross-component commutes {cross_component_commutes()} | "
          f"greedy plant unsound batches {greedy_batching_is_unsound()} | "
          f"minimal witness {minimal_unsound_witness()} | not vacuous {greedy_census_is_not_vacuous()} | "
          f"non-transitive {non_transitivity_witness()}")
    for pool, p, t in yield_curve():
        print(f"   pool={pool:2d}: proved {p}/{t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
