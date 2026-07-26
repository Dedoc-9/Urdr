# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""disjoint — STRUCTURAL COMMUTATION BY MORTON PREFIX-DISJOINTNESS (URDRDSJ1): task 58 Half B, made
DECIDABLE by the lattice that S1 built. NO NEW GLYPH.

WHAT HALF B WAS WAITING FOR. `commute` (URDRCMU1), `rannull` (RAN-0) and `nway` (URDRNWY1) already
establish order-independence, but they establish it PER INSTANCE — each pair of edits is checked.
`horn`'s declared boundary (c) depends on that check: replay from a sparse anchor is sound only if the
intervening operations commute, and under a user-authored city that is exactly where operation order
is least controlled. Making commutation STRUCTURAL rather than checked has been the oldest open item
in the arc, and it was open because "these two edits share no semantic authority" was a judgment
rather than a predicate.

The integer voxel lattice (URDRVOX1) turns that judgment into arithmetic. An edit's footprint is a
set of Morton keys; two footprints occupy disjoint subtrees exactly when their level-L prefixes do not
intersect; and a prefix is a shift. So the question becomes one integer comparison per prefix.

THE THEOREM (SOUNDNESS), DECIDED. For last-writer-wins occupancy edits, if two edits are
PREFIX-DISJOINT at any level then they COMMUTE — applying them in either order gives the same world,
for every world. Decided exhaustively over the pinned edit family: 18144 prefix-disjoint pairs, 18144
commuting, 0 exceptions.

THE POLARITY, WHICH IS WHERE THIS KEEPS GOING WRONG. Disjointness is `lca_depth < L`, NOT
`lca_depth >= threshold`. A HIGH common-ancestor depth means a DEEP SHARED prefix, which means the
SAME subtree, which means OVERLAP. A handed-down statement of this rung had the comparison inverted,
and `_disjoint_by_lca_ge` keeps that form as a plant: MEASURED, it admits 402 NON-COMMUTING pairs as
structurally safe. That is unsound in the direction that ships — it would license exactly the replays
that corrupt state. This is the THIRD appearance of this same inversion in the arc's history (the
2-adic-valuation LCA form in `voxlat`, the "collision-relevant proximity" predicate in a handed-down
framework, and now this), which is enough repetitions to treat the polarity as a hazard class rather
than as three unrelated slips.

THE BOUNDARY, MEASURED RATHER THAN GLOSSED: the predicate is SUFFICIENT and NOT NECESSARY. Of 47922
overlapping pairs, 38640 — about 80% — commute anyway, because two edits writing the SAME value to a
shared cell commute regardless of order. So prefix-disjointness is a SOUND but INCOMPLETE test, and
the incompleteness is large. Stating it as an equivalence would be false, and stating only the
soundness would hide that four fifths of the overlapping cases are still recoverable by the existing
per-instance check. The honest split is therefore:

    prefix-disjoint  -> commutes BY CONSTRUCTION, no check, defect zero
    overlapping      -> fall through to commute/rannull/nway's per-instance check

which is what makes this a strict improvement rather than a replacement: it converts the common case
into a proof and leaves the rest exactly where it was.

LEVEL MONOTONICITY. Disjointness at a COARSE level implies disjointness at every FINER level, since a
coarse prefix is a prefix of a fine one — decided by enumeration, 0 counterexamples. So a coarse level
is the CONSERVATIVE choice: it admits fewer pairs and never admits a wrong one. Deployment can raise
the level to recover precision without ever risking soundness, which is the right direction for a
knob to be safe in.

GRADE. MEASURED: soundness over the whole pinned family; the incompleteness fraction; the inverted
plant's exact unsound admissions; level monotonicity; determinism. DECLARED: the edit family is
last-writer-wins occupancy writes over a 2-level lattice — a bounded model, decided completely within
its bounds, and the extension to richer edit semantics is NOT claimed. does_not_show: commutation for
edits that are not pure writes (read-modify-write, transactional groups); anything about WHEN edits
arrive (that is `lagcomp`/`horn`); that overlapping edits fail to commute (measured, they mostly do);
cross-placement."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb, product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxlat as VX                              # noqa: E402  (the lattice that makes this decidable)

