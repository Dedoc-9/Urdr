# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""toric — the toric-code / surface-code detector: 𝔽₂ homology of a cellulated surface.

The first NEW detector admitted under D17 (spec/D17-invariant-detectors.md), chosen because it
pressures the admission law in three fresh directions at once: an ALGEBRAIC invariant (a homology
dimension, not a geometric one), a NEW EXACT SUBSTRATE (𝔽₂ via `gf2`, not ℤ / Q32.32), and a
MULTI-PART TOPOLOGICAL WITNESS (boundary matrices → ranks → the H₁ dimension). D17 admitted it
UNCHANGED — the six conditions held with no flex.

The mathematics: a closed surface is a chain complex `C₂ →∂₂ C₁ →∂₁ C₀` over 𝔽₂ (faces → edges →
vertices), and `∂₁∂₂ = 0`. Kitaev's toric/surface code on this cellulation has
  * n = |E| physical qubits (one per edge),
  * k = dim H₁ = |E| − rank ∂₁ − rank ∂₂ logical qubits (= 2·genus for an orientable surface),
  * distance d = the shortest non-contractible cycle (a systole).
The logical information lives in H₁ — homology classes of cycles — which is exactly why it is
protected: a local (contractible) error is a boundary and acts trivially on the code. `k` is a
TOPOLOGICAL INVARIANT: it depends only on the surface's genus, not on how finely it is cellulated.

