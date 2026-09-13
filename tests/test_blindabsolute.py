# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/blindabsolute.py — THE ABSOLUTENESS RUNG, 0 FOR 5 (URDRBAB1).

  ABSOLUTENESS IS STRUCTURAL — an absolute candidate's signature CANNOT receive the face pair, so
    the claim is enforced by the signature rather than by a comment promising the function does not
    peek. The two-pointed subject takes the axis, and that is what makes it the B3 subject.
  THE SEARCH CAN RETURN NOTHING — connectivity has no equal-value opposite-verdict pair in the
    corpus or the construction, without which `refuted` would mean only that the search ran.
  IT REPRODUCES TWO ANSWERS `blindscreen` ALREADY PUBLISHED, on both polarities: `cell_count` falls
    from the corpus, `free_components` does not and needs the construction.
  THE SCORED SET IS CLOSED against the set the committed record declares.
  THE VERDICTS ARE WHAT WAS MEASURED — all five MISSED, including the refuting arm — and the tests
    assert that, because a rung whose gate row demanded its predictions HOLD could never report a
    refutation.
  AND THE CRITERION IS NOT REPAIRED HERE — structurally: this module assigns nothing into the module
    it is scoring.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import ast
import inspect
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import blindabsolute as BA                                          # noqa: E402
import blindscreen as BS                                            # noqa: E402
import cohort as CO                                                 # noqa: E402


