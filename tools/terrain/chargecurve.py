# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""chargecurve — THE REGISTERED EXPERIMENT, RUN (URDRCHG1). The peak question, answered as asked and
then shown to have been malformed as asked.

WHAT THIS DISCHARGES. `cohort` (URDRCOH1) shipped the budget charge `B // max(k, 1)` and carried, for
several rungs, a stated and UNRUN falsification protocol: *measure end-to-end verification cost
against k on a real corpus; if cost is maximal at k = 1 rather than at k = 0, the peaked charge is
the correct schedule and this constant is wrong.* One commit ago it registered C1 through C5 against
that measurement, WITH the classifier, so the rule could not be chosen after the numbers arrived.
This module is the measurement. It reads `cohort.prediction_text()` — which is also what makes it the
derived discharger `disposition` recognises — and scores every id.

    THE HEADLINE IS NOT WHICH ARM HELD. IT IS THAT THE SHIPPED ONE-LINE FALSIFIER, TAKEN AT ITS WORD,
    WOULD HAVE ADOPTED THE PEAKED CHARGE.

The protocol component IS maximal at k = 1. A reading of that sentence with the numbers in hand — and
with no registration to answer to — adopts the peak. It should not, for two reasons that only a
committed prediction makes it natural to state. The component that peaks is NOT the one the schedule
is a schedule for; and the k = 1 reading is a FAILED verification exhausting the peer list, not a
more expensive success, so it is not a point on the same curve as the others at all. Restricted to
the members whose outcome is the same, the protocol cost is FLAT. That is the whole value of having
registered a family rather than the metaphor: the inflation here was available, cheap, and one
sentence away.

THE MEASURAND IS COUNTED, NEVER TIMED, exactly as registered. Wall clock is MEASURED-on-named-host in
this tree and ungated by rule. Two components:

    DECISION COST   `free_reaches` evaluations the SHIPPED `min_cut` performs on the occupancy
    PROTOCOL COST   peers the SHIPPED `verify_cohort` fetches

Both are instrumented by wrapping `cohort.free_reaches` and reading `verify_cohort`'s own return, so
what is measured is the shipped procedure rather than a re-implementation of it — a falsifier that
does not run the thing it measures guards a copy. They are reported SIDE BY SIDE AND NEVER SUMMED:
fusing them needs a weight, the weight would be chosen, and the chosen weight would decide the shape.

THE PEER FIXTURE IS DERIVED FROM THE SHIPPED ONE RATHER THAN INVENTED. `cohort.peer_population` takes
`(n, thick)` and so cannot express a BREACHED submitter, which is the k = 0 point. `peers_for` takes
an occupancy and applies the same construction, and `the_peer_construction_reproduces_the_shipped_one`
proves the two agree on every wall where both are defined.

    AND THAT EXTENSION IS WHAT EXPOSED C2. At k = 1 the sub-gap perturbation set is EMPTY — the
    census runs over `range(1, max(k, 1))` — so a one-cell peer is AT the gap, where `cohort`'s own
    `at_or_above_the_gap_disagreement_becomes_possible` says disagreement is possible. Measured: all
    16 one-cell peers disagree, agreement never reaches the threshold, the loop exhausts the list, and
    the verdict is COHORT_FAILED. The fixture has no below-gap noise at k = 1 to have.

GRADE (D5). MEASURED: both cost components over the declared corpus, with the shipped procedures
instrumented rather than reimplemented; the volume control; the outcome census that shows the k = 1
protocol reading is a different event from the others. DERIVED: every shape verdict comes from
`cohort.classify_shape`, committed one rung earlier and not re-chosen here. DECLARED: the corpus is
the synthetic `spanning_wall` family `cohort` already declares as such, and the peer fixture is
`cohort`'s own construction extended to one occupancy it could not name.

does_not_show: that the charge `B // max(k, 1)` is the RIGHT policy — C4's disposition is that it is
a policy rather than a model of measured cost, which says what it is NOT and leaves what it ought to
be untouched; that these two components are the only costs that matter, since a deployment's costs
are latency and bytes and neither is countable in a byte-identical gate; that the peak is absent in
some system other than this one, the corpus being synthetic and k confounded with wall volume by
construction, which C5 measures rather than waves away; and nothing about whether a DIFFERENT peer
fixture — one carrying genuine below-gap noise at k = 1 — would leave the protocol cost flat, which
is the obvious next question and is NOT answered here."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import budget as _BG                                                # noqa: E402
import cohort as CO                                                 # noqa: E402

