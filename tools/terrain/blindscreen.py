# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""blindscreen — CHEAPNESS IS NOT SOUNDNESS (URDRBLS1): the whole family of cheap pre-screens refuted
at once, and the one hole `autoroute` left open. NO NEW GLYPH.

WHY THIS RUNG EXISTS. `autoroute` routes a query to the cheapest level that CAN decide it, and drops a
fetch only where a witness search and a syntactic proof agree. What it cannot yet do is tell the
difference between two situations that look identical from inside a cascade:

    (a) THIS TIER DECIDES — the cheap answer is backed by a determinacy proof
    (b) THIS TIER IS ALL I CAN AFFORD — the cheap answer is backed by nothing

A cascade that cannot distinguish those will accept a screen because it is cheap. This module supplies
the missing falsifier, and it supplies it for the whole FAMILY rather than one predicate at a time.

    MEASURED: four cheap invariants — cell count, boundary occupancy, tile prefix, occupancy defect —
    are EACH blind to the verdict, and so is their CONJUNCTION. There exist two occupancies agreeing on
    ALL FOUR simultaneously with OPPOSITE breach verdicts, differing by 2 cells. Stacking cheap checks
    does not converge on the answer, because they are all blind in the same direction.

That is the load-bearing negative. Every future proposal of the form "add one more cheap check before
the payload moves" is answered by this pair, without needing to be measured again.

THE HISTORICAL TRAJECTORY THIS FORMALIZES, WITH ITS DATES CORRECTED. A four-step chemical structure
determination was offered as a blueprint for the cascade, running biosynthesis -> extraction ->
isomerization -> degradation. Checked against the record, three of the four attributions do not hold
and the ordering is not a trajectory:

    1844  Saint-Evre determines the empirical FORMULA of safrole.
    1869  Grimaux and Ruotte investigate and NAME safrole. Separately, Fittig prepares piperonal by
          permanganate oxidation of piperic acid — 1869 rather than 1871, a different substrate and a
          different reagent from the cleavage the blueprint cites, and Remsen is not named in the
          1911 encyclopaedic account of it at all.
    1885  Eijkman shows "shikimol" (from Illicium anisatum) and safrole are the SAME compound, on the
          grounds that they share an empirical formula and have other similar properties. He also
          isolates shikimic acid from that plant the same year — which is the only step the blueprint
          attributes correctly.
    1888  Bruhl establishes that safrole's C3H5 group is an ALLYL group.

So the structural feature the blueprint has being isomerized in 1886 was not itself established until
1888. The order is an anachronism, and the corrected sequence tells the OPPOSITE story:

    FORMULA -> NAME -> IDENTITY-BY-SHARED-INVARIANT -> STRUCTURE

Each step used a weaker invariant than the question demanded, and the structural answer came LAST — not
because cheap-first was a sound strategy but because the structural instrument did not exist yet. The
cascade is therefore not this trajectory; it is its INVERSE, and it is sound only because the arc
already owns the structural answer. Cheap-first is legitimate exactly where cheapness is backed by a
determinacy proof and illegitimate where it is backed by the unavailability of anything better.

AND THE 1885 STEP IS A NAMED INSTANCE OF THE DEFECT, WHICH IS WHY IT IS WORTH PINNING RATHER THAN
ADMIRING. "Same empirical formula plus similar properties, therefore the same compound" is an identity
claim from an invariant that provably cannot decide identity: safrole and isosafrole share the formula
C10H10O2 and are different compounds with different reactivity. The conclusion was right; the argument
as stated does not reach it. That is exactly `cohort`'s refutation (1) — a count is blind to
arrangement — and exactly why a hash of a lattice is a CLAIM rather than a verification. This module
carries the lattice analogue as a live witness: two occupancies with the identical CELL COUNT and
opposite verdicts, which is the isomer pair with the chemistry removed.

THE COST ORDER AND THE DECISIVENESS ORDER ARE DIFFERENT ORDERS, AND THAT IS THE WHOLE POINT. Measured
side by side, the invariants sort one way by cost and another way by what they settle; the cheapest
four settle nothing and the only decisive measurand is the most expensive. A cascade is sound only
where the two orders COINCIDE, and `autoroute`'s CERT tier qualifies only because `inputset` proved
determinacy there — not because it is first.

