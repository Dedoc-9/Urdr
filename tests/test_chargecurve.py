# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/chargecurve.py — THE REGISTERED EXPERIMENT, RUN (URDRCHG1).

  THE SHIPPED PROCEDURES ARE INSTRUMENTED, NOT REIMPLEMENTED — the decision cost counts calls to
    the `free_reaches` that `min_cut` actually uses, and the wrapper is proved to be removed again.
  THE CLASSIFIER IS `cohort`'s, FROZEN ONE COMMIT EARLIER — never a rule chosen here.
  THE PEER FIXTURE IS DERIVED FROM THE SHIPPED ONE — identical on every wall where both are defined,
    and extended only to the breached occupancy `cohort.peer_population` could not name.
  THE SCORED SET IS CLOSED AGAINST THE REGISTERED SET — read out of `cohort`'s committed record, so
    scoring an unregistered id or leaving a registered one unscored both redden.
  THE k = 1 PROTOCOL READING IS A DIFFERENT EVENT — a FAILED verification exhausting the peer list,
    not a dearer success, and the outcome-homogeneous subpanel is flat.
  AND THE SHIPPED ONE-LINE FALSIFIER'S ANTECEDENT HOLDS — so it would have adopted the peak.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import chargecurve as CC                                            # noqa: E402
import cohort as CO                                                 # noqa: E402