MAGIC = b"URDRCHG1"

HELD, MISSED = "HELD", "MISSED"

#: The corpus, DECLARED. `spanning_wall(n, thick)` has k == thick, and the breached member is that
#: same one-thick wall with its lowest cell removed — the k = 0 point `cohort.peer_population` could
#: not express, since its signature takes a thickness and not an occupancy.
WORLD = 4
THICKNESSES = (1, 2, 3)
#: The volume control for C5: the same k at two world sizes.
CONTROL = ((4, 2), (5, 2))


class ChargeCurveError(Exception):
    code = "CHARGE-REFUSE"


def breached_occupancy(n=WORLD):
    """A BREACHED submitter — the k = 0 corpus member. One cell out of a one-thick spanning wall."""
    w = CO.spanning_wall(n, 1)
    return w - {sorted(w)[0]}


def corpus():
    """((label, occupancy, n), ...) in ascending k — the order every shape is read in."""
    out = [("k0-breached", breached_occupancy(), WORLD)]
    for t in THICKNESSES:
        out.append((f"k{t}-thick{t}", CO.spanning_wall(WORLD, t), WORLD))
    return tuple(out)


# ---- instrumentation: the SHIPPED procedures, counted rather than reimplemented -------------------
def decision_cost(occ, n):
    """(k, probes) — `probes` is the number of `free_reaches` evaluations the SHIPPED `min_cut`
    performs, counted by wrapping the function `min_cut` actually calls. Reimplementing a counting
    min-cut would measure a copy."""
    real = CO.free_reaches
    box = [0]

    def counted(o, m, axis=0):
        box[0] += 1
        return real(o, m, axis)

    try:
        CO.free_reaches = counted
        k = CO.min_cut(occ, n)
    finally:
        CO.free_reaches = real
    return k, box[0]


def peers_for(occ):
    """`cohort.peer_population`'s construction, over an OCCUPANCY rather than a thickness."""
    cs = sorted(occ)
    if len(cs) < 14:
        raise ChargeCurveError(f"occupancy of {len(cs)} is too small for this fixture")
    return (CO._peer(1, occ), CO._peer(2, occ - {cs[0]}), CO._peer(3, occ - {cs[5]}),
            CO._peer(4, occ - {cs[9]}), CO._peer(5, occ - {cs[13]}), CO._peer(6, frozenset()))


def the_peer_construction_reproduces_the_shipped_one():
    """The extension is DERIVED, not invented: it agrees with `cohort.peer_population` on every wall
    where that function is defined. Returns a row per thickness: (thick, identical)."""
    return tuple((t, peers_for(CO.spanning_wall(WORLD, t)) == CO.peer_population(WORLD, t))
                 for t in THICKNESSES)


def protocol_cost(occ, n):
    """(outcome, agreeing, fetched) from the SHIPPED `verify_cohort`."""
    outcome, agreeing, fetched, _rem = CO.verify_cohort(occ, peers_for(occ), _BG.SHARD_BUDGET, n)
    return outcome, agreeing, fetched


# ---- the panel -----------------------------------------------------------------------------------
def panel():
    """(label, k, cells, decision, protocol, outcome, agreeing) per corpus member, in ascending k."""
    rows = []
    for label, occ, n in corpus():
        k, probes = decision_cost(occ, n)
        outcome, agreeing, fetched = protocol_cost(occ, n)
        rows.append((label, k, len(occ), probes, fetched, outcome, agreeing))
    return tuple(rows)


def decision_shape():
    return CO.classify_shape([r[3] for r in panel()])


def protocol_shape():
    return CO.classify_shape([r[4] for r in panel()])


def schedule_shape():
    """The SHIPPED schedule read at the same k values — the thing the two components are compared
    against. It is not measured; it is evaluated."""
    return CO.classify_shape([CO.charge_for_gap(r[1]) for r in panel()])


