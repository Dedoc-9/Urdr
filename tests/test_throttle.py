# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/throttle.py — the CLARITY-BOUNDED UPDATE THROTTLE (URDRTHR1): deterministic
simulation-rate decoupling, the third pillar the focal lens unlocks. The same awareness the lens computes
bounds a per-entity POSITION-refresh rate (rate = 2^shift), decoupling client compute from the global sim
rate by perceptual relevance. Composition over `anamorphosis`, NO new glyph.

  THE SEPARATION — the throttle delays POSITION, never PRESENCE: MEMBERSHIP is the live manifested set
    (closed-world every tick, no ghosts), POSITION is refreshed on the clarity cadence and carried between.
  BOUNDED STALENESS — every shown position is ≤ 2^COARSEST − 1 ticks old (every rate divides 2^COARSEST, so
    the tick T mod 2^COARSEST == 0 refreshes ALL); a sharp entity is never stale.
  DETERMINISTIC REPLAY — a run is a pure function of (tick sequence, lens); the wall-clock plant diverges.
  REAL THROTTLE — the refreshed count is strictly fewer than refresh-everything-every-tick (measured).
  NO TIMING CHANNEL — constant-shape every tick; a change to a hidden entity is byte-identical.
  REDUCES TO ANAMORPHOSIS — at the identity lens every rate is 1, every entity live every tick.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import throttle as TH                                           # noqa: E402
import anamorphosis as A                                        # noqa: E402
import perception as PC                                         # noqa: E402


def _d(i):
    return TH._d(i)


def _cl():
    return PC.client(0, 0, 1, 0, 3, 2, 400, 0)


