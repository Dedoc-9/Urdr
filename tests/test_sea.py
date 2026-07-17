# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the S1 sea slice (`tools/terrain/sea.py` — bathymetry adapter + masked
flux-form transport over the frozen urdr-field substrate).

  * REFERENCE — the pinned island sea (drop at the deepest cell, 40 masked ticks)
    reproduces its URDRFLD1 digest ×2;
  * CONSERVATION — total mass is EXACTLY conserved across the masked evolution;
  * COAST — land cells are identically zero at init and after evolution (the coastline
    is boundary; water cannot come ashore);
  * EQUIVALENCE — an all-sea mask reproduces the frozen `field.step` bit-for-bit,
    advection included (the masked law is the frozen law plus a boundary, nothing more);
  * DEFECT — evolving the same scene with the UNMASKED frozen step wets land cells and
    diverges from the golden (the mask is load-bearing, not decorative);
  * REFUSAL — empty seas, drops on land, bool params (TERRAIN-REFUSE) and structural
    grid/mask mismatches (FIELD-REFUSE), each typed."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import heightfield as HF                                    # noqa: E402
import sea as SEA                                           # noqa: E402
from field import FixedPoint as FP, FieldError, step, mass, digest   # noqa: E402


def _pinned():
    p = HF.SCENES[SEA.SEA_SCENE["terrain"]]()
    mask, grid = SEA.sea_from_terrain(FP, p)
    x, y = SEA.SEA_SCENE["drop_xy"]
    g0 = SEA.drop(FP, grid, mask, p["w"], x, y, *SEA.SEA_SCENE["drop"])
    return p, mask, g0


class Sea(unittest.TestCase):
    def test_island_sea_golden(self):
        p, mask, g0 = _pinned()
        gN = SEA.evolve(FP, g0, mask, p["w"], p["h"], SEA.SEA_SCENE["k"], SEA.SEA_SCENE["ticks"])
        d1 = digest(FP, gN, p["w"], p["h"])
        self.assertEqual(d1, SEA.golden("island_sea"), "the sea scene drifted from its golden")
        gN2 = SEA.evolve(FP, g0, mask, p["w"], p["h"], SEA.SEA_SCENE["k"], SEA.SEA_SCENE["ticks"])
        self.assertEqual(digest(FP, gN2, p["w"], p["h"]), d1, "nondeterministic")

    def test_mass_conserved_exactly(self):
        p, mask, g0 = _pinned()
        gN = SEA.evolve(FP, g0, mask, p["w"], p["h"], SEA.SEA_SCENE["k"], SEA.SEA_SCENE["ticks"])
        self.assertEqual(mass(FP, g0), mass(FP, gN),
                         "masked flux form must conserve total mass EXACTLY")
        self.assertNotEqual(g0, gN, "nothing moved — the scene is vacuous")

    def test_land_stays_dry(self):
        p, mask, g0 = _pinned()
        gN = SEA.evolve(FP, g0, mask, p["w"], p["h"], SEA.SEA_SCENE["k"], SEA.SEA_SCENE["ticks"])
        for i in range(len(mask)):
            if not mask[i]:
                self.assertTrue(FP.is_zero(g0[i]), "land wet at init")
                self.assertTrue(FP.is_zero(gN[i]), "water came ashore through the mask")

    def test_all_sea_mask_equals_frozen_step(self):
        allmask = [True] * 256
        g = [FP.unit(3, 1)] * 256
        g[40] = FP.unit(9, 1)
        a = SEA.step_masked(FP, g, allmask, 16, 16, (1, 8), (1, 16), (0, 1))
        b = step(FP, g, 16, 16, (1, 8), (1, 16), (0, 1))
        self.assertEqual(a, b, "an all-sea mask must reproduce the frozen step bit-for-bit")

    def test_unmasked_defect_leaks_and_diverges(self):
        p, mask, g0 = _pinned()
        gU = g0
        for _ in range(SEA.SEA_SCENE["ticks"]):
            gU = step(FP, gU, p["w"], p["h"], SEA.SEA_SCENE["k"], (0, 1), (0, 1))
        leaked = sum(1 for i in range(len(mask)) if not mask[i] and not FP.is_zero(gU[i]))
        self.assertGreater(leaked, 0, "the unmasked step did not leak — the defect is vacuous")
        self.assertNotEqual(digest(FP, gU, p["w"], p["h"]), SEA.golden("island_sea"),
                            "the leaking evolution did not diverge from the golden")

    def test_drop_refusals(self):
        p, mask, g0 = _pinned()
        for (x, y) in ((32, 32), (999, 0)):                 # interior land; outside grid
            with self.assertRaises(HF.TerrainError) as cm:
                SEA.drop(FP, g0, mask, p["w"], x, y, 1, 1)
            self.assertEqual(cm.exception.code, "TERRAIN-REFUSE")

    def test_adapter_refusals(self):
        p = HF.SCENES["island"]()
        with self.assertRaises(HF.TerrainError) as cm:
            SEA.sea_from_terrain(FP, dict(p, sea_level=0))  # empty sea
        self.assertEqual(cm.exception.code, "TERRAIN-REFUSE")
        with self.assertRaises(HF.TerrainError) as cm:
            SEA.sea_from_terrain(FP, p, depth_num=True)     # bool depth scale
        self.assertEqual(cm.exception.code, "TERRAIN-REFUSE")

    def test_structural_refusal_is_field_side(self):
        p, mask, g0 = _pinned()
        with self.assertRaises(FieldError) as cm:
            SEA.step_masked(FP, g0[:-1], mask, p["w"], p["h"], (1, 8), (0, 1), (0, 1))
        self.assertEqual(cm.exception.code, "FIELD-REFUSE")


