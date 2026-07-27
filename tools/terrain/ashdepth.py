# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""ashdepth — THE VACUITY FLOOR (URDRASH1): how far an abstraction may be coarsened before it stops
saying anything, and the tripwire that refuses silence. NO NEW GLYPH.

THE PREMISE THAT INVERTED. A handed-down design proposed an "ash-depth bound" k* — the coarsest
abstraction level at which `P subset gamma_k(alpha_k(P))` still holds — on the reasoning that burning
past it "collapses the Galois connection into an unsound approximation." MEASURED, that is backwards,
and the correction is the whole rung:

    level 0 (coarsest) :    0/12090 fast-path,  0 unsound   VACUOUS
    level 1            : 4212/12090 fast-path,  0 unsound   sound
    level 2 (finest)   : 8580/12090 fast-path,  0 unsound   sound

SOUNDNESS NEVER BREAKS. Coarsening is strictly MORE CONSERVATIVE — that is `disjoint`'s already-decided
level monotonicity, coarse-disjoint implying fine-disjoint — so a coarser abstraction admits strictly
FEWER pairs and can never admit a wrong one. `P subset gamma_k(alpha_k(P))` holds at EVERY k including
the coarsest, so the proposed k* is vacuously the maximum burn and the guard would pass at the exact
point it was built to catch.

The failure at full burn is not a lie. It is an EMPTY FAST PATH. Burning past the useful depth does
not breach the Galois connection; it collapses alpha to a constant, and a constant abstraction is
perfectly sound and perfectly useless. **A void is sound.**

THE BOUND THAT IS ACTUALLY WORTH GUARDING is therefore the other end:

    k_min = min { k : alpha_k still DISTINGUISHES something, i.e. the fast path is non-empty }

Decided by the same monotonicity read in the same direction, and it catches the failure this
architecture actually admits — an accelerator that proves nothing — rather than the one it structurally
cannot commit.

WHY THIS RUNG EXISTS AT ALL: VACUITY IS THE ARC'S CHARACTERISTIC FAILURE, and this is its FOURTH
appearance in a single session. (1) `disjoint`'s first edit family wrote a single value, under which
every pair commutes trivially and the census would have confirmed ANY predicate including the inverted
one. (2) `frontier`'s greedy plant scored zero on a 60-edit slice where every batch was a SINGLETON,
which would have retired an unsound rule as harmless. (3) The level comparison that produced the table
above was first run on a corpus where the fast path was empty at EVERY level — it distinguished no
levels and was one keystroke from being reported as "soundness never breaks at any level." (4) The
handed-down k* itself, which passes vacuously at maximum burn.

The pattern is stable enough to name as a law rather than fix four times: **in this architecture wrong
answers are rare and empty answers are common, and an empty answer is indistinguishable from a correct
one unless something asserts non-emptiness.** Every census here therefore carries a NON-VACUITY
PRECONDITION, and `VacuityError` is raised rather than a zero quietly returned.

THE TRIPWIRE. `EMPTY_CORPUS` is pinned as a hard test asset: a corpus on which the fast path is empty
at every level. Any future refinement that quietly zeroes the fast path reproduces it and trips
`ASHDEPTH-VACUOUS` instead of reporting a clean zero.

GRADE. MEASURED: the level table over the pinned spread corpus; soundness at every level including
the coarsest; k_min; the four vacuity witnesses; determinism. DECLARED: the corpus is `disjoint`'s
edit model spread across the lattice, bounded and inherited; "distinguishes something" is defined as a
non-empty fast path, which is the weakest useful non-vacuity condition and is a choice.
does_not_show: that k_min is the OPTIMAL operating level — it is the floor below which the abstraction
is silent, never a recommendation of where to sit; any wall-clock cost of a level; that a non-empty
fast path is a USEFUL one (a single admitted pair clears the floor); cross-placement."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import disjoint as DJ                             # noqa: E402
import frontier as FR                             # noqa: E402

MAGIC = b"URDRASH1"
LEVELS = tuple(range(DJ.LEVELS + 1))              # every coarseness the lattice admits, 0 = coarsest
SPREAD = 5                                        # stride of the spread corpus


