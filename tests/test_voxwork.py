# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxwork (URDRVXO1) — the exact work floor, and a ruler proved not to move what it measures."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxwork as VO                                         # noqa: E402
import voxray as VX                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheRulerIsInert(unittest.TestCase):
    def test_the_observable_is_unmoved(self):
        """An observer that changes a byte of what it observes is not an observer."""
        self.assertTrue(VO.the_observable_is_unmoved())

    def test_the_comparison_is_on_buffers_not_digests(self):
        """A digest comparison would pass on two buffers that collide."""
        prims = VX.primitives_with("reversed")
        _nm, eye, fwd = VR.TRACE[5]
        col, dep, _n = VO.instrument(prims, eye, fwd)
        rc, rd = VR.render(prims, eye, fwd)
        self.assertIsInstance(col, list)
        self.assertIsInstance(dep, list)
        self.assertEqual(len(col), VR.W * VR.H)
        self.assertEqual(col, rc)
        self.assertEqual(dep, rd)

    def test_the_buffers_are_not_trivially_equal(self):
        """Two all-background buffers would satisfy the binding and prove nothing."""
        prims = VX.primitives_with("reversed")
        col, dep, _n = VO.instrument(prims, VR.TRACE[5][1], VR.TRACE[5][2])
        self.assertGreater(len({*col}), 1)
        self.assertGreater(len({*dep}), 1)

    def test_nothing_is_optimised(self):
        self.assertTrue(VO.nothing_is_optimised())


class TheWalk(unittest.TestCase):
    def test_the_fates_partition_the_walk(self):
        self.assertTrue(VO.the_fates_partition_the_walk())

    def test_the_walk_model_equals_the_run(self):
        """Model == execution. A cost model only ever compared to itself is a formula."""
        self.assertTrue(VO.the_walk_model_equals_the_run())

    def test_the_walk_model_is_computed_without_the_inner_loop(self):
        """Otherwise the model would be the run wearing a different name."""
        model = VO.walk_model()
        self.assertEqual(len(model), len(VR.TRACE))
        self.assertTrue(all(m > 0 for m in model))

    def test_the_overdraw_is_the_headline(self):
        self.assertTrue(VO.the_overdraw_is_the_headline())

    def test_the_overdraw_is_a_pair_and_not_a_ratio(self):
        w, out = VO.overdraw()
        self.assertIsInstance(w, int)
        self.assertIsInstance(out, int)
        self.assertEqual(out, len(VR.TRACE) * VR.W * VR.H)

    def test_the_two_losses_are_of_different_kinds(self):
        self.assertTrue(VO.most_of_the_walk_is_outside_the_triangle())
        self.assertTrue(VO.most_of_the_coverage_loses_the_depth_test())

    def test_the_losses_are_never_summed(self):
        """They have different remedies, so a single wasted-work number would hide the difference."""
        p = VO.fates()
        self.assertEqual(set(p), set(VO.FATES))
        self.assertGreater(p["outside"], 0)
        self.assertGreater(p["beaten"], 0)
        self.assertGreater(p["written"], 0)

    def test_every_frame_has_its_own_partition(self):
        for f in range(len(VR.TRACE)):
            p = VO.fates(f)
            self.assertEqual(sum(p.values()), VO.census()[f][2]["walked"])

    def test_a_frame_outside_the_trace_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.fates(len(VR.TRACE))


class TheArithmetic(unittest.TestCase):
    def test_the_arithmetic_model_equals_the_run(self):
        self.assertTrue(VO.the_arithmetic_model_equals_the_run())

    def test_the_inner_loop_dominates_but_the_setup_is_not_negligible(self):
        """The first draft of this law claimed three quarters and reddened. It is 71%."""
        self.assertTrue(VO.the_inner_loop_dominates_but_the_setup_is_not_negligible())

    def test_the_split_sums_to_the_total(self):
        setup, inner = VO.arithmetic_split()
        self.assertEqual(setup + inner, VO.total("mul"))

    def test_the_setup_is_more_than_a_fifth(self):
        setup, _inner = VO.arithmetic_split()
        self.assertGreater(setup * 5, VO.total("mul"))

    def test_the_basis_multiply_is_paid_before_anything_is_known(self):
        """It runs for every quad including the ones the near test then throws away."""
        rejected = VO.total("near_rejected")
        self.assertGreater(rejected, 0)
        self.assertEqual(VO.MUL_PER_QUAD * VO.total("primitives"),
                         VO.MUL_PER_QUAD * (VO.total("primitives") - rejected)
                         + VO.MUL_PER_QUAD * rejected)

    def test_the_triangles_are_two_per_surviving_quad(self):
        self.assertTrue(VO.the_triangles_are_two_per_surviving_quad())

    def test_an_unknown_counter_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.total("cycles")


class TheStopwatchStaysOutside(unittest.TestCase):
    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VO.no_wall_clock_enters_this_rung())

    def test_the_wall_clock_law_can_bite(self):
        """A law with an empty live population cannot be told from one that cannot look."""
        self.assertTrue(VO.the_wall_clock_law_can_bite())

    def test_the_forbidden_set_is_not_empty(self):
        self.assertGreater(len(VO.FORBIDDEN_IMPORTS), 0)
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VO.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VO.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VO.a_tampered_row_refuses())

    def test_a_count_row_naming_no_counter_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.parse("# world x\ncount 0 seam cycles 5\n")

    def test_a_fate_row_naming_no_fate_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.parse("# world x\nfate wasted 5\n")

    def test_a_walk_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.parse("# world x\nwalk 5\n")

    def test_a_split_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.parse("# world x\nsplit 5\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VO.generate(), VO._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VO.SCENES:
            self.assertEqual(VO.scene_result(name), VO.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.scene_case("census2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VO.VoxworkError):
            VO.golden("nope")


if __name__ == "__main__":
    unittest.main()
