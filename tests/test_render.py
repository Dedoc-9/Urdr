# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-render rung 1 (the deterministic fixed-point rasterizer).

These pin the properties that make a frame a WITNESS under the D11 §4 frame law:
  * a scene's frame digest is reproducible (determinism) and matches its golden;
  * the top-left fill rule tiles a shared edge EXACTLY once (no gap, no double) —
    with a non-vacuity check that the 'closed' rule really does double-cover;
  * integer line rasterization has exact, known coverage;
  * i64 overflow in the viewport transform is a REFUSAL, not a wrap;
  * a corner-sample defect diverges from the center-sample golden (catchable).
No floating point is used anywhere. Each negative test asserts the wrong outcome
would have passed (non-vacuity)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RDIR = os.path.join(_ROOT, "tools", "render")
if _RDIR not in sys.path:
    sys.path.insert(0, _RDIR)

import raster                                        # noqa: E402
import scenes                                        # noqa: E402
from raster import Framebuffer, SUB, NDC_ONE, triangle_pixels, line_pixels  # noqa: E402


def _load_goldens():
    out = {}
    with open(os.path.join(_RDIR, "conformance.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dg = ln.split()
                out[name] = dg
    return out


class FrameDeterminism(unittest.TestCase):
    def test_each_scene_is_reproducible_and_matches_golden(self):
        goldens = _load_goldens()
        self.assertEqual(set(goldens), set(scenes.SCENES))     # corpus complete
        for name, build in scenes.SCENES.items():
            d1, d2 = build().digest(), build().digest()
            self.assertEqual(d1, d2, f"{name} nondeterministic")
            self.assertEqual(d1, goldens[name], f"{name} != golden")


class TopLeftFillRule(unittest.TestCase):
    """Two triangles sharing the main diagonal must cover an 8x8 square exactly
    once each pixel — the shared edge passes through the (i,i) pixel centers."""
    W = H = 8
    A, B = (0, 0), (8 * SUB, 0)
    C, D = (8 * SUB, 8 * SUB), (0, 8 * SUB)

    def _coverage(self, rule):
        cnt = [0] * (self.W * self.H)
        for tri in ((self.A, self.B, self.C), (self.A, self.C, self.D)):
            for (x, y) in triangle_pixels(*tri, self.W, self.H, rule=rule):
                cnt[y * self.W + x] += 1
        return cnt

    def test_topleft_covers_every_pixel_exactly_once(self):
        cnt = self._coverage("topleft")
        self.assertEqual(min(cnt), 1, "a pixel was left uncovered (gap)")
        self.assertEqual(max(cnt), 1, "a pixel was covered twice (double-draw)")

    def test_closed_rule_double_covers_the_shared_edge(self):
        # non-vacuity: the WRONG rule must actually double-cover, else the test
        # above proves nothing.
        cnt = self._coverage("closed")
        self.assertGreaterEqual(sum(1 for c in cnt if c >= 2), 1)

    def test_two_triangles_equal_a_full_square(self):
        full = Framebuffer(self.W, self.H)
        for y in range(self.H):
            for x in range(self.W):
                full.plot(x, y, 0x80)
        self.assertEqual(scenes.scene_quad_two_tri().digest(), full.digest())


class LineCoverage(unittest.TestCase):
    def test_horizontal(self):
        self.assertEqual(line_pixels(2, 5, 6, 5),
                         [(2, 5), (3, 5), (4, 5), (5, 5), (6, 5)])

    def test_vertical(self):
        self.assertEqual(line_pixels(3, 1, 3, 4),
                         [(3, 1), (3, 2), (3, 3), (3, 4)])

    def test_diagonal(self):
        self.assertEqual(line_pixels(0, 0, 3, 3),
                         [(0, 0), (1, 1), (2, 2), (3, 3)])

    def test_reverse_endpoints_same_set(self):
        self.assertEqual(set(line_pixels(1, 2, 7, 5)),
                         set(line_pixels(7, 5, 1, 2)))


class ViewportRefusal(unittest.TestCase):
    def test_overflow_is_a_refusal_not_a_wrap(self):
        with self.assertRaises(raster.RenderError) as ctx:
            raster.viewport_x(NDC_ONE, 10 ** 18)       # W * SUB * ... blows i64
        self.assertEqual(ctx.exception.code, "RENDER-REFUSE")
        # non-vacuity: an in-range viewport call returns a plain int
        self.assertIsInstance(raster.viewport_x(0, 32), int)


class DefectCaught(unittest.TestCase):
    def test_corner_sample_diverges_from_center_golden(self):
        golden = _load_goldens()["tri"]
        fb = Framebuffer(16, 16)
        fb.draw_triangle((2 * SUB, 2 * SUB), (13 * SUB, 4 * SUB),
                         (5 * SUB, 13 * SUB), 0xFF, sample=0)   # corner, not center
        self.assertNotEqual(fb.digest(), golden)


if __name__ == "__main__":
    unittest.main()
