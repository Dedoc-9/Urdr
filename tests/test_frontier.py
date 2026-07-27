# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/frontier.py — THE ADMISSION ACCELERATOR (URDRFRN1).

  CROSS-COMPONENT COMMUTATION — decided against the SEMANTICS, not against the predicate that built
    the graph, so the theorem cannot be true by construction.
  NON-TRANSITIVITY — witnessed, not warned about. The greedy plant's minimal bite is THREE edits.
  THE VACUITY GUARD — on 60 edits every greedy batch is a singleton and the plant scores 0. A
    batching census over a corpus that never batches proves nothing. SECOND occurrence in the arc.
  CONSERVATION AND MONOTONICITY — nothing dropped; refining only moves obligations to proved.
  THE YIELD CURVE — 27% is an artifact of density, not a constant.

Every test can go red (L5); the greedy plant bites before any golden pins (L15)."""
import os
import sys
import unittest
from itertools import combinations

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import frontier as FR                                              # noqa: E402
import disjoint as DJ                                              # noqa: E402


class TheTheorem(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in FR.SCENES:
            self.assertEqual(FR.scene_result(n), FR.golden(n), n)
            self.assertEqual(FR.scene_result(n), FR.scene_result(n), n)

    def test_cross_component_pairs_commute(self):
        """Checked against the commutation SEMANTICS, not against prefix_disjoint — otherwise the
        theorem would be true by construction and prove nothing."""
        self.assertTrue(FR.cross_component_commutes())
        self.assertTrue(FR.components_are_sound())

    def test_components_partition_the_family(self):
        fam = DJ.edit_family()[:60]
        comps = FR.components(fam)
        self.assertEqual(sorted(i for c in comps for i in c), list(range(len(fam))))
        self.assertEqual(sum(len(c) for c in comps), len(fam), "components must not overlap")


class TheHazard(unittest.TestCase):
    def test_disjointness_is_not_transitive(self):
        ab, bc, ac = FR.non_transitivity_witness()
        self.assertTrue(ab)
        self.assertTrue(bc)
        self.assertFalse(ac, "A||B and B||C must NOT give A||C")

    def test_the_greedy_plant_builds_unsound_batches(self):
        """L15 — the plant produces batches that are not independent sets."""
        self.assertGreater(FR.greedy_batching_is_unsound(), 0)

    def test_the_minimal_bite_is_three_edits(self):
        hx, hy, xy, bad = FR.minimal_unsound_witness()
        self.assertTrue(hx)
        self.assertTrue(hy)
        self.assertFalse(xy, "the two admitted members conflict with each other")
        self.assertEqual(bad, 1, "and the batch containing all three is not independent")


class TheVacuityGuard(unittest.TestCase):
    """Second occurrence in the arc, so it is a standing guard rather than a fixed bug."""

    def test_a_corpus_that_never_batches_proves_nothing(self):
        self.assertTrue(FR.the_small_slice_was_vacuous())
        sub = DJ.edit_family()[:60]
        self.assertEqual(max(len(b) for b in FR._batch_by_greedy_pairwise(sub)), 1)
        self.assertEqual(FR.greedy_batching_is_unsound(sub), 0,
                         "on this slice the unsound rule looks sound")

    def test_the_census_asserts_grouping_actually_happens(self):
        self.assertTrue(FR.greedy_census_is_not_vacuous())
        self.assertGreater(max(len(b) for b in FR._batch_by_greedy_pairwise(DJ.edit_family())), 1)


class TheObligationSignature(unittest.TestCase):
    def test_nothing_is_dropped(self):
        """The failure an accelerator invites: a fast path that silently discards what it cannot
        handle is indistinguishable from one that handles it."""
        self.assertTrue(FR.conservation_holds())
        p, o, t = FR.signature(DJ.edit_family())
        self.assertEqual(p + o, t)
        self.assertEqual((p, o, t), (18144, 47922, 66066))

    def test_refining_only_moves_obligations_to_proved(self):
        """'Uncertainty preserved or reduced, never silently grown' — decided, not intended."""
        self.assertTrue(FR.obligations_are_monotone())
        fam = DJ.edit_family()
        _p1, o1, _t1 = FR.signature(fam, 1)
        _p2, o2, _t2 = FR.signature(fam, 2)
        self.assertLessEqual(o2, o1, "a finer level must not create obligations")

    def test_every_pair_is_routed_somewhere(self):
        fam = DJ.edit_family()[:40]
        routes = [FR.route(a, b) for a, b in combinations(fam, 2)]
        self.assertEqual(len(routes), len(fam) * (len(fam) - 1) // 2)
        self.assertTrue(set(routes) <= {FR.ROUTE_PROVED, FR.ROUTE_FRONTIER})
        self.assertEqual(FR._ROUTE_NAME[FR.ROUTE_FRONTIER], "FRONTIER")


class TheYieldCurve(unittest.TestCase):
    def test_the_fast_path_fraction_is_not_a_constant(self):
        """27% is an artifact of one corpus's density. Quoting it as the accelerator's value would
        be the same inflation the arc keeps catching."""
        lo, hi, differ = FR.the_pinned_fraction_is_an_artifact()
        self.assertTrue(differ, "the fraction must move with density")
        self.assertNotEqual(lo, hi)

    def test_curve_shape_is_decided_in_exact_integers(self):
        """No floats, no regression — cross-multiplication only."""
        self.assertTrue(FR.yield_rises_with_spread())
        rows = FR.yield_curve()
        self.assertEqual(len(rows), len(FR.POOLS))
        for _pool, p, t in rows:
            self.assertLessEqual(p, t)
            self.assertGreater(t, 0)


if __name__ == "__main__":
    unittest.main()
