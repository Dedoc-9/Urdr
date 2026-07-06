# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R3a falsifiers: the verbose keyword profile. Three spellings — glyph, digraph,
word — one token stream, one digest. A profile is spelling, never semantics."""
import unittest

from urdr import canon, evaluate, lexer
from urdr.errors import UrdrError

GLYPH = """
s ≔ ᚠ{x: 1, y: 2}
d0 ≔ ᛝ(s)
t ≔ ☿(s, 'x, 5)
back ≔ ≟(ᛝ(↩(t)), d0)
7 ᛚ (λ n ↦ n + len(ᛃ(t)))
"""

WORDS = """
s := store{x: 1, y: 2}
d0 := digest(s)
t := edit(s, 'x, 5)
back := expect(digest(recall(t)), d0)
7 flow (fn n |-> n + len(lineage(t)))
"""

DIGRAPH = r"""
s := \st{x: 1, y: 2}
d0 := \di(s)
t := \ed(s, 'x, 5)
back := =?(\di(\am(t)), d0)
7 \fl (\fn n |-> n + len(\pv(t)))
"""


class TestVerboseProfile(unittest.TestCase):
    def test_three_spellings_one_digest(self):
        dg = canon.hexdigest(evaluate.run_program(GLYPH))
        dw = canon.hexdigest(evaluate.run_program(WORDS))
        dd = canon.hexdigest(evaluate.run_program(DIGRAPH))
        self.assertEqual(dg, dw)
        self.assertEqual(dw, dd)

    def test_verify_and_annot_words(self):
        src = """
c := annot <| IMPLEMENTED , DECLARED |> 42
g := verify(fn v |-> v = 42, c)
[grounded(g), evidence(g)]
"""
        rendered = evaluate.render(evaluate.run_program(src))
        self.assertIn("MEASURED", rendered)

    def test_compose_word_after(self):
        src = "inc := fn x |-> x + 1\ndbl := fn x |-> x + x\n(dbl after inc)(3)"
        self.assertEqual(evaluate.render(evaluate.run_program(src)), "8")

    def test_fold_word(self):
        src = "fold(range(5), 0, fn acc x |-> acc + x)"
        self.assertEqual(evaluate.render(evaluate.run_program(src)), "10")

    def test_reserved_words_cannot_be_bound(self):
        for word in ("view", "edit", "store", "fold", "flow", "expect",
                     "recall", "digest", "lineage", "verify", "annot", "after",
                     "fn"):
            with self.subTest(word=word):
                with self.assertRaises(UrdrError) as ctx:
                    evaluate.run_program(f"{word} := 1")
                self.assertEqual(ctx.exception.code, "URDR-PARSE")

    def test_formatter_words_to_glyphs(self):
        out = lexer.format_source("t := edit(store{x: 1}, 'x, 2)\nexpect(digest(recall(t)), digest(store{x: 1}))")
        for glyph in ("☿", "ᚠ", "≟", "ᛝ", "↩", "≔"):
            self.assertIn(glyph, out)
        # formatting must not change the token stream
        src = WORDS
        self.assertEqual([t.kind for t in lexer.lex(src)],
                         [t.kind for t in lexer.lex(lexer.format_source(src))])


if __name__ == "__main__":
    unittest.main()
