# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/lagcomp.py — TEMPORAL LAG-COMPENSATION (URDRLAG1): the refinement that earns
the hit channel (URDRHIT1) its teeth against MOVING targets. A shooter fired at what they saw — an earlier
tick — so the server rewinds the target to the shooter's view-tick and adjudicates there, within a bounded
window. Composition over `hitbox` (over `perception`), NO new glyph.

  REWIND TEETH — a legitimate shot at a target that has since moved away is ADMITTED by rewinding, while the
    no-rewind adjudicator at `now` REFUSES it (non-vacuous: the target actually moved).
  WINDOW BOUND — a future claim (vt > now) and an over-old claim (vt < now - MAX_REWIND) are REFUSED, each
    plant (clamp-future / unbounded-rewind) admitting where the law refuses (anti-abuse).
  COMPOSED GEOMETRY — URDRHIT1's refusals hold at the rewound tick: a wall-shadowed rewound shot is refused.
  CONSTANT-SHAPE + PROOF-CARRYING — the verdict is fixed-length and carries the view-tick + the exact rewound
    position; a re-sealed forged ADMIT still fails verify_verdict.
  THE SWEEP BITES — a no-rewind adjudicator refuses a legitimate moving-target shot, so the seeded sweep RAISES.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import lagcomp as LC                                              # noqa: E402
import hitbox as HB                                               # noqa: E402


def _sh():
    return HB.shooter(0, 0, 1, 0, 400)


