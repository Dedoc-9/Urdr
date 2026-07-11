# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-field (deterministic scalar-field transport).

Pins the properties that make the pluggable-backend field honest:
  * each scene's digest is reproducible and matches its golden;
  * the FIELDFP field stays BOUNDED (fits i64) over a long run;
  * total mass is conserved EXACTLY (the conservative flux form) — even in
    fixed-point, because the rounded flux is applied +to one cell, −to the other;
  * ROUNDING is load-bearing: a truncation backend diverges from round-to-nearest
    (so a divergent rounding implementation is caught cross-placement) — NON-VACUITY;
  * the EXACT (FIELDQ) backend is exact + mass-conserved on a tiny field, and
    REFUSES on a larger/longer one (denominators exceed i64);
  * the backend is part of IDENTITY: FixedPoint and Exact never share a digest."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import field as FLD                                     # noqa: E402
import field_scenes                                    # noqa: E402
from field import FixedPoint, Exact, FieldError, ONE    # noqa: E402
from rational import RationalError                      # noqa: E402


def _load_goldens():
    out = {}
    with open(os.path.join(_PDIR, "conformance_field.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dg = ln.split()
                out[name] = dg
    return out


class _Trunc(FixedPoint):
    """A defect backend: truncates instead of round-to-nearest."""
    @staticmethod
    def mul_k(a, kn, kd):
        return FixedPoint._g((a * kn) // kd)


class Scenes(unittest.TestCase):
    def test_each_scene_reproducible_and_matches_golden(self):
        goldens = _load_goldens()
        self.assertEqual(set(goldens), set(field_scenes.SCENES))
        for name in field_scenes.SCENES:
            d1 = field_scenes.run(name)
            d2 = field_scenes.run(name)
            self.assertEqual(d1, d2, f"{name} nondeterministic")
            self.assertEqual(d1, goldens[name], f"{name} != golden")


class FixedPointField(unittest.TestCase):
    def _bump(self, w, h):
        g = [0] * (w * h)
        g[(h // 2) * w + w // 2] = ONE
        return g

    def test_bounded_and_mass_conserved_exactly(self):
        w = h = 8
        g = self._bump(w, h)
        m0 = FLD.mass(FixedPoint, g)
        for _ in range(200):                              # stable params (4k+vx+vy = 3/4 ≤ 1)
            g = FLD.step(FixedPoint, g, w, h, (1, 16), (1, 4), (1, 4))
        self.assertTrue(all(-((1 << 63) - 1) <= v <= (1 << 63) - 1 for v in g))
        self.assertEqual(FLD.mass(FixedPoint, g), m0)     # flux form: EXACT even rounded

    def test_rounding_is_load_bearing_nonvacuity(self):
        w = h = 8
        base = self._bump(w, h)
        g = list(base)
        t = list(base)
        for _ in range(100):
            g = FLD.step(FixedPoint, g, w, h, (1, 8), (1, 2), (0, 1))
            t = FLD.step(_Trunc, t, w, h, (1, 8), (1, 2), (0, 1))
        self.assertNotEqual(FLD.digest(FixedPoint, g, w, h),
                            FLD.digest(_Trunc, t, w, h))   # truncation diverges


class ExactField(unittest.TestCase):
    def _bump(self, w, h):
        g = [Exact.unit(0, 1)] * (w * h)
        g[(h // 2) * w + w // 2] = Exact.unit(1, 1)
        return g

    def test_tiny_exact_mass_conserved(self):
        w = h = 4
        g = self._bump(w, h)
        m0 = FLD.mass(Exact, g)
        for _ in range(3):
            g = FLD.step(Exact, g, w, h, (1, 8), (1, 2), (0, 1))
        self.assertTrue(FLD.mass(Exact, g).__eq__(m0))     # exact, no rounding

    def test_longer_exact_run_refuses(self):
        w = h = 4
        g = self._bump(w, h)
        with self.assertRaises(RationalError):
            for _ in range(200):
                g = FLD.step(Exact, g, w, h, (1, 8), (1, 2), (0, 1))


class BackendIdentity(unittest.TestCase):
    def test_backend_is_part_of_digest(self):
        # two grids of all-zero cells but different backends -> different digests
        fp = FLD.digest(FixedPoint, [FixedPoint.zero()] * 4, 2, 2)
        ex = FLD.digest(Exact, [Exact.zero()] * 4, 2, 2)
        self.assertNotEqual(fp, ex)                        # the tag is in identity

    def test_fixed_point_overflow_refuses(self):
        with self.assertRaises(FieldError) as ctx:
            FixedPoint.mul_k((1 << 62), (1 << 5), 1)
        self.assertEqual(ctx.exception.code, "FIELD-REFUSE")


if __name__ == "__main__":
    unittest.main()
