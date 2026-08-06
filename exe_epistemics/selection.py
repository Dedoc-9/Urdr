# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""selection — the SELECTION FUNCTIONAL made explicit, and the winner made VERIFIABLE.

WHY THIS EXISTS, AND WHY IT NEEDS NO STANDING. Rung 9 found the line that answers L63's question --
WHICH diagnostic beat the seated incumbent -- returning the alphabetically smallest NAME instead of
the argmin of the SCORE. The repair was one line. The reason the defect could exist is not.

Between `tournament` and `winner` there was always a functional

    candidates x objective -> winner

and it was never an object. It lived inline, as `min(...)`, so it could be silently replaced by a
DIFFERENT functional (`argmin over names` instead of `argmin over scores`) with nothing to diff,
nothing to hash, and nothing to audit. This module makes that functional DATA.

**This is not a new diagnostic and does not seek standing under L63.** The distinction is the whole
licence for building it: L63 governs objects that CLAIM TO EXPLAIN OR PREDICT -- they may not be
reasoned from until they beat a seated incumbent on a declared objective. A selector is not such an
object. It was already operating, in every tournament this arc has run, as an unnamed implementation
detail. Making an already-operating mechanism EXPLICIT adds no claim; it only makes an existing one
checkable. Nothing here predicts anything, and nothing here may be cited as evidence for any
hypothesis -- it is apparatus, in the sense L5/L15 use the word, and the bar apparatus must clear is
that it BITES, not that it wins.

WHAT IS DELIBERATELY NOT BUILT. Selector EQUIVALENCE and tournament MORPHISMS were proposed
alongside this and are NOT here. Two selectors having the same type does not make a morphism between
them meaningful, exactly as `D : Repository -> Evidence` failing to compose made the detector
"algebra" a type error rather than a structure (Rung 9). A morphism earns its name by preserving
something non-trivially, on an exhibited non-identity instance. None exists, so none is claimed.

    PYTHONHASHSEED=0 python3 exe_epistemics/selection.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

#: THE SELECTOR, AS DATA. Every field is a decision that was previously implicit in a call to `min`.
#: `objective` fixes the direction, `metric` names WHAT is being minimised (so a selector cannot be
#: reused against a score it was not written for), `tie_break` makes ties deterministic rather than
#: dict-order-dependent, and `exclude` names candidates that are present but not competing -- the
#: seated null is scored and displayed, and must never be able to WIN its own contest.
LOJO_MISS = {
    "objective": "min",
    "metric": "lojo_brier_miss_x10000",
    "tie_break": "lexicographic",
    "exclude": ("null",),
    "baseline": "null",
}


class SelectionError(Exception):
    """Raised when a selector is applied to scores it was not written for."""


#: THE SELECTOR SCHEMA. A certificate advertises its whole selector, so a verifier that interprets
#: only some of those fields lets the rest be forged freely -- the certificate would then certify a
#: winner while lying about the rule that chose it. Exact key equality is required (not a subset):
#: an unexpected key is a selector this verifier does not understand, and silently ignoring it is
#: how a field stops being checked.
_SELECTOR_KEYS = frozenset(("objective", "metric", "tie_break", "exclude", "baseline"))
_OBJECTIVES = ("min", "max")
_TIE_BREAKS = ("lexicographic", "reverse_lexicographic")


def validate_selector(selector):
    """Is this a well-formed selector? Schema first, so every advertised field has a checked meaning
    before any of them is used. `baseline in exclude` is L62 as a TYPE constraint rather than a
    remembered convention: a selector whose baseline can compete is not a strict selector with a
    quirk, it is malformed."""
    if not isinstance(selector, dict) or set(selector) != set(_SELECTOR_KEYS):
        return False
    if selector["objective"] not in _OBJECTIVES:
        return False
    if selector["tie_break"] not in _TIE_BREAKS:
        return False
    if not isinstance(selector["metric"], str) or not selector["metric"]:
        return False
    if not isinstance(selector["exclude"], tuple):
        return False
    if selector["baseline"] is not None and selector["baseline"] not in selector["exclude"]:
        return False
    return True


