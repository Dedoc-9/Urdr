# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/jurisdiction.py — S3 IN THE DEFECT FRAMEWORK (URDRJUR1).

  ADMISSIBILITY IS A LATTICE PREDICATE — a bound certificate asserting the block is fine is ADMITTED
    by metadata and REFUSED by the lattice, and the verdict is invariant under every certificate.
  ONE UNIT, ONE BUDGET — defect in cells, subadditive over 55 pairs with 0 violations and 3 pairs
    carrying defect on BOTH sides so the census is not confirming 0 + 0 = 0.
  COMPOSITION IS STRUCTURAL — 49 prefix-disjoint pairs compose by union, 0 exceptions.
  THE FILTRATION DID NOT SURVIVE — it separates a careless doctorer AND is reachable by any chosen
    confidences, so it is a screen, not the integrity signal it was proposed as. recirc had already
    measured the operator idempotent, so there is no iteration history to compare at all.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import jurisdiction as JR                                           # noqa: E402


class AdmissibilityIsALatticePredicate(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in JR.SCENES:
            self.assertEqual(JR.scene_result(n), JR.golden(n), n)
            self.assertEqual(JR.scene_result(n), JR.scene_result(n), n)
        self.assertTrue(JR.emitted_matches_pinned())

    def test_metadata_admits_what_the_lattice_refuses(self):
        """The lift attack provbind's binding cannot stop, because binding proves the claim BELONGS
        to this lattice — not that the claim is true."""
        metadata_admits, lattice_refuses = JR.lift_attack()
        self.assertTrue(metadata_admits, "a bound, truthful-looking certificate passes metadata")
        self.assertTrue(lattice_refuses, "and the lattice predicate refuses it anyway")

    def test_the_verdict_is_invariant_under_every_certificate(self):
        verdicts = JR.certificate_is_not_consulted()
        self.assertEqual(len(verdicts), 1, "the certificate must not move the verdict at all")
        self.assertEqual(verdicts, (False,))

    def test_a_clean_block_is_admitted(self):
        """Validity-not-outcome: a predicate that refuses everything is useless."""
        self.assertTrue(JR.adjudicate(frozenset({(0, 0, 0), (5, 5, 5)})))
        self.assertTrue(JR.admissible(frozenset({(10, 10, 10)})))

    def test_a_violating_block_raises(self):
        with self.assertRaises(JR.Inadmissible):
            JR.adjudicate(frozenset({(33, 33, 33)}))
        self.assertEqual(JR.defect(frozenset({(33, 33, 33), (33, 33, 34), (0, 0, 0)})), 2)

    def test_cells_outside_the_world_refuse(self):
        for bad in ((64, 0, 0), (-1, 0, 0), (0, 0, 999)):
            with self.assertRaises(JR.JurisdictionError):
                JR.defect(frozenset({bad}))

    def test_the_two_refusal_classes_are_distinct(self):
        self.assertNotEqual(JR.Inadmissible("x").code, JR.JurisdictionError("x").code)


class OneUnitOneBudget(unittest.TestCase):
    def test_the_family_is_not_vacuous(self):
        """L19 — and this census caught a real defect: a first draft had ZERO disjoint pairs."""
        blocks, violating, disjoint = JR.family_is_not_vacuous()
        self.assertEqual((blocks, violating, disjoint), (11, 3, 49))
        self.assertGreater(violating, 0, "blocks must actually violate or defect is always 0")
        self.assertGreater(disjoint, 0, "and pairs must actually be disjoint or composition is free")

    def test_defect_is_subadditive(self):
        pairs, violations, tight, both_positive = JR.subadditivity_census()
        self.assertEqual(violations, 0, "defect(A|B) never exceeds defect(A) + defect(B)")
        self.assertEqual((pairs, tight, both_positive), (55, 53, 3))
        self.assertGreater(both_positive, 0, "or the law is confirming 0 + 0 = 0")
        self.assertTrue(JR.subadditive())

    def test_composition_over_disjoint_subtrees_is_structural(self):
        disjoint, exceptions, total = JR.composition_census()
        self.assertEqual(exceptions, 0, "disjoint supports compose by union with no check")
        self.assertEqual((disjoint, total), (49, 55))
        self.assertLess(disjoint, total, "and non-disjoint pairs exist, so the filter does work")
        self.assertTrue(JR.composition_is_structural())


class TheFiltrationDidNotSurvive(unittest.TestCase):
    def test_it_separates_a_careless_doctorer(self):
        """(a) The proposal's intuition, and it is sound."""
        doctored, honest = JR.filtration_separates_a_careless_doctorer()
        self.assertEqual((doctored, honest), ((0, 1), (1, 2, 3)))
        self.assertLess(max(doctored), max(honest))

    def test_it_is_reachable_by_any_chosen_confidences(self):
        """(b) And it is free to anyone who reads it — the filtration is submitter-supplied data."""
        n_by, distinct, honest_shaped, reachable, every = JR.filtration_is_forgeable()
        self.assertEqual((n_by, distinct, honest_shaped, reachable), (256, 256, 8, 9))
        self.assertTrue(every, "every honest-shaped filtration is reachable by an adversary")
        self.assertLessEqual(honest_shaped, reachable)

    def test_the_honest_disposition_is_screen_not_verdict(self):
        separates, forgeable = JR.filtration_is_a_screen_not_a_verdict()
        self.assertTrue(separates, "it does catch the careless")
        self.assertTrue(forgeable, "and it is free to the informed — so it is not an integrity signal")

    def test_recirc_already_refuted_the_iteration(self):
        """(c) Cross-module, read from recirc rather than restated: if that module ever moves, this
        goes red."""
        idempotent, at_most_one, collides = JR.recirc_already_refuted_the_iteration()
        self.assertTrue(idempotent, "the operator is idempotent — there is no filtration to compare")
        self.assertTrue(at_most_one)
        self.assertTrue(collides, "and fixed points conflate honest with doctored")


class TheCorpusIsEmittedNotInscribed(unittest.TestCase):
    def test_the_pinned_file_is_the_modules_own_output(self):
        self.assertEqual(JR.conformance_lines(), JR.pinned_lines())

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(JR.JurisdictionError):
            JR.golden("no_such_scene")


if __name__ == "__main__":
    unittest.main()
