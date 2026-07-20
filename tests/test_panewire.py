# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/panewire.py — V2, the wired window (URDRPNW1).

The whole arc composed in one live loop: MOVEMENT (panelight's tick), REPLICATION
(wire's equal-or-refuse admission), and STREAMING (driftgaze's verified acquisition)
driving one avatar over a REPLICATED, STREAMED world. The first playable networked
world. panewire MINTS NOTHING — it is pure composition — and certifies four laws
that only exist when the three meet:

  RESIDENT-OR-REFUSE — the avatar folds over the resident REPLICA, not the field; a
  step into an unresident region refuses (the avatar cannot walk on unloaded
  terrain) until the region is ACQUIRED by verified fetch (interest follows the
  avatar).
  LIVE EDIT CHANGES THE WALKED WORLD — a terraform edit admitted mid-play to a
  resident region changes the terrain the avatar then walks on (a raised wall stops
  a walk that would otherwise pass) — the world is live, not a backdrop.
  TWO WINDOWS, ONE AUTHORITY — two independent runs over the same (input, edits)
  reach the IDENTICAL composed witness (avatar + world): an edit made in one view IS
  seen in the other, every byte admitted rather than trusted; a different edit
  stream lands a different witness.
  EQUAL-OR-REFUSE UNDER PLAY — a tampered or foreign edit woven into the stream
  refuses mid-loop with the replica byte-unchanged, and the avatar's walk is
  UNPERTURBED (malice cannot move the world or the player).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))

import chunkload as CK                                     # noqa: E402
import glide as GL                                         # noqa: E402
import panewire as PW                                      # noqa: E402


def _blank():
    return GL._heights("blank")


class TestResidentOrRefuse(unittest.TestCase):
    def test_unacquired_crossing_refuses(self):
        """Without streaming, the avatar cannot cross into an unresident region — the
        wired loop refuses rather than walking on unloaded terrain."""
        fld = _blank()
        with self.assertRaises((PW.PaneWireError, CK.ChunkError)):
            PW.run_wired(fld, (2, 8), "EEEEEE", {}, 4, 4000, acquire=False)

    def test_acquire_on_cross_completes_the_walk(self):
        """With streaming on, the loop ACQUIRES the region the avatar enters (verified
        fetch) and the walk completes — equal to the full-field glide, and at least
        one region was acquired mid-walk."""
        fld = _blank()
        out = PW.run_wired(fld, (2, 8), "EEEEEE", {}, 4, 4000)
        want = GL.glide_cells(fld, (2, 8), "EEEEEE", 4000, 4)
        self.assertEqual(out["transcript"], want)
        self.assertGreater(out["acquired"], 0)


class TestLiveEditChangesTheWalkedWorld(unittest.TestCase):
    def test_raised_wall_stops_the_avatar(self):
        """A terraform edit that raises a wall in the avatar's path, admitted mid-play,
        stops the walk where it would otherwise pass — the walked world is live."""
        fld = _blank()
        base = PW.run_wired(fld, (2, 8), "EEEEEE", {}, 4, 4000)
        # raise cell (10,8) far above max_step BEFORE the avatar reaches it (tick 1)
        walled = PW.run_wired(fld, (2, 8), "EEEEEE", {1: ("edit", 10, 8, 9000)}, 4, 4000)
        self.assertNotEqual(base["transcript"], walled["transcript"])
        # the avatar stops WEST of the raised cell (its final x never reaches 10)
        self.assertLess(walled["transcript"][-1][0] >> 32, 10)

    def test_edit_reflected_in_composed_witness(self):
        """The composed witness (avatar + world) moves when the world is edited, even if
        the avatar's own path were unchanged — the world is part of the authority."""
        fld = _blank()
        # edit a resident cell OFF the avatar's path (region (0,1), far from the walk)
        a = PW.run_wired(fld, (2, 8), "ee", {}, 4, 4000)
        b = PW.run_wired(fld, (2, 8), "ee", {0: ("edit", 1, 12, 40)}, 4, 4000)
        self.assertEqual(a["transcript"], b["transcript"])       # the avatar's path is identical
        self.assertNotEqual(a["witness"], b["witness"])          # but the world differs


class TestTwoWindowsOneAuthority(unittest.TestCase):
    def test_two_runs_same_witness(self):
        """Two independent wired runs over the same (input, edits) reach the identical
        composed witness — the edit made in one window IS seen in the other."""
        fld = _blank()
        edits = {1: ("edit", 12, 12, 30), 3: ("edit", 13, 9, 20)}
        a = PW.run_wired(fld, (2, 8), "EEEEEE", edits, 4, 4000)
        b = PW.run_wired(fld, (2, 8), "EEEEEE", edits, 4, 4000)
        self.assertEqual(a["witness"], b["witness"])

    def test_different_edits_diverge(self):
        """A different edit stream lands a different composed witness — the world is
        authoritative, not cosmetic."""
        fld = _blank()
        a = PW.run_wired(fld, (2, 8), "EEEEEE", {1: ("edit", 12, 12, 30)}, 4, 4000)
        b = PW.run_wired(fld, (2, 8), "EEEEEE", {1: ("edit", 12, 12, 31)}, 4, 4000)
        self.assertNotEqual(a["witness"], b["witness"])


class TestEqualOrRefuseUnderPlay(unittest.TestCase):
    def test_malice_refuses_and_the_walk_is_unperturbed(self):
        """A tampered edit woven into the stream refuses mid-loop (counted), the replica
        is byte-unchanged by it, and the avatar's walk equals the malice-free walk —
        malice moves neither the world nor the player."""
        fld = _blank()
        clean = PW.run_wired(fld, (2, 8), "EEEEEE", {}, 4, 4000)
        besieged = PW.run_wired(fld, (2, 8), "EEEEEE", {1: ("malice",), 3: ("malice",)}, 4, 4000)
        self.assertGreater(besieged["refusals"], 0)
        self.assertEqual(besieged["transcript"], clean["transcript"])
        self.assertEqual(besieged["witness"], clean["witness"])   # world unchanged by refused malice


class TestScenesAndDeterminism(unittest.TestCase):
    def test_scene_digests_match_goldens(self):
        for name in PW.SCENES:
            self.assertEqual(PW.scene_result(name), PW.golden(name), name)

    def test_determinism(self):
        for name in PW.SCENES:
            self.assertEqual(PW.scene_result(name), PW.scene_result(name), name)

    def test_digest_binds_verdict(self):
        a = PW.panewire_digest("x", "00" * 32, 6, 1, 0, "ADMIT")
        b = PW.panewire_digest("x", "00" * 32, 6, 1, 0, "PANEWIRE-REFUSE")
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
