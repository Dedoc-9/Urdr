# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxmanifold (URDRVXV1) — does certificate validity have structure? Yes on locality, no on the
manifold."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxmanifold as VM                                     # noqa: E402
import voxstate as VT                                        # noqa: E402
import voxcond as VD                                         # noqa: E402
import voxwork as VO                                         # noqa: E402


class ThePreRegistration(unittest.TestCase):
    def test_the_prediction_is_quoted_from_the_earlier_commit(self):
        self.assertTrue(VM.the_prediction_is_quoted_from_the_earlier_commit())

    def test_the_verdicts_match_the_committed_prediction(self):
        self.assertTrue(VM.the_verdicts_match_the_committed_prediction())

    def test_the_record_carries_hits_and_misses(self):
        self.assertTrue(VM.the_record_carries_hits_and_misses())

    def test_three_predictions_missed(self):
        self.assertEqual(VM.hits(), ("M2", "M3"))
        self.assertEqual(VM.misses(), ("M1", "M4", "M5"))

    def test_the_predictions_are_parsed_not_restated(self):
        self.assertEqual(VM.PREDICTIONS, tuple(sorted(VM.committed_prediction())))


class TheContract(unittest.TestCase):
    def test_every_traversal_reproduces_the_cold_baseline(self):
        self.assertTrue(VM.every_traversal_reproduces_the_cold_baseline())

    def test_each_state_inherits_only_from_its_declared_predecessor(self):
        """The cold-start control: a warm cache would show up as a mismatched operation count."""
        self.assertTrue(VM.each_state_inherits_only_from_its_declared_predecessor())

    def test_nothing_but_the_owner_map_crosses_between_states(self):
        col, dep, key, ex, cert, ch = VM.render_state(0, None)
        self.assertEqual(cert, 0)
        self.assertEqual(ch, 0)
        self.assertGreater(ex, 0)

    def test_an_unknown_order_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.run("Z9")

    def test_nothing_is_promoted(self):
        self.assertTrue(VM.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VM.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class TheLocalityThatSurvives(unittest.TestCase):
    def test_retirement_rises_with_inheritance_quality(self):
        self.assertGreater(VM.retired("Z2"), VM.retired("Z1"))
        self.assertGreaterEqual(VM.retired("Z3"), VM.retired("Z2"))

    def test_the_nearest_neighbour_order_nearly_doubles_the_scan_order(self):
        self.assertGreater(VM.retired("Z3") * 2, VM.retired("Z1") * 3)

    def test_the_cold_baseline_retires_nothing(self):
        self.assertEqual(VM.retired("Z0"), 0)
        self.assertEqual(VM.run("Z0")[2], 0)


class TheManifoldThatDies(unittest.TestCase):
    def test_adjacency_helps_but_not_categorically(self):
        a, nb, na, nn = VM.certified_by_adjacency()
        self.assertGreater(a * nn, nb * na)
        self.assertLess(a * nn, nb * na * 2)

    def test_every_state_is_a_validity_boundary(self):
        """There is no cheap interior for a boundary scheme to be cheap around."""
        self.assertEqual(len(VM.boundary_states()), len(VT.STATES))

    def test_no_intermediate_state_contributes_reusable_structure(self):
        sub = VM.subadditivity()
        self.assertEqual(len(sub), 24)
        self.assertEqual(sum(1 for d in sub.values() if d < 0), 0)

    def test_the_detour_always_costs_more(self):
        for (a, b, c), d in VM.subadditivity().items():
            self.assertGreater(d, 0, (a, b, c))


class TheBaselines(unittest.TestCase):
    def test_the_ambiguity_in_my_own_prediction_is_disclosed(self):
        self.assertTrue(VM.the_ambiguity_in_my_own_prediction_is_disclosed())

    def test_the_reference_is_measured_on_this_lattice(self):
        """The first draft compared against voxcond's 31-frame figure — a different workload."""
        self.assertGreater(VM.reference_cost(), 0)
        self.assertNotEqual(VM.reference_cost(), VD.tiling_overhead()[1])

    def test_the_scaffolding_reproduces_voxconds_ratio(self):
        z0, ref = VM.run("Z0")[1], VM.reference_cost()
        self.assertGreater(z0 * 100, ref * 180)
        self.assertLess(z0 * 100, ref * 190)

    def test_even_the_best_traversal_loses_to_the_reference(self):
        self.assertGreater(VM.run("Z3")[1], VM.reference_cost())


class ThePathsThatCarryNoVerdict(unittest.TestCase):
    def test_the_path_results_carry_no_verdict(self):
        self.assertTrue(VM.the_path_results_carry_no_verdict())

    def test_the_paths_visit_the_same_states(self):
        for p in VM.PATHS:
            self.assertEqual(sorted(p), sorted(VM.CORNER))

    def test_two_paths_are_entirely_adjacent_and_two_are_not(self):
        adj = []
        for p in VM.PATHS:
            steps = [VT.adjacent(VM.corner_index(p[i]), VM.corner_index(p[i + 1]))
                     for i in range(3)]
            adj.append(all(steps))
        self.assertEqual(sorted(adj), [False, False, True, True])

    def test_an_unknown_path_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.path_cost("DCBA")

    def test_an_unknown_corner_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.corner_index("Z")


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VM.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VM.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VM.a_tampered_row_refuses())

    def test_an_order_row_naming_no_order_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.parse("# world x\norder Z9 1 2 3 4\n")

    def test_a_verdict_row_naming_no_prediction_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.parse("# world x\nverdict M9 HIT nothing\n")

    def test_a_path_row_naming_no_path_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.parse("# world x\npath DCBA 5\n")

    def test_a_delta_row_naming_no_triple_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.parse("# world x\ndelta AZQ 5\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VM.generate(), VM._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VM.SCENES:
            self.assertEqual(VM.scene_result(name), VM.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.scene_case("orders2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VM.VoxmanifoldError):
            VM.golden("nope")


if __name__ == "__main__":
    unittest.main()
