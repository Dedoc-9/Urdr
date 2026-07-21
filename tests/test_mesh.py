# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/mesh.py — Phase M rung M3 (URDRMSH1): the meshed simulation. The
capstone ∀-law MESH == MONOLITH — N authorities owning regions and MIGRATING authority over time
compose to the SAME world witness a single monolithic authority would compute, bit-for-bit, or refuse.

M3 is a COMPOSITION: `nway` (M1) schedules the concurrent per-tick writes (the independence lattice as
the concurrency certificate — one round iff genuinely parallel); `migrate` (M2) moves authority between
ticks (witness-neutral) and gates every write (steward-checked admit); `terraform` is the MONOLITH
oracle (the neutral ruler — it never consults custody, so a mesh bug cannot hide in its own answer).
This generalizes `regionprop`'s reunify==monolith from STATIC seams to MIGRATING authorities.

  MESH == MONOLITH — a concurrent multi-steward simulation with authority migrating equals the
    monolith of the same writes, bit-for-bit.
  THE MIGRATION IS WITNESS-NEUTRAL AT SCALE — the witness is invariant to WHO owned WHAT WHEN;
    the same writes under any migration schedule land the same world.
  THE CONCURRENCY IS REAL — each tick's writes form ONE independence round (genuinely parallel).
  REJECT-WHOLE — a non-steward write, an overlapping concurrent batch, and a theft migration each
    refuse the WHOLE tick typed (the atomicity discipline).
  THE SWEEP BITES — a custody-blind monolith (writes applied ignoring the steward) diverges, and a
    tick that silently drops a refused write diverges — the sweep RAISES (L15).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import mesh as MS                                                # noqa: E402


