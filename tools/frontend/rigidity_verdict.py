#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rigidity_verdict — an EXACT rigidity certificate for a canonical URDROBJ2 object.

Observability that is authority, not a display float. A canonical object is exactly a
2D rigidity framework `(n, d=2, edges, coords)`, so the exact-integer rigidity layer
(`tools/intla/rigidity`, cross-placed via urdr-math) answers, over ℤ:

    Is this structure RIGID, or does it FLEX? If it flexes, by how many degrees of
    freedom, and WHICH vertices move?

Unlike the replay overlays (which draw float projections of Q32.32 words), this verdict
is a certificate: `rank(R) == d·n − d(d+1)/2` iff the framework is infinitesimally
rigid; otherwise an internal flex names the deforming vertices. `admitted ≠ trusted` —
but a rigidity verdict is checkable, and reproduces on every conforming host.

The architecture keeps its law: the AUTHORITY computes (this module, exact, gated); a
browser DISPLAYS a recorded verdict, it never recomputes rigidity in float. `annotate`
writes the verdict onto a design so a re-opened project shows badges read, not derived.

GRADE: MEASURED (`rigidity_verdict` gate stage, `tests/test_rigidity_verdict.py`) —
the classic frameworks classify exactly to pinned goldens, a flex names its vertices,
and a full-rank defect misclassifies (non-vacuity). The verdict inherits urdr-math's
overflow refusal (`REFUSE`).

  usage:  python3 rigidity_verdict.py project.json [out.json]
          → prints each design's verdict; with out.json, writes a copy annotated with
            recorded verdicts (the editor displays them).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "intla"))
import rigidity as RG                                      # noqa: E402  exact-integer rigidity
import urdr_math                                           # noqa: E402


def _framework(design):
    """(n, d=2, edges, coords) from a design's integer geometry. z is ignored — a
    URDROBJ2 object is a 2D wireframe."""
    coords = [(int(v["x"]), int(v["y"])) for v in design["verts"]]
    edges = [(int(e[0]), int(e[1])) for e in design["edges"]]
    return len(coords), 2, edges, coords


def verdict(design):
    """The exact rigidity verdict of a canonical object. Returns a dict:
    verdict ∈ {RIGID, FLEXIBLE, REFUSE, DEGENERATE}, rank, rigid_rank, dof (>=0),
    moving_verts (the vertices with nonzero flex, for FLEXIBLE)."""
    n, d, edges, coords = _framework(design)
    if n < 2:
        return {"verdict": "DEGENERATE", "rank": 0, "rigid_rank": 0, "dof": 0,
                "moving_verts": [], "note": "fewer than two vertices"}
    R = RG.rigidity_matrix(n, d, edges, coords)
    r = urdr_math.rank(R)
    if r == "REFUSE":
        return {"verdict": "REFUSE", "rank": -1, "rigid_rank": -1, "dof": -1,
                "moving_verts": [], "note": "i64 overflow in exact rank (refused, not approximated)"}
    rr = RG.rigid_rank(n, d)
    if rr < 0:
        rr = 0
    dof = max(0, rr - r)
    if r == rr:
        return {"verdict": "RIGID", "rank": r, "rigid_rank": rr, "dof": 0, "moving_verts": []}
    flex = RG.internal_flex(n, d, edges, coords)
    moving = []
    if flex:
        vec = flex[0] if flex and isinstance(flex[0], list) else flex
        for i in range(n):
            if any(vec[d * i + a] != 0 for a in range(d)):
                moving.append(i)
    return {"verdict": "FLEXIBLE", "rank": r, "rigid_rank": rr, "dof": dof,
            "moving_verts": moving}


def verdict_defect_full_rank(design):
    """THE DEFECT (gate non-vacuity): compares rank to the FULL dimension d·n instead of
    the rigid rank d·n − d(d+1)/2 — i.e. forgets to subtract the trivial motions. Must
    misclassify the rigid triangle (rank 3 ≠ 6 → FLEXIBLE)."""
    n, d, edges, coords = _framework(design)
    R = RG.rigidity_matrix(n, d, edges, coords)
    r = urdr_math.rank(R)
    if r == "REFUSE":
        return {"verdict": "REFUSE"}
    return {"verdict": "RIGID" if r == d * n else "FLEXIBLE", "rank": r}


def annotate(design):
    """Return a copy of the design with a recorded `rigidity` verdict — the browser
    displays this, it never recomputes."""
    out = dict(design)
    v = verdict(design)
    out["rigidity"] = {"verdict": v["verdict"], "dof": v["dof"],
                       "moving_verts": v["moving_verts"]}
    return out


def annotate_project(proj):
    out = dict(proj)
    out["designs"] = [annotate(d) for d in proj.get("designs", [])]
    return out


def main(argv):
    if len(argv) < 2:
        print("usage: rigidity_verdict.py project.json [out.json]")
        return 2
    import json
    with open(argv[1], "r", encoding="utf-8") as fh:
        proj = json.load(fh)
    designs = proj.get("designs", [proj] if "verts" in proj else [])
    for d in designs:
        v = verdict(d)
        tag = {"RIGID": "●", "FLEXIBLE": "◍", "REFUSE": "⊘", "DEGENERATE": "·"}.get(v["verdict"], "?")
        extra = "" if v["verdict"] != "FLEXIBLE" else f"  dof {v['dof']} · moves verts {v['moving_verts']}"
        print(f"  {tag} {d.get('name', '?'):16s} {v['verdict']:10s} rank {v['rank']}/{v['rigid_rank']}{extra}")
    if len(argv) > 2:
        with open(argv[2], "w", encoding="utf-8") as fh:
            json.dump(annotate_project(proj), fh)
        print("wrote annotated project:", argv[2], "(open in urdr_designer.html — verdicts show as badges)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
