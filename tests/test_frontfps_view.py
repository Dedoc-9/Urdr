#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the view stream (tools/frontfps/frontfps_view.py)."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "tools", "frontfps")
if p not in sys.path:
    sys.path.insert(0, p)

import frontfps_view as FV  # noqa: E402


def _corpus():
    path = os.path.join(ROOT, "tools", "frontfps", "conformance_view2.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split()
                out[k] = v
    return out


class Goldens(unittest.TestCase):
    def test_stream_digest_reproduces_twice(self):
        d1 = FV.stream_digest()
        d2 = FV.stream_digest()
        self.assertEqual(d1, _corpus()["view_stream"])
        self.assertEqual(d1, d2)

    def test_stream_bytes_pinned(self):
        self.assertEqual(FV.stream_bytes(), int(_corpus()["view_bytes"]))


class Recompute(unittest.TestCase):
    def test_recompute_law(self):
        self.assertTrue(FV.recompute_matches())

    def test_decode_reproduces_bound_witness(self):
        traj = FV.demo_trajectory()
        dec = FV.decode_stream(FV.encode_stream(traj, FV.CANON_SHIFT))
        for (seq, wit, _disp), snap in zip(dec, traj):
            self.assertEqual(wit, FV.authority_witness(snap))


class NoFeedback(unittest.TestCase):
    def test_witness_invariant_under_presentation(self):
        self.assertTrue(FV.witness_invariant_under_presentation())

    def test_fold_defect_moves_the_witness(self):
        """The no-feedback law is non-vacuous: folding presentation into the
        witness MUST make it presentation-dependent (the gate can redden)."""
        self.assertTrue(FV.defect_folds_presentation_into_witness())

    def test_display_is_a_lossy_projection(self):
        self.assertTrue(FV.display_is_lossy())


class Refusals(unittest.TestCase):
    def _refused(self, stream, why):
        with self.subTest(why=why):
            with self.assertRaises(FV.ViewError) as ctx:
                FV.decode_stream(stream)
            self.assertEqual(ctx.exception.code, "VIEW-REFUSE")

    def test_delta_missing_base_refused(self):
        self._refused(FV.demo_stream_missing_base(), "delta references base never sent")

    def test_delta_first_refused(self):
        self._refused(FV.demo_stream_delta_first(), "stream opens on a delta")

    def test_bad_magic_refused(self):
        self._refused(FV.demo_stream_bad_magic(), "bad magic")

    def test_valid_stream_decodes(self):
        dec = FV.decode_stream(FV.encode_stream(FV.demo_trajectory(), FV.CANON_SHIFT))
        self.assertEqual(len(dec), 4)


if __name__ == "__main__":
    unittest.main()
