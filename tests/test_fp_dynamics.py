# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-physics rung 5 (bounded fixed-point dynamics).

Pins the properties that make the fixed-point real-time path a deterministic,
reproducible, bounded time-stepper -- the honest complement to the exact rungs:
  * each scene's trace digest is DETERMINISTIC (same twice) and matches its frozen golden;
  * the settling contact stack comes to REST (final |v| within the sleep threshold);
  * the pendulum's rod stays BOUNDED (squared-length Baumgarte holds |d·d − L²| small);
  * a DEFECT step -- no sleep clamp, or no Baumgarte -- diverges from the golden
    (non-vacuity: the gate can redden);
  * the substrate is BOUNDED: a wildly out-of-range value REFUSES (FIELD-REFUSE),
    never wraps.
Not exact (fixed-point rounds); each negative test asserts the wrong outcome would pass."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import fp_dynamics as D                                 # noqa: E402
import fp_scenes                                        # noqa: E402
from field import FixedPoint, ONE, FieldError           # noqa: E402


def _load_goldens():
    out = {}
    with open(os.path.join(_PDIR, "conformance_fp.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dig = ln.split()
                out[name] = dig
    return out


class FixedPointDynamics(unittest.TestCase):
    def test_deterministic_and_golden(self):
        goldens = _load_goldens()
        for name in fp_scenes.SCENES:
            t1, _ = fp_scenes.run(name)
            t2, _ = fp_scenes.run(name)
            self.assertEqual(t1, t2, f"{name} nondeterministic")
            self.assertIn(name, goldens, f"{name} missing golden")
            self.assertEqual(t1, goldens[name], f"{name} trace ≠ golden")

    def test_stack_settles(self):
        _t, fvy = fp_scenes.run("stack3")
        thr = FixedPoint.unit(5, 2)
        self.assertTrue(all(-thr < v < thr for v in fvy), "stack did not come to rest")

    def test_pendulum_bounded(self):
        # the rod's squared length stays within a small band of its initial L² (no drift)
        _t, (px, py) = D.run_swing()
        ax, ay = D.fp(190), D.fp(60)
        nx, ny = FixedPoint.sub(px, ax), FixedPoint.sub(py, ay)
        dd = FixedPoint.add(D.fmul(nx, nx), D.fmul(ny, ny))
        L2_0 = D.fmul(D.fp(90), D.fp(90))                # initial |d|² (ball started 90 to the side)
        drift = abs((dd - L2_0)) / ONE
        self.assertLess(drift, 400.0, f"rod length drifted too far (|Δd·d|={drift:.0f})")

    def test_defect_nonvacuous(self):
        # a wrong step must diverge from the golden — otherwise the gate could never redden
        goldens = _load_goldens()
        for name in fp_scenes.SCENES:
            self.assertNotEqual(fp_scenes.run_defect(name), goldens[name],
                                f"{name} defect matched golden (gate cannot redden)")

    def test_substrate_bounded_refuses(self):
        # the frozen substrate refuses rather than wrap on i64 overflow
        with self.assertRaises(FieldError):
            FixedPoint.mul_k(FixedPoint.unit(3, 1), (1 << 62), 1)


if __name__ == "__main__":
    unittest.main()
