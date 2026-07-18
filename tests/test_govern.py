# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the per-tick work governor (`tools/terrain/govern.py`, T3.30, MMO Stage H) — the `opcost`
envelope turned into LIVE enforcement: admit a FIFO prefix within the tick op-budget, defer the rest, refuse a
single over-budget actor. Self-contained (no network, no chunking).

  * REFERENCE — the three pinned schedules reproduce their URDROPC2 digests, deterministically;
  * ACTOR COST TIE — actor_cost is exactly the opcost contribution (glide micro-steps + admit sub-steps);
  * NEVER-OVERRUN (the guarantee) — every admitted tick's spent work is <= budget, across a range of budgets;
  * PROGRESS — every tick admits >= 1 actor and drain terminates in <= N ticks (no deadlock);
  * BOUNDED-WAIT / FIFO — wait_ticks is non-decreasing (in-order) and <= N (no starvation);
  * SINGLE OVER-BUDGET REFUSE — an actor whose cost alone exceeds the budget is a typed OPCOST-REFUSE;
  * CONSERVATION — admitted + deferred == all actors, and the admitted set is the in-order prefix (none lost,
    duplicated, or reordered);
  * KNOWN SCHEDULES — fits_one=(5,), split_two=(3,2), one_each=(1,1,1,1,1);
  * DEFECT DIVERGES — a changed budget / schedule moves the URDROPC2 digest.

Composes `opcost` and `glide`; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import govern as G                                             # noqa: E402
import opcost as OC                                            # noqa: E402


class Govern(unittest.TestCase):
    def setUp(self):
        self.fld = G._flat16()
        self.ms, self.sub = G._MS, G._SUB
        self.starts, self.cmds = G._STARTS, G._CMDS
        self.a = G._actor_cost_flat()

    def test_scene_goldens(self):
        for name in G.SCENES:
            dig = G.scene_result(name)
            self.assertEqual(dig, G.golden(name), f"{name}: govern digest drifted")
            self.assertEqual(G.scene_result(name), dig, f"{name}: nondeterministic")

    def test_actor_cost_tie(self):
        s = self.starts[0]
        g = __import__("glide").glide_cells(self.fld, s, self.cmds, self.ms, self.sub)
        cells = tuple((p[0] >> 32, p[1] >> 32) for p in g)
        want = OC.glide_micro_count(self.fld, s, self.cmds, self.ms, self.sub) + OC.admit_substeps(cells)
        self.assertEqual(G.actor_cost(self.fld, s, self.cmds, self.ms, self.sub), want,
                         "actor_cost must be the opcost contribution")

    def test_never_overrun(self):
        for budget in (self.a, 2 * self.a, 3 * self.a, 5 * self.a, 100 * self.a):
            queue = self.starts
            while queue:
                _adm, deferred, spent = G.admit_tick(self.fld, queue, self.cmds, self.ms, self.sub, budget)
                self.assertLessEqual(spent, budget, f"budget {budget}: an admitted tick overran")
                queue = deferred

    def test_progress(self):
        counts = G.drain(self.fld, self.starts, self.cmds, self.ms, self.sub, self.a)
        self.assertTrue(all(c >= 1 for c in counts), "every tick must admit at least one actor")
        self.assertLessEqual(len(counts), len(self.starts), "drain must terminate in <= N ticks")

    def test_bounded_wait_fifo(self):
        w = G.wait_ticks(self.fld, self.starts, self.cmds, self.ms, self.sub, 2 * self.a)
        self.assertEqual(len(w), len(self.starts), "every actor must be served")
        self.assertEqual(list(w), sorted(w), "waits must be non-decreasing (FIFO, in-order)")
        self.assertLessEqual(max(w), len(self.starts), "no actor waits more than N ticks")

    def test_single_over_budget_refuse(self):
        with self.assertRaises(OC.OpcostError) as cm:
            G.admit_tick(self.fld, self.starts, self.cmds, self.ms, self.sub, self.a - 1)
        self.assertEqual(cm.exception.code, "OPCOST-REFUSE", "an actor bigger than the budget must refuse")

    def test_conservation(self):
        adm, deferred, _ = G.admit_tick(self.fld, self.starts, self.cmds, self.ms, self.sub, 2 * self.a)
        self.assertEqual(len(adm) + len(deferred), len(self.starts), "no actor lost or duplicated")
        self.assertEqual(adm, self.starts[:len(adm)], "admitted must be the in-order prefix")
        self.assertEqual(deferred, self.starts[len(adm):], "deferred must be the in-order suffix")

    def test_known_schedules(self):
        self.assertEqual(G.scene_schedule("fits_one"), (5,))
        self.assertEqual(G.scene_schedule("split_two"), (3, 2))
        self.assertEqual(G.scene_schedule("one_each"), (1, 1, 1, 1, 1))

    def test_defect_diverges(self):
        base = G.govern_digest("x", self.fld, self.starts, self.cmds, self.ms, self.sub, 3 * self.a)
        other = G.govern_digest("x", self.fld, self.starts, self.cmds, self.ms, self.sub, 2 * self.a)
        self.assertNotEqual(base, other, "a changed budget must move the schedule digest")


if __name__ == "__main__":
    unittest.main()