class VacuityError(Exception):
    """Raised rather than returning a quiet zero. Silence must be loud."""
    def __init__(self, message):
        super().__init__(f"ASHDEPTH-VACUOUS: {message}")
        self.code = "ASHDEPTH-VACUOUS"


class AshdepthError(Exception):
    def __init__(self, message):
        super().__init__(f"ASHDEPTH-REFUSE: {message}")
        self.code = "ASHDEPTH-REFUSE"


# ---- the corpora ---------------------------------------------------------------------------------
def spread_corpus(stride=SPREAD):
    """A corpus SPREAD across the lattice, so different levels actually behave differently. The dense
    corpus `disjoint` pins is fine for its own theorem and useless for this one — a level comparison
    on a corpus where every level scores zero distinguishes no levels."""
    ks = DJ.keys()[::stride]
    return [dict(zip(p, v)) for p in _comb(ks, 2) for v in ((1, 0), (0, 1))]


def EMPTY_CORPUS():
    """THE TRIPWIRE, pinned as a hard asset: every edit touches a COMMON PIVOT KEY, so every pair
    overlaps at every level and the fast path is empty at all of them — including the finest, where
    the prefix is the whole key. A first draft of this corpus merely shared a level-1 block, which
    left the finest level non-empty and the tripwire silent: the vacuity asset was itself
    insufficiently vacuous, which is the fifth turn of this same screw and is why it is measured
    rather than asserted. This is the shape that nearly produced a false finding, kept so any future
    refinement which quietly zeroes the fast path reproduces it and trips instead of returning a
    clean zero."""
    ks = DJ.keys()
    pivot = ks[0]
    return [{pivot: 1, other: 0} for other in ks[1:9]]


# ---- the level census ----------------------------------------------------------------------------
def level_row(edits, level):
    """(fast_path, unsound, total) at one coarseness. `unsound` counts pairs the abstraction admits
    that do NOT actually commute — the quantity the handed-down bound thought would go positive."""
    wl = DJ.worlds()
    proved = unsound = total = 0
    for i, j in _comb(range(len(edits)), 2):
        total += 1
        if DJ.prefix_disjoint(edits[i], edits[j], level):
            proved += 1
            if not DJ.commutes(edits[i], edits[j], wl):
                unsound += 1
    return proved, unsound, total


def level_table(edits=None, levels=LEVELS):
    return tuple((lv,) + level_row(edits if edits is not None else spread_corpus(), lv)
                 for lv in levels)


def soundness_never_breaks(edits=None, levels=LEVELS):
    """THE CORRECTION, DECIDED: no level admits an unsound pair — not even the coarsest. Coarsening
    loses precision monotonically and correctness never."""
    return all(u == 0 for _lv, _p, u, _t in level_table(edits, levels))


def precision_is_monotone_in_level(edits=None, levels=LEVELS):
    """Coarser admits strictly fewer: the fast path is non-decreasing as the level refines. This is
    `disjoint.level_monotone` observed through its consequence rather than its definition."""
    rows = level_table(edits, levels)
    return all(p0 <= p1 for (_l0, p0, _u0, _t0), (_l1, p1, _u1, _t1) in zip(rows, rows[1:]))


def k_min(edits=None, levels=LEVELS):
    """THE BOUND WORTH GUARDING: the coarsest level at which the abstraction still DISTINGUISHES
    anything. Below it the fast path is empty — sound, and silent."""
    for lv, proved, _u, _t in level_table(edits, levels):
        if proved > 0:
            return lv
    raise VacuityError("the fast path is empty at every level; this corpus distinguishes nothing")


def handed_down_k_star(edits=None, levels=LEVELS):
    """A FALSIFIER TOOL (not the law): the proposed bound, max{k : P subset gamma_k(alpha_k(P))}.
    Because soundness holds everywhere it returns the COARSEST level — passing at exactly the point it
    was built to catch, and licensing a fast path of size zero."""
    sound = [lv for lv, _p, u, _t in level_table(edits, levels) if u == 0]
    return min(sound) if sound else None