def _tie_precedes(a, b, tie_break):
    """Under the DECLARED tie rule, does candidate `a` come before `b`? Used by verification so the
    tie check follows the selector rather than a hard-coded `<`. The first verifier hard-coded
    lexicographic order while advertising `tie_break`, so a certificate could carry
    `reverse_lexicographic` and still verify -- the advertised rule and the enforced rule were
    different rules."""
    if tie_break == "lexicographic":
        return a < b
    if tie_break == "reverse_lexicographic":
        return a > b
    raise SelectionError("unknown tie_break %r" % (tie_break,))


def select(scores, selector):
    """Apply a SELECTOR (data) to a score table. Returns the winning candidate name.

    The objective is read from the selector rather than compiled in, so a change of direction is a
    change of DATA and shows up in a diff."""
    if not validate_selector(selector):
        raise SelectionError("malformed selector %r" % (selector,))
    return _select_general(scores, selector)


def certify(scores, selector):
    """Produce a CERTIFICATE rather than an assertion. The winner is never returned alone: it
    arrives with the score that won, the closest competitor, the comparison that decided it, the
    baseline it must also beat, and the selector that was used -- so a reader can check the verdict
    without re-running the procedure that produced it."""
    winner = select(scores, selector)
    field = [k for k in scores if k not in selector["exclude"]]
    rivals = [k for k in field if k != winner]
    sign = 1 if selector["objective"] == "min" else -1
    runner_up = _select_general({k: scores[k] for k in rivals}, selector) if rivals else None
    base = selector.get("baseline")
    return {
        "winner": winner,
        "score": scores[winner],
        "runner_up": runner_up,
        "runner_up_score": scores[runner_up] if runner_up else None,
        "baseline": base,
        "baseline_score": scores[base] if base in scores else None,
        "beats_baseline": (sign * scores[winner] < sign * scores[base]) if base in scores else None,
        "selector": dict(selector),
        "field": tuple(sorted(field)),
    }


def verify(cert, scores, expect_metric):
    """VERIFY THE PROPERTY, NEVER RE-RUN THE PROCEDURE -- and verify EVERY FIELD THE CERTIFICATE
    ADVERTISES, not merely the winner.

    L23 is explicit that two computations agreeing is a measurement only when they share no
    primitive -- one computation restated is a definition, not a check. So this does NOT call
    `select` again and compare. It checks DEFINING PROPERTIES directly, and a certificate that
    passes is correct even if `select` is wrong.

    THE SECOND VERSION OF THIS FUNCTION. The first checked `winner`, `score` and `field` and
    ignored `runner_up`, `runner_up_score`, `baseline`, `baseline_score` and `beats_baseline` --
    so a certificate could pass with an AUTHENTIC WINNER AND FORGED SURROUNDINGS, which is exactly
    the shape a certificate exists to prevent. A verifier that checks a subset of what its object
    advertises is not a verifier of that object; it is a verifier of the subset, and the name
    over-claims the difference. Either every advertised field is checked or the object is renamed
    to what it actually certifies. This checks every field."""
    sel = cert["selector"]
    if not validate_selector(sel):
        return False                          # an unverifiable selector verifies nothing
    if sel["metric"] != expect_metric:
        return False
    sign = 1 if sel["objective"] == "min" else -1
    tb = sel["tie_break"]
    field = [k for k in scores if k not in sel["exclude"]]
    # ---- the winner is a genuine argmin of the declared field -----------------------------------
    if cert["winner"] not in field:
        return False
    if tuple(sorted(field)) != tuple(cert["field"]):
        return False
    if scores[cert["winner"]] != cert["score"]:
        return False
    w = sign * scores[cert["winner"]]
    for k in field:
        if sign * scores[k] < w:
            return False                      # someone strictly better: not an argmin
        if sign * scores[k] == w and _tie_precedes(k, cert["winner"], tb):
            return False                      # a tie the DECLARED rule should have taken
    # ---- the runner-up is a genuine argmin of the field MINUS the winner ------------------------
    rivals = [k for k in field if k != cert["winner"]]
    if not rivals:
        if cert["runner_up"] is not None or cert["runner_up_score"] is not None:
            return False
    else:
        ru = cert["runner_up"]
        if ru not in rivals or scores[ru] != cert["runner_up_score"]:
            return False
        r = sign * scores[ru]
        for k in rivals:
            if sign * scores[k] < r:
                return False
            if sign * scores[k] == r and _tie_precedes(k, ru, tb):
                return False
    # ---- the baseline and the comparison against it ---------------------------------------------
    base = cert["baseline"]
    if base is not None:
        if base not in scores:
            return False
        if scores[base] != cert["baseline_score"]:
            return False
        if cert["beats_baseline"] != (sign * scores[cert["winner"]] < sign * scores[base]):
            return False
    return True