Honest scope: `k` (the code dimension) is always exact and cheap. The DISTANCE is exact only for
structured families (the L×L torus has distance L); the general minimum-distance problem is the
minimum-weight-codeword problem, which is NP-hard — so distance is offered only for the toric
family and REFUSEd otherwise, a clean D17 domain boundary. GRADE (D5): MEASURED (reference);
cross-placement DECLARED; the invariant is exact over 𝔽₂ (no rounding, no bound)."""
import hashlib
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gf2                                                   # noqa: E402  exact 𝔽₂ linear algebra

MAGIC = b"URDRTOR1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class ToricError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


# ---- surfaces as 𝔽₂ chain complexes -------------------------------------------------
def torus(L):
    """The L×L square torus: V=L², E=2L² (one edge per horizontal + vertical link), F=L²
    (one square face each). Returns a complex dict with 𝔽₂ boundary maps d1 (V×E) and d2 (F×E)."""
    def vid(r, c):
        return (r % L) * L + (c % L)
    edges, eidx = [], {}
    for r in range(L):
        for c in range(L):
            eidx[("H", r, c)] = len(edges); edges.append((vid(r, c), vid(r, c + 1)))
            eidx[("V", r, c)] = len(edges); edges.append((vid(r, c), vid(r + 1, c)))
    V, E = L * L, len(edges)
    d1 = [[0] * E for _ in range(V)]
    for j, (a, b) in enumerate(edges):
        d1[a][j] ^= 1; d1[b][j] ^= 1
    faces = [[eidx[("H", r, c)], eidx[("V", r, (c + 1) % L)],
              eidx[("H", (r + 1) % L, c)], eidx[("V", r, c)]]
             for r in range(L) for c in range(L)]
    d2 = [[0] * E for _ in range(len(faces))]
    for i, fe in enumerate(faces):
        for e in fe:
            d2[i][e] ^= 1
    return {"V": V, "E": E, "F": len(faces), "d1": d1, "d2": d2, "family": ("torus", L)}


def sphere():
    """A sphere as the octahedron (V=6, E=12, F=8, χ=2) — genus 0, so k = dim H₁ = 0."""
    edges = [(0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5),
             (2, 4), (4, 3), (3, 5), (5, 2)]
    eidx = {e: i for i, e in enumerate(edges)}

    def eid(a, b):
        return eidx[(a, b)] if (a, b) in eidx else eidx[(b, a)]
    faces = [(0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2),
             (1, 2, 4), (1, 4, 3), (1, 3, 5), (1, 5, 2)]
    V, E = 6, 12
    d1 = [[0] * E for _ in range(V)]
    for j, (a, b) in enumerate(edges):
        d1[a][j] ^= 1; d1[b][j] ^= 1
    d2 = [[0] * E for _ in range(len(faces))]
    for i, (a, b, c) in enumerate(faces):
        for (x, y) in ((a, b), (b, c), (a, c)):
            d2[i][eid(x, y)] ^= 1
    return {"V": V, "E": E, "F": len(faces), "d1": d1, "d2": d2, "family": ("sphere", 0)}


# ---- the detector (Dom, Inv, W, R) --------------------------------------------------
def is_complex(cx):
    """Membership in Dom: `∂₁∂₂ = 0` over 𝔽₂ (every face boundary is a cycle). Decidable."""
    V, E = cx["V"], cx["E"]
    d1, d2 = cx["d1"], cx["d2"]
    for i in range(cx["F"]):
        acc = [0] * V
        for j in range(E):
            if d2[i][j]:
                for v in range(V):
                    acc[v] ^= d1[v][j]
        if any(acc):
            return False
    return True


def code_dimension(cx):
    """The invariant `k = dim H₁ = E − rank ∂₁ − rank ∂₂` over 𝔽₂ (= logical qubits = 2·genus).
    Refuses `TORIC-REFUSE` if the input is not a chain complex (`∂₁∂₂ ≠ 0`)."""
    if not is_complex(cx):
        raise ToricError("TORIC-REFUSE", "∂₁∂₂ ≠ 0 (mod 2): not a chain complex")
    E = cx["E"]
    r1 = gf2.rank(cx["d1"], E)
    r2 = gf2.rank(cx["d2"], E)
    return E - r1 - r2


def distance(cx):
    """The code distance — exact ONLY for the toric family (an L×L torus has distance L). The
    general minimum-distance problem is NP-hard, so anything else is `TORIC-REFUSE` (a clean
    domain boundary, not an approximation)."""
    fam = cx.get("family", (None, None))
    if fam[0] == "torus":
        return fam[1]
    if fam[0] == "sphere":
        return 0                                            # no logical qubits ⇒ no distance
    raise ToricError("TORIC-REFUSE", "exact minimum distance is NP-hard off the toric family")


def boundary_digest(cx):
    """The witness digest: SHA-256 over the two 𝔽₂ boundary matrices (independently recomputable)."""
    h = hashlib.sha256(); h.update(MAGIC)
    for M in (cx["d1"], cx["d2"]):
        for row in M:
            h.update(bytes(row))
    return h.hexdigest()


def witness(cx):
    """The independently-checkable certificate: `n` physical qubits, `k` logical, distance `d`,
    the boundary ranks, and the boundary-matrix digest. Recomputing `k = E − r1 − r2` and checking
    `∂₁∂₂ = 0` reproduces the invariant from the matrices alone."""
    k = code_dimension(cx)
    E = cx["E"]
    return {"n": E, "k": k, "d": distance(cx),
            "rank_d1": gf2.rank(cx["d1"], E), "rank_d2": gf2.rank(cx["d2"], E),
            "euler": cx["V"] - cx["E"] + cx["F"], "digest": boundary_digest(cx)}


def code_dimension_defect(cx):
    """THE DEFECT (D17 non-invariance): forgets to subtract rank ∂₂, so it reports dim ker ∂₁
    instead of dim H₁ — a plausible wrong homology that must misclassify the code dimension."""
    if not is_complex(cx):
        raise ToricError("TORIC-REFUSE", "∂₁∂₂ ≠ 0")
    return cx["E"] - gf2.rank(cx["d1"], cx["E"])            # = dim ker ∂₁, NOT dim H₁


def golden(name):
    path = _os.path.join(_HERE, "conformance_toric.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ToricError("TORIC-REFUSE", f"no golden named {name!r}")
