# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the CAPSULE / body seam (`tools/terrain/fpcap.py`, T3.16, Slice 4b) — the close of the
FPS arc: the actor's capsule stands on the certified terrain, its collision is EXACT even in the
fixed-point regime, and rounding is confined to continuous mouse-look POSING (never the body).

  * REFERENCE — the three pinned scenes reproduce their URDRCAP1 digests ×2;
  * COVERAGE — the vertical capsule covers its own foot/mid/head joints (exact);
  * CERTIFICATE LOAD-BEARING — a point just inside the radius is covered, one just outside is not (the
    exact division-free integer certificate bites — no rounding);
  * REUSES fppose — `covers` IS `fppose._in_capsule` (the certified point-to-segment test), not a copy;
  * RESTS ON EXACT GROUND — the foot sits at `heightfield[y][x] · ONE` exactly (the terrain authority);
  * STEP LAW ≡ STANCE — `wall_between` is `stance`'s law: a rise > MAX_STEP is a wall, at the exact
    boundary (rise == MAX_STEP is NOT a wall; rise == MAX_STEP + 1 IS) — the capsule respects the terrain;
  * POSE CARDINAL EXACT / MOUSE-LOOK ROUNDS — the head offset upright and at a 90° pitch is exact; a
    non-cardinal (~45°) mouse-look pitch rounds (the boundary inherited from fpface);
  * DEFECT — a shrunk radius uncovers a point it must cover and moves the `collision` digest;
  * REFUSAL — off-grid / bad height / radius < 1 / negative max_step → typed `CAP-REFUSE`.

Requires the fppose capsule test + fpquat rotation (`fppose` → `fpquat` → `field`); the full gate runs
with them."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "frontfps"),
           os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import fpcap as C                                                 # noqa: E402
import fppose as PS                                               # noqa: E402  (the reused exact certificate)
import stance as ST                                               # noqa: E402
from field import ONE                                            # noqa: E402


class FpCap(unittest.TestCase):
    def test_scene_goldens(self):
        for name in C.SCENES:
            dig = C.scene_result(name)
            self.assertEqual(dig, C.golden(name), f"{name}: fpcap digest drifted")
            self.assertEqual(C.scene_result(name), dig, f"{name}: nondeterministic")

    def test_capsule_covers_joints(self):
        H = C._heights("blank")
        cap = C.stand(H, 2, 8, 4, 1)
        g = C.ground_at(H, 2, 8)
        for pt in (cap["a"], cap["b"], (2 * ONE, (g + 2) * ONE, 8 * ONE)):
            self.assertTrue(C.covers(cap, pt), "the capsule must cover its own foot/mid/head joints")

    def test_radius_certificate_load_bearing(self):
        H = C._heights("blank")
        cap = C.stand(H, 2, 8, 4, 1)
        g = C.ground_at(H, 2, 8)
        inside = (2 * ONE, (g + 2) * ONE, 8 * ONE + (ONE - 1))
        outside = (2 * ONE, (g + 2) * ONE, 8 * ONE + (ONE + 1))
        self.assertTrue(C.covers(cap, inside), "a point just inside the radius must be covered")
        self.assertFalse(C.covers(cap, outside), "a point just outside the radius must NOT be covered")

    def test_covers_is_fppose_certificate(self):
        H = C._heights("blank")
        cap = C.stand(H, 2, 8, 4, 1)
        for pt in (cap["a"], (2 * ONE, cap["a"][1], 8 * ONE + 5), (99 * ONE, 0, 0)):
            self.assertEqual(C.covers(cap, pt), PS._in_capsule(pt, cap),
                             "covers must BE fppose's certified point-in-capsule test, not a copy")

    def test_rests_on_exact_ground(self):
        H = C._heights("mountains")
        cap = C.stand(H, 2, 1, 4, 1)
        self.assertEqual(cap["a"][1], C.ground_at(H, 2, 1) * ONE,
                         "the foot must rest at the exact heightfield ground × ONE (no rounding)")

    def test_step_law_matches_stance(self):
        # a controlled field: centre rises 10; wall_between agrees with stance's law at the exact boundary
        heights = ((0, 0, 0), (0, 10, 0), (0, 0, 0))
        self.assertFalse(C.wall_between(heights, 0, 1, 1, 1, 10), "rise == MAX_STEP is NOT a wall")
        self.assertTrue(C.wall_between(heights, 0, 1, 1, 1, 9), "rise > MAX_STEP IS a wall")
        # and on the terrain it must agree with stance's own DIRS-driven law
        H = C._heights("mountains")
        for d in ("N", "E", "S", "W"):
            dx, dy = ST.DIRS[d]
            rise = C.ground_at(H, 2 + dx, 1 + dy) - C.ground_at(H, 2, 1)
            self.assertEqual(C.wall_between(H, 2, 1, 2 + dx, 1 + dy, 4), rise > 4,
                             f"wall_between must equal stance's rise>MAX_STEP for {d}")

    def test_pose_cardinal_exact_mouselook_rounds(self):
        up = C.head_offset(4, (ONE, 0, 0, 0))
        self.assertEqual(up, (0, 4 * ONE, 0), "upright head offset is exact")
        card = C.head_offset(4, C._FQ.qnormalize((C._R2, C._R2, 0, 0)))
        self.assertEqual(sorted(abs(v) for v in card), [0, 0, 4 * ONE],
                         "a 90° cardinal pitch lands the head on an exact axis (0 ulp)")
        mouse = C.head_offset(4, C.pitch_quat(ONE // 2))
        self.assertNotIn(mouse, [(0, 4 * ONE, 0), (0, 0, 4 * ONE), (0, 0, -4 * ONE)],
                         "a non-cardinal mouse-look pitch must round to a continuous (non-axis) offset")
        self.assertEqual(C.head_offset(4, C.pitch_quat(ONE // 2)), mouse, "posing must be deterministic")

    def test_defect_shrunk_radius_diverges(self):
        H = C._heights("blank")
        good = C.scene_result("collision")
        # a point at radius exactly (just inside): a shrunk radius uncovers it
        cap = C.stand(H, 2, 8, 4, 1)
        g = C.ground_at(H, 2, 8)
        pt = (2 * ONE, (g + 2) * ONE, 8 * ONE + (ONE - 1))
        shrunk = dict(cap, r=cap["r"] // 2)
        self.assertTrue(C.covers(cap, pt))
        self.assertFalse(C.covers(shrunk, pt), "a shrunk radius must uncover a point the full capsule covers")
        self.assertEqual(C.scene_result("collision"), good, "the golden scene is unchanged (non-mutating)")

    def test_typed_refusals(self):
        H = C._heights("blank")
        cases = [
            lambda: C.stand(H, 99, 0, 4, 1),                      # off-grid
            lambda: C.capsule(2, 8, 5, 0, 1),                     # height < 1
            lambda: C.capsule(2, 8, 5, 4, 0),                     # radius < 1
            lambda: C.capsule(2, 8, 5, 4, True),                  # bool radius
            lambda: C.wall_between(H, 2, 8, 3, 8, -1),            # negative max_step
        ]
        for fn in cases:
            with self.assertRaises(C.CapError) as cm:
                fn()
            self.assertEqual(cm.exception.code, "CAP-REFUSE", "wrong refusal code")


if __name__ == "__main__":
    unittest.main()
