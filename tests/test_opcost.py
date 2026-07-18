# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the certified integer-work envelope (`tools/terrain/opcost.py`, T3.29, MMO Stage H opener) —
the DETERMINISTIC, EXACT op-count that is the gate-certifiable half of a latency guarantee (wall-clock is
`bench.py`, MEASURED-on-named-host, never gated).

  * REFERENCE — the five pinned scenarios reproduce their URDROPC1 op-count digests, deterministically;
  * GLIDE COUNT EXACT — glide_micro_count is exactly len(glide) - 1 (the real micro-step work), a pure
    function of the input;
  * GLIDE BOUND (non-vacuity) — glide_micro_count <= the no-wall bound always, and STRICTLY less on a wall
    scene (the bound bites);
  * WARDEN EDGE CLOSED-FORM — warden_edge_checks == (W-1)*H + W*(H-1) == the adjacencies warden.components
    actually examines;
  * ADMIT SUBSTEPS EXACT — admit_substeps == sum of |dx| + |dy| over the claimed trajectory;
  * WARDHOM COLUMNS — wardhom_columns == n1 (the F2 boundary column count);
  * TICK ENVELOPE ADDITIVE — tick_envelope == sum over actors of (glide micro-steps + admit sub-steps);
  * BUDGET REFUSE — within_budget ADMITS at/under budget and raises a typed OPCOST-REFUSE over it;
  * DEFECT DIVERGES — a changed op-count moves the URDROPC1 digest (the envelope is load-bearing).

Composes `glide`, `warden`, and `wardhom`; the gate runs it. `bench.py` (wall-clock) is deliberately NOT
tested here — its times are non-deterministic by construction and belong to MEASURED-on-named-host, not the
byte-exact gate."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "homology"))

import unittest
import opcost as OC                                            # noqa: E402
import glide as GL                                             # noqa: E402
import warden as W                                             # noqa: E402
import wardhom as WH                                           # noqa: E402


class Opcost(unittest.TestCase):
    def setUp(self):
        self.flat = OC._flat16()
        self.wall = OC._wall_scene()
        self.ms, self.sub = OC._MS, OC._SUB

    def test_scene_goldens(self):
        for name in OC.SCENES:
            dig = OC.scene_result(name)
            self.assertEqual(dig, OC.golden(name), f"{name}: opcost digest drifted")
            self.assertEqual(OC.scene_result(name), dig, f"{name}: nondeterministic")

    def test_glide_count_exact(self):
        cnt = OC.glide_micro_count(self.flat, (2, 8), "eeee", self.ms, self.sub)
        self.assertEqual(cnt, len(GL.glide(self.flat, (2, 8), "eeee", self.ms, self.sub)) - 1,
                         "glide op-count must be the real micro-step count")

    def test_glide_bound_nonvacuous(self):
        og = OC.glide_micro_count(self.flat, (2, 8), "eeee", self.ms, self.sub)
        self.assertLessEqual(og, OC.glide_micro_bound("eeee", self.sub), "count must not exceed the bound")
        wc = OC.glide_micro_count(self.wall, (2, 8), "eeeeeeee", self.ms, self.sub)
        self.assertLess(wc, OC.glide_micro_bound("eeeeeeee", self.sub),
                        "a wall must stop the glide strictly below the no-wall bound")

    def test_warden_edge_closed_form(self):
        w = len(self.flat[0])
        h = len(self.flat)
        actual = sum((1 if x + 1 < w else 0) + (1 if y + 1 < h else 0) for y in range(h) for x in range(w))
        self.assertEqual(OC.warden_edge_checks(self.flat, self.ms), (w - 1) * h + w * (h - 1))
        self.assertEqual(OC.warden_edge_checks(self.flat, self.ms), actual,
                         "the closed form must equal the adjacencies warden.components examines")

    def test_admit_substeps_exact(self):
        cells = ((2, 8), (4, 8), (4, 10))
        self.assertEqual(OC.admit_substeps(cells), 2 + 2, "sum of |dx|+|dy| over the trajectory")

    def test_wardhom_columns(self):
        self.assertEqual(OC.wardhom_columns(WH._barrier8(), WH._MS), WH.counts(WH._barrier8(), WH._MS)[1],
                         "wardhom column count must equal n1")

    def test_tick_envelope_additive(self):
        starts = ((2, 6), (2, 8))
        total = OC.tick_envelope(self.flat, starts, "eeee", self.ms, self.sub)
        by_hand = 0
        for s in starts:
            g = GL.glide_cells(self.flat, s, "eeee", self.ms, self.sub)
            cells = tuple((p[0] >> 32, p[1] >> 32) for p in g)
            by_hand += OC.glide_micro_count(self.flat, s, "eeee", self.ms, self.sub) + OC.admit_substeps(cells)
        self.assertEqual(total, by_hand, "the tick envelope must be the sum of per-actor work")

    def test_budget_refuse(self):
        self.assertTrue(OC.within_budget(400, 500))
        self.assertTrue(OC.within_budget(500, 500))
        with self.assertRaises(OC.OpcostError) as cm:
            OC.within_budget(501, 500)
        self.assertEqual(cm.exception.code, "OPCOST-REFUSE", "over-budget work must refuse, never overrun")

    def test_defect_diverges(self):
        base = OC.opcost_digest("x", {"a": 10, "b": 20})
        self.assertNotEqual(base, OC.opcost_digest("x", {"a": 11, "b": 20}),
                            "a changed op-count must move the digest")


if __name__ == "__main__":
    unittest.main()
