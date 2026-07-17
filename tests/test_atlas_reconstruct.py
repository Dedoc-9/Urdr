# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for exact observer-atlas RECONSTRUCTION (inversion).

Pins the constructive sibling of the injectivity certificate: over an injective
atlas, recover the state from its observations -- exactly -- or refuse.
  * ROUND-TRIP: for a known state x, reconstruct(M x) == x, exactly (integer
    states recover with den==1; a genuinely fractional state recovers as the
    exact reduced rational, den>1 -- not a float, not a round).
  * WITNESS: the returned (num, den) satisfies the independently-checkable
    identity M·num == den·y with den>0.
  * FORGERY REFUSED (RED-FIRST non-vacuity): perturb one *redundant* coordinate
    of a genuine observation so it leaves the column space; reconstruction must
    REFUSE (INCONSISTENT). This is the whole point of over-determination -- a
    reconstructor that "recovers" a state from an impossible view is vacuous.
  * DEFICIENT REFUSED: on a non-injective atlas the state is not unique (the
    injectivity collision witness exhibits two states with one observation), so
    reconstruction must REFUSE (NOT_INJECTIVE) rather than invent an answer.
Exact over Z / Q (frozen Bareiss rank + determinant); i64 overflow refuses."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_IDIR = os.path.join(_ROOT, "tools", "intla")
if _IDIR not in sys.path:
    sys.path.insert(0, _IDIR)

import atlas_reconstruct as R                            # noqa: E402


_N = 3
# injective (full column rank 3) over-determined atlas: 5 observation rows.
_FULL = [[[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [1, 1, 0]], [[0, 1, 1]]]
# deficient atlas: the z axis is never observed (rank 2 < 3).
_DEFICIENT = [[[1, 0, 0], [0, 1, 0]], [[1, 1, 0]]]
# a scaled 3x2 atlas whose subsystem determinant is 2, so a half-integer state
# recovers as an exact non-trivial rational.
_HALF = [[[2, 0], [0, 2]], [[1, 1]]]


class RoundTrip(unittest.TestCase):
    def test_integer_states_recover_exactly(self):
        m = R.stack(_FULL)
        for x in ([2, -3, 5], [0, 0, 1], [-7, 4, 0], [1, 1, 1], [9, -9, 9]):
            y = R.matvec(m, x)
            state = R.reconstruct(_FULL, y, _N)
            self.assertIsNotNone(state, "genuine observation was refused")
            num, den = state
            self.assertEqual(den, 1)                    # integer state, reduced
            self.assertEqual(num, x)                    # recovered exactly

    def test_fractional_state_recovers_as_exact_rational(self):
        # true state s = [1, 1] / 2; its observation under _HALF is all-integer.
        m = R.stack(_HALF)
        y = R.matvec(m, [1, 1])                          # = 2 * observation of s
        y = [v // 2 for v in y]                          # observation of s = [1,1]/2
        state = R.reconstruct(_HALF, y, 2)
        self.assertEqual(state, ([1, 1], 2))             # exact rational, den>1 (not a round)


class Witness(unittest.TestCase):
    def test_witness_is_independently_checkable(self):
        m = R.stack(_FULL)
        for x in ([4, 4, -1], [3, -2, 7]):
            y = R.matvec(m, x)
            state = R.reconstruct(_FULL, y, _N)
            self.assertIsNotNone(state)
            self.assertTrue(R.verifies(_FULL, y, _N, state))   # M·num == den·y, den>0
            num, den = state
            mn = R.matvec(m, num)
            self.assertTrue(den > 0)
            self.assertEqual(mn, [den * v for v in y])


class ForgeryRefused(unittest.TestCase):
    def test_perturbed_redundant_row_is_refused(self):
        m = R.stack(_FULL)
        y = R.matvec(m, [2, -3, 5])
        # rows 0,1,2 form the solved subsystem; rows 3 and 4 are redundant.
        for bad_row in (3, 4):
            forged = list(y)
            forged[bad_row] += 1                         # leave the column space
            status, state = R.solve(_FULL, forged, _N)
            self.assertEqual(status, R.INCONSISTENT, "a forged observation was accepted")
            self.assertIsNone(state)
            self.assertFalse(R.is_genuine_observation(_FULL, forged, _N))

    def test_non_vacuity_the_genuine_observation_would_have_passed(self):
        # control: the un-perturbed observation IS accepted, so the refusal above
        # is caused by the forgery, not by a broken reconstructor.
        m = R.stack(_FULL)
        y = R.matvec(m, [2, -3, 5])
        self.assertTrue(R.is_genuine_observation(_FULL, y, _N))


class DeficientRefused(unittest.TestCase):
    def test_non_injective_atlas_refuses_no_unique_state(self):
        m = R.stack(_DEFICIENT)
        # z is unobserved, so [2,-3,0] and [2,-3,9] share this observation.
        y = R.matvec(m, [2, -3, 0])
        self.assertEqual(R.matvec(m, [2, -3, 0]), R.matvec(m, [2, -3, 99]))  # collision
        status, state = R.solve(_DEFICIENT, y, _N)
        self.assertEqual(status, R.NOT_INJECTIVE)
        self.assertIsNone(state)


class ReorderInvariant(unittest.TestCase):
    # The D17 ~ (equivalence) role for the reconstructibility detector: a state does not depend on
    # the ORDER it was measured in. Reordering the observations -- permuting the rows of M and the
    # observation y TOGETHER -- must leave both the recovered state and the injectivity verdict
    # unchanged; a MISPAIRED reorder must break it (non-vacuity).
    def test_reordering_observations_preserves_state_and_verdict(self):
        m = R.stack(_FULL)
        y = R.matvec(m, [4, 4, -1])
        base_state = R.reconstruct(_FULL, y, _N)
        base_status = R.solve(_FULL, y, _N)[0]
        self.assertIsNotNone(base_state)
        for perm in ([4, 1, 3, 0, 2], [2, 0, 4, 3, 1], [1, 2, 3, 4, 0]):
            rows_p = [m[i] for i in perm]
            y_p = [y[i] for i in perm]
            self.assertEqual(R.reconstruct([rows_p], y_p, _N), base_state,
                             f"reorder {perm} moved the recovered state")
            self.assertEqual(R.solve([rows_p], y_p, _N)[0], base_status,
                             f"reorder {perm} moved the injectivity verdict")

    def test_mispaired_reorder_breaks_it_non_vacuity(self):
        # control: move the rows but NOT the observation -> the answer changes, so the invariance
        # above is a real preservation, not a vacuous identity.
        m = R.stack(_FULL)
        y = R.matvec(m, [4, 4, -1])
        base_state = R.reconstruct(_FULL, y, _N)
        rows_p = [m[i] for i in [4, 1, 3, 0, 2]]
        self.assertNotEqual(R.reconstruct([rows_p], y, _N), base_state,
                            "a mispaired reorder did not change the answer (invariance is vacuous)")


if __name__ == "__main__":
    unittest.main()