class TheInstrumentRunsTheShippedProcedure(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in CC.SCENES:
            self.assertEqual(CC.scene_result(n), CC.golden(n), n)
            self.assertEqual(CC.scene_result(n), CC.scene_result(n), n)
        self.assertTrue(CC.emitted_matches_pinned())

    def test_the_counter_is_removed_again(self):
        """An instrument left installed would poison every later reading in the process."""
        before = CO.free_reaches
        CC.decision_cost(CO.spanning_wall(4, 1), 4)
        self.assertIs(CO.free_reaches, before, "the wrapper outlived the measurement")

    def test_the_counter_survives_a_raising_measurement(self):
        """The restore is in a `finally`, and that is asserted rather than read."""
        before = CO.free_reaches
        with self.assertRaises(TypeError):
            CC.decision_cost(None, 4)                        # not an occupancy; raises inside
        self.assertIs(CO.free_reaches, before)
        # and the module still measures afterwards, so the restore is a restore and not a reset
        self.assertEqual(CC.decision_cost(CO.spanning_wall(4, 1), 4)[0], 1)

    def test_the_decision_cost_counts_the_real_min_cut(self):
        """Not a re-implementation: a wall whose k is known must come back with that k."""
        for thick in (1, 2, 3):
            k, probes = CC.decision_cost(CO.spanning_wall(4, thick), 4)
            self.assertEqual(k, thick, f"thick={thick}")
            self.assertGreater(probes, 0)

    def test_the_peer_fixture_reproduces_the_shipped_one(self):
        rows = CC.the_peer_construction_reproduces_the_shipped_one()
        self.assertEqual(len(rows), 3)
        for thick, same in rows:
            self.assertTrue(same, f"the fixture drifted from cohort's at thick={thick}")

    def test_a_too_small_occupancy_refuses(self):
        with self.assertRaises(CC.ChargeCurveError):
            CC.peers_for(frozenset({(0, 0, 0)}))


class ThePanel(unittest.TestCase):
    def test_the_corpus_spans_k_zero_through_three(self):
        self.assertEqual(tuple(r[1] for r in CC.panel()), (0, 1, 2, 3))

    def test_both_components_are_measured_and_not_summed(self):
        rows = CC.panel()
        self.assertEqual(tuple(r[3] for r in rows), (1, 2, 49, 1778))
        self.assertEqual(tuple(r[4] for r in rows), (5, 6, 5, 5))

    def test_the_shapes_come_from_the_frozen_classifier(self):
        """Every verdict is `cohort.classify_shape`, committed one rung before the numbers."""
        self.assertEqual(CC.decision_shape(), CO.SHAPE_NEITHER)
        self.assertEqual(CC.protocol_shape(), CO.SHAPE_PEAKED)
        self.assertEqual(CC.schedule_shape(), CO.SHAPE_MONOTONE)
        self.assertEqual(CC.decision_shape(),
                         CO.classify_shape([r[3] for r in CC.panel()]))

    def test_the_volume_control_moves_the_cost_at_fixed_k(self):
        rows = CC.volume_control()
        self.assertEqual(tuple(r[2] for r in rows), (2, 2), "k must be held")
        self.assertNotEqual(rows[0][4], rows[1][4], "the confound did not bite")
        self.assertEqual(rows, ((4, 2, 2, 32, 49), (5, 2, 2, 50, 76)))


class TheScoring(unittest.TestCase):
    def test_the_scored_set_equals_the_registered_set(self):
        ok, missing, extra = CC.every_registered_prediction_has_exactly_one_disposition()
        self.assertTrue(ok, f"missing={missing} extra={extra}")
        self.assertEqual({i for i, _v, _w in CC.dispositions()},
                         set(CO.registered_predictions()))

    def test_an_unregistered_id_is_caught(self):
        """The plant. Scoring something nobody registered is the back-dating this whole mechanism
        exists to forbid, wearing the clothes of extra diligence."""
        keep = dict(CC.DISPOSITIONS)
        try:
            CC.DISPOSITIONS["C9"] = (CC.HELD, "invented after the fact")
            ok, _m, extra = CC.every_registered_prediction_has_exactly_one_disposition()
            self.assertFalse(ok)
            self.assertEqual(extra, ("C9",))
            self.assertNotEqual(CC.problems(), [])
        finally:
            CC.DISPOSITIONS.clear()
            CC.DISPOSITIONS.update(keep)
        self.assertEqual(CC.problems(), [])

    def test_an_unscored_registered_id_is_caught(self):
        keep = dict(CC.DISPOSITIONS)
        try:
            del CC.DISPOSITIONS["C3"]
            ok, missing, _e = CC.every_registered_prediction_has_exactly_one_disposition()
            self.assertFalse(ok)
            self.assertEqual(missing, ("C3",))
        finally:
            CC.DISPOSITIONS.clear()
            CC.DISPOSITIONS.update(keep)

    def test_four_held_and_one_missed_each_with_a_mechanism(self):
        verdicts = {i: v for i, v, _w in CC.dispositions()}
        self.assertEqual(verdicts, {"C1": CC.HELD, "C2": CC.MISSED, "C3": CC.HELD,
                                    "C4": CC.HELD, "C5": CC.HELD})
        for i, _v, why in CC.dispositions():
            self.assertTrue(why.strip(), i)
            self.assertGreater(len(why), 60, f"{i} has no mechanism, only a verdict")

    def test_the_record_is_unedited(self):
        """A record rewritten once the numbers were in reddens in `cohort`'s own corpus; this
        re-reads it from the same source the scoring used, so a scorer cannot work from a different
        text than the one that is pinned."""
        pinned, no_result = CC.the_record_is_unedited()
        self.assertTrue(pinned)
        self.assertTrue(no_result)


class TheDiagnosisIsReportedBesideTheVerdict(unittest.TestCase):
    def test_the_k1_reading_is_a_different_event(self):
        sub, at, dis, k1, others = CC.the_k1_reading_is_a_different_event()
        self.assertEqual(sub, 0, "there is no below-gap noise at k=1 to have")
        self.assertEqual((at, dis), (16, 16), "every one-cell peer sits AT the gap and disagrees")
        self.assertEqual(k1, CO.FAILED)
        self.assertEqual(others, (CO.VERIFIED,))

    def test_the_outcome_homogeneous_subpanel_is_flat(self):
        ks, costs, shape = CC.outcome_homogeneous_protocol()
        self.assertEqual(ks, (0, 2, 3))
        self.assertEqual(costs, (5, 5, 5))
        self.assertEqual(shape, CO.SHAPE_MONOTONE)
        self.assertNotEqual(shape, CC.protocol_shape(),
                            "the diagnosis must differ from the verdict or it adds nothing")

    def test_the_shipped_falsifier_would_have_adopted_the_peak(self):
        """THE FINDING, and it is about the method rather than about the charge."""
        at0, at1, antecedent, dec_max_at_0 = CC.the_shipped_falsifier_would_have_adopted_the_peak()
        self.assertEqual((at0, at1), (5, 6))
        self.assertTrue(antecedent, "cost IS maximal at k=1 for the protocol component")
        self.assertFalse(dec_max_at_0, "and the decision component is maximal at the other end")


if __name__ == "__main__":
    unittest.main()
