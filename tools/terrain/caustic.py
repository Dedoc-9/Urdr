# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""caustic — THE SCALE AT WHICH A BUDGET DIES (URDRCAU1), and the refusal that keeps it honest.

A subsystem with an exact growth law in some countable and a budget has a SCALE AT WHICH IT DIES.
This repository pins a dozen such laws and asks none of them that question; each carries a
"headroom" instead, which is the same fact read from the comfortable end. The caustic reads it
from the other end and needs no new measurement — only slopes that are already pinned.

  caustic(name, budget) -> the LARGEST axis value whose cost still fits the budget

THE REFUSAL IS THE POINT, AND IT WAS PAID FOR. `sealframe`'s first caustic rested on work being
"exactly linear in primitives". The equality was real; the AXIS LABEL WAS NOT — the fixture it was
measured on added a fresh patch of frame per primitive, so the law was linear in COVERAGE. A
caustic computed from a slope whose axis moves with something else is not a bound, it is a
coincidence with units. Generalizing that pattern across five subsystems without carrying the
lesson would have propagated the error five times, so the mechanism REFUSES a fitted slope
(`CAUSTIC-REFUSE`) rather than trusting the name it was given.

THREE KINDS, AND ONLY ONE IS REFUSED:

  PROVEN_CLOSED_FORM — a formula DERIVED and asserted EQUAL to the execution it models, at several
    values of its axis with everything else held fixed. Its axis cannot be confounded, because the
    formula names its own variable and is checked against the real thing as that variable moves.
  ISOLATED_FIXTURE — measured, but on a fixture that varies the named axis ALONE. Weaker than a
    proof and strictly stronger than a slope read off whatever the fixture happened to do.
  FITTED — a slope taken from a fixture that moves more than one thing. REFUSED, by name, with the
    confound stated. This class is populated on purpose: a checker with no rejects is not a
    checker (L61), and the entry that populates it is the very slope that produced the defect.

GRADE (honest, D5): MEASURED — the closed forms are checked against execution on this run (not
quoted from their modules), affineness is verified rather than assumed, the caustic is exact
integer arithmetic over them, and the refusal is proved to fire on the confounded law and NOT on
the sound ones. DECLARED: that a caustic is REACHABLE — it says where the budget is spent, never
that a real workload gets there. `does_not_show`: any wall-clock claim (no timing enters this
module); that a PROVEN law is proven for axis values outside the range checked here; that the
three registered subsystems are all of them."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRCAU1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _p in (_HERE, _os.path.join(_os.path.dirname(_HERE), "physics"),
           _os.path.join(_os.path.dirname(_HERE), "render"),
           _os.path.join(_os.path.dirname(_HERE), "frontfps")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

KIND_PROVEN = "PROVEN_CLOSED_FORM"
KIND_ISOLATED = "ISOLATED_FIXTURE"
KIND_FITTED = "FITTED"
KINDS = (KIND_PROVEN, KIND_ISOLATED, KIND_FITTED)
_SOUND = (KIND_PROVEN, KIND_ISOLATED)


class CausticError(Exception):
    def __init__(self, message):
        super().__init__(f"CAUSTIC-REFUSE: {message}")
        self.code = "CAUSTIC-REFUSE"


def _storecost_form(n):
    import storecost as SC
    return SC.snapshot_bytes(n)


def _storecost_exec(n):
    import storecost as SC
    return len(SC.serialize(tuple((0, 0, 0, 0) for _ in range(n))))


def _warden_form(n):
    import opcost as OC
    if n < 1:
        return 0
    return OC.warden_edge_checks(tuple(tuple(0 for _ in range(n)) for _ in range(n)), 1)


def _warden_exec(n):
    """COUNTED, not restated. The first version returned `(n-1)*n + n*(n-1)` — the closed form
    written a second time, which proves that multiplication is deterministic and nothing else
    (L23: one computation restated is a definition). This walks the grid and counts the pairs."""
    return sum(1
               for y in range(n) for x in range(n)
               for (dx, dy) in ((1, 0), (0, 1))
               if 0 <= x + dx < n and 0 <= y + dy < n)


def _raster_form(lv):
    """AXIS IS SUBDIVISION LEVELS, not primitive count — because primitives here move in powers of
    four and a bisection over integers would ask the law about values it has no answer for. An
    axis a mechanism cannot step along is not an axis."""
    import sealframe as SF
    return SF.raster_ops(SF.subdivided_scene(lv, 256), 256, 256)["samples_model"]


def _raster_exec(lv):
    import sealframe as SF
    return SF.raster_ops(SF.subdivided_scene(lv, 256), 256, 256)["samples"]


