# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcam (URDRVXB1) — the candidate that works, and it is still not the reference."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxcam as VB                                          # noqa: E402
import voxcand as VC                                         # noqa: E402
import voxray as VX                                          # noqa: E402
import voxsample as VA                                       # noqa: E402
import voxwin as VW                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheSingleVariable(unittest.TestCase):
    def test_the_arms_differ_only_by_the_shift(self):
        self.assertTrue(VB.the_arms_differ_only_by_the_shift())

    def test_the_near_plane_is_the_same_plane(self):
        self.assertTrue(VB.the_near_plane_is_the_same_plane())

    def test_the_near_constants_are_not_the_same_number(self):
        """Otherwise `the same plane` would be true because nothing was re-expressed."""
        self.assertEqual(VB.near_of("candidate"), VB.near_of("control") << VB.SHIFT)
        self.assertNotEqual(VB.near_of("candidate"), VB.near_of("control"))

    def test_the_arms_really_do_differ(self):
        """A single-variable arm that moved nothing would pass every law here vacuously."""
        eye, fwd = VR.TRACE[5][1], VR.TRACE[5][2]
        m = VR.basis(fwd)
        v = (3 * VR.Q, 4 * VR.Q, 5 * VR.Q)
        self.assertNotEqual(VB.camera(v, eye, m, "control"), VB.camera(v, eye, m, "candidate"))

    def test_an_unknown_arm_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.camera((0, 0, 0), (0, 0, 0), VR.basis(VR.TRACE[0][2]), "float")

    def test_an_unknown_arm_has_no_near_plane(self):
        with self.assertRaises(VB.VoxcamError):
            VB.near_of("float")

    def test_an_unknown_arm_has_no_reading(self):
        with self.assertRaises(VB.VoxcamError):
            VB.reading("float")

    def test_the_control_is_the_reference_projection_itself(self):
        """The rung is only about `voxref._project` if the control IS what that function computes —
        asserted against the committed function rather than against a re-typed copy of its body."""
        self.assertEqual(VB.SHIFT, 16)
        for f in (0, 3, 5, 7):
            _nm, eye, fwd = VR.TRACE[f]
            m = VR.basis(fwd)
            for v in ((0, 0, 0), (3 * VR.Q, 4 * VR.Q, 5 * VR.Q), (-9 * VR.Q, VR.Q, 2 * VR.Q)):
                self.assertEqual(VB.camera(v, eye, m, "control"), VR._project(v, eye, m))


class TheBinding(unittest.TestCase):
    def test_the_control_arm_matches_the_ladder(self):
        """A candidate measured against a stranger measures nothing."""
        self.assertTrue(VB.the_control_arm_matches_the_ladder())

    def test_the_control_arm_gains_and_loses_nothing(self):
        r = VB.reading("control")
        self.assertEqual((r[2], r[3], r[4]), (0, 0, 0))

    def test_the_populations_are_inherited_and_not_restated(self):
        self.assertEqual(len(VB.population("on_surface")), 215)
        self.assertEqual(len(VB.population("sub_pixel")), 103)
        self.assertEqual(len(VB.population("winner_miss")), 56)
        self.assertEqual(len(VB.population("tie")), 2)
        self.assertEqual(len(VB.population("phantom")), 2)

    def test_the_populations_are_disjoint_from_the_ties(self):
        for name in ("on_surface", "sub_pixel", "winner_miss"):
            self.assertEqual(VB.population(name) & VB.population("tie"), set())

    def test_an_unknown_population_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.population("elsewhere")


class TheVerdicts(unittest.TestCase):
    def test_every_prediction_has_a_verdict(self):
        self.assertTrue(VB.every_prediction_has_a_verdict())

    def test_the_record_carries_hits_and_misses(self):
        self.assertTrue(VB.the_record_carries_hits_and_misses())

    def test_the_prediction_is_pinned_as_data(self):
        self.assertIsInstance(VB.PREDICTION, tuple)
        self.assertEqual(len(VB.PREDICTION), 5)
        for pid, text in VB.PREDICTION:
            self.assertTrue(pid.startswith("C"))
            self.assertGreater(len(text), 40)

    def test_the_verdicts_are_computed_from_the_arm(self):
        """Not from the prediction's own text, which would score itself."""
        self.assertEqual(set(VB.hits()) | set(VB.misses()), {p for p, _t in VB.PREDICTION})
        self.assertEqual(set(VB.hits()) & set(VB.misses()), set())

    def test_the_miss_is_the_tie_prediction(self):
        self.assertEqual(VB.misses(), ("C5",))


class TheWin(unittest.TestCase):
    def test_the_candidate_wins_on_evidence(self):
        self.assertTrue(VB.the_candidate_wins_on_evidence())

    def test_gained_and_lost_are_carried_separately(self):
        c = VB.reading("candidate")
        self.assertGreater(c[2], 0)
        self.assertGreater(c[3], 0)
        self.assertNotEqual(c[2] - c[3], c[2])

    def test_the_impossible_count_falls(self):
        self.assertLess(VB.reading("candidate")[1], VB.reading("control")[1])

    def test_the_changed_population_is_not_the_whole_frame(self):
        """A change touching every pixel would be a different renderer, not one variable."""
        self.assertLess(VB.reading("candidate")[4], VR.W * VR.H // 8)


class TheResidue(unittest.TestCase):
    def test_the_survivors_are_named_not_rounded(self):
        self.assertTrue(VB.the_survivors_are_named_not_rounded())

    def test_the_phantoms_are_not_swallowed(self):
        self.assertTrue(VB.the_phantoms_are_not_swallowed())

    def test_the_tie_pixels_keep_their_geometry(self):
        """The ties close as a DEPTH tie; `voxwin`'s world-space edge crossing is undisturbed."""
        self.assertTrue(VB.the_tie_pixels_keep_their_geometry())
        self.assertTrue(VW.the_exceptions_are_exactly_the_exact_ties())

    def test_the_survivors_sum_to_what_did_not_close(self):
        s, c = VB.survivors(), VB.reading("candidate")[5]
        for p in VB.POPULATIONS:
            self.assertEqual(s[p] + c[p], len(VB.population(p)))

    def test_nothing_is_promoted(self):
        self.assertTrue(VB.nothing_is_promoted())

    def test_the_reference_still_truncates(self):
        """`nothing_is_promoted` must be about THIS shift, so the shift must still be there."""
        self.assertTrue(VC.the_committed_reference_is_untouched())
        self.assertTrue(VA.nothing_is_altered())


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VB.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VB.the_record_is_bound_to_the_live_code())

    def test_the_record_carries_the_prediction_text(self):
        self.assertTrue(VB.the_record_carries_the_prediction_text())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VB.a_tampered_row_refuses())

    def test_a_verdict_row_naming_no_prediction_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.parse("# world x\nverdict C9 HIT nothing\n")

    def test_an_arm_row_naming_no_arm_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.parse("# world x\narm float 1 2 3 4 5\n")

    def test_a_closed_row_naming_no_population_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.parse("# world x\nclosed candidate elsewhere 3\n")

    def test_a_survivor_row_naming_no_population_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.parse("# world x\nsurvivor elsewhere 3\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VB.generate(), VB._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VB.SCENES:
            self.assertEqual(VB.scene_result(name), VB.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.scene_case("arms2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VB.VoxcamError):
            VB.golden("nope")


if __name__ == "__main__":
    unittest.main()
