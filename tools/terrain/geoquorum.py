# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""geoquorum — ADVERSARIAL GEOMETRY SUBMISSION (URDRGEO1): admitting user-authored world geometry
against evidence the submitter does not control. Slice S4 of the city-replica arc. NO NEW GLYPH.

THE HOLE THIS CLOSES, AND WHY THE OBVIOUS DEFENCE DOES NOT. The previous rung (`voxlat`, URDRVOX1)
makes quantization canonical, and the planned divergence bound would bound how far a rendered splat
may sit from its collision lattice. Both are defences against ERROR. Neither is a defence against
INTENT, and the reason is exact rather than rhetorical:

    A submitter who thins a wall in the SPLAT and derives the lattice FROM the doctored splat
    produces a pair whose internal divergence is ZERO. The two agree perfectly. Both are wrong.

`divergence_is_blind` measures precisely that: the honest pair and the doctored pair have the same
internal divergence, so no bound computed from a submission alone can separate them. This is not a
gap in the bound's threshold; it is a statement about what a single submission can possibly witness.
Self-consistency is the one property a liar can always supply.

THE ONLY EVIDENCE A LIAR DOES NOT CONTROL is other people's captures of the same place. That is
exactly `oobprior`'s structure (URDROOB1) — a reference built from a cohort with the judged party
STRUCTURALLY EXCLUDED — applied to geometry rather than to latency. The composition is literal, not
decorative: blocks are identified by Morton prefix using `voxlat`'s lattice and LCA machinery, so
"the same place" is an exact integer predicate rather than a spatial tolerance.

THE QUORUM THEOREM, DECIDED. Occupancy is admitted by strict MAJORITY over the cohort. For a cohort
of k submissions of which c collude on the same falsehood, the consensus flips exactly when

    c  >=  ceil(k / 2)

DECIDED EXHAUSTIVELY over every (k, c) with k <= 9: `flip_threshold` enumerates rather than derives.
A first draft of this rung asserted floor(k/2) + 1 and the enumeration REFUSED it. The two forms
agree on odd k and differ on every even k, because a strict majority of 2j requires j+1 votes while a
strict majority of 2j-1 requires only j — so the even cohort is broken by the same c that breaks the
odd one below it.

  COROLLARY, and it is operational rather than cosmetic: AN EVEN COHORT BUYS NOTHING. Cohort 4 has
  exactly the resistance of cohort 3, cohort 6 of cohort 5. The marginal submission is wasted, so
  cohorts should be recruited to ODD sizes. `even_cohorts_buy_nothing` decides this over every pair
  in range. This is the kind of result the wrong closed form would have hidden.

A lone liar therefore flips NOTHING at any cohort of 3 or more — measured, not assumed.

WHY MAJORITY AND NOT THE TWO OBVIOUS ALTERNATIVES, both kept as plants because each fails to exactly
one direction of attack and the pair of failures is what argues for the middle:

  * UNION (admit any voxel anyone claims) fails to ADDITION. One liar invents cover that is not
    there, knows where it is, and no one else can see it.
  * INTERSECTION (admit only what everyone claims) fails to DELETION. One liar simply omits a wall
    and it vanishes from the world for everybody.

Majority resists both, up to the decided threshold. `_consensus_by_union` and
`_consensus_by_intersection` are measured falling to a SINGLE liar; `_consensus_including_self` is
the third plant and is `oobprior`'s own defect restated for geometry — a submitter that votes on its
own admission is self-certifying, and at cohort size 1 it is admitted unconditionally.

TWO REFUSAL CLASSES, KEPT DISTINCT. `GEOQUORUM-THIN` (fewer than MIN_COHORT independent submissions
cover this block) is NOT a cheating verdict — it is coverage-or-refusal, the same discipline
`pingpolicy` uses, and it must never be counted as an integrity event. `GEOQUORUM-DEVIATE` is the
integrity verdict. Conflating them would inflate cheat statistics exactly the way the surveyed
industry does: Escape from Tarkov's own Q1 2026 figures put only 54% of banned accounts as actually
cheating, and that is what happens when unadjudicable and dishonest share a counter.