class TheLagCompensation(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in LC.SCENES:
            self.assertEqual(LC.scene_result(name), LC.golden(name), name)
            self.assertEqual(LC.scene_result(name), LC.scene_result(name), name)

    def test_witness_blind_and_deterministic(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        before = LC.world_digest(tl, frozenset())
        v = LC.adjudicate(tl, frozenset(), _sh(), (1, 7, 0, 95))
        self.assertEqual(LC.world_digest(tl, frozenset()), before, "adjudication mutated the witness")
        self.assertEqual(v, LC.adjudicate(tl, frozenset(), _sh(), (1, 7, 0, 95)), "not a pure function")


class TheRewindTeeth(unittest.TestCase):
    def test_rewind_admits_moved_target_no_rewind_refuses(self):
        """The core value: the target was on the crosshair at vt=95 and has drifted off by now=100. Rewinding
        admits the shot; the no-rewind adjudicator at `now` refuses it."""
        tl = LC._moving_timeline(100, 7, 95, 2)
        claim = (1, 7, 0, 95)
        self.assertTrue(LC.admit(tl, frozenset(), _sh(), claim), "the rewound shot should admit")
        self.assertFalse(LC._admit_no_rewind(tl, frozenset(), _sh(), claim),
                         "the no-rewind adjudicator must refuse the moved target — else the teeth are vacuous")

    def test_verdict_carries_rewound_position(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        eid, hx, hy, vt, admitted, reason, rex, rey, cite = LC.read_verdict(
            LC.adjudicate(tl, frozenset(), _sh(), (1, 7, 0, 95)))
        self.assertTrue(admitted)
        self.assertEqual((rex, rey), (7, 0), "the verdict must record the exact rewound position used")
        self.assertEqual(cite, tl[95][1][4], "an ADMIT verdict carries the rewound target's citation")

    def test_target_that_did_not_move_is_a_noop(self):
        """Sanity: with the target static on-axis at every tick, rewind and no-rewind agree (the teeth need a
        moving target to have value — this documents the boundary, it does not fail)."""
        tl = {t: {1: (7, 0, 1, 1, LC._d(1))} for t in range(90, 101)}
        claim = (1, 7, 0, 95)
        self.assertTrue(LC.admit(tl, frozenset(), _sh(), claim))
        self.assertTrue(LC._admit_no_rewind(tl, frozenset(), _sh(), claim))


class TheWindowBound(unittest.TestCase):
    def test_stale_refused_unbounded_plant_bites(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        stale = (3, 6, 0, 100 - (LC.MAX_REWIND + 1))              # one tick past the window
        self.assertFalse(LC.admit(tl, frozenset(), _sh(), stale))
        self.assertEqual(LC._reason(tl, frozenset(), _sh(), stale), LC.R_STALE)
        self.assertTrue(LC._admit_no_window(tl, frozenset(), _sh(), stale),
                        "the unbounded-rewind plant must admit the over-old claim the law refuses")

    def test_future_refused_clamp_plant_bites(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        future = (3, 6, 0, 101)
        self.assertFalse(LC.admit(tl, frozenset(), _sh(), future))
        self.assertEqual(LC._reason(tl, frozenset(), _sh(), future), LC.R_FUTURE)
        self.assertTrue(LC._admit_clamp_future(tl, frozenset(), _sh(), future),
                        "the clamp-future plant must admit the future claim the law refuses")

    def test_window_edges(self):
        tl = LC._moving_timeline(100, 3, 95, 2)                  # id3 static at (6,0); use it on-axis
        # exactly at the oldest honoured tick (now - MAX_REWIND) is inside the window
        self.assertNotEqual(LC._reason(tl, frozenset(), _sh(), (3, 6, 0, 100 - LC.MAX_REWIND)), LC.R_STALE)
        # one tick older is stale
        self.assertEqual(LC._reason(tl, frozenset(), _sh(), (3, 6, 0, 100 - LC.MAX_REWIND - 1)), LC.R_STALE)


class TheComposedGeometry(unittest.TestCase):
    def test_wall_shadowed_rewound_shot_refused(self):
        """Lag-comp moves the target in time, it does not open a wall: the far target behind a wall is refused
        at the rewound tick (URDRHIT1's occlusion composes)."""
        tl = LC._moving_timeline(100, 7, 95, 2)
        walls = frozenset({(10, 0)})
        claim = (2, 14, 0, 95)
        self.assertFalse(LC.admit(tl, walls, _sh(), claim))
        self.assertEqual(LC._reason(tl, walls, _sh(), claim), HB.R_WALL)

    def test_off_box_rewound_shot_refused(self):
        tl = LC._moving_timeline(100, 7, 95, 2)                  # id1 at (7,0) at vt=95
        self.assertFalse(LC.admit(tl, frozenset(), _sh(), (1, 11, 0, 95)),  # on ray, past the box
                         "an off-box point at the rewound tick must still be refused")
        self.assertEqual(LC._reason(tl, frozenset(), _sh(), (1, 11, 0, 95)), HB.R_OFFBOX)


class TheProofCarryingContract(unittest.TestCase):
    def test_constant_shape(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        a = LC.adjudicate(tl, frozenset(), _sh(), (1, 7, 0, 95))          # admit
        b = LC.adjudicate(tl, frozenset(), _sh(), (3, 6, 0, 80))          # stale refuse
        c = LC.adjudicate(tl, frozenset(), _sh(), (9, 0, 0, 101))         # future / no target
        self.assertEqual(len(a), len(b))
        self.assertEqual(len(a), len(c))
        self.assertEqual(len(a), LC.verdict_bytes_len())

    def test_honest_verdict_verifies(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        for claim in ((1, 7, 0, 95), (3, 6, 0, 80), (2, 14, 0, 95)):
            self.assertTrue(LC.verify_verdict(tl, frozenset({(10, 0)}), _sh(),
                                              LC.adjudicate(tl, frozenset({(10, 0)}), _sh(), claim)))

    def test_forged_admit_never_verifies(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        walls = frozenset({(10, 0)})
        refuse_v = LC.adjudicate(tl, walls, _sh(), (2, 14, 0, 95))        # wall-shadowed → REFUSE
        forged = LC.forge_admit(refuse_v)
        self.assertTrue(LC.read_verdict(forged)[4], "the forgery should read as ADMIT to a naive client")
        self.assertFalse(LC.verify_verdict(tl, walls, _sh(), forged),
                         "a forged ADMIT verified — the proof-carrying contract broke")

    def test_tampered_view_tick_reddens(self):
        tl = LC._moving_timeline(100, 7, 95, 2)
        v = bytearray(LC.adjudicate(tl, frozenset(), _sh(), (1, 7, 0, 95)))
        v[LC._HEADER + 12] ^= 0x01                                # flip a byte of vt, leave the digest stale
        self.assertFalse(LC.verify_verdict(tl, frozenset(), _sh(), bytes(v)))


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = LC.sweep_digest()
        self.assertEqual(d1, LC.sweep_digest(), "deterministic")
        self.assertEqual(d1, LC.sweep_golden(), "sweep drifted from golden")
        rep = LC.sweep()
        self.assertGreater(rep["rewind_seen"], 0, "the rewind teeth were never exercised")
        self.assertGreater(rep["stale_seen"], 0, "the stale bound was never exercised")
        self.assertGreater(rep["future_seen"], 0, "the future bound was never exercised")
        self.assertGreater(rep["wall_seen"], 0, "composed geometry was never exercised")

    def test_sweep_bites_no_rewind(self):
        """L15 — an adjudicator that never rewinds (always uses `now`) refuses a legitimate moving-target
        shot, so the seeded sweep RAISES; clean again after the revert."""
        orig = LC._snapshot_at
        LC._snapshot_at = lambda tl, vt: tl[LC.timeline_now(tl)]     # disable the rewind
        try:
            with self.assertRaises(LC.LagcompError):
                LC.sweep()
        finally:
            LC._snapshot_at = orig
        self.assertEqual(LC.sweep_digest(), LC.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
