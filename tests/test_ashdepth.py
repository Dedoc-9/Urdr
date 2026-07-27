# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/ashdepth.py — THE VACUITY FLOOR (URDRASH1).

  SOUNDNESS NEVER BREAKS — no level admits an unsound pair, not even the coarsest. A VOID IS SOUND.
  THE HANDED-DOWN BOUND IS VACUOUS — k* passes at maximum burn, licensing an empty fast path.
  k_min IS THE REAL FLOOR — the coarsest level that still distinguishes anything.
  THE TRIPWIRE FIRES — a corpus that distinguishes nothing RAISES rather than returning zero.
  FOUR VACUITY WITNESSES — the arc's characteristic failure, pinned as constants not memories.

Every test can go red (L5); the handed-down bound is refuted before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import ashdepth as AD                                              # noqa: E402


class TheInversion(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in AD.SCENES:
            self.assertEqual(AD.scene_result(n), AD.golden(n), n)
            self.assertEqual(AD.scene_result(n), AD.scene_result(n), n)

    def test_soundness_never_breaks_at_any_level(self):
        """A void is sound. Coarsening loses precision monotonically and correctness never."""
        self.assertTrue(AD.soundness_never_breaks())
        for _lv, _p, unsound, _t in AD.level_table():
            self.assertEqual(unsound, 0)

    def test_the_table_actually_distinguishes_levels(self):
        """The non-vacuity precondition on the census itself — this is the check whose absence
        nearly produced a false finding."""
        proved = [p for _lv, p, _u, _t in AD.level_table()]
        self.assertGreater(max(proved), 0, "the corpus must distinguish something")
        self.assertGreater(len(set(proved)), 1, "and the levels must differ from each other")

    def test_precision_is_monotone(self):
        self.assertTrue(AD.precision_is_monotone_in_level())


class TheFloor(unittest.TestCase):
    def test_k_min_is_the_coarsest_level_that_says_anything(self):
        floor = AD.k_min()
        self.assertEqual(floor, 1)
        rows = {lv: p for lv, p, _u, _t in AD.level_table()}
        self.assertGreater(rows[floor], 0)
        self.assertEqual(rows[floor - 1], 0, "one level coarser must be empty")

    def test_the_handed_down_bound_is_vacuous(self):
        """L15 — k* passes at maximum burn, licensing a fast path of size zero."""
        self.assertTrue(AD.handed_down_bound_is_vacuous())
        self.assertEqual(AD.handed_down_k_star(), 0)
        self.assertLess(AD.handed_down_k_star(), AD.k_min())

    def test_the_guard_refuses_below_the_floor(self):
        self.assertTrue(AD.guard_refuses_below_floor())
        fam = AD.spread_corpus()
        with self.assertRaises(AD.VacuityError):
            AD.guard(fam, 0)
        self.assertEqual(AD.guard(fam, 1), 1)

    def test_guard_rejects_levels_outside_the_lattice(self):
        for bad in (-1, 99):
            with self.assertRaises(AD.AshdepthError):
                AD.guard(AD.spread_corpus(), bad)


class TheTripwire(unittest.TestCase):
    def test_an_empty_corpus_raises_rather_than_returning_zero(self):
        """Silence must be loud. This is the hard asset."""
        self.assertTrue(AD.tripwire_fires_on_the_empty_corpus())
        with self.assertRaises(AD.VacuityError):
            AD.k_min(AD.EMPTY_CORPUS())

    def test_the_empty_corpus_is_empty_at_every_level_including_the_finest(self):
        """A first draft shared only a level-1 block, leaving the finest level non-empty and the
        tripwire silent — the vacuity asset was itself insufficiently vacuous."""
        for lv, proved, _u, _t in AD.level_table(AD.EMPTY_CORPUS()):
            self.assertEqual(proved, 0, f"level {lv} must be empty")


class TheFourWitnesses(unittest.TestCase):
    def test_all_four_vacuities_are_witnessed_not_remembered(self):
        w1, w2, w3, w4 = AD.vacuity_witnesses()
        self.assertTrue(w1, "single-valued edits: every pair commutes, confirms any predicate")
        self.assertTrue(w2, "singleton batches: no grouping occurs, unsound rule scores clean")
        self.assertTrue(w3, "all-levels-empty: distinguishes no levels")
        self.assertTrue(w4, "handed-down k*: passes at maximum burn")
        self.assertTrue(AD.all_four_vacuities_are_witnessed())

    def test_corpora_are_pinned(self):
        self.assertEqual(AD.spread_corpus(), AD.spread_corpus())
        self.assertEqual(AD.EMPTY_CORPUS(), AD.EMPTY_CORPUS())


if __name__ == "__main__":
    unittest.main()