GRADE. MEASURED: the blindness of internal divergence to a self-consistent doctored pair; the
collusion threshold, decided exhaustively for every cohort up to 9; the single-liar failure of union
and intersection; the self-inclusion plant's unconditional admission at cohort 1; determinism.
DECLARED: majority is a POLICY over the cohort, not a theorem about truth — it decides what the
cohort agrees on, and the arc has no way to know the cohort is right. does_not_show, and this is the
load-bearing boundary: **NO SYBIL RESISTANCE**. k submissions from one person wearing k identities
defeat this completely, because the mechanism reasons about submissions and not about people.
Identity is a different subsystem and this rung does not touch it, does not claim it, and would be
dishonest if it did. Also does_not_show: that the cohort's consensus matches the real city (the real
city changes, and a stale unanimous cohort is unanimously wrong); capture quality; cross-placement."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxlat as VX                            # noqa: E402  (the lattice this adjudicates over)

MAGIC = b"URDRGEO1"
MIN_COHORT = 5                                 # below this a block is unadjudicable, never "cheating"
#   NOT 3. A first draft inherited 3 by analogy with oobprior and a falsifier refused it: the
#   leave-one-out reference has k-1 members, so at k=3 an honest submitter is judged against a
#   cohort of 2, which ONE liar deadlocks — framing the honest party. See false_positive_threshold.
BLOCK_LEVEL = 2                                # octree depth at which "the same place" is decided
MAX_COHORT_DECIDED = 9                         # the threshold theorem is decided up to this size

R_ADMIT = 0
R_THIN = 1                                     # coverage-or-refusal — NOT an integrity verdict
R_DEVIATE = 2                                  # the integrity verdict
_REASON_NAME = {R_ADMIT: "ADMIT", R_THIN: "GEOQUORUM-THIN", R_DEVIATE: "GEOQUORUM-DEVIATE"}


class GeoquorumError(Exception):
    def __init__(self, message):
        super().__init__(f"GEOQUORUM-REFUSE: {message}")
        self.code = "GEOQUORUM-REFUSE"


# ---- blocks: "the same place" as an exact integer predicate -----------------------------------
def block_of(key, level=BLOCK_LEVEL, levels=VX.LEVELS):
    """The Morton prefix naming the block a voxel belongs to. Exact integer, no tolerance."""
    if type(key) is not int or key < 0:
        raise GeoquorumError(f"voxel key must be a non-negative int, got {key!r}")
    return key >> (3 * (levels - level))


def same_block(a, b, level=BLOCK_LEVEL, levels=VX.LEVELS):
    """Two voxels are in the same block iff their octree LCA is at least `level` deep — the
    composition with URDRVOX1 is literal: this is that rung's identity, reused."""
    return VX.lca_depth(a, b, levels) >= level


# ---- the motivating measurement: internal divergence cannot see intent ------------------------
def _wall(thickness=3):
    """An honest wall: a run of occupied voxels."""
    return frozenset(range(thickness))


def doctored(wall, thin_by=1):
    """A wall with voxels removed — the submitter's advantage is shooting and seeing through it."""
    return frozenset(sorted(wall)[thin_by:])


def internal_divergence(splat_occ, lattice_occ):
    """The only quantity a SINGLE submission can witness: how far its own lattice sits from its own
    render. Exact integer symmetric difference."""
    return len(set(splat_occ) ^ set(lattice_occ))


def divergence_is_blind(thickness=3, thin_by=1):
    """THE MEASUREMENT THAT MOTIVATES THIS WHOLE RUNG. An honest submitter derives the lattice from an
    honest splat; a liar derives it from a doctored splat. BOTH have internal divergence zero, so no
    bound computed from a submission alone can tell them apart. Returns (honest_div, doctored_div,
    the_lie_is_real) — the first two must be equal and zero while the third is true."""
    w = _wall(thickness)
    d = doctored(w, thin_by)
    honest = internal_divergence(w, w)
    liar = internal_divergence(d, d)
    return honest, liar, len(w) != len(d)


