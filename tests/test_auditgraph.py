# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/auditgraph.py — THE EXCLUSION PRICE (URDRAUD1).

  THE PRICE IS KAPPA — the simulated attack (subset enumeration) and MENGER MAX-FLOW agree on all
    771 connected labelled graphs to order 5, 0 exceptions, sharing no primitive.
  AND THE CHECK CAN FAIL — corrupt components() and the Menger census goes red while the ORIGINAL
    cross-check does not. That original compared two functions that share components() and cannot
    disagree; it was a tautology sold as a measurement and it shipped three times. The numbers were
    always right — the reason to believe them was not.
  ALL-PAIRS IS THE ONLY UNBREAKABLE TOPOLOGY — and that reverses splitview's recommendation, whose
    "a spanning tree suffices" is true in a model where the server cannot exclude anyone.
  THE LADDER IS 1 / 2 / INFINITE — and it starts at FOUR clients, because on three the ring IS the
    complete graph and the law came back False.
  THE PLANTS FAIL OPTIMISTICALLY — lambda and delta over-price 15 times each and under-price 0,
    telling a deployment the server must work harder than it does.

Every test can go red (L5); the three plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import auditgraph as AG                                            # noqa: E402


class ThePriceIsVertexConnectivity(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in AG.SCENES:
            self.assertEqual(AG.scene_result(n), AG.golden(n), n)
            self.assertEqual(AG.scene_result(n), AG.scene_result(n), n)

    def test_simulated_attack_equals_menger_maxflow(self):
        """THE LOAD-BEARING CHECK: subset enumeration against flow augmentation, no shared
        primitive."""
        agree, exc, total = AG.menger_census()
        self.assertEqual(exc, 0, "the attack price diverged from Menger kappa")
        self.assertEqual((agree, total), (771, 771))
        self.assertTrue(AG.price_is_vertex_connectivity())

    def test_the_cross_check_can_actually_fail(self):
        """L15 APPLIED TO A CHECKER. Corrupt the primitive the attack depends on; the Menger census
        AND the family census must both react. Without this the agreements are unfalsifiable."""
        circular_exc, menger_exc, family_exc = AG.cross_check_is_falsifiable()
        self.assertGreater(menger_exc, 0, "a checker that cannot fail is not evidence")
        self.assertGreater(family_exc, 0, "and the DENOMINATOR needs its own live check")
        self.assertEqual(circular_exc, 0)
        self.assertTrue(AG.family_check_is_falsifiable())

    def test_the_denominator_is_cross_checked(self):
        """is_connected builds connected_graphs, which is the denominator of every census here.
        Flood fill against max-flow over every labelled graph, not just the connected ones."""
        agree, exc, total, conn = AG.family_census()
        self.assertEqual(exc, 0, "flood fill and max-flow disagreed about connectivity")
        self.assertEqual((agree, total, conn), (1099, 1099, 772))

    def test_malformed_graphs_refuse_instead_of_being_dropped(self):
        """HARDENING: an out-of-range endpoint used to be silently dropped and is_connected returned
        a plausible False — answering a question the caller never asked."""
        for k, e in ((3, ((0, 1), (1, 99))), (3, ((0, 1), (-5, 2))),
                     (2, ((0, 0),)), (3, ((0, 1, 2),)), (3, ((0, "x"),))):
            with self.assertRaises(AG.AuditGraphError, msg=f"{k} {e}"):
                AG.is_connected(k, e)
        with self.assertRaises(AG.AuditGraphError):
            AG.validate_graph(-1, ())

    def test_validation_admits_every_graph_the_censuses_use(self):
        """Validity-not-outcome: the guard must not be so strict it empties the family."""
        self.assertEqual(len(AG.connected_graphs(5)), 728)
        for k in range(3, 7):
            self.assertTrue(AG.validate_graph(k, AG.ring_graph(k)))
            self.assertTrue(AG.validate_graph(k, AG.path_graph(k)))
            self.assertTrue(AG.validate_graph(k, AG.complete_graph(k)))

    def test_the_original_cross_check_was_circular(self):
        """THE DEFECT, KEPT LIVE. exclusion_price and vertex_connectivity share components() and are
        separated only by a guard that cannot change the answer, so they can never disagree — the
        agreement was a tautology sold as a measurement, and it shipped three times."""
        self.assertTrue(AG.circular_check_cannot_fail())
        diff = [(k, e) for k in range(2, AG.MAX_ORDER + 1) for e in AG.connected_graphs(k)
                if AG.exclusion_price(k, e) != AG.vertex_connectivity(k, e)]
        self.assertEqual(diff, [], "they are structurally incapable of disagreeing")

    def test_menger_and_the_enumerated_kappa_still_agree(self):
        """The NUMBERS were never wrong — only the reason to believe them."""
        for k in range(2, AG.MAX_ORDER + 1):
            for e in AG.connected_graphs(k):
                self.assertEqual(AG.vertex_connectivity(k, e),
                                 AG.vertex_connectivity_menger(k, e), (k, e))

    def test_the_family_is_not_vacuous(self):
        """L19 — the census is free if every graph has the same price."""
        prices = {AG.exclusion_price(5, e) for e in AG.connected_graphs(5)}
        self.assertGreater(len(prices), 2, "the family must span several prices")
        self.assertIn(AG.INFINITE, prices)
        self.assertIn(1, prices)

    def test_a_survivor_set_of_one_is_not_a_win(self):
        """splitview's k=1 vacuity, inherited rather than re-earned: excluding everyone but one
        client leaves nothing to equivocate between."""
        self.assertFalse(AG.server_wins_after_excluding(3, AG.path_graph(3), (0, 1)))
        self.assertFalse(AG.server_wins_after_excluding(3, AG.path_graph(3), (0, 1, 2)))
        self.assertTrue(AG.server_wins_after_excluding(3, AG.path_graph(3), (1,)))

    def test_kappa_is_infinite_not_k_minus_one_on_a_complete_graph(self):
        """The textbook convention would inflate a guarantee into a price."""
        for k in range(2, 6):
            self.assertIs(AG.vertex_connectivity(k, AG.complete_graph(k)), AG.INFINITE)
            self.assertIs(AG.exclusion_price(k, AG.complete_graph(k)), AG.INFINITE)


class AllPairsIsTheOnlyUnbreakableTopology(unittest.TestCase):
    def test_unbreakable_set_is_exactly_the_complete_graphs(self):
        table = AG.unbreakable_are_exactly_complete()
        self.assertEqual(table, ((2, 1, True), (3, 1, True), (4, 1, True), (5, 1, True)))
        for _k, count, exact in table:
            self.assertEqual(count, 1, "exactly one unbreakable topology per order")
            self.assertTrue(exact, "and it is the complete graph")

    def test_the_spanning_tree_falls_to_one_exclusion(self):
        """THE CONCRETE WARNING against reading splitview alone."""
        table = AG.spanning_tree_falls_to_one_exclusion()
        self.assertEqual(table, ((4, 1), (5, 1), (6, 1), (7, 1), (8, 1)))
        self.assertTrue(all(p == 1 for _k, p in table))

    def test_the_ladder_is_one_two_infinite(self):
        self.assertTrue(AG.ladder_is_one_two_infinite())
        for k, p, r, c in AG.price_ladder():
            self.assertEqual((p, r), (1, 2), k)
            self.assertIs(c, AG.INFINITE, k)

    def test_the_ladder_starts_at_four_because_it_was_false_at_three(self):
        """L20 — a universal asserted from a mental sample of one, refused by enumeration."""
        same, ring_price, complete_price = AG.the_triangle_is_both()
        self.assertTrue(same, "on three clients the ring IS the complete graph")
        self.assertIs(ring_price, AG.INFINITE)
        self.assertEqual(ring_price, complete_price)
        self.assertEqual(AG.LADDER_MIN, 4)
        self.assertFalse(AG.ladder_is_one_two_infinite(min_k=3),
                         "and running it from three must still be False, or the lesson is gone")


class TheAssignmentLeverAndItsRemoval(unittest.TestCase):
    def test_a_server_that_picks_sessions_picks_the_partition(self):
        for k, expect in ((2, (1, 2)), (3, (4, 5)), (4, (14, 15)), (5, (51, 52))):
            self.assertEqual(AG.server_choice_census(k), expect, k)
        dis, total = AG.server_choice_census(5)
        self.assertEqual(dis, total - 1, "every partition but the single block disconnects")
        self.assertGreater(dis, 0)

    def test_commitment_collapses_it_to_zero(self):
        self.assertEqual(AG.committed_census(5), (0, 1))
        self.assertTrue(AG.commitment_removes_the_assignment_lever())

    def test_committing_to_the_server_assigned_index_is_not_commitment(self):
        """L15 — the plant that is hard to see: relabelling preserves connectivity, so the topology
        still looks safe, while the server chooses WHICH REAL CLIENT sits at each cut position."""
        connected, victims = AG.index_commitment_is_not_commitment()
        self.assertTrue(connected, "which is exactly why the defect is easy to miss")
        self.assertEqual(victims, 10, "it can select every one of the C(5,2) victim pairs")
        self.assertGreater(victims, 1)


class ThePlantsFailOptimistically(unittest.TestCase):
    def test_lambda_and_delta_overprice_and_never_underprice(self):
        lo, lu, do, du, total = AG.overprice_census()
        self.assertEqual((lo, lu, do, du, total), (15, 0, 15, 0, 767))
        self.assertEqual(lu, 0, "an under-price would be the safe direction; there are none")
        self.assertEqual(du, 0)
        self.assertGreater(lo, 0, "a plant that never over-prices has not been tested")
        self.assertTrue(AG.plants_only_fail_optimistically())

    def test_the_family_contains_kappa_below_lambda(self):
        """L19 — if kappa == lambda everywhere the plants could never bite."""
        self.assertEqual(AG.kappa_below_lambda_witness(), 15)
        self.assertGreater(AG.kappa_below_lambda_witness(), 0)

    def test_whitney_direction_holds_in_the_family(self):
        """kappa <= lambda <= delta, checked rather than cited."""
        for k in range(2, AG.MAX_ORDER + 1):
            for e in AG.connected_graphs(k):
                kap, lam, dee = (AG.vertex_connectivity(k, e), AG.edge_connectivity(k, e),
                                 AG.min_degree(k, e))
                if kap is AG.INFINITE or lam is AG.INFINITE:
                    continue
                self.assertLessEqual(kap, lam)
                self.assertLessEqual(lam, dee)


class TheRefusalIsTyped(unittest.TestCase):
    def test_a_cheap_topology_is_refused_not_warned(self):
        self.assertTrue(AG.refuses_a_spanning_tree())
        with self.assertRaises(AG.AuditGraphError):
            AG.require_price_at_least(6, AG.path_graph(6), 2)

    def test_a_ring_clears_a_floor_of_two(self):
        self.assertTrue(AG.admits_a_ring())

    def test_an_unbreakable_topology_always_clears(self):
        self.assertTrue(AG.require_price_at_least(5, AG.complete_graph(5), 99))

    def test_a_ring_below_three_refuses(self):
        for bad in (0, 1, 2):
            with self.assertRaises(AG.AuditGraphError):
                AG.ring_graph(bad)


if __name__ == "__main__":
    unittest.main()
