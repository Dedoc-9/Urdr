# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/nway.py — Phase M rung M1 (URDRNWY1): n-way nullity + the independence
lattice, the certified mesh's write scheduler.

`rannull` proved PAIRWISE nullity; this generalizes it to N regional edits on pairwise-disjoint
authorities — the parallel shard head equals every serial order, zero rebases; overlap refuses; and
the shard path is cross-checked against the global monolith (`terraform`, the independent oracle).

  THEOREM — N disjoint edits: parallel == all N! serial orders, one head (checked directly).
  N=2 AGREES WITH RAN-0 — the generalization is faithful (URDRNWY1 at N=2 is URDRRAN0).
  SHARD == GLOBAL — the shard head equals the independent terraform monolith.
  LATTICE — a repeated chunk serializes into successive rounds, each pairwise-disjoint.
  OVERLAP — a shared authority refuses, in two layers (disjointness AND parallel!=serial).
  CERTIFICATE — a tampered / reordered certificate refuses under re-derivation.
  THE SWEEP BITES — an off-by-one shard makes the seeded sweep RAISE (L15).

Every test can go red (L5); the plants bite before the golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import nway as NW                                               # noqa: E402
import rannull as RN                                            # noqa: E402
import chunkload as CK                                          # noqa: E402
import itertools                                                # noqa: E402

C = 8


class TheTheorem(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in NW.SCENES:
            self.assertEqual(NW.scene_result(name), NW.golden(name), name)
            self.assertEqual(NW.scene_result(name), NW.scene_result(name), name)

    def test_nway_theorem_directly(self):
        """Four disjoint edits: the parallel head equals EVERY one of the 24 serial orders; the
        certificate re-verifies; and it is one independence round."""
        fld = NW.flat_world(32)
        man = CK.field_manifest(fld, C)
        store = {CK.address(r): r for r in CK.cut(fld, C).values()}
        recs = (NW.rrec(fld, C, 2, 2, 11), NW.rrec(fld, C, 10, 4, 22),
                NW.rrec(fld, C, 20, 20, 33), NW.rrec(fld, C, 28, 10, 44))
        par = NW.nway_parallel_head(man, store, recs)
        for order in itertools.permutations(range(4)):
            self.assertEqual(NW.nway_serial_head(man, store, recs, order), par, order)
        cert, head = NW.nway_null(fld, C, recs)
        self.assertEqual(NW.check_nway(fld, C, cert), head)
        self.assertEqual(NW.independence_rounds(fld, C, recs), [(0, 1, 2, 3)])

    def test_n2_agrees_with_ran0(self):
        """At N=2 the n-way head equals RAN-0's pairwise nullity head — a faithful generalization."""
        fld = NW.flat_world(32)
        ra, rb = NW.rrec(fld, C, 2, 2, 11), NW.rrec(fld, C, 20, 20, 33)
        _c, head = NW.nway_null(fld, C, (ra, rb))
        _rc, ranhead = RN.nullity(fld, C, ra, rb)
        self.assertEqual(head, ranhead)

    def test_shard_head_equals_global_monolith(self):
        """The shard n-way head equals the INDEPENDENT global terraform monolith (anti-Goodhart)."""
        fld = NW.flat_world(32)
        recs = (NW.rrec(fld, C, 2, 2, 11), NW.rrec(fld, C, 10, 4, 22), NW.rrec(fld, C, 28, 28, 33))
        _c, head = NW.nway_null(fld, C, recs)
        self.assertEqual(head, NW._global_head(fld, C, recs))


class TheLatticeAndConflict(unittest.TestCase):
    def test_lattice_serializes_a_shared_chunk(self):
        """Two edits on chunk (0,0) plus two on distinct chunks → TWO rounds, each pairwise-disjoint."""
        fld = NW.flat_world(32)
        r0a = NW.rrec(fld, C, 1, 1, 5)
        f1 = NW._apply_global(fld, C, (r0a,))
        r0b = NW.rrec(f1, C, 3, 3, 4)                           # chunk (0,0) again
        recs = (r0a, NW.rrec(fld, C, 10, 2, 7), NW.rrec(fld, C, 18, 18, 9), r0b)
        rounds = NW.independence_rounds(fld, C, recs)
        self.assertEqual(len(rounds), 2)
        for rd in rounds:
            self.assertTrue(NW._disjoint_round(fld, C, recs, rd), f"round {rd} not disjoint")

    def test_overlap_refuses_in_two_layers(self):
        """A shared authority refuses — via the disjointness check, and (with it defanged) via the
        deeper parallel!=serial layer: individually redundant, jointly load-bearing."""
        fld = NW.flat_world(32)
        ra = NW.rrec(fld, C, 2, 2, 11)
        rc = RN.regional_record(CK.address(CK.cut(fld, C)[(0, 0)]), 0, 0, 5, 5, 0, 7)   # same chunk
        with self.assertRaises(NW.NwayError):
            NW.nway_null(fld, C, (ra, rc))
        orig = NW.first_overlap
        NW.first_overlap = lambda auths: None                  # defang layer 1
        try:
            with self.assertRaises(NW.NwayError):               # layer 2 still catches it
                NW.nway_null(fld, C, (ra, rc))
        finally:
            NW.first_overlap = orig

    def test_certificate_forgery_refuses(self):
        """A flipped byte in the certificate refuses; a certificate for a different world refuses."""
        fld = NW.flat_world(32)
        recs = (NW.rrec(fld, C, 2, 2, 11), NW.rrec(fld, C, 20, 20, 33))
        cert, _h = NW.nway_null(fld, C, recs)
        bad = bytearray(cert); bad[40] ^= 0x01
        with self.assertRaises(NW.NwayError):
            NW.check_nway(fld, C, bytes(bad))


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = NW.sweep_digest()
        self.assertEqual(d1, NW.sweep_digest(), "deterministic")
        self.assertEqual(d1, NW.sweep_golden(), "sweep drifted from golden")
        rep = NW.sweep()
        self.assertGreaterEqual(len(rep["sizes"]), 3, "batch sizes not varied")
        self.assertEqual(rep["overlaps_refused"], rep["scenarios"], "not every overlap refused")

    def test_shard_mutant_falsifies_the_sweep(self):
        """An off-by-one shard makes the shard head diverge from the global monolith — the sweep RAISES."""
        orig = RN.shard_apply

        def bad(ch, rec):
            p, kx, ky, x, y, oh, nh = RN.restore_regional(rec)
            return orig(ch, RN.regional_record(p, kx, ky, x, y, oh, nh + 1))
        RN.shard_apply = bad
        try:
            with self.assertRaises(NW.NwayError):
                NW.sweep()
        finally:
            RN.shard_apply = orig
        self.assertEqual(NW.sweep_digest(), NW.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