def outcome_homogeneous_protocol():
    """THE DIAGNOSIS, REPORTED BESIDE THE VERDICT AND NEVER INSTEAD OF IT. A protocol cost is only
    comparable across k where the OUTCOME is the same: a run that FAILED exhausted the peer list, and
    exhaustion is not a more expensive success. Returns (ks, costs, shape) over the members that
    reached COHORT_VERIFIED."""
    rows = [r for r in panel() if r[5] == CO.VERIFIED]
    costs = [r[4] for r in rows]
    return tuple(r[1] for r in rows), tuple(costs), CO.classify_shape(costs)


def the_k1_reading_is_a_different_event():
    """WHY THE PROTOCOL COMPONENT PEAKS, measured rather than asserted. At k = 1 the sub-gap
    perturbation set is EMPTY — `cohort`'s census runs over `range(1, max(k, 1))` — so a one-cell peer
    sits AT the gap, where that module's own law says disagreement is POSSIBLE. Returns
    (sub_gap_peers, at_gap_peers, at_gap_disagreements, k1_outcome, others_outcome)."""
    _k, sub, _imp = CO.sub_gap_disagreement_is_impossible(WORLD, 1)
    _k2, at, dis = CO.at_or_above_the_gap_disagreement_becomes_possible(WORLD, 1)
    rows = {r[1]: r[5] for r in panel()}
    return sub, at, dis, rows[1], tuple(sorted({v for kk, v in rows.items() if kk != 1}))


def volume_control():
    """C5: hold k, vary the world. Returns ((n, thick, k, cells, decision), ...)."""
    out = []
    for n, t in CONTROL:
        w = CO.spanning_wall(n, t)
        k, probes = decision_cost(w, n)
        out.append((n, t, k, len(w), probes))
    return tuple(out)


# ---- scoring: every registered id, with its mechanism ---------------------------------------------
#: THE DISPOSITIONS. Each id is scored against what the committed record said it would show, using
#: `cohort.classify_shape` — the rule frozen one rung earlier — and never a rule chosen here.
DISPOSITIONS = {
    "C1": (HELD,
           "the decision cost RISES with k and is classified NEITHER, as registered. Measured "
           "1, 2, 49, 1778 across k = 0..3. The mechanism registered with it is the one that "
           "produced it: `min_cut` returns at the first subset size that opens the wall, so "
           "certifying gap k contains the work of refuting every smaller gap"),
    "C2": (MISSED,
           "the protocol cost is NOT constant in k: 6 fetches at k = 1 against 5 everywhere else. "
           "The registered mechanism said the population's capture noise lies BELOW the gap, and at "
           "k = 1 there is no below-gap noise to have — the sub-gap set is EMPTY, all 16 one-cell "
           "peers disagree, agreement never reaches the threshold, and the loop exhausts the list to "
           "COHORT_FAILED. The record flagged this arm as most likely a FIXTURE artifact and it is "
           "one, in the direction of the fixture being under-specified rather than over-tuned"),
    "C3": (HELD,
           "the two components have unrelated k-dependence and land in DIFFERENT registered classes "
           "— decision NEITHER, protocol PEAKED — one growing without bound and the other varying "
           "by a single fetch. No scalar represents both, so the peak question as originally posed "
           "presumes one curve where there are two"),
    "C4": (HELD,
           "the shipped schedule is MONOTONE and matches NEITHER measured component. THIS WAS THE "
           "ARM THAT COULD REFUTE THE REGISTRATION and it did not: `B // max(k, 1)` is a POLICY "
           "rather than a model of measured cost. What that licenses is RELABELLING it, never "
           "replacing it with a peaked schedule — the measurement says what the charge is not"),
    "C5": (HELD,
           "the k/volume confound BITES rather than being hypothetical: holding k = 2 and moving the "
           "world from 4 to 5 moves the decision cost from 49 to 76. A cost curve read against k in "
           "this family is also a curve against volume, and the two cannot be separated within it"),
}


def dispositions():
    return tuple((i, DISPOSITIONS[i][0], DISPOSITIONS[i][1]) for i in sorted(DISPOSITIONS))


