# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the FIXED-POINT facing seam (`tools/terrain/fpface.py`, T3.15, Slice 4a) — the
exact-integer terrain facing lifts into the fpquat Q32.32 rotation regime, EXACTLY at the cardinals and
rounding between them. This is the FIRST terrain canon that deliberately leaves the division-free regime.

  * REFERENCE — the two pinned scenes reproduce their URDRFACE1 digests ×2;
  * EXACT LIFT — all four cardinal facings rotate the forward vector onto their exact direction vectors
    with ZERO ulp error (the exact embedding), even though the 90° quaternion carries a rounded √2/2;
  * CYCLIC GROUP — E→N→W→S→E under a 90° yaw permutes the direction vectors exactly;
  * SEAM CONVENTION — fpface uses drive/stance's own facing map (N/E/S/W) and its lifted (x,z) directions
    equal stance's grid `DIRS` — the seam connects to the terrain stack, not a private convention;
  * TRIG-FREE — the √2/2 component is `fpquat.rsqrt(2·ONE)` (the frozen integer isqrt value 3037000499),
    NOT a `math` trig value (3037000500) — the seam stays inside the frozen fixed-point discipline;
  * MOUSE-LOOK ROUNDS — an interior nlerp orientation is a continuous, rounded direction (not a cardinal
    ±ONE axis), while the endpoints are exact; the sweep is deterministic (bit-reproducible);
  * ACCUMULATION DRIFTS — composing a non-cardinal rotation through a full turn leaves a bounded,
    deterministic, NON-zero drift: exactness holds only on the cardinal lattice (the honest boundary);
  * DEFECT — a wrong cardinal quaternion breaks the exact lift and moves the `cardinals` digest;
  * REFUSAL — a non-cardinal facing is a typed `FACE-REFUSE`.

Requires the fpquat Q32.32 substrate (`fpquat` → `field`); the full gate always runs with it."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "frontfps"),
           os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import fpface as F                                                # noqa: E402
import fpquat as FQ                                               # noqa: E402
import stance as ST                                               # noqa: E402  (the grid DIRS the seam lifts)
import drive as DR                                                # noqa: E402  (the movement stack's facing map)
from field import ONE                                            # noqa: E402


class FpFace(unittest.TestCase):
    def test_scene_goldens(self):
        for name in F.SCENES:
            dig = F.scene_result(name)
            self.assertEqual(dig, F.golden(name), f"{name}: fpface digest drifted")
            self.assertEqual(F.scene_result(name), dig, f"{name}: nondeterministic")

    def test_cardinal_lift_exact(self):
        for f in range(4):
            self.assertEqual(F.lift(f), F.facing_vec(f),
                             f"facing {f} must lift to its exact direction vector (0 ulp)")
        self.assertTrue(F.lift_is_exact(), "the exact embedding must hold for all four cardinals")

    def test_cyclic_group_exact(self):
        self.assertTrue(F.cyclic_is_exact(), "the E→N→W→S→E facing group must permute exactly under 90° yaw")

    def test_seam_uses_terrain_facing_convention(self):
        self.assertEqual(F._FACE, DR._FACE, "the seam must use drive's own N/E/S/W facing map")
        # fpface's lifted (x, z) direction for each facing equals stance's grid DIRS (dx, dy)
        for letter, idx in F._FACE.items():
            vx, _vy, vz = F.facing_vec(idx)
            self.assertEqual((vx // ONE, vz // ONE), ST.DIRS[letter],
                             f"facing {letter}: lifted (x,z) must equal stance's grid DIRS")

    def test_trig_free_rsqrt(self):
        self.assertEqual(F.R2, FQ.rsqrt(2 * ONE), "the √2/2 component must be the frozen isqrt value")
        self.assertEqual(F.R2, 3037000499, "the frozen isqrt value (not the math-trig 3037000500)")

    def test_mouselook_rounds_endpoints_exact(self):
        self.assertEqual(F.look(0), (ONE, 0, 0), "t=0 is exact E")
        self.assertEqual(F.look(ONE), (0, 0, -ONE), "t=ONE is exact N")
        mid = F.look(ONE // 2)
        self.assertNotIn(mid, (F.facing_vec(0), F.facing_vec(1), F.facing_vec(2), F.facing_vec(3)),
                         "an interior mouse-look direction must be continuous (rounded), not a cardinal axis")
        self.assertTrue(any(c not in (0, ONE, -ONE) for c in mid), "the interior direction must round")
        self.assertEqual(F.look(ONE // 2), mid, "mouse-look must be deterministic (frozen rounding)")

    def test_accumulation_drifts(self):
        drift = F.compose_drift()
        self.assertNotEqual(drift, (0, 0, 0),
                            "a non-cardinal rotation composed through a full turn MUST drift (exactness "
                            "does not survive accumulation — the honest boundary)")
        self.assertEqual(drift, F.compose_drift(), "the drift must be deterministic (bounded, reproducible)")

    def test_defect_wrong_quat_diverges(self):
        good = F.scene_result("cardinals")
        saved = F.FACING_QUAT[0]
        try:
            F.FACING_QUAT[0] = (ONE, 0, 0, 0)                     # identity instead of the 90° yaw — breaks N
            self.assertNotEqual(F.scene_result("cardinals"), good,
                                "a wrong cardinal quaternion must move the digest (non-vacuity)")
        finally:
            F.FACING_QUAT[0] = saved
        self.assertEqual(F.scene_result("cardinals"), good, "restore must recover the golden")

    def test_typed_refusals(self):
        for bad in (9, -1, True, "N", 1.0):
            with self.assertRaises(F.FaceError) as cm:
                F.lift(bad)
            self.assertEqual(cm.exception.code, "FACE-REFUSE", f"wrong code for facing {bad!r}")


if __name__ == "__main__":
    unittest.main()
