# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""skycost (URDRSKY1) — the far field's price as gate-read evidence."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import skycost as S                                          # noqa: E402


class TheRecords(unittest.TestCase):
    def test_all_three_records_hash_to_their_pins(self):
        for which in S.RECORDS:
            self.assertTrue(S.load_log(which))
        self.assertTrue(S.load_skychain())

    def test_a_flipped_byte_refuses(self):
        self.assertTrue(S.a_flipped_byte_refuses())

    def test_a_duplicate_record_refuses(self):
        self.assertTrue(S.a_duplicate_record_refuses())

    def test_an_anonymous_record_refuses(self):
        self.assertTrue(S.an_anonymous_record_refuses())


class TheLabelAndTheFreeze(unittest.TestCase):
    def test_the_off_record_carries_the_committed_oracle(self):
        off, _on = S.admit()
        import reachenv as R
        self.assertEqual(off["chain"], R.parse_chain(R.load_chain(S.REACH)))

    def test_the_on_record_carries_the_container_sky_chain(self):
        _off, on = S.admit()
        self.assertEqual(on["chain"], S.parse_chain(S.load_skychain()))

    def test_a_relabeled_sky_is_caught_by_its_bytes(self):
        self.assertTrue(S.a_relabeled_sky_is_caught())

    def test_one_edited_digest_reddens(self):
        self.assertTrue(S.a_mismatched_chain_refuses())

    def test_both_records_wear_the_frozen_defaults(self):
        off, on = S.admit()
        import capcost as C
        for log in (off, on):
            fp = C.footprint(log["rings"])
            self.assertEqual(log["prefill"], fp)
            self.assertEqual(log["cap"], 2 * fp)
            self.assertEqual(log["evictions"], 0)
            self.assertEqual(log["policy"], "derived-rail-2x-footprint")

    def test_an_off_rail_record_refuses(self):
        self.assertTrue(S.an_off_rail_record_refuses())


class ThePrice(unittest.TestCase):
    def test_the_admitted_price_matches_the_golden(self):
        self.assertEqual(S.scene_result("skyprice"), S.golden("skyprice"))

    def test_every_segment_pays_a_positive_price(self):
        off, on = S.admit()
        for d in S.price(off, on)["deltas_ns"]:
            self.assertGreater(d, 0)

    def test_the_far_field_rides_inside_the_competitive_profile(self):
        self.assertTrue(S.verdict_holds())

    def test_the_ceiling_stays_under_the_slot_with_the_sky_on(self):
        off, on = S.admit()
        p = S.price(off, on)
        self.assertLessEqual(p["worst_on"], S.SLOT_120_NS)
        self.assertEqual(p["late_on"], 0)


if __name__ == "__main__":
    unittest.main()
