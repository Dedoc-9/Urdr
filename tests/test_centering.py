# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Centering / quotient invariant over Z (D1 §18) — exact-integer falsifiers.
The seal certifies ALGEBRAIC facts of M = nI - J only: M·1 = 0 (the all-ones
gauge direction is in the kernel), M² = nM (idempotent up to scale), the scaled
orthogonal split n·x = Mx + Jx with |Mx|²+|Jx|² = n²|x|². The neijuan/gauge
interpretation is docs-only provenance (signum ≠ rēs) and is asserted NOWHERE
here. Every test can fail; the wrong-projection program is required to die."""
import os
import unittest

from urdr import canon, evaluate
from urdr.compiler import run_program_compiled
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples", "centering_quotient.urdr")

SETUP = (
    "n := 5\n"
    "idx := range(n)\n"
    "sumv := \\fn v |-> \\fo(v, 0, \\fn a e |-> a + e)\n"
    "dot := \\fn u v |-> \\fo(idx, 0, \\fn a i |-> a + nth(u, i) * nth(v, i))\n"
    "scale := \\fn k v |-> \\fo(idx, [], \\fn a i |-> push(a, k * nth(v, i)))\n"
    "mcenter := \\fn v |-> \\fo(idx, [], \\fn a i |-> "
    "push(a, n * nth(v, i) - sumv(v)))\n"
    "ones := \\fo(idx, [], \\fn a i |-> push(a, 1))\n"
)


def run(src, **kw):
    return evaluate.run_program(src, **kw)


class TestCenteringSeal(unittest.TestCase):
    def test_example_seals_six_grounded(self):
        with open(EX, "r", encoding="utf-8-sig") as fh:
            v = run(fh.read())
        from urdr import values as V
        self.assertIsInstance(v, V.Grounded)
        self.assertEqual(evaluate.render(v.value), "6")

    def test_wrong_projection_dies(self):
        # claims M^2 = M; the integer operator has M^2 = nM, so it must break
        src = SETUP + "mx := mcenter([3,1,4,1,5])\n=?(mcenter(mx), mx)"
        with self.assertRaises(UrdrError) as ctx:
            run(src)
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")

    def test_all_ones_in_kernel(self):
        # M·1 = 0 for every n we try (the gauge direction is unrewarded)
        for nn in (2, 5, 9):
            src = (f"n := {nn}\nidx := range(n)\n"
                   "sumv := \\fn v |-> \\fo(v, 0, \\fn a e |-> a + e)\n"
                   "ones := \\fo(idx, [], \\fn a i |-> push(a, 1))\n"
                   "zeros := \\fo(idx, [], \\fn a i |-> push(a, 0))\n"
                   "mc := \\fn v |-> \\fo(idx, [], \\fn a i |-> "
                   "push(a, n * nth(v, i) - sumv(v)))\n"
                   "=?(mc(ones), zeros)")
            self.assertEqual(evaluate.render(run(src)),
                             evaluate.render(run(f"n:={nn}\nidx:=range(n)\n"
                                                 "\\fo(idx, [], \\fn a i |-> push(a, 0))")))

    def test_idempotent_up_to_scale_holds_and_true_projection_fails(self):
        base = SETUP + "mx := mcenter([3,1,4,1,5])\n"
        # M(Mx) = n*Mx  holds
        self.assertEqual(
            evaluate.render(run(base + "=?(mcenter(mx), scale(n, mx))")),
            evaluate.render(run(base + "scale(n, mx)")))
        # M(Mx) = Mx  fails (would be a true projection)
        with self.assertRaises(UrdrError) as ctx:
            run(base + "=?(mcenter(mx), mx)")
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")

    def test_pythagoras_split_is_exact_integer(self):
        src = (SETUP +
               "dotm := \\fn u v |-> \\fo(idx, 0, \\fn a i |-> "
               "a + nth(u,i)*nth(v,i))\n"
               "x := [3,1,4,1,5]\ns := sumv(x)\nmx := mcenter(x)\n"
               "jx := scale(s, ones)\n"
               "=?(dotm(mx,mx) + dotm(jx,jx), n*n*dotm(x,x))")
        # returns the RHS (assert passed) — a non-crashing run is the witness
        self.assertEqual(evaluate.render(run(src)), "1300")

    def test_placements_agree_on_the_seal(self):
        with open(EX, "r", encoding="utf-8-sig") as fh:
            src = fh.read()
        self.assertEqual(canon.hexdigest(run(src)),
                         canon.hexdigest(run_program_compiled(src)),
                         "one kernel, every placement")


if __name__ == "__main__":
    unittest.main()
