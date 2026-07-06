# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Lexer hygiene falsifiers: closed alphabet, confusables, glyph⇄digraph identity.
signum ≠ rēs as a security property: a token that merely LOOKS right is rejected."""
import unittest

from urdr import lexer
from urdr.errors import UrdrError


def code_of(fn, *args):
    try:
        fn(*args)
    except UrdrError as err:
        return err.code
    return None


class TestClosedAlphabet(unittest.TestCase):
    def test_unknown_codepoint_rejected(self):
        # An emoji is neither core glyph, ASCII, nor whitespace.
        self.assertEqual(code_of(lexer.lex, "x := 1 \U0001F409"), "URDR-LEX-UNKNOWN")

    def test_unlisted_rune_rejected(self):
        # ᚢ (uruz) is real Elder Futhark but NOT in the v0.1 alphabet: closed means closed.
        self.assertIsNotNone(code_of(lexer.lex, "ᚢ"))


class TestConfusables(unittest.TestCase):
    def test_greek_capital_alpha_named(self):
        # Α (U+0391) imitates Latin A. Must be URDR-LEX-CONFUSABLE, not merely unknown.
        self.assertEqual(code_of(lexer.lex, "a := Α"), "URDR-LEX-CONFUSABLE")

    def test_cyrillic_o_named(self):
        self.assertEqual(code_of(lexer.lex, "о := 1"), "URDR-LEX-CONFUSABLE")

    def test_hygiene_excluded_rune_raidho(self):
        # ᚱ (~Latin R) is excluded for confusability (D1 §2.6), diagnosed as such.
        self.assertEqual(code_of(lexer.lex, "ᚱ"), "URDR-LEX-CONFUSABLE")

    def test_zero_width_space_rejected(self):
        self.assertEqual(code_of(lexer.lex, "a​ := 1"), "URDR-LEX-CONFUSABLE")

    def test_nbsp_rejected(self):
        self.assertEqual(code_of(lexer.lex, "a :=  1"), "URDR-LEX-CONFUSABLE")


class TestGlyphDigraphIdentity(unittest.TestCase):
    """Glyph and ASCII digraph are ONE token type — two spellings, one meaning."""

    PAIRS = [
        ("\U0001202D", r"\an"),   # 𒀭 annotate
        ("ᛞ", r"\ve"),       # ᛞ verify
        ("☽", r"\vw"),       # ☽ view
        ("☿", r"\ed"),       # ☿ edit
        ("↩", r"\am"),       # ↩ anamnesis
        ("ᛝ", r"\di"),       # ᛝ digest
        ("ᚠ", r"\st"),       # ᚠ store
        ("ᛚ", r"\fl"),       # ᛚ flow
        ("λ", r"\fn"),       # λ
        ("↦", "|->"),        # ↦
        ("≔", ":="),         # ≔
        ("∘", r"\o"),        # ∘
        ("Σ", r"\fo"),       # Σ
        ("≟", "=?"),         # ≟
        ("⟨", "<|"),         # ⟨
        ("⟩", "|>"),         # ⟩
        ("≠", "!="),         # ≠
        ("≤", "<="),         # ≤
        ("≥", ">="),         # ≥
    ]

    def test_each_glyph_equals_its_digraph(self):
        for glyph, digraph in self.PAIRS:
            with self.subTest(glyph=glyph):
                toks_g = lexer.lex(glyph)
                toks_d = lexer.lex(digraph)
                self.assertEqual(
                    [t.kind for t in toks_g], [t.kind for t in toks_d],
                    f"{glyph!r} and {digraph!r} must be one token type",
                )

    def test_formatter_canonicalizes_to_glyphs(self):
        src = r"s := \st{x: 1}" + "\n" + r"\vw(s, 'x)" + "\n"
        formatted = lexer.format_source(src)
        self.assertIn("≔", formatted)
        self.assertIn("ᚠ", formatted)
        self.assertIn("☽", formatted)
        # Formatting must not change the token stream.
        self.assertEqual(
            [t.kind for t in lexer.lex(src)],
            [t.kind for t in lexer.lex(formatted)],
        )


if __name__ == "__main__":
    unittest.main()