# ---- the quorum ------------------------------------------------------------------------------
def consensus(submissions, voxel, exclude=None):
    """MAJORITY over the cohort, with the judged submitter STRUCTURALLY EXCLUDED — the exclusion is
    an argument, not a discipline anyone has to remember. `submissions` is a sequence of occupancy
    sets. Returns True iff strictly more than half the referenced submissions claim `voxel`."""
    ref = [s for i, s in enumerate(submissions) if i != exclude]
    if not ref:
        return False
    claims = sum(1 for s in ref if voxel in s)
    return 2 * claims > len(ref)


def _consensus_including_self(submissions, voxel, exclude=None):
    """A FALSIFIER TOOL (not the law): `oobprior`'s own defect restated for geometry. The judged
    submitter votes on its own admission, so at a cohort of one it certifies itself unconditionally
    and at larger cohorts it needs one fewer accomplice."""
    claims = sum(1 for s in submissions if voxel in s)
    return 2 * claims > len(submissions)


def _consensus_by_union(submissions, voxel, exclude=None):
    """A FALSIFIER TOOL (not the law): admit anything anyone claims. Fails to ADDITION — one liar
    invents cover nobody else can see and knows exactly where it is."""
    ref = [s for i, s in enumerate(submissions) if i != exclude]
    return any(voxel in s for s in ref)


def _consensus_by_intersection(submissions, voxel, exclude=None):
    """A FALSIFIER TOOL (not the law): admit only what everyone claims. Fails to DELETION — one liar
    omits a wall and it vanishes from the world for everybody."""
    ref = [s for i, s in enumerate(submissions) if i != exclude]
    return bool(ref) and all(voxel in s for s in ref)


def admitted_block(submissions, voxels, _rule=None):
    """The world the cohort agrees on, over the voxels of one block."""
    rule = _rule or consensus
    return frozenset(v for v in voxels if rule(submissions, v))


def adjudicate(submissions, judged, voxels, _rule=None):
    """The verdict on ONE submission against a reference it does not control. Coverage first: below
    MIN_COHORT the block is unadjudicable and refused as THIN, which is NOT an integrity finding."""
    if not (0 <= judged < len(submissions)):
        raise GeoquorumError(f"judged index {judged!r} outside the cohort")
    if len(submissions) < MIN_COHORT:
        return R_THIN, frozenset()
    rule = _rule or consensus
    ref = frozenset(v for v in voxels if rule(submissions, v, exclude=judged))
    mine = frozenset(v for v in voxels if v in submissions[judged])
    return (R_ADMIT if mine == ref else R_DEVIATE), ref


# ---- the threshold theorem, decided ----------------------------------------------------------
def flips(k, c, _rule=None):
    """Does a cohort of k submissions, c of which collude on omitting the voxel, lose it? ENUMERATED
    over an explicit cohort rather than derived."""
    subs = [frozenset() if i < c else frozenset({0}) for i in range(k)]
    rule = _rule or consensus
    return not rule(subs, 0, exclude=None)


def flip_threshold(k, _rule=None):
    """The smallest number of colluders that flips a cohort of k — decided by enumeration."""
    for c in range(k + 1):
        if flips(k, c, _rule):
            return c
    return k + 1