# ---- red-first: the certificate must REFUSE a forged winner -------------------------------------
def forged_winner_is_caught():
    """The plant. A certificate is issued honestly, then EVERY advertised field is forged in turn and
    `verify` must reject each one. If any forgery verifies, the certificate certifies nothing and
    every verdict resting on one is unsupported.

    THE SURROUNDING-FIELD FORGERIES ARE THE POINT of the second version: a certificate whose winner
    is authentic but whose runner-up, baseline or `beats_baseline` verdict is fabricated is exactly
    what the first `verify` would have waved through."""
    scores = {"null": 5000, "aaa": 9999, "mmm": 1000, "zzz": 1000}
    cert = certify(scores, LOJO_MISS)
    m0 = LOJO_MISS["metric"]
    honest = (verify(cert, scores, m0) and cert["winner"] == "mmm"     # ties -> lexicographic
              and cert["runner_up"] == "zzz" and cert["beats_baseline"] is True)
    forgeries = [
        dict(cert, winner="aaa", score=9999),                      # a loser crowned
        dict(cert, winner="zzz", score=1000),                      # the tie-loser crowned
        dict(cert, winner="null", score=5000),                     # an EXCLUDED candidate crowned
        dict(cert, score=1),                                       # winner right, score forged
        dict(cert, runner_up="aaa", runner_up_score=9999),         # runner-up forged
        dict(cert, runner_up_score=7),                             # runner-up score forged
        dict(cert, baseline_score=1),                              # baseline score forged
        dict(cert, beats_baseline=False),                          # the VERDICT itself forged
        dict(cert, field=("aaa", "mmm")),                          # the declared field forged
    ]
    return honest and not any(verify(f, scores, m0) for f in forgeries)


def forged_selector_is_caught():
    """THE FOURTH INSTANCE OF THE PATTERN, PLANTED. A certificate advertises its whole selector, and
    the previous verifier interpreted only `objective`, `exclude` and `baseline` -- so a certificate
    could carry an AUTHENTIC WINNER while lying about the rule that chose it. Worse, the tie check
    hard-coded `<` while the selector advertised `tie_break`, so the advertised rule and the enforced
    rule were simply different rules.

    Every forgery below keeps the winner and every score honest and corrupts only the SELECTOR."""
    scores = {"null": 5000, "aaa": 9999, "mmm": 1000, "zzz": 1000}
    cert = certify(scores, LOJO_MISS)
    honest = verify(cert, scores, expect_metric=LOJO_MISS["metric"])
    forgeries = [
        dict(cert["selector"], tie_break="reverse_lexicographic"),   # advertised rule flipped
        dict(cert["selector"], metric="totally_different_metric"),   # metric fabricated
        dict(cert["selector"], objective="max"),                     # direction flipped
        dict(cert["selector"], bogus="x"),                           # unknown key smuggled in
        {k: v for k, v in cert["selector"].items() if k != "baseline"},          # key removed
        dict(cert["selector"], exclude=()),                          # L62: baseline freed to compete
        dict(cert["selector"], metric=""),                           # empty metric
        dict(cert["selector"], exclude=["null"]),                    # wrong type for exclude
    ]
    m = LOJO_MISS["metric"]
    caught = not any(verify(dict(cert, selector=f), scores, expect_metric=m) for f in forgeries)
    metric_checked = not verify(cert, scores, expect_metric="some_other_metric")
    return honest and caught and metric_checked


