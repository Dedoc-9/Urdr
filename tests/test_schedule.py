# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/schedule.py — the ADAPTIVE PRIORITY SCHEDULER (URDRSCH1): bandwidth- and
importance-aware refresh scheduling over the clarity-bounded throttle. When more entities are due than a
per-tick BUDGET allows, the scheduler serves them OLDEST-FIRST (starvation-free), importance and eid as
tiebreaks, while membership stays live. Composition over `throttle`, NO new glyph.

  BUDGETED — at most `budget` discretionary refreshes per tick (the bandwidth cap); the over-budget plant
    is caught.
  PRIORITY CORRECT — the refreshed set is exactly the top-`budget` due-known by priority; inversion caught.
  STARVATION-FREE — under a saturated budget, staleness ≤ MAX_STALE + ⌈CAPACITY/budget⌉; the static-priority
    (importance-only) plant starves the coarse and exceeds the bound.
  CLOSED-WORLD EVERY TICK — a deferred entity is still SHOWN (carried); the membership-defer plant that
    drops it breaks closed-world and is caught.
  DETERMINISTIC — a run is a pure function of (ticks, lens, budget); the wall-clock plant diverges.
  REDUCES TO THE THROTTLE — at budget ≥ CAPACITY nothing is deferred; staleness collapses to ≤ MAX_STALE.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import schedule as SC                                           # noqa: E402
import throttle as TH                                           # noqa: E402
import anamorphosis as A                                        # noqa: E402
import perception as PC                                         # noqa: E402


