#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-render, rung 1 — a deterministic, fixed-point, integer-only rasterizer.

This is the first MEASURABLE slice of the D11 §4 renderer contract: turn
`State ⟶ Framebuffer` from a shape into `Digest(Frame) = SHA-256(canon(Frame))`,
with the frame reproducible bit-for-bit by any conforming *integer* placement.
NO floating point anywhere. All arithmetic is exact integer / fixed-point, and
any i64 overflow is a REFUSAL (`RENDER-REFUSE`), never a saturate.

Scope, stated honestly (the no-inflation rule): this proves the rasterizer is
deterministic and self-consistent on a stated corpus of scenes and refusals,
across conforming integer implementations. It does NOT claim determinism across
GPU hardware (there is no GPU here) nor completeness for all scenes. `a green
gate certifies these tests on this code`.

Obligations covered by this rung (of D11 §4's eight):
  (1) fixed-point coordinates      -- SUBPIXEL_BITS subpixel precision
  (2) exact edge functions         -- integer cross products, no epsilon
  (3) exact fill rule              -- top-left tie-break (shared edge once)
  (5) deterministic sampling       -- pixel-center sample, fixed scan order
  (7) canonical serialization      -- MAGIC|W|H|C|row-major bytes -> SHA-256
Plus a fixed-point viewport transform and integer line rasterization.
Depends on: urdr-math (`floor_divmod`, exact floor division). Consumes no core.
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "intla"))
from urdr_math import floor_divmod                       # noqa: E402  exact floor division

SUBPIXEL_BITS = 8
SUB = 1 << SUBPIXEL_BITS          # subpixel units per pixel
HALF = SUB >> 1                    # pixel-center offset, in subpixel units
NDC_ONE = 1 << 16                  # fixed-point 1.0 for NDC inputs (Q16.16)
IMAX = (1 << 63) - 1               # i64 magnitude bound
MAGIC = b"URDRFB1"                 # framebuffer format tag (part of frame identity)


class RenderError(Exception):
    """A typed renderer refusal. `code` mirrors the kernel's URDR-* discipline:
    a refusal is never a wrapped/saturated pixel, it is a stop."""
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _g(v):
    """i64 guard: any intermediate outside [-IMAX, IMAX] is a refusal, not a wrap."""
    if v > IMAX or v < -IMAX:
        raise RenderError("RENDER-REFUSE", f"i64 overflow ({v} out of range)")
    return v


def _fdiv(num, den):
    """Exact floor division through urdr-math; its 'REFUSE' becomes RENDER-REFUSE."""
    r = floor_divmod(_g(num), _g(den))
    if r == "REFUSE":
        raise RenderError("RENDER-REFUSE", f"floor_divmod refused ({num}/{den})")
    return r[0]


# -- viewport transform: NDC (fixed-point) -> subpixel screen coordinates -------
def viewport_x(ndc_x, w):
    """NDC x in [-NDC_ONE, +NDC_ONE] -> subpixel screen x in [0, w*SUB). Exact
    floor; y-independent. Overflow refuses."""
    return _fdiv(_g((_g(ndc_x + NDC_ONE)) * _g(w * SUB)), 2 * NDC_ONE)


def viewport_y(ndc_y, h):
    """NDC y in [-NDC_ONE, +NDC_ONE] -> subpixel screen y, TOP-LEFT origin
    (y flipped: +1 is the top row). Exact floor; overflow refuses."""
    return _fdiv(_g((_g(NDC_ONE - ndc_y)) * _g(h * SUB)), 2 * NDC_ONE)


# -- exact edge function --------------------------------------------------------
def edge(ax, ay, bx, by, px, py):
    """Signed area x2 of triangle (A, B, P) = cross(B-A, P-A), exact integer.
    > 0 : P left of A->B (for this y-down convention, interior side after
    orientation normalization). Overflow refuses."""
    return _g(_g((bx - ax) * (py - ay)) - _g((by - ay) * (px - ax)))


def _orient2d(ax, ay, bx, by, cx, cy):
    return edge(ax, ay, bx, by, cx, cy)


def _top_left(dx, dy):
    """Top-left fill rule for a positively-oriented (area>0) triangle, y-down:
    a boundary sample (edge function == 0) is INSIDE iff its edge is a LEFT edge
    (dy > 0) or a TOP edge (dy == 0 and dx < 0). This makes a shared edge belong
    to exactly one of the two triangles that meet on it."""
    return (dy > 0) or (dy == 0 and dx < 0)


