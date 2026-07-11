# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for field → body surface-tension coupling.

  * EXACT BOOKKEEPING: the body's momentum change equals the injected impulse
    exactly (integer add — no drift), for every axis.
  * UP-GRADIENT: a field rising in +x pushes the body in +x (toward higher
    surface tension); a flat axis contributes no force.
  * NON-VACUITY: a UNIFORM field has zero gradient ⇒ zero force ⇒ zero impulse,
    while a non-uniform field gives a nonzero impulse — so the gradient is
    load-bearing, not decorative.
  * MONOTONE PUSH: under a static gradient the momentum grows monotonically.
  * DETERMINISM + OVERFLOW: identical inputs give identical impulses; an i64
    overflow is a typed FIELD-REFUSE, never a wrap."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import field_coupling as C                               # noqa: E402
from field import FixedPoint, FieldError                 # noqa: E402


def _ramp():
    # a field rising in +x: [0.1, 0.2, 0.4, 0.7, 1.0] on a 5x1 grid
    return [C.unit(1, 10), C.unit(2, 10), C.unit(4, 10), C.unit(7, 10), C.unit(10, 10)], 5, 1


class ExactBookkeeping(unittest.TestCase):
    def test_momentum_change_equals_impulse_exactly(self):
        grid, w, h = _ramp()
        j = C.impulse(C.force(grid, w, h, 2, (1, 4)), (1, 2))
        p0 = (C.unit(3, 1), C.unit(-2, 1))
        p1 = C.apply_impulse(p0, j)
        dp = (FixedPoint.sub(p1[0], p0[0]), FixedPoint.sub(p1[1], p0[1]))
        self.assertEqual(dp, j)                          # exact, both axes


class UpGradient(unittest.TestCase):
    def test_force_points_toward_higher_surface_tension(self):
        grid, w, h = _ramp()
        fx, fy = C.force(grid, w, h, 2, (1, 4))
        self.assertGreater(fx, 0)                        # +x gradient ⇒ +x push
        self.assertEqual(fy, 0)                          # flat in y ⇒ no y force


class NonVacuity(unittest.TestCase):
    def test_uniform_field_exerts_no_force(self):
        uni = [C.unit(5, 10)] * 5
        self.assertEqual(C.force(uni, 5, 1, 2, (1, 4)), (0, 0))
        self.assertEqual(C.impulse(C.force(uni, 5, 1, 2, (1, 4)), (1, 2)), (0, 0))

    def test_nonuniform_field_does_exert_force(self):
        grid, w, h = _ramp()
        self.assertNotEqual(C.force(grid, w, h, 2, (1, 4)), (0, 0))


class MonotonePush(unittest.TestCase):
    def test_momentum_grows_monotonically_under_static_gradient(self):
        grid, w, h = _ramp()
        p = (0, 0)
        xs = []
        for _ in range(4):
            p = C.apply_impulse(p, C.impulse(C.force(grid, w, h, 2, (1, 4)), (1, 2)))
            xs.append(p[0])
        self.assertTrue(all(xs[k + 1] > xs[k] for k in range(len(xs) - 1)))


class DeterminismAndOverflow(unittest.TestCase):
    def test_deterministic(self):
        grid, w, h = _ramp()
        a = C.impulse(C.force(grid, w, h, 2, (1, 4)), (1, 2))
        b = C.impulse(C.force(grid, w, h, 2, (1, 4)), (1, 2))
        self.assertEqual(a, b)

    def test_overflow_refuses(self):
        with self.assertRaises(FieldError) as ctx:
            C.apply_impulse((FixedPoint._g((1 << 63) - 1), 0), ((1 << 62), 0))
        self.assertEqual(ctx.exception.code, "FIELD-REFUSE")


if __name__ == "__main__":
    unittest.main()
