# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for glide resumption (`tools/terrain/splice.py`, T3.19, MMO Stage B foundation) — the
memoryless property that makes continuous movement ROLLBACK-ABLE. A glide's future depends only on its
current Q32.32 pose, not on the history that produced it, so a glide can be cut at any command boundary
and re-glided from the boundary pose — which is exactly what a rollback does.

  * REFERENCE — the three pinned scenes reproduce their URDRSPLICE1 resumed-trajectory digests;
  * SPLICE EQUIVALENCE (the keystone) — splice (glide the prefix, RESUME the suffix from the boundary
    pose) equals glide_cells(full) BIT-FOR-BIT, for every log, every interior split, and every
    subdivision — and the sweep is NON-VACUOUS: it exercises resumes from genuine SUB-CELL boundaries;
  * SUB-CELL RESUME — a resume from a wall-stopped fractional pose (a sprint EAST into a wall, stopped
    3/4 of a cell in) reconstructs the whole; resumption is not limited to cell-aligned cuts;
  * MEMORYLESS — two different histories that reach the SAME pose have the SAME future (the pose is the
    whole state);
  * BOUNDARY IS A GLIDE POSE — the cut point is glide's own command-boundary pose, not a fresh construction;
  * FLOORS TO DRIVE — the spliced continuous trajectory still floors to `drive` (resumption composes with
    the refinement bridge — the certified discrete regime is preserved through the cut);
  * DETERMINISM / TAMPER-EVIDENCE — resume is a pure function; the digest binds the pose and the split;
  * REFUSAL — an off-grid / non-integer resume pose, a bad facing, or a non-interior split is a typed
    `SPLICE-REFUSE`.

