# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/inputset.py — WHICH INPUTS DETERMINE A QUANTITY (URDRINP1).

  CLASSIFICATION BY WITNESS, NOT BY TABLE — a quantity's tier is the coarsest level that determines
    it, PROVED by a refuting pair at the level below. Every non-CERT row ships its own falsifier.
  THE PROPOSED TAXONOMY MISFILES THE QUORUM — it is peer-dependent, not path-dependent. Identical
    certificate, identical occupancy AND identical history still differ in agreement.
  FOUR TIERS, NOT THREE, AND THE FOURTH EARNS ITS PLACE — publishing the log determines the ledger
    (True) and leaves the quorum undetermined (False). Different obstruction, different remedy.
  THE LAZY CHECK IS VACUOUS — comparing a situation to itself classifies 6 of 6 as CERT-local.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import inputset as IS                                              # noqa: E402


class ClassificationIsDecidedNotTabulated(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in IS.SCENES:
            self.assertEqual(IS.scene_result(n), IS.golden(n), n)
            self.assertEqual(IS.scene_result(n), IS.scene_result(n), n)
        self.assertTrue(IS.emitted_matches_pinned())

    def test_the_decided_table(self):
        got = {name: tier for name, tier, _w in IS.classification()}
        self.assertEqual(got, {
            "exclusion_membership": "CERT",
            "prefix_disjointness": "CERT",
            "liveness_horizon": "CERT",
            "occupancy_defect": "LATTICE",
            "ledger_remainder": "HISTORY",
            "quorum_agreement": "COHORT",
        })

    def test_every_non_cert_row_ships_its_refutation(self):
        """The discipline: nothing is classified above CERT without a witness that it cannot be
        classified lower."""
        with_witness, cert_tier, total = IS.every_classification_carries_a_refutation()
        self.assertEqual((with_witness, cert_tier, total), (3, 3, 6))
        self.assertEqual(with_witness + cert_tier, total)
        for _name, tier, witness in IS.classification():
            if tier != "CERT":
                self.assertIsNotNone(witness, "a higher tier must be earned by a refuting pair")
                self.assertNotEqual(witness[0], witness[1])

    def test_determination_is_monotone(self):
        """Which is what makes 'coarsest' meaningful rather than an artifact of iteration order."""
        self.assertTrue(IS.determination_is_monotone())

    def test_the_levels_are_nested(self):
        fam = IS.family()
        for coarse, fine in zip(IS.LEVELS, IS.LEVELS[1:]):
            for s in fam[:6]:
                self.assertEqual(IS.proj(fine, s)[:len(IS.proj(coarse, s))], IS.proj(coarse, s))

    def test_an_unknown_level_refuses(self):
        with self.assertRaises(IS.InputSetError):
            IS.proj("GALAXY", IS.family()[0])


class TheQuorumIsPeerNotPath(unittest.TestCase):
    def test_neither_the_payload_nor_the_log_determines_it(self):
        tier, lattice, history = IS.quorum_is_peer_not_path()
        self.assertEqual(tier, "COHORT")
        self.assertFalse(lattice, "downloading your own tile settles nothing")
        self.assertFalse(history, "and neither does publishing your own log")

    def test_the_fourth_tier_earns_its_place(self):
        """Different obstruction, different remedy — measured rather than argued."""
        log_fixes_ledger, log_fixes_quorum = IS.path_and_peer_need_different_remedies()
        self.assertTrue(log_fixes_ledger, "publishing the log determines the ledger")
        self.assertFalse(log_fixes_quorum, "and leaves the quorum undetermined")

    def test_the_asserted_table_is_wrong_on_exactly_one_row(self):
        """L15 — the hand-written taxonomy, right on five and wrong on the one that matters."""
        disagreements, total, rows = IS.asserted_table_disagrees()
        self.assertEqual((disagreements, total), (1, 6))
        self.assertEqual(rows, (("quorum_agreement", "LATTICE", "COHORT"),))


class TheWitnessSearchIsThePoint(unittest.TestCase):
    def test_the_lazy_check_is_vacuous(self):
        """L19 — comparing a situation to itself proves nothing and classifies everything as CERT."""
        vacuous, total = IS.witnessless_check_is_vacuous()
        self.assertEqual((vacuous, total), (6, 6))
        self.assertEqual(vacuous, total, "it returns True for every quantity at every level")

    def test_the_family_separates_every_adjacent_level(self):
        """L19 — without separation every quantity would classify as CERT-local for free."""
        seps = IS.family_separates_every_level()
        self.assertEqual(seps, (171, 168, 56))
        for n in seps:
            self.assertGreater(n, 0, "each adjacent level pair must be separated by some pair")
        self.assertEqual(len(IS.family()), 59)

    def test_determines_returns_a_usable_witness(self):
        qfn = dict(IS.QUANTITIES)["occupancy_defect"]
        ok, witness = IS.determines("CERT", qfn)
        self.assertFalse(ok)
        self.assertEqual(witness, (1, 0), "same certificate, different defect")
        ok2, witness2 = IS.determines("LATTICE", qfn)
        self.assertTrue(ok2)
        self.assertIsNone(witness2)


if __name__ == "__main__":
    unittest.main()
