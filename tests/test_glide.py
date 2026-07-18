# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for continuous fixed-point movement (`tools/terrain/glide.py`, T3.18, MMO Stage B) — the
sub-cell REFINEMENT of the URDRDRIVE1 transcript. The SAME input log is folded into Q32.32 sub-cell poses;
the load-bearing claim is that this continuous regime CONTAINS the certified discrete one.

  * REFERENCE — the three pinned scenes reproduce their URDRGLIDE1 digests, deterministically;
  * REFINEMENT BRIDGE (the keystone) — glide's command-boundary poses, floored to cells, reproduce
    `drive`'s certified trajectory BIT-FOR-BIT, for every input log and every subdivision (drive ⊑ glide);
  * SUB=1 IS DRIVE LIFTED — at the coarsest subdivision every micro-step IS a cell, so the floored
    micro-trajectory is exactly `drive`;
  * SUBDIVISION GRANULARITY — sub genuinely subdivides: an unwalled stroll yields 4·sub + 1 micro-poses;
  * DETERMINISM — replaying (start, log, sub) reproduces the fixed-point trajectory bit-for-bit;
  * TAMPER-EVIDENCE — the digest binds the log AND the subdivision; changing either moves it;
  * SUB-CELL WALL — a glide into the ridge stops one micro-step short of the too-high cell and floors to
    `drive`'s wall stop (non-vacuity: glide cannot vault a wall the grid refused);
  * FLOOR-SAMPLED GROUND — the ground under the actor is the EXACT floor-cell height, never interpolated;
  * CONTAINMENT — every sub-cell pose floors to a cell `drive` actually visited (no stray excursion);
  * REFUSAL — an unknown command / empty log / off-grid start / bad subdivision is a typed `GLIDE-REFUSE`.