Requires the continuous mover (`glide`) and the certified terrain (`heightfield`); the gate runs it."""
import itertools
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import splice as SP                                               # noqa: E402
import glide as GL                                                # noqa: E402
import drive as DR                                                # noqa: E402
from glide import ONE                                             # noqa: E402

_BLANK, _START, _MS = "blank", (2, 8), 16


class Splice(unittest.TestCase):
    def test_scene_goldens(self):
        for name in SP.SCENES:
            dig = SP.scene_result(name)
            self.assertEqual(dig, SP.golden(name), f"{name}: splice digest drifted")
            self.assertEqual(SP.scene_result(name), dig, f"{name}: nondeterministic")

    def test_splice_equivalence(self):
        """THE KEYSTONE: splice(at) == glide_cells(full) for every log, interior split, subdivision —
        and the sweep must actually exercise SUB-CELL boundaries (else the hard case is vacuous)."""
        checked = subcell = 0
        for scene, start, ms in ((_BLANK, _START, _MS), ("mountains", (6, 24), 20),
                                 ("mountains", (2, 0), 20)):          # (2,0): east walls → sub-cell stops
            H = GL._heights(scene)
            for L in (2, 3, 4):
                for combo in itertools.product("eEnNsSwW", repeat=L):
                    log = "".join(combo)
                    full = GL.glide_cells(H, start, log, ms, 4)
                    for at in range(1, L):
                        self.assertEqual(SP.splice(H, start, log, ms, 4, at), full,
                                         f"splice broke: scene={scene} log={log!r} at={at}")
                        b = SP.boundary(H, start, log, ms, 4, at)
                        if b[0] % ONE or b[1] % ONE:
                            subcell += 1
                        checked += 1
        self.assertGreater(checked, 0, "the sweep must run")
        self.assertGreater(subcell, 0, "NON-VACUITY: the sweep must resume from at least one sub-cell boundary")

    def test_subcell_resume(self):
        H = GL._heights("mountains")
        scene, start, cmds, ms, sub, at = SP.SCENES["splice_wall"]()
        b = SP.boundary(H, start, cmds, ms, sub, at)
        self.assertTrue(b[0] % ONE or b[1] % ONE, "splice_wall must cut at a genuine sub-cell boundary")
        self.assertEqual(SP.splice(H, start, cmds, ms, sub, at), GL.glide_cells(H, start, cmds, ms, sub),
                         "a resume from a sub-cell wall-stopped pose must reconstruct the whole")

    def test_memoryless_future_depends_only_on_pose(self):
        H = GL._heights(_BLANK)
        p1 = GL.glide_cells(H, (2, 8), "ee", _MS, 4)[-1]             # two DIFFERENT histories...
        p2 = GL.glide_cells(H, (0, 8), "eeee", _MS, 4)[-1]          # ...reaching the SAME pose
        self.assertEqual(p1, p2, "the two histories must reach the same boundary pose")
        f1 = SP.resume(H, (p1[0], p1[1], p1[3]), "nw", _MS, 4)
        f2 = SP.resume(H, (p2[0], p2[1], p2[3]), "nw", _MS, 4)
        self.assertEqual(f1, f2, "the future depends only on the pose, not the path that reached it")

    def test_boundary_is_glide_pose(self):
        H = GL._heights(_BLANK)
        cells = GL.glide_cells(H, _START, "eEnw", _MS, 4)
        for at in range(len(cells)):
            self.assertEqual(SP.boundary(H, _START, "eEnw", _MS, 4, at), cells[at],
                             f"the boundary at {at} must BE glide's own command-boundary pose")

    def test_splice_floors_to_drive(self):
        H = GL._heights(_BLANK)
        for log, at in (("eeee", 2), ("eEnw", 1), ("wwss", 3)):
            spliced = SP.splice(H, _START, log, _MS, 4, at)
            self.assertEqual(GL.floored(spliced), DR.drive(H, _START, log, _MS),
                             f"the spliced continuous trajectory must still floor to drive for {log!r}")

    def test_resume_determinism(self):
        H = GL._heights(_BLANK)
        pose = (2 * ONE + (ONE >> 2), 8 * ONE, 1)                   # a sub-cell pose
        self.assertEqual(SP.resume(H, pose, "eEn", _MS, 4), SP.resume(H, pose, "eEn", _MS, 4),
                         "resume must be a pure function of its inputs")

    def test_tamper_evidence(self):
        H = GL._heights(_BLANK)
        base = SP.splice_digest("s", _START, "eeee", 4, 2, SP.resume(H, (4 * ONE, 8 * ONE, 1), "ee", _MS, 4))
        moved_pose = SP.splice_digest("s", _START, "eeee", 4, 2, SP.resume(H, (5 * ONE, 8 * ONE, 1), "ee", _MS, 4))
        moved_split = SP.splice_digest("s", _START, "eeee", 4, 3, SP.resume(H, (4 * ONE, 8 * ONE, 1), "ee", _MS, 4))
        self.assertNotEqual(base, moved_pose, "a forged resume pose must move the digest")
        self.assertNotEqual(base, moved_split, "a moved split must move the digest")

    def test_typed_refusals(self):
        H = GL._heights(_BLANK)
        # resume-domain refusals
        for pose, cmds in (((-1, 0, 1), "ee"), ((0, 0, 9), "ee"), ((2 * ONE, 8 * ONE, 1), "eXe")):
            with self.assertRaises(SP.SpliceError) as cm:
                SP.resume(H, pose, cmds, _MS, 4)
            self.assertEqual(cm.exception.code, "SPLICE-REFUSE", f"wrong code for resume {(pose, cmds)!r}")
        # splice non-interior / short-log refusals
        for log, at in (("eeee", 0), ("eeee", 4), ("e", 0)):
            with self.assertRaises(SP.SpliceError) as cm:
                SP.splice(H, _START, log, _MS, 4, at)
            self.assertEqual(cm.exception.code, "SPLICE-REFUSE", f"wrong code for splice {(log, at)!r}")


if __name__ == "__main__":
    unittest.main()
