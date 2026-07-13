# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the toric-code detector (`tools/intla/toric.py`) — the first NEW detector
admitted under D17. It exercises the admission law in three fresh directions: an algebraic
invariant (𝔽₂ homology), a new exact substrate (GF(2)), and a multi-part topological witness.

Pinned laws (the four D17 roles + the substrate):
  * GF(2) — rank/nullity over 𝔽₂ are exact (rank–nullity holds);
  * REFERENCE — the 3×3 torus reproduces k = dim H₁ = 2 and the pinned boundary digest;
  * INVARIANCE — k tracks GENUS, not the mesh: torus (2×2, 3×3, 4×4) all give k=2, sphere gives
    k=0 (`k = 2·genus`);
  * DEFECT (non-invariance) — a wrong homology (dim ker ∂₁ instead of dim H₁) misclassifies k;
  * REFUSAL — a non-chain-complex (`∂₁∂₂ ≠ 0`) is `TORIC-REFUSE`d;
  * SCOPE — distance is exact for the toric family (L×L → L) and refuses off it (NP-hard)."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "intla")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import gf2                                                   # noqa: E402
import toric as T                                            # noqa: E402


def _golden(name):
    with open(os.path.join(_ROOT, "tools", "intla", "conformance_toric.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AssertionError(f"golden {name} missing")


class GF2(unittest.TestCase):
    def test_rank_nullity(self):
        M = [[1, 0, 1], [0, 1, 1], [1, 1, 0]]  # rows sum to 0 → rank 2, nullity 1
        self.assertEqual(gf2.rank(M, 3), 2)
        self.assertEqual(gf2.nullity(M, 3), 1)


class ToricDetector(unittest.TestCase):
    def test_reference_torus3_k2_and_digest(self):
        cx = T.torus(3)
        self.assertEqual(T.code_dimension(cx), 2, "3×3 torus is not 2 logical qubits")
        self.assertEqual(T.boundary_digest(cx), _golden("torus3"), "boundary digest drifted")

    def test_invariance_k_tracks_genus_not_mesh(self):
        # cellulation-independence: every torus mesh is k=2 (genus 1); the sphere is k=0 (genus 0)
        for L in (2, 3, 4):
            self.assertEqual(T.code_dimension(T.torus(L)), 2, f"{L}×{L} torus ≠ 2")
        self.assertEqual(T.code_dimension(T.sphere()), 0, "sphere ≠ 0")

    def test_defect_misclassifies(self):
        cx = T.torus(3)
        self.assertEqual(T.code_dimension(cx), 2)
        self.assertNotEqual(T.code_dimension_defect(cx), 2,
                            "the wrong homology (no rank ∂₂ subtraction) did not misclassify")

    def test_non_complex_refused(self):
        cx = T.torus(3)
        cx["d2"] = [row[:] for row in cx["d2"]]
        cx["d2"][0][0] ^= 1                                  # break ∂₁∂₂ = 0
        self.assertFalse(T.is_complex(cx))
        with self.assertRaises(T.ToricError):
            T.code_dimension(cx)

    def test_distance_scope(self):
        self.assertEqual(T.distance(T.torus(4)), 4, "toric distance ≠ L")
        # off the toric family, exact distance is NP-hard → REFUSE
        bad = {"family": ("wild", 0), "V": 1, "E": 1, "F": 0, "d1": [[0]], "d2": []}
        with self.assertRaises(T.ToricError):
            T.distance(bad)

    def test_deterministic(self):
        self.assertEqual(T.boundary_digest(T.torus(3)), T.boundary_digest(T.torus(3)))


if __name__ == "__main__":
    unittest.main()
