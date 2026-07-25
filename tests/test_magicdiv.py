# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/magicdiv.py — DIVISION BY AN INVARIANT CONSTANT (URDRMAG1), the
Granlund-Montgomery multiply-shift identity, EXHAUSTIVELY DECIDED rather than swept.

  THE IDENTITY — floor(n/d) == (m*n) >> s for EVERY divisor and EVERY dividend in the word. Not a
    sample: 1047552 checks, decided.
  THE PLANT BITES — floor-instead-of-ceil for the multiplier is correct only for powers of two and
    fails on 1013 divisors; exhaustion is what catches it.
  CLAIM 1 REFUTED — Lambda is countable, so its Hausdorff dimension is 0, not log2(log2 M).
  CLAIM 2 TRUE WITH ONE BOUNDARY EXCEPTION — the equal-shift classes ARE the dyadic blocks, every
    upper edge a power of two except the final class, truncated by the word.
  CLAIM 4 DEMYSTIFIED — s == W + ceil(log2 d) exactly; the "self-organization" is bit-length.

Every test can go red (L5); the plant bites before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import magicdiv as MD                                             # noqa: E402


class TheIdentity(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in MD.SCENES:
            self.assertEqual(MD.scene_result(name), MD.golden(name), name)
            self.assertEqual(MD.scene_result(name), MD.scene_result(name), name)

    def test_exhaustively_decided(self):
        """Not a sweep — every divisor against every dividend in the word."""
        checks, fails = MD.exhaustive()
        self.assertEqual(fails, 0, "the multiply-shift identity failed somewhere in the word")
        self.assertEqual(checks, (1 << MD.WORD) * ((1 << MD.WORD) - 1),
                         "the exhaustive check did not cover the whole word")

    def test_no_floats_in_the_construction(self):
        """ceil_log2 is bit_length, not math.log — the arc's floor."""
        # Look for the CALL, not the prose: the docstring legitimately says "no math.log", so a bare
        # substring test matches the module's own claim about itself and always fails. (Caught by
        # this test failing on its first run — the apparatus asserting itself rather than the code.)
        src = open(os.path.join(_ROOT, "tools", "terrain", "magicdiv.py"), encoding="utf-8").read()
        self.assertNotIn("math.log(", src)
        self.assertNotIn("float(", src)
        self.assertNotIn("import math\n", src)      # only `from math import gcd` is admitted
        for d in (1, 2, 3, 4, 5, 7, 8, 9, 1023):
            self.assertEqual(MD.ceil_log2(d), max(0, (d - 1).bit_length()))

    def test_rejects_bad_divisors(self):
        for bad in (0, -1, 2.0):
            with self.assertRaises(MD.MagicdivError):
                MD.plan(bad)


class ThePlantBites(unittest.TestCase):
    def test_floor_plant_fails_exhaustively(self):
        _c, fails = MD.exhaustive(_plan=MD._plan_floor)
        self.assertGreater(fails, 0, "the floor-instead-of-ceil plant must fail")

    def test_floor_plant_is_correct_only_for_powers_of_two(self):
        """The plant's subtlety is why exhaustion earns its keep: it looks right on the easy cases."""
        for d in (1, 2, 4, 8, 16):
            self.assertTrue(MD.verify_divisor(d, _plan=MD._plan_floor), f"pow2 {d}")
        self.assertIsNotNone(MD.first_counterexample(3, _plan=MD._plan_floor))
        self.assertTrue(MD.verify_divisor(3), "the honest plan must hold where the plant fails")


class TheGradedCorollaries(unittest.TestCase):
    def test_claim1_is_refuted_by_definition(self):
        kind, dim = MD.refutes_claim1()
        self.assertEqual((kind, dim), ("countable", 0),
                         "a countable set has Hausdorff dimension 0 — the claim cannot be rescued")

    def test_claim2_dyadic_with_the_boundary_exception(self):
        self.assertTrue(MD.classes_are_dyadic())
        cls = [c for c in MD.shift_classes() if c[2] > c[1]]
        for _s, _lo, hi in cls[:-1]:
            self.assertEqual(hi & (hi - 1), 0, "an interior class must end on a power of two")
        self.assertEqual(cls[-1][2], (1 << MD.WORD) - 1,
                         "the final class must be the word-truncated one")

    def test_claim4_is_bitlength_not_emergence(self):
        self.assertTrue(MD.shift_is_bitlength())
        for d in (1, 3, 5, 17, 513):
            self.assertEqual(MD.plan(d)[1], MD.WORD + MD.ceil_log2(d))

    def test_claim3_histogram_is_reported_not_asserted(self):
        hist = MD.equiv_classes()
        self.assertGreater(sum(hist.values()), 0)
        self.assertEqual(sum(k * v for k, v in hist.items()), (1 << MD.WORD) - 1,
                         "the class histogram must account for every divisor")


class TheDeclaredWiderWord(unittest.TestCase):
    def test_wide_spotcheck(self):
        """DECLARED, not decided: the same construction at a wider word, spot-checked only."""
        self.assertTrue(MD.wide_spotcheck())


if __name__ == "__main__":
    unittest.main()
