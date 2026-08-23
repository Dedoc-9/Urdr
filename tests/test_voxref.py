# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxref (URDRVXF1) — rung zero of the voxel arc: the observable frozen before any reduction."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxref as V                                           # noqa: E402


class TheReference(unittest.TestCase):
    def test_it_is_deterministic(self):
        self.assertTrue(V.the_reference_is_deterministic())

    def test_it_draws_every_face_of_every_solid_voxel(self):
        n = sum(1 for x in range(V.N) for y in range(V.N) for z in range(V.N)
                if V.solid(x, y, z))
        self.assertEqual(len(V.primitives()), 6 * n)

    def test_the_world_is_neither_empty_nor_full(self):
        n = sum(1 for x in range(V.N) for y in range(V.N) for z in range(V.N)
                if V.solid(x, y, z))
        self.assertGreater(n, 0)
        self.assertLess(n, V.N ** 3)

    def test_a_camera_along_up_refuses(self):
        with self.assertRaises(V.VoxrefError):
            V.basis((0, 0, 1))

    def test_a_zero_forward_refuses(self):
        with self.assertRaises(V.VoxrefError):
            V.basis((0, 0, 0))


class TheCoveragePartition(unittest.TestCase):
    def test_no_pixel_of_a_quad_is_claimed_twice(self):
        self.assertTrue(V.the_coverage_is_a_partition())

    def test_the_sample_is_not_empty(self):
        self.assertGreater(V.partition_report()[1], 0)

    def test_a_cover_double_claims_on_the_same_sample(self):
        self.assertTrue(V.a_cover_double_claims_and_a_partition_does_not())
        self.assertGreater(V.cover_report()[0], 0)


class TheOrderIrrelevance(unittest.TestCase):
    def test_a_permutation_leaves_the_observable_alone(self):
        self.assertTrue(V.the_order_permutation_leaves_the_observable_alone())

    def test_the_permutations_really_permute(self):
        self.assertTrue(V.a_shuffled_order_is_a_real_shuffle())

    def test_the_corpus_contains_the_case_the_law_is_for(self):
        self.assertTrue(V.the_corpus_contains_coincident_faces())
        self.assertGreater(V._coincident_pairs(), 0)


class TheObservable(unittest.TestCase):
    def test_the_depth_digest_is_not_redundant(self):
        self.assertTrue(V.the_depth_digest_is_not_redundant())

    def test_the_witness_actually_renders_something(self):
        both, only = V.depth_witness()
        self.assertEqual(both[0], only[0])
        self.assertNotEqual(both[1], only[1])

    def test_every_declared_case_is_distinct(self):
        self.assertTrue(V.every_declared_case_is_distinct())

    def test_the_colour_digest_is_not_redundant(self):
        self.assertTrue(V.the_colour_digest_is_not_redundant())

    def test_the_colour_witness_actually_renders_something(self):
        a, b = V.colour_witness()
        self.assertEqual(a[1], b[1])
        self.assertNotEqual(a[0], b[0])

    def test_the_census_is_reported_and_never_required(self):
        """A FIRST VERSION OF THIS TEST ASSERTED THAT DEPTH SEPARATED FEWER FRAMES THAN COLOUR,
        which was true of one hash seed and false of the next. The census is REPORTED; what the
        gate requires is the two CONSTRUCTED witnesses, which no reseed can delete."""
        frames, distinct, dc, dz = V.coarseness()
        self.assertEqual(frames, len(V.TRACE))
        self.assertEqual(distinct, frames)
        self.assertLessEqual(dc, frames)
        self.assertLessEqual(dz, frames)


class TheGoldens(unittest.TestCase):
    def test_both_scenes_reproduce_their_goldens(self):
        for name in ("contract", "laws"):
            self.assertEqual(V.scene_result(name), V.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(V.VoxrefError):
            V.scene_case("nope")


if __name__ == "__main__":
    unittest.main()
