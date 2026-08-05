# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""mdl — closing E's open term: a real code length for DELTA-L-MODEL.

WHY THIS EXISTS. Rung 4 re-froze resolution efficiency as an MDL quantity after the original ratio
form (dG / (dC + dR)) was shown malformed twice over -- a RATIO where MDL's tradeoff is additive, and
a quotient of INCOMMENSURABLE units. The repaired form fixed everything except one term:

    E = dL_data - lambda * dL_model,   both in MILLIBITS,   lambda = 1 (the canonical two-part code)

`dL_data` was closed at Rung 4: log loss IS code length by Kraft-McMillan, and multinull.py computes
it. `dL_model` was left OPEN with one constraint recorded -- it must be a REAL CODE LENGTH (bits to
DESCRIBE the change), never a count of edits wearing a bit's clothing. This module closes it.

THE DEFINITION, and why this one. The engine's model is a CATEGORICAL PREDICTOR: per joint it emits a
distribution over the live class vocabulary. Minting a seam family ENLARGES that vocabulary. The
standard two-part code charges a model its PARAMETRIC COMPLEXITY -- the bits needed to state the
fitted parameters to the precision the data can support -- and for a multinomial over K classes fitted
on n observations that is the classical Rissanen term:

    L_model(K, n) = ((K - 1) / 2) * log2(n)   bits          [K-1 free parameters, (1/2)log2(n) each]

so minting, which takes the vocabulary from K to K', costs

    dL_model = L_model(K', n) - L_model(K, n) = ((K' - K) / 2) * log2(n)   bits.

This is a code length, not an edit count: it is the number of bits actually required to transmit the
enlarged model's parameters at the resolution n observations justify. It is also the term that makes E
a genuine tradeoff -- a family that explains nothing still costs (K'-K)/2 * log2(n) bits, so E goes
NEGATIVE for a mint that buys no predictive improvement, which is exactly the behaviour the ratio form
could not produce.

WHAT IS COMPUTED HERE, AND WHAT IS DELIBERATELY NOT. `dL_model` is computable now, from K and n alone,
and it is computed below for the arc's two mints. **`dL_data` for those mints is NOT computed**, and
the reason is a discipline point rather than an effort one: measuring it requires constructing a
COUNTERFACTUAL pre-mint model (what would the basis have predicted without the class it later
minted?), and how that counterfactual redistributes the minted class's mass is a MODELLING CHOICE that
would decide the answer. Choosing it now, with the outcomes already known, is precisely the freedom
checkpoint 9's preregistration existed to remove. The protocol is FROZEN below and left unrun.

GRADE. MEASURED: the parametric-complexity arithmetic (exact rational, integer millibits, rerun
byte-identical). DECLARED: that multinomial parametric complexity is the right model cost for this
predictor -- a standard choice, but a choice. does_not_show: E itself (dL_data is unrun); that either
mint was efficient or inefficient; anything about the arc's correctness.

    PYTHONHASHSEED=0 python3 exe_epistemics/mdl.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

MILLIBIT = 1000

#: The arc's two MINTS, with the class vocabulary before and after each. Transcribed from the ledger:
#: the approximation axis minted at checkpoint 4 (frontier/ashdepth carriers, C-FLOOR entering the
#: live vocabulary), the scheduling axis at P27 (govern/priogov, C-ORD entering).
#: `n` is the number of SCORED joints available at that point -- the observations the parameters are
#: fitted on, which is what the (1/2)log2(n) precision term refers to.
MINTS = (
    ("approximation axis (checkpoint 4)", 7, 8, 17),
    ("scheduling axis (P27)", 8, 9, 27),
)


def _log2_millibits(x):
    """log2(x) in millibits, computed in float and ROUNDED to an integer millibit. The rounding is
    what keeps the gate byte-identical: any plausible last-ULP difference is far below 1 millibit."""
    import math
    return int(round(math.log2(x) * MILLIBIT))


def l_model(k, n):
    """Rissanen's parametric complexity for a multinomial over k classes fitted on n observations:
    ((k-1)/2) * log2(n) bits, returned in MILLIBITS as an integer."""
    if k < 1 or n < 1:
        raise ValueError("k and n must be >= 1")
    return ((k - 1) * _log2_millibits(n)) // 2


def delta_l_model(k_before, k_after, n):
    """The code-length cost of enlarging the class vocabulary from k_before to k_after on n
    observations. Positive when the vocabulary grows -- a mint always COSTS, which is the property
    that makes E a tradeoff rather than a reward."""
    return l_model(k_after, n) - l_model(k_before, n)


def mint_costs():
    """dL_model for each recorded mint. dL_data is NOT computed (see the frozen protocol)."""
    return [(name, kb, ka, n, delta_l_model(kb, ka, n)) for name, kb, ka, n in MINTS]


def a_useless_family_still_costs():
    """DECIDED, and it is the property that distinguishes this form from the refuted ratio: a family
    that explains NOTHING (dL_data = 0) yields a NEGATIVE E, because dL_model is strictly positive.
    The old ratio form divided by a structural-change count and could not express this at all."""
    cost = delta_l_model(8, 9, 27)
    e_if_useless = 0 - cost
    return cost > 0 and e_if_useless < 0


def frozen_protocol():
    """THE FROZEN dL_data PROTOCOL -- stated, and deliberately NOT executed here.

    To measure dL_data for a past mint, a PRE-MINT counterfactual model is required: what the basis
    would have predicted on the same joints without the class it later minted. Three things must be
    fixed BEFORE any score exists, because each of them decides the answer:

      (1) REDISTRIBUTION. The minted class's mass in each frozen vector must go somewhere. The rule is
          fixed as PROPORTIONAL redistribution over the remaining classes -- the maximum-entropy choice
          given no further information, and the only one that adds no new assumption.
      (2) SCOPE. dL_data is summed over the joints scored AFTER the mint only. Including earlier joints
          would credit a family for outcomes it was minted FROM, which is the retrofit trap L58 names.
      (3) RULE. Log loss in millibits, the same proper score as checkpoint 9's MDL rescore, so the
          numbers are commensurable with the record rather than a parallel scale.

    Running this with the outcomes already known and the redistribution rule unfixed would let the
    author choose the verdict. The rule is fixed here; the run belongs to a rung that has not happened.
    """
    return {"redistribution": "proportional (max-entropy)",
            "scope": "joints scored strictly after the mint",
            "rule": "log loss, millibits",
            "status": "FROZEN, UNRUN"}


def main():
    print("DELTA-L-MODEL — the parametric code length of enlarging the class vocabulary")
    print("  L_model(k, n) = ((k-1)/2) * log2(n) bits   [Rissanen two-part code]")
    print()
    print("%-36s %5s %5s %5s %12s" % ("mint", "K", "K'", "n", "dL_model (mb)"))
    for name, kb, ka, n, cost in mint_costs():
        print("%-36s %5d %5d %5d %12d" % (name, kb, ka, n, cost))
    print()
    print("a family explaining NOTHING still costs (so E goes negative): %s"
          % a_useless_family_still_costs())
    print()
    print("dL_data: %s" % frozen_protocol())
    print()
    print("E IS NOT COMPUTED. dL_model is closed; dL_data's counterfactual protocol is frozen and")
    print("unrun, because choosing the redistribution rule with outcomes known would decide the")
    print("answer. STATUS: E remains EXPERIMENTAL under L63.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
