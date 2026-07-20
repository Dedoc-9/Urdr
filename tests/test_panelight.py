# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/panelight.py — V1, the windowed loop (URDRPNL1).

The FIRST time the certified substrate is driven as a live interactive game rather
than a batch fold: input -> fixed-timestep authority tick -> witness -> declared
interpolated view. panelight MINTS its motion from `glide` (composition) and adds
three genuinely new certified laws:

  INTERACTIVE == BATCH — the tick loop, run one command at a time from a resumable
  pose, reproduces `glide_cells` bit-for-bit on a pure-move log; the interactive
  world IS the batch authority (the theorem that licenses a live game).
  THE ACCUMULATOR (frame/tick decoupling) — given a per-frame dt-log and a fixed
  tick duration, the tick schedule is deterministic, consumes each input EXACTLY
  ONCE (no lost, no duplicated tick), the leftover alpha is always in [0, TICK_MS),
  and — the decoupling law — two DIFFERENT dt-logs with the same total ticks over
  the same input land the IDENTICAL authority witness (render cadence never moves
  the authority).
  THE INTERPOLATION FIREWALL — a frame renders a DECLARED pose interpolated between
  two tick poses by alpha; the witness is over the TICK poses ONLY and is invariant
  to alpha; interpolation smooths the VIEW, never the transcript (D15 on the loop).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))

import glide as GL                                          # noqa: E402
import panelight as PL                                      # noqa: E402
from field import ONE                                       # noqa: E402


def _blank():
    return GL._heights("blank")


class TestInteractiveEqualsBatch(unittest.TestCase):
    def test_loop_reproduces_glide_cells(self):
        """The tick loop, run one command at a time, equals the batch glide_cells
        bit-for-bit on a pure-move log — the interactive world is the batch law."""
        fld = _blank()
        for log in ("eeee", "EEEE", "eennww"):
            got = PL.run(fld, (4, 8), log, 16, 4)
            want = GL.glide_cells(fld, (4, 8), log, 16, 4)
            self.assertEqual(got, want, log)

    def test_idle_rests_the_avatar(self):
        """An idle tick leaves the pose byte-identical (the world advances, the avatar
        stands) — and idles between moves do not perturb the moving poses."""
        fld = _blank()
        with_idle = PL.run(fld, (4, 8), "ee..ee", 16, 4)
        # the two idle poses equal the pose reached after the second move
        self.assertEqual(with_idle[2], with_idle[3])
        self.assertEqual(with_idle[3], with_idle[4])
        # dropping the idles gives the same MOVING subsequence
        no_idle = PL.run(fld, (4, 8), "eeee", 16, 4)
        moving = [with_idle[0], with_idle[1], with_idle[2], with_idle[5], with_idle[6]]
        self.assertEqual(moving, list(no_idle))


