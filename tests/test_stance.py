# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the MEASURED stance consumer (`tools/terrain/stance.py`, T3.9) — the grounded,
integer, first-person walk over the URDRHF1 heightfield.

  * REFERENCE — the pinned walks reproduce their URDRSTANCE1 digests ×2;
  * GROUNDED — the ground profile is EXACTLY `heights[y][x]` along the walked path (standing is
    reading the field, not a model of it);
  * FIRST — the result is the FIRST step blocked by an unclimbable rise (every earlier rise ≤
    MAX_STEP, and the blocking step's rise > MAX_STEP when it is not a clear);
  * MAX_STEP — on ONE path a high MAX_STEP clears and a low MAX_STEP is walled (load-bearing);
  * GRADES — plain_walk + ridge_clear clear (result == len); ridge_blocked is walled (< len);
  * BLIND — the walk-through-walls defect (ignore the step gate) changes where a walled walk ends —
    the terrain gate is load-bearing;
  * REFUSAL — start off the grid, a path that leaves the grid, an unknown move, a negative step, a
    non-positive actor, an empty path, bool/float params are all STANCE-REFUSE;
  * NO-DIVISION — the source has no `/`, `//`, `%` operator (cross-placement is structural)."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import stance as S                                                # noqa: E402
import heightfield as HF                                          # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


class Stance(unittest.TestCase):
    def test_scene_goldens(self):
        for name in S.SCENES:
            r, d = S.scene_result(name)
            self.assertEqual(d, S.golden(name), f"{name}: digest drifted")
            self.assertEqual(S.scene_result(name)[1], d, f"{name}: nondeterministic")

    def test_profile_is_exact_ground(self):
        # GROUNDED: the footing at each cell is exactly the heightfield value there.
        for name in S.SCENES:
            scene, start, moves, ms, ph = S.SCENES[name]()
            heights = _heights(scene)
            _r, prof = S.walk_trace(heights, start, moves, ms, ph)
            x, y = start
            expect = [heights[y][x]]
            for m in moves:
                dx, dy = S.DIRS[m]
                x += dx
                y += dy
                expect.append(heights[y][x])
            self.assertEqual(prof, tuple(expect), f"{name}: profile is not the exact ground under the path")

    def test_first_blocked_is_first(self):
        for name in S.SCENES:
            scene, start, moves, ms, ph = S.SCENES[name]()
            r, prof = S.walk_trace(_heights(scene), start, moves, ms, ph)
            for i in range(r):                                    # every walked step was climbable
                self.assertLessEqual(prof[i + 1] - prof[i], ms, f"{name}: an earlier rise exceeded MAX_STEP")
            if r < len(moves):                                    # the stop is a real wall
                self.assertGreater(prof[r + 1] - prof[r], ms, f"{name}: the blocking step is not a wall")

    def test_max_step_load_bearing(self):
        scene, start, moves, _ms, ph = S.ridge_clear()           # ridge_clear + ridge_blocked share this path
        heights = _heights(scene)
        self.assertEqual(S.walk(heights, start, moves, 40, ph), len(moves), "a high MAX_STEP must clear")
        self.assertLess(S.walk(heights, start, moves, 20, ph), len(moves), "a low MAX_STEP must be walled")

    def test_cleared_and_walled_grades(self):
        for name in ("plain_walk", "ridge_clear"):
            scene, start, moves, ms, ph = S.SCENES[name]()
            self.assertEqual(S.walk(_heights(scene), start, moves, ms, ph), len(moves), f"{name} must clear")
        scene, start, moves, ms, ph = S.ridge_blocked()
        self.assertLess(S.walk(_heights(scene), start, moves, ms, ph), len(moves), "ridge_blocked must be walled")

    def test_blind_defect_diverges(self):
        # ignoring the step gate (walk through walls) must change where a walled walk ends
        scene, start, moves, ms, ph = S.ridge_blocked()
        heights = _heights(scene)
        real = S.walk(heights, start, moves, ms, ph)
        blind = S.walk(heights, start, moves, ms, ph, blind=True)
        self.assertNotEqual(blind, real, "the walk-through-walls defect did not diverge (the gate is load-bearing)")

    def test_off_grid_start_refusal(self):
        with self.assertRaises(S.StanceError) as cm:
            S.walk(_heights("blank"), (-1, 0), "EE", 8)
        self.assertEqual(cm.exception.code, "STANCE-REFUSE")

    def test_path_leaves_grid_refusal(self):
        with self.assertRaises(S.StanceError) as cm:
            S.walk(_heights("blank"), (2, 8), "E" * 16, 8)       # exits the east edge of the 16-wide grid
        self.assertEqual(cm.exception.code, "STANCE-REFUSE")

    def test_typed_refusals_total(self):
        H = _heights("blank")
        cases = [
            ((2, 8), "EX", 8, 1),                                 # unknown move
            ((2, 8), "EE", -1, 1),                                # negative max_step
            ((2, 8), "EE", 8, 0),                                 # non-positive actor
            ((2, 8), "", 8, 1),                                   # empty path
            ((2, 8), "EE", True, 1),                              # bool max_step
            ((0.0, 8), "EE", 8, 1),                               # non-integer start
        ]
        for start, moves, ms, ph in cases:
            with self.assertRaises(S.StanceError) as cm:
                S.walk(H, start, moves, ms, ph)
            self.assertEqual(cm.exception.code, "STANCE-REFUSE", f"wrong code for {(start, moves, ms, ph)!r}")

    def test_no_division_operators(self):
        # STRUCTURAL cross-placement guarantee — no `/`, `//`, or `%` operator in stance.py.
        import tokenize
        forbidden = {"/", "//", "%", "/=", "//=", "%="}
        bad = []
        with open(S.__file__, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.OP and tok.string in forbidden:
                    bad.append((tok.start, tok.string))
        self.assertEqual(bad, [], f"division/modulo operators found in stance.py: {bad}")


if __name__ == "__main__":
    unittest.main()
