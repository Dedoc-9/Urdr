# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/latencyest.py — THE LATENCY-ESTIMATOR (URDRLES1): measure the attested clock
(lat, jitter) URDRCLK1 consumes from the ack/RTT stream, and defend it against a slow-drip latency forge.
Composition over `clockauth` (over `lagcomp`, `hitbox`, `perception`), NO new glyph.

  MIN-FLOOR — the one-way latency is min(RTT)//2; delaying some acks (mean rises) does NOT move it, while the
    mean-based plant inflates it.
  RATE-LIMITED RISE / FREE FALL — the estimate rises at most MAX_RISE per update (the no-ratelimit plant
    jumps) but falls immediately when the ping improves.
  JITTER CAP — the jitter is the bounded spread, capped at MAX_JITTER.
  PLAUSIBILITY — an implausible RTT is refused, never folded in (the no-plausibility plant tolerates it).
  END-TO-END — the honest estimator feeding URDRCLK1 REFUSES a backdate a defective (mean) estimator's
    widened band would admit.
  PROOF-CARRYING — the published record is bound to the ack window; a forged higher latency fails.
  THE SWEEP BITES — a mean-based estimator moves the latency off the floor, so the seeded sweep RAISES.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import latencyest as LE                                           # noqa: E402
import clockauth as CK                                            # noqa: E402


def _win(rtts, base=0):
    return [LE.sample(base + i, base + i + r) for i, r in enumerate(rtts)]


class TheEstimator(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in LE.SCENES:
            self.assertEqual(LE.scene_result(name), LE.golden(name), name)
            self.assertEqual(LE.scene_result(name), LE.scene_result(name), name)

    def test_honest_convergence(self):
        self.assertEqual(LE.estimate(3, _win([6, 6, 6, 6])), (3, 0))

    def test_deterministic(self):
        w = _win([6, 8, 6, 10])
        self.assertEqual(LE.estimate(3, w), LE.estimate(3, w))


class TheMinFloor(unittest.TestCase):
    def test_inflation_does_not_move_latency(self):
        """Delaying half the acks (RTT 12) leaves the minimum at 6, so the latency stays at its honest floor
        (3) — the mean-based plant, by contrast, inflates it."""
        w = _win([6, 12, 6, 12])
        self.assertEqual(LE.estimate(3, w)[0], 3, "the min floor must hold against a partial inflation")
        self.assertGreater(LE._estimate_by_mean(3, w)[0], 3, "the mean plant must inflate the latency")

    def test_end_to_end_min_floor_refuses_backdate(self):
        """The payoff: the honest estimator's clock keeps the URDRCLK1 band tight and refuses a backdate, while
        the mean-inflated clock widens the band and admits it."""
        tl = CK._static_timeline(100, 7)
        sh = CK.HB.shooter(0, 0, 1, 0, 400)
        w = _win([6, 12, 6, 12])
        honest = LE.estimate(3, w)
        mean = LE._estimate_by_mean(3, w)
        backdate = (1, 7, 0, 100 - honest[0] - LE.MAX_JITTER - 1)
        self.assertFalse(CK.admit(tl, frozenset(), sh, honest, backdate),
                         "the honest estimator must keep the band tight enough to refuse the backdate")
        self.assertTrue(CK.admit(tl, frozenset(), sh, mean, backdate),
                        "the mean-inflated clock must admit the backdate — else the teeth are toothless")


class TheRateLimitAndFall(unittest.TestCase):
    def test_drip_rises_at_most_max_rise(self):
        w = _win([10, 10, 10, 12])                               # raw latency 5
        self.assertLessEqual(LE.estimate(2, w)[0], 2 + LE.MAX_RISE, "the rise must be rate-limited")
        self.assertGreater(LE._estimate_no_ratelimit(2, w)[0], LE.estimate(2, w)[0],
                           "the no-ratelimit plant must jump past the rate-limited estimate")

    def test_improved_ping_falls_freely(self):
        self.assertEqual(LE.estimate(5, _win([4, 4]))[0], 2, "a better ping must tighten the band immediately")

    def test_jitter_capped(self):
        w = _win([6, 6 + 4 * LE.MAX_JITTER, 6])                  # a wide spread
        self.assertLessEqual(LE.estimate(3, w)[1], LE.MAX_JITTER, "jitter must be capped")


class ThePlausibility(unittest.TestCase):
    def test_implausible_rtt_refused(self):
        with self.assertRaises(LE.LatencyestError):
            LE.estimate(3, _win([6, LE.MAX_RTT + 5, 6]))

    def test_no_plausibility_plant_tolerates_it(self):
        # the plant folds the garbage sample in instead of refusing (it returns without raising)
        self.assertIsNotNone(LE._estimate_no_plausibility(3, _win([6, LE.MAX_RTT + 5, 6])))

    def test_negative_rtt_refused(self):
        with self.assertRaises(LE.LatencyestError):
            LE.estimate(3, [LE.sample(10, 4)])                   # echo before the ping


class TheProofCarryingRecord(unittest.TestCase):
    def test_constant_shape_and_verifies(self):
        rec = LE.publish(3, _win([6, 6, 6, 6]))
        self.assertEqual(len(rec), LE.record_bytes_len())
        self.assertTrue(LE.verify_record(3, _win([6, 6, 6, 6]), rec))
        self.assertEqual(LE.clock_of(rec), (3, 0))

    def test_forged_higher_latency_fails(self):
        rec = LE.publish(3, _win([6, 6, 6, 6]))
        forged = LE.forge_clock(rec, 7)
        self.assertEqual(LE.read_record(forged)[1], 7, "the forgery should read as a higher latency")
        self.assertFalse(LE.verify_record(3, _win([6, 6, 6, 6]), forged),
                         "a forged higher latency verified — the proof-carrying contract broke")

    def test_record_bound_to_its_ack_window(self):
        rec = LE.publish(3, _win([6, 6, 6, 6]))
        self.assertFalse(LE.verify_record(3, _win([6, 6, 6, 8]), rec),
                         "a record must not verify against a different ack window")

    def test_publish_refuses_implausible_window(self):
        with self.assertRaises(LE.LatencyestError):
            LE.publish(3, _win([6, LE.MAX_RTT + 5]))


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = LE.sweep_digest()
        self.assertEqual(d1, LE.sweep_digest(), "deterministic")
        self.assertEqual(d1, LE.sweep_golden(), "sweep drifted from golden")
        rep = LE.sweep()
        for k in ("floor_seen", "drip_seen", "implausible_seen", "compose_seen"):
            self.assertGreater(rep[k], 0, f"{k} never exercised")

    def test_sweep_bites_mean_estimator(self):
        """L15 — a mean-based estimator moves the latency off the min floor, so the seeded sweep RAISES; clean
        again after the revert."""
        orig = LE.estimate
        LE.estimate = LE._estimate_by_mean
        try:
            with self.assertRaises(LE.LatencyestError):
                LE.sweep()
        finally:
            LE.estimate = orig
        self.assertEqual(LE.sweep_digest(), LE.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
