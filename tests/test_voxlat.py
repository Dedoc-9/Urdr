# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/voxlat.py — THE INTEGER VOXEL LATTICE (URDRVOX1), slice S1.

  THE LCA IDENTITY — leading agreement, 7140/7140 against an independent brute-force oracle.
  THE ctz PLANT BITES — the 2-adic (trailing) form is wrong on the MAJORITY of pairs, not merely
    imprecise. It is the form a handed-down draft asserted, so it is pinned rather than deleted.
  THE ZERO CASE — a == b is where x86 BSF is UNDEFINED and __builtin_ctz(0) is UB. Closed explicitly.
  THE OVERFLOW THEOREM — max |n.u0| == 4*B^3 EXACTLY, decided exhaustively over every ordered triple.
  THE EXPONENT IS CUBIC — decided by exact integer comparison, and the quadratic estimate refuted.
  THE QUADRATIC PLANT BITES — it claims a 64-bit fit where the decided law needs 84.

Every test can go red (L5); both plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxlat as VX                                                # noqa: E402


class TheEncoding(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in VX.SCENES:
            self.assertEqual(VX.scene_result(n), VX.golden(n), n)
            self.assertEqual(VX.scene_result(n), VX.scene_result(n), n)

    def test_morton_is_a_bijection(self):
        self.assertTrue(VX.morton_is_bijective())
        for c in ((0, 0, 0), (1, 2, 3), (63, 0, 63), (63, 63, 63)):
            self.assertEqual(VX.unmorton(VX.morton(*c)), c)

    def test_hierarchy_lives_in_the_high_bits(self):
        """The mechanism behind the whole LCA correction: the root octant is the TOP group."""
        a = VX.morton(0, 0, 0)
        b = VX.morton(32, 0, 0)          # differs only in the most significant x bit
        self.assertEqual(VX.lca_depth(a, b), 0, "a root-level split must have depth 0")
        c = VX.morton(1, 0, 0)           # differs only in the least significant x bit
        self.assertEqual(VX.lca_depth(a, c), VX.LEVELS - 1, "a leaf sibling must be deepest")

    def test_rejects_out_of_lattice(self):
        for bad in ((-1, 0, 0), (64, 0, 0), (0, 0, 64), (1.0, 0, 0)):
            with self.assertRaises(VX.VoxlatError):
                VX.morton(*bad)


class TheLCAIdentity(unittest.TestCase):
    def test_identity_matches_the_oracle_on_every_pair(self):
        pairs, ok = VX.lca_census()
        self.assertEqual(pairs, VX.CORPUS * (VX.CORPUS - 1) // 2)
        self.assertEqual(ok, pairs, "the closed form must agree with the walk everywhere")

    def test_corpus_is_pinned_not_sampled(self):
        """A measured failure rate is only a constant if the corpus never moves."""
        self.assertEqual(VX.corpus(), VX.corpus())
        self.assertEqual(len(VX.corpus()), VX.CORPUS)

    def test_zero_case_is_closed_explicitly(self):
        """The case where x86 BSF is UNDEFINED and __builtin_ctz(0) is UB — and the commonest case
        in the world, a voxel compared with itself."""
        self.assertTrue(VX.zero_case_is_closed())
        for k in VX.corpus()[:8]:
            self.assertEqual(VX.lca_depth(k, k), VX.LEVELS)


class TheCtzPlantBites(unittest.TestCase):
    def test_trailing_form_is_wrong_on_most_pairs(self):
        """L15 — not merely imprecise. Wrong on the majority, and it is what a handed-down draft
        asserted, so the gate carries the refutation rather than a chat message."""
        pairs, ok = VX.lca_census(_impl=VX._lca_by_ctz)
        self.assertLess(ok, pairs // 2, "the ctz plant must fail on more than half the pairs")
        self.assertGreater(pairs - ok, 3000)

    def test_the_two_forms_disagree_on_a_named_witness(self):
        """The starkest case, and the one that shows the two forms read opposite ends of the word:
        two LEAF SIBLINGS differing only in the last z bit. True depth is 5 — they share every
        ancestor but the last. The leading form says 5; the trailing form says 0, i.e. that they
        diverge at the ROOT. It is not off by a little, it is inverted."""
        a, b = VX.morton(0, 0, 0), VX.morton(0, 0, 1)
        true = VX.lca_depth_bruteforce(a, b)
        self.assertEqual(true, VX.LEVELS - 1)
        self.assertEqual(VX.lca_depth(a, b), true)
        self.assertEqual(VX._lca_by_ctz(a, b), 0, "the plant reports root divergence for siblings")


class TheOverflowTheorem(unittest.TestCase):
    def test_attained_maximum_is_exactly_four_b_cubed(self):
        """DECIDED, not sampled: every ordered triple on each pinned lattice."""
        self.assertTrue(VX.law_is_four_b_cubed())
        for B in VX.PINNED_BOUNDS:
            self.assertEqual(VX.attained_max(B), 4 * B ** 3, f"B={B}")

    def test_exponent_is_cubic_by_exact_integer_comparison(self):
        """No regression, no float — m1*b0^3 == m0*b1^3 exactly."""
        self.assertTrue(VX.growth_is_cubic())

    def test_quadratic_growth_is_refuted(self):
        self.assertTrue(VX.quadratic_estimate_is_refuted())

    def test_analytic_bound_is_correct_but_loose(self):
        """192*B^3 is provable and 48x loose — which is why the constant had to be measured."""
        self.assertTrue(VX.analytic_bound_is_loose())
        for B in VX.PINNED_BOUNDS:
            self.assertEqual(192 * B ** 3 // VX.attained_max(B), 48)

    def test_the_plane_test_is_the_dominant_term(self):
        """The mechanism, not the observation: the nine edge tests are only quadratic, so a bound
        read off them alone gets the exponent wrong."""
        B = 3
        tr = []
        VX.tri_box_overlap((B, -B, B), (-B, B, -B), (B, B, -B), (0, 0, 0), (1, 1, 1), _trace=tr)
        self.assertTrue(tr)
        self.assertLessEqual(max(tr), 4 * B ** 3)

    def test_overlap_is_exact_on_known_cases(self):
        unit = (1, 1, 1)
        self.assertTrue(VX.tri_box_overlap((-2, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 0), unit))
        self.assertFalse(VX.tri_box_overlap((5, 5, 5), (6, 5, 5), (5, 6, 5), (0, 0, 0), unit))

    def test_rejects_bounds_outside_the_decided_range(self):
        for bad in (0, -1, 7, 100):
            with self.assertRaises(VX.VoxlatError):
                VX.attained_max(bad)


class TheQuadraticPlantBites(unittest.TestCase):
    def test_plant_claims_a_64_bit_fit_that_does_not_exist(self):
        """L15, and this is the plant that matters: it is wrong in the direction that ships. It
        reports a width fitting uint64_t, so the defect is invisible on small test scenes and
        silently corrupts a real city."""
        self.assertTrue(VX.quadratic_plant_underestimates())
        self.assertEqual(VX._bound_by_quadratic(32000, 12), 57)
        self.assertEqual(VX.city_scale_bits(32000, 12), (84, False))

    def test_no_fractional_precision_rescues_it(self):
        """Not a k that can be tuned around — every admitted k overflows 64 bits at city scale."""
        for k in (8, 12, 16):
            need, fits = VX.city_scale_bits(32000, k)
            self.assertFalse(fits, f"k={k} must not fit")
            self.assertGreater(need, VX._bound_by_quadratic(32000, k))

    def test_the_word_derives_a_tile_size(self):
        """The corollary: the arithmetic sizes the shard rather than taste doing it."""
        cb = VX.max_tile_coord_bits()
        self.assertEqual(cb, 20)
        self.assertLessEqual(VX.width_for(cb), 64)
        self.assertGreater(VX.width_for(cb + 1), 64)


if __name__ == "__main__":
    unittest.main()
