# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/tilemin.py — THE MINIMAL CERTIFICATE (URDRTMN1).

  3 OF 3 FIELDS LATTICE-FREE, against tilecert's 2 of 5. remaining_budget is structurally ABSENT.
  THE REGION IS RECOMPUTED, NEVER TRUSTED — a server marking a restricted tile OPEN and signing it
    correctly is caught with NO lattice at all. That is what makes the field proof-carrying.
  INTEGRITY AND POLICY ARE TWO VERDICTS — an honest certificate for a restricted tile passes
    integrity and fails policy; a forged one fails integrity. Merging them destroys attribution.
  SOUND AND COARSE, BOTH MEASURED — 0 exceptions over 64 tiles, at a 1024x over-refusal.

Every test can go red (L5); the five plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import tilemin as TM                                               # noqa: E402


class AllThreeFieldsAreLatticeFree(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in TM.SCENES:
            self.assertEqual(TM.scene_result(n), TM.golden(n), n)
            self.assertEqual(TM.scene_result(n), TM.scene_result(n), n)
        self.assertTrue(TM.emitted_matches_pinned())

    def test_three_of_three_against_two_of_five(self):
        now, total, was, was_total = TM.all_fields_are_lattice_free()
        self.assertEqual((now, total), (3, 3), "every field checkable with no occupancy")
        self.assertEqual((was, was_total), (2, 5), "tilecert's split, for comparison")

    def test_the_unverifiable_field_is_structurally_absent(self):
        fields, present = TM.the_budget_is_absent()
        self.assertFalse(present, "an unverifiable number on a certificate makes it a claim")
        self.assertNotIn("remaining_budget", fields)
        self.assertEqual(set(TM.FIELDS), {"tile_prefix", "jurisdiction_region", "liveness_token"})

    def test_an_honest_certificate_is_admitted(self):
        """Validity-not-outcome: a verifier that refuses everything proves nothing."""
        self.assertTrue(TM.admits_an_honest_certificate())
        occ = frozenset({(0, 0, 0), (0, 0, 1)})
        cert = TM.certify(occ, 5)
        self.assertTrue(TM.adjudicate(cert, (cert["tile_prefix"] ^ 1,), 6))


class TheRegionIsRecomputedNeverTrusted(unittest.TestCase):
    def test_a_forged_region_dies_without_any_lattice(self):
        """THE PLANT THAT MATTERS — caught before a single voxel moves."""
        caught, honest = TM.forged_region_plant()
        self.assertTrue(caught, "a signed lie about the region is recomputed away")
        self.assertTrue(honest, "and an honest region verifies")

    def test_region_is_a_pure_function_of_the_prefix(self):
        for p in TM.all_tiles():
            self.assertEqual(TM.region_of(p), TM.region_of(p))
            self.assertIn(TM.region_of(p), (TM.OPEN, TM.RESTRICTED))

    def test_an_out_of_range_prefix_refuses(self):
        for bad in (-1, 8 ** TM.TILE_LEVEL, "3", None):
            with self.assertRaises(TM.TileMinError):
                TM.region_of(bad)


class IntegrityAndPolicyAreTwoVerdicts(unittest.TestCase):
    def test_the_two_refusals_stay_distinct(self):
        """A first draft merged them, making an honest restricted tile look forged."""
        honest_integrity, honest_policy, forged_integrity = TM.the_two_refusals_stay_distinct()
        self.assertTrue(honest_integrity, "an honest restricted certificate IS honest")
        self.assertFalse(honest_policy, "and the client still may not enter")
        self.assertFalse(forged_integrity, "while a forged region fails integrity")
        self.assertNotEqual(honest_integrity, forged_integrity, "they must be distinguishable")

    def test_the_refusal_classes_are_distinct(self):
        codes = {TM.TileMinError("x").code, TM.Restricted("x").code, TM.Stale("x").code}
        self.assertEqual(len(codes), 3)

    def test_a_restricted_tile_raises_restricted_not_refuse(self):
        occ = frozenset({(33, 33, 33), (33, 33, 34)})
        cert = TM.certify(occ, 5)
        with self.assertRaises(TM.Restricted):
            TM.adjudicate(cert, (cert["tile_prefix"] ^ 1,), 5, policy_open=True)
        self.assertTrue(TM.adjudicate(cert, (cert["tile_prefix"] ^ 1,), 5, policy_open=False))


class SoundAndCoarse(unittest.TestCase):
    def test_location_jurisdiction_is_sound(self):
        open_t, restricted, exceptions = TM.soundness_census()
        self.assertEqual(exceptions, 0, "an OPEN region must contain no forbidden cell")
        self.assertEqual((open_t, restricted), (63, 1))
        self.assertGreater(restricted, 0, "or the census is vacuous")
        self.assertTrue(TM.location_jurisdiction_is_sound())

    def test_the_over_refusal_is_priced(self):
        refused, actual, ratio = TM.over_refusal_price()
        self.assertEqual((refused, actual, ratio), (4096, 4, 1024))
        self.assertGreater(ratio, 1, "the coarseness is real and stated, not hidden")
        self.assertTrue(TM.coarseness_is_stated())


class ThePlants(unittest.TestCase):
    def test_a_stale_token_is_refused(self):
        fresh, stale_refused = TM.stale_token_plant()
        self.assertTrue(fresh, "at the horizon edge it still verifies")
        self.assertTrue(stale_refused, "and one tick past it does not")
        occ = frozenset({(0, 0, 0)})
        cert = TM.certify(occ, 5)
        with self.assertRaises(TM.Stale):
            TM.adjudicate(cert, (cert["tile_prefix"] ^ 1,), 5 + TM.HORIZON + 1)

    def test_the_neighbour_plants_bite(self):
        self_claim, empty_set, honest = TM.forged_neighbour_plant()
        self.assertTrue(self_claim, "a tile claiming itself as a disjoint neighbour is refused")
        self.assertTrue(empty_set, "and an empty neighbour set does not pass vacuously")
        self.assertTrue(honest, "while a genuinely disjoint neighbour verifies")

    def test_the_lift_attack_is_refused(self):
        self.assertTrue(TM.lifted_certificate_plant())

    def test_an_empty_or_split_tile_refuses(self):
        with self.assertRaises(TM.TileMinError):
            TM.tile_prefix(frozenset())
        with self.assertRaises(TM.TileMinError):
            TM.tile_prefix(frozenset({(0, 0, 0), (63, 63, 63)}))

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(TM.TileMinError):
            TM.golden("no_such_scene")


if __name__ == "__main__":
    unittest.main()
