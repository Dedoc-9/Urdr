# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""scenecost (URDRSCN1) — the composed scene's price as gate-read evidence."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import scenecost as S                                        # noqa: E402


class TheRecords(unittest.TestCase):
    def test_all_eight_artifacts_hash_to_their_pins(self):
        for key in S.RECORDS:
            self.assertTrue(S.load_log(key))
        for cfg in S.CHAINS:
            self.assertTrue(S.load_chain(cfg))

    def test_a_flipped_byte_refuses(self):
        self.assertTrue(S.a_flipped_byte_refuses())

    def test_a_duplicate_record_refuses(self):
        self.assertTrue(S.a_duplicate_record_refuses())

    def test_an_anonymous_record_refuses(self):
        self.assertTrue(S.an_anonymous_record_refuses())

    def test_a_short_focus_counter_refuses(self):
        self.assertTrue(S.a_short_focus_counter_refuses())

    def test_every_record_wears_the_frozen_configuration(self):
        import capcost as C
        logs = S.admit()
        for log in logs.values():
            fp = C.footprint(log["rings"])
            self.assertEqual(log["prefill"], fp)
            self.assertEqual(log["cap"], 2 * fp)
            self.assertEqual(log["evictions"], 0)
            self.assertEqual(log["policy"], "derived-rail-2x-footprint")


class TheIdentityLaws(unittest.TestCase):
    def test_the_baselines_reproduce_the_committed_oracle(self):
        import reachenv as R
        logs = S.admit()
        oracle = R.parse_chain(R.load_chain(S.REACH))
        for sw in S.SWEEPS:
            self.assertEqual(logs[(sw, "off")]["chain"], oracle)

    def test_the_composed_scenes_are_cross_os_identical(self):
        logs = S.admit()
        for cfg in ("third", "full"):
            container = S.parse_chain(S.load_chain(cfg))
            for sw in S.SWEEPS:
                self.assertEqual(logs[(sw, cfg)]["chain"], container)

    def test_two_sweeps_of_one_configuration_render_identically(self):
        logs = S.admit()
        for cfg in S.CONFIGS:
            self.assertEqual(logs[("s1", cfg)]["chain"], logs[("s2", cfg)]["chain"])

    def test_one_edited_digest_reddens(self):
        self.assertTrue(S.a_mismatched_chain_refuses())


class TheVerdicts(unittest.TestCase):
    def test_the_admitted_scene_matches_the_golden(self):
        self.assertEqual(S.scene_result("scene"), S.golden("scene"))

    def test_both_sweeps_classify_every_configuration_fits(self):
        logs = S.admit()
        self.assertEqual(S.verdicts(logs),
                         {"off": "FITS", "third": "FITS", "full": "FITS"})

    def test_a_disagreeing_pair_refuses_to_speak(self):
        self.assertTrue(S.a_disagreeing_pair_refuses_to_speak())


class TheResolutionLaw(unittest.TestCase):
    def test_the_instrument_spread_is_measured_from_the_baseline(self):
        logs = S.admit()
        self.assertGreater(S.instrument_spread(logs), 0)

    def test_terrain_and_wanderer_are_resolved_operating_points(self):
        res = S.resolution(S.admit())
        self.assertTrue(res["off"]["resolved"])
        self.assertTrue(res["third"]["resolved"])

    def test_the_full_composition_is_fits_but_unresolved(self):
        logs = S.admit()
        self.assertEqual(S.verdicts(logs)["full"], "FITS")
        self.assertFalse(S.resolution(logs)["full"]["resolved"])

    def test_the_unresolved_margin_is_inside_the_instrument_spread(self):
        logs = S.admit()
        self.assertLess(S.resolution(logs)["full"]["min"], S.instrument_spread(logs))

    def test_an_unresolved_margin_is_caught(self):
        self.assertTrue(S.an_unresolved_margin_is_caught())


class ThePrice(unittest.TestCase):
    def test_the_total_price_is_positive_in_both_sweeps(self):
        self.assertTrue(S.price_total_positive(S.admit()))

    def test_the_sky_increment_corroborates_its_sealed_standalone_price(self):
        self.assertTrue(S.sky_corroborates(S.admit()))


if __name__ == "__main__":
    unittest.main()
