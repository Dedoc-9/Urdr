# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""castlecost (URDRCCS1) — the castle's price, and the separation that outlives it."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import castlecost as C                                          # noqa: E402


class TheRecords(unittest.TestCase):
    def test_every_run_is_complete(self):
        self.assertTrue(C.every_run_is_complete())

    def test_the_records_have_graduated(self):
        self.assertTrue(C.the_records_have_graduated())

    def test_the_workload_still_predates_the_contract(self):
        self.assertTrue(C.the_workload_still_predates_the_contract())

    def test_completeness_is_delegated_not_reimplemented(self):
        # The source of truth is admit's adjudication, so a record that admit refuses must fail
        # HERE too — no private second opinion that could disagree in silence.
        import admit as AD
        for n in C.RUNS.values():
            self.assertEqual(AD.adjudicate(AD.parse_record(C._read(n))), "ADMITTED", n)

    def test_every_pair_is_chain_identical(self):
        self.assertTrue(C.every_pair_is_chain_identical())

    def test_the_arms_differ_in_exactly_one_declared_variable(self):
        self.assertTrue(C.the_arms_differ_in_exactly_one_declared_variable())

    def test_the_trace_is_the_workload_both_arms_ran(self):
        self.assertTrue(C.the_trace_is_the_workload_both_arms_ran())

    def test_every_record_carries_the_named_host(self):
        for key in C.RUNS:
            r = C.record(key)
            self.assertEqual(r["host"], "ROG-Ally-X-Z2-Extreme")
            self.assertNotEqual(r["power"], "-")
            self.assertNotEqual(r["scheduler"], "-")


class TheVerdict(unittest.TestCase):
    def test_the_castle_exceeds_the_slot_at_both_reaches(self):
        self.assertTrue(C.the_castle_exceeds_the_slot_at_both_reaches())

    def test_the_castle_delta_is_reach_invariant(self):
        self.assertTrue(C.the_castle_delta_is_reach_invariant())

    def test_the_terrain_side_did_get_cheaper(self):
        self.assertTrue(C.the_terrain_side_did_get_cheaper())

    def test_the_scene_without_the_castle_fits(self):
        self.assertTrue(C.the_scene_without_the_castle_fits())

    def test_the_frozen_segment_set_is_not_the_whole_run(self):
        # If the read rule covered every segment it would not be a rule.
        every = set(C.record(("r120", "on", "b"))["seg"])
        self.assertTrue(set(C.TEST_SEGMENTS) < every)

    def test_a_segment_outside_the_frozen_set_is_not_consulted(self):
        self.assertTrue(C.a_segment_outside_the_frozen_set_is_not_consulted())

    def test_a_swapped_arm_is_caught(self):
        self.assertTrue(C.a_swapped_arm_is_caught())


class ThePresenceOracle(unittest.TestCase):
    def test_the_cost_is_fill_not_setup(self):
        self.assertTrue(C.the_cost_is_fill_not_setup())

    def test_a_presence_segment_is_not_a_content_segment(self):
        self.assertTrue(C.a_presence_segment_is_not_a_content_segment())

    def test_the_presence_segments_really_are_chain_identical(self):
        off = dict(C.record(("r120", "off", "b"))["chain"])
        on = dict(C.record(("r120", "on", "b"))["chain"])
        n = C.record(("r120", "off", "b"))["seg"][0]["n"]
        for seg in C.presence_segments("r120"):
            marks = [f for f in off if seg * n <= int(f) < (seg + 1) * n]
            self.assertTrue(marks, seg)
            for f in marks:
                self.assertEqual(off[f], on[f], (seg, f))

    def test_the_chains_do_diverge_somewhere(self):
        # NON-VACUITY of the oracle: if the two arms agreed everywhere, the castle drew nothing
        # at all and every delta here would be measuring noise.
        off = dict(C.record(("r120", "off", "b"))["chain"])
        on = dict(C.record(("r120", "on", "b"))["chain"])
        self.assertTrue(any(off[f] != on[f] for f in off))


class TheRefusals(unittest.TestCase):
    def test_a_missing_record_refuses(self):
        self.assertTrue(C.a_missing_record_refuses())

    def test_a_headerless_record_refuses(self):
        self.assertTrue(C.a_headerless_record_refuses())

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(C.CastlecostError):
            C.scene_case("no-such-scene")

    def test_the_scene_matches_its_pinned_golden(self):
        self.assertEqual(C.scene_result("verdict"), C.golden("verdict"))

    def test_the_derivation_is_a_pure_function_of_the_bytes(self):
        self.assertEqual(C.scene_result("verdict"), C.scene_result("verdict"))


if __name__ == "__main__":                                      # pragma: no cover
    unittest.main()
