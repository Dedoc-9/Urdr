# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/divergence.py — THE QUANTIZATION DEFECT (URDRDVG1), slice S2.

  RATE IS BLIND — same rate 2/35, run 1 vs 2, breached False vs True. The rate cannot see the only
    thing that matters, which is why it is not the measurand.
  THE RUN IS THE PRECONDITION — the minimum breaching run equals the wall thickness exactly.
  THE MAXIMUM IS ATTAINED — over every k-subset the largest run is exactly k. Decided, not sampled.
  THE MODEL IS DECLARED — adversarial choice, not Gaussian, and bounded in both directions.

Every test can go red (L5); the rate plant bites before any golden pins (L15)."""
import os
import sys
import unittest
from itertools import combinations

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import divergence as DV                                            # noqa: E402


class TheRateIsBlind(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in DV.SCENES:
            self.assertEqual(DV.scene_result(n), DV.golden(n), n)
            self.assertEqual(DV.scene_result(n), DV.scene_result(n), n)

    def test_same_rate_different_run_and_different_consequence(self):
        """The refutation, stated so it can be false."""
        (ra, run_a, breach_a), (rb, run_b, breach_b) = DV.rate_is_blind()
        self.assertEqual(ra, rb, "the rates must be IDENTICAL or the refutation is not about rate")
        self.assertNotEqual(run_a, run_b, "and the runs must differ")
        self.assertFalse(breach_a, "scattered holes leave the wall standing")
        self.assertTrue(breach_b, "aligned holes open it")
        self.assertTrue(DV.rate_equal_run_differs())

    def test_the_rate_plant_conflates_them(self):
        """L15 — the handed-down measure assigns the same defect to both."""
        self.assertTrue(DV.rate_plant_conflates_them())
        gt = DV.wall()
        a = DV.perturb(gt, [(DV.WALL_X, 0), (DV.WALL_X + 1, 2)])
        b = DV.perturb(gt, [(DV.WALL_X, 0), (DV.WALL_X + 1, 0)])
        self.assertEqual(DV._defect_by_rate(gt, a), DV._defect_by_rate(gt, b))
        self.assertNotEqual(DV.largest_run(gt, a), DV.largest_run(gt, b))
        self.assertNotEqual(DV.breached(a), DV.breached(b))


class TheRunIsThePrecondition(unittest.TestCase):
    def test_a_breach_needs_a_run_at_least_as_deep_as_the_wall(self):
        """Not a proxy for the harm — the harm's precondition, which is what makes it the right
        measurand rather than a convenient one."""
        min_run, thick = DV.breach_needs_a_run_of_at_least_thickness()
        self.assertEqual(thick, DV.THICK)
        self.assertGreaterEqual(min_run, thick)
        self.assertEqual((min_run, thick), (2, 2))

    def test_a_one_cell_wall_would_have_refuted_this(self):
        """The first draft's scene, kept as a live check: at thickness 1 any single hole breaches, so
        run length and traversability are unrelated and the metric would only be describing."""
        thin = frozenset((DV.WALL_X, y) for y in range(DV.H))
        holed = DV.perturb(thin, [(DV.WALL_X, 0)])
        self.assertEqual(DV.largest_run(thin, holed), 1)
        self.assertTrue(DV.breached(holed), "one hole in a one-cell wall is already a breach")
        self.assertGreater(DV.THICK, 1, "so the pinned scene must be thicker than one")

    def test_breach_census_is_non_vacuous(self):
        """The vacuity law: a census where nothing breaches would prove nothing about breaching."""
        breach, total = DV.breach_census()
        self.assertEqual((breach, total), (155, 6545))
        self.assertGreater(breach, 0, "some perturbation must actually breach")
        self.assertLess(breach, total, "and some must not")


class TheAttainedMaximum(unittest.TestCase):
    def test_worst_run_is_exactly_k_and_is_attained(self):
        """Decided by enumeration over every k-subset — a bound, not an estimate."""
        self.assertTrue(DV.worst_run_is_k())
        self.assertEqual(DV.worst_run_table(), ((1, 1), (2, 2), (3, 3)))

    def test_worst_run_is_monotone_in_k(self):
        rows = DV.worst_run_table()
        for (_k0, r0), (_k1, r1) in zip(rows, rows[1:]):
            self.assertLessEqual(r0, r1)

    def test_a_sampled_mean_would_understate_it(self):
        """Why the maximum and not the mean: most perturbations are scattered, so the mean run is
        well below the attained worst case the adversary can always reach."""
        gt = DV.wall()
        runs = [DV.largest_run(gt, DV.perturb(gt, f)) for f in combinations(DV.cells(), 3)]
        mean_num, mean_den = sum(runs), len(runs)
        self.assertLess(mean_num, 3 * mean_den, "the mean run is strictly below the worst case 3")
        self.assertEqual(max(runs), DV.worst_run(3))


class TheGuards(unittest.TestCase):
    def test_rejects_cells_outside_the_scene(self):
        for bad in ((99, 0), (0, 99), (-1, 0)):
            with self.assertRaises(DV.DivergenceError):
                DV.perturb(DV.wall(), [bad])

    def test_rejects_unpinned_perturbation_sizes(self):
        for bad in (0, 4, 99):
            with self.assertRaises(DV.DivergenceError):
                DV.worst_run(bad)

    def test_the_scene_is_pinned(self):
        self.assertEqual(DV.wall(), DV.wall())
        self.assertEqual(len(DV.wall()), DV.THICK * DV.H)


if __name__ == "__main__":
    unittest.main()
