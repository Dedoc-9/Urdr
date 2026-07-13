# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for persistent homology (`tools/intla/persim.py`).

  * REFERENCE — the circle reproduces its pinned barcode digest, deterministically;
  * BETTI — the circle has b0=1, b1=1; the disk has b1=0 (its loop is filled at t=2);
  * INVARIANCE — reordering simplices within one filtration value gives the same barcode;
  * DEFECT — the un-reduced pairing (colliding lows) gives a wrong barcode;
  * REFUSAL — a non-monotone filtration is PH-REFUSEd."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "intla")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import persim as P                                          # noqa: E402


def _golden(name):
    with open(os.path.join(_ROOT, "tools", "intla", "conformance_persim.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AssertionError(f"golden {name} missing")


class Persim(unittest.TestCase):
    def test_circle_barcode_golden(self):
        bars = P.persistence(P.circle())
        self.assertEqual(P.barcode_digest(bars), _golden("circle"), "circle barcode drifted")
        self.assertEqual(P.barcode_digest(P.persistence(P.circle())),
                         P.barcode_digest(bars), "nondeterministic")

    def test_betti(self):
        self.assertEqual(P.betti(P.persistence(P.circle())), {0: 1, 1: 1}, "circle Betti wrong")
        self.assertEqual(P.betti(P.persistence(P.disk())), {0: 1}, "disk should have b1=0 (loop filled)")

    def test_disk_distinguishes_from_circle(self):
        self.assertNotEqual(P.barcode_digest(P.persistence(P.disk())),
                            P.barcode_digest(P.persistence(P.circle())),
                            "disk and circle have the same barcode")

    def test_order_invariance(self):
        c = P.circle()
        reordered = c[:4] + [c[7], c[5], c[4], c[6]]         # edges permuted within t=1
        self.assertEqual(P.persistence(reordered), P.persistence(c),
                         "reordering within a filtration value changed the barcode")

    def test_defect_differs(self):
        c = P.circle()
        self.assertNotEqual(P.persistence_defect(c), P.persistence(c),
                            "the un-reduced pairing did not misclassify")

    def test_non_monotone_refused(self):
        bad = [(1, 0, [0, 1]), (0, 0, []), (0, 0, [])]       # an edge before its vertices
        with self.assertRaises(P.PersimError):
            P.persistence(bad)


if __name__ == "__main__":
    unittest.main()
