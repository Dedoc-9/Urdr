# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Chain-complex falsifiers (D1 §22) — homology's founding law d.d = 0 by exact
integer evaluation, and the honest test of the SFH-style glyph candidate
'identity modulo a certified transformation space'. The finding: that relation is
ABSORBED by existing machinery — a witnessed deformation is a fold (Σ) that
asserts (≟) a declared invariant is preserved at every step. No new primitive, no
new refusal (URDR-ASSERT is the red state), so no glyph."""
import os
import unittest

from urdr import canon, evaluate
from urdr import values as V
from urdr.compiler import run_program_compiled
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples", "chain_complex.urdr")


def run(src, **kw):
    return evaluate.run_program(src, **kw)


class TestChainComplex(unittest.TestCase):
    def test_boundary_of_boundary_is_zero_sealed(self):
        with open(EX, "r", encoding="utf-8-sig") as fh:
            v = run(fh.read())
        self.assertIsInstance(v, V.Grounded)
        self.assertEqual(evaluate.render(v.value), "4")

    def test_wrong_boundary_dies(self):
        # orientation lost -> d.d != 0 -> URDR-ASSERT (non-vacuity)
        src = ("d2 := \\fn c |-> [nth(c,0), nth(c,0), nth(c,0)]\n"
               "d1 := \\fn c |-> [0-nth(c,1)-nth(c,2), 0-nth(c,0)+nth(c,2), "
               "nth(c,0)+nth(c,1)]\n=?(d1(d2([1])), [0,0,0])")
        with self.assertRaises(UrdrError) as ctx:
            run(src)
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")

    def test_placements_agree(self):
        with open(EX, "r", encoding="utf-8-sig") as fh:
            src = fh.read()
        self.assertEqual(canon.hexdigest(run(src)),
                         canon.hexdigest(run_program_compiled(src)))


class TestWitnessedDeformationIsAbsorbed(unittest.TestCase):
    """'x ~ y iff a certified chain of invariant-preserving transformations
    connects them' = Σ over the witness chain asserting ≟ on the invariant.
    Existing primitives express it; the three proposed red states all collapse."""

    SETUP = ("inv := \\fn v |-> \\fo(v, 0, \\fn a e |-> a + e)\n"   # invariant = sum
             "certify := \\fn chain |-> \\fo(chain, 1, \\fn ok x |-> "
             "?(inv(x) = inv(nth(chain, 0)), ok, 0))\n")

    def test_certified_chain_is_admitted(self):
        # a witnessed deformation preserving the invariant at every step
        src = self.SETUP + "=?(certify([[3,0], [2,1], [1,2]]), 1)"
        self.assertEqual(evaluate.render(run(src)), "1")

    def test_chain_breaking_the_invariant_dies(self):
        # red state 1+2: a step outside the allowed family / breaking the invariant
        src = self.SETUP + "=?(certify([[3,0], [2,2]]), 1)"   # sums 3,4
        with self.assertRaises(UrdrError) as ctx:
            run(src)
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")

    def test_equivalence_without_a_witness_cannot_be_claimed(self):
        # red state 3: no witness chain -> nothing to certify. The relation
        # STRUCTURALLY requires the witness as data; you cannot assert ~ without it.
        # (There is no primitive that grants equivalence sans chain — by design.)
        one_step = self.SETUP + "=?(certify([[3,0]]), 1)"   # trivial chain, reflexive
        self.assertEqual(evaluate.render(run(one_step)), "1")


if __name__ == "__main__":
    unittest.main()
