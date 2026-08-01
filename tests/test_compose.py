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


class TheSerializationReplayLaw(unittest.TestCase):
    """The commuting diagram: fold_from o deserialize o restore o serialize == fold_from.

    `splice` already gates resumption WITHIN glide for every log and interior split. What nothing
    asserted is that the pose survives the ROUND TRIP THROUGH BYTES and still resumes — a property
    owned by no single module, because the seam spans glide, storecost and persist."""

    def test_both_paths_land_on_the_same_tail(self):
        rows = CM.the_serialization_replay_law()
        self.assertEqual(rows, (("stroll", 4, 0, 0), ("sprint", 4, 0, 0), ("wall", 6, 0, 0)))
        for name, bounds, rt, tail in rows:
            self.assertGreater(bounds, 0, f"{name}: zero boundaries examined is a vacuous pass")
            self.assertEqual(rt, 0, f"{name}: a pose did not survive checkpoint/restore")
            self.assertEqual(tail, 0, f"{name}: the restored pose produced a different future")

    def test_three_axes_no_two_sharing_a_failure_mode(self):
        corrupt, permute, coincide, diverged, testable, total = CM.the_replay_plants()
        self.assertEqual((corrupt, permute, coincide, diverged, testable, total),
                         (14, 14, 0, 11, 11, 14))
        self.assertEqual(corrupt, total, "a corrupted checkpoint was admitted")
        self.assertEqual(diverged, testable, "a wrong continuation did not diverge")

    def test_axis_two_refuses_for_a_reason_that_is_weaker_than_it_looks(self):
        """The permutation was PREDICTED to serialize cleanly and diverge on replay — a silent
        semantic fault. It refuses instead, because `facing` carries a range guard (0..3) and every
        ground height here is >= 24. That is a stronger outcome and a weaker guarantee: the schema is
        protected by a range coincidence, not by structure. This test pins the coincidence count at 0
        so that a future scene with ground heights in 0..3 REDDENS rather than silently passing."""
        _c, permute, coincide, _d, _t, total = CM.the_replay_plants()
        self.assertEqual(permute, total, "a permuted pose serialized cleanly")
        self.assertEqual(coincide, 0,
                         "a boundary now has ground == facing, so the permutation is "
                         "INDISTINGUISHABLE there and axis 2 no longer covers it")

    def test_axis_three_reports_testable_not_total(self):
        """A scene's last boundary has no next command, so there is no wrong continuation to resume
        against. 14 - 3 scenes = 11. Reported as 11 of 11 rather than 11 of 14 with three misses."""
        _c, _p, _co, diverged, testable, total = CM.the_replay_plants()
        self.assertEqual(total - testable, 3, "one untestable final boundary per scene")
        self.assertEqual(diverged, testable)


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
        """The module must say what it does NOT show. The replay law WAS the declared successor and
        has since landed, so the boundary had to move rather than stay true-sounding: it now names the
        schema's range-coincidence weakness, the D11 durability boundary, and a SESSION law as the
        successor. A boundary that survives the thing it was hedging against is a stale boundary."""
        # WHITESPACE-NORMALIZED, because the first version of this test failed on a phrase that was
        # merely LINE-WRAPPED ("D11 durability\nboundary") — the same defect class as the wrapped
        # count phrase in L46, now in a checker rather than a doc. A prose-presence check that is
        # sensitive to where the author happened to break the line is testing the formatting.
        doc = " ".join(CM.__doc__.split())
        self.assertIn("does_not_show", doc)
        self.assertIn("D11 durability boundary", doc)
        self.assertIn("declared successor", doc)
        self.assertIn("SESSION law", doc)
        self.assertNotIn("declared successor to this rung", doc,
                         "the replay law shipped; it can no longer be the successor")


if __name__ == "__main__":
    unittest.main()
