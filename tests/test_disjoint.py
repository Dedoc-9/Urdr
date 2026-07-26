# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/disjoint.py — STRUCTURAL COMMUTATION (URDRDSJ1), task 58 Half B.

  SOUNDNESS — prefix-disjoint implies commutes, decided over every pair of the pinned family.
  THE POLARITY — disjointness is lca_depth < level, NOT >= threshold. The inverted plant admits
    402 NON-COMMUTING pairs as safe, which is unsound in the direction that ships.
  NOT NECESSARY — ~80% of overlapping pairs commute anyway. Sound but incomplete, and the
    incompleteness is a measured number rather than an adjective.
  LEVEL MONOTONE — coarse disjointness implies fine disjointness, so the knob is safe upward.
  THE VACUOUS FAMILY — single-valued edits make every pair commute and prove nothing; conflict must
    be constructible or the census is theatre.

Every test can go red (L5); the inverted plant bites before any golden pins (L15)."""
import os
import sys
import unittest
from itertools import combinations, product

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import disjoint as D                                               # noqa: E402
import voxlat as VX                                                # noqa: E402


class TheTheorem(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in D.SCENES:
            self.assertEqual(D.scene_result(n), D.golden(n), n)
            self.assertEqual(D.scene_result(n), D.scene_result(n), n)

    def test_prefix_disjoint_implies_commutes(self):
        """THE THEOREM, decided over every pair — no sampling."""
        self.assertTrue(D.disjointness_is_sufficient())
        dn, dc, _on, _oc = D.census()
        self.assertEqual((dn, dc), (18144, 18144))
        self.assertEqual(D.law_admits_nothing_unsound(), 0)

    def test_sufficiency_holds_pairwise_not_just_in_aggregate(self):
        """The census is a count; this walks the pairs so a counting bug cannot hide a failure."""
        fam, wl = D.edit_family(), D.worlds()
        checked = 0
        for e1, e2 in combinations(fam[:120], 2):
            if D.prefix_disjoint(e1, e2):
                self.assertTrue(D.commutes(e1, e2, wl), f"{e1} / {e2}")
                checked += 1
        self.assertGreater(checked, 0, "the sample must contain disjoint pairs at all")


class ThePolarity(unittest.TestCase):
    """Third appearance of this inversion in the arc. It is a hazard class, not a slip."""

    def test_deep_common_ancestor_means_overlap_not_independence(self):
        a = VX.morton(0, 0, 0, D.LEVELS)
        b = VX.morton(0, 0, 1, D.LEVELS)          # adjacent — deep shared prefix
        c = VX.morton(3, 3, 3, D.LEVELS)          # far — diverges at the root
        self.assertGreater(VX.lca_depth(a, b, D.LEVELS), VX.lca_depth(a, c, D.LEVELS))
        self.assertEqual(D.prefix(a), D.prefix(b), "adjacent keys share a subtree")
        self.assertNotEqual(D.prefix(a), D.prefix(c), "distant keys do not")
        self.assertFalse(D.prefix_disjoint({a: 1}, {b: 0}), "shared subtree is NOT disjoint")
        self.assertTrue(D.prefix_disjoint({a: 1}, {c: 0}))

    def test_the_inverted_plant_is_unsound(self):
        """L15, and in the dangerous direction: it licenses replays across conflicting edits."""
        bad = D.inverted_predicate_is_unsound()
        self.assertEqual(bad, 402)
        self.assertGreater(bad, 0, "the inverted form must admit non-commuting pairs")
        self.assertEqual(D.law_admits_nothing_unsound(), 0, "the law must admit none")


class TheBoundary(unittest.TestCase):
    def test_sufficient_but_not_necessary(self):
        """Measured, not glossed: most overlapping pairs commute anyway."""
        on, oc = D.disjointness_is_not_necessary()
        self.assertEqual((on, oc), (47922, 38640))
        self.assertGreater(oc, 0, "an equivalence claim would be false")
        self.assertLess(oc, on, "and so would 'overlap implies conflict'")
        self.assertGreater(100 * oc // on, 75, "the incompleteness is large, not marginal")

    def test_the_split_is_a_strict_improvement(self):
        """Disjoint pairs become a proof; the rest fall through to the existing per-instance check
        exactly as before. Nothing is made worse."""
        structural, per_instance, total = D.split_of_the_work()
        self.assertEqual(structural + per_instance, total)
        self.assertGreater(structural, 0, "the structural path must actually carry work")
        self.assertGreater(per_instance, 0, "and the fall-through must remain populated")

    def test_level_is_a_safe_knob(self):
        """Coarse disjointness implies fine, so raising the level recovers precision and can never
        admit a pair the coarser level refused."""
        self.assertTrue(D.level_monotone())


class TheVacuousFamily(unittest.TestCase):
    def test_single_valued_edits_prove_nothing(self):
        """The first draft's mistake, kept as a test: with one value every pair commutes, so the
        census would 'confirm' any predicate at all — including the inverted one."""
        ks = D.keys()[:8]
        flat = [dict.fromkeys(p, 1) for p in combinations(ks, 2)]
        wl = D.worlds()
        self.assertTrue(all(D.commutes(e1, e2, wl) for e1, e2 in combinations(flat, 2)),
                        "single-valued edits commute unconditionally — a vacuous census")
        self.assertTrue(all(D._disjoint_by_lca_ge(e1, e2) is not None
                            for e1, e2 in combinations(flat[:10], 2)))

    def test_the_pinned_family_can_actually_conflict(self):
        """The fix: conflict has to be constructible or the measurement is theatre."""
        fam, wl = D.edit_family(), D.worlds()
        self.assertTrue(any(not D.commutes(e1, e2, wl)
                            for e1, e2 in combinations(fam[:200], 2)),
                        "the family must contain genuinely non-commuting pairs")

    def test_family_and_worlds_are_pinned(self):
        self.assertEqual(D.edit_family(), D.edit_family())
        self.assertEqual(D.worlds(), D.worlds())


class TheGuards(unittest.TestCase):
    def test_rejects_malformed_keys_and_levels(self):
        for bad in (-1, 1.0, "3"):
            with self.assertRaises(D.DisjointError):
                D.prefix(bad)
        for lvl in (-1, D.LEVELS + 1, 99):
            with self.assertRaises(D.DisjointError):
                D.prefix(0, lvl)

    def test_apply_is_last_writer_wins(self):
        w = {0: 0, 1: 0}
        self.assertEqual(D.apply(w, {0: 1}), {0: 1, 1: 0})
        self.assertEqual(D.apply(D.apply(w, {0: 1}), {0: 0}), {0: 0, 1: 0})
        self.assertEqual(w, {0: 0, 1: 0}, "apply must not mutate its input")


if __name__ == "__main__":
    unittest.main()
