# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the snapshot-storage envelope (`tools/terrain/storecost.py`, T3.35, MMO Stage H) — the SPACE
companion to horizon's time bound: the exact bytes a depth-H rollback window costs, with a STORAGE-REFUSE past a
memory budget. snapshot_bytes(n) = 4 + 25*n checked EQUAL to a real serialization; window = (H+1)*snapshot_bytes.

  * REFERENCE — the three pinned configs reproduce their URDRLAT4 digests, deterministically;
  * SERIALIZE SOUNDNESS — snapshot_bytes(N) EQUALS len(serialize(real glide state)) over a corpus (the byte
    count is measured against reality, not assumed);
  * ROUND-TRIP + OVERFLOW — deserialize(serialize(state)) == state bit-for-bit; an out-of-range field is a
    typed STORAGE-REFUSE (never a silent truncation);
  * WINDOW — window_storage(H, n) == (H+1)*snapshot_bytes(n), strictly increasing in H and in N;
  * HORIZON TIE — retained_snapshots(H) == horizon.worst_case_window(H) + 1 (a depth-H window is H+1 boundaries);
  * BUDGET ADMIT — a window within the memory budget ADMITS;
  * OVER-BUDGET REFUSE — a window exceeding the budget is a typed STORAGE-REFUSE;
  * DEFECT DIVERGES — a changed horizon / actor count moves the URDRLAT4 digest.

Composes `glide` (the boundary poses), `horizon` (the window), and `opcost`; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import storecost as SC                                          # noqa: E402
import horizon as HZ                                            # noqa: E402


class Storecost(unittest.TestCase):
    def setUp(self):
        self.fld = SC._flat16()
        self.starts = ((2, 4), (2, 6), (2, 8), (2, 10), (2, 12), (3, 8), (4, 8))

    def _state(self, n, boundary=4):
        return SC.boundary_state(self.fld, self.starts[:n], "eeee", 40, 4, boundary)

    def test_scene_goldens(self):
        for name in SC.SCENES:
            dig = SC.scene_result(name)
            self.assertEqual(dig, SC.golden(name), f"{name}: storecost digest drifted")
            self.assertEqual(SC.scene_result(name), dig, f"{name}: nondeterministic")

    def test_serialize_soundness(self):
        for n in (1, 2, 3, 5, 7):
            for b in (0, 1, 2, 4):
                state = self._state(n, b)
                self.assertEqual(len(SC.serialize(state)), SC.snapshot_bytes(n),
                                 f"serialized length must equal the closed form (n={n} b={b})")
                self.assertTrue(SC.serialize_is_exact(state), f"soundness must hold (n={n} b={b})")

    def test_roundtrip_and_overflow(self):
        for n in (1, 3, 5):
            state = self._state(n)
            self.assertEqual(SC.deserialize(SC.serialize(state)), state, "round-trip must be byte-exact")
        with self.assertRaises(SC.StoreError) as cm:
            SC.serialize(((1 << 63, 0, 0, 0),))                 # beyond int64
        self.assertEqual(cm.exception.code, "STORAGE-REFUSE", "an over-range field must refuse, not truncate")

    def test_window_monotone(self):
        for n in (1, 3, 5):
            for h in (0, 1, 2, 4, 8):
                self.assertEqual(SC.window_storage(h, n), (h + 1) * SC.snapshot_bytes(n),
                                 "window must be (H+1) * snapshot_bytes")
        self.assertLess(SC.window_storage(4, 5), SC.window_storage(8, 5), "window must grow with H")
        self.assertLess(SC.window_storage(8, 1), SC.window_storage(8, 5), "window must grow with N")

    def test_horizon_tie(self):
        for h in (0, 1, 3, 5, 10):
            self.assertEqual(SC.retained_snapshots(h), HZ.worst_case_window(h) + 1,
                             "a depth-H window retains worst_case_window(H)+1 boundary snapshots")

    def test_budget_admit(self):
        self.assertTrue(SC.within_storage_budget(SC.window_storage(4, 1), 10000),
                        "a window within budget must admit")

    def test_over_budget_refuse(self):
        with self.assertRaises(SC.StoreError) as cm:
            SC.within_storage_budget(SC.window_storage(8, 5), 1000)
        self.assertEqual(cm.exception.code, "STORAGE-REFUSE", "an over-budget window must refuse")

    def test_defect_diverges(self):
        base = SC.storecost_digest("x", 5, 8, SC.snapshot_bytes(5), SC.window_storage(8, 5), "ADMIT")
        other = SC.storecost_digest("x", 5, 4, SC.snapshot_bytes(5), SC.window_storage(4, 5), "ADMIT")
        self.assertNotEqual(base, other, "a changed horizon must move the digest")


if __name__ == "__main__":
    unittest.main()
