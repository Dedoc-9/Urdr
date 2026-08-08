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
import hashlib
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


#: The content address of the FRAMEWORK a verdict describes. The census read this module
#: as GUARDED-COMPUTATION — a typed refusal with no computed identity — and that missing
#: half was pointing at a live defect rather than a formality.
#:
#: MEASURED: `annotate` recorded {verdict, dof, moving_verts} with NOTHING binding the badge
#: to the geometry it came from, and the docstring says the browser "displays this, it never
#: recomputes". So a design edited after annotation keeps its badge. A rigid triangle
#: annotated RIGID, then given a moved vertex and a dropped edge, still reads RIGID while the
#: truth is FLEXIBLE with 1 degree of freedom — a certificate describing a structure that no
#: longer exists, and nothing in the tree could tell.
#:
#: Edges are canonicalised (each sorted, then the list sorted) because the framework is a
#: SET of edges — reordering them is the same structure and must digest the same. Vertex
#: order is NOT canonicalised: coords[i] IS vertex i, and `moving_verts` indexes it.
FRAMEWORK_MAGIC = b"URDRRGV1"


class VerdictError(Exception):
    """A typed refusal. `RIGIDITY-REFUSE` is a stop, never a stale badge shown as fresh."""

    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def framework_digest(design):
    """SHA-256 over the exact framework `(n, d, edges, coords)` — the identity a recorded
    verdict is a verdict ABOUT."""
    n, d, edges, coords = _framework(design)
    h = hashlib.sha256()
    h.update(FRAMEWORK_MAGIC)
    h.update(n.to_bytes(4, "big"))
    h.update(d.to_bytes(1, "big"))
    for (x, y) in coords:
        h.update(x.to_bytes(9, "big", signed=True))
        h.update(y.to_bytes(9, "big", signed=True))
    canon = sorted(tuple(sorted(e)) for e in edges)
    h.update(len(canon).to_bytes(4, "big"))
    for a, b in canon:
        h.update(int(a).to_bytes(4, "big", signed=True))
        h.update(int(b).to_bytes(4, "big", signed=True))
    return h.hexdigest()


def annotation_is_current(design):
    """Is the recorded badge still a verdict about THIS geometry? A design with no
    annotation, or one whose record predates the content address, is a typed REFUSAL — 'no
    badge' and 'a wrong badge' are different facts and must not both return False."""
    rec = design.get("rigidity")
    if not isinstance(rec, dict):
        raise VerdictError("RIGIDITY-REFUSE", "design carries no recorded verdict")
    if "framework" not in rec:
        raise VerdictError("RIGIDITY-REFUSE",
                           "recorded verdict cites no framework; it cannot be checked")
    return rec["framework"] == framework_digest(design)


def the_stale_badge_is_caught():
    """THE FALSIFIER, and the defect it replays. Annotate a rigid triangle, then move a
    vertex and drop an edge: the badge still says RIGID, the truth is FLEXIBLE, and before
    the content address nothing could tell. Now the citation does."""
    tri = {"verts": [{"x": 0, "y": 0}, {"x": 4, "y": 0}, {"x": 0, "y": 3}],
           "edges": [[0, 1], [1, 2], [2, 0]]}
    fresh = annotate(tri)
    if not annotation_is_current(fresh) or fresh["rigidity"]["verdict"] != "RIGID":
        return False
    stale = dict(fresh)
    stale["verts"] = [{"x": 0, "y": 0}, {"x": 4, "y": 0}, {"x": 99, "y": 99}]
    stale["edges"] = [[0, 1], [1, 2]]
    return (not annotation_is_current(stale)
            and stale["rigidity"]["verdict"] == "RIGID"
            and verdict(stale)["verdict"] == "FLEXIBLE")


def the_citation_is_edge_order_invariant():
    """The framework is a SET of edges: reordering them, or writing an edge backwards, is
    the same structure and must not move the address. A digest that changed would make
    every re-serialisation look like an edit."""
    a = {"verts": [{"x": 0, "y": 0}, {"x": 4, "y": 0}, {"x": 0, "y": 3}],
         "edges": [[0, 1], [1, 2], [2, 0]]}
    b = {"verts": a["verts"], "edges": [[2, 1], [0, 2], [1, 0]]}
    return framework_digest(a) == framework_digest(b)


def the_citation_reads_the_geometry():
    """NON-VACUITY: an address that ignored the coordinates would be order-invariant too,
    and useless. Moving one vertex by one unit must move it."""
    a = {"verts": [{"x": 0, "y": 0}, {"x": 4, "y": 0}, {"x": 0, "y": 3}],
         "edges": [[0, 1], [1, 2], [2, 0]]}
    b = {"verts": [{"x": 0, "y": 0}, {"x": 4, "y": 0}, {"x": 0, "y": 4}],
         "edges": a["edges"]}
    c = {"verts": a["verts"], "edges": [[0, 1], [1, 2]]}
    return (framework_digest(a) != framework_digest(b)
            and framework_digest(a) != framework_digest(c))


def the_refusal_is_typed():
    """'No badge' and 'a wrong badge' are different facts."""
    for bad in ({"verts": [], "edges": []},
                {"verts": [], "edges": [], "rigidity": {"verdict": "RIGID"}}):
        try:
            annotation_is_current(bad)
            return False
        except VerdictError as exc:
            if exc.code != "RIGIDITY-REFUSE":
                return False
    return True


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
                       "moving_verts": v["moving_verts"],
                       "framework": framework_digest(design)}
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
