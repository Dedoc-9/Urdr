# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the photo→wireframe tracer (tools/tracer/photo_trace.py).

The tracer is an AUTHORING tool — the aesthetics of a trace are not gate-able. But
its deterministic core IS, and one invariant is load-bearing: the tracer must mint a
design's identity by the SAME `URDROBJ2` canon law the browser editor uses, so a
CLI-traced design and the editor agree on the digest. That cross-tool identity is
pinned to the digest the actual designer canon function produces (computed in node
from urdr_designer.html's `canonBytes`), so a drift in either reddens here.

Pinned laws:
  * `design_digest` reproduces the BROWSER's URDROBJ2 canon (fixed reference square →
    dc086bf1…) — CLI ≡ editor identity;
  * the canon is load-bearing: an un-normalized-edge variant produces a DIFFERENT
    digest (the edge min-sort is not decorative);
  * decode is deterministic and from-scratch: a synthesized PGM and a synthesized
    PNG (zlib, filter 0) round-trip to the same grayscale grid;
  * tracing a synthetic filled square yields a closed integer loop of a few vertices,
    deterministically twice;
  * refusals are typed and whole: JPEG magic → TRACE-REFUSE (stdlib can't DCT);
    a blank image (no silhouette) → TRACE-REFUSE; a corrupt header → TRACE-REFUSE;
  * every emitted coordinate is an integer (the N4/authoring boundary — snap, never
    a float)."""
import hashlib
import os
import struct
import sys
import unittest
import zlib

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "tracer")
if _p not in sys.path:
    sys.path.insert(0, _p)

import photo_trace as PT                                   # noqa: E402

_BROWSER_SQUARE = "dc086bf1ae439d08ed267f4b45b605c629ddf294efc56b9b339f12311bddf696"
_REF_SQUARE = ([(0, 0, 0), (40, 0, 0), (40, 24, 0), (0, 24, 0)],
               [(0, 1), (1, 2), (2, 3), (3, 0)])


def _pgm(grid):
    """P5 binary PGM bytes from a grid of 0..255 rows."""
    h = len(grid); w = len(grid[0])
    head = ("P5\n%d %d\n255\n" % (w, h)).encode("ascii")
    return head + bytes(v for row in grid for v in row)


def _png_gray(grid):
    """A minimal 8-bit grayscale PNG (filter 0) — exercises the from-scratch decoder."""
    h = len(grid); w = len(grid[0])
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(row) for row in grid)   # filter byte 0 per scanline
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def _square_grid(n=32, m=6):
    """Light background (240) with a dark filled square (20) inset by m."""
    return [[20 if (m <= x < n - m and m <= y < n - m) else 240
             for x in range(n)] for y in range(n)]


class Canon(unittest.TestCase):
    def test_design_digest_matches_browser(self):
        verts, edges = _REF_SQUARE
        self.assertEqual(PT.design_digest(verts, edges), _BROWSER_SQUARE,
                         "tracer canon diverged from the editor's URDROBJ2 law")

    def test_edge_normalization_is_load_bearing(self):
        verts, edges = _REF_SQUARE
        good = PT.design_digest(verts, edges)
        # feed edges reversed + unsorted; the canon must normalize them to the same digest
        scrambled = [(3, 0), (2, 3), (0, 1), (1, 2)]
        self.assertEqual(PT.design_digest(verts, scrambled), good,
                         "canon is not order-invariant — normalization broken")
        # a DIFFERENT topology must differ (non-vacuity of the digest)
        self.assertNotEqual(PT.design_digest(verts, [(0, 1), (1, 2), (2, 3)]), good)

    def test_defect_canon_without_normalization_diverges(self):
        verts, edges = _REF_SQUARE
        self.assertNotEqual(PT.design_digest_defect_raw_edges(verts, [(1, 0), (2, 1), (3, 2), (0, 3)]),
                            _BROWSER_SQUARE,
                            "the defect canon matched the golden — normalization not load-bearing")


class Decode(unittest.TestCase):
    def test_pgm_and_png_agree(self):
        grid = _square_grid()
        gp = PT.decode_bytes(_pgm(grid))
        gn = PT.decode_bytes(_png_gray(grid))
        self.assertEqual(gp, gn, "PGM and PNG decoders disagree on the same grid")
        self.assertEqual(gp.w, len(grid[0])); self.assertEqual(gp.h, len(grid))

    def test_jpeg_refused_typed(self):
        with self.assertRaises(PT.TraceError) as ctx:
            PT.decode_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 32)   # JPEG SOI+APP0
        self.assertEqual(ctx.exception.code, "TRACE-REFUSE")

    def test_corrupt_header_refused(self):
        with self.assertRaises(PT.TraceError) as ctx:
            PT.decode_bytes(b"not an image at all")
        self.assertEqual(ctx.exception.code, "TRACE-REFUSE")


class Trace(unittest.TestCase):
    def test_square_traces_to_closed_integer_loop_twice(self):
        img = PT.decode_bytes(_pgm(_square_grid()))
        d1 = PT.trace_design(img, name="sq")
        d2 = PT.trace_design(img, name="sq")
        self.assertEqual(d1["digest"], d2["digest"], "tracing is nondeterministic")
        vs = d1["verts"]
        self.assertGreaterEqual(len(vs), 4)
        self.assertLessEqual(len(vs), 12, "a square should simplify to a few corners")
        for p in vs:
            self.assertEqual((p["x"], p["y"], p.get("z", 0)),
                             (int(p["x"]), int(p["y"]), int(p.get("z", 0))),
                             "a non-integer coordinate escaped the snap")
        # closed loop: n edges for n verts, each vertex used twice
        self.assertEqual(len(d1["edges"]), len(vs))

    def test_blank_image_refused(self):
        blank = [[240] * 24 for _ in range(24)]
        with self.assertRaises(PT.TraceError) as ctx:
            PT.trace_design(PT.decode_bytes(_pgm(blank)), name="blank")
        self.assertEqual(ctx.exception.code, "TRACE-REFUSE")

    def test_emits_loadable_project(self):
        img = PT.decode_bytes(_pgm(_square_grid()))
        proj = PT.project_json(PT.trace_design(img, name="sq"))
        self.assertEqual(proj["format"], "URDR-PROJECT-1")
        self.assertEqual(len(proj["designs"]), 1)
        self.assertIn("digest", proj["designs"][0])


if __name__ == "__main__":
    unittest.main()