GRADE. MEASURED: the four cheap invariants each refuted by an equal-invariant opposite-verdict pair;
the conjunction of all four refuted by a single pair differing in 2 cells; the operational cost of
installing a cell-count screen, counted as peers wrongly cleared; connectivity separating the same pair
as a positive control, so the corpus is not simply degenerate; the cost order against the decisiveness
order; the router's decision path checked by signature to contain no blind invariant. DECLARED: the
corpus is a pinned synthetic set built to contain the pairs, and a refutation needs only one witness so
that is sound — but the ABSENCE of a decisive cheap invariant is over this enumerated family of four
and is not a proof that no cheap invariant exists; what is proved is that these four and their
conjunction fail. The historical dates are cited from secondary sources listed in the conformance
header, and this module makes no chemical claim beyond attribution and shared empirical formula.
does_not_show: that connectivity is CHEAP — it is the expensive measurand and this rung is the argument
for paying for it; that a routed verdict is honest, inherited unchanged from `cohort`; that no cheap
invariant whatsoever could decide breach, only that these four cannot."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import cohort as _CO                                                # noqa: E402
import jurisdiction as _JR                                          # noqa: E402
import tilemin as _TM                                               # noqa: E402

MAGIC = b"URDRBLS1"
WORLD = 4


class BlindError(Exception):
    def __init__(self, message):
        super().__init__(f"BLINDSCREEN-REFUSE: {message}")
        self.code = "BLINDSCREEN-REFUSE"


# ---- the cheap invariants, each a candidate pre-payload or pre-fill screen ----------------------------
def cell_count(occ, n=WORLD):
    """THE EMPIRICAL FORMULA of an occupancy: how many cells, blind to where they are."""
    return len(occ)


def boundary_occupancy(occ, n=WORLD):
    """The strongest of the cheap four, and the one `cohort` already refuted for this purpose."""
    return frozenset(c for c in occ if 0 in c or (n - 1) in c)


def tile_prefix(occ, n=WORLD):
    return _TM.tile_prefix(occ)


def occupancy_defect(occ, n=WORLD):
    return _JR.defect(occ)


CHEAP = (("cell_count", cell_count), ("boundary_occupancy", boundary_occupancy),
         ("tile_prefix", tile_prefix), ("occupancy_defect", occupancy_defect))
DECISIVE = ("connectivity", _CO.free_reaches)


# ---- the corpus, canonically ordered so every witness search is deterministic --------------------------
def _key(occ):
    return tuple(sorted(occ))


def corpus(n=WORLD):
    """Built to CONTAIN the pairs rather than to be representative, and ordered canonically so the
    first witness found is a function of the corpus and not of set iteration."""
    out = []
    for thick in (1, 2):
        wall = _CO.spanning_wall(n, thick)
        cs = sorted(wall)
        free = [c for c in sorted(_CO.world(n)) if c not in wall]
        out.append(wall)
        for i in range(0, len(cs), 3):
            out.append(wall - {cs[i]})
        for i in range(0, len(cs) - 1, 5):
            out.append(wall - {cs[i], cs[i + 1]})
        # COUNT-PRESERVING perturbations: remove r cells, add r elsewhere. Same "formula",
        # different structure — the lattice analogue of an isomer pair, and the reason the corpus is
        # built rather than sampled. A sparser sweep produced NO conjunction witness at all, which
        # would have read as "the cheap conjunction survives" when it was the corpus that was thin.
        for c in cs:
            for f in free[:10]:
                out.append((wall - {c}) | {f})
        for i in range(0, len(cs) - 1, 4):
            for j in (0, 3, 7):
                if j + 1 < len(free):
                    out.append((wall - {cs[i], cs[i + 1]}) | {free[j], free[j + 1]})
    return tuple(sorted(dict.fromkeys(out), key=_key))


def verdicts(n=WORLD):
    return {o: _CO.verdict(o, n) for o in corpus(n)}


def corpus_census(n=WORLD):
    """Validity-not-outcome: a corpus that is all one verdict cannot refute anything. Returns
    (size, breached, intact)."""
    v = verdicts(n)
    return (len(v), sum(1 for x in v.values() if x == _CO.BREACHED),
            sum(1 for x in v.values() if x == _CO.INTACT))


# ---- each cheap invariant, refuted ---------------------------------------------------------------------
def blindness_witness(fn, n=WORLD):
    """The first equal-invariant / opposite-verdict pair in canonical order, or None."""
    v = verdicts(n)
    for a, b in _comb(corpus(n), 2):
        if v[a] != v[b] and fn(a, n) == fn(b, n):
            return a, b
    return None


def blindness_census(n=WORLD):
    """Returns ((name, refuted, divergence), ...) — every row must be refuted."""
    out = []
    for name, fn in CHEAP:
        w = blindness_witness(fn, n)
        out.append((name, w is not None, len(w[0] ^ w[1]) if w else 0))
    return tuple(out)


