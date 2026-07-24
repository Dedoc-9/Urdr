# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/boundedhist.py — the BOUNDED-HISTORY OPTIMIZER (URDRBHO1): where look-ahead
earns its teeth on the REAL model. A bounded H-slot keyframe cache couples the ticks (a CITE is lawful only
if its keyframe is still cached), so greedy LRU eviction thrashes while a bounded-window Belady optimum wins.
Composition over `lookahead`, NO new glyph.

  LOOK-AHEAD-HAS-TEETH — on a thrashing cyclic world Belady's wire is strictly smaller than LRU's (the DP
    beats greedy on the real, coupled model — the inversion URDRLKA1 predicted).
  BELADY-OPTIMAL — unbounded Belady achieves the minimum miss count (the offline optimum).
  REPRESENTATION-INDEPENDENCE — every policy reconstructs the same keys; the optimizer changes only the byte
    cost, never the state.
  BOUNDED-CACHE — every eviction slot is within [0, H); a CITE to an evicted / empty slot is refused.
  DETERMINISTIC — the client mirrors the wire deterministically; the wall-clock plant diverges.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import boundedhist as BH                                        # noqa: E402


class TheTeeth(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in BH.SCENES:
            self.assertEqual(BH.scene_result(name), BH.golden(name), name)
            self.assertEqual(BH.scene_result(name), BH.scene_result(name), name)

    def test_lookahead_beats_greedy_on_the_real_model(self):
        """The payoff: with a bounded cache the ticks couple, and Belady (look-ahead) produces a strictly
        smaller wire than LRU (greedy) — the inversion of the URDRLKA1 finding."""
        acc = BH._cyclic(3, 8)
        H = 2
        self.assertLess(BH.cost(acc, H, "belady"), BH.cost(acc, H, "lru"))

    def test_lru_thrashes_on_the_cycle(self):
        """LRU's worst case: on a cycle of length > H, LRU evicts exactly the key about to be used, so it
        misses everything — the coupling is real."""
        acc = BH._cyclic(3, 8)
        self.assertEqual(BH.encode(acc, 2, "lru")["hits"], 0)
        self.assertGreater(BH.encode(acc, 2, "belady")["hits"], 0)


class TheBeladyOptimality(unittest.TestCase):
    def test_belady_is_optimal(self):
        acc = BH._cyclic(4, 6)
        self.assertEqual(BH.encode(acc, 3, "belady", window=len(acc))["misses"], BH._optimal_misses(acc, 3))

    def test_belady_never_worse_than_lru(self):
        for cyc, reps, H in ((3, 8, 2), (4, 5, 2), (5, 4, 3), (4, 6, 3)):
            acc = BH._cyclic(cyc, reps)
            self.assertLessEqual(BH.cost(acc, H, "belady"), BH.cost(acc, H, "lru"))


class TheRepresentationIndependence(unittest.TestCase):
    def test_every_policy_reconstructs_the_same_keys(self):
        acc = BH._cyclic(3, 8)
        H = 2
        self.assertTrue(BH.representation_independent(acc, H))
        for policy in ("lru", "belady"):
            self.assertEqual(BH.client_reconstruct(BH.encode(acc, H, policy)["wire"], H), acc)

    def test_wrong_slot_cite_reconstructs_wrong(self):
        """A CITE that reads the wrong slot reconstructs the wrong key — the client mirror catches the
        divergence (representation-independence has teeth)."""
        acc = BH._cyclic(3, 8)
        H = 2
        wire, honest = BH._forge_wrong_slot(acc, H)
        self.assertNotEqual(BH.client_reconstruct(wire, H), honest)


class TheBoundedCache(unittest.TestCase):
    def test_cache_never_exceeds_H(self):
        acc = BH._cyclic(3, 8)
        self.assertTrue(BH.bounded_cache_ok(acc, 2, "belady"))
        self.assertTrue(BH.bounded_cache_ok(acc, 2, "lru"))

    def test_out_of_range_slot_refused(self):
        with self.assertRaises(BH.BoundedHistError):
            BH.client_reconstruct([("full", 0, 2)], 2)   # slot 2 outside [0,2)

    def test_cite_to_empty_slot_refused(self):
        with self.assertRaises(BH.BoundedHistError):
            BH.client_reconstruct([("cite", 0)], 2)      # nothing cached yet


class TheDeterminism(unittest.TestCase):
    def test_encoding_is_pure(self):
        acc = BH._cyclic(3, 8)
        self.assertEqual(BH.encode(acc, 2, "belady")["wire"], BH.encode(acc, 2, "belady")["wire"])

    def test_wallclock_plant_diverges(self):
        acc = BH._cyclic(3, 8)
        pure = BH.encode(acc, 2, "belady")["wire"]
        self.assertEqual(pure, BH.encode(acc, 2, "belady", _clock=lambda: 0)["wire"])
        self.assertNotEqual(pure, BH.encode(acc, 2, "belady", _clock=lambda: 1)["wire"])


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = BH.sweep_digest()
        self.assertEqual(d1, BH.sweep_digest(), "deterministic")
        self.assertEqual(d1, BH.sweep_golden(), "sweep drifted from golden")
        self.assertGreater(BH.sweep()["teeth_seen"], 0, "look-ahead never beat greedy (no coupling)")

    def test_sweep_bites_wrong_reconstruction(self):
        """L15 — if a policy ever reconstructed the wrong keys, the sweep's representation-independence
        check would raise; a monkeypatched broken reconstruction proves the check bites, clean after."""
        orig = BH.client_reconstruct
        BH.client_reconstruct = lambda wire, H: [-1]          # always wrong
        try:
            with self.assertRaises(BH.BoundedHistError):
                BH.sweep()
        finally:
            BH.client_reconstruct = orig
        self.assertEqual(BH.sweep_digest(), BH.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
