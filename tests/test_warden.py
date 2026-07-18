# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for structural anti-cheat (`tools/terrain/warden.py`, T3.24, MMO Stage E) — a claimed
trajectory or position is ADMITTED or a typed WARD-REFUSE; a claim that could not have happened is a
certified refusal, not a heuristic flag.

  * REFERENCE — the two pinned scenarios reproduce their URDRWARD1 digests, deterministically;
  * BARRIER TOPOLOGY (non-vacuity) — the wall-split world genuinely has β₀ = 3 components; the topological
    check has real structure to certify against;
  * HONEST ADMITS — an honest walk, and a real `glide` trajectory within a component, both admit;
  * WALL TUNNEL REFUSED — a step that climbs the wall is `WARD-TUNNEL` (the kinematic step law);
  * TELEPORT REFUSED — a diagonal or > 2-cell jump is `WARD-TELEPORT`;
  * UNREACHABLE REFUSED — a bare position across the barrier is `WARD-UNREACH`;
  * STRUCTURAL BEATS REPLAY (the headline) — the across-barrier teleport is refused from the field's
    component structure ALONE, with no trajectory to inspect — a certificate a per-step kinematic check
    cannot produce;
  * REACHABILITY SYMMETRIC — the undirected walkable components are symmetric (a ⟷ b);
  * REFUSAL — every refusal is a typed `WARD-REFUSE` with a sub-code; a malformed claim is `WARD-MALFORMED`.

Composes the mover (`glide`) and exact connected components (β₀ = rank H₀); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import warden as W                                                # noqa: E402
import glide as GL                                                # noqa: E402


class Warden(unittest.TestCase):
    def setUp(self):
        self.fld = W._barrier_field()
        self.ms = W._MS

    def test_scene_goldens(self):
        for name in W.SCENES:
            dig = W.scene_result(name)
            self.assertEqual(dig, W.golden(name), f"{name}: warden digest drifted")
            self.assertEqual(W.scene_result(name), dig, f"{name}: nondeterministic")

    def test_barrier_topology(self):
        self.assertEqual(W.betti0(self.fld, self.ms), 3, "the wall must split the world into 3 components")

    def test_honest_admits(self):
        self.assertEqual(W.admit_trajectory(self.fld, ((2, 8), (3, 8), (4, 8), (5, 8)), self.ms), "WARD-OK")
        g = GL.glide_cells(self.fld, (2, 8), "eee", self.ms, 4)   # an honest glide within the west component
        gcells = tuple((p[0] >> 32, p[1] >> 32) for p in g)
        self.assertEqual(W.admit_trajectory(self.fld, gcells, self.ms), "WARD-OK", "an honest glide must admit")

    def test_tunnel_refused(self):
        self.assertEqual(W.step_kind(self.fld, (7, 8), (8, 8), self.ms), "WARD-TUNNEL")
        with self.assertRaises(W.WardError) as cm:
            W.admit_trajectory(self.fld, ((7, 8), (8, 8)), self.ms)
        self.assertEqual(cm.exception.sub, "WARD-TUNNEL", "climbing the wall must be a tunnel refusal")

    def test_teleport_refused(self):
        self.assertEqual(W.step_kind(self.fld, (2, 8), (5, 8), self.ms), "WARD-TELEPORT")   # 3 cells
        self.assertEqual(W.step_kind(self.fld, (2, 8), (3, 9), self.ms), "WARD-TELEPORT")   # diagonal
        with self.assertRaises(W.WardError) as cm:
            W.admit_trajectory(self.fld, ((2, 8), (5, 8)), self.ms)
        self.assertEqual(cm.exception.sub, "WARD-TELEPORT")

    def test_unreachable_refused(self):
        with self.assertRaises(W.WardError) as cm:
            W.admit_position(self.fld, (2, 8), (12, 8), self.ms)
        self.assertEqual(cm.exception.sub, "WARD-UNREACH", "an across-barrier position must be unreachable")

    def test_structural_beats_replay(self):
        """The across-barrier teleport is refused from the component structure ALONE — no trajectory."""
        self.assertGreaterEqual(W.betti0(self.fld, self.ms), 2, "the field must be genuinely disconnected")
        self.assertFalse(W.reachable(self.fld, (2, 8), (12, 8), self.ms), "west and east are different components")
        self.assertTrue(W.reachable(self.fld, (2, 8), (6, 8), self.ms), "same-side must stay reachable")
        with self.assertRaises(W.WardError):                      # refused with only (anchor, claim), no path
            W.admit_position(self.fld, (2, 8), (12, 8), self.ms)

    def test_reachability_symmetric(self):
        for a, b in (((2, 8), (12, 8)), ((2, 8), (6, 8)), ((0, 0), (15, 15))):
            self.assertEqual(W.reachable(self.fld, a, b, self.ms), W.reachable(self.fld, b, a, self.ms),
                             f"undirected reachability must be symmetric for {a},{b}")

    def test_typed_refusals(self):
        with self.assertRaises(W.WardError) as cm:                # empty claim
            W.admit_trajectory(self.fld, (), self.ms)
        self.assertEqual(cm.exception.sub, "WARD-MALFORMED")
        # every cheat refusal carries the WARD-REFUSE code with a sub-code
        try:
            W.admit_trajectory(self.fld, ((7, 8), (8, 8)), self.ms)
        except W.WardError as exc:
            self.assertEqual(exc.code, "WARD-REFUSE")
            self.assertEqual(exc.sub, "WARD-TUNNEL")


if __name__ == "__main__":
    unittest.main()
