# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for D14 — the front-end admission contract.

Multiple authoring modalities (the designer, the photo tracer, and future importers)
converge on ONE authoritative representation. This suite makes that convergence a
law, not a slogan: `tools/frontend/canon_ref.py` is the executable contract — the
reference URDROBJ2 canon plus the integer + provenance obligations every front end
must satisfy to be admitted.

Pinned laws (D14 clauses):
  * REFERENCE ≡ BROWSER: the reference canon reproduces the digest the actual editor
    `canonBytes` produces, over a multi-shape corpus (square/tri/penta/hex6);
  * INDEPENDENT AGREEMENT: the photo tracer's OWN `design_digest` reproduces the same
    corpus digests — two independent implementations, one identity law (the
    cross-placement discipline applied to front ends);
  * PROVENANCE-INDEPENDENCE (the load-bearing invariant): identity is geometry only.
    Two designs with identical geometry but different provenance metadata produce the
    SAME URDROBJ2 digest — downstream cannot tell which front end made the object;
  * INTEGER OBLIGATION: a design carrying a non-integer coordinate is CONTRACT-REFUSE
    (authoring snaps; the runtime never rounds);
  * NON-VACUITY: a defect canon that folds provenance INTO the digest must diverge
    (proving provenance-independence is a real, checked property)."""
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("frontend", "tracer"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import canon_ref as CR                                     # noqa: E402
import photo_trace as PT                                   # noqa: E402


def _corpus():
    path = os.path.join(_ROOT, "tools", "frontend", "conformance_frontend.txt")
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dig = ln.split()
                rows[name] = dig
    return rows


# the shared reference shapes (geometry only; the SAME the browser goldens were cut from)
def _loop(n):
    return [(i, (i + 1) % n) for i in range(n)]


SHAPES = {
    "square": ([(0, 0), (40, 0), (40, 24), (0, 24)], _loop(4)),
    "tri": ([(0, 0), (30, 0), (15, 20)], _loop(3)),
    "penta": ([(0, -20), (19, -6), (12, 16), (-12, 16), (-19, -6)], _loop(5)),
    "hex6": ([(-30, 0), (-15, -12), (15, -12), (30, 0), (15, 12), (-15, 12)], _loop(6)),
}


class FrontEndContract(unittest.TestCase):
    def test_reference_reproduces_browser_goldens(self):
        g = _corpus()
        for name, (verts, edges) in SHAPES.items():
            self.assertEqual(CR.canon(verts, edges), g[name],
                             f"reference canon diverged from the browser golden for {name}")

    def test_tracer_agrees_with_reference_independently(self):
        """The tracer's OWN implementation must reproduce every corpus digest — two
        independent canons, one law."""
        for name, (verts, edges) in SHAPES.items():
            v3 = [(x, y, 0) for (x, y) in verts]
            self.assertEqual(PT.design_digest(v3, edges), CR.canon(verts, edges),
                             f"tracer canon ≠ reference canon for {name}")

    def test_provenance_does_not_affect_identity(self):
        """The engine cannot tell which front end made an object: identical geometry,
        different provenance → identical URDROBJ2 digest."""
        verts, edges = SHAPES["square"]
        a = {"verts": [{"x": x, "y": y, "z": 0} for (x, y) in verts], "edges": [list(e) for e in edges],
             "provenance": {"tool": "designer", "author": "hand"}}
        b = {"verts": [{"x": x, "y": y, "z": 0} for (x, y) in verts], "edges": [list(e) for e in edges],
             "provenance": {"tool": "photo_trace", "source": "cat.png"}}
        self.assertEqual(CR.design_digest(a), CR.design_digest(b),
                         "provenance leaked into identity — the front end is distinguishable")
        self.assertEqual(CR.design_digest(a), _corpus()["square"])

    def test_noninteger_geometry_refused(self):
        verts = [{"x": 0, "y": 0, "z": 0}, {"x": 40.5, "y": 0, "z": 0},
                 {"x": 40, "y": 24, "z": 0}, {"x": 0, "y": 24, "z": 0}]
        with self.assertRaises(CR.ContractError) as ctx:
            CR.check_design({"verts": verts, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})
        self.assertEqual(ctx.exception.code, "CONTRACT-REFUSE")

    def test_integer_geometry_admitted(self):
        verts, edges = SHAPES["square"]
        design = {"verts": [{"x": x, "y": y, "z": 0} for (x, y) in verts],
                  "edges": [list(e) for e in edges], "provenance": {"tool": "test"}}
        self.assertEqual(CR.check_design(design), "ADMIT")

    def test_defect_canon_folds_provenance_diverges(self):
        """Non-vacuity: a canon that mixes provenance into the digest MUST diverge from
        the geometry-only golden — proving provenance-independence is really checked."""
        verts, edges = SHAPES["square"]
        d = {"verts": [{"x": x, "y": y, "z": 0} for (x, y) in verts], "edges": [list(e) for e in edges],
             "provenance": {"tool": "designer"}}
        self.assertNotEqual(CR.design_digest_defect_with_provenance(d), _corpus()["square"],
                            "the provenance-folding defect matched the golden — invariant vacuous")


if __name__ == "__main__":
    unittest.main()
