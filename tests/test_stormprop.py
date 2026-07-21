# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/stormprop.py — the property sweep for the storm's PREFIX PROPERTY
(Tier-2, URDRSTP1): equal-or-refuse under chaos, swept.

`storm` proves that a wire client under a seeded adversarial transport either converges to the
authority witness or freezes each gapped region at the authority's PREFIX; the gate checks four curated
seeds. This sweeps random storms against INDEPENDENT oracles — the authority's own witness (loss-free)
and storm.prefix_witness computed WITHOUT the loom (lossy).

  DIGEST — the fixed-seed sweep reproduces its pinned aggregate digest, deterministically.
  BOTH BRANCHES — loss-free storms converge to the authority witness; lossy storms equal the prefix.
  LOAD-BEARING — some lossy prefix is STRICTLY below the full log, so a gap-ignoring client is caught.
  NON-VACUITY — real drops / reorderings / duplicates / detected stalls; both branches occur.
  THE SWEEP BITES — a wrong prefix oracle (the full-log witness) makes the sweep RAISE (L15).

Every test can go red (L5); the plants bite before the golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import stormprop as SP                                          # noqa: E402
import storm as ST                                             # noqa: E402


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_deterministic(self):
        d1 = SP.sweep_digest()
        d2 = SP.sweep_digest()
        self.assertEqual(d1, d2, "the sweep must be deterministic")
        self.assertEqual(d1, SP.golden(), "the sweep digest drifted from its golden")

    def test_report_counters_are_non_vacuous(self):
        rep = SP.sweep()
        self.assertGreater(rep["lossy"], 0, "no lossy storms")
        self.assertGreater(rep["lossfree"], 0, "no loss-free storms")
        for k in ("drops", "reorder", "dup", "stalled"):
            self.assertGreater(rep[k], 0, f"the storm did not storm ({k}=0)")
        self.assertGreater(rep["prefix_ne_want"], 0,
                           "no strict prefix — the prefix property would be indistinguishable")


class TheOracles(unittest.TestCase):
    def test_lossfree_converges_to_authority_witness(self):
        """A loss-free storm (reorder + dup, no loss) converges to the AUTHORITY witness, exactly-once."""
        fld = ST._blank()
        updates, want = ST.authority_log(fld, SP.CSIZE)
        sched = ST.schedule(b"lf-chaos", len(updates), loss_pct=0, dup_pct=40, delay_max=6)
        out = ST.run_client(fld, SP.CSIZE, updates, sched)
        self.assertEqual(ST._WR.replica_witness(out["client"]), want)
        self.assertEqual(out["admitted"], len(updates))

    def test_prefix_property_is_load_bearing(self):
        """A lossy storm with a real gap freezes at the authority PREFIX, and that prefix is strictly
        below the full log — so a client that admitted past the gap (converging to `want`) is caught."""
        fld = ST._blank()
        updates, want = ST.authority_log(fld, SP.CSIZE)
        sched = ST.schedule(b"tempest-loss", len(updates), loss_pct=25, dup_pct=20, delay_max=6)
        self.assertGreater(ST.measure(sched)["drops"], 0, "the fixture must actually drop")
        out = ST.run_client(fld, SP.CSIZE, updates, sched)
        exp = ST.prefix_witness(fld, SP.CSIZE, updates, sched)
        self.assertEqual(ST._WR.replica_witness(out["client"]), exp, "replica must equal the prefix")
        self.assertNotEqual(exp, want, "the prefix must be strictly below the full log (load-bearing)")


class TheSweepBites(unittest.TestCase):
    def test_wrong_prefix_oracle_falsifies_the_sweep(self):
        """Replacing the honest prefix oracle with the full-log witness makes the sweep RAISE on a
        lossy storm — the prefix property is a live falsifier, not decoration."""
        want_oracle = lambda *a, **k: ST.authority_log(ST._blank(), SP.CSIZE)[1]
        with self.assertRaises(SP.SweepError):
            SP.sweep(oracle=want_oracle)
        self.assertEqual(SP.sweep_digest(), SP.golden(), "the module must be clean after")


if __name__ == "__main__":
    unittest.main()
