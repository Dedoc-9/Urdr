# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `voxin` (URDRVXI1) — the import boundary.

Every test here asserts the APPARATUS, never a hoped result: each one is written so that a real
defect in the importer would make it fail. The three refusal tests are the plants — they exist to
prove the door can close, because an importer that admits everything has no boundary to certify.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_T = os.path.join(ROOT, "tools", "terrain")
if _T not in sys.path:
    sys.path.insert(0, _T)

import voxin as VI                                                        # noqa: E402
import voxlat as VX                                                       # noqa: E402


class TheDerivedBound(unittest.TestCase):
    def test_bound_comes_from_voxlat_not_from_a_local_constant(self):
        """A bound restated in two places is a bound that can disagree with itself."""
        self.assertTrue(VI.bound_is_derived_not_restated())
        self.assertEqual(VI.admissible_coord_bits(), VX.max_tile_coord_bits(VX.WORD64))

    def test_the_bound_is_the_one_voxlat_decided(self):
        """20 bits, from `3*coord_bits + 2 <= 64`. If voxlat's law moves, this moves with it."""
        self.assertEqual(VI.admissible_coord_bits(), 20)
        self.assertEqual(VI.coord_limit(), (1 << 20) - 1)

    def test_geometry_one_past_the_bound_is_refused(self):
        """THE PLANT: the exact geometry voxlat proved would overflow a 64-bit placement."""
        over = VI.coord_limit() + 1
        with self.assertRaises(VI.VoxinError) as ctx:
            VI.occupancy([((0, 0, 0), (1, 0, 0), (0, over, 0))])
        self.assertEqual(ctx.exception.code, "VOXIN-REFUSE")
        self.assertTrue(VI.over_bound_geometry_is_refused())

    def test_geometry_exactly_at_the_bound_is_admitted(self):
        """The refusal must be a boundary, not a wall one short of it — otherwise the derived bound
        is not the bound being enforced."""
        at = VI.coord_limit()
        self.assertIsInstance(VI.occupancy([((0, 0, 0), (1, 0, 0), (0, at, 0))]), tuple)


class TheDoorIsTyped(unittest.TestCase):
    def test_float_is_refused_never_rounded(self):
        """Quantization is the CALLER's declared act. A silent rounding here would be an authority
        act with no record."""
        for bad in (1.0, 0.5, -2.0, 3.000000001):
            with self.assertRaises(VI.VoxinError) as ctx:
                VI.occupancy([((0, 0, 0), (1, 0, 0), (0, bad, 0))])
            self.assertEqual(ctx.exception.code, "VOXIN-REFUSE")

    def test_degenerate_triangle_is_refused(self):
        for t in (((1, 1, 1), (1, 1, 1), (2, 2, 2)),
                  ((0, 0, 0), (2, 2, 2), (0, 0, 0))):
            with self.assertRaises(VI.VoxinError):
                VI.occupancy([t])

    def test_malformed_input_is_typed_refusal(self):
        for bad in ("not a list", [((0, 0), (1, 0, 0), (0, 1, 0))], [((0, 0, 0), (1, 0, 0))],
                    [None], [((0, 0, 0), (1, 0, 0), "xyz")]):
            with self.assertRaises(VI.VoxinError):
                VI.occupancy(bad)

    def test_refusal_is_total_no_silent_admission(self):
        """Exhaustive over the malformed shapes above: every one raises, none returns a plausible
        wrong answer. A partition with a fall-through is not a partition (L60)."""
        shapes = ["str", [((0, 0), (1, 0, 0), (0, 1, 0))], [((0, 0, 0), (1, 0, 0))], [None]]
        refused = 0
        for bad in shapes:
            try:
                VI.occupancy(bad)
            except VI.VoxinError:
                refused += 1
        self.assertEqual(refused, len(shapes))


class OccupancyIsAFunctionOfGeometry(unittest.TestCase):
    def test_permutation_invariance_on_the_pinned_scene(self):
        self.assertTrue(VI.occupancy_is_permutation_invariant(VI.SCENE))

    def test_permutation_invariance_over_a_swept_corpus(self):
        """One scene proves nothing (L20). Every rotation of a 4-triangle soup must agree."""
        soup = list(VI.SCENE) + [((0, 2, 0), (3, 2, 3), (0, 5, 3))]
        base = VI.occupancy_digest(soup)
        for i in range(len(soup)):
            rotated = soup[i:] + soup[:i]
            self.assertEqual(VI.occupancy_digest(rotated), base,
                             "occupancy depends on input ORDER at rotation %d" % i)

    def test_digest_is_deterministic_across_calls(self):
        first = VI.occupancy_digest(VI.SCENE)
        for _ in range(4):
            self.assertEqual(VI.occupancy_digest(VI.SCENE), first)

    def test_distinct_geometry_gives_distinct_occupancy(self):
        """Non-vacuity: if every input digested the same the invariance law would hold trivially."""
        other = (((0, 0, 0), (5, 0, 0), (0, 5, 5)),)
        self.assertNotEqual(VI.occupancy_digest(VI.SCENE), VI.occupancy_digest(other))

    def test_occupancy_is_non_empty_on_the_pinned_scene(self):
        """L61: an importer that emitted nothing would satisfy every invariance law above."""
        self.assertGreater(len(VI.occupancy(VI.SCENE)), 0)


class AgainstTheOracle(unittest.TestCase):
    def test_every_emitted_voxel_satisfies_voxlats_own_test(self):
        """Checked against `voxlat.tri_box_overlap` — an INDEPENDENT route — rather than against
        this module's traversal, so a bug in the loop cannot hide behind its own digest (L23)."""
        self.assertTrue(VI.occupancy_agrees_with_voxlat(VI.SCENE))

    def test_no_overlapping_voxel_is_omitted(self):
        """The converse direction: the oracle finds nothing the importer missed."""
        soup = (((0, 0, 0), (4, 0, 0), (0, 4, 2)),)
        self.assertTrue(VI.occupancy_agrees_with_voxlat(soup))

    def test_emitted_keys_are_valid_morton_codes(self):
        for k in VI.occupancy(VI.SCENE):
            x, y, z = VX.unmorton(k, VI.LEVELS)
            self.assertEqual(VX.morton(x, y, z, VI.LEVELS), k)


if __name__ == "__main__":
    unittest.main(verbosity=2)
