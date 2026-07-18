# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for cross-region structural anti-cheat (`tools/terrain/crosswarden.py`, T3.25, MMO Stage E, the
D+E synthesis) — the seamless handoff seam is made CHEAT-PROOF. A claimed crossing is admitted against the
MERGED authority (`hand.merge`), not against either shard's stale view of its neighbor, or a typed
WARD-REFUSE.

  * REFERENCE — the two pinned scenarios reproduce their URDRWARD2 digests, deterministically;
  * MERGE IS THE HANDOFF'S MERGE — the field the crossing is certified against is `hand.merge` bit-for-bit
    (Stage E certifies against exactly the world Stage D produces);
  * HONEST CROSSING ADMITS — an actor that crosses the seam and stops before B's wall admits;
  * SEAM TUNNEL REFUSED — a crossing that steps through B's wall is `WARD-TUNNEL` against the merge;
  * SHARD-LOCAL INSUFFICIENT (the headline) — the exploit trajectory AND the exploit position both ADMIT
    under a shard-local `warden(F_A)` (A's stale flat view passes the cheat) while `crosswarden` REFUSES both;
    only the merged-authority warden catches the boundary exploit;
  * CROSS POSITION UNREACHABLE — a bare cell beyond B's wall, claimed from a west anchor, is `WARD-UNREACH`
    against the merge, from the merged field alone;
  * MERGE TOPOLOGY RISES (non-vacuity) — β₀(F_merged) = 3 genuinely exceeds β₀(F_A) = 1: B's wall adds real
    component structure the stale shard cannot see;
  * DESYNCED BAND REFUSED — a handoff whose seam band is not synced is `WARD-SEAM` (no canonical merge);
  * HONEST HANDOFF ADMITS AND EQUALS MERGED GLIDE — a real `hand.handoff` trajectory admits under the
    cross-region warden and equals `hand.merged_glide` bit-for-bit (the Stage D <-> Stage E tie);
  * REFUSAL — every refusal is a typed `WARD-REFUSE` with a sub-code; a malformed claim is `WARD-MALFORMED`.

Composes the handoff (`hand`), the single-field warden (`warden`), and the mover (`glide`); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import crosswarden as CW                                         # noqa: E402
import warden as W                                               # noqa: E402
import hand as H                                                 # noqa: E402


class CrossWarden(unittest.TestCase):
    def setUp(self):
        self.fa, self.fb = CW._shards()
        self.ms, self.split, self.band = CW._MS, CW._SPLIT, CW._BAND

    def test_scene_goldens(self):
        for name in CW.SCENES:
            dig = CW.scene_result(name)
            self.assertEqual(dig, CW.golden(name), f"{name}: crosswarden digest drifted")
            self.assertEqual(CW.scene_result(name), dig, f"{name}: nondeterministic")

    def test_merge_is_hand_merge(self):
        self.assertEqual(CW.merged_field(self.fa, self.fb, self.split),
                         H.merge(self.fa, self.fb, self.split),
                         "the certified world must be hand's merge bit-for-bit")

    def test_honest_crossing_admits(self):
        self.assertEqual(CW.admit_crossing(self.fa, self.fb, self.split, self.band, CW._HONEST_CELLS, self.ms),
                         "WARD-OK", "an honest seam crossing that stops before the wall must admit")

    def test_seam_tunnel_refused(self):
        with self.assertRaises(W.WardError) as cm:
            CW.admit_crossing(self.fa, self.fb, self.split, self.band, CW._TUNNEL_CELLS, self.ms)
        self.assertEqual(cm.exception.sub, "WARD-TUNNEL", "stepping through B's wall must be a tunnel refusal")

    def test_shard_local_insufficient(self):
        """THE HEADLINE — a shard-local warden on F_A ADMITS both exploits the cross-region warden refuses."""
        # trajectory exploit: shard-local A admits (flat stale view), crosswarden refuses
        self.assertTrue(CW.shard_admits_trajectory(self.fa, CW._TUNNEL_CELLS, self.ms),
                        "shard-local F_A must (wrongly) admit the through-wall sprint")
        with self.assertRaises(W.WardError):
            CW.admit_crossing(self.fa, self.fb, self.split, self.band, CW._TUNNEL_CELLS, self.ms)
        # position exploit: shard-local A admits, crosswarden refuses
        self.assertTrue(CW.shard_admits_position(self.fa, CW._ANCHOR, CW._BEYOND, self.ms),
                        "shard-local F_A must (wrongly) admit the beyond-wall position")
        with self.assertRaises(W.WardError):
            CW.admit_crossing_position(self.fa, self.fb, self.split, self.band, CW._ANCHOR, CW._BEYOND, self.ms)

    def test_cross_position_unreachable(self):
        with self.assertRaises(W.WardError) as cm:
            CW.admit_crossing_position(self.fa, self.fb, self.split, self.band, CW._ANCHOR, CW._BEYOND, self.ms)
        self.assertEqual(cm.exception.sub, "WARD-UNREACH", "a cell beyond B's wall must be unreachable vs merge")

    def test_merge_topology_rises(self):
        self.assertEqual(CW.cross_betti0(self.fa, self.fb, self.split, self.ms), 3, "the merge must have b0 = 3")
        self.assertEqual(W.betti0(self.fa, self.ms), 1, "the stale shard is one flat component")
        self.assertGreater(CW.cross_betti0(self.fa, self.fb, self.split, self.ms), W.betti0(self.fa, self.ms),
                           "the merge must gain component structure the stale shard cannot see")

    def test_desynced_band_refused(self):
        fad, fbd = CW._desynced_shards()
        with self.assertRaises(W.WardError) as cm:
            CW.admit_crossing(fad, fbd, self.split, self.band, CW._HONEST_CELLS, self.ms)
        self.assertEqual(cm.exception.sub, "WARD-SEAM", "a desynced seam band has no canonical merge")

    def test_honest_handoff_admits_and_equals_merged(self):
        start, cmds, sub, at = (2, 8), "eeeeeee", 4, 5
        traj = H.handoff(self.fa, self.fb, start, cmds, self.ms, sub, at, self.split, self.band)
        cells = tuple((p[0] >> 32, p[1] >> 32) for p in traj)
        self.assertEqual(CW.admit_crossing(self.fa, self.fb, self.split, self.band, cells, self.ms), "WARD-OK",
                         "an honest hand.handoff trajectory must admit under the cross-region warden")
        self.assertEqual(traj, H.merged_glide(self.fa, self.fb, start, cmds, self.ms, sub, self.split),
                         "the handoff must equal the merged glide — the warden certifies the handoff's world")

    def test_typed_refusals(self):
        # malformed claim
        with self.assertRaises(W.WardError) as cm:
            CW.admit_crossing(self.fa, self.fb, self.split, self.band, (), self.ms)
        self.assertEqual(cm.exception.sub, "WARD-MALFORMED")
        # every cheat refusal carries the WARD-REFUSE code with a sub-code
        try:
            CW.admit_crossing(self.fa, self.fb, self.split, self.band, CW._TUNNEL_CELLS, self.ms)
        except W.WardError as exc:
            self.assertEqual(exc.code, "WARD-REFUSE")
            self.assertEqual(exc.sub, "WARD-TUNNEL")


if __name__ == "__main__":
    unittest.main()
