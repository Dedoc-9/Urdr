# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the MEASURED wave-crossing consumer (`tools/terrain/crossing.py`, T3.7).

  * REFERENCE — the pinned crossings reproduce their URDRCROSS1 digests ×2;
  * MOVING — the height trace is exactly `wavefield.height` at the MOVING cell and the MOVING tick
    (it reads the travelling authority along the trajectory, not a snapshot);
  * FIRST — the result is the FIRST overtopping tick (every earlier tick ≤ clearance, and > clearance
    at the result when it is not a clear);
  * CLEARANCE — on ONE path a high clearance clears and a low clearance is overtopped (load-bearing);
  * GRADES — ferry_clear clears (result == T); the swamped/swimmer scenes are overtopped (< T);
  * FROZEN — freezing the wave (every tick at t=0) changes when the agent is overtopped — wave travel
    is load-bearing;
  * REFUSAL — zero velocity, a path that leaves the grid, non-positive window, bool/float params are
    all CROSS-REFUSE;
  * NO-DIVISION — the source has no `/`, `//`, `%` operator (cross-placement is structural)."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import crossing as C                                             # noqa: E402
import wavefield as WF                                           # noqa: E402

W = H = 24
T = 12


class Crossing(unittest.TestCase):
    def test_scene_goldens(self):
        for name in C.SCENES:
            r, d = C.scene_result(name)
            self.assertEqual(d, C.golden(name), f"{name}: digest drifted")
            self.assertEqual(C.scene_result(name)[1], d, f"{name}: nondeterministic")

    def test_trace_reads_moving_field(self):
        comps, s, v, clr = C.swimmer_north()
        _r, tr = C.crossing_trace(W, H, T, comps, s, v, clr)
        expect = tuple(WF.height(s[0] + v[0] * t, s[1] + v[1] * t, t, comps) for t in range(T))
        self.assertEqual(tr, expect, "the trace must be wavefield.height at the moving cell AND moving tick")

    def test_first_overtop_is_first(self):
        for name in C.SCENES:
            comps, s, v, clr = C.SCENES[name]()
            r, tr = C.crossing_trace(W, H, T, comps, s, v, clr)
            self.assertTrue(all(h <= clr for h in tr[:r]), f"{name}: an earlier tick already exceeded clearance")
            if r < T:
                self.assertGreater(tr[r], clr, f"{name}: the result tick does not exceed clearance")

    def test_clearance_load_bearing(self):
        comps, s, v, _clr = C.ferry_clear()                      # ferry_clear + ferry_swamped share this path
        self.assertEqual(C.crossing(W, H, T, comps, s, v, 48), T, "a high clearance must clear")
        self.assertLess(C.crossing(W, H, T, comps, s, v, 27), T, "a low clearance must be overtopped")

    def test_cleared_and_overtopped_grades(self):
        self.assertEqual(C.crossing(W, H, T, *C.ferry_clear()), T, "ferry_clear must clear the window")
        self.assertLess(C.crossing(W, H, T, *C.ferry_swamped()), T, "ferry_swamped must be overtopped")
        self.assertLess(C.crossing(W, H, T, *C.swimmer_north()), T, "swimmer_north must be overtopped")

    def test_frozen_wave_defect_diverges(self):
        # freezing the wave (every tick at t=0) must change WHEN an overtopped agent is hit
        comps, s, v, clr = C.ferry_swamped()
        real = C.crossing(W, H, T, comps, s, v, clr)
        frozen = C.crossing(W, H, T, comps, s, v, clr, frozen=True)
        self.assertNotEqual(frozen, real, "the frozen-wave defect did not diverge (travel is load-bearing)")

    def test_zero_velocity_refusal(self):
        with self.assertRaises(C.CrossError) as cm:
            C.crossing(W, H, T, WF.swell(), (5, 5), (0, 0), 10)
        self.assertEqual(cm.exception.code, "CROSS-REFUSE")

    def test_path_leaves_grid_refusal(self):
        with self.assertRaises(C.CrossError) as cm:
            C.crossing(W, H, T, WF.swell(), (20, 12), (2, 0), 10)  # exits the east edge mid-window
        self.assertEqual(cm.exception.code, "CROSS-REFUSE")

    def test_typed_refusals_total(self):
        cases = [
            (0, (0, 12), (2, 0), 10),                            # non-positive window
            (T, (0, 12), (2, 0), True),                          # bool clearance
            (T, (0.0, 12), (2, 0), 10),                          # non-integer start
            (T, (0, 12), (2,), 10),                              # malformed velocity
        ]
        for ticks, start, vel, clr in cases:
            with self.assertRaises(C.CrossError) as cm:
                C.crossing(W, H, ticks, WF.swell(), start, vel, clr)
            self.assertEqual(cm.exception.code, "CROSS-REFUSE", f"wrong code for {(ticks, start, vel, clr)!r}")

    def test_no_division_operators(self):
        # STRUCTURAL cross-placement guarantee — no `/`, `//`, or `%` operator in crossing.py.
        import tokenize
        forbidden = {"/", "//", "%", "/=", "//=", "%="}
        bad = []
        with open(C.__file__, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.OP and tok.string in forbidden:
                    bad.append((tok.start, tok.string))
        self.assertEqual(bad, [], f"division/modulo operators found in crossing.py: {bad}")


if __name__ == "__main__":
    unittest.main()
