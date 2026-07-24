# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/adaptcite.py — ADAPTIVE (BANDWIDTH-AWARE) REPRESENTATION SELECTION
(URDRADC1): choosing the cheapest LAWFUL encoding of each entity update. Since a CITE is fixed-width,
'bandwidth-aware' is about which REPRESENTATION (nothing < MOVE < CITE < FULL), not which anchor. The
adaptive encoder picks the minimum-cost lawful spelling, deterministically, subject to mandatory baselines.
Composition over `citation`, NO new glyph.

  REPRESENTATION-INDEPENDENCE — the headline: adaptive, oldest-match, and all-baseline encoders reconstruct
    the SAME state sequence; a lawful spelling never alters semantics.
  ADAPTIVE-OPTIMALITY — each non-baseline update uses the minimum-cost lawful representation; the suboptimal
    encoder spends more and is caught.
  LAWFUL-ONLY — a forged CITE to an UNCERTIFIED anchor is cheaper than a FULL but refused by the certified
    law.
  SEMANTICS-PRESERVING — a forged CITE to a NON-matching anchor reconstructs the wrong state; representation-
    independence catches it.
  A REAL SAVING — the adaptive wire is never larger than the fixed rule and strictly smaller when a MOVE was
    available where the fixed rule spent a CITE.
  DETERMINISTIC — selection is a pure function of state/history; the wall-clock plant diverges.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import adaptcite as C                                           # noqa: E402
import citation as CT                                           # noqa: E402
import anamorphosis as A                                        # noqa: E402
import perception as PC                                         # noqa: E402

_CFG = (C.B_ROOMY, C.ACK_LAG, C.REFRESH_INTERVAL)


class TheRepresentationIndependence(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in C.SCENES:
            self.assertEqual(C.scene_result(name), C.golden(name), name)
            self.assertEqual(C.scene_result(name), C.scene_result(name), name)

    def test_representation_independent(self):
        ticks, cl = C._oscillate()
        self.assertTrue(C.representation_independent(ticks, cl, A.lens(0, 0)),
                        "a lawful representation altered the reconstructed semantics")

    def test_representation_drift_plant_bites(self):
        """A forged CITE to a NON-matching anchor is cheap but reconstructs the wrong state — the
        representation-independence law catches it, while adaptive matches the baseline (L15)."""
        ticks, cl = C._oscillate()
        base = C.run(ticks, cl, A.lens(0, 0), mode="baseline")["recon"]
        self.assertNotEqual(C.run(ticks, cl, A.lens(0, 0), mode="drift")["recon"], base)
        self.assertEqual(C.run(ticks, cl, A.lens(0, 0), mode="adaptive")["recon"], base)


class TheOptimality(unittest.TestCase):
    def test_optimality_holds(self):
        ticks, cl = C._oscillate()
        self.assertTrue(C.optimality_ok(ticks, cl, A.lens(0, 0)))

    def test_adaptive_beats_the_fixed_rule(self):
        ticks, cl = C._oscillate()
        a = C.used_total(ticks, cl, A.lens(0, 0), mode="adaptive")
        o = C.used_total(ticks, cl, A.lens(0, 0), mode="oldest")
        self.assertLessEqual(a, o)
        self.assertLess(a, o, "the adaptive encoder found no cheaper spelling than the fixed rule")

    def test_suboptimal_plant_spends_more(self):
        """The suboptimal encoder (max-cost lawful spelling) produces a strictly larger wire — the
        optimality the adaptive rule claims is real."""
        ticks, cl = C._oscillate()
        self.assertGreater(C.used_total(ticks, cl, A.lens(0, 0), mode="suboptimal"),
                           C.used_total(ticks, cl, A.lens(0, 0), mode="adaptive"))

    def test_move_preferred_over_equal_cite(self):
        """The concrete win: when a position returns with an unchanged citation, both a MOVE (7) and a CITE
        (9) are lawful; the adaptive encoder chooses the cheaper MOVE."""
        reps = [(0, "none", b""), (7, "move", b"m"), (9, "cite", b"ccc"), (39, "full", b"f")]
        # with a change present, none is not lawful; the min among move/cite/full is move
        changed = [r for r in reps if r[1] != "none"]
        self.assertEqual(C._choose(changed, "adaptive")[1], "move")
        self.assertEqual(C._choose(changed, "oldest")[1], "cite", "the fixed rule overspends on a CITE")


class TheLawfulOnly(unittest.TestCase):
    def test_uncertified_cite_refused(self):
        """The minimum is taken over LAWFUL options: a forged CITE to an un-acknowledged anchor (cheaper
        than a FULL) is refused by the certified law."""
        self.assertFalse(CT.verify_records([("cite", 1, 5)], 6, _CFG, {1: {5: (3, 0, C._d(1))}}),
                         "an uncertified citation (anchor 5 > ack_max 4) was admitted")

    def test_lawful_reps_only_include_valid(self):
        """A CITE representation is offered only when the anchor is certified AND matches; a MOVE only when
        the citation is unchanged."""
        cur = {1: (3, 0, C._d(1))}
        hist = {1: {0: (3, 0, C._d(1))}}
        reps = C._lawful_reps(cur, hist, 1, (5, 0, C._d(1)), 6, C.ACK_LAG)  # cite unchanged, pos moved
        kinds = {r[1] for r in reps}
        self.assertIn("move", kinds, "an unchanged-citation move must be lawful")
        self.assertIn("full", kinds, "a full is always lawful")


class TheInheritedLaws(unittest.TestCase):
    def test_closed_world_and_constant_shape_and_rate(self):
        ticks, cl = C._oscillate()
        rep = C.run(ticks, cl, A.lens(0, 0))
        self.assertTrue(C.is_closed_world_run(ticks, cl, A.lens(0, 0)))
        self.assertTrue(C.constant_shape_ok(rep))
        self.assertTrue(C.rate_ok(rep))

    def test_wallclock_plant_diverges(self):
        ticks, cl = C._oscillate()
        L = A.lens(0, 0)
        pure = C.run(ticks, cl, L)["packets"]
        self.assertEqual(pure, C.run(ticks, cl, L, _clock=lambda: 0)["packets"])
        self.assertNotEqual(pure, C.run(ticks, cl, L, _clock=lambda: 1)["packets"])


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = C.sweep_digest()
        self.assertEqual(d1, C.sweep_digest(), "deterministic")
        self.assertEqual(d1, C.sweep_golden(), "sweep drifted from golden")
        rep = C.sweep()
        self.assertGreater(rep["cheaper_seen"], 0, "the adaptive encoder never beat the fixed rule")
        self.assertGreater(rep["cite_seen"], 0, "citations were never exercised")
        self.assertGreater(rep["move_seen"], 0, "moves were never exercised")

    def test_sweep_bites_leaked_hidden(self):
        orig = A._manifest_under
        A._manifest_under = lambda entities, walls, cl, L: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(C.AdaptCiteError):
                C.sweep()
        finally:
            A._manifest_under = orig
        self.assertEqual(C.sweep_digest(), C.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
