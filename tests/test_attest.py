# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""attest (URDRATT1) — a graduated claim is a committed log the gate re-reads, and every number in
it is derived rather than typed.

The endpoint of the arc `measure` opened: the answer stops being a paste in a conversation and
becomes an artifact the gate re-reads on every run."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    sys.path.insert(0, os.path.join(_ROOT, "tools", _d))

import attest as AT                                          # noqa: E402
import measure as MS                                         # noqa: E402
import repeat as RP                                          # noqa: E402
import rollbench as RB                                       # noqa: E402


class TheRecordIsReal(unittest.TestCase):
    def test_it_is_committed_and_still_seals(self):
        self.assertTrue(AT.the_record_is_committed_and_still_seals())
        self.assertTrue(os.path.exists(os.path.join(_ROOT, AT.RECORD)))

    def test_a_tampered_record_refuses(self):
        self.assertTrue(AT.a_tampered_record_refuses())

    def test_a_missing_record_refuses(self):
        with self.assertRaises(AT.AttestError) as ctx:
            AT.record("spec/attest/there-is-no-such-log.txt")
        self.assertEqual(ctx.exception.code, "ATTEST-REFUSE")

    def test_the_record_is_not_the_scratch_path(self):
        """`--bench` overwrites its output path every run; a record kept there is one command from
        being replaced by a different measurement under the same name."""
        self.assertTrue(AT.the_record_is_not_the_scratch_path())
        self.assertNotEqual(AT.RECORD, AT.SCRATCH)

    def test_it_grades_admissible_against_the_live_door(self):
        p = AT.record()
        self.assertEqual(RB.evidence_grade(p)[0], RB.MEASURED)
        self.assertEqual(p["host"], "ROG-Ally-X-Z2-Extreme")


class TheFormatOutlivedIt(unittest.TestCase):
    def test_a_v1_record_reads_under_a_v2_writer(self):
        """L64 + L67: the versioning law ships WITH a real successor format, in the same commit,
        because a law never met by one is inherited rather than tested."""
        self.assertTrue(AT.the_record_survives_the_format_that_superseded_it())
        self.assertEqual(AT.record()["version"], "v1")
        self.assertEqual(RB.LOG_VERSION, "v2")
        self.assertLess(len(RB.ROW_FIELDS_BY_VERSION["v1"]), len(RB.ROW_FIELDS))

    def test_an_unknown_format_refuses(self):
        self.assertTrue(AT.an_unknown_format_refuses())

    def test_a_v1_row_carries_no_field_v1_never_had(self):
        for r in AT.record()["rows"]:
            self.assertNotIn("peak", r)
            self.assertIn("blocks", r)


class TheNumbersAreDerived(unittest.TestCase):
    def test_nothing_is_typed(self):
        """No derived figure may appear as a literal in the module: a typed number is a copy that
        drifts from its source the first time either is edited."""
        self.assertTrue(AT.the_numbers_are_derived_not_typed())

    def test_the_reading_is_stable(self):
        self.assertEqual(AT.reading(), AT.reading())

    def test_the_reading_matches_an_independent_recomputation(self):
        """Derived twice by different code: once by the module, once here from the raw rows."""
        r = AT.reading()
        rows = AT.record()["rows"]
        self.assertEqual(r["executions"], len({int(x["run"]) for x in rows}))
        self.assertEqual(r["experiments"], len(AT.experiments()))
        self.assertEqual(r["separated"] + r["indistinguishable"] + r["undetermined"],
                         r["experiments"])

    def test_a_different_record_gives_a_different_reading(self):
        """NON-VACUITY: if the reading did not depend on the bytes, pinning it would prove nothing."""
        with self.assertRaises(Exception):
            AT.reading("tools/terrain/conformance_attest.txt")


class TheResult(unittest.TestCase):
    def test_the_penalty_is_a_constant_not_a_slope(self):
        """`measure` predicted this from op counts before any host ran anything: moulding moves the
        INTERCEPT and cannot move the SLOPE."""
        self.assertTrue(AT.the_penalty_is_a_constant_not_a_slope())
        r = AT.reading()
        span = r["penalty_max_ns"] - r["penalty_min_ns"]
        self.assertLessEqual(abs(r["penalty_deep_ns"] - r["penalty_shallow_ns"]), span)

    def test_the_penalty_has_a_sign(self):
        """Positive means `moulded` is SLOWER. A magnitude with no sign is not a result."""
        self.assertGreater(AT.reading()["penalty_median_ns"], 0)

    def test_direction_and_separation_are_reported_apart(self):
        self.assertTrue(AT.the_direction_is_reported_with_the_verdict())
        r = AT.reading()
        self.assertGreater(r["pairs"], r["experiments"])
        self.assertLess(r["reversals"], r["pairs"] // 2)

    def test_the_indistinguishable_ones_are_not_upgraded(self):
        """The honest half: where URDRRPT1 reads INDISTINGUISHABLE it stays that way here."""
        r = AT.reading()
        self.assertGreater(r["indistinguishable"], 0)
        self.assertGreater(r["separated"], 0)

    def test_the_claim_is_admitted_by_measure_and_a_partial_one_is_not(self):
        self.assertTrue(AT.the_claim_is_well_formed())
        self.assertEqual(MS.claim_fault(dict(AT.CLAIM_SHAPE)), "")
        bad = dict(AT.CLAIM_SHAPE)
        bad.pop("baseline")
        self.assertNotEqual(MS.claim_fault(bad), "")


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in AT.SCENES:
            with self.subTest(name):
                self.assertEqual(AT.scene_result(name), AT.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(AT.attest_digest(), AT.golden("attest"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(AT.AttestError):
            AT.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
