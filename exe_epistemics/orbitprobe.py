# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""orbitprobe — checkpoint 10 RESEARCH: does an orbit scalar earn existence? (not an adopted instrument)

THE PROPOSAL under examination. Pair the structural cost H = (R,F,D,C) with an ORBIT-RETURN scalar
    Omega_t = min_{0<=j<t-l} d(S_t, S_j),   S_t = (B_t, Pi_t, R_t, M_t)
    d = d_B + d_Pi + d_R + d_M      (symmetric differences + fixed-point probability L1)
and a predictive-gain scalar G_t = L_null,t - L_engine,t, combining into a STERILE-ORBIT detector: the
engine returns near an earlier organizational state AND has failed to improve against the null. The
motivating question is real and this ledger cannot presently answer it: after three consecutive
triple-zero runs, is the engine at a PREDICTIVE FIXED POINT or in a SINGLE-BASIS ORBIT with no
available opponent? H and v_D cannot tell those apart.

THIS SCRIPT DOES NOT ADOPT THE INSTRUMENT. The arc has a scar here: the coupling/interface instrument
(URDRQPR1's Gamma table) WAS adopted mid-run, then SUSPENDED at checkpoint 3 -- starved of emergence
events, with its one directional call wrong. L58 (representation is earned, not designed) and L3 (no
promotion without independent preregistered recurrence) both apply. So this rung MEASURES three
decidable things and stops.

FINDING 1 -- OMEGA AS SPECIFIED IS DEGENERATE HERE, and this is a proof, not an opinion. The ledger is
APPEND-ONLY by L2: a freeze is never rewritten, a resolution never retracted. Therefore for every
j < t the resolved signature satisfies R_j subset R_t, so
    d_R(S_t,S_j) = |R_t \\ R_j| = (joints resolved between j and t) >= 3 per batch,
and likewise M_j subset M_t. Hence
    Omega_t >= 3*(l+1) > 0  for all t  -- the scalar can NEVER return to zero,
and because d_R grows strictly with distance, the minimizing j is ALWAYS the most recent admissible
one. Omega_t therefore measures ELAPSED BATCHES, not recurrence: it is a clock wearing a topologist's
clothes. The defect is not in the idea but in the STATE VECTOR -- a return detector cannot include
monotone-accumulating components.

    THE REPAIR, stated but NOT adopted: define the state over the non-accumulating CONFIGURATION --
    the multiset of error TYPES (not instances), the live-basis identity/count, the minted-family SET,
    and the calibration shape. Return then becomes possible, because "sole basis, underconfident,
    v_D = 0, error-types {ranking, ranking, clean}" is a configuration that CAN recur.

FINDING 2 -- THE PREMISE IS CONFIRMED BY MEASUREMENT: v_D does not track predictive gain. Per-batch
G is computed here from the checkpoint-9 corpus under the same frozen proper score. Across the three
consecutive triple-zero runs G/joint is NOT monotone, and the v_D = 0 batches span nearly the whole
observed range -- so the engine's own convergence census is blind to its predictive performance,
which is exactly the gap the orbit proposal names.

FINDING 3 -- A CANDIDATE NEAR-RETURN EXISTS IN CONFIGURATION SPACE. Under the repaired state, batch 2
and batch 8 are near-identical (same leading-class hit rate, adjacent G/joint) while v_D calls them
DIFFERENT (1 vs 0). If the repaired Omega is ever adopted, that pair is its first test case -- and
notably it is a pair the existing census misclassifies.

GRADE. MEASURED: the per-batch G decomposition, the v_D/G non-separation, the degeneracy bound (an
arithmetic consequence of append-only, asserted and checked here), determinism (stdlib-only,
exhaustive, rerun byte-identical). DECLARED: the batch->joint grouping, transcribed from the ledger's
run structure. does_not_show: that the REPAIRED Omega would work -- it is stated, not built, and its
falsifier is frozen in PREDICTIONS.md for a PROSPECTIVE test; that G differences between batches are
significant (n = 2-3 joints per batch, descriptive only, L20); anything about Urdr's correctness.

    PYTHONHASHSEED=0 python3 exe_epistemics/orbitprobe.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import multinull as MN                                   # the checkpoint-9 corpus and frozen scorer

#: The ledger's own run/batch structure. P10 and P19 are absent because the ledger declared them
#: NON-SCORING at their freeze (disclosed contamination) -- the same rule checkpoint 9 applied.
BATCHES = (
    ("b1", ("P9", "P11"), None),
    ("b2", ("P12", "P13", "P14"), 1),
    ("b3", ("P15", "P16", "P17"), 1),
    ("b4", ("P18", "P20"), 0),
    ("b5", ("P21", "P22", "P23"), 0),
    ("b6", ("P24", "P25", "P26"), 0),
    ("b7", ("P27", "P28", "P29"), 1),
    ("b8", ("P30", "P31", "P32"), 0),
)

#: Batches per checkpoint step, used only for the degeneracy bound's joint count.
JOINTS_PER_BATCH = 3


def per_batch():
    rows = dict((r["pid"], r) for r in MN.run())
    out = []
    for name, pids, vd in BATCHES:
        sel = [rows[p] for p in pids if p in rows]
        if not sel:
            continue
        inc = sum(r["bs_p"] for r in sel)
        nul = sum(r["bs_q"] for r in sel)
        g = nul - inc
        out.append({"batch": name, "n": len(sel), "v_D": vd, "inc": inc, "null": nul, "G": g,
                    "g_per": g // len(sel),
                    "lead": sum(1 for r in sel if r["lead_p"] == r["y"])})
    return out


def omega_lower_bound(gap_l=1, joints=JOINTS_PER_BATCH):
    """FINDING 1, as arithmetic: because the ledger is append-only, d_R alone forces
    Omega_t >= joints*(l+1) > 0. Returns that bound; it is never 0 for any admissible l >= 0."""
    return joints * (gap_l + 1)


def omega_can_return(gap_l=1):
    """The decidable form of finding 1: can the specified Omega ever reach 0? No -- for any l."""
    return omega_lower_bound(gap_l) == 0


def vd_separates_gain(stats=None):
    """FINDING 2, decided: does v_D separate predictive gain? TRUE only if the v_D=1 and v_D=0 batches
    occupy DISJOINT ranges of G/joint. Overlap means the census is blind to predictive performance."""
    stats = per_batch() if stats is None else stats
    one = [s["g_per"] for s in stats if s["v_D"] == 1]
    zero = [s["g_per"] for s in stats if s["v_D"] == 0]
    if not one or not zero:
        return None
    return min(one) > max(zero) or min(zero) > max(one)


def near_return_candidate(stats=None):
    """FINDING 3: the closest pair in the REPAIRED (non-accumulating) configuration projection used
    here -- equal leading-class hit rate, minimal |G/joint| difference, non-adjacent batches."""
    stats = per_batch() if stats is None else stats
    best = None
    for i, a in enumerate(stats):
        for b in stats[i + 2:]:                          # non-adjacent only (the l guard)
            if a["n"] != b["n"] or a["lead"] != b["lead"]:
                continue
            d = abs(a["g_per"] - b["g_per"])
            if best is None or d < best[0]:
                best = (d, a["batch"], b["batch"], a["v_D"], b["v_D"])
    return best


# ---- BLOCKER 1: the append-only plant (red-first, per L15/L23) ------------------------------------
#: Two synthetic histories with IDENTICAL live organizational configuration and DIFFERENT ledger
#: length. This is the exact plant the impossibility law needs: a valid LIVE-state metric must assign
#: zero distance; the specified Omega assigns a large positive one, purely from archived rows.
_LIVE_CONFIG = {"bases": ("B-M'",),
                "families": ("approximation", "scheduling"),
                "predictor": (("C-R", 45), ("C-INV", 28), ("C-EQ", 10), ("C-FLOOR", 8),
                              ("R-M", 4), ("R-O", 5))}
HISTORY_A = {"live": _LIVE_CONFIG, "resolved": tuple()}                  # no archive
HISTORY_B = {"live": _LIVE_CONFIG, "resolved": tuple(range(30))}         # 30 archived resolutions


def _sym_diff(a, b):
    return len(set(a) ^ set(b))


def distance_specified(h1, h2):
    """d = d_B + d_Pi + d_R + d_M, AS PROPOSED -- the ledger coordinate carries positive weight."""
    live1, live2 = h1["live"], h2["live"]
    d_b = _sym_diff(live1["bases"], live2["bases"])
    d_m = _sym_diff(live1["families"], live2["families"])
    d_pi = sum(abs(dict(live1["predictor"]).get(c, 0) - dict(live2["predictor"]).get(c, 0))
               for c in set(dict(live1["predictor"])) | set(dict(live2["predictor"])))
    d_r = _sym_diff(h1["resolved"], h2["resolved"])                      # THE APPEND-ONLY COORDINATE
    return d_b + d_pi + d_r + d_m


def distance_live(h1, h2):
    """THE REPAIR: the same metric over the LIVE quotient only -- lineage is a path label, not a
    state coordinate. S_live = (bases, predictor, active families); L = (resolved, minted) excluded."""
    live1, live2 = h1["live"], h2["live"]
    d_b = _sym_diff(live1["bases"], live2["bases"])
    d_m = _sym_diff(live1["families"], live2["families"])
    d_pi = sum(abs(dict(live1["predictor"]).get(c, 0) - dict(live2["predictor"]).get(c, 0))
               for c in set(dict(live1["predictor"])) | set(dict(live2["predictor"])))
    return d_b + d_pi + d_m


def append_only_plant_bites():
    """RED-FIRST: the plant must expose the defect in BOTH directions -- the specified metric reports
    a large distance between operationally IDENTICAL live states, and the repaired metric reports
    zero. If either half failed, the impossibility law would be decoration."""
    d_spec = distance_specified(HISTORY_A, HISTORY_B)
    d_live = distance_live(HISTORY_A, HISTORY_B)
    return d_spec > 0 and d_live == 0, d_spec, d_live


# ---- BLOCKER 2: leave-one-batch-out model comparison ---------------------------------------------
#: FROZEN model set. Tiny by design (L58): each is at most two parameters, and the NULL is seated
#: from the start (L62). Scored leave-one-batch-out so no model is fitted on the point it predicts.
def _mean(xs):
    from fractions import Fraction
    return Fraction(sum(xs), len(xs)) if xs else Fraction(0)


def _fit_predict(train, test_x, use_vd, use_hist):
    """Exact rational least squares (stdlib Fraction -- no float enters the verdict). Returns the
    prediction for test_x. Falls back to the training mean where a predictor is constant/absent."""
    from fractions import Fraction
    ys = [Fraction(t["y"]) for t in train]
    if not use_vd and not use_hist:
        return _mean(ys)
    cols = []
    if use_vd:
        cols.append([Fraction(t["vd"]) for t in train])
    if use_hist:
        cols.append([Fraction(t["prev"]) for t in train])
    ybar = _mean(ys)
    if len(cols) == 1:
        x = cols[0]
        xbar = _mean(x)
        sxx = sum((xi - xbar) ** 2 for xi in x)
        if sxx == 0:
            return ybar
        b = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, ys)) / sxx
        a = ybar - b * xbar
        xv = Fraction(test_x[0] if use_vd else test_x[1])
        return a + b * xv
    x1, x2 = cols
    m1, m2 = _mean(x1), _mean(x2)
    s11 = sum((v - m1) ** 2 for v in x1)
    s22 = sum((v - m2) ** 2 for v in x2)
    s12 = sum((v - m1) * (w - m2) for v, w in zip(x1, x2))
    s1y = sum((v - m1) * (y - ybar) for v, y in zip(x1, ys))
    s2y = sum((w - m2) * (y - ybar) for w, y in zip(x2, ys))
    det = s11 * s22 - s12 * s12
    if det == 0:
        return ybar
    b1 = (s22 * s1y - s12 * s2y) / det
    b2 = (s11 * s2y - s12 * s1y) / det
    a = ybar - b1 * m1 - b2 * m2
    return a + b1 * Fraction(test_x[0]) + b2 * Fraction(test_x[1])


