# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""prediction_residuals — Rung 2: the ERROR SURFACE, and the joint-vs-batch granularity test.

FROZEN AS THE SUCCESSOR at checkpoint 9 ("Rung 2 -- the ERROR SURFACE"), and built here to that plan
rather than improvised. Checkpoint 10 then sharpened WHY it matters: batch-level G is nearly
unpredictable (leave-one-batch-out, the history model beat the null by ~2% and the census model lost
to it outright). Two readings are possible and they demand opposite architectures:

    (a) the engine's errors are NOISE -- nothing to synthesize a challenger from, and the whole
        theory-algebra program is unearned; or
    (b) AGGREGATION DESTROYED THE SIGNAL -- prediction happens at the JOINT, and the checkpoint is a
        compression that averages it away.

Reading (b) is the reviewer's hypothesis and this rung's decisive question. It is decidable with the
corpus already earned, so it is decided here rather than assumed in either direction.

THE ERROR SURFACE. Per scoring joint: the frozen vector, the observed class, both Brier losses, the
per-joint gain G_j = BS_null - BS_inc, the leading-class hit, the FIRST-TO-SECOND MARGIN, the class
count, and a mechanical error TYPE. The types are assigned by rule, never by judgement:

    CLEAN      -- leading class correct.
    RANKING    -- the observed class was named and carried non-trivial mass, but was not the argmax.
    SUPPORT    -- the observed class was named but carried near-zero mass (<= SUPPORT_FLOOR).
    PARTITION  -- the observed class was NOT in the frozen partition (fell to the catch-all).

THE GRANULARITY TEST, preregistered small predictors of "will the leading class MISS?" -- the exact
weakness batch 8 exposed. Each is at most one parameter, the NULL is seated from the start (L62), and
all are scored LEAVE-ONE-JOINT-OUT so none is fitted on the joint it predicts:

    null        -- the historical miss rate (no covariate).
    margin      -- the first-minus-second credence gap. The standing hypothesis is "low margin =>
                   higher miss probability", and it carries GENUINE FAILURE RISK: P30 missed at a
                   margin of 18 (C-INV 40 vs C-EQ 22), which is not especially close.
    nclass      -- the number of classes in the frozen partition.
    topmass     -- the probability assigned to the leading class.

Scored by Brier on the binary miss event, so a predictor that is confidently wrong is punished rather
than merely counted.

GRADE. MEASURED: the residual table, the error-type census, the leave-one-joint-out scores,
determinism (stdlib-only, exact integer/rational arithmetic, exhaustive, rerun byte-identical).
DECLARED: the error-type rule and the SUPPORT_FLOOR, both fixed here before scoring. does_not_show:
SIGNIFICANCE -- n = 22 joints, retrospective, descriptive only (L20); that a predictor which wins here
would survive prospectively (that is the forward test, not this); anything about Urdr's correctness --
this measures the DISCOVERY ENGINE.

    PYTHONHASHSEED=0 python3 exe_epistemics/prediction_residuals.py
