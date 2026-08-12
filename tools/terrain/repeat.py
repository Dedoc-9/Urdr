# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""repeat — VARIANCE HAS LEVELS, AND TWO HUNDRED ITERATIONS IN ONE PROCESS SAMPLE EXACTLY ONE OF
THEM (URDRRPT1). The hole `confound` could not see, because balancing a schedule inside one
execution does nothing about the execution itself.

`rollbench` times each cell 200 times and reports p50, p95 and p99. Every one of those quantiles is
a WITHIN-EXECUTION quantile: 200 samples of iteration-level variation, and exactly ONE sample of
everything that is fixed for the life of a process — the hash seed, the address-space layout, where
the allocator happened to start, which core the scheduler chose. Kalibera and Jones state the
consequence plainly, and it is not a matter of degree:

    MORE ITERATIONS INSIDE ONE EXECUTION CANNOT REDUCE EXECUTION-LEVEL VARIANCE.

Not "reduce it slowly". Cannot. The quantity is not being sampled at all, so `n` grows and the
confidence interval that matters does not move. `pyperf` spawns separate worker PROCESSES for
exactly this reason, and says so: address-space randomisation and hash randomisation vary per
process and are invisible from inside one.

THE LAW, and it is a refusal rather than a caution:

    A DIFFERENCE SMALLER THAN THE BETWEEN-EXECUTION SPREAD IS NOT A DIFFERENCE. WITH ONE
    EXECUTION, THE BETWEEN-EXECUTION SPREAD IS UNKNOWN AND NO DIFFERENCE CAN BE CLAIMED AT ALL.

Three verdicts, because they are three findings and fusing any two of them loses the one that
matters. SEPARATED: the gap between the two medians exceeds the spread of per-execution medians.
INDISTINGUISHABLE: it does not, and reporting it as a result would be reporting the noise floor.
UNDETERMINED: fewer than two executions, so the spread is not merely large — IT DOES NOT EXIST, and
a detector returning INDISTINGUISHABLE here would be claiming to have looked.

WHY UNDETERMINED IS NOT A POLITE INDISTINGUISHABLE. Every timing this repository has ever produced
is UNDETERMINED under this law, including the two admissible host logs. That is the finding, and it
is uncomfortable in the right way: the numbers are real, the schedule is now balanced, and the
question of whether any gap survives a second process has never been asked.

ARITHMETIC IS INTEGER AND EXACT. Medians take the LOWER of the two middle values on an even count,
declared here rather than left to a float, because a benchmark law that itself introduces a
rounding choice has no business grading anyone. Nothing here divides.

`does_not_show` — the bound, and it is not small. THE SPREAD OF A FEW EXECUTIONS IS NOT A
CONFIDENCE INTERVAL. This reports whether a gap clears the observed between-execution range; it
computes no distribution, assumes none, and offers no p-value, so with three executions it is a
weak instrument that can only be more conservative than the truth, never less. And it grades only
what it is HANDED: a factor that is constant across every execution — the machine, the interpreter
build, the working directory — is invisible here exactly as run position was invisible before
`confound`, and Mytkowicz's result is that such factors are worth 2-8% on their own.