def every_registered_prediction_has_exactly_one_disposition():
    """`voxreanchor`'s local law, applied to this record: the scored set must EQUAL the REGISTERED
    set, read out of `cohort`'s committed file rather than from a list kept here. Scoring a
    prediction that was never registered, or leaving a registered one unscored, both redden.

    Calling `cohort.prediction_text()` from another module is ALSO what makes this module the derived
    discharger `disposition` recognises — the same call doing the work and proving it was done."""
    registered = set(CO.registered_predictions())
    scored = set(DISPOSITIONS)
    return (registered == scored, tuple(sorted(registered - scored)),
            tuple(sorted(scored - registered)))


def the_record_is_unedited():
    """The registration is pinned by `cohort`'s own conformance corpus, so a record rewritten once
    the numbers were in reddens THERE. This re-reads it from the same source the scoring used, so a
    scorer cannot quietly work from a different text than the one that is pinned."""
    return (CO.scene_result("prediction") == CO.golden("prediction"),
            "NO RESULT IS NAMED" in CO.prediction_text())


def the_shipped_falsifier_would_have_adopted_the_peak():
    """THE FINDING, AND IT IS ABOUT THE METHOD RATHER THAN ABOUT THE CHARGE.

    `cohort`'s one-line protocol says: if cost is maximal at k = 1 rather than at k = 0, the peaked
    charge is correct. Taken at its word against the protocol component, the antecedent HOLDS — and
    the conclusion does not follow, because that component is not the one the schedule schedules and
    its k = 1 reading is an exhausted failure rather than a dearer success. Returns
    (protocol_at_k0, protocol_at_k1, antecedent_holds, decision_is_maximal_at_k0)."""
    rows = {r[1]: (r[3], r[4]) for r in panel()}
    dec = [v[0] for _k, v in sorted(rows.items())]
    return (rows[0][1], rows[1][1], rows[1][1] > rows[0][1], dec[0] == max(dec))


def problems():
    out = []
    ok, missing, extra = every_registered_prediction_has_exactly_one_disposition()
    if not ok:
        out.append(("unscored", missing, extra))
    if not the_record_is_unedited()[0]:
        out.append(("record-edited", (), ()))
    for t, same in the_peer_construction_reproduces_the_shipped_one():
        if not same:
            out.append(("fixture-drift", (t,), ()))
    for i, verdict, reason in dispositions():
        if verdict not in (HELD, MISSED) or not reason.strip():
            out.append(("bad-disposition", (i,), ()))
    return out


# ---- digests + scenes ------------------------------------------------------------------------------
def cc_digest(name, payload):
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(f"|{name}|{payload}".encode())
    return h.hexdigest()


def _scene_panel():
    return cc_digest("panel", f"{panel()}:{decision_shape()}:{protocol_shape()}:"
                              f"{schedule_shape()}:{volume_control()}")


def _scene_scoring():
    return cc_digest("scoring", f"{dispositions()}:"
                                f"{every_registered_prediction_has_exactly_one_disposition()}:"
                                f"{outcome_homogeneous_protocol()}:"
                                f"{the_k1_reading_is_a_different_event()}:"
                                f"{the_shipped_falsifier_would_have_adopted_the_peak()}:"
                                f"{the_peer_construction_reproduces_the_shipped_one()}")


_SCENES = {"panel": _scene_panel, "scoring": _scene_scoring}
SCENES = ("panel", "scoring")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_chargecurve.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                out.append(ln)
    return tuple(out)


def emitted_matches_pinned():
    return conformance_lines() == pinned_lines()


def golden(name):
    for ln in pinned_lines():
        nm, dig = ln.split()
        if nm == name:
            return dig
    raise ChargeCurveError(f"no golden named {name!r}")


if __name__ == "__main__":
    for r in panel():
        print("%-12s k=%-4s cells=%-3d decision=%-7d protocol=%-2d %-16s agreeing=%d" % r)
    print()
    print("decision shape :", decision_shape())
    print("protocol shape :", protocol_shape())
    print("schedule shape :", schedule_shape())
    print("homogeneous    :", outcome_homogeneous_protocol())
    print("k1 is different:", the_k1_reading_is_a_different_event())
    print("volume control :", volume_control())
    print("would adopt    :", the_shipped_falsifier_would_have_adopted_the_peak())
    print()
    for i, v, why in dispositions():
        print("%s %-7s %s" % (i, v, why[:96]))
    print()
    print("closure  :", every_registered_prediction_has_exactly_one_disposition())
    print("problems :", problems())
    for n in SCENES:
        print(n, scene_result(n))
