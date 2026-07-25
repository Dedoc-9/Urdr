# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/pingpolicy.py — THE PING POLICY (URDRPNG1): the scheduling / sample-selection
layer feeding URDRLES1's ack window, organised around ONE invariant. Composition over `latencyest` (over
`clockauth`, `lagcomp`, `hitbox`, `perception`), NO new glyph.

  CONDITIONAL MONOTONE DISADVANTAGE (the headline theorem) — GIVEN a session floor founded on an unpadded
    window, for every client strategy reach <= honest reach (+ DRIFT_ALLOWANCE for a total delay). Every
    lever such a client can pull resolves against them.
  THE COLD-START RESIDUAL — the precondition failing: a client padding from connect founds an inflated floor
    and keeps a WIDER band. Measured, bounded by the plausibility ceiling, and asserted so it stays visible.
  AUTHENTICATED ECHO — a forged or replayed echo earns no coverage; the no-auth plant hands it over.
  COVERAGE OR REFUSAL — too few authenticated echoes freezes the band and then refuses; silence never widens.
  THE LOWER-HALF RULE — partial delay cannot move the jitter; the full-spread plant lets it.
  THE SESSION FLOOR — total delay is pinned to a constant by the client's own honest early samples; the
    no-floor plant escapes it.
  SCRUTINY — the rate rises freely, falls one step per stable window, floored; the free-fall plant thins it.
  PROOF-CARRYING — the record is bound to its window; a forged widened band fails.
  THE SWEEP BITES — a no-floor policy falsifies the theorem, so the seeded sweep RAISES.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import pingpolicy as PP                                           # noqa: E402

S = PP.SECRET