GRADE (honest, D5): MEASURED — a gap below the between-execution spread reads INDISTINGUISHABLE and
one above it reads SEPARATED, each planted separately; a single execution reads UNDETERMINED
whatever the gap, and MULTIPLYING THE ITERATION COUNT BY A HUNDRED DOES NOT CHANGE THAT, which is
the paper's claim reproduced as a falsifier rather than cited; the arithmetic is integer and its
tie-breaking is pinned. DECLARED: that the between-execution spread is the RANGE of per-execution
medians — a choice, and the most conservative one available without assuming a distribution."""
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))

MAGIC = b"URDRRPT1"

SEPARATED = "SEPARATED"
INDISTINGUISHABLE = "INDISTINGUISHABLE"
UNDETERMINED = "UNDETERMINED"
OUTCOMES = (SEPARATED, INDISTINGUISHABLE, UNDETERMINED)

#: The minimum number of independent EXECUTIONS before a between-execution spread exists at all.
#: Two is not a good number; it is the smallest number that is not zero, and the module says so.
MIN_EXECUTIONS = 2


class RepeatError(Exception):
    def __init__(self, message):
        super().__init__(f"REPEAT-REFUSE: {message}")
        self.code = "REPEAT-REFUSE"


# ---- exact integer statistics ----------------------------------------------------------------------
def median(values):
    """LOWER median on an even count, DECLARED rather than averaged. A law that graded benchmarks
    while introducing its own rounding choice would be an odd thing to trust, and nothing here
    divides, so no result of this module can depend on float behaviour."""
    v = sorted(values)
    if not v:
        raise RepeatError("the median of no samples is not zero, it is undefined")
    return v[(len(v) - 1) // 2]


def per_execution_medians(by_run):
    """{run: median of that run's samples}, sorted by run so the output is order-independent."""
    if not isinstance(by_run, dict) or not by_run:
        raise RepeatError("no executions were handed in — an empty grouping is not one execution")
    for r, s in by_run.items():
        if not s:
            raise RepeatError(f"execution {r!r} carries no samples")
    return {r: median(by_run[r]) for r in sorted(by_run)}


def between_spread(by_run):
    """THE RANGE of the per-execution medians. DECLARED: the range rather than a standard deviation,
    because a standard deviation over three executions asserts a distribution nobody measured, and
    the range is the most conservative statement the data supports."""
    m = per_execution_medians(by_run)
    if len(m) < MIN_EXECUTIONS:
        raise RepeatError(f"{len(m)} execution(s): the between-execution spread does not EXIST "
                          f"below {MIN_EXECUTIONS}, which is a different finding from it being "
                          f"small, and treating them alike is the whole defect this module names")
    vals = list(m.values())
    return max(vals) - min(vals)


def within_spread(by_run):
    """The median per-execution internal range — reported BESIDE the between-execution spread and
    never combined with it, because the two answer different questions and a single pooled number
    would let the one that is cheap to shrink hide the one that is not."""
    return median([max(s) - min(s) for s in by_run.values()])


# ---- the verdict ---------------------------------------------------------------------------------
def verdict(a_by_run, b_by_run):
    """SEPARATED / INDISTINGUISHABLE / UNDETERMINED for two arms measured across executions."""
    runs = set(a_by_run) & set(b_by_run)
    if len(runs) < MIN_EXECUTIONS:
        return UNDETERMINED
    a = {r: a_by_run[r] for r in runs}
    b = {r: b_by_run[r] for r in runs}
    gap = abs(median(list(per_execution_medians(a).values()))
              - median(list(per_execution_medians(b).values())))
    floor = max(between_spread(a), between_spread(b))
    return SEPARATED if gap > floor else INDISTINGUISHABLE


def report(a_by_run, b_by_run):
    """The verdict WITH its terms, so a reader never receives the word alone."""
    v = verdict(a_by_run, b_by_run)
    if v == UNDETERMINED:
        return {"verdict": v, "executions": len(set(a_by_run) & set(b_by_run)),
                "gap": None, "between": None, "within": None}
    runs = set(a_by_run) & set(b_by_run)
    a = {r: a_by_run[r] for r in runs}
    b = {r: b_by_run[r] for r in runs}
    return {"verdict": v, "executions": len(runs),
            "gap": abs(median(list(per_execution_medians(a).values()))
                       - median(list(per_execution_medians(b).values()))),
            "between": max(between_spread(a), between_spread(b)),
            "within": max(within_spread(a), within_spread(b))}


# ---- fixtures --------------------------------------------------------------------------------------
def _arm(base, run_offsets, jitter=(0, 1, 2, 3, 4)):
    """An arm with a per-execution offset and a fixed within-execution jitter. Deterministic, and
    it makes the two levels of variance separable by construction so a plant can move one alone."""
    return {i: [base + off + j for j in jitter] for i, off in enumerate(run_offsets)}


# ---- the laws ---------------------------------------------------------------------------------------
def one_execution_can_separate_nothing():
    """THE FINDING, AND IT INDICTS EVERY LOG THIS REPOSITORY HAS PRODUCED. With one execution the
    verdict is UNDETERMINED no matter how large the gap — a thousand nanoseconds apart or a
    million — because the quantity the comparison must clear has not been sampled once."""
    for gap in (1, 1000, 10 ** 6):
        if verdict(_arm(100, [0]), _arm(100 + gap, [0])) != UNDETERMINED:
            return False
    return True


def more_iterations_do_not_help():
    """KALIBERA AND JONES, REPRODUCED AS A FALSIFIER RATHER THAN CITED. Multiply the iteration count
    by a hundred inside the single execution and the verdict does not move, because iterations
    sample the wrong level. This is the claim that separates this module from 'collect more data'."""
    small = _arm(100, [0], jitter=tuple(range(5)))
    big = _arm(100, [0], jitter=tuple(range(500)))
    other_s = _arm(1100, [0], jitter=tuple(range(5)))
    other_b = _arm(1100, [0], jitter=tuple(range(500)))
    return (verdict(small, other_s) == UNDETERMINED
            and verdict(big, other_b) == UNDETERMINED
            and len(next(iter(big.values()))) == 100 * len(next(iter(small.values()))))


def an_effect_below_the_between_spread_is_indistinguishable():
    """PLANTED. Two arms 10 apart, with per-execution offsets spanning 100: the gap is real in the
    data and smaller than the floor, and reporting it would be reporting the noise."""
    a = _arm(1000, [0, 50, 100])
    b = _arm(1010, [0, 50, 100])
    return verdict(a, b) == INDISTINGUISHABLE


def an_effect_above_the_between_spread_separates():
    """THE OTHER HALF, or the law would be a wall that refuses every result. Same executions, a gap
    of 500 against a floor of 100."""
    a = _arm(1000, [0, 50, 100])
    b = _arm(1500, [0, 50, 100])
    return verdict(a, b) == SEPARATED


def the_two_levels_are_reported_apart():
    """`panel != scalar`, at the level that matters here: within-execution and between-execution
    spread are returned SEPARATELY and never pooled, because iterations shrink the first and cannot
    touch the second, and one number would let the cheap one hide the expensive one."""
    a = _arm(1000, [0, 50, 100], jitter=tuple(range(40)))
    b = _arm(1500, [0, 50, 100], jitter=tuple(range(40)))
    r = report(a, b)
    return (r["within"] is not None and r["between"] is not None
            and r["within"] != r["between"] and r["verdict"] == SEPARATED)


def the_arithmetic_is_integer_and_pinned():
    """No float can enter a verdict. The even-count tie-break is the LOWER middle value, declared
    and asserted, so a future reader cannot discover it from behaviour alone."""
    if median([1, 2, 3, 4]) != 2 or median([5]) != 5:
        return False
    r = report(_arm(1000, [0, 50, 100]), _arm(1500, [0, 50, 100]))
    return all(isinstance(r[k], int) for k in ("gap", "between", "within", "executions"))


def an_empty_or_ragged_input_refuses():
    """A grouping with no executions, or an execution with no samples, is refused rather than
    scored — an empty median is undefined and returning zero would make silence look like agreement."""
    caught = 0
    for bad in ({}, {0: []}, {0: [1], 1: []}):
        try:
            per_execution_medians(bad)
        except RepeatError:
            caught += 1
    return caught == 3


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("verdicts", "levels")


def scene_case(name):
    if name == "verdicts":
        return "one=%s|iters=%s|below=%s|above=%s|refuse=%s" % (
            one_execution_can_separate_nothing(), more_iterations_do_not_help(),
            an_effect_below_the_between_spread_is_indistinguishable(),
            an_effect_above_the_between_spread_separates(), an_empty_or_ragged_input_refuses())
    if name == "levels":
        r = report(_arm(1000, [0, 50, 100], jitter=tuple(range(40))),
                   _arm(1500, [0, 50, 100], jitter=tuple(range(40))))
        return "%s|apart=%s|int=%s|min=%d" % (
            sorted(r.items(), key=lambda kv: kv[0]), the_two_levels_are_reported_apart(),
            the_arithmetic_is_integer_and_pinned(), MIN_EXECUTIONS)
    raise RepeatError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def repeat_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_repeat.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RepeatError(f"no golden named {name!r}")


if __name__ == "__main__":
    print("one execution separates nothing :", one_execution_can_separate_nothing())
    print("more iterations do not help     :", more_iterations_do_not_help())
    print("below the floor                 :", an_effect_below_the_between_spread_is_indistinguishable())
    print("above the floor                 :", an_effect_above_the_between_spread_separates())
    print("levels reported apart           :", the_two_levels_are_reported_apart())
    print("integer and pinned              :", the_arithmetic_is_integer_and_pinned())
    print("empty/ragged refuses            :", an_empty_or_ragged_input_refuses())
    print()
    print("report:", report(_arm(1000, [0, 50, 100], jitter=tuple(range(40))),
                            _arm(1500, [0, 50, 100], jitter=tuple(range(40)))))
    for n in SCENES:
        print(n, scene_result(n))
    print("repeat", repeat_digest())
