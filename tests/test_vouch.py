# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `vouch` (URDRVCH1) — can rollback reproduce the exact REASON the actor was
grounded?

The claim only has content because the resume starts MID-TRAJECTORY: replaying from the start and
asserting equality would restate that `stride.simulate` is a pure function (L23). These check that
the snapshot is SUFFICIENT at every tick of a real arc, that four perturbations move the reasons and
delivery reorder does not, that a divergence localizes and NAMES A CELL, and that a stale snapshot
REFUSES rather than diverging.

Each planted defect below was run RED before its golden was pinned — including the fixture defect
this rung found in itself: the first `event_tick` perturbation was aimed at a mid-flight tick, which
`stride` correctly ignores as air control, so the clause read INERT and proved nothing."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import vouch as VC                                           # noqa: E402
import contact as CT                                         # noqa: E402
import lockstep as L                                         # noqa: E402
import stride as SR                                          # noqa: E402


class TheResumeReproducesTheReasons(unittest.TestCase):
    def test_at_every_tick_of_the_arc(self):
        """Not one convenient moment: a snapshot that happened to be sufficient at tick 3 and lossy
        at tick 9 would pass a single-point check."""
        holds, n = VC.the_resume_reproduces_the_reasons()
        self.assertTrue(holds)
        self.assertGreater(n, 5)

    def test_positions_and_reasons_are_checked_apart(self):
        """A rung that fused them could not say which had moved."""
        self.assertTrue(VC.the_positions_and_the_reasons_are_checked_apart())

    def test_the_stream_carries_both_kinds(self):
        """L61: an all-grounded or all-airborne arc would make every comparison vacuous — one has
        witnesses everywhere and the other nowhere."""
        w, lg = VC.demo()
        _f, _s, wits = VC.full(w, lg)
        kinds = {("-" if x == "-" else "W") for row in VC.witness_stream(wits) for x in row}
        self.assertEqual(kinds, {"-", "W"})

    def test_a_lossy_snapshot_would_be_caught(self):
        """RED-FIRST, and the whole reason a mid-trajectory resume is the test: drop the vertical
        velocity from the record and the resumed reasons diverge, where a from-the-start replay
        would still have agreed."""
        w, lg = VC.demo()
        frames, _s, wits = VC.full(w, lg)
        snap = VC.snapshot(w, frames, 2)
        lossy = (snap[0], tuple(a[:3] + (0,) for a in snap[1]), snap[2])
        self.assertNotEqual(lossy, snap, "the fixture has no velocity to lose at this tick")
        self.assertNotEqual(VC.witness_stream(VC.resume(w, lossy, lg)[2]),
                            VC.witness_stream(wits[3:]))


class ThePerturbations(unittest.TestCase):
    """Four must move the reasons and two must not."""

    def setUp(self):
        self.v = VC.the_perturbations_bite()

    def test_all_verdicts_hold(self):
        self.assertTrue(VC.the_perturbation_verdicts_hold())

    def test_a_changed_revision_refuses_rather_than_diverging(self):
        self.assertEqual(self.v["revision"], "REFUSED")

    def test_a_changed_cell_and_height_move_the_reasons(self):
        self.assertEqual(self.v["cell"], "moved")
        self.assertEqual(self.v["height"], "moved")

    def test_a_moved_event_tick_moves_the_reasons(self):
        """The fixture defect this rung found in itself: aimed at a mid-flight tick the clause read
        INERT, because `stride` refuses air control and the move changed nothing. A perturbation
        that cannot reach the law it is aimed at is a green result with no content."""
        self.assertEqual(self.v["event_tick"], "moved")

    def test_delivery_is_absorbed(self):
        """The clause that must NOT bite. Without it this rung would certify a witness stream that
        changed whenever anything did."""
        self.assertEqual(self.v["delivery_reorder"], "absorbed")
        self.assertEqual(self.v["delivery_duplicate"], "absorbed")


class TheDivergenceNamesACell(unittest.TestCase):
    """`lockstep.first_desync` localizes to a TICK — the most a digest chain can say, because a
    digest has no parts. A witness has parts."""

    def test_it_localizes(self):
        d, report = VC.the_divergence_localizes()
        self.assertIsNotNone(d)
        tick, actor, wa, wb = d
        self.assertGreaterEqual(tick, 0)
        self.assertEqual(actor, 0)
        self.assertNotEqual(wa, wb)

    def test_the_report_carries_the_cell_and_the_revision(self):
        _d, report = VC.the_divergence_localizes()
        self.assertIn("cell", report)
        self.assertIn("rev-0", report)
        self.assertIn("actor 0", report)

    def test_a_clean_resume_is_silent(self):
        """NON-VACUITY: a detector that always fires reports nothing."""
        self.assertTrue(VC.a_clean_resume_does_not_diverge())

    def test_identical_streams_have_no_divergence(self):
        w, lg = VC.demo()
        _f, _s, wits = VC.full(w, lg)
        s = VC.witness_stream(wits)
        self.assertIsNone(VC.first_witness_divergence(s, s))


class TheStaleSnapshot(unittest.TestCase):
    def test_it_refuses_both_ways(self):
        """One direction alone would be a door that is always shut."""
        self.assertTrue(VC.the_stale_snapshot_refuses_both_ways())

    def test_the_refusal_is_typed_and_says_it_is_not_a_divergence(self):
        w, lg = VC.demo("rev-0")
        frames, _s, _w = VC.full(w, lg)
        snap = VC.snapshot(w, frames, 3)
        other, _l = VC.demo("rev-1")
        with self.assertRaises(VC.VouchError) as ctx:
            VC.resume(other, snap, lg)
        self.assertEqual(ctx.exception.code, "VOUCH-REFUSE")
        self.assertIn("never entitled to run", str(ctx.exception))

    def test_every_malformed_record_is_typed(self):
        w, _lg = VC.demo()
        for bad in ((1, 2), ("x", ((0, 0, 0, 0),), "rev-0"), (-1, ((0, 0, 0, 0),), "rev-0"),
                    (0, ((0, 0, 0, 0), (1, 1, 1, 1)), "rev-0")):
            with self.subTest(repr(bad)):
                with self.assertRaises(VC.VouchError):
                    VC.admit_resume(w, bad)

    def test_the_boundary_is_the_boundary(self):
        w, lg = VC.demo()
        frames, _s, _w = VC.full(w, lg)
        self.assertEqual(VC.admit_resume(w, VC.snapshot(w, frames, 0)), 0)
        with self.assertRaises(VC.VouchError):
            VC.snapshot(w, frames, len(frames))


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in VC.SCENES:
            with self.subTest(name):
                self.assertEqual(VC.scene_result(name), VC.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(VC.vouch_digest(), VC.vouch_digest())

    def test_the_payload_is_readable(self):
        self.assertIn("REFUSED", VC.scene_case("perturbations"))
        self.assertIn("absorbed", VC.scene_case("perturbations"))
        self.assertIn("cell", VC.scene_case("localization"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VC.VouchError):
            VC.scene_case("nope")
        with self.assertRaises(VC.VouchError):
            VC.golden("nope")


if __name__ == "__main__":
    unittest.main()