class SeaMarangoni(unittest.TestCase):
    def _wide(self):
        p = HF.SCENES[SEA.SEA_SCENE_WIDE["terrain"]]()
        sc = SEA.SEA_SCENE_WIDE
        mask, grid = SEA.sea_from_terrain(FP, p, *sc["depth"],
                                          scene_sea_level=sc["scene_sea_level"])
        g0 = SEA.drop(FP, grid, mask, p["w"], *sc["drop_xy"], *sc["drop"])
        return p, sc, mask, g0

    def test_wide_sea_golden(self):
        p, sc, mask, g0 = self._wide()
        gN = SEA.evolve_marangoni(g0, mask, p["w"], p["h"], sc["k"], sc["kappa"], sc["ticks"])
        d1 = digest(FP, gN, p["w"], p["h"])
        self.assertEqual(d1, SEA.golden("island_sea_wide"), "the wide-sea scene drifted")
        gN2 = SEA.evolve_marangoni(g0, mask, p["w"], p["h"], sc["k"], sc["kappa"], sc["ticks"])
        self.assertEqual(digest(FP, gN2, p["w"], p["h"]), d1, "nondeterministic")

    def test_marangoni_mass_monotone_and_peak(self):
        p, sc, mask, g0 = self._wide()
        m0 = mass(FP, g0)
        g = g0
        for t in range(sc["ticks"]):
            g = SEA.step_marangoni_masked(g, mask, p["w"], p["h"], sc["k"], sc["kappa"])
            self.assertGreaterEqual(min(g), 0,
                                    f"tick {t}: negative cell — the pinned kappa left the monotone regime")
        self.assertEqual(mass(FP, g), m0, "Marangoni transport must conserve mass EXACTLY")
        gD = SEA.evolve(FP, g0, mask, p["w"], p["h"], sc["k"], sc["ticks"])
        self.assertGreater(max(g), max(gD),
                           "kappa must keep the peak above pure diffusion (the Marangoni content)")
        for i in range(len(mask)):
            if not mask[i]:
                self.assertTrue(FP.is_zero(g[i]), "Marangoni water came ashore")

    def test_overbound_kappa_defect(self):
        p, sc, mask, g0 = self._wide()
        gB = SEA.evolve_marangoni(g0, mask, p["w"], p["h"], sc["k"],
                                  sc["defect_kappa"], sc["defect_ticks"])
        self.assertLess(min(gB), 0,
                        "the over-bound kappa did not overshoot negative (the CFL bound is vacuous)")
        self.assertEqual(mass(FP, gB), mass(FP, g0),
                         "even the unphysical overshoot must conserve mass (flux form)")

    def test_scene_sea_level_refusals(self):
        p = HF.SCENES["island"]()
        for bad in (0, True, p["height_scale"] + 1):
            with self.assertRaises(HF.TerrainError) as cm:
                SEA.sea_from_terrain(FP, p, scene_sea_level=bad)
            self.assertEqual(cm.exception.code, "TERRAIN-REFUSE", f"wrong code for {bad!r}")


if __name__ == "__main__":
    unittest.main()
