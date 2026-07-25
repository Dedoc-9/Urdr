# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/clockauth.py — CLOCK-AUTHORITY (URDRCLK1): bound the VIEW-TICK a client may
assert to its server-attested latency, closing the backdating-within-the-window abuse URDRLAG1 left. A cheater
can otherwise cherry-pick the most favourable tick in the lag window; clock-authority refuses any view-tick
the client's measured latency does not justify. Composition over `lagcomp` (over `hitbox`, over `perception`),
NO new glyph.

  CLOCK-CONSISTENT ADMIT — a view-tick matching the attested latency, geometrically valid, admits.
  BACKDATING TEETH — a cherry-picked older view-tick (inside the window, geometrically valid) is REFUSED with
    R_CLOCK, while the no-clock adjudicator admits it.
  FORWARD-SKEW — a view-tick fresher than the latency allows is REFUSED.
  ATTESTATION — a client-asserted latency cannot widen the band: the plant that trusts one admits a backdate
    the attested latency refuses.
  LATENCY-PROPORTIONAL — a higher-latency client legitimately gets an older admissible band.
  COMPOSITION — URDRLAG1's window/rewind and URDRHIT1's geometry hold: a wall-shadowed clock-consistent shot
    is refused.
  CONSTANT-SHAPE + PROOF-CARRYING — the verdict is fixed-length and carries the attested latency + band; a
    re-sealed forged ADMIT still fails.
  THE SWEEP BITES — a disabled clock band admits a backdate, so the seeded sweep RAISES.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import clockauth as CK                                            # noqa: E402
import hitbox as HB                                               # noqa: E402


def _sh():
    return HB.shooter(0, 0, 1, 0, 400)