MAGIC = b"URDRDSJ1"
LEVELS = 2                                       # octree height of the decided model
POOL = 14                                        # keys the pinned edit family draws from
BLOCK_LEVEL = 1                                  # the level disjointness is decided at


class DisjointError(Exception):
    def __init__(self, message):
        super().__init__(f"DISJOINT-REFUSE: {message}")
        self.code = "DISJOINT-REFUSE"


# ---- the predicate ---------------------------------------------------------------------------
def prefix(key, level=BLOCK_LEVEL, levels=LEVELS):
    """The Morton prefix naming a subtree. One shift."""
    if type(key) is not int or key < 0:
        raise DisjointError(f"key must be a non-negative int, got {key!r}")
    if not (0 <= level <= levels):
        raise DisjointError(f"level {level!r} outside [0, {levels}]")
    return key >> (3 * (levels - level))


def footprint(edit, level=BLOCK_LEVEL, levels=LEVELS):
    """The set of subtrees an edit touches."""
    return frozenset(prefix(k, level, levels) for k in edit)


def prefix_disjoint(e1, e2, level=BLOCK_LEVEL, levels=LEVELS):
    """THE PREDICATE. Two edits occupy disjoint subtrees iff their prefix sets do not intersect.
    Note the POLARITY: this is `lca_depth < level` between every cross pair, NOT `>= threshold`.
    A deep common ancestor means a shared subtree, which is overlap, not independence."""
    return not (footprint(e1, level, levels) & footprint(e2, level, levels))


def _disjoint_by_lca_ge(e1, e2, level=BLOCK_LEVEL, levels=LEVELS):
    """A FALSIFIER TOOL (not the law): the INVERTED form, in which a deep common ancestor is read as
    independence. It is unsound in the direction that ships — it licenses replays across edits that
    genuinely conflict. Kept because this inversion has now appeared three times in the arc."""
    return min(VX.lca_depth(a, b, levels) for a in e1 for b in e2) >= level


# ---- the semantics ---------------------------------------------------------------------------
def apply(world, edit):
    """Last-writer-wins occupancy write. The declared edit model, bounded and stated."""
    w = dict(world)
    w.update(edit)
    return w


def commutes(e1, e2, worlds):
    """Order-independence, evaluated rather than assumed: both orders must agree on every world."""
    return all(apply(apply(w, e1), e2) == apply(apply(w, e2), e1) for w in worlds)


def keys(levels=LEVELS):
    return [VX.morton(x, y, z, levels) for x, y, z in _prod(range(1 << levels), repeat=3)]


def worlds(levels=LEVELS):
    """Two pinned worlds — an empty one and an alternating one. Fixed, never sampled."""
    ks = keys(levels)
    return [{k: 0 for k in ks}, {k: k % 2 for k in ks}]


def edit_family(pool=POOL, levels=LEVELS):
    """The pinned edit family: every two-key write over the first `pool` keys, at every value
    assignment — so two edits can genuinely CONFLICT on a shared cell. A first draft of this rung
    used single-valued edits, under which every pair commutes trivially and the measurement was
    vacuous; conflict has to be constructible or the census proves nothing."""
    ks = keys(levels)[:pool]
    return [dict(zip(pair, vals)) for pair in _comb(ks, 2) for vals in _prod((0, 1), repeat=2)]


# ---- the census, decided ----------------------------------------------------------------------
def census(level=BLOCK_LEVEL, _pred=None):
    """EXHAUSTIVE over every pair of the pinned family. Returns
    (disjoint_pairs, disjoint_commuting, overlap_pairs, overlap_commuting)."""
    pred = _pred or prefix_disjoint
    fam, wl = edit_family(), worlds()
    dn = dc = on = oc = 0
    for e1, e2 in _comb(fam, 2):
        c = commutes(e1, e2, wl)
        if pred(e1, e2, level):
            dn += 1; dc += c
        else:
            on += 1; oc += c
    return dn, dc, on, oc


