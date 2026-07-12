# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the SVG → canonical importer (tools/frontend/svg_import.py).

The first front end admitted down the D14 ladder. SVG is the ideal exercise of the
contract because it is MORE deterministic than the photo tracer: vector paths are
already integer-snappable polylines, so there is no threshold, no contour extraction,
no aesthetic interpretation — only deterministic parsing, fixed-tolerance curve
flattening, integer snap, and the shared URDROBJ2 canon.

Pinned laws (the D14 obligations, for this front end):
  * a `<polygon>`/`<rect>`/`<path M/L/H/V/Z Z>` closes; a `<polyline>` stays OPEN
    (SVG semantics, no closing-by-guess) — and geometry-only identity equals the
    shared canon computed by canon_ref (CLI ≡ the one law);
  * cubic `C` beziers flatten DETERMINISTICALLY at the fixed tolerance (same SVG →
    same digest twice), pinned by a corpus golden;
  * every emitted coordinate is an integer (the snap; never a float);
  * typed refusals, never approximation: an arc `A`, a `transform`, a `<circle>`
    primitive, and a malformed path each raise SVG-REFUSE;
  * provenance carries the source but never enters identity (inherited from D14)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "frontend")
if _p not in sys.path:
    sys.path.insert(0, _p)

import svg_import as SVG                                   # noqa: E402
import canon_ref as CR                                    # noqa: E402


def _corpus():
    path = os.path.join(_ROOT, "tools", "frontend", "conformance_svg.txt")
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dig = ln.split()
                rows[name] = dig
    return rows


class SvgGeometry(unittest.TestCase):
    def test_polygon_matches_shared_canon(self):
        svg = '<svg><polygon points="0,0 40,0 40,24 0,24"/></svg>'
        d = SVG.import_design(svg, name="p")
        verts = [(v["x"], v["y"], 0) for v in d["verts"]]
        edges = [(e[0], e[1]) for e in d["edges"]]
        self.assertEqual(d["digest"], CR.canon(verts, edges))
        self.assertEqual(d["digest"], _corpus().get("square", d["digest"]))
        for v in d["verts"]:
            self.assertEqual((v["x"], v["y"]), (int(v["x"]), int(v["y"])))

    def test_three_constructs_one_square(self):
        """The convergence, at the SVG level: polygon, rect, and a path M/L/H/V/Z of the
        SAME square all produce the identical URDROBJ2 digest (a closed loop, 4/4)."""
        digs = set()
        for svg in ('<svg><polygon points="0,0 40,0 40,24 0,24"/></svg>',
                    '<svg><rect x="0" y="0" width="40" height="24"/></svg>',
                    '<svg><path d="M0 0 H40 V24 H0 Z"/></svg>'):
            d = SVG.import_design(svg, name="q")
            self.assertEqual(len(d["verts"]), 4)
            self.assertEqual(len(d["edges"]), 4)               # closed loop
            for v in d["verts"]:
                self.assertEqual((v["x"], v["y"]), (int(v["x"]), int(v["y"])))
            digs.add(d["digest"])
        self.assertEqual(len(digs), 1, "three SVG constructs of one square disagreed on identity")

    def test_polyline_is_open(self):
        """A polyline is OPEN by SVG semantics — n verts, n-1 edges — never closed by guess."""
        d = SVG.import_design('<svg><polyline points="0,0 40,0 40,24 0,24 0,0"/></svg>', name="pl")
        self.assertEqual(len(d["edges"]), len(d["verts"]) - 1)

    def test_cubic_flatten_deterministic_and_pinned(self):
        svg = '<svg><path d="M0 0 C 20 -40 60 -40 80 0 L 80 30 L 0 30 Z"/></svg>'
        d1 = SVG.import_design(svg, name="c")
        d2 = SVG.import_design(svg, name="c")
        self.assertEqual(d1["digest"], d2["digest"], "flattening is nondeterministic")
        self.assertEqual(d1["digest"], _corpus()["arch"],
                         "cubic flatten digest drifted from its pinned golden")

    def test_admits_under_contract(self):
        d = SVG.import_design('<svg><polygon points="0,0 40,0 40,24 0,24"/></svg>', name="p")
        self.assertEqual(CR.check_design(d), "ADMIT")


class SvgRefusals(unittest.TestCase):
    def _refuses(self, svg, why):
        with self.assertRaises(SVG.SvgError, msg=why) as ctx:
            SVG.import_design(svg, name="x")
        self.assertEqual(ctx.exception.code, "SVG-REFUSE")

    def test_arc_command_refused(self):
        self._refuses('<svg><path d="M0 0 A 30 30 0 0 1 60 0 Z"/></svg>', "arc")

    def test_transform_refused(self):
        self._refuses('<svg><polygon transform="rotate(30)" points="0,0 40,0 40,24"/></svg>', "transform")

    def test_circle_primitive_refused(self):
        self._refuses('<svg><circle cx="20" cy="20" r="18"/></svg>', "circle")

    def test_malformed_path_refused(self):
        self._refuses('<svg><path d="M0 0 L nonsense"/></svg>', "malformed")

    def test_empty_svg_refused(self):
        self._refuses('<svg></svg>', "empty")


if __name__ == "__main__":
    unittest.main()
