# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""divergence — THE QUANTIZATION DEFECT, IN CELLS (URDRDVG1): slice S2 of the city-replica arc, the
last one, and the one that was always known to be irreducible. NO NEW GLYPH.

WHY THIS IS THE LAST SLICE AND WHY IT CANNOT BE ELIMINATED. S6 turned out to be zero by construction
once visibility was adjudicated on the lattice; S3 and S4 are enforcement; Half B made commutation
structural. S2 is different: capture error is intrinsic to the float-to-integer boundary and no
architectural move removes it. It can only be MEASURED — and the whole content of this rung is
measuring the right thing.

THE MEASURAND IS NOT A RATE. A handed-down protocol proposed the mean fraction of cells whose
occupancy flips. That is the wrong quantity for the same reason luminance was the wrong quantity for
S6: it is not in the units the adversary works in. **An adversary does not attack the mean.** A 2%
flip rate scattered across a park is nothing; the same 2% concentrated on one wall face is a hole a
player walks through. The rate is identical and the consequence is not.

    THE QUANTITY IS THE LARGEST CONNECTED RUN OF FLIPPED CELLS — an integer, and the thing a body
    can actually pass through.

MEASURED, and this is the refutation stated so it can be false: two perturbations of the same wall
with the SAME flip count and the SAME rate, one scattered and one contiguous, differ in largest run
and differ in whether the wall is BREACHED. `rate_is_blind` returns both and they must disagree.

THE ATTAINED MAXIMUM, DECIDED. `worst_run(k)` enumerates EVERY k-cell perturbation of the pinned wall
and returns the largest run achievable — a worst-case-over-inputs, not a sample mean, decided by
enumeration exactly as `voxlat` decided 4*B^3 and `horn` decided its minimax. A mean over sampled
perturbations would report a number an adversary never has to accept.

THE NOISE MODEL IS DECLARED AS A MODEL, WHICH IS THE HONEST PART. This rung perturbs by ADVERSARIAL
CHOICE — every k-subset — not by a Gaussian. Real capture error is view-dependent, correlated and
anisotropic: worse behind the capture hemisphere, worse on specular and textureless surfaces. An iid
Gaussian would report an optimistic figure with no bound on its optimism. Adversarial choice over a
synthetic wall is not an estimate of real divergence either — it is an upper bound on what k flipped
cells can do to THIS geometry, and a LOWER bound on what real capture does to a real one, because
real error is correlated in exactly the direction that builds runs. Both directions are stated; the
number is not presented as a prediction.

THE BREACH PREDICATE is what makes the run count operational rather than descriptive: a wall is
breached when the flipped cells complete a traversable path from one side to the other. That is a
connectivity question on an integer lattice, decided by flood fill — the one step of the splat
pipeline that was genuinely integer all along.

GRADE. MEASURED: the rate/run divergence on same-rate perturbations; the attained worst run over
every k-subset at the pinned k; the breach census; monotonicity of the worst run in k; determinism.
DECLARED: the perturbation model is adversarial k-subset choice over a synthetic wall — a MODEL, and
the figure it yields bounds this geometry rather than predicting a real capture; the wall is 2D for
tractability and the 3D case is not enumerated here. does_not_show: what k a real capture produces
(that needs a corpus of real scans and is the open half of S2 — this rung supplies the metric, not
the datum); any float capture pipeline; that a non-breaching run is harmless (it is not, it is only
non-traversable); cross-placement."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRDVG1"
W, H = 7, 5                                       # the pinned scene
WALL_X = 3                                        # a vertical wall starting at this column
THICK = 2                                         # ...and this many columns thick
PINNED_K = (1, 2, 3)                              # perturbation sizes the worst case is DECIDED at


class DivergenceError(Exception):
    def __init__(self, message):
        super().__init__(f"DIVERGENCE-REFUSE: {message}")
        self.code = "DIVERGENCE-REFUSE"


