# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""wardhom — the warden's beta0 IS the certified F2-homology beta0, cross-placed (T3.27, MMO Stage E,
URDRWARDH1): the topological anti-cheat's component count, computed directly by union-find in `warden`, is the
SAME invariant URDRPD1 certifies as rank H0 over F2 — and this slice wires the two together and CROSS-PLACES
the walkable-graph homology in Python + C99 + Rust.

THE BRIDGE. The warden's walkable field is a GRAPH: a vertex per cell, an undirected edge between adjacent
cells when the step is legal both ways (|delta ground| <= MAX_STEP). Read as a 1-dimensional simplicial
complex (0-simplices = cells, 1-simplices = legal-step edges), its homology is elementary and exact:
  * beta0 = n0 - rank(d1) = the number of connected components — EXACTLY warden.betti0, but obtained by F2
    boundary-matrix rank instead of union-find;
  * beta1 = n1 - rank(d1) = the number of independent cycles (loops) in the walkable space.

THE KEYSTONE (measured). TWO independent methods agree: warden.betti0 (union-find) == URDRPD1 F2-rank beta0,
on every pinned world. And the F2-rank computation is CROSS-PLACED: `wardhom_c/` (C99) and `wardhom_rs/`
(Rust) build the same walkable complex from the same field and reproduce the URDRWARDH1 digest
(MAGIC | name | n0 | n1 | rank | beta0 | beta1) BIT-FOR-BIT. So the anti-cheat's topological certificate is no
longer only a direct union-find count — it is the rank of a boundary operator over F2, reproduced across
three languages, which is the invariant the URDRPD1 detector already certifies.

NON-VACUITY. The pinned worlds have genuinely different topology the digest must separate: `barrier8` (a wall
column) has beta0 = 3; `cliff8` (a one-way-height boundary, but |delta| > MAX_STEP so undirected-disconnected)
has beta0 = 2; `flat8` has beta0 = 1 and the most cycles. A `--defect` that drops the rank subtraction (the
URDRPD1 defect mode) inflates beta0 and moves the digest.

GRADE. The union-find-vs-F2-rank agreement, the beta0/beta1 counts, and the THREE-PLACEMENT digest parity
(Python == C99 == Rust, verified in-session on rustc 1.95.0 / gcc 13.3) are MEASURED (exact, reproducible, a
defect diverges). `does_not_show`: beta2 and higher (the walkable graph is 1-dimensional by construction);
PERSISTENCE (this is the static complex's homology, not a filtration); torsion (F2 ranks only, as URDRPD1);
weighting the edges (a single MAX_STEP); and any WALL-CLOCK cost (NOT_MEASURED until a sealed bench, Stage H).
The homology here is the walkable graph's, not a Vietoris-Rips point cloud's — but it uses URDRPD1's exact F2
machinery verbatim, so the two agree by construction where they overlap (beta0)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRWARDH1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
_HOM = _os.path.join(_os.path.dirname(_HERE), "homology")
if _HOM not in _sys.path:
    _sys.path.insert(0, _HOM)
import warden as _W                                              # union-find beta0 (the direct method)
import urdr_homology as _H                                       # URDRPD1 F2-rank betti (the certified method)


def walkable_complex(field, max_step):
    """The warden's walkable graph as a 1-complex: a 0-simplex (v,) per cell, a 1-simplex (u, v) per adjacent
    pair with |delta ground| <= max_step (the warden's UNDIRECTED step criterion). Vertex id = y*w + x."""
    w = len(field[0])
    h = len(field)
    simplices = set()
    for y in range(h):
        for x in range(w):
            simplices.add((y * w + x,))
    for y in range(h):
        for x in range(w):
            v = y * w + x
            if x + 1 < w and abs(field[y][x + 1] - field[y][x]) <= max_step:
                simplices.add((v, y * w + x + 1))
            if y + 1 < h and abs(field[y + 1][x] - field[y][x]) <= max_step:
                simplices.add((v, (y + 1) * w + x))
    return simplices


def counts(field, max_step):
    """(n0, n1, rank_d1, beta0, beta1): n0 vertices, n1 edges, rank of the F2 boundary d1; beta0 = n0 - rank,
    beta1 = n1 - rank. The full homology summary the C99/Rust placements reproduce."""
    cx = walkable_complex(field, max_step)
    dims = _H.by_dimension(cx)
    n0 = len(dims.get(0, []))
    n1 = len(dims.get(1, []))
    rank = _H.rank_f2(_H.boundary_columns(dims, 1))
    return n0, n1, rank, n0 - rank, n1 - rank


def homology_betti0(field, max_step):
    """beta0 of the walkable graph via URDRPD1's F2-rank betti (the certified, three-placed method)."""
    return _H.betti(walkable_complex(field, max_step), maxdim=1)[0]


def agree(field, max_step):
    """THE KEYSTONE: warden.betti0 (union-find) == URDRPD1 F2-rank beta0. Two independent methods, one
    invariant."""
    return _W.betti0(field, max_step) == homology_betti0(field, max_step)


def wardhom_digest(name, field, max_step):
    """URDRWARDH1 = SHA-256(MAGIC | name | '|' | n0 | n1 | rank | beta0 | beta1), each count 4-byte big-endian.
    The digest the C99 and Rust placements reproduce bit-for-bit."""
    n0, n1, rank, b0, b1 = counts(field, max_step)
    out = bytearray(MAGIC) + name.encode() + b"|"
    for v in (n0, n1, rank, b0, b1):
        out += v.to_bytes(4, "big")
    return hashlib.sha256(bytes(out)).hexdigest()


# ---- pinned worlds (8x8, so <= 64 vertices and the F2 columns fit a single uint64 in C99 / Rust) ----------
_MS = 40


def _barrier8():
    """A wall column at x=4 (height 200) splits an 8x8 flat world -> beta0 = 3 (west / wall / east)."""
    return tuple(tuple(200 if x == 4 else 0 for x in range(8)) for _y in range(8))


def _cliff8():
    """West half (x<4) at height 100, east at 0: |delta| = 100 > MAX_STEP at the boundary -> beta0 = 2."""
    return tuple(tuple(100 if x < 4 else 0 for x in range(8)) for _y in range(8))


def _flat8():
    """A flat 8x8 world -> beta0 = 1, the most cycles (a full grid graph)."""
    return tuple(tuple(0 for _x in range(8)) for _y in range(8))


SCENES = {"barrier8": _barrier8, "cliff8": _cliff8, "flat8": _flat8}


def scene_result(name):
    """Run a named world -> its URDRWARDH1 digest (the value the three placements must agree on)."""
    return wardhom_digest(name, SCENES[name](), _MS)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_wardhom.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise _W.WardError("WARD-MALFORMED", f"no golden named {name!r}")