def _four_steward_genesis():
    """Assign the 16-region 4×4 grid to four stewards by quadrant."""
    a = {}
    for ky in range(4):
        for kx in range(4):
            a[(kx, ky)] = ("alfa", "bravo", "charl", "delta")[(kx // 2) + 2 * (ky // 2)]
    return a


class TheCapstone(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in MS.SCENES:
            self.assertEqual(MS.scene_result(name), MS.golden(name), name)
            self.assertEqual(MS.scene_result(name), MS.scene_result(name), name)

    def test_parallel_tick_equals_monolith(self):
        """Four stewards each write their own region in ONE concurrent tick — the mesh witness equals
        the monolith, and the tick is a single independence round (genuinely parallel)."""
        fld = MS.flat_world(32)
        assign = _four_steward_genesis()
        schedule = [{"writes": [("alfa", 0, 0, 1, 1, 11), ("bravo", 2, 0, 1, 1, 22),
                                ("charl", 0, 2, 1, 1, 33), ("delta", 2, 2, 1, 1, 44)],
                     "migrations": []}]
        rep = MS.mesh_run(fld, assign, schedule)
        self.assertEqual(rep["witness"], MS.monolith(fld, schedule))
        self.assertEqual(rep["max_tick_width"], 4)
        self.assertGreaterEqual(rep["concurrent_writes"], 4)

    def test_migration_is_witness_neutral_at_scale(self):
        """The SAME writes under DIFFERENT migration schedules land the SAME world witness — authority
        mobility does not perturb the world (guarantee #2/#3 at mesh scale)."""
        fld = MS.flat_world(32)
        assign = {k: "alfa" for k in _four_steward_genesis()}
        # schedule 1: alfa keeps writing (no migration)
        s1 = [{"writes": [("alfa", 0, 0, 1, 1, 100)], "migrations": []},
              {"writes": [("alfa", 0, 0, 2, 2, 50)], "migrations": []}]
        # schedule 2: same writes, but authority migrates alfa->bravo between the ticks
        s2 = [{"writes": [("alfa", 0, 0, 1, 1, 100)], "migrations": [(0, 0, "alfa", "bravo")]},
              {"writes": [("bravo", 0, 0, 2, 2, 50)], "migrations": []}]
        r1 = MS.mesh_run(fld, assign, s1)
        r2 = MS.mesh_run(fld, assign, s2)
        self.assertEqual(r1["witness"], r2["witness"], "migration perturbed the witness")
        self.assertEqual(r1["witness"], MS.monolith(fld, s1))
        self.assertEqual(r2["migrations"], 1)

    def test_handoff_then_write_lands_under_the_new_steward(self):
        """A region migrates A->B->C over ticks and each current steward writes it in turn — every
        write lands, the mesh equals the monolith, custody depth grows."""
        fld = MS.flat_world(32)
        assign = {k: "alfa" for k in _four_steward_genesis()}
        sched = [{"writes": [("alfa", 1, 1, 0, 0, 7)], "migrations": [(1, 1, "alfa", "bravo")]},
                 {"writes": [("bravo", 1, 1, 1, 1, 8)], "migrations": [(1, 1, "bravo", "charl")]},
                 {"writes": [("charl", 1, 1, 2, 2, 9)], "migrations": []}]
        rep = MS.mesh_run(fld, assign, sched)
        self.assertEqual(rep["witness"], MS.monolith(fld, sched))
        self.assertEqual(rep["migrations"], 2)


class TheRefusals(unittest.TestCase):
    def test_non_steward_write_rejects_whole_tick(self):
        """A write by a steward that does not own the region refuses the WHOLE tick (reject-whole)."""
        fld = MS.flat_world(32)
        assign = _four_steward_genesis()
        # bravo does not own (0,0) (alfa does)
        sched = [{"writes": [("alfa", 0, 0, 1, 1, 5), ("bravo", 0, 0, 2, 2, 6)], "migrations": []}]
        with self.assertRaises(MS.MeshError):
            MS.mesh_run(fld, assign, sched)

    def test_overlapping_concurrent_batch_refuses(self):
        """Two writes on the SAME region in ONE tick are not concurrent-schedulable — MESH-REFUSE
        (overlapping writes belong in successive ticks, the independence lattice's law)."""
        fld = MS.flat_world(32)
        assign = {k: "alfa" for k in _four_steward_genesis()}
        sched = [{"writes": [("alfa", 0, 0, 1, 1, 5), ("alfa", 0, 0, 2, 2, 6)], "migrations": []}]
        with self.assertRaises(MS.MeshError):
            MS.mesh_run(fld, assign, sched)

    def test_theft_migration_refuses(self):
        """A migration whose source is not the region's steward refuses (migrate's theft law,
        inherited)."""
        fld = MS.flat_world(32)
        assign = {k: "alfa" for k in _four_steward_genesis()}
        sched = [{"writes": [], "migrations": [(0, 0, "bravo", "charl")]}]   # bravo is not steward
        with self.assertRaises(MS.MeshError):
            MS.mesh_run(fld, assign, sched)


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = MS.sweep_digest()
        self.assertEqual(d1, MS.sweep_digest(), "deterministic")
        self.assertEqual(d1, MS.sweep_golden(), "sweep drifted from golden")
        rep = MS.sweep()
        self.assertGreater(rep["migrations_total"], 0, "no scenario migrated authority")
        self.assertGreater(rep["concurrent_ticks"], 0, "no tick had >1 concurrent write")
        self.assertGreaterEqual(len(rep["steward_counts"]), 2, "layouts not varied")
        self.assertGreater(rep["changed"], 0, "no scenario changed the world")

    def test_sweep_bites_custody_blind_monolith(self):
        """L15 — if the monolith oracle were computed WITHOUT the writes it should include (a dropped
        write), it diverges from the mesh and the sweep RAISES; clean again after the revert."""
        orig = MS._monolith_apply
        MS._monolith_apply = lambda field, writes: orig(field, writes[:-1]) if writes else orig(field, writes)
        try:
            with self.assertRaises(MS.MeshError):
                MS.sweep()
        finally:
            MS._monolith_apply = orig
        self.assertEqual(MS.sweep_digest(), MS.sweep_golden(), "clean after revert")

    def test_sweep_bites_dropped_write(self):
        """A mesh tick that silently DROPS a refused-looking write (applies fewer than asked) diverges
        from the monolith — the sweep RAISES."""
        orig = MS._apply_one_write
        state = {"n": 0}

        def skipping(sman, certs, man, store, writer, kx, ky, lx, ly, dh):
            state["n"] += 1
            if state["n"] == 2:                                  # silently drop the 2nd write ever
                return man, store, None
            return orig(sman, certs, man, store, writer, kx, ky, lx, ly, dh)
        MS._apply_one_write = skipping
        try:
            with self.assertRaises(MS.MeshError):
                MS.sweep()
        finally:
            MS._apply_one_write = orig
        self.assertEqual(MS.sweep_digest(), MS.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
