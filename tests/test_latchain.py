# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""latchain (URDRLTC1) — the waiting latency record through the strict door."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import latchain as L                                         # noqa: E402
import sealframe as SF                                       # noqa: E402


class TheRecord(unittest.TestCase):
    def test_the_record_hashes_to_its_pin(self):
        self.assertTrue(L.load())

    def test_a_flipped_byte_refuses(self):
        self.assertTrue(L.a_flipped_byte_refuses())

    def test_a_v01_header_refuses_by_version_dispatch(self):
        self.assertTrue(L.a_v01_record_refuses())

    def test_every_chain_total_re_adds(self):
        parsed = L.parse(L.load())
        self.assertEqual(len(parsed["chains"]), 32)

    def test_a_broken_sum_refuses(self):
        self.assertTrue(L.a_broken_sum_refuses())


class TheStrictDoor(unittest.TestCase):
    def setUp(self):
        self.parsed = L.parse(L.load())

    def test_the_strict_door_admits_this_record(self):
        ok, why = L.the_strict_door_admits(self.parsed, SF.make_segment_log, SF.ledger_from_log)
        self.assertTrue(ok, why)

    def test_a_condition_stripped_log_refuses(self):
        self.assertTrue(L.a_condition_stripped_log_refuses(
            self.parsed, SF.make_segment_log, SF.ledger_from_log))

    def test_the_floor_cannot_be_lowered(self):
        ok, why = L.the_floor_cannot_be_lowered(
            self.parsed, SF.make_segment_log, SF.ledger_from_log, SF.SEGMENTS)
        self.assertTrue(ok, why)


class ThePartialChainLaw(unittest.TestCase):
    def test_the_bound_rises_and_the_verdict_stays_undetermined(self):
        parsed = L.parse(L.load())
        ok, why = L.the_bound_rises_and_stays_a_bound(
            parsed, SF.make_segment_log, SF.ledger_from_log, SF.SEGMENTS,
            SF.lower_bound_ms, SF.budget_verdict)
        self.assertTrue(ok, why)

    def test_a_photon_claim_refuses(self):
        self.assertTrue(L.a_photon_claim_refuses(SF.grade_segment))


class TheGolden(unittest.TestCase):
    def test_the_record_scene_reproduces_its_golden(self):
        self.assertEqual(L.scene_result("record"), L.golden("record"))


if __name__ == "__main__":
    unittest.main()
