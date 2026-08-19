# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""admit (URDRADM1) — the instrument reports; the gate adjudicates."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import admit as A                                                # noqa: E402


class TheContract(unittest.TestCase):
    def test_the_class_table_is_not_vacuous(self):
        self.assertTrue(A.the_class_table_is_not_vacuous())

    def test_the_version_extractor_is_imported(self):
        self.assertTrue(A.the_version_extractor_is_imported())

    def test_a_complete_run_is_admitted(self):
        self.assertTrue(A.a_complete_run_is_admitted())

    def test_a_play_record_carries_no_completeness_verdict(self):
        self.assertTrue(A.a_play_record_carries_no_completeness_verdict())

    def test_the_status_is_a_conjunction_not_one_condition(self):
        # frames alone, focus alone, and both — three distinct refusals, one verdict.
        self.assertEqual(A.adjudicate(A._rec((9, 10), (9, 9), "INCOMPLETE (frames)")), "REJECTED")
        self.assertEqual(A.adjudicate(A._rec((10, 10), (9, 10), "INCOMPLETE (focus)")), "REJECTED")
        self.assertEqual(A.adjudicate(A._rec((9, 10), (8, 9), "INCOMPLETE (frames, focus)")),
                         "REJECTED")


class TheRefusals(unittest.TestCase):
    def test_a_truncated_replay_is_rejected(self):
        self.assertTrue(A.a_truncated_replay_is_rejected())

    def test_a_lost_focus_frame_is_rejected(self):
        self.assertTrue(A.a_lost_focus_frame_is_rejected())

    def test_a_lying_verdict_is_caught(self):
        self.assertTrue(A.a_lying_verdict_is_caught())

    def test_a_lying_verdict_in_the_other_direction_is_also_caught(self):
        # A clean run mislabelled INCOMPLETE is the same drift with the sign flipped, and a
        # reader that only distrusted optimism would miss it.
        self.assertEqual(A.adjudicate(A._rec((10, 10), (10, 10), "INCOMPLETE (frames)")),
                         "DISAGREEMENT")

    def test_a_current_record_without_the_contract_refuses(self):
        self.assertTrue(A.a_current_record_without_the_contract_refuses())

    def test_every_contract_field_is_load_bearing(self):
        # Drop each field in turn; each omission alone must refuse. Otherwise a field is
        # decoration and the contract is narrower than it claims.
        base = ("fpsdemo v1.15 | host H\nmeasurement_class replay\n"
                "replay_trace w.txt bytes %s\nreplay_workload sha256 %s\n"
                "replay_declared 10\nreplay_frames 10/10\nreplay_focus 10/10\n"
                "replay_status COMPLETE\n") % ("a" * 64, "b" * 64)
        self.assertEqual(A.adjudicate(A.parse_record(base)), "ADMITTED")
        for line in ("replay_trace", "replay_workload", "replay_declared",
                     "replay_frames", "replay_focus", "replay_status", "measurement_class"):
            cut = "\n".join(l for l in base.splitlines() if not l.startswith(line)) + "\n"
            self.assertEqual(A.adjudicate(A.parse_record(cut)), "CONTRACT-MISSING", line)

    def test_recompute_refuses_without_its_inputs(self):
        with self.assertRaises(A.AdmitError):
            A.recompute({})


class TheBoundary(unittest.TestCase):
    def test_a_legacy_record_is_exempt_by_version(self):
        self.assertTrue(A.a_legacy_record_is_exempt_by_version())

    def test_the_boundary_is_load_bearing(self):
        self.assertTrue(A.the_boundary_is_load_bearing())

    def test_the_exemption_is_finite_and_counted(self):
        self.assertTrue(A.the_exemption_is_finite_and_counted())

    def test_the_exemption_covers_only_versions_below_the_intro(self):
        self.assertEqual(A._cmp_version("v1.13.3", A.COMPLETENESS_INTRO), -1)
        self.assertEqual(A._cmp_version("v1.14", A.COMPLETENESS_INTRO), -1)
        self.assertEqual(A._cmp_version("v1.15", A.COMPLETENESS_INTRO), 0)
        self.assertEqual(A._cmp_version("v1.15.1", A.COMPLETENESS_INTRO), 1)


class TheCorpus(unittest.TestCase):
    def test_no_committed_record_is_refused(self):
        self.assertTrue(A.no_committed_record_is_refused())

    def test_the_census_is_a_pure_function_of_the_corpus(self):
        self.assertEqual(A.census(), A.census())

    def test_the_scene_matches_its_pinned_golden(self):
        self.assertEqual(A.scene_result("verdicts"), A.golden("verdicts"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(A.AdmitError):
            A.scene_case("no-such-scene")


if __name__ == "__main__":                                       # pragma: no cover
    unittest.main()