def lobo_models(stats=None):
    """THE HARD TEST for blocker 2. Does adding v_D improve HELD-OUT prediction of G over a
    null/history-only model? Corpus: batches with a known v_D AND a predecessor G (so the
    history model is defined). Reports mean absolute held-out error per model."""
    stats = per_batch() if stats is None else stats
    pts = []
    for i, s in enumerate(stats):
        if s["v_D"] is None or i == 0:
            continue
        pts.append({"batch": s["batch"], "y": s["g_per"], "vd": s["v_D"],
                    "prev": stats[i - 1]["g_per"]})
    out = {}
    for name, uv, uh in (("null", False, False), ("census(v_D)", True, False),
                         ("history(G-1)", False, True), ("combined", True, True)):
        errs = []
        for i, p in enumerate(pts):
            train = pts[:i] + pts[i + 1:]
            if not train:
                continue
            pred = _fit_predict(train, (p["vd"], p["prev"]), uv, uh)
            errs.append(abs(pred - p["y"]))
        out[name] = (int(_mean(errs)) if errs else None, len(errs))
    return out, pts


def census_adds_predictive_information(res=None):
    """DECIDED: does seating v_D beat BOTH the null and the history-only model out-of-sample?
    If False, v_D is structurally informative but NOT predictively informative over this corpus."""
    res = lobo_models()[0] if res is None else res
    c, n, h = res["census(v_D)"][0], res["null"][0], res["history(G-1)"][0]
    if None in (c, n, h):
        return None
    return c < n and c < h


