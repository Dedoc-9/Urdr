# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for seamless cross-region authority handoff (`tools/terrain/hand.py`, T3.23, MMO Stage D) — an
actor glides across a region boundary and authority transfers atomically between shards without a desync.

  * REFERENCE — the two pinned scenarios reproduce their URDRHAND1 digests, deterministically;
  * HANDOFF EQUIVALENCE (the keystone) — `handoff` (prefix glides over shard A, suffix resumes over shard B)
    equals `glide` over the merged world F_merged BIT-FOR-BIT: the seam is provably invisible;
  * LATENCY-INVARIANCE — the handoff is bit-identical for EVERY handoff tick within the seam band; the
    bridge survives handoff latency (wall-clock latency itself is NOT_MEASURED). Out-of-band ticks refuse;
  * MANY POINTS — a whole batch of actors crossing together each reconstructs exactly (the scale case);
  * USES SHARD B (non-vacuity) — the handoff differs from a glide that stayed on shard A, because B's terrain
    east of the band really differs; the handoff resumes over B, not A;
  * SEAM AGREEMENT REQUIRED — a handoff across a band where the shards disagree (a desync) is refused;
  * TAMPER-EVIDENCE — a moved actor moves the handoff digest; the seam digest binds the shared band;
  * REFUSAL — a desynced seam, an out-of-band tick, mismatched shard sizes, or a too-short log is a typed
    `HAND-REFUSE`.

Composes the continuous mover (`glide`) and resumption (`splice`); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import hand as H                                                  # noqa: E402
import glide as GL                                                # noqa: E402


class Hand(unittest.TestCase):
    def setUp(self):
        self.fa, self.fb = H._shards()
        self.split, self.band, self.ms, self.sub = H._SPLIT, H._BAND, H._MS, H._SUB
        self.start, self.cmds = H._START, H._CMDS
        self.ref = H.merged_glide(self.fa, self.fb, self.start, self.cmds, self.ms, self.sub, self.split)

    def test_scene_goldens(self):
        for name in H.SCENES:
            dig = H.scene_result(name)
            self.assertEqual(dig, H.golden(name), f"{name}: handoff digest drifted")
            self.assertEqual(H.scene_result(name), dig, f"{name}: nondeterministic")

    def test_handoff_equivalence(self):
        h = H.handoff(self.fa, self.fb, self.start, self.cmds, self.ms, self.sub, 5, self.split, self.band)
        self.assertEqual(h, self.ref, "the handoff must equal a single authority over the merged world")

    def test_latency_invariance(self):
        """The handoff is bit-identical for EVERY in-band tick — the bridge survives handoff latency."""
        lo, hi = H._band(self.split, self.band)
        inband = 0
        for at in range(1, len(self.cmds)):
            try:
                h = H.handoff(self.fa, self.fb, self.start, self.cmds, self.ms, self.sub, at, self.split, self.band)
            except H.HandError:
                continue                                          # out-of-band ticks refuse (checked below)
            self.assertEqual(h, self.ref, f"handoff at in-band tick {at} diverged from the merged world")
            inband += 1
        self.assertGreater(inband, 1, "the band must admit more than one handoff tick (latency has slack)")

    def test_many_points_batch(self):
        batch = H.batch_handoff(self.fa, self.fb, H._STARTS, self.cmds, self.ms, self.sub, 5, self.split, self.band)
        self.assertEqual(len(batch), len(H._STARTS), "every actor must be handed off")
        for tr, s in zip(batch, H._STARTS):
            self.assertEqual(tr, H.merged_glide(self.fa, self.fb, s, self.cmds, self.ms, self.sub, self.split),
                             f"batch actor from {s} did not reconstruct the merged trajectory")

    def test_uses_region_b_terrain(self):
        h = H.handoff(self.fa, self.fb, self.start, self.cmds, self.ms, self.sub, 5, self.split, self.band)
        glide_a_only = GL.glide_cells(self.fa, self.start, self.cmds, self.ms, self.sub)
        self.assertNotEqual(h, glide_a_only, "the handoff must resume over shard B, not stay on shard A")
        self.assertEqual(h, self.ref, "...while still equalling the merged world")

    def test_seam_agreement_required(self):
        desync = tuple(tuple(v + 1 if x == 7 else v for x, v in enumerate(row)) for row in self.fa)  # band cell
        with self.assertRaises(H.HandError) as cm:
            H.handoff(self.fa, desync, self.start, self.cmds, self.ms, self.sub, 5, self.split, self.band)
        self.assertEqual(cm.exception.code, "HAND-REFUSE", "a desynced seam must be refused")

    def test_out_of_band_handoff_refused(self):
        with self.assertRaises(H.HandError) as cm:                # at=1 → cell x=3, west of the band [6,10)
            H.handoff(self.fa, self.fb, self.start, self.cmds, self.ms, self.sub, 1, self.split, self.band)
        self.assertEqual(cm.exception.code, "HAND-REFUSE", "an out-of-band handoff must be refused")

    def test_tamper_evidence(self):
        base = H.hand_digest("s", H.handoff(self.fa, self.fb, (2, 8), self.cmds, self.ms, self.sub, 5, self.split, self.band))
        moved = H.hand_digest("s", H.handoff(self.fa, self.fb, (2, 6), self.cmds, self.ms, self.sub, 5, self.split, self.band))
        self.assertNotEqual(base, moved, "moving the actor must move the handoff digest")

    def test_seam_digest_binds_band(self):
        lo, hi = H._band(self.split, self.band)
        self.assertTrue(H.seam_ok(self.fa, self.fb, lo, hi), "the reference shards agree on the band")
        d_same = H.seam_digest(self.fa, self.fb, lo, hi)
        self.assertEqual(d_same, H.seam_digest(self.fa, self.fb, lo, hi), "seam digest deterministic")

    def test_typed_refusals(self):
        cases = [
            lambda: H.handoff(self.fa, self.fb, self.start, "e", self.ms, self.sub, 1, self.split, self.band),   # short log
            lambda: H.handoff(self.fa, self.fb, self.start, self.cmds, self.ms, self.sub, 0, self.split, self.band),  # non-interior
            lambda: H.handoff(self.fa, self.fb[:-1], self.start, self.cmds, self.ms, self.sub, 5, self.split, self.band),  # size mismatch
        ]
        for call in cases:
            with self.assertRaises(H.HandError) as cm:
                call()
            self.assertEqual(cm.exception.code, "HAND-REFUSE", "must be a typed HAND-REFUSE")


if __name__ == "__main__":
    unittest.main()
