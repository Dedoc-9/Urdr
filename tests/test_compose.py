#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the Stage 5 COMPOSITION LAWS (URDRCMP1).

The arc proves its slices individually. Measured before this module existed, the gate carried 26 rows
across `rollback` (10), `lease` (6), `persist` (6) and `boundary` (4) — and ZERO for identity,
associativity or replay. Those three exist only BETWEEN modules, which is why nothing had them: a
defect in a seam is invisible to every test that stays inside one component.

`inside-correct != composes`.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in (os.path.join(ROOT, "tools", "netcode"), os.path.join(ROOT, "tools", "physics")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import compose as CM  # noqa: E402


class TheSegmentationLaw(unittest.TestCase):
    """Cut the run at any tick, resume from that tick's snapshot, reproduce the tail exactly. This is
    what makes a checkpoint a checkpoint."""

    def test_no_cut_of_any_world_diverges(self):
        rows = CM.the_segmentation_law()
        self.assertEqual(rows, (("collide", 0, 39), ("arena", 0, 119)))
        for name, bad, cuts in rows:
            self.assertEqual(bad, 0, f"{name}: resuming from a snapshot changed the tail")
            self.assertGreater(cuts, 0, f"{name}: zero cuts examined is a vacuous pass")

    def test_two_independent_worlds(self):
        """One fixture is not a corpus. The worlds differ in physics and in length — body-body
        contact at T=40 against the arena at T=120."""
        names = [n for n, _b, _c in CM.the_segmentation_law()]
        self.assertEqual(sorted(names), ["arena", "collide"])
        self.assertEqual(len({c for _n, _b, c in CM.the_segmentation_law()}), 2,
                         "both worlds have the same length; they may not be independent")

    def test_an_unknown_world_is_a_typed_refusal(self):
        with self.assertRaises(CM.ComposeError) as cm:
            CM.segmentation_divergences("no_such_world")
        self.assertEqual(cm.exception.code, "COMPOSE-REFUSE")


class ThePlantsBite(unittest.TestCase):
    """Non-vacuity, and specifically from TWO directions. A law that holds is worth exactly what its
    check's ability to fail is worth, and these two failure modes are not interchangeable."""

    def test_both_plants_and_their_exact_counts(self):
        perturb, hidden, cuts = CM.the_law_can_fail()
        self.assertEqual((perturb, hidden, cuts), (1, 39, 39))

    def test_a_perturbed_snapshot_diverges_at_exactly_one_cut(self):
        """Moving ONE word of the starting state must show up at that cut and nowhere else. A
        comparison insensitive to the state it compares would report 0 here and still report 0 on the
        clean run, and the law would look identical."""
        perturb, _hidden, _cuts = CM.the_law_can_fail()
        self.assertEqual(perturb, 1, "the comparison is blind to the state it claims to compare")

    def test_hidden_state_diverges_at_every_cut(self):
        """Carrying a value across ticks that the snapshot does not hold is the defect the law exists
        to catch — and it is precisely the one a perturbation plant would never exercise, which is
        why one plant is not enough."""
        _perturb, hidden, cuts = CM.the_law_can_fail()
        self.assertEqual(hidden, cuts, "hidden state did not break resumption at every cut")


class TheIdentityLaw(unittest.TestCase):
    def test_composing_with_nothing_changes_nothing(self):
        """Asserted separately from segmentation rather than folded in: k=0 and k=T are the
        boundaries, and boundaries are where an off-by-one in a cut-and-resume lives."""
        self.assertEqual(CM.the_identity_law(), (("collide", True), ("arena", True)))


class TheCorpusIsPinned(unittest.TestCase):
    def test_emitted_matches_pinned(self):
        self.assertTrue(CM.emitted_matches_pinned(),
                        "the pinned corpus is not what --emit produces")

    def test_every_scene_reproduces_its_golden(self):
        for n in CM.SCENES:
            self.assertEqual(CM.scene_result(n), CM.golden(n), n)

    def test_an_unknown_golden_is_a_typed_refusal(self):
        with self.assertRaises(CM.ComposeError):
            CM.golden("no_such_scene")

    def test_the_boundary_is_stated(self):
        """The module must say what it does NOT show — that the world state is (pos, vel) in general,
        and that a checkpoint written by `persist` and read back reproduces the tail. The second is
        the replay law across the serialization boundary and is the declared successor, not a claim."""
        doc = CM.__doc__
        self.assertIn("does_not_show", doc)
        self.assertIn("persist", doc)
        self.assertIn("declared successor", doc)


if __name__ == "__main__":
    unittest.main()
