# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Exact perspective projection (renderer rung 3) — the projective chart swap.

A pinhole camera at the origin looking down +z maps a 3D point `(x, y, z)` to the
image plane at focal length `f`: `screen = (f·x/z, f·y/z)`. The real-valued screen
position is generally irrational, BUT rasterization only needs the integer PIXEL,
and the floor of a rational is *exact*. So projection to the pixel grid is done
with the frozen, cross-placed `floor_divmod` (via `raster._fdiv`):

        px = cx + floor(f·x / z)
        py = cy − floor(f·y / z)          (y-up world → y-down screen)

This is **exact and reproducible, not rounded** — unlike the continuous fixed-point
substrate, perspective-to-pixel introduces no approximation; the only stops are a
typed refusal on i64 overflow (`RENDER-REFUSE`) and the **near-plane clip**: a
vertex at or behind the near plane (`z < znear`, `znear > 0`) cannot be projected
and is refused, never wrapped.

The defining property of perspective — parallel receding lines converge to a
vanishing point — is exact here: two rails at world `x = ±h` project to a pixel
gap `floor(f·h/z) − floor(−f·h/z)` that is **monotonically non-increasing in z**
and shrinks toward the vanishing pixel, while an orthographic projector keeps the
gap constant (the non-vacuity control). No new invariant, no new glyph — a chart
swap over the both-placements `div`. Consumes `raster` (rung 1 framebuffer + exact
floor division); the frame law is the same `URDRFB1` color image."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import _fdiv, RenderError, Framebuffer, MAGIC   # noqa: E402,F401  URDRFB1 reused


def project(vertex, focal, cx, cy, znear=1):
    """Project a 3D vertex to an exact integer screen pixel, or REFUSE.

    `focal > 0`, image centre `(cx, cy)`, `znear > 0`. A vertex with `z < znear`
    (at or behind the near plane) is a typed refusal `RENDER-REFUSE`, not a wrap.
    The pixel is the exact floor of a rational (frozen `floor_divmod`)."""
    x, y, z = vertex
    if z < znear:
        raise RenderError("RENDER-REFUSE",
                          f"vertex at/behind near plane (z={z} < znear={znear})")
    px = cx + _fdiv(focal * x, z)
    py = cy - _fdiv(focal * y, z)
    return (px, py)


def project_or_none(vertex, focal, cx, cy, znear=1):
    """`project`, but a near-plane / overflow refusal returns None (a clipped
    vertex) instead of raising — for callers that drop clipped geometry."""
    try:
        return project(vertex, focal, cx, cy, znear)
    except RenderError:
        return None


def draw_wireframe(fb, verts, edges, focal, cx, cy, znear=1, values=None):
    """Project every vertex and draw each edge as an exact integer line into `fb`
    (rung-1 rasterizer). `edges` is a list of (i, j) index pairs; `values` an
    optional per-edge 8-bit intensity (default 255). All vertices must be in
    front of the near plane (a behind-camera vertex refuses)."""
    pts = [project(v, focal, cx, cy, znear) for v in verts]
    for k, (a, b) in enumerate(edges):
        val = 255 if values is None else values[k]
        (x0, y0), (x1, y1) = pts[a], pts[b]
        fb.draw_line(x0, y0, x1, y1, val)
    return fb


def rail_gap(x_half, zs, focal, cx, cy, znear=1):
    """The vanishing-point signature: the projected pixel gap between two parallel
    rails at world `x = ±x_half`, receding through depths `zs`. Under perspective
    this is monotonically non-increasing and shrinks toward the vanishing pixel;
    an orthographic projector (px = cx ± x_half) keeps it constant."""
    return [project((x_half, 0, z), focal, cx, cy, znear)[0]
            - project((-x_half, 0, z), focal, cx, cy, znear)[0] for z in zs]
