#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical render corpus — the shared scenes whose frame digests are witnesses.

Each scene is a pure function State -> Framebuffer. The gate and the falsifiers
both import THESE, so a golden is pinned once and checked everywhere. Every scene
uses only integer / fixed-point inputs (no float), so its frame digest is a
reproducible witness under the D11 §4 frame law."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import raster                                      # noqa: E402
from raster import Framebuffer, SUB, NDC_ONE, viewport_x, viewport_y   # noqa: E402


def scene_tri():
    """A single filled triangle, subpixel coords, 16x16 (edge/fill + serialize)."""
    fb = Framebuffer(16, 16)
    fb.draw_triangle((2 * SUB, 2 * SUB), (13 * SUB, 4 * SUB), (5 * SUB, 13 * SUB), 0xFF)
    return fb


def scene_tri_ndc():
    """A triangle defined in NDC, mapped through the fixed-point viewport
    transform to 32x32 (exercises viewport_x / viewport_y)."""
    w = h = 32
    ndc = [(-(NDC_ONE * 3 // 4), -(NDC_ONE * 3 // 4)),
           (NDC_ONE * 3 // 4, -(NDC_ONE // 2)),
           (0, NDC_ONE * 3 // 4)]
    v = [(viewport_x(nx, w), viewport_y(ny, h)) for (nx, ny) in ndc]
    fb = Framebuffer(w, h)
    fb.draw_triangle(v[0], v[1], v[2], 0xC0)
    return fb


def scene_line_box():
    """A box outline via integer line rasterization, 16x16."""
    fb = Framebuffer(16, 16)
    for (a, b, c, d) in ((1, 1, 14, 1), (14, 1, 14, 14),
                         (14, 14, 1, 14), (1, 14, 1, 1)):
        fb.draw_line(a, b, c, d, 0xFF)
    return fb


def scene_quad_two_tri():
    """An 8x8 square as TWO triangles sharing the main diagonal, same value.
    The shared edge passes through pixel centers (i,i); the top-left rule must
    cover the whole square with no gap and no double-value — so this frame digest
    equals a fully-covered square."""
    fb = Framebuffer(8, 8)
    a, b = (0, 0), (8 * SUB, 0)
    c, d = (8 * SUB, 8 * SUB), (0, 8 * SUB)
    fb.draw_triangle(a, b, c, 0x80)
    fb.draw_triangle(a, c, d, 0x80)
    return fb


SCENES = {
    "tri": scene_tri,
    "tri_ndc": scene_tri_ndc,
    "line_box": scene_line_box,
    "quad_two_tri": scene_quad_two_tri,
}


if __name__ == "__main__":
    for name in sorted(SCENES):
        print(f"{name} {SCENES[name]().digest()}")
