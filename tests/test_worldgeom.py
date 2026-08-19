# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""worldgeom (URDRWGM1) — a castle generated from what it IS, on ground it did not choose."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import worldgeom as G                                        # noqa: E402


class TheAuthoredCastle(unittest.TestCase):
    def test_the_corpus_parses(self):
        spec = G.parse_castle(G.load_corpus())
        self.assertEqual(spec["world"], "Blackstone")
        self.assertEqual(spec["zones"], ["bailey", "gate_ward", "inner_ward"])
        self.assertGreaterEqual(len(spec["parts"]), 20)

    def test_every_part_declares_an_archetype(self):
        spec = G.parse_castle(G.load_corpus())
        for name, p in spec["parts"].items():
            self.assertIn(p["archetype"], G.ARCHETYPES, name)

    def test_an_unknown_key_refuses(self):
        self.assertTrue(G.an_unknown_key_refuses())

    def test_an_archetypeless_entity_refuses(self):
        bad = G.load_corpus().replace("  archetype wall\n", "", 1)
        with self.assertRaises(G.WorldgeomError):
            G.parse_castle(bad)


class TheExactShapes(unittest.TestCase):
    def test_the_octagon_is_integer_and_convex(self):
        self.assertTrue(G.the_octagon_is_integer_and_convex())

    def test_the_octagon_is_not_claimed_regular(self):
        # a corner-cut square: the cut is r//3, so opposite runs are unequal by construction
        o = G.octagon(0, 0, 30)
        e0 = abs(o[1][0] - o[0][0])
        e1 = abs(o[2][1] - o[1][1])
        self.assertNotEqual(e0, e1)

    def test_a_concave_plan_refuses(self):
        self.assertTrue(G.a_concave_plan_refuses())


class TheGroundContract(unittest.TestCase):
    def test_everything_is_supported(self):
        self.assertTrue(G.everything_is_supported(G.generate()["built"]))

    def test_every_part_reaches_its_declared_height(self):
        self.assertTrue(G.every_part_reaches_its_height(G.generate()["built"]))

    def test_a_floating_wall_is_caught(self):
        self.assertTrue(G.a_floating_wall_is_caught())

    def test_an_overhanging_merlon_is_caught(self):
        self.assertTrue(G.an_overhanging_merlon_is_caught())

    def test_an_undeclared_overhang_is_caught(self):
        self.assertTrue(G.an_undeclared_overhang_is_caught())

    def test_an_uncarried_overhang_is_caught(self):
        self.assertTrue(G.an_uncarried_overhang_is_caught())

    def test_a_swallowed_wall_is_caught(self):
        self.assertTrue(G.a_swallowed_wall_is_caught())


class TheMilitaryGeometry(unittest.TestCase):
    def test_every_flanking_tower_projects(self):
        proj, flank = G.towers_project(G.generate()["built"])
        self.assertGreater(flank, 0)
        self.assertEqual(proj, flank)

    def test_a_hidden_tower_is_caught(self):
        self.assertTrue(G.a_hidden_tower_is_caught())

    def test_the_gate_passage_is_open(self):
        self.assertTrue(G.gate_passage_is_open(G.generate()["built"]))

    def test_a_blocked_gate_is_caught(self):
        self.assertTrue(G.a_blocked_gate_is_caught())


class TheRecord(unittest.TestCase):
    def test_the_castle_matches_the_golden(self):
        self.assertEqual(G.scene_result("castle"), G.golden("castle"))

    def test_generation_is_deterministic(self):
        self.assertTrue(G.generation_is_deterministic())

    def test_the_committed_record_is_what_generation_produces(self):
        self.assertTrue(G.the_committed_record_is_what_generation_produces())

    def test_a_tampered_record_refuses_its_pin(self):
        with self.assertRaises(Exception):
            G.load_record(G.load_record() + "prism ghost 000000 0 1 4 0 0 1 0 1 1 0 1\n")


if __name__ == "__main__":
    unittest.main()
