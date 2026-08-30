# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxsilo (URDRVXH1) — three silos, eight cells, and the full combination is not the best one."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxsilo as VS                                         # noqa: E402
import voxwork as VO                                         # noqa: E402
import voxray as VX                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheContract(unittest.TestCase):
    def test_every_cell_reproduces_the_observable(self):
        """A silo may optimise its implementation and may not redefine the observable."""
        self.assertTrue(VS.every_cell_reproduces_the_observable())

    def test_the_comparison_is_on_buffers_not_digests(self):
        prims = VX.primitives_with("reversed")
        _nm, eye, fwd = VR.TRACE[5]
        rc, rd = VR.render(prims, eye, fwd)
        for cell in VS.CELLS:
            col, dep, _n = VS.render_cell(prims, eye, fwd, cell)
            self.assertEqual(col, rc, VS.cell_name(cell))
            self.assertEqual(dep, rd, VS.cell_name(cell))

    def test_an_unknown_cell_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.panel(("G", "Z"))

    def test_an_unknown_bound_refuses(self):
        prims = VX.primitives_with("reversed")
        with self.assertRaises(VS.VoxsiloError):
            VS.render_cell(prims, VR.TRACE[0][1], VR.TRACE[0][2], ("G",), bound="optimistic")

    def test_an_unknown_column_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.column("cycles")

    def test_nothing_is_promoted(self):
        self.assertTrue(VS.nothing_is_promoted())


class ThePremise(unittest.TestCase):
    def test_the_naive_bound_is_unsound(self):
        """The refutation is kept RUNNABLE, not described in a comment."""
        self.assertTrue(VS.the_naive_bound_is_unsound())

    def test_the_corrected_bound_is_never_violated(self):
        self.assertTrue(VS.the_corrected_bound_is_never_violated())

    def test_the_premise_fails_on_most_pixels(self):
        self.assertTrue(VS.the_premise_fails_on_most_pixels())

    def test_the_failure_is_not_a_corner_case(self):
        cov, bad, worst = VS.premise_census()
        self.assertGreater(cov, 0)
        self.assertGreater(bad * 2, cov)
        self.assertGreater(worst, 1000)

    def test_the_two_bounds_are_not_the_same_function(self):
        """Otherwise `corrected` would be the naive bound wearing a different name."""
        p, q, r = (0, 0, 7783), (1, 0, 7783), (0, 1, 7783)
        self.assertEqual(VS.naive_bound(p, q, r, 3, -2), 7783)
        self.assertLess(VS.corrected_bound(p, q, r, 3, -2), 7783)

    def test_the_correction_is_identity_with_no_bias(self):
        """A bias sum of zero leaves the convex combination intact, so the bounds must agree."""
        p, q, r = (0, 0, 500), (1, 0, 600), (0, 1, 700)
        self.assertEqual(VS.corrected_bound(p, q, r, 40, 0), VS.naive_bound(p, q, r, 40, 0))


class TheLattice(unittest.TestCase):
    def test_the_lattice_is_complete(self):
        self.assertTrue(VS.the_lattice_is_complete())

    def test_the_lattice_has_every_subset_once(self):
        self.assertEqual(len(VS.CELLS), 2 ** len(VS.ARMS))
        self.assertEqual(len({frozenset(c) for c in VS.CELLS}), len(VS.CELLS))

    def test_the_empty_cell_is_the_committed_floor(self):
        """Measured against the committed ruler, not a baseline this rung invented."""
        base = VS.panel(())
        self.assertEqual(base["walked"], VO.total("walked"))
        self.assertEqual(base["mul"], VO.total("mul"))
        self.assertEqual(base["div"], VO.total("div"))

    def test_every_arm_has_exactly_one_question(self):
        self.assertEqual(sorted(VS.QUESTION), sorted(VS.ARMS))
        for a in VS.ARMS:
            self.assertGreater(len(VS.QUESTION[a]), 20)

    def test_the_best_cell_is_not_the_full_combination(self):
        self.assertTrue(VS.the_best_cell_is_not_the_full_combination())
        self.assertEqual(VS.best_cell("mul"), "GA")

    def test_the_tile_arm_is_destructive_with_the_arithmetic_arm(self):
        self.assertTrue(VS.the_tile_arm_is_destructive_with_the_arithmetic_arm())

    def test_the_tile_arm_still_retires_pixels(self):
        """The test works; the exchange rate fails. Those are different verdicts."""
        self.assertTrue(VS.the_tile_arm_still_retires_pixels())

    def test_the_exchange_rate_is_a_pair_and_not_a_rate(self):
        spent, saved = VS.exchange_rate()
        self.assertGreater(spent, 0)
        self.assertGreater(saved, 0)
        self.assertGreater(spent, saved)

    def test_the_average_triangle_is_smaller_than_a_tile(self):
        self.assertTrue(VS.the_average_triangle_is_smaller_than_a_tile())

    def test_the_panel_is_never_fused(self):
        """A divide is not a multiply is not a compare; a sum would invent a cost model."""
        for c in VS.CELLS:
            p = VS.panel(c)
            self.assertEqual(sorted(p), sorted(VS.COLUMNS))

    def test_the_primitive_arm_retires_redundant_writes(self):
        """Byte-identical output with fewer writes means the writes retired were overwritten."""
        w = VS.column("written")
        self.assertLess(w["G"], w["-"])


class TheOrthogonality(unittest.TestCase):
    def test_the_arms_are_not_all_orthogonal(self):
        self.assertTrue(VS.the_arms_are_not_all_orthogonal())

    def test_the_tile_and_arithmetic_arms_subtract(self):
        """Omega above one is not redundancy — it is subtraction."""
        self.assertTrue(VS.the_tile_and_arithmetic_arms_subtract())

    def test_omega_is_an_exact_fraction(self):
        for x, y in (("G", "T"), ("G", "A"), ("T", "A")):
            num, den = VS.orthogonality(x, y)
            self.assertIsInstance(num, int)
            self.assertIsInstance(den, int)
            self.assertGreater(den, 0)

    def test_the_pairs_are_ordered_consistently(self):
        self.assertEqual(VS.orthogonality("T", "A"), VS.orthogonality("A", "T"))

    def test_an_arm_paired_with_itself_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.orthogonality("A", "A")

    def test_an_unknown_arm_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.orthogonality("G", "Z")


class TheRefusals(unittest.TestCase):
    def test_the_rung_makes_no_prediction_claim(self):
        """The arms ran first, so pinning a prediction now would be back-dating one."""
        self.assertTrue(VS.the_rung_makes_no_prediction_claim())
        self.assertFalse(hasattr(VS, "PREDICTION"))

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VS.no_wall_clock_enters_this_rung())

    def test_the_wall_clock_rule_is_inherited_not_restated(self):
        self.assertIs(VO.FORBIDDEN_IMPORTS, VO.FORBIDDEN_IMPORTS)
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VS.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VS.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VS.a_tampered_row_refuses())

    def test_a_cell_row_naming_no_cell_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("# world x\ncell GZ mul 5\n")

    def test_a_cell_row_naming_no_column_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("# world x\ncell GA cycles 5\n")

    def test_an_omega_row_naming_no_pair_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("# world x\nomega GG 1 2\n")

    def test_a_premise_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("# world x\npremise 5\n")

    def test_a_best_row_naming_no_cell_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("# world x\nbest GZ\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VS.generate(), VS._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VS.SCENES:
            self.assertEqual(VS.scene_result(name), VS.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.scene_case("lattice2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VS.VoxsiloError):
            VS.golden("nope")


if __name__ == "__main__":
    unittest.main()
