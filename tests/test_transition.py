# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""transition_witness (D1 s19) — the first library function, ASCII by the glyph
budget. It is the dual of ≟: it asserts a REAL state transition and packages its
endpoints as a first-class witness store {from, to}. Two laws it must obey and
every test here can break: (1) it NEVER mints Grounded — only ᛞ does; (2) a
zero-delta transition is refused (URDR-DELTA-UNEARNED). A symbol without a red
state is decoration."""
import os
import unittest

from urdr import canon, evaluate
from urdr import values as V
from urdr.compiler import run_program_compiled
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples", "transition_witness.urdr")


def run(src, **kw):
    return evaluate.run_program(src, **kw)


class TestTransitionWitness(unittest.TestCase):
    def test_moved_state_yields_a_witness_store_not_grounded(self):
        v = run("transition_witness(\\st{live: [1,2,3,4]}, \\st{live: [3,4]})")
        self.assertIsInstance(v, V.Store)
        self.assertNotIsInstance(v, V.Grounded)         # it does NOT mint evidence
        self.assertEqual(sorted(v.fields), ["from", "to"])
        self.assertIsInstance(v.fields["from"], V.DigestV)
        self.assertIsInstance(v.fields["to"], V.DigestV)

    def test_endpoints_are_the_actual_digests(self):
        before = run("\\st{live: [1,2,3,4]}")
        after = run("\\st{live: [3,4]}")
        w = run("transition_witness(\\st{live: [1,2,3,4]}, \\st{live: [3,4]})")
        self.assertEqual(w.fields["from"].raw, canon.digest(before))
        self.assertEqual(w.fields["to"].raw, canon.digest(after))

    def test_zero_delta_is_refused(self):
        with self.assertRaises(UrdrError) as ctx:
            run("s := \\st{live: [1,2,3,4]}\ntransition_witness(s, s)")
        self.assertEqual(ctx.exception.code, "URDR-DELTA-UNEARNED")

    def test_it_is_the_dual_of_assert(self):
        # ≟ passes on sameness, dies on difference; transition_witness is the
        # mirror: dies on sameness, witnesses a difference.
        self.assertEqual(evaluate.render(run("=?(\\st{a:1}, \\st{a:1})")),
                         "ᚠ{a: 1}")                       # ≟ same -> returns it
        with self.assertRaises(UrdrError) as ctx:         # tw same -> dies
            run("transition_witness(\\st{a:1}, \\st{a:1})")
        self.assertEqual(ctx.exception.code, "URDR-DELTA-UNEARNED")
        with self.assertRaises(UrdrError) as ctx:         # ≟ diff -> dies
            run("=?(\\st{a:1}, \\st{a:2})")
        self.assertEqual(ctx.exception.code, "URDR-ASSERT")
        self.assertIsInstance(                            # tw diff -> witness
            run("transition_witness(\\st{a:1}, \\st{a:2})"), V.Store)

    def test_prelude_name_is_unshadowable(self):
        with self.assertRaises(UrdrError) as ctx:
            run("transition_witness := 5")
        self.assertEqual(ctx.exception.code, "URDR-REBIND")

    def test_example_seals_and_placements_agree(self):
        with open(EX, "r", encoding="utf-8-sig") as fh:
            src = fh.read()
        v = run(src)
        self.assertIsInstance(v, V.Grounded)             # ᛞ mints, not the witness
        self.assertEqual(canon.hexdigest(v),
                         canon.hexdigest(run_program_compiled(src)))


if __name__ == "__main__":
    unittest.main()
