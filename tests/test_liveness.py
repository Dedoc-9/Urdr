# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/liveness.py — THE KEYED HEARTBEAT (URDRLIV1).

  THE COUNTERFEIT RESET IS CLOSED — an unkeyed heartbeat is forged 12 of 12 by anyone holding only
    public data; the keyed one 0 of 12. Proof of POSSESSION, not a hash anyone can recompute.
  REPLAY IS BOUNDED TO EXACTLY ONE TICK — not eliminated. The adversary gains no tick he did not
    already have, which is the honest form of the claim.
  THE DESCENT IS WELL-FOUNDED — pure subtraction, no clamp, the fault firing exactly before zero.
    The max(0, ...) plant runs 500 ticks of silence without ever firing.
  THE MASKING LADDER IS STRICT — one stolen token hides 4 / 8 / 40 ticks of a 40-tick stall against
    the honest step, a bounded window, and a verifier that accepts any historical token.
  THE FAULT IS NOT SWALLOWED — asserted by a test against a live swallowing plant, NOT by a
    BaseException base class, which was measured to abort the gate rather than redden a row.

Every test can go red (L5); the four plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import liveness as LV                                              # noqa: E402


class TheHeartbeatIsKeyed(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in LV.SCENES:
            self.assertEqual(LV.scene_result(n), LV.golden(n), n)
            self.assertEqual(LV.scene_result(n), LV.scene_result(n), n)

    def test_the_counterfeit_reset_is_closed(self):
        unkeyed, keyed, attempts = LV.forgery_census()
        self.assertEqual(unkeyed, attempts, "an unkeyed heartbeat is forgeable by every observer")
        self.assertEqual(keyed, 0, "and the keyed one by nobody without the secret")
        self.assertEqual(attempts, 12, "the denominator, so neither number reads as an empty search")
        self.assertTrue(LV.keyed_auth_closes_the_counterfeit_reset())

    def test_replay_is_bounded_to_one_tick_not_eliminated(self):
        window, span = LV.replay_window()
        self.assertEqual(window, 1, "a token verifies at its own tick and nowhere else")
        self.assertEqual(span, 12)
        self.assertGreater(window, 0, "it IS valid somewhere — that is not elimination")

    def test_a_wrong_secret_never_verifies(self):
        good = LV.token(LV.SECRET, LV.SESSION, 5)
        self.assertTrue(LV.verify_token(LV.SECRET, LV.SESSION, 5, good))
        self.assertFalse(LV.verify_token(b"wrong-secret", LV.SESSION, 5, good))
        self.assertFalse(LV.verify_token(LV.SECRET, b"other-session", 5, good))
        self.assertFalse(LV.verify_token(LV.SECRET, LV.SESSION, 6, good))

    def test_non_bytes_and_garbage_never_verify(self):
        for junk in (None, "", 0, b"", b"\x00" * LV.TOKEN_BYTES, object()):
            self.assertFalse(LV.verify_token(LV.SECRET, LV.SESSION, 1, junk), repr(junk))

    def test_the_tick_is_clockauth_attested(self):
        (lo, hi), inside, outside = LV.bound_to_clockauth_band()
        self.assertLessEqual(lo, hi)
        self.assertEqual(inside, hi - lo + 1, "every tick in the admissible band authenticates")
        self.assertGreater(outside, 0, "and a token from one tick does not serve another")

    def test_a_negative_or_non_int_tick_refuses(self):
        for bad in (-1, "3", 1.0):
            with self.assertRaises(LV.LivenessError):
                LV.token(LV.SECRET, LV.SESSION, bad)


class TheDescentIsWellFounded(unittest.TestCase):
    def test_exactly_patience_minus_one_ticks_survive(self):
        survived, raised, patience = LV.well_founded_descent()
        self.assertTrue(raised, "total silence must terminate in a fault")
        self.assertEqual(survived, patience - 1,
                         "PATIENCE-1 ticks survive and the PATIENCE-th raises")
        self.assertEqual((survived, patience), (3, 4))

    def test_the_budget_never_leaves_the_naturals(self):
        """No clamp, and no negative or zero return — the fault fires strictly before either."""
        min_seen, all_positive = LV.budget_never_leaves_the_naturals()
        self.assertTrue(all_positive)
        self.assertEqual(min_seen, 1, "the last surviving value is 1, and the next raises")

    def test_a_valid_heartbeat_keeps_the_session_alive(self):
        """Validity-not-outcome: a watchdog that always fires is useless."""
        survived, raised = LV.heartbeat_resets_the_budget()
        self.assertFalse(raised, "an alive server must never be declared offline")
        self.assertEqual(survived, LV.PATIENCE * 3)

    def test_an_invalid_budget_refuses(self):
        for bad in (0, -3, "4", None):
            with self.assertRaises(LV.LivenessError):
                LV.step(bad, None)

    def test_the_clamp_plant_never_fires(self):
        """L15 — the 'defensive' max(0, ...) that reopens the residual in one line."""
        clamped_never_fired, honest_survived = LV.clamp_plant_never_fires()
        self.assertTrue(clamped_never_fired, "500 ticks of silence and it never raises")
        self.assertEqual(honest_survived, LV.PATIENCE - 1, "while the honest step raises at 4")


class TheMaskingLadder(unittest.TestCase):
    def test_each_relaxation_buys_the_adversary_strictly_more(self):
        honest, window, history, ticks = LV.sliding_window_plant_masks_a_stall()
        self.assertEqual((honest, window, history, ticks), (4, 8, 40, 40))
        self.assertLess(honest, window, "a bounded window doubles the exposure")
        self.assertLess(window, history, "and accepting any history hides the stall entirely")
        self.assertEqual(history, ticks, "forever, for the whole run")
        self.assertTrue(LV.masking_ladder_is_strict())

    def test_the_correct_module_raises_where_the_plants_do_not(self):
        """The red-first assertion the spec asked for, stated directly."""
        stolen = LV.token(LV.SECRET, LV.SESSION, 0)
        with self.assertRaises(LV.ServerOffline):
            budget = LV.PATIENCE
            for t in range(LV.PATIENCE * 4):
                budget = LV.step(budget, stolen, LV.SECRET, LV.SESSION, t)
        budget = LV.PATIENCE
        for t in range(LV.PATIENCE * 4):
            budget = LV._step_accepts_any_history(budget, stolen, LV.SECRET, LV.SESSION, t)
        self.assertEqual(budget, LV.PATIENCE, "the plant never even decremented")


class TheFaultIsNotSwallowed(unittest.TestCase):
    def test_step_lets_the_fault_out(self):
        self.assertTrue(LV.step_does_not_swallow())
        with self.assertRaises(LV.ServerOffline):
            LV.step(1, None)

    def test_the_swallowing_plant_hides_it(self):
        """L15 — THIS is the failure mode the BaseException proposal was aimed at, and blocking it is
        a test rather than a base class."""
        swallowed, honest_survived = LV.swallowing_plant_hides_the_fault()
        self.assertTrue(swallowed, "the wrapper never surfaces the fault")
        self.assertEqual(honest_survived, LV.PATIENCE - 1)

    def test_baseexception_would_abort_the_gate(self):
        """THE DESIGN DECISION, PINNED AS DATA. verify.py wraps every stage in `except Exception`."""
        exc_recorded, base_recorded = LV.baseexception_would_abort_the_gate()
        self.assertTrue(exc_recorded, "a normal Exception reddens a row and the gate survives")
        self.assertFalse(base_recorded, "a BaseException escapes and aborts the run")

    def test_the_fault_is_an_exception_subclass(self):
        self.assertTrue(issubclass(LV.ServerOffline, Exception))
        self.assertNotEqual(LV.ServerOffline("x").code, LV.LivenessError("x").code)


class TheCorpusIsEmittedNotInscribed(unittest.TestCase):
    def test_the_pinned_file_is_the_modules_own_output(self):
        """No hand-typed hex: `--emit` produces exactly the pinned data lines."""
        self.assertTrue(LV.emitted_matches_pinned())
        self.assertEqual(LV.conformance_lines(), LV.pinned_lines())

    def test_the_corpus_is_frozen_not_regenerated(self):
        """L23 — a golden the gate rewrites at run time cannot detect drift. The module EMITS and a
        human PINS; nothing here writes the file."""
        import inspect
        src = inspect.getsource(LV)
        self.assertNotIn('open(_os.path.join(_HERE, "conformance_liveness.txt"), "w"', src)
        self.assertEqual(src.count('encoding="utf-8"'), src.count("conformance_liveness.txt"))

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(LV.LivenessError):
            LV.golden("no_such_scene")


if __name__ == "__main__":
    unittest.main()
