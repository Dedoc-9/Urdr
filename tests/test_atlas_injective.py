# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the general-n observer-atlas injectivity certificate.

Pins the exact injectivity theorem beyond the square/det case:
  * a full-COLUMN-rank (over-determined, rectangular) atlas is injective — rank==n,
    no collision, and distinct states give distinct observations;
  * a DEFICIENT atlas (an unobserved axis) is NOT injective, and the exact
    nullspace witness v (M v = 0, v != 0) exhibits a real collision: states 0 and
    v are indistinguishable under every chart — RED-FIRST, the collision must exist;
  * the two exact engines agree: rank==n  <=>  no nullspace witness;
  * NON-VACUITY: adding the missing chart restores injectivity (the deficiency was
    real, not an artifact).
Exact over Z (frozen Bareiss rank/nullspace); i64 overflow refuses."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_IDIR = os.path.join(_ROOT, "tools", "intla")
if _IDIR not in sys.path:
    sys.path.insert(0, _IDIR)

import atlas_injective as A                              # noqa: E402


# n = 3 state; a full-rank rectangular atlas (5 observation rows) and a deficient
# atlas that never observes the third (z) axis.
_N = 3
_FULL = [[[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [1, 1, 0]], [[0, 1, 1]]]
_DEFICIENT = [[[1, 0, 0], [0, 1, 0]], [[1, 1, 0]]]        # z never observed


class FullRankInjective(unittest.TestCase):
    def test_rank_equals_n_and_no_collision(self):
        self.assertTrue(A.injective(_FULL, _N))
        self.assertEqual(A.rank(_FULL), _N)
        self.assertIsNone(A.collision_witness(_FULL, _N))

    def test_distinct_states_distinct_observations(self):
        s = A.stack(_FULL)
        seen = {}
        for a in range(-1, 2):
            for b in range(-1, 2):
                for c in range(-1, 2):
                    x = [a, b, c]
                    key = tuple(A.matvec(s, x))
                    self.assertNotIn(key, seen, "distinct states collided under a full-rank atlas")
                    seen[key] = tuple(x)


class DeficientCollides(unittest.TestCase):
    def test_not_injective_and_exact_collision_witness(self):
        self.assertFalse(A.injective(_DEFICIENT, _N))
        self.assertLess(A.rank(_DEFICIENT), _N)
        v = A.collision_witness(_DEFICIENT, _N)
        self.assertIsNotNone(v)
        self.assertTrue(any(x != 0 for x in v))          # a genuine nonzero witness
        s = A.stack(_DEFICIENT)
        self.assertTrue(all(x == 0 for x in A.matvec(s, v)))   # v is in the kernel
        # the collision: states 0 and v produce identical observations
        self.assertEqual(A.matvec(s, [0] * _N), A.matvec(s, v))

    def test_rank_and_nullspace_engines_agree(self):
        for atlas in (_FULL, _DEFICIENT):
            inj, w = A.certifies_injective(atlas, _N)
            self.assertIsNotNone(inj, "rank and nullspace disagreed — verdict refused")
            self.assertEqual(inj, w is None)


class NonVacuity(unittest.TestCase):
    def test_adding_missing_chart_restores_injectivity(self):
        # the deficiency was real: observing z makes the atlas injective.
        fixed = _DEFICIENT + [[[0, 0, 1]]]
        self.assertFalse(A.injective(_DEFICIENT, _N))
        self.assertTrue(A.injective(fixed, _N))


if __name__ == "__main__":
    unittest.main()
