# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/cohort.py — THE COHORT FETCH PROTOCOL, GAP DERIVED (URDRCOH1).

  THE TIER IS THE FETCH PLAN, read from inputset rather than retyped, and the plans are NESTED.
  THE GAP IS MENGER'S MIN-CUT, NOT A TUNED CONSTANT — a 1-thick spanning wall has k=1 and a 2-thick
    wall has k=2, so THICK = 2 is min-cut(wall) computed from the wall's own geometry.
  SUB-GAP DISAGREEMENT IS IMPOSSIBLE, NOT MERELY TOLERATED — below k the theorem FORBIDS the
    verdicts differing, so a peer that disagrees there is provably faulty. At k it becomes possible.
  FOUR MEASURANDS DIED BY MEASUREMENT — Jaccard is blind to structure, run length is INVERTED, the
    boundary reduction does not exist, and the Hex Z2 duality is two-dimensional.
  FIRST-AGREEMENT IS CHERRY-PICKING — it verifies a cohort of one; the threshold rule refuses.
  THE CENTRALITY DIVIDEND IS THE REFUND PUMP. The graph is a real observable, wired to nothing.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import inspect
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import cohort as CO                                                 # noqa: E402


class TheTierIsTheFetchPlan(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in CO.SCENES:
            self.assertEqual(CO.scene_result(n), CO.golden(n), n)
            self.assertEqual(CO.scene_result(n), CO.scene_result(n), n)
        self.assertTrue(CO.emitted_matches_pinned())

    def test_the_plan_is_read_from_the_classifier(self):
        self.assertEqual(CO.plan_matches_the_classifier(), (
            ("exclusion_membership", "CERT", 0),
            ("prefix_disjointness", "CERT", 0),
            ("liveness_horizon", "CERT", 0),
            ("occupancy_defect", "LATTICE", 1),
            ("ledger_remainder", "HISTORY", 2),
            ("quorum_agreement", "COHORT", 3),
        ))

    def test_the_plans_are_nested(self):
        """Which is what makes 'a progressively richer fetch' meaningful."""
        self.assertTrue(CO.plans_are_nested())

    def test_the_threshold_is_geoquorums(self):
        same, n = CO.threshold_is_geoquorums()
        self.assertTrue(same, "MIN_PEERS is inherited, not re-chosen")
        self.assertEqual(n, 5)

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(CO.CohortError):
            CO.golden("no_such_scene")


class TheGapIsDerivedNotTuned(unittest.TestCase):
    def test_the_min_cut_equals_the_wall_thickness(self):
        """The load-bearing result: THICK = 2 was never a tuned constant."""
        self.assertEqual(CO.gap_table(),
                         ((3, 1, 1), (4, 1, 1), (4, 2, 2), (5, 1, 1), (5, 2, 2)))
        self.assertTrue(CO.the_gap_is_the_thickness())

    def test_the_wall_actually_spans_the_cross_section(self):
        """L19 — a first draft's 'wall' did not span, so free space walked around it and every min-cut
        came back 1. The number was measuring a wall that never blocked anything."""
        n, thick = 4, 2
        wall = CO.spanning_wall(n, thick)
        self.assertEqual(len(wall), thick * n * n)
        cross = {(y, z) for _x, y, z in wall}
        self.assertEqual(len(cross), n * n, "every cell of the cross-section is walled")
        self.assertEqual(CO.verdict(wall, n), CO.INTACT, "and it actually blocks")

    def test_a_breached_wall_has_min_cut_zero(self):
        """Validity-not-outcome: k is 0 exactly when the wall is already open."""
        self.assertEqual(CO.min_cut(frozenset(), 4), 0)
        self.assertEqual(CO.verdict(frozenset(), 4), CO.BREACHED)

    def test_the_screening_law_is_a_theorem(self):
        k, tried, flips = CO.screening_law_census()
        self.assertEqual((k, tried, flips), (2, 32, 0))
        self.assertGreater(tried, 0, "an empty census would pass vacuously")
        self.assertEqual(flips, 0, "below k the verdict cannot move")
        self.assertTrue(CO.screening_law_holds())

    def test_a_thickness_that_does_not_fit_refuses(self):
        for bad in (0, -1, 4, 9):
            with self.assertRaises(CO.CohortError):
                CO.spanning_wall(4, bad)


class SubGapDisagreementIsImpossible(unittest.TestCase):
    def test_below_the_gap_the_theorem_forbids_disagreement(self):
        """Not a tolerance — an impossibility check. A peer that disagrees here is provably faulty."""
        k, peers, impossible = CO.sub_gap_disagreement_is_impossible()
        self.assertEqual((k, peers, impossible), (2, 32, 0))
        self.assertGreater(peers, 0, "the check must range over something")
        self.assertEqual(impossible, 0)

    def test_at_the_gap_disagreement_becomes_reachable(self):
        """The bound is TIGHT — otherwise the impossibility above would be a statement about an
        unreachable regime rather than about the gap."""
        k, peers, disagree = CO.at_or_above_the_gap_disagreement_becomes_possible()
        self.assertEqual((k, peers, disagree), (2, 496, 16))
        self.assertGreater(disagree, 0, "at k the verdict CAN flip")

    def test_agreement_is_verdict_equality_not_overlap(self):
        """No rational bar, no distance, no float — the same structural bit."""
        wall = CO.spanning_wall(4, 2)
        cs = sorted(wall)
        self.assertTrue(CO.peers_agree(wall, wall - {cs[0]}, 4), "a sub-gap peer agrees")
        self.assertFalse(CO.peers_agree(wall, frozenset(), 4), "an empty report does not")
        src = inspect.getsource(CO.peers_agree)
        self.assertNotIn("/", src, "no division enters the predicate")


class TheRefutedMeasurands(unittest.TestCase):
    def test_jaccard_is_blind_to_structure(self):
        """(1) L21 reproduced one layer up, in this module's own first draft. The predicate that
        shipped in the previous rung is superseded, not merely suspect."""
        scat, cont, same_size, same_jac = CO.jaccard_is_blind_to_structure()
        self.assertEqual((scat, cont), (1, 4), "scattered and contiguous divergence differ in run")
        self.assertTrue(same_size, "and by the same cell count")
        self.assertTrue(same_jac, "so the Jaccard verdict is identical — it cannot see the difference")
        self.assertNotEqual(scat, cont)

    def test_run_length_is_inverted(self):
        """(2) Wrong in the DANGEROUS direction: it over-flags the non-breaching case."""
        d_run, d_breached, b_run, b_breached = CO.run_length_is_inverted()
        self.assertEqual((d_run, d_breached), (49, False), "a whole face removed, still no passage")
        self.assertEqual((b_run, b_breached), (3, True), "an actual breach of three cells")
        self.assertGreater(d_run, b_run, "the run metric ranks them backwards")

    def test_the_boundary_reduction_does_not_exist(self):
        """(3) No tier between CERT and LATTICE. Breach is interior reachability, and no surface sum
        determines it — which is why inputset's four tiers stand."""
        identical, va, vb = CO.boundary_does_not_determine_breach()
        self.assertTrue(identical, "byte-identical boundary occupancy")
        self.assertNotEqual(va, vb, "and opposite breach verdicts")
        self.assertEqual((va, vb), (CO.BREACHED, CO.INTACT))

    def test_the_hex_duality_is_two_dimensional(self):
        """(4) A free tube through a solid slab connects free space along x AND the occupied set along
        z, simultaneously. So there is no two-valued order parameter of that kind here."""
        fx, oz, both = CO.hex_duality_fails_in_3d()
        self.assertTrue(fx, "free space crosses along x")
        self.assertTrue(oz, "the occupied set crosses along z")
        self.assertTrue(both, "both at once — the 2D exclusivity fails")


class PolicyIsDeclaredNotDerived(unittest.TestCase):
    def test_thin_walls_are_refused_rather_than_caveated(self):
        thin, thick = CO.thin_walls_are_refused()
        self.assertTrue(thin, "a wall one cell can open cannot be signed at all")
        self.assertTrue(thick)
        with self.assertRaises(CO.TooThin):
            CO.certifiable(CO.spanning_wall(4, 1), 4)

    def test_too_thin_is_a_distinct_code_from_refuse(self):
        """tilemin's lesson: merging an honest-but-fragile verdict with a malformed-input refusal
        destroys attribution."""
        self.assertNotEqual(CO.TooThin("x").code, CO.CohortError("x").code)
        self.assertEqual(CO.TooThin("x").code, "COHORT-TOOTHIN")
        self.assertFalse(issubclass(CO.TooThin, CO.CohortError))

    def test_the_charge_is_monotone_and_the_peak_is_not_adopted(self):
        self.assertEqual(CO.charge_table(),
                         ((0, 12), (1, 12), (2, 6), (3, 4), (4, 3), (6, 2), (12, 1)))
        self.assertTrue(CO.charge_is_monotone_non_increasing())
        c1, c0, peaked = CO.the_peak_is_not_adopted()
        self.assertEqual((c1, c0), (12, 12))
        self.assertFalse(peaked, "monotone is the conservative default; the peak was NOT measured")

    def test_the_charge_is_integer_only(self):
        for bad in (-1, "2", 2.0, True):
            with self.assertRaises(CO.CohortError):
                CO.charge_for_gap(bad)
        self.assertEqual(CO.charge_for_gap(None), 0, "an undecided cut charges nothing")

    def test_the_floor_is_stated_as_policy(self):
        self.assertEqual(CO.WALL_MIN_K, 2)
        self.assertEqual(CO.BASE_CHARGE, 12)


class ThresholdNotFirstAgreement(unittest.TestCase):
    def test_first_agreement_verifies_a_cohort_of_one(self):
        fo, fc, to, ta = CO.first_agreement_is_cherry_picking()
        self.assertEqual(fo, CO.VERIFIED, "the proposed loop is satisfied by one peer")
        self.assertEqual(fc, 1)
        self.assertEqual(to, CO.UNAVAILABLE, "and the threshold rule refuses it")
        self.assertEqual(ta, 1)
        self.assertNotEqual(fo, to)

    def test_the_loop_terminates_within_budget(self):
        fetched, budget, bounded = CO.loop_terminates()
        self.assertTrue(bounded, "the ledger bounds the fetch count")
        self.assertEqual((fetched, budget), (6, 6))

    def test_a_threshold_below_one_refuses(self):
        with self.assertRaises(CO.CohortError):
            CO.verify_cohort(CO.submitter(), CO.peer_population(), 20, min_peers=0)

    def test_no_peer_is_a_set_duplicate_of_another(self):
        """A reordering is the SAME frozenset — a duplicate masquerading as an observer."""
        occs = [p["occupancy"] for p in CO.peer_population()]
        self.assertEqual(len(occs), len(set(occs)), "every peer must be a distinct observation")

    def test_the_honest_peers_are_sub_gap_and_the_liar_is_not(self):
        """Validity-not-outcome: the population must actually exercise both arms."""
        mine, n = CO.submitter(), 4
        k = CO.min_cut(mine, n)
        honest = [p for p in CO.peer_population() if CO.peers_agree(mine, p["occupancy"], n)]
        self.assertEqual(len(honest), 5)
        for p in honest:
            self.assertLess(len(mine ^ p["occupancy"]), k,
                            "every honest peer is STRICTLY sub-gap, so Menger forbids disagreement")
        liar = CO.peer_population()[5]
        self.assertFalse(CO.peers_agree(mine, liar["occupancy"], n))


class TheGradedOutcomes(unittest.TestCase):
    def test_all_three_are_reachable(self):
        self.assertTrue(CO.all_three_outcomes_are_reachable())
        rows = {r[0]: r[1] for r in CO.outcome_census()}
        self.assertEqual(rows["full population"], CO.VERIFIED)
        self.assertEqual(rows["no peers"], CO.UNAVAILABLE)
        self.assertEqual(rows["all disagree"], CO.FAILED)

    def test_unavailable_is_not_failure(self):
        """geoquorum's THIN-versus-DEVIATE at this layer: coverage is not integrity."""
        no_peer, disagree, distinct = CO.unavailable_is_not_failure()
        self.assertEqual(no_peer, CO.UNAVAILABLE)
        self.assertEqual(disagree, CO.FAILED)
        self.assertTrue(distinct)


class TheCentralityDividendIsRefused(unittest.TestCase):
    def test_the_pump_across_alpha(self):
        rows = CO.centrality_dividend_pump()
        self.assertEqual(rows, ((0, -34, False), (1, 6, False), (2, 46, True), (3, 86, True)))
        for alpha, _remaining, grew in rows:
            if alpha >= CO.EDGE_COST + 1:
                self.assertTrue(grew, "at alpha above the edge cost the budget grows unbounded")

    def test_there_is_no_safe_and_useful_alpha(self):
        pumping, draining, both = CO.dividend_has_no_safe_useful_setting()
        self.assertEqual(pumping, (2, 3))
        self.assertEqual(draining, (0, 1))
        self.assertEqual(both, (), "no setting both rewards participation and preserves the bound")

    def test_the_graph_is_structurally_unwired(self):
        """Not a promise — a signature check. No admission path takes centrality."""
        charge_params, verify_params, appears = CO.the_graph_is_unwired()
        self.assertFalse(appears, "centrality is measured and consulted by nothing")
        self.assertEqual(charge_params, ("remaining", "cost"))
        self.assertNotIn("centrality", verify_params)

    def test_the_graph_is_still_a_real_observable(self):
        """Validity-not-outcome: an unwired measurement must still be a measurement."""
        edges = CO.edge_log()
        self.assertEqual(len(edges), 15)
        self.assertEqual(edges, tuple(sorted(edges)), "deterministic order")
        self.assertGreater(CO.centrality(1), 0)


if __name__ == "__main__":
    unittest.main()