def handed_down_bound_is_vacuous(edits=None, levels=LEVELS):
    """MEASURED: the proposed bound admits a level whose fast path is EMPTY, and k_min does not."""
    rows = {lv: p for lv, p, _u, _t in level_table(edits, levels)}
    kstar = handed_down_k_star(edits, levels)
    return kstar is not None and rows[kstar] == 0 and rows[k_min(edits, levels)] > 0


# ---- the guard -----------------------------------------------------------------------------------
def guard(edits, level, levels=LEVELS):
    """The runtime tripwire. Refuses any burn coarser than k_min, LOUDLY — an empty fast path is
    reported as ASHDEPTH-VACUOUS rather than returned as a clean zero."""
    if level not in levels:
        raise AshdepthError(f"level {level!r} outside {levels}")
    floor = k_min(edits, levels)
    if level < floor:
        raise VacuityError(f"level {level} is below k_min={floor}: the fast path would be empty")
    return level


def guard_refuses_below_floor(edits=None, levels=LEVELS):
    """The guard bites: every level below k_min raises, every level at or above it passes."""
    fam = edits if edits is not None else spread_corpus()
    floor = k_min(fam, levels)
    for lv in levels:
        try:
            guard(fam, lv, levels)
            if lv < floor:
                return False
        except VacuityError:
            if lv >= floor:
                return False
    return floor > min(levels)


def tripwire_fires_on_the_empty_corpus():
    """THE HARD ASSET: the corpus that distinguishes nothing must RAISE, not return zero. This is the
    corpus that nearly produced a false finding, pinned so it cannot do so silently again."""
    try:
        k_min(EMPTY_CORPUS())
    except VacuityError:
        return True
    return False


def vacuity_witnesses():
    """The four occurrences, as measured constants rather than a memory. Each is a case where an empty
    or degenerate corpus would have confirmed a false claim:
      1. single-valued edits    — every pair commutes; confirms ANY predicate
      2. singleton batches      — no grouping occurs; an unsound grouping rule scores clean
      3. all-levels-empty       — no level distinguishes; 'soundness never breaks' proved on nothing
      4. handed-down k*         — passes at maximum burn, licensing an empty fast path"""
    flat = [dict.fromkeys(p, 1) for p in _comb(DJ.keys()[:8], 2)]
    wl = DJ.worlds()
    w1 = all(DJ.commutes(a, b, wl) for a, b in _comb(flat, 2))
    w2 = max(len(b) for b in FR._batch_by_greedy_pairwise(DJ.edit_family()[:60])) == 1
    w3 = all(p == 0 for _lv, p, _u, _t in level_table(EMPTY_CORPUS()))
    w4 = handed_down_bound_is_vacuous()
    return (w1, w2, w3, w4)


def all_four_vacuities_are_witnessed():
    return all(vacuity_witnesses())


# ---- digests + scenes -------------------------------------------------------------------------
def ash_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_levels():
    return ash_digest("levels", f"{level_table()}:{soundness_never_breaks()}:"
                                f"{precision_is_monotone_in_level()}")


def _scene_floor():
    return ash_digest("floor", f"{k_min()}:{handed_down_k_star()}:"
                               f"{handed_down_bound_is_vacuous()}:{guard_refuses_below_floor()}")


def _scene_vacuity():
    return ash_digest("vacuity", f"{vacuity_witnesses()}:{all_four_vacuities_are_witnessed()}:"
                                 f"{tripwire_fires_on_the_empty_corpus()}")


_SCENES = {"levels": _scene_levels, "floor": _scene_floor, "vacuity": _scene_vacuity}
SCENES = ("levels", "floor", "vacuity")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_ashdepth.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AshdepthError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"{'level':>6} {'fast-path':>10} {'unsound':>8} {'total':>7}")
    for lv, p, u, t in level_table():
        print(f"{lv:>6} {p:>10} {u:>8} {t:>7}  {'VACUOUS' if p == 0 else 'sound'}")
    print(f"k_min {k_min()} | handed-down k* {handed_down_k_star()} "
          f"(vacuous {handed_down_bound_is_vacuous()}) | guard bites {guard_refuses_below_floor()}")
    print(f"four vacuity witnesses {vacuity_witnesses()} | tripwire "
          f"{tripwire_fires_on_the_empty_corpus()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
