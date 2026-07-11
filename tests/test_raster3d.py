# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-render rung 2 (3D depth: z-buffer occlusion + clipping).

Pins the properties that make depth occlusion exact and deterministic:
  * each scene's frame digest is reproducible and matches its golden;
  * occlusion is ORDER-INDEPENDENT for distinct depths (draw A,B == draw B,A) —
    the nearest fragment wins regardless of submission order;
  * NON-VACUITY: painter's order (last-write-wins, no depth test) IS
    order-dependent, so the z-test is what earns order-independence;
  * near/far clip removes out-of-range fragments exactly;
  * screen clip never writes out of bounds (fb.oob stays 0);
  * the whole render is deterministic.
No float, no division; each negative test asserts the wrong outcome would pass."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RDIR = os.path.join(_ROOT, "tools", "render")
if _RDIR not in sys.path:
    sys.path.insert(0, _RDIR)

import scenes3d                                        # noqa: E402
from raster import SUB                                 # noqa: E402
from raster3d import DepthFramebuffer                  # noqa: E402


def _p(x, y):
    return (x * SUB, y * SUB)


def _load_goldens():
    out = {}
    with open(os.path.join(_RDIR, "conformance3d.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dg = ln.split()
                out[name] = dg
    return out


# the two overlapping triangles used by the occlusion scenes
_A = (_p(1, 1), _p(12, 1), _p(1, 12), (1, 1, 1), 0xAA)     # near
_B = (_p(10, 10), _p(2, 10), _p(10, 2), (5, 5, 5), 0xBB)   # far


def _render(order):
    fb = DepthFramebuffer(16, 16, 0, 100)
    for (v0, v1, v2, z, c) in order:
        fb.draw_triangle_z(v0, v1, v2, z, c)
    return fb


class FrameGoldens(unittest.TestCase):
    def test_each_scene_reproducible_and_matches_golden(self):
        goldens = _load_goldens()
        self.assertEqual(set(goldens), set(scenes3d.SCENES))
        for name, build in scenes3d.SCENES.items():
            d1, d2 = build().digest(), build().digest()
            self.assertEqual(d1, d2, f"{name} nondeterministic")
            self.assertEqual(d1, goldens[name], f"{name} != golden")
            self.assertEqual(build().oob, 0, f"{name} wrote out of bounds")


class Occlusion(unittest.TestCase):
    def test_z_test_is_order_independent(self):
        self.assertEqual(_render([_A, _B]).digest(), _render([_B, _A]).digest())

    def test_near_occludes_far(self):
        fb = _render([_A, _B])
        self.assertIn(0xAA, fb.buf)          # near visible
        self.assertIn(0xBB, fb.buf)          # far visible where unoccluded

    def test_equal_depth_is_order_dependent_nonvacuity(self):
        # NON-VACUITY: with EQUAL depths the tie is broken by draw order, so the
        # frame depends on order — proving the depth values (not just coverage)
        # are what earn the distinct-depth order-independence above. If coverage
        # alone decided, distinct-depth AB==BA would be vacuous.
        eqA = (_A[0], _A[1], _A[2], (3, 3, 3), 0xAA)
        eqB = (_B[0], _B[1], _B[2], (3, 3, 3), 0xBB)
        self.assertNotEqual(_render([eqA, eqB]).digest(), _render([eqB, eqA]).digest())


class Clipping(unittest.TestCase):
    def test_near_far_clip_removes_out_of_range(self):
        far = DepthFramebuffer(16, 16, 0, 4)             # far plane below the far tri
        far.draw_triangle_z(*_B[:4], _B[4])
        self.assertTrue(all(v == 0 for v in far.buf))    # z=5 > zfar=4: nothing drawn
        near = DepthFramebuffer(16, 16, 0, 4)
        near.draw_triangle_z(*_A[:4], _A[4])
        self.assertIn(0xAA, near.buf)                    # z=1 in range: drawn

    def test_screen_clip_writes_zero_out_of_bounds(self):
        fb = DepthFramebuffer(16, 16, 0, 100)
        fb.draw_triangle_z((-5 * SUB, -5 * SUB), (40 * SUB, 2 * SUB), (2 * SUB, 40 * SUB),
                           (2, 2, 2), 0xCC)
        self.assertEqual(fb.oob, 0)
        self.assertIn(0xCC, fb.buf)                      # still fills valid pixels


if __name__ == "__main__":
    unittest.main()
