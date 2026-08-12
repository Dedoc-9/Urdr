# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""deeper (URDRDPR1) — a timing difference with no counted difference is unexplained, and
unexplained is a verdict.

The live instance: under a balanced schedule the named host showed `moulded` beating `flat` at
exactly one work level, ticks = 8, in three of four workloads — while `measure` had already proved
in exact counts that the three representations share a slope and differ only in the intercept. A
band that appears at one tick count and vanishes either side is a difference the op model says
cannot exist."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    sys.path.insert(0, os.path.join(_ROOT, "tools", _d))

import deeper as DP                                          # noqa: E402
import rollbench as RB                                       # noqa: E402


class TheThreeVerdicts(unittest.TestCase):
    def test_a_moving_count_explains_a_moving_time(self):
        self.assertTrue(DP.a_count_that_moves_with_the_time_explains_it())

    def test_no_moving_count_is_unexplained(self):
        self.assertTrue(DP.a_difference_with_no_moving_count_is_unexplained())

    def test_no_counters_at_all_is_not_asked(self):
        """NOT the same as 'no cause found'. Nothing was looked at."""
        self.assertTrue(DP.a_log_without_counters_reads_not_asked())

    def test_they_are_three_findings(self):
        self.assertEqual(len({DP.EXPLAINED, DP.UNEXPLAINED, DP.NOT_ASKED}), 3)
        self.assertTrue(DP.the_three_verdicts_are_different_findings())

    def test_the_symmetric_case_is_also_unexplained(self):
        """Counts differ, time does not: the model predicted a difference that never appeared, and
        a detector looking only for unexplained slowness would miss it."""
        self.assertTrue(DP.equal_times_with_unequal_counts_are_also_unexplained())

    def test_moved_names_the_counter(self):
        a = DP._row(1000, blocks=10, gc0=1, gc1=0, gc2=0)
        b = DP._row(1200, blocks=10, gc0=4, gc1=0, gc2=0)
        self.assertEqual(DP.moved(a, b), ("gc0",))
        self.assertEqual(DP.verdict(a, b), DP.EXPLAINED)


class TheProbe(unittest.TestCase):
    def test_it_bites(self):
        """Without this the module would certify silence: a dead instrument reports 'no difference'
        exactly as convincingly as a working one reports the truth."""
        self.assertTrue(DP.the_probe_bites())

    def test_the_result_is_held_alive_across_the_snapshot(self):
        """THE BUG THIS FALSIFIER CAUGHT. `getallocatedblocks` is a LEVEL, not a counter — discard
        the return value before snapshotting and every transient allocation is already freed, so
        the probe reads zero for a callable allocating five hundred objects."""
        d = DP.count_delta(lambda: [object() for _ in range(500)])
        self.assertGreater(d["blocks"], 100)
        self.assertEqual(sorted(d), sorted(DP.COUNTERS))

    def test_the_transient_counter_sees_churn_the_resident_one_cannot(self):
        """WHY `peak` EXISTS, and it was forced by a reading: on the named host `blocks` was 4
        against 4 in every cell while the times differed by a constant microsecond."""
        self.assertTrue(DP.the_transient_counter_sees_what_resident_counting_cannot())

    def test_the_grouped_form_does_not_depend_on_row_order(self):
        """The row-at-a-time form read whichever row came first; across five executions one cell
        reported EXPLAINED purely because run 0's two timings tied."""
        self.assertTrue(DP.the_grouped_form_does_not_depend_on_row_order())

    def test_an_archived_record_is_compared_on_the_fields_it_has(self):
        self.assertTrue(DP.a_v1_record_is_compared_on_the_fields_it_has())

    def test_grouped_refuses_arms_sharing_no_execution(self):
        with self.assertRaises(DP.DeeperError):
            DP.verdict_grouped({0: {"p50_ns": 1}}, {1: {"p50_ns": 2}})

    def test_a_row_without_a_time_refuses(self):
        self.assertTrue(DP.a_row_without_a_time_refuses())
        with self.assertRaises(DP.DeeperError) as ctx:
            DP.verdict(DP._row(1), {})
        self.assertEqual(ctx.exception.code, "DEEPER-REFUSE")

    def test_a_non_row_refuses(self):
        with self.assertRaises(DP.DeeperError):
            DP.verdict(DP._row(1, blocks=1), ["not", "a", "row"])


class TheBoundIsDeclared(unittest.TestCase):
    def test_the_counter_list_is_declared(self):
        self.assertTrue(DP.the_counter_list_is_declared_not_discovered())
        self.assertEqual(DP.COUNTERS, ("blocks", "gc0", "gc1", "gc2", "peak"))
        self.assertEqual(DP.ADDED_AFTER_V1, ("peak",))

    def test_no_count_reaches_a_golden(self):
        """CPython-version dependent by nature: this container runs a different interpreter from
        the named host, so a digested count would redden the operator's gate for a reason that has
        nothing to do with the tree. Only the PROBE'S PROPERTIES are pinned."""
        import re
        payload = DP.scene_case("probe")
        live = DP.counters()
        # The allocated-block count is a large, host-and-version-specific number: it must not
        # appear, and neither must any multi-digit run, since every live counter is one.
        self.assertNotIn(str(live["blocks"]), payload)
        self.assertEqual(re.findall(r"\d{3,}", payload), [])
        self.assertIn("bites=", payload)


class TheHarnessCarriesIt(unittest.TestCase):
    def test_every_counter_is_a_row_field(self):
        for c in DP.COUNTERS:
            self.assertIn(c, RB.ROW_FIELDS)

    def test_a_parsed_log_carries_them(self):
        p = RB.parse_log(RB._declared_log())
        for r in p["rows"]:
            for c in DP.COUNTERS:
                self.assertIn(c, r)


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in DP.SCENES:
            with self.subTest(name):
                self.assertEqual(DP.scene_result(name), DP.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(DP.deeper_digest(), DP.golden("deeper"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(DP.DeeperError):
            DP.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
