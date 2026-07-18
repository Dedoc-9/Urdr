# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the per-CLASS worst-case latency SLO (`tools/terrain/clslo.py`, T3.34, MMO Stage H) — the
priority-class refinement of the composite slo: each priority tier gets its OWN certified worst-case latency
ceil(N>=p / floor(budget/cost)) + horizon, with a by-name CLSLO-REFUSE when a tier cannot meet its target.

  * REFERENCE — the three pinned configs reproduce their URDRLAT3 digests, deterministically;
  * REFINEMENT — a higher priority class carries a tighter-or-equal bound (monotone in priority);
  * SINGLE-CLASS == SLO — one class reduces exactly to the composite slo's uniform worst-case latency;
  * ADMISSION SOUNDNESS — the per-class bound EQUALS priogov's real per-class last-served tick over a corpus
    (exact for equal-cost actors — the guarantee is checked against the scheduler, not assumed);
  * MEETS — a config where every tier meets its target ADMITS and returns the per-class table;
  * PER-CLASS REFUSE — a tier whose worst-case exceeds its own target is a typed CLSLO-REFUSE naming that tier;
  * ACTOR-OVER-BUDGET — a single actor bigger than the budget is an OPCOST-REFUSE;
  * DEFECT DIVERGES — a changed horizon moves the URDRLAT3 digest.

Composes `priogov` (per-class drain, for soundness), `slo` (the one-class bound), `horizon`, and `opcost`; the
gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import clslo as CL                                              # noqa: E402
import slo as SL                                                # noqa: E402
import opcost as OC                                             # noqa: E402


class Clslo(unittest.TestCase):
    def setUp(self):
        self.fld = CL._flat16()
        self.c = CL._actor_cost()
        self.classes = ((3, 2), (2, 3), (1, 4))

    def test_scene_goldens(self):
        for name in CL.SCENES:
            dig = CL.scene_result(name)
            self.assertEqual(dig, CL.golden(name), f"{name}: clslo digest drifted")
            self.assertEqual(CL.scene_result(name), dig, f"{name}: nondeterministic")

    def test_refinement_monotone(self):
        tbl = CL.class_table(self.classes, 3 * self.c, self.c, 2)
        for i in range(len(tbl) - 1):
            self.assertLessEqual(tbl[i][1], tbl[i + 1][1],
                                 "a higher priority class must carry a tighter-or-equal bound")
        self.assertLess(tbl[0][1], tbl[-1][1], "premium must beat free in this config (real differentiation)")

    def test_single_class_equals_slo(self):
        for n in (1, 5, 6, 9):
            for bmult in (1, 2, 3):
                self.assertEqual(
                    CL.class_worst_case_latency(((1, n),), bmult * self.c, self.c, 2, 1),
                    SL.worst_case_latency(n, bmult * self.c, self.c, 2),
                    "the one-class case must equal the composite slo's uniform bound")

    def test_admission_soundness(self):
        corpus = (((3, 2), (2, 3), (1, 4)), ((5, 1), (3, 2), (1, 3)), ((2, 4), (1, 2)),
                  ((7, 2), (5, 2), (3, 2), (1, 2)), ((1, 5),))
        for cfg in corpus:
            for bmult in (1, 2, 3, 4):
                for age in (0, 1, 3):
                    self.assertTrue(
                        CL.soundness_holds(self.fld, cfg, CL._CMDS, CL._MS, CL._SUB, bmult * self.c, age),
                        f"per-class bound must equal priogov's real drain (cfg={cfg} b={bmult}c age={age})")

    def test_meets(self):
        tbl = CL.class_slo_admit(self.classes, 3 * self.c, self.c, 2, ((3, 3), (2, 4), (1, 5)))
        self.assertEqual(tbl, ((3, 3), (2, 4), (1, 5)), "the admitted table must carry each tier's latency")

    def test_per_class_refuse(self):
        with self.assertRaises(CL.ClsloError) as cm:
            CL.class_slo_admit(self.classes, 3 * self.c, self.c, 2, ((3, 2), (2, 4), (1, 5)))
        self.assertEqual(cm.exception.code, "CLSLO-REFUSE", "an over-target tier must refuse")
        self.assertEqual(cm.exception.priority, 3, "the refuse must name the failing tier (premium p3)")

    def test_actor_over_budget(self):
        with self.assertRaises(OC.OpcostError) as cm:
            CL.class_admission_wait(((1, 3),), self.c - 1, self.c, 1)
        self.assertEqual(cm.exception.code, "OPCOST-REFUSE")

    def test_defect_diverges(self):
        base = CL.clslo_digest("x", self.classes, 3 * self.c, self.c, 2,
                               CL.class_table(self.classes, 3 * self.c, self.c, 2), "ADMIT")
        other = CL.clslo_digest("x", self.classes, 3 * self.c, self.c, 3,
                                CL.class_table(self.classes, 3 * self.c, self.c, 3), "ADMIT")
        self.assertNotEqual(base, other, "a changed horizon must move the digest")


if __name__ == "__main__":
    unittest.main()
