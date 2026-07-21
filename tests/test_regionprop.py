# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/netcode/regionprop.py — the property sweep for the Seam Composition Theorem
(Tier-2, URDRRGP1): reunify == monolith under a seeded adversary.

`worldregion` (D16) proves that ANY valid spatial partition reunifies to the monolithic witness
bit-for-bit; the gate checks six hand-chosen seams. This sweeps random valid partitions against the
MONOLITH as an INDEPENDENT oracle (worldstep.simulate never partitions), turning existence-on-a-corpus
into confidence-over-a-sampled-partition-space.

  DIGEST — the fixed-seed sweep reproduces its pinned aggregate digest, deterministically.
  COMPOSITION — every random valid partition composes to the monolith (checked directly here too).
  NON-VACUITY — >=3 distinct region counts occur and the monolith actually evolves.
  DROPPED BOUNDARY — the defect (admit no ghosts) makes the sweep RAISE (L15).
  MALFORMED PARTITION — a non-increasing seam is REGION-REFUSEd before a tick runs.

Every test can go red (L5); the plants bite before the golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "netcode"), os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import regionprop as RP                                         # noqa: E402
import worldregion as R                                        # noqa: E402
import worldstep as WS                                         # noqa: E402


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_deterministic(self):
        d1 = RP.sweep_digest()
        d2 = RP.sweep_digest()
        self.assertEqual(d1, d2, "the sweep must be deterministic")
        self.assertEqual(d1, RP.golden(), "the sweep digest drifted from its golden")

    def test_report_counters_are_non_vacuous(self):
        rep = RP.sweep()
        self.assertEqual(rep["scenarios"], RP.COUNT)
        self.assertGreaterEqual(len(rep["region_counts"]), 3, "generator stuck on one partition shape")
        self.assertGreater(rep["frames"], 1, "the monolith did not evolve — composition trivial")


class TheOracle(unittest.TestCase):
    def test_random_partitions_compose_to_the_monolith(self):
        """The independent oracle, directly: worldstep.simulate (never partitions) equals every random
        region_simulate, over generated seams, with the region count actually varying."""
        w, log = R.seam2_world(), R.seam2_log()
        mono = WS.simulate(w, log)
        r = RP._LCG(1234)
        seen = set()
        for _ in range(80):
            seams = RP.gen_seams(r)
            self.assertEqual(R.region_simulate(w, log, seams), mono, f"partition {seams} diverged")
            seen.add(len(seams) + 1)
        self.assertGreaterEqual(len(seen), 3, "did not exercise multiple region counts")

    def test_malformed_partition_refused(self):
        """A non-increasing (or non-integer) seam is REGION-REFUSEd — the partition never rounds."""
        w, log = R.seam2_world(), R.seam2_log()
        with self.assertRaises(R.RegionError):
            R.region_simulate(w, log, [150, 150])
        with self.assertRaises(R.RegionError):
            R.region_simulate(w, log, [200, 100])


class TheSweepBites(unittest.TestCase):
    def test_dropped_boundary_falsifies_the_sweep(self):
        """The dropped-boundary defect (admit no ghosts) diverges from the monolith — the sweep RAISES."""
        orig = R.region_simulate
        R.region_simulate = lambda w, log, seams, **k: orig(w, log, seams, defect_drop_ghost=True)
        try:
            with self.assertRaises(RP.SweepError):
                RP.sweep()
        finally:
            R.region_simulate = orig
        self.assertEqual(RP.sweep_digest(), RP.golden(), "the module must be clean after the revert")


if __name__ == "__main__":
    unittest.main()
