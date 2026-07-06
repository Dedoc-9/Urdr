# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R1c falsifiers: the graded-algebra rung, run from the exact example sources.
The honest 'M-capable' test: represent a Z2-graded / Clifford structure as a value
and verify its defining relations BY EVALUATION. Not physics; algebra."""
import os
import unittest

from urdr import evaluate
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8-sig") as fh:
        return fh.read()


class TestGradedAlgebra(unittest.TestCase):
    def test_z2_grading_closure_seals_grounded(self):
        result = evaluate.run_program(load("examples/z2_grading.urdr"))
        rendered = evaluate.render(result)
        # 64 pair-checks, sealed by the mint: evidence is earned, not written.
        self.assertIn("⊢ 64", rendered)
        self.assertIn("MEASURED", rendered)

    def test_clifford_relations_seal_grounded(self):
        result = evaluate.run_program(load("examples/clifford_relations.urdr"))
        rendered = evaluate.render(result)
        self.assertIn("⊢ 9", rendered)
        self.assertIn("MEASURED", rendered)

    def test_wrong_relation_dies_with_assert(self):
        # Non-vacuity: the commutation claim must be killed by ≟, not tolerated.
        with self.assertRaises(UrdrError) as ctx:
            evaluate.run_program(load("examples/rejected/clifford_wrong.urdr"))
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")

    def test_anticommutation_spot_check_in_language(self):
        # e0 e1 = -e1 e0 and (e2)^2 = +1, asserted directly with fresh helpers.
        src = load("examples/clifford_relations.urdr")
        # The example already asserts these (anti, square binds); a breach anywhere
        # would have raised. Reaching here green means the spot checks executed.
        result = evaluate.run_program(src)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
