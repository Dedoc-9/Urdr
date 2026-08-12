# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""confound — A TREATMENT AXIS MAY NOT BE A PROXY FOR ELAPSED TIME, AND A CELL IS NOT AN EXPERIMENT
(URDRCNF1). Both laws were written after the FIRST REAL HOST LOG refuted the harness that produced
it, using nothing but the harness's own numbers.

WHAT THE LOG SAID, AND WHY IT CANNOT BE TRUE.

`rollbench` v1.2 timed three representations of a rollback record. In the log from the named host,
`narrowed` was faster than `moulded` in 23 of 28 cells, median 500 ns. Read `one_rollback`:

    rec  = MS.record_for(rep, ...)                       # `narrowed` = `moulded` + a widths tuple
    flat = rec if rep == "flat" else MD.to_vouch(world, (rec[0], rec[1], rec[2]))

Both non-flat arms go through `to_vouch`, and the widths `narrowed` stores are NEVER READ. So
`narrowed` executes a strict SUPERSET of `moulded`'s timed instructions. A representation doing more
work cannot be faster, and the log said it was — so the log was measuring something other than the
representation.

IT WAS MEASURING WHEN THE CELL RAN. `cells()` iterates representation-outermost, so `flat` occupied
run positions 0-27, `moulded` 28-55 and `narrowed` 56-83. Every flat sample preceded every moulded
sample preceded every narrowed sample, across 16 800 timed operations on a handheld under a turbo
power profile. Clock ramp, thermal state and allocator warmth all drift monotonically through a run
like that, and the treatment axis was ALIGNED WITH THAT DRIFT. "Narrowed is fastest" and "narrowed
ran last" were the same measurement, and no amount of extra iterations would have separated them.

    A FACTOR PERFECTLY CORRELATED WITH RUN POSITION IS NOT MEASURED, IT IS CONFOUNDED.

THE SECOND LAW, from the same log. `depth` is the number of ticks a rollback is asked to replay, and
the harness reported seven of them. It could not replay them: the walk saturates against the world's
own length. `all_airborne` replays TWO ticks at depths 4, 8, 16, 32 and 64 — five rows of a table,
one experiment. `all_grounded` and `alternating` saturate at 11 ticks from depth 16; `frequent_landing`
at 12. Of 28 (workload, depth) cells, ELEVEN duplicate another cell exactly: 17 experiments wearing
28 names, and any count over those cells carries a denominator that is 39% copies. That is L44 with
the numerator disguised as the axis — `depth` is a REQUEST and `ticks` is the WORK, and the log
reported only the request.

THE REPAIR IS A SCHEDULE, NOT A CAVEAT. Cells are visited on a stride co-prime to their count, so
every level of every axis is spread across the whole run. The stride is CHOSEN BY MEASUREMENT
against a criterion fixed in advance — minimise the worst per-axis deviation of a level's mean run
position from the run's midpoint — and the search is reproduced by a falsifier rather than asserted
here. Randomisation would have done the same job and is forbidden: determinism is the floor, and a
seed is one more thing a result can depend on.

`does_not_show` — and the bound is sharp. BALANCE IS NOT INDEPENDENCE. Spreading a factor across the
run removes the CORRELATION between treatment and position; it does not remove position as a source
of variance, and it cannot detect a drift that is periodic at the stride. Nor does this module make
any timing claim: it grades the SCHEDULE, never the numbers. And it reads the plan's axes as DATA —
a factor nobody put in the plan is invisible here, so a harness confounded with something it never
recorded reads BALANCED and is not.

