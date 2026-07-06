# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Determinism falsifiers (in-process half; the gate adds subprocess isolation)."""
import unittest

from urdr import canon, evaluate
from urdr.errors import UrdrError

PROBE = r"""
base := \st{acc: 0, n: 12}
xs := range(\vw(base, 'n))
total := \fo(xs, \vw(base, 'acc), \fn acc x |-> acc + (x * x + 3))
s1 := \ed(base, 'acc, total)
\vw(s1, 'acc)
"""

PROBE_GLYPHS = """
base ≔ ᚠ{acc: 0, n: 12}
xs ≔ range(☽(base, 'n))
total ≔ Σ(xs, ☽(base, 'acc), λ acc x ↦ acc + (x * x + 3))
s1 ≔ ☿(base, 'acc, total)
☽(s1, 'acc)
"""


class TestDeterminism(unittest.TestCase):
    def test_same_source_same_digest(self):
        d1 = canon.hexdigest(evaluate.run_program(PROBE))
        d2 = canon.hexdigest(evaluate.run_program(PROBE))
        self.assertEqual(d1, d2)

    def test_glyph_and_digraph_sources_are_one_program(self):
        # Two spellings, one token stream, one digest.
        d_ascii = canon.hexdigest(evaluate.run_program(PROBE))
        d_glyph = canon.hexdigest(evaluate.run_program(PROBE_GLYPHS))
        self.assertEqual(d_ascii, d_glyph)

    def test_probe_value_is_542(self):
        # Σ x² for x∈0..11 is 506; plus 3·12 = 542. The number must be possible.
        result = evaluate.run_program(PROBE)
        self.assertEqual(evaluate.render(result), "542")

    def test_store_source_order_irrelevant(self):
        d1 = canon.hexdigest(evaluate.run_program(r"\st{a: 1, b: 2}"))
        d2 = canon.hexdigest(evaluate.run_program(r"\st{b: 2, a: 1}"))
        self.assertEqual(d1, d2)

    def test_i64_wrap_is_defined(self):
        src = "9223372036854775807 + 1"
        result = evaluate.run_program(src)
        self.assertEqual(evaluate.render(result), "-9223372036854775808")

    def test_fuel_exhaustion_is_deterministic_error(self):
        with self.assertRaises(UrdrError) as ctx:
            evaluate.run_program(PROBE, fuel=10)
        self.assertEqual(ctx.exception.code, "URDR-FUEL")

    # -- α-normalization (R1a) ------------------------------------------------
    # R0 shipped test_alpha_sensitivity_is_pinned, which pinned the honest R0
    # behavior (α-SENSITIVE canon) and instructed: "when α-normalization lands
    # this test must be UPDATED, not deleted." This is that update.

    def test_alpha_equivalence_after_normalization(self):
        # λ canonical form uses positional (De Bruijn) indices for λ-bound names,
        # in canon only: α-equivalent lambdas are ONE value, one digest.
        dx = canon.hexdigest(evaluate.run_program(r"\fn x |-> x"))
        dy = canon.hexdigest(evaluate.run_program(r"\fn y |-> y"))
        self.assertEqual(dx, dy)

    def test_alpha_normalization_is_not_structure_blind(self):
        # Non-vacuity: structurally different lambdas must still differ.
        d1 = canon.hexdigest(evaluate.run_program(r"\fn x y |-> x"))
        d2 = canon.hexdigest(evaluate.run_program(r"\fn x y |-> y"))
        self.assertNotEqual(d1, d2)

    def test_alpha_normalization_respects_shadowing(self):
        # λx↦λx↦x ≡α λa↦λb↦b (innermost binder wins) and ≢α λa↦λb↦a.
        d_shadow = canon.hexdigest(evaluate.run_program(r"\fn x |-> \fn x |-> x"))
        d_inner = canon.hexdigest(evaluate.run_program(r"\fn a |-> \fn b |-> b"))
        d_outer = canon.hexdigest(evaluate.run_program(r"\fn a |-> \fn b |-> a"))
        self.assertEqual(d_shadow, d_inner)
        self.assertNotEqual(d_shadow, d_outer)

    def test_free_names_stay_named_in_canon(self):
        # Only λ-BOUND names normalize; a lambda over a different captured top-level
        # binding is a different closure and must digest differently.
        d_a = canon.hexdigest(evaluate.run_program("k := 1\n" + r"\fn x |-> x + k"))
        d_b = canon.hexdigest(evaluate.run_program("k := 2\n" + r"\fn x |-> x + k"))
        self.assertNotEqual(d_a, d_b)

    def test_digest_is_sha256_shaped(self):
        d = canon.hexdigest(evaluate.run_program("1 + 1"))
        self.assertEqual(len(d), 64)
        int(d, 16)  # must be hex


if __name__ == "__main__":
    unittest.main()
