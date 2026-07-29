# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/tilecert.py — THE TILE CERTIFICATE (URDRTIL1).

  THE THREE-TIER SPLIT — of five fields, 2 are checkable without the lattice (genuinely
    proof-carrying in Necula's sense), 2 only once the bytes arrive, and 1 NEVER from bytes at all.
  ATTRIBUTION, NOT PRE-DOWNLOAD VERIFICATION — a lying field is invisible before, transferable proof
    after. And the limit is measured beside the win: a false budget is admitted.
  THE ESTIMATOR IS REFUTED TWICE — it saves 0 work, and its perfect correlation is an artifact that
    hand-built witnesses invert (defect 4 at estimate 6 against defect 0 at estimate 16).
  A VACUOUS CHECK CAUGHT BY ITS OWN PLANT — the disjointness verifier filtered out the only case it
    could be wrong about, so all() ran empty and returned True.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import tilecert as TC                                              # noqa: E402


class TheThreeTierSplit(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in TC.SCENES:
            self.assertEqual(TC.scene_result(n), TC.golden(n), n)
            self.assertEqual(TC.scene_result(n), TC.scene_result(n), n)
        self.assertTrue(TC.emitted_matches_pinned())

    def test_the_taxonomy_is_three_tiered(self):
        without, with_l, never, total = TC.verifiability_taxonomy()
        self.assertEqual((without, with_l, never, total), (2, 2, 1, 5))
        self.assertEqual(without + with_l + never, total, "every field is classified")
        self.assertGreater(never, 0, "and the unverifiable tier is not empty")
        self.assertTrue(TC.taxonomy_is_three_tiered())

    def test_the_budget_field_is_never_settled_by_bytes(self):
        """THE SHARP ONE: budget is a function of admission HISTORY, not of occupancy."""
        same_digest, diff_budget, checker_none = TC.the_budget_field_is_never_settled_by_bytes()
        self.assertTrue(same_digest, "byte-identical lattices")
        self.assertTrue(diff_budget, "carrying different remainders")
        self.assertTrue(checker_none, "and no download decides between them")

    def test_the_tiers_are_the_declared_sets(self):
        self.assertEqual(len(TC.WITHOUT_LATTICE), 2)
        self.assertEqual(len(TC.WITH_LATTICE), 2)
        self.assertEqual(len(TC.NEVER_FROM_LATTICE), 1)
        self.assertEqual(set(TC.WITHOUT_LATTICE) | set(TC.WITH_LATTICE)
                         | set(TC.NEVER_FROM_LATTICE), set(TC.FIELDS))


class AttributionNotVerification(unittest.TestCase):
    def test_a_lie_is_invisible_before_and_transferable_after(self):
        invisible, caught, third_party = TC.attribution_is_transferable()
        self.assertTrue(invisible, "no lattice-less client can see it")
        self.assertTrue(caught, "the bytes settle it")
        self.assertTrue(third_party, "and any third party reaches the same verdict")

    def test_attribution_does_not_reach_the_budget(self):
        """THE LIMIT, measured beside the win rather than omitted."""
        admitted, field = TC.attribution_does_not_reach_the_budget()
        self.assertTrue(admitted, "a false budget is admitted — nothing recomputes it")
        self.assertIsNone(field)

    def test_an_honest_certificate_is_admitted(self):
        """Validity-not-outcome: a verifier that refuses everything proves nothing."""
        occ = frozenset({(33, 0, 0), (33, 0, 1)})
        self.assertTrue(TC.adjudicate(TC.certify(occ, 3, 7), occ))

    def test_the_binding_holds_and_an_unbound_certificate_refuses(self):
        occ = frozenset({(33, 0, 0)})
        cert = TC.certify(occ, 3, 7)
        self.assertTrue(TC.binding_holds(cert))
        cert["binding"] = "0" * 64
        with self.assertRaises(TC.TileCertError):
            TC.adjudicate(cert, occ)


class ThePlants(unittest.TestCase):
    def test_the_forged_disjointness_plant_bites(self):
        """L15 — and this plant caught a VACUOUS check in the verifier it was testing."""
        liar, honest = TC.forged_disjointness_plant()
        self.assertFalse(liar, "a tile claiming itself as a disjoint neighbour must be refused")
        self.assertTrue(honest, "and a genuinely disjoint neighbour accepted")

    def test_the_disjointness_check_is_not_vacuous(self):
        """The defect directly: an empty neighbour set must not pass by running all() over nothing."""
        occ = frozenset({(33, 0, 0)})
        cert = TC.certify(occ, 3, 7)
        self.assertFalse(TC.check_without_lattice(cert, ())["tile_prefix"])

    def test_the_forged_budget_plant_shows_the_gap(self):
        unsigned_caught, resigned_caught = TC.forged_budget_plant()
        self.assertTrue(unsigned_caught, "an unsigned edit breaks the binding")
        self.assertFalse(resigned_caught, "a correctly re-signed lie is admitted — that IS the gap")

    def test_the_lift_attack_is_refused(self):
        """provbind's attack at the tile layer."""
        self.assertEqual(TC.lifted_certificate_plant(), (True,))


class TheEstimatorIsRefuted(unittest.TestCase):
    def test_it_saves_no_work(self):
        est, exact, saving = TC.estimator_saves_no_work()
        self.assertEqual(saving, 0, "'refuse before processing' processes")
        self.assertEqual(est, exact)

    def test_its_perfect_correlation_is_an_artifact(self):
        """L20 caught on the repo's own family — the number must not be read as an endorsement."""
        agree, pairs = TC.estimator_correlation()
        self.assertEqual((agree, pairs), (24, 24))
        td, te, sd, se, inverted = TC.estimator_correlation_is_an_artifact()
        self.assertEqual((td, te, sd, se), (4, 6, 0, 16))
        self.assertGreater(td, sd, "the tight cluster has MORE defect")
        self.assertLess(te, se, "and LESS estimated cost")
        self.assertTrue(inverted, "so the proxy orders them backwards")


class TheRefusalIsTyped(unittest.TestCase):
    def test_an_empty_or_split_tile_refuses(self):
        with self.assertRaises(TC.TileCertError):
            TC.tile_prefix(frozenset())
        with self.assertRaises(TC.TileCertError):
            TC.tile_prefix(frozenset({(0, 0, 0), (63, 63, 63)}))

    def test_the_two_classes_are_distinct(self):
        self.assertNotEqual(TC.Misattested("x").code, TC.TileCertError("x").code)

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(TC.TileCertError):
            TC.golden("no_such_scene")


if __name__ == "__main__":
    unittest.main()
