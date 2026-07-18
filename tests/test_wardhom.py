# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the warden's walkable-graph homology, cross-placed (`tools/terrain/wardhom.py`, T3.27, MMO
Stage E, URDRWARDH1) — the warden's beta0, computed directly by union-find, IS the invariant URDRPD1 certifies
as rank H0 over F2, and this ties the two together and cross-places the walkable-graph homology.

  * REFERENCE — the three pinned worlds reproduce their URDRWARDH1 digests, deterministically;
  * THE KEYSTONE (warden tie) — warden.betti0 (union-find) == URDRPD1 F2-rank beta0 on every world, including
    the 16x16 warden barrier (two independent methods, one invariant);
  * KNOWN-ANSWER BETTI — barrier8 beta0 = 3, cliff8 beta0 = 2, flat8 beta0 = 1 (textbook component counts);
  * COUNTS IDENTITY — beta0 = n0 - rank(d1) and beta1 = n1 - rank(d1) over F2, n0 = 64 (the homology identity);
  * BETA1 CYCLES (non-vacuity) — the walkable graph has real cycles (beta1 > 0) and the flat world has more of
    them than the wall-split one;
  * THE COMPLEX IS THE WARDEN'S GRAPH — the walkable 1-complex's edges are EXACTLY warden's legal-both-ways
    steps (the bridge is faithful, not a different graph);
  * DEFECT DIVERGES — dropping the F2 rank subtraction (the URDRPD1 defect mode) inflates beta0 and moves the
    digest, so the reduction is load-bearing;
  * GENERALIZES — the union-find-vs-rank tie holds on the OTHER wardens' worlds too (the dirward cliff, the
    crosswarden merge), not only the 8x8 pins.

The C99 (`wardhom_c/`) and Rust (`wardhom_rs/`) placements reproduce the same digests bit-for-bit; the gate's
`wardhom-placement` row re-verifies them live where a toolchain is present. Composes `warden` + URDRPD1's
`urdr_homology`; the gate runs it."""
import os
import sys
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "homology"))

import unittest
import wardhom as WH                                            # noqa: E402
import warden as W                                             # noqa: E402
import dirward as D                                            # noqa: E402
import crosswarden as CW                                       # noqa: E402


class WardHom(unittest.TestCase):
    def setUp(self):
        self.ms = WH._MS
        self.worlds = {"barrier8": WH._barrier8(), "cliff8": WH._cliff8(), "flat8": WH._flat8()}

    def test_scene_goldens(self):
        for name in WH.SCENES:
            dig = WH.scene_result(name)
            self.assertEqual(dig, WH.golden(name), f"{name}: wardhom digest drifted")
            self.assertEqual(WH.scene_result(name), dig, f"{name}: nondeterministic")

    def test_warden_tie(self):
        for name, fld in self.worlds.items():
            self.assertEqual(W.betti0(fld, self.ms), WH.homology_betti0(fld, self.ms),
                             f"{name}: union-find beta0 != F2-rank beta0")
        # generalize beyond the 8x8 pins: the 16x16 warden barrier
        self.assertEqual(W.betti0(W._barrier_field(), self.ms),
                         WH.homology_betti0(W._barrier_field(), self.ms), "16x16 barrier tie failed")

    def test_known_betti(self):
        self.assertEqual(WH.counts(self.worlds["barrier8"], self.ms)[3], 3, "wall splits into 3 components")
        self.assertEqual(WH.counts(self.worlds["cliff8"], self.ms)[3], 2, "the height jump splits into 2")
        self.assertEqual(WH.counts(self.worlds["flat8"], self.ms)[3], 1, "flat is one component")

    def test_counts_identity(self):
        for name, fld in self.worlds.items():
            n0, n1, rank, b0, b1 = WH.counts(fld, self.ms)
            self.assertEqual(n0, 64, f"{name}: n0 must be 64")
            self.assertEqual(b0, n0 - rank, f"{name}: beta0 = n0 - rank(d1)")
            self.assertEqual(b1, n1 - rank, f"{name}: beta1 = n1 - rank(d1)")

    def test_beta1_cycles(self):
        b1_flat = WH.counts(self.worlds["flat8"], self.ms)[4]
        b1_barrier = WH.counts(self.worlds["barrier8"], self.ms)[4]
        self.assertGreater(b1_barrier, 0, "the walkable graph must have cycles")
        self.assertGreater(b1_flat, b1_barrier, "the flat world must have more cycles than the wall-split one")

    def test_complex_is_wardens_graph(self):
        fld = self.worlds["barrier8"]
        w = len(fld[0])
        cx = WH.walkable_complex(fld, self.ms)
        edges = {s for s in cx if len(s) == 2}
        # independently enumerate warden's legal-both-ways adjacent steps
        want = set()
        for y in range(len(fld)):
            for x in range(w):
                v = y * w + x
                if x + 1 < w and abs(fld[y][x + 1] - fld[y][x]) <= self.ms:
                    want.add((v, y * w + x + 1))
                if y + 1 < len(fld) and abs(fld[y + 1][x] - fld[y][x]) <= self.ms:
                    want.add((v, (y + 1) * w + x))
        self.assertEqual(edges, want, "the 1-complex edges must be exactly warden's walkable steps")

    def test_defect_diverges(self):
        # replicate the digest with the F2 rank subtraction DROPPED (beta0=n0, beta1=n1) — must differ
        for name, fld in self.worlds.items():
            n0, n1, rank, _b0, _b1 = WH.counts(fld, self.ms)
            out = bytearray(WH.MAGIC) + name.encode() + b"|"
            for v in (n0, n1, rank, n0, n1):     # defect values
                out += v.to_bytes(4, "big")
            defect = hashlib.sha256(bytes(out)).hexdigest()
            self.assertNotEqual(defect, WH.golden(name), f"{name}: the rank subtraction must be load-bearing")

    def test_generalizes_to_other_wardens(self):
        for fld in (D._cliff_field(), CW.merged_field(*CW._shards(), CW._SPLIT)):
            self.assertEqual(W.betti0(fld, self.ms), WH.homology_betti0(fld, self.ms),
                             "the union-find / F2-rank tie must hold on the other wardens' worlds")


if __name__ == "__main__":
    unittest.main()
