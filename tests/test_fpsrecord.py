# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fpsrecord (URDRFPR1) — the demo's workload records as gate-read artifacts."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import fpsrecord as F                                        # noqa: E402


class TheRecords(unittest.TestCase):
    def test_every_record_hashes_to_its_pin(self):
        for i in range(len(F.RECORDS)):
            self.assertTrue(F.load(i))

    def test_a_flipped_byte_refuses(self):
        self.assertTrue(F.a_flipped_byte_refuses())

    def test_the_activity_figures_derive_from_the_bytes(self):
        act = F.activity(F.parse_trace(F.load(2)))
        self.assertEqual(act, {"frames": 1145, "keyed": 757, "moused": 310,
                               "zero_prefix": 236})

    def test_an_unknown_trace_version_refuses(self):
        self.assertTrue(F.an_unknown_trace_version_refuses())

    def test_the_one_frame_record_is_a_witness_not_a_workload(self):
        self.assertTrue(F.a_one_frame_trace_is_not_a_workload())


class TheBinding(unittest.TestCase):
    def test_every_chain_binds_to_its_trace(self):
        traces, chains, _log = F._admit_all()
        for t, c in sorted(F.CHAIN_OF.items()):
            self.assertTrue(F.bind(traces[t], chains[c]))

    def test_a_foreign_chain_refuses_binding(self):
        self.assertTrue(F.a_foreign_chain_refuses_binding())

    def test_the_zero_prefix_law_is_not_vacuous(self):
        chain = F.parse_chain(F.load(6))
        inside = [d for f, d in chain if f < 236]
        self.assertEqual(len(inside), 3)
        self.assertTrue(all(d == F.ZERO_CONSTANT for d in inside))


class TheCrossOsAgreement(unittest.TestCase):
    def test_host_and_container_chains_agree_digest_for_digest(self):
        _traces, chains, log = F._admit_all()
        self.assertTrue(F.crossos(log, chains[F.CHAIN_OF[F.LOG_TRACE]]))

    def test_one_edited_digest_reddens_the_agreement(self):
        self.assertTrue(F.a_mismatched_chain_reddens())

    def test_a_truncated_log_refuses(self):
        self.assertTrue(F.a_truncated_log_refuses())

    def test_an_anonymous_log_refuses(self):
        text = F.load(F.NAMED_LOG).replace("host ROG-Ally-X-Z2-Extreme", "host -")
        with self.assertRaises(F.FpsrecordError):
            F.parse_named_log(text)


class TheGoldens(unittest.TestCase):
    def test_both_scenes_reproduce_their_goldens(self):
        for name in ("records", "laws"):
            self.assertEqual(F.scene_result(name), F.golden(name))


if __name__ == "__main__":
    unittest.main()
