# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-netcode N2 — rollback as a deterministic replay primitive.

The claim under test: a peer that receives inputs LATE (out of tick order, within a
stated snapshot horizon) rewinds to the newest canonical snapshot at-or-before the
input's tick, re-simulates to the present, and CONVERGES — its witness chain becomes
bit-identical to the canonical timeline (`lockstep.simulate` over the full log, the
frozen N1 oracle). Everything else is typed:

  * on-time, late, permuted, duplicated deliveries of ONE logical log -> ONE chain,
    equal to the oracle's, for every snapshot cadence K (K is operational, not
    semantic);
  * a provisional chain BEFORE the late input differs from the oracle at the input's
    tick (rollback demonstrably did work — non-vacuity of convergence);
  * snapshot restore is exact: the restored state reproduces the URDRLST1 witness
    pinned at the snapshot tick, and re-simulation from a snapshot equals cold
    simulation (snapshots introduce no drift);
  * an input OLDER than the rollback horizon is a typed refusal ROLLBACK-REFUSE,
    never a wrong chain;
  * a second event with the SAME (peer, seq) but DIFFERENT payload (a forgery or a
    tick-move) is a typed refusal ROLLBACK-CONFLICT, localized to the offending
    identity; an EXACT duplicate is absorbed;
  * an input the peer NEVER receives desyncs vs the oracle, localized by
    `first_desync` to the first mismatching tick (and a complete run does NOT);
  * the wrong implementation — applying a late input at the CURRENT head instead of
    rolling back — DIVERGES from the oracle (the defect the gate must catch).
`digest != MAC` still: identity conflicts are detected, signatures are not claimed."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lockstep as L                                       # noqa: E402
import rollback as R                                       # noqa: E402


def oracle_chain(w, log):
    frames, _ = L.simulate(w, log)
    return frames


class RollbackConvergence(unittest.TestCase):
    def setUp(self):
        self.w = L.world()
        self.log = L.sample_log()
        self.oracle = oracle_chain(self.w, self.log)

    def _run_schedule(self, schedule, K=8, H=64):
        """schedule: list of (deliver_after_tick, event). Advance tick-by-tick,
        delivering each event once the peer's head has passed its gate tick."""
        peer = R.Peer(self.w, K=K, H=H)
        pending = sorted(range(len(schedule)), key=lambda i: (schedule[i][0], i))
        idx = 0
        for t in range(self.w["T"]):
            while idx < len(pending) and schedule[pending[idx]][0] <= t:
                peer.deliver(schedule[pending[idx]][1])
                idx += 1
            peer.advance(t + 1)
        while idx < len(pending):
            peer.deliver(schedule[pending[idx]][1])
            idx += 1
        return peer

    def test_on_time_equals_oracle(self):
        """All inputs known from the start -> the oracle chain, bit-for-bit."""
        peer = R.Peer(self.w, K=8, H=64)
        for e in self.log:
            peer.deliver(e)
        peer.advance(self.w["T"])
        self.assertEqual(peer.chain(), self.oracle)

    def test_late_input_converges_and_rollback_happened(self):
        """One input delivered LATE (after its tick was simulated) converges to the
        oracle; the provisional chain before delivery differed at/after its tick
        (rollback demonstrably rewrote history — the test is non-vacuous)."""
        late = self.log[2]                                  # event at tick 5
        peer = R.Peer(self.w, K=4, H=64)
        for e in self.log:
            if e != late:
                peer.deliver(e)
        peer.advance(10)                                    # simulate PAST tick 5
        provisional = list(peer.chain())
        self.assertNotEqual(provisional[: 10 + 1], self.oracle[: 10 + 1],
                            "provisional chain already canonical — lateness fixture is vacuous")
        peer.deliver(late)                                  # late-but-valid -> rewind + replay
        peer.advance(self.w["T"])
        self.assertEqual(peer.chain(), self.oracle,
                         "late-but-valid input did not converge to the canonical timeline")

    def test_schedules_and_cadences_converge_to_one_chain(self):
        """Permuted + duplicated + assorted-lateness schedules, at snapshot cadences
        K in {4, 8}, all converge to the oracle chain (K is not semantic)."""
        base = [(0, e) for e in self.log]
        permuted = [(0, e) for e in reversed(self.log)]
        duplicated = [(0, e) for e in self.log] + [(0, e) for e in self.log]
        lateness = [(min(e[0] + 3, self.w["T"] - 1), e) for e in self.log]
        for K in (4, 8):
            for name, sched in (("base", base), ("permuted", permuted),
                                ("duplicated", duplicated), ("late", lateness)):
                peer = self._run_schedule(sched, K=K)
                peer.advance(self.w["T"])
                self.assertEqual(peer.chain(), self.oracle,
                                 f"schedule {name} @K={K} did not converge")

    def test_snapshot_restore_is_exact(self):
        """A restored snapshot reproduces the URDRLST1 witness pinned at its tick —
        snapshots introduce no drift (the snapshot contract's load-bearing half)."""
        peer = R.Peer(self.w, K=4, H=64)
        for e in self.log:
            peer.deliver(e)
        peer.advance(self.w["T"])
        self.assertTrue(peer.snapshots, "no snapshots retained — fixture is vacuous")
        for (t, pos, vel) in peer.snapshots:
            self.assertEqual(L._digest(pos, vel, self.w["n"]), self.oracle[t],
                             f"snapshot at tick {t} does not reproduce the pinned witness")

    def test_determinism_twice(self):
        """The same delivery schedule twice -> byte-identical chains."""
        sched = [(min(e[0] + 3, self.w["T"] - 1), e) for e in self.log]
        a = self._run_schedule(sched, K=4)
        b = self._run_schedule(sched, K=4)
        self.assertEqual(a.chain(), b.chain())


