# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxpath (URDRVXJ1) — a second declared trace, because the first one cannot answer the question."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxpath as VP                                         # noqa: E402
import voxwork as VO                                         # noqa: E402
import voxref as VR                                          # noqa: E402


class ThePath(unittest.TestCase):
    def test_every_episode_is_present_and_nonempty(self):
        self.assertTrue(VP.the_every_episode_is_present_and_nonempty())

    def test_the_path_is_continuous_except_where_declared(self):
        self.assertTrue(VP.the_path_is_continuous_except_where_declared())

    def test_exactly_one_step_exceeds_the_bound(self):
        lim = VP.MAX_STEP * VP.MAX_STEP
        over = [i for i in range(1, len(VP.PATH)) if VP.step(i) > lim]
        self.assertEqual(over, [VP.TELEPORT_AT])

    def test_the_only_turning_episodes_are_the_turns(self):
        self.assertTrue(VP.the_only_turning_episodes_are_the_turns())
        self.assertEqual(VP.turning_episodes(), ("pan", "whip"))

    def test_the_whip_turns_further_than_the_pan(self):
        self.assertTrue(VP.the_whip_turns_further_than_the_pan())

    def test_the_eye_never_enters_matter(self):
        """voxref.TRACE already owns the buried case; blank frames would flatter every figure."""
        self.assertTrue(VP.the_eye_never_enters_matter())

    def test_no_two_consecutive_frames_are_indistinguishable(self):
        """The same standard voxref holds its own trace to."""
        self.assertTrue(VP.no_two_consecutive_frames_are_indistinguishable())

    def test_an_unknown_episode_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.episode("strafe")

    def test_the_path_is_longer_than_the_old_trace(self):
        self.assertGreater(len(VP.PATH), len(VR.TRACE))

    def test_the_path_is_not_the_old_trace(self):
        self.assertTrue(VP.the_path_is_not_the_old_trace())


class TheControls(unittest.TestCase):
    def test_the_still_episode_changes_nothing(self):
        self.assertTrue(VP.the_still_episode_changes_nothing())

    def test_the_teleport_changes_almost_everything(self):
        self.assertTrue(VP.the_teleport_changes_almost_everything())

    def test_the_two_controls_are_at_opposite_ends(self):
        lo, hi, n = VP.episode_coherence("still")
        tel = [r for r in VP.coherence() if r[0] == VP.TELEPORT_AT][0]
        self.assertEqual((lo, hi), (n, n))
        self.assertLess(tel[2] * 10, n)


class TheHeadline(unittest.TestCase):
    def test_the_exact_observable_loses_coherence_the_colour_half_keeps_it(self):
        """Depth is a continuous function of camera position and O_t contains it exactly."""
        self.assertTrue(VP.the_exact_observable_loses_coherence_the_colour_half_keeps_it())

    def test_the_creep_gap_is_large(self):
        p = VP.episode_coherence("creep")
        c = VP.episode_colour("creep")
        self.assertGreater(c[0], 6 * p[0])

    def test_the_colour_figure_is_an_upper_bound_on_ownership(self):
        self.assertTrue(VP.the_colour_figure_is_an_upper_bound_on_ownership())

    def test_the_pair_is_why_colour_alone_would_lie(self):
        self.assertTrue(VP.the_pair_is_why_colour_alone_would_lie())

    def test_the_hard_episodes_are_hard(self):
        self.assertTrue(VP.the_hard_episodes_are_hard())

    def test_the_new_path_carries_colour_coherence_the_old_trace_does_not(self):
        self.assertTrue(VP.the_new_path_carries_colour_coherence_the_old_trace_does_not())

    def test_the_comparison_excludes_the_degenerate_pair(self):
        """Quoting a pair the observable cannot tell apart would be quoting an artefact."""
        b, c, n = VP.old_trace_best_distinguishable()
        self.assertLess(b, n)
        self.assertLess(c, n)

    def test_an_episode_with_no_interior_pair_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.episode_colour("nonesuch")


class TheWinding(unittest.TestCase):
    def test_the_reversed_winding_collapses_a_declared_case(self):
        self.assertTrue(VP.the_reversed_winding_collapses_a_declared_case())

    def test_the_committed_law_still_holds(self):
        """The finding is scoped: the reference's own distinctness law is RUN, not merely cited."""
        self.assertTrue(VP.the_committed_law_still_holds())
        self.assertTrue(VR.every_declared_case_is_distinct())

    def test_the_census_names_both_windings(self):
        a, b, n = VP.winding_distinctness()
        self.assertEqual(a, n)
        self.assertEqual(b, n - 1)

    def test_the_old_trace_is_untouched(self):
        self.assertTrue(VP.the_old_trace_is_untouched())


class ThePreRegistration(unittest.TestCase):
    def test_the_prediction_ships_before_the_arms(self):
        self.assertTrue(VP.the_prediction_ships_before_the_arms())

    def test_the_prediction_names_no_result(self):
        """A pre-registration that already contained its answer would not be one."""
        self.assertTrue(VP.the_prediction_names_no_result())

    def test_the_prediction_declares_five_of_each(self):
        t = VP.prediction_text()
        self.assertEqual(sum(1 for ln in t.split("\n") if ln.startswith("predicate ")), 5)
        self.assertEqual(sum(1 for ln in t.split("\n") if ln.startswith("predict ")), 5)

    def test_the_prediction_digest_is_pinned(self):
        self.assertEqual(VP.prediction_digest(), VP.golden("prediction"))

    def test_no_certificate_is_built(self):
        self.assertTrue(VP.no_certificate_is_built())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VP.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VP.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VP.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VP.a_tampered_row_refuses())

    def test_a_frame_row_naming_no_episode_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.parse("# world x\nframe 0 strafe s 1,2,3 0,1,0\n")

    def test_a_pair_row_naming_no_episode_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.parse("# world x\npair 1 strafe 5 10\n")

    def test_a_colour_row_naming_no_episode_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.parse("# world x\ncolour strafe 1 2 3\n")

    def test_a_winding_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.parse("# world x\nwinding 8\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VP.generate(), VP._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VP.SCENES:
            self.assertEqual(VP.scene_result(name), VP.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.scene_case("path2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VP.VoxpathError):
            VP.golden("nope")


if __name__ == "__main__":
    unittest.main()