class TheClockAuthority(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in CK.SCENES:
            self.assertEqual(CK.scene_result(name), CK.golden(name), name)
            self.assertEqual(CK.scene_result(name), CK.scene_result(name), name)

    def test_witness_blind_and_deterministic(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        before = CK.world_digest(tl, frozenset(), clk)
        v = CK.adjudicate(tl, frozenset(), _sh(), clk, (1, 7, 0, 97))
        self.assertEqual(CK.world_digest(tl, frozenset(), clk), before, "adjudication mutated the witness")
        self.assertEqual(v, CK.adjudicate(tl, frozenset(), _sh(), clk, (1, 7, 0, 97)), "not a pure function")

    def test_band_math(self):
        self.assertEqual(CK.band(100, CK.clock(3, 1)), (96, 98))
        self.assertEqual(CK.band(100, CK.clock(0, 0)), (100, 100))
        # the band clamps inside the lag window and never exceeds now
        lo, hi = CK.band(100, CK.clock(CK.MAX_REWIND + 5, 0))
        self.assertEqual(lo, 100 - CK.MAX_REWIND)
        self.assertLessEqual(hi, 100)


class TheClockConsistentAdmit(unittest.TestCase):
    def test_consistent_admits(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        self.assertTrue(CK.admit(tl, frozenset(), _sh(), clk, (1, 7, 0, 97)))
        rd = CK.read_verdict(CK.adjudicate(tl, frozenset(), _sh(), clk, (1, 7, 0, 97)))
        self.assertTrue(rd[8])                                    # admitted
        self.assertEqual((rd[4], rd[5]), (3, 1), "the verdict must carry the attested latency + jitter")
        self.assertEqual((rd[6], rd[7]), (96, 98), "the verdict must carry the enforced band")

    def test_laggy_client_gets_older_band(self):
        tl = CK._static_timeline(100, 7)
        # a high-latency client legitimately admits an older view-tick a low-latency one could not
        self.assertTrue(CK.admit(tl, frozenset(), _sh(), CK.clock(6, 1), (1, 7, 0, 94)))
        self.assertFalse(CK.admit(tl, frozenset(), _sh(), CK.clock(3, 1), (1, 7, 0, 94)),
                         "a low-latency client must not be able to claim a laggy view-tick")


class TheBackdatingTeeth(unittest.TestCase):
    def test_backdate_refused_no_clock_plant_bites(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)                                      # band [96,98]
        back = (1, 7, 0, 95)                                      # in the lag window, geometrically valid, older
        self.assertFalse(CK.admit(tl, frozenset(), _sh(), clk, back))
        self.assertEqual(CK._reason(tl, frozenset(), _sh(), clk, back), CK.R_CLOCK,
                         "a backdate must be refused specifically by the clock, not the geometry")
        self.assertTrue(CK._admit_no_clock(tl, frozenset(), _sh(), clk, back),
                        "the no-clock plant must admit the backdate the law refuses")

    def test_forward_skew_refused(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        fwd = (1, 7, 0, 100)                                      # fresher than lat allows (band tops at 98)
        self.assertFalse(CK.admit(tl, frozenset(), _sh(), clk, fwd))
        self.assertEqual(CK._reason(tl, frozenset(), _sh(), clk, fwd), CK.R_CLOCK)
        self.assertTrue(CK._admit_no_clock(tl, frozenset(), _sh(), clk, fwd))

    def test_client_asserted_latency_cannot_widen_band(self):
        """The attestation property: the law reads only the server-attested clock. A cheater claiming a
        larger latency (the `_admit_client_latency` plant) admits a backdate the attested clock refuses."""
        tl = CK._static_timeline(100, 7)
        attested = CK.clock(3, 1)
        back = (1, 7, 0, 95)
        self.assertFalse(CK.admit(tl, frozenset(), _sh(), attested, back))
        inflated = CK.clock(5, 1)                                 # the client lies about being laggier
        self.assertTrue(CK._admit_client_latency(tl, frozenset(), _sh(), inflated, back),
                        "trusting a client-asserted latency must admit the backdate — the reason to attest")


class TheComposition(unittest.TestCase):
    def test_wall_shadowed_clock_consistent_shot_refused(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        walls = frozenset({(10, 0)})
        claim = (2, 14, 0, 97)                                    # clock-consistent, but the far target is walled
        self.assertFalse(CK.admit(tl, walls, _sh(), clk, claim))
        self.assertEqual(CK._reason(tl, walls, _sh(), clk, claim), HB.R_WALL,
                         "URDRHIT1's occlusion must compose through clock-authority")

    def test_stale_beyond_window_still_refused(self):
        """A view-tick far below the band is clock-refused first; the composition never even reaches the lag
        window's stale check, but the claim is still refused (defence in depth)."""
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        self.assertFalse(CK.admit(tl, frozenset(), _sh(), clk, (1, 7, 0, 100 - CK.MAX_REWIND)))


class TheProofCarryingContract(unittest.TestCase):
    def test_constant_shape(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        a = CK.adjudicate(tl, frozenset(), _sh(), clk, (1, 7, 0, 97))      # admit
        b = CK.adjudicate(tl, frozenset(), _sh(), clk, (1, 7, 0, 95))      # clock refuse
        c = CK.adjudicate(tl, frozenset(), _sh(), clk, (9, 0, 0, 97))      # no target
        self.assertEqual(len(a), len(b))
        self.assertEqual(len(a), len(c))
        self.assertEqual(len(a), CK.verdict_bytes_len())

    def test_forged_admit_never_verifies(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        refuse_v = CK.adjudicate(tl, frozenset(), _sh(), clk, (1, 7, 0, 95))   # backdate → REFUSE
        forged = CK.forge_admit(refuse_v)
        self.assertTrue(CK.read_verdict(forged)[8], "the forgery should read as ADMIT to a naive client")
        self.assertFalse(CK.verify_verdict(tl, frozenset(), _sh(), clk, forged),
                         "a forged ADMIT verified — the proof-carrying contract broke")

    def test_verdict_bound_to_attested_clock(self):
        """A verdict issued under one attested clock does not verify under a different one — the clock is part
        of the authoritative input, not the claim."""
        tl = CK._static_timeline(100, 7)
        v = CK.adjudicate(tl, frozenset(), _sh(), CK.clock(3, 1), (1, 7, 0, 97))
        self.assertTrue(CK.verify_verdict(tl, frozenset(), _sh(), CK.clock(3, 1), v))
        self.assertFalse(CK.verify_verdict(tl, frozenset(), _sh(), CK.clock(6, 1), v),
                         "a verdict must not verify under a clock it was not issued for")

    def test_tampered_latency_reddens(self):
        tl = CK._static_timeline(100, 7)
        clk = CK.clock(3, 1)
        v = bytearray(CK.adjudicate(tl, frozenset(), _sh(), clk, (1, 7, 0, 97)))
        v[CK._HEADER + 16] ^= 0x01                                # flip a byte of the lat field, digest stale
        self.assertFalse(CK.verify_verdict(tl, frozenset(), _sh(), clk, bytes(v)))


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = CK.sweep_digest()
        self.assertEqual(d1, CK.sweep_digest(), "deterministic")
        self.assertEqual(d1, CK.sweep_golden(), "sweep drifted from golden")
        rep = CK.sweep()
        for k in ("admit_seen", "backdate_seen", "forward_seen", "attest_seen", "wall_seen"):
            self.assertGreater(rep[k], 0, f"{k} never exercised")

    def test_sweep_bites_disabled_clock(self):
        """L15 — a disabled clock band admits a backdated view-tick, so the seeded sweep RAISES; clean again
        after the revert."""
        orig = CK._clock_ok
        CK._clock_ok = lambda now, clk, vt: True                 # accept any view-tick
        try:
            with self.assertRaises(CK.ClockauthError):
                CK.sweep()
        finally:
            CK._clock_ok = orig
        self.assertEqual(CK.sweep_digest(), CK.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
