# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/bombtest.py — INTERACTION-FREE TAMPER DETECTION (URDRBMB1).

  INTERACTION-FREE IS A CALL COUNT — the audit invokes the rule 0 times, the court 6. That is the
    entire operational content of the Elitzur-Vaidman analogy; the rest is structure, not physics.
  THE DARK PORT IS A NEVER CLAIM — 4096 states, 13824 legal transitions, 0 acceptances, and a
    planted non-conserved arm accepts 4608 times so the check is a live falsifier.
  THE BLIND SPOT IS A KERNEL — 3^k * 9^(3-k) invisible deltas, closed form against enumeration.
  SILENCE IS NOT INNOCENCE — an adaptive tamperer is caught 0 of 70 times. Measured, not caveated.
  THREE TIERS, DISJOINT MISSES — (screen, court, chain) = (False, True, True) on a kernel tamper.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import bombtest as BT                                              # noqa: E402


class TheAuditTouchesNothing(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in BT.SCENES:
            self.assertEqual(BT.scene_result(n), BT.golden(n), n)
            self.assertEqual(BT.scene_result(n), BT.scene_result(n), n)

    def test_interaction_free_is_an_instrumented_zero(self):
        """THE WHOLE CLAIM. Not a metaphor — a counter."""
        audit_calls, court_calls = BT.audit_invokes_nothing()
        self.assertEqual(audit_calls, 0, "the audit must never execute a rule")
        self.assertGreater(court_calls, 0, "and the court must, or there is nothing being saved")
        self.assertEqual((audit_calls, court_calls), (0, 6))

    def test_the_counter_actually_counts(self):
        """Validity-not-outcome: a zero from a counter that never increments is worthless."""
        BT.reset_invocations()
        self.assertEqual(BT.invocations(), 0)
        BT.apply_rule(BT.START, 0)
        self.assertEqual(BT.invocations(), 1, "the instrument must move when a rule runs")
        BT.reset_invocations()

    def test_the_screen_still_localizes_a_step(self):
        path = BT.trails()[0]
        bad = list(path)
        bad[1] = (bad[1][0] + 1,) + bad[1][1:]
        self.assertEqual(BT.audit(tuple(bad)), 0)


class TheDarkPortIsANeverClaim(unittest.TestCase):
    def test_no_legal_transition_breaks_a_conserved_arm(self):
        checked, accepted, states = BT.never_claim_census()
        self.assertEqual(accepted, 0, "a false positive would condemn honest work")
        self.assertEqual((checked, states), (13824, 4096))
        self.assertTrue(BT.never_claim_is_discharged())

    def test_a_planted_non_conserved_arm_accepts(self):
        """L15 — without this the exhaustive check is decoration."""
        bad, honest = BT.planted_functional_breaks_the_never_claim()
        self.assertGreater(bad, 0, "the never-claim must be able to accept")
        self.assertEqual(honest, 0)
        self.assertEqual(bad, 4608)

    def test_the_transition_count_is_read_not_computed(self):
        """The header first claimed 24576 = 4096 x 6, counting boundary-blocked moves that never
        fire. The measured count of LEGAL transitions is strictly smaller."""
        checked, _a, states = BT.never_claim_census()
        self.assertLess(checked, states * len(BT.RULES))
        self.assertEqual(checked, 13824)


class TheBlindSpotIsAKernel(unittest.TestCase):
    def test_the_detection_ladder(self):
        self.assertEqual(BT.detection_ladder(), ((1, 486, 728), (2, 648, 728), (3, 702, 728)))

    def test_the_closed_form_matches_enumeration(self):
        self.assertTrue(BT.ladder_matches_the_closed_form())
        self.assertEqual([BT.kernel_size_closed_form(k) for k in range(BT.PAIRS + 1)],
                         [729, 243, 81, 27])

    def test_more_arms_detect_strictly_more(self):
        """The Zeno move: efficiency rises with arms, and never falls."""
        rates = [d for _k, d, _t in BT.detection_ladder()]
        self.assertEqual(rates, sorted(rates))
        self.assertLess(rates[0], rates[-1])

    def test_the_blind_spot_is_never_empty(self):
        """L19 inverted — if the kernel were empty the one-sidedness would be untestable."""
        for k in range(1, BT.PAIRS + 1):
            det, total = BT.detection_census(k)
            self.assertLess(det, total, "there must always be a dud class")

    def test_detection_is_trail_independent(self):
        agree, exc = BT.detection_is_trail_independent()
        self.assertEqual(exc, 0, "linearity makes detection a property of the delta alone")
        self.assertEqual(agree, 65400)

    def test_out_of_range_k_refuses(self):
        for bad in (-1, BT.PAIRS + 1):
            with self.assertRaises(BT.BombTestError):
                BT.kernel_size_closed_form(bad)


class SilenceIsNotInnocence(unittest.TestCase):
    def test_an_adaptive_tamperer_is_never_caught(self):
        """THE CEILING, measured rather than caveated."""
        caught, attempted = BT.adaptive_tamperer_is_never_caught()
        self.assertEqual(caught, 0, "reading the invariants is enough to evade the screen")
        self.assertEqual(attempted, 70)
        self.assertGreater(attempted, 0)

    def test_the_silence_plant_bites(self):
        """L15 — THE Elitzur-Vaidman error: reading a quiet dark port as proof of a dud."""
        self.assertTrue(BT.silence_plant_bites())

    def test_the_chain_only_plant_goes_quiet(self):
        """A tamperer who recomputes the root defeats the chain entirely — and that is exactly the
        party a forensics court audits, since they publish the root."""
        chain_caught, screen_caught = BT.chain_only_plant_bites()
        self.assertFalse(chain_caught, "the recomputed root matches its own tampered trail")
        self.assertTrue(screen_caught, "while the screen still fires")

    def test_the_three_tiers_miss_disjointly(self):
        screen, court, chain = BT.the_court_catches_what_the_screen_misses()
        self.assertFalse(screen, "the screen is blind to the kernel")
        self.assertTrue(court, "the court is not")
        self.assertTrue(chain, "nor is the chain")


class TheCensusIsHonestAboutItsBounds(unittest.TestCase):
    def test_the_trail_cap_is_reported(self):
        """No silent truncation — the failure this repo has hit most often."""
        kept, full, capped = BT.trail_cap_is_reported()
        self.assertEqual((kept, full, capped), (24, 858, True))
        self.assertLess(kept, full, "and the shortfall is stated rather than hidden")


class TheRefusalIsTyped(unittest.TestCase):
    def test_a_detectable_tamper_raises(self):
        self.assertTrue(BT.refuses_a_detectable_tamper())

    def test_an_honest_trail_is_admitted(self):
        self.assertTrue(BT.admits_an_honest_trail())

    def test_the_two_refusal_classes_are_distinct(self):
        """A tamper is an integrity alarm; a malformed request is a usage error."""
        self.assertNotEqual(BT.TamperDetected("x").code, BT.BombTestError("x").code)


if __name__ == "__main__":
    unittest.main()
