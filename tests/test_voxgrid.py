# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxgrid (URDRVXG1) — is the degeneracy the lattice or the sampling grid? Both, and the ladder separates them."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxgrid as VG                                         # noqa: E402
import voxevent as VE                                        # noqa: E402
import voxfill as VL                                         # noqa: E402
import voxref as VR                                          # noqa: E402


class TheRay(unittest.TestCase):
    def test_the_ray_is_the_declared_ray(self):
        self.assertTrue(VG.the_ray_is_the_declared_ray())

    def test_an_unknown_convention_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.ladder("gaussian")

    def test_an_undeclared_scale_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.artefact_share(3)

    def test_the_conventions_and_scales_are_inherited(self):
        self.assertIs(VG.CONVENTIONS, VL.CONVENTIONS)
        self.assertIs(VG.SCALES, VE.SCALES)


class TheBinding(unittest.TestCase):
    def test_the_corner_arm_reproduces_voxevent(self):
        """A re-derivation that cannot reproduce the census it re-derives measures something else."""
        self.assertTrue(VG.the_corner_arm_reproduces_voxevent())

    def test_every_scale_and_column_is_compared(self):
        mine, theirs = VG.ladder("corner"), VE.ladder()
        for s in VG.SCALES:
            for c in VG.COLUMNS:
                self.assertEqual(mine[s][c], theirs[s][c], (s, c))

    def test_the_columns_that_cannot_move_are_not_claimed(self):
        """solid_cells and primitives cannot depend on where a ray was aimed."""
        self.assertTrue(VG.the_columns_that_cannot_move_are_not_claimed())


class TheSeparation(unittest.TestCase):
    def test_the_degeneracy_separates_along_the_ladder(self):
        self.assertTrue(VG.the_degeneracy_separates_along_the_ladder())

    def test_the_base_lattice_is_almost_all_artefact(self):
        c, m = VG.artefact_share(VG.SCALES[0])
        self.assertGreater(c, 10 * m)

    def test_the_finest_scale_is_not(self):
        """The correction: voxconv's one-liner carried no scale, and the answer depends on it."""
        c, m = VG.artefact_share(VG.SCALES[-1])
        self.assertGreater(c, m)
        self.assertLess(c, 3 * m)

    def test_the_share_is_a_pair_and_not_a_ratio(self):
        for s in VG.SCALES:
            pair = VG.artefact_share(s)
            self.assertEqual(len(pair), 2)
            self.assertTrue(all(isinstance(v, int) for v in pair))


class TheSurvival(unittest.TestCase):
    def test_the_visible_surface_is_not_the_convention(self):
        self.assertTrue(VG.the_visible_surface_is_not_the_convention())

    def test_the_ray_budget_censoring_survives(self):
        """voxevent's sharpest structural result, untouched: hits identical at every scale."""
        self.assertTrue(VG.the_ray_budget_censoring_survives())

    def test_the_two_conventions_hit_different_totals(self):
        """Otherwise 'identical at every scale' would be trivially true of one number."""
        self.assertNotEqual(VG.ladder("corner")[1]["hits"], VG.ladder("centre")[1]["hits"])

    def test_nothing_is_adopted(self):
        self.assertTrue(VG.nothing_is_adopted())


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VG.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VG.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VG.a_tampered_row_refuses())

    def test_a_rung_row_outside_the_grid_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.parse("# world x\nrung gaussian 1 hits 5\n")

    def test_a_share_row_on_no_declared_scale_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.parse("# world x\nshare 3 1 2 of 4\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VG.SCENES:
            self.assertEqual(VG.scene_result(name), VG.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.scene_case("ladder2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VG.VoxgridError):
            VG.golden("nope")


if __name__ == "__main__":
    unittest.main()
