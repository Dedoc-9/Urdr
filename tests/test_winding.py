# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the winding-number detector (`tools/intla/winding.py`, W1 of D19 §5).

  * REFERENCE — the Loewner scenes and the sign controls reproduce their pinned (w, digest),
    deterministically;
  * LOEWNER — every pinned probe on both Loewner scenes has w ≥ 0 (the theorem-backed corpus
    property; a fact about the FROZEN integer objects, not a proof of the smooth theorem);
  * WITNESS — the crossing list recounts to the invariant; a tampered list fails the check;
  * INVARIANCE — cyclic rotation, integer collinear subdivision, and translation preserve w;
    orientation reversal NEGATES it (the documented covariance);
  * DEFECT — the unsigned (parity) count misreads every negatively-wound curve;
  * REFUSAL — degenerate polylines, non-integer input, and a probe on the trace WIND-REFUSE."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "intla")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import winding as W                                         # noqa: E402


class Winding(unittest.TestCase):
    def test_loewner_wave_golden(self):
        poly, probe = W.loewner_wave()
        w, dig = W.golden("loewner_wave")
        self.assertEqual(W.winding_number(poly, probe), w, "loewner_wave invariant drifted")
        self.assertEqual(W.witness_digest(poly, probe), dig, "loewner_wave witness drifted")
        self.assertEqual(W.witness_digest(poly, probe), W.witness_digest(poly, probe),
                         "nondeterministic")

    def test_loewner_second_golden_w2(self):
        poly, probe = W.loewner_second()
        w, dig = W.golden("loewner_second")
        self.assertEqual(w, 2, "the pinned probe must sit in the doubly-wound region")
        self.assertEqual(W.winding_number(poly, probe), w, "loewner_second invariant drifted")
        self.assertEqual(W.witness_digest(poly, probe), dig, "loewner_second witness drifted")

    def test_sign_controls(self):
        for name, expect in (("ccw_square", 1), ("cw_square", -1), ("figure_eight", -1)):
            poly, probe = W.SCENES[name]()
            w, dig = W.golden(name)
            self.assertEqual(w, expect, f"{name} golden mispinned")
            self.assertEqual(W.winding_number(poly, probe), expect, f"{name} sign wrong")
            self.assertEqual(W.witness_digest(poly, probe), dig, f"{name} witness drifted")
        poly, _ = W.ccw_square()
        self.assertEqual(W.winding_number(poly, (9, 9)), 0, "exterior probe must read 0")

    def test_loewner_cubic_golden_w2_core(self):
        poly, probe = W.loewner_cubic()
        w, dig = W.golden("loewner_cubic")
        self.assertEqual(w, 2, "the cubic family's core must be doubly wound")
        self.assertEqual(W.winding_number(poly, probe), w, "loewner_cubic invariant drifted")
        self.assertEqual(W.witness_digest(poly, probe), dig, "loewner_cubic witness drifted")
        for p in ((-41987, -8493), (-8412, -17419)):        # the near-curve shoulder probes
            self.assertEqual(W.winding_number(poly, p), 1,
                             f"near-curve probe {p} must read w=1 on the outer shoulder")

    def test_loewner_nonnegative_property(self):
        for name, (builder, probes) in W.LOEWNER.items():
            poly, _ = builder()
            for p in probes():
                self.assertGreaterEqual(W.winding_number(poly, p), 0,
                                        f"{name} probe {p}: negative winding on a Loewner scene")

    def test_witness_recounts_and_tamper_fails(self):
        poly, probe = W.loewner_second()
        cross = W.crossings(poly, probe)
        self.assertEqual(sum(s for (_i, s) in cross), W.winding_number(poly, probe),
                         "the witness sum is not the invariant")
        self.assertTrue(W.check_witness(poly, probe, cross), "genuine witness rejected")
        tampered = list(cross)
        tampered[0] = (tampered[0][0], -tampered[0][1])
        self.assertFalse(W.check_witness(poly, probe, tampered), "tampered witness accepted")
        self.assertNotEqual(W.witness_digest(poly, probe, tampered),
                            W.witness_digest(poly, probe), "tamper did not move the digest")

    def test_cyclic_rotation_invariance(self):
        for name, builder in W.SCENES.items():
            poly, probe = builder()
            w0 = W.winding_number(poly, probe)
            for k in (1, len(poly) // 2, len(poly) - 1):
                self.assertEqual(W.winding_number(poly[k:] + poly[:k], probe), w0,
                                 f"{name}: cyclic rotation by {k} moved the invariant")

    def test_collinear_subdivision_invariance(self):
        poly, probe = W.ccw_square()                        # even coordinates by construction
        w0 = W.winding_number(poly, probe)
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            mid = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
            sub = poly[:i + 1] + [mid] + poly[i + 1:]
            self.assertEqual(W.winding_number(sub, probe), w0,
                             f"subdividing edge {i} moved the invariant")

    def test_translation_invariance(self):
        for name, builder in W.SCENES.items():
            poly, probe = builder()
            w0 = W.winding_number(poly, probe)
            dx, dy = 7, -13
            moved = [(x + dx, y + dy) for (x, y) in poly]
            self.assertEqual(W.winding_number(moved, (probe[0] + dx, probe[1] + dy)), w0,
                             f"{name}: translation moved the invariant")

    def test_reversal_negates(self):
        for name in ("ccw_square", "cw_square", "loewner_wave"):
            poly, probe = W.SCENES[name]()
            self.assertEqual(W.winding_number(list(reversed(poly)), probe),
                             -W.winding_number(poly, probe),
                             f"{name}: reversal must negate w (documented covariance)")

    def test_defect_caught_on_negative_winding(self):
        poly, probe = W.cw_square()
        self.assertEqual(W.winding_number(poly, probe), -1)
        self.assertEqual(W.winding_defect(poly, probe), 1,
                         "the parity defect should misread cw as +1")
        self.assertNotEqual(W.winding_defect(poly, probe), W.winding_number(poly, probe),
                            "the defect did not misclassify (vacuous non-invariance control)")
        poly8, probe8 = W.figure_eight()
        self.assertNotEqual(W.winding_defect(poly8, probe8), W.winding_number(poly8, probe8),
                            "the defect must also misread the figure-eight lobe")

    def test_refusals_typed_and_total(self):
        cases = [
            ([(0, 0), (4, 0)], (1, 1)),                     # fewer than 3 vertices
            ([(0, 0), (4, 0), (4, 0), (0, 4)], (1, 1)),     # repeated consecutive vertex
            ([(0, 0), (4, 0), (0, 4), (0, 0)], (1, 1)),     # repeated across the closure
            ([(0, 0), (4.0, 0), (0, 4)], (1, 1)),           # float vertex
            ([(0, 0), (True, 0), (0, 4)], (1, 1)),          # bool is not a coordinate
            ([(0, 0), (4, 0), (0, 4)], (1, 1.5)),           # float probe
        ]
        for poly, probe in cases:
            with self.assertRaises(W.WindingError) as cm:
                W.winding_number(poly, probe)
            self.assertEqual(cm.exception.code, "WIND-REFUSE", f"wrong code for {poly!r}")

    def test_probe_on_trace_refused(self):
        tri = [(0, 0), (4, 0), (0, 4)]
        for probe in ((2, 0), (0, 0), (2, 2)):              # edge interior, vertex, hypotenuse
            with self.assertRaises(W.WindingError) as cm:
                W.winding_number(tri, probe)
            self.assertEqual(cm.exception.code, "WIND-REFUSE",
                             f"probe {probe} on the trace must WIND-REFUSE")


if __name__ == "__main__":
    unittest.main()