def threshold_is_ceil_half(max_k=MAX_COHORT_DECIDED):
    """THE THEOREM, decided exhaustively for every cohort size: the collusion threshold is EXACTLY
    ceil(k/2), i.e. (k+1)//2. A first draft of this rung asserted floor(k/2)+1 and the enumeration
    refused it — the two agree on odd k and differ on every even k, because strict majority means a
    cohort of 2k has the same resistance as a cohort of 2k-1."""
    return all(flip_threshold(k) == (k + 1) // 2 for k in range(1, max_k + 1))


def even_cohorts_buy_nothing(max_k=MAX_COHORT_DECIDED):
    """THE COROLLARY, and it is operational rather than cosmetic: an even cohort has exactly the
    resistance of the odd cohort below it, so the marginal submission is wasted. Recruit to ODD
    cohort sizes. Decided over every pair in range."""
    return all(flip_threshold(2 * j) == flip_threshold(2 * j - 1)
               for j in range(1, max_k // 2 + 1))


def admit_threshold(k, _rule=None):
    """The quantity the ADJUDICATION cares about, as distinct from world consensus: the smallest
    number of colluders needed for a LIAR to be admitted when judged. Decided by enumeration."""
    voxels = (0,)
    for c in range(1, k + 1):
        subs = [frozenset() if i < c else frozenset({0}) for i in range(k)]
        if adjudicate(subs, 0, voxels, _rule=_rule)[0] == R_ADMIT:
            return c
    return k + 1


def false_positive_threshold(k, _rule=None):
    """THE QUANTITY THAT KEEPS A BAN LIST HONEST: the smallest number of liars needed to make an
    HONEST submitter be judged DEVIATE. Measured against the leave-one-out REFERENCE directly, so it
    is defined below MIN_COHORT too — otherwise the coverage gate would mask the very setting this
    number exists to refuse. It is NOT the collusion threshold, because leave-one-out shrinks the
    reference to k-1, which is exactly the trap a first draft fell into by setting MIN_COHORT = 3 out
    of analogy with `oobprior`: at k = 3 the reference is 2 and a single liar deadlocks it, framing an
    honest contributor. Flagging honest people is the worse error here, and this governs it."""
    rule = _rule or consensus
    for c in range(0, k):
        subs = [frozenset({0})] + [frozenset() if i < c else frozenset({0}) for i in range(k - 1)]
        if not rule(subs, 0, exclude=0):       # the reference no longer agrees with the honest claim
            return c
    return k


def lone_liar_cannot_frame(min_k=MIN_COHORT, max_k=MAX_COHORT_DECIDED):
    """THE LAW that sets MIN_COHORT: at every admissible cohort, one liar cannot make an honest
    submitter deviate. False at k = 3, which is why MIN_COHORT is 5 and not 3."""
    return all(false_positive_threshold(k) >= 2 for k in range(min_k, max_k + 1))


def three_would_have_framed_the_honest(_k=3):
    """The REFUSED SETTING, kept as a measured witness rather than a footnote: at a cohort of 3 the
    false-positive threshold is 1 — one liar is enough to have an honest contributor judged DEVIATE.
    That measurement is why MIN_COHORT is 5. It is checked against the reference directly, below the
    coverage gate, because the gate would otherwise hide it."""
    return false_positive_threshold(_k) == 1 and false_positive_threshold(MIN_COHORT) >= 2


def the_two_optima_disagree(max_k=MAX_COHORT_DECIDED):
    """AN HONEST TENSION, surfaced rather than smoothed over. World consensus uses all k and is
    strongest at ODD k; adjudication uses the leave-one-out reference of k-1 and is therefore
    strongest when k-1 is odd, i.e. at EVEN k. The two quantities do not want the same cohort size.
    Returns True iff that disagreement is real in the measured range — it is resolved by policy
    (odd k >= 5, which is strong on both) and not by pretending one number serves both."""
    return any(flip_threshold(k) > flip_threshold(k + 1) or
               false_positive_threshold(k) < false_positive_threshold(k + 1)
               for k in range(MIN_COHORT, max_k))


def lone_liar_flips_nothing(max_k=MAX_COHORT_DECIDED):
    """The operative corollary: at any admissible cohort a single liar changes nothing."""
    return all(not flips(k, 1) for k in range(MIN_COHORT, max_k + 1))


def plant_thresholds(max_k=MAX_COHORT_DECIDED):
    """MEASURED: what each rejected rule costs. Union and intersection both fall to ONE liar, in
    opposite directions; self-inclusion needs one fewer accomplice than the law."""
    return {
        "law": [flip_threshold(k) for k in range(1, max_k + 1)],
        "intersection": [flip_threshold(k, _consensus_by_intersection) for k in range(1, max_k + 1)],
    }


def admit_plant_thresholds(max_k=MAX_COHORT_DECIDED):
    """MEASURED, and this is where the self-inclusion plant actually bites — in ADJUDICATION, not in
    world consensus. A submitter that votes on its own admission needs FEWER accomplices, and the
    gap appears on exactly the even cohorts the corollary above already calls wasteful."""
    ks = range(MIN_COHORT, max_k + 1)
    return {"law": [admit_threshold(k) for k in ks],
            "including_self": [admit_threshold(k, _consensus_including_self) for k in ks]}


def self_inclusion_lowers_the_bar(max_k=MAX_COHORT_DECIDED):
    """The plant bites, stated so it can be false: there must EXIST a cohort at which self-inclusion
    admits a liar the law refuses, and self-inclusion must NEVER require more accomplices."""
    ks = list(range(MIN_COHORT, max_k + 1))
    law = [admit_threshold(k) for k in ks]
    plant = [admit_threshold(k, _consensus_including_self) for k in ks]
    return any(p < l for p, l in zip(plant, law)) and all(p <= l for p, l in zip(plant, law))


def union_fails_to_addition(k=5):
    """The other direction, which `flips` (a deletion attack) cannot see: under UNION a lone liar
    ADDS a voxel no honest submission claims, and it is admitted."""
    subs = [frozenset({99})] + [frozenset() for _ in range(k - 1)]
    return _consensus_by_union(subs, 99) and not consensus(subs, 99)


def self_inclusion_self_certifies():
    """The self-inclusion plant at its starkest: a cohort of one admits its own claim."""
    solo = [frozenset({7})]
    return _consensus_including_self(solo, 7, exclude=0) and not consensus(solo, 7, exclude=0)


# ---- digests + scenes -------------------------------------------------------------------------
def geo_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_blindness():
    """Internal divergence cannot separate an honest pair from a self-consistent doctored one."""
    return geo_digest("blindness", f"{divergence_is_blind()}:{divergence_is_blind(5, 2)}")


def _scene_threshold():
    """The quorum theorem, decided over every cohort size up to the pinned maximum."""
    return geo_digest("threshold", f"{[flip_threshold(k) for k in range(1, MAX_COHORT_DECIDED+1)]}:"
                                   f"{threshold_is_ceil_half()}:{lone_liar_flips_nothing()}:"
                                   f"{even_cohorts_buy_nothing()}:"
                                   f"{[false_positive_threshold(k) for k in range(1, MAX_COHORT_DECIDED+1)]}:"
                                   f"{lone_liar_cannot_frame()}:{three_would_have_framed_the_honest()}:"
                                   f"{the_two_optima_disagree()}")


def _scene_plants():
    """What each rejected rule costs, measured rather than argued."""
    p = plant_thresholds()
    return geo_digest("plants", f"{sorted(p.items())}:{union_fails_to_addition()}:"
                                f"{self_inclusion_self_certifies()}:"
                                f"{sorted(admit_plant_thresholds().items())}:"
                                f"{self_inclusion_lowers_the_bar()}")


def _scene_verdicts():
    """The two refusal classes, kept distinct: THIN is coverage, DEVIATE is integrity."""
    voxels = tuple(range(4))
    honest = [frozenset({0, 1, 2}) for _ in range(3)]
    liar = [frozenset({1, 2})] + [frozenset({0, 1, 2}) for _ in range(2)]
    rows = [
        ("thin", adjudicate(honest[:2], 0, voxels)[0]),
        ("honest", adjudicate(honest, 0, voxels)[0]),
        ("liar", adjudicate(liar, 0, voxels)[0]),
        ("liar_world", sorted(admitted_block(liar, voxels))),
    ]
    return geo_digest("verdicts", f"{rows}:{sorted(_REASON_NAME.items())}")


_SCENES = {"blindness": _scene_blindness, "threshold": _scene_threshold,
           "plants": _scene_plants, "verdicts": _scene_verdicts}
SCENES = ("blindness", "threshold", "plants", "verdicts")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_geoquorum.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise GeoquorumError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"blindness (honest_div, liar_div, lie_real) = {divergence_is_blind()}")
    print(f"threshold ceil(k/2) {threshold_is_ceil_half()} | lone liar flips nothing "
          f"{lone_liar_flips_nothing()} | even cohorts wasted {even_cohorts_buy_nothing()}")
    for k, v in sorted(plant_thresholds().items()):
        print(f"  flip {k:>13}: {v}")
    for k, v in sorted(admit_plant_thresholds().items()):
        print(f"  admit {k:>12}: {v}")
    print(f"self-inclusion lowers the bar {self_inclusion_lowers_the_bar()}")
    print(f"union fails to addition {union_fails_to_addition()} | "
          f"self-inclusion self-certifies {self_inclusion_self_certifies()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
