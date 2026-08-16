# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""capcost (URDRCPC1) — the bounded cache's cost surface as gate-read evidence."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import capcost as C                                          # noqa: E402


class TheRecords(unittest.TestCase):
    def test_all_six_records_hash_to_their_pins(self):
        for key in C.RECORDS:
            self.assertTrue(C.load_log(key))
        self.assertTrue(C.load_schedule())

    def test_a_flipped_byte_refuses(self):
        self.assertTrue(C.a_flipped_byte_refuses())

    def test_a_duplicate_record_refuses(self):
        self.assertTrue(C.a_duplicate_record_refuses())

    def test_an_anonymous_record_refuses(self):
        self.assertTrue(C.an_anonymous_record_refuses())


class TheContracts(unittest.TestCase):
    def test_every_prefill_count_equals_the_ladders_own_footprint(self):
        for key in C.RECORDS:
            log = C.parse_log(C.load_log(key))
            self.assertEqual(log["prefill"], C.footprint(log["rings"]))

    def test_a_tampered_prefill_is_caught(self):
        self.assertTrue(C.a_tampered_prefill_refuses())

    def test_every_host_chain_equals_the_committed_oracle(self):
        import reachenv as R
        for (reach, cap) in C.RECORDS:
            log = C.parse_log(C.load_log((reach, cap)))
            self.assertEqual(log["chain"], R.parse_chain(R.load_chain(reach)))

    def test_one_edited_digest_reddens(self):
        self.assertTrue(C.a_mismatched_chain_refuses())


class TheTwoRegimes(unittest.TestCase):
    def test_the_admitted_table_matches_the_golden(self):
        self.assertEqual(C.scene_result("captable"), C.golden("captable"))

    def test_the_above_footprint_rail_rides_free(self):
        logs, _s = C.admit()
        self.assertEqual(C._counts(logs[(500, 131072)]), C._counts(logs[(500, 0)]))
        self.assertEqual(logs[(500, 131072)]["evictions"], 0)

    def test_a_below_footprint_cap_wears_regime_b(self):
        logs, _s = C.admit()
        for cap in (65536, 32768):
            g = logs[(500, cap)]
            self.assertEqual(C.regime(cap, C.footprint(g["rings"])), "B")
            self.assertGreater(g["evictions"], 0)
            self.assertGreater(g["recomputes"], g["occupancy"])

    def test_a_relabeled_cap_is_caught_by_its_scars(self):
        self.assertTrue(C.a_relabeled_cap_is_caught())

    def test_the_degradation_is_visible_in_the_sealed_bytes(self):
        logs, _s = C.admit()
        late_a = max(logs[(500, 0)]["late"], logs[(500, 131072)]["late"])
        for cap in (65536, 32768):
            self.assertGreater(logs[(500, cap)]["late"], late_a)


class TheOneSchedule(unittest.TestCase):
    def test_the_prefilled_container_counts_equal_the_demos(self):
        logs, sched = C.admit()
        for key, log in logs.items():
            self.assertEqual(C._counts(sched["run"][key]), C._counts(log))

    def test_the_no_prefill_counts_differ_at_every_shared_point(self):
        logs, sched = C.admit()
        for key, r in sched["raw"].items():
            self.assertNotEqual(C._counts(r), C._counts(logs[key]))

    def test_a_prefill_free_count_claim_refuses(self):
        self.assertTrue(C.a_prefill_free_count_claim_refuses())

    def test_the_container_reach_60_boundary_point_wears_regime_b(self):
        _logs, sched = C.admit()
        ex = sched["run"][(60, 16384)]
        self.assertGreater(ex["evictions"], 0)
        self.assertEqual(ex["occupancy"], 16384)
        self.assertGreater(ex["recomputes"], ex["occupancy"])


if __name__ == "__main__":
    unittest.main()
