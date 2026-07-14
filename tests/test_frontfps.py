#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the URDR-FPSW-1 authoring canon (tools/frontfps/).

Every ordering law is tested from BOTH sides: where invariance is declared the
scramble must not move identity, and where order-is-content is declared the swap
MUST move it — under-claiming an ordering law is as dishonest as over-claiming
one. Refusals assert the exact code (FPSW-REFUSE) per obligation; the two shipped
defects (provenance-folding canon, floor-radius capsule) must break their laws or
the suite is vacuous.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = os.path.join(ROOT, "tools", "frontfps")
if FDIR not in sys.path:
    sys.path.insert(0, FDIR)

import frontfps as FW  # noqa: E402


def _corpus():
    path = os.path.join(FDIR, "conformance_frontfps.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                name, dig = line.split()
                out[name] = dig
    return out


class Goldens(unittest.TestCase):
    def test_pinned_corpus_reproduces(self):
        goldens = _corpus()
        self.assertEqual(sorted(goldens), ["arena_duel", "crate_solo"])
        builders = {"crate_solo": FW.demo_crate_solo, "arena_duel": FW.demo_arena_duel}
        for name, dig in goldens.items():
            with self.subTest(world=name):
                self.assertEqual(FW.world_digest(builders[name]()), dig)

    def test_determinism_twice(self):
        self.assertEqual(FW.world_digest(FW.demo_arena_duel()),
                         FW.world_digest(FW.demo_arena_duel()))


class OrderingLaws(unittest.TestCase):
    def test_noncontent_order_never_moves_identity(self):
        base = FW.demo_arena_duel()
        self.assertEqual(FW.world_digest(FW.scramble_noncontent_order(base)),
                         FW.world_digest(base))

    def test_actor_order_is_content(self):
        base = FW.demo_arena_duel()
        swapped = FW.demo_arena_duel()
        swapped["actors"] = list(reversed(swapped["actors"]))
        self.assertNotEqual(FW.world_digest(swapped), FW.world_digest(base))

    def test_spawn_order_is_content(self):
        base = FW.demo_arena_duel()
        swapped = FW.demo_arena_duel()
        swapped["spawns"] = list(reversed(swapped["spawns"]))
        self.assertNotEqual(FW.world_digest(swapped), FW.world_digest(base))

    def test_bone_order_is_content_within_topology(self):
        """arm_l/arm_r share a parent, so swapping them stays topologically legal —
        and MUST move identity (bones are an authored sequence)."""
        base = FW.demo_arena_duel()
        swapped = FW.demo_arena_duel()
        bones = swapped["rigs"]["biped"]["bones"]
        bones[3], bones[4] = bones[4], bones[3]
        self.assertNotEqual(FW.world_digest(swapped), FW.world_digest(base))


class ProvenanceLaw(unittest.TestCase):
    def test_provenance_never_enters_identity(self):
        base = FW.demo_arena_duel()
        tagged = FW.demo_arena_duel()
        tagged["provenance"] = {"tool": "unit-test", "model": "an-llm", "n": 7}
        self.assertEqual(FW.world_digest(tagged), FW.world_digest(base))

    def test_folding_defect_diverges(self):
        tagged = FW.demo_arena_duel()
        tagged["provenance"] = {"tool": "unit-test"}
        self.assertNotEqual(FW.world_digest_defect_folding_provenance(tagged),
                            FW.world_digest(tagged))


class Refusals(unittest.TestCase):
    def _refused(self, world, why):
        with self.subTest(why=why):
            with self.assertRaises(FW.FpswError) as ctx:
                FW.check_world(world)
            self.assertEqual(ctx.exception.code, "FPSW-REFUSE")

    def test_each_obligation_refuses_typed(self):
        w = FW.demo_arena_duel()
        w["meshes"]["crate"]["verts"][0]["x"] = 1.5
        self._refused(w, "non-integer coordinate")

        w = FW.demo_arena_duel()
        w["meshes"]["crate"]["edges"][0] = (2, 2)
        self._refused(w, "degenerate edge")

        w = FW.demo_arena_duel()
        w["rigs"]["biped"]["bones"][2]["name"] = "root"
        self._refused(w, "duplicate bone name")

        w = FW.demo_arena_duel()
        w["rigs"]["biped"]["bones"][1]["parent"] = 4
        self._refused(w, "forward parent (cycle-shaped)")

        w = FW.demo_arena_duel()
        w["hitboxes"]["biped_torso"]["r"] = 0
        self._refused(w, "zero capsule radius")

        w = FW.demo_arena_duel()
        w["hitboxes"]["biped_torso"]["bone"] = "tail"
        self._refused(w, "missing bone reference")

        w = FW.demo_arena_duel()
        w["actors"][0]["mesh"] = "ghost"
        self._refused(w, "missing mesh reference")

        w = FW.demo_arena_duel()
        w["actors"][0]["yaw"] = 360000
        self._refused(w, "yaw out of range — refused, never normalized")

        w = FW.demo_arena_duel()
        w["regions"] = [0, 0]
        self._refused(w, "non-increasing seams (D16 law)")

        w = FW.demo_arena_duel()
        w["actors"][0]["name"] = "Cover-East"
        self._refused(w, "name outside the closed alphabet")

    def test_no_digest_for_inadmissible_world(self):
        w = FW.demo_arena_duel()
        w["spawns"][0]["team"] = -1
        with self.assertRaises(FW.FpswError):
            FW.world_digest(w)


class AutoCapsule(unittest.TestCase):
    # A crafted cloud whose max perpendicular square (5) is not a perfect square:
    # ceiling and floor radii MUST differ, so the defect can bite.
    CLOUD = [{"x": 0, "y": 0, "z": 0}, {"x": 100, "y": 0, "z": 0},
             {"x": 50, "y": 2, "z": 1}, {"x": 25, "y": -2, "z": -1}]

    def test_containment_certificate_holds(self):
        cap = FW.auto_capsule(self.CLOUD)
        self.assertTrue(FW.capsule_contains_all(self.CLOUD, cap))

    def test_witness_names_the_extremal_vertex(self):
        cap = FW.auto_capsule(self.CLOUD)
        self.assertIn(cap["witness"], (2, 3))  # perp² = 5 at both; first wins
        self.assertEqual(cap["witness"], 2)

    def test_deterministic_twice(self):
        self.assertEqual(FW.auto_capsule(self.CLOUD), FW.auto_capsule(self.CLOUD))

    def test_floor_radius_defect_violates_containment(self):
        bad = FW.auto_capsule_defect_floor_radius(self.CLOUD)
        self.assertFalse(FW.capsule_contains_all(self.CLOUD, bad),
                         "floor-radius defect contained the cloud — the ceiling "
                         "law (and this suite) would be vacuous")

    def test_degenerate_cloud_refused(self):
        with self.assertRaises(FW.FpswError):
            FW.auto_capsule([{"x": 0, "y": 0, "z": 0}])


class ViewSeam(unittest.TestCase):
    def test_view_is_witness_bound_and_nonauthoritative(self):
        w = FW.demo_arena_duel()
        view = FW.to_view(w)
        self.assertEqual(view["witness"], FW.world_digest(w))
        view["actors"][0]["aabb"] = [[0, 0, 0], [0, 0, 0]]  # restyle freely…
        self.assertEqual(FW.world_digest(w), view["witness"])  # …authority unmoved

    def test_view_counts_match_authority(self):
        w = FW.demo_arena_duel()
        view = FW.to_view(w)
        self.assertEqual(view["counts"]["actors"], len(w["actors"]))
        self.assertEqual(view["counts"]["meshes"], len(w["meshes"]))


if __name__ == "__main__":
    unittest.main()
