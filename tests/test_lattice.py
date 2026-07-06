# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Rhombohedral lattice falsifiers (user-directed conversion, D1 §12b).
Assigned meaning of 'rhombohedral diagonal consolidation': the C3 orbit-average
v + Rv + R²v of ANY vector lands on the invariant diagonal subspace of the
rhombohedral (FCC-primitive) lattice. Integer algebra checked by evaluation;
crystallography inspires, physics is claimed nowhere."""
import os
import unittest

from urdr import canon, compiler, evaluate
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8-sig") as fh:
        return fh.read()


class TestRhombohedralLattice(unittest.TestCase):
    def test_lattice_relations_seal_grounded(self):
        result = evaluate.run_program(load("examples/rhombo_lattice.urdr"))
        rendered = evaluate.render(result)
        self.assertIn("⊢ 11", rendered)   # 11 relations, sealed at the mint
        self.assertIn("MEASURED", rendered)

    def test_wrong_fixation_claim_dies(self):
        # Non-vacuity: claiming the rotation FIXES a basis vector must die.
        with self.assertRaises(UrdrError) as ctx:
            evaluate.run_program(load("examples/rejected/rhombo_wrong.urdr"))
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")

    def test_both_placements_agree_on_the_lattice(self):
        src = load("examples/rhombo_lattice.urdr")
        d_ref = canon.hexdigest(evaluate.run_program(src))
        d_com = canon.hexdigest(compiler.run_program_compiled(src))
        self.assertEqual(d_ref, d_com)

    def test_consolidation_of_arbitrary_vector_in_language(self):
        # Orbit-sum of (9, -4, 1) has all components equal to 9-4+1 = 6.
        src = """
rot := fn v |-> [nth(v, 2), nth(v, 0), nth(v, 1)]
vadd := fn u v |-> [nth(u, 0) + nth(v, 0), nth(u, 1) + nth(v, 1), nth(u, 2) + nth(v, 2)]
w := [9, -4, 1]
expect(vadd(vadd(w, rot(w)), rot(rot(w))), [6, 6, 6])
"""
        evaluate.run_program(src)  # ≟ raises on breach


if __name__ == "__main__":
    unittest.main()