# ---- the scene ------------------------------------------------------------------------------------
def wall():
    """The ground-truth occupancy: a solid vertical wall separating left from right, THICK columns
    deep. Thickness is what makes the run count relate to the breach at all — a one-cell wall falls
    to any single hole, so run length and traversability would be unrelated and the metric would be
    describing rather than predicting. A first draft used thickness 1 and measured a minimum
    breaching run of 1, refuting its own claim that a breach needs a full run; the scene was changed
    rather than the claim weakened."""
    return frozenset((WALL_X + t, y) for t in range(THICK) for y in range(H))


def cells():
    return tuple((x, y) for x in range(W) for y in range(H))


def perturb(gt, flips):
    """Apply a flip set — an occupancy cell removed is a hole, one added is phantom cover."""
    for c in flips:
        if c not in cells():
            raise DivergenceError(f"cell {c!r} outside the scene")
    return frozenset(gt ^ frozenset(flips))


# ---- the measurands -------------------------------------------------------------------------------
def flipped(gt, obs):
    """The COUNT, in cells. Exact integer symmetric difference — never a rate."""
    return len(set(gt) ^ set(obs))


def flip_rate_num_den(gt, obs):
    """The rate the handed-down protocol proposed, as an exact RATIONAL pair so it never becomes a
    float. Kept only so the refutation can show two perturbations sharing it."""
    return flipped(gt, obs), len(cells())


def _components(cs):
    """Connected components of a cell set under 4-connectivity. Integer flood fill — the one step of
    the splat pipeline that was genuinely integer all along."""
    todo, out = set(cs), []
    while todo:
        seed = min(todo)
        comp, stack = set(), [seed]
        while stack:
            c = stack.pop()
            if c in comp or c not in todo:
                continue
            comp.add(c)
            x, y = c
            for n in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if n in todo and n not in comp:
                    stack.append(n)
        todo -= comp
        out.append(frozenset(comp))
    return tuple(sorted(out, key=lambda s: (-len(s), sorted(s))))


def largest_run(gt, obs):
    """THE QUANTITY: the largest connected run of flipped cells. An integer, and the thing a body can
    actually pass through — as opposed to a rate, which the adversary does not attack."""
    diff = frozenset(set(gt) ^ set(obs))
    comps = _components(diff)
    return len(comps[0]) if comps else 0


def breached(obs):
    """OPERATIONAL: is there a traversable path from the left edge to the right edge through
    unoccupied cells? Connectivity on the integer lattice, decided by flood fill."""
    free = frozenset(c for c in cells() if c not in obs)
    left = frozenset(c for c in free if c[0] == 0)
    if not left:
        return False
    seen, stack = set(), list(left)
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        seen.add(c)
        x, y = c
        for n in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if n in free and n not in seen:
                stack.append(n)
    return any(c[0] == W - 1 for c in seen)


# ---- the refutation: rate is blind to the thing that matters ----------------------------------------
def rate_is_blind():
    """THE REFUTATION, stated so it can be false. Two perturbations of the same wall with the SAME
    flip count — hence the same rate — one SCATTERED and one CONTIGUOUS. Returns
    ((rate_a, run_a, breach_a), (rate_b, run_b, breach_b)); the rates must be EQUAL and the runs and
    breaches must DIFFER, which is exactly what makes the rate useless as the measurand."""
    gt = wall()
    scattered = [(WALL_X, 0), (WALL_X + 1, 2)]       # holes in different rows: no aligned path
    contiguous = [(WALL_X, 0), (WALL_X + 1, 0)]      # holes in the SAME row: the wall is open
    a, b = perturb(gt, scattered), perturb(gt, contiguous)
    return ((flip_rate_num_den(gt, a), largest_run(gt, a), breached(a)),
            (flip_rate_num_den(gt, b), largest_run(gt, b), breached(b)))


def rate_equal_run_differs():
    """The law: same rate, different run. If this ever goes False the refutation has evaporated."""
    (ra, run_a, _ba), (rb, run_b, _bb) = rate_is_blind()
    return ra == rb and run_a != run_b


