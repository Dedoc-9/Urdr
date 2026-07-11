# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical Marangoni scenes → URDRFLD1/FIELDFP frame digests.

Three fixed scenes on the frozen fixed-point backend; each evolves a scalar field
under surface-tension-gradient advection (+ diffusion) and digests the result:
  * `marangoni_sharpen` — a 1-D concentration peak that Marangoni keeps sharper
    than diffusion alone would (5×1, 5 steps).
  * `marangoni_peak2d`  — a 2-D centre peak, 10 steps (mass conserved exactly).
  * `marangoni_ridge`   — an alternating hi/lo ridge advected by Marangoni only
    (no diffusion), 3 steps.
Goldens pinned in `conformance_marangoni.txt`; a cross-placement must reproduce
them bit-for-bit."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marangoni as M                                    # noqa: E402


def scene_sharpen():
    lo, hi = M.unit(1, 10), M.unit(1, 1)
    return M.digest(M.run([lo, lo, hi, lo, lo], 5, 1, (1, 20), (1, 8), 5), 5, 1)


def scene_peak2d():
    lo, hi = M.unit(1, 10), M.unit(1, 1)
    grid = [lo] * 25
    grid[12] = hi
    return M.digest(M.run(grid, 5, 5, (1, 20), (1, 10), 10), 5, 5)


def scene_ridge():
    lo, hi = M.unit(2, 10), M.unit(8, 10)
    return M.digest(M.run([lo, hi, lo, hi, lo], 5, 1, (0, 1), (1, 8), 3), 5, 1)


SCENES = {
    "marangoni_sharpen": scene_sharpen,
    "marangoni_peak2d": scene_peak2d,
    "marangoni_ridge": scene_ridge,
}


def digests():
    return {name: fn() for name, fn in SCENES.items()}


if __name__ == "__main__":
    for name, dig in digests().items():
        print(f"{name:18s} {dig}")
