# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/blindscreen.py — CHEAPNESS IS NOT SOUNDNESS (URDRBLS1).

  EVERY CHEAP INVARIANT IS BLIND TO THE VERDICT — cell_count, boundary_occupancy, tile_prefix and
    occupancy_defect, 4 of 4 refuted by an equal-invariant / opposite-verdict pair.
  AND SO IS THEIR CONJUNCTION — one pair agrees on ALL FOUR at once and has opposite verdicts, two
    16-cell occupancies differing in 2 cells. Stacking cheap checks does not converge.
  CONNECTIVITY SEPARATES THAT SAME PAIR — the positive control, without which the corpus would be
    degenerate rather than the invariants blind.
  THE COST ORDER IS NOT THE DECISIVENESS ORDER — the four cheapest settle nothing and only the most
    expensive settles anything, so a cascade is sound only where the two orders coincide.
  A CELL-COUNT SCREEN CLEARS 8 OF 8 PEERS AND 3 OF THEM WRONGLY, with the population asserted to
    exercise both arms.
  THE ROUTER TAKES NO BLIND INVARIANT — a signature check, not a promise.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import blindscreen as BS                                            # noqa: E402
import cohort as CO                                                 # noqa: E402


class EveryCheapInvariantIsBlind(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in BS.SCENES:
            self.assertEqual(BS.scene_result(n), BS.golden(n), n)
            self.assertEqual(BS.scene_result(n), BS.scene_result(n), n)
        self.assertTrue(BS.emitted_matches_pinned())

    def test_the_corpus_exercises_both_verdicts(self):
        """A corpus that is all one verdict cannot refute anything."""
        size, breached, intact = BS.corpus_census()
        self.assertEqual((size, breached, intact), (545, 170, 375))
        self.assertGreater(breached, 0)
        self.assertGreater(intact, 0)
        self.assertEqual(breached + intact, size)

    def test_the_corpus_order_is_canonical(self):
        """Otherwise 'the first witness found' is a function of set iteration, not of the corpus."""
        c = BS.corpus()
        self.assertEqual(c, tuple(sorted(c, key=BS._key)))
        self.assertEqual(len(c), len(set(c)), "no duplicates")

    def test_all_four_are_refuted(self):
        rows = BS.blindness_census()
        self.assertEqual(rows, (("cell_count", True, 4),
                                ("boundary_occupancy", True, 2),
                                ("tile_prefix", True, 16),
                                ("occupancy_defect", True, 16)))
        self.assertEqual(BS.every_cheap_invariant_is_blind(), (4, 4))
        for name, refuted, div in rows:
            self.assertTrue(refuted, name)
            self.assertGreater(div, 0, "a witness pair must actually differ")

    def test_each_witness_really_has_equal_invariant_and_opposite_verdict(self):
        """Read the pair rather than trusting the boolean."""
        for name, fn in BS.CHEAP:
            a, b = BS.blindness_witness(fn)
            self.assertEqual(fn(a), fn(b), name)
            self.assertNotEqual(CO.verdict(a, BS.WORLD), CO.verdict(b, BS.WORLD), name)

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(BS.BlindError):
            BS.golden("no_such_scene")


class TheConjunctionIsAlsoBlind(unittest.TestCase):
    def test_one_pair_defeats_all_four_at_once(self):
        """The load-bearing negative: every future 'add one more cheap check' is answered here."""
        refuted, ca, cb, div, va, vb = BS.the_conjunction_is_also_blind()
        self.assertTrue(refuted)
        self.assertEqual((ca, cb), (16, 16), "identical cell count")
        self.assertEqual(div, 2, "differing in two cells")
        self.assertEqual((va, vb), (CO.BREACHED, CO.INTACT), "and opposite verdicts")

    def test_the_pair_agrees_on_every_cheap_invariant(self):
        a, b = BS.conjunction_witness()
        for name, fn in BS.CHEAP:
            self.assertEqual(fn(a), fn(b), name)

    def test_connectivity_separates_the_same_pair(self):
        """POSITIVE CONTROL — without this the pair would show a degenerate corpus, not blindness."""
        ra, rb, sep = BS.connectivity_separates_the_pair()
        self.assertTrue(sep)
        self.assertNotEqual(ra, rb)

    def test_the_1885_identity_argument_as_a_lattice_witness(self):
        """'Same empirical formula plus similar properties, therefore the same compound' — identity
        from an invariant that cannot decide it. safrole and isosafrole share C10H10O2."""
        same_count, same_boundary, same_prefix, opposite = \
            BS.eijkman_identity_is_underdetermined()
        self.assertTrue(same_count)
        self.assertTrue(same_boundary)
        self.assertTrue(same_prefix)
        self.assertTrue(opposite, "and yet the verdicts differ")


class CheapnessIsNotSoundness(unittest.TestCase):
    def test_the_two_orders_disagree(self):
        cheap, dear, agree = BS.cheapness_is_not_soundness()
        self.assertEqual(cheap, (), "no cheap invariant decides anything")
        self.assertEqual(dear, ("connectivity",), "only the expensive measurand decides")
        self.assertFalse(agree, "so cost order is not decisiveness order")

    def test_the_ranking_is_read_in_cost_order(self):
        rows = BS.decisiveness_rank()
        self.assertEqual(rows, (("cell_count", False), ("tile_prefix", False),
                                ("occupancy_defect", False), ("boundary_occupancy", False),
                                ("connectivity", True)))
        costs = [dict(BS.COST_RANK)[nm] for nm, _d in rows]
        self.assertEqual(costs, sorted(costs), "presented cheapest-first, which is the temptation")

    def test_the_cheap_screen_clears_liars(self):
        cleared, wrong, total = BS.a_cheap_screen_would_clear_a_liar()
        self.assertEqual((cleared, wrong, total), (8, 3, 8))
        self.assertEqual(cleared, total, "a cell-count screen clears the whole population")
        self.assertGreater(wrong, 0, "and it is wrong about some of them")

    def test_the_population_exercises_both_arms(self):
        """A population of honest peers only would have made the screen look free."""
        agree, disagree = BS.the_population_exercises_both_arms()
        self.assertEqual((agree, disagree), (5, 3))
        self.assertGreater(agree, 0)
        self.assertGreater(disagree, 0)

    def test_the_router_takes_no_blind_invariant(self):
        """A signature check on the decision path, the same discipline that keeps cohort's centrality
        graph unwired."""
        checked, hits = BS.the_router_takes_no_blind_invariant()
        self.assertEqual(checked, 4)
        self.assertEqual(hits, (), "no blind invariant reaches any admission path")


class TheStructuralReasonIsInclusionExclusion(unittest.TestCase):
    def test_three_cheap_invariants_are_valuations_and_the_verdict_is_not(self):
        """The blindness is not four unlucky choices — it is what inclusion-exclusion forces."""
        self.assertEqual(BS.valuation_census(), (
            ("cell_count", 400, 0, True),
            ("boundary_occupancy", None, None, False),
            ("tile_prefix", 400, 0, True),
            ("occupancy_defect", 400, 0, True),
            ("verdict", 400, 24, False),
            ("free_components", 400, 29, False),
        ))
        cheap_vals, tested, viol = BS.the_verdict_is_not_a_valuation()
        self.assertEqual(cheap_vals, ("cell_count", "tile_prefix", "occupancy_defect"))
        self.assertEqual(tested, 400)
        self.assertGreater(viol, 0, "the verdict violates inclusion-exclusion")

    def test_breach_is_two_pointed(self):
        """A valuation assigns one number to one set; breach asks about TWO designated faces."""
        needs_two, one_set, is_a_reason = BS.breach_is_two_pointed()
        self.assertTrue(needs_two)
        self.assertTrue(one_set)
        self.assertTrue(is_a_reason, "graded as a reason, not a theorem")

    def test_the_corpus_missed_the_fifth_witness(self):
        """L19 again, inside this module: a built corpus finding no witness is NOT a surviving
        predicate. The corpus warning this rung already carried came true one invariant later."""
        corpus_found, hand_equal, hand_opposite = BS.the_corpus_missed_the_fifth_witness()
        self.assertFalse(corpus_found, "the 545-occupancy corpus contains no such pair")
        self.assertTrue(hand_equal, "yet a hand-built pair has equal component counts")
        self.assertTrue(hand_opposite, "and opposite verdicts")

    def test_the_fifth_witness_reads_correctly(self):
        ca, cb, va, vb, div = BS.the_fifth_witness()
        self.assertEqual((ca, cb), (1, 1), "one free component each")
        self.assertEqual((va, vb), (CO.INTACT, CO.BREACHED))
        self.assertEqual(div, 35)

    def test_five_of_five_are_blind(self):
        self.assertEqual(BS.five_of_five_are_blind(), (5, 5))


class TheFalsificationRecordIsScoped(unittest.TestCase):
    def test_every_candidate_has_a_row_with_a_witness(self):
        rows = BS.falsification_record()
        self.assertEqual(BS.every_candidate_is_falsified_with_a_witness(), (6, 6))
        for cand, status, witness, failure, impact in rows:
            self.assertEqual(status, "FALSIFIED", cand)
            self.assertTrue(witness.strip(), cand)
            self.assertTrue(failure.strip(), cand)
            self.assertTrue(impact.strip(), cand)

    def test_the_vocabulary_admits_nothing_stronger_than_falsified(self):
        """Five counterexamples are five counterexamples; an impossibility theorem is a different
        object. The scoping is enforced in the status vocabulary, not promised in prose."""
        statuses, forbidden, all_witnessed = BS.the_record_claims_no_impossibility_theorem()
        self.assertEqual(statuses, ("FALSIFIED",))
        self.assertEqual(forbidden, (), "no CONFIRMED / PROVED / IMPOSSIBLE anywhere in the record")
        self.assertTrue(all_witnessed)
        self.assertEqual(BS.STATUS_VOCABULARY, ("FALSIFIED", "OPEN"))

    def test_the_free_components_row_states_its_corpus_limitation(self):
        """The row has to carry the reason the corpus missed it, or the next topological candidate
        gets swept the same insufficient way."""
        row = next(r for r in BS.falsification_record() if r[0] == "free_components")
        self.assertIn("two-pointed", row[3])
        self.assertIn("corpus did NOT contain", row[4])


if __name__ == "__main__":
    unittest.main()
