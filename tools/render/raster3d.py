# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-render rung 2 -- exact 3D depth: z-buffer occlusion + near/far/screen clip.

Rung 1 rasterized flat 2D coverage. This adds true depth occlusion (objects
correctly hide what is behind them) and clipping, staying EXACT and DETERMINISTIC
with no float and no division:

  * per-vertex integer DEPTH z0,z1,z2;
  * per-pixel depth = the exact rational barycentric interpolation
        depth = (w0·z0 + w1·z1 + w2·z2) / (w0+w1+w2)
    where w0,w1,w2 are the integer edge-function weights (their sum is the
    doubled triangle area, > 0 after orientation normalization);
  * the DEPTH TEST is a cross-multiplication, never a division: a fragment at
    num/den is nearer than the stored num'/den' iff  num·den' < num'·den
    (denominators are positive), so the z-buffer stays exact;
  * NEAR/FAR clip: a fragment is kept iff  znear ≤ depth ≤ zfar, i.e.
    znear·den ≤ num ≤ zfar·den (exact);
  * SCREEN clip: a pixel outside [0,W)×[0,H) is never written (the buffer
    tallies any attempt, which the gate asserts stays zero).

Occlusion is ORDER-INDEPENDENT for distinct depths: the nearest fragment wins
regardless of triangle submission order, so the frame is a function of the SET of
triangles (an equal-depth tie deterministically keeps the earlier-written
fragment). The frame digest reuses the rung-1 color-frame law (`URDRFB1`): a
3D-rendered frame is still just an image, hashed the same way, so its digest is a
cross-checkable witness of the *visible* result. Depth/clip are internal.

Scope: orthographic (screen-space) depth; no perspective-correct interpolation
and no geometric Sutherland-Hodgman re-triangulation yet (those arrive with
perspective projection + w-clip, a later rung). Consumes rung-1 primitives;
touches no core; no new glyph."""
import hashlib

from raster import SUB, HALF, edge, MAGIC


def _top_left(dx, dy):
    return (dy > 0) or (dy == 0 and dx < 0)


class DepthFramebuffer:
    """A W×H color buffer with an exact-rational depth buffer and a fixed depth
    range [znear, zfar]. `oob` counts attempted out-of-bounds writes (screen clip
    — it must stay 0)."""
    def __init__(self, w, h, znear, zfar, channels=1):
        if w <= 0 or h <= 0 or w > 4096 or h > 4096:
            raise ValueError(f"framebuffer size out of range ({w}x{h})")
        self.w, self.h, self.channels = w, h, channels
        self.buf = [0] * (w * h)
        self.znum = [None] * (w * h)      # per-pixel depth numerator (None = empty)
        self.zden = [None] * (w * h)      # per-pixel depth denominator (> 0)
        self.znear, self.zfar = znear, zfar
        self.oob = 0

    def _plot(self, x, y, value, num, den):
        if not (0 <= x < self.w and 0 <= y < self.h):
            self.oob += 1
            return                         # screen clip: never write out of bounds
        i = y * self.w + x
        cn, cd = self.znum[i], self.zden[i]
        # nearer = smaller depth; strictly-less replaces (equal keeps the earlier).
        if cn is None or (num * cd < cn * den):
            self.buf[i] = value & 0xFF
            self.znum[i] = num
            self.zden[i] = den

    def draw_triangle_z(self, v0, v1, v2, depths, value):
        """Rasterize a triangle with per-vertex depths (z0,z1,z2), applying the
        exact depth test and near/far/screen clip. Vertices in subpixel coords."""
        (x0, y0), (x1, y1), (x2, y2) = v0, v1, v2
        z0, z1, z2 = depths
        if edge(x0, y0, x1, y1, x2, y2) < 0:            # orientation normalize
            (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
            z1, z2 = z2, z1
        area = edge(x0, y0, x1, y1, x2, y2)
        if area == 0:
            return
        minx = max(0, min(x0, x1, x2) // SUB)
        maxx = min(self.w - 1, max(x0, x1, x2) // SUB)
        miny = max(0, min(y0, y1, y2) // SUB)
        maxy = min(self.h - 1, max(y0, y1, y2) // SUB)
        for py in range(miny, maxy + 1):
            sy = py * SUB + HALF
            for px in range(minx, maxx + 1):
                sx = px * SUB + HALF
                ea = edge(x0, y0, x1, y1, sx, sy)       # weight of v2
                eb = edge(x1, y1, x2, y2, sx, sy)       # weight of v0
                ec = edge(x2, y2, x0, y0, sx, sy)       # weight of v1
                inside = True
                for e, (ax, ay, bx, by) in (
                        (ea, (x0, y0, x1, y1)),
                        (eb, (x1, y1, x2, y2)),
                        (ec, (x2, y2, x0, y0))):
                    if e > 0:
                        continue
                    if e == 0 and _top_left(bx - ax, by - ay):
                        continue
                    inside = False
                    break
                if not inside:
                    continue
                num = eb * z0 + ec * z1 + ea * z2       # depth numerator
                den = area                              # depth denominator (> 0)
                if not (self.znear * den <= num <= self.zfar * den):
                    continue                            # near/far clip
                self._plot(px, py, value, num, den)

    def serialize(self):
        head = MAGIC + self.w.to_bytes(4, "big") + self.h.to_bytes(4, "big") \
            + self.channels.to_bytes(1, "big")
        return head + bytes(self.buf)

    def digest(self):
        return hashlib.sha256(self.serialize()).hexdigest()
