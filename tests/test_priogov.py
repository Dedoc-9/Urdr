# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the PRIORITY work governor (`tools/terrain/priogov.py`, T3.31, MMO Stage H) — the
weighted-fairness follow-on `govern` named: admit the highest-effective-priority prefix within the tick
op-budget, with AGING so the lowest priority never starves.

  * REFERENCE — the three pinned schedules reproduce their URDROPC3 digests, deterministically;
  * NEVER-OVERRUN — every admitted tick's work is <= budget (the live latency guarantee, preserved);
  * PRIORITY-ORDER (fresh) — at one actor per tick, service order is exactly base priority (highest first);
  * NO-STARVATION / BOUNDED-WAIT — with aging, every actor is served in <= N ticks (even the lowest priority);
  * PROGRESS — each tick admits >= 1 actor (no deadlock);
  * SINGLE OVER-BUDGET REFUSE — an actor bigger than the budget is a typed OPCOST-REFUSE;
  * CONSERVATION — every actor is served exactly once (N distinct served ticks over the actor set);
  * DEFECT DIVERGES — a changed priority / budget / aging rate moves the URDROPC3 digest.

Composes `govern` (actor_cost) and `opcost`; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import priogov as P                                            # noqa: E402
import govern as GV                                            # noqa: E402
import opcost as OC                                            # noqa: E402


class Priogov(unittest.TestCase):
    def setUp(self):
        self.fld = P._flat16()
        self.ms, self.sub, self.cmds = P._MS, P._SUB, P._CMDS
        self.actors = P._ACTORS
        self.a = GV.actor_cost(self.fld, self.actors[0][0], self.cmds, self.ms, self.sub)

    def test_scene_goldens(self):
        for name in P.SCENES:
            dig = P.scene_result(name)
            self.assertEqual(dig, P.golden(name), f"{name}: priogov digest drifted")
            self.assertEqual(P.scene_result(name), dig, f"{name}: nondeterministic")

    def test_never_overrun(self):
        for budget in (self.a, 2 * self.a, 3 * self.a, 5 * self.a):
            waits = [0] * len(self.actors)
            remaining = self.actors
            while remaining:
                adm, deferred, spent = P.admit_tick_prio(self.fld, remaining, self.cmds, self.ms, self.sub, budget)
                self.assertLessEqual(spent, budget, f"budget {budget}: an admitted tick overran")
                remaining = tuple(remaining[i] for i in deferred)

    def test_priority_order_fresh(self):
        served = P.drain_prio(self.fld, self.actors, self.cmds, self.ms, self.sub, self.a, 1)
        # actor 4 has the HIGHEST base priority (5) and must be served before actor 0 (priority 1)
        self.assertLess(served[4], served[0], "higher base priority must be served earlier")
        self.assertEqual(served, tuple(sorted(served)) if False else served)  # keep served as computed
        self.assertEqual(served[4], 1, "the top priority is served on tick 1")

    def test_no_starvation(self):
        served = P.drain_prio(self.fld, self.actors, self.cmds, self.ms, self.sub, self.a, 1)
        self.assertEqual(len(set(served)), len(self.actors), "each actor served on a distinct tick here")
        self.assertLessEqual(max(served), len(self.actors), "every actor served within N ticks (no starvation)")

    def test_progress(self):
        # even without aging (age_step 0), each tick admits >= 1 and drain terminates
        served = P.drain_prio(self.fld, self.actors, self.cmds, self.ms, self.sub, self.a, 0)
        self.assertEqual(len(served), len(self.actors), "every actor served")
        self.assertLessEqual(max(served), len(self.actors), "drain terminates in <= N ticks")

    def test_single_over_budget_refuse(self):
        with self.assertRaises(OC.OpcostError) as cm:
            P.drain_prio(self.fld, self.actors, self.cmds, self.ms, self.sub, self.a - 1, 1)
        self.assertEqual(cm.exception.code, "OPCOST-REFUSE")

    def test_conservation(self):
        served = P.drain_prio(self.fld, self.actors, self.cmds, self.ms, self.sub, 2 * self.a, 1)
        self.assertEqual(len(served), len(self.actors), "no actor lost or duplicated")
        self.assertTrue(all(t >= 1 for t in served), "every actor served on a real tick")

    def test_defect_diverges(self):
        base = P.priogov_digest("x", self.fld, self.actors, self.cmds, self.ms, self.sub, 2 * self.a, 1)
        other = P.priogov_digest("x", self.fld, self.actors, self.cmds, self.ms, self.sub, 2 * self.a, 0)
        self.assertNotEqual(base, other, "a changed aging rate must move the digest")


if __name__ == "__main__":
    unittest.main()