Requires the frozen Q32.32 radix (`field.ONE`) and the certified terrain (`heightfield`); the gate runs it."""
import itertools
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import glide as G                                                  # noqa: E402
import drive as DR                                                 # noqa: E402
from field import ONE                                              # noqa: E402

_BLANK, _START, _MS = "blank", (2, 8), 16


class Glide(unittest.TestCase):
    def test_scene_goldens(self):
        for name in G.SCENES:
            _pose, dig = G.scene_result(name)
            self.assertEqual(dig, G.golden(name), f"{name}: glide digest drifted")
            self.assertEqual(G.scene_result(name)[1], dig, f"{name}: nondeterministic")

    def test_refinement_bridge(self):
        """THE KEYSTONE: floored command-boundary poses == drive, for every log and every subdivision."""
        checked = 0
        for scene, start, ms in ((_BLANK, _START, _MS), ("mountains", (6, 24), 20)):
            H = G._heights(scene)
            for L in (1, 2, 3):
                for combo in itertools.product("eEnNsSwW", repeat=L):
                    log = "".join(combo)
                    drive_traj = DR.drive(H, start, log, ms)
                    for sub in G.SUBDIV:
                        self.assertEqual(G.floored(G.glide_cells(H, start, log, ms, sub)), drive_traj,
                                         f"refinement broke: scene={scene} log={log!r} sub={sub}")
                        checked += 1
        self.assertEqual(checked, 2 * (8 + 64 + 512) * len(G.SUBDIV),
                         "the bridge must be checked over the whole log × subdivision grid")

    def test_sub1_cell_aligned(self):
        """At the coarsest subdivision the actor is always cell-aligned — every position is an exact
        multiple of ONE (drive lifted onto the fixed-point lattice, no sub-cell offset) — and its cell
        samples floor to drive (the base of the refinement)."""
        H = G._heights(_BLANK)
        for log in ("e", "eenw", "EnWs", "wwww"):
            for fx, fy, _g, _f in G.glide(H, _START, log, _MS, 1):
                self.assertEqual((fx % ONE, fy % ONE), (0, 0),
                                 f"sub=1 must be cell-aligned (no sub-cell offset) for {log!r}")
            self.assertEqual(G.floored(G.glide_cells(H, _START, log, _MS, 1)), DR.drive(H, _START, log, _MS),
                             f"sub=1 cell samples must be drive for {log!r}")

    def test_subdivision_granularity(self):
        H = G._heights(_BLANK)
        for sub in G.SUBDIV:
            micro = G.glide(H, _START, "eeee", _MS, sub)             # unwalled: 4 cells, no truncation
            self.assertEqual(len(micro), 4 * sub + 1,
                             f"sub={sub} must subdivide each cell into {sub} micro-steps")

    def test_determinism(self):
        H = G._heights(_BLANK)
        for sub in (1, 4, 16):
            a = G.glide(H, _START, "eEnwS", _MS, sub)
            b = G.glide(H, _START, "eEnwS", _MS, sub)
            self.assertEqual(a, b, f"glide must be a pure function of its inputs (sub={sub})")

    def test_tamper_evidence(self):
        H = G._heights(_BLANK)
        base = G.glide_digest("s", _START, "eeee", 4, G.glide(H, _START, "eeee", _MS, 4))
        moved_cmd = G.glide_digest("s", _START, "eene", 4, G.glide(H, _START, "eene", _MS, 4))
        moved_sub = G.glide_digest("s", _START, "eeee", 8, G.glide(H, _START, "eeee", _MS, 8))
        self.assertNotEqual(base, moved_cmd, "a changed command must move the digest")
        self.assertNotEqual(base, moved_sub, "a changed subdivision must move the digest (sub is bound)")

    def test_subcell_wall_stops(self):
        scene, start, cmds, ms, sub = G.SCENES["glide_wall"]()
        H = G._heights(scene)
        self.assertEqual(G.floored(G.glide_cells(H, start, cmds, ms, sub)), DR.drive(H, start, cmds, ms),
                         "the sub-cell wall stop must floor to drive's wall stop (glide cannot vault a wall)")
        final_cell = G.cell_of(*G.glide_cells(H, start, cmds, ms, sub)[-1][:2])
        self.assertEqual(final_cell[1], 17, "the actor is walled at y=17")
        self.assertGreater(final_cell[1], 24 - 6 * 2,
                           "y=17 is short of the y=12 an unwalled 6-sprint would reach (a wall was hit)")

    def test_floor_sampled_ground(self):
        H = G._heights(_BLANK)
        for fx, fy, ground, _facing in G.glide(H, _START, "eEnw", _MS, 8):
            self.assertEqual(ground, H[fy >> 32][fx >> 32],
                             "ground must be the EXACT floor-sampled cell height, never interpolated")

    def test_finer_subdivision_no_new_cells(self):
        """Refining the subdivision adds sub-cell resolution but never reaches a cell the coarse
        traversal did not — the sub-cell poses live strictly BETWEEN the same cells (containment)."""
        H = G._heights(_BLANK)
        for log in ("eeee", "eEnwS", "wwnn"):
            coarse = {(fx >> 32, fy >> 32) for fx, fy, _g, _f in G.glide(H, _START, log, _MS, 1)}
            for fx, fy, _g, _f in G.glide(H, _START, log, _MS, 16):
                self.assertIn((fx >> 32, fy >> 32), coarse,
                              f"a finer subdivision floored outside the coarse traversal for {log!r}")

    def test_typed_refusals(self):
        H = G._heights(_BLANK)
        cases = [
            (H, _START, "eXe", _MS, 4),        # unknown command
            (H, _START, "", _MS, 4),           # empty log
            (H, (-1, 0), "ee", _MS, 4),        # off-grid start
            (H, _START, "ee", _MS, 3),         # subdivision not a frozen power of two
            (H, (2, 8.0), "ee", _MS, 4),       # non-int start
            (H, _START, "ee", -1, 4),          # negative max_step
        ]
        for args in cases:
            with self.assertRaises(G.GlideError) as cm:
                G.glide(*args)
            self.assertEqual(cm.exception.code, "GLIDE-REFUSE", f"wrong code for {args[1:]!r}")


if __name__ == "__main__":
    unittest.main()