def tie_rule_is_the_declared_one():
    """The tie check must FOLLOW the certificate's declared rule, not a fixed `<`. Under
    `reverse_lexicographic` the tied winner is `zzz`; a certificate declaring that rule while naming
    `aaa` must FAIL, and the honest one must pass. The old hard-coded verifier accepted both."""
    tied = {"null": 9000, "aaa": 1000, "zzz": 1000}
    rev = dict(LOJO_MISS, tie_break="reverse_lexicographic")
    cert = certify(tied, rev)
    honest = verify(cert, tied, expect_metric=rev["metric"]) and cert["winner"] == "zzz"
    swapped = dict(cert, winner="aaa", score=1000, runner_up="zzz", runner_up_score=1000)
    return honest and not verify(swapped, tied, expect_metric=rev["metric"])


def baseline_cannot_win():
    """L62 made structural: the seated null is SCORED and DISPLAYED but excluded from the field, so a
    tournament can never crown its own baseline. Here the null is the best number on the table and
    must still not be returned."""
    scores = {"null": 1, "aaa": 500, "bbb": 900}
    cert = certify(scores, LOJO_MISS)
    return cert["winner"] == "aaa" and cert["beats_baseline"] is False


# ---- winner stability: leave-one-out, transferred from the PROBE corpus to the TOURNAMENT --------
def ablation_stability(items, score_fn, selector, baseline=True):
    """THE COMBINATORIAL ENGINE, DECOUPLED FROM THE STATISTICAL MODEL.

    Delete each item, rescore with `score_fn`, re-select, and report which deletions move the
    winner. `score_fn` is a parameter rather than a hard-wired call to `prediction_residuals.lojo`
    precisely so the engine can be tested against a HAND-BUILT scorer whose answers are known
    exactly -- which is the only way to plant a knife edge and prove the instrument sees it. While
    the ablation was welded to the live corpus, the only fixtures available were real ones, and a
    fixture whose behaviour you cannot state in advance cannot falsify anything."""
    full = score_fn(items)
    full_winner = _select_general(full, selector)
    flips, winners = [], {}
    for i, item in enumerate(items):
        reduced = items[:i] + items[i + 1:]
        if not reduced:
            continue
        sc = score_fn(reduced)
        w = _select_general(sc, selector)
        winners[w] = winners.get(w, 0) + 1
        lost = baseline and selector.get("baseline") in sc and \
            not (sc[w] < sc[selector["baseline"]])
        if w != full_winner or lost:
            flips.append((item.get("pid", i) if isinstance(item, dict) else i,
                          w, sc[w], sc.get(selector.get("baseline"))))
    return {"winner": full_winner, "n": len(items), "flips": flips, "n_flips": len(flips),
            "stable": len(flips) == 0, "winner_census": dict(sorted(winners.items()))}


def stability_detects_a_knife_edge():
    """RED-FIRST, AND THE SECOND VERSION. The first read

        return isinstance(out.get("n_flips"), int)

    which is TRUE for every possible result, including one with zero flips. It asserted the RETURN
    TYPE of the function while its name promised the DETECTION OF FRAGILITY, so Rung 10's claim
    that fragility was provably detectable rested on a check that could not fail (L23). It happened
    to run on a fragile fixture, which is luck, not evidence.

    This version plants a scorer whose answers are known exactly: `alpha` wins on the full set, and
    deleting the single item `KNIFE` -- and only `KNIFE` -- hands the win to `beta`. The plant must
    report exactly one flip, name it, and the CONTROL scorer (a constant, where nothing can move)
    must report zero. A check that reports fragility everywhere is as useless as one that reports it
    nowhere, so both directions are demanded."""
    knife = [{"pid": "KNIFE"}, {"pid": "A"}, {"pid": "B"}]

    def knife_scores(items):
        pids = {i["pid"] for i in items}
        # alpha wins only while KNIFE is present; drop it and beta takes the lead.
        return {"null": 900, "alpha": 100 if "KNIFE" in pids else 500, "beta": 300}

    def flat_scores(items):
        return {"null": 900, "alpha": 100, "beta": 300}

    hot = ablation_stability(knife, knife_scores, LOJO_MISS)
    cold = ablation_stability(knife, flat_scores, LOJO_MISS)
    return (hot["winner"] == "alpha" and hot["n_flips"] == 1
            and hot["flips"][0][0] == "KNIFE" and hot["flips"][0][1] == "beta"
            and hot["stable"] is False
            and cold["stable"] is True and cold["n_flips"] == 0)