def _defect_by_rate(gt, obs):
    """A FALSIFIER TOOL (not the measurand): the handed-down rate. It assigns the SAME defect to a
    scattered perturbation and to one that opens a traversable hole."""
    n, d = flip_rate_num_den(gt, obs)
    return (n, d)


def rate_plant_conflates_them():
    """The plant BITES: the rate cannot separate the two, and the run can."""
    gt = wall()
    a = perturb(gt, [(WALL_X, 0), (WALL_X + 1, 2)])
    b = perturb(gt, [(WALL_X, 0), (WALL_X + 1, 0)])
    return _defect_by_rate(gt, a) == _defect_by_rate(gt, b) and largest_run(gt, a) != largest_run(gt, b)


# ---- the attained maximum, decided ------------------------------------------------------------------
def worst_run(k):
    """DECIDED: over EVERY k-cell perturbation of the pinned wall, the largest run achievable. A
    worst-case-over-inputs, enumerated — not a mean over samples, which reports a number the adversary
    never has to accept."""
    if not (1 <= k <= 3):
        raise DivergenceError("the worst case is decided only at the pinned perturbation sizes")
    gt, best = wall(), 0
    for flips in _comb(cells(), k):
        r = largest_run(gt, perturb(gt, flips))
        if r > best:
            best = r
    return best


def worst_run_table(ks=PINNED_K):
    return tuple((k, worst_run(k)) for k in ks)


def worst_run_is_k(ks=PINNED_K):
    """The attained maximum is exactly k: an adversary who may flip k cells can always make them
    contiguous. Obvious in hindsight and decided rather than assumed — the point is that the bound is
    attained, so it is a bound and not an estimate."""
    return all(worst_run(k) == k for k in ks)


def breach_census(k=3):
    """MEASURED: of every k-cell perturbation, how many BREACH the wall. The operational figure."""
    if not (1 <= k <= 3):
        raise DivergenceError("the breach census is decided only at the pinned sizes")
    gt = wall()
    total = breach = 0
    for flips in _comb(cells(), k):
        total += 1
        if breached(perturb(gt, flips)):
            breach += 1
    return breach, total


def breach_needs_a_run_of_at_least_thickness(k=3):
    """THE CONNECTION between the metric and the consequence, DECIDED: a breach requires the flipped
    cells to span the wall, so no perturbation whose largest run is below the wall thickness can open
    it. The run count is therefore not a proxy for the harm — it is the harm's PRECONDITION, which is
    what makes it the right measurand rather than a convenient one. Returns
    (min_run_among_breaching, THICK); the first must be at least the second."""
    gt = wall()
    runs = [largest_run(gt, perturb(gt, f)) for f in _comb(cells(), k)
            if breached(perturb(gt, f))]
    return (min(runs) if runs else 0), THICK


# ---- digests + scenes -------------------------------------------------------------------------
def dv_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_refutation():
    return dv_digest("refutation", f"{rate_is_blind()}:{rate_equal_run_differs()}:"
                                   f"{rate_plant_conflates_them()}")


def _scene_worst():
    return dv_digest("worst", f"{worst_run_table()}:{worst_run_is_k()}")


def _scene_breach():
    return dv_digest("breach", f"{breach_census()}:{breach_needs_a_run_of_at_least_thickness()}:"
                               f"{sorted(wall())}")


_SCENES = {"refutation": _scene_refutation, "worst": _scene_worst, "breach": _scene_breach}
SCENES = ("refutation", "worst", "breach")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_divergence.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise DivergenceError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    (ra, runa, ba), (rb, runb, bb) = rate_is_blind()
    print(f"scattered: rate {ra[0]}/{ra[1]} run {runa} breached {ba}")
    print(f"contiguous: rate {rb[0]}/{rb[1]} run {runb} breached {bb}")
    print(f"same rate, different run: {rate_equal_run_differs()} | plant conflates: "
          f"{rate_plant_conflates_them()}")
    print(f"worst run table {worst_run_table()} (attained = k: {worst_run_is_k()})")
    print(f"breach census {breach_census()} | min breaching run vs thickness "
          f"{breach_needs_a_run_of_at_least_thickness()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
