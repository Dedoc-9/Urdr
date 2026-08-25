# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxevent (URDRVXE1) — the subdivision ladder, the degeneracy families, and the tie convention."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxevent as VE                                        # noqa: E402
import voxray as VX                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheLadderIsAnInstrument(unittest.TestCase):
    def test_the_subdivision_moves_no_point(self):
        self.assertTrue(VE.the_subdivision_moves_no_point())

    def test_a_shifted_subdivision_is_caught(self):
        self.assertTrue(VE.a_shifted_subdivision_is_caught())

    def test_the_lever_is_the_declared_size(self):
        self.assertTrue(VE.the_primitive_ladder_is_exact())
        self.assertEqual(VE.solid_cells(8), VE.solid_cells(1) * 512)

    def test_the_extent_is_unchanged_by_the_scale(self):
        """Halving the cell while doubling the lattice is the same world, not a bigger one."""
        for s in VE.SCALES:
            n, q = VE.lattice(s)
            self.assertEqual(n * q, VR.N * VR.Q)

    def test_an_undeclared_scale_refuses(self):
        with self.assertRaises(VE.VoxeventError):
            VE.lattice(3)

    def test_the_parameters_compare_by_value_not_by_representation(self):
        """`first_hit` returns UNREDUCED rationals, so the same parameter differs as a tuple at a
        different cell size. The first version of the ladder probe was wrong in exactly this way."""
        _n, eye, fwd = VR.TRACE[4]
        d = VX.ray_for_pixel(eye, fwd, VR.W // 2, VR.H // 2)
        a = VX.first_hit(eye, d, None, VE.ORIGIN)
        n, q = VE.lattice(4)
        b = VX.first_hit(eye, d, VE.occupancy(4), VE.ORIGIN, n, q)
        self.assertNotEqual(a[2], b[2])
        self.assertTrue(VE._teq(a[2], b[2]))


class TheMeasurement(unittest.TestCase):
    def test_the_ordering_holds_at_every_scale(self):
        self.assertTrue(VE.the_ordering_holds_at_every_scale())

    def test_the_first_rung_is_flat(self):
        self.assertTrue(VE.the_first_rung_is_flat())

    def test_the_confound_is_declared_not_hidden(self):
        """The far end of the ladder measures the sampler; that is a row, not a footnote."""
        self.assertTrue(VE.the_census_is_censored_by_the_sampler())

    def test_the_rays_are_the_same_rays_at_every_scale(self):
        lad = VE.ladder()
        self.assertEqual(len({lad[s]["hits"] for s in VE.SCALES}), 1)

    def test_the_merge_relation_bites_in_both_directions(self):
        self.assertTrue(VE.a_relation_that_merges_nothing_is_not_this_one())


class TheDegeneracies(unittest.TestCase):
    def test_every_family_meets_its_prediction(self):
        self.assertEqual(VE.failing_degeneracies(), [])

    def test_a_wrong_corner_count_is_caught(self):
        self.assertTrue(VE.a_wrong_corner_count_is_caught())

    def test_the_families_are_visible_before_they_are_counted(self):
        """A count over an empty visible set would pass any prediction that expected zero."""
        for d in VE.DEGENERACIES:
            self.assertGreater(len(VE.degeneracy_reading(d)[0]), 0, d["name"])

    def test_an_unknown_family_refuses(self):
        with self.assertRaises(VE.VoxeventError):
            VE.degeneracy("nope")


class TheTieConvention(unittest.TestCase):
    def test_the_tiebreak_is_the_declared_convention(self):
        self.assertTrue(VE.the_tiebreak_is_the_declared_convention())

    def test_the_losing_candidate_is_not_merely_relabelled(self):
        """It is never entered — so the convention decides reachability, not naming."""
        self.assertTrue(VE.a_broken_tie_misses_the_other_candidate())

    def test_the_population_is_not_empty(self):
        """A convention nothing exercises would be a smaller problem; this one governs a fifth of
        the rays at the finest scale."""
        lad = VE.ladder()
        self.assertGreater(lad[8]["simultaneous"], 0)
        self.assertGreater(lad[8]["simultaneous"], lad[1]["simultaneous"])


class TheRecord(unittest.TestCase):
    def test_the_record_is_exactly_the_derived_grid(self):
        self.assertTrue(VE.the_record_is_exactly_the_derived_grid())

    def test_the_record_names_this_world(self):
        self.assertTrue(VE.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VE.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VE.a_tampered_row_refuses())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VE.SCENES:
            self.assertEqual(VE.scene_result(name), VE.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VE.VoxeventError):
            VE.scene_case("nope")


if __name__ == "__main__":
    unittest.main()