def every_cheap_invariant_is_blind(n=WORLD):
    rows = blindness_census(n)
    return sum(1 for _n, r, _d in rows if r), len(rows)


# ---- and so is their CONJUNCTION, which is the result that closes the family ----------------------------
def conjunction_witness(n=WORLD):
    """THE LOAD-BEARING NEGATIVE: one pair agreeing on ALL FOUR cheap invariants at once with OPPOSITE
    verdicts. Stacking cheap checks does not converge, because they are blind in the same direction."""
    v = verdicts(n)
    for a, b in _comb(corpus(n), 2):
        if v[a] != v[b] and all(fn(a, n) == fn(b, n) for _nm, fn in CHEAP):
            return a, b
    return None


def the_conjunction_is_also_blind(n=WORLD):
    """Returns (refuted, count_a, count_b, divergence, verdict_a, verdict_b)."""
    w = conjunction_witness(n)
    if w is None:
        return False, 0, 0, 0, None, None
    a, b = w
    return (True, len(a), len(b), len(a ^ b), _CO.verdict(a, n), _CO.verdict(b, n))


def connectivity_separates_the_pair(n=WORLD):
    """POSITIVE CONTROL. If the decisive measurand could not tell the pair apart either, the corpus
    would be degenerate rather than the invariants blind. Returns (reaches_a, reaches_b, separated)."""
    w = conjunction_witness(n)
    if w is None:
        raise BlindError("no conjunction witness to control against")
    a, b = w
    ra, rb = _CO.free_reaches(a, n), _CO.free_reaches(b, n)
    return ra, rb, ra != rb


# ---- what installing the cheap screen would actually cost ----------------------------------------------
def count_matched_population(n=WORLD, size=8):
    """A peer population every member of which has the SAME cell count as the submitter, so a
    cell-count screen clears ALL of them. Some are honest and some are not."""
    mine = _CO.submitter(n, 2)
    cs, free = sorted(mine), [c for c in sorted(_CO.world(n)) if c not in mine]
    peers, i = [], 0
    # honest: count-preserving swaps that do NOT breach
    for j in range(3):
        peers.append(_CO._peer(len(peers) + 1, (mine - {cs[j]}) | {free[j]}))
    # faulty: count-preserving swaps that DO breach, via an aligned two-cell tunnel
    tunnels = (((1, 2, 2), (2, 2, 2)), ((1, 0, 0), (2, 0, 0)), ((1, 3, 1), (2, 3, 1)))
    for t in tunnels:
        if all(c in mine for c in t) and i + 1 < len(free):
            peers.append(_CO._peer(len(peers) + 1, (mine - set(t)) | {free[i], free[i + 1]}))
            i += 2
    while len(peers) < size and i + 1 < len(free):
        peers.append(_CO._peer(len(peers) + 1, (mine - {cs[i]}) | {free[i]}))
        i += 1
    return tuple(peers[:size])


def a_cheap_screen_would_clear_a_liar(n=WORLD):
    """THE OPERATIONAL COST, counted rather than argued: how many peers a cell-count screen clears,
    and how many of those it clears WRONGLY. Returns (cleared, wrongly_cleared, total)."""
    mine = _CO.submitter(n, 2)
    mv = _CO.verdict(mine, n)
    peers = count_matched_population(n)
    cleared = sum(1 for p in peers if cell_count(p["occupancy"], n) == cell_count(mine, n))
    wrong = sum(1 for p in peers
                if cell_count(p["occupancy"], n) == cell_count(mine, n)
                and _CO.verdict(p["occupancy"], n) != mv)
    return cleared, wrong, len(peers)


def the_population_exercises_both_arms(n=WORLD):
    """Otherwise the count above is a measurement of nothing. Returns (agreeing, disagreeing)."""
    mine = _CO.submitter(n, 2)
    mv = _CO.verdict(mine, n)
    peers = count_matched_population(n)
    agree = sum(1 for p in peers if _CO.verdict(p["occupancy"], n) == mv)
    return agree, len(peers) - agree


# ---- the two orders, and they are not the same order ----------------------------------------------------
COST_RANK = (("cell_count", 1), ("tile_prefix", 1), ("occupancy_defect", 2),
             ("boundary_occupancy", 3), ("connectivity", 4))


