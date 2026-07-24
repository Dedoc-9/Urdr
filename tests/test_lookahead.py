# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/lookahead.py — the BOUNDED LOOK-AHEAD OPTIMALITY CERTIFICATE (URDRLKA1):
proving whether a multi-tick optimizer can beat the greedy adaptive encoder, and honestly finding it cannot
on this model. A deterministic bounded Viterbi DP over a W-tick window minimises the true total cost.
Composition over `adaptcite`, NO new glyph.

  GREEDY-OPTIMALITY — on the real model (cross-tick independent, transition = 0) the DP total equals the
    greedy total: greedy is globally optimal and no look-ahead helps (measured, non-vacuously).
  OPTIMIZER-HAS-TEETH — on a synthetic coupled model the DP beats greedy's actual cost; the DP is a real
    optimizer, so the greedy-optimality result is not vacuous.
  CERTIFICATE-DETECTS-COUPLING — under coupling the DP total differs from greedy, so the real-model equality
    is a genuine measurement, not a tautology.
  REPRESENTATION-INDEPENDENCE — the look-ahead encoding equals the adaptive encoding, which reconstructs the
    same states as the all-baseline encoding.
  BOUNDED-WINDOW — the search examines at most W ticks; an over-window search is rejected.
  DETERMINISTIC — the DP is a pure function with a lexicographic tiebreak.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import lookahead as LK                                          # noqa: E402
import adaptcite as AC                                          # noqa: E402
import anamorphosis as A                                        # noqa: E402


_OPTS = [[(7, "move"), (9, "cite"), (39, "full")],
         [(7, "move"), (9, "cite"), (39, "full")]]


class TheGreedyOptimality(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in LK.SCENES:
            self.assertEqual(LK.scene_result(name), LK.golden(name), name)
            self.assertEqual(LK.scene_result(name), LK.scene_result(name), name)

    def test_greedy_optimal_on_real(self):
        ticks, cl = LK._oscillate()
        ok, seen = LK.certify_greedy_optimal(ticks, cl, A.lens(0, 0))
        self.assertTrue(ok, "the bounded DP beat greedy on the real model")
        self.assertGreater(seen, 0, "no genuine multi-option window was certified (vacuous)")

    def test_dp_equals_greedy_on_real(self):
        self.assertEqual(LK.window_dp(_OPTS, LK.real_trans)[0], LK.greedy_cost(_OPTS))
        self.assertEqual(LK.window_dp(_OPTS, LK.real_trans)[1], ["move", "move"])


class TheTeeth(unittest.TestCase):
    def test_optimizer_has_teeth(self):
        """On the coupled model the DP finds a strictly cheaper assignment than greedy's actual cost — the
        DP is a genuine optimizer, so the real-model equality is meaningful (L15)."""
        self.assertTrue(LK.optimizer_has_teeth())
        self.assertLess(LK.window_dp(_OPTS, LK.coupled_trans)[0],
                        LK.greedy_actual_cost(_OPTS, LK.coupled_trans))

    def test_certificate_detects_coupling(self):
        """Under coupling the DP total differs from the greedy base total — the greedy-optimality equality
        is a real measurement (it CAN fail), not a tautology."""
        self.assertNotEqual(LK.window_dp(_OPTS, LK.coupled_trans)[0], LK.greedy_cost(_OPTS))

    def test_greedy_actual_pays_the_coupling(self):
        # greedy picks move,move (base 14) but pays the 100 penalty → actual 114; the DP avoids it
        self.assertEqual(LK.greedy_actual_cost(_OPTS, LK.coupled_trans), 114)
        self.assertEqual(LK.window_dp(_OPTS, LK.coupled_trans)[0], 16)


class TheRepresentationIndependence(unittest.TestCase):
    def test_representation_independent(self):
        ticks, cl = LK._oscillate()
        self.assertTrue(LK.representation_independent(ticks, cl, A.lens(0, 0)))

    def test_lookahead_wire_is_the_adaptive_wire(self):
        """The certificate made concrete: on the real model the per-window DP optimum equals the per-tick
        greedy optimum, so the look-ahead wire IS the adaptive wire."""
        ticks, cl = LK._oscillate()
        self.assertEqual(LK.lookahead_wire(ticks, cl, A.lens(0, 0)),
                         AC.run(ticks, cl, A.lens(0, 0), mode="adaptive")["packets"])

    def test_drift_would_break_independence(self):
        """If the encoding diverged from adaptive (as adaptcite's drift plant does), the reconstruction
        would differ from the baseline — the independence the certificate relies on has teeth."""
        ticks, cl = LK._oscillate()
        base = AC.run(ticks, cl, A.lens(0, 0), mode="baseline")["recon"]
        self.assertNotEqual(AC.run(ticks, cl, A.lens(0, 0), mode="drift")["recon"], base)


class TheBoundedWindow(unittest.TestCase):
    def test_over_window_rejected(self):
        over = [[(7, "move")]] * (LK.WINDOW + 1)
        with self.assertRaises(LK.LookaheadError):
            LK.window_dp(over, LK.real_trans)

    def test_exactly_window_accepted(self):
        exact = [[(7, "move")]] * LK.WINDOW
        self.assertEqual(LK.window_dp(exact, LK.real_trans)[0], 7 * LK.WINDOW)


class TheDeterminism(unittest.TestCase):
    def test_dp_is_pure(self):
        self.assertEqual(LK.window_dp(_OPTS, LK.coupled_trans), LK.window_dp(_OPTS, LK.coupled_trans))

    def test_tiebreak_is_lexicographic(self):
        # two equal-cost single-tick options → the deterministic DP picks the lexicographically smaller label
        opts = [[(5, "b"), (5, "a")]]
        self.assertEqual(LK.window_dp(opts, LK.real_trans)[1], ["a"])


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = LK.sweep_digest()
        self.assertEqual(d1, LK.sweep_digest(), "deterministic")
        self.assertEqual(d1, LK.sweep_golden(), "sweep drifted from golden")
        self.assertGreater(LK.sweep()["choices_total"], 0, "no genuine-choice window was ever certified")

    def test_sweep_bites_leaked_hidden(self):
        orig = A._manifest_under
        A._manifest_under = lambda entities, walls, cl, L: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(LK.LookaheadError):
                LK.sweep()
        finally:
            A._manifest_under = orig
        self.assertEqual(LK.sweep_digest(), LK.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
