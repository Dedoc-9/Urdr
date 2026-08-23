# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcoarse (URDRVXC1) — how coarse the frozen observable is, measured before anything leans on it."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxcoarse as VC                                       # noqa: E402


class TheRecord(unittest.TestCase):
    def test_it_is_exactly_the_declared_lattice(self):
        self.assertTrue(VC.the_record_is_exactly_the_declared_lattice())

    def test_it_names_this_world(self):
        self.assertTrue(VC.the_record_names_this_world())

    def test_it_is_bound_to_the_live_renderer(self):
        self.assertTrue(VC.the_record_is_bound_to_the_live_renderer())

    def test_a_dropped_row_reddens_the_lattice_law(self):
        self.assertTrue(VC.a_dropped_row_reddens_the_lattice_law())

    def test_a_moved_state_reddens_the_lattice_law(self):
        self.assertTrue(VC.a_moved_state_reddens_the_lattice_law())

    def test_a_short_row_refuses(self):
        self.assertTrue(VC.a_short_row_refuses())

    def test_a_record_without_a_world_refuses(self):
        self.assertTrue(VC.a_record_without_a_world_refuses())

    def test_a_flipped_digest_breaks_the_binding(self):
        self.assertTrue(VC.a_flipped_digest_breaks_the_binding())


class TheCensus(unittest.TestCase):
    def test_it_is_not_vacuous_in_either_direction(self):
        self.assertTrue(VC.the_census_is_not_vacuous())

    def test_state_equality_is_not_observable_equality(self):
        self.assertTrue(VC.a_state_difference_is_not_an_observable_difference())

    def test_the_largest_fibre_is_the_empty_view(self):
        self.assertTrue(VC.the_largest_fibre_is_the_empty_view())

    def test_the_empty_observable_is_derived_not_read_off_the_data(self):
        """Rendering nothing gives the category by construction; taking the biggest fibre and
        calling it 'empty' would be reading the answer off the data."""
        import voxref as VR
        self.assertEqual(VC.empty_observable(),
                         VR.observable(*VR.render([], (0, 0, 0), (1, 0, 0))))

    def test_excluding_the_empty_view_leaves_a_live_census(self):
        self.assertTrue(VC.excluding_the_empty_view_leaves_a_live_census())

    def test_the_state_count_tracks_the_filter(self):
        """The denominator must move with the numerator. It did not at first: `states` was
        `len(rows)` under both censuses, so the collided ratio read 3.9% instead of 11.3%."""
        whole = VC.census()
        seeing = VC.census(exclude_empty=True)
        self.assertEqual(whole[0], len(VC.lattice()))
        self.assertLess(seeing[0], whole[0])
        self.assertEqual(whole[0] - seeing[0], whole[3])

    def test_the_witnesses_re_render(self):
        self.assertTrue(VC.the_witnesses_re_render())

    def test_a_collision_carries_its_states(self):
        for _obs, members, states in VC.collision_witnesses(3):
            self.assertGreater(len(members), 1)
            self.assertNotEqual(states[0], states[1])


class TheGoldens(unittest.TestCase):
    def test_both_scenes_reproduce_their_goldens(self):
        for name in ("census", "witnesses"):
            self.assertEqual(VC.scene_result(name), VC.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VC.VoxcoarseError):
            VC.scene_case("nope")


if __name__ == "__main__":
    unittest.main()
