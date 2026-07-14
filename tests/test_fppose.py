#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for posed transforms & capsules (tools/frontfps/fppose.py)."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("frontfps", "physics"):
    p = os.path.join(ROOT, "tools", d)
    if p not in sys.path:
        sys.path.insert(0, p)

import fppose as FP  # noqa: E402
from field import ONE  # noqa: E402


def _corpus():
    path = os.path.join(ROOT, "tools", "frontfps", "conformance_fppose.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split()
                out[k] = v
    return out


class Goldens(unittest.TestCase):
    def test_posed_digest_reproduces_twice(self):
        d1 = FP.posed_digest(FP.demo_rig(), FP.demo_pose(), FP.RADII)
        d2 = FP.posed_digest(FP.demo_rig(), FP.demo_pose(), FP.RADII)
        self.assertEqual(d1, _corpus()["posed_biped"])
        self.assertEqual(d1, d2)

    def test_op_count_pinned(self):
        self.assertEqual(FP.count_pose_world_ops(FP.demo_rig(), FP.demo_pose()),
                         int(_corpus()["pose_ops"]))


class Certificates(unittest.TestCase):
    def test_real_capsules_cover_walk_and_reach(self):
        rig = FP.demo_rig()
        for pose in (FP.demo_pose(), FP.demo_pose_reach()):
            _, wp = FP.pose_world(rig, pose)
            caps = FP.posed_capsules(rig, wp, FP.RADII)
            self.assertTrue(FP.capsules_cover_joints(wp, caps))

    def test_point_in_capsule_is_exact_at_the_boundary(self):
        cap = {"a": (0, 0, 0), "b": (0, 0, 10 * ONE), "r": ONE}
        self.assertTrue(FP._in_capsule((ONE, 0, 5 * ONE), cap))       # exactly on r
        self.assertFalse(FP._in_capsule((ONE + 1, 0, 5 * ONE), cap))  # one ulp out
        self.assertTrue(FP._in_capsule((0, 0, -0 + 0), cap))          # endpoint a
        self.assertFalse(FP._in_capsule((0, 0, 11 * ONE + 1), cap))   # past b + r


class DefectsBite(unittest.TestCase):
    def test_swapped_compose_diverges(self):
        rig, pose = FP.demo_rig(), FP.demo_pose()
        self.assertNotEqual(FP._pose_world_defect_swapped_compose(rig, pose),
                            FP.pose_world(rig, pose))

    def test_local_offset_defect_fails_coverage_on_reach(self):
        rig = FP.demo_rig()
        _, wp = FP.pose_world(rig, FP.demo_pose_reach())
        bad = FP._posed_capsules_defect_local_offsets(rig, FP.RADII)
        self.assertFalse(FP.capsules_cover_joints(wp, bad),
                         "defect covered the reach pose — re-arm the corpus")

    def test_local_offset_defect_indistinguishable_at_rest(self):
        """Documents WHY the reach pose exists: at the identity pose the defect
        is byte-identical to the truth — an eyeball test would pass it."""
        rig = FP.demo_rig()
        identity = tuple((ONE, 0, 0, 0) for _ in rig["bones"])
        _, wp = FP.pose_world(rig, identity)
        good = FP.posed_capsules(rig, wp, FP.RADII)
        bad = FP._posed_capsules_defect_local_offsets(rig, FP.RADII)
        self.assertEqual(good, bad)


class Refusals(unittest.TestCase):
    def _refused(self, fn, why):
        with self.subTest(why=why):
            with self.assertRaises(FP.PoseError) as ctx:
                fn()
            self.assertEqual(ctx.exception.code, "PSE-REFUSE")

    def test_obligations(self):
        rig = FP.demo_rig()
        self._refused(lambda: FP.pose_world(rig, FP.demo_pose()[:3]),
                      "pose length mismatch")
        _, wp = FP.pose_world(rig, FP.demo_pose())
        radii = dict(FP.RADII)
        del radii["head"]
        self._refused(lambda: FP.posed_capsules(rig, wp, radii), "missing radius")
        radii = dict(FP.RADII)
        radii["head"] = 0
        self._refused(lambda: FP.posed_capsules(rig, wp, radii), "zero radius")
        radii = dict(FP.RADII)
        radii["head"] = True
        self._refused(lambda: FP.posed_capsules(rig, wp, radii), "bool radius")


if __name__ == "__main__":
    unittest.main()
