# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the rigidity verdict — observability that IS authority.

Every canonical URDROBJ2 object is a rigidity framework `(n, d=2, edges, coords)`. The
verdict — RIGID / FLEXIBLE / REFUSE, with the exact rank, the degrees of freedom, and
the vertices that move under an internal flex — is computed by the exact-integer
`tools/intla/rigidity` layer (cross-placed via urdr-math), so it is AUTHORITATIVE, not
a display float. This is the observability the architecture makes cheap: surfacing a
recorded certificate, not reconstructing engine state.

Pinned laws:
  * the classic frameworks classify correctly and exactly: a triangle is RIGID (dof 0),
    a bare square is FLEXIBLE (dof 1 — the shear mode names the moving vertices), a
    square braced by one diagonal is RIGID, and a square with two diagonals is RIGID
    (over-braced) — each matching its pinned (verdict, rank, dof) golden;
  * a FLEXIBLE verdict NAMES the moving vertices (a non-empty subset of the framework);
  * the verdict is deterministic (same design → same verdict twice);
  * NON-VACUITY: a defect that compares the rank to the FULL dimension (d·n) instead of
    the rigid rank (d·n − d(d+1)/2) misclassifies the rigid triangle — proving the
    trivial-motion subtraction is load-bearing."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("frontend", "intla"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import rigidity_verdict as RV                              # noqa: E402


def _loop(n):
    return [[i, (i + 1) % n] for i in range(n)]


def _design(coords, edges, name="x"):
    return {"name": name,
            "verts": [{"x": x, "y": y, "z": 0} for (x, y) in coords],
            "edges": [list(e) for e in edges]}


SHAPES = {
    "triangle": _design([(0, 0), (30, 0), (15, 20)], [[0, 1], [1, 2], [2, 0]]),
    "square": _design([(0, 0), (40, 0), (40, 24), (0, 24)], _loop(4)),
    "square_diag": _design([(0, 0), (40, 0), (40, 24), (0, 24)], _loop(4) + [[0, 2]]),
    "square_2diag": _design([(0, 0), (40, 0), (40, 24), (0, 24)], _loop(4) + [[0, 2], [1, 3]]),
}


def _corpus():
    path = os.path.join(_ROOT, "tools", "frontend", "conformance_rigidity.txt")
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, verdict, rank, dof = ln.split()
                rows[name] = (verdict, int(rank), int(dof))
    return rows


class RigidityVerdict(unittest.TestCase):
    def test_shapes_match_pinned_verdicts(self):
        g = _corpus()
        for name, design in SHAPES.items():
            v = RV.verdict(design)
            self.assertEqual((v["verdict"], v["rank"], v["dof"]), g[name],
                             f"{name}: got {(v['verdict'], v['rank'], v['dof'])}, pinned {g[name]}")

    def test_triangle_rigid_square_flexible(self):
        self.assertEqual(RV.verdict(SHAPES["triangle"])["verdict"], "RIGID")
        vs = RV.verdict(SHAPES["square"])
        self.assertEqual(vs["verdict"], "FLEXIBLE")
        self.assertGreaterEqual(vs["dof"], 1)

    def test_flexible_names_moving_vertices(self):
        v = RV.verdict(SHAPES["square"])
        self.assertTrue(v["moving_verts"], "a FLEXIBLE verdict must name the vertices that move")
        self.assertTrue(all(0 <= i < 4 for i in v["moving_verts"]))

    def test_bracing_a_square_makes_it_rigid(self):
        self.assertEqual(RV.verdict(SHAPES["square"])["verdict"], "FLEXIBLE")
        self.assertEqual(RV.verdict(SHAPES["square_diag"])["verdict"], "RIGID")

    def test_deterministic_twice(self):
        a = RV.verdict(SHAPES["square"]); b = RV.verdict(SHAPES["square"])
        self.assertEqual(a, b)

    def test_defect_full_rank_misclassifies_triangle(self):
        """Non-vacuity: comparing rank to d·n instead of the rigid rank calls the rigid
        triangle FLEXIBLE — the trivial-motion subtraction is load-bearing."""
        real = RV.verdict(SHAPES["triangle"])["verdict"]
        defect = RV.verdict_defect_full_rank(SHAPES["triangle"])["verdict"]
        self.assertEqual(real, "RIGID")
        self.assertNotEqual(defect, "RIGID",
                            "the full-rank defect still called the triangle rigid — probe vacuous")

    def test_annotate_records_verdict_on_design(self):
        d = dict(SHAPES["square"])
        out = RV.annotate(d)
        self.assertIn("rigidity", out)
        self.assertEqual(out["rigidity"]["verdict"], "FLEXIBLE")


if __name__ == "__main__":
    unittest.main()