class TheScheduler(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in SC.SCENES:
            self.assertEqual(SC.scene_result(name), SC.golden(name), name)
            self.assertEqual(SC.scene_result(name), SC.scene_result(name), name)

    def test_budget_respected(self):
        ticks, cl = SC._contended()
        rep = SC.run(ticks, cl, A.lens(0, 0), 2)
        self.assertLessEqual(rep["max_disc"], 2, "the scheduler exceeded its refresh budget")
        self.assertGreater(rep["deferrals"], 0, "no contention — the budget was never binding")

    def test_over_budget_plant_bites(self):
        ticks, cl = SC._contended()
        self.assertGreater(SC._run_over_budget(ticks, cl, A.lens(0, 0), 2)["max_disc"], 2)

    def test_reduces_to_throttle_at_high_budget(self):
        """At budget ≥ CAPACITY nothing is ever deferred, so staleness collapses to the throttle's bound."""
        ticks, cl = SC._contended()
        rep = SC.run(ticks, cl, A.lens(0, 0), SC.CAPACITY)
        self.assertEqual(rep["deferrals"], 0)
        self.assertLessEqual(rep["max_stale"], SC.MAX_STALE)


class ThePriority(unittest.TestCase):
    def test_priority_correct(self):
        ticks, cl = SC._contended()
        self.assertTrue(SC.priority_correct(ticks, cl, A.lens(0, 0), 2))

    def test_inversion_plant_starves(self):
        """Serving the youngest-first (priority inversion) starves the oldest — staleness exceeds the bound
        on a run long enough for starvation to manifest, while the honest run stays within it."""
        ticks, cl = SC._contended(24)
        self.assertGreater(SC._run_inversion(ticks, cl, A.lens(0, 0), 1)["max_stale"], SC.stale_bound(1))
        self.assertLessEqual(SC.run(ticks, cl, A.lens(0, 0), 1)["max_stale"], SC.stale_bound(1))


class TheStarvationFreedom(unittest.TestCase):
    def test_staleness_bounded_under_saturated_budget(self):
        ticks, cl = SC._contended(24)
        rep = SC.run(ticks, cl, A.lens(0, 0), 1)               # the tightest budget
        self.assertTrue(SC.staleness_ok(rep, 1))
        self.assertLessEqual(rep["max_stale"], SC.stale_bound(1))

    def test_static_priority_plant_starves(self):
        """Importance-only priority (no age) starves the low-importance coarse entity — its staleness grows
        past the bound; age-first (the law) keeps it bounded (L15)."""
        ticks, cl = SC._contended(24)
        self.assertGreater(SC._run_static_priority(ticks, cl, A.lens(0, 0), 1)["max_stale"],
                           SC.stale_bound(1))
        self.assertLessEqual(SC.run(ticks, cl, A.lens(0, 0), 1)["max_stale"], SC.stale_bound(1))


class TheClosedWorldPerTick(unittest.TestCase):
    def test_closed_world_every_tick(self):
        ticks, cl = SC._contended()
        rep = SC.run(ticks, cl, A.lens(0, 0), 2)
        for t, (ents, walls) in enumerate(ticks):
            self.assertTrue(SC.is_closed_world_at(ents, walls, cl, A.lens(0, 0), rep["transcripts"][t]), t)

    def test_membership_defer_plant_bites(self):
        """Dropping a DEFERRED due entity from the transcript (instead of showing it carried) breaks
        closed-world — the reconstruction becomes a strict subset of the live manifested set."""
        ticks, cl = SC._contended()
        md = SC._run_membership_defer(ticks, cl, A.lens(0, 0), 2)
        bit = any(set(SC.reconstruct(md[t])) != set(A._manifest_under(e, w, cl, A.lens(0, 0)))
                  for t, (e, w) in enumerate(ticks))
        self.assertTrue(bit, "the membership-defer mistake was not caught")


class TheDeterminism(unittest.TestCase):
    def test_pure_run_deterministic_and_replayable(self):
        ticks, cl = SC._contended()
        L = A.lens(0, 0)
        a = SC.run(ticks, cl, L, 2)["transcripts"]
        self.assertEqual(a, SC.run(ticks, cl, L, 2)["transcripts"])
        state = {}
        for t, (ents, walls) in enumerate(ticks):
            tr, state, _m, _r, _d = SC.step(state, ents, walls, cl, L, t, 2)
            self.assertEqual(tr, a[t], f"step replay diverged at tick {t}")

    def test_wallclock_plant_diverges(self):
        ticks, cl = SC._contended()
        L = A.lens(0, 0)
        pure = SC.run(ticks, cl, L, 2)["transcripts"]
        self.assertEqual(pure, SC.run(ticks, cl, L, 2, _clock=lambda: 0)["transcripts"])
        self.assertNotEqual(pure, SC.run(ticks, cl, L, 2, _clock=lambda: 1)["transcripts"])


class TheShapeAndHidden(unittest.TestCase):
    def test_constant_shape_every_tick(self):
        ticks, cl = SC._contended()
        for tr in SC.run(ticks, cl, A.lens(0, 0), 2)["transcripts"]:
            self.assertEqual(len(tr), SC.transcript_bytes_len())

    def test_hidden_change_byte_identical(self):
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        L = A.lens(0, 0)
        base = SC._seq({1: [(4, 0)] * 5, 2: [(-6, 0)] * 5}, 5)   # id2 behind → hidden
        moved = SC._seq({1: [(4, 0)] * 5, 2: [(-6, 3)] * 5}, 5)
        self.assertEqual(SC.run(base, cl, L, 2)["transcripts"], SC.run(moved, cl, L, 2)["transcripts"])


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = SC.sweep_digest()
        self.assertEqual(d1, SC.sweep_digest(), "deterministic")
        self.assertEqual(d1, SC.sweep_golden(), "sweep drifted from golden")
        rep = SC.sweep()
        self.assertGreater(rep["deferrals"], 0, "the budget was never binding")
        self.assertGreater(rep["departures"], 0, "no entity ever departed")
        self.assertGreater(rep["stale_seen"], 0, "staleness was never exercised")

    def test_sweep_bites_leaked_hidden(self):
        orig = A._manifest_under
        A._manifest_under = lambda entities, walls, cl, L: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(SC.ScheduleError):
                SC.sweep()
        finally:
            A._manifest_under = orig
        self.assertEqual(SC.sweep_digest(), SC.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
