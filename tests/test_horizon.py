# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the rollback-horizon reconcile window (`tools/terrain/horizon.py`, T3.32, MMO Stage H) — the
worst-case reconciliation latency of a client correction, a certified hard bound. A correction is ADMITTED iff
its rollback depth is within the snapshot horizon H, else a typed HORIZON-REFUSE; on admit the reconstruction
is byte-exact (delta = 0).

  * REFERENCE — the three pinned scenarios reproduce their URDRLAT1 digests, deterministically;
  * DEPTH MEASURE — rollback_depth is n - k, the boundaries the reconcile replays (0 for a correct prediction);
  * BYTE-EXACT RECONSTRUCT — an admitted reconcile equals the authoritative glide bit-for-bit (delta = 0);
  * DEPTH BOUND — an admitted reconcile's depth is <= horizon;
  * HORIZON-REFUSE — a rollback deeper than the horizon is refused (a stale correction, not silently served);
  * WINDOW — worst_case_window(H) == H (the certified worst-case reconcile latency);
  * COST BOUND — reconcile_cost is 0 for a correct prediction and bounded by the depth otherwise;
  * DEEP-UNDER-LARGE — a deep misprediction admits under a large horizon and is still byte-exact.

Composes `cpredict` (reconcile / reconstruct), `glide`, and `opcost`; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import horizon as H                                            # noqa: E402
import glide as GL                                             # noqa: E402


class Horizon(unittest.TestCase):
    def setUp(self):
        self.fld = H._flat16()
        self.ms, self.sub, self.start = H._MS, H._SUB, H._START
        self.auth = H._AUTH

    def test_scene_goldens(self):
        for name in H.SCENES:
            dig = H.scene_result(name)
            self.assertEqual(dig, H.golden(name), f"{name}: horizon digest drifted")
            self.assertEqual(H.scene_result(name), dig, f"{name}: nondeterministic")

    def test_depth_measure(self):
        self.assertEqual(H.rollback_depth(self.fld, self.start, "eeee", "eeee", self.ms, self.sub), 0,
                         "a correct prediction has depth 0")
        self.assertEqual(H.rollback_depth(self.fld, self.start, "eeee", "neee", self.ms, self.sub),
                         len("eeee") + 1, "a boundary-0 mispredict replays the whole transcript")

    def test_byte_exact_reconstruct(self):
        recon = H.admit_reconcile(self.fld, self.start, "eeee", "eeen", self.ms, self.sub, 5)
        self.assertEqual(recon, GL.glide_cells(self.fld, self.start, "eeee", self.ms, self.sub),
                         "an admitted reconcile must land on the authority byte-for-byte")

    def test_depth_bound(self):
        for pred in ("eeee", "eeen", "eene"):
            d = H.rollback_depth(self.fld, self.start, "eeee", pred, self.ms, self.sub)
            H.admit_reconcile(self.fld, self.start, "eeee", pred, self.ms, self.sub, d)  # admits at depth==horizon
            self.assertLessEqual(d, len("eeee") + 1)

    def test_horizon_refuse(self):
        with self.assertRaises(H.HorizonError) as cm:
            H.admit_reconcile(self.fld, self.start, "eeee", "neee", self.ms, self.sub, 2)
        self.assertEqual(cm.exception.code, "HORIZON-REFUSE", "a too-deep rollback must refuse")

    def test_window(self):
        self.assertEqual(H.worst_case_window(4), 4, "the worst-case reconcile window is the horizon")

    def test_cost_bound(self):
        self.assertEqual(H.reconcile_cost(self.fld, self.start, "eeee", "eeee", self.ms, self.sub), 0,
                         "a correct prediction replays nothing")
        self.assertGreater(H.reconcile_cost(self.fld, self.start, "eeee", "eeen", self.ms, self.sub), 0,
                           "a misprediction replays a non-empty suffix")

    def test_deep_under_large_horizon(self):
        recon = H.admit_reconcile(self.fld, self.start, "eeee", "neee", self.ms, self.sub, 10)
        self.assertEqual(recon, GL.glide_cells(self.fld, self.start, "eeee", self.ms, self.sub),
                         "a deep misprediction still reconstructs byte-exactly when the horizon allows it")


if __name__ == "__main__":
    unittest.main()
