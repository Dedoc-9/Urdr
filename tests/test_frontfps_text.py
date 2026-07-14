#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the LLM authoring surface (tools/frontfps/frontfps_text.py)."""
import hashlib
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "tools", "frontfps")
if p not in sys.path:
    sys.path.insert(0, p)

import frontfps as FW  # noqa: E402
import frontfps_text as FT  # noqa: E402


def _corpus():
    path = os.path.join(ROOT, "tools", "frontfps", "conformance_text.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split()
                out[k] = v
    return out


class Goldens(unittest.TestCase):
    def test_canonical_text_digest(self):
        d = hashlib.sha256((FT.to_text(FW.demo_crate_solo())
                            + FT.to_text(FW.demo_arena_duel())).encode()).hexdigest()
        self.assertEqual(d, _corpus()["text_canon"])

    def test_fuzz_outcome_digest_pinned(self):
        self.assertEqual(FT.fuzz_digest(), _corpus()["fuzz_outcomes"])


class RoundTrip(unittest.TestCase):
    def test_roundtrip_preserves_digest(self):
        for w in (FW.demo_crate_solo(), FW.demo_arena_duel()):
            self.assertTrue(FT.roundtrip_preserves_digest(w))

    def test_to_text_idempotent(self):
        for w in (FW.demo_crate_solo(), FW.demo_arena_duel()):
            self.assertTrue(FT.to_text_idempotent(w))

    def test_parsed_digest_equals_frontfps_identity(self):
        w = FW.demo_arena_duel()
        dig, _ = FT.admit_text(FT.to_text(w))
        self.assertEqual(dig, FW.world_digest(w))


class Identity(unittest.TestCase):
    def test_prov_line_does_not_move_identity(self):
        self.assertTrue(FT.prov_line_does_not_move_identity(FW.demo_arena_duel()))


class Totality(unittest.TestCase):
    def test_fuzz_is_total_and_nonvacuous(self):
        tags, admits, refuses = FT.fuzz_outcomes()
        self.assertEqual(admits + refuses, len(tags))     # everything landed
        self.assertGreaterEqual(admits, 1)
        self.assertGreaterEqual(refuses, 1)

    def test_no_input_raises_untyped(self):
        """The parser's refusals are total: nasty inputs raise ONLY TextError or
        FpswError, never a bare Python exception (which would propagate + fail)."""
        nasty = ["", "\x00\x00", "vert", "vert a", "edge nomesh 0 1",
                 "actor a m - 0 0 0", "region x", "hitbox h bad.x.y 0 0 0 0 0 0 1",
                 "bone", "\n\n#comment\n", "prov onlyone", "florb"]
        for c in nasty:
            with self.subTest(c=c):
                try:
                    FT.admit_text(c)
                except (FT.TextError, FW.FpswError):
                    pass


class Repair(unittest.TestCase):
    def test_repair_loop_closes(self):
        self.assertTrue(FT.repair_roundtrip())


class AutoArena(unittest.TestCase):
    def test_symmetry_certified(self):
        w, _ = FT.auto_arena(3)
        self.assertTrue(FT.arena_is_mirror_symmetric(w))

    def test_asymmetric_defect_violates(self):
        self.assertFalse(FT.arena_is_mirror_symmetric(FT.auto_arena_defect_asymmetric(3)))


class Refusals(unittest.TestCase):
    def _refused(self, text, why):
        with self.subTest(why=why):
            with self.assertRaises((FT.TextError, FW.FpswError)):
                FT.admit_text(text)

    def test_typed_refusals(self):
        self._refused("vert CRATE 0 0 0\nvert CRATE 1 1 1\n", "uppercase name")
        self._refused("vert crate 0 0 0\nvert crate 1 1 1\nactor a crate - 0 0 0 999999\n", "yaw OOR")
        self._refused("vert crate 0 0 0\nvert crate 1 1 1\nregion 5\nregion 5\n", "non-increasing region")
        self._refused("florb 1 2 3\n", "unknown directive")


if __name__ == "__main__":
    unittest.main()
