#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the doc-currency checker (tools/specfreeze/doc_currency.py).

These test the CHECKER LOGIC (does it catch a stale count?), not the live gate totals —
the live consistency is the `doc-currency` gate row's job, since only the running gate knows
its own testsRun and row total."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SPEC = os.path.join(ROOT, "tools", "specfreeze")
if _SPEC not in sys.path:
    sys.path.insert(0, _SPEC)

import doc_currency as DC  # noqa: E402

_LIVE = {"rust": 21, "c": 12, "fals": 519, "rows": 374}


class StaleIsCaught(unittest.TestCase):
    def test_wrong_falsifier_count_flagged(self):
        # A doc snippet quoting the wrong falsifier count must be reported.
        hits = list(DC.scan("behind a %d-test gate" % (_LIVE["fals"] + 5)))
        self.assertTrue(any(k == "fals" and v != _LIVE["fals"] for k, v in hits))

    def test_wrong_placement_count_flagged(self):
        hits = list(DC.scan("%d independent Rust placements" % (_LIVE["rust"] - 1)))
        self.assertTrue(any(k == "rust" and v != _LIVE["rust"] for k, v in hits))

    def test_self_defect_is_caught(self):
        # The in-gate non-vacuity helper: a planted stale count is always caught.
        self.assertTrue(DC.defect_is_caught(_LIVE))


class CurrentPasses(unittest.TestCase):
    def test_correct_counts_not_flagged(self):
        text = ("behind a %d-test gate; %d unit falsifiers / %d rows; "
                "%d independent Rust placements and %d C99 runtimes"
                % (_LIVE["fals"], _LIVE["fals"], _LIVE["rows"], _LIVE["rust"], _LIVE["c"]))
        for key, got in DC.scan(text):
            self.assertEqual(got, _LIVE[key], (key, got))


class GroundTruth(unittest.TestCase):
    def test_placements_counted_from_filesystem(self):
        rs, c = DC.count_placements(ROOT)
        # mechanism, not a second pin: there are more Rust placements than C99, both present.
        self.assertGreater(rs, 0)
        self.assertGreater(c, 0)
        self.assertGreaterEqual(rs, c)


if __name__ == "__main__":
    unittest.main()