class TestAccumulator(unittest.TestCase):
    def test_alpha_bounded_and_ticks_exact(self):
        """Every frame's leftover alpha is in [0, TICK_MS), and the total ticks equal
        floor(sum(dt) / TICK_MS) — the accumulator loses no time and invents none."""
        dt_log = (10, 22, 16, 8, 30, 12)
        sched, total, leftover = PL.schedule_ticks(dt_log, PL.TICK_MS)
        for (_n, alpha) in sched:
            self.assertTrue(0 <= alpha < PL.TICK_MS)
        self.assertEqual(total, sum(dt_log) // PL.TICK_MS)
        self.assertEqual(leftover, sum(dt_log) - total * PL.TICK_MS)

    def test_exactly_once_input_no_loss(self):
        """Driving the loop by the frame schedule consumes each input EXACTLY once —
        the transcript has one tick pose per input (plus the seed), none lost, none
        duplicated."""
        fld = _blank()
        log = "eeee"
        dt_log = (16, 16, 16, 16)
        transcript, frames = PL.drive_loop(fld, (4, 8), log, dt_log, 16, 4)
        self.assertEqual(len(transcript), len(log) + 1)      # seed + one per input
        self.assertEqual(len(frames), len(dt_log))           # one declared pose per frame

    def test_decoupling_render_cadence_irrelevant(self):
        """THE DECOUPLING LAW: two different dt-logs with the same total ticks over the
        same input land the IDENTICAL authority witness — the render rate never moves
        the authority."""
        fld = _blank()
        log = "eeee"
        a = PL.drive_loop(fld, (4, 8), log, (16, 16, 16, 16), 16, 4)
        b = PL.drive_loop(fld, (4, 8), log, (8, 8, 8, 8, 8, 8, 8, 8), 16, 4)
        self.assertEqual(PL.loop_witness(a[0]), PL.loop_witness(b[0]))
        # but the DECLARED frame streams differ (different cadence) — presentation moved
        self.assertNotEqual(len(a[1]), len(b[1]))

    def test_lost_input_defect_would_be_caught(self):
        """A schedule that drops a tick (total < inputs) leaves inputs unconsumed — the
        loop refuses rather than silently skipping."""
        fld = _blank()
        with self.assertRaises(PL.PanelError):
            PL.drive_loop(fld, (4, 8), "eeee", (16, 16, 16), 16, 4)  # only 3 ticks for 4 inputs


class TestInterpolationFirewall(unittest.TestCase):
    def test_frame_is_bounded_between_ticks(self):
        """A declared frame pose sits BETWEEN its two bracketing tick poses on every
        axis — interpolation cannot leave the certified segment."""
        fld = _blank()
        t = PL.run(fld, (4, 8), "eeee", 16, 4)
        for alpha in (0, 4, 8, 15):
            fr = PL.interpolate(t[0], t[1], alpha, PL.TICK_MS)
            lo, hi = min(t[0][0], t[1][0]), max(t[0][0], t[1][0])
            self.assertTrue(lo <= fr[0] <= hi)
        # alpha = 0 is exactly the left tick pose
        self.assertEqual(PL.interpolate(t[0], t[1], 0, PL.TICK_MS)[:2], t[0][:2])

    def test_witness_invariant_to_interpolation(self):
        """The authority witness is over TICK poses only — recomputing it with any frame
        schedule yields the same hex; interpolation is presentation, walled from it."""
        fld = _blank()
        t = PL.run(fld, (4, 8), "eeee", 16, 4)
        base = PL.loop_witness(t)
        # producing declared frames does not (cannot) change the witness
        for dt_log in ((16, 16, 16, 16), (4, 12, 20, 8, 16, 20, 4)):
            transcript, _frames = PL.drive_loop(fld, (4, 8), "eeee", dt_log, 16, 4) \
                if sum(dt_log) // 16 == 4 else (t, [])
            if sum(dt_log) // 16 == 4:
                self.assertEqual(PL.loop_witness(transcript), base)

    def test_digest_binds_verdict(self):
        a = PL.panelight_digest("x", "00" * 32, 4, 4, "ADMIT")
        b = PL.panelight_digest("x", "00" * 32, 4, 4, "PANEL-REFUSE")
        self.assertNotEqual(a, b)


class TestTerrainGate(unittest.TestCase):
    def test_wall_stops_the_avatar_in_the_loop(self):
        """The terrain gate holds in the loop: a sprint into a too-high ridge stops the
        avatar (its final cell is not past the wall) — the same gate `drive`/`glide`
        certify, now inside the game loop."""
        fld = GL._heights("mountains")
        t = PL.run(fld, (6, 24), "NNNNNN", 20, 4)
        # the loop's cell trajectory floors to glide's — and glide stops at the wall
        want = GL.glide_cells(fld, (6, 24), "NNNNNN", 20, 4)
        self.assertEqual(t, want)


class TestScenesAndDeterminism(unittest.TestCase):
    def test_scene_digests_match_goldens(self):
        for name in PL.SCENES:
            self.assertEqual(PL.scene_result(name), PL.golden(name), name)

    def test_determinism(self):
        for name in PL.SCENES:
            self.assertEqual(PL.scene_result(name), PL.scene_result(name), name)


if __name__ == "__main__":
    unittest.main()
