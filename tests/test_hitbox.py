# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/hitbox.py — SERVER-AUTHORITATIVE HIT VALIDATION (URDRHIT1): the ACTIVE
channel of the anti-cheat firewall. Witnessed/audible absence govern what a client RECEIVES; this governs
what a client CLAIMS. A claimed hit is adjudicated against the AUTHORITATIVE world; an unearned hit is
un-addressed — the client cannot manufacture an ADMIT. Composition over `perception`, NO new glyph.

  SERVER-AUTHORITY — the verdict is a pure function of (world, claim), never of a client-supplied extent.
  CLEAN ADMITS — a legitimate hit (on-box, on-ray, in-range, unoccluded) admits (non-vacuity).
  PHANTOM / OFF-RAY / OUT-OF-RANGE / WALL-SHOT / INFLATED — each forgery is REFUSED, and each PLANT
    (a version that skips exactly that check, or trusts the client's extent) ADMITS where the law refuses.
  CONSTANT-SHAPE + PROOF-CARRYING — the verdict is fixed-length; a re-sealed forged ADMIT still fails
    verify_verdict, because a fresh authoritative adjudication disagrees.
  THE SWEEP BITES — a skipped-occlusion adjudicator admits a wall-shot, so the seeded sweep RAISES.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import hitbox as HB                                               # noqa: E402


def _d(i):
    return HB._d(i)


class TheHitFirewall(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in HB.SCENES:
            self.assertEqual(HB.scene_result(name), HB.golden(name), name)
            self.assertEqual(HB.scene_result(name), HB.scene_result(name), name)

    def test_witness_blind_and_deterministic(self):
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        before = HB.world_digest(tg, frozenset())
        v = HB.adjudicate(tg, frozenset(), sh, (1, 10, 0))
        self.assertEqual(HB.world_digest(tg, frozenset()), before, "adjudication mutated the witness")
        self.assertEqual(v, HB.adjudicate(tg, frozenset(), sh, (1, 10, 0)), "not a pure function")

    def test_clean_hit_admits(self):
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        self.assertTrue(HB.admit(tg, frozenset(), sh, (1, 10, 0)))
        eid, hx, hy, admitted, reason, cite = HB.read_verdict(HB.adjudicate(tg, frozenset(), sh, (1, 10, 0)))
        self.assertTrue(admitted)
        self.assertEqual(reason, HB.R_ADMIT)
        self.assertEqual(cite, tg[1][4], "an ADMIT verdict must carry the target's authority citation")


class TheFiveRefusals(unittest.TestCase):
    def setUp(self):
        self.tg = {1: (10, 0, 1, 1, _d(1))}
        self.sh = HB.shooter(0, 0, 1, 0, 400)

    def test_phantom_off_box_refused_plant_bites(self):
        claim = (1, 13, 0)                                        # on the ray but past the box
        self.assertFalse(HB.admit(self.tg, frozenset(), self.sh, claim))
        self.assertEqual(HB._reason(self.tg, frozenset(), self.sh, claim), HB.R_OFFBOX)
        self.assertTrue(HB._admit_no_box(self.tg, frozenset(), self.sh, claim),
                        "the phantom-hit plant (skip the box test) must admit where the law refuses")

    def test_offray_refused_plant_bites(self):
        claim = (1, 10, 1)                                        # a box corner off the aim line
        self.assertFalse(HB.admit(self.tg, frozenset(), self.sh, claim))
        self.assertEqual(HB._reason(self.tg, frozenset(), self.sh, claim), HB.R_OFFRAY)
        self.assertTrue(HB._admit_no_ray(self.tg, frozenset(), self.sh, claim),
                        "the aimbot plant (skip the ray test) must admit where the law refuses")

    def test_out_of_range_refused_plant_bites(self):
        tg = {1: (30, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 100)                          # reach 100 < d²=900
        claim = (1, 30, 0)
        self.assertFalse(HB.admit(tg, frozenset(), sh, claim))
        self.assertEqual(HB._reason(tg, frozenset(), sh, claim), HB.R_RANGE)
        self.assertTrue(HB._admit_no_range(tg, frozenset(), sh, claim),
                        "the out-of-range plant (skip the range test) must admit where the law refuses")

    def test_wallshot_refused_plant_bites(self):
        walls = frozenset({(5, 0)})
        claim = (1, 10, 0)
        self.assertFalse(HB.admit(self.tg, walls, self.sh, claim))
        self.assertEqual(HB._reason(self.tg, walls, self.sh, claim), HB.R_WALL)
        self.assertTrue(HB._admit_no_occlusion(self.tg, walls, self.sh, claim),
                        "the wall-shoot plant (skip the occlusion test) must admit where the law refuses")

    def test_inflated_hitbox_gains_nothing_plant_bites(self):
        claim = (1, 13, 0)                                        # off the real box
        self.assertFalse(HB.admit(self.tg, frozenset(), self.sh, claim))
        self.assertTrue(HB._admit_client_extent(self.tg, frozenset(), self.sh, (1, 13, 0, 4, 4)),
                        "the inflated-hitbox plant (trust the client extent) must admit off the real box")


class TheServerAuthority(unittest.TestCase):
    def test_verdict_ignores_any_client_extent(self):
        """The verdict is a pure function of (world, claim point) — the claim carries no extent the server
        reads, so no client assertion about hitbox size can change the outcome."""
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        off_box = (1, 13, 0)
        # whatever extent a cheat pretends, the authoritative adjudication refuses the off-real-box point
        self.assertFalse(HB.admit(tg, frozenset(), sh, off_box))
        for chbx, chby in ((3, 3), (5, 5), (100, 100)):
            self.assertTrue(HB._admit_client_extent(tg, frozenset(), sh, (1, 13, 0, chbx, chby)))
            # the honest verdict is unmoved regardless of the pretended extent
            self.assertFalse(HB.read_verdict(HB.adjudicate(tg, frozenset(), sh, off_box))[3])

    def test_verdict_constant_shape(self):
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        admit_v = HB.adjudicate(tg, frozenset(), sh, (1, 10, 0))
        refuse_v = HB.adjudicate(tg, frozenset(), sh, (1, 13, 0))
        notarget_v = HB.adjudicate(tg, frozenset(), sh, (99, 0, 0))
        self.assertEqual(len(admit_v), len(refuse_v))
        self.assertEqual(len(admit_v), len(notarget_v))
        self.assertEqual(len(admit_v), HB.verdict_bytes_len())

    def test_refuse_verdict_carries_zero_cite(self):
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        _e, _x, _y, admitted, _r, cite = HB.read_verdict(HB.adjudicate(tg, frozenset(), sh, (1, 13, 0)))
        self.assertFalse(admitted)
        self.assertEqual(cite, "00" * HB.DIGEST_BYTES, "a REFUSE must not leak a citation")


class TheProofCarryingContract(unittest.TestCase):
    def test_honest_verdict_verifies(self):
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        for claim in ((1, 10, 0), (1, 13, 0), (1, 10, 1)):
            self.assertTrue(HB.verify_verdict(tg, frozenset(), sh, HB.adjudicate(tg, frozenset(), sh, claim)))

    def test_forged_admit_never_verifies(self):
        """A re-sealed forged ADMIT (valid self-digest, verdict flipped) still fails — a fresh authoritative
        adjudication of the same claim disagrees. The server, not the client, decides."""
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        walls = frozenset({(5, 0)})
        refuse_v = HB.adjudicate(tg, walls, sh, (1, 10, 0))       # a wall-shot → REFUSE
        forged = HB.forge_admit(refuse_v)
        self.assertTrue(HB.read_verdict(forged)[3], "the forgery should read as ADMIT to a naive client")
        self.assertFalse(HB.verify_verdict(tg, walls, sh, forged),
                         "a forged ADMIT verified — the proof-carrying contract broke")

    def test_tampered_verdict_reddens(self):
        tg = {1: (10, 0, 1, 1, _d(1))}
        sh = HB.shooter(0, 0, 1, 0, 400)
        v = bytearray(HB.adjudicate(tg, frozenset(), sh, (1, 10, 0)))
        v[HB._HEADER + 4] ^= 0x01                                 # flip a byte of hx, leave the digest stale
        self.assertFalse(HB.verify_verdict(tg, frozenset(), sh, bytes(v)))


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = HB.sweep_digest()
        self.assertEqual(d1, HB.sweep_digest(), "deterministic")
        self.assertEqual(d1, HB.sweep_golden(), "sweep drifted from golden")
        rep = HB.sweep()
        self.assertGreater(rep["admit_seen"], 0, "no legitimate hit was ever admitted")
        self.assertGreater(rep["wall_seen"], 0, "no wall-shot was ever exercised")
        self.assertGreater(rep["offray_seen"], 0, "no off-ray claim was ever exercised")
        self.assertGreater(rep["inflated_seen"], 0, "the inflated-extent plant was never exercised")

    def test_sweep_bites_skipped_occlusion(self):
        """L15 — an adjudicator that skips the line-of-fire occlusion admits a wall-shot, so the seeded
        sweep RAISES; clean again after the revert."""
        orig = HB._clear_los
        HB._clear_los = lambda *a: True                          # skip occlusion → wall-shots admit
        try:
            with self.assertRaises(HB.HitboxError):
                HB.sweep()
        finally:
            HB._clear_los = orig
        self.assertEqual(HB.sweep_digest(), HB.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