class RollbackRefusals(unittest.TestCase):
    def setUp(self):
        self.w = L.world()
        self.log = L.sample_log()

    def test_horizon_exceeded_is_typed_refusal(self):
        """An input older than the oldest retained snapshot REFUSES (typed), and the
        chain is left untouched — never silently wrong."""
        peer = R.Peer(self.w, K=4, H=2)                     # tiny horizon: keep 2 snapshots
        for e in self.log:
            if e[0] != 2:                                   # withhold the tick-2 inputs
                peer.deliver(e)
        peer.advance(60)                                    # snapshots at 52, 56 (H=2)
        before = list(peer.chain())
        with self.assertRaises(R.RollbackError) as ctx:
            peer.deliver(L.event(2, 0, 0, 0, 4, -6))
        self.assertEqual(ctx.exception.code, "ROLLBACK-REFUSE")
        self.assertEqual(peer.chain(), before, "a refused input still mutated the chain")

    def test_identity_conflict_is_typed_refusal(self):
        """Same (peer, seq), different payload — a forgery or tick-move — REFUSES
        ROLLBACK-CONFLICT naming the identity; an EXACT duplicate is absorbed."""
        peer = R.Peer(self.w, K=4, H=64)
        e = L.event(2, 0, 0, 0, 4, -6)
        peer.deliver(e)
        self.assertEqual(peer.deliver(e), "duplicate")      # exact duplicate absorbed
        with self.assertRaises(R.RollbackError) as ctx:
            peer.deliver(L.event(2, 0, 0, 0, 9, -6))        # same (peer,seq), altered dvx
        self.assertEqual(ctx.exception.code, "ROLLBACK-CONFLICT")
        with self.assertRaises(R.RollbackError) as ctx2:
            peer.deliver(L.event(3, 0, 0, 0, 4, -6))        # same (peer,seq), moved tick
        self.assertEqual(ctx2.exception.code, "ROLLBACK-CONFLICT")

    def test_missing_input_desyncs_localized(self):
        """An input NEVER delivered desyncs vs the oracle, localized to its tick by
        first_desync; the complete run does not (the detector discriminates)."""
        oracle = oracle_chain(self.w, self.log)
        peer = R.Peer(self.w, K=4, H=64)
        for e in self.log[1:]:                              # drop the tick-2 event
            peer.deliver(e)
        peer.advance(self.w["T"])
        d = L.first_desync(peer.chain(), oracle)
        self.assertIsNotNone(d, "a missing input produced the canonical chain (impossible)")
        self.assertEqual(d, self.log[0][0] + 1,
                         "desync not localized to the first affected witness")
        complete = R.Peer(self.w, K=4, H=64)
        for e in self.log:
            complete.deliver(e)
        complete.advance(self.w["T"])
        self.assertIsNone(L.first_desync(complete.chain(), oracle))

    def test_defect_apply_at_head_diverges(self):
        """The WRONG implementation — applying a late input at the current head
        instead of rewinding — must diverge from the oracle (the gate's defect)."""
        oracle = oracle_chain(self.w, self.log)
        late = self.log[2]
        peer = R.Peer(self.w, K=4, H=64)
        for e in self.log:
            if e != late:
                peer.deliver(e)
        peer.advance(10)
        peer.deliver_defect_apply_at_head(late)             # the defect path
        peer.advance(self.w["T"])
        self.assertNotEqual(peer.chain(), oracle,
                            "the apply-at-head defect converged — the invariant is vacuous")


if __name__ == "__main__":
    unittest.main()
