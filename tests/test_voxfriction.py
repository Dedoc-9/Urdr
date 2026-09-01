# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxfriction (URDRVXY1) — can a probe cheaper than the work it avoids tell when to bother?"""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxfriction as VF                                     # noqa: E402
import voxmanifold as VM                                     # noqa: E402
import voxcond as VD                                         # noqa: E402
import voxwork as VO                                         # noqa: E402


class TheProbe(unittest.TestCase):
    def test_the_probe_reads_only_what_the_certificate_already_reads(self):
        """The first draft of this law compared costs; the two are not alternatives."""
        self.assertTrue(VF.the_probe_reads_only_what_the_certificate_already_reads())

    def test_the_probe_returns_both_signals(self):
        prev = [0] * (VM.VR.W * VM.VR.H) if hasattr(VM, "VR") else None
        owners, longest, ops = VF.probe([7] * (96 * 72), 0, 7, 0, 7)
        self.assertEqual(owners, 1)
        self.assertEqual(longest, 8)
        self.assertEqual(ops, 64)

    def test_the_probe_sees_many_owners_when_there_are_many(self):
        buf = [i % 5 for i in range(96 * 72)]
        owners, longest, ops = VF.probe(buf, 0, 7, 0, 7)
        self.assertGreater(owners, 1)
        self.assertEqual(longest, 1)

    def test_the_tile_is_inherited_from_voxcond(self):
        self.assertEqual(VF.TILE, VD.TILE)


class TheSurface(unittest.TestCase):
    def test_the_payoff_surface_has_a_crossover(self):
        self.assertTrue(VF.the_payoff_surface_has_a_crossover())

    def test_the_cheap_tiles_are_the_ones_that_pay(self):
        """A probe reading a signal that does not order the outcome is a coin toss with a cost."""
        self.assertTrue(VF.the_cheap_tiles_are_the_ones_that_pay())

    def test_the_transition_is_sharp(self):
        s = VF.by_owner()
        for b in (1, 2, 3):
            self.assertGreater(s[b][2], 0, b)
        for b in (4, 6, 9):
            self.assertLess(s[b][2], 0, b)

    def test_the_certificate_stops_firing_entirely_past_the_cutoff(self):
        s = VF.by_owner()
        for b in (4, 6, 9):
            self.assertEqual(s[b][1], 0, b)
        self.assertGreater(sum(s[b][0] for b in (4, 6, 9)), 100)

    def test_single_owner_tiles_carry_most_of_the_value(self):
        s = VF.by_owner()
        total = sum(v[2] for v in s.values())
        self.assertGreater(s[1][2] * 10, total * 9)

    def test_the_run_signal_is_monotone_the_other_way(self):
        r = VF.by_run()
        self.assertGreater(r[8][2], r[4][2])
        self.assertGreater(r[4][2], r[2][2])

    def test_the_cutoff_and_crossover_are_reported(self):
        self.assertEqual(VF.cutoff(VF.by_owner()), 3)
        self.assertIsNotNone(VF.crossover(VF.by_owner()))

    def test_every_payoff_has_its_population_beside_it(self):
        for b, v in VF.by_owner().items():
            self.assertEqual(len(v), 3)
            self.assertGreaterEqual(v[0], v[1])


class TheCounterfactual(unittest.TestCase):
    def test_the_payoff_is_a_counterfactual_and_it_was_run(self):
        """voxcond shipped exactly this defect once, counting a retirement it never took."""
        self.assertTrue(VF.the_payoff_is_a_counterfactual_and_it_was_run())

    def test_this_rung_is_a_diagnostic_not_an_implementation(self):
        self.assertTrue(VF.this_rung_is_a_diagnostic_not_an_implementation())

    def test_every_certified_tile_has_a_full_raster_measurement(self):
        for r in VF.census():
            if r[8]:
                self.assertGreater(r[7], 0)

    def test_a_declined_tile_pays_only_probe_and_check(self):
        for r in VF.census():
            if not r[8] and r[2] > 0:
                self.assertEqual(VF.payoff(r), -(r[4] + r[5]))
                break


class TheAsymmetry(unittest.TestCase):
    def test_declining_can_never_change_the_observable(self):
        """A wrong decision either way costs performance and never correctness."""
        self.assertTrue(VF.declining_can_never_change_the_observable())

    def test_both_degenerate_limits_are_run(self):
        self.assertEqual(sorted(VF.LIMITS), ["always", "never"])
        for n in VF.LIMITS:
            self.assertTrue(VF.limit_frames(n))

    def test_an_unknown_limit_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.limit_frames("sometimes")


class TheRefusals(unittest.TestCase):
    def test_the_rung_makes_no_prediction_claim(self):
        """Picking a threshold after seeing the curve and scoring it would be fitting."""
        self.assertTrue(VF.the_rung_makes_no_prediction_claim())
        self.assertFalse(hasattr(VF, "PREDICTION"))

    def test_nothing_is_promoted(self):
        self.assertTrue(VF.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VF.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VF.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VF.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VF.a_tampered_row_refuses())

    def test_an_owner_row_naming_no_bucket_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.parse("# world x\nowner 7 1 2 3\n")

    def test_a_run_row_naming_no_bucket_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.parse("# world x\nrun 3 1 2 3\n")

    def test_a_cost_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.parse("# world x\ncost 5\n")

    def test_a_cut_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.parse("# world x\ncut 5\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VF.generate(), VF._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VF.SCENES:
            self.assertEqual(VF.scene_result(name), VF.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.scene_case("surface2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VF.VoxfrictionError):
            VF.golden("nope")


if __name__ == "__main__":
    unittest.main()
