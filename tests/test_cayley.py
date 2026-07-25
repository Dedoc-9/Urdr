# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/cayley.py — THE CAYLEY-MENGER REALIZABILITY LAW (URDRCAY1).

  THE IDENTITIES — Heron (-det == 16*area^2) and the simplex volume (det == 288*V^2), each against an
    independently computed quantity, not against themselves.
  REALIZABILITY — any 5 points in R^3 give a vanishing determinant: a coordinate-free tautology.
  THE FORGERY BITES — one fabricated distance makes the set impossible; the credulous plant admits it.
  TWO INDEPENDENT ALGORITHMS — Bareiss (divides exactly) and Leibniz (never divides) must agree.
  DEGENERACY — coplanar and collinear detection from the same determinant at different sizes.

Every test can go red (L5); the plant bites before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import cayley as CY                                              # noqa: E402


class TheIdentities(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in CY.SCENES:
            self.assertEqual(CY.scene_result(name), CY.golden(name), name)
            self.assertEqual(CY.scene_result(name), CY.scene_result(name), name)

    def test_heron_against_independent_area(self):
        tri = CY.table([(0, 0, 0), (3, 0, 0), (0, 4, 0)])        # 3-4-5, area 6
        self.assertEqual(CY.area_sq_16(tri), 16 * 6 * 6)

    def test_simplex_against_independent_volume(self):
        tet = CY.table([(0, 0, 0), (6, 0, 0), (0, 6, 0), (0, 0, 6)])
        self.assertEqual(CY.volume_sq_288(tet), 288 * 36 * 36)   # V = 36

    def test_degeneracy(self):
        self.assertTrue(CY.is_collinear(CY.table([(0, 0, 0), (2, 0, 0), (5, 0, 0)])))
        self.assertFalse(CY.is_collinear(CY.table([(0, 0, 0), (2, 1, 0), (5, 0, 0)])))
        self.assertTrue(CY.is_coplanar(CY.table([(0, 0, 0), (4, 0, 0), (0, 7, 0), (4, 7, 0)])))
        self.assertFalse(CY.is_coplanar(CY.table([(0, 0, 0), (4, 0, 0), (0, 7, 0), (1, 1, 9)])))


class TheRealizabilityLaw(unittest.TestCase):
    def test_five_points_in_3space_vanish(self):
        five = CY.table(CY.RING_CHAIR[:5])
        self.assertEqual(CY.realizability_residue(five), 0)
        self.assertTrue(CY.realizable_3d(five))

    def test_forged_distance_is_refused_and_the_plant_admits_it(self):
        five = CY.table(CY.RING_CHAIR[:5])
        bad = CY.forge_distance(five, 0, 4, 1)
        self.assertFalse(CY.realizable_3d(bad), "an impossible distance set was admitted")
        self.assertNotEqual(CY.realizability_residue(bad), 0)
        self.assertTrue(CY._realizable_blind(bad), "the credulous plant must admit what the law refuses")

    def test_law_refuses_wrong_point_counts(self):
        with self.assertRaises(CY.CayleyError):
            CY.realizable_3d(CY.table(CY.RING_CHAIR[:4]))


class TheTwoAlgorithmsAgree(unittest.TestCase):
    def test_bareiss_equals_leibniz(self):
        """Independent oracles: one divides exactly, the other never divides."""
        for pts in ([(0, 0, 0), (3, 0, 0), (0, 4, 0)],
                    [(0, 0, 0), (6, 0, 0), (0, 6, 0), (0, 0, 6)],
                    CY.RING_CHAIR[:5]):
            sq = CY.table(pts)
            self.assertEqual(CY.cm_det(sq), CY.cm_det_leibniz(sq))

    def test_leibniz_is_division_free(self):
        import inspect
        src = inspect.getsource(CY.leibniz_det)
        body = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
        body = body.split('"""')[-1]                             # drop the docstring
        self.assertNotIn("//", body, "the Leibniz expansion must never divide")
        self.assertNotIn("/", body.replace("//", ""), "no division of any kind")

    def test_term_counts_measured(self):
        self.assertEqual(CY.leibniz_terms(4), 120)               # tetrahedron identity, S_5
        self.assertEqual(CY.leibniz_terms(5), 720)               # realizability identity, S_6


class TheChairRing(unittest.TestCase):
    def test_pucker_census_distinguishes_chair_from_planar(self):
        """MEASURED, not assumed: the chair gives exactly 3 coplanar four-subsets of 15 (the three
        opposite-atom selections, whose atom-pairs lie on parallel lines — an earlier draft picked
        one of those three and wrongly read it as a bug), with all 12 others sharing one volume. The
        flattened ring gives 15 of 15. The conformation is legible from distances alone."""
        n_chair, vols_chair = CY.ring_pucker_census(CY.RING_CHAIR)
        n_planar, vols_planar = CY.ring_pucker_census(CY.RING_PLANAR)
        self.assertEqual(n_chair, 3, "the chair has exactly three coplanar four-subsets")
        self.assertEqual(len(vols_chair), 1, "the other twelve share one volume — the chair symmetry")
        self.assertEqual(n_planar, 15, "a flat ring is coplanar everywhere")
        self.assertEqual(vols_planar, [], "a flat ring has no non-zero volume")

    def test_the_three_coplanar_subsets_are_the_opposite_pairs(self):
        import itertools
        cop = [c for c in itertools.combinations(range(6), 4)
               if CY.volume_sq_288(CY.table([CY.RING_CHAIR[i] for i in c])) == 0]
        self.assertEqual(cop, [(0, 1, 3, 4), (0, 2, 3, 5), (1, 2, 4, 5)])


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = CY.sweep_digest()
        self.assertEqual(d1, CY.sweep_digest(), "deterministic")
        self.assertEqual(d1, CY.sweep_golden(), "sweep drifted from golden")
        rep = CY.sweep()
        self.assertGreater(rep["honest"], 0)
        self.assertGreater(rep["forged"], 0)


if __name__ == "__main__":
    unittest.main()
