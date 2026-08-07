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
from raster import _fdiv, _g, RenderError, Framebuffer, MAGIC   # noqa: E402,F401  URDRFB1 reused


def _int(name, v):
    """Quantization is the CALLER's declared act (the `voxin` law). A float that
    reached `focal * x` would produce a float pixel here and an integer one in any
    conforming placement — a silent divergence with no record."""
    if not isinstance(v, int) or isinstance(v, bool):
        raise RenderError("RENDER-REFUSE", f"{name} must be an integer (got {v!r})")
    return v


def project(vertex, focal, cx, cy, znear=1):
    """Project a 3D vertex to an exact integer screen pixel, or REFUSE.

    `focal > 0`, image centre `(cx, cy)`, `znear > 0`. A vertex with `z < znear`
    (at or behind the near plane) is a typed refusal `RENDER-REFUSE`, not a wrap.
    The pixel is the exact floor of a rational (frozen `floor_divmod`).

    THE PRECONDITIONS ARE NOW ENFORCED. They were stated in this docstring and
    checked nowhere, and all three were reachable: `focal=0` was ADMITTED and
    collapsed every vertex onto the centre pixel; `focal<0` was ADMITTED and
    mirrored the image through it; and `znear<0` was ADMITTED and projected
    geometry BEHIND the camera — `project((10,10,-3), 8, 0, 0, znear=-5)` returned
    `(-27, 27)`, bypassing the near-plane refusal this docstring advertises as the
    module's headline safety property. `claim != code`.

    The final sum is guarded too. `cx + _fdiv(...)` was outside `_g()`, so
    `project((1,0,1), 1, 2**63-1, 0)` returned `px = 2**63` — an i64 overflow with
    no refusal, the same shape `renderbound` found one rung down."""
    focal = _int("focal", focal)
    znear = _int("znear", znear)
    cx, cy = _int("cx", cx), _int("cy", cy)
    if focal <= 0:
        raise RenderError("RENDER-REFUSE", f"focal must be positive (got {focal})")
    if znear <= 0:
        raise RenderError("RENDER-REFUSE", f"znear must be positive (got {znear})")
    x, y, z = (_int("vertex component", c) for c in vertex)
    if z < znear:
        raise RenderError("RENDER-REFUSE",
                          f"vertex at/behind near plane (z={z} < znear={znear})")
    px = _g(cx + _fdiv(focal * x, z))
    py = _g(cy - _fdiv(focal * y, z))
    return (px, py)


def project_orthographic(vertex, focal, cx, cy, znear=1):
    """THE CONTROL — a projector that ignores depth: `px = cx + x`, `py = cy - y`.

    The vanishing-point property is only evidence if something FAILS it, and the
    thing that fails it is a camera with no perspective. That control was described
    in this module's prose and in the gate's own docstring, and it did not exist:
    the gate computed `ortho_gap = [40 for _ in zs]` and then asserted
    `ortho_gap[0] == ortho_gap[-1]` — a list literal compared to itself, a
    tautology that could not fail (L23). This is the projector that comment named.

    Same admission law as `project`, so the two differ in the depth division and
    nowhere else — a control that also relaxed the preconditions would be
    measuring two things at once."""
    focal = _int("focal", focal)
    znear = _int("znear", znear)
    cx, cy = _int("cx", cx), _int("cy", cy)
    if focal <= 0:
        raise RenderError("RENDER-REFUSE", f"focal must be positive (got {focal})")
    if znear <= 0:
        raise RenderError("RENDER-REFUSE", f"znear must be positive (got {znear})")
    x, y, z = (_int("vertex component", c) for c in vertex)
    if z < znear:
        raise RenderError("RENDER-REFUSE",
                          f"vertex at/behind near plane (z={z} < znear={znear})")
    return (_g(cx + x), _g(cy - y))


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


def _rail_gap(proj, x_half, zs, focal, cx, cy, znear):
    return [proj((x_half, 0, z), focal, cx, cy, znear)[0]
            - proj((-x_half, 0, z), focal, cx, cy, znear)[0] for z in zs]


def rail_gap(x_half, zs, focal, cx, cy, znear=1):
    """The vanishing-point signature: the projected pixel gap between two parallel
    rails at world `x = ±x_half`, receding through depths `zs`. Under perspective
    this is monotonically non-increasing and shrinks toward the vanishing pixel;
    `rail_gap_orthographic` is the control that keeps it constant."""
    return _rail_gap(project, x_half, zs, focal, cx, cy, znear)


def rail_gap_orthographic(x_half, zs, focal, cx, cy, znear=1):
    """The same measurement through the depth-blind projector: constant `2*x_half`
    at every depth. COMPUTED, not asserted — the gate compares this against
    `rail_gap` rather than against a literal it wrote down itself."""
    return _rail_gap(project_orthographic, x_half, zs, focal, cx, cy, znear)
