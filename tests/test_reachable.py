# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `reachable` (URDRRCH1) — a gate must admit something its own producer can make.

L65 named this detector and deliberately left it unbuilt so a successor would TEST the rule rather
than inherit it. The successor inherited it: `rollbench` v1's host string could never satisfy the
gate it was handed to. These check the law, both plants, and the distinction that IS the detector —
a witness is PRODUCED, never written, because a human can type what a machine cannot emit."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import reachable as RC                                       # noqa: E402
import rollbench as RB                                       # noqa: E402
import sealframe as SF                                       # noqa: E402


class TheLaw(unittest.TestCase):
    def test_every_registered_gate_admits_what_its_producer_makes(self):
        self.assertTrue(RC.every_gate_admits_what_its_producer_makes())

    def test_every_entry_is_reachable(self):
        for name, v in RC.census().items():
            with self.subTest(name):
                self.assertEqual(v, RC.REACHABLE)

    def test_the_register_is_not_empty(self):
        self.assertGreaterEqual(len(RC.names()), 8)

    def test_an_unknown_pair_refuses(self):
        with self.assertRaises(RC.ReachError):
            RC.verdict("nope")


class BothPlantsBite(unittest.TestCase):
    """The two halves fail in opposite directions, so both are planted separately."""

    def test_the_exact_defect_it_was_built_for(self):
        """`rollbench` v1.1's positional argv reader. Re-plant it and the DOCUMENTED invocation
        yields conditions the live door refuses, so the pair reads UNREACHABLE — the repair
        existed in the library and no operator could reach it from the command line."""
        self.assertTrue(RC.the_detector_bites())

    def test_a_gate_that_accepts_everything_is_caught(self):
        """Without this half the register would certify a door that was never shut."""
        self.assertTrue(RC.a_gate_that_accepts_everything_is_caught())

    def test_the_two_plants_produce_different_verdicts(self):
        """UNREACHABLE and VACUOUS are different findings and a detector that fused them would
        report an unsatisfiable gate as an open one."""
        real_p, real_g = RB.parse_argv, SF.conditions_sufficient
        try:
            RB.parse_argv = lambda argv: {"out": "", "note": "", "machine": "m",
                                          "power": "", "scheduler": ""}
            self.assertEqual(RC.verdict(RC.names()[0]), RC.UNREACHABLE)
        finally:
            RB.parse_argv = real_p
        try:
            SF.conditions_sufficient = lambda _c, _i: ()
            self.assertEqual(RC.verdict(RC.names()[0]), RC.VACUOUS)
        finally:
            SF.conditions_sufficient = real_g
        self.assertEqual(RC.verdict(RC.names()[0]), RC.REACHABLE)

    def test_a_producer_that_raises_refuses_rather_than_scoring(self):
        real = RB.parse_argv
        try:
            RB.parse_argv = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
            with self.assertRaises(RC.ReachError):
                RC.verdict(RC.names()[0])
        finally:
            RB.parse_argv = real


class TheWitnessIsProducedNotWritten(unittest.TestCase):
    def test_the_register_holds_callables(self):
        """The distinction that IS the detector: `named_host_ok` would have passed any check that
        let a human type the expected string. A human can type it; the machine could not, and the
        machine was the caller."""
        self.assertTrue(RC.the_witness_is_produced_not_written())

    def test_a_hand_written_witness_would_have_hidden_the_defect(self):
        """Exhibited rather than argued: the literal passes while the producer's output does not."""
        self.assertTrue(SF.named_host_ok(SF.NAMED_HOST))
        import platform
        self.assertFalse(SF.named_host_ok(
            f"{platform.node()} | {platform.system()} {platform.release()}"))


class TheRegisterIsAFloor(unittest.TestCase):
    def test_it_says_so_checkably(self):
        """`does_not_show` made checkable: there are strictly more typed refusal codes in the tree
        than registered pairs, so the boundary cannot quietly stop being true."""
        more, ncodes, npairs = RC.the_register_is_a_floor_not_a_survey()
        self.assertTrue(more)
        self.assertGreater(ncodes, npairs)

    def test_an_unregistered_gate_is_unchecked_not_proved(self):
        codes = RC.the_register_is_a_floor_not_a_survey()[1]
        self.assertGreater(codes, len(RC.names()))


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in RC.SCENES:
            with self.subTest(name):
                self.assertEqual(RC.scene_result(name), RC.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(RC.reachable_digest(), RC.reachable_digest())

    def test_the_payload_is_readable(self):
        self.assertIn("REACHABLE", RC.scene_case("census"))
        self.assertIn("floor=True", RC.scene_case("census"))
        self.assertIn("unreachable=True", RC.scene_case("plants"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RC.ReachError):
            RC.scene_case("nope")
        with self.assertRaises(RC.ReachError):
            RC.golden("nope")


if __name__ == "__main__":
    unittest.main()
