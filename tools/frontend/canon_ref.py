#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""canon_ref — the executable form of the D14 front-end admission contract.

Multiple authoring modalities (the designer, the photo tracer, and future importers —
SVG, CAD, procedural generators) converge on ONE authoritative representation. This
module is the REFERENCE implementation of the canon every front end must reproduce,
plus the obligations a design must satisfy to be admitted. It is to front ends what
the Python reference is to placements: independent front-end implementations must
agree with it bit-for-bit, and that agreement is the whole convergence claim.

The URDROBJ2 canon (byte-identical to `urdr_designer.html` canonBytes):

    SHA-256("URDROBJ2|v{n}|x,y,z|…|e{m}|a-b|…")

with each edge normalized min-first and the edge list lexically sorted. IDENTITY IS
GEOMETRY ONLY — provenance metadata (which tool made the object, its source file, an
author) is carried alongside but never enters the digest, so downstream physics /
render / replay / netcode cannot tell which front end produced an object. Authoring
snaps to integers; a non-integer coordinate is CONTRACT-REFUSE (the runtime never
rounds — the N4/WORLD-REFUSE boundary, one layer up).

The admission ladder any new front end follows (D14 §obligations):
  1. deterministic normalization of its input;
  2. typed refusals for ambiguous/unsupported constructs (never approximate);
  3. produce canonical URDROBJ2 through its OWN implementation;
  4. match the pinned canon corpus (this module's reference);
  5. red-first defect fixtures;
  6. cross-place if the front end becomes load-bearing;
  7. admit.

Admitted front ends today: the designer (`urdr_designer.html`), the photo tracer
(`tools/tracer/photo_trace.py`), and the SVG importer (`svg_import.py`) — each an
independent implementation reproducing this canon.

GRADE: the contract's checkable core is MEASURED (`frontend_contract` gate stage,
`tests/test_frontend_contract.py`) — reference ≡ browser goldens, tracer ≡ reference
independently, provenance-independence, the integer obligation, and a non-vacuity
defect. The AESTHETIC quality of any front end's extraction is out of scope, as ever.
"""
import hashlib
import math


class ContractError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _r(v):
    """Round half up (JavaScript Math.round semantics), so canon coords agree."""
    return math.floor(v + 0.5)


def _is_int(v):
    return isinstance(v, int) or (isinstance(v, float) and v == int(v))


# ---- the canon (the one law every front end reproduces) ------------------------------
def canon(verts, edges):
    """The reference URDROBJ2 digest. `verts` = iterable of (x, y[, z]); `edges` =
    iterable of (a, b). Byte-identical to the editor's canonBytes."""
    parts = ["URDROBJ2", "v%d" % len(verts)]
    for v in verts:
        x, y = v[0], v[1]
        z = v[2] if len(v) > 2 else 0
        parts.append("%d,%d,%d" % (_r(x), _r(y), _r(z)))
    norm = sorted((min(a, b), max(a, b)) for (a, b) in edges)
    parts.append("e%d" % len(norm))
    for (a, b) in norm:
        parts.append("%d-%d" % (a, b))
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _geometry(design):
    """Extract (verts, edges) from a design dict — GEOMETRY ONLY. Provenance and any
    other metadata are ignored: identity does not depend on them."""
    verts = [(v["x"], v["y"], v.get("z", 0)) for v in design["verts"]]
    edges = [(e[0], e[1]) for e in design["edges"]]
    return verts, edges


def design_digest(design):
    """The URDROBJ2 identity of a design dict — provenance-independent by construction."""
    verts, edges = _geometry(design)
    return canon(verts, edges)


def design_digest_defect_with_provenance(design):
    """THE DEFECT (gate non-vacuity): a canon that folds provenance INTO the digest.
    Must diverge from the geometry-only golden — proving provenance-independence is a
    real, checked property and not an accident of the fixtures."""
    verts, edges = _geometry(design)
    base = canon(verts, edges)
    prov = repr(sorted((design.get("provenance") or {}).items()))
    return hashlib.sha256((base + "|" + prov).encode("utf-8")).hexdigest()


# ---- the admission obligations -------------------------------------------------------
def check_design(design):
    """Validate a design against the D14 obligations. Returns "ADMIT" or raises
    ContractError(CONTRACT-REFUSE). Checks: well-formed geometry, INTEGER-only
    coordinates, edge indices in range. Provenance is optional and unconstrained."""
    if not isinstance(design, dict) or "verts" not in design or "edges" not in design:
        raise ContractError("CONTRACT-REFUSE", "design missing verts/edges")
    verts = design["verts"]
    if len(verts) < 2:
        raise ContractError("CONTRACT-REFUSE", "a design needs at least two vertices")
    for i, v in enumerate(verts):
        for k in ("x", "y"):
            if k not in v or not _is_int(v[k]):
                raise ContractError("CONTRACT-REFUSE",
                                    f"vertex {i} coordinate {k}={v.get(k)!r} is not an integer "
                                    f"(authoring snaps; the runtime never rounds)")
        if "z" in v and not _is_int(v["z"]):
            raise ContractError("CONTRACT-REFUSE", f"vertex {i} z={v['z']!r} is not an integer")
    n = len(verts)
    for e in design["edges"]:
        if not (0 <= e[0] < n and 0 <= e[1] < n):
            raise ContractError("CONTRACT-REFUSE", f"edge {e} references a missing vertex")
    return "ADMIT"


if __name__ == "__main__":
    # self-demo: the reference square canon
    sq = [(0, 0), (40, 0), (40, 24), (0, 24)]
    loop = [(i, (i + 1) % 4) for i in range(4)]
    print("URDROBJ2 square canon:", canon(sq, loop))