def stability_detects_a_lost_baseline():
    """The OTHER flip this instrument must see: the winner does not change, but it stops beating the
    baseline. A verdict can die without the crown moving, and an ablation that only watches the
    crown would call that STABLE."""
    items = [{"pid": "P"}, {"pid": "Q"}]

    def scores(its):
        return {"null": 300 if len(its) == 2 else 90, "alpha": 100, "beta": 500}

    out = ablation_stability(items, scores, LOJO_MISS)
    return out["winner"] == "alpha" and out["n_flips"] == 2 and out["stable"] is False


def winner_stability(rows=None, selector=LOJO_MISS):
    """HOW FRAGILE IS THE VERDICT? Rung 5 measured Q's W3 identifiability as ONE-PROBE FRAGILE by
    deleting each probe and asking whether the verdict flipped; QP05 alone carried it. This is the
    identical instrument applied one level up -- delete each JOINT, recompute the whole
    leave-one-joint-out table, and ask whether the WINNER changes.

    **This is a BOUNDARY, not a challenger.** It proposes no hypothesis and competes with nothing;
    it reports how much of a recorded verdict rests on a single row. That is a `does_not_show`
    made numerical, which is why it needs no standing under L63 either.

    THE LIVE-CORPUS APPLICATION of `ablation_stability`, which holds the combinatorics. The split is
    what makes the instrument testable: the engine takes a `score_fn`, so it can be run against a
    hand-built scorer whose answers are known in advance, while this wrapper supplies the real one."""
    import prediction_residuals as PR
    rows = PR.surface() if rows is None else rows
    out = ablation_stability(rows, PR.lojo, selector)
    n = out["n"]
    out["verdict"] = ("STABLE" if not out["flips"] else
                      "ONE-JOINT FRAGILE" if out["n_flips"] == 1 else
                      "FRAGILE (%d of %d joints flip it)" % (out["n_flips"], n))
    return out


# ---- selector SENSITIVITY: perturb the SELECTOR, not the data ------------------------------------
#: THE ADMISSIBLE POLYTOPE, DECLARED BEFORE IT IS EXPLORED. Winner stability perturbs the CORPUS;
#: this perturbs the SELECTOR, and asks how much selector freedom exists before the winner moves.
#:
#: The critical discipline is that a variant must be DEFENSIBLE A PRIORI, never merely different --
#: a search over arbitrary selectors would find one that changes the answer and prove nothing. Most
#: of the selector's apparent degrees of freedom turn out to be CONSTRAINED BY LAWS ALREADY ON THE
#: BOOKS, and that is itself the finding:
#:
#:   objective  FIXED by the metric. Both scores are losses (lower is better), so `max` is not a
#:              variant, it is an error. The metric determines the direction.
#:   exclude    FIXED by L62. The seated baseline may not be able to win its own contest; dropping
#:              the exclusion is not an admissible selector, it is the defect L62 names.
#:   baseline   FIXED. The rolling empirical marginal null is the seated incumbent (checkpoint 9);
#:              a different baseline is a different tournament, not a different selector over it.
#:   metric     FREE, 2 values. Brier and log loss are both PROPER scoring rules. multinull already
#:              established that the INCUMBENT verdict is not rule-dependent; this asks the identical
#:              question of the COVARIATE verdict, which no rung has asked.
#:   tie_break  FREE, 2 values. Both are arbitrary but deterministic; if the winner moves under a
#:              tie-break change, the verdict rests on an exact tie and should say so.
#:
#: So the admissible polytope has FOUR points, not dozens. The smallness is not a limitation of the
#: analysis -- it is a measurement of how much the existing laws already pin down.
FREE_AXES = {
    "metric": ("lojo_brier_miss_x10000", "lojo_logloss_miss_millibits"),
    "tie_break": ("lexicographic", "reverse_lexicographic"),
}