def disjointness_is_sufficient(level=BLOCK_LEVEL):
    """THE THEOREM: every prefix-disjoint pair commutes. Decided, not sampled."""
    dn, dc, _on, _oc = census(level)
    return dn > 0 and dc == dn


def disjointness_is_not_necessary(level=BLOCK_LEVEL):
    """THE BOUNDARY, measured rather than glossed: overlapping pairs mostly commute anyway, because
    two edits writing the same value to a shared cell are order-independent. Returns
    (overlap_pairs, overlap_commuting) so the incompleteness is a number, not an adjective."""
    _dn, _dc, on, oc = census(level)
    return on, oc


def inverted_predicate_is_unsound(level=BLOCK_LEVEL):
    """The plant BITES, and in the dangerous direction: count the NON-COMMUTING pairs the inverted
    form would admit as structurally safe. Must be strictly positive."""
    fam, wl = edit_family(), worlds()
    return sum(1 for e1, e2 in _comb(fam, 2)
               if _disjoint_by_lca_ge(e1, e2, level) and not commutes(e1, e2, wl))


def law_admits_nothing_unsound(level=BLOCK_LEVEL):
    """The same count for the LAW, which must be exactly zero."""
    fam, wl = edit_family(), worlds()
    return sum(1 for e1, e2 in _comb(fam, 2)
               if prefix_disjoint(e1, e2, level) and not commutes(e1, e2, wl))


def level_monotone(levels=LEVELS):
    """Disjointness at a COARSE level implies disjointness at every FINER level — a coarse prefix is
    a prefix of a fine one. Decided by enumeration. This is what makes the level a SAFE knob: raising
    it recovers precision and can never admit a pair the coarser level refused."""
    ks = keys(levels)
    for lo in range(1, levels):
        for a in ks:
            for b in ks:
                if prefix(a, lo, levels) != prefix(b, lo, levels) \
                        and prefix(a, lo + 1, levels) == prefix(b, lo + 1, levels):
                    return False
    return True


def split_of_the_work(level=BLOCK_LEVEL):
    """What this rung actually buys, as a fraction of pairs: how many go to the STRUCTURAL path
    (proved, no check) versus the PER-INSTANCE path (commute/rannull/nway, unchanged)."""
    dn, _dc, on, _oc = census(level)
    return dn, on, dn + on


# ---- digests + scenes -------------------------------------------------------------------------
def dsj_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_soundness():
    """The theorem, decided over every pair of the pinned family."""
    return dsj_digest("soundness", f"{census()}:{disjointness_is_sufficient()}:"
                                   f"{law_admits_nothing_unsound()}")


def _scene_incompleteness():
    """The honest boundary: sufficient, not necessary, and by how much."""
    return dsj_digest("incompleteness", f"{disjointness_is_not_necessary()}:{split_of_the_work()}")


def _scene_polarity():
    """The inverted plant, and the exact number of unsound admissions it makes."""
    return dsj_digest("polarity", f"{inverted_predicate_is_unsound()}:{level_monotone()}")


_SCENES = {"soundness": _scene_soundness, "incompleteness": _scene_incompleteness,
           "polarity": _scene_polarity}
SCENES = ("soundness", "incompleteness", "polarity")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_disjoint.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise DisjointError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    dn, dc, on, oc = census()
    print(f"disjoint {dc}/{dn} commute (sufficient {dc == dn}) | "
          f"overlap {oc}/{on} commute (necessary {oc == 0})")
    print(f"inverted plant admits {inverted_predicate_is_unsound()} non-commuting pairs | "
          f"law admits {law_admits_nothing_unsound()} | level monotone {level_monotone()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
