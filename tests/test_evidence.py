# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Evidence-transition falsifiers (D1 s19). The pipeline as a native source of
evidence: an action purchases evidence iff a verifier observes a real reduction
in the live-hypothesis set (>= 1 bit iff 2|kept| <= |before|). The mint stays
singular -- ᛞ alone constructs Grounded; a zero-delta transition cannot be
sealed. Integer only; float bits are the voi_gate tool's job (provenance)."""
import os
import unittest

from urdr import canon, evaluate
from urdr import values as V
from urdr.compiler import run_program_compiled
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples", "evidence_transition.urdr")

FILTER = ("obs := \\fn xs t |-> \\fo(xs, [], \\fn a e |-> ?(e >= t, push(a, e), a))\n"
          "before := [1, 2, 3, 4]\n")


def run(src, **kw):
    return evaluate.run_program(src, **kw)


class TestEvidenceTransition(unittest.TestCase):
    def test_transition_seals_grounded_on_gain(self):
        with open(EX, "r", encoding="utf-8-sig") as fh:
            v = run(fh.read())
        self.assertIsInstance(v, V.Grounded)
        self.assertEqual(evaluate.render(v.value), "1")

    def test_one_bit_boundary_bites(self):
        # 4 -> 2 (>= 1 bit) purchased; 4 -> 3 (< 1 bit) not purchased
        gain = FILTER + "kept := obs(before, 3)\n2 * len(kept) <= len(before)"
        none = FILTER + "kept := obs(before, 2)\n2 * len(kept) <= len(before)"
        # t=3 keeps {3,4}=2 -> 2*2<=4 true ; t=2 keeps {2,3,4}=3 -> 2*3<=4 false
        self.assertEqual(evaluate.render(run(gain)), "1")
        self.assertEqual(evaluate.render(run(none)), "0")

    def test_zero_delta_cannot_be_sealed_yields_conflict(self):
        # the mint DECLINES: a falsy evidence verifier yields ↯, never Grounded
        src = ("c := \\an <| IMPLEMENTED , DECLARED |> 0\n"
               "\\ve(\\fn v |-> v = 1, c)")
        v = run(src)
        self.assertIsInstance(v, V.Conflict)
        self.assertNotIsInstance(v, V.Grounded)

    def test_no_gain_assertion_dies(self):
        src = FILTER + ("kept := obs(before, 0)\n"          # keeps all 4
                        "=?(?(2 * len(kept) <= len(before), 1, 0), 1)")
        with self.assertRaises(UrdrError) as ctx:
            run(src)
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")

    def test_measuring_the_unbuilt_is_unlicensed(self):
        # requesting MEASURED on a not-built (SCOPED) claim: the mint refuses
        src = ("c := \\an <| SCOPED , DECLARED |> 1\n"
               "\\ve(\\fn v |-> v = 1, c)")
        with self.assertRaises(UrdrError) as ctx:
            run(src)
        self.assertEqual(ctx.exception.code, "URDR-VERIFY-UNLICENSED")

    def test_placements_agree(self):
        with open(EX, "r", encoding="utf-8-sig") as fh:
            src = fh.read()
        self.assertEqual(canon.hexdigest(run(src)),
                         canon.hexdigest(run_program_compiled(src)))


if __name__ == "__main__":
    unittest.main()
