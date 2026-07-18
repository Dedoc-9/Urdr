# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for directed-reachability structural anti-cheat (`tools/terrain/dirward.py`, T3.26, MMO Stage E)
— the topological anti-cheat refined from UNDIRECTED reachability (URDRWARD1/2) to DIRECTED reachability, so a
ONE-WAY cliff is modelled honestly (you may descend but not climb).

  * REFERENCE — the two pinned scenarios reproduce their URDRWARD3 digests, deterministically;
  * REACHABILITY ASYMMETRIC (non-vacuity) — on the cliff, `can_reach(top, bottom)` holds and `can_reach(
    bottom, top)` does not; `reach_asymmetry` is positive — there is real one-way structure;
  * SYMMETRIC TERRAIN COLLAPSES — on flat terrain `reach_asymmetry` is 0 and `num_scc == betti0`, so the
    directed refinement is honest where there is nothing one-way to see;
  * HONEST DESCENT ADMITS — an actor dropping off the ledge (top -> bottom) admits;
  * CLIMB-BACK ONE-WAY — a bare claim to be back on top (bottom -> top) is `WARD-ONEWAY`;
  * UNDIRECTED WARDEN FALSE-REFUSES THE DESCENT (headline 1) — `warden.admit_position(top, bottom)` REFUSES
    the LEGAL descent `WARD-UNREACH` (it would kick an honest player), while `dirward.admit_move` admits it;
  * UNDIRECTED WARDEN CONFLATES ONE-WAY WITH WALL (headline 2) — `warden.admit_position` returns the SAME
    `WARD-UNREACH` for the cliff climb-back and for a genuine wall; `dirward` separates `WARD-ONEWAY` from
    `WARD-UNREACH`;
  * WALL UNREACHABLE — across a genuine impassable wall, `admit_move` is `WARD-UNREACH` (no directed path
    either way);
  * HONEST DESCENT GLIDE — a real `glide` descent trajectory admits kinematically (composes `glide`);
  * REFUSAL — every refusal is a typed `WARD-REFUSE` with a sub-code; a malformed claim is `WARD-MALFORMED`.

Composes the mover (`glide`) and the undirected warden (`warden`) it refines; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import dirward as D                                              # noqa: E402
import warden as W                                              # noqa: E402
import glide as GL                                              # noqa: E402


class Dirward(unittest.TestCase):
    def setUp(self):
        self.cliff = D._cliff_field()
        self.wall = D._wall_field()
        self.flat = tuple(tuple(0 for _ in range(16)) for _ in range(16))
        self.ms = D._MS
        self.top, self.bottom = D._TOP, D._BOTTOM

    def test_scene_goldens(self):
        for name in D.SCENES:
            dig = D.scene_result(name)
            self.assertEqual(dig, D.golden(name), f"{name}: dirward digest drifted")
            self.assertEqual(D.scene_result(name), dig, f"{name}: nondeterministic")

    def test_reachability_asymmetric(self):
        self.assertTrue(D.can_reach(self.cliff, self.top, self.bottom, self.ms), "the descent must be reachable")
        self.assertFalse(D.can_reach(self.cliff, self.bottom, self.top, self.ms), "the climb must NOT be reachable")
        self.assertGreater(D.reach_asymmetry(self.cliff, self.ms), 0, "the cliff must have one-way structure")

    def test_symmetric_terrain_collapses(self):
        self.assertEqual(D.reach_asymmetry(self.flat, self.ms), 0, "flat terrain has no one-way structure")
        self.assertEqual(D.num_scc(self.flat, self.ms), W.betti0(self.flat, self.ms), "SCC must collapse to betti0")

    def test_honest_descent_admits(self):
        self.assertEqual(D.admit_move(self.cliff, self.top, self.bottom, self.ms), "WARD-OK",
                         "dropping off the ledge is a legal move")

    def test_climb_back_oneway(self):
        with self.assertRaises(W.WardError) as cm:
            D.admit_move(self.cliff, self.bottom, self.top, self.ms)
        self.assertEqual(cm.exception.sub, "WARD-ONEWAY", "climbing back up a one-way cliff must be WARD-ONEWAY")

    def test_undirected_false_refuses_descent(self):
        """HEADLINE 1 — the undirected warden refuses the LEGAL descent; the directed warden admits it."""
        with self.assertRaises(W.WardError) as cm:                # undirected: top and bottom look disconnected
            W.admit_position(self.cliff, self.top, self.bottom, self.ms)
        self.assertEqual(cm.exception.sub, "WARD-UNREACH", "the undirected warden false-refuses the descent")
        self.assertEqual(D.admit_move(self.cliff, self.top, self.bottom, self.ms), "WARD-OK",
                         "the directed warden admits the descent the undirected one wrongly refused")

    def test_undirected_conflates_oneway_and_wall(self):
        """HEADLINE 2 — the undirected warden returns the same code for a one-way cliff and a solid wall."""
        def undirected(anchor, claim, fld):
            try:
                return W.admit_position(fld, anchor, claim, self.ms)
            except W.WardError as exc:
                return exc.sub

        def directed(anchor, claim, fld):
            try:
                return D.admit_move(fld, anchor, claim, self.ms)
            except W.WardError as exc:
                return exc.sub
        # undirected: identical WARD-UNREACH for the cliff climb-back and the genuine wall
        self.assertEqual(undirected(self.bottom, self.top, self.cliff),
                         undirected((2, 8), (14, 8), self.wall), "undirected conflates the two")
        # directed: distinguishes them
        self.assertEqual(directed(self.bottom, self.top, self.cliff), "WARD-ONEWAY")
        self.assertEqual(directed((2, 8), (14, 8), self.wall), "WARD-UNREACH")

    def test_wall_unreachable(self):
        with self.assertRaises(W.WardError) as cm:
            D.admit_move(self.wall, (2, 8), (14, 8), self.ms)
        self.assertEqual(cm.exception.sub, "WARD-UNREACH", "across a genuine wall there is no directed path")

    def test_honest_descent_glide(self):
        g = GL.glide_cells(self.cliff, self.top, "eeee", self.ms, 4)  # glide east, off the ledge
        gcells = tuple((p[0] >> 32, p[1] >> 32) for p in g)
        self.assertEqual(W.admit_trajectory(self.cliff, gcells, self.ms), "WARD-OK",
                         "an honest glide descent must admit kinematically")
        self.assertEqual(D.admit_move(self.cliff, gcells[0], gcells[-1], self.ms), "WARD-OK",
                         "and its endpoints must be directed-reachable")

    def test_typed_refusals(self):
        with self.assertRaises(W.WardError) as cm:                # malformed cell
            D.admit_move(self.cliff, self.bottom, (99, 99), self.ms)
        self.assertEqual(cm.exception.sub, "WARD-MALFORMED")
        try:
            D.admit_move(self.cliff, self.bottom, self.top, self.ms)
        except W.WardError as exc:
            self.assertEqual(exc.code, "WARD-REFUSE")
            self.assertEqual(exc.sub, "WARD-ONEWAY")


if __name__ == "__main__":
    unittest.main()