class TheCandidatesWereDeclaredBeforeMeasurement(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in BA.SCENES:
            self.assertEqual(BA.scene_result(n), BA.golden(n), n)
            self.assertEqual(BA.scene_result(n), BA.scene_result(n), n)
        self.assertTrue(BA.emitted_matches_pinned())

    def test_absoluteness_is_enforced_by_the_signature(self):
        """`sealframe`'s neutral ruler applied to a measurand: an absolute candidate cannot be
        handed the face pair, so it cannot peek even if its author wanted it to."""
        for name, kind, params, consistent in BA.absoluteness_is_structural():
            self.assertTrue(consistent, f"{name} is declared {kind} and its signature disagrees")
            if kind == BA.ABSOLUTE:
                self.assertNotIn("axis", params, name)
            else:
                self.assertIn("axis", params, name)

    def test_the_declared_set_is_four_absolute_and_one_two_pointed(self):
        kinds = [k for _n, k, _f, _v, _r in BA.CANDIDATES]
        self.assertEqual(kinds.count(BA.ABSOLUTE), 4)
        self.assertEqual(kinds.count(BA.TWO_POINTED), 1)
        for _n, _k, _f, _v, rationale in BA.CANDIDATES:
            self.assertGreater(len(rationale), 40, "a subject with no rationale is a subject chosen")

    def test_the_unscored_subject_is_kept_out_of_the_scoring(self):
        """A subject introduced after the registration may inform the reading and may not move the
        score — letting it would be the back-dating the whole mechanism exists to forbid."""
        scored = {n for n, _k, _f, _v, _r in BA.CANDIDATES}
        self.assertNotIn("face_component_pair", scored)
        self.assertIn("face_component_pair", {n for n, _k, _f, _r in BA.UNSCORED})
        self.assertEqual(len(BA.census()), 5)

    def test_an_undeclared_candidate_refuses(self):
        with self.assertRaises(BA.BlindAbsoluteError):
            BA.kind_of("not-a-candidate")


class TheSearchCanReturnNothing(unittest.TestCase):
    def test_the_positive_control(self):
        """Without this, `refuted` would mean only that the search ran. Connectivity is the decisive
        measurand and survives both the corpus and the construction."""
        self.assertTrue(BA.a_candidate_that_is_not_blind_is_not_refuted())

    def test_it_reproduces_blindscreens_published_answers_on_both_polarities(self):
        corpus_cell, corpus_free_is_none, hand_free = BA.the_search_finds_a_known_witness()
        self.assertTrue(corpus_cell, "cell_count must fall from the corpus")
        self.assertTrue(corpus_free_is_none, "free_components must have NO corpus witness")
        self.assertTrue(hand_free, "and must fall to the construction")

    def test_the_corpus_is_searched_before_the_construction(self):
        """B4 is about that order: the construction is only reached where the corpus has nothing."""
        for name, _k, refuted, source, _d, _t, _b, _v in BA.census():
            if refuted:
                self.assertIn(source, ("CORPUS", "HAND"), name)
        self.assertEqual(BA.refutation("euler_characteristic")[1], "CORPUS")


class TheScoring(unittest.TestCase):
    def test_the_scored_set_equals_the_registered_set(self):
        ok, missing, extra = BA.every_registered_prediction_has_exactly_one_disposition()
        self.assertTrue(ok, f"missing={missing} extra={extra}")
        self.assertEqual({i for i, _v, _w in BA.score()}, set(BS.registered_predictions()))

    def test_all_five_missed_and_each_carries_its_reading(self):
        """THE RESULT, ASSERTED. A gate row that demanded the predictions HOLD could never report a
        refutation, which would make the registration decorative."""
        verdicts = {i: v for i, v, _w in BA.score()}
        self.assertEqual(verdicts, {"B1": BA.MISSED, "B2": BA.MISSED, "B3": BA.MISSED,
                                    "B4": BA.MISSED, "B5": BA.MISSED})
        for i, _v, why in BA.score():
            self.assertGreater(len(why), 40, f"{i} has a verdict and no reading")

    def test_the_refuting_arm_is_the_one_that_fired(self):
        """B3 named this outcome in advance: a two-pointed candidate refuted means the criterion is
        wrong about what it explains."""
        two = [r for r in BA.census() if r[1] == BA.TWO_POINTED]
        self.assertEqual(len(two), 1)
        self.assertTrue(two[0][2], "the two-pointed subject was NOT refuted")
        b3 = next(w for i, _v, w in BA.score() if i == "B3")
        self.assertIn("WRONG ABOUT WHAT IT EXPLAINS", b3)

    def test_an_absolute_candidate_survived(self):
        surv = [r[0] for r in BA.census() if r[1] == BA.ABSOLUTE and not r[2]]
        self.assertEqual(surv, ["largest_free_component"])

    def test_the_record_is_unedited(self):
        pinned, no_result = BA.the_record_is_unedited()
        self.assertTrue(pinned, "the committed record no longer matches blindscreen's own pin")
        self.assertTrue(no_result)

    def test_an_unregistered_id_cannot_be_scored(self):
        self.assertEqual(BA.an_unregistered_id_cannot_be_scored(), (True, True))


class TheCriterionIsNotRepairedHere(unittest.TestCase):
    def test_this_module_assigns_nothing_into_the_module_it_scores(self):
        """Structural, and deliberately not textual: the first draft of this guard tested its own
        text and failed on itself, because the guard names the substrings it searches for."""
        self.assertEqual(BA.the_criterion_is_not_repaired_here(), (True, True, True))
        tree = ast.parse(inspect.getsource(sys.modules["blindabsolute"]))
        writes = [t for n in ast.walk(tree) if isinstance(n, ast.Assign) for t in n.targets
                  if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                  and t.value.id == "BS"]
        self.assertEqual(writes, [], "the scorer edited the module it is scoring")

    def test_the_guard_bites_on_a_module_that_does_mutate(self):
        """L15: the plant must bite. A synthetic scorer that writes into `BS` must fail the check
        the real one passes."""
        src = 'import blindscreen as BS\ndef repair():\n    BS.CHEAP = ()\n'
        tree = ast.parse(src)
        writes = [t for n in ast.walk(tree) if isinstance(n, ast.Assign) for t in n.targets
                  if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                  and t.value.id == "BS"]
        self.assertEqual(len(writes), 1, "the structural check cannot see a mutation")


class TheDiagnosisIsReportedBesideTheVerdict(unittest.TestCase):
    def test_the_survivor_is_in_the_state_the_fifth_witness_was_in(self):
        surv, topological, missed_corpus, needed_hand = \
            BA.the_survivor_is_in_the_state_the_fifth_witness_WAS_in()
        self.assertEqual(surv, ("largest_free_component",))
        self.assertTrue(topological, "the survivor is topological, as the fifth witness was")
        self.assertTrue(missed_corpus, "free_components also had no corpus witness")
        self.assertTrue(needed_hand, "and also needed a construction")

    def test_the_candidate_level_predictions_were_scored_too(self):
        rows = BA.the_candidate_level_predictions_were_also_scored()
        self.assertEqual(len(rows), 4)
        surprises = [r[0] for r in rows if not r[3]]
        self.assertEqual(surprises, ["euler_characteristic"],
                         "the canonical lattice valuation violates inclusion-exclusion here")
        euler = next(r for r in BA.census() if r[0] == "euler_characteristic")
        self.assertGreater(euler[6], 0, "and the violation count must be positive, not assumed")

    def test_the_two_connectivity_halves_of_b5_still_hold(self):
        """B5 missed on the survivor, not on connectivity — reported so the miss is not over-read."""
        _dec, conn = BA.decisiveness()
        self.assertTrue(conn, "connectivity no longer separates the pair")
        _cheap, _dear, orders_agree = BS.cheapness_is_not_soundness()
        self.assertFalse(orders_agree, "the cost and decisiveness orders converged")


class TheRegistrationDischarges(unittest.TestCase):
    def test_this_module_is_the_derived_discharger(self):
        """The discharge is DERIVED from a cross-module call to the registrar's own accessor, so the
        same call scores the record and proves it was scored."""
        import disposition as DP
        self.assertEqual(DP.dischargers().get("blindscreen"), ("blindabsolute",))
        self.assertEqual(DP.REGISTER["blindscreen"][0], DP.STATE_DISCHARGED)
        self.assertEqual(DP.in_flight_records(), ())
        self.assertEqual(DP.debt_records(), ("voxstrip",))

    def test_a_registrar_still_cannot_score_itself(self):
        import disposition as DP
        self.assertNotEqual(DP.REGISTER["blindscreen"][1], "blindscreen")
        self.assertEqual(DP.a_registrar_cannot_score_itself(), (True, False, True))


if __name__ == "__main__":
    unittest.main()
