# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/partition.py — Phase M rung M4 (URDRPRT1): the partitioned mesh. M3
proved MESH == MONOLITH while connected; M4 asks what happens when the connection disappears, and the
answer is already latent in the laws (M1 disjointness + M2 custody CAS + the storm prefix property):

  THE PARTITION PREFIX THEOREM. Every lawful partitioned execution equals a PREFIX of the corresponding
  connected execution; any attempt to extend beyond that certified prefix either preserves equality or
  refuses. In one line:  partitioned mesh == monolith prefix  OR  refuse.

The system refuses to invent history — a stronger, more distinctive statement than "the cluster remains
available." This suite encodes the five attacks the honest implementation must survive:

  1. SILENT DIVERGENCE — both sides continue "successfully" and reunify; a side that wrote a region it
     could not verify diverges, and the honest impl refuses BEFORE divergence (the freeze rule).
  2. AVAILABILITY FORGERY — gut the freeze rule, let the isolated side speculate; reunification fails
     against the monolith.
  3. PREFIX VIOLATION — partition mid-transfer, admit beyond the last shared prefix; refuse.
  4. SPLIT-BRAIN AUTHORITY — a valid lease duplicated across both sides; both admit; reunify != monolith;
     the honest impl refuses (custody, then the reunify overlap — two layers).
  5. PARTITION-TRANSPORT FORGERY — a migration certificate generated from the unreachable partition;
     authority continuation refuses (the migration CAS against the frozen custody head).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import partition as PT                                           # noqa: E402


def _cut():
    """A standard cut: flat 32×32 world (16 regions), the 4×4 grid split into a LEFT half (kx<2) owned
    by steward 'lear' and a RIGHT half (kx>=2) owned by steward 'raun'."""
    fld = PT.flat_world(32)
    assign = {}
    for ky in range(4):
        for kx in range(4):
            assign[(kx, ky)] = "lear" if kx < 2 else "raun"
    side_of = {"lear": "L", "raun": "R"}
    return fld, assign, side_of


