# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the MEASURED buoyancy consumer (`tools/terrain/buoyancy.py`, T3.5).

  * REFERENCE — the pinned raft scenes reproduce their URDRBUOY1 digests ×2 at every pinned tick;
  * BRACKET — the equilibrium waterline satisfies the exact Archimedes bracket Δ(z*) ≥ W > Δ(z*+1);
  * MONOTONE — the displaced measure Δ(z) is non-increasing in the waterline z;
  * HEAVE/REST — the raft heaves on the moving swell and rests dead-flat on the zero-speed still;
  * CONSUMES-EXACT — the wetted profile is exactly max(0, certified_field − z*) (it reads the T3.3
    authority, not an approximation);
  * DEFECT — the UNCLAMPED-displacement defect diverges from the correct heave (clamp load-bearing);
  * BINDS — the digest binds BOTH z* and the per-cell profile (a wrong either reddens);
  * REFUSAL — empty/out-of-grid/duplicate footprint, non-positive or too-heavy weight, bool/float
    are all BUOY-REFUSE; too-heavy is the physical "it sinks" boundary;
  * NO-DIVISION — the source has no `/`, `//`, `%` operator (cross-placement is structural)."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import buoyancy as B                                             # noqa: E402
import wavefield as WF                                           # noqa: E402

W = H = 24


class Buoyancy(unittest.TestCase):
    def test_scene_goldens(self):
        for name in B.SCENES:
            for t in B.SCENE_TICKS[name]:
                z, d = B.scene_state(name, t)
                self.assertEqual(d, B.golden(name, t), f"{name}@{t}: digest drifted")
                z2, d2 = B.scene_state(name, t)
                self.assertEqual(d2, d, f"{name}@{t}: nondeterministic")

    def test_archimedes_bracket(self):
        for name in B.SCENES:
            comps, fp, wt = B.SCENES[name]()
            for t in B.SCENE_TICKS[name]:
                field = WF.field(W, H, t, comps)
                z = B.waterline(W, H, t, comps, fp, wt)
                self.assertGreaterEqual(B._displacement(field, fp, z), wt,
                                        f"{name}@{t}: Δ(z*) < weight (raft under-displaces)")
                self.assertGreater(wt, B._displacement(field, fp, z + 1),
                                   f"{name}@{t}: Δ(z*+1) ≥ weight (z* is not the largest)")

    def test_displacement_monotone(self):
        for name in B.SCENES:
            comps, fp, _wt = B.SCENES[name]()
            field = WF.field(W, H, 0, comps)
            lo, hi = B._bounds(field, fp)
            prev = None
            for z in range(lo, hi + 2):
                d = B._displacement(field, fp, z)
                if prev is not None:
                    self.assertLessEqual(d, prev, f"{name}: Δ rose from {prev} to {d} at z={z}")
                prev = d

    def test_heave_and_rest(self):
        sw = B.heave(W, H, range(0, 8), *B.raft_swell())
        self.assertGreater(len(set(sw)), 1, "the raft must heave on the moving swell")
        st = B.heave(W, H, range(0, 8), *B.raft_still())
        self.assertEqual(len(set(st)), 1, "a zero-speed field must hold the raft dead-flat")

    def test_consumes_exact_field(self):
        comps, fp, wt = B.raft_swell()
        z = B.waterline(W, H, 3, comps, fp, wt)
        prof = B.submerged_profile(W, H, 3, comps, fp, z)
        field = WF.field(W, H, 3, comps)
        expect = tuple(max(0, field[y][x] - z) for (x, y) in fp)
        self.assertEqual(prof, expect, "the wetted profile must be max(0, certified_field − z*)")

    def test_defect_diverges(self):
        comps, fp, wt = B.raft_swell()
        correct = B.heave(W, H, range(0, 8), comps, fp, wt)
        defect = B.heave(W, H, range(0, 8), comps, fp, wt, disp=B._displacement_defect)
        self.assertNotEqual(defect, correct,
                            "the unclamped-displacement defect must diverge (gate can redden)")

    def test_digest_binds_profile_and_waterline(self):
        self.assertNotEqual(B.buoy_digest("s", 0, 5, (1, 2, 3)),
                            B.buoy_digest("s", 0, 5, (1, 2, 4)), "profile must bind the digest")
        self.assertNotEqual(B.buoy_digest("s", 0, 5, (1, 2, 3)),
                            B.buoy_digest("s", 0, 6, (1, 2, 3)), "z* must bind the digest")

    def test_refusals_typed_and_total(self):
        raft = B.raft()
        cases = [
            ((), 100),                                          # empty footprint
            (((99, 0),), 100),                                  # cell outside the grid
            ((raft[0], raft[0]), 100),                          # duplicate cell
            (raft, 0),                                          # non-positive weight
            (raft, True),                                       # bool weight
            (((10, 10.0),), 100),                               # non-integer cell
        ]
        for fp, wt in cases:
            with self.assertRaises(B.BuoyError) as cm:
                B.waterline(W, H, 0, WF.swell(), fp, wt)
            self.assertEqual(cm.exception.code, "BUOY-REFUSE", f"wrong code for {fp!r},{wt!r}")

    def test_too_heavy_sinks(self):
        comps, fp, _wt = B.raft_swell()
        cap = B.max_displacement(W, H, 0, comps, fp)
        with self.assertRaises(B.BuoyError) as cm:                # one over the cap cannot float
            B.waterline(W, H, 0, comps, fp, cap + 1)
        self.assertEqual(cm.exception.code, "BUOY-REFUSE", "too-heavy raft must refuse, not fake a float")
        self.assertEqual(B._displacement(WF.field(W, H, 0, comps), fp,
                                         B.waterline(W, H, 0, comps, fp, cap)), cap,
                         "at exactly the cap the raft floats fully submerged")

    def test_no_division_operators(self):
        # STRUCTURAL cross-placement guarantee — no `/`, `//`, or `%` operator in buoyancy.py
        # (integer `/` and `%` disagree across languages on negative operands; the bisection uses
        # `>>` instead). The check tokenizes the source, so `/` in comments/strings is ignored.
        import tokenize
        forbidden = {"/", "//", "%", "/=", "//=", "%="}
        bad = []
        with open(B.__file__, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.OP and tok.string in forbidden:
                    bad.append((tok.start, tok.string))
        self.assertEqual(bad, [], f"division/modulo operators found in buoyancy.py: {bad}")


if __name__ == "__main__":
    unittest.main()
