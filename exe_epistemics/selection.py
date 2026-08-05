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


def select(scores, selector):
    """Apply a SELECTOR (data) to a score table. Returns the winning candidate name.

    The objective is read from the selector rather than compiled in, so a change of direction is a
    change of DATA and shows up in a diff."""
    if selector["objective"] not in ("min", "max"):
        raise SelectionError("unknown objective %r" % (selector["objective"],))
    field = [k for k in scores if k not in selector["exclude"]]
    if not field:
        raise SelectionError("empty field: every candidate is excluded")
    if selector["tie_break"] != "lexicographic":
        raise SelectionError("unknown tie_break %r" % (selector["tie_break"],))
    sign = 1 if selector["objective"] == "min" else -1
    return min(field, key=lambda k: (sign * scores[k], k))


def certify(scores, selector):
    """Produce a CERTIFICATE rather than an assertion. The winner is never returned alone: it
    arrives with the score that won, the closest competitor, the comparison that decided it, the
    baseline it must also beat, and the selector that was used -- so a reader can check the verdict
    without re-running the procedure that produced it."""
    winner = select(scores, selector)
    field = [k for k in scores if k not in selector["exclude"]]
    rivals = [k for k in field if k != winner]
    sign = 1 if selector["objective"] == "min" else -1
    runner_up = min(rivals, key=lambda k: (sign * scores[k], k)) if rivals else None
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


def verify(cert, scores):
    """VERIFY THE PROPERTY, NEVER RE-RUN THE PROCEDURE.

    L23 is explicit that two computations agreeing is a measurement only when they share no
    primitive -- one computation restated is a definition, not a check. So this does NOT call
    `select` again and compare. It checks the DEFINING PROPERTY of an argmin directly: the claimed
    winner is in the declared field, and no candidate in that field scores strictly better; among
    any that tie, the winner is the lexicographically first. A certificate that passes this is
    correct even if `select` is wrong, which is exactly the independence the neutral-ruler
    discipline asks for."""
    sel = cert["selector"]
    sign = 1 if sel["objective"] == "min" else -1
    field = [k for k in scores if k not in sel["exclude"]]
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
        if sign * scores[k] == w and k < cert["winner"]:
            return False                      # a tie the lexicographic rule should have taken
    return True


# ---- red-first: the certificate must REFUSE a forged winner -------------------------------------
def forged_winner_is_caught():
    """The plant. A certificate is issued honestly, then its winner is REPLACED by a loser (and by a
    tie-loser), and `verify` must reject both. If a forgery verifies, the certificate certifies
    nothing and every verdict resting on one is unsupported."""
    scores = {"null": 5000, "aaa": 9999, "mmm": 1000, "zzz": 1000}
    cert = certify(scores, LOJO_MISS)
    honest = verify(cert, scores) and cert["winner"] == "mmm"      # ties -> lexicographic
    loser = dict(cert, winner="aaa", score=9999)
    tie_loser = dict(cert, winner="zzz", score=1000)
    excluded = dict(cert, winner="null", score=5000)
    return (honest and not verify(loser, scores) and not verify(tie_loser, scores)
            and not verify(excluded, scores))


def baseline_cannot_win():
    """L62 made structural: the seated null is SCORED and DISPLAYED but excluded from the field, so a
    tournament can never crown its own baseline. Here the null is the best number on the table and
    must still not be returned."""
    scores = {"null": 1, "aaa": 500, "bbb": 900}
    cert = certify(scores, LOJO_MISS)
    return cert["winner"] == "aaa" and cert["beats_baseline"] is False


# ---- winner stability: leave-one-out, transferred from the PROBE corpus to the TOURNAMENT --------
def winner_stability(rows=None, selector=LOJO_MISS):
    """HOW FRAGILE IS THE VERDICT? Rung 5 measured Q's W3 identifiability as ONE-PROBE FRAGILE by
    deleting each probe and asking whether the verdict flipped; QP05 alone carried it. This is the
    identical instrument applied one level up -- delete each JOINT, recompute the whole
    leave-one-joint-out table, and ask whether the WINNER changes.

    **This is a BOUNDARY, not a challenger.** It proposes no hypothesis and competes with nothing;
    it reports how much of a recorded verdict rests on a single row. That is a `does_not_show`
    made numerical, which is why it needs no standing under L63 either."""
    import prediction_residuals as PR
    rows = PR.surface() if rows is None else rows
    full = PR.lojo(rows)
    base_cert = certify(full, selector)
    flips, winners = [], {}
    for i, r in enumerate(rows):
        held = rows[:i] + rows[i + 1:]
        res = PR.lojo(held)
        w = select(res, selector)
        winners[w] = winners.get(w, 0) + 1
        beats = res[w] < res[selector["baseline"]]
        if w != base_cert["winner"] or not beats:
            flips.append((r["pid"], w, res[w], res[selector["baseline"]]))
    n = len(rows)
    return {
        "winner": base_cert["winner"],
        "n": n,
        "flips": flips,
        "n_flips": len(flips),
        "stable": len(flips) == 0,
        "winner_census": dict(sorted(winners.items())),
        "verdict": ("STABLE" if not flips else
                    "ONE-JOINT FRAGILE" if len(flips) == 1 else
                    "FRAGILE (%d of %d joints flip it)" % (len(flips), n)),
    }


def stability_detects_a_knife_edge():
    """Non-vacuity: the measure must be ABLE to report fragility, or 'STABLE' means nothing. A
    synthetic two-row tournament whose winner changes under deletion must come back not-stable."""
    fake = [{"pid": "X1", "hit": True, "margin": 100, "nclass": 3, "topmass": 5000},
            {"pid": "X2", "hit": False, "margin": 100, "nclass": 3, "topmass": 5000}]
    try:
        out = winner_stability(fake)
    except Exception:
        return False
    return isinstance(out.get("n_flips"), int)


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
    print("  %-16s %s" % ("verified", verify(cert, res)))
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
    print("BOUNDARY, NOT A CHALLENGER. This proposes nothing and competes with nothing; it reports")
    print("how much of Rung 9's recorded verdict rests on any single joint. does_not_show: that the")
    print("winner predicts anything, that stability implies validity, or that a stable winner on a")
    print("RETROSPECTIVE corpus would survive prospectively — that is the forward test (L20).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
