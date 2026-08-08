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


class TheSubstrateHasADomain(unittest.TestCase):
    """"No float, no clock, no RNG" is this module's headline and the foundation of
    every determinism claim above it. Nothing checked it, and the gap was a DESYNC
    vector rather than an audit hole: `lockstep._u` truncates with `int(v)` and
    `worldstep.step_tick` did not, so one float impulse in a shared transcript
    produced two different witness chains with no refusal from either."""

    BACKENDS = (FixedPoint, Exact)

    def test_every_door_refuses_a_float_and_admits_an_int(self):
        """Both halves matter. A door that refused everything would pass the first
        assertion and be useless, which is why the honest int is asserted too."""
        for B in self.BACKENDS:
            with self.subTest(B.tag):
                self.assertTrue(FLD.every_door_refuses(B))

    def test_the_caller_supplied_coefficient_is_a_door_too(self):
        """THE ONE I GOT WRONG. `unit` looked like the sole entry because add/sub are
        closed over the substrate's own values — but `mul_k`'s `kn`/`kd` are a
        caller's rational coefficient, and `lockstep` passes the restitution `w["e"]`
        straight through it. Before the guard, two integer inputs plus a float
        coefficient returned a float."""
        for B in self.BACKENDS:
            with self.subTest(B.tag):
                one = B.unit(1, 1)
                with self.assertRaises(FieldError) as ctx:
                    B.mul_k(one, 1.5, 2)
                self.assertEqual(ctx.exception.code, "FIELD-REFUSE")
                B.mul_k(one, 1, 2)                    # the honest coefficient passes

    def test_the_witness_is_an_independent_second_guard(self):
        """`ser` used to do `int(a).to_bytes(...)`, truncating at witness time — which
        is exactly why the contamination was invisible to every conformance digest in
        the tree. It must refuse a value that never passed a door, or it is redundant
        rather than independent."""
        for B in self.BACKENDS:
            with self.subTest(B.tag):
                self.assertTrue(FLD.the_witness_refuses(B))

    def test_arithmetic_is_int_closed_measured_not_asserted(self):
        for B in self.BACKENDS:
            with self.subTest(B.tag):
                self.assertTrue(FLD.arithmetic_is_int_closed(B))

    def test_bool_is_refused_boolport_one_layer_down(self):
        """`True == 1` reaches a frozen integer parameter as a value nobody wrote."""
        for B in self.BACKENDS:
            with self.subTest(B.tag):
                with self.assertRaises(FieldError) as ctx:
                    B.unit(True, 1)
                self.assertEqual(ctx.exception.code, "FIELD-REFUSE")

    def test_the_exact_backend_no_longer_builds_a_float_rational(self):
        """`Exact` was the worse of the pair. It did not truncate — it built
        `RQ(5.5, 1)` and carried a rational whose PARTS ARE FLOATS, printing
        `11.0/2.0`, after which `ser` raised an untyped AttributeError reaching for
        `.to_bytes` on a float. A rational with a float numerator is not a slower
        exact number; it is the exactness claim inverted."""
        with self.assertRaises(FieldError) as ctx:
            Exact.unit(5.5, 1)
        self.assertEqual(ctx.exception.code, "FIELD-REFUSE")
        q = Exact.unit(11, 2)
        self.assertIsInstance(q.n, int)
        self.assertIsInstance(q.d, int)

    def test_the_legitimate_corpus_is_untouched(self):
        """NON-VACUITY IN THE OTHER DIRECTION: the guard must be free. Every pinned
        scene still reproduces its golden, so the domain law refuses what was never
        admitted and nothing that was."""
        goldens = _load_goldens()
        self.assertTrue(goldens)
        for name, want in sorted(goldens.items()):
            with self.subTest(name):
                self.assertEqual(field_scenes.run(name), want)


if __name__ == "__main__":
    unittest.main()
