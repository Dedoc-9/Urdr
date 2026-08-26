# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxtie (URDRVXT1) — defect or event surface, decided by limits rather than by counting."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxtie as VT                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheLadder(unittest.TestCase):
    def test_level_zero_is_the_candidate_arm(self):
        """The chain from voxref.render through two transcriptions stays bound."""
        self.assertTrue(VT.the_ladder_starts_at_the_candidate())

    def test_each_level_changes_one_thing(self):
        seen = set()
        for _n, sym, s in VT.LEVELS:
            seen.add((sym, s))
        self.assertEqual(len(seen), len(VT.LEVELS))

    def test_an_undeclared_level_refuses(self):
        with self.assertRaises(VT.VoxtieError):
            VT.level("subpixel8")

    def test_the_subpixel_floor_is_measured_not_assumed(self):
        """1/256 must buy nothing meaningful over 1/64, or 'the floor' would be a guess."""
        a = VT.level_reading("subpixel64", frame=4)
        b = VT.level_reading("subpixel256", frame=4)
        self.assertLess(abs(a[1] - b[1]), 20)


class TheClassifier(unittest.TestCase):
    def test_every_class_is_reachable(self):
        self.assertTrue(VT.every_class_is_reachable())

    def test_a_genuine_defect_is_found(self):
        """A classifier that called everything a boundary would manufacture the carve-out."""
        self.assertTrue(VT.the_classifier_finds_a_genuine_defect())

    def test_the_carve_out_is_refused_by_the_trace(self):
        self.assertTrue(VT.the_carve_out_is_refused_by_the_trace())

    def test_the_oracle_never_gives_an_isolated_answer(self):
        """No ABA anywhere: the exact value always equals one of the two sides."""
        self.assertTrue(VT.the_oracle_never_gives_an_isolated_answer())

    def test_stable_impossible_pixels_dominate_boundary_ones(self):
        s = VT.census_summary()
        self.assertGreater(s["stable"][1], s["boundary"][1])

    def test_the_classes_partition_the_residual(self):
        s = VT.census_summary()
        self.assertEqual(sum(s[c][0] for c in VT.CLASSES), len(VT.census()))


class TheTiePopulation(unittest.TestCase):
    def test_the_resolvable_ceiling_bounds_every_rule(self):
        self.assertTrue(VT.no_tie_rule_can_beat_the_resolvable_ceiling())

    def test_the_committed_rule_is_below_the_ceiling(self):
        """Arbitrary AND worse than available — which is what makes the proposal bounded."""
        self.assertTrue(VT.the_committed_rule_leaves_the_ceiling_unreached())

    def test_every_rule_preserves_draw_order_independence(self):
        self.assertTrue(VT.every_rule_is_order_independent())

    def test_no_rule_is_adopted(self):
        self.assertTrue(VT.no_rule_is_adopted())

    def test_an_unknown_rule_refuses(self):
        with self.assertRaises(VT.VoxtieError):
            VT.rule_pick("coin_flip", (0, 0, 0), (1, 1, 1), [])

    def test_every_tie_has_at_least_two_candidates(self):
        for _px, _py, cands, _o, _c, _d in VT.tie_population():
            self.assertGreaterEqual(len(cands), 2)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VT.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VT.the_record_is_bound_to_the_live_code())

    def test_the_population_is_pinned_not_the_count(self):
        self.assertTrue(VT.the_population_is_pinned_not_the_count())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VT.a_tampered_row_refuses())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VT.SCENES:
            self.assertEqual(VT.scene_result(name), VT.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VT.VoxtieError):
            VT.scene_case("nope")


if __name__ == "__main__":
    unittest.main()
