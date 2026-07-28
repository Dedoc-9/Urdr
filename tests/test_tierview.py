# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/tierview.py — VISUAL ASYMMETRY (URDRTIR1), slice S6.

  ZERO BY CONSTRUCTION — the authoritative predicate takes no tier, so the defect is 0, not bounded.
  STRUCTURAL, NOT DISCIPLINARY — checked by signature, the way horn._honest_band is.
  THE PLANT BITES — a tier-reading authority path costs 1152 cells across the same census.
  LUMINANCE IS THE WRONG QUANTITY — refuted in both directions by construction.
  IT REFUSES — an asymmetric tier pair is an unequal game, not a warning.

Every test can go red (L5); the plant bites before any golden pins (L15)."""
import os
import sys
import unittest
from itertools import product

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import tierview as TV                                              # noqa: E402


class TheZeroDefect(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in TV.SCENES:
            self.assertEqual(TV.scene_result(n), TV.golden(n), n)
            self.assertEqual(TV.scene_result(n), TV.scene_result(n), n)

    def test_defect_is_zero_not_bounded(self):
        """Decided over every observer, both pinned walls, every ordered tier pair."""
        self.assertTrue(TV.defect_is_zero())
        self.assertEqual(TV.census(), 0)

    def test_zero_holds_pairwise_not_just_in_aggregate(self):
        """A total of zero could hide cancelling errors if the defect could be negative; it cannot,
        but the pairwise walk makes that independent of the counting."""
        occ = TV.walls()[0]
        for obs in product(range(TV.GRID), repeat=2):
            if obs in occ:
                continue
            for t1, t2 in product(TV.TIERS, repeat=2):
                self.assertEqual(TV.asymmetry(obs, occ, t1, t2), 0, f"{obs} {t1}/{t2}")

    def test_decoupling_is_structural(self):
        """The strongest form: the tier cannot reach the predicate through ANY argument."""
        self.assertTrue(TV.decoupling_is_structural())
        import inspect
        self.assertNotIn("tier", inspect.signature(TV.visible).parameters)


class ThePlantBites(unittest.TestCase):
    def test_a_tier_reading_authority_path_costs_cells(self):
        self.assertEqual(TV.plant_defect(), 1152)
        self.assertGreater(TV.plant_defect(), 0)
        self.assertEqual(TV.census(), 0, "the law must stay at zero beside it")

    def test_the_plant_is_refused_and_the_law_admitted(self):
        occ = TV.walls()[0]
        self.assertEqual(TV.adjudicate_pair((0, 0), occ, "low", "high")[0], TV.R_ADMIT)
        r, d = TV.adjudicate_pair((0, 0), occ, "low", "high", TV.GRID, TV._visible_by_tier)
        self.assertEqual(r, TV.R_ASYMMETRIC)
        self.assertGreater(d, 0)
        self.assertEqual(TV._REASON_NAME[TV.R_ASYMMETRIC], "TIERVIEW-ASYMMETRIC")


class TheWrongQuantity(unittest.TestCase):
    def test_luminance_fails_in_both_directions(self):
        """Large delta with zero asymmetry, and small delta with real asymmetry — so the measure is
        neither sound nor complete for the thing it claims to bound."""
        (tint_delta, tint_defect), (cull_delta, cull_defect) = \
            TV.luminance_delta_is_the_wrong_quantity()
        self.assertGreater(tint_delta, 0)
        self.assertEqual(tint_defect, 0, "a big pixel delta with no information asymmetry")
        self.assertLess(cull_delta, tint_delta)
        self.assertGreater(cull_defect, 0, "a small pixel delta with real information asymmetry")


class ThePredicate(unittest.TestCase):
    def test_occlusion_is_exact_integer(self):
        occ = frozenset({(2, 0)})
        self.assertFalse(TV.visible((0, 0), (4, 0), occ), "a wall between must occlude")
        self.assertTrue(TV.visible((0, 0), (4, 4), occ), "an unobstructed diagonal must not")
        self.assertTrue(TV.visible((0, 0), (2, 0), occ), "the target cell itself is not an occluder")

    def test_rejects_malformed_coordinates(self):
        for bad in ((0.0, 0), (0,), "ab", [0, 0]):
            with self.assertRaises(TV.TierviewError):
                TV.visible(bad if type(bad) is tuple else (0, 0),
                           (1, 1) if type(bad) is tuple else bad, frozenset())

    def test_walls_are_pinned(self):
        self.assertEqual(TV.walls(), TV.walls())


if __name__ == "__main__":
    unittest.main()