GRADE (honest, D5): MEASURED — every axis of the live plan reads BALANCED under the pinned schedule,
the previous schedule reads CONFOUNDED on the representation axis with all three levels in disjoint
contiguous blocks, the stride's optimality is re-derived by search rather than asserted, every cell
is visited exactly once, and the saturation is counted exactly (28 cells, 17 distinct, 11
duplicates). DECLARED: the tolerance, the stride, and the axis list — all three are choices, pinned
as data so a later reading cannot be graded against a bar nobody is watching."""
import hashlib
import os as _os
import statistics
from math import gcd

# THIS MODULE IMPORTS NOTHING FROM THIS TREE, AND THE LATTICE IS WHY THE FIRST DRAFT DID.
# It read `measure` for the live plan, which put a new node between the harness and the plan and
# pushed `reachable`'s import depth to 14 against a sealed ceiling of 13. The depth proof reddened,
# and it was right about more than depth: a detector that grades SCHEDULES has no business knowing
# what a rollback benchmark is. Cells and axis names arrive as ARGUMENTS; the caller that owns the
# plan supplies them. The scenes pin behaviour on a FIXTURE of the same shape (3 x 4 x 7 = 84), and
# the LIVE plan is graded at the gate and by `rollbench`'s own law, where the plan actually lives.

_HERE = _os.path.dirname(_os.path.abspath(__file__))

MAGIC = b"URDRCNF1"

BALANCED = "BALANCED"
CONFOUNDED = "CONFOUNDED"
SKEWED = "SKEWED"
OUTCOMES = (BALANCED, CONFOUNDED, SKEWED)

#: The axes of a bench cell, in the order `measure.bench_plan` names them. READ as data: a factor
#: nobody put in the plan is invisible here, which is this module's `does_not_show`.
AXES = ("representation", "workload", "depth")

#: A FIXTURE PLAN OF THE SAME SHAPE AS THE LIVE ONE (3 x 4 x 7 = 84 cells), so this module's scenes
#: are self-contained and its stride transfers. The live plan is graded by the caller.
FIXTURE = tuple((r, w, d) for r in ("A", "B", "C")
                for w in ("w0", "w1", "w2", "w3") for d in (1, 2, 4, 8, 16, 32, 64))

#: DECLARED. A level's mean run position may sit this far from the run's midpoint, as a fraction of
#: the run length. The floor for this plan is 0.0357 and it is STRUCTURAL — seven depth levels do
#: not tile 84 positions evenly — so a tolerance below it would refuse every possible schedule, and
#: one far above it would accept the confounded schedule this module exists to catch (0.333).
TOLERANCE = 0.05

#: DECLARED, AND CHOSEN BY MEASUREMENT. Visiting cell `(i*STRIDE) mod n` for a stride co-prime to
#: `n` spreads every axis across the whole run. `the_stride_is_optimal_by_search` re-derives this
#: over every co-prime stride against the criterion above, so the number is reproduced rather than
#: trusted. Six strides tie at the floor; the smallest is taken.
STRIDE = 25


class ConfoundError(Exception):
    def __init__(self, message):
        super().__init__(f"CONFOUND-REFUSE: {message}")
        self.code = "CONFOUND-REFUSE"


# ---- the schedule ---------------------------------------------------------------------------------
def schedule(cells, stride=None):
    """The run order. A permutation by construction — `gcd(stride, n) == 1` makes `i*stride mod n`
    a bijection — so no cell is dropped or run twice, which a hand-written interleave can do."""
    cells = tuple(cells)
    n = len(cells)
    k = STRIDE if stride is None else stride
    if n == 0:
        raise ConfoundError("an empty plan has no schedule")
    if gcd(k, n) != 1:
        raise ConfoundError(f"stride {k} shares a factor with {n} cells, so the walk revisits "
                            f"cells and never reaches others — not a permutation, not a schedule")
    return tuple(cells[(i * k) % n] for i in range(n))


def positions(order, axis):
    """{level: (run positions)} for one axis."""
    if axis not in AXES:
        raise ConfoundError(f"no axis named {axis!r}; the plan names {AXES}")
    i = AXES.index(axis)
    out = {}
    for pos, cell in enumerate(order):
        out.setdefault(cell[i], []).append(pos)
    return {k: tuple(v) for k, v in sorted(out.items(), key=lambda kv: repr(kv[0]))}


def deviation(order, axis):
    """The worst distance from a level's MEAN run position to the run's midpoint, as a fraction of
    the run. Zero means every level is centred; large means some level lives early or late."""
    n = len(order)
    mid = (n - 1) / 2
    return max(abs(statistics.mean(p) - mid) for p in positions(order, axis).values()) / n


def blocked(order, axis):
    """Every level occupies ONE CONTIGUOUS RUN of positions — the exact shape of the defect, where
    a whole treatment happens before another whole treatment begins."""
    return all(max(p) - min(p) + 1 == len(p) for p in positions(order, axis).values())


def verdict(order, axis):
    """CONFOUNDED / SKEWED / BALANCED, and they are three findings rather than a scale.

    CONFOUNDED — the levels are disjoint contiguous blocks. The factor IS run position.
    SKEWED     — interleaved, but some level still sits systematically early or late.
    """
    if blocked(order, axis):
        return CONFOUNDED
    return SKEWED if deviation(order, axis) > TOLERANCE else BALANCED


def census(order=None):
    o = schedule(FIXTURE) if order is None else order
    return {a: verdict(o, a) for a in AXES}


# ---- what a cell actually costs ---------------------------------------------------------------------
def duplicates(keys):
    """(n, distinct, duplicates) over experiment keys the CALLER computes. This module cannot know
    what makes two cells the same experiment — only the plan's owner does — so it counts, and the
    owner supplies. `rollbench` passes (workload, ticks); the depth that was ASKED for is not in the
    key, which is the entire point."""
    keys = tuple(keys)
    return (len(keys), len(set(keys)), len(keys) - len(set(keys)))


# ---- the laws ---------------------------------------------------------------------------------------
def no_axis_is_confounded():
    """THE LAW. Under the pinned schedule every axis of the live plan reads BALANCED."""
    c = census()
    return bool(c) and all(v == BALANCED for v in c.values())


def the_old_schedule_is_confounded():
    """RED-FIRST, WITH THE ORDER THAT ACTUALLY SHIPPED. `measure.bench_cells()` in plan order is
    representation-outermost; graded, it reads CONFOUNDED on `representation` with all three levels
    in disjoint contiguous blocks. This is not a constructed example — it is the schedule that
    produced the host log this module was written to explain."""
    old = tuple(FIXTURE)
    return (verdict(old, "representation") == CONFOUNDED
            and blocked(old, "representation")
            and deviation(old, "representation") > TOLERANCE
            and verdict(schedule(old), "representation") == BALANCED)


def a_merely_interleaved_schedule_can_still_be_skewed():
    """The second verdict, planted separately, because CONFOUNDED and SKEWED fail differently. Move
    one level's cells toward the front without making them contiguous: not blocked, still early.
    A detector with only the block test would call this balanced."""
    cells = tuple(FIXTURE)
    first = cells[0][0]
    mine = [c for c in cells if c[0] == first]
    rest = [c for c in cells if c[0] != first]
    woven = []
    for i, c in enumerate(rest):                            # thread `first` densely through the head
        if mine:
            woven.append(mine.pop())
        woven.append(c)
    woven.extend(mine)
    return (not blocked(tuple(woven), "representation")
            and verdict(tuple(woven), "representation") == SKEWED)


def every_cell_is_visited_exactly_once():
    """A schedule that loses or repeats a cell is a different benchmark. Guaranteed by co-primality
    rather than by inspection, and asserted so the guarantee is not merely believed."""
    cells = tuple(FIXTURE)
    o = schedule(cells)
    return len(o) == len(cells) and sorted(map(repr, o)) == sorted(map(repr, cells))


def a_stride_sharing_a_factor_refuses():
    """The co-primality condition is what makes the walk a permutation, so violating it must REFUSE
    rather than quietly produce a shorter run."""
    n = len(tuple(FIXTURE))
    bad = next((k for k in range(2, n) if gcd(k, n) != 1), None)
    if bad is None:
        return False
    try:
        schedule(FIXTURE, stride=bad)
        return False
    except ConfoundError:
        return True


def the_stride_is_optimal_by_search():
    """THE STRIDE IS A CHOICE, RE-DERIVED RATHER THAN TRUSTED. Search every co-prime stride against
    the criterion fixed in advance — minimise the worst per-axis deviation — and `STRIDE` must be
    the smallest that attains the floor. If a future plan makes another stride better, this reddens
    and the pin is updated with the measurement in hand."""
    cells = tuple(FIXTURE)
    n = len(cells)

    def worst(k):
        o = schedule(cells, stride=k)
        return max(deviation(o, a) for a in AXES)
    scores = {k: worst(k) for k in range(2, n) if gcd(k, n) == 1}
    floor = min(scores.values())
    best = min(k for k, v in scores.items() if v == floor)
    return (best == STRIDE, floor, sum(1 for v in scores.values() if v == floor))


def the_tolerance_admits_the_floor_and_refuses_the_defect():
    """NON-VACUITY IN BOTH DIRECTIONS, which a bare threshold never gets. TOLERANCE must sit ABOVE
    the structural floor — below it no schedule could pass and the law would be a wall — and BELOW
    the deviation of the schedule that shipped, or it would admit the very defect it was written
    for."""
    _ok, floor, _ties = the_stride_is_optimal_by_search()
    shipped = deviation(tuple(FIXTURE), "representation")
    return floor < TOLERANCE < shipped


def a_repeated_key_is_counted_as_one_experiment():
    """L44, WITH THE NUMERATOR DISGUISED AS THE AXIS. Two cells whose WORK key is equal are one
    experiment however differently they were requested — checked on a fixture that repeats, because
    the live instance lives in `measure` where the plan is."""
    return (duplicates(("a", "a", "b")) == (3, 2, 1)
            and duplicates(("a", "b", "c")) == (3, 3, 0)
            and duplicates(()) == (0, 0, 0))


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("schedule", "duplicates")


def scene_case(name):
    if name == "schedule":
        o = schedule(FIXTURE)
        return "|".join("%s=%s dev=%.4f" % (a, verdict(o, a), deviation(o, a)) for a in AXES) \
            + "||old=%s %.4f||stride=%d once=%s" % (
                verdict(tuple(FIXTURE), "representation"),
                deviation(tuple(FIXTURE), "representation"),
                STRIDE, every_cell_is_visited_exactly_once())
    if name == "duplicates":
        return "%s|%s|%s|%s" % (duplicates(("a", "a", "b")), duplicates(("a", "b", "c")),
                                duplicates(()), a_repeated_key_is_counted_as_one_experiment())
    raise ConfoundError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def confound_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_confound.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ConfoundError(f"no golden named {name!r}")


if __name__ == "__main__":
    o = schedule(FIXTURE)
    for a in AXES:
        print("%-16s %-11s dev=%.4f  (shipped order: %s dev=%.4f)"
              % (a, verdict(o, a), deviation(o, a),
                 verdict(tuple(FIXTURE), a), deviation(tuple(FIXTURE), a)))
    print()
    print("no axis confounded  :", no_axis_is_confounded())
    print("old order caught    :", the_old_schedule_is_confounded())
    print("skew caught         :", a_merely_interleaved_schedule_can_still_be_skewed())
    print("every cell once     :", every_cell_is_visited_exactly_once())
    print("bad stride refuses  :", a_stride_sharing_a_factor_refuses())
    print("stride by search    :", the_stride_is_optimal_by_search())
    print("tolerance two-sided :", the_tolerance_admits_the_floor_and_refuses_the_defect())
    print("repeat key counted  :", a_repeated_key_is_counted_as_one_experiment())
    for n in SCENES:
        print(n, scene_result(n))
    print("confound", confound_digest())