def _select_general(scores, selector):
    """`select` widened to the admissible tie-break variants only."""
    field = [k for k in scores if k not in selector["exclude"]]
    if not field:
        raise SelectionError("empty field")
    sign = 1 if selector["objective"] == "min" else -1
    if selector["tie_break"] == "lexicographic":
        return min(field, key=lambda k: (sign * scores[k], k))
    if selector["tie_break"] == "reverse_lexicographic":
        return min(field, key=lambda k: (sign * scores[k], [-ord(c) for c in k]))
    raise SelectionError("unknown tie_break %r" % (selector["tie_break"],))


def lojo_logloss(rows=None):
    """The SAME leave-one-joint-out design as `prediction_residuals.lojo`, scored by LOG LOSS in
    millibits instead of Brier. Log loss is code length by Kraft-McMillan, so this is the MDL-side
    reading of the identical experiment.

    THE BOUNDARY RULE WAS FIXED BEFORE COMPUTING, and then found unnecessary: log loss diverges if a
    prediction reaches exactly 0 or 1, so a clamp would have been a modelling choice that decides the
    answer. It was checked first -- predictions on this corpus lie in [0.025, 0.670], strictly
    interior -- so NO CLAMP IS APPLIED and none is hidden. Were a future corpus to hit the boundary
    this function must RAISE rather than silently clamp."""
    import math
    import prediction_residuals as PR
    rows = PR.surface() if rows is None else rows
    out = {}
    for name, feat in (("null", None), ("margin", "margin"), ("nclass", "nclass"),
                       ("topmass", "topmass")):
        total = 0
        for i, r in enumerate(rows):
            train = rows[:i] + rows[i + 1:]
            p = PR._predict(train, r, feat)
            p_y = p if not r["hit"] else 1 - p
            if p_y <= 0:
                raise SelectionError("log loss undefined: p_y <= 0 at %s/%s" % (name, r["pid"]))
            total += -math.log2(float(p_y))
        out[name] = int(round(total / len(rows) * 1000))
    return out


def _scores_for(metric, rows=None):
    import prediction_residuals as PR
    if metric == "lojo_brier_miss_x10000":
        return PR.lojo(rows)
    if metric == "lojo_logloss_miss_millibits":
        return lojo_logloss(rows)
    raise SelectionError("unknown metric %r" % (metric,))


def admissible_selectors():
    """The four points of the declared polytope, in a deterministic order."""
    out = []
    for metric in FREE_AXES["metric"]:
        for tb in FREE_AXES["tie_break"]:
            out.append(dict(LOJO_MISS, metric=metric, tie_break=tb))
    return out


def sensitivity(rows=None):
    """WINNER UNDER EVERY ADMISSIBLE SELECTOR, plus the minimum selector EDIT DISTANCE to a different
    winner. Reports `INVARIANT` when no admissible selector changes the answer -- which is a stronger
    statement than winner stability, because it says the verdict is not an artefact of how the
    contest was scored OR how ties were broken."""
    ref = LOJO_MISS
    ref_scores = _scores_for(ref["metric"], rows)
    ref_winner = _select_general(ref_scores, ref)
    table, distances = [], []
    for sel in admissible_selectors():
        sc = _scores_for(sel["metric"], rows)
        w = _select_general(sc, sel)
        edits = sum(1 for k in FREE_AXES if sel[k] != ref[k])
        beats = sc[w] < sc[sel["baseline"]]
        table.append({"metric": sel["metric"], "tie_break": sel["tie_break"], "winner": w,
                      "score": sc[w], "baseline": sc[sel["baseline"]], "beats_baseline": beats,
                      "edits": edits})
        if w != ref_winner:
            distances.append(edits)
    return {
        "reference_winner": ref_winner,
        "table": table,
        "n_selectors": len(table),
        "min_edit_to_change_winner": min(distances) if distances else None,
        "verdict": ("INVARIANT across the admissible polytope" if not distances else
                    "SELECTOR-SENSITIVE (%d edit(s) suffice)" % min(distances)),
        "always_beats_baseline": all(r["beats_baseline"] for r in table),
    }


