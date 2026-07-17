# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the heightfield generator (`tools/terrain/heightfield.py`, T1 — the D14
procedural modality).

  * REFERENCE — the three preset scenes reproduce their pinned URDRHF1 digests ×2;
  * BYTE LAW — pinned lattice integers anchor the seeded-hash law at the byte level;
  * VALIDITY — heights bounded in [0, height_scale] on every scene; island corners are
    exactly zero; the island mask never raises a height;
  * IDENTITY — seed and layer changes move the digest; sea level moves the CANON but
    never the FIELD (presentation-adjacent params cannot alter terrain heights);
  * DEFECT — the linear-fade variant diverges from every golden while staying bounded
    (plausible wrongness, the D14 red-first obligation);
  * REFUSAL — out-of-range dims/layers/params are TERRAIN-REFUSE, never a clamp."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)
_f = os.path.join(_ROOT, "tools", "frontend")
if _f not in sys.path:
    sys.path.insert(0, _f)

import unittest
import heightfield as HF                                    # noqa: E402
import terrain_bridge as TBR                                # noqa: E402
import canon_ref as CR                                      # noqa: E402


class Terrain(unittest.TestCase):
    def test_scene_goldens(self):
        for name, builder in HF.SCENES.items():
            p = builder()
            d1, _ = HF.scene_digest(p)
            d2, _ = HF.scene_digest(p)
            self.assertEqual(d1, HF.golden(name), f"{name}: digest drifted")
            self.assertEqual(d1, d2, f"{name}: nondeterministic")

    def test_lattice_byte_law(self):
        # Pinned at authoring (2026-07-16): the seeded-hash lattice law, byte-anchored.
        self.assertEqual(HF._lattice(2920741843, 0, 0, 0), 44850)
        self.assertEqual(HF._lattice(2920741843, 1, 3, 5), 3056)
        self.assertEqual(HF._lattice(7, 0, 1, 1), 54717)

    def test_heights_bounded(self):
        for name, builder in HF.SCENES.items():
            p = builder()
            _, hts = HF.scene_digest(p)
            for row in hts:
                for v in row:
                    self.assertTrue(0 <= v <= p["height_scale"],
                                    f"{name}: height {v} outside 0..{p['height_scale']}")

    def test_island_corners_zero(self):
        _, hts = HF.scene_digest(HF.island())
        for v in (hts[0][0], hts[0][-1], hts[-1][0], hts[-1][-1]):
            self.assertEqual(v, 0, "an island corner is not at sea-floor zero")

    def test_island_mask_never_raises(self):
        p = HF.island()
        _, masked = HF.scene_digest(p)
        q = dict(p, falloff="none", falloff_width=0)
        _, flat = HF.scene_digest(q)
        for (mr, fr) in zip(masked, flat):
            for (mv, fv) in zip(mr, fr):
                self.assertLessEqual(mv, fv, "the island mask raised a height")

    def test_seed_moves_digest(self):
        p = HF.island()
        d1, _ = HF.scene_digest(p)
        d2, _ = HF.scene_digest(dict(p, seed=p["seed"] + 1))
        self.assertNotEqual(d1, d2, "seed change did not move the digest")

    def test_layer_moves_digest(self):
        p = HF.island()
        d1, _ = HF.scene_digest(p)
        d2, _ = HF.scene_digest(dict(p, layers=((32, 4), (16, 2), (8, 2))))
        self.assertNotEqual(d1, d2, "layer change did not move the digest")

    def test_sea_level_in_canon_not_field(self):
        p = HF.island()
        d1, h1 = HF.scene_digest(p)
        d2, h2 = HF.scene_digest(dict(p, sea_level=p["sea_level"] + 1))
        self.assertEqual(h1, h2, "sea level must never alter the height FIELD")
        self.assertNotEqual(d1, d2, "sea level is declared in the canon and must move it")

    def test_defect_diverges_bounded(self):
        for name, builder in HF.SCENES.items():
            p = builder()
            dd, dh = HF.scene_digest(p, fade=lambda t: t)
            self.assertNotEqual(dd, HF.golden(name),
                                f"{name}: the linear-fade defect did not diverge")
            for row in dh:
                for v in row:
                    self.assertTrue(0 <= v <= p["height_scale"],
                                    f"{name}: defect output unbounded (implausible defect)")

    def test_refusals_typed_and_total(self):
        base = HF.blank()
        cases = [
            dict(base, w=3),                                # below the dimension floor
            dict(base, h=513),                              # above the dimension cap
            dict(base, seed=True),                          # bool is not a seed
            dict(base, layers=()),                          # no layers
            dict(base, layers=tuple((8, 1) for _ in range(13))),   # over the stack cap
            dict(base, falloff="ridge"),                    # unknown falloff
            dict(base, sea_level=101),                      # sea above the scale
            dict(base, layers=((8, 1.0),)),                 # float amplitude
            dict(base, falloff="island", falloff_width=257),  # Q8 out of range
        ]
        for p in cases:
            with self.assertRaises(HF.TerrainError) as cm:
                HF.scene_digest(p)
            self.assertEqual(cm.exception.code, "TERRAIN-REFUSE", f"wrong code for {p!r}")

    def test_fresh_cache_determinism(self):
        p = HF.mountains()
        h1 = HF.generate(p["w"], p["h"], p["seed"], p["height_scale"], p["sea_level"],
                         p["layers"], p["falloff"], p["falloff_width"])
        h2 = HF.generate(p["w"], p["h"], p["seed"], p["height_scale"], p["sea_level"],
                         p["layers"], p["falloff"], p["falloff_width"])
        self.assertEqual(h1, h2, "independent caches produced different fields")


