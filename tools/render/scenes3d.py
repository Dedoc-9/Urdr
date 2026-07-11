# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical 3D (depth) render corpus -- each frame digest is a witness.

A scene builds a DepthFramebuffer and returns it. Module basename `scenes3d` is
globally unique across tools/ (the gate shares one sys.path)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import SUB                                 # noqa: E402
from raster3d import DepthFramebuffer                  # noqa: E402


def _p(x, y):
    return (x * SUB, y * SUB)


def scene_occlusion():
    """A near triangle (z=1) overlapping a far one (z=5): the near one occludes
    the far one in the overlap, the far one shows where unoccluded."""
    fb = DepthFramebuffer(16, 16, 0, 100)
    fb.draw_triangle_z(_p(1, 1), _p(12, 1), _p(1, 12), (1, 1, 1), 0xAA)
    fb.draw_triangle_z(_p(10, 10), _p(2, 10), _p(10, 2), (5, 5, 5), 0xBB)
    return fb


def scene_gradient():
    """A depth-gradient triangle (near at one corner, far at the others) over a
    flat mid-depth triangle: exact per-pixel depth interpolation decides who wins."""
    fb = DepthFramebuffer(16, 16, 0, 100)
    fb.draw_triangle_z(_p(1, 1), _p(14, 1), _p(1, 14), (1, 9, 9), 0x11)
    fb.draw_triangle_z(_p(1, 1), _p(14, 1), _p(1, 14), (5, 5, 5), 0x22)
    return fb


def scene_nearfar():
    """Far plane at z=4: the far triangle (z=5) is entirely clipped away; only the
    near triangle (z=1) survives."""
    fb = DepthFramebuffer(16, 16, 0, 4)
    fb.draw_triangle_z(_p(1, 1), _p(12, 1), _p(1, 12), (1, 1, 1), 0xAA)
    fb.draw_triangle_z(_p(10, 10), _p(2, 10), _p(10, 2), (5, 5, 5), 0xBB)
    return fb


def scene_screenclip():
    """A triangle extending far outside the screen is cleanly cropped: no pixel
    outside [0,16)² is ever written (fb.oob stays 0)."""
    fb = DepthFramebuffer(16, 16, 0, 100)
    fb.draw_triangle_z((-5 * SUB, -5 * SUB), (40 * SUB, 2 * SUB), (2 * SUB, 40 * SUB),
                       (2, 2, 2), 0xCC)
    return fb


SCENES = {
    "occlusion": scene_occlusion,
    "gradient": scene_gradient,
    "nearfar": scene_nearfar,
    "screenclip": scene_screenclip,
}


if __name__ == "__main__":
    for name in sorted(SCENES):
        fb = SCENES[name]()
        print(name, fb.digest(), "oob=" + str(fb.oob))
