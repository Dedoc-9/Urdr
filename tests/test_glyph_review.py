# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Glyph-review falsifiers (D1 §20). Two things must hold and both can break:
(1) the glyph is a LOSSLESS alias — three spellings, one digest; (2) the review
can REJECT a bad candidate (URDR-GLYPH-NOT-EARNED). A review that cannot reject
would be decoration."""
import os
import sys
import unittest

from urdr import canon, evaluate

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from glyph_review import review_glyph, EARNED, NOT_EARNED  # noqa: E402


def digest(sym):
    return canon.hexdigest(evaluate.run_program(
        sym + "(\\st{a: 1}, \\st{a: 2})"))


class TestLosslessAlias(unittest.TestCase):
    def test_three_spellings_one_digest(self):
        d = digest("transition_witness")
        self.assertEqual(digest("⟿"), d)       # glyph
        self.assertEqual(digest("\\tw"), d)     # digraph
        # a real transition still witnesses through the glyph spelling
        v = evaluate.run_program("⟿(\\st{a: 1}, \\st{a: 2})")
        from urdr import values as V
        self.assertIsInstance(v, V.Store)
        self.assertEqual(sorted(v.fields), ["from", "to"])


class TestGlyphReviewCanReject(unittest.TestCase):
    OK = dict(lossless=True, digraph="\\tw",
              attested="U+27FF long rightwards squiggle arrow (math notation)",
              assigned="verified transition witness")

    def test_earned_candidate_passes(self):
        lossless = digest("⟿") == digest("transition_witness")
        v, why = review_glyph("⟿", **{**self.OK, "lossless": lossless})
        self.assertEqual(v, EARNED, why)

    def test_rejects_confusable(self):
        v, why = review_glyph("Α", **self.OK)          # Greek Alpha ~ 'A'
        self.assertEqual(v, NOT_EARNED)
        self.assertTrue(any("confusable" in r for r in why))

    def test_rejects_non_lossless(self):
        v, _ = review_glyph("⟿", **{**self.OK, "lossless": False})
        self.assertEqual(v, NOT_EARNED)

    def test_rejects_core_glyph_collision(self):
        v, why = review_glyph("↦", **self.OK)          # already mapsto
        self.assertEqual(v, NOT_EARNED)
        self.assertTrue(any("core glyph" in r for r in why))

    def test_rejects_missing_provenance(self):
        v, _ = review_glyph("⇝", **{**self.OK, "attested": ""})
        self.assertEqual(v, NOT_EARNED)


if __name__ == "__main__":
    unittest.main()
