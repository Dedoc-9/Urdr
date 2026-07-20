# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/commuteprop.py — the property-based falsifier stage (Tier-2, URDRCPS1).

`commute` proves the diamond on four hand-chosen scenes; this sweeps it with a seeded generator and
INDEPENDENT oracles (a brute-permutation orbit for the head/field, chunk geometry for the rank) so the
∀-law faces an adversary, not a fixed corpus. The oracles are what the module-under-test cannot read
(the anti-Goodhart rule): a bug in certify/closure/predict cannot hide inside its own answer.

  DIGEST — the fixed-seed sweep reproduces its pinned aggregate digest, deterministically.
  DIAMOND — the brute-permutation orbit is a SINGLETON (order cannot matter), and non-vacuous
    (edits actually mutate the world; both ranks occur).
  RANK — commute.predict matches INDEPENDENT chunk geometry (not certify's own predict — circular).
  CONTESTED — a same-cell pair REFUSES (load-bearing).
  CLOSURE — commute.closure's head equals the brute orbit's head.
  THE SWEEP BITES — a mutated commute module makes the sweep RAISE, not return a digest (L15).

Every test can go red (L5); the plants bite before the golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import commuteprop as CP                                        # noqa: E402
import commute as CM                                            # noqa: E402
import terraform as TF                                          # noqa: E402


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_deterministic(self):
        """The fixed-seed sweep reproduces its pinned aggregate digest, twice."""
        d1 = CP.sweep_digest()
        d2 = CP.sweep_digest()
        self.assertEqual(d1, d2, "the sweep must be deterministic")
        self.assertEqual(d1, CP.golden(), "the sweep digest drifted from its golden")

    def test_report_counters_are_non_vacuous(self):
        """The sweep exercised BOTH ranks, every contested pair refused, and edits actually mutated."""
        rep = CP.sweep()
        self.assertEqual(rep["scenarios"], CP.COUNT)
        self.assertGreater(rep["rank0"], 0, "no rank-0 (different-chunk) pairs — vacuous")
        self.assertGreater(rep["rank1"], 0, "no rank-1 (same-chunk) pairs — vacuous")
        self.assertEqual(rep["contested"], CP.COUNT, "not every contested pair refused")
        self.assertGreater(rep["changed"], 0, "no scenario changed the world — the edits were no-ops")


class TheOracles(unittest.TestCase):
    def _scenarios(self, seed, n):
        r = CP._LCG(seed)
        return [CP.gen_scenario(r, CP.CSIZE, CP.W, CP.H) for _ in range(n)]

    def test_diamond_orbit_is_a_singleton(self):
        """THE INDEPENDENT DIAMOND ORACLE: for every generated scenario, applying all permutations of
        the rebased edits lands ONE head AND one field — and at least one scenario actually changed
        the world (non-vacuity)."""
        changed = 0
        for fld, recs, _cells in self._scenarios(777, 120):
            heads, fields = CP.brute_orbit(fld, CP.CSIZE, recs)
            self.assertEqual(len(heads), 1, "orders produced different head manifests")
            self.assertEqual(len(fields), 1, "orders produced different fields")
            if next(iter(fields)) != fld:
                changed += 1
        self.assertGreater(changed, 0, "NON-VACUITY: no generated scenario mutated the world")

    def test_predict_matches_independent_geometry(self):
        """commute.predict equals chunk geometry computed WITHOUT commute (the anti-circularity rule),
        over generated scenarios and a constructed load-bearing same-chunk pair."""
        for fld, recs, _cells in self._scenarios(4242, 120):
            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    _p, xa, ya, _o, _n = TF.restore_edit(recs[i])
                    _q, xb, yb, _o2, _n2 = TF.restore_edit(recs[j])
                    exp = CP._geo_rank(CP.CSIZE, xa, ya, xb, yb)
                    self.assertEqual(CM.predict(CP.CSIZE, xa, ya, xb, yb), exp)
        # load-bearing: two distinct cells in the SAME chunk are rank 1 by geometry, not 0
        self.assertEqual(CP._geo_rank(4, 0, 0, 1, 0), 1, "same-chunk distinct cells are rank 1")
        self.assertEqual(CP._geo_rank(4, 0, 0, 4, 0), 0, "cross-chunk cells are rank 0")

    def test_contested_pair_refuses(self):
        """A same-cell pair on a generated world REFUSES (COMMUTE-REFUSE) — the certified conflict."""
        for fld, _recs, cells in self._scenarios(99, 60):
            x, y = cells[0]
            p = TF.parent_address(fld, CP.CSIZE)
            ra = TF.edit_record(p, x, y, fld[y][x], fld[y][x] + 3)
            rb = TF.edit_record(p, x, y, fld[y][x], fld[y][x] - 3)
            with self.assertRaises(CM.CommuteError):
                CM.certify(fld, CP.CSIZE, ra, rb)

    def test_closure_head_equals_brute_orbit(self):
        """commute.closure's head equals the INDEPENDENT brute-permutation orbit's single head."""
        for fld, recs, _cells in self._scenarios(20260720, 60):
            heads, _fields = CP.brute_orbit(fld, CP.CSIZE, recs)
            ch, _certs = CM.closure(fld, CP.CSIZE, recs)
            self.assertEqual(ch, next(iter(heads)), "closure disagrees with the brute oracle")


class TheSweepBites(unittest.TestCase):
    """L15 at the sweep level: a mutated commute module makes the sweep RAISE, not silently pass."""

    def test_predict_mutant_falsifies_the_sweep(self):
        orig = CM.predict
        CM.predict = lambda cs, xa, ya, xb, yb: 0               # MUTANT: always rank 0
        try:
            with self.assertRaises(CP.SweepError):
                CP.sweep()
        finally:
            CM.predict = orig
        self.assertEqual(CP.sweep_digest(), CP.golden(), "the module must be clean after the revert")

    def test_closure_mutant_falsifies_the_sweep(self):
        orig = CM.closure
        CM.closure = lambda f, cs, recs: (TF.parent_address(f, cs), ())   # MUTANT: identity head
        try:
            with self.assertRaises(CP.SweepError):
                CP.sweep()
        finally:
            CM.closure = orig


if __name__ == "__main__":
    unittest.main()