def triangle_pixels(v0, v1, v2, w, h, rule="topleft", sample=HALF):
    """Pixels (x, y) covered by triangle v0,v1,v2 (subpixel coords), scanned in
    canonical order (y outer, x inner). `rule`='topleft' applies the tie-break;
    'closed' (E>=0, no tie-break) is the deliberate DEFECT used for non-vacuity.
    `sample`=HALF samples pixel centers; sample=0 (corner) is another defect."""
    (x0, y0), (x1, y1), (x2, y2) = v0, v1, v2
    if _orient2d(x0, y0, x1, y1, x2, y2) < 0:      # normalize to area > 0
        (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
    area = _orient2d(x0, y0, x1, y1, x2, y2)
    if area == 0:
        return []                                   # degenerate: no coverage
    edges = ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0))
    minx = max(0, _fdiv(min(x0, x1, x2), SUB))
    maxx = min(w - 1, _fdiv(max(x0, x1, x2), SUB))
    miny = max(0, _fdiv(min(y0, y1, y2), SUB))
    maxy = min(h - 1, _fdiv(max(y0, y1, y2), SUB))
    out = []
    for py in range(miny, maxy + 1):
        sy = py * SUB + sample
        for px in range(minx, maxx + 1):
            sx = px * SUB + sample
            inside = True
            for (ax, ay, bx, by) in edges:
                e = edge(ax, ay, bx, by, sx, sy)
                if e > 0:
                    continue
                if e == 0 and rule == "topleft" and _top_left(bx - ax, by - ay):
                    continue
                if e == 0 and rule == "closed":
                    continue
                inside = False
                break
            if inside:
                out.append((px, py))
    return out


# -- integer line rasterization (deterministic Bresenham, pixel coords) ---------
def line_pixels(x0, y0, x1, y1):
    """All pixels on the segment (x0,y0)-(x1,y1), integer PIXEL coords, exact
    integer Bresenham. ENDPOINT-SYMMETRIC: a segment is undirected, so the
    endpoints are canonicalized (lexicographically smaller first) before
    rasterizing — line(A,B) and line(B,A) yield the identical pixel list."""
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    if (x1, y1) < (x0, y0):                        # canonical undirected order
        x0, y0, x1, y1 = x1, y1, x0, y0
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    out = []
    x, y = x0, y0
    while True:
        out.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return out


# -- framebuffer + canonical serialization + frame digest -----------------------
class Framebuffer:
    """A W x H single-channel (8-bit) integer buffer, top-left origin. The one
    canonical serialization is its only identity: MAGIC | W | H | C | pixels."""
    def __init__(self, w, h, channels=1):
        if w <= 0 or h <= 0 or w > 4096 or h > 4096:
            raise RenderError("RENDER-REFUSE", f"framebuffer size out of range ({w}x{h})")
        self.w, self.h, self.channels = w, h, channels
        self.buf = [0] * (w * h)

    def plot(self, x, y, value):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buf[y * self.w + x] = value & 0xFF

    def draw_triangle(self, v0, v1, v2, value, rule="topleft", sample=HALF):
        for (px, py) in triangle_pixels(v0, v1, v2, self.w, self.h, rule, sample):
            self.plot(px, py, value)

    def draw_line(self, x0, y0, x1, y1, value):
        for (px, py) in line_pixels(x0, y0, x1, y1):
            self.plot(px, py, value)

    def serialize(self):
        """Canonical bytes: format tag, dimensions, channel count, then pixels
        row-major from the top-left. Dimensions are part of identity."""
        head = MAGIC + self.w.to_bytes(4, "big") + self.h.to_bytes(4, "big") \
            + self.channels.to_bytes(1, "big")
        return head + bytes(self.buf)

    def digest(self):
        """The frame-digest law (D11 §4): Digest(Frame) = SHA-256(canon(Frame))."""
        return hashlib.sha256(self.serialize()).hexdigest()


if __name__ == "__main__":
    fb = Framebuffer(8, 8)
    fb.draw_triangle((0, 0), (7 * SUB, 0), (0, 7 * SUB), 0xFF)
    print("frame digest:", fb.digest())
