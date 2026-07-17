# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the MEASURED movement transcript (`tools/terrain/drive.py`, T3.11) — the
authoritative trajectory is a pure exact-integer function of (initial pose, input log) over the terrain.

  * REFERENCE — the three pinned transcripts reproduce their URDRDRIVE1 digests ×2;
  * DETERMINISM — replaying the same (start, input log) reproduces the trajectory bit-for-bit;
  * PURE FOLD — `drive` is exactly the fold of `step` over the input log;
  * GAIT — sprint (uppercase) covers twice the ground of walk on the same directions (load-bearing);
  * SPRINT IS GATED — a sprint whose second cell is a rise > MAX_STEP moves one cell and stops (the
    per-cell step gate applies under sprint, not just walk — sprint does not vault a wall);
  * STEP LAW — a cell is entered iff its rise is at most MAX_STEP (stance's law), at the exact boundary;
  * TAMPER-EVIDENCE — a forged / replayed / reordered command moves the transcript digest;
  * REFUSAL — unknown command, empty log, off-grid start, negative step, bool/float are DRIVE-REFUSE;
  * NO-DIVISION — the source has no `/`, `//`, `%` operator (cross-placement is structural)."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import drive as D                                                # noqa: E402


def _heights(scene):
    import heightfield as HF
    return HF.scene_digest(HF.SCENES[scene]())[1]


class Drive(unittest.TestCase):
    def test_scene_goldens(self):
        for name in D.SCENES:
            _final, dig = D.scene_result(name)
            self.assertEqual(dig, D.golden(name), f"{name}: transcript digest drifted")
            self.assertEqual(D.scene_result(name)[1], dig, f"{name}: nondeterministic")

    def test_determinism_replay(self):
        scene, start, cmds, ms = D.stroll()
        H = _heights(scene)
        self.assertEqual(D.drive(H, start, cmds, ms), D.drive(H, start, cmds, ms),
                         "replaying the input log must reproduce the trajectory bit-for-bit")

    def test_trajectory_is_pure_fold(self):
        scene, start, cmds, ms = D.sprint_run()
        H = _heights(scene)
        traj = D.drive(H, start, cmds, ms)
        pose = (start[0], start[1], H[start[1]][start[0]], D._FACE[D._parse(cmds[0])[0]])
        expect = [pose]
        for c in cmds:
            pose = D.step(H, pose, c, ms)
            expect.append(pose)
        self.assertEqual(traj, tuple(expect), "drive must be exactly the fold of step over the log")

    def test_gait_load_bearing(self):
        scene, start, _c, ms = D.stroll()                        # stroll + sprint_run share start/terrain
        H = _heights(scene)
        walk = D.drive(H, start, "eeee", ms)
        sprint = D.drive(H, start, "EEEE", ms)
        self.assertEqual(sprint[-1][0] - start[0], 2 * (walk[-1][0] - start[0]),
                         "sprint must cover twice the ground of walk on the same directions")

    def test_sprint_is_gated_by_wall(self):
        scene, start, cmds, ms = D.sprint_wall()
        H = _heights(scene)
        traj = D.drive(H, start, cmds, ms)
        dist = [abs(traj[i + 1][0] - traj[i][0]) + abs(traj[i + 1][1] - traj[i][1]) for i in range(len(cmds))]
        self.assertIn(1, dist, "a sprint whose second cell is a wall must move exactly one cell (partial stride)")
        self.assertIn(0, dist, "past the wall the actor is fully stopped")
        self.assertTrue(all(d <= 2 for d in dist), "a sprint never moves more than two cells")

    def test_step_law_boundary(self):
        # a cell is entered iff its rise is at most MAX_STEP — the exact stance boundary, under drive.
        heights = ((0, 0, 0), (0, 10, 0), (0, 0, 0))             # centre cell (1,1) rises 10
        atlas_start = (0, 1)                                     # value 0; east neighbour (1,1) rises 10
        self.assertEqual(D.drive(heights, atlas_start, "e", 10)[-1][:2], (1, 1), "rise == MAX_STEP enters")
        self.assertEqual(D.drive(heights, atlas_start, "e", 9)[-1][:2], (0, 1), "rise > MAX_STEP is walled")

    def test_tamper_evidence(self):
        scene, start, _c, ms = D.stroll()
        H = _heights(scene)
        base = D.transcript_digest("t", start, "enen", D.drive(H, start, "enen", ms))
        flip = D.transcript_digest("t", start, "enEn", D.drive(H, start, "enEn", ms))   # cmd 3 walk->sprint
        reorder = D.transcript_digest("t", start, "nene", D.drive(H, start, "nene", ms))  # reordered
        self.assertNotEqual(base, flip, "flipping one command must move the transcript digest")
        self.assertNotEqual(base, reorder, "reordering commands must move the transcript digest")

    def test_blocked_walk_stops_not_clamps(self):
        heights = ((0, 0), (0, 9))                               # (0,1)->(1,1) rise 9
        self.assertEqual(D.drive(heights, (0, 1), "e", 4)[-1][:2], (0, 1), "a blocked walk stays put, never clamps past the wall")

    def test_typed_refusals_total(self):
        H = _heights("blank")
        cases = [((2, 8), "eeXe", 16), ((2, 8), "", 16), ((-1, 0), "ee", 16),
                 ((2, 8), "ee", -1), ((2, 8), "ee", True), ((0.0, 8), "ee", 16)]
        for start, cmds, ms in cases:
            with self.assertRaises(D.DriveError) as cm:
                D.drive(H, start, cmds, ms)
            self.assertEqual(cm.exception.code, "DRIVE-REFUSE", f"wrong code for {(start, cmds, ms)!r}")

    def test_no_division_operators(self):
        import tokenize
        forbidden = {"/", "//", "%", "/=", "//=", "%="}
        bad = []
        with open(D.__file__, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.OP and tok.string in forbidden:
                    bad.append((tok.start, tok.string))
        self.assertEqual(bad, [], f"division/modulo operators found in drive.py: {bad}")


if __name__ == "__main__":
    unittest.main()