def sensitivity_can_report_sensitivity():
    """Non-vacuity (L61): the analysis must be ABLE to return SELECTOR-SENSITIVE, or INVARIANT is an
    empty answer. A synthetic score table whose winner differs by tie-break is constructed and the
    tie-break axis alone must flip it."""
    tied = {"null": 9000, "aaa": 1000, "zzz": 1000}
    lex = _select_general(tied, dict(LOJO_MISS, tie_break="lexicographic"))
    rev = _select_general(tied, dict(LOJO_MISS, tie_break="reverse_lexicographic"))
    return lex == "aaa" and rev == "zzz" and lex != rev


def main():
    import prediction_residuals as PR
    print("SELECTION — the functional between a tournament and its winner, as an object")
    print()
    print("selector (DATA, not code): %s" % LOJO_MISS)
    print()
    res = PR.lojo()
    cert = certify(res, LOJO_MISS)
    print("scores: %s" % dict(sorted(res.items())))
    print()
    print("CERTIFICATE")
    for k in ("winner", "score", "runner_up", "runner_up_score", "baseline", "baseline_score",
              "beats_baseline", "field"):
        print("  %-16s %s" % (k, cert[k]))
    print("  %-16s %s" % ("verified", verify(cert, res, LOJO_MISS["metric"])))
    print()
    print("red-first — a forged winner is REFUSED : %s" % forged_winner_is_caught())
    print("red-first — the baseline cannot win    : %s" % baseline_cannot_win())
    print("red-first — fragility is detectable    : %s" % stability_detects_a_knife_edge())
    print()
    st = winner_stability()
    print("WINNER STABILITY — leave-one-joint-out over the tournament (Rung 5's instrument, one "
          "level up)")
    print("  winner (full corpus) : %s" % st["winner"])
    print("  joints               : %d" % st["n"])
    print("  winner census        : %s" % st["winner_census"])
    print("  flips                : %d" % st["n_flips"])
    for pid, w, s, b in st["flips"]:
        print("      drop %-5s -> winner %-8s %d vs baseline %d%s"
              % (pid, w, s, b, "  (NO LONGER BEATS BASELINE)" if s >= b else ""))
    print("  VERDICT              : %s" % st["verdict"])
    print()
    sen = sensitivity()
    print("SELECTOR SENSITIVITY — perturbing the SELECTOR instead of the corpus")
    print("  free axes: %s" % {k: list(v) for k, v in sorted(FREE_AXES.items())})
    print("  fixed by law: objective (by the metric), exclude (L62), baseline (checkpoint 9)")
    print()
    print("  %-32s %-22s %-9s %8s %9s %6s" % ("metric", "tie_break", "winner", "score",
                                              "baseline", "edits"))
    for r in sen["table"]:
        print("  %-32s %-22s %-9s %8d %9d %6d"
              % (r["metric"], r["tie_break"], r["winner"], r["score"], r["baseline"], r["edits"]))
    print()
    print("  red-first — sensitivity is reportable : %s" % sensitivity_can_report_sensitivity())
    print("  min selector edits to change winner   : %s" % sen["min_edit_to_change_winner"])
    print("  beats the baseline under ALL of them  : %s" % sen["always_beats_baseline"])
    print("  VERDICT                               : %s" % sen["verdict"])
    print()
    print("BOUNDARY, NOT A CHALLENGER. This proposes nothing and competes with nothing; it reports")
    print("how much of Rung 9's recorded verdict rests on any single joint, and how much on how the")
    print("contest was scored. does_not_show: that the winner predicts anything, that stability or")
    print("invariance implies validity (a stable wrong answer is stable), or that a RETROSPECTIVE")
    print("verdict survives prospectively — that is the forward test (L20).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