def _divisions_form(n):
    import frontbench as FB
    return FB.sim_tick_divisions(n)


def _divisions_exec(n):
    """COUNTED by threading an instrumented divider through the real work, which is what
    `frontbench` itself does — the count is the run's, not the formula's."""
    import frontbench as FB
    seen = [0]

    def div(a, b):
        seen[0] += 1
        return FB._rdiv(a, b)
    FB.run_sim_tick(n, div)
    return seen[0]


def _confounded_form(n):
    import sealframe as SF
    return SF.raster_ops(SF.synthetic_scene(n, 128), 128, 128)["samples_model"]


def _confounded_exec(n):
    import sealframe as SF
    return SF.raster_ops(SF.synthetic_scene(n, 128), 128, 128)["samples"]


# (name, kind, axis, unit, VERIFIED DOMAIN sample points, closed form, execution, confound)
#
# THE DOMAIN IS PART OF THE LAW. A closed form is known where it was CHECKED AGAINST EXECUTION and
# nowhere else; answering a caustic outside that range would be an extrapolation of a formula, which
# is the move this whole arc keeps catching in other clothes. `caustic` bisects INSIDE the domain
# and REFUSES when the budget is not binding within it, naming the range rather than guessing past
# its edge.
LAWS = (
    ("storecost.snapshot_bytes", KIND_PROVEN, "actors", "bytes",
     (0, 1, 8, 64, 512, 4096), _storecost_form, _storecost_exec, ""),
    ("opcost.warden_edge_checks", KIND_PROVEN, "grid_side", "adjacency checks",
     (1, 2, 4, 8, 16, 32, 64), _warden_form, _warden_exec, ""),
    ("sealframe.raster_samples", KIND_ISOLATED, "subdivision_levels", "sample tests",
     (0, 1, 2, 3, 4), _raster_form, _raster_exec, ""),
    ("frontbench.sim_tick_divisions", KIND_PROVEN, "bipeds", "frozen divisions",
     (1, 5, 25, 100, 400), _divisions_form, _divisions_exec, ""),
    ("sealframe.synthetic_primitives", KIND_FITTED, "primitives", "sample tests",
     (4, 16, 64), _confounded_form, _confounded_exec,
     "`synthetic_scene` adds a fresh patch of frame per primitive, so this slope is linear in "
     "COVERAGE and is labelled linear in PRIMITIVES — the defect that paid for this module"),
)


def domain(name):
    """The range over which the closed form is CHECKED against execution this run."""
    xs = law(name)[4]
    return (xs[0], xs[-1])


def law(name):
    for entry in LAWS:
        if entry[0] == name:
            return entry
    raise CausticError(f"no such law: {name!r}")


def model_equals_execution(name):
    """THE AXIS-ISOLATION CHECK, run rather than quoted. The closed form must equal the execution
    at EVERY sampled axis value — which is what makes the formula a description of the work and
    not a description of one fixture."""
    _n, _k, _a, _u, xs, form, execute, _c = law(name)
    return all(form(x) == execute(x) for x in xs)


def is_monotone(name):
    """Non-decreasing over the sampled axis — the only property `caustic` actually needs, since a
    non-monotone law has no single crossing to name."""
    _n, _k, _a, _u, xs, form, _e, _c = law(name)
    ys = [form(x) for x in xs]
    return all(ys[i + 1] >= ys[i] for i in range(len(ys) - 1)) and ys[-1] > ys[0]


def is_affine(name):
    """Second differences vanish. REPORTED, NOT REQUIRED — and that demotion is a finding.

    The first version of `caustic` divided by a single slope and therefore demanded affineness,
    which REFUSED THREE OF THE FOUR REGISTERED LAWS on its first run: `warden_edge_checks` is
    quadratic in grid side, and `raster_samples` is sublinear in primitives because bounding-box
    slack grows slower than the count. Half the registered laws are affine and half are not.

    THE CLAIM THIS DOCSTRING FIRST MADE WAS AN OVERCLAIM AND IS RETRACTED. It said the finding
    "makes every `headroom x N` reading elsewhere suspect". The repository was then SEARCHED for
    such readings and there is essentially ONE — `bench_protocol` §4's frozen-division bridge,
    echoed in `fpclip.count_pose_ops`'s docstring. `renderbound`'s "thirty-two bits of headroom"
    is a magnitude bound and is already a cautionary tale rather than an instance; `fpquat`'s "~2x
    headroom" is slack on an error bound. One instance is not every reading, and the difference
    between them is the difference between a survey and a flourish."""
    _n, _k, _a, _u, xs, form, _e, _c = law(name)
    if len(xs) < 3:
        return False
    ys = [form(x) for x in xs]
    slopes = [(ys[i + 1] - ys[i]) * 1.0 / (xs[i + 1] - xs[i]) for i in range(len(xs) - 1)]
    return all(abs(s - slopes[0]) < 1e-9 for s in slopes)