class TerrainBridge(unittest.TestCase):
    def test_object_goldens_and_referee_agreement(self):
        for name, (scene, stride, xy, zn, zd) in TBR.BRIDGES.items():
            p = HF.SCENES[scene]()
            verts, edges, dig, design = TBR.bridge_scene(p, stride, xy, zn, zd)
            self.assertEqual(dig, HF.golden(name), f"{name}: object golden drifted")
            self.assertEqual(dig, CR.canon(verts, edges),
                             f"{name}: own canon disagrees with the D14 reference")
            self.assertEqual(dig, TBR.own_canon(verts, edges), f"{name}: nondeterministic")
            self.assertEqual(CR.check_design(design), "ADMIT", f"{name}: D14 obligations failed")

    def test_object_provenance_inert(self):
        p = HF.SCENES["blank"]()
        _, _, d1, _ = TBR.bridge_scene(p, 5, 32, provenance={"tool": "terrain"})
        _, _, d2, _ = TBR.bridge_scene(p, 5, 32, provenance={"author": "someone else"})
        self.assertEqual(d1, d2, "provenance moved the object identity")

    def test_object_defect_diverges(self):
        for name, (scene, stride, xy, zn, zd) in TBR.BRIDGES.items():
            p = HF.SCENES[scene]()
            verts, edges, dig, _ = TBR.bridge_scene(p, stride, xy, zn, zd)
            self.assertNotEqual(TBR.own_canon_defect(verts, edges), dig,
                                f"{name}: the max-first canon defect did not diverge")

    def test_object_grid_coverage(self):
        p = HF.SCENES["island"]()
        verts, edges, _, _ = TBR.bridge_scene(p, 9, 8)
        self.assertEqual(len(verts), 64, "63/9 must give an 8x8 grid — border included")
        self.assertEqual(len(edges), 112)
        self.assertEqual((verts[0][0], verts[0][1]), (0, 0))
        self.assertEqual((verts[-1][0], verts[-1][1]), (504, 504),
                         "the last sample must sit exactly on the far border")

    def test_object_refusals_typed(self):
        p = HF.SCENES["blank"]()
        hts = HF.generate(p["w"], p["h"], p["seed"], p["height_scale"], p["sea_level"],
                          p["layers"], p["falloff"], p["falloff_width"])
        for args in ((hts, 4, 32), (hts, 5, 0), (hts, True, 32)):
            with self.assertRaises(HF.TerrainError) as cm:
                TBR.to_object(*args)
            self.assertEqual(cm.exception.code, "TERRAIN-REFUSE", f"wrong code for {args[1:]}")


if __name__ == "__main__":
    unittest.main()