class ThePolicy(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in PP.SCENES:
            self.assertEqual(PP.scene_result(name), PP.golden(name), name)
            self.assertEqual(PP.scene_result(name), PP.scene_result(name), name)

    def test_schedule_is_covering_and_keyed(self):
        ticks = [t for t, _n in PP.schedule(S, 0, PP.MAX_RATE)]
        self.assertEqual(len(ticks), PP.MAX_RATE)
        self.assertEqual(len(set(ticks)), PP.MAX_RATE, "pings must not collide")
        self.assertEqual(sorted(ticks), ticks, "pings must be ordered across the window")
        # a different secret moves the phase (the placement is keyed, not a fixed cadence)
        other = bytes((S[0] ^ 0xFF,)) + S[1:]
        self.assertNotEqual([PP.nonce(S, t) for t in ticks], [PP.nonce(other, t) for t in ticks])

    def test_step_deterministic(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        e = PP.play(S, 0, PP.MAX_RATE, 6, "honest")
        self.assertEqual(PP.step(S, st, 0, e), PP.step(S, st, 0, e))


class TheMonotoneDisadvantageTheorem(unittest.TestCase):
    def test_theorem_holds_over_the_strategy_space(self):
        holds, h, reaches = PP.monotone_disadvantage(S, 6, 5)
        self.assertTrue(holds, f"monotone disadvantage falsified: honest {h}, {reaches}")
        for strat in PP.NON_TOTAL_DELAY:
            self.assertLessEqual(reaches[strat], h, f"{strat} out-reached honest play")
        self.assertLessEqual(reaches["delay_all"], h + PP.DRIFT_ALLOWANCE,
                             "a total delay escaped the declared drift allowance")

    def test_theorem_is_non_vacuous(self):
        """The honest reach must be positive and the refused strategies must actually be refused — otherwise
        the theorem would hold trivially."""
        _holds, h, reaches = PP.monotone_disadvantage(S, 6, 5)
        self.assertGreater(h, 0, "the honest client must earn a real band")
        for strat in ("drop_all", "replay", "forge"):
            self.assertEqual(reaches[strat], -1, f"{strat} should end in refusal")

    def test_no_floor_plant_falsifies_the_theorem(self):
        holds, _h, _r = PP.monotone_disadvantage(S, 6, 6, _step=PP._step_no_floor)
        self.assertFalse(holds, "the no-floor plant must break monotone disadvantage")


class TheColdStartResidual(unittest.TestCase):
    """The theorem's PRECONDITION failing — the rung's declared, measured residual. These tests assert the
    bound that DOES hold and keep the gap VISIBLE, so it can never be quietly relabelled as covered."""

    def test_cold_start_out_reaches_honest_the_gap_is_real(self):
        """A client padding every ack from connect never founds an honest floor and keeps a WIDER band than
        honest play. If this ever stops holding, the declared boundary has gone vacuous (or the rung genuinely
        improved) — either way the claim must be re-graded, so this test failing is a signal, not a nuisance."""
        h = PP.strategy_reach(S, 6, "honest", 5)
        cold = PP.cold_start_reach(S, 6, 6, 5)
        self.assertGreater(cold, h + PP.DRIFT_ALLOWANCE,
                           "the cold-start residual is no longer witnessed — re-grade the claim")

    def test_cold_start_is_bounded_by_the_plausibility_ceiling(self):
        for base in (4, 6, 8):
            for pad in (0, 2, 4, 6):
                self.assertLessEqual(PP.cold_start_reach(S, base, pad, 6), PP.cold_start_ceiling(),
                                     f"cold start base={base} pad={pad} passed the ceiling")

    def test_padding_beyond_plausibility_is_refused_outright(self):
        self.assertEqual(PP.cold_start_reach(S, 6, PP.MAX_RTT + 4, 5), -1,
                         "an implausibly padded cold start must be refused, not folded in")

    def test_ceiling_is_the_documented_expression(self):
        self.assertEqual(PP.cold_start_ceiling(), PP.MAX_RTT // 2 + PP.DRIFT_ALLOWANCE + PP.MAX_JITTER)

    def test_theorem_does_not_claim_to_cover_cold_start(self):
        """The conditional theorem is evaluated from an honestly-seeded floor; that precondition is what the
        cold start violates. Asserting both here keeps the two statements from being conflated."""
        holds, h, _r = PP.monotone_disadvantage(S, 6, 5)
        self.assertTrue(holds, "the conditional theorem must hold on its own precondition")
        self.assertGreater(PP.cold_start_reach(S, 6, 6, 5), h + PP.DRIFT_ALLOWANCE,
                           "and must NOT be read as covering a client that pads from connect")


class TheAuthenticatedEcho(unittest.TestCase):
    def test_replay_and_forgery_earn_no_coverage(self):
        for bad in ("replay", "forge"):
            e = PP.play(S, 0, PP.MAX_RATE, 6, bad)
            self.assertLess(len(PP.authenticate(S, 0, PP.MAX_RATE, e)), PP.MIN_SAMPLES, bad)
            self.assertGreaterEqual(len(PP._authenticate_none(S, 0, PP.MAX_RATE, e)), PP.MIN_SAMPLES,
                                    f"the no-auth plant must hand {bad} coverage")

    def test_honest_echoes_authenticate(self):
        e = PP.play(S, 0, PP.MAX_RATE, 6, "honest")
        self.assertEqual(len(PP.authenticate(S, 0, PP.MAX_RATE, e)), PP.MAX_RATE)

    def test_implausible_rtt_not_authenticated(self):
        t, n = PP.schedule(S, 0, PP.MAX_RATE)[0]
        self.assertEqual(PP.authenticate(S, 0, PP.MAX_RATE, [PP.echo(t, n, t + PP.MAX_RTT + 5)]), [])
        self.assertEqual(PP.authenticate(S, 0, PP.MAX_RATE, [PP.echo(t, n, t - 1)]), [])


class TheCoverageLaw(unittest.TestCase):
    def test_silence_freezes_then_refuses(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        _fs, clk, reason = PP.run(S, st, 6, "drop_all", PP.STARVE_WINDOWS)
        self.assertEqual(reason, PP.R_COVERAGE, "sustained silence must end in refusal")
        self.assertEqual(clk[1], 0, "a starved band must have its jitter collapsed")
        self.assertLessEqual(clk[0], st[1], "a starved band must never have widened")

    def test_partial_coverage_before_refusal_does_not_widen(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        ns, clk, reason = PP.step(S, st, 0, PP.play(S, 0, PP.MAX_RATE, 6, "drop_all"))
        self.assertEqual(reason, PP.R_OK, "one quiet window is a freeze, not yet a refusal")
        self.assertEqual(PP.reach(clk), st[1], "a deficit window must not widen the reach")
        self.assertEqual(ns[3], 1, "the starve counter must advance")


class TheLowerHalfRule(unittest.TestCase):
    def test_partial_delay_cannot_move_the_jitter(self):
        e = PP.play(S, 0, PP.MAX_RATE, 6, "delay_half")
        rtts = [b - a for (a, b) in PP.authenticate(S, 0, PP.MAX_RATE, e)]
        self.assertEqual(PP.lower_half_jitter(rtts), 0, "the fast half must be untouched by a partial delay")
        self.assertGreater(PP._full_spread_jitter(rtts), PP.lower_half_jitter(rtts),
                           "the full-spread plant must inflate where the lower-half rule does not")

    def test_genuine_lower_half_spread_is_read(self):
        # a path with real variability in its FAST samples is read honestly (the rule is not always zero)
        self.assertGreater(PP.lower_half_jitter([4, 8, 8, 10]), 0)


class TheSessionFloor(unittest.TestCase):
    def test_honest_start_pins_a_later_total_delay(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        st, _c, _r = PP.run(S, st, 6, "honest", 1)                # one honest window records the floor
        floor = st[2]
        st, clk, _r = PP.run(S, st, 6, "delay_all", 6)            # then delay everything, at length
        self.assertEqual(st[2], floor, "the session floor must never rise")
        self.assertLessEqual(clk[0], floor // 2 + PP.DRIFT_ALLOWANCE,
                             "a total delay escaped the session floor pin")

    def test_no_floor_plant_drifts_further(self):
        pinned = PP.strategy_reach(S, 6, "delay_all", 6)
        loose = PP.strategy_reach(S, 6, "delay_all", 6, _step=PP._step_no_floor)
        self.assertGreater(loose, pinned, "the no-floor plant must drift past the pinned policy")


class TheScrutiny(unittest.TestCase):
    def test_rate_falls_one_step_and_is_floored(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        e = PP.play(S, 0, PP.MAX_RATE, 6, "honest")
        ns, _c, _r = PP.step(S, st, 0, e)
        self.assertEqual(ns[0], PP.MAX_RATE - 1, "a stable window earns back exactly one step")
        low = PP.state(PP.MIN_RATE, 3, 6)
        ns2, _c2, _r2 = PP.step(S, low, 0, PP.play(S, 0, PP.MIN_RATE, 6, "honest"))
        self.assertEqual(ns2[0], PP.MIN_RATE, "the rate must never fall below its floor")

    def test_instability_raises_the_rate_at_once(self):
        st = PP.state(PP.MIN_RATE, 3, 6)
        ns, _c, _r = PP.step(S, st, 0, PP.play(S, 0, PP.MIN_RATE, 6, "drop_all"))
        self.assertEqual(ns[0], PP.MAX_RATE, "a coverage deficit must jump scrutiny to its maximum")

    def test_free_fall_plant_thins_the_stream(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        e = PP.play(S, 0, PP.MAX_RATE, 6, "honest")
        self.assertLess(PP._step_rate_free_fall(S, st, 0, e)[0][0], PP.step(S, st, 0, e)[0][0])


class TheProofCarryingRecord(unittest.TestCase):
    def test_constant_shape_and_verifies(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        e = PP.play(S, 0, PP.MAX_RATE, 6, "honest")
        rec = PP.publish(S, st, 0, e)
        self.assertEqual(len(rec), PP.record_bytes_len())
        self.assertTrue(PP.verify_record(S, st, 0, e, rec))

    def test_forged_widened_band_fails(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        e = PP.play(S, 0, PP.MAX_RATE, 6, "honest")
        rec = PP.publish(S, st, 0, e)
        forged = PP.forge_widen(rec, 7, PP.MAX_JITTER)
        self.assertEqual(PP.read_record(forged)[1], 7, "the forgery should read as a wider band")
        self.assertFalse(PP.verify_record(S, st, 0, e, forged),
                         "a forged widened band verified — the proof-carrying contract broke")

    def test_record_bound_to_its_window(self):
        st = PP.state(PP.MAX_RATE, 3, 6)
        rec = PP.publish(S, st, 0, PP.play(S, 0, PP.MAX_RATE, 6, "honest"))
        self.assertFalse(PP.verify_record(S, st, 0, PP.play(S, 0, PP.MAX_RATE, 8, "honest"), rec),
                         "a record must not verify against a different ack window")


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = PP.sweep_digest()
        self.assertEqual(d1, PP.sweep_digest(), "deterministic")
        self.assertEqual(d1, PP.sweep_golden(), "sweep drifted from golden")
        rep = PP.sweep()
        for k in ("theorem_seen", "auth_seen", "floor_seen", "half_seen", "rate_seen", "cold_seen"):
            self.assertGreater(rep[k], 0, f"{k} never exercised")

    def test_sweep_bites_no_floor_policy(self):
        """L15 — a policy without the session floor lets a total delay widen the band without bound, so the
        monotone-disadvantage theorem fails and the seeded sweep RAISES; clean again after the revert."""
        orig = PP.step
        PP.step = PP._step_no_floor
        try:
            with self.assertRaises(PP.PingpolicyError):
                PP.sweep()
        finally:
            PP.step = orig
        self.assertEqual(PP.sweep_digest(), PP.sweep_golden(), "clean after revert")

    def test_sweep_bites_full_spread_jitter(self):
        """L15 — reading the jitter from the full spread lets a partial delay inflate the reach, falsifying
        the theorem; clean again after the revert."""
        orig = PP.lower_half_jitter
        PP.lower_half_jitter = PP._full_spread_jitter
        try:
            with self.assertRaises(PP.PingpolicyError):
                PP.sweep()
        finally:
            PP.lower_half_jitter = orig
        self.assertEqual(PP.sweep_digest(), PP.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