def slope(name):
    _n, _k, _a, _u, xs, form, _e, _c = law(name)
    return (form(xs[-1]) - form(xs[0])) * 1.0 / (xs[-1] - xs[0])


def caustic(name, budget):
    """THE SCALE AT WHICH `budget` IS SPENT, in the law's own axis. Exact arithmetic over a
    checked closed form — never an extrapolation of a timing, and never a fitted slope."""
    entry = law(name)
    kind, confound = entry[1], entry[7]
    if kind == KIND_FITTED:
        raise CausticError(
            f"{name} is FITTED and cannot carry a caustic: {confound}. A caustic from a slope "
            f"whose axis moves with something else is not a bound, it is a coincidence with units")
    if not model_equals_execution(name):
        raise CausticError(f"{name}: the closed form does not equal the execution it models")
    if not is_monotone(name):
        raise CausticError(f"{name}: not monotone over its sampled range — no single crossing")
    form = entry[5]
    d0, d1 = domain(name)
    if form(d0) > budget:
        raise CausticError(
            f"{name}: the budget is already spent at the bottom of the verified domain "
            f"({d0}) — there is no scale that fits")
    if form(d1) <= budget:
        raise CausticError(
            f"{name}: the budget is NOT BINDING within the verified domain [{d0}, {d1}] — an "
            f"answer here would extrapolate a closed form past where it was checked against "
            f"execution, which is the move this module exists to refuse. Widen the domain")
    lo, hi = d0, d1                                        # integer bisection INSIDE the domain
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if form(mid) <= budget:
            lo = mid
        else:
            hi = mid
    return lo


def every_kind_is_populated():
    """L61: a classification nothing falls foul of carries no information, and a REFUSING class
    with no members is a checker that has never rejected anything."""
    have = {k for (_n, k, *_r) in LAWS}
    return have == set(KINDS)


def the_refusal_is_selective():
    """The refusal must fire on the confounded law and NOT on the sound ones — a refuser that
    refuses everything is as useless as one that refuses nothing."""
    refused, allowed = [], []
    for (name, kind, *_r) in LAWS:
        try:
            caustic(name, BUDGETS[name])
            allowed.append(name)
        except CausticError:
            refused.append(name)
    return (tuple(refused) == tuple(n for (n, k, *_r) in LAWS if k == KIND_FITTED)
            and tuple(allowed) == tuple(n for (n, k, *_r) in LAWS if k in _SOUND))


def caustic_digest():
    """URDRCAU1 canon over the registered laws and their caustics at a pinned budget."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for (name, kind, axis, unit, xs, form, _e, _c) in LAWS:
        hh.update(f"|{name}|{kind}|{axis}|{unit}|{xs}|{form(xs[0])}|{form(xs[-1])}".encode())
        hh.update(f"|aff:{is_affine(name)}|mono:{is_monotone(name)}".encode())
        if kind in _SOUND:
            hh.update(f"|c:{caustic(name, BUDGETS[name])}".encode())
    return hh.hexdigest()


BUDGETS = {"storecost.snapshot_bytes": 100000, "opcost.warden_edge_checks": 5000,
           "sealframe.raster_samples": 39000, "sealframe.synthetic_primitives": 39000,
           "frontbench.sim_tick_divisions": 13200}


def report(budgets=None):
    """The panel — every law side by side, refusals included. Never one number (`panel != scalar`)."""
    b = budgets or BUDGETS
    out = []
    for (name, kind, axis, unit, _xs, _f, _e, _c) in LAWS:
        try:
            out.append((name, kind, axis, unit, caustic(name, b[name]), ""))
        except CausticError as exc:
            out.append((name, kind, axis, unit, None, exc.args[0]))
    return tuple(out)


if __name__ == "__main__":
    print("CAUSTICS — the scale at which each pinned law spends its budget")
    for (name, kind, axis, unit, c, why) in report():
        if c is None:
            print(f"  {name:34s} {kind:19s} REFUSED")
            print(f"      {why}")
        else:
            print(f"  {name:34s} {kind:19s} dies at {c} {axis} ({unit}); "
                  f"affine={is_affine(name)} domain={domain(name)}")
    print(f"  digest {caustic_digest()}")