def decisiveness_rank(n=WORLD):
    """Decides the verdict, or does not. Returns ((name, decides), ...) in COST order."""
    rows = {nm: refuted for nm, refuted, _d in blindness_census(n)}
    out = []
    for name, _c in COST_RANK:
        if name == DECISIVE[0]:
            out.append((name, connectivity_separates_the_pair(n)[2]))
        else:
            out.append((name, not rows[name]))
    return tuple(out)


def cheapness_is_not_soundness(n=WORLD):
    """THE POINT, MEASURED: sort by cost and sort by what is settled, and the orders disagree — the
    four cheapest settle nothing and the only decisive measurand is the most expensive. Returns
    (cheap_that_decide, expensive_that_decide, orders_agree)."""
    rows = decisiveness_rank(n)
    cheap = tuple(nm for nm, dec in rows if dec and dict(COST_RANK)[nm] < 4)
    dear = tuple(nm for nm, dec in rows if dec and dict(COST_RANK)[nm] >= 4)
    return cheap, dear, bool(cheap) and not dear


def eijkman_identity_is_underdetermined(n=WORLD):
    """THE 1885 STEP AS A LATTICE WITNESS. "Same empirical formula plus similar properties, therefore
    the same compound" is identity from an invariant that cannot decide it — safrole and isosafrole
    share C10H10O2. Here: identical cell count, identical boundary, opposite verdict. Returns
    (same_count, same_boundary, same_prefix, opposite_verdict)."""
    w = conjunction_witness(n)
    if w is None:
        raise BlindError("no witness for the identity argument")
    a, b = w
    return (cell_count(a, n) == cell_count(b, n),
            boundary_occupancy(a, n) == boundary_occupancy(b, n),
            tile_prefix(a, n) == tile_prefix(b, n),
            _CO.verdict(a, n) != _CO.verdict(b, n))


# ---- the router must REFUSE the cheap screen, and that is a signature check ------------------------------
def the_router_takes_no_blind_invariant():
    """Not a promise in prose — a signature check on the decision path, the same discipline that keeps
    `cohort`'s centrality graph unwired. Returns (checked, appearances)."""
    import inspect
    import autoroute as _AR
    names = [nm for nm, _f in CHEAP]
    hits = []
    for fn in (_AR.verify_routed, _AR.screen_decides, _AR.plan_for, _CO.peers_agree):
        src = inspect.getsource(fn)
        for nm in names:
            if nm in src:
                hits.append((fn.__name__, nm))
    return 4, tuple(hits)


# ---- digests + scenes ------------------------------------------------------------------------------------
def bs_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_blind():
    return bs_digest("blind", f"{corpus_census()}:{blindness_census()}:"
                              f"{every_cheap_invariant_is_blind()}")


def _scene_conjunction():
    return bs_digest("conjunction", f"{the_conjunction_is_also_blind()}:"
                                    f"{connectivity_separates_the_pair()}:"
                                    f"{eijkman_identity_is_underdetermined()}")


def _scene_cost():
    return bs_digest("cost", f"{a_cheap_screen_would_clear_a_liar()}:"
                             f"{the_population_exercises_both_arms()}:"
                             f"{decisiveness_rank()}:{cheapness_is_not_soundness()}:"
                             f"{the_router_takes_no_blind_invariant()}")


_SCENES = {"blind": _scene_blind, "conjunction": _scene_conjunction, "cost": _scene_cost}
SCENES = ("blind", "conjunction", "cost")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_blindscreen.txt"), encoding="utf-8") as fh:
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
    raise BlindError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"corpus (size, breached, intact) {corpus_census()}")
    print("PER-INVARIANT BLINDNESS (name, refuted, divergence)")
    for row in blindness_census():
        print(f"    {row}")
    print(f"all four blind {every_cheap_invariant_is_blind()}")
    print(f"THE CONJUNCTION IS ALSO BLIND {the_conjunction_is_also_blind()}")
    print(f"  positive control, connectivity separates it {connectivity_separates_the_pair()}")
    print(f"  the 1885 identity argument, as a lattice witness "
          f"{eijkman_identity_is_underdetermined()}")
    print(f"a cheap screen clears (cleared, WRONGLY, total) {a_cheap_screen_would_clear_a_liar()} "
          f"| population exercises both arms {the_population_exercises_both_arms()}")
    print("COST ORDER vs DECISIVENESS")
    for nm, dec in decisiveness_rank():
        print(f"    cost {dict(COST_RANK)[nm]}  {nm:20} decides {dec}")
    print(f"cheapness is not soundness {cheapness_is_not_soundness()}")
    print(f"router takes no blind invariant {the_router_takes_no_blind_invariant()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv[1:]))