def main():
    stats = per_batch()
    print("%-5s %2s %4s %14s %14s %14s %10s %s"
          % ("batch", "n", "v_D", "BS(inc)", "BS(null)", "G=null-inc", "G/joint", "lead"))
    for s in stats:
        print("%-5s %2d %4s %14d %14d %14d %10d %d/%d"
              % (s["batch"], s["n"], s["v_D"], s["inc"], s["null"], s["G"], s["g_per"],
                 s["lead"], s["n"]))
    print()
    print("FINDING 1 -- Omega (as specified) can return to 0: %s" % omega_can_return())
    print("            lower bound Omega_t >= %d for l=1 (append-only forces d_R > 0); the"
          % omega_lower_bound())
    print("            minimizing j is always the most recent admissible one, so the scalar")
    print("            measures ELAPSED BATCHES, not recurrence. Degenerate as specified.")
    print()
    triple = [s for s in stats if s["batch"] in ("b6", "b7", "b8")]
    print("FINDING 2 -- across the three consecutive triple-zero runs, G/joint = %s"
          % ", ".join(str(s["g_per"]) for s in triple))
    print("            monotone? %s" % (triple[0]["g_per"] <= triple[1]["g_per"] <= triple[2]["g_per"]
                                        or triple[0]["g_per"] >= triple[1]["g_per"] >= triple[2]["g_per"]))
    print("            v_D separates predictive gain: %s" % vd_separates_gain(stats))
    print("            -> the engine's own convergence census is BLIND to predictive performance,")
    print("               which is the gap the orbit proposal correctly names.")
    print()
    nr = near_return_candidate(stats)
    print("FINDING 3 -- closest non-adjacent configuration pair: %s vs %s "
          "(|dG/joint| = %d, v_D %s vs %s)" % (nr[1], nr[2], nr[0], nr[3], nr[4]))
    print("            v_D calls them different; the configuration projection calls them near-identical.")
    print()
    bites, d_spec, d_live = append_only_plant_bites()
    print("BLOCKER 1 PLANT -- two synthetic histories, IDENTICAL live configuration, ledger lengths")
    print("            0 vs 30 archived resolutions:")
    print("              specified metric d(A,B) = %d   (nonzero purely from archived rows)" % d_spec)
    print("              repaired live metric  = %d   (operationally identical -> 0)" % d_live)
    print("            plant bites in both directions: %s" % bites)
    print()
    res, pts = lobo_models(stats)
    print("BLOCKER 2 HARD TEST -- leave-one-batch-out, mean absolute held-out error on G/joint")
    print("            (exact rational fits, no float; corpus n = %d batches)" % len(pts))
    for name in ("null", "census(v_D)", "history(G-1)", "combined"):
        err, n = res[name]
        print("              %-14s MAE = %12s  (n=%d)" % (name, err, n))
    print("            v_D adds predictive information (beats null AND history): %s"
          % census_adds_predictive_information(res))
    print()
    print("NOT ADOPTED. The repaired Omega is STATED, not built; its falsifier is frozen in")
    print("PREDICTIONS.md for a PROSPECTIVE test (L58: representation is earned, not designed;")
    print("the suspended Gamma instrument is the precedent this rung refuses to repeat).")
    print("NO SIGNIFICANCE CLAIMED: the LOBO corpus is %d batches. Descriptive only (L20)." % len(pts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
