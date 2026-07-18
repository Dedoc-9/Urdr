# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for deterministic Area-of-Interest relevance (`tools/terrain/interest.py`, T3.21, MMO Stage
C) — which peers need to hear about which actors. The narrow phase (exact Chebyshev radius) is the ground
truth; the broad phase (side-2^k buckets) is the O(local) acceleration that must never miss a relevant actor.

  * REFERENCE — the two pinned scenes reproduce their URDRAOI1 digests, deterministically;
  * EXACTNESS — `aoi_radius` == the brute-force within-R set: complete (no in-range actor omitted) and
    sound (no out-of-range actor admitted);
  * SYMMETRY — B is relevant to A iff A is relevant to B (Chebyshev distance is symmetric);
  * BROAD-PHASE SOUNDNESS (the keystone) — for R <= 2^k, `aoi_radius(R)` is a SUBSET of `aoi_buckets(2^k)`:
    the acceleration never misses a relevant actor. Non-vacuous: a witness where the broad phase strictly
    over-approximates (an in-bucket actor outside R);
  * PRECONDITION IS LOAD-BEARING — at R > 2^k the broad phase CAN miss a relevant actor (a constructed
    defect), so `R <= 2^k` is required, not decorative;
  * TAMPER-EVIDENCE — moving one actor moves the relevance digest;
  * NO SEAM AT ZERO — buckets floor toward -inf, so negative and positive coordinates tile without a gap;
  * REFUSAL — a duplicate / non-integer actor, an unknown observer, a negative radius, or a non-power-of-two
    bucket side is a typed `AOI-REFUSE`.

Pure integer geometry; the gate runs it."""
import os
import random
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import unittest
import interest as I                                              # noqa: E402


def _cloud(rng, n, span):
    return tuple([("o", 0, 0)] + [(f"a{i}", rng.randint(-span, span), rng.randint(-span, span))
                                  for i in range(n)])


def _brute(cloud, obs, R):
    pos = {a: (x, y) for a, x, y in cloud}
    ox, oy = pos[obs]
    return tuple(sorted(a for a, x, y in cloud
                        if a != obs and max(abs(ox - x), abs(oy - y)) <= R))


class Interest(unittest.TestCase):
    def test_scene_goldens(self):
        for name in I.SCENES:
            dig = I.scene_result(name)
            self.assertEqual(dig, I.golden(name), f"{name}: interest digest drifted")
            self.assertEqual(I.scene_result(name), dig, f"{name}: nondeterministic")

    def test_exactness(self):
        rng = random.Random(20260718)
        for _ in range(300):
            cl = _cloud(rng, 12, 40)
            R = rng.randint(0, 20)
            self.assertEqual(I.aoi_radius(cl, "o", R), _brute(cl, "o", R),
                             "aoi_radius must be exactly the within-R set (complete and sound)")

    def test_symmetry(self):
        rng = random.Random(4242)
        for _ in range(200):
            cl = _cloud(rng, 10, 30)
            R = rng.randint(0, 15)
            for a, _x, _y in cl:
                for b in I.aoi_radius(cl, a, R):
                    self.assertIn(a, I.aoi_radius(cl, b, R),
                                  f"relevance must be symmetric: {b} sees {a} but not vice versa")

    def test_broad_phase_soundness(self):
        """THE KEYSTONE: for R <= side, aoi_radius(R) ⊆ aoi_buckets(side). Non-vacuous — the broad phase
        must strictly over-approximate in at least one cloud."""
        rng = random.Random(99)
        strict = 0
        for _ in range(500):
            cl = _cloud(rng, 20, 60)
            side = rng.choice([4, 8, 16, 32])
            R = rng.randint(0, side)                              # R <= side
            narrow = set(I.aoi_radius(cl, "o", R))
            broad = set(I.aoi_buckets(cl, "o", side))
            self.assertTrue(narrow.issubset(broad),
                            f"broad phase missed a relevant actor (R={R} side={side})")
            if narrow < broad:
                strict += 1
        self.assertGreater(strict, 0, "NON-VACUITY: the broad phase must strictly over-approximate somewhere")

    def test_precondition_is_load_bearing(self):
        """At R > 2^k the broad phase CAN miss a relevant actor — a constructed defect proving R<=2^k bites."""
        cloud = (("obs", 7, 0), ("x", 16, 0))                    # d(obs,x)=9; side 8 → buckets 0 and 2
        narrow = set(I.aoi_radius(cloud, "obs", 9))              # x is relevant (d=9 <= 9)
        broad = set(I.aoi_buckets(cloud, "obs", 8))              # x's bucket is 2 buckets away → excluded
        self.assertIn("x", narrow, "x is within R=9")
        self.assertNotIn("x", broad, "x is two buckets away → the broad phase at side 8 misses it")
        self.assertFalse(narrow.issubset(broad), "so R=9 > side=8 breaks soundness — the precondition bites")

    def test_tamper_evidence(self):
        cl = (("o", 0, 0), ("b", 3, 0))
        base = I.relevance_digest("s", cl, 4, I.aoi_radius(cl, "o", 4))
        moved = (("o", 0, 0), ("b", 9, 0))                       # b moved out of range
        after = I.relevance_digest("s", moved, 4, I.aoi_radius(moved, "o", 4))
        self.assertNotEqual(base, after, "moving an actor must move the relevance digest")

    def test_no_seam_at_zero(self):
        # coords straddling 0 must bucket by floor(-inf): -1 and 0 differ, -1 and -8 share bucket at side 8
        self.assertEqual(I.bucket(-1, 0, 8), (-1, 0), "-1 must floor to bucket -1, not 0")
        self.assertEqual(I.bucket(-8, 0, 8), (-1, 0), "-8 and -1 share bucket -1 (tiling without a seam)")
        self.assertEqual(I.bucket(0, 0, 8), (0, 0))

    def test_typed_refusals(self):
        good = (("o", 0, 0), ("b", 1, 1))
        cases = [
            (lambda: I.aoi_radius((("o", 0, 0), ("o", 1, 1)), "o", 4)),   # duplicate id
            (lambda: I.aoi_radius((("o", 0, 0), ("b", 1, 1.0)), "o", 4)), # non-int coord
            (lambda: I.aoi_radius(good, "ghost", 4)),                     # unknown observer
            (lambda: I.aoi_radius(good, "o", -1)),                        # negative radius
            (lambda: I.aoi_buckets(good, "o", 3)),                        # non-power-of-two side
        ]
        for call in cases:
            with self.assertRaises(I.AoiError) as cm:
                call()
            self.assertEqual(cm.exception.code, "AOI-REFUSE", "wrong refusal code")


if __name__ == "__main__":
    unittest.main()
