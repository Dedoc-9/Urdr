# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the composite worst-case latency SLO (`tools/terrain/slo.py`, T3.33, MMO Stage H) — the
end-to-end latency guarantee as ONE certified number, with a SLO-REFUSE when a config cannot meet its target.
worst_case_latency = admission_wait (governor) + horizon (rollback window).

  * REFERENCE — the three pinned configs reproduce their URDRLAT2 digests, deterministically;
  * COMPOSITION — worst_case_latency == admission_wait + worst_case_window (the two bounded parts);
  * ADMISSION SOUNDNESS — the admission_wait formula is a true UPPER BOUND on the governor's actual drain, over
    a corpus of configs (the guarantee is real, not optimistic);
  * ADMISSION EXACT — for equal-cost actors the formula equals the real governor drain exactly;
  * MEETS — a config within the target ADMITS and returns its worst-case latency;
  * REFUSE — a config whose worst-case exceeds the target is a typed SLO-REFUSE;
  * ACTOR-OVER-BUDGET — a single actor bigger than the budget is an OPCOST-REFUSE (from admission_wait);
  * DEFECT DIVERGES — a changed config moves the URDRLAT2 digest.

Composes `govern` (actual drain, for soundness), `horizon` (window), and `opcost`; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import slo as S                                                # noqa: E402
import govern as GV                                            # noqa: E402
import horizon as HZ                                           # noqa: E402
import opcost as OC                                            # noqa: E402


class Slo(unittest.TestCase):
    def setUp(self):
        self.fld = S._flat16()
        self.c = S._actor_cost()

    def test_scene_goldens(self):
        for name in S.SCENES:
            dig = S.scene_result(name)
            self.assertEqual(dig, S.golden(name), f"{name}: slo digest drifted")
            self.assertEqual(S.scene_result(name), dig, f"{name}: nondeterministic")

    def test_composition(self):
        n, budget, hz = 6, 3 * self.c, 2
        self.assertEqual(S.worst_case_latency(n, budget, self.c, hz),
                         S.admission_wait(n, budget, self.c) + HZ.worst_case_window(hz),
                         "worst-case latency must be admission wait + rollback window")

    def test_admission_soundness(self):
        for n in (1, 2, 3, 5, 6, 8, 12, 14):
            for bmult in (1, 2, 3, 5):
                budget = bmult * self.c
                starts = tuple((2, i) for i in range(n))
                actual = len(GV.drain(self.fld, starts, "eeee", S._MS, S._SUB, budget))
                self.assertLessEqual(actual, S.admission_wait(n, budget, self.c),
                                     f"admission_wait must upper-bound the real drain (n={n}, b={bmult}c)")

    def test_admission_exact_equal_cost(self):
        n, budget = 6, 2 * self.c
        starts = tuple((2, i) for i in range(n))
        self.assertEqual(len(GV.drain(self.fld, starts, "eeee", S._MS, S._SUB, budget)),
                         S.admission_wait(n, budget, self.c),
                         "for equal-cost actors the formula is exact")

    def test_meets(self):
        w = S.slo_admit(6, 3 * self.c, self.c, 2, 5)
        self.assertEqual(w, 4, "ceil(6/3) + 2 = 4")

    def test_refuse(self):
        with self.assertRaises(S.SloError) as cm:
            S.slo_admit(12, 2 * self.c, self.c, 5, 8)
        self.assertEqual(cm.exception.code, "SLO-REFUSE", "an over-target config must refuse")

    def test_actor_over_budget(self):
        with self.assertRaises(OC.OpcostError) as cm:
            S.admission_wait(3, self.c - 1, self.c)
        self.assertEqual(cm.exception.code, "OPCOST-REFUSE")

    def test_defect_diverges(self):
        base = S.slo_digest("x", 6, 3 * self.c, self.c, 2, 4, "ADMIT")
        other = S.slo_digest("x", 6, 3 * self.c, self.c, 3, 5, "ADMIT")
        self.assertNotEqual(base, other, "a changed horizon must move the digest")


if __name__ == "__main__":
    unittest.main()