class TheThrottle(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in TH.SCENES:
            self.assertEqual(TH.scene_result(name), TH.golden(name), name)
            self.assertEqual(TH.scene_result(name), TH.scene_result(name), name)

    def test_real_throttle_saves_compute(self):
        """The point of the rung: a coarse entity is refreshed less than every tick, so the refreshed count
        is STRICTLY fewer than refresh-everything-every-tick."""
        ticks, cl = TH._paths_scene()
        rep = TH.run(ticks, cl, A.lens(0, 0))
        self.assertLess(rep["refresh_total"], rep["manifest_total"], "the throttle saved no compute")
        self.assertGreater(rep["carries"], 0, "nothing was ever carried")

    def test_sharp_is_live_coarse_is_carried(self):
        ticks, cl = TH._paths_scene()
        self.assertTrue(TH.sharp_is_live(ticks, cl, A.lens(0, 0)), "a sharp entity lagged")

    def test_reduces_to_anamorphosis_at_identity_lens(self):
        """At the identity lens (focus saturating) every rate is 1 — every manifested entity is refreshed
        every tick, live and exact: the no-throttle corner, per-tick anamorphosis."""
        ticks, cl = TH._paths_scene()
        L = A.lens(0, A.COARSEST)
        state = {}
        for t, (ents, walls) in enumerate(ticks):
            _tr, state, man, _r = TH.step(state, ents, walls, cl, L, t)
            for eid in man:
                self.assertEqual(TH.rate_of(A.shift_of(ents, cl, L, eid)), 1)
                self.assertEqual(state[eid][:2], (ents[eid][0], ents[eid][1]), "not exact at ⊤")
                self.assertEqual(state[eid][3], t, "not live at ⊤")


class TheClosedWorldPerTick(unittest.TestCase):
    def test_closed_world_every_tick(self):
        ticks, cl = TH._paths_scene()
        L = A.lens(0, 0)
        rep = TH.run(ticks, cl, L)
        for t, (ents, walls) in enumerate(ticks):
            self.assertTrue(TH.is_closed_world_at(ents, walls, cl, L, rep["transcripts"][t]), f"tick {t}")

    def test_ghost_plant_bites(self):
        """A departed entity whose last position lingers is a GHOST — addressable but not in the live
        manifested set; the closed-world-per-tick property must catch it."""
        cl = PC.client(0, 0, 1, 0, 1, 2, 400, 0)               # narrow wedge → id1 drifts out
        ticks = TH._seq_from_paths({1: [(6, t * 3) for t in range(6)]}, 6)
        ghost = TH._run_ghost(ticks, cl, A.lens(0, 0))
        bit = any(set(TH.reconstruct(ghost[t])) != set(A._manifest_under(e, w, cl, A.lens(0, 0)))
                  for t, (e, w) in enumerate(ticks))
        self.assertTrue(bit, "the ghost was not caught")
        # the honest run drops the departed entity
        self.assertEqual(TH.reconstruct(TH.run(ticks, cl, A.lens(0, 0))["transcripts"][-1]), {})

    def test_membership_throttle_plant_bites(self):
        """Throttling MEMBERSHIP (delaying a newly-entered coarse entity's presence until its cadence)
        breaks closed-world — the reconstruction is a strict subset of the live manifested set."""
        cl = _cl()
        ticks = TH._seq_from_paths({3: [(-5, 0), (17, 0), (17, 0), (17, 0)]}, 4)  # id3 enters coarse at t1
        mt = TH._run_membership_throttle(ticks, cl, A.lens(0, 0))
        self.assertEqual(TH.reconstruct(mt[1]), {}, "the delayed entity should be missing under the plant")
        self.assertIn(3, A._manifest_under(ticks[1][0], ticks[1][1], cl, A.lens(0, 0)))
        self.assertFalse(TH.is_closed_world_at(ticks[1][0], ticks[1][1], cl, A.lens(0, 0), mt[1]))


class TheBoundedStaleness(unittest.TestCase):
    def test_staleness_within_bound(self):
        ticks, cl = TH._paths_scene()
        rep = TH.run(ticks, cl, A.lens(0, 0))
        self.assertTrue(TH.staleness_ok(rep))
        self.assertLessEqual(rep["max_stale"], TH.MAX_STALE)

    def test_unbounded_plant_bites(self):
        """Never refreshing after entry lets staleness grow without bound — on a run longer than
        2^COARSEST the plant exceeds the bound while the honest run stays within it."""
        cl = _cl()
        ticks = TH._seq_from_paths({3: [(17, 0)] * 12}, 12)    # coarse, continuously manifested
        self.assertGreater(TH._run_unbounded(ticks, cl, A.lens(0, 0))["max_stale"], TH.MAX_STALE)
        self.assertLessEqual(TH.run(ticks, cl, A.lens(0, 0))["max_stale"], TH.MAX_STALE)


class TheDeterminism(unittest.TestCase):
    def test_pure_run_is_deterministic_and_replayable(self):
        ticks, cl = TH._paths_scene()
        L = A.lens(0, 0)
        a = TH.run(ticks, cl, L)["transcripts"]
        self.assertEqual(a, TH.run(ticks, cl, L)["transcripts"], "run is not a pure function")
        # step-replay reproduces the run tick-for-tick
        state = {}
        for t, (ents, walls) in enumerate(ticks):
            tr, state, _m, _r = TH.step(state, ents, walls, cl, L, t)
            self.assertEqual(tr, a[t], f"step replay diverged at tick {t}")

    def test_wallclock_plant_diverges(self):
        """A wall-clock dependency is a non-determinism source: a zero clock is inert (equals the pure run),
        a nonzero clock perturbs the cadence and changes the output — the determinism law would catch it."""
        ticks, cl = TH._paths_scene()
        L = A.lens(0, 0)
        pure = TH.run(ticks, cl, L)["transcripts"]
        self.assertEqual(pure, TH.run(ticks, cl, L, _clock=lambda: 0)["transcripts"], "zero clock not inert")
        self.assertNotEqual(pure, TH.run(ticks, cl, L, _clock=lambda: 1)["transcripts"],
                            "a nonzero clock must perturb the throttle")


class TheShapeAndHidden(unittest.TestCase):
    def test_constant_shape_every_tick(self):
        ticks, cl = TH._paths_scene()
        for tr in TH.run(ticks, cl, A.lens(0, 0))["transcripts"]:
            self.assertEqual(len(tr), TH.transcript_bytes_len())

    def test_hidden_change_is_byte_identical(self):
        """A change to a sub-boundary (behind) entity leaves every tick's transcript byte-identical — the
        refresh cadence carries nothing about the hidden set."""
        cl = _cl()
        L = A.lens(0, 0)
        base = TH._seq_from_paths({1: [(4, 0)] * 5, 2: [(-6, 0)] * 5}, 5)   # id2 behind → hidden
        moved = TH._seq_from_paths({1: [(4, 0)] * 5, 2: [(-6, 2)] * 5}, 5)  # move the hidden entity
        self.assertEqual(TH.run(base, cl, L)["transcripts"], TH.run(moved, cl, L)["transcripts"])


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = TH.sweep_digest()
        self.assertEqual(d1, TH.sweep_digest(), "deterministic")
        self.assertEqual(d1, TH.sweep_golden(), "sweep drifted from golden")
        rep = TH.sweep()
        self.assertGreater(rep["carries"], 0, "nothing was ever carried")
        self.assertGreater(rep["departures"], 0, "no entity ever departed")
        self.assertGreater(rep["stale_seen"], 0, "staleness was never exercised")

    def test_sweep_bites_leaked_hidden(self):
        """L15 — a manifest that leaks the hidden set breaks closed-world per tick, so the seeded sweep
        RAISES; clean again after the revert."""
        orig = A._manifest_under
        A._manifest_under = lambda entities, walls, cl, L: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(TH.ThrottleError):
                TH.sweep()
        finally:
            A._manifest_under = orig
        self.assertEqual(TH.sweep_digest(), TH.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
