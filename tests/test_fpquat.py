#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the Q32.32 rotation substrate (tools/frontfps/fpquat.py).

Bounds below are MEASURED ON THE PINNED BATTERY and pinned with ~2x headroom —
they are corpus claims, not universal theorems (`corpus agreement != universal
correctness`). The exact laws (mul nearest-rounding, the rsqrt inequality,
isqrt == math.isqrt) are asserted as inequalities/equalities, not samples.
"""
import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("frontfps", "physics"):
    p = os.path.join(ROOT, "tools", d)
    if p not in sys.path:
        sys.path.insert(0, p)

import fpquat as FQ  # noqa: E402
from field import ONE  # noqa: E402

TOL_UNIT = 4        # measured worst 2
TOL_ROUNDTRIP = 16  # measured worst 8
TOL_COMPOSE = 32    # measured worst 15
TOL_DRIFT = 64      # measured worst 39


def _corpus():
    path = os.path.join(ROOT, "tools", "frontfps", "conformance_fpquat.txt")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                name, dig = line.split()
                if name == "battery":
                    return dig
    raise AssertionError("battery vector missing from corpus")


class Goldens(unittest.TestCase):
    def test_battery_reproduces_pinned_digest(self):
        self.assertEqual(FQ.battery_digest(), _corpus())

    def test_battery_deterministic_twice(self):
        self.assertEqual(FQ.battery_digest(), FQ.battery_digest())

    def test_battery_row_count_declared(self):
        self.assertEqual(len(FQ._battery()), 66)


class ExactLaws(unittest.TestCase):
    def test_fqmul_is_nearest_rounding(self):
        """|a*b - r*ONE| <= ONE/2 exactly — the _rdiv law, checked as integers."""
        for a, b in ((FQ.H, FQ.H), (FQ.Q3, -FQ.T3), (3 * ONE, 5 * ONE),
                     (-7 * ONE // 3, 11 * ONE // 7), (1, 1), (FQ.H, 3)):
            r = FQ.fqmul(a, b)
            self.assertLessEqual(2 * abs(a * b - r * ONE), ONE, (a, b, r))

    def test_rsqrt_inequality_law(self):
        """r = rsqrt(x) satisfies r^2*x <= 2^96 < (r+2)^2*x — within 2 ulp of
        2^48/sqrt(x), proved per input, not sampled."""
        for x in FQ.RSQRT_IN:
            r = FQ.rsqrt(x)
            self.assertLessEqual(r * r * x, 1 << 96, x)
            self.assertGreater((r + 2) * (r + 2) * x, 1 << 96, x)

    def test_isqrt_newton_equals_math_isqrt(self):
        for n in (0, 1, 2, 3, 4, 5, 15, 16, 17, 24, 25, 26, 99, 10 ** 12,
                  (1 << 96) // 3, (1 << 96) // FQ.COMP_MAX, (1 << 96) - 1):
            self.assertEqual(FQ._isqrt_newton(n), math.isqrt(n), n)

    def test_conj_is_exact_involution(self):
        q = FQ.QUATS[2]
        self.assertEqual(FQ.qconj(FQ.qconj(q)), q)


class MeasuredBounds(unittest.TestCase):
    def test_normalize_lands_near_unit(self):
        for q in FQ.QUATS:
            u = FQ.qnormalize(q)
            self.assertLessEqual(abs(FQ.qnorm2(u) - ONE), TOL_UNIT, q)

    def test_rotate_preserves_norm2_within_bound(self):
        for q in FQ.QUATS:
            u = FQ.qnormalize(q)
            for v in FQ.VECS:
                rv = FQ.vrotate(u, v)
                drift = abs(FQ.qnorm2((0,) + rv) - FQ.qnorm2((0,) + v))
                self.assertLessEqual(drift, TOL_DRIFT, (q, v))

    def test_conj_rotation_roundtrips(self):
        for q in FQ.QUATS:
            u = FQ.qnormalize(q)
            for v in FQ.VECS:
                back = FQ.vrotate(FQ.qconj(u), FQ.vrotate(u, v))
                self.assertLessEqual(max(abs(a - b) for a, b in zip(v, back)),
                                     TOL_ROUNDTRIP, (q, v))

    def test_rotation_composes_within_bound(self):
        units = [FQ.qnormalize(q) for q in FQ.QUATS]
        for a in units:
            for b in units:
                ab = FQ.qnormalize(FQ.qmul(a, b))
                for v in FQ.VECS:
                    r1 = FQ.vrotate(ab, v)
                    r2 = FQ.vrotate(a, FQ.vrotate(b, v))
                    self.assertLessEqual(max(abs(x - y) for x, y in zip(r1, r2)),
                                         TOL_COMPOSE, (a, b, v))

    def test_nlerp_endpoints_are_normalized_inputs(self):
        p, q = FQ.QUATS[1], FQ.QUATS[2]
        self.assertEqual(FQ.qnlerp(p, q, 0), FQ.qnormalize(p))
        self.assertEqual(FQ.qnlerp(p, q, ONE), FQ.qnormalize(q))


class Refusals(unittest.TestCase):
    def _refused(self, fn, why):
        with self.subTest(why=why):
            with self.assertRaises(FQ.FpqError) as ctx:
                fn()
            self.assertEqual(ctx.exception.code, "FPQ-REFUSE")

    def test_each_refusal_typed_and_total(self):
        self._refused(lambda: FQ.rsqrt(0), "rsqrt of zero")
        self._refused(lambda: FQ.rsqrt(-ONE), "rsqrt of negative")
        self._refused(lambda: FQ.fqmul(FQ.COMP_MAX + 1, ONE), "beyond COMP_MAX")
        self._refused(lambda: FQ.fqmul(1.5, ONE), "non-integer input")
        self._refused(lambda: FQ.qnormalize((0, 0, 0, 0)), "normalize zero quat")
        self._refused(lambda: FQ.qnlerp(FQ.QUATS[0], FQ.QUATS[1], ONE + 1),
                      "nlerp t beyond ONE — refused, never clamped")
        self._refused(lambda: FQ.qnlerp(FQ.QUATS[0], FQ.QUATS[1], -1),
                      "nlerp negative t")
        self._refused(lambda: FQ.qnorm2((ONE, 0, 0)), "3-tuple is not a quat")


class DefectsBite(unittest.TestCase):
    def test_truncdiv_defect_diverges(self):
        self.assertNotEqual(FQ.battery_digest_defect_truncdiv(), _corpus())

    def test_wrap64_defect_diverges(self):
        self.assertNotEqual(FQ.battery_digest_defect_wrap64(), _corpus())

    def test_wrap64_actually_wraps_on_battery(self):
        """The defect is non-vacuous because the battery FORCES a wrap: the large
        quaternion's norm products exceed i64. If this stops holding, the defect
        (and the battery) must be re-armed."""
        w, x, y, z = FQ.QUATS[3]
        self.assertGreater(w * w + x * x + y * y + z * z, FQ.IMAX)


if __name__ == "__main__":
    unittest.main()
