#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the pose & clip canon (tools/frontfps/fpclip.py).

Ordering laws tested from both sides (rule authoring order must NOT move the
trace; keyframe disorder must REFUSE, not sort). The op count is pinned as the
budget's host-independent proxy. `corpus agreement != universal correctness`.
"""
import hashlib
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("frontfps", "physics"):
    p = os.path.join(ROOT, "tools", d)
    if p not in sys.path:
        sys.path.insert(0, p)

import fpclip as FC  # noqa: E402
import fpquat as FQ  # noqa: E402
from field import ONE, _rdiv  # noqa: E402


def _corpus():
    path = os.path.join(ROOT, "tools", "frontfps", "conformance_fpclip.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split()
                out[k] = v
    return out


class Goldens(unittest.TestCase):
    def test_walk_pose_reproduces(self):
        pose = FC.sample_pose(FC.demo_walk(), _rdiv(ONE, 3))
        dig = hashlib.sha256(FC.MAGIC + FC.pose_bytes(pose)).hexdigest()
        self.assertEqual(dig, _corpus()["walk_pose"])

    def test_arena_trace_reproduces_twice(self):
        m = FC.demo_machine()
        d1 = FC.trace_digest(m, FC.TICKS, FC.HZ, FC.SCRIPT)
        d2 = FC.trace_digest(FC.demo_machine(), FC.TICKS, FC.HZ, FC.SCRIPT)
        self.assertEqual(d1, _corpus()["arena_trace"])
        self.assertEqual(d1, d2)

    def test_pose_op_count_pinned(self):
        self.assertEqual(FC.count_pose_ops(FC.demo_walk(), _rdiv(ONE, 3)),
                         int(_corpus()["pose_ops"]))


class SamplingLaws(unittest.TestCase):
    def test_endpoint_lands_on_normalized_keyframe(self):
        clip = FC.demo_twist()
        kf0 = FQ.qnormalize(tuple(clip["tracks"]["root"][0][1]))
        self.assertEqual(FC.sample_pose(clip, 0)[0], kf0)
        kf1 = FQ.qnormalize(tuple(clip["tracks"]["root"][-1][1]))
        self.assertEqual(FC.sample_pose(clip, ONE)[0], kf1)

    def test_loop_wraps_exactly(self):
        walk = FC.demo_walk()
        self.assertEqual(FC.sample_pose(walk, 0), FC.sample_pose(walk, ONE))
        self.assertEqual(FC.sample_pose(walk, ONE // 3),
                         FC.sample_pose(walk, ONE + ONE // 3))

    def test_absolute_tick_time_never_accumulates(self):
        """t_i computed FROM i: tick 3*80 at 240Hz is exactly ONE — no drift."""
        self.assertEqual(_rdiv(240 * ONE, 240), ONE)
        self.assertEqual(sum([_rdiv(ONE, 240)] * 240) == ONE, False)  # naive sum drifts…
        self.assertEqual(_rdiv(240 * ONE, 240), ONE)                  # …absolute does not

    def test_out_of_range_refused_never_clamped(self):
        twist = FC.demo_twist()
        for t in (-1, ONE + 1):
            with self.assertRaises(FC.ClipError):
                FC.sample_pose(twist, t)
        with self.assertRaises(FC.ClipError):
            FC.sample_pose(FC.demo_walk(), -1)   # loop still refuses before t0


class Refusals(unittest.TestCase):
    def _refused(self, fn, why):
        with self.subTest(why=why):
            with self.assertRaises(FC.ClipError) as ctx:
                fn()
            self.assertEqual(ctx.exception.code, "CLIP-REFUSE")

    def test_structural_obligations(self):
        def unsorted():
            c = FC.demo_twist()
            c["tracks"]["root"] = [[ONE, (ONE, 0, 0, 0)], [0, (ONE, 0, 0, 0)]]
            FC.check_clip(c)
        self._refused(unsorted, "unsorted keyframes refused, never sorted")

        def degenerate():
            c = FC.demo_twist()
            c["tracks"]["root"][0][1] = (0, 0, 0, 0)
            FC.check_clip(c)
        self._refused(degenerate, "zero-quaternion keyframe")

        def ambiguous():
            m = FC.demo_machine()
            m["rules"].append({"from": "idle", "to": "idle", "event": "go", "priority": 0})
            FC.check_machine(m)
        self._refused(ambiguous, "two rules share (from,event,priority)")

        def unknown_event():
            m = FC.demo_machine()
            FC.check_machine(m)
            FC.step(m, "idle", "teleport")
        self._refused(unknown_event, "event outside vocabulary (typo totality)")

        def bad_script():
            FC.run_trace(FC.demo_machine(), 10, 240, [[5, "go"], [5, "stop"]])
        self._refused(bad_script, "non-increasing script ticks")


class OrderLaws(unittest.TestCase):
    def test_rule_authoring_order_never_moves_the_trace(self):
        m = FC.demo_machine()
        base = FC.trace_digest(m, FC.TICKS, FC.HZ, FC.SCRIPT)
        m2 = FC.demo_machine()
        m2["rules"] = list(reversed(m2["rules"]))
        self.assertEqual(FC.trace_digest(m2, FC.TICKS, FC.HZ, FC.SCRIPT), base)

    def test_authored_order_defect_diverges(self):
        m = FC.demo_machine()
        self.assertNotEqual(FC.trace_digest_defect_authored_order(m, FC.TICKS, FC.HZ, FC.SCRIPT),
                            FC.trace_digest(m, FC.TICKS, FC.HZ, FC.SCRIPT))

    def test_canonical_choice_is_minimum_priority(self):
        m = FC.demo_machine()
        state, moved = FC.step(m, "walk", "sprint")
        self.assertTrue(moved)
        self.assertEqual(state, "walk")     # prio 2 beats authored-first prio 5


class AutoLoopable(unittest.TestCase):
    def test_certificate_and_witness(self):
        v = FC.auto_loopable(FC.demo_idle(), 4)
        self.assertTrue(v["loopable"])
        self.assertTrue(FC.loop_seam_within(FC.demo_idle(), 4))
        self.assertIn(v["witness_bone"], FC.demo_idle()["bones"])

    def test_twist_is_not_loopable(self):
        self.assertFalse(FC.auto_loopable(FC.demo_twist(), 4)["loopable"])

    def test_w_only_defect_misgrades_twist(self):
        self.assertTrue(FC.auto_loopable_defect_w_only(FC.demo_twist(), 4)["loopable"],
                        "defect no longer mis-grades — re-arm the twist clip")


if __name__ == "__main__":
    unittest.main()
