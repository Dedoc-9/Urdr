# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical perspective scenes (renderer rung 3) → URDRFB1 frame digests.

Two wireframe scenes on a fixed 120×120 pinhole camera (focal 100, centre 60,60,
near plane 1), each an exact floor-division projection drawn with the rung-1
rasterizer:
  * `persp_rails` — two parallel rails receding in depth with cross-ties; the
    rails visibly converge toward the vanishing point.
  * `persp_cube` — a wireframe cube whose near face projects larger than its far
    face (perspective foreshortening).
The frame goldens are pinned in `conformance_persp.txt`; an independent placement
(`urdr_render_rs/`) must reproduce them bit-for-bit."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Framebuffer                            # noqa: E402
from perspective import project                           # noqa: E402

F, CX, CY, ZN, W, H = 100, 60, 60, 1, 120, 120


def scene_rails():
    """Two parallel rails (world x = ±20, y = −15) receding through increasing
    depth, drawn as polylines, with cross-ties (sleepers) at each depth."""
    fb = Framebuffer(W, H)
    zs = [2, 3, 5, 8, 13, 21, 34]
    left = [project((-20, -15, z), F, CX, CY, ZN) for z in zs]
    right = [project((20, -15, z), F, CX, CY, ZN) for z in zs]
    for i in range(len(zs) - 1):
        fb.draw_line(*left[i], *left[i + 1], 255)
        fb.draw_line(*right[i], *right[i + 1], 255)
    for i in range(len(zs)):
        fb.draw_line(*left[i], *right[i], 180)            # sleepers
    return fb


def scene_cube():
    """A wireframe cube: near face (z=4) projects larger than the far face (z=12)
    — perspective foreshortening — with the four connecting edges."""
    fb = Framebuffer(W, H)
    half, dn, df = 20, 4, 12
    c = {}
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
        c[("n", i)] = project((sx * half, sy * half, dn), F, CX, CY, ZN)
        c[("f", i)] = project((sx * half, sy * half, df), F, CX, CY, ZN)
    for face, val in (("n", 255), ("f", 200)):
        for i in range(4):
            fb.draw_line(*c[(face, i)], *c[(face, (i + 1) % 4)], val)
    for i in range(4):
        fb.draw_line(*c[("n", i)], *c[("f", i)], 150)     # connectors
    return fb


SCENES = {"persp_rails": scene_rails, "persp_cube": scene_cube}


def digests():
    """name -> URDRFB1 frame digest for every perspective scene."""
    return {name: fn().digest() for name, fn in SCENES.items()}


if __name__ == "__main__":
    for name, dig in digests().items():
        print(f"{name:12s} {dig}")