"""
import os
import sys
from fractions import Fraction

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import multinull as MN                                   # the checkpoint-9 corpus and frozen scorer

SCALE = MN.SCALE
#: DECLARED before scoring: mass at or below this is "near-zero support" (2% of the vector).
SUPPORT_FLOOR = 200


def surface():
    """The canonical residual table -- one row per scoring joint, every field derived."""
    out = []
    for r in MN.run():
        p, classes, y = r["p"], r["classes"], r["y"]
        ranked = sorted(classes, key=lambda c: (-p.get(c, 0), c))
        top, second = ranked[0], (ranked[1] if len(ranked) > 1 else ranked[0])
        margin = p.get(top, 0) - p.get(second, 0)
        hit = (r["lead_p"] == y)
        if r["mapped"]:
            etype = "PARTITION"
        elif hit:
            etype = "CLEAN"
        elif p.get(y, 0) <= SUPPORT_FLOOR:
            etype = "SUPPORT"
        else:
            etype = "RANKING"
        out.append({"pid": r["pid"], "y": y, "lead": r["lead_p"], "hit": hit, "type": etype,
                    "margin": margin, "topmass": p.get(top, 0), "p_y": p.get(y, 0),
                    "nclass": len(classes), "g": r["bs_q"] - r["bs_p"],
                    "bs_p": r["bs_p"], "bs_q": r["bs_q"]})
    return out


def type_census(rows=None):
    rows = surface() if rows is None else rows
    cen = {}
    for r in rows:
        cen[r["type"]] = cen.get(r["type"], 0) + 1
    return dict(sorted(cen.items()))


# ---- the granularity test: leave-one-joint-out prediction of a MISS -------------------------------
def _mean(xs):
    return Fraction(sum(xs), len(xs)) if xs else Fraction(0)


def _predict(train, x, feature):
    """One-parameter least-squares fit of P(miss) on `feature`, clamped to [0,1]. With no feature the
    prediction is the training miss rate (the seated null)."""
    ys = [Fraction(1 if t["hit"] is False else 0) for t in train]
    ybar = _mean(ys)
    if feature is None:
        return ybar
    xs = [Fraction(t[feature]) for t in train]
    xbar = _mean(xs)
    sxx = sum((v - xbar) ** 2 for v in xs)
    if sxx == 0:
        return ybar
    b = sum((v - xbar) * (yy - ybar) for v, yy in zip(xs, ys)) / sxx
    pred = ybar + b * (Fraction(x[feature]) - xbar)
    return min(Fraction(1), max(Fraction(0), pred))


def lojo(rows=None):
    """Leave-one-joint-out Brier on the binary MISS event, scaled to integer /10000 for reporting."""
    rows = surface() if rows is None else rows
    out = {}
    for name, feat in (("null", None), ("margin", "margin"), ("nclass", "nclass"),
                       ("topmass", "topmass")):
        errs = []
        for i, r in enumerate(rows):
            train = rows[:i] + rows[i + 1:]
            pred = _predict(train, r, feat)
            actual = Fraction(0 if r["hit"] else 1)
            errs.append((pred - actual) ** 2)
        out[name] = int(_mean(errs) * 10000)
    return out


def joint_level_beats_null(res=None):
    """THE DECISIVE QUESTION. Does ANY preregistered joint-level covariate beat the seated null
    out-of-sample? If False, the errors are noise at this granularity too, and reading (b) --
    'aggregation destroyed the signal' -- is NOT supported by this corpus.

    THE WINNER IS NAMED BY SCORE. Until 2026-08-05 this line read `best = min(k for k in res if k
    != "null")`, which is the lexicographic minimum of the key STRINGS, not the argmin of the
    scores -- it returned "margin" for any corpus whatever. The defect was VACUOUS while every
    covariate lost to the null: nothing consulted `best` when `beats` was False, so a wrong answer
    had no observable consequence. It became load-bearing at the exact run that first flipped
    `beats` to True (n=33: topmass 2433 beats the null's 2539 by 106) and reported the winner as
    `margin`, which LOSES by 112 -- naming as victor the one covariate whose standing hypothesis
    this corpus had already embarrassed. A defect that is only observable once the result changes
    is not caught by re-running a green instrument; `vacuous != correct`.

    Ties break lexicographically so the answer is deterministic (`PYTHONHASHSEED=0` is not enough
    when the tiebreak is unspecified)."""
    res = lojo() if res is None else res
    others = [k for k in res if k != "null"]
    best = min(others, key=lambda k: (res[k], k))
    return res[best] < res["null"], best


def winner_is_named_by_score(res=None):
    """RED-FIRST: the falsifier the naming line never had. Plants a synthetic result whose
    alphabetically-FIRST covariate is the WORST, and demands the reported winner be the
    lowest-scoring one. The pre-2026-08-05 implementation returns "aaa" here and fails."""
    plant = {"null": 5000, "aaa": 9999, "zzz": 1000}
    beats, best = joint_level_beats_null(plant)
    caught = (best == "zzz" and beats is True)
    tie = joint_level_beats_null({"null": 5000, "bbb": 1000, "aaa": 1000})[1] == "aaa"
    live = joint_level_beats_null(res)
    consistent = live[0] == (min(res[k] for k in res if k != "null") < res["null"]) \
        if res else True
    return caught and tie and consistent


def non_vacuous(rows=None):
    """L61: both outcomes must occur, or 'the null wins' is a one-class artifact."""
    rows = surface() if rows is None else rows
    return any(r["hit"] for r in rows) and any(not r["hit"] for r in rows)


def main():
    rows = surface()
    print("%-5s %-9s %-9s %-10s %8s %8s %8s %14s"
          % ("P", "observed", "lead", "type", "margin", "topmass", "p_y", "G_j"))
    for r in rows:
        print("%-5s %-9s %-9s %-10s %8d %8d %8d %14d"
              % (r["pid"], r["y"], r["lead"], r["type"], r["margin"], r["topmass"], r["p_y"], r["g"]))
    print()
    print("error-type census: %s" % type_census(rows))
    print("non-vacuous (both hits and misses occur): %s" % non_vacuous(rows))
    print()
    res = lojo(rows)
    print("LEAVE-ONE-JOINT-OUT Brier on the MISS event (x10000, lower is better; n=%d):" % len(rows))
    for k in ("null", "margin", "nclass", "topmass"):
        print("   %-9s %6d%s" % (k, res[k], "   <- seated null" if k == "null" else ""))
    beats, best = joint_level_beats_null(res)
    print()
    print("ANY joint-level covariate beats the null out-of-sample: %s  (best non-null: %s, %d vs "
          "null %d)" % (beats, best, res[best], res["null"]))
    print("winner named by SCORE, not by name (red-first plant caught): %s"
          % winner_is_named_by_score(res))
    if beats:
        print("L63 STATUS: `%s` has ONE out-of-sample win on record. That is NOT standing --"
              % best)
        print("  L63 requires REPEATED preregistered improvement over the seated incumbent, so")
        print("  `%s` stays EXPERIMENTAL: it may be computed and reported, and may NOT be" % best)
        print("  reasoned from. The corpus that produced this win is also retrospective (L20).")
    misses = [r["pid"] for r in rows if not r["hit"]]
    print("misses: %s" % misses)
    hit_m = _mean([r["margin"] for r in rows if r["hit"]])
    mis_m = _mean([r["margin"] for r in rows if not r["hit"]])
    print("mean margin  hits %d   misses %d   (the standing 'low margin => miss' hypothesis)"
          % (int(hit_m), int(mis_m)))
    print()
    print("NO SIGNIFICANCE CLAIMED: n = %d joints, retrospective. Descriptive only (L20)." % len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
