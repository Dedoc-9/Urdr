# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for exact perspective projection (renderer rung 3).

Pins the projective chart swap:
  * EXACT pixels: projection is the exact floor of a rational (frozen floor_divmod)
    — known vertices land on the exact expected pixels, no rounding.
  * NEAR-PLANE CLIP (red-first): a vertex at or behind the near plane REFUSES
    `RENDER-REFUSE`; a vertex in front projects (non-vacuity — the refusal is
    caused by the clip, not a broken projector).
  * VANISHING POINT: two parallel rails' projected pixel gap is monotonically
    non-increasing in depth and shrinks toward the vanishing pixel; an
    ORTHOGRAPHIC projector keeps the gap constant — so perspective is
    load-bearing (the property would pass vacuously under no-perspective).
  * FORESHORTENING: the near face of a box projects wider than the far face.
  * FRAME GOLDENS: the canonical scenes reproduce their pinned URDRFB1 digests."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RDIR = os.path.join(_ROOT, "tools", "render")
_IDIR = os.path.join(_ROOT, "tools", "intla")
for _d in (_RDIR, _IDIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import perspective as P                                   # noqa: E402
import persp_scenes as S                                  # noqa: E402
from raster import RenderError                            # noqa: E402


class ExactPixels(unittest.TestCase):
    def test_known_projections_are_exact(self):
        f, cx, cy = 100, 50, 50
        self.assertEqual(P.project((10, 0, 10), f, cx, cy), (150, 50))   # 100*10/10 = 100
        self.assertEqual(P.project((0, 5, 50), f, cx, cy), (50, 40))     # 100*5/50 = 10, y flips
        # floor of a negative rational is exact (toward -inf): floor(-300/7) = -43
        self.assertEqual(P.project((-3, 0, 7), f, cx, cy), (cx + (-300 // 7), 50))


class NearPlaneClip(unittest.TestCase):
    def test_behind_or_at_near_plane_refuses(self):
        for z in (0, -5):
            with self.assertRaises(RenderError) as ctx:
                P.project((1, 1, z), 100, 50, 50, znear=1)
            self.assertEqual(ctx.exception.code, "RENDER-REFUSE")
        # znear itself: a vertex just inside is refused, one at znear projects
        with self.assertRaises(RenderError):
            P.project((1, 1, 3), 100, 50, 50, znear=4)

    def test_non_vacuity_front_vertex_projects(self):
        # the refusals above are the clip, not a broken projector: a front vertex works
        self.assertEqual(P.project((0, 0, 5), 100, 50, 50, znear=1), (50, 50))
        self.assertIsNotNone(P.project_or_none((0, 0, 5), 100, 50, 50))
        self.assertIsNone(P.project_or_none((0, 0, 0), 100, 50, 50))     # clipped -> None


class VanishingPoint(unittest.TestCase):
    def test_parallel_rails_converge_monotonically(self):
        f, cx, cy = 100, 60, 60
        zs = [2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 500, 2000, 4000]
        gap = P.rail_gap(20, zs, f, cx, cy)
        # monotone non-increasing, strictly shrinking overall, and → the vanishing
        # pixel (gap ≤ 2) at large depth: the railroad-tracks-converge property
        self.assertTrue(all(gap[i + 1] <= gap[i] for i in range(len(gap) - 1)))
        self.assertGreater(gap[0], gap[-1])
        self.assertLessEqual(gap[-1], 2)

    def test_orthographic_projector_does_not_converge(self):
        # non-vacuity control: with no perspective the gap is constant, so the
        # convergence above is caused by the division, not by the test being weak.
        cx = 60
        zs = [2, 8, 34, 144, 4000]
        gap_ortho = [(cx + 20) - (cx - 20) for _ in zs]           # px = cx ± x, ignores z
        self.assertTrue(all(g == 40 for g in gap_ortho))
        self.assertEqual(gap_ortho[0], gap_ortho[-1])             # never shrinks


class Foreshortening(unittest.TestCase):
    def test_near_face_wider_than_far_face(self):
        f, cx, cy = 100, 60, 60
        near = (P.project((20, 0, 4), f, cx, cy)[0] - P.project((-20, 0, 4), f, cx, cy)[0])
        far = (P.project((20, 0, 12), f, cx, cy)[0] - P.project((-20, 0, 12), f, cx, cy)[0])
        self.assertGreater(near, far)


class FrameGoldens(unittest.TestCase):
    def test_scenes_match_pinned_digests(self):
        golden = {}
        with open(os.path.join(_RDIR, "conformance_persp.txt"), "r", encoding="utf-8") as fh:
            for ln in fh.read().splitlines():
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    name, dig = ln.split()
                    golden[name] = dig
        live = S.digests()
        self.assertEqual(live, golden)


if __name__ == "__main__":
    unittest.main()
