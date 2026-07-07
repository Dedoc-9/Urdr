# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Foreign-placement-oracle falsifiers (R6a). The point that CAN be measured
cargo-free: the harness admits a placement that matches the reference and
REDDENS on one that does not (the oracle can go red on a foreign placement).
What is NOT claimed: that an independent Rust impl agrees — that is SPECULATIVE
until urdr-core-rs exists (no Rust toolchain here)."""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import foreign_oracle as F  # noqa: E402

URDR = os.path.join(ROOT, "urdr.py")
EXAMPLE = os.path.join(ROOT, "examples", "lens_roundtrip.urdr")


class TestForeignPlacementOracle(unittest.TestCase):
    def test_agreeing_placement_is_admitted(self):
        # a placement that reproduces the reference digest is admitted. (Here the
        # "foreign" command is urdr.py itself — this proves the HARNESS compares
        # correctly, not that an independent impl agrees.)
        verdict, name, ref, got = F.admit(
            EXAMPLE, [sys.executable, URDR, "run"], name="self")
        self.assertEqual(verdict, "ADMITTED")
        self.assertEqual(ref, got)

    def test_diverging_placement_is_refused(self):
        # the RED STATE: a foreign placement emitting a wrong digest must diverge
        bad = os.path.join(tempfile.mkdtemp(), "bad_placement.py")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("import sys\nprint('digest: ' + '0'*64)\n")
        self.addCleanup(lambda: os.path.exists(bad) and os.remove(bad))
        verdict, name, ref, got = F.admit(
            EXAMPLE, [sys.executable, bad], name="rust")
        self.assertEqual(verdict, F.DIVERGENCE)      # URDR-PLACEMENT-DIVERGENCE
        self.assertNotEqual(ref, got)

    def test_placement_with_no_digest_is_an_error(self):
        silent = os.path.join(tempfile.mkdtemp(), "silent.py")
        with open(silent, "w", encoding="utf-8") as fh:
            fh.write("print('hello, no digest here')\n")
        self.addCleanup(lambda: os.path.exists(silent) and os.remove(silent))
        with self.assertRaises(ValueError):
            F.admit(EXAMPLE, [sys.executable, silent], name="broken")


if __name__ == "__main__":
    unittest.main()
