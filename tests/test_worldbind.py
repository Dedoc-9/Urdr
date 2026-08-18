# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""worldbind (URDRWBD1) — an authored world bound to certified ground."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import worldbind as W                                        # noqa: E402


class TheNumericDoor(unittest.TestCase):
    def test_an_inexact_coordinate_refuses(self):
        self.assertTrue(W.an_inexact_coordinate_refuses())

    def test_a_representable_fraction_admits(self):
        self.assertTrue(W.a_representable_fraction_admits())

    def test_no_float_shaped_token_is_accepted(self):
        self.assertTrue(W.a_float_coordinate_refuses())

    def test_placement_is_injective(self):
        self.assertTrue(W.placement_is_injective())

    def test_parse_exact_never_builds_a_float(self):
        self.assertEqual(W.parse_exact("-3.25"), (-325, 2))
        self.assertEqual(W.parse_exact("14"), (14, 0))


class TheAxisDoor(unittest.TestCase):
    def test_the_declared_map_is_right_handed(self):
        self.assertTrue(W.check_axis_map())

    def test_a_mirrored_axis_map_refuses(self):
        self.assertTrue(W.a_mirrored_axis_map_refuses())

    def test_the_authored_up_axis_becomes_the_runtime_up_axis(self):
        # author (0, 1, 0) is "one unit up"; runtime up is +z
        self.assertEqual(W.map_axes((0, 1, 0)), (0, 0, 1))
        # author +z (toward the viewer) becomes runtime -y (toward the camera)
        self.assertEqual(W.map_axes((0, 0, 1)), (0, -1, 0))


class TheCertifiedGround(unittest.TestCase):
    def test_python_ground_equals_the_rust_record(self):
        self.assertTrue(W.ground_agrees_across_languages())

    def test_every_bound_entity_stands_on_canon_ground(self):
        self.assertTrue(W.bound_entities_stand_on_canon_ground())


class TheAuthoredSpec(unittest.TestCase):
    def test_the_corpus_parses_to_six_entities_and_three_zones(self):
        spec = W.parse_wrk(W.load_corpus())
        self.assertEqual(len(spec["entities"]), 6)
        self.assertEqual(spec["zones"], ["courtyard", "market", "reactor"])
        self.assertEqual(spec["world"], "Fortress")

    def test_reversed_relations_point_from_target_to_entity(self):
        spec = W.parse_wrk(W.load_corpus())
        self.assertIn(("generator", "depends_on", "gate"), spec["relations"])
        self.assertIn(("generator", "powered_by", "turret"), spec["relations"])

    def test_an_unknown_key_refuses(self):
        bad = W.load_corpus().replace("  health 100\n", "  wibble 100\n", 1)
        with self.assertRaises(W.WorldbindError):
            W.parse_wrk(bad)

    def test_a_positionless_entity_cannot_be_bound(self):
        bad = W.load_corpus().replace("  position 14 0 -6\n", "", 1)
        with self.assertRaises(W.WorldbindError):
            W.parse_wrk(bad)

    def test_a_subtile_placement_refuses(self):
        self.assertTrue(W.a_subtile_placement_refuses())


class TheWorldRecord(unittest.TestCase):
    def test_the_bound_world_matches_the_golden(self):
        self.assertEqual(W.scene_result("fortress"), W.golden("fortress"))

    def test_save_is_byte_identical_and_loads(self):
        self.assertTrue(W.round_trip_is_byte_identical())

    def test_content_is_canonical_while_provenance_records_the_source(self):
        self.assertTrue(W.canonical_under_shuffle())

    def test_an_edit_dirties_only_what_it_touches(self):
        self.assertTrue(W.an_edit_dirties_only_what_it_touches())

    def test_a_tampered_chunk_refuses_at_load(self):
        self.assertTrue(W.a_tampered_chunk_refuses_at_load())

    def test_every_chunk_hashes_to_its_manifest_address(self):
        w = W.save()
        self.assertTrue(W.load(w))
        for addr, (raw, dig) in w["chunks"].items():
            self.assertEqual(W.chunk_digest(raw), dig)


if __name__ == "__main__":
    unittest.main()
