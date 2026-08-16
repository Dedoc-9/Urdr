# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""reachenv (URDRENV1) — the reach envelope as gate-read evidence."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import reachenv as R                                         # noqa: E402


class TheRecords(unittest.TestCase):
    def test_all_eight_records_hash_to_their_pins(self):
        for reach in R.REACHES:
            self.assertTrue(R.load_log(reach))
            self.assertTrue(R.load_chain(reach))

    def test_a_flipped_byte_refuses(self):
        self.assertTrue(R.a_flipped_byte_refuses())

    def test_a_wrong_version_refuses(self):
        self.assertTrue(R.a_wrong_version_refuses())

    def test_an_anonymous_record_refuses(self):
        self.assertTrue(R.an_anonymous_record_refuses())


class TheContracts(unittest.TestCase):
    def test_every_printed_ladder_matches_the_derived_model(self):
        for reach in R.REACHES:
            log = R.parse_log(R.load_log(reach))
            self.assertEqual(log["rings"], R.expected_ladder(reach))

    def test_a_tampered_ring_is_caught(self):
        self.assertTrue(R.a_tampered_ring_refuses())

    def test_host_and_container_chains_agree_at_every_reach(self):
        for reach in R.REACHES:
            log = R.parse_log(R.load_log(reach))
            self.assertEqual(log["chain"], R.parse_chain(R.load_chain(reach)))

    def test_one_edited_digest_reddens(self):
        self.assertTrue(R.a_mismatched_chain_refuses())


class TheEnvelope(unittest.TestCase):
    def test_the_verdicts_derive_and_match_the_golden(self):
        self.assertEqual(R.scene_result("envelope"), R.golden("envelope"))

    def test_reach_60_fits_the_competitive_budget_by_ceiling(self):
        env = R.envelope(R.admit())
        self.assertEqual(env[60]["at120"], "FITS")
        self.assertEqual(env[60]["late"], 0)

    def test_every_swept_reach_fits_60hz(self):
        env = R.envelope(R.admit())
        for reach in R.REACHES:
            self.assertEqual(env[reach]["at60"], "FITS")


if __name__ == "__main__":
    unittest.main()
