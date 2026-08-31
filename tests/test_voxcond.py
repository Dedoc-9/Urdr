# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcond (URDRVXQ1) — five conditional certificates, scored against a prediction committed first."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxcond as VC                                         # noqa: E402
import voxpath as VP                                         # noqa: E402
import voxsilo as VS                                         # noqa: E402
import voxwork as VO                                         # noqa: E402


class ThePreRegistration(unittest.TestCase):
    def test_the_prediction_is_quoted_from_the_earlier_commit(self):
        self.assertTrue(VC.the_prediction_is_quoted_from_the_earlier_commit())

    def test_the_predicates_are_parsed_and_not_restated(self):
        """A restatement is a copy, and a copy can drift."""
        preds, verds = VC.committed_prediction()
        self.assertEqual(tuple(sorted(preds)), VC.PREDICATES)
        self.assertEqual(tuple(sorted(verds)), VC.PREDICTIONS)
        self.assertEqual(len(VC.PREDICATES), 5)

    def test_the_verdicts_match_the_committed_prediction(self):
        self.assertTrue(VC.the_verdicts_match_the_committed_prediction())

    def test_the_digest_is_the_one_voxpath_pinned(self):
        self.assertEqual(VP.prediction_digest(), VP.golden("prediction"))

    def test_the_record_carries_hits_and_misses(self):
        self.assertTrue(VC.the_record_carries_hits_and_misses())

    def test_two_predictions_missed(self):
        """A pre-registration that landed all five would have been luck or hindsight."""
        self.assertEqual(VC.misses(), ("D4", "D5"))
        self.assertEqual(VC.hits(), ("D1", "D2", "D3"))


class TheContract(unittest.TestCase):
    def test_every_arm_is_checked_against_the_reference(self):
        self.assertTrue(VC.every_arm_is_checked_against_the_reference())

    def test_the_unsound_predicates_are_still_unsound(self):
        """A refutation that stops being executable stops being evidence."""
        self.assertTrue(VC.the_unsound_predicates_are_still_unsound())

    def test_the_unsound_predicates_fail_for_one_reason(self):
        """Each holds somewhere; none is failing merely by never firing."""
        self.assertTrue(VC.the_unsound_predicates_fail_for_one_reason())
        for p in ("P2", "P3", "P5"):
            self.assertGreater(VC.panel(p)["population"], 0)

    def test_the_only_sound_cheap_predicate_is_the_trivial_one(self):
        self.assertTrue(VC.the_only_sound_cheap_predicate_is_the_trivial_one())

    def test_an_unknown_predicate_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.panel("P9")

    def test_an_unknown_quantity_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.quantity("cycles")

    def test_the_first_frame_has_no_predecessor(self):
        with self.assertRaises(VC.VoxcondError):
            VC.holds("P1", 0)


class TheOwnershipCertificate(unittest.TestCase):
    def test_the_ownership_certificate_is_sound(self):
        self.assertTrue(VC.the_ownership_certificate_is_sound())

    def test_the_fast_path_is_actually_taken(self):
        """The guard against the defect this rung shipped in its first draft."""
        self.assertTrue(VC.the_fast_path_is_actually_taken())
        self.assertGreater(VC.panel("P4")["population"], 0)

    def test_the_certificate_wins_against_the_loop_it_sits_on(self):
        self.assertTrue(VC.the_certificate_wins_against_the_loop_it_sits_on())

    def test_the_loop_it_sits_on_loses_against_the_reference(self):
        """So the nineteen times can never be quoted alone."""
        self.assertTrue(VC.the_loop_it_sits_on_loses_against_the_reference())

    def test_the_overhead_is_a_pair_and_not_netted(self):
        tiled, ref = VC.tiling_overhead()
        self.assertGreater(tiled, ref)
        self.assertGreater(tiled - VC.panel("P4")["retired"], ref)

    def test_the_tile_is_inherited_from_voxsilo(self):
        """Two rungs that drifted into different tile sizes would both be measuring `the tile`."""
        self.assertEqual(VC.TILE, VS.TILE)

    def test_the_certificate_uses_the_corrected_bound(self):
        """The naive conservative bound is unsound and voxsilo proved it."""
        p, q, r = (0, 0, 7783), (1, 0, 7783), (0, 1, 7783)
        self.assertLess(VS.corrected_bound(p, q, r, 3, -2), VS.naive_bound(p, q, r, 3, -2))


class TheQuantities(unittest.TestCase):
    def test_three_quantities_are_carried_separately(self):
        for p in VC.PREDICATES:
            self.assertEqual(sorted(VC.panel(p)), sorted(VC.QUANTITIES))

    def test_the_trivial_predicate_is_nearly_free(self):
        p1 = VC.panel("P1")
        self.assertGreater(p1["retired"], 1000 * p1["cost"])

    def test_the_occupancy_predicate_is_expensive(self):
        """P5 must enumerate the world; its cost is reported rather than waved at."""
        self.assertGreater(VC.panel("P5")["cost"], 100 * VC.panel("P1")["cost"])

    def test_the_epsilon_is_declared_and_sub_voxel(self):
        self.assertEqual(VC.EPS, 32)
        self.assertLess(VC.EPS * 4, VC.Q)


class TheRefusals(unittest.TestCase):
    def test_nothing_is_promoted(self):
        self.assertTrue(VC.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VC.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VC.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VC.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VC.a_tampered_row_refuses())

    def test_an_arm_row_naming_no_predicate_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.parse("# world x\narm P9 SOUND 1 2 3\n")

    def test_a_verdict_row_naming_no_prediction_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.parse("# world x\nverdict D9 HIT nothing\n")

    def test_a_loop_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.parse("# world x\nloop 5\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VC.generate(), VC._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VC.SCENES:
            self.assertEqual(VC.scene_result(name), VC.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.scene_case("arms2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VC.VoxcondError):
            VC.golden("nope")


if __name__ == "__main__":
    unittest.main()
