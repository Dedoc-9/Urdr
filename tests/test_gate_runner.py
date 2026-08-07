# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifier for the gate runner's own progress reporting.

The counter must be per-call. It already was — the class lived inside `unit_tests`, so
each call rebound it — but only BY PLACEMENT, and hoisting the class to module scope
would have leaked the count silently. A factory makes the property checkable without
running 2133 tests to observe it.
"""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _verify_module():
    argv, sys.argv = sys.argv, ["verify.py"]
    try:
        spec = importlib.util.spec_from_file_location("_verify_probe",
                                                      os.path.join(ROOT, "verify.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = argv


class TheProgressCounterIsPerCall(unittest.TestCase):
    def test_two_result_classes_do_not_share_state(self):
        """THE HARDENING. A second `unit_tests` call in the same process must restart at
        zero, whatever refactor moves the class around."""
        V = _verify_module()
        a, b = V._progress_result_class(10), V._progress_result_class(10)
        self.assertEqual(a.counter[1], 0)
        self.assertEqual(b.counter[1], 0)
        a.counter[1] = 99
        a.counter[0] = "tests.something"
        self.assertEqual(b.counter[1], 0, "the counter is shared between calls")
        self.assertIsNone(b.counter[0])

    def test_a_fresh_class_starts_at_zero_after_use(self):
        """Non-vacuity: the first assertion would pass on a class that never counts.
        Advance one, then build another and require it to be fresh."""
        V = _verify_module()
        used = V._progress_result_class(10)
        used.counter[1] += 7
        self.assertEqual(used.counter[1], 7)
        self.assertEqual(V._progress_result_class(10).counter[1], 0)

    def test_the_progress_stream_is_stderr_never_stdout(self):
        """stdout is the CERTIFIED transcript; a progress byte there would break the
        byte-identity the gate's whole determinism claim rests on."""
        src = open(os.path.join(ROOT, "verify.py"), encoding="utf-8").read()
        blk = src[src.index("def _progress_result_class("):]
        blk = blk[:blk.index("class Gate:")]
        self.assertIn("sys.stderr.write", blk)
        self.assertNotIn("sys.stdout", blk)
        self.assertNotIn("print(", blk)


if __name__ == "__main__":
    unittest.main(verbosity=2)
