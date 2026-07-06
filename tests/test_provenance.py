# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R1d falsifiers: ᛃ (jera) — the provenance walk. Lineage is already part of a
store's identity (D1 §8); ᛃ makes it observable: ancestor digests, nearest first."""
import unittest

from urdr import evaluate, lexer
from urdr.errors import UrdrError


def run(src, **kw):
    return evaluate.run_program(src, **kw)


def code_of(src):
    try:
        run(src)
    except UrdrError as err:
        return err.code
    return None


class TestProvenance(unittest.TestCase):
    def test_root_lineage_is_empty(self):
        out = run(r"len(\pv(\st{x: 1}))")
        self.assertEqual(evaluate.render(out), "0")

    def test_lineage_nearest_first_and_matches_digests(self):
        src = r"""
s0 := \st{x: 1}
s1 := \ed(s0, 'x, 2)
s2 := \ed(s1, 'y, 3)
line := \pv(s2)
a := =?(len(line), 2)
b := =?(nth(line, 0), \di(s1))
=?(nth(line, 1), \di(s0))
"""
        run(src)  # any breach raises URDR-ASSERT

    def test_lineage_agrees_with_anamnesis(self):
        src = r"""
s0 := \st{x: 1}
s2 := \ed(\ed(s0, 'x, 2), 'x, 3)
=?(nth(\pv(s2), 1), \di(\am(\am(s2))))
"""
        run(src)

    def test_prov_wants_store(self):
        self.assertEqual(code_of(r"\pv(1)"), "URDR-TYPE-RUN")
        self.assertEqual(code_of(r"\pv([1, 2])"), "URDR-TYPE-RUN")

    def test_glyph_digraph_identity(self):
        self.assertEqual([t.kind for t in lexer.lex("ᛃ")],
                         [t.kind for t in lexer.lex(r"\pv")])

    def test_formatter_emits_jera(self):
        self.assertIn("ᛃ", lexer.format_source(r"\pv(\st{x: 1})"))


if __name__ == "__main__":
    unittest.main()
