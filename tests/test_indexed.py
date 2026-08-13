# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""indexed (URDRIDX1) — a gated module appears in the tree's own index.

Twenty consecutive rungs were absent from `tools/terrain/README.md`, the file whose own heading is
"The ladder, module by module" — roughly a thousand gate rows of work — while `doc-currency` and
`doc-staleness` were both GREEN, because a count is cheap to sweep and a paragraph is not."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import indexed as IX                                         # noqa: E402


class TheLaw(unittest.TestCase):
    def test_this_arc_is_indexed(self):
        ok, n, missing = IX.this_arc_is_indexed()
        self.assertTrue(ok, f"unindexed: {missing}")
        self.assertEqual(n, 20)

    def test_the_gated_set_is_large_and_derived(self):
        self.assertGreater(len(IX.staged_modules()), 50)
        self.assertTrue(IX.the_gated_set_is_read_from_the_gate())

    def test_a_source_without_stage_order_refuses(self):
        with self.assertRaises(IX.IndexedError) as ctx:
            IX.staged_modules(source="nothing here\n")
        self.assertEqual(ctx.exception.code, "INDEXED-REFUSE")


class ThePlantsBite(unittest.TestCase):
    def test_a_removed_entry_reddens(self):
        self.assertTrue(IX.a_removed_entry_reddens())

    def test_a_bare_word_is_not_coverage(self):
        """Otherwise the check is a spell-checker: the English word `entry`, or a path containing
        `attest`, would count as an entry."""
        self.assertTrue(IX.a_bare_word_is_not_coverage())

    def test_an_empty_index_is_fully_unindexed(self):
        self.assertEqual(len(IX.unindexed(text="")), len(IX.staged_modules()))
        self.assertEqual(IX.verdict(text=""), IX.UNINDEXED)


class TheRatchet(unittest.TestCase):
    def test_the_debt_has_not_grown(self):
        held, u = IX.the_debt_has_not_grown()
        self.assertTrue(held)
        self.assertLessEqual(u, IX.DEBT_CEILING)

    def test_the_ceiling_sits_at_the_live_reading(self):
        """A ceiling with slack is one the next gated module fits under without anyone deciding."""
        self.assertTrue(IX.the_ceiling_is_the_live_reading())
        self.assertEqual(IX.counts()[2], IX.DEBT_CEILING)

    def test_the_counts_add_up(self):
        g, c, u = IX.counts()
        self.assertEqual(g, c + u)


class TheBound(unittest.TestCase):
    def test_naming_is_not_describing(self):
        """An index that is nothing but backticked filenames satisfies this law completely —
        demonstrated, so the bound cannot be mistaken for modesty."""
        self.assertTrue(IX.naming_is_not_describing())

    def test_it_ranges_over_terrain_only(self):
        """A law living in `netcode`, `physics` or `specfreeze` is outside this check entirely."""
        for m in IX.staged_modules():
            self.assertTrue(os.path.exists(
                os.path.join(_ROOT, "tools", "terrain", m + ".py")))


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in IX.SCENES:
            with self.subTest(name):
                self.assertEqual(IX.scene_result(name), IX.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(IX.indexed_digest(), IX.golden("indexed"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(IX.IndexedError):
            IX.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