class ThePartitionPrefixTheorem(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in PT.SCENES:
            self.assertEqual(PT.scene_result(name), PT.golden(name), name)
            self.assertEqual(PT.scene_result(name), PT.scene_result(name), name)

    def test_lawful_partition_equals_monolith_prefix(self):
        """Each side writes only its own regions during the partition; reunify equals the monolith of
        exactly the admitted writes — and that is a PREFIX of the connected execution (every region's
        partitioned chunk is either its connected chunk or its cut chunk, never a third state)."""
        fld, assign, side_of = _cut()
        left = [("write", "lear", 0, 0, 1, 1, 100), ("write", "lear", 1, 3, 2, 2, 40)]
        right = [("write", "raun", 3, 3, 3, 3, 55), ("write", "raun", 2, 1, 0, 0, 25)]
        rep = PT.partitioned_run(fld, assign, side_of, left, right)
        self.assertEqual(rep["witness"], PT.monolith_of(fld, rep["admitted"]))
        self.assertTrue(PT.is_prefix_of_connected(fld, assign, side_of, left, right),
                        "the partitioned world is not a prefix of the connected execution")
        self.assertEqual(rep["frozen"], 0, "no cross-partition op here — nothing should freeze")

    def test_disjoint_sides_reunify_without_conflict(self):
        """The two sides write DISJOINT region sets, so reunification is well-defined and equals the
        monolith — the n-way nullity of M1, now across a partition boundary."""
        fld, assign, side_of = _cut()
        left = [("write", "lear", 0, 0, 1, 1, 7), ("write", "lear", 0, 1, 1, 1, 8),
                ("migrate", 0, 0, "lear", "lear")]   # a vacuous self-migration is refused → caught below
        # replace the vacuous migration with a real local one is out of scope here; keep writes only
        left = [("write", "lear", 0, 0, 1, 1, 7), ("write", "lear", 0, 1, 1, 1, 8)]
        right = [("write", "raun", 3, 0, 1, 1, 9), ("write", "raun", 3, 1, 1, 1, 10)]
        rep = PT.partitioned_run(fld, assign, side_of, left, right)
        self.assertEqual(rep["witness"], PT.monolith_of(fld, rep["admitted"]))
        self.assertEqual(rep["admitted_count"], 4)


class TheFiveAttacks(unittest.TestCase):
    def test_1_silent_divergence_refused_before_it_occurs(self):
        """A side writes a region it does not own (the other side's). The HONEST impl freezes it (refuse
        before divergence). With the freeze rule GUTTED it is admitted, and reunification then diverges
        from the monolith / conflicts — the divergence the freeze prevents is real."""
        fld, assign, side_of = _cut()
        # LEFT tries to write a RIGHT region (3,3) using its true steward 'raun' — a speculation
        left = [("write", "lear", 0, 0, 1, 1, 5), ("write", "raun", 3, 3, 2, 2, 6)]
        right = [("write", "raun", 3, 3, 1, 1, 9)]     # RIGHT legitimately writes (3,3)
        # honest: LEFT's (3,3) write FREEZES; reunify == monolith of the admitted (no conflict)
        rep = PT.partitioned_run(fld, assign, side_of, left, right)
        self.assertGreater(rep["frozen"], 0, "the cross-partition write should have frozen")
        self.assertEqual(rep["witness"], PT.monolith_of(fld, rep["admitted"]))
        # gut the freeze rule → LEFT and RIGHT both change (3,3) → reunify REFUSES (split-brain layer)
        orig = PT._freeze_ok
        PT._freeze_ok = lambda side, region_side, kx, ky: True
        try:
            with self.assertRaises(PT.PartitionError):
                PT.partitioned_run(fld, assign, side_of, left, right)
        finally:
            PT._freeze_ok = orig

    def test_2_availability_forgery_fails_at_reunification(self):
        """Gut the freeze rule and let the isolated side speculate on regions across the partition;
        the apparent progress does not survive reunification against the monolith."""
        fld, assign, side_of = _cut()
        left = [("write", "raun", 2, 2, 1, 1, 12), ("write", "raun", 3, 2, 2, 2, 13)]  # all cross
        right = [("write", "raun", 2, 2, 3, 3, 99)]    # RIGHT also writes (2,2)
        orig = PT._freeze_ok
        PT._freeze_ok = lambda side, region_side, kx, ky: True
        try:
            with self.assertRaises(PT.PartitionError):
                PT.partitioned_run(fld, assign, side_of, left, right)
        finally:
            PT._freeze_ok = orig

    def test_3_prefix_violation_refuses(self):
        """Partition mid-transfer: a cross-partition migration is FROZEN, so the destination side never
        receives authority; a write by the would-be new steward beyond the shared prefix refuses."""
        fld, assign, side_of = _cut()
        # LEFT tries to migrate its region (0,0) to RIGHT's steward 'raun' — cross-partition → FROZEN
        # then RIGHT tries to write (0,0) as 'raun' (authority it never lawfully received) → frozen/refused
        left = [("migrate", 0, 0, "lear", "raun")]
        right = [("write", "raun", 0, 0, 1, 1, 50)]
        rep = PT.partitioned_run(fld, assign, side_of, left, right)
        self.assertEqual(rep["admitted_count"], 0, "nothing beyond the shared prefix may be admitted")
        self.assertGreaterEqual(rep["frozen"], 2, "both the cross migration and the beyond-prefix write freeze")
        self.assertEqual(rep["witness"], PT.cut_witness(fld), "the world stayed at the shared prefix")

    def test_4_split_brain_authority_refuses(self):
        """A valid lease duplicated across both sides: both sides attempt to write the SAME region as
        its true steward. Custody keeps only the owning side (the freeze rule); with it gutted, both
        admit and reunification REFUSES — two layers, individually redundant, jointly load-bearing."""
        fld, assign, side_of = _cut()
        left = [("write", "lear", 1, 1, 1, 1, 30)]     # LEFT owns (1,1)
        right = [("write", "lear", 1, 1, 2, 2, 40)]    # RIGHT speculates on (1,1) as 'lear' (duplicated authority)
        # honest: RIGHT's (1,1) write freezes (region_side is L); reunify clean
        rep = PT.partitioned_run(fld, assign, side_of, left, right)
        self.assertEqual(rep["witness"], PT.monolith_of(fld, rep["admitted"]))
        # gut the freeze rule → both write (1,1) → split-brain → reunify REFUSES
        orig = PT._freeze_ok
        PT._freeze_ok = lambda side, region_side, kx, ky: True
        try:
            with self.assertRaises(PT.PartitionError):
                PT.partitioned_run(fld, assign, side_of, left, right)
        finally:
            PT._freeze_ok = orig

    def test_5_partition_transport_forgery_refuses(self):
        """A migration certificate minted on the unreachable side (a different, post-cut custody head)
        is presented to this side for authority continuation; the migration CAS against this side's
        FROZEN custody head refuses it — never rebased."""
        fld, assign, side_of = _cut()
        with self.assertRaises(PT.PartitionError):
            PT.adopt_foreign_certificate(fld, assign, side_of)


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = PT.sweep_digest()
        self.assertEqual(d1, PT.sweep_digest(), "deterministic")
        self.assertEqual(d1, PT.sweep_golden(), "sweep drifted from golden")
        rep = PT.sweep()
        self.assertGreater(rep["frozen_total"], 0, "no cross-partition op ever froze")
        self.assertGreater(rep["admitted_total"], 0, "no op was ever admitted")
        self.assertGreater(rep["both_sides_active"], 0, "some scenario must exercise both sides")
        self.assertGreater(rep["changed"], 0, "no scenario changed the world")

    def test_sweep_bites_gutted_freeze(self):
        """L15 — with the freeze rule gutted, the isolated sides speculate across the partition and the
        sweep hits a divergence/split-brain and RAISES; clean again after the revert."""
        orig = PT._freeze_ok
        PT._freeze_ok = lambda side, region_side, kx, ky: True
        try:
            with self.assertRaises(PT.PartitionError):
                PT.sweep()
        finally:
            PT._freeze_ok = orig
        self.assertEqual(PT.sweep_digest(), PT.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
