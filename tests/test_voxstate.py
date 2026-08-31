# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxstate (URDRVXU1) — a state lattice, and four ways to walk it. No certificate is built."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxstate as VT                                        # noqa: E402
import voxcond as VD                                         # noqa: E402
import voxwork as VO                                         # noqa: E402
import voxref as VR                                          # noqa: E402


class TheLattice(unittest.TestCase):
    def test_the_shape_is_declared_and_full(self):
        self.assertEqual(len(VT.STATES), VT.SHAPE[0] * VT.SHAPE[1])
        self.assertEqual(len(VT.AXES), 2)

    def test_every_state_is_distinct(self):
        """A state the observable cannot tell from another is a state bought and not paid for."""
        self.assertTrue(VT.every_state_is_distinct())

    def test_the_world_admits_no_third_axis(self):
        self.assertTrue(VT.the_world_admits_no_third_axis())

    def test_adjacency_is_one_step_on_one_axis(self):
        self.assertTrue(VT.adjacent(VT.INDEX[(0, 0)], VT.INDEX[(0, 1)]))
        self.assertTrue(VT.adjacent(VT.INDEX[(0, 0)], VT.INDEX[(1, 0)]))
        self.assertFalse(VT.adjacent(VT.INDEX[(0, 0)], VT.INDEX[(1, 1)]))
        self.assertFalse(VT.adjacent(VT.INDEX[(0, 0)], VT.INDEX[(0, 2)]))

    def test_a_state_outside_the_lattice_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.state(len(VT.STATES))

    def test_the_anchor_sits_in_the_declared_corridor(self):
        self.assertEqual(VT.ANCHOR_EYE[0] // VR.Q, VT.STATES[0][1][0] // VR.Q)


class TheOrders(unittest.TestCase):
    def test_the_orders_are_permutations_of_one_lattice(self):
        """No traversal may win by visiting a different or smaller lattice."""
        self.assertTrue(VT.the_orders_are_permutations_of_one_lattice())

    def test_the_baseline_inherits_nothing(self):
        self.assertTrue(VT.the_baseline_inherits_nothing())

    def test_the_other_orders_inherit_everywhere_but_the_first(self):
        self.assertTrue(VT.the_other_orders_inherit_everywhere_but_the_first())

    def test_the_zigzag_is_always_adjacent_and_the_scan_is_not(self):
        """The control the next rung depends on."""
        self.assertTrue(VT.the_zigzag_is_always_adjacent_and_the_scan_is_not())
        self.assertEqual(VT.nonadjacent_inheritances("Z2"), 0)
        self.assertEqual(VT.nonadjacent_inheritances("Z3"), 0)
        self.assertGreater(VT.nonadjacent_inheritances("Z1"), 0)

    def test_the_zigzag_reverses_alternate_rows(self):
        seq = VT.order("Z2")[0]
        rows, cols = VT.SHAPE
        self.assertEqual(seq[:cols], tuple(VT.INDEX[(0, j)] for j in range(cols)))
        self.assertEqual(seq[cols:2 * cols],
                         tuple(VT.INDEX[(1, j)] for j in range(cols - 1, -1, -1)))

    def test_the_breadth_first_order_starts_at_the_anchor(self):
        self.assertEqual(VT.order("Z3")[0][0], VT.INDEX[(0, 0)])

    def test_an_unknown_order_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.order("Z9")

    def test_an_order_that_inherits_nothing_has_no_span(self):
        with self.assertRaises(VT.VoxstateError):
            VT.order_span("Z0")


class TheGeometry(unittest.TestCase):
    def test_the_observable_distance_is_saturated(self):
        """The first draft of this law asked the wrong question and reddened."""
        self.assertTrue(VT.the_observable_distance_is_saturated())

    def test_a_quarter_voxel_already_changes_most_of_the_frame(self):
        lo, hi, n = VT.adjacent_span()
        self.assertGreater(lo * 5, 3 * n)
        self.assertLess(hi, n)

    def test_the_traversals_are_alike_in_distance_and_differ_in_structure(self):
        self.assertTrue(VT.the_traversals_are_alike_in_distance_and_differ_in_structure())

    def test_distance_counts_both_halves_of_the_observable(self):
        """voxpath's definition: a pixel survives only if colour AND depth do."""
        a, b = VT.adjacent_pairs()[0]
        fa, fb = VT.frames()[a], VT.frames()[b]
        colour_only = sum(1 for x, y in zip(fa[0], fb[0]) if x != y)
        self.assertGreaterEqual(VT.distance(a, b), colour_only)

    def test_every_adjacent_pair_is_measured(self):
        rows, cols = VT.SHAPE
        self.assertEqual(len(VT.adjacent_pairs()),
                         rows * (cols - 1) + cols * (rows - 1))


class TheDeadFamily(unittest.TestCase):
    def test_adjacency_is_not_a_validity_claim(self):
        """voxcond's refutations are RUN here, not cited."""
        self.assertTrue(VT.adjacency_is_not_a_validity_claim())

    def test_the_refuted_predicates_are_still_refuted(self):
        for p in ("P2", "P3", "P5"):
            self.assertFalse(VD.sound(p))

    def test_no_certificate_is_built(self):
        self.assertTrue(VT.no_certificate_is_built())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VT.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class ThePreRegistration(unittest.TestCase):
    def test_the_prediction_ships_before_the_traversals(self):
        self.assertTrue(VT.the_prediction_ships_before_the_traversals())

    def test_the_prediction_names_no_result(self):
        self.assertTrue(VT.the_prediction_names_no_result())

    def test_the_prediction_declares_five(self):
        t = VT.prediction_text()
        self.assertEqual(sum(1 for ln in t.split("\n") if ln.startswith("predict ")), 5)

    def test_the_prediction_digest_is_pinned(self):
        self.assertEqual(VT.prediction_digest(), VT.golden("prediction"))


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VT.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VT.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VT.a_tampered_row_refuses())

    def test_a_walk_row_naming_no_order_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.parse("# world x\nwalk Z9 0 1 2 3\n")

    def test_a_near_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.parse("# world x\nnear 1 2\n")

    def test_a_span_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.parse("# world x\nspan 5\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VT.generate(), VT._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VT.SCENES:
            self.assertEqual(VT.scene_result(name), VT.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.scene_case("lattice2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VT.VoxstateError):
            VT.golden("nope")


if __name__ == "__main__":
    unittest.main()
